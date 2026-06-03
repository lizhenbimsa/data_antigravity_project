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
    metadata['target_bank'] = VariableMetadata(
        var_name='target_bank',
        label='Target Bank',
        description='目标银行名称（标准化后的银行全称）',
        data_type='str',
        unit='',
        value_range='42家商业银行',
        formula='',
        source_stage='Stage 11',
        reference='',
        notes='面板数据的银行维度主键',
        category='主键',
        track='',
    )

    metadata['year'] = VariableMetadata(
        var_name='year',
        label='Year',
        description='年份',
        data_type='int',
        unit='年',
        value_range='[2013, 2023]',
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
        source_stage='Stage 45/46 (panel/encode compute_fintech_attention_index)',
        reference='Da et al. (2011, JF); Fang & Peress (2009, JF)',
        notes='媒体覆盖率范式 (coverage ratio) 的年度基准; 无距离衰减 (距离衰减仅用于 '
              'ft_attn_prov / ft_attn_city 地理变体)。实测值域 ≈ [0.23, 0.30]',
        category='注意力指数',
        track='',
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
        notes='使用GPT-5-nano、Gemini-3、Grok-4.1三个模型的多数投票结果',
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
        notes='上下文轨道可以减少噪音，提高情感识别的精确度',
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
        source_stage='Stage 46',
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

    # ═══ v3.2.0 Stage 3 双轨标签篇章级 (plan v14 §2.1, BREAKING) ═══
    for _suffix, _track_zh, _track_en, _ref in [
        ('_full', '全文', 'Full-text', 'Gomber 2018 JMIS'),
        ('_ctx', '上下文', 'Entity-context', 'Hassan 2019 QJE entity-proximity'),
    ]:
        metadata[f'innovation_locus{_suffix}'] = VariableMetadata(
            var_name=f'innovation_locus{_suffix}',
            label=f'Innovation Locus ({_track_en}, {_ref})',
            description=f'金融科技创新位点 ({_track_zh}判定): 0=底层技术 / 1=应用场景',
            data_type='Int8 (encoded byte) or str',
            unit='类别',
            value_range='0 (底层技术) | 1 (应用场景) | NaN',
            formula=f'majority_vote_3LLMs(innovation_locus | {_track_en} prompt) + canonicalize_topic crossvalidation',
            source_stage='Stage 21',
            reference=f'Gomber et al. (2018, JMIS); Adner & Kapoor (2010, SMJ); {_ref}',
            notes=f'v3.2.0 BREAKING: 替代 v3.1.x bare innovation_locus. {_track_zh}轨独立判定.',
            category='创新属性-locus',
            track=_track_zh,
        )
        metadata[f'innovation_substantiveness{_suffix}'] = VariableMetadata(
            var_name=f'innovation_substantiveness{_suffix}',
            label=f'Innov. Substantiveness ({_track_en}, W&Z 1998 ASQ)',
            description=f'金融科技创新实质性 ({_track_zh}判定): 0=实质性 / 1=象征性 (洗稿率框架)',
            data_type='Int8 (encoded byte) or str',
            unit='类别',
            value_range='0 (实质性) | 1 (象征性) | NaN',
            formula=f'majority_vote_3LLMs(innovation_substantiveness | {_track_en} prompt)',
            source_stage='Stage 21',
            reference=f'Westphal & Zajac (1994, 1998, ASQ); Fiss & Zajac (2006, ASQ); Bingler et al. (2022, FRL)',
            notes=f'v3.2.0 BREAKING: 替代 v3.1.x bare innovation_substantiveness. {_track_zh}轨独立判定.',
            category='创新属性-substantiveness',
            track=_track_zh,
        )
        # v3.4.0 BREAKING: 第三维度 innovation_collab_mode (Chesbrough 2003 + L&S 2006 SMJ;
        # additive supplementation per Nosek 2018 PNAS, v7 双维语义不变)
        metadata[f'innovation_collab_mode{_suffix}'] = VariableMetadata(
            var_name=f'innovation_collab_mode{_suffix}',
            label=f'Innov. Collab Mode ({_track_en}, Chesbrough 2003)',
            description=(f'金融科技创新协作模式 ({_track_zh}判定): '
                         '0=自主研发 (closed innovation) / 1=外部协同 (open innovation)'),
            data_type='Int8 (encoded byte) or str',
            unit='类别',
            value_range='0 (自主研发) | 1 (外部协同) | NaN',
            formula=f'majority_vote_3LLMs(innovation_collab_mode | {_track_en} prompt)',
            source_stage='Stage 21',
            reference=('Chesbrough (2003) Open Innovation; '
                       'Laursen & Salter (2006, SMJ 27:131-150); '
                       'Hagedoorn (2002, Research Policy)'),
            notes=(f'v3.4.0 BREAKING: 第三维度对称扩张. {_track_zh}轨独立判定. '
                   'tie→"自主研发" (MAP under uniform prior).'),
            category='创新属性-collab_mode',
            track=_track_zh,
        )
        metadata[f'innovation_collab_mode_confidence{_suffix}'] = VariableMetadata(
            var_name=f'innovation_collab_mode_confidence{_suffix}',
            label=f'Collab Mode Confidence ({_track_en}, raw LLM)',
            description=f'innovation_collab_mode{_suffix} 原始 LLM 置信度 (跨模型 row-level 平均)',
            data_type='float',
            unit='概率',
            value_range='[0, 1]',
            formula=f'mean(per_model innovation_collab_mode_confidence | {_track_en} prompt) over verifying models',
            source_stage='Stage 21',
            reference='Törnberg (2024) LLM verbalized confidence',
            notes='v3.4.0: pure LLM confidence (no keyword fallback, mirrors substantiveness pattern)',
            category='置信度-collab_mode',
            track=_track_zh,
        )
        metadata[f'category_confidence{_suffix}'] = VariableMetadata(
            var_name=f'category_confidence{_suffix}',
            label=f'Locus Confidence ({_track_en}, LLM+kw hybrid)',
            description=f'innovation_locus{_suffix} 置信度 (LLM × keyword crossvalidation, +0.2 boost / ×0.5 penalty)',
            data_type='float',
            unit='概率',
            value_range='[0, 1]',
            formula='LLM_majority_conf ± boost/penalty by canonicalize_topic agreement',
            source_stage='Stage 21',
            reference='Gilardi et al. (2023, PNAS) LLM-vs-rule crossvalidation',
            notes='hybrid confidence; raw LLM confidence 在 innovation_locus_confidence_{full,ctx} 列',
            category='置信度-locus',
            track=_track_zh,
        )
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
            notes=f'plan v1.37 P2; positive_class=象征性 aligns with stata_export 1=对照 encoding',
            category='prob_score-substantiveness',
            track=_track_zh,
        )
        metadata[f'avg_subst_prob_score_std{_suffix}'] = VariableMetadata(
            var_name=f'avg_subst_prob_score_std{_suffix}',
            label=f'Std Subst P_BIN ({_track_en}, bank-year SD)',
            description=f'avg_subst_prob_score{_suffix} 的 bank-year 标准差',
            data_type='float',
            unit='概率SD',
            value_range='[0, 0.5]',
            formula=f'std(avg_subst_prob_score{_suffix}) over articles per (target_bank, year)',
            source_stage='Stage 45 panel aggregation',
            reference='Plan v1.37 P2 §5.3.2',
            notes='zero-article bank-year → NaN per encode.py L1105 convention',
            category='prob_score-substantiveness',
            track=_track_zh,
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
            notes=f'plan v1.37 P2; positive_class=应用场景 aligns with stata_export 1=对照 encoding',
            category='prob_score-locus',
            track=_track_zh,
        )
        metadata[f'avg_locus_prob_score_std{_suffix}'] = VariableMetadata(
            var_name=f'avg_locus_prob_score_std{_suffix}',
            label=f'Std Locus P_BIN ({_track_en}, bank-year SD)',
            description=f'avg_locus_prob_score{_suffix} 的 bank-year 标准差',
            data_type='float',
            unit='概率SD',
            value_range='[0, 0.5]',
            formula=f'std(avg_locus_prob_score{_suffix}) over articles per (target_bank, year)',
            source_stage='Stage 45 panel aggregation',
            reference='Plan v1.37 P2 §5.3.2',
            notes='zero-article bank-year → NaN per encode.py L1105 convention',
            category='prob_score-locus',
            track=_track_zh,
        )

    # ═══ v3.2.0 Dual gate 三互斥指示列 (plan v14 §3.1 Action #6) ═══
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
            source_stage='Stage 21',
            reference='Hassan et al. (2019, QJE) entity-proximity independence',
            notes='plan v14 §3.1 P1 R1-A: 改并集 verified_full | verified_ctx 修复',
            category='Stage 1 gate',
            track='dual',
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

    # ═══ v3.5.1 A3 Numerical Intensity (真双轨, Hales 2011 CAR Eq.1) ═══
    metadata['mean_num_intensity_full'] = VariableMetadata(
        var_name='mean_num_intensity_full',
        label='Mean Numerical Intensity Full (Hales 2011 CAR, dual-track)',
        description='Bank-year 加权平均量化披露强度; 基于 content_full + cn2arab + 正则独立扫描',
        data_type='float',
        unit='digits per sentence',
        value_range='[0, +∞) ∪ NaN',
        formula='Σ w_i × (n_digits_full_i / n_sentences_full_i) / Σ w_i; n_sentences lookahead/behind 排除小数点',
        source_stage='Stage 22 (tone_words post-processor enrich_with_num_intensity_dual_track) + Stage 45',
        reference='Hales, Kuang & Venkataraman (2011) CAR 28(1); Davis & Tama-Sweet (2012) CAR 29(3)',
        notes='v3.5.1 A3 真双轨; cn2arab 5 标准样例 frozen at D0; 不定数 (几千/数十亿) 不计为 token (修 R7-M2); 中文 sentence 分母与英文 Hales 2011 不直接可比 (paper §3.4 disclosure 修 R7-M1)',
        category='Numerical Intensity (v3.5.1 A3)',
        track='full',
    )

    metadata['mean_num_intensity_ctx'] = VariableMetadata(
        var_name='mean_num_intensity_ctx',
        label='Mean Numerical Intensity Ctx (Hales 2011 CAR, dual-track)',
        description='Bank-year 加权平均 num_intensity; ctx 轨独立扫描',
        data_type='float',
        unit='digits per sentence',
        value_range='[0, +∞) ∪ NaN',
        formula='Σ w_i × (n_digits_ctx_i / n_sentences_ctx_i) / Σ w_i',
        source_stage='Stage 22 + Stage 45',
        reference='Hales, Kuang & Venkataraman (2011) CAR 28(1)',
        notes='ctx 残半句已被 entity_context 完整句号过滤 (修 R3-H3)',
        category='Numerical Intensity (v3.5.1 A3)',
        track='ctx',
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


def generate_codebook(
    panel: pd.DataFrame,
    output_dir: str,
    formats: List[str] | None = None,
) -> Dict[str, str]:
    """生成完整的变量代码手册

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
        excel_path = os.path.join(output_dir, 'variable_codebook.xlsx')
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            codebook_df.to_excel(writer, sheet_name='Codebook', index=False)
            # 调整列宽
            worksheet = writer.sheets['Codebook']
            for idx, col in enumerate(codebook_df.columns, 1):
                max_length = max(
                    codebook_df[col].astype(str).map(len).max(),
                    len(col)
                )
                worksheet.column_dimensions[chr(64 + idx)].width = min(max_length + 2, 50)
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
    """自动推断来源阶段"""
    if 'llm' in var_name or 'gpt' in var_name or 'gemini' in var_name:
        return 'Stage 21'
    elif 'bert' in var_name:
        return 'Stage 23'
    elif 'dict' in var_name or 'jiang' in var_name or 'yao' in var_name:
        return 'Stage 22'
    elif 'attn' in var_name:
        return 'Stage 24'
    elif 'network' in var_name or 'cent' in var_name:
        return 'Stage 46'
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

