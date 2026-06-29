"""
news_process.validation.prompt_sensitivity — Prompt 措辞敏感度量化测试

迁移说明 (Phase 7b)：
    本模块由原 root script ``70_prompt_sensitivity.py`` body 迁入。
    规范调用方式: ``python -m news_process.validation.prompt_sensitivity``

===============================================================

功能：
    通过系统性改写 Prompt 措辞（保持任务语义不变），量化 LLM 标注结果
    对 Prompt 表述选择的敏感程度。采用三轨（full + ctx + ss）测试架构，
    与 21_tone_llms.py 主流水线保持一致。

方法论依据：
    Carlson & Burbano (2026, SMJ 47(3):699–725, §3.5): "generating
    families of related prompts... testing their impact on downstream
    analyses" — Stage 5: Validation and Robustness.

变体设计原则：
    每个变体仅改变表述方式，不改变判定标准的实质内容，不改变输出
    JSON schema。一致性差异完全归因于措辞敏感度。

v7 升级（2026-05-14）：
    4 变体全面同步 v7 三阶段 schema（含 W&Z 1994/1998 ASQ substantiveness +
    Gomber 2018 JMIS locus）。每变体在自身扰动维度（V1 角色 / V2 结构 /
    V3 精简 / V4 改写）内保持 W&Z substantive-symbolic 与 Gomber
    technology-application 判定标准的实质内容不变；仅改变表述方式。

v8 升级（2026-06-11, fix(omni-g-val-prompt-02)）：
    4 变体 JSON schema 同步补齐生产 v8 (unified_cot.txt v8-2026-05-17) 第三维度
    innovation_collab_mode 三字段（Chesbrough 2003 Open Innovation +
    Laursen & Salter 2006 SMJ 自主研发 vs 外部协同），消除 baseline (v8)
    与变体 (v7) 的 schema 不一致（版本级混淆）并补上第三维度的敏感性覆盖；
    各变体仍在自身扰动维度内保持 collab 判定标准实质不变。配套接入
    PASS_THRESHOLD_INNOVATION_COLLAB_MODE 进 pass criteria（此前为死阈值）。
    同时（fix omni-g-val-prompt-01/03/04/05）：ctx/ss 轨变体 prompt 构造前剥离
    stage 13 prepend 的标题（镜像生产 tonellms-01）；pass/fail 裁决改三轨
    AND（full / ctx / ss 各自评估，JSON 报 per-track）；变体 locus 空票回退与
    生产 keyword 分类器对齐；API 全失败行加掩码不计入措辞不一致。

输入：
    阶段21输出 21_tone_llms_full.parquet（含三轨 LLM 判定列）

输出：
    eval_reports/prompt_sensitivity_results.json   — 结构化指标
    eval_reports/prompt_sensitivity_detail.csv     — 逐条对比
    eval_reports/prompt_sensitivity_table.tex      — LaTeX 表格
    eval_reports/prompt_sensitivity_heatmap.png    — κ 热力图

白话:
    担心 LLM 的判定结果是"prompt 怎么写"碰巧决定的。本检验把同一个任务
    用 4 种不同说法重写 (换角色口吻 / 换段落顺序 / 大幅精简 / 整句改写),
    意思完全不变, 再让 LLM 对同一批文章重判。如果 5 个版本 (原版+4 变体)
    给出的答案高度一致 (一致率/κ/α 全过阈值, 且 full / ctx / ss 三条轨道都要
    过), 就说明结果反映的是文章本身, 不是 prompt 措辞的偶然产物。

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 70_prompt_sensitivity.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**核心问题**: 量化 LLM 标注对 prompt 措辞选择的敏感度 — 同一任务用不同说法重写, 答案变不变。

**输入**: `21_tone_llms_full.parquet` (CONFIG['filenames']['output_21_tone_llms_full']; 含三轨 LLM 判定列, 必需列 llm_verified_full/ctx + llm_sentiment_full/ctx)。随机抽样 N=1000 (PS_CFG sample_size, seed=42)。

**处理步骤**:
1. `extract_baseline` 取 V0 (= 生产 prompt v8, PROMPT_TEMPLATE) 的三轨判定 + 三创新维度 (substantiveness/locus/collab_mode) baseline。
2. 4 个硬编码变体 VARIANT_PROMPTS: V1_role (角色改写) / V2_structure (调换前两阶段顺序+Markdown) / V3_concise (精简) / V4_paraphrase (整句改写+XML `<role>` 标签)。每变体仅改表述, 保持任务语义 + 输出 JSON schema 不变 (v8 已补齐第三维度 innovation_collab_mode 三字段, 消除 baseline v8 vs 变体 v7 的 schema 不一致)。
3. 对每变体 `run_variant_llms` 异步发三轨 × 3 模型请求; `aggregate_variant_results` 用 `_aggregate_track` 聚合 (locus 直接复用生产模块级 `_resolve_locus_track` 保证规则同源; substantiveness/collab 用 majority_vote_categorical conservative); call_failure/undefined 旗标保留。
4. 分轨算: pairwise (变体 vs V0 的验证一致率/情感一致率/Cohen's κ + 三创新维度 κ) + 多变体 (5 编码者 = V0+4 变体的 Krippendorff's α + Fleiss' κ, `compute_fleiss_kappa` 内联实现 line 472) + 跨变体方差。

**关键算法/公式**: Fleiss' κ = (P̄−P_e)/(1−P_e) 推广到 5 编码者。compute_cohens_kappa / compute_krippendorffs_alpha 复用 `validation.llms_evaluation`。失败行掩码 (fix omni-g-val-prompt-05): 变体 API 全失败行剔除, 不计为'措辞不一致'; 全失败→指标 NaN (fail-loud)。阈值: 验证一致率≥0.85 / 情感≥0.80 / κ≥0.70 / α≥0.667 / substantiveness≥0.75 / locus≥0.80 / collab≥0.70。gate = full/ctx/ss 三轨各自全 criteria AND (fix omni-g-val-prompt-03: 此前仅 full 进 gate, 而 P1 主 spec=ctx 轨, 会误报)。

**外部依赖**: LLM API, 4 变体 × 1000 × 3 模型 × 3 轨 = 最多 36000 请求; aiohttp 异步限流。确定性锚点 = `_llm_cache_validation.db` (验证变体库, LLMCache; 变体 prompt 与生产不同 → 增量付费请求, 冷缓存需线上跑)。PROMPT_MAX_RETRIES 缺省已对齐生产 MAX_RETRIES (validation.yaml 可显式取 1 防长尾卡死, 已披露)。timeout=43200s (12h)。matplotlib κ 热力图 (5 编码者 panel)。

**学术依据**: Carlson & Burbano (2026, SMJ §3.5) generating families of related prompts; 框架引 Westphal & Zajac 1994/1998 ASQ + Gomber 2018 JMIS + Chesbrough 2003 + Laursen & Salter 2006 SMJ。

■ 白话说明

**这一步在做什么**: 同一道判断题, 用 5 种不同的问法去问 AI — 原版问法, 加上换个口吻、换段落顺序、大幅精简、整句重写这 4 个变体, 意思一字不差。然后看 AI 对同一批新闻给出的 5 套答案一不一致。

**为什么需要它**: 用 AI 做研究有个隐忧: 结果会不会只是'指令 (prompt) 碰巧那么写'才出来的? 换个说法就翻盘? 这就像同一道题, 老师换个措辞问, 学生答案就全变了, 那这答案就不可靠。如果 5 个版本的答案高度一致 (各项一致率、κ、α 都过线, 而且整篇/上下文/同句三条文本轨道都要过), 就证明结果反映的是新闻本身, 不是问法的偶然产物。

**对面板和论文的影响**: 这是 AI 标注可信度的另一根支柱 (和涂名检验互补: 涂名查'是否看名字', 这里查'是否看问法')。如果 AI 判定随 prompt 措辞飘忽, 那银行-年度面板里所有 AI 派生的情感、创新属性变量都成了'问法的产物', 论文核心结论会崩。通过这一关, 才能在论文里写'我们的 LLM 标注对 prompt 措辞稳健'。它是全流水线最贵的检验 (要跑约 3.6 万次 AI 调用), 因此配了 12 小时的超长超时。
========================================================================
"""

import asyncio
import json
import os
import sys
import time

import aiohttp
import matplotlib
import numpy as np
import pandas as pd

matplotlib.use('Agg')
from importlib import import_module

import matplotlib.pyplot as plt
from matplotlib import font_manager

# Phase 7b: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 news_process/validation/prompt_sensitivity.py 出发, 上溯 2 层抵达项目父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

import platform

from news_process.core.caching import LLMCache
from news_process.core.config import load_config
from news_process.core.logging import log_memory_usage, pct4, setup_logging, sig4

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "70_prompt_sensitivity"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# Phase 7a-4: 21_tone_llms 已 thin shim 化, body 迁至 news_process.pipeline.sentiment.tone_llms
# 直接从规范包路径取内部函数, 不再走数字前缀文件名 import_module
_tone_llms = import_module('news_process.pipeline.sentiment.tone_llms')
fetch_llm_async        = _tone_llms.fetch_llm_async
_aggregate_track       = _tone_llms._aggregate_track
build_llm_connector    = _tone_llms.build_llm_connector
build_llm_timeout      = _tone_llms.build_llm_timeout
build_model_pacers     = _tone_llms.build_model_pacers
AsyncModelAvailability = _tone_llms.AsyncModelAvailability
preflight_model_availability = _tone_llms.preflight_model_availability
# 注：parse_json_response, majority_vote_bool/sentiment 由 _aggregate_track 内部调用，无需显式导入
MODELS                 = _tone_llms.MODELS
MAX_CONCURRENCY        = _tone_llms.MAX_CONCURRENCY
PROMPT_TEMPLATE        = _tone_llms.PROMPT_TEMPLATE  # V0 baseline（测试套件用于差异比对）
majority_vote_categorical = _tone_llms.majority_vote_categorical  # v7 R7.2: innov 维度跨变体一致性所需
# fix(omni-g-val-prompt-01, 2026-06-11): ctx 轨剥离 prepend 标题, 镜像生产 tonellms-01
_strip_prepended_title = _tone_llms._strip_prepended_title
# fix(omni-g-val-prompt-04, 2026-06-11): locus 空票 keyword 回退与生产 _resolve_locus_track 对齐
canonicalize_topic = _tone_llms.canonicalize_topic
# fix(omni-gapfill-18, 2026-06-12): 直接复用生产模块级 _resolve_locus_track —
# g-val-prompt-04 曾手工内联旧生产行为 (empty_fallback=keyword 硬默认), 随后
# g-tonellms-10 把生产改为零证据空票 → (None, 0.0), 两侧再度漂移。改为同一函数
# 对象后 baseline↔variant 的 locus 聚合规则永久同源 (含未来任何生产侧演进)。
_resolve_locus_track = _tone_llms._resolve_locus_track

# 复用评估模块的一致性指标
_eval = import_module('news_process.validation.llms_evaluation')
compute_cohens_kappa       = _eval.compute_cohens_kappa
compute_krippendorffs_alpha = _eval.compute_krippendorffs_alpha

# 注：content_ctx 物化由 _tone_llms._materialize_content_ctx 内部完成，
# 其依赖的 extract_entity_context/get_target_aliases 无需在此显式导入。

