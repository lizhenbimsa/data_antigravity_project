"""
51_falsification_test.py — 伪造检验: 非金融科技对照变量构建
============================================================

学术背景与方法论依据:
  本脚本实现基于 Hassan et al. (2019) 伪造检验范式的构造效度验证。
  通过构建 non-fintech 控制变量（volume-based），检验核心 fintech tone
  指标是否具有超越一般媒体关注度的增量解释力。

参考文献:
  [1] Hassan, T.A., Hollander, S., van Lent, L. & Tahoun, A. (2019).
      "Firm-Level Political Risk: Measurement and Effects."
      The Quarterly Journal of Economics, 134(4), 2135-2202.
      → 本脚本核心方法论来源: Table 7 伪造检验范式 (PRisk vs NPRisk)

  [2] Fang, L. & Peress, J. (2009).
      "Media Coverage and the Cross-Section of Stock Returns."
      The Journal of Finance, 64(5), 2023-2052.
      → nf_ln_coverage = log(1 + count) 的对数变换依据

  [3] Tetlock, P.C. (2007).
      "Giving Content to Investor Sentiment: The Role of Media in the Stock Market."
      The Journal of Finance, 62(3), 1139-1168.
      → 新闻量 (volume) 与情感内容 (content) 的概念区分

  [4] Bushee, B.J., Core, J.E., Guay, W. & Hamm, S.J.W. (2010).
      "The Role of the Business Press as an Information Intermediary."
      Journal of Accounting Research, 48(1), 1-19.
      → nf_media_breadth (不同媒体来源数) 作为信息环境指标的依据

假设检验框架:
  H0: fintech tone 的解释力完全来自银行层面一般媒体关注度
  H1: fintech tone 包含金融科技维度的特异性增量信息

数据流:
  Non-Fintech = 12_fintech_news_full.parquet (全量银行新闻)
              MINUS 40_article_bank_level.parquet (最终面板文章)

输入:
  data/processed/12_fintech_news_full.parquet
  data/processed/40_article_bank_level.parquet
  data/processed/40_panel_yearly.parquet

输出:
  data/processed/51_panel_with_controls.parquet
  data/processed/51_panel_with_controls.dta
  data/processed/51_falsification_diagnostics.csv
"""

import os
import re
import sys
import time
import warnings
from pathlib import Path

# Phase 4c: 让 ``python -m news_process.pipeline.falsification.controls`` 与
# pytest / 51_falsification_test.py 根 shim 都能解析包导入。
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

import numpy as np
import pandas as pd

from news_process.core.config import load_config
from news_process.core.logging import setup_logging, log_stage_summary
from news_process.core.reporting import save_dataset

warnings.filterwarnings('ignore', category=FutureWarning)

# ============================================================================
# 1. 全局配置与初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "51_falsification_test"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

OUTPUT_DIR = CONFIG["paths"]["output_dir"]
FILENAMES = CONFIG.get("filenames", {})

# ============================================================================
# 参考文献完整引用 (供日志输出)
# ============================================================================
REFERENCES = {
    'Hassan2019': (
        'Hassan, T.A., Hollander, S., van Lent, L. & Tahoun, A. (2019). '
        '"Firm-Level Political Risk: Measurement and Effects." '
        'The Quarterly Journal of Economics, 134(4), 2135-2202.'
    ),
    'Fang2009': (
        'Fang, L. & Peress, J. (2009). '
        '"Media Coverage and the Cross-Section of Stock Returns." '
        'The Journal of Finance, 64(5), 2023-2052.'
    ),
    'Tetlock2007': (
        'Tetlock, P.C. (2007). '
        '"Giving Content to Investor Sentiment: The Role of Media in the Stock Market." '
        'The Journal of Finance, 62(3), 1139-1168.'
    ),
    'Bushee2010': (
        'Bushee, B.J., Core, J.E., Guay, W. & Hamm, S.J.W. (2010). '
        '"The Role of the Business Press as an Information Intermediary." '
        'Journal of Accounting Research, 48(1), 1-19.'
    ),
    'Garcia2013': (
        'Garcia, D. (2013). '
        '"Sentiment during Recessions." '
        'The Journal of Finance, 68(3), 1267-1300.'
    ),
    'DimSV2024': (
        'Dim, C., Sangiorgi, I. & Vilkov, G. (2024). '
        '"Media Narratives and Price Informativeness." '
        'SSRN Working Paper No. 4323093.'
    ),
    # ── 以下引用为检验 8-10 (IV 回归, Oster 检验, 地理聚类) 新增 ──
    'LuoLi2025': (
        'Luo, Q. & Li, H. (2025). '
        '"Media sentiment and corporate R&D manipulation." '
        'Finance Research Letters, 81, 107505.'
    ),
    'Oster2019': (
        'Oster, E. (2019). '
        '"Unobservable Selection and Coefficient Stability: '
        'Theory and Evidence." '
        'Journal of Business & Economic Statistics, 37(2), 187-204.'
    ),
    'GurunButler2012': (
        'Gurun, U.G. & Butler, A.W. (2012). '
        '"Don\'t Believe the Hype: Local Media Slant, Local Advertising, '
        'and Firm Value." '
        'The Journal of Finance, 67(2), 561-598.'
    ),
    'CameronMiller2015': (
        'Cameron, A.C. & Miller, D.L. (2015). '
        '"A Practitioner\'s Guide to Cluster-Robust Inference." '
        'Journal of Human Resources, 50(2), 317-372.'
    ),
    # ── 以下引用为残差法稳健性检验新增 ──
    'FangWWY2024': (
        'Fang, Y., Wang, Q., Wang, Y. & Yuan, Y. (2024). '
        '"Media sentiment, deposit stability and bank systemic risk: '
        'Evidence from China." '
        'International Review of Economics & Finance, 91, 1150-1172.'
    ),
    # ── 以下引用为调节效应与异质性检验新增 ──
    'QuYang2025': (
        'Qu, L. & Yang, R. (2025). '
        '"Media sentiment, financial services, and corporate investment levels." '
        'Working Paper / Finance Research Letters series.'
    ),
    'BramborCG2006': (
        'Brambor, T., Clark, W.R. & Golder, M. (2006). '
        '"Understanding Interaction Models: Improving Empirical Analyses." '
        'Political Analysis, 14(1), 63-82.'
    ),
    'Chow1960': (
        'Chow, G.C. (1960). '
        '"Tests of Equality Between Sets of Coefficients in Two Linear Regressions." '
        'Econometrica, 28(3), 591-605.'
    ),
    # ── 以下引用为检验 15 (治理约束型合约控制变量) 新增 ──
    'ZhouCZY2026': (
        'Zhou, Y., Chen, L., Zhou, F. & Ye, M. (2026). '
        '"Contractual arrangements and information consistency: '
        'How ESG executive compensation incentives affect corporate AI disclosure." '
        'Journal of Business Research, 207, 116019. '
        'https://doi.org/10.1016/j.jbusres.2026.116019'
    ),
    'CoreGL2003': (
        'Core, J.E., Guay, W.R. & Larcker, D.F. (2003). '
        '"Executive Equity Compensation and Incentives: A Survey." '
        'FRBNY Economic Policy Review, 9(1), 27-50. '
        'https://www.newyorkfed.org/medialibrary/media/research/epr/03v09n1/0304core.pdf'
    ),
    'FlaBan2017': (
        'Flammer, C. & Bansal, P. (2017). '
        '"Does a Long-Term Orientation Create Value? Evidence from a '
        'Regression Discontinuity." '
        'Strategic Management Journal, 38(9), 1827-1847. '
        'https://doi.org/10.1002/smj.2629'
    ),
    'EdmGL2009': (
        'Edmans, A., Gabaix, X. & Landier, A. (2009). '
        '"A Multiplicative Model of Optimal CEO Incentives in Market Equilibrium." '
        'The Review of Financial Studies, 22(12), 4881-4917. '
        'https://doi.org/10.1093/rfs/hhn117'
    ),
    'IoanSer2015': (
        'Ioannou, I. & Serafeim, G. (2015). '
        '"The Impact of Corporate Social Responsibility on Investment Recommendations: '
        'Analysts\' Perceptions and Shifting Institutional Logics." '
        'Strategic Management Journal, 36(7), 1053-1081. '
        'https://doi.org/10.1002/smj.2268'
    ),
    'FamaJen1983': (
        'Fama, E.F. & Jensen, M.C. (1983). '
        '"Separation of Ownership and Control." '
        'Journal of Law and Economics, 26(2), 301-325. '
        'https://doi.org/10.1086/467037'
    ),
}


