"""
test_entity_masking.py — Entity Masking 稳健性测试的单元测试（双轨版）

覆盖范围：
  - 银行名替换算法（长别名优先、共提银行、标题替换等）
  - 实体残留检测
  - 双轨 Baseline 提取逻辑
  - 双轨一致性指标计算
  - 双轨掩码列命名一致性
"""

import os
import sys

import pandas as pd
import pytest

# 确保项目根目录在 path 中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# ============================================================================
# 复制被测纯函数（避免 import 66_entity_masking_test 触发 LLM 模块加载）
#
# 注 fix(omni g-val-mask, 2026-06-11): 下列本地副本保留修复前语义, 仅锁通用算法
# 骨架 (长别名优先/占位符分配等)。生产模块 validation/entity_masking.py 的修复后
# 行为 (ctx 轨剥标题/残留扫描含标题/共提计数含标题/聚合分母 ITT vs per-protocol
# 双口径) 由 tests/test_omni_fix_val_mask.py 直接 import 真模块锁定。
# ============================================================================

PLACEHOLDER = "目标银行A"
PEER_TEMPLATE = "同业银行{}"
TRACKS = ['full', 'ctx']


def mask_entity(text, title, target_bank, target_aliases, co_mentioned_banks, bank_names_file):
    """被测函数：银行名替换"""
    masked_text, masked_title = text, title
    n_replacements = 0

    for alias in sorted(target_aliases, key=len, reverse=True):
        cnt = masked_text.count(alias) + masked_title.count(alias)
        masked_text = masked_text.replace(alias, PLACEHOLDER)
        masked_title = masked_title.replace(alias, PLACEHOLDER)
        n_replacements += cnt

    masked_peers = []
    if co_mentioned_banks and str(co_mentioned_banks).strip():
        for i, peer in enumerate(
            b.strip() for b in str(co_mentioned_banks).split(';') if b.strip()
        ):
            peer_ph = PEER_TEMPLATE.format(chr(66 + i))
            # 简化：测试中直接用 peer 本身作为唯一别名
            peer_aliases = [peer]
            for alias in sorted(peer_aliases, key=len, reverse=True):
                cnt = masked_text.count(alias)
                masked_text = masked_text.replace(alias, peer_ph)
                masked_title = masked_title.replace(alias, peer_ph)
                n_replacements += cnt
            masked_peers.append(peer_ph)

    return {
        'masked_text': masked_text,
        'masked_title': masked_title,
        'masked_target': PLACEHOLDER,
        'masked_co_mentioned': ';'.join(masked_peers) if masked_peers else '无',
        'n_replacements': n_replacements,
    }


def verify_masking_completeness(masked_text, original_aliases, co_bank_aliases):
    """被测函数：残留检测"""
    residuals = [a for a in original_aliases + co_bank_aliases if a in masked_text]
    return {'complete': len(residuals) == 0, 'residual_aliases': residuals}


def extract_baseline(df_sample, models):
    """被测函数：双轨 baseline 提取"""
    df = df_sample.copy()
    for track in TRACKS:
        suffix = f'_{track}'
        df[f'baseline_verified_{track}'] = df[f'llm_verified{suffix}']
        df[f'baseline_sentiment_{track}'] = df[f'llm_sentiment{suffix}']
        for m in models:
            short = m['short_name']
            df[f'{short}_baseline_verified_{track}'] = df[f'{short}_verified{suffix}']
            df[f'{short}_baseline_sentiment_{track}'] = df[f'{short}_sentiment{suffix}']
    return df


def compute_masking_consistency_local(df_result, track, models):
    """被测函数：单轨道一致性指标（本地简化版，不依赖外部 Cohen's κ）"""
    b_ver = f'baseline_verified_{track}'
    m_ver = f'masked_verified_{track}'
    b_sen = f'baseline_sentiment_{track}'
    m_sen = f'masked_sentiment_{track}'

    ver_match = (df_result[b_ver] == df_result[m_ver]).mean()

    both_true = df_result[b_ver] & df_result[m_ver]
    n_both_true = int(both_true.sum())
    sen_match = (
        (df_result.loc[both_true, b_sen] == df_result.loc[both_true, m_sen]).mean()
        if n_both_true > 0 else float('nan')
    )

    per_model = {}
    for m in models:
        short = m['short_name']
        b_col = f'{short}_baseline_verified_{track}'
        m_col = f'{short}_masked_verified_{track}'
        if b_col in df_result.columns and m_col in df_result.columns:
            valid = df_result[b_col].notna() & df_result[m_col].notna()
            if valid.sum() > 0:
                per_model[short] = round(
                    (df_result.loc[valid, b_col] == df_result.loc[valid, m_col]).mean(), 4
                )

    return {
        'track': track,
        'verification_consistency': round(ver_match, 4),
        'sentiment_consistency': round(sen_match, 4) if not pd.isna(sen_match) else None,
        'per_model_consistency': per_model,
        'n_samples': len(df_result),
        'n_both_true': n_both_true,
        'n_zero_replacements': int((df_result[f'n_replacements_{track}'] == 0).sum()),
    }


