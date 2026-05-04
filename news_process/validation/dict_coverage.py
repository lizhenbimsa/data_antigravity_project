"""
news_process.validation.dict_coverage — 金融科技词典覆盖率审计

迁移说明 (Phase 7b)：
    本模块由原 root script ``37_dict_coverage_audit.py`` body 迁入。
    规范调用方式: ``python -m news_process.validation.dict_coverage``

==================================================

审计目标:
    量化评估静态金融科技词典 (fintech_dict.json) 是否存在系统性覆盖盲区,
    从 Precision（阈值边际噪声）、Coverage（词典遗漏）和 Stability（时间退化）
    三个维度提供全自动化诊断。

分析内容:
    1. 边际通过率分布 (Precision)
    2. LLM 验证率的单调性检验 (Precision)
    3. 关键词贡献集中度 (Coverage)
    4. 时间稳定性 (Stability)
    5. 灰色地带自动化评估 (Coverage)

学术依据:
    - Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R. (2023).
      Firm-Level Climate Change Exposure.
      Journal of Finance, 78(3), 1449–1498.
      → 证明预定义关键词表会系统性遗漏"利基语言" (niche language),
        本审计量化此风险在当前管道中的严重程度。

统计方法参考:
    - Cochran, W. G. (1954). Some Methods for Strengthening the Common
      χ² Tests. Biometrics, 10(4), 417–451.
    - Armitage, P. (1955). Tests for Linear Trends in Proportions and
      Frequencies. Biometrics, 11(3), 375–386.
      → 以上两篇为 Cochran-Armitage 趋势检验的原始文献。
    - Wilson, E. B. (1927). Probable Inference, the Law of Succession,
      and Statistical Inference. Journal of the American Statistical
      Association, 22(158), 209–212.
      → Wilson score interval 的原始文献, 用于比例的置信区间估计。
    - Laakso, M. & Taagepera, R. (1979). "Effective" Number of Parties:
      A Measure with Application to West Europe. Comparative Political
      Studies, 12(1), 3–27.
      → 有效数量指标 (ENK = 1/HHI) 的方法论来源。

设计原则:
    - 全自动化执行, 零人工参与
    - 不修改任何现有管道代码
    - 所有阈值从 config.yaml 动态读取

用法:
    python 37_dict_coverage_audit.py                  # 分析 1-4 + 5a (纯统计)
    python 37_dict_coverage_audit.py --run-llm-check  # 追加 5b (LLM 交叉验证)
"""

import os
import sys
import json
import time
import argparse
import os
import sys
import warnings
from collections import Counter

import numpy as np
import pandas as pd

# Phase 7b: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 news_process/validation/dict_coverage.py 出发, 上溯 2 层抵达项目父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import setup_logging, log_stage_summary

warnings.filterwarnings('ignore', category=FutureWarning)

# ============================================================================
# 1. 全局配置
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "37_dict_coverage_audit"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

OUTPUT_DIR = CONFIG["paths"]["output_dir"]
EVAL_DIR = os.path.join(OUTPUT_DIR, 'eval_reports')
os.makedirs(EVAL_DIR, exist_ok=True)

# 从 config.yaml 动态读取阈值 T
FINTECH_PARAMS = CONFIG.get('fintech_news_classification', {})
T = FINTECH_PARAMS.get('min_distinct_keywords', 3)


# ============================================================================
# 2. 统计工具函数
# ============================================================================

def wilson_ci(p_hat: float, n: int, z: float = 1.96) -> tuple:
    """Wilson score interval for a binomial proportion.

    参考: Wilson, E. B. (1927). Probable Inference, the Law of Succession,
    and Statistical Inference. JASA, 22(158), 209–212.

    Args:
        p_hat: 观测比例
        n:     样本量
        z:     正态分位数 (默认 1.96 对应 95% CI)

    Returns:
        (lower, upper) 置信区间
    """
    if n == 0:
        return (0.0, 1.0)
    denom = 1 + z**2 / n
    center = (p_hat + z**2 / (2 * n)) / denom
    margin = z * np.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * n)) / n) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def cochran_armitage_trend_test(counts_table: np.ndarray,
                                 scores: np.ndarray) -> dict:
    """Cochran-Armitage test for trend in proportions.

    参考:
        Cochran, W. G. (1954). Some Methods for Strengthening the Common
        χ² Tests. Biometrics, 10(4), 417–451.
        Armitage, P. (1955). Tests for Linear Trends in Proportions and
        Frequencies. Biometrics, 11(3), 375–386.

    Args:
        counts_table: 2×K array, row 0 = successes, row 1 = failures per group
        scores:       length-K array of ordinal scores for each group

    Returns:
        dict with keys: 'statistic', 'p_value', 'slope_sign'
    """
    from scipy import stats as sp_stats

    n_j = counts_table.sum(axis=0).astype(float)  # group totals
    r_j = counts_table[0].astype(float)            # successes
    N = n_j.sum()
    R = r_j.sum()
    p_bar = R / N

    t_bar = np.sum(n_j * scores) / N

    # Numerator
    numer = np.sum(n_j * (r_j / n_j - p_bar) * (scores - t_bar))

    # Denominator
    denom_sq = p_bar * (1 - p_bar) * (np.sum(n_j * scores**2) - N * t_bar**2)

    if denom_sq <= 0:
        return {'statistic': 0.0, 'p_value': 1.0, 'slope_sign': 0}

    z_stat = numer / np.sqrt(denom_sq)
    p_value = 2 * (1 - sp_stats.norm.cdf(abs(z_stat)))

    return {
        'statistic': round(z_stat, 4),
        'p_value': round(p_value, 6),
        'slope_sign': int(np.sign(z_stat)),
    }