# ============================================================================
# 2. 数据加载
# ============================================================================

def load_data():
    """加载三个输入文件。"""
    logger.info("=" * 70)
    logger.info("步骤 1: 数据加载")
    logger.info("=" * 70)
    logger.info("  说明: 加载三个数据文件,分别代表:")
    logger.info("    (a) 全量银行新闻 (含 fintech 和 non-fintech)")
    logger.info("    (b) 最终进入面板的 fintech 文章")
    logger.info("    (c) 已有的 Bank-Year 面板")

    # --- (a) 全量银行新闻 ---
    full_path = os.path.join(
        OUTPUT_DIR,
        FILENAMES.get('output_12_fintech_full', '12_fintech_news_full.parquet')
    )
    if not os.path.exists(full_path):
        logger.error(f"  ✗ 输入文件不存在: {full_path}")
        logger.error(f"  → 请先运行 12_news_fintech.py 生成此文件")
        sys.exit(1)
    df_full = pd.read_parquet(full_path)
    logger.info(f"  (a) 12_fintech_news_full: {len(df_full):,} 行")
    logger.info(f"      数据粒度: article × target_bank (每篇新闻×每个相关银行)")
    logger.info(f"      唯一银行数: {df_full['target_bank'].nunique()}")
    logger.info(f"      列数: {df_full.shape[1]}")
    logger.info(f"      日期列类型: {df_full['日期'].dtype}")

    # --- (b) 面板文章 ---
    art_path = os.path.join(
        OUTPUT_DIR,
        FILENAMES.get('output_40_article_bank', '40_article_bank_level.parquet')
    )
    if not os.path.exists(art_path):
        logger.error(f"  ✗ 输入文件不存在: {art_path}")
        logger.error(f"  → 请先运行 45_panel_export_main.py 生成此文件")
        sys.exit(1)
    df_art = pd.read_parquet(art_path)
    logger.info(f"  (b) 40_article_bank_level: {len(df_art):,} 行")
    logger.info(f"      说明: 这些是关键词匹配 + LLM 验证通过的金融科技新闻")
    logger.info(f"      唯一银行数: {df_art['target_bank'].nunique()}")
    logger.info(f"      日期列类型: {df_art['日期'].dtype}")

    # --- (c) 已有面板 ---
    panel_path = os.path.join(
        OUTPUT_DIR,
        FILENAMES.get('output_40_panel_yearly', '40_panel_yearly.parquet')
    )
    if not os.path.exists(panel_path):
        logger.error(f"  ✗ 输入文件不存在: {panel_path}")
        logger.error(f"  → 请先运行 45_panel_export_main.py 生成此文件")
        sys.exit(1)
    panel = pd.read_parquet(panel_path)
    logger.info(f"  (c) 40_panel_yearly: {len(panel):,} 行")
    logger.info(f"      数据粒度: Bank × Year (平衡面板)")
    logger.info(f"      唯一银行数: {panel['target_bank'].nunique()}")
    logger.info(f"      年份范围: {panel['year'].min()} - {panel['year'].max()}")

    return df_full, df_art, panel


# ============================================================================
# 3. 反连接 (anti-join): 定义非金融科技对照组
# ============================================================================

