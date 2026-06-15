"""
news_process.pipeline.filtering.fintech_intensity — 阶段14：金融科技技术重度评分
=================================================================================

功能：
    在阶段 12 的 AC 关键词分类（二元判定）基础上，使用 TF-IDF + IDF 加权关键词
    向量质心（IDF-weighted keyword embedding centroid）计算连续型技术强度得分
    `fintech_intensity_score`，消除三类系统性偏差：
      1. 复读机刷分（Cheap Talk）— Bingler et al. (2022, FRL)
      2. 长文体量偏差（Document Length Bias）— Manning et al. (2008, Ch 6.4)
      3. 术语区分度缺失（Term Discriminability Loss）— Loughran & McDonald (2011, JF)

    核心公式（双重对数方程）:
      Score_d = Σ_{i: TF_{d,i}>0} [ (1 + ln(TF_{d,i})) / (1 + ln(L_d)) ] × W_i
      其中 W_i = IDF_i × CosSim_scaled_i

    白话解释:
      给每个金融科技关键词加上"含金量权重"（IDF稀缺度 × 语义纯粹度），
      同时防复读机刷分和长文偏差。产出连续型"真实技术强度分"。

    **阶段 12 零修改。** 本文件完全独立，删除即可回滚。

输入：
    阶段 12 输出的 `12_fintech_news_full.parquet`（全量含非金融科技, 用于全局 IDF;
      fix omni-g-fintech-01/-03, 2026-06-11: DF 按唯一文档 (标题,日期) 去重后以
      jieba 整词统计 — 与 TF 同分词器, 替换原 AC 子串计数源; 语料列在线物化
      content_full = 标题 + 内容, 与 TF 打分文本同语义。⚠ 参考语料必须是全量:
      13_news_with_ctx 仅含 fintech 子集, 不可用作 IDF 语料）
    阶段 12 输出的 `12_fintech_news.parquet`（仅金融科技，用于得分计算）

输出：
    `14_fintech_intensity.parquet`（= 12 filtered + fintech_intensity_score + intensity_verified
      + 三轨列 fintech_intensity_score_{full,ctx,ss} / intensity_verified_{full,ctx,ss};
      无后缀列 = _full alias 向后兼容。ss 轨 = 银行+金科同句共现, 回退镜像 ctx→全文 body）

学术依据：
    Li, K., Mai, F., Shen, R., & Yan, X. (2021). Measuring corporate culture using
      machine learning. The Review of Financial Studies, 34(7), 3265-3315.
    Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to Information
      Retrieval. Cambridge University Press.
    Arora, S., Liang, Y., & Ma, T. (2017). A simple but tough-to-beat baseline for
      sentence embeddings. Proceedings of ICLR 2017.
      — fix(omni-g-fintech-02, 2026-06-11): 仅为 "加权质心" 思想借鉴, **非 SIF 实现**。
        本实现无 a/(a+p(w)) 平滑逆频率权重、无首主成分 (common component) 去除,
        实际为 IDF 加权普通质心 (np.average(embeddings, weights=idf))。
    Ethayarajh, K. (2019). How contextual are contextualized word representations?
      Proceedings of EMNLP-IJCNLP 2019.
      — fix(omni-g-fintech-02, 2026-06-11): 仅作各向异性 **现象的动机引用**; 下文
        min-max + floor 重标定是工程化 ad hoc 处理, 非该文提出的校准方法。
    Singhal, A., Buckley, C., & Mitra, M. (1996). Pivoted document length normalization.
      Proceedings of SIGIR '96, pp. 21-29.

迁移说明 (Phase 7a-3)：
    本模块由原 root script ``14_fintech_intensity.py`` body 迁入。
    规范调用方式：
        python -m news_process.pipeline.filtering.fintech_intensity
"""

import logging
import math
import os
import sys
import time

import jieba
import numpy as np
import pandas as pd

jieba.setLogLevel(logging.WARNING)

from collections import Counter

from joblib import Parallel, delayed

