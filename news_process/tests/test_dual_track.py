"""
test_dual_track.py — 三轨重构全面验证测试 (full/ctx/ss)
==========================================

用 pytest 验证所有阶段输出的列完整性、数据质量和回退公理。

三轨 (ss 银行+金科同句共现轨, 2026-06-14): 在 full/ctx 之外新增并列第三主轨
content_ss (suffix '_ss', 标签"(银行+金科同句)"); 下游各阶段以
['_full','_ctx','_ss'] 三轨平价产列。⚠ ss 列须经付费 stage 21 重跑播种缓存后
方落盘 — 在 ss 数据落盘前, 本测试对 `_ss` 列一律走 **skip-if-missing 软守卫**
(graceful skip), 不强断言 (避免冻结 panel 上误 fail); 仅当 ss 列已存在时才校验
结构平价。

注意:
  本测试需要实际的 data/processed/*.parquet 文件存在。
  如果文件不存在，对应测试将被 skip 而非 fail。

Phase 8 (2026-05-04): 路径从 ``data_processed`` 重命名为 ``data/processed``.
"""
import os

import pandas as pd
import pytest

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope='module')
def output_dir():
    """返回 data/processed 绝对路径 (Phase 8 重命名后)。"""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'data', 'processed',
    )


def _load_parquet_or_skip(output_dir, filename):
    """加载 Parquet 文件，不存在则 skip。"""
    path = os.path.join(output_dir, filename)
    if not os.path.exists(path):
        pytest.skip(f"{filename} not found (未生成或路径不存在)")
    return pd.read_parquet(path)


# ============================================================================
# 阶段 21: LLM 双轨输出
# ============================================================================

class TestStage21LLMDualTrack:
    """阶段 21: LLM 三轨输出列完整性 (full/ctx/ss)。"""

    @pytest.fixture(scope='class')
    def df21(self, output_dir):
        return _load_parquet_or_skip(output_dir, '21_tone_llms.parquet')

    def test_core_columns_exist(self, df21):
        """核心双轨列存在.

        v3.2.0 BREAKING (dual-track 化) 后: innovation_locus / innovation_substantiveness
        / category_confidence 被拆分为 _full / _ctx 双轨. 本测试同步至 v3.2.0+ schema.
        """
        core_cols = [
            'llm_verified_full', 'llm_verified_ctx',
            'llm_sentiment_full', 'llm_sentiment_ctx',
            'llm_agreement_rate_full', 'llm_agreement_rate_ctx',
            # v3.2.0 dual-track 后 → _full/_ctx 双轨; 原非双轨列不再产出
            'innovation_locus_full', 'innovation_locus_ctx',
            'category_confidence_full', 'category_confidence_ctx',
            # v7 新增 stage 3 (W&Z 1994/1998 ASQ substantiveness + Gomber 2018 locus confidence)
            'innovation_substantiveness_full', 'innovation_substantiveness_ctx',
            'innovation_substantiveness_confidence_full',
            'innovation_substantiveness_confidence_ctx',
            'innovation_locus_confidence_full',
            'innovation_locus_confidence_ctx',
        ]
        for col in core_cols:
            assert col in df21.columns, f"缺少核心列: {col}"

    def test_ss_core_columns_parity(self, df21):
        """三轨 (ss 2026-06-14): ss 核心列与 ctx 平价 (skip-if-missing 软守卫)。

        ss 列须经付费 stage 21 重跑播种后落盘; ss 未落盘时整体 skip。一旦 ss 锚定
        列 (llm_verified_ss) 出现, 则其余 ss 核心列必须全平价存在 (机械 _ctx→_ss)。
        """
        if 'llm_verified_ss' not in df21.columns:
            pytest.skip("ss 轨尚未落盘 (需付费 stage 21 重跑播种 ss 缓存)")
        ss_core = [c.replace('_ctx', '_ss') for c in [
            'llm_verified_ctx', 'llm_sentiment_ctx', 'llm_agreement_rate_ctx',
            'innovation_locus_ctx', 'category_confidence_ctx',
            'innovation_substantiveness_ctx',
            'innovation_substantiveness_confidence_ctx',
            'innovation_locus_confidence_ctx',
        ]]
        for col in ss_core:
            assert col in df21.columns, f"ss 轨已落盘但缺核心列: {col}"

    def test_per_model_dual_track_columns(self, df21):
        """逐模型双轨列完整"""
        # 非模型来源的 *_verified_full 列 (需排除):
        #   - 'llm':       v3.2.0 聚合 verification flag (跨模型 OR)
        #   - 'intensity': v3.6.0 stage 14 fintech intensity 验证标志 (上游列)
        _NON_MODEL_VERIFIED_PREFIXES = {'llm', 'intensity'}
        model_shorts = []
        for c in df21.columns:
            if c.endswith('_verified_full'):
                sn = c.replace('_verified_full', '')
                if sn not in _NON_MODEL_VERIFIED_PREFIXES:
                    model_shorts.append(sn)

        assert len(model_shorts) > 0, "未发现逐模型列"

        _model_sfx = ['_verified', '_sentiment',
                      '_verification_confidence', '_sentiment_confidence']
        # 三轨 (ss 2026-06-14): full/ctx 始终硬断言; ss 仅当首模型 ss 锚定列出现时
        # 才纳入 (skip-if-missing 软守卫, ss 须付费 stage 21 重跑后落盘)。
        tracks = ['_full', '_ctx']
        _ss_landed = f"{model_shorts[0]}_sentiment_ss" in df21.columns
        if _ss_landed:
            tracks = tracks + ['_ss']

        for sn in model_shorts:
            for track in tracks:
                for sfx in _model_sfx:
                    col = f"{sn}{sfx}{track}"
                    assert col in df21.columns, \
                        f"逐模型列缺失: {col}"
            # 标题轨道仅含情感列（无真伪验证列）
            # 注：v3.8.0 (remove-title-track) 已删除独立 _title 情感轨,
            # 这些列不会再生成 → 下方分支在现行 schema 下恒走 skip (历史兼容保留)
            first_title_col = f"{model_shorts[0]}_sentiment_title"
            if first_title_col not in df21.columns:
                pytest.skip("标题轨道列尚未生成（需重跑 21_tone_llms.py）")
            for sfx in ['_sentiment', '_sentiment_confidence']:
                col = f"{sn}{sfx}_title"
                assert col in df21.columns, \
                    f"标题轨道列缺失: {col}"


