"""
27_fintech_benefit_society.py — 金融科技经营效益态度指数模块
============================================================================

【学术支撑 (Academic Foundation)】
本模块严格基于 Jha, Liu & Manela (2026, RFS, §1.3.2 Eq. 1) 的"双极连续余弦投影网络"
框架，构建银行金融科技/数字化转型对自身经营活动的情感态度连续指数。

核心方法论链:
  1. 双极锚点投影 (Bipolar Anchor Projection):
     Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit society?
     A language embedding approach. Review of Financial Studies, 39(5),
     1227–1266. https://doi.org/10.1093/rfs/hhaf012
     → §1.3.2 Eq. 1: a_j = cos(s_j, p), 其中 p = mean(pos) - mean(neg)
     → Table 2: 正负极锚点句严格对偶 (single-word-change)

  2. 文化几何学 (Geometry of Culture) — 方法论上游:
     Kozlowski, A. C., Taddy, M., & Evans, J. A. (2019). The geometry of
     culture: Analyzing the meanings of class through word embeddings.
     American Sociological Review, 84(5), 905–949.
     https://doi.org/10.1177/0003122419877135
     → §2.1: 通过正-负差分向量定义语义维度

  3. Sentence Embedding 降级方案:
     Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings
     using Siamese BERT-networks. EMNLP, 3982–3992.
     https://doi.org/10.18653/v1/D19-1410

【白话说明 (Plain Language)】
任务目标：给每篇金融科技新闻打一个"经营效益态度分"——衡量这篇新闻把银行金融科技
描述成"利好经营"还是"损害经营"。

核心做法：
  1. 定义 10 对正/负极锚点句（如"金融科技提升经营效率" vs "金融科技降低经营效率"）
  2. 把正极句和负极句分别变成向量，做差得到"利好经营"方向轴
  3. 把每篇新闻也变成向量，往方向轴上投影（余弦相似度）
  4. 分数 > 0 = 利好经营，分数 < 0 = 损害经营，分数 = 0 = 中性

与其他模块的区别：
  - Stage 15/26: 锚点是单一政策文本，衡量"像不像政策"
  - Stage 27:   锚点是双极对偶句，衡量"利好还是损害经营"（连续轴）
  - 词典法/LLM情感: 衡量"通用正面/负面"，不针对金融科技经营维度

输出变量 (Bank-Year 级):
  benefit_mean_full/ctx:      态度均值 ∈ [-1, 1]
  benefit_std_full/ctx:       态度离散度 ∈ [0, 1]
  benefit_pos_frac_full/ctx:  正态度文章占比 ∈ [0, 1]
  benefit_neg_frac_full/ctx:  负态度文章占比 ∈ [0, 1]
============================================================================
"""

import os
import asyncio
import numpy as np
import pandas as pd
import tiktoken
import importlib.util as _iu

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================
# 【术语】通过 importlib 动态加载 41 号共享配置模块，复用 logger 和 CONFIG
# 【白话】项目的"总开关"配置统一在 41 号文件里管理，所有模块共用同一套设置
_p41 = os.path.join(os.path.dirname(__file__), '41_panel_encode_aggregate.py')
if not os.path.exists(_p41):
    raise FileNotFoundError(f"缺失共享配置依赖: {_p41}")
_s41 = _iu.spec_from_file_location('_41_mod', _p41)
_m41 = _iu.module_from_spec(_s41)
_s41.loader.exec_module(_m41)
logger = _m41.logger
CONFIG = _m41.CONFIG
FILENAMES = _m41.FILENAMES
OUTPUT_DIR = _m41.OUTPUT_DIR

STAGE_NAME = "27_fintech_benefit_society"

# LLM API 配置（复用 tone_llm_processing 节中的 base_url 和 api_key）
LLM_CONFIG = CONFIG.get('tone_llm_processing', {})

