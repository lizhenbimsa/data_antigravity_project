"""
test_omni_fix_panel_export.py — omni 审计修复回归锁 (g-panel-export 组, 2026-06-11)
================================================================================
锁定 8 条 confirmed 缺陷的修复后行为 (fix omni-g-panel-export-01..-08), 防静默
revert。全部使用合成 DataFrame / 源码静态解析, 不依赖盘上大数据、不调外部 API。

覆盖:
  -01 deepseekv4 标签供应商归属 (Grok-4.1 → DeepSeek-V4)
  -02 STATA_LABELS 陈旧键 (herd 无后缀 / bartik_fintech 旧命名) → 双轨/lf+lc 活跃键
  -03 27 个幻影 Bartik 维度 (~50 键) 移除
  -04 leave1out_dict 列名压缩 (33 字符 → dict_tone 词干, full/ctx 对称 ≤32)
  -05 low_conf_flag 物化移出 log_diagnostics (诊断纯只读 + schema 不随数据漂移)
  -06 .dta 变量标签覆盖率兜底 (_apply_label_fallback, 100% 覆盖)
  -07 [v3.14.0 删除] 原 t2v 标签 40/46-path 同步锁 — 本地 text2vec(_t2v) 整体移除,
      export.py STATA_LABELS 不再含任何嵌入 anchor 标签 (单一源收敛到 stata_export)
  -08 ai_reg_* 构念勘误 (AI Imitation Rate → Peer FinTech Coverage Penetration)

# 白话: 面板导出给 Stata 时, 每个变量都带一个英文标签当"名牌"。这组测试守住:
# 名牌上不能写编造的模型名(Grok)和名不副实的构念(变量算的是同行报道覆盖率,
# 名牌却写 AI 模仿率); 已改名的变量旧名牌要删干净; 根本不存在的变量不该有
# 名牌; 每个真实变量都必须有名牌且符合 Stata 的 80 字符/latin-1 限制;
# 列名压到 32 字符内, full/ctx 两轨名字保持对称。
"""
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# 注入 news_process 父目录, 解析 ``news_process.*`` (与既有测试一致)
_PROJECT_PARENT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.pipeline.panel import export as _exp  # noqa: E402
from news_process.pipeline.panel import geography as _geo  # noqa: E402

# ============================================================================
# 共用: 从 export.py 源码提取 STATA_LABELS 字典字面量并求值
# (dict 仍为 export_panel 函数局部; 复用 test_40_panel_export_main 的
#  brace-matching 技术, 但 eval 整个字面量以同时覆盖 ** 推导式展开的键)
# ============================================================================

def _load_stata_labels() -> dict:
    src = Path(_exp.__file__).read_text(encoding='utf-8')
    m = re.search(r'STATA_LABELS\s*=\s*\{', src)
    assert m, "找不到 STATA_LABELS 字典字面量"
    start = m.end() - 1
    depth = 0
    end = start
    for i, ch in enumerate(src[start:], start):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    # 纯字面量 (str/list/dict 推导式), 空 builtins 下可安全求值
    return eval(src[start:end], {'__builtins__': {}})  # noqa: S307


@pytest.fixture(scope='module')
def stata_labels() -> dict:
    return _load_stata_labels()


# ============================================================================
# fix-01: deepseekv4 供应商归属
# ============================================================================

class TestDeepseekVendorLabel:
    def test_deepseek_conf_labels_corrected(self, stata_labels):
        assert stata_labels['avg_deepseekv4_conf_full'] == 'DeepSeek-V4 Confidence (Full)'
        assert stata_labels['avg_deepseekv4_conf_ctx'] == 'DeepSeek-V4 Confidence (Ctx)'

    def test_no_grok_attribution_anywhere_in_labels(self, stata_labels):
        """单一事实源 config/sentiment.yaml: 阵容 OpenAI+Google+DeepSeek, 无 Grok."""
        offenders = [k for k, v in stata_labels.items() if 'grok' in v.lower()]
        assert not offenders, f"标签值仍含 Grok 归属: {offenders}"

    def test_attention_media_comment_corrected(self):
        from news_process.pipeline.panel import attention_media as _am
        src = Path(_am.__file__).read_text(encoding='utf-8')
        assert 'DeepSeek V4 Flash' in src


# ============================================================================
# fix-02: 陈旧键 → 活跃双轨键 (herd 权重 + fintech Bartik lf/lc)
# ============================================================================

