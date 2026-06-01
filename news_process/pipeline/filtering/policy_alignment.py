"""
15_article_policy_alignment.py — 文章级政策语义对齐度计算模块
============================================================================

【学术支撑 (Academic Foundation)】
本模块实现 Distel, Grimpe & Poetz (2026, Research Policy, §3.2.1) 的核心方法论：
在逐篇文章粒度计算与权威政策锚点的语义相似度，以支持后续 Token/Hidden
采纳行为的解耦分析。

核心学术逻辑链:
  1. 余弦相似度度量:
     Hoberg, G. & Phillips, G. (2016). Text-based network industries and
     endogenous product differentiation. Journal of Political Economy,
     124(5), 1423–1465. https://doi.org/10.1086/688176
     → §III: 余弦相似度作为文本语义距离的标准度量

  2. 宏观政策向量注入微观企业文本空间:
     Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019).
     Firm-level political risk: Measurement and effects. The Quarterly
     Journal of Economics, 134(4), 2135–2202.
     https://doi.org/10.1093/qje/qjz021
     → 核心思路: 将宏观政策文本嵌入与微观企业特征共享的向量空间

  3. Token vs Hidden 解耦:
     Distel, A. P., Grimpe, C., & Poetz, M. (2026). From evidence to
     impact: The use of scientific research in policy documents. Research
     Policy, 55(3), 105426. https://doi.org/10.1016/j.respol.2026.105426
     → §3.2.1: 逐篇文档级相似度计算，区分"显性引用"与"文本级语义实质借鉴"

  4. 象征性采用的制度理论基础:
     Westphal, J. D. & Zajac, E. J. (2001). Decoupling policy from
     practice: The case of stock repurchase programs. Administrative
     Science Quarterly, 46(2), 202–228. https://doi.org/10.2307/2667086
     → Token Adoption 旨在获取合法性 (Legitimacy Function)

  5. Cheap Talk 偏差:
     Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022).
     Cheap talk and cherry-picking: What ClimateBert has to say on
     corporate climate risk disclosures. Finance Research Letters, 47,
     102776. https://doi.org/10.1016/j.frl.2022.102776
     → 高频关键词 ≠ 实质性行动，需要语义层面的独立度量

【白话说明 (Plain Language)】
任务目标：给每一篇金融科技新闻打一个"政策对齐分"——衡量这篇新闻跟
国家金融科技政策像不像。

核心做法：
  1. 把国家的重磅政策文件（权威语料库）变成一个"标准答案向量"
  2. 把每篇新闻（标题+全文）也变成一个向量
  3. 计算两者的余弦相似度：分数越高，说明这篇新闻越贴合政策方向

为什么需要逐篇计算？
  - Stage 26 是给银行打"年度总分"（先把一年的新闻拼在一起再比较）
  - 但我们后续要给每篇新闻贴标签（是"洗科技"还是"真干事"）
  - 所以必须先算出每篇新闻各自的对齐分数

与 Stage 26 的区别：
  - Stage 26: Bank-Year 粒度，聚合后比较，用于面板回归
  - Stage 15: Article 粒度，逐篇比较，用于 Token/Hidden 四象限分类

输入:
  14_fintech_intensity.parquet (含 标题、内容、fintech_intensity_score 等)
  config/authoritative_corpus.txt (权威政策文本)

输出:
  15_article_alignment.parquet (= 原数据 + 新增 policy_cosine_sim 列)
============================================================================
"""

import asyncio
import json
import os
import sys
import time

import numpy as np
import pandas as pd

# Phase 5c-1: 注入项目根, 让 ``news_process.core.*`` 在包模式下可解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.caching import LLMCache

# ============================================================================
# 1. 全局配置和初始化  (Phase 2a: 取代旧的 importlib 反射)
# ============================================================================
from news_process.pipeline.panel.encode import CONFIG, logger  # noqa: E402
from news_process.pipeline.text import embedding_engine as _eng