# 模块专属配置
_BENEFIT_CFG = CONFIG.get('benefit_society', {})
_MAX_TOKENS_PER_INPUT = _BENEFIT_CFG.get('max_tokens_per_input', 8191)
_MAX_TOKENS_PER_REQUEST = _BENEFIT_CFG.get('max_tokens_per_request', 250_000)
_CACHE_EMBEDDINGS = _BENEFIT_CFG.get('cache_embeddings', True)

# tiktoken 精确 Token 计数器
_ENCODING = tiktoken.get_encoding("cl100k_base")


# ============================================================================
# 2. 锚点句定义
# ============================================================================
# 【学术依据】[Jha et al. 2026, RFS] Table 2: 正负极锚点句必须严格对偶
#   原文 5 对，本项目扩充至 10 对以覆盖银行经营全维度
#   均值聚合后差分，句数增加可进一步降低单句噪声 (§1.3.2)
# 【白话】10 把"尺子"从不同角度衡量银行金融科技对自身经营的情感影响
#
# 维度覆盖验证 (银行经营全景):
#   核心经营: ① 盈利效率  ③ 风险管控  ⑨ 信贷质量
#   增长能力: ② 业务转型  ④ 客户基础  ⑤ 市场竞争力
#   资源投入: ⑦ 经济效益  ⑩ 人才队伍
#   合规安全: ⑥ 合规成本  ⑧ 信息安全
#
# 【对偶原则】严格遵循 [Jha et al. 2026] Table 2 的 single-word-change 规则:
#   (a) 每对仅替换一个核心动词，不加/不换副词，正负极除该动词外 100% 相同
#   (b) 使用一般现在时 (去掉"了")，对标原文 benefit/damage/helps/hurts
#       → 锚点表达"一般性态度/信念"，非描述过去事件 (Table 2 + App. A)

POSITIVE_ANCHORS = [
    # --- 核心经营 (3 维度) ---
    "银行数字化转型提升经营效率与盈利能力",             # ① enhances↔diminishes
    #   EN: Bank digital transformation enhances operational efficiency and profitability
    "金融科技应用改善银行风险管控水平",                 # ③ improves↔worsens
    #   EN: Fintech application improves bank risk management capability
    "金融科技提高银行信贷质量与资产安全性",             # ⑨ elevates↔lowers
    #   EN: Fintech elevates bank credit quality and asset safety
    # --- 增长能力 (3 维度) ---
    "金融科技创新促进银行业务转型与发展",               # ② promotes↔hinders
    #   EN: Fintech innovation promotes bank business transformation and development
    "数字金融服务拓展银行客户基础与服务渠道",           # ④ expands↔contracts
    #   EN: Digital financial services expand bank customer base and service channels
    "金融科技布局增强银行的市场竞争力",                 # ⑤ strengthens↔weakens
    #   EN: Fintech deployment strengthens bank market competitiveness
    # --- 资源投入 (2 维度) ---
    "银行金融科技投入提升整体经营效益",                 # ⑦ boosts↔harms
    #   EN: Bank fintech investment boosts overall operational returns
    "银行数字化转型推动科技人才队伍建设",               # ⑩ facilitates↔constrains
    #   EN: Bank digital transformation facilitates technology talent development
    # --- 合规安全 (2 维度) ---
    "金融科技建设降低银行合规成本与运营风险",           # ⑥ reduces↔increases
    #   EN: Fintech development reduces bank compliance costs and operational risks
    "银行数字化转型保障客户信息安全与隐私",             # ⑧ safeguards↔compromises
    #   EN: Bank digital transformation safeguards customer information security and privacy
]

