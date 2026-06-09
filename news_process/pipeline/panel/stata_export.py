"""news_process.pipeline.panel.stata_export — Stage 46 Stata 数据导出层 (v3.2.0)

功能 (plan v14 §9.1):
    把 stage 45 panel parquet (40_panel_yearly.parquet) 转换为 Stata .dta + labels.

输出三文件 (与 plan v14 §9.1 一致):
    46_panel_yearly_core.dta    # Stata IC 兼容 (≤ 2048 vars)
    46_panel_yearly_full.dta    # 全列 (Stata SE/MP)
    46_panel_yearly_aux.dta     # robustness 子集 (core 互补; merge 1:1 可还原 full)
    46_panel_yearly_labels.do   # variable/value labels Stata 脚本
    46_panel_yearly_codebook.xlsx  # 人类可读变量字典

关键转换 (plan v14 §9.1; v3.4.0 +collab_mode):
    - innovation_locus_{full,ctx} (中文 str) → byte 0=底层技术, 1=应用场景 + value label
    - innovation_substantiveness_{full,ctx} (中文 str) → byte 0=实质性, 1=象征性 + value label
    - innovation_collab_mode_{full,ctx} (中文 str) → byte 0=自主研发, 1=外部协同 + value label  [v3.4.0]
    - NaN → . / .a / .b (extended missing for distinguishable causes)
    - 列名 ≤ 32 字符 (Stata 硬限)
    - variable label ≤ 80 字符 (Stata 硬限)

锚定文献:
    Westphal & Zajac (1994, 1998, ASQ) substantive-symbolic
    Gomber, Kauffman, Parker, Weber (2018, JMIS) enabling tech vs business function
    Chesbrough (2003) Open Innovation; Laursen & Salter (2006, SMJ) [v3.4.0 第三维度]
    Hassan, Hollander, van Lent, Tahoun (2019, QJE) entity-proximity attribution
"""
from __future__ import annotations

import logging
import os
from typing import Dict, List, Tuple

import pandas as pd

logger = logging.getLogger(__name__)

# Stata 硬限 (plan v14 §9.5 / R32-D, R42-A 修复)
STATA_VAR_NAME_MAXLEN = 32      # 变量名最长 32 字符
STATA_VAR_LABEL_MAXLEN = 80     # 变量标签最长 80 字符
STATA_IC_MAX_VARS = 2048        # Stata IC license 最大列数

# v3.2.0 类别 → byte encoding 映射 (plan v14 §9.1 + R32-B 编码方向论证)
# 关键: 0=baseline, 1=对照 (洗稿率框架天然解释方向)
LOCUS_ENCODING: Dict[str, int] = {
    '底层技术': 0,
    '应用场景': 1,
}

SUBSTANTIVENESS_ENCODING: Dict[str, int] = {
    '实质性': 0,
    '象征性': 1,
}

# v3.4.0: 第三维度 collab_mode (Chesbrough 2003 + L&S 2006 SMJ; positive_class=外部协同)
# 关键: 0=自主研发 (closed innovation / baseline), 1=外部协同 (open innovation / 对照)
# 与 substantiveness/locus 同模式: 0=baseline, 1=对照 (paper 主回归 treatment 焦点)
COLLAB_MODE_ENCODING: Dict[str, int] = {
    '自主研发': 0,
    '外部协同': 1,
}

# v3.5.0 D2: cell_id 1..8 value label (per stage3_v3_5_0_augmentation_plan.md §2.1.3)
# cell_id = subst*4 + locus*2 + collab + 1
# cell 1 = (0, 0, 0) = 实质性·底层技术·自主研发 (三维全 baseline)
# cell 8 = (1, 1, 1) = 象征性·应用场景·外部协同 (三维全 contrast)
# ASCII-only labels for Stata value label compat (32K bytes 软上限).
CELL_ID_VALUE_LABEL: Dict[int, str] = {
    1: 'sub.tech.indep',  2: 'sub.tech.collab',
    3: 'sub.app.indep',   4: 'sub.app.collab',
    5: 'symb.tech.indep', 6: 'symb.tech.collab',
    7: 'symb.app.indep',  8: 'symb.app.collab',
}

# v3.5.0 D4: d4_data_quality_flag str column value mapping (per plan §2.3.4 F6).
# Persisted via str column (not byte encoding) for Stata user visibility.
# Stata 端典型用法: `keep if d4_data_quality_flag == "ok"` 过滤不可信 ctx coverage.
D4_DATA_QUALITY_FLAG_VALUES = ('ok', 'insufficient')

# Value labels (双语 zh + EN, plan v14 §9.1 普通人版变更 20)
LOCUS_VALUE_LABELS: Dict[int, str] = {
    0: "底层技术 (Technology)",
    1: "应用场景 (Application)",
}

SUBSTANTIVENESS_VALUE_LABELS: Dict[int, str] = {
    0: "实质性 (Substantive)",
    1: "象征性 (Symbolic)",
}

COLLAB_MODE_VALUE_LABELS: Dict[int, str] = {
    0: "自主研发 (Independent R&D / Closed Innovation)",
    1: "外部协同 (External Collaboration / Open Innovation)",
}