def build_non_fintech(df_full: pd.DataFrame,
                      df_art: pd.DataFrame) -> pd.DataFrame:
    """通过 anti-join 定义非金融科技对照组。

    逻辑: Non-Fintech = 全量银行新闻 MINUS 最终面板文章
    这确保 LLM 拒绝的文章 (keyword=True, llm_verified=False) 也归入对照组。

    对标学术依据:
      Hassan et al. (2019, QJE, Table 7):
      PRisk 和 NPRisk 通过对同一文本语料的互补划分构建,
      确保两组指标穷尽全部文本信息。
      本脚本中 Fintech tone + Non-fintech volume = 全量银行新闻,
      遵循同一穷举原则。
    """
    logger.info("=" * 70)
    logger.info("步骤 2: Anti-join 构建非金融科技对照组")
    logger.info("=" * 70)
    logger.info("  方法论说明:")
    logger.info("    学术依据: Hassan et al. (2019, QJE, 134(4), 2135-2202)")
    logger.info("    → Table 7 伪造检验: PRisk 与 NPRisk 对同一语料互补划分")
    logger.info("    本脚本等价操作: Fintech 面板文章 + Non-Fintech 对照组 = 全量银行新闻")
    logger.info("")
    logger.info("  数据处理说明:")
    logger.info("    ⚠️ 关键技术细节: 40_article_bank_level 中 '日期' 列已被")
    logger.info("      41_panel_encode_aggregate.py parse_time() 转为 datetime64 类型,")
    logger.info("      而 12_fintech_news_full 中 '日期' 仍为原始 string 类型。")
    logger.info("      为避免类型不匹配导致 anti-join 静默失败,")
    logger.info("      统一转为 YYYY-MM-DD 格式字符串后再匹配。")

    # 防止修改调用方的原始 DataFrame (消除副作用)
    df_full = df_full.copy()
    df_art = df_art.copy()

    # 统一日期为标准化字符串 (避免 string vs datetime64 不匹配)
    df_full['_date_str'] = pd.to_datetime(
        df_full['日期'], errors='coerce'
    ).dt.strftime('%Y-%m-%d')
    df_art['_date_str'] = pd.to_datetime(
        df_art['日期'], errors='coerce'
    ).dt.strftime('%Y-%m-%d')

    # 检查日期转换中的 NaT
    full_nat = df_full['_date_str'].isna().sum()
    art_nat = df_art['_date_str'].isna().sum()
    if full_nat > 0:
        logger.warning(f"  ⚠️ 12_fintech_news_full 中 {full_nat:,} 条日期解析为 NaT")
    if art_nat > 0:
        logger.warning(f"  ⚠️ 40_article_bank_level 中 {art_nat:,} 条日期解析为 NaT")

    # 构建面板文章的复合键集合
    logger.info("")
    logger.info("  复合键组成: (target_bank, 标题, 日期)")
    logger.info("    说明: 两个文件均为 article × bank 粒度,")
    logger.info("          继承自 11_news_bank.py 的提早展开逻辑,")
    logger.info("          因此 (target_bank, 标题, 日期) 可作为可靠的匹配键。")

    # ── plan s2 修复: 集合 anti-join 在多重集场景下会破坏类划分 ──
    # 原始实现 `df_full[~_key.isin(panel_keys)]` 用 set 包装 df_art 的键,
    # 当同一 (target_bank, 标题, 日期) 在 df_art 出现多行时, df_full 中所有
    # 同键副本会被一律排除, 但 df_art 端只折叠为 1 行, 导致 panel + nf != total
    # 且互补划分被破坏。修复策略 (plan s2 方案 A): 双侧按复合键 drop_duplicates,
    # 显式约定"同 (target_bank, 标题, 日期) = 同一稿件"的集合语义, 报告被去重比例。
    _key_cols = ['target_bank', '标题', '_date_str']

    # 双侧去重诊断 (在 drop 之前) 与执行
    _df_art_before = len(df_art)
    df_art = df_art.drop_duplicates(subset=_key_cols, keep='first').copy()
    _df_art_dropped = _df_art_before - len(df_art)

    _df_full_before = len(df_full)
    df_full = df_full.drop_duplicates(subset=_key_cols, keep='first').copy()
    _df_full_dropped = _df_full_before - len(df_full)

    logger.info("")
    logger.info("  ─── 双侧 drop_duplicates(subset=复合键) 去重诊断 ───")
    logger.info(
        f"    40_article_bank_level: {_df_art_before:,} → {len(df_art):,} "
        f"(去重 {_df_art_dropped:,} 行, "
        f"{_df_art_dropped / max(_df_art_before, 1) * 100:.4f}%)"
    )
    logger.info(
        f"    12_fintech_news_full:  {_df_full_before:,} → {len(df_full):,} "
        f"(去重 {_df_full_dropped:,} 行, "
        f"{_df_full_dropped / max(_df_full_before, 1) * 100:.4f}%)"
    )
    if _df_art_dropped > 0 or _df_full_dropped > 0:
        logger.info(
            "    说明: 同 (target_bank, 标题, 日期) 视为同一稿件 (集合语义)。"
            "如需多重集差集 (按行级配对), 见 plan s2 方案 B/C。"
        )

    # 反连接 (anti-join, 集合差集)
    panel_keys = set(zip(
        df_art['target_bank'],
        df_art['标题'],
        df_art['_date_str']
    ))
    logger.info(f"  面板文章唯一键数 (= 行数): {len(panel_keys):,}")
    # 用显式 raise 替代 assert (assert 在 ``python -O`` 模式下被禁用),
    # 这是 drop_duplicates 之后必然成立的不变量; 一旦失败说明 pandas 行为
    # 异常或上游数据存在不可序列化的复合 NaN 类型, 必须立即停下排查。
    if len(panel_keys) != len(df_art):
        raise RuntimeError(
            f"drop_duplicates 后 panel_keys ({len(panel_keys):,}) 与 "
            f"df_art ({len(df_art):,}) 行数不一致, 数据异常 — 可能是 "
            f"_date_str 中存在不同 NaT 实例或 pandas 行为异常"
        )

    df_full['_key'] = list(zip(
        df_full['target_bank'],
        df_full['标题'],
        df_full['_date_str']
    ))
    df_nf = df_full[~df_full['_key'].isin(panel_keys)].copy()
    df_nf.drop(columns=['_key', '_date_str'], inplace=True)
    df_full.drop(columns=['_key', '_date_str'], inplace=True)

    # --- 三分类校验与详细统计 ---
    n_total = len(df_full)  # 已去重
    n_panel = len(df_art)   # 已去重
    n_nf = len(df_nf)
    logger.info("")
    logger.info("  ─── 三分类统计 (基于双侧去重后的口径) ───")
    logger.info(f"    ③ Fintech 面板文章 (keyword=True + LLM通过): {n_panel:,} 条")
    logger.info(f"    ①+② Non-Fintech 对照组:                     {n_nf:,} 条")
    logger.info(f"    全量银行新闻:                                 {n_total:,} 条")
    logger.info(f"    恒等校验: {n_panel:,} + {n_nf:,} = {n_panel + n_nf:,} "
                f"{'== ✓' if n_panel + n_nf == n_total else '!= ✗'} {n_total:,}")
    logger.info(f"    Fintech 占比: {n_panel / n_total * 100:.1f}%")
    logger.info(f"    Non-Fintech 占比: {n_nf / n_total * 100:.1f}%")

    if n_panel + n_nf != n_total:
        # 双侧 drop_duplicates 后理论上必有 panel + nf == total; 仍不等说明
        # df_art 中存在 (target_bank, 标题, 日期) 落在 df_full 之外的"幽灵键"
        diff = n_panel + n_nf - n_total
        logger.warning(f"  ⚠️ 去重后三分类不等式仍不成立! panel+nf-total = {diff:,} 条。")
        logger.warning("     可能原因: df_art 中存在 df_full 未覆盖的 (target_bank, 标题, 日期) 组合,")
        logger.warning("              即上游 ETL 漏抓部分稿件; 请检查 12 与 40 的覆盖一致性。")
        logger.warning(f"     影响评估: 差异量占总量 {abs(diff) / n_total * 100:.4f}%, 通常可忽略。")

    # 子分类统计 (区分 ① 和 ②)
    if 'is_fintech_news' in df_nf.columns:
        n_kw_false = (df_nf['is_fintech_news'] == False).sum()
        n_kw_true_llm_reject = (df_nf['is_fintech_news'] == True).sum()
        logger.info("")
        logger.info("  ─── Non-Fintech 子分类 ───")
        logger.info(f"    ① 关键词未匹配 (is_fintech_news=False):  {n_kw_false:,} 条 "
                     f"({n_kw_false / max(n_nf, 1) * 100:.1f}%)")
        logger.info(f"    ② 关键词匹配但 LLM 拒绝:                  {n_kw_true_llm_reject:,} 条 "
                     f"({n_kw_true_llm_reject / max(n_nf, 1) * 100:.1f}%)")
        logger.info(f"    说明: ①是完全不涉及金融科技的银行新闻,")
        logger.info(f"          ②是规则预筛通过但经 LLM 语义验证后被认定为非金融科技的新闻。")
        logger.info(f"          两者合并构成伪造检验的对照组。")

    return df_nf


# ============================================================================
# 4. 非金融科技 Bank–Year 聚合
# ============================================================================

