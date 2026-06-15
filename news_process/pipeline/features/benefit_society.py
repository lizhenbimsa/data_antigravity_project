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
  benefit_mean_full/ctx/ss:      态度均值 ∈ [-1, 1]
  benefit_std_full/ctx/ss:       态度离散度 ∈ [0, 1] (单观测 bank-year 为 NaN,
                              fix(omni-g-benefit-05): 不再 fillna(0) — '只有 1 篇报道'
                              与 '多篇完全一致' 在统计上不可区分, 与核心 tone std 族对齐)
  benefit_pos_frac_full/ctx/ss:  正态度文章占比 ∈ [0, 1]
  benefit_neg_frac_full/ctx/ss:  负态度文章占比 ∈ [0, 1]
  (上述 4 指标 × full/ctx/ss 三轨另各有 _t2v 稳健 twin 列:
   benefit_mean_t2v_full/ctx/ss 等; MAIN=API 1536 维 / ROBUSTNESS=text2vec 768 维, 共 24 列)
  ss 轨 (银行+金科同句, content_ss): 仅取"同句内同时含 目标银行∧金科词"的句 ±N 句窗,
   回退=无共现→镜像 ctx 回退全文 body (ss_is_fallback=True); 与 full/ctx 并列第三主轨。

pos/neg_frac 阈值中心 (KNOWN-OPEN① 修复, fix(omni-g-benefit, 2026-06-11)):
  median-center 不再每次 run 现算 — 首跑以全样本投影 pooled median 计算并持久化到
  data/processed/_benefit_center_sidecar.json, 后续 run 读冻结值 (跨 run 可比;
  披露: 冻结值仍是首跑 in-sample median, P(>center)≈0.5 仅对首跑语料成立)。

审计链路落盘 (fix(omni-g-benefit-01, 2026-06-11)):
  cache_embeddings=true 时落盘全长文章嵌入 27_benefit_embeddings{_t2v}_{full,ctx}.npy
  + 方向向量 27_benefit_direction{_t2v}.npy (各带 .sidecar.json: model_id/n_rows/dim),
  供 27c alt-anchor / placebo 审计链路同嵌入空间消费。
============================================================================
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

# Phase 5c-1: 注入项目根, 让 ``news_process.core.*`` 在包模式下可解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.caching import LLMCache
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
from news_process.pipeline.panel.encode import CONFIG, FILENAMES, OUTPUT_DIR, logger  # noqa: E402

STAGE_NAME = "27_fintech_benefit_society"

# LLM API 配置（复用 tone_llm_processing 节中的 base_url 和 api_key）
LLM_CONFIG = CONFIG.get('tone_llm_processing', {})
EMBEDDING_CONFIG = CONFIG.get('embedding_api', {})           # MAIN spec → canonical 列
# v3.7.x 双模型嵌入: ROBUSTNESS twin (shibing624/text2vec, local) → '_t2v' 列
_ROBUSTNESS_SPEC = CONFIG.get('embedding_robustness', {})
_LOCAL_EMBEDDING_MODEL = None

# 模块专属配置
_BENEFIT_CFG = CONFIG.get('benefit_society', {})
_MAX_TOKENS_PER_INPUT = _BENEFIT_CFG.get('max_tokens_per_input', 8191)
_MAX_TOKENS_PER_REQUEST = _BENEFIT_CFG.get('max_tokens_per_request', 250_000)
_CACHE_EMBEDDINGS = _BENEFIT_CFG.get('cache_embeddings', True)
_ANCHOR_SIGN_TOL = float(_BENEFIT_CFG.get('anchor_sign_tolerance', 0.03))
_ANCHOR_PAIR_MIN_MARGIN = float(_BENEFIT_CFG.get('anchor_pair_min_margin', 0.02))

RETRY_DELAY = 5
MAX_RETRY_DELAY = 60
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


def _embedding_config_uses_local() -> bool:
    base_url = str(EMBEDDING_CONFIG.get('base_url') or '').strip().lower()
    return base_url in {
        'local',
        'local://',
        'sentence-transformers',
        'sentence_transformers',
    }


