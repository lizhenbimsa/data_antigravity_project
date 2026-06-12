"""test_omni_fix_val_mask.py — fix(omni g-val-mask, 2026-06-11) 回归锁。

锁定 validation/entity_masking.py 的三组修复行为:
  - g-val-mask-01: ctx 轨掩码前剥离 stage13 prepend 的标题前缀
    (与生产 tone_llms.iter_article_track_prompts 的 prompt 构造对齐,
    防掩码 prompt 标题双重注入污染一致性指标)。
  - g-val-mask-02 / g-val-mask-04: 聚合一致性分母双口径 —
    主口径 per-protocol (剔除 LLM 调用全失败行, 空票判 False 属测量缺失)
    + ITT (physical 分母) 披露口径, n_call_failure 显式报告。
  - g-val-mask-03: 残留扫描扩展到标题 + 共提银行替换计数计入标题命中。

全部用合成 DataFrame, 不依赖盘上数据, 不触网 (无 LLM 调用)。

# 白话: 实体掩码检验是把新闻里的银行名遮住再让模型判情感, 看结论变不变。
# 这组测试锁三件事: 1) 遮名前先把拼进正文开头的标题摘掉, 别让标题被遮两次;
# 2) 算一致率时分两套分母 — 剔除调用失败的"按实际服药"口径和不剔的"按分组
# 意向"口径, 失败篇数要明说; 3) 检查有没有漏遮时, 标题里的银行名也要查。
"""

import inspect

import pandas as pd
import pytest

from news_process.core.text.entity_context import prepend_title
from news_process.validation import entity_masking as em

# ============================================================================
# g-val-mask-01: ctx 轨掩码输入与生产 prompt 构造对齐
# ============================================================================

class TestCtxStripAlignment:
    """ctx 轨掩码前剥离 prepend 标题前缀, 复用生产同一实现。"""

    def test_reuses_production_strip_impl(self):
        """模块内 _strip_prepended_title 必须是 tone_llms 生产实现的同一对象 (只读复用)。"""
        assert em._strip_prepended_title is em._tone_llms._strip_prepended_title

    def test_strips_prepended_title_with_separator(self):
        """标题无句末标点 → prepend 用'。'分隔 → 剥离后恢复纯实体窗口。"""
        assert em.build_ctx_masking_input("工商银行创新。工商银行推出AI产品", "工商银行创新") \
            == "工商银行推出AI产品"

    def test_strips_prepended_title_with_end_punct(self):
        """标题末尾已带句末标点 → prepend 直连 → 同样可剥离。"""
        assert em.build_ctx_masking_input("重磅！银行窗口内容", "重磅！") == "银行窗口内容"

    def test_no_title_prefix_unchanged(self):
        """ctx 不以标题开头 (如旧格式数据) → 原样返回, 不误删。"""
        assert em.build_ctx_masking_input("银行窗口内容", "完全无关的标题") == "银行窗口内容"

    def test_empty_title_unchanged(self):
        assert em.build_ctx_masking_input("银行窗口内容", "") == "银行窗口内容"
        assert em.build_ctx_masking_input("银行窗口内容", None) == "银行窗口内容"

    @pytest.mark.parametrize("title,body", [
        ("工商银行创新", "工商银行推出AI产品。"),
        ("银行年报发布！", "净利润同比增长。"),
        ("标题以分号结尾；", "窗口正文。"),
        ("", "纯正文无标题。"),
    ])
    def test_roundtrip_matches_production_strip(self, title, body):
        """prepend → strip 往返与生产 _strip_prepended_title 语义逐字节一致。"""
        ctx_on_disk = prepend_title(title, body)
        assert em.build_ctx_masking_input(ctx_on_disk, title) \
            == em._tone_llms._strip_prepended_title(ctx_on_disk, title)

    def test_main_wires_ctx_strip_before_masking(self):
        """接线锁: main() 的 ctx 轨掩码必须经 build_ctx_masking_input 剥标题。"""
        src = inspect.getsource(em.main)
        assert 'build_ctx_masking_input(' in src, \
            "main() ctx 轨掩码未剥离 prepend 标题 — 回归 g-val-mask-01"


# ============================================================================
# g-val-mask-03: 残留扫描扩展到标题 + 共提银行计数计入标题
# ============================================================================