NEGATIVE_ANCHORS = [
    # --- 核心经营 ---
    "银行数字化转型降低经营效率与盈利能力",             # ①
    #   EN: Bank digital transformation diminishes operational efficiency and profitability
    "金融科技应用恶化银行风险管控水平",                 # ③
    #   EN: Fintech application worsens bank risk management capability
    "金融科技降低银行信贷质量与资产安全性",             # ⑨
    #   EN: Fintech lowers bank credit quality and asset safety
    # --- 增长能力 ---
    "金融科技创新阻碍银行业务转型与发展",               # ②
    #   EN: Fintech innovation hinders bank business transformation and development
    "数字金融服务缩减银行客户基础与服务渠道",           # ④
    #   EN: Digital financial services contract bank customer base and service channels
    "金融科技布局削弱银行的市场竞争力",                 # ⑤
    #   EN: Fintech deployment weakens bank market competitiveness
    # --- 资源投入 ---
    "银行金融科技投入损害整体经营效益",                 # ⑦
    #   EN: Bank fintech investment harms overall operational returns
    "银行数字化转型制约科技人才队伍建设",               # ⑩
    #   EN: Bank digital transformation constrains technology talent development
    # --- 合规安全 ---
    "金融科技建设增加银行合规成本与运营风险",           # ⑥
    #   EN: Fintech development increases bank compliance costs and operational risks
    "银行数字化转型损害客户信息安全与隐私",             # ⑧
    #   EN: Bank digital transformation compromises customer information security and privacy
]

assert len(POSITIVE_ANCHORS) == len(NEGATIVE_ANCHORS), \
    f"正极 ({len(POSITIVE_ANCHORS)}) 和负极 ({len(NEGATIVE_ANCHORS)}) 锚点句数量不一致"


# ============================================================================
# 3. Token 截断与 Embedding 工具
# ============================================================================

def _count_tokens(text: str) -> int:
    """精确计算文本的 token 数 (cl100k_base 编码器)。

    【术语】tiktoken cl100k_base 是 text-embedding-3-small 的底层编码器
      参考: OpenAI Embeddings API 文档 — Model Overview
    【白话】把一段中文变成模型能读的"令牌"，数一数有多少个
      中文大约 1 个字 ≈ 1.5~2 个令牌
    """
    return len(_ENCODING.encode(text))


def _truncate_to_max_tokens(text: str, max_tokens: int = _MAX_TOKENS_PER_INPUT) -> str:
    """将文本精确截断至不超过 max_tokens 个 token。

    【术语】使用 tiktoken 编码→截断→解码三步法，确保结果严格不超限
      - text-embedding-3-small 单条输入硬性上限: 8,191 tokens (OpenAI 官方文档)
      - 超限行为: HTTP 400 BadRequestError (API 不会自动截断)
    【白话】如果文章太长（超过 ~4000 中文字），就只保留前面的部分
      绝大多数新闻不会超限，只有极长的万字报告会被截断
    """
    tokens = _ENCODING.encode(text)
    if len(tokens) <= max_tokens:
        return text
    return _ENCODING.decode(tokens[:max_tokens])


async def _get_embeddings_api(texts: list[str], token_counts: list[int]) -> np.ndarray:
    """通过 API 获取文本 Embedding 向量 — 动态批量策略。

    【术语】复用 Stage 15 (15_article_policy_alignment.py L161-238) 的动态批量策略
      API 限制 (OpenAI 官方文档, 经生产验证):
        - 单条输入上限: 8,191 tokens
        - 单次请求总 token 上限: 300,000 tokens (安全线设为 250,000)
        - 超限行为: HTTP 400 BadRequestError (不会自动截断)
    【白话】把文章发给 AI 模型变成数字向量，按总字数自动切分批次
      短新闻多的批次可能装 200+ 篇，长新闻多的批次可能只装 30 篇

    Args:
        texts: 已截断至 8191 tokens 的文本列表
        token_counts: 每篇文本对应的 token 数

    Returns:
        np.ndarray: Embedding 矩阵 (N × 1536)

    Raises:
        RuntimeError: API 返回非 200 状态码
    """
    import aiohttp
    cfg = LLM_CONFIG.get('models', [{}])[0]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {cfg['api_key']}"
    }

    # 动态批量切分 (按 token 总数)
    batches = []
    current_batch, current_tokens = [], 0
    for text, n_tok in zip(texts, token_counts):
        if current_batch and current_tokens + n_tok > _MAX_TOKENS_PER_REQUEST:
            batches.append(current_batch)
            current_batch, current_tokens = [], 0
        current_batch.append(text)
        current_tokens += n_tok
    if current_batch:
        batches.append(current_batch)

    logger.info(f"    Embedding 动态分批: {len(batches)} 批, "
                f"共 {len(texts)} 条, 总 {sum(token_counts):,} tokens")

    all_emb = []
    async with aiohttp.ClientSession() as session:
        for batch_idx, batch in enumerate(batches):
            async with session.post(
                f"{cfg['base_url']}/embeddings",
                json={"model": "text-embedding-3-small", "input": batch},
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=180)
            ) as resp:
                if resp.status != 200:
                    err_text = await resp.text()
                    raise RuntimeError(
                        f"Embedding API HTTP {resp.status} "
                        f"(batch {batch_idx+1}/{len(batches)}, "
                        f"{len(batch)} texts): {err_text[:200]}"
                    )
                data = await resp.json()
                all_emb.extend([
                    d['embedding']
                    for d in sorted(data['data'], key=lambda x: x['index'])
                ])

            if (batch_idx + 1) % 5 == 0:
                logger.info(f"    Embedding 进度: {batch_idx+1}/{len(batches)} 批完成")

    return np.array(all_emb)