# ============================================================================
# 测试 Fixtures
# ============================================================================

MOCK_MODELS = [
    {'short_name': 'modelA', 'model_name': 'model-a'},
    {'short_name': 'modelB', 'model_name': 'model-b'},
    {'short_name': 'modelC', 'model_name': 'model-c'},
]


@pytest.fixture
def sample_dual_track_df():
    """创建一个包含 full + ctx 双轨列的模拟 DataFrame。"""
    n = 10
    data = {
        '内容': ['工商银行推出AI金融产品，提升业务效率。'] * n,
        'content_ctx': ['工商银行推出AI金融产品。'] * n,
        '标题': ['工商银行创新'] * n,
        'target_bank': ['工商银行'] * n,
        'co_mentioned_banks': [''] * n,
        # full 轨道原始判定
        'llm_verified_full': [True] * 8 + [False] * 2,
        'llm_sentiment_full': ['正面'] * 5 + ['中性'] * 3 + ['中性'] * 2,
        # ctx 轨道原始判定
        'llm_verified_ctx': [True] * 7 + [False] * 3,
        'llm_sentiment_ctx': ['正面'] * 4 + ['中性'] * 3 + ['中性'] * 3,
    }
    # 逐模型列
    for m in MOCK_MODELS:
        short = m['short_name']
        data[f'{short}_verified_full'] = data['llm_verified_full']
        data[f'{short}_sentiment_full'] = data['llm_sentiment_full']
        data[f'{short}_verified_ctx'] = data['llm_verified_ctx']
        data[f'{short}_sentiment_ctx'] = data['llm_sentiment_ctx']

    return pd.DataFrame(data)


# ============================================================================
# 测试用例：银行名替换算法
# ============================================================================

class TestMaskEntity:
    """银行名替换算法测试"""

    def test_mask_long_alias_first(self):
        """长别名优先替换，短别名不残留"""
        result = mask_entity(
            "中国工商银行和工商银行联合推出", "",
            "中国工商银行", ["中国工商银行", "工商银行"], "", ""
        )
        assert "工商银行" not in result['masked_text']
        assert "目标银行A" in result['masked_text']
        assert result['n_replacements'] == 2

    def test_mask_co_mentioned_banks(self):
        """共提银行使用不同占位符"""
        result = mask_entity(
            "工商银行与建设银行合作", "", "工商银行",
            ["工商银行"], "建设银行", ""
        )
        assert "同业银行B" in result['masked_text']
        assert "目标银行A" in result['masked_text']

    def test_mask_empty_co_banks(self):
        """无共提银行时不报错"""
        result = mask_entity("工商银行", "", "工商银行", ["工商银行"], "", "")
        assert result['masked_co_mentioned'] == '无'

    def test_mask_title_also_replaced(self):
        """标题中的银行名也应被替换"""
        result = mask_entity(
            "工商银行发布了新产品", "工商银行新闻",
            "工商银行", ["工商银行"], "", ""
        )
        assert "工商银行" not in result['masked_title']
        assert "目标银行A" in result['masked_title']
        assert result['n_replacements'] == 2  # 正文1次 + 标题1次

    def test_zero_replacements_flagged(self):
        """文中无银行名时替换次数为零"""
        result = mask_entity("今天天气很好", "", "工商银行", ["工商银行"], "", "")
        assert result['n_replacements'] == 0

    def test_multiple_co_banks(self):
        """多个共提银行各用不同占位符"""
        result = mask_entity(
            "工商银行联合建设银行和农业银行", "", "工商银行",
            ["工商银行"], "建设银行;农业银行", ""
        )
        assert "同业银行B" in result['masked_text']
        assert "同业银行C" in result['masked_text']
        assert "目标银行A" in result['masked_text']


