"""news_process.pipeline.audit.stats_excel — 阶段 82: 审计用统计表 Excel 导出。

由历史 ``news_process/82_export_stats_excel.py`` 在 Phase 1.4b **试点**
正文迁移而来。功能行为逐字保留; 仅变更物理路径, 且原 ``utils.helpers``
导入经 Phase 1 转发链解析至 ``news_process.core.*``。

Phase 1 状态: 此处为规范实现体。根目录 ``news_process/82_export_stats_excel.py``
为极薄 CLI 适配层, 仅转调本模块 ``main()``。

Phase 2 规划: (a) 将其余 23 个简易 CLI 正文迁入子包; (b) 将 22/23/35/38b/39
中依赖 ``__file__`` 的资源路径改为 ``CONFIG['paths'][...]`` (并在 ``paths.yaml``
增补 ``models_dir`` / ``eval_reports_dir`` 等键); (c) 原子迁移 15/45/库文件路径。

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 82_export_stats_excel.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**输入**: 按 4 个阶段读对应 parquet 的 3 个元数据列 (columns 限定读, 省内存) — 00_preprocessing / 11_bank_news / 12_fintech_news / 21_tone_llms (文件名经 config['filenames'] 的 output_00_preprocessing / output_11_bank_news / output_12_fintech_news / output_21_tone_llms 解析); 缺文件则 print 跳过该阶段。

**处理步骤 (main)**:
1. Windows 控制台 utf-8 重配 (失败静默 pass)。
2. 对每个阶段 × 每个统计字段 (媒体(中文) / 国家地区/省份 / 城市) 做 `df[col].fillna('(空值)').value_counts().reset_index()`, 列名命名为 [原字段名, 数量]; 字段列不存在则 print 警告跳过。
3. 经 openpyxl ExcelWriter 各写一个 sheet (sheet 名 `{label}_{中文后缀}` 截断 31 字符, Excel 上限), 输出单一 Excel `各阶段_媒体_地区_城市_统计.xlsx`。

**关键算法**: 纯 value_counts 频次分布, 无回归/聚合公式。

**外部依赖**: pandas + openpyxl; 无 LLM/Embedding/网络。无 timeout (不在 DAG)。确定性强。规范调用: `python -m news_process.pipeline.audit.stats_excel` 或 `python news_process/82_export_stats_excel.py`。

**DAG 位置**: 不在 DAG。是横切多阶段的描述性统计便利工具, 由用户手动触发, 与主链解耦。

■ 白话说明

**这一步是什么**: 这是个统计小帮手。它把流水线四个关键阶段 (原始预处理、银行新闻、金融科技新闻、LLM 打分后) 的新闻, 按哪家媒体发的、来自哪个省、哪个城市分别数一数各有多少条, 然后整理成一个多页的 Excel 表格, 每一页是一个阶段、一个维度的分布清单。打个比方: 就是把一大堆新闻按媒体/地区/城市分类点名, 做成一份花名册。

**为什么需要它**: 研究者想快速了解我的新闻数据都来自哪些媒体、覆盖哪些地区、各阶段筛选后样本怎么变化, 不用自己写代码, 跑一下就能拿到一份现成的 Excel 概览。论文的样本描述、数据来源说明、附录里的覆盖范围表常常要用到这些数字。

**做得好不好的影响**: 它不参与任何回归计算, 也不改面板数据, 纯粹是给人看的描述性统计。所以它好不好不会影响论文的核心结果, 但它能帮研究者快速发现样本是否偏向某几家媒体或某个地区 (代表性问题), 以及各阶段筛选掉了多少数据。属于了解自己数据家底的辅助工具, 想用就用、不用也不影响主流程。
========================================================================
"""

from __future__ import annotations

import logging
import os
import sys

import pandas as pd

from news_process.core.config import load_config

# 模块级 logger 占位; main() 内经 setup_logging 重绑为带 FileHandler 的实例
# (此前本模块只用 print, 无 logger; 现对齐同族 audit 阶段, 让日志落 <stage>.log)。
logger = logging.getLogger(__name__)