def encode_categorical_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Dict[int, str]]]:
    """把 stage 3 字符串列编码为 byte 0/1 + 收集 value labels.

    Args:
        df: panel DataFrame 含 innovation_locus_{full,ctx} 与
            innovation_substantiveness_{full,ctx} 字符串列.
    Returns:
        (encoded_df, value_labels_dict): {var_name: {int_code: label_str}}
    """
    df = df.copy()
    value_labels: Dict[str, Dict[int, str]] = {}

    for col in ['innovation_locus_full', 'innovation_locus_ctx']:
        if col in df.columns:
            df[col] = df[col].map(LOCUS_ENCODING).astype('Int8')
            value_labels[col] = LOCUS_VALUE_LABELS

    for col in ['innovation_substantiveness_full', 'innovation_substantiveness_ctx']:
        if col in df.columns:
            df[col] = df[col].map(SUBSTANTIVENESS_ENCODING).astype('Int8')
            value_labels[col] = SUBSTANTIVENESS_VALUE_LABELS

    # v3.4.0: 第三维度 collab_mode encoding (Chesbrough 2003)
    for col in ['innovation_collab_mode_full', 'innovation_collab_mode_ctx']:
        if col in df.columns:
            df[col] = df[col].map(COLLAB_MODE_ENCODING).astype('Int8')
            value_labels[col] = COLLAB_MODE_VALUE_LABELS

    return df, value_labels


