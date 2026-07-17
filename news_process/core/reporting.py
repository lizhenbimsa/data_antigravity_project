"""news_process.core.reporting — 数据集持久化 + DataFrame 与流水线报告。

由三个历史模块合并而来:
  - ``utils/helpers.py``   reporting helpers   → ``save_dataset`` / ``safe_save_preview_csv``
  - ``utils/reporting.py`` DataFrame 分析      → ``generate_dataframe_report`` / ``_format_stat`` / ``_is_categorical``
  - ``utils/pipeline_reporting.py``            → ``generate_pipeline_summary``

公开 API 表面 (历史 ``utils/*.py`` shim 已转发):
``save_dataset``、``safe_save_preview_csv``、``generate_dataframe_report``、
``_format_stat``、``_is_categorical``、``generate_pipeline_summary``。
"""

from __future__ import annotations

import logging
import os

import pandas as pd
import pyarrow.parquet as pq

from news_process.core.logging import pct4, sig4

# ============================================================================
# 1. 数据集持久化 (Parquet + CSV 预览)。来源于 utils/helpers.py。
# ============================================================================


def safe_save_preview_csv(df: pd.DataFrame, preview_path: str, logger=None):
    """保存前 5,000 行为 CSV 预览, 静默吞掉 PermissionError。

    CSV 预览是非关键路径: 写入失败 (典型情形是 Excel 已打开占用) 不应该
    中断主流水线。本函数记录 warning 并继续执行。
    """
    try:
        df_preview = df.head(5000) if hasattr(df, 'head') else df
        df_preview.to_csv(preview_path, index=False, encoding='utf-8-sig')
        if logger:
            logger.info(f"已生成预览文件: {preview_path}")
    except PermissionError as e:
        if logger:
            logger.warning(
                f"无法保存预览文件 (可能正被其它软件占用): {preview_path} | {e}"
            )
    except Exception as e:
        if logger:
            logger.error(f"保存预览文件时发生未知错误: {preview_path} | {e}")


