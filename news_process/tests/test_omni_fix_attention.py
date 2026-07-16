"""test_omni_fix_attention.py — OMNI 审计 g-attention 组修复回归锁
=================================================================

锁定 2026-06-11 OMNI 审计 (scripts/audit/_omni_fix/g-attention.json) 八条
确认缺陷的修复后行为, 防静默 revert:

  - g-attention-01/08: attention_attr_share 由 clip(Σctx/Σfull, 0, 1) 右删失
                       构造改为有界 share Σctx/(Σctx+Σfull) ∈ [0,1] (保序无删失)
  - g-attention-02:    维度⑤⑥互斥构造 official := OFF−MKT / market := MKT−OFF
                       (双判据媒体不入任一处理组, 落入 nonoff/nonmkt 对照)
  - g-attention-03:    停刊检测构念措辞修正为"话题覆盖退出"代理 (披露锁:
                       suspected 未经 NPPA 证实仍入排除集, 行为契约不变)
  - g-attention-04:    平衡媒体面板判据由端点 (first/last_year) 改窗口内逐年覆盖
  - g-attention-05:    ft_attn_prov/city 地理注意力指数 leave-one-out 化
                       (剔除焦点银行自身文章后再算 cell 指数)
  - g-attention-06:    attention_disp_full = outlet 集中度 HHI (高值=集中),
                       docstring/spec 披露锁 + 单 outlet → 1.0 功能锁
  - g-attention-07:    homeprov/homecity 地理元数据缺失 → NaN 出域 (而非编码
                       为"非本地" 0 混入分母与 away 对照组)
  - 组级裁决 (zerofill): n_articles_exc 计数零填契约补齐 — 本模块在
                       balance_panel 之后 merge, 零文章 bank-year 不得残留 NaN

全部用合成 DataFrame + tmp_path 临时 parquet/JSON, 不依赖盘上大数据,
不调外部 API。
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from news_process.pipeline.panel import attention_media as am

pytestmark = pytest.mark.fast

SRC = Path(am.__file__).read_text(encoding='utf-8')
_SPEC = (Path(am.__file__).parents[2] / 'papers' / 'bank_fintech_attention'
         / 'paper_spec.yaml').read_text(encoding='utf-8')

_S14_NAME = am.FILENAMES.get(
    'output_14_fintech_intensity', '15_fintech_intensity.parquet')
_F12_NAME = am.FILENAMES.get(
    'output_12_fintech_full', '12_fintech_news_full.parquet')


# ============================================================================
# 共享 helper: 合成 attention 处理变量环境 (14/12 parquet → tmp OUTPUT_DIR)
# ============================================================================

def _write_attention_env(tmp_path, monkeypatch):
    """写最小 15_fintech_intensity + 12_fintech_news_full 并重定向 OUTPUT_DIR。

    设计: A/B/C 各 1 篇 fintech 文章, ctx/full 强度比分别 1.5 / 1.2 / 0.5
    (前两个在旧 clip 构造下越界删失到 1.0); D 仅 1 篇非 fintech (零 fintech 曝光)。
    """
    s14 = pd.DataFrame({
        'target_bank': ['A', 'B', 'C'],
        '日期': ['2020-03-01'] * 3,
        'fintech_intensity_score_full': [1.0, 1.0, 1.0],
        'fintech_intensity_score_ctx': [1.5, 1.2, 0.5],
    })
    f12 = pd.DataFrame({
        'target_bank': ['A', 'A', 'B', 'C', 'D'],
        '日期': ['2020-03-01'] * 5,
        'is_fintech_news': [True, False, True, True, False],
        '媒体(中文)': ['媒体一', '媒体二', '媒体一', '媒体三', '媒体二'],
    })
    s14.to_parquet(tmp_path / _S14_NAME)
    f12.to_parquet(tmp_path / _F12_NAME)
    monkeypatch.setattr(am, 'OUTPUT_DIR', str(tmp_path))
    return pd.DataFrame({'target_bank': ['A', 'B', 'C', 'D'],
                         'year': [2020] * 4})


# ============================================================================
# g-attention-01/08: attr_share 有界构造 (无 censor clip)
# ============================================================================

class TestAttrShareBoundedConstruction:

    @pytest.fixture()
    def out(self, tmp_path, monkeypatch):
        panel = _write_attention_env(tmp_path, monkeypatch)
        return am.compute_attention_treatments(panel).set_index('target_bank')

    def test_share_formula_ctx_over_sum(self, out):
        # share = Σctx/(Σctx+Σfull): A=1.5/2.5, B=1.2/2.2, C=0.5/1.5
        assert out.loc['A', 'attention_attr_share'] == pytest.approx(0.6)
        assert out.loc['B', 'attention_attr_share'] == pytest.approx(1.2 / 2.2)
        assert out.loc['C', 'attention_attr_share'] == pytest.approx(0.5 / 1.5)

    def test_no_right_censoring_at_one(self, out):
        # 旧 clip 构造: A/B (ctx>full) 同被记 1.0 (删失质量点 + 排序破坏)。
        # 新构造: 无任何值贴 1.0, 且保持 r=ctx/full 的严格单调排序 A > B > C。
        s = out['attention_attr_share'].dropna()
        assert (s < 1.0).all(), f'残留删失质量点 1.0: {s[s >= 1.0]}'
        assert (out.loc['A', 'attention_attr_share']
                > out.loc['B', 'attention_attr_share']
                > out.loc['C', 'attention_attr_share'])

    def test_share_structurally_bounded(self, out):
        s = out['attention_attr_share'].dropna()
        assert s.between(0.0, 1.0).all()

    def test_zero_fintech_share_nan(self, out):
        # Σctx+Σfull=0 (零 fintech) → NaN (无可归因), 不是 0
        assert pd.isna(out.loc['D', 'attention_attr_share'])

    def test_source_clip_removed(self):
        # 源码级: censor clip 构造不得复活 (允许 sum 的 clip(lower=0) 防负守卫)
        assert '_share.clip(0.0, 1.0)' not in SRC
        assert "(t['sum_ctx'] + t['sum_full'])" in SRC


# ============================================================================
# g-attention-02: official/market 互斥构造
# ============================================================================

def _write_media_cls(tmp_path, monkeypatch, extra=None):
    """写媒体分类 JSON + 重定向 CONFIG 路径; OFF∩MKT 含双判据媒体 '双料报'。"""
    cls = {
        'financial_media': [], 'comprehensive_media': [], 'central_media': [],
        'official_media': ['官方报', '双料报'],
        'market_media': ['市场报', '双料报'],
        'deep_dive_periodicals': [], 'high_frequency_dailies': [],
    }
    if extra:
        cls.update(extra)
    (tmp_path / 'media_classification.json').write_text(
        json.dumps(cls, ensure_ascii=False), encoding='utf-8')
    monkeypatch.setitem(am.CONFIG['paths'], 'media_weights_file',
                        str(tmp_path / 'media_weights.json'))
    monkeypatch.setitem(am.CONFIG['paths'], 'nppa_newspapers_csv',
                        str(tmp_path / 'no_such_nppa.csv'))
    monkeypatch.setattr(am, 'OUTPUT_DIR', str(tmp_path))


class TestOfficialMarketMutualExclusion:

    @pytest.fixture()
    def out(self, tmp_path, monkeypatch):
        _write_media_cls(tmp_path, monkeypatch)
        df = pd.DataFrame({
            '媒体(中文)': ['官方报', '市场报', '双料报', '其他报'],
            'target_bank': ['B1'] * 4,
            'year': [2023] * 4,
            'llm_vote_score_full': [1.0, -1.0, 0.0, 0.0],
            'llm_vote_score_ctx': [1.0, -1.0, 0.0, 0.0],
        })
        panel = pd.DataFrame({'target_bank': ['B1'], 'year': [2023]})
        return am.compute_media_heterogeneity(df, panel).iloc[0]

    def test_official_excludes_dual_criterion(self, out):
        # official := OFF−MKT → 双料报不计入官方组, frac = 1/4 (非旧 2/4)
        assert out['official_media_frac'] == pytest.approx(0.25)

    def test_market_excludes_dual_criterion(self, out):
        # market := MKT−OFF → 双料报不计入市场组, frac = 1/4 (非旧 2/4)
        assert out['market_media_frac'] == pytest.approx(0.25)

    def test_frac_sum_le_one(self, out):
        # 互斥构造 ⟹ 占比之和 ≤ 1 (旧重叠 dummy 实测和 1.53)
        assert (out['official_media_frac'] + out['market_media_frac']) <= 1.0 + 1e-9

    def test_nonoff_contains_all_market_media(self, out):
        # nonoff 对照组 = {市场报, 双料报, 其他报} → mean(-1, 0, 0) = -1/3
        # (旧构造的 nonoff 反而剔除了大部分市场化媒体)
        assert out['tone_official_media_full'] == pytest.approx(1.0)
        assert out['tone_nonoff_media_full'] == pytest.approx(-1.0 / 3.0)
        assert out['tone_gap_official_nonoff_full'] == pytest.approx(4.0 / 3.0)

    def test_nonmkt_contains_dual_and_official(self, out):
        # nonmkt 对照组 = {官方报, 双料报, 其他报} → mean(1, 0, 0) = 1/3
        assert out['tone_market_media_full'] == pytest.approx(-1.0)
        assert out['tone_nonmkt_media_full'] == pytest.approx(1.0 / 3.0)
        assert out['tone_gap_market_nonmkt_full'] == pytest.approx(-4.0 / 3.0)

    def test_source_mutual_exclusion_construct(self):
        # 源码级: 两个 dummy 必须用集合差构造
        assert 'isin(OFFICIAL - MARKET)' in SRC
        assert 'isin(MARKET - OFFICIAL)' in SRC
        # 旧"正交分类"误述日志不得复活 (official/market 互斥, 仅与内容分类正交)
        assert '中央级/official/market 与内容分类为正交分类 (无互斥约束)' not in SRC


# ============================================================================
# g-attention-03: 停刊检测 = 话题覆盖退出代理 (披露锁 + 行为契约锁)
# ============================================================================

class TestCessationTopicExitDisclosure:

    def test_suspected_still_in_exclusion_set(self, tmp_path):
        # 行为契约 (裁决: 措辞修正, 不收窄排除集): 无 NPPA 证实的 data-driven
        # 旗标 (suspected) 仍全量进入 ceased_all
        rows = []
        for y in (2007, 2008):
            rows += [{'媒体(中文)': '退出报', 'year': y, 'target_bank': 'B1'}] * 6
        for y in range(2007, 2025):
            rows.append({'媒体(中文)': '在刊报', 'year': y, 'target_bank': 'B1'})
        df = pd.DataFrame(rows)
        ceased, report = am.detect_defacto_cessation(
            df, am.logger, str(tmp_path))
        assert '退出报' in ceased          # last_year=2008 < 2022, n=12 ≥ 10
        assert '在刊报' not in ceased
        assert report.loc['退出报', 'cessation_status'] == 'suspected'
        assert (df.loc[df['媒体(中文)'] == '退出报', '_is_ceased_media'] == 1).all()

    def test_docstring_topic_exit_construct(self):
        # 披露锁: docstring 必须以"话题覆盖退出"为构念, 并披露 suspected 入排除集
        doc = am.detect_defacto_cessation.__doc__
        assert '话题' in doc and '覆盖退出' in doc
        assert '未经 NPPA 证实' in doc
        assert 'article × bank 行计数' in doc  # n_articles 非 docid 去重的披露


# ============================================================================
# g-attention-04: 平衡媒体面板 = 窗口内逐年覆盖
# ============================================================================

class TestBalancedPanelPerYearCoverage:

    @pytest.fixture()
    def out(self):
        # F6 (2026-07-16): 年跨度扩至 2025 (T=19 口径); GAP 端点同步 (2007, 2025)
        # 保持中间全缺 — 维持"旧端点判据误纳入/新逐年判据剔除"的回归判别力
        rows = []
        for y in range(2007, 2026):     # FULL: 2007..2025 每年 1 篇
            rows.append({'媒体(中文)': 'FULL', 'target_bank': 'B1', 'year': y,
                         'llm_vote_score_full': 0.5})
        for y in (2007, 2025):          # GAP: 仅端点两年 (旧端点判据误纳入)
            rows.append({'媒体(中文)': 'GAP', 'target_bank': 'B1', 'year': y,
                         'llm_vote_score_full': -1.0})
        df = pd.DataFrame(rows)
        panel = pd.DataFrame({'target_bank': 'B1',
                              'year': list(range(2007, 2026))})
        return am.compute_balanced_media_robustness(df, panel, am.logger, [])

    def test_intermittent_media_excluded(self, out):
        # GAP (first=2007, last=2025, 中间全缺) 不再算"平衡" → 每窗口仅 FULL 1 家
        for sfx in ('w0725', 'w1025', 'w1125'):
            assert (out[f'n_media_bal_{sfx}'] == 1).all(), \
                f'{sfx}: 间歇媒体被误纳入平衡子集'

    def test_bal_tone_excludes_gap_articles(self, out):
        # 2007 年: 旧判据含 GAP → mean(0.5, -1.0) = -0.25; 新判据仅 FULL → 0.5
        row = out[out['year'] == 2007].iloc[0]
        assert row['bal_w0725_tone_full'] == pytest.approx(0.5)

    def test_source_per_year_criterion(self):
        # 源码级: 逐年覆盖判据在, 端点判据不得复活
        assert "groupby('媒体(中文)')['year'].nunique()" in SRC
        assert "(media_span['first_year'] <= start_year)" not in SRC

    def test_f6_windows_t19_endpoint_and_name_consistency(self):
        """F6 T5 (2026-07-16): 右端点=2025 (T=19 口径) 且窗口后缀名实一致 —
        防下次语料口径变更再次漏改功能常量 (90c40e92 只改注释的教训)。"""
        for start, end, sfx in am.ROBUSTNESS_WINDOWS:
            assert end == 2025, f'窗口 {sfx} 右端点 {end} != 2025 (T=19 口径)'
            assert sfx == f'w{start % 100:02d}{end % 100:02d}', \
                f'窗口后缀 {sfx} 与年窗 ({start},{end}) 名实不符'


# ============================================================================
# g-attention-05: 地理注意力指数 leave-one-out
# ============================================================================

class TestGeoAttentionLeaveOneOut:

    GEO = '国家地区/省份'

    @pytest.fixture()
    def panel(self):
        # cell (G1, 2020): 10 唯一文章, 4 fintech。
        #   bank A 提及 d1(ft) + d5(non) → LOO = (4−1)/(10−2) = 0.375
        #   bank B 提及 d6(non)          → LOO = (4−0)/(10−1) = 4/9
        #   bank C 提及 7 篇 (3 ft)      → LOO 分母 10−7 = 3 < 5 → NaN
        rows = [
            {'docid': 'd1', 'target_bank': 'A', 'is_fintech_news': True},
            {'docid': 'd5', 'target_bank': 'A', 'is_fintech_news': False},
            {'docid': 'd6', 'target_bank': 'B', 'is_fintech_news': False},
        ]
        for d, ft in [('d2', True), ('d3', True), ('d4', True),
                      ('d7', False), ('d8', False), ('d9', False),
                      ('d10', False)]:
            rows.append({'docid': d, 'target_bank': 'C', 'is_fintech_news': ft})
        df_all = pd.DataFrame(rows)
        df_all['year'] = 2020
        df_all[self.GEO] = 'G1'

        df_unique = df_all.drop_duplicates(subset=['docid'])
        idx = am._build_geo_index(df_unique, self.GEO, 'ft_attn_prov',
                                  min_articles=5)
        panel = pd.DataFrame({'target_bank': ['A', 'B', 'C'],
                              'year': [2020] * 3})
        out = am._merge_geo_index_to_panel(
            df_all, panel,
            idx[[self.GEO, 'year', '_total', '_ft', 'ft_attn_prov']],
            self.GEO, 'ft_attn_prov', vol_col='ft_vol_prov')
        return out.set_index('target_bank')

    def test_loo_excludes_own_articles(self, panel):
        # 旧全单元值: 三家银行同得 0.4; LOO 后随自身贡献而异
        assert panel.loc['A', 'ft_attn_prov'] == pytest.approx(0.375)
        assert panel.loc['B', 'ft_attn_prov'] == pytest.approx(4.0 / 9.0)
        assert panel.loc['A', 'ft_attn_prov'] != pytest.approx(0.4)

    def test_dominant_bank_small_residual_nan(self, panel):
        # 自身支配单元: 剔除后剩余 < min_articles → NaN (0/1 噪声守卫)
        assert pd.isna(panel.loc['C', 'ft_attn_prov'])

    def test_loo_values_stay_bounded(self, panel):
        v = panel['ft_attn_prov'].dropna()
        assert v.between(0, 1).all()

    # ── 总量孪生 ft_vol_* (互为稳健性, 2026-06-13) ──
    def test_volume_twin_loo_counts(self, panel):
        # 总量 = ln(1 + LOO fintech 篇数) (分子, 不除分母):
        #   A: cell_ft − own_ft = 4 − 1 = 3 → ln(1+3)
        #   B: 4 − 0 = 4               → ln(1+4)
        assert panel.loc['A', 'ft_vol_prov'] == pytest.approx(np.log1p(3))
        assert panel.loc['B', 'ft_vol_prov'] == pytest.approx(np.log1p(4))

    def test_volume_twin_same_nan_sample_as_ratio(self, panel):
        # 互为稳健性前提: 总量与比值共享 min_articles 守卫 → 同非缺样本
        assert pd.isna(panel.loc['C', 'ft_vol_prov'])  # 同比值 C → NaN
        ratio_na = panel['ft_attn_prov'].isna()
        vol_na = panel['ft_vol_prov'].isna()
        assert (ratio_na == vol_na).all(), '总量与比值的 NaN 模式必须一致 (同样本)'

    def test_volume_twin_nonnegative(self, panel):
        # ln(1+篇数) 结构性 ≥0 (extensive 规模, 非 [0,1] share)
        v = panel['ft_vol_prov'].dropna()
        assert (v >= 0).all()

    def test_ratio_only_backward_compatible(self):
        # vol_col 默认 None → 仅产比值, 不产 ft_vol_* (历史调用零行为变更)
        df_all = pd.DataFrame({
            'docid': ['d1', 'd2', 'd3', 'd4', 'd5'],
            'target_bank': ['A', 'A', 'B', 'B', 'B'],
            'is_fintech_news': [True, False, True, False, False],
            'year': 2020, self.GEO: 'G1',
        })
        idx = am._build_geo_index(df_all.drop_duplicates('docid'), self.GEO,
                                  'ft_attn_prov', min_articles=5)
        panel = pd.DataFrame({'target_bank': ['A', 'B'], 'year': [2020, 2020]})
        out = am._merge_geo_index_to_panel(
            df_all, panel,
            idx[[self.GEO, 'year', '_total', '_ft', 'ft_attn_prov']],
            self.GEO, 'ft_attn_prov')
        assert 'ft_attn_prov' in out.columns
        assert 'ft_vol_prov' not in out.columns

    # ── toptier-audit D3-3 / D6-3: 年档 + 市档 + clip 守卫覆盖 ──
    def test_city_tier_and_clip_guard_negative_loo_to_zero(self):
        """市档 vol_col='ft_vol_city' 接线 + clip 守卫: 违反 'docid 内 geo 恒定' 不变量
        (同 docid 跨 geo + 多 bank) → own_ft>cell_ft → _loo_num<0; clip(lower=0) 须令
        ft_vol→0 (非 ln1p(负)=NaN)、ft_attn→0 (非负值逃过 [0,1] 校验)。"""
        GEO = '城市'
        # 2 个 fintech 幽灵 docid 首现于 G2 (df_unique 归 G2), bank A 在 G1 也引用之
        rows = [
            {'docid': 'X1', 'target_bank': 'Z', GEO: 'G2', 'is_fintech_news': True},
            {'docid': 'X2', 'target_bank': 'Z', GEO: 'G2', 'is_fintech_news': True},
            {'docid': 'X1', 'target_bank': 'A', GEO: 'G1', 'is_fintech_news': True},
            {'docid': 'X2', 'target_bank': 'A', GEO: 'G1', 'is_fintech_news': True},
        ]
        # G1 cell: 8 篇非 fintech (bank B) → cell_ft=0, cell_total=8
        rows += [{'docid': f'g{i}', 'target_bank': 'B', GEO: 'G1',
                  'is_fintech_news': False} for i in range(8)]
        df_all = pd.DataFrame(rows)
        df_all['year'] = 2020
        df_unique = df_all.drop_duplicates('docid')
        idx = am._build_geo_index(df_unique, GEO, 'ft_attn_city', min_articles=5)
        panel = pd.DataFrame({'target_bank': ['A'], 'year': [2020]})
        out = am._merge_geo_index_to_panel(
            df_all, panel,
            idx[[GEO, 'year', '_total', '_ft', 'ft_attn_city']],
            GEO, 'ft_attn_city', vol_col='ft_vol_city').set_index('target_bank')
        # A: _loo_den = cell_total(8) − own_total(2) = 6 ≥ 5 (过门, 非 NaN);
        #    _loo_num = cell_ft(0) − own_ft(2) = −2 → clip(0) → 两列均 0
        assert 'ft_vol_city' in out.columns                 # 市档接线
        assert not pd.isna(out.loc['A', 'ft_vol_city'])     # 非 NaN (clip 而非 ln1p(负))
        assert out.loc['A', 'ft_vol_city'] == pytest.approx(0.0)
        assert out.loc['A', 'ft_attn_city'] == pytest.approx(0.0)   # 非负值
        assert out.loc['A', 'ft_attn_city'] >= 0

    def test_year_tier_volume_and_orchestrator(self, tmp_path, monkeypatch):
        """年档 ft_vol_yr = ln1p(当年 fintech 唯一篇数), year-constant、无 LOO; 同时端到端
        锁 compute_fintech_attention_index orchestrator (此前仅 smoke 不验行为)。"""
        GP, GC = '国家地区/省份', '城市'
        rows = [{'docid': d, 'target_bank': 'A', '日期': '2020-01-01',
                 'is_fintech_news': ft, GP: 'P1', GC: 'C1'}
                for d, ft in [('d1', True), ('d2', True), ('d3', True),
                              ('d4', False), ('d5', False), ('d6', False)]]
        pd.DataFrame(rows).to_parquet(tmp_path / '12_fintech_news_full.parquet')
        monkeypatch.setattr(am, 'OUTPUT_DIR', str(tmp_path))
        monkeypatch.setattr(am, 'FILENAMES',
                            {'output_12_fintech_full': '12_fintech_news_full.parquet'})
        monkeypatch.setattr(am, '_save_attn_index', lambda *a, **k: None)
        panel = pd.DataFrame({'target_bank': ['A', 'B'], 'year': [2020, 2020]})
        out = am.compute_fintech_attention_index(panel)
        assert 'ft_vol_yr' in out.columns
        v = out['ft_vol_yr'].dropna()
        assert v.nunique() == 1                              # year-constant (无 LOO)
        assert v.iloc[0] == pytest.approx(np.log1p(3))       # 3 fintech 唯一篇 → ln1p(3)


# ============================================================================
# g-attention-06: attention_disp_full = 集中度 HHI (披露锁 + 方向功能锁)
# ============================================================================

class TestDispConcentrationSemantics:

    def test_single_outlet_hhi_is_one(self, tmp_path, monkeypatch):
        # 功能锁: 单 outlet bank-year → HHI = 1.0 = 最大集中 (非最大分散)
        panel = _write_attention_env(tmp_path, monkeypatch)
        out = (am.compute_attention_treatments(panel)
               .set_index('target_bank'))
        assert out.loc['A', 'attention_disp_full'] == pytest.approx(1.0)
        assert out.loc['A', 'n_outlets'] == 1

    def test_docstring_and_spec_disclose_concentration(self):
        # 披露锁: docstring 与 paper spec 必须标注集中度方向, 防按 "dispersion"
        # 反向解读符号 (codebook/export 标签同步属 g-codebook/Wave-1 范围)
        doc = am.compute_attention_treatments.__doc__
        assert '集中度' in doc and '高值=集中' in doc
        assert 'fix(omni-g-attention-06' in _SPEC
        assert '勿按 dispersion 反向解读符号' in _SPEC


# ============================================================================
# g-attention-07: homeprov/homecity 缺失 → NaN 出域
# ============================================================================

def _write_geo_hetero_env(tmp_path, monkeypatch):
    _write_media_cls(tmp_path, monkeypatch)
    addr = {
        'B1': {'province': '北京', 'city': '北京市'},
        'B2': {'province': '', 'city': ''},          # 总部地理缺失
        'B3': {'province': '浙江省', 'city': '杭州市'},
    }
    (tmp_path / 'bank_addresses.json').write_text(
        json.dumps(addr, ensure_ascii=False), encoding='utf-8')


class TestHomeGeoMissingIsOutOfDomain:

    @pytest.fixture()
    def out(self, tmp_path, monkeypatch):
        _write_geo_hetero_env(tmp_path, monkeypatch)
        df = pd.DataFrame({
            '媒体(中文)': ['m1', 'm2', 'm3', 'm4', 'm5'],
            'target_bank': ['B1', 'B1', 'B1', 'B2', 'B3'],
            'year': [2023] * 5,
            # B1: 本地(北京) / 异地(上海) / 地理缺失;  B2: 总部缺失;
            # B3: 省字段缺失但城市命中 (拓扑提升 city=1 ⇒ prov=1)
            '国家地区/省份': ['北京', '上海', np.nan, '北京', np.nan],
            '城市': ['北京', '上海', np.nan, '北京', '杭州'],
            'llm_vote_score_full': [1.0, -1.0, 0.0, 0.5, 0.2],
            'llm_vote_score_ctx': [1.0, -1.0, 0.0, 0.5, 0.2],
        })
        panel = pd.DataFrame({'target_bank': ['B1', 'B2', 'B3'],
                              'year': [2023] * 3})
        return (am.compute_media_heterogeneity(df, panel)
                .set_index('target_bank'))

    def test_frac_denominator_excludes_unknown(self, out):
        # B1: 可判定 2 篇 (本地 1 / 异地 1), 缺失 1 篇出域 → frac = 1/2
        # (旧编码缺失→0 计入分母 → 1/3 低估)
        assert out.loc['B1', 'homeprov_media_frac'] == pytest.approx(0.5)
        assert out.loc['B1', 'homecity_media_frac'] == pytest.approx(0.5)

    def test_away_group_excludes_unknown(self, out):
        # away 组只含确认异地 m2 (tone −1.0); 旧编码混入 m3 → mean(−1, 0) = −0.5
        assert out.loc['B1', 'tone_nonprov_media_full'] == pytest.approx(-1.0)
        assert out.loc['B1', 'tone_gap_homeprov_nonprov_full'] == pytest.approx(2.0)

    def test_bank_hq_missing_gives_nan_not_zero(self, out):
        # B2 总部省/市缺失 → 整行不可判 → frac NaN (旧编码伪零 0.0)
        assert pd.isna(out.loc['B2', 'homeprov_media_frac'])
        assert pd.isna(out.loc['B2', 'homecity_media_frac'])

    def test_city_match_still_promotes_province(self, out):
        # 拓扑不变量保留: B3 省字段缺失但同城命中 → homeprov 提升为 1 (非 NaN)
        assert out.loc['B3', 'homecity_media_frac'] == pytest.approx(1.0)
        assert out.loc['B3', 'homeprov_media_frac'] == pytest.approx(1.0)

    def test_source_no_zero_coercion(self):
        # 源码级: 缺失→0 强制编码不得复活
        assert "df.loc[_prov_invalid, '_is_homeprov'] = 0" not in SRC
        assert "df.loc[_prov_invalid, '_is_homeprov'] = np.nan" in SRC
        assert "df.loc[_city_invalid, '_is_homecity'] = np.nan" in SRC


# ============================================================================
# 组级裁决 (zerofill): n_articles_exc 计数零填契约补齐
# ============================================================================

class TestCountZeroFillContract:

    @pytest.fixture()
    def out(self, tmp_path, monkeypatch):
        _write_media_cls(tmp_path, monkeypatch)
        df = pd.DataFrame({
            '媒体(中文)': ['m1', 'm2'],
            'target_bank': ['B1', 'B1'],
            'year': [2023] * 2,
            'llm_vote_score_full': [1.0, -1.0],
            'llm_vote_score_ctx': [1.0, -1.0],
        })
        # panel 含 balance_panel 笛卡尔积产生的零文章行 (B9, 2023)
        panel = pd.DataFrame({'target_bank': ['B1', 'B9'],
                              'year': [2023] * 2})
        return (am.compute_media_heterogeneity(df, panel)
                .set_index('target_bank'))

    def test_zero_article_bank_year_count_is_zero(self, out):
        # 本模块在 balance_panel ("计数/和类填 0", n_articles* 前缀通配) 之后
        # merge → 零文章 bank-year 的 n_articles_exc 旧残留 NaN (.dta 显 . 而非
        # 0, 与兄弟列 n_articles=0 矛盾)。Σ over ∅ = 0。
        assert out.loc['B9', 'n_articles_exc'] == 0
        assert out.loc['B1', 'n_articles_exc'] == 2
        assert out['n_articles_exc'].dtype.kind == 'i', '计数列须恢复整型'

    def test_ratio_and_tone_cols_stay_nan(self, out):
        # 防过度零填: 比例类 (ceased_media_frac) / 情感类 (exc_tone_*) 在零文章
        # bank-year 按契约保持 NaN (不可测), 不得连带填 0
        assert pd.isna(out.loc['B9', 'ceased_media_frac'])
        assert pd.isna(out.loc['B9', 'exc_tone_full'])


# ============================================================================
# fix(2026-06-20): 六部情感词典 ↔ _SCORE_PATTERNS 对称锁
#   _SCORE_PATTERNS 驱动 exc_*(停刊稳健性) 与 bal_*(平衡媒体) 两族的动态发现。
#   第 6 部 loughran (L&M 2011 JF 中文主译) 新增时漏列, 致 exc_loughran_* 缺 12 列、
#   与其余 5 部不对称 (loughran 99 列 vs jiang/yao/bian/du/you 各 111 列)。
#   本锁防回归: 凡 encode.DICT_NAMES 中的词典都须在 _SCORE_PATTERNS 有对应
#   '{dict}_score_' 前缀 (再加第 7 部时若漏列, 此处即红)。
# ============================================================================

def test_all_sentiment_dicts_have_score_pattern():
    """encode.DICT_NAMES ⊆ {p 去掉 '_score_' 后缀 | p ∈ _SCORE_PATTERNS}。"""
    from news_process.pipeline.panel.encode import DICT_NAMES

    pattern_dicts = {p[:-len('_score_')] for p in am._SCORE_PATTERNS
                     if p.endswith('_score_')}
    missing = [d for d in DICT_NAMES if d not in pattern_dicts]
    assert not missing, (
        f"词典 {missing} 在 encode.DICT_NAMES 但 _SCORE_PATTERNS 无 '{{d}}_score_' "
        f"前缀 → exc_*/bal_* 稳健性两族缺该词典列, 与其余词典不对称 "
        f"(见 attention_media.py::_SCORE_PATTERNS fix 2026-06-20)")


def test_loughran_score_pattern_present():
    """具体锁: 第 6 部 loughran 前缀就位 (回归此次 fix 的根因)。"""
    assert 'loughran_score_' in am._SCORE_PATTERNS


# ============================================================================
# F4 (2026-07-16, FATAL_DEFECT_REMEDIATION §2-F4): ATT-2 后文章级 fintech 身份
# = 任一对级 verified (any, 行序无关); 哨兵双成因分诊
# ============================================================================

class TestF4AnyPairVerifiedIdentity:
    GP, GC = '国家地区/省份', '城市'

    def _rows(self, order_a_first=True):
        # 文章 X: 银行 A 对级判伪 / 银行 B 对级 verified (分裂验证, 对级判伪率场景)
        x_rows = [
            {'docid': 'X', 'target_bank': 'A', '日期': '2020-01-01',
             'is_fintech_news': True, self.GP: 'P1', self.GC: 'C1'},
            {'docid': 'X', 'target_bank': 'B', '日期': '2020-01-01',
             'is_fintech_news': True, self.GP: 'P1', self.GC: 'C1'},
        ]
        if not order_a_first:
            x_rows = x_rows[::-1]
        rows = x_rows + [
            {'docid': 'Y', 'target_bank': 'B', '日期': '2020-01-01',
             'is_fintech_news': True, self.GP: 'P1', self.GC: 'C1'},
        ] + [
            {'docid': f'n{i}', 'target_bank': 'A', '日期': '2020-01-01',
             'is_fintech_news': False, self.GP: 'P1', self.GC: 'C1'}
            for i in range(3)
        ]
        return pd.DataFrame(rows)

    def _run(self, tmp_path, monkeypatch, order_a_first, verified_pairs):
        df = self._rows(order_a_first)
        df.to_parquet(tmp_path / '12_fintech_news_full.parquet')
        monkeypatch.setattr(am, 'OUTPUT_DIR', str(tmp_path))
        monkeypatch.setattr(am, 'FILENAMES',
                            {'output_12_fintech_full': '12_fintech_news_full.parquet'})
        monkeypatch.setattr(am, '_save_attn_index', lambda *a, **k: None)

        def _fake_verified(sub, *a, **k):   # 模拟 ATT-2 对级 verified 域
            mask = sub.apply(
                lambda r: (r['docid'], r['target_bank']) in verified_pairs, axis=1)
            return sub[mask]

        monkeypatch.setattr(am, 'restrict_to_verified', _fake_verified)
        panel = pd.DataFrame({'target_bank': ['A', 'B'], 'year': [2020, 2020]})
        return am.compute_fintech_attention_index(panel)

    def test_t1_order_invariant_and_any_counted(self, tmp_path, monkeypatch, caplog):
        """分裂验证文章 X (A 伪/B 真): 两种行序输出逐位相同且 X 计入年 _ft (any);
        旧 keep='first' 语义下 A 行在前时 X 被误剔 (行序驱动测量)。"""
        verified = {('X', 'B'), ('Y', 'B')}
        out1 = self._run(tmp_path, monkeypatch, True, verified)
        out2 = self._run(tmp_path, monkeypatch, False, verified)
        pd.testing.assert_frame_equal(
            out1.sort_values('target_bank').reset_index(drop=True),
            out2.sort_values('target_bank').reset_index(drop=True))
        v = out1['ft_vol_yr'].dropna()
        assert v.iloc[0] == pytest.approx(np.log1p(2)), 'X(any=True) + Y = 2 篇'
        # T2: ATT-2 分裂场景下 own_ft <= cell_ft 恒成立 → 哨兵不触发
        # (跨 geo 幽灵是另一独立成因, 由既有 clip 用例覆盖, 与本断言不冲突)
        assert not any('LOO 不变量哨兵' in r.message for r in caplog.records)

    def test_t3_all_pairs_refused_excluded(self, tmp_path, monkeypatch):
        """X 两对级全判伪 → any=False → 不计入年 _ft。"""
        out = self._run(tmp_path, monkeypatch, True, {('Y', 'B')})
        v = out['ft_vol_yr'].dropna()
        assert v.iloc[0] == pytest.approx(np.log1p(1)), '仅 Y 计入'

    def test_t4_fail_open_any_equals_first(self, tmp_path, monkeypatch):
        """fail-open (restrict_to_verified 原样返回, 不重标) → is_fintech_news 保持
        文章级常量 → any() ≡ first, 行为零变化。"""
        df = self._rows(True)
        df.to_parquet(tmp_path / '12_fintech_news_full.parquet')
        monkeypatch.setattr(am, 'OUTPUT_DIR', str(tmp_path))
        monkeypatch.setattr(am, 'FILENAMES',
                            {'output_12_fintech_full': '12_fintech_news_full.parquet'})
        monkeypatch.setattr(am, '_save_attn_index', lambda *a, **k: None)
        monkeypatch.setattr(am, 'restrict_to_verified', lambda sub, *a, **k: sub)
        panel = pd.DataFrame({'target_bank': ['A', 'B'], 'year': [2020, 2020]})
        out = am.compute_fintech_attention_index(panel)
        v = out['ft_vol_yr'].dropna()
        assert v.iloc[0] == pytest.approx(np.log1p(2)), 'X + Y 全保留 (X 文章级 True)'
