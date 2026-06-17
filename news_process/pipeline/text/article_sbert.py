"""news_process.pipeline.text.article_sbert — stage 30a article-level SBERT 持久化.

v3.7.0 PR #9 — D 组前置. 把 stage 30 内部计算后即丢的 article-level SBERT
embeddings 持久化, 让 D2 (staleness) / D3 (Krippendorff α)
能直接复用, 避免重复编码 (节省 ~12-15 h 计算).

学术依据
--------
Bybee, L., Kelly, B. T., Manela, A., & Xiu, D. (2024). Business news and
business cycles. The Journal of Finance, 79(5), 3105-3147.
https://doi.org/10.1111/jofi.13377
→ 标题 + 首段 300 字策略 (避免 SBERT 512-token 截断丢尾段)
  (期刊订正: 此前误标 RFS 37(3):887-936, 经 Crossref 核验为 JF 79(5);
   与 scripts/audit/LITERATURE_ANCHORS_2026-06-13.md:140 锚点对齐)

设计决策
--------
1. **SBERT 模型**: 读 ``config/features.yaml::embedding_robustness.model``
   (默认 ``shibing624/text2vec-base-chinese``, 与 stage 15 / strategic_diff t2v 轨
   真单源, 零下载 + 零 (full/ctx) 嵌入轨配置漂移; fix(omni-g-embed-05, 2026-06-11) —
   此前读不存在的 'embedding' 键恒走硬编码默认)
2. **输入策略**: 标题 + 首段 300 字 (实际新闻中位 800 字 ≈ 1200 token, SBERT
   max_seq_len=512 截断会丢失末段)
3. **嵌入轴仍 full/ctx 两路, ss 待 30a 嵌入上线** (2026-06-08 parity; legacy (full/ctx) 示例):
   full 读 content_full / ctx 读 content_ctx (两者均由 stage 13 prepend 标题【恰好一次】),
   编码时 title_col=None 关闭二次前置 → full/ctx 同型构造、标题各一次 (修 ctx 标题×2 反向
   病根); 仅输入文本范围不同 (全文 vs 实体窗口)。缺 content_full 时回退裸 '内容'+'标题'
   (走 _truncate_for_sbert Bybee 前置, 标题一次)。
   **三轨说明 (v3.9.0)**: ss SBERT embedding 孪生 (emb_ss / semantic_staleness_ss) 在
   v1 延后 (plan §④/§7.5, 最贵收益低; 30a ss 上线前 semantic_staleness_ss = NaN);
   情感轨的 full/ctx/ss 三轨在 stage 21/22/23 已平价, 此处嵌入轴仅 full/ctx (ss 待 30a 上线)。
4. **存储**: parquet (article_id, target_bank, year, emb_full[768], emb_ctx[768])
   预估 400k × 768 × 4 byte × 2 轨 = ~2.5 GB

D-0 实测项
----------
- HF cache 是否含 shibing624/text2vec-base-chinese (validate via SentenceTransformer init)
- GPU vs CPU 速度 (项目本机有 CUDA 时 < 2 h, CPU 4-6 h)

运行方式
---------
本 stage 已注册于 core/dag.py::STAGES_MAIN (无 enabled_when 条件, 随主管道
always-on 执行); 也可单独手动触发 (全量 40 万文章编码 GPU 约 4-6 h):
    python news_process/30a_article_sbert.py

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 30a_article_sbert.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**在 DAG 中的位置**: STAGES_MAIN 阶段30a, kind=robustness, timeout=21600(GPU 4-6h / CPU 12-24h)。D 组前置阶段, 上游 = stage 13(13_news_with_ctx.parquet), 下游被 stage 18(D2 staleness 的 semantic 轨)及模块 docstring 提及的 D3(Krippendorff α, 39c/39d/39f 族)复用——核心动机是把 article-level SBERT 嵌入持久化一次, 避免多处重复编码(节省约12-15h)。

**输入**: `13_news_with_ctx.parquet`(article 级; 优先用 content_full / content_ctx, 缺则回退 内容 + 标题)。

**处理步骤**:
1. `_resolve_sbert_model` 从 `config/features.yaml::embedding_robustness.model`(默认 shibing624/text2vec-base-chinese, 与 stage 15/25 t2v 轨真单源) 解析 model_id + 可选 revision(钉死 HF commit 防权重漂移)。
2. `encode_articles`: 推理前 `ensure_torch_determinism()`(seed 四源 + deterministic algorithms + cuDNN 策略, 对齐 stage 23)。文本构造 = Bybee 2024 风格'标题(≤100字, TITLE_CHARS) + 首段(≤300字, FIRST_PARA_CHARS)'(避免 SBERT 512-token 截断丢尾段)。**关键对称性**: content_full/content_ctx 已由 stage 13 prepend 标题恰好一次, 故 `title_col=None` 关闭二次前置(否则 ctx 轨标题被注入两次, 与 full 轨不对称)。`model.encode(normalize_embeddings=True, convert_to_numpy=True)` → (N,768) float32; show_progress_bar 仅交互式 TTY 显示。
3. emb_full 读 content_full(缺则裸 内容+标题, title_col='标题'), emb_ctx 读 content_ctx(缺则 np.full_like NaN)。
4. `_build_output_frame`: 组装 article_id(= stage 13 的 df.index, 供 stage 18 显式 join 对齐键)+ docid 透传 + target_bank/year/日期 + emb_full/emb_ctx(parquet 兼容的 list-of-1D-array)+ 三列 provenance(model_id / model_revision / text_pipeline_version='v2-2026-06-08-dualtrack-prepend')。

**外部依赖/确定性**: sentence-transformers + 本地 SBERT 模型(shibing624/text2vec, 与 stage 15 _t2v 同源)。**无 LLM/Embedding API、$0**(本地模型); 本地重跑须设 HF_HUB_OFFLINE=1 / TRANSFORMERS_OFFLINE=1(连不上 hf.co 但有本地缓存)。确定性由 ensure_torch_determinism + revision 钉死保证。无 _llm_cache.db 参与(本地编码每跑重算)。timeout=21600。

■ 白话说明

这一步把每篇新闻'翻译'成一串数字(768个数的向量), 让计算机能比较'两篇新闻意思像不像', 然后把这些向量存成文件备用。

打个比方: 它像一个一次性的'语义指纹采集站'——把40万篇新闻挨个扫一遍, 给每篇生成一个'意思指纹', 存进一个大文件。为了省时间和保证一致, 它只读每篇的'标题 + 开头300字'(中文新闻中位数约800字, 模型一次读不完整篇, 而开头通常已含核心信息), 而且特意保证标题只被算进去一次(否则带标题的窗口会把标题权重算重)。

为什么需要它: 后面好几个步骤都要用'语义像不像'——比如 stage 18 判断一篇新闻是不是'旧闻重印'、还有评估多个评分者一致性的步骤(D3)。如果每个步骤各自重新算一遍这些指纹, 要多花十几个小时。这一步算一次、存下来、大家共用, 是个纯粹的'性能/复用'前置, 本身不产出面板里的最终变量。

对最终面板/论文的影响: 它是间接的'地基'——它算出的语义向量喂给 stage 18 的'语义陈旧度', 进而进入稳健性检验。如果这里模型选错、标题被算重、或不同步(比如上游新闻重生了它却没重算导致向量和文章对不上号), 下游的语义相似度就会变成噪音; 代码因此特意用 article_id 严格配对并在对不上时直接报错停下, 强制重算, 防止论文用到错位的语义信号。注意它目前只算'全文'和'银行局部窗口'两条轨, 第三条'银行+金科同句'轨的语义向量暂未上线(成本高收益低), 所以面板里对应的'同句语义陈旧度'暂为空缺, 不影响其它指标。
========================================================================
"""