# Phase 7a-3: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import log_memory_usage, log_stage_summary, setup_logging
from news_process.core.reporting import save_dataset
from news_process.core.text.ahocorasick import load_fintech_dict

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "14_fintech_intensity"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 读取技术重度评分配置 (config.yaml → fintech_intensity 节)
INTENSITY_CONFIG = CONFIG.get('fintech_intensity', {})
EMBEDDING_MODEL = INTENSITY_CONFIG.get('embedding_model', 'shibing624/text2vec-base-chinese')
MIN_DISTINCT_KEYWORDS_JIEBA = INTENSITY_CONFIG.get('min_distinct_keywords_jieba', 2)
WINSORIZE_PERCENTILES = INTENSITY_CONFIG.get('winsorize_percentiles', [1, 99])
ANISOTROPY_FLOOR = INTENSITY_CONFIG.get('anisotropy_floor', 0.1)

# 加载金融科技词典（与阶段 12 共享同一份词典）
FINTECH_KEYWORDS, _ = load_fintech_dict(CONFIG['paths'].get('fintech_dict_file', ''))
logger.info(f"金融科技词典: 共 {len(FINTECH_KEYWORDS)} 个词汇")

# fix(omni-g-fintech-03 组级裁决, 2026-06-11): jieba 注入态单源 — DF 与 TF 共用同一
# 注入 + 同一可匹配词集 (同分词器原则, 对齐 tone_words._get_tone_tokenizer 先例)。
# 词典中 6/1506 含空格/顿号的关键词 (如 'Open Banking' / '治理、风险与合规') 会被
# jieba 块切分正则在词典查找之前切开, jieba.add_word 注入也**永不可能**成为单 token
# ("注入" 路径技术不可行) → 按裁决走 "剔除 + 披露": 从权重宇宙 (IDF 归一化 / 质心 /
# CosSim 重标定) 剔除并 WARNING 披露, 避免 DF=0 的幻影词拉高 IDF 均值、扭曲质心与
# min-max 缩放 (TF 端 jieba 本就不可见这些词, 剔除不改任何单篇 TF 命中)。
# 白话: 个别带空格/顿号的关键词, jieba 分词器天生切不出来、文章里永远数不到它们;
# 如果还让它们参与算权重, 等于拿一批"永远命中 0 次的幽灵词"去拉偏所有词的权重,
# 所以干脆把它们从权重计算里踢掉, 并在日志里说明踢了哪些。
_KW_STATE: dict = {'injected': False, 'matchable': None, 'unmatchable': None}


def _ensure_keywords_injected() -> tuple:
    """注入全部关键词到 jieba 并划分可匹配/永不可匹配两类 (幂等, 进程内缓存)。

    Returns:
        tuple: (matchable: list[str], unmatchable: list[str])
    """
    if not _KW_STATE['injected']:
        for kw in FINTECH_KEYWORDS:
            jieba.add_word(kw)
        unmatchable = [kw for kw in FINTECH_KEYWORDS
                       if list(jieba.cut(kw)) != [kw]]
        _unmatch_set = set(unmatchable)
        matchable = [kw for kw in FINTECH_KEYWORDS if kw not in _unmatch_set]
        _KW_STATE['matchable'] = matchable
        _KW_STATE['unmatchable'] = unmatchable
        _KW_STATE['injected'] = True
        if unmatchable:
            logger.warning(
                f"⚠ 词典披露[fintech_intensity] (fix omni-g-fintech 组级, 2026-06-11): "
                f"{len(unmatchable)}/{len(FINTECH_KEYWORDS)} 个关键词含 jieba 块切分"
                f"边界字符 (空格/标点), 整词分词永不可命中, 已从 IDF/质心/CosSim "
                f"权重宇宙剔除 (TF 端本就不可见, 不影响单篇得分命中): {unmatchable}")
    return _KW_STATE['matchable'], _KW_STATE['unmatchable']


# ============================================================================
# 2. 全局文档频率解析 (Module A)
# ============================================================================

def _materialize_df_corpus_column(df_ref: pd.DataFrame) -> tuple:
    """为 DF 统计在线物化与 TF 同语义的语料列, 返回 (frame, 列名)。

    fix(omni-g-fintech-03, 2026-06-11): TF 打分文本 (full 轨) 是 content_full
    (= 标题 + 内容, stage 13 经 prepend_title 物化), 而 DF 参考语料
    12_fintech_news_full.parquet 无该列 → 此处用同一单一事实源 prepend_title
    在线物化 (逐字同口径), 使 DF 与 TF 同语料 (tone_words 2026-06-10 "IDF 在与
    TF 加权同一语料上统一计算" 先例; 否则标题词 df 被低估)。只进 DF 统计,
    不写盘。缺 '标题'/'内容' 列时回退 '内容' (与打分侧单轨退化路径同口径)。

    Returns:
        tuple: (df: pd.DataFrame, text_col: str)
    """
    if 'content_full' in df_ref.columns:
        return df_ref, 'content_full'
    if '标题' in df_ref.columns and '内容' in df_ref.columns:
        from news_process.core.text.entity_context import prepend_title
        titles = df_ref['标题'].fillna('').astype(str)
        bodies = df_ref['内容'].fillna('').astype(str)
        # .assign 浅拷贝其余列 (零数据复制), 不污染调用方 frame
        df_ref = df_ref.assign(
            content_full=[prepend_title(t, b) for t, b in zip(titles, bodies)])
        return df_ref, 'content_full'
    return df_ref, '内容'