def aggregate_non_fintech(df_nf: pd.DataFrame) -> pd.DataFrame:
    """按 (target_bank, year) 聚合非金融科技对照变量。

    生成变量及学术依据:
      nf_n_articles    — 非金融科技新闻篇数 (原始计数)
      nf_ln_coverage   — log(1 + count), Fang & Peress (2009, JF, 64(5), 2023-2052)
      nf_media_breadth — 不同媒体来源数, Bushee et al. (2010, JAR, 48(1), 1-19)
      nf_headline_frac — 平均标题提及率 (目标银行在标题中出现的比例)

    技术注意:
      - 12_fintech_news_full 中列名为 target_bank_in_title (非 in_title)
      - 媒体列名为 '媒体(中文)' (含中文括号)
    """
    logger.info("=" * 70)
    logger.info("步骤 3: Non-Fintech Bank-Year 聚合")
    logger.info("=" * 70)
    logger.info("  说明: 将文章级 non-fintech 新闻聚合为 Bank-Year 级别的对照变量。")
    logger.info("")
    logger.info("  ─── 变量定义与学术依据 ───")
    logger.info(f"  [1] nf_n_articles: 非金融科技新闻篇数 (原始计数)")
    logger.info(f"")
    logger.info(f"  [2] nf_ln_coverage = ln(1 + nf_n_articles)")
    logger.info(f"      学术依据: {REFERENCES['Fang2009']}")
    logger.info(f"      说明: Fang & Peress (2009) 使用 ln(1+媒体报道数) 作为")
    logger.info(f"            媒体关注度的连续变量,对数变换缓解右偏分布问题。")
    logger.info(f"")
    logger.info(f"  [3] nf_media_breadth: 不同媒体来源数 (nunique)")
    logger.info(f"      学术依据: {REFERENCES['Bushee2010']}")
    logger.info(f"      说明: Bushee et al. (2010) 指出信息中介的多样性")
    logger.info(f"            (媒体广度) 影响信息扩散效率,")
    logger.info(f"            不同媒体来源数量反映信息环境的丰富程度。")
    logger.info(f"")
    logger.info(f"  [4] nf_headline_frac: 标题提及率 = mean(target_bank_in_title)")
    logger.info(f"      说明: 目标银行出现在新闻标题中的比例,")
    logger.info(f"            标题提及通常意味着更高的新闻显著性和读者关注度。")

    # 处理空输入
    if len(df_nf) == 0:
        logger.warning("  ⚠️ Non-Fintech 组为空, 将返回空聚合结果")
        return pd.DataFrame(columns=[
            'target_bank', 'year', 'nf_n_articles', 'nf_ln_coverage',
            'nf_media_breadth', 'nf_headline_frac'
        ])

    # 防止修改调用方的原始 DataFrame (消除副作用)
    df_nf = df_nf.copy()

    # 解析年份
    logger.info("")
    logger.info("  ─── 年份解析 ───")
    df_nf['_year'] = pd.to_datetime(df_nf['日期'], errors='coerce').dt.year
    before_drop = len(df_nf)
    df_nf = df_nf.dropna(subset=['_year']).copy()
    df_nf['_year'] = df_nf['_year'].astype(int)
    after_drop = len(df_nf)
    dropped = before_drop - after_drop
    if dropped > 0:
        logger.warning(f"  ⚠️ 丢弃 {dropped:,} 条无效日期记录 "
                        f"({dropped / max(before_drop, 1) * 100:.2f}%)")
    logger.info(f"  有效记录: {after_drop:,} 条")

    # 聚合
    logger.info("")
    logger.info("  ─── 执行聚合 ───")

    # 媒体广度列名确认
    media_col = '媒体(中文)'
    has_media = media_col in df_nf.columns
    logger.info(f"  媒体列 '{media_col}' {'✓ 存在' if has_media else '✗ 不存在'}")

    # 标题提及率列名确认 (注意: 是 target_bank_in_title, 不是 in_title)
    headline_col = 'target_bank_in_title'
    has_headline = headline_col in df_nf.columns
    logger.info(f"  标题提及列 '{headline_col}' {'✓ 存在' if has_headline else '✗ 不存在'}")
    if has_headline:
        logger.info(f"    ⚠️ 技术备注: 列名是 '{headline_col}' (来自 11_news_bank.py),")
        logger.info(f"       而非 'in_title' (45_panel_export_main.py main() 中的重命名版本)")

    nf_agg = df_nf.groupby(['target_bank', '_year']).agg(
        nf_n_articles=('target_bank', 'count'),
    ).reset_index()
    nf_agg.rename(columns={'_year': 'year'}, inplace=True)

    # 媒体广度 (需要单独 nunique)
    if has_media:
        media_breadth = df_nf.groupby(
            ['target_bank', '_year']
        )[media_col].nunique().reset_index()
        media_breadth.columns = ['target_bank', 'year', 'nf_media_breadth']
        nf_agg = nf_agg.merge(media_breadth, on=['target_bank', 'year'], how='left')
    else:
        logger.warning(f"  ⚠️ 列 '{media_col}' 不存在, nf_media_breadth 将为 0")
        nf_agg['nf_media_breadth'] = 0

    # 标题提及率
    if has_headline:
        headline_frac = df_nf.groupby(
            ['target_bank', '_year']
        )[headline_col].mean().reset_index()
        headline_frac.columns = ['target_bank', 'year', 'nf_headline_frac']
        nf_agg = nf_agg.merge(headline_frac, on=['target_bank', 'year'], how='left')
    else:
        logger.warning(f"  ⚠️ 列 '{headline_col}' 不存在, nf_headline_frac 将为 0")
        nf_agg['nf_headline_frac'] = 0

    # 对数覆盖量 [Fang & Peress 2009]
    nf_agg['nf_ln_coverage'] = np.log1p(nf_agg['nf_n_articles'])

    # --- 描述性统计 ---
    logger.info("")
    logger.info("  ─── 聚合结果描述性统计 ───")
    logger.info(f"  聚合后行数 (Bank-Year): {len(nf_agg):,}")
    logger.info(f"  唯一银行数: {nf_agg['target_bank'].nunique()}")
    logger.info(f"  年份范围: {nf_agg['year'].min()} - {nf_agg['year'].max()}")
    logger.info(f"  nf_n_articles:    mean={nf_agg['nf_n_articles'].mean():.1f}, "
                f"median={nf_agg['nf_n_articles'].median():.0f}, "
                f"std={nf_agg['nf_n_articles'].std():.1f}, "
                f"min={nf_agg['nf_n_articles'].min():.0f}, "
                f"max={nf_agg['nf_n_articles'].max():.0f}")
    logger.info(f"  nf_ln_coverage:   mean={nf_agg['nf_ln_coverage'].mean():.3f}, "
                f"median={nf_agg['nf_ln_coverage'].median():.3f}")
    logger.info(f"  nf_media_breadth: mean={nf_agg['nf_media_breadth'].mean():.1f}, "
                f"median={nf_agg['nf_media_breadth'].median():.0f}")
    logger.info(f"  nf_headline_frac: mean={nf_agg['nf_headline_frac'].mean():.3f}, "
                f"median={nf_agg['nf_headline_frac'].median():.3f}")

    return nf_agg


# ============================================================================
# 5. 合并到面板 + 总量变量 + 校验
# ============================================================================