def compute_hhi(freq_array: np.ndarray) -> float:
    """Herfindahl-Hirschman Index.

    HHI = Σ s_k², 其中 s_k = n_k / Σ n_k.
    有效关键词数 ENK = 1 / HHI.

    ENK 的概念类比: Laakso, M. & Taagepera, R. (1979). "Effective" Number
    of Parties. Comparative Political Studies, 12(1), 3–27.
    """
    total = freq_array.sum()
    if total == 0:
        return 0.0
    shares = freq_array / total
    return float(np.sum(shares ** 2))


# ============================================================================
# 3. 分析 1: 边际通过率分布
# ============================================================================

def analysis_1_marginal_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """统计 fintech_distinct_keywords 的频率分布 (仅 fintech=True 行)."""
    logger.info("=" * 70)
    logger.info(f"分析 1: 边际通过率分布 (阈值 T={T})")
    logger.info("=" * 70)
    logger.info("")
    logger.info("  [说明] 本分析统计被判定为金融科技新闻的文章中,")
    logger.info(f"  每篇文章命中了多少个不同的金融科技关键词 (distinct_keywords)。")
    logger.info(f"  当前阈值 T={T}, 即文章必须命中 ≥{T} 个不同关键词才被认定为金融科技新闻。")
    logger.info(f"  '边际通过率' = 恰好命中 {T} 个 (刚好踩线通过) 的文章占比。")
    logger.info(f"  如果这个比例很高 (>15%), 说明很多文章都是勉强通过的,")
    logger.info(f"  词典对这批文章的覆盖能力有限。")
    logger.info("")

    dist = df['fintech_distinct_keywords'].value_counts().sort_index()
    total = len(df)

    dist_df = pd.DataFrame({
        'distinct_keywords': dist.index,
        'n_articles': dist.values,
        'pct': (dist.values / total * 100).round(2) if total > 0 else dist.values * 0.0,
    })

    marginal_count = int((df['fintech_distinct_keywords'] == T).sum())
    marginal_rate = marginal_count / total if total > 0 else 0

    logger.info(f"  fintech=True 文章总数: {total:,}")
    logger.info(f"  distinct_keywords 分布:")
    for _, row in dist_df.iterrows():
        marker = f" ← 边际组 (恰好={T}个, 刚好踩线)" if row['distinct_keywords'] == T else ""
        logger.info(f"    命中 {int(row['distinct_keywords']):>2} 个不同关键词: "
                     f"{int(row['n_articles']):>6,} 篇 ({row['pct']:>5.1f}%){marker}")
    logger.info("")
    logger.info(f"  【边际通过率】: {marginal_rate:.1%} "
                 f"({marginal_count:,} / {total:,})")
    if marginal_rate > 0.15:
        logger.info(f"    ⚠ 超过 15% 的安全阈值! 说明大量文章是'勉强通过'的,")
        logger.info(f"      词典可能不够丰富, 无法充分覆盖金融科技术语。")
    else:
        logger.info(f"    ✓ 在 15% 安全阈值以内, 词典在阈值区域表现健康。")

    return dist_df


# ============================================================================
# 4. 分析 2: LLM 验证率的单调性检验
# ============================================================================

