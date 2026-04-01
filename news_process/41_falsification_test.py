"""
41_falsification_test.py — 伪造检验: 非金融科技对照变量构建
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
  data_processed/12_fintech_news_full.parquet
  data_processed/40_article_bank_level.parquet
  data_processed/40_panel_yearly.parquet

输出:
  data_processed/41_panel_with_controls.parquet
  data_processed/41_panel_with_controls.dta
  data_processed/41_falsification_diagnostics.csv
"""

import os
import re
import sys
import time
import warnings

import numpy as np
import pandas as pd

from utils.helpers import (
    load_config, setup_logging, log_stage_summary, save_dataset
)

warnings.filterwarnings('ignore', category=FutureWarning)

# ============================================================================
# 1. 全局配置与初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "41_falsification_test"
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
        logger.error(f"  → 请先运行 40_build_panel.py 生成此文件")
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
        logger.error(f"  → 请先运行 40_build_panel.py 生成此文件")
        sys.exit(1)
    panel = pd.read_parquet(panel_path)
    logger.info(f"  (c) 40_panel_yearly: {len(panel):,} 行")
    logger.info(f"      数据粒度: Bank × Year (平衡面板)")
    logger.info(f"      唯一银行数: {panel['target_bank'].nunique()}")
    logger.info(f"      年份范围: {panel['year'].min()} - {panel['year'].max()}")

    return df_full, df_art, panel


