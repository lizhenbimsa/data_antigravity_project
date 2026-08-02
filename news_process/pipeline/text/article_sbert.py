"""news_process.pipeline.text.article_sbert — stage 30a article-level SBERT 持久化.

v3.7.0 PR #9 — D 组前置. 把 stage 30 内部计算后即丢的 article-level SBERT
embeddings 持久化, 让 D2 (staleness) / D3 (Krippendorff α)
能直接复用, 避免重复编码 (节省 ~12-15 h 计算).

学术依据
--------
Bybee, L., Kelly, B. T., Manela, A., & Xiu, D. (2024). Business news and
business cycles. The Journal of Finance, 79(5), 3105-3147.
https://doi.org/10.1111/jofi.13377
→ 标题 + 首段 300 字策略 (**v1 口径, 2026-07-26 起退役**; 其理由「避免 SBERT
  512-token 截断丢尾段」属本地 SentenceTransformer 时代, API 化后已失效 — 见
  「输入策略」段)
  (期刊订正: 此前误标 RFS 37(3):887-936, 经 Crossref 核验为 JF 79(5);
   与 scripts/audit/LITERATURE_ANCHORS_2026-06-13.md:140 锚点对齐)

设计决策
--------
1. **嵌入模型 (v3.14.0, 2026-06-27 — all-API co-primary 双轨, 零本地模型)**: 每轨用
   两个 API spec 各嵌一遍 —— MAIN (canonical 无后缀) = ``config/features.yaml::embedding_api``
   (Qwen/Qwen3-Embedding-8B, 阿里/硅基流动) + ``_lg`` (孪生) = ``embedding_large``
   (text-embedding-3-large, OpenAI)。两者地位对等、互为稳健性 (跨厂商独立性), ``_lg``
   后缀仅命名机制无层级。统一经 ``embedding_engine.embed_texts(spec=…)`` (API 路径,
   经 ``_llm_cache.db`` 穿透缓存); 本地 SentenceTransformer (text2vec/bge-m3) 已整体移除。
2. **输入策略 (v2, 2026-07-26 用户裁定改整篇; v1 为 Bybee 400 字截断, 已退役但保留可回退)**:
   **整篇** content_{full,ctx,ss}, 与 stage 16 ``policy_alignment.main()`` **逐字节同构**
   (full 轨 ``.str.strip()``; ctx/ss 轨不 strip —— 该不对称是 stage 16 既有事实, 照抄),
   无预截断, 超长交引擎 ``split_text_for_embedding`` 切块 + token 加权池化。
   改因: v1 的理由「中文新闻 ~1200 token > SBERT max_seq_len=512」属 v3.14.0 之前的本地
   模型约束, API 化后单条上限 8191 token; 生产实测 content_full 均值 1,512 字 / p95
   4,003 字, **块扩展因子 1.0118 (99% 单块直送)**, 截断前提消失。
   收益 (2026-07-26 只读探针实测): 三轨并集 582,724 唯一块, 两 spec 各 **582,724/582,724
   命中 miss=0** ⟹ 本阶段零新增付费嵌入 (全部复用 stage 16 已播条目)。
   代价: 向量改变 ⟹ stage 26 ``semantic_staleness_*`` 及 ``_lg`` 孪生改数, 面板下游随之
   改数; 且 surface 轨本就是整篇 MinHash, semantic 改整篇后**互补性可能下降**, 每次重生
   须复核 G-D2.1 诊断带 corr∈[0.3,0.7] 并如实披露。
   ⚠ 缓存键命名空间 (``text_pipeline_version``) **不得因本变更 bump** —— 见常量区告警。
3. **嵌入轴 full/ctx/ss 三路平价 × co-primary 双 spec**:
   full 读 content_full / ctx 读 content_ctx / ss 读 content_ss (三者均由 stage 13
   prepend 标题【恰好一次】), 编码时 title_col=None 关闭二次前置 → 三轨同型构造、标题各一次;
   仅输入文本范围不同 (全文 vs 实体窗口 vs 银行+金科同句窗口)。缺 content_full 时回退裸
   '内容'+'标题' (v2 走 ``prepend_title(t, b).strip()``, 与 stage 16 回退分支同构, 标题一次;
   v1 曾走 _truncate_for_sbert Bybee 前置)。
   **🔴 both-or-neither parity (D-4a)**: 每轨 MAIN 或 _lg 任一 embed_texts 返回 None →
   该轨两列 (emb_X / emb_X_lg) 同缺 (不留单边孤儿列)。content_ss/content_ctx 缺列 (旧 schema)
   时该轨两列均不写, 下游 stage 26 优雅缺席对应 semantic_staleness (向后兼容)。
4. **存储**: parquet (article_id, target_bank, year, emb_{full,ctx,ss}[4096] (Qwen MAIN) +
   emb_{full,ctx,ss}_lg[3072] (large) + 双套 provenance)。回退行其 emb_ss≡emb_full。

D-0 实测项
----------
- Qwen / text-embedding-3-large 经各自端点可达性 + corr(Qwen, large) 跨厂商互证一致性
- API 缓存命中率 (NEWS_PROCESS_LLM_OFFLINE=1 离线 $0 复现的前提是 _llm_cache.db 0-miss)

运行方式
---------
本 stage 已注册于 core/dag.py::STAGES_MAIN (无 enabled_when 条件, 随主管道
always-on 执行); 也可单独手动触发:
    python news_process/25_article_sbert.py

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 25_article_sbert.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**在 DAG 中的位置**: STAGES_MAIN 阶段30a, kind=robustness, timeout=21600(GPU 4-6h / CPU 12-24h)。D 组前置阶段, 上游 = stage 13(14_news_with_ctx.parquet), 下游被 stage 18(D2 staleness 的 semantic 轨)及模块 docstring 提及的 D3(Krippendorff α, 39c/39d/39f 族)复用——核心动机是把 article-level SBERT 嵌入持久化一次, 避免多处重复编码(节省约12-15h)。

**输入**: `14_news_with_ctx.parquet`(article 级; 优先用 content_full / content_ctx / content_ss, 缺则回退 内容 + 标题)。

**处理步骤** (v3.14.0, 2026-06-27 all-API co-primary 双轨):
1. 嵌入 spec 从 `config/features.yaml` 取两套: MAIN=`embedding_api` (Qwen/Qwen3-Embedding-8B) + `_lg`=`embedding_large` (text-embedding-3-large); 各带 text_pipeline_version 作缓存命名空间。
2. `encode_articles(df, content_col, spec, …)`: 文本构造 = **整篇** content_{track} (v2, 2026-07-26; 与 stage 16 policy_alignment 逐字节同构 — full 轨 strip / ctx·ss 不 strip, 无预截断)。v1 的 Bybee'标题(≤100字)+首段(≤300字)'口径已退役, 常量与 `_truncate_for_sbert` 保留供一键回退 (INPUT_STRATEGY='bybee400_v1')。**关键对称性**: content_full/content_ctx/content_ss 已由 stage 13 prepend 标题恰好一次, 故 `title_col=None` 关闭二次前置。经 `embedding_engine.embed_texts(spec=…)` 走 API 路径 (穿透 _llm_cache.db); 返回单位归一向量 (N, 4096) (Qwen) / (N, 3072) (large) float32; embed_texts 返回 None (API 重试耗尽) 时该轨置 None。
3. 每轨 (full/ctx/ss) 用 MAIN + _lg 两 spec 各嵌一遍 (`_embed_track_dual`); both-or-neither: 任一 None 则该轨两列同缺。emb_full 读 content_full(缺则裸 内容+标题), emb_ctx 读 content_ctx(缺列则不产), emb_ss 读 content_ss(缺列则不产)。
4. `_build_output_frame`: 组装 article_id(= stage 13 的 df.index, 供 stage 26 显式 join 对齐键)+ docid 透传 + target_bank/year/日期 + emb_{full,ctx,ss}(Qwen) + emb_{full,ctx,ss}_lg(large)(parquet 兼容的 list-of-1D-array; 缺轨不写)+ 双套 provenance(MAIN model_id/model_revision/text_pipeline_version + _lg 镜像三元组)。

**外部依赖/确定性**: 统一引擎 `embed_texts` 两 API spec (Qwen 经硅基流动 + text-embedding-3-large 经 OpenLux)。需 EMBEDDING_API_KEY; 经 _llm_cache.db 穿透缓存命中即 $0 逐位复现 (NEWS_PROCESS_LLM_OFFLINE=1 强制离线, 须 0-miss)。无本地模型加载。timeout=21600。

■ 白话说明

这一步把每篇新闻'翻译'成一串数字(语义向量; Qwen 主轨 4096 个数), 让计算机能比较'两篇新闻意思像不像', 然后把这些向量存成文件备用。

打个比方: 它像一个一次性的'语义指纹采集站'——把40万篇新闻挨个扫一遍, 给每篇生成一个'意思指纹', 存进一个大文件。为了省时间和保证一致, 它只读每篇的'标题 + 开头300字'(中文新闻中位数约800字, 模型一次读不完整篇, 而开头通常已含核心信息), 而且特意保证标题只被算进去一次(否则带标题的窗口会把标题权重算重)。

为什么需要它: 后面好几个步骤都要用'语义像不像'——比如 stage 18 判断一篇新闻是不是'旧闻重印'、还有评估多个评分者一致性的步骤(D3)。如果每个步骤各自重新算一遍这些指纹, 要多花十几个小时。这一步算一次、存下来、大家共用, 是个纯粹的'性能/复用'前置, 本身不产出面板里的最终变量。

对最终面板/论文的影响: 它是间接的'地基'——它算出的语义向量喂给 stage 18 的'语义陈旧度', 进而进入稳健性检验。如果这里模型选错、标题被算重、或不同步(比如上游新闻重生了它却没重算导致向量和文章对不上号), 下游的语义相似度就会变成噪音; 代码因此特意用 article_id 严格配对并在对不上时直接报错停下, 强制重算, 防止论文用到错位的语义信号。它现在算三条轨的语义向量: '全文'、'银行局部窗口'、'银行+金科同句窗口'(第三条 ss 轨 2026-06-21 上线, 与前两条平价), 分别喂给 stage 18 的三轨语义陈旧度。
========================================================================
"""

