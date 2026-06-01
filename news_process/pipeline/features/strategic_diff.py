"""
25_strategic_differentiation.py — 金融科技战略差异度指数
=======================================================

改进 A: 构建基于文本距离的"金融科技战略差异度指数"
      (FinTech Strategic Differentiation Score)

论文依据 (核心公式映射):
  严格映射 Guzman & Li (2023, MS) Section 3 "From similarity to founding
  strategy" 中关于计算企业文本表述的余弦相似度并聚合至最近竞争者的规则:

      Ŝ_i = (1/N) Σ_{j ∈ J_i^N} δ_ij
      (Guzman & Li 2023, MS, Eq. in §3; 本模块 N=5 为基准, N=3~7 为敏感性检验)

  其中:
    - δ_ij = 1 - cosine_similarity(TF-IDF_i, TF-IDF_j) 为银行 i 与银行 j
      之间的文本距离
    - J_i^N 为银行 i 在文本向量空间中的 N 个最近邻集合
    - Ŝ_i 值越大, 表明银行 i 的金融科技战略与同业差异越大, 即占据更独特的
      "战略生态位" (strategic niche)

  Hoberg & Phillips (2016, JPE, §III) 原始框架使用 10-K 产品描述构建
  Text-based Network Industry Classifications (TNIC), 本模块将其迁移至
  银行金融科技新闻文本场景, 将每家银行的年度新闻聚合文档视为其"产品描述"
  的代理变量。

预期的边际贡献 / 解决的内生性问题:
  引入该指数作为全新的分析维度。将所有银行当年的金融科技新闻文本聚合,
  并计算其与其他所有银行的 TF-IDF (及 LDA+JSD / Embedding) 文本相似度,
  通过测度每家银行在向量空间中与其最近的几家同业的文本"距离", 能够揭示
  银行业金融科技创新的战略生态位。这解决了当前研究中粗颗粒度加权方法
  (单纯比拼新闻数量和情感得分) 所带来的内生性问题 — 数量和情感指标
  容易受银行规模、媒体关注度等混杂因素驱动, 而文本距离度量的是战略内容
  本身的差异性, 能更精准地分离出差异化战略所带来的超额边际贡献。

本模块实现基于新闻文本的银行战略差异度量化框架, 核心思路是:
  1. 按 (银行, 年度) 聚合新闻文本 → 构建 "企业-年" 文档
  2. 使用多种文本表征方法 (TF-IDF / LDA / Embedding) 计算银行间文本距离
  3. 对每家银行取 N-最近邻 (N=3~7) 的平均距离作为差异度指标 → Ŝ_i
  4. 计算全行业向量法 (centroid distance) 度量与行业平均的差异
  5. 计算 Fluidity (市场流动性) 衡量竞争环境变化速度
  6. Full/Ctx 双轨对比: 检验全文 vs 上下文窗口文本的指标稳健性

方法论来源:
  - [核心] 创业战略度量: Guzman, J., & Li, A. (2023). Measuring founding
    strategy. Management Science, 69(1), 101–118.
    https://doi.org/10.1287/mnsc.2022.4369
    → Section 3: 余弦相似度 + N-最近邻聚合公式, 本模块的核心算法来源
  - [核心] 文本产品空间: Hoberg, G., & Phillips, G. (2016). Text-based
    network industries and endogenous product differentiation. Journal of
    Political Economy, 124(5), 1423–1465. https://doi.org/10.1086/688176
    → §III: TNIC 框架, 逐年重建文本相似度矩阵的方法论基础
  - 产品市场流动性: Hoberg, G., Phillips, G., & Prabhala, N. (2014). Product
    market threats, payouts, and financial flexibility. The Journal of Finance,
    69(1), 293–324. https://doi.org/10.1111/jofi.12050
    → Eq. 2: Fluidity 指标定义, 衡量竞争环境动态变化
  - 文本创新度量: Bellstam, G., Bhagat, S., & Cookson, J. A. (2021). A
    text-based analysis of corporate innovation. Management Science, 67(7),
    4004–4031. https://doi.org/10.1287/mnsc.2020.3682
  - JSD 距离: Lin, J. (1991). Divergence measures based on the Shannon
    entropy. IEEE Transactions on Information Theory, 37(1), 145–151.
    https://doi.org/10.1109/18.61115
  - TF-IDF 稳健性: Manning, C. D., Raghavan, P., & Schütze, H. (2008). 
    Introduction to information retrieval. Cambridge University Press. 
    https://doi.org/10.1017/CBO9780511809071
  - 文本连贯性: 欧阳志刚, 胡雯华. (2024). 央行沟通公告有助于提升政策利率
    的传导效率吗？数量经济技术经济研究, 41(10), 69–88. 
    https://doi.org/10.13653/j.cnki.jqte.2024.10.004
  - 句向量表征: Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence
    embeddings using Siamese BERT-networks. Proceedings of EMNLP 2019,
    3982–3992. https://doi.org/10.18653/v1/D19-1410
  - LDA 主题模型: Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent
    Dirichlet allocation. Journal of Machine Learning Research, 3, 993–1022.
    https://www.jmlr.org/papers/v3/blei03a.html
  - 文本数据方法论: Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as
    data. Journal of Economic Literature, 57(3), 535–574.
    https://doi.org/10.1257/jel.20181020
  - [新增] 全行业向量法: 谢佳松, 樊嘉诚, & 林建浩. (2025). 信息摩擦、公共数据
    与企业创新边界. 经济研究, (11).
    → 图 1: BERTopic 余弦相似度 → 技术布局引导, 本模块迁移为行业质心距离

输出列 (~50 列, 值域均为 [0, 1]; 含 2026-05-29 双模型新增的 text2vec 稳健 twin 列):
  --- N-最近邻 Full 轨 (18 列) ---
  strat_diff_n{3..7}       TF-IDF char N-近邻差异度 (Ŝ_i, N=3~7)
  strat_diff_n{3..7}_w     TF-IDF jieba 词级 N-近邻差异度 (稳健性检验)
  strat_sim_max / _w       最大同行相似度 (max cosine sim to any peer)
  strat_fluidity / _w      市场流动性 (Hoberg et al. 2014, Eq. 2)
  strat_diff_n5_lda        LDA+JSD N=5 差异度 (主题分布距离, 稳健性检验)
  strat_sim_max_lda        LDA+JSD 最大同行相似度
  strat_diff_n5_emb        Embedding N=5 差异度 (稠密语义距离, 稳健性检验)
  strat_sim_max_emb        Embedding 最大同行相似度
  --- N-最近邻 Ctx 轨 (8 列, N=5 only) ---
  strat_diff_n5_ctx / _w_ctx    TF-IDF char/word Ctx 轨 N=5 差异度
  strat_sim_max_ctx / _w_ctx    TF-IDF char/word Ctx 轨最大同行相似度
  strat_diff_n5_lda_ctx         LDA+JSD Ctx 轨 N=5 差异度
  strat_sim_max_lda_ctx         LDA+JSD Ctx 轨最大同行相似度
  strat_diff_n5_emb_ctx         Embedding Ctx 轨 N=5 差异度
  strat_sim_max_emb_ctx         Embedding Ctx 轨最大同行相似度
  --- 全行业向量法 (谢佳松 2025; 8 列) ---
  centroid_diff_tfidf_c / _w     TF-IDF char/word Full 轨 centroid 距离
  centroid_diff_lda              LDA θ Full 轨 centroid 距离
  centroid_diff_emb              Embedding Full 轨 centroid 距离
  centroid_diff_tfidf_c_ctx / _w_ctx  TF-IDF Ctx 轨 centroid 距离
  centroid_diff_lda_ctx          LDA θ Ctx 轨 centroid 距离
  centroid_diff_emb_ctx          Embedding Ctx 轨 centroid 距离
  --- 相邻期文本连贯性 (欧阳志刚 & 胡雯华 2024; 8 列) ---
  coh_tfidf_c_{full|ctx}   TF-IDF char 相邻期文本连贯性
  coh_tfidf_w_{full|ctx}   TF-IDF jieba 相邻期文本连贯性 (稳健性检验)
  coh_lda_{full|ctx}       LDA+JSD 相邻期文本连贯性 (稳健性检验)
  coh_emb_{full|ctx}       Embedding 相邻期文本连贯性 (稳健性检验)
  --- text2vec 稳健 twin 列 (2026-05-29 双模型重构; stage 30 退役后由本 stage 内联产出) ---
  strat_diff_n5_emb_t2v{,_ctx}    text2vec N=5 Embedding 差异度
  strat_sim_max_emb_t2v{,_ctx}    text2vec Embedding 最大同行相似度
  centroid_diff_emb_t2v{,_ctx}    text2vec Embedding centroid 距离
  strat_diff_t2v_{full,ctx}       契约别名 (export REQUIRED_PANEL_COLUMNS 硬要求)
  coh_emb_t2v_{full,ctx}          text2vec Embedding 相邻期连贯性

注意: 连贯性变量 (coh_*) 对首年及年份间隙返回 NaN (与 strat_fluidity 一致),
      严格定义"相邻期"为连续年度 (year_t 与 year_{t-1})。

局限性:
  1. 原始文献 (Hoberg & Phillips 2016) 使用企业自有 10-K 披露文本,
     本项目使用第三方新闻报道, 测量的是"媒体感知差异"而非"自我披露差异"
  2. 银行样本量 (~54 家/年) 远小于 TNIC 数据集 (~5000 家/年),
     N=5 近邻占样本比例 ~10%, 需注意小样本偏差
  3. Embedding 长文本已采用 token 分段 + 均值池化, 避免超长文本尾部语义被截断
"""
# ══ 导入依赖库 (Dependencies) ══
# 【术语】导入数值计算、NLP 特征提取、主题模型和信息论距离等工具库
# 【白话】下面这些 import 就是"引入工具箱":
#   - numpy/pandas: 数据处理的基础工具，类似 Excel 的高级版
#   - jieba: 中文分词器，能把"银行金融科技"切成"银行""金融""科技"
#   - TfidfVectorizer: 把文本转成 TF-IDF 向量（想象成把文章变成坐标点）
#   - cosine_similarity: 计算两个向量的余弦相似度（0=方向完全不同, 1=方向完全相同）
#   - LDA (Latent Dirichlet Allocation): 主题模型，自动发现文本中隐藏的"话题"
#   - jensenshannon: Jensen-Shannon 散度，衡量两个概率分布有多不同
import asyncio
import logging
import os
import sys