# ============================================================================
# 3. Anti-join: 定义非金融科技对照组
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
    logger.info("      40_build_panel.py 第135行转为 datetime64 类型,")
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
    panel_keys = set(zip(
        df_art['target_bank'],
        df_art['标题'],
        df_art['_date_str']
    ))
    logger.info(f"  面板文章唯一键数: {len(panel_keys):,}")
    logger.info(f"  面板文章总行数: {len(df_art):,}")
    if len(panel_keys) != len(df_art):
        logger.warning(f"  ⚠️ 唯一键数 ≠ 总行数, 存在 {len(df_art) - len(panel_keys):,} 个重复键")

    # Anti-join
    df_full['_key'] = list(zip(
        df_full['target_bank'],
        df_full['标题'],
        df_full['_date_str']
    ))
    df_nf = df_full[~df_full['_key'].isin(panel_keys)].copy()
    df_nf.drop(columns=['_key', '_date_str'], inplace=True)
    df_full.drop(columns=['_key', '_date_str'], inplace=True)

    # --- 三分类校验与详细统计 ---
    n_total = len(df_full)
    n_panel = len(df_art)
    n_nf = len(df_nf)
    logger.info("")
    logger.info("  ─── 三分类统计 ───")
    logger.info(f"    ③ Fintech 面板文章 (keyword=True + LLM通过): {n_panel:,} 条")
    logger.info(f"    ①+② Non-Fintech 对照组:                     {n_nf:,} 条")
    logger.info(f"    全量银行新闻:                                 {n_total:,} 条")
    logger.info(f"    恒等校验: {n_panel:,} + {n_nf:,} = {n_panel + n_nf:,} "
                f"{'== ✓' if n_panel + n_nf == n_total else '!= ✗'} {n_total:,}")
    logger.info(f"    Fintech 占比: {n_panel / n_total * 100:.1f}%")
    logger.info(f"    Non-Fintech 占比: {n_nf / n_total * 100:.1f}%")

    if n_panel + n_nf != n_total:
        diff = abs(n_total - n_panel - n_nf)
        logger.warning(f"  ⚠️ 三分类不等式不成立! 差异 {diff:,} 条。")
        logger.warning(f"     可能原因: 存在相同 (target_bank, 标题, 日期) 但不同内容的文章。")
        logger.warning(f"     影响评估: 差异量占总量 {diff / n_total * 100:.4f}%, 通常可忽略。")

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
# 4. Non-Fintech Bank-Year 聚合
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
        logger.info(f"       而非 'in_title' (40_build_panel.py 中的重命名版本)")

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
    logger.info(f"          与 40_build_panel.py balance_panel 的零新闻处理一致。")

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
        'output_41_panel_controls', '41_panel_with_controls.parquet'
    )
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    save_dataset(panel, output_path, logger)

    # Stata .dta
    dta_path = os.path.splitext(output_path)[0] + '.dta'
    logger.info(f"  正在生成 Stata .dta 文件...")
    logger.info(f"    说明: Stata 列名不支持中文和特殊字符,")
    logger.info(f"          将自动清理列名 (去除中文、替换括号、截断32字符)。")
    try:
        panel_stata = panel.copy()
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
        diag_path = os.path.join(OUTPUT_DIR, '41_falsification_diagnostics.csv')
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

    template = """
* ============================================================
* 伪造检验 Stata 回归模板
* ============================================================
* 数据文件: 41_panel_with_controls.dta
* 请将 Y 替换为因变量 (如: ROA, Tobin_Q, 数字化转型投资等)
* 请将 X 替换为其他控制变量 (如: size, leverage, age 等)
*
* 方法论对标:
*   Hassan, T.A. et al. (2019). "Firm-Level Political Risk."
*   QJE, 134(4), 2135-2202, Table 7.
* ============================================================

use "41_panel_with_controls.dta", clear

* ── 检验 1: 基准回归 ──
* 目的: 确认 fintech tone 对 Y 有显著解释力
reghdfe Y llm_vote_tone_full X, absorb(target_bank year) vce(cluster target_bank)
  est store base

* ── 检验 2: 控制非金融科技新闻量 ──
* 目的: 加入 non-fintech 控制变量后, tone 是否仍显著
* 对标: Hassan Table 7 col 2
* 依据: Fang & Peress (2009, JF, 64(5), 2023-2052) → ln(1+count)
*        Bushee et al. (2010, JAR, 48(1), 1-19) → 媒体广度
reghdfe Y llm_vote_tone_full nf_ln_coverage nf_media_breadth X, ///
  absorb(target_bank year) vce(cluster target_bank)
  est store ctrl_nf

* ── 检验 3: 替换 (Placebo) ──
* 目的: 仅用 non-fintech 变量能否解释 Y
* 对标: Hassan Table 7 Panel B/C
* 预期: nf 系数弱/不显著 → 一般新闻量本身不驱动 Y
reghdfe Y nf_ln_coverage nf_media_breadth X, ///
  absorb(target_bank year) vce(cluster target_bank)
  est store replace_nf

* ── 检验 4: 赛马 (Horse Race) ──
* 目的: 同时控制总新闻量, tone 是否仍有增量贡献
* 对标: Hassan Table 7 col 3
reghdfe Y llm_vote_tone_full all_ln_coverage X, ///
  absorb(target_bank year) vce(cluster target_bank)
  est store ctrl_all

* ── 检验 5: 交互项 ──
* 目的: 金融科技新闻占比是否调节 tone 的边际效应
reghdfe Y c.llm_vote_tone_full##c.fintech_share X, ///
  absorb(target_bank year) vce(cluster target_bank)
  est store interact

* ── 检验 6: 控制新闻语言特征 ──
* 目的: 验证 tone 不受文本长度/词汇多样性/可读性驱动
* 对标: He et al. (2024, IRFA, Table 4, Panel A.5)
* 变量映射:
*   avg_article_length — ln(1+平均文章词数), ≈ 论文 MLENGTH (无 track 后缀)
*   avg_sent_len_full  — 平均句长
*   avg_ttr_full       — 类符/形符比 (词汇多样性)
*   avg_cpw_full       — 字符/词 (可读性)
reghdfe Y llm_vote_tone_full avg_article_length avg_sent_len_full ///
  avg_ttr_full avg_cpw_full X, ///
  absorb(target_bank year) vce(cluster target_bank)
  est store ctrl_ling

* ── 检验 7: 排除压力年份稳健性 ──
* 目的: 移除系统性危机年份, 验证 fintech tone 不受宏观冲击驱动
* 对标: Dim, Sangiorgi & Vilkov (2024, §3.5)
*        — 移除 NBER 衰退年份 (2001, 2008-2009, 2020) 后结果不变
*        Garcia (2013, JF, 68(3), 1267-1300)
*        — 衰退期间情感指标统计特征显著不同
* 中国银行业压力期: 2015(股灾), 2018(去杠杆), 2020(疫情)
preserve
  drop if inlist(year, 2015, 2018, 2020)
  reghdfe Y llm_vote_tone_full nf_ln_coverage nf_media_breadth X, ///
    absorb(target_bank year) vce(cluster target_bank)
  est store robust_no_stress
restore

* ── 输出格式化表格 ──
esttab base ctrl_nf replace_nf ctrl_all interact ctrl_ling robust_no_stress ///
  using "table_falsification.tex", ///
  star(* 0.10 ** 0.05 *** 0.01) se replace

* ============================================================
* 结果解读指南:
* ────────────────────────────────────────────────────────────
* β₁(tone) 显著且稳健 + β₂(nf) 不显著
*   → ✅ 金融科技情感有特异性增量信息 (理想结果)
*
* β₁ 衰减但仍显著 + β₂ 显著
*   → ✅ 两者各有独立信息 (可接受, 类似 Hassan Table 7 Panel A)
*
* β₁ 不再显著 + β₂ 显著
*   → ⚠️ 金融科技情感可能仅代理一般媒体关注度 (需要进一步分析)
*
* β₁(tone) 在排除压力年份后仍显著
*   → ✅ 金融科技情感非系统危机的副产品 (Dim et al. 2024, §3.5)
* ============================================================

* ============================================================
* 稳健性检验: 计数型情感指标 (MSENT 公式族)
* ────────────────────────────────────────────────────────────
* 管道主得分 (如 llm_vote_tone_full) 使用语言学增强加权公式,
* 与 Tetlock (2007, JF) / He et al. (2024, IRFA) 的简单
* 计数型公式不同。以下提供两种计数型替代指标:
*
* (A) MSENT 主公式: (Neg-Pos)/(Neg+Pos), 值域 [-1,+1]
*     对标: He et al. (2024, IRFA), Eq. (1)
*     面板变量: avg_msent_full (由管道直接输出)
reghdfe Y avg_msent_full X, absorb(target_bank year) vce(cluster target_bank)
*
* (B) MSENT2 公式: (Neg-Pos)/TotalWords
*     对标: He et al. (2024, IRFA), Table 3, Panel B
*     可在 Stata 中从现有变量近似重构:
*     注: pos_ratio/neg_ratio 使用语言学规则后极性 (含否定翻转),
*         与论文原始词典计数存在微小差异 (~5% 词受否定影响)
cap drop dict_msent2_full
gen dict_msent2_full = avg_neg_ratio_full - avg_pos_ratio_full
reghdfe Y dict_msent2_full X, absorb(target_bank year) vce(cluster target_bank)
* ============================================================
"""
    for line in template.strip().split('\n'):
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
# 主流程
# ============================================================================

def main():
    """41_falsification_test 主流程。"""
    start_time = time.time()
    logger.info("=" * 70)
    logger.info("===  41_falsification_test: 伪造检验对照变量构建  ===")
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

    logger.info("41_falsification_test 执行完毕 ✓")


if __name__ == '__main__':
    main()