# 模块配置
PS_CFG = CONFIG.get('prompt_sensitivity_test', {})
SAMPLE_SIZE = PS_CFG.get('sample_size', 1000)
RANDOM_SEED = PS_CFG.get('random_seed', 42)
PROMPT_MAX_CONCURRENCY = max(1, min(MAX_CONCURRENCY, int(PS_CFG.get('max_concurrency', 20))))
PROMPT_REQUEST_SPACING = float(PS_CFG.get('request_spacing_seconds', 0.0))
PROMPT_REQUEST_TIMEOUT_SECONDS = float(
    PS_CFG.get('request_timeout_seconds', min(60.0, _tone_llms.REQUEST_TIMEOUT_TOTAL))
)
# fix(omni-g-val-prompt-05, 2026-06-11): 缺省值改为与生产 stage 21 MAX_RETRIES 对齐
# (此前缺省 1 → 变体调用失败率系统性高于 baseline)。config 显式 max_retries 仍可下调
# (validation.yaml 当前刻意取 1 防 24k 请求长尾重试卡死, 该取舍已在 YAML 注释与 JSON
# 报告 prompt_max_retries 字段中披露); 失败行另由 call_failure 掩码剔除, 不再偏置 κ。
PROMPT_MAX_RETRIES = max(1, min(
    _tone_llms.MAX_RETRIES,
    int(PS_CFG.get('max_retries', _tone_llms.MAX_RETRIES)),
))
PASS_THRESHOLD_VERIFICATION = PS_CFG.get('pass_threshold_verification', 0.85)
PASS_THRESHOLD_SENTIMENT    = PS_CFG.get('pass_threshold_sentiment', 0.80)
PASS_THRESHOLD_KAPPA        = PS_CFG.get('pass_threshold_kappa', 0.70)
PASS_THRESHOLD_ALPHA        = PS_CFG.get('pass_threshold_alpha', 0.667)
# v7 R6-B + R8-A: stage 3 阈值 (Westphal & Zajac 1994/1998 + Gomber 2018 框架)
PASS_THRESHOLD_INNOVATION_SUBSTANTIVENESS = PS_CFG.get('pass_threshold_innovation_substantiveness', 0.75)
PASS_THRESHOLD_INNOVATION_LOCUS           = PS_CFG.get('pass_threshold_innovation_locus', 0.80)
# v3.4.0: 第三维度 collab_mode 阈值 (Chesbrough 2003 + L&S 2006 SMJ)
PASS_THRESHOLD_INNOVATION_COLLAB_MODE     = PS_CFG.get('pass_threshold_innovation_collab_mode', 0.70)


def _build_prompt_llm_timeout() -> aiohttp.ClientTimeout:
    timeout_s = max(1.0, PROMPT_REQUEST_TIMEOUT_SECONDS)
    return aiohttp.ClientTimeout(
        total=timeout_s,
        connect=min(timeout_s, _tone_llms.REQUEST_TIMEOUT_CONNECT),
        sock_connect=min(timeout_s, _tone_llms.REQUEST_TIMEOUT_SOCK_CONNECT),
        sock_read=timeout_s,
    )


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

【任务三：金融科技创新属性分类】（仅当任务一判定为 true 时执行）

作为银行业数字化转型分析师，从三个并列维度刻画该报道的创新属性。

(1) 创新实质性 (innovation_substantiveness)
依据 Westphal & Zajac (1994, 1998 ASQ) substantive-vs-symbolic management 框架：该银行行动是否产生实际经济/运营后果？还是主要服务于合法性获取或印象管理而与实际行为脱钩？
- 实质性：有可独立验证的资源投入、能力建设或业务影响（产品交付、数据披露、协议落地、专利获批等）。
- 象征性：仅有战略口号、规划愿景、形式性发布、跟风式表态；或决策与行动脱钩 (decoupling)。
注: 象征性 ≠ 缺乏事实；含具体数据但纯属公关包装的发布会报道仍应判象征性。

(2) 创新位点 (innovation_locus)
依据 Gomber et al. (2018 JMIS) enabling-technology vs business-function 框架：
- 底层技术：AI、区块链、大数据、云计算等使能技术层。
- 应用场景：数字支付、开放银行、智能风控等业务功能层。

(3) 创新协作模式 (innovation_collab_mode)
依据 Chesbrough (2003) Open Innovation 与 Laursen & Salter (2006 SMJ) 框架：该银行的金融科技创新由自有资源完成，还是与外部组织协同？
- 自主研发：自建技术团队、自有研发实验室/专利/数据，内部 IT 部门主导建设，或报道明示"自研/自建/自主开发"。
- 外部协同：与金融科技公司、科技巨头、高校院所的联合研发或技术合作；收购/战略投资金融科技公司；开放银行 API 第三方接入、行业联盟、引入外部供应商技术。
注: 单纯采购通用 IT 设备不算外部协同；雇外部顾问做培训仍判自主研发；内外兼有时按报道主导事件（首段主语/标题指向）判定，不设混合类。

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
  "verification_confidence": 0.0~1.0,
  "sentiment_reason": "简明说明情感判定依据",
  "sentiment": "正面/中性/负面（false 时固定填\\"中性\\"）",
  "sentiment_confidence": 0.0~1.0,
  "innovation_substantiveness_reason": "简明说明实质/象征判定依据（false 时填 null）",
  "innovation_substantiveness": "实质性/象征性（false 时填 null）",
  "innovation_substantiveness_confidence": 0.0~1.0,
  "innovation_locus_reason": "简明说明位点判定依据（false 时填 null）",
  "innovation_locus": "底层技术/应用场景（false 时填 null）",
  "innovation_locus_confidence": 0.0~1.0,
  "innovation_collab_mode_reason": "简明说明协作模式判定依据（false 时填 null）",
  "innovation_collab_mode": "自主研发/外部协同（false 时填 null）",
  "innovation_collab_mode_confidence": 0.0~1.0
}}""",

    # ── V2: 结构重组 (Structural Variation) ──
    # 调换前两阶段顺序（先情感后验证），第三阶段创新属性紧随；去除 XML 标签、使用编号列表 + Markdown 标题
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

## 第三步：创新属性分类（仅当第二步判定为 true 时执行）

分为三个并列的属性维度：

3a. 创新实质性 (innovation_substantiveness)
判定问题：该银行行动是否产生实际经济/运营后果，还是主要服务于合法性获取与印象管理？
框架: Westphal & Zajac (1994, 1998 ASQ) substantive vs symbolic management。
1. 实质性：真实资源投入 + 可独立验证的能力建设/业务影响（产品上线、数据披露、协议落地等）。
2. 象征性：仅有战略口号 / 公关包装 / 跟风表态 / 决策行动脱钩 (decoupling)。
原则：象征性不等于缺事实；含数据但纯营销的发布会也判象征性。

3b. 创新位点 (innovation_locus)
框架: Gomber et al. (2018 JMIS) enabling-technology vs business-function。
1. 底层技术：AI、区块链、大数据、云计算等使能技术。
2. 应用场景：数字支付、开放银行、智能风控等业务功能。

3c. 创新协作模式 (innovation_collab_mode)
判定问题：该银行的金融科技创新由自有资源完成，还是与外部组织协同完成？
框架: Chesbrough (2003) Open Innovation；Laursen & Salter (2006 SMJ) search breadth & depth。
1. 自主研发：自建技术团队 / 自有研发实验室、专利、数据 / 内部 IT 部门主导 / 报道明示"自研、自建、自主开发"。
2. 外部协同：与金融科技公司、科技巨头、高校院所的联合研发或技术合作；收购或战略投资金融科技公司；开放银行 API 第三方接入 / 行业联盟 / 引入外部供应商技术。
原则：采购通用 IT 设备不算外部协同；外聘顾问培训仍判自主研发；内外兼有按报道主导事件（首段主语 / 标题指向）判定，不设混合类。

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
  "verification_confidence": 0.0~1.0,
  "sentiment_reason": "简明说明情感判定依据",
  "sentiment": "正面/中性/负面（false 时固定填\\"中性\\"）",
  "sentiment_confidence": 0.0~1.0,
  "innovation_substantiveness_reason": "简明说明实质/象征判定依据（false 时填 null）",
  "innovation_substantiveness": "实质性/象征性（false 时填 null）",
  "innovation_substantiveness_confidence": 0.0~1.0,
  "innovation_locus_reason": "简明说明位点判定依据（false 时填 null）",
  "innovation_locus": "底层技术/应用场景（false 时填 null）",
  "innovation_locus_confidence": 0.0~1.0,
  "innovation_collab_mode_reason": "简明说明协作模式判定依据（false 时填 null）",
  "innovation_collab_mode": "自主研发/外部协同（false 时填 null）",
  "innovation_collab_mode_confidence": 0.0~1.0
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

三、创新属性：仅当上述判定为 true 时，做三个二分类。
3a. 实质性 vs 象征性 (Westphal & Zajac 1994/1998 ASQ): 行动有可独立验证的经济/运营后果判实质性；仅合法性信号 / 印象管理 / decoupling 判象征性。象征性 ≠ 缺事实，含数据但纯营销也归象征性。
3b. 底层技术 vs 应用场景 (Gomber et al. 2018 JMIS): 使能技术层 (AI/区块链/大数据/云) vs 业务功能层 (数字支付/开放银行/智能风控)。
3c. 自主研发 vs 外部协同 (Chesbrough 2003; Laursen & Salter 2006 SMJ): 创新由自有资源完成 (自建团队/自有专利/内部 IT 主导) 判自主研发；外部组织实质参与 (合作研发/收购投资/开放 API 接入/联盟/引入外部技术) 判外部协同。采购通用 IT 设备或外聘顾问培训不算外部协同；内外兼有按报道主导事件判定。

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
  "verification_confidence": 0.0~1.0,
  "sentiment_reason": "简明说明情感判定依据",
  "sentiment": "正面/中性/负面（false 时固定填\\"中性\\"）",
  "sentiment_confidence": 0.0~1.0,
  "innovation_substantiveness_reason": "简明说明实质/象征判定依据（false 时填 null）",
  "innovation_substantiveness": "实质性/象征性（false 时填 null）",
  "innovation_substantiveness_confidence": 0.0~1.0,
  "innovation_locus_reason": "简明说明位点判定依据（false 时填 null）",
  "innovation_locus": "底层技术/应用场景（false 时填 null）",
  "innovation_locus_confidence": 0.0~1.0,
  "innovation_collab_mode_reason": "简明说明协作模式判定依据（false 时填 null）",
  "innovation_collab_mode": "自主研发/外部协同（false 时填 null）",
  "innovation_collab_mode_confidence": 0.0~1.0
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
抗污染指令：文中可能同时提及同行（{co_mentioned_banks}），其利好或负面与【{target_bank}】无直接关联时，一律视为噪音，不影响评分。
- `正面`：业绩增长、技术突破、创新合作、监管认可等积极事件。
- `中性`：客观陈述事实或中立行业动态，无明显褒贬。
- `负面`：风险暴露、监管处罚、安全事故、舆论危机等负面事件。
</step2_sentiment>

<step3_innovation>
**阶段三：金融科技创新属性评估**（仅当阶段一判定为 true 时执行）

本阶段对该篇报道做三项并列的创新属性研判。

**A. 实质性属性研判 (innovation_substantiveness)**

理论依据：Westphal & Zajac (1994, 1998 ASQ) 关于 substance-symbolism 的二元分类。
中心问题：该银行的金融科技行动究竟是产生**实际经济或运营后果**——抑或只是为满足合法性诉求与印象管理的表演性投射？

- `实质性`：能查证的资源投入、能力建设或业务影响（如系统部署、产品上线、数据披露、协议执行、专利落地、技术资质等）；且与该行实际经营或战略路径有据可循。
- `象征性`：仅有战略宣示、口号、目标承诺、形式性发布或跟风性表态；甚至含数据/产品却属公关包装；又或决策与实际行动相互脱钩（decoupling）。

注: `象征性` 并不要求文本缺乏事实——其关键在于行动**实质后果的有无**，而非文本信息量。

**B. 位点属性研判 (innovation_locus)**

理论依据：Gomber, Kauffman, Parker, Weber (2018 JMIS) 关于 enabling-technology 与 business-function 的层级二分。
- `底层技术`：使能技术栈层（AI、区块链、大数据、云计算、量子计算、生物识别等）。
- `应用场景`：业务功能层（数字支付、开放银行、智能风控、智能投顾、数字信贷等）。

**C. 协作模式属性研判 (innovation_collab_mode)**

理论依据：Chesbrough (2003) 开放式创新范式；Laursen & Salter (2006 SMJ 27(2):131-150) 关于外部搜索宽度与深度的论述。
中心问题：该银行的金融科技创新究竟依托**自有资源独立完成**——抑或存在**外部组织的实质性协同参与**？

- `自主研发`：依托行内自建技术团队、自有研发实验室、自有专利或数据资产完成；内部 IT 部门主导的系统建设；报道明确以"自研""自建""自主开发"为主语。
- `外部协同`：与金融科技企业、科技巨头、高校或研究机构开展联合研发或技术合作；收购金融科技子公司、战略投资、设立合资公司；开放银行 API 第三方接入、SDK、行业联盟、产业链协作；引入外部供应商技术栈或技术许可。

注: 单纯采购通用 IT 设备（服务器、办公软件）**不**构成外部协同；自建团队雇佣外部顾问做培训仍判 `自主研发`；同篇内外兼述时，按**报道主导事件**（首段主语 / 标题指向）裁定，不引入「混合」类。
</step3_innovation>

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
  "verification_confidence": 0.0~1.0,
  "sentiment_reason": "简明说明情感判定依据",
  "sentiment": "正面/中性/负面（false 时固定填\\"中性\\"）",
  "sentiment_confidence": 0.0~1.0,
  "innovation_substantiveness_reason": "简明说明实质/象征判定依据（false 时填 null）",
  "innovation_substantiveness": "实质性/象征性（false 时填 null）",
  "innovation_substantiveness_confidence": 0.0~1.0,
  "innovation_locus_reason": "简明说明位点判定依据（false 时填 null）",
  "innovation_locus": "底层技术/应用场景（false 时填 null）",
  "innovation_locus_confidence": 0.0~1.0,
  "innovation_collab_mode_reason": "简明说明协作模式判定依据（false 时填 null）",
  "innovation_collab_mode": "自主研发/外部协同（false 时填 null）",
  "innovation_collab_mode_confidence": 0.0~1.0
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
# 代码库中 63_news_llms_evaluation.py 仅有 Krippendorff's α 和 Cohen's κ（二分类）。
# Fleiss' κ 用于 n 个固定编码者对 N 个项目的多编码者名义一致性。

def compute_fleiss_kappa(ratings_matrix: np.ndarray) -> float:
    """计算 Fleiss' κ（多编码者名义一致性系数）。

    Args:
        ratings_matrix: 形状 (N_items, K_categories) 的计数矩阵，
            其中 ratings_matrix[i, j] 表示第 i 个项目被 j 类别标注的编码者数。

    Returns:
        float: Fleiss' κ 值。完全一致=1, 偶然一致=0, 系统性不一致<0。

    白话: Cohen's κ 只能比较两个编码者; 这里有 5 个"编码者" (原版 prompt
    + 4 个变体), Fleiss' κ 把"扣除碰巧一致后的一致度"推广到任意多个
    编码者同时互比。
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
# 4. LLM 三轨批量请求（自写编排，不能复用 run_all_llms）
# ============================================================================
# run_all_llms 硬编码了 PROMPT_TEMPLATE，无法传入变体 prompt。
# 本函数结构参考 66_entity_masking_test.run_masked_llms (L178-215)，
# 但增加了三轨 (full + ctx + ss) 支持。