# ============================================================================
# 测试用例：实体残留检测
# ============================================================================

class TestMaskingCompleteness:
    """实体残留检测测试"""

    def test_detects_residual(self):
        """残留检测正确识别不完整替换"""
        result = verify_masking_completeness(
            "目标银行A发布了工商银行的产品", ["工商银行"], []
        )
        assert result['complete'] is False
        assert "工商银行" in result['residual_aliases']

    def test_passes_clean_text(self):
        """完全替换后通过残留检测"""
        result = verify_masking_completeness(
            "目标银行A发布了新产品", ["工商银行"], []
        )
        assert result['complete'] is True
        assert result['residual_aliases'] == []

    def test_detects_co_bank_residual(self):
        """检测共提银行残留"""
        result = verify_masking_completeness(
            "目标银行A和建设银行合作", ["工商银行"], ["建设银行"]
        )
        assert result['complete'] is False
        assert "建设银行" in result['residual_aliases']


# ============================================================================
# 测试用例：双轨 Baseline 提取
# ============================================================================

class TestDualTrackBaseline:
    """双轨 Baseline 提取测试"""

    def test_baseline_columns_created(self, sample_dual_track_df):
        """双轨 baseline 列正确创建"""
        result = extract_baseline(sample_dual_track_df, MOCK_MODELS)

        for track in TRACKS:
            assert f'baseline_verified_{track}' in result.columns
            assert f'baseline_sentiment_{track}' in result.columns

            for m in MOCK_MODELS:
                short = m['short_name']
                assert f'{short}_baseline_verified_{track}' in result.columns
                assert f'{short}_baseline_sentiment_{track}' in result.columns

    def test_baseline_values_match_original(self, sample_dual_track_df):
        """baseline 值与原始列完全一致"""
        result = extract_baseline(sample_dual_track_df, MOCK_MODELS)

        pd.testing.assert_series_equal(
            result['baseline_verified_full'],
            sample_dual_track_df['llm_verified_full'],
            check_names=False,
        )
        pd.testing.assert_series_equal(
            result['baseline_verified_ctx'],
            sample_dual_track_df['llm_verified_ctx'],
            check_names=False,
        )

    def test_full_and_ctx_tracks_independent(self, sample_dual_track_df):
        """full 和 ctx 的 baseline 值互相独立"""
        result = extract_baseline(sample_dual_track_df, MOCK_MODELS)

        # full 有 8 个 True，ctx 有 7 个 True
        assert result['baseline_verified_full'].sum() == 8
        assert result['baseline_verified_ctx'].sum() == 7


# ============================================================================
# 测试用例：双轨一致性指标
# ============================================================================