# LLM API 配置（复用 tone_llm_processing 节中的 base_url 和 api_key）
LLM_CONFIG = CONFIG.get('tone_llm_processing', {})
# MAIN spec = text-embedding-3-small (API) → canonical policy_cosine_sim* 列
EMBEDDING_CONFIG = CONFIG.get('embedding_api', {})
# ROBUSTNESS spec = shibing624/text2vec (local) → _t2v 后缀稳健 twin 列
_ROBUSTNESS_SPEC = CONFIG.get('embedding_robustness', {})
RETRY_DELAY = 5
MAX_RETRY_DELAY = 60
CACHE_DB_PATH = CONFIG['paths'].get('llm_cache_db', os.path.join(CONFIG['paths']['output_dir'], '_llm_cache.db'))

# 模块专属配置
_ALIGN_CFG = CONFIG.get('policy_alignment', {})

# Stage 名称
STAGE_NAME = "15_article_policy_alignment"

# ============================================================================
# 2. tiktoken 精确 Token 计数器
# ============================================================================
# tiktoken 工具 — 统一复用 core/text/token_utils (薄包装保留旧签名)

_ALIGN_CFG = CONFIG.get('article_alignment', {})


def _coerce_positive_int(value, default: int) -> int:
    """配置兜底: 将 token 上限解析为正整数，异常时回退到安全默认值。"""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


# 【术语】OpenAI text-embedding-3-small 的硬性约束:
#   单条输入上限 8,191 tokens (cl100k_base 编码)
#   单次请求总 token 上限 ~300,000 tokens (经验值, 官方文档未精确公布)
# 【白话】每篇文章最多约 4,000 中文字, 每次 API 调用最多装约 125,000 中文字
_MAX_TOKENS_PER_INPUT = _coerce_positive_int(
    _ALIGN_CFG.get('max_tokens_per_input'), 8191)
_MAX_TOKENS_PER_REQUEST = _coerce_positive_int(
    _ALIGN_CFG.get('max_tokens_per_request'), 250_000)


def _count_tokens(text: str) -> int:
    """精确计算文本的 token 数 (已迁至 core.text.token_utils)。"""
    from news_process.core.text.token_utils import count_tokens
    return count_tokens(text)


def _truncate_to_max_tokens(text: str, max_tokens: int = _MAX_TOKENS_PER_INPUT) -> str:
    """将文本精确截断至不超过 max_tokens 个 token (已迁至 core.text.token_utils)。"""
    from news_process.core.text.token_utils import truncate_to_max_tokens
    return truncate_to_max_tokens(text, max_tokens)


def _split_into_chunks(text: str, max_tokens: int = _MAX_TOKENS_PER_INPUT) -> list[str]:
    """将超长文本按 token 粒度切分为多个不重叠分段 (已迁至 core.text.token_utils)。"""
    from news_process.core.text.token_utils import split_into_chunks
    return split_into_chunks(text, max_tokens)


# ============================================================================
# 3. Embedding API 管线（动态批量）
# ============================================================================
# 【术语】复用 Stage 25 (25_strategic_differentiation.py L358-390) 的
#   text-embedding-3-small API 调用架构，但改用动态批量大小以适配
#   逐篇文章全文输入的场景
#
#   Stage 25 使用固定每批 100 条 (L375)，适用于 Bank-Year 聚合文本
#   (通常几十条短文本)。Stage 15 处理逐篇文章全文，若 100 篇 ×
#   平均 3000 tokens = 300,000 tokens，恰好撞到 API 上限。
#   因此改用动态批量：按 token 总数而非文章数切分批次。
#
# 【白话】不是固定每批 100 篇，而是看总字数决定每批装多少篇
#   短新闻多的批次可能装 200+ 篇，长新闻多的批次可能只装 30 篇
#   这样确保每次调用 API 都不会超过它的容量上限