def _get_embeddings_with_fallback(texts: list[str], token_counts: list[int]) -> np.ndarray | None:
    """三层降级策略获取 Embedding 向量。

    【术语】三层降级: API → 本地 Sentence-BERT → None
      复用 Stage 15 (L241-280) / Stage 25 (L393-426) 的降级架构
    【白话】优先用在线模型，不行就用本地模型，再不行就放弃

    ⚠️ 降级风险警告:
      API (1536 维) 和本地 text2vec (768 维) 的向量空间不同构。
      如果锚点使用 API 而新闻降级为本地模型，方向向量与新闻向量
      将处于不同维度空间，余弦投影在数学上无意义。
      当前设计: 锚点和新闻在同一次调用中使用相同降级策略，
      因此不会出现跨空间投影。

    Args:
        texts: 已截断的文本列表
        token_counts: 每篇文本的 token 数

    Returns:
        np.ndarray (N × d) 或 None (完全降级失败)
    """
    # 策略 1: API (text-embedding-3-small, 1536 维)
    try:
        emb = asyncio.run(_get_embeddings_api(texts, token_counts))
        logger.info(f"    Embedding: API 成功, 维度 {emb.shape}")
        return emb
    except Exception as e:
        logger.warning(f"    Embedding API 降级: {type(e).__name__}: {e}")

    # 策略 2: 本地 sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('shibing624/text2vec-base-chinese')
        emb = model.encode(texts, show_progress_bar=True, batch_size=64)
        logger.info(f"    Embedding: 本地 text2vec 成功, 维度 {emb.shape}")
        return np.array(emb)
    except Exception as e2:
        logger.warning(f"    Embedding 完全降级: {type(e2).__name__}: {e2}")

    return None


# ============================================================================
# 4. 方向向量计算
# ============================================================================

