"""news_process.pipeline.panel.export — 面板诊断 + 多格式导出。

Phase 2b 从 pipeline/panel/runner.py 抽离, 落实单一职责拆分:
  - log_diagnostics(panel, df_exploded)  → 面板诊断统计
                                                (纯只读, 不变异 panel schema;
                                                fix omni-g-panel-export-05)
  - export_panel(panel, df_exploded)     → Parquet + Stata .dta 导出, 含
                                                Stata 32 字符列名纪律 +
                                                STATA_LABELS 标签字典
                                                (含 low_conf_flag 无条件物化 +
                                                变量标签启发式兜底).

导入本模块无副作用; 调用方需显式调用上述两个函数。
runner.py re-export 这两个函数以保持向后兼容。
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

from news_process.core.config import herd_sensitivity_grid
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
    和面板平衡性诊断 (G-07)。

    fix(omni-g-panel-export-05, 2026-06-11): 本函数为纯只读 (read-only) — 不再
    副作用式创建 low_conf_flag 列 (原嵌在 `if len(valid_conf) > 0` 分支内, 致
    panel schema 随数据内容漂移, 且隐式依赖 runner 先 log_diagnostics 后
    export_panel 的调用顺序契约); 该列物化移至 export_panel 无条件执行。
    """
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

            # ── G-20: 低置信度分类诊断 (read-only) ──
            # fix(omni-g-panel-export-05, 2026-06-11): 不再在诊断函数内变异
            # panel (low_conf_flag 列改由 export_panel 经
            # _materialize_low_conf_flag 无条件物化, schema 稳定);
            # 此处仅本地计算统计量供日志输出。
            _low_mask = panel['avg_category_confidence'] < 0.5
            low_n = int(_low_mask.sum())
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
# 8b. 导出前置 helpers (fix omni-g-panel-export-05/-06, 2026-06-11)
# ============================================================================

def _materialize_low_conf_flag(panel: pd.DataFrame) -> pd.DataFrame:
    """无条件物化 G-20 低置信度诊断列 low_conf_flag (schema 稳定)。

    fix(omni-g-panel-export-05, 2026-06-11): 原实现把列创建埋在 log_diagnostics
    的 `if len(valid_conf) > 0` 分支 (数据依赖的 schema 漂移 + 诊断函数副作用):
    avg_category_confidence 全 NaN 时列缺失 (盘上试跑样本即如此), 全量置信度
    就位后列突现 → panel/.dta 列集随数据内容而非代码漂移。现改为: 只要
    avg_category_confidence 列存在即创建 (全 NaN → 全 0, 与原 `NaN < 0.5 ==
    False → 0` 语义逐位一致), 列存在性仅取决于上游代码路径。
    """
    if 'avg_category_confidence' in panel.columns:
        panel['low_conf_flag'] = (
            panel['avg_category_confidence'] < 0.5
        ).astype(int)
    return panel


def _apply_label_fallback(labels: dict, columns) -> dict:
    """40-path .dta 变量标签覆盖率兜底 (返回新 dict, 不原地修改入参)。

    fix(omni-g-panel-export-06, 2026-06-11): STATA_LABELS 仅命中部分列 (实测
    992/1658 列在 40_panel_yearly.dta 中无任何 variable label, 含主回归 DV
    llm_vote_tone_full/_ctx 与主键 target_bank/year), 与 export_panel 自述
    "确保导入 Stata 后能直接跑回归" 不符 — stage 46 的 46_*.dta 有
    codebook+启发式+列名三级兜底而 40-path 没有。本函数复用 stage 46 的
    build_variable_labels (codebook 优先 → HEURISTIC_LABELS → 列名兜底)
    补齐未命中列, 保证 100% 标签覆盖。

    防御: pandas to_stata 要求 variable label ≤80 字符且 latin-1 可编码 —
    兜底标签若含非 latin-1 字符 (如中文 codebook label) 则退回列名本身
    (此时列名已被 sanitize_stata_columns asciify, 安全)。
    """
    out = dict(labels)
    missing = [c for c in columns if c not in out]
    if not missing:
        return out
    # 延迟 import: 仅 .dta 导出路径需要, 且避免模块级 import 链膨胀
    from news_process.pipeline.panel.stata_export import build_variable_labels
    fb = build_variable_labels(pd.DataFrame(columns=missing))
    for c in missing:
        lab = str(fb.get(c, c)) or str(c)
        try:
            lab.encode('latin-1')
        except UnicodeEncodeError:
            lab = str(c)  # 列名已 ASCII 化, 必然 latin-1 可编码
        out[c] = lab[:80]
    return out


# ============================================================================
# 9. 导出
# ============================================================================

