"""tests/test_omni_fix_runner.py — omni 审计 g-runner 组修复回归锁 (2026-06-11).

锁定 pipeline/panel/runner.py 的修复后行为 (防静默 revert):

  g-runner-01        BERT 2/3-class 概率尺度统一 → 逐模型 argmax 极性指示
  g-runner-02        7h-token 政策对齐族聚合域 semi-join 收敛到 verified 子集
  g-runner-03/-11    四象限 NaN 掩码: 测量失败行指示=NaN (非隐式 Irrelevant/伪 Token)
  g-runner-04        Bartik _t01 真池化基期 base_years=[T0,T0+1] + _t1 外生性守卫
  g-runner-05/-09    方法 F 高置信阈值 0.67 → 2/3 - 1e-9 (2/3 票档按声明纳入)
  g-runner-06/-15    log_sent 零覆盖 bank-year → NaN (对齐同族缺失语义)
  g-runner-07        四象限 ctx 孪生 (sim=policy_cosine_sim_ctx)
  g-runner-08        日志/注释计数动态化 (disag/洗稿变体/BERT 模型数)
  g-runner-10/-14    洗稿率分母同域化: 阳性 ∧ substantiveness 已测量
  g-runner-16        8c opt-in merge 新鲜度守卫 + 重复键 fail-loud
  组级裁决            article_sim_std 单观测 fillna(0) 删除 (保持 NaN)

全部用合成 DataFrame + tmp_path, 不依赖盘上数据, 无外部 API。

# 白话: runner.py 是把所有指标拼成最终面板的总装车间, 这组修复锁:
# BERT 判正负面改用"哪个概率最大"而不是"是否过 0.5"(三分类下 0.4 也可能是
# 最大); 测不出来的行记 NaN, 不能被当成 0 或被错误归类; "高/低覆盖银行"的
# 分组身份在基期就定死, 不随后续年份翻转(防内生); 合并可选特征文件前检查
# 它比上游数据新(防拼进过期数据), 键重复直接报错。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

from news_process.pipeline.panel.runner import (  # noqa: E402
    HC_AGREEMENT_THRESHOLD,
    _base_year_median_split,
    _bert_argmax_pos_neg,
    _classify_policy_quadrants,
    _filter_to_verified_universe,
    _gated_log_sent,
    _merge_optin_feature_panels,
    _pool_svd_substvalid_counts,
)

pytestmark = pytest.mark.fast

_RUNNER_PATH = (Path(__file__).resolve().parents[1]
                / "pipeline" / "panel" / "runner.py")


def _runner_src() -> str:
    return _RUNNER_PATH.read_text(encoding="utf-8")


# ============================================================================
# g-runner-01 — BERT argmax 极性指示 (类数尺度不变量)
# ============================================================================

class TestBertArgmax:
    def test_three_class_argmax_below_half(self):
        """3-class: P(正)=0.4 为 argmax → 正面 (旧 >0.5 阈值会误判 False)."""
        df = pd.DataFrame({
            'm_正面_full': [0.40, 0.20, 0.34],
            'm_负面_full': [0.30, 0.50, 0.33],
            'm_中性_full': [0.30, 0.30, 0.33],
        })
        pos, neg = _bert_argmax_pos_neg(df, 'm', '_full')
        assert pos.tolist() == [True, False, True]
        assert neg.tolist() == [False, True, False]

    def test_three_class_tie_is_neither(self):
        """3-class 平局 (P 正 == P 负) → 两者均 False."""
        df = pd.DataFrame({
            'm_正面_full': [0.4], 'm_负面_full': [0.4], 'm_中性_full': [0.2]})
        pos, neg = _bert_argmax_pos_neg(df, 'm', '_full')
        assert not pos.iloc[0] and not neg.iloc[0]

    def test_two_class_keeps_half_threshold(self):
        """2-class (无中性列): P>0.5 ⇔ argmax, 与旧行为逐位一致."""
        df = pd.DataFrame({
            'm2_正面_full': [0.6, 0.5, 0.4],
            'm2_负面_full': [0.4, 0.5, 0.6],
        })
        pos, neg = _bert_argmax_pos_neg(df, 'm2', '_full')
        assert pos.tolist() == [True, False, False]
        assert neg.tolist() == [False, False, True]

    def test_missing_negative_column_degrades(self):
        """缺负面概率列 → neg=None (调用方跳过 negative 编码), pos 退化 >0.5."""
        df = pd.DataFrame({'m3_正面_full': [0.7, 0.3]})
        pos, neg = _bert_argmax_pos_neg(df, 'm3', '_full')
        assert neg is None
        assert pos.tolist() == [True, False]

    def test_nan_probability_is_neither(self):
        """NaN 概率行 → pos/neg 均 False (与旧 >0.5 行为一致)."""
        df = pd.DataFrame({
            'm_正面_full': [np.nan], 'm_负面_full': [0.3], 'm_中性_full': [0.3]})
        pos, neg = _bert_argmax_pos_neg(df, 'm', '_full')
        assert not pos.iloc[0] and not neg.iloc[0]

    # fix(dta-coverage-audit, 2026-07-03) 回归护栏: 生产 finbert2 parquet 形态是
    # "2-class + 全 NaN `_中性` 占位列" (tone_berts 刻意补列), 与上方 m2 用例的
    # "无中性列"不同。曾因仅凭列存在判 3-class 致 finbert2 判正 0/1005 篇、
    # washing_ratio_finbert2 三轨全 NaN。以下用例锚死修复语义, 防"等价清理"复发。
    def test_two_class_all_nan_neutral_placeholder_uses_half_threshold(self):
        """finbert2 实况: 中性列在场但全 NaN 占位 → 必须走 2-class P>0.5."""
        df = pd.DataFrame({
            'finbert2_正面_full': [0.8, 0.3, 0.6],
            'finbert2_负面_full': [0.2, 0.7, 0.4],
            'finbert2_中性_full': [np.nan, np.nan, np.nan],
        })
        pos, neg = _bert_argmax_pos_neg(df, 'finbert2', '_full')
        assert pos.tolist() == [True, False, True]
        assert neg.tolist() == [False, True, False]

    def test_three_class_ssot_model_never_falls_to_half_threshold(self):
        """SSOT 注册的 3-class 模型 (finbert_cn) 中性列即便损坏为全 NaN, 也须
        留在 argmax 分支输出全 False (NaN 行契约), 绝不退到 P>0.5 尺度混用
        (P(正)=0.55>0.5 若走 2-class 路径会误判 True)."""
        df = pd.DataFrame({
            'finbert_cn_正面_full': [0.55],
            'finbert_cn_负面_full': [0.45],
            'finbert_cn_中性_full': [np.nan],
        })
        pos, neg = _bert_argmax_pos_neg(df, 'finbert_cn', '_full')
        assert not pos.iloc[0] and not neg.iloc[0]

    def test_unknown_model_with_real_neutral_values_uses_argmax(self):
        """SSOT 外模型但中性列真有值 → 数据驱动兜底走 argmax."""
        df = pd.DataFrame({
            'mx_正面_full': [0.40], 'mx_负面_full': [0.30], 'mx_中性_full': [0.30]})
        pos, neg = _bert_argmax_pos_neg(df, 'mx', '_full')
        assert pos.iloc[0] and not neg.iloc[0]


# ============================================================================
# g-runner-05/-09 — 方法 F 高置信阈值
# ============================================================================

class TestHcThreshold:
    def test_two_thirds_included(self):
        """支撑集 {1/3, 2/3, 1.0}: 2/3 票档须按声明的 '≥ 2/3' 纳入."""
        rates = pd.Series([1.0 / 3.0, 2.0 / 3.0, 1.0])
        hc = rates >= HC_AGREEMENT_THRESHOLD
        assert hc.tolist() == [False, True, True]

    def test_threshold_value(self):
        assert pytest.approx(2.0 / 3.0 - 1e-9) == HC_AGREEMENT_THRESHOLD
        assert HC_AGREEMENT_THRESHOLD < 2.0 / 3.0

    def test_no_hardcoded_067_in_active_code(self):
        """旧 `>= 0.67` 字面量不得回潮 (仅允许出现在 fix 注释里)."""
        for line in _runner_src().splitlines():
            code = line.split('#', 1)[0]
            assert '>= 0.67' not in code, f"0.67 阈值回潮: {line.strip()}"


# ============================================================================
# g-runner-10/-14 — substvalid 同域分母
# ============================================================================

class TestSvdPooling:
    def test_pool_and_rename(self):
        frame = pd.DataFrame({
            'target_bank': ['A', 'A', 'B'],
            'year': [2017, 2017, 2017],
            '_svd_pos_full': [1, 0, 1],
            '_svd_neg_ctx': [0, 1, 1],
            'other_col': [9, 9, 9],   # 非 _svd_ 列不入聚合
        })
        out = _pool_svd_substvalid_counts(frame)
        assert set(out.columns) == {'target_bank', 'year',
                                    'pos_substvalid_count_full',
                                    'neg_substvalid_count_ctx'}
        a = out[out['target_bank'] == 'A'].iloc[0]
        assert a['pos_substvalid_count_full'] == 1
        assert a['neg_substvalid_count_ctx'] == 1

    def test_no_svd_columns_returns_none(self):
        frame = pd.DataFrame({'target_bank': ['A'], 'year': [2017], 'x': [1]})
        assert _pool_svd_substvalid_counts(frame) is None

    def test_missing_year_returns_none(self):
        frame = pd.DataFrame({'target_bank': ['A'], '_svd_pos_full': [1]})
        assert _pool_svd_substvalid_counts(frame) is None

    def test_washing_denominators_wired_to_substvalid(self):
        """7h 各方法分母须经 _svd_denom 走 substvalid 计数 (防回退物理分母)."""
        src = _runner_src()
        for pat in ("_svd_denom(f'pos_substvalid_count{track}'",
                    "_svd_denom(f'neg_substvalid_count{track}'",
                    "_svd_denom(f'dict_pos_substvalid_count{track}'",
                    "_svd_denom(f'bert_pos_substvalid_count{track}'",
                    "_svd_denom(f'pos_hc_substvalid_count{track}'",
                    "_svd_denom(f'{llm}_pos_substvalid_count{track}'",
                    "_svd_denom(f'{d}_pos_substvalid_count{track}'",
                    "_svd_denom(f'{b}_pos_substvalid_count{track}'"):
            assert pat in src, f"洗稿率分母未接 substvalid: {pat}"


# ============================================================================
# g-runner-12/-13 — pre-period 固定切分
# ============================================================================

class TestBaseYearMedianSplit:
    def _panel(self):
        return pd.DataFrame({
            'target_bank': ['A', 'B', 'C', 'A', 'B', 'C'],
            'year': [2017, 2017, 2017, 2018, 2018, 2018],
            # 2018 覆盖量大翻转: A 10→1, B 2→50 — 身份须仍由 2017 决定
            'n_articles': [10, 2, 0, 1, 50, 5],
            'bank_type': ['X', 'X', 'X', 'X', 'X', 'X'],
        })

    def test_membership_frozen_at_base_year(self):
        panel = self._panel()
        member = _base_year_median_split(panel, value_col='n_articles')
        panel['m'] = member
        # 基年 median([10,2])=6 → A=1, B=0; C 基年零覆盖 → 0
        for yr in (2017, 2018):
            sub = panel[panel['year'] == yr].set_index('target_bank')['m']
            assert sub['A'] == 1, f"A@{yr}"
            assert sub['B'] == 0, f"B@{yr} (2018 年 50 篇也不得翻转)"
            assert sub['C'] == 0, f"C@{yr}"

    def test_by_group_split(self):
        panel = pd.DataFrame({
            'target_bank': ['A', 'B', 'C', 'D'] * 2,
            'year': [2017] * 4 + [2018] * 4,
            'n_articles': [10, 2, 8, 4] * 2,
            'bank_type': ['X', 'X', 'Y', 'Y'] * 2,
        })
        m = _base_year_median_split(panel, value_col='n_articles',
                                    by='bank_type')
        panel['m'] = m
        sub = panel[panel['year'] == 2017].set_index('target_bank')['m']
        # X 组 median([10,2])=6 → A=1,B=0; Y 组 median([8,4])=6 → C=1,D=0
        assert (sub['A'], sub['B'], sub['C'], sub['D']) == (1, 0, 1, 0)

    def test_bank_absent_in_base_year_gets_zero(self):
        panel = pd.DataFrame({
            'target_bank': ['A', 'B', 'A', 'B', 'E'],
            'year': [2017, 2017, 2018, 2018, 2018],
            'n_articles': [10, 2, 1, 50, 100],
        })
        m = _base_year_median_split(panel, value_col='n_articles')
        panel['m'] = m
        # E 不在基年 → 0 (无前定信息, 不得用 2018 自身实现值)
        assert panel.loc[panel['target_bank'] == 'E', 'm'].iloc[0] == 0

    def test_runner_no_per_year_median_split(self):
        """同年 groupby(...'year')['n_articles'].transform('median') 切分模式
        不得回潮 (digital_frontier / high_coverage 均改 pre-period 固定切分)."""
        src = _runner_src()
        assert "'year')['n_articles'].transform('median')" not in src
        assert src.count('_base_year_median_split(') >= 3  # def + 2 调用
        assert "by='bank_type')" in src  # digital_frontier 组内切分


# ============================================================================
# g-runner-02 — verified 聚合域
# ============================================================================

class TestVerifiedUniverse:
    def test_semi_join_filters_unverified(self):
        df_align = pd.DataFrame({
            'docid': ['d1', 'd2', 'd3'],
            'target_bank': ['A', 'A', 'B'],
            'policy_cosine_sim': [0.1, 0.2, 0.3],
        })
        df_exploded = pd.DataFrame({
            'docid': ['d1', 'd3', 'd3'],          # 重复 verified 键安全
            'target_bank': ['A', 'B', 'B'],
        })
        out = _filter_to_verified_universe(df_align, df_exploded)
        assert len(out) == 2
        assert set(out['docid']) == {'d1', 'd3'}
        # 行不被 dup 放大 (semi-join 语义)
        assert out['docid'].is_unique

    def test_missing_keys_passthrough(self):
        df_align = pd.DataFrame({'target_bank': ['A'], 'x': [1]})
        df_exploded = pd.DataFrame({'target_bank': ['A']})
        out = _filter_to_verified_universe(df_align, df_exploded)
        assert out is df_align  # 旧 schema 原样返回 (warning 路径)

    def test_runner_wires_filter_before_aggregation(self):
        assert "_filter_to_verified_universe(df_align, df_exploded)" \
            in _runner_src()


# ============================================================================
# g-runner-03/-07/-11 — 四象限 NaN 掩码 + ctx 孪生
# ============================================================================

class TestQuadrantClassification:
    def test_measured_rows_classified(self):
        df = pd.DataFrame({
            'year': [2017, 2017],
            'sim': [0.9, 0.1],
            'freq': [1.0, 10.0],
        })
        tok, hid, sub = _classify_policy_quadrants(df, 'sim', 'freq', 50)
        # p50(sim)=0.5, p50(freq)=5.5
        assert tok.tolist() == [0.0, 1.0]   # 高频低相似 = Token
        assert hid.tolist() == [1.0, 0.0]   # 低频高相似 = Hidden
        assert sub.tolist() == [0.0, 0.0]

    def test_nan_rows_excluded_not_misclassified(self):
        """sim/freq 任一 NaN → 三指示均 NaN (旧行为: NaN>=thresh→False→伪归类)."""
        df = pd.DataFrame({
            'year': [2017, 2017, 2017, 2017],
            'sim': [0.1, 0.9, np.nan, 0.8],
            'freq': [1.0, 10.0, 5.0, np.nan],
        })
        tok, hid, sub = _classify_policy_quadrants(df, 'sim', 'freq', 50)
        for s in (tok, hid, sub):
            assert np.isnan(s.iloc[2]) and np.isnan(s.iloc[3])
        # 已测量行照常分类 (定义域一致: 阈值与分类均只看已测量)
        assert not np.isnan(tok.iloc[0]) and not np.isnan(tok.iloc[1])

    def test_all_nan_sim_yields_all_nan(self):
        """stage 15 优雅早退全 NaN parquet → 全部指示 NaN (旧行为: 高词频全归
        Token, 由零测量制造非 NaN 面板值)."""
        df = pd.DataFrame({
            'year': [2017, 2017, 2017],
            'sim': [np.nan] * 3,
            'freq': [1.0, 5.0, 10.0],
        })
        tok, hid, sub = _classify_policy_quadrants(df, 'sim', 'freq', 50)
        assert tok.isna().all() and hid.isna().all() and sub.isna().all()
        # groupby mean 在全 NaN 上输出 NaN → 面板侧为 NaN 而非伪零
        assert np.isnan(tok.mean())

    def test_runner_wires_ctx_twin(self):
        """四象限 ctx 孪生须接线 (sim 轨循环 + _ctx 列名后缀).

        2026-06-21: _sim_tracks 改由 anchor 变体 (_anc_base) f-string 构造以支持
        全年份 _allv 孪生 (`f'{_anc_base}_ctx'`), 故 ctx 接线断言更新为 f-string 形式。"""
        src = _runner_src()
        assert "_sim_tracks" in src
        assert "f'{_anc_base}_ctx'" in src, "ctx 孪生须经 anchor 变体 f-string 接线"
        assert "token_adopt_{_k}" in src
        assert src.count('_classify_policy_quadrants(') >= 2  # def + 调用

    def test_runner_wires_allv_anchor_variant(self):
        """全年份锚点 _allv 四象限孪生须接线 (anchor 变体外层循环 + _anc_sfx 进列名键)."""
        src = _runner_src()
        assert "_anchor_variants" in src, "缺 anchor 变体外层循环"
        assert "('_allv', 'policy_cosine_sim_allv')" in src, "缺 _allv 全年份锚点变体"
        # 占比列名键须含 anchor 后缀 (_anc_sfx) → token_adopt_kw_p25_allv_ctx 等
        assert "{_anc_sfx}{_sim_sfx}" in src, "四象限列名键须插入 anchor 后缀"
        # 连续聚合 + co-primary _lg 聚合的 _allv 孪生 (v3.14.0: 本地 _t2v 已删,
        # _lg=text-embedding-3-large 是 runner 的嵌入 co-primary 源)
        assert "article_sim_mean_allv" in src
        assert "policy_cosine_sim_lg_allv_full" in src


# ============================================================================
# g-runner-06/-15 — log_sent 覆盖门控
# ============================================================================

class TestGatedLogSent:
    def _panel(self):
        return pd.DataFrame({
            'n_articles': [0, 3, 2],
            'pos_count_full': [0, 2, 1],
            'neg_count_full': [0, 1, 1],
        })

    def test_zero_coverage_is_nan(self):
        ls = _gated_log_sent(self._panel(), '_full')
        assert np.isnan(ls.iloc[0]), "零覆盖 bank-year 须 NaN 而非伪中性 0"

    def test_covered_rows_keep_formula(self):
        ls = _gated_log_sent(self._panel(), '_full')
        assert ls.iloc[1] == pytest.approx(np.log1p(2) - np.log1p(1))

    def test_true_balanced_zero_retained(self):
        """有覆盖且 1正1负 → 真实测量 0.0 保留 (与伪零可区分)."""
        ls = _gated_log_sent(self._panel(), '_full')
        assert ls.iloc[2] == 0.0 and not np.isnan(ls.iloc[2])

    def test_nan_counts_treated_as_zero_within_coverage(self):
        panel = pd.DataFrame({
            'n_articles': [4],
            'pos_count_full': [np.nan],   # balance 前的 NaN 计数
            'neg_count_full': [2.0],
        })
        ls = _gated_log_sent(panel, '_full')
        assert ls.iloc[0] == pytest.approx(0.0 - np.log1p(2))

    def test_runner_wires_gated_log_sent(self):
        src = _runner_src()
        assert "panel[f'log_sent{track}'] = _gated_log_sent(panel, track)" in src

    # ── F5 (2026-07-16, FATAL_DEFECT_REMEDIATION §2-F5): ctx/ss 轨 per-track
    #    有效票门控 (此前统一用 full 轨 n_articles → "有覆盖但该轨全无效" 的
    #    bank-year 被注入伪中性 0.0, 盘上实测 ctx 15 行 / ss 11 行) ──

    def test_f5_t1_ctx_track_invalid_is_nan(self):
        """ctx 轨: 有覆盖 (n_articles=5) 但该轨 LLM 全部无效 (valid_ctx=0,
        pos/neg 合法为 0) → NaN (旧实现输出伪中性 0.0)。"""
        panel = pd.DataFrame({
            'n_articles': [5],
            'n_articles_llm_valid_ctx': [0],
            'pos_count_ctx': [0],
            'neg_count_ctx': [0],
        })
        ls = _gated_log_sent(panel, '_ctx')
        assert np.isnan(ls.iloc[0]), "该轨零有效票须 NaN 而非伪中性 0.0"

    def test_f5_t2_ctx_track_valid_formula_unchanged(self):
        """ctx 轨有有效票时数值公式不变。ss 轨同式 (共用实现)。"""
        panel = pd.DataFrame({
            'n_articles': [5],
            'n_articles_llm_valid_ctx': [3],
            'pos_count_ctx': [2],
            'neg_count_ctx': [1],
        })
        ls = _gated_log_sent(panel, '_ctx')
        assert ls.iloc[0] == pytest.approx(np.log1p(2) - np.log1p(1))

    def test_f5_t3_full_track_bitwise_unchanged(self):
        """full 轨行为逐位保持 (门控列仍为物理 n_articles, 字节稳定)。"""
        panel = pd.DataFrame({
            'n_articles': [0, 3, 2],
            'n_articles_llm_valid': [0, 0, 0],   # 即便 full valid 全 0
            'pos_count_full': [0, 2, 1],
            'neg_count_full': [0, 1, 1],
        })
        ls = _gated_log_sent(panel, '_full')
        assert np.isnan(ls.iloc[0])
        assert ls.iloc[1] == pytest.approx(np.log1p(2) - np.log1p(1))
        assert ls.iloc[2] == 0.0

    def test_f5_t4_missing_valid_col_falls_back(self):
        """旧 schema 缺 n_articles_llm_valid_ss → 回退 n_articles 门控 (不崩)。"""
        panel = pd.DataFrame({
            'n_articles': [0, 4],
            'pos_count_ss': [0, 1],
            'neg_count_ss': [0, 2],
        })
        ls = _gated_log_sent(panel, '_ss')
        assert np.isnan(ls.iloc[0])
        assert ls.iloc[1] == pytest.approx(np.log1p(1) - np.log1p(2))


# ============================================================================
# g-runner-04 — Bartik _t01 真池化基期 + _t1 守卫 (runner 侧接线)
# ============================================================================

class TestBartikT01Wiring:
    def test_t01_uses_base_years_interface(self):
        """_t01 须传全量 df_exploded + base_years=[T0,T0+1] (iv_did 池化接口)."""
        src = _runner_src()
        assert "base_years=[T0, T0 + 1]" in src
        # 旧幻影实现 (年份子集当全量传入) 不得回潮
        assert ".isin([T0, T0+1])" not in src
        assert "base_t01" not in src

    def test_t1_exogeneity_guard_present(self):
        """_t1/_t01 基期落入政策冲击区间 → 置 NaN 跳过 (外生性守卫)."""
        src = _runner_src()
        assert "base_yr >= _bartik_pre_cutoff" in src
        assert "_bartik_pre_cutoff <= T0 + 1" in src

    def test_ivdid_signature_has_base_years(self):
        """核对 iv_did 新接口签名 (g-ivdid 组实现) — 接线前提."""
        import inspect

        from news_process.pipeline.panel.iv_did import compute_bartik_iv
        assert 'base_years' in inspect.signature(compute_bartik_iv).parameters


# ============================================================================
# g-runner-08 — 日志计数动态化
# ============================================================================

class TestDynamicCounts:
    def test_disag_log_is_dynamic(self):
        src = _runner_src()
        assert "({_disag_n} 变量)" in src
        assert '完成 (32 变量)")' not in src

    def test_log_sent_log_is_dynamic(self):
        src = _runner_src()
        assert "({_log_sent_n} 变量" in src
        assert 'log_sent 指标计算完成 (2 变量)")' not in src

    def test_washing_header_no_stale_counts(self):
        """步骤 7h 标题不再硬编码 '(40种)' (变体数以 wr_variants 动态日志为准)."""
        src = _runner_src()
        assert '双轨构造 (40种)' not in src


# ============================================================================
# 组级裁决 — article_sim_std 单观测 fillna(0) 删除
# ============================================================================

class TestArticleSimStdNoFill:
    def test_no_fillna_on_article_sim_std(self):
        src = _runner_src()
        assert "article_sim_std'].fillna" not in src
        assert "article_sim_std_ctx'].fillna" not in src


# ============================================================================
# g-runner-16 — 8c opt-in merge 新鲜度守卫 + 重复键 fail-loud
# ============================================================================

class TestOptinFeatureMerge:
    @staticmethod
    def _panel():
        return pd.DataFrame({
            'target_bank': ['工商', '建设'],
            'year': [2018, 2018],
            'llm_vote_tone_full': [0.1, -0.2],
        })

    def test_graceful_noop_when_file_absent(self, tmp_path):
        panel = self._panel()
        out = _merge_optin_feature_panels(panel.copy(), str(tmp_path))
        pd.testing.assert_frame_equal(out, panel)

    def test_fresh_feature_merged(self, tmp_path):
        feat = pd.DataFrame({
            'target_bank': ['工商'], 'year': [2018],
            'surface_staleness_full': [0.5],
        })
        fpath = tmp_path / '26_staleness_panel.parquet'
        feat.to_parquet(fpath, index=False)
        # 上游存在但 mtime 更旧 → 新鲜, 照常合并
        up = tmp_path / '24_herd_decay.parquet'
        pd.DataFrame({'docid': ['d1']}).to_parquet(up, index=False)
        t = os.path.getmtime(fpath)
        os.utime(up, (t - 1000, t - 1000))
        out = _merge_optin_feature_panels(self._panel(), str(tmp_path))
        assert 'surface_staleness_full' in out.columns
        assert len(out) == 2
        assert out.loc[out['target_bank'] == '工商',
                       'surface_staleness_full'].iloc[0] == 0.5
        assert pd.isna(out.loc[out['target_bank'] == '建设',
                               'surface_staleness_full'].iloc[0])

    def test_stale_feature_skipped(self, tmp_path):
        """特征文件早于其登记上游 (数据代际陈旧) → 跳过 merge 而非静默并入."""
        feat = pd.DataFrame({
            'target_bank': ['工商'], 'year': [2018],
            'cross_outlet_tone_variance_full': [0.5],
        })
        fpath = tmp_path / '75_cross_media_alpha.parquet'
        feat.to_parquet(fpath, index=False)
        up = tmp_path / '21_tone_llms.parquet'
        pd.DataFrame({'docid': ['d1']}).to_parquet(up, index=False)
        t = os.path.getmtime(up)
        os.utime(fpath, (t - 1000, t - 1000))   # 特征文件比上游旧
        out = _merge_optin_feature_panels(self._panel(), str(tmp_path))
        assert 'cross_outlet_tone_variance_full' not in out.columns, \
            "陈旧代际的 39f 不得并入面板"

    def test_duplicate_keys_raise(self, tmp_path):
        feat = pd.DataFrame({
            'target_bank': ['工商', '工商'], 'year': [2018, 2018],
            'surface_staleness_full': [0.5, 0.9],
        })
        feat.to_parquet(tmp_path / '26_staleness_panel.parquet', index=False)
        with pytest.raises(RuntimeError, match="键重复"):
            _merge_optin_feature_panels(self._panel(), str(tmp_path))

    def test_existing_panel_column_not_overwritten(self, tmp_path):
        feat = pd.DataFrame({
            'target_bank': ['工商'], 'year': [2018],
            'llm_vote_tone_full': [9.9],          # 与面板既有列同名
            'surface_staleness_full': [0.5],
        })
        feat.to_parquet(tmp_path / '26_staleness_panel.parquet', index=False)
        out = _merge_optin_feature_panels(self._panel(), str(tmp_path))
        assert out.loc[out['target_bank'] == '工商',
                       'llm_vote_tone_full'].iloc[0] == 0.1
        assert 'surface_staleness_full' in out.columns

    def test_missing_keys_skipped(self, tmp_path):
        feat = pd.DataFrame({'bank': ['工商'], 'val': [1.0]})
        feat.to_parquet(tmp_path / '26_staleness_panel.parquet', index=False)
        out = _merge_optin_feature_panels(self._panel(), str(tmp_path))
        assert 'val' not in out.columns

    def test_runner_wires_helper(self):
        src = _runner_src()
        assert "panel = _merge_optin_feature_panels(panel, OUTPUT_DIR)" in src
