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
import asyncio
import time
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

# LLM API 配置（复用 tone_llm_processing 节中的 base_url 和 api_key）
LLM_CONFIG = CONFIG.get('tone_llm_processing', {})

# Stage 名称
STAGE_NAME = "15_article_policy_alignment"

# ============================================================================
# 2. tiktoken 精确 Token 计数器
# ============================================================================
# 【术语】使用 OpenAI 官方的 tiktoken 库和 cl100k_base 编码器精确计算 token 数
#   text-embedding-3-small 使用 cl100k_base 编码，单条输入上限 8191 tokens
#   参考: OpenAI 官方文档 — Embeddings API
# 【白话】把文字变成模型能读的"令牌"，然后数一数有多少个
#   中文大约 1 个字 = 1.5~2 个令牌
#   如果超过 8191 个令牌，就只保留前 8191 个（模型的硬性上限）

_ENCODING = tiktoken.get_encoding("cl100k_base")
_ALIGN_CFG = CONFIG.get('article_alignment', {})


def _coerce_positive_int(value, default: int) -> int:
    """配置兜底: 将 token 上限解析为正整数，异常时回退到安全默认值。

    【术语】防御式类型校验 (Defensive Type Coercion)
      YAML 1.1 规范下，未加引号的数字值会被 PyYAML 自动推断为 int/float，
      但加了引号的 "8191" 会被解析为 str。此函数统一处理两种情况，
      确保下游 token 切片逻辑 (tokens[:max_tokens]) 的操作数始终为 int。
      与 Stage 25 (25_strategic_differentiation.py L152-158) 保持一致，
      维护流水线跨阶段的配置解析行为一致性 (Configuration Consistency)。
    【白话】config.yaml 里的数字可能被误写成字符串或留空 (null)，
      这个函数确保无论怎么写，最终拿到的都是一个正整数。
      如果实在解析不了，就用安全的默认值兜底，不会让流水线崩溃。

    Args:
        value: 从 config.yaml 读取的原始值 (可能是 int, str, None 等)
        default: 解析失败时的回退默认值

    Returns:
        int: 正整数配置值。若 value 无法解析或 <= 0，返回 default。
    """
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
    """精确计算文本的 token 数。

    【术语】使用 tiktoken cl100k_base 编码器 (text-embedding-3-small 的编码器)
    【白话】数一数这段文字要用多少个"令牌"来表示
    """
    return len(_ENCODING.encode(text))


def _truncate_to_max_tokens(text: str, max_tokens: int = _MAX_TOKENS_PER_INPUT) -> str:
    """将文本精确截断至不超过 max_tokens 个 token。

    【术语】使用 tiktoken 编码→截断→解码三步法，确保结果严格不超限
      - 与 Stage 25 的字符级粗略截断 (t[:8000]) 不同，本函数在 token 粒度操作
      - 原因: 8000 中文字 ≈ 12,000~16,000 tokens，远超 8191 token 上限
    【白话】如果文章太长（超过 ~4000 中文字），就只保留前面的部分
      绝大多数新闻不会超限，只有极长的万字报告会被截断

    Args:
        text: 原始文本
        max_tokens: 最大 token 数 (默认 8191)

    Returns:
        截断后的文本（token 数 ≤ max_tokens）
    """
    tokens = _ENCODING.encode(text)
    if len(tokens) <= max_tokens:
        return text
    return _ENCODING.decode(tokens[:max_tokens])


def _split_into_chunks(text: str, max_tokens: int = _MAX_TOKENS_PER_INPUT) -> list[str]:
    """将超长文本按 token 粒度切分为多个不重叠分段。

    【术语】Early Chunking (Günther et al., 2024, arXiv:2409.04701):
      对超过 Embedding 模型单条上限的长文本，先按固定 token 数切分为 K 个
      不重叠段，各段独立嵌入后均值池化 (Mean Pooling)，是 API 调用场景下
      长文档嵌入的标准基线方案。
      池化策略依据: Reimers & Gurevych (2019, EMNLP, DOI: 10.18653/v1/D19-1410)
      确认 Mean Pooling 在三种池化方式 (CLS/Mean/Max) 中综合表现最优。
    【白话】把超长政策文件切成多段，每段不超过模型容量上限 (8,191 tokens)，
      之后分别处理再取平均，这样 5 份政策文件的全部语义信息都能保留。

    Args:
        text: 原始文本
        max_tokens: 每段最大 token 数 (默认 8191)

    Returns:
        list[str]: 分段文本列表，每段 token 数 ≤ max_tokens。
                   若原文未超限，返回包含原文的单元素列表。
    """
    tokens = _ENCODING.encode(text)
    if len(tokens) <= max_tokens:
        return [text]  # 未超限，原样返回，避免 encode/decode 往返引入编码伪影
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunks.append(_ENCODING.decode(tokens[i:i + max_tokens]))
    return chunks


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

