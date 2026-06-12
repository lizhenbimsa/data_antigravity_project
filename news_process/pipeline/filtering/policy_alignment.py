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
  15_article_alignment.parquet (= 原数据 + 新增 5 列: policy_cosine_sim
  (legacy alias = _full) + policy_cosine_sim_{full,ctx} 双轨
  + policy_cosine_sim_t2v_{full,ctx} 双模型稳健 twin)
============================================================================
"""

import asyncio
import json
import os
import re as _re
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
# 2b. 权威政策语料 vintage 解析 (fix(omni-g-policy-02, 2026-06-11))
# ============================================================================
# 【术语】Vintage-aware Anchor: 静态权威语料把 2015-2025 间发布的 6 份政策文件
#   拼接为单一锚点 → 时刻 t 的 policy_cosine_sim / auth_sim_* 嵌入了 t 期不可知
#   的未来政策语言 (look-ahead bias, 前视构造)。修复: 语料按文档切分并解析发布
#   年份 (vintage), 消费方对年度 t 仅用发布年份 ≤ t 的文档段构造锚点。
# 【白话】2017 年的新闻不该拿来跟 2022 年才发布的政策文件比"像不像"——
#   那时政策还没出生。所以把语料库按"哪年发布"拆开, 算哪一年就只用那一年
#   (含) 之前已经发布的政策文件当"标准答案"。
# 年份来源优先级: 语料内 `# [VINTAGE YYYY]` 标注行 > 文档前部落款日期行
#   (如 "2019 年 8 月") > 文号 `〔YYYY〕N号` 的最大年份。仍解析不出 → 默认取
#   语料库最早年份并在日志披露 (master 设计决定: 无法解析年份默认最早年)。

# 标注行: `# [VINTAGE 2021] <标题> — <发布依据>` (注释剥离机制保证不进入锚点文本)
_VINTAGE_MARKER_RE = _re.compile(r'^#\s*\[VINTAGE\s+((?:19|20)\d{2})(?:-\d{1,2})?\]')
# 落款日期行: 独占一行的 "YYYY年M月" (容忍全角空格/半角空格)
_DATE_LINE_RE = _re.compile(r'^[\s　]*((?:19|20)\d{2})\s*年\s*\d{1,2}\s*月[\s　]*$')
# 文号: 〔YYYY〕N号 / [YYYY]N号 (如 银发〔2015〕221号、国办发〔2025〕8号)
_DOCNO_RE = _re.compile(r'[〔\[]\s*((?:19|20)\d{2})\s*[〕\]]\s*\d+\s*号')

# fix(omni-g-policy-01, 2026-06-11): 与新闻侧预处理对称的敏感词清除。
# preprocess/normalize.py::_clean_single_text 步骤 2.5 对全部新闻标题/内容无条件
# 删除 '习近平'; 权威语料此前裸读不经该规则 → 相似度两端文本预处理不对称
# (语料 6 处 vs 新闻侧 0 处)。此处镜像同一规则使两端口径一致 (对称清洗级,
# 裁决: 锚为全行共享常量, 实测效应 ≤3.2e-3, P3 披露级)。
_LEADER_NAME_TOKENS = ('习近平',)


def _strip_leader_names(text: str) -> str:
    """对语料文本应用与 normalize.py 步骤 2.5 相同的敏感词删除 (对称清洗)。"""
    for tok in _LEADER_NAME_TOKENS:
        text = text.replace(tok, '')
    return text


def load_policy_corpus_docs(auth_path: str) -> list[dict]:
    """加载权威政策语料并按文档切分, 解析各文档 vintage 年份。

    fix(omni-g-policy-01/02, 2026-06-11) 语义披露:
      - 文本经 _strip_leader_names 对称清洗 (与新闻侧 normalize 步骤 2.5 同规则);
      - 文档切分: `# [VINTAGE]` 标注行优先, 无标注时按 ≥3 连续空行分隔;
      - 年份解析失败的文档默认取语料库最早已知年份, 并 logger.warning 披露。

    Returns:
        list[dict]: [{'text': str, 'year': int | None, 'year_imputed': bool}, ...]
        year 仅当全语料无任何可解析年份时为 None (消费方应退化为静态锚点并披露)。
    """
    docs: list[dict] = []
    cur_year: int | None = None
    cur_lines: list[str] = []
    blank_run = 0

    def _flush():
        nonlocal cur_year, cur_lines
        text = _strip_leader_names('\n'.join(cur_lines).strip())
        if text:
            year = cur_year
            if year is None:
                # 回退正则: 文档前 5 个非空行找落款日期, 其次全文文号取最大年份
                head = [ln for ln in cur_lines if ln.strip()][:5]
                for ln in head:
                    m = _DATE_LINE_RE.match(ln)
                    if m:
                        year = int(m.group(1))
                        break
                if year is None:
                    docno_years = [int(y) for y in _DOCNO_RE.findall(text)]
                    if docno_years:
                        year = max(docno_years)
            docs.append({'text': text, 'year': year, 'year_imputed': False})
        cur_year, cur_lines = None, []

    with open(auth_path, 'r', encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.rstrip('\n')
            marker = _VINTAGE_MARKER_RE.match(line.strip())
            if marker:
                if cur_lines:
                    _flush()
                cur_year = int(marker.group(1))
                blank_run = 0
                continue
            if line.strip().startswith('#'):
                continue  # 注释剥离机制 (Anti-Pollution Filter)
            if not line.strip():
                blank_run += 1
                # 无标注语料的回退切分: ≥3 连续空行 = 文档分隔符
                if blank_run >= 3 and cur_lines:
                    _flush()
                continue
            blank_run = 0
            cur_lines.append(line)
    if cur_lines:
        _flush()

    known_years = [d['year'] for d in docs if d['year'] is not None]
    if known_years:
        earliest = min(known_years)
        for d in docs:
            if d['year'] is None:
                # master 设计决定: 无法解析年份的锚点段默认最早年 + 披露
                d['year'] = earliest
                d['year_imputed'] = True
                logger.warning(
                    f"  权威语料 vintage: 1 份文档无法解析发布年份, "
                    f"默认归入语料库最早年 {earliest} (前视守卫保守披露): "
                    f"{d['text'][:30]}...")
    else:
        if docs:
            logger.warning(
                "  权威语料 vintage: 全部文档均无法解析发布年份, "
                "无法做 vintage 切分 — 消费方将退化为静态全语料锚点 (前视披露)")
    return docs


def vintage_aware_enabled() -> bool:
    """vintage-aware 锚点开关 (默认 True; 静态全语料旧行为降级为稳健性 opt-out)。

    供 stage 15 (本模块) 与 stage 26 (policy_similarity) 共用 — 两者消费同一语料,
    锚点口径必须一致。config 键: article_alignment.vintage_aware。
    """
    return bool((CONFIG.get('article_alignment') or {}).get('vintage_aware', True))


def vintage_anchor_text(docs: list[dict], year) -> str | None:
    """拼接发布年份 ≤ year 的文档文本作为该年度锚点; 无可用文档 → None。"""
    parts = [d['text'] for d in docs
             if d['year'] is not None and d['year'] <= year]
    joined = '\n\n'.join(parts).strip()
    return joined or None


# ============================================================================
# 3. Embedding API 管线（动态批量）
# ============================================================================
# 【术语】(2026-06-11 注释纠偏, fix(omni-g-policy-04)) 本节的
#   _get_embeddings_api_dynamic 是 **legacy 实现, 生产路径已不再调用**:
#   生产嵌入统一走 pipeline/text/embedding_engine.py::embed_texts
#   (LLMCache 穿透 + 动态分批: 单批 ≤2000 条 且 token 总和 ≤ 上限 + 超长文本
#   Early Chunking + Mean Pooling)。Stage 25/26/27 也走同一引擎 (不存在旧注释
#   所称 "Stage 25 固定每批 100 条" — 该描述已随引擎统一而过时)。
#   本函数仅余 tests/test_pipeline_robustness.py 引用 (缓存穿透/重试机制单测),
#   保留以维持测试契约; 勿在生产代码中新增调用。

async def _get_embeddings_api_dynamic(
    texts: list[str],
    token_counts: list[int],
    cache: LLMCache = None,
    *,
    prompt_version_override: str | None = None,
) -> np.ndarray:
    """通过 API 获取文本 Embedding 向量 — 穿透式缓存与死战不退容错。

    ⚠ LEGACY (test-only, fix(omni-g-policy-04, 2026-06-11) 标注): 生产调用链已
    全部迁移至 embedding_engine.embed_texts (_cosine_for_spec 内), 本函数生产
    0 调用, 仅 tests/test_pipeline_robustness.py 的缓存穿透/重试单测引用。
    保留以维持测试契约; 勿在生产代码中新增调用。

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
    # Round 4 M8 修: 用参数 prompt_version_override 替代全局 mutation, 避免污染其他 callsite。
    # (2026-06-11 注释纠偏, fix(omni-g-policy-04)): 旧注释所述 "ctx 轨调用方传
    # base+'-ctx' 显式隔离 namespace" 在现行调用链中已不存在 — 生产双轨均经
    # embedding_engine 以同一 text_pipeline_version 入缓存 (键含逐字文本, 天然隔离);
    # override 参数仅为本 legacy 函数的测试接口保留, 勿据此审计生产缓存命名空间。
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
    doc_chunks: list[list[str]],
    spec: dict,
    *,
    doc_years: list | None = None,
    article_years: np.ndarray | None = None,
) -> tuple[np.ndarray | None, np.ndarray | None]:
    """用单一 spec 嵌入 (full / ctx / auth) 并返回 (cos_full, cos_ctx)。

    【关键约束】每个 spec 用**自己的**模型独立嵌入自己的 anchors/texts,
    绝不复用另一 spec 的向量 (API 1536 维 vs text2vec 768 维, 严禁混算)。

    fix(omni-g-policy-02, 2026-06-11) 语义变更: 锚点改为 vintage-aware —
    传入 doc_years (各政策文档发布年份) + article_years (各文章年份) 时, 年度 t
    的文章只与发布年份 ≤ t 的政策文档段的池化锚点算余弦 (消除前视构造);
    无 ≤t 文档的年份与年份未知的文章 → NaN。两参数任一为 None → 静态全语料
    锚点 (旧行为, 仅作稳健性/降级路径)。

    流程:
      1. 用 spec 经 _eng.embed_texts 分别嵌入 full_texts / ctx_texts / 全部文档段
         (text-level, 内部已处理 chunk 切分 + mean pooling + local/API 分派)。
      2. 对各年度允许的文档段嵌入做 mean pooling + L2 归一化 → 该年度政策锚点
         向量 (保留 zero-norm 守卫)。
      3. cosine_similarity(full, anchor_year) / cosine_similarity(ctx, anchor_year)。

    Args:
        full_texts: full 轨文本 (不截断; 超长由引擎分段池化)
        ctx_texts:  ctx 轨文本
        doc_chunks: 权威政策语料分段, 按文档分组 (list per 文档)
        spec: embedding spec (MAIN=API / ROBUSTNESS=local)
        doc_years: 各文档 vintage 年份 (与 doc_chunks 对齐); None → 静态锚点
        article_years: (N,) 文章年份 float 数组 (NaN=未知); None → 静态锚点

    Returns:
        (cos_full_array, cos_ctx_array): 各为 (N,) np.ndarray;
        嵌入失败 (embed_texts 返回 None) 或静态锚点范数为零 → (None, None)。
    """
    from sklearn.metrics.pairwise import cosine_similarity

    model_id = _eng.spec_model(spec)
    log_prefix = f"Embedding[{model_id}]"

    auth_chunks = [c for chunks in doc_chunks for c in chunks]
    # 每个分段所属文档下标 (用于 vintage 过滤)
    chunk_doc_idx = np.array(
        [i for i, chunks in enumerate(doc_chunks) for _ in chunks], dtype=int)

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

    def _pooled_anchor(chunk_mask: np.ndarray) -> np.ndarray | None:
        """选中分段 → mean pooling + L2 归一化 → (1, D) 锚点; 范数零 → None。"""
        sub = auth_chunk_embs[chunk_mask]
        anchor = sub.mean(axis=0, keepdims=True)
        norm = np.linalg.norm(anchor, axis=1, keepdims=True)
        if norm.item() <= 0:
            return None
        return anchor / norm

    vintage_mode = (
        doc_years is not None and article_years is not None
        and any(y is not None for y in doc_years)
    )

    if not vintage_mode:
        # 静态全语料锚点 (旧行为; 仅稳健性 opt-out / 无年份信息降级, 调用方已披露)
        auth_emb = _pooled_anchor(np.ones(len(auth_chunks), dtype=bool))
        if auth_emb is None:
            logger.error(f"  ⚠️ {log_prefix}: 政策锚点均值池化后范数为零!")
            return None, None
        logger.info(f"  {log_prefix} 政策锚点(静态): {len(auth_chunk_embs)} 段 → "
                    f"Mean Pooling → 1 个 {auth_emb.shape[1]}D 向量")
        cos_full = cosine_similarity(article_embs_full, auth_emb)[:, 0]
        cos_ctx = cosine_similarity(article_embs_ctx, auth_emb)[:, 0]
        return cos_full, cos_ctx

    # --- vintage-aware: 逐年度构造 ≤t 锚点 ---
    doc_years_arr = np.array(
        [np.nan if y is None else float(y) for y in doc_years], dtype=float)
    n = len(full_texts)
    cos_full = np.full(n, np.nan, dtype=np.float64)
    cos_ctx = np.full(n, np.nan, dtype=np.float64)

    year_vals = np.asarray(article_years, dtype=float)
    n_unknown = int(np.isnan(year_vals).sum())
    if n_unknown:
        logger.warning(f"  {log_prefix}: {n_unknown} 篇文章年份未知, "
                       f"无法做前视守卫 → policy_cosine_sim 置 NaN")

    for year in np.unique(year_vals[~np.isnan(year_vals)]):
        art_mask = year_vals == year
        allowed_docs = ~np.isnan(doc_years_arr) & (doc_years_arr <= year)
        if not allowed_docs.any():
            logger.warning(
                f"  {log_prefix} {int(year)}: 无发布年份 ≤ {int(year)} 的政策"
                f"文档 (前视守卫), 该年 {int(art_mask.sum())} 篇置 NaN")
            continue
        chunk_mask = np.isin(chunk_doc_idx, np.where(allowed_docs)[0])
        anchor = _pooled_anchor(chunk_mask)
        if anchor is None:
            logger.error(f"  ⚠️ {log_prefix} {int(year)}: 锚点范数为零, 该年置 NaN")
            continue
        cos_full[art_mask] = cosine_similarity(
            article_embs_full[art_mask], anchor)[:, 0]
        cos_ctx[art_mask] = cosine_similarity(
            article_embs_ctx[art_mask], anchor)[:, 0]
        logger.info(f"  {log_prefix} 政策锚点(vintage≤{int(year)}): "
                    f"{int(allowed_docs.sum())}/{len(doc_chunks)} 文档 "
                    f"{int(chunk_mask.sum())} 段 → {int(art_mask.sum())} 篇")
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
      - auth_text 为权威政策语料库 (config/authoritative_corpus.txt) 中发布年份
        ≤ 文章年份的文档段拼接 (vintage-aware, fix(omni-g-policy-02, 2026-06-11):
        旧静态全语料锚点含未来政策文本, 构成前视; 现按政策发布年份切分,
        年度 t 只用 t 期已存在的政策文件; 无年份信息时降级为静态锚点并披露)
      - cos(A,B) = (A·B) / (||A|| × ||B||)，值域 [-1, 1]

    该度量直接映射 Distel et al. (2026, Research Policy, §3.2.1) 的方法论:
    对每篇政策文档独立计算与基准文本的语义相似度，以此判定该文档是
    "显性引用" (Token) 还是 "文本级语义实质借鉴" (Hidden)。

    参考: Hassan et al. (2019, QJE) — 将宏观政策文本注入微观企业向量空间

    【白话说明】
    给每篇金融科技新闻打一个对齐分 (余弦相似度, 理论值域 [-1, 1],
    实务上政策语料相似度多落在 0~1 区间; fix(omni-g-policy-04) 纠偏旧 "0~1" 表述)：
      - 分数高 → 这篇新闻跟国家政策"很像"（语义对齐度高）
      - 分数低 → 这篇新闻跟国家政策"不太像"（语义对齐度低）
    且只跟"这篇新闻发表时已经发布"的政策文件比 (vintage-aware, 见上)。

    后续 Stage 45 会结合词频维度（Stage 12/14）把每篇新闻归入四个象限:
      Token (词频高+对齐低=洗科技) / Hidden (词频低+对齐高=闷声干大事) /
      Substantive (词频高+对齐高=言行一致) / Irrelevant (词频低+对齐低=不相关)

    Args:
        df: DataFrame (来自 14_fintech_intensity.parquet)。full 轨优先读 stage 13
            物化的 'content_full' 列; 缺列时回退用 '标题' + '内容' 经 prepend_title 构建。
            ctx 轨读 'content_ctx' 列。

    Returns:
        DataFrame: 新增 'policy_cosine_sim' (legacy alias) + _full/_ctx 双轨
        + _t2v_full/_t2v_ctx 稳健 twin, 共 5 列 (见模块 docstring 输出段)
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

    # fix(omni-g-policy-01/02, 2026-06-11): 经 load_policy_corpus_docs 统一加载 —
    # (01) 语料文本经与新闻侧 normalize 步骤 2.5 相同的敏感词对称清洗;
    # (02) 按政策发布年份 (vintage) 切分为文档列表, 供下方按年构造 ≤t 锚点。
    auth_docs = load_policy_corpus_docs(auth_path)

    if not auth_docs:
        logger.warning("  权威政策语料为空。跳过 Stage 15 计算。")
        for _c in _ALIGN_NAN_COLS:
            df[_c] = np.nan
        return df

    _n_chars = sum(len(d['text']) for d in auth_docs)
    logger.info(f"  权威政策语料: {len(auth_docs)} 份文档 / {_n_chars} 字符, "
                f"vintage 年份: {sorted({d['year'] for d in auth_docs})}")

    # ---- 4.2 构建文章输入文本 (v3.6.0 Plan E P3 B2: 双轨) ----
    # 【术语】full 轨 = 标题 + 全文; ctx 轨 = content_ctx (= 标题 + 实体局部窗口,
    #   上游 stage 13 ctx_materializer 已 prepend 标题, remove-title-track 终态:
    #   full/ctx 两轨均含同一标题前缀)
    # 【白话】两条轨道分别打分:
    #   - full: 整篇新闻 vs 政策 (措施层 — Hassan 2019 macro 类比)
    #   - ctx:  目标银行那段 vs 政策 (实体特异性 — Tetlock 2007 / L&M 2016)
    # P0 修复 (embedding-reuse-audit 2026-06-05, 病根A 残留): full 轨改读 stage 13
    # 物化的 content_full (= prepend_title(标题, 内容)), 替代旧的裸 '标题 + 空格 + 内容'。
    # 两个动机:
    #   (1) embedding 缓存复用: content_full 是逐字节固定的文章级串, 与 **stage 27
    #       (benefit_society) 逐篇嵌入的 content_full 同源** → 同篇文章的
    #       text-embedding-3-small 向量经 LLMCache (键含逐字文本) 只付费一次; 旧空格
    #       口径与 content_full 不同字节 → 互为 cache miss, 各付一次。
    #       ⚠ 复用范围仅限 stage 27: stage 25 (strategic_diff) 嵌的是 (bank,year)
    #       聚合超级文档 (非文章级), 粒度错配不可能共享缓存; tone_words/tone_berts
    #       虽读同一 content_full 源串, 但走词典/BERT 不调 embedding API, 不进此缓存。
    #   (2) full↔ctx 标题对称: full 轨 (含标题) 与 ctx 轨 (content_ctx 含标题) 标题
    #       口径一致 (病根A 同型, 与 fintech_intensity / strategic_diff 等同批修复)。
    # 缺 content_full 列时回退至 prepend_title 内联构建 — 与 stage 13 同函数同输入,
    # 产出字节一致字符串, 故两个分支都能命中 stage 27 的共享缓存。
    if 'content_full' in df.columns:
        full_texts = df['content_full'].fillna('').astype(str).str.strip().tolist()
    else:
        from news_process.core.text.entity_context import prepend_title
        _titles = df.get('标题', pd.Series('', index=df.index)).fillna('').astype(str)
        _contents = df.get('内容', pd.Series('', index=df.index)).fillna('').astype(str)
        full_texts = [prepend_title(t, b).strip() for t, b in zip(_titles, _contents)]

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

    # ---- 4.3 Token 诊断 (无预截断 — 超长由引擎 chunk+pool 接管) ----
    # 【术语】fix(2026-06-12, 选项 B; 镜像 stage 27 omni-g-benefit-04): 移除文章侧
    #   8191-token 预截断。统一引擎 _eng.embed_texts 自带 Early Chunking + token
    #   加权 Mean Pooling (Günther et al. 2024, arXiv:2409.04701; Reimers &
    #   Gurevych 2019, EMNLP), 对超长文章无损分段池化 — 与锚点侧 (4.4) 及 stage
    #   25/26/27 完全同一口径。两侧 (文章 / 政策锚点) 现走**对称** chunk-pool 管线,
    #   符合 Hoberg & Phillips (2016, JPE) / Loughran & McDonald (2011, JF) 文本
    #   相似度 "对比双方同管线、整文不截断" 的顶刊规范 (近期 earnings-call 实证亦
    #   采分段嵌入+平均, 无公认最优池化规则)。
    # 口径变更 (supersedes omni-g-policy-03): 此前为锁 LLMCache 缓存键的字节确定性,
    #   刻意把文章截到前 8191 token (尾部丢弃; 盘上 5/1170 篇受影响, 最长截掉 ~23%)。
    #   现改全文 chunk-pool: API 主轨 ≤8191 token 文章缓存键不变 (旧截断恒等 → cache
    #   hit), 超长文章首块与旧截断文本字节一致 (cache hit), 仅尾部块为新键 → 增量
    #   嵌入仅 ~5 篇尾段 (≈$0 API)。t2v 稳健轨走本地模型不进缓存 (每 run 重算, $0),
    #   其超长文章因本地模型 128-token 边界, 受影响幅度比 API 主轨更大。
    #   ⚠ golden 重生范围**非仅这 ~5 篇**: 四象限分类用年度内分位阈值
    #   (runner._classify_policy_quadrants), 单篇 sim 变动会移动整年度阈值 → 同年度
    #   其它文章归类可能离散翻转, 连带 bank-year 聚合 / *_adopt_* 占比列变 → 须整体
    #   重生 40/51 面板 (test_panel_reproducibility 门覆盖)。本段只保留 token 诊断。
    # 【白话】数一数每篇文章多少 token、有几篇超长 (会被引擎拆段读完再取平均), 但
    #   不再"撕掉尾巴" — 超长文章整篇都算进对齐分, 跟政策文件那侧的处理方式一致。
    logger.info("  正在计算 token 数 (无预截断, 超长走引擎 chunk+pool)...")
    token_counts = [_count_tokens(text) for text in raw_texts]
    n_long = sum(1 for n in token_counts if n > _MAX_TOKENS_PER_INPUT)
    avg_tokens = np.mean(token_counts) if token_counts else 0
    logger.info(f"  Token 统计: 平均 {avg_tokens:.0f} tokens/篇, "
                f"超长 (引擎 chunk+pool) {n_long}/{len(raw_texts)} 篇")

    # ---- 4.4 权威政策文本分段 (Chunk-then-Pool, 按文档分组) ----
    # 【术语】Early Chunking + Mean Pooling (Günther et al., 2024; Reimers &
    #   Gurevych, 2019): 将超长锚点文本按 token 上限切分为 K 个不重叠段，
    #   各段独立嵌入后均值池化为单个锚点向量，保留全部语义信息。
    # fix(omni-g-policy-02, 2026-06-11): 分段改为**逐文档**进行 (doc_chunks 按
    #   文档分组), 段不跨文档边界 → 下游可按各文档 vintage 年份过滤分段,
    #   构造年度 t 的 ≤t 锚点。
    # 【白话】政策文件可能远超模型单条输入上限 (8,191 tokens)，所以按实际 token
    #   数切成多段分别处理，最后取平均，全部政策文件的内容都不会被丢弃。
    doc_chunks = [_split_into_chunks(d['text'], _MAX_TOKENS_PER_INPUT)
                  for d in auth_docs]
    doc_years = [d['year'] for d in auth_docs]

    # ---- 4.4a 文章年份解析 (vintage-aware 前视守卫, fix(omni-g-policy-02)) ----
    # 优先读上游已派生的 'year' 列; 否则从 '日期' 列派生 (与 panel/encode 同口径);
    # 两者皆缺 / vintage opt-out → article_years=None → 静态全语料锚点降级 + 披露。
    article_years = None
    if vintage_aware_enabled() and any(y is not None for y in doc_years):
        if 'year' in df.columns:
            article_years = pd.to_numeric(
                df['year'], errors='coerce').to_numpy(dtype=float)
        elif '日期' in df.columns:
            article_years = pd.to_datetime(
                df['日期'], errors='coerce').dt.year.to_numpy(dtype=float)
        else:
            logger.warning(
                "  vintage 前视守卫: 输入缺 'year'/'日期' 列, 无法解析文章年份 "
                "→ 降级为静态全语料锚点 (含未来政策文本, 前视披露)")
    else:
        logger.warning(
            "  vintage 前视守卫: 关闭 (article_alignment.vintage_aware=false "
            "或语料年份全部未知) → 静态全语料锚点 (含未来政策文本, 前视披露)")

    # ---- 4.4b ctx 轨 token 诊断 (无预截断, 同 4.3 选项 B) ----
    # ctx 轨 = 标题 + 实体局部窗口, 构造上几乎不超长; 仍与 full 轨同口径不预截断,
    # 万一超长由引擎 chunk+pool 接管 (两轨对称)。
    ctx_token_counts = [_count_tokens(text) for text in ctx_texts]
    n_long_ctx = sum(1 for n in ctx_token_counts if n > _MAX_TOKENS_PER_INPUT)
    logger.info(f"  ctx 轨 token: 超长 (引擎 chunk+pool) "
                f"{n_long_ctx}/{len(ctx_texts)} 篇")

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
    # 选项 B: 直送**全文** full_texts / ctx_texts (非预截断版), 超长由引擎 chunk+pool。
    sim_scores_full, sim_scores_ctx = _cosine_for_spec(
        full_texts, ctx_texts, doc_chunks, EMBEDDING_CONFIG,
        doc_years=doc_years, article_years=article_years)
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
    # fix(omni-g-policy-05, 2026-06-11): try/except 守卫 raise 路径 — 此前仅拦
    # embed_texts 返回 None; embedding_robustness 配置缺失 ({} → spec_uses_local
    # 为 False → API 分支 get_embeddings_api raise RuntimeError) 或本地模型加载
    # 抛错会沿调用链炸掉整个 stage (canonical 列一并丢失), 与本契约注释矛盾。
    try:
        # 选项 B: 同 MAIN, 直送全文 full_texts / ctx_texts, 超长由引擎 chunk+pool。
        t2v_full, t2v_ctx = _cosine_for_spec(
            full_texts, ctx_texts, doc_chunks, _ROBUSTNESS_SPEC,
            doc_years=doc_years, article_years=article_years)
    except Exception as _t2v_exc:
        logger.warning(f"  ROBUSTNESS (text2vec) 嵌入异常: "
                       f"{type(_t2v_exc).__name__}: {_t2v_exc} → _t2v 轨置 NaN "
                       f"(canonical 不受影响, omni-g-policy-05)")
        t2v_full, t2v_ctx = None, None
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
    # fix(omni-g-policy-02, 2026-06-11): 统计/诊断/断言全部改 NaN-安全 —
    # vintage 前视守卫会产生合法 NaN (文章年份未知 / 早于全部政策文档),
    # 旧 .min()/.max() 在含 NaN 时返回 NaN → 值域断言 `NaN >= x` 恒 False 假崩。
    _n_nan_full = int(np.isnan(sim_scores_full).sum())
    if _n_nan_full:
        logger.info(f"     vintage 前视守卫: {_n_nan_full}/{len(sim_scores_full)} "
                    f"篇 full 轨置 NaN (年份未知或早于全部政策文档)")
    logger.info(f"  ✅ policy_cosine_sim 双轨计算完成:")
    for _nm, _sc in [('full', sim_scores_full), ('ctx ', sim_scores_ctx)]:
        if np.isnan(_sc).all():
            logger.warning(f"     {_nm} 轨全 NaN (无任何可比文章-锚点对)")
            continue
        logger.info(f"     {_nm} 范围: [{np.nanmin(_sc):.4f}, {np.nanmax(_sc):.4f}], "
                    f"均值={np.nanmean(_sc):.4f}, σ={np.nanstd(_sc):.4f}")

    # 双轨独立性诊断 (Plan E 验收门)
    try:
        from scipy.stats import spearmanr
        # 常量输入 (min == max, 零方差) 时 Spearman ρ 无定义, scipy 会发
        # ConstantInputWarning。退化场景 (如双轨完全一致或样本极小) 下该诊断无
        # 意义, 显式跳过避免未预期告警, 并防止 rho=nan 误判为 "⚠ 高度相关"。
        _valid = ~np.isnan(sim_scores_full) & ~np.isnan(sim_scores_ctx)
        _vf, _vc = sim_scores_full[_valid], sim_scores_ctx[_valid]
        if _valid.sum() < 3:
            logger.info("     双轨独立性诊断: 有效样本 <3, 跳过")
        elif _vf.min() == _vf.max() or _vc.min() == _vc.max():
            logger.info("     双轨独立性诊断: 输入为常量 (零方差), "
                        "Spearman ρ 无定义, 跳过")
        else:
            rho, _ = spearmanr(_vf, _vc)
            logger.info(f"     双轨独立性诊断: Spearman ρ = {rho:.4f} "
                        f"({'真双轨' if abs(rho) < 0.95 else '⚠ 高度相关'})")
    except ImportError:
        pass

    # 值域断言 (双轨同时检, NaN-安全: 仅检有效值)
    for name, scores in [('full', sim_scores_full), ('ctx', sim_scores_ctx)]:
        if np.isnan(scores).all():
            continue
        assert np.nanmin(scores) >= -1.0 - 1e-6, \
            f"policy_cosine_sim_{name} 下界异常: {np.nanmin(scores)}"
        assert np.nanmax(scores) <= 1.0 + 1e-6, \
            f"policy_cosine_sim_{name} 上界异常: {np.nanmax(scores)}"

    return df


# ============================================================================
# 5. 入口函数
# ============================================================================

def main():
    """Stage 15 主入口。

    数据流: 14_fintech_intensity.parquet → 15_article_alignment.parquet
    新增列: policy_cosine_sim 族共 5 列 (float32, 值域 [-1, 1];
    含 _full/_ctx 双轨 + _t2v_* 双模型稳健 twin)
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
