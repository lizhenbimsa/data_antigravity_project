"""
news_process.validation.dedup_threshold — 去重阈值参数敏感性分析 (全量数据版)

迁移说明 (Phase 7b)：
    本模块由原 root script ``32a_dedup_threshold_sensitivity.py`` body 迁入。
    规范调用方式: ``python -m news_process.validation.dedup_threshold``

=============================================================================

功能：
    针对 LLM 语义精筛后的最终分析数据集 (21_tone_llms.parquet)，
    使用 Jaccard MinHash 分别测试截断点阈值 [0.75, 0.80, 0.85, 0.90]，
    输出去重敏感性统计表，供实证检验附件使用。

    本阶段用于证明生产去重阈值 (config.yaml: deduplication.jaccard_similarity_threshold)
    的选择不影响核心结论，属于学术论文附录中的参数稳健性检验。

    方法论要点：
      敏感性分析的核心问题是："如果使用不同的去重阈值，最终分析样本是否会
      显著改变？" 因此，输入数据应为经过完整流水线处理后的最终分析数据集
      (21_tone_llms.parquet)，而非预处理阶段的中间产出。这确保了敏感性检验
      直接对标审稿人关注的研究结论稳健性。

学术基准：
    Broder, A. Z. (1997). On the resemblance and containment of documents.
    Compression and Complexity of Sequences 1997. Proceedings (pp. 21-29). IEEE.
    https://doi.org/10.1109/SEQUEN.1997.666900
    → MinHash LSH 的 Jaccard 相似度理论支撑

流水线集成：
    由 run_pipeline_validation.py 调度，在阶段 32 (人工抽样) 之后执行。
    受 config.yaml 中 validation.dedup_sensitivity 开关控制 (默认开启)。

输入：
    21_tone_llms.parquet — 阶段 21 LLM 语义精筛后的最终分析数据集
    (经 00→11→12→21 完整流水线处理，含文本列 '内容' 供 MinHash 计算)

输出：
    eval_reports/dedup_sensitivity_report.csv — 多阈值去重敏感性统计表
    列: Threshold, Retained, Dropped, Retained_Ratio, Is_Production
"""

import os
import sys
import pandas as pd
import time
import importlib
import gc

# Phase 7b: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 news_process/validation/dedup_threshold.py 出发, 上溯 2 层抵达项目父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import setup_logging

# Phase 6a: 00_preprocessing.py 已是 Phase 2c thin shim, ArticleDeduplicator
# 的 canonical 路径是 news_process.pipeline.preprocess.dedup
try:
    from news_process.pipeline.preprocess.dedup import ArticleDeduplicator
except ImportError as e:
    raise ImportError(
        f"无法导入 ArticleDeduplicator: {e}. "
        f"canonical path: news_process.pipeline.preprocess.dedup"
    )

STAGE_NAME = "32a_dedup_sensitivity"