class TestDualTrackConsistency:
    """双轨一致性指标计算测试"""

    def _make_consistency_df(self, track, agreement_rate=1.0):
        """构建带双轨列的测试 DataFrame。"""
        n = 20
        n_agree = int(n * agreement_rate)
        baseline = [True] * 15 + [False] * 5
        if agreement_rate == 1.0:
            masked = baseline.copy()
        else:
            masked = baseline[:n_agree] + [not x for x in baseline[n_agree:]]

        data = {
            f'baseline_verified_{track}': baseline,
            f'masked_verified_{track}': masked,
            f'baseline_sentiment_{track}': ['正面' if v else '中性' for v in baseline],
            f'masked_sentiment_{track}': ['正面' if v else '中性' for v in masked],
            f'n_replacements_{track}': [3] * n,
        }
        for m in MOCK_MODELS:
            short = m['short_name']
            data[f'{short}_baseline_verified_{track}'] = baseline
            data[f'{short}_masked_verified_{track}'] = masked
        return pd.DataFrame(data)

    def test_perfect_consistency(self):
        """完全一致时验证一致率为 1.0"""
        for track in TRACKS:
            df = self._make_consistency_df(track, agreement_rate=1.0)
            result = compute_masking_consistency_local(df, track, MOCK_MODELS)

            assert result['track'] == track
            assert result['verification_consistency'] == 1.0
            assert result['n_samples'] == 20

    def test_partial_consistency(self):
        """部分一致时一致率正确计算"""
        for track in TRACKS:
            df = self._make_consistency_df(track, agreement_rate=0.8)
            result = compute_masking_consistency_local(df, track, MOCK_MODELS)

            assert 0.7 <= result['verification_consistency'] <= 0.9

    def test_per_model_breakdown(self):
        """逐模型分解在双轨下独立计算"""
        for track in TRACKS:
            df = self._make_consistency_df(track, agreement_rate=1.0)
            result = compute_masking_consistency_local(df, track, MOCK_MODELS)

            for m in MOCK_MODELS:
                assert m['short_name'] in result['per_model_consistency']
                assert result['per_model_consistency'][m['short_name']] == 1.0

    def test_zero_replacements_counted(self):
        """零替换条数正确统计"""
        track = 'full'
        df = self._make_consistency_df(track)
        # 将前 3 条设为零替换
        df.loc[0:2, f'n_replacements_{track}'] = 0
        result = compute_masking_consistency_local(df, track, MOCK_MODELS)
        assert result['n_zero_replacements'] == 3

    def test_sentiment_consistency_conditional(self):
        """情感一致率仅在双方均为 True 的子集上计算"""
        track = 'ctx'
        n = 10
        data = {
            f'baseline_verified_{track}': [True, True, True, False, False] * 2,
            f'masked_verified_{track}':   [True, True, False, True, False] * 2,
            f'baseline_sentiment_{track}': ['正面', '负面', '中性', '中性', '中性'] * 2,
            f'masked_sentiment_{track}':   ['正面', '正面', '中性', '中性', '中性'] * 2,
            f'n_replacements_{track}': [2] * n,
        }
        for m in MOCK_MODELS:
            short = m['short_name']
            data[f'{short}_baseline_verified_{track}'] = data[f'baseline_verified_{track}']
            data[f'{short}_masked_verified_{track}'] = data[f'masked_verified_{track}']
        df = pd.DataFrame(data)
        result = compute_masking_consistency_local(df, track, MOCK_MODELS)

        # both_true 子集 = baseline=True AND masked=True → 行 0,1 (×2=4条)
        # 行0: 正面==正面(一致), 行1: 负面!=正面(不一致) → 50%
        assert result['n_both_true'] == 4
        assert result['sentiment_consistency'] == 0.5


# ============================================================================
# 测试用例：双轨掩码列命名一致性
# ============================================================================

class TestDualTrackColumnNaming:
    """双轨列命名约定一致性测试"""

    def test_masked_text_columns_follow_convention(self):
        """掩码结果列名遵循 *_{track} 后缀约定"""
        expected_columns_per_track = [
            'masked_text_{track}',
            'n_replacements_{track}',
            'baseline_verified_{track}',
            'baseline_sentiment_{track}',
            'masked_verified_{track}',
            'masked_sentiment_{track}',
        ]
        for track in TRACKS:
            for template in expected_columns_per_track:
                col_name = template.format(track=track)
                # 验证命名格式合理（不含双下划线等异常）
                assert '__' not in col_name
                assert col_name.endswith(f'_{track}')

    def test_shared_columns_no_track_suffix(self):
        """共享列（masked_title, masked_target, masked_co_mentioned）无轨道后缀"""
        shared_cols = ['masked_title', 'masked_target', 'masked_co_mentioned']
        for col in shared_cols:
            assert not col.endswith('_full')
            assert not col.endswith('_ctx')

    def test_full_ctx_same_mask_on_same_text(self):
        """同一条新闻的 full 和 ctx 文本掩码独立执行"""
        text_full = "工商银行推出AI金融产品，提升业务效率。建设银行也参与。"
        text_ctx = "工商银行推出AI金融产品。"

        result_full = mask_entity(
            text_full, "标题", "工商银行", ["工商银行"], "建设银行", ""
        )
        result_ctx = mask_entity(
            text_ctx, "标题", "工商银行", ["工商银行"], "建设银行", ""
        )

        # full 文本包含共提银行，ctx 不包含
        assert "同业银行B" in result_full['masked_text']
        assert "同业银行B" not in result_ctx['masked_text']

        # 但目标银行在两者中都被替换
        assert "目标银行A" in result_full['masked_text']
        assert "目标银行A" in result_ctx['masked_text']

        # 替换次数不同
        assert result_full['n_replacements'] >= result_ctx['n_replacements']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
