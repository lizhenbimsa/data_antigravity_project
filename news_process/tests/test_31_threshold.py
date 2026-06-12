"""
tests/test_31_threshold.py — 31_bank_fintech_threshold.py 纯函数测试
======================================================================

测试阈值敏感性分析中可独立复刻的核心分类逻辑。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================================
# 复刻纯函数（避免 import 31_bank_fintech_threshold.py 时触发全局初始化）
# ============================================================================

def simulate_bank_classification_from_precomputed(article_matches: list,
                                                   min_upper: int,
                                                   min_lower: int,
                                                   threshold: int) -> int:
    """对预计算的银行匹配数据进行阈值过滤，返回分类为正的数量。

    fix(omni-extra-threshold-condb, 2026-06-11): 与 validation/threshold.py 的
    修复同步 — 路径 B (cond_b) 用正文 total (upper+lower) 对齐生产
    analyze_bank_matches, 不再用含标题的 total_with_title。
    """
    count = 0
    for m in article_matches:
        for bank_name, counts in m['bank_counts'].items():
            if counts['total'] >= threshold:
                cond_a = counts['upper'] >= min_upper and counts['lower'] >= min_lower
                cond_b = (counts['title'] > 0
                          and (counts['upper'] + counts['lower']) >= min_upper)
                if cond_a or cond_b:
                    count += 1
                    break
    return count


def simulate_fintech_classification_vectorized(article_matches: list,
                                                min_upper: int,
                                                min_lower: int,
                                                threshold: int) -> int:
    """对预计算的匹配数据进行阈值过滤（向量化），返回分类为正的数量。"""
    count = 0
    for m in article_matches:
        if m['distinct_count'] >= threshold:
            cond_a = m['upper_total'] >= min_upper and m['lower_total'] >= min_lower
            cond_b = m['any_in_title'] and m['grand_total'] >= min_upper
            if cond_a or cond_b:
                count += 1
    return count


def generate_sensitivity_latex(bank_results: list, fintech_results: list,
                                output_path: str, logger_inst):
    """生成敏感性分析的 LaTeX 表格。"""
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Classification Threshold Sensitivity Analysis}",
        r"\label{tab:threshold_sensitivity}",
        "",
        r"% Panel A: Bank News Classification",
        r"\begin{subtable}{\textwidth}",
        r"\centering",
        r"\caption{Panel A: Bank News Classification (min\_name\_occurrences)}",
        r"\begin{tabular}{crrr}",
        r"\hline",
        r"Threshold & Classified Positive & Retention Rate (\%) & $\Delta$ Count \\",
        r"\hline",
    ]

    prev_count = None
    for r in bank_results:
        delta = f"{r['count'] - prev_count:+,}" if prev_count is not None else "--"
        lines.append(
            f"  {r['threshold']} & {r['count']:,} & {r['ratio']:.1f} & {delta} \\\\"
        )
        prev_count = r['count']

    lines.extend([
        r"\hline",
        r"\end{tabular}",
        r"\end{subtable}",
        "",
        r"\\[12pt]",
        "",
        r"% Panel B: FinTech News Classification",
        r"\begin{subtable}{\textwidth}",
        r"\centering",
        r"\caption{Panel B: FinTech News Classification (min\_distinct\_keywords)}",
        r"\begin{tabular}{crrr}",
        r"\hline",
        r"Threshold & Classified Positive & Retention Rate (\%) & $\Delta$ Count \\",
        r"\hline",
    ])

    prev_count = None
    for r in fintech_results:
        delta = f"{r['count'] - prev_count:+,}" if prev_count is not None else "--"
        lines.append(
            f"  {r['threshold']} & {r['count']:,} & {r['ratio']:.1f} & {delta} \\\\"
        )
        prev_count = r['count']

    lines.extend([
        r"\hline",
        r"\end{tabular}",
        r"\end{subtable}",
        r"\end{table}",
    ])

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    except Exception:
        pass


# ============================================================================
# simulate_bank_classification_from_precomputed 测试
# ============================================================================

class TestBankClassificationThreshold:
    """测试银行新闻分类阈值逻辑。"""

    def test_above_threshold(self):
        """出现次数超过阈值应分类为正。"""
        matches = [
            {'bank_counts': {'中国工商银行': {'total': 5, 'upper': 3, 'lower': 2, 'title': 0}}}
        ]
        result = simulate_bank_classification_from_precomputed(matches, 1, 1, 3)
        assert result == 1

    def test_below_threshold(self):
        """出现次数低于阈值应分类为负。"""
        matches = [
            {'bank_counts': {'中国工商银行': {'total': 2, 'upper': 1, 'lower': 1, 'title': 0}}}
        ]
        result = simulate_bank_classification_from_precomputed(matches, 1, 1, 3)
        assert result == 0

    def test_exact_threshold(self):
        """恰好等于阈值应分类为正。"""
        matches = [
            {'bank_counts': {'中国工商银行': {'total': 3, 'upper': 2, 'lower': 1, 'title': 0}}}
        ]
        result = simulate_bank_classification_from_precomputed(matches, 1, 1, 3)
        assert result == 1

    def test_title_match_bypass(self):
        """标题中出现 + 正文达标应走 cond_b 路径。

        fix(omni-extra-threshold-condb, 2026-06-11): 旧 fixture (upper=0,
        lower=0, title=1, total=3) 锁定的是 total_with_title 的错误口径;
        生产 cond_b 比较基数 = 正文 total (upper+lower), 改为正文 2 次 +
        标题 1 次的生产可达样态。
        """
        matches = [
            {'bank_counts': {'中国工商银行': {'total': 3, 'upper': 2, 'lower': 0, 'title': 1}}}
        ]
        # cond_a: upper >= 1 && lower >= 1 → lower=0 → False
        # cond_b: title > 0 && (upper+lower)=2 >= 1 → True
        result = simulate_bank_classification_from_precomputed(matches, 1, 1, 3)
        assert result == 1

    def test_title_only_no_body_mentions_rejected(self):
        """标题-only 提及 (正文 0 次) 不再走 cond_b — 对齐生产逻辑。

        fix(omni-extra-threshold-condb, 2026-06-11): 旧实现 cond_b 用
        total_with_title, 该样态会被误判达标 (低阈值端正例虚高)。
        """
        matches = [
            {'bank_counts': {'中国工商银行': {'total': 3, 'upper': 0, 'lower': 0, 'title': 3}}}
        ]
        # 前置: total_with_title=3 >= 3 → 通过
        # cond_a: False; cond_b: title > 0 但 (upper+lower)=0 < 1 → False
        result = simulate_bank_classification_from_precomputed(matches, 1, 1, 3)
        assert result == 0

    def test_multiple_banks_one_matches(self):
        """多银行中只要一个达标就算正。"""
        matches = [
            {'bank_counts': {
                '中国工商银行': {'total': 1, 'upper': 0, 'lower': 0, 'title': 0},
                '中国建设银行': {'total': 5, 'upper': 3, 'lower': 2, 'title': 0},
            }}
        ]
        result = simulate_bank_classification_from_precomputed(matches, 1, 1, 3)
        assert result == 1

    def test_empty_matches(self):
        """空匹配列表应返回 0。"""
        result = simulate_bank_classification_from_precomputed([], 1, 1, 3)
        assert result == 0

    def test_no_bank_counts(self):
        """文章无银行匹配应返回 0。"""
        matches = [{'bank_counts': {}}]
        result = simulate_bank_classification_from_precomputed(matches, 1, 1, 3)
        assert result == 0

    def test_multiple_articles(self):
        """多篇文章各自独立判断。"""
        matches = [
            {'bank_counts': {'A': {'total': 5, 'upper': 3, 'lower': 2, 'title': 0}}},
            {'bank_counts': {'B': {'total': 1, 'upper': 1, 'lower': 0, 'title': 0}}},
            {'bank_counts': {'C': {'total': 4, 'upper': 2, 'lower': 2, 'title': 0}}},
        ]
        result = simulate_bank_classification_from_precomputed(matches, 1, 1, 3)
        assert result == 2  # 第1、3篇达标

    def test_high_threshold_filters_all(self):
        """阈值过高应全部滤除。"""
        matches = [
            {'bank_counts': {'A': {'total': 5, 'upper': 3, 'lower': 2, 'title': 0}}},
        ]
        result = simulate_bank_classification_from_precomputed(matches, 1, 1, 100)
        assert result == 0

    def test_upper_lower_constraint(self):
        """上/下半要求不满足应过滤（无标题匹配时）。"""
        matches = [
            {'bank_counts': {'A': {'total': 6, 'upper': 6, 'lower': 0, 'title': 0}}},
        ]
        # cond_a: upper >= 1 && lower >= 1 → lower=0 → False
        # cond_b: title > 0 → False
        result = simulate_bank_classification_from_precomputed(matches, 1, 1, 3)
        assert result == 0


# ============================================================================
# simulate_fintech_classification_vectorized 测试
# ============================================================================

class TestFintechClassificationThreshold:
    """测试金融科技新闻分类阈值逻辑。"""

    def test_above_threshold(self):
        """关键词多样性超过阈值应分类为正。"""
        matches = [
            {'distinct_count': 5, 'upper_total': 3, 'lower_total': 2,
             'grand_total': 5, 'any_in_title': False}
        ]
        result = simulate_fintech_classification_vectorized(matches, 1, 1, 3)
        assert result == 1

    def test_below_threshold(self):
        """关键词多样性不足应分类为负。"""
        matches = [
            {'distinct_count': 2, 'upper_total': 3, 'lower_total': 2,
             'grand_total': 5, 'any_in_title': False}
        ]
        result = simulate_fintech_classification_vectorized(matches, 1, 1, 3)
        assert result == 0

    def test_exact_threshold(self):
        """恰好等于阈值应分类为正。"""
        matches = [
            {'distinct_count': 3, 'upper_total': 2, 'lower_total': 1,
             'grand_total': 3, 'any_in_title': False}
        ]
        result = simulate_fintech_classification_vectorized(matches, 1, 1, 3)
        assert result == 1

    def test_title_bypass(self):
        """标题包含关键词应走 cond_b 路径。"""
        matches = [
            {'distinct_count': 3, 'upper_total': 0, 'lower_total': 0,
             'grand_total': 2, 'any_in_title': True}
        ]
        # cond_a: upper >= 1 && lower >= 1 → False
        # cond_b: any_in_title && grand_total >= 1 → True
        result = simulate_fintech_classification_vectorized(matches, 1, 1, 3)
        assert result == 1

    def test_empty_matches(self):
        """空匹配列表应返回 0。"""
        result = simulate_fintech_classification_vectorized([], 1, 1, 3)
        assert result == 0

    def test_multiple_articles(self):
        """多篇文章独立判断。"""
        matches = [
            {'distinct_count': 5, 'upper_total': 3, 'lower_total': 2,
             'grand_total': 5, 'any_in_title': False},
            {'distinct_count': 1, 'upper_total': 1, 'lower_total': 0,
             'grand_total': 1, 'any_in_title': False},
            {'distinct_count': 4, 'upper_total': 2, 'lower_total': 2,
             'grand_total': 4, 'any_in_title': True},
        ]
        result = simulate_fintech_classification_vectorized(matches, 1, 1, 3)
        assert result == 2  # 第1、3篇达标

    def test_monotonically_decreasing(self):
        """随着阈值增加，分类为正的数量应单调不增。"""
        matches = [
            {'distinct_count': i, 'upper_total': i, 'lower_total': i,
             'grand_total': 2 * i, 'any_in_title': False}
            for i in range(1, 11)
        ]
        results = []
        for threshold in range(1, 11):
            r = simulate_fintech_classification_vectorized(matches, 1, 1, threshold)
            results.append(r)
        # 单调不增
        for i in range(len(results) - 1):
            assert results[i] >= results[i + 1]


# ============================================================================
# generate_sensitivity_latex 测试
# ============================================================================

class TestGenerateSensitivityLatex:
    """测试 LaTeX 表格生成。"""

    def test_generates_valid_file(self, tmp_path):
        """应生成非空 LaTeX 文件。"""
        import logging
        logger = logging.getLogger('test_latex')
        output_path = str(tmp_path / 'test.tex')
        bank_results = [
            {'threshold': 1, 'count': 100, 'ratio': 50.0},
            {'threshold': 2, 'count': 80, 'ratio': 40.0},
        ]
        fintech_results = [
            {'threshold': 1, 'count': 200, 'ratio': 80.0},
            {'threshold': 2, 'count': 150, 'ratio': 60.0},
        ]
        generate_sensitivity_latex(bank_results, fintech_results,
                                    output_path, logger)
        assert os.path.exists(output_path)
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert r'\begin{table}' in content
        assert r'\end{table}' in content

    def test_empty_results(self, tmp_path):
        """空结果列表不应崩溃。"""
        import logging
        logger = logging.getLogger('test_latex_empty')
        output_path = str(tmp_path / 'empty.tex')
        generate_sensitivity_latex([], [], output_path, logger)
        assert os.path.exists(output_path)

    def test_single_threshold(self, tmp_path):
        """单阈值结果应正常生成。"""
        import logging
        logger = logging.getLogger('test_latex_single')
        output_path = str(tmp_path / 'single.tex')
        bank_results = [{'threshold': 3, 'count': 50, 'ratio': 25.0}]
        fintech_results = [{'threshold': 3, 'count': 100, 'ratio': 50.0}]
        generate_sensitivity_latex(bank_results, fintech_results,
                                    output_path, logger)
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert '50' in content