def _compute_global_df_jieba(df_full: pd.DataFrame, text_col: str = '内容') -> tuple:
    """在全量参考语料上以 jieba 整词重算每个关键词的文档频率 (DF)。

    学术依据: Gentzkow, Kelly & Taddy (2019, JEL, §2.2):
      "IDF must be computed on the full reference corpus"

    fix(omni-g-fintech-03, 2026-06-11, P2): 旧实现 (_parse_global_df) 从 stage 12
      fintech_keyword_details 解析 DF — 该 DF 源自 AC 子串扫描, 允许子串误命中
      (如 '网贷' ∈ '互联网贷款') 与重叠双计 (如 '大数据'+'数据风控'), 而 TF 走
      jieba 整词 → 同一关键词两侧 "出现" 定义不同, DF 系统性偏大 → 子串高发
      关键词 IDF/权重系统性偏低, 违 GKT 同语料原则。tone_words.py 已为同一问题
      "坚决废除 Aho-Corasick 子匹配" (build_idf_weights), 本函数与其对齐:
      DF 与 TF 同分词器 (jieba 整词, 同注入态)、同语料列 (caller 传 content_full
      优先, 回退 '内容')。

    fix(omni-g-fintech-01, 2026-06-11, P3): DF 与 N_total 按**唯一文档**统计 —
      全量表每行 = (文章 × target_bank) 爆炸行 + 跨媒体转载 (盘上 4054 行 vs
      3646 唯一 (标题,日期)), 旧实现同一物理文档在 DF 分子与 N_total 分母中计
      k 次。现按 ['标题','日期'] 去重 (缺列回退文本内容自身为唯一键, 同
      tone_words fix omni-g-tonewords-04), 与 fintech_share 2026-06-10 确立的
      去重计数基对齐。

    Args:
        df_full: 全量参考语料 DataFrame（含非金融科技文档）。
        text_col: DF 统计语料列 — 与 TF 打分同列 (content_full 优先, 回退 '内容')。

    Returns:
        tuple: (keyword_doc_freq: Counter, N_total: int)
    """
    matchable, _ = _ensure_keywords_injected()
    kw_set = set(matchable)

    if text_col not in df_full.columns:
        logger.warning(f"  DF 语料列 '{text_col}' 不存在, 回退至 '内容'")
        text_col = '内容'

    # 唯一文档去重 (g-fintech-01): (标题, 日期) 优先; 缺列回退文本自身为键
    if {'标题', '日期'}.issubset(df_full.columns):
        texts = (df_full.drop_duplicates(subset=['标题', '日期'])[text_col]
                 .fillna('').astype(str).tolist())
    else:
        texts = (df_full[text_col].fillna('').astype(str)
                 .drop_duplicates().tolist())

    N_total = len(texts)
    keyword_doc_freq = Counter()
    if N_total == 0:
        logger.info("全局 DF 解析完成: 0 篇唯一文档")
        return keyword_doc_freq, 0

    def _chunk_df(chunk_texts):
        local = Counter()
        for text in chunk_texts:
            local.update(set(jieba.cut(text)) & kw_set)
        return local

    batch_size = 2000
    num_batches = max(1, (N_total - 1) // batch_size + 1)
    chunks = [texts[i * batch_size:(i + 1) * batch_size]
              for i in range(num_batches)]
    logger.info(f"全局 DF (jieba 整词, 唯一文档语料): {N_total} 篇, {num_batches} 批次")
    results = Parallel(n_jobs=-1, prefer='threads')(
        delayed(_chunk_df)(chunk) for chunk in chunks
    )
    for local in results:
        keyword_doc_freq.update(local)

    logger.info(f"全局 DF 解析完成: {N_total} 篇唯一文档, "
                f"{len(keyword_doc_freq)} 个不同关键词")
    return keyword_doc_freq, N_total


# ============================================================================
# 3. 综合权重构建 (Module B)
# ============================================================================

def _build_intensity_weights(keyword_doc_freq: Counter, N_total: int) -> dict:
    """构建 IDF × CosSim 综合权重。

    步骤 A: 全局 IDF 计算 + 均值归一化 + Winsorization
    步骤 B: IDF 加权质心 + 各向异性重标定
      (fix omni-g-fintech-02, 2026-06-11: 原称 "SIF 加权质心" 名实不符 — 无
      a/(a+p(w)) 频率权重、无首主成分去除, 实为 IDF 加权普通质心, 措辞已修正)
    步骤 C: 预乘综合权重

    fix(omni-g-fintech-03 组级裁决, 2026-06-11): 权重宇宙 = jieba 可匹配关键词
      (_ensure_keywords_injected 的 matchable 集)。永不可匹配的 6 个含空格/顿号
      关键词被剔除 — 它们 TF 端恒不可见, 留在宇宙内只会以 DF=0 的最大 IDF 拉高
      均值归一化分母、并把幻影向量混入质心与 CosSim min-max 缩放。

    Args:
        keyword_doc_freq: {关键词: 出现该词的文档数} (jieba 整词口径)。
        N_total: 全量唯一文档总数。

    Returns:
        dict: {关键词: 综合权重 (float)}
    """
    matchable, _ = _ensure_keywords_injected()
    if not keyword_doc_freq or N_total == 0:
        # 审计修复 (degradation F11): 升 ERROR — 同名 fintech_intensity_score
        # 此时由"语义加权"静默退化为纯词频, 列名不变, 下游回归无从察觉口径漂移
        # (R7 测量一致性). 全权重 1.0 的数值不可用于发表对比。
        logger.error("⚠ 口径降级[fintech_intensity]: DF 为空或文档数为零，"
                     "所有权重降级为 1.0 → 评分退化为纯词频, 与语义加权设计不一致, "
                     "勿用于发表/跨样本对比。")
        # fix(omni-g-fintech-03 组级): 降级宇宙同样限 matchable (不可匹配词无意义)
        return {kw: 1.0 for kw in matchable}

    # ── 步骤 A: 全局 IDF 计算 ──
    raw_idf = {}
    for kw in matchable:
        df_w = keyword_doc_freq.get(kw, 0)
        raw_idf[kw] = math.log10(N_total / (1 + df_w))

    values = list(raw_idf.values())
    mean_val = float(np.mean(values)) if values else 1.0
    if mean_val > 0:
        normed_idf = {w: v / mean_val for w, v in raw_idf.items()}
    else:
        # 审计修复 (degradation F11, 第5个同型支闭合): IDF 均值≤0 (绝大多数关键词
        # 近乎篇篇出现, 极小/退化样本可达) → 归一化 IDF 全塌缩为 1.0, IDF 维度静默
        # 失效, 评分退化。原先此支连 warning 都无 (可见性低于其余 4 支), 补 ERROR。
        logger.error("⚠ 口径降级[fintech_intensity]: IDF 均值≤0，归一化 IDF 全回退 1.0 "
                     "→ IDF 维度失效, 评分退化, 与设计不一致, 勿用于发表/跨样本对比")
        normed_idf = {w: 1.0 for w in raw_idf}

    normed_vals = np.array(list(normed_idf.values()))
    p_lo, p_hi = WINSORIZE_PERCENTILES
    if len(normed_vals) >= 2:
        p1 = float(np.percentile(normed_vals, p_lo))
        p99 = float(np.percentile(normed_vals, p_hi))
        idf_weights = {w: float(np.clip(v, p1, p99)) for w, v in normed_idf.items()}
    else:
        idf_weights = dict(normed_idf)

    logger.info(f"IDF 权重: mean={np.mean(list(idf_weights.values())):.4f}, "
                f"std={np.std(list(idf_weights.values())):.4f}")

    # ── 步骤 B: IDF 加权质心 + 各向异性重标定 ──
    # fix(omni-g-fintech-02, 2026-06-11): 原注释 "SIF 加权质心" 名实不符, 见模块
    # docstring Arora et al. (2017) 引用降格说明。
    try:
        from sentence_transformers import SentenceTransformer
        logger.info(f"加载词向量模型: {EMBEDDING_MODEL}")
        model = SentenceTransformer(EMBEDDING_MODEL)

        kw_list = list(idf_weights.keys())
        embeddings = model.encode(kw_list, show_progress_bar=False)

        weights_arr = np.array([idf_weights[kw] for kw in kw_list])
        centroid = np.average(embeddings, axis=0, weights=weights_arr)

        centroid_norm = centroid / (np.linalg.norm(centroid) + 1e-10)
        emb_norms = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-10)
        cos_sims = emb_norms @ centroid_norm

        # ── 各向异性重标定 (min-max + floor; fix omni-g-fintech-02: 工程化 ad hoc
        #    处理, Ethayarajh 2019 仅为现象动机引用, 非该文提出的校准方法) ──
        min_sim, max_sim = float(cos_sims.min()), float(cos_sims.max())

        cos_sim_scaled = {}
        if max_sim > min_sim:
            for i, kw in enumerate(kw_list):
                scaled = ANISOTROPY_FLOOR + (1.0 - ANISOTROPY_FLOOR) * \
                         (cos_sims[i] - min_sim) / (max_sim - min_sim)
                cos_sim_scaled[kw] = float(scaled)
        else:
            # 审计修复 (degradation F11, 复核补全): 第 4 个同型降级支 — 全部关键词
            # 余弦相似度相同时 CosSim 亦塌缩为 1.0 (评分退化为纯 IDF), 升 ERROR 闭合。
            logger.error("⚠ 口径降级[fintech_intensity]: 所有关键词余弦相似度相同，"
                         "CosSim 权重回退为 1.0 → 评分退化为纯 IDF, 与语义加权设计不一致, "
                         "勿用于发表/跨样本对比")
            cos_sim_scaled = {kw: 1.0 for kw in kw_list}

        logger.info(f"CosSim 校准: min={min_sim:.4f}, max={max_sim:.4f}, "
                    f"floor={ANISOTROPY_FLOOR}")
        del model, embeddings

    except ImportError:
        # 审计修复 (degradation F11): 升 ERROR — CosSim 维度静默失效会让
        # fintech_intensity_score 由语义加权退化为纯 IDF (列名不变, R7 口径漂移)。
        logger.error("⚠ 口径降级[fintech_intensity]: sentence_transformers 未安装，"
                     "CosSim 权重降级为 1.0（评分退化为纯 IDF, 与语义加权设计不一致, "
                     "勿用于发表/跨样本对比）")
        cos_sim_scaled = {kw: 1.0 for kw in idf_weights}
    except Exception as e:
        # 审计修复 (degradation F11/补漏): 装了库但运行期失败 (模型连不上/OOM 等)
        # 是更危险的同型触发 — 同样静默退化为纯 IDF, 升 ERROR。
        logger.error(f"⚠ 口径降级[fintech_intensity]: 词向量计算异常 "
                     f"({type(e).__name__}: {e})，CosSim 降级为 1.0 → 评分退化为纯 IDF, "
                     f"与语义加权设计不一致, 勿用于发表/跨样本对比")
        cos_sim_scaled = {kw: 1.0 for kw in idf_weights}

    # ── 步骤 C: 预乘综合权重 ──
    # fix(omni-g-fintech-03 组级): 宇宙限 matchable — 不可匹配词 TF 恒 0, 无需权重
    combined_weights = {}
    for kw in matchable:
        combined_weights[kw] = idf_weights.get(kw, 1.0) * cos_sim_scaled.get(kw, 1.0)

    sorted_weights = sorted(combined_weights.items(), key=lambda x: x[1], reverse=True)
    logger.info("综合权重 Top 20 (硬核词):")
    for kw, w in sorted_weights[:20]:
        logger.info(f"  {kw}: {w:.4f} (IDF={idf_weights.get(kw, 0):.3f}, "
                    f"CosSim={cos_sim_scaled.get(kw, 0):.3f})")
    logger.info("综合权重 Bottom 20 (泛化词):")
    for kw, w in sorted_weights[-20:]:
        logger.info(f"  {kw}: {w:.4f} (IDF={idf_weights.get(kw, 0):.3f}, "
                    f"CosSim={cos_sim_scaled.get(kw, 0):.3f})")

    return combined_weights


