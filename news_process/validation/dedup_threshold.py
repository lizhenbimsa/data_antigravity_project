"""
news_process.validation.dedup_threshold — 去重阈值参数敏感性分析 (全量数据版)

迁移说明 (Phase 7b)：
    本模块由原 root script ``62_dedup_threshold_sensitivity.py`` body 迁入。
    规范调用方式: ``python -m news_process.validation.dedup_threshold``

=============================================================================

功能：
    使用 Jaccard MinHash 分别测试截断点阈值 [0.70, 0.75, 0.80, 0.85, 0.90]，
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
    阈值换成 0.70/0.75/0.80/0.85/0.90 各跑一遍, 看保留的文章数变化大不大;
    变化小就说明结论不依赖这个阈值。关键坑 ("机械截尾"): 如果输入语料
    本身已经按 0.80 去过重, 那再用 0.85/0.90 去测肯定"测不出"新重复 —
    这不是稳健, 是数据早被剪过了。所以本模块优先读去重之前的原始快照
    (_cache/), 实在拿不到才退回旧输入, 并在报告里逐行标明哪些数字是
    机械结果不可当证据。

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 62_dedup_threshold_sensitivity.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**⚠ 与任务描述的偏差订正**: 任务要点写的 'attention_*_jXXwY 20列演示' 实际属于另一个模块 `pipeline/panel/dedup_sensitivity.py` (runner 步骤 6b-3, 在面板上派生 20 个 `attention_*_jXXwY` 列)。本 shim (32a) 转发的是 `validation/dedup_threshold.py`, 它产出的是 `dedup_sensitivity_report.csv` (5 阈值×7 列), 与 jXXwY 列无关, 不要混淆。

**输入 (双口径, 关键)**: 优先 `data/processed/_cache/*.parquet` — 这是 stage 00 在去重**之前**写的 per-file 增量快照 (normalize+filter 后), 经 `_load_pre_dedup_corpus` 仅读 5 列 ['docid','标题','内容','日期','媒体(中文)']。缓存目录缺失/为空/任一文件缺列或读取失败时回退 `21_tone_llms.parquet` (CONFIG['filenames']['output_21_tone_llms']; 已按生产阈值去过重的下游产物)。

**处理步骤**:
1. 读生产阈值 `deduplication.jaccard_similarity_threshold` (默认 0.80) 作基准标注。
2. 实例化 `ArticleDeduplicator(config, logger)` (canonical path = `news_process.pipeline.preprocess.dedup`, 与生产 stage 00 同一类), 先 `_prepare_dataframe` + `_perform_exact_deduplication` 做一次精确去重 (作近似去重基数)。
3. 对 thresholds=[0.70, 0.75, 0.80, 0.85, 0.90] 逐个覆写 `dedup.threshold` 并 `_perform_near_deduplication`, 记录 Retained/Dropped/Retained_Ratio, 每轮 `del df_near; gc.collect()` 防 OOM。

**关键算法**: Jaccard MinHash LSH 近似去重 (Broder 1997 IEEE SEQUENCES, DOI:10.1109/SEQUEN.1997.666900)。`_annotate_censoring` 追加披露列: pre_dedup_cache 口径双向有效 (Mechanically_Censored 全 False); post_dedup_fallback 口径下 `Threshold >= 生产阈值` 的行 Dropped≈0 是'机械截尾'而非稳健性 (逐行标 Mechanically_Censored=True) — 这是 fix(omni-g-val-robust-01, 2026-06-11) 的核心: 旧实现读已去重数据扫更高阈值必然 Retained≈100%, 是数据被剪过的假象, 现改读去重前快照真实重去重。

**外部依赖**: 无 LLM; ArticleDeduplicator 内部用 MinHash (datasketch)、pyarrow.parquet (读 schema/列子集)。无显式 timeout。确定性: MinHash 用固定 permutation, 结果确定。

**上下游**: 纯诊断, 不写回主链, golden 不受影响。

■ 白话说明

**这一步在做什么**: 同一条新闻常被多家媒体转载, 流水线会把高度相似的稿子合并成一条 (去重)。'相似到什么程度算重复' 是个门槛 (现在用 0.80, 即 80% 相似)。这一步把门槛换成 0.70/0.75/0.80/0.85/0.90 各跑一遍, 看每个门槛下还剩多少篇文章。

**为什么需要它**: 防止有人质疑'你定 0.80 是为了凑数据'。如果门槛上下挪保留的文章数变化不大, 就说明去重不会人为操纵样本。这里有个大坑模块特意防住了: 如果拿'已经去过重的数据'去测更严的门槛, 肯定测不出新重复 — 不是因为门槛好, 而是数据早被剪过了。所以它优先去读'去重之前的原始快照'来真测, 实在拿不到才退而求其次并在报告里逐行老实标明'这个数字是机械结果, 别当证据'。

**对面板和论文的影响**: 去重直接决定每条新闻只数一次还是被重复计入。去重门槛若不稳, 银行某一年的'新闻热度/情感'就会被转载量人为放大或缩小, 进而扭曲银行-年度面板的核心变量。这一步给出的就是'去重门槛不影响结论'的书面证据。
========================================================================
"""

