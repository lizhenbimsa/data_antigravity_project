"""
00_preprocessing — 阶段 00: 数据预处理流水线编排器 (Phase 4b 重构)
=====================================================================

模块职责
--------
本模块在 Phase 4b 重构后仅保留*流水线编排*角色, 真正的处理逻辑分散在
4 个 sub-module:

    _constants.py  — 模块级常量 / CONFIG / logger / 已编译正则
    load.py        — Aho-Corasick 自动机 + 单文件并行入口
    normalize.py   — OpenCC 繁简、HTML 清洗、噪声去除、尾部规范化
    filter.py      — 8 步初步过滤 (含 Schema 统一 + 媒体名称清理)
    dedup.py       — 精确去重 + MinHash LSH 近似去重

本文件保留:
    load_and_process_data() — XLSX 并行加载 + 增量缓存编排
    main()                  — 阶段 CLI 入口
    print_stata_template -- 不在这里, 见 falsification

处理对象
--------
    176 个 XLSX 文件 (~37GB, ~1700 万条媒体报道记录)

处理流程
--------
    1. 并行加载 XLSX → pd.DataFrame (calamine 引擎, 比 openpyxl 快 5-10x)
    2. 初步过滤 (地域 / 媒体类型 / 缺失值 / 广告 / 银行关键词保留)
    3. 文本标准化 (编码修复 / 繁简 / 全角半角 / HTML / 噪声)
    4. 长度过滤 (标题/内容汉字数上下限)
    5. 增量缓存 (Parquet, 配置哈希守门)
    6. 精确去重 (标题+内容完全匹配; 保留首发 — 日期为第一排序键,
       媒体权重仅作同日 tiebreak, fix omni-g-preprocess-06)
    7. 近似去重 (MinHash LSH + 5 工作日时间窗口, Jaccard ≥ 0.8)

性能特性
--------
    - ProcessPoolExecutor 多进程并行处理独立 XLSX 文件
    - Aho-Corasick 自动机实现 O(n) 银行关键词匹配
    - 预编译正则合并 (单次 re.sub 替代多次调用)
    - multiprocessing.Pool 分块并行 MinHash 生成 (每 10% 进度输出)
    - 增量缓存避免重复处理
    - Parquet + Snappy 压缩减少磁盘 I/O

输入
----
    config.yaml 中 ``paths.raw_data_dir`` 指定的目录下所有 .xlsx 文件

输出
----
    config.yaml 中 ``paths.output_dir / filenames.output_00_preprocessing``
    指定的 Parquet 文件
"""

from __future__ import annotations

import concurrent.futures
import gc
import glob
import json
import os
import sys
import time

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Phase 4b: sys.path 注入 — 让 ``python -m news_process.pipeline.preprocess.runner``
# 与 ``python news_process/00_preprocessing.py`` 都能解析包导入。
if __name__ == "__main__":
    _project_parent = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    if _project_parent not in sys.path:
        sys.path.insert(0, _project_parent)

from news_process.core.logging import (
    log_and_time,
    log_memory_usage,
    log_stage_summary,
)
from news_process.core.reporting import safe_save_preview_csv
from news_process.pipeline.preprocess._constants import (
    CONFIG,
    MEDIA_NAME_OVERRIDES,
    PARAMS,
    PREPROCESS_CODE_VERSION,
    STAGE_NAME,
    logger,
)
from news_process.pipeline.preprocess.dedup import ArticleDeduplicator
from news_process.pipeline.preprocess.load import _process_single_file

# ============================================================================
# 增量缓存键 — config + 资源内容 + 清洗代码版本
# ============================================================================