import jieba
import numpy as np
import pandas as pd

jieba.setLogLevel(logging.WARNING)
import json

import tiktoken
from scipy.spatial.distance import jensenshannon
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Phase 5c-1: 注入项目根, 让 ``news_process.core.*`` 在包模式下可解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.caching import LLMCache
from news_process.pipeline.text import embedding_engine as _eng

# v3.7.0 (DC3 + C1 + M13 修复): LLM raw response archive 集成 (V4 F-P2.1 critical)
# R1-R5 audit fix A5 (2026-05-27): V4 F-P2.1 仅承诺 stage 21 (tone_llms) + stage 48
# (llm_peer_iv) 接入, 此 import 是 strategic_diff stage 27c embedding LLM 调用的
# **前瞻性留位**, 当前 0 call site 是已知设计 (并非虚假声明). 未来若 stage 27c
# 真接入 LLM-based embedding (vs 当前 sentence-transformers 本地) 时再补 call.
# 保留 import 而非删除, 以维持模块层 archive 可用性检测稳定接口.
try:
    from news_process.pipeline.llm_archive import (
        archive_record as _llm_archive_record,  # noqa: F401  # TODO: stage 27c embedding archive
    )
    from news_process.pipeline.llm_archive.archive import _get_default_archive as _get_archive  # noqa: F401
    _LLM_ARCHIVE_AVAILABLE = True
except ImportError as _archive_import_exc:
    _llm_archive_record = None
    _get_archive = None
    _LLM_ARCHIVE_AVAILABLE = False
    import logging as _logging_for_archive_error
    _logging_for_archive_error.getLogger(__name__).warning(
        "v3.7.0: llm_archive 不可用 (%s). strategic_diff 当前未调用 archive_record "
        "(stage 27c 使用本地 sentence-transformers, 无 LLM raw response 需归档).",
        _archive_import_exc,
    )

# Embedding Token 级精确截断与分段 (统一 Stage 15 标准)
# 【术语】text-embedding-3-small 使用 cl100k_base 编码，单条上限 8,191 tokens
#   对超过上限的文本 (如权威政策语料)，采用 Early Chunking + Mean Pooling
#   策略 (Guenther et al., 2024, arXiv:2409.04701; Reimers & Gurevych, 2019,
#   EMNLP, DOI: 10.18653/v1/D19-1410)，分段嵌入后均值池化为单个向量。
# 【白话】用 AI 模型同款的"令牌计数器"来精确控制文本长度，
#   短文本正常处理，超长文本切段后取平均，保留完整语义。
_EMB_ENCODING = tiktoken.get_encoding("cl100k_base")
_EMB_MAX_TOKENS = 8191
_EMB_MAX_TOKENS_PER_REQUEST = 250_000

RETRY_DELAY = 5
MAX_RETRY_DELAY = 60


def _coerce_positive_int(value, default: int) -> int:
    """配置兜底: 将 token 上限解析为正整数，异常时回退到安全默认值。"""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


def _split_text_for_embedding(text: str) -> list[str]:
    """按 token 粒度切分超长文本，适配 Embedding 模型上限。

    【术语】Early Chunking (Guenther et al., 2024, arXiv:2409.04701):
      将超过单条上限的文本切分为不重叠段，各段独立嵌入后均值池化。
    【白话】短文本原样返回；超长文本（如权威政策语料）切成多段处理。

    Returns:
        list[str]: 分段文本列表，每段 <= 8,191 tokens。
    """
    try:
        if pd.isna(text):
            text = ""
    except (TypeError, ValueError):
        pass
    text = str(text)
    if not text:
        text = " "

    tokens = _EMB_ENCODING.encode(text)
    if len(tokens) <= _EMB_MAX_TOKENS:
        return [text]  # 未超限，直接返回原文 (避免 encode/decode 往返)
    return [_EMB_ENCODING.decode(tokens[i:i + _EMB_MAX_TOKENS])
            for i in range(0, len(tokens), _EMB_MAX_TOKENS)]


# --- 从 panel/encode 导入共享配置 (Phase 2a: 取代旧的 importlib 反射) ---
from news_process.pipeline.panel.encode import CONFIG, logger  # noqa: E402

LLM_CONFIG = CONFIG.get('tone_llm_processing', {})
EMBEDDING_CONFIG = CONFIG.get('embedding_api', {})            # MAIN spec (text-embedding-3-small)
_ROBUSTNESS_SPEC = CONFIG.get('embedding_robustness', {})    # 稳健 twin spec (text2vec, 2026-05-29 双模型)
_ALIGN_CFG = CONFIG.get('article_alignment', {})
_EMB_MAX_TOKENS = _coerce_positive_int(
    _ALIGN_CFG.get('max_tokens_per_input'), _EMB_MAX_TOKENS)
_EMB_MAX_TOKENS_PER_REQUEST = _coerce_positive_int(
    _ALIGN_CFG.get('max_tokens_per_request'), _EMB_MAX_TOKENS_PER_REQUEST)
_EMB_MAX_TOKENS_PER_REQUEST = max(
    _EMB_MAX_TOKENS, _EMB_MAX_TOKENS_PER_REQUEST)
_LOCAL_EMBEDDING_MODEL = None


def _embedding_config_uses_local(spec=None) -> bool:
    """spec 是否指向本地模型 (默认主 spec)。委托给 embedding_engine。"""
    return _eng.spec_uses_local(spec if spec is not None else EMBEDDING_CONFIG)


def _encode_embeddings_local(texts, *, spec=None, log_prefix="Embedding") -> np.ndarray:
    """本地 sentence-transformers 编码 (默认主 spec)。委托给 embedding_engine。"""
    return _eng.encode_local(
        texts, spec if spec is not None else EMBEDDING_CONFIG, log_prefix=log_prefix)

# 中文停用词表 (Stopwords) — 排除高频虚词以提高 TF-IDF 区分度
# 【术语】停用词 (Stopwords) 是 NLP 中被过滤的高频无信息量词汇，
#   去除后可提升 TF-IDF 的区分性 (discriminative power)
# 【白话】"的""了""在"这些词几乎每篇文章都有，不能帮我们区分不同银行，
#   所以要去掉，只保留有实际含义的词（如"区块链""风控""支付"）。
# 参考: Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data.
# Journal of Economic Literature, 57(3), 535–574.
# https://doi.org/10.1257/jel.20181020
_STOPWORDS = {'的', '了', '在', '是', '和', '与', '为', '对', '等',
              '将', '也', '及', '到', '从', '中', '上', '下', '不'}


def _jieba_tokenizer(text: str) -> list[str]:
    """jieba 中文分词 + 停用词过滤 (Chinese Tokenizer with Stopword Filtering)。

    【术语】基于 jieba 的中文分词器，保留 len≥2 的 token 并移除停用词，
      符合 NLP 中文文本预处理的标准做法 (Gentzkow et al. 2019, JEL)。
    【白话】把一段中文文本切成一个个词语，然后：
      - 扔掉单个字（如"的""了"），因为单字没啥意义
      - 扔掉停用词（如"和""在"），只保留有意义的词
    例如: "银行的金融科技" → ["银行", "金融", "科技"]
    """
    return [w for w in jieba.lcut(text) if len(w) >= 2 and w not in _STOPWORDS]


def _l2_normalize(m: np.ndarray) -> np.ndarray:
    """L2 行归一化 (L2 Row Normalization)，零向量保持不变 (避免除零)。

    【术语】将每行向量除以其 L2 范数 (Euclidean norm)，使其模长为 1，
      确保 cosine_similarity 等价于向量内积，提升计算效率。
    【白话】把每行向量"拉"成长度为 1，这样比较方向时不受"长度"影响。
      就像比较两个人走的方向，不管他们走了多远，只看方向是否一致。
    """
    norms = np.linalg.norm(m, axis=1, keepdims=True)
    return m / np.where(norms == 0, 1, norms)


# ============================================================================
# 1. 文本聚合 (Text Aggregation): 按 (银行, 年度) 拼接新闻标题+正文
# 【术语】构建 Hoberg & Phillips (2016) 框架中的"企业-年"文档 (firm-year document)，
#   将同一银行同一年度的所有新闻拼接为单一文档作为"产品描述"的代理变量 (proxy)。
# 【白话】把同一家银行、同一年的所有新闻全部拼在一起，变成一篇"大文章"。
#   就像把某银行 2023 年所有新闻合并成一份"年度总结"，用来代表它这一年的
#   金融科技战略方向。
# ============================================================================

def _aggregate_bank_year_texts(df_exploded, text_col='内容'):
    """按 (target_bank, year) 聚合新闻文本。

    【学术】Hoberg & Phillips (2016, JPE, §II.A) 将同一企业同一年度的
    所有 10-K 产品描述拼接为单一文档, 构建"年度产品空间"向量。
    本函数将其适配至新闻场景: 每家银行每年的所有新闻拼接为一篇"年度文本画像"。

    【白话】把同一家银行同一年的所有新闻（标题+正文）合并成一大段文本,
    方便后续用数学方法比较不同年份之间这段文本的变化程度。

    Args:
        df_exploded: 文章-银行级 DataFrame, 需包含 target_bank, year 列
        text_col: 聚合使用的文本列名 ('内容' for Full 轨, 'content_ctx' for Ctx 轨)

    Returns:
        DataFrame[target_bank, year, agg_text], 已过滤空文本行
    """
    # 守卫: 空输入或目标文本列缺失 → 直接返回空 DataFrame
    if df_exploded.empty or text_col not in df_exploded.columns:
        logger.info(f"  文本聚合: 0 个 Bank-Year 文档 (text_col='{text_col}' 缺失或数据为空)")
        return pd.DataFrame(columns=['target_bank', 'year', 'agg_text'])

    def _concat(group):
        # 闭包引用外层 text_col (而非硬编码 '内容'), 支持双轨聚合
        bodies = group[text_col].fillna('').astype(str)
        titles = group['标题'].fillna('').astype(str) if '标题' in group.columns else bodies
        return ' '.join(titles + ' ' + bodies)

    agg = df_exploded.groupby(['target_bank', 'year']).apply(
        _concat, include_groups=False).reset_index(name='agg_text')
    result = agg[agg['agg_text'].str.strip().str.len() > 0]
    logger.info(f"  文本聚合: {len(result)} 个 Bank-Year 文档 "
                f"(覆盖 {result['target_bank'].nunique()} 银行, "
                f"{result['year'].nunique()} 年)")
    return result