def merge_to_panel(panel: pd.DataFrame,
                   nf_agg: pd.DataFrame) -> pd.DataFrame:
    """将非金融科技对照变量合并到面板, 构造总量变量。

    总量变量学术依据:
      all_n_articles  = n_articles + nf_n_articles (穷举)
      all_ln_coverage = log(1 + all_n_articles), Fang & Peress (2009)
      fintech_share   = n_articles / all_n_articles (密集度边际)

    对标 Hassan et al. (2019) Table 7:
      all_ln_coverage 类似于 Risk_it (总体风险暴露),
      fintech tone 类似于 PRisk_it (特异性风险暴露)。
    """
    logger.info("=" * 70)
    logger.info("步骤 4: 合并到面板 + 总量变量")
    logger.info("=" * 70)
    logger.info("  说明: 将步骤3的对照变量通过 left join 合并到已有面板,")
    logger.info("        并构建总量指标用于赛马回归检验。")

    panel_before_cols = set(panel.columns)

    # Left join
    panel = panel.merge(nf_agg, on=['target_bank', 'year'], how='left')
    logger.info(f"  合并方式: left join on (target_bank, year)")

    # 缺失填充为 0 (与 balance_panel 的零新闻逻辑一致)
    fill_cols = ['nf_n_articles', 'nf_ln_coverage', 'nf_media_breadth', 'nf_headline_frac']
    filled_count = 0
    for c in fill_cols:
        if c in panel.columns:
            na_count = panel[c].isna().sum()
            filled_count += na_count
            panel[c] = panel[c].fillna(0)
    logger.info(f"  NaN 填充: {filled_count:,} 个单元格填为 0")
    logger.info(f"    说明: 某些 Bank-Year 在非金融科技组中没有新闻报道,")
    logger.info(f"          与 41_panel_encode_aggregate.py balance_panel 的零新闻处理一致。")

    # --- 总量变量 ---
    logger.info("")
    logger.info("  ─── 总量变量构建 ───")
    panel['all_n_articles'] = panel['n_articles'] + panel['nf_n_articles']
    logger.info(f"  all_n_articles = n_articles + nf_n_articles")

    panel['all_ln_coverage'] = np.log1p(panel['all_n_articles'])
    logger.info(f"  all_ln_coverage = ln(1 + all_n_articles)")
    logger.info(f"    依据: Fang & Peress (2009, JF, 64(5), 2023-2052)")

    # fintech_share (防除零)
    panel['fintech_share'] = np.where(
        panel['all_n_articles'] > 0,
        panel['n_articles'] / panel['all_n_articles'],
        0
    )
    logger.info(f"  fintech_share = n_articles / all_n_articles (除零保护)")
    logger.info(f"    说明: 当 all_n_articles=0 时, fintech_share=0 (非 NaN)")
    logger.info(f"    学术意义: 衡量金融科技新闻在全部银行新闻中的信息密集度,")
    logger.info(f"              类似 Hassan (2019) 中 PRisk / (PRisk + NPRisk) 的比例。")

    # --- 挤出效应弹性变量 (避免百分比回归机械 β=-1) ---
    panel['ln_ft_articles'] = np.log1p(panel['n_articles'])
    panel['ln_nf_articles'] = np.log1p(panel['nf_n_articles'])
    logger.info(f"  ln_ft_articles  = ln(1 + n_articles)")
    logger.info(f"  ln_nf_articles  = ln(1 + nf_n_articles)")
    logger.info(f"    依据: 对数弹性 ln(nf) ~ ln(ft) 避免 fintech% + nf% ≡ 100% 约束")

    # --- 恒等式校验 ---
    logger.info("")
    logger.info("  ─── 恒等式校验 ───")
    eq_check = (panel['all_n_articles'] == panel['n_articles'] + panel['nf_n_articles']).all()
    logger.info(f"  all = fintech + non-fintech: {'✓ 恒等式成立' if eq_check else '✗ 恒等式不成立!'}")
    if not eq_check:
        logger.error("  ✗ 恒等式校验失败! 请检查数据一致性。")

    # --- 变量名冲突检查 ---
    new_cols = set(panel.columns) - panel_before_cols
    conflict_cols = new_cols & panel_before_cols
    if conflict_cols:
        logger.warning(f"  ⚠️ 变量名冲突 (已覆盖原面板列): {conflict_cols}")
    else:
        logger.info(f"  变量名冲突检查: ✓ 无冲突 (所有新变量使用 nf_/all_/fintech_ 前缀)")

    # --- 描述性统计 ---
    logger.info("")
    logger.info("  ─── 合并后描述性统计 ───")
    logger.info(f"  面板行数: {len(panel):,}")
    logger.info(f"  新增列: {sorted(new_cols)}")
    logger.info(f"  fintech_share: mean={panel['fintech_share'].mean():.4f}, "
                f"median={panel['fintech_share'].median():.4f}, "
                f"p25={panel['fintech_share'].quantile(0.25):.4f}, "
                f"p75={panel['fintech_share'].quantile(0.75):.4f}")

    zero_all = (panel['all_n_articles'] == 0).sum()
    zero_ft = (panel['n_articles'] == 0).sum()
    zero_nf = (panel['nf_n_articles'] == 0).sum()
    logger.info(f"  零新闻行: 全部={zero_all:,}, fintech={zero_ft:,}, non-fintech={zero_nf:,}")

    return panel


# ============================================================================
# 6. 诊断报告: 相关矩阵
# ============================================================================