from __future__ import annotations

import os
import platform
import sys
import time
from typing import Optional

import numpy as np
import pandas as pd

# v3.14.0 (2026-06-27, all-API-embedding): stage 25 弃本地 SentenceTransformer,
# 改走统一引擎 embed_texts 的两 API spec (Qwen MAIN + text-embedding-3-large _lg)
# co-primary 双轨。本地嵌入模型 (text2vec/bge-m3) 已整体移除, 故不再设 HF 离线 env
# (无任何本地模型加载) — title+300char 短文本经 API 嵌入, 维度 Qwen 4096 / large 3072。

# 路径注入: 让 ``news_process.core.*`` 在任意 cwd 下可解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.caching import LLMCache  # noqa: E402
from news_process.core.config import load_config  # noqa: E402
from news_process.core.data_versioning import save_parquet_with_metadata  # noqa: E402
from news_process.core.logging import pct4, setup_logging, sig4  # noqa: E402
from news_process.pipeline.text import _constants as _CONST  # noqa: E402
from news_process.pipeline.text import embedding_engine as _eng  # noqa: E402

CONFIG = load_config()
STAGE_NAME = "25_article_sbert"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# ── v3.14.0 (2026-06-27): co-primary 双 API 嵌入 spec (零本地模型) ──
# MAIN (canonical, 无后缀) = Qwen/Qwen3-Embedding-8B (config embedding_api)
# _lg (孪生槽)            = text-embedding-3-large (config embedding_large)
# 两者地位对等、互为稳健性 (跨厂商 阿里 Qwen ⟂ OpenAI), `_lg` 后缀仅命名机制无层级。
# v2 (2026-07-26) 整篇输入: 生产实测块扩展因子 1.0118 → ~99% 单块直送, 超 8191 token 的极长文
# 由引擎切块 + token 加权池化 (v1「title+300char 远未触上限、绝不分块」已退役)。
# 维度 Qwen 4096 / large 3072 (不同, 余弦维度无关绝不混算)。
_MAIN_SPEC = CONFIG.get('embedding_api', {})
_LARGE_SPEC = CONFIG.get('embedding_large', {})

# LLMCache 路径 (穿透式缓存, 跨 run/跨 stage 命中即 $0 复现; 与 5 cosine producer 同源)。
CACHE_DB_PATH = CONFIG['paths'].get(
    'llm_cache_db', os.path.join(CONFIG['paths']['output_dir'], '_llm_cache.db')
)

# provenance: MAIN (Qwen) + _lg (large) 两套 (model_id, text_pipeline_version),
# 供 stage 26 对两套嵌入各自独立 fail-loud 校验 (镜像 5 cosine producer 缓存键维度)。
_SBERT_MODEL_ID = _eng.spec_model(_MAIN_SPEC, default='Qwen/Qwen3-Embedding-8B')
_SBERT_MODEL_ID_LG = _eng.spec_model(_LARGE_SPEC, default='text-embedding-3-large')