def compute_preprocess_cache_key(
    params: dict | None = None,
    normalization: dict | None = None,
    noise_patterns_path: str | None = None,
    bank_keywords_path: str | None = None,
    code_version: str | None = None,
) -> str:
    """计算 per-file 增量缓存键 (SHA-256).

    fix(omni-g-preprocess-04, 2026-06-11): 旧实现仅 hash PARAMS (preprocessing
    段), 注释却声称 plan m4 已覆盖 noise_patterns / normalize* 等键 — 与实现
    不符。per-file 清洗结果实际还依赖:
      ① ``CONFIG['normalization']`` 段 (opencc_config / html_removal_length_threshold,
         独立顶层段, 不在 PARAMS 内);
      ② noise_patterns.json 与 bank_keywords.json 的**文件内容** (路径在 paths 段,
         内容从不进哈希 → 改资源文件后缓存仍命中, 盘上已实证混规则语料);
      ③ 清洗代码本身的版本 (正则/过滤逻辑变更)。
    现缓存键 = SHA-256(preprocessing 段 + normalization 段 + 两资源文件 sha256
    + PREPROCESS_CODE_VERSION) — 任一变更 → production run 自动失效重算。
    资源文件缺失时以 ``missing:<文件名>`` 哨兵入哈希 (fail-soft, 与 _constants
    资源加载失败回退空列表的行为一致)。

    Args:
        params:             preprocessing 配置段 (默认取全局 PARAMS)。
        normalization:      normalization 配置段 (默认取 CONFIG['normalization'])。
        noise_patterns_path: 噪声模式 JSON 路径 (默认取 CONFIG['paths'])。
        bank_keywords_path:  银行关键词 JSON 路径 (默认取 CONFIG['paths'])。
        code_version:       清洗代码版本号 (默认 PREPROCESS_CODE_VERSION)。

    Returns:
        str: 64 位十六进制 SHA-256 摘要。
    """
    from news_process.core.data_versioning import (
        compute_config_hash,
        compute_file_hash,
    )

    def _resource_hash(path: str | None) -> str:
        try:
            return compute_file_hash(path)
        except (OSError, TypeError):
            return f'missing:{os.path.basename(str(path))}'

    if noise_patterns_path is None:
        noise_patterns_path = CONFIG['paths'].get('noise_patterns_file', '')
    if bank_keywords_path is None:
        bank_keywords_path = CONFIG['paths'].get('bank_keywords_file', '')

    payload = {
        'preprocessing': params if params is not None else PARAMS,
        'normalization': (normalization if normalization is not None
                          else CONFIG.get('normalization', {})),
        'noise_patterns_sha256': _resource_hash(noise_patterns_path),
        'bank_keywords_sha256': _resource_hash(bank_keywords_path),
        'code_version': (code_version if code_version is not None
                         else PREPROCESS_CODE_VERSION),
    }
    return compute_config_hash(payload)


# ============================================================================
# 主处理函数 — XLSX 并行加载 + 增量缓存
# ============================================================================