async def run_variant_llms(
    df: pd.DataFrame,
    variant_prompt: str,
    models: list,
    variant_name: str,
    cache: LLMCache | None = None,
    model_availability: AsyncModelAvailability | None = None,
) -> dict:
    """对样本执行三轨 LLM 请求，使用指定的变体 prompt。

    Args:
        df: 样本 DataFrame，须含 '内容', 'content_ctx', 'content_ss',
            'target_bank', 'co_mentioned_banks', '标题' 列。
        variant_prompt: 变体 prompt 模板字符串。
        models: 模型配置列表。
        variant_name: 变体名称（仅用于日志）。

    Returns:
        dict: {row_idx: {'full': {...}, 'ctx': {...}, 'ss': {...}}}
    """
    semaphore = asyncio.Semaphore(PROMPT_MAX_CONCURRENCY)
    # 三轨投票桶 (full=全文 / ctx=实体窗口 / ss=银行+金科同句共现)
    results_map = {i: {'full': {}, 'ctx': {}, 'ss': {}} for i in df.index}

    # 三轨化: 任务总数 ×3 (此前 ×2)
    total_tasks = len(df) * len(models) * 3
    logger.info(
        f"  [{variant_name}] 三轨请求: {len(df)} 条 × {len(models)} 模型 × 3 轨道 = "
        f"{total_tasks:,} 请求, concurrency={PROMPT_MAX_CONCURRENCY}, "
        f"per_model_spacing={sig4(PROMPT_REQUEST_SPACING)}s, "
        f"timeout={sig4(PROMPT_REQUEST_TIMEOUT_SECONDS)}s, retries={PROMPT_MAX_RETRIES}"
    )

    connector = build_llm_connector(PROMPT_MAX_CONCURRENCY)
    request_pacers = build_model_pacers(models, PROMPT_REQUEST_SPACING)
    request_timeout = _build_prompt_llm_timeout()
    if model_availability is None:
        model_availability = AsyncModelAvailability()
    async with aiohttp.ClientSession(connector=connector, timeout=request_timeout) as session:
        await preflight_model_availability(session, models, model_availability)
        tasks = []
        for idx, row in df.iterrows():
            content_full = str(row.get('内容', ''))
            target_bank = str(row.get('target_bank', ''))
            co_banks = str(row.get('co_mentioned_banks', '无'))
            title = str(row.get('标题', ''))
            # fix(omni-g-val-prompt-01, 2026-06-11): 镜像生产 iter_article_track_prompts
            # (tonellms-01) — content_ctx 已由 stage 13 prepend 标题, 而变体模板另以
            # {title} 字段注入标题; 不剥离则变体 ctx 轨标题注入 2 次 (V0 baseline 仅
            # 1 次), baseline↔variant 差异混入双重注入噪声而非纯措辞敏感度。
            content_ctx = _strip_prepended_title(
                str(row.get('content_ctx', content_full)), title
            )
            # ss 轨同构 (content_ss 同由 stage 13 prepend 标题, 同样需剥离再由
            # {title} 字段注入 1 次); 缺列优雅回退全文 (镜像 ss_is_fallback)。
            content_ss = _strip_prepended_title(
                str(row.get('content_ss', content_full)), title
            )

            for track, content in [
                ('full', content_full),
                ('ctx', content_ctx),
                ('ss', content_ss),
            ]:
                prompt = variant_prompt.format(
                    title=title,
                    content=content,
                    target_bank=target_bank,
                    co_mentioned_banks=co_banks,
                )
                for m in models:
                    tasks.append(
                        fetch_llm_async(
                            session, semaphore, prompt, m, idx, track, cache=cache,
                            request_pacer=request_pacers.get(m['model_name']),
                            model_availability=model_availability,
                            request_timeout=request_timeout,
                            max_retries=PROMPT_MAX_RETRIES,
                        )
                    )

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
                logger.info(f"    [{variant_name}] 进度: {completed:,}/{total:,} "
                            f"({pct4(completed / total)}) | {sig4(elapsed)}s")

    return results_map