async def _get_embeddings_api_dynamic(
    texts: list[str],
    token_counts: list[int],
    cache: LLMCache = None,
    *,
    prompt_version_override: str | None = None,
) -> np.ndarray:
    """通过 API 获取文本 Embedding 向量 — 穿透式缓存与死战不退容错。

    【术语】
    引入 LLMCache 穿透查询，未命中则走 API。
    针对 API 使用"无限退避重试 (Infinite Exponential Backoff)"，
    只要是网络故障 (429, 500+) 绝不退出，直到取回完美向量为止。
    若是致命错误 (400, 401, 404)，则抛出 ValueError 拦截并中止进程。

    【白话】先把文章在缓存库里查一遍。没查到的打包发给大模型。
    如果网断了或者被限流，就一直等、一直试，绝不报错退出（除非密码错了），
    确保拿回来的全是完好无损的数据。

    Args:
        texts: 已截断至 8191 tokens 的文本列表
        token_counts: 每篇文本对应的 token 数
        cache: LLMCache 实例

    Returns:
        np.ndarray: Embedding 矩阵 (N × d)，d = 1536
    """
    import aiohttp
    models = LLM_CONFIG.get('models') or []
    cfg = models[0] if models else {}
    if EMBEDDING_CONFIG:
        base_url = EMBEDDING_CONFIG.get('base_url')
        api_key = EMBEDDING_CONFIG.get('api_key')
        embedding_model = (EMBEDDING_CONFIG.get('model') or "text-embedding-3-small")
    else:
        base_url = cfg.get('base_url')
        api_key = cfg.get('api_key')
        embedding_model = "text-embedding-3-small"
    if not base_url or not api_key:
        raise RuntimeError("Embedding API config missing base_url or api_key")
    base_url = str(base_url).rstrip("/")
    # Plan-r3 P3-17 接入: embedding 缓存键的 prompt_version 维度,
    # 防止改 embedding model / 文本预处理后旧 cache silent 命中.
    # Round 4 M8 修: 用参数 prompt_version_override 替代全局 mutation, 避免污染其他 callsite
    # 默认走 EMBEDDING_CONFIG 的 base version (full+auth 命中 v3.5.x 旧 cache);
    # ctx 轨调用方传 base+'-ctx' 显式隔离 namespace, 不再 mutate 全局 dict.
    text_pipeline_version = (
        prompt_version_override
        if prompt_version_override is not None
        else EMBEDDING_CONFIG.get('text_pipeline_version', 'v0')
    )
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # --- 1. 穿透式缓存层 ---
    cached_results = [
        cache.get(embedding_model, text, prompt_version=text_pipeline_version)
        if cache else None
        for text in texts
    ]
    missing_indices = [i for i, res in enumerate(cached_results) if res is None]
    missing_texts = [texts[i] for i in missing_indices]
    missing_tokens = [token_counts[i] for i in missing_indices]

    logger.info(f"    缓存拦截: 命中 {len(texts) - len(missing_texts)} 条, 缺失 {len(missing_texts)} 条")

    missing_embs = []
    if missing_texts:
        # --- 2. 动态批量切分 ---
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

        logger.info(f"    网络请求: 动态分批为 {len(batches)} 批")

        # --- 3. 死战不退重试循环 ---
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
                                # 原子写入缓存
                                if cache:
                                    cache.put_batch(
                                        embedding_model,
                                        batch,
                                        [json.dumps(emb) for emb in batch_embs],
                                        prompt_version=text_pipeline_version,
                                    )
                                break  # 成功，跳出无限重试
                            elif status in (429, 500, 502, 503, 504):
                                err_text = await resp.text()
                                logger.warning(f"    HTTP {status} (batch {batch_idx+1}): {err_text[:100]}。休眠 {delay} 秒后重试...")
                                await asyncio.sleep(delay)
                                delay = min(delay * 2, MAX_RETRY_DELAY)
                            else:
                                err_text = await resp.text()
                                raise ValueError(f"不可恢复的 API 错误 {status} (batch {batch_idx+1}): {err_text[:200]}")
                    except ValueError:
                        raise  # 直接向上抛出致命错误
                    except Exception as e:
                        logger.warning(f"    网络异常 (batch {batch_idx+1}): {type(e).__name__}: {e}。休眠 {delay} 秒后重试...")
                        await asyncio.sleep(delay)
                        delay = min(delay * 2, MAX_RETRY_DELAY)

                if (batch_idx + 1) % 5 == 0:
                    logger.info(f"    API 进度: {batch_idx+1}/{len(batches)} 批完成")

    # --- 4. 向量拼装复原 ---
    assert len(missing_embs) == len(missing_texts), "返回数量与缺失数量不符！"
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
# 3b. 双轨嵌入 + 余弦相似度公共算子 (v3.7.5: 双模型 dual-model)
# ============================================================================

