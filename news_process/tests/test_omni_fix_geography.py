"""test_omni_fix_geography.py — OMNI 审计 g-geography 组修复回归锁
=================================================================

锁定 2026-06-11 OMNI 审计 (scripts/audit/_omni_fix/g-geography.json) 六条
确认缺陷的修复后行为, 防静默 revert:

  - g-geography-01: prox 双轨情感格 Int8 全-NA 圈 mean→pd.NA → object dtype
                    (修复: astype('float64') 归一, 全-NA 圈得 np.nan)
  - g-geography-02: n_geocoded==0 时 is_local/n_media/n_articles 与 frac
                    的 NaN 语义对齐 (域未知, 非"确知为 0")
  - g-geography-03: (a) merge_bank_geography 回退路径改包根 config/
                    (b) capital/bank_addr 路径 None 短路守卫
                    (c) Stata '' 聚类"安全忽略"误述勘误 (源码级断言)
  - g-geography-04: 省会回退插补诊断列 prox_geo_imputed_frac
  - g-geography-05: Manski/Bramoullé "文献支撑"倒置→识别威胁披露 + 28→40
                    计数勘误 (源码级断言)
  - g-geography-06: bert_avg_pos/neg 全族仅在三分类模型上平均 (与 neu 同域,
                    finbert2 二分类不混入), pos+neu+neg≈1 恒等式成立

全部用合成 DataFrame + tmp_path 临时 JSON, 不依赖盘上大数据, 不调外部 API。

# 白话: 这组测试管"媒体离银行多远"那套地理指标: 一篇文章都定位不了时,
# 各项指标该记"不知道"(NaN)而不是"确定是 0"; 用省会坐标凑数的比例要单独
# 披露一列; 配置文件找不到时要回退到正确目录而不是悄悄全部留空; BERT 综合
# 情感分只在三分类模型间平均, 不能把二分类模型混进来导致"正面+中性+负面"
# 加起来超过 1。
"""

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from news_process.pipeline.panel import geography as geo

pytestmark = pytest.mark.fast

SRC = Path(geo.__file__).read_text(encoding='utf-8')


# ============================================================================
# 共享 fixtures: 临时地理配置 (城市坐标 / 省会映射 / 银行地址)
# ============================================================================

@pytest.fixture()
def geo_config_files(tmp_path):
    """生成最小可用的三个地理 JSON, 返回路径 dict。"""
    city_coords = {
        '北京市': {'lat': 39.9042, 'lon': 116.4074},
        '上海市': {'lat': 31.2304, 'lon': 121.4737},
        '石家庄市': {'lat': 38.0428, 'lon': 114.5149},
    }
    capital_map = {'河北': '石家庄', '北京': '北京', '上海': '上海'}
    bank_addr = {
        '测试银行': {'province': '北京', 'city': '北京市',
                     'district': '', 'address': ''},
    }
    paths = {}
    for name, payload in [('city_coordinates.json', city_coords),
                          ('province_capital_map.json', capital_map),
                          ('bank_addresses.json', bank_addr)]:
        p = tmp_path / name
        p.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
        paths[name] = str(p)
    return paths


@pytest.fixture()
def patched_geo_paths(geo_config_files, monkeypatch):
    """把 geography.CONFIG['paths'] 三键指向临时 JSON。"""
    monkeypatch.setitem(geo.CONFIG['paths'], 'city_coordinates_file',
                        geo_config_files['city_coordinates.json'])
    monkeypatch.setitem(geo.CONFIG['paths'], 'province_capital_map_file',
                        geo_config_files['province_capital_map.json'])
    monkeypatch.setitem(geo.CONFIG['paths'], 'bank_addresses_file',
                        geo_config_files['bank_addresses.json'])
    return geo_config_files


def _make_panel(banks_years):
    return pd.DataFrame(
        [{'target_bank': b, 'year': y} for b, y in banks_years])


# ============================================================================
# g-geography-06: bert_avg_pos/neg 仅三分类聚合域
# ============================================================================

