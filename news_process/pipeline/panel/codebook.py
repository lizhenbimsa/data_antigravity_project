"""news_process.pipeline.panel.codebook — 变量代码手册自动生成模块

功能：
1. 自动生成完整的变量代码手册（Variable Codebook）
2. 包含变量名、标签、注释、数据类型、取值范围、计算公式等完整属性
3. 支持导出为 Excel、CSV、Markdown、JSON 等多种格式
4. 自动从面板数据中提取变量统计信息

v3.0.0 (v8) schema 升级 (2026-05-15):
    prompt v7 把 text_type → innovation_substantiveness (W&Z 1994/1998 ASQ
    substantive-vs-symbolic 框架); fintech_category → innovation_locus (Gomber
    et al. 2018 JMIS enabling-technology vs business-function 框架)。

    v3.0.0 (v8): 翻译层已废除. panel 列值即 LLM 原始输出, 列名后缀正名:

      _sub  -> 实质性 (substantive, W&Z 1998 ASQ)
      _symb -> 象征性 (symbolic, W&Z 1998 ASQ)     ← v6/v7 的 _desc 重命名
      _tech -> 底层技术 (enabling technology, Gomber 2018)
      _app  -> 应用场景 (business function, Gomber 2018)

    历史: v6 panel 用 _desc 命名 (Stata + papers/ + golden baseline 兼容);
    v7 引入 inline 翻译层 (tone_llms.py: 象征性→描述性); v8 (v3.0.0) 翻译层
    废除, 全局重命名 _desc → _symb 与 W&Z framework 对齐.
    详见仓库根 CHANGELOG.md 的 v3.0.0 章节.

作者: Claude Opus 4.7
日期: 2026-05-10 (v6) / 2026-05-14 (v7 schema) / 2026-05-15 (v3.0.0/v8 术语正名)
"""

from __future__ import annotations

import json
import logging
import os
import platform
import re
import sys
import time
from typing import Any, Dict, List

import pandas as pd

from news_process.core.config import load_config
from news_process.core.logging import pct4, sig4

# 互为稳健性 (2026-07-02): per-model SSOT 从 encode 单一事实源**模块级**导入 (供
# _LLM_MODEL_RE/_BERT_MODEL_RE matcher 与 _infer_source_stage 宽前缀路由用; encode↔codebook
# 无循环导入)。⚠ 勿依赖 get_variable_metadata_dict 内 :~684 的函数级局部别名导入
# (_ISS_LLM_MODELS) — 那对模块级 matcher / _infer_source_stage 不可见 → NameError。
from news_process.pipeline.panel.encode import BERT_MODELS, LLM_CLASS_SPEC, LLM_MODELS

# 初始化配置和日志
CONFIG = load_config()
logger = logging.getLogger(__name__)

# fix(omni-g-codebook-02/-09, 2026-06-11): LLM 投票阵容 notes 从 config 动态拼接
# (单一事实源 = config/sentiment.yaml::tone_llm_processing.models, 与 encode.LLM_MODELS
# 同源), 杜绝硬编码漂移 (历史硬编码 'GPT-5-nano、Gemini-3、Grok-4.1' 三个名字全错)。
_TONE_LLM_CFG = CONFIG.get('tone_llm_processing', {}).get('models', [])
_LLM_MODEL_NAMES: List[str] = [
    m.get('model_name', m.get('short_name', '?')) for m in _TONE_LLM_CFG
] or ['gpt-5.4-nano', 'gemini-3.1-flash-lite', 'deepseek-v4-flash']

# fix(omni-g-codebook-05, 2026-06-11): track 字段全卷统一枚举 (生成期断言用)
# 三轨 (third-track _ss, 2026-06-14): 加性追加 'ss' (银行+金科同句共现轨), 保留 'dual'。
# 'ss' = content_ss 物化轨 (full/ctx/ss 三轨之一); 任一 _ss 列经 _infer_track 归为 'ss'。
_ALLOWED_TRACKS = frozenset({'', 'full', 'ctx', 'ss', 'dual'})


# ============================================================================
# 1. 变量元数据定义（Variable Metadata Schema）
# ============================================================================

