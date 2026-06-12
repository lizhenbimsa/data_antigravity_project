"""
news_process.pipeline.sentiment.herd_decay — 跟风/抄袭新闻检测与衰减加权 (双轨版 v3.6.0)
=========================================================================

迁移说明 (Phase 7a-7)：
    本模块由原 root script ``24_herd_decay_processor.py`` body 迁入。
    规范调用方式: ``python -m news_process.pipeline.sentiment.herd_decay``

v3.6.0 (Plan E P1 B3) 双轨化升级:
    原实现仅对 '内容' 全文做 TF-IDF 相似度判定, 算出单列 herd_weight,
    被下游同时施加到 _full / _ctx 两轨。这是 measurement-treatment
    错配 (Edwards 2001 ORM): 全文相似度 ≠ 对目标银行的报道相似度。
    本版本改为对 '内容' 和 'content_ctx' 分别做 TF-IDF, 输出双轨权重
    herd_weight_full + herd_weight_ctx, 下游按 track 各自施加。

功能:
  对同一 target_bank 在同一时间窗口内的多篇新闻进行文本相似度聚类,
  识别"跟风抄袭"新闻并施加衰减权重, 防止重复计数导致情感指标注水。
  v3.6.0 起按 full / ctx 双轨独立判定。

学术依据:
  - Tetlock (2011, RFS 24(5):1481-1512): 媒体新闻的信息冗余与重复效应
  - Sautner et al. (2023, JF): 文本相似度驱动的曝光度度量
  - Edwards (2001, ORM): measurement-treatment matching (双轨化动因)

关键设计:
  - TF-IDF 向量化 + 维度封锁 (max_features=10000)
    ⚠ 披露 (fix(omni-g-herd-02, 2026-06-11)): max_features 按**原始词频**截断 top-k —
    全量语料 (2007-2024) 头部银行单组数十万篇时 char 2-4 gram 词表达百万级, top-10k
    截断把相似度计算压入高频 boilerplate ngram 子空间 (判别性长尾缺席 → 余弦系统性
    膨胀, 规模依赖)。截断咬合时运行期记 logger.warning; 共享全语料词表 / 按 IDF 选
    top-k 的重设计与全量 run 一并处理, 届时应做 max_features 敏感性检验。
  - df 阈值比例化 (fix(omni-g-herd-01, 2026-06-11)): min_df = min(MIN_DF,
    max(2, ceil(0.01·n))), 消除小组词表塌缩断崖; max_df 守卫 df-band 退化 (详见
    _build_tfidf_vectorizer docstring)。
    ⚠ 披露: 词表/IDF 仍按 (bank, 年度前缀) 组内拟合, 相似度刻度跨组不完全同质 →
    0.35 阈值的跨银行严格可比性不成立 (比例化仅消除 df-band 退化这一最大失真源)。
  - as-of yearly vocab fit (fix(omni-g-herd-05, 2026-06-11)): 年 t 文章的前驱计数仅用
    year ≤ t 文档拟合的向量空间 (前驱构念严格后视, 向量空间不得含未来 DF/IDF);
    年内残余前视为接受粒度 (面板为 bank-year)。
  - ≤2000 篇/前缀 走 dense pairwise; >2000 篇走 7 天窗双指针分桶 O(N·window) (W1 2026-06-05)
  - 相似度阈值 0.35: 相似度 ≥ 此值视为"跟风" (闭边界, 代码用 >=)
  - 衰减公式: weight = 1 / (1 + n_similar_predecessors)
  - **双轨**: full 用 'content_full'(标题+全文), ctx 用 'content_ctx'(标题+实体窗口);
    两者均由 stage 13 物化、含标题对称 (病根A 已修); 缺 content_full 时 full 回退裸 '内容'

输入: 23_bert_tone.parquet (含 content_ctx 列, 由 stage 13 ctx_materializer 物化后下传)
输出: 24_herd_decay.parquet (追加 6 列: 4 双轨列 herd_weight_full + herd_weight_ctx
      + n_similar_articles_full + n_similar_articles_ctx, 外加 herd_weight +
      n_similar_articles 两个单列 —— 后者作为 _full 轨的 NON-BREAKING 别名保留
      (v3.6.0 F-B 修, 见下方主路径), 供 v3.5.x 既有调用方继续读取, 不强制下游显式指定轨道)
"""

import os
import sys

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import pairwise_distances