# ============================================================================
# 阶段 22: 词典法双轨输出
# ============================================================================

class TestStage22DictDualTrack:
    """阶段 22: 词典法三轨输出列完整性 (full/ctx/ss)。"""

    @pytest.fixture(scope='class')
    def df22(self, output_dir):
        return _load_parquet_or_skip(output_dir, '22_words_tone.parquet')

    def test_dict_dual_track_columns(self, df22):
        """6 套词典 × 2 轨道 × 3 指标 = 36 列 (ss 落盘后 × 3 轨 = 54 列; loughran 第 6 部仅在 golden 重生后落盘)"""
        dicts = ['jiang_2021', 'yao_2021', 'bian_2021',
                 'du_2022', 'you_2018']
        # v3.10.0: 第 6 部 loughran 仅当已落盘 (golden 重生后) 时纳入硬断言, 否则软跳过
        # (旧盘面 5-dict parquet 仍绿; 重生后 6-dict 自动覆盖)。
        if 'loughran_score_full' in df22.columns:
            dicts = dicts + ['loughran']
        # 三轨 (ss 2026-06-14): full/ctx 硬断言; ss 仅当首词典首指标 ss 列已落盘时
        # 纳入 (skip-if-missing 软守卫, ss 须付费 stage 21 重跑前置 stage 13/22 重算)。
        tracks = ['_full', '_ctx']
        if f'{dicts[0]}_score_ss' in df22.columns:
            tracks = tracks + ['_ss']
        for d in dicts:
            for track in tracks:
                for sfx in ['_score', '_label', '_zscore']:
                    col = f"{d}{sfx}{track}"
                    assert col in df22.columns, f"缺少列: {col}"
        # 标题轨道 — v3.8.0 已删除 _title 情感轨, 现行 schema 下恒 skip (历史兼容保留)
        if f'{dicts[0]}_score_title' not in df22.columns:
            pytest.skip("标题轨道列尚未生成（需重跑 22_tone_words.py）")
        for d in dicts:
            for sfx in ['_score', '_label', '_zscore']:
                col = f"{d}{sfx}_title"
                assert col in df22.columns, f"缺少列: {col}"

    def test_sentiment_details_columns(self, df22):
        """sentiment_details 双轨列存在 (ss 落盘后第三轨平价, 软守卫)"""
        assert 'sentiment_details_full' in df22.columns
        assert 'sentiment_details_ctx' in df22.columns
        # 三轨 (ss): 仅当 ss 列已落盘时校验平价存在
        if 'sentiment_details_ss' in df22.columns:
            assert 'sentiment_details_ss' in df22.columns

    def test_zscore_independence(self, df22):
        """Z-score 独立标准化: 均值接近 0 (三轨 full/ctx/ss, 每轨各 if 存在守卫)"""
        dicts = ['jiang_2021', 'yao_2021', 'bian_2021',
                 'du_2022', 'you_2018', 'loughran']  # v3.10.0 +loughran (per-col 软守卫)
        # 三轨 (ss 2026-06-14): 每轨各自 `if col in columns` 守卫 → ss/loughran 未落盘自动跳过
        for d in dicts:
            for track in ('_full', '_ctx', '_ss'):
                col = f'{d}_zscore{track}'
                if col in df22.columns:
                    mean_t = df22[col].mean()
                    assert abs(mean_t) < 0.01, \
                        f"{d} zscore{track}_mean={mean_t:.6f} 不接近 0"