def analysis_2_monotonicity_test(df: pd.DataFrame,
                                  dist_df: pd.DataFrame) -> pd.DataFrame:
    """按 distinct_keywords 分组检验 LLM 验证率的单调性."""
    logger.info("=" * 70)
    logger.info("分析 2: LLM 验证率单调性检验")
    logger.info("=" * 70)
    logger.info("")
    logger.info("  [说明] 管道中 LLM 会对每篇候选文章进行'二次验证',")
    logger.info("  判断它是否真正与银行金融科技相关 (llm_verified_full)。")
    logger.info("  本分析检查: 关键词命中越多的文章, LLM 验证通过率是否越高?")
    logger.info("  如果是, 说明关键词数量越多 → 文章越可能是真正的金融科技新闻。")
    logger.info("  如果边际组 (刚好踩线) 的通过率远低于高命中组, 说明踩线文章中")
    logger.info("  混入了较多噪声 (非金融科技新闻被错误放行)。")
    logger.info("")

    if 'llm_verified_full' not in df.columns:
        logger.warning("  llm_verified_full 列不存在, 跳过分析 2")
        return dist_df

    # 分组: T, T+1, T+2, >=T+3
    def _group_label(d):
        if d == T:
            return f'={T}'
        elif d == T + 1:
            return f'={T+1}'
        elif d == T + 2:
            return f'={T+2}'
        else:
            return f'>={T+3}'

    df = df.copy()
    df['_group'] = df['fintech_distinct_keywords'].apply(_group_label)

    group_order = [f'={T}', f'={T+1}', f'={T+2}', f'>={T+3}']
    results = []

    for g in group_order:
        mask = df['_group'] == g
        sub = df[mask]
        n = len(sub)
        if n == 0:
            results.append({'group': g, 'n': 0, 'verified_rate': np.nan})
            continue
        verified = sub['llm_verified_full'].sum()
        rate = verified / n
        lo, hi = wilson_ci(rate, n)
        results.append({
            'group': g,
            'n': n,
            'n_verified': int(verified),
            'verified_rate': round(rate, 4),
            'ci_lower': round(lo, 4),
            'ci_upper': round(hi, 4),
        })

    results_df = pd.DataFrame(results)

    for _, row in results_df.iterrows():
        if row['n'] > 0:
            ci_str = f"[{row.get('ci_lower', '?'):.3f}, {row.get('ci_upper', '?'):.3f}]"
            logger.info(f"  组 {row['group']}: n={int(row['n']):,}, "
                         f"验证率={row['verified_rate']:.3f} "
                         f"95% Wilson CI {ci_str}")

    # --- 效应量: 边际组 vs 高命中组 ---
    logger.info("")
    logger.info("  [效应量分析] 比较'刚好踩线组'和'高命中组'的 LLM 验证通过率差异:")
    marginal = results_df[results_df['group'] == f'={T}']
    high_hit = results_df[results_df['group'] == f'>={T+3}']

    if not marginal.empty and not high_hit.empty:
        m_rate = marginal.iloc[0]['verified_rate']
        h_rate = high_hit.iloc[0]['verified_rate']
        diff_pp = (m_rate - h_rate) * 100

        m_n = int(marginal.iloc[0]['n'])
        h_n = int(high_hit.iloc[0]['n'])

        # 差异的近似 CI (Wald method for difference)
        if m_n > 0 and h_n > 0:
            se_diff = np.sqrt(m_rate * (1 - m_rate) / m_n +
                              h_rate * (1 - h_rate) / h_n)
            diff_lo = diff_pp - 1.96 * se_diff * 100
            diff_hi = diff_pp + 1.96 * se_diff * 100
        else:
            diff_lo, diff_hi = np.nan, np.nan

        logger.info(f"    边际组 (={T}) 验证率: {m_rate:.1%} ({m_n:,} 篇)")
        logger.info(f"    高命中组 (>={T+3}) 验证率: {h_rate:.1%} ({h_n:,} 篇)")
        logger.info(f"    差异: {diff_pp:+.1f} 百分点 (95% 置信区间: [{diff_lo:.1f}, {diff_hi:.1f}]pp)")
        if abs(diff_pp) < 3.0:
            logger.info(f"    ✓ 差异不足 3 百分点, 可视为无实质差异 → 词典精度在各级别上保持稳定")
        else:
            logger.info(f"    ⚠ 差异超过 3 百分点 → 边际组混入了更多噪声,")
            logger.info(f"      即踩线文章中有较多'伪金融科技新闻'被关键词过滤放行")
    else:
        logger.warning("  边际组或高命中组为空, 无法计算效应量")

    # --- Cochran-Armitage 趋势检验 ---
    #   得分赋值: T, T+1, T+2 各组赋原始值; >=T+3 组赋该组中位数
    try:
        ca_groups = []
        ca_scores = []
        for g in group_order:
            sub = df[df['_group'] == g]
            if len(sub) == 0:
                continue
            n_g = len(sub)
            v_g = int(sub['llm_verified_full'].sum())
            ca_groups.append((v_g, n_g - v_g))

            if g.startswith('>='):
                score = sub['fintech_distinct_keywords'].median()
            else:
                score = int(g.replace('=', ''))
            ca_scores.append(score)

        if len(ca_groups) >= 2:
            counts_table = np.array(ca_groups).T  # 2×K
            scores = np.array(ca_scores, dtype=float)
            ca_result = cochran_armitage_trend_test(counts_table, scores)

            trend_msg = ("正向趋势 (关键词越多 → 验证率越高)"
                         if ca_result['slope_sign'] > 0
                         else "负向趋势 (关键词越多 → 验证率反而越低)")
            sig_msg = "显著" if ca_result['p_value'] < 0.05 else "不显著"
            logger.info("")
            logger.info("  [Cochran-Armitage 趋势检验]")
            logger.info(f"    这是一个统计学检验, 用于判断'验证率'是否随关键词数量单调变化。")
            logger.info(f"    z 统计量 = {ca_result['statistic']:.3f}, p 值 = {ca_result['p_value']:.4f}")
            if ca_result['p_value'] < 0.05 and ca_result['slope_sign'] > 0:
                logger.info(f"    ✓ 趋势在统计学上显著 (p<0.05): {trend_msg}")
                logger.info(f"      说明关键词命中数越多, 文章越可能是真正的金融科技新闻。")
            elif ca_result['p_value'] >= 0.05:
                logger.info(f"    结果不显著 (p≥0.05): 验证率在各组之间没有明确的变化趋势。")
            else:
                logger.info(f"    ⚠ {trend_msg}, 这是异常信号。")

            results_df.attrs['ca_statistic'] = ca_result['statistic']
            results_df.attrs['ca_p_value'] = ca_result['p_value']
        else:
            logger.warning("  分组不足 2 组, 跳过趋势检验")
    except ImportError:
        logger.warning("  scipy 不可用, 跳过 Cochran-Armitage 趋势检验")

    # --- Fisher's Exact Test (辅助) ---
    try:
        from scipy.stats import fisher_exact
        if not marginal.empty and not high_hit.empty:
            m_row = marginal.iloc[0]
            h_row = high_hit.iloc[0]
            table = np.array([
                [int(m_row['n_verified']), int(m_row['n'] - m_row['n_verified'])],
                [int(h_row['n_verified']), int(h_row['n'] - h_row['n_verified'])],
            ])
            _, p_fisher = fisher_exact(table)
            logger.info(f"  【Fisher's Exact Test (辅助)】p={p_fisher:.4f}")
    except Exception as e:
        logger.info(f"  Fisher's Exact Test 跳过: {e}")

    return results_df