def _cosine_for_spec(
    full_texts: list[str],
    ctx_texts: list[str],
    auth_chunks: list[str],
    spec: dict,
) -> tuple[np.ndarray | None, np.ndarray | None]:
    """用单一 spec 嵌入 (full / ctx / auth) 并返回 (cos_full, cos_ctx)。

    【关键约束】每个 spec 用**自己的**模型独立嵌入自己的 anchors/texts,
    绝不复用另一 spec 的向量 (API 1536 维 vs text2vec 768 维, 严禁混算)。

    流程:
      1. 用 spec 经 _eng.embed_texts 分别嵌入 full_texts / ctx_texts / auth_chunks
         (text-level, 内部已处理 chunk 切分 + mean pooling + local/API 分派)。
      2. 对 auth-chunk 嵌入做 mean pooling + L2 归一化 → 单个政策锚点向量
         (保留原 zero-norm 守卫: 范数为零时返回 NaN series)。
      3. cosine_similarity(full, anchor) / cosine_similarity(ctx, anchor)。

    Args:
        full_texts: 已截断的 full 轨文本
        ctx_texts:  已截断的 ctx 轨文本
        auth_chunks: 权威政策语料分段
        spec: embedding spec (MAIN=API / ROBUSTNESS=local)

    Returns:
        (cos_full_array, cos_ctx_array): 各为 (N,) np.ndarray;
        嵌入失败 (embed_texts 返回 None) 或锚点范数为零 → (None, None)。
    """
    from sklearn.metrics.pairwise import cosine_similarity

    model_id = _eng.spec_model(spec)
    log_prefix = f"Embedding[{model_id}]"

    article_embs_full = _eng.embed_texts(
        full_texts, spec, cache_db_path=CACHE_DB_PATH, log_prefix=log_prefix)
    article_embs_ctx = _eng.embed_texts(
        ctx_texts, spec, cache_db_path=CACHE_DB_PATH, log_prefix=log_prefix)
    auth_chunk_embs = _eng.embed_texts(
        auth_chunks, spec, cache_db_path=CACHE_DB_PATH, log_prefix=log_prefix)

    if (article_embs_full is None or article_embs_ctx is None
            or auth_chunk_embs is None):
        logger.warning(f"  {log_prefix}: 嵌入返回 None, 该 spec 轨置 NaN")
        return None, None

    # 均值池化 + L2 归一化 → 单个政策锚点向量 (维度无关)
    auth_emb = auth_chunk_embs.mean(axis=0, keepdims=True)
    auth_norm = np.linalg.norm(auth_emb, axis=1, keepdims=True)
    if auth_norm.item() > 0:
        auth_emb = auth_emb / auth_norm
    else:
        logger.error(f"  ⚠️ {log_prefix}: 政策锚点均值池化后范数为零!")
        return None, None
    logger.info(f"  {log_prefix} 政策锚点: {len(auth_chunk_embs)} 段 → "
                f"Mean Pooling → 1 个 {auth_emb.shape[1]}D 向量")

    cos_full = cosine_similarity(article_embs_full, auth_emb)[:, 0]
    cos_ctx = cosine_similarity(article_embs_ctx, auth_emb)[:, 0]
    return cos_full, cos_ctx


# ============================================================================
# 4. 主流程函数
# ============================================================================