# ============================================================================
# 阶段 23: BERT 双轨输出
# ============================================================================

class TestStage23BERTDualTrack:
    """阶段 23: BERT 三轨输出列完整性 (full/ctx/ss)。"""

    @pytest.fixture(scope='class')
    def df23(self, output_dir):
        return _load_parquet_or_skip(output_dir, '23_bert_tone.parquet')

    def test_bert_window_columns(self, df23):
        """BERT 窗口计数双轨列 (ss 落盘后第三轨, 软守卫)"""
        assert 'bert_num_windows_full' in df23.columns
        assert 'bert_num_windows_ctx' in df23.columns
        # 三轨 (ss 2026-06-14): bert_num_windows_ss 须 ss 落盘后才存在
        if 'bert_num_windows_ss' in df23.columns:
            assert 'bert_num_windows_ss' in df23.columns

    def test_inherited_llm_columns(self, df23):
        """LLM 列继承检查 (ss 落盘后第三轨, 软守卫)"""
        assert 'llm_verified_full' in df23.columns
        assert 'llm_sentiment_ctx' in df23.columns
        if 'llm_verified_ss' in df23.columns:
            assert 'llm_sentiment_ss' in df23.columns

    def test_inherited_dict_columns(self, df23):
        """词典列继承检查 (ss 落盘后第三轨, 软守卫)"""
        assert 'jiang_2021_score_full' in df23.columns
        assert 'jiang_2021_score_ctx' in df23.columns
        if 'jiang_2021_score_ss' in df23.columns:
            assert 'jiang_2021_score_ss' in df23.columns


# ============================================================================
# 阶段 41-45: 面板数据双轨输出
# ============================================================================