@log_and_time(logger)
def load_and_process_data(raw_data_dir: str, output_path: str) -> int:
    """并行加载和处理所有 XLSX 文件, 将结果写入单个 Parquet 文件.

    处理流程:
      1. 扫描 XLSX 文件列表, 检查增量缓存
      2. 读取已缓存的 Parquet 文件
      3. 并行处理未缓存的 XLSX 文件 (ProcessPoolExecutor)
      4. 将处理结果追加写入输出 Parquet 文件, 同时写入缓存

    Args:
        raw_data_dir: 原始 XLSX 文件目录。
        output_path:  输出 Parquet 文件路径。

    Returns:
        int: 最终写入的总行数。
    """
    xlsx_files = glob.glob(os.path.join(raw_data_dir, '*.xlsx'))
    logger.info(f"找到 {len(xlsx_files)} 个 XLSX 文件")

    if not xlsx_files:
        logger.error("未找到任何 XLSX 文件!")
        return 0

    # ── 增量缓存检查 ──
    # 已处理的文件写入 Parquet 缓存, 下次运行时直接读取
    # 缓存键: preprocessing 段 + normalization 段 + noise_patterns/bank_keywords
    # 资源内容 sha256 + 清洗代码版本号 (PREPROCESS_CODE_VERSION), 任一变更时
    # 自动使缓存失效 (fix omni-g-preprocess-04, 详见 compute_preprocess_cache_key)。
    config_hash = compute_preprocess_cache_key()
    logger.info(f"当前预处理配置哈希: {config_hash}")

    cache_dir = os.path.join(os.path.dirname(output_path), '_cache')
    os.makedirs(cache_dir, exist_ok=True)

    files_to_process = []
    cached_files = []
    for xlsx_file in xlsx_files:
        cache_path = os.path.join(
            cache_dir, os.path.basename(xlsx_file).replace('.xlsx', '.parquet')
        )
        # 缓存有效条件: 缓存文件存在 且 修改时间晚于源文件 且 配置哈希一致
        # 这确保当源 XLSX 内容更新或配置变更时, 缓存自动失效重新处理
        if (os.path.exists(cache_path)
                and os.path.getmtime(cache_path) > os.path.getmtime(xlsx_file)):
            try:
                cached_meta = pq.read_schema(cache_path).metadata or {}
                if cached_meta.get(b'config_hash', b'').decode() == config_hash:
                    cached_files.append(cache_path)
                    continue
                else:
                    logger.info(
                        f"  配置已变更, 缓存失效: {os.path.basename(cache_path)}"
                    )
            except Exception:
                pass
        files_to_process.append(xlsx_file)

    logger.info(
        f"增量处理: {len(cached_files)} 个已缓存, {len(files_to_process)} 个待处理"
    )

    writer = None
    total_rows = 0
    # 审计修复 (degradation F7): 逐源行数贡献 + 失败清单, 供处理后 found-vs-contributed
    # 对账 (旧实现单源读取/处理崩溃 → load.py return None → runner 静默 continue,
    # 整源记录从面板消失且无任何对账, R3 样本透明)。
    source_rows: dict[str, int] = {}
    failed_files: list[tuple[str, str]] = []

    # 工作进程数: 取 CPU 核心数和配置值的较小者, 防止内存溢出
    cpu_count = os.cpu_count() or 4
    num_workers = PARAMS.get('num_workers', min(cpu_count, 32))
    logger.info(f"并行工作进程: {num_workers} (CPU 核心数: {cpu_count})")
    log_memory_usage(logger, "并行处理开始前")

    # ── Step 1: 读取缓存 ──
    if cached_files:
        logger.info(f"读取 {len(cached_files)} 个缓存文件...")
        for cache_path in cached_files:
            try:
                table = pq.read_table(cache_path)
                if writer is None:
                    writer = pq.ParquetWriter(
                        output_path, table.schema, compression='snappy'
                    )
                writer.write_table(table)
                total_rows += table.num_rows
                _xlsx_name = os.path.basename(cache_path).replace('.parquet', '.xlsx')
                source_rows[_xlsx_name] = source_rows.get(_xlsx_name, 0) + table.num_rows
            except Exception as e:
                logger.warning(
                    f"缓存 {os.path.basename(cache_path)} 读取失败, 将重新处理: {e}"
                )
                xlsx_name = os.path.basename(cache_path).replace('.parquet', '.xlsx')
                xlsx_path = os.path.join(raw_data_dir, xlsx_name)
                if os.path.exists(xlsx_path) and xlsx_path not in files_to_process:
                    files_to_process.append(xlsx_path)
        logger.info(f"缓存数据加载完成: {total_rows:,} 行")

    # ── Step 2: 并行处理新文件 ──
    if files_to_process:
        completed = 0
        total_to_process = len(files_to_process)

        with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
            future_to_file = {
                executor.submit(_process_single_file, f): f
                for f in files_to_process
            }

            for future in concurrent.futures.as_completed(future_to_file):
                completed += 1
                source_file = future_to_file[future]
                file_name = os.path.basename(source_file)

                try:
                    df_cleaned = future.result()
                except Exception as e:
                    logger.error(f"处理 {file_name} 异常: {e}")
                    failed_files.append((file_name, str(e)))
                    source_rows.setdefault(file_name, 0)
                    continue

                if df_cleaned is not None and not df_cleaned.empty:
                    source_rows[file_name] = source_rows.get(file_name, 0) + len(df_cleaned)
                    table = pa.Table.from_pandas(df_cleaned)
                    if writer is None:
                        writer = pq.ParquetWriter(
                            output_path, table.schema, compression='snappy'
                        )
                    writer.write_table(table)
                    total_rows += len(df_cleaned)

                    # 写入增量缓存
                    cache_path = os.path.join(
                        cache_dir, file_name.replace('.xlsx', '.parquet')
                    )
                    try:
                        existing_meta = table.schema.metadata or {}
                        new_meta = {**existing_meta,
                                    b'config_hash': config_hash.encode()}
                        table = table.replace_schema_metadata(new_meta)
                        pq.write_table(table, cache_path, compression='snappy')
                    except Exception as e:
                        logger.warning(f"缓存写入失败 {cache_path}: {e}")

                    del df_cleaned, table

                logger.info(
                    f"进度: [{completed}/{total_to_process}] {file_name} | "
                    f"累计 {total_rows:,} 行"
                )

                # 每处理 5 个文件执行一次垃圾回收, 控制内存峰值
                if completed % 5 == 0:
                    gc.collect()

    if writer:
        writer.close()
        logger.info(f"数据加载完成, 共 {total_rows:,} 行 → {output_path}")
    else:
        logger.warning("所有文件均为空或无法处理, 未生成输出文件")

    # ── 审计修复 (degradation F7): 源文件 found-vs-contributed 对账 ──
    # 把"发现 N 源 / 贡献 M 源 / 零贡献 K 源"写入产物级 sidecar, 使源记录静默丢失对
    # referee/data-editor 可见 (旧实现仅 logger.error 埋日志)。**所有零贡献源** (合法
    # 空源 + 处理失败源) 都进 zero_contribution_files 可见 — 这是丢源可见性的关键保证。
    # failed_files 仅是其子集: 只捕获**逃出 worker 进程**的崩溃 (BrokenProcessPool /
    # 结果不可 pickle / OOM kill); 大多数 per-file 处理异常被 load.py:179-181 在 worker
    # 内 catch→return None, 经 df_cleaned is None 落入 zero_contribution_files (非
    # failed_files)。设 NEWS_PROCESS_STRICT_SOURCES=1 可在有失败/零贡献时 fail-loud。
    all_sources = [os.path.basename(f) for f in xlsx_files]
    zero_contrib = [s for s in all_sources if source_rows.get(s, 0) == 0]
    n_contributed = sum(1 for s in all_sources if source_rows.get(s, 0) > 0)
    recon = {
        'n_found': len(all_sources),
        'n_contributed': n_contributed,
        'n_zero_contribution': len(zero_contrib),
        'total_rows': total_rows,
        'failed_files': [{'file': f, 'error': e} for f, e in failed_files],
        'zero_contribution_files': zero_contrib,
        'per_source_rows': {s: source_rows.get(s, 0) for s in all_sources},
    }
    try:
        recon_path = os.path.join(os.path.dirname(output_path),
                                  'source_reconciliation.json')
        with open(recon_path, 'w', encoding='utf-8') as _f:
            json.dump(recon, _f, ensure_ascii=False, indent=2)
        logger.info(f"源文件对账已落盘: {recon_path}")
    except Exception as e:
        logger.warning(f"source_reconciliation.json 写入失败: {e}")

    if failed_files or zero_contrib:
        logger.error(
            f"⚠ 源文件对账[degradation F7]: 发现 {recon['n_found']} 源 / "
            f"贡献 {n_contributed} 源 / 零贡献 {len(zero_contrib)} 源 "
            f"(其中处理失败 {len(failed_files)} 源). 零贡献源已记入 "
            f"source_reconciliation.json — 勿默认'全部源已纳入面板'; "
            f"设 NEWS_PROCESS_STRICT_SOURCES=1 可在此 fail-loud。"
        )
        if os.environ.get('NEWS_PROCESS_STRICT_SOURCES', '').strip().lower() in (
                '1', 'true', 'yes', 'on'):
            raise RuntimeError(
                f"[STRICT_SOURCES] {len(failed_files)} 源处理失败 / "
                f"{len(zero_contrib)} 源零贡献; 详见 source_reconciliation.json"
            )
    else:
        logger.info(f"源文件对账: 发现={recon['n_found']} 源, 全部贡献 (>0 行)。")

    log_memory_usage(logger, "并行处理完成后")
    return total_rows


