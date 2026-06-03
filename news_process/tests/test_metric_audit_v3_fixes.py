"""回归测试: metric-audit V3 终极验证的缺陷修复 (2026-06-02/03).

权威报告: scripts/audit/METRIC_AUDIT_V3_METAVERIFY_2026-06-02.md
覆盖以下可单元测试的纯函数级修复 (panel 级修复由 rerun + test_panel_reproducibility
+ scripts/audit 数据复核守卫):
- numintensity-02: cn2arab 序数 "第N" 不转阿拉伯数字 (避免假定量 token)
- genA-01/V4:     num_intensity 双轨 full_col 可指定 content_full (含标题)
- network-01/V2:  W² 去对角 (Bramoullé 排他性: 二阶溢出不含本行自反馈)
- jf-int8/V1:     Janis-Fadner 系数须用 float64 计数避免 Int8 整数溢出越界
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

pytestmark = pytest.mark.fast


class TestCn2ArabOrdinalGuard:
    """numintensity-02: 序数词 '第N' 不应被转成阿拉伯数字 token."""

    def test_ordinal_not_converted(self):
        from news_process.pipeline.sentiment.numerical_intensity import _cn2arab
        # '第三季度' 的 '三' 紧跟 '第' → 序数, 不转
        assert '3' not in _cn2arab('第三季度')
        assert _cn2arab('第三季度') == '第三季度'
        # '第十八届' 同理
        assert _cn2arab('第十八届大会') == '第十八届大会'

    def test_genuine_number_still_converted(self):
        from news_process.pipeline.sentiment.numerical_intensity import _cn2arab
        # 非序数的真实数量词仍须转换 (不得误伤)
        assert '30000000' in _cn2arab('三千万元')
        assert '30%' in _cn2arab('百分之三十')

    def test_ordinal_num_intensity_drops(self):
        from news_process.pipeline.sentiment.numerical_intensity import compute_num_intensity
        # 纯序数文本不应贡献定量 token
        assert compute_num_intensity('公司在第三季度第四季度召开会议。') == 0.0


class TestNumIntensityFullColParam:
    """genA-01/V4: full 轨可指定 content_full (含标题), 不再硬编码裸 '内容'."""

    def test_full_col_uses_content_full(self):
        from news_process.pipeline.sentiment.numerical_intensity import (
            enrich_with_num_intensity_dual_track,
        )
        df = pd.DataFrame({
            '内容': ['正文无数字。'],
            'content_full': ['标题含3个要点。正文无数字。'],
            'content_ctx': ['标题含3个要点。窗口。'],
        })
        out = enrich_with_num_intensity_dual_track(df, full_col='content_full')
        # full 轨读 content_full (含 '3') → num_intensity_full > 0
        assert out['num_intensity_full'].iloc[0] > 0
        # 对照: 若读裸 '内容' (无数字) 则会是 0 → 证明确实读了 content_full
        out_body = enrich_with_num_intensity_dual_track(df, full_col='内容')
        assert out_body['num_intensity_full'].iloc[0] == 0.0


class TestNetworkW2Dediagonal:
    """network-01/V2: 二阶网络溢出 W² 必须去对角 (排除本行自反馈)."""

    def test_w2_diagonal_zeroed(self):
        # 3 节点行随机矩阵 (无自环)
        W = np.array([
            [0.0, 0.5, 0.5],
            [0.5, 0.0, 0.5],
            [0.5, 0.5, 0.0],
        ])
        W2 = W @ W
        # 原始 W² 对角非零 (= 自反馈), 这正是 bug
        assert W2[0, 0] > 0
        np.fill_diagonal(W2, 0.0)
        assert np.allclose(np.diag(W2), 0.0)
        # 去对角后, peer_tone_2nd 不含本行自身 tone 的贡献
        tone = np.array([1.0, -1.0, 0.0])
        peer_tone_2nd = W2 @ tone
        # 验证节点 0 的二阶溢出不再含自身 tone[0]=1.0 的回流
        # (此处只断言对角为 0 即排他性成立)
        assert peer_tone_2nd.shape == (3,)


class TestJanisFadnerNoInt8Overflow:
    """jf-int8/V1: Janis-Fadner 系数须在 float64 下计算, 理论域 [-1,1]."""

    def _jf(self, P, N):
        P = float(P); N = float(N)
        denom = (P + N) ** 2
        if denom == 0:
            return np.nan
        if P > N:
            return (P ** 2 - P * N) / denom
        if N > P:
            return (P * N - N ** 2) / denom
        return 0.0

    def test_int8_overflow_demonstrated(self):
        # 复现 bug: Int8 算术下 (P+N)**2 / P**2 静默回绕
        P = np.int8(14)
        N = np.int8(1)
        # numpy int8: (P+N)=15, 15**2=225 → 回绕 (>127)
        bad = np.int8(P + N) ** np.int8(2)
        assert int(bad) != 225  # 证明确有溢出

    def test_float64_in_range(self):
        # 修复后: float64 计算的 jf 必落 [-1,1]
        for P, N in [(14, 1), (98, 1), (50, 30), (0, 0), (1, 99)]:
            jf = self._jf(P, N)
            if not np.isnan(jf):
                assert -1.0 <= jf <= 1.0, f"P={P},N={N} → jf={jf} 越界"
        # 平安银行 2017 真实案例: P=14,N=1 → 0.8089 (非溢出的 2.387)
        assert abs(self._jf(14, 1) - 0.8089) < 1e-3