# ============================================================================
# 4. 逐文档得分计算 (Module C)
# ============================================================================

def _compute_intensity_scores(
    df: pd.DataFrame,
    combined_weights: dict,
    text_col: str = '内容',
) -> tuple:
    """计算每篇文档的技术重度得分 (v3.6.0 Plan E P4 B1: 支持多轨)。

    核函数（双重对数方程）:
      Score_d = Σ_{i: TF>0} [ (1 + ln(TF_{d,i})) / (1 + ln(L_d)) ] × W_i

    v3.6.0 升级:
      text_col 参数让同一函数可对 '内容' / 'content_ctx' / 'content_ss' 三种
      输入计算, 实现 fintech_intensity_score_{full,ctx,ss} 三轨。doc_length 仍按
      text_col 实际长度推算 (避免用全文长度归一化 ctx/ss 短文本)。

    Args:
        df: 金融科技子集 DataFrame。
        combined_weights: {关键词: 综合权重}。
        text_col: 文本列名 — '内容' (full 轨) / 'content_ctx' (ctx 轨) /
            'content_ss' (ss 轨, 银行+金科同句共现)。

    Returns:
        tuple: (scores: list[float], verified_flags: list[bool])
    """
    # fix(omni-g-fintech-03 组级, 2026-06-11): 注入走单源 helper, TF 匹配集与
    # DF 统计集 (_compute_global_df_jieba) 严格同一 (不可匹配词本就不可能命中)
    matchable, _ = _ensure_keywords_injected()

    if text_col not in df.columns:
        # 缺失时回退到 '内容' (保证 ctx/ss 轨在 stage 13 未跑时不崩)
        logger.warning(f"  '{text_col}' 列不存在, 回退至 '内容' (单轨退化)")
        text_col = '内容'
    contents = df[text_col].fillna('').astype(str).tolist()
    kw_set = set(matchable)

    def _tokenize_chunk(chunk_texts):
        chunk_results = []
        for text in chunk_texts:
            tokens = list(jieba.cut(text))
            tf = Counter(t for t in tokens if t in kw_set)
            chunk_results.append(tf)
        return chunk_results

    batch_size = 2000
    n_docs = len(contents)
    num_batches = max(1, (n_docs - 1) // batch_size + 1)
    chunks = [contents[i * batch_size:(i + 1) * batch_size] for i in range(num_batches)]

    logger.info(f"Jieba 并行分词: {n_docs} 篇, {num_batches} 批次")
    parallel_results = Parallel(n_jobs=-1, prefer='threads')(
        delayed(_tokenize_chunk)(chunk) for chunk in chunks
    )

    all_tfs = []
    for chunk_res in parallel_results:
        all_tfs.extend(chunk_res)

    scores = []
    verified_flags = []

    # v3.6.0 P4 B1: doc_length 按 text_col 实际长度推算 (ctx/ss 短文本不能用全文长度)
    if text_col == '内容' and 'doc_length' in df.columns:
        doc_lengths = df['doc_length'].values
    else:
        doc_lengths = df[text_col].fillna('').str.len().clip(lower=1).values

    n_fused = 0

    for idx in range(n_docs):
        tf = all_tfs[idx]
        L_d = max(int(doc_lengths[idx]), 1)

        distinct = len(tf)

        if distinct < MIN_DISTINCT_KEYWORDS_JIEBA:
            # fix(omni-g-fintech 组级裁决, 2026-06-11): 二次熔断由零填改 NaN —
            # 旧 0.0 会计入下游 bank-year 均值分母 (encode.py avg_ft_intensity* /
            # attention_media mean_*), 把 "未通过验证" 的文章当 "零强度" 系统性
            # 拉低均值。NaN 在 pandas mean/std 聚合中自动剔除 (sum 仍视同 0,
            # ln_sum_* 语义不变); intensity_verified=False 标志保持不变。
            scores.append(float('nan'))
            verified_flags.append(False)
            n_fused += 1
            continue

        score = 0.0
        ln_L = 1.0 + math.log(L_d) if L_d > 1 else 1.0
        for kw, count in tf.items():
            if count > 0 and kw in combined_weights:
                ln_tf = 1.0 + math.log(count)
                score += (ln_tf / ln_L) * combined_weights[kw]

        scores.append(round(score, 6))
        verified_flags.append(True)

    logger.info(f"得分计算完成: {n_docs} 篇, 二次熔断降级: {n_fused} 篇 "
                f"({n_fused / max(n_docs, 1) * 100:.1f}%)")

    valid_scores = [s for s, v in zip(scores, verified_flags) if v]
    if valid_scores:
        logger.info(f"得分分布 (verified=True): "
                    f"mean={np.mean(valid_scores):.4f}, "
                    f"std={np.std(valid_scores):.4f}, "
                    f"min={np.min(valid_scores):.4f}, "
                    f"max={np.max(valid_scores):.4f}, "
                    f"median={np.median(valid_scores):.4f}")

    return scores, verified_flags


# ============================================================================
# 5. 主流程编排 (Module D)
# ============================================================================

def main():
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")
    log_memory_usage(logger, "阶段启动")

    output_dir = CONFIG['paths']['output_dir']

    full_filename = CONFIG['filenames'].get('output_12_fintech_full', '12_fintech_news_full.parquet')
    full_path = os.path.join(output_dir, full_filename)

    if not os.path.exists(full_path):
        logger.error(f"全量分类结果文件未找到: {full_path}")
        logger.error("请确保阶段 12 已执行且生成了全量输出文件。")
        raise SystemExit(1)

    # fix(omni-g-fintech-03, 2026-06-11): IDF 参考语料 = stage 12 全量 (含非金融科技
    # 文档, GKT "full reference corpus" 语义) — ⚠ 勿改用 13_news_with_ctx: 盘上实证
    # 其仅含 is_fintech_news=True 子集 (1170/4054 行), 用它会把参考语料塌缩为命中
    # 子集、摧毁 IDF 区分度。语料列与 TF 同语义: 在线物化 content_full (= 标题 +
    # 内容, prepend_title 单一事实源, 与 stage 13 物化口径逐字一致), 只进 DF 统计
    # 不写盘。DF 以 jieba 整词重算 (_compute_global_df_jieba), 不再消费 AC 子串计数。
    logger.info(f"加载 IDF 参考语料 (stage 12 全量): {full_path}")
    df_ref = pd.read_parquet(full_path)
    df_ref, ref_text_col = _materialize_df_corpus_column(df_ref)
    keyword_doc_freq, N_total = _compute_global_df_jieba(df_ref, text_col=ref_text_col)
    del df_ref
    log_memory_usage(logger, "全量 DF 解析后(已释放)")

    combined_weights = _build_intensity_weights(keyword_doc_freq, N_total)

    filtered_filename = CONFIG['filenames'].get('output_12_fintech_news', '12_fintech_news.parquet')
    filtered_path = os.path.join(output_dir, filtered_filename)

    if not os.path.exists(filtered_path):
        logger.error(f"金融科技子集文件未找到: {filtered_path}")
        raise SystemExit(1)

    # v3.6.0 (Plan E P4 A1/B1): 优先读 stage 13 输出 (含 content_ctx 列),
    # 缺失则 fallback 到 stage 12 输出 (无 ctx, 触发 _ctx 轨回退)
    ctx_filename = CONFIG['filenames'].get(
        'output_13_news_with_ctx', '13_news_with_ctx.parquet')
    ctx_path = os.path.join(output_dir, ctx_filename)
    if os.path.exists(ctx_path):
        logger.info(f"加载 stage 13 输出 (含 content_ctx): {ctx_path}")
        df = pd.read_parquet(ctx_path)
        # stage 13 输出是 stage 12 全集 + ctx 列, 但 stage 14 需要金融科技子集
        if 'is_fintech_news' in df.columns:
            df = df[df['is_fintech_news'].astype(bool)].reset_index(drop=True)
            logger.info(f"  筛选 is_fintech_news=True: {len(df)} 篇")
    else:
        logger.warning(f"  stage 13 输出未找到 ({ctx_path}), fallback 至 stage 12 "
                       f"(ctx 轨将退化为 full)")
        logger.info(f"加载金融科技子集: {filtered_path}")
        df = pd.read_parquet(filtered_path)
    logger.info(f"金融科技子集: {len(df)} 篇文档")

    # v3.6.0 (Plan E P4 B1): 三轨计算 — full 用 content_full (回退 '内容'),
    # ctx 用 'content_ctx', ss 用 'content_ss' (银行+金科同句共现, 回退镜像 ctx→全文 body)
    # 输出列: fintech_intensity_score_{full,ctx,ss} + intensity_verified_{full,ctx,ss}
    # 向后兼容: 同时保留无后缀 fintech_intensity_score = _full alias
    # P1 修复 (metric-audit 2026-06-02, 病根A): full 轨改读 content_full (含标题), 与
    # ctx 轨 (content_ctx) 对称; 缺列回退 '内容' (_compute_intensity_scores 内亦有兜底).
    _full_col = 'content_full' if 'content_full' in df.columns else '内容'
    scores_full, verified_full = _compute_intensity_scores(df, combined_weights, text_col=_full_col)
    df['fintech_intensity_score_full'] = scores_full
    df['intensity_verified_full'] = verified_full
    # legacy alias (历史无后缀别名, 待各论文迁移到 _full/_ctx 列后弃用)
    df['fintech_intensity_score'] = scores_full
    df['intensity_verified'] = verified_full

    if 'content_ctx' in df.columns:
        logger.info("=" * 60)
        logger.info("v3.6.0 三轨: 对 content_ctx 计算 fintech_intensity_score_ctx")
        logger.info("=" * 60)
        scores_ctx, verified_ctx = _compute_intensity_scores(
            df, combined_weights, text_col='content_ctx')
        df['fintech_intensity_score_ctx'] = scores_ctx
        df['intensity_verified_ctx'] = verified_ctx
    else:
        logger.warning(
            "  content_ctx 列缺失 (stage 13 _materialize_ctx 未跑?), "
            "ctx 轨回退 = full — 此时 fintech_intensity_score_ctx ≡ _full")
        df['fintech_intensity_score_ctx'] = scores_full
        df['intensity_verified_ctx'] = verified_full

    # 第三轨 ss (银行+金科同句共现): 镜像 ctx 路径, 对 content_ss 计算
    # (content_ss = 标题 + 同句内同时含 目标银行∧金科词 的句 ±N 句窗;
    #  无共现时 stage 13 已回退全文 body, ss_is_fallback=True, 镜像 ctx 回退公理)。
    # 缺列优雅跳过 (stage 13 ss 物化未跑) → ss 轨回退 = full, 与 ctx 缺列分支同口径。
    if 'content_ss' in df.columns:
        logger.info("=" * 60)
        logger.info("v3.6.0 三轨: 对 content_ss 计算 fintech_intensity_score_ss")
        logger.info("=" * 60)
        scores_ss, verified_ss = _compute_intensity_scores(
            df, combined_weights, text_col='content_ss')
        df['fintech_intensity_score_ss'] = scores_ss
        df['intensity_verified_ss'] = verified_ss
    else:
        logger.warning(
            "  content_ss 列缺失 (stage 13 ss 物化未跑?), "
            "ss 轨回退 = full — 此时 fintech_intensity_score_ss ≡ _full")
        df['fintech_intensity_score_ss'] = scores_full
        df['intensity_verified_ss'] = verified_full

    assert 'is_fintech_news' in df.columns, "原有列 is_fintech_news 丢失!"
    assert 'fintech_intensity_score' in df.columns
    assert 'fintech_intensity_score_full' in df.columns
    assert 'fintech_intensity_score_ctx' in df.columns
    assert 'fintech_intensity_score_ss' in df.columns
    assert 'intensity_verified' in df.columns

    output_filename = CONFIG['filenames'].get(
        'output_14_fintech_intensity', '14_fintech_intensity.parquet')
    output_path = os.path.join(output_dir, output_filename)
    # 使用数据版本控制保存
    input_file = os.path.join(CONFIG['paths']['output_dir'],
                              CONFIG['filenames']['output_12_fintech_news'])
    save_dataset(
        df=df,
        output_path=output_path,
        logger=logger,
        stage_name="14_fintech_intensity",
        config=CONFIG,
        input_files=[full_path, input_file],
    )

    n_verified_full = sum(verified_full)
    n_verified_ctx = sum(df['intensity_verified_ctx'])
    n_verified_ss = sum(df['intensity_verified_ss'])
    n_total = len(df)
    logger.info(f"intensity_verified_full=True: {n_verified_full}/{n_total} "
                f"({n_verified_full / max(n_total, 1) * 100:.1f}%)")
    logger.info(f"intensity_verified_ctx=True:  {n_verified_ctx}/{n_total} "
                f"({n_verified_ctx / max(n_total, 1) * 100:.1f}%)")
    logger.info(f"intensity_verified_ss=True:   {n_verified_ss}/{n_total} "
                f"({n_verified_ss / max(n_total, 1) * 100:.1f}%)")

    log_stage_summary(logger, STAGE_NAME, stage_start, n_total, n_total)
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


if __name__ == "__main__":
    main()