def build_variable_labels(df: pd.DataFrame) -> Dict[str, str]:
    """为每列生成 ≤ 80 字符英文 variable label.

    优先级:
        1. codebook.py::get_variable_metadata_dict()[col].label (若存在)
        2. heuristic 基于列名命名规则 (locus_full → "..." 等)
        3. fallback: 列名本身

    所有 label 强制截断至 80 字符 (R32-H + R40-A fallback策略).
    """
    labels: Dict[str, str] = {}
    try:
        from news_process.pipeline.panel.codebook import get_variable_metadata_dict
        meta = get_variable_metadata_dict()
    except Exception as e:
        logger.warning(f"codebook metadata 不可用 ({e}), 使用启发式标签")
        meta = {}

    # 启发式映射 (覆盖 v3.2.0 新增双轨列, codebook 未及时同步时的 fallback)
    HEURISTIC_LABELS: Dict[str, str] = {
        'n_articles_llm_valid':             "News count, LLM-valid (category-frac denominator)",
        'n_articles_llm_valid_ctx':         "News count, ctx-track LLM-valid (ctx category-frac denom)",
        'innovation_locus_full':            "Innovation Locus (Full-text, Gomber 2018 JMIS)",
        'innovation_locus_ctx':             "Innovation Locus (Entity-context, Hassan 2019 QJE)",
        'innovation_substantiveness_full':  "Innov. Substantiveness (Full-text, W&Z 1998 ASQ)",
        'innovation_substantiveness_ctx':   "Innov. Substantiveness (Entity-ctx, Hassan 2019 QJE)",
        'innovation_collab_mode_full':      "Innov. Collab Mode (Full-text, Chesbrough 2003)",
        'innovation_collab_mode_ctx':       "Innov. Collab Mode (Entity-ctx, Hassan 2019 QJE)",
        'innovation_collab_mode_confidence_full': "Collab Mode Confidence (Full-text, raw LLM)",
        'innovation_collab_mode_confidence_ctx':  "Collab Mode Confidence (Entity-ctx, raw LLM)",
        'category_confidence_full':         "Locus Confidence (Full-text, hybrid LLM+keyword)",
        'category_confidence_ctx':          "Locus Confidence (Entity-ctx, hybrid LLM+keyword)",
        'llm_verified_dual_full_only':      "Dual Gate: Full-track only verified",
        'llm_verified_dual_ctx_only':       "Dual Gate: Ctx-track only verified",
        'llm_verified_dual_both':           "Dual Gate: Both tracks verified",
        'tone_gap_tech_app_lc_ctx':         "Tone Gap: Tech-App (Loc=Ctx, ctx sentiment)",
        'tone_gap_sub_symb_sc_ctx':         "Tone Gap: Sub-Symb (Subst=Ctx, ctx sentiment)",
        'tech_frac_lc':                     "Frac of Tech-locus articles (ctx classification)",
        'app_frac_lc':                      "Frac of App-locus articles (ctx classification)",
        'sub_frac_sc':                      "Frac of Substantive articles (ctx classification)",
        'symb_frac_sc':                     "Frac of Symbolic articles (ctx classification)",
        # Plan v1.37 P2 §5.3.4: 8 binary prob_score columns (≤ 80 UTF-8 bytes;
        # em-dash 3 bytes; positive_class = 象征性 / 应用场景 per stata_export
        # encoding 1=对照).
        'avg_subst_prob_score_full':        "Avg Subst P_BIN (full-track) — 1=symbolic, max-ent map",
        'avg_subst_prob_score_std_full':    "Std Subst P_BIN (full-track, bank-year SD)",
        'avg_subst_prob_score_ctx':         "Avg Subst P_BIN (ctx-track) — 1=symbolic, max-ent map",
        'avg_subst_prob_score_std_ctx':     "Std Subst P_BIN (ctx-track, bank-year SD)",
        'avg_locus_prob_score_full':        "Avg Locus P_BIN (full-track) — 1=application, max-ent map",
        'avg_locus_prob_score_std_full':    "Std Locus P_BIN (full-track, bank-year SD)",
        'avg_locus_prob_score_ctx':         "Avg Locus P_BIN (ctx-track) — 1=application, max-ent map",
        'avg_locus_prob_score_std_ctx':     "Std Locus P_BIN (ctx-track, bank-year SD)",
        # v3.5.1 A1 Lexical Clarity (LM 2011 JF 66:1; You 2018 hhx055 Panel C/D)
        # 真双轨独立扫描; 每条 ≤ 80 UTF-8 bytes (per plan v0.3 §2.4.1 frozen at D0).
        'mean_clarity_score_full':          "Mean Clarity Score from indep Full-text scan (LM 2011 JF; You 2018)",
        'mean_clarity_score_ctx':           "Mean Clarity Score from indep Ctx-text scan (LM 2011 JF; You 2018)",
        'mean_frac_definite_full':          "Mean Frac Definite from indep Full scan (You 2018 Panel C 388 words)",
        'mean_frac_definite_ctx':           "Mean Frac Definite from indep Ctx scan (You 2018 Panel C 388 words)",
        'frac_amb_articles_full':           "Frac Articles Ambiguous Full (>=D0 median, You 2018 Panel D)",
        'frac_amb_articles_ctx':            "Frac Articles Ambiguous Ctx (>=D0 median, You 2018 Panel D)",
        # v3.5.1 A3 Numerical Intensity (数值披露强度; 引文勘误见 codebook reference) 真双轨
        'mean_num_intensity_full':          "Mean Numerical Intensity Full (dual-track)",
        'mean_num_intensity_ctx':           "Mean Numerical Intensity Ctx (dual-track)",
        # remove-title-track: title-indicator labels 已移除
        # ─────────────────────────────────────────────────────────────
        # 2026-05-29 双模型嵌入: text2vec 稳健 twin (主轨=text-embedding-3-small,
        # 这些 _t2v 列=shibing624/text2vec-base-chinese 同算法只换模型)。落 aux。
        # ─────────────────────────────────────────────────────────────
        'strat_diff_t2v_full':              "Strat Diff (T2V robust=text2vec, full)",
        'strat_diff_t2v_ctx':               "Strat Diff (T2V robust=text2vec, ctx)",
        'strat_diff_n5_emb_t2v':            "Strat Diff N5 Emb (T2V robust, full)",
        'strat_diff_n5_emb_t2v_ctx':        "Strat Diff N5 Emb (T2V robust, ctx)",
        'strat_sim_max_emb_t2v':            "Strat Max Sim Emb (T2V robust, full)",
        'strat_sim_max_emb_t2v_ctx':        "Strat Max Sim Emb (T2V robust, ctx)",
        'centroid_diff_emb_t2v':            "Centroid Diff Emb (T2V robust, full)",
        'centroid_diff_emb_t2v_ctx':        "Centroid Diff Emb (T2V robust, ctx)",
        'coh_emb_t2v_full':                 "Temporal Coherence Emb (T2V robust, full)",
        'coh_emb_t2v_ctx':                  "Temporal Coherence Emb (T2V robust, ctx)",
        'policy_cosine_sim_t2v_full':       "Policy Cosine Sim (T2V robust, full)",
        'policy_cosine_sim_t2v_ctx':        "Policy Cosine Sim (T2V robust, ctx)",
        'auth_sim_emb_t2v_full':            "Auth Policy Sim Emb (T2V robust, full)",
        'auth_sim_emb_t2v_ctx':             "Auth Policy Sim Emb (T2V robust, ctx)",
        'benefit_mean_t2v_full':            "Benefit Attitude Mean (T2V robust, full)",
        'benefit_mean_t2v_ctx':             "Benefit Attitude Mean (T2V robust, ctx)",
        'benefit_std_t2v_full':             "Benefit Attitude SD (T2V robust, full)",
        'benefit_std_t2v_ctx':              "Benefit Attitude SD (T2V robust, ctx)",
        'benefit_pos_frac_t2v_full':        "Benefit Pos Frac (T2V robust, full)",
        'benefit_pos_frac_t2v_ctx':         "Benefit Pos Frac (T2V robust, ctx)",
        'benefit_neg_frac_t2v_full':        "Benefit Neg Frac (T2V robust, full)",
        'benefit_neg_frac_t2v_ctx':         "Benefit Neg Frac (T2V robust, ctx)",
        'emb_peer_tone_lag1_t2v_full':      "Emb Peer Tone Lag1 (T2V robust, full)",
        'bank_emb_sim_mean_t2v':            "Bank Emb Sim Mean (T2V robust)",
    }

    for col in df.columns:
        # 优先 codebook
        if col in meta and hasattr(meta[col], 'label') and meta[col].label:
            label = meta[col].label
        elif col in HEURISTIC_LABELS:
            label = HEURISTIC_LABELS[col]
        else:
            # fallback: 列名 (注意中文 column 名直接用)
            label = col

        # 截断至 80 字符 (R40-A fallback)
        if len(label.encode('utf-8')) > STATA_VAR_LABEL_MAXLEN:
            label = label[:STATA_VAR_LABEL_MAXLEN - 3] + '...'

        labels[col] = label
    return labels