from __future__ import annotations

import os
import sys
import time
from typing import Optional

import numpy as np
import pandas as pd

# 路径注入: 让 ``news_process.core.*`` 在任意 cwd 下可解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config  # noqa: E402
from news_process.core.logging import setup_logging  # noqa: E402

CONFIG = load_config()
STAGE_NAME = "30a_article_sbert"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

def _resolve_sbert_model(config: dict) -> tuple[str, str | None]:
    """从 config/features.yaml::embedding_robustness 解析 (model_id, revision).

    fix(omni-g-embed-05, 2026-06-11): 此前读不存在的 'embedding' 顶级键 (features.yaml
    仅有 embedding_api / embedding_robustness 两键) → 恒走硬编码默认, "单源对齐"声称
    失实; 改 embedding_robustness.model 时 stage 30a 静默不跟随, 与 stage 15/25 t2v
    轨配置漂移。现真单源 = embedding_robustness.model (+ 可选 revision 键钉死 HF
    commit, 防上游模型权重更新静默改变全部嵌入派生测度)。
    """
    rob = (config or {}).get('embedding_robustness', {}) or {}
    model_id = rob.get('model') or 'shibing624/text2vec-base-chinese'
    revision = rob.get('revision') or None
    return model_id, revision


# 与 config/features.yaml::embedding_robustness.model 真单源对齐 (stage 15/25 t2v 同源)
_SBERT_MODEL_ID, _SBERT_REVISION = _resolve_sbert_model(CONFIG)

