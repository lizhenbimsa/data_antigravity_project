"""news_process.pipeline.panel.export — diagnostics + multi-format panel export.

Extracted from pipeline/panel/runner.py during Phase 2b to enforce single-
responsibility separation:
  - log_diagnostics(panel, df_exploded)  → panel diagnostic statistics
  - export_panel(panel, df_exploded)     → Parquet + Stata .dta export with
                                                32-character Stata column-name
                                                discipline + STATA_LABELS dict.

Importing this module is side-effect free; consumers call the two functions
explicitly.  runner.py re-exports them for backwards compatibility.
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

from news_process.core.reporting import save_dataset
from news_process.pipeline.panel.encode import (
    CONFIG,
    FILENAMES,
    OUTPUT_DIR,
    PANEL_CFG,
    logger,
)

# ============================================================================
# 8. 诊断统计量
# ============================================================================

def log_diagnostics(panel: pd.DataFrame, df_exploded: pd.DataFrame):
    """输出面板诊断统计, 包含分类维度(底层技术/应用场景)的覆盖率、置信度
    和面板平衡性诊断 (G-07)。"""
    logger.info("=" * 60)
    logger.info("步骤 8: 诊断统计量")
    logger.info("=" * 60)

    n_banks = panel['target_bank'].nunique()
    n_years = panel['year'].nunique()
    year_min, year_max = panel['year'].min(), panel['year'].max()

    no_news = (panel['n_articles'] == 0).sum()
    no_news_pct = no_news / len(panel) if len(panel) > 0 else 0

    logger.info(f"  面板维度: {len(panel):,} 行 ({n_banks} 银行 × {n_years} 年)")
    logger.info(f"  时间跨度: {year_min} - {year_max}")
    logger.info(f"  零新闻观测: {no_news:,} ({no_news_pct:.1%})")

    if 'n_articles' in panel.columns:
        logger.info(f"  新闻覆盖量统计:")
        desc = panel['n_articles'].describe()
        logger.info(f"    mean={desc['mean']:.1f}, median={desc['50%']:.0f}, "
                    f"max={desc['max']:.0f}, std={desc['std']:.1f}")

    if 'llm_vote_tone_full' in panel.columns:
        valid_tone = panel['llm_vote_tone_full'].dropna()
        if len(valid_tone) > 0:
            logger.info(f"  LLM 投票情感强度: mean={valid_tone.mean():.4f}, "
                        f"std={valid_tone.std():.4f}")

    # --- 分类维度诊断 ---
    if 'tech_frac' in panel.columns:
        valid_tf = panel['tech_frac'].dropna()
        if len(valid_tf) > 0:
            logger.info(f"  底层技术占比 (tech_frac):")
            logger.info(f"    mean={valid_tf.mean():.3f}, median={valid_tf.median():.3f}, "
                        f"std={valid_tf.std():.3f}")
    for suffix, label in [('_tech', '底层技术'), ('_app', '应用场景')]:
        col = f'n_articles{suffix}'
        if col in panel.columns:
            has_cat = (panel[col] > 0).sum()
            total = (panel['n_articles'] > 0).sum()
            if total > 0:
                logger.info(f"  {label} ({col}): "
                            f"有文章的 Bank-Year = {has_cat}/{total} ({has_cat/total:.1%})")
            else:
                logger.info(f"  {label} ({col}): 无有效新闻观测")
    if 'avg_category_confidence' in panel.columns:
        valid_conf = panel['avg_category_confidence'].dropna()
        if len(valid_conf) > 0:
            logger.info(f"  分类置信度: mean={valid_conf.mean():.3f}, "
                        f"median={valid_conf.median():.3f}")

            # ── G-20: 低置信度分类诊断列 ──
            # 纯诊断性质: 标记 avg_category_confidence < 0.5 的 Bank-Year,
            # 供下游分析筛选, 不改变任何指标的计算逻辑
            panel['low_conf_flag'] = (
                panel['avg_category_confidence'] < 0.5
            ).astype(int)
            low_n = panel['low_conf_flag'].sum()
            low_pct = low_n / max(len(panel), 1)
            logger.info(f"  G-20 低置信度标记: {low_n}/{len(panel)} "
                        f"({low_pct:.1%} Bank-Year, conf < 0.5)")

    # ── G-14: 距离衰减敏感性检验结果摘要 ──
    decay_report = os.path.join(OUTPUT_DIR, 'eval_reports', '38_decay_sensitivity.csv')
    if os.path.exists(decay_report):
        try:
            decay_df = pd.read_csv(decay_report)
            # 计算 uniform vs inverse 的平均 Pearson
            dict_names = ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']
            pearsons = []
            for dn in dict_names:
                u_col, d_col = f'{dn}_uniform', f'{dn}_inverse'
                if u_col in decay_df.columns and d_col in decay_df.columns:
                    r = decay_df[u_col].corr(decay_df[d_col])
                    if not np.isnan(r):
                        pearsons.append(r)
            if pearsons:
                logger.info(f"  G-14 距离衰减: Pearson(uniform, inverse) = "
                            f"{np.mean(pearsons):.4f} (avg), "
                            f"{min(pearsons):.4f} (min)")
        except Exception as e:
            logger.debug(f"  G-14 报告读取失败: {e}")

    # 文章级统计
    logger.info(f"  展开后文章-银行级行数: {len(df_exploded):,}")
    logger.info(f"  多银行文章占比: {df_exploded['is_multi_bank'].mean():.1%}")


    # ── G-07: 面板平衡性诊断 ──
    # 学术依据: Wooldridge (2010), Baltagi (2021) — 不平衡面板的标准诊断
    logger.info("")
    logger.info("  --- 面板平衡性诊断 (G-07) ---")

    # (a) 理论最大行数 vs 实际行数
    max_years = year_max - year_min + 1
    theoretical_rows = n_banks * max_years
    balance_ratio = len(panel) / theoretical_rows if theoretical_rows > 0 else 0
    logger.info(f"  理论最大维度: {n_banks} 银行 × {max_years} 年 = {theoretical_rows:,} 行")
    logger.info(f"  实际行数: {len(panel):,} ({balance_ratio:.1%} 平衡率)")
    if balance_ratio >= 0.95:
        logger.info(f"  ✅ 高度平衡面板 (≥95%)")
    elif balance_ratio >= 0.80:
        logger.info(f"  近似平衡面板 (80-95%)")
    else:
        logger.info(f"  🔴 不平衡面板 (<80%), 建议检查银行进入/退出")

    # (b) 每家银行的年份覆盖
    bank_year_counts = panel.groupby('target_bank')['year'].nunique()
    full_coverage = (bank_year_counts == max_years).sum()
    partial = (bank_year_counts < max_years).sum()
    logger.info(f"  完整覆盖 ({max_years} 年): {full_coverage}/{n_banks} 银行 "
                f"({full_coverage/n_banks:.1%})")
    if partial > 0:
        min_years = bank_year_counts.min()
        logger.info(f"  部分覆盖银行: {partial} 家, 最少仅覆盖 {min_years} 年")

    # (c) 每年的银行数
    year_bank_counts = panel.groupby('year')['target_bank'].nunique()
    logger.info(f"  逐年银行数分布:")
    for yr in sorted(year_bank_counts.index):
        cnt = year_bank_counts[yr]
        marker = "" if cnt == n_banks else f" (缺 {n_banks - cnt})"
        logger.info(f"    {yr}: {cnt} 家{marker}")

    # (d) 有效覆盖率 (有新闻的 Bank-Year 占比)
    has_news = (panel['n_articles'] > 0).sum()
    news_coverage = has_news / len(panel) if len(panel) > 0 else 0
    logger.info(f"  有效新闻覆盖: {has_news}/{len(panel)} Bank-Year ({news_coverage:.1%})")

    # (e) 关键变量缺失率
    key_vars = ['llm_vote_tone_full', 'llm_vote_tone_ctx', 'bank_province',
                'bank_city', 'ln_news_coverage']
    logger.info(f"  关键变量缺失率:")
    for var in key_vars:
        if var in panel.columns:
            miss = panel[var].isna().sum()
            miss_pct = miss / len(panel) if len(panel) > 0 else 0
            logger.info(f"    {var}: {miss:,}/{len(panel):,} ({miss_pct:.1%})")


# ============================================================================
# 9. 导出
# ============================================================================

def export_panel(panel: pd.DataFrame, df_exploded: pd.DataFrame):
    """多格式导出面板数据。

    .. todo:: v3.0-split (Plan-r3 P1-7 锚点, god function)

        本函数是 ``export.py`` 的主体. 内部职责高度异质, 至少应拆为 6 个
        独立子函数:
        1. ``_validate_panel_schema`` -- N1/N2 schema 守护与列必需性检查
        2. ``_export_parquet`` -- pyarrow 写 panel.parquet (流水线下游主格式)
        3. ``_export_csv`` -- pandas to_csv 写 panel.csv (人类可读)
        4. ``_clean_stata_columns`` -- 32 字符截断 + 哈希碰撞防撞
        5. ``_build_stata_labels`` -- STATA_LABELS 字典 + 列存在性过滤
           (含 P0-2 修复后的 dedup 不变量)
        6. ``_export_dta`` -- pandas to_stata 写 .dta (raise on失败, B-2 修复)

        拆分后 STATA_LABELS dict 可移到模块级常量, 配合 P0-2 invariant test
        实现"加新列必须加新 label, 不允许 silent drop".

    【方法论演变与学术辩护 (Methodological Evolution & Academic Defense)】
    本函数作为项目数据管线的最终“封印”环节，承载着 Python 动态数据流与传统计量经济学软件（Stata）严格边界之间的适配责任。
    - 前置假设条件 (A Priori Assumptions)：假定 Python 端的所有浮点计算（Float64/Int64）必须降级兼容为 Stata 支持的 strict float/double，否则 xtset 或 reghdfe 会遭遇不可预知的 type casting error。
    - 潜在局限性 (Potential Limitations)：Stata 的底层 C 语言框架要求变量名极其苛刻的 32 字符截断限制。在高度复杂的深度网络推导中（例如 LLM_peer_competition_idx_full），强行截断极易产生列名哈希碰撞（Collision）。本模块构建了严密的截断降级与字典映射防撞机制。
    
    【通俗应用 (Layman's Terms)】
    这里是数据的“出关口岸”。Python 可以随意给数据起长名字（比如长达100个字母），但古老的 Stata 只认 32 个字母，超出就报错，甚至把两个名字砍短后变成同名从而导致数据崩溃。本模块就是个极其严格的“护照审查员”，把长名字安全剪裁，并贴上详细的学术标签（STATA_LABELS），确保导入 Stata 后能直接跑回归。
    """
    # ────────────────────────────────────────────────────────────────────────
    # Step 5 硬化 (致命问题 5 / 红队 v6 N2): REQUIRED_PANEL_COLUMNS 门槛.
    # 在写出任何 .parquet / .dta / .csv 之前先验列, 缺列即 raise RuntimeError,
    # 杜绝"新 .parquet 写成功但 .dta 异常"导致 .parquet 与 .dta 语义错位的隐性
    # 灾难 (此前 40_panel_yearly.parquet=5月5日 而 .dta=5月1日 的真实事故).
    # 校验集对应 Step 4 硬化保证存在的 4 个上游契约:
    #   stage 15 (政策对齐)  → 7h-token 四象限分类列
    #   stage 30 (双轨稳健)  → strat_diff_t2v_*/policy_cosine_sim_t2v_*
    #   stage 25/26/27 (硬import) → strat_diff_full / auth_sim_* / benefit_sim_*
    # 使用 raise 而非 assert (assert 在 python -O 优化模式下会被剥离).
    REQUIRED_PANEL_COLUMNS = [
        # bank-year 主键
        'target_bank', 'year',
        # stage 30 双轨稳健性 (4 列, 由 8e 步骤 merge)
        'strat_diff_t2v_full', 'strat_diff_t2v_ctx',
        'policy_cosine_sim_t2v_full', 'policy_cosine_sim_t2v_ctx',
    ]
    _missing = [c for c in REQUIRED_PANEL_COLUMNS if c not in panel.columns]
    if _missing:
        raise RuntimeError(
            f"[export_panel] panel 缺失必填列 {_missing}; "
            f"现有 {len(panel.columns)} 列前 30 个: {list(panel.columns)[:30]}; "
            f"拒绝写出避免 .parquet/.dta 语义错位。"
            f" 请检查上游 stage 15/30 输出是否存在 + Step 4 硬化是否生效."
        )
    logger.info(
        f"[export_panel] REQUIRED_PANEL_COLUMNS 校验通过 "
        f"({len(REQUIRED_PANEL_COLUMNS)} 列 / panel 共 {len(panel.columns)} 列, "
        f"{len(panel)} 行)"
    )

    logger.info("=" * 60)
    logger.info("步骤 9: 多格式导出")
    logger.info("=" * 60)

    # 年度面板 Parquet
    panel_filename = FILENAMES.get('output_40_panel_yearly', '40_panel_yearly.parquet')
    panel_path = os.path.join(OUTPUT_DIR, panel_filename)
    # 血缘修复 (audit-fixes 2026-05-29): stage 45 是 fan-in, runner 硬读
    # 24_herd_decay (主) + 15_article_alignment (RuntimeError if absent,
    # runner.py:1077) + 30_text2vec_indicators (RuntimeError if absent,
    # runner.py:1534). 记全部硬上游闭包, 否则 verify_data_integrity 对 15/30 的
    # 篡改/陈旧检测不到 (与 stage 14 fintech_intensity 记双输入的受测约定一致).
    # 缺失文件由 data_versioning 的 exists 守卫优雅跳过.
    _od = CONFIG['paths']['output_dir']
    _fn = CONFIG['filenames']
    input_files = [
        os.path.join(_od, _fn['output_24_herd_decay']),
        os.path.join(_od, _fn.get('output_15_article_alignment', '15_article_alignment.parquet')),
        os.path.join(_od, '30_text2vec_indicators.parquet'),  # 无 config key (硬编码于 validation/text2vec.py)
    ]
    save_dataset(panel, panel_path, logger,
                stage_name="45_panel_export_main",
                config=CONFIG,
                input_files=input_files)

    # 年度面板 Stata .dta
    if PANEL_CFG.get('export_stata', True):
        dta_path = os.path.splitext(panel_path)[0] + '.dta'
        # B-3 修复 (v7 外副作用): 先删除旧 .dta 再尝试写出, 避免本次写出失败时
        # 旧 .dta (与新 .parquet 语义错位) 残留导致 Stata 端误用陈旧数据。
        # 这是 N2 修复 (REQUIRED_PANEL_COLUMNS) 的同精神延伸: 杜绝 .parquet/.dta
        # 错位灾难。
        if os.path.exists(dta_path):
            os.remove(dta_path)
            logger.info(f"  已删除旧 .dta (避免与新 .parquet 错位): {dta_path}")
        try:
            panel_stata = panel.copy()
            # B-1 修复 (v7 外副作用): 防御性 object → float64 转换。
            # 根因: 上游 geography.py 等 buf_results 模式生成的列 (例如
            # prox_50km_tone_full), 当多个 bank-year 的 within[tone_col].mean()
            # 返回 NaN 时, pd.DataFrame(buf_rows) 推断该列为 object dtype, 即使
            # 里面其实有少量 float 值。to_stata() 在 object 列上误判为
            # "Object arrays containing only null values" 然后 raise.
            # 这里把所有 object dtype 但语义为数值的列 (无 str 元素) 强制转为
            # float64, 让 to_stata 能正确识别。
            # 注意: pyarrow 写 .parquet 时会自动恢复 dtype, 因此 .parquet 路径
            # 不受影响; 此修复仅为 .dta 路径补齐 dtype 语义.
            for _col in panel_stata.select_dtypes(include=['object']).columns:
                _s = panel_stata[_col]
                _non_null = _s.dropna()
                if len(_non_null) > 0 and _non_null.map(lambda x: isinstance(x, str)).any():
                    continue  # 真字符串列 (target_bank 等), 不转
                try:
                    panel_stata[_col] = pd.to_numeric(_s, errors='coerce').astype(float)
                except Exception:
                    pass  # 极少数无法转换的留给 to_stata 自己处理 (会被下面 raise 暴露)
            # v6/F2 Stata 兼容: pandas Int8/Int16/Int32/Int64 nullable 类型
            #   to_stata() 不能直接处理 <NA>，需先转 Float64 (NaN 会保留)。
            #   Stata 端用 mvdecode 处理缺失，与原 NaN 语义一致。
            for _col in panel_stata.select_dtypes(include=['Int8','Int16','Int32','Int64']).columns:
                panel_stata[_col] = panel_stata[_col].astype('Float64')
            # boolean nullable 同理
            for _col in panel_stata.select_dtypes(include=['boolean']).columns:
                panel_stata[_col] = panel_stata[_col].astype('Float64')
            # Stata 列名清理: 复用 papers/_common/tables.py 的统一实现
            from news_process.papers._common.tables import sanitize_stata_columns
            panel_stata.columns = sanitize_stata_columns(panel_stata.columns, max_len=32)
            # 确保数值列没有 nullable dtypes（Stata 不支持）
            for col in panel_stata.select_dtypes(include=['Float64', 'Int64']).columns:
                panel_stata[col] = panel_stata[col].astype(float)
            # 学术级变量标签 (Stata variable labels, ≤80 字符)
            STATA_LABELS = {
                # 注意力指数 (Da et al. 2011; Fang & Peress 2009)
                'ft_attn_yr':    'Fintech Attention Index (Year)',
                'ft_attn_prov':  'Fintech Attention (Province, Exp-Wt)',
                'ft_attn_city':  'Fintech Attention (City, Exp-Wt)',
                # 媒体异质性 - 占比
                'fin_media_frac':              'Financial Media Share',
                'comp_media_frac':             'Comprehensive Media Share',
                'central_media_frac':          'Central-Level Media Share',
                # 媒体异质性 - 情感均值 (Full 轨道)
                'tone_fin_media_full':         'Avg Tone: Financial Media (Full)',
                'tone_comp_media_full':        'Avg Tone: Comprehensive Media (Full)',
                'tone_other_media_full':       'Avg Tone: Other Media (Full)',
                'tone_central_media_full':     'Avg Tone: Central Media (Full)',
                'tone_local_media_full':       'Avg Tone: Local Media (Full)',
                # 媒体异质性 - 情感均值 (Ctx 轨道)
                'tone_fin_media_ctx':          'Avg Tone: Financial Media (Ctx)',
                'tone_comp_media_ctx':         'Avg Tone: Comprehensive Media (Ctx)',
                'tone_other_media_ctx':        'Avg Tone: Other Media (Ctx)',
                'tone_central_media_ctx':      'Avg Tone: Central Media (Ctx)',
                'tone_local_media_ctx':        'Avg Tone: Local Media (Ctx)',
                # 媒体异质性 - 情感缺口 (Full 轨道)
                'tone_gap_fin_other_full':     'Tone Gap: Fin - Other (Full)',
                'tone_gap_comp_other_full':    'Tone Gap: Comp - Other (Full)',
                'tone_gap_fin_comp_full':      'Tone Gap: Fin - Comp (Full)',
                'tone_gap_central_local_full': 'Tone Gap: Central - Local (Full)',
                # 媒体异质性 - 情感缺口 (Ctx 轨道)
                'tone_gap_fin_other_ctx':      'Tone Gap: Fin - Other (Ctx)',
                'tone_gap_comp_other_ctx':     'Tone Gap: Comp - Other (Ctx)',
                'tone_gap_fin_comp_ctx':       'Tone Gap: Fin - Comp (Ctx)',
                'tone_gap_central_local_ctx':  'Tone Gap: Central - Local (Ctx)',
                # 媒体异质性 - 占比 (新增四维度)
                'official_media_frac':          'Official Media Share (You 2018)',
                'market_media_frac':            'Market Media Share (You 2018)',
                'deepdive_media_frac':          'Deep-dive Periodical Share (Bushee 2010)',
                'daily_media_frac':             'High-freq Daily Share (Tetlock 2007)',
                # 媒体异质性 - 新增情感均值 (Full 轨道)
                'tone_official_media_full':     'Avg Tone: Official Media (Full)',
                'tone_nonoff_media_full':       'Avg Tone: Non-Official Media (Full)',
                'tone_market_media_full':       'Avg Tone: Market Media (Full)',
                'tone_nonmkt_media_full':       'Avg Tone: Non-Market Media (Full)',
                'tone_deepdive_media_full':     'Avg Tone: Deep-dive Media (Full)',
                'tone_nondeep_media_full':      'Avg Tone: Non-Deep Media (Full)',
                'tone_daily_media_full':        'Avg Tone: Daily Media (Full)',
                'tone_nondaily_media_full':     'Avg Tone: Non-Daily Media (Full)',
                # 媒体异质性 - 新增情感均值 (Ctx 轨道)
                'tone_official_media_ctx':      'Avg Tone: Official Media (Ctx)',
                'tone_nonoff_media_ctx':        'Avg Tone: Non-Official Media (Ctx)',
                'tone_market_media_ctx':        'Avg Tone: Market Media (Ctx)',
                'tone_nonmkt_media_ctx':        'Avg Tone: Non-Market Media (Ctx)',
                'tone_deepdive_media_ctx':      'Avg Tone: Deep-dive Media (Ctx)',
                'tone_nondeep_media_ctx':       'Avg Tone: Non-Deep Media (Ctx)',
                'tone_daily_media_ctx':         'Avg Tone: Daily Media (Ctx)',
                'tone_nondaily_media_ctx':      'Avg Tone: Non-Daily Media (Ctx)',
                # 媒体异质性 - 新增情感缺口 (Full)
                'tone_gap_official_nonoff_full':   'Tone Gap: Official-NonOff (Full)',
                'tone_gap_market_nonmkt_full':     'Tone Gap: Market-NonMkt (Full)',
                'tone_gap_deepdive_nondeep_full':  'Tone Gap: DeepDive-NonDeep (Full)',
                'tone_gap_daily_nondaily_full':    'Tone Gap: Daily-NonDaily (Full)',
                # 媒体异质性 - 新增情感缺口 (Ctx)
                'tone_gap_official_nonoff_ctx':    'Tone Gap: Official-NonOff (Ctx)',
                'tone_gap_market_nonmkt_ctx':      'Tone Gap: Market-NonMkt (Ctx)',
                'tone_gap_deepdive_nondeep_ctx':   'Tone Gap: DeepDive-NonDeep (Ctx)',
                'tone_gap_daily_nondaily_ctx':     'Tone Gap: Daily-NonDaily (Ctx)',
                # 集中度
                'media_hhi':                   'Media Source HHI',
                # 媒体权威性加权 (Holzman et al. 2023, TAR)
                'llm_vote_tone_mw_full':          'LLM Vote Tone (Media-Auth Wt, Full)',
                'llm_vote_tone_mw_ctx':           'LLM Vote Tone (Media-Auth Wt, Ctx)',
                'llm_vote_cont_mw_full':          'LLM Vote Cont (Media-Auth Wt, Full)',
                'llm_vote_cont_mw_ctx':           'LLM Vote Cont (Media-Auth Wt, Ctx)',
                'llm_models_avg_tone_mw_full':    'LLM Avg Tone (Media-Auth Wt, Full)',
                'llm_models_avg_tone_mw_ctx':     'LLM Avg Tone (Media-Auth Wt, Ctx)',
                'dict_avg_tone_mw_full':          'Dict Avg Tone (Media-Auth Wt, Full)',
                'dict_avg_tone_mw_ctx':           'Dict Avg Tone (Media-Auth Wt, Ctx)',
                'dict_avg_idf_tone_mw_full':      'Dict IDF Tone (Media-Auth Wt, Full)',
                'dict_avg_idf_tone_mw_ctx':       'Dict IDF Tone (Media-Auth Wt, Ctx)',
                'bert_avg_pos_mw_full':           'BERT Avg Pos (Media-Auth Wt, Full)',
                'bert_avg_pos_mw_ctx':            'BERT Avg Pos (Media-Auth Wt, Ctx)',
                'bert_avg_neg_mw_full':           'BERT Avg Neg (Media-Auth Wt, Full)',
                'bert_avg_neg_mw_ctx':            'BERT Avg Neg (Media-Auth Wt, Ctx)',
                # MSENT 计数型情感 (He et al. 2024, IRFA)
                'avg_msent_full':                 'MSENT (Neg-Pos)/(Neg+Pos) EW Mean (Full)',
                'avg_msent_ctx':                  'MSENT (Neg-Pos)/(Neg+Pos) EW Mean (Ctx)',
                'avg_msent_std_full':              'MSENT Std Dev (Full)',
                'avg_msent_std_ctx':               'MSENT Std Dev (Ctx)',
                # 文章长度 (He et al. 2024, IRFA)
                'avg_article_length':             'Article Length ln(1+avg_words)',
                # Fintech Exposure (Dim et al. 2024 概念迁移)
                'fintech_exposure_full':   'Fintech Exposure (Cov*Std, Full)',
                'fintech_exposure_ctx':    'Fintech Exposure (Cov*Std, Ctx)',
                # 截面标准化 (Fama-MacBeth 1973)
                'llm_vote_tone_full_z':    'LLM Vote Tone Z-scored (Full)',
                'llm_vote_tone_ctx_z':     'LLM Vote Tone Z-scored (Ctx)',
                'llm_vote_cont_full_z':    'LLM Vote Cont Z-scored (Full)',
                'llm_vote_cont_ctx_z':     'LLM Vote Cont Z-scored (Ctx)',
                'dict_avg_tone_full_z':    'Dict Avg Tone Z-scored (Full)',
                'dict_avg_tone_ctx_z':     'Dict Avg Tone Z-scored (Ctx)',
                'ln_news_coverage_z':      'News Coverage ln Z-scored',
                'media_breadth_z':         'Media Breadth Z-scored',
                'fintech_exposure_full_z': 'Fintech Exposure Z (Full)',
                'fintech_exposure_ctx_z':  'Fintech Exposure Z (Ctx)',
                # 银行注册地地理信息 (Luo & Li 2025, FRL, Table A.2)
                # 用途: vce(cluster bank_province), vce(cluster bank_city)
                'bank_province':                   'Bank HQ Province (Registration)',
                'bank_city':                       'Bank HQ City (Registration)',
                # Leave-one-out 地理平均情感 IV (Luo & Li 2025, Table 3)
                # 定义: 同省/同城市其他银行的年度平均情感 (排除自身)
                # 用途: ivreghdfe Y (tone = prov_leave1out_tone_full) X, ...
                'prov_leave1out_tone_full':         'Province Leave-1-Out Tone (Full)',
                'prov_leave1out_tone_ctx':          'Province Leave-1-Out Tone (Ctx)',
                'city_leave1out_tone_full':         'City Leave-1-Out Tone (Full)',
                'city_leave1out_tone_ctx':          'City Leave-1-Out Tone (Ctx)',
                # Bartik IV — 银行类型维度 (主)
                'bank_type':                           'Bank Type (nfra_type)',
                'bartik_type_iv_full':                 'Bartik IV: Bank-Type (Full)',
                'bartik_type_iv_ctx':                  'Bartik IV: Bank-Type (Ctx)',
                'bartik_type_share_soe':               'Bartik Share: SOE Banks',
                'bartik_type_share_joint':             'Bartik Share: Joint-Stock',
                'bartik_type_share_city':              'Bartik Share: City Commercial',
                'bartik_type_share_rural':             'Bartik Share: Rural Commercial',
                'bartik_type_share_private':           'Bartik Share: Private Banks',
                'bartik_type_share_foreign':           'Bartik Share: Foreign Banks',
                # Bartik IV — 规模维度 (稳健性 1)
                'bank_scale':                          'Bank Scale (enterprise_scale)',
                'bartik_scale_iv_full':                'Bartik IV: Bank-Scale (Full)',
                'bartik_scale_iv_ctx':                 'Bartik IV: Bank-Scale (Ctx)',
                'bartik_scale_share_L':                'Bartik Share: Large Banks',
                'bartik_scale_share_M':                'Bartik Share: Medium Banks',
                'bartik_scale_share_S':                'Bartik Share: Small Banks',
                'bartik_scale_share_XS':               'Bartik Share: Micro Banks',
                # Bartik IV — 金融科技类型维度 (稳健性 2)
                'bartik_fintech_iv_full':              'Bartik IV: Fintech-Category (Full)',
                'bartik_fintech_iv_ctx':               'Bartik IV: Fintech-Category (Ctx)',
                'bartik_fintech_share_tech':           'Bartik Share: Technology',
                'bartik_fintech_share_app':            'Bartik Share: Application',
                # Bartik IV — 媒体类型维度 (稳健性 3)
                'bartik_media_iv_full':                'Bartik IV: Media-Type (Full)',
                'bartik_media_iv_ctx':                 'Bartik IV: Media-Type (Ctx)',
                'bartik_media_share_fin':              'Bartik Share: Financial Media',
                'bartik_media_share_comp':             'Bartik Share: Comprehensive Media',
                # Bartik IV — 中央/地方 (稳健性 4)
                'bartik_mcentral_iv_full':             'Bartik IV: Central-Local (Full)',
                'bartik_mcentral_iv_ctx':              'Bartik IV: Central-Local (Ctx)',
                'bartik_mcentral_share_central':       'Bartik Share: Central Media',
                'bartik_mcentral_share_local':         'Bartik Share: Local Media',
                # Bartik IV — 财经/非财经 (稳健性 5)
                'bartik_mfin_iv_full':                 'Bartik IV: Fin-NonFin (Full)',
                'bartik_mfin_iv_ctx':                  'Bartik IV: Fin-NonFin (Ctx)',
                'bartik_mfin_share_fin':               'Bartik Share: Financial',
                'bartik_mfin_share_nonfin':            'Bartik Share: Non-Financial',
                # Bartik IV — 综合类/非综合类 (稳健性 6)
                'bartik_mcomp_iv_full':                'Bartik IV: Comp-NonComp (Full)',
                'bartik_mcomp_iv_ctx':                 'Bartik IV: Comp-NonComp (Ctx)',
                'bartik_mcomp_share_comp':             'Bartik Share: Comprehensive',
                'bartik_mcomp_share_noncomp':          'Bartik Share: Non-Comprehensive',
                # Bartik IV — 官方/非官方 (稳健性 7a)
                'bartik_mofficial_iv_full':             'Bartik IV: Official-NonOff (Full)',
                'bartik_mofficial_iv_ctx':              'Bartik IV: Official-NonOff (Ctx)',
                'bartik_mofficial_share_official':      'Bartik Share: Official Media',
                'bartik_mofficial_share_nonoff':        'Bartik Share: Non-Official',
                # Bartik IV — 市场化/非市场化 (稳健性 7b)
                'bartik_mmarket_iv_full':               'Bartik IV: Market-NonMkt (Full)',
                'bartik_mmarket_iv_ctx':                'Bartik IV: Market-NonMkt (Ctx)',
                'bartik_mmarket_share_market':          'Bartik Share: Market Media',
                'bartik_mmarket_share_nonmkt':          'Bartik Share: Non-Market',
                # Bartik IV — 出版频率三方 (稳健性 7c)
                'bartik_mfreq_iv_full':                'Bartik IV: Pub-Frequency (Full)',
                'bartik_mfreq_iv_ctx':                 'Bartik IV: Pub-Frequency (Ctx)',
                'bartik_mfreq_share_deepdive':          'Bartik Share: Deep-dive',
                'bartik_mfreq_share_daily':             'Bartik Share: Daily',
                # Bartik IV — 深度/非深度 (稳健性 7d)
                'bartik_mdeep_iv_full':                'Bartik IV: Deep-NonDeep (Full)',
                'bartik_mdeep_iv_ctx':                 'Bartik IV: Deep-NonDeep (Ctx)',
                'bartik_mdeep_share_deepdive':          'Bartik Share: Deep-dive',
                'bartik_mdeep_share_nondeep':           'Bartik Share: Non-Deep',
                # Bartik IV — 日报/非日报 (稳健性 7e)
                'bartik_mdaily_iv_full':                'Bartik IV: Daily-NonDaily (Full)',
                'bartik_mdaily_iv_ctx':                 'Bartik IV: Daily-NonDaily (Ctx)',
                'bartik_mdaily_share_daily':            'Bartik Share: Daily',
                'bartik_mdaily_share_nondaily':         'Bartik Share: Non-Daily',
                # Bartik IV — 媒体省份 (稳健性 8)
                'bartik_mprov_iv_full':                'Bartik IV: Media-Province (Full)',
                'bartik_mprov_iv_ctx':                 'Bartik IV: Media-Province (Ctx)',
                # Bartik IV — 媒体权威性 (稳健性 8)
                'bartik_mauth_iv_full':                'Bartik IV: Media-Authority (Full)',
                'bartik_mauth_iv_ctx':                 'Bartik IV: Media-Authority (Ctx)',
                'bartik_mauth_share_high':             'Bartik Share: High Authority',
                'bartik_mauth_share_mid':              'Bartik Share: Mid Authority',
                'bartik_mauth_share_low':              'Bartik Share: Low Authority',
                # Bartik IV — 文章长度 (稳健性 9)
                'bartik_doclen_iv_full':               'Bartik IV: Doc-Length (Full)',
                'bartik_doclen_iv_ctx':                'Bartik IV: Doc-Length (Ctx)',
                'bartik_doclen_share_long':            'Bartik Share: Long Articles',
                'bartik_doclen_share_short':           'Bartik Share: Short Articles',
                # Bartik IV — 半年度 (稳健性 10)
                'bartik_half_iv_full':                 'Bartik IV: Half-Year (Full)',
                'bartik_half_iv_ctx':                  'Bartik IV: Half-Year (Ctx)',
                'bartik_half_share_H1':                'Bartik Share: First Half',
                'bartik_half_share_H2':                'Bartik Share: Second Half',
                # Bartik IV — 季度 (稳健性 11)
                'bartik_qtr_iv_full':                  'Bartik IV: Quarter (Full)',
                'bartik_qtr_iv_ctx':                   'Bartik IV: Quarter (Ctx)',
                # Bartik IV — 月度 (稳健性 12)
                'bartik_month_iv_full':                'Bartik IV: Month (Full)',
                'bartik_month_iv_ctx':                 'Bartik IV: Month (Ctx)',
                # Bartik IV — 工作日/周末 (稳健性 13)
                'bartik_wkday_iv_full':                'Bartik IV: Weekday-Weekend (Full)',
                'bartik_wkday_iv_ctx':                 'Bartik IV: Weekday-Weekend (Ctx)',
                # Bartik IV — 专属/共享 (稳健性 14)
                'bartik_excl_iv_full':                 'Bartik IV: Exclusive-Shared (Full)',
                'bartik_excl_iv_ctx':                  'Bartik IV: Exclusive-Shared (Ctx)',
                'bartik_excl_share_exclusive':         'Bartik Share: Exclusive',
                'bartik_excl_share_shared':            'Bartik Share: Shared',
                # Bartik IV — 地理邻近 (稳健性 15)
                'bartik_geoprox_iv_full':              'Bartik IV: Geo-Proximity (Full)',
                'bartik_geoprox_iv_ctx':               'Bartik IV: Geo-Proximity (Ctx)',
                # Bartik IV — 标题出现 (稳健性 16)
                'bartik_title_iv_full':                'Bartik IV: Title-Body (Full)',
                'bartik_title_iv_ctx':                 'Bartik IV: Title-Body (Ctx)',
                # Bartik IV — 关键词多样性 (稳健性 17)
                'bartik_mden_iv_full':                 'Bartik IV: Mention-Density (Full)',
                'bartik_mden_iv_ctx':                  'Bartik IV: Mention-Density (Ctx)',
                # Bartik IV — 关键词密度 (稳健性 18)
                'bartik_mcount_iv_full':               'Bartik IV: Mention-Count (Full)',
                'bartik_mcount_iv_ctx':                'Bartik IV: Mention-Count (Ctx)',
                # Bartik IV — 提及密度 (稳健性 19)
                'bartik_breadth_iv_full':              'Bartik IV: Outlet-Breadth (Full)',
                'bartik_breadth_iv_ctx':               'Bartik IV: Outlet-Breadth (Ctx)',

                'bartik_sentlen_iv_full':              'Bartik IV: Sentence-Length (Full)',
                'bartik_sentlen_iv_ctx':               'Bartik IV: Sentence-Length (Ctx)',
                # Bartik IV — 词汇丰富度 (稳健性 22)
                'bartik_ttr_iv_full':                  'Bartik IV: Type-Token-Ratio (Full)',
                'bartik_ttr_iv_ctx':                   'Bartik IV: Type-Token-Ratio (Ctx)',
                # Bartik IV — 平均句长 (稳健性 23)
                'bartik_pubfmt_iv_full':               'Bartik IV: Pub-Format (Full)',
                'bartik_pubfmt_iv_ctx':                'Bartik IV: Pub-Format (Ctx)',
                # Bartik IV — 词汇丰富度 (稳健性 24)
                'bartik_author_iv_full':               'Bartik IV: Author-Byline (Full)',
                'bartik_author_iv_ctx':                'Bartik IV: Author-Byline (Ctx)',
                # Bartik IV — 出版形态 (稳健性 25)
                'bartik_page_iv_full':                 'Bartik IV: Section-Position (Full)',
                'bartik_page_iv_ctx':                  'Bartik IV: Section-Position (Ctx)',
                # Bartik IV — 作者署名 (稳健性 26)
                'bartik_pgnum_iv_full':                'Bartik IV: Page-Number (Full)',
                'bartik_pgnum_iv_ctx':                 'Bartik IV: Page-Number (Ctx)',
                # Bartik IV — 版面位置 (稳健性 27)
                'bartik_kwdiv_iv_full':                'Bartik IV: Keyword-Diversity (Full)',
                'bartik_kwdiv_iv_ctx':                 'Bartik IV: Keyword-Diversity (Ctx)',
                # Bartik IV — 页号位置 (稳健性 28)
                'bartik_kwden_iv_full':                'Bartik IV: Keyword-Density (Full)',
                'bartik_kwden_iv_ctx':                 'Bartik IV: Keyword-Density (Ctx)',
                # Bartik IV — 基期敏感性
                'bartik_type_iv_full_t0':              'Bartik IV: Type (Full, T0)',
                'bartik_type_iv_full_t1':              'Bartik IV: Type (Full, T0+1)',
                'bartik_type_iv_full_t01':             'Bartik IV: Type (Full, T0&T0+1)',
                'bartik_type_iv_ctx_t0':               'Bartik IV: Type (Ctx, T0)',
                'bartik_type_iv_ctx_t1':               'Bartik IV: Type (Ctx, T0+1)',
                'bartik_type_iv_ctx_t01':              'Bartik IV: Type (Ctx, T0&T0+1)',
                # 经济圈 LOO IV
                'zone_leave1out_tone_full':            'Econ Zone Leave-1-Out Tone (Full)',
                'zone_leave1out_tone_ctx':             'Econ Zone Leave-1-Out Tone (Ctx)',
                'bank_zone':                           'Economic Zone',
                # DID 政策冲击
                'dcep_treated':                        'DCEP Pilot (0/1)',
                'dcep_post':                           'Post DCEP Pilot (0/1)',
                'dcep_treat_year':                     'DCEP First Treatment Year',
                'sandbox_treated':                     'Fintech Sandbox (0/1)',
                'sandbox_post':                        'Post Sandbox (0/1)',
                'sandbox_treat_year':                  'Sandbox First Treatment Year',
                # 权威政策响应度 (Stage 26, Hassan et al. 2019)
                'auth_sim_tfidf_c_full':               'Auth Alignment TF-IDF char (Full)',
                'auth_sim_tfidf_w_full':               'Auth Alignment TF-IDF word (Full)',
                'auth_sim_lda_full':                   'Auth Alignment LDA (Full)',
                'auth_sim_emb_full':                   'Auth Alignment Embedding (Full)',
                'auth_sim_tfidf_c_ctx':                'Auth Alignment TF-IDF char (Ctx)',
                'auth_sim_tfidf_w_ctx':                'Auth Alignment TF-IDF word (Ctx)',
                'auth_sim_lda_ctx':                    'Auth Alignment LDA (Ctx)',
                'auth_sim_emb_ctx':                    'Auth Alignment Embedding (Ctx)',
                # 文本张量双轨稳健性 (Stage 30)
                'strat_diff_t2v_full':                 'Strategic Diff (T2V, Full)',
                'strat_diff_t2v_ctx':                  'Strategic Diff (T2V, Ctx)',
                'policy_cosine_sim_t2v_full':          'Policy Auth Sim (T2V, Full)',
                'policy_cosine_sim_t2v_ctx':           'Policy Auth Sim (T2V, Ctx)',
                # Event Study 动态效应 (Callaway & Sant'Anna 2021, JoE)
                'dcep_rel_year':                       'DCEP Relative Year to Treatment',
                'dcep_lead3':                          'DCEP Lead 3 Periods (k=-3)',
                'dcep_lead2':                          'DCEP Lead 2 Periods (k=-2)',
                'dcep_lag0':                           'DCEP Treatment Year (k=0)',
                'dcep_lag1':                           'DCEP Lag 1 Period (k=+1)',
                'dcep_lag2':                           'DCEP Lag 2 Periods (k=+2)',
                'dcep_lag3':                           'DCEP Lag 3 Periods (k=+3)',
                'dcep_lead4plus':                      'DCEP Lead 4+ Periods (k<=-4)',
                'dcep_lag4plus':                       'DCEP Lag 4+ Periods (k>=+4)',
                'sandbox_rel_year':                    'Sandbox Relative Year to Treatment',
                'sandbox_lead3':                       'Sandbox Lead 3 Periods (k=-3)',
                'sandbox_lead2':                       'Sandbox Lead 2 Periods (k=-2)',
                'sandbox_lag0':                        'Sandbox Treatment Year (k=0)',
                'sandbox_lag1':                        'Sandbox Lag 1 Period (k=+1)',
                'sandbox_lag2':                        'Sandbox Lag 2 Periods (k=+2)',
                'sandbox_lag3':                        'Sandbox Lag 3 Periods (k=+3)',
                'sandbox_lead4plus':                   'Sandbox Lead 4+ Periods (k<=-4)',
                'sandbox_lag4plus':                    'Sandbox Lag 4+ Periods (k>=+4)',
                # LLM 置信度 (Shapiro et al. 2022, JoE; Baker et al. 2024, JAR)
                'avg_llm_conf_full':                   'LLM Avg Confidence (Full)',
                'avg_llm_conf_std_full':               'LLM Confidence Std Dev (Full)',
                'avg_llm_conf_ctx':                    'LLM Avg Confidence (Ctx)',
                'avg_llm_conf_std_ctx':                'LLM Confidence Std Dev (Ctx)',
                'avg_gpt54nano_conf_full':              'GPT-5nano Confidence (Full)',
                'avg_gpt54nano_conf_ctx':               'GPT-5nano Confidence (Ctx)',
                'avg_gemini31111_conf_full':               'Gemini-3 Confidence (Full)',
                'avg_gemini31111_conf_ctx':                'Gemini-3 Confidence (Ctx)',
                'avg_deepseekv4_conf_full':                'Grok-4.1 Confidence (Full)',
                'avg_deepseekv4_conf_ctx':                 'Grok-4.1 Confidence (Ctx)',
                # 其他
                'has_coverage':                        'Has News Coverage (0/1)',
                # ═══ 异质性分析变量 (Angrist & Pischke 2009; Brambor et al. 2006) ═══
                'is_soe':                              'SOE Dummy (0/1)',
                'bank_scale_ord':                      'Bank Scale Ordinal (XS=1..L=4)',
                'high_coverage':                       'High Media Coverage (0/1)',
                'tone_x_soe_full':                     'Tone x SOE (Full)',
                'tone_x_soe_ctx':                      'Tone x SOE (Ctx)',
                'tone_x_scale_full':                   'Tone x Bank Scale (Full)',
                'tone_x_scale_ctx':                    'Tone x Bank Scale (Ctx)',
                'tone_x_highcov_full':                 'Tone x High Coverage (Full)',
                'tone_x_highcov_ctx':                  'Tone x High Coverage (Ctx)',
                'digital_frontier':                    'Digital Frontier (0/1)',
                'dcep_ddd_digfront':                   'DCEP x Post x DigFrontier (DDD)',
                'sandbox_ddd_digfront':                'Sandbox x Post x DigFrontier (DDD)',
                'avg_llm_conf_full_z':                 'LLM Confidence Z (Full)',
                'avg_llm_conf_ctx_z':                  'LLM Confidence Z (Ctx)',
                'stress_period':                       'Stress Period (2015/2018/2020)',
                'tone_x_stress_full':                  'Tone x Stress Period (Full)',
                'tone_x_stress_ctx':                   'Tone x Stress Period (Ctx)',
                'depins_post':                         'Post Deposit Insurance (0/1)',
                'tone_x_depins_full':                  'Tone x Deposit Insurance (Full)',
                'tone_x_depins_ctx':                   'Tone x Deposit Insurance (Ctx)',
                'concern_score_full':                  'Concern Score (Full)',
                'concern_score_ctx':                   'Concern Score (Ctx)',
                'llm_vote_tone_full_lag1':             'Lagged Tone t-1 (Full)',
                'llm_vote_tone_ctx_lag1':              'Lagged Tone t-1 (Ctx)',
                'tone_reversal_full':                  'Tone Reversal t-(t-1) (Full)',
                'tone_reversal_ctx':                   'Tone Reversal t-(t-1) (Ctx)',
                # 跟风新闻检测 (Tetlock 2011, JF)
                'avg_herd_weight':                     'Avg Herd Decay Weight 1/(1+N) (Tetlock 2011)',
                'min_herd_weight':                     'Min Herd Decay Weight (Tetlock 2011)',
                # 跟风衰减加权情感 (Tetlock 2011, JF)
                'llm_vote_tone_hw_full':               'LLM Vote Tone (Herd-Decay Wt, Full)',
                'llm_vote_tone_hw_ctx':                'LLM Vote Tone (Herd-Decay Wt, Ctx)',
                'llm_vote_cont_hw_full':               'LLM Vote Cont (Herd-Decay Wt, Full)',
                'llm_vote_cont_hw_ctx':                'LLM Vote Cont (Herd-Decay Wt, Ctx)',
                # ═══ 银行共现网络: Part A (11) ═══
                'bank_degree_cent':     'Co-mention Degree Centrality (Freeman 1979)',
                'bank_strength_cent':   'Co-mention Strength Centrality (Opsahl 2010)',
                'bank_between_cent':    'Co-mention Betweenness (Battiston 2012)',
                'bank_harmonic_cent':   'Co-mention Harmonic Centrality (Boldi 2014)',
                'bank_eigen_cent':      'Co-mention Eigenvec Centrality (Bonacich 1972)',
                'bank_katz_cent':       'Co-mention Katz Centrality (Acemoglu 2012)',
                'bank_subgraph_cent':   'Co-mention Subgraph Centrality (Estrada 2005)',
                'bank_cfbetween_cent':  'Co-mention Current-Flow Betw (Newman 2005)',
                'bank_clustering':      'Co-mention Clustering Coeff (Watts 1998)',
                'bank_constraint':      'Co-mention Structural Constraint (Burt 1992)',
                'bank_is_hub':          'Co-mention Hub (Top 10% Degree, 0/1)',
                # ═══ 银行共现网络: Part B (7) ═══
                'bank_ego_density':     'Co-mention Ego-Network Density (Burt 1992)',
                'bank_ci':              'Co-mention Struct Hole Richness CI (Burt 1992)',
                'bank_effective_size':  'Co-mention Effective Size (Burt 1992)',
                'bank_closeness_cent':  'Co-mention Closeness Centrality (Freeman 1979)',
                'bank_eccentricity':    'Co-mention Eccentricity (Harary 1969)',
                'bank_avg_nbr_deg':     'Co-mention Avg Neighbor Degree (Barrat 2004)',
                'bank_coreness':        'Co-mention K-Core Number (Seidman 1983)',
                # ═══ 银行共现网络: Part C (4) ═══
                'net_density_yr':       'Annual Co-mention Network Density',
                'net_avg_cluster_yr':   'Annual Avg Clustering Coefficient',
                'net_avg_path_yr':      'Annual Avg Path Length (LCC)',
                'net_degree_gini_yr':   'Annual Degree Distribution Gini',
                # ═══ 银行共现网络: Part D-1 一阶溢出 (3) ═══
                'peer_tone_lag1_full':      '1st-Order Peer Sentiment (Full)',
                'peer_tone_lag1_ctx':       '1st-Order Peer Sentiment (Ctx)',
                'peer_tone_lag1_title':     '1st-Order Peer Sentiment (Title)',
                # ═══ 银行共现网络: Part D-2 二阶溢出 (3) ═══
                'peer_tone_2nd_lag1_full':  '2nd-Order Peer Sentiment Spillover (Full)',
                'peer_tone_2nd_lag1_ctx':   '2nd-Order Peer Sentiment Spillover (Ctx)',
                'peer_tone_2nd_lag1_title': '2nd-Order Peer Sentiment Spillover (Title)',
                # ═══ 地理邻近性: 维度⑨ (Gurun & Butler 2012, JF) ═══
                'homeprov_media_frac':              'Home-Province Media Fraction',
                'homecity_media_frac':              'Home-City Media Fraction',
                'tone_homeprov_media_full':         'Home-Province Media Tone (Full)',
                'tone_nonprov_media_full':          'Non-Province Media Tone (Full)',
                'tone_gap_homeprov_nonprov_full':   'Local Media Slant: Prov (Full)',
                'tone_homecity_media_full':         'Home-City Media Tone (Full)',
                'tone_noncity_media_full':          'Non-City Media Tone (Full)',
                'tone_gap_homecity_noncity_full':   'Local Media Slant: City (Full)',
                'neg_frac_homeprov_full':           'Home-Province Neg Frac (Full)',
                'neg_frac_nonprov_full':            'Non-Province Neg Frac (Full)',
                'neg_frac_homecity_full':           'Home-City Neg Frac (Full)',
                'neg_frac_noncity_full':            'Non-City Neg Frac (Full)',
                # 姜富伟系数 (Jiang et al. 2019)
                'jf_coefficient_full':              'JF Coefficient (Full-text)',
                'jf_coefficient_ctx':               'JF Coefficient (Context)',
                'jf_coefficient_title':             'JF Coefficient (Title)',
                # 媒体质量指标 — 洗稿率 44 种 (Bingler et al. 2022, FRL)
                'washing_ratio':                    'Washing Ratio: LLM Vote (Full)',
                'washing_ratio_ctx':                'Washing Ratio: LLM Vote (Ctx)',
                'neg_sub_ratio_full':               'Neg Substantive Ratio (Full)',
                'neg_sub_ratio_ctx':                'Neg Substantive Ratio (Ctx)',
                'washing_asymmetry_full':           'Washing Asymmetry (Full)',
                'washing_asymmetry_ctx':            'Washing Asymmetry (Ctx)',
                'tone_gap_symb_sub_full':           'Tone Gap: Symb-Sub (Full)',
                'tone_gap_symb_sub_ctx':            'Tone Gap: Symb-Sub (Ctx)',
                'washing_ratio_dict':               'WR: Dict 5-Avg (Full)',
                'washing_ratio_dict_ctx':           'WR: Dict 5-Avg (Ctx)',
                'washing_ratio_bert':               'WR: BERT 5-Avg (Full)',
                'washing_ratio_bert_ctx':           'WR: BERT 5-Avg (Ctx)',
                'washing_ratio_hc':                 'WR: Hi-Conf (Full)',
                'washing_ratio_hc_ctx':             'WR: Hi-Conf (Ctx)',
                # 文本类型与时间取向 (Categorical Dimensions)
                'n_articles_sub':                   'Count: Substantive News',
                'sub_frac':                         'Frac: Substantive News',
                'n_articles_symb':                  'Count: Symbolic News (W&Z 1998)',
                'symb_frac':                        'Frac: Symbolic News',
                'llm_vote_tone_sub_full':           'Avg Tone: Substantive (Full)',
                'llm_vote_tone_sub_ctx':            'Avg Tone: Substantive (Ctx)',
                'llm_vote_tone_symb_full':          'Avg Tone: Symbolic (Full)',
                'llm_vote_tone_symb_ctx':           'Avg Tone: Symbolic (Ctx)',
                'washing_tone_shift_full':          'Symb Tone Shift (Full)',
                'washing_tone_shift_ctx':           'Symb Tone Shift (Ctx)',
                'pos_symb_count_full':              'Pos & Symb Count (Full)',
                'pos_symb_count_ctx':               'Pos & Symb Count (Ctx)',
                'dummy_no_positive_news':           'No Positive News Dummy',
                'low_conf_flag':                    'Low Confidence Flag',
                # 单模型洗稿率 — 双轨 (动态生成)
                **{f'washing_ratio_{m}{s}': f'WR: {m} ({t})'
                   for m in ['gpt54nano', 'gemini31111', 'deepseekv4',
                             'jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018',
                             'finbert_cn', 'fin_sent_zh', 'erlangshen', 'hw2942', 'finbert2']
                   for s, t in [('', 'Full'), ('_ctx', 'Ctx')]},
                # ═══ 停刊稳健性 (Heese et al. 2022, JFE) ═══
                'ceased_media_frac':             'Ceased Media Article Share',
                'n_articles_exc':                'N Articles Excl Ceased Media',
                'exc_tone_full':                 'Tone Excl Ceased (LLM Vote, Full)',
                'exc_tone_ctx':                  'Tone Excl Ceased (LLM Vote, Ctx)',
                'exc_tone_title':                'Tone Excl Ceased (LLM Vote, Title)',
                # ═══ 平衡媒体面板 (Wooldridge 2010, §19.9) ═══
                'bal_w0724_tone_full':           'Balanced W07-24 Tone (Full)',
                'bal_w0724_tone_ctx':            'Balanced W07-24 Tone (Ctx)',
                'bal_w0724_tone_title':          'Balanced W07-24 Tone (Title)',
                'bal_w1024_tone_full':           'Balanced W10-24 Tone (Full)',
                'bal_w1024_tone_ctx':            'Balanced W10-24 Tone (Ctx)',
                'bal_w1024_tone_title':          'Balanced W10-24 Tone (Title)',
                'bal_w1124_tone_full':           'Balanced W11-24 Tone (Full)',
                'bal_w1124_tone_ctx':            'Balanced W11-24 Tone (Ctx)',
                'bal_w1124_tone_title':          'Balanced W11-24 Tone (Title)',
                'n_media_bal_w0724':             'N Media Balanced W07-24',
                'n_media_bal_w1024':             'N Media Balanced W10-24',
                'n_media_bal_w1124':             'N Media Balanced W11-24',
                # === 四梯度距离缓冲 (Gurun & Butler 2012) ===
                'prox_50km_n_media':             'N Media Within 50km',
                'prox_50km_n_articles':          'N Articles Within 50km',
                'prox_50km_frac':                'Frac Articles Within 50km',
                'prox_50km_tone_full':           'Avg Tone Within 50km (Full)',
                'prox_50km_pos_frac':            'Pos Frac Within 50km',
                'prox_50km_neg_frac':            'Neg Frac Within 50km',
                'prox_50km_is_local':            'Has Local Media 50km (0/1)',
                'prox_100km_n_media':            'N Media Within 100km',
                'prox_100km_n_articles':         'N Articles Within 100km',
                'prox_100km_frac':               'Frac Articles Within 100km',
                'prox_100km_tone_full':          'Avg Tone Within 100km (Full)',
                'prox_100km_pos_frac':           'Pos Frac Within 100km',
                'prox_100km_neg_frac':           'Neg Frac Within 100km',
                'prox_100km_is_local':           'Has Local Media 100km (0/1)',
                'prox_150km_n_media':            'N Media Within 150km',
                'prox_150km_n_articles':         'N Articles Within 150km',
                'prox_150km_frac':               'Frac Articles Within 150km',
                'prox_150km_tone_full':          'Avg Tone Within 150km (Full)',
                'prox_150km_pos_frac':           'Pos Frac Within 150km',
                'prox_150km_neg_frac':           'Neg Frac Within 150km',
                'prox_150km_is_local':           'Has Local Media 150km (0/1)',
                'prox_200km_n_media':            'N Media Within 200km',
                'prox_200km_n_articles':         'N Articles Within 200km',
                'prox_200km_frac':               'Frac Articles Within 200km',
                'prox_200km_tone_full':          'Avg Tone Within 200km (Full)',
                'prox_200km_pos_frac':           'Pos Frac Within 200km',
                'prox_200km_neg_frac':           'Neg Frac Within 200km',
                'prox_200km_is_local':           'Has Local Media 200km (0/1)',
                # === 区域 AI 模仿渗透率 (Leary & Roberts 2014) ===
                'ai_reg_province':               'AI Imitation Rate (Province)',
                'ai_reg_city':                   'AI Imitation Rate (City)',
                'ai_reg_50km':                   'AI Imitation Rate (50km)',
                'ai_reg_100km':                  'AI Imitation Rate (100km)',
                'ai_reg_150km':                  'AI Imitation Rate (150km)',
                'ai_reg_200km':                  'AI Imitation Rate (200km)',
                # === 战略差异度 (Guzman & Li 2023; Hoberg & Phillips 2016) ===
                'strat_diff_n3':       'Strat Diff N=3 (TF-IDF char)',
                'strat_diff_n4':       'Strat Diff N=4 (TF-IDF char)',
                'strat_diff_n5':       'Strat Diff N=5 (TF-IDF char)',
                'strat_diff_n6':       'Strat Diff N=6 (TF-IDF char)',
                'strat_diff_n7':       'Strat Diff N=7 (TF-IDF char)',
                'strat_diff_n3_w':     'Strat Diff N=3 (TF-IDF jieba)',
                'strat_diff_n4_w':     'Strat Diff N=4 (TF-IDF jieba)',
                'strat_diff_n5_w':     'Strat Diff N=5 (TF-IDF jieba)',
                'strat_diff_n6_w':     'Strat Diff N=6 (TF-IDF jieba)',
                'strat_diff_n7_w':     'Strat Diff N=7 (TF-IDF jieba)',
                'strat_sim_max':       'Max Peer Similarity (TF-IDF char)',
                'strat_sim_max_w':     'Max Peer Similarity (TF-IDF jieba)',
                'strat_fluidity':      'Product Mkt Fluidity (TF-IDF char)',
                'strat_fluidity_w':    'Product Mkt Fluidity (TF-IDF jieba)',
                'strat_diff_n5_lda':   'Strat Diff N=5 (LDA+JSD)',
                'strat_sim_max_lda':   'Max Peer Similarity (LDA+JSD)',
                'strat_diff_n5_emb':   'Strat Diff N=5 (Embedding)',
                'strat_sim_max_emb':   'Max Peer Similarity (Embedding)',
                # === N-最近邻 Ctx 轨 (Guzman & Li 2023, Ctx window) ===
                'strat_diff_n5_ctx':       'Strat Diff N=5 TF-IDF char (Ctx)',
                'strat_diff_n5_w_ctx':     'Strat Diff N=5 TF-IDF jieba (Ctx)',
                'strat_sim_max_ctx':       'Max Peer Similarity char (Ctx)',
                'strat_sim_max_w_ctx':     'Max Peer Similarity jieba (Ctx)',
                'strat_diff_n5_lda_ctx':   'Strat Diff N=5 LDA+JSD (Ctx)',
                'strat_sim_max_lda_ctx':   'Max Peer Similarity LDA (Ctx)',
                'strat_diff_n5_emb_ctx':   'Strat Diff N=5 Embedding (Ctx)',
                'strat_sim_max_emb_ctx':   'Max Peer Similarity Emb (Ctx)',
                # === 全行业向量法 Full (谢佳松 2025; Industry Centroid) ===
                'centroid_diff_tfidf_c':     'Centroid Dist TF-IDF char (Full)',
                'centroid_diff_tfidf_w':     'Centroid Dist TF-IDF jieba (Full)',
                'centroid_diff_lda':         'Centroid Dist LDA theta (Full)',
                'centroid_diff_emb':         'Centroid Dist Embedding (Full)',
                # === 全行业向量法 Ctx (谢佳松 2025; Industry Centroid) ===
                'centroid_diff_tfidf_c_ctx': 'Centroid Dist TF-IDF char (Ctx)',
                'centroid_diff_tfidf_w_ctx': 'Centroid Dist TF-IDF jieba (Ctx)',
                'centroid_diff_lda_ctx':     'Centroid Dist LDA theta (Ctx)',
                'centroid_diff_emb_ctx':     'Centroid Dist Embedding (Ctx)',
                # === 相邻期文本连贯性 (欧阳志刚 & 胡雯华 2024; Temporal Text Coherence) ===
                'coh_tfidf_c_full':  'Text Coherence t/(t-1) TF-IDF char (Full)',
                'coh_tfidf_c_ctx':   'Text Coherence t/(t-1) TF-IDF char (Ctx)',
                'coh_tfidf_w_full':  'Text Coherence t/(t-1) TF-IDF jieba (Full)',
                'coh_tfidf_w_ctx':   'Text Coherence t/(t-1) TF-IDF jieba (Ctx)',
                'coh_lda_full':      'Text Coherence t/(t-1) LDA+JSD (Full)',
                'coh_lda_ctx':       'Text Coherence t/(t-1) LDA+JSD (Ctx)',
                'coh_emb_full':      'Text Coherence t/(t-1) Embedding (Full)',
                'coh_emb_ctx':       'Text Coherence t/(t-1) Embedding (Ctx)',
                # === 认知邻近度 (Boschma 2005) ===
                'bank_cogn_mean':                'Cognitive Proximity (TF-IDF)',
                # === 信息经纪网络 (Han et al. 2024) ===
                'brokerage_eigen_cent':          'Brokerage Eigenvector Cent',
                'industry_neg_shock':            'Industry Neg Shock (LOO)',
                'brokerage_fire_sale':           'Brokerage x Neg Shock',
                # === 同行金融科技溢出 (Berger et al. 2022) ===
                'peer_fintech_exposure_lag1':    'Peer Fintech Exposure (L1)',
                # === Embedding 同业网络 (Hoberg & Phillips 2016) ===
                'emb_peer_tone_lag1_full':      'Emb Peer Tone L1 (Full)',
                'bank_emb_sim_mean':            'Bank Embedding Sim Mean',
                # === LLM-Peer 竞争网络 IV (Cao et al. 2025) ===
                # 主回归变量 (cutoff=0.80 TNIC 标准, 无后缀)
                'llm_peer_tone_iv_full':        'LLM-Peer Tone IV (Full)',
                'llm_peer_coverage_iv':         'LLM-Peer Coverage IV',
                'llm_peer_count':               'LLM-Peer Count',
                'peer_compete_idx':             'Peer Competition Index (0.80)',
                # 多阈值敏感性变体 (cutoff=0.70/0.75/0.80/0.85/0.90)
                **{f'llm_peer_tone_iv_full_{c}': f'LLM-Peer Tone IV (Full, c={c/100:.2f})'
                   for c in [70, 75, 80, 85, 90]},
                **{f'llm_peer_coverage_iv_{c}': f'LLM-Peer Coverage IV (c={c/100:.2f})'
                   for c in [70, 75, 80, 85, 90]},
                **{f'llm_peer_count_{c}': f'LLM-Peer Count (c={c/100:.2f})'
                   for c in [70, 75, 80, 85, 90]},
                **{f'peer_compete_idx_{c}': f'Peer Compete Idx (c={c/100:.2f})'
                   for c in [70, 75, 80, 85, 90]},
                # ═══ 治理约束型合约 (Zhou et al., 2026, JBR §2.1; Core et al. 2003) ═══
                'GOV_equity_ratio':             'Equity Comp / Total Comp Ratio',
                'GOV_cash_ratio':               'Cash Comp / Total Comp Ratio',
                'GOV_top3_pay_gap':             'ln(Top3 Exec Pay / Avg Emp Pay)',
                'GOV_esg_kpi':                  'ESG-KPI in Exec Comp (0/1)',
                'GOV_board_indep':              'Independent Director Ratio',
                'GOV_dual_chair':               'CEO-Chair Duality (0/1)',
                'GOV_comp_committee':           'Compensation Committee (0/1)',
                'GOV_ceo_tenure':               'CEO Tenure (Years)',
                # ═══ 情感分歧 (姜富伟 2024; Antweiler & Frank 2004) ═══
                **{f'disag{s}': f'Disagreement: Dict Avg ({t})'
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                **{f'disag_{d}{s}': f'Disagreement: {d} ({t})'
                   for d in ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                **{f'disag_llm{s}': f'Disagreement: LLM Vote ({t})'
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                **{f'disag_{m}{s}': f'Disagreement: {m} ({t})'
                   for m in ['gpt54nano', 'gemini31111', 'deepseekv4']
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                **{f'disag_bert{s}': f'Disagreement: BERT Avg ({t})'
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                **{f'disag_{b}{s}': f'Disagreement: {b} ({t})'
                   for b in ['finbert_cn', 'fin_sent_zh', 'erlangshen', 'hw2942', 'finbert2']
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                # ═══ 对数降噪情感 (Angelico et al. 2022) ═══
                **{f'log_sent{s}': f'Log Sentiment ({t})'
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                # ═══ 算法迎合度 (Cao et al. 2023; Huang et al. 2023) ═══
                **{f'algo_cater{s}': f'Algo Catering: Dict-LLM ({t})'
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                **{f'algo_cater_b{s}': f'Algo Catering: Dict-BERT ({t})'
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                **{f'{d}_cater{s}': f'Catering: {d}-LLM ({t})'
                   for d in ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                **{f'{d}_cater_b{s}': f'Catering: {d}-BERT ({t})'
                   for d in ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                **{f'cater_{m}{s}': f'Catering: Dict-{m} ({t})'
                   for m in ['gpt54nano', 'gemini31111', 'deepseekv4']
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                **{f'cater_{b}{s}': f'Catering: Dict-{b} ({t})'
                   for b in ['finbert_cn', 'fin_sent_zh', 'erlangshen', 'hw2942', 'finbert2']
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                # ═══ 披露密度 (Abraham et al. 2024) ═══
                'avg_ft_word_ratio':     'Avg Fintech Word Ratio',
                'avg_ft_word_ratio_std': 'Std Fintech Word Ratio',
                # ═══ 技术重度 (Li et al. 2021, RFS; 14_fintech_intensity.py) ═══
                'avg_ft_intensity':     'Avg FinTech Intensity Score (TF-IDF)',
                'avg_ft_intensity_std': 'Std FinTech Intensity Score (TF-IDF)',
                # ═══ 同业竞争 (Cao et al. 2025) ═══
                # 注: 'peer_compete_idx' 已在 line 857 声明为 'Peer Competition Index (0.80)'
                # (含 cutoff=0.80 的明确学术语义); 此处不再重复以避免 dict-key silent
                # override (Plan-r3 P0-2 修复, ruff F601).
                # ═══ 前置中间变量: neg_count ═══
                **{f'{m}_neg_count{s}': f'Neg Count: {m} ({t})'
                   for m in ['gpt54nano', 'gemini31111', 'deepseekv4']
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                **{f'{d}_neg_count{s}': f'Neg Count: {d} ({t})'
                   for d in ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                **{f'{b}_neg_count{s}': f'Neg Count: {b} ({t})'
                   for b in ['finbert_cn', 'fin_sent_zh', 'erlangshen', 'hw2942', 'finbert2']
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                # ═══ 前置中间变量: 单词典 pos/neg ratio ═══
                **{f'avg_{d}_pos_ratio{s}': f'Avg Pos Ratio: {d} ({t})'
                   for d in ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                **{f'avg_{d}_neg_ratio{s}': f'Avg Neg Ratio: {d} ({t})'
                   for d in ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                # ═══ Logit-to-Score 概率映射情感 (Törnberg 2024 / Shapiro 2022) ═══
                **{f'avg_llm_prob_score{s}': f'Avg Prob Score ({t})'
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx'), ('_title', 'Title')]},
                **{f'avg_llm_prob_score_std{s}': f'Std Prob Score ({t})'
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx'), ('_title', 'Title')]},
                **{f'llm_prob_score_sum{s}': f'Sum Prob Score ({t})'
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx'), ('_title', 'Title')]},
                **{f'llm_vote_tone_vw_prob{s}': f'VW Prob Tone ({t})'
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx'), ('_title', 'Title')]},
                **{f'llm_vote_tone_mw_prob{s}': f'MW Prob Tone ({t})'
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx'), ('_title', 'Title')]},
                **{f'llm_vote_tone_hw_prob{s}': f'HW Prob Tone ({t})'
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx'), ('_title', 'Title')]},
                'prob_gap_title_full': 'Prob Score Gap: Title - Full',
                # === 权威政策战略响应度 (Stage 26; Hassan et al. 2019) ===
                # 注: 8 个 'auth_sim_*' key 已在 line 573-580 声明 (字符串完全相同),
                # 此处不再重复以保持 dict-key 唯一性 (Plan-r3 P0-2 修复, ruff F601).
                # ═══ 经营效益情感态度投影 (Stage 27; Jha, Liu & Manela 2026, RFS §1.3.2) ═══
                'benefit_mean_full':      'Benefit-Operations Attitude Mean (Full)',
                'benefit_mean_ctx':       'Benefit-Operations Attitude Mean (Ctx)',
                'benefit_std_full':       'Benefit-Operations Attitude Std (Full)',
                'benefit_std_ctx':        'Benefit-Operations Attitude Std (Ctx)',
                'benefit_pos_frac_full':  'Benefit-Ops Positive Frac (Full)',
                'benefit_pos_frac_ctx':   'Benefit-Ops Positive Frac (Ctx)',
                'benefit_neg_frac_full':  'Benefit-Ops Negative Frac (Full)',
                'benefit_neg_frac_ctx':   'Benefit-Ops Negative Frac (Ctx)',
                # === Article-level Policy Alignment (Stage 15; Distel et al. 2026) ===
                # Continuous aggregation (main regression)
                'article_sim_mean':       'Avg Article-Policy Cosine Sim',
                'article_sim_std':        'Std Article-Policy Cosine Sim',
                'fintech_intensity_mean': 'Avg FinTech Intensity Score',
                # Quadrant discrete classification (mechanism / robustness)
                # Track A (kw) x P={25,50,75}
                'token_adopt_kw_p25':     'Token Adoption (KW, P25)',
                'hidden_adopt_kw_p25':    'Hidden Adoption (KW, P25)',
                'subst_adopt_kw_p25':     'Substantive Adoption (KW, P25)',
                'token_adopt_kw_p50':     'Token Adoption (KW, P50)',
                'hidden_adopt_kw_p50':    'Hidden Adoption (KW, P50)',
                'subst_adopt_kw_p50':     'Substantive Adoption (KW, P50)',
                'token_adopt_kw_p75':     'Token Adoption (KW, P75)',
                'hidden_adopt_kw_p75':    'Hidden Adoption (KW, P75)',
                'subst_adopt_kw_p75':     'Substantive Adoption (KW, P75)',
                # Track B (int) x P={25,50,75}
                'token_adopt_int_p25':    'Token Adoption (INT, P25)',
                'hidden_adopt_int_p25':   'Hidden Adoption (INT, P25)',
                'subst_adopt_int_p25':    'Substantive Adoption (INT, P25)',
                'token_adopt_int_p50':    'Token Adoption (INT, P50)',
                'hidden_adopt_int_p50':   'Hidden Adoption (INT, P50)',
                'subst_adopt_int_p50':    'Substantive Adoption (INT, P50)',
                'token_adopt_int_p75':    'Token Adoption (INT, P75)',
                'hidden_adopt_int_p75':   'Hidden Adoption (INT, P75)',
                'subst_adopt_int_p75':    'Substantive Adoption (INT, P75)',
                # v3.5.1 A1 Lexical Clarity (LM 2011 JF; You 2018 hhx055) — 真双轨独立扫描
                # 与 stata_export.py::HEURISTIC_LABELS 同步 (test_stata_export_v3_5_1 验证一致性).
                'mean_clarity_score_full':   'Mean Clarity Score from indep Full-text scan (LM 2011 JF; You 2018)',
                'mean_clarity_score_ctx':    'Mean Clarity Score from indep Ctx-text scan (LM 2011 JF; You 2018)',
                'mean_frac_definite_full':   'Mean Frac Definite from indep Full scan (You 2018 Panel C 388 words)',
                'mean_frac_definite_ctx':    'Mean Frac Definite from indep Ctx scan (You 2018 Panel C 388 words)',
                'frac_amb_articles_full':    'Frac Articles Ambiguous Full (>=D0 median, You 2018 Panel D)',
                'frac_amb_articles_ctx':     'Frac Articles Ambiguous Ctx (>=D0 median, You 2018 Panel D)',
                # v3.5.1 A3 Numerical Intensity (Hales 2011 CAR) — 真双轨
                'mean_num_intensity_full':   'Mean Numerical Intensity Full (Hales 2011 CAR, dual-track)',
                'mean_num_intensity_ctx':    'Mean Numerical Intensity Ctx (Hales 2011 CAR, dual-track)',
            }
            # 仅保留面板中实际存在的列
            labels = {k: v for k, v in STATA_LABELS.items()
                      if k in panel_stata.columns}
            panel_stata.to_stata(dta_path, write_index=False, version=118,
                                 variable_labels=labels)
            logger.info(f"  已导出 Stata 文件: {dta_path}")
        except Exception as e:
            # B-2 修复 (v7 外副作用): 经典 swallow-errors 反模式根除.
            # 旧代码仅 logger.warning, 让 stage 45 退出码假装 0, 但 .dta 实际
            # 没写出, 与 .parquet 形成"语义错位"灾难 (现实中触发: 5月1日的
            # 旧 .dta 与 5月5日的新 .parquet 同时存在). 改为 raise 让上层
            # orchestrator 立即停止, 与 N2 的 REQUIRED_PANEL_COLUMNS 同精神.
            # B-3 已在 try 之前先删旧 .dta, 故 raise 后 .dta 不存在 (干净失败,
            # 不会留下语义错位的半成品).
            raise RuntimeError(
                f"[export_panel] Stata 导出失败: {e}; "
                f"已删除旧 .dta 避免与新 .parquet 错位; "
                f"请检查 panel 中是否有 to_stata 不兼容的 dtype/数据 "
                f"(如全 None object 列), B-1 防御性转换已就位但仍未覆盖该情形."
            ) from e

    # 文章-银行级数据
    article_filename = FILENAMES.get('output_40_article_bank', '40_article_bank_level.parquet')
    article_path = os.path.join(OUTPUT_DIR, article_filename)
    # 血缘 (audit-fixes 2026-05-29, 10 轮审核 r4 修正): 文章级 df_exploded 仅派生自
    # stage 24 (article×bank 级 herd_decay 输出); stage 15/30 是 PANEL 级 (bank-year)
    # merge, 不进 article-level 输出 (实测 40_article_bank_level 无 policy_cosine/t2v
    # 列)。故此处只记 24, 避免过度归因 (panel 级 40_panel_yearly 才记 24+15+30)。
    input_file = os.path.join(CONFIG['paths']['output_dir'],
                              CONFIG['filenames']['output_24_herd_decay'])
    save_dataset(df_exploded, article_path, logger,
                stage_name="45_panel_export_main",
                config=CONFIG,
                input_files=[input_file])