class TestBertAvgThreeClassDomain:
    """bert_avg_{pos,neg,neu} 全族同聚合域 = THREE_CLASS_MODELS。"""

    @pytest.fixture()
    def composite_panel(self):
        # 三分类: finbert_cn (.6/.3/.1), fin_sent_zh (.5/.25/.25);
        # 二分类: finbert2 (pos+neg≡1, pos=.9) — 修复后不得混入 bert_avg_*
        n = 2
        data = {
            'target_bank': ['A行', 'B行'], 'year': [2017, 2017],
            'n_articles': [5, 3],
            # hanzi-char-dual: 汉字口径文章长度聚合源 (geography → ln_han_count)
            'avg_han_count_full': [800.0, 600.0], 'avg_han_count_ctx': [400.0, 300.0],
            'finbert_cn_pos_full': [0.6] * n, 'finbert_cn_neg_full': [0.1] * n,
            'finbert_cn_neu_full': [0.3] * n,
            'fin_sent_zh_pos_full': [0.5] * n, 'fin_sent_zh_neg_full': [0.25] * n,
            'fin_sent_zh_neu_full': [0.25] * n,
            'finbert2_pos_full': [0.9] * n, 'finbert2_neg_full': [0.1] * n,
            # _sum / _std 族
            'finbert_cn_pos_sum_full': [3.0] * n, 'fin_sent_zh_pos_sum_full': [2.5] * n,
            'finbert2_pos_sum_full': [4.5] * n,
            'finbert_cn_neg_sum_full': [0.5] * n, 'fin_sent_zh_neg_sum_full': [1.25] * n,
            'finbert2_neg_sum_full': [0.5] * n,
            'finbert_cn_neu_sum_full': [1.5] * n, 'fin_sent_zh_neu_sum_full': [1.25] * n,
            'finbert_cn_pos_std_full': [0.10] * n, 'fin_sent_zh_pos_std_full': [0.20] * n,
            'finbert2_pos_std_full': [0.90] * n,
            # 加权族 (_vw/_mw/_hw)
            'finbert_cn_pos_vw_full': [0.62] * n, 'fin_sent_zh_pos_vw_full': [0.52] * n,
            'finbert2_pos_vw_full': [0.92] * n,
            'finbert_cn_neg_vw_full': [0.12] * n, 'fin_sent_zh_neg_vw_full': [0.22] * n,
            'finbert2_neg_vw_full': [0.08] * n,
            'finbert_cn_pos_mw_full': [0.64] * n, 'fin_sent_zh_pos_mw_full': [0.54] * n,
            'finbert2_pos_mw_full': [0.94] * n,
            'finbert_cn_neg_mw_full': [0.14] * n, 'fin_sent_zh_neg_mw_full': [0.24] * n,
            'finbert2_neg_mw_full': [0.06] * n,
            'finbert_cn_pos_hw_full': [0.66] * n, 'fin_sent_zh_pos_hw_full': [0.56] * n,
            'finbert2_pos_hw_full': [0.96] * n,
            'finbert_cn_neg_hw_full': [0.16] * n, 'fin_sent_zh_neg_hw_full': [0.26] * n,
            'finbert2_neg_hw_full': [0.04] * n,
            # 分类维度 (_tech)
            'n_articles_tech': [2, 1],
            'finbert_cn_pos_tech_full': [0.7] * n, 'fin_sent_zh_pos_tech_full': [0.3] * n,
            'finbert2_pos_tech_full': [0.99] * n,
            'finbert_cn_neg_tech_full': [0.2] * n, 'fin_sent_zh_neg_tech_full': [0.4] * n,
            'finbert2_neg_tech_full': [0.01] * n,
            'finbert_cn_neu_tech_full': [0.1] * n, 'fin_sent_zh_neu_tech_full': [0.3] * n,
        }
        panel = pd.DataFrame(data)
        return geo.compute_composite_indicators(panel)

    def test_pos_excludes_binary_finbert2(self, composite_panel):
        # 旧 (混入 finbert2): (.6+.5+.9)/3 = .6667; 新: (.6+.5)/2 = .55
        assert composite_panel['bert_avg_pos_full'].iloc[0] == pytest.approx(0.55)

    def test_ln_han_count_from_avg_han_count(self, composite_panel):
        # hanzi-char-dual: 汉字口径文章长度 ln_han_count = log1p(avg_han_count), 双轨
        assert 'ln_han_count_full' in composite_panel.columns
        assert 'ln_han_count_ctx' in composite_panel.columns
        assert composite_panel['ln_han_count_full'].iloc[0] == pytest.approx(np.log1p(800.0))
        assert composite_panel['ln_han_count_ctx'].iloc[0] == pytest.approx(np.log1p(400.0))

    def test_neg_excludes_binary_finbert2(self, composite_panel):
        assert composite_panel['bert_avg_neg_full'].iloc[0] == pytest.approx(0.175)

    def test_simplex_identity_holds(self, composite_panel):
        # 修复核心验收: pos+neu+neg ≈ 1 (旧行为 max 达 1.33)
        total = (composite_panel['bert_avg_pos_full']
                 + composite_panel['bert_avg_neu_full']
                 + composite_panel['bert_avg_neg_full'])
        assert np.allclose(total, 1.0, atol=1e-9)

    def test_sum_and_std_families_three_class_only(self, composite_panel):
        assert composite_panel['bert_avg_pos_sum_full'].iloc[0] == pytest.approx(2.75)
        assert composite_panel['bert_avg_neg_sum_full'].iloc[0] == pytest.approx(0.875)
        assert composite_panel['bert_avg_pos_std_full'].iloc[0] == pytest.approx(0.15)

    def test_weighted_families_three_class_only(self, composite_panel):
        assert composite_panel['bert_avg_pos_vw_full'].iloc[0] == pytest.approx(0.57)
        assert composite_panel['bert_avg_neg_vw_full'].iloc[0] == pytest.approx(0.17)
        assert composite_panel['bert_avg_pos_mw_full'].iloc[0] == pytest.approx(0.59)
        assert composite_panel['bert_avg_neg_mw_full'].iloc[0] == pytest.approx(0.19)
        assert composite_panel['bert_avg_pos_hw_full'].iloc[0] == pytest.approx(0.61)
        assert composite_panel['bert_avg_neg_hw_full'].iloc[0] == pytest.approx(0.21)

    def test_classification_suffix_three_class_only(self, composite_panel):
        assert composite_panel['bert_avg_pos_tech_full'].iloc[0] == pytest.approx(0.5)
        assert composite_panel['bert_avg_neg_tech_full'].iloc[0] == pytest.approx(0.3)
        assert composite_panel['bert_avg_neu_tech_full'].iloc[0] == pytest.approx(0.2)

    def test_finbert2_per_model_columns_preserved(self, composite_panel):
        # 二分类稳健轨: finbert2 逐模型列原样保留, 不被综合指标覆盖
        assert composite_panel['finbert2_pos_full'].iloc[0] == pytest.approx(0.9)
        assert composite_panel['finbert2_neg_full'].iloc[0] == pytest.approx(0.1)