# 30a 输入文本构造版本 (provenance, 与 LLMCache 的 prompt_version 维度同哲学):
# v2 = 2026-06-08 dual-track parity (content_full/content_ctx 已 prepend 标题一次,
# title_col=None 关闭二次前置)。任何对输入构造/截断策略的变更必须 bump。
_TEXT_PIPELINE_VERSION = 'v2-2026-06-08-dualtrack-prepend'

# Bybee 2024 风格 "标题 + 首段 300 字" 截断
TITLE_CHARS = 100
FIRST_PARA_CHARS = 300


def _truncate_for_sbert(title: str, content: str) -> str:
    """构造 SBERT 输入: 截短标题 + 首段 300 字; 避免 512 token 截断丢尾."""
    t = (title or '')[:TITLE_CHARS].strip()
    c = (content or '')[:FIRST_PARA_CHARS].strip()
    if t and c:
        return f"{t} | {c}"
    return t or c


def encode_articles(
    df: pd.DataFrame,
    content_col: str,
    title_col: Optional[str] = '标题',
    batch_size: int = 64,
) -> np.ndarray:
    """SBERT batch 编码; 输出 (N, 768) numpy 数组.

    Args:
        df: article-level DataFrame.
        content_col: '内容' or 'content_ctx'.
        title_col: '标题' (可选, 用于 Bybee 2024 截断策略).
        batch_size: 默认 64; GPU 可上调 128/256.

    Returns:
        (N, 768) float32 embeddings.
    """
    try:
        from sentence_transformers import SentenceTransformer  # noqa: E402
    except ImportError:
        logger.error("sentence-transformers 未安装; pip install sentence-transformers")
        raise

    # fix(omni-g-embed-07, 2026-06-11): 推理前确定性硬化 (共享 helper, 对齐 stage 23
    # tone_berts V4 T1.1a — seed 四源 + deterministic algorithms + cuDNN 策略)
    from news_process.pipeline.text.embedding_engine import ensure_torch_determinism
    ensure_torch_determinism()

    logger.info(
        f"  加载 SBERT: {_SBERT_MODEL_ID}"
        + (f" @ revision={_SBERT_REVISION}" if _SBERT_REVISION else "")
    )
    # fix(omni-g-embed-05, 2026-06-11): 配置了 revision 时钉死 HF commit;
    # 未配置保持旧调用形态 (兼容旧版 sentence-transformers 无 revision kwarg)
    if _SBERT_REVISION:
        model = SentenceTransformer(_SBERT_MODEL_ID, revision=_SBERT_REVISION)
    else:
        model = SentenceTransformer(_SBERT_MODEL_ID)

    if title_col and title_col in df.columns:
        docs = [
            _truncate_for_sbert(t, c)
            for t, c in zip(df[title_col].fillna(''), df[content_col].fillna(''))
        ]
    else:
        docs = [
            (c or '')[:TITLE_CHARS + FIRST_PARA_CHARS]
            for c in df[content_col].fillna('')
        ]

    logger.info(f"  编码 {len(docs)} 篇文章, batch_size={batch_size}")
    t0 = time.time()
    embs = model.encode(
        docs,
        batch_size=batch_size,
        # 仅在交互式 (stderr 为 TTY) 时显示 tqdm 进度条; 在 run_pipeline_function
        # 子进程 (stderr 为管道) 下静默, 避免向 stderr 输出进度条噪声 (不影响编码结果)。
        show_progress_bar=sys.stderr.isatty(),
        normalize_embeddings=True,  # D2 cosine 友好 + D1 UMAP cosine metric 等价欧式
        convert_to_numpy=True,
    )
    logger.info(f"  编码完成: {time.time() - t0:.1f}s, shape={embs.shape}")
    return embs.astype(np.float32)