def compute_article_policy_alignment(df: pd.DataFrame) -> pd.DataFrame:
    """计算文章级政策语义对齐度 (Article-level Policy Cosine Similarity)。

    【学术支撑】
    本函数实现的核心度量：

        policy_cosine_sim_i = cos(emb(article_i), emb(auth_text))

    其中:
      - emb() 为 text-embedding-3-small 的稠密语义编码 (1536 (API main) / 768 (text2vec robustness) 维)
      - auth_text 为权威政策语料库的拼接文本 (config/authoritative_corpus.txt)
      - cos(A,B) = (A·B) / (||A|| × ||B||)，值域 [-1, 1]

    该度量直接映射 Distel et al. (2026, Research Policy, §3.2.1) 的方法论:
    对每篇政策文档独立计算与基准文本的语义相似度，以此判定该文档是
    "显性引用" (Token) 还是 "文本级语义实质借鉴" (Hidden)。

    参考: Hassan et al. (2019, QJE) — 将宏观政策文本注入微观企业向量空间

    【白话说明】
    给每篇金融科技新闻打一个 0~1 的分数：
      - 分数高 → 这篇新闻跟国家政策"很像"（语义对齐度高）
      - 分数低 → 这篇新闻跟国家政策"不太像"（语义对齐度低）

    后续 Stage 45 会结合词频维度（Stage 12/14）把每篇新闻归入四个象限:
      Token (词频高+对齐低=洗科技) / Hidden (词频低+对齐高=闷声干大事) /
      Substantive (词频高+对齐高=言行一致) / Irrelevant (词频低+对齐低=不相关)

    Args:
        df: 含 '标题' 和 '内容' 列的 DataFrame (来自 14_fintech_intensity.parquet)

    Returns:
        DataFrame: 新增 'policy_cosine_sim' 列
    """
    logger.info("=" * 60)
    logger.info("开始计算: 文章级政策语义对齐度 (Stage 15)")
    logger.info("=" * 60)

    # ---- 4.1 加载权威政策文本 ----
    # 【术语】权威政策语料 = 国家级金融科技宏观政策文件的拼接文本
    #   与 Stage 26 (26_authoritative_similarity.py L106) 共享同一份语料
    # 【白话】读取国家的重磅政策文件，作为"标准答案"
    # Phase 1 重构: 通过 CONFIG['paths']['authoritative_corpus_file'] 读取，
    # 替代旧的 os.path.dirname(__file__) + 'config/' 硬编码。
    auth_path = CONFIG['paths'].get(
        'authoritative_corpus_file',
        os.path.join(os.path.dirname(__file__), 'config', 'authoritative_corpus.txt'),
    )
    # 双模型双轨列契约 (2026-05-29): 早退路径也须产出全部 5 列 (全 NaN), 否则
    # 下游 runner 聚合缺 policy_cosine_sim_t2v_* → export.py REQUIRED_PANEL_COLUMNS
    # 抛 RuntimeError (原 stage 30 退役后 stage 15 是 _t2v 唯一来源)。
    _ALIGN_NAN_COLS = (
        'policy_cosine_sim', 'policy_cosine_sim_full', 'policy_cosine_sim_ctx',
        'policy_cosine_sim_t2v_full', 'policy_cosine_sim_t2v_ctx',
    )

    if not os.path.exists(auth_path):
        logger.warning(f"  找不到权威政策语料: {auth_path}。"
                       f"跳过 Stage 15 计算。")
        for _c in _ALIGN_NAN_COLS:
            df[_c] = np.nan
        return df

    with open(auth_path, 'r', encoding='utf-8') as f:
        auth_lines = [line for line in f if not line.strip().startswith('#')]
        auth_text = '\n'.join(auth_lines).strip()

    if not auth_text:
        logger.warning("  权威政策语料为空。跳过 Stage 15 计算。")
        for _c in _ALIGN_NAN_COLS:
            df[_c] = np.nan
        return df

    logger.info(f"  权威政策语料: {len(auth_text)} 字符")

    # ---- 4.2 构建文章输入文本 (v3.6.0 Plan E P3 B2: 双轨) ----
    # 【术语】full 轨 = 标题 + 全文; ctx 轨 = content_ctx (= 标题 + 实体局部窗口,
    #   上游 stage 13 ctx_materializer 已 prepend 标题, remove-title-track 终态:
    #   full/ctx 两轨均含同一标题前缀)
    # 【白话】两条轨道分别打分:
    #   - full: 整篇新闻 vs 政策 (措施层 — Hassan 2019 macro 类比)
    #   - ctx:  目标银行那段 vs 政策 (实体特异性 — Tetlock 2007 / L&M 2016)
    titles = df['标题'].fillna('').astype(str)
    contents = df['内容'].fillna('').astype(str)
    full_texts = (titles + ' ' + contents).tolist()

    has_ctx = 'content_ctx' in df.columns
    if has_ctx:
        ctx_texts = df['content_ctx'].fillna('').astype(str).tolist()
        logger.info(f"  双轨输入: full={len(full_texts)} | ctx={len(ctx_texts)}")
    else:
        logger.warning(
            "  content_ctx 列缺失 (stage 13 未跑?), ctx 轨回退至 full — "
            "此时 policy_cosine_sim_ctx ≡ _full, 不构成真双轨")
        ctx_texts = full_texts

    # 处理 full 轨 raw_texts (与下游保持兼容名)
    raw_texts = full_texts
    logger.info(f"  文章总数: {len(raw_texts)}")

    # ---- 4.3 Token 精确截断 ----
    # 【术语】使用 tiktoken cl100k_base 编码器精确计算每篇文章的 token 数
    #   超过 8191 tokens 的文章截断至上限 (API 硬性限制，超限报 HTTP 400)
    #   与 Stage 25 的字符级粗略截断 (t[:8000]) 不同
    # 【白话】数一数每篇文章有多少个"令牌"，太长就截短
    logger.info("  正在计算 token 数并截断超限文章...")
    truncated_texts = []
    token_counts = []
    n_truncated = 0

    for text in raw_texts:
        n_tok = _count_tokens(text)
        if n_tok > _MAX_TOKENS_PER_INPUT:
            text = _truncate_to_max_tokens(text, _MAX_TOKENS_PER_INPUT)
            n_tok = _MAX_TOKENS_PER_INPUT
            n_truncated += 1
        truncated_texts.append(text)
        token_counts.append(n_tok)

    avg_tokens = np.mean(token_counts) if token_counts else 0
    logger.info(f"  Token 统计: 平均 {avg_tokens:.0f} tokens/篇, "
                f"截断 {n_truncated}/{len(raw_texts)} 篇")

    # ---- 4.4 权威政策文本分段 (Chunk-then-Pool) ----
    # 【术语】Early Chunking + Mean Pooling (Günther et al., 2024; Reimers &
    #   Gurevych, 2019): 将超长锚点文本按 token 上限切分为 K 个不重叠段，
    #   各段独立嵌入后均值池化为单个锚点向量，保留全部语义信息。
    # 【白话】政策文件可能远超模型单条输入上限 (8,191 tokens)，所以按实际 token
    #   数切成多段分别处理，最后取平均，5 份文件的内容都不会被丢弃。
    auth_chunks = _split_into_chunks(auth_text, _MAX_TOKENS_PER_INPUT)

    # ---- 4.4b ctx 轨 token 截断 (v3.6.0 P3 B2) ----
    truncated_ctx_texts = []
    ctx_token_counts = []
    n_truncated_ctx = 0
    for text in ctx_texts:
        n_tok = _count_tokens(text)
        if n_tok > _MAX_TOKENS_PER_INPUT:
            text = _truncate_to_max_tokens(text, _MAX_TOKENS_PER_INPUT)
            n_tok = _MAX_TOKENS_PER_INPUT
            n_truncated_ctx += 1
        truncated_ctx_texts.append(text)
        ctx_token_counts.append(n_tok)
    logger.info(f"  ctx 轨 token: 截断 {n_truncated_ctx}/{len(ctx_texts)} 篇")

    # ---- 4.5 双模型嵌入 + 余弦相似度 (v3.7.5: dual-model) ----
    # 【术语】Hoberg & Phillips (2016, JPE, §III) 余弦相似度;
    #   v3.6.0 Plan E P3 B2 full/ctx 双轨; v3.7.5 在其上叠加 MAIN/ROBUSTNESS
    #   双模型: MAIN = text-embedding-3-small (API, 1536 维) → canonical 列,
    #   ROBUSTNESS = shibing624/text2vec (local, 768 维) → _t2v 列。
    # 【关键】两个模型各嵌各的 anchors/texts, 绝不混算 (维度不同 + 语义空间不同)。
    #   embedding 取得统一经 _eng (本地 vs API 由 spec 内部分派, 不再 inline if)。
    # 【白话】同一批新闻用两个不同模型各算一遍政策对齐分, text2vec 那遍是
    #   稳健性对照, 列名加 _t2v 后缀; 主轨 (API) 列名保持不变。
    df = df.copy()

    # --- MAIN (canonical) 轨: 列名 byte-for-byte 不变 ---
    sim_scores_full, sim_scores_ctx = _cosine_for_spec(
        truncated_texts, truncated_ctx_texts, auth_chunks, EMBEDDING_CONFIG)
    if sim_scores_full is None or sim_scores_ctx is None:
        # F1 fix (2026-05-30): MAIN 失败也须产出全部 5 列 (含 _t2v, 全 NaN), 与
        # 上面两个 auth 早退路径对称。否则缺 policy_cosine_sim_t2v_* → 下游
        # export.py::REQUIRED_PANEL_COLUMNS 抛 RuntimeError (stage 30 退役后
        # stage 15 是 policy_cosine_sim_t2v 的唯一来源)。
        logger.error("  ⚠️ MAIN spec 嵌入失败, canonical + _t2v 全 5 列置 NaN "
                     "(保持双模型 5 列契约)")
        for _c in _ALIGN_NAN_COLS:
            df[_c] = np.nan
        return df

    df['policy_cosine_sim_full'] = sim_scores_full.astype(np.float32)
    df['policy_cosine_sim_ctx'] = sim_scores_ctx.astype(np.float32)
    # legacy alias = _full (v3.5.0 schemas.py 契约保留, 9 paper 迁移后可弃)
    df['policy_cosine_sim'] = df['policy_cosine_sim_full']

    # --- ROBUSTNESS (_t2v) 轨: 失败不破坏 canonical, 仅 _t2v 列置 NaN ---
    t2v_full, t2v_ctx = _cosine_for_spec(
        truncated_texts, truncated_ctx_texts, auth_chunks, _ROBUSTNESS_SPEC)
    if t2v_full is None or t2v_ctx is None:
        logger.warning(
            "  ROBUSTNESS (text2vec) 嵌入失败, "
            "policy_cosine_sim_t2v_{full,ctx} 置 NaN (canonical 不受影响)")
        df['policy_cosine_sim_t2v_full'] = np.nan
        df['policy_cosine_sim_t2v_ctx'] = np.nan
    else:
        df['policy_cosine_sim_t2v_full'] = t2v_full.astype(np.float32)
        df['policy_cosine_sim_t2v_ctx'] = t2v_ctx.astype(np.float32)

    # ---- 4.7 统计报告 ----
    logger.info(f"  ✅ policy_cosine_sim 双轨计算完成:")
    logger.info(f"     full 范围: [{sim_scores_full.min():.4f}, {sim_scores_full.max():.4f}], "
                f"均值={sim_scores_full.mean():.4f}, σ={sim_scores_full.std():.4f}")
    logger.info(f"     ctx  范围: [{sim_scores_ctx.min():.4f}, {sim_scores_ctx.max():.4f}], "
                f"均值={sim_scores_ctx.mean():.4f}, σ={sim_scores_ctx.std():.4f}")

    # 双轨独立性诊断 (Plan E 验收门)
    try:
        from scipy.stats import spearmanr
        # 常量输入 (min == max, 零方差) 时 Spearman ρ 无定义, scipy 会发
        # ConstantInputWarning。退化场景 (如双轨完全一致或样本极小) 下该诊断无
        # 意义, 显式跳过避免未预期告警, 并防止 rho=nan 误判为 "⚠ 高度相关"。
        full_constant = sim_scores_full.min() == sim_scores_full.max()
        ctx_constant = sim_scores_ctx.min() == sim_scores_ctx.max()
        if full_constant or ctx_constant:
            logger.info("     双轨独立性诊断: 输入为常量 (零方差), "
                        "Spearman ρ 无定义, 跳过")
        else:
            rho, _ = spearmanr(sim_scores_full, sim_scores_ctx)
            logger.info(f"     双轨独立性诊断: Spearman ρ = {rho:.4f} "
                        f"({'真双轨' if abs(rho) < 0.95 else '⚠ 高度相关'})")
    except ImportError:
        pass

    # 值域断言 (双轨同时检)
    for name, scores in [('full', sim_scores_full), ('ctx', sim_scores_ctx)]:
        assert scores.min() >= -1.0 - 1e-6, \
            f"policy_cosine_sim_{name} 下界异常: {scores.min()}"
        assert scores.max() <= 1.0 + 1e-6, \
            f"policy_cosine_sim_{name} 上界异常: {scores.max()}"

    return df