class TestStaleKeysReplaced:
    HERD_STALE = ['avg_herd_weight', 'min_herd_weight']
    HERD_ACTIVE = [
        'avg_herd_weight_full', 'avg_herd_weight_ctx',
        'min_herd_weight_full', 'min_herd_weight_ctx',
        'sum_herd_weight_full', 'sum_herd_weight_ctx',
    ]
    BARTIK_STALE = [
        'bartik_fintech_iv_full', 'bartik_fintech_iv_ctx',
        'bartik_fintech_share_tech', 'bartik_fintech_share_app',
    ]
    BARTIK_ACTIVE = [
        'bartik_fintech_lf_iv_full', 'bartik_fintech_lf_iv_ctx',
        'bartik_fintech_lf_share_tech', 'bartik_fintech_lf_share_app',
        'bartik_fintech_lc_iv_full', 'bartik_fintech_lc_iv_ctx',
        'bartik_fintech_lc_share_tech', 'bartik_fintech_lc_share_app',
    ]

    def test_herd_stale_keys_gone(self, stata_labels):
        for k in self.HERD_STALE:
            assert k not in stata_labels, f"陈旧键 {k} 不应存在 (v3.6.0 双轨化)"

    def test_herd_dual_track_keys_present(self, stata_labels):
        for k in self.HERD_ACTIVE:
            assert k in stata_labels, f"活跃双轨列 {k} 缺标签"

    def test_bartik_fintech_stale_keys_gone(self, stata_labels):
        for k in self.BARTIK_STALE:
            assert k not in stata_labels, f"陈旧键 {k} 不应存在 (v3.2 lf/lc 双套)"

    def test_bartik_fintech_lf_lc_keys_present(self, stata_labels):
        for k in self.BARTIK_ACTIVE:
            assert k in stata_labels, f"活跃 Bartik 列 {k} 缺标签"

    def test_stata_audit_core_vars_updated(self):
        from news_process.pipeline.audit import stata_audit as _audit
        src = Path(_audit.__file__).read_text(encoding='utf-8')
        assert re.search(r"'avg_herd_weight'", src) is None, \
            "stata_audit.py 仍引用陈旧列名 'avg_herd_weight'"
        assert "'avg_herd_weight_full'" in src
        assert "'avg_herd_weight_ctx'" in src


# ============================================================================
# fix-03: 幻影 Bartik 维度标签移除 (无生产代码的 27 族)
# ============================================================================

class TestPhantomBartikRemoved:
    PHANTOM_DIMS = [
        'mcentral', 'mfin', 'mcomp', 'mofficial', 'mmarket', 'mfreq',
        'mdeep', 'mdaily', 'mprov', 'doclen', 'half', 'qtr', 'month',
        'wkday', 'excl', 'title', 'mden', 'mcount', 'breadth', 'sentlen',
        'ttr', 'pubfmt', 'author', 'page', 'pgnum', 'kwdiv', 'kwden',
    ]
    # runner.py 实际调用的七族 (compute_bartik_iv / compute_bartik_iv_fintech)
    REAL_FAMILY_KEYS = [
        'bartik_type_iv_full', 'bartik_type_share_soe',
        'bartik_scale_iv_full', 'bartik_scale_share_L',
        'bartik_media_iv_full', 'bartik_media_share_fin',
        'bartik_mauth_iv_full', 'bartik_mauth_share_high',
        'bartik_geoprox_iv_full', 'bartik_geoprox_iv_ctx',
        'bartik_fintech_lf_iv_full', 'bartik_fintech_lc_iv_full',
        'bartik_type_iv_full_t0', 'bartik_type_iv_ctx_t01',
    ]

    def test_phantom_dims_absent(self, stata_labels):
        offenders = [
            k for k in stata_labels
            if any(k.startswith(f'bartik_{dim}_') for dim in self.PHANTOM_DIMS)
        ]
        assert not offenders, (
            f"幻影 Bartik 键回潮 ({len(offenders)} 个, 全仓无生产代码): "
            f"{offenders[:10]}"
        )

    def test_real_families_kept(self, stata_labels):
        for k in self.REAL_FAMILY_KEYS:
            assert k in stata_labels, f"真实 Bartik 族键 {k} 被误删"