# Phase 7a-7: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 pipeline/sentiment/herd_decay.py 出发, 上溯 3 层抵达 news_process/ 的父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import setup_logging

# ============================================================================
# 1. 全局配置
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "24_herd_decay_processor"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

OUTPUT_DIR = CONFIG["paths"]["output_dir"]

# 跟风检测参数
HERD_CFG = CONFIG.get('herd_detection', {})
SIMILARITY_THRESHOLD = HERD_CFG.get('similarity_threshold', 0.35)
TIME_WINDOW_DAYS = HERD_CFG.get('time_window_days', 7)
MAX_FEATURES = HERD_CFG.get('max_features', 10000)
MIN_DF = HERD_CFG.get('min_df', 5)
MAX_DF = HERD_CFG.get('max_df', 0.9)
CHUNK_SIZE = HERD_CFG.get('chunk_size', 1000)  # 仅用于日志显示; >2000 篇分支已改 7 天窗双指针分桶 (W1), 不再用 chunked working_memory


# ============================================================================
# 2. 核心算法: 分块相似度计算
# ============================================================================

def _build_tfidf_vectorizer(n_docs: int, *, relaxed: bool = False) -> TfidfVectorizer:
    """Create a TF-IDF vectorizer whose df thresholds are valid for the group size.

    fix(omni-g-herd-01, 2026-06-11): min_df 比例化 (proportional df threshold)。
    原实现 min_df=MIN_DF 为**绝对**文档数: n=6 的组配合 max_df=0.9 (floor(5.4)=5)
    把存活词表压到"恰好 5/6 篇共现"的 boilerplate 子空间 → 余弦相似度系统性膨胀
    (盘上实证 +17%~∞ flags), 且与 n≤MIN_DF 的 relaxed 分支 (min_df=1) 形成断崖
    不连续 → 0.35 阈值跨银行不可比。现改 min(MIN_DF, max(2, ceil(0.01·n))):
    小/中组 min_df=2 (仅剪 hapax 噪声), n≳200 平滑爬升, n≥~500 封顶于 MIN_DF
    (大组与历史行为一致); 另加 max_df 守卫 — 若 floor(max_df·n) ≤ min_df
    (df-band 退化为近全员共现带), 放开 max_df=1.0 而非把 min_df 压回退化带。
    """
    if relaxed or n_docs < 4:
        # 微型组 (n<4): 任何 df 剪枝都会让词表退化, 直接放开
        min_df = 1
        max_df = 1.0
    else:
        # 比例化下限 2 (剪 hapax), 按 1%·n 爬升, 上限 MIN_DF (config 绝对计数 cap)
        min_df = int(min(MIN_DF, max(2, int(np.ceil(0.01 * n_docs)))))
        max_df = MAX_DF
        if isinstance(max_df, float) and 0 < max_df < 1.0:
            max_allowed_df = int(np.floor(max_df * n_docs))
            if max_allowed_df <= min_df:
                # fix(omni-g-herd-01): df-band 退化守卫 — 小 n 下 max_df 把允许带
                # 收窄到 [min_df, min_df] 或更窄时, 放开 max_df 保留全部 ≥min_df
                # 特征, 避免相似度在近全员共现子空间被强行抬高
                max_df = 1.0

    return TfidfVectorizer(
        max_features=MAX_FEATURES,
        min_df=min_df,
        max_df=max_df,
        analyzer='char_wb',  # 中文友好: 字符级 n-gram
        ngram_range=(2, 4),
        dtype=np.float32,  # 节省内存
    )