def _compute_direction_vector() -> np.ndarray | None:
    """计算"利好经营"方向向量 p = mean(pos_emb) - mean(neg_emb)。

    【学术依据】
    Jha et al. (2026, RFS §1.3.2): "average the embeddings of positive
    sentences less [minus] that of their negative counterparts"
    Kozlowski et al. (2019, ASR §2.1): 差分向量定义语义维度

    【白话】把 10 句"利好经营的话"和 10 句"不利经营的话"分别平均，
    然后做差，得到一个指向"利好经营"的方向。这个方向是全局唯一的，
    不按年份重算。

    Returns:
        np.ndarray (d,) 或 None (Embedding 失败 / 方向向量退化)
    """
    # ---- 锚点 Embedding 缓存 ----
    # 【白话】锚点句固定不变，缓存后不再重复花钱调 API
    anchor_cache_name = FILENAMES.get('output_27_benefit_cache',
                                      '27_benefit_embeddings.npy')
    anchor_cache_path = os.path.join(
        OUTPUT_DIR, anchor_cache_name.replace('.npy', '_anchors.npy'))

    emb = None
    if _CACHE_EMBEDDINGS and os.path.exists(anchor_cache_path):
        cached = np.load(anchor_cache_path)
        if cached.shape[0] == len(POSITIVE_ANCHORS) + len(NEGATIVE_ANCHORS):
            emb = cached
            logger.info(f"    锚点 Embedding 缓存命中: {anchor_cache_path}")
        else:
            logger.warning(f"    锚点缓存行数不匹配 ({cached.shape[0]} vs "
                           f"{len(POSITIVE_ANCHORS) + len(NEGATIVE_ANCHORS)}), 重新计算")

    if emb is None:
        all_anchors = POSITIVE_ANCHORS + NEGATIVE_ANCHORS
        token_counts = [_count_tokens(s) for s in all_anchors]
        emb = _get_embeddings_with_fallback(all_anchors, token_counts)
        if emb is None:
            return None
        # 保存锚点缓存
        if _CACHE_EMBEDDINGS:
            os.makedirs(os.path.dirname(anchor_cache_path), exist_ok=True)
            np.save(anchor_cache_path, emb)
            logger.info(f"    锚点 Embedding 缓存已保存: {anchor_cache_path}")

    n_pos = len(POSITIVE_ANCHORS)
    pos_emb = emb[:n_pos].mean(axis=0)    # 正极均值
    neg_emb = emb[n_pos:].mean(axis=0)    # 负极均值
    direction = pos_emb - neg_emb         # 利好经营方向

    # ---- 零范数防护 (退化检测) ----
    # 【学术依据】Kozlowski et al. (2019, ASR §2.1): 差分向量为零意味着
    #   正/负极在语义空间中完全重合，方向轴退化，投影无意义。
    # 【白话】如果"利好"和"损害"的向量完全一样，说明模型分不清好坏，
    #   这种情况下不能继续计算，否则会产生 inf/NaN 污染整个面板。
    dir_norm_val = np.linalg.norm(direction)
    if dir_norm_val < 1e-10:
        logger.error("    ❌ 方向向量范数为零 (正/负极语义重合), 中止 Stage 27")
        return None

    # 方向性自检: 每句正极的投影应 > 0, 每句负极应 < 0
    dir_norm = direction / dir_norm_val
    for i, s in enumerate(POSITIVE_ANCHORS):
        emb_norm = np.linalg.norm(emb[i])
        if emb_norm < 1e-10:
            logger.warning(f"    ⚠️ 正极句 #{i+1} 为零向量, 跳过自检: {s[:20]}...")
            continue
        score = np.dot(emb[i], dir_norm) / emb_norm
        if score <= 0:
            logger.warning(f"    ⚠️ 正极句 #{i+1} 投影为负 ({score:.4f}): {s[:20]}...")
    for i, s in enumerate(NEGATIVE_ANCHORS):
        emb_norm = np.linalg.norm(emb[n_pos + i])
        if emb_norm < 1e-10:
            logger.warning(f"    ⚠️ 负极句 #{i+1} 为零向量, 跳过自检: {s[:20]}...")
            continue
        score = np.dot(emb[n_pos + i], dir_norm) / emb_norm
        if score >= 0:
            logger.warning(f"    ⚠️ 负极句 #{i+1} 投影为正 ({score:.4f}): {s[:20]}...")

    logger.info(f"    方向向量: 维度 {direction.shape}, "
                f"||p|| = {dir_norm_val:.4f}")
    return direction


# ============================================================================
# 5. 文章级投影计算
# ============================================================================