# ============================================================================
# 主函数
# ============================================================================


def main() -> None:
    """主执行函数: 数据加载 → 文本标准化 → 过滤 → 去重."""
    stage_start = time.time()
    logger.info(f"{'='*70}")
    logger.info(f"=== 开始执行: {STAGE_NAME} ===")
    logger.info(f"{'='*70}")
    logger.info("")
    logger.info("  📌 阶段目的")
    logger.info("     将 176 个原始 XLSX 文件 (~37GB, ~1700万条) 处理为干净的 Parquet 文件。")
    logger.info("     核心步骤: 加载 → 过滤(地域/媒体/广告/银行关键词) → 文本标准化")
    logger.info("     → 长度过滤 → 精确去重 → 近似去重(MinHash LSH)")
    logger.info("")
    logger.info("  📖 方法论依据")
    logger.info("     · 近似去重: MinHash LSH 算法 (Broder, 1997, SEQUENCES '97)")
    logger.info("       128 个置换函数保证 Jaccard 相似度估计的标准差 ≈ 1/√128 ≈ 8.8%")
    logger.info("     · 时间窗口: 5 个工作日内的近似重复视为转载, 保留首发源")
    logger.info("     · Aho-Corasick 自动机: O(n+m) 多模式匹配, 用于银行关键词过滤")
    logger.info("")
    logger.info("  📊 关键指标解读")
    logger.info("     · 去重保留率: 85%-95% 为健康范围, <80% 需排查数据源质量")
    logger.info("     · Jaccard 阈值: 由 config.yaml 控制 (config 默认 0.8), 越高 → 去重越保守")
    logger.info("       [学术支持]: The informational content of key audit matters 及 胡俊(2021)")
    logger.info("       均印证 ≥ 0.8/0.85 为合理的文本高度相似/冗余判别门槛")
    logger.info("     · MinHash 签名: 128 个置换 = 精度与速度的工业级平衡点")
    logger.info("")
    log_memory_usage(logger, "阶段启动")

    output_dir = CONFIG['paths']['output_dir']
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(
        output_dir, CONFIG['filenames']['output_00_preprocessing']
    )

    # ── 数据加载、过滤和标准化 ──
    load_rows = load_and_process_data(CONFIG['paths']['raw_data_dir'], output_path)

    # ── 媒体名称映射后处理 + 去重 ──
    if os.path.exists(output_path):
        logger.info("读取合并数据...")
        df = pd.read_parquet(output_path)
        df = df.reset_index(drop=True)
        input_rows = len(df)
        log_memory_usage(logger, "去重前")

        if not df.empty:
            # ── 媒体名称全局映射 (使用模块级常量 MEDIA_NAME_OVERRIDES) ──
            # 注意: filter.py:_clean_and_filter_dataframe 中的 override 仅在
            # 处理新 xlsx 时执行, 增量缓存命中时会被跳过。此处作为兜底,
            # 确保映射始终作用于全量数据。
            if '媒体(中文)' in df.columns:
                replaced = df['媒体(中文)'].replace(MEDIA_NAME_OVERRIDES)
                n_changed = (replaced != df['媒体(中文)']).sum()
                if n_changed > 0:
                    df['媒体(中文)'] = replaced
                    logger.info(f"媒体名称全局映射: {n_changed:,} 条记录已更新")
                else:
                    logger.info("媒体名称全局映射: 无需更新")

            # ── 去重 ──
            logger.info("执行去重...")
            deduplicator = ArticleDeduplicator(config=CONFIG, logger_instance=logger)
            df = deduplicator.run(df)

            logger.info(f"写入去重结果 → {output_path}")
            table = pa.Table.from_pandas(df, preserve_index=False)
            pq.write_table(
                table, output_path,
                compression='snappy',     # Snappy: 压缩比 ~2:1, 解压缩极快 (~250MB/s)
                row_group_size=100_000,   # 每组 10 万行: 平衡列存储压缩率与读取粒度
                use_dictionary=True,      # 字符串列字典编码, 重复值多时显著节省空间
                write_statistics=True,    # 列统计 (min/max), 加速后续谓词下推过滤
            )

            # 生成 CSV 预览 (前 2000 行, 便于用 Excel 快速检查)
            preview_path = output_path.replace('.parquet', '.csv')
            safe_save_preview_csv(df, preview_path, logger)

            output_rows = len(df)
        else:
            output_rows = 0
    else:
        input_rows = load_rows
        output_rows = load_rows

    # ── 阶段摘要 ──
    log_stage_summary(
        logger, STAGE_NAME, stage_start,
        input_rows=input_rows, output_rows=output_rows,
        extra_info={"加载总行数": f"{load_rows:,}"}
    )
    logger.info(f"=== 完成: {STAGE_NAME} ===")


if __name__ == "__main__":
    main()