# ============================================================================
# fix-04: leave1out_dict 列名压缩 (产生端) + 标签 + 32 字符对称
# ============================================================================

def _loo_panel() -> pd.DataFrame:
    rows = []
    banks = ['A银行', 'B银行', 'C银行']
    for year in (2017, 2018):
        for i, b in enumerate(banks):
            rows.append({
                'target_bank': b, 'year': year,
                'bank_province': '广东省', 'bank_city': '深圳市',
                'llm_vote_tone_full': 0.1 * (i + 1),
                'llm_vote_tone_ctx': 0.1 * (i + 1) - 0.05,
                'dict_avg_tone_full': 0.2 * (i + 1),
                'dict_avg_tone_ctx': 0.2 * (i + 1) + 0.01,
                'bert_avg_pos_full': 0.3 + 0.1 * i,
                'bert_avg_pos_ctx': 0.25 + 0.1 * i,
            })
    return pd.DataFrame(rows)


class TestLooDictToneRename:
    NEW_COLS = [
        'prov_leave1out_dict_tone_full', 'prov_leave1out_dict_tone_ctx',
        'city_leave1out_dict_tone_full', 'city_leave1out_dict_tone_ctx',
        'prov_leave1out_bert_avg_pos_full', 'prov_leave1out_bert_avg_pos_ctx',
        'city_leave1out_bert_avg_pos_full', 'city_leave1out_bert_avg_pos_ctx',
    ]
    OLD_COLS = [
        'prov_leave1out_dict_avg_tone_full', 'prov_leave1out_dict_avg_tone_ctx',
        'city_leave1out_dict_avg_tone_full', 'city_leave1out_dict_avg_tone_ctx',
    ]

    def test_renamed_columns_produced_and_old_gone(self):
        out = _geo.compute_leave_one_out_sentiment(_loo_panel())
        for c in self.NEW_COLS:
            assert c in out.columns, f"产生端缺新列 {c}"
        for c in self.OLD_COLS:
            assert c not in out.columns, f"旧 33/32 字符列名 {c} 不应再产出"

    def test_all_loo_columns_within_stata_32_and_track_symmetric(self):
        out = _geo.compute_leave_one_out_sentiment(_loo_panel())
        loo_cols = [c for c in out.columns if '_leave1out_' in c]
        too_long = [c for c in loo_cols if len(c) > 32]
        assert not too_long, f"LOO 列名超 Stata 32 字符上限: {too_long}"
        # full/ctx 词干对称: 每个 _full 列必有同词干 _ctx 孪生
        for c in loo_cols:
            if c.endswith('_full'):
                twin = c[:-5] + '_ctx'
                assert twin in loo_cols, f"双轨词干不对称: {c} 缺 {twin}"

    def test_loo_value_correctness_after_rename(self):
        """改名只动列名不动公式: LOO = 组内其余银行均值."""
        out = _geo.compute_leave_one_out_sentiment(_loo_panel())
        row = out[(out['target_bank'] == 'A银行') & (out['year'] == 2017)]
        # dict_avg_tone_full 组值 [0.2, 0.4, 0.6] → A 的 LOO = (0.4+0.6)/2
        assert row['prov_leave1out_dict_tone_full'].iloc[0] == pytest.approx(0.5)
        assert row['city_leave1out_dict_tone_full'].iloc[0] == pytest.approx(0.5)

    def test_sanitize_is_noop_for_new_names(self):
        """新列名 ≤32 → sanitize_stata_columns 不再单侧缩写, full/ctx 进 .dta 同词干."""
        from news_process.papers._common.tables import sanitize_stata_columns
        sanitized = sanitize_stata_columns(pd.Index(self.NEW_COLS), max_len=32)
        assert list(sanitized) == self.NEW_COLS

    def test_recommended_stata_command_uses_existing_column(self):
        """geography 日志推荐的 overid 命令不得引用 .dta 中不存在的旧列名 (r(111))."""
        src = Path(_geo.__file__).read_text(encoding='utf-8')
        assert '"prov_leave1out_dict_tone_full "' in src
        assert '"prov_leave1out_dict_avg_tone_full "' not in src

    def test_new_loo_columns_have_stata_labels(self, stata_labels):
        for c in self.NEW_COLS:
            assert c in stata_labels, f"新 LOO 列 {c} 缺 Stata 标签"


# ============================================================================
# fix-05: low_conf_flag 物化移出诊断函数
# ============================================================================

