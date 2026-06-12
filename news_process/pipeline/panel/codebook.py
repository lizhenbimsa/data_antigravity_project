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
from typing import Any, Dict, List

import pandas as pd

from news_process.core.config import load_config

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
_ALLOWED_TRACKS = frozenset({'', 'full', 'ctx', 'dual'})


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
            track: 文本轨道（full/ctx）
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
        # fix(omni-g-codebook-04, 2026-06-11): 原 'Stage 45/46' — 现行 DAG stage 46 =
        # stata_export 不产指标, 该列在 stage 45 panel encode 内物化
        source_stage='Stage 45 (panel/encode compute_fintech_attention_index)',
        reference='Da et al. (2011, JF); Fang & Peress (2009, JF)',
        notes='媒体覆盖率范式 (coverage ratio) 的年度基准; 无距离衰减 (距离衰减仅用于 '
              'ft_attn_prov / ft_attn_city 地理变体)。实测值域 ≈ [0.23, 0.30]',
        category='注意力指数',
        track='',
    )

    # ═══ P2 attention 处理变量 (bank_fintech_attention) ═══
    # fix(omni-g-codebook-03, 2026-06-11): 族级锚点与 attention_media.py:227-231 更正对齐 —
    # 主处理 attention_index = ln(1+Σ intensity) 是 **extensive 累积曝光** (Fang & Peress 2009 JF),
    # **不是** Hassan et al. (2019 QJE) intensive 归一化份额; intensive 对应 attention_pct/density。
    # W2 (2026-06-05): compute_attention_treatments 物化。双轨=互为稳健性 (main=full, robustness=ctx
    # 分离复跑)。零-fintech bank-year: index/pct/density→0 (真零曝光), disp/sd/gap/share→NaN。
    _ATTN_TREAT = [
        ('attention_index_full', 'Fintech Attention Index (full)', 'full',
         'ln(1 + Σ_d fintech_intensity_score_full)', '[0, +inf)',
         '银行-年累积 fintech 曝光强度 (全文口径); P2 主处理变量 (cumulative attention without sign); '
         'extensive 累积曝光, 非 Hassan intensive 归一化份额 (intensive 对应 attention_pct/density)'),
        ('attention_index_ctx', 'Fintech Attention Index (ctx)', 'ctx',
         'ln(1 + Σ_d fintech_intensity_score_ctx)', '[0, +inf)',
         '同上, 实体窗口口径 (entity-context 窗口归因); 双轨稳健性: 与 _full 分离复跑; '
         'extensive 累积曝光, 非 Hassan intensive 份额'),
        ('attention_pct_full', 'Fintech Attention Share', '',
         'N_ft / N_all (12_full 全部银行新闻为分母)', '[0, 1]',
         'fintech 新闻占该行该年全部新闻的议程份额 (track-agnostic 单轨, Fang-Peress 2009 JF)'),
        ('attention_disp_full', 'Fintech Attention Dispersion (outlet HHI)', '',
         'Σ_o (n_o / Σn)²  on 媒体(中文)', '[0, 1]',
         '跨媒体曝光集中度 (HHI, 单 outlet=1); 零-fintech→NaN (track-agnostic, Cookson-Niessner 2020 JF)'),
        ('attention_intensity_density_full', 'Attention Intensity Density (full)', 'full',
         'Σ_d fintech_intensity_score_full / N_all', '[0, +inf)',
         '强度加权曝光密度 (非[0,1]故非"share"名); 双轨稳健性载体'),
        ('attention_intensity_density_ctx', 'Attention Intensity Density (ctx)', 'ctx',
         'Σ_d fintech_intensity_score_ctx / N_all', '[0, +inf)',
         '同上, 实体窗口口径; 与 _full 分离复跑'),
        ('attention_intensity_sd_full', 'Attention Intensity SD (full)', 'full',
         'std_d(fintech_intensity_score_full), ddof=1', '[0, +inf)',
         '篇间 fintech 技术强度离散 (二阶矩); N<2→NaN; disp 真双轨载体'),
        ('attention_intensity_sd_ctx', 'Attention Intensity SD (ctx)', 'ctx',
         'std_d(fintech_intensity_score_ctx), ddof=1', '[0, +inf)',
         '同上, 实体窗口口径; 双轨相关最低 (实跑 0.656), 最强稳健性'),
        ('attention_gap_full_ctx', 'Attention Attribution Gap', '',
         'mean_d(intensity_full − intensity_ctx)', '(-inf, +inf)',
         '双轨派生: 注意力借位/稀释度 (full 相对 ctx 的非本行归因量); 机制变量'),
        ('attention_attr_share', 'Attention Attribution Purity', '',
         'clip(Σ_d ctx / Σ_d full, 0, 1)', '[0, 1]',
         '双轨派生: 归因纯度 (指向本行的 fintech 注意力占比); Σfull=0→NaN'),
        ('n_fintech_articles', 'N fintech articles', '',
         'count(fintech 文章 in bank-year)', '[0, +inf)',
         'extensive-margin baseline 计数 (诊断/对照, track-agnostic)'),
        ('n_outlets', 'N distinct outlets', '',
         'nunique(媒体(中文) over fintech 文章)', '[0, +inf)',
         'HHI 可算性诊断 (n_outlets≥2 才有 disp 变异); 零-fintech→NaN'),
    ]
    for _vn, _lbl, _trk, _fml, _rng, _desc in _ATTN_TREAT:
        # fix(omni-g-codebook-03, 2026-06-11): attention_index_* 是 extensive 累积曝光
        # (Fang & Peress 2009 JF 主锚, Hassan 2019 QJE 仅作 cf. 对照), 其余列保持族级共引。
        if _vn.startswith('attention_index'):
            _ref = ('Fang & Peress (2009, JF) extensive coverage; '
                    'cf. Hassan et al. (2019, QJE) intensive share; '
                    'Cookson & Niessner (2020, JF)')
        else:
            _ref = ('Hassan et al. (2019, QJE); Fang & Peress (2009, JF); '
                    'Cookson & Niessner (2020, JF)')
        metadata[_vn] = VariableMetadata(
            var_name=_vn, label=_lbl, description=_desc, data_type='float',
            unit='比率' if _rng == '[0, 1]' else '',
            value_range=_rng, formula=_fml,
            source_stage='Stage 45 (panel/attention_media compute_attention_treatments)',
            reference=_ref,
            notes='W2 物化 (2026-06-05); 双轨=互为稳健性 (main=full / robustness=ctx 分离复跑); '
                  '零-fintech bank-year 填 0(index/pct/density) 或 NaN(disp/sd/gap/share)',
            category='注意力指数', track=_trk,
        )

    # ═══ 文章计数口径 (物理篇数 vs LLM 有效投票篇数) ═══
    # metric-audit 2026-06-02 (nart-02 codebook 缺新列): encode-02 重构区分两个
    # 口径 — n_articles = 物理新闻覆盖篇数 (含 LLM 失败/NA 行, 供 ln_news_coverage /
    # falsification 等 coverage 消费者); n_articles_llm_valid(_ctx) = LLM 有效投票
    # 篇数, 用作所有分类组成型 frac (tech/app/sub/symb/indep/collab) 的分母, 保证
    # 分子分母同口径 (encode.py:579-588)。补这三列的 codebook 条目消除元数据缺口。
    metadata['n_articles'] = VariableMetadata(
        var_name='n_articles',
        label='N articles (physical coverage)',
        description='该 Bank-Year 的物理新闻覆盖篇数 (组内全部行, 含 LLM 投票失败 / NA 行); '
                    '用作媒体覆盖度 (ln_news_coverage) 与 falsification 的曝露量',
        data_type='int',
        unit='篇',
        value_range='[0, +∞)',
        formula="size(llm_vote_score_full)  (groupby bank-year 行数, 含 NA)",
        source_stage='Stage 45 (panel/encode aggregate_panel)',
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
        source_stage='Stage 45 (panel/encode aggregate_panel)',
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
        source_stage='Stage 45 (panel/encode aggregate_panel)',
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
    metadata['llm_vote_tone_full'] = VariableMetadata(
        var_name='llm_vote_tone_full',
        label='LLM Vote Tone (Full-text)',
        description='LLM投票情感指数（全文轨道），基于多个大语言模型的投票结果',
        data_type='float',
        unit='情感值',
        value_range='[-1, 1]',
        formula='(n_pos - n_neg) / (n_pos + n_neg + n_neu)',
        source_stage='Stage 21',
        reference='Cao et al. (2025, Working Paper)',
        notes=_llm_lineup_note,
        category='情感指标',
        track='full',
    )

    metadata['llm_vote_tone_ctx'] = VariableMetadata(
        var_name='llm_vote_tone_ctx',
        label='LLM Vote Tone (Context)',
        description='LLM投票情感指数（上下文轨道），仅分析包含目标银行的句子及其前后文',
        data_type='float',
        unit='情感值',
        value_range='[-1, 1]',
        formula='(n_pos - n_neg) / (n_pos + n_neg + n_neu)',
        source_stage='Stage 21',
        reference='Cao et al. (2025, Working Paper)',
        notes=f'上下文轨道可以减少噪音，提高情感识别的精确度；{_llm_lineup_note}',
        category='情感指标',
        track='ctx',
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
        source_stage='Stage 45 (panel/network_spillover, 历史模块名 46_network_spillovers)',
        reference='Freeman (1979, Social Networks)',
        notes='度中心度越高，表示该银行与其他银行共同出现在新闻中的频率越高',
        category='网络指标',
        track='',
    )

    # ═══ Innovation Substantiveness 子集 LLM Tone (v3.1.0, W&Z 1998 ASQ) ═══
    # 12 列: 3 LLM × (_sub|_symb) × (_full|_ctx)
    # 使用 encode.py 的 LLM_MODELS 避免硬编码不同步
    from news_process.pipeline.panel.encode import LLM_MODELS as _ISS_LLM_MODELS
    _ISS_SUBSETS = {
        '_sub':  {'panel_value': '实质性', 'zh': '实质性', 'en': 'Substantive'},
        '_symb': {'panel_value': '象征性', 'zh': '象征性', 'en': 'Symbolic'},
    }
    _ISS_TRACKS = {'_full': ('全文', 'Full-text'), '_ctx': ('上下文', 'Context')}
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
                    source_stage='Stage 45 (panel/encode aggregate_panel)',
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
        source_stage='Stage 45 (panel/encode aggregate_panel)',
        reference='Adner & Kapoor (2010) SMJ; Gomber et al. (2018) JMIS',
        notes='探索性指标 - 无预先理论符号; 实证用途仅作描述统计或交互项. '
              'min ≥ 5 过滤防 compositional confound (R8 audit). '
              '对称于 tone_gap_sub_symb (v3.0.0) 但增加 min 过滤.',
        category='情感指标-locus 子集',
        track='full',
    )

    # ═══ v3.2.0 Stage 3 双轨 prob_score bank-year 聚合 (plan v1.37 P2) ═══
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
    ]:
        _trk = _suffix.lstrip('_')  # 'full' / 'ctx' 标准枚举值
        # ─── Plan v1.37 P2: 4 binary prob_score columns per track ───
        metadata[f'avg_subst_prob_score{_suffix}'] = VariableMetadata(
            var_name=f'avg_subst_prob_score{_suffix}',
            label=f'Avg Subst P_BIN ({_track_en}, 1=symbolic)',
            description=f'平均 binary prob_score for innovation_substantiveness {_track_zh}轨',
            data_type='float',
            unit='概率',
            value_range='[0, 1]',
            formula=f'mean(compute_prob_score_binary(label, conf, positive_class="象征性")) over models on innovation_substantiveness{_suffix}',
            source_stage='Stage 21 (article-level) → Stage 45 (bank-year mean)',
            reference='Cover & Thomas (2006) §2 Bernoulli entropy; Jaynes (1957); Törnberg (2024)',
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
            source_stage='Stage 45 panel aggregation',
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
            source_stage='Stage 21 (article-level) → Stage 45 (bank-year mean)',
            reference='Cover & Thomas (2006) §2; Jaynes (1957); Törnberg (2024); Shapiro et al. (2022 J.Econometrics)',
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
            source_stage='Stage 45 panel aggregation',
            reference='Plan v1.37 P2 §5.3.2',
            notes=_PROB_STD_NOTE,
            category='prob_score-locus',
            track=_trk,
        )

    # ═══ 分类组成型 frac (panel 真实聚合列) ═══
    # fix(omni-g-codebook-10, 2026-06-11): 把原 13 个死条目承载的三维分类引文转移到
    # panel 中真实存在的 bank-year 聚合 frac 列 (encode.py:1039-1048/1117-1122/
    # 1188-1192/1238-1243/1308-1312/1370-1375); 分母 = 同轨 n_articles_llm_valid(_ctx)
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
            source_stage='Stage 45 (panel/encode aggregate_panel)',
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
            source_stage='Stage 45 (panel/encode aggregate_panel)',
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
            source_stage='Stage 45',
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
            source_stage='Stage 45',
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
            source_stage='Stage 45',
            reference='W&Z (1998, ASQ); Bingler et al. (2022, FRL)',
            notes='对角线列 _sc × _ctx; 论文用作 entity-proximate substantiveness measure',
            category='情感指标-substantiveness 子集 (ctx)',
            track='ctx',
        )

    # ═══ tone_gap 双轨对角线 ═══
    metadata['tone_gap_tech_app_lc_ctx'] = VariableMetadata(
        var_name='tone_gap_tech_app_lc_ctx',
        label='Tone Gap: Tech-App (Loc=Ctx, ctx sentiment)',
        description='Tech 子集 LLM 投票情感 - App 子集 (entity-ctx classification + ctx sentiment)',
        data_type='float',
        unit='情感差值',
        value_range='[-2, +2] ∪ NaN',
        formula='llm_vote_tone_tech_lc_ctx - llm_vote_tone_app_lc_ctx if min(n_tech, n_app) >= 5 else NaN',
        source_stage='Stage 45',
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
        source_stage='Stage 45',
        reference='Westphal & Zajac (1998, ASQ); Bingler et al. (2022, FRL)',
        notes='ctx 轨同构 tone_gap_sub_symb; 论文洗稿率指标核心 ctx 版本',
        category='情感指标-substantiveness 子集 (ctx)',
        track='ctx',
    )

    # ═══ v3.5.1 A1 Lexical Clarity (真双轨, LM 2011 JF + You 2018 hhx055) ═══
    # 锚定: Loughran & McDonald (2011) JF 66(1) uncertain dictionary;
    #       You et al. (2018) hhx055 Panel C (388 definite) / Panel D (178 ambiguous);
    #       Bonsall, Leone, Miller, Rennekamp (2017) JAE 63(2-3).
    # 真双轨: _compute_clarity_for_text 对 content_full + content_ctx 独立扫描;
    # title 轨不纳入 (修 R3-H1: title 文本 < 50 字符分母不稳).
    metadata['mean_clarity_score_full'] = VariableMetadata(
        var_name='mean_clarity_score_full',
        label='Mean Clarity Score from indep Full-text scan (LM 2011 JF; You 2018)',
        description='Bank-year 加权平均 clarity_score; 基于 content_full 独立词典扫描',
        data_type='float',
        unit='clarity ratio',
        value_range='[-1, +1]',
        formula='Σ w_i × clarity_score_full_i / Σ w_i; clarity_score = frac_definite − frac_ambiguous',
        source_stage='Stage 22 (tone_words) + Stage 45 (encode_collab apply_v3_5_1)',
        reference='Loughran & McDonald (2011) JF 66(1); You et al. (2018) hhx055',
        notes='v3.5.1 A1 真双轨独立扫描; 与 LLM substance 做 HTMT discriminant validity (stage 39d)',
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
        source_stage='Stage 22 + Stage 45',
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
        source_stage='Stage 22 + Stage 45',
        reference='You et al. (2018) hhx055 Panel C',
        notes='clarity 双轨连续备份; 与 frac_amb_articles 二值化指标互补',
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
        source_stage='Stage 22 + Stage 45',
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
        source_stage='Stage 22 + Stage 45',
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
        source_stage='Stage 22 + Stage 45',
        reference='You et al. (2018) hhx055 Panel D',
        notes='ctx 双轨二值化; 与 frac_amb_articles_full 配对',
        category='Lexical Clarity (v3.5.1 A1)',
        track='ctx',
    )

    # ═══ v3.5.1 A3 Numerical Intensity (真双轨, 数值披露强度; 2026-06-05 引文勘误见 reference) ═══
    metadata['mean_num_intensity_full'] = VariableMetadata(
        var_name='mean_num_intensity_full',
        label='Mean Numerical Intensity Full (dual-track)',
        description='Bank-year 加权平均量化披露强度; 基于 content_full + cn2arab + 正则独立扫描',
        data_type='float',
        unit='digits per sentence',
        value_range='[0, +∞) ∪ NaN',
        formula='Σ w_i × (n_digits_full_i / n_sentences_full_i) / Σ w_i; n_sentences lookahead/behind 排除小数点',
        source_stage='Stage 22 (tone_words post-processor enrich_with_num_intensity_dual_track) + Stage 45',
        reference='Davis & Tama-Sweet (2012) CAR 29(3); 公式为项目自定义操作化 (2026-06-05 引文勘误: 原引 Hales-Kuang-Venkataraman 2011 系误归, 该文实为 JAR 49(1) 论 vivid/pallid 语言, 未定义 numerical intensity)',
        notes='v3.5.1 A3 真双轨; cn2arab 5 标准样例 frozen at D0; 不定数 (几千/数十亿) 不计为 token (修 R7-M2); 中文 sentence 分母与英文文献不直接可比 (paper §3.4 disclosure 修 R7-M1)',
        category='Numerical Intensity (v3.5.1 A3)',
        track='full',
    )

    metadata['mean_num_intensity_ctx'] = VariableMetadata(
        var_name='mean_num_intensity_ctx',
        label='Mean Numerical Intensity Ctx (dual-track)',
        description='Bank-year 加权平均 num_intensity; ctx 轨独立扫描',
        data_type='float',
        unit='digits per sentence',
        value_range='[0, +∞) ∪ NaN',
        formula='Σ w_i × (n_digits_ctx_i / n_sentences_ctx_i) / Σ w_i',
        source_stage='Stage 22 + Stage 45',
        reference='Davis & Tama-Sweet (2012) CAR 29(3); 公式为项目自定义操作化 (原引 Hales 2011 系误归, 见 full 轨 reference)',
        notes='ctx 残半句已被 entity_context 完整句号过滤 (修 R3-H3)',
        category='Numerical Intensity (v3.5.1 A3)',
        track='ctx',
    )

    # ═══ 文本测度缺口补全 (2026-06-05, 批 #1–#15): 词汇复杂度/披露质量/新闻显著性 ═══
    # 全 $0 (jieba/posseg/纯解析); 真双轨; 详见 lexical_complexity.py / news_salience.py +
    # scripts/audit/TEXTUAL_MEASURE_GAP_AUDIT_2026-06-05.md。
    _CAT_NEW = 'Text Complexity/Disclosure (2026-06-05)'
    # (col_base, label, unit, value_range, formula, reference, source_stage)
    _DUAL_TEXT_SPECS = [
        ('avg_rare_word', 'Rare-Word Ratio', 'token fraction', '[0,1] ∪ NaN',
         'bank-year mean of (低频词 token / 总 token); 低频=jieba 冻结词典词频≤P20 cutoff(实测覆盖~57% distinct词, 实为"非高频词率")',
         'You & Zhang (2009) RAS 14(4); Gentzkow-Kelly-Taddy (2019) JEL 57(3)', 'Stage 22 (lexical_complexity) + Stage 45'),
        ('avg_hard_char', 'Hard-Char Ratio', 'char fraction', '[0,1] ∪ NaN',
         'bank-year mean of (非常用汉字 / 全部汉字); 常用字=jieba 词典字频累计 99.5% 派生集',
         '丘心颖等 (2016) 经济学(季刊) 15(4):1483; Dale & Chall (1948)', 'Stage 22 (lexical_complexity) + Stage 45'),
        ('avg_nominalization', 'Nominalization Ratio', 'token fraction', '[0,1] ∪ NaN',
         'bank-year mean of (vn/an 词性+性/化/度/型/制 后缀名词 / 总 token); posseg 近似(含专名 nr 小幅高估)',
         'Bonsall-Leone-Miller-Rennekamp (2017) JAE 63(2-3) Bog 句法成分', 'Stage 22 (lexical_complexity) + Stage 45'),
        ('avg_function_word', 'Function-Word Ratio (LIWC Analytic 近似)', 'token fraction', '[0,1] ∪ NaN',
         'bank-year mean of (u/p/c/r/y/e 虚词词性 / 总 token); 虚词占比高≈低分析性',
         'LIWC Analytic 维中文近似', 'Stage 22 (lexical_complexity) + Stage 45'),
        ('avg_specificity', 'Specificity / Hard-Info Density', 'token fraction', '[0,1] ∪ NaN',
         'bank-year mean of ((nr/ns/nt/nz 实体 + m 数词)/总 token); reframe=报道硬信息密度(非10-K披露); posseg 粗近似',
         'Hope, Hu & Lu (2016) RAS 21(4):1005', 'Stage 22 (lexical_complexity) + Stage 45'),
        ('avg_within_doc_redund', 'Within-Document Redundancy', 'ratio', '[0,1] ∪ NaN',
         'bank-year mean of (1 − 唯一字符3-gram/全部字符3-gram); 篇内自重复(与 staleness 跨篇正交)',
         'Dyer-Lang-Stice-Lawrence (2017) JAE 64(2-3); Cazier & Pfeiffer (2016)', 'Stage 22 (lexical_complexity) + Stage 45'),
        ('avg_adversative', 'Adversative-Conjunction Ratio', 'token fraction', '[0,1] ∪ NaN',
         'bank-year mean of (独立逆接连词表命中/总 token); 探索性, 不复用情感轨 adversative_words',
         '徐巍-姚振晔-陈冬华 (2021) 会计研究 (3):28; Ding-Liu-Yu (2008) WSDM', 'Stage 22 (lexical_complexity) + Stage 45'),
        ('avg_word_count', 'Avg Word Count (jieba)', 'words', '[0, +∞) ∪ NaN',
         'bank-year mean of 文章 jieba 词数(去空白)',
         'Li (2008) JAE 45(2-3) 篇幅代理', 'Stage 22 (lexical_complexity) + Stage 45'),
        ('ln_word_count', 'Article Length ln(1+avg_words) 词口径 MLENGTH', 'ln words', '[0, +∞) ∪ NaN',
         'ln(1 + avg_word_count); 真词口径 MLENGTH (区别于字符口径 avg_article_length)',
         'Li (2008) JAE 45(2-3); He et al. (2024) IRFA', 'Stage 45 (geography)'),
        ('mean_num_intensity_word', 'Numerical Intensity per-Word (§4.3)', 'digits per word', '[0, +∞) ∪ NaN',
         'bank-year 加权均值 of (数字 token / jieba 词数); 句级 num_intensity 的词级替代版, 对中文句读 sparse 稳健',
         'Davis & Tama-Sweet (2012) CAR 29(3) (构念; 公式为项目自定义)', 'Stage 22 (numerical_intensity) + Stage 45'),
        ('tone_volatility', 'Tone Volatility (rolling SD)', 'std', '[0, +∞) ∪ NaN',
         'per-bank 3-year rolling std of llm_vote_tone (min_periods=2); 时间维二阶矩(与年内SD/反转正交)',
         'De Bondt-Thaler (1985) 反转之二阶矩补全', 'Stage 45 (runner i2)'),
        ('lazy_jaccard', 'YoY Text Change — Jaccard', 'distance', '[0,1] ∪ NaN',
         '相邻年(t,t-1)同行聚合文本 1 − jieba 词集 Jaccard; 首年 NaN',
         'Cohen, Malloy & Nguyen (2020) JF 75(3):1371', 'Stage 45 (strategic_diff)'),
        ('lazy_overlap', 'YoY Text Change — Word-Overlap', 'distance', '[0,1] ∪ NaN',
         '相邻年 1 − |A∩B|/min(|A|,|B|) 词集; 首年 NaN',
         'Cohen, Malloy & Nguyen (2020) JF 75(3):1371', 'Stage 45 (strategic_diff)'),
        ('lazy_minedit', 'YoY Text Change — Norm-Levenshtein', 'distance', '[0,1] ∪ NaN',
         '相邻年 归一化编辑距离(rapidfuzz, 截断前2000字); 首年 NaN',
         'Cohen, Malloy & Nguyen (2020) JF 75(3):1371', 'Stage 45 (strategic_diff)'),
    ]
    for _base, _label, _unit, _vr, _formula, _ref, _src in _DUAL_TEXT_SPECS:
        for _tk, _tn in (('_full', 'full'), ('_ctx', 'ctx')):
            metadata[f'{_base}{_tk}'] = VariableMetadata(
                var_name=f'{_base}{_tk}', label=f'{_label} ({_tn})',
                description=f'{_label}; bank-year 聚合, {_tn} 轨', data_type='float',
                unit=_unit, value_range=_vr, formula=_formula, source_stage=_src,
                reference=_ref, category=_CAT_NEW, track=_tn)

    # 新闻体裁显著性 (#8–#10, 非双轨; 版面/页号/作者 解析, Tetlock 2007/2008; Boudoukh 2019 RFS)
    _SINGLE_TEXT_SPECS = [
        ('frac_front_page', 'Front-Page Coverage Frac', '[0,1] ∪ NaN',
         'bank-year mean of is_front_page (头版/要闻 或 A叠首页)', 'Tetlock (2007) JF 62(3); Boudoukh et al. (2019) RFS', 'Stage 11 (news_salience) + Stage 45'),
        ('frac_front_section', 'Front-Section Coverage Frac', '[0,1] ∪ NaN',
         'bank-year mean of is_front_section (版面含头版/要闻/头条关键词)', 'Tetlock (2007) JF 62(3)', 'Stage 11 (news_salience) + Stage 45'),
        ('avg_page_rank', 'Avg Page Prominence (lower=front)', 'rank ∪ NaN',
         'bank-year mean of page_rank=叠字母序×100+页码 (越小越显著)', 'Tetlock (2007) JF 62(3); Boudoukh et al. (2019) RFS', 'Stage 11 (news_salience) + Stage 45'),
        ('staff_written_frac', 'Staff-Written (Byline) Frac', '[0,1] ∪ NaN',
         'bank-year mean of has_byline (作者具名且非通讯社)', '来源原创性 (投入端, 与 media_authority/herd 正交)', 'Stage 11 (news_salience) + Stage 45'),
        ('wire_frac', 'Wire-Service Frac', '[0,1] ∪ NaN',
         'bank-year mean of is_wire (作者/电头命中通讯社)', '通稿/转载来源', 'Stage 11 (news_salience) + Stage 45'),
        ('frac_target_in_lead', 'Target-in-Lead Frac', '[0,1] ∪ NaN',
         'bank-year mean of target_in_lead (规范行名出现在标题或正文前2句)', 'Tetlock (2008); Boudoukh et al. (2019) RFS relevance/centrality', 'Stage 11 (news_salience) + Stage 45'),
        ('coverage_active_days', 'Active Coverage Days per Year', 'days ∪ NaN',
         'bank-year 内有报道的不同日历天数(nunique 日期)', 'Hillert-Jacobs-Müller (2014) RFS', 'Stage 45 (encode)'),
        ('coverage_continuity', 'Coverage Continuity (active/span)', '[0,1] ∪ NaN',
         'coverage_active_days / (报道跨度天数); 1=天天有, 低=爆发式 (节奏, 与 staleness 内容重复正交)', 'Hillert-Jacobs-Müller (2014) RFS', 'Stage 45 (encode)'),
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
            reference='Törnberg (2024) LLM verbalized confidence',
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
    for _gate_var, _gate_zh, _gate_en in [
        ('llm_verified_dual_full_only',  '只 full 通过',  'Full-track only'),
        ('llm_verified_dual_ctx_only',   '只 ctx 通过',   'Ctx-track only'),
        ('llm_verified_dual_both',       '双轨都通过',    'Both tracks'),
    ]:
        metadata[_gate_var] = VariableMetadata(
            var_name=_gate_var,
            label=f'Dual Gate: {_gate_en} verified',
            description=f'三互斥指示 ({_gate_zh}): R1-A 致命修复, ctx 轨独立可作 main spec',
            data_type='bool',
            unit='二元',
            value_range='True | False',
            formula='derived from llm_verified_full / llm_verified_ctx',
            source_stage='Stage 21 (article-level, 21_tone_llms.parquet)',
            reference='Hassan et al. (2019, QJE) entity-proximity independence',
            notes='plan v14 §3.1 P1 R1-A: 改并集 verified_full | verified_ctx 修复',
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
    if formats is None:
        formats = list(_DEFAULT_CODEBOOK_FORMATS)
    logger.info("=" * 70)
    logger.info("生成变量代码手册（Variable Codebook）")
    logger.info("=" * 70)

    # 获取变量元数据字典
    metadata_dict = get_variable_metadata_dict()

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

    # 生成输出文件
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
                max_length = max(
                    int(codebook_df[col].map(lambda v: len(str(v))).max()),
                    len(col)
                )
                worksheet.column_dimensions[get_column_letter(idx)].width = min(max_length + 2, 50)
        output_files['excel'] = excel_path
        logger.info(f"  ✓ Excel 格式: {excel_path}")

    # CSV 格式
    if 'csv' in formats:
        csv_path = os.path.join(output_dir, 'variable_codebook.csv')
        codebook_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        output_files['csv'] = csv_path
        logger.info(f"  ✓ CSV 格式: {csv_path}")

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
        logger.info(f"  ✓ Markdown 格式: {md_path}")

    # JSON 格式
    if 'json' in formats:
        json_path = os.path.join(output_dir, 'variable_codebook.json')
        codebook_dict = codebook_df.to_dict(orient='records')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(codebook_dict, f, ensure_ascii=False, indent=2)
        output_files['json'] = json_path
        logger.info(f"  ✓ JSON 格式: {json_path}")

    logger.info(f"\n变量代码手册生成完成！共 {len(codebook_df)} 个变量")
    return output_files


# ============================================================================
# 5. 辅助函数：自动推断变量属性
# ============================================================================

def _infer_label(var_name: str) -> str:
    """自动推断变量标签"""
    # 轨道映射
    track_suffix = ''
    if var_name.endswith('_full'):
        track_suffix = ' (Full)'
    elif var_name.endswith('_ctx'):
        track_suffix = ' (Ctx)'

    # 基础标签推断
    if 'tone' in var_name:
        return f'Sentiment Tone{track_suffix}'
    elif 'attn' in var_name:
        return f'Attention Index{track_suffix}'
    elif 'cent' in var_name:
        return f'Network Centrality{track_suffix}'
    elif 'media' in var_name:
        return f'Media Indicator{track_suffix}'
    else:
        return var_name.replace('_', ' ').title()


def _infer_description(var_name: str) -> str:
    """自动推断变量描述"""
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
    if 'llm' in var_name or 'gpt' in var_name or 'gemini' in var_name:
        return 'Stage 21'
    elif 'bert' in var_name:
        return 'Stage 23'
    elif 'dict' in var_name or 'jiang' in var_name or 'yao' in var_name:
        return 'Stage 22'
    elif 'attn' in var_name:
        return 'Stage 45 (panel/attention_media·encode)'
    elif 'network' in var_name or 'cent' in var_name:
        return 'Stage 45 (panel/network_spillover)'
    elif 'strat' in var_name:
        return 'Stage 25'
    else:
        return '未知'


def _infer_category(var_name: str) -> str:
    """自动推断变量类别"""
    if var_name in ['target_bank', 'year']:
        return '主键'
    elif 'tone' in var_name or 'sent' in var_name:
        return '情感指标'
    elif 'attn' in var_name:
        return '注意力指数'
    elif 'cent' in var_name or 'network' in var_name:
        return '网络指标'
    elif 'media' in var_name:
        return '媒体指标'
    elif 'strat' in var_name:
        return '战略差异'
    else:
        return '其他'


def _infer_track(var_name: str) -> str:
    """自动推断文本轨道"""
    if var_name.endswith('_full'):
        return 'full'
    elif var_name.endswith('_ctx'):
        return 'ctx'
    else:
        return ''

