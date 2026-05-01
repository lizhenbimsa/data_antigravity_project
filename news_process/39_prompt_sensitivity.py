"""
39_prompt_sensitivity.py — Prompt 措辞敏感度量化测试
===============================================================

功能：
    通过系统性改写 Prompt 措辞（保持任务语义不变），量化 LLM 标注结果
    对 Prompt 表述选择的敏感程度。采用双轨（full + ctx）测试架构，
    与 21_tone_llms.py 主流水线保持一致。

方法论依据：
    Carlson & Burbano (2026, SMJ 47(3):699–725, §3.5): "generating
    families of related prompts... testing their impact on downstream
    analyses" — Stage 5: Validation and Robustness.

变体设计原则：
    每个变体仅改变表述方式，不改变判定标准的实质内容，不改变输出
    JSON schema。一致性差异完全归因于措辞敏感度。

输入：
    阶段21输出 21_tone_llms_full.parquet（含双轨 LLM 判定列）

输出：
    eval_reports/prompt_sensitivity_results.json   — 结构化指标
    eval_reports/prompt_sensitivity_detail.csv     — 逐条对比
    eval_reports/prompt_sensitivity_table.tex      — LaTeX 表格
    eval_reports/prompt_sensitivity_heatmap.png    — κ 热力图
"""

import os
import time
import json

import asyncio
import aiohttp
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from importlib import import_module

from utils.helpers import load_config, setup_logging, log_memory_usage

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "39_prompt_sensitivity"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 复用 21_tone_llms.py 的 LLM 基础设施（与 36_entity_masking_test.py 一致的 import 模式）
_tone_llms = import_module('21_tone_llms')
fetch_llm_async        = _tone_llms.fetch_llm_async
_aggregate_track       = _tone_llms._aggregate_track
# 注：parse_json_response, majority_vote_bool/sentiment 由 _aggregate_track 内部调用，无需显式导入
MODELS                 = _tone_llms.MODELS
MAX_CONCURRENCY        = _tone_llms.MAX_CONCURRENCY
PROMPT_TEMPLATE        = _tone_llms.PROMPT_TEMPLATE  # V0 baseline（测试套件用于差异比对）

# 复用评估模块的一致性指标
_eval = import_module('33_news_llms_evaluation')
compute_cohens_kappa       = _eval.compute_cohens_kappa
compute_krippendorffs_alpha = _eval.compute_krippendorffs_alpha

# 注：content_ctx 物化由 _tone_llms._materialize_content_ctx 内部完成，
# 其依赖的 extract_entity_context/get_target_aliases 无需在此显式导入。

# 模块配置
PS_CFG = CONFIG.get('prompt_sensitivity_test', {})
SAMPLE_SIZE = PS_CFG.get('sample_size', 1000)
RANDOM_SEED = PS_CFG.get('random_seed', 42)
PASS_THRESHOLD_VERIFICATION = PS_CFG.get('pass_threshold_verification', 0.85)
PASS_THRESHOLD_SENTIMENT    = PS_CFG.get('pass_threshold_sentiment', 0.80)
PASS_THRESHOLD_KAPPA        = PS_CFG.get('pass_threshold_kappa', 0.70)
PASS_THRESHOLD_ALPHA        = PS_CFG.get('pass_threshold_alpha', 0.667)


# ============================================================================
# 2. Prompt 变体定义（硬编码）
# ============================================================================
# 设计原则：每个变体仅改变表述方式，保持任务语义和输出 JSON schema 不变。
# 所有变体共享 {target_bank}, {co_mentioned_banks}, {title}, {content} 占位符
# 和 {{ / }} JSON 转义格式。
#
# 学术依据 1: De Kok (2025) Appendix C - GLLMs Generate Text Left to Right. 
#   在 JSON 输出中前置 explanation（如 verification_reason），迫使模型将其作为后续 classification 的上下文，以实现 Zero-shot CoT。
# 学术依据 2: Generative AI and Finance (Section 3.7.2) - Explanation and evaluation of LLM reasoning.
#   强制要求模型先生成解释，然后再输出分数或判定结论，从而彻底纠正模型的因果错位（Post-hoc rationalization）与幻觉。