# ============================================================================
# 2. TF-IDF 相似度矩阵 (Cosine Similarity Matrix) (Hoberg & Phillips 2016, §III)
# 【术语】通过 TF-IDF 向量化构建逐年的 pairwise cosine similarity matrix，
#   复现 Hoberg & Phillips (2016, JPE) §III 中的 TNIC 方法论。
# 【白话】把每家银行的"年度总结"文本变成数字向量，然后两两比较。
#   就像把 54 家银行放在一个"坐标系"里，离得近的说明战略很像，离得远说明很不一样。
# ============================================================================

def _build_tfidf_sim_matrix(texts, mode='char'):
    """构建逐年独立的 TF-IDF cosine 相似度矩阵。

    两种模式:
      - char: char_wb(2,4) 字符 n-gram, 不依赖分词质量
      - word: jieba 词级, 语义粒度更高

    参数设置依据:
      - max_features=5000: 控制词表大小, 平衡信息量与噪声
      - min_df=1: 保留所有出现过的词, 避免小样本/高差异文本清空词表
      - max_df=0.95: 排除出现在 95% 以上文档的超高频词 (高度相似时降级为 1.0)
      - sublinear_tf=True: log(1+tf) 降低词频极端值的影响
        (Manning, C. D., Raghavan, P., & Schütze, H. (2008).
        Introduction to Information Retrieval. Cambridge University Press.
        https://doi.org/10.1017/CBO9780511809071, §6.4)

    Args:
        texts: 文本列表 (逐年切片)
        mode: 'char' 或 'word'

    Returns:
        tuple: (sim, tfidf_mat)
          - sim: np.ndarray, 相似度矩阵, 对角线 NaN (排除自身比较)
          - tfidf_mat: csr_matrix (n_banks, n_features), 原始 TF-IDF 向量
            (供 centroid 计算复用)
    """
    # min_df=1: 保留所有出现过的词, 防止小样本/高差异文本清空词表
    # 噪声控制依赖 max_df=0.95 和 max_features=5000
    _mdf = 1
    _max_df = 0.95
    if mode == 'char':
        _kw = dict(analyzer='char_wb', ngram_range=(2, 4),
                   max_features=5000, min_df=_mdf, sublinear_tf=True)
    else:
        _kw = dict(tokenizer=_jieba_tokenizer,
                   token_pattern=None,
                   max_features=5000, min_df=_mdf, sublinear_tf=True)
    try:
        vec = TfidfVectorizer(max_df=_max_df, **_kw)
        tfidf_mat = vec.fit_transform(texts)
        sim = cosine_similarity(tfidf_mat)
    except ValueError:
        # max_df=0.95 过滤后词表为空 (如文档高度相似), 降级为不过滤
        logger.warning(f"    TF-IDF {mode}: max_df=0.95 词表清空, 降级为 max_df=1.0")
        vec = TfidfVectorizer(max_df=1.0, **_kw)
        tfidf_mat = vec.fit_transform(texts)
        sim = cosine_similarity(tfidf_mat)
    np.fill_diagonal(sim, np.nan)
    return sim, tfidf_mat  # sim: similarity ∈ [0,1]; tfidf_mat: csr_matrix (n_banks, n_features)


# ============================================================================
# 3. LDA + Jensen-Shannon 距离矩阵 (Topic Distribution Distance) (Lin 1991; Blei et al. 2003)
# 【术语】先通过 LDA (Blei et al. 2003) 得到每家银行的主题分布 θ_i，
#   再用 JSD (Lin 1991) 计算 pairwise 主题分布距离，作为 TF-IDF 的稳健性检验。
# 【白话】另一种比较方法。先用 LDA 发现每家银行新闻的"主题比例"
#   （比如: 30% 讲移动支付, 20% 讲区块链, 50% 讲智能风控），
#   然后用 JSD 距离衡量两家银行的主题比例有多不同。
#   这是 TF-IDF 方法的稳健性检验 (robustness check)，看换一种方法结果是否一致。
# ============================================================================