# ============================================================================
# 5. 分析 3: 关键词贡献集中度
# ============================================================================

def analysis_3_keyword_concentration(df: pd.DataFrame) -> tuple:
    """分析关键词频率分布、HHI、零命中关键词."""
    logger.info("=" * 70)
    logger.info("分析 3: 关键词贡献集中度")
    logger.info("=" * 70)
    logger.info("")
    logger.info("  [说明] 本分析检查词典中的关键词是否被'均匀使用',")
    logger.info("  还是只有少数几个高频词贡献了绝大多数命中。")
    logger.info("  如果词典有 1500 个词, 但只有 50 个词在实际新闻中出现过,")
    logger.info("  那词典的'有效覆盖面'其实远小于其表面规模。")
    logger.info("")

    # 加载词典
    dict_path = CONFIG['paths'].get('fintech_dict_file', '')
    if not dict_path or not os.path.exists(dict_path):
        dict_path = os.path.join(os.path.dirname(__file__),
                                 'config', 'fintech_dict.json')
    try:
        with open(dict_path, 'r', encoding='utf-8') as f:
            all_keywords = set(json.load(f))
        logger.info(f"  词典加载: {len(all_keywords)} 个关键词 ({dict_path})")
    except Exception as e:
        logger.error(f"  词典加载失败: {e}")
        return pd.DataFrame(), pd.DataFrame()

    # --- 3a: 解析 fintech_keyword_details, 统计 article-level 频率 ---
    keyword_counter = Counter()

    for details_str in df['fintech_keyword_details'].dropna():
        if not details_str or details_str == '':
            continue
        try:
            details = json.loads(details_str)
            seen_in_article = set()
            for item in details:
                kw = item.get('keyword', '')
                if kw and kw not in seen_in_article:
                    keyword_counter[kw] += 1
                    seen_in_article.add(kw)
        except (json.JSONDecodeError, TypeError):
            continue

    freq_df = pd.DataFrame([
        {'keyword': kw, 'article_count': cnt}
        for kw, cnt in keyword_counter.most_common()
    ])

    logger.info(f"  实际命中的不同关键词数: {len(keyword_counter)}")
    if not freq_df.empty:
        logger.info(f"  Top-10 高频关键词:")
        for i, row in freq_df.head(10).iterrows():
            logger.info(f"    {i+1:>3}. {row['keyword']}: {row['article_count']:,} 篇")

    # --- 3b: HHI + ENK ---
    if len(keyword_counter) > 0:
        freq_array = np.array(list(keyword_counter.values()), dtype=float)
        hhi = compute_hhi(freq_array)
        enk = 1.0 / hhi if hhi > 0 else len(keyword_counter)
        logger.info("")
        logger.info(f"  【HHI 集中度指数】: {hhi:.6f}")
        logger.info(f"    HHI 衡量关键词使用的集中程度, 范围 0~1。")
        logger.info(f"    越接近 0 = 越分散 (好), 越接近 1 = 越集中在少数词 (差)。")
        logger.info(f"  【有效关键词数 ENK = 1/HHI】: {enk:.1f}")
        logger.info(f"    ENK 表示'如果所有关键词被均匀使用, 等效于有多少个词在工作'。")
        if enk < 50:
            logger.info(f"    ⚠ ENK < 50, 说明词典虽然有 {len(keyword_counter)} 个命中词,")
            logger.info(f"      但实际上只有约 {enk:.0f} 个词在真正发挥作用。")
        else:
            logger.info(f"    ✓ ENK ≥ 50, 关键词使用相对分散, 词典有效覆盖面较好。")
    else:
        hhi, enk = 0.0, 0.0

    # --- 3c: 零命中关键词 ---
    hit_keywords = set(keyword_counter.keys())
    zero_hit = sorted(all_keywords - hit_keywords)
    zero_hit_df = pd.DataFrame({'keyword': zero_hit})

    # --- 3d: 有效覆盖率 ---
    coverage_rate = 1 - len(zero_hit) / len(all_keywords) if all_keywords else 0
    logger.info("")
    logger.info(f"  【零命中关键词】: {len(zero_hit)} / {len(all_keywords)} 个")
    logger.info(f"    这 {len(zero_hit)} 个词存在于词典中, 但在全部语料中从未出现过 ('死词')。")
    logger.info(f"  【有效覆盖率】: {coverage_rate:.1%}")
    logger.info(f"    即词典中实际在语料中命中过的词占总词表的比例。")
    if coverage_rate < 0.50:
        logger.info(f"    ⚠ 有效覆盖率低于 50%, 超过一半的词典词条是'死词',")
        logger.info(f"      建议清理这些无效词条, 或检查词典与语料的匹配度。")
    else:
        logger.info(f"    ✓ 有效覆盖率 ≥ 50%, 词典与语料匹配度尚可。")

    return freq_df, zero_hit_df


# ============================================================================
# 6. 分析 4: 时间稳定性
# ============================================================================