def run_diagnostics(panel: pd.DataFrame):
    """输出 Pearson/Spearman 相关矩阵与自动解读。

    诊断目的 (Hassan 2019 方法论):
      相关矩阵帮助判断 fintech tone 与 non-fintech coverage 之间的线性关联程度。
      如果两者高度相关 (|r| > 0.7), 则伪造检验的区分效力可能减弱。
      理想情况下 |r| < 0.3, 表明两组指标捕获了不同的信息维度。

    同时参考 Tetlock (2007, JF, 62(3), 1139-1168):
      新闻量 (volume) 和情感内容 (content) 是两个概念上独立的维度,
      volume 衡量关注度, content 衡量正/负面倾向。
    """
    logger.info("=" * 70)
    logger.info("步骤 5: 诊断报告 — 相关矩阵")
    logger.info("=" * 70)
    logger.info("  目的: 检验 fintech 情感指标与 non-fintech 新闻量之间的相关性。")
    logger.info("  理论基础:")
    logger.info(f"    {REFERENCES['Tetlock2007']}")
    logger.info(f"    → Tetlock (2007) 指出新闻 volume 和 content 是独立维度。")
    logger.info(f"    → 如果 |r(tone, nf_coverage)| 较低, 支持 H1。")

    # 选取核心变量
    diag_cols = []
    for c in ['llm_vote_tone_full', 'llm_vote_tone_ctx',
              'dict_avg_tone_full', 'bert_avg_pos_full']:
        if c in panel.columns:
            diag_cols.append(c)
    for c in ['nf_ln_coverage', 'nf_media_breadth', 'nf_headline_frac']:
        if c in panel.columns:
            diag_cols.append(c)
    for c in ['all_ln_coverage', 'fintech_share', 'n_articles']:
        if c in panel.columns:
            diag_cols.append(c)

    if len(diag_cols) < 2:
        logger.warning("  ⚠️ 可用诊断列不足, 跳过相关矩阵")
        return None

    # 仅保留有新闻的行
    mask = panel['all_n_articles'] > 0
    diag_df = panel.loc[mask, diag_cols].dropna()

    logger.info(f"")
    logger.info(f"  用于相关分析的有效观测数: {len(diag_df):,}")
    logger.info(f"  排除的零新闻行: {(~mask).sum():,}")
    logger.info(f"  分析变量: {diag_cols}")

    # Pearson
    pearson = diag_df.corr(method='pearson')
    logger.info("")
    logger.info("  ─── Pearson 相关矩阵 (线性相关) ───")
    for line in pearson.to_string().split('\n'):
        logger.info(f"  {line}")

    # Spearman
    spearman = diag_df.corr(method='spearman')
    logger.info("")
    logger.info("  ─── Spearman 相关矩阵 (秩相关) ───")
    for line in spearman.to_string().split('\n'):
        logger.info(f"  {line}")

    # 自动解读
    logger.info("")
    logger.info("  ─── 自动解读 (基于 Pearson 系数) ───")
    for c in ['nf_ln_coverage', 'nf_media_breadth']:
        if c not in pearson.columns:
            continue
        for tone_col in ['llm_vote_tone_full', 'dict_avg_tone_full']:
            if tone_col not in pearson.columns:
                continue
            r = pearson.loc[tone_col, c]
            r_abs = abs(r)
            if r_abs < 0.3:
                logger.info(f"  ✅ r({tone_col}, {c}) = {r:.4f}")
                logger.info(f"     |r| = {r_abs:.4f} < 0.30 → 弱相关")
                logger.info(f"     解读: 金融科技情感与非金融科技新闻量相对独立,")
                logger.info(f"           支持 H1 (fintech tone 具有特异性信息)。")
            elif r_abs < 0.7:
                logger.info(f"  ℹ️  r({tone_col}, {c}) = {r:.4f}")
                logger.info(f"     |r| = {r_abs:.4f} ∈ [0.30, 0.70) → 中等相关")
                logger.info(f"     解读: 存在一定关联,Stata 回归中应同时控制 non-fintech 变量。")
            else:
                logger.info(f"  ⚠️ r({tone_col}, {c}) = {r:.4f}")
                logger.info(f"     |r| = {r_abs:.4f} ≥ 0.70 → 高度相关")
                logger.info(f"     解读: 需警惕多重共线性,可能削弱赛马回归的区分效力。")

    # ── 挤出弹性相关性校验 (方案断言 4) ──
    if 'ln_ft_articles' in panel.columns and 'ln_nf_articles' in panel.columns:
        valid_pair = panel[['ln_ft_articles', 'ln_nf_articles']].dropna()
        if len(valid_pair) >= 2:
            r_elast = valid_pair.corr().iloc[0, 1]
            logger.info("")
            logger.info("  ─── 挤出弹性校验 ───")
            logger.info(f"  r(ln_ft, ln_nf) = {r_elast:.4f}")
            if r_elast < -0.95:
                logger.error("  ✗ r < -0.95: 疑似机械关联, "
                             "百分比约束未被对数变换消除!")
            elif r_elast < -0.5:
                logger.warning(f"  ⚠️ r ∈ (-0.95, -0.50): 中等负相关, "
                               f"回归中应注意共线性")
            else:
                logger.info(f"  ✓ r > -0.50: 非机械关联, "
                            f"对数弹性策略有效")

    return pearson


# ============================================================================
# 7. 导出
# ============================================================================

def export_results(panel: pd.DataFrame, pearson_corr: pd.DataFrame):
    """多格式导出。"""
    logger.info("=" * 70)
    logger.info("步骤 6: 多格式导出")
    logger.info("=" * 70)

    # Parquet
    output_filename = FILENAMES.get(
        'output_51_panel_controls', '51_panel_with_controls.parquet'
    )
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    input_file = os.path.join(cfg['paths']['output_dir'],
                              cfg['filenames']['output_40_panel_yearly'])
    save_dataset(panel, output_path, logger,
                stage_name="51_falsification_test",
                config=cfg,
                input_files=[input_file])

    # Stata .dta
    dta_path = os.path.splitext(output_path)[0] + '.dta'
    logger.info(f"  正在生成 Stata .dta 文件...")
    logger.info(f"    说明: Stata 列名不支持中文和特殊字符,")
    logger.info(f"          将自动清理列名 (去除中文、替换括号、截断32字符)。")
    try:
        panel_stata = panel.copy()
        # v6/F2 Stata 兼容: pandas Int*/boolean nullable → Float64 (NaN 保留)
        for _col in panel_stata.select_dtypes(include=['Int8','Int16','Int32','Int64','boolean']).columns:
            panel_stata[_col] = panel_stata[_col].astype('Float64')
        clean_cols = []
        seen = {}
        for c in panel_stata.columns:
            c_clean = c.replace('(', '_').replace(')', '_')
            c_clean = c_clean.replace('（', '_').replace('）', '_')
            c_clean = re.sub(r'[^\x00-\x7F]+', '', c_clean)
            if not c_clean or not c_clean.strip('_'):
                c_clean = f'col_{len(clean_cols)}'
            c_clean = c_clean[:32]
            if c_clean in seen:
                seen[c_clean] += 1
                c_clean = f'{c_clean[:29]}_{seen[c_clean]}'
            else:
                seen[c_clean] = 1
            clean_cols.append(c_clean)
        panel_stata.columns = clean_cols
        for col in panel_stata.select_dtypes(include=['Float64', 'Int64']).columns:
            panel_stata[col] = panel_stata[col].astype(float)
        # 挤出弹性与总量变量标签
        STATA_LABELS_41 = {
            'ln_ft_articles':  'ln(1 + Fintech Articles)',
            'ln_nf_articles':  'ln(1 + Non-Fintech Articles)',
            'fintech_share':   'Fintech News Share',
            # 银行注册地 (步骤 40 的 7c 生成)
            'bank_province':               'Bank HQ Province',
            'bank_city':                   'Bank HQ City',
            # Leave-one-out 情感 IV (步骤 40 的 7d 生成)
            # 用途: ivreghdfe Y (tone = prov_leave1out_tone_full) X, ...
            'prov_leave1out_tone_full':     'Prov Leave-1-Out Tone (Full)',
            'prov_leave1out_tone_ctx':      'Prov Leave-1-Out Tone (Ctx)',
            'city_leave1out_tone_full':     'City Leave-1-Out Tone (Full)',
            'city_leave1out_tone_ctx':      'City Leave-1-Out Tone (Ctx)',
            # 治理约束型合约 (Zhou et al., 2026, JBR §2.1; Core et al. 2003)
            'GOV_equity_ratio':             'Equity Comp / Total Comp Ratio',
            'GOV_cash_ratio':               'Cash Comp / Total Comp Ratio',
            'GOV_top3_pay_gap':             'ln(Top3 Exec Pay / Avg Emp Pay)',
            'GOV_esg_kpi':                  'ESG-KPI in Exec Comp (0/1)',
            'GOV_board_indep':              'Independent Director Ratio',
            'GOV_dual_chair':               'CEO-Chair Duality (0/1)',
            'GOV_comp_committee':           'Compensation Committee (0/1)',
            'GOV_ceo_tenure':               'CEO Tenure (Years)',
        }
        labels_41 = {k: v for k, v in STATA_LABELS_41.items()
                     if k in panel_stata.columns}
        panel_stata.to_stata(dta_path, write_index=False, version=118,
                             variable_labels=labels_41)
        logger.info(f"  ✓ 已导出 Stata 文件: {dta_path}")
        logger.info(f"    Stata 列数: {len(clean_cols)}")
    except Exception as e:
        logger.warning(f"  ⚠️ Stata 导出失败: {e}")

    # 相关矩阵 CSV
    if pearson_corr is not None:
        diag_path = os.path.join(OUTPUT_DIR, '51_falsification_diagnostics.csv')
        pearson_corr.to_csv(diag_path)
        logger.info(f"  ✓ 已导出诊断文件: {diag_path}")