def main():
    config = load_config()
    logger = setup_logging(STAGE_NAME, config["paths"]["log_dir"])

    logger.info("=" * 60)
    logger.info("阶段 32a: 去重阈值参数敏感性实证测试")
    logger.info("=" * 60)
    logger.info("  学术依据: Broder, A. Z. (1997). On the resemblance and")
    logger.info("  containment of documents. IEEE SEQUENCES.")
    logger.info("  https://doi.org/10.1109/SEQUEN.1997.666900")

    # ── 加载生产阈值 (作为基准参考标注) ──
    prod_threshold = config.get('deduplication', {}).get(
        'jaccard_similarity_threshold', 0.80)
    logger.info(f"  生产去重阈值 (config.yaml): {prod_threshold}")

    # ── 加载输入数据: 阶段 21 的最终分析数据集 ──
    # 使用 21_tone_llms.parquet 而非 00_preprocessing.parquet，原因:
    #   1. 00_preprocessing.parquet 已在生产阈值 (0.80) 下完成去重，
    #      在其上重复运行去重会低估阈值变化的真实影响 (方法论偏误)
    #   2. 审稿人关心的是最终分析样本的稳健性，而非中间预处理数据
    #   3. 21 的输出保留了原始文本列 '内容'，可直接用于 MinHash 计算
    output_dir = config['paths']['output_dir']
    input_filename = config.get('filenames', {}).get(
        'output_21_tone_llms', '21_tone_llms.parquet')
    input_path = os.path.join(output_dir, input_filename)

    if not os.path.exists(input_path):
        logger.error(f"输入文件未找到: {input_path}")
        logger.error("  请确保阶段 21 (21_tone_llms.py) 已执行完成")
        return

    logger.info(f"正在加载分析数据集: {input_path}")
    df = pd.read_parquet(input_path)
    logger.info(f"成功加载数据, 行数: {len(df):,}")

    if df.empty:
        logger.error("数据为空，无法执行测试。")
        return

    # ── 校验文本列存在性 ──
    text_col = config.get('deduplication', {}).get('text_column',
               config.get('preprocessing', {}).get('text_column', '内容'))
    if text_col not in df.columns:
        logger.error(f"文本列 '{text_col}' 不存在于输入数据中，无法计算 MinHash")
        logger.error(f"  可用列: {list(df.columns[:20])}...")
        return

    thresholds = [0.75, 0.80, 0.85, 0.90]
    results = []

    # ── 前置预处理 + 精确去重 (仅执行一次) ──
    # 注意: 此处调用 ArticleDeduplicator 的内部方法 (_prepare_dataframe 等)，
    # 这些方法与 00_preprocessing.py 的生产逻辑完全相同。由于输入数据已经过
    # 阶段 00 的预处理，_prepare_dataframe 的操作是幂等的 (无副作用)，
    # _perform_exact_deduplication 不会再移除行 (精确重复已在阶段 00 清除)。
    # 若 ArticleDeduplicator API 变更，需同步更新。
    dedup = ArticleDeduplicator(config, logger)
    df_prep = dedup._prepare_dataframe(df)
    df_exact = dedup._perform_exact_deduplication(df_prep)
    exact_retained = len(df_exact)

    logger.info(f"精确去重完成, 剩余行数: {exact_retained:,} "
                f"(作为近似去重的基数)")

    for th in thresholds:
        logger.info(f"\n--- 测试阈值: Jaccard >= {th} "
                     f"{'← 生产阈值' if th == prod_threshold else ''} ---")
        start_t = time.time()

        # 覆写 dedup 实例的阈值 (单阶段内安全, 无并发竞争)
        dedup.threshold = th
        df_near = dedup._perform_near_deduplication(df_exact)

        retained = len(df_near)
        dropped = exact_retained - retained
        retained_ratio = retained / exact_retained if exact_retained > 0 else 0

        elapsed = time.time() - start_t
        logger.info(f"阈值 {th}: 拦截 {dropped:,} 篇, "
                    f"剩余 {retained:,} 篇 (占比 {retained_ratio:.2%}), "
                    f"耗时 {elapsed:.1f}秒")

        results.append({
            'Threshold': th,
            'Retained': retained,
            'Dropped': dropped,
            'Retained_Ratio': retained_ratio,
            'Is_Production': th == prod_threshold,
        })

        # [内存安全保护] 显式释放大对象视图以防止内存溢出 (OOM)
        del df_near
        gc.collect()

    logger.info("\n" + "=" * 40)
    logger.info("去重阈值敏感性报告 (供附录参考):")
    logger.info("=" * 40)

    res_df = pd.DataFrame(results)
    # 格式化输出百分比
    res_df_display = res_df.copy()
    res_df_display['Retained_Ratio'] = res_df_display[
        'Retained_Ratio'].apply(lambda x: f"{x:.2%}")
    logger.info("\n" + res_df_display.to_string(index=False))

    # ── 输出到 eval_reports/ (与其他验证模块输出目录一致) ──
    eval_dir = os.path.join(output_dir, 'eval_reports')
    os.makedirs(eval_dir, exist_ok=True)
    csv_path = os.path.join(eval_dir, "dedup_sensitivity_report.csv")
    res_df.to_csv(csv_path, index=False)
    logger.info(f"报告已保存至: {csv_path}")

    # ── 阶段汇总 ──
    logger.info("=" * 60)
    logger.info(f"阶段 32a 完成: 测试 {len(thresholds)} 个阈值, "
                f"生产阈值={prod_threshold}")
    logger.info(f"  输入数据: {input_filename} ({len(df):,} 行)")
    logger.info(f"  保留率范围: "
                f"{min(r['Retained_Ratio'] for r in results):.2%} ~ "
                f"{max(r['Retained_Ratio'] for r in results):.2%}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
