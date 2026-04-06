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
  data_processed/12_fintech_news_full.parquet
  data_processed/40_article_bank_level.parquet
  data_processed/40_panel_yearly.parquet

输出:
  data_processed/51_panel_with_controls.parquet
  data_processed/51_panel_with_controls.dta
  data_processed/51_falsification_diagnostics.csv
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
            # 银行注册地 (步骤 40 的 7c 生成)
            'bank_province':               'Bank HQ Province',
            'bank_city':                   'Bank HQ City',
            # Leave-one-out 情感 IV (步骤 40 的 7d 生成)
            # 用途: ivreghdfe Y (tone = prov_leave1out_tone_full) X, ...
            'prov_leave1out_tone_full':     'Prov Leave-1-Out Tone (Full)',
            'prov_leave1out_tone_ctx':      'Prov Leave-1-Out Tone (Ctx)',
            'city_leave1out_tone_full':     'City Leave-1-Out Tone (Full)',
            'city_leave1out_tone_ctx':      'City Leave-1-Out Tone (Ctx)',
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

    template = """
* ============================================================
* 伪造检验 Stata 回归模板
* ============================================================
* 数据文件: 51_panel_with_controls.dta
* 请将 Y 替换为因变量 (如: ROA, Tobin_Q, 数字化转型投资等)
* 请将 X 替换为其他控制变量 (如: size, leverage, age 等)
*
* 方法论对标:
*   Hassan, T.A. et al. (2019). "Firm-Level Political Risk."
*   QJE, 134(4), 2135-2202, Table 7.
* ============================================================

use "51_panel_with_controls.dta", clear

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

* ── 检验 5b: 外部经济环境调节效应 ──
* 目的: 检验外部环境变量 M 是否调节 tone → Y 的传导机制
* 对标: Qu & Yang (2025, §4.3, Eq. 3)
*       Finratio1 × mediasen 交互项检验金融服务的调节效应
*
* 理论逻辑:
*   情感 → 行为 的传导可能取决于外部环境:
*   (1) 金融服务环境: 融资渠道畅通时, 乐观情感更易转化为投资
*   (2) 数字金融环境: 数字普惠金融发达地区, 信息传导更高效
*   (3) 融资约束: 约束严重的企业对负面情感更敏感
*
* 推荐调节变量 M 的候选 (用户需从 CSMAR/Wind/PKU-DFIIC 获取):
*   DFIIC      — 北大数字普惠金融指数 (地级市级)
*               郭峰等 (2020, 经济学(季刊), 19(4), 1401-1418)
*   SA_index   — SA 融资约束指数
*               Hadlock & Pierce (2010, RFS, 23(5), 1909-1940)
*   Finratio1  — 金融服务便利度综合指数 (Qu & Yang 2025, 熵权法)
*   MKT_index  — 市场化指数 (省级)
*               王小鲁、樊纲、胡李鹏 (2021, 《中国分省份市场化指数报告》)
*
* 注: 以下使用 M 作为通用占位符, 请替换为实际变量名 (DFIIC/SA_index/...)
*
* ⚠️ 技术要求 (Brambor, Clark & Golder 2006, PA):
*   交互项回归中, 主效应 tone 和 M 必须同时进入模型,
*   否则交互项系数估计有偏。Stata 的 ## 语法自动满足此要求。
*
* ⚠️ 变量重复声明警告:
*   ## 语法会自动将 M 作为主效应纳入。如果 M 已在 X 中,
*   须从 X 中移除 M, 否则因完美共线性导致估计失败。
*   例: X 定义为 "Size Lev ROA" 而非 "Size Lev ROA M"
*
* ⚠️ 中心化建议: 当 M 的均值远离 0 时,
*   交互项可能产生 VIF 膨胀。建议先去均值:
*   egen M_c = std(M)  // 标准化 (均值=0, 标准差=1)
*   或 sum M → gen M_c = M - r(mean)  // 仅去均值

* (5b-1) 连续型调节变量
reghdfe Y c.llm_vote_tone_full##c.M X, ///
  absorb(target_bank year) vce(cluster target_bank)
  est store moderate_cont

* (5b-2) 虚拟型调节变量 (适用于阈值型机制)
* cap drop M_high
* sum M, detail
* gen M_high = (M >= r(p50)) if !missing(M)
*   // ⚠️ if !missing(M) 防止缺失值被归入高组 (同 7b 缺失值陷阱)
* reghdfe Y c.llm_vote_tone_full##i.M_high X, ///
*   absorb(target_bank year) vce(cluster target_bank)
*   est store moderate_dum

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

* ── 检验 7b: 银行特征异质性分组检验 ──
* 目的: 检验 tone 的直接效应在不同银行类型间是否存在异质性
* 对标: Qu & Yang (2025, §5.7, Tables 8-9)
*       按收入增长率 / 上市年限中位数分组
*
* 方法论说明:
*   分样本回归 + 全样本交互项 — 双方法互验
*   (a) 分样本法: 直观展示各组系数大小和显著性
*   (b) 交互项法: 提供组间差异的正式统计检验
*   两者在线性模型 + 同方差假设下给出完全相同的 F 统计量
*   (Chow 1960, Econometrica, 28(3), 591-605)
*   注: 使用 vce(cluster) 时, 两种方法的点估计相同,
*   但标准误可能存在微小差异 (因子样本聚类数更少)
*
*   ⚠️ 分样本法的局限:
*     两组 β₁ 可能均显著但数值不同, 而差异实际不显著
*     → 必须配合 (b) 交互项法确认组间差异的统计显著性
*
* 推荐分组变量 Z (需从 CSMAR/Wind 获取并合并):
*   ln_total_assets — 银行规模 (大行 vs 中小行)
*   ROA            — 盈利能力 (高盈利 vs 低盈利)
*   NPL_ratio      — 不良贷款率 (高 vs 低)
*   listing_age    — 上市年限 (长 vs 短, 直接对标论文 H5)
*
* 注: 以下使用 Z 作为通用占位符, 请替换为实际变量名

* ── 动态中位数计算 (避免硬编码) ──
sum Z, detail
local med_Z = r(p50)

* ── (7b-a) 分样本法 ──
* 注: local 宏在 preserve/restore 内仍可访问 (不随数据恢复而丢失)
*
* ⚠️ Stata 缺失值陷阱:
*   Stata 中 missing (.) 被视为正无穷大.
*   因此 `Z >= med_Z` 在 Z 缺失时为 TRUE,
*   会将缺失值观测错误归入高组.
*   → 必须显式排除: & !missing(Z)

preserve
  keep if Z >= `med_Z' & !missing(Z)
  reghdfe Y llm_vote_tone_full X, ///
    absorb(target_bank year) vce(cluster target_bank)
  est store het_high
restore

preserve
  keep if Z < `med_Z' & !missing(Z)
  reghdfe Y llm_vote_tone_full X, ///
    absorb(target_bank year) vce(cluster target_bank)
  est store het_low
restore

* ── (7b-b) 全样本交互项法 (正式统计检验) ──
cap drop Z_high
gen Z_high = (Z >= `med_Z') if !missing(Z)
* 注: if !missing(Z) 使 Z 缺失时 Z_high = . (而非 1)
*     reghdfe 自动排除 Z_high 为缺失的观测
reghdfe Y c.llm_vote_tone_full##i.Z_high X, ///
  absorb(target_bank year) vce(cluster target_bank)
  est store het_chow
* → c.llm_vote_tone_full#1.Z_high 的系数 = β₁(高组) - β₁(低组)
* → 该系数显著 ⇒ 组间异质性在统计上成立(Chow 1960)

* ── (7b-c) 稳健性: 三分位分组 (排除二分法阈值敏感性) ──
* xtile Z_tercile = Z, nq(3)
* reghdfe Y c.llm_vote_tone_full##i.Z_tercile X, ///
*   absorb(target_bank year) vce(cluster target_bank)
*   est store het_tercile

* ── (7b-d) 进阶: 调节效应异质性 (三重交互项) ──
* → 检验调节效应本身在不同银行类型间是否不同
*   (直接对标 Qu & Yang 2025, Tables 8-9 的精确回归设定)
* → 需同时拥有调节变量 M (检验 5b) 和分组变量 Z
* ⚠️ 样本量要求: 三重交互产生 7 个系数 (3主效应 + 3二重 + 1三重),
*   对于银行面板 (~40 家 × 15 年 ≈ 600 obs) 可能精度不足.
*   建议: N > 1000 时再尝试, 或使用 7b-a/b 的分样本法替代.
* reghdfe Y c.llm_vote_tone_full##c.M##i.Z_high X, ///
*   absorb(target_bank year) vce(cluster target_bank)
*   est store het_mod_chow
* → c.llm_vote_tone_full#c.M#1.Z_high = 调节效应的组间差异

* ============================================================
* 检验 8-10: 因果识别与地理稳健性
* ============================================================
* 背景:
*   OLS 回归 Y = β·tone + controls 中, β 的因果解读要求 tone
*   与误差项不相关。但以下两种情形下此条件被违反:
*     (1) 反向因果: 企业行为 (如 R&D 操纵) 引发媒体报道
*     (2) 遗漏变量: 不可观测的企业能力同时影响媒体关注和投资
*   检验 8 (IV) 和检验 9 (Oster) 分别从不同角度处理内生性。
*   检验 10 (地理聚类) 则验证推断对空间相关性的稳健性。
*
* 对标: Luo & Li (2025, FRL, Tables 3-4, A.2)
* ============================================================

* ── 检验 8: 工具变量回归 (IV/2SLS) ──
*
* 方法论说明:
*   工具变量 Z 须满足两个条件:
*     (i)  相关性 (relevance): Cov(Z, tone) ≠ 0
*          → 通过第一阶段 F 统计量检验, F > 10 为合格门槛
*             (Stock & Yogo 2005, JBES)
*     (ii) 排他性 (exclusion): Cov(Z, ε) = 0
*          → Z 只通过 tone 影响 Y, 不直接影响 Y
*          → 当 IV 数量 > 内生变量数量时, 可通过 Hansen J 检验
*
*   本模板提供两个维度共四个 IV:
*     维度 1 — 媒体关注度 IV (Da et al. 2011; Fang & Peress 2009):
*       ft_attn_prov / ft_attn_city
*       = 报道该银行的媒体来源地的金融科技文章占全部文章的比例
*       排他性论证: 媒体所在地区的金融科技关注度影响其报道银行时的
*                  选题倾向和行文方式 (相关性), 但一个地区的媒体生态
*                  不会直接影响被报道银行的经营决策 (排他性)
*
*     维度 2 — 情感溢出 IV (Luo & Li 2025):
*       prov_leave1out_tone_full / city_leave1out_tone_full
*       = 同省/城市其他银行的年度平均情感 (排除目标银行自身)
*       排他性论证: 同地区银行共享相同的地方媒体环境 (记者网络、
*                  编辑偏好、地方政策报道基调), 导致情感得分正相关 (相关性)。
*                  但其他银行的平均媒体情感不直接驱动目标银行的
*                  R&D 投资决策 (排他性)。
*                  → 直接对标 Luo & Li (2025) Table 3 的 Province_news_sentiment
*
* 前提: ssc install ivreghdfe

* ─── 维度 1: 媒体关注度 IV ───

* (8a) 省级关注度 IV
*   ft_attn_prov = 报道该银行的媒体来源省份的金融科技文章占比
*   第一阶段: tone_i = π·ft_attn_prov + controls + FE + v
ivreghdfe Y (llm_vote_tone_full = ft_attn_prov) X, ///
  absorb(target_bank year) cluster(target_bank) first
  est store iv_attn_prov
* 弱工具变量检验: 查看上方输出中的 Kleibergen-Paap rk Wald F > 10
*   (Stock & Yogo 2005 临界值; ivreghdfe 基于 ivreg2, 主输出自动报告)

* (8b) 城市级关注度 IV
*   ft_attn_city = 报道该银行的媒体来源城市的金融科技文章占比
*   预期: 城市级变异 > 省级变异 → 第一阶段 F 更高
ivreghdfe Y (llm_vote_tone_full = ft_attn_city) X, ///
  absorb(target_bank year) cluster(target_bank) first
  est store iv_attn_city

* ─── 维度 2: 情感溢出 IV (直接对标论文) ───

* (8c) 省级情感 IV — 精确对标 Luo & Li (2025, Table 3)
*   prov_leave1out_tone_full = 同省其他银行的年度平均情感 (排除自身)
*   构建方法: (省内所有银行 tone 总和 - 自身 tone) / (省内银行数 - 1)
*   论文原文: "Province_news_sentiment, which is the average news sentiment
*             of firms in the same province" (Luo & Li 2025, §4.1)
ivreghdfe Y (llm_vote_tone_full = prov_leave1out_tone_full) X, ///
  absorb(target_bank year) cluster(target_bank) first
  est store iv_sent_prov

* (8d) 城市级情感 IV — 城市级媒体生态的情感溢出
*   city_leave1out_tone_full = 同城市其他银行的年度平均情感 (排除自身)
*   与 8c 的区别: 城市级捕获更精细的地方媒体环境差异
*   (同一个省内不同城市的媒体生态可能显著不同)
ivreghdfe Y (llm_vote_tone_full = city_leave1out_tone_full) X, ///
  absorb(target_bank year) cluster(target_bank) first
  est store iv_sent_city

* (8e) 多 IV 过度识别检验 (Hansen J test)
*   当 IV 数量 (2) > 内生变量数量 (1) 时, 可检验排他性约束
*   H0: 所有 IV 均满足排他性 (均外生)
*   p > 0.10 → 无法拒绝 H0 → 排他性可信
*   此处使用关注度 + 情感两个不同维度的 IV
ivreghdfe Y (llm_vote_tone_full = ft_attn_prov ///
  prov_leave1out_tone_full) X, ///
  absorb(target_bank year) cluster(target_bank)
  est store iv_overid
* Hansen J 过度识别检验 p 值已在上方 ivreghdfe 主输出中报告
* (ivreghdfe 基于 ivreg2, 当 IV 数 > 内生变量数时自动报告 Hansen J)

* (8f) Distance IV — 需用户自行构建数据
*   ln_distance = ln(媒体-银行平均地理距离)
*   排他性: 距离影响报道正面偏向 (proximity bias),
*           但距离本身不影响银行投资决策
*   数据来源: bank_addresses.json 中的银行地址 + 媒体地址
*   参考: Gurun & Butler (2012, JF, 67(2), 561-598)
* ivreghdfe Y (llm_vote_tone_full = ln_distance) X, ///
*   absorb(target_bank year) cluster(target_bank)

* ── 检验 9: Oster (2019) 遗漏变量偏误检验 ──
*
* 方法论说明:
*   IV 处理可观测的内生性, 但 Oster (2019) 方法处理的是:
*   "假如存在不可观测的遗漏变量, 它们需要多大的选择效应
*   才能完全消除 tone 的回归系数?"
*
*   核心参数:
*     δ = (不可观测变量的选择效应) / (可观测控制变量的选择效应)
*     → δ > 1 意味着遗漏变量需要比所有已有控制变量组合起来
*       更强的解释力才能消除效应
*     → δ < 0 意味着加入更多控制后系数反而增大 (保守估计)
*
*     bounded set = [β̂, β*(δ=1, R_max=1.3×R²)]
*     → 如果 bounded set 不包含 0, 则即使在最悲观的遗漏变量
*       假设下, 效应仍非零
*
*   实际操作:
*     R_max = 1.3 × R²_long 是 Oster (2019, Table 1) 推荐的
*     保守设定, 假设 R² 上限为完整模型 R² 的 1.3 倍
*
* 对标: Luo & Li (2025, FRL, Table 4)
* 前提: ssc install psacalc
*
* ⚠️ 技术注意: psacalc 包仅兼容 reg/areg/xtreg 等标准回归命令,
*    不支持 reghdfe (因 e() 返回值结构不同)。
*    等价替代: areg Y ... i.year, absorb(target_bank)
*    ≡ reghdfe Y ..., absorb(target_bank year)
*    (两者计量上完全等价, 仅实现方式不同)

* 步骤 1: 短回归 (仅核心自变量 + FE, 无额外控制)
*   目的: 观察无控制变量时的系数 β_short 和 R²_short
*   注: psacalc 会内部自行计算短回归, 此步骤仅供用户
*       对比 β_short vs β_long 的衰减方向 (诊断选择偏误方向)
areg Y llm_vote_tone_full i.year, absorb(target_bank) vce(cluster target_bank)
local r2_short = e(r2)

* 步骤 2: 长回归 (核心自变量 + 全部控制变量 + FE)
*   目的: 获取加入控制后的系数和 R²
*   关键观察: |β_long| 相对 |β_short| 的变化方向表明选择偏误方向
areg Y llm_vote_tone_full X i.year, absorb(target_bank) vce(cluster target_bank)
local r2_long = e(r2)

* 步骤 3: 计算 δ 和 bounded set
*   R_max = 1.3 × R²_long (Oster 2019, JBEStat, Table 1)
psacalc delta llm_vote_tone_full, rmax(`=1.3*`r2_long'')
*   → 输出 δ 值. 解读:
*     δ < 0: 加入控制变量使系数增大, 选择性为保守方向 (较理想)
*     0 < δ < 1: 遗漏变量选择效应小于可观测变量, 不足以翻转结论
*     δ > 1: 遗漏变量需要更强效应才能消除结果, 结论较稳健
*     |δ| >> 1: 极其稳健, 遗漏变量几乎不可能消除效应
psacalc beta llm_vote_tone_full, rmax(`=1.3*`r2_long'') delta(1)
*   → 输出 β*(δ=1, R_max) — 假设遗漏变量与可观测变量选择效应
*     相同时的系数. 若 β* 与 β̂ 同号且 bounded set 不含 0, 结论稳健

* ── 检验 10: 地理层级递进聚类标准误 ──
*
* 方法论说明:
*   标准面板回归使用银行级聚类: vce(cluster target_bank)
*   但如果同省/同城市银行因共同的媒体环境导致误差项组内相关,
*   银行级聚类会低估标准误 → t 值偏高 → 虚假显著。
*
*   通过逐级提升聚类层级, 可检验系数显著性是否稳健:
*     银行级 (基准) → 城市级 (329 组) → 省级 (31 组)
*
*   ⚠️ 关键: 不能同时 absorb(target_bank bank_province)!
*   因为每家银行仅注册在一个省, bank_province 是 target_bank
*   的确定性函数, 两者间存在完美共线性。
*   正确做法: 保留原 FE 结构, 仅提升聚类层级。
*
* 对标: Luo & Li (2025, FRL, Table A.2, Col. 3)
*        Cameron & Miller (2015, JHR): 聚类数 ≥ 50 门槛

* (10a) 城市级聚类 — 329 个聚类, 超过 Cameron & Miller (2015) 的 50 个门槛
*   标准渐近推断可靠, 无需 wild bootstrap 补充
reghdfe Y llm_vote_tone_full nf_ln_coverage nf_media_breadth X, ///
  absorb(target_bank year) vce(cluster bank_city)
  est store robust_city_cluster

* (10b) 省级聚类 — 31 个聚类, 低于 50 个门槛
*   ⚠️ Cameron & Miller (2015, JHR, p.355) 指出:
*   聚类数 < 50 时, 标准聚类 SE 通常偏小 (over-rejection),
*   导致 Wald test 的实际拒绝率高于名义水平。
*   如果系数在此设定下仍显著, 结论更令人信服;
*   如果边际不显著, 建议运行 10c 的 wild bootstrap 确认。
reghdfe Y llm_vote_tone_full nf_ln_coverage nf_media_breadth X, ///
  absorb(target_bank year) vce(cluster bank_province)
  est store robust_prov_cluster

* (10c) Wild cluster bootstrap — 省级, 适用于少聚类情形
*   Cameron, Gelbach & Miller (2008, REStat):
*     wild bootstrap 在聚类数极少时仍能保持正确的拒绝率
*   前提: ssc install boottest
*   注: 默认为注释状态, 需要时取消注释运行
*   weighttype(webb): 31 个聚类 → Rademacher 仅 2^31 种排列,
*     Webb (2014) 六点分布在少聚类下提供更精确的 p 值
* boottest llm_vote_tone_full, cluster(bank_province) ///
*   weighttype(webb) reps(9999) seed(42)

* ── 输出格式化表格 ──
* 采用分表策略 (学术出版标准: 每表 ≤ 8 列)

* 表 1: 伪造检验主表 (对标 Hassan 2019, Table 7)
* 列: 基准 → 控制 → 替换 → 赛马 → 交互 → 语言 → 压力年
esttab base ctrl_nf replace_nf ctrl_all interact ///
  ctrl_ling robust_no_stress ///
  using "table_falsification.tex", ///
  star(* 0.10 ** 0.05 *** 0.01) se replace

* 表 2: 调节效应与异质性 (对标 Qu & Yang 2025, Tables 6, 8-9)
* 列: 调节 → 高Z组 → 低Z组 → Chow检验
esttab moderate_cont het_high het_low het_chow ///
  using "table_moderation_heterogeneity.tex", ///
  star(* 0.10 ** 0.05 *** 0.01) se replace

* 表 3: 因果识别 (对标 Luo & Li 2025, Tables 3-4, A.2)
* 列: IV(关注度×2 + 情感×2 + overid) → 聚类(城市 + 省)
esttab iv_attn_prov iv_attn_city ///
  iv_sent_prov iv_sent_city iv_overid ///
  robust_city_cluster robust_prov_cluster ///
  using "table_causal_identification.tex", ///
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
*
* IV: leave1out_tone 系数显著且第一阶段 F > 10
*   → ✅ 同区域情感溢出是有效外生变异来源
*     精确对标 Luo & Li (2025) Table 3 的 Province_news_sentiment
*
* 城市级 IV 第一阶段 F > 省级 IV
*   → ✅ 城市内媒体生态变异更强, 工具更有力
*   (同一省内不同城市的媒体环境差异提供了额外的变异来源)
*
* Hansen J (overid) p > 0.10
*   → ✅ 关注度 IV 和情感 IV 同时满足排他性约束
*   (两个不同维度的 IV 给出一致的因果估计)
*
* Oster δ < 0 或 |δ| >> 1
*   → ✅ 不可观测选择性不足以消除效应 (Oster 2019, JBEStat)
*
* β₁ 在城市/省级聚类下仍显著
*   → ✅ 效应非地理空间自相关的产物
*
* β₁ 在省级聚类下边际不显著但城市聚类下显著
*   → ℹ️ 可能因 31 个聚类数不足导致 SE 偏大
*      运行 10c wild cluster bootstrap 确认
*
* β₁(residual_tone) 显著且 ≈ β₁(baseline tone)
*   → ✅ 情感效应非银行基本面信息的副产品
*     对标 Fang et al. (2024, IREF, Table 5, Panel A)
*
* β₁(residual_tone) 显著但明显小于 β₁(baseline tone)
*   → ℹ️ 基本面部分混淆情感效应, 但独立媒体冲击仍存在
*
* β₁(residual_tone) 不显著
*   → ⚠️ 情感效应主要反映基本面信息, 而非媒体报道本身
*     (需结合 Oster δ 值和 IV 结果综合判断)
*
* ── 调节效应解读 (检验 5b, 对标 Qu & Yang 2025 Table 6) ──
*
* ⚠️ 解读前提 (Brambor et al. 2006):
*   在交互项模型中, β₁(tone) 的含义是 "当 M=0 时 tone 的效应".
*   如果 M 未中心化, M=0 可能在数据范围外, β₁ 不可解读.
*   建议: 先对 M 去均值 (egen M_c = std(M)), 此时
*   β₁ = "在 M 的均值处, tone 的边际效应"
*
* β₃(tone×M) 显著且 β₁(tone) 仍显著
*   → ✅ 外部环境调节情感传导, 且存在直接效应 (互补型调节)
*
* β₃(tone×M) 显著但 β₁(tone) 不显著
*   → ℹ️ 在 M 的均值处, 情感无直接效应,
*     但情感效应随 M 增大而显现 (纯调节型)
*     → 需确认 M 已中心化, 否则 β₁ 不可解读
*
* β₃(tone×M) 不显著
*   → ℹ️ 外部环境不调节情感传导 (直接效应型稳定)
*
* ── 异质性分组解读 (检验 7b, 对标 Qu & Yang 2025 Tables 8-9) ──
*
* β₁ 在高Z组显著但低Z组不显著 (或反之)
*   → ✅ 效应存在银行特征异质性
*
* 交互项 (7b-b) c.llm_vote_tone_full#1.Z_high 显著
*   → ✅ 组间差异有正式统计推断支持 (Chow 1960)
*
* 两组 β₁ 均显著但数值不同, 交互项不显著
*   → ℹ️ 差异存在但统计功效不足
*     建议: (1) 增大样本 (2) 使用连续交互项 (5b)
*     (3) 使用三分位 (7b-c) 检查单调性
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

* ============================================================
* 稳健性检验: 剔除银行基本面的纯情感残差
* ────────────────────────────────────────────────────────────
* 对标: Fang, Wang, Wang & Yuan (2024, IREF, 91, 1150-1172)
*       Table 5, Panel A: "Excluding bank fundamentals"
*
* 方法论说明:
*   银行基本面 (规模、杠杆、盈利等) 可能同时影响媒体报道的
*   情感基调和因变量, 导致遗漏变量偏误。本检验将情感指标
*   对银行基本面回归取残差, 残差仅保留"纯媒体冲击"成分。
*
*   Fang et al. (2024) 步骤 1 中使用的基本面变量:
*     Size         = ln(总资产)
*     Leverage     = 杠杆率 (常用: 总负债/总资产, 需按论文确认)
*     Liquidity    = 流动资产/总资产
*     Inefficiency = 营业成本/总营业收入
*     Income_div   = 非利息收入/总营业收入
*     Loan_ratio   = 贷款/总资产
*     BM           = 账面/市值
*     DI_dummy     = 存款保险制度虚拟变量 (2015年后=1)
*   注: 以上为论文原始变量, 用户应根据自身数据替换 X
*
* 与 Oster 检验 (检验 9) 的区别:
*   Oster: 假设性推演 — "需要多大的遗漏变量才能消除效应?"
*   残差法: 直接操作 — 从情感中剔除基本面可预测的部分
*   两者互补: Oster 检验不可观测变量, 残差法处理可观测变量
*
* ⚠️ FWL 注意: 步骤 1 故意不含银行 FE (仅 reg + i.year),
*   步骤 2 含银行 FE (reghdfe)。FE 结构差异避免 FWL 退化。
*   进阶: 在步骤 1 的 X 中额外加入非标准控制变量
*   (如 DI_dummy) 可增强残差法的独立信息量。
*
* 标准误说明: 步骤 2 中 residual_tone 为生成回归元 (generated
*   regressor), 其标准误未校正步骤 1 的估计不确定性。实践中
*   Fang et al. (2024) 等应用文献均未校正此项, 但用户应知
*   这可能导致 SE 略小于真实值 (即 t 统计量略有膨胀)。
*
* 步骤 1: 情感 ~ 银行基本面 (无银行 FE), 取残差
reg llm_vote_tone_full X i.year, vce(cluster target_bank)
*   → 检查 R²: 若 R² 极低, 基本面几乎不预测情感,
*     残差 ≈ 原始情感, 本检验无附加信息
cap drop residual_tone
predict residual_tone, residual
*
* 步骤 2: 用残差替代原始情感指标 (含银行 FE)
reghdfe Y residual_tone X, absorb(target_bank year) vce(cluster target_bank)
  est store residual_base
*
* 解读:
*   residual_tone 显著 → 情感效应来自媒体报道本身 (非信息渠道)
*   residual_tone 不显著 → 情感效应主要反映基本面信息, 需审慎
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
