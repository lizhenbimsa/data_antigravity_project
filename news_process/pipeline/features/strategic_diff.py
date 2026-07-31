"""
25_strategic_differentiation.py — 金融科技战略差异度指数
=======================================================

改进 A: 构建基于文本距离的"金融科技战略差异度指数"
      (FinTech Strategic Differentiation Score)

论文依据 (核心公式映射):
  严格映射 Guzman & Li (2023, MS) Section 3 "From similarity to founding
  strategy" 中关于计算企业文本表述的余弦相似度并聚合至最近竞争者的规则:

      Ŝ_i = (1/N) Σ_{j ∈ J_i^N} δ_ij
      (Guzman & Li 2023, MS, Eq. in §3; 本模块 N=5 为基准, N∈{3,4,6,7}∪{10,20,30,40,50} 为敏感性检验)

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
  3. 对每家银行取 N-最近邻 (N∈{3,4,5,6,7,10,20,30,40,50}) 的平均距离作为差异度指标 → Ŝ_i
  4. 计算全行业向量法 (centroid distance) 度量与行业平均的差异
  5. 计算 Fluidity (市场流动性) 衡量竞争环境变化速度
  6. Full/Ctx/Ss 三轨对比: 检验全文 vs 上下文窗口 vs 银行+金科同句共现文本的
     指标稳健性 (三轨互为稳健性, 归因窗口逐级收紧)

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
    [DOI 未在 chndoi.org 注册, 经 Crossref/DataCite/doi.org 均 404; 文献本身经
     WebSearch 佐证存在 (欧阳志刚 & 胡雯华 2024 央行沟通研究), 但 DOI 链接待核验]
  - 句向量表征: Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence
    embeddings using Siamese BERT-networks. Proceedings of EMNLP 2019,
    3980-3990. https://doi.org/10.18653/v1/D19-1410
  - LDA 主题模型: Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent
    Dirichlet allocation. Journal of Machine Learning Research, 3, 993–1022.
    https://www.jmlr.org/papers/v3/blei03a.html
  - 文本数据方法论: Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as
    data. Journal of Economic Literature, 57(3), 535–574.
    https://doi.org/10.1257/jel.20181020
  - [新增] 全行业向量法: 谢佳松, 樊嘉诚, & 林建浩. (2025). 信息摩擦、公共数据
    与企业创新边界. 经济研究, (11).
    → 图 1: BERTopic 余弦相似度 → 技术布局引导, 本模块迁移为行业质心距离

输出列 (~125 列; 含 co-primary _lg (text-embedding-3-large) 嵌入 twin 列)。
top-k N 扩展 (fix topk-n-expansion, 2026-07-02): 下列所有 N-最近邻差异度列 (strat_diff_n5*)
  自 2026-07-02 起**均另有 N∈{10,20,30,40,50} 大邻域孪生** (_TOPK_NN, 全方法 TF-IDF char/word ·
  LDA · Embedding Qwen · Embedding large _lg × 全轨 full/ctx/ss; 净增 ~75 列), 与 n5 互为稳健性、
  不分主次。下方列清单为省略计仍以 n5/n{3..7} 示例, 实际含各 N。
口径披露 (fix inject-fintech-word-lda, 2026-06-21): **全部 word 级 TF-IDF 列 (*_w) 与全部 LDA 列
(*_lda) 自 2026-06-21 起改用注入全量金科词典 (2026-07-21 起 607 词) 的独立分词器** (见 _get_diff_tokenizer), 领域复合词
(金融科技/区块链 等) 整词保留, 与 char 轨 (char_wb)/embedding 轨领域感知口径一致; char/emb 列字节不变。
值域口径 (fix(omni-g-strategic-02/03), 2026-06-11): TF-IDF/LDA 轨 (非负向量/分布)
∈ [0,1]; **Embedding 轨余弦真值域 [-1,1]** → 相似度列 (strat_sim_max_emb*, coh_emb*)
∈ [-1,1], 距离列 (strat_diff_*_emb*, centroid_diff_emb*, strat_diff_lg_*) ∈ [0,2]
(此前对 emb 轨统一 clip [0,1] 属值域删失, 负余弦被地板到 0):
  --- N-最近邻 Full 轨 (~43 列; N∈{3,4,5,6,7}∪_TOPK_NN for char/word, {5}∪_TOPK_NN for lda/emb/lg) ---
  strat_diff_n{3..7,10..50}       TF-IDF char N-近邻差异度 (Ŝ_i)
  strat_diff_n{3..7,10..50}_w     TF-IDF jieba 词级 N-近邻差异度 (稳健性检验)
  strat_sim_max / _w       最大同行相似度 (max cosine sim to any peer)
  strat_fluidity / _w      市场流动性 (Hoberg et al. 2014, Eq. 2)
  strat_diff_n5_lda        LDA+JSD N=5 差异度 (主题分布距离, 稳健性检验)
  strat_sim_max_lda        LDA+JSD 最大同行相似度
  strat_diff_n5_emb        Embedding N=5 差异度 (稠密语义距离, 稳健性检验)
  strat_sim_max_emb        Embedding 最大同行相似度
  --- N-最近邻 Ctx 轨 (~48 列; 五方法各 N∈{5}∪_TOPK_NN) ---
  strat_diff_n5_ctx / _w_ctx    TF-IDF char/word Ctx 轨 N=5 差异度
  strat_sim_max_ctx / _w_ctx    TF-IDF char/word Ctx 轨最大同行相似度
  strat_diff_n5_lda_ctx         LDA+JSD Ctx 轨 N=5 差异度
  strat_sim_max_lda_ctx         LDA+JSD Ctx 轨最大同行相似度
  strat_diff_n5_emb_ctx         Embedding Ctx 轨 N=5 差异度
  strat_sim_max_emb_ctx         Embedding Ctx 轨最大同行相似度
  --- N-最近邻 Ss 轨 (~48 列; 五方法各 N∈{5}∪_TOPK_NN; 银行+金科同句共现, 镜像 Ctx 轨) ---
  strat_diff_n5_ss / _w_ss      TF-IDF char/word Ss 轨 N=5 差异度
  strat_sim_max_ss / _w_ss      TF-IDF char/word Ss 轨最大同行相似度
  strat_diff_n5_lda_ss          LDA+JSD Ss 轨 N=5 差异度
  strat_sim_max_lda_ss          LDA+JSD Ss 轨最大同行相似度
  strat_diff_n5_emb_ss          Embedding Ss 轨 N=5 差异度
  strat_sim_max_emb_ss          Embedding Ss 轨最大同行相似度
  --- 全行业向量法 (谢佳松 2025; 三轨 full/ctx/ss) ---
  centroid_diff_tfidf_c / _w     TF-IDF char/word Full 轨 centroid 距离
  centroid_diff_lda              LDA θ Full 轨 centroid 距离
  centroid_diff_emb              Embedding Full 轨 centroid 距离
  centroid_diff_tfidf_c_ctx / _w_ctx  TF-IDF Ctx 轨 centroid 距离
  centroid_diff_lda_ctx          LDA θ Ctx 轨 centroid 距离
  centroid_diff_emb_ctx          Embedding Ctx 轨 centroid 距离
  centroid_diff_tfidf_c_ss / _w_ss   TF-IDF Ss 轨 centroid 距离 (银行+金科同句)
  centroid_diff_lda_ss           LDA θ Ss 轨 centroid 距离
  centroid_diff_emb_ss           Embedding Ss 轨 centroid 距离
  --- 相邻期文本连贯性 (欧阳志刚 & 胡雯华 2024; 三轨 full/ctx/ss) ---
  coh_tfidf_c_{full|ctx|ss}   TF-IDF char 相邻期文本连贯性
  coh_tfidf_w_{full|ctx|ss}   TF-IDF jieba 相邻期文本连贯性 (稳健性检验)
  coh_lda_{full|ctx|ss}       LDA+JSD 相邻期文本连贯性 (稳健性检验)
  coh_emb_{full|ctx|ss}       Embedding 相邻期文本连贯性 (稳健性检验)
  --- co-primary _lg 嵌入 twin 列 (text-embedding-3-large API; v3.14.0 起 ACTIVE) ---
  strat_diff_n5_emb_lg{,_ctx,_ss}     _lg N=5 Embedding 差异度
  strat_sim_max_emb_lg{,_ctx,_ss}     _lg Embedding 最大同行相似度
  centroid_diff_emb_lg{,_ctx,_ss}     _lg Embedding centroid 距离
  strat_diff_lg_{full,ctx,ss}     契约别名: = centroid_diff_emb_lg 的逐值别名
                                  (**centroid 构念**, 谢佳松 2025), 非 Guzman-Li
                                  N-NN 构念 — N-NN 的 _lg 孪生是 strat_diff_n5_emb_lg,
                                  稳健配对勿错配
  coh_emb_lg_{full,ctx,ss}        _lg Embedding 相邻期连贯性

注意: 连贯性变量 (coh_*) 对首年及年份间隙返回 NaN (与 strat_fluidity 一致),
      严格定义"相邻期"为连续年度 (year_t 与 year_{t-1})。

局限性:
  1. 原始文献 (Hoberg & Phillips 2016) 使用企业自有 10-K 披露文本,
     本项目使用第三方新闻报道, 测量的是"媒体感知差异"而非"自我披露差异"
  2. 银行样本量 (~54 家/年) 远小于 TNIC 数据集 (~5000 家/年),
     N=5 近邻占样本比例 ~10%, 需注意小样本偏差
  3. Embedding 长文本采用 token 分段 + 均值池化, 避免超长文本尾部语义被截断。
     主轨 (Qwen) 与 co-primary _lg (text-embedding-3-large) 均走 API 分段池化。
  4. 共提及文章机械相似 (披露, omni-g-strategic-01/09, 2026-06-11): full 轨中
     一篇共提 n 家银行的文章会逐字进入每家被提银行的年度聚合文档 (HP2016/GL2023
     的企业自撰文本互斥, 无此问题) → 共同被报道的银行对之间产生与战略无关的
     机械相似, N-NN 最近邻部分被共享语料而非战略邻居驱动 (试跑盘上 13.8% 展开行
     为跨银行逐字重复, 5/118 bank-year 文档 100% 由共享文章构成)。缓解:
     (a) 同行年内重复全文已 content 去重 (默认开, 见 _aggregate_bank_year_texts);
     (b) ctx 轨文本为 bank-specific 实体窗口, 跨银行逐字共享天然弱;
     (c) 稳健开关 strategic_diff.co_mention_downweight 按 1/n_banks 降权
         (句子级 round-robin 均分, 跨银行零逐字重叠)。
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
import logging
import os
import re
import sys
import threading

import jieba
import numpy as np
import pandas as pd

jieba.setLogLevel(logging.WARNING)

import tiktoken
from scipy.spatial.distance import jensenshannon
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── F26 (2026-07-27): LDA fit 段的 BLAS 线程钉死 ────────────────────────────
# **实测事实 (2026-07-27 真数据探针, 2007-2011, 503 个 bank-year 超级文档)**:
#   同一个 `_compute_lda_coherence`, BLAS 线程不钉 = **775.2s**, 钉到 1 = **140.0s**
#   —— 快 **5.5×**。sklearn LDA 的 online E-step 是大量小矩阵运算, 多线程 BLAS 的
#   同步开销远超收益 (典型过度订阅)。
# **更要紧的是确定性**: 同一探针证明, 不钉线程时并行臂与串行臂 **265/277 个值位模式
#   不同** (相对误差 ~1e-13); 钉到 1 后 **277/277 逐位相同**。也就是说 —— 现状下
#   `coh_lda*` / `strat_diff_n*_lda` / `centroid_diff_lda` 的数值**本就依赖运行机器的
#   BLAS 线程数**, 而 fix(omni-g-strategic-16, 2026-06-11) 当初把 `n_jobs=-1` 改成 1
#   正是为了消除这类核数依赖 —— 那次修复只堵了 sklearn 自身的 E-step 切片, 没堵住
#   底层 BLAS, 留了半个口子。
# **本修复**: 在 LDA fit 现场显式 `threadpool_limits(1)`, 使其**与环境无关**地取
#   CLAUDE.md 既定 golden 重生协议 (全 BLAS 线程钉 1) 下的那个值。
# ⚠ **这是改数动作** (量级 ~1e-13): 未钉线程的旧跑与本版会有末位差异, 方向是**向
#   canonical 靠拢**, 非引入新噪声。受影响列族: coh_lda{,_ctx,_ss} /
#   strat_diff_n*_lda{,_ctx,_ss} / strat_sim_max_lda* / centroid_diff_lda*。
try:
    from threadpoolctl import threadpool_limits as _threadpool_limits
except ImportError:      # threadpoolctl 是 sklearn 依赖; 极端裸环境缺失则退化为无操作
    from contextlib import nullcontext as _nullcontext

    def _threadpool_limits(limits=None, user_api=None):
        return _nullcontext()

# Phase 5c-1: 注入项目根, 让 ``news_process.core.*`` 在包模式下可解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.pipeline.text import embedding_engine as _eng

# v3.7.0 (DC3 + C1 + M13 修复): LLM raw response archive 集成 (V4 F-P2.1 critical)
# R1-R5 audit fix A5 (2026-05-27): V4 F-P2.1 仅承诺 stage 21 (tone_llms) + stage 48
# (llm_peer_iv) 接入, 此 import 是 strategic_diff stage 27c embedding LLM 调用的
# **前瞻性留位**, 当前 0 call site 是已知设计 (并非虚假声明). 未来若 stage 27c
# 真接入 LLM-based embedding archive (当前 embedding 经统一 API 引擎 _eng.embed_texts,
# v3.14.0 起已无 sentence-transformers 本地轨) 时再补 call.
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
        "(经统一引擎 API 嵌入, 无 LLM raw response 需归档).",
        _archive_import_exc,
    )

# Embedding Token 级精确截断与分段 (统一 Stage 15 标准)
# 【术语】cl100k_base 编码 (历史上是 text-embedding-3-small 编码器, 现作 Qwen/large 嵌入的保守 token 代理)，单条上限 8,191 tokens
#   对超过上限的文本 (如权威政策语料)，采用朴素分段 (naive / independent
#   chunking) + Mean Pooling 策略 (Reimers & Gurevych, 2019,
#   EMNLP, DOI: 10.18653/v1/D19-1410)，分段嵌入后均值池化为单个向量。
# 【白话】用 AI 模型同款的"令牌计数器"来精确控制文本长度，
#   短文本正常处理，超长文本切段后取平均，保留完整语义。
_EMB_ENCODING = tiktoken.get_encoding("cl100k_base")
_EMB_MAX_TOKENS = 8191
_EMB_MAX_TOKENS_PER_REQUEST = 250_000

# 嵌入重试已集中在 embedding_engine (2026-06-26 全项目统一固定 10s 间隔); 本模块经
# _eng.embed_texts 委托嵌入, 不再自带重试常量 (原 RETRY_DELAY/MAX_RETRY_DELAY 为死常量)。


def _coerce_positive_int(value, default: int) -> int:
    """配置兜底: 将 token 上限解析为正整数，异常时回退到安全默认值。"""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


def _split_text_for_embedding(text: str) -> list[str]:
    """按 token 粒度切分超长文本，适配 Embedding 模型上限。

    【术语】朴素分段 (naive / independent chunking):
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

    # F2 (2026-07-16): disallowed_special=() — 特殊 token 字面量按普通文本 BPE,
    # 不抛 ValueError (毒丸防护; 无特殊字面量的文本逐 token 不变)。
    tokens = _EMB_ENCODING.encode(text, disallowed_special=())
    if len(tokens) <= _EMB_MAX_TOKENS:
        return [text]  # 未超限，直接返回原文 (避免 encode/decode 往返)
    return [_EMB_ENCODING.decode(tokens[i:i + _EMB_MAX_TOKENS])
            for i in range(0, len(tokens), _EMB_MAX_TOKENS)]


# --- 从 panel/encode 导入共享配置 (Phase 2a: 取代旧的 importlib 反射) ---
from news_process.core.logging import pct4, sig4  # noqa: E402  # 日志四位有效数字单一事实源
from news_process.pipeline.panel.encode import CONFIG, logger  # noqa: E402

LLM_CONFIG = CONFIG.get('tone_llm_processing', {})
EMBEDDING_CONFIG = CONFIG.get('embedding_api', {})            # MAIN spec (Qwen/Qwen3-Embedding-8B, 无后缀)
_LARGE_SPEC = CONFIG.get('embedding_large', {})              # co-primary 嵌入 twin spec (_lg=text-embedding-3-large API; v3.14.0 起 ACTIVE 协同主轨)
_ALIGN_CFG = CONFIG.get('article_alignment', {})
_EMB_MAX_TOKENS = _coerce_positive_int(
    _ALIGN_CFG.get('max_tokens_per_input'), _EMB_MAX_TOKENS)
_EMB_MAX_TOKENS_PER_REQUEST = _coerce_positive_int(
    _ALIGN_CFG.get('max_tokens_per_request'), _EMB_MAX_TOKENS_PER_REQUEST)
_EMB_MAX_TOKENS_PER_REQUEST = max(
    _EMB_MAX_TOKENS, _EMB_MAX_TOKENS_PER_REQUEST)