# 30a 输入文本构造版本 (provenance, 与 LLMCache 的 prompt_version 维度同哲学):
# v4 = 2026-06-28 all-API co-primary dual (Qwen MAIN + large _lg; content_full/ctx/ss
# 已 prepend 标题一次, title_col=None 关二次前置)。
# ⚠⚠ **绝不因本模块的输入构造变更去 bump 这两个版本号** (2026-07-26 用户裁定改整篇时的
#   头号陷阱): 它们是 `_eng.spec_version(spec)` 读出的 **spec 级共享**命名空间 (config
#   `embedding_api.text_pipeline_version` / `embedding_large.…`), 被 stage 15/16/26/27/40
#   共用 —— 一旦 bump, 全部已播种嵌入 (2026-07-24/25 生产首播 117 万条 + 本轮增量) **全部
#   作废需重播**。本模块 2026-07-26 的构造变更**恰好不需要 bump**: 新构造与 stage 16
#   (policy_alignment) 逐字节同构 ⟹ 缓存键与其**已在 v4 命名空间下的正确条目重合**。
#   构造代际改由下方 `INPUT_STRATEGY` 单独记入产物 provenance 列 (不进缓存键)。
_TEXT_PIPELINE_VERSION = _eng.spec_version(_MAIN_SPEC)
_TEXT_PIPELINE_VERSION_LG = _eng.spec_version(_LARGE_SPEC)

# ── 输入文本构造策略 (2026-07-26 用户裁定: v1 Bybee 400 字截断 → v2 整篇) ──
# **为何改**: v1 的书面理由是「中文新闻中位 ~800 字 ≈1200 token > SBERT max_seq_len=512,
#   取标题(≤100)+首段(≤300) 避免 512-token 截断丢尾」—— 该约束属 v3.14.0 之前的**本地
#   SentenceTransformer 时代**; 改走 API 后单条上限 8191 token, 实测生产语料 content_full
#   均值 1,512 字 / p95 4,003 字, **块扩展因子仅 1.0118 (99% 单块直送, 不触发池化)**,
#   截断的技术前提已消失。
# **改成什么**: 与 stage 16 `policy_alignment.main()` **逐字节同构** ——
#   full 轨 `.str.strip()`; ctx/ss 轨**不** strip (该不对称是 stage 16 的既有事实, 照抄);
#   无预截断, 超长交引擎 `split_text_for_embedding` 切块 + token 加权池化。
# **收益 (实测, 非估算)**: 2026-07-26 只读探针 — 三轨并集 582,724 个唯一块, 两 spec
#   **各 582,724/582,724 命中, miss=0** ⟹ stage 25 改造后**零新增付费嵌入**。
# **代价 (须知情)**: 本模块向量改变 ⟹ stage 26 `semantic_staleness_{full,ctx,ss}` 及其
#   `_lg` 孪生改数 ⟹ 面板与下游 40/46/51 相关列改数。另: stage 26 的 surface 轨是整篇
#   MinHash, semantic 轨改整篇后两者**互补性可能下降** (设计诊断带 corr∈[0.3,0.7],
#   见 article_staleness G-D2.1) → 每次重生须复核该诊断值并如实披露。
# v1 口径 (`_truncate_for_sbert` + TITLE_CHARS/FIRST_PARA_CHARS) **保留但已退役**:
#   供历史对照与一键回退 (把 _constants.INPUT_STRATEGY 改回 'bybee400_v1' 即可), 勿删。
# ⚠ SSOT 已迁至叶模块 `pipeline/text/_constants.py` (F22, 2026-07-27): orchestrator 的
#   --skip-unchanged 代码版本门要在**父进程**里 import 版本号, 而 import 本模块会触发
#   setup_logging → 截断本阶段生产日志。故常量下沉到零副作用叶模块, 此处仅 re-export
#   (保持 `article_sbert.INPUT_STRATEGY` 既有引用/monkeypatch 点不变)。
INPUT_STRATEGY = _CONST.INPUT_STRATEGY  # 'whole_text_v2' (现行) | 'bybee400_v1' (退役参照)
_VALID_STRATEGIES = _CONST.VALID_STRATEGIES

# Bybee 2024 风格 "标题 + 首段 300 字" 截断 (v1 退役口径; 保留供回退/历史对照)
TITLE_CHARS = 100
FIRST_PARA_CHARS = 300


def _truncate_for_sbert(title: str, content: str) -> str:
    """[v1 退役口径, 保留供回退] 构造 SBERT 输入: 截短标题 + 首段 300 字。

    ⚠ 仅在 INPUT_STRATEGY='bybee400_v1' 时生效; 现行 v2 走整篇 (见上方策略段)。"""
    t = (title or '')[:TITLE_CHARS].strip()
    c = (content or '')[:FIRST_PARA_CHARS].strip()
    if t and c:
        return f"{t} | {c}"
    return t or c


def _build_track_docs(
    df: pd.DataFrame,
    content_col: str,
    title_col: Optional[str] = '标题',
    *,
    strip_text: bool = False,
) -> list[str]:
    """构造一轨的输入文本 list。

    v2 (现行, INPUT_STRATEGY='whole_text_v2'): **整篇** content_{track}, 与 stage 16
    `policy_alignment.main()` 逐字节同构 —— `strip_text=True` 仅 full 轨用 (照抄 stage 16
    的既有不对称: full 带 `.str.strip()`, ctx/ss 不带); 无预截断, 超长交引擎切块池化。
    旧 schema 回退分支 (无 content_* 列时 title_col='标题') 亦对齐 stage 16 的
    `prepend_title(t, b).strip()`, 使两阶段在回退路径上同样共享缓存。

    v1 (退役, 'bybee400_v1'): 标题(≤100)+首段(≤300) 截断; 保留供一键回退。
    """
    if INPUT_STRATEGY not in _VALID_STRATEGIES:      # config 畸值 → fail-loud (绝不静默改测度)
        raise ValueError(
            f"article_sbert: 未知 INPUT_STRATEGY={INPUT_STRATEGY!r}; "
            f"合法值 {sorted(_VALID_STRATEGIES)}")

    if INPUT_STRATEGY == 'bybee400_v1':
        if title_col and title_col in df.columns:
            return [
                _truncate_for_sbert(t, c)
                for t, c in zip(df[title_col].fillna(''), df[content_col].fillna(''))
            ]
        return [
            (c or '')[:TITLE_CHARS + FIRST_PARA_CHARS]
            for c in df[content_col].fillna('')
        ]

    # ── v2 整篇 (与 stage 16 逐字节同构) ──
    if title_col and title_col in df.columns:
        # 旧 schema 回退: 镜像 policy_alignment 的 `prepend_title(t, b).strip()` 分支
        from news_process.core.text.entity_context import prepend_title
        _t = df[title_col].fillna('').astype(str)
        _c = df[content_col].fillna('').astype(str)
        return [prepend_title(t, b).strip() for t, b in zip(_t, _c)]
    _s = df[content_col].fillna('').astype(str)
    return _s.str.strip().tolist() if strip_text else _s.tolist()