def _fit_tfidf_with_fallback(texts: list, *, bank_name=None, track=None):
    """Fit TF-IDF with transparent relaxed fallback; return matrix or None.

    fix(omni-g-herd-03, 2026-06-11): 原两层 ValueError fallback 均零日志 — 走
    relaxed (min_df=1/max_df=1.0) 的组其相似度刻度 (全词表) 与主参数组不同, 二次
    失败整组 weight 保持 1.0, 用户无法审计哪些 (bank, track) 降级 (违反降级透明
    红线, 同族 F7/F16/F21/F22)。现两分支各记 logger.warning(bank/track/n_docs/原因)。

    fix(omni-g-herd-02, 2026-06-11): max_features 截断咬合 (词表撞 cap) 时记
    logger.warning 披露规模依赖的相似度膨胀风险 (见模块头 ⚠ 披露)。
    """
    n_docs = len(texts)
    try:
        vectorizer = _build_tfidf_vectorizer(n_docs)
        tfidf_matrix = vectorizer.fit_transform(texts)
    except ValueError as exc:
        logger.warning(
            f"  [herd] TF-IDF 主参数 fit 失败, 降级 relaxed (min_df=1/max_df=1.0): "
            f"bank={bank_name}, track={track}, n_docs={n_docs}, 原因: {exc}. "
            f"该组相似度刻度与未降级组不同 (词表带放宽), 审计时注意。"
        )
        try:
            vectorizer = _build_tfidf_vectorizer(n_docs, relaxed=True)
            tfidf_matrix = vectorizer.fit_transform(texts)
        except ValueError as exc2:
            logger.warning(
                f"  [herd] relaxed 重试仍失败, 该组本轨保持 weight=1.0 / count=0: "
                f"bank={bank_name}, track={track}, n_docs={n_docs}, 原因: {exc2}"
            )
            return None
    # max_features 截断透明化: 词表撞 cap 说明按词频截断已咬合 (大组高频
    # boilerplate 子空间), 相似度刻度存在规模依赖膨胀 — 全量 run 必触发, 须披露
    if MAX_FEATURES and len(vectorizer.vocabulary_) >= MAX_FEATURES:
        logger.warning(
            f"  [herd] max_features={MAX_FEATURES} 截断咬合: bank={bank_name}, "
            f"track={track}, n_docs={n_docs} — 相似度计算被压入高频 ngram 子空间, "
            f"大组相似度刻度可能膨胀 (建议全量 run 做 max_features 敏感性检验)"
        )
    return tfidf_matrix


def _dense_similar_counts(tfidf_matrix, dates: list) -> np.ndarray:
    """≤2000 篇稠密分支 (参照实现): 全 N×N 余弦 + 7 天窗下三角 mask 的前驱计数。

    语义: 对每篇 i, 计 {j : j<i (index, 已排序故=日期序), |date_i-date_j|<=window,
    cos_sim(i,j) >= SIMILARITY_THRESHOLD}; NaT 篇不计数也不作候选。
    """
    n_articles = len(dates)
    _epoch = pd.Timestamp('1970-01-01')
    dates_num = np.array(
        [(d - _epoch).days if pd.notna(d) else np.nan for d in dates],
        dtype=np.float64)
    time_diff = np.abs(np.subtract.outer(dates_num, dates_num))
    time_diff = np.nan_to_num(time_diff, nan=float(TIME_WINDOW_DAYS + 1))
    valid_mask = (time_diff <= TIME_WINDOW_DAYS) & np.tril(
        np.ones((n_articles, n_articles), dtype=bool), k=-1)
    sim_matrix = 1.0 - pairwise_distances(tfidf_matrix, metric='cosine')
    herd_mask = (sim_matrix >= SIMILARITY_THRESHOLD) & valid_mask
    return herd_mask.sum(axis=1).astype(int)


def _bucketed_similar_counts(tfidf_matrix, dates: list) -> np.ndarray:
    """>2000 篇 M0 规模分支: 7 天窗双指针分桶, O(N·window), 与 _dense_similar_counts 数值逐位等价。

    前置: dates 已升序排序 (NaT 末尾) — 由 compute_herd_weights 的 sort_values('日期')
    保证。因 index 序 = 日期序, 每篇 i 的候选前驱仅落在 [date_i-window, date_i] 的连续
    滑窗 [lo, i) 内; 双指针使左界 lo 单调右移, 每篇只对窗内候选算余弦, 把 per-bank 成本
    从 O(N^2) 降到 O(N*window)。NaT 篇不计数也不作候选 (与稠密分支一致)。
    """
    n_articles = len(dates)
    _epoch = pd.Timestamp('1970-01-01')
    dates_num = np.array(
        [(d - _epoch).days if pd.notna(d) else np.nan for d in dates],
        dtype=np.float64)
    similar_counts = np.zeros(n_articles, dtype=int)
    lo = 0
    for i in range(n_articles):
        di = dates_num[i]
        if np.isnan(di):
            continue  # NaT: 与稠密分支 nan_to_num>window 一致, 不计数
        # 双指针: 左界右移直到 dates_num[lo] 落入 [di-window, di]
        # (有效前缀里无 NaN; isnan 守卫纯防御以兼容任意 NaT 排序)
        while lo < i and (np.isnan(dates_num[lo])
                          or di - dates_num[lo] > TIME_WINDOW_DAYS):
            lo += 1
        if lo >= i:
            continue
        # 仅对窗内候选 [lo, i) 算余弦 (稀疏行 × 稀疏块, 窗口仅几十~几百篇)
        # i:i+1 切片保持 2D (稀疏 CSR 与 numpy dense 通用; 裸 [i] 在 dense 下退化 1D)
        sims = 1.0 - pairwise_distances(
            tfidf_matrix[i:i + 1], tfidf_matrix[lo:i], metric='cosine')[0]
        # fix(herd-bucket-nat, metric-audit 2026-06-10): 排除窗内 NaT 候选, 与 _dense
        # (nan_to_num>window 已排除 NaT) 逐位对齐。生产 sort 使 NaT 末位故一般不触发, 但
        # 任意 NaT 排列下双指针窗 [lo,i) 可能含内部 NaT, 此守卫保证无条件等价 (3rd-layer P3)。
        _cand_valid = ~np.isnan(dates_num[lo:i])
        similar_counts[i] = int(
            np.count_nonzero((sims >= SIMILARITY_THRESHOLD) & _cand_valid))
    return similar_counts