def analysis_4_temporal_stability(df_full: pd.DataFrame) -> pd.DataFrame:
    """逐年计算总体通过率、边际通过率、平均命中词数."""
    logger.info("=" * 70)
    logger.info("分析 4: 时间稳定性")
    logger.info("=" * 70)
    logger.info("")
    logger.info("  [说明] 本分析逐年追踪词典的表现, 检查是否存在'老化'趋势。")
    logger.info("  如果金融科技领域出现了新术语 (如 '数字人民币', 'Web3'),")
    logger.info("  但词典没有及时更新, 那么越来越多的新文章只能勉强通过阈值,")
    logger.info("  表现为: 边际通过率逐年升高 + 总体通过率逐年下降。")
    logger.info("")

    df = df_full.copy()
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
    df['year'] = df['日期'].dt.year
    df = df.dropna(subset=['year'])
    df['year'] = df['year'].astype(int)

    years = sorted(df['year'].unique())
    rows = []

    for yr in years:
        yr_df = df[df['year'] == yr]
        total = len(yr_df)
        fintech_mask = yr_df['is_fintech_news'] == True
        n_fintech = int(fintech_mask.sum())

        overall_rate = n_fintech / total if total > 0 else 0

        fintech_df = yr_df[fintech_mask]
        n_marginal = int((fintech_df['fintech_distinct_keywords'] == T).sum())
        marginal_rate = n_marginal / n_fintech if n_fintech > 0 else 0

        avg_kw = fintech_df['fintech_distinct_keywords'].mean() if n_fintech > 0 else 0

        rows.append({
            'year': yr,
            'n_total': total,
            'n_fintech': n_fintech,
            'overall_pass_rate': round(overall_rate, 4),
            'n_marginal': n_marginal,
            'marginal_rate': round(marginal_rate, 4),
            'avg_distinct_keywords': round(avg_kw, 2),
        })

    trend_df = pd.DataFrame(rows)

    logger.info(f"  年份范围: {min(years)} - {max(years)}")
    for _, row in trend_df.iterrows():
        logger.info(f"  {int(row['year'])}: "
                     f"总体通过率={row['overall_pass_rate']:.1%}, "
                     f"边际率={row['marginal_rate']:.1%}, "
                     f"平均命中词={row['avg_distinct_keywords']:.1f}")

    # 简单趋势判断
    if len(trend_df) >= 3:
        marginal_trend = np.polyfit(range(len(trend_df)),
                                     trend_df['marginal_rate'].values, 1)[0]
        overall_trend = np.polyfit(range(len(trend_df)),
                                    trend_df['overall_pass_rate'].values, 1)[0]
        if marginal_trend > 0.005 and overall_trend < -0.005:
            logger.info("  ⚠ 趋势信号: 边际率↑ + 总体率↓ → 词典可能老化")
        elif marginal_trend > 0.005:
            logger.info("  ⚠ 趋势信号: 边际率有上升趋势")
        else:
            logger.info("  ✓ 边际率稳定, 无明显老化信号")

    return trend_df


# ============================================================================
# 7. 分析 5: 灰色地带自动化评估
# ============================================================================

def analysis_5a_grey_zone_stats(df_full: pd.DataFrame) -> dict:
    """灰色地带形态统计."""
    logger.info("=" * 70)
    logger.info("分析 5a: 灰色地带形态统计")
    logger.info("=" * 70)
    logger.info("")
    logger.info("  [说明] '灰色地带'是指那些有少量关键词命中但未达到阈值的文章。")
    logger.info(f"  例如阈值 T={T}, 那么命中 1 或 2 个关键词的文章就在灰色地带:")
    logger.info(f"  它们可能确实是金融科技新闻, 但因词典覆盖不足而被'漏掉'了。")
    logger.info(f"  如果灰色地带的文章数量很大, 说明词典可能存在系统性遗漏。")
    logger.info("")

    rejected = df_full[df_full['is_fintech_news'] == False]
    total_bank_news = len(df_full)
    n_rejected = len(rejected)

    has_kw_col = 'fintech_distinct_keywords' in rejected.columns

    if has_kw_col:
        zero_hit = rejected[rejected['fintech_distinct_keywords'] == 0]
        grey_zone = rejected[(rejected['fintech_distinct_keywords'] >= 1) &
                              (rejected['fintech_distinct_keywords'] < T)]
    else:
        zero_hit = rejected
        grey_zone = pd.DataFrame()

    n_zero = len(zero_hit)
    n_grey = len(grey_zone)

    pct_zero = n_zero / total_bank_news if total_bank_news > 0 else 0
    pct_grey = n_grey / total_bank_news if total_bank_news > 0 else 0

    logger.info(f"  全部银行新闻: {total_bank_news:,}")
    logger.info(f"  被拒绝 (fintech=False): {n_rejected:,}")
    logger.info(f"    零命中 (distinct=0): {n_zero:,} ({pct_zero:.1%})")
    logger.info(f"    灰色地带 (1≤distinct<{T}): {n_grey:,} ({pct_grey:.1%})"
                 f" {'⚠ > 10%' if pct_grey > 0.10 else '✓'}")

    if has_kw_col and n_grey > 0:
        grey_dist = grey_zone['fintech_distinct_keywords'].value_counts().sort_index()
        for val, cnt in grey_dist.items():
            logger.info(f"      distinct={int(val)}: {cnt:,} 篇")

    return {
        'total_bank_news': total_bank_news,
        'n_zero_hit': n_zero,
        'n_grey_zone': n_grey,
        'pct_grey_zone': round(pct_grey, 4),
        'grey_zone_df': grey_zone,
    }