def encode_articles(
    df: pd.DataFrame,
    content_col: str,
    spec: dict,
    title_col: Optional[str] = '标题',
    *,
    strip_text: bool = False,
    cache=None,
    log_prefix: str = "ArticleSBERT",
) -> np.ndarray | None:
    """经统一引擎 (embed_texts) 对一轨文本做 API 嵌入; 输出 (N, dim) numpy 数组.

    v3.14.0 (2026-06-27): 弃本地 SentenceTransformer, 改走 embed_texts(spec=…) 的
    API 路径 (Qwen MAIN 或 large _lg); 返回单位归一向量 (norm=1 → cosine=点积)。
    v2 (2026-07-26): 输入改**整篇** (与 stage 16 逐字节同构) —— 生产实测块扩展因子
    1.0118, 即 ~99% 文章仍单块直送, 余下超 8191 token 的极长文由引擎切块 + token 加权
    池化 (旧注「title+300char 远未触上限、引擎不分块」已随 v1 退役, 勿再据此推断)。

    Args:
        df: article-level DataFrame.
        content_col: 'content_full' / 'content_ctx' / 'content_ss' / '内容'.
        spec: 嵌入 spec (CONFIG['embedding_api'] 或 CONFIG['embedding_large']).
        title_col: '标题' (仅旧 schema 回退时用; content_* 已 prepend 标题恰好一次).
        strip_text: 是否对文本做 `.str.strip()` —— **仅 full 轨为 True**, 照抄 stage 16
            的既有不对称; 该值决定缓存键字节, 改动会使该轨全体 miss 并付费重嵌。
        cache: 已打开的 LLMCache 共享连接 (跨轨/跨 spec 复用)。

    Returns:
        (N, dim) float32 embeddings, 或 embed_texts 返回 None (API 重试耗尽/形状异常)
        时返回 None (该轨置 NaN, 由 main both-or-neither 联动降级)。
    """
    docs = _build_track_docs(df, content_col, title_col, strip_text=strip_text)

    logger.info(
        f"  编码 {len(docs)} 篇文章 (spec={_eng.spec_model(spec)}, content_col={content_col})"
    )
    t0 = time.time()
    embs = _eng.embed_texts(
        docs, spec, cache=cache, cache_db_path=CACHE_DB_PATH, log_prefix=log_prefix,
    )
    if embs is None:
        logger.warning(
            f"  编码失败: embed_texts({_eng.spec_model(spec)}) 返回 None "
            f"(API 重试耗尽/形状异常) → 该轨置 NaN"
        )
        return None
    embs = np.asarray(embs, dtype=np.float32)
    logger.info(f"  编码完成: {sig4(time.time() - t0)}s, shape={embs.shape}")
    return embs


def _build_output_frame(
    df: pd.DataFrame,
    embs_full: np.ndarray | None, embs_ctx: np.ndarray | None,
    embs_ss: np.ndarray | None = None,
    *,
    embs_full_lg: np.ndarray | None = None,
    embs_ctx_lg: np.ndarray | None = None,
    embs_ss_lg: np.ndarray | None = None,
) -> pd.DataFrame:
    """组装 30a 输出 frame (对齐键 + 双套 provenance + co-primary 6 嵌入列).

    v3.14.0 (2026-06-27, all-API co-primary 双轨): 每轨 (full/ctx/ss) 各产两个
    嵌入列 —— ``emb_{full,ctx,ss}`` (MAIN/Qwen, canonical 无后缀) +
    ``emb_{full,ctx,ss}_lg`` (large, _lg 孪生)。两套互为稳健性、地位对等。

    嵌入轴 full/ctx/ss 三路平价。``embs_ss=None`` (旧 schema 无 content_ss) 时不写
    emb_ss/emb_ss_lg 列, 向后兼容 — 下游 stage 26 据列是否存在决定产/不产
    semantic_staleness_ss(_lg) (优雅降级)。

    🔴 both-or-neither (D-4a parity): 某轨 MAIN 或 _lg 任一 embed_texts 返回 None →
    该轨两列 (emb_X / emb_X_lg) 均跳过 (由 main 联动判定后传入 None) → 不留单边孤儿列。

    provenance 双套 (与 LLMCache 键维度对齐): MAIN (model_id/model_revision/
    text_pipeline_version) + _lg 镜像 (model_id_lg/model_revision_lg/
    text_pipeline_version_lg) — 供 stage 26 对两套嵌入各自独立 fail-loud 校验
    (按 article_id 显式 join, 防 30a 陈旧静默错位)。
    """
    out: dict = {
        'article_id': df.index if 'article_id' not in df.columns else df['article_id'],
    }
    if 'docid' in df.columns:
        out['docid'] = df['docid']
    out.update({
        'target_bank': df['target_bank'] if 'target_bank' in df.columns else pd.NA,
        'year': df['year'] if 'year' in df.columns else pd.NA,
        '日期': df['日期'] if '日期' in df.columns else pd.NA,
    })
    # MAIN (Qwen) 三轨; None (both-or-neither 联动失败) 时跳过该列。
    if embs_full is not None:
        out['emb_full'] = list(embs_full)   # list of 1D arrays (parquet-compatible)
    if embs_ctx is not None:
        out['emb_ctx'] = list(embs_ctx)
    if embs_ss is not None:
        out['emb_ss'] = list(embs_ss)
    # _lg (large) 三轨孪生; 与 MAIN both-or-neither 双射 (同轨同存/同缺)。
    if embs_full_lg is not None:
        out['emb_full_lg'] = list(embs_full_lg)
    if embs_ctx_lg is not None:
        out['emb_ctx_lg'] = list(embs_ctx_lg)
    if embs_ss_lg is not None:
        out['emb_ss_lg'] = list(embs_ss_lg)
    out.update({
        # MAIN (Qwen) provenance
        'model_id': _SBERT_MODEL_ID,
        'model_revision': '',          # API spec 无 HF revision 概念 (保留列供向后兼容)
        'text_pipeline_version': _TEXT_PIPELINE_VERSION,
        # _lg (large) provenance 镜像三元组
        'model_id_lg': _SBERT_MODEL_ID_LG,
        'model_revision_lg': '',
        'text_pipeline_version_lg': _TEXT_PIPELINE_VERSION_LG,
        # 输入文本构造代际 (2026-07-26 新增): **不进缓存键**, 仅标记本产物由哪代构造生成。
        # 必要性: v1 (400 字截断) 与 v2 (整篇) 两代产物的 text_pipeline_version 同为 v4
        # (键命名空间未变, 见常量区「绝不 bump」告警), 若无本列则两代产物在 provenance 上
        # 不可区分 —— 而它们的 semantic_staleness 下游数值不同, 混用会静默串代。
        'sbert_input_strategy': INPUT_STRATEGY,
    })
    return pd.DataFrame(out)