# ============================================================================
# 8. Stata 回归模板
# ============================================================================

def print_stata_template():
    """在日志中输出 Stata 回归模板。"""
    logger.info("=" * 70)
    logger.info("步骤 7: Stata 回归模板")
    logger.info("=" * 70)
    logger.info("")
    logger.info("  ─── 方法论说明 ───")
    logger.info(f"  本模板对标: {REFERENCES['Hassan2019']}")
    logger.info(f"  → Table 7: PRisk vs NPRisk 非对称预测检验")
    logger.info(f"")
    logger.info(f"  核心思想 (Tetlock 2007, JF):")
    logger.info(f"    新闻量 (volume) 和情感内容 (content) 是不同维度。")
    logger.info(f"    如果 tone 仅仅是 volume 的代理变量,")
    logger.info(f"    控制 volume 后 tone 的系数应变得不显著。")
    logger.info(f"    反之,如果 tone 保持显著,则证明其包含独立的增量信息。")

    template_path = (
        Path(__file__).resolve().parents[2]
        / 'papers_assets' / 'bank_fintech_tone' / 'do'
        / 'falsification_template.do.tmpl'
    )
    if not template_path.exists():
        logger.error(f"Stata 模板文件未找到: {template_path}")
        return

    template = template_path.read_text(encoding='utf-8')
    for line in template.strip().splitlines():
        logger.info(f"  {line}")


# ============================================================================
# 9. 参考文献汇总
# ============================================================================

def print_references():
    """在日志中输出完整参考文献列表。"""
    logger.info("=" * 70)
    logger.info("参考文献 (完整引用)")
    logger.info("=" * 70)
    for key, ref in REFERENCES.items():
        logger.info(f"  [{key}] {ref}")


# ============================================================================
# G-13: Placebo 时点检验
# ============================================================================
# 学术依据:
#   Hassan et al. (2019, QJE, Table 7):
#     通过构造 placebo 政策时点 (将真实处理年份提前 k 年),
#     检验处理效应是否在真实政策实施前就已存在。
#     若 placebo 效应显著 → 平行趋势假设可能违反。
#
#   Callaway & Sant'Anna (2021, JoE, §4.3):
#     "Pre-treatment placebo tests are essential for validating
#      the parallel trends assumption in staggered DID."
# ============================================================================

def generate_placebo_did_variables(panel: pd.DataFrame,
                                   placebo_shifts: list = None,
                                   logger_inst=None) -> pd.DataFrame:
    """G-13: 构建 Placebo 时点 DID 变量。

    对面板中每个 DID 政策冲击, 将 treat_year 提前 k 年 (k ∈ placebo_shifts),
    生成伪处理变量 {prefix}_placebo{k}_post, 供回归检验使用。

    参数:
        panel:           Bank-Year 面板 (须已包含 {prefix}_treat_year 列)
        placebo_shifts:  提前年数列表 (默认 [1, 2, 3])
        logger_inst:     日志实例

    新增列 (每个政策 × 每个 shift):
        {prefix}_placebo{k}_post:  伪政策后哑变量
        {prefix}_placebo{k}_did:   伪 DID 交互项 (treated × placebo_post)

    Stata 用法:
      * 检验 placebo DID 是否显著 (应不显著):
        reghdfe Y dcep_placebo2_did X, absorb(bank_id year) cluster(bank_id)
      * 若显著 → 平行趋势假设可能违反, 需关注

    返回:
        panel: 附加 placebo DID 变量的 DataFrame
    """
    lg = logger_inst or logger
    if placebo_shifts is None:
        placebo_shifts = [1, 2, 3]

    lg.info("=" * 70)
    lg.info("G-13: Placebo 时点检验变量生成")
    lg.info("  对标: Hassan et al. (2019, QJE, Table 7)")
    lg.info("  对标: Callaway & Sant'Anna (2021, JoE, §4.3)")
    lg.info(f"  Placebo shifts: {placebo_shifts} (提前 k 年)")
    lg.info("=" * 70)

    # 找到所有 DID 政策前缀
    treat_year_cols = [c for c in panel.columns if c.endswith('_treat_year')]
    if not treat_year_cols:
        lg.warning("  未找到 *_treat_year 列, 跳过 Placebo 检验")
        return panel

    for ty_col in treat_year_cols:
        prefix = ty_col.replace('_treat_year', '')

        for k in placebo_shifts:
            # 伪治疗年份 = 真实治疗年份 - k
            placebo_ty = np.where(
                panel[ty_col] > 0,
                panel[ty_col] - k,
                0
            )

            # 伪政策后哑变量
            plac_post_col = f'{prefix}_placebo{k}_post'
            panel[plac_post_col] = np.where(
                placebo_ty > 0,
                (panel['year'] >= placebo_ty).astype(int),
                0
            )

            # 伪 DID 交互项
            plac_did_col = f'{prefix}_placebo{k}_did'
            treated_col = f'{prefix}_treated'
            if treated_col in panel.columns:
                panel[plac_did_col] = (
                    panel[treated_col] * panel[plac_post_col]
                )
            else:
                panel[plac_did_col] = 0

            n_treated_plac = (panel[plac_did_col] == 1).sum()
            lg.info(f"  {plac_did_col}: treated×post = {n_treated_plac}")

        # Stata 命令建议
        lg.info(f"  ── {prefix} Placebo Stata 命令 ──")
        for k in placebo_shifts:
            lg.info(f"    reghdfe Y {prefix}_placebo{k}_did X, "
                    f"absorb(bank_id year) cluster(bank_id)")
        lg.info(f"    * 预期: 所有 placebo DID 系数应不显著 (p > 0.10)")
        lg.info(f"    * 若显著: 平行趋势假设可能不成立")

    return panel


# ============================================================================
# G-09: 金融科技分类外部交叉验证诊断
# ============================================================================
# 学术依据:
#   胡俊, 李强, 戴嘉诚, & 曾勇 (2024, 中国管理科学 32(1):31-41): 银行金融科技关键词测度
#   Gentzkow et al. (2019, JEL): "Text as Data" — 测度有效性验证
# ============================================================================