import gc
import glob
import os
import platform
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
from news_process.core.logging import pct4, setup_logging, sig4

# Phase 6a: 00_preprocessing.py 已是 Phase 2c thin shim, ArticleDeduplicator
# 的 canonical 路径是 news_process.pipeline.preprocess.dedup
try:
    from news_process.pipeline.preprocess.dedup import ArticleDeduplicator
except ImportError as e:
    raise ImportError(
        f"无法导入 ArticleDeduplicator: {e}. "
        f"canonical path: news_process.pipeline.preprocess.dedup"
    )

STAGE_NAME = "62_dedup_sensitivity"

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
    # IO provenance (日志富集, 2026-06-29): 列数物化口径 (此处固定为 5 列必需子集) +
    # 驻留内存, 便于审计"读了多少列 vs 去重实际所需列"。纯日志, 不改任何产物 (golden-safe)。
    try:
        _mem_gib = df.memory_usage(deep=True).sum() / (1024 ** 3)
        logger.info(f"     · 列数 = {df.shape[1]:,} (= 去重所需最小列集 "
                    f"{PRE_DEDUP_REQUIRED_COLS}, 仅按需读列控内存) | "
                    f"驻留内存 ≈ {sig4(_mem_gib)} GiB")
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  预去重语料列数/内存 provenance 打印失败 (不影响处理): {_e}")
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


