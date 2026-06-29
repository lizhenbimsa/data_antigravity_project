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
     using Siamese BERT-networks. EMNLP, 3980-3990.
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
  benefit_mean_full/ctx/ss:      态度均值 ∈ [-1, 1]
  benefit_std_full/ctx/ss:       态度离散度 ∈ [0, 1] (单观测 bank-year 为 NaN,
                              fix(omni-g-benefit-05): 不再 fillna(0) — '只有 1 篇报道'
                              与 '多篇完全一致' 在统计上不可区分, 与核心 tone std 族对齐)
  benefit_pos_frac_full/ctx/ss:  正态度文章占比 ∈ [0, 1]
  benefit_neg_frac_full/ctx/ss:  负态度文章占比 ∈ [0, 1]
  (上述 4 指标 × full/ctx/ss 三轨另各有 _lg co-primary twin 列:
   benefit_mean_lg_full/ctx/ss 等; MAIN=Qwen/Qwen3-Embedding-8B API / LARGE=text-embedding-3-large API,
   共 24 列; v3.14.0 已移除本地 _t2v/_bge 稳健轨, 仅余双 API 模型)
  ss 轨 (银行+金科同句, content_ss): 仅取"同句内同时含 目标银行∧金科词"的句 ±N 句窗,
   回退=无共现→镜像 ctx 回退全文 body (ss_is_fallback=True); 与 full/ctx 并列第三主轨。

pos/neg_frac 阈值中心 (KNOWN-OPEN① 修复, fix(omni-g-benefit, 2026-06-11)):
  median-center 不再每次 run 现算 — 首跑以全样本投影 pooled median 计算并持久化到
  data/processed/_benefit_center_sidecar.json, 后续 run 读冻结值 (跨 run 可比;
  披露: 冻结值仍是首跑 in-sample median, P(>center)≈0.5 仅对首跑语料成立)。

审计链路落盘 (fix(omni-g-benefit-01, 2026-06-11)):
  cache_embeddings=true 时落盘全长文章嵌入 27_benefit_embeddings{_lg}_{full,ctx,ss}.npy
  + 方向向量 27_benefit_direction{_lg}.npy (各带 .sidecar.json: model_id/n_rows/dim),
  供 27c alt-anchor / placebo 审计链路同嵌入空间消费。