class TestLowConfFlagMaterialization:
    def _diag_panel(self) -> pd.DataFrame:
        return pd.DataFrame({
            'target_bank': ['A银行', 'A银行', 'B银行', 'B银行'],
            'year': [2017, 2018, 2017, 2018],
            'n_articles': [3, 0, 1, 2],
            'avg_category_confidence': [0.9, 0.3, np.nan, 0.7],
            'llm_vote_tone_full': [0.1, np.nan, 0.2, -0.1],
        })

    def test_log_diagnostics_is_read_only(self):
        """诊断函数不得变异 panel (原副作用式创建 low_conf_flag 已移除)."""
        panel = self._diag_panel()
        cols_before = list(panel.columns)
        df_exploded = pd.DataFrame({'is_multi_bank': [False, True, False]})
        _exp.log_diagnostics(panel, df_exploded)
        assert list(panel.columns) == cols_before
        assert 'low_conf_flag' not in panel.columns

    def test_materialize_with_mixed_confidence(self):
        p = pd.DataFrame({'avg_category_confidence': [0.9, 0.3, np.nan]})
        out = _exp._materialize_low_conf_flag(p)
        # 与原 G-20 语义逐位一致: conf<0.5 → 1; NaN<0.5 == False → 0
        assert out['low_conf_flag'].tolist() == [0, 1, 0]

    def test_materialize_all_nan_creates_stable_schema(self):
        """关键修复点: 全 NaN (盘上试跑样本即如此) 也必须创建列 → schema 不随数据漂移."""
        p = pd.DataFrame({'avg_category_confidence': [np.nan, np.nan]})
        out = _exp._materialize_low_conf_flag(p)
        assert 'low_conf_flag' in out.columns
        assert out['low_conf_flag'].tolist() == [0, 0]

    def test_materialize_skips_when_upstream_column_absent(self):
        """列存在性只跟随上游代码路径: 无 avg_category_confidence 则不伪造 flag."""
        p = pd.DataFrame({'x': [1, 2]})
        out = _exp._materialize_low_conf_flag(p)
        assert 'low_conf_flag' not in out.columns

    def test_low_conf_flag_label_retained(self, stata_labels):
        """物化后 low_conf_flag 是真实列, 其标签键必须保留 (不再是幻影)."""
        assert 'low_conf_flag' in stata_labels


# ============================================================================
# fix-06: 变量标签覆盖率兜底
# ============================================================================

class TestLabelFallback:
    def test_full_coverage_and_constraints(self):
        base = {'known_col': 'Known Label'}
        cols = pd.Index(['known_col', 'llm_vote_tone_full', 'target_bank',
                         'zz_unknown_col_123'])
        out = _exp._apply_label_fallback(base, cols)
        for c in cols:
            lab = out[c]
            assert lab, f"{c} 标签为空 (覆盖率兜底失效)"
            assert len(lab) <= 80, f"{c} 标签超 80 字符: {lab!r}"
            lab.encode('latin-1')  # to_stata 硬约束, 不可编码会 raise

    def test_explicit_labels_take_priority(self):
        out = _exp._apply_label_fallback(
            {'llm_vote_tone_full': 'Explicit Wins'},
            pd.Index(['llm_vote_tone_full']))
        assert out['llm_vote_tone_full'] == 'Explicit Wins'

    def test_unknown_column_falls_back_to_its_own_name(self):
        out = _exp._apply_label_fallback({}, pd.Index(['zz_unknown_col_123']))
        assert out['zz_unknown_col_123'] == 'zz_unknown_col_123'

    def test_main_regression_dv_gets_semantic_label_when_codebook_available(self):
        """主回归 DV llm_vote_tone_full 必须获得语义标签 (codebook/启发式)."""
        try:
            from news_process.pipeline.panel.codebook import (
                get_variable_metadata_dict,
            )
            meta = get_variable_metadata_dict()
        except Exception:
            meta = {}
        if 'llm_vote_tone_full' not in meta:
            pytest.skip("codebook 元数据不可用, 语义标签断言跳过 (覆盖率仍由其他用例锁定)")
        out = _exp._apply_label_fallback({}, pd.Index(['llm_vote_tone_full']))
        assert out['llm_vote_tone_full'] == meta['llm_vote_tone_full'].label

    def test_input_dict_not_mutated(self):
        base = {'a': 'A'}
        _exp._apply_label_fallback(base, pd.Index(['a', 'b']))
        assert base == {'a': 'A'}


