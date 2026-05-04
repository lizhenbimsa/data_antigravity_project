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
import sys
import asyncio
import numpy as np
import pandas as pd
import tiktoken
import json

# Phase 5c-1: 注入项目根, 让 ``news_process.core.*`` 在包模式下可解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.caching import LLMCache

# ============================================================================
# 1. 全局配置和初始化  (Phase 2a: 取代旧的 importlib 反射)
# ============================================================================
from news_process.pipeline.panel.encode import logger, CONFIG, FILENAMES, OUTPUT_DIR  # noqa: E402

STAGE_NAME = "27_fintech_benefit_society"

# LLM API 配置（复用 tone_llm_processing 节中的 base_url 和 api_key）
LLM_CONFIG = CONFIG.get('tone_llm_processing', {})
EMBEDDING_CONFIG = CONFIG.get('embedding_api', {})

# 模块专属配置
_BENEFIT_CFG = CONFIG.get('benefit_society', {})
_MAX_TOKENS_PER_INPUT = _BENEFIT_CFG.get('max_tokens_per_input', 8191)
_MAX_TOKENS_PER_REQUEST = _BENEFIT_CFG.get('max_tokens_per_request', 250_000)
_CACHE_EMBEDDINGS = _BENEFIT_CFG.get('cache_embeddings', True)

RETRY_DELAY = 5
MAX_RETRY_DELAY = 60
CACHE_DB_PATH = CONFIG['paths'].get('llm_cache_db', os.path.join(CONFIG['paths']['output_dir'], '_llm_cache.db'))

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


async def _get_embeddings_api(texts: list[str], token_counts: list[int], cache: LLMCache = None) -> np.ndarray:
    """通过 API 获取文本 Embedding 向量 — 穿透式缓存与死战不退容错。"""
    import aiohttp
    models = LLM_CONFIG.get('models') or []
    cfg = models[0] if models else {}
    if EMBEDDING_CONFIG:
        base_url = EMBEDDING_CONFIG.get('base_url')
        api_key = EMBEDDING_CONFIG.get('api_key')
        embedding_model = EMBEDDING_CONFIG.get('model') or "text-embedding-3-small"
    else:
        base_url = cfg.get('base_url')
        api_key = cfg.get('api_key')
        embedding_model = "text-embedding-3-small"
    if not base_url or not api_key:
        raise RuntimeError("Embedding API config missing base_url or api_key")
    base_url = str(base_url).rstrip("/")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    cached_results = [cache.get(embedding_model, text) if cache else None for text in texts]
    missing_indices = [i for i, res in enumerate(cached_results) if res is None]
    missing_texts = [texts[i] for i in missing_indices]
    missing_tokens = [token_counts[i] for i in missing_indices]

    missing_embs = []
    if missing_texts:
        batches = []
        current_batch, current_tokens = [], 0
        for text, n_tok in zip(missing_texts, missing_tokens):
            if current_batch and (len(current_batch) >= 2000 or current_tokens + n_tok > _MAX_TOKENS_PER_REQUEST):
                batches.append(current_batch)
                current_batch, current_tokens = [], 0
            current_batch.append(text)
            current_tokens += n_tok
        if current_batch:
            batches.append(current_batch)

        logger.info(f"    Embedding 动态分批: {len(batches)} 批")

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
                                        [json.dumps(emb) for emb in batch_embs]
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

    assert len(missing_embs) == len(missing_texts)
    final_embs = []
    missing_ptr = 0
    for res in cached_results:
        if res is not None:
            final_embs.append(json.loads(res))
        else:
            final_embs.append(missing_embs[missing_ptr])
            missing_ptr += 1

    return np.array(final_embs, dtype=np.float32)




# ============================================================================
# 4. 方向向量计算
# ============================================================================

def _compute_direction_vector() -> np.ndarray | None:
    all_anchors = POSITIVE_ANCHORS + NEGATIVE_ANCHORS
    token_counts = [_count_tokens(s) for s in all_anchors]
    with LLMCache(CACHE_DB_PATH) as cache:
        emb = asyncio.run(_get_embeddings_api(all_anchors, token_counts, cache))
    if emb is None or len(emb) == 0:
        return None

    n_pos = len(POSITIVE_ANCHORS)
    pos_emb = emb[:n_pos].mean(axis=0)
    neg_emb = emb[n_pos:].mean(axis=0)
    direction = pos_emb - neg_emb

    dir_norm_val = np.linalg.norm(direction)
    if dir_norm_val < 1e-10:
        logger.error("    ❌ 方向向量范数为零 (正/负极语义重合), 中止 Stage 27")
        return None

    dir_norm = direction / dir_norm_val
    for i, s in enumerate(POSITIVE_ANCHORS):
        emb_norm = np.linalg.norm(emb[i])
        if emb_norm < 1e-10:
            continue
        score = np.dot(emb[i], dir_norm) / emb_norm
        if score <= 0:
            logger.warning(f"    ⚠️ 正极句 #{i+1} 投影为负 ({score:.4f}): {s[:20]}...")
    for i, s in enumerate(NEGATIVE_ANCHORS):
        emb_norm = np.linalg.norm(emb[n_pos + i])
        if emb_norm < 1e-10:
            continue
        score = np.dot(emb[n_pos + i], dir_norm) / emb_norm
        if score >= 0:
            logger.warning(f"    ⚠️ 负极句 #{i+1} 投影为正 ({score:.4f}): {s[:20]}...")

    logger.info(f"    方向向量: 维度 {direction.shape}, ||p|| = {dir_norm_val:.4f}")
    return direction


# ============================================================================
# 5. 文章级投影计算
# ============================================================================

def _project_texts(texts: list[str], direction: np.ndarray, cache_path: str | None = None) -> np.ndarray:
    truncated = [_truncate_to_max_tokens(t) for t in texts]
    token_counts = [_count_tokens(t) for t in truncated]

    with LLMCache(CACHE_DB_PATH) as cache:
        emb = asyncio.run(_get_embeddings_api(truncated, token_counts, cache))

    if emb is None or len(emb) == 0:
        return np.full(len(texts), np.nan)

    dir_norm = direction / np.linalg.norm(direction)
    norms = np.linalg.norm(emb, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
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