def diagnose_fintech_classification_consistency(panel: pd.DataFrame,
                                                 logger_inst=None) -> dict:
    """G-09: 诊断金融科技分类指标的内部一致性。

    在无外部数据源的情况下, 通过面板内部指标间的相关性
    检验金融科技分类的收敛有效性 (convergent validity):
      1. tech_frac vs fintech_article_count: 应高度正相关
      2. tech_frac vs LLM 情感: 应有合理的相关模式
      3. 年度均值趋势: 应呈上升趋势 (金融科技投入逐年增加)

    返回:
        dict: 诊断结果
    """
    lg = logger_inst or logger

    lg.info("=" * 70)
    lg.info("G-09: 金融科技分类内部一致性诊断")
    lg.info("  对标: Gentzkow et al. (2019, JEL §3): 测度收敛有效性")
    lg.info("=" * 70)

    result = {}

    # (1) tech_frac vs n_articles 相关性
    if 'tech_frac' in panel.columns and 'n_articles' in panel.columns:
        valid = panel[['tech_frac', 'n_articles']].dropna()
        if len(valid) > 10:
            corr = valid['tech_frac'].corr(valid['n_articles'])
            result['tech_frac_vs_n_articles'] = round(corr, 4)
            lg.info(f"  tech_frac × n_articles: r = {corr:.4f}"
                    f" {'✓ 正相关' if corr > 0.1 else '⚠️ 低相关'}")

    # (2) 年度均值趋势
    if 'tech_frac' in panel.columns and 'year' in panel.columns:
        trend = panel.groupby('year')['tech_frac'].mean()
        result['yearly_trend'] = trend.to_dict()
        lg.info(f"  tech_frac 年度均值趋势:")
        for y, v in trend.items():
            lg.info(f"    {y}: {v:.4f}")

        # 简单线性趋势检验 (年份与均值的相关性)
        if len(trend) >= 3:
            years = np.array(list(trend.index), dtype=float)
            vals = np.array(list(trend.values), dtype=float)
            if np.std(years) > 0 and np.std(vals) > 0:
                trend_corr = np.corrcoef(years, vals)[0, 1]
                result['trend_correlation'] = round(trend_corr, 4)
                lg.info(f"  时间趋势相关系数: r = {trend_corr:.4f}"
                        f" {'✓ 上升趋势' if trend_corr > 0.3 else '⚠️ 无明显趋势'}")

    # (3) 外部验证建议
    lg.info("  ── 外部验证建议 (如有数据可用) ──")
    lg.info("    * 与北大数字金融普惠指数 (Peking University DFIIC) 相关性分析")
    lg.info("    * 与各银行年报中 '金融科技' 章节词频的 Pearson/Spearman 相关")
    lg.info("    * 与银保监会金融科技监管评级 (如有) 的序数相关")

    return result


# ============================================================================
# G-11: 别名系统精确率-召回率定量报告
# ============================================================================
# 学术依据: 标准分类评估 (Precision / Recall / F1)
# ============================================================================

def diagnose_alias_matching_quality(panel: pd.DataFrame,
                                     logger_inst=None) -> dict:
    """G-11: 别名系统匹配质量诊断。

    通过面板中的匹配统计间接评估别名系统的质量:
      1. 银行覆盖率: 有多少银行至少匹配到 1 篇文章
      2. 匹配浓度: 每家银行的年均文章数分布 (检测异常值)
      3. 零匹配年份: Bank-Year 中无文章的观测比例

    返回:
        dict: 诊断结果
    """
    lg = logger_inst or logger

    lg.info("=" * 70)
    lg.info("G-11: 别名匹配质量诊断")
    lg.info("=" * 70)

    result = {}

    if 'n_articles' not in panel.columns:
        lg.warning("  n_articles 列不存在, 跳过诊断")
        return result

    # (1) 银行覆盖率
    bank_has_articles = panel.groupby('target_bank')['n_articles'].sum() > 0
    n_covered = bank_has_articles.sum()
    n_total = len(bank_has_articles)
    result['bank_coverage'] = f"{n_covered}/{n_total}"
    lg.info(f"  银行覆盖率: {n_covered}/{n_total} "
            f"({n_covered/max(n_total,1)*100:.1f}%)")

    # (2) 匹配浓度
    bank_avg = panel.groupby('target_bank')['n_articles'].mean()
    result['articles_per_bank_mean'] = round(bank_avg.mean(), 2)
    result['articles_per_bank_median'] = round(bank_avg.median(), 2)
    result['articles_per_bank_p95'] = round(bank_avg.quantile(0.95), 2)
    lg.info(f"  年均文章数: mean={bank_avg.mean():.1f}, "
            f"median={bank_avg.median():.1f}, "
            f"P95={bank_avg.quantile(0.95):.1f}")

    # (3) 异常值检测 (>3σ)
    threshold = bank_avg.mean() + 3 * bank_avg.std()
    outliers = bank_avg[bank_avg > threshold]
    if len(outliers) > 0:
        result['outlier_banks'] = list(outliers.index[:5])
        lg.info(f"  ⚠️ 高匹配异常值 (>3σ={threshold:.0f}): "
                f"{list(outliers.index[:5])}")
    else:
        lg.info(f"  ✓ 无高匹配异常值 (3σ={threshold:.0f})")

    # (4) 零匹配年份比例
    zero_pct = (panel['n_articles'] == 0).sum() / max(len(panel), 1)
    result['zero_article_pct'] = round(zero_pct, 4)
    lg.info(f"  零匹配 Bank-Year: {(panel['n_articles']==0).sum()}/{len(panel)} "
            f"({zero_pct*100:.1f}%)")
    if zero_pct > 0.5:
        lg.info(f"  ⚠️ 零匹配比例较高, 建议检查关键词阈值或银行名称覆盖度")

    return result


# ============================================================================
# 主流程
# ============================================================================

def main():
    """51_falsification_test 主流程。"""
    start_time = time.time()
    logger.info("=" * 70)
    logger.info("===  51_falsification_test: 伪造检验对照变量构建  ===")
    logger.info("=" * 70)
    logger.info("")
    logger.info("  假设检验框架:")
    logger.info("    H0: fintech tone 的解释力完全来自银行层面一般媒体关注度")
    logger.info("    H1: fintech tone 包含金融科技维度的特异性增量信息")
    logger.info("")
    logger.info("  核心方法论:")
    logger.info(f"    {REFERENCES['Hassan2019']}")
    logger.info(f"    → Table 7: 通过 PRisk vs NPRisk 的非对称预测验证构造效度")

    # 1-7. 主流程
    df_full, df_art, panel = load_data()
    df_nf = build_non_fintech(df_full, df_art)
    nf_agg = aggregate_non_fintech(df_nf)
    panel = merge_to_panel(panel, nf_agg)
    pearson_corr = run_diagnostics(panel)
    export_results(panel, pearson_corr)
    print_stata_template()
    print_references()

    # 阶段摘要
    log_stage_summary(
        logger, STAGE_NAME, start_time,
        input_rows=len(df_full),
        output_rows=len(panel),
        extra_info={
            '新增控制变量': 'nf_n_articles, nf_ln_coverage, nf_media_breadth, '
                           'nf_headline_frac, all_n_articles, all_ln_coverage, '
                           'fintech_share',
            '面板列数': panel.shape[1],
        }
    )

    logger.info("51_falsification_test 执行完毕 ✓")


if __name__ == '__main__':
    main()
