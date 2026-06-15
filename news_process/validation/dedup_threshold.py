"""
news_process.validation.dedup_threshold — 去重阈值参数敏感性分析 (全量数据版)

迁移说明 (Phase 7b)：
    本模块由原 root script ``32a_dedup_threshold_sensitivity.py`` body 迁入。
    规范调用方式: ``python -m news_process.validation.dedup_threshold``

=============================================================================

功能：
    使用 Jaccard MinHash 分别测试截断点阈值 [0.75, 0.80, 0.85, 0.90]，
    输出去重敏感性统计表，供实证检验附件使用。

    本阶段用于证明生产去重阈值 (config/preprocessing.yaml:
    deduplication.jaccard_similarity_threshold)
    的选择不影响核心结论，属于学术论文附录中的参数稳健性检验。

    方法论要点 (fix(omni-g-val-robust-01, 2026-06-11) 修订)：
      敏感性输入必须是 **去重前** 的语料。旧实现读 21_tone_llms.parquet —
      它严格继承 stage 00 在生产阈值 (0.80) 下的近似去重结果, 所有相似度
      >=0.80 的对已被移除; 在其上扫描 0.85/0.90 (要求更高相似度才算重复)
      找到的新重复对 ⊂ 已删集合 → Dropped≈0 / Retained≈100% 是机械结果,
      稳健性单侧截尾 (仅 <0.80 一侧有信息), 且旧 docstring 以同一偏误为由
      弃用 00 输出、改用 00 的下游, 论证自我否定。
      修复: 优先从 stage 00 的 per-file 增量缓存 (data/processed/_cache/
      *.parquet — normalize+filter 后、去重前的快照) 重建预去重语料, 对每个
      阈值真实执行 精确去重 + 近似去重, 双向均有信息量; 缓存不可得时回退旧
      输入并在日志与报告列 (Input_Mode / Mechanically_Censored) 中显式披露
      ">= 生产阈值方向机械截尾"。

学术基准：
    Broder, A. Z. (1997). On the resemblance and containment of documents.
    Compression and Complexity of Sequences 1997. Proceedings (pp. 21-29). IEEE.
    https://doi.org/10.1109/SEQUEN.1997.666900
    → MinHash LSH 的 Jaccard 相似度理论支撑

流水线集成：
    由 run_pipeline_validation.py 调度，在阶段 32 (人工抽样) 之后执行。
    受 config/validation.yaml 中 validation.dedup_sensitivity 开关控制 (默认开启)。

输入：
    优先: data/processed/_cache/*.parquet — stage 00 增量缓存
    (normalize+filter 后、**去重前** 的 per-file 快照, 仅读去重所需 5 列)
    回退: 21_tone_llms.parquet (经生产阈值去重的下游产物;
    此口径下 >=生产阈值方向机械截尾, 报告中显式披露)

输出：
    eval_reports/dedup_sensitivity_report.csv — 多阈值去重敏感性统计表
    列: Threshold, Retained, Dropped, Retained_Ratio, Is_Production,
        Input_Mode, Mechanically_Censored

白话:
    去重时"相似到多少算重复"是个人为定的阈值 (生产用 0.80)。本检验把
    阈值换成 0.75/0.80/0.85/0.90 各跑一遍, 看保留的文章数变化大不大;
    变化小就说明结论不依赖这个阈值。关键坑 ("机械截尾"): 如果输入语料
    本身已经按 0.80 去过重, 那再用 0.85/0.90 去测肯定"测不出"新重复 —
    这不是稳健, 是数据早被剪过了。所以本模块优先读去重之前的原始快照
    (_cache/), 实在拿不到才退回旧输入, 并在报告里逐行标明哪些数字是
    机械结果不可当证据。

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 32a_dedup_threshold_sensitivity.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**⚠ 与任务描述的偏差订正**: 任务要点写的 'attention_*_jXXwY 20列演示' 实际属于另一个模块 `pipeline/panel/dedup_sensitivity.py` (runner 步骤 6b-3, 在面板上派生 20 个 `attention_*_jXXwY` 列)。本 shim (32a) 转发的是 `validation/dedup_threshold.py`, 它产出的是 `dedup_sensitivity_report.csv` (4 阈值×7 列), 与 jXXwY 列无关, 不要混淆。

**输入 (双口径, 关键)**: 优先 `data/processed/_cache/*.parquet` — 这是 stage 00 在去重**之前**写的 per-file 增量快照 (normalize+filter 后), 经 `_load_pre_dedup_corpus` 仅读 5 列 ['docid','标题','内容','日期','媒体(中文)']。缓存目录缺失/为空/任一文件缺列或读取失败时回退 `21_tone_llms.parquet` (CONFIG['filenames']['output_21_tone_llms']; 已按生产阈值去过重的下游产物)。

**处理步骤**:
1. 读生产阈值 `deduplication.jaccard_similarity_threshold` (默认 0.80) 作基准标注。
2. 实例化 `ArticleDeduplicator(config, logger)` (canonical path = `news_process.pipeline.preprocess.dedup`, 与生产 stage 00 同一类), 先 `_prepare_dataframe` + `_perform_exact_deduplication` 做一次精确去重 (作近似去重基数)。
3. 对 thresholds=[0.75, 0.80, 0.85, 0.90] 逐个覆写 `dedup.threshold` 并 `_perform_near_deduplication`, 记录 Retained/Dropped/Retained_Ratio, 每轮 `del df_near; gc.collect()` 防 OOM。

**关键算法**: Jaccard MinHash LSH 近似去重 (Broder 1997 IEEE SEQUENCES, DOI:10.1109/SEQUEN.1997.666900)。`_annotate_censoring` 追加披露列: pre_dedup_cache 口径双向有效 (Mechanically_Censored 全 False); post_dedup_fallback 口径下 `Threshold >= 生产阈值` 的行 Dropped≈0 是'机械截尾'而非稳健性 (逐行标 Mechanically_Censored=True) — 这是 fix(omni-g-val-robust-01, 2026-06-11) 的核心: 旧实现读已去重数据扫更高阈值必然 Retained≈100%, 是数据被剪过的假象, 现改读去重前快照真实重去重。

**外部依赖**: 无 LLM; ArticleDeduplicator 内部用 MinHash (datasketch)、pyarrow.parquet (读 schema/列子集)。无显式 timeout。确定性: MinHash 用固定 permutation, 结果确定。

**上下游**: 纯诊断, 不写回主链, golden 不受影响。

■ 白话说明

**这一步在做什么**: 同一条新闻常被多家媒体转载, 流水线会把高度相似的稿子合并成一条 (去重)。'相似到什么程度算重复' 是个门槛 (现在用 0.80, 即 80% 相似)。这一步把门槛换成 0.75/0.80/0.85/0.90 各跑一遍, 看每个门槛下还剩多少篇文章。

**为什么需要它**: 防止有人质疑'你定 0.80 是为了凑数据'。如果门槛上下挪保留的文章数变化不大, 就说明去重不会人为操纵样本。这里有个大坑模块特意防住了: 如果拿'已经去过重的数据'去测更严的门槛, 肯定测不出新重复 — 不是因为门槛好, 而是数据早被剪过了。所以它优先去读'去重之前的原始快照'来真测, 实在拿不到才退而求其次并在报告里逐行老实标明'这个数字是机械结果, 别当证据'。

**对面板和论文的影响**: 去重直接决定每条新闻只数一次还是被重复计入。去重门槛若不稳, 银行某一年的'新闻热度/情感'就会被转载量人为放大或缩小, 进而扭曲银行-年度面板的核心变量。这一步给出的就是'去重门槛不影响结论'的书面证据。
========================================================================
"""

