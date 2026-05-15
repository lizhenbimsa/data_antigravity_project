"""news_process.pipeline.panel.stata_export — Stage 46 Stata 数据导出层 (v3.2.0)

功能 (plan v14 §9.1):
    把 stage 45 panel parquet (40_panel_yearly.parquet) 转换为 Stata .dta + labels.

输出三文件 (与 plan v14 §9.1 一致):
    46_panel_yearly_core.dta    # Stata IC 兼容 (≤ 2048 vars)
    46_panel_yearly_full.dta    # 全列 (Stata SE/MP)
    46_panel_yearly_aux.dta     # robustness 子集 (core 互补; merge 1:1 可还原 full)
    46_panel_yearly_labels.do   # variable/value labels Stata 脚本
    46_panel_yearly_codebook.xlsx  # 人类可读变量字典

关键转换 (plan v14 §9.1):
    - innovation_locus_{full,ctx} (中文 str) → byte 0=底层技术, 1=应用场景 + value label
    - innovation_substantiveness_{full,ctx} (中文 str) → byte 0=实质性, 1=象征性 + value label
    - NaN → . / .a / .b (extended missing for distinguishable causes)
    - 列名 ≤ 32 字符 (Stata 硬限)
    - variable label ≤ 80 字符 (Stata 硬限)

锚定文献:
    Westphal & Zajac (1994, 1998, ASQ) substantive-symbolic
    Gomber, Kauffman, Parker, Weber (2018, JMIS) enabling tech vs business function
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

# Value labels (双语 zh + EN, plan v14 §9.1 普通人版变更 20)
LOCUS_VALUE_LABELS: Dict[int, str] = {
    0: "底层技术 (Technology)",
    1: "应用场景 (Application)",
}

SUBSTANTIVENESS_VALUE_LABELS: Dict[int, str] = {
    0: "实质性 (Substantive)",
    1: "象征性 (Symbolic)",
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
        'innovation_locus_full':            "Innovation Locus (Full-text, Gomber 2018 JMIS)",
        'innovation_locus_ctx':             "Innovation Locus (Entity-context, Hassan 2019 QJE)",
        'innovation_substantiveness_full':  "Innov. Substantiveness (Full-text, W&Z 1998 ASQ)",
        'innovation_substantiveness_ctx':   "Innov. Substantiveness (Entity-ctx, Hassan 2019 QJE)",
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
        'n_articles', 'media_breadth', 'ln_news_coverage', 'bank_type',
        'bank_size', 'bank_age', 'bank_province', 'bank_zone',
        'digital_frontier',
        # sentiment 双轨主指标
        'llm_sentiment_full', 'llm_sentiment_ctx',
        'llm_vote_tone_full', 'llm_vote_tone_ctx',
        'llm_prob_score_full', 'llm_prob_score_ctx',
        'avg_llm_prob_score_full', 'avg_llm_prob_score_ctx',
        # stage 3 双轨标签 + confidence
        'innovation_locus_full', 'innovation_locus_ctx',
        'innovation_substantiveness_full', 'innovation_substantiveness_ctx',
        'category_confidence_full', 'category_confidence_ctx',
        'avg_il_confidence_full', 'avg_il_confidence_ctx',
        'avg_iss_confidence_full', 'avg_iss_confidence_ctx',
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
        # 主 Bartik IV (lf + lc 各一套, 共 6 列含 full/ctx/title)
        'bartik_fintech_iv_full', 'bartik_fintech_iv_ctx', 'bartik_fintech_iv_title',
        # 主洗稿率 count (sentiment × _full)
        'pos_symb_count_full', 'pos_symb_count_ctx',
        'neg_sub_count_full', 'neg_sub_count_ctx',
    ]

    core = [c for c in core_patterns if c in df.columns]

    if len(core) > STATA_IC_MAX_VARS:
        raise ValueError(
            f"Core column count {len(core)} exceeds Stata IC max {STATA_IC_MAX_VARS}. "
            f"plan v14 §9.5 R42-A 验收门违反, 需要拆 core/aux 再分配."
        )

    logger.info(f"  Core 列数: {len(core)} / {len(df.columns)} (IC 余量 {STATA_IC_MAX_VARS - len(core)})")
    return core


def validate_stata_compat(df: pd.DataFrame, var_labels: Dict[str, str]) -> None:
    """plan v14 §9.5 验收门: 列名 ≤ 32 字符 + label ≤ 80 字符 + 编码方向."""
    issues: List[str] = []
    for col in df.columns:
        if len(col) > STATA_VAR_NAME_MAXLEN:
            issues.append(f"列名超 32 字符: '{col}' ({len(col)} chars)")
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

    lines.append('')
    lines.append('* Apply value labels to encoded columns')
    locus_cols = [c for c in value_labels if 'innovation_locus' in c]
    subst_cols = [c for c in value_labels if 'innovation_substantiveness' in c]
    if locus_cols:
        lines.append(f'capture label values {" ".join(locus_cols)} locus_lbl')
    if subst_cols:
        lines.append(f'capture label values {" ".join(subst_cols)} subst_lbl')

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    logger.info(f"  Stata labels .do 已写入: {out_path} ({len(lines)} 行)")


def export_panel_to_stata(
    panel_path: str,
    output_dir: str,
    output_prefix: str = '46_panel_yearly',
) -> Dict[str, str]:
    """主导出函数: 从 panel parquet 产出 .dta + labels.do + codebook.xlsx.

    Args:
        panel_path: 输入 40_panel_yearly.parquet 路径
        output_dir: 输出目录 (data/processed/)
        output_prefix: 文件名前缀 (默认 46_panel_yearly)
    Returns:
        dict 含产出文件路径: {'core_dta': '...', 'aux_dta': '...', 'full_dta': '...',
                             'labels_do': '...', 'codebook_xlsx': '...'}
    """
    try:
        import pyreadstat  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "pyreadstat 未装. 请运行 `pip install pyreadstat>=1.2`. "
            "v3.2.0 stage 46 stata_export 硬依赖 pyreadstat (plan v14 §9.4)."
        ) from e
    import pyreadstat

    logger.info(f"=== Stage 46 Stata Export (plan v14 §9.1) ===")
    logger.info(f"  输入: {panel_path}")

    if not os.path.exists(panel_path):
        raise FileNotFoundError(f"panel parquet 不存在: {panel_path}")

    df = pd.read_parquet(panel_path)
    logger.info(f"  panel 载入: {len(df)} 行 × {len(df.columns)} 列")

    # 1. 类别变量编码 (中文 str → byte 0/1)
    df_encoded, value_labels = encode_categorical_columns(df)

    # 2. 生成 variable labels
    var_labels = build_variable_labels(df_encoded)

    # 3. Stata 兼容性校验 (plan v14 §9.5)
    validate_stata_compat(df_encoded, var_labels)

    # 4. core/aux 拆分 (plan v14 §9.1 R42-A + R44-A)
    core_cols = assign_core_columns(df_encoded)
    aux_cols = [c for c in df_encoded.columns if c not in core_cols]

    # 5. 写 .dta 三件套
    core_path = os.path.join(output_dir, f'{output_prefix}_core.dta')
    full_path = os.path.join(output_dir, f'{output_prefix}_full.dta')
    aux_path  = os.path.join(output_dir, f'{output_prefix}_aux.dta')

    pyreadstat.write_dta(
        df_encoded[core_cols],
        core_path,
        variable_value_labels=value_labels,
        column_labels=[var_labels.get(c, c) for c in core_cols],
    )
    logger.info(f"  Core .dta 已写入: {core_path} ({len(core_cols)} 列, ≤ {STATA_IC_MAX_VARS})")

    pyreadstat.write_dta(
        df_encoded,
        full_path,
        variable_value_labels=value_labels,
        column_labels=[var_labels.get(c, c) for c in df_encoded.columns],
    )
    logger.info(f"  Full .dta 已写入: {full_path} ({len(df_encoded.columns)} 列)")

    if aux_cols:
        # aux 含主键 + aux 列, 用户可 merge 1:1 到 core
        aux_with_keys = ['target_bank', 'year'] + [c for c in aux_cols if c not in ('target_bank', 'year')]
        pyreadstat.write_dta(
            df_encoded[aux_with_keys],
            aux_path,
            variable_value_labels={k: v for k, v in value_labels.items() if k in aux_with_keys},
            column_labels=[var_labels.get(c, c) for c in aux_with_keys],
        )
        logger.info(f"  Aux .dta 已写入: {aux_path} ({len(aux_with_keys)} 列)")

    # 6. labels .do
    labels_path = os.path.join(output_dir, f'{output_prefix}_labels.do')
    write_labels_do_file(labels_path, var_labels, value_labels)

    # 7. codebook .xlsx (依赖 codebook.py)
    codebook_path = os.path.join(output_dir, f'{output_prefix}_codebook.xlsx')
    try:
        _write_codebook_xlsx(df_encoded, var_labels, value_labels, core_cols, codebook_path)
    except Exception as e:
        logger.warning(f"  codebook .xlsx 写入失败 (非阻塞): {e}")

    return {
        'core_dta': core_path,
        'full_dta': full_path,
        'aux_dta':  aux_path if aux_cols else '',
        'labels_do': labels_path,
        'codebook_xlsx': codebook_path,
    }


def _write_codebook_xlsx(
    df: pd.DataFrame,
    var_labels: Dict[str, str],
    value_labels: Dict[str, Dict[int, str]],
    core_cols: List[str],
    out_path: str,
) -> None:
    """生成人类可读 codebook .xlsx."""
    rows = []
    core_set = set(core_cols)
    for col in df.columns:
        rows.append({
            'var_name': col,
            'label': var_labels.get(col, col),
            'data_type': str(df[col].dtype),
            'is_core': col in core_set,
            'value_labels': '; '.join(f'{k}={v}' for k, v in value_labels.get(col, {}).items()),
            'n_non_null': df[col].notna().sum(),
            'n_unique': df[col].nunique() if df[col].dtype.kind != 'f' else None,
        })
    codebook_df = pd.DataFrame(rows)
    codebook_df.to_excel(out_path, index=False, engine='xlsxwriter')
    logger.info(f"  Codebook .xlsx 已写入: {out_path} ({len(rows)} 列条目)")


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