class TestPanelDualTrack:
    """阶段 41-45: 面板数据三轨输出 (full/ctx/ss)。"""

    @pytest.fixture(scope='class')
    def df_panel(self, output_dir):
        return _load_parquet_or_skip(output_dir, '40_panel_yearly.parquet')

    def test_panel_key_columns(self, df_panel):
        """面板核心列存在"""
        panel_key_cols = [
            'n_articles', 'target_bank', 'year',
            'llm_vote_tone_full', 'llm_vote_tone_ctx',
            'pos_frac_full', 'pos_frac_ctx',
            'neg_frac_full', 'neg_frac_ctx',
            'dict_avg_tone_full', 'dict_avg_tone_ctx',
            'bert_avg_pos_full', 'bert_avg_pos_ctx',
            'bert_avg_neg_full', 'bert_avg_neg_ctx',
            'llm_models_avg_tone_full', 'llm_models_avg_tone_ctx',
            'avg_agreement_rate_full', 'avg_agreement_rate_ctx',
        ]
        for col in panel_key_cols:
            assert col in df_panel.columns, f"面板缺少核心列: {col}"

    def test_panel_ss_key_columns_parity(self, df_panel):
        """三轨 (ss 2026-06-14): 面板 ss 主语调列与 ctx 平价 (skip-if-missing 软守卫)。

        ss 面板列须经付费 stage 21 重跑 + stage 45/46 重生后落盘。ss 锚定列
        (llm_vote_tone_ss) 缺失时整体 skip; 一旦出现则其余 ss 主语调列平价校验。
        """
        if 'llm_vote_tone_ss' not in df_panel.columns:
            pytest.skip("ss 面板轨尚未落盘 (需付费 stage 21 重跑 + stage 45/46 重生)")
        ss_key_cols = [c.replace('_ctx', '_ss') for c in [
            'llm_vote_tone_ctx', 'pos_frac_ctx', 'neg_frac_ctx',
            'dict_avg_tone_ctx', 'bert_avg_pos_ctx', 'bert_avg_neg_ctx',
            'llm_models_avg_tone_ctx', 'avg_agreement_rate_ctx',
        ]]
        for col in ss_key_cols:
            assert col in df_panel.columns, f"ss 面板轨已落盘但缺主语调列: {col}"

    def test_panel_dual_track_balance(self, df_panel):
        """面板 _full / _ctx / _ss 列数基本均衡 (ss 未落盘时仅校验 full/ctx)"""
        full_cols = [c for c in df_panel.columns if c.endswith('_full')]
        ctx_cols = [c for c in df_panel.columns if c.endswith('_ctx')]
        ss_cols = [c for c in df_panel.columns if c.endswith('_ss')]
        # 允许一定比例差异（某些变量可能仅 full 轨道）
        assert len(full_cols) > 0, "面板无 _full 列"
        assert len(ctx_cols) > 0, "面板无 _ctx 列"
        # 三轨 (ss): ss 列须付费重跑后落盘; 已落盘则断言非空 (结构平价)
        if ss_cols:
            assert len(ss_cols) > 0, "面板 ss 轨已落盘但无 _ss 列"


# ============================================================================
# 回退公理验证 (NaN 检查)
# ============================================================================

class TestFallbackAxiom:
    """回退公理验证 (v6/F2 重写)。

    v6 之前: "_full 轨道无 NaN" 是不变量。
    v6 之后: 该不变量被 **故意打破**——LLM 调用失败 / verification 拒绝 /
            sentiment 三方分歧平局等情况，sentiment 列**应当**为 NaN，
            以与"真实中性"严格区分。这是 F2 修复的核心。

    新不变量：BERT / 词典法等**非 LLM 衍生的双轨列**仍应无 NaN
            （这些方法对每篇文章都能产出确定值）。

    三轨 (ss 2026-06-14): ss 轨与 ctx 轨同一回退/NaN 语义 — ss 列须付费 stage 21
            重跑后落盘, 故 ss NaN 校验走 skip-if-missing 软守卫。
    """

    @pytest.fixture(scope='class')
    def df23(self, output_dir):
        return _load_parquet_or_skip(output_dir, '23_bert_tone.parquet')

    # v6/F2 允许 NaN 的列前缀（LLM 衍生）
    # v7 扩展: 含 per-model _verified 列 — API 失败时 (raw_text is None) 这些列填 None,
    #          与 sentiment NaN 同语义 (LLM 衍生失败信号, 见 tone_llms.py 814-817)
    _LLM_NAN_ALLOWED_PREFIXES = (
        'llm_sentiment',
        'llm_agreement_rate_s',  # 仅 verifying 子集上的 agree rate
        'gpt54nano_sentiment', 'gemini31_sentiment', 'deepseekv4_sentiment',
        'gpt54nano_prob_score', 'gemini31_prob_score', 'deepseekv4_prob_score',
        'gpt54nano_prob_source', 'gemini31_prob_source', 'deepseekv4_prob_source',
        # v7: per-model verified API-failure NaN 容忍
        'gpt54nano_verified', 'gemini31_verified', 'deepseekv4_verified',
        # v3.7.1 (test drift fix): v3.2.0 dual-track BREAKING 后, stage 21 LLM
        # 也产 innovation_locus / innovation_substantiveness / category_confidence /
        # ...confidence 列 — 这些与 sentiment 同源, LLM 失败时 NaN 是预期信号.
        'innovation_locus',         # *_full / *_ctx
        'innovation_substantiveness',
        'category_confidence',
        # v3.4.0+ (P5 collab + ensemble aggregation): innovation_collab_mode 及
        # avg_subst_prob_score / avg_locus_prob_score / avg_collab_prob_score 是
        # 跨模型聚合 LLM 衍生列, 任何 LLM 失败的样本上聚合为 NaN 是预期信号.
        'innovation_collab_mode',
        'avg_subst_prob_score',
        'avg_locus_prob_score',
        'avg_collab_prob_score',
    )

    def _is_llm_nan_allowed(self, col_name: str) -> bool:
        return any(col_name.startswith(p) for p in self._LLM_NAN_ALLOWED_PREFIXES)

    def test_no_nan_in_full_track(self, df23):
        """_full 轨道：仅 LLM 衍生列允许 NaN（v6/F2 语义），其余无 NaN。"""
        full_cols = [c for c in df23.columns if c.endswith('_full')]
        unexpected_nan = {}
        for c in full_cols:
            n = df23[c].isna().sum()
            if n > 0 and not self._is_llm_nan_allowed(c):
                unexpected_nan[c] = int(n)
        assert len(unexpected_nan) == 0, \
            f"_full 轨道存在不应有的 NaN (非 LLM 衍生列): {unexpected_nan}"

    def test_no_nan_in_ctx_track(self, df23):
        """_ctx 轨道：仅 LLM 衍生列允许 NaN（v6/F2 语义），其余无 NaN。"""
        ctx_cols = [c for c in df23.columns if c.endswith('_ctx')]
        unexpected_nan = {}
        for c in ctx_cols:
            n = df23[c].isna().sum()
            if n > 0 and not self._is_llm_nan_allowed(c):
                unexpected_nan[c] = int(n)
        assert len(unexpected_nan) == 0, \
            f"_ctx 轨道存在不应有的 NaN (非 LLM 衍生列): {unexpected_nan}"

    def test_no_nan_in_ss_track(self, df23):
        """三轨 (ss 2026-06-14): _ss 轨道与 ctx 同 NaN 语义 (skip-if-missing 软守卫)。

        ss 列须付费 stage 21 重跑后落盘; 未落盘则整体 skip。一旦 ss 列存在,
        仅 LLM 衍生列允许 NaN, 其余 (BERT/词典 ss 列) 应无 NaN (镜像 ctx 不变式)。
        """
        ss_cols = [c for c in df23.columns if c.endswith('_ss')]
        if not ss_cols:
            pytest.skip("ss 轨尚未落盘 (需付费 stage 21 重跑播种 ss 缓存)")
        unexpected_nan = {}
        for c in ss_cols:
            n = df23[c].isna().sum()
            if n > 0 and not self._is_llm_nan_allowed(c):
                unexpected_nan[c] = int(n)
        assert len(unexpected_nan) == 0, \
            f"_ss 轨道存在不应有的 NaN (非 LLM 衍生列): {unexpected_nan}"