def _compute_similar_counts_for_track(
    bank_df: pd.DataFrame, text_col: str, dates: list, *, bank_name=None
) -> np.ndarray | None:
    """对单一文本列计算同银行 + 时间窗口内的"前驱跟风计数"向量。

    抽出 v3.5.0 单轨实现的核心算法以支持双轨复用 (Plan E P1 B3)。
    返回 None 表示无法向量化 (空文本 / TF-IDF 失败), 调用方应保留 weight=1.0。

    fix(omni-g-herd-05, 2026-06-11): as-of yearly vocab fit — 原实现对单银行
    **全历史** texts 一次 fit_transform, 历史文章对的余弦使用了由未来文档频率决定
    的 IDF 权重与 df 词表剪裁 (前驱计数构念严格后视, 向量空间却含前视) → 样本扩展
    时历史 herd_weight 非不变 (0.35 阈值附近计数可翻转)。现按年截断: 年 t 文章的
    计数仅在 year ≤ t 文档拟合的向量空间内计算 (前驱候选集不变 — 7 天窗下三角本就
    只看更早文章); 年内残余前视为接受粒度 (面板为 bank-year, 年级 as-of 已足)。
    NaT 日期文章排除出 fit (年份未知; 既有语义下其本就不计数、不作候选)。

    Args:
        bank_df: 单银行子集, 已按日期升序排序 (NaT 末位, 由调用方 sort_values 保证)。
        text_col: 文本列名 ('content_full' for full, 'content_ctx' for ctx; 均含标题)。
        dates:    与 bank_df 对齐的日期列表 (含 NaT)。
        bank_name: 银行名, 仅用于降级/截断透明日志 (fix(omni-g-herd-03))。

    Returns:
        np.ndarray[int] 长度 = len(bank_df), 每元素为 i 的"早于 i 且相似 ≥ 阈值"
        前驱数; 完全无法向量化 (全空文本) 返回 None。
    """
    texts = bank_df[text_col].fillna('').astype(str).tolist()
    non_empty = [t for t in texts if len(t.strip()) > 0]
    if len(non_empty) < 2:
        return None

    n_articles = len(texts)
    counts = np.zeros(n_articles, dtype=int)

    # 非 NaT 前缀: 调用方已按日期升序排序 (NaT 末位), 故有效日期文档构成连续前缀
    # [0, dated_n); 首个 NaT 即截断 (防御任意排列 — NaT 后的文档不进任何年度 fit)。
    years: list[int] = []
    for d in dates:
        if pd.isna(d):
            break
        years.append(int(pd.Timestamp(d).year))
    dated_n = len(years)
    if dated_n < 2:
        # 可计数文档不足 2 篇 (其余皆 NaT): 与旧实现等价 (NaT 不计数), 全 0
        return counts

    years_arr = np.asarray(years)
    for t in np.unique(years_arr):
        # 年度前缀 [0, prefix_end) = 全部 year ≤ t 文档; 本年文章区间 [target_lo, prefix_end)
        prefix_end = int(np.searchsorted(years_arr, t, side='right'))
        target_lo = int(np.searchsorted(years_arr, t, side='left'))
        if prefix_end < 2:
            continue  # 首年仅 1 篇: 无前驱对可计
        sub_texts = texts[:prefix_end]
        if sum(1 for s in sub_texts if s.strip()) < 2:
            continue
        tfidf_matrix = _fit_tfidf_with_fallback(
            sub_texts, bank_name=bank_name, track=text_col)
        if tfidf_matrix is None:
            continue  # 该年度前缀 fit 失败 (已 warning): 本年文章保持 count=0
        sub_dates = dates[:prefix_end]
        if prefix_end <= 2000:
            sub_counts = _dense_similar_counts(tfidf_matrix, sub_dates)
        else:
            # M0 规模 (>2000 篇/前缀): 7 天窗双指针分桶替换原 O(N^2) 纯 Python 双循环。
            # 头部银行 (工农中建招) 全量 2007-2024 可达数十万篇, 原 O(N^2) 是 stage 24
            # 的 wall-clock cliff + N×N 余弦 OOM 悬崖。_bucketed 与 _dense 数值逐位等价,
            # 由 tests/test_24_herd_decay_bucketing.py 在 >2000 fixture 上对拍守护。
            sub_counts = _bucketed_similar_counts(tfidf_matrix, sub_dates)
        # 仅采纳本年文章的计数 (前驱候选 = 前缀内更早文章, 跨年 7 天窗自然覆盖)
        counts[target_lo:prefix_end] = sub_counts[target_lo:prefix_end]
    return counts