def _log_environment_and_config(logger, config, output_dir: str,
                                prod_threshold, thresholds) -> None:
    """打印项目/环境信息 + 运行配置 + 方法论引文 (日志富集, 2026-06-24)。

    把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数、方法学出处"一次性
    落进日志, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 (golden-safe)。
    日志 emit 只在函数体内调用 (绝不在模块顶层), 避免 import 时截断生产日志。
    """
    try:
        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (阶段 62 去重阈值参数敏感性, "
                    "STAGES_VALIDATION; 纯诊断不写回主链)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) "
                    "v3.16.0")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "本阶段纯 CPU / 无 LLM·Embedding·网络·API ($0); "
                    "MinHash 固定 permutation → 结果逐位可复现")

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 优先输入: {os.path.join(output_dir, '_cache', '*.parquet')} "
                    "(stage 00 normalize+filter 后、去重前快照, 仅读 5 列)")
        _fallback_fn = config.get('filenames', {}).get(
            'output_21_tone_llms', '21_tone_llms.parquet')
        logger.info(f"     · 回退输入: {os.path.join(output_dir, _fallback_fn)} "
                    "(已按生产阈值去重的下游产物; 此口径单侧机械截尾)")
        logger.info(f"     · 输出:     {os.path.join(output_dir, 'eval_reports', 'dedup_sensitivity_report.csv')} "
                    "(5 阈值 × 7 列)")

        logger.info("  ⚙ 运行配置 (config/preprocessing.yaml::deduplication; "
                    "config/validation.yaml::validation.dedup_sensitivity 开关)")
        logger.info(f"     · 生产去重阈值 = {sig4(prod_threshold)} "
                    "(deduplication.jaccard_similarity_threshold)")
        logger.info("     · 扫描阈值网格 = ["
                    + ", ".join(sig4(t) for t in thresholds) + "]")
        _dedup_cfg = config.get('deduplication', {})
        _text_col = _dedup_cfg.get('text_column',
                                   config.get('preprocessing', {}).get('text_column', '内容'))
        logger.info(f"     · 文本列 = '{_text_col}' | 去重所需最小列集 = {PRE_DEDUP_REQUIRED_COLS}")
        logger.info("     · 签名与阈值无关 → 全阈值共用一次 MinHash 签名 "
                    "(逐阈值仅 find_near_duplicate_indices 判重)")

        logger.info("  📖 方法论依据 (参考文献, 经核验注册表逐字照抄)")
        logger.info("     · MinHash / Jaccard 相似度理论支撑: Broder, A. Z. (1997). "
                    "On the resemblance and containment of documents. In Proceedings. "
                    "Compression and Complexity of SEQUENCES 1997 "
                    "(Cat. No.97TB100171) (pp. 21-29). IEEE Computer Society. "
                    "https://doi.org/10.1109/SEQUEN.1997.666900")
        logger.info("       → 为什么用: MinHash 以固定 permutation 估计文档对 Jaccard "
                    "相似度, 把 O(N²) 全对比对压成近似近邻查询, 支撑大语料近似去重。")
        logger.info("     · LSH / 近似近邻 (ANN) 候选查询基元 (把 MinHash 签名分桶为候选对): "
                    "Indyk, P., & Motwani, R. (1998). Approximate nearest neighbors: "
                    "Towards removing the curse of dimensionality. In Proceedings of "
                    "the Thirtieth Annual ACM Symposium on Theory of Computing "
                    "(STOC '98) (pp. 604-613). ACM. "
                    "https://doi.org/10.1145/276698.276876")
        logger.info("       (白话: Broder 1997 只给出 MinHash 签名/Jaccard 估计这一原语, "
                    "真正把 O(N²) 全对比对压成近似近邻候选查询的是 LSH banding 分桶 — "
                    "datasketch 的 find_near_duplicate_indices 正依赖它把近似重复文档"
                    "落进同桶后才逐桶判重; Indyk-Motwani 1998 是该 LSH/ANN 框架的奠基工作, "
                    "补齐本模块 docstring 已断言却未引的 'O(N²)→近邻查询' 压缩原语。)")
        logger.info("     · 商业新闻语料近重复检测基准: Kumar, A., Tumre, S., & Patil, S. "
                    "(2025). Benchmarking near-duplicate detection in the era of "
                    "pay-walled news. In Companion Proceedings of the ACM on Web "
                    "Conference 2025 (WWW '25 Companion) (pp. 745-748). Association "
                    "for Computing Machinery. https://doi.org/10.1145/3701716.3715303")
        logger.info("       (白话: 在商业新闻语料上系统比较 SimHash / MinHash-LSH 近重复"
                    "检测, 与本模块'同一新闻多家转载需合并'的去重任务镜像同构, 佐证"
                    "MinHash-LSH 仍是新闻近重复的当代基线。)")
        logger.info("     · MinHash 族 2024 同行评议进展: Peng, Z., Zhang, Y., & Deng, D. "
                    "(2024). Near-duplicate text alignment with one permutation "
                    "hashing. Proceedings of the ACM on Management of Data, 2(4), "
                    "Article 222, 1-26. https://doi.org/10.1145/3677136")
        logger.info("       (白话: one-permutation hashing 把多 permutation MinHash 压成单次"
                    "置换, 是 MinHash 族近重复对齐的 2024 同行评议新进展, 印证本阶段所用"
                    "固定 permutation 签名路线的前沿延续性。)")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法论信息打印失败 (不影响处理): {e}")