def _build_output_frame(
    df: pd.DataFrame, embs_full: np.ndarray, embs_ctx: np.ndarray,
) -> pd.DataFrame:
    """组装 30a 输出 frame (对齐键 + provenance + full/ctx 两路向量).

    嵌入轴仍 full/ctx 两路 (ss 待 30a 嵌入上线); legacy (full/ctx) 示例。

    fix(omni-g-embed-03, 2026-06-11): 新增 model_id / model_revision /
    text_pipeline_version provenance 列 (与 LLMCache 键维度对齐) + docid 透传 —
    供 stage 18 消费端按 article_id 显式 join 并检测 30a 陈旧 (此前消费端纯位置
    对齐, 行数恰相等的陈旧 30a 会静默整列错位)。
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
        'emb_full': list(embs_full),   # list of 1D arrays (parquet-compatible)
        'emb_ctx': list(embs_ctx),
        'model_id': _SBERT_MODEL_ID,
        'model_revision': _SBERT_REVISION or '',
        'text_pipeline_version': _TEXT_PIPELINE_VERSION,
    })
    return pd.DataFrame(out)


def main():
    stage_start = time.time()
    logger.info("=" * 72)
    logger.info(
        "阶段 30a: Article-level SBERT 嵌入持久化 "
        "(v3.7.0 PR #9; Bybee et al. 2024 JF 标题+首段策略)"
    )
    logger.info("=" * 72)
    logger.info(
        "【功能】把每篇新闻'翻译'成一串语义向量 (意思指纹, 默认 768 维, 随所配 SBERT 隐藏维), 一次性持久化成 "
        "30a_article_embeddings.parquet 备用; 是 D 组前置 (stage 18 语义陈旧度 / D3 "
        "Krippendorff α 等)的共享地基, 算一次大家共用, 省 ~12-15h 重复编码。"
    )
    logger.info(
        "【方法】SBERT 模型 = config/features.yaml::embedding_robustness.model "
        f"(实解析={_SBERT_MODEL_ID}" + (f"@{_SBERT_REVISION}" if _SBERT_REVISION else "")
        + "); 输入构造 = 标题(≤"
        f"{TITLE_CHARS}字) + 首段(≤{FIRST_PARA_CHARS}字) 防 512-token 截断丢尾; "
        "嵌入轴 full/ctx 两路 (content_full/content_ctx 已由 stage 13 prepend 标题恰好一次, "
        "title_col=None 关二次前置); model.encode(normalize_embeddings=True) "
        "→ (N, hidden_dim) float32 (默认 768)。"
    )
    logger.info(
        "【判读】嵌入有效率越高(NaN 行越少)越好; emb_full 单位归一化 → L2 范数应≈1.0 "
        "(偏离=归一化失效); emb_ctx 全 NaN = 上游缺 content_ctx 回退 (ctx 语义陈旧度将不可用)。"
    )
    logger.info(
        "【确定性】纯本地 CPU/GPU 推理, 无 LLM/Embedding API、$0; ensure_torch_determinism + "
        "revision 钉死保证逐位可复现; 无 _llm_cache.db 参与 (每跑重算)。"
    )

    output_dir = CONFIG['paths']['output_dir']
    src_path = os.path.join(output_dir, '13_news_with_ctx.parquet')
    if not os.path.exists(src_path):
        logger.error(f"  上游 stage 13 未跑: {src_path}")
        sys.exit(1)

    df = pd.read_parquet(src_path)
    logger.info(f"  article-level: {len(df)} 行")

    # ── 嵌入轴 full/ctx 两路编码 (parity 2026-06-08; ss 嵌入轨 v1 延后; legacy (full/ctx) 示例) ──
    # content_full / content_ctx 均已由 stage 13 (ctx_materializer) prepend 标题【恰好一次】。
    # 故 title_col=None 关闭 encode_articles 内 _truncate_for_sbert 的二次标题前置 —— 否则
    # ctx 轨 (读已含标题的 content_ctx) 会重复注入标题 (标题×2), 与 full 轨 (标题×1) 不对称,
    # 致 emb_full/emb_ctx 语义权重不可比 (下传 stage 18 semantic_staleness;
    # 原 stage 17 topic emb 消费端已于 2026-06-09 随 BERTopic 阶段整体移除)。
    # full/ctx 改为同型构造: 各取 content_*[:TITLE+PARA] (标题在串首恰好一次), 仅输入文本范围不同
    # (full=标题+全文 / ctx=标题+实体窗口)。与同源 content_full/content_ctx 消费者 (stage 15
    # policy_alignment / stage 27 benefit_society) 读同一含标题串、标题注入一次的口径对齐
    # (注: 各模块下游截断方式不同——sbert 取字符 [:400], stage 15 走 token 截断——此处仅指
    #  "读含标题串、标题恰好一次"这一点对齐, 非截断算法相同)。
    # 缺 content_full 时回退裸 '内容'+'标题' (旧 schema; _truncate_for_sbert 注入标题一次)。
    _has_cfull = 'content_full' in df.columns
    embs_full = encode_articles(
        df,
        content_col='content_full' if _has_cfull else '内容',
        title_col=None if _has_cfull else '标题',
    )
    embs_ctx = (
        encode_articles(df, content_col='content_ctx', title_col=None)
        if 'content_ctx' in df.columns
        else np.full_like(embs_full, np.nan)
    )

    # ss SBERT embedding twin deferred (plan §④/§7.5); semantic_staleness_ss = NaN
    # until 30a ss online.
    # 防御性优雅跳过: content_ss 即便已由 stage 13 物化 (v3.9.0 三轨), 本 stage 30a
    # 在 v1 仍**不**为其编码 emb_ss (最贵收益低)。情感轨 full/ctx/ss 在 stage 21/22/23
    # 已平价; 此处嵌入轨仅保留 full/ctx, 下游 stage 18 的 semantic_staleness_ss 因无
    # emb_ss 而恒 NaN, 直到 30a ss 上线 (届时镜像 ctx 加 emb_ss 列即可)。下方仅显式
    # 记录跳过决策, 不写任何 emb_ss / *_ss 列 (避免被审稿读成平价漏洞)。
    if 'content_ss' in df.columns:
        logger.info(
            "  [30a] content_ss 已物化但 ss SBERT 嵌入轨 v1 延后 (plan §④/§7.5) — "
            "本 stage 不编码 emb_ss; semantic_staleness_ss 在 30a ss 上线前恒 NaN。"
        )

    # ── 持久化 (fix(omni-g-embed-03, 2026-06-11): 含 provenance 列) ──
    out_path = os.path.join(output_dir, '30a_article_embeddings.parquet')
    out_df = _build_output_frame(df, embs_full, embs_ctx)
    out_df.to_parquet(out_path, index=False)

    size_mb = os.path.getsize(out_path) / 1024 / 1024
    logger.info(f"  输出: {out_path} ({size_mb:.1f} MB)")

    # ── 结果分析 (纯增量日志: 下列度量仅用于打印, 不回写 df / 不进任何产物;
    #    且整体在 to_parquet 写盘之后执行, 故崩溃也不丢产物。仍包 try/except 双保险:
    #    分析块抛异常不得让阶段非零退出 / 影响 golden) ──
    logger.info("-" * 72)
    logger.info("【结果分析】SBERT 嵌入持久化产出体检 (语义指纹的完整性 / 归一化 / 双轨覆盖):")
    try:
        _n_art = len(out_df)
        _dim_full = embs_full.shape[1] if embs_full.ndim == 2 else -1
        logger.info(
            f"  文章篇数 = {_n_art} 篇; emb_full 维度 = {_dim_full} "
            f"(= 所配 SBERT 隐藏维; 默认 shibing624/text2vec-base-chinese=768。维度与 "
            f"model_id={_SBERT_MODEL_ID} 应自洽 —— 若换稳健性模型须同步确认下游 stage 18 "
            "Faiss/语义陈旧度的维度假设)。"
        )

        if _n_art == 0:
            # 空 frame 守卫: 无任何文章 → 不进比率/方向判读 (否则 _full_rate=0.0 会误报
            # "100% 行全 NaN")。走"无有效数据"分支, 后续判读整体短路 (不抛异常)。
            logger.warning(
                "  本阶段 0 篇文章 (上游 13_news_with_ctx.parquet 为空?), 无嵌入可体检; "
                "跳过有效率/归一化/双轨覆盖判读。"
            )
        else:
            # full 轨有效率: 整行全 NaN 视为编码失败 (正常 full 轨应 100% 有效, 无回退 NaN 路径)。
            # 性能: 唯一 NaN 路径是整数组 np.full_like(.., nan) 回退 → 行级全 NaN ⟺ 首列 NaN,
            # 故用 (N,) 首列判定替换满 (N,768) bool 矩阵, 全量 17M 时内存/算力降一个数量级。
            _full_valid_mask = (
                ~np.isnan(embs_full[:, 0])
                if embs_full.ndim == 2
                else np.zeros(0, dtype=bool)
            )
            _full_valid = int(_full_valid_mask.sum())
            _full_rate = _full_valid / _n_art
            logger.info(
                f"  emb_full 有效行 = {_full_valid}/{_n_art} ({_full_rate:.1%}); "
                + ("好: full 轨全覆盖 (无 NaN), 符合预期。"
                   if _full_rate >= 0.999
                   else f"⚠ 临界/坏: {(1 - _full_rate):.1%} 行 emb_full 全 NaN, full 轨编码异常须排查。")
            )

            # ctx 轨: 上游缺 content_ctx 时 embs_ctx = np.full_like(.., nan) → 全 NaN 回退。
            # 同 full 轨, 用 (N,) 首列判定替换满矩阵 isnan (唯一 NaN 路径是整数组级回退)。
            _ctx_col0 = embs_ctx[:, 0] if embs_ctx.ndim == 2 else embs_ctx
            _ctx_all_nan = bool(np.isnan(_ctx_col0).all())
            if _ctx_all_nan:
                logger.warning(
                    "  emb_ctx 全 NaN: 上游 stage 13 缺 content_ctx 列, ctx 轨已优雅回退占位; "
                    "下游 stage 18 的 ctx 语义陈旧度 (semantic_staleness_ctx) 将不可用。"
                )
            else:
                _ctx_valid_mask = ~np.isnan(_ctx_col0)
                _ctx_valid = int(_ctx_valid_mask.sum())
                _ctx_rate = _ctx_valid / _n_art
                logger.info(
                    f"  emb_ctx 有效行 = {_ctx_valid}/{_n_art} ({_ctx_rate:.1%}); "
                    + ("好: ctx 轨 (实体窗口)语义指纹齐备。"
                       if _ctx_rate >= 0.999
                       else f"⚠ {(1 - _ctx_rate):.1%} 行 emb_ctx 全 NaN (部分文章无 ctx 文本)。")
                )

            # 归一化体检: normalize_embeddings=True → 每行 L2 范数应≈1.0 (随机取首个有效行)
            if _full_valid > 0:
                _first_valid_idx = int(np.argmax(_full_valid_mask))
                _l2 = float(np.linalg.norm(embs_full[_first_valid_idx]))
                logger.info(
                    f"  emb_full 单位归一化抽检 (行 {_first_valid_idx}): L2 范数 = {_l2:.4f}; "
                    + ("好: ≈1.0, normalize_embeddings 生效 (cosine 友好)。"
                       if abs(_l2 - 1.0) < 1e-3
                       else "⚠ 偏离 1.0: 归一化可能未生效, 下游 cosine 度量须复核。")
                )
            else:
                logger.warning(
                    "  emb_full 无有效行 (全 NaN 或空): 跳过归一化抽检; full 轨编码可能整体失败。"
                )

            # ss 嵌入轨上线状态 (v1 延后, 信息性记录)
            if 'content_ss' in df.columns:
                logger.info(
                    "  ss 嵌入轨: content_ss 已物化但 emb_ss 在 v1 延后 (plan §④/§7.5, 最贵收益低); "
                    "semantic_staleness_ss 在 30a ss 上线前恒 NaN (预期行为, 非缺陷)。"
                )

            # provenance 自证 (供 stage 18 检测 30a 陈旧, 防位置错位)
            logger.info(
                f"  provenance: model_id={_SBERT_MODEL_ID} / "
                f"model_revision={_SBERT_REVISION or '(未钉死)'} / "
                f"text_pipeline_version={_TEXT_PIPELINE_VERSION}; "
                "下游 stage 18 按 article_id 显式 join 并核对这三列, 不匹配即报错强制重算 (防错位语义信号)。"
            )

            # 小样本 (盘面 T=2) 警告
            if _n_art < 2000:
                logger.info(
                    f"  ⚠ 小样本 (仅 {_n_art} 篇, 盘面 T=2 验证语料): 上述比率/范数仅验证编码管道正确性, "
                    "全量结论以 17M 文章 / T=18 实测为准。"
                )
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")
    logger.info("-" * 72)

    logger.info(f"  耗时: {time.time() - stage_start:.1f} s")


if __name__ == '__main__':
    main()