def compute_herd_weights(df: pd.DataFrame) -> pd.DataFrame:
    """对同一银行在时间窗口内的新闻进行**双轨**跟风检测 (Plan E P1 B3, v3.6.0)。

    算法流程 (对 full / ctx 两轨各跑一次):
      1. 按 target_bank 分组
      2. 对每组新闻进行 TF-IDF 向量化 (轨 1 用 'content_full' 标题+全文, 缺列回退
         '内容'/'正文'/'content'; 轨 2 用 'content_ctx')
         — fix(omni-g-herd-04, 2026-06-11): 原文档误称轨 1 为裸正文列, 与病根A修复
         后的实现 (优先 content_full) 不符, 已同步
      3. 计算余弦距离 (≤2000 篇 dense / >2000 篇 7 天窗双指针分桶, W1 2026-06-05)
      4. 在时间窗口内, 若文章 j 与更早的文章 i 的相似度 ≥ 阈值 (闭边界, 代码 >=),
         则 j 被标记为"跟风", 衰减权重递减
      5. 衰减公式: weight_j = 1 / (1 + n_similar_predecessors)

    v3.6.0 修复 (Edwards 2001 ORM measurement-treatment matching):
      原 v3.5.0 仅对全文计算 herd_weight 单列, 被下游同时施加到
      _full / _ctx 两轨, 造成 _ctx 路径被"全文相似度"惩罚。
      本版本输出 herd_weight_full + herd_weight_ctx 两列, 下游按轨匹配。

    Args:
        df: 篇章级 DataFrame, 须含 'target_bank', '日期', 'content_full'(或 '内容') 列;
            'content_ctx' 可选 — 缺失时 ctx 轨回退到 full 轨文本 (即与 full 同值)。

    Returns:
        df: 附加 'herd_weight_full' / 'herd_weight_ctx' /
            'n_similar_articles_full' / 'n_similar_articles_ctx' 四列。
    """
    logger.info("=" * 60)
    logger.info("步骤 1: 跟风/抄袭新闻检测与衰减加权 (双轨 v3.6.0)")
    logger.info("=" * 60)
    logger.info(f"  参数: similarity_threshold={SIMILARITY_THRESHOLD}, "
                f"time_window={TIME_WINDOW_DAYS}天, "
                f"max_features={MAX_FEATURES}, chunk_size={CHUNK_SIZE}")

    # 确保日期列为 datetime
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')

    # 双轨文本列解析
    # full 轨: 优先 content_full (含标题), 缺列回退 '内容' / '正文' / 'content'
    # P1 修复 (metric-audit 2026-06-02, 病根A): full 轨优先 content_full (含标题, 与
    # 加权对象 _full 情感同源), 缺列回退 '内容'/'正文'/'content'.
    full_col = 'content_full' if 'content_full' in df.columns else (
        '内容' if '内容' in df.columns else (
            '正文' if '正文' in df.columns else 'content'))
    has_full = full_col in df.columns
    # ctx 轨: 来自 stage 13 ctx_materializer (fix(omni-g-herd-04, 2026-06-11):
    # 原注释错标到 stage 21, 与本文件头部/现行架构矛盾); 缺失则回退 full
    has_ctx = 'content_ctx' in df.columns

    if not has_full:
        logger.warning(f"  文本列 '{full_col}' 不存在, 所有 herd_weight 设为 1.0")
        df['herd_weight_full'] = 1.0
        df['herd_weight_ctx'] = 1.0
        df['n_similar_articles_full'] = 0
        df['n_similar_articles_ctx'] = 0
        # NON-BREAKING alias (F-B 修)
        df['herd_weight'] = 1.0
        df['n_similar_articles'] = 0
        return df

    if not has_ctx:
        logger.warning(
            "  'content_ctx' 列不存在 (stage 13 ctx_materializer 未跑?), "
            "ctx 轨回退至全文计算 — 此时 herd_weight_ctx ≡ herd_weight_full, "
            "不构成真双轨。建议先执行 stage 13 物化 content_ctx。"
        )

    # 初始化结果列
    df['herd_weight_full'] = 1.0
    df['herd_weight_ctx'] = 1.0
    df['n_similar_articles_full'] = 0
    df['n_similar_articles_ctx'] = 0

    if 'target_bank' not in df.columns:
        logger.warning("  'target_bank' 列不存在, 所有 herd_weight 设为 1.0")
        # NON-BREAKING alias (F-B 修)
        df['herd_weight'] = df['herd_weight_full']
        df['n_similar_articles'] = df['n_similar_articles_full']
        return df

    bank_groups = df.groupby('target_bank')
    n_banks = len(bank_groups)
    logger.info(f"  共 {n_banks} 家银行待处理 (双轨)")

    total_herd_full = 0
    total_herd_ctx = 0

    for bank_idx, (bank_name, bank_df) in enumerate(bank_groups):
        if len(bank_df) < 2:
            continue

        # fix(herd-decay-01, metric-audit 2026-06-10): 同日文章排序须确定 (原默认 quicksort
        # 不稳定 + 无次键 → 同日 tie 顺序 run-to-run 非确定 → 加权 llm_vote_tone_hw 漂移)。
        # 加 kind='stable' + 内容派生次键 (标题, 内容) 使同日次序内容确定、跨运行可复现。
        _sort_keys = ['日期'] + [c for c in ('标题', '内容') if c in bank_df.columns]
        bank_df = bank_df.sort_values(_sort_keys, kind='stable').copy()
        indices = bank_df.index.tolist()
        dates = bank_df['日期'].tolist()

        # full 轨计算 (bank_name 仅供降级/截断透明日志, fix(omni-g-herd-03, 2026-06-11))
        full_counts = _compute_similar_counts_for_track(
            bank_df, full_col, dates, bank_name=bank_name)
        # ctx 轨计算 (缺失时回退 = full)
        if has_ctx:
            ctx_counts = _compute_similar_counts_for_track(
                bank_df, 'content_ctx', dates, bank_name=bank_name)
        else:
            ctx_counts = full_counts  # 回退: 与 full 同值, 由 has_ctx 警告告知用户

        for k, idx in enumerate(indices):
            if full_counts is not None:
                n_sim_f = int(full_counts[k])
                df.at[idx, 'n_similar_articles_full'] = n_sim_f
                df.at[idx, 'herd_weight_full'] = 1.0 / (1.0 + n_sim_f)
                if n_sim_f > 0:
                    total_herd_full += 1
            if ctx_counts is not None:
                n_sim_c = int(ctx_counts[k])
                df.at[idx, 'n_similar_articles_ctx'] = n_sim_c
                df.at[idx, 'herd_weight_ctx'] = 1.0 / (1.0 + n_sim_c)
                if n_sim_c > 0:
                    total_herd_ctx += 1

        if (bank_idx + 1) % 50 == 0:
            logger.info(f"  已处理 {bank_idx + 1}/{n_banks} 家银行")

    n_total = len(df)
    logger.info(f"  双轨跟风检测完成:")
    logger.info(f"    总新闻数: {n_total:,}")
    logger.info(f"    full 轨跟风: {total_herd_full:,} "
                f"({total_herd_full/max(n_total,1):.1%})")
    logger.info(f"    ctx  轨跟风: {total_herd_ctx:,} "
                f"({total_herd_ctx/max(n_total,1):.1%})")
    logger.info(f"    herd_weight_full mean={df['herd_weight_full'].mean():.4f}, "
                f"min={df['herd_weight_full'].min():.4f}")
    logger.info(f"    herd_weight_ctx  mean={df['herd_weight_ctx'].mean():.4f}, "
                f"min={df['herd_weight_ctx'].min():.4f}")

    # v3.6.0 NON-BREAKING 兼容层 (F-B 修): 保留 herd_weight / n_similar_articles
    # 单列 alias = _full 路径, 让 v3.5.x 既有调用方 (paper Stata 模板 / 测试套件 /
    # legacy panel reader) 不破坏. 下游若想用 ctx 路径必须显式引用 _ctx 后缀列.
    df['herd_weight'] = df['herd_weight_full']
    df['n_similar_articles'] = df['n_similar_articles_full']

    # 双轨独立性诊断 (Plan E P1 B3 验收门 #2):
    # 若 Spearman ρ(herd_weight_full, herd_weight_ctx) < 0.95, 视为"真双轨";
    # ≥ 0.95 提示 ctx 与 full 文本几乎相同 (可能 content_ctx fallback 比例过高)
    try:
        from scipy.stats import spearmanr
        valid = (df['herd_weight_full'].notna() &
                 df['herd_weight_ctx'].notna() &
                 (df['herd_weight_full'].nunique() > 1))
        if valid.sum() >= 50:
            rho, _ = spearmanr(
                df.loc[valid, 'herd_weight_full'],
                df.loc[valid, 'herd_weight_ctx'])
            logger.info(f"    双轨独立性诊断: Spearman ρ = {rho:.4f} "
                        f"({'真双轨' if abs(rho) < 0.95 else '⚠ 高度相关, 检查 content_ctx fallback 比例'})")
    except ImportError:
        pass

    return df