VARIANT_PROMPTS = {
    # ── V1: 角色改写 (Role-Based Variation) ──
    # 改变角色定义和语气，移除元方法描述
    "V1_role": """你是一名中国银行业数字化转型分析师，具备丰富的银行金融科技战略评估与中文财经文本分析经验。请依次完成以下两项分析任务。

【任务一：银行金融科技新闻验证】

针对【目标分析银行: {target_bank}】，判断本文是否为该银行的金融科技相关新闻。判定为 true 须同时满足以下全部条件：
1. 主体关联：正文实质性涉及【{target_bank}】（不含来源标注、免责声明、赞助冠名等边缘提及）。
2. 主题聚焦：核心议题聚焦金融科技（AI、区块链、数字货币、大数据风控、云计算、开放银行、数字支付等）。
3. 实质关联：该银行与金融科技主题存在可证实的实质联系（技术研发、产品发布、业务合作、战略部署、应用落地等）。

不满足任一条件、或金融科技仅作背景修辞、或文章为纯宏观综述而无具体银行行动，均判定为 false。

【任务二：情感倾向分析】（仅当任务一判定为 true 时执行）

聚焦新闻仅对【{target_bank}】的情感倾向。
注意：文中可能同时提及同行（{co_mentioned_banks}），其利好或负面与【{target_bank}】无直接关联时，一律视为噪音，不影响评分。
- 正面：业绩增长、技术突破、创新合作、监管认可等积极事件。
- 中性：客观陈述事实或中立行业动态，无明显褒贬。
- 负面：风险暴露、监管处罚、安全事故、舆论危机等负面事件。

目标分析银行: {target_bank}
同文提及的其他银行（仅供参考，不作为评分对象）: {co_mentioned_banks}
标题: {title}
内容: {content}

严格输出以下 JSON，禁止添加前缀、后缀或 Markdown 包裹：
{{
  "verification_reason": "简明说明判定依据，须引用文章具体内容",
  "is_bank_fintech_news": true/false,
  "confirmed_bank": "确认关联的匹配银行名称（false 时填 null）",
  "fintech_topic": "核心金融科技主题简述（false 时填 null）",
  "fintech_category": "「底层技术」或「应用场景」（false 时填 null）",
  "verification_confidence": 0.0~1.0,
  "sentiment_reason": "简明说明情感判定依据",
  "sentiment": "正面/中性/负面（false 时固定填\\"中性\\"）",
  "sentiment_confidence": 0.0~1.0
}}""",

    # ── V2: 结构重组 (Structural Variation) ──
    # 调换两阶段顺序（先情感后验证）、去除 XML 标签、使用编号列表
    "V2_structure": """你是资深金融科技研究员，精通银行数字化转型与中文财经文本情感分析。请严格按以下顺序完成两阶段分析。

## 第一步：情感倾向预判

先对新闻整体情感做出初步判断：
- 正面：业绩增长、技术突破、创新合作、监管认可等积极事件。
- 中性：客观陈述事实或中立行业动态，无明显褒贬。
- 负面：风险暴露、监管处罚、安全事故、舆论危机等负面事件。

聚焦新闻仅对【{target_bank}】的情感倾向。
注意：文中可能同时提及同行（{co_mentioned_banks}），其利好或负面与【{target_bank}】无直接关联时，一律视为噪音，不影响评分。

## 第二步：银行金融科技新闻验证

仅针对【目标分析银行: {target_bank}】进行验证。判定为 true 须同时满足：
1. 主体关联：正文实质性涉及【{target_bank}】（不含来源标注、免责声明、赞助冠名等边缘提及）。
2. 主题聚焦：核心议题聚焦金融科技（AI、区块链、数字货币、大数据风控、云计算、开放银行、数字支付等）。
3. 实质关联：该银行与金融科技主题存在可证实的实质联系（技术研发、产品发布、业务合作、战略部署、应用落地等）。

不满足任一条件、或金融科技仅作背景修辞、或文章为纯宏观综述而无具体银行行动，均判定为 false。
若判定为 false，则情感固定填"中性"。

## 输入数据

目标分析银行: {target_bank}
同文提及的其他银行（仅供参考）: {co_mentioned_banks}
标题: {title}
内容: {content}

## 输出格式

严格输出以下 JSON，禁止添加前缀、后缀或 Markdown 包裹：
{{
  "verification_reason": "简明说明判定依据，须引用文章具体内容",
  "is_bank_fintech_news": true/false,
  "confirmed_bank": "确认关联的匹配银行名称（false 时填 null）",
  "fintech_topic": "核心金融科技主题简述（false 时填 null）",
  "fintech_category": "「底层技术」或「应用场景」（false 时填 null）",
  "verification_confidence": 0.0~1.0,
  "sentiment_reason": "简明说明情感判定依据",
  "sentiment": "正面/中性/负面（false 时固定填\\"中性\\"）",
  "sentiment_confidence": 0.0~1.0
}}""",

    # ── V3: 精简压缩 (Complexity Reduction) ──
    # 删除所有冗余修辞和示例枚举，保留最小必要指令
    "V3_concise": """请完成以下两项分析。

一、验证：判断本文是否为【{target_bank}】的金融科技实质性新闻。
判 true 须同时满足：(1) 正文实质涉及该银行，(2) 核心议题为金融科技，(3) 该银行与金融科技有可证实的实质联系。
否则判 false。

二、情感：仅当上述判定为 true 时，判断新闻对【{target_bank}】的情感倾向（正面/中性/负面）。
忽略同文提及的其他银行（{co_mentioned_banks}）的情感信号。
若判定为 false，情感固定填"中性"。

目标分析银行: {target_bank}
同文提及银行: {co_mentioned_banks}
标题: {title}
内容: {content}

严格输出以下 JSON：
{{
  "verification_reason": "简明说明判定依据，须引用文章具体内容",
  "is_bank_fintech_news": true/false,
  "confirmed_bank": "确认关联的匹配银行名称（false 时填 null）",
  "fintech_topic": "核心金融科技主题简述（false 时填 null）",
  "fintech_category": "「底层技术」或「应用场景」（false 时填 null）",
  "verification_confidence": 0.0~1.0,
  "sentiment_reason": "简明说明情感判定依据",
  "sentiment": "正面/中性/负面（false 时固定填\\"中性\\"）",
  "sentiment_confidence": 0.0~1.0
}}""",

    # ── V4: 判定改写 (Paraphrase Variation) ──
    # 用完全不同的句式和词汇表达相同的验证三条件
    "V4_paraphrase": """<role>
你是资深金融科技研究员，精通银行数字化转型与中文财经文本情感分析。请严格遵循思维链（Chain-of-Thought）完成以下两阶段序贯分析。
</role>

<step1_verification>
**阶段一：语义真伪精筛**

请评估本文是否构成【{target_bank}】在金融科技领域的实质性报道。做出"是"的判定需要以下三个维度全部成立：
A. **银行实体的深度参与**：文章主体部分讨论了【{target_bank}】的具体行为或决策，而非仅在出处、免责条款或赞助标注中提及其名称。
B. **金融科技的核心地位**：文章的中心论题围绕数字化技术在金融服务中的应用展开，如人工智能、分布式账本、数字资产、智能风控、云端基础设施、开放接口银行、电子支付体系等。
C. **银行与技术的因果关联**：存在可验证的证据表明该银行正在从事与金融科技直接相关的活动——包括但不限于自主研发、产品上线、跨界合作、战略规划或技术方案落地执行。

若上述三项中任一不成立，或金融科技仅作为修辞背景出现，或文章属于缺乏具体银行行动的宏观趋势综述，则应判定为"否"。
</step1_verification>

<step2_sentiment>
**阶段二：情感倾向分析**（仅当阶段一判定为 true 时执行）

聚焦新闻**仅对【{target_bank}】**的情感倾向。
⚠️ 抗污染指令：文中可能同时提及同行（{co_mentioned_banks}），其利好或负面与【{target_bank}】无直接关联时，一律视为噪音，不影响评分。
- `正面`：业绩增长、技术突破、创新合作、监管认可等积极事件。
- `中性`：客观陈述事实或中立行业动态，无明显褒贬。
- `负面`：风险暴露、监管处罚、安全事故、舆论危机等负面事件。
</step2_sentiment>

<input_data>
目标分析银行: {target_bank}
同文提及的其他银行（仅供参考，不作为评分对象）: {co_mentioned_banks}
标题: {title}
内容: {content}
</input_data>

<output_format>
严格输出以下 JSON，禁止添加前缀、后缀或 Markdown 包裹：
{{
  "verification_reason": "简明说明判定依据，须引用文章具体内容",
  "is_bank_fintech_news": true/false,
  "confirmed_bank": "确认关联的匹配银行名称（false 时填 null）",
  "fintech_topic": "核心金融科技主题简述（false 时填 null）",
  "fintech_category": "「底层技术」或「应用场景」（false 时填 null）",
  "verification_confidence": 0.0~1.0,
  "sentiment_reason": "简明说明情感判定依据",
  "sentiment": "正面/中性/负面（false 时固定填\\"中性\\"）",
  "sentiment_confidence": 0.0~1.0
}}
</output_format>""",
}