# ============================================================================
# 5. 入口函数
# ============================================================================

def main():
    """Stage 15 主入口。

    数据流: 14_fintech_intensity.parquet → 15_article_alignment.parquet
    新增列: policy_cosine_sim (float32, 值域 [-1, 1])
    """
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")

    # 读取 Stage 14 输出
    output_dir = CONFIG['paths']['output_dir']
    input_filename = CONFIG['filenames'].get(
        'output_14_fintech_intensity', '14_fintech_intensity.parquet')
    input_path = os.path.join(output_dir, input_filename)

    if not os.path.exists(input_path):
        logger.error(f"输入文件未找到: {input_path}")
        raise SystemExit(1)

    logger.info(f"加载输入: {input_path}")
    df = pd.read_parquet(input_path)
    logger.info(f"输入数据: {len(df)} 篇文档, {len(df.columns)} 列")

    # 执行计算
    df = compute_article_policy_alignment(df)

    # 列完整性断言
    assert 'policy_cosine_sim' in df.columns, "policy_cosine_sim 列缺失!"
    assert 'fintech_intensity_score' in df.columns, \
        "原有列 fintech_intensity_score 丢失! (零破坏性违规)"
    assert 'fintech_distinct_keywords' in df.columns, \
        "原有列 fintech_distinct_keywords 丢失! (零破坏性违规)"

    # 保存输出
    output_filename = CONFIG['filenames'].get(
        'output_15_article_alignment', '15_article_alignment.parquet')
    output_path = os.path.join(output_dir, output_filename)

    from news_process.core.logging import log_stage_summary
    from news_process.core.reporting import save_dataset
    # 使用数据版本控制保存
    input_file = os.path.join(CONFIG['paths']['output_dir'],
                              CONFIG['filenames']['output_14_fintech_intensity'])
    save_dataset(
        df=df,
        output_path=output_path,
        logger=logger,
        stage_name="15_article_policy_alignment",
        config=CONFIG,
        input_files=[input_file],
    )

    # 统计报告
    n_valid = df['policy_cosine_sim'].notna().sum()
    logger.info(f"  有效 policy_cosine_sim: {n_valid}/{len(df)} "
                f"({n_valid / max(len(df), 1) * 100:.1f}%)")

    log_stage_summary(logger, STAGE_NAME, stage_start, len(df), len(df))
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


if __name__ == "__main__":
    main()