def main():
    config = load_config()
    logger = setup_logging(STAGE_NAME, config["paths"]["log_dir"])

    # 运行期阶段计时 (各主要子阶段墙钟耗时, 末尾汇总; 纯日志)
    stage_start = time.time()
    phase_durations: dict[str, float] = {}

    logger.info("=" * 72)
    logger.info("阶段 62: 去重阈值参数敏感性 (Jaccard MinHash LSH, Broder 1997)")
    logger.info("=" * 72)
    logger.info("【功能】把 stage 00 的近似去重阈值换成 [0.70/0.75/0.80/0.85/0.90] 各跑一遍,")
    logger.info("        统计每个阈值下保留/拦截的文章数与保留率, 产出 dedup_sensitivity_report.csv,")
    logger.info("        作为'去重阈值不影响核心结论'的参数稳健性附录证据 (纯诊断, 不写回主链)。")
    logger.info("【方法】Jaccard MinHash LSH 近似去重 (Broder 1997 IEEE SEQUENCES, "
                "DOI:10.1109/SEQUEN.1997.666900);")
    logger.info("        签名仅依赖文本+(num_perm,ngram), 与阈值无关 → 全阈值共用一次签名,")
    logger.info("        逐阈值 find_near_duplicate_indices(th) 判重 (与 _perform_near_deduplication 逐位一致)。")
    logger.info("        生产阈值 = deduplication.jaccard_similarity_threshold (默认 0.80)。")
    logger.info("【判读】各阈值保留率随阈值升高单调上升=正常 (阈值越严, 越少文章被判重而被剔除);")
    logger.info("        相邻阈值保留率跨度越小 → 结论越不依赖 0.80 这一人为门槛 (稳健, 好)。")
    logger.info("【确定性】无 LLM/Embedding, 纯 CPU; MinHash 用固定 permutation → 结果逐位可复现。")

    # ── 加载生产阈值 (作为基准参考标注) ──
    prod_threshold = config.get('deduplication', {}).get(
        'jaccard_similarity_threshold', 0.80)
    logger.info(f"  生产去重阈值 (config/preprocessing.yaml::deduplication.jaccard_similarity_threshold): {sig4(prod_threshold)}")

    # 项目/环境信息 + 运行配置 + 方法论引文 (日志富集 2026-06-24)
    # 阈值网格与下方 thresholds 定义保持一致 (仅供日志披露, 不改控制流)
    _log_environment_and_config(
        logger, config, config['paths']['output_dir'],
        prod_threshold, [0.70, 0.75, 0.80, 0.85, 0.90])

    # ── 加载输入数据 ──
    # fix(omni-g-val-robust-01, 2026-06-11): 优先用 stage 00 的 per-file 增量缓存
    # (_cache/*.parquet = normalize+filter 后、**去重前** 的快照) 作为敏感性输入。
    # 旧实现读 21_tone_llms.parquet 并以 "00 输出已按生产阈值去重 → 低估阈值
    # 影响" 为由 — 但 21 严格继承 00 的去重, 同一偏误原样存在 (论证自我否定):
    # 相似度 >=0.80 的对已被删, 0.85/0.90 扫不出新重复, Retained≈100% 是机械
    # 结果, 稳健性单侧截尾。预去重口径下每个阈值真实执行去重, 双向均有信息。
    output_dir = config['paths']['output_dir']
    _t_load = time.time()
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
            # fix(D2, 2026-07-18): 缺输入=检验未执行, 静默 return 会让入口假绿; fail-loud 速败。
            sys.exit(1)

        logger.info(f"正在加载回退分析数据集: {input_path}")
        df = pd.read_parquet(input_path)
        logger.info(f"成功加载数据, 行数: {len(df):,}")
        # IO provenance (日志富集, 2026-06-29; 数字更新 2026-07-05): 回退口径 read_parquet 物化了全部 ~3395 列 (随重生漂移, 以实读为准),
        # 但本阶段下游仅消费单一文本列 (text_col) → 显式记录"物化列数 vs 实际所需 1 列"的
        # 冗余 IO 差距, 便于审计宽表读取代价。纯日志, 不改任何产物 (golden-safe)。
        try:
            _mem_gib = df.memory_usage(deep=True).sum() / (1024 ** 3)
            logger.info(f"     · 列数 = {df.shape[1]:,} (全量物化; 本阶段下游仅消费单一文本列, "
                        f"余列未用 → 冗余 IO 已知可接受) | 驻留内存 ≈ {sig4(_mem_gib)} GiB")
        except Exception as _e:  # noqa: BLE001
            logger.warning(f"  回退数据集列数/内存 provenance 打印失败 (不影响处理): {_e}")

        # fix(omni-g-val-robust-01, 2026-06-11): 诚实披露单侧截尾 —
        # 回退输入已按生产阈值去重, >= 生产阈值方向的 Dropped≈0 为机械结果
        logger.warning("⚠ 输入口径: post_dedup_fallback — 数据已按生产阈值 "
                       f"({sig4(prod_threshold)}) 去重。阈值 >= {sig4(prod_threshold)} 方向的 "
                       "'高保留率' 是机械截尾而非稳健性证据, 仅 < "
                       f"{sig4(prod_threshold)} 方向有信息量; 报告列 "
                       "Mechanically_Censored 已逐行标记。")

    if df.empty:
        logger.error("数据为空，无法执行测试。")
        # fix(D2, 2026-07-18): 空输入=检验未执行; fail-loud 速败 (同文件同函数口径统一)。
        sys.exit(1)

    # ── 校验文本列存在性 ──
    text_col = config.get('deduplication', {}).get('text_column',
               config.get('preprocessing', {}).get('text_column', '内容'))
    if text_col not in df.columns:
        logger.error(f"文本列 '{text_col}' 不存在于输入数据中，无法计算 MinHash")
        logger.error(f"  可用列: {list(df.columns[:20])}...")
        # fix(D2, 2026-07-18): 缺必要列=检验未执行; fail-loud 速败。
        sys.exit(1)

    thresholds = [0.70, 0.75, 0.80, 0.85, 0.90]
    results = []

    # ── 前置预处理 + 精确去重 (仅执行一次) ──
    # 注意: 此处调用 ArticleDeduplicator 的内部方法 (_prepare_dataframe 等)，
    # 这些方法与 00_preprocessing.py 的生产逻辑完全相同。
    # fix(omni-g-val-robust-01, 2026-06-11): 预去重口径 (pre_dedup_cache) 下
    # 精确去重会真实移除行 (与生产 stage 00 行为一致); 仅回退口径
    # (post_dedup_fallback) 下精确重复已被上游清除、此步为幂等空转。
    # 若 ArticleDeduplicator API 变更，需同步更新。
    # 输入语料行数 (供末尾汇总; df 下面会被释放以省内存)
    n_input_rows = len(df)
    phase_durations['①加载输入语料'] = time.time() - _t_load

    _t_exact = time.time()
    dedup = ArticleDeduplicator(config, logger)
    df_prep = dedup._prepare_dataframe(df)
    df_exact = dedup._perform_exact_deduplication(df_prep)
    exact_retained = len(df_exact)
    phase_durations['②预处理+精确去重'] = time.time() - _t_exact

    logger.info(f"精确去重完成, 剩余行数: {exact_retained:,} "
                f"(作为近似去重的基数)")

    # fix(perf-mem, 2026-06-17): 精确去重后立即释放近似去重【不需要】的重列 —
    # 原始 标题/内容 (与已合并的 temp_title_content 重复持有, 全量 ~385 万行正文是
    # 本阶段内存最大头) + 日期/媒体(中文)/temp_content_length。下游仅需 4 列:
    #   temp_title_content (compute_minhashes + N4 真 Jaccard 复核),
    #   temp_datetime / temp_media_weight / docid (find_near_duplicate_indices 簇内排序判重)。
    # 纯丢列 + 释放预去重全量帧, 不改任何去重结果; 文本内存由 3 份 (标题+内容+合并)
    # 收缩到 1 份 (合并), 峰值约降 2/3。
    _keep_cols = [dedup.COL_COMBINED, dedup.COL_DATETIME, dedup.COL_WEIGHT, 'docid']
    df_exact = df_exact[[c for c in _keep_cols if c in df_exact.columns]].copy()
    del df, df_prep  # df_prep 即 _prepare_dataframe 原地改写后返回的 df, 同一对象
    gc.collect()

    # fix(perf, 2026-06-17): MinHash 签名只依赖文本 + (num_perm, ngram_size), **与 Jaccard
    # 阈值无关** (见 compute_minhashes docstring) — 故全部阈值共用同一批签名, 仅计算一次。
    # 旧实现逐阈值调 _perform_near_deduplication, 每次都从头重算签名 (在去重前全量语料
    # 上是分钟级多进程重负载), N 个阈值 = N× 冗余 MinHash, 是 stage 32a 在全量语料上
    # 超时 (7200s) 的主因之一。判重逐阈值调 find_near_duplicate_indices(threshold=th),
    # 结果与逐阈值 _perform_near_deduplication 逐位一致 (compute_minhashes + find(默认参数)
    # == _perform_near_deduplication, 由 test_dedup_sensitivity.py::
    # test_default_params_equal_production_method 锚定)。
    logger.info("计算 MinHash 签名 (一次, 全部阈值共用; 签名与阈值无关)...")
    mh_start = time.time()
    # F8 (2026-06-26): 刻意不传 cache_dir — W9 内容寻址 sidecar 仅接在生产路径 dedup_sensitivity
    # (runner step 6b-3, 每次 stage40 跑); 本 validation 阶段按需手动跑, 跨-run 重算可接受。
    # (W9 键内容寻址, 即便接同一 cache_dir 也因语料指纹不同而不碰撞, 此处仅为不增维护面。)
    minhashes = dedup.compute_minhashes(df_exact)
    mh_elapsed = time.time() - mh_start
    phase_durations['③MinHash签名(一次)'] = mh_elapsed
    logger.info(f"MinHash 签名完成, 耗时 {sig4(mh_elapsed)}秒 "
                f"(此前每阈值重算, 现 {len(thresholds)} 阈值共用此一次)")

    _t_scan = time.time()
    for th in thresholds:
        logger.info(f"\n--- 测试阈值: Jaccard >= {sig4(th)} "
                     f"{'← 生产阈值' if th == prod_threshold else ''} ---")
        start_t = time.time()

        # 共用 minhashes, 仅按 th 判重 (window 取生产默认 5 工作日, 同
        # _perform_near_deduplication); dropped = 应剔除索引数。
        drop_idx = dedup.find_near_duplicate_indices(
            df_exact, minhashes, threshold=th)
        dropped = len(drop_idx)
        retained = exact_retained - dropped
        retained_ratio = retained / exact_retained if exact_retained > 0 else 0

        elapsed = time.time() - start_t
        logger.info(f"阈值 {sig4(th)}: 拦截 {dropped:,} 篇, "
                    f"剩余 {retained:,} 篇 (占比 {pct4(retained_ratio)}), "
                    f"耗时 {sig4(elapsed)}秒")

        results.append({
            'Threshold': th,
            'Retained': retained,
            'Dropped': dropped,
            'Retained_Ratio': retained_ratio,
            'Is_Production': th == prod_threshold,
        })

        # [内存安全保护] 释放本轮临时对象 (minhashes 跨阈值复用, 不释放)
        del drop_idx
        gc.collect()

    phase_durations['④逐阈值判重扫描'] = time.time() - _t_scan

    logger.info("\n" + "=" * 40)
    logger.info("去重阈值敏感性报告 (供附录参考):")
    logger.info("=" * 40)

    res_df = pd.DataFrame(results)
    # fix(omni-g-val-robust-01, 2026-06-11): 追加输入口径 + 机械截尾披露列
    res_df = _annotate_censoring(res_df, input_mode, prod_threshold)
    # 格式化输出百分比 (仅 res_df_display 用于日志展示, 不写盘; res_df 原值落 CSV)
    res_df_display = res_df.copy()
    res_df_display['Retained_Ratio'] = res_df_display[
        'Retained_Ratio'].apply(lambda x: pct4(x))
    logger.info("\n" + res_df_display.to_string(index=False))

    # ── 输出到 eval_reports/ (与其他验证模块输出目录一致) ──
    eval_dir = os.path.join(output_dir, 'eval_reports')
    os.makedirs(eval_dir, exist_ok=True)
    csv_path = os.path.join(eval_dir, "dedup_sensitivity_report.csv")
    res_df.to_csv(csv_path, index=False)
    logger.info(f"报告已保存至: {csv_path}")

    # ── 【结果分析】对照阈值/预期方向逐指标判读 (纯日志, 不回写产物) ──
    # crash-guard (2026-06-17): 本判读块只读已落盘的 res_df/results 算诊断指标,
    # 整体包进 try/except — 任何指标计算异常 (缺列/空序列/除零等) 仅吞掉并 WARNING,
    # 绝不冒泡使阶段崩溃 (产物 dedup_sensitivity_report.csv 已在上方写盘, 此块纯日志)。
    logger.info("-" * 72)
    logger.info("【结果分析】去重阈值敏感性产出指标判读 (阈值稳健 ⇒ 结论不依赖 0.80 门槛)")
    try:
        # 指标①: 输入口径有效性 — 双向有效 / 单侧机械截尾
        # column-guard: Mechanically_Censored 由 _annotate_censoring 保证存在, 防御性再核
        if 'Mechanically_Censored' in res_df.columns:
            n_censored = int(res_df['Mechanically_Censored'].sum())
        else:
            n_censored = 0
        if input_mode == 'pre_dedup_cache':
            logger.info(f"  · 输入口径 = pre_dedup_cache (去重前快照, {n_input_rows:,} 行) → "
                        "双向阈值敏感性均有效, 全部阈值是真稳健性证据 (好)。")
        else:
            logger.warning(f"  · 输入口径 = post_dedup_fallback (已按生产阈值 {sig4(prod_threshold)} 去重的 "
                           f"{input_desc}, {n_input_rows:,} 行)。")
            logger.warning(f"    Threshold >= {sig4(prod_threshold)} 的 {n_censored} 行 Dropped≈0 是机械截尾, "
                           f"仅 < {sig4(prod_threshold)} 一侧有信息量 (报告列 Mechanically_Censored 已逐行标记)。")

        # 指标②: 精确去重基数 (近似去重的分母)
        # NaN/除零-guard: df.empty 已在上方提前返回 → n_input_rows>0; 仍显式守 >0 防御
        exact_drop = n_input_rows - exact_retained
        if n_input_rows > 0:
            logger.info(f"  · 精确去重基数 = {exact_retained:,} 篇 "
                        f"(精确剔除 {exact_drop:,} 篇 = {pct4(exact_drop / n_input_rows)}, 全字符重复)。")
        else:
            logger.info(f"  · 精确去重基数 = {exact_retained:,} 篇 (输入行数为 0, 跳过占比计算)。")

        # 指标③: 生产阈值 (0.80) 下的保留率 — 实际投产口径的结果
        prod_row = next((r for r in results if r['Is_Production']), None)
        if prod_row is not None:
            logger.info(f"  · 生产阈值 {sig4(prod_threshold)} 保留率 = {pct4(prod_row['Retained_Ratio'])} "
                        f"(保留 {prod_row['Retained']:,} / 拦截 {prod_row['Dropped']:,} 篇) "
                        "← 这是实际投产口径。")

        # 指标④/⑤/⑥: 保留率序列诊断 (Retained_Ratio 恒为数值, 见 retained_ratio 计算的 else 0 兜底)
        ratios = [r['Retained_Ratio'] for r in results]
        if not ratios:
            # 序列空 (thresholds 非空时不可达) → 跳过序列类指标, 不落进 max()/min() 空序列崩溃
            logger.info("  · 无阈值结果 (results 为空), 跳过单调性/跨度/边际诊断。")
        else:
            # 指标④: 保留率随阈值单调性 — 预期方向 = 随阈值升高单调不减
            monotone = all(b >= a - 1e-9 for a, b in zip(ratios, ratios[1:]))
            if monotone:
                logger.info("  · 保留率随阈值单调不减: 是 (符合预期 — 阈值越严, 越少文章被判重剔除, 好)。")
            else:
                logger.warning("  · 保留率随阈值单调不减: 否 (反常! 阈值变严反而剔除更多, 需复查 MinHash 判重逻辑)。")

            # 指标⑤: 保留率跨度 — 越小越稳健 (经验门槛: 全程 <5pp 视为高度稳健)
            ratio_span = max(ratios) - min(ratios)
            span_verdict = ("高度稳健" if ratio_span < 0.05
                            else "中等敏感" if ratio_span < 0.15 else "高敏感(需警惕)")
            logger.info(f"  · 保留率跨度 (max-min) = {pct4(ratio_span)} → {span_verdict}; "
                        f"区间 {pct4(min(ratios))} ~ {pct4(max(ratios))} "
                        f"(跨度越小 ⇒ 结论越不依赖 {sig4(prod_threshold)} 门槛)。")

            # 指标⑥: 相邻阈值边际变化 — 0.80 附近最敏感档位
            deltas = [(thresholds[i + 1], ratios[i + 1] - ratios[i])
                      for i in range(len(ratios) - 1)]
            if deltas:
                max_th, max_delta = max(deltas, key=lambda kv: abs(kv[1]))
                logger.info(f"  · 最大相邻边际变化 = {pct4(abs(max_delta))} (出现在 → {sig4(max_th)} 档); "
                            "边际越平滑说明阈值附近无悬崖式样本翻转。")

        # 小样本警告 (盘面 T=2 / 极少行只验证管道正确性)
        # 口径消歧 (2026-06-17): 本 stage 真实输入 = _load_pre_dedup_corpus 读 stage 00
        # _cache (normalize+filter 后、去重前快照) ≈ 405万行 (32a 日志实测 4,046,188 "去重前口径";
        # 其中精确去重后 ≈ 385万行 (实测 3,853,947) = 近似 MinHash 去重的基数, 见 line 289 perf 注释);
        # 约1,819万 是 normalize+filter **之前** 的项目级原始 raw 报道数, 本 stage 永远不会扫到 →
        # 全量分母只挂一次 "T=19", 给 405万 加 "去重前" 限定、约1,819万 加 "项目级原始" 限定, 防误判量级。
        if n_input_rows < 50_000:
            logger.warning(f"  ⚠ 输入仅 {n_input_rows:,} 行 (远小于本 stage 去重前全量语料 ~405万行, "
                           "其中精确去重后 ~385万行为 MinHash 基数): 本次仅验证管道正确性与阈值单调性, "
                           "稳健性结论须以全量去重前语料 (~405万行 = 项目级原始 约1,819万 经 normalize+filter 后, "
                           "2007-2025 T=19) 实测为准。")
    except Exception as _e:
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")
    logger.info("-" * 72)

    # ── 阶段汇总 ──
    logger.info("=" * 60)
    logger.info(f"阶段 62 完成: 测试 {len(thresholds)} 个阈值, "
                f"生产阈值={sig4(prod_threshold)}")
    logger.info(f"  输入数据: {input_desc} ({n_input_rows:,} 行, 口径={input_mode})")
    logger.info(f"  保留率范围: "
                f"{pct4(min(r['Retained_Ratio'] for r in results))} ~ "
                f"{pct4(max(r['Retained_Ratio'] for r in results))}")
    logger.info("=" * 60)

    # ── ⏱ 阶段计时汇总 (各主要子阶段墙钟耗时; 纯日志, golden-safe) ──
    try:
        total_elapsed = time.time() - stage_start
        logger.info("  ⏱ 阶段计时汇总 (秒)")
        for _phase, _dur in phase_durations.items():
            _share = (_dur / total_elapsed) if total_elapsed > 0 else 0.0
            logger.info(f"     · {_phase}: {sig4(_dur)}秒 ({pct4(_share)})")
        logger.info(f"     · 阶段总墙钟: {sig4(total_elapsed)}秒")
    except Exception as _te:  # noqa: BLE001
        logger.warning(f"  阶段计时汇总打印失败 (不影响产物): {_te}")


if __name__ == "__main__":
    main()