def _encode_embeddings_local(texts, *, log_prefix="Embedding") -> np.ndarray:
    global _LOCAL_EMBEDDING_MODEL

    from sentence_transformers import SentenceTransformer

    local_model_id = (
        EMBEDDING_CONFIG.get('model')
        or 'shibing624/text2vec-base-chinese'
    )
    if _LOCAL_EMBEDDING_MODEL is None:
        logger.info(f"    {log_prefix}: 使用本地模型 {local_model_id}")
        _LOCAL_EMBEDDING_MODEL = SentenceTransformer(local_model_id)

    emb_local = _LOCAL_EMBEDDING_MODEL.encode(
        list(texts),
        batch_size=int(EMBEDDING_CONFIG.get('batch_size', 32) or 32),
        show_progress_bar=False,
    )
    return np.asarray(emb_local, dtype=np.float32)


def _get_embeddings(texts: list[str],
                    token_counts: list[int] = None,
                    *,
                    spec: dict | None = None,
                    log_prefix: str = "Embedding") -> np.ndarray:
    """文本 → Embedding 向量, 委托给统一引擎 _eng.embed_texts。

    spec 决定模型与路径 (MAIN=text-embedding-3-small / ROBUSTNESS=text2vec)。
    token_counts 已不再需要 (引擎内部按 token 自行分批), 保留参数仅为签名兼容。
    """
    return _eng.embed_texts(
        texts,
        spec or EMBEDDING_CONFIG,
        cache_db_path=CACHE_DB_PATH,
        log_prefix=log_prefix,
    )


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
    # Plan-r3 P3-17 接入: embedding 缓存键的 prompt_version 维度.
    text_pipeline_version = EMBEDDING_CONFIG.get('text_pipeline_version', 'v0')
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    cached_results = [
        cache.get(embedding_model, text, prompt_version=text_pipeline_version)
        if cache else None
        for text in texts
    ]
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
                                        [json.dumps(emb) for emb in batch_embs],
                                        prompt_version=text_pipeline_version,
                                    )
                                # v3.7.0 (C1 + M15 修复): LLM archive batch API
                                # 单次 lock + 单次 file open (vs N 条 lock contention)
                                if _LLM_ARCHIVE_AVAILABLE:
                                    try:
                                        actual_version = data.get('model', embedding_model)
                                        api_endpoint = f"{base_url}/embeddings"
                                        records = [
                                            {
                                                'cache_key': LLMCache.make_key(
                                                    embedding_model, text,
                                                    prompt_version=text_pipeline_version,
                                                ),
                                                'model_id': embedding_model,
                                                'model_version': actual_version,
                                                'prompt': text,
                                                'response_raw': json.dumps({
                                                    'embedding': emb,
                                                    'batch_index': i,
                                                    'batch_total': len(batch_embs),
                                                    'batch_id': batch_idx,
                                                }, ensure_ascii=False),
                                                'prompt_version': text_pipeline_version,
                                                'temperature': 0.0,  # embedding API 无 temperature
                                                'api_endpoint': api_endpoint,
                                                'http_status': status,
                                            }
                                            for i, (text, emb) in enumerate(zip(batch, batch_embs))
                                        ]
                                        _get_archive().append_batch(records)
                                    except Exception as _arch_exc:
                                        logger.warning(
                                            f"    LLM archive (benefit_society batch {batch_idx+1}) "
                                            f"失败 (不阻塞): {_arch_exc!r}"
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

def _compute_direction_vector(spec: dict | None = None) -> np.ndarray | None:
    all_anchors = POSITIVE_ANCHORS + NEGATIVE_ANCHORS
    token_counts = [_count_tokens(s) for s in all_anchors]
    emb = _get_embeddings(
        all_anchors,
        token_counts,
        spec=spec or EMBEDDING_CONFIG,
        log_prefix="Benefit anchor embedding",
    )
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
                f"(pos={pos_score:.4f}, neg={neg_score:.4f}, margin={margin:.4f}): "
                f"{pos_sentence[:18]}... / {neg_sentence[:18]}..."
            )
        elif pos_score <= -_ANCHOR_SIGN_TOL:
            logger.warning(
                f"    正极句 #{i+1} 明显投影为负 ({pos_score:.4f}): "
                f"{pos_sentence[:20]}..."
            )
        elif neg_score >= _ANCHOR_SIGN_TOL:
            logger.warning(
                f"    负极句 #{i+1} 明显投影为正 ({neg_score:.4f}): "
                f"{neg_sentence[:20]}..."
            )
        elif pos_score <= 0 or neg_score >= 0:
            logger.info(
                f"    锚点对 #{i+1} 存在近零边界符号 "
                f"(pos={pos_score:.4f}, neg={neg_score:.4f}, margin={margin:.4f}), "
                "正负间隔正常"
            )

    logger.info(f"    方向向量: 维度 {direction.shape}, ||p|| = {dir_norm_val:.4f}")
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
    embed_texts 自带 Early Chunking + token 加权 mean pooling (与 stage 25
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

    emb = _get_embeddings(
        valid_texts,
        None,
        spec=spec or EMBEDDING_CONFIG,
        log_prefix="Benefit text embedding",
    )

    if emb is None or len(emb) == 0:
        return scores

    if cache_path and _CACHE_EMBEDDINGS:
        _persist_article_embeddings(cache_path, emb, valid_mask,
                                    spec=spec or EMBEDDING_CONFIG)

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
        如 ``benefit_score_full`` / ``benefit_score_t2v_ctx``);
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
        logger.info(f"    {score_key}: 使用冻结 center={entry['center']:.6f} (sidecar)")
        return float(entry['center'])

    center = float(scores.dropna().median()) if scores.notna().any() else float('nan')
    if not np.isfinite(center):
        logger.warning(f"    {score_key}: 无有效投影得分, center 回退 0.0 (不冻结)")
        return 0.0
    n_scores = int(scores.notna().sum())
    if n_scores < _CENTER_MIN_N_TO_FREEZE:
        logger.warning(
            f"    {score_key}: 有效得分仅 {n_scores} 篇 < {_CENTER_MIN_N_TO_FREEZE}, "
            f"本次使用现算 center={center:.6f} 但**不冻结** (防 toy/试跑数据持久化)"
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
        logger.info(f"    {score_key}: 首跑冻结 center={center:.6f} "
                    f"→ {_CENTER_SIDECAR_FILENAME}")
    except OSError as exc:
        logger.warning(f"    center sidecar 写入失败 (本次仍用 {center:.6f}): {exc!r}")
    return center

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
        pd.DataFrame: 合并了 24 列 benefit_* 指标的面板 (MAIN + _t2v 双模型 × Full/Ctx/SS 三轨 × 4 指标)
    """
    logger.info("=" * 60)
    logger.info("步骤 7h-benefit: 金融科技经营效益态度投影")
    logger.info("  (Jha, Liu & Manela 2026, RFS §1.3.2)")
    logger.info("=" * 60)

    df_exploded = df_exploded.copy()

    # ---- 6.0 缓存路径 ----
    cache_filename = FILENAMES.get('output_27_benefit_cache',
                                   '27_benefit_embeddings.npy')

    # ---- 6.1 双模型外层循环 (Dual-Model Embedding) ----
    # suffix='' → MAIN spec (text-embedding-3-small, API) → 既有 canonical 列
    #             (benefit_mean_full / benefit_std_full / ... 字节级不变)
    # suffix='_t2v' → ROBUSTNESS spec (shibing624/text2vec, local) → 平行稳健列
    #             (benefit_mean_t2v_full / ...; 768 维独立计算, 绝不与 API 1536 维混算)
    # 每个 spec 用自己的锚点 + 文本 + 方向向量, 全程维度无关 (emb.shape[1] 驱动)。
    for suffix, spec in [('', EMBEDDING_CONFIG), ('_t2v', _ROBUSTNESS_SPEC)]:
        spec_tag = "MAIN" if suffix == '' else "ROBUSTNESS(_t2v)"

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
            #   suffix='_t2v' → benefit_mean_t2v_full 等 (robustness twin)
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

            logger.info(f"  [{spec_tag}] {track.upper()} 轨聚合完成: "
                        f"benefit_mean{suffix}_{track} 非空率 "
                        f"{panel[f'benefit_mean{suffix}_{track}'].notna().mean():.1%}")

    logger.info("=" * 60)
    return panel