class TestResidualScanTitle:
    """漏遮审计须覆盖标题 (掩码标题同样注入 LLM prompt 的 {title} 字段)。"""

    def test_residual_in_title_detected(self):
        result = em.verify_masking_completeness(
            "目标银行A发布了新产品", ["工商银行"], [],
            masked_title="工商银行新闻",
        )
        assert result['complete'] is False
        assert "工商银行" in result['residual_aliases']

    def test_co_bank_residual_in_title_detected(self):
        result = em.verify_masking_completeness(
            "目标银行A发布了新产品", ["工商银行"], ["建设银行"],
            masked_title="建设银行参与合作",
        )
        assert result['complete'] is False
        assert "建设银行" in result['residual_aliases']

    def test_clean_body_and_title_pass(self):
        result = em.verify_masking_completeness(
            "目标银行A发布了新产品", ["工商银行"], ["建设银行"],
            masked_title="目标银行A与同业银行B合作",
        )
        assert result['complete'] is True
        assert result['residual_aliases'] == []

    def test_body_residual_still_detected(self):
        """既有行为不回归: 正文残留照常检出。"""
        result = em.verify_masking_completeness(
            "目标银行A发布了工商银行的产品", ["工商银行"], [],
            masked_title="干净标题",
        )
        assert result['complete'] is False

    def test_default_no_title_backward_compatible(self):
        """不传 masked_title (默认 '') → 等价旧的正文-only 行为。"""
        result = em.verify_masking_completeness("目标银行A发布了新产品", ["工商银行"], [])
        assert result['complete'] is True


class TestPeerTitleReplacementCount:
    """共提银行替换计数与目标银行口径对齐: 标题命中计入 n_replacements。"""

    @pytest.fixture(autouse=True)
    def _stub_aliases(self, monkeypatch):
        # 防 get_target_aliases 用空 bank_names_file 污染模块级全局缓存
        monkeypatch.setattr(em, 'get_target_aliases', lambda bank, f: [bank])

    def test_peer_hit_only_in_title_counted(self):
        result = em.mask_entity(
            "正文不含同业银行名", "建设银行参与合作",
            "工商银行", ["工商银行"], "建设银行", "",
        )
        # 目标 0 次 + 共提标题 1 次
        assert result['n_replacements'] == 1
        assert "同业银行B" in result['masked_title']
        assert "建设银行" not in result['masked_title']

    def test_peer_hits_in_body_and_title_both_counted(self):
        result = em.mask_entity(
            "建设银行发布公告", "建设银行新闻",
            "工商银行", ["工商银行"], "建设银行", "",
        )
        assert result['n_replacements'] == 2

    def test_target_count_unchanged(self):
        """既有行为不回归: 目标银行正文+标题各 1 次 → n=2。"""
        result = em.mask_entity(
            "工商银行发布了新产品", "工商银行新闻",
            "工商银行", ["工商银行"], "", "",
        )
        assert result['n_replacements'] == 2


# ============================================================================
# g-val-mask-02 / g-val-mask-04: 聚合分母双口径 (ITT vs per-protocol)
# ============================================================================

def _make_consistency_df(track='full'):
    """10 行合成轨道数据: 8 行有效 (全一致), 2 行掩码重判调用全失败。

    失败行 (idx 8,9): masked_call_failure=1, masked_verified 被空票判 False,
    而 baseline_verified=True → ITT 口径计为翻转, per-protocol 口径剔除。
    """
    baseline_v = [True] * 6 + [False] * 2 + [True] * 2
    masked_v = [True] * 6 + [False] * 2 + [False] * 2   # 失败行空票 → False
    call_fail = [0] * 8 + [1, 1]
    baseline_s = ['正面'] * 5 + ['正面'] + ['中性'] * 2 + ['正面'] * 2
    masked_s = ['正面'] * 5 + ['中性'] + ['中性'] * 2 + [None] * 2
    return pd.DataFrame({
        f'baseline_verified_{track}': baseline_v,
        f'masked_verified_{track}': masked_v,
        f'baseline_sentiment_{track}': baseline_s,
        f'masked_sentiment_{track}': masked_s,
        f'masked_call_failure_{track}': call_fail,
        f'n_replacements_{track}': [3] * 10,
    })