def assign_core_columns(df: pd.DataFrame) -> List[str]:
    """按 plan v14 §9.1 (R42-A + R44-A): 划分 core 列 (≤ 2048, Stata IC 兼容).

    Core 列规则:
        - 主键 (target_bank, year)
        - sentiment 双轨主指标 (llm_sentiment_*, llm_vote_*, llm_prob_score_*)
        - stage 3 双轨标签 + confidence (innovation_*_{full,ctx})
        - dual gate 三互斥指示
        - 主子集 mean 列 (_lf × _full 隐式 + _lc × _ctx 显式对角线)
        - 主洗稿率 count
        - 主 Bartik IV (full/ctx)
        - 基础统计 (n_articles, frac, ln_news_coverage)

    Aux 列:
        - 4-way 洗稿率非主组合 (sentiment × subst 笛卡尔积非对角)
        - inter-track κ
        - 历史保留列
    """
    core_patterns = [
        # 主键
        'target_bank', 'year',
        # 基础统计 + bank 属性
        'n_articles', 'n_articles_llm_valid', 'n_articles_llm_valid_ctx', 'media_breadth', 'ln_news_coverage', 'bank_type',
        'bank_size', 'bank_age', 'bank_province', 'bank_zone',
        'digital_frontier',
        # sentiment 双轨主指标
        'llm_sentiment_full', 'llm_sentiment_ctx',
        'llm_vote_tone_full', 'llm_vote_tone_ctx',
        'llm_prob_score_full', 'llm_prob_score_ctx',
        'avg_llm_prob_score_full', 'avg_llm_prob_score_ctx',
        # stage 3 双轨标签 + confidence (v3.4.0: 加 collab_mode 第三维度)
        'innovation_locus_full', 'innovation_locus_ctx',
        'innovation_substantiveness_full', 'innovation_substantiveness_ctx',
        'innovation_collab_mode_full', 'innovation_collab_mode_ctx',
        'innovation_collab_mode_confidence_full', 'innovation_collab_mode_confidence_ctx',
        'category_confidence_full', 'category_confidence_ctx',
        'avg_il_confidence_full', 'avg_il_confidence_ctx',
        'avg_iss_confidence_full', 'avg_iss_confidence_ctx',
        'avg_icm_confidence_full', 'avg_icm_confidence_ctx',
        # dual gate
        'llm_verified_dual_full_only', 'llm_verified_dual_ctx_only', 'llm_verified_dual_both',
        # 主子集对角线 (_lf × _full 隐式 + _lc × _ctx 显式)
        'tech_frac', 'app_frac', 'sub_frac', 'symb_frac',
        'tech_frac_lc', 'app_frac_lc', 'sub_frac_sc', 'symb_frac_sc',
        'n_articles_tech', 'n_articles_app', 'n_articles_sub', 'n_articles_symb',
        'n_articles_tech_lc_ctx', 'n_articles_app_lc_ctx',
        'n_articles_sub_sc_ctx', 'n_articles_symb_sc_ctx',
        'llm_vote_tone_tech_full', 'llm_vote_tone_app_full',
        'llm_vote_tone_tech_lc_ctx', 'llm_vote_tone_app_lc_ctx',
        'llm_vote_tone_sub_full', 'llm_vote_tone_symb_full',
        'llm_vote_tone_sub_sc_ctx', 'llm_vote_tone_symb_sc_ctx',
        # tone gap
        'tone_gap_tech_app', 'tone_gap_tech_app_lc_ctx',
        'tone_gap_sub_symb', 'tone_gap_sub_symb_sc_ctx',
        # 主 Bartik IV (full/ctx 2 列; _title 列已随标题情感轨删除)
        'bartik_fintech_iv_full', 'bartik_fintech_iv_ctx',  # remove-title-track
        # 主洗稿率 count (sentiment × _full)
        'pos_symb_count_full', 'pos_symb_count_ctx',
        'neg_sub_count_full', 'neg_sub_count_ctx',
        # Plan v1.37 P2 §5.3.4: 8 binary prob_score columns (core; not aux).
        'avg_subst_prob_score_full', 'avg_subst_prob_score_ctx',
        'avg_subst_prob_score_std_full', 'avg_subst_prob_score_std_ctx',
        'avg_locus_prob_score_full', 'avg_locus_prob_score_ctx',
        'avg_locus_prob_score_std_full', 'avg_locus_prob_score_std_ctx',
        # v3.5.1 A1 Lexical Clarity (LM 2011 JF; You 2018) — 6 列全进 core
        # (per plan v0.3 §1.3 invariant + §2.4.1; core 当前 ~95+8=103 远低于 IC 2048).
        'mean_clarity_score_full', 'mean_clarity_score_ctx',
        'mean_frac_definite_full', 'mean_frac_definite_ctx',
        'frac_amb_articles_full', 'frac_amb_articles_ctx',
        # v3.5.1 A3 Numerical Intensity (数值披露强度) — 2 列全进 core
        'mean_num_intensity_full', 'mean_num_intensity_ctx',
        # v3.7.2 R8-H1 全管道延伸: ctx 独立度信号 (entity-miss → ctx ≡ full → 双轨退化)
        # ⚠ 与 intensity_verified_{full,ctx} 不同义:
        #    - frac_ctx_fallback: 上游 entity_context 提取失败 (Hassan 2019 QJE proximity)
        #    - intensity_verified_*: stage 14 fintech 关键词 IDF 验证失败
        # n_articles_for_ctx_independence: 绝对独立文章数, 避免按比例 filter 时的银行规模偏差
        # 论文用途: P1 (llm_vote_tone_ctx) / P11 (mean_clarity_score_ctx) measurement-error robustness
        'frac_ctx_fallback', 'n_articles_for_ctx_independence',
        # v3.7.4 P3.1.6: title indicators for Panel D/E stratified robustness
        # Anchor: Antweiler-Frank (2004) JF subject-relevance threshold;
        #          Da-Engelberg-Gao (2011) JF attention-channel separation.
        # ─────────────────────────────────────────────────────────────
        # v3.5.2 PR #14 集成 — A1 LM 4 子词典 + A2 FLS (本批列在 v3.5.2
        # PR #3 panel 集成完成前会被 ``if c in df.columns`` 过滤; append-only
        # 不破坏 v3.6.0 已 frozen 契约).
        # ─────────────────────────────────────────────────────────────
        # A1 LM 2011 JF non-sentiment 4 子词典 (8 列双轨)
        'uncert_frac_full', 'uncert_frac_ctx',
        'litig_frac_full', 'litig_frac_ctx',
        'constr_frac_full', 'constr_frac_ctx',
        'modal_strong_frac_full', 'modal_strong_frac_ctx',
        # A2 Forward-Looking Statements (Li 2010 JAR) — 2 列双轨
        'frac_fls_full', 'frac_fls_ctx',
        # ─────────────────────────────────────────────────────────────
        # v3.6.1 PR #14 集成 — C1 媒体 3 级 tier
        # ─────────────────────────────────────────────────────────────
        # C1 媒体 tier 加权 (sensitivity, 不替换原 media_authority_weight)
        'media_authority_weight_tier', 'media_tier_label',
        # ─────────────────────────────────────────────────────────────
        # v3.7.0 PR #14 集成 — D 组 (staleness / α)
        # ─────────────────────────────────────────────────────────────
        # D2 staleness 双指标
        'surface_staleness_full', 'surface_staleness_ctx',
        'semantic_staleness_full', 'semantic_staleness_ctx',
        # D3 Krippendorff α (与第 10 篇 bank_media_disagreement 对齐)
        'cross_outlet_tone_variance_full', 'cross_outlet_tone_variance_ctx',
        'cross_media_alpha_full', 'cross_media_alpha_ctx',
    ]

    core = [c for c in core_patterns if c in df.columns]

    if len(core) > STATA_IC_MAX_VARS:
        raise ValueError(
            f"Core column count {len(core)} exceeds Stata IC max {STATA_IC_MAX_VARS}. "
            f"plan v14 §9.5 R42-A 验收门违反, 需要拆 core/aux 再分配."
        )

    logger.info(f"  Core 列数: {len(core)} / {len(df.columns)} (IC 余量 {STATA_IC_MAX_VARS - len(core)})")
    return core