============================================================================
"""

import json
import os
import platform
import sys
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd

# Phase 5c-1: 注入项目根, 让 ``news_process.core.*`` 在包模式下可解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.pipeline.text import embedding_engine as _eng

# v3.7.0 (DC3 + C1 + M13 修复): LLM raw response archive 集成 (V4 F-P2.1 critical)
# R1-R5 audit fix A5 (2026-05-27): V4 F-P2.1 仅承诺 stage 21 (tone_llms) + stage 48
# (llm_peer_iv) 接入, 此 import 是 stage 27 embedding (Jha et al. 2026) 的
# **前瞻性留位**, 当前 embedding 路径走本地 model 缓存或 OpenAI embedding API
# 已写 LLMCache (cache 即 reproducibility ledger), 无独立 archive_record 调用.
# 保留 import 维持模块层接口稳定; 未来若 embedding 切换为 LLM-generated 双极锚点
# (vs 当前固定 anchor) 再补 archive_record(...) 调用.
try:
    from news_process.pipeline.llm_archive import (
        archive_record as _llm_archive_record,  # noqa: F401  # TODO: stage 27 embedding archive
    )
    from news_process.pipeline.llm_archive.archive import _get_default_archive as _get_archive  # noqa: F401
    _LLM_ARCHIVE_AVAILABLE = True
except ImportError as _archive_import_exc:
    _llm_archive_record = None
    _get_archive = None
    _LLM_ARCHIVE_AVAILABLE = False
    import logging as _logging_for_archive_error
    _logging_for_archive_error.getLogger(__name__).warning(
        "v3.7.0: llm_archive 不可用 (%s). Stage 27 embedding 仍依赖 LLMCache "
        "作为 reproducibility ledger (cache hit/miss 完整记录).",
        _archive_import_exc,
    )

# ============================================================================
# 1. 全局配置和初始化  (Phase 2a: 取代旧的 importlib 反射)
# ============================================================================
from news_process.core.logging import pct4, sig4  # noqa: E402  # 4-sig-fig 日志渲染单一事实源
from news_process.pipeline.panel.encode import CONFIG, FILENAMES, OUTPUT_DIR, logger  # noqa: E402

STAGE_NAME = "27_fintech_benefit_society"

# LLM API 配置（复用 tone_llm_processing 节中的 base_url 和 api_key）
LLM_CONFIG = CONFIG.get('tone_llm_processing', {})
EMBEDDING_CONFIG = CONFIG.get('embedding_api', {})           # MAIN spec → canonical 列 (Qwen)
# v3.14.0 双 API 模型嵌入: LARGE twin (text-embedding-3-large, API) → '_lg' 列。
# co-primary 活动轨 (与 MAIN 并列, 非休眠): config/features.yaml 已激活 embedding_large 块。
# (v3.14.0 已整体移除本地稳健轨 _t2v(text2vec) / _bge(bge-m3); 仅余双 API 模型)
_LARGE_SPEC = CONFIG.get('embedding_large', {})

# 模块专属配置
_BENEFIT_CFG = CONFIG.get('benefit_society', {})
_MAX_TOKENS_PER_INPUT = _BENEFIT_CFG.get('max_tokens_per_input', 8191)
_MAX_TOKENS_PER_REQUEST = _BENEFIT_CFG.get('max_tokens_per_request', 250_000)
_CACHE_EMBEDDINGS = _BENEFIT_CFG.get('cache_embeddings', True)
_ANCHOR_SIGN_TOL = float(_BENEFIT_CFG.get('anchor_sign_tolerance', 0.03))
_ANCHOR_PAIR_MIN_MARGIN = float(_BENEFIT_CFG.get('anchor_pair_min_margin', 0.02))

# 嵌入重试已集中在 embedding_engine (2026-06-26 全项目统一固定 10s 间隔); 本模块经
# _eng.embed_texts 委托嵌入, 不再自带重试常量 (原 RETRY_DELAY/MAX_RETRY_DELAY 为死常量)。
CACHE_DB_PATH = CONFIG['paths'].get('llm_cache_db', os.path.join(CONFIG['paths']['output_dir'], '_llm_cache.db'))

# tiktoken 工具 — 统一复用 core/text/token_utils (下方 _count_tokens 等为薄包装)


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
    """精确计算文本的 token 数 (委托给 core.text.token_utils)。"""
    from news_process.core.text.token_utils import count_tokens
    return count_tokens(text)


def _truncate_to_max_tokens(text: str, max_tokens: int = _MAX_TOKENS_PER_INPUT) -> str:
    """将文本精确截断至不超过 max_tokens 个 token (委托给 core.text.token_utils)。"""
    from news_process.core.text.token_utils import truncate_to_max_tokens
    return truncate_to_max_tokens(text, max_tokens)


def _get_embeddings(texts: list[str],
                    token_counts: list[int] = None,
                    *,
                    spec: dict | None = None,
                    log_prefix: str = "Embedding") -> np.ndarray:
    """文本 → Embedding 向量, 委托给统一引擎 _eng.embed_texts。

    spec 决定模型与路径 (MAIN=Qwen/Qwen3-Embedding-8B / LARGE=text-embedding-3-large, 均 API)。
    token_counts 已不再需要 (引擎内部按 token 自行分批), 保留参数仅为签名兼容。

    P0-1 (API-fatal 守卫): 仅对 co-primary twin `_lg` (API 且**非** MAIN canonical) 的
    致命错 (鉴权/网络/配额/离线闸) 兜底降级 None + logger.warning, 使该 twin 仅跳过
    (其轨列 NaN), 不连带炸 stage。**MAIN canonical** (EMBEDDING_CONFIG) 一律 fail-fast
    (走裸路径, 异常照常上抛) — 既保留 MAIN 既有失败语义, 又不吞 embedding_engine 离线
    确定性闸 RuntimeError (防主结果列被静默置 NaN bless 进 golden)。对齐
    policy_alignment/policy_similarity 范本。
    ⚠ 双 API 模型 (v3.14.0) 下 _lg 单边降级会留单边孤儿列 (MAIN 列在但 _lg 列全 NaN);
    both-or-neither 同生同灭由 compute_benefit_society_panel 的 spec 循环**之后**的
    family-level parity 守卫 (§6.5b, code-review P1-B) 统一处理。本函数保持单 spec 语义不变。
    """
    _spec = spec or EMBEDDING_CONFIG
    # 守卫范围铁律: MAIN canonical (EMBEDDING_CONFIG) 走 fail-fast 裸路径 (保留 MAIN 既有失败
    # 语义 + 不吞 embedding_engine 离线确定性闸 RuntimeError, 防主结果列被静默置 NaN bless 进
    # golden); 仅 _lg twin (API 且非 MAIN) 进下方 try/except 软降级。spec_uses_local 在
    # v3.14.0 双 API 模型下恒 False (已移除本地 _t2v/_bge), 保留仅为防御 (未来本地 spec 复用)。
    if _eng.spec_uses_local(_spec) or _spec is EMBEDDING_CONFIG:
        # MAIN canonical (或未来本地 spec): 不兜底 (fail-fast)。
        return _eng.embed_texts(
            texts,
            _spec,
            cache_db_path=CACHE_DB_PATH,
            log_prefix=log_prefix,
        )
    try:
        return _eng.embed_texts(
            texts,
            _spec,
            cache_db_path=CACHE_DB_PATH,
            log_prefix=log_prefix,
        )
    except Exception as exc:  # noqa: BLE001 — 仅 _lg twin API 致命错降级, 防连带炸 stage
        logger.warning(
            f"    [API spec] {log_prefix} 嵌入失败 (model={_eng.spec_model(_spec)}), "
            f"该 spec 降级为 None (其轨列 NaN, 不影响其他 spec): {exc!r}"
        )
        return None


# ============================================================================
# 4. 方向向量计算
# ============================================================================

def _compute_direction_vector(spec: dict | None = None) -> np.ndarray | None:
    _spec = spec or EMBEDDING_CONFIG
    all_anchors = POSITIVE_ANCHORS + NEGATIVE_ANCHORS
    token_counts = [_count_tokens(s) for s in all_anchors]
    # P0-1 (API-fatal 守卫): _get_embeddings 已对 API spec 兜底为 None; 此处再包一层
    # 防御性 except (仅 API spec 兜底, local 不变) 以防未来绕过 _get_embeddings 直调引擎。
    try:
        emb = _get_embeddings(
            all_anchors,
            token_counts,
            spec=_spec,
            log_prefix="Benefit anchor embedding",
        )
    except Exception as exc:  # noqa: BLE001
        if _eng.spec_uses_local(_spec) or _spec is EMBEDDING_CONFIG:
            raise  # MAIN canonical (或未来本地 spec): fail-fast, 异常照常上抛 (不吞离线闸)
        logger.warning(
            f"    [API spec] 锚点方向向量嵌入失败 (model={_eng.spec_model(_spec)}), "
            f"该 spec 跳过 (返回 None): {exc!r}"
        )
        return None
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
    emb_norms = np.linalg.norm(emb, axis=1)
    safe_norms = np.where(emb_norms < 1e-10, 1.0, emb_norms)
    anchor_scores = (emb @ dir_norm) / safe_norms
    pos_scores = anchor_scores[:n_pos]
    neg_scores = anchor_scores[n_pos:]

    for i, (pos_sentence, neg_sentence) in enumerate(
        zip(POSITIVE_ANCHORS, NEGATIVE_ANCHORS)
    ):
        if emb_norms[i] < 1e-10 or emb_norms[n_pos + i] < 1e-10:
            logger.warning(f"    锚点对 #{i+1} embedding 范数过小, 请检查锚句配置")
            continue

        pos_score = float(pos_scores[i])
        neg_score = float(neg_scores[i])
        margin = pos_score - neg_score
        if margin <= _ANCHOR_PAIR_MIN_MARGIN:
            logger.warning(
                f"    锚点对 #{i+1} 正负间隔异常 "
                f"(pos={sig4(pos_score)}, neg={sig4(neg_score)}, margin={sig4(margin)}): "
                f"{pos_sentence[:18]}... / {neg_sentence[:18]}..."
            )
        elif pos_score <= -_ANCHOR_SIGN_TOL:
            logger.warning(
                f"    正极句 #{i+1} 明显投影为负 ({sig4(pos_score)}): "
                f"{pos_sentence[:20]}..."
            )
        elif neg_score >= _ANCHOR_SIGN_TOL:
            logger.warning(
                f"    负极句 #{i+1} 明显投影为正 ({sig4(neg_score)}): "
                f"{neg_sentence[:20]}..."
            )
        elif pos_score <= 0 or neg_score >= 0:
            logger.info(
                f"    锚点对 #{i+1} 存在近零边界符号 "
                f"(pos={sig4(pos_score)}, neg={sig4(neg_score)}, margin={sig4(margin)}), "
                "正负间隔正常"
            )

    # 结果解读: 方向向量范数 = 正负极语义可分性 (Jha et al. 2026, RFS §1.3.2; 双极锚点
    # 差分 p=mean(pos)−mean(neg))。范数越大 → 正负极锚点在嵌入空间分得越开 → 投影轴越锐利。
    try:
        _n_pairs = len(POSITIVE_ANCHORS)
        _mean_margin = float(np.mean(pos_scores - neg_scores)) if _n_pairs else float('nan')
        _min_margin = float(np.min(pos_scores - neg_scores)) if _n_pairs else float('nan')
        _verdict = (
            "✅ 锚点轴锐利" if (np.isfinite(_min_margin) and _min_margin > _ANCHOR_PAIR_MIN_MARGIN)
            else "⚠ 存在弱可分锚点对 (见上方告警)"
        )
        logger.info(
            f"    方向向量: 维度 {direction.shape}, ||p|| = {sig4(dir_norm_val)} | "
            f"锚点对均值间隔={sig4(_mean_margin)} / 最小间隔={sig4(_min_margin)} "
            f"(阈值>{sig4(_ANCHOR_PAIR_MIN_MARGIN)}) → {_verdict}"
        )
    except Exception as _ml_exc:  # noqa: BLE001
        logger.warning(f"    方向向量范数: 维度 {direction.shape}, ||p|| = {sig4(dir_norm_val)} "
                       f"(间隔解读跳过: {_ml_exc!r})")
    return direction


# ============================================================================
# 5. 文章级投影计算
# ============================================================================

def _persist_article_embeddings(cache_path: str, emb: np.ndarray,
                                valid_mask: np.ndarray, *, spec: dict) -> None:
    """fix(omni-g-benefit-01, 2026-06-11): 落盘全长文章嵌入 .npy + .sidecar.json。

    行序与 df_exploded 一一对应 (空文本行 = NaN), 供 27c alt-anchor/placebo
    审计链路对齐消费; sidecar 记录 model_id / n_rows / dim, 消费端据此做
    嵌入空间一致性断言 (2026-05-29 主轨换模后维度错配的根因防线)。
    落盘失败仅 warning, 不阻塞主流程 (主面板不依赖 .npy)。
    """
    try:
        full = np.full((len(valid_mask), emb.shape[1]), np.nan, dtype=np.float32)
        full[valid_mask] = np.asarray(emb, dtype=np.float32)
        np.save(cache_path, full)
        sidecar = {
            'schema_version': '1.0',
            'producer': 'stage 27 benefit_society._project_texts',
            'model_id': _eng.spec_model(spec),
            'text_pipeline_version': _eng.spec_version(spec),
            'n_rows': int(len(valid_mask)),
            'n_valid': int(valid_mask.sum()),
            'dim': int(emb.shape[1]),
            'dtype': 'float32',
            'nan_rows': '空文本行 (与 df_exploded 行序一一对应)',
            'created_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        }
        with open(f"{cache_path}.sidecar.json", 'w', encoding='utf-8') as f:
            json.dump(sidecar, f, ensure_ascii=False, indent=2)
        logger.info(f"    嵌入落盘: {os.path.basename(str(cache_path))} "
                    f"({sidecar['n_rows']}×{sidecar['dim']}, valid={sidecar['n_valid']})")
    except OSError as exc:
        logger.warning(f"    嵌入 .npy 落盘失败 (不阻塞主流程): {exc!r}")


def _persist_direction_vector(direction: np.ndarray, suffix: str,
                              *, spec: dict) -> None:
    """fix(omni-g-benefit-01, 2026-06-11): 落盘方向向量 p = mean(pos) − mean(neg)。

    27c placebo 链路的 ``--main-direction-npy`` 此前无任何产出方 — 现由 stage 27
    在每个 spec 计算方向向量后写 ``27_benefit_direction{suffix}.npy`` + sidecar。
    注意: 此向量是**未归一**的原始差分 (消费端 project 前自行归一), sidecar 中
    ``unit_norm: false`` 显式披露。
    """
    path = os.path.join(OUTPUT_DIR, f'27_benefit_direction{suffix}.npy')
    try:
        np.save(path, np.asarray(direction, dtype=np.float32))
        sidecar = {
            'schema_version': '1.0',
            'producer': 'stage 27 benefit_society._compute_direction_vector',
            'model_id': _eng.spec_model(spec),
            'text_pipeline_version': _eng.spec_version(spec),
            'dim': int(np.asarray(direction).shape[0]),
            'n_anchor_pairs': len(POSITIVE_ANCHORS),
            'unit_norm': False,
            'created_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        }
        with open(f"{path}.sidecar.json", 'w', encoding='utf-8') as f:
            json.dump(sidecar, f, ensure_ascii=False, indent=2)
        logger.info(f"    方向向量落盘: 27_benefit_direction{suffix}.npy "
                    f"(dim={sidecar['dim']})")
    except OSError as exc:
        logger.warning(f"    方向向量 .npy 落盘失败 (不阻塞主流程): {exc!r}")


def _project_texts(texts: list[str], direction: np.ndarray,
                   cache_path: str | None = None,
                   *, spec: dict | None = None) -> np.ndarray:
    """文章级投影 a_j = cos(s_j, p) (Jha et al. 2026, RFS §1.3.2 Eq. 1)。

    接收 **全量** 文本列表 (与 df_exploded 行序一致, 允许空文本); 空文本不送
    引擎, 对应得分为 NaN。返回与 texts 等长的得分向量。

    fix(omni-g-benefit-04, 2026-06-11): 移除 8191-token 预截断 — 统一引擎
    embed_texts 自带朴素分段 (naive chunking) + token 加权 mean pooling (与 stage 25
    strategic_diff 同口径), 长文尾部不再被静默丢弃 (兑现 'Full 轨: 完整语义
    信号' 声称)。≤8191 token 文本的缓存键不变 (旧截断恒等); 超长文本首块与旧
    截断文本字节一致 (cache hit), 仅尾部块为新键 → 嵌入重算 deferred 到下次
    生产 run。

    fix(omni-g-benefit-01, 2026-06-11): cache_path 参数真实生效 (此前函数体
    完全忽略, _CACHE_EMBEDDINGS 死读, 27c 链路输入断供) — cache_embeddings=true
    时经 _persist_article_embeddings 落盘全长嵌入 .npy + sidecar。
    """
    texts = ['' if t is None else str(t) for t in texts]
    valid_mask = np.array([bool(t.strip()) for t in texts], dtype=bool)
    scores = np.full(len(texts), np.nan)
    valid_texts = [t for t, m in zip(texts, valid_mask) if m]
    if not valid_texts:
        return scores

    _spec = spec or EMBEDDING_CONFIG
    # P0-1 (API-fatal 守卫): _get_embeddings 已对 API spec 兜底为 None; 此处再包一层
    # 防御性 except (仅 API spec 兜底, local 不变) 以防未来绕过 _get_embeddings 直调引擎。
    try:
        emb = _get_embeddings(
            valid_texts,
            None,
            spec=_spec,
            log_prefix="Benefit text embedding",
        )
    except Exception as exc:  # noqa: BLE001
        if _eng.spec_uses_local(_spec) or _spec is EMBEDDING_CONFIG:
            raise  # MAIN canonical (或未来本地 spec): fail-fast, 异常照常上抛 (不吞离线闸)
        logger.warning(
            f"    [API spec] 文章文本嵌入失败 (model={_eng.spec_model(_spec)}), "
            f"该 spec 跳过 (返回全 NaN 得分): {exc!r}"
        )
        return scores

    if emb is None or len(emb) == 0:
        return scores

    if cache_path and _CACHE_EMBEDDINGS:
        _persist_article_embeddings(cache_path, emb, valid_mask,
                                    spec=_spec)

    dir_norm = direction / np.linalg.norm(direction)
    norms = np.linalg.norm(emb, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    scores[valid_mask] = (emb @ dir_norm) / norms.ravel()
    return scores


# ============================================================================
# 5b. pos/neg_frac 阈值中心 — 冻结 sidecar (KNOWN-OPEN① 修复)
# ============================================================================

_CENTER_SIDECAR_FILENAME = '_benefit_center_sidecar.json'

# 纵深防御 (2026-06-11 实测教训): 同分支并发 agent 曾用 4 篇 toy 数据跑
# compute_benefit_society_panel (未重定向 OUTPUT_DIR 的旧版测试) → toy median
# 被冻结进真实 data/processed sidecar。样本量低于此阈值时只现算不持久化,
# 防 toy/试跑数据被冻结为生产阈值 (测试同时已全部重定向 OUTPUT_DIR)。
_CENTER_MIN_N_TO_FREEZE = 50


def _get_frozen_center(score_key: str, scores: pd.Series, model_id: str) -> float:
    """pos/neg_frac 阈值中心的单一事实源 (冻结 sidecar)。

    fix(omni-g-benefit KNOWN-OPEN①, 2026-06-11): 此前 _center 每次 run 用当期
    语料 pooled median 现算 → 语料增量会平移全历史 pos/neg_frac (跨 run 不可比,
    纯 in-sample 阈值)。现改为:
      - 首跑: 以当期全样本投影 median 计算, 持久化到
        ``data/processed/_benefit_center_sidecar.json`` (键 = score 列名,
        如 ``benefit_score_full`` / ``benefit_score_lg_ctx``);
      - 后续 run: 直接读冻结值, 不随语料漂移;
      - sidecar 记录 model_id, 与当前 spec 不匹配 → fail-loud (嵌入模型换代须
        显式删除过期条目重冻结, 防跨嵌入空间阈值误用)。
    披露: 冻结值本质仍是首跑 in-sample median — P(>center)≈0.5 仅对首跑语料
    成立; benefit_mean 连续主测度不经此中心化, 不受影响。
    """
    sidecar_path = os.path.join(OUTPUT_DIR, _CENTER_SIDECAR_FILENAME)
    record: dict = {}
    if os.path.exists(sidecar_path):
        try:
            with open(sidecar_path, encoding='utf-8') as f:
                record = json.load(f)
            if not isinstance(record, dict):
                record = {}
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(f"    center sidecar 读取失败, 按首跑重建: {exc!r}")
            record = {}

    entry = record.get(score_key)
    if (isinstance(entry, dict)
            and isinstance(entry.get('center'), (int, float))
            and np.isfinite(entry['center'])):
        frozen_model = entry.get('model_id')
        if frozen_model is not None and frozen_model != model_id:
            raise ValueError(
                f"benefit center sidecar 条目 {score_key!r} 冻结自 model="
                f"{frozen_model!r}, 当前 spec model={model_id!r} — 嵌入模型换代须"
                f"删除 {sidecar_path} 中该条目后重冻结 (防跨嵌入空间阈值误用)"
            )
        logger.info(f"    {score_key}: 使用冻结 center={sig4(entry['center'])} (sidecar)")
        return float(entry['center'])

    center = float(scores.dropna().median()) if scores.notna().any() else float('nan')
    if not np.isfinite(center):
        logger.warning(f"    {score_key}: 无有效投影得分, center 回退 0.0 (不冻结)")
        return 0.0
    n_scores = int(scores.notna().sum())
    if n_scores < _CENTER_MIN_N_TO_FREEZE:
        logger.warning(
            f"    {score_key}: 有效得分仅 {n_scores:,d} 篇 < {_CENTER_MIN_N_TO_FREEZE}, "
            f"本次使用现算 center={sig4(center)} 但**不冻结** (防 toy/试跑数据持久化)"
        )
        return center
    record[score_key] = {
        'center': center,
        'model_id': model_id,
        'method': 'pooled-median (首跑 in-sample, 冻结)',
        'n_scores': n_scores,
        'frozen_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
    }
    try:
        with open(sidecar_path, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        logger.info(f"    {score_key}: 首跑冻结 center={sig4(center)} "
                    f"→ {_CENTER_SIDECAR_FILENAME}")
    except OSError as exc:
        logger.warning(f"    center sidecar 写入失败 (本次仍用 {sig4(center)}): {exc!r}")
    return center

# ============================================================================
# 6. Bank-Year 聚合 + 面板合并（核心入口函数）
# ============================================================================

def _log_benefit_env_config_methods(panel: pd.DataFrame,
                                     df_exploded: pd.DataFrame) -> None:
    """子步骤 banner: 环境/配置/方法论引文 (日志富集, 2026-06-24, golden-safe)。

    benefit_society 是 panel runner (步骤 7h-benefit) 调用的库函数, 共用
    panel-build 日志, 无独立 main()。按 playbook §0.5 (called-by-runner helper):
    在被调函数起始处打一个**子步骤 banner** —— ① 环境指纹 + ② 输入/输出 +
    ③ 运行配置 + ④ 方法论依据 (含 DOI, 逐字取自经核验注册表)。纯日志, 不改任何
    写盘值 / schema / 控制流 (golden-safe)。
    """
    try:
        _main_model = _eng.spec_model(EMBEDDING_CONFIG)
        _lg_model = _eng.spec_model(_LARGE_SPEC) if _LARGE_SPEC else '(未配置)'
        _offline = os.environ.get('NEWS_PROCESS_LLM_OFFLINE', '') in ('1', 'true', 'True')

        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 子步骤: 7h-benefit ({STAGE_NAME}; runner 调用的库函数, 无独立 main)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板)")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    f"LLM_OFFLINE={'是' if _offline else '否'}")
        logger.info("     · 成本/确定性: 嵌入 API 缓存命中=$0; 冷缓存=付费嵌入调用 "
                    "(MAIN Qwen + _lg text-embedding-3-large 双 API 模型)")

        logger.info("  📂 输入 / 输出")
        logger.info(f"     · 输入 panel: {len(panel):,d} 行 × {panel.shape[1]:,d} 列 "
                    f"(bank-year 面板)")
        logger.info(f"     · 输入 df_exploded: {len(df_exploded):,d} 行 (文章-银行级)")
        logger.info(f"     · 嵌入缓存 DB: {CACHE_DB_PATH}")
        logger.info(f"     · 嵌入落盘目录: {OUTPUT_DIR} "
                    f"(27_benefit_embeddings*.npy / 27_benefit_direction*.npy)")
        logger.info(f"     · center sidecar: "
                    f"{os.path.join(OUTPUT_DIR, _CENTER_SIDECAR_FILENAME)}")

        logger.info("  ⚙ 运行配置 (config::benefit_society / embedding_api / embedding_large)")
        logger.info(f"     · MAIN 嵌入模型: {_main_model} (canonical 列) | "
                    f"LARGE co-primary: {_lg_model} (_lg 列)")
        logger.info(f"     · 锚点对数: {len(POSITIVE_ANCHORS):,d} (正/负极严格对偶, "
                    "single-word-change)")
        logger.info(f"     · 锚点符号容差 anchor_sign_tolerance={sig4(_ANCHOR_SIGN_TOL)} | "
                    f"锚点对最小间隔 anchor_pair_min_margin={sig4(_ANCHOR_PAIR_MIN_MARGIN)}")
        logger.info(f"     · max_tokens_per_input={_MAX_TOKENS_PER_INPUT:,d} | "
                    f"max_tokens_per_request={_MAX_TOKENS_PER_REQUEST:,d} | "
                    f"cache_embeddings={_CACHE_EMBEDDINGS}")
        logger.info(f"     · center 冻结最小样本 _CENTER_MIN_N_TO_FREEZE={_CENTER_MIN_N_TO_FREEZE:,d} | "
                    "三轨 = full / ctx / ss")

        logger.info("  📖 方法论依据 (参考文献逐字取自经核验注册表)")
        logger.info("     · 双极锚点连续投影 a_j = cos(s_j, p), p = mean(pos) − mean(neg):")
        logger.info("       Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit "
                    "society? A language embedding approach. The Review of Financial "
                    "Studies, 39(5), 1227-1266. https://doi.org/10.1093/rfs/hhaf012")
        logger.info("       → §1.3.2 Eq. 1 文章级投影 + Eq. 2 等权 Bank-Year 聚合")
        logger.info("     · 语义维度 = 正−负差分向量 (文化几何学, 方法论上游):")
        logger.info("       Kozlowski, A. C., Taddy, M., & Evans, J. A. (2019). The geometry "
                    "of culture: Analyzing the meanings of class through word embeddings. "
                    "American Sociological Review, 84(5), 905-949. "
                    "https://doi.org/10.1177/0003122419877135")
        logger.info("     · 句向量方法 (sentence embedding 上游):")
        logger.info("       Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence "
                    "embeddings using Siamese BERT-networks. In Proceedings of EMNLP-IJCNLP "
                    "(pp. 3980-3990). ACL. https://doi.org/10.18653/v1/D19-1410")
        logger.info("     · 嵌入派生测度作『生成式回归量』的计量推断框架 (benefit_mean 进面板回归的依据):")
        logger.info("       Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). Large language "
                    "models: An applied econometric framework (NBER Working Paper No. 33344). "
                    "National Bureau of Economic Research. https://doi.org/10.3386/w33344")
        logger.info("       → benefit_score = 嵌入×锚点方向余弦投影的 generated regressor; 下游以 "
                    "bank/year FE 吸收其固定偏移、listwise 处理 NaN, 对齐该框架对测度误差的告诫")
        logger.info("     · 白话: 给每篇金科新闻打『利好/损害银行经营』连续态度分 "
                    "(>0 利好, <0 损害), 双 API 模型 × 三轨交叉验证。")
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法块打印失败 (不影响处理): {exc!r}")


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
        pd.DataFrame: 合并了 24 列 benefit_* 指标的面板 (MAIN + _lg 双 API 模型 × Full/Ctx/SS 三轨 × 4 指标)
    """
    _step_start = time.time()
    logger.info("=" * 60)
    logger.info("步骤 7h-benefit: 金融科技经营效益态度投影")
    logger.info("  (Jha, Liu & Manela 2026, RFS §1.3.2)")
    logger.info("=" * 60)

    _log_benefit_env_config_methods(panel, df_exploded)

    df_exploded = df_exploded.copy()
    _emitted_cols: list[str] = []  # 仅服务于末尾结果分析/计时的日志局部变量

    # ---- 6.0 缓存路径 ----
    cache_filename = FILENAMES.get('output_27_benefit_cache',
                                   '27_benefit_embeddings.npy')

    # ---- 6.1 双 API 模型外层循环 (Dual-API-Model Embedding, v3.14.0) ----
    # suffix='' → MAIN spec (Qwen/Qwen3-Embedding-8B, API) → 既有 canonical 列
    #             (benefit_mean_full / benefit_std_full / ...)
    # suffix='_lg' → LARGE spec (text-embedding-3-large, API) → 平行 co-primary 稳健列
    #             (benefit_mean_lg_full / ...; 维度独立计算, 由 emb.shape[1] 驱动)。
    # 每个 spec 用自己的锚点 + 文本 + 方向向量, 全程维度无关。_lg 为活动 co-primary
    # (config/features.yaml 已激活 embedding_large), 仅当 config 缺该块时才退化为单 MAIN。
    # (v3.14.0 已整体移除本地稳健轨 _t2v / _bge; 仅余双 API 模型)
    _specs = [('', EMBEDDING_CONFIG)]
    if _LARGE_SPEC:
        _specs.append(('_lg', _LARGE_SPEC))
    for suffix, spec in _specs:
        spec_tag = "MAIN" if suffix == '' else f"CO-PRIMARY({suffix})"

        # ---- 6.2 计算方向向量 (per spec) ----
        direction = _compute_direction_vector(spec=spec)
        if direction is None:
            logger.warning(
                f"  [{spec_tag}] 方向向量计算失败, 跳过该 spec "
                f"(model={_eng.spec_model(spec)})"
            )
            continue

        # fix(omni-g-benefit-01, 2026-06-11): 方向向量落盘 (27c placebo 链路
        # --main-direction-npy 的产出方; 此前该输入从未被任何阶段产出)。
        if _CACHE_EMBEDDINGS:
            _persist_direction_vector(direction, suffix, spec=spec)

        # ---- 6.3 三轨投影 ----
        # 【术语】三轨投影 (Triple-Track Projection):
        #   - Full 轨: 标题 + 全文正文，完整语义信号
        #   - Ctx  轨: 实体上下文 (entity_context.py 提取)，消除非目标实体的情感污染
        #   - SS   轨: 银行+金科同句共现 (content_ss; 仅"同句内同时含 目标银行∧金科词"
        #             的句 ±N 句窗, 无共现→镜像 ctx 回退全文 body), 锁定金科归因更窄的语境
        #   与 Stage 25/26 的双轨设计同构 (此处扩为三轨)
        # 【白话】Full 轨 = 整篇新闻; Ctx 轨 = 只看提到这家银行的段落;
        #   SS 轨 = 只看"既提这家银行又提金融科技"的同一句话 (归因最严)
        for track in ['full', 'ctx', 'ss']:
            col_score = f'benefit_score{suffix}_{track}'

            # 检查 Ctx/SS 轨数据是否存在 (content_ctx / content_ss 缺列时优雅跳过,
            # 镜像 ctx 守卫: ss 由 stage 13 ctx_materializer 物化, 旧 schema 可能缺列)
            content_col_for_track = f'content_{track}'
            if track in ('ctx', 'ss') and content_col_for_track not in df_exploded.columns:
                logger.info(f"  [{spec_tag}] {track.upper()} 轨: {content_col_for_track} 列不存在, 跳过")
                continue

            # 向量化文本构建（避免 iterrows 性能瓶颈）
            if track == 'full':
                # P1 修复 (metric-audit 2026-06-02, 病根A): 改读 content_full (= stage13
                # prepend_title(标题,内容), 与 tone_words/tone_berts/ctx/ss 轨同源), 替代裸
                # 空格拼接; 缺列回退 prepend_title 内联构建.
                if 'content_full' in df_exploded.columns:
                    texts = df_exploded['content_full'].fillna('').astype(str).str.strip().tolist()
                else:
                    from news_process.core.text.entity_context import prepend_title
                    _t = df_exploded.get('标题', pd.Series('', index=df_exploded.index)).fillna('').astype(str)
                    _b = df_exploded.get('内容', pd.Series('', index=df_exploded.index)).fillna('').astype(str)
                    texts = [prepend_title(t, b).strip() for t, b in zip(_t, _b)]
            else:
                # ctx → content_ctx / ss → content_ss (同句共现; 回退已在 stage 13 镜像 ctx)
                texts = df_exploded[content_col_for_track].fillna('').astype(str).str.strip().tolist()

            # 过滤空文本
            valid_mask = np.array([bool(t) for t in texts])
            valid_texts = [t for t, m in zip(texts, valid_mask) if m]

            if not valid_texts:
                logger.info(f"  [{spec_tag}] {track.upper()} 轨: 无有效文本, 跳过")
                continue

            logger.info(f"  [{spec_tag}] {track.upper()} 轨: "
                        f"{len(valid_texts)}/{len(texts)} 篇有效文本")

            # 缓存路径 (spec × track 分开)
            cache_path = os.path.join(
                OUTPUT_DIR,
                cache_filename.replace('.npy', f'{suffix}_{track}.npy'))

            # 投影计算 (用本 spec 嵌入并投影到本 spec 的方向向量)。
            # fix(omni-g-benefit-01, 2026-06-11): _project_texts 现接收全量
            # 文本 (含空文本, 内部过滤并返回等长 NaN-填充得分), 使其能按
            # df_exploded 行序落盘全长嵌入 .npy + sidecar (27c 链路输入)。
            scores = _project_texts(texts, direction, cache_path, spec=spec)

            # 回填至 df_exploded (in-place 副作用)
            # ⚠️ 此处向 df_exploded 添加了 benefit_score{suffix}_{track} 中间列。
            #   该列仅用于下方 Bank-Year 聚合，不影响后续模块
            #   (compute_brokerage_centrality 等只读取自身所需列)。
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

            # 正/负态度占比 (P1 修复 metric-audit 2026-06-02; fix(benefitfrac-01)): 余弦投影
            # 受嵌入空间各向异性影响, 绝对 sign-at-0 阈值使 benefit_pos_frac 近饱和退化
            # (实测 ~96.9% 文章投影>0, 作回归自变量信息量趋零).
            # 注 [锚点勘误 2026-06-10]: Mu & Viswanath (2018, All-but-the-Top) 与 Ethayarajh
            # (2019) 仅**记录嵌入空间各向异性问题** (动因), 二者的方法是去主成分/whitening,
            # **不是**中位数中心化。下面"以全样本投影中位数为中心"是本项目针对左偏分布的
            # 操作化处理, 勿声称实现了 Mu-Viswanath/Ethayarajh 的各向异性校正法。**以全样本投影中位数为中心**:
            # 原 mean-center 在左偏分布 (skew≈-1.23) 下仅得 P(>mean)=0.5634≠0.5, 未达声称的
            # ~50% 平衡基线; median-center 由构造保证 P(>median)≈0.5, 对投影偏态稳健。
            # benefit_mean (连续主测度) 不变, 其绝对偏移由 bank/year FE 吸收.
            # 注 (correctness-01): "P(>median)≈0.5" 指文章级 pooled 分布 (_center 由
            # df_exploded 算出); 面板列 benefit_pos_frac 因 mean-of-fractions 聚合 (各
            # bank-year 文章数不均的 Jensen 效应) 实测 bank-year 简单均值 ~0.45, 非 0.5。
            # fix(omni-g-benefit KNOWN-OPEN①, 2026-06-11): median 不再每次 run 现算
            # — 改冻结 sidecar (_benefit_center_sidecar.json): 首跑计算持久化, 后续
            # 读冻结值; 语料增量不再平移全历史 pos/neg_frac。详见 _get_frozen_center。
            _center = _get_frozen_center(col_score, df_exploded[col_score],
                                         _eng.spec_model(spec))
            frac = (df_exploded
                    .dropna(subset=[col_score])
                    .groupby(['target_bank', 'year'])[col_score]
                    .agg(
                        benefit_pos_frac=lambda x, c=_center: (x > c).mean(),
                        benefit_neg_frac=lambda x, c=_center: (x < c).mean(),
                    )
                    .reset_index())

            agg = agg.merge(frac, on=['target_bank', 'year'], how='left')

            # fix(omni-g-benefit-05, 2026-06-11): 单观测 bank-year 的 std (ddof=1)
            # 在统计上未定义 — 保持 NaN, 不再 fillna(0) (填 0 令'只有 1 篇报道'与
            # '多篇完全一致(真实零分歧)'不可区分, 且与同面板核心 llm_vote_tone_std
            # 族的 NaN 口径冲突)。下游回归经 listwise deletion 自然处理。

            # 重命名: 添加 (模型 suffix +) 轨后缀
            #   suffix='' → benefit_mean_full 等 (canonical, 字节级不变)
            #   suffix='_lg' → benefit_mean_lg_full 等 (co-primary twin, text-embedding-3-large)
            rename_map = {
                'benefit_mean': f'benefit_mean{suffix}_{track}',
                'benefit_std': f'benefit_std{suffix}_{track}',
                'benefit_pos_frac': f'benefit_pos_frac{suffix}_{track}',
                'benefit_neg_frac': f'benefit_neg_frac{suffix}_{track}',
            }
            agg = agg.rename(columns=rename_map)

            # ---- 6.5 合并至面板 ----
            new_cols = list(rename_map.values())
            panel = panel.merge(
                agg[['target_bank', 'year'] + new_cols],
                on=['target_bank', 'year'],
                how='left'
            )

            _mean_col = f'benefit_mean{suffix}_{track}'
            _emitted_cols.append(_mean_col)
            _notna_rate = float(panel[_mean_col].notna().mean())
            # 结果解读: 非空率 = 该 (spec×轨) 在 bank-year 面板的覆盖率。
            # T=2 试跑下覆盖率天然偏低; 生产 T=18 应趋高。
            _cov_verdict = (
                "✅ 覆盖充分" if _notna_rate >= 0.50
                else ("⚠ 覆盖偏低 (小样本/稀疏轨)" if _notna_rate > 0
                      else "❌ 全空 (无有效投影)")
            )
            logger.info(f"  [{spec_tag}] {track.upper()} 轨聚合完成: "
                        f"{_mean_col} 非空率 {pct4(_notna_rate)} → {_cov_verdict}")

    # ---- 6.5b co-primary both-or-neither parity 守卫 (D-4a, code-review P1-B) ----
    # benefit_society 的 spec 循环对 MAIN / _lg 各自 direction-None 时 `continue` 整体跳过,
    # 会留单边孤儿列 (MAIN 有 benefit_*_{track}, _lg 缺 benefit_*_lg_{track}, 或反之)。
    # 此处对每轨检查两 co-primary 覆盖: 若恰一侧有效 (列存在且有非空值) → 两族 (MAIN + _lg)
    # 该轨全部列均**建并置 NaN** (列名双射成立、值 NaN), 杜绝单边孤儿。仅 _lg 激活时生效。
    if _LARGE_SPEC and len(_specs) == 2:
        _BENEFIT_BASES = ['benefit_mean', 'benefit_std', 'benefit_pos_frac', 'benefit_neg_frac']
        for track in ['full', 'ctx', 'ss']:
            _mc, _lc = f'benefit_mean_{track}', f'benefit_mean_lg_{track}'
            _m_ok = _mc in panel.columns and bool(panel[_mc].notna().any())
            _l_ok = _lc in panel.columns and bool(panel[_lc].notna().any())
            if _m_ok != _l_ok:  # 恰一侧有效 = 单边孤儿 (列缺失或全空)
                logger.error(
                    f"  ⚠ co-primary parity 违例 [{track}]: MAIN 有效={_m_ok} / _lg 有效={_l_ok}; "
                    f"both-or-neither → 两族 {track} 列均建并置 NaN (无单边孤儿)"
                )
                for _base in _BENEFIT_BASES:
                    for _sfx in ('', '_lg'):
                        panel[f'{_base}{_sfx}_{track}'] = np.nan

    # ---- 6.6 结果分析 + 阶段计时 (日志富集, golden-safe) ----
    try:
        logger.info("  📊 关键指标解读 (benefit 面板覆盖率, sig4)")
        _n_emitted = len(_emitted_cols)
        if _n_emitted == 0:
            logger.warning("     · 未产出任何 benefit_mean 列 (全部 spec×轨 跳过); "
                           "检查嵌入 API / content_ctx·content_ss 列可用性")
        else:
            _rates = {c: float(panel[c].notna().mean()) for c in _emitted_cols}
            _best = max(_rates.values())
            _worst = min(_rates.values())
            _mean_cov = sum(_rates.values()) / len(_rates)
            _n_lg = sum(1 for _c in _emitted_cols if '_lg_' in _c)
            logger.info(f"     · 产出 benefit_mean 列数={_n_emitted:,d} (含 _lg co-primary twin × 三轨) | "
                        f"覆盖率区间 [{pct4(_worst)}, {pct4(_best)}]")
            logger.info(f"       (均值覆盖率={pct4(_mean_cov)} | _lg co-primary twin 列数={_n_lg:,d} / "
                        f"MAIN canonical 列数={_n_emitted - _n_lg:,d}; 双 API 模型 both-or-neither parity)")
            for _c, _r in _rates.items():
                logger.info(f"       - {_c}: 非空率 {pct4(_r)}")
            # 连续主测度 benefit_mean 的整体数值健康 (取首个非全空列做快速诊断)
            for _c in _emitted_cols:
                _ser = panel[_c].dropna()
                if len(_ser) > 0:
                    logger.info(
                        f"     · {_c} 分布: μ={sig4(float(_ser.mean()))} / "
                        f"σ={sig4(float(_ser.std()))} / "
                        f"min={sig4(float(_ser.min()))} / max={sig4(float(_ser.max()))} "
                        f"(理论域 [-1, 1])"
                    )
                    # 中位数 + 四分位距 (median + Q1/Q3/IQR): benefit_mean 是双极余弦投影头号
                    # 连续测度, §6.5 注披露其左偏 (skew≈-1.23) 却仅 log 了 μ/σ — 单点矩不足以
                    # 刻画偏态。补 median/IQR 让 .log 自证分布形状: 负偏 (skew<0) 时通常 median>μ
                    # (均值被左尾拉低)。read-only, _q 喂 logger 后即弃, 不回流下游 (golden-safe)。
                    _q = _ser.quantile([0.25, 0.5, 0.75])
                    logger.info(
                        f"       (median={sig4(float(_q.loc[0.5]))} / "
                        f"Q1={sig4(float(_q.loc[0.25]))} / Q3={sig4(float(_q.loc[0.75]))} / "
                        f"IQR={sig4(float(_q.loc[0.75] - _q.loc[0.25]))}; "
                        f"median 与 μ 之差刻画偏态方向, 左偏投影时通常 median>μ)"
                    )
                    break
        _elapsed = time.time() - _step_start
        logger.info(f"  ⏱ 步骤 7h-benefit 墙钟耗时: {sig4(_elapsed)} 秒")
    except Exception as _ra_exc:  # noqa: BLE001
        logger.warning(f"  结果分析/计时块打印失败 (不影响产物): {_ra_exc!r}")

    # ---- 6.6b 其余三输出族分布 (pos/neg_frac + std, 日志富集, golden-safe) ----
    # §6.6 仅追踪 benefit_mean (_emitted_cols 只 append _mean_col); pos_frac / neg_frac /
    # std 三族虽全部并入面板 (rename_map) 却无任何运行期分布报告。此块仅**只读**既有面板列、
    # 由 _emitted_cols 机械派生同名孪生列, 结果喂 logger 后即弃 (不回流下游); 控制流 / 写盘 /
    # schema / 返回值全不变 (golden-safe; 镜像 §6.6 的 try/except 骨架)。
    try:
        # (a) benefit_pos_frac 面板级均值 → 运行期自证 §6.5 注 (correctness-01) 的已披露
        #     经验陈述: 文章级 P(>median)≈0.5, 但面板列 benefit_pos_frac 经 mean-of-fractions
        #     聚合 (各 bank-year 文章数不均的 Jensen 效应) 实测 bank-year 简单均值 ~0.45 (≠0.5)。
        #     让 .log 把这个论文级披露数字当场复核, 而非只留注释。
        _pos_cols = [c.replace('benefit_mean', 'benefit_pos_frac') for c in _emitted_cols]
        _pos_cols = [c for c in _pos_cols if c in panel.columns]
        if _pos_cols:
            _pos_pool = pd.concat([panel[c].dropna() for c in _pos_cols], ignore_index=True)
            if len(_pos_pool) > 0:
                logger.info(
                    f"     · benefit_pos_frac 面板级均值={pct4(float(_pos_pool.mean()))} "
                    f"(n={len(_pos_pool):,d} bank-year×族; 披露基线 ~0.45 ≠ 0.5 → "
                    f"mean-of-fractions Jensen 效应自证)"
                )
        # (b) benefit_std 族 (within-bank-year 态度分歧度, 已发布输出测度; 单观测 ddof=1 std
        #     未定义→NaN): 报 notna 覆盖率 (= 多观测 bank-year 占比) + 中位离散度。
        _std_cols = [c.replace('benefit_mean', 'benefit_std') for c in _emitted_cols]
        _std_cols = [c for c in _std_cols if c in panel.columns]
        if _std_cols:
            _std_all = pd.concat([panel[c] for c in _std_cols], ignore_index=True)
            _std_pool = _std_all.dropna()
            _std_med = float(_std_pool.median()) if len(_std_pool) > 0 else float('nan')
            logger.info(
                f"     · benefit_std 族 (内部分歧度) notna 覆盖率={pct4(float(_std_all.notna().mean()))} "
                f"(多观测 bank-year 占比; 单篇报道 std 未定义→NaN) | "
                f"中位离散度 median={sig4(_std_med)} (理论域 [0, 1])"
            )
    except Exception as _frac_exc:  # noqa: BLE001
        logger.warning(f"  pos_frac/std 分布打印失败 (不影响产物): {_frac_exc!r}")

    logger.info("=" * 60)
    return panel