import gc
import glob
import os
import sys
import time

import pandas as pd
import pyarrow.parquet as pq

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

# ArticleDeduplicator 全流程 (媒体权重排序 / 标题+内容合并 / 日期窗口) 所需最小列集
PRE_DEDUP_REQUIRED_COLS = ['docid', '标题', '内容', '日期', '媒体(中文)']


def _load_pre_dedup_corpus(output_dir: str, logger) -> "pd.DataFrame | None":
    """加载 stage 00 去重前的 normalize 后语料 (per-file 增量缓存)。

    fix(omni-g-val-robust-01, 2026-06-11): stage 00 (pipeline.preprocess.runner)
    在去重 **之前** 把每个 xlsx 的 normalize+filter 结果写入
    ``<output_dir>/_cache/<file>.parquet`` 增量缓存 — 这是管道中唯一持久化的
    预去重快照, 正是阈值敏感性的正确输入。仅读取去重所需 5 列以控内存。

    Returns:
        pd.DataFrame | None: 拼接后的预去重语料; 缓存目录缺失/为空/任一文件
        缺列或读取失败时返回 None (调用方回退旧输入并披露单侧截尾)。
    """
    cache_dir = os.path.join(output_dir, '_cache')
    if not os.path.isdir(cache_dir):
        logger.warning(f"预去重缓存目录不存在: {cache_dir}")
        return None

    cache_files = sorted(glob.glob(os.path.join(cache_dir, '*.parquet')))
    if not cache_files:
        logger.warning(f"预去重缓存目录为空: {cache_dir}")
        return None

    frames = []
    for fp in cache_files:
        try:
            schema_names = set(pq.read_schema(fp).names)
        except Exception as e:
            logger.warning(f"预去重缓存 schema 读取失败 ({os.path.basename(fp)}): {e}")
            return None
        missing = [c for c in PRE_DEDUP_REQUIRED_COLS if c not in schema_names]
        if missing:
            logger.warning(f"预去重缓存缺少必需列 {missing} "
                           f"({os.path.basename(fp)}), 放弃缓存口径")
            return None
        try:
            frames.append(pd.read_parquet(fp, columns=PRE_DEDUP_REQUIRED_COLS))
        except Exception as e:
            logger.warning(f"预去重缓存读取失败 ({os.path.basename(fp)}): {e}")
            return None

    df = pd.concat(frames, ignore_index=True)
    logger.info(f"预去重语料加载完成: {len(cache_files)} 个缓存文件, "
                f"{len(df):,} 行 (去重前口径)")
    return df