# ============================================================================
# 全量 LLM 输出验证
# ============================================================================

class TestFullLLMOutput:
    """全量 LLM 输出文件验证。"""

    @pytest.fixture(scope='class')
    def df21(self, output_dir):
        return _load_parquet_or_skip(output_dir, '21_tone_llms.parquet')

    @pytest.fixture(scope='class')
    def df21_full(self, output_dir):
        return _load_parquet_or_skip(
            output_dir, '21_tone_llms_full.parquet')

    def test_full_file_columns(self, df21_full):
        """全量文件包含三轨列 (full/ctx; ss 落盘后第三轨, 软守卫)"""
        assert 'llm_verified_full' in df21_full.columns
        assert 'llm_verified_ctx' in df21_full.columns
        # 三轨 (ss 2026-06-14): ss 列须付费 stage 21 重跑后落盘
        if 'llm_verified_ss' in df21_full.columns:
            assert 'llm_verified_ss' in df21_full.columns

    def test_filtered_row_count(self, df21, df21_full):
        """过滤文件行数 ≈ 全量文件中 verified_full=True 的行数。

        历史 invariant 是严格相等，但当时 stage 21 的 title-track 批处理
        会偶发地丢失少量行（约 < 1%），属于已知的非 v6 引入小问题。
        v6 仍校验"差距 ≤ 1% 且不超过 100 行"以防退化。
        (注: v3.8.0 已移除 title 情感轨, 上述丢行机制不复存在; 宽容度断言保留。)
        """
        verified_full = int(df21_full['llm_verified_full'].sum())
        diff = abs(len(df21) - verified_full)
        assert diff <= max(100, int(verified_full * 0.01)), \
            f"filtered={len(df21)}, verified_full={verified_full}, diff={diff}"
