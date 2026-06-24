"""test_prob_score.py — compute_prob_score() 单元测试。

学术依据:
  Törnberg, P. (2023). arXiv:2307.13106. DOI: 10.48550/arXiv.2307.13106
  Shapiro, A.H. et al. (2022). JoE, 228(2). DOI: 10.1016/j.jeconom.2020.07.053
  Jaynes, E.T. (1957). Phys Rev, 106(4). DOI: 10.1103/PhysRev.106.620

验证目标:
  1. 概率公理: Σ(P_pos + P_neu + P_neg) = 1
  2. 值域: Score ∈ [-1, +1]
  3. P2/P3 路径分支
  4. 数学性质:
     - 中性 → Score ≡ 0
     - 正面 c>1/3 → Score > 0; c=1/3 → Score=0; c<1/3 → Score < 0
     - 负面 对称
  5. 边界条件: confidence=0, confidence=1, confidence=None
"""

import os
import sys

import pytest

# 将 tests 目录加入 sys.path
sys.path.insert(0, os.path.dirname(__file__))

from twenty_one_tone_llms_import_helper import compute_prob_score

# ============================================================================
# 辅助函数
# ============================================================================

def _assert_prob_axiom(result: dict, tol=1e-9):
    """验证概率公理: Σ = 1"""
    total = result['prob_pos'] + result['prob_neu'] + result['prob_neg']
    assert abs(total - 1.0) < tol, f"概率之和 = {total}, 应为 1.0"


def _assert_score_range(result: dict):
    """验证值域: Score ∈ [-1, +1]"""
    s = result['prob_score']
    assert -1.0 <= s <= 1.0, f"Score = {s}, 超出 [-1, +1] 范围"


# ============================================================================
# 测试用例
# ============================================================================

class TestP2Path:
    """P2 路径: confidence > 0, 概率均分模拟"""

    def test_positive_high_confidence(self):
        """正面 + 高置信度 → Score > 0"""
        r = compute_prob_score("正面", 0.85)
        _assert_prob_axiom(r)
        _assert_score_range(r)
        assert r['prob_source'] == 'P2'
        assert r['prob_score'] > 0, "正面高置信度应产生正分数"
        # 数学验证: Score = (3*0.85 - 1)/2 = 0.775
        assert abs(r['prob_score'] - 0.775) < 1e-4

    def test_negative_high_confidence(self):
        """负面 + 高置信度 → Score < 0"""
        r = compute_prob_score("负面", 0.85)
        _assert_prob_axiom(r)
        _assert_score_range(r)
        assert r['prob_score'] < 0, "负面高置信度应产生负分数"
        # 数学验证: Score = (1 - 3*0.85)/2 = -0.775
        assert abs(r['prob_score'] - (-0.775)) < 1e-4

    def test_neutral_any_confidence(self):
        """中性 → Score ≡ 0 (∀ c)"""
        for c in [0.1, 0.5, 0.85, 1.0]:
            r = compute_prob_score("中性", c)
            _assert_prob_axiom(r)
            assert r['prob_score'] == 0.0, f"中性 c={c} 应产生 Score=0"

    def test_flip_point_one_third(self):
        """c = 1/3 翻转点: 正面标签但 Score = 0"""
        r = compute_prob_score("正面", 1/3)
        _assert_prob_axiom(r)
        assert abs(r['prob_score']) < 1e-6, "c=1/3 时 Score 应为 0"

    def test_positive_low_confidence_flips(self):
        """c < 1/3: 正面标签但 Score < 0 (模型不确定性压倒分类)"""
        r = compute_prob_score("正面", 0.1)
        _assert_prob_axiom(r)
        assert r['prob_score'] < 0, "c=0.1 时正面标签应产生负分数"
        # 数学验证: Score = (3*0.1 - 1)/2 = -0.35
        assert abs(r['prob_score'] - (-0.35)) < 1e-4

    def test_symmetry(self):
        """对称性: positive(c) + negative(c) ≈ 0 (∀ c)"""
        for c in [0.1, 0.5, 0.8, 1.0]:
            r_pos = compute_prob_score("正面", c)
            r_neg = compute_prob_score("负面", c)
            assert abs(r_pos['prob_score'] + r_neg['prob_score']) < 1e-9, \
                f"c={c} 时正负对称性失败"


class TestP3Path:
    """P3 路径: confidence = 0 或无效 → one-hot 硬分类"""

    def test_zero_confidence(self):
        """confidence = 0 → 走 P3 one-hot 硬分类路径"""
        r = compute_prob_score("正面", 0.0)
        _assert_prob_axiom(r)
        assert r['prob_source'] == 'P3'
        assert r['prob_score'] == 1.0, "P3 正面应为 +1.0"

    def test_none_confidence(self):
        """confidence = None → 回退 P3 路径"""
        r = compute_prob_score("负面", None)
        _assert_prob_axiom(r)
        assert r['prob_source'] == 'P3'
        assert r['prob_score'] == -1.0, "P3 负面应为 -1.0"

    def test_negative_confidence_rejected_p3_inv(self):
        """confidence < 0 → 无效输入域 → P3_INV (NaN).

        fix(omni-g-tonellms-07/11, 2026-06-11): 原断言锁定旧 clamp-to-0 行为;
        新政策与 compute_prob_score_binary 对齐 — 越界 confidence 显式拒绝,
        返回 NaN/P3_INV 由聚合层 isnan 剔除, 不再静默 clip。
        """
        import math
        r = compute_prob_score("中性", -0.5)
        assert r['prob_source'] == 'P3_INV'
        assert math.isnan(r['prob_score'])


class TestBoundaryAndEdgeCases:
    """边界与异常输入"""

    def test_confidence_one(self):
        """c = 1.0 → Score = ±1.0"""
        r = compute_prob_score("正面", 1.0)
        assert r['prob_score'] == 1.0
        assert r['prob_pos'] == 1.0
        assert r['prob_neg'] == 0.0

    def test_confidence_over_one_rejected_p3_inv(self):
        """c > 1 → 无效输入域 → P3_INV (NaN).

        fix(omni-g-tonellms-07/11, 2026-06-11): 原断言锁定旧 clamp-to-1.0 行为
        (百分制误报 confidence=95 会被静默编码为最强信号); 新政策显式拒绝。
        """
        import math
        r = compute_prob_score("正面", 1.5)
        assert r['prob_source'] == 'P3_INV'
        assert math.isnan(r['prob_score'])

    def test_unknown_label_defaults_neutral(self):
        """未知标签 → 默认中性"""
        r = compute_prob_score("未知", 0.8)
        _assert_prob_axiom(r)
        assert r['prob_score'] == 0.0, "未知标签应映射为中性 → Score=0"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