VARIANT_LABELS = {
    "V1_role": "V1 (Role)",
    "V2_structure": "V2 (Structure)",
    "V3_concise": "V3 (Concise)",
    "V4_paraphrase": "V4 (Paraphrase)",
}


# ============================================================================
# 3. Fleiss' κ 内联实现
# ============================================================================
# 基于 Fleiss (1971, Psychological Bulletin, 76(5):378) 原始公式。
# 代码库中 33_news_llms_evaluation.py 仅有 Krippendorff's α 和 Cohen's κ（二分类）。
# Fleiss' κ 用于 n 个固定编码者对 N 个项目的多编码者名义一致性。

def compute_fleiss_kappa(ratings_matrix: np.ndarray) -> float:
    """计算 Fleiss' κ（多编码者名义一致性系数）。

    Args:
        ratings_matrix: 形状 (N_items, K_categories) 的计数矩阵，
            其中 ratings_matrix[i, j] 表示第 i 个项目被 j 类别标注的编码者数。

    Returns:
        float: Fleiss' κ 值。完全一致=1, 偶然一致=0, 系统性不一致<0。
    """
    N, k = ratings_matrix.shape  # N=项目数, k=类别数
    if N == 0:
        return 0.0

    n = ratings_matrix.sum(axis=1)  # 每个项目的编码者总数
    n_raters = int(n[0])  # 假定每个项目的编码者数相同

    if n_raters <= 1:
        return 0.0

    # 每个项目的一致性 P_i = (1 / (n*(n-1))) * (sum(n_ij^2) - n)
    P_i = (1.0 / (n_raters * (n_raters - 1))) * (
        (ratings_matrix ** 2).sum(axis=1) - n_raters
    )
    P_bar = P_i.mean()  # 整体观测一致性

    # 各类别的边际概率 p_j = sum(n_ij) / (N * n)
    p_j = ratings_matrix.sum(axis=0) / (N * n_raters)
    P_e = (p_j ** 2).sum()  # 期望偶然一致性

    if abs(1.0 - P_e) < 1e-10:
        return 1.0 if abs(P_bar - 1.0) < 1e-10 else 0.0

    kappa = (P_bar - P_e) / (1.0 - P_e)
    return float(kappa)


def _build_fleiss_matrix(labels_matrix: np.ndarray) -> np.ndarray:
    """将编码者标签矩阵转换为 Fleiss 计数矩阵。

    Args:
        labels_matrix: 形状 (n_coders, n_items)，值为整数类别编码。

    Returns:
        np.ndarray: 形状 (n_items, n_categories) 的计数矩阵。
    """
    n_coders, n_items = labels_matrix.shape
    categories = sorted(set(labels_matrix.flatten()))
    cat_to_idx = {c: i for i, c in enumerate(categories)}
    n_cats = len(categories)

    count_matrix = np.zeros((n_items, n_cats), dtype=int)
    for coder in range(n_coders):
        for item in range(n_items):
            cat = labels_matrix[coder, item]
            count_matrix[item, cat_to_idx[cat]] += 1

    return count_matrix