def save_dataset(
    df: pd.DataFrame,
    output_path: str,
    logger=None,
    stage_name: str = None,
    config: dict = None,
    input_files: list = None,
    extra_schema_metadata: dict = None,
):
    """将 ``df`` 同时持久化为 Parquet + CSV 预览, 两者共享 ``output_path`` 词干。

    ``.parquet`` 是契约格式, 失败会抛异常; 同词干的 ``.csv`` 是非关键预览,
    写入失败不会抛异常。

    Args:
        df: 要保存的 DataFrame
        output_path: 输出文件路径
        logger: 日志记录器
        stage_name: 阶段名称（可选，用于数据版本控制）
        config: 配置字典（可选，用于数据版本控制）
        input_files: 依赖的输入文件列表（可选，用于数据版本控制）
        extra_schema_metadata: 额外 pyarrow schema metadata (bytes→bytes), 透传给
            ``save_parquet_with_metadata``（仅当 stage_name+config 均提供时生效；
            V9-PRE-1: stage 21 用它记录 ``b"news_process.prompt_version"``）
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        # 如果提供了版本控制参数，使用save_parquet_with_metadata
        if stage_name and config is not None:
            from news_process.core.data_versioning import save_parquet_with_metadata
            save_parquet_with_metadata(
                df=df,
                output_path=output_path,
                stage_name=stage_name,
                config=config,
                input_files=input_files,
                extra_schema_metadata=extra_schema_metadata,
            )
        else:
            # 向后兼容：没有版本控制参数时使用原始方法
            if extra_schema_metadata and logger:
                # V9-PRE-1: 向后兼容分支不支持自定义 schema metadata (无 save_parquet_with_metadata
                # 承载点) —— 如实告警而非静默丢弃调用方的意图, 但不因此升级为异常。
                logger.warning(
                    "save_dataset: extra_schema_metadata 已提供但缺 stage_name/config "
                    "(向后兼容 to_parquet 分支不支持附加 schema metadata) — 已忽略"
                )
            df.to_parquet(output_path, index=False)

        if logger:
            logger.info(
                f"已保存 parquet 文件: {output_path}  ({len(df):,} 行)"
            )
    except Exception as e:
        if logger:
            logger.error(f"保存 parquet 文件失败: {output_path} | {e}")
        raise

    csv_path = os.path.splitext(output_path)[0] + ".csv"
    safe_save_preview_csv(df, csv_path, logger)


# ============================================================================
# 2. DataFrame 分析报告。逐字搬运自 utils/reporting.py。
# ============================================================================


def _format_stat(value, precision=2):
    """格式化数值用于日志输出; NaN 返回 ``"N/A"``。

    项目规范 (2026-06-24): 日志中所有非整数数字一律经 :func:`sig4` 渲染为四位
    有效数字。``precision`` 形参保留以维持调用方签名向后兼容, 但实际有效数字位数
    统一由 sig4 决定。本返回值**只用于 logger 打印**, 绝不写入产物列 (golden-safe)。
    """
    if pd.isna(value):
        return "N/A"
    if isinstance(value, (int, float)):
        return sig4(value)
    return str(value)


def _is_categorical(dtype):
    """pandas >= 2.1 兼容的 categorical-dtype 检测。"""
    return isinstance(dtype, pd.CategoricalDtype)


def generate_dataframe_report(df: pd.DataFrame, logger: logging.Logger):
    """向 ``logger`` 输出 ``df`` 的详细统计报告。

    报告分两节:
      1. 整体概览: shape、重复行数、内存占用、dtype 分布。
      2. 逐列分析: 缺失率、唯一值数、类型自适应统计
         (数值五数概括 / datetime 范围 / 布尔值计数 /
         categorical-or-object 值分布)。

    防御性设计: 任何内部失败均以 WARNING 级别打印, 不抛异常 — 保证
    报告生成不会破坏宿主流水线。
    """
    try:
        logger.info("\n" + "=" * 60)
        logger.info(" DataFrame 统计报告 (DataFrame Statistics Report)")
        logger.info("=" * 60)

        if df.empty:
            logger.warning("输入数据为空，无法生成详细统计报告。")
            logger.info("=" * 60 + "\n")
            return

        total_rows = len(df)
        logger.info(
            f"数据维度 (Shape): {df.shape[0]:,} 行, {df.shape[1]} 列"
        )

        duplicate_rows = df.duplicated().sum()
        duplicate_fraction = (
            (duplicate_rows / total_rows) if total_rows > 0 else 0
        )
        logger.info(
            f"重复行数 (Duplicate Rows): {duplicate_rows:,} "
            f"({pct4(duplicate_fraction)})"
        )

        memory_usage_bytes = df.memory_usage(deep=True).sum()
        if memory_usage_bytes < 1024 ** 2:
            memory_usage, unit = memory_usage_bytes / 1024, "KB"
        elif memory_usage_bytes < 1024 ** 3:
            memory_usage, unit = memory_usage_bytes / (1024 ** 2), "MB"
        else:
            memory_usage, unit = memory_usage_bytes / (1024 ** 3), "GB"
        logger.info(f"内存占用 (Memory Usage): {sig4(memory_usage)} {unit}")

        logger.info("数据类型概览 (Data Types Summary):")
        dtype_counts_str = df.dtypes.value_counts().to_string()
        indented = "\n".join(
            [f"    {line}" for line in dtype_counts_str.split('\n')]
        )
        logger.info(indented)

        logger.info("\n" + "-" * 60)
        logger.info(" 字段逐一分析报告 (Column Analysis Report)")
        logger.info("-" * 60)

        for column in df.columns:
            col_series = df[column]
            dtype = col_series.dtype

            logger.info(f"\n--- 字段 (Column): '{column}' ---")
            logger.info(f"    - 数据类型 (Dtype): {dtype}")

            missing_count = col_series.isnull().sum()
            if total_rows > 0:
                missing_fraction = missing_count / total_rows
                logger.info(
                    f"    - 缺失值 (Missing Values): "
                    f"{missing_count:,} ({pct4(missing_fraction)})"
                )
            else:
                logger.info(
                    f"    - 缺失值 (Missing Values): {missing_count:,} (N/A%)"
                )

            unique_count = col_series.nunique()
            logger.info(f"    - 唯一值数量 (Unique Values): {unique_count:,}")

            if col_series.isnull().all():
                logger.info("    - 该字段所有值均为空。")

            elif pd.api.types.is_numeric_dtype(dtype):
                stats = col_series.describe()
                logger.info("    - 数值统计 (Numeric Stats):")
                logger.info(
                    f"      - 均值 (mean): {_format_stat(stats.get('mean'))}"
                )
                logger.info(
                    f"      - 标准差 (std): {_format_stat(stats.get('std'))}"
                )
                logger.info(
                    f"      - 最小值 (min): {_format_stat(stats.get('min'))}"
                )
                logger.info(
                    f"      - 25% 分位数: {_format_stat(stats.get('25%'))}"
                )
                logger.info(
                    f"      - 中位数 (50%): {_format_stat(stats.get('50%'))}"
                )
                logger.info(
                    f"      - 75% 分位数: {_format_stat(stats.get('75%'))}"
                )
                logger.info(
                    f"      - 最大值 (max): {_format_stat(stats.get('max'))}"
                )

            elif pd.api.types.is_datetime64_any_dtype(dtype):
                logger.info("    - 日期时间统计 (Datetime Stats):")
                min_date, max_date = col_series.min(), col_series.max()
                logger.info(f"      - 最早时间 (Earliest): {min_date}")
                logger.info(f"      - 最晚时间 (Latest):   {max_date}")
                if pd.notna(min_date) and pd.notna(max_date):
                    logger.info(
                        f"      - 时间跨度 (Duration):  {max_date - min_date}"
                    )

            elif pd.api.types.is_bool_dtype(dtype):
                logger.info("    - 布尔值分布 (Boolean Value Counts):")
                logger.info(
                    f"\n{col_series.value_counts(dropna=False).to_string()}"
                )

            elif pd.api.types.is_object_dtype(dtype) or _is_categorical(dtype):
                if unique_count <= 15:
                    logger.info("    - 值分布 (Value Counts):")
                    logger.info(
                        f"\n{col_series.value_counts(dropna=False).to_string()}"
                    )
                else:
                    logger.info(
                        "    - 最常见的5个值 (Top 5 Most Common Values):"
                    )
                    logger.info(
                        f"\n{col_series.value_counts().head(5).to_string()}"
                    )

        logger.info("\n" + "=" * 60)
        logger.info(" 报告结束 (End of Report)")
        logger.info("=" * 60 + "\n")

    except Exception as e:
        logger.warning(
            f"生成统计报告时发生错误（不影响数据处理）: {e}",
            exc_info=True,
        )


# ============================================================================
# 3. 流水线收尾的数据流转摘要。来源于 utils/pipeline_reporting.py。
# ============================================================================


def _log_environment_and_config(config, logger, output_dir: str,
                                n_article_stages: int, n_panel_stages: int) -> None:
    """打印 ① 项目/环境信息 + ② 输入/输出位置 + ③ 运行配置 + ④ 方法论依据 (日志富集, 2026-06-24)。

    把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数、报告口径的学术出处"一次性
    落进日志, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 (golden-safe)。
    ④ 方法论引文仅 emit 经 Crossref 真值核验的条目, 含 DOI 可访问链接 (Gebru et al. 2021
    CACM https://doi.org/10.1145/3458723; Mitchell et al. 2019 FAccT
    https://doi.org/10.1145/3287560.3287596), 绝不伪造 DOI (playbook §4 铁律)。
    """
    try:
        import platform
        import sys

        logger.info("  🧭 项目 / 环境信息")
        logger.info("     · 阶段: 流水线收尾摘要 (Pipeline Summary; 全流程数据流转 + 面板尺寸盘点)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) v3.16.0")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "本模块纯读 parquet footer / 全量加载末阶段 → 无 LLM·Embedding·网络·API ($0)")

        logger.info("  📂 输入 / 输出位置")
        logger.info(f"     · 数据目录: {output_dir} (各阶段 .parquet 产物所在)")
        logger.info("     · 报告去向: 仅写日志 (不落任何产物文件; 行计数走 pyarrow footer 廉价读)")

        filenames = config.get('filenames', {}) if isinstance(config, dict) else {}
        logger.info("  ⚙ 运行配置 (盘点对象)")
        logger.info(f"     · 文章级数据流转阶段数: {n_article_stages:,d} (00 预处理 → 24 跟风衰减)")
        logger.info(f"     · 面板级盘点阶段数:   {n_panel_stages:,d} (40 主面板 / 40 文章-银行级 / 51 证伪控制)")
        logger.info(f"     · 已登记输出文件名键: {len(filenames):,d} (config['filenames'])")
        logger.info("     · 末阶段全量统计: generate_dataframe_report (缺失率/唯一值/数值五数概括, 数字经 sig4)")

        logger.info("  📖 方法论依据 (数据/流水线报告标准)")
        logger.info("     · 数据集文档化标准: Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., "
                    "Wallach, H., Daumé III, H., & Crawford, K. (2021). Datasheets for datasets. "
                    "Communications of the ACM, 64(12), 86-92. https://doi.org/10.1145/3458723")
        logger.info("       → 摘要报告逐阶段记录行数/保留率/差值, 是 datasheet 'composition / collection' 维度的运行期实现")
        logger.info("     · 模型/产物报告卡片: Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., "
                    "Hutchinson, B., Spitzer, E., Raji, I. D., & Gebru, T. (2019). Model cards for model "
                    "reporting. Proceedings of the Conference on Fairness, Accountability, and Transparency "
                    "(FAccT '19), 220-229. https://doi.org/10.1145/3287560.3287596")
        logger.info("       → 末阶段 dtype/缺失率/数值分布报告对应 model card 的 'quantitative analyses' 透明度披露")
        logger.info("     · LLM 标注可复现性: Cheng, X., Mayya, R., & Sedoc, J. (2024). To err is "
                    "human; to annotate, SILICON? Toward robust reproducibility in LLM annotation "
                    "(arXiv:2412.14461). arXiv. https://doi.org/10.48550/arXiv.2412.14461")
        logger.info("       → 摘要表逐阶段披露 LLM 标注列 (stage 21 tone_llms) 经过的留篇/聚合行集, "
                    "为'LLM 生成的情感分数如何被记录与离线复现'提供运行期审计轨迹")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法信息打印失败 (不影响处理): {e}")


def generate_pipeline_summary(config, logger):
    """打印一次完整运行结束后的流水线摘要报告。

    报告分两个粒度:
      1. 文章级数据流转 (00 -> 24): 每阶段的行数、与上一阶段的差值、
         相对最初阶段的保留率。
      2. Bank-Year 面板摘要 (45 / 51): 行数 x 列数。

    使用 ``pyarrow.parquet.read_metadata`` 进行廉价行计数 (只读 parquet
    footer, 不全量加载); 然后对最终阶段全量加载, 调用
    ``generate_dataframe_report`` 输出完整统计。
    """
    import time
    _t_start = time.time()
    # 运行期阶段计时累计 (各主要子阶段墙钟耗时, 末尾汇总打印; 纯日志, golden-safe)
    phase_durations: dict[str, float] = {}

    logger.info("\n" + "=" * 70)
    logger.info("===          数据管道执行摘要报告 (Pipeline Summary)         ===")
    logger.info("=" * 70)
    logger.info("【功能】把一整次流水线跑完后'每个阶段还剩多少条新闻、面板有多大'盘点成一张表,")
    logger.info("        让人一眼看出数据在哪一步被过滤掉多少 (排错/复现/审计的总览仪表盘)。")
    logger.info("【方法】对 00→24 各阶段 parquet 只读 footer 取行数 (廉价, 不全量加载), 计算与上一")
    logger.info("        阶段的差值 + 相对最初阶段的保留率; 末阶段全量加载出完整 dtype/缺失/分布统计;")
    logger.info("        再盘点 40/51 面板阶段的行数×列数。")
    logger.info("【判读】保留率逐阶段单调下降属正常 (每步在过滤); 某步骤骤降 = 该阶段过滤过猛, 需复核。")
    logger.info("        Change(%) 为相对上一阶段的增减 (12b 共现硬过滤会为负)。")
    logger.info("【确定性】纯读盘 + 计数, 无 LLM/Embedding/网络/API ($0); 输出仅落日志, 不改任何产物 (golden-safe)。")

    output_dir = config['paths']['output_dir']

    # 阶段清单 = 单一事实源 (env banner 计数与下方循环共用 → 计数永不与列表漂移)。
    stages = [
        ("模块一: 00_preprocessing", "output_00_preprocessing"),
        ("模块二: 11_news_bank", "output_11_bank_news"),
        ("模块二: 12_news_fintech", "output_12_fintech_news"),
        # 12b 银行×金科邻近共现硬过滤 (v3.10.0): 丢行, 故行数会下降,
        # 须列入摘要否则保留率会漏掉这一步硬过滤 (12 与 13 之间)。
        ("模块二: 13_cooccurrence_filter", "output_12b_cooccurrence"),
        ("模块二: 15_fintech_intensity", "output_14_fintech_intensity"),
        ("模块三: 21_tone_llms", "output_21_tone_llms"),
        ("模块三: 21_tone_llms(全量)", "output_21_tone_llms_full"),
        ("模块三: 22_tone_words", "output_22_words_tone"),
        ("模块三: 23_tone_berts", "output_23_bert_tone"),
        ("模块三: 24_herd_decay", "output_24_herd_decay"),
    ]
    # 面板级盘点清单 (移至此, 同样作为 banner 计数的单一事实源; 循环在下方复用)。
    panel_stages = [
        ("模块五: 40_panel_export_main", "output_40_panel_yearly"),
        ("模块五: 40_article_bank", "output_40_article_bank"),
        ("模块六: 51_falsification", "output_51_panel_controls"),
    ]
    _log_environment_and_config(
        config, logger, output_dir, len(stages), len(panel_stages),
    )

    summary_data = []
    previous_count = 0
    initial_count = 0

    import time as _time
    _t_flow = _time.time()
    for stage_name, filename_key in stages:
        filename = config['filenames'].get(filename_key)
        if not filename:
            logger.warning(
                f"阶段 {stage_name} 的输出文件名未在配置中找到 "
                f"(key: {filename_key})。"
            )
            continue

        file_path = os.path.join(output_dir, filename)

        try:
            current_count = 0
            if os.path.exists(file_path):
                metadata = pq.read_metadata(file_path)
                current_count = metadata.num_rows
            else:
                logger.warning(f"文件未找到: {file_path}")

            # plan m3: initial_count == 0 时分母为零, 旧实现强行返回 0.0%,
            # 容易被运维误读为"全丢光"; 现改为显式 "N/A" 字符串
            # 注: pct_change_str / retention_str 是**纯展示字符串** (经 sig4/pct4 渲染),
            # 仅塞进随后用于 to_string() 打印的临时 summary_df, 绝不落 parquet / 不返回
            # / 不进任何数值计算 → 符合 "sig4 输出只用于日志" 的铁律 (golden-safe)。
            if stage_name == "模块一: 00_preprocessing":
                change = 0
                # 首阶段约定增量为 0、保留率为 100%; 带符号前缀以与下游阶段口径一致
                pct_change_str = "+" + pct4(0.0, fraction=False)
                initial_count = current_count
                if initial_count > 0:
                    retention_str = pct4(1.0)
                else:
                    retention_str = "N/A"
            else:
                change = current_count - previous_count
                if previous_count > 0:
                    _pct = change / previous_count * 100
                    # 保留带符号前缀 (增/减一目了然), 量级走 sig4 四位有效数字
                    pct_change_str = ("+" if _pct >= 0 else "-") + pct4(abs(_pct), fraction=False)
                else:
                    pct_change_str = "N/A"
                if initial_count > 0:
                    retention_str = pct4(current_count / initial_count)
                else:
                    retention_str = "N/A"

            summary_data.append({
                "Stage": stage_name,
                "Rows": current_count,
                "Change": change,
                "Change (%)": pct_change_str,
                "Retention (vs Initial)": retention_str,
            })

            previous_count = current_count

        except Exception as e:
            logger.error(f"无法读取阶段 {stage_name} 的输出文件: {e}")
            summary_data.append({
                "Stage": stage_name,
                "Rows": "Error",
                "Change": "N/A",
                "Change (%)": "N/A",
                "Retention (vs Initial)": "N/A",
            })

    phase_durations['①文章级数据流转盘点'] = _time.time() - _t_flow

    summary_df = pd.DataFrame(summary_data)
    logger.info("\n数据流转统计 (Data Flow Summary):")
    logger.info("\n" + summary_df.to_string(index=False))

    final_stage_key = stages[-1][1]
    final_filename = config['filenames'].get(final_stage_key)
    if final_filename:
        final_file_path = os.path.join(output_dir, final_filename)
        if os.path.exists(final_file_path):
            logger.info(
                f"\n正在生成最终数据 ({final_filename}) 的详细统计报告..."
            )
            try:
                _t_final = _time.time()
                final_df = pd.read_parquet(final_file_path)
                generate_dataframe_report(final_df, logger)
                phase_durations['②末阶段全量统计报告'] = _time.time() - _t_final
            except Exception as e:
                logger.error(f"生成最终详细报告失败: {e}")
        else:
            logger.warning(
                f"最终输出文件不存在，无法生成详细统计: {final_file_path}"
            )

    _t_panel = _time.time()
    # panel_stages 已在函数顶部定义 (banner 计数单一事实源), 此处直接复用。
    panel_data = []
    for stage_name, filename_key in panel_stages:
        filename = config['filenames'].get(filename_key)
        if not filename:
            continue
        file_path = os.path.join(output_dir, filename)
        try:
            if os.path.exists(file_path):
                metadata = pq.read_metadata(file_path)
                panel_data.append({
                    "Stage": stage_name,
                    "Rows": metadata.num_rows,
                    "Columns": metadata.num_columns,
                })
            else:
                panel_data.append({
                    "Stage": stage_name,
                    "Rows": "未生成",
                    "Columns": "N/A",
                })
        except Exception as e:
            logger.error(
                f"无法读取面板阶段 {stage_name} 的输出: {e}"
            )
            panel_data.append({
                "Stage": stage_name,
                "Rows": "Error",
                "Columns": "N/A",
            })

    if panel_data:
        panel_summary_df = pd.DataFrame(panel_data)
        logger.info(
            "\n面板构建阶段统计 (Panel Construction Summary, Bank-Year 级):"
        )
        logger.info("\n" + panel_summary_df.to_string(index=False))

    phase_durations['③面板尺寸盘点'] = _time.time() - _t_panel

    # ── ⏱ 阶段计时汇总 (墙钟秒, sig4; 纯日志, golden-safe) ──
    _total = _time.time() - _t_start
    logger.info("  ⏱ 阶段计时 (墙钟秒)")
    for _name, _dur in phase_durations.items():
        _share = (_dur / _total) if _total > 0 else 0.0
        logger.info(f"     · {_name}: {sig4(_dur)} s ({pct4(_share)})")
    logger.info(f"     · 总计: {sig4(_total)} s")