# ============================================================================
# g-geography-01 / 02 / 04: compute_geo_proximity_buffers
# ============================================================================

def _exploded(rows):
    """构造篇章级 df_exploded (含双轨 Int8 情感列)。"""
    df = pd.DataFrame(rows)
    for track in ('_full', '_ctx'):
        for col in (f'llm_vote_score{track}', f'is_positive{track}',
                    f'is_negative{track}'):
            df[col] = df[col].astype('Int8')
    return df


class TestProxAllNaTrackDtype:
    """g-geography-01: 全-NA 圈内均值须为 np.nan (float64), 非 pd.NA (object)。"""

    def test_all_na_ctx_track_yields_float64_nan(self, patched_geo_paths):
        rows = [
            # 两篇北京媒体文章, 距银行 0 km (必在 50km 圈内);
            # full 轨有值 (+1/-1), ctx 轨全 NA (实体窗缺失场景)
            {'target_bank': '测试银行', 'year': 2017, '城市': '北京市',
             '国家地区/省份': '北京', '媒体(中文)': '媒体A',
             'llm_vote_score_full': 1, 'is_positive_full': 1,
             'is_negative_full': 0, 'llm_vote_score_ctx': pd.NA,
             'is_positive_ctx': pd.NA, 'is_negative_ctx': pd.NA},
            {'target_bank': '测试银行', 'year': 2017, '城市': '北京市',
             '国家地区/省份': '北京', '媒体(中文)': '媒体B',
             'llm_vote_score_full': -1, 'is_positive_full': 0,
             'is_negative_full': 1, 'llm_vote_score_ctx': pd.NA,
             'is_positive_ctx': pd.NA, 'is_negative_ctx': pd.NA},
        ]
        df_exploded = _exploded(rows)
        panel = _make_panel([('测试银行', 2017)])
        out = geo.compute_geo_proximity_buffers(df_exploded, panel)

        # ctx 轨全-NA → np.nan 且 dtype 必须是 float64 (修复前: object/pd.NA)
        for col in ['prox_50km_tone_ctx', 'prox_50km_pos_frac_ctx',
                    'prox_50km_neg_frac_ctx']:
            assert out[col].dtype == np.float64, f"{col} dtype={out[col].dtype}"
            assert out[col].isna().all()
            # 修复前回归路径: 单元格是 pd.NA 而非 np.nan
            assert out[col].iloc[0] is not pd.NA

        # full 轨正常聚合不受影响
        assert out['prox_50km_tone_full'].iloc[0] == pytest.approx(0.0)
        assert out['prox_50km_pos_frac'].iloc[0] == pytest.approx(0.5)
        assert out['prox_50km_neg_frac'].iloc[0] == pytest.approx(0.5)


