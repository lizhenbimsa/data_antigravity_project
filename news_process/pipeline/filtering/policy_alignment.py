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

import os
import sys
import asyncio
import time
import numpy as np
import pandas as pd
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
from news_process.pipeline.panel.encode import logger, CONFIG  # noqa: E402

# LLM API 配置（复用 tone_llm_processing 节中的 base_url 和 api_key）
LLM_CONFIG = CONFIG.get('tone_llm_processing', {})
EMBEDDING_CONFIG = CONFIG.get('embedding_api', {})
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

async def _get_embeddings_api_dynamic(texts: list[str], token_counts: list[int], cache: LLMCache = None) -> np.ndarray:
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
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # --- 1. 穿透式缓存层 ---
    cached_results = [cache.get(embedding_model, text) if cache else None for text in texts]
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
                                        [json.dumps(emb) for emb in batch_embs]
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
# 4. 主流程函数
# ============================================================================

def compute_article_policy_alignment(df: pd.DataFrame) -> pd.DataFrame:
    """计算文章级政策语义对齐度 (Article-level Policy Cosine Similarity)。

    【学术支撑】
    本函数实现的核心度量：

        policy_cosine_sim_i = cos(emb(article_i), emb(auth_text))

    其中:
      - emb() 为 text-embedding-3-small 的稠密语义编码 (1536 维)
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
    if not os.path.exists(auth_path):
        logger.warning(f"  找不到权威政策语料: {auth_path}。"
                       f"跳过 Stage 15 计算。")
        df['policy_cosine_sim'] = np.nan
        return df

    with open(auth_path, 'r', encoding='utf-8') as f:
        auth_lines = [line for line in f if not line.strip().startswith('#')]
        auth_text = '\n'.join(auth_lines).strip()

    if not auth_text:
        logger.warning("  权威政策语料为空。跳过 Stage 15 计算。")
        df['policy_cosine_sim'] = np.nan
        return df

    logger.info(f"  权威政策语料: {len(auth_text)} 字符")

    # ---- 4.2 构建文章输入文本 ----
    # 【术语】输入文本 = 标题 + 全文正文，不做字数截断
    #   仅在 token 层面进行精确截断 (8191 tokens 硬性上限)
    #   列名已验证: '标题' (12_news_fintech.py L134), '内容' (L133)
    # 【白话】把每篇新闻的标题和正文拼在一起，作为这篇新闻的完整代表
    titles = df['标题'].fillna('').astype(str)
    contents = df['内容'].fillna('').astype(str)
    raw_texts = (titles + ' ' + contents).tolist()

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
    auth_chunk_tok_counts = [_count_tokens(c) for c in auth_chunks]
    auth_total_tokens = sum(auth_chunk_tok_counts)
    logger.info(f"  政策文本: {auth_total_tokens:,} tokens → "
                f"{len(auth_chunks)} 段 (Chunk-then-Pool)")

    # ---- 4.5 获取 Embedding ----
    # 【术语】新闻文章 + 政策分段共用同一 API 调用流 (动态批量调度)
    #   政策分段放在列表末尾 (与 Stage 26 的 Ghost Anchor 策略一致)
    # 【白话】把所有"考生答卷"和"切段后的标准答案"一起送去打分
    all_texts = truncated_texts + auth_chunks
    all_token_counts = token_counts + auth_chunk_tok_counts

    with LLMCache(CACHE_DB_PATH) as cache:
        emb = asyncio.run(_get_embeddings_api_dynamic(all_texts, all_token_counts, cache))

    # 死战不退机制保证了 emb 绝对不是 None 且不含 NaN，若 API 实在不可恢复，程序早就中断了
    if emb is None or len(emb) == 0:
        logger.error("  Embedding 获取失败或为空，终止计算。")
        df['policy_cosine_sim'] = np.nan
        return df

    # ---- 4.6 计算余弦相似度 ----
    # 【术语】
    #   article_embs: 所有文章的 Embedding 向量 (N × d)
    #   auth_emb: 权威政策的 Embedding 向量 (1 × d)
    #   policy_cosine_sim = cos(article_embs, auth_emb)
    #   公式: cos(A,B) = (A·B) / (||A|| × ||B||)，值域 [-1, 1]
    #
    #   参考: Hoberg & Phillips (2016, JPE, §III) — 余弦相似度作为
    #   文本语义距离的标准度量
    #
    # 【白话】计算每篇新闻跟政策的"方向夹角"——角度越小（分数越高），
    #   说明这篇新闻跟政策越像
    from sklearn.metrics.pairwise import cosine_similarity

    # 分离: 前 N 个 = 文章, 后 K 个 = 政策分段
    n_articles = len(truncated_texts)
    article_embs = emb[:n_articles]        # N × 1536
    auth_chunk_embs = emb[n_articles:]     # K × 1536

    # 均值池化 + L2 归一化 → 单个政策锚点向量
    # 【术语】Mean Pooling (Reimers & Gurevych, 2019, EMNLP,
    #   DOI: 10.18653/v1/D19-1410): 对 K 个分段向量取算术均值后
    #   L2 归一化，生成文档级语义表示。
    # 【白话】把 K 段的向量取平均，得到一个代表全部政策的"标准答案向量"
    auth_emb = auth_chunk_embs.mean(axis=0, keepdims=True)  # (1, 1536)
    auth_norm = np.linalg.norm(auth_emb, axis=1, keepdims=True)
    if auth_norm.item() > 0:
        auth_emb = auth_emb / auth_norm
    else:
        logger.error("  ⚠️ 政策锚点均值池化后范数为零!")
        df['policy_cosine_sim'] = np.nan
        return df
    logger.info(f"  政策锚点: {len(auth_chunk_embs)} 段 → "
                f"Mean Pooling → 1 个 {auth_emb.shape[1]}D 向量")

    # cosine_similarity 返回 (N, 1)，取 [:, 0] 展平为 (N,)
    sim_scores = cosine_similarity(article_embs, auth_emb)[:, 0]

    df = df.copy()
    df['policy_cosine_sim'] = sim_scores.astype(np.float32)

    # ---- 4.7 统计报告 ----
    logger.info(f"  ✅ policy_cosine_sim 计算完成:")
    logger.info(f"     范围: [{sim_scores.min():.4f}, {sim_scores.max():.4f}]")
    logger.info(f"     均值: {sim_scores.mean():.4f}, 标准差: {sim_scores.std():.4f}")
    logger.info(f"     中位数: {np.median(sim_scores):.4f}")

    # 值域断言
    assert sim_scores.min() >= -1.0 - 1e-6, \
        f"policy_cosine_sim 下界异常: {sim_scores.min()}"
    assert sim_scores.max() <= 1.0 + 1e-6, \
        f"policy_cosine_sim 上界异常: {sim_scores.max()}"

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

    from news_process.core.reporting import save_dataset
    from news_process.core.logging import log_stage_summary
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