def export_panel(panel: pd.DataFrame, df_exploded: pd.DataFrame):
    """多格式导出面板数据。

    行为披露 (fix omni-g-panel-export-05/-06, 2026-06-11): 导出前无条件物化
    G-20 诊断列 low_conf_flag (取代 log_diagnostics 的数据依赖式副作用创建);
    .dta 变量标签对 STATA_LABELS 未命中列启用 stage-46 启发式兜底, 保证
    100% 标签覆盖 (原实测 59.8% 列无标签, 含主回归 DV llm_vote_tone_full/_ctx)。

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
    # 校验集对应 Step 4 硬化保证存在的 4 个上游契约 (2026-05-29 双模型重构后,
    # 原独立 stage 30 已退役, _t2v 契约列改由 stage 15/25 主流程内联双模型产出):
    #   stage 15 (政策对齐)  → 7h-token 四象限分类列 + policy_cosine_sim_t2v_* (runner 聚合)
    #   stage 25 (战略差异)  → strat_diff_t2v_* (内联 text2vec twin)
    #   stage 25/26/27 (硬import) → strat_diff_full / auth_sim_* / benefit_sim_*
    # 使用 raise 而非 assert (assert 在 python -O 优化模式下会被剥离).
    REQUIRED_PANEL_COLUMNS = [
        # bank-year 主键
        'target_bank', 'year',
        # 双轨稳健性 (4 列) — 2026-05-29 双模型重构后由 stage 15/25 内联双模型产出
        # (原 stage 30 已退役): strat_diff_t2v_* ← stage 25; policy_cosine_sim_t2v_* ← stage 15 聚合
        'strat_diff_t2v_full', 'strat_diff_t2v_ctx',
        'policy_cosine_sim_t2v_full', 'policy_cosine_sim_t2v_ctx',
    ]
    _missing = [c for c in REQUIRED_PANEL_COLUMNS if c not in panel.columns]
    if _missing:
        raise RuntimeError(
            f"[export_panel] panel 缺失必填列 {_missing}; "
            f"现有 {len(panel.columns)} 列前 30 个: {list(panel.columns)[:30]}; "
            f"拒绝写出避免 .parquet/.dta 语义错位。"
            f" 请检查上游 stage 15 (policy_cosine_sim_t2v) + stage 25 (strat_diff_t2v) "
            f"内联双模型输出是否存在 (stage 30 已于 2026-05-29 退役)."
        )
    logger.info(
        f"[export_panel] REQUIRED_PANEL_COLUMNS 校验通过 "
        f"({len(REQUIRED_PANEL_COLUMNS)} 列 / panel 共 {len(panel.columns)} 列, "
        f"{len(panel)} 行)"
    )

    # fix(omni-g-panel-export-05, 2026-06-11): G-20 low_conf_flag 在导出前
    # 无条件物化 (原由 log_diagnostics 数据依赖式副作用创建, 见 helper docstring)
    panel = _materialize_low_conf_flag(panel)

    logger.info("=" * 60)
    logger.info("步骤 9: 多格式导出")
    logger.info("=" * 60)

    # 年度面板 Parquet
    panel_filename = FILENAMES.get('output_40_panel_yearly', '40_panel_yearly.parquet')
    panel_path = os.path.join(OUTPUT_DIR, panel_filename)
    # 血缘修复 (audit-fixes 2026-05-29): stage 45 是 fan-in, runner 硬读
    # 24_herd_decay (主) + 15_article_alignment (RuntimeError if absent, runner.py:1077).
    # 记全部硬上游闭包, 否则 verify_data_integrity 对 15 的篡改/陈旧检测不到
    # (与 stage 14 fintech_intensity 记双输入的受测约定一致).
    # 2026-05-29 双模型重构: 原 stage 30 (30_text2vec_indicators) 已退役 — 其 t2v 列改由
    # stage 15/25 内联双模型产出, 不再是独立上游 parquet, 故从血缘闭包中移除。
    # 缺失文件由 data_versioning 的 exists 守卫优雅跳过.
    _od = CONFIG['paths']['output_dir']
    _fn = CONFIG['filenames']
    input_files = [
        os.path.join(_od, _fn['output_24_herd_decay']),
        os.path.join(_od, _fn.get('output_15_article_alignment', '15_article_alignment.parquet')),
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
                # 总量孪生 (互为稳健性, 2026-06-13): ln(1+fintech 覆盖篇数), extensive 规模
                'ft_vol_yr':     'Fintech Coverage Volume (Year, ln)',
                'ft_vol_prov':   'Fintech Coverage Volume (Province, Exp-Wt, ln)',
                'ft_vol_city':   'Fintech Coverage Volume (City, Exp-Wt, ln)',
                # P2 attention 处理变量 (W2 2026-06-05; Hassan 2019 QJE; 双轨)
                'attention_index_full':             'Fintech Attention Index (full)',
                'attention_index_ctx':              'Fintech Attention Index (ctx)',
                'attention_pct_full':               'Fintech Attention Share',
                'attention_disp_full':              'Fintech Attention Dispersion (outlet HHI)',
                'attention_intensity_density_full': 'Attention Intensity Density (full)',
                'attention_intensity_density_ctx':  'Attention Intensity Density (ctx)',
                'attention_intensity_sd_full':      'Attention Intensity SD (full)',
                'attention_intensity_sd_ctx':       'Attention Intensity SD (ctx)',
                'attention_gap_full_ctx':           'Attention Attribution Gap (full-ctx)',
                'attention_attr_share':             'Attention Attribution Purity',
                'n_fintech_articles':               'N fintech articles (bank-year)',
                'n_outlets':                        'N distinct outlets (fintech)',
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
                # 规则消融稳健性: 仅否定 (rule-ablation negation-only, 2026-06-13)
                # 三点 ablation 谱: avg_msent(零规则) → *_negonly(仅否定) → 全规则 dict_avg_tone
                'dict_avg_negonly_tone_full':     'Dict Avg Tone (Negation-Only, Full)',
                'dict_avg_negonly_tone_ctx':      'Dict Avg Tone (Negation-Only, Ctx)',
                'avg_msent_negonly_full':         'MSENT (Negation-Only Count) EW Mean (Full)',
                'avg_msent_negonly_ctx':          'MSENT (Negation-Only Count) EW Mean (Ctx)',
                # 文章长度: avg_article_length=字符口径 ln(1+avg_chars) (2026-06-05 单位勘误,
                # 原标 avg_words 系误标, 底层 doc_length=字符数); ln_word_count=词口径 (Li 2008)
                'avg_article_length':             'Article Length ln(1+avg_chars)',
                # ── 文本测度缺口补全 (2026-06-05, 批 #1–#15) Stata 标签 ──
                'mean_num_intensity_word_full':  'Num Intensity per-Word (Full)',
                'mean_num_intensity_word_ctx':   'Num Intensity per-Word (Ctx)',
                'avg_rare_word_full':            'Rare-Word Ratio (Full)',
                'avg_rare_word_ctx':             'Rare-Word Ratio (Ctx)',
                'avg_hard_char_full':            'Hard-Char Ratio (Full)',
                'avg_hard_char_ctx':             'Hard-Char Ratio (Ctx)',
                'avg_nominalization_full':       'Nominalization Ratio (Full)',
                'avg_nominalization_ctx':        'Nominalization Ratio (Ctx)',
                'avg_function_word_full':        'Function-Word Ratio LIWC-Analytic (Full)',
                'avg_function_word_ctx':         'Function-Word Ratio LIWC-Analytic (Ctx)',
                'avg_specificity_full':          'Specificity Hard-Info Density (Full)',
                'avg_specificity_ctx':           'Specificity Hard-Info Density (Ctx)',
                'avg_within_doc_redund_full':    'Within-Doc Redundancy (Full)',
                'avg_within_doc_redund_ctx':     'Within-Doc Redundancy (Ctx)',
                # 汉字口径冗余孪生 (剔数字/标点/拉丁; 与上方字符口径双口径, hanzi-char-dual 2026-06-13)
                'avg_within_doc_redund_han_full': 'Within-Doc Redundancy Han-char (Full)',
                'avg_within_doc_redund_han_ctx':  'Within-Doc Redundancy Han-char (Ctx)',
                'avg_adversative_full':          'Adversative-Conjunction Ratio (Full)',
                'avg_adversative_ctx':           'Adversative-Conjunction Ratio (Ctx)',
                'avg_word_count_full':           'Avg Word Count (Full)',
                'avg_word_count_ctx':            'Avg Word Count (Ctx)',
                'ln_word_count_full':            'Article Length ln(1+avg_words) (Full)',
                'ln_word_count_ctx':             'Article Length ln(1+avg_words) (Ctx)',
                # 汉字口径文章长度 (第三口径; 剔数字/标点/拉丁, hanzi-char-dual 2026-06-13)
                'avg_han_count_full':            'Avg Han-Char Count (Full)',
                'avg_han_count_ctx':             'Avg Han-Char Count (Ctx)',
                'ln_han_count_full':             'Article Length ln(1+avg_hanchars) (Full)',
                'ln_han_count_ctx':              'Article Length ln(1+avg_hanchars) (Ctx)',
                'frac_front_page':               'Front-Page Coverage Frac',
                'frac_front_section':            'Front-Section Coverage Frac',
                'avg_page_rank':                 'Avg Page Prominence (lower=front)',
                'staff_written_frac':            'Staff-Written Byline Frac',
                'wire_frac':                     'Wire-Service Frac',
                'frac_target_in_lead':           'Target-in-Lead Frac',
                'tone_volatility_full':          'Tone Volatility 3y-roll SD (Full)',
                'tone_volatility_ctx':           'Tone Volatility 3y-roll SD (Ctx)',
                'coverage_active_days':          'Active Coverage Days per Year',
                'coverage_continuity':           'Coverage Continuity active/span',
                'lazy_jaccard_full':             'YoY Text Change Jaccard (Full)',
                'lazy_jaccard_ctx':              'YoY Text Change Jaccard (Ctx)',
                'lazy_overlap_full':             'YoY Text Change Word-Overlap (Full)',
                'lazy_overlap_ctx':              'YoY Text Change Word-Overlap (Ctx)',
                'lazy_minedit_full':             'YoY Text Change Norm-Leven (Full)',
                'lazy_minedit_ctx':              'YoY Text Change Norm-Leven (Ctx)',
                'abnormal_tone_full':            'Abnormal Tone resid-vs-fundmtl (Full)',
                'abnormal_tone_ctx':             'Abnormal Tone resid-vs-fundmtl (Ctx)',
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
                # G-08 多情感度量 LOO IV 扩展 (Hansen J 过度识别; geography.py)
                # fix(omni-g-panel-export-04, 2026-06-11): 产生端列名压缩为
                # dict_tone 词干 (原 prov/city_leave1out_dict_avg_tone_full 33
                # 字符超 Stata 32 上限, 被 sanitize 单侧缩写致 .dta 内 full/ctx
                # 词干不对称); 此处按新对称列名补标签。
                'prov_leave1out_dict_tone_full':    'Province Leave-1-Out Dict Tone (Full)',
                'prov_leave1out_dict_tone_ctx':     'Province Leave-1-Out Dict Tone (Ctx)',
                'city_leave1out_dict_tone_full':    'City Leave-1-Out Dict Tone (Full)',
                'city_leave1out_dict_tone_ctx':     'City Leave-1-Out Dict Tone (Ctx)',
                'prov_leave1out_bert_avg_pos_full': 'Province Leave-1-Out BERT Pos (Full)',
                'prov_leave1out_bert_avg_pos_ctx':  'Province Leave-1-Out BERT Pos (Ctx)',
                'city_leave1out_bert_avg_pos_full': 'City Leave-1-Out BERT Pos (Full)',
                'city_leave1out_bert_avg_pos_ctx':  'City Leave-1-Out BERT Pos (Ctx)',
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
                # Bartik IV — 金融科技类型维度 (稳健性 2; v3.2.0 M3 P4 双套独立:
                # lf=innovation_locus_full 基期份额 / lc=innovation_locus_ctx)
                # fix(omni-g-panel-export-02, 2026-06-11): v3.2 起实际列为 lf/lc
                # 两套 8 列 (runner.py compute_bartik_iv_fintech 调用), 原
                # bartik_fintech_iv_*/share_* 陈旧键已不存在 → 活跃列曾无标签。
                'bartik_fintech_lf_iv_full':           'Bartik IV: Fintech-Cat (Locus=Full, Full)',
                'bartik_fintech_lf_iv_ctx':            'Bartik IV: Fintech-Cat (Locus=Full, Ctx)',
                'bartik_fintech_lf_share_tech':        'Bartik Share: Technology (Locus=Full)',
                'bartik_fintech_lf_share_app':         'Bartik Share: Application (Locus=Full)',
                'bartik_fintech_lc_iv_full':           'Bartik IV: Fintech-Cat (Locus=Ctx, Full)',
                'bartik_fintech_lc_iv_ctx':            'Bartik IV: Fintech-Cat (Locus=Ctx, Ctx)',
                'bartik_fintech_lc_share_tech':        'Bartik Share: Technology (Locus=Ctx)',
                'bartik_fintech_lc_share_app':         'Bartik Share: Application (Locus=Ctx)',
                # Bartik IV — 媒体类型维度 (稳健性 3)
                'bartik_media_iv_full':                'Bartik IV: Media-Type (Full)',
                'bartik_media_iv_ctx':                 'Bartik IV: Media-Type (Ctx)',
                'bartik_media_share_fin':              'Bartik Share: Financial Media',
                'bartik_media_share_comp':             'Bartik Share: Comprehensive Media',
                # fix(omni-g-panel-export-03, 2026-06-11): 移除"稳健性 4-8"幻影
                # Bartik 维度标签 (mcentral/mfin/mcomp/mofficial/mmarket/mfreq/
                # mdeep/mdaily/mprov) — 全仓无任何生产代码产出这些列 (runner.py
                # 仅调用 type/scale/media/mauth/geoprox/fintech_lf/lc 七族;
                # v6/F4 删除清单见 runner.py "v6/F4 删除清单" 注释段)。这些键
                # 不是数据未就位的合法 dormant (如 GOV_*/bal_w*), 而是代码路径
                # 根本不存在的纯幻影, 保留会虚报测度面。
                # Bartik IV — 媒体权威性 (稳健性 4)
                'bartik_mauth_iv_full':                'Bartik IV: Media-Authority (Full)',
                'bartik_mauth_iv_ctx':                 'Bartik IV: Media-Authority (Ctx)',
                'bartik_mauth_share_high':             'Bartik Share: High Authority',
                'bartik_mauth_share_mid':              'Bartik Share: Mid Authority',
                'bartik_mauth_share_low':              'Bartik Share: Low Authority',
                # fix(omni-g-panel-export-03, 2026-06-11): 移除"稳健性 9-14"幻影
                # Bartik 维度标签 (doclen/half/qtr/month/wkday/excl) — 同上,
                # 无任何生产代码产出 (且与 v6/F4 外生性公理删除决策一致)。
                # Bartik IV — 地理邻近 (稳健性 5)
                'bartik_geoprox_iv_full':              'Bartik IV: Geo-Proximity (Full)',
                'bartik_geoprox_iv_ctx':               'Bartik IV: Geo-Proximity (Ctx)',
                # fix(omni-g-panel-export-03, 2026-06-11): 移除"稳健性 16-28"幻影
                # Bartik 维度标签 (title/mden/mcount/breadth/sentlen/ttr/pubfmt/
                # author/page/pgnum/kwdiv/kwden) — 同上, 无任何生产代码产出
                # (title 维度另随 v3.8.0 remove-title-track 失去语义基础)。
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
                # 双模型嵌入: text2vec 稳健 twin (2026-05-29 双模型重构; 主轨=
                # text-embedding-3-small, _t2v=shibing624/text2vec 同算法只换模型)。
                # 原 stage 30 退役后, 这些列由 stage 15/25/26/27/network 内联产出。
                # fix(omni-g-panel-export-07, 2026-06-11): 原注释声称"与
                # stata_export.py::HEURISTIC_LABELS 同源"不实 — 实为手抄副本且
                # 2 对文本已漂移 (strat_diff_t2v_*/policy_cosine_sim_t2v_*); 现
                # 逐字对齐 46-path 文本 (verbatim sync, 由
                # tests/test_omni_fix_panel_export.py 锁定)。真单一常量化需
                # stata_export 侧将 HEURISTIC_LABELS 提升为模块级配合 (另组负责);
                # 46-path 缺 emb_peer_tone_lag1_t2v_ctx 键亦待该侧补齐。
                'strat_diff_t2v_full':                 'Strat Diff (T2V robust=text2vec, full)',
                'strat_diff_t2v_ctx':                  'Strat Diff (T2V robust=text2vec, ctx)',
                'policy_cosine_sim_t2v_full':          'Policy Cosine Sim (T2V robust, full)',
                'policy_cosine_sim_t2v_ctx':           'Policy Cosine Sim (T2V robust, ctx)',
                'strat_diff_n5_emb_t2v':               'Strat Diff N5 Emb (T2V robust, full)',
                'strat_diff_n5_emb_t2v_ctx':           'Strat Diff N5 Emb (T2V robust, ctx)',
                'strat_sim_max_emb_t2v':               'Strat Max Sim Emb (T2V robust, full)',
                'strat_sim_max_emb_t2v_ctx':           'Strat Max Sim Emb (T2V robust, ctx)',
                'centroid_diff_emb_t2v':               'Centroid Diff Emb (T2V robust, full)',
                'centroid_diff_emb_t2v_ctx':           'Centroid Diff Emb (T2V robust, ctx)',
                'coh_emb_t2v_full':                    'Temporal Coherence Emb (T2V robust, full)',
                'coh_emb_t2v_ctx':                     'Temporal Coherence Emb (T2V robust, ctx)',
                'auth_sim_emb_t2v_full':               'Auth Policy Sim Emb (T2V robust, full)',
                'auth_sim_emb_t2v_ctx':                'Auth Policy Sim Emb (T2V robust, ctx)',
                'benefit_mean_t2v_full':               'Benefit Attitude Mean (T2V robust, full)',
                'benefit_mean_t2v_ctx':                'Benefit Attitude Mean (T2V robust, ctx)',
                'benefit_std_t2v_full':                'Benefit Attitude SD (T2V robust, full)',
                'benefit_std_t2v_ctx':                 'Benefit Attitude SD (T2V robust, ctx)',
                'benefit_pos_frac_t2v_full':           'Benefit Pos Frac (T2V robust, full)',
                'benefit_pos_frac_t2v_ctx':            'Benefit Pos Frac (T2V robust, ctx)',
                'benefit_neg_frac_t2v_full':           'Benefit Neg Frac (T2V robust, full)',
                'benefit_neg_frac_t2v_ctx':            'Benefit Neg Frac (T2V robust, ctx)',
                'emb_peer_tone_lag1_t2v_full':         'Emb Peer Tone Lag1 (T2V robust, full)',
                'emb_peer_tone_lag1_t2v_ctx':          'Emb Peer Tone Lag1 (T2V robust, ctx)',
                'bank_emb_sim_mean_lag1_t2v':          'Bank Emb Sim Mean (L1, T2V robust)',
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
                # fix(omni-g-panel-export-01, 2026-06-11): 供应商归属勘误 —
                # deepseekv4 实为 DeepSeek V4 Flash (单一事实源 config/
                # sentiment.yaml::models, 直连 api.deepseek.com), 原误标
                # 'Grok-4.1' (xAI 与 DeepSeek 是两家公司的不同模型)。
                'avg_deepseekv4_conf_full':                'DeepSeek-V4 Confidence (Full)',
                'avg_deepseekv4_conf_ctx':                 'DeepSeek-V4 Confidence (Ctx)',
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
                # 跟风新闻检测 (Tetlock 2011, RFS)
                # fix(omni-g-panel-export-02, 2026-06-11): v3.6.0 双轨化后实际
                # 列为 *_herd_weight_full/_ctx 六列 (encode.py 聚合), 原无后缀
                # 键 avg/min_herd_weight 已不存在 → 活跃列曾在 .dta 中无标签。
                'avg_herd_weight_full':                'Avg Herd Decay Weight 1/(1+N) (Tetlock 2011, Full)',
                'avg_herd_weight_ctx':                 'Avg Herd Decay Weight 1/(1+N) (Tetlock 2011, Ctx)',
                'min_herd_weight_full':                'Min Herd Decay Weight (Tetlock 2011, Full)',
                'min_herd_weight_ctx':                 'Min Herd Decay Weight (Tetlock 2011, Ctx)',
                'sum_herd_weight_full':                'Sum Herd Decay Weight (HW denominator, Full)',
                'sum_herd_weight_ctx':                 'Sum Herd Decay Weight (HW denominator, Ctx)',
                # 跟风衰减加权情感 (Tetlock 2011, RFS)
                'llm_vote_tone_hw_full':               'LLM Vote Tone (Herd-Decay Wt, Full)',
                'llm_vote_tone_hw_ctx':                'LLM Vote Tone (Herd-Decay Wt, Ctx)',
                'llm_vote_cont_hw_full':               'LLM Vote Cont (Herd-Decay Wt, Full)',
                'llm_vote_cont_hw_ctx':                'LLM Vote Cont (Herd-Decay Wt, Ctx)',
                # 跟风阈值敏感性变体 (2026-06-13) 的标签在字典字面量闭合后由
                # update() 注入 (见下方) — 本字面量须保持纯常量, 供
                # test_omni_fix_panel_export 以空 builtins eval 提取。
                # ═══ 银行共现网络: Part A (11) ═══
                'bank_degree_cent':     'Co-mention Degree Centrality (Freeman 1979)',
                'bank_strength_cent':   'Co-mention Strength Centrality (Opsahl 2010)',
                'bank_between_cent':    'Co-mention Betweenness (Freeman 1979)',
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
                # ═══ 银行共现网络: Part D-2 二阶溢出 (3) ═══
                'peer_tone_2nd_lag1_full':  '2nd-Order Peer Sentiment Spillover (Full)',
                'peer_tone_2nd_lag1_ctx':   '2nd-Order Peer Sentiment Spillover (Ctx)',
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
                # dual-track parity (2026-06-08): 地理-媒体情感 _ctx 孪生 (attention_media
                # 早已双轨产出, 仅此前缺 Stata 标签 → .dta 中 _ctx 列丢失变量标签)。
                'tone_homeprov_media_ctx':          'Home-Province Media Tone (Ctx)',
                'tone_nonprov_media_ctx':           'Non-Province Media Tone (Ctx)',
                'tone_gap_homeprov_nonprov_ctx':    'Local Media Slant: Prov (Ctx)',
                'tone_homecity_media_ctx':          'Home-City Media Tone (Ctx)',
                'tone_noncity_media_ctx':           'Non-City Media Tone (Ctx)',
                'tone_gap_homecity_noncity_ctx':    'Local Media Slant: City (Ctx)',
                'neg_frac_homeprov_ctx':            'Home-Province Neg Frac (Ctx)',
                'neg_frac_nonprov_ctx':             'Non-Province Neg Frac (Ctx)',
                'neg_frac_homecity_ctx':            'Home-City Neg Frac (Ctx)',
                'neg_frac_noncity_ctx':             'Non-City Neg Frac (Ctx)',
                # Janis-Fadner 极性系数 (Janis & Fadner 1965; Deephouse 2000, J. of Management 26(6):1091-1112).
                # ⚠ 2026-06-05 勘误: 此前误注 "Jiang et al. 2019 (姜富伟)"; 实现的是 J-F
                # 极性集中度系数 (P²-PN)/(P+N)² 类, 与 Jiang 2019 PLS 市场情绪指数无关。
                'jf_coefficient_full':              'JF Coefficient (Full-text)',
                'jf_coefficient_ctx':               'JF Coefficient (Context)',
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
                             'finbert_cn', 'fin_sent_zh', 'finbert2']
                   for s, t in [('', 'Full'), ('_ctx', 'Ctx')]},
                # ═══ 停刊稳健性 (Heese et al. 2022, JFE) ═══
                'ceased_media_frac':             'Ceased Media Article Share',
                'n_articles_exc':                'N Articles Excl Ceased Media',
                'exc_tone_full':                 'Tone Excl Ceased (LLM Vote, Full)',
                'exc_tone_ctx':                  'Tone Excl Ceased (LLM Vote, Ctx)',
                # ═══ 平衡媒体面板 (Wooldridge 2010, §19.9) ═══
                'bal_w0724_tone_full':           'Balanced W07-24 Tone (Full)',
                'bal_w0724_tone_ctx':            'Balanced W07-24 Tone (Ctx)',
                'bal_w1024_tone_full':           'Balanced W10-24 Tone (Full)',
                'bal_w1024_tone_ctx':            'Balanced W10-24 Tone (Ctx)',
                'bal_w1124_tone_full':           'Balanced W11-24 Tone (Full)',
                'bal_w1124_tone_ctx':            'Balanced W11-24 Tone (Ctx)',
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
                # dual-track parity (2026-06-08): 距离缓冲情感 _ctx 孪生 (geography.py 新增,
                # 由同模块 LOO-IV 双轨惯用法指导; full 轨保留既有列名: tone_*_full + pos/neg_frac)。
                'prox_50km_tone_ctx':            'Avg Tone Within 50km (Ctx)',
                'prox_50km_pos_frac_ctx':        'Pos Frac Within 50km (Ctx)',
                'prox_50km_neg_frac_ctx':        'Neg Frac Within 50km (Ctx)',
                'prox_100km_tone_ctx':           'Avg Tone Within 100km (Ctx)',
                'prox_100km_pos_frac_ctx':       'Pos Frac Within 100km (Ctx)',
                'prox_100km_neg_frac_ctx':       'Neg Frac Within 100km (Ctx)',
                'prox_150km_tone_ctx':           'Avg Tone Within 150km (Ctx)',
                'prox_150km_pos_frac_ctx':       'Pos Frac Within 150km (Ctx)',
                'prox_150km_neg_frac_ctx':       'Neg Frac Within 150km (Ctx)',
                'prox_200km_tone_ctx':           'Avg Tone Within 200km (Ctx)',
                'prox_200km_pos_frac_ctx':       'Pos Frac Within 200km (Ctx)',
                'prox_200km_neg_frac_ctx':       'Neg Frac Within 200km (Ctx)',
                # === 区域同行 FinTech 新闻覆盖渗透率 (Leary & Roberts 2014 同行压力代理) ===
                # fix(omni-g-panel-export-08, 2026-06-11): 构念勘误 — 实测度为
                # LOO mean I(n_articles>0) (geography.py: 区域内其他银行有任意
                # fintech 新闻覆盖的比例), 无 AI 子类过滤、亦非"模仿率"; 原标签
                # 'AI Imitation Rate' 把误称固化进 .dta。列名 ai_reg_* 保留
                # (向后兼容), 标签如实改述为同行覆盖渗透。
                'ai_reg_province':               'Peer FinTech Coverage Penetration (Province, LOO)',
                'ai_reg_city':                   'Peer FinTech Coverage Penetration (City, LOO)',
                'ai_reg_50km':                   'Peer FinTech Coverage Penetration (50km, LOO)',
                'ai_reg_100km':                  'Peer FinTech Coverage Penetration (100km, LOO)',
                'ai_reg_150km':                  'Peer FinTech Coverage Penetration (150km, LOO)',
                'ai_reg_200km':                  'Peer FinTech Coverage Penetration (200km, LOO)',
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
                # dual-track parity (2026-06-08): Fluidity _ctx 孪生 (strategic_diff.py 新增)
                'strat_fluidity_ctx':   'Product Mkt Fluidity TF-IDF char (Ctx)',
                'strat_fluidity_w_ctx': 'Product Mkt Fluidity TF-IDF jieba (Ctx)',
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
                'industry_neg_shock':            'Industry Neg Shock (LOO, same-period; year-FE collinear)',
                'industry_neg_shock_lag1':       'Industry Neg Shock LOO (L1, year-FE-safe)',
                'brokerage_fire_sale':           'Brokerage x Neg Shock',
                # === 同行金融科技溢出 (LeSage & Pace 2009; Leary & Roberts 2014 JF) ===
                # fix(omni-g-misc-01, 2026-06-11): 原误引 Berger et al. (2022, JFI) — 该文研究
                # EPU 与银行流动性囤积, 与本构念 (row-stochastic 同行声量溢出) 不符; 正确锚点
                # 同 network_spillover.py:309-316 勘误 (空间滞后 + 同行均值范式)。
                'peer_fintech_exposure_lag1':    'Peer Fintech Exposure (L1)',
                # === Embedding 同业网络 (Hoberg & Phillips 2016) ===
                'emb_peer_tone_lag1_full':      'Emb Peer Tone L1 (Full)',
                'emb_peer_tone_lag1_ctx':       'Emb Peer Tone L1 (Ctx)',
                'bank_emb_sim_mean_lag1':       'Bank Embedding Sim Mean (L1)',
                # === LLM-Peer 竞争网络 IV (Cao et al. 2025) ===
                # 主回归变量 (无后缀, difflib 名归一 cutoff=0.80)
                # fix(omni-g-misc-02, 2026-06-11): cutoff 是 difflib.get_close_matches 的
                # 字符串匹配严格度 (LLM 输出银行名 → 规范名归一), 非 Hoberg-Phillips TNIC
                # 同行语义相似度阈值 — 口径勘误同 llm_peer_iv.py:692。
                'llm_peer_tone_iv_full':        'LLM-Peer Tone IV (Full)',
                'llm_peer_tone_iv_ctx':         'LLM-Peer Tone IV (Ctx)',
                # === IV 扩展族 (iv_extensions.py, 2026-06-13) ===
                # 引用见模块头: GPSS 2020 AER / Manski 1993 / Leary-Roberts 2014 JF /
                # Gentzkow-Shapiro 2010 ECMA / Dougal et al. 2012 RFS / Gurun-Butler 2012 JF
                'leave_one_out_peer_attention_iv':
                    'Peer LOO Attention IV (type-year)',
                'leave_one_out_peer_attention_iv_lag1':
                    'Peer LOO Attention IV (lag 1)',
                'bartik_attention_iv':          'Bartik Attention IV (Full)',
                'bartik_attention_iv_full':     'Bartik Attention IV (Full)',
                'bartik_attention_iv_ctx':      'Bartik Attention IV (Ctx)',
                'leave_one_out_peer_subst_iv':  'Peer LOO Substantive IV',
                'leave_one_out_peer_subst_iv_lag1':
                    'Peer LOO Substantive IV (lag 1)',
                'bartik_subst_iv_full':         'Bartik Substantive IV (Full)',
                'bartik_subst_iv_ctx':          'Bartik Substantive IV (Ctx)',
                'leave_one_out_peer_locus_iv':  'Peer LOO Locus(Tech) IV',
                'leave_one_out_peer_locus_iv_lag1':
                    'Peer LOO Locus(Tech) IV (lag 1)',
                'leave_one_out_peer_collab_iv': 'Peer LOO Collab IV',
                'leave_one_out_peer_collab_iv_lag1':
                    'Peer LOO Collab IV (lag 1)',
                'bartik_collab_iv_full':        'Bartik Collab IV (Full)',
                'bartik_collab_iv_ctx':         'Bartik Collab IV (Ctx)',
                'leave_one_out_peer_benefit_iv': 'Peer LOO Benefit-Attitude IV',
                'leave_one_out_peer_benefit_iv_lag1':
                    'Peer LOO Benefit-Attitude IV (lag 1)',
                'zone_leave1out_benefit_iv':    'Zone LOO Benefit-Attitude IV',
                'outlet_disp_exposure_iv_full': 'Outlet Dispersion Exposure IV (Full)',
                'outlet_disp_exposure_iv_ctx':  'Outlet Dispersion Exposure IV (Ctx)',
                'outlet_style_clarity_iv_full': 'Outlet Style Clarity IV (Full)',
                'outlet_style_clarity_iv_ctx':  'Outlet Style Clarity IV (Ctx)',
                'llm_peer_coverage_iv':         'LLM-Peer Coverage IV',
                'llm_peer_count':               'LLM-Peer Count',
                'peer_compete_idx':             'Peer Competition Index (0.80)',
                # 多阈值敏感性变体 (cutoff=0.70/0.75/0.80/0.85/0.90)
                **{f'llm_peer_tone_iv_full_{c}': f'LLM-Peer Tone IV (Full, c={c/100:.2f})'
                   for c in [70, 75, 80, 85, 90]},
                # dual-track parity (2026-06-08): ctx 轨 IV 多阈值 (llm_peer_iv.py 新增)
                **{f'llm_peer_tone_iv_ctx_{c}': f'LLM-Peer Tone IV (Ctx, c={c/100:.2f})'
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
                   for b in ['finbert_cn', 'fin_sent_zh', 'finbert2']
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
                   for b in ['finbert_cn', 'fin_sent_zh', 'finbert2']
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
                   for b in ['finbert_cn', 'fin_sent_zh', 'finbert2']
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
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                **{f'avg_llm_prob_score_std{s}': f'Std Prob Score ({t})'
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                **{f'llm_prob_score_sum{s}': f'Sum Prob Score ({t})'
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                **{f'llm_vote_tone_vw_prob{s}': f'VW Prob Tone ({t})'
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                **{f'llm_vote_tone_mw_prob{s}': f'MW Prob Tone ({t})'
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
                **{f'llm_vote_tone_hw_prob{s}': f'HW Prob Tone ({t})'
                   for s, t in [('_full', 'Full'), ('_ctx', 'Ctx')]},
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
                # === 文章级政策对齐 Article-level Policy Alignment (Stage 15; Distel et al. 2026) ===
                # 连续型聚合 (主回归用)
                'article_sim_mean':       'Avg Article-Policy Cosine Sim',
                'article_sim_std':        'Std Article-Policy Cosine Sim',
                # dual-track parity (2026-06-08): MAIN/API spec 政策对齐 _ctx 孪生 (runner.py
                # 新增聚合; 与 _t2v 轨 policy_cosine_sim_t2v_full/_ctx 面板双轨对称)。
                'article_sim_mean_ctx':   'Avg Article-Policy Cosine Sim (Ctx)',
                'article_sim_std_ctx':    'Std Article-Policy Cosine Sim (Ctx)',
                'fintech_intensity_mean': 'Avg FinTech Intensity Score',
                # 象限离散分类 (机制检验 / 稳健性用)
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
                # v3.5.1 A3 Numerical Intensity (数值披露强度; 引文勘误见 codebook reference) — 真双轨
                'mean_num_intensity_full':   'Mean Numerical Intensity Full (dual-track)',
                'mean_num_intensity_ctx':    'Mean Numerical Intensity Ctx (dual-track)',
            }
            # 跟风阈值敏感性变体标签 (2026-06-13): 逐 τ 重估的稳健性 DV +
            # 逐 τ 权重诊断; 网格单一事实源 = core.config.herd_sensitivity_grid。
            # 字面量外 update 注入: 标签随配置网格动态, 不能写死在纯常量字典里。
            for _thr, _tag in zip(*herd_sensitivity_grid(CONFIG)):
                for _s, _t in (('_full', 'Full'), ('_ctx', 'Ctx')):
                    STATA_LABELS[f'llm_vote_tone_hw_{_tag}{_s}'] = (
                        f'LLM Vote Tone (Herd Wt @t={_thr:.2f}, {_t})')
                    STATA_LABELS[f'llm_vote_cont_hw_{_tag}{_s}'] = (
                        f'LLM Vote Cont (Herd Wt @t={_thr:.2f}, {_t})')
                    STATA_LABELS[f'avg_herd_weight{_s}_{_tag}'] = (
                        f'Avg Herd Decay Weight @t={_thr:.2f} ({_t})')
                    STATA_LABELS[f'sum_herd_weight{_s}_{_tag}'] = (
                        f'Sum Herd Decay Weight @t={_thr:.2f} ({_t})')
            # 仅保留面板中实际存在的列
            labels = {k: v for k, v in STATA_LABELS.items()
                      if k in panel_stata.columns}
            # fix(omni-g-panel-export-06, 2026-06-11): 未命中 STATA_LABELS 的列
            # 复用 stage 46 启发式兜底 (codebook → HEURISTIC_LABELS → 列名),
            # 杜绝主回归变量 (llm_vote_tone_full/_ctx 等) 在 .dta 中无标签;
            # 兜底后做 100% 覆盖率断言 (fail-loud 而非静默漏标)。
            labels = _apply_label_fallback(labels, panel_stata.columns)
            _unlabeled = [c for c in panel_stata.columns if not labels.get(c)]
            if _unlabeled:
                raise RuntimeError(
                    f"[export_panel] 变量标签覆盖率断言失败: "
                    f"{len(_unlabeled)} 列无标签 (前 10): {_unlabeled[:10]}"
                )
            logger.info(
                f"  变量标签覆盖: {len(labels)}/{len(panel_stata.columns)} 列 "
                f"(显式 STATA_LABELS 命中 "
                f"{sum(1 for c in panel_stata.columns if c in STATA_LABELS)}, "
                f"其余启发式兜底)"
            )
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