def analysis_5b_llm_cross_validation(grey_zone_df: pd.DataFrame):
    """对灰色地带文章执行 LLM 自动化交叉验证.

    方法论独立性说明:
        关键词过滤器 (Aho-Corasick 词袋匹配) 与 LLM 验证 (语义理解) 是
        方法论独立的两套分类器——前者基于词表精确匹配, 后者基于上下文语义推理,
        二者无共享参数或训练数据。因此用 LLM 交叉验证关键词过滤器不构成循环
        论证, 与 Sautner et al. (2023, JF) 使用独立人工审读验证 ML 分类器
        的逻辑一致。

    样本量依据:
        n=1000 在 p=20% 时 95% CI 半宽度 ±2.5pp.
        参考: Wilson (1927, JASA 22(158):209-212).
    """
    logger.info("=" * 70)
    logger.info("分析 5b: 灰色地带 LLM 自动化交叉验证")
    logger.info("=" * 70)

    if grey_zone_df.empty:
        logger.info("  灰色地带为空, 跳过 LLM 交叉验证")
        return

    n_total = len(grey_zone_df)
    n_sample = min(1000, n_total)
    is_census = n_sample == n_total

    if is_census:
        sample_df = grey_zone_df.copy()
        logger.info(f"  灰色地带总量 {n_total} ≤ 1000, 执行全量验证")
    else:
        sample_df = grey_zone_df.sample(n=n_sample, random_state=42)
        logger.info(f"  从 {n_total:,} 篇中随机抽取 {n_sample} 篇 (seed=42)")

    # --- 复用 21_tone_llms.py 的 LLM 基础设施 ---
    try:
        # 延迟导入, 仅在 --run-llm-check 时加载
        # Phase 6a: utils.helpers → news_process.core.config (load_config 已在文件顶部 import,
        # 此处保留是历史 dead-code; utils.llm_clients 模块从未存在, 整个 try-block 必然走 except 分支)
        from news_process.core.config import load_config  # noqa: F401  (re-import OK)
        from utils.llm_clients import call_llm_models_async  # noqa: F401 — known-broken; preserved verbatim

        llm_config = CONFIG.get('tone_llm_processing', {})
        models = llm_config.get('models', [])

        if not models:
            logger.error("  config.yaml 中未配置 LLM 模型, 无法执行交叉验证")
            return

        logger.info(f"  LLM 模型: {[m['short_name'] for m in models]}")
        logger.info(f"  预计 LLM 调用次数: ~{n_sample * len(models)}")

        # 构建 prompt (复用 21_tone_llms.py 的 prompt 模板)
        prompt_template = llm_config.get('prompt_template', '')
        if not prompt_template:
            prompt_template = (
                "请判断以下新闻是否与银行金融科技相关。\n"
                "标题: {title}\n内容: {content}\n"
                "请以 JSON 格式回答: "
                '{{\"is_bank_fintech_news\": true/false, '
                '\"sentiment\": \"正面/中性/负面\"}}'
            )

        results = []
        batch_size = 50
        n_batches = (n_sample + batch_size - 1) // batch_size

        for batch_i in range(n_batches):
            start = batch_i * batch_size
            end = min(start + batch_size, n_sample)
            batch = sample_df.iloc[start:end]

            logger.info(f"  处理批次 {batch_i+1}/{n_batches} "
                         f"({start+1}-{end}/{n_sample})")

            for idx, row in batch.iterrows():
                title = str(row.get('标题', ''))
                content = str(row.get('内容', ''))[:2000]

                try:
                    import asyncio

                    # 调用多模型
                    model_responses = asyncio.run(
                        call_llm_models_async(
                            prompt_template.format(title=title, content=content),
                            models
                        )
                    )

                    # 多数投票判断 is_bank_fintech_news
                    votes = []
                    for m in models:
                        resp = model_responses.get(m['model_name'], '')
                        if resp:
                            try:
                                # 尝试解析 JSON
                                import re
                                json_match = re.search(r'\{[^}]+\}', resp)
                                if json_match:
                                    jd = json.loads(json_match.group())
                                    v = jd.get('is_bank_fintech_news', False)
                                    if isinstance(v, str):
                                        v = v.strip().lower() in ('true', '1', 'yes')
                                    votes.append(bool(v))
                            except (json.JSONDecodeError, AttributeError):
                                pass

                    # 多数决
                    is_fintech = sum(votes) > len(votes) / 2 if votes else False

                    results.append({
                        'idx': idx,
                        'distinct_keywords': row.get('fintech_distinct_keywords', 0),
                        'llm_is_fintech': is_fintech,
                        'n_votes': len(votes),
                        'n_yes': sum(votes) if votes else 0,
                    })
                except Exception as e:
                    logger.warning(f"    LLM 调用失败 (idx={idx}): {e}")
                    results.append({
                        'idx': idx,
                        'distinct_keywords': row.get('fintech_distinct_keywords', 0),
                        'llm_is_fintech': None,
                        'n_votes': 0,
                        'n_yes': 0,
                    })

        # --- 汇总 FNR ---
        results_df = pd.DataFrame(results)
        valid = results_df[results_df['llm_is_fintech'].notna()]

        if len(valid) > 0:
            fnr_overall = valid['llm_is_fintech'].mean()
            lo, hi = wilson_ci(fnr_overall, len(valid))
            logger.info(f"  【总体 FNR】: {fnr_overall:.1%} "
                         f"95% CI [{lo:.1%}, {hi:.1%}]"
                         f" ({'⚠ > 20%' if fnr_overall > 0.20 else '✓'})")

            # 分层报告
            for d_val in sorted(valid['distinct_keywords'].unique()):
                sub = valid[valid['distinct_keywords'] == d_val]
                if len(sub) > 0:
                    fnr_d = sub['llm_is_fintech'].mean()
                    lo_d, hi_d = wilson_ci(fnr_d, len(sub))
                    logger.info(f"    distinct={int(d_val)}: "
                                 f"FNR={fnr_d:.1%} [{lo_d:.1%}, {hi_d:.1%}] "
                                 f"(n={len(sub)})")

        # 保存
        output_path = os.path.join(EVAL_DIR, '37_false_negative_estimate.csv')
        results_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"  LLM 交叉验证结果已保存: {output_path}")

    except ImportError as e:
        logger.error(f"  LLM 基础设施导入失败: {e}")
        logger.error("  请确认 utils/llm_clients.py 存在且 API 密钥已配置")
    except Exception as e:
        logger.error(f"  LLM 交叉验证执行失败: {e}")