# ── top-k N-最近邻扩展 (2026-07-02) ──────────────────────────────────────────
# 【术语】在既有 N-邻敏感性梯度基础上追加大邻域半径 N∈{10,20,30,40,50}, 与既有
#   N (基准 5 + 稳健 3,4,6,7) **互为稳健性、不分主次** (同族 N-邻敏感性梯度)。
# 【白话】除了看"最像的 5 家同行", 再看"最像的 10/20/30/40/50 家", 换邻居数看结论稳不稳。
# 该常量是全方法 (TF-IDF char/word · LDA · Embedding Qwen · Embedding large _lg) ×
#   全轨 (full/ctx/ss) 追加 N 的**单一事实源** (SSOT): 各方法的 N 列表 = 既有 ∪ _TOPK_NN。
#   emb 主轨与 _lg 孪生**必须共用同一 N 列表**以维持 co-primary both-or-neither parity。
# 成本: 扩 N 是对已算好相似度/距离矩阵的纯后处理 (见 _compute_nn_scores), **零额外
#   嵌入 API 调用** (_build_embedding_sim_matrix 每轨仅调一次, 与 N 无关)。
# 值域: 大 N 时 top-N 近邻趋近"与几乎全部同业的平均距离" (N→n_banks−1 时 ≡ 全 peer
#   均距), 与 centroid 构念趋同但仍为 Guzman-Li N-NN 口径 — 互为稳健性连续谱, 非冗余。
# 覆盖: 年内可比银行 < N+1 → 该 (bank, year) 的 N 列 NaN (|peers|<N→NaN 优雅降级)。
_TOPK_NN = [10, 20, 30, 40, 50]


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


# ── 领域注入的独立 jieba Tokenizer (fix inject-fintech-word-lda, 2026-06-21) ──
# 旧实现 _jieba_tokenizer 走裸全局 jieba.lcut, 默认词典把绝大多数中文金科复合词切碎
# (实测 1381/1480 ≥3 字金科词被切, 如 金融科技→金融/科技 · 区块链→区块/链), 致 word 级
# TF-IDF/LDA 稳健性对照轨的词表与 char 轨/embedding 轨**领域感知口径不一致**。修复: 把
# fintech_dict.json (607 词, 2026-07-21 换血; 与 stage 11/14/15 同源单一事实源) 注入一个**独立** jieba.Tokenizer
# 实例 (不污染全局 jieba.dt — 镜像 tone_words._get_tone_tokenizer / lexical_complexity
# ._get_pristine_tokenizer 既有最佳实践), 让 word/LDA 轨看到整词领域复合词。
# 影响列 = 全部 *_w (word TF-IDF) + 全部 *_lda 列 (含 ctx/ss/policy_similarity 复用)；
# char 轨 (char_wb n-gram, 不经本 tokenizer) 与 embedding 轨**字节不变** (经验探针 C1 已证)。
# 确定性来源 = 懒单例 (进程内只注入一次) + 词典文件确定序 + jieba==0.42.1 冻结
# (add_word 本身**非幂等** FREQ 累加, 但单例只构建一次故无累加; 探针 C2/C3/C4: 注入态两跑 bit 一致)。
# 6 个含空格/顿号关键词 (Open Banking 等) add_word 后仍被块切分正则切开退化为子 token,
# bag-of-words 场景无害 (与未注入等价), 故无需 matchable/unmatchable 分区。
# 权威计划 = scripts/audit/INJECT_FINTECH_DICT_WORD_LDA_TRACKS_PLAN_2026-06-21.md (三轮审核 + 经验实测)。
_DIFF_TOKENIZER_LOCK = threading.RLock()  # RLock: 防 sklearn joblib 线程并行 fit 时注入竞态
_DIFF_TOKENIZER: "jieba.Tokenizer | None" = None


def _get_diff_tokenizer() -> "jieba.Tokenizer":
    """返回注入了金科词的独立 jieba.Tokenizer (lazy 单例, DCL 锁)。

    fix(inject-fintech-word-lda, 2026-06-21): 领域词注入只进此实例, 全局 jieba.dt 保持纯净。
    词典缺失 (load_fintech_dict 返回空) → loud WARNING + 退化为未注入 Tokenizer, **绝不 raise**
    (优雅降级, 镜像 ctx_materializer 的 FINTECH_AC=None 安全语义)。
    """
    global _DIFF_TOKENIZER
    if _DIFF_TOKENIZER is None:
        with _DIFF_TOKENIZER_LOCK:
            if _DIFF_TOKENIZER is None:
                tk = jieba.Tokenizer()
                try:
                    from news_process.core.text.ahocorasick import load_fintech_dict
                    _dict_path = CONFIG['paths'].get('fintech_dict_file', '')
                    fintech_keywords, _ = load_fintech_dict(_dict_path)
                    if not fintech_keywords:
                        # fix(impl-attestation P2, 2026-06-21): 空/缺失词典 load_fintech_dict
                        # 返回 [] **不抛异常** → 必须显式 loud WARNING (否则只落静默 INFO,
                        # 与 docstring 承诺的"词典缺失 loud WARNING"不符, 留失明窗)。
                        logger.warning(
                            f"    [strategic_diff] 金科词典为空或缺失 ({_dict_path!r}); "
                            f"word/LDA 轨退化为未注入 jieba (领域复合词将被切碎, 口径回退旧态)")
                    else:
                        for _kw in fintech_keywords:
                            tk.add_word(_kw)
                        logger.info(
                            f"    [strategic_diff] word/LDA 轨分词器已注入 {len(fintech_keywords)} "
                            f"个金科词 (独立实例, 全局 jieba 纯净)")
                except Exception as e:  # noqa: BLE001
                    logger.warning(
                        f"    [strategic_diff] 金科词注入失败 ({type(e).__name__}: {e}); "
                        f"word/LDA 轨退化为未注入 jieba (领域复合词将被切碎, 口径回退旧态)")
                _DIFF_TOKENIZER = tk
    return _DIFF_TOKENIZER


def _jieba_tokenizer(text: str) -> list[str]:
    """jieba 中文分词 + 停用词过滤 (Chinese Tokenizer with Stopword Filtering)。

    【术语】基于**注入金科词的独立 jieba 实例** (见 ``_get_diff_tokenizer``) 的中文分词器,
      保留 len≥2 的 token 并移除停用词, 符合 NLP 中文文本预处理的标准做法 (Gentzkow et al. 2019, JEL)。
    【白话】把一段中文文本切成一个个词语，然后：
      - 扔掉单个字（如"的""了"），因为单字没啥意义
      - 扔掉停用词（如"和""在"），只保留有意义的词
      - **领域复合词整体保留**（如"金融科技""区块链"不再被切碎），与 char/embedding 轨口径一致
    例如: "银行的金融科技" → ["银行", "金融科技"] (注入后; 旧裸 jieba 为 ["银行","金融","科技"])
    """
    return [w for w in _get_diff_tokenizer().cut(text) if len(w) >= 2 and w not in _STOPWORDS]


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

# 句界切分 (sentence boundary): 用于共提及文章 1/n_banks 降权的 round-robin 均分
_SENT_SPLIT_RE = re.compile(r'(?<=[。！？!?；;\n])')


def _round_robin_sentences(text: str, rank: int, n: int) -> str:
    """共享文章句子级 round-robin 均分 (fix(omni-g-strategic-09), 2026-06-11)。

    【术语】同年内被 n>1 家银行共提的同文 (content 相同), 第 rank 家银行
    (按银行名排序的确定性序) 保留句子序列的 pieces[rank::n] 子集 —
    各银行保留的句子互不重叠 (零逐字共享), 每家期望词项权重 = 1/n_banks。
    【白话】一篇同时报道 3 家银行的文章, 把句子轮流分给 3 家银行, 每家拿 1/3,
    既保留信号又避免 3 家银行的"年度文档"出现一模一样的大段文字。
    无句界可切 (单句) 时退化为独占指派: 仅 rank=0 的银行保留全文。
    """
    if n <= 1:
        return text
    pieces = [s for s in _SENT_SPLIT_RE.split(text) if s]
    if len(pieces) <= 1:
        return text if rank == 0 else ''
    return ''.join(pieces[rank::n])


def _aggregate_bank_year_texts(df_exploded, text_col='内容',
                               co_mention_downweight=False):
    """按 (target_bank, year) 聚合新闻文本。

    【学术】Hoberg & Phillips (2016, JPE, §II.A) 将同一企业同一年度的
    所有 10-K 产品描述拼接为单一文档, 构建"年度产品空间"向量。
    本函数将其适配至新闻场景: 每家银行每年的所有新闻拼接为一篇"年度文本画像"。

    【白话】把同一家银行同一年的所有新闻（标题+正文）合并成一大段文本,
    方便后续用数学方法比较不同年份之间这段文本的变化程度。

    fix(omni-g-strategic-01, 2026-06-11) 语义变更: 同 (bank, year) 内逐字重复的
    文章文本 (content 相同, 含标题拼接后) 只计一次 — 防止转载/重发的同文机械
    放大词项权重。跨银行共享文章 (共提及) 默认**保留** (与 HP2016 互斥文本的
    构念差异见模块 docstring 局限性 4), 可经 co_mention_downweight 开关降权。

    Args:
        df_exploded: 文章-银行级 DataFrame, 需包含 target_bank, year 列
        text_col: 聚合使用的文本列名 — 三轨: '内容'/'content_full' (Full 轨),
            'content_ctx' (Ctx 轨), 'content_ss' (Ss 轨, 银行+金科同句共现)
        co_mention_downweight: fix(omni-g-strategic-09) 稳健开关 (默认 False =
            维持原口径)。True 时同年内被 n>1 家银行共享的同文按句子 round-robin
            均分到各银行 (每家 1/n_banks 权重, 跨银行零逐字重叠)。

    Returns:
        DataFrame[target_bank, year, agg_text], 已过滤空文本行
    """
    # 守卫: 空输入或目标文本列缺失 → 直接返回空 DataFrame
    if df_exploded.empty or text_col not in df_exploded.columns:
        logger.info(f"  文本聚合: 0 个 Bank-Year 文档 (text_col='{text_col}' 缺失或数据为空)")
        return pd.DataFrame(columns=['target_bank', 'year', 'agg_text'])

    bodies = df_exploded[text_col].fillna('').astype(str)
    if '标题' in df_exploded.columns:
        titles = df_exploded['标题'].fillna('').astype(str)
        # P1 修复 (metric-audit 2026-06-02): 去重防双标题. ctx 轨 text_col=content_ctx
        # 已由 stage 13 prepend_title 注入标题, 旧 'titles + 内容' 对 ctx 二次注入标题
        # → auth_sim_*_ctx / strat_*_ctx 全列受污 (full 轨 text_col=内容 无标题, 不受影响).
        # body 已以标题开头(ctx 轨) → 不再重复拼接标题; 否则按原 '标题 正文' 拼接.
        parts = [b if (t and b.startswith(t)) else (f"{t} {b}" if t else b)
                 for t, b in zip(titles, bodies)]
    else:
        parts = bodies.tolist()

    work = pd.DataFrame({
        'target_bank': df_exploded['target_bank'].values,
        'year': df_exploded['year'].values,
        '_part': parts,
    })
    # fix(omni-g-strategic-01): 文章级 content 去重 — 同 (bank, year) 内重复全文只计一次
    n_before = len(work)
    work = work.drop_duplicates(subset=['target_bank', 'year', '_part'],
                                keep='first')
    if len(work) < n_before:
        logger.info(f"  文本聚合: 同行年内重复全文去重 {n_before - len(work)} 行 "
                    f"(omni-g-strategic-01)")

    if co_mention_downweight and not work.empty:
        # fix(omni-g-strategic-09): 同年跨银行共享同文 → 句子级 round-robin 均分,
        # rank 按银行名排序确定性指派 (mergesort 稳定排序 + cumcount; 去重后
        # 每 (year, 同文) 组内银行唯一, cumcount 即 dense rank)
        n_share = (work.groupby(['year', '_part'])['target_bank']
                   .transform('nunique'))
        _sorted = work.sort_values(['year', '_part', 'target_bank'],
                                   kind='mergesort')
        rank = (_sorted.groupby(['year', '_part']).cumcount()
                .reindex(work.index))
        mask = (n_share > 1) & (work['_part'].str.len() > 0)
        if mask.any():
            logger.info(f"  文本聚合: 共提及降权 (1/n_banks) 作用于 "
                        f"{int(mask.sum())} 行 (omni-g-strategic-09)")
            work.loc[mask, '_part'] = [
                _round_robin_sentences(p, r, n)
                for p, r, n in zip(work.loc[mask, '_part'],
                                   rank[mask], n_share[mask])
            ]

    agg = (work.groupby(['target_bank', 'year'])['_part']
           .agg(' '.join).reset_index(name='agg_text'))
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