class TestProxUngeocodableSiblingNaN:
    """g-geography-02: n_geocoded==0 时 is_local/n_media/n_articles 与 frac 同 NaN。"""

    def test_all_siblings_nan_when_no_geocode(self, patched_geo_paths):
        rows = [
            # 媒体城市/省份均无法解析 → n_geocoded = 0 (域未知)
            {'target_bank': '测试银行', 'year': 2017, '城市': '未知城',
             '国家地区/省份': '火星省', '媒体(中文)': '媒体X',
             'llm_vote_score_full': 1, 'is_positive_full': 1,
             'is_negative_full': 0, 'llm_vote_score_ctx': 1,
             'is_positive_ctx': 1, 'is_negative_ctx': 0},
        ]
        df_exploded = _exploded(rows)
        panel = _make_panel([('测试银行', 2017)])
        out = geo.compute_geo_proximity_buffers(df_exploded, panel)

        for threshold in (50, 100, 150, 200):
            prefix = f'prox_{threshold}km'
            for suffix in ('_frac', '_is_local', '_n_media', '_n_articles'):
                col = f'{prefix}{suffix}'
                assert out[col].isna().all(), (
                    f"{col} 应为 NaN (域未知), 实际 {out[col].iloc[0]!r}")
        # 插补占比同样未知
        assert out['prox_geo_imputed_frac'].isna().all()

    def test_geocoded_cell_keeps_zero_one_semantics(self, patched_geo_paths):
        # 对照组: 可定位但圈外 (上海媒体 vs 北京银行 ≈ 1068 km)
        rows = [
            {'target_bank': '测试银行', 'year': 2017, '城市': '上海市',
             '国家地区/省份': '上海', '媒体(中文)': '媒体Y',
             'llm_vote_score_full': 1, 'is_positive_full': 1,
             'is_negative_full': 0, 'llm_vote_score_ctx': 1,
             'is_positive_ctx': 1, 'is_negative_ctx': 0},
        ]
        df_exploded = _exploded(rows)
        panel = _make_panel([('测试银行', 2017)])
        out = geo.compute_geo_proximity_buffers(df_exploded, panel)
        # 可定位 → "确知圈内为 0" 的 0/0.0 语义保留
        assert out['prox_50km_is_local'].iloc[0] == 0
        assert out['prox_50km_n_articles'].iloc[0] == 0
        assert out['prox_50km_frac'].iloc[0] == pytest.approx(0.0)
        assert out['prox_50km_n_media'].iloc[0] == 0


class TestCapitalImputationDisclosure:
    """g-geography-04: 省会回退插补占比诊断列 prox_geo_imputed_frac。"""

    def test_imputed_frac_half(self, patched_geo_paths):
        rows = [
            # 文章 A: 城市精确解析 (Level 1)
            {'target_bank': '测试银行', 'year': 2017, '城市': '北京市',
             '国家地区/省份': '北京', '媒体(中文)': '媒体A',
             'llm_vote_score_full': 1, 'is_positive_full': 1,
             'is_negative_full': 0, 'llm_vote_score_ctx': 1,
             'is_positive_ctx': 1, 'is_negative_ctx': 0},
            # 文章 B: 城市不可解析, 省份"河北省"→ 省会石家庄 (Level 3 插补)
            {'target_bank': '测试银行', 'year': 2017, '城市': '保定县城',
             '国家地区/省份': '河北省', '媒体(中文)': '媒体B',
             'llm_vote_score_full': -1, 'is_positive_full': 0,
             'is_negative_full': 1, 'llm_vote_score_ctx': -1,
             'is_positive_ctx': 0, 'is_negative_ctx': 1},
        ]
        df_exploded = _exploded(rows)
        panel = _make_panel([('测试银行', 2017)])
        out = geo.compute_geo_proximity_buffers(df_exploded, panel)
        assert out['prox_geo_imputed_frac'].iloc[0] == pytest.approx(0.5)

    def test_imputed_frac_zero_when_all_exact(self, patched_geo_paths):
        rows = [
            {'target_bank': '测试银行', 'year': 2017, '城市': '上海市',
             '国家地区/省份': '上海', '媒体(中文)': '媒体C',
             'llm_vote_score_full': 1, 'is_positive_full': 1,
             'is_negative_full': 0, 'llm_vote_score_ctx': 1,
             'is_positive_ctx': 1, 'is_negative_ctx': 0},
        ]
        df_exploded = _exploded(rows)
        panel = _make_panel([('测试银行', 2017)])
        out = geo.compute_geo_proximity_buffers(df_exploded, panel)
        assert out['prox_geo_imputed_frac'].iloc[0] == pytest.approx(0.0)


