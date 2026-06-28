"""
16_article_policy_alignment.py — 文章级政策语义对齐度计算模块
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
  15_fintech_intensity.parquet (含 标题、内容、fintech_intensity_score 等)
  config/authoritative_corpus.txt (权威政策文本)

输出:
  16_article_alignment.parquet (= 原数据 + 新增 7 列: policy_cosine_sim
  (legacy alias = _full) + policy_cosine_sim_{full,ctx,ss} 三轨 (MAIN, 无后缀)
  + policy_cosine_sim_lg_{full,ctx,ss} 双 co-primary 孪生 (large))
  注: ss 轨 = content_ss (标题 + 银行∧金科同句共现窗), 上游 stage 13 物化;
      回退 (无共现) → 全文 body (镜像 ctx 回退公理, ss_is_fallback=True)。
  全年份锚点稳健孪生 (2026-06-21, article_alignment.all_vintage_companion=true 默认):
  并列再新增 `_allv` (all-vintage) 一族 policy_cosine_sim_allv[_full/_ctx/_ss] +
  alias + policy_cosine_sim_lg_allv_*——年度 t 文章与**所有年份**政策文档拼成的
  静态全语料锚点算余弦 (口径 = vintage 关闭时的旧静态锚点), 用**完全一致的下游构造**
  作 anchor-robustness 对照。⚠ `_allv` 含未来政策文本, 仅稳健性对照, 绝不替换 vintage
  主轨, 两轨禁混进同一 over-identified 检验 (见 all_vintage_companion_enabled docstring)。
============================================================================

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 16_article_policy_alignment.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**在 DAG 中的位置**: STAGES_MAIN 阶段15, kind=filter, timeout=7200(因含 Embedding API)。上游 = stage 14(直接读 15_fintech_intensity.parquet), 下游被 stage 45 panel runner 的四象限分类(Token/Hidden/Substantive/Irrelevant)消费。

**输入**:
- `15_fintech_intensity.parquet`(含 标题/内容/content_full/content_ctx/content_ss/year/日期 等)。
- `config/authoritative_corpus.txt`(权威政策语料, 经 CONFIG['paths']['authoritative_corpus_file'] 读取, 与 stage 26 共享同一份)。

**核心度量**: `policy_cosine_sim_i = cos(emb(article_i), emb(auth_anchor))`, 理论值域 [-1,1], 实务多落 0~1。

**处理步骤**:
1. **语料加载** `load_policy_corpus_docs`: 按 `# [VINTAGE YYYY]` 标注行 / 落款日期行(YYYY年M月)/ 文号〔YYYY〕N号 解析各政策文档发布年份(vintage); 经 `_strip_leader_names` 镜像新闻侧 normalize 步骤2.5 做敏感词('习近平'简→繁'習近平')对称归一化; 无 VINTAGE 标注时按 ≥3 连续空行切文档。
2. **Vintage-aware 前视守卫**(默认开, config: article_alignment.vintage_aware, 函数 vintage_aware_enabled): 年度 t 的文章只与 **发布年份 ≤ t** 的政策文档段拼成锚点算余弦(消除'2017年新闻比2022年才发布的政策'前视构造)。文章年份从 year 列或 日期 列派生; 年份未知或早于全部政策文档 → 该篇置 NaN。无年份信息或 opt-out 时降级为静态全语料锚点并 WARNING 披露。
3. **嵌入与池化** `_cosine_for_spec`: 政策语料按文档朴素分段 (naive chunking)(_split_into_chunks, token 上限切不重叠段)→ 各段独立嵌入 → 对该年度允许的段做 mean pooling + L2 归一化 = 年度锚点; 文章侧无预截断(2026-06-12 选项 B 移除 8191-token 预截断), 超长文章由引擎 chunk+pool。文章与锚点算 cosine_similarity。每个 spec 用自己的模型独立嵌(MAIN Qwen 4096维 vs large 3072维, 维度不同, 余弦维度无关绝不混算)。
4. **双 co-primary (v3.14.0, 全平价)**: MAIN = Qwen-embedding(config embedding_api, API, 4096 维)→ canonical `policy_cosine_sim_{full,ctx,ss}` + 无后缀别名; LARGE = text-embedding-3-large(API 3072 维, config embedding_large)→ `policy_cosine_sim_lg_{full,ctx,ss}`。both-or-neither parity: MAIN 或 _lg 任一族嵌入失败 → 两族同时置 NaN(无单边孤儿列)。
5. 统计/断言全部 NaN-安全(nanmin/nanmax/nanmean); full↔ctx Spearman ρ 轨间独立性诊断。

**外部依赖/缓存**: 生产嵌入统一走 `pipeline/text/embedding_engine.embed_texts`(LLMCache 穿透 + 动态分批 + chunk-pool); 缓存键含逐字文本(故三轨 content_full/ctx/ss 文本不同字节天然隔离缓存项), 缓存库 = _llm_cache.db。content_full 与 stage 27(benefit_society)逐篇嵌入同源, 同篇文章 API 向量只付费一次。模块内 `_get_embeddings_api_dynamic` 是 legacy(仅 tests/test_pipeline_robustness.py 与 tests/test_omni_fix_policy.py 引用, 生产0调用)。**API 离线守卫**: 嵌入 miss 即付费调 API(不受 NEWS_PROCESS_LLM_OFFLINE 的 stage 21 守卫保护; 裸环境须设 SSL_CERT_FILE=certifi 修 api.siliconflow.cn / yunwu.ai 证书)。timeout=7200。

■ 白话说明

这一步给每篇金科新闻打一个'政策对齐分'——衡量这篇新闻跟国家金融科技政策'像不像'。

打个比方: 先把国家发布的一摞重磅金科政策文件读进来, 浓缩成一份'标准答案'; 再把每篇新闻也变成一串数字(向量), 算它跟'标准答案'的夹角余弦——越接近1说明这篇新闻越贴政策方向, 越低说明越不沾边。这里有个很讲究的细节: 算2017年的新闻时, 只拿'2017年(含)之前已经发布'的政策当标准答案, 绝不拿几年后才出台的政策来比——否则就成了'用未来的信息预测过去', 是学术大忌(叫前视偏误)。

它还同时用两套不同的'翻译机'(都是联网大模型 API: 一套阿里 Qwen, 一套 OpenAI large)各算一遍, 互为稳健性对照: 如果两套都给出类似结论, 结果就更可信。

为什么需要它: 后面要把每篇新闻分到四个格子里——'关键词刷得多但其实不贴政策'(洗科技/喊口号)、'关键词不多但很贴政策'(闷声干事)、'又多又贴'(言行一致)、'又少又不贴'(无关)。要分格子, 就必须先有这个'贴不贴政策'的对齐分(配合 stage 14 的'关键词强度')。

对最终面板/论文的影响: 这是把'象征性 vs 实质性采纳'这个核心构念落地的关键一步。若政策语料选错、前视守卫没做、或嵌入算偏, 银行被错分进'洗科技'还是'真干事'就会反转, 直接动摇 P1/P3 等论文关于'媒体语调/政策实质'的主结论。它的输出还会经年度内分位阈值定四象限, 所以哪怕单篇分数小变动, 也可能让整年阈值移动、连带多篇文章翻类, 需要谨慎重生面板。
========================================================================
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
from news_process.core.logging import pct4, sig4  # 4 有效数字渲染 (日志专用)

# ============================================================================
# 1. 全局配置和初始化  (Phase 2a: 取代旧的 importlib 反射)
# ============================================================================
from news_process.pipeline.panel.encode import CONFIG, logger  # noqa: E402
from news_process.pipeline.text import embedding_engine as _eng

# LLM API 配置（复用 tone_llm_processing 节中的 base_url 和 api_key）
LLM_CONFIG = CONFIG.get('tone_llm_processing', {})
# MAIN spec = 无后缀主嵌入模型 (config embedding_api, Qwen/Qwen3-Embedding-8B) → canonical
# policy_cosine_sim* 列。
EMBEDDING_CONFIG = CONFIG.get('embedding_api', {})
# LARGE spec = co-primary 嵌入模型 (text-embedding-3-large, 3072 维) → _lg 后缀孪生列,
# 与 MAIN(无后缀) 全平价并列 (v3.14.0 起为 ACTIVE co-primary, 非休眠)。
_LARGE_SPEC = CONFIG.get('embedding_large', {})
# 2026-06-26 全项目统一: 嵌入 API 每次重试固定间隔 10s (flat, 不再指数退避)
RETRY_DELAY = 10
CACHE_DB_PATH = CONFIG['paths'].get('llm_cache_db', os.path.join(CONFIG['paths']['output_dir'], '_llm_cache.db'))

# 模块专属配置
_ALIGN_CFG = CONFIG.get('policy_alignment', {})

# Stage 名称
STAGE_NAME = "16_article_policy_alignment"

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


# 【术语】嵌入切块的保守 token 约束 (cl100k_base; 历史源自 text-embedding-3-small, 现作 Qwen/large 嵌入的保守代理):
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


def _count_tokens_batch(texts) -> list[int]:
    """批量精确 token 计数 (cl100k encode_batch, tiktoken 内部多线程)。

    逐位等价于 ``[_count_tokens(t) for t in texts]`` (同 cl100k 编码器 + 同
    disallowed_special 默认), 仅把纯诊断日志用的全量 token 统计从逐条 Python
    encode 改走批接口提速 (2026-06-23 零风险小优化, 计数与输出均不变)。
    """
    from news_process.core.text.token_utils import get_encoding
    enc = get_encoding()
    return [len(t) for t in enc.encode_batch([str(x) for x in texts])]


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
# 【术语】Vintage-aware Anchor: 静态权威语料把 2001-2025 间发布的 10 份政策文件
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

# fix(omni-g-policy-01, 2026-06-11; 2026-06-22 改: 删除→简繁转换): 与新闻侧预处理对称的
# 敏感词归一化。preprocess/normalize.py::_clean_single_text 步骤 2.5 对全部新闻标题/内容
# 把 '习近平' 简体→繁体 '習近平' (体现而非删除); 权威语料若裸读不经该规则 → 相似度两端
# 文本预处理不对称 (语料 6 处)。此处镜像同一规则使两端口径一致 (对称归一化级,
# 裁决: 锚为全行共享常量, 实测效应 ≤3.2e-3, P3 披露级)。
_LEADER_NAME_TOKENS = ('习近平',)
_LEADER_NAME_TRAD = '習近平'  # 简体 → 繁体, 与 normalize.py 步骤 2.5 同口径


def _strip_leader_names(text: str) -> str:
    """对语料文本应用与 normalize.py 步骤 2.5 相同的敏感词归一化 (简体→繁体, 对称口径)。

    2026-06-22: 由"删除 '习近平'"改为"简体→繁体 '習近平'" (体现而非删除), 与新闻侧
    normalize 步骤 2.5 保持同一规则。函数名沿用历史前缀 (_strip_), 行为现为归一化而非删除。
    """
    for tok in _LEADER_NAME_TOKENS:
        text = text.replace(tok, _LEADER_NAME_TRAD)
    return text


def load_policy_corpus_docs(auth_path: str) -> list[dict]:
    """加载权威政策语料并按文档切分, 解析各文档 vintage 年份。

    fix(omni-g-policy-01/02, 2026-06-11) 语义披露:
      - 文本经 _strip_leader_names 对称归一化 (与新闻侧 normalize 步骤 2.5 同规则: '习近平'简→繁);
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