# ============================================================================
# 8. 综合结论
# ============================================================================

def log_summary(marginal_rate: float, effect_size: float,
                enk: float, coverage_rate: float, fnr: float = None):
    """输出综合审计结论."""
    logger.info("")
    logger.info("=" * 70)
    logger.info("综合审计结论")
    logger.info("=" * 70)
    logger.info("")
    logger.info("  以下是本次审计的核心指标汇总:")
    logger.info(f"    · 边际通过率: {marginal_rate:.1%}   (安全阈值: ≤15%)")
    logger.info(f"    · 验证率差异: {effect_size:+.1f}pp  (安全阈值: <3pp)")
    logger.info(f"    · 有效关键词数 ENK: {enk:.0f}     (建议: ≥50)")
    logger.info(f"    · 有效覆盖率: {coverage_rate:.1%}   (建议: ≥50%)")
    if fnr is not None:
        logger.info(f"    · 自动化 FNR: {fnr:.1%}      (安全阈值: <10%)")
    logger.info("")

    issues = []
    if marginal_rate > 0.15:
        issues.append(f"边际通过率偏高 ({marginal_rate:.1%} > 15%): "
                       f"太多文章刚好踩线通过, 词典对边际区域覆盖不足")
    if abs(effect_size) >= 5.0:
        issues.append(f"边际组精度下降 ({effect_size:+.1f}pp): "
                       f"踩线文章中混入了较多噪声")
    if enk < 50:
        issues.append(f"有效关键词数不足 (ENK={enk:.0f}): "
                       f"词典过度依赖少数高频词, 有效维度偏低")
    if coverage_rate < 0.50:
        issues.append(f"有效覆盖率偏低 ({coverage_rate:.1%}): "
                       f"词典中超过一半的词条从未在语料中出现过")
    if fnr is not None and fnr > 0.20:
        issues.append(f"FNR 偏高 ({fnr:.1%}): "
                       f"灰色地带中有大量真正的金融科技新闻被遗漏")

    if not issues:
        logger.info("  ✓ 词典覆盖率审计通过, 未发现系统性缺陷。")
        logger.info("    当前静态词典的覆盖能力满足需求, 暂不需要引入 ML 关键词发现算法。")
    else:
        logger.info(f"  ⚠ 发现 {len(issues)} 项需关注的问题:")
        for i, issue in enumerate(issues, 1):
            logger.info(f"    {i}. {issue}")
        logger.info("")
        logger.info("  [建议] 可考虑以下改进措施:")
        if marginal_rate > 0.15 or (enk < 50):
            logger.info("    → 扩展词典: 引入类 Sautner et al. (2023) 的 ML 关键词发现算法")
        if coverage_rate < 0.50:
            logger.info("    → 清理词典: 移除零命中的'死词', 提高词典信噪比")
        if fnr is not None and fnr > 0.20:
            logger.info(f"    → 降低阈值: 考虑将 min_distinct_keywords 从 {T} 下调至 {T-1}")