def _build_lda_jsd_matrix(texts, n_banks):
    """jieba 词级 → LDA 主题分布 → pairwise JSD 距离。

    使用 Jensen-Shannon divergence (Lin 1991) 度量主题分布差异,
    JSD 是 KLD 的对称化平滑版本, 满足度量公理 (三角不等式)。

    主题数 K 的选取:
      - K = max(10, n_banks // 30), 确保主题数不低于 10
      - 当银行数 ~54 时 K=10, 每个主题约覆盖 5-6 家银行

    Args:
        texts: 文本列表
        n_banks: 银行数量

    Returns:
        tuple: (jsd_mat, theta)
          - jsd_mat: np.ndarray, JSD 距离矩阵 ∈ [0,1], 对角线 NaN
          - theta: np.ndarray (n_banks, K), LDA 主题分布矩阵
            (供 centroid 计算复用)
    """
    K = max(10, n_banks // 30)
    cv = CountVectorizer(
        tokenizer=_jieba_tokenizer,
        token_pattern=None,
        max_features=5000, min_df=1, max_df=0.95)
    try:
        dtm = cv.fit_transform(texts)
    except ValueError:
        # max_df=0.95 过滤后词表为空, 降级
        logger.warning("    LDA: max_df=0.95 词表清空, 降级为 max_df=1.0")
        cv = CountVectorizer(
            tokenizer=_jieba_tokenizer,
            token_pattern=None,
            max_features=5000, min_df=1, max_df=1.0)
        dtm = cv.fit_transform(texts)
    lda = LatentDirichletAllocation(
        n_components=K, random_state=42,
        max_iter=50, learning_method='online', n_jobs=-1)
    theta = lda.fit_transform(dtm)
    logger.info(f"    LDA K={K}, perplexity={lda.perplexity(cv.transform(texts)):.1f}")

    # 计算 pairwise JSD (对称半矩阵)
    jsd_mat = np.zeros((n_banks, n_banks))
    for i in range(n_banks):
        for j in range(i + 1, n_banks):
            d = jensenshannon(theta[i], theta[j])  # sqrt(JSD) ∈ [0,1]
            jsd_mat[i, j] = jsd_mat[j, i] = d
    np.fill_diagonal(jsd_mat, np.nan)
    return jsd_mat, theta  # jsd_mat: distance ∈ [0,1]; theta: ndarray (n_banks, K) 主题分布


# ============================================================================
# 4. Embedding 相似度矩阵 (Dense Semantic Similarity) (Reimers & Gurevych 2019)
# 【术语】用预训练语言模型 (Sentence-BERT) 生成稠密语义向量，
#   计算 pairwise cosine similarity，作为 TF-IDF/LDA 的第三种稳健性检验。
# 【白话】第三种比较方法。用 AI 模型把文本变成"语义向量"，能理解
#   "移动支付"和"手机银行"意思很像（而 TF-IDF 只能看字面）。
#   这也是稳健性检验 (robustness check)，看不同方法结果是否一致。
# ============================================================================

async def _get_embeddings_api(texts, cache=None):
    """通过 API 获取文本 Embedding 向量 — 穿透式缓存与死战不退容错。"""
    import aiohttp
    texts = [] if texts is None else list(texts)
    if len(texts) == 0:
        return np.empty((0, 0), dtype=np.float32)

    models = LLM_CONFIG.get('models') or []
    cfg = models[0] if models else {}
    if EMBEDDING_CONFIG:
        base_url = EMBEDDING_CONFIG.get('base_url')
        api_key = EMBEDDING_CONFIG.get('api_key')
        embedding_model = EMBEDDING_CONFIG.get('model') or 'text-embedding-3-small'
    else:
        base_url = cfg.get('base_url')
        api_key = cfg.get('api_key')
        embedding_model = 'text-embedding-3-small'
    if not base_url or not api_key:
        raise RuntimeError('Embedding API config missing base_url or api_key')
    base_url = str(base_url).rstrip('/')
    # Plan-r3 P3-17 接入: embedding 缓存键的 prompt_version 维度.
    text_pipeline_version = EMBEDDING_CONFIG.get('text_pipeline_version', 'v0')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    cached_results = [
        cache.get(embedding_model, text, prompt_version=text_pipeline_version)
        if cache else None
        for text in texts
    ]
    missing_indices = [i for i, res in enumerate(cached_results) if res is None]
    missing_texts = [texts[i] for i in missing_indices]

    if len(texts) > 1:
        logger.info(f"    缓存拦截: 命中 {len(texts) - len(missing_texts)} 条, 缺失 {len(missing_texts)} 条")

    missing_embs = []
    if missing_texts:
        batches = []
        current_batch = []
        current_tokens = 0
        for text in missing_texts:
            n_tok = max(1, len(_EMB_ENCODING.encode(text)))
            if n_tok > _EMB_MAX_TOKENS:
                raise RuntimeError(f"Embedding 单条输入仍超限: {n_tok} > {_EMB_MAX_TOKENS}")

            if current_batch and (len(current_batch) >= 100 or current_tokens + n_tok > _EMB_MAX_TOKENS_PER_REQUEST):
                batches.append(current_batch)
                current_batch = []
                current_tokens = 0

            current_batch.append(text)
            current_tokens += n_tok

        if current_batch:
            batches.append(current_batch)

        if len(batches) > 1:
            logger.info(f"    网络请求: 动态分批为 {len(batches)} 批")

        async with aiohttp.ClientSession() as session:
            for batch_idx, batch in enumerate(batches):
                delay = RETRY_DELAY
                while True:
                    try:
                        async with session.post(
                            f"{base_url}/embeddings",
                            json={"model": embedding_model, "input": batch},
                            headers=headers,
                            timeout=aiohttp.ClientTimeout(total=180)
                        ) as resp:
                            status = resp.status
                            if status == 200:
                                data = await resp.json()
                                if 'data' not in data:
                                    raise ValueError(f"API 响应格式异常(缺少'data'): {str(data)[:200]}")
                                sorted_data = sorted(data['data'], key=lambda x: x.get('index', 0))
                                batch_embs = [d['embedding'] for d in sorted_data]
                                missing_embs.extend(batch_embs)
                                if cache:
                                    cache.put_batch(
                                        embedding_model,
                                        batch,
                                        [json.dumps(emb) for emb in batch_embs],
                                        prompt_version=text_pipeline_version,
                                    )
                                # v3.7.0 (C1 + M15 修复): LLM archive batch API
                                if _LLM_ARCHIVE_AVAILABLE:
                                    try:
                                        actual_version = data.get('model', embedding_model)
                                        api_endpoint = f"{base_url}/embeddings"
                                        records = [
                                            {
                                                'cache_key': LLMCache.make_key(
                                                    embedding_model, text,
                                                    prompt_version=text_pipeline_version,
                                                ),
                                                'model_id': embedding_model,
                                                'model_version': actual_version,
                                                'prompt': text,
                                                'response_raw': json.dumps({
                                                    'embedding': emb,
                                                    'batch_index': i,
                                                    'batch_total': len(batch_embs),
                                                    'batch_id': batch_idx,
                                                }, ensure_ascii=False),
                                                'prompt_version': text_pipeline_version,
                                                'temperature': 0.0,
                                                'api_endpoint': api_endpoint,
                                                'http_status': status,
                                            }
                                            for i, (text, emb) in enumerate(zip(batch, batch_embs))
                                        ]
                                        _get_archive().append_batch(records)
                                    except Exception as _arch_exc:
                                        logger.warning(
                                            f"    LLM archive (strategic_diff batch {batch_idx+1}) "
                                            f"失败 (不阻塞): {_arch_exc!r}"
                                        )
                                break
                            elif status in (429, 500, 502, 503, 504):
                                err_text = await resp.text()
                                logger.warning(f"    HTTP {status} (batch {batch_idx+1}): {err_text[:100]}。休眠 {delay} 秒后重试...")
                                await asyncio.sleep(delay)
                                delay = min(delay * 2, MAX_RETRY_DELAY)
                            else:
                                err_text = await resp.text()
                                raise ValueError(f"不可恢复的 API 错误 {status} (batch {batch_idx+1}): {err_text[:200]}")
                    except ValueError:
                        raise
                    except Exception as e:
                        logger.warning(f"    网络异常 (batch {batch_idx+1}): {type(e).__name__}: {e}。休眠 {delay} 秒后重试...")
                        await asyncio.sleep(delay)
                        delay = min(delay * 2, MAX_RETRY_DELAY)

    assert len(missing_embs) == len(missing_texts), f"返回数量异常: expected {len(missing_texts)}, got {len(missing_embs)}"
    final_embs = []
    missing_ptr = 0
    for res in cached_results:
        if res is not None:
            final_embs.append(json.loads(res))
        else:
            final_embs.append(missing_embs[missing_ptr])
            missing_ptr += 1

    return np.array(final_embs, dtype=np.float32)


def _embed_texts_with_chunk_pooling(texts, *, spec=None, log_prefix="Embedding"):
    """将任意长度文本嵌入为文本级向量 (2026-05-29: 委托 embedding_engine, spec 参数化)。

    超长文本走 Early Chunking + Mean Pooling。spec 默认主轨 (text-embedding-3-small);
    传 _ROBUSTNESS_SPEC 则走 text2vec 本地稳健轨。失败/形状异常 → None。

    Returns:
        np.ndarray | None: 文本级 Embedding 向量 (n_texts, dim)
    """
    db_path = CONFIG['paths'].get(
        'llm_cache_db',
        os.path.join(CONFIG['paths']['output_dir'], '_llm_cache.db'),
    )
    return _eng.embed_texts(
        texts,
        spec if spec is not None else EMBEDDING_CONFIG,
        cache_db_path=db_path,
        log_prefix=log_prefix,
    )


def _build_embedding_sim_matrix(texts, spec=None):
    """构建 Embedding cosine 相似度矩阵, 长文本分段池化 (spec 参数化双轨)。

    Returns:
        tuple: (sim, emb)
          - sim: np.ndarray | None, 相似度矩阵, 降级失败时返回 None
          - emb: np.ndarray | None, 文本级 Embedding 向量 (n_banks, dim)
            (供 centroid 计算复用)
    """
    emb = _embed_texts_with_chunk_pooling(texts, spec=spec, log_prefix="Embedding")
    if emb is None:
        return None, None

    sim = cosine_similarity(emb)
    np.fill_diagonal(sim, np.nan)
    return sim, emb  # sim: similarity ∈ [0,1]; emb: ndarray (n_banks, dim)


# ============================================================================
# 5. N-最近邻聚合 (N-Nearest Neighbor Aggregation) (Hoberg & Phillips 2016, §III.B)
# 【术语】实现 Guzman & Li (2023, MS, §3) 核心公式 Ŝ_i = (1/N)Σδ_ij，
#   对每家银行取其在文本空间中 N 个最近邻的平均距离作为战略差异度。
# 【白话】这是核心步驤！对每家银行，找到和它最像的 N 家同行，
#   然后看它与这 N 家同行的"平均距离"。
#   比喻: 就像在班级里找到和你成绩最接近的 5 个同学，
#   然后看你们的平均差距有多大 — 差距越大，说明你越"与众不同"。
# ============================================================================

def _compute_nn_scores(matrix, bank_list, N_list, is_distance=False):
    """N-最近邻差异度聚合 — 实现 Guzman & Li (2023) Section 3 核心公式。

    本函数直接实现论文中从相似度到战略差异度的转换规则:

        Ŝ_i = (1/N) Σ_{j ∈ J_i^N} δ_ij
        (Guzman & Li 2023, Management Science, §3 "From similarity to
         founding strategy")

    其中 δ_ij = 1 - cosine_similarity(v_i, v_j) 为文本距离,
    J_i^N 为银行 i 的 N 个最近邻 (文本空间中相似度最高的 N 家同行)。

    对于每家银行, 找到文本空间中最近的 N 个同行:
      - similarity 矩阵: 取最大 N 个, 差异度 = mean(1 - sim_topN) → Ŝ_i
      - distance 矩阵: 取最小 N 个, 差异度 = mean(dist_topN) → Ŝ_i

    N=5 为基准 (与论文一致), N=3,4,6,7 为敏感性检验。
    N 值敏感性检验的理论基础:
      Bresnahan, T. F., & Reiss, P. C. (1991). Entry and competition in
      concentrated markets. Journal of Political Economy, 99(5), 977–1009.
      https://doi.org/10.1086/261786

    Args:
        matrix: 相似度或距离矩阵 (n×n), 对角线为 NaN
        bank_list: 银行名称列表
        N_list: N 值列表 (如 [3,4,5,6,7])
        is_distance: True=距离矩阵, False=相似度矩阵

    Returns:
        dict: {f'n{N}': {bank: Ŝ_i}, 'sim_max': {bank: max_similarity}}
    """
    results = {f'n{N}': {} for N in N_list}
    results['sim_max'] = {}
    for i, bank in enumerate(bank_list):
        valid = matrix[i][~np.isnan(matrix[i])]
        if len(valid) == 0:
            for N in N_list:
                results[f'n{N}'][bank] = np.nan
            results['sim_max'][bank] = np.nan
            continue
        if is_distance:
            # 距离矩阵: 升序排列, 取最小 N 个 (LDA+JSD 路径)
            idx = np.argsort(valid)
            results['sim_max'][bank] = float(1.0 - valid[idx[0]])
            for N in N_list:
                k = min(N, len(valid))
                # Ŝ_i = mean(dist_topK), K = min(N, |peers|)
                results[f'n{N}'][bank] = float(np.mean(valid[idx[:k]]))
        else:
            # 相似度矩阵: 降序排列, 取最大 N 个
            # Guzman & Li (2023, §3): δ_ij = 1 - sim_ij → Ŝ_i = mean(δ_topN)
            idx = np.argsort(valid)[::-1]
            results['sim_max'][bank] = float(valid[idx[0]])
            for N in N_list:
                k = min(N, len(valid))
                # Ŝ_i = (1/k) Σ_{j ∈ J_i^k} (1 - sim_ij)
                results[f'n{N}'][bank] = float(np.mean(1.0 - valid[idx[:k]]))
    return results


# ============================================================================
# 5b. 全行业向量法 (Industry Centroid Distance) (谢佳松 2025, 经济研究, 图 1)
#
# ── 改进 B: 基于新闻主题余弦相似度构建"转型创新边界"指标 ──
#
# 【具体修改建议 (已实施)】
#   在阶段 25 (本模块) 的面板数据生成环节:
#     1. 汇总各银行年度的金融科技新闻文本 (含 Full 全文 / Ctx 上下文窗口),
#        通过 TF-IDF / LDA / Embedding 四轨方法生成主题向量;
#     2. 计算某银行 t 年主题向量与全行业总体主题向量 (industry centroid)
#        的余弦相似度 (Cosine Similarity);
#     3. 取 1 - 相似度 作为该银行的"战略差异度"或"创新边界拓展性"。
#
# 【论文依据】
#   谢佳松, 樊嘉诚, & 林建浩. (2025). 信息摩擦、公共数据与企业创新边界.
#     经济研究, (11).
#     参考论文图 1 及表 2: 利用 BERTopic 构建企业专利与公共数据的
#     主题余弦相似度, 以度量"技术布局引导"效应。
#
# 【预期的边际贡献 / 解决的内生性问题】
#   1. 完美复刻甚至超越了论文的 NLP 结构化变量构造方法:
#      - 论文用 BERTopic → 本项目用 TF-IDF/LDA/Embedding 四轨方法,
#        多维度交叉验证, 稳健性更强;
#   2. 避免了传统研究中仅用"词频统计"量化金融科技的问题:
#      - 词频无法区分"深度布局"与"浅层提及", 而余弦距离度量的是
#        向量空间中的结构性差异, 能精准刻画战略定位;
#   3. 提供了与 N-最近邻法 (Guzman & Li 2023, MS) 互补的量化视角:
#      - N-NN: "我与最像的几家同行有多不同" → niche distance
#      - Centroid: "我与行业平均水平有多不同" → average distance
#      - 两者的 Horse Race 回归可检验信息独立性;
#   4. Full/Ctx 双轨对比检验全文噪声对指标的影响,
#      增强学术论文稳健性检验的厚度。
#
# 【术语】计算每家银行文本向量与全行业质心 (centroid) 的余弦距离，
#   度量银行与"行业平均水平"的战略偏离程度。
# 【白话】把所有银行的向量取平均，得到"行业平均画像"。
#   然后看每家银行和这个"平均画像"有多不同。越不同 = 创新边界越大。
# ============================================================================

def _compute_centroid_scores(vectors, bank_list, is_sparse=False):
    """全行业向量法: 1 - CosineSim(bank_vec, industry_centroid)。

    ── 改进 B: 基于新闻主题余弦相似度构建"转型创新边界"指标 ──

    【具体实施】
      将各银行年度金融科技新闻文本 (Full 全文 / Ctx 上下文窗口) 通过
      TF-IDF / LDA / Embedding 四轨方法生成主题向量, 计算每家银行 t 年
      主题向量与全行业总体主题向量 (industry centroid) 的余弦相似度
      (Cosine Similarity), 取 1 - 相似度 作为"战略差异度"或"创新边界
      拓展性"。

    【学术依据】
      谢佳松, 樊嘉诚, & 林建浩. (2025). 信息摩擦、公共数据与企业创新边界.
        经济研究, (11).
        → 图 1 / 表 2: BERTopic 余弦相似度 → 技术布局引导效应
        本函数将此方法迁移至银行金融科技新闻场景: 计算每家银行的
        文本向量与全行业质心向量 (centroid) 的余弦距离。

    【白话】把所有银行的向量取平均, 得到"行业平均画像"。
      然后看每家银行和这个"平均画像"有多不同。越不同 = 创新边界越大。

    【边际贡献】
      1. 四轨方法 (TF-IDF char/word + LDA + Embedding) 交叉验证,
         比论文单一 BERTopic 稳健性更强;
      2. 余弦距离度量向量空间结构性差异, 克服词频统计的"Cheap Talk"偏差;
      3. 与 N-最近邻法互补 (可做 Horse Race 回归检验信息独立性);
      4. Full/Ctx 双轨对比增强稳健性检验厚度。

    与 N-最近邻法的区别:
      - N-NN (Guzman & Li 2023, MS, §3): Ŝ_i = mean(dist to N peers)
        → "我与最像我的几家同行有多不同" (niche distance)
      - Centroid (谢佳松 2025, 经济研究, 图 1): C_i = 1 - cos(vec_i, mean(all vecs))
        → "我与行业平均水平有多不同" (average distance)

    Args:
        vectors: (n_banks, dim) 向量矩阵 (稀疏或稠密)
        bank_list: 银行名称列表
        is_sparse: True 则使用稀疏矩阵操作

    Returns:
        dict: {bank: centroid_diff ∈ [0, 1]}

    References:
        谢佳松, 樊嘉诚, & 林建浩. (2025). 信息摩擦、公共数据与企业创新边界.
          经济研究, (11).
        Guzman, J., & Li, A. (2023). Measuring founding strategy.
          Management Science, 69(1), 101–118.
          https://doi.org/10.1287/mnsc.2022.4369
    """
    if is_sparse:
        # csr_matrix.mean(axis=0) 返回 np.matrix, 需转为 ndarray
        centroid = np.asarray(vectors.mean(axis=0))
    else:
        centroid = np.mean(vectors, axis=0, keepdims=True)
    sims = cosine_similarity(vectors, centroid).flatten()
    # clip 防止浮点误差导致超出 [0, 1]
    return {bank: float(np.clip(1.0 - sims[i], 0.0, 1.0))
            for i, bank in enumerate(bank_list)}

# ============================================================================
# 6. 产品市场流动性 (Product Market Fluidity) (Hoberg et al. 2014, JF, Eq.2)
# 【术语】Fluidity_i,t = cos(N_i,t, Σ_{j≠i}|N_j,t - N_j,t-1|)，衡量银行 i 当前
#   的文本位置与竞争对手 t 期与 t-1 期之间变化方向的一致性。
# 【白话】衡量竞争者是否正在向你的"领地"移动。
#   想象你开了一家奶茶店，如果别人也纷纷开始卖奶茶，那就是 Fluidity 高，
#   说明竞争加剧了。反之如果别人都在做咖啡，没人跟你抢奶茶生意，
#   那就是 Fluidity 低。
# ============================================================================

def _compute_fluidity(agg_df, mode='char'):
    """计算产品市场流动性指标。

    定义 (Hoberg et al. 2014, Eq. 2):
      Fluidity_i,t = cosine(N_i,t, Σ_{j≠i} |N_j,t - N_j,t-1|)

    直觉: 衡量银行 i 当前的文本"位置"与市场整体"变化方向"的一致性。
    高 Fluidity 意味着竞争对手正向银行 i 所在的文本空间移动。

    注意: 首年无前期数据, 返回 NaN。

    Args:
        agg_df: 聚合文本 DataFrame[target_bank, year, agg_text]
        mode: 'char' 或 'word'

    Returns:
        dict: {(bank, year): fluidity_score}
    """
    fluidity = {}
    for year in sorted(agg_df['year'].unique()):
        df_t = agg_df[agg_df['year'] == year]
        df_t1 = agg_df[agg_df['year'] == year - 1]
        if df_t1.empty:
            continue  # 首年无前期数据

        # min_df: 跨 t 和 t-1 合并后的文档池，动态调整
        # min_df=1: 与 _build_tfidf_sim_matrix 保持一致
        _mdf_flu = 1
        kw = (dict(analyzer='char_wb', ngram_range=(2, 4),
                   max_features=5000, min_df=_mdf_flu)
              if mode == 'char'
              else dict(tokenizer=_jieba_tokenizer,
                        token_pattern=None,
                        max_features=5000, min_df=_mdf_flu))
        try:
            vec = TfidfVectorizer(max_df=0.95, **kw).fit(
                pd.concat([df_t['agg_text'], df_t1['agg_text']]))
        except ValueError:
            logger.warning(f"    Fluidity {mode}: max_df=0.95 词表清空, 降级为 1.0")
            vec = TfidfVectorizer(max_df=1.0, **kw).fit(
                pd.concat([df_t['agg_text'], df_t1['agg_text']]))
        vt = _l2_normalize(vec.transform(df_t['agg_text'].values).toarray())
        vt1 = _l2_normalize(vec.transform(df_t1['agg_text'].values).toarray())

        # 建立 t-1 期银行索引映射
        t1_map = {b: i for i, b in enumerate(df_t1['target_bank'].values)}
        for i, bank in enumerate(df_t['target_bank'].values):
            # 计算市场变化向量: Σ_{j≠i} |N_j,t - N_j,t-1|
            change = np.zeros(vt.shape[1])
            for j, other in enumerate(df_t['target_bank'].values):
                if other != bank and other in t1_map:
                    change += np.abs(vt[j] - vt1[t1_map[other]])
            d = np.linalg.norm(vt[i]) * np.linalg.norm(change)
            fluidity[(bank, year)] = float(np.dot(vt[i], change) / d) if d > 0 else np.nan
    return fluidity


# ============================================================================
# 6b. 相邻期文本连贯性 (Temporal Text Coherence)
# 【术语】实现欧阳志刚 & 胡雯华 (2024, 数量经济技术经济研究, §三(三)2.(2)) 的
#   余弦相似度连贯性指标: 同一银行 t 期与 t-1 期聚合文本的高维特征相似度。
#   高连贯性 → 市场理解偏差小 → 不确定性降低 → 信息传导效率高。
# 【白话】看每家银行今年的新闻画像和去年有多像。越像 = 沟通越稳定一致,
#   市场越容易理解其意图。这是一个"连贯性"指标, 与情感分析正交。
#
# 学术参考:
#   欧阳志刚, 胡雯华. (2024). 央行沟通公告有助于提升政策利率的传导效率吗？
#     数量经济技术经济研究, 41(10), 69–88.
#     https://doi.org/10.13653/j.cnki.jqte.2024.10.004
#   Salton, G., & Buckley, C. (1988). Term-weighting approaches in automatic
#     text retrieval. Information Processing & Management, 24(5), 513–523.
#     https://doi.org/10.1016/0306-4573(88)90021-0
#   Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent Dirichlet
#     allocation. JMLR, 3(Jan), 993–1022.
#     https://www.jmlr.org/papers/v3/blei03a.html
#   Lin, J. (1991). Divergence measures based on the Shannon entropy.
#     IEEE Trans. Inform. Theory, 37(1), 145–151.
#     https://doi.org/10.1109/18.61115
# ============================================================================


def _compute_tfidf_coherence(agg_df, mode='char'):
    """计算同一银行相邻两期 (t, t-1) 聚合文本的 TF-IDF 余弦相似度。

    【学术】欧阳志刚 & 胡雯华 (2024, 数量经济技术经济研究, §三(三)2.(2)):
    "利用余弦相似度计算前后相邻两期文本的高维特征相似度,
    论证高相似度的文本能降低市场理解偏差（不确定性）。"

    TF-IDF 加权方案参见 Salton & Buckley (1988, IP&M);
    sublinear_tf=True 即 Manning et al. (2008, §6.4) 的 1+log(tf) 缩放,
    降低词频极端值对相似度的扭曲影响。

    【白话】对每家银行, 把今年和去年的"年度文本画像"分别转换成数字向量,
    然后算两个向量之间的"夹角余弦值"。值越接近1, 说明两年的新闻内容越像
    (沟通连贯); 值越接近0, 说明内容变化很大(沟通不连贯)。

    策略: 逐对年度 (t, t-1) 池化所有银行文本 fit TF-IDF,
    使 IDF 权重在共享词表空间中有区分力 (避免仅 2 文档时 IDF 退化为二值)。
    与 _compute_fluidity 同构, 但计算目标不同: fluidity = 竞争者变化,
    coherence = 自身连贯性。

    注意: 首年及年份间隙 (如 2018→2020 缺 2019) 返回缺失, 严格定义"相邻"为连续年度,
    与 strat_fluidity 处理方式一致。

    Args:
        agg_df: _aggregate_bank_year_texts 的输出 DataFrame[target_bank, year, agg_text]
        mode: 'char' (字符 n-gram, analyzer='char_wb', ngram 2-4) 或
              'word' (jieba 分词, 词级 TF-IDF)

    Returns:
        dict: {(bank, year): coherence ∈ [0,1]}, 首年/间隙年 → 缺失
    """
    coherence = {}
    # TF-IDF 参数与 _build_tfidf_sim_matrix 保持一致 (含 sublinear_tf=True)
    if mode == 'char':
        _kw = dict(analyzer='char_wb', ngram_range=(2, 4),
                   max_features=5000, min_df=1, sublinear_tf=True)
    else:
        _kw = dict(tokenizer=_jieba_tokenizer,
                   token_pattern=None,
                   max_features=5000, min_df=1, sublinear_tf=True)

    for year in sorted(agg_df['year'].unique()):
        df_t = agg_df[agg_df['year'] == year]
        df_t1 = agg_df[agg_df['year'] == year - 1]
        if df_t1.empty:
            continue  # 首年无前期数据 → 该年所有银行的连贯性为 NaN

        # 池化 t 和 t-1 所有银行文本 → fit TF-IDF (共享 IDF 权重空间)
        pooled_texts = pd.concat([df_t['agg_text'], df_t1['agg_text']],
                                  ignore_index=True)
        try:
            vec = TfidfVectorizer(max_df=0.95, **_kw).fit(pooled_texts)
        except ValueError:
            logger.warning(f"    Coherence TF-IDF {mode} {year}: "
                           f"max_df=0.95 词表清空, 降级为 max_df=1.0")
            vec = TfidfVectorizer(max_df=1.0, **_kw).fit(pooled_texts)

        vt = vec.transform(df_t['agg_text'].values)
        vt1 = vec.transform(df_t1['agg_text'].values)

        # 建立 t-1 期银行索引映射
        t1_map = {b: i for i, b in enumerate(df_t1['target_bank'].values)}
        for i, bank in enumerate(df_t['target_bank'].values):
            if bank in t1_map:
                # cosine_similarity 接受稀疏矩阵, 内部含 L2 归一化
                sim = cosine_similarity(vt[i:i+1], vt1[t1_map[bank]:t1_map[bank]+1])
                coherence[(bank, year)] = float(sim[0, 0])

    logger.info(f"    TF-IDF {mode} 连贯性: {len(coherence)} 个 Bank-Year 对")
    return coherence


def _compute_lda_coherence(agg_df):
    """LDA 主题模型 + Jensen-Shannon 散度的相邻期文本连贯性。

    【学术】Blei, Ng & Jordan (2003, JMLR) 的 LDA 提取文档主题分布 θ,
    然后用 Lin (1991, IEEE TIT) 的 Jensen-Shannon 散度衡量分布差异:
      coherence = 1 - JSD_distance(θ_{i,t}, θ_{i,t-1})
    其中 scipy.jensenshannon 返回 √JSD (JSD distance), ∈ [0,1] (log base 2)。
    因此 coherence = 1 - √JSD ∈ [0,1], 高值 = 主题分布接近 = 连贯。

    【白话】用主题模型把每篇"年度文本画像"概括成若干主题的比例组合
    (比如 30% 谈 AI, 40% 谈风控, 30% 谈支付), 然后比较同一银行今年和去年
    的主题比例是否接近。越接近 = 沟通越连贯。

    参数一致性: random_state=42, max_iter=50, learning_method='online',
    n_jobs=-1 (与 _build_lda_jsd_matrix 完全一致, 保证可复现性)。

    Args:
        agg_df: _aggregate_bank_year_texts 的输出

    Returns:
        dict: {(bank, year): coherence ∈ [0,1]}, 首年/间隙年 → 缺失
    """
    coherence = {}
    for year in sorted(agg_df['year'].unique()):
        df_t = agg_df[agg_df['year'] == year]
        df_t1 = agg_df[agg_df['year'] == year - 1]
        if df_t1.empty:
            continue

        n_t = len(df_t)
        all_texts = pd.concat([df_t['agg_text'], df_t1['agg_text']],
                               ignore_index=True).tolist()
        n_total = len(all_texts)
        K = max(10, n_total // 30)  # 主题数: 与 _build_lda_jsd_matrix 一致

        try:
            # CountVectorizer → DTM → LDA
            cv = CountVectorizer(tokenizer=_jieba_tokenizer,
                                 token_pattern=None,
                                 max_features=5000, min_df=1, max_df=0.95)
            try:
                dtm = cv.fit_transform(all_texts)
            except ValueError:
                cv = CountVectorizer(tokenizer=_jieba_tokenizer,
                                     token_pattern=None,
                                     max_features=5000, min_df=1, max_df=1.0)
                dtm = cv.fit_transform(all_texts)

            lda = LatentDirichletAllocation(
                n_components=K, random_state=42,
                max_iter=50, learning_method='online', n_jobs=-1)
            theta = lda.fit_transform(dtm)
            # theta[:n_t] 对应 df_t, theta[n_t:] 对应 df_t1

            t1_map = {b: idx + n_t for idx, b in
                      enumerate(df_t1['target_bank'].values)}
            for i, bank in enumerate(df_t['target_bank'].values):
                if bank in t1_map:
                    # jensenshannon 返回 √JSD ∈ [0,1] (Lin, 1991)
                    d = jensenshannon(theta[i], theta[t1_map[bank]])
                    coherence[(bank, year)] = float(1.0 - d)
        except Exception as e:
            logger.warning(f"    LDA 连贯性 {year}: {type(e).__name__}: {e}, 跳过")
            continue

    logger.info(f"    LDA+JSD 连贯性: {len(coherence)} 个 Bank-Year 对")
    return coherence


def _compute_emb_coherence(agg_df, spec=None):
    """稠密语义嵌入的相邻期文本连贯性 (spec 参数化双轨; 默认主轨)。

    【学术】使用预训练语言模型 (text2vec / OpenAI Embedding) 将文本映射到
    高维语义空间, 计算 cosine similarity。与 TF-IDF 的词袋假设不同,
    Embedding 捕获词序和上下文语义 (Guzman & Li 2023, Management Science)。

    【白话】让 AI "读懂" 每年的文本画像, 把理解结果变成一串数字(向量),
    然后比较今年和去年的"理解"有多接近。AI 比 TF-IDF 更"聪明",
    能理解同义词和上下文, 但计算更慢(需要调用 API)。

    效率: 一次性获取所有 Bank-Year 嵌入，长文本复用分段池化逻辑；
    避免逐对调用。三层降级: API → sentence-transformers → 返回空 dict。

    Args:
        agg_df: _aggregate_bank_year_texts 的输出

    Returns:
        dict: {(bank, year): coherence ∈ [0,1]}, 首年/间隙年 → 缺失
    """
    coherence = {}
    all_texts = agg_df['agg_text'].tolist()
    banks = agg_df['target_bank'].tolist()
    years = agg_df['year'].tolist()

    if not all_texts:
        return coherence

    emb = _embed_texts_with_chunk_pooling(
        all_texts, spec=spec, log_prefix="Embedding 连贯性")
    if emb is None:
        return coherence

    # 【审查加固】防范 API 静默丢弃文档导致向量与银行列表不对齐
    if len(emb) != len(banks):
        logger.warning(f"    Embedding 连贯性: 向量数量与文档数量不匹配 "
                       f"(expected {len(banks)}, got {len(emb)})，已降级跳过计算")
        return coherence

    # 建立 (bank, year) → row_index 映射
    emb_map = {(banks[i], years[i]): i for i in range(len(banks))}

    for i, (bank, year) in enumerate(zip(banks, years)):
        key_t1 = (bank, year - 1)
        if key_t1 in emb_map:
            sim = cosine_similarity(
                emb[i].reshape(1, -1),
                emb[emb_map[key_t1]].reshape(1, -1))
            coherence[(bank, year)] = float(sim[0, 0])

    logger.info(f"    Embedding 连贯性: {len(coherence)} 个 Bank-Year 对")
    return coherence


def _log_coherence_diagnostics(panel):
    """输出连贯性四方法相关矩阵 + 值域断言。

    【白话】连贯性的"质量检查"函数:
      1. 四种方法 (TF-IDF char/word, LDA, Embedding) 的结果是否大致一致
         — 如果四种方法都说某银行的沟通很连贯, 说明结论可靠
      2. 与情感变量 (llm_vote_tone_full) 相关性低 → 确认正交性
         — 连贯性衡量"稳定性", 情感衡量"内容", 二者应独立
      3. 所有分数是否在 [0,1] 范围内 — 超出说明计算有 Bug
    """
    # 四方法收敛效度 (Full 轨)
    coh_cols = [c for c in ['coh_tfidf_c_full', 'coh_tfidf_w_full',
                            'coh_lda_full', 'coh_emb_full']
                if c in panel.columns]
    if len(coh_cols) >= 2:
        logger.info(f"  连贯性四方法相关矩阵:\n"
                    f"{panel[coh_cols].corr().round(3).to_string()}")

    # 正交性验证: 与情感变量的相关系数 (期望 |r| < 0.3)
    tone_col = 'llm_vote_tone_full'
    if tone_col in panel.columns and len(coh_cols) >= 1:
        for cc in coh_cols:
            valid = panel[[cc, tone_col]].dropna()
            if len(valid) > 5:
                r = valid[cc].corr(valid[tone_col])
                logger.info(f"    {cc} ↔ {tone_col}: r = {r:.3f} "
                            f"({'✅ 正交' if abs(r) < 0.3 else '相关偏高'})")

    # 值域断言: 所有 coh_* 列 ∈ [0, 1] (含浮点误差容忍)
    for col in [c for c in panel.columns if c.startswith('coh_')]:
        v = panel[col].dropna()
        if len(v) > 0:
            assert (v >= -1e-10).all() and (v <= 1 + 1e-10).all(), \
                f"{col} 超出 [0,1] 值域: min={v.min():.6f}, max={v.max():.6f}"


# ============================================================================
# 7. 主入口 + 诊断 (Main Entry + Diagnostics)
# 【术语】编排全部 pipeline: 文本聚合 → 多方法距离矩阵 → NN 聚合 → Fluidity →
#   面板合并 + 收敛效度诊断 (convergent validity diagnostics)
# 【白话】下面是这个模块的"总指挥"，调用上面所有工具函数，
#   按顺序执行: 聚合文本 → 计算距离 → 找最近邻 → 算 Fluidity → 合并到面板
# ============================================================================

def compute_strategic_differentiation(df_exploded, panel):
    """计算金融科技战略差异度指数 (FinTech Strategic Differentiation Score)。

    改进 A: 构建基于文本距离的全新分析维度
    ─────────────────────────────────────
    论文依据:
      严格映射 Guzman & Li (2023, MS) Section 3 "From similarity to founding
      strategy" 中关于计算企业文本表述的余弦相似度并聚合至最近竞争者的规则:

          Ŝ_i = (1/N) Σ_{j ∈ J_i^N} δ_ij
          (N=5 为基准, N=3~7 为敏感性检验)

    边际贡献 / 解决的内生性问题:
      将所有银行当年的金融科技新闻文本聚合, 计算其与其他所有银行的
      TF-IDF (及 LDA+JSD / Embedding) 文本相似度。通过测度每家银行在
      向量空间中与其最近的几家同业的文本"距离", 揭示银行业金融科技
      创新的战略生态位。这解决了当前粗颗粒度加权方法 (单纯比拼新闻
      数量和情感得分) 所带来的内生性问题 — 数量和情感指标容易受银行
      规模、媒体关注度等混杂因素驱动, 而文本距离度量的是战略内容本身
      的差异性, 能更精准地分离出差异化战略所带来的超额边际贡献。

    处理流程:
      1. 按 (银行, 年度) 聚合新闻文本 → "企业产品描述"代理变量
      2. 逐年计算 4 种文本距离矩阵 (TF-IDF char/word, LDA+JSD, Embedding)
         → Hoberg & Phillips (2016, JPE, §III) 逐年重建方法
      3. N-最近邻聚合 → Ŝ_i (N=3,4,5,6,7 for TF-IDF; N=5 for LDA/Embedding)
      4. 全行业向量法 → 1 - cos(vec_i, centroid) (谢佳松 2025, 经济研究)
      5. 计算 Fluidity → Hoberg et al. (2014, JF, Eq. 2)
      6. Ctx 轨双轨对比 → 上下文窗口文本重跑 N-NN(N=5) + centroid
      7. 合并到面板并执行六方法收敛效度诊断

    Args:
        df_exploded: 文章-银行级 DataFrame
        panel: 银行-年面板 DataFrame

    Returns:
        panel: 新增 ~50 列战略差异度指标的面板 DataFrame
          (含 N-NN Full/Ctx, centroid Full/Ctx, fluidity, 连贯性,
           及 text2vec 稳健 twin 列 strat_diff_*_t2v / centroid_diff_emb_t2v / coh_emb_t2v / strat_diff_t2v_{full,ctx})
    """
    logger.info("=" * 60)
    logger.info("战略差异度指数 (Guzman & Li 2023; Hoberg & Phillips 2016)")
    logger.info("=" * 60)

    # 【白话】N_LIST = [3,4,5,6,7] 表示分别看最像的 3/4/5/6/7 家同行
    #   N=5 是论文推荐的基准值，其他是"换个数字看结果是否稳定"
    N_LIST = [3, 4, 5, 6, 7]
    # 第一步: 把所有新闻按 (银行, 年) 合并成"年度总结"大文档
    agg_df = _aggregate_bank_year_texts(df_exploded)
    all_results = []  # 用来收集所有年度、所有银行的计算结果

    # 【白话】逐年计算 — 每一年独立建模，不跨年混合
    #   这样做是因为金融科技领域变化很快，2020年的"热词"和2024年可能完全不同
    for year in sorted(agg_df['year'].unique()):
        dy = agg_df[agg_df['year'] == year]
        banks = dy['target_bank'].tolist()   # 这一年有哪些银行
        texts = dy['agg_text'].tolist()       # 每家银行的"年度总结"文本
        if len(banks) < 3:
            # 少于 3 家银行没法比较，跳过
            logger.warning(f"  年度={year}: 仅 {len(banks)} 家银行, 跳过 (最低要求 3)")
            continue
        logger.info(f"  年度={year}, 银行数={len(banks)}")

        # 方法 A: TF-IDF 字符级 — 看字符组合的相似度（不依赖分词）
        sim_c, vec_c = _build_tfidf_sim_matrix(texts, 'char')
        sc = _compute_nn_scores(sim_c, banks, N_LIST)
        # 全行业向量法 (谢佳松 2025, 经济研究, 图 1)
        cd_c = _compute_centroid_scores(vec_c, banks, is_sparse=True)
        # 方法 B: TF-IDF 词级 — 用 jieba 分词后比较（语义更精准）
        sim_w, vec_w = _build_tfidf_sim_matrix(texts, 'word')
        sw = _compute_nn_scores(sim_w, banks, N_LIST)
        cd_w = _compute_centroid_scores(vec_w, banks, is_sparse=True)
        # 方法 C: LDA + JSD — 比较"主题分布"的差异（稳健性检验）
        try:
            jsd_mat, theta = _build_lda_jsd_matrix(texts, len(banks))
            sl = _compute_nn_scores(jsd_mat, banks, [5], is_distance=True)
            cd_lda = _compute_centroid_scores(theta, banks)
        except Exception as e:
            logger.warning(f"    LDA+JSD 失败 ({type(e).__name__}), 跳过")
            sl = None
            cd_lda = None
        # 方法 D: Embedding (主轨) — text-embedding-3-small 语义距离
        se_mat, se_emb = _build_embedding_sim_matrix(texts)
        if se_mat is not None:
            se = _compute_nn_scores(se_mat, banks, [5])
            cd_emb = _compute_centroid_scores(se_emb, banks)
        else:
            se, cd_emb = None, None
        # 方法 D-t2v: 稳健 twin — text2vec 本地模型 (2026-05-29 双模型, 同算法只换模型)
        se_mat_t2v, se_emb_t2v = _build_embedding_sim_matrix(
            texts, spec=_ROBUSTNESS_SPEC)
        if se_mat_t2v is not None:
            se_t2v = _compute_nn_scores(se_mat_t2v, banks, [5])
            cd_emb_t2v = _compute_centroid_scores(se_emb_t2v, banks)
        else:
            se_t2v, cd_emb_t2v = None, None

        # 【白话】把这一年每家银行的计算结果打包成一行行数据
        #   每一行 = 一家银行在这一年的所有差异度分数
        for bank in banks:
            row = {'target_bank': bank, 'year': year}
            for N in N_LIST:
                # strat_diff_n5 = 和最像的5家同行的平均"距离"（字符级）
                row[f'strat_diff_n{N}'] = sc[f'n{N}'][bank]
                # strat_diff_n5_w = 同上，但用词级方法（稳健性）
                row[f'strat_diff_n{N}_w'] = sw[f'n{N}'][bank]
            # strat_sim_max = 和最像的那一家同行的相似度
            row['strat_sim_max'] = sc['sim_max'][bank]
            row['strat_sim_max_w'] = sw['sim_max'][bank]
            if sl:  # LDA 方法成功时才有
                row['strat_diff_n5_lda'] = sl['n5'].get(bank, np.nan)
                row['strat_sim_max_lda'] = sl['sim_max'].get(bank, np.nan)
            if se:  # Embedding 方法成功时才有
                row['strat_diff_n5_emb'] = se['n5'].get(bank, np.nan)
                row['strat_sim_max_emb'] = se['sim_max'].get(bank, np.nan)
            if se_t2v:  # 稳健 twin (text2vec)
                row['strat_diff_n5_emb_t2v'] = se_t2v['n5'].get(bank, np.nan)
                row['strat_sim_max_emb_t2v'] = se_t2v['sim_max'].get(bank, np.nan)
            # 全行业向量法 Full 轨 (谢佳松 2025, 经济研究, 图1/表2)
            row['centroid_diff_tfidf_c'] = cd_c[bank]
            row['centroid_diff_tfidf_w'] = cd_w[bank]
            if cd_lda:
                row['centroid_diff_lda'] = cd_lda.get(bank, np.nan)
            if cd_emb:
                row['centroid_diff_emb'] = cd_emb.get(bank, np.nan)
            if cd_emb_t2v:  # 稳健 twin + 契约别名 strat_diff_t2v_full (保留 stage 30 旧列名)
                row['centroid_diff_emb_t2v'] = cd_emb_t2v.get(bank, np.nan)
                row['strat_diff_t2v_full'] = cd_emb_t2v.get(bank, np.nan)
            all_results.append(row)

    # 【白话】Fluidity: 衡量竞争者是否在向你的"领地"移动
    #   char/word 双模式 = 用两种不同的文本分析方法各算一遍
    flu_c = _compute_fluidity(agg_df, 'char')
    flu_w = _compute_fluidity(agg_df, 'word')

    # 【白话】最终组装: 把所有计算结果合并到面板数据里
    #   面板(panel) = 每行是一家银行的一年，这里把差异度分数填进去
    if all_results:
        res = pd.DataFrame(all_results)
        # 把 Fluidity 分数也加上
        res['strat_fluidity'] = res.apply(
            lambda r: flu_c.get((r['target_bank'], r['year']), np.nan), axis=1)
        res['strat_fluidity_w'] = res.apply(
            lambda r: flu_w.get((r['target_bank'], r['year']), np.nan), axis=1)
        # 用银行名+年份做"钥匙"，把新列合并到面板
        panel = panel.merge(res, on=['target_bank', 'year'], how='left')
        # 跑诊断: 检查四种方法的结果是否大致一致（收敛效度）
        _log_robustness_diagnostics(panel)
        logger.info(f"  ✅ 战略差异度: 成功合并 {len(res)} 行, "
                    f"新增 {len(res.columns) - 2} 列")
    else:
        logger.warning("  无有效结果 (所有年度银行数不足 3)")

    # ══════════════════════════════════════════════════════════════════
    # 改进 B: 相邻期文本连贯性 (欧阳志刚 & 胡雯华 2024)
    # ══════════════════════════════════════════════════════════════════
    # 【学术】欧阳志刚 & 胡雯华 (2024, 数量经济技术经济研究, §三(三)2.(2)):
    #   余弦相似度 → 连贯性 → 降低不确定性 → 提升传导效率
    # 【白话】看每家银行今年和去年的新闻有多像, 越像说明沟通越稳定
    logger.info("=" * 60)
    logger.info("相邻期文本连贯性 (欧阳志刚 & 胡雯华 2024)")
    logger.info("=" * 60)

    # Full 轨: 复用本函数顶部已生成的 agg_df (避免冗余聚合)
    # Ctx 轨: 新建聚合 (使用 content_ctx 列)
    tracks = [('_full', agg_df)]
    if 'content_ctx' in df_exploded.columns:
        agg_ctx = _aggregate_bank_year_texts(df_exploded, text_col='content_ctx')
        tracks.append(('_ctx', agg_ctx))
    else:
        logger.warning("  连贯性 _ctx: 列 'content_ctx' 不存在, 跳过 Ctx 轨道")

    for track_suffix, agg_track in tracks:
        if agg_track.empty:
            continue
        logger.info(f"  轨道{track_suffix}: {len(agg_track)} 个 Bank-Year 文档")

        coh_tc  = _compute_tfidf_coherence(agg_track, 'char')
        coh_tw  = _compute_tfidf_coherence(agg_track, 'word')
        coh_lda = _compute_lda_coherence(agg_track)
        coh_emb = _compute_emb_coherence(agg_track)
        coh_emb_t2v = _compute_emb_coherence(agg_track, spec=_ROBUSTNESS_SPEC)  # 稳健 twin

        for name, coh_dict in [
            (f'coh_tfidf_c{track_suffix}', coh_tc),
            (f'coh_tfidf_w{track_suffix}', coh_tw),
            (f'coh_lda{track_suffix}',     coh_lda),
            (f'coh_emb{track_suffix}',     coh_emb),
            (f'coh_emb_t2v{track_suffix}', coh_emb_t2v),
        ]:
            # d=coh_dict: 默认参数绑定避免 Python 闭包延迟绑定陷阱 (审阅问题 9)
            panel[name] = panel.apply(
                lambda r, d=coh_dict: d.get(
                    (r['target_bank'], r['year']), np.nan),
                axis=1)

    _log_coherence_diagnostics(panel)
    coh_count = sum(1 for c in panel.columns if c.startswith('coh_'))
    logger.info(f"  ✅ 文本连贯性: 新增 {coh_count} 列")

    # ══════════════════════════════════════════════════════════════════
    # 改进 C: Ctx 轨 N-最近邻差异度 + 全行业向量法
    # ══════════════════════════════════════════════════════════════════
    # 【学术】Ctx 轨使用上下文窗口文本 (content_ctx) 聚合,
    #   排除与银行无关的通用报道段落, 信噪比更高。
    #   双轨对比可检验全文噪声对差异度指标的影响。
    # 【白话】Full 轨用完整新闻, Ctx 轨只用提到银行名字附近的段落。
    #   N-NN 仅跑 N=5 (不展开 N=3~7, N 敏感性已由 Full 轨覆盖)。
    logger.info("=" * 60)
    logger.info("Ctx 轨: N-最近邻 + 全行业向量法")
    logger.info("=" * 60)

    if 'content_ctx' in df_exploded.columns:
        agg_ctx_sd = _aggregate_bank_year_texts(
            df_exploded, text_col='content_ctx')
        ctx_results = []

        for year in sorted(agg_ctx_sd['year'].unique()):
            dy = agg_ctx_sd[agg_ctx_sd['year'] == year]
            banks = dy['target_bank'].tolist()
            texts = dy['agg_text'].tolist()
            if len(banks) < 3:
                continue

            # N-NN (N=5 only) + centroid, 四方法
            sim_c, vec_c = _build_tfidf_sim_matrix(texts, 'char')
            sc = _compute_nn_scores(sim_c, banks, [5])
            cd_c = _compute_centroid_scores(vec_c, banks, is_sparse=True)

            sim_w, vec_w = _build_tfidf_sim_matrix(texts, 'word')
            sw = _compute_nn_scores(sim_w, banks, [5])
            cd_w = _compute_centroid_scores(vec_w, banks, is_sparse=True)

            try:
                jsd_mat, theta = _build_lda_jsd_matrix(texts, len(banks))
                sl = _compute_nn_scores(jsd_mat, banks, [5],
                                         is_distance=True)
                cd_lda = _compute_centroid_scores(theta, banks)
            except Exception:
                sl, cd_lda = None, None

            se_mat, se_emb = _build_embedding_sim_matrix(texts)
            if se_mat is not None:
                se = _compute_nn_scores(se_mat, banks, [5])
                cd_emb = _compute_centroid_scores(se_emb, banks)
            else:
                se, cd_emb = None, None
            # 稳健 twin (text2vec, 2026-05-29 双模型)
            se_mat_t2v, se_emb_t2v = _build_embedding_sim_matrix(
                texts, spec=_ROBUSTNESS_SPEC)
            if se_mat_t2v is not None:
                se_t2v = _compute_nn_scores(se_mat_t2v, banks, [5])
                cd_emb_t2v = _compute_centroid_scores(se_emb_t2v, banks)
            else:
                se_t2v, cd_emb_t2v = None, None

            for bank in banks:
                row = {'target_bank': bank, 'year': year}
                # N-NN Ctx 轨 (N=5)
                row['strat_diff_n5_ctx'] = sc['n5'][bank]
                row['strat_diff_n5_w_ctx'] = sw['n5'][bank]
                row['strat_sim_max_ctx'] = sc['sim_max'][bank]
                row['strat_sim_max_w_ctx'] = sw['sim_max'][bank]
                if sl:
                    row['strat_diff_n5_lda_ctx'] = sl['n5'].get(bank, np.nan)
                    row['strat_sim_max_lda_ctx'] = sl['sim_max'].get(bank, np.nan)
                if se:
                    row['strat_diff_n5_emb_ctx'] = se['n5'].get(bank, np.nan)
                    row['strat_sim_max_emb_ctx'] = se['sim_max'].get(bank, np.nan)
                if se_t2v:  # 稳健 twin (text2vec)
                    row['strat_diff_n5_emb_t2v_ctx'] = se_t2v['n5'].get(bank, np.nan)
                    row['strat_sim_max_emb_t2v_ctx'] = se_t2v['sim_max'].get(bank, np.nan)
                # Centroid Ctx 轨
                row['centroid_diff_tfidf_c_ctx'] = cd_c[bank]
                row['centroid_diff_tfidf_w_ctx'] = cd_w[bank]
                if cd_lda:
                    row['centroid_diff_lda_ctx'] = cd_lda.get(bank, np.nan)
                if cd_emb:
                    row['centroid_diff_emb_ctx'] = cd_emb.get(bank, np.nan)
                if cd_emb_t2v:  # 稳健 twin + 契约别名 strat_diff_t2v_ctx
                    row['centroid_diff_emb_t2v_ctx'] = cd_emb_t2v.get(bank, np.nan)
                    row['strat_diff_t2v_ctx'] = cd_emb_t2v.get(bank, np.nan)
                ctx_results.append(row)

        if ctx_results:
            ctx_df = pd.DataFrame(ctx_results)
            panel = panel.merge(ctx_df, on=['target_bank', 'year'],
                                how='left')
            logger.info(f"  ✅ Ctx 轨: {len(ctx_df)} 行, "
                        f"{len(ctx_df.columns) - 2} 列")
        else:
            logger.warning("  Ctx 轨: 无有效结果")
    else:
        logger.warning("  Ctx 轨: 列 'content_ctx' 不存在, 跳过")

    # ── 双模型契约保证 (F2 fix 2026-05-30) ──
    # strat_diff_t2v_{full,ctx} 是 export.py::REQUIRED_PANEL_COLUMNS 硬要求列
    # (stage 30 退役后 stage 25 是其唯一来源)。上面 `if cd_emb_t2v` 仅在
    # ROBUSTNESS (text2vec) 嵌入成功时建列; 若本地模型加载失败 / 某年银行不足 /
    # content_ctx 缺失, 该列不会出现 → 下游 export_panel 抛 RuntimeError。与
    # stage 15 (policy_alignment) / stage 26 (policy_similarity) 的 NaN 降级对称,
    # 这里兜底保证两列恒存在 (失败即全 NaN, 不破坏 canonical 主轨)。
    for _contract_col in ('strat_diff_t2v_full', 'strat_diff_t2v_ctx'):
        if _contract_col not in panel.columns:
            panel[_contract_col] = np.nan

    return panel


def _log_robustness_diagnostics(panel):
    """输出六方法相关矩阵 + 值域断言。

    【白话】这是"质量检查"函数，做两件事：
      1. 看六种方法（TF-IDF字符/词级、LDA、Embedding + centroid 字符/Embedding）
         算出来的分数是否大致一致 — 如果都说某银行很独特，说明结果可靠
      2. 检查所有 strat_* 和 centroid_* 分数是否在 0~1 之间 — 超出范围说明有 Bug
    """
    cols = [c for c in ['strat_diff_n5', 'strat_diff_n5_w',
                        'strat_diff_n5_lda', 'strat_diff_n5_emb',
                        'centroid_diff_tfidf_c', 'centroid_diff_emb']
            if c in panel.columns]
    if len(cols) >= 2:
        logger.info(f"  六方法相关矩阵:\n{panel[cols].corr().round(3).to_string()}")

    # 值域断言: 所有 strat_* / centroid_* 列 ∈ [0, 1] (含浮点误差容忍)
    for col in [c for c in panel.columns
                if c.startswith('strat_') or c.startswith('centroid_')]:
        v = panel[col].dropna()
        if len(v) > 0:
            assert (v >= -1e-10).all() and (v <= 1 + 1e-10).all(), \
                f"{col} 超出 [0,1] 值域: min={v.min():.6f}, max={v.max():.6f}"
