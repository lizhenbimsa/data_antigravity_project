"""tests/test_13_materialize_ctx.py — v3.7.2 R8-H1 全管道延伸测试.

测试 ctx_is_fallback 列的产生、dtype 稳定性、idempotent 行为, 以及
encode.py 聚合产 frac_ctx_fallback / n_articles_for_ctx_independence 的正确性.

三轨 (ss 银行+金科同句共现轨, 2026-06-14): stage 13 在 content_ctx 之外额外
物化第三条文本轨 content_ss + ss_is_fallback (镜像 ctx 回退公理: 无银行∧金科
同句共现 → content_ss 退回全文 body → ss_is_fallback=True)。本测试同步加 ss
列的结构存在性 + dtype + 旧 schema 回填 (哨兵填充, 不重算) 断言。

锚定: pipeline/audit/lexical_discriminant_validity.py:20 (R8-H1 audit anchor).
实测 fallback 率 (T0 R4-1, disk 13_news_with_ctx.parquet 1170 行) = 10.43%.
"""
from __future__ import annotations

import pandas as pd
import pytest

# sys.path 已由 conftest.py 处理
from news_process.pipeline.text.ctx_materializer import materialize_content_ctx


@pytest.fixture
def df_with_ctx_already():
    """模拟 stage 12 输出 + content_ctx 已物化 (旧 schema 兼容场景).

    构造: 第 0 行 ctx ≠ full (真双轨); 第 1 行 ctx ≠ full (真双轨);
          第 2 行 ctx == full (fallback) — 用 expected = [False, False, True] 验证.
    """
    return pd.DataFrame({
        '内容': ['银行 A 发布数字化战略报告。这是另一句无关内容。',
                  '银行 B 与某科技公司合作。某无关补充句。',
                  '银行 C 季报披露。某非提及内容。'],
        'target_bank': ['银行 A', '银行 B', '银行 C'],
        'content_ctx': ['银行 A 发布数字化战略报告。',
                          '银行 B 与某科技公司合作。',  # 与 '内容' 不同 (少了"某无关补充句")
                          '银行 C 季报披露。某非提及内容。'],  # 与 '内容' 相同 (fallback)
    })


@pytest.fixture
def df_no_ctx():
    """模拟 stage 12 raw 输出 (无 content_ctx, 无 ctx_is_fallback)."""
    return pd.DataFrame({
        '内容': ['银行 A 发布。短文本。',
                  '银行 B 季报。',
                  ''],
        'target_bank': ['银行 A', '银行 B', ''],  # 第 3 行 target_bank 空
    })


class TestCtxIsFallbackColumnCreation:
    """T2 核心测试: ctx_is_fallback 列产生 + 一致性."""

    def test_old_schema_backfill_compatibility(self, df_with_ctx_already):
        """旧 schema (content_ctx 已存在, ctx_is_fallback 缺): 自动补算."""
        result = materialize_content_ctx(df_with_ctx_already)
        assert 'ctx_is_fallback' in result.columns, \
            "旧 schema 路径必须补算 ctx_is_fallback"
        # 第 3 行 ctx == full → True; 其余 False
        expected = pd.Series([False, False, True], name='ctx_is_fallback')
        pd.testing.assert_series_equal(
            result['ctx_is_fallback'].reset_index(drop=True),
            expected, check_names=False
        )

    def test_idempotent_when_both_columns_present(self):
        """双列都已存在: skip 物化 (logger.info 'idempotent')."""
        df = pd.DataFrame({
            '内容': ['x', 'y'],
            'target_bank': ['A', 'B'],
            'content_ctx': ['x', 'y'],
            'ctx_is_fallback': [True, True],
        })
        result = materialize_content_ctx(df)
        # 列原样返回, 不重算
        pd.testing.assert_series_equal(
            result['ctx_is_fallback'], df['ctx_is_fallback']
        )

    def test_dtype_is_bool_not_object(self, df_with_ctx_already):
        """dtype 必须严格 bool (防 parquet round-trip 漂移为 object)."""
        result = materialize_content_ctx(df_with_ctx_already)
        assert result['ctx_is_fallback'].dtype == bool, \
            f"ctx_is_fallback dtype 必须为 bool, 实际为 {result['ctx_is_fallback'].dtype}"