# ============================================================================
# fix-07: t2v 标签同步 — v3.14.0 (2026-06-27, all-API-embedding) 整体删除
# ----------------------------------------------------------------------------
# 原 TestT2vLabelSync 锁定 export.py::STATA_LABELS (40-path) 与 stata_export.py
# (46-path) 的 _t2v 嵌入标签逐字同步。v3.14.0 彻底移除本地 text2vec(_t2v) 轨:
#   · export.py::STATA_LABELS 中 *所有* 嵌入 anchor 标签 (_t2v/_lg) 均已删除
#     (实测 0 个 _t2v 键 / 0 个 _lg 键) → 嵌入标签的单一事实源收敛到 stata_export.py
#     ::HEURISTIC_LABELS, 不再有 40-path/46-path 双写需要同步的 _t2v 标签。
#   · co-primary _lg (text-embedding-3-large) 标签由 stata_export.py 机械派生,
#     其派生正确性由 tests/test_omni_fix_policy.py::
#     test_allv_labels_mechanically_derived_in_both_label_dicts 等覆盖。
# 故本整组测试 (test_drifted_pairs / test_ctx_twin_present_in_40_path /
# test_verbatim_sync_with_stata_export_source) 测的功能已不存在, 整组删除。
# ============================================================================


# ============================================================================
# fix-08: ai_reg_* 构念勘误
# ============================================================================

class TestAiRegRelabel:
    AI_REG_KEYS = ['ai_reg_province', 'ai_reg_city', 'ai_reg_50km',
                   'ai_reg_100km', 'ai_reg_150km', 'ai_reg_200km']

    def test_labels_describe_peer_coverage_not_ai_imitation(self, stata_labels):
        for k in self.AI_REG_KEYS:
            assert k in stata_labels
            assert stata_labels[k].startswith('Peer FinTech Coverage Penetration'), \
                f"{k} 标签未如实改述: {stata_labels[k]!r}"
        offenders = [k for k, v in stata_labels.items() if 'AI Imitation' in v]
        assert not offenders, f"'AI Imitation' 误称回潮: {offenders}"

    def test_construct_is_loo_mean_of_any_fintech_coverage(self, monkeypatch):
        """锁定披露口径: ai_reg_X = LOO mean I(n_articles>0), 无 AI 子类过滤."""
        panel = pd.DataFrame({
            'target_bank': ['A银行', 'B银行', 'C银行'],
            'year': [2017] * 3,
            'bank_province': ['广东省'] * 3,
            'bank_city': ['深圳市'] * 3,
            'n_articles': [5, 0, 2],
        })
        # 跳过距离级 LOO (坐标/地址路径置空 → 优雅早退, 省/市级已算完)
        monkeypatch.setitem(_geo.CONFIG['paths'], 'city_coordinates_file', '')
        monkeypatch.setitem(_geo.CONFIG['paths'], 'bank_addresses_file', '')
        out = _geo.compute_regional_imitation_pressure(panel)
        # has = [1, 0, 1] → LOO: A=(0+1)/2, B=(1+1)/2, C=(1+0)/2
        assert out['ai_reg_province'].tolist() == pytest.approx([0.5, 1.0, 0.5])
        assert out['ai_reg_city'].tolist() == pytest.approx([0.5, 1.0, 0.5])
        assert '_has_fintech' not in out.columns


# ============================================================================
# 标签卫生横切不变量 (to_stata 硬约束)
# ============================================================================

class TestLabelHygiene:
    def test_all_labels_within_80_chars_and_latin1(self, stata_labels):
        too_long = [k for k, v in stata_labels.items() if len(v) > 80]
        assert not too_long, f"标签超 80 字符 (to_stata 拒绝): {too_long}"
        non_latin = []
        for k, v in stata_labels.items():
            try:
                v.encode('latin-1')
            except UnicodeEncodeError:
                non_latin.append(k)
        assert not non_latin, f"标签含非 latin-1 字符 (to_stata 拒绝): {non_latin}"

    def test_label_count_sane(self, stata_labels):
        # 幻影清除后仍应保有大体量学术标签 (708 键 @ 2026-06-11; 容忍漂移)
        assert len(stata_labels) > 600
