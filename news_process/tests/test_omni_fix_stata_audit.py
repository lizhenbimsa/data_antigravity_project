"""回归测试: omni 2026-06-11 修复组 g-stata-audit (pipeline/audit/stata_audit.py).

覆盖三个修复 (见 scripts/audit/_omni_fix/g-stata-audit.json):
- g-stata-audit-01 (P1): 3e 加权恒等式 LLM 族期望分母改用 valid-mask 列
  sum_wd_{wtag}_llm{track} (与 encode.py::_llm_denom 2026-06-10 修复对齐);
  缺 mask 列回退物理分母 (旧冻结 panel 兼容)。修复前: valid-mask 重生面板
  上按物理分母重算 → 含 LLM-invalid 文章的 bank-year 必误 FAIL。
- g-stata-audit-02 (P2): 修正 3e 两处陈旧列名 (VW 分子 llm_vote_score_vw_sum_full
  → llm_vote_score_w_sum{track}; HW 物理分母 sum_herd_weight →
  sum_herd_weight_full/_ctx), 并把静默跳过改为缺任一所需列即 WARN。
- g-stata-audit-03 (P3): 6d .dta 精度检查补 NaN 位置对称比对 — 修复前
  (dta-pq).abs().max() 的 skipna 吞掉单侧 NaN, "值→缺失"腐蚀 (KNOWN-OPEN ⑥
  Int8∈[101,126]→extended missing 模式) 恒 PASS。

全部用合成 DataFrame, 不依赖盘上大数据 / 外部 API。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import news_process.pipeline.audit.stata_audit as sa

pytestmark = pytest.mark.fast


def _run_sentiment(panel: pd.DataFrame) -> dict:
    """跑 audit_sentiment_consistency, 返回 {check_name: record}."""
    sa.audit_results.clear()
    sa.audit_sentiment_consistency(panel, 'test')
    return {r['check']: r for r in sa.audit_results}


def _run_stata_compat(panel: pd.DataFrame, dta_path: str) -> dict:
    """跑 audit_stata_compatibility, 返回 {check_name: record}."""
    sa.audit_results.clear()
    sa.audit_stata_compatibility(panel, dta_path, 'test')
    return {r['check']: r for r in sa.audit_results}


class TestWeightedIdentityValidMaskDenominator:
    """g-stata-audit-01: 3e LLM 族恒等式须用 valid-mask 分母, 缺列回退物理."""

    def test_mw_valid_mask_panel_no_false_fail(self):
        # 重生面板: 1 银行 2 篇, 其中 1 篇 LLM-invalid。
        # 物理分母 Σw=5.0, valid-mask 分母 sum_wd_mw_llm_full=2.0;
        # 分子 Σ(w·s)=2.0 → tone = 2.0/2.0 = 1.0 (encode valid-mask 口径)。
        # 修复前: expected=2.0/5.0=0.4 vs actual=1.0 → diff=0.6 误 FAIL。
        panel = pd.DataFrame({
            'target_bank': ['A'], 'year': [2018],
            'n_articles': [2], 'n_articles_llm_valid': [1],
            'sum_media_authority_weight': [5.0],
            'sum_wd_mw_llm_full': [2.0],
            'llm_vote_score_mw_sum_full': [2.0],
            'llm_vote_tone_mw_full': [1.0],
        })
        r = _run_sentiment(panel)['MW加权恒等式 (_full)']
        assert r['status'] == 'PASS', f"valid-mask 面板不应误 FAIL: {r['detail']}"
        assert 'valid-mask' in r['detail'], "detail 须注明分母口径"

    def test_mw_physical_fallback_old_panel(self):
        # 旧冻结面板: 无 sum_wd_* 列 → 回退物理分母 (encode 同款回退契约)。
        # tone = 2.0/5.0 = 0.4 (旧 encode 物理口径) → PASS。
        panel = pd.DataFrame({
            'target_bank': ['A'], 'year': [2018], 'n_articles': [2],
            'sum_media_authority_weight': [5.0],
            'llm_vote_score_mw_sum_full': [2.0],
            'llm_vote_tone_mw_full': [0.4],
        })
        r = _run_sentiment(panel)['MW加权恒等式 (_full)']
        assert r['status'] == 'PASS', f"物理回退应 PASS: {r['detail']}"
        assert 'physical' in r['detail']

    def test_vw_valid_mask_denominator(self):
        # VW 同款: mask=2.0 优先于物理 sum_mention_density=5.0。
        panel = pd.DataFrame({
            'target_bank': ['A'], 'year': [2018], 'n_articles': [2],
            'sum_mention_density': [5.0],
            'sum_wd_vw_llm_full': [2.0],
            'llm_vote_score_w_sum_full': [2.0],
            'llm_vote_tone_vw_full': [1.0],
        })
        r = _run_sentiment(panel)['VW加权恒等式 (_full)']
        assert r['status'] == 'PASS', f"VW valid-mask 应 PASS: {r['detail']}"
        assert 'valid-mask' in r['detail']


class TestWeightedIdentityStaleColumnNames:
    """g-stata-audit-02: VW 分子 / HW 分母陈旧列名修正 + 缺列必 WARN 不静默."""

    def test_vw_check_actually_runs_with_real_numerator_name(self):
        # 修复前: 3e 找 llm_vote_score_vw_sum_full (不存在的幻影名) → 静默死亡,
        # 零记录。修复后: 用真名 llm_vote_score_w_sum_full, 检查真正执行。
        panel = pd.DataFrame({
            'target_bank': ['A'], 'year': [2018], 'n_articles': [2],
            'sum_mention_density': [5.0],
            'llm_vote_score_w_sum_full': [2.0],
            'llm_vote_tone_vw_full': [0.4],   # = 2.0/5.0 物理口径
        })
        recs = _run_sentiment(panel)
        assert 'VW加权恒等式 (_full)' in recs, "VW 检查不得静默消失"
        assert recs['VW加权恒等式 (_full)']['status'] == 'PASS'

    def test_vw_true_mismatch_still_fails(self):
        # 守卫有效性: 真错配 (tone 与任何口径都不符) 仍须 FAIL。
        panel = pd.DataFrame({
            'target_bank': ['A'], 'year': [2018], 'n_articles': [2],
            'sum_mention_density': [5.0],
            'llm_vote_score_w_sum_full': [2.0],
            'llm_vote_tone_vw_full': [0.9],   # ≠ 2.0/5.0, 真错配
        })
        r = _run_sentiment(panel)['VW加权恒等式 (_full)']
        assert r['status'] == 'FAIL', "真错配必须仍能 FAIL"

    def test_hw_dual_track_denominators(self):
        # 修复前: 3e 找 legacy 单列 sum_herd_weight (v3.6.0 后不存在) → HW 检查
        # 静默死亡且 else 兜底排除 hw → 零记录。修复后: 按轨用
        # sum_herd_weight_full / sum_herd_weight_ctx, 两轨独立验证。
        panel = pd.DataFrame({
            'target_bank': ['A'], 'year': [2018], 'n_articles': [2],
            'sum_herd_weight_full': [4.0],
            'sum_herd_weight_ctx': [8.0],
            'llm_vote_score_hw_sum_full': [2.0],
            'llm_vote_score_hw_sum_ctx': [2.0],
            'llm_vote_tone_hw_full': [0.5],    # 2.0/4.0 (full 轨分母)
            'llm_vote_tone_hw_ctx': [0.25],    # 2.0/8.0 (ctx 轨分母)
        })
        recs = _run_sentiment(panel)
        assert recs['HW加权恒等式 (_full)']['status'] == 'PASS', \
            recs['HW加权恒等式 (_full)']['detail']
        # ctx 轨若误用 full 分母 (2.0/4.0=0.5 ≠ 0.25) 会 FAIL → 锁双轨独立
        assert recs['HW加权恒等式 (_ctx)']['status'] == 'PASS', \
            recs['HW加权恒等式 (_ctx)']['detail']

    def test_missing_columns_warn_not_silent(self):
        # 修复前: 旧 else 兜底仅当 'vw/mw 且 tone 列缺失' 才 WARN ('hw' 被排除;
        # 分子/分母缺失更是零记录)。修复后: 三种权重 × 双轨缺任一所需列即 WARN。
        panel = pd.DataFrame({
            'target_bank': ['A'], 'year': [2018], 'n_articles': [2],
            'pos_frac_full': [0.5], 'neg_frac_full': [0.2],
        })
        recs = _run_sentiment(panel)
        for wt in ['VW', 'MW', 'HW']:
            for track in ['_full', '_ctx']:
                check = f'{wt}加权恒等式 ({track})'
                assert check in recs, f"{check} 缺列时不得静默跳过"
                assert recs[check]['status'] == 'WARN'

    def test_partial_missing_numerator_warns(self):
        # tone 列在、分子列缺 → 修复前零记录 (else 兜底条件不触发), 修复后 WARN。
        panel = pd.DataFrame({
            'target_bank': ['A'], 'year': [2018], 'n_articles': [2],
            'sum_mention_density': [5.0],
            'llm_vote_tone_vw_full': [0.4],
        })
        r = _run_sentiment(panel)['VW加权恒等式 (_full)']
        assert r['status'] == 'WARN'
        assert 'llm_vote_score_w_sum_full' in r['detail']


class TestDtaPrecisionNanSymmetry:
    """g-stata-audit-03: 6d 须捕获 '值→缺失' 腐蚀 (NaN 位置不对称)."""

    def _panel(self) -> pd.DataFrame:
        return pd.DataFrame({
            'target_bank': ['A', 'B', 'C'], 'year': [2017, 2017, 2017],
            'n_articles': [105.0, 1.0, 2.0],
            'llm_vote_tone_full': [0.5, -0.2, 0.1],
            'ln_news_coverage': [1.0, 0.7, 1.1],
        })

    def test_value_to_missing_corruption_fails(self, tmp_path):
        # 模拟 KNOWN-OPEN ⑥ 腐蚀: parquet 值 105 在 .dta 中被静默改写为缺失。
        # 修复前: (dta-pq).abs().max() skipna 吞 NaN → max_diff=0.0 → PASS (失明)。
        panel = self._panel()
        corrupted = panel.copy()
        corrupted.loc[0, 'n_articles'] = np.nan
        dta_path = tmp_path / 'corrupted.dta'
        corrupted.to_stata(dta_path, write_index=False, version=118)

        recs = _run_stata_compat(panel, str(dta_path))
        assert '.dta NaN对齐-n_articles' in recs, "值→缺失腐蚀不得逃逸"
        assert recs['.dta NaN对齐-n_articles']['status'] == 'FAIL'
        # 未腐蚀列不应误报
        assert '.dta NaN对齐-llm_vote_tone_full' not in recs

    def test_aligned_nan_passes(self, tmp_path):
        # 两侧 NaN 位置一致 (合法缺失) → 无 NaN对齐 FAIL, 精度 PASS。
        panel = self._panel()
        panel.loc[1, 'llm_vote_tone_full'] = np.nan
        dta_path = tmp_path / 'aligned.dta'
        panel.to_stata(dta_path, write_index=False, version=118)

        recs = _run_stata_compat(panel, str(dta_path))
        assert '.dta NaN对齐-llm_vote_tone_full' not in recs
        assert recs['.dta 精度-llm_vote_tone_full']['status'] == 'PASS'
        assert recs['.dta 精度-n_articles']['status'] == 'PASS'

    def test_precision_compared_on_nonmissing_positions(self, tmp_path):
        # NaN 对齐 + 非缺失位置真有数值漂移 → 精度 WARN 仍能触发 (守卫有效性)。
        panel = self._panel()
        drifted = panel.copy()
        drifted.loc[2, 'llm_vote_tone_full'] = 0.1 + 0.01  # 漂移 > 0.001
        dta_path = tmp_path / 'drifted.dta'
        drifted.to_stata(dta_path, write_index=False, version=118)

        recs = _run_stata_compat(panel, str(dta_path))
        assert recs['.dta 精度-llm_vote_tone_full']['status'] == 'WARN'

    def test_row_count_mismatch_skips_elementwise_with_warn(self, tmp_path):
        # 行数不一致: 6c 已 FAIL; 6d 逐位比对显式 WARN 跳过 (numpy 长度守卫, 不崩)。
        panel = self._panel()
        dta_path = tmp_path / 'short.dta'
        panel.head(2).to_stata(dta_path, write_index=False, version=118)

        recs = _run_stata_compat(panel, str(dta_path))
        assert recs['.dta 行数一致性']['status'] == 'FAIL'
        assert recs['.dta 精度检查']['status'] == 'WARN'