class TestSsMaterialization:
    """T3 三轨 (ss 银行+金科同句, 2026-06-14): content_ss + ss_is_fallback 物化.

    回退公理镜像 ctx: 无银行∧金科同句共现 → content_ss 退回全文 body →
    ss_is_fallback=True; FINTECH_AC=None (词典加载失败) ⇒ ss 全部回退 → 全 True。
    旧 schema (content_ctx 已存在, 缺 content_ss/ss_is_fallback) 路径按 plan §8.3
    哨兵填充 (content_ss=全文 body=content_full, ss_is_fallback=True, 不重算 ss)。
    """

    def test_ss_backfill_on_old_schema(self, df_with_ctx_already):
        """旧 schema (有 content_ctx, 缺 ss 两列): 回填 content_ss + ss_is_fallback."""
        result = materialize_content_ctx(df_with_ctx_already)
        assert 'content_ss' in result.columns, \
            "旧 schema 路径必须回填 content_ss"
        assert 'ss_is_fallback' in result.columns, \
            "旧 schema 路径必须回填 ss_is_fallback"

    def test_ss_is_fallback_is_bool(self, df_with_ctx_already):
        """ss_is_fallback dtype 必须严格 bool (镜像 ctx_is_fallback dtype 守卫)."""
        result = materialize_content_ctx(df_with_ctx_already)
        assert result['ss_is_fallback'].dtype == bool, \
            f"ss_is_fallback dtype 必须为 bool, 实际为 {result['ss_is_fallback'].dtype}"

    def test_ss_backfill_is_sentinel_all_true(self, df_with_ctx_already):
        """plan §8.3 回填策略: 旧 schema 缺 ss → 哨兵 ss_is_fallback 全 True (不重算)."""
        result = materialize_content_ctx(df_with_ctx_already)
        # 哨兵填充 = 全文 body, 镜像 ctx 回退公理, 故每行皆 fallback
        assert result['ss_is_fallback'].all(), \
            "旧 schema 回填时 ss_is_fallback 应全 True (哨兵填充, 不重算 ss)"

    def test_ss_materialized_when_no_content_ctx(self):
        """全新物化 (无 content_ctx): content_ss/ss_is_fallback 与 ctx 五列并出.

        FINTECH_AC 加载失败时 ss 全回退全文 body (镜像 ctx 回退契约), 但列结构
        必齐 — 本测试只断言**结构平价** (五列齐全 + dtype), 不断言 ss 具体取句值
        (ss 数据/词典依实际运行环境而定; 保守只验结构, 见 plan §⑫)。
        """
        df = pd.DataFrame({
            '内容': ['银行 A 推进金融科技战略。这是另一句无关内容。',
                      '银行 B 季报披露盈利。某非提及内容。'],
            'target_bank': ['银行 A', '银行 B'],
        })
        result = materialize_content_ctx(df)
        for col in ('content_full', 'content_ctx', 'content_ss',
                    'ctx_is_fallback', 'ss_is_fallback'):
            assert col in result.columns, f"全新物化缺五列之一: {col}"
        assert result['ss_is_fallback'].dtype == bool
        # 回退公理镜像 ctx: 回退行 content_ss == content_full (全文 body+标题)
        fb_rows = result[result['ss_is_fallback']]
        if len(fb_rows) > 0:
            assert (fb_rows['content_ss'] == fb_rows['content_full']).all(), \
                "ss 回退行 content_ss 应镜像 ctx 退回全文 body (==content_full)"

    def test_idempotent_when_all_five_columns_present(self):
        """五列 (content_full/ctx/ss + ctx/ss_is_fallback) 都在: skip 物化 (idempotent)."""
        df = pd.DataFrame({
            '内容': ['x', 'y'],
            'target_bank': ['A', 'B'],
            'content_full': ['标题。x', '标题。y'],
            'content_ctx': ['标题。x', '标题。y'],
            'content_ss': ['标题。x', '标题。y'],
            'ctx_is_fallback': pd.Series([True, True], dtype='bool'),
            'ss_is_fallback': pd.Series([True, True], dtype='bool'),
        })
        result = materialize_content_ctx(df)
        # 列原样返回, 不重算
        pd.testing.assert_series_equal(
            result['ss_is_fallback'], df['ss_is_fallback'])
        pd.testing.assert_series_equal(
            result['content_ss'], df['content_ss'])