async def _get_embeddings_api_dynamic(texts: list[str], token_counts: list[int]) -> np.ndarray:
    """通过 API 获取文本 Embedding 向量 — 动态批量策略。

    【术语】
    与 Stage 25 的 _get_embeddings_api() (L358-390) 功能等价，但批量策略不同:
      - Stage 25: 固定每批 100 条 (L375)
      - Stage 15: 动态批量，按 token 总数切分 (MAX_TOKENS_PER_REQUEST = 250,000)

    API 限制 (经验证):
      - 单条输入上限: 8,191 tokens (OpenAI 官方文档)
      - 单次请求总 token 上限: 300,000 tokens (OpenAI 官方文档)
      - 超限行为: HTTP 400 BadRequestError (不会自动截断)

    【白话】把一批文章发给 AI 模型，让它把每篇文章变成一个数字向量。
    为了不超过模型的容量限制，每次发送的文章总字数不超过 25 万个令牌。

    Args:
        texts: 已截断至 8191 tokens 的文本列表
        token_counts: 每篇文本对应的 token 数

    Returns:
        np.ndarray: Embedding 矩阵 (N × d)，d = 1536 for text-embedding-3-small

    Raises:
        RuntimeError: API 返回非 200 状态码
    """
    import aiohttp
    # --- 配置提取与前置校验 (Fail-Fast) ---
    # 【术语】Fail-Fast 原则: 在函数入口处立即校验所有必要前置条件,
    #   而非等到实际调用 API 时才发现配置缺失。这避免了在已消耗大量
    #   计算资源 (如 token 计数、批量切分) 后才崩溃的浪费。
    # 【白话】先检查"钥匙"和"地址"有没有配好，没配好就立刻报错,
    #   不要等到真正要开门的时候才发现没带钥匙。
    models = LLM_CONFIG.get('models') or []
    cfg = models[0] if models else {}
    base_url = cfg.get('base_url')
    api_key = cfg.get('api_key')
    if not base_url or not api_key:
        raise RuntimeError(
            "Embedding API 配置缺少 base_url 或 api_key "
            "(检查 config.yaml → tone_llm_processing → models)")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # --- 动态批量切分 ---
    # 按 token 总数切分批次，而非固定条数
    batches = []
    current_batch = []
    current_tokens = 0
    for i, (text, n_tok) in enumerate(zip(texts, token_counts)):
        if current_batch and current_tokens + n_tok > _MAX_TOKENS_PER_REQUEST:
            batches.append(current_batch)
            current_batch = []
            current_tokens = 0
        current_batch.append(text)
        current_tokens += n_tok
    if current_batch:  # 最后一批
        batches.append(current_batch)

    logger.info(f"    Embedding 动态分批: {len(batches)} 批, "
                f"共 {len(texts)} 篇, 总 {sum(token_counts):,} tokens")

    # --- 逐批请求 ---
    all_emb = []
    async with aiohttp.ClientSession() as session:
        for batch_idx, batch in enumerate(batches):
            async with session.post(
                f"{base_url}/embeddings",
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

    # 【术语】Embedding 对齐不变量 (Alignment Invariant):
    #   输入 N 条文本必须精确返回 N 个向量。若不等, 说明 API 静默
    #   丢弃了某些输入 (如空字符串或超长文本), 后续 cosine_similarity
    #   矩阵的行索引会与 DataFrame 行索引错位, 导致 policy_cosine_sim
    #   列被错误赋值到不相关的文章上——这是无法通过下游断言检测的
    #   "静默数据污染" (Silent Data Corruption)。
    #   与 Stage 25 (25_strategic_differentiation.py L486-488) 的防护标准对齐。
    # 【白话】发出去 100 篇文章, 必须拿回 100 个向量。如果 API 偷偷吞了
    #   几篇, 后面算出来的相似度就会张冠李戴——这种错误最危险, 因为
    #   程序不会报错, 但数据已经错了。
    if len(all_emb) != len(texts):
        raise RuntimeError(
            f"Embedding API 返回数量异常: expected {len(texts)}, "
            f"got {len(all_emb)}")
    return np.array(all_emb)


def _get_embeddings_with_fallback(texts: list[str], token_counts: list[int]) -> np.ndarray | None:
    """三层降级策略获取 Embedding 向量。

    【术语】复用 Stage 25 (L393-426) 的三层降级逻辑:
      1. API (text-embedding-3-small) — 首选, 质量最高, 1536 维
      2. sentence-transformers (shibing624/text2vec-base-chinese) — 本地备选
      3. None — 跳过，返回 None

    【白话】优先用在线 AI 模型（效果最好），如果在线不行就用本地模型，
    如果本地也不行就放弃。

    Args:
        texts: 已截断的文本列表
        token_counts: 每篇文本的 token 数

    Returns:
        np.ndarray (N × d) 或 None (降级失败)
    """
    # 策略 1: API Embedding
    try:
        emb = asyncio.run(_get_embeddings_api_dynamic(texts, token_counts))
        logger.info(f"    Embedding: API (text-embedding-3-small) 成功, "
                    f"维度 {emb.shape}")
        return emb
    except Exception as e:
        logger.warning(f"    Embedding API 降级: {type(e).__name__}: {e}")

    # 策略 2: 本地 sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('shibing624/text2vec-base-chinese')
        emb = model.encode(texts, show_progress_bar=True, batch_size=64)
        logger.info(f"    Embedding: 本地 text2vec-base-chinese 成功, "
                    f"维度 {emb.shape}")
        return np.array(emb)
    except Exception as e2:
        logger.warning(f"    Embedding 完全降级: {type(e2).__name__}: {e2}")

    # 策略 3: 放弃
    return None


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
    auth_path = os.path.join(os.path.dirname(__file__),
                             'config', 'authoritative_corpus.txt')
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

    emb = _get_embeddings_with_fallback(all_texts, all_token_counts)

    if emb is None:
        logger.error("  Embedding 获取完全失败。所有文章 policy_cosine_sim 设为 NaN。")
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
        return

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

    from utils.helpers import save_dataset, log_stage_summary
    save_dataset(df, output_path, logger)

    # 统计报告
    n_valid = df['policy_cosine_sim'].notna().sum()
    logger.info(f"  有效 policy_cosine_sim: {n_valid}/{len(df)} "
                f"({n_valid / max(len(df), 1) * 100:.1f}%)")

    log_stage_summary(logger, STAGE_NAME, stage_start, len(df), len(df))
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


if __name__ == "__main__":
    main()