class VariableMetadata:
    """变量元数据类，包含变量的完整属性"""

    def __init__(
        self,
        var_name: str,
        label: str,
        description: str = "",
        data_type: str = "",
        unit: str = "",
        value_range: str = "",
        formula: str = "",
        source_stage: str = "",
        reference: str = "",
        notes: str = "",
        category: str = "",
        track: str = "",
    ):
        """初始化变量元数据

        Args:
            var_name: 变量名
            label: 变量标签（简短描述）
            description: 详细描述/注释
            data_type: 数据类型（float, int, str, bool等）
            unit: 单位（如：元、%、分等）
            value_range: 取值范围（如：[0, 1]、[-1, 1]等）
            formula: 计算公式
            source_stage: 来源阶段（如：Stage 21, Stage 46等）
            reference: 学术文献引用
            notes: 额外说明
            category: 变量类别（如：情感指标、网络指标等）
            track: 文本轨道（三轨: full/ctx/ss，ss=银行+金科同句共现）
        """
        self.var_name = var_name
        self.label = label
        self.description = description
        self.data_type = data_type
        self.unit = unit
        self.value_range = value_range
        self.formula = formula
        self.source_stage = source_stage
        self.reference = reference
        self.notes = notes
        self.category = category
        self.track = track

    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式"""
        return {
            '变量名': self.var_name,
            '标签': self.label,
            '描述': self.description,
            '数据类型': self.data_type,
            '单位': self.unit,
            '取值范围': self.value_range,
            '计算公式': self.formula,
            '来源阶段': self.source_stage,
            '学术引用': self.reference,
            '备注': self.notes,
            '变量类别': self.category,
            '文本轨道': self.track,
        }


# ============================================================================
# v3.10.0 测度变更披露: 6-词典体系 (union 5→6, plan §R1)
# ============================================================================
# L&M 2011 中文主译接成第 6 部词典后, 凡【依赖词典集合】的派生 panel 列 —— 固定 union
# 投票的 avg_msent/msent_sum/avg_pos_ratio/avg_neg_ratio + 跨词典均值 dict_avg_* —— 的
# 数值由 5 部基扩为 6 部基而回溯微变 (有意测度变更, 非 bug)。实测 (见
# scripts/audit/measure_dict_union_impact.py): Pearson r(5,6)=0.985 / 符号翻转 0.13% /
# mean msent ~3.5% 微变 → 词表覆盖改善。
# ⚠ 此披露必须落到【真实 panel 列】: 此前 _UNION_NOTE 仅绑在 article 级 msent_score_*
# 幻影列上, 而 codebook 发射门控 (`for col in panel.columns`) 只对 panel 实存列发射元数据
# → 幻影列永不进 codebook/.dta, 真正受影响的 avg_msent_*/avg_pos_ratio_*/dict_avg_* DV
# 零披露。修复 = 在 emission-loop 按列名前缀注入下列披露 (panel 驱动, 覆盖全部变体)。
_DICT6_DISCLOSURE_NOTE = (
    'v3.10.0 测度变更: 本列依赖词典法词典集合; 新增第 6 部 Loughran-McDonald (2011, JF) '
    '中文主译本使词表由 5 部扩为 6 部 (固定 union 投票基 / 跨词典均值基), 致本列回溯微变 '
    '(r=0.985 / 符号翻转 0.13% / mean msent ~3.5%), 反映词表覆盖改善非方法误。'
    '见 scripts/audit/measure_dict_union_impact.py 与论文稳健性披露。'
)
_DICT6_CITATION = ('Loughran & McDonald (2011, JF); Tetlock (2007, JF); Garcia (2013, JF)')
_DICT6_MARKER = 'v3.10.0 测度变更'  # 幂等注入守卫 (备注已含则不重复追加)
_AUTO_INFER_NOTE = '自动推断的元数据，需要人工审核'  # 与 emission-loop fallback 备注同字面
# 6-词典扩张 (5→6) 回溯改变【数值】的真实 panel 列前缀: union 投票 DV +
# 跨词典均值族 (dict_avg_tone/idf/negonly + app/tech/vw/mw/hw/sum/std/_z 全变体)。
# 不匹配 per-dict 新增列 (avg_loughran_pos_ratio 等 = 新增列非"变值", 走 provenance 另标)。
_DICT6_AFFECTED_RE = re.compile(
    r'^(?:avg_msent|msent_sum|avg_pos_ratio|avg_neg_ratio|dict_avg_'
    r'|disag_(?:full|ctx|ss)$'              # 跨词典 Dict-Avg 分歧 (非 per-method disag_jiang_*/disag_bert_*)
    r'|washing_ratio_dict(?:_ctx|_ss)?$)'   # 跨词典 Dict-Avg 洗稿率 (非 per-dict washing_ratio_bian_*)
)


def _is_dict6_union_affected(col: str) -> bool:
    """col 是否为 6-词典扩张 (union 5→6 / 跨词典均值 5→6) 回溯改变数值的真实 panel 列。"""
    return bool(_DICT6_AFFECTED_RE.match(col))


# --- LM 第 6 部主词典 + 6 非情感子集 provenance (plan §Tier-1.2 / §注册:164) ---
# loughran_* 全列族 (第 6 部主情感词典: tone/negonly/idf/score/washing_ratio/disag/cater/
# pos_neg_ratio 等) 与 6 个非情感子集 frac (原 uncert/litig/constr/modal_strong + 新
# modal_weak/complexity) 是【新增/扩展】列, 非"变值"列。.dta 标签经 stata_export.py
# HEURISTIC_LABELS 已带 L&M provenance, 但 codebook 此前走 auto-infer → 学术引用为空、
# 备注='需人工审核'。此处按列名补 L&M 引文 + provenance 备注 (panel 驱动, 含 negonly 红线标注)。
_LM_PROVENANCE_CITATION = 'Loughran & McDonald (2011, JF); 中文主译本 (2026)'
_LM_PROVENANCE_NOTE = (
    'Loughran-McDonald (2011, JF) 金融情感词表中文主译本 (v3.10.0 接入第 6 部主词典 + '
    'weak_modal/complexity 非情感子集 + _ss 三轨)。'
)
_LM_NEGONLY_NOTE = ' negonly = rule-reduced L&M (仅否定规则 ≈ L&M 原版纯计数 baseline; 见 plan §Tier-1.2)。'
_LM_SUBSET_FRAC_RE = re.compile(r'^(uncert|litig|constr|modal_strong|modal_weak|complexity)_frac')


def _is_lm_provenance_col(col: str) -> bool:
    """col 是否为 L&M 词表派生的新增/扩展列 (第 6 部主词典全列族 + 6 子集 frac), 需补 provenance。"""
    return ('loughran' in col) or bool(_LM_SUBSET_FRAC_RE.match(col))


# --- 规则消融梯度 (rule-ablation ladder, v3.11.1) codebook provenance / MATH-1 披露 ---
# panel 列 {dict}_{suffix}_tone{track}: 逐 token 状态机三规则 (否定窗口 / 程度副词六级权重 /
# 转折增强) 的**全 powerset** 组合在 bank-year 的均值。计数口径 msent 不入梯度 (程度/转折严格
# 正乘子、永不翻号 → 退化)。变体语义单一事实源 = tone_words._RULE_ABLATION_VARIANTS。
_RULE_ABLATION_SFX_DESC = {
    'raw':     '零规则基线 (无否定/程度/转折)',
    'negonly': '仅否定翻转 (≈ L&M 纯计数 baseline)',
    'degonly': '仅程度六级加权',
    'advonly': '仅转折增强',
    'negdeg':  '否定+程度 (= full − 转折)',
    'negadv':  '否定+转折 (= full − 程度)',
    'degadv':  '程度+转折 (= full − 否定)',
}
# group(1) 含 'dict_avg' = 跨 6 词典均值的消融梯度 (geography.py dict_avg_{sfx}_tone, v3.11.1);
# 其余 = per-dict {d}_{sfx}_tone (encode.py)。两者同享 rule-specific 标签 + MATH-1 披露。
_RULE_ABLATION_RE = re.compile(
    r'^(jiang_2021|yao_2021|bian_2021|du_2022|you_2018|loughran|dict_avg)_'
    r'(raw|negonly|degonly|advonly|negdeg|negadv|degadv)_tone(?:_(?:full|ctx|ss))?$')
_RULE_ABLATION_CITATION = ('Kennedy & Inkpen (2006); Ding, Liu & Yu (2008); '
                           'Taboada et al. (2011); Loughran & McDonald (2011, JF)')
_RULE_ABLATION_NOTE = (
    '规则消融梯度变体 (v3.11.1): 状态机三规则 (否定窗口 / 程度副词六级权重 / 转折增强) 的 powerset '
    '组合在 bank-year 的均值, 各变体独立 Σ|final| 自归一化。⚠ 非可加分解 (audit MATH-1): 相邻级差含 '
    'negation×degree 交互 + 自归一化分母变更 → 仅作"主结果对每条规则是否敏感"的稳健性对照 (定性不变), '
    '不可解读为某规则纯贡献; 计数口径 msent 不入梯度 (程度/转折不翻号)。'
)


def _rule_ablation_match(col: str):
    """返回 (dict_name, suffix) 若 col 为规则消融梯度 panel 列 ({d}_{sfx}_tone{track}), 否则 None。"""
    m = _RULE_ABLATION_RE.match(col)
    return (m.group(1), m.group(2)) if m else None


# panel 列 du_2022_{polw*}_tone{track}: 政治词权重敏感性 (political-weight sensitivity, v3.15.x)。
# Du et al. (2022, RoF) political_positive 生产口径 0.5 权重计入正侧; 0.5 为研究者选择, 故并排
# 物化权重 ∈ {0.0,0.5,1.0} 三者互为稳健性、不分主次 (polw05 ≡ canonical du_2022_tone)。变体语义
# 单一事实源 = tone_words.POLITICAL_WEIGHT_VARIANTS。⚠ 三权重禁混同一 over-identified Hansen J。
_POLITICAL_WEIGHT_SFX_DESC = {
    'polw00': '政治词权重 0.0 (剔除政治正面词)',
    'polw05': '政治词权重 0.5 (Du et al. 2022 弱信号折中; ≡ canonical)',
    'polw10': '政治词权重 1.0 (政治正面词全权正侧)',
}
_POLITICAL_WEIGHT_RE = re.compile(
    r'^(du_2022)_(polw00|polw05|polw10)_tone(?:_(?:full|ctx|ss))?$')
_POLITICAL_WEIGHT_CITATION = ('Du, Huang, Wermers & Wu (2022, Review of Finance, '
                              'doi:10.1093/rof/rfab036)')
_POLITICAL_WEIGHT_NOTE = (
    '政治词权重敏感性 (du_2022 特有 political_positive): 依据 Du et al. (2022, RoF) 政治正面词'
    '信号弱于普通正面词, 生产口径以 0.5 权重计入正侧; 0.5 为研究者选择, 故做敏感性检验 — 权重 '
    '∈ {0.0, 0.5, 1.0} 的 bank-year 均值三者互为稳健性、不分主次 (polw05 ≡ du_2022_tone), 证明主'
    '结论不被这一取值驱动。与规则消融梯度正交不交叉。⚠ 三权重禁混同一 over-identified Hansen J。'
)


def _political_weight_match(col: str):
    """返回 (dict_name, suffix) 若 col 为政治词权重敏感性 panel 列 (du_2022_{polw*}_tone{track}), 否则 None。"""
    m = _POLITICAL_WEIGHT_RE.match(col)
    return (m.group(1), m.group(2)) if m else None


# panel 列 per-model 语调 (per-model robustness, 2026-07-02): LLM 三家 / BERT 三模型 co-equal
# 互为稳健、不分主次 (llm_vote_tone = 共识 canonical headline; BERT 无 ensemble headline)。
# SSOT = encode.LLM_MODELS / BERT_MODELS (模块顶部导入)。metric 全集 + 可选加权臂 (_vw/_mw/_hw)
# + 可选轨; 锚定 (^model_) 天然排除 llm_vote_* (不以模型名开头) 与 {short}_tone_sub/_symb
# (metric alternation 不含 tone_sub/tone_symb)。⚠ 各自 just-identified 并排, 禁混同一 over-identified
# Hansen J。metric 按 longest-first 排列避免 alternation 短匹配截断。
_LLM_MODEL_RE = re.compile(
    r'^(' + '|'.join(re.escape(m) for m in LLM_MODELS)
    + r')_(cont_mean|cont_sum|tone_sum|tone_std|tone|'
    # per-model 分类维度 frac (2026-07-03, ROBUSTNESS_GAP_BACKFILL §2 A4): metric 由
    # encode.LLM_CLASS_SPEC 值[0] 派生 (sub_frac/tech_frac/collab_frac), 与 tone 族同 matcher
    # (weight 可选组保持同一覆盖域; 面板不产加权分类列, 多余覆盖无害)。
    + '|'.join(re.escape(v[0]) for v in LLM_CLASS_SPEC.values())
    + r')((?:_(?:vw|mw|hw))?)(?:_(?:full|ctx|ss))?$')
# per-model 分类 frac metric 集 (文案分流用: tone/cont 族 → 「语调」, frac 族 → 「分类占比」)
_LLM_CLASS_METRICS = frozenset(v[0] for v in LLM_CLASS_SPEC.values())
_BERT_MODEL_RE = re.compile(
    r'^(' + '|'.join(re.escape(m) for m in BERT_MODELS)
    + r')_(net_tone|pos_sum|pos_std|neg_sum|neu_sum|pos|neg|neu)((?:_(?:vw|mw|hw))?)(?:_(?:full|ctx|ss))?$')
_PER_MODEL_HANSEN_NOTE = ('各自 just-identified 并排, 禁混同一 over-identified Hansen J '
                          '(与三轨 / co-primary 嵌入 / 政治词权重梯度同款铁律)')
_LLM_MODEL_NOTE = (
    'LLM 逐模型语调 (per-model robustness): 三家大模型 (gpt54nano/gemini31/deepseekv4) 的 bank-year '
    '语调, 与投票共识 llm_vote_tone (canonical headline) co-equal 互为稳健性、不分主次, 证明主结论'
    '不被任一厂商模型驱动 (Wang et al. 2023 self-consistency 多模型三角验证)。⚠ 三家' + _PER_MODEL_HANSEN_NOTE + '。'
)
_BERT_MODEL_NOTE = (
    'BERT 逐模型情感 (per-model robustness): 三个中文金融 BERT (finbert_cn/fin_sent_zh/finbert2) 的 '
    'bank-year 概率/net_tone, co-equal 互为稳健性、不分主次 (无 ensemble headline); per-model 独立降级 '
    '(finbert2 缺席仅掉自身族)。⚠ 三模型' + _PER_MODEL_HANSEN_NOTE + '。'
)
_LLM_MODEL_CITATION = 'Wang et al. (2023) LLM self-consistency; 多模型三角验证 (Denzin 2017)'
_BERT_MODEL_CITATION = 'Araci (2019) FinBERT; 多模型三角验证 (Denzin 2017)'
_PER_MODEL_METRIC_ZH = {
    'tone': '语调均值', 'tone_sum': '语调总和', 'tone_std': '语调离散', 'cont_mean': '连续分均值',
    'cont_sum': '连续分总和', 'net_tone': 'net-tone (正−负)', 'pos': '正面概率', 'neg': '负面概率',
    'neu': '中性概率', 'pos_sum': '正面概率和', 'neg_sum': '负面概率和', 'neu_sum': '中性概率和',
    'pos_std': '正面概率离散',
    # per-model 分类维度 frac (2026-07-03 §2 A4; 与 LLM_CLASS_SPEC 值[0] byte-sync)
    'sub_frac': '实质创新占比', 'tech_frac': '底层技术占比', 'collab_frac': '外部协同占比',
}
_LLM_CLASS_NOTE = (
    'LLM 逐模型分类占比 (per-model robustness, 2026-07-03): 三家大模型各自的分类维度 frac '
    '(分母=该模型自身 verified 篇数, 非共识 n_articles_llm_valid; 文章级存档不门控、门控在 encode 层), '
    '与共识 sub_frac/tech_frac/collab_frac (canonical headline) co-equal 互为稳健性、不分主次, '
    '证明分类结论不被任一厂商模型驱动。⚠ 三家' + _PER_MODEL_HANSEN_NOTE + '。'
)
_PER_MODEL_WEIGHT_ZH = {'': '', '_vw': ' [市值加权]', '_mw': ' [媒体加权]', '_hw': ' [羊群加权]'}


def _llm_model_match(col: str):
    """返回 (model, metric, weight_tail) 若 col 为 LLM 逐模型 panel 列, 否则 None。
    锚定 ^model_ 排除 llm_vote_* (不以模型名开头) 与 {short}_tone_sub/_symb (metric 不含)。"""
    m = _LLM_MODEL_RE.match(col)
    return (m.group(1), m.group(2), m.group(3)) if m else None


def _bert_model_match(col: str):
    """返回 (model, metric, weight_tail) 若 col 为 BERT 逐模型 panel 列, 否则 None。"""
    m = _BERT_MODEL_RE.match(col)
    return (m.group(1), m.group(2), m.group(3)) if m else None


# ============================================================================
# 2. 变量元数据字典（完整版）
# ============================================================================

def get_variable_metadata_dict() -> Dict[str, VariableMetadata]:
    """获取完整的变量元数据字典

    包含所有变量的详细属性：
    - 变量名、标签、描述
    - 数据类型、单位、取值范围
    - 计算公式、来源阶段、学术引用
    """
    metadata = {}

    # ═══ 主键变量 ═══
    # fix(omni-g-codebook-06/-14, 2026-06-11): 取值范围不再硬编码 '42家商业银行'
    # (盘上实测 87 家, 同行 唯一值数 字段自相矛盾) — 生成时由
    # generate_codebook::_apply_dynamic_value_ranges 从 panel nunique 动态覆盖,
    # 此处仅作 panel 缺列时的 fallback 文案。
    metadata['target_bank'] = VariableMetadata(
        var_name='target_bank',
        label='Target Bank',
        description='目标银行名称（标准化后的银行全称）',
        data_type='str',
        unit='',
        value_range='商业银行标准化全称 (家数生成时从 panel 动态实测)',
        formula='',
        source_stage='Stage 11',
        reference='',
        notes='面板数据的银行维度主键',
        category='主键',
        track='',
    )

    # fix(omni-g-codebook-01/-08, 2026-06-11): year 取值范围不再硬编码 '[2013, 2023]'
    # (盘上实际 2017–2018, 全量语料 2007–2024, 两种口径下都错) — 生成时动态覆盖。
    metadata['year'] = VariableMetadata(
        var_name='year',
        label='Year',
        description='年份',
        data_type='int',
        unit='年',
        value_range='生成时从 panel 动态实测 (min–max)',
        formula='',
        source_stage='Stage 11',
        reference='',
        notes='面板数据的时间维度主键',
        category='主键',
        track='',
    )

    # ═══ 注意力指数 ═══
    # metric-audit 2026-06-02 (attention_media-01 codebook 三项更正):
    #   原 formula/range/source 三项均与 attention_media.py:279 实现不符 —
    #   实际 ft_attn_yr = 当年 fintech 文章数 / 当年全部唯一文章数 (一个比率),
    #   不是 "ln(1+n_articles)×exp(-distance_decay)"; 值域 [0,1] 非 [0,+∞);
    #   无任何距离衰减 (距离衰减仅用于 ft_attn_prov/city 的地理变体); 在
    #   panel encode (compute_fintech_attention_index) 物化而非 Stage 24。
    metadata['ft_attn_yr'] = VariableMetadata(
        var_name='ft_attn_yr',
        label='Fintech Attention Index (Year)',
        description='年度金融科技注意力强度 = 当年金融科技新闻占当年全部唯一文章的比例 '
                    '(year-level 常量, 同年所有 bank 取同值)',
        data_type='float',
        unit='比率',
        value_range='[0, 1]',
        formula='fintech_articles / total_articles  '
                '(按 docid 去重后, 当年 is_fintech_news==True 篇数 / 当年全部唯一篇数)',
        # fix(omni-g-codebook-04, 2026-06-11): 原 'Stage 40/46' — 现行 DAG stage 46 =
        # stata_export 不产指标, 该列在 stage 45 panel encode 内物化
        source_stage='Stage 40 (panel/encode compute_fintech_attention_index)',
        reference='Da et al. (2011, JF); Fang & Peress (2009, JF)',
        notes='媒体覆盖率范式 (coverage ratio) 的年度基准; 无距离衰减 (距离衰减仅用于 '
              'ft_attn_prov / ft_attn_city 地理变体)。实测值域 ≈ [0.23, 0.30]',
        category='注意力指数',
        track='',
    )

    # ═══ 地理注意力: 省/市 比值 (ft_attn_*) + 三档总量孪生 (ft_vol_*) ═══
    # 2026-06-13 (互为稳健性): 三档 (年/省/市) 各产 比值 ft_attn_* (intensive 议程份额
    # fintech/total ∈[0,1]) 与 总量 ft_vol_* (extensive 覆盖规模 ln(1+fintech 篇数)
    # ∈[0,+∞), Fang & Peress 2009 JF 覆盖计数)。省/市经曝露加权 leave-one-out 映射到
    # bank-year (剔除焦点银行自身报道, 反身性内生守卫), 比值与总量共享 min_articles=5
    # 守卫 → 同非缺样本。yr 为 year-level 常量、无 LOO。两测度分别进各自回归互为稳健性。
    # (同时补 ft_attn_prov/city 此前自动推断占位 → 精修元数据。)
    # ⚠ 样本宇宙 (ATT-2, panel-universe-consistency-audit 2026-06-13): 本地理族
    # (ft_attn_*/ft_vol_*) 的 is_fintech 分子取自**未经 stage-21 验证**的 12_full 全集
    # (地理支系未门控, deferred 待决 gate-or-disclose) — 与 firm-level attention 处理变量族
    # (compute_attention_treatments, 已门控 verified 集) 刻意不同; 可能含 LLM 判伪文章,
    # 论文 data/sample 段须披露该口径。注 notes 字段同载此披露。
    _GEO_ATTN = [
        ('ft_attn_prov', 'Fintech Attention (Province, Exp-Wt)', '比率', '[0, 1]',
         '(cell_ft − own_ft)/(cell_total − own_total) 按 (省,年) LOO, 再 bank-year 曝露加权均值',
         '省级金融科技注意力比值 = 报道该行的媒体来源省份 (剔除自身报道后) 的 fintech 议程份额; '
         '曝露加权 leave-one-out (反身性内生守卫); LOO 余分母 < 5 → NaN'),
        ('ft_attn_city', 'Fintech Attention (City, Exp-Wt)', '比率', '[0, 1]',
         '(cell_ft − own_ft)/(cell_total − own_total) 按 (市,年) LOO, 再 bank-year 曝露加权均值',
         '市级金融科技注意力比值; 口径同 ft_attn_prov, 地理粒度细化到城市; 小单元更易退化 → NaN 守卫'),
        ('ft_vol_yr', 'Fintech Coverage Volume (Year, ln)', '', '[0, +inf)',
         'ln(1 + 当年 fintech 唯一篇数)',
         '年度金融科技覆盖总量 (extensive 规模, year-level 常量, 无 LOO); ft_attn_yr 比值的总量孪生, 互为稳健性'),
        ('ft_vol_prov', 'Fintech Coverage Volume (Province, Exp-Wt, ln)', '', '[0, +inf)',
         'ln(1 + 曝露加权 LOO fintech 篇数, 按 (省,年))',
         '省级金融科技覆盖总量; ft_attn_prov 比值的总量孪生 (同 LOO 样本/守卫), 互为稳健性'),
        ('ft_vol_city', 'Fintech Coverage Volume (City, Exp-Wt, ln)', '', '[0, +inf)',
         'ln(1 + 曝露加权 LOO fintech 篇数, 按 (市,年))',
         '市级金融科技覆盖总量; ft_attn_city 比值的总量孪生 (同 LOO 样本/守卫), 互为稳健性'),
    ]
    for _vn, _lbl, _unit, _rng, _fml, _desc in _GEO_ATTN:
        metadata[_vn] = VariableMetadata(
            var_name=_vn, label=_lbl, description=_desc, data_type='float',
            unit=_unit, value_range=_rng, formula=_fml,
            source_stage='Stage 40 (panel/encode compute_fintech_attention_index)',
            reference='Da et al. (2011, JF); Fang & Peress (2009, JF)',
            notes='三档 (年/省/市) 比值 ft_attn_* 与总量 ft_vol_* 互为稳健性 '
                  '(2026-06-13); prov/city 曝露加权 LOO 映射, 与对应测度同非缺样本; '
                  '比值与总量分别进各自回归、不同进一个 RHS。'
                  '⚠ 构念界定 (toptier-audit 2026-06-13): prov/city 的总量是银行媒体'
                  '**邻域** (报道它的省/市) 曝露加权平均 fintech 篇数 = 二阶邻域曝露量, '
                  '非银行自身覆盖计数; Fang-Peress 2009 firm-own-count 范式更贴 yr 档 '
                  '(ft_vol_yr = 当年 fintech 总篇数, 真覆盖计数), prov/city 系地理曝露工具。'
                  '⚠ 样本宇宙 (ATT-2): is_fintech 分子取自未经 stage-21 验证的 12_full '
                  '(地理族未门控, deferred), 可能含 LLM 判伪文章, 论文 data/sample 须披露',
            category='注意力指数', track='',
        )

    # ═══ P2 attention 处理变量 (bank_fintech_attention) ═══
    # fix(omni-g-codebook-03, 2026-06-11): 族级锚点与 attention_media.py:227-231 更正对齐 —
    # 主处理 attention_index = ln(1+Σ intensity) 是 **extensive 累积曝光** (Fang & Peress 2009 JF),
    # **不是** Hassan et al. (2019 QJE) intensive 归一化份额; intensive 对应 attention_pct/density。
    # W2 (2026-06-05): compute_attention_treatments 物化。三轨 (full/ctx/ss) 互为稳健性
    # (main=full, robustness=ctx/ss 分离复跑; ss=银行+金科同句共现轨)。零-fintech bank-year:
    # index/pct/density→0 (真零曝光), disp/sd/gap/share→NaN。
    # 注: 下方 _ATTN_TREAT 静态列表仅 curate full/ctx 列; attention_media 产出的 _ss 注意力
    # 列在 codebook 中走 _infer_track/_infer_label 兜底 (已三轨化), 不在此重复 curate。
    _ATTN_TREAT = [
        ('attention_index_full', 'Fintech Attention Index (full)', 'full',
         'ln(1 + Σ_d fintech_intensity_score_full)', '[0, +inf)',
         '银行-年累积 fintech 曝光强度 (全文口径); P2 主处理变量 (cumulative attention without sign); '
         'extensive 累积曝光, 非 Hassan intensive 归一化份额 (intensive 对应 attention_pct/density)'),
        ('attention_index_ctx', 'Fintech Attention Index (ctx)', 'ctx',
         'ln(1 + Σ_d fintech_intensity_score_ctx)', '[0, +inf)',
         '同上, 实体窗口口径 (entity-context 窗口归因); 三轨 (full/ctx/ss) 稳健性: 与 _full/_ss 分离复跑; '
         'extensive 累积曝光, 非 Hassan intensive 份额'),
        ('attention_pct_full', 'Fintech Attention Share', '',
         'N_ft / N_all (12_full 全部银行新闻为分母)', '[0, 1]',
         'fintech 新闻占该行该年全部新闻的议程份额 (track-agnostic 单轨, Fang-Peress 2009 JF)'),
        ('attention_disp_full', 'Fintech Attention Dispersion (outlet HHI)', '',
         'Σ_o (n_o / Σn)²  on 媒体(中文)', '[0, 1]',
         '跨媒体曝光集中度 (HHI, 单 outlet=1); 零-fintech→NaN (track-agnostic, Cookson-Niessner 2020 JF)'),
        ('attention_intensity_density_full', 'Attention Intensity Density (full)', 'full',
         'Σ_d fintech_intensity_score_full / N_all', '[0, +inf)',
         '强度加权曝光密度 (非[0,1]故非"share"名); 三轨 (full/ctx/ss) 稳健性载体'),
        ('attention_intensity_density_ctx', 'Attention Intensity Density (ctx)', 'ctx',
         'Σ_d fintech_intensity_score_ctx / N_all', '[0, +inf)',
         '同上, 实体窗口口径; 与 _full 分离复跑'),
        ('attention_intensity_sd_full', 'Attention Intensity SD (full)', 'full',
         'std_d(fintech_intensity_score_full), ddof=1', '[0, +inf)',
         '篇间 fintech 技术强度离散 (二阶矩); N<2→NaN; disp 三轨 (full/ctx/ss) 载体'),
        ('attention_intensity_sd_ctx', 'Attention Intensity SD (ctx)', 'ctx',
         'std_d(fintech_intensity_score_ctx), ddof=1', '[0, +inf)',
         '同上, 实体窗口口径; 三轨 (full/ctx/ss) 中与 full 相关最低 (实跑 0.656), 最强稳健性'),
        ('attention_gap_full_ctx', 'Attention Attribution Gap', '',
         'mean_d(intensity_full − intensity_ctx)', '(-inf, +inf)',
         'full/ctx 派生: 注意力借位/稀释度 (full 相对 ctx 的非本行归因量); 机制变量'),
        ('attention_attr_share', 'Attention Attribution Purity', '',
         # fix(toptier-audit D4-1, 2026-06-13): 同步 attention_media.py:472-474 的有界 share
         # 构造 — 旧 clip(Σctx/Σfull,0,1) 右删失版已于 2026-06-12 撤回 (见该处 fix 注),
         # codebook 此前漏同步 (docstring:433 承诺的集中重生未落)。
         'Σ_d ctx / (Σ_d ctx + Σ_d full)  (= r/(1+r), 保序无删失)', '[0, 1]',
         'full/ctx 派生: 归因纯度 (指向本行的 fintech 注意力占比); Σctx+Σfull=0→NaN'),
        ('n_fintech_articles', 'N fintech articles', '',
         'count(fintech 文章 in bank-year)', '[0, +inf)',
         'extensive-margin baseline 计数 (诊断/对照, track-agnostic)'),
        ('n_outlets', 'N distinct outlets', '',
         'nunique(媒体(中文) over fintech 文章)', '[0, +inf)',
         'HHI 可算性诊断 (n_outlets≥2 才有 disp 变异); 零-fintech→NaN'),
    ]
    # 构念效度披露 (ATTN CV-1/CV-2, PROJECT_REAUDIT_TOPTIER_T18 2026-06-14):
    #   CV-2 (attention_disp): outlet-HHI 在【低覆盖 bank-year 机械 =1】 (单 outlet → HHI=1),
    #     混淆"集中度"与"低覆盖量"; 进回归时须控 ln(n_outlets)/n_fintech_articles 或仅
    #     n_outlets≥3 子样本, 否则 disp 系数吸收的是覆盖广度而非真集中度。disp 是 secondary/
    #     robustness 测度 (非主处理), n_outlets 已在盘作诊断列。
    #   CV-1 (attention_index nomological): 注意力指数族的内部一致性 (nomological) 证据 =
    #     attention_index 与已物化 salience 输入 (n_fintech_articles/attention_pct/density)
    #     的 bank-year 相关矩阵 — 高相关只证内部一致 (类 Cronbach α), 非 DEG 2011 意义的
    #     criterion validity (后者需独立于媒体的 turnover/收益); 外部 criterion 留待财务数据。
    _ATTN_DISP_DISCLOSURE = (
        ' ⚠ 构念效度 (ATTN CV-2, 顶刊重审 2026-06-14): outlet-HHI 在低覆盖 bank-year 机械=1 '
        '(单 outlet → HHI=1), 混淆集中度与低覆盖量; 回归须控 ln(n_outlets) 或仅 n_outlets≥3 '
        '子样本 (n_outlets 已在盘); 仅作 secondary/robustness, 非主处理。'
    )
    _ATTN_INDEX_DISCLOSURE = (
        ' ⚠ 构念效度 (ATTN CV-1, 顶刊重审 2026-06-14): 内部一致性 (nomological) 证据 = '
        'attention_index 与已物化 salience 输入 (n_fintech_articles/attention_pct/density) 的 '
        'bank-year 相关矩阵 (类 Cronbach α, 证内部一致非 DEG 2011 criterion validity); '
        '外部 criterion (独立于媒体的 turnover/收益) 留待财务数据接入。'
    )
    for _vn, _lbl, _trk, _fml, _rng, _desc in _ATTN_TREAT:
        # fix(omni-g-codebook-03, 2026-06-11): attention_index_* 是 extensive 累积曝光
        # (Fang & Peress 2009 JF 主锚, Hassan 2019 QJE 仅作 cf. 对照), 其余列保持族级共引。
        if _vn.startswith('attention_index'):
            _ref = ('Fang & Peress (2009, JF) extensive coverage; '
                    'cf. Hassan et al. (2019, QJE) intensive share; '
                    'Da, Engelberg & Gao (2011, JF); Cookson & Niessner (2020, JF)')
        else:
            _ref = ('Hassan et al. (2019, QJE); Fang & Peress (2009, JF); '
                    'Cookson & Niessner (2020, JF)')
        _notes = ('W2 物化 (2026-06-05); 三轨 (full/ctx/ss) 互为稳健性 (main=full / '
                  'robustness=ctx/ss 分离复跑; ss=银行+金科同句共现); '
                  '零-fintech bank-year 填 0(index/pct/density) 或 NaN(disp/sd/gap/share)')
        if _vn == 'attention_disp_full':
            _notes += _ATTN_DISP_DISCLOSURE
        elif _vn.startswith('attention_index'):
            _notes += _ATTN_INDEX_DISCLOSURE
        metadata[_vn] = VariableMetadata(
            var_name=_vn, label=_lbl, description=_desc, data_type='float',
            unit='比率' if _rng == '[0, 1]' else '',
            value_range=_rng, formula=_fml,
            source_stage='Stage 40 (panel/attention_media compute_attention_treatments)',
            reference=_ref,
            notes=_notes,
            category='注意力指数', track=_trk,
        )

    # ═══ 文章计数口径 (物理篇数 vs LLM 有效投票篇数) ═══
    # metric-audit 2026-06-02 (nart-02 codebook 缺新列): encode-02 重构区分两个
    # 口径 — n_articles = 物理新闻覆盖篇数 (含 LLM 失败/NA 行, 供 ln_news_coverage /
    # falsification 等 coverage 消费者); n_articles_llm_valid(_ctx) = LLM 有效投票
    # 篇数, 用作所有分类组成型 frac (tech/app/sub/symb/indep/collab) 的分母, 保证
    # 分子分母同口径 (encode.py:661-684)。补这三列的 codebook 条目消除元数据缺口。
    metadata['n_articles'] = VariableMetadata(
        var_name='n_articles',
        label='N articles (physical coverage)',
        description='该 Bank-Year 的物理新闻覆盖篇数 (组内全部行, 含 LLM 投票失败 / NA 行); '
                    '用作媒体覆盖度 (ln_news_coverage) 与 falsification 的曝露量',
        data_type='int',
        unit='篇',
        value_range='[0, +∞)',
        formula="size(llm_vote_score_full)  (groupby bank-year 行数, 含 NA)",
        source_stage='Stage 40 (panel/encode aggregate_panel)',
        reference='Fang & Peress (2009, JF) media coverage',
        notes='区别于 n_articles_llm_valid (后者为分类 frac 的分母, 跳过 NA)。'
              '实测值域 [0, 101]',
        category='文章计数',
        track='',
    )
    metadata['n_articles_llm_valid'] = VariableMetadata(
        var_name='n_articles_llm_valid',
        label='N articles, LLM-valid (category-frac denominator)',
        description='该 Bank-Year LLM 有效分类/投票成功的篇数 (full 轨); '
                    '是 tech/app/sub/symb/indep/collab 等分类组成型 frac 的正确分母',
        data_type='int',
        unit='篇',
        value_range='[0, n_articles]',
        formula="count(llm_vote_score_full)  (groupby bank-year 非 NA 计数)",
        source_stage='Stage 40 (panel/encode aggregate_panel)',
        reference='Antweiler & Frank (2004, JF); Fang & Peress (2009, JF)',
        notes='与 n_articles 的差额 = LLM 投票失败 / NA 篇数。分类 frac 分子分母同口径 '
              '(修 encode-02 轨道不对称除法)',
        category='文章计数',
        track='full',
    )
    metadata['n_articles_llm_valid_ctx'] = VariableMetadata(
        var_name='n_articles_llm_valid_ctx',
        label='N articles, ctx-track LLM-valid (ctx category-frac denom)',
        description='该 Bank-Year ctx 轨 LLM 有效投票篇数; 是 ctx 对角线分类 frac '
                    '(tech/app_lc, sub/symb_sc, indep/collab_cm) 的正确分母',
        data_type='int',
        unit='篇',
        value_range='[0, n_articles]',
        formula="count(llm_vote_score_ctx)  (groupby bank-year 非 NA 计数)",
        source_stage='Stage 40 (panel/encode aggregate_panel)',
        reference='Hassan et al. (2019, QJE) entity-proximity; Antweiler & Frank (2004, JF)',
        notes='ctx 轨 LLM 成功率与 full 轨独立, 故 ctx 分类 frac 必须用本列做分母 '
              '(旧实现错用 full 轨 n_articles_llm_valid → frac 越界至 3.0, 已修)',
        category='文章计数',
        track='ctx',
    )

    # ═══ LLM 情感指标 ═══
    # fix(omni-g-codebook-02/-09, 2026-06-11): 投票阵容从 config 动态拼接 (原硬编码
    # 'GPT-5-nano、Gemini-3、Grok-4.1' 三名全错且 Grok 从未在阵容中)。
    _llm_lineup_note = (
        f"使用 {'、'.join(_LLM_MODEL_NAMES)} 共 {len(_LLM_MODEL_NAMES)} 个模型的"
        f"多数投票结果 (阵容动态读自 config/sentiment.yaml)"
    )
    # ───────────────────────────────────────────────────────────────────────
    # 构念效度披露 (SENT CV-1, PROJECT_REAUDIT_TOPTIER_T18 2026-06-14):
    #   主因变量 llm_vote_tone 的【负面类近乎退化】 — 24_herd_decay.parquet 验证篇
    #   实测 正 798 / 中 33 / 负 2 (负面占比仅 0.24%, 三模型 0–0.6%)。
    #   ⚠ 计数更新 (2026-06-23 平局保守降级决策): verified 轨情感**平局/空票**已由
    #     原"未定(None)→排除"改为保守降级"中性"(逆转 v6/F2; 见 tone_llms.py final_v 分支),
    #     故重生后"中"计数将上移约 verified 平局率 (盘面 2.1~2.3%), 上列 正798/中33/负2 为
    #     **改动前历史快照**, 确切类别先验以重生后 panel 实测为准。该变更只会让 tone 更向
    #     "正面 vs 中性"边际集中, **不改**下述单极/负面退化的定性结论。这是中文银行
    #   新闻 PR-positive 语料伪迹 + LLM 乐观偏置的联合结果, 在全量 T=18 上不会反转。
    #   故双极 (-1↔+1) "情感" 实为【单极正向报道倾向 / 乐观度 (favorability/optimism)】:
    #   tone 的变异主要来自「正面 vs 中性」边际, 而非「正面 vs 负面」。系数应解读为
    #   "更乐观/更正面的媒体报道", 不能解读为"从负面到正面的双极摆动"。
    #   ⚠ 负面子样本零方差诊断: 负面类近退化 → 任何"负面媒体冲击"机制识别力弱,
    #   论文 measurement 节须报告类别先验 (正/中/负 边际分布) + 负面子样本极小 N。
    #   $0 披露/framing (不改面板值, .dta 标签随下次重生生效)。
    # ───────────────────────────────────────────────────────────────────────
    _TONE_FAVORABILITY_NOTE = (
        '⚠ 构念=媒体正向报道倾向/乐观度 (favorability/optimism), 非双极情感: '
        '负面类近退化 (验证篇改动前快照 正798/中33/负2, 负面 0.24%) — '
        'tone 变异主要来自正面 vs 中性边际; 系数解读为"更乐观/更正面", 勿作双极摆动。'
        '注: 2026-06-23 起 verified 轨情感平局/空票保守降级"中性"(原"未定"), "中"计数上移, '
        '确切类别先验以重生后 panel 为准。类别先验与负面零方差诊断须进 measurement 节 (SENT CV-1)。'
    )
    metadata['llm_vote_tone_full'] = VariableMetadata(
        var_name='llm_vote_tone_full',
        label='Media Favorability/Optimism (LLM Vote, Full; neg degenerate)',
        description='LLM 投票媒体正向报道倾向/乐观度指数 (全文轨道), 多模型多数投票; '
                    '名义双极 [-1,1] 但负面类近退化 → 实为单极正向强度 (favorability)',
        data_type='float',
        unit='正向倾向值 (favorability)',
        value_range='[-1, 1] (名义); 实测近退化为单极正向 (负面类 0.24%)',
        formula='(n_pos - n_neg) / (n_pos + n_neg + n_neu)',
        source_stage='Stage 21',
        reference='Loughran & McDonald (2011, JF); Tetlock (2007, JF); '
                  'King & Zeng (2001); Cao et al. (2025, Working Paper)',
        notes=f'{_TONE_FAVORABILITY_NOTE} {_llm_lineup_note}',
        category='情感指标 (媒体正向倾向/favorability)',
        track='full',
    )

    metadata['llm_vote_tone_ctx'] = VariableMetadata(
        var_name='llm_vote_tone_ctx',
        label='Media Favorability/Optimism (LLM Vote, Ctx; neg degenerate)',
        description='LLM 投票媒体正向报道倾向/乐观度指数 (上下文轨道, 仅含目标银行句及其前后文); '
                    '名义双极 [-1,1] 但负面类近退化 → 实为单极正向强度',
        data_type='float',
        unit='正向倾向值 (favorability)',
        value_range='[-1, 1] (名义); 实测近退化为单极正向 (负面类 0.24%)',
        formula='(n_pos - n_neg) / (n_pos + n_neg + n_neu)',
        source_stage='Stage 21',
        reference='Loughran & McDonald (2011, JF); Tetlock (2007, JF); '
                  'King & Zeng (2001); Cao et al. (2025, Working Paper)',
        notes=f'上下文轨道可以减少噪音，提高识别精确度；{_TONE_FAVORABILITY_NOTE} {_llm_lineup_note}',
        category='情感指标 (媒体正向倾向/favorability)',
        track='ctx',
    )

    # ═══ v3.10.0 测度变更披露: 跨词典固定 union 5→6 (plan §R1) ═══
    # L&M 2011 中文主译接成第 6 部主情感词典 → 固定 union 词典 5 部扩为 6 部, 驱动
    # pos_ratio/neg_ratio/msent_score 计数基改变 (有意测度变更, 非 bug)。实测影响
    # (scripts/audit/measure_dict_union_impact.py): Pearson r(5,6)=0.985 / 符号翻转 0.13%
    # / mean msent ~3.5% 微变 → 词表覆盖改善, 论文作稳健性如实披露。
    _UNION_NOTE = ('v3.10.0: 计数基 = 固定 6-词典 union (jiang/yao/bian/du/you + '
                   'Loughran-McDonald 2011 中文译本)。union 5→6 致本列微变 '
                   '(r=0.985/符号翻转0.13%), 反映词表覆盖改善非方法误; 见 '
                   'scripts/audit/measure_dict_union_impact.py 与论文稳健性披露。')
    for _trk in ('full', 'ctx', 'ss'):
        _mcol = f'msent_score_{_trk}'
        metadata[_mcol] = VariableMetadata(
            var_name=_mcol,
            label=f'Net-Negative MSENT ({_trk}-track, 6-dict union v3.10.0)',
            description='固定 union 词典原始极性计数净负情感 (零语言学规则; '
                        'Tetlock 2007 / Garcia 2013 固定词表范式)',
            data_type='float',
            unit='净负极性比',
            value_range='[-1, 1]',
            formula='(raw_neg - raw_pos) / (raw_pos + raw_neg)',
            source_stage='Stage 22 (union) + Stage 40',
            reference='Tetlock (2007, JF); Garcia (2013, JF); Loughran & McDonald (2011, JF)',
            notes=_UNION_NOTE,
            category='情感指标 (跨词典 union 净负情感)',
            track=_trk,
        )

    # ═══ CV-1 类别先验诊断列 (再审 v2 2026-06-15, CV-1-INFRA) ═══
    # encode.py:547-550 已产 pos_frac/neg_frac/pos_count/neg_count × {_full,_ctx,_ss};
    # 这些列支撑 SENT CV-1 measurement 节的"类别先验 + 负面子样本零方差/极小 N"诊断,
    # 此前仅由 codebook fallback 自动推断, 此处补精写元数据 (含义/公式/来源/用途/引文)。
    _SENT_DIAG_SPECS = {
        'pos_frac': ('Positive-Class Fraction', '正面类占比 (文章级 is_positive 的 bank-year 均值)',
                     'mean(is_positive)', '[0, 1]', '占比'),
        'neg_frac': ('Negative-Class Fraction (near-degenerate)', '负面类占比 (近退化, 验证篇实测 0.24%)',
                     'mean(is_negative)', '[0, 1] (实测近 0)', '占比'),
        'pos_count': ('Positive-Class Count', '正面类文章计数 (bank-year)',
                      'sum(is_positive)', '[0, +inf)', '篇'),
        'neg_count': ('Negative-Class Count (near-zero)', '负面类文章计数 (近零)',
                      'sum(is_negative)', '[0, +inf) (实测近 0)', '篇'),
    }
    _DIAG_TRACK_LABEL = {'_full': 'Full', '_ctx': 'Ctx', '_ss': 'SS (bank+fintech same-sentence)'}
    for _stem, (_lab, _desc, _formula, _vrange, _unit) in _SENT_DIAG_SPECS.items():
        for _trk in ('_full', '_ctx', '_ss'):
            _col = f'{_stem}{_trk}'
            metadata[_col] = VariableMetadata(
                var_name=_col,
                label=f'{_lab} ({_DIAG_TRACK_LABEL[_trk]})',
                description=f'{_desc}; {_DIAG_TRACK_LABEL[_trk]} 轨道。LLM 投票类别先验诊断, 支撑 '
                            'SENT CV-1 measurement 节 (负面类近退化 → 报告类别先验 + 负面子样本零方差/极小 N)。',
                data_type='float',
                unit=_unit,
                value_range=_vrange,
                formula=_formula,
                source_stage='Stage 21 -> encode.py:547-550 (bank-year 聚合)',
                reference='Loughran & McDonald (2011, JF); King & Zeng (2001, Political Analysis)',
                notes=f'CV-1 类别先验诊断列; {_TONE_FAVORABILITY_NOTE}',
                category='情感指标 (类别先验诊断/CV-1)',
                track=_trk.lstrip('_'),
            )

    # ═══ 网络三轨/W-轨扩展精写 (2026-07-03, 计划层 E — 终验 traceability-3:
    #     必做非可选; 备注承载 D5 文本源不同源披露 + D6 兜底机制分家披露) ═══
    _D5_NOTE = ('D5 口径披露: canonical (无后缀) 文本源 = 原始「内容+标题」拼接 '
                '(历史口径, 缓存锚); ctx/ss 轨 = stage 14 物化 content_{ctx,ss} '
                '原样拼接 (prepend_title 已内嵌标题, 禁再拼 title — 双标题陷阱), '
                '且剔除 *_is_fallback==True 行 (纯轨文本)。两口径刻意不同源。')
    _D6_NOTE = ('D6 兜底分家: cogn 路径 = 100 字符最短守卫→NaN; emb 路径 = 剔行后 '
                'bank 从 groupby 缺席→NaN + 空超级文档剔节点 (无 100 字符门, '
                '短文本照嵌)。三轨/W-轨互为稳健性、不分主次, 禁混同一 Hansen J。')
    for _sfx, _trk_zh in (('', 'full(canonical)'), ('_ctx', 'ctx'), ('_ss', 'ss')):
        _col = f'industry_neg_shock{_sfx}'
        metadata[_col] = VariableMetadata(
            var_name=_col,
            label=(f"Industry Neg Shock (LOO same-period"
                   f"{', ' + _sfx.lstrip('_') if _sfx else ''}; year-FE collinear)"),
            description=f'行业负面冲击 LOO ({_trk_zh} 轨): 同行银行负面报道占比的 '
                        f'leave-one-out 均值; 分子分母严格逐轨 '
                        f'(neg_count{_sfx or "_full"} / n_articles_llm_valid{_sfx})。',
            data_type='float', unit='占比', value_range='[0, 1]',
            formula=f'mean_{{j≠i}}(neg_count{_sfx or "_full"}_j / n_valid{_sfx}_j)',
            source_stage='Stage 40 (panel/network_brokerage)',
            reference='Manski (1993, RES); Angrist (2014, Labour Economics)',
            notes='⚠ 同期版含年FE与自身负面率精确共线, 回归请用 lag1 变体。'
                  '三轨互为稳健性、不分主次 (无后缀=历史命名非"主")。',
            category='情感指标 (行业冲击 LOO)', track=(_sfx.lstrip('_') or 'full'),
        )
        metadata[f'industry_neg_shock_lag1{_sfx}'] = VariableMetadata(
            var_name=f'industry_neg_shock_lag1{_sfx}',
            label=(f"Industry Neg Shock LOO (L1, year-FE-safe"
                   f"{', ' + _sfx.lstrip('_') if _sfx else ''})"),
            description=f'行业负面冲击 LOO 的 t-1 滞后 ({_trk_zh} 轨), 含年FE规格的可用形态。',
            data_type='float', unit='占比', value_range='[0, 1]',
            formula=f'L1.industry_neg_shock{_sfx}',
            source_stage='Stage 40 (panel/network_brokerage)',
            reference='Manski (1993, RES)',
            notes='年FE-safe 滞后变体; 三轨禁混同一 Hansen J。',
            category='情感指标 (行业冲击 LOO)', track=(_sfx.lstrip('_') or 'full'),
        )
    for _wt in ('ctx', 'ss'):
        metadata[f'bank_cogn_mean_{_wt}'] = VariableMetadata(
            var_name=f'bank_cogn_mean_{_wt}',
            label=f'Cognitive Proximity TF-IDF ({_wt} '
                  f'{"window" if _wt == "ctx" else "same-sent"} text)',
            description=f'认知邻近度 ({_wt} 轨文本): 银行 content_{_wt} 超级文档 '
                        f'TF-IDF char-ngram cosine 对其他银行的均值。',
            data_type='float', unit='余弦相似度', value_range='[0, 1]',
            formula=f'mean_j(cosine(tfidf(superdoc_{_wt}_i), tfidf(superdoc_{_wt}_j)))',
            source_stage='Stage 40 (panel/network_spillover)',
            reference='Boschma (2005, Regional Studies)',
            notes=f'{_D5_NOTE} {_D6_NOTE}',
            category='网络指标 (认知邻近)', track=_wt,
        )
        metadata[f'emb_peer_tone_lag1_{_wt}'] = VariableMetadata(
            var_name=f'emb_peer_tone_lag1_{_wt}',
            label=f'Emb Peer Tone L1 (W=full, tone={_wt}) '
                  f'(co-primary: Qwen/Qwen3-Embedding-8B)',
            description=f'嵌入加权同行情感 (legacy 列): W 矩阵来源恒为 full 文本超级'
                        f'文档, 传播 {_wt} 轨 tone — 语义 = W_full × tone_{_wt}。',
            data_type='float', unit='语调', value_range='[-1, 1]',
            formula=f'W_emb^full(t-1) × llm_vote_tone_{_wt}(t-1)',
            source_stage='Stage 40 (panel/network_spillover)',
            reference='Hoberg & Phillips (2016, JPE); Manski (1993, RES)',
            notes='⚠ 与 diag 列仅差 W 来源轨 — 标签/备注必须写明 W, 防审稿人混淆 '
                  '(终验 econ-final-3)。co-primary _lg 孪生同语义。',
            category='情感指标 (嵌入同行)', track=_wt,
        )
        metadata[f'emb_peer_tone_diag_lag1_{_wt}'] = VariableMetadata(
            var_name=f'emb_peer_tone_diag_lag1_{_wt}',
            label=f'Emb Peer Tone Diag L1 (W={_wt}) '
                  f'(co-primary: Qwen/Qwen3-Embedding-8B)',
            description=f'嵌入加权同行情感 (diag 对角轨, 2026-07-03): W 矩阵由 '
                        f'content_{_wt} 超级文档构建, 传播同轨 tone — '
                        f'语义 = W_{_wt} × tone_{_wt} (W same-track)。',
            data_type='float', unit='语调', value_range='[-1, 1]',
            formula=f'W_emb^{_wt}(t-1) × llm_vote_tone_{_wt}(t-1)',
            source_stage='Stage 40 (panel/network_spillover)',
            reference='Hoberg & Phillips (2016, JPE); Manski (1993, RES)',
            notes=f'{_D5_NOTE} {_D6_NOTE} per-W-轨独立降级 (D8): 本单元 miss 不连坐 '
                  f'full 族。',
            category='情感指标 (嵌入同行)', track=_wt,
        )
        metadata[f'bank_emb_sim_mean_lag1_{_wt}'] = VariableMetadata(
            var_name=f'bank_emb_sim_mean_lag1_{_wt}',
            label=f'Bank Emb Sim Mean (L1, W={_wt}) '
                  f'(co-primary: Qwen/Qwen3-Embedding-8B)',
            description=f'银行嵌入相似度均值 (W 来源轨 = {_wt}): content_{_wt} 超级'
                        f'文档 (t-1) 两两 cosine 对其他银行的均值。后缀语义 = W 来源轨。',
            data_type='float', unit='余弦相似度', value_range='[-1, 1]',
            formula=f'mean_j(cosine(emb(superdoc_{_wt}_i, t-1), emb(superdoc_{_wt}_j, t-1)))',
            source_stage='Stage 40 (panel/network_spillover)',
            reference='Hoberg & Phillips (2016, JPE)',
            notes=f'{_D5_NOTE} {_D6_NOTE}',
            category='网络指标 (嵌入相似)', track=_wt,
        )

    # ═══ 网络中心度指标 ═══
    metadata['bank_degree_cent'] = VariableMetadata(
        var_name='bank_degree_cent',
        label='Co-mention Degree Centrality',
        description='银行共现网络的度中心度，衡量银行在媒体报道中的连接数量',
        data_type='float',
        unit='中心度',
        value_range='[0, 1]',
        formula='degree(i) / (n - 1)',
        # fix(omni-g-codebook-04, 2026-06-11): 现行 DAG 的 stage 46 = stata_export
        # (不产指标); 该列实际在 stage 45 panel 构建 Step 7f/7g 内由
        # network_spillover.py 计算 (模块历史名 46_network_spillovers 系遗留编号)。
        source_stage='Stage 40 (panel/network_spillover, 历史模块名 46_network_spillovers)',
        reference='Freeman (1979, Social Networks)',
        notes='度中心度越高，表示该银行与其他银行共同出现在新闻中的频率越高',
        category='网络指标',
        track='',
    )

    # ═══ Innovation Substantiveness 子集 LLM Tone (v3.1.0, W&Z 1998 ASQ) ═══
    # 三轨 (third-track _ss, 2026-06-14): 18 列 = 3 LLM × (_sub|_symb) × (_full|_ctx|_ss)
    # (_ss = 银行+金科同句共现轨; 原双轨 12 列)。
    # 使用 encode.py 的 LLM_MODELS 避免硬编码不同步
    from news_process.pipeline.panel.encode import LLM_MODELS as _ISS_LLM_MODELS
    _ISS_SUBSETS = {
        '_sub':  {'panel_value': '实质性', 'zh': '实质性', 'en': 'Substantive'},
        '_symb': {'panel_value': '象征性', 'zh': '象征性', 'en': 'Symbolic'},
    }
    # _ISS_TRACKS: 静态轨枚举 (驱动下方 substantiveness-subset VariableMetadata 循环)。
    # 三轨化 (third-track _ss): 加 '_ss':('同句','Same-sentence') (银行+金科同句共现)。
    _ISS_TRACKS = {
        '_full': ('全文', 'Full-text'),
        '_ctx': ('上下文', 'Context'),
        '_ss': ('同句', 'Same-sentence'),
    }
    for _short in _ISS_LLM_MODELS:
        for _suffix, _meta in _ISS_SUBSETS.items():
            for _track, (_zh_t, _en_t) in _ISS_TRACKS.items():
                _var = f'{_short}_tone{_suffix}{_track}'
                metadata[_var] = VariableMetadata(
                    var_name=_var,
                    label=f'{_short} Tone in {_meta["en"]} subset ({_en_t})',
                    description=f'{_short} 模型对【{_meta["zh"]}创新】新闻 sentiment 在{_zh_t}轨道的 bank-year 均值',
                    data_type='float',
                    unit='情感值',
                    value_range='[-1, +1] ∪ NaN',
                    formula=f'mean({_short}_score{_track} | innovation_substantiveness == "{_meta["panel_value"]}")',
                    source_stage='Stage 40 (panel/encode aggregate_panel)',
                    reference='Westphal & Zajac (1998) ASQ',
                    notes=f'NaN 当 bank-year 在 {_meta["zh"]} 子集下无新闻',
                    category='情感指标-substantiveness 子集',
                    track=_track.lstrip('_'),
                )

    # ═══ tone_gap_tech_app (v3.1.1, Adner & Kapoor 2010 + Gomber 2018) ═══
    # 反向借鉴 tone_gap_sub_symb (v3.0.0); 增加 min(n_tech,n_app)>=5 confound 防御
    metadata['tone_gap_tech_app'] = VariableMetadata(
        var_name='tone_gap_tech_app',
        label='Technology-Application Sentiment Gap',
        description='同一 bank-year 内 底层技术类 LLM 投票情感 减去 应用场景类，'
                    '反映该银行该年度技术层 vs 业务应用层的舆论温差。',
        data_type='float',
        unit='情感差值',
        value_range='[-2, +2] ∪ NaN',
        formula='(llm_vote_tone_tech_full - llm_vote_tone_app_full) '
                'if min(n_articles_tech, n_articles_app) >= 5 else NaN',
        source_stage='Stage 40 (panel/encode aggregate_panel)',
        reference='Adner & Kapoor (2010) SMJ; Gomber et al. (2018) JMIS',
        notes='探索性指标 - 无预先理论符号; 实证用途仅作描述统计或交互项. '
              'min ≥ 5 过滤防 compositional confound (R8 audit). '
              '对称于 tone_gap_sub_symb (v3.0.0) 但增加 min 过滤.',
        category='情感指标-locus 子集',
        track='full',
    )

    # ═══ v3.2.0 Stage 3 三轨 (full/ctx/ss) prob_score bank-year 聚合 (plan v1.37 P2) ═══
    # 三轨 (third-track _ss, 2026-06-14): prob_score 轨枚举加 '_ss' (银行+金科同句共现);
    # ss 列在 stage 21 ss 跑落盘前缺失 → generate_codebook 只迭代 panel.columns 自动不发射。
    # fix(omni-g-codebook-10, 2026-06-11): 本循环原先还注册 13 个 article 级列名
    # (innovation_locus_* / innovation_substantiveness_* / innovation_collab_mode_* /
    # *_confidence_* / llm_verified_dual_*) — 这些列只存在于 21_tone_llms.parquet,
    # 从不出现在 bank-year panel, generate_codebook 只迭代 panel.columns → 永不发射。
    # 已迁往 get_article_level_metadata_dict() 保留引文; panel 真实聚合列 (tech_frac
    # 等 12 个分类组成型 frac) 改为按真实列名 curated 注册 (见下方 _FRAC_SPECS)。
    # fix(omni-g-codebook-05, 2026-06-11): track 改全卷标准 'full'/'ctx' 枚举
    # (原误用中文 '全文'/'上下文', 致产物 文本轨道 字段 4+4 行混编)。
    # fix(omni-g-codebook-13, 2026-06-11): *_prob_score_std 取值范围 [0, 0.5] →
    # [0, 1/√2 ≈ 0.7071] — 实现是 pandas ddof=1 样本 SD; [0,1] 有界变量的样本 SD
    # 上确界 = √(n/(n-1))·0.5, 在 n=2 取得 sup = 1/√2 (盘上实测 0.5292 已越出旧界)。
    _PROB_STD_RANGE = '[0, 1/√2 ≈ 0.7071]'
    _PROB_STD_NOTE = ('zero-article bank-year → NaN per encode.py L1105 convention; '
                      '上界 1/√2 为 ddof=1 样本 SD 上确界 (√(n/(n-1))·0.5, n=2 时取得)')
    for _suffix, _track_zh, _track_en in [
        ('_full', '全文', 'Full-text'),
        ('_ctx', '上下文', 'Entity-context'),
        ('_ss', '同句', 'Same-sentence'),
    ]:
        _trk = _suffix.lstrip('_')  # 'full' / 'ctx' / 'ss' 标准枚举值
        # ─── Plan v1.37 P2 + 三维对称 (2026-06-14): 每轨 6 个 binary prob_score
        #     列 (subst/locus/collab × {mean,std}), 三轨 (full/ctx/ss) 共 18 列 ───
        metadata[f'avg_subst_prob_score{_suffix}'] = VariableMetadata(
            var_name=f'avg_subst_prob_score{_suffix}',
            label=f'Avg Subst P_BIN ({_track_en}, 1=symbolic)',
            description=f'平均 binary prob_score for innovation_substantiveness {_track_zh}轨',
            data_type='float',
            unit='概率',
            value_range='[0, 1]',
            formula=f'mean(compute_prob_score_binary(label, conf, positive_class="象征性")) over models on innovation_substantiveness{_suffix}',
            source_stage='Stage 21 (article-level) → Stage 40 (bank-year mean)',
            reference='Cover & Thomas (2006) §2 Bernoulli entropy; Jaynes (1957); Törnberg (2023)',
            notes='plan v1.37 P2; positive_class=象征性 aligns with stata_export 1=对照 encoding',
            category='prob_score-substantiveness',
            track=_trk,
        )
        metadata[f'avg_subst_prob_score_std{_suffix}'] = VariableMetadata(
            var_name=f'avg_subst_prob_score_std{_suffix}',
            label=f'Std Subst P_BIN ({_track_en}, bank-year SD)',
            description=f'avg_subst_prob_score{_suffix} 的 bank-year 标准差',
            data_type='float',
            unit='概率SD',
            value_range=_PROB_STD_RANGE,
            formula=f'std(avg_subst_prob_score{_suffix}) over articles per (target_bank, year)',
            source_stage='Stage 40 panel aggregation',
            reference='Plan v1.37 P2 §5.3.2',
            notes=_PROB_STD_NOTE,
            category='prob_score-substantiveness',
            track=_trk,
        )
        metadata[f'avg_locus_prob_score{_suffix}'] = VariableMetadata(
            var_name=f'avg_locus_prob_score{_suffix}',
            label=f'Avg Locus P_BIN ({_track_en}, 1=application)',
            description=f'平均 binary prob_score for innovation_locus {_track_zh}轨',
            data_type='float',
            unit='概率',
            value_range='[0, 1]',
            formula=f'mean(compute_prob_score_binary(label, conf, positive_class="应用场景")) over models on innovation_locus{_suffix}',
            source_stage='Stage 21 (article-level) → Stage 40 (bank-year mean)',
            reference='Cover & Thomas (2006) §2; Jaynes (1957); Törnberg (2023); Shapiro et al. (2022 J.Econometrics)',
            notes='plan v1.37 P2; positive_class=应用场景 aligns with stata_export 1=对照 encoding',
            category='prob_score-locus',
            track=_trk,
        )
        metadata[f'avg_locus_prob_score_std{_suffix}'] = VariableMetadata(
            var_name=f'avg_locus_prob_score_std{_suffix}',
            label=f'Std Locus P_BIN ({_track_en}, bank-year SD)',
            description=f'avg_locus_prob_score{_suffix} 的 bank-year 标准差',
            data_type='float',
            unit='概率SD',
            value_range=_PROB_STD_RANGE,
            formula=f'std(avg_locus_prob_score{_suffix}) over articles per (target_bank, year)',
            source_stage='Stage 40 panel aggregation',
            reference='Plan v1.37 P2 §5.3.2',
            notes=_PROB_STD_NOTE,
            category='prob_score-locus',
            track=_trk,
        )
        # 三维对称补全 (2026-06-14): collab 维 prob_score (Chesbrough 2003 开放创新;
        # positive_class=外部协同 与 stata_export 1=对照 一致), 与 subst/locus 同构。
        metadata[f'avg_collab_prob_score{_suffix}'] = VariableMetadata(
            var_name=f'avg_collab_prob_score{_suffix}',
            label=f'Avg Collab P_BIN ({_track_en}, 1=external/open)',
            description=f'平均 binary prob_score for innovation_collab_mode {_track_zh}轨',
            data_type='float',
            unit='概率',
            value_range='[0, 1]',
            formula=f'mean(compute_prob_score_binary(label, conf, positive_class="外部协同")) over models on innovation_collab_mode{_suffix}',
            source_stage='Stage 21 (article-level) → Stage 40 (bank-year mean)',
            reference='Chesbrough (2003) Open Innovation; Laursen & Salter (2006 SMJ); Cover & Thomas (2006) §2; Jaynes (1957)',
            notes='三维对称 2026-06-14; positive_class=外部协同 aligns with stata_export 1=对照 encoding',
            category='prob_score-collab',
            track=_trk,
        )
        metadata[f'avg_collab_prob_score_std{_suffix}'] = VariableMetadata(
            var_name=f'avg_collab_prob_score_std{_suffix}',
            label=f'Std Collab P_BIN ({_track_en}, bank-year SD)',
            description=f'avg_collab_prob_score{_suffix} 的 bank-year 标准差',
            data_type='float',
            unit='概率SD',
            value_range=_PROB_STD_RANGE,
            formula=f'std(avg_collab_prob_score{_suffix}) over articles per (target_bank, year)',
            source_stage='Stage 40 panel aggregation',
            reference='Plan v1.37 P2 §5.3.2; 三维对称 2026-06-14',
            notes=_PROB_STD_NOTE,
            category='prob_score-collab',
            track=_trk,
        )

    # ═══ 分类组成型 frac (panel 真实聚合列) ═══
    # fix(omni-g-codebook-10, 2026-06-11): 把原 13 个死条目承载的三维分类引文转移到
    # panel 中真实存在的 bank-year 聚合 frac 列 (见 encode.aggregate_panel 中
    # _aggregate_ctx_diagonal 各 frac 赋值处, 用符号引用避免行号漂移); 分母 = 同轨 n_articles_llm_valid(_ctx)
    # (分子分母同口径, metric-audit 2026-06-02 final 修轨道不对称除法)。
    # (var, 子集中文, 子集英文, track, 分子列, 分母列, reference, category)
    _FRAC_SPECS = [
        ('tech_frac', '底层技术', 'Technology', 'full',
         'n_articles_tech', 'n_articles_llm_valid',
         'Gomber et al. (2018, JMIS); Adner & Kapoor (2010, SMJ)', '创新属性-locus'),
        ('app_frac', '应用场景', 'Application', 'full',
         'n_articles_app', 'n_articles_llm_valid',
         'Gomber et al. (2018, JMIS); Adner & Kapoor (2010, SMJ)', '创新属性-locus'),
        ('tech_frac_lc', '底层技术', 'Technology', 'ctx',
         'n_articles_tech_lc_ctx', 'n_articles_llm_valid_ctx',
         'Gomber et al. (2018, JMIS); Hassan et al. (2019, QJE) entity-proximity', '创新属性-locus'),
        ('app_frac_lc', '应用场景', 'Application', 'ctx',
         'n_articles_app_lc_ctx', 'n_articles_llm_valid_ctx',
         'Gomber et al. (2018, JMIS); Hassan et al. (2019, QJE) entity-proximity', '创新属性-locus'),
        ('sub_frac', '实质性', 'Substantive', 'full',
         'n_articles_sub', 'n_articles_llm_valid',
         'Westphal & Zajac (1994, 1998, ASQ); Fiss & Zajac (2006, ASQ)', '创新属性-substantiveness'),
        ('symb_frac', '象征性', 'Symbolic', 'full',
         'n_articles_symb', 'n_articles_llm_valid',
         'Westphal & Zajac (1994, 1998, ASQ); Bingler et al. (2022, FRL)', '创新属性-substantiveness'),
        ('sub_frac_sc', '实质性', 'Substantive', 'ctx',
         'n_articles_sub_sc_ctx', 'n_articles_llm_valid_ctx',
         'Westphal & Zajac (1998, ASQ); Hassan et al. (2019, QJE) entity-proximity', '创新属性-substantiveness'),
        ('symb_frac_sc', '象征性', 'Symbolic', 'ctx',
         'n_articles_symb_sc_ctx', 'n_articles_llm_valid_ctx',
         'Westphal & Zajac (1998, ASQ); Bingler et al. (2022, FRL)', '创新属性-substantiveness'),
        ('indep_frac', '自主研发', 'Closed/independent', 'full',
         'n_articles_indep', 'n_articles_llm_valid',
         'Chesbrough (2003) Open Innovation; Laursen & Salter (2006, SMJ)', '创新属性-collab_mode'),
        ('collab_frac', '外部协同', 'Open/collaborative', 'full',
         'n_articles_collab', 'n_articles_llm_valid',
         'Chesbrough (2003) Open Innovation; Laursen & Salter (2006, SMJ)', '创新属性-collab_mode'),
        ('indep_frac_cm', '自主研发', 'Closed/independent', 'ctx',
         'n_articles_indep_cm_ctx', 'n_articles_llm_valid_ctx',
         'Chesbrough (2003); Hassan et al. (2019, QJE) entity-proximity', '创新属性-collab_mode'),
        ('collab_frac_cm', '外部协同', 'Open/collaborative', 'ctx',
         'n_articles_collab_cm_ctx', 'n_articles_llm_valid_ctx',
         'Chesbrough (2003); Hassan et al. (2019, QJE) entity-proximity', '创新属性-collab_mode'),
        # ═══ 第三轨 "_ss" (银行+金科同句共现) frac 条目 (third-track, 2026-06-14) ═══
        # 三轨 (full/ctx/ss): 6 个 ss 分类组成型 frac, 镜像 ctx 轨 6 个对角 frac, 分类于
        # ss 轨 (同句共现窗口口径)。变量名沿用 ctx 对角编码 + ss 轨字母:
        #   locus  ls (locus-ss):  tech_frac_ls / app_frac_ls
        #   subst  ss (subst-ss):  sub_frac_ss / symb_frac_ss
        #   collab cm_ss:          indep_frac_cm_ss / collab_frac_cm_ss
        # ⚠ 分母 = ss 轨**独立** n_articles_llm_valid_ss (各轨 LLM 成功率不同, encode.py
        #   :677/684 产出并使用; 与 ctx 用 n_articles_llm_valid_ctx 同口径)。原注释误称
        #   "共享 n_articles_llm_valid" 与 encode.py 实现不符, 已订正 (code-vs-code 平价审计)。
        # 分子 = 同轨 ss 对角分类计数列 (encode.py stage 45 ss 聚合落盘);
        # 列缺失时 generate_codebook 只迭代 panel.columns → 该条目自动不发射 (优雅跳过)。
        ('tech_frac_ls', '底层技术', 'Technology', 'ss',
         'n_articles_tech_ls_ss', 'n_articles_llm_valid_ss',
         'Gomber et al. (2018, JMIS); Gentzkow & Shapiro (2010, ECMA) co-mention', '创新属性-locus'),
        ('app_frac_ls', '应用场景', 'Application', 'ss',
         'n_articles_app_ls_ss', 'n_articles_llm_valid_ss',
         'Gomber et al. (2018, JMIS); Gentzkow & Shapiro (2010, ECMA) co-mention', '创新属性-locus'),
        ('sub_frac_ss', '实质性', 'Substantive', 'ss',
         'n_articles_sub_ss_ss', 'n_articles_llm_valid_ss',
         'Westphal & Zajac (1998, ASQ); Dougal et al. (2012, RFS) co-mention sentiment', '创新属性-substantiveness'),
        ('symb_frac_ss', '象征性', 'Symbolic', 'ss',
         'n_articles_symb_ss_ss', 'n_articles_llm_valid_ss',
         'Westphal & Zajac (1998, ASQ); Bingler et al. (2022, FRL)', '创新属性-substantiveness'),
        ('indep_frac_cm_ss', '自主研发', 'Closed/independent', 'ss',
         'n_articles_indep_cm_ss', 'n_articles_llm_valid_ss',
         'Chesbrough (2003); Gentzkow & Shapiro (2010, ECMA) co-mention', '创新属性-collab_mode'),
        ('collab_frac_cm_ss', '外部协同', 'Open/collaborative', 'ss',
         'n_articles_collab_cm_ss', 'n_articles_llm_valid_ss',
         'Chesbrough (2003); Gentzkow & Shapiro (2010, ECMA) co-mention', '创新属性-collab_mode'),
    ]
    for _vn, _zh, _en, _trk, _num, _den, _ref, _cat in _FRAC_SPECS:
        metadata[_vn] = VariableMetadata(
            var_name=_vn,
            label=f'Frac {_en} articles ({_trk})',
            description=f'该 Bank-Year 中 LLM 判定为「{_zh}」的文章占比 ({_trk} 轨分类)',
            data_type='float',
            unit='比率',
            value_range='[0, 1] ∪ NaN',
            formula=f'{_num} / {_den}  ({_den} == 0 → NaN)',
            source_stage='Stage 40 (panel/encode aggregate_panel)',
            reference=_ref,
            notes='分子分母同轨同口径 (LLM 有效投票篇数为分母); '
                  '原 article 级标签列元数据见 get_article_level_metadata_dict()',
            category=_cat,
            track=_trk,
        )

    # ═══ v3.2.0 M2 P2 子集对角线列 (_lc × _ctx, _sc × _ctx; plan v14 §2.2) ═══
    for _cat_label, _suffix, _zh, _en in [
        ('底层技术', '_tech_lc_ctx', '底层技术', 'Technology'),
        ('应用场景', '_app_lc_ctx',  '应用场景', 'Application'),
    ]:
        metadata[f'n_articles{_suffix}'] = VariableMetadata(
            var_name=f'n_articles{_suffix}',
            label=f'N articles in {_en} subset (Loc=Ctx)',
            description=f'innovation_locus_ctx="{_zh}" 子集篇章数 (entity-ctx classification)',
            data_type='int',
            unit='篇',
            value_range='[0, n_articles]',
            formula=f"count(*) where innovation_locus_ctx == '{_zh}'",
            source_stage='Stage 40 (panel/encode aggregate_panel)',
            reference='Hassan et al. (2019, QJE); Sautner et al. (2023, JF)',
            notes='v3.2.0 M2 P2 加性追加; M8 BREAKING 后单轨 _tech/_app 重命名为 _lf 完成对角线对称',
            category='计数-locus 子集 (ctx)',
            track='ctx',
        )
        metadata[f'llm_vote_tone{_suffix}'] = VariableMetadata(
            var_name=f'llm_vote_tone{_suffix}',
            label=f'LLM Tone in {_en} subset (Loc=Ctx, ctx sent)',
            description=f'LLM 投票情感 ({_zh} 子集, ctx 分类, ctx 情感) mean',
            data_type='float',
            unit='情感值',
            value_range='[-1, 1] ∪ NaN',
            formula=f"mean(llm_vote_score_ctx | innovation_locus_ctx == '{_zh}')",
            source_stage='Stage 40',
            reference='Hassan et al. (2019, QJE) entity-proximity sentiment',
            notes='对角线列 _lc × _ctx (plan v14 §2.2 mean diagonal rule)',
            category='情感指标-locus 子集 (ctx)',
            track='ctx',
        )

    for _tt_label, _suffix, _zh, _en in [
        ('实质性', '_sub_sc_ctx',  '实质性',  'Substantive'),
        ('象征性', '_symb_sc_ctx', '象征性',  'Symbolic'),
    ]:
        metadata[f'n_articles{_suffix}'] = VariableMetadata(
            var_name=f'n_articles{_suffix}',
            label=f'N articles in {_en} subset (Subst=Ctx)',
            description=f'innovation_substantiveness_ctx="{_zh}" 子集篇章数',
            data_type='int',
            unit='篇',
            value_range='[0, n_articles]',
            formula=f"count(*) where innovation_substantiveness_ctx == '{_zh}'",
            source_stage='Stage 40',
            reference='Bingler et al. (2022, FRL); W&Z (1998, ASQ)',
            notes='对角线列 _sc × _ctx (plan v14 §2.2)',
            category='计数-substantiveness 子集 (ctx)',
            track='ctx',
        )
        metadata[f'llm_vote_tone{_suffix}'] = VariableMetadata(
            var_name=f'llm_vote_tone{_suffix}',
            label=f'LLM Tone in {_en} subset (Subst=Ctx)',
            description=f'LLM 投票情感 ({_zh} 子集, ctx 分类, ctx 情感) mean',
            data_type='float',
            unit='情感值',
            value_range='[-1, 1] ∪ NaN',
            formula=f"mean(llm_vote_score_ctx | innovation_substantiveness_ctx == '{_zh}')",
            source_stage='Stage 40',
            reference='W&Z (1998, ASQ); Bingler et al. (2022, FRL)',
            notes='对角线列 _sc × _ctx; 论文用作 entity-proximate substantiveness measure',
            category='情感指标-substantiveness 子集 (ctx)',
            track='ctx',
        )

    # ═══ tone_gap full/ctx 对角线 (有意仅双轨, 第三轨 _ss 不分类故不产 tone_gap 对角线) ═══
    # 三轨说明 (third-track _ss): tone_gap 对角线锚定 LLM 分类属性 (locus/substantiveness),
    #   而 ss 是纯情感轨 (不做 D2/D4 分类分解, 见 plan §7.3-A1) → 刻意无 _ss 孪生。
    metadata['tone_gap_tech_app_lc_ctx'] = VariableMetadata(
        var_name='tone_gap_tech_app_lc_ctx',
        label='Tone Gap: Tech-App (Loc=Ctx, ctx sentiment)',
        description='Tech 子集 LLM 投票情感 - App 子集 (entity-ctx classification + ctx sentiment)',
        data_type='float',
        unit='情感差值',
        value_range='[-2, +2] ∪ NaN',
        formula='llm_vote_tone_tech_lc_ctx - llm_vote_tone_app_lc_ctx if min(n_tech, n_app) >= 5 else NaN',
        source_stage='Stage 40',
        reference='Adner & Kapoor (2010, SMJ); Gomber et al. (2018, JMIS); Hassan et al. (2019, QJE)',
        notes='ctx 轨同构 tone_gap_tech_app; min ≥ 5 防御 compositional confound (v3.1.1 R8 audit)',
        category='情感指标-locus 子集 (ctx)',
        track='ctx',
    )
    metadata['tone_gap_sub_symb_sc_ctx'] = VariableMetadata(
        var_name='tone_gap_sub_symb_sc_ctx',
        label='Tone Gap: Sub-Symb (Subst=Ctx, ctx sentiment)',
        description='Substantive - Symbolic LLM 情感 (ctx 分类 + ctx 情感, 洗稿率 cheap talk 指标)',
        data_type='float',
        unit='情感差值',
        value_range='[-2, +2] ∪ NaN',
        formula='llm_vote_tone_sub_sc_ctx - llm_vote_tone_symb_sc_ctx',
        source_stage='Stage 40',
        reference='Westphal & Zajac (1998, ASQ); Bingler et al. (2022, FRL)',
        notes='ctx 轨同构 tone_gap_sub_symb; 论文洗稿率指标核心 ctx 版本',
        category='情感指标-substantiveness 子集 (ctx)',
        track='ctx',
    )

    # ═══ v3.5.1 A1 Lexical Clarity (三轨 full/ctx/ss, LM 2011 JF + You 2018 hhx055) ═══
    # 锚定: Loughran & McDonald (2011) JF 66(1) uncertain dictionary;
    #       You et al. (2018) hhx055 Panel C (388 definite) / Panel D (178 ambiguous);
    #       Bonsall, Leone, Miller, Rennekamp (2017) JAE 63(2-3).
    # 三轨 (third-track _ss, 2026-06-14): _compute_clarity_for_text 泛型扫描, 由上游对
    #   content_full / content_ctx / content_ss (银行+金科同句共现) 分别独立扫描; 此处
    #   curate full/ctx 条目, ss 孪生 (mean_clarity_score_ss 等) 走 _infer_* 兜底注册;
    # title 轨不纳入 (修 R3-H1: title 文本 < 50 字符分母不稳).
    metadata['mean_clarity_score_full'] = VariableMetadata(
        var_name='mean_clarity_score_full',
        label='Mean Clarity Score from indep Full-text scan (LM 2011 JF; You 2018)',
        description='Bank-year 加权平均 clarity_score; 基于 content_full 独立词典扫描',
        data_type='float',
        unit='clarity ratio',
        value_range='[-1, +1]',
        formula='Σ w_i × clarity_score_full_i / Σ w_i; clarity_score = frac_definite − frac_ambiguous',
        source_stage='Stage 22 (tone_words) + Stage 40 (encode_collab apply_v3_5_1)',
        reference='Loughran & McDonald (2011) JF 66(1); You et al. (2018) hhx055',
        notes='v3.5.1 A1 三轨 (full/ctx/ss) 独立扫描; 与 LLM substance 做 HTMT discriminant validity (stage 39d)',
        category='Lexical Clarity (v3.5.1 A1)',
        track='full',
    )

    metadata['mean_clarity_score_ctx'] = VariableMetadata(
        var_name='mean_clarity_score_ctx',
        label='Mean Clarity Score from indep Ctx-text scan (LM 2011 JF; You 2018)',
        description='Bank-year 加权平均 clarity_score; 基于 content_ctx 独立词典扫描',
        data_type='float',
        unit='clarity ratio',
        value_range='[-1, +1]',
        formula='Σ w_i × clarity_score_ctx_i / Σ w_i',
        source_stage='Stage 22 + Stage 40',
        reference='Loughran & McDonald (2011) JF 66(1); You et al. (2018) hhx055',
        notes='ctx 轨与 full 轨分母不直接可比 (ctx 文本短约 50-80%, paper §3.4 disclosure)',
        category='Lexical Clarity (v3.5.1 A1)',
        track='ctx',
    )

    metadata['mean_frac_definite_full'] = VariableMetadata(
        var_name='mean_frac_definite_full',
        label='Mean Frac Definite from indep Full scan (You 2018 Panel C 388 words)',
        description='Bank-year 加权平均 frac_definite (备份连续指标, 修 R9-M3 不损失信息)',
        data_type='float',
        unit='token fraction',
        value_range='[0, 1]',
        formula='Σ w_i × (n_definite_full_i / n_tokens_clarity_base_full_i) / Σ w_i',
        source_stage='Stage 22 + Stage 40',
        reference='You et al. (2018) hhx055 Panel C',
        notes='clarity 三轨 (full/ctx/ss) 连续备份; 与 frac_amb_articles 二值化指标互补',
        category='Lexical Clarity (v3.5.1 A1)',
        track='full',
    )

    metadata['mean_frac_definite_ctx'] = VariableMetadata(
        var_name='mean_frac_definite_ctx',
        label='Mean Frac Definite from indep Ctx scan (You 2018 Panel C 388 words)',
        description='Bank-year 加权平均 frac_definite (ctx 轨)',
        data_type='float',
        unit='token fraction',
        value_range='[0, 1]',
        formula='Σ w_i × (n_definite_ctx_i / n_tokens_clarity_base_ctx_i) / Σ w_i',
        source_stage='Stage 22 + Stage 40',
        reference='You et al. (2018) hhx055 Panel C',
        notes='ctx 轨连续 frac_definite',
        category='Lexical Clarity (v3.5.1 A1)',
        track='ctx',
    )

    metadata['frac_amb_articles_full'] = VariableMetadata(
        var_name='frac_amb_articles_full',
        label='Frac Articles Ambiguous Full (>=D0 median, You 2018 Panel D)',
        description='Bank-year 中 frac_ambiguous_full ≥ D0 frozen 全样本中位数的 article 占比',
        data_type='float',
        unit='article fraction',
        value_range='[0, 1] ∪ NaN',
        formula='#{i: frac_ambiguous_full_i ≥ median_amb_d0 ∧ n_articles ≥ 2} / n_articles',
        source_stage='Stage 22 + Stage 40',
        reference='You et al. (2018) hhx055 Panel D; LM 2011 JF binarized version',
        notes='二值化指标 (修 R9-M3); n_articles<2 cell → NaN (修 R8-H2); median anchored to prompt v8 + stage 21 (修 R7-H1)',
        category='Lexical Clarity (v3.5.1 A1)',
        track='full',
    )

    metadata['frac_amb_articles_ctx'] = VariableMetadata(
        var_name='frac_amb_articles_ctx',
        label='Frac Articles Ambiguous Ctx (>=D0 median, You 2018 Panel D)',
        description='Bank-year 中 frac_ambiguous_ctx ≥ D0 frozen 中位数的 article 占比 (ctx 轨)',
        data_type='float',
        unit='article fraction',
        value_range='[0, 1] ∪ NaN',
        formula='#{i: frac_ambiguous_ctx_i ≥ median_amb_d0 ∧ n_articles ≥ 2} / n_articles',
        source_stage='Stage 22 + Stage 40',
        reference='You et al. (2018) hhx055 Panel D',
        notes='ctx 三轨 (full/ctx/ss) 二值化之一; 与 frac_amb_articles_full 配对',
        category='Lexical Clarity (v3.5.1 A1)',
        track='ctx',
    )

    # ═══ v3.5.1 A3 Numerical Intensity (三轨 full/ctx/ss, 数值披露强度; 2026-06-05 引文勘误见 reference) ═══
    # 三轨 (third-track _ss, 2026-06-14): 泛型 num_intensity 扫描由上游对 content_full/ctx/ss
    #   (银行+金科同句共现) 分别调用; 此处 curate full/ctx, mean_num_intensity_ss 走 _infer_* 兜底。
    metadata['mean_num_intensity_full'] = VariableMetadata(
        var_name='mean_num_intensity_full',
        label='Mean Numerical Intensity Full (three-track)',
        description='Bank-year 加权平均量化披露强度; 基于 content_full + cn2arab + 正则独立扫描',
        data_type='float',
        unit='digits per sentence',
        value_range='[0, +∞) ∪ NaN',
        formula='Σ w_i × (n_digits_full_i / n_sentences_full_i) / Σ w_i; n_sentences lookahead/behind 排除小数点',
        source_stage='Stage 22 (tone_words post-processor enrich_with_num_intensity_dual_track) + Stage 40',
        reference='Davis & Tama-Sweet (2012) CAR 29(3); 公式为项目自定义操作化 (2026-06-05 引文勘误: 原引 Hales-Kuang-Venkataraman 2011 系误归, 该文实为 JAR 49(1) 论 vivid/pallid 语言, 未定义 numerical intensity)',
        notes='v3.5.1 A3 三轨 (full/ctx/ss); cn2arab 5 标准样例 frozen at D0; 不定数 (几千/数十亿) 不计为 token (修 R7-M2); 中文 sentence 分母与英文文献不直接可比 (paper §3.4 disclosure 修 R7-M1)',
        category='Numerical Intensity (v3.5.1 A3)',
        track='full',
    )

    metadata['mean_num_intensity_ctx'] = VariableMetadata(
        var_name='mean_num_intensity_ctx',
        label='Mean Numerical Intensity Ctx (three-track)',
        description='Bank-year 加权平均 num_intensity; ctx 轨独立扫描',
        data_type='float',
        unit='digits per sentence',
        value_range='[0, +∞) ∪ NaN',
        formula='Σ w_i × (n_digits_ctx_i / n_sentences_ctx_i) / Σ w_i',
        source_stage='Stage 22 + Stage 40',
        reference='Davis & Tama-Sweet (2012) CAR 29(3); 公式为项目自定义操作化 (原引 Hales 2011 系误归, 见 full 轨 reference)',
        notes='ctx 残半句已被 entity_context 完整句号过滤 (修 R3-H3)',
        category='Numerical Intensity (v3.5.1 A3)',
        track='ctx',
    )

    # ═══ 文本测度缺口补全 (2026-06-05, 批 #1–#15): 词汇复杂度/披露质量/新闻显著性 ═══
    # 全 $0 (jieba/posseg/纯解析); 三轨 (full/ctx/ss); 详见 lexical_complexity.py /
    # news_salience.py + scripts/audit/TEXTUAL_MEASURE_GAP_AUDIT_2026-06-05.md。
    # 三轨 (third-track _ss, 2026-06-14): 下方 _DUAL_TEXT_SPECS 循环加 '_ss' (银行+金科
    #   同句共现) 轨; 但仅 lexical_complexity 泛型 per-article 测度真出 ss 列, 而
    #   strategic_diff (lazy_*) / geography (ln_*_count) / runner (tone_volatility) 等
    #   非 per-article 泛型测度无 ss 孪生 → 其 _ss 元数据条目永不命中 panel.columns,
    #   generate_codebook 静默不发射 (graceful, 无幻影行)。
    _CAT_NEW = 'Text Complexity/Disclosure (2026-06-05)'
    # (col_base, label, unit, value_range, formula, reference, source_stage)
    _DUAL_TEXT_SPECS = [
        # D2 FLS 全族补录 (2026-07-03 §5: 此前 frac_fls 族 codebook 零条目, 顺手偿还欠账;
        # 同名直聚合 dst=src, 非 avg_ 前缀范式):
        ('frac_fls', 'Forward-Looking Statements Frac (dual-gate)', '[0,1]', '[0,1] ∪ NaN',
         'bank-year mean of (FLS 句数/总句数); 双门=句含 future 词∧time 词 (canonical headline); 与单门 frac_fls_fonly 互为稳健、不分主次, 禁混同一 Hansen J',
         'Li (2010) JAR 48(5); Bozanic-Roulstone-Van Buskirk (2018) JAE 65(1); Muslu et al. (2015) MS', 'Stage 22 (forward_looking) + Stage 40'),
        ('frac_fls_fonly', 'Forward-Looking Statements Frac (future-only)', '[0,1]', '[0,1] ∪ NaN',
         'bank-year mean of (单门 FLS 句数/总句数); 单门=句含 future 词即计 (双门的超集, 逐句蕴含); 证明 FLS 结论不被 time 门控驱动 (2026-07-03 D2 稳健臂)',
         'Li (2010) JAR 48(5); Bozanic-Roulstone-Van Buskirk (2018) JAE 65(1)', 'Stage 22 (forward_looking) + Stage 40'),
        # WP-C 三轨化 (2026-07-03, 自 _SINGLE_TEXT_SPECS 的 'avg_boilerplate_full' 迁入;
        # base label 已去 '(full)' 后缀 → 发射 label 'Boilerplate Phrase Ratio (full)' 与旧
        # 单轨条目逐字节同; full=headline, ctx/ss=互为稳健轨):
        ('avg_boilerplate', 'Boilerplate Phrase Ratio', '[0,1]', '[0,1] ∪ NaN',
         'bank-year mean of (命中跨语料高频 char_wb(4,6)-gram 套话集出现数/全部 n-gram 出现数); 解释性限定: 套话集口径在 ctx/ss 子窗信号较弱, ctx/ss 作稳健对照. ⚠ 套话集建在 stage22 输入子集(非真全量), 中文新闻落地非英文 10-K 原做法; 与 within_doc_redundancy(篇内)/staleness(整篇相似度)正交; 非嵌入族无 _lg 孪生',
         'Lang-Stice-Lawrence (2015) JAE 60(2-3):110; Dyer-Lang-Stice-Lawrence (2017) JAE 64(2-3)', 'Stage 22 (boilerplate) + Stage 40'),
        ('avg_rare_word', 'Rare-Word Ratio', 'token fraction', '[0,1] ∪ NaN',
         'bank-year mean of (低频词 token / 总 token); 低频=jieba 冻结词典词频≤P20 cutoff(实测覆盖~57% distinct词, 实为"非高频词率")',
         'You & Zhang (2009) RAS 14(4); Gentzkow-Kelly-Taddy (2019) JEL 57(3)', 'Stage 22 (lexical_complexity) + Stage 40'),
        # D1 频次 cutoff 梯子 (2026-07-03 §5): c2/c5 与 canonical (cutoff=3, 上行) 互为稳健、
        # 不分主次; 频次而非分位参数化 (冻结词典低频 tie 使分位梯子退化), 禁混同一 Hansen J
        ('avg_rare_word_c2', 'Rare-Word Ratio (cutoff=2)', 'token fraction', '[0,1] ∪ NaN',
         'bank-year mean; 低频=词频≤2 (≈实测 P10, 覆盖~11.6% distinct 词); canonical(≤3) 的敏感性臂, SSOT=lexical_complexity.RARE_WORD_FREQ_CUTOFFS',
         'You & Zhang (2009) RAS 14(4); Gentzkow-Kelly-Taddy (2019) JEL 57(3)', 'Stage 22 (lexical_complexity) + Stage 40'),
        ('avg_rare_word_c5', 'Rare-Word Ratio (cutoff=5)', 'token fraction', '[0,1] ∪ NaN',
         'bank-year mean; 低频=词频≤5 (≈实测 P63, 覆盖~63.4% distinct 词); canonical(≤3) 的敏感性臂, SSOT=lexical_complexity.RARE_WORD_FREQ_CUTOFFS',
         'You & Zhang (2009) RAS 14(4); Gentzkow-Kelly-Taddy (2019) JEL 57(3)', 'Stage 22 (lexical_complexity) + Stage 40'),
        ('avg_hard_char', 'Hard-Char Ratio', 'char fraction', '[0,1] ∪ NaN',
         'bank-year mean of (非常用汉字 / 全部汉字); 常用字=jieba 词典字频累计 99.5% 派生集',
         '丘心颖等 (2016) 经济学(季刊) 15(4):1483; Dale & Chall (1948)', 'Stage 22 (lexical_complexity) + Stage 40'),
        ('avg_nominalization', 'Nominalization Ratio', 'token fraction', '[0,1] ∪ NaN',
         'bank-year mean of (vn/an 词性+性/化/度/型/制 后缀名词 / 总 token); posseg 近似(含专名 nr 小幅高估)',
         'Bonsall-Leone-Miller-Rennekamp (2017) JAE 63(2-3) Bog 句法成分', 'Stage 22 (lexical_complexity) + Stage 40'),
        ('avg_function_word', 'Function-Word Ratio (LIWC Analytic 近似)', 'token fraction', '[0,1] ∪ NaN',
         'bank-year mean of (u/p/c/r/y/e 虚词词性 / 总 token); 虚词占比高≈低分析性',
         'LIWC Analytic 维中文近似', 'Stage 22 (lexical_complexity) + Stage 40'),
        ('avg_specificity', 'Specificity / Hard-Info Density', 'token fraction', '[0,1] ∪ NaN',
         'bank-year mean of ((nr/ns/nt/nz 实体 + m 数词)/总 token); reframe=报道硬信息密度(非10-K披露); posseg 粗近似',
         'Hope, Hu & Lu (2016) RAS 21(4):1005', 'Stage 22 (lexical_complexity) + Stage 40'),
        ('avg_named_entity', 'Named-Entity Density (specificity 实体面)', 'token fraction', '[0,1] ∪ NaN',
         'bank-year mean of (nr/ns/nt/nz 具名实体/总 token); specificity 的纯实体子集(不含 m 数词), 拆出实体面以与数字面(num_intensity)正交. ⚠ avg_specificity 真子集分子(机械相关); T=2 盘面实测 article corr≈0.81 / bank-year≈0.75-0.80 — 中高相关非别名(信息量充分, 可作独立 specificity-面稳健性列), 但因子集机械相关勿与 avg_specificity 同进同一回归式(corr 数值待生产 T=18 回填)',
         'Hope, Hu & Lu (2016) RAS 21(4):1005', 'Stage 22 (lexical_complexity) + Stage 40'),
        ('avg_within_doc_redund', 'Within-Document Redundancy', 'ratio', '[0,1] ∪ NaN',
         'bank-year mean of (1 − 唯一字符3-gram/全部字符3-gram); 篇内自重复(与 staleness 跨篇正交)',
         'Dyer-Lang-Stice-Lawrence (2017) JAE 64(2-3); Cazier & Pfeiffer (2016)', 'Stage 22 (lexical_complexity) + Stage 40'),
        ('avg_within_doc_redund_han', 'Within-Document Redundancy (Han-char)', 'ratio', '[0,1] ∪ NaN',
         'bank-year mean of (1 − 唯一汉字3-gram/全部汉字3-gram); 仅汉字口径(剔数字/标点/拉丁), 分子分母同为汉字. ⚠与字符口径 avg_within_doc_redund 文章级 corr≈0.99 → 敏感性诊断非独立构念, 勿同进一回归 (hanzi-char-dual); 锚点系中文落地非英文原文做法',
         'Dyer-Lang-Stice-Lawrence (2017) JAE 64(2-3); Cazier & Pfeiffer (2016)', 'Stage 22 (lexical_complexity) + Stage 40'),
        # fix(dta-coverage-audit, 2026-07-03): redundancy 配对长度控制 (字符/汉字双口径).
        # 聚合=mean-of-ln (文章级 ln 长度的 bank-year 均值), 与 avg_within_doc_redund(_han)
        # 同域同口径配对; ≠ geography 的 ln-of-mean (ln_word_count/ln_han_count), 刻意并存.
        ('avg_redund_log_length', 'Redundancy Paired Length Control (ln chars)', 'ln(chars)', '[0, +∞) ∪ NaN',
         'bank-year mean of ln(去空白字符数); 回归用 avg_within_doc_redund 时的配对长度控制 (redundancy 与长度机械相关, Cazier & Pfeiffer 2016), 与其同定义域',
         'Dyer-Lang-Stice-Lawrence (2017) JAE 64(2-3); Cazier & Pfeiffer (2016)', 'Stage 22 (lexical_complexity) + Stage 40'),
        ('avg_redund_han_log_length', 'Redundancy Paired Length Control (ln Han chars)', 'ln(chars)', '[0, +∞) ∪ NaN',
         'bank-year mean of ln(汉字数); 回归用 avg_within_doc_redund_han 时的配对长度控制, 与其同定义域 (hanzi-char-dual 汉字口径)',
         'Dyer-Lang-Stice-Lawrence (2017) JAE 64(2-3); Cazier & Pfeiffer (2016)', 'Stage 22 (lexical_complexity) + Stage 40'),
        ('avg_adversative', 'Adversative-Conjunction Ratio', 'token fraction', '[0,1] ∪ NaN',
         'bank-year mean of (独立逆接连词表命中/总 token); 探索性, 不复用情感轨 adversative_words',
         '徐巍-姚振晔-陈冬华 (2021) 会计研究 (3):28; Ding-Liu-Yu (2008) WSDM', 'Stage 22 (lexical_complexity) + Stage 40'),
        ('avg_word_count', 'Avg Word Count (jieba)', 'words', '[0, +∞) ∪ NaN',
         'bank-year mean of 文章 jieba 词数(去空白)',
         'Li (2008) JAE 45(2-3) 篇幅代理', 'Stage 22 (lexical_complexity) + Stage 40'),
        ('ln_word_count', 'Article Length ln(1+avg_words) 词口径 MLENGTH', 'ln words', '[0, +∞) ∪ NaN',
         'ln(1 + avg_word_count); 真词口径 MLENGTH (区别于字符口径 avg_article_length)',
         'Li (2008) JAE 45(2-3); He et al. (2024) IRFA', 'Stage 40 (geography)'),
        ('avg_han_count', 'Avg Han-Char Count', 'han chars', '[0, +∞) ∪ NaN',
         'bank-year mean of 文章 CJK 汉字数 (is_cjk 计数, 剔数字/标点/拉丁; 与 hard_char 的 n_han 同源)',
         'Li (2008) JAE 45(2-3) 篇幅代理 (汉字口径)', 'Stage 22 (lexical_complexity) + Stage 40'),
        ('ln_han_count', 'Article Length ln(1+avg_hanchars) 汉字口径', 'ln han chars', '[0, +∞) ∪ NaN',
         'ln(1 + avg_han_count); 文章长度第三口径, 与字符口径 avg_article_length / 词口径 ln_word_count 互为长度稳健 (hanzi-char-dual)',
         'Li (2008) JAE 45(2-3); He et al. (2024) IRFA', 'Stage 40 (geography)'),
        ('mean_num_intensity_word', 'Numerical Intensity per-Word (§4.3)', 'digits per word', '[0, +∞) ∪ NaN',
         'bank-year 加权均值 of (数字 token / jieba 词数); 句级 num_intensity 的词级替代版, 对中文句读 sparse 稳健',
         'Davis & Tama-Sweet (2012) CAR 29(3) (构念; 公式为项目自定义)', 'Stage 22 (numerical_intensity) + Stage 40'),
        ('tone_volatility', 'Tone Volatility (rolling SD)', 'std', '[0, +∞) ∪ NaN',
         'per-bank 3-year rolling std of llm_vote_tone (min_periods=2); 时间维二阶矩(与年内SD/反转正交)',
         'De Bondt-Thaler (1985) 反转之二阶矩补全', 'Stage 40 (runner i2)'),
        ('lazy_jaccard', 'YoY Text Change — Jaccard', 'distance', '[0,1] ∪ NaN',
         '相邻年(t,t-1)同行聚合文本 1 − jieba 词集 Jaccard; 首年 NaN',
         'Cohen, Malloy & Nguyen (2020) JF 75(3):1371', 'Stage 40 (strategic_diff)'),
        ('lazy_overlap', 'YoY Text Change — Word-Overlap', 'distance', '[0,1] ∪ NaN',
         '相邻年 1 − |A∩B|/min(|A|,|B|) 词集; 首年 NaN',
         'Cohen, Malloy & Nguyen (2020) JF 75(3):1371', 'Stage 40 (strategic_diff)'),
        ('lazy_minedit', 'YoY Text Change — Norm-Levenshtein', 'distance', '[0,1] ∪ NaN',
         '相邻年 归一化编辑距离(rapidfuzz, 截断前2000字); 首年 NaN',
         'Cohen, Malloy & Nguyen (2020) JF 75(3):1371', 'Stage 40 (strategic_diff)'),
    ]
    for _base, _label, _unit, _vr, _formula, _ref, _src in _DUAL_TEXT_SPECS:
        # 三轨 (full/ctx/ss): ss 条目仅对 lexical_complexity 泛型测度命中 panel (见上注),
        # 其余永不发射 → 加性安全。
        for _tk, _tn in (('_full', 'full'), ('_ctx', 'ctx'), ('_ss', 'ss')):
            metadata[f'{_base}{_tk}'] = VariableMetadata(
                var_name=f'{_base}{_tk}', label=f'{_label} ({_tn})',
                description=f'{_label}; bank-year 聚合, {_tn} 轨', data_type='float',
                unit=_unit, value_range=_vr, formula=_formula, source_stage=_src,
                reference=_ref, category=_CAT_NEW, track=_tn)

    # 新闻体裁显著性 (#8–#10, track-agnostic 单轨, 无 full/ctx/ss 分轨; 版面/页号/作者 解析,
    # Tetlock 2007/2008; Boudoukh 2019 RFS)
    _SINGLE_TEXT_SPECS = [
        ('frac_front_page', 'Front-Page Coverage Frac', '[0,1] ∪ NaN',
         'bank-year mean of is_front_page (头版/要闻 或 A叠首页)', 'Tetlock (2007) JF 62(3); Boudoukh et al. (2019) RFS', 'Stage 11 (news_salience) + Stage 40'),
        ('frac_front_section', 'Front-Section Coverage Frac', '[0,1] ∪ NaN',
         'bank-year mean of is_front_section (版面含头版/要闻/头条关键词)', 'Tetlock (2007) JF 62(3)', 'Stage 11 (news_salience) + Stage 40'),
        ('avg_page_rank', 'Avg Page Prominence (lower=front)', 'rank ∪ NaN',
         'bank-year mean of page_rank=叠字母序×100+页码 (越小越显著)', 'Tetlock (2007) JF 62(3); Boudoukh et al. (2019) RFS', 'Stage 11 (news_salience) + Stage 40'),
        ('staff_written_frac', 'Staff-Written (Byline) Frac', '[0,1] ∪ NaN',
         'bank-year mean of has_byline (作者具名且非通讯社)', '来源原创性 (投入端, 与 media_authority/herd 正交)', 'Stage 11 (news_salience) + Stage 40'),
        ('wire_frac', 'Wire-Service Frac', '[0,1] ∪ NaN',
         'bank-year mean of is_wire (作者/电头命中通讯社)', '通稿/转载来源', 'Stage 11 (news_salience) + Stage 40'),
        ('frac_target_in_lead', 'Target-in-Lead Frac', '[0,1] ∪ NaN',
         'bank-year mean of target_in_lead (规范行名出现在标题或正文前2句)', 'Tetlock (2008); Boudoukh et al. (2019) RFS relevance/centrality', 'Stage 11 (news_salience) + Stage 40'),
        ('coverage_active_days', 'Active Coverage Days per Year', 'days ∪ NaN',
         'bank-year 内有报道的不同日历天数(nunique 日期)', 'Hillert-Jacobs-Müller (2014) RFS', 'Stage 40 (encode)'),
        ('coverage_continuity', 'Coverage Continuity (active/span)', '[0,1] ∪ NaN',
         'coverage_active_days / (报道跨度天数); 1=天天有, 低=爆发式 (节奏, 与 staleness 内容重复正交)', 'Hillert-Jacobs-Müller (2014) RFS', 'Stage 40 (encode)'),
    ]
    for _name, _label, _vr, _formula, _ref, _src in _SINGLE_TEXT_SPECS:
        metadata[_name] = VariableMetadata(
            var_name=_name, label=_label, description=_label, data_type='float',
            unit=_vr.split()[0] if '∪' not in _vr.split()[0] else '—',
            value_range=_vr, formula=_formula, source_stage=_src,
            # fix(omni-g-codebook-05, 2026-06-11): track-agnostic 空值统一 ''
            # (原 '—' 与其他条目的 '' 两种空值并存)
            reference=_ref, category=_CAT_NEW, track='')

    return metadata


def get_article_level_metadata_dict() -> Dict[str, VariableMetadata]:
    """article 级 (21_tone_llms.parquet) 列的 curated 元数据 — 不进 panel codebook 产物。

    fix(omni-g-codebook-10, 2026-06-11): 这 13 个条目原registered在
    get_variable_metadata_dict() 中, 但列名只存在于 article 级 21_tone_llms.parquet,
    从不出现在 bank-year panel — generate_codebook 仅迭代 panel.columns, 故它们
    永远不会写入任何产物 (死条目)。迁出以 (a) 保留精心撰写的引文供未来 article 级
    sheet / 文档复用; (b) 修正取值范围: article 级 parquet 实际存储中文标签字符串
    (large_string, 如 '底层技术'/'应用场景'), 0/1 编码仅发生在下游 stata_export
    (本模块 docstring v3.0.0: '翻译层已废除, panel 列值即 LLM 原始输出')。
    panel 真实存在的聚合派生列 (tech_frac 等) 已在主字典按真实列名注册。
    """
    metadata: Dict[str, VariableMetadata] = {}

    for _suffix, _track_zh, _track_en, _ref in [
        ('_full', '全文', 'Full-text', 'Gomber 2018 JMIS'),
        ('_ctx', '上下文', 'Entity-context', 'Hassan 2019 QJE entity-proximity'),
    ]:
        _trk = _suffix.lstrip('_')  # fix(omni-g-codebook-05): 'full'/'ctx' 标准枚举
        metadata[f'innovation_locus{_suffix}'] = VariableMetadata(
            var_name=f'innovation_locus{_suffix}',
            label=f'Innovation Locus ({_track_en}, {_ref})',
            description=f'金融科技创新位点 ({_track_zh}判定): 底层技术 / 应用场景',
            data_type='str (article-level raw LLM label)',
            unit='类别',
            value_range="'底层技术' | '应用场景' | NaN (0/1 编码仅在下游 stata_export)",
            formula=f'majority_vote_3LLMs(innovation_locus | {_track_en} prompt) + canonicalize_topic crossvalidation',
            source_stage='Stage 21 (article-level, 21_tone_llms.parquet)',
            reference=f'Gomber et al. (2018, JMIS); Adner & Kapoor (2010, SMJ); {_ref}',
            notes=f'v3.2.0 BREAKING: 替代 v3.1.x bare innovation_locus. {_track_zh}轨独立判定. '
                  'panel 聚合派生列 = tech_frac/app_frac (full) 与 tech_frac_lc/app_frac_lc (ctx).',
            category='创新属性-locus',
            track=_trk,
        )
        metadata[f'innovation_substantiveness{_suffix}'] = VariableMetadata(
            var_name=f'innovation_substantiveness{_suffix}',
            label=f'Innov. Substantiveness ({_track_en}, W&Z 1998 ASQ)',
            description=f'金融科技创新实质性 ({_track_zh}判定): 实质性 / 象征性 (洗稿率框架)',
            data_type='str (article-level raw LLM label)',
            unit='类别',
            value_range="'实质性' | '象征性' | NaN (0/1 编码仅在下游 stata_export)",
            formula=f'majority_vote_3LLMs(innovation_substantiveness | {_track_en} prompt)',
            source_stage='Stage 21 (article-level, 21_tone_llms.parquet)',
            reference='Westphal & Zajac (1994, 1998, ASQ); Fiss & Zajac (2006, ASQ); Bingler et al. (2022, FRL)',
            notes=f'v3.2.0 BREAKING: 替代 v3.1.x bare innovation_substantiveness. {_track_zh}轨独立判定. '
                  'panel 聚合派生列 = sub_frac/symb_frac (full) 与 sub_frac_sc/symb_frac_sc (ctx).',
            category='创新属性-substantiveness',
            track=_trk,
        )
        # v3.4.0 BREAKING: 第三维度 innovation_collab_mode (Chesbrough 2003 + L&S 2006 SMJ;
        # additive supplementation per Nosek 2018 PNAS, v7 双维语义不变)
        metadata[f'innovation_collab_mode{_suffix}'] = VariableMetadata(
            var_name=f'innovation_collab_mode{_suffix}',
            label=f'Innov. Collab Mode ({_track_en}, Chesbrough 2003)',
            description=(f'金融科技创新协作模式 ({_track_zh}判定): '
                         '自主研发 (closed innovation) / 外部协同 (open innovation)'),
            data_type='str (article-level raw LLM label)',
            unit='类别',
            value_range="'自主研发' | '外部协同' | NaN (0/1 编码仅在下游 stata_export)",
            formula=f'majority_vote_3LLMs(innovation_collab_mode | {_track_en} prompt)',
            source_stage='Stage 21 (article-level, 21_tone_llms.parquet)',
            reference=('Chesbrough (2003) Open Innovation; '
                       'Laursen & Salter (2006, SMJ 27:131-150); '
                       'Hagedoorn (2002, Research Policy)'),
            notes=(f'v3.4.0 BREAKING: 第三维度对称扩张. {_track_zh}轨独立判定. '
                   'tie→"自主研发" (MAP under uniform prior). '
                   'panel 聚合派生列 = indep_frac/collab_frac (full) 与 indep_frac_cm/collab_frac_cm (ctx).'),
            category='创新属性-collab_mode',
            track=_trk,
        )
        metadata[f'innovation_collab_mode_confidence{_suffix}'] = VariableMetadata(
            var_name=f'innovation_collab_mode_confidence{_suffix}',
            label=f'Collab Mode Confidence ({_track_en}, raw LLM)',
            description=f'innovation_collab_mode{_suffix} 原始 LLM 置信度 (跨模型 row-level 平均)',
            data_type='float',
            unit='概率',
            value_range='[0, 1]',
            formula=f'mean(per_model innovation_collab_mode_confidence | {_track_en} prompt) over verifying models',
            source_stage='Stage 21 (article-level, 21_tone_llms.parquet)',
            reference='Törnberg (2023) LLM verbalized confidence',
            notes='v3.4.0: pure LLM confidence (no keyword fallback, mirrors substantiveness pattern)',
            category='置信度-collab_mode',
            track=_trk,
        )
        metadata[f'category_confidence{_suffix}'] = VariableMetadata(
            var_name=f'category_confidence{_suffix}',
            label=f'Locus Confidence ({_track_en}, LLM+kw hybrid)',
            description=f'innovation_locus{_suffix} 置信度 (LLM × keyword crossvalidation, +0.2 boost / ×0.5 penalty)',
            data_type='float',
            unit='概率',
            value_range='[0, 1]',
            formula='LLM_majority_conf ± boost/penalty by canonicalize_topic agreement',
            source_stage='Stage 21 (article-level, 21_tone_llms.parquet)',
            reference='Gilardi et al. (2023, PNAS) LLM-vs-rule crossvalidation',
            notes='hybrid confidence; raw LLM confidence 在 innovation_locus_confidence_{full,ctx} 列',
            category='置信度-locus',
            track=_trk,
        )

    # ═══ v3.2.0 Dual gate 三互斥指示列 (plan v14 §3.1 Action #6; article 级 bool) ═══
    # 门控口径 (full-only, 用户决策 2026-06-29; 逆转 v3.2.0 R1-A + v3.9.0 三轨并集门):
    #   是否留篇 (21_tone_llms.parquet 行集) 现**仅由全文轨 verified_full** 决定 —— ctx/ss
    #   窗口截断可能漏信息, 降为 conditional-on-full 测度/稳健性轨。下列 dual_* 与 tone_llms
    #   产的 7 互斥态 (full_only/ctx_only/ss_only/full_ctx/full_ss/ctx_ss/all_three) 仍**全量
    #   计算并落盘作诊断**, 但 full-only 下凡 full 未过的态 (dual_ctx_only / triple_ctx_only /
    #   ss_only / ctx_ss) 因对应行已被排除而**结构性恒 False (近零方差)**; 真正进输出的只有
    #   含-full 的态。列名单一事实源 = tone_llms (新 7 态列走 _infer_* 兜底, 此处不凭空注册)。
    for _gate_var, _gate_zh, _gate_en in [
        ('llm_verified_dual_full_only',  '只 full 通过',  'Full-track only'),
        ('llm_verified_dual_ctx_only',   '只 ctx 通过 (full-only 下恒 False)',   'Ctx-track only (empty under full-only)'),
        ('llm_verified_dual_both',       'full 与 ctx 都通过',    'Both full & ctx tracks'),
    ]:
        metadata[_gate_var] = VariableMetadata(
            var_name=_gate_var,
            label=f'Dual Gate: {_gate_en} verified',
            description=f'三互斥诊断指示 ({_gate_zh}): full-only 门控下留篇仅看 verified_full, ctx 仅作 conditional-on-full 测度',
            data_type='bool',
            unit='二元',
            value_range='True | False',
            formula='derived from llm_verified_full / llm_verified_ctx (诊断列; 留篇门控仅 verified_full, 见上注)',
            source_stage='Stage 21 (article-level, 21_tone_llms.parquet)',
            reference='Hassan et al. (2019, QJE) entity-proximity independence',
            notes='full-only gating (用户决策 2026-06-29, 逆转 v3.2.0 R1-A 并集): 留篇仅 verified_full; '
                  'dual_ctx_only / triple_ctx_only / ss_only / ctx_ss 因 full 未过而结构性恒 False (诊断保留)',
            category='Stage 1 gate',
            track='dual',
        )

    return metadata


# ============================================================================
# 3. 自动提取变量统计信息
# ============================================================================

def extract_variable_stats(
    panel: pd.DataFrame,
    var_name: str
) -> Dict[str, Any]:
    """从面板数据中自动提取变量的统计信息

    Args:
        panel: 面板数据
        var_name: 变量名

    Returns:
        包含统计信息的字典
    """
    if var_name not in panel.columns:
        return {}

    series = panel[var_name]
    stats = {
        '观测数': len(series),
        '缺失数': series.isna().sum(),
        '缺失率': f"{series.isna().mean():.2%}",
    }

    # 数值型变量的统计
    if pd.api.types.is_numeric_dtype(series):
        valid = series.dropna()
        if len(valid) > 0:
            stats.update({
                '均值': f"{valid.mean():.4f}",
                '标准差': f"{valid.std():.4f}",
                '最小值': f"{valid.min():.4f}",
                '25分位': f"{valid.quantile(0.25):.4f}",
                '中位数': f"{valid.median():.4f}",
                '75分位': f"{valid.quantile(0.75):.4f}",
                '最大值': f"{valid.max():.4f}",
            })

    # 分类变量的统计
    elif pd.api.types.is_string_dtype(series) or pd.api.types.is_categorical_dtype(series):
        valid = series.dropna()
        if len(valid) > 0:
            value_counts = valid.value_counts()
            stats.update({
                '唯一值数': len(value_counts),
                '最常见值': value_counts.index[0] if len(value_counts) > 0 else '',
                '最常见值频数': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
            })

    return stats


# ============================================================================
# 4. 生成完整的变量代码手册
# ============================================================================

_DEFAULT_CODEBOOK_FORMATS: tuple[str, ...] = ('excel', 'csv', 'markdown', 'json')


def _artifact_size_note(path: str) -> str:
    """读落盘产物字节大小, 返回 ' (xx,xxx B / yy.yy KB)' 文案 (纯日志, golden-safe)。

    白话: 确认 4 个复现产物真的非空、体量符合预期, 供 replication-package 审计核对。
    完全包在 try/except 中, 结果只喂日志、不参与任何计算/返回/产物 (失败则返回空串,
    不影响生成)。整数字节用 :,d, KB 为浮点须经 sig4。
    """
    try:
        _bytes = os.path.getsize(path)
        return f" ({_bytes:,d} B / {sig4(_bytes / 1024.0)} KB)"
    except Exception:  # noqa: BLE001
        return ""


def _apply_dynamic_value_ranges(
    row: Dict[str, Any],
    col: str,
    panel: pd.DataFrame,
) -> Dict[str, Any]:
    """生成时从 panel 动态计算主键取值范围, 覆盖静态 fallback 文案。

    fix(omni-g-codebook-06/-14, 2026-06-11): target_bank 原硬编码 '42家商业银行'
    (盘上实测 87 家, 与同行 唯一值数 字段自相矛盾) → 改 nunique 动态实测。
    fix(omni-g-codebook-01/-08, 2026-06-11): year 原硬编码 '[2013, 2023]'
    (盘上实际 2017–2018) → 改 min–max 动态实测, panel 重生后自愈。
    """
    if col == 'target_bank' and col in panel.columns:
        n_banks = int(panel[col].nunique(dropna=True))
        row['取值范围'] = f'{n_banks}家商业银行 (生成时实测)'
    elif col == 'year' and col in panel.columns:
        yv = pd.to_numeric(panel[col], errors='coerce').dropna()
        if len(yv) > 0:
            row['取值范围'] = f'[{int(yv.min())}, {int(yv.max())}] (生成时实测)'
    return row


def _log_codebook_environment_and_config(
    panel: pd.DataFrame,
    output_dir: str,
    formats: List[str],
) -> None:
    """打印 codebook 生成的【项目/环境 + 输入输出 + 配置 + 方法论依据】块 (日志富集, 2026-06-24)。

    本模块是 runner / stata_export / scripts.generate_codebook 调用的库函数, 无独立 main();
    按"日志富集 playbook §0.5 (called-by-runner helper)"做法, 在被调函数起始处一次性落入
    五大块中的①②③④ (环境/IO/配置/方法论), 结果分析⑤与计时⑥在主流程末尾另行汇总。
    纯日志, 不改任何产物/schema/控制流 (golden-safe); 失败仅 WARN, 绝不中断 codebook 生成。
    """
    try:
        logger.info("  🧭 项目 / 环境信息")
        logger.info("     · 阶段: 变量代码手册生成 (Variable Codebook; stage 45/46 panel→Stata "
                    "导出族的人类可读变量字典层)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板); "
                    "版本 v3.11.1 (rule-ablation-ladder)")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "本阶段纯 CPU·读 panel/写字典 / 无 LLM·网络·API ($0, 确定性)")

        logger.info("  📂 输入 / 输出")
        logger.info(f"     · 输入: 内存 panel DataFrame ({len(panel):,d} 行 × "
                    f"{len(panel.columns):,d} 列; 上游 51_panel_with_controls / 40_panel_yearly)")
        logger.info(f"     · 输出目录: {output_dir}")
        for _fmt in ('excel', 'csv', 'markdown', 'json'):
            _ext = {'excel': 'xlsx', 'csv': 'csv', 'markdown': 'md', 'json': 'json'}[_fmt]
            _on = '✓启用' if _fmt in formats else '—跳过'
            logger.info(f"     · {_on} {_fmt:8s}: variable_codebook.{_ext}")

        logger.info("  ⚙ 运行配置")
        logger.info(f"     · 导出格式: {list(formats)} (默认全 4: {list(_DEFAULT_CODEBOOK_FORMATS)})")
        logger.info(f"     · 文本轨道枚举 (生成期断言): {sorted(_ALLOWED_TRACKS)} "
                    "(非法值 fail-loud raise ValueError)")
        logger.info(f"     · LLM 投票阵容 (单一事实源 config/sentiment.yaml): {_LLM_MODEL_NAMES}")
        logger.info("     · provenance 注入开关 (panel 驱动幂等): "
                    "6-词典 union 5→6 披露 / L&M 第6部 provenance / 规则消融 MATH-1 非可加披露")

        logger.info("  📖 方法论依据 (codebook 内嵌的学术 provenance, emit 进日志)")
        # 白话: 本步生成的"变量代码手册"= 数据字典 = 可复现研究的文档化产物 —— 每列都带
        # source_stage/计算公式/学术引用 provenance (VariableMetadata 字段), 自动落 4 格式
        # data dictionary。Sandve et al. (2013) 的"记录每个结果如何产生 + 把陈述连回产生它
        # 的数据/代码"诸规则, 正是本自动文档化行为本身 (而非被记录变量的测度法) 的方法学锚点。
        logger.info("     · 可复现研究文档化 (codebook 生成行为本身的依据): Sandve, G. K., "
                    "Nekrutenko, A., Taylor, J., & Hovig, E. (2013). Ten simple rules for "
                    "reproducible computational research. PLoS Computational Biology, 9(10), "
                    "e1003285. https://doi.org/10.1371/journal.pcbi.1003285")
        logger.info("     · 金融情感词典 (第6部主词典): Loughran, T., & McDonald, B. (2011). "
                    "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. "
                    "The Journal of Finance, 66(1), 35-65. "
                    "https://doi.org/10.1111/j.1540-6261.2010.01625.x")
        logger.info("       → 为何用: 金融文本情感的标准词表锚点, 中文主译本接入构成 6-词典 union 投票基")
        logger.info("     · 媒体语调度量: Tetlock, P. C. (2007). Giving content to investor sentiment: "
                    "The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. "
                    "https://doi.org/10.1111/j.1540-6261.2007.01232.x")
        logger.info("     · 语调景气循环: García, D. (2013). Sentiment during recessions. "
                    "The Journal of Finance, 68(3), 1267-1300. https://doi.org/10.1111/jofi.12027")
        logger.info("     · 文本分析综述: Loughran, T., & McDonald, B. (2016). Textual analysis in "
                    "accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. "
                    "https://doi.org/10.1111/1475-679X.12123")
        logger.info("     · 词典消融-否定/上下文价移: Kennedy, A., & Inkpen, D. (2006). Sentiment "
                    "classification of movie reviews using contextual valence shifters. "
                    "Computational Intelligence, 22(2), 110-125. "
                    "https://doi.org/10.1111/j.1467-8640.2006.00277.x")
        logger.info("     · 词典消融-整体词典法: Ding, X., Liu, B., & Yu, P. S. (2008). A holistic "
                    "lexicon-based approach to opinion mining. In Proceedings of WSDM '08 (pp. 231-240). "
                    "ACM. https://doi.org/10.1145/1341531.1341561")
        logger.info("     · prob_score 族 LLM 置信校准: Geng, J., Cai, F., Wang, Y., Koeppl, H., "
                    "Nakov, P., & Gurevych, I. (2024). A survey of confidence estimation and calibration "
                    "in large language models. In Proceedings of the 2024 Conference of the North American "
                    "Chapter of the Association for Computational Linguistics: Human Language Technologies "
                    "(Volume 1: Long Papers) (pp. 6577-6595). Association for Computational Linguistics. "
                    "https://doi.org/10.18653/v1/2024.naacl-long.366")
        logger.info("       → 为何用: avg_*_prob_score{,_std} 族取自 LLM 输出 confidence (conf), "
                    "本综述将 ECE 置信校准置于 LLM 时代, 为以 conf 构造 binary prob_score 的做法提供方法学锚点")
        logger.info("     · LLM 标注最佳实践 (llm_vote_tone 族标注效度): Törnberg, P. (2024). "
                    "Best practices for text annotation with large language models. "
                    "Sociologica, 18(2), 67–85. https://doi.org/10.6092/issn.1971-8853/19461")
        logger.info("     · LLM 文本标注风险导航 (社科语境): Lin, H., & Zhang, Y. (2026). "
                    "Navigating the risks of using large language models for text annotation "
                    "in social science research. Social Science Computer Review, 44(3), "
                    "403–427. https://doi.org/10.1177/08944393251366243")
        logger.info("       → 为何用: 本手册 llm_vote_tone_{full,ctx,ss} 等列由三家 LLM 多模型"
                    "合票标注而成, 上两篇为'LLM 作标注器'的效度/风险/可复现提供当代 (2024/2026) "
                    "方法学锚点, 亦支撑 CV-1 负向类近退化 (情感呈单极偏好而非双极) 的诚实披露")
        logger.info("     · 实质/象征二元 (W&Z 1994/1998 ASQ) 与底层/应用二元 (Gomber et al. 2018 JMIS) "
                    "构念见列名后缀正名, 注册表无对应 DOI 故此处仅注名。")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  codebook 环境/配置/方法论信息打印失败 (不影响生成): {e}")


def _log_codebook_result_analysis(
    codebook_df: pd.DataFrame,
    panel: pd.DataFrame,
) -> None:
    """打印 codebook 关键指标解读 (运行结果信息, ⑤; 阈值判读, 日志富集 2026-06-24)。

    对生成的 codebook 做覆盖度自检: 预定义 vs 自动推断占比、学术引用/来源阶段填充率、
    文本轨道分布、面板维度与小样本告警。纯日志读已算出的真实值, 不改任何产物 (golden-safe)。
    """
    try:
        if codebook_df is None or len(codebook_df) == 0:
            logger.warning("  📊 关键指标解读: codebook 为空 (0 变量), 跳过解读")
            return
        n_var = len(codebook_df)

        # ① 自动推断占比 (越低越好 = 越多列有人工预定义元数据)
        _note_col = codebook_df.get('备注')
        n_auto = int(_note_col.astype(str).str.contains(_AUTO_INFER_NOTE, na=False).sum()) \
            if _note_col is not None else 0
        auto_frac = n_auto / n_var if n_var else 0.0
        _v_auto = ('好 (元数据覆盖高)' if auto_frac < 0.30
                   else '临界' if auto_frac < 0.60 else '偏弱 (大量列待人工审核)')
        logger.info(f"     · 自动推断列: {n_auto:,d}/{n_var:,d} = {pct4(auto_frac)} → {_v_auto}")

        # ② 学术引用填充率 (越高越好)
        _cite_col = codebook_df.get('学术引用')
        n_cite = int((_cite_col.astype(str).str.strip() != '').sum()) if _cite_col is not None else 0
        cite_frac = n_cite / n_var if n_var else 0.0
        logger.info(f"     · 含学术引用列: {n_cite:,d}/{n_var:,d} = {pct4(cite_frac)} "
                    "(provenance 注入覆盖度)")

        # ③ 来源阶段已知率 (未知=溯源缺口, 越低越好)
        _src_col = codebook_df.get('来源阶段')
        n_unknown = int((_src_col.astype(str).str.strip() == '未知').sum()) \
            if _src_col is not None else 0
        unk_frac = n_unknown / n_var if n_var else 0.0
        _v_unk = ('好' if unk_frac < 0.10 else '临界' if unk_frac < 0.25 else '偏高 (溯源缺口)')
        logger.info(f"     · 来源阶段=未知: {n_unknown:,d}/{n_var:,d} = {pct4(unk_frac)} → {_v_unk}")

        # ④ 文本轨道分布 (三轨 full/ctx/ss + track-agnostic)
        _trk_col = codebook_df.get('文本轨道')
        if _trk_col is not None:
            _vc = _trk_col.fillna('').astype(str).value_counts()
            _parts = [f"{(k or 'track-agnostic')}={int(v):,d}" for k, v in _vc.items()]
            logger.info(f"     · 文本轨道分布: {' | '.join(_parts)}")

        # ⑤ 面板维度 + 小样本告警
        n_rows = len(panel)
        logger.info(f"     · 面板维度: {n_rows:,d} 行 × {len(panel.columns):,d} 列")
        if n_rows < 200:
            logger.warning(f"     · ⚠ 面板深度仅 {n_rows:,d} 行 (T 小样本, 如 T=2 试跑); "
                           "codebook 统计量 (均值/分位) 仅供结构核对, 非生产规模解读")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  codebook 结果解读打印失败 (不影响生成): {e}")


def generate_codebook(
    panel: pd.DataFrame,
    output_dir: str,
    formats: List[str] | None = None,
) -> Dict[str, str]:
    """生成完整的变量代码手册

    fix(omni-g-codebook, 2026-06-11): 生成期新增两道行为 — 主键 (target_bank/year)
    取值范围从 panel 动态实测覆盖静态 fallback; track 编码非法值 (∉ {'', 'full',
    'ctx', 'dual'}) fail-loud raise ValueError 而非静默进产物。

    Args:
        panel: 面板数据
        output_dir: 输出目录
        formats: 输出格式列表，可选：'excel', 'csv', 'markdown', 'json'.
            None 时取 _DEFAULT_CODEBOOK_FORMATS 全 4 格式.

    Returns:
        生成的文件路径字典
    """
    _stage_start = time.time()
    _phase_durations: Dict[str, float] = {}
    if formats is None:
        formats = list(_DEFAULT_CODEBOOK_FORMATS)
    logger.info("=" * 70)
    logger.info("生成变量代码手册（Variable Codebook）")
    logger.info("=" * 70)

    # 日志富集 (2026-06-24): 环境/IO/配置/方法论 (①-④) 一次性落盘 (纯日志, golden-safe)
    _log_codebook_environment_and_config(panel, output_dir, formats)

    # 获取变量元数据字典
    _t = time.time()
    metadata_dict = get_variable_metadata_dict()
    _phase_durations['①元数据字典构建'] = time.time() - _t
    _t = time.time()

    # 构建完整的代码手册数据
    codebook_data = []
    for col in panel.columns:
        # 获取预定义的元数据
        if col in metadata_dict:
            meta = metadata_dict[col]
            row = meta.to_dict()
        else:
            # 自动推断元数据
            row = {
                '变量名': col,
                '标签': _infer_label(col),
                '描述': _infer_description(col),
                '数据类型': str(panel[col].dtype),
                '单位': '',
                '取值范围': '',
                '计算公式': '',
                '来源阶段': _infer_source_stage(col),
                '学术引用': '',
                '备注': '自动推断的元数据，需要人工审核',
                '变量类别': _infer_category(col),
                '文本轨道': _infer_track(col),
            }

        # v3.10.0 测度变更披露 (plan §R1): 把 union 5→6 / 6-词典扩张披露落到【真实 panel 列】
        # (此前 _UNION_NOTE 仅绑 article 级幻影列 msent_score_* → 永不发射; 见模块顶 _DICT6_* 注释)。
        # panel 驱动注入 → 覆盖 avg_msent/pos_ratio/neg_ratio/dict_avg_* 全部变体; 幂等。
        if _is_dict6_union_affected(col):
            _note = row.get('备注', '') or ''
            if (not _note.strip()) or (_AUTO_INFER_NOTE in _note):
                row['备注'] = _DICT6_DISCLOSURE_NOTE
            elif _DICT6_MARKER not in _note:
                row['备注'] = f'{_note} {_DICT6_DISCLOSURE_NOTE}'
            if not (row.get('学术引用', '') or '').strip():
                row['学术引用'] = _DICT6_CITATION
        elif _is_lm_provenance_col(col):
            # L&M 第 6 部主词典 / 6 子集 frac 的 provenance (新增列, 非变值列; plan §Tier-1.2)
            if not (row.get('学术引用', '') or '').strip():
                row['学术引用'] = _LM_PROVENANCE_CITATION
            _pn = row.get('备注', '') or ''
            if (not _pn.strip()) or (_AUTO_INFER_NOTE in _pn):
                row['备注'] = _LM_PROVENANCE_NOTE + (_LM_NEGONLY_NOTE if 'negonly' in col else '')

        # 规则消融梯度 (v3.11.1): MATH-1 非可加披露 — 对全部 {d}_{sfx}_tone 列幂等追加 (含 negonly,
        # 与上方 LM provenance 块叠加不冲突); 独立 if (非 elif) 故 loughran 消融列既得 provenance 又得 MATH-1。
        if _rule_ablation_match(col):
            if not (row.get('学术引用', '') or '').strip():
                row['学术引用'] = _RULE_ABLATION_CITATION
            _rn = row.get('备注', '') or ''
            if 'audit MATH-1' not in _rn:
                row['备注'] = (_RULE_ABLATION_NOTE
                               if (not _rn.strip() or _AUTO_INFER_NOTE in _rn)
                               else f'{_rn} {_RULE_ABLATION_NOTE}')

        # 政治词权重敏感性 (du_2022 only): Du et al. (2022, RoF) 依据 + 不分主次披露 (独立 if)。
        if _political_weight_match(col):
            if not (row.get('学术引用', '') or '').strip():
                row['学术引用'] = _POLITICAL_WEIGHT_CITATION
            _pwn = row.get('备注', '') or ''
            if '政治词权重敏感性' not in _pwn:
                row['备注'] = (_POLITICAL_WEIGHT_NOTE
                               if (not _pwn.strip() or _AUTO_INFER_NOTE in _pwn)
                               else f'{_pwn} {_POLITICAL_WEIGHT_NOTE}')

        # fix(omni-g-codebook-06/-14/-01, 2026-06-11): 主键取值范围动态实测覆盖
        row = _apply_dynamic_value_ranges(row, col, panel)

        # fix(omni-g-codebook-05, 2026-06-11): 生成期断言 track 编码统一枚举,
        # 防 '全文'/'上下文'/'—' 等混编值再次进入产物
        if row['文本轨道'] not in _ALLOWED_TRACKS:
            raise ValueError(
                f"codebook track 编码非法: 列 {col!r} 的 文本轨道={row['文本轨道']!r}, "
                f"允许枚举 = {sorted(_ALLOWED_TRACKS)}"
            )

        # 添加统计信息
        stats = extract_variable_stats(panel, col)
        row.update(stats)

        codebook_data.append(row)

    # 转换为 DataFrame
    codebook_df = pd.DataFrame(codebook_data)
    _phase_durations['②逐列元数据+统计+provenance注入'] = time.time() - _t

    # 关键指标解读 (⑤): codebook 覆盖度/溯源/轨道分布自检 (纯日志, golden-safe)
    logger.info("  📊 关键指标解读 (codebook 覆盖度自检)")
    _log_codebook_result_analysis(codebook_df, panel)

    # 生成输出文件
    _t = time.time()
    output_files = {}
    os.makedirs(output_dir, exist_ok=True)

    # Excel 格式
    if 'excel' in formats:
        # fix(omni-g-codebook-12, 2026-06-11): 列字母改用 openpyxl get_column_letter —
        # 原 chr(64+idx) 仅支持 A–Z (26 列), idx=27 → '[' 非法列名致 xlsx 崩溃
        # (当前 25 列距边界仅 1 列裕度, latent)。
        from openpyxl.utils import get_column_letter
        excel_path = os.path.join(output_dir, 'variable_codebook.xlsx')
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            codebook_df.to_excel(writer, sheet_name='Codebook', index=False)
            # 调整列宽
            worksheet = writer.sheets['Codebook']
            for idx, col in enumerate(codebook_df.columns, 1):
                # 逐元素 str() 再取 len: nullable Float64/NaN 列上 .astype(str).map(len)
                # 会在 pandas 2.x 留下 float 标量导致 `object of type 'float' has no len()`,
                # 改用 map(lambda v: len(str(v))) 对每个标量先 Python str() 再 len, dtype 无关。
                # 三轨 (third-track _ss, 2026-06-14): 新增 _ss 列的统计值 (mean/std/min/max 等)
                # 同样可能落为 nullable Float64/NaN/<NA> — len(str(v)) 对每个标量逐元素处理,
                # str(np.nan)='nan' / str(pd.NA)='<NA>' 均可 len, 故 ss 列天然受此守卫覆盖。
                # 防御 (空 codebook_df 退化态): .max() 在零行列上返回 NaN → int(NaN) 崩溃,
                # 用 pd.isna 兜底回退 len(col)。
                _per_cell_max = codebook_df[col].map(lambda v: len(str(v))).max()
                max_length = max(
                    int(_per_cell_max) if not pd.isna(_per_cell_max) else 0,
                    len(col)
                )
                worksheet.column_dimensions[get_column_letter(idx)].width = min(max_length + 2, 50)
        output_files['excel'] = excel_path
        logger.info(f"  ✓ Excel 格式: {excel_path}{_artifact_size_note(excel_path)}")

    # CSV 格式
    if 'csv' in formats:
        csv_path = os.path.join(output_dir, 'variable_codebook.csv')
        codebook_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        output_files['csv'] = csv_path
        logger.info(f"  ✓ CSV 格式: {csv_path}{_artifact_size_note(csv_path)}")

    # Markdown 格式
    if 'markdown' in formats:
        md_path = os.path.join(output_dir, 'variable_codebook.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# 变量代码手册（Variable Codebook）\n\n")
            f.write(f"**生成时间**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**变量总数**: {len(codebook_df)}\n\n")
            f.write(f"**面板维度**: {len(panel)} 行 × {len(panel.columns)} 列\n\n")
            f.write("---\n\n")
            f.write(codebook_df.to_markdown(index=False))
        output_files['markdown'] = md_path
        logger.info(f"  ✓ Markdown 格式: {md_path}{_artifact_size_note(md_path)}")

    # JSON 格式
    if 'json' in formats:
        json_path = os.path.join(output_dir, 'variable_codebook.json')
        codebook_dict = codebook_df.to_dict(orient='records')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(codebook_dict, f, ensure_ascii=False, indent=2)
        output_files['json'] = json_path
        logger.info(f"  ✓ JSON 格式: {json_path}{_artifact_size_note(json_path)}")

    _phase_durations['③多格式落盘'] = time.time() - _t

    logger.info(f"\n变量代码手册生成完成！共 {len(codebook_df):,d} 个变量")

    # ⏱ 阶段计时 (墙钟): 各子阶段耗时 + 总耗时 (秒 → sig4; 纯日志, golden-safe)
    try:
        _total = time.time() - _stage_start
        logger.info("  ⏱ 运行期阶段计时 (墙钟, 秒)")
        for _name, _dur in _phase_durations.items():
            _frac = (_dur / _total) if _total > 0 else 0.0
            logger.info(f"     · {_name}: {sig4(_dur)} s ({pct4(_frac)})")
        logger.info(f"     · 合计: {sig4(_total)} s | 生成 {len(output_files):,d} 个格式文件")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  codebook 计时汇总打印失败 (不影响生成): {e}")

    return output_files


# ============================================================================
# 5. 辅助函数：自动推断变量属性
# ============================================================================

# ── 网络构造判据后缀归一 (2026-07-03, 计划 NETWORK_TRITRACK_AND_CRITERIA 层 E) ──
# ② 类结构网络指标的判据变体后缀 _win1 (银行∧银行 ±1 句窗) / _sent (严格同句)。
# ⚠ 三个推断函数 (_infer_label/_infer_source_stage/_infer_category) 入口先剥
# 该后缀再匹配 (镜像 _strip_lg token 剥离先例) — 否则: ① '_sent' 含子串 'sent'
# 被 _infer_category 误归「情感指标」(33 列); ② net_*_yr 的 endswith('_yr')
# 联合判据被后缀破坏落「未知」(20 列)。判据后缀 ≠ 三轨文本后缀 (_full/_ctx/_ss),
# 全仓无既有列以 _win1/_sent 结尾 (终验实测), 剥离对既有列恒为 no-op。
_CRITERIA_SFX_RE = re.compile(r'_(win1|sent)$')
_CRITERIA_SFX_DESC = {
    'win1': 'bank-bank ±1-sent edge',
    'sent': 'bank-bank same-sent edge',
}
# 8 个无 'cent' 子串的节点级结构指标基名 (现状落'未知'的既存缺口, 一并消化;
# 终验 identity-trap-1: 白名单须同时接入 source_stage 与 category 两函数)
_NET_STRUCT_BASES = frozenset({
    'bank_clustering', 'bank_constraint', 'bank_ego_density',
    'bank_effective_size', 'bank_avg_nbr_deg', 'bank_coreness',
    'bank_ci', 'bank_is_hub',
})


def _strip_criteria_suffix(var_name: str) -> tuple:
    """剥判据后缀: 返回 (基名, 'win1'|'sent'|None)。"""
    m = _CRITERIA_SFX_RE.search(var_name)
    if m:
        return var_name[:m.start()], m.group(1)
    return var_name, None


def _infer_label(var_name: str) -> str:
    """自动推断变量标签 (三轨: full/ctx/ss; ss=银行+金科同句共现)"""
    # 判据后缀归一 (2026-07-03): 基名推断 + bank-bank 限定注解 (措辞刻意与
    # `_ss` 银行∧金科文本轨的 'same-sent' 官方压缩词区分, 终验 econ-final-1)
    _crit_base, _crit = _strip_criteria_suffix(var_name)
    if _crit:
        return f'{_infer_label(_crit_base)} ({_CRITERIA_SFX_DESC[_crit]})'
    # 轨道映射
    track_suffix = ''
    if var_name.endswith('_full'):
        track_suffix = ' (Full)'
    elif var_name.endswith('_ctx'):
        track_suffix = ' (Ctx)'
    elif var_name.endswith('_ss'):
        track_suffix = ' (SS; 同句共现)'

    # 基础标签推断
    # 规则消融梯度 (v3.11.1): rule-specific 标签, 须早于泛型 'tone' 分支
    _abl = _rule_ablation_match(var_name)
    if _abl:
        _d = '跨词典均值' if _abl[0] == 'dict_avg' else _abl[0]
        return f'词典语调 {_d} · 规则消融:{_RULE_ABLATION_SFX_DESC[_abl[1]]}{track_suffix}'
    # 政治词权重敏感性 (du_2022 only): rule-specific 标签, 亦须早于泛型 'tone' 分支
    _polw = _political_weight_match(var_name)
    if _polw:
        return f'词典语调 {_polw[0]} · {_POLITICAL_WEIGHT_SFX_DESC[_polw[1]]}{track_suffix}'
    # per-model 语调 (互为稳健性, 2026-07-02): 须早于泛型 'tone'/Title-case 分支, 否则裸
    # {short}_tone / {short}_pos / {short}_net_tone 退化为泛型标签。
    _lm = _llm_model_match(var_name)
    if _lm:
        # 文案按 metric 族分流 (2026-07-03 §2 A4): frac 族是分类占比非语调, 勿顶「语调」字样
        _lm_kind = 'LLM 逐模型分类占比' if _lm[1] in _LLM_CLASS_METRICS else 'LLM 逐模型语调'
        return (f'{_lm_kind} {_lm[0]} · {_PER_MODEL_METRIC_ZH.get(_lm[1], _lm[1])}'
                f'{_PER_MODEL_WEIGHT_ZH.get(_lm[2], _lm[2])}{track_suffix}')
    _bm = _bert_model_match(var_name)
    if _bm:
        return (f'BERT 逐模型 {_bm[0]} · {_PER_MODEL_METRIC_ZH.get(_bm[1], _bm[1])}'
                f'{_PER_MODEL_WEIGHT_ZH.get(_bm[2], _bm[2])}{track_suffix}')
    if 'tone' in var_name:
        return f'Sentiment Tone{track_suffix}'
    elif 'attn' in var_name or var_name.startswith('ft_vol'):
        return f'Attention Index{track_suffix}'
    elif var_name.startswith('gf_'):
        # 网络指标扩展 2026-06-21: Gould-Fernandez 经纪角色 (无向坍缩)
        return 'GF Brokerage Role (Gould-Fernandez 1989)'
    elif var_name.startswith('brok_bip'):
        # 仅 WS-B 二分图原生; **不**用 startswith('brok') 以免改写既有
        # brokerage_eigen_cent / brokerage_fire_sale 的标签 (MISSING_SCHEMA-2)
        return f'Bipartite Media-Bank Centrality{track_suffix}'
    elif var_name.startswith('net_') and var_name.endswith('_yr'):
        # net_*_yr = 年度网络级结构 (年广播; 年 FE 下不可识别)
        return 'Network-Level Structure (annual)'
    elif 'cent' in var_name:
        return f'Network Centrality{track_suffix}'
    elif 'media' in var_name:
        return f'Media Indicator{track_suffix}'
    else:
        return var_name.replace('_', ' ').title()


def _infer_description(var_name: str) -> str:
    """自动推断变量描述"""
    _abl = _rule_ablation_match(var_name)
    if _abl:
        _d = '跨 6 词典均值' if _abl[0] == 'dict_avg' else f'词典 {_abl[0]}'
        return (f'{_d} 的规则消融梯度变体「{_RULE_ABLATION_SFX_DESC[_abl[1]]}」: '
                f'状态机 Σ|final| 自归一化语调在 bank-year 的均值, 作语言学规则稳健性对照 '
                f'(详见备注 audit MATH-1 非可加披露)。')
    _polw = _political_weight_match(var_name)
    if _polw:
        return (f'词典 {_polw[0]} 的政治词权重敏感性变体「{_POLITICAL_WEIGHT_SFX_DESC[_polw[1]]}」: '
                f'政治正面词权重在 bank-year 的均值。{_POLITICAL_WEIGHT_NOTE}')
    _lm = _llm_model_match(var_name)
    if _lm:
        # NOTE 按 metric 族分流 (2026-07-03 §2 A4): frac 族用分类占比专用 NOTE (含分母口径披露)
        _lm_note = _LLM_CLASS_NOTE if _lm[1] in _LLM_CLASS_METRICS else _LLM_MODEL_NOTE
        return (f'LLM 模型 {_lm[0]} 的 {_PER_MODEL_METRIC_ZH.get(_lm[1], _lm[1])}'
                f'{_PER_MODEL_WEIGHT_ZH.get(_lm[2], _lm[2])} 在 bank-year 的聚合。{_lm_note}')
    _bm = _bert_model_match(var_name)
    if _bm:
        return (f'BERT 模型 {_bm[0]} 的 {_PER_MODEL_METRIC_ZH.get(_bm[1], _bm[1])}'
                f'{_PER_MODEL_WEIGHT_ZH.get(_bm[2], _bm[2])} 在 bank-year 的聚合。{_BERT_MODEL_NOTE}')
    return f'变量 {var_name} 的详细描述（需要人工补充）'


def _infer_source_stage(var_name: str) -> str:
    """自动推断来源阶段

    fix(omni-g-codebook-04/-11, 2026-06-11): 两处系统性错标更正 —
    'attn' 原映射 'Stage 24' (= herd_decay, 与本文件 L162-166 的 2026-06-02 审计
    更正注释直接矛盾): attention 族实际由 stage 45 panel 构建内
    attention_media/encode (compute_fintech_attention_index /
    compute_attention_treatments) 物化;
    network/cent 原映射 'Stage 46' (现行 DAG 的 stage 46 = stata_export, 不产
    指标): 实际在 stage 45 panel 构建 Step 7f/7g 内由 network_spillover.py 计算
    (模块历史名 46_network_spillovers 系遗留编号)。
    """
    # per-model 宽前缀 (2026-07-02, 互为稳健性): 覆盖 deepseekv4_* / fin_sent_zh_* 等
    # 无 llm/gpt/gemini/bert 子串的 per-model 列 (含加权 _vw/_mw/_hw / 计数 / 和变体),
    # 否则窄子串判据漏 → 落 '未知'。llm_vote_* 不以模型名开头故不误命中; 模型名与
    # 词典/网络列名无碰撞 (前置早返回安全)。
    # 判据后缀归一 (2026-07-03, 层 E): 全仓无既有列以 _win1/_sent 结尾 → 恒 no-op 安全
    var_name = _CRITERIA_SFX_RE.sub('', var_name)
    if any(var_name.startswith(m + '_') for m in LLM_MODELS):
        return 'Stage 21'
    if any(var_name.startswith(m + '_') for m in BERT_MODELS):
        return 'Stage 23'
    if 'llm' in var_name or 'gpt' in var_name or 'gemini' in var_name:
        return 'Stage 21'
    elif 'bert' in var_name:
        return 'Stage 23'
    elif (_rule_ablation_match(var_name) or _political_weight_match(var_name)
          or 'dict' in var_name or 'jiang' in var_name
          or 'yao' in var_name or 'loughran' in var_name or 'modal_weak' in var_name
          or 'complexity' in var_name):
        # v3.10.0: loughran (L&M 第 6 部主词典) + LM 新非情感子集 modal_weak/complexity
        # v3.11.1: 规则消融梯度全 6 词典 (含 bian/du/you 的 {sfx}_tone, 否则误落 '未知')
        return 'Stage 22'
    elif 'attn' in var_name or var_name.startswith('ft_vol'):
        # ft_vol_* = 地理注意力总量孪生 (compute_fintech_attention_index, 2026-06-13)
        return 'Stage 40 (panel/attention_media·encode)'
    elif ('network' in var_name or 'cent' in var_name
          or var_name.startswith('gf_') or var_name.startswith('brok')
          or (var_name.startswith('net_') and var_name.endswith('_yr'))
          or var_name in _NET_STRUCT_BASES):
        # 网络指标扩展 2026-06-21: gf_*/brok_bip_*/net_*_yr 一并归网络族
        # (含既有 4 个 net_*_yr — 此前漏 token 误落 '未知', 一并修, §3.1 Q7)
        # 2026-07-03: + 8 个无 'cent' 子串节点基名白名单 (_NET_STRUCT_BASES,
        # 判据后缀已在入口剥离 → 基名精确匹配)
        return 'Stage 40 (panel/network_spillover·network_brokerage)'
    elif ('neg_shock' in var_name or var_name.startswith('bank_cogn')
          or var_name.startswith('emb_peer_tone')
          or var_name.startswith('bank_emb_sim')):
        # 2026-07-03 (计划 D17): industry_neg_shock 三轨 (network_brokerage) +
        # 认知邻近/嵌入相似网族 (network_spillover) — 此前落 '未知' 的既存缺口
        return 'Stage 40 (panel/network_spillover·network_brokerage)'
    elif 'strat' in var_name:
        return 'Stage 25'
    else:
        return '未知'


def _infer_category(var_name: str) -> str:
    """自动推断变量类别"""
    # 判据后缀归一 (2026-07-03, 层 E): 必须在 'sent' 子串分支**之前**剥离 —
    # 否则全部 *_sent 结构网络列被误归「情感指标」(终验 identity-trap-1)
    var_name = _CRITERIA_SFX_RE.sub('', var_name)
    if var_name in ['target_bank', 'year']:
        return '主键'
    elif 'tone' in var_name or 'sent' in var_name or 'neg_shock' in var_name:
        return '情感指标'
    elif 'attn' in var_name or var_name.startswith('ft_vol'):
        return '注意力指数'
    elif ('cent' in var_name or 'network' in var_name
          or var_name.startswith('gf_') or var_name.startswith('brok')
          or (var_name.startswith('net_') and var_name.endswith('_yr'))
          or var_name in _NET_STRUCT_BASES
          or var_name.startswith('bank_cogn')
          or var_name.startswith('bank_emb_sim')):
        return '网络指标'
    elif 'media' in var_name:
        return '媒体指标'
    elif 'strat' in var_name:
        return '战略差异'
    else:
        return '其他'


def _infer_track(var_name: str) -> str:
    """自动推断文本轨道 (三轨: full/ctx/ss; ss=银行+金科同句共现)"""
    if var_name.endswith('_full'):
        return 'full'
    elif var_name.endswith('_ctx'):
        return 'ctx'
    elif var_name.endswith('_ss'):
        return 'ss'
    else:
        return ''