# ============================================================================
# 3. 主流程
# ============================================================================

def main():
    """主入口: 加载数据 → 跟风检测 → 保存。"""
    import time
    start_time = time.time()

    logger.info("=" * 60)
    logger.info(f"阶段 {STAGE_NAME} 启动")
    logger.info("=" * 60)

    # 加载篇章级数据: 固定读取阶段 23 (BERT情感分析) 的输出
    # 严禁回退读取 22/21 的输出，避免磁盘残留旧文件导致静默数据污染
    filenames = CONFIG.get('filenames', {})
    input_filename = filenames.get('output_23_bert_tone', '23_bert_tone.parquet')
    output_filename = filenames.get('output_24_herd_decay', '24_herd_decay.parquet')
    input_file = os.path.join(OUTPUT_DIR, input_filename)
    output_file = os.path.join(OUTPUT_DIR, output_filename)

    if not os.path.exists(input_file):
        logger.error(
            f"输入文件未找到: {input_file}。"
            f"请确保阶段 23 (tone_berts) 已在 enabled_methods 中启用并成功执行。"
        )
        # 显式以非零返回码退出, 让上游编排器能感知"DAG 24 依赖 23"契约违规,
        # 避免父进程把 'silent return' 误判为 stage 24 成功 (详见 plan c2)。
        raise SystemExit(1)

    # 记录输入文件修改时间，便于数据溯源审计
    import datetime as _dt
    _mtime = os.path.getmtime(input_file)
    logger.info(
        f"  📁 输入文件: {input_filename} "
        f"(修改时间: {_dt.datetime.fromtimestamp(_mtime).strftime('%Y-%m-%d %H:%M:%S')})"
    )

    df = pd.read_parquet(input_file)
    logger.info(f"  加载 {len(df):,} 条新闻 (来源: {input_filename})")

    # 执行跟风检测
    df = compute_herd_weights(df)

    # 保存 (追加 herd_weight 列后写入独立输出文件)
    # 使用数据版本控制保存
    from news_process.core.data_versioning import save_parquet_with_metadata
    save_parquet_with_metadata(
        df=df,
        output_path=output_file,
        stage_name="24_herd_decay",
        config=CONFIG,
        input_files=[input_file],
    )
    logger.info(f"  已保存至 {output_file}")

    elapsed = time.time() - start_time
    logger.info(f"  耗时: {elapsed:.1f}秒")
    logger.info(f"阶段 {STAGE_NAME} 完成 ✓")


if __name__ == '__main__':
    main()