def _build_lda_jsd_matrix(texts, n_banks, log_sink=None):
    """jieba 词级 → LDA 主题分布 → pairwise JSD 距离。

    使用 Jensen-Shannon divergence (Lin 1991) 度量主题分布差异,
    JSD 是 KLD 的对称化平滑版本, 满足度量公理 (三角不等式)。

    主题数 K 的选取:
      - K = max(10, n_banks // 30), 确保主题数不低于 10
      - 当银行数 ~54 时 K=10, 每个主题约覆盖 5-6 家银行
      - ⚠ **旧披露 (omni-g-strategic-06, 2026-06-11) 称 "K 对本样本实为固定常数 10
        (伪自适应)" —— 该结论在生产规模上已被实测证伪, 2026-07-28 订正**:
        它成立的前提是 "<300 银行/年", 而生产 T=19 语料 2017-2025 每年
        428-584 家银行 (2022 年 584 家) ⟹ 584//30 = 19。stage 40 生产日志实测
        K ∈ {10, 11, 14, 15, 18, 19} (三轨各 37 次 LDA fit 全部逐条核对),
        **K 是真自适应且直接驱动本函数耗时** (LDA 成本近似线性于 K)。
        同段旧披露 ">165 银行/年时两处将分叉" 亦已发生: `_compute_lda_coherence`
        的 K 基数是两年池 n_total (≠ 此处单年 n_banks), 生产上两者取值不同。
      - 仍然成立的披露: 无 perplexity/held-out 数据驱动选 K, 亦无 K∈{5,15,20}
        敏感性列 (Bybee et al. / Hanley-Hoberg 类文本论文的标准披露项)。

    确定性 (fix(omni-g-strategic-16), 2026-06-11): n_jobs=1 + random_state=42。
    原 n_jobs=-1 时 sklearn online LDA E-step 按 effective_n_jobs 切片累加充分
    统计量, 切片数=核数 → 跨机器浮点求和序不同, 实测 max|Δθ|≈0.99 (nj=1 vs 2);
    random_state 仅在单线程下保证逐位可复现。~百级文档/年, 并行收益可忽略。
    (本函数被 policy_similarity.py 复用 → auth_sim_lda* 同受益。)

    Args:
        texts: 文本列表
        n_banks: 银行数量
        log_sink: 可选 ``list``; 给出时把本函数的 "LDA K=…, perplexity=…" 一行
            **追加进该列表** (元素为 ``(level, msg)``) 而非直接 ``logger.info``。
            ``None`` (默认) = 原样直接落日志, 与旧码逐字节同路径。
            ⚠ 存在的唯一理由: 本函数会在 **loky worker 内**被调用
            (policy_similarity 逐年并行, S5)。worker 体内直接 ``logger`` 会
            (a) 打乱行序、(b) 走子进程 console 而非阶段文件 handler ——
            与本模块 "worker 体内零 logger 调用, 告警一律回传父端 emit" 的既有
            契约冲突 (见 ``_run_year_tasks`` 上方长注释护栏 ④)。

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
    # fix(omni-g-strategic-16, 2026-06-11): n_jobs=-1 → 1 (跨机器核数依赖的
    # E-step 浮点求和序破坏逐位可复现性, 见函数 docstring "确定性" 段)
    # F26 (2026-07-27): 补钉底层 BLAS 线程 —— 上一行只堵了 sklearn 自身的 E-step 切片,
    # 没堵住 BLAS, 数值仍随机器线程数漂 ~1e-13。钉 1 后与环境无关且实测快 5.5×。
    lda = LatentDirichletAllocation(
        n_components=K, random_state=42,
        max_iter=50, learning_method='online', n_jobs=1)
    with _threadpool_limits(limits=1):
        theta = lda.fit_transform(dtm)
        _perp = lda.perplexity(cv.transform(texts))   # perplexity 亦走 BLAS, 同域内算
    # 行内容与旧码逐字节一致; 仅"由谁 emit"可切换 (见 Args::log_sink)。
    _lda_line = f"    LDA K={K}, perplexity={sig4(_perp)}"
    if log_sink is None:
        logger.info(_lda_line)
    else:
        log_sink.append((logging.INFO, _lda_line))

    # 计算 pairwise JSD (对称半矩阵)
    jsd_mat = np.zeros((n_banks, n_banks))
    for i in range(n_banks):
        for j in range(i + 1, n_banks):
            d = jensenshannon(theta[i], theta[j], base=2)  # sqrt(JSD) ∈ [0,1] (fix 2026-06-10: 原缺 base= → 默认 base e 上界 √ln2≈0.833≠1, 与 [0,1] 声称不符)
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


def _embed_texts_with_chunk_pooling(texts, *, spec=None, log_prefix="Embedding"):
    """将任意长度文本嵌入为文本级向量 (委托 embedding_engine, spec 参数化)。

    超长文本走朴素分段 (naive chunking) + Mean Pooling。spec 默认主轨
    (EMBEDDING_CONFIG, Qwen/Qwen3-Embedding-8B); 传 _LARGE_SPEC 则走
    co-primary _lg (text-embedding-3-large API)。失败/形状异常 → None。

    Returns:
        np.ndarray | None: 文本级 Embedding 向量 (n_texts, dim)
    """
    db_path = CONFIG['paths'].get(
        'llm_cache_db',
        os.path.join(CONFIG['paths']['output_dir'], '_llm_cache.db'),
    )
    _eff_spec = spec if spec is not None else EMBEDDING_CONFIG
    # API-fatal 守卫: _eng.embed_texts 对 API spec (网络/认证致命错) 无兜底直接 raise。
    # MAIN canonical (EMBEDDING_CONFIG=Qwen) 与本地 spec (如 SBERT) 一律 fail-fast
    # (保留 MAIN 既有失败语义 + 不吞离线确定性闸 RuntimeError); 仅 _lg twin (API 且非
    # MAIN) 把致命异常降级 None + warning (twin 是软诊断, 不应 fail-fast 整条流水线;
    # 与 policy_alignment 的 NaN 降级哲学一致)。⚠ both-or-neither: 调用方须保证一旦
    # 任一 spec (MAIN 或 _lg) 返回 None, 同族无后缀与 _lg 列一并置 NaN, 见 §5 编排。
    try:
        return _eng.embed_texts(
            texts,
            _eff_spec,
            cache_db_path=db_path,
            log_prefix=log_prefix,
        )
    except Exception as e:
        if _eng.spec_uses_local(_eff_spec) or _eff_spec is EMBEDDING_CONFIG:
            raise  # MAIN canonical 与本地 spec 致命错显式暴露 (行为不变)
        logger.warning(
            f"    {log_prefix}: _lg twin API 嵌入致命异常 "
            f"({type(e).__name__}: {e}), 降级 None (twin 软诊断, 不中断 stage)")
        return None


def _build_embedding_sim_matrix(texts, spec=None):
    """构建 Embedding cosine 相似度矩阵, 长文本分段池化 (spec 参数化, 逐轨复用于三轨 full/ctx/ss)。

    Returns:
        tuple: (sim, emb)
          - sim: np.ndarray | None, 相似度矩阵, 降级失败时返回 None
          - emb: np.ndarray | None, 文本级 Embedding 向量 (n_banks, dim)
            (供 centroid 计算复用)
    """
    emb = _embed_texts_with_chunk_pooling(texts, spec=spec, log_prefix="Embedding")
    if emb is None:
        return None, None

    # F41 (2026-07-31): 钉 BLAS 线程 —— 与 F26 (LDA fit 现场) 同一手法, 补的是**另一个
    # 口子**。`cosine_similarity(emb)` 对 dense float32 走 BLAS `gemm`, 其归约序随线程数
    # 变 ⟹ 输出逐位随机器/并行度漂移。实测 (500×4096 float32): 1 线程 vs 8/16 线程
    # `np.array_equal`=False, maxdiff **1.19e-7** (float32 嵌入, 比 LDA 的 1e-13 大 6 个
    # 量级)。而 emb 正是 `_embed_texts_with_chunk_pooling` 的 float32 输出。
    # **为何非补不可**: 本函数被 `policy_similarity._auth_year_worker` (S5 逐年 loky 并行)
    # 调用, 而 joblib `LokyBackend._prepare_worker_env` 给 worker 的线程数是
    # `os.environ.get(var, cpu_count() // n_jobs)` —— 父进程**未钉** BLAS 环境变量时,
    # worker 得到 `32 // n_jobs`, 于是 `NEWS_PROCESS_AUTH_JOBS` 这个**纯运维旋钮**会
    # 静默改变 `auth_sim_emb*` / `auth_sim_emb_lg*` 的产出值; 串行回落臂 (父进程 32 线程)
    # 与并行臂也算不出同一个数。钉 1 后三者收敛到同一个 canonical 值。
    # **golden-safe (已实证)**: 在 CLAUDE.md 既定重生协议 (MKL/OPENBLAS/NUMEXPR/OMP
    # 四个环境变量全 =1) 下, 本 with 块是逐位 no-op (同探针 `np.array_equal`=True) ⟹
    # 不可能移动 golden。受影响的是**未钉环境**下的旧跑, 方向同 F26: 向 canonical 靠拢。
    with _threadpool_limits(limits=1):
        sim = cosine_similarity(emb)
    np.fill_diagonal(sim, np.nan)
    # fix(omni-g-strategic-02, 2026-06-11): emb 余弦真值域 [-1,1] (非 [0,1]) —
    # 消费端 _compute_nn_scores 须传 sim_bounds=(-1,1), 勿按 [0,1] 删失
    return sim, emb  # sim: similarity ∈ [-1,1] (embedding 余弦); emb: ndarray (n_banks, dim)


# ============================================================================
# 5. N-最近邻聚合 (N-Nearest Neighbor Aggregation) (Hoberg & Phillips 2016, §III.B)
# 【术语】实现 Guzman & Li (2023, MS, §3) 核心公式 Ŝ_i = (1/N)Σδ_ij，
#   对每家银行取其在文本空间中 N 个最近邻的平均距离作为战略差异度。
# 【白话】这是核心步驤！对每家银行，找到和它最像的 N 家同行，
#   然后看它与这 N 家同行的"平均距离"。
#   比喻: 就像在班级里找到和你成绩最接近的 5 个同学，
#   然后看你们的平均差距有多大 — 差距越大，说明你越"与众不同"。
# ============================================================================

def _compute_nn_scores(matrix, bank_list, N_list, is_distance=False,
                       sim_bounds=(0.0, 1.0)):
    """N-最近邻差异度聚合 — 实现 Guzman & Li (2023) Section 3 核心公式。

    fix(omni-g-strategic-02/05, 2026-06-11) 两处语义变更:
    1. sim_bounds 参数化相似度真值域 — TF-IDF (非负向量) 默认 (0,1);
       embedding 余弦须传 (-1,1), clip 仅作浮点容忍 (~1e-7) 而非值域删失
       (原统一 clip[0,1] 把 emb 真负余弦地板到 0 → δ 封顶 1.0/sim_max 报 0);
       emb 轨距离 δ=1-sim ∈ [0,2]。
    2. |peers| < N → 置 NaN (不可测量) — 原 k=min(N,|peers|) 静默降级使低覆盖
       年份 n3..n7 五列塌缩同值, 制造虚假的 N 敏感性稳健。

    本函数直接实现论文中从相似度到战略差异度的转换规则:

        Ŝ_i = (1/N) Σ_{j ∈ J_i^N} δ_ij
        (Guzman & Li 2023, Management Science, §3 "From similarity to
         founding strategy")

    其中 δ_ij = 1 - cosine_similarity(v_i, v_j) 为文本距离,
    J_i^N 为银行 i 的 N 个最近邻 (文本空间中相似度最高的 N 家同行)。

    对于每家银行, 找到文本空间中最近的 N 个同行:
      - similarity 矩阵: 取最大 N 个, 差异度 = mean(1 - sim_topN) → Ŝ_i
      - distance 矩阵: 取最小 N 个, 差异度 = mean(dist_topN) → Ŝ_i

    N=5 为基准 (与论文一致), N∈{3,4,6,7}∪{10,20,30,40,50} 为敏感性检验 (小/大邻域半径, 互为稳健性)。
    N 值敏感性检验的理论基础:
      Bresnahan, T. F., & Reiss, P. C. (1991). Entry and competition in
      concentrated markets. Journal of Political Economy, 99(5), 977–1009.
      https://doi.org/10.1086/261786

    Args:
        matrix: 相似度或距离矩阵 (n×n), 对角线为 NaN
        bank_list: 银行名称列表
        N_list: N 值列表 (如 [3,4,5,6,7])
        is_distance: True=距离矩阵, False=相似度矩阵
        sim_bounds: 相似度算子真值域 (lo, hi) — TF-IDF/LDA 默认 (0,1);
            embedding 余弦传 (-1,1) (fix(omni-g-strategic-02))

    Returns:
        dict: {f'n{N}': {bank: Ŝ_i}, 'sim_max': {bank: max_similarity}}
        (|peers| < N 的 bank → n{N} 为 NaN, fix(omni-g-strategic-05))
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
            # float 误差容忍: 距离可微负 / sim=1-dist 可微超 1 → clip [0,1] (镜像 L839)
            results['sim_max'][bank] = float(np.clip(1.0 - valid[idx[0]], 0.0, 1.0))
            for N in N_list:
                if len(valid) < N:
                    # fix(omni-g-strategic-05, 2026-06-11): |peers| < N → NaN
                    # (原 k=min(N,|peers|) 静默降级 → n3..n7 塌缩同值伪稳健)
                    results[f'n{N}'][bank] = np.nan
                    continue
                # Ŝ_i = mean(dist_topN)
                results[f'n{N}'][bank] = float(np.clip(np.mean(valid[idx[:N]]), 0.0, 1.0))
        else:
            # 相似度矩阵: 降序排列, 取最大 N 个
            # Guzman & Li (2023, §3): δ_ij = 1 - sim_ij → Ŝ_i = mean(δ_topN)
            # metric-audit 2026-06-02 + fix(omni-g-strategic-02, 2026-06-11):
            # float32 cosine 点积可溢出真值域 ~1e-7 (归一化向量内积舍入) → clip 到
            # **算子真值域 sim_bounds** (TF-IDF [0,1] / emb [-1,1]) 作浮点容忍;
            # 原硬编码 [0,1] 对 emb 是值域删失 (真负余弦地板到 0)。
            valid = np.clip(valid, sim_bounds[0], sim_bounds[1])
            idx = np.argsort(valid)[::-1]
            results['sim_max'][bank] = float(valid[idx[0]])
            for N in N_list:
                if len(valid) < N:
                    # fix(omni-g-strategic-05, 2026-06-11): |peers| < N → NaN
                    results[f'n{N}'][bank] = np.nan
                    continue
                # Ŝ_i = (1/N) Σ_{j ∈ J_i^N} (1 - sim_ij)
                results[f'n{N}'][bank] = float(np.mean(1.0 - valid[idx[:N]]))
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
#   4. Full/Ctx/Ss 三轨对比检验全文噪声 / 归因窗口收紧对指标的影响,
#      增强学术论文稳健性检验的厚度。
#
# 【术语】计算每家银行文本向量与全行业质心 (centroid) 的余弦距离，
#   度量银行与"行业平均水平"的战略偏离程度。
# 【白话】把所有银行的向量取平均，得到"行业平均画像"。
#   然后看每家银行和这个"平均画像"有多不同。越不同 = 创新边界越大。
# ============================================================================

def _compute_centroid_scores(vectors, bank_list, is_sparse=False,
                             dist_bounds=(0.0, 1.0)):
    """全行业向量法: 1 - CosineSim(bank_vec, leave-one-out industry_centroid)。

    fix(omni-g-strategic-10, 2026-06-11) 语义变更: 行业质心改 **leave-one-out**
    (c_{-i} = (n·c − v_i)/(n−1)) — 原 mean(全部含自身) 使 cos(v_i, c) 含 ~1/n_t
    机械自相关, 且对与行业越正交的银行抬升越多 → centroid_diff 右尾被系统性
    压缩。与模块内既有惯例一致 (N-NN 路径 fill_diagonal NaN / fluidity
    other != bank 均排除自身, 质心路径原是模块内唯一不排除者)。n<2 → NaN。
    fix(omni-g-strategic-02 同口径): dist_bounds 参数化距离真值域 — TF-IDF/LDA
    (非负向量/分布, cos ∈ [0,1]) 默认 (0,1); embedding 余弦 ∈ [-1,1] →
    距离 ∈ [0,2], 调用方传 (0,2), clip 仅作浮点容忍而非值域删失。

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
      4. Full/Ctx/Ss 三轨对比增强稳健性检验厚度。

    与 N-最近邻法的区别:
      - N-NN (Guzman & Li 2023, MS, §3): Ŝ_i = mean(dist to N peers)
        → "我与最像我的几家同行有多不同" (niche distance)
      - Centroid (谢佳松 2025, 经济研究, 图 1): C_i = 1 - cos(v_i, c_{-i}),
        c_{-i} = leave-one-out 行业质心 (排除自身后均值)
        → "我与行业平均水平有多不同" (average distance)

    Args:
        vectors: (n_banks, dim) 向量矩阵 (稀疏或稠密)
        bank_list: 银行名称列表
        is_sparse: True 则使用稀疏矩阵操作
        dist_bounds: 距离真值域 (lo, hi) — TF-IDF/LDA 默认 (0,1);
            embedding 余弦传 (0,2) (fix(omni-g-strategic-02 同口径))

    Returns:
        dict: {bank: centroid_diff ∈ dist_bounds}; n<2 时全 NaN (LOO 无定义)

    References:
        谢佳松, 樊嘉诚, & 林建浩. (2025). 信息摩擦、公共数据与企业创新边界.
          经济研究, (11).
        Guzman, J., & Li, A. (2023). Measuring founding strategy.
          Management Science, 69(1), 101–118.
          https://doi.org/10.1287/mnsc.2022.4369
    """
    # fix(omni-g-strategic-10, 2026-06-11): leave-one-out 质心 c_{-i} = (n·c − v_i)/(n−1)
    # — 原 mean(全部, 含自身权重 1/n_t) 使 cos(v_i, c) 含机械自相关, 且对与行业越
    # 正交的银行抬升越多 → centroid_diff 右尾被系统性压缩。与模块内既有惯例对齐
    # (N-NN 路径 fill_diagonal NaN / fluidity other != bank 均排除自身)。
    dense = (np.asarray(vectors.todense(), dtype=np.float64) if is_sparse
             else np.asarray(vectors, dtype=np.float64))
    n = dense.shape[0]
    if n < 2:
        # 单银行年: leave-one-out 质心无定义 → NaN (不可测量)
        return {bank: float('nan') for bank in bank_list}
    total = dense.sum(axis=0, keepdims=True)
    loo_centroid = (total - dense) / (n - 1)   # 每行 = 排除该银行自身后的行业质心
    num = np.einsum('ij,ij->i', dense, loo_centroid)
    denom = (np.linalg.norm(dense, axis=1)
             * np.linalg.norm(loo_centroid, axis=1))
    with np.errstate(invalid='ignore', divide='ignore'):
        sims = np.where(denom > 0, num / np.where(denom == 0, 1.0, denom), np.nan)
    # clip 至算子真值域 dist_bounds (仅浮点容忍, fix(omni-g-strategic-02 同口径)):
    # TF-IDF/LDA 非负向量 → cos ∈ [0,1] → 距离 [0,1]; embedding 余弦 ∈ [-1,1] →
    # 距离 [0,2] (调用方传 (0,2), 原硬编码 [0,1] 对 emb 是值域删失)
    lo, hi = dist_bounds
    return {bank: (float(np.clip(1.0 - sims[i], lo, hi))
                   if np.isfinite(sims[i]) else float('nan'))
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

# ════════════════════════════════════════════════════════════════════════════
# F25 (2026-07-27): 「相邻期 (t, t-1)」逐年循环的进程并行驱动
#
# **为何 (2026-07-27 生产实弹)**: stage 40 跑满 21,600s 被父端强杀, 逐子步骤归因显示
# 「相邻期文本连贯性」是仅次于战略差异度主循环的第二大极 —— 单轨 TF-IDF char 28 分钟
# + word 25 分钟, 三轨 × 4 算子外推 ≈5 小时, 而全程只用 32 逻辑核中的 **1 核**。
#
# **为何这里是最安全的并行靶**: 本族三个函数 (_compute_fluidity /
# _compute_tfidf_coherence / _compute_lda_coherence) 形状完全一致 ——
#   for year in sorted(unique): 取 df_t / df_t1 → 首年或断档 continue → 本年自洽计算
#   → 写入 {(bank, year): 值} 的**互斥键**
# 逐年之间零共享状态、零 DB、零 API、零随机源 (LDA 已 random_state=42 + n_jobs=1),
# 故进程并行**不改任何数值**, 只改执行顺序; 而结果按任务原序归并, 连 dict 插入序都与
# 串行一致。
#
# **确定性护栏**:
#   ① 任务切分 `_adjacent_year_tasks` 与串行循环**同序同筛选** (sorted(unique) + 同
#      df_t1.empty 判据) —— 切分口径一旦漂移就是静默改测度;
#   ② joblib.Parallel 按**提交序**返回, 不按完成序 → 归并序恒定;
#   ③ 年数 < _PROC_PARALLEL_MIN_YEARS 或只配到 1 worker 时**回落串行**, 与旧码逐字节
#      同路径 (T=2 dev / golden 小样本因此零行为变化);
#   ④ worker 体内**零 logger 调用** —— 降级/失败告警一律回传, 由父端统一 emit,
#      保证告警不丢也不重, 且 worker 被父进程直接调用 (串行回落) 时行为一致。
#   ⚠ 本模块**没有**模块级 setup_logging (只 logging.getLogger), 故 loky worker import
#      本模块不会截断生产日志 (对比 herd_decay: 2026-07-26 实弹被 A/B 脚本抹掉过日志)。
#
# **实测边界 (2026-07-27 真数据 A/B, 2007-2011)**: TF-IDF 连贯性 277 键 / fluidity
# 455 键在 char 与 word 双 mode 下**全部逐位相同**, 提速 2.83× / 3.09× / 1.43× / 7.33×;
# `_compute_lda_coherence` 首版曾出现 265/277 个 ~1e-13 漂移 —— 根因是 **BLAS 线程数
# 差异**而非并行本身 (loky worker 默认钉 1, 父进程用满线程)。
# ⚠ **2026-07-28 订正**: 该漂移已由 F26 (LDA fit 现场 `threadpool_limits(1)`) 根治,
#   `_compute_lda_coherence` **早已改为并行** (见其函数体, 走 `_run_year_tasks`)。
#   本段此前遗留 "该函数恒串行" 的结论是 F26 落地时未同步更新的陈旧文案, 现已作废 ——
#   它会直接误导 "LDA 不可并行", 而 S5 (policy_similarity, LDA 占其 39.9%) 正建立在
#   相反的事实上: 只要 BLAS 钉 1, LDA 并行即字节安全。
# ════════════════════════════════════════════════════════════════════════════

#: 年数下限 — 低于此值进程启动开销 (loky spawn + 每 worker 一份 jieba Trie) 不划算。
_PROC_PARALLEL_MIN_YEARS = 4
#: worker 上限 — 与 stage 15/22/24 同档。每 worker 各持一份注入 607 词的 jieba Tokenizer
#: + sklearn 词表; n_jobs=-1 (32 副本) 在 stage 22 已实弹 MemoryError, 此处不重蹈。
_PROC_PARALLEL_MAX_WORKERS = 12


def _proc_workers(n_tasks: int) -> int:
    """并行度 = min(硬上限, 可用核-2, 任务数); 至少 1。留 2 核给父进程与系统。"""
    try:
        n_cpu = len(os.sched_getaffinity(0))          # Linux/容器 亲和性口径
    except AttributeError:
        n_cpu = os.cpu_count() or 1                   # Windows 走这条
    return max(1, min(_PROC_PARALLEL_MAX_WORKERS, n_cpu - 2, n_tasks))


# ════════════════════════════════════════════════════════════════════════════
# S13 (2026-07-31): 主逐年循环 (`compute_strategic_differentiation`) 的进程并行
# ════════════════════════════════════════════════════════════════════════════
# F25 只并行了 fluidity / tfidf_coherence / lda_coherence 三个「相邻期」循环;
# 本函数**自己的**三轨逐年循环 (Full + _ctx + _ss) 一直是串行的, 而它才是 stage 40
# 里 strategic_diff 窗口的大头。
#
# 🔴 **并行它之前必须先解决一个别处没有的阻断项**: 本循环体内会调 `embed_texts`,
# 而 `embedding_engine.EMB_API_CONCURRENCY` 默认 **250** (每次调用内部
# `asyncio.Semaphore(min(250, n_batches))`)。若直接 fan-out 到 P 个 loky worker,
# 对同一端点的并发上界就变成 **P × 250** —— 而 250 这个值本身就是 2026-07-24
# stage 16 首播撞硅基流动 TPM 限流后**降下来**的结果, 再乘 12 必然重演 F28
# (重试耗尽 → `strat_diff_n*_emb*` / `centroid_diff_emb*` 整族静默 NaN)。
#
# **解法 (`_scale_worker_emb_concurrency`)**: fan-out 前把 `NEWS_PROCESS_EMB_CONCURRENCY`
# 按 worker 数**等比缩小**写进环境, loky worker 重新 import 时读到的就是 `250 // P`,
# 于是**总并发回到 250 —— 与今天的串行行为一致**。
#   · 为什么有效: 该常量在模块 import 时求值, 而 loky worker 是新进程、必然重新 import;
#     父进程自己的常量已在更早的 import 固化, 不受影响 (作用域天然只覆盖新 worker)。
#   · 为什么不选"父进程串行预播种": 那要把嵌入读+解码做两遍 (实测占单任务 ~17%),
#     且会改变阶段日志结构; 本方案零额外工作、日志结构不变。
#   · 用户已显式设过该变量时**一律不覆盖** (运维意图优先)。
#
# **确定性**: 并发只影响墙钟不影响产出字节 (embedding_engine 按 batch_idx 重组, 见其
# 模块注释); 循环体内的 dense-BLAS 现场已由 F26 (LDA fit) 与 F41 (emb cosine) 钉死;
# `_compute_centroid_scores` 的三处归约 (`sum(axis=0)` / `einsum('ij,ij->i')` /
# `norm(axis=1)`) 实测**线程无关** (1/2/8/16/24 五档 × emb/tfidf/theta 三形态全同,
# 含同线程数重复两次的控制组) ⟹ 不需要额外钉。
_STRAT_PARALLEL_MIN_YEARS = 12   #: 3 轨 × N 年扁平池; T=2 dev (6) 与单测一律留串行
_STRAT_JOBS_ENV = 'NEWS_PROCESS_STRAT_JOBS'      #: 运维旁路 (同 S5 的 AUTH_JOBS)
_EMB_CONCURRENCY_ENV = 'NEWS_PROCESS_EMB_CONCURRENCY'
_EMB_CONCURRENCY_BASELINE = 250  #: 与 embedding_engine 默认值一致 (总并发预算)


def _strat_jobs_override():
    """读 ``NEWS_PROCESS_STRAT_JOBS``; 非正整数或未设 → None (用默认并行度)。"""
    raw = os.environ.get(_STRAT_JOBS_ENV, '').strip()
    if not raw:
        return None
    try:
        v = int(raw)
    except ValueError:
        logger.warning(f"  {_STRAT_JOBS_ENV}='{raw}' 非整数, 忽略 (用默认并行度)")
        return None
    if v < 1:
        logger.warning(f"  {_STRAT_JOBS_ENV}={v} < 1, 忽略 (用默认并行度)")
        return None
    return v


#: 本进程是否已由 `_scale_worker_emb_concurrency` 写过并发环境变量。
#: ⚠ 需要这个标记而不能只看"变量是否已设": 三条轨会各调一次, 第 2/3 次看到的是
#: **我们自己**上一次写的值, 若照"已设 ⟹ 运维意图优先"分支去报, 日志就是假的。
_EMB_CONCURRENCY_SCALED_BY_US = False


def _scale_worker_emb_concurrency(n_jobs: int) -> None:
    """把嵌入 API 并发按 worker 数等比缩小写进环境, 使**总**并发回到基线 250。

    只对**之后新建的** loky worker 生效 (它们重新 import `embedding_engine`);
    父进程自身的常量早已固化, 不受影响。用户显式设过该变量时不覆盖。
    """
    global _EMB_CONCURRENCY_SCALED_BY_US
    _cur = os.environ.get(_EMB_CONCURRENCY_ENV, '').strip()
    if _cur and not _EMB_CONCURRENCY_SCALED_BY_US:
        logger.info(
            f"  嵌入 API 并发: 沿用已设的 {_EMB_CONCURRENCY_ENV}={_cur} "
            f"(运维意图优先, 不按 worker 数缩放)")
        return
    per_worker = max(1, _EMB_CONCURRENCY_BASELINE // max(1, n_jobs))
    if _cur == str(per_worker):
        return                      # 同轨同并行度重复调用: 静默幂等, 不刷重复日志
    os.environ[_EMB_CONCURRENCY_ENV] = str(per_worker)
    _EMB_CONCURRENCY_SCALED_BY_US = True
    logger.info(
        f"  嵌入 API 并发: 每 worker {per_worker} × {n_jobs} worker "
        f"≈ {per_worker * n_jobs} (基线 {_EMB_CONCURRENCY_BASELINE}) —— "
        f"防 P×250 打爆 TPM 重演 F28")


# ⚠ 刻意**没有** `_silence_worker_logging()`: 下方三个 worker 会被**父进程直接调用**
# (年数 < 阈值 / 只配到 1 worker 的串行回落路径, 以及 `_run_year_tasks` 的 OOM 兜底
# 整批串行重跑路径)。若在 worker 里降 logger 级别, 这些串行路径会把整个 stage 的 INFO
# 日志掐掉 —— 那正是 F16 那类"日志落空"缺陷的自造版本。改用**告警回传父端 emit**:
# worker 体内零 logger 调用。
# (原文此处还列了"LDA 的恒串行路径" —— F26 之后 LDA 已并行, 该项 2026-07-28 删除。)


def _strat_year_worker(task, n_list_cw, n_list_other, few_banks_warn,
                       lda_fail_tmpl, bon_tail_tmpl):
    """单 (轨, 年) 的五方法计算 —— 原逐年循环体的**计算段**逐字节照搬。

    ⚠ 与串行循环唯一的差别: 所有 ``logger.*`` 改为写进本地 ``logs`` 回传, 由父端按
    提交序统一 emit (与 S5 `_auth_year_worker` 同一护栏)。两个早退守卫 (<3 家银行 /
    both-or-neither 塌缩) **刻意留在 worker 内**, 提到父端会让守卫告警与计算类日志的
    交错顺序偏离串行。

    ⚠ **行装配刻意不在这里**: 列名 (`strat_diff_n{N}{sfx}` 等几十个) 全部留在父端
    原地不动 —— 移动几十个 f-string 列名是本改动风险最高、收益最低的部分, 而它们
    是纯字典查表, 本就不耗时。worker 只回传各方法的小字典 (n_banks × ~10 个 float),
    IPC 轻。

    Args:
        task: ``(track_label, track_suffix, year, banks, texts)``。
        n_list_cw:    char/word 两法的 N 列表 (Full 轨 = N_LIST; 子轨 = LDA_EMB_N_LIST)。
        n_list_other: lda/emb/emb_lg 的 N 列表 (两轨均 = LDA_EMB_N_LIST)。
        few_banks_warn: <3 家银行时是否发告警 (Full 轨 True; 子轨原为裸 continue)。
        lda_fail_tmpl:  LDA 失败告警模板 (含 ``{year}`` / ``{exc}`` 占位)。
        bon_tail_tmpl:  both-or-neither 告警的列名尾串模板 (含 ``{n}``)。

    Returns:
        ``(payload | None, logs)`` — payload 为各方法结果字典; None 表示该年跳过。
    """
    track_label, track_suffix, year, banks, texts = task
    logs: list[tuple[int, str]] = []

    if len(banks) < 3:
        if few_banks_warn:
            logs.append((logging.WARNING,
                         f"  年度={year}: 仅 {len(banks)} 家银行, 跳过 (最低要求 3)"))
        return None, logs
    if few_banks_warn:
        logs.append((logging.INFO, f"  年度={year}, 银行数={len(banks)}"))

    # 方法 A: TF-IDF 字符级 — 看字符组合的相似度（不依赖分词）
    sim_c, vec_c = _build_tfidf_sim_matrix(texts, 'char')
    sc = _compute_nn_scores(sim_c, banks, n_list_cw)
    # 全行业向量法 (谢佳松 2025, 经济研究, 图 1)
    cd_c = _compute_centroid_scores(vec_c, banks, is_sparse=True)
    # 方法 B: TF-IDF 词级 — 用 jieba 分词后比较（语义更精准）
    sim_w, vec_w = _build_tfidf_sim_matrix(texts, 'word')
    sw = _compute_nn_scores(sim_w, banks, n_list_cw)
    cd_w = _compute_centroid_scores(vec_w, banks, is_sparse=True)
    # 方法 C: LDA + JSD — 比较"主题分布"的差异（稳健性检验）
    try:
        jsd_mat, theta = _build_lda_jsd_matrix(texts, len(banks), log_sink=logs)
        sl = _compute_nn_scores(jsd_mat, banks, n_list_other, is_distance=True)
        cd_lda = _compute_centroid_scores(theta, banks)
    except Exception as e:
        logs.append((logging.WARNING,
                     lda_fail_tmpl.format(year=year, exc=type(e).__name__)))
        sl = None
        cd_lda = None
    # 方法 D: Embedding (主轨) — Qwen/Qwen3-Embedding-8B 语义距离
    # fix(omni-g-strategic-02/10, 2026-06-11): emb 余弦真值域 [-1,1] /
    # 距离 [0,2] — 显式传 bounds, 防按 TF-IDF [0,1] 默认值删失负余弦
    se_mat, se_emb = _build_embedding_sim_matrix(texts)
    if se_mat is not None:
        se = _compute_nn_scores(se_mat, banks, n_list_other, sim_bounds=(-1.0, 1.0))
        cd_emb = _compute_centroid_scores(se_emb, banks, dist_bounds=(0.0, 2.0))
    else:
        se, cd_emb = None, None
    # 方法 D-lg: co-primary 嵌入 (_lg=text-embedding-3-large API; v3.14.0 起 ACTIVE)
    se_lg, cd_emb_lg = None, None
    if _LARGE_SPEC:
        se_mat_lg, se_emb_lg = _build_embedding_sim_matrix(texts, spec=_LARGE_SPEC)
        if se_mat_lg is not None:
            se_lg = _compute_nn_scores(se_mat_lg, banks, n_list_other,
                                       sim_bounds=(-1.0, 1.0))
            cd_emb_lg = _compute_centroid_scores(se_emb_lg, banks,
                                                 dist_bounds=(0.0, 2.0))
        # both-or-neither parity (v3.14.0): MAIN 与 _lg 是 co-primary, 任一嵌入
        # 失败 → 两者同族列一并 NaN (无单边孤儿列, parity test 守门)。
        if se is None or se_lg is None:
            # F28 同型站点留痕 (2026-07-28); 只加日志, 零数值改动。
            logs.append((logging.ERROR,
                         f"🔴 战略差异度 both-or-neither 塌缩 [{track_label} 轨 "
                         f"year={year}]: "
                         f"失败臂={'MAIN(Qwen)' if se is None else ''}"
                         f"{'+' if se is None and se_lg is None else ''}"
                         f"{'_lg(large)' if se_lg is None else ''}; "
                         + bon_tail_tmpl.format(n=len(banks))))
            se, cd_emb = None, None
            se_lg, cd_emb_lg = None, None

    return {'sc': sc, 'sw': sw, 'sl': sl, 'se': se, 'se_lg': se_lg,
            'cd_c': cd_c, 'cd_w': cd_w, 'cd_lda': cd_lda,
            'cd_emb': cd_emb, 'cd_emb_lg': cd_emb_lg}, logs


def _run_strat_year_tasks(tasks, n_list_cw, n_list_other, few_banks_warn,
                          lda_fail_tmpl, bon_tail_tmpl):
    """S13 驱动器: 决定并行度 → 缩放嵌入 API 并发 → 复用 `_run_year_tasks` 执行。

    并行度 = `NEWS_PROCESS_STRAT_JOBS` 覆盖值, 否则 `_proc_workers(len(tasks))`。
    走串行臂时**不动**嵌入并发环境变量 (串行本就只有一个 250 的预算)。
    """
    _n = _strat_jobs_override()
    _eff = _n if _n is not None else _proc_workers(len(tasks))
    if len(tasks) >= _STRAT_PARALLEL_MIN_YEARS and _eff > 1:
        _scale_worker_emb_concurrency(_eff)
        logger.info(
            f"  逐年并行: {len(tasks)} 个 (轨,年) 任务 → n_jobs={_eff} "
            f"(阈值 {_STRAT_PARALLEL_MIN_YEARS}; 旁路 {_STRAT_JOBS_ENV})")
    else:
        logger.info(
            f"  逐年串行: {len(tasks)} 个 (轨,年) 任务 "
            f"(< 阈值 {_STRAT_PARALLEL_MIN_YEARS} 或并行度={_eff})")
    return _run_year_tasks(
        tasks, _strat_year_worker,
        n_list_cw, n_list_other, few_banks_warn, lda_fail_tmpl, bon_tail_tmpl,
        min_tasks=_STRAT_PARALLEL_MIN_YEARS, n_jobs=_n)


def _strat_year_tasks(agg, track_label, track_suffix):
    """把主逐年循环切成 ``(轨, 年, banks, texts)`` 任务单元。

    ⚠ 必须与串行循环**同序同筛选**: `sorted(agg['year'].unique())`, 且 <3 家银行的
    年份**照样进池** (由 worker 内的守卫早退并发告警) —— 在这里提前筛掉会让告警
    时序偏离串行。
    """
    return [(track_label, track_suffix, year,
             agg[agg['year'] == year]['target_bank'].tolist(),
             agg[agg['year'] == year]['agg_text'].tolist())
            for year in sorted(agg['year'].unique())]


def _adjacent_year_tasks(agg_df):
    """把「取 df_t / df_t1」的逐年循环切成任务单元。

    ⚠ 必须与串行循环**同序同筛选**: sorted(agg_df['year'].unique()) + 同一
    ``df_t1.empty → continue`` 判据。任一处漂移都是静默改测度 (少算/多算年份)。
    只带出 target_bank / agg_text 两列以压 IPC (三函数的循环体只读这两列)。
    """
    tasks = []
    for year in sorted(agg_df['year'].unique()):
        df_t = agg_df[agg_df['year'] == year]
        df_t1 = agg_df[agg_df['year'] == year - 1]
        if df_t1.empty:
            continue                                   # 首年无前期数据 (与串行同)
        tasks.append((
            int(year),
            df_t[['target_bank', 'agg_text']].reset_index(drop=True),
            df_t1[['target_bank', 'agg_text']].reset_index(drop=True),
        ))
    return tasks


def _run_year_tasks(tasks, worker, *extra, min_tasks=None, n_jobs=None,
                    on_result=None):
    """串/并自适应执行, 结果**按提交序**返回 (joblib.Parallel 语义, 非完成序)。

    Args:
        tasks:     任务单元列表 (由 ``_adjacent_year_tasks`` 等切分函数产出)。
        worker:    模块级 worker 函数 (须可 pickle by reference)。
        *extra:    透传给 worker 的额外定参。
        min_tasks: 走并行的任务数下限; ``None`` = 用本模块的
                   ``_PROC_PARALLEL_MIN_YEARS`` (=4)。
        n_jobs:    并行度; ``None`` = 用 ``_proc_workers(len(tasks))``。
        on_result: 可选回调 ``f(result)``; 给出时**每个任务一完成就立刻回调**
                   (仍按提交序), 而不是等整批算完。``None`` (默认) = 老路径,
                   与既有三个调用点逐字节同路。返回值不受影响 (恒为完整 list)。

    ⚠ **两个参数都是 2026-07-28 S4 新增的向后兼容扩展**, 默认值使既有三个调用点
    (fluidity / tfidf_coherence / lda_coherence) 走**逐字节同一条路径**, 行为零变化。
    加它们是因为设计评审实测出两条:

      ① **阈值不能跨模块硬借**。``policy_similarity`` 的任务池是「3 轨 × N 年」扁平池,
         只要 N≥2 就 ≥6 个任务, 直接复用 4 这个阈值会让**现存单测也走进并行分支** ——
         而单测靠 ``monkeypatch`` 打桩, **桩不会传播进 loky 子进程** ⟹ 测试当场失真。
         故调用方须能自设更高阈值 (如 12/20), 让 toy fixture 与 T=2 dev 一律串行。
      ② **并行度必须可控**。方案自设的风控「首跑用 P=8 观测 RSS, 确认后再上 12」
         在旧签名下**根本够不着** —— n_jobs 是函数内部算死的。

    **OOM 兜底 (评审致命问题 #4)**: worker 被 OS 杀掉时 joblib 抛
    ``TerminatedWorkerError``, 旧码会让整个 stage 崩掉、几小时工作归零。这里改为
    捕获后 **loud ERROR + 整批串行重跑** —— 慢 N× 但绝不丢 run。这条兜底比任何调参
    都重要 (2026-07-27 stage 40 已经因超时闸被强杀过一次, 教训是「宁可慢, 不可归零」)。
    """
    def _serial(_ts):
        _out = []
        for _t in _ts:
            _r = worker(_t, *extra)
            if on_result is not None:
                on_result(_r)
            _out.append(_r)
        return _out

    _min = _PROC_PARALLEL_MIN_YEARS if min_tasks is None else min_tasks
    if len(tasks) < _min:
        return _serial(tasks)
    _n = _proc_workers(len(tasks)) if n_jobs is None else max(1, int(n_jobs))
    if _n <= 1:
        return _serial(tasks)
    from joblib import Parallel, delayed
    if on_result is None:
        # 老路径逐字节保留 (既有三个调用点走这条)。
        try:
            return Parallel(n_jobs=_n, prefer='processes')(
                delayed(worker)(t, *extra) for t in tasks)
        except Exception as exc:  # noqa: BLE001 — 含 TerminatedWorkerError (OOM/被杀)
            logger.error(
                f"🔴 并行执行失败 ({type(exc).__name__}: {str(exc)[:160]}) — "
                f"worker={getattr(worker, '__name__', worker)} tasks={len(tasks)} "
                f"n_jobs={_n}; **整批回落串行重跑** (慢 ~{_n}× 但不丢 run)。"
                f"常见成因: worker 被 OS 因内存杀掉 (每 worker 各持一份 jieba Trie + "
                f"sklearn 词表)。若反复出现请调低 n_jobs。")
            return _serial(tasks)

    # ── 流式路径 (on_result 给出时) ──
    # **为何需要**: 老路径把整批算完才返回, 调用方也就只能等全部结束再打日志。
    # 2026-07-28 实弹: policy_similarity 生产上这一步跑 10.57 小时, 期间 111 条
    # "LDA K=…" 是**唯一**的进度信号; 缓冲到最后再吐 ⟹ 十小时日志空白, 且一旦
    # 像 2026-07-27 那样被超时闸强杀, **缓冲的日志连同进度全部丢失**。
    # `return_as='generator'` (joblib ≥1.3) 仍按**提交序**产出, 只是边算边给 —— 顺序
    # 保证不变, 故归并序/列序/日志行序与串行完全一致。
    _done = []
    try:
        for _r in Parallel(n_jobs=_n, prefer='processes', return_as='generator')(
                delayed(worker)(t, *extra) for t in tasks):
            on_result(_r)
            _done.append(_r)
        return _done
    except Exception as exc:  # noqa: BLE001 — 含 TerminatedWorkerError (OOM/被杀)
        # 流式下已产出 len(_done) 个结果 → **只补跑剩余的**, 不整批重来。
        logger.error(
            f"🔴 并行执行失败 ({type(exc).__name__}: {str(exc)[:160]}) — "
            f"worker={getattr(worker, '__name__', worker)} tasks={len(tasks)} "
            f"n_jobs={_n}; 已完成 {len(_done)}/{len(tasks)}, "
            f"**剩余 {len(tasks) - len(_done)} 个回落串行补跑** (不丢 run, 也不重算已完成的)。"
            f"常见成因: worker 被 OS 因内存杀掉 (每 worker 各持一份 jieba Trie + "
            f"sklearn 词表)。若反复出现请调低 n_jobs。")
        _done.extend(_serial(tasks[len(_done):]))
        return _done


def _fluidity_year_worker(task, mode):
    """`_compute_fluidity` 的单年循环体 (逐字节照搬, 仅把 logger.warning 改回传)。"""
    year, df_t, df_t1 = task
    _mdf_flu = 1
    kw = (dict(analyzer='char_wb', ngram_range=(2, 4),
               max_features=5000, min_df=_mdf_flu, sublinear_tf=True)
          if mode == 'char'
          else dict(tokenizer=_jieba_tokenizer,
                    token_pattern=None,
                    max_features=5000, min_df=_mdf_flu, sublinear_tf=True))
    degraded = False
    try:
        vec = TfidfVectorizer(max_df=0.95, **kw).fit(
            pd.concat([df_t['agg_text'], df_t1['agg_text']]))
    except ValueError:
        degraded = True
        vec = TfidfVectorizer(max_df=1.0, **kw).fit(
            pd.concat([df_t['agg_text'], df_t1['agg_text']]))
    vt = _l2_normalize(vec.transform(df_t['agg_text'].values).toarray())
    vt1 = _l2_normalize(vec.transform(df_t1['agg_text'].values).toarray())

    t1_map = {b: i for i, b in enumerate(df_t1['target_bank'].values)}
    out = []
    # F41 (2026-07-31): 钉 BLAS 线程 —— `vt` 是 `.toarray()` 后的 **dense** 矩阵,
    # 故 `np.dot(vt[i], change)` 走 BLAS `ddot` (n = max_features ≤ 5000), 其归约序
    # **随线程数变**。控制组实测 (n=5000): 同线程数重复两次逐位相同, 而 1/2/4/8/16/24
    # 六档线程数只产出 **3 个不同值** (1 vs 16 差 4.26e-14)。本 worker 自 F25 起就在
    # loky 里跑, 而 joblib 给 worker 的线程数是 `cpu_count() // n_jobs` ⟹ `strat_fluidity*`
    # 的值此前一直**随并行度漂移**, 且与串行回落臂 (父进程满线程) 不同。钉 1 后收敛到
    # 与 F26/F41 同一个 canonical 值。golden-safe 同 F41: 重生协议下四个 BLAS 环境变量
    # 已 =1, 本 with 块为逐位 no-op。
    with _threadpool_limits(limits=1):
        for i, bank in enumerate(df_t['target_bank'].values):
            change = np.zeros(vt.shape[1])
            for j, other in enumerate(df_t['target_bank'].values):
                if other != bank and other in t1_map:
                    change += np.abs(vt[j] - vt1[t1_map[other]])
            d = np.linalg.norm(vt[i]) * np.linalg.norm(change)
            out.append(((bank, year),
                        float(np.dot(vt[i], change) / d) if d > 0 else np.nan))
    return out, degraded


def _tfidf_coherence_year_worker(task, mode):
    """`_compute_tfidf_coherence` 的单年循环体 (逐字节照搬)。"""
    year, df_t, df_t1 = task
    if mode == 'char':
        _kw = dict(analyzer='char_wb', ngram_range=(2, 4),
                   max_features=5000, min_df=1, sublinear_tf=True)
    else:
        _kw = dict(tokenizer=_jieba_tokenizer,
                   token_pattern=None,
                   max_features=5000, min_df=1, sublinear_tf=True)
    pooled_texts = pd.concat([df_t['agg_text'], df_t1['agg_text']],
                             ignore_index=True)
    degraded = False
    try:
        vec = TfidfVectorizer(max_df=0.95, **_kw).fit(pooled_texts)
    except ValueError:
        degraded = True
        vec = TfidfVectorizer(max_df=1.0, **_kw).fit(pooled_texts)

    vt = vec.transform(df_t['agg_text'].values)
    vt1 = vec.transform(df_t1['agg_text'].values)

    t1_map = {b: i for i, b in enumerate(df_t1['target_bank'].values)}
    out = []
    for i, bank in enumerate(df_t['target_bank'].values):
        if bank in t1_map:
            sim = cosine_similarity(vt[i:i + 1], vt1[t1_map[bank]:t1_map[bank] + 1])
            out.append(((bank, year), float(np.clip(sim[0, 0], 0.0, 1.0))))
    return out, degraded


def _lda_coherence_year_worker(task):
    """`_compute_lda_coherence` 的单年循环体 (逐字节照搬; LDA seed=42 + n_jobs=1 不变)。"""
    year, df_t, df_t1 = task
    n_t = len(df_t)
    all_texts = pd.concat([df_t['agg_text'], df_t1['agg_text']],
                          ignore_index=True).tolist()
    n_total = len(all_texts)
    K = max(10, n_total // 30)
    try:
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
            max_iter=50, learning_method='online', n_jobs=1)
        # F26: 钉 BLAS 线程 —— 既消除对机器线程数的数值依赖 (实测: 不钉时并行/串行
        # 265/277 键位模式不同; 钉后 277/277 相同), 又实测快 5.5×。
        with _threadpool_limits(limits=1):
            theta = lda.fit_transform(dtm)

        t1_map = {b: idx + n_t for idx, b in
                  enumerate(df_t1['target_bank'].values)}
        out = []
        for i, bank in enumerate(df_t['target_bank'].values):
            if bank in t1_map:
                d = jensenshannon(theta[i], theta[t1_map[bank]], base=2)
                out.append(((bank, year), float(np.clip(1.0 - d, 0.0, 1.0))))
        return out, None
    except Exception as e:  # noqa: BLE001 — 与串行同: 该年整体跳过, 回传告警文本
        return [], f"{type(e).__name__}: {e}"


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
    # F25 (2026-07-27): 逐年循环外提到 `_fluidity_year_worker` 进程并行 (见上方驱动段)。
    # 循环体逐字节照搬, 仅 max_df 降级告警改由 worker 回传、父端 emit (子进程无 handler)。
    # min_df / sublinear_tf 的既有依据 (fix omni-g-strategic-11, 2026-06-11): vectorizer
    # 全参数与 _build_tfidf_sim_matrix / _compute_tfidf_coherence 家族统一 —— log(1+tf)
    # 更贴近 HPP 2014 的准二值词使用向量 (Manning et al. 2008 §6.4)。
    fluidity = {}
    for pairs, degraded in _run_year_tasks(
            _adjacent_year_tasks(agg_df), _fluidity_year_worker, mode):
        if degraded:
            logger.warning(f"    Fluidity {mode}: max_df=0.95 词表清空, 降级为 1.0")
        fluidity.update(pairs)
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
#     [DOI 未在 chndoi.org 注册, Crossref/DataCite/doi.org 均 404; 文献待核验]
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
    # F25 (2026-07-27): 逐年循环外提到 `_tfidf_coherence_year_worker` 进程并行。
    # 本函数是 2026-07-27 归因出的第二大极 (单轨 char 28 分钟 + word 25 分钟, 三轨 ≈5h,
    # 全程仅占 1/32 核)。循环体逐字节照搬 —— 含: 池化 t/t-1 共享 IDF 权重空间、
    # max_df=0.95 词表清空时降级 1.0、clip 至真值域 [0,1] (fix omni-g-strategic-12:
    # TF-IDF 非负 → cos∈[0,1]; 高度相似文档 cos=1+ε 会崩诊断断言)。
    coherence = {}
    _tasks = _adjacent_year_tasks(agg_df)
    for (pairs, degraded), (_yr, _, _) in zip(
            _run_year_tasks(_tasks, _tfidf_coherence_year_worker, mode), _tasks):
        if degraded:
            logger.warning(f"    Coherence TF-IDF {mode} {_yr}: "
                           f"max_df=0.95 词表清空, 降级为 max_df=1.0")
        coherence.update(pairs)

    logger.info(f"    TF-IDF {mode} 连贯性: {len(coherence)} 个 Bank-Year 对")
    return coherence


# Lazy-Prices 多算子稳健性 (批 #13, 2026-06-05): 归一化编辑距离截断长度 (控 O(L²) 成本)
_LEVEN_MAX_CHARS = 2000
try:  # rapidfuzz 已在 requirements (canonicalization.py 在用); 缺失则降级 difflib
    from rapidfuzz.distance import Levenshtein as _RFLeven

    def _normalized_levenshtein(a: str, b: str) -> float:
        if not a and not b:
            return float('nan')
        return float(_RFLeven.normalized_distance(a, b))
except Exception:  # pragma: no cover - 仅依赖缺失时触发
    import difflib

    def _normalized_levenshtein(a: str, b: str) -> float:
        if not a and not b:
            return float('nan')
        return 1.0 - difflib.SequenceMatcher(None, a, b).ratio()


def _compute_lazy_distances(agg_df):
    """相邻期 (t, t-1) 文档变化量的 3 个非余弦距离 (Lazy-Prices 稳健性矩阵补充, P3)。

    【学术】Cohen, Malloy & Nguyen (2020) JF 75(3):1371-1415 "Lazy Prices": 用多种文本
    距离度量同一主体相邻期文档的"改动量"。核心余弦构念本项目已由 coh_* 覆盖 (故 P3 降级),
    此处仅补 Jaccard / 词重叠 / 归一化编辑距离 3 个并列算子, 作多算子稳健性矩阵。

    【白话】对每家银行, 看它今年和去年的"年度文本"差了多少 —— 用三把不同的尺子量"改动量"
    (词集不重合度、最小集合不重合度、逐字编辑距离)。距离越大=年际措辞改得越多。

    距离 = 1 − 相似度; 首年/年份间隙 → 缺失。Levenshtein 对长文 O(L²), 截断到
    _LEVEN_MAX_CHARS (全量长文须抽样/限长, 见缺口报告 G6 caveat)。

    披露 (omni-g-strategic-14, 2026-06-11): minedit 仅对聚合文档前
    _LEVEN_MAX_CHARS=2000 字**前缀**计算, 而前缀 = groupby 保序拼接的头部文章
    (组内不按日期排序, 内容取决于上游 parquet 行序) → 实质度量"两个任意头部
    文章片段的编辑距离", 上游重排/去重即改值; 盘上实测近天花板 (mean≈0.95,
    变异极小, 即任意两段不同中文前缀的噪声)。回归端优先用全文 token 集的
    jaccard/overlap 算子; minedit 仅作多算子矩阵的披露性补充, 勿单独入主回归。

    Returns:
        dict[(bank, year)] -> {'jaccard': d, 'overlap': d, 'minedit': d}
    """
    out = {}
    bank_year_text = {(r['target_bank'], r['year']): r['agg_text']
                      for _, r in agg_df.iterrows()}
    for (bank, year), text_t in bank_year_text.items():
        text_t1 = bank_year_text.get((bank, year - 1))
        if text_t1 is None:
            continue  # 首年/间隙 → 缺失 (与 coherence 同口径)
        set_t = set(_jieba_tokenizer(text_t))
        set_t1 = set(_jieba_tokenizer(text_t1))
        union = set_t | set_t1
        inter = set_t & set_t1
        jaccard_sim = (len(inter) / len(union)) if union else float('nan')
        min_sz = min(len(set_t), len(set_t1))
        overlap_sim = (len(inter) / min_sz) if min_sz > 0 else float('nan')
        out[(bank, year)] = {
            'jaccard': (1.0 - jaccard_sim) if jaccard_sim == jaccard_sim else float('nan'),
            'overlap': (1.0 - overlap_sim) if overlap_sim == overlap_sim else float('nan'),
            'minedit': _normalized_levenshtein(text_t[:_LEVEN_MAX_CHARS],
                                               text_t1[:_LEVEN_MAX_CHARS]),
        }
    return out


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

    确定性 (fix(omni-g-strategic-16), 2026-06-11): random_state=42, max_iter=50,
    learning_method='online', n_jobs=1 (与 _build_lda_jsd_matrix 一致)。
    可复现性来自 random_state + 单线程 E-step; 原 n_jobs=-1 的核数依赖切片
    求和使 θ 跨机漂移 (实测 max|Δθ|≈0.99), 与旧注释"保证可复现性"相反
    (机制详见 _build_lda_jsd_matrix docstring "确定性" 段)。

    Args:
        agg_df: _aggregate_bank_year_texts 的输出

    Returns:
        dict: {(bank, year): coherence ∈ [0,1]}, 首年/间隙年 → 缺失
    """
    # F25+F26 (2026-07-27): 逐年循环外提到 `_lda_coherence_year_worker` 进程并行。
    #
    # 排查经过 (留证, 勿删): 首版 A/B (2007-2011, 277 个 bank-year 键) 抓到并行臂与串行臂
    # **265/277 个值位模式不同** (~1e-13, 如 0.39496233027673233 vs ...76686)。根因探针
    # 确证 = **BLAS 线程数差异** (loky worker 默认钉 1, 父进程用满线程), 非并行本身:
    # 在全 BLAS 钉 1 环境下同一对照 **277/277 逐位相同**。同批 A/B 里 TF-IDF 连贯性与
    # fluidity 均逐位相同 —— 稀疏/简单 numpy 路径不吃这个。
    #
    # 因此正解不是放弃并行, 而是 F26: 在 worker 的 LDA fit 现场 `threadpool_limits(1)`,
    # 令其**与环境无关**地取 golden 协议下的那个值 ⟹ 父/子进程算的是同一个 canonical 值
    # ⟹ 并行安全; 且顺带实测快 5.5×。
    # ⚠ LDA 的 `n_jobs=1` (fix omni-g-strategic-16) **原样保留** —— 并行发生在**年之间**,
    #   不发生在 LDA 内部, 那次修复完好无损。
    coherence = {}
    _tasks = _adjacent_year_tasks(agg_df)
    for (pairs, err), (_yr, _, _) in zip(
            _run_year_tasks(_tasks, _lda_coherence_year_worker), _tasks):
        if err:
            logger.warning(f"    LDA 连贯性 {_yr}: {err}, 跳过")
        coherence.update(pairs)
    # ⚠ 原串行循环体已整体搬进 `_lda_coherence_year_worker` (逐字节照搬), 含既有披露:
    #   主题数 K=max(10, n_total//30) 的基数是**两年池** n_total (≈2×单年银行数), 与
    #   `_build_lda_jsd_matrix` 的单年 n_banks 基数**不同**; 当前两处同被 max(10,·)
    #   兜底为常数 10, >165 银行/年时将分叉 (omni-g-strategic-06, 2026-06-11 —
    #   原注释"与 _build_lda_jsd_matrix 一致"仅因兜底巧合成立)。

    logger.info(f"    LDA+JSD 连贯性: {len(coherence)} 个 Bank-Year 对")
    return coherence


def _compute_emb_coherence(agg_df, spec=None):
    """稠密语义嵌入的相邻期文本连贯性 (spec 参数化, 逐轨复用于三轨 full/ctx/ss; 默认主轨)。

    【学术】使用预训练语言模型 (Qwen / OpenAI Embedding) 将文本映射到
    高维语义空间, 计算 cosine similarity。与 TF-IDF 的词袋假设不同,
    Embedding 捕获词序和上下文语义 (Guzman & Li 2023, Management Science)。

    【白话】让 AI "读懂" 每年的文本画像, 把理解结果变成一串数字(向量),
    然后比较今年和去年的"理解"有多接近。AI 比 TF-IDF 更"聪明",
    能理解同义词和上下文, 但计算更慢(需要调用 API)。

    效率: 一次性获取所有 Bank-Year 嵌入，长文本复用分段池化逻辑；
    避免逐对调用。降级: 统一 API 引擎 (MAIN 致命错 fail-fast raise / _lg twin 异常降 None)
    → 返回空 dict (v3.14.0 起已无 sentence-transformers 本地轨)。

    值域 (fix(omni-g-strategic-03/12), 2026-06-11): embedding 余弦真值域
    **[-1,1]** (非 TF-IDF/LDA 的 [0,1]) — 落值 clip 至 [-1,1] 仅作浮点容忍
    (float32 余弦误差 ~1e-7), 合法负余弦**保留不删失**; 下游
    _log_coherence_diagnostics 对 coh_emb* 按 [-1,1] 断言。

    Args:
        agg_df: _aggregate_bank_year_texts 的输出

    Returns:
        dict: {(bank, year): coherence ∈ [-1,1]}, 首年/间隙年 → 缺失
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
            # fix(omni-g-strategic-03/12, 2026-06-11): clip 至 emb 真值域 [-1,1]
            # 仅作浮点容忍 (float32 cos 可 1+ε, ε~1e-7 > 断言容差 1e-10 →
            # 原裸值+硬断言 [0,1] 是 latent 崩溃); 负余弦保留, 不删失到 0
            coherence[(bank, year)] = float(np.clip(sim[0, 0], -1.0, 1.0))

    logger.info(f"    Embedding 连贯性: {len(coherence)} 个 Bank-Year 对")
    return coherence


def _log_coherence_diagnostics(panel):
    """输出连贯性四方法相关矩阵 + 值域断言。

    【白话】连贯性的"质量检查"函数:
      1. 四种方法 (TF-IDF char/word, LDA, Embedding) 的结果是否大致一致
         — 如果四种方法都说某银行的沟通很连贯, 说明结论可靠
      2. 与情感变量 (llm_vote_tone_full) 相关性低 → 确认正交性
         — 连贯性衡量"稳定性", 情感衡量"内容", 二者应独立
      3. 值域检查 (fix(omni-g-strategic-03), 2026-06-11): coh_emb*
         (embedding 余弦) ∈ [-1,1], 其余 (TF-IDF/LDA) ∈ [0,1] —
         原对全部 coh_* 断言 [0,1], 对 emb 轨的合法负余弦数学上不成立
         (latent AssertionError 崩 stage 45)
    """
    # 四方法收敛效度 (Full 轨)
    coh_cols = [c for c in ['coh_tfidf_c_full', 'coh_tfidf_w_full',
                            'coh_lda_full', 'coh_emb_full']
                if c in panel.columns]
    if len(coh_cols) >= 2:
        logger.info(f"  连贯性四方法相关矩阵:\n"
                    f"{panel[coh_cols].corr().round(4).to_string()}")
        # 多方法一致性摘要 (round 7 富集): 相关矩阵上三角 |r| 的中位/极差 sig4 量化收敛效度;
        # 纯日志诊断 (throwaway 局部变量, 不入 panel/产物), golden-safe。
        try:
            _cm = panel[coh_cols].corr().to_numpy()
            _iu = np.triu_indices_from(_cm, k=1)
            _offdiag = np.abs(_cm[_iu])
            _offdiag = _offdiag[~np.isnan(_offdiag)]
            if _offdiag.size:
                _med_r = float(np.median(_offdiag))
                _cv = ("✅ 多法高度收敛" if _med_r >= 0.7
                       else ("中度收敛" if _med_r >= 0.4 else "⚠ 多法弱收敛(测度信号分歧)"))
                logger.info(f"    四方法收敛效度: |r| 中位={sig4(_med_r)} "
                            f"范围=[{sig4(float(_offdiag.min()))}, {sig4(float(_offdiag.max()))}] "
                            f"(n_pair={_offdiag.size:,d}) → {_cv}")
        except Exception as _cv_exc:  # noqa: BLE001
            logger.warning(f"  连贯性收敛效度摘要失败 (不阻塞): {_cv_exc!r}")

    # 正交性验证: 与情感变量的相关系数 (期望 |r| < 0.3)
    tone_col = 'llm_vote_tone_full'
    if tone_col in panel.columns and len(coh_cols) >= 1:
        for cc in coh_cols:
            valid = panel[[cc, tone_col]].dropna()
            if len(valid) > 5:
                r = valid[cc].corr(valid[tone_col])
                logger.info(f"    {cc} ↔ {tone_col}: r = {sig4(r)} "
                            f"({'✅ 正交' if abs(r) < 0.3 else '相关偏高'})")

    # 值域断言 (fix(omni-g-strategic-03), 2026-06-11): coh_emb* (embedding 余弦,
    # 真值域 [-1,1]) 下界放宽到 -1; 其余 (TF-IDF/LDA, 非负算子) 维持 [0,1]
    for col in [c for c in panel.columns if c.startswith('coh_')]:
        v = panel[col].dropna()
        if len(v) > 0:
            lo = -1.0 if col.startswith('coh_emb') else 0.0
            assert (v >= lo - 1e-10).all() and (v <= 1 + 1e-10).all(), \
                f"{col} 超出 [{lo:g},1] 值域: min={sig4(v.min())}, max={sig4(v.max())}"


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
          (N=5 为基准, N∈{3,4,6,7}∪{10,20,30,40,50} 为敏感性检验)

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
      3. N-最近邻聚合 → Ŝ_i (N∈{3,4,5,6,7}∪_TOPK_NN for TF-IDF char/word; {5}∪_TOPK_NN for LDA/Embedding; _TOPK_NN={10,20,30,40,50})
      4. 全行业向量法 → 1 - cos(vec_i, centroid) (谢佳松 2025, 经济研究)
      5. 计算 Fluidity → Hoberg et al. (2014, JF, Eq. 2)
      6. Ctx / Ss 轨三轨对比 → 上下文窗口 (content_ctx) / 银行+金科同句共现
         (content_ss) 文本各重跑 N-NN(N=5) + centroid (ss 缺列优雅跳过)
      7. 合并到面板并执行六方法收敛效度诊断

    Args:
        df_exploded: 文章-银行级 DataFrame
        panel: 银行-年面板 DataFrame

    Returns:
        panel: 新增 ~50 列战略差异度指标的面板 DataFrame
          (含 N-NN Full/Ctx/Ss, centroid Full/Ctx/Ss, fluidity, 连贯性,
           及 co-primary _lg 嵌入 twin 列 strat_diff_*_lg / centroid_diff_emb_lg / coh_emb_lg / strat_diff_lg_{full,ctx,ss})
    """
    logger.info("=" * 60)
    logger.info("战略差异度指数 (Guzman & Li 2023; Hoberg & Phillips 2016)")
    logger.info("=" * 60)

    # ── 子步骤 banner (called-by-runner helper, 共享 40_build_panel 日志; ENV/CONFIG
    #    由 runner 入口负责, 此处只打 step 名 + 方法依据引文 + 本步配置/判读) ──
    # 失败包 try/except, 日志块绝不崩阶段 (playbook §1)。
    import time as _time  # 仅服务于本步 per-phase 计时
    _t_entry = _time.time()
    try:
        logger.info("  ┌─ 子步骤: 金融科技战略差异度指数 (FinTech Strategic Differentiation)")
        logger.info("  │  功能: (银行,年) 聚合新闻文档 → 4 法文本距离矩阵 → N-最近邻聚合 Ŝ_i")
        logger.info("  │        + 全行业质心距离 + Fluidity + 相邻期连贯性; 三轨 full/ctx/ss 互为稳健性")
        logger.info("  │  确定性/成本: 本地 TF-IDF/LDA $0 确定 (LDA n_jobs=1+seed=42 逐位可复现);")
        logger.info("  │        Embedding 主轨 (Qwen/Qwen3-Embedding-8B) 缓存命中 $0, 缺失才付费;")
        logger.info("  │        co-primary _lg (text-embedding-3-large API) 缓存命中 $0, 缺失才付费;")
        logger.info("  │        离线 NEWS_PROCESS_LLM_OFFLINE=1 时 miss→raise 零网络 (受统一引擎离线闸约束)")
        logger.info("  │  📖 方法论依据 (核心构念 → 学术出处, emit 进日志):")
        logger.info("  │   · N-最近邻战略差异度 Ŝ_i=(1/N)Σδ_ij: Guzman, J., & Li, A. (2023). "
                    "Measuring founding strategy. Management Science, 69(1), 101-118. "
                    "https://doi.org/10.1287/mnsc.2022.4369")
        logger.info("  │   · 逐年文本相似度网络 (TNIC): Hoberg, G., & Phillips, G. (2016). "
                    "Text-based network industries and endogenous product differentiation. "
                    "Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176")
        logger.info("  │   · Fluidity 竞争流动性: Hoberg, G., Phillips, G., & Prabhala, N. (2014). "
                    "Product market threats, payouts, and financial flexibility. The Journal of "
                    "Finance, 69(1), 293-324. https://doi.org/10.1111/jofi.12050")
        logger.info("  │   · 文本创新度量: Bellstam, G., Bhagat, S., & Cookson, J. A. (2021). "
                    "A text-based analysis of corporate innovation. Management Science, 67(7), "
                    "4004-4031. https://doi.org/10.1287/mnsc.2020.3682")
        logger.info("  │   · JSD 主题分布距离: Lin, J. (1991). Divergence measures based on the "
                    "Shannon entropy. IEEE Transactions on Information Theory, 37(1), 145-151. "
                    "https://doi.org/10.1109/18.61115")
        logger.info("  │   · TF-IDF 词权与 sublinear tf: Manning, C. D., Raghavan, P., & Schütze, H. "
                    "(2008). Introduction to information retrieval. Cambridge University Press. "
                    "https://doi.org/10.1017/CBO9780511809071")
        logger.info("  │   · term-weighting 经典依据: Salton, G., & Buckley, C. (1988). "
                    "Term-weighting approaches in automatic text retrieval. Information Processing "
                    "& Management, 24(5), 513-523. https://doi.org/10.1016/0306-4573(88)90021-0")
        logger.info("  │   · 稠密语义向量 (Embedding 轨): Reimers, N., & Gurevych, I. (2019). "
                    "Sentence-BERT: Sentence embeddings using Siamese BERT-networks. In Proceedings "
                    "of the 2019 Conference on Empirical Methods in Natural Language Processing and "
                    "the 9th International Joint Conference on Natural Language Processing "
                    "(EMNLP-IJCNLP) (pp. 3980-3990). Association for Computational Linguistics. "
                    "https://doi.org/10.18653/v1/D19-1410")
        logger.info("  │   · 文本数据方法论 (分词/停用词): Gentzkow, M., Kelly, B., & Taddy, M. (2019). "
                    "Text as data. Journal of Economic Literature, 57(3), 535-574. "
                    "https://doi.org/10.1257/jel.20181020")
        logger.info("  │   · 相邻期连贯性: 欧阳志刚 & 胡雯华 (2024). 数量经济技术经济研究, 41(10), "
                    "69-88 (DOI 待核验, chndoi.org 未注册, 不作已证事实引用)")
        logger.info("  │   · 战略差异度近期应用 (TNIC 式技术差异/niche): Arts, S., Cassiman, B., "
                    "& Hou, J. (2025). Technology differentiation, product market rivalry, and "
                    "M&A transactions. Strategic Management Journal, 46(4), 837-862. "
                    "https://doi.org/10.1002/smj.3687")
        logger.info("  │     (白话: 用文本网络定位企业技术空间组合的唯一性, 把 TNIC 式 niche / "
                    "战略距离用于并购市场, 是本模块 Guzman-Li / Hoberg-Phillips 构念的近期应用)")
        logger.info("  │   · 最优独特性 / 战略生态位定位 (niche positioning): Su, J., Gao, X., & Tan, J. "
                    "(2024). Positioning for optimal distinctiveness: How firms manage competitive and "
                    "institutional pressures under dynamic and complex environment. Strategic Management "
                    "Journal, 45(2), 333-361. https://doi.org/10.1002/smj.3549")
        logger.info("  │     (白话: 企业如何在竞争与制度压力下定位'最优独特性', 直接锚定本模块 Ŝ_i "
                    "战略生态位 (strategic niche) 距离的构念)")
        logger.info("  │   · 数字化驱动的差异化战略变迁 (text-based 差异化测度): Miller, C. D., & "
                    "Wang, R. D. (2024). Product digitization and differentiation strategy change: "
                    "Evidence from the book publishing industry. Strategic Management Journal, 45(7), "
                    "1241-1272. https://doi.org/10.1002/smj.3586")
        logger.info("  │     (白话: 用文本测度数字化如何改变企业差异化战略, 与本模块以金科(数字化)新闻 "
                    "文本测度银行战略差异度同范式的近期应用)")
        logger.info("  │   · Embedding 轨金融语义嵌入近期应用: Jha, M., Liu, H., & Manela. (2026). "
                    "Does finance benefit society? A language embedding approach. The Review of "
                    "Financial Studies, 39(5), 1227–1266. https://doi.org/10.1093/rfs/hhaf012")
        logger.info("  │     (白话: 以 language embedding 用 BERT 嵌入测金融文本语义立场, 与本模块 "
                    "Embedding 轨 / _lg co-primary twin 同范式的最新金融应用)")
        logger.info("  │   · Embedding 轨金融域适配: Jehnen, S., Villalba-Díez, J., & "
                    "Ordieres-Meré, J. (2026). FinTextSim: A domain-specific sentence-transformer "
                    "for extracting predictive latent topics from financial disclosures. Frontiers "
                    "in Artificial Intelligence, 9, Article 1752103. "
                    "https://doi.org/10.3389/frai.2026.1752103")
        logger.info("  │     (白话: 对金融披露文本微调 sentence-transformer, 直接对标本模块 "
                    "SBERT / Embedding 轨在金融域的适配方向)")
        logger.info("  │   · Embedding co-primary 双模型互证依据 (金融文本嵌入横向基准): Tang, Y., & "
                    "Yang, Y. (2025). FinMTEB: Finance Massive Text Embedding Benchmark. In Proceedings "
                    "of the 2025 Conference on Empirical Methods in Natural Language Processing "
                    "(pp. 3620-3638). Association for Computational Linguistics. "
                    "https://doi.org/10.18653/v1/2025.emnlp-main.179")
        logger.info("  │     (白话: 金融文本嵌入基准对多模型横向评测, 锚定本模块 MAIN(Qwen) ⟂ _lg(large) "
                    "co-primary 跨厂商双模型 both-or-neither parity 稳健性设计)")
    except Exception as _banner_exc:  # noqa: BLE001
        logger.warning(f"  战略差异度 banner 日志失败 (不阻塞): {_banner_exc!r}")

    # 【白话】N_LIST 表示分别看最像的 3/4/5/6/7 家同行, 外加 10/20/30/40/50 家 (大邻域)
    #   N=5 是论文推荐的基准值，其余 (含 _TOPK_NN 大 N) 是"换个数字看结果是否稳定" (互为稳健性、不分主次)
    # fix(topk-n-expansion, 2026-07-02): 追加 _TOPK_NN=[10,20,30,40,50] (SSOT, 见模块顶部常量);
    #   TF-IDF char/word full 轨的 N 集 = 既有 {3,4,5,6,7} ∪ _TOPK_NN。LDA/emb/lg 及 ctx/ss 轨
    #   同步扩 (各自 {5} ∪ _TOPK_NN), 见下方各方法 compute 调用与 emit 循环。
    N_LIST = [3, 4, 5, 6, 7] + _TOPK_NN
    # fix(topk-n-expansion, 2026-07-02): LDA/Embedding(Qwen)/Embedding(large _lg) 三方法的 N 集
    #   = 既有基准 {5} ∪ _TOPK_NN (这些方法历史上只跑 n5, 现追加大 N)。emb 与 _lg **共用此列表**
    #   以保 co-primary both-or-neither 列名双射 (见 _compute_nn_scores 调用与 emit 循环)。
    LDA_EMB_N_LIST = [5] + _TOPK_NN
    # fix(omni-g-strategic-09, 2026-06-11): 共提及文章 1/n_banks 降权稳健开关
    # (config strategic_diff.co_mention_downweight, 默认 False = 维持原口径;
    # 详见 _aggregate_bank_year_texts / 模块 docstring 局限性 4)
    _co_dw = bool(CONFIG.get('strategic_diff', {})
                  .get('co_mention_downweight', False))
    # 第一步: 把所有新闻按 (银行, 年) 合并成"年度总结"大文档
    # fix(completeness-04): full 轨读 content_full(含标题), 与 ctx 轨(content_ctx)对称;
    # 原默认裸 '内容'(无标题) 致 full↔ctx 不对称 (病根A 同型, 见 :339 注释)。
    _full_text_col = 'content_full' if 'content_full' in df_exploded.columns else '内容'
    # ── 本步配置快照 (helper 读取的可调参数; 输入/输出路径由 runner 入口已打) ──
    try:
        _emb_main = (EMBEDDING_CONFIG.get('model') or 'Qwen/Qwen3-Embedding-8B') if EMBEDDING_CONFIG else 'Qwen/Qwen3-Embedding-8B'
        _emb_lg = (_LARGE_SPEC.get('model') or '(text-embedding-3-large)') if _LARGE_SPEC else '(未启用)'
        logger.info(
            f"  │  ⚙ 配置: N_LIST={N_LIST} (基准 N=5) · co_mention_downweight={_co_dw} · "
            f"full轨文本列='{_full_text_col}' · 主嵌入='{_emb_main}' · co-primary _lg='{_emb_lg}' · "
            f"emb单条上限={_EMB_MAX_TOKENS:,d} tok · 批上限={_EMB_MAX_TOKENS_PER_REQUEST:,d} tok")
        logger.info(
            "  └─ 值域口径: TF-IDF/LDA 距离∈[0,1]; Embedding 相似度∈[-1,1], 距离δ=1−cos∈[0,2]; "
            "LDA n_jobs=1+seed=42 (跨机逐位可复现)")
    except Exception as _cfg_exc:  # noqa: BLE001
        logger.warning(f"  战略差异度 config 日志失败 (不阻塞): {_cfg_exc!r}")
    agg_df = _aggregate_bank_year_texts(df_exploded, text_col=_full_text_col,
                                        co_mention_downweight=_co_dw)
    all_results = []  # 用来收集所有年度、所有银行的计算结果

    # 【白话】逐年计算 — 每一年独立建模，不跨年混合
    #   这样做是因为金融科技领域变化很快，2020年的"热词"和2024年可能完全不同
    # S13 (2026-07-31): 计算段下沉到 `_strat_year_worker` 并逐年进程并行; 本处只剩
    # 「回放日志 + 装配行」。任务切分/结果回收均按 `sorted(year)` 提交序 ⟹ 日志行序、
    # all_results 行序、列值均与串行逐字节一致 (F28 塌缩告警亦在其原位置)。
    _tasks_full = _strat_year_tasks(agg_df, 'Full', '')
    _bon_tail_full = ("该年 {n} 家银行的 strat_diff_n*_emb / strat_sim_max_emb / "
                      "centroid_diff_emb / strat_diff_full 及其 _lg 孪生一并置 NaN")
    for (_payload, _logs), _task in zip(
            _run_strat_year_tasks(
                _tasks_full, N_LIST, LDA_EMB_N_LIST, True,
                "    LDA+JSD 失败 ({exc}), 跳过", _bon_tail_full),
            _tasks_full):
        for _lvl, _msg in _logs:
            logger.log(_lvl, _msg)
        if _payload is None:
            continue
        banks = _task[3]
        year = _task[2]
        sc, sw, sl = _payload['sc'], _payload['sw'], _payload['sl']
        se, se_lg = _payload['se'], _payload['se_lg']
        cd_c, cd_w, cd_lda = _payload['cd_c'], _payload['cd_w'], _payload['cd_lda']
        cd_emb, cd_emb_lg = _payload['cd_emb'], _payload['cd_emb_lg']

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
            # fix(topk-n-expansion, 2026-07-02): LDA/emb/lg 由单 n5 改 for-N 多列写出
            #   (N∈LDA_EMB_N_LIST={5}∪_TOPK_NN); sim_max N-independent 仍每方法一列。
            if sl:  # LDA 方法成功时才有
                for N in LDA_EMB_N_LIST:
                    row[f'strat_diff_n{N}_lda'] = sl[f'n{N}'].get(bank, np.nan)
                row['strat_sim_max_lda'] = sl['sim_max'].get(bank, np.nan)
            if se:  # Embedding 主轨 (Qwen) 成功时才有
                for N in LDA_EMB_N_LIST:
                    row[f'strat_diff_n{N}_emb'] = se[f'n{N}'].get(bank, np.nan)
                row['strat_sim_max_emb'] = se['sim_max'].get(bank, np.nan)
            if se_lg:  # co-primary 嵌入 (_lg=text-embedding-3-large); 与 emb 严格同 N 列表保 parity
                for N in LDA_EMB_N_LIST:
                    row[f'strat_diff_n{N}_emb_lg'] = se_lg[f'n{N}'].get(bank, np.nan)
                row['strat_sim_max_emb_lg'] = se_lg['sim_max'].get(bank, np.nan)
            # 全行业向量法 Full 轨 (谢佳松 2025, 经济研究, 图1/表2)
            row['centroid_diff_tfidf_c'] = cd_c[bank]
            row['centroid_diff_tfidf_w'] = cd_w[bank]
            if cd_lda:
                row['centroid_diff_lda'] = cd_lda.get(bank, np.nan)
            if cd_emb:
                row['centroid_diff_emb'] = cd_emb.get(bank, np.nan)
                # code-review P1-3: MAIN 契约别名 strat_diff_full (= centroid_diff_emb 逐值别名),
                # 与 _lg 的 strat_diff_lg_full 对称 → co-primary 列名双射 (无孤儿 _lg)。
                row['strat_diff_full'] = cd_emb.get(bank, np.nan)
            if cd_emb_lg:  # co-primary 嵌入 + 契约别名 strat_diff_lg_full
                row['centroid_diff_emb_lg'] = cd_emb_lg.get(bank, np.nan)
                row['strat_diff_lg_full'] = cd_emb_lg.get(bank, np.nan)
            all_results.append(row)

    # 【白话】Fluidity: 衡量竞争者是否在向你的"领地"移动
    #   char/word 双模式 = 用两种不同的文本分析方法各算一遍
    flu_c = _compute_fluidity(agg_df, 'char')
    flu_w = _compute_fluidity(agg_df, 'word')

    # 【白话】最终组装: 把所有计算结果合并到面板数据里
    #   面板(panel) = 每行是一家银行的一年，这里把差异度分数填进去
    if all_results:
        res = pd.DataFrame(all_results)
        # 用银行名+年份做"钥匙"，把新列合并到面板
        panel = panel.merge(res, on=['target_bank', 'year'], how='left')
        logger.info(f"  ✅ 战略差异度: 成功合并 {len(res):,d} 行, "
                    f"新增 {len(res.columns) - 2:,d} 列")
    else:
        logger.warning("  无有效结果 (所有年度银行数不足 3)")
    # fix(omni-g-strategic-13, 2026-06-11): fluidity 落列独立于 NN ≥3 银行闸门 —
    # 原经 res (行集 ⊂ 通过闸门的年份) 附着, <3 银行年份已算出的 fluidity 被
    # 静默丢弃; 全年份失败时列根本不创建。fluidity 仅要求 t-1 非空 (2 家银行
    # 即可定义), 故直接以 panel 为骨架附着, 与 coh_* 落列口径一致。
    panel['strat_fluidity'] = panel.apply(
        lambda r: flu_c.get((r['target_bank'], r['year']), np.nan), axis=1)
    panel['strat_fluidity_w'] = panel.apply(
        lambda r: flu_w.get((r['target_bank'], r['year']), np.nan), axis=1)
    # 跑诊断: 检查四种方法的结果是否大致一致（收敛效度）+ 分族值域断言
    _log_robustness_diagnostics(panel)

    # ══════════════════════════════════════════════════════════════════
    # 改进 B: 相邻期文本连贯性 (欧阳志刚 & 胡雯华 2024)
    # ══════════════════════════════════════════════════════════════════
    # 【学术】欧阳志刚 & 胡雯华 (2024, 数量经济技术经济研究, §三(三)2.(2)):
    #   余弦相似度 → 连贯性 → 降低不确定性 → 提升传导效率
    # 【白话】看每家银行今年和去年的新闻有多像, 越像说明沟通越稳定
    logger.info("=" * 60)
    logger.info("相邻期文本连贯性 (欧阳志刚 & 胡雯华 2024)")
    logger.info("=" * 60)

    # 三轨 (full/ctx/ss) 连贯性:
    # Full 轨: 复用本函数顶部已生成的 agg_df (避免冗余聚合)
    # Ctx 轨: 新建聚合 (使用 content_ctx 列)
    # Ss  轨: 新建聚合 (使用 content_ss 列, 银行+金科同句共现; 回退镜像 ctx→全文)
    tracks = [('_full', agg_df)]
    if 'content_ctx' in df_exploded.columns:
        agg_ctx = _aggregate_bank_year_texts(df_exploded, text_col='content_ctx',
                                             co_mention_downweight=_co_dw)
        tracks.append(('_ctx', agg_ctx))
    else:
        logger.warning("  连贯性 _ctx: 列 'content_ctx' 不存在, 跳过 Ctx 轨道")
    # ss 轨守卫镜像 ctx: content_ss 缺失则优雅跳过 (graceful skip)
    if 'content_ss' in df_exploded.columns:
        agg_ss = _aggregate_bank_year_texts(df_exploded, text_col='content_ss',
                                            co_mention_downweight=_co_dw)
        tracks.append(('_ss', agg_ss))
    else:
        logger.warning("  连贯性 _ss: 列 'content_ss' 不存在, 跳过 Ss 轨道")

    # 📖 方法论依据 (emit 进运行期日志, 让 .log 自证): 下方轨道循环内
    #   _compute_lazy_distances 为 full/ctx/ss 各落 lazy_jaccard / lazy_overlap /
    #   lazy_minedit (3 轨 × 3 算子 = 9 列) —— 相邻期 (t, t-1) 文档"改动量"的
    #   Jaccard / 集合重叠 / 归一化编辑距离三算子, 直接复用 Cohen-Malloy-Nguyen
    #   的多距离 adjacent-period document-change 方法论 (核心余弦构念已由 coh_* 覆盖)。
    # 【白话】对每家银行比较今年 vs 去年的"年度文本"用三把不同尺子量改了多少,
    #   思路源自该文 "公司年报改动越少越像在偷懒(lazy)" 的文档变化度量。
    logger.info("  📖 相邻期文档变化多算子 (lazy_jaccard/overlap/minedit): "
                "Cohen, L., Malloy, C., & Nguyen, Q. (2020). Lazy prices. "
                "The Journal of Finance, 75(3), 1371-1415. "
                "https://doi.org/10.1111/jofi.12885")

    for track_suffix, agg_track in tracks:
        if agg_track.empty:
            continue
        logger.info(f"  轨道{track_suffix}: {len(agg_track):,d} 个 Bank-Year 文档")

        coh_tc  = _compute_tfidf_coherence(agg_track, 'char')
        coh_tw  = _compute_tfidf_coherence(agg_track, 'word')
        coh_lda = _compute_lda_coherence(agg_track)
        coh_emb = _compute_emb_coherence(agg_track)            # 主轨 (Qwen)
        _coh_pairs = [
            (f'coh_tfidf_c{track_suffix}', coh_tc),
            (f'coh_tfidf_w{track_suffix}', coh_tw),
            (f'coh_lda{track_suffix}',     coh_lda),
            (f'coh_emb{track_suffix}',     coh_emb),
        ]
        # co-primary 嵌入 coh_emb_lg (_lg=text-embedding-3-large; v3.14.0 起 ACTIVE)
        if _LARGE_SPEC:
            coh_emb_lg = _compute_emb_coherence(agg_track, spec=_LARGE_SPEC)
            # both-or-neither parity: MAIN 与 _lg coherence 任一嵌入失败 (空 dict)
            # → 两者同族 coh 列一并空, 不留单边孤儿列。
            if not coh_emb or not coh_emb_lg:
                # 🔴 F28 留痕 (2026-07-28): 本分支在 2026-07-27 生产跑里**静默**触发了
                # 两次 —— ctx 轨 16:40:30、ss 轨 18:24:44, 主轨 Qwen 嵌入在 429/TPM 风暴下
                # 重试 80 次耗尽返回 None, 连坐把**已算成功的 _lg 结果一并丢弃**,
                # 导致交付面板 coh_emb_{ctx,ss} 与 coh_emb_lg_{ctx,ss} 四列 23,693 行全 NaN
                # (共丢 4 × 3,891 = 15,564 个应有值), 而阶段照常打印「✅ 新增 15 列」、
                # 管道报「✓ 全部阶段执行成功」、EXIT=0 —— 28 小时无人察觉。
                # 本块**不改任何数值语义** (值仍按 both-or-neither 同置空), 只把静默变成
                # 可检出: ERROR 级 + 逐列点名 + 点明被丢弃的成功臂规模。配合 F29
                # (孤儿模块 ERROR 落地), `grep -c " - ERROR - "` 这条验收判据才第一次
                # 对本类数据丢失有效。
                # ⚠ 「失败一臂时保留另一臂」属**改值语义**, 与 CLAUDE.md「两轨严格 parity
                #   (both-or-neither)」铁律正面冲突, 属研究口径变更, 须用户裁定后另案实施。
                _failed = [n for n, d in (('MAIN(Qwen)', coh_emb),
                                          ('_lg(large)', coh_emb_lg)) if not d]
                _kept = [(n, len(d)) for n, d in (('MAIN(Qwen)', coh_emb),
                                                  ('_lg(large)', coh_emb_lg)) if d]
                _cols = f'coh_emb{track_suffix}, coh_emb_lg{track_suffix}'
                logger.error(
                    f"🔴 嵌入连贯性 both-or-neither 塌缩 [轨道{track_suffix or '_full'}]: "
                    f"失败臂={'+'.join(_failed)}; "
                    f"被连坐丢弃的**已成功**结果="
                    f"{', '.join(f'{n} {c:,d} 个值' for n, c in _kept) or '无'}; "
                    f"受影响列 (2 列将全 NaN): {_cols}"
                )
                logger.error(
                    f"   ⚠ 后果: 该轨嵌入连贯性在面板中不可用 (三轨互为稳健性梯子缺 1/3); "
                    f"且因同批文本随后可能被成功嵌入并入缓存, **重跑会填上这两列** "
                    f"⟹ 本次交付产物不可复现。根因通常是嵌入 API 重试耗尽 "
                    f"(见同期 embedding_engine 的 '重试 80 次仍失败' ERROR)。"
                )
                coh_emb, coh_emb_lg = {}, {}
                _coh_pairs[-1] = (f'coh_emb{track_suffix}', coh_emb)
            _coh_pairs.append((f'coh_emb_lg{track_suffix}', coh_emb_lg))

        for name, coh_dict in _coh_pairs:
            # d=coh_dict: 默认参数绑定避免 Python 闭包延迟绑定陷阱 (审阅问题 9)
            panel[name] = panel.apply(
                lambda r, d=coh_dict: d.get(
                    (r['target_bank'], r['year']), np.nan),
                axis=1)

        # Lazy-Prices 3 补充距离 (批 #13, P3): 同 t/t-1 配对, 补 coh_* 余弦之外的算子
        lazy = _compute_lazy_distances(agg_track)
        for _dk, _col in [('jaccard', f'lazy_jaccard{track_suffix}'),
                          ('overlap', f'lazy_overlap{track_suffix}'),
                          ('minedit', f'lazy_minedit{track_suffix}')]:
            panel[_col] = panel.apply(
                lambda r, k=_dk, d=lazy: d.get(
                    (r['target_bank'], r['year']), {}).get(k, np.nan),
                axis=1)

    _log_coherence_diagnostics(panel)
    coh_count = sum(1 for c in panel.columns if c.startswith('coh_'))
    logger.info(f"  ✅ 文本连贯性: 新增 {coh_count:,d} 列")

    # ══════════════════════════════════════════════════════════════════
    # 改进 C: Ctx / Ss 轨 N-最近邻差异度 + 全行业向量法 (三轨 full/ctx/ss)
    # ══════════════════════════════════════════════════════════════════
    # 【学术】Ctx 轨使用上下文窗口文本 (content_ctx) 聚合, 排除与银行无关的
    #   通用报道段落, 信噪比更高; Ss 轨进一步收紧到银行+金科同句共现文本
    #   (content_ss), 仅保留两实体出现在同一句的最强信号 (回退镜像 ctx→全文)。
    #   三轨 (full/ctx/ss) 互为稳健性, 检验归因窗口收紧对差异度指标的影响。
    # 【白话】Full 轨用完整新闻, Ctx 轨只用提到银行名字附近的段落,
    #   Ss 轨只用"银行和金融科技出现在同一句话"的文本。
    # fix(topk-n-expansion, 2026-07-02): ctx/ss 五方法均展开 N∈LDA_EMB_N_LIST={5}∪_TOPK_NN
    #   (原仅 n5; 现与 Full 轨大 N 对称, 互为稳健性、不分主次)。
    # 注: 此处把原 ctx 内联块参数化为 (track_suffix, text_col) 循环, ss 复用
    #   完全相同的方法 (TF-IDF char/word + LDA + Embedding 主轨 + co-primary _lg) 逻辑;
    #   每轨守卫 text_col 存在 (缺失 → graceful skip), 列名机械 _ctx/_ss 后缀。
    logger.info("=" * 60)
    logger.info("Ctx / Ss 轨: N-最近邻 + 全行业向量法 (三轨)")
    logger.info("=" * 60)

    # 三轨参数化: (列名后缀, 源文本列) — ctx=上下文窗口, ss=银行+金科同句共现
    _sub_tracks = [('_ctx', 'content_ctx'), ('_ss', 'content_ss')]
    for _tsfx, _text_col in _sub_tracks:
        if _text_col not in df_exploded.columns:
            logger.warning(f"  {_tsfx} 轨: 列 '{_text_col}' 不存在, 跳过")
            continue
        agg_sub_sd = _aggregate_bank_year_texts(
            df_exploded, text_col=_text_col, co_mention_downweight=_co_dw)
        # dual/tri-track parity: Fluidity 与同业相对测度
        # (strat_diff_n5 / strat_sim_max / centroid_diff_*) 各轨齐全。
        # _compute_fluidity(agg_df, mode) 签名 track-agnostic, 复用本轨聚合
        # 补 strat_fluidity{_tsfx} / strat_fluidity_w{_tsfx}, 与 Full 轨对称。
        flu_c_sub = _compute_fluidity(agg_sub_sd, 'char')
        flu_w_sub = _compute_fluidity(agg_sub_sd, 'word')
        sub_results = []

        # S13 (2026-07-31): 计算段下沉到 `_strat_year_worker` + 逐年进程并行
        # (与 Full 轨同一 worker、同一驱动器)。⚠ 两处口径差异刻意保留:
        #   ① 子轨 char/word 用 LDA_EMB_N_LIST (Full 轨用 N_LIST);
        #   ② 子轨 <3 家银行原为**裸 continue 无告警**, 故 few_banks_warn=False,
        #      日志与旧码逐行一致 (不借机"顺手补告警" —— 那会改变日志基线)。
        _tasks_sub = _strat_year_tasks(agg_sub_sd, _tsfx, _tsfx)
        _bon_tail_sub = (
            "该年 {n} 家银行的 strat_diff_n*_emb" + _tsfx + " / "
            "strat_sim_max_emb" + _tsfx + " / centroid_diff_emb" + _tsfx + " "
            "及其 _lg 孪生一并置 NaN")
        for (_payload, _logs), _task in zip(
                _run_strat_year_tasks(
                    _tasks_sub, LDA_EMB_N_LIST, LDA_EMB_N_LIST, False,
                    "    " + _tsfx + " 轨 year={year} LDA+JSD 失败 ({exc}), 跳过",
                    _bon_tail_sub),
                _tasks_sub):
            for _lvl, _msg in _logs:
                logger.log(_lvl, _msg)
            if _payload is None:
                continue
            banks = _task[3]
            year = _task[2]
            sc, sw, sl = _payload['sc'], _payload['sw'], _payload['sl']
            se, se_lg = _payload['se'], _payload['se_lg']
            cd_c, cd_w, cd_lda = _payload['cd_c'], _payload['cd_w'], _payload['cd_lda']
            cd_emb, cd_emb_lg = _payload['cd_emb'], _payload['cd_emb_lg']

            for bank in banks:
                row = {'target_bank': bank, 'year': year}
                # N-NN 本轨, 列名机械 _ctx/_ss 后缀
                # fix(topk-n-expansion, 2026-07-02): 五方法均由单 n5 改 for-N 多列写出
                #   (N∈LDA_EMB_N_LIST); ⚠ char/word 的 emit 原为循环外单 n5 硬写, 此处已改循环。
                #   sim_max 保持 N-independent 每方法一列。
                for N in LDA_EMB_N_LIST:
                    row[f'strat_diff_n{N}{_tsfx}'] = sc[f'n{N}'][bank]
                    row[f'strat_diff_n{N}_w{_tsfx}'] = sw[f'n{N}'][bank]
                row[f'strat_sim_max{_tsfx}'] = sc['sim_max'][bank]
                row[f'strat_sim_max_w{_tsfx}'] = sw['sim_max'][bank]
                if sl:
                    for N in LDA_EMB_N_LIST:
                        row[f'strat_diff_n{N}_lda{_tsfx}'] = sl[f'n{N}'].get(bank, np.nan)
                    row[f'strat_sim_max_lda{_tsfx}'] = sl['sim_max'].get(bank, np.nan)
                if se:
                    for N in LDA_EMB_N_LIST:
                        row[f'strat_diff_n{N}_emb{_tsfx}'] = se[f'n{N}'].get(bank, np.nan)
                    row[f'strat_sim_max_emb{_tsfx}'] = se['sim_max'].get(bank, np.nan)
                if se_lg:  # co-primary 嵌入 (_lg); 与 emb 严格同 N 列表保 parity
                    for N in LDA_EMB_N_LIST:
                        row[f'strat_diff_n{N}_emb_lg{_tsfx}'] = se_lg[f'n{N}'].get(bank, np.nan)
                    row[f'strat_sim_max_emb_lg{_tsfx}'] = se_lg['sim_max'].get(bank, np.nan)
                # Centroid 本轨
                row[f'centroid_diff_tfidf_c{_tsfx}'] = cd_c[bank]
                row[f'centroid_diff_tfidf_w{_tsfx}'] = cd_w[bank]
                if cd_lda:
                    row[f'centroid_diff_lda{_tsfx}'] = cd_lda.get(bank, np.nan)
                if cd_emb:
                    row[f'centroid_diff_emb{_tsfx}'] = cd_emb.get(bank, np.nan)
                    # code-review P1-3: MAIN 契约别名 strat_diff_{ctx,ss} 与 _lg strat_diff_lg_{ctx,ss} 对称
                    row[f'strat_diff{_tsfx}'] = cd_emb.get(bank, np.nan)
                if cd_emb_lg:  # co-primary 嵌入 + 契约别名 strat_diff_lg_{ctx,ss}
                    row[f'centroid_diff_emb_lg{_tsfx}'] = cd_emb_lg.get(bank, np.nan)
                    row[f'strat_diff_lg{_tsfx}'] = cd_emb_lg.get(bank, np.nan)
                sub_results.append(row)

        if sub_results:
            sub_df = pd.DataFrame(sub_results)
            panel = panel.merge(sub_df, on=['target_bank', 'year'],
                                how='left')
            logger.info(f"  ✅ {_tsfx} 轨: {len(sub_df)} 行, "
                        f"{len(sub_df.columns) - 2} 列")
        else:
            logger.warning(f"  {_tsfx} 轨: 无有效结果")
        # Fluidity 本轨 (tri-track parity; 与 Full strat_fluidity 对称)
        # fix(omni-g-strategic-13, 2026-06-11): 同 Full 轨, 落列独立于 NN ≥3
        # 银行闸门 (原经 sub_results 行附着, <3 银行年份的 fluidity 被丢弃)
        panel[f'strat_fluidity{_tsfx}'] = panel.apply(
            lambda r, d=flu_c_sub: d.get((r['target_bank'], r['year']), np.nan),
            axis=1)
        panel[f'strat_fluidity_w{_tsfx}'] = panel.apply(
            lambda r, d=flu_w_sub: d.get((r['target_bank'], r['year']), np.nan),
            axis=1)

    # ── 关键指标解读 (运行结果信息) + 子步骤墙钟 ──
    try:
        _strat_cols = [c for c in panel.columns
                       if c.startswith('strat_') or c.startswith('centroid_')
                       or c.startswith('coh_') or c.startswith('lazy_')]
        logger.info(f"  📊 战略差异度结果: 落列 {len(_strat_cols):,d} 列 "
                    f"(strat_*/centroid_*/coh_*/lazy_*) on {len(panel):,d} 银行年")
        # 基准列 strat_diff_n5 (Guzman-Li N=5) 的覆盖率与分布判读
        _base = 'strat_diff_n5'
        if _base in panel.columns:
            v = panel[_base].dropna()
            if len(v) > 0:
                _cov = len(v) / max(1, len(panel))
                _cov_verdict = ('✅ 覆盖充分' if _cov >= 0.5
                                else ('⚠ 覆盖偏低 (小样本/年内<3 银行闸门)' if _cov >= 0.2
                                      else '❌ 覆盖过低'))
                logger.info(
                    f"    · {_base}: 非空 {len(v):,d}/{len(panel):,d} "
                    f"({pct4(_cov)}) {_cov_verdict}; "
                    f"μ={sig4(v.mean())} σ={sig4(v.std())} "
                    f"[min={sig4(v.min())}, max={sig4(v.max())}]")
                # 五数概括 (Round-8 分布标准: median + IQR 补足偏度/集中度判读;
                # Guzman-Li N=5 bashline 战略差异度指数, 仅日志, 不改任何值)
                logger.info(
                    f"      五数概括: median={sig4(v.median())} "
                    f"IQR=[q25={sig4(v.quantile(0.25))}, q75={sig4(v.quantile(0.75))}]")
                # 零方差自检 (战略差异度若全相等 → 文档高度同质, 无区分力)
                if float(v.std()) < 1e-9:
                    logger.warning("    · strat_diff_n5 近零方差: 年内文档高度同质, "
                                   "战略差异度无区分力 (检查文本聚合/共提及机械相似)")
            else:
                logger.warning(f"    · {_base}: 全空 (无年度通过 ≥3 银行闸门)")
        # 三轨齐备性判读 (full/ctx/ss N=5 主列)
        _track_cov = {
            sfx or 'full': (panel[f'strat_diff_n5{sfx}'].notna().sum()
                            if f'strat_diff_n5{sfx}' in panel.columns else 0)
            for sfx in ('', '_ctx', '_ss')}
        logger.info(f"    · 三轨 strat_diff_n5 覆盖 (非空行数): "
                    f"full={_track_cov['full']:,d} ctx={_track_cov['_ctx']:,d} "
                    f"ss={_track_cov['_ss']:,d} "
                    f"({'三轨齐备' if all(_track_cov.values()) else '部分轨道空/缺列, 优雅降级'})")
        # Lazy-Prices 3 算子 (_full 轨) 覆盖率 + μ/σ/[min,max] 分布判读: 实证
        # _compute_lazy_distances docstring (L1120-1125) 的披露 —— lazy_minedit 仅取
        # 前 2000 字前缀 → 近天花板 (mean≈0.95) 近零方差, 让 referee 从 .log 实证
        # 该退化而非凭注释采信; jaccard/overlap 为全文 token 集算子, 变异更可用。
        for _lz in ('lazy_jaccard_full', 'lazy_overlap_full', 'lazy_minedit_full'):
            if _lz in panel.columns:
                _lv = panel[_lz].dropna()
                if len(_lv) > 0:
                    logger.info(
                        f"    · {_lz}: 非空 {len(_lv):,d}/{len(panel):,d} "
                        f"({pct4(len(_lv) / max(1, len(panel)))}); "
                        f"μ={sig4(_lv.mean())} σ={sig4(_lv.std())} "
                        f"[min={sig4(_lv.min())}, max={sig4(_lv.max())}]")
        logger.info(f"  ⏱ 战略差异度子步骤墙钟: {sig4(_time.time() - _t_entry)} 秒")
    except Exception as _result_exc:  # noqa: BLE001
        logger.warning(f"  战略差异度 result-analysis 日志失败 (不阻塞): {_result_exc!r}")

    return panel


def _log_robustness_diagnostics(panel):
    """输出六方法相关矩阵 + 分族值域断言。

    【白话】这是"质量检查"函数，做两件事：
      1. 看六种方法（TF-IDF字符/词级、LDA、Embedding + centroid 字符/Embedding）
         算出来的分数是否大致一致 — 如果都说某银行很独特，说明结果可靠
      2. 分族值域检查 (fix(omni-g-strategic-02/10), 2026-06-11):
         - emb 轨相似度 (strat_sim_max*emb*) ∈ [-1,1] (余弦真值域)
         - emb 轨距离 (strat_diff_*emb* / centroid_diff_emb* / strat_diff_lg_*)
           ∈ [0,2] (δ = 1 − cos)
         - 其余 (TF-IDF/LDA 非负向量/分布 + fluidity) ∈ [0,1]
         原对全族统一断言 [0,1], 与 emb 轨去删失后的真值域不符
    """
    cols = [c for c in ['strat_diff_n5', 'strat_diff_n5_w',
                        'strat_diff_n5_lda', 'strat_diff_n5_emb',
                        'centroid_diff_tfidf_c', 'centroid_diff_emb']
            if c in panel.columns]
    if len(cols) >= 2:
        logger.info(f"  六方法相关矩阵:\n{panel[cols].corr().round(4).to_string()}")

    # 分族值域断言 (含浮点误差容忍)
    for col in [c for c in panel.columns
                if c.startswith('strat_') or c.startswith('centroid_')]:
        v = panel[col].dropna()
        if len(v) == 0:
            continue
        if col.startswith('strat_sim_max') and '_emb' in col:
            lo, hi = -1.0, 1.0       # emb 余弦相似度
        elif ('_emb' in col or col.startswith('strat_diff_lg')
                or col in ('strat_diff_full', 'strat_diff_ctx', 'strat_diff_ss')):
            # emb 距离 δ = 1 − cos ∈ [0,2] (含 _lg 别名 + MAIN centroid 别名 strat_diff_{full,ctx,ss};
            # 审计 F7: MAIN 别名本体 = centroid_diff_emb, 负余弦时 δ>1, 原 [0,1] 桶会误崩阶段)
            lo, hi = 0.0, 2.0
        else:
            lo, hi = 0.0, 1.0        # TF-IDF / LDA / fluidity
        assert (v >= lo - 1e-10).all() and (v <= hi + 1e-10).all(), \
            f"{col} 超出 [{lo:g},{hi:g}] 值域: min={sig4(v.min())}, max={sig4(v.max())}"