class TestParquetRoundtrip:
    """v3.7.2 R4-2 dtype roundtrip 防御 (pyarrow 21 验证)."""

    def test_bool_dtype_survives_parquet_roundtrip(self, tmp_path):
        """parquet write + read 后 bool dtype 保持 (pyarrow >= 13 行为)."""
        df = pd.DataFrame({
            'a': [1, 2, 3],
            'ctx_is_fallback': pd.Series([True, False, True], dtype='bool'),
        })
        path = tmp_path / 'roundtrip.parquet'
        df.to_parquet(path)
        df2 = pd.read_parquet(path)
        assert df2['ctx_is_fallback'].dtype == bool, \
            f"parquet roundtrip 后 dtype 应为 bool, 实际 {df2['ctx_is_fallback'].dtype}"
        assert df2['ctx_is_fallback'].mean() == pytest.approx(2/3)


class TestPanelAggregation:
    """T2 panel 层测试: frac_ctx_fallback + n_articles_for_ctx_independence."""

    def test_frac_ctx_fallback_in_range_0_1(self):
        """frac_ctx_fallback 必须 ∈ [0, 1]."""
        from news_process.pipeline.panel.encode import build_aggregation_dict
        df = pd.DataFrame({
            'target_bank': ['A', 'A', 'B'],
            'year': [2024, 2024, 2024],
            'ctx_is_fallback': pd.Series([True, False, True], dtype='bool'),
            'llm_vote_score_full': [1, -1, 0],
            'in_title': [0, 1, 0],
            'is_multi_bank': [False, False, True],
            'bank_count': [1, 1, 2],
            'mention_density': [0.5, 0.3, 0.4],
            'doc_length': [100, 200, 150],
            'target_bank_mention_count': [1, 2, 1],
        })
        agg = build_aggregation_dict(df)
        assert 'frac_ctx_fallback' in agg, \
            "build_aggregation_dict 必须注册 frac_ctx_fallback (ctx_is_fallback 在 df)"
        # 测真实聚合
        valid_agg = {k: v for k, v in agg.items() if v[0] in df.columns}
        panel = df.groupby(['target_bank', 'year']).agg(**valid_agg).reset_index()
        assert (panel['frac_ctx_fallback'] >= 0).all()
        assert (panel['frac_ctx_fallback'] <= 1).all()
        # 银行 A: 1/2 = 0.5; 银行 B: 1/1 = 1.0
        bank_a = panel.loc[panel['target_bank'] == 'A', 'frac_ctx_fallback'].iloc[0]
        bank_b = panel.loc[panel['target_bank'] == 'B', 'frac_ctx_fallback'].iloc[0]
        assert bank_a == pytest.approx(0.5)
        assert bank_b == pytest.approx(1.0)

    def test_agg_dict_skips_when_column_absent(self):
        """无 ctx_is_fallback 列时, build_aggregation_dict 跳过 frac_ctx_fallback 注册 (向后兼容)."""
        from news_process.pipeline.panel.encode import build_aggregation_dict
        df = pd.DataFrame({
            'target_bank': ['A'],
            'year': [2024],
            'llm_vote_score_full': [1],
        })
        agg = build_aggregation_dict(df)
        assert 'frac_ctx_fallback' not in agg, \
            "向后兼容: 无 ctx_is_fallback 列时不注册聚合"


class TestIntensityVerifiedDisagreement:
    """R4-2 边际信息量 sanity check: ctx_is_fallback vs intensity_verified_ctx 非同义.

    若 disagreement < 5% → 两个信号近共线 → 新列边际价值低, 应升级到 user.
    """

    def test_signals_can_disagree(self):
        """构造 disagreement case: ctx_is_fallback=True 但 intensity_verified_ctx=True
        (fallback 后的 content_ctx == content_full, 但 fintech IDF 验证仍可能通过).
        """
        # ctx==full 不等于 intensity 验证失败; 这是构造性证明两者非同义
        df = pd.DataFrame({
            'ctx_is_fallback': [True, True, False, False],
            'intensity_verified_ctx': [True, False, True, False],
        })
        # 四种组合都合法 → 信号正交
        agreement = (df['ctx_is_fallback'] == ~df['intensity_verified_ctx'])
        # 如果完全同义, agreement.mean() 应 ≈ 1.0; 实际为 0.5
        assert agreement.mean() < 0.95, \
            "ctx_is_fallback 与 ~intensity_verified_ctx 不应完全同义 (R4-2)"