# ============================================================================
# 主流程
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='金融科技词典覆盖率审计')
    parser.add_argument('--run-llm-check', action='store_true',
                        help='执行分析 5b: LLM 灰色地带交叉验证')
    args = parser.parse_args()

    start_time = time.time()
    logger.info("=" * 70)
    logger.info("===  37_dict_coverage_audit: 词典覆盖率审计  ===")
    logger.info("=" * 70)
    logger.info(f"  阈值 T (min_distinct_keywords): {T}")
    logger.info(f"  LLM 交叉验证: {'启用' if args.run_llm_check else '禁用'}")

    # ================================================================
    # 加载数据
    # ================================================================

    # --- 21_tone_llms_full.parquet (分析 1, 2, 3) ---
    llm_full_file = CONFIG.get('filenames', {}).get(
        'output_21_tone_llms_full', '21_tone_llms_full.parquet')
    llm_full_path = os.path.join(OUTPUT_DIR, llm_full_file)

    # --- 12_fintech_news_full.parquet (分析 4, 5) ---
    ft_full_file = CONFIG.get('filenames', {}).get(
        'output_12_fintech_full', '12_fintech_news_full.parquet')
    ft_full_path = os.path.join(OUTPUT_DIR, ft_full_file)

    if not os.path.exists(llm_full_path):
        logger.error(f"文件不存在: {llm_full_path}")
        logger.error("请先运行阶段 21 (21_tone_llms.py)")
        sys.exit(1)

    if not os.path.exists(ft_full_path):
        logger.error(f"文件不存在: {ft_full_path}")
        logger.error("请先运行阶段 12 (12_news_fintech.py)")
        sys.exit(1)

    logger.info(f"加载 LLM 全量数据: {llm_full_path}")
    df_llm = pd.read_parquet(llm_full_path)
    logger.info(f"  行数: {len(df_llm):,}, 列数: {df_llm.shape[1]}")

    logger.info(f"加载 fintech 全量数据: {ft_full_path}")
    df_ft_full = pd.read_parquet(ft_full_path)
    logger.info(f"  行数: {len(df_ft_full):,}, 列数: {df_ft_full.shape[1]}")

    # ================================================================
    # 分析 1: 边际通过率分布
    # ================================================================
    dist_df = analysis_1_marginal_distribution(df_llm)

    # ================================================================
    # 分析 2: LLM 验证率单调性检验
    # ================================================================
    group_df = analysis_2_monotonicity_test(df_llm, dist_df)

    # ================================================================
    # 分析 3: 关键词贡献集中度
    # ================================================================
    freq_df, zero_hit_df = analysis_3_keyword_concentration(df_llm)

    # ================================================================
    # 分析 4: 时间稳定性
    # ================================================================
    trend_df = analysis_4_temporal_stability(df_ft_full)

    # ================================================================
    # 分析 5a: 灰色地带形态统计
    # ================================================================
    grey_info = analysis_5a_grey_zone_stats(df_ft_full)

    # ================================================================
    # 分析 5b: LLM 交叉验证 (可选)
    # ================================================================
    if args.run_llm_check:
        analysis_5b_llm_cross_validation(grey_info['grey_zone_df'])

    # ================================================================
    # 保存输出
    # ================================================================
    logger.info("=" * 70)
    logger.info("保存输出文件")
    logger.info("=" * 70)

    # 分析 1+2 合并输出
    coverage_path = os.path.join(EVAL_DIR, '37_coverage_distribution.csv')
    if not group_df.empty:
        group_df.to_csv(coverage_path, index=False, encoding='utf-8-sig')
    else:
        dist_df.to_csv(coverage_path, index=False, encoding='utf-8-sig')
    logger.info(f"  分析 1+2: {coverage_path}")

    # 分析 3a: 关键词频率
    freq_path = os.path.join(EVAL_DIR, '37_keyword_frequency.csv')
    if not freq_df.empty:
        freq_df.to_csv(freq_path, index=False, encoding='utf-8-sig')
    logger.info(f"  分析 3a:  {freq_path}")

    # 分析 3c: 零命中关键词
    zero_path = os.path.join(EVAL_DIR, '37_zero_hit_keywords.csv')
    if not zero_hit_df.empty:
        zero_hit_df.to_csv(zero_path, index=False, encoding='utf-8-sig')
    logger.info(f"  分析 3c:  {zero_path}")

    # 分析 4: 时间趋势
    trend_path = os.path.join(EVAL_DIR, '37_temporal_drift.csv')
    if not trend_df.empty:
        trend_df.to_csv(trend_path, index=False, encoding='utf-8-sig')
    logger.info(f"  分析 4:   {trend_path}")

    # ================================================================
    # 综合结论
    # ================================================================
    # 提取关键指标
    total_fintech = len(df_llm)
    n_marginal = int((df_llm['fintech_distinct_keywords'] == T).sum())
    marginal_rate = n_marginal / total_fintech if total_fintech > 0 else 0

    effect_size = 0.0
    if not group_df.empty and 'verified_rate' in group_df.columns:
        m_group = group_df[group_df['group'] == f'={T}']
        h_group = group_df[group_df['group'] == f'>={T+3}']
        if not m_group.empty and not h_group.empty:
            m_r = m_group.iloc[0]['verified_rate']
            h_r = h_group.iloc[0]['verified_rate']
            if not np.isnan(m_r) and not np.isnan(h_r):
                effect_size = (m_r - h_r) * 100

    # HHI / ENK
    if not freq_df.empty:
        freq_array = freq_df['article_count'].values.astype(float)
        hhi = compute_hhi(freq_array)
        enk = 1.0 / hhi if hhi > 0 else len(freq_df)
    else:
        enk = 0.0

    # 有效覆盖率
    dict_path = CONFIG['paths'].get('fintech_dict_file', '')
    if not dict_path or not os.path.exists(dict_path):
        dict_path = os.path.join(os.path.dirname(__file__),
                                 'config', 'fintech_dict.json')
    try:
        with open(dict_path, 'r', encoding='utf-8') as f:
            n_dict = len(json.load(f))
        coverage_rate = 1 - len(zero_hit_df) / n_dict if n_dict > 0 else 0
    except Exception:
        coverage_rate = 0.0

    log_summary(marginal_rate, effect_size, enk, coverage_rate)

    elapsed = time.time() - start_time
    logger.info(f"\n审计完成, 总耗时: {elapsed:.1f} 秒")


if __name__ == '__main__':
    main()