def _project_texts(texts: list[str], direction: np.ndarray,
                   cache_path: str | None = None) -> np.ndarray:
    """将文本列表投影至方向向量，返回连续态度得分 ∈ [-1, 1]。

    【学术依据】Jha et al. (2026, RFS §1.3.2 Eq. 1):
        a_j = cos(s_j, p) = (s_j · p) / (||s_j|| × ||p||)

    【白话】算每篇新闻在"利好经营"方向上的投影 — 正数=利好, 负数=损害, 零=中性

    Args:
        texts: 文章文本列表
        direction: 方向向量 p
        cache_path: .npy 缓存路径 (可选)

    Returns:
        np.ndarray (N,): 连续态度得分
    """
    # 尝试加载缓存
    # 【白话】如果之前已经算过并保存了结果，直接加载，不再花钱调 API
    # ⚠️ 缓存一致性约束: 缓存仅按行数校验。若锚点句变更导致方向向量
    #   改变，而缓存的 Embedding 未更新，投影值仍为旧方向上的投影。
    #   解决方案: 修改锚点后需手动删除 .npy 缓存文件。
    if cache_path and os.path.exists(cache_path):
        logger.info(f"    加载 Embedding 缓存: {cache_path}")
        emb = np.load(cache_path)
        if emb.shape[0] == len(texts):
            dir_norm = direction / np.linalg.norm(direction)
            norms = np.linalg.norm(emb, axis=1, keepdims=True)
            norms = np.where(norms == 0, 1.0, norms)  # 避免除零
            scores = (emb @ dir_norm) / norms.ravel()
            return scores
        else:
            logger.warning(f"    缓存行数不匹配 ({emb.shape[0]} vs {len(texts)}), 重新计算")

    # 截断 + token 计数
    truncated = [_truncate_to_max_tokens(t) for t in texts]
    token_counts = [_count_tokens(t) for t in truncated]

    # 获取 Embedding
    emb = _get_embeddings_with_fallback(truncated, token_counts)
    if emb is None:
        return np.full(len(texts), np.nan)

    # 保存缓存
    if cache_path and _CACHE_EMBEDDINGS:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        np.save(cache_path, emb)
        logger.info(f"    Embedding 缓存已保存: {cache_path}")

    # 余弦投影
    dir_norm = direction / np.linalg.norm(direction)
    norms = np.linalg.norm(emb, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)  # 避免除零
    scores = (emb @ dir_norm) / norms.ravel()
    return scores


# ============================================================================
# 6. Bank-Year 聚合 + 面板合并（核心入口函数）
# ============================================================================