def aggregate_variant_results(
    df: pd.DataFrame,
    results_map: dict,
    models: list,
    variant_key: str,
) -> pd.DataFrame:
    """将变体的 LLM 响应聚合为 DataFrame 列。

    为每个变体生成以下列（每轨道独立 full/ctx/ss）：
        {variant_key}_verified_full/ctx/ss    — 多数投票验证结果 (bool)
        {variant_key}_sentiment_full/ctx/ss   — 多数投票情感标签 (str)
        {variant_key}_innovation_substantiveness_full/ctx/ss — W&Z 多数票
        {variant_key}_innovation_locus_full/ctx/ss — Gomber 多数票
            (生产 tone_llms._resolve_locus_track 同源聚合)
        {variant_key}_innovation_collab_mode_full/ctx/ss — Chesbrough 多数票 (v8)
        {variant_key}_call_failure_full/ctx/ss — API 全失败旗标 (一致性计算掩码用)
        {variant_key}_undefined_full/ctx/ss    — 情感平局旗标 (透明披露)

    语义变更披露: fix(omni-g-val-prompt-02/05, 2026-06-11) — 新增 collab 列;
    call_failure/undefined 旗标不再丢弃。fix(omni-gapfill-18, 2026-06-12) —
    locus 聚合改为直接 import 生产 _resolve_locus_track (零证据空票 → None,
    keyword 有真实证据时回退 keyword 类目), baseline↔variant 规则永久同源。

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

    for track in ['_full', '_ctx', '_ss']:
        track_key = track.lstrip('_')  # 'full' / 'ctx' / 'ss'
        v_list = []
        s_list = []
        innov_subst_list = []   # v7 R7.2: 创新实质性 (W&Z 1994/1998 ASQ)
        innov_locus_list = []   # v7 R7.2: 创新位点 (Gomber 2018 JMIS)
        innov_collab_list = []  # fix(omni-g-val-prompt-02): 创新协作模式 (Chesbrough 2003, v8)
        call_fail_list = []     # fix(omni-g-val-prompt-05): API 全失败旗标
        undefined_list = []     # fix(omni-g-val-prompt-05): 情感平局旗标

        for idx in df.index:
            model_res = results_map.get(idx, {}).get(track_key, {})
            (
                final_v, final_s,
                _agree_rate_v, _agree_rate_s,
                _n_valid_votes, _n_verifying_votes,
                call_failure, undefined,
                _parsed, topics, innov_loci, innov_substs,
                n_fail, _avg_prob_score,
                _avg_subst_prob_score, _avg_locus_prob_score,
                innov_collab_modes, _avg_collab_prob_score,  # v3.4.0 BREAKING: 18-tuple
            ) = _aggregate_track(model_res, models)
            v_list.append(final_v)
            s_list.append(final_s)
            # v7 R7.2: 对变体 LLM 多模型输出做 majority vote (二分类 conservative)
            innov_subst_list.append(majority_vote_categorical(
                innov_substs, tie_strategy='conservative',
                tie_default='象征性', empty_fallback=None,
            ))
            # fix(omni-gapfill-18, 2026-06-12): locus 聚合直接调用生产模块级
            # _resolve_locus_track (tone_llms.py) — 取代 g-val-prompt-04 的手工
            # 内联对齐 (该内联复制的是 g-tonellms-10 之前的旧生产行为:
            # empty_fallback=keyword 硬默认, 零证据空票也得 '应用场景')。现规则
            # 与生产逐字节同源: 空票 + keyword 零证据 → None; 空票 + keyword
            # 有真实证据 (conf>0) → keyword 类目; 有票平局 tie→'应用场景'。
            # 变体列仅存 label, confidence 弃用 (与旧实现一致)。
            _locus_label, _ = _resolve_locus_track(innov_loci, topics)
            innov_locus_list.append(_locus_label)
            # fix(omni-g-val-prompt-02, 2026-06-11): v8 第三维度 collab_mode 多数决,
            # tie/empty 策略与生产 stage 21 写回 (tone_llms.py) 完全一致。
            innov_collab_list.append(majority_vote_categorical(
                innov_collab_modes, tie_strategy='conservative',
                tie_default='自主研发', empty_fallback=None,
            ))
            call_fail_list.append(int(call_failure))
            undefined_list.append(int(undefined))
            n_parse_fail += n_fail
            n_total += len(models)

        df[f'{variant_key}_verified{track}'] = v_list
        df[f'{variant_key}_sentiment{track}'] = s_list
        df[f'{variant_key}_innovation_substantiveness{track}'] = innov_subst_list
        df[f'{variant_key}_innovation_locus{track}'] = innov_locus_list
        df[f'{variant_key}_innovation_collab_mode{track}'] = innov_collab_list
        df[f'{variant_key}_call_failure{track}'] = call_fail_list
        df[f'{variant_key}_undefined{track}'] = undefined_list

    fail_rate = n_parse_fail / max(n_total, 1)
    if fail_rate > 0.20:
        logger.info(f"  [{variant_key}] API/解析失败率 {pct4(fail_rate)} > 20%，该变体可能不可靠")

    df[f'{variant_key}_parse_fail_rate'] = fail_rate
    return df


# ============================================================================
# 5. 抽样与 Baseline 提取
# ============================================================================

def random_sample(df: pd.DataFrame, sample_size: int, seed: int) -> pd.DataFrame:
    """简单随机抽样（可复现）。"""
    n = min(sample_size, len(df))
    if n < sample_size:
        logger.info(f"可用数据 {len(df)} 条 < 请求抽样数 {sample_size}，取全部 {n} 条")
    return df.sample(n=n, random_state=seed)


def extract_baseline(df_sample: pd.DataFrame) -> pd.DataFrame:
    """从样本中提取已有的三轨 LLM 判定作为 baseline (V0)。"""
    df = df_sample.copy()

    # 整体投票结果 (full/ctx 为生产必备列; ss 镜像写法但加列存在守卫,
    # 盘上未物化 _ss 时优雅跳过, 下游 ss 轨指标自然缺席而不崩)。
    df['V0_baseline_verified_full'] = df['llm_verified_full']
    df['V0_baseline_verified_ctx'] = df['llm_verified_ctx']
    df['V0_baseline_sentiment_full'] = df['llm_sentiment_full']
    df['V0_baseline_sentiment_ctx'] = df['llm_sentiment_ctx']
    if 'llm_verified_ss' in df.columns:
        df['V0_baseline_verified_ss'] = df['llm_verified_ss']
    if 'llm_sentiment_ss' in df.columns:
        df['V0_baseline_sentiment_ss'] = df['llm_sentiment_ss']

    # v7 R7.2 / v3.2.0 (plan v14 §3.5 P5.7): V0 baseline 含 innovation 三轨独立
    # v3.2.0 BREAKING: bare innovation_* 已重命名为 _full / _ctx / _ss, 此处对应轨道独立 baseline
    for _track, _suffix in [('_full', '_full'), ('_ctx', '_ctx'), ('_ss', '_ss')]:
        src_subst = f'innovation_substantiveness{_suffix}'
        src_locus = f'innovation_locus{_suffix}'
        # fix(omni-g-val-prompt-02, 2026-06-11): v8 第三维度 collab_mode 纳入 baseline
        src_collab = f'innovation_collab_mode{_suffix}'
        if src_subst in df.columns:
            df[f'V0_baseline_innovation_substantiveness{_track}'] = df[src_subst]
        if src_locus in df.columns:
            df[f'V0_baseline_innovation_locus{_track}'] = df[src_locus]
        if src_collab in df.columns:
            df[f'V0_baseline_innovation_collab_mode{_track}'] = df[src_collab]

    # 逐模型结果（用于后续分析扩展, 三轨; src 列缺失时按列守卫优雅跳过）
    for m in MODELS:
        short = m['short_name']
        for track in ['_full', '_ctx', '_ss']:
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
        track: '_full' / '_ctx' / '_ss'。

    Returns:
        dict: {verification_agreement, sentiment_agreement, cohens_kappa_verification}

    语义变更披露: fix(omni-g-val-prompt-05, 2026-06-11) — 变体 API 全失败行
    (call_failure=1, final_v/final_s 为默认值而非真实 LLM 判定) 掩码剔除,
    不再把 API 噪声计为"措辞不一致"; 剔除量经 n_call_failures_excluded 披露。
    """
    # fix(omni-g-val-prompt-05, 2026-06-11): 失败行掩码 (旗标列缺失时向后兼容不掩码)
    fail_col = f'{variant_key}_call_failure{track}'
    n_call_failures = 0
    if fail_col in df.columns:
        ok_mask = df[fail_col].fillna(0).astype(int) == 0
        n_call_failures = int((~ok_mask).sum())
        df = df.loc[ok_mask]

    result_meta = {
        'n_compared': int(len(df)),
        'n_call_failures_excluded': n_call_failures,
    }
    if len(df) == 0:
        # 全部行均为 API 失败 → 无可比样本, 指标 NaN (fail-loud 而非伪 0/伪 1)
        return {
            'verification_agreement': float('nan'),
            'sentiment_agreement': float('nan'),
            'cohens_kappa_verification': float('nan'),
            'observed_agreement': float('nan'),
            'expected_agreement': float('nan'),
            **result_meta,
        }

    base_v = df[f'V0_baseline_verified{track}'].astype(int).values
    var_v = df[f'{variant_key}_verified{track}'].astype(int).values

    base_s = df[f'V0_baseline_sentiment{track}'].astype(str).values
    var_s = df[f'{variant_key}_sentiment{track}'].astype(str).values

    # Verification 一致率 + Cohen's κ（二分类，复用 33_ 版本）
    v_agree = np.mean(base_v == var_v)
    kappa_result = compute_cohens_kappa(base_v, var_v)

    # Sentiment 一致率（三分类简单匹配率）
    s_agree = np.mean(base_s == var_s)

    result = {
        'verification_agreement': round(float(v_agree), 4),
        'sentiment_agreement': round(float(s_agree), 4),
        'cohens_kappa_verification': round(float(kappa_result['kappa']), 4),
        'observed_agreement': round(float(kappa_result['observed_agreement']), 4),
        'expected_agreement': round(float(kappa_result['expected_agreement']), 4),
        **result_meta,
    }

    # v7 R7.2: innovation_substantiveness 维度 (仅 verified=True 子集; 二分类)
    iss_col_base = f'V0_baseline_innovation_substantiveness{track}'
    iss_col_var = f'{variant_key}_innovation_substantiveness{track}'
    if iss_col_base in df.columns and iss_col_var in df.columns:
        # 仅在 baseline + variant 都 verified=True 时比较 (innovation 在 false 时为 None)
        mask = (base_v == 1) & (var_v == 1)
        if mask.sum() >= 2:
            base_iss = df.loc[mask, iss_col_base].astype(str).values
            var_iss = df.loc[mask, iss_col_var].astype(str).values
            iss_agree = float(np.mean(base_iss == var_iss))
            # Cohen's κ for binary innovation_substantiveness (map to 0/1)
            iss_b = np.array([1 if v == '实质性' else 0 for v in base_iss])
            iss_v = np.array([1 if v == '实质性' else 0 for v in var_iss])
            iss_kappa = compute_cohens_kappa(iss_b, iss_v)
            result['innovation_substantiveness_agreement'] = round(iss_agree, 4)
            result['cohens_kappa_innovation_substantiveness'] = round(float(iss_kappa['kappa']), 4)
            result['innovation_substantiveness_n'] = int(mask.sum())
        else:
            result['innovation_substantiveness_agreement'] = float('nan')
            result['cohens_kappa_innovation_substantiveness'] = float('nan')
            result['innovation_substantiveness_n'] = int(mask.sum())

    # v7 R7.2: innovation_locus 维度 (仅 verified=True 子集; 二分类)
    il_col_base = f'V0_baseline_innovation_locus{track}'
    il_col_var = f'{variant_key}_innovation_locus{track}'
    if il_col_base in df.columns and il_col_var in df.columns:
        mask = (base_v == 1) & (var_v == 1)
        if mask.sum() >= 2:
            base_il = df.loc[mask, il_col_base].astype(str).values
            var_il = df.loc[mask, il_col_var].astype(str).values
            il_agree = float(np.mean(base_il == var_il))
            il_b = np.array([1 if v == '底层技术' else 0 for v in base_il])
            il_v = np.array([1 if v == '底层技术' else 0 for v in var_il])
            il_kappa = compute_cohens_kappa(il_b, il_v)
            result['innovation_locus_agreement'] = round(il_agree, 4)
            result['cohens_kappa_innovation_locus'] = round(float(il_kappa['kappa']), 4)
            result['innovation_locus_n'] = int(mask.sum())
        else:
            result['innovation_locus_agreement'] = float('nan')
            result['cohens_kappa_innovation_locus'] = float('nan')
            result['innovation_locus_n'] = int(mask.sum())

    # fix(omni-g-val-prompt-02, 2026-06-11): innovation_collab_mode 维度
    # (v8 第三维度, Chesbrough 2003; 仅 verified=True 子集; 二分类)
    icm_col_base = f'V0_baseline_innovation_collab_mode{track}'
    icm_col_var = f'{variant_key}_innovation_collab_mode{track}'
    if icm_col_base in df.columns and icm_col_var in df.columns:
        mask = (base_v == 1) & (var_v == 1)
        if mask.sum() >= 2:
            base_icm = df.loc[mask, icm_col_base].astype(str).values
            var_icm = df.loc[mask, icm_col_var].astype(str).values
            icm_agree = float(np.mean(base_icm == var_icm))
            icm_b = np.array([1 if v == '外部协同' else 0 for v in base_icm])
            icm_v = np.array([1 if v == '外部协同' else 0 for v in var_icm])
            icm_kappa = compute_cohens_kappa(icm_b, icm_v)
            result['innovation_collab_mode_agreement'] = round(icm_agree, 4)
            result['cohens_kappa_innovation_collab_mode'] = round(float(icm_kappa['kappa']), 4)
            result['innovation_collab_mode_n'] = int(mask.sum())
        else:
            result['innovation_collab_mode_agreement'] = float('nan')
            result['cohens_kappa_innovation_collab_mode'] = float('nan')
            result['innovation_collab_mode_n'] = int(mask.sum())

    return result


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
        track: '_full' / '_ctx' / '_ss'。

    Returns:
        dict: {krippendorffs_alpha, fleiss_kappa, n_items, n_call_failures_excluded}

    语义变更披露: fix(omni-g-val-prompt-05, 2026-06-11) — 任一变体 API 全失败的行
    剔除 (失败行 verified 是默认 False 非真实判定, 会污染 α/Fleiss κ)。
    """
    # fix(omni-g-val-prompt-05, 2026-06-11): 失败行掩码 (旗标列缺失时向后兼容不掩码)
    fail_cols = [f'{k}_call_failure{track}' for k in variant_keys
                 if f'{k}_call_failure{track}' in df.columns]
    n_excluded = 0
    if fail_cols:
        ok_mask = (df[fail_cols].fillna(0).astype(int) == 0).all(axis=1)
        n_excluded = int((~ok_mask).sum())
        df = df.loc[ok_mask]

    n_items = len(df)
    all_keys = ['V0_baseline'] + variant_keys
    n_coders = len(all_keys)

    if n_items == 0:
        # 全样本失败 → 指标 NaN (拒绝空泛 1.0)
        return {
            'krippendorffs_alpha': float('nan'),
            'fleiss_kappa': float('nan'),
            'n_items': 0,
            'n_call_failures_excluded': n_excluded,
        }

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
        'n_items': int(n_items),
        'n_call_failures_excluded': n_excluded,
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


def _min_valid_kappa(pw: dict, variant_keys: list, key: str) -> float:
    """跨变体取某 κ 指标的最小有效值 (skip None/NaN); 全无效返回 NaN。"""
    vals = []
    for vk in variant_keys:
        v = pw[vk].get(key)
        if v is None:
            continue
        if isinstance(v, float) and np.isnan(v):
            continue
        vals.append(v)
    return min(vals) if vals else float('nan')


def evaluate_track_criteria(
    pairwise_results: dict,
    multi_results: dict,
    variant_keys: list,
    track: str,
) -> tuple:
    """对单一轨道评估全部 pass criteria。

    fix(omni-g-val-prompt-03, 2026-06-11): 此前裁决仅基于 full 轨, 而 P1 主线
    main spec = llm_vote_tone_ctx (ctx 轨) — full 过而 ctx 不过时会误报通过。
    抽出单轨评估函数, 由 main() 对 full/ctx/ss 各评一次并取 AND。
    fix(omni-g-val-prompt-02, 2026-06-11): 接入 PASS_THRESHOLD_INNOVATION_COLLAB_MODE
    (v8 第三维度, 此前为从未消费的死阈值)。

    Args:
        pairwise_results: {track: {variant_key: pairwise dict}}
        multi_results: {track: multi-variant dict}
        variant_keys: 变体标识符列表。
        track: '_full' / '_ctx' / '_ss'。

    Returns:
        tuple: (criteria: dict[str, bool], summary: dict[str, float])
    """
    pw = pairwise_results[track]
    multi = multi_results[track]

    mean_v_agree = float(np.mean([pw[vk]['verification_agreement'] for vk in variant_keys]))
    mean_s_agree = float(np.mean([pw[vk]['sentiment_agreement'] for vk in variant_keys]))
    min_kappa = min(pw[vk]['cohens_kappa_verification'] for vk in variant_keys)
    alpha_val = multi['krippendorffs_alpha']

    # v7 R7.2 + W6: innovation 维度最小 Cohen's κ (skip NaN safely)
    min_iss_kappa = _min_valid_kappa(pw, variant_keys, 'cohens_kappa_innovation_substantiveness')
    min_il_kappa = _min_valid_kappa(pw, variant_keys, 'cohens_kappa_innovation_locus')
    min_icm_kappa = _min_valid_kappa(pw, variant_keys, 'cohens_kappa_innovation_collab_mode')

    criteria = {
        f'均值验证一致率 ≥ {PASS_THRESHOLD_VERIFICATION}': mean_v_agree >= PASS_THRESHOLD_VERIFICATION,
        f'均值情感一致率 ≥ {PASS_THRESHOLD_SENTIMENT}': mean_s_agree >= PASS_THRESHOLD_SENTIMENT,
        f'最小 Cohen\'s κ (verification) ≥ {PASS_THRESHOLD_KAPPA}': min_kappa >= PASS_THRESHOLD_KAPPA,
        f'Krippendorff\'s α ≥ {PASS_THRESHOLD_ALPHA}': alpha_val >= PASS_THRESHOLD_ALPHA,
        f'最小 Cohen\'s κ (innovation_substantiveness, W&Z 1994) ≥ {PASS_THRESHOLD_INNOVATION_SUBSTANTIVENESS}':
            (not np.isnan(min_iss_kappa)) and (min_iss_kappa >= PASS_THRESHOLD_INNOVATION_SUBSTANTIVENESS),
        f'最小 Cohen\'s κ (innovation_locus, Gomber 2018) ≥ {PASS_THRESHOLD_INNOVATION_LOCUS}':
            (not np.isnan(min_il_kappa)) and (min_il_kappa >= PASS_THRESHOLD_INNOVATION_LOCUS),
        f'最小 Cohen\'s κ (innovation_collab_mode, Chesbrough 2003) ≥ {PASS_THRESHOLD_INNOVATION_COLLAB_MODE}':
            (not np.isnan(min_icm_kappa)) and (min_icm_kappa >= PASS_THRESHOLD_INNOVATION_COLLAB_MODE),
    }

    summary = {
        'mean_verification_agreement': mean_v_agree,
        'mean_sentiment_agreement': mean_s_agree,
        'min_kappa_verification': float(min_kappa),
        'krippendorffs_alpha': float(alpha_val),
        'min_kappa_innovation_substantiveness': float(min_iss_kappa),
        'min_kappa_innovation_locus': float(min_il_kappa),
        'min_kappa_innovation_collab_mode': float(min_icm_kappa),
    }
    return criteria, summary


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
    passed_by_track: dict | None = None,
):
    """生成全部报告文件（JSON/CSV/LaTeX/PNG）。

    fix(omni-g-val-prompt-03, 2026-06-11): 新增可选 passed_by_track
    ({'_full': bool, '_ctx': bool, '_ss': bool}), JSON 报 per-track 裁决
    (passed_full / passed_ctx / passed_ss); 总 `passed` = 三轨 AND (由 main()
    计算)。未传时各字段为 null。
    """

    # ── 7.1 JSON 报告 ──
    json_report = {
        'stage': '70_prompt_sensitivity',
        'methodology': 'Carlson & Burbano (2026, SMJ §3.5)',
        'sample_size': len(df),
        'random_seed': RANDOM_SEED,
        'n_variants': len(variant_keys),
        'n_models': len(MODELS),
        'model_names': [m['model_name'] for m in MODELS],
        'tracks': ['full', 'ctx', 'ss'],
        'thresholds': {
            'verification': PASS_THRESHOLD_VERIFICATION,
            'sentiment': PASS_THRESHOLD_SENTIMENT,
            'kappa': PASS_THRESHOLD_KAPPA,
            'alpha': PASS_THRESHOLD_ALPHA,
            # v7 R7.2 + W6: innovation κ thresholds
            'innovation_substantiveness_kappa': PASS_THRESHOLD_INNOVATION_SUBSTANTIVENESS,
            'innovation_locus_kappa': PASS_THRESHOLD_INNOVATION_LOCUS,
            # fix(omni-g-val-prompt-02, 2026-06-11): v8 第三维度阈值接入 (原死配置)
            'innovation_collab_mode_kappa': PASS_THRESHOLD_INNOVATION_COLLAB_MODE,
        },
        # fix(omni-g-val-prompt-05, 2026-06-11): 重试策略透明披露 — 变体重试低于生产时
        # 失败率系统性更高 (失败行已掩码剔除, 见 n_call_failures_excluded)
        'prompt_max_retries': PROMPT_MAX_RETRIES,
        'production_max_retries': _tone_llms.MAX_RETRIES,
        'passed': passed,
        # fix(omni-g-val-prompt-03, 2026-06-11): per-track 裁决 — P1 主 spec 在 ctx 轨
        # (llm_vote_tone_ctx), 总判定 = full AND ctx AND ss (三轨), 不再仅 full 轨
        'passed_full': None if passed_by_track is None else bool(passed_by_track.get('_full')),
        'passed_ctx': None if passed_by_track is None else bool(passed_by_track.get('_ctx')),
        'passed_ss': None if passed_by_track is None else bool(passed_by_track.get('_ss')),
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
        # ss 轨 (银行+金科同句共现) per-track 明细
        'ss_track': {
            'pairwise': pairwise_results.get('_ss', {}),
            'multi_variant': multi_results.get('_ss', {}),
            'cross_variant_variance': variance_results.get('_ss', {}),
        },
    }

    json_path = os.path.join(report_dir, 'prompt_sensitivity_results.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_report, f, ensure_ascii=False, indent=2)
    logger.info(f"  ✅ JSON 报告: {json_path}")

    # ── 7.2 CSV 逐条对比 ──
    csv_rows = []
    for track in ['_full', '_ctx', '_ss']:
        track_label = track.lstrip('_')
        # ss 轨守卫: 盘上未物化 _ss 时 baseline 列缺席 → 跳过该轨 (镜像
        # full/ctx 始终存在的前提, 让三轨化对旧 parquet 优雅降级)。
        if f'V0_baseline_verified{track}' not in df.columns:
            continue
        for vk in variant_keys:
            # fix(omni-g-val-prompt-05, 2026-06-11): detail CSV 增加 call_failure 列
            # (旗标列缺失时向后兼容填 False)
            fail_col = f'{vk}_call_failure{track}'
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
                    'call_failure': (
                        bool(df.at[idx, fail_col]) if fail_col in df.columns else False
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
    """生成 LaTeX 表格（三轨分 Panel full/ctx/ss）。"""
    lines = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(rf"\caption{{Prompt Wording Sensitivity Analysis ($N={n_samples}$, Three-Track)}}")
    lines.append(r"\label{tab:prompt_sensitivity}")
    lines.append(r"\begin{tabular}{lcccc}")
    lines.append(r"\hline")
    lines.append(r"Variant & Verif. Agree. & Sent. Agree. & Cohen's $\kappa_{\text{verif}}$ & Parse Fail \\")
    lines.append(r"\hline")

    # 三轨 pairwise Panel: full=Panel A / ctx=Panel B / ss=Panel C (银行+金科同句)
    for track, panel_label in [('_full', 'Panel A: Full-Text Track'),
                                ('_ctx', 'Panel B: Context-Snippet Track'),
                                ('_ss', 'Panel C: Bank+FinTech Same-Sentence Track')]:
        # 盘上未物化 _ss 时该轨 pairwise dict 为空 → 跳过该 Panel (优雅降级)
        if track == '_ss' and not pairwise.get(track):
            continue
        lines.append(rf"\multicolumn{{5}}{{l}}{{\textit{{{panel_label} (Pairwise vs. Baseline)}}}} \\")
        for vk in variant_keys:
            pw = pairwise.get(track, {}).get(vk, {})
            va = pw.get('verification_agreement', 0) * 100
            sa = pw.get('sentiment_agreement', 0) * 100
            kp = pw.get('cohens_kappa_verification', 0)
            # 解析失败率从 df 列中无法直接获取，用 0 占位
            lines.append(rf"\quad {VARIANT_LABELS.get(vk, vk)} & {va:.1f}\% & {sa:.1f}\% & {kp:.4f} & -- \\")
        lines.append(r"\hline")

    # 多变体一致性 Panel D: 每指标三轨并列 (Full / Ctx / SS)
    lines.append(r"\multicolumn{5}{l}{\textit{Panel D: Multi-Variant Agreement (Full / Ctx / SS)}} \\")
    mf = multi.get('_full', {})
    mc = multi.get('_ctx', {})
    ms = multi.get('_ss', {})
    lines.append(rf"\quad Krippendorff's $\alpha$ & \multicolumn{{4}}{{c}}{{{mf.get('krippendorffs_alpha', 0):.4f} / {mc.get('krippendorffs_alpha', 0):.4f} / {ms.get('krippendorffs_alpha', 0):.4f}}} \\")
    lines.append(rf"\quad Fleiss' $\kappa$ & \multicolumn{{4}}{{c}}{{{mf.get('fleiss_kappa', 0):.4f} / {mc.get('fleiss_kappa', 0):.4f} / {ms.get('fleiss_kappa', 0):.4f}}} \\")
    vf = variance.get('_full', {})
    vc = variance.get('_ctx', {})
    vs = variance.get('_ss', {})
    lines.append(rf"\quad Cross-Variant $\sigma$(True Rate) & \multicolumn{{4}}{{c}}{{{vf.get('true_rate_std', 0):.4f} / {vc.get('true_rate_std', 0):.4f} / {vs.get('true_rate_std', 0):.4f}}} \\")
    lines.append(r"\hline")
    lines.append(r"\end{tabular}")
    lines.append(r"\par\smallskip\footnotesize")
    lines.append(r"\textit{Notes:} Baseline uses the original prompt from the production pipeline.")
    lines.append(r"Each variant modifies wording while preserving identical task semantics.")
    lines.append(r"Full track uses complete article text; Ctx track uses entity-specific context")
    lines.append(r"snippets; SS track uses bank+fintech same-sentence co-occurrence snippets.")
    lines.append(r"Methodology follows Carlson \& Burbano (2026, SMJ \S3.5).")
    lines.append(r"\end{table}")

    tex_path = os.path.join(report_dir, 'prompt_sensitivity_table.tex')
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    logger.info(f"  ✅ LaTeX 表格: {tex_path}")


def _generate_heatmap(df: pd.DataFrame, variant_keys: list, report_dir: str):
    """生成三轨 (full/ctx/ss) pairwise Cohen's κ 热力图 (一轨一列)。"""
    all_keys = ['V0_baseline'] + variant_keys
    labels = ['V0 Baseline'] + [VARIANT_LABELS.get(vk, vk) for vk in variant_keys]
    n = len(all_keys)

    # 配置中文字体
    _setup_chinese_font()

    # 三轨候选; ss 轨盘上未物化 (V0_baseline_verified_ss 列缺席) 时优雅剔除,
    # 子图数随有效轨数自适应 (镜像 full/ctx 始终存在的前提)。
    _track_titles = [
        ('_full', 'Full Track: Pairwise κ (Verification)'),
        ('_ctx', 'Ctx Track: Pairwise κ (Verification)'),
        ('_ss', 'SS Track (Bank+FinTech same-sentence): Pairwise κ (Verification)'),
    ]
    track_titles = [
        (tr, ti) for tr, ti in _track_titles
        if f'V0_baseline_verified{tr}' in df.columns
    ]
    n_panels = len(track_titles)

    fig, axes = plt.subplots(1, n_panels, figsize=(7 * n_panels, 6))
    # 单轨时 subplots 返回单 Axes, 统一成 list 便于索引。
    if n_panels == 1:
        axes = [axes]

    for ax_idx, (track, title_str) in enumerate(track_titles):
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
    # fix(log-clobber-2026-06-27): 本阶段 import 并复用 tone_llms 的 LLM-fetch/聚合
    # 函数 (fetch_llm_async / AsyncModelAvailability / preflight / _aggregate_track),
    # 它们默认经 tone_llms 模块级 "21_tone_llms" logger 落盘 → 会截断覆盖真实
    # stage 21 的 logs/21_tone_llms.log。把 tone_llms 模块 logger 重定向到本阶段
    # 自己的 logger, 借用函数日志改落 logs/70_prompt_sensitivity.log (纯日志归属,
    # golden-safe; 详见 tone_llms.redirect_module_logger 的根因说明)。
    _tone_llms.redirect_module_logger(logger)

    # fix(2026-06-19 run-check F7): 同阶段 36 — 离线确定性模式下变体 prompt 必为冷缓存,
    # 强行运行会抛大量 LLMCacheMissError + 异步未回收异常噪声。阶段 39 在线付费 only
    # (EXPECTED_NO_OUTPUT, 不写面板) → 离线优雅跳过, 在线行为不变。复用 tone_llms.LLM_OFFLINE。
    if _tone_llms.LLM_OFFLINE:
        logger.warning(
            "阶段 39 (Prompt 敏感度) 需在线 LLM 重判变体 prompt (冷缓存); "
            "NEWS_PROCESS_LLM_OFFLINE=1 离线守卫下优雅跳过 — 在线运行不受影响。"
        )
        return

    stage_start = time.time()
    # 运行期 per-phase 墙钟计时累计 (Step 1-8 各阶段, 末尾汇总; 纯日志, golden-safe)
    phase_durations: dict[str, float] = {}

    # ── ① 🧭 项目 / 环境信息 (日志富集 2026-06-24; 纯日志, 不改任何产物) ──
    try:
        logger.info("  🧭 项目 / 环境信息")
        logger.info("     · 阶段: 70_prompt_sensitivity / 阶段 39 (Prompt 措辞敏感度量化测试, "
                    "STAGES_VALIDATION; thin shim 70_prompt_sensitivity.py)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) "
                    "| 版本 v3.11.1")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'}")
        logger.info("     · 成本/确定性: 调 LLM API (变体 prompt ≠ 生产 → 增量付费请求, 冷缓存需线上跑); "
                    "确定性锚点 = _llm_cache_validation.db; NEWS_PROCESS_LLM_OFFLINE=1 时缓存 miss 抛错而非偷跑。")
        logger.info("     · 全流水线最贵检验 (最多 4 变体 × N × 3 模型 × 3 轨 请求); "
                    "validation-only, 不写 panel/parquet (EXPECTED_NO_OUTPUT)。")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境信息打印失败 (不影响处理): {e}")

    logger.info("=" * 70)
    logger.info("=== 阶段 39: Prompt 措辞敏感度量化测试 (Prompt Wording Sensitivity) ===")
    logger.info("=" * 70)
    logger.info("")
    logger.info("  📌 方法论依据 (核心方法/构念学术出处)")
    logger.info("     · 措辞敏感度框架: Carlson & Burbano (2026, SMJ 47(3):699–725, §3.5)")
    logger.info('        "generating families of related prompts... testing their')
    logger.info('         impact on downstream analyses" (Stage 5: Validation & Robustness)')
    logger.info("        → 为何用: 量化 LLM 标注对 prompt 表述选择的稳健性, 排除'问法偶然产物'")
    logger.info("     · 创新实质性维度: Westphal & Zajac (1994/1998, ASQ) substantive-vs-symbolic 框架")
    logger.info("     · 创新位点维度:   Gomber et al. (2018, JMIS) enabling-technology vs business-function")
    logger.info("     · 创新协作模式:   Chesbrough (2003) Open Innovation; Laursen & Salter (2006, SMJ 27(2):131-150)")
    logger.info("     · 一致性度量:     Cohen's κ / Krippendorff's α / Fleiss' κ (扣除碰巧一致后的真实一致度)")
    logger.info("     (注: 上述框架文献的经核验 DOI 见下方独立 📖 块; 前述'不 emit DOI'表述就此作废)")
    logger.info("")
    # round-7 富集 (2026-06-29): 把 📌 块的框架文献从作者-年-期刊升格为带经核验 DOI 的
    # 正式条目, 并补当代 prompt-敏感度 / LLM-标注稳健性锚点 (纯日志, golden-safe)。
    logger.info("  📖 方法论依据 (经 Crossref 核验 DOI; round-7 富集)")
    logger.info("     · 措辞敏感度框架 (本阶段'生成相关 prompt 家族'的直接出处): Carlson, N. A., & Burbano, V. "
                "(2026). The use of LLMs to annotate data in management research: Foundational guidelines "
                "and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023")
    logger.info("     · 创新实质性 (substantiveness 二分类构念): Westphal, J. D., & Zajac, E. J. (1994). "
                "Substance and symbolism in CEOs' long-term incentive plans. Administrative Science "
                "Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295")
    logger.info("     · 实质/象征管理 (substantive-vs-symbolic): Westphal, J. D., & Zajac, E. J. (1998). The "
                "symbolic management of stockholders: Corporate governance reforms and shareholder "
                "reactions. Administrative Science Quarterly, 43(1), 127-153. https://doi.org/10.2307/2393593")
    logger.info("     · 创新位点 (locus = 使能技术 vs 业务功能): Gomber, P., Kauffman, R. J., Parker, C., & "
                "Weber, B. W. (2018). On the fintech revolution: Interpreting the forces of innovation, "
                "disruption, and transformation in financial services. Journal of Management Information "
                "Systems, 35(1), 220-265. https://doi.org/10.1080/07421222.2018.1440766")
    logger.info("     · 创新协作模式 (collab = 自主 vs 外部协同): Laursen, K., & Salter, A. (2006). Open for "
                "innovation: The role of openness in explaining innovation performance among U.K. "
                "manufacturing firms. Strategic Management Journal, 27(2), 131-150. "
                "https://doi.org/10.1002/smj.507")
    logger.info("     · 多编码者一致性 (5 编码者 V0+V1-V4 的 Fleiss' κ 出处): Fleiss, J. L. (1971). Measuring "
                "nominal scale agreement among many raters. Psychological Bulletin, 76(5), 378-382. "
                "https://doi.org/10.1037/h0031619")
    # round-8 富集 (2026-06-29): κ 三元组 (Cohen/Krippendorff/Fleiss) 此前仅 emit Fleiss DOI;
    # Cohen κ 是本检验对 验证/情感/3 创新维度 的主要两两一致量, Krippendorff α 是 5 编码者 gate
    # 阈值量 → 补两个出处级 DOI, 凑齐第 1469 行命名的系数三元组 (纯日志, golden-safe)。
    logger.info("     · 两两名义一致 (Cohen's κ 的出处, 本检验 验证/情感/substantiveness·locus·collab 三维度成对一致度量): "
                "Cohen, J. (1960). A coefficient of agreement for nominal scales. Educational and "
                "Psychological Measurement, 20(1), 37–46. https://doi.org/10.1177/001316446002000104")
    logger.info("     · 多评分者/缺失数据信度 α (Krippendorff's α 的标准实现, 本检验 5 编码者 α≥阈值 gate 度量): "
                "Hayes, A. F., & Krippendorff, K. (2007). Answering the call for a standard reliability "
                "measure for coding data. Communication Methods and Measures, 1(1), 77–89. "
                "https://doi.org/10.1080/19312450709336664")
    logger.info("     · LLM hacking / prompt 配置敏感性风险量化 (本检验当代动机): Baumann, J., Röttger, P., "
                "Urman, A., Wendsjö, A., Plaza-del-Arco, F. M., Gruber, J. B., & Hovy, D. (2025). Large "
                "language model hacking: Quantifying the hidden risks of using LLMs for text annotation. "
                "arXiv. https://doi.org/10.48550/arXiv.2509.08825")
    logger.info("     · LLM 标注跨 prompt 可复现性 (SILICON): Cheng, X., Mayya, R., & Sedoc, J. (2024). To err "
                "is human; to annotate, SILICON? Toward robust reproducibility in LLM annotation. arXiv. "
                "https://doi.org/10.48550/arXiv.2412.14461")
    logger.info("")
    logger.info("  📖 测试设计")
    logger.info(f"     变体数量: {len(VARIANT_PROMPTS)} (V1-V4) + V0 Baseline")
    logger.info(f"     抽样数量: {SAMPLE_SIZE}，随机种子: {RANDOM_SEED}")
    logger.info(f"     模型数量: {len(MODELS)}")
    logger.info(f"     测试轨道: full + ctx + ss（三轨）")
    logger.info(f"     并发上限: {PROMPT_MAX_CONCURRENCY}")
    logger.info(f"     预计请求: {len(VARIANT_PROMPTS)} × {SAMPLE_SIZE} × {len(MODELS)} × 3 = "
                f"{len(VARIANT_PROMPTS) * SAMPLE_SIZE * len(MODELS) * 3:,} 次")
    logger.info("")

    # ── 黄金范式【功能】banner (自带说明书; 取自 PIPELINE_NUMBERED_PY_REFERENCE 白话/详细说明) ──
    logger.info("=" * 72)
    logger.info("阶段 39: Prompt 措辞敏感度量化测试 (Carlson & Burbano 2026 SMJ §3.5)")
    logger.info("=" * 72)
    logger.info("【功能】同一道判断题, 用 5 种问法 (原版 V0 + 4 变体 V1-V4) 重问 AI, 意思一字不差:")
    logger.info("        V1 换角色口吻 / V2 调段落顺序+Markdown / V3 大幅精简 / V4 整句改写+XML 标签;")
    logger.info("        看 5 套答案是否一致, 量化 LLM 标注对 prompt 措辞选择的敏感程度 (越一致越稳健)。")
    logger.info("        产出 eval_reports/{results.json, detail.csv, table.tex, heatmap.png}, 不写 parquet。")
    logger.info("【方法】三轨 (full/ctx/ss) 各自评估; 变体 vs V0 的 pairwise (验证一致率/情感一致率/Cohen's κ")
    logger.info("        + 三创新维度 κ) + 5 编码者多变体 (Krippendorff's α + Fleiss' κ=(P̄−P_e)/(1−P_e)) + 跨变体方差;")
    logger.info("        API 全失败行掩码剔除 (不计为措辞不一致), 全失败→指标 NaN (fail-loud)。")
    logger.info(
        f"【阈值】验证一致率≥{sig4(PASS_THRESHOLD_VERIFICATION)} / 情感≥{sig4(PASS_THRESHOLD_SENTIMENT)} / "
        f"κ≥{sig4(PASS_THRESHOLD_KAPPA)} / α≥{sig4(PASS_THRESHOLD_ALPHA)} / "
        f"substantiveness κ≥{sig4(PASS_THRESHOLD_INNOVATION_SUBSTANTIVENESS)} / "
        f"locus κ≥{sig4(PASS_THRESHOLD_INNOVATION_LOCUS)} / "
        f"collab κ≥{sig4(PASS_THRESHOLD_INNOVATION_COLLAB_MODE)}")
    logger.info("【判读】各指标越高=越稳健 (=好); gate = full/ctx/ss 三轨各自全 criteria AND (P1 主 spec 在 ctx 轨);")
    logger.info("        过线 → 可在论文写'LLM 标注对 prompt 措辞稳健'; 不过线 → AI 派生情感/创新变量恐成'问法的产物'。")
    logger.info("【确定性】调 LLM API (变体 prompt 与生产不同 → 增量付费请求, 冷缓存需线上跑); 确定性锚点 = _llm_cache_validation.db;")
    logger.info("          NEWS_PROCESS_LLM_OFFLINE=1 时缓存 miss 抛错而非偷跑 API。全流水线最贵检验, timeout=43200s (12h)。")
    logger.info("=" * 72)

    log_memory_usage(logger, "模块启动")

    # ── ③ ⚙ 运行配置 (config: prompt_sensitivity_test 块 + paths; 纯日志, golden-safe) ──
    try:
        _in_fn = CONFIG.get('filenames', {}).get(
            'output_21_tone_llms_full', '21_tone_llms_full.parquet')
        _in_path = os.path.join(CONFIG['paths']['output_dir'], _in_fn)
        _report_dir = os.path.join(CONFIG['paths']['output_dir'], 'eval_reports')
        logger.info("  ⚙ 运行配置 (config/validation.yaml::prompt_sensitivity_test + paths)")
        logger.info(f"     · 抽样: sample_size={SAMPLE_SIZE:,} | random_seed={RANDOM_SEED}")
        logger.info(f"     · 变体: {len(VARIANT_PROMPTS)} (V1_role/V2_structure/V3_concise/V4_paraphrase) + V0 baseline")
        logger.info(f"     · 模型: {len(MODELS)} ({', '.join(m['model_name'] for m in MODELS)}) | 轨道: full/ctx/ss (三轨)")
        logger.info(f"     · 并发: max_concurrency={PROMPT_MAX_CONCURRENCY} "
                    f"| request_spacing={sig4(PROMPT_REQUEST_SPACING)}s "
                    f"| request_timeout={sig4(PROMPT_REQUEST_TIMEOUT_SECONDS)}s")
        logger.info(f"     · 重试: prompt_max_retries={PROMPT_MAX_RETRIES} (生产 MAX_RETRIES={_tone_llms.MAX_RETRIES})")
        logger.info(f"     · 阈值: verif≥{sig4(PASS_THRESHOLD_VERIFICATION)} / sent≥{sig4(PASS_THRESHOLD_SENTIMENT)} "
                    f"/ κ≥{sig4(PASS_THRESHOLD_KAPPA)} / α≥{sig4(PASS_THRESHOLD_ALPHA)} "
                    f"/ subst κ≥{sig4(PASS_THRESHOLD_INNOVATION_SUBSTANTIVENESS)} "
                    f"/ locus κ≥{sig4(PASS_THRESHOLD_INNOVATION_LOCUS)} "
                    f"/ collab κ≥{sig4(PASS_THRESHOLD_INNOVATION_COLLAB_MODE)}")
        logger.info(f"     · 输入:   {_in_path}")
        logger.info(f"     · 输出目录: {_report_dir} (results.json / detail.csv / table.tex / heatmap.png)")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  运行配置打印失败 (不影响处理): {e}")
    logger.info("")

    # 2026-06-13: stage 39 已改为无条件 always-on (用户决策: 全部启用而非条件启用),
    # 移除 prompt_sensitivity_test.enabled 早退门; enabled flag 仅作记录, 启停由
    # core/dag.py 的 always_enabled 谓词决定。

    # ── Step 1: 加载数据 ──
    logger.info("Step 1: 加载 21_tone_llms_full.parquet ...")
    _t_load = time.time()
    input_filename = CONFIG.get('filenames', {}).get(
        'output_21_tone_llms_full', '21_tone_llms_full.parquet')
    input_path = os.path.join(CONFIG['paths']['output_dir'], input_filename)

    if not os.path.exists(input_path):
        logger.error(f"输入文件不存在: {input_path}")
        logger.error("请先运行阶段 21 (21_tone_llms.py) 生成全量 LLM 判定结果")
        return

    df_full = pd.read_parquet(input_path)
    logger.info(f"  加载 {len(df_full):,} 条记录 × {df_full.shape[1]:,} 列")
    # ── io-provenance (round-8 富集): 在阶段边界自记录三轨情感列 schema 广度,
    #    让 .log 自证输入 schema (full/ctx/ss 各 verified+sentiment); 纯日志, golden-safe ──
    try:
        _track_cols = [c for c in (
            'llm_verified_full', 'llm_verified_ctx', 'llm_verified_ss',
            'llm_sentiment_full', 'llm_sentiment_ctx', 'llm_sentiment_ss')
            if c in df_full.columns]
        logger.info(
            f"     · 三轨情感列就位: {len(_track_cols)}/6 [{', '.join(_track_cols)}]"
            if _track_cols else
            "     · 三轨情感列: 未检出 (下游 required_cols 守卫将处理)")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  输入 schema 自记录失败 (不影响处理): {e}")
    phase_durations['①加载+抽样+baseline'] = time.time() - _t_load

    # ── Step 2: 随机抽样 ──
    logger.info(f"Step 2: 随机抽样 N={SAMPLE_SIZE}, seed={RANDOM_SEED} ...")
    df_sample = random_sample(df_full, SAMPLE_SIZE, RANDOM_SEED)
    logger.info(f"  抽样完成: {len(df_sample):,} 条")

    # ── Step 3: 提取 baseline 三轨判定 ──
    logger.info("Step 3: 提取 baseline (V0) 三轨判定 ...")
    # full/ctx 为生产必备列 (缺则报错退出); ss 不列入必备 (盘上未物化 _ss 时
    # extract_baseline 已按列守卫优雅跳过, ss 轨指标自然缺席而不阻断 full/ctx)。
    required_cols = ['llm_verified_full', 'llm_verified_ctx',
                     'llm_sentiment_full', 'llm_sentiment_ctx']
    missing = [c for c in required_cols if c not in df_sample.columns]
    if missing:
        logger.error(f"缺少必要列: {missing}")
        return

    df_sample = extract_baseline(df_sample)
    baseline_true_rate = df_sample['V0_baseline_verified_full'].astype(int).mean()
    logger.info(f"  Baseline true_rate (full): {pct4(baseline_true_rate)}")
    # ── 样本基率特征 (round-8 富集): V0 baseline 情感三分类 (正面/中性/负面) 占比,
    #    审稿人常需的 base-rate 统计; 结果只喂 logger, 不参与任何下游计算 (golden-safe) ──
    try:
        _v0_sent = df_sample['V0_baseline_sentiment_full'].value_counts(normalize=True)
        _shares = " / ".join(f"{k}={pct4(v)}" for k, v in _v0_sent.items())
        logger.info(f"  Baseline (V0) 情感类占比 (full): {_shares}")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  baseline 情感占比打印失败 (不影响处理): {e}")

    # ── Step 4: 物化 content_ctx（安全后备） ──
    if 'content_ctx' not in df_sample.columns:
        logger.info("Step 4: content_ctx 列缺失，执行后备物化 ...")
        _materialize = _tone_llms._materialize_content_ctx
        df_sample = _materialize(df_sample)
    else:
        logger.info("Step 4: content_ctx 列已存在，跳过物化")
    # ss 轨安全后备: content_ss 缺列 → 回退全文 (镜像 ss_is_fallback 公理),
    # run_variant_llms 内 row.get('content_ss', content_full) 已含此回退,
    # 此处仅显式物化一份兜底列, 保证 detail/ss 轨指标有源。
    if 'content_ss' not in df_sample.columns:
        logger.info("Step 4b: content_ss 列缺失，ss 轨回退全文 (镜像 ctx 回退)")
        df_sample['content_ss'] = df_sample['内容'].astype(str)

    # ── Step 5: 循环 4 个变体执行三轨 LLM 请求 ──
    logger.info("Step 5: 执行变体 LLM 三轨请求 ...")
    _t_variants = time.time()
    variant_keys = list(VARIANT_PROMPTS.keys())

    # W4 (2026-06-25): 验证变体响应隔离到独立库 (不写生产 golden 锚点 _llm_cache.db) —
    # hygiene: 生产库 size 日志纯净 + 不因跑验证而膨胀。变体 prompt 与生产键互异, 故不影响
    # stage21 复现; 隔离仅防膨胀 (CF-14: 非"verify 计数不被稀释", 后者本就由点查免疫)。
    cache_db = os.path.join(CONFIG["paths"]["output_dir"], '_llm_cache_validation.db')
    with LLMCache(cache_db) as cache:
        logger.info(f"Prompt 敏感度 LLM 缓存: {cache.size()} 条已缓存, 路径: {cache_db}")
        model_availability = AsyncModelAvailability()

        for vk in variant_keys:
            logger.info(f"  ── 开始变体 {VARIANT_LABELS.get(vk, vk)} ──")
            t0 = time.time()

            results_map = asyncio.run(
                run_variant_llms(
                    df_sample, VARIANT_PROMPTS[vk], MODELS, vk, cache=cache,
                    model_availability=model_availability,
                )
            )
            df_sample = aggregate_variant_results(df_sample, results_map, MODELS, vk)

            elapsed = time.time() - t0
            true_rate = df_sample[f'{vk}_verified_full'].astype(int).mean()
            logger.info(f"  ── {VARIANT_LABELS.get(vk, vk)} 完成 | "
                        f"耗时 {sig4(elapsed)}s | true_rate(full): {pct4(true_rate)} ──")

    phase_durations['②变体 LLM 三轨请求 (Step 5)'] = time.time() - _t_variants

    # ── Step 6: 分轨道计算全部一致性指标 ──
    logger.info("Step 6: 计算一致性指标（分轨道）...")
    _t_metrics = time.time()
    pairwise_results = {}
    multi_results = {}
    variance_results = {}

    # 有效轨道集: full/ctx 始终在; ss 仅当变体聚合真正产出 _ss 列 (= 盘上有
    # content_ss 真同句片段或回退全文) 时纳入, 否则三轨化对旧 parquet 优雅降级。
    active_tracks = ['_full', '_ctx']
    if f'{variant_keys[0]}_verified_ss' in df_sample.columns:
        active_tracks.append('_ss')

    for track in active_tracks:
        track_label = track.lstrip('_')
        logger.info(f"  ── {track_label} 轨道 ──")

        # 6.1 Pairwise
        pw = {}
        for vk in variant_keys:
            pw[vk] = compute_pairwise_consistency(df_sample, vk, track)
            logger.info(f"    {VARIANT_LABELS.get(vk, vk)}: "
                        f"v_agree={pct4(pw[vk]['verification_agreement'])}, "
                        f"s_agree={pct4(pw[vk]['sentiment_agreement'])}, "
                        f"κ={sig4(pw[vk]['cohens_kappa_verification'])}")
        pairwise_results[track] = pw

        # 6.2 Multi-variant
        multi = compute_multivariant_consistency(df_sample, variant_keys, track)
        multi_results[track] = multi
        logger.info(f"    Multi-variant α={sig4(multi['krippendorffs_alpha'])}, "
                    f"Fleiss' κ={sig4(multi['fleiss_kappa'])}")

        # 6.3 跨变体方差 Cross-variant variance
        var = compute_cross_variant_variance(df_sample, variant_keys, track)
        variance_results[track] = var
        logger.info(f"    True rate σ={sig4(var['true_rate_std'])}")

    # ── Step 7: 通过/未通过判定（三轨 AND） ──
    # fix(omni-g-val-prompt-03, 2026-06-11): 此前仅 full 轨进 gate, 而 P1 主线
    # main spec = llm_vote_tone_ctx (ctx 轨) — full 过 ctx 不过会误报通过。
    # 改为 full / ctx / ss 各自评估全部 criteria, 总判定 = 三轨 AND, JSON 报 per-track。
    logger.info("Step 7: 通过/未通过判定（full / ctx / ss 三轨均须通过）...")
    phase_durations['③一致性指标计算 (Step 6)'] = time.time() - _t_metrics

    summary_by_track = {}
    passed_by_track = {}
    for track in active_tracks:
        track_label = track.lstrip('_')
        criteria, summary = evaluate_track_criteria(
            pairwise_results, multi_results, variant_keys, track)
        summary_by_track[track] = summary
        passed_by_track[track] = all(criteria.values())

        logger.info(f"  ── {track_label} 轨道 ──")
        for desc, met in criteria.items():
            logger.info(f"    {'✅' if met else '❌'} {desc}")
        logger.info(f"    {track_label} 轨道判定: "
                    f"{'✅ 通过' if passed_by_track[track] else '❌ 未通过'}")

    # 总判定 = 全部有效轨道 AND (full/ctx 必含, ss 物化时一并纳入)
    passed = all(passed_by_track[track] for track in active_tracks)

    if passed:
        track_names = '/'.join(t.lstrip('_') for t in active_tracks)
        logger.info(f"  ✅ 判定: 通过 ({track_names} 三轨) — Prompt 措辞改写对标注结果无实质影响")
    else:
        logger.info("  ❌ 判定: 未通过 — 至少一条轨道有指标低于阈值，需审查变体敏感性")

    # ── Step 8: 生成报告 ──
    logger.info("Step 8: 生成报告 ...")
    _t_report = time.time()
    report_dir = os.path.join(CONFIG['paths']['output_dir'], 'eval_reports')
    os.makedirs(report_dir, exist_ok=True)

    generate_reports(df_sample, variant_keys, pairwise_results,
                     multi_results, variance_results, passed, report_dir,
                     passed_by_track=passed_by_track)
    phase_durations['④报告生成 (Step 8)'] = time.time() - _t_report

    # ── 最终摘要 ──
    logger.info("")
    logger.info("=" * 70)
    logger.info(">>> 最终摘要 <<<")
    logger.info("=" * 70)
    logger.info(f"  样本量: {len(df_sample):,}")
    logger.info(f"  变体数: {len(variant_keys)} + baseline")
    for track in active_tracks:
        track_label = track.lstrip('_')
        s = summary_by_track[track]
        logger.info(f"  {track_label.capitalize()} 轨道:")
        logger.info(f"    均值验证一致率: {pct4(s['mean_verification_agreement'])}")
        logger.info(f"    均值情感一致率: {pct4(s['mean_sentiment_agreement'])}")
        logger.info(f"    最小 Cohen's κ: {sig4(s['min_kappa_verification'])}")
        logger.info(f"    Krippendorff's α: {sig4(s['krippendorffs_alpha'])}")
        logger.info(f"    Fleiss' κ: {sig4(multi_results[track]['fleiss_kappa'])}")
        logger.info(f"    轨道判定: {'✅ 通过' if passed_by_track[track] else '❌ 未通过'}")
    logger.info(f"  总判定 ({' AND '.join(t.lstrip('_') for t in active_tracks)}): "
                f"{'✅ 通过' if passed else '❌ 未通过'}")
    logger.info("=" * 70)

    # ── 黄金范式【结果分析】(逐指标对照阈值/预期方向给好-坏-临界判读) ──
    logger.info("-" * 72)
    logger.info("【结果分析】Prompt 措辞敏感度 — 5 问法 (V0+V1-V4) 答案是否一致, 越一致 = AI 标注越稳健")

    def _verdict(val: float, thr: float, *, margin: float = 0.03) -> str:
        # 临界带 = 阈值上下 margin; NaN (依赖缺失/全失败) 单独判读
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return "数据缺失(NaN)"
        if val < thr:
            return "❌ 未达阈值"
        if val < thr + margin:
            return "⚠ 临界(刚过线)"
        return "✅ 稳健"

    for track in active_tracks:
        track_label = track.lstrip('_')
        s = summary_by_track[track]
        multi = multi_results[track]
        var = variance_results[track]
        logger.info(f"  ── {track_label} 轨道 ──")
        # 1) 验证一致率: 4 变体相对 V0 的"是否金科新闻"判定一致比例
        logger.info(
            f"    均值验证一致率 = {pct4(s['mean_verification_agreement'])} "
            f"(阈值 {pct4(PASS_THRESHOLD_VERIFICATION)}) → {_verdict(s['mean_verification_agreement'], PASS_THRESHOLD_VERIFICATION)}")
        # 2) 情感一致率: 三分类(正/中/负)简单匹配率
        logger.info(
            f"    均值情感一致率 = {pct4(s['mean_sentiment_agreement'])} "
            f"(阈值 {pct4(PASS_THRESHOLD_SENTIMENT)}) → {_verdict(s['mean_sentiment_agreement'], PASS_THRESHOLD_SENTIMENT)}")
        # 3) 最小 Cohen's κ (验证): 取最差变体, 扣除碰巧一致后的真实一致度
        logger.info(
            f"    最小 Cohen's κ(verification) = {sig4(s['min_kappa_verification'])} "
            f"(阈值 {sig4(PASS_THRESHOLD_KAPPA)}) → {_verdict(s['min_kappa_verification'], PASS_THRESHOLD_KAPPA)}")
        # 4) Krippendorff's α: 5 编码者整体一致性
        logger.info(
            f"    Krippendorff's α = {sig4(s['krippendorffs_alpha'])} "
            f"(阈值 {sig4(PASS_THRESHOLD_ALPHA)}) → {_verdict(s['krippendorffs_alpha'], PASS_THRESHOLD_ALPHA)}")
        # 5) Fleiss' κ: 5 编码者多人名义一致 (与 α 互证, 越高越好, 无独立 gate 阈值)
        logger.info(
            f"    Fleiss' κ(5 编码者) = {sig4(multi['fleiss_kappa'])} (与 α 互证, 越高=越一致)")
        # 6) 三创新维度最小 κ (仅 verified=True 子集; NaN=该轨双向 verified 样本不足)
        logger.info(
            f"    最小 κ(substantiveness, W&Z 1994) = {sig4(s['min_kappa_innovation_substantiveness'])} "
            f"(阈值 {sig4(PASS_THRESHOLD_INNOVATION_SUBSTANTIVENESS)}) → "
            f"{_verdict(s['min_kappa_innovation_substantiveness'], PASS_THRESHOLD_INNOVATION_SUBSTANTIVENESS)}")
        logger.info(
            f"    最小 κ(locus, Gomber 2018) = {sig4(s['min_kappa_innovation_locus'])} "
            f"(阈值 {sig4(PASS_THRESHOLD_INNOVATION_LOCUS)}) → "
            f"{_verdict(s['min_kappa_innovation_locus'], PASS_THRESHOLD_INNOVATION_LOCUS)}")
        logger.info(
            f"    最小 κ(collab_mode, Chesbrough 2003) = {sig4(s['min_kappa_innovation_collab_mode'])} "
            f"(阈值 {sig4(PASS_THRESHOLD_INNOVATION_COLLAB_MODE)}) → "
            f"{_verdict(s['min_kappa_innovation_collab_mode'], PASS_THRESHOLD_INNOVATION_COLLAB_MODE)}")
        # 7) 跨变体 true_rate 标准差: 5 问法下"判 true 比例"的离散度, 越小越好 (措辞越不影响产出)
        logger.info(
            f"    跨变体 true_rate σ = {sig4(var['true_rate_std'])} "
            f"(越小越好; σ→0 表示措辞几乎不改变金科新闻判定比例)")
        # 8) API 全失败掩码剔除量 (透明披露; 剔除多则该轨指标基于更小有效样本)
        n_excluded = multi.get('n_call_failures_excluded', 0)
        n_items = multi.get('n_items', len(df_sample))
        if n_excluded > 0:
            logger.warning(
                f"    ⚠ {track_label} 轨: {n_excluded} 行因变体 API 全失败被掩码剔除, "
                f"有效比对样本 {n_items} 条 (失败行不计为'措辞不一致', 避免偏置 κ/α)")
        logger.info(
            f"    {track_label} 轨道判定: {'✅ 通过' if passed_by_track[track] else '❌ 未通过'}")

    # 小样本警告 (盘面 T=2 / 抽样数远小于设计 N=1000 时)
    if len(df_sample) < SAMPLE_SIZE:
        logger.info(
            f"  ⚠ 小样本: 实际抽样 {len(df_sample):,} 条 < 设计 N={SAMPLE_SIZE} "
            f"(盘面 T=2 仅验证管道正确性; κ/α 在小样本下方差大, 全量结论以 17M/T=18 实测为准)")

    # 优雅降级警告: ss 轨未纳入有效轨道集 (盘上未物化 content_ss / 变体未产出 _ss 列)
    if '_ss' not in active_tracks:
        logger.warning(
            "  ⚠ ss 轨 (银行+金科同句) 未纳入裁决: 盘上变体未产出 _ss 列 (content_ss 缺失或旧 parquet), "
            "本次仅 full/ctx 两轨进 gate (对旧 parquet 优雅降级, 非错误)")
    # 重试策略披露: 变体 max_retries 低于生产时失败率系统性偏高
    if PROMPT_MAX_RETRIES < _tone_llms.MAX_RETRIES:
        logger.info(
            f"  ⚠ 变体 max_retries={PROMPT_MAX_RETRIES} < 生产 {_tone_llms.MAX_RETRIES} "
            f"(validation.yaml 刻意下调防长尾卡死; 失败行已掩码剔除, 不偏置 κ)")

    # 总裁决判读: 三轨 AND 才算通过, 否则核心结论恐成"问法的产物"
    if passed:
        logger.info(
            "  ✅ 总判读: 全部有效轨道各项指标过线 — LLM 标注对 prompt 措辞稳健, "
            "可在论文声明'标注结果反映新闻本身而非问法偶然产物'")
    else:
        logger.info(
            "  ❌ 总判读: 至少一条轨道有指标低于阈值 — AI 派生情感/创新变量可能随措辞飘忽, "
            "须审查未过线维度/变体, 否则面板下游结论存效度风险")
    logger.info("-" * 72)

    # ── ⑥ ⏱ 阶段计时 (各主要子阶段墙钟耗时 + 总耗时; 纯日志, golden-safe) ──
    try:
        total_elapsed = time.time() - stage_start
        logger.info("  ⏱ 阶段计时 (各子阶段墙钟耗时)")
        for _phase_name, _dur in phase_durations.items():
            _share = pct4(_dur / total_elapsed) if total_elapsed > 0 else "n/a"
            logger.info(f"     · {_phase_name}: {sig4(_dur)}s ({_share})")
        logger.info(f"     · 总耗时: {sig4(total_elapsed)}s")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  阶段计时打印失败 (不影响处理): {e}")

    log_memory_usage(logger, "模块完成")


if __name__ == '__main__':
    main()