# ============================================================================
# g-geography-03: 回退路径 / None 守卫 / Stata '' 注释勘误
# ============================================================================

class TestMergeBankGeographyFallbackPath:
    """g-geography-03a: 未配置 bank_addresses_file 时回退到包根 config/。"""

    def test_fallback_resolves_to_package_root_config(self, monkeypatch):
        # 删除配置键 → 触发回退路径; 修复前回退到 pipeline/panel/config/
        # (不存在) → 全列静默置 ''; 修复后回退到 <pkg>/config/ (存在)。
        monkeypatch.delitem(geo.CONFIG['paths'], 'bank_addresses_file',
                            raising=False)
        pkg_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(geo.__file__))))
        addr_file = os.path.join(pkg_root, 'config', 'bank_addresses.json')
        assert os.path.exists(addr_file), "包根 config/bank_addresses.json 应存在"

        with open(addr_file, 'r', encoding='utf-8') as f:
            addr_data = json.load(f)
        real_bank = next(k for k, v in addr_data.items() if v.get('province'))

        panel = _make_panel([(real_bank, 2017)])
        out = geo.merge_bank_geography(panel)
        # 修复前 (假回退路径): bank_province 全 '' (文件不存在 → 跳过)
        assert out['bank_province'].iloc[0] != ''
        assert out['bank_province'].iloc[0] == addr_data[real_bank]['province']


class TestProximityBuffersNoneGuard:
    """g-geography-03b: capital/bank_addr 路径未配置 (None) 不得 TypeError。"""

    def test_none_paths_do_not_crash(self, geo_config_files, monkeypatch):
        monkeypatch.setitem(geo.CONFIG['paths'], 'city_coordinates_file',
                            geo_config_files['city_coordinates.json'])
        # 两键缺失 → CONFIG['paths'].get(...) 返回 None;
        # 修复前 os.path.exists(None) 抛 TypeError
        monkeypatch.delitem(geo.CONFIG['paths'], 'province_capital_map_file',
                            raising=False)
        monkeypatch.delitem(geo.CONFIG['paths'], 'bank_addresses_file',
                            raising=False)

        df_exploded = _exploded([
            {'target_bank': '测试银行', 'year': 2017, '城市': '北京市',
             '国家地区/省份': '北京', '媒体(中文)': '媒体A',
             'llm_vote_score_full': 1, 'is_positive_full': 1,
             'is_negative_full': 0, 'llm_vote_score_ctx': 1,
             'is_positive_ctx': 1, 'is_negative_ctx': 0},
        ])
        panel = _make_panel([('测试银行', 2017)])
        out = geo.compute_geo_proximity_buffers(df_exploded, panel)
        # 无银行地址 → 无法定位银行 → 不产 prox 列, 但绝不允许 TypeError
        assert len(out) == 1


class TestSourceLevelDisclosures:
    """g-geography-03c / 05: 源码级断言锁定注释/日志勘误 (防 revert)。"""

    def test_stata_empty_string_misstatement_removed(self):
        # 旧误述: "空字符串可被安全忽略" — Stata 中 '' 即字符串缺失,
        # vce(cluster) 会剔除观测 (样本静默缩小)
        assert '空字符串可被安全忽略' not in SRC
        assert '从估计样本中' in SRC and '剔除' in SRC

    def test_manski_bramoulle_reframed_as_threat(self):
        # 旧倒置: 反射问题文献被标为 "[文献支撑]"
        assert '文献支撑 1' not in SRC
        assert '文献支撑 2' not in SRC
        assert '识别威胁披露 1' in SRC
        assert '识别威胁披露 2' in SRC
        assert 'Manski' in SRC and 'reflection problem' in SRC

    def test_stale_28_count_corrected(self):
        # 模块头与 Returns 段的陈旧 "28 个" 计数 (full/ctx 化后 40, v3.9.0 三轨 ss → 52)
        assert '28 个媒体接近度指标' not in SRC
        assert '追加 28 个距离缓冲变量' not in SRC
        # v3.9.0 三轨: full/ctx 化 28→40, ss 情感三项各补 _ss 孪生 40→52
        assert '40→52' in SRC

    def test_imputation_column_disclosed_in_docstring(self):
        assert 'prox_geo_imputed_frac' in SRC