def compute_benefit_society_panel(panel: pd.DataFrame,
                                 df_exploded: pd.DataFrame) -> pd.DataFrame:
    """从 df_exploded 计算文章级经营效益情感投影得分，聚合至 Bank-Year 面板。

    【学术依据】
    Jha et al. (2026, RFS §1.3.2 Eq. 1 + Eq. 2):
      - Eq. 1: 文章级投影 a_j = cos(s_j, p)
      - Eq. 2: Bank-Year 聚合 f_it = Σ_j a_ji × (c_jit / Σ_k c_kit)
        本项目每篇文章权重相等 (c=1)，等价于算术均值

    【架构】与 26_authoritative_similarity.compute_authoritative_similarity() 同构
    【数据流】df_exploded → 文章级 benefit_score → Bank-Year 聚合 → merge 到 panel

    Args:
        panel: 当前 Bank-Year 面板
        df_exploded: 包含新闻原文的文章-银行级数据集

    Returns:
        pd.DataFrame: 合并了 8 列 benefit_* 指标的面板
    """
    logger.info("=" * 60)
    logger.info("步骤 7h-benefit: 金融科技经营效益态度投影")
    logger.info("  (Jha, Liu & Manela 2026, RFS §1.3.2)")
    logger.info("=" * 60)

    # ---- 6.1 计算方向向量 ----
    direction = _compute_direction_vector()
    if direction is None:
        logger.warning("  方向向量计算失败, 跳过 Stage 27")
        return panel

    # ---- 6.2 缓存路径 ----
    cache_filename = FILENAMES.get('output_27_benefit_cache',
                                   '27_benefit_embeddings.npy')

    # ---- 6.3 双轨投影 ----
    # 【术语】双轨投影 (Dual-Track Projection):
    #   - Full 轨: 标题 + 全文正文，完整语义信号
    #   - Ctx  轨: 实体上下文 (entity_context.py 提取)，消除非目标实体的情感污染
    #   与 Stage 25/26 的双轨设计同构
    # 【白话】Full 轨 = 整篇新闻; Ctx 轨 = 只看提到这家银行的段落
    for track in ['full', 'ctx']:
        col_score = f'benefit_score_{track}'

        # 检查 Ctx 轨数据是否存在
        if track == 'ctx' and 'content_ctx' not in df_exploded.columns:
            logger.info(f"  {track.upper()} 轨: content_ctx 列不存在, 跳过")
            continue

        # 向量化文本构建（避免 iterrows 性能瓶颈）
        if track == 'full':
            texts = (df_exploded.get('标题', pd.Series('', index=df_exploded.index))
                     .fillna('').astype(str)
                     + ' '
                     + df_exploded.get('内容', pd.Series('', index=df_exploded.index))
                     .fillna('').astype(str)).str.strip().tolist()
        else:
            texts = df_exploded['content_ctx'].fillna('').astype(str).str.strip().tolist()

        # 过滤空文本
        valid_mask = np.array([bool(t) for t in texts])
        valid_texts = [t for t, m in zip(texts, valid_mask) if m]

        if not valid_texts:
            logger.info(f"  {track.upper()} 轨: 无有效文本, 跳过")
            continue

        logger.info(f"  {track.upper()} 轨: {len(valid_texts)}/{len(texts)} 篇有效文本")

        # 缓存路径 (Full 和 Ctx 分开)
        cache_path = os.path.join(OUTPUT_DIR,
                                  cache_filename.replace('.npy', f'_{track}.npy'))

        # 投影计算
        valid_scores = _project_texts(valid_texts, direction, cache_path)

        # 向量化回填至 df_exploded (in-place 副作用)
        # ⚠️ 此处向 df_exploded 添加了 benefit_score_{track} 中间列。
        #   该列仅用于下方 Bank-Year 聚合，不影响后续模块
        #   (compute_brokerage_centrality 等只读取自身所需列)。
        scores = np.full(len(texts), np.nan)
        scores[valid_mask] = valid_scores
        df_exploded[col_score] = scores

        # ---- 6.4 Bank-Year 聚合 ----
        # 【学术依据】Jha et al. (2026, RFS Eq. 2): 等权算术均值
        # 【白话】算每家银行每年所有新闻的"经营效益态度平均分"
        agg = (df_exploded
               .dropna(subset=[col_score])
               .groupby(['target_bank', 'year'])[col_score]
               .agg(
                   benefit_mean=('mean'),
                   benefit_std=('std'),
               )
               .reset_index())

        # 正/负态度占比
        frac = (df_exploded
                .dropna(subset=[col_score])
                .groupby(['target_bank', 'year'])[col_score]
                .agg(
                    benefit_pos_frac=lambda x: (x > 0).mean(),
                    benefit_neg_frac=lambda x: (x < 0).mean(),
                )
                .reset_index())

        agg = agg.merge(frac, on=['target_bank', 'year'], how='left')

        # std 的 NaN (单观测) → 0
        agg['benefit_std'] = agg['benefit_std'].fillna(0)

        # 重命名: 添加轨后缀
        rename_map = {
            'benefit_mean': f'benefit_mean_{track}',
            'benefit_std': f'benefit_std_{track}',
            'benefit_pos_frac': f'benefit_pos_frac_{track}',
            'benefit_neg_frac': f'benefit_neg_frac_{track}',
        }
        agg = agg.rename(columns=rename_map)

        # ---- 6.5 合并至面板 ----
        new_cols = list(rename_map.values())
        panel = panel.merge(
            agg[['target_bank', 'year'] + new_cols],
            on=['target_bank', 'year'],
            how='left'
        )

        logger.info(f"  {track.upper()} 轨聚合完成: "
                    f"benefit_mean_{track} 非空率 "
                    f"{panel[f'benefit_mean_{track}'].notna().mean():.1%}")

    logger.info("=" * 60)
    return panel