def all_vintage_companion_enabled() -> bool:
    """全年份锚点稳健性孪生 (_allv = all-vintage) 开关 (默认 True; 用户 2026-06-21 决策)。

    【动机】vintage-aware 主轨用"年度 t 仅 ≤t 政策段"消除前视构造 (look-ahead),
    是 identification 的正确口径。但审稿人常追问: 结论是否被 vintage 裁剪本身驱动?
    本开关让 stage 15 (本模块) 与 stage 26 (policy_similarity) 在保留 vintage 主轨
    不动的前提下, **并列**产出一套"年度 t 文章与**所有年份**政策文档拼成锚点"的孪生
    指标 (后缀 `_allv`), 用**完全一致的下游构造方法** (同嵌入/同池化/同余弦/同四象限)
    作为稳健性对照。`_allv` 锚点 = 既有静态全语料锚点 (vintage 关闭时的旧行为),
    此处提升为并列稳健列而非仅作降级回退。

    【口径铁律】`_allv` 含未来政策文本, **仅作稳健性对照, 绝不替换 vintage 主轨**;
    论文须明确披露 `_allv` 系 ex-post / 全语料口径 (Hassan et al. 2019 锚点注入范式
    下的 anchor-robustness, 非前视守卫指标)。两轨绝不混进同一 over-identified 检验。

    config 键: article_alignment.all_vintage_companion (与 vintage_aware 同节)。
    """
    return bool((CONFIG.get('article_alignment') or {}).get(
        'all_vintage_companion', True))


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
#   朴素分段 (naive chunking) + Mean Pooling)。Stage 25/26/27 也走同一引擎 (不存在旧注释
#   所称 "Stage 25 固定每批 100 条" — 该描述已随引擎统一而过时)。
#   本函数仅余 tests/test_pipeline_robustness.py (缓存穿透/重试) 与
#   tests/test_omni_fix_policy.py (legacy 标注断言) 引用,
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
    0 调用, 仅 tests/test_pipeline_robustness.py (缓存穿透/重试) 与
    tests/test_omni_fix_policy.py (legacy 标注) 单测引用。
    保留以维持测试契约; 勿在生产代码中新增调用。

    【术语】
    引入 LLMCache 穿透查询，未命中则走 API。
    针对 API 使用"无限固定间隔重试 (Infinite Flat-Interval Retry, 每次 10s)"，
    只要是网络故障 (429, 500+) 绝不退出，直到取回完美向量为止。
    若是致命错误 (400, 401, 404)，则抛出 ValueError 拦截并中止进程。

    【白话】先把文章在缓存库里查一遍。没查到的打包发给大模型。
    如果网断了或者被限流，就每隔 10 秒再试一次、一直试，绝不报错退出（除非密码错了），
    确保拿回来的全是完好无损的数据。

    Args:
        texts: 已截断至 8191 tokens 的文本列表
        token_counts: 每篇文本对应的 token 数
        cache: LLMCache 实例

    Returns:
        np.ndarray: Embedding 矩阵 (N × d)，d = 嵌入模型维度 (API 驱动; Qwen=4096 / large=3072)
    """
    import aiohttp
    models = LLM_CONFIG.get('models') or []
    cfg = models[0] if models else {}
    if EMBEDDING_CONFIG:
        base_url = EMBEDDING_CONFIG.get('base_url')
        api_key = EMBEDDING_CONFIG.get('api_key')
        embedding_model = (EMBEDDING_CONFIG.get('model') or "Qwen/Qwen3-Embedding-8B")
    else:
        base_url = cfg.get('base_url')
        api_key = cfg.get('api_key')
        embedding_model = "Qwen/Qwen3-Embedding-8B"
    if not base_url or not api_key:
        raise RuntimeError("Embedding API config missing base_url or api_key")
    base_url = str(base_url).rstrip("/")
    # Plan-r3 P3-17 接入: embedding 缓存键的 prompt_version 维度,
    # 防止改 embedding model / 文本预处理后旧 cache silent 命中.
    # Round 4 M8 修: 用参数 prompt_version_override 替代全局 mutation, 避免污染其他 callsite。
    # (2026-06-11 注释纠偏, fix(omni-g-policy-04)): 旧注释所述 "ctx 轨调用方传
    # base+'-ctx' 显式隔离 namespace" 在现行调用链中已不存在 — 生产三轨 (full/ctx/ss)
    # 均经 embedding_engine 以同一 text_pipeline_version 入缓存 (键含逐字文本, 天然隔离);
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
                            else:
                                err_text = await resp.text()
                                raise ValueError(f"不可恢复的 API 错误 {status} (batch {batch_idx+1}): {err_text[:200]}")
                    except ValueError:
                        raise  # 直接向上抛出致命错误
                    except Exception as e:
                        logger.warning(f"    网络异常 (batch {batch_idx+1}): {type(e).__name__}: {e}。休眠 {delay} 秒后重试...")
                        await asyncio.sleep(delay)

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
# 3b. 三轨 (full/ctx/ss) 嵌入 + 余弦相似度公共算子 (v3.14.0: 双 co-primary, 按 spec 调用)
# ============================================================================

def _cosine_for_spec(
    full_texts: list[str],
    ctx_texts: list[str],
    doc_chunks: list[list[str]],
    spec: dict,
    *,
    ss_texts: list[str] | None = None,
    doc_years: list | None = None,
    article_years: np.ndarray | None = None,
    return_static: bool = False,
):
    """用单一 spec 嵌入 (full / ctx / ss / auth) 并返回 (cos_full, cos_ctx, cos_ss)。

    三轨 (full/ctx/ss) — ss = content_ss (标题 + 银行∧金科同句共现窗, 回退镜像 ctx);
    ss_texts=None 时 cos_ss 返回 None (上游缺 content_ss 列时优雅跳过)。

    全年份锚点稳健孪生 (2026-06-21, return_static): 嵌入 (article + auth_chunks)
    只算一次, 既用于 vintage-aware 主锚点, 也用于"全语料(所有年份)静态锚点"。
    return_static=False (默认, 向后兼容) → 返回 3-tuple 主轨 (vintage 可用时=vintage,
    否则=静态); return_static=True → 返回 ((主轨三元组), (静态全年份三元组)) 供调用方
    并列产出 `_allv` 稳健列。静态三元组复用同一批 article embeddings → **零额外 API**。

    【关键约束】每个 spec 用**自己的**模型独立嵌入自己的 anchors/texts,
    绝不复用另一 spec 的向量 (MAIN Qwen 4096 维 vs large 3072 维, 维度不同, 严禁混算)。
    ⚠ 嵌入缓存键含逐字文本 (非轨标签) → content_ss 文本与 full/ctx 不同字节自然
    隔离独立缓存项, 三轨复用同一 spec 无键碰撞。

    fix(omni-g-policy-02, 2026-06-11) 语义变更: 锚点改为 vintage-aware —
    传入 doc_years (各政策文档发布年份) + article_years (各文章年份) 时, 年度 t
    的文章只与发布年份 ≤ t 的政策文档段的池化锚点算余弦 (消除前视构造);
    无 ≤t 文档的年份与年份未知的文章 → NaN。两参数任一为 None → 静态全语料
    锚点 (旧行为, 仅作稳健性/降级路径)。

    流程:
      1. 用 spec 经 _eng.embed_texts 分别嵌入 full_texts / ctx_texts / ss_texts /
         全部文档段 (text-level, 内部已处理 chunk 切分 + mean pooling + local/API 分派)。
      2. 对各年度允许的文档段嵌入做 mean pooling + L2 归一化 → 该年度政策锚点
         向量 (保留 zero-norm 守卫)。
      3. cosine_similarity(full / ctx / ss, anchor_year)。

    Args:
        full_texts: full 轨文本 (不截断; 超长由引擎分段池化)
        ctx_texts:  ctx 轨文本
        doc_chunks: 权威政策语料分段, 按文档分组 (list per 文档)
        spec: embedding spec (MAIN=Qwen API / LARGE=text-embedding-3-large API)
        ss_texts:   ss 轨文本 (银行+金科同句); None → 不算 ss, cos_ss 返回 None
        doc_years: 各文档 vintage 年份 (与 doc_chunks 对齐); None → 静态锚点
        article_years: (N,) 文章年份 float 数组 (NaN=未知); None → 静态锚点

    Returns:
        return_static=False → (cos_full, cos_ctx, cos_ss): 主轨三元组, 前二各为
        (N,) np.ndarray; cos_ss 为 (N,) 或 None (ss_texts=None); 嵌入失败
        (embed_texts 返回 None) 或静态锚点范数为零 → (None, None, None)。
        return_static=True → ((主轨三元组), (静态全年份三元组)): 第二元组为"全语料
        (所有年份)静态锚点"对应的 (cos_full, cos_ctx, cos_ss), 供调用方产出 `_allv`
        稳健列; 嵌入失败时两元组均为 (None, None, None)。vintage 不可用时主轨 ≡ 静态,
        故两元组数值相同 (诚实的退化, 调用方据此知 _allv≡主轨)。
    """
    from sklearn.metrics.pairwise import cosine_similarity

    def _wrap(primary, static):
        """按 return_static 决定返回 3-tuple 主轨 或 (主轨, 静态) 2-元组。"""
        return (primary, static) if return_static else primary

    model_id = _eng.spec_model(spec)
    log_prefix = f"Embedding[{model_id}]"

    auth_chunks = [c for chunks in doc_chunks for c in chunks]
    # 每个分段所属文档下标 (用于 vintage 过滤)
    chunk_doc_idx = np.array(
        [i for i, chunks in enumerate(doc_chunks) for _ in chunks], dtype=int)

    # 单连接复用 (2026-06-23 零风险小优化): 本函数 ≤4 次 embed_texts 调用此前各开一个
    # LLMCache (≤4 次 sqlite connect/WAL/建表); 改为本函数开一个共享连接传入, 省去重复
    # 打开 (产出逐位不变)。两 co-primary (MAIN/large) 均经 API embed 走 LLMCache 穿透,
    # 命中即 $0 跨 run/跨 stage 复现。
    has_ss = ss_texts is not None
    shared_cache = LLMCache(CACHE_DB_PATH)
    try:
        article_embs_full = _eng.embed_texts(
            full_texts, spec, cache=shared_cache, cache_db_path=CACHE_DB_PATH,
            log_prefix=log_prefix)
        article_embs_ctx = _eng.embed_texts(
            ctx_texts, spec, cache=shared_cache, cache_db_path=CACHE_DB_PATH,
            log_prefix=log_prefix)
        auth_chunk_embs = _eng.embed_texts(
            auth_chunks, spec, cache=shared_cache, cache_db_path=CACHE_DB_PATH,
            log_prefix=log_prefix)
        # ss 轨: 镜像 full/ctx 嵌入路径; ss_texts=None 时不算 (优雅跳过 → cos_ss=None)
        article_embs_ss = (
            _eng.embed_texts(
                ss_texts, spec, cache=shared_cache, cache_db_path=CACHE_DB_PATH,
                log_prefix=log_prefix)
            if has_ss else None
        )
    finally:
        if shared_cache is not None:
            shared_cache.close()

    if (article_embs_full is None or article_embs_ctx is None
            or auth_chunk_embs is None or (has_ss and article_embs_ss is None)):
        logger.warning(f"  {log_prefix}: 嵌入返回 None, 该 spec 轨置 NaN")
        return _wrap((None, None, None), (None, None, None))

    def _pooled_anchor(chunk_mask: np.ndarray) -> np.ndarray | None:
        """选中分段 → mean pooling + L2 归一化 → (1, D) 锚点; 范数零 → None。"""
        sub = auth_chunk_embs[chunk_mask]
        anchor = sub.mean(axis=0, keepdims=True)
        norm = np.linalg.norm(anchor, axis=1, keepdims=True)
        if norm.item() <= 0:
            return None
        return anchor / norm

    def _static_triple():
        """全语料(所有年份)静态锚点对 full/ctx/ss 的余弦三元组 (复用已嵌入向量)。

        = 既有"静态全语料锚点"口径 (vintage 关闭时的旧行为), 此处供 `_allv` 全年份
        稳健孪生复用; 锚点范数为零 → (None, None, None)。**零额外 API** (embeddings
        已在上方算好)。
        """
        anchor = _pooled_anchor(np.ones(len(auth_chunks), dtype=bool))
        if anchor is None:
            logger.error(f"  ⚠️ {log_prefix}: 政策锚点(全年份静态)均值池化后范数为零!")
            return None, None, None
        cf = cosine_similarity(article_embs_full, anchor)[:, 0]
        cc = cosine_similarity(article_embs_ctx, anchor)[:, 0]
        cs = (cosine_similarity(article_embs_ss, anchor)[:, 0]
              if has_ss else None)
        return cf, cc, cs

    vintage_mode = (
        doc_years is not None and article_years is not None
        and any(y is not None for y in doc_years)
    )

    # 全年份静态三元组: return_static 或非 vintage 模式 (主轨即静态) 时才算, 否则 None
    static_triple = (_static_triple()
                     if (return_static or not vintage_mode)
                     else (None, None, None))

    if not vintage_mode:
        # 静态全语料锚点 (旧行为; 仅稳健性 opt-out / 无年份信息降级, 调用方已披露)
        # 主轨 ≡ 静态三元组; 静态侧若范数为零亦随之 (None,None,None)。
        if static_triple[0] is None:
            return _wrap((None, None, None), (None, None, None))
        logger.info(f"  {log_prefix} 政策锚点(静态): {len(auth_chunk_embs)} 段 → "
                    f"Mean Pooling → 1 个向量 (主轨 ≡ 全年份 _allv)")
        return _wrap(static_triple, static_triple)

    # --- vintage-aware: 逐年度构造 ≤t 锚点 ---
    doc_years_arr = np.array(
        [np.nan if y is None else float(y) for y in doc_years], dtype=float)
    n = len(full_texts)
    cos_full = np.full(n, np.nan, dtype=np.float64)
    cos_ctx = np.full(n, np.nan, dtype=np.float64)
    # ss 轨镜像 cos_ctx 的 NaN-预填; 无 ss → None (返回时优雅跳过)
    cos_ss = np.full(n, np.nan, dtype=np.float64) if has_ss else None

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
        # ss 轨镜像: 同一 ≤t 锚点对 ss 文本算余弦
        if has_ss:
            cos_ss[art_mask] = cosine_similarity(
                article_embs_ss[art_mask], anchor)[:, 0]
        logger.info(f"  {log_prefix} 政策锚点(vintage≤{int(year)}): "
                    f"{int(allowed_docs.sum())}/{len(doc_chunks)} 文档 "
                    f"{int(chunk_mask.sum())} 段 → {int(art_mask.sum())} 篇")
    return _wrap((cos_full, cos_ctx, cos_ss), static_triple)


# ============================================================================
# 4. 主流程函数
# ============================================================================

def compute_article_policy_alignment(df: pd.DataFrame) -> pd.DataFrame:
    """计算文章级政策语义对齐度 (Article-level Policy Cosine Similarity)。

    【学术支撑】
    本函数实现的核心度量：

        policy_cosine_sim_i = cos(emb(article_i), emb(auth_text))

    其中:
      - emb() 为稠密语义编码: MAIN spec = Qwen-embedding (API, 4096 维, 无后缀 canonical); LARGE spec = text-embedding-3-large (API, 3072 维, _lg co-primary); 两 spec 各自独立编码, 全平价并列, 严禁混算。
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
        df: DataFrame (来自 15_fintech_intensity.parquet)。full 轨优先读 stage 13
            物化的 'content_full' 列; 缺列时回退用 '标题' + '内容' 经 prepend_title 构建。
            ctx 轨读 'content_ctx' 列; ss 轨读 'content_ss' 列 (银行+金科同句共现窗,
            stage 13 物化; 缺列时优雅跳过, 不产出 _ss 列)。

    Returns:
        DataFrame: 新增 'policy_cosine_sim' (legacy alias) + _full/_ctx/_ss 三轨 (MAIN)
        + _lg_full/_lg_ctx/_lg_ss 双 co-primary 孪生 (large), 共 7 列 (content_ss 缺失时
        退回 5 列; 见模块 docstring 输出段)。MAIN 与 _lg both-or-neither: 任一族嵌入失败
        两族同时置 NaN。
        全年份锚点稳健孪生 (2026-06-21, article_alignment.all_vintage_companion=true 默认):
        再并列新增 `_allv` 一族 (policy_cosine_sim_allv[_full/_ctx/_ss] + alias +
        _lg_allv_*), 用全语料(所有年份)静态锚点 + 完全一致下游构造, 作 anchor-robustness
        对照 (绝不替换 vintage 主轨, 详见 all_vintage_companion_enabled docstring)。
    """
    # 旧短 banner ("=" * 60 + "开始计算...") 已删: 与 main() 新【功能】黄金范式 banner
    # 重复 (替换而非叠加, 对齐 39c construct_orthogonality.py); 此处仅留计算起点标记。
    logger.info("开始计算: 文章级政策语义对齐度 (Stage 15)")

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
    # 三轨 (full/ctx/ss) ss 轨可用性: 上游 stage 13 物化 content_ss 时才产 _ss 列,
    # 缺列优雅跳过 (镜像 ctx 守卫) — 早退/失败路径据此决定是否把 _ss 列也置 NaN。
    has_ss = 'content_ss' in df.columns
    # 全年份锚点稳健孪生开关 (2026-06-21): true → 并列产出 `_allv` 一族 (全语料静态锚点)。
    _companion = all_vintage_companion_enabled()

    # 双 co-primary (MAIN 无后缀 + _lg) full/ctx → 三轨 (full/ctx/ss) 列契约: 早退路径也须
    # 产出全部列 (全 NaN), 否则下游 runner 聚合缺列 → export.py REQUIRED_PANEL_COLUMNS 抛
    # RuntimeError。content_ss 缺失时 _ss 不进契约 (退回 5 列), 与 ctx 守卫一致。
    # 🔴 both-or-neither parity (D-4a): MAIN(无后缀) 与 _lg 列同进同出 — 早退路径两族同时
    #   置 NaN, 计算成功路径若任一 embed 返回 None 则两族同时置 NaN (见下方 _main_res 守卫)。
    _ALIGN_NAN_COLS = [
        'policy_cosine_sim', 'policy_cosine_sim_full', 'policy_cosine_sim_ctx',
        'policy_cosine_sim_lg_full', 'policy_cosine_sim_lg_ctx',
    ]
    if has_ss:
        _ALIGN_NAN_COLS += ['policy_cosine_sim_ss', 'policy_cosine_sim_lg_ss']
    # `_allv` 全年份锚点孪生 (companion 开启时): 早退路径同样须产全 NaN 占位列, 与主轨
    # 列契约对称 (下游 runner 按存在性优雅聚合; _allv 非 REQUIRED_PANEL_COLUMNS 硬契约)。
    if _companion:
        _ALIGN_NAN_COLS += [
            'policy_cosine_sim_allv', 'policy_cosine_sim_allv_full',
            'policy_cosine_sim_allv_ctx',
            'policy_cosine_sim_lg_allv_full', 'policy_cosine_sim_lg_allv_ctx',
        ]
        if has_ss:
            _ALIGN_NAN_COLS += ['policy_cosine_sim_allv_ss',
                                'policy_cosine_sim_lg_allv_ss']

    if not os.path.exists(auth_path):
        logger.warning(f"  找不到权威政策语料: {auth_path}。"
                       f"跳过 Stage 15 计算。")
        for _c in _ALIGN_NAN_COLS:
            df[_c] = np.nan
        return df

    # fix(omni-g-policy-01/02, 2026-06-11): 经 load_policy_corpus_docs 统一加载 —
    # (01) 语料文本经与新闻侧 normalize 步骤 2.5 相同的敏感词对称归一化 ('习近平'简→繁);
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

    # ---- 4.2 构建文章输入文本 (v3.6.0 Plan E P3 B2: full/ctx → 三轨 (full/ctx/ss) 2026-06-14) ----
    # 【术语】full 轨 = 标题 + 全文; ctx 轨 = content_ctx (= 标题 + 目标银行局部窗口);
    #   ss 轨 = content_ss (= 标题 + 目标银行∧金科同句共现窗口, 上游 stage 13
    #   ctx_materializer 物化; 无共现回退全文 body, 镜像 ctx 回退公理 ss_is_fallback=True)。
    #   三轨均含同一标题前缀 (remove-title-track 终态: 标题 prepend 进 full/ctx/ss)。
    # 【白话】三条轨道分别打分:
    #   - full: 整篇新闻 vs 政策 (措施层 — Hassan 2019 macro 类比)
    #   - ctx:  目标银行那段 vs 政策 (实体特异性窗口 — Hassan et al. 2019 QJE §III.B
    #           proximity-based attribution; Tetlock 2007 / L&M 2016 为媒体文本分析谱系)
    #   - ss:   目标银行∧金科同句那段 vs 政策 (共现特异性, 主题漂移更小的独立信号)
    # P0 修复 (embedding-reuse-audit 2026-06-05, 病根A 残留): full 轨改读 stage 13
    # 物化的 content_full (= prepend_title(标题, 内容)), 替代旧的裸 '标题 + 空格 + 内容'。
    # 两个动机:
    #   (1) embedding 缓存复用: content_full 是逐字节固定的文章级串, 与 **stage 27
    #       (benefit_society) 逐篇嵌入的 content_full 同源** → 同篇文章的
    #       嵌入向量经 LLMCache (键含逐字文本) 只付费一次; 旧空格
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
        logger.info(f"  full/ctx 输入: full={len(full_texts)} | ctx={len(ctx_texts)} "
                    f"(ss 轨另行记录)")
    else:
        logger.warning(
            "  content_ctx 列缺失 (stage 13 未跑?), ctx 轨回退至 full — "
            "此时 policy_cosine_sim_ctx ≡ _full, 不构成真正独立的 ctx 轨")
        ctx_texts = full_texts

    # ss 轨输入 (银行+金科同句): content_ss 由 stage 13 物化 (无共现已回退全文 body,
    # 镜像 ctx); 缺列 (has_ss=False) → ss_texts=None → 下游 _cosine_for_spec 优雅跳过,
    # 不产出 _ss 列 (镜像 ctx 缺列守卫的"不构成真三轨"逻辑, 但此处选择不产 _ss 列以
    # 避免 _ss≡_full 的伪列污染面板)。
    if has_ss:
        ss_texts = df['content_ss'].fillna('').astype(str).tolist()
        logger.info(f"  三轨输入: full={len(full_texts)} | ctx={len(ctx_texts)} "
                    f"| ss={len(ss_texts)}")
    else:
        logger.warning(
            "  content_ss 列缺失 (stage 13 未物化同句共现轨?), 跳过 ss 轨 — "
            "不产出 policy_cosine_sim_ss / _lg_ss 列 (镜像 ctx 缺列优雅跳过)")
        ss_texts = None

    # 处理 full 轨 raw_texts (与下游保持兼容名)
    raw_texts = full_texts
    logger.info(f"  文章总数: {len(raw_texts)}")

    # ---- 4.3 Token 诊断 (无预截断 — 超长由引擎 chunk+pool 接管) ----
    # 【术语】fix(2026-06-12, 选项 B; 镜像 stage 27 omni-g-benefit-04): 移除文章侧
    #   8191-token 预截断。统一引擎 _eng.embed_texts 自带朴素分段 (naive chunking) + token
    #   加权 Mean Pooling (Reimers &
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
    token_counts = _count_tokens_batch(raw_texts)
    n_long = sum(1 for n in token_counts if n > _MAX_TOKENS_PER_INPUT)
    avg_tokens = np.mean(token_counts) if token_counts else 0
    logger.info(f"  Token 统计: 平均 {sig4(avg_tokens)} tokens/篇, "
                f"超长 (引擎 chunk+pool) {n_long:,d}/{len(raw_texts):,d} 篇")

    # ---- 4.4 权威政策文本分段 (Chunk-then-Pool, 按文档分组) ----
    # 【术语】朴素分段 (naive / independent chunking) + Mean Pooling (Reimers &
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

    # ---- 4.4b ctx / ss 轨 token 诊断 (无预截断, 同 4.3 选项 B) ----
    # ctx 轨 = 标题 + 实体局部窗口, ss 轨 = 标题 + 同句共现窗口, 构造上几乎不超长;
    # 仍与 full 轨同口径不预截断, 万一超长由引擎 chunk+pool 接管 (三轨对称)。
    ctx_token_counts = _count_tokens_batch(ctx_texts)
    n_long_ctx = sum(1 for n in ctx_token_counts if n > _MAX_TOKENS_PER_INPUT)
    logger.info(f"  ctx 轨 token: 超长 (引擎 chunk+pool) "
                f"{n_long_ctx}/{len(ctx_texts)} 篇")
    if ss_texts is not None:
        ss_token_counts = _count_tokens_batch(ss_texts)
        n_long_ss = sum(1 for n in ss_token_counts if n > _MAX_TOKENS_PER_INPUT)
        logger.info(f"  ss 轨 token: 超长 (引擎 chunk+pool) "
                    f"{n_long_ss}/{len(ss_texts)} 篇")

    # ---- 4.5 双 co-primary 嵌入 + 余弦相似度 (MAIN 无后缀 + _lg 全平价) ----
    # 【术语】Hoberg & Phillips (2016, JPE, §III) 余弦相似度;
    #   v3.6.0 Plan E P3 B2 full/ctx → 2026-06-14 加 ss 同句共现轨成 full/ctx/ss
    #   三轨; v3.14.0 双 co-primary:
    #   MAIN = Qwen-embedding (API, 4096 维) → canonical 无后缀列,
    #   LARGE = text-embedding-3-large (API, 3072 维) → _lg 列 (ACTIVE co-primary)。
    # 【关键】两个模型各嵌各的 anchors/texts, 绝不混算 (维度不同 + 语义空间不同)。
    #   embedding 取得统一经 _eng (本地 vs API 由 spec 内部分派, 不再 inline if)。
    # 🔴 both-or-neither parity (D-4a): MAIN 与 _lg 是双射孪生 — 任一族 embed 返回 None
    #   则两族同时置 NaN, 绝不留单边孤儿列。故先各自算结果, 再统一判 None 联动降级。
    # 【白话】同一批新闻用两个 API 模型各算一遍政策对齐分, 两套结果全平价并列;
    #   主轨无后缀, large 那遍列名加 _lg 后缀; 任一套算不出来则两套一起置空。
    df = df.copy()

    # --- 先算 MAIN 与 _lg 两 co-primary 结果 (尚未落列), 供下方 both-or-neither 联动判定 ---
    # 选项 B: 直送**全文** full_texts / ctx_texts / ss_texts (非预截断版), 超长由引擎
    # chunk+pool。ss_texts=None (content_ss 缺失) 时 *_ss 返回 None, 跳过 _ss 列。
    # return_static=_companion: companion 开启时同步取"全年份(静态全语料)锚点"孪生
    # (av_* = all-vintage; 复用同一批 article embeddings → 零额外 API)。
    _main_res = _cosine_for_spec(
        full_texts, ctx_texts, doc_chunks, EMBEDDING_CONFIG,
        ss_texts=ss_texts, doc_years=doc_years, article_years=article_years,
        return_static=_companion)
    if _companion:
        (sim_scores_full, sim_scores_ctx, sim_scores_ss), \
            (av_full, av_ctx, av_ss) = _main_res
    else:
        sim_scores_full, sim_scores_ctx, sim_scores_ss = _main_res
        av_full = av_ctx = av_ss = None

    # --- LARGE (_lg) co-primary 轨: 与 MAIN 全平价 (ACTIVE, 非休眠) ---
    # 选项 B: 同 MAIN, 直送全文 full_texts / ctx_texts / ss_texts, 超长引擎 chunk+pool。
    # return_static=_companion: 同步取 _lg 轨的全年份(静态)锚点孪生 (lg_av_*)。
    _lg_res = _cosine_for_spec(
        full_texts, ctx_texts, doc_chunks, _LARGE_SPEC,
        ss_texts=ss_texts, doc_years=doc_years, article_years=article_years,
        return_static=_companion)
    if _companion:
        (lg_full, lg_ctx, lg_ss), (lg_av_full, lg_av_ctx, lg_av_ss) = _lg_res
    else:
        lg_full, lg_ctx, lg_ss = _lg_res
        lg_av_full = lg_av_ctx = lg_av_ss = None

    # 🔴 both-or-neither 联动降级: MAIN 或 _lg 任一族 full/ctx 嵌入返回 None → 两族全列
    # 置 NaN (含 _ss/_allv), 绝不留单边孤儿列 (D-4a parity 不变量)。
    _main_failed = sim_scores_full is None or sim_scores_ctx is None
    _lg_failed = lg_full is None or lg_ctx is None
    if _main_failed or _lg_failed:
        logger.error(
            f"  ⚠️ 嵌入失败 (MAIN_failed={_main_failed}, _lg_failed={_lg_failed}): "
            "canonical 与 _lg 两 co-primary 全列联动置 NaN (both-or-neither parity, "
            "保持双射列契约)")
        for _c in _ALIGN_NAN_COLS:
            df[_c] = np.nan
        return df

    df['policy_cosine_sim_full'] = sim_scores_full.astype(np.float32)
    df['policy_cosine_sim_ctx'] = sim_scores_ctx.astype(np.float32)
    # ss 轨 (银行+金科同句): sim_scores_ss=None (content_ss 缺失/ss_texts=None) 时跳过,
    # 不产 _ss 列 (镜像 ctx 缺列守卫)。
    if sim_scores_ss is not None:
        df['policy_cosine_sim_ss'] = sim_scores_ss.astype(np.float32)
    # legacy alias = _full (v3.5.0 schemas.py 契约保留, 9 paper 迁移后可弃)
    df['policy_cosine_sim'] = df['policy_cosine_sim_full']

    # 全年份锚点稳健孪生 (_allv): companion 开启时并列产出全语料(所有年份)静态锚点的
    # 余弦, 列名 = 主轨名插入 `_allv` (在 track 后缀前)。静态锚点退化 (范数零) → NaN 占位
    # 维持列契约对称。vintage 不可用时 av_* ≡ 主轨 (诚实退化, _allv≡主轨)。
    if _companion:
        if av_full is not None and av_ctx is not None:
            df['policy_cosine_sim_allv_full'] = av_full.astype(np.float32)
            df['policy_cosine_sim_allv_ctx'] = av_ctx.astype(np.float32)
            if av_ss is not None:
                df['policy_cosine_sim_allv_ss'] = av_ss.astype(np.float32)
            df['policy_cosine_sim_allv'] = df['policy_cosine_sim_allv_full']
        else:
            logger.warning("  全年份锚点 _allv: 静态全语料锚点退化 (范数零?), "
                           "policy_cosine_sim_allv* 置 NaN (主轨不受影响)")
            df['policy_cosine_sim_allv_full'] = np.nan
            df['policy_cosine_sim_allv_ctx'] = np.nan
            if has_ss:
                df['policy_cosine_sim_allv_ss'] = np.nan
            df['policy_cosine_sim_allv'] = np.nan

    # --- LARGE (_lg) co-primary 轨落列: 与 MAIN 全平价 (ACTIVE) ---
    # lg_* 已在上方与 MAIN 一并算好; both-or-neither 守卫已保证此处 lg_full/lg_ctx 必非
    # None (任一 co-primary full/ctx 失败已联动早退置 NaN)。故主列无条件落盘。
    df['policy_cosine_sim_lg_full'] = lg_full.astype(np.float32)
    df['policy_cosine_sim_lg_ctx'] = lg_ctx.astype(np.float32)
    # ss 轨 _lg (银行+金科同句): lg_ss=None (ss_texts=None) 时跳过, 不产 _ss 列 (镜像 MAIN)
    if lg_ss is not None:
        df['policy_cosine_sim_lg_ss'] = lg_ss.astype(np.float32)

    # 全年份锚点 _lg_allv 孪生 (companion 开启时): 镜像 _lg 主轨, 仅换静态锚点。
    # lg 静态锚点退化 (lg_av_full=None) → 占位 NaN; ss 缺列时不产 _allv_ss (与 MAIN 对齐)。
    if _companion:
        if lg_av_full is not None and lg_av_ctx is not None:
            df['policy_cosine_sim_lg_allv_full'] = lg_av_full.astype(np.float32)
            df['policy_cosine_sim_lg_allv_ctx'] = lg_av_ctx.astype(np.float32)
            if lg_av_ss is not None:
                df['policy_cosine_sim_lg_allv_ss'] = lg_av_ss.astype(np.float32)
        else:
            df['policy_cosine_sim_lg_allv_full'] = np.nan
            df['policy_cosine_sim_lg_allv_ctx'] = np.nan
            if has_ss:
                df['policy_cosine_sim_lg_allv_ss'] = np.nan

    # ---- 4.7 统计报告 ----
    # fix(omni-g-policy-02, 2026-06-11): 统计/诊断/断言全部改 NaN-安全 —
    # vintage 前视守卫会产生合法 NaN (文章年份未知 / 早于全部政策文档),
    # 旧 .min()/.max() 在含 NaN 时返回 NaN → 值域断言 `NaN >= x` 恒 False 假崩。
    _n_nan_full = int(np.isnan(sim_scores_full).sum())
    if _n_nan_full:
        logger.info(f"     vintage 前视守卫: {_n_nan_full}/{len(sim_scores_full)} "
                    f"篇 full 轨置 NaN (年份未知或早于全部政策文档)")
    logger.info(f"  ✅ policy_cosine_sim 三轨计算完成:")
    # 三轨范围统计 (ss 仅当 sim_scores_ss 非 None — content_ss 物化时); 列表追加保留对齐
    _stat_tracks = [('full', sim_scores_full), ('ctx ', sim_scores_ctx)]
    if sim_scores_ss is not None:
        _stat_tracks.append(('ss  ', sim_scores_ss))
    for _nm, _sc in _stat_tracks:
        if np.isnan(_sc).all():
            logger.warning(f"     {_nm} 轨全 NaN (无任何可比文章-锚点对)")
            continue
        logger.info(f"     {_nm} 范围: [{sig4(np.nanmin(_sc))}, {sig4(np.nanmax(_sc))}], "
                    f"均值={sig4(np.nanmean(_sc))}, σ={sig4(np.nanstd(_sc))}")

    # 全年份锚点 _allv 孪生范围统计 (companion 开启且静态锚点有效时); 与主轨对照可见
    # vintage 裁剪对均值的影响幅度 (全年份锚点通常覆盖率更高、早年文章不再 NaN)。
    if _companion and av_full is not None:
        _av_stats = [('allv_f', av_full), ('allv_c', av_ctx)]
        if av_ss is not None:
            _av_stats.append(('allv_s', av_ss))
        for _nm, _sc in _av_stats:
            if _sc is None or np.isnan(_sc).all():
                continue
            logger.info(f"     {_nm} 范围: [{sig4(np.nanmin(_sc))}, {sig4(np.nanmax(_sc))}], "
                        f"均值={sig4(np.nanmean(_sc))}, σ={sig4(np.nanstd(_sc))} (全年份锚点)")

    # 轨间独立性诊断 (Plan E 验收门; full vs ctx pairwise — ss 轨的 full/ctx/ss
    # 三向 pairwise 独立性集中在 stage 24 herd_decay 做, 此处仍仅 full↔ctx 单对)
    try:
        from scipy.stats import spearmanr
        # 常量输入 (min == max, 零方差) 时 Spearman ρ 无定义, scipy 会发
        # ConstantInputWarning。退化场景 (如 full 与 ctx 完全一致或样本极小) 下该诊断无
        # 意义, 显式跳过避免未预期告警, 并防止 rho=nan 误判为 "⚠ 高度相关"。
        _valid = ~np.isnan(sim_scores_full) & ~np.isnan(sim_scores_ctx)
        _vf, _vc = sim_scores_full[_valid], sim_scores_ctx[_valid]
        if _valid.sum() < 3:
            logger.info("     轨间独立性诊断 (full↔ctx): 有效样本 <3, 跳过")
        elif _vf.min() == _vf.max() or _vc.min() == _vc.max():
            logger.info("     轨间独立性诊断 (full↔ctx): 输入为常量 (零方差), "
                        "Spearman ρ 无定义, 跳过")
        else:
            rho, _ = spearmanr(_vf, _vc)
            logger.info(f"     轨间独立性诊断 (full↔ctx): Spearman ρ = {sig4(rho)} "
                        f"({'轨道真独立' if abs(rho) < 0.95 else '⚠ 高度相关'})")
    except ImportError:
        pass

    # 值域断言 (三轨同时检, NaN-安全: 仅检有效值); ss 仅当物化 (sim_scores_ss 非 None)
    # 全年份锚点 _allv 孪生同走值域断言 (companion 开启且静态锚点有效时), 余弦同 ⊆[-1,1]。
    _assert_tracks = [('full', sim_scores_full), ('ctx', sim_scores_ctx)]
    if sim_scores_ss is not None:
        _assert_tracks.append(('ss', sim_scores_ss))
    if _companion and av_full is not None:
        _assert_tracks += [('allv_full', av_full), ('allv_ctx', av_ctx)]
        if av_ss is not None:
            _assert_tracks.append(('allv_ss', av_ss))
    for name, scores in _assert_tracks:
        if scores is None or np.isnan(scores).all():
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

    数据流: 15_fintech_intensity.parquet → 16_article_alignment.parquet
    新增列: policy_cosine_sim 族共 7 列 (float32, 值域 [-1, 1];
    含 _full/_ctx/_ss 三轨 (MAIN) + _lg_* 双 co-primary 孪生; content_ss 缺失时退回 5 列)。
    全年份锚点稳健孪生 (all_vintage_companion=true 默认): 再并列 `_allv` 一族 (同列数,
    全语料静态锚点; anchor-robustness 对照, 不替换 vintage 主轨)。
    """
    # setup_logging 接线 (golden 范式): 本模块的 logger 自 encode.py import,
    # 其 STAGE_NAME='40_build_panel' → stage 15 日志原会落入 40_build_panel.log。
    # 此处按本阶段 STAGE_NAME 重接, 使 <stage>.log 命名为 16_article_policy_alignment.log
    # (纯日志路由, 不改任何返回值/产物/计量逻辑)。
    global logger
    from news_process.core.logging import setup_logging
    logger = setup_logging(STAGE_NAME, CONFIG["paths"].get("log_dir", "logs"))

    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")

    # ---- 【功能】banner (golden 范式: 紧随"开始执行阶段"之后) ----
    logger.info("=" * 72)
    logger.info("阶段 15: 文章级政策语义对齐度 (Distel/Grimpe/Poetz 2026 RP §3.2.1; "
                "余弦相似度 Hoberg & Phillips 2016 JPE)")
    logger.info("=" * 72)
    logger.info("【功能】给每篇金科新闻打一个『政策对齐分』(余弦相似度 ∈ [-1,1], 实务多落 0~1): 把国家重磅金科政策文件浓缩成")
    logger.info("        一份『标准答案向量』, 再算每篇新闻向量与它的夹角余弦; 产出 policy_cosine_sim")
    logger.info("        族列 (full/ctx/ss 三轨 + _lg 双 co-primary twin), 供 stage 45 四象限分类消费。")
    logger.info("【方法】policy_cosine_sim_i = cos(emb(article_i), emb(auth_anchor)), 值域 [-1,1] 实务多落 0~1。")
    logger.info("        anchor = 权威语料按文档朴素分段 → mean pooling + L2 归一化; vintage-aware 前视守卫:")
    logger.info("        年度 t 文章只与发布年份 ≤ t 的政策段算锚 (article_alignment.vintage_aware)。")
    logger.info("        双 co-primary (全平价): MAIN=Qwen-embedding(API,4096维) → canonical 无后缀; LARGE=text-embedding-3-large(API,3072维) → _lg。")
    logger.info("        全年份锚点稳健孪生 (_allv, all_vintage_companion): 并列再用『所有年份』政策段拼静态锚点算一套")
    logger.info("        policy_cosine_sim_allv* (anchor-robustness 对照, 含未来政策文本, 绝不替换 vintage 主轨)。")
    logger.info("【判读】分数越高 = 这篇新闻越贴政策方向 (实质性); 越低 = 越不沾边 (象征性/无关)。")
    logger.info("        full↔ctx Spearman ρ < 0.95 = 轨道真独立 (期望); 三轨值域须 ⊆ [-1,1]。")
    logger.info("【确定性】调 Embedding API (MAIN + _lg 两 co-primary 轨, miss 即付费; 不受 NEWS_PROCESS_LLM_OFFLINE 守卫保护)。")
    logger.info("          API 向量经 _llm_cache.db 缓存, 命中即逐位可复现。")

    # ---- 🧭 项目 / 环境信息 (golden 范式 ①: 运行环境指纹, 纯日志) ----
    # crash-guard: 整块包 try/except, 任何环境探针异常仅降级 warning, 绝不让纯日志块崩阶段。
    try:
        import platform as _platform
        logger.info("-" * 72)
        logger.info("🧭 项目 / 环境信息")
        logger.info("  · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) | 版本 v3.11.1")
        logger.info(f"  · 阶段: {STAGE_NAME} (STAGES_MAIN, kind=filter, timeout=7200s 因含 Embedding API)")
        logger.info("  · 功能: 文章级政策语义对齐度 (article-level policy cosine similarity), 供 stage 45 四象限分类")
        logger.info(f"  · Python {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"  · 平台: {_platform.platform()} | CPU {os.cpu_count()} 核 | PID {os.getpid()}")
        logger.info(f"  · RUN_ID={os.environ.get('NEWS_PROCESS_RUN_ID', '(未设)')} | "
                    f"LLM_OFFLINE={os.environ.get('NEWS_PROCESS_LLM_OFFLINE', '0')} "
                    "(⚠ 本阶段嵌入 miss 不受该守卫保护, 仍付费调 API)")
        logger.info("  · 成本/确定性: MAIN + _lg 两 API co-primary 嵌入 miss 即付费 "
                    "(MAIN/Qwen 经硅基流动, _lg/large 经 yunwu, 均 OpenAI-compat); "
                    "缓存命中即逐位可复现")
        logger.info(f"  · 模块: {os.path.abspath(__file__)}")
        logger.info(f"  · 工作目录: {os.getcwd()}")
    except Exception as _e:
        logger.warning(f"[环境信息] 探针异常, 跳过(不影响产物): {_e}")

    # ---- 📖 方法论依据 (golden 范式 ④: 核心方法学出处 emit 进日志, 仅引经核验注册表) ----
    # 5 个 DOI 逐字取自 VERIFIED_REFERENCES 注册表 (Crossref 核验, status=match); 不自创/不改动。
    try:
        logger.info("-" * 72)
        logger.info("📖 方法论依据 (本阶段核心方法/构念的学术出处, 进日志以供审计追溯)")
        logger.info("  · 余弦相似度作为文本语义距离的标准度量 (本阶段核心算子):")
        logger.info("    Hoberg, G., & Phillips, G. (2016). Text-based network industries and "
                    "endogenous product differentiation. Journal of Political Economy, 124(5), "
                    "1423-1465. https://doi.org/10.1086/688176")
        logger.info("  · 句嵌入余弦相似度与可解释性 (本阶段 dense-embedding 语义对齐算子的近期方法学锚, 2023-2026):")
        logger.info("    Opitz, J., Moeller, L., Michail, A., Padó, S., & Clematide, S. (2025). "
                    "Interpretable text embeddings and text similarity explanation: A survey. In "
                    "Proceedings of the 2025 Conference on Empirical Methods in Natural Language "
                    "Processing (pp. 22314-22330). Association for Computational Linguistics. "
                    "https://doi.org/10.18653/v1/2025.emnlp-main.1135")
        logger.info("  · 金融文本嵌入基准 (含中英监管文件 STS, 锚定嵌入余弦做金融/政策相似度的构念依据, 2023-2026):")
        logger.info("    Tang, Y., & Yang, Y. (2025). FinMTEB: Finance Massive Text Embedding "
                    "Benchmark. In Proceedings of the 2025 Conference on Empirical Methods in "
                    "Natural Language Processing (pp. 3620-3638). Association for Computational "
                    "Linguistics. https://doi.org/10.18653/v1/2025.emnlp-main.179")
        logger.info("  · 宏观政策向量注入微观企业文本空间 (锚点注入范式):")
        logger.info("    Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). "
                    "Firm-level political risk: Measurement and effects. The Quarterly Journal "
                    "of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021")
        logger.info("  · 逐篇文档级相似度 / 显性引用 vs 文本级语义实质借鉴 (Token vs Hidden 解耦):")
        logger.info("    Distel, A. P., Grimpe, C., & Poetz, M. (2026). From evidence to impact: "
                    "The use of scientific research in policy documents. Research Policy, 55(3), "
                    "105426. https://doi.org/10.1016/j.respol.2026.105426")
        logger.info("  · 象征性采用的制度理论基础 (Token Adoption 获取合法性):")
        logger.info("    Westphal, J. D., & Zajac, E. J. (2001). Decoupling policy from practice: "
                    "The case of stock repurchase programs. Administrative Science Quarterly, "
                    "46(2), 202-228. https://doi.org/10.2307/2667086")
        logger.info("  · Cheap talk 偏差 (高频关键词 ≠ 实质性行动, 需语义层独立度量):")
        logger.info("    Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). "
                    "Cheap talk and cherry-picking: What ClimateBert has to say on corporate "
                    "climate risk disclosures. Finance Research Letters, 47, 102776. "
                    "https://doi.org/10.1016/j.frl.2022.102776")
    except Exception as _e:
        logger.warning(f"[方法论] 引文输出异常, 跳过(不影响产物): {_e}")

    # ---- ⚙ 运行配置 (golden 范式 ③: 本阶段可调参数 + config 来源键, 纯日志) ----
    try:
        logger.info("-" * 72)
        logger.info("⚙ 运行配置 (来源 config/filtering.yaml::article_alignment + config/paths.yaml)")
        logger.info(f"  · vintage_aware 前视守卫: {vintage_aware_enabled()} "
                    "(article_alignment.vintage_aware; True=年度 t 仅用 ≤t 政策段)")
        logger.info(f"  · all_vintage_companion (_allv 全年份锚点孪生): {all_vintage_companion_enabled()} "
                    "(article_alignment.all_vintage_companion; 仅稳健性对照, 不替换主轨)")
        logger.info(f"  · 单条输入 token 上限 max_tokens_per_input: {_MAX_TOKENS_PER_INPUT:,d} | "
                    f"单次请求 token 上限 max_tokens_per_request: {_MAX_TOKENS_PER_REQUEST:,d}")
        logger.info(f"  · MAIN spec (canonical, 无后缀): {_eng.spec_model(EMBEDDING_CONFIG)} "
                    "(Qwen-embedding, API 4096 维)")
        if _LARGE_SPEC:
            logger.info(f"  · LARGE spec (_lg co-primary): {_eng.spec_model(_LARGE_SPEC)} "
                        "(text-embedding-3-large, API 3072 维; 与 MAIN 全平价, 维度不同严禁混算)")
        logger.info(f"  · 缓存库: {CACHE_DB_PATH} | 重试间隔: {sig4(RETRY_DELAY)}s 固定 (flat, 2026-06-26 全项目统一)")
        logger.info("  · 权威语料: config/authoritative_corpus.txt (paths.authoritative_corpus_file, 与 stage 26 共享)")
    except Exception as _e:
        logger.warning(f"[运行配置] 输出异常, 跳过(不影响产物): {_e}")

    # per-phase 墙钟计时锚点 (golden 范式 ⑥): 各子阶段 time.time() 差, 末尾汇总。
    _phase_t = {}

    # 读取 Stage 14 输出
    output_dir = CONFIG['paths']['output_dir']
    input_filename = CONFIG['filenames'].get(
        'output_14_fintech_intensity', '15_fintech_intensity.parquet')
    input_path = os.path.join(output_dir, input_filename)

    if not os.path.exists(input_path):
        logger.error(f"输入文件未找到: {input_path}")
        raise SystemExit(1)

    logger.info(f"加载输入: {input_path}")
    _t0 = time.time()
    df = pd.read_parquet(input_path)
    _phase_t['加载输入parquet'] = time.time() - _t0
    logger.info(f"输入数据: {len(df):,d} 篇文档, {len(df.columns):,d} 列")

    # 执行计算 (含语料加载 + 双 co-primary 三轨嵌入 + 余弦 + 统计诊断)
    _t0 = time.time()
    df = compute_article_policy_alignment(df)
    _phase_t['嵌入+余弦计算'] = time.time() - _t0

    # 列完整性断言
    assert 'policy_cosine_sim' in df.columns, "policy_cosine_sim 列缺失!"
    assert 'fintech_intensity_score' in df.columns, \
        "原有列 fintech_intensity_score 丢失! (零破坏性违规)"
    assert 'fintech_distinct_keywords' in df.columns, \
        "原有列 fintech_distinct_keywords 丢失! (零破坏性违规)"

    # 保存输出
    output_filename = CONFIG['filenames'].get(
        'output_15_article_alignment', '16_article_alignment.parquet')
    output_path = os.path.join(output_dir, output_filename)

    from news_process.core.logging import log_stage_summary
    from news_process.core.reporting import save_dataset
    # 使用数据版本控制保存
    input_file = os.path.join(CONFIG['paths']['output_dir'],
                              CONFIG['filenames']['output_14_fintech_intensity'])
    _t0 = time.time()
    save_dataset(
        df=df,
        output_path=output_path,
        logger=logger,
        stage_name="16_article_policy_alignment",
        config=CONFIG,
        input_files=[input_file],
    )
    _phase_t['写盘parquet'] = time.time() - _t0

    # 统计报告
    n_valid = df['policy_cosine_sim'].notna().sum()
    logger.info(f"  有效 policy_cosine_sim: {n_valid:,d}/{len(df):,d} "
                f"({pct4(n_valid / max(len(df), 1))})")

    # ---- 【结果分析】(golden 范式: 取真实产出指标 + 对照阈值/方向给判读) ----
    # 全部为日志专用局部量, 不回写 df / 不改任何产物。
    # crash-guard (golden-safety): 整块包 try/except, 任何诊断异常 (空 Series / 缺列 /
    # scipy 行为变更等) 只降级为 warning, 绝不让纯日志块崩掉阶段。本块虽已在 save_dataset
    # 之后 (产物已落盘), 仍兜底防 main() 非零退出污染编排链。
    try:
        logger.info("-" * 72)
        logger.info("【结果分析】文章级政策对齐分质检 —— 逐轨值域/覆盖率/轨间独立性, 以下判读仅供解读:")
        _n_total = len(df)

        # (1) 主轨覆盖率 (有效非 NaN 占比): vintage 前视守卫会把年份未知/早于全部政策的文章合法置 NaN。
        _valid_pct = n_valid / max(_n_total, 1) * 100
        if _valid_pct >= 90:
            _cov_judge = "好 (绝大多数文章落在政策发布年之后, 前视守卫几乎不丢分)"
        elif _valid_pct >= 50:
            _cov_judge = "临界 (相当比例文章年份未知或早于全部政策 → 合法 NaN, 检查 year/日期 列与语料最早 vintage)"
        else:
            _cov_judge = "差/可疑 (多数文章无对齐分; 多因 vintage 前视守卫剔除或锚点缺失, 须核语料年份覆盖)"
        logger.info(f"  · canonical 主轨覆盖率 policy_cosine_sim: {n_valid:,d}/{_n_total:,d} "
                    f"({pct4(_valid_pct, fraction=False)}) → {_cov_judge}")

        # (2) 逐轨值域/均值判读: 政策余弦实务多落 0~1, 均值偏高=语料整体偏政策腔, 偏低=偏市场化报道。
        _track_cols = [
            ('full ', 'policy_cosine_sim_full'),
            ('ctx  ', 'policy_cosine_sim_ctx'),
            ('ss   ', 'policy_cosine_sim_ss'),
            ('lg_f ', 'policy_cosine_sim_lg_full'),
            ('lg_c ', 'policy_cosine_sim_lg_ctx'),
            ('lg_s ', 'policy_cosine_sim_lg_ss'),
            # 全年份锚点 _allv 孪生 (缺列 = companion 关闭, 自动跳过)
            ('avf  ', 'policy_cosine_sim_allv_full'),
            ('avc  ', 'policy_cosine_sim_allv_ctx'),
            ('avs  ', 'policy_cosine_sim_allv_ss'),
            ('av_lgf', 'policy_cosine_sim_lg_allv_full'),
            ('av_lgc', 'policy_cosine_sim_lg_allv_ctx'),
            ('av_lgs', 'policy_cosine_sim_lg_allv_ss'),
        ]
        for _nm, _col in _track_cols:
            if _col not in df.columns:
                continue
            _arr = df[_col].to_numpy(dtype=float)
            # NaN-guard: 全 NaN 轨直接走"无有效数据"分支, 不落入均值/方向判读 (否则打 nan)。
            if np.isnan(_arr).all():
                logger.warning(f"  · {_nm} 轨 ({_col}) 全 NaN (该轨无有效数据) → 嵌入失败或上游列缺失, "
                               f"下游消费该轨将退化 (优雅降级披露)")
                continue
            _lo, _hi = np.nanmin(_arr), np.nanmax(_arr)
            _mu, _sd = np.nanmean(_arr), np.nanstd(_arr)
            _range_ok = (_lo >= -1.0 - 1e-6) and (_hi <= 1.0 + 1e-6)
            _range_judge = "值域合法 ⊆[-1,1]" if _range_ok else "⚠ 值域越界! 嵌入/池化异常"
            logger.info(f"  · {_nm} 轨 {_col}: 范围=[{sig4(_lo)}, {sig4(_hi)}] 均值={sig4(_mu)} σ={sig4(_sd)} → {_range_judge}")

        # (3) 轨间独立性 (full vs ctx): ρ 过高说明 ctx 局部窗口未带来增量信号 (退化为 full)。
        if ('policy_cosine_sim_full' in df.columns
                and 'policy_cosine_sim_ctx' in df.columns):
            _f = df['policy_cosine_sim_full'].to_numpy(dtype=float)
            _c = df['policy_cosine_sim_ctx'].to_numpy(dtype=float)
            _both = ~np.isnan(_f) & ~np.isnan(_c)
            _n_both = int(_both.sum())
            if _n_both < 3:
                logger.info(f"  · 轨间独立性 full↔ctx: 共同有效样本 {_n_both} <3, 跳过 (样本不足)")
            elif _f[_both].min() == _f[_both].max() or _c[_both].min() == _c[_both].max():
                logger.info("  · 轨间独立性 full↔ctx: 某轨零方差 (常量), Spearman ρ 无定义, 跳过")
            else:
                try:
                    from scipy.stats import spearmanr
                    _rho, _ = spearmanr(_f[_both], _c[_both])
                    if abs(_rho) < 0.95:
                        _rho_judge = "好 (轨道真独立, ctx 局部窗口带来增量信号)"
                    elif _f[_both].tolist() == _c[_both].tolist():
                        _rho_judge = "已知降级 (content_ctx 缺失 → ctx 轨回退为 full, ρ≈1 符合预期)"
                    else:
                        _rho_judge = "⚠ 高度相关 (ctx 与 full 近乎一致, 独立性存疑, 须核 content_ctx 物化)"
                    logger.info(f"  · 轨间独立性 full↔ctx: Spearman ρ={sig4(_rho)} (n={_n_both:,d}) → {_rho_judge}")
                except ImportError:
                    logger.info("  · 轨间独立性 full↔ctx: scipy 缺失, 跳过相关性诊断")

        # (4) 双 co-primary 一致性 (MAIN(Qwen) 与 _lg(large) 同向则结论更可信)。
        if ('policy_cosine_sim_full' in df.columns
                and 'policy_cosine_sim_lg_full' in df.columns):
            _m = df['policy_cosine_sim_full'].to_numpy(dtype=float)
            _t = df['policy_cosine_sim_lg_full'].to_numpy(dtype=float)
            _mt = ~np.isnan(_m) & ~np.isnan(_t)
            _n_mt = int(_mt.sum())
            if _n_mt < 3:
                logger.info(f"  · 双模型一致性 MAIN↔lg(full): 共同有效样本 {_n_mt} <3, 跳过 (_lg 轨可能全 NaN/未跑)")
            elif _m[_mt].min() == _m[_mt].max() or _t[_mt].min() == _t[_mt].max():
                logger.info("  · 双模型一致性 MAIN↔lg(full): 某轨零方差, 相关性无定义, 跳过")
            else:
                try:
                    from scipy.stats import spearmanr
                    _rho_mt, _ = spearmanr(_m[_mt], _t[_mt])
                    _mt_judge = ("好 (两套嵌入同向, 对齐分稳健)" if _rho_mt >= 0.3
                                 else "临界/弱 (两套嵌入结论分歧, 稳健性对照偏弱, 披露即可)")
                    logger.info(f"  · 双模型一致性 MAIN↔lg(full): Spearman ρ={sig4(_rho_mt)} (n={_n_mt:,d}) → {_mt_judge}")
                except ImportError:
                    pass

        # (5) 小样本 / 依赖缺失警告。
        if _n_total < 50:
            logger.info(f"  · ⚠ 小样本: 本次仅 {_n_total:,d} 篇 (盘面 T=2 演示规模) → 上述判读仅验证管道正确性, "
                        f"全量结论以 17M/T=18 实测为准。")
        if 'policy_cosine_sim_ss' not in df.columns:
            logger.warning("  · content_ss 未物化 → ss 三轨 (policy_cosine_sim_ss / _lg_ss) 未产出, "
                           "下游 ss 轨对齐信号缺失 (镜像 ctx 缺列优雅降级)。")
        if 'policy_cosine_sim_lg_full' in df.columns and df['policy_cosine_sim_lg_full'].isna().all():
            logger.warning("  · co-primary (_lg) 全 NaN → large 嵌入失败 → both-or-neither 联动应同时使 "
                           "canonical 置 NaN (须核查 parity 守卫)。")
        logger.info("-" * 72)
    except Exception as _e:
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")

    # ---- ⏱ 阶段计时 (golden 范式 ⑥: 各子阶段墙钟耗时, 末尾汇总; 秒数 sig4) ----
    try:
        logger.info("⏱ 阶段计时 (per-phase wall-clock, 秒)")
        for _ph, _sec in _phase_t.items():
            logger.info(f"  · {_ph}: {sig4(_sec)} s")
        logger.info(f"  · 小计 (已计时子阶段): {sig4(sum(_phase_t.values()))} s "
                    f"/ 阶段总墙钟: {sig4(time.time() - stage_start)} s")
    except Exception as _e:
        logger.warning(f"[阶段计时] 输出异常, 跳过(不影响产物): {_e}")

    log_stage_summary(logger, STAGE_NAME, stage_start, len(df), len(df))
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


if __name__ == "__main__":
    main()