# ============================================================================
# 4. LLM 双轨批量请求（自写编排，不能复用 run_all_llms）
# ============================================================================
# run_all_llms 硬编码了 PROMPT_TEMPLATE，无法传入变体 prompt。
# 本函数结构参考 36_entity_masking_test.run_masked_llms (L178-215)，
# 但增加了双轨 (full + ctx) 支持。

async def run_variant_llms(
    df: pd.DataFrame,
    variant_prompt: str,
    models: list,
    variant_name: str,
) -> dict:
    """对样本执行双轨 LLM 请求，使用指定的变体 prompt。

    Args:
        df: 样本 DataFrame，须含 '内容', 'content_ctx', 'target_bank',
            'co_mentioned_banks', '标题' 列。
        variant_prompt: 变体 prompt 模板字符串。
        models: 模型配置列表。
        variant_name: 变体名称（仅用于日志）。

    Returns:
        dict: {row_idx: {'full': {model_id: res_text}, 'ctx': {model_id: res_text}}}
    """
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    results_map = {i: {'full': {}, 'ctx': {}} for i in df.index}

    total_tasks = len(df) * len(models) * 2
    logger.info(f"  [{variant_name}] 双轨请求: {len(df)} 条 × {len(models)} 模型 × 2 轨道 = {total_tasks} 请求")

    connector = aiohttp.TCPConnector(
        limit=MAX_CONCURRENCY, keepalive_timeout=30, enable_cleanup_closed=True,
    )
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for idx, row in df.iterrows():
            content_full = str(row.get('内容', ''))
            content_ctx = str(row.get('content_ctx', content_full))
            target_bank = str(row.get('target_bank', ''))
            co_banks = str(row.get('co_mentioned_banks', '无'))
            title = str(row.get('标题', ''))

            for track, content in [('full', content_full), ('ctx', content_ctx)]:
                prompt = variant_prompt.format(
                    title=title,
                    content=content,
                    target_bank=target_bank,
                    co_mentioned_banks=co_banks,
                )
                for m in models:
                    tasks.append(fetch_llm_async(session, semaphore, prompt, m, idx, track))

        completed = 0
        total = len(tasks)
        report_interval = max(1, total // 10)
        t0 = time.time()

        for coro in asyncio.as_completed(tasks):
            row_idx, model_id, res_text, track = await coro
            if res_text is not None:
                results_map[row_idx][track][model_id] = res_text
            completed += 1
            if completed % report_interval == 0 or completed == total:
                elapsed = time.time() - t0
                logger.info(f"    [{variant_name}] 进度: {completed}/{total} "
                            f"({completed/total*100:.0f}%) | {elapsed:.0f}s")

    return results_map


def aggregate_variant_results(
    df: pd.DataFrame,
    results_map: dict,
    models: list,
    variant_key: str,
) -> pd.DataFrame:
    """将变体的 LLM 响应聚合为 DataFrame 列。

    为每个变体生成以下列（每轨道独立）：
        {variant_key}_verified_full/ctx    — 多数投票验证结果 (bool)
        {variant_key}_sentiment_full/ctx   — 多数投票情感标签 (str)

    Args:
        df: 样本 DataFrame。
        results_map: run_variant_llms 返回的结果。
        models: 模型配置列表。
        variant_key: 变体标识符（如 'V1_role'）。

    Returns:
        pd.DataFrame: 增加了变体列的 DataFrame。
    """
    n_parse_fail = 0
    n_total = 0

    for track in ['_full', '_ctx']:
        track_key = track.lstrip('_')  # 'full' 或 'ctx'
        v_list = []
        s_list = []

        for idx in df.index:
            model_res = results_map.get(idx, {}).get(track_key, {})
            final_v, final_s, _, _, _, _, _, _, n_fail, _ = _aggregate_track(model_res, models)
            v_list.append(final_v)
            s_list.append(final_s)
            n_parse_fail += n_fail
            n_total += len(models)

        df[f'{variant_key}_verified{track}'] = v_list
        df[f'{variant_key}_sentiment{track}'] = s_list

    fail_rate = n_parse_fail / max(n_total, 1)
    if fail_rate > 0.20:
        logger.warning(f"  [{variant_key}] API/解析失败率 {fail_rate:.1%} > 20%，该变体可能不可靠")

    df[f'{variant_key}_parse_fail_rate'] = fail_rate
    return df


# ============================================================================
# 5. 抽样与 Baseline 提取
# ============================================================================

def random_sample(df: pd.DataFrame, sample_size: int, seed: int) -> pd.DataFrame:
    """简单随机抽样（可复现）。"""
    n = min(sample_size, len(df))
    if n < sample_size:
        logger.warning(f"可用数据 {len(df)} 条 < 请求抽样数 {sample_size}，取全部 {n} 条")
    return df.sample(n=n, random_state=seed)


def extract_baseline(df_sample: pd.DataFrame) -> pd.DataFrame:
    """从样本中提取已有的双轨 LLM 判定作为 baseline (V0)。"""
    df = df_sample.copy()

    # 整体投票结果
    df['V0_baseline_verified_full'] = df['llm_verified_full']
    df['V0_baseline_verified_ctx'] = df['llm_verified_ctx']
    df['V0_baseline_sentiment_full'] = df['llm_sentiment_full']
    df['V0_baseline_sentiment_ctx'] = df['llm_sentiment_ctx']

    # 逐模型结果（用于后续分析扩展）
    for m in MODELS:
        short = m['short_name']
        for track in ['_full', '_ctx']:
            src_v = f'{short}_verified{track}'
            src_s = f'{short}_sentiment{track}'
            if src_v in df.columns:
                df[f'{short}_baseline_verified{track}'] = df[src_v]
            if src_s in df.columns:
                df[f'{short}_baseline_sentiment{track}'] = df[src_s]

    return df


# ============================================================================
# 6. 一致性指标计算（分轨道独立计算）
# ============================================================================

def compute_pairwise_consistency(
    df: pd.DataFrame,
    variant_key: str,
    track: str,
) -> dict:
    """计算单个变体 vs baseline 的逐对一致性指标。

    Args:
        df: 含 baseline 和变体列的 DataFrame。
        variant_key: 变体标识符。
        track: '_full' 或 '_ctx'。

    Returns:
        dict: {verification_agreement, sentiment_agreement, cohens_kappa_verification}
    """
    base_v = df[f'V0_baseline_verified{track}'].astype(int).values
    var_v = df[f'{variant_key}_verified{track}'].astype(int).values

    base_s = df[f'V0_baseline_sentiment{track}'].astype(str).values
    var_s = df[f'{variant_key}_sentiment{track}'].astype(str).values

    # Verification 一致率 + Cohen's κ（二分类，复用 33_ 版本）
    v_agree = np.mean(base_v == var_v)
    kappa_result = compute_cohens_kappa(base_v, var_v)

    # Sentiment 一致率（三分类简单匹配率）
    s_agree = np.mean(base_s == var_s)

    return {
        'verification_agreement': round(float(v_agree), 4),
        'sentiment_agreement': round(float(s_agree), 4),
        'cohens_kappa_verification': round(float(kappa_result['kappa']), 4),
        'observed_agreement': round(float(kappa_result['observed_agreement']), 4),
        'expected_agreement': round(float(kappa_result['expected_agreement']), 4),
    }


def compute_multivariant_consistency(
    df: pd.DataFrame,
    variant_keys: list,
    track: str,
) -> dict:
    """计算多变体整体一致性指标（Krippendorff's α + Fleiss' κ）。

    5 个编码者 = V0 baseline + 4 个变体。

    Args:
        df: 含全部变体列的 DataFrame。
        variant_keys: 变体标识符列表（不含 V0）。
        track: '_full' 或 '_ctx'。

    Returns:
        dict: {krippendorffs_alpha, fleiss_kappa}
    """
    n_items = len(df)
    all_keys = ['V0_baseline'] + variant_keys
    n_coders = len(all_keys)

    # 构建编码者 × 项目矩阵（verification 二分类）
    ratings = np.zeros((n_coders, n_items), dtype=int)
    for i, key in enumerate(all_keys):
        col = f'{key}_verified{track}'
        ratings[i, :] = df[col].astype(int).values

    # Krippendorff's α
    # 需要将 0/1 矩阵传入，-1 表示缺失（此处无缺失）
    alpha = compute_krippendorffs_alpha(ratings)

    # Fleiss' κ
    count_matrix = _build_fleiss_matrix(ratings)
    fleiss = compute_fleiss_kappa(count_matrix)

    return {
        'krippendorffs_alpha': round(float(alpha), 4),
        'fleiss_kappa': round(float(fleiss), 4),
    }


def compute_cross_variant_variance(
    df: pd.DataFrame,
    variant_keys: list,
    track: str,
) -> dict:
    """计算跨变体方差（Carlson & Burbano 2026, Figure 3 逻辑）。

    衡量不同 prompt 措辞下 true_rate 和情感分布的离散程度。
    """
    all_keys = ['V0_baseline'] + variant_keys

    true_rates = []
    sentiment_dists = {'正面': [], '中性': [], '负面': []}

    for key in all_keys:
        v_col = f'{key}_verified{track}'
        s_col = f'{key}_sentiment{track}'
        true_rate = df[v_col].astype(int).mean()
        true_rates.append(true_rate)

        s_counts = df[s_col].value_counts(normalize=True)
        for label in ['正面', '中性', '负面']:
            sentiment_dists[label].append(s_counts.get(label, 0.0))

    return {
        'true_rate_mean': round(float(np.mean(true_rates)), 4),
        'true_rate_std': round(float(np.std(true_rates)), 4),
        'true_rates': {k: round(float(v), 4) for k, v in zip(all_keys, true_rates)},
        'sentiment_std': {
            label: round(float(np.std(vals)), 4)
            for label, vals in sentiment_dists.items()
        },
    }


# ============================================================================
# 7. 报告生成
# ============================================================================

def generate_reports(
    df: pd.DataFrame,
    variant_keys: list,
    pairwise_results: dict,
    multi_results: dict,
    variance_results: dict,
    passed: bool,
    report_dir: str,
):
    """生成全部报告文件（JSON/CSV/LaTeX/PNG）。"""

    # ── 7.1 JSON 报告 ──
    json_report = {
        'stage': '39_prompt_sensitivity',
        'methodology': 'Carlson & Burbano (2026, SMJ §3.5)',
        'sample_size': len(df),
        'random_seed': RANDOM_SEED,
        'n_variants': len(variant_keys),
        'n_models': len(MODELS),
        'model_names': [m['model_name'] for m in MODELS],
        'tracks': ['full', 'ctx'],
        'thresholds': {
            'verification': PASS_THRESHOLD_VERIFICATION,
            'sentiment': PASS_THRESHOLD_SENTIMENT,
            'kappa': PASS_THRESHOLD_KAPPA,
            'alpha': PASS_THRESHOLD_ALPHA,
        },
        'passed': passed,
        'full_track': {
            'pairwise': pairwise_results.get('_full', {}),
            'multi_variant': multi_results.get('_full', {}),
            'cross_variant_variance': variance_results.get('_full', {}),
        },
        'ctx_track': {
            'pairwise': pairwise_results.get('_ctx', {}),
            'multi_variant': multi_results.get('_ctx', {}),
            'cross_variant_variance': variance_results.get('_ctx', {}),
        },
    }

    json_path = os.path.join(report_dir, 'prompt_sensitivity_results.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_report, f, ensure_ascii=False, indent=2)
    logger.info(f"  ✅ JSON 报告: {json_path}")

    # ── 7.2 CSV 逐条对比 ──
    csv_rows = []
    for track in ['_full', '_ctx']:
        track_label = track.lstrip('_')
        for vk in variant_keys:
            for idx in df.index:
                csv_rows.append({
                    'article_index': idx,
                    'track': track_label,
                    'variant': vk,
                    'baseline_verified': df.at[idx, f'V0_baseline_verified{track}'],
                    'variant_verified': df.at[idx, f'{vk}_verified{track}'],
                    'baseline_sentiment': df.at[idx, f'V0_baseline_sentiment{track}'],
                    'variant_sentiment': df.at[idx, f'{vk}_sentiment{track}'],
                    'verification_match': (
                        df.at[idx, f'V0_baseline_verified{track}'] ==
                        df.at[idx, f'{vk}_verified{track}']
                    ),
                    'sentiment_match': (
                        df.at[idx, f'V0_baseline_sentiment{track}'] ==
                        df.at[idx, f'{vk}_sentiment{track}']
                    ),
                })

    csv_df = pd.DataFrame(csv_rows)
    csv_path = os.path.join(report_dir, 'prompt_sensitivity_detail.csv')
    csv_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    logger.info(f"  ✅ CSV 逐条对比: {csv_path} ({len(csv_df)} 行)")

    # ── 7.3 LaTeX 表格 ──
    _generate_latex_table(pairwise_results, multi_results, variance_results,
                          variant_keys, len(df), report_dir)

    # ── 7.4 热力图 ──
    _generate_heatmap(df, variant_keys, report_dir)


def _generate_latex_table(
    pairwise: dict, multi: dict, variance: dict,
    variant_keys: list, n_samples: int, report_dir: str,
):
    """生成 LaTeX 表格（双轨分 Panel）。"""
    lines = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(rf"\caption{{Prompt Wording Sensitivity Analysis ($N={n_samples}$, Dual-Track)}}")
    lines.append(r"\label{tab:prompt_sensitivity}")
    lines.append(r"\begin{tabular}{lcccc}")
    lines.append(r"\hline")
    lines.append(r"Variant & Verif. Agree. & Sent. Agree. & Cohen's $\kappa_{\text{verif}}$ & Parse Fail \\")
    lines.append(r"\hline")

    for track, panel_label in [('_full', 'Panel A: Full-Text Track'),
                                ('_ctx', 'Panel B: Context-Snippet Track')]:
        lines.append(rf"\multicolumn{{5}}{{l}}{{\textit{{{panel_label} (Pairwise vs. Baseline)}}}} \\")
        for vk in variant_keys:
            pw = pairwise.get(track, {}).get(vk, {})
            va = pw.get('verification_agreement', 0) * 100
            sa = pw.get('sentiment_agreement', 0) * 100
            kp = pw.get('cohens_kappa_verification', 0)
            # 解析失败率从 df 列中无法直接获取，用 0 占位
            lines.append(rf"\quad {VARIANT_LABELS.get(vk, vk)} & {va:.1f}\% & {sa:.1f}\% & {kp:.4f} & -- \\")
        lines.append(r"\hline")

    lines.append(r"\multicolumn{5}{l}{\textit{Panel C: Multi-Variant Agreement (Full / Ctx)}} \\")
    mf = multi.get('_full', {})
    mc = multi.get('_ctx', {})
    lines.append(rf"\quad Krippendorff's $\alpha$ & \multicolumn{{4}}{{c}}{{{mf.get('krippendorffs_alpha', 0):.4f} / {mc.get('krippendorffs_alpha', 0):.4f}}} \\")
    lines.append(rf"\quad Fleiss' $\kappa$ & \multicolumn{{4}}{{c}}{{{mf.get('fleiss_kappa', 0):.4f} / {mc.get('fleiss_kappa', 0):.4f}}} \\")
    vf = variance.get('_full', {})
    vc = variance.get('_ctx', {})
    lines.append(rf"\quad Cross-Variant $\sigma$(True Rate) & \multicolumn{{4}}{{c}}{{{vf.get('true_rate_std', 0):.4f} / {vc.get('true_rate_std', 0):.4f}}} \\")
    lines.append(r"\hline")
    lines.append(r"\end{tabular}")
    lines.append(r"\par\smallskip\footnotesize")
    lines.append(r"\textit{Notes:} Baseline uses the original prompt from the production pipeline.")
    lines.append(r"Each variant modifies wording while preserving identical task semantics.")
    lines.append(r"Full track uses complete article text; Ctx track uses entity-specific context snippets.")
    lines.append(r"Methodology follows Carlson \& Burbano (2026, SMJ \S3.5).")
    lines.append(r"\end{table}")

    tex_path = os.path.join(report_dir, 'prompt_sensitivity_table.tex')
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    logger.info(f"  ✅ LaTeX 表格: {tex_path}")


def _generate_heatmap(df: pd.DataFrame, variant_keys: list, report_dir: str):
    """生成 2×1 双轨 pairwise Cohen's κ 热力图。"""
    all_keys = ['V0_baseline'] + variant_keys
    labels = ['V0 Baseline'] + [VARIANT_LABELS.get(vk, vk) for vk in variant_keys]
    n = len(all_keys)

    # 配置中文字体
    _setup_chinese_font()

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for ax_idx, (track, title_str) in enumerate([
        ('_full', 'Full Track: Pairwise κ (Verification)'),
        ('_ctx', 'Ctx Track: Pairwise κ (Verification)'),
    ]):
        kappa_matrix = np.ones((n, n))

        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                key_i = all_keys[i]
                key_j = all_keys[j]
                col_i = f'{key_i}_verified{track}'
                col_j = f'{key_j}_verified{track}'
                if col_i in df.columns and col_j in df.columns:
                    arr_i = df[col_i].astype(int).values
                    arr_j = df[col_j].astype(int).values
                    result = compute_cohens_kappa(arr_i, arr_j)
                    kappa_matrix[i, j] = result['kappa']

        ax = axes[ax_idx]
        im = ax.imshow(kappa_matrix, cmap='Blues', vmin=0.6, vmax=1.0)
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_title(title_str, fontsize=10, fontweight='bold')

        # 数值标注
        for i in range(n):
            for j in range(n):
                ax.text(j, i, f'{kappa_matrix[i, j]:.3f}',
                        ha='center', va='center', fontsize=7,
                        color='white' if kappa_matrix[i, j] > 0.85 else 'black')

        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    plt.tight_layout()
    png_path = os.path.join(report_dir, 'prompt_sensitivity_heatmap.png')
    plt.savefig(png_path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"  ✅ 热力图: {png_path}")


def _setup_chinese_font():
    """配置 matplotlib 中文字体。"""
    font_candidates = [
        'SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei',
        'Noto Sans CJK SC', 'PingFang SC', 'Heiti SC',
    ]
    for font_name in font_candidates:
        try:
            fp = font_manager.FontProperties(family=font_name)
            if fp.get_name() != font_name:
                continue
            plt.rcParams['font.sans-serif'] = [font_name]
            plt.rcParams['axes.unicode_minus'] = False
            return
        except Exception:
            continue
    # 回退
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# 8. 主流程
# ============================================================================

def main():
    """Prompt 措辞敏感度量化测试主流程。"""
    logger.info("=" * 70)
    logger.info("=== 阶段 39: Prompt 措辞敏感度量化测试 (Prompt Wording Sensitivity) ===")
    logger.info("=" * 70)
    logger.info("")
    logger.info("  📌 方法论依据")
    logger.info("     Carlson & Burbano (2026, SMJ 47(3):699–725, §3.5)")
    logger.info('     "generating families of related prompts... testing their')
    logger.info('      impact on downstream analyses"')
    logger.info("")
    logger.info("  📖 测试设计")
    logger.info(f"     变体数量: {len(VARIANT_PROMPTS)} (V1-V4) + V0 Baseline")
    logger.info(f"     抽样数量: {SAMPLE_SIZE}，随机种子: {RANDOM_SEED}")
    logger.info(f"     模型数量: {len(MODELS)}")
    logger.info(f"     测试轨道: full + ctx（双轨）")
    logger.info(f"     预计请求: {len(VARIANT_PROMPTS)} × {SAMPLE_SIZE} × {len(MODELS)} × 2 = "
                f"{len(VARIANT_PROMPTS) * SAMPLE_SIZE * len(MODELS) * 2:,} 次")
    logger.info("")
    log_memory_usage(logger, "模块启动")

    # ── 检查 enabled ──
    if not PS_CFG.get('enabled', True):
        logger.info("⏭ prompt_sensitivity_test.enabled = false，跳过本阶段")
        return

    # ── Step 1: 加载数据 ──
    logger.info("Step 1: 加载 21_tone_llms_full.parquet ...")
    input_filename = CONFIG.get('filenames', {}).get(
        'output_21_tone_llms_full', '21_tone_llms_full.parquet')
    input_path = os.path.join(CONFIG['paths']['output_dir'], input_filename)

    if not os.path.exists(input_path):
        logger.error(f"输入文件不存在: {input_path}")
        logger.error("请先运行阶段 21 (21_tone_llms.py) 生成全量 LLM 判定结果")
        return

    df_full = pd.read_parquet(input_path)
    logger.info(f"  加载 {len(df_full):,} 条记录")

    # ── Step 2: 随机抽样 ──
    logger.info(f"Step 2: 随机抽样 N={SAMPLE_SIZE}, seed={RANDOM_SEED} ...")
    df_sample = random_sample(df_full, SAMPLE_SIZE, RANDOM_SEED)
    logger.info(f"  抽样完成: {len(df_sample):,} 条")

    # ── Step 3: 提取 baseline 双轨判定 ──
    logger.info("Step 3: 提取 baseline (V0) 双轨判定 ...")
    required_cols = ['llm_verified_full', 'llm_verified_ctx',
                     'llm_sentiment_full', 'llm_sentiment_ctx']
    missing = [c for c in required_cols if c not in df_sample.columns]
    if missing:
        logger.error(f"缺少必要列: {missing}")
        return

    df_sample = extract_baseline(df_sample)
    baseline_true_rate = df_sample['V0_baseline_verified_full'].astype(int).mean()
    logger.info(f"  Baseline true_rate (full): {baseline_true_rate:.2%}")

    # ── Step 4: 物化 content_ctx（安全后备） ──
    if 'content_ctx' not in df_sample.columns:
        logger.info("Step 4: content_ctx 列缺失，执行后备物化 ...")
        _materialize = _tone_llms._materialize_content_ctx
        df_sample = _materialize(df_sample)
    else:
        logger.info("Step 4: content_ctx 列已存在，跳过物化")

    # ── Step 5: 循环 4 个变体执行双轨 LLM 请求 ──
    logger.info("Step 5: 执行变体 LLM 双轨请求 ...")
    variant_keys = list(VARIANT_PROMPTS.keys())

    for vk in variant_keys:
        logger.info(f"  ── 开始变体 {VARIANT_LABELS.get(vk, vk)} ──")
        t0 = time.time()

        results_map = asyncio.run(
            run_variant_llms(df_sample, VARIANT_PROMPTS[vk], MODELS, vk)
        )
        df_sample = aggregate_variant_results(df_sample, results_map, MODELS, vk)

        elapsed = time.time() - t0
        true_rate = df_sample[f'{vk}_verified_full'].astype(int).mean()
        logger.info(f"  ── {VARIANT_LABELS.get(vk, vk)} 完成 | "
                    f"耗时 {elapsed:.0f}s | true_rate(full): {true_rate:.2%} ──")

    # ── Step 6: 分轨道计算全部一致性指标 ──
    logger.info("Step 6: 计算一致性指标（分轨道）...")
    pairwise_results = {}
    multi_results = {}
    variance_results = {}

    for track in ['_full', '_ctx']:
        track_label = track.lstrip('_')
        logger.info(f"  ── {track_label} 轨道 ──")

        # 6.1 Pairwise
        pw = {}
        for vk in variant_keys:
            pw[vk] = compute_pairwise_consistency(df_sample, vk, track)
            logger.info(f"    {VARIANT_LABELS.get(vk, vk)}: "
                        f"v_agree={pw[vk]['verification_agreement']:.2%}, "
                        f"s_agree={pw[vk]['sentiment_agreement']:.2%}, "
                        f"κ={pw[vk]['cohens_kappa_verification']:.4f}")
        pairwise_results[track] = pw

        # 6.2 Multi-variant
        multi = compute_multivariant_consistency(df_sample, variant_keys, track)
        multi_results[track] = multi
        logger.info(f"    Multi-variant α={multi['krippendorffs_alpha']:.4f}, "
                    f"Fleiss' κ={multi['fleiss_kappa']:.4f}")

        # 6.3 Cross-variant variance
        var = compute_cross_variant_variance(df_sample, variant_keys, track)
        variance_results[track] = var
        logger.info(f"    True rate σ={var['true_rate_std']:.4f}")

    # ── Step 7: 通过/未通过判定（基于 full 轨道） ──
    logger.info("Step 7: 通过/未通过判定（基于 full 轨道）...")

    full_pw = pairwise_results['_full']
    full_multi = multi_results['_full']

    mean_v_agree = np.mean([full_pw[vk]['verification_agreement'] for vk in variant_keys])
    mean_s_agree = np.mean([full_pw[vk]['sentiment_agreement'] for vk in variant_keys])
    min_kappa = min(full_pw[vk]['cohens_kappa_verification'] for vk in variant_keys)
    alpha_val = full_multi['krippendorffs_alpha']

    criteria = {
        f'均值验证一致率 ≥ {PASS_THRESHOLD_VERIFICATION}': mean_v_agree >= PASS_THRESHOLD_VERIFICATION,
        f'均值情感一致率 ≥ {PASS_THRESHOLD_SENTIMENT}': mean_s_agree >= PASS_THRESHOLD_SENTIMENT,
        f'最小 Cohen\'s κ ≥ {PASS_THRESHOLD_KAPPA}': min_kappa >= PASS_THRESHOLD_KAPPA,
        f'Krippendorff\'s α ≥ {PASS_THRESHOLD_ALPHA}': alpha_val >= PASS_THRESHOLD_ALPHA,
    }

    passed = all(criteria.values())

    for desc, met in criteria.items():
        logger.info(f"    {'✅' if met else '❌'} {desc}")

    if passed:
        logger.info("  ✅ 判定: 通过 — Prompt 措辞改写对标注结果无实质影响")
    else:
        logger.info("  ❌ 判定: 未通过 — 部分指标低于阈值，需审查变体敏感性")

    # ── Step 8: 生成报告 ──
    logger.info("Step 8: 生成报告 ...")
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'eval_reports')
    os.makedirs(report_dir, exist_ok=True)

    generate_reports(df_sample, variant_keys, pairwise_results,
                     multi_results, variance_results, passed, report_dir)

    # ── 最终摘要 ──
    logger.info("")
    logger.info("=" * 70)
    logger.info(">>> 最终摘要 <<<")
    logger.info("=" * 70)
    logger.info(f"  样本量: {len(df_sample):,}")
    logger.info(f"  变体数: {len(variant_keys)} + baseline")
    logger.info(f"  Full 轨道:")
    logger.info(f"    均值验证一致率: {mean_v_agree:.2%}")
    logger.info(f"    均值情感一致率: {mean_s_agree:.2%}")
    logger.info(f"    最小 Cohen's κ: {min_kappa:.4f}")
    logger.info(f"    Krippendorff's α: {alpha_val:.4f}")
    logger.info(f"    Fleiss' κ: {full_multi['fleiss_kappa']:.4f}")
    logger.info(f"  判定: {'✅ PASSED' if passed else '❌ FAILED'}")
    logger.info("=" * 70)
    log_memory_usage(logger, "模块完成")


if __name__ == '__main__':
    main()