def shorten_long_column_names(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """v3.2.0 M3/7: 自动缩短超 32 字符列名 (Stata 硬限).

    缩写规则:
        1. 常见模式替换 (idf_score → idfsc, leave1out → l1o, 等)
        2. 若仍 > 32, 截断到 32 字符
        3. 截断后冲突 → 后缀 _1, _2, ...
        4. 返回 (df_renamed, mapping) 让 codebook 记录原名

    Returns:
        (renamed_df, {short_name: original_name}) — codebook 可反查
    """
    abbreviations = [
        ('_idf_score_', '_idfsc_'),
        ('_leave1out_', '_l1o_'),
        ('_dict_avg_tone_', '_davg_t_'),
        ('_bert_avg_pos_', '_bavg_p_'),
    ]
    rename_map: Dict[str, str] = {}  # short → original
    new_cols: List[str] = []
    used: set = set()
    # P-063 修复 (v3.7.1): 旧 dedup 用 _1/_2 numeric suffix 截断 base
    # (`base[:MAX-2] + '_1'`), 把 32-char 区间内的关键 suffix (_full/_ctx/
    # _t0/_t1) 吃掉, 破坏 track 语义. 改用 6-char md5 hash suffix 保留尽量
    # 多的 discriminating chars + 跨 run 确定性 (同 col 总产同 hash).
    import hashlib as _hashlib  # 局部 import 避免 module-level 污染
    for col in df.columns:
        new_col = col
        if len(new_col) > STATA_VAR_NAME_MAXLEN:
            for old, new in abbreviations:
                if old in new_col:
                    new_col = new_col.replace(old, new)
                    if len(new_col) <= STATA_VAR_NAME_MAXLEN:
                        break
        # 仍超 → 截断
        if len(new_col) > STATA_VAR_NAME_MAXLEN:
            new_col = new_col[:STATA_VAR_NAME_MAXLEN]
        # 冲突处理: 用 md5 hash suffix 保 discriminating chars
        if new_col in used:
            base = new_col[:STATA_VAR_NAME_MAXLEN - 7]
            h = _hashlib.md5(col.encode('utf-8')).hexdigest()[:6]
            new_col = f"{base}_{h}"
        used.add(new_col)
        new_cols.append(new_col)
        if new_col != col:
            rename_map[new_col] = col

    df_renamed = df.copy()
    df_renamed.columns = new_cols
    return df_renamed, rename_map


# 中文情感标签 → ASCII 确定性映射 (与既有 fin_sent_zh_pos/neg 命名约定一致)
_CN_LABEL_ASCII = {
    '正面': 'pos', '负面': 'neg', '中性': 'neu',
    '积极': 'pos', '消极': 'neg', '中立': 'neu',
}


def asciify_non_ascii_columns(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """H3 (audit-fixes 2026-05-29): 把含非 ASCII 字符的列名转写为合法 Stata 变量名.

    Stata 变量名即使在 Unicode 版 (14+/19) 也必须匹配
    ``^[A-Za-z_][A-Za-z0-9_]{0,31}$`` (Unicode 仅允许出现在值/标签, 不允许在
    变量名)。此前 ``shorten_long_column_names`` 仅按长度截断、不处理非 ASCII,
    导致 117 个中文后缀列 (如 ``finbert_cn_正面_w_sum_full``) 以非法名写入
    full/aux .dta, 且 labels.do 的 ``capture label var <中文>`` 静默 no-op 丢标签.

    sentiment-label 段 (正面/负面/中性) 用确定性映射 → pos/neg/neu (不丢信息,
    与既有 ASCII 变体 fin_sent_zh_pos/neg 一致); 残留非 ASCII 字符移除;
    清理重复下划线 + 保证合法首字符 + 截断 32 + md5 后缀去重 (跨 run 确定性).

    Returns:
        (df_renamed, {new_name: original_name}) — 供 codebook 反查.
    """
    import hashlib as _hashlib
    import re as _re

    mapping: Dict[str, str] = {}
    new_cols: List[str] = []
    used = {c for c in df.columns if c.isascii()}
    for col in df.columns:
        if col.isascii():
            new_cols.append(col)
            continue
        new = col
        for cn, asc in _CN_LABEL_ASCII.items():
            new = new.replace(cn, asc)
        # 残留非 ASCII → 移除
        new = ''.join(ch for ch in new if ord(ch) < 128)
        new = _re.sub(r'_+', '_', new).strip('_')
        if not new or not (new[0].isalpha() or new[0] == '_'):
            new = 'v_' + new
        new = new[:STATA_VAR_NAME_MAXLEN]
        if new in used:
            base = new[:STATA_VAR_NAME_MAXLEN - 7]
            h = _hashlib.md5(col.encode('utf-8')).hexdigest()[:6]
            new = f"{base}_{h}"
        used.add(new)
        new_cols.append(new)
        mapping[new] = col
    df_renamed = df.copy()
    df_renamed.columns = new_cols
    return df_renamed, mapping


def validate_stata_compat(df: pd.DataFrame, var_labels: Dict[str, str]) -> None:
    """plan v14 §9.5 验收门: 列名 ≤ 32 字符 + 合法 Stata 标识符 + label ≤ 80 字符."""
    import re as _re
    _ident_re = _re.compile(r'^[A-Za-z_][A-Za-z0-9_]{0,31}$')
    issues: List[str] = []
    for col in df.columns:
        if len(col) > STATA_VAR_NAME_MAXLEN:
            issues.append(f"列名超 32 字符: '{col}' ({len(col)} chars)")
        elif not _ident_re.match(col):
            # H3 (audit-fixes 2026-05-29): 非 ASCII / 非法字符 / 非字母下划线起始
            # 都是 Stata 拒绝的变量名 — 此前仅查长度, 放过了 117 个中文列名。
            issues.append(f"非法 Stata 变量名 (非 ASCII 或含非法字符): '{col}'")
        if col in var_labels:
            label_bytes = len(var_labels[col].encode('utf-8'))
            if label_bytes > STATA_VAR_LABEL_MAXLEN:
                issues.append(f"label 超 80 字节: '{col}' ({label_bytes} bytes)")
    if issues:
        raise ValueError(
            f"Stata 兼容性校验失败 ({len(issues)} 处):\n  - " +
            "\n  - ".join(issues[:10])
        )


def write_labels_do_file(
    out_path: str,
    var_labels: Dict[str, str],
    value_labels: Dict[str, Dict[int, str]],
) -> None:
    """生成 Stata .do 脚本: variable labels + value labels + apply.

    Args:
        out_path: 输出 .do 路径
        var_labels: {var_name: english_label}
        value_labels: {var_name: {int_code: label_string}}
    """
    lines: List[str] = [
        '* news_process v3.2.0 — Stata variable/value labels (plan v14 §9.1)',
        '* Generated by news_process.pipeline.panel.stata_export.write_labels_do_file',
        '',
        '* Section 1: Variable labels (每列加 ≤ 80 字符英文说明)',
    ]
    for col, label in var_labels.items():
        # Stata `label var` 语法: label var <name> "<label>"
        safe_label = label.replace('"', '""')
        lines.append(f'capture label var {col} "{safe_label}"')

    lines.extend([
        '',
        '* Section 2: Value labels (类别变量 0=baseline / 1=对照, 双语)',
    ])

    # locus_lbl (共享)
    lines.append('capture label drop locus_lbl')
    lines.append('label define locus_lbl 0 "底层技术 (Technology)" 1 "应用场景 (Application)"')

    # subst_lbl (共享)
    lines.append('capture label drop subst_lbl')
    lines.append('label define subst_lbl 0 "实质性 (Substantive)" 1 "象征性 (Symbolic)"')

    # v3.4.0: collab_mode_lbl (Chesbrough 2003 + L&S 2006 SMJ; 第三维度)
    lines.append('capture label drop collab_mode_lbl')
    lines.append('label define collab_mode_lbl 0 "自主研发 (Independent R&D)" 1 "外部协同 (External Collab)"')

    lines.append('')
    lines.append('* Apply value labels to encoded columns')
    # v3.4.0 ordering: collab_mode 必须先于 substantiveness 检测, 避免子串误匹配
    # ('innovation_substantiveness' 与 'innovation_collab_mode' 互不包含, 但保留显式过滤)
    locus_cols = [c for c in value_labels if 'innovation_locus' in c]
    subst_cols = [c for c in value_labels if 'innovation_substantiveness' in c]
    collab_cols = [c for c in value_labels if 'innovation_collab_mode' in c]
    if locus_cols:
        lines.append(f'capture label values {" ".join(locus_cols)} locus_lbl')
    if subst_cols:
        lines.append(f'capture label values {" ".join(subst_cols)} subst_lbl')
    if collab_cols:
        lines.append(f'capture label values {" ".join(collab_cols)} collab_mode_lbl')

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    logger.info(f"  Stata labels .do 已写入: {out_path} ({len(lines)} 行)")


def _write_dta_pyreadstat(df, path, value_labels, var_labels):
    """Backend 1 (推荐): pyreadstat 全功能写入 (value labels + 中文 + extended missing)."""
    import pyreadstat
    pyreadstat.write_dta(
        df, path,
        variable_value_labels=value_labels,
        column_labels=[var_labels.get(c, c) for c in df.columns],
    )


def _write_dta_pandas_fallback(df, path, value_labels, var_labels):
    """Backend 2 (fallback): pandas 原生 .to_stata().

    限制 (相比 pyreadstat):
        - 无 value labels (需用 labels.do 手动 apply)
        - 无 extended missing (.a/.b/.c)
        - 仅 variable label 通过 variable_labels 参数支持
    但不需要额外安装 pyreadstat, 让用户在 minimal install 下也能跑 stage 46.
    """
    # pandas to_stata 接受 dict-form variable_labels
    df.to_stata(
        path,
        write_index=False,
        variable_labels={k: v for k, v in var_labels.items() if k in df.columns},
        version=118,  # Stata 14+ format (与 pyreadstat write_dta 默认对齐)
    )


def _select_dta_backend():
    """探测可用 .dta 写入 backend; 优先 pyreadstat (功能更全)."""
    try:
        import pyreadstat  # noqa: F401
        return 'pyreadstat', _write_dta_pyreadstat
    except ImportError:
        logger.warning(
            "  pyreadstat 未装, fallback 到 pandas to_stata. "
            "限制: value labels 需用 labels.do 手动 apply; extended missing 不支持. "
            "推荐: pip install pyreadstat>=1.2 启用全功能."
        )
        return 'pandas', _write_dta_pandas_fallback


def export_panel_to_stata(
    panel_path: str,
    output_dir: str,
    output_prefix: str = '46_panel_yearly',
) -> Dict[str, str]:
    """主导出函数: 从 panel parquet 产出 .dta + labels.do + codebook.xlsx.

    v3.2.0 M1/7 (此 commit): pyreadstat 改为 OPTIONAL, fallback 到 pandas to_stata.
    解除 plan v14 §9.4 的"硬依赖"约束, 让用户在 minimal install 下也能产 .dta.

    Args:
        panel_path: 输入 40_panel_yearly.parquet 路径
        output_dir: 输出目录 (data/processed/)
        output_prefix: 文件名前缀 (默认 46_panel_yearly)
    Returns:
        dict 含产出文件路径: {'core_dta', 'aux_dta', 'full_dta',
                             'labels_do', 'codebook_xlsx', 'backend'}
    """
    backend_name, write_dta = _select_dta_backend()

    logger.info("=== Stage 46 Stata Export (plan v14 §9.1) ===")
    logger.info(f"  Backend: {backend_name}")
    logger.info(f"  输入: {panel_path}")

    if not os.path.exists(panel_path):
        raise FileNotFoundError(f"panel parquet 不存在: {panel_path}")

    df = pd.read_parquet(panel_path)
    logger.info(f"  panel 载入: {len(df)} 行 × {len(df.columns)} 列")

    # 1. 类别变量编码 (中文 str → byte 0/1)
    df_encoded, value_labels = encode_categorical_columns(df)

    # 1b. v3.2.0 M3/7: 自动缩短超 32 字符列名 (Stata 硬限) + 记录 mapping
    df_encoded, rename_map = shorten_long_column_names(df_encoded)
    if rename_map:
        logger.info(f"  Renamed {len(rename_map)} long columns (>32 chars) to Stata-compatible names")
        for short, orig in list(rename_map.items())[:3]:
            logger.info(f"    {orig} → {short}")
        if len(rename_map) > 3:
            logger.info(f"    ... +{len(rename_map) - 3} more (full mapping in codebook.xlsx)")

    # 1c. H3 (audit-fixes 2026-05-29): 把残留非 ASCII (中文) 列名转写为合法
    # Stata 变量名 (正面/负面/中性 → pos/neg/neu)。此前缺该步, 117 个中文列名
    # 以非法 Stata 标识符写入 full/aux .dta, labels.do 静默丢标签。
    df_encoded, ascii_map = asciify_non_ascii_columns(df_encoded)
    if ascii_map:
        logger.info(
            f"  Transliterated {len(ascii_map)} non-ASCII (中文) column names "
            f"to Stata-legal ASCII"
        )
        # 同步 value_labels 键 (若被改名的列恰有 value label)
        if value_labels:
            _orig2new = {orig: new for new, orig in ascii_map.items()}
            value_labels = {_orig2new.get(k, k): v for k, v in value_labels.items()}
        rename_map.update(ascii_map)

    # 2. 生成 variable labels (基于新 (短/ASCII) 列名)
    var_labels = build_variable_labels(df_encoded)

    # 3. Stata 兼容性校验 (plan v14 §9.5; 缩短后应全过)
    validate_stata_compat(df_encoded, var_labels)

    # 4. core/aux 拆分 (plan v14 §9.1 R42-A + R44-A)
    core_cols = assign_core_columns(df_encoded)
    aux_cols = [c for c in df_encoded.columns if c not in core_cols]

    # 5. 写 .dta 三件套 (经 backend 抽象, 兼容 pyreadstat / pandas)
    core_path = os.path.join(output_dir, f'{output_prefix}_core.dta')
    full_path = os.path.join(output_dir, f'{output_prefix}_full.dta')
    aux_path  = os.path.join(output_dir, f'{output_prefix}_aux.dta')

    write_dta(df_encoded[core_cols], core_path, value_labels, var_labels)
    logger.info(f"  Core .dta 已写入: {core_path} ({len(core_cols)} 列, ≤ {STATA_IC_MAX_VARS})")

    write_dta(df_encoded, full_path, value_labels, var_labels)
    logger.info(f"  Full .dta 已写入: {full_path} ({len(df_encoded.columns)} 列)")

    if aux_cols:
        # aux 含主键 + aux 列, 用户可 merge 1:1 到 core
        aux_with_keys = ['target_bank', 'year'] + [c for c in aux_cols if c not in ('target_bank', 'year')]
        aux_value_labels = {k: v for k, v in value_labels.items() if k in aux_with_keys}
        write_dta(df_encoded[aux_with_keys], aux_path, aux_value_labels, var_labels)
        logger.info(f"  Aux .dta 已写入: {aux_path} ({len(aux_with_keys)} 列)")

    # 6. labels .do
    labels_path = os.path.join(output_dir, f'{output_prefix}_labels.do')
    write_labels_do_file(labels_path, var_labels, value_labels)

    # 7. codebook .xlsx (依赖 codebook.py)
    codebook_path = os.path.join(output_dir, f'{output_prefix}_codebook.xlsx')
    try:
        _write_codebook_xlsx(df_encoded, var_labels, value_labels, core_cols, codebook_path,
                              rename_map=rename_map)
    except Exception as e:
        logger.warning(f"  codebook .xlsx 写入失败 (非阻塞): {e}")

    return {
        'core_dta': core_path,
        'full_dta': full_path,
        'aux_dta':  aux_path if aux_cols else '',
        'labels_do': labels_path,
        'codebook_xlsx': codebook_path,
        'backend': backend_name,  # v3.2.0 M1/7: 'pyreadstat' | 'pandas'
    }


def _write_codebook_xlsx(
    df: pd.DataFrame,
    var_labels: Dict[str, str],
    value_labels: Dict[str, Dict[int, str]],
    core_cols: List[str],
    out_path: str,
    rename_map: Dict[str, str] = None,
) -> None:
    """生成人类可读 codebook .xlsx.

    Args:
        rename_map: v3.2.0 M3/7 新增: {short_stata_name: original_panel_name}
                    用户可在 codebook 反查 Stata 短名对应的原 panel 列名.
    """
    if rename_map is None:
        rename_map = {}
    rows = []
    core_set = set(core_cols)
    for col in df.columns:
        rows.append({
            'var_name': col,
            'original_name': rename_map.get(col, col),  # M3/7: 缩短前原名 (用户反查)
            'label': var_labels.get(col, col),
            'data_type': str(df[col].dtype),
            'is_core': col in core_set,
            'value_labels': '; '.join(f'{k}={v}' for k, v in value_labels.get(col, {}).items()),
            'n_non_null': df[col].notna().sum(),
            'n_unique': df[col].nunique() if df[col].dtype.kind != 'f' else None,
        })
    codebook_df = pd.DataFrame(rows)
    codebook_df.to_excel(out_path, index=False, engine='xlsxwriter')
    logger.info(f"  Codebook .xlsx 已写入: {out_path} ({len(rows)} 列条目; "
                f"含 {len(rename_map)} 个 Stata-shortened names 反查映射)")


def main():
    """Stage 46 CLI 入口 (由 thin shim 46_stata_export.py 调用)."""
    from news_process.core.config import load_config
    from news_process.core.logging import setup_logging

    CONFIG = load_config()
    STAGE_NAME = '46_stata_export'
    log = setup_logging(STAGE_NAME, CONFIG['paths']['log_dir'])
    log.info(f"--- Stage 46 Stata Export (plan v14 §9 stata_export) ---")

    panel_filename = CONFIG.get('filenames', {}).get('output_45_panel_main', '40_panel_yearly.parquet')
    panel_path = os.path.join(CONFIG['paths']['output_dir'], panel_filename)
    output_dir = CONFIG['paths']['output_dir']

    results = export_panel_to_stata(panel_path, output_dir)
    log.info(f"Stage 46 完成. 产出:")
    for k, v in results.items():
        log.info(f"  {k}: {v}")


if __name__ == '__main__':
    main()