def main():
    stage_start = time.time()
    logger.info("=" * 72)
    logger.info(
        "阶段 25: Article-level SBERT 嵌入持久化 "
        f"(v3.7.0 PR #9; 输入策略={INPUT_STRATEGY} — v2 整篇, 与 stage 16 逐字节同构)"
    )
    logger.info("=" * 72)
    logger.info(
        "【功能】把每篇新闻'翻译'成一串语义向量 (意思指纹, Qwen 4096 维 / large 3072 维), 一次性持久化成 "
        "25_article_embeddings.parquet 备用; 是 D 组前置 (stage 26 语义陈旧度 / D3 "
        "Krippendorff α 等)的共享地基, 算一次大家共用, 省重复编码。"
    )
    logger.info(
        "【方法】v3.14.0 co-primary 双 API 嵌入 (零本地模型): 每轨用两个 API spec 各嵌一遍 —— "
        f"MAIN(canonical 无后缀)={_SBERT_MODEL_ID} + _lg(孪生)={_SBERT_MODEL_ID_LG} "
        "(跨厂商 阿里 Qwen ⟂ OpenAI 对等互证); 输入构造 = **整篇** content_{track} "
        "(v2 2026-07-26; 与 stage 16 policy_alignment 逐字节同构 — full 轨 .strip() / "
        "ctx·ss 不 strip, 无预截断, 超长交引擎切块+token 加权池化; 故本阶段与 stage 16 "
        "共享同一批缓存条目, 正常情况下零新增付费); "
        "嵌入轴 full/ctx/ss 三路 (content_full/content_ctx/content_ss 已由 stage 13 prepend 标题恰好一次, "
        "title_col=None 关二次前置; ss=银行+金科同句轨, content_ss 缺则不产 emb_ss); "
        "embed_texts 返回单位归一向量 → (N, 4096) (Qwen) / (N, 3072) (large) float32。"
    )
    logger.info(
        "【判读】嵌入有效率越高(NaN 行越少)越好; emb_full 单位归一化 → L2 范数应≈1.0 "
        "(偏离=归一化失效); emb_ctx 全 NaN = 上游缺 content_ctx 回退 (ctx 语义陈旧度将不可用)。"
    )
    logger.info(
        "【确定性】纯 API 嵌入 (Qwen MAIN + large _lg), 经 _llm_cache.db 穿透缓存命中即 $0 "
        "逐位复现; both-or-neither parity: 某轨 MAIN 或 _lg 任一失败则该轨两列同缺 (不留单边孤儿列)。"
    )

    output_dir = CONFIG['paths']['output_dir']
    # fix(sbert-input-config-wiring, 2026-06-25): 输入文件名经 config 单一真值解析
    # (output_13_news_with_ctx → 14_news_with_ctx.parquet), 替代历史硬编码字面量, 与
    # 同链 ctx_materializer / cooccurrence_filter / herd_decay 惯例一致 (用户在 paths.yaml
    # 改 stage 14 输出名时本阶段输入随之跟随)。golden-safe: 键存在且值=默认字面量。
    # 输出 25_article_embeddings.parquet 无 config 键 (schemas None), 仍保字面量。
    src_name = CONFIG['filenames'].get('output_13_news_with_ctx', '14_news_with_ctx.parquet')

    # ── 🧭 项目 / 环境信息 (日志富集 2026-06-24; 纯日志, golden-safe) ──
    # 把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数"一次性落进日志, 便于审计/复现。
    try:
        logger.info("-" * 72)
        logger.info("  🧭 项目 / 环境信息")
        logger.info(
            "     · 阶段: 25 / 25_article_sbert (STAGES_MAIN, kind=robustness; "
            "article-level SBERT 语义指纹持久化, D 组前置)"
        )
        logger.info(
            "     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板); "
            "版本 v3.16.0 (rule-ablation-ladder)"
        )
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(
            f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
            f"LLM_OFFLINE={os.environ.get('NEWS_PROCESS_LLM_OFFLINE') or '(未设置)'}"
        )
        logger.info(
            "     · 成本/确定性: co-primary 双 API 嵌入 (Qwen MAIN + large _lg); "
            "经 _llm_cache.db 穿透缓存命中即 $0 逐位复现"
        )

        # ── 📖 方法论依据 (参考文献信息; 把核心方法的学术出处 emit 进日志) ──
        logger.info("  📖 方法论依据 (经核验注册表, 逐字照抄 APA-7 + DOI)")
        logger.info(
            "     · 标题+首段 SBERT 输入策略 (**v1 口径, 2026-07-26 起退役**; 引文保留以记载来源): "
            "Bybee, L., Kelly, B., Manela, A., & Xiu, D. "
            "(2024). Business news and business cycles. The Journal of Finance, 79(5), "
            "3105-3147. https://doi.org/10.1111/jofi.13377"
        )
        logger.info(
            "       → v1 理由『中文新闻中位 ~800 字 ≈1200 token > SBERT max_seq_len=512, "
            "取标题(≤100)+首段(≤300) 避免截断丢尾』属**本地 SentenceTransformer 时代**约束; "
            "v3.14.0 全 API 化后单条上限 8191 token, 该前提已失效 → 2026-07-26 改整篇 (v2)。"
        )
        logger.info(
            "     · 整篇不截断 + 超长分段池化 (v2 现行口径, 与 stage 16 / 27 同管线): "
            "Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using "
            "Siamese BERT-networks. In Proceedings of the 2019 Conference on Empirical "
            "Methods in Natural Language Processing and the 9th International Joint "
            "Conference on Natural Language Processing (EMNLP-IJCNLP) (pp. 3982-3992). "
            "Association for Computational Linguistics. https://doi.org/10.18653/v1/D19-1410"
        )
        logger.info(
            "       → 对比双方 (文章 / 政策锚点 / 陈旧度参照) 同管线、整文不截断, 符合 "
            "Hoberg & Phillips (2016 JPE) / Loughran & McDonald (2011 JF) 文本相似度规范。"
        )
        logger.info(
            "     · language embedding 范式 (BERT 嵌入测文本语义立场, 本阶段 SBERT 轨最新锚): "
            "Jha, M., Liu, H., & Manela. (2026). Does finance benefit society? A language "
            "embedding approach. The Review of Financial Studies, 39(5), 1227-1266. "
            "https://doi.org/10.1093/rfs/hhaf012"
        )
        logger.info(
            "       → (白话: 以 language embedding 命名方法、用 BERT 句嵌入度量文本语义立场, "
            "为 stage 25 article-level SBERT 持久化提供最新方法学锚点。)"
        )
        logger.info(
            "     · 金融域 sentence-transformer 适配 (对标 SBERT 轨金融领域微调): "
            "Jehnen, S., Villalba-Díez, J., & Ordieres-Meré, J. (2026). FinTextSim: A "
            "domain-specific sentence-transformer for extracting predictive latent topics "
            "from financial disclosures. Frontiers in Artificial Intelligence, 9, Article "
            "1752103. https://doi.org/10.3389/frai.2026.1752103"
        )
        logger.info(
            "       → (白话: 对金融披露文本微调 sentence-transformer 的领域适配范式, "
            "为本阶段在中文银行/金科语料上做文章级语义嵌入提供方法学方向参照。)"
        )
        logger.info(
            "     · 句嵌入余弦相似度与可解释性 (锚定 normalize_embeddings 后 cosine=语义对齐): "
            "Opitz, J., Moeller, L., Michail, A., Padó, S., & Clematide, S. (2025). "
            "Interpretable text embeddings and text similarity explanation: A survey. In "
            "Proceedings of the 2025 Conference on Empirical Methods in Natural Language "
            "Processing (pp. 22314-22330). Association for Computational Linguistics. "
            "https://doi.org/10.18653/v1/2025.emnlp-main.1135"
        )
        logger.info(
            "       → (白话: 句嵌入余弦相似度及其可解释性综述, 锚定本阶段 "
            "normalize_embeddings=True → 行 L2≈1 → cosine 即语义对齐的方法构念。)"
        )

        # ── ⚙ 运行配置 (config/features.yaml::embedding_api + embedding_large) ──
        logger.info("  ⚙ 运行配置 (config/features.yaml::embedding_api + embedding_large)")
        logger.info(
            f"     · 嵌入模型 (co-primary 双轨): MAIN={_SBERT_MODEL_ID} (canonical 无后缀) "
            f"+ _lg={_SBERT_MODEL_ID_LG} (跨厂商对等互证)"
        )
        logger.info(
            f"     · 输入构造: INPUT_STRATEGY={INPUT_STRATEGY} "
            + ("(整篇, 无预截断; full 轨 .strip() / ctx·ss 不 strip — 与 stage 16 逐字节同构)"
               if INPUT_STRATEGY == 'whole_text_v2'
               else f"(v1 退役口径: TITLE_CHARS={TITLE_CHARS:,d} + FIRST_PARA_CHARS={FIRST_PARA_CHARS:,d})")
            + f" | text_pipeline_version={_TEXT_PIPELINE_VERSION} | "
            f"_lg version={_TEXT_PIPELINE_VERSION_LG} "
            "(⚠ 该版本号是 spec 级共享命名空间, 严禁因本阶段输入构造变更而 bump)"
        )
        logger.info(
            "     · 嵌入轴: full/ctx/ss 三路平价 (content_full/content_ctx/content_ss "
            "由 stage 13 prepend 标题恰好一次, title_col=None 关二次前置)"
        )
        logger.info(
            f"     · 输入:   {os.path.join(output_dir, src_name)}"
        )
        logger.info(
            f"     · 输出:   {os.path.join(output_dir, '25_article_embeddings.parquet')}"
        )
        logger.info("-" * 72)
    except Exception as _e_env:  # noqa: BLE001
        logger.warning(f"  环境/方法/配置信息打印失败 (不影响处理): {_e_env}")

    src_path = os.path.join(output_dir, src_name)
    if not os.path.exists(src_path):
        logger.error(f"  上游 stage 13 未跑: {src_path}")
        sys.exit(1)

    df = pd.read_parquet(src_path)
    logger.info(f"  article-level: {len(df)} 行")

    # ── 📥 输入 schema provenance (日志富集 Round8 2026-06-29; 纯日志, golden-safe) ──
    # 在 stage 读入边界一次性落: 行×列计数 + 三轨源列 (content_full/content_ctx/content_ss)
    # 在输入 schema 中的存在性 → 审计者在读入点即可看出本输入能支持哪几条嵌入轨 (此前仅靠
    # 下游散落的 per-track warning 间接透露)。结果仅喂日志, 不回写 df / 不进任何产物。
    try:
        logger.info(f"  输入 schema: {len(df):,d} 行 × {df.shape[1]:,d} 列")
        _track_src_cols = [
            c for c in ('content_full', 'content_ctx', 'content_ss') if c in df.columns
        ]
        logger.info(
            "  输入可支持嵌入轨源列 (present): "
            f"{_track_src_cols or '(无 content_* — 回退裸 内容+标题, 仅 full 轨)'}"
        )
    except Exception as _e_io:  # noqa: BLE001
        logger.warning(f"  输入 schema provenance 打印失败 (不影响处理): {_e_io}")

    # ── 📏 输入长度的语料实证 (日志富集 Round8 2026-06-29; 2026-07-26 随 v2 改口径; 纯日志) ──
    # 原动机: docstring 曾把"中文新闻中位 ~800 字 > SBERT 512 token"当作 v1『标题+首段 300 字』
    # 截断的依据却从未在真实语料上 MEASURE, 故此处实测长度分布把断言升级为运行期度量。
    # v2 (2026-07-26 整篇) 下**不再有任何预截断** → 截断率语义消失, 改为:
    #   · 长度分布 (中位/均值/标准差/四分位 via sig4 + min/max 整数) 保留 (仍是有用的语料画像);
    #   · 「被丢尾占比」两行仅在 INPUT_STRATEGY='bybee400_v1' 时才 emit (否则是失实断言);
    #   · v2 下超长文章由引擎 split_text_for_embedding 切块+池化, 其规模由 embedding_engine
    #     的「分段: N 文本 → M 段」日志行给出 (不在此重复分词, 免 242k 篇的重复 tokenize 开销)。
    # 整块在 try/except 内, 结果仅喂 logger, 不回写 df。
    try:
        _len_src_col = 'content_full' if 'content_full' in df.columns else '内容'
        if _len_src_col in df.columns and len(df) > 0:
            _body_len = df[_len_src_col].fillna('').astype(str).str.len()
            _q = _body_len.quantile([0.25, 0.5, 0.75])
            logger.info(
                f"  📏 嵌入源正文字符长度分布 (列={_len_src_col}, n={len(df):,d}): "
                f"中位={sig4(_q.loc[0.5])} 均值={sig4(_body_len.mean())} "
                f"标准差={sig4(_body_len.std())} | Q1={sig4(_q.loc[0.25])} "
                f"Q3={sig4(_q.loc[0.75])} | min={int(_body_len.min()):,d} "
                f"max={int(_body_len.max()):,d} 字"
            )
            if INPUT_STRATEGY == 'bybee400_v1':
                _trunc_body = float((_body_len > FIRST_PARA_CHARS).mean())
                logger.info(
                    f"     · 首段截断率: {pct4(_trunc_body)} 文章正文 > FIRST_PARA_CHARS="
                    f"{FIRST_PARA_CHARS:,d} 字 (= Bybee 2024 取首段后被丢尾的文章占比; "
                    "截断越多说明『取首段而非全文』省下越多嵌入算力)"
                )
                if '标题' in df.columns:
                    _title_len = df['标题'].fillna('').astype(str).str.len()
                    _trunc_title = float((_title_len > TITLE_CHARS).mean())
                    logger.info(
                        f"     · 标题截断率: {pct4(_trunc_title)} 文章标题 > TITLE_CHARS="
                        f"{TITLE_CHARS:,d} 字 (标题中位={sig4(_title_len.median())} 字)"
                    )
                logger.info(
                    "       → (白话: 把 docstring 断言的『中文新闻中位 ~800 字』在本语料上实测一遍, "
                    "用实际字符长度分布与截断率印证『标题+首段 300 字』的取舍丢弃了多少正文 —— "
                    "让截断决策从断言变为有语料证据的运行期度量。)"
                )
            else:
                logger.info(
                    "     · 预截断: **无** (INPUT_STRATEGY=whole_text_v2, 2026-07-26 改整篇) — "
                    "全篇送嵌入, 超 8191 token 的文章由引擎 split_text_for_embedding 切块 + "
                    "token 加权池化处理, 分段规模见下方 embedding 引擎的『分段: N 文本 → M 段』行"
                )
                logger.info(
                    "       → (白话: 以前只把标题和开头 300 字交给模型, 现在整篇都交。上面这组"
                    "长度数字就是本批语料的真实体量; 极少数超长文章会被切成几段分别算再合并, "
                    "不会丢掉尾巴。)"
                )
    except Exception as _e_len:  # noqa: BLE001
        logger.warning(f"  截断决策语料实证打印失败 (不影响处理): {_e_len}")

    # ── 嵌入轴 full/ctx/ss 三路 × co-primary 双 spec (Qwen MAIN + large _lg) 编码 ──
    # v3.14.0 (2026-06-27): 弃本地 SentenceTransformer, 每轨用两个 API spec 各嵌一遍。
    # content_full / content_ctx / content_ss 均已由 stage 13 (ctx_materializer) prepend 标题【恰好一次】,
    # 故 title_col=None 关闭二次前置 (否则 ctx/ss 轨标题×2 与 full 轨不对称)。
    # full/ctx/ss 同型构造, 仅输入文本范围不同 (full=标题+全文 / ctx=标题+实体窗口 / ss=标题+银行∧金科同句窗口)。
    # 缺 content_full 时回退裸 '内容'+'标题' (旧 schema; v2 走 prepend_title(...).strip(), 标题一次)。
    # ⚠ v2 (2026-07-26): 仅 full 轨传 strip_text=True — 该不对称照抄 stage 16, 是缓存键共享的
    #    字节级前提 (改任一侧 → 该轨全体 cache miss + 付费重嵌)。
    # 🔴 both-or-neither parity (D-4a): 每轨 MAIN 或 _lg 任一 embed_texts 返回 None →
    #    该轨两列 (emb_X / emb_X_lg) 同置 None (不产, 不留单边孤儿列)。
    # 单连接复用: 一个共享 LLMCache 传入全部 ≤6 次 embed_texts (省重复 open; 产出逐位不变)。
    _shared_cache = LLMCache(CACHE_DB_PATH)

    def _embed_track_dual(content_col: str, title_col, *, strip_text: bool = False):
        """对一轨用 MAIN + _lg 两 spec 各嵌一遍; both-or-neither → 任一 None 则返 (None, None).

        `strip_text` 只在 full 轨为 True —— 照抄 stage 16 `policy_alignment` 的既有不对称
        (full 轨 `.str.strip()`, ctx/ss 轨不 strip); 该不对称是缓存键共享的**字节级前提**,
        改任一侧都会使该轨全体 cache miss 并产生付费重嵌。"""
        _m = encode_articles(
            df, content_col=content_col, spec=_MAIN_SPEC, title_col=title_col,
            strip_text=strip_text, cache=_shared_cache, log_prefix="ArticleSBERT-MAIN",
        )
        _l = encode_articles(
            df, content_col=content_col, spec=_LARGE_SPEC, title_col=title_col,
            strip_text=strip_text, cache=_shared_cache, log_prefix="ArticleSBERT-LARGE",
        )
        if _m is None or _l is None:
            logger.error(
                f"  ⚠️ 轨 {content_col} 嵌入失败 (MAIN={'None' if _m is None else 'OK'}, "
                f"_lg={'None' if _l is None else 'OK'}): both-or-neither → 该轨两列同置 None "
                "(不留单边孤儿列, 保持 co-primary 列双射契约)"
            )
            return None, None
        return _m, _l

    try:
        _has_cfull = 'content_full' in df.columns
        embs_full, embs_full_lg = _embed_track_dual(
            content_col='content_full' if _has_cfull else '内容',
            title_col=None if _has_cfull else '标题',
            strip_text=True,        # 仅 full 轨 strip (镜像 stage 16; 见 _embed_track_dual 注释)
        )
        embs_ctx, embs_ctx_lg = (
            _embed_track_dual(content_col='content_ctx', title_col=None)
            if 'content_ctx' in df.columns
            else (None, None)
        )
        # 三轨 ss (镜像 ctx): content_ss 由 stage 13 v3.9.0 恒物化 (零共现亦回退全文 body),
        # 故生产数据恒走 encode 分支; `else (None, None)` 仅为后向兼容旧 schema (无 content_ss),
        # 此时不产 emb_ss/emb_ss_lg, 下游 stage 26 的 semantic_staleness_ss(_lg) 优雅缺席。
        embs_ss, embs_ss_lg = (
            _embed_track_dual(content_col='content_ss', title_col=None)
            if 'content_ss' in df.columns
            else (None, None)
        )
    finally:
        _shared_cache.close()

    # ── 持久化 (co-primary 6 嵌入列 + 双套 provenance) ──
    out_path = os.path.join(output_dir, '25_article_embeddings.parquet')
    out_df = _build_output_frame(
        df, embs_full, embs_ctx, embs_ss,
        embs_full_lg=embs_full_lg, embs_ctx_lg=embs_ctx_lg, embs_ss_lg=embs_ss_lg,
    )
    # F22 (2026-07-27): 由裸 to_parquet 改 save_parquet_with_metadata —— 写 data_version
    # (input_hashes/config_file_hashes/resource_hashes/code_version) 使本阶段可被
    # orchestrator 的通用 --skip-unchanged 判据识别。此前无元数据 ⟹ 结构性**不可跳过**
    # ⟹ 每次 stage 40 失败重试都白跑 25(2645s)+26(6766s) ≈ 2.6h (2026-07-26/27 实弹两次)。
    # preserve_index=False 逐位等价原 to_parquet(index=False); 元数据只进 schema 不进数据列
    # → golden 只哈希数据列 → golden-safe。
    save_parquet_with_metadata(
        df=out_df,
        output_path=out_path,
        stage_name="25_article_sbert",
        config=CONFIG,
        input_files=[src_path],
        code_version=_CONST.SBERT_CODE_VERSION,
        preserve_index=False,
    )

    size_mb = os.path.getsize(out_path) / 1024 / 1024
    logger.info(f"  输出: {out_path} ({sig4(size_mb)} MB)")

    # ── 结果分析 (纯增量日志: 下列度量仅用于打印, 不回写 df / 不进任何产物;
    #    且整体在 to_parquet 写盘之后执行, 故崩溃也不丢产物。仍包 try/except 双保险:
    #    分析块抛异常不得让阶段非零退出 / 影响 golden) ──
    logger.info("-" * 72)
    logger.info("【结果分析】SBERT 嵌入持久化产出体检 (语义指纹的完整性 / 归一化 / 双轨覆盖):")
    try:
        _n_art = len(out_df)
        # both-or-neither: embs_full=None 表示 full 轨 MAIN/_lg 任一失败 → 全列联动缺席。
        _full_ok = embs_full is not None and getattr(embs_full, 'ndim', 0) == 2
        _dim_full = embs_full.shape[1] if _full_ok else -1
        logger.info(
            f"  文章篇数 = {_n_art:,d} 篇; emb_full 维度 = {_dim_full:,d} "
            f"(= 嵌入模型维度; co-primary 双轨 Qwen 4096 / large 3072 (维度不同, 余弦维度无关绝不混算)。维度与 "
            f"model_id={_SBERT_MODEL_ID} (MAIN) / {_SBERT_MODEL_ID_LG} (_lg) 应自洽 —— "
            "下游 stage 26 Faiss IndexFlatIP(dim) 已维度无关)。"
        )

        if not _full_ok:
            logger.warning(
                "  emb_full 缺席 (full 轨 MAIN 或 _lg 嵌入失败, both-or-neither 联动置 None); "
                "跳过有效率/归一化/双轨覆盖判读。"
            )
        elif _n_art == 0:
            # 空 frame 守卫: 无任何文章 → 不进比率/方向判读 (否则 _full_rate=0.0 会误报
            # "100% 行全 NaN")。走"无有效数据"分支, 后续判读整体短路 (不抛异常)。
            logger.warning(
                "  本阶段 0 篇文章 (上游 14_news_with_ctx.parquet 为空?), 无嵌入可体检; "
                "跳过有效率/归一化/双轨覆盖判读。"
            )
        else:
            # full 轨有效率: 整行全 NaN 视为编码失败 (正常 full 轨应 100% 有效)。
            # 用 (N,) 首列判定替换满 (N,4096) bool 矩阵, 全量 约1,819万 时内存/算力降一个数量级。
            _full_valid_mask = ~np.isnan(embs_full[:, 0])
            _full_valid = int(_full_valid_mask.sum())
            _full_rate = _full_valid / _n_art
            logger.info(
                f"  emb_full 有效行 = {_full_valid:,d}/{_n_art:,d} ({pct4(_full_rate)}); "
                + ("好: full 轨全覆盖 (无 NaN), 符合预期。"
                   if _full_rate >= 0.999
                   else f"⚠ 临界/坏: {pct4(1 - _full_rate)} 行 emb_full 全 NaN, full 轨编码异常须排查。")
            )

            # ctx 轨: content_ctx 缺列时 embs_ctx=None (both-or-neither 不产 emb_ctx 列)。
            if embs_ctx is None or getattr(embs_ctx, 'ndim', 0) != 2:
                logger.warning(
                    "  emb_ctx 缺席: 上游 stage 13 缺 content_ctx 列 (或 ctx 轨嵌入失败); "
                    "下游 stage 26 的 ctx 语义陈旧度 (semantic_staleness_ctx) 将不可用。"
                )
            else:
                _ctx_col0 = embs_ctx[:, 0]
                _ctx_valid_mask = ~np.isnan(_ctx_col0)
                _ctx_valid = int(_ctx_valid_mask.sum())
                _ctx_rate = _ctx_valid / _n_art
                logger.info(
                    f"  emb_ctx 有效行 = {_ctx_valid:,d}/{_n_art:,d} ({pct4(_ctx_rate)}); "
                    + ("好: ctx 轨 (实体窗口)语义指纹齐备。"
                       if _ctx_rate >= 0.999
                       else f"⚠ {pct4(1 - _ctx_rate)} 行 emb_ctx 全 NaN (部分文章无 ctx 文本)。")
                )

            # 归一化体检: normalize_embeddings=True → 每行 L2 范数应≈1.0 (随机取首个有效行)
            if _full_valid > 0:
                _first_valid_idx = int(np.argmax(_full_valid_mask))
                _l2 = float(np.linalg.norm(embs_full[_first_valid_idx]))
                logger.info(
                    f"  emb_full 单位归一化抽检 (行 {_first_valid_idx:,d}): L2 范数 = {sig4(_l2)}; "
                    + ("好: ≈1.0, normalize_embeddings 生效 (cosine 友好)。"
                       if abs(_l2 - 1.0) < 1e-3
                       else "⚠ 偏离 1.0: 归一化可能未生效, 下游 cosine 度量须复核。")
                )
            else:
                logger.warning(
                    "  emb_full 无有效行 (全 NaN 或空): 跳过归一化抽检; full 轨编码可能整体失败。"
                )

            # ss 嵌入轨上线状态 (2026-06-21 平价产出, 体检 emb_ss 有效率)
            if 'content_ss' in df.columns and embs_ss is not None and embs_ss.ndim == 2:
                _ss_col0 = embs_ss[:, 0]
                _ss_valid = int((~np.isnan(_ss_col0)).sum())
                _ss_rate = _ss_valid / max(_n_art, 1)
                logger.info(
                    f"  emb_ss 有效行 = {_ss_valid:,d}/{_n_art:,d} ({pct4(_ss_rate)}); "
                    + ("好: ss 轨 (银行+金科同句) 语义指纹齐备 (回退行其 emb_ss≡emb_full, 镜像 ctx)。"
                       if _ss_rate >= 0.999
                       else f"⚠ {pct4(1 - _ss_rate)} 行 emb_ss 全 NaN (部分文章无 content_ss)。")
                )

            # provenance 自证 (供 stage 26 检测 30a 陈旧, 防位置错位; 双套 MAIN + _lg)
            logger.info(
                f"  provenance: MAIN model_id={_SBERT_MODEL_ID} / "
                f"text_pipeline_version={_TEXT_PIPELINE_VERSION} | "
                f"_lg model_id={_SBERT_MODEL_ID_LG} / "
                f"text_pipeline_version={_TEXT_PIPELINE_VERSION_LG}; "
                "下游 stage 26 按 article_id 显式 join 并核对两套 provenance, 不匹配即报错强制重算。"
            )

            # 小样本 (早期试跑盘面 T=2) 警告
            if _n_art < 2000:
                logger.info(
                    f"  ⚠ 小样本 (仅 {_n_art:,d} 篇, 早期试跑盘面 T=2 验证语料): 上述比率/范数仅验证编码管道正确性, "
                    "全量结论以 约1,819万 文章 / T=19 实测为准。"
                )
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")
    logger.info("-" * 72)

    logger.info(f"  耗时: {sig4(time.time() - stage_start)} s")


if __name__ == '__main__':
    main()