def _annotate_censoring(res_df: pd.DataFrame, input_mode: str,
                        prod_threshold: float) -> pd.DataFrame:
    """为敏感性报告追加输入口径与机械截尾披露列。

    fix(omni-g-val-robust-01, 2026-06-11): 回退口径 (post_dedup_fallback) 下,
    输入已按生产阈值去重 — 所有 Threshold >= 生产阈值的行 Dropped≈0 是机械
    结果而非稳健性证据, 标记 Mechanically_Censored=True 使报告自描述;
    预去重口径 (pre_dedup_cache) 下双向均有信息, 全部 False。
    """
    out = res_df.copy()
    out['Input_Mode'] = input_mode
    if input_mode == 'pre_dedup_cache':
        out['Mechanically_Censored'] = False
    else:
        out['Mechanically_Censored'] = out['Threshold'] >= prod_threshold
    return out


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

    # ── 加载输入数据 ──
    # fix(omni-g-val-robust-01, 2026-06-11): 优先用 stage 00 的 per-file 增量缓存
    # (_cache/*.parquet = normalize+filter 后、**去重前** 的快照) 作为敏感性输入。
    # 旧实现读 21_tone_llms.parquet 并以 "00 输出已按生产阈值去重 → 低估阈值
    # 影响" 为由 — 但 21 严格继承 00 的去重, 同一偏误原样存在 (论证自我否定):
    # 相似度 >=0.80 的对已被删, 0.85/0.90 扫不出新重复, Retained≈100% 是机械
    # 结果, 稳健性单侧截尾。预去重口径下每个阈值真实执行去重, 双向均有信息。
    output_dir = config['paths']['output_dir']
    df = _load_pre_dedup_corpus(output_dir, logger)

    if df is not None and not df.empty:
        input_mode = 'pre_dedup_cache'
        input_desc = '_cache/*.parquet (stage 00 去重前快照)'
        logger.info("输入口径: 预去重语料 (pre_dedup_cache) — 双向阈值敏感性均有效")
    else:
        # ── 回退: 阶段 21 输出 (已按生产阈值去重的下游产物) + 单侧截尾披露 ──
        input_mode = 'post_dedup_fallback'
        input_filename = config.get('filenames', {}).get(
            'output_21_tone_llms', '21_tone_llms.parquet')
        input_desc = input_filename
        input_path = os.path.join(output_dir, input_filename)

        if not os.path.exists(input_path):
            logger.error(f"输入文件未找到: {input_path}")
            logger.error("  请确保阶段 00 缓存 (_cache/) 或阶段 21 输出至少一项可用")
            return

        logger.info(f"正在加载回退分析数据集: {input_path}")
        df = pd.read_parquet(input_path)
        logger.info(f"成功加载数据, 行数: {len(df):,}")

        # fix(omni-g-val-robust-01, 2026-06-11): 诚实披露单侧截尾 —
        # 回退输入已按生产阈值去重, >= 生产阈值方向的 Dropped≈0 为机械结果
        logger.warning("⚠ 输入口径: post_dedup_fallback — 数据已按生产阈值 "
                       f"({prod_threshold}) 去重。阈值 >= {prod_threshold} 方向的 "
                       "'高保留率' 是机械截尾而非稳健性证据, 仅 < "
                       f"{prod_threshold} 方向有信息量; 报告列 "
                       "Mechanically_Censored 已逐行标记。")

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
    # 这些方法与 00_preprocessing.py 的生产逻辑完全相同。
    # fix(omni-g-val-robust-01, 2026-06-11): 预去重口径 (pre_dedup_cache) 下
    # 精确去重会真实移除行 (与生产 stage 00 行为一致); 仅回退口径
    # (post_dedup_fallback) 下精确重复已被上游清除、此步为幂等空转。
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
    # fix(omni-g-val-robust-01, 2026-06-11): 追加输入口径 + 机械截尾披露列
    res_df = _annotate_censoring(res_df, input_mode, prod_threshold)
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
    logger.info(f"  输入数据: {input_desc} ({len(df):,} 行, 口径={input_mode})")
    logger.info(f"  保留率范围: "
                f"{min(r['Retained_Ratio'] for r in results):.2%} ~ "
                f"{max(r['Retained_Ratio'] for r in results):.2%}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