def main():
    """按阶段汇总媒体 / 省域 / 城市分布, 写入 Excel。"""
    # Windows 控制台 GBK 回退 (保持历史行为)。
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

    config = load_config()
    output_dir = config['paths']['output_dir']

    # 接入项目统一日志: 写 <log_dir>/82_export_stats_excel.log。
    # 此前本阶段仅用 print() 输出 (CLI 便利工具, 不在 DAG), 不落 <stage>.log。
    # 现对齐同族 audit 阶段的 setup_logging 约定, 让日志自带阶段用途说明与结果分析;
    # 原 print() 全部保留 (向后兼容外部 CLI 契约), 仅【新增】logger 调用。
    global logger
    from news_process.core.logging import pct4, setup_logging, sig4
    logger = setup_logging(
        "82_export_stats_excel",
        config['paths'].get('log_dir', 'logs'),
    )

    # 功能说明 banner — 写入 <stage>.log, 让日志自带阶段用途说明 (仿 39c)。
    logger.info("=" * 72)
    logger.info("阶段 82: 各阶段媒体/地区/城市描述性统计 Excel 导出 (value_counts 频次分布)")
    logger.info("=" * 72)
    logger.info("【功能】把流水线四个关键阶段 (00 预处理 / 11 银行新闻 / 12 金科新闻 / 21 LLM 打分后)")
    logger.info("        的新闻, 按发文媒体、来源省份、来源城市分别数频次, 写成多 sheet Excel,")
    logger.info("        供论文样本描述/数据来源说明/覆盖范围附录使用 (纯描述性, 不进面板/回归)。")
    logger.info("【方法】每阶段 × 每字段做 df[col].fillna('(空值)').value_counts(); 一个 sheet 一个分布;")
    logger.info("        无回归/聚合公式。外部依赖仅 pandas + openpyxl, 无 LLM/Embedding/网络, 确定性强。")
    logger.info("【判读】看 ① 各阶段行数的逐级漏斗 (筛选强度); ② 头部媒体/地区集中度 (代表性偏倚预警);")
    logger.info("        ③ 各字段不同取值数与空值占比 (元数据完整性)。本工具不影响论文核心结果。")

    # ------------------------------------------------------------------
    # ① 🧭 项目 / 环境信息 (ENV banner) — 运行环境指纹, 便于审计可复现性。
    # 纯 logger 输出, 不参与任何产物计算 (golden-safe, 失败不崩阶段)。
    # ------------------------------------------------------------------
    import time as _time
    phase_t: dict[str, float] = {}  # 仅供 per-phase 计时日志 (绝不回写产物)
    _t_overall = _time.time()
    try:
        import platform as _platform
        logger.info("-" * 72)
        logger.info("【环境】项目 = news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) v3.11.1")
        logger.info("        阶段 82 export_stats_excel — 审计 CLI, 不在 DAG, 用户手动触发, 与主链解耦。")
        logger.info(
            f"        Python {sys.version.split()[0]} @ {sys.executable}"
        )
        logger.info(
            f"        platform={_platform.platform()}  cpu={os.cpu_count()}  pid={os.getpid()}"
        )
        logger.info(
            f"        run_id={os.environ.get('NEWS_PROCESS_RUN_ID', '(unset)')}  cwd={os.getcwd()}"
        )
        logger.info(
            f"        module={os.path.abspath(__file__)}"
        )
        logger.info(
            "        成本/确定性: 纯 pandas+openpyxl value_counts, 无 LLM/Embedding/网络 = $0, 确定性强。"
        )
    except Exception as _e:
        logger.warning(f"[环境] ENV banner 输出异常, 跳过 (不影响产物): {_e}")

    # 仅供【结果分析】的日志变量 (绝不回写产物): 逐阶段行数 + 逐 sheet 摘要。
    stage_rowcounts: dict[str, int] = {}
    stage_field_summary: list[tuple[str, str, int, int, float, int]] = []
    missing_stages: list[str] = []
    missing_fields: list[str] = []

    stages = [
        {'label': '00_preprocessing',
         'filename': config['filenames'].get('output_00_preprocessing', '00_preprocessing.parquet')},
        {'label': '11_news_bank',
         'filename': config['filenames'].get('output_11_bank_news', '11_bank_news.parquet')},
        # 注 (2026-06-15): 读 stage 12b 邻近共现硬过滤【之前】的关键词金科阶段 (pre-12b);
        #   本审计逐阶段统计原始关键词口径, 非 12b 过滤后的分析宇宙 (后者经 13→21 链)。
        {'label': '12_news_fintech',
         'filename': config['filenames'].get('output_12_fintech_news', '12_fintech_news.parquet')},
        {'label': '21_tone_llms',
         'filename': config['filenames'].get('output_21_tone_llms', '21_tone_llms.parquet')},
    ]

    stat_fields = [
        ('媒体(中文)', '媒体'),
        ('国家地区/省份', '国家地区_省份'),
        ('城市', '城市'),
    ]

    output_excel = os.path.join(output_dir, '各阶段_媒体_地区_城市_统计.xlsx')
    print(f"输出文件: {output_excel}")

    # ------------------------------------------------------------------
    # ⚙ 运行配置 (CONFIG block) — 输入 parquet 集 / 输出路径 / 统计字段 / 阈值清单。
    # 此前这些信息散在 print(); 现集中 emit 进 <stage>.log 以便审计 (纯日志, golden-safe)。
    # 阈值字面值与下方【结果分析】块的常量同源 (HIGH_CONCENTRATION/HIGH_NULL), 仅作记录。
    # ------------------------------------------------------------------
    try:
        logger.info("-" * 72)
        logger.info("【配置】路径与可调参数 (来源 config: paths.yaml::output_dir + filenames::output_*):")
        logger.info(f"  · output_dir       = {output_dir}")
        logger.info(f"  · 输出 Excel       = {output_excel}")
        logger.info(
            f"  · 扫描阶段 ({len(stages):,} 个) = "
            + ", ".join(f"{s['label']}<-{s['filename']}" for s in stages)
        )
        logger.info(
            f"  · 统计字段 ({len(stat_fields):,} 个) = "
            + ", ".join(f"{f}->sheet后缀'{sfx}'" for f, sfx in stat_fields)
        )
        logger.info(
            "  · 阈值: 头部集中度告警 HIGH_CONCENTRATION="
            f"{sig4(0.50)} (头部单一取值占比 ≥ 此值视高集中); "
            f"空值告警 HIGH_NULL={sig4(0.20)} (空值占比 ≥ 此值视元数据偏低)。"
        )
        logger.info("  · sheet 名上限 = 31 字符 (Excel 约束, 超长截断); 缺文件/缺列则 print 跳过该项。")
    except Exception as _e:
        logger.warning(f"[配置] CONFIG block 输出异常, 跳过 (不影响产物): {_e}")

    _t_excel = _time.time()
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        for stage in stages:
            parquet_path = os.path.join(output_dir, stage['filename'])
            label = stage['label']

            if not os.path.exists(parquet_path):
                print(f"[跳过] {label}: 文件不存在 ({parquet_path})")
                missing_stages.append(label)  # 仅供结果分析日志
                continue

            print(f"[读取] {label}: {parquet_path}")
            cols_to_read = [f for f, _ in stat_fields]
            df = pd.read_parquet(parquet_path, columns=cols_to_read)
            print(f"  行数: {len(df):,}")
            stage_rowcounts[label] = len(df)  # 仅供结果分析日志

            for col_name, sheet_suffix in stat_fields:
                if col_name not in df.columns:
                    print(f"  [警告] 列 '{col_name}' 不存在于 {label}，跳过")
                    missing_fields.append(f"{label}.{col_name}")  # 仅供结果分析日志
                    continue

                sheet_name = f"{label}_{sheet_suffix}"[:31]  # Excel sheet 名上限 31 字符

                vc = df[col_name].fillna('(空值)').value_counts().reset_index()
                vc.columns = [col_name, '数量']
                vc.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"  [OK] Sheet '{sheet_name}': {len(vc)} 个不同值")

                # 仅供结果分析日志: 不同值数 / 总频次 / 头部值占比 / 空值条数 (不回写产物)。
                # crash-guard: 此块在 ExcelWriter 仍打开时执行, 若诊断计算抛异常 (如空表
                # iloc[0] / 计数转换), 异常会冲出 with 块致 Excel 未正常落盘 → 丢产物。
                # 包 try/except 后即便诊断失败也不影响 sheet 已写入的产物。
                try:
                    n_distinct = len(vc)
                    total_cnt = int(vc['数量'].sum())
                    top_share = (
                        float(vc['数量'].iloc[0]) / total_cnt
                        if (total_cnt > 0 and len(vc) > 0)
                        else 0.0
                    )
                    null_mask = vc[col_name] == '(空值)'
                    null_cnt = int(vc.loc[null_mask, '数量'].sum()) if null_mask.any() else 0
                    stage_field_summary.append(
                        (label, col_name, n_distinct, total_cnt, top_share, null_cnt)
                    )
                except Exception as _e:
                    logger.warning(
                        f"[结果分析] sheet '{sheet_name}' 诊断指标计算异常, 跳过"
                        f" (不影响产物): {_e}"
                    )

    print(f"\n已生成 Excel: {output_excel}")
    phase_t['read_count_write_excel'] = _time.time() - _t_excel

    # ------------------------------------------------------------------
    # 结果分析 — 写入日志: 逐阶段行数漏斗 + 各 sheet 集中度/完整性判读。
    # 纯描述性诊断, 取已算出的真实数值, 不改任何产物。
    # crash-guard: 整块包 try/except — 该块虽在 ExcelWriter 关闭【之后】执行
    # (产物已落盘), 但仍以 try/except 兜底, 确保任何诊断异常 (除零/空 dict/缺键)
    # 都不会让 stage 退出非零码或刷掉已生成的 Excel。golden-safe 不可证伪。
    # ------------------------------------------------------------------
    try:
        logger.info("-" * 72)
        logger.info("【结果分析】各阶段样本漏斗与字段分布 (描述性, 仅供数据家底体检, 不进回归):")

        # ① 逐级漏斗: 00 全量 → 11 银行 → 12 金科(关键词) → 21 LLM 验证。
        # 观测单位差异 (关键判读前提): 00 为【文章级】, 11/12/21 为【firm-document 级】
        # (一篇讲多家银行会展开成多条物理行, 见 PIPELINE_NUMBERED_PY_REFERENCE)。
        # 故 00→11 行数比是【跨观测单位比】(文章级→firm-doc 级), 非严格保留率, 行数可合法 >00;
        # 只有同为 firm-doc 级的 11→12→21 才是真子集, 其"本步保留率"才有单调收窄的预期意义。
        funnel_order = ['00_preprocessing', '11_news_bank', '12_news_fintech', '21_tone_llms']
        # firm-document 展开起点: 该阶段之前 (即从 00 跨到它) 属跨观测单位比, 不打反增警告。
        firmdoc_expansion_step = '11_news_bank'
        present_funnel = [s for s in funnel_order if s in stage_rowcounts]
        if present_funnel:
            base = stage_rowcounts[present_funnel[0]]
            logger.info(f"  样本漏斗 (相邻阶段保留率 + 相对首阶段 {present_funnel[0]} 累计占比):")
            prev_label = None
            prev_n = None
            for s in present_funnel:
                n = stage_rowcounts[s]
                cum_share = (n / base) if base > 0 else 0.0
                # 用 prev_label is None 精确判"真首阶段" (仅首轮迭代为 None), 与"上一阶段 0 行"分开。
                if prev_label is None:
                    logger.info(f"    {s}: {n:,} 篇 (基准)")
                elif not prev_n:  # 上一阶段存在但 0 行: 保留率无意义, 不误标为漏斗起点
                    logger.info(
                        f"    {prev_label} → {s}: {n:,} 篇  上一阶段 0 行, 本步保留率无意义  "
                        f"累计占首阶段={pct4(cum_share)}"
                    )
                else:
                    step_ratio = n / prev_n
                    if s == firmdoc_expansion_step:
                        # 00(文章级)→11(firm-doc 级): 跨观测单位, 行数 >00 属 firm-document 展开, 非异常
                        note = "  (11 为 firm-document 展开, 行数可 >00 属正常, 此比非严格保留率)"
                    else:
                        # 同口径 firm-doc 阶段对 (11→12, 12→21): 才用子集保留率, 反增才提示
                        note = "" if step_ratio <= 1.0 + 1e-9 else "  ⚠ 反增(本阶段非上阶段子集?)"
                    logger.info(
                        f"    {prev_label} → {s}: {n:,} 篇  本步比值={pct4(step_ratio)}  "
                        f"累计占首阶段={pct4(cum_share)}{note}"
                    )
                prev_label, prev_n = s, n
        else:
            logger.info("  (无任何阶段成功读入, 无法绘制漏斗)")

        # ② 各 sheet 集中度与完整性: 头部取值占比 (代表性偏倚) + 不同值数 + 空值占比。
        # 头部占比越高 = 样本越向少数媒体/地区集中 = 代表性预警; 空值占比高 = 元数据缺失。
        HIGH_CONCENTRATION = 0.50  # 头部单一取值 >50% 视作高集中, 论文需披露代表性局限
        HIGH_NULL = 0.20           # 空值 >20% 视作元数据完整性偏低
        if stage_field_summary:
            logger.info("  逐字段分布 (头部占比越低=越分散; 空值占比越低=元数据越全):")
            for label, col_name, n_distinct, total_cnt, top_share, null_cnt in stage_field_summary:
                null_share = (null_cnt / total_cnt) if total_cnt > 0 else 0.0
                flags = []
                if top_share >= HIGH_CONCENTRATION:
                    flags.append("高集中(代表性预警)")
                if null_share >= HIGH_NULL:
                    flags.append("空值偏高(元数据缺失)")
                verdict = ("  ⚠ " + " / ".join(flags)) if flags else "  ✓ 分布健康"
                logger.info(
                    f"    {label} · {col_name}: 不同取值={n_distinct:,} 个  "
                    f"头部占比={pct4(top_share)}  空值占比={pct4(null_share)}{verdict}"
                )
        else:
            logger.info("  (无任何字段成功统计)")

        # ③ 小样本警告: 盘面 T=2 仅验证管道正确性, 结论以全量为准。
        max_rows = max(stage_rowcounts.values()) if stage_rowcounts else 0
        if 0 < max_rows < 100000:
            logger.info(
                f"  ⚠ 最大阶段样本 = {max_rows:,} 篇 (盘面 T=2 小样本, 仅验证管道与 Excel 导出正确性,"
                " 媒体/地区覆盖结论以全量 17M/T=18 实测为准)"
            )

        # ④ 优雅降级警告: 缺文件 / 缺字段。
        if missing_stages:
            logger.warning(
                f"  缺失阶段产物 (跳过, 该阶段在 Excel 中无 sheet): {', '.join(missing_stages)} "
                "— 上游阶段未跑或文件不在 output_dir; 不影响其余阶段导出。"
            )
        if missing_fields:
            logger.warning(
                f"  缺失统计字段 (跳过对应 sheet): {', '.join(missing_fields)} "
                "— 该阶段 parquet 不含此元数据列 (如 21 阶段精筛后可能丢列); 仅影响该字段分布。"
            )
        # ⑤ ⏱ 阶段计时: 读盘+频次+写 Excel 主相 + 全程墙钟 (秒, 4 位有效数字)。
        try:
            phase_t['total_wall'] = _time.time() - _t_overall
            logger.info("  ⏱ 阶段计时 (墙钟, 秒):")
            logger.info(
                f"    读盘+value_counts+写 Excel = {sig4(phase_t.get('read_count_write_excel', 0.0))} s"
            )
            logger.info(f"    全程 (含环境/配置/结果分析日志) = {sig4(phase_t['total_wall'])} s")
        except Exception as _te:
            logger.warning(f"[计时] per-phase 计时输出异常, 跳过 (不影响产物): {_te}")

        logger.info("-" * 72)
        logger.info(
            f"  ✓ stage 82 done; 成功统计阶段={len(stage_rowcounts)} 个 / "
            f"sheet={len(stage_field_summary)} 张; 输出 = {output_excel}"
        )
    except Exception as _e:
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过 (不影响产物): {_e}")


if __name__ == '__main__':
    main()