class TestDualDenominator:
    """主口径 per-protocol + ITT 披露口径, 两个数并行报告。"""

    def test_per_protocol_excludes_call_failures(self):
        df = _make_consistency_df('full')
        result = em.compute_masking_consistency(df, 'full')
        # per-protocol: 8 有效行全一致
        assert result['verification_consistency'] == 1.0
        # ITT: 10 行中 2 失败行计为翻转 → 8/10
        assert result['verification_consistency_itt'] == 0.8

    def test_call_failure_accounting_reported(self):
        df = _make_consistency_df('full')
        result = em.compute_masking_consistency(df, 'full')
        assert result['n_call_failure'] == 2
        assert result['n_samples'] == 10           # ITT physical 分母
        assert result['n_samples_valid'] == 8      # per-protocol valid 分母
        assert 'per-protocol' in result['denominator_note']

    def test_kappa_dual_denominators(self):
        df = _make_consistency_df('full')
        result = em.compute_masking_consistency(df, 'full')
        # per-protocol: 8 行全一致 (6 True / 2 False 双边) → κ = 1.0
        assert result['cohens_kappa']['kappa'] == 1.0
        assert result['cohens_kappa']['n_samples'] == 8
        # ITT: p_o=0.8, p_e=(8*6+2*4)/100=0.56 → κ=(0.8-0.56)/0.44≈0.5455
        assert result['cohens_kappa_itt']['kappa'] == pytest.approx(0.5455, abs=1e-3)
        assert result['cohens_kappa_itt']['n_samples'] == 10

    def test_sentiment_subset_on_valid_rows(self):
        df = _make_consistency_df('full')
        result = em.compute_masking_consistency(df, 'full')
        # both_true (valid 行) = idx 0..5; idx5 情感翻转 → 5/6
        assert result['n_both_true'] == 6
        assert result['sentiment_consistency'] == pytest.approx(round(5 / 6, 4))

    def test_baseline_call_failure_also_excluded(self):
        """baseline 侧 llm_call_failure 行同样剔除 (suggested_fix '及 baseline 对应失败行')。"""
        track = 'ctx'
        df = pd.DataFrame({
            f'baseline_verified_{track}': [False, True, True, True],
            f'masked_verified_{track}': [True, True, True, True],
            f'baseline_sentiment_{track}': [None, '正面', '正面', '正面'],
            f'masked_sentiment_{track}': ['正面'] * 4,
            f'masked_call_failure_{track}': [0, 0, 0, 0],
            f'llm_call_failure_{track}': [1, 0, 0, 0],   # idx0: baseline 空票 False
            f'n_replacements_{track}': [2] * 4,
        })
        result = em.compute_masking_consistency(df, track)
        assert result['n_call_failure'] == 1
        assert result['verification_consistency'] == 1.0          # 3/3
        assert result['verification_consistency_itt'] == 0.75     # 3/4

    def test_graceful_without_failure_columns(self):
        """旧 detail 数据缺 call_failure 列 → 不过滤, 双口径同值。"""
        track = 'full'
        df = _make_consistency_df(track).drop(columns=[f'masked_call_failure_{track}'])
        result = em.compute_masking_consistency(df, track)
        assert result['n_call_failure'] == 0
        assert result['verification_consistency'] == result['verification_consistency_itt'] == 0.8
        assert result['n_samples_valid'] == result['n_samples'] == 10

    def test_zero_replacements_still_counted(self):
        """既有行为不回归: n_zero_replacements 统计照旧 (在全样本上)。"""
        df = _make_consistency_df('full')
        df.loc[0:2, 'n_replacements_full'] = 0
        result = em.compute_masking_consistency(df, 'full')
        assert result['n_zero_replacements'] == 3


class TestCallFailureMaskHelper:
    """_call_failure_mask: 共用过滤助手 (聚合指标与混淆矩阵同口径)。"""

    def test_union_of_masked_and_baseline_failures(self):
        df = pd.DataFrame({
            'masked_call_failure_full': [1, 0, 0, None],
            'llm_call_failure_full': [0, 1, 0, 0],
        })
        mask = em._call_failure_mask(df, 'full')
        assert mask.tolist() == [True, True, False, False]

    def test_missing_columns_all_false(self):
        df = pd.DataFrame({'whatever': [1, 2, 3]})
        mask = em._call_failure_mask(df, 'ctx')
        assert not mask.any()

    def test_confusion_matrix_uses_same_filter(self):
        """接线锁: 混淆矩阵图与主口径共用 _call_failure_mask。"""
        src = inspect.getsource(em._generate_confusion_matrix_dual)
        assert '_call_failure_mask(' in src


class TestReportDiscloseBothDenominators:
    """报告层双口径披露接线锁 (不实际写盘)。"""

    def test_latex_panel_includes_itt_row(self):
        src = inspect.getsource(em.generate_report)
        assert "'verification_consistency_itt'" in src, \
            "LaTeX Panel A 未披露 ITT 口径 — 回归 g-val-mask-02"

    def test_detail_csv_exports_call_failure_flag(self):
        src = inspect.getsource(em.generate_report)
        assert "masked_call_failure_{track}" in src, \
            "detail CSV 未导出 call_failure 旗标 — 双口径不可复算"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
