"""tests/test_iv_did.py — V8 Wave 2 paper-critical math coverage.

iv_did.py 是主论文计量识别核心 (812 行实现 Bartik IV + DID + Rotemberg
诊断), 此前 0 测试覆盖. 本批先用合成 mini 数据 (3 银行 × 3 年, 5-8 文章)
覆盖纯数学函数, 不依赖 JSON 配置或大数据集:

  1. load_bank_group_maps          — JSON -> 2 dict 映射
  2. compute_bartik_iv             — 通用 Bartik (co-mention shares)
  3. compute_bartik_iv_fintech     — Bartik (article category col)
  4. compute_zone_leave1out        — 经济圈 LOO 均值
  5. diagnose_rotemberg_weights    — α_k = Cov(share, IV)/Var(IV)

排除 (留待后续):
  - merge_policy_shocks  — 需 policy_shocks.json + bank_city/province 配置,
                           复杂匹配规则 (城市/省/别名), 单独测试更合适

学术依据 (验证数学正确性):
  Goldsmith-Pinkham, Sorkin & Swift (2020, AER, DOI 10.1257/aer.20181047)
  Callaway & Sant'Anna (2021, JoE, DOI 10.1016/j.jeconom.2020.12.001)
  Rotemberg (1983) -- 权重分解
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

from news_process.pipeline.panel import iv_did  # noqa: E402

# ============================================================================
# 共享 fixtures: 3 银行 × 3 年的最小合成数据
# ============================================================================

@pytest.fixture
def mini_panel() -> pd.DataFrame:
    """3 银行 × 3 年 = 9 行的 bank-year panel."""
    banks = ['工行', '招行', '宁波银行']
    years = [2020, 2021, 2022]
    rows = []
    for b in banks:
        for y in years:
            rows.append({
                'target_bank': b,
                'year': y,
                'bank_province': {'工行': '北京', '招行': '广东', '宁波银行': '浙江'}[b],
                'bank_city': {'工行': '北京', '招行': '深圳', '宁波银行': '宁波'}[b],
            })
    return pd.DataFrame(rows)


@pytest.fixture
def mini_articles() -> pd.DataFrame:
    """文章级 df_exploded: 5 篇文章, 跨 3 年 3 银行, 含 co_mentioned + 评分.

    评分设计:
      llm_vote_score_full ∈ {-1, 0, 1} 代表负/中/正情感
      _full / _ctx 同值简化校验 (remove-title-track: _title 情感轨已删, iv_did 仅消费/产出 _full/_ctx)
    """
    rows = [
        # 工行: 基期 2020 提到招行
        {'docid': 1, 'target_bank': '工行', 'year': 2020,
         'co_mentioned_banks': '招行', 'llm_vote_score_full': 1.0,
         'llm_vote_score_ctx': 1.0,
         'innovation_locus': 'payment'},
        # 招行: 基期 2020 提到工行
        {'docid': 2, 'target_bank': '招行', 'year': 2020,
         'co_mentioned_banks': '工行', 'llm_vote_score_full': -1.0,
         'llm_vote_score_ctx': -1.0,
         'innovation_locus': 'payment'},
        # 宁波: 基期 2020 提到工行
        {'docid': 3, 'target_bank': '宁波银行', 'year': 2020,
         'co_mentioned_banks': '工行', 'llm_vote_score_full': 0.0,
         'llm_vote_score_ctx': 0.0,
         'innovation_locus': 'lending'},
        # 2021: 工行评分提升
        {'docid': 4, 'target_bank': '工行', 'year': 2021,
         'co_mentioned_banks': '', 'llm_vote_score_full': 1.0,
         'llm_vote_score_ctx': 1.0,
         'innovation_locus': 'payment'},
        # 2022: 招行评分下降
        {'docid': 5, 'target_bank': '招行', 'year': 2022,
         'co_mentioned_banks': '', 'llm_vote_score_full': -1.0,
         'llm_vote_score_ctx': -1.0,
         'innovation_locus': 'lending'},
    ]
    return pd.DataFrame(rows)


# ============================================================================
# 1. load_bank_group_maps
# ============================================================================

def test_load_bank_group_maps_returns_two_dicts(tmp_path, monkeypatch):
    """从 tmp JSON 读, 验证 type_map + scale_map 两个 dict 正确构建."""
    addr_path = tmp_path / "bank_addresses.json"
    addr_path.write_text(json.dumps({
        '工行':       {'nfra_type': '国有大型商业银行', 'enterprise_scale': 'L(大型)'},
        '招行':       {'nfra_type': '股份制商业银行',   'enterprise_scale': 'L(大型)'},
        '宁波银行':   {'nfra_type': '城市商业银行',     'enterprise_scale': 'M(中型)'},
        '兴福村镇':   {'nfra_type': '农村商业银行',     'enterprise_scale': 'XS(微型)'},
        '某境外':     {'nfra_type': '外资法人银行',     'enterprise_scale': 'S(小型)'},
        '未知行':     {'nfra_type': '未识别',           'enterprise_scale': '未识别'},
    }, ensure_ascii=False), encoding='utf-8')

    monkeypatch.setitem(iv_did.CONFIG['paths'], 'bank_addresses_file', str(addr_path))

    type_map, scale_map = iv_did.load_bank_group_maps()

    assert type_map['工行'] == 'soe'
    assert type_map['招行'] == 'joint'
    assert type_map['宁波银行'] == 'city'
    assert type_map['兴福村镇'] == 'rural'
    assert type_map['某境外'] == 'foreign'
    assert type_map['未知行'] == 'other'

    assert scale_map['工行'] == 'L'
    assert scale_map['宁波银行'] == 'M'
    assert scale_map['兴福村镇'] == 'XS'
    assert scale_map['某境外'] == 'S'
    assert scale_map['未知行'] == 'other'


# ============================================================================
# 2. compute_bartik_iv
# ============================================================================

def test_compute_bartik_iv_adds_group_label_column(mini_panel, mini_articles):
    """compute_bartik_iv 输出含 bank_{prefix} 标签列."""
    group_map = {'工行': 'soe', '招行': 'joint', '宁波银行': 'city'}
    out = iv_did.compute_bartik_iv(mini_panel, mini_articles, group_map,
                                    group_prefix='type', base_year=2020)
    assert 'bank_type' in out.columns
    assert out.loc[out['target_bank'] == '工行', 'bank_type'].iloc[0] == 'soe'
    assert out.loc[out['target_bank'] == '招行', 'bank_type'].iloc[0] == 'joint'


def test_compute_bartik_iv_share_columns_are_built(mini_panel, mini_articles):
    """共同提及驱动的 share 列必须为每个非-other group 创建, 范围在 [0, 1]."""
    group_map = {'工行': 'soe', '招行': 'joint', '宁波银行': 'city'}
    out = iv_did.compute_bartik_iv(mini_panel, mini_articles, group_map,
                                    group_prefix='type', base_year=2020)

    share_cols = [c for c in out.columns if c.startswith('bartik_type_share_')]
    assert set(share_cols) == {
        'bartik_type_share_soe',
        'bartik_type_share_joint',
        'bartik_type_share_city',
    }
    for c in share_cols:
        assert (out[c] >= 0).all(), f"{c} 含负值"
        assert (out[c] <= 1).all(), f"{c} > 1"


def test_compute_bartik_iv_loo_excludes_self(mini_panel, mini_articles):
    """LOO shift 必须从组聚合中减除自身贡献.

    在基期 2020, 工行 (soe) 仅有自己 1 篇 score=1.0 → 组 soe 的 LOO
    对工行无可计算 (remain_cnt=0), shift_soe = NaN. iv 计入 share×NaN
    -> 不应抛 KeyError; 应正常返回.
    fix(omni-g-ivdid-03, 2026-06-11): share>0 × shift 缺失现传播 NaN
    (原 fillna(0) 零插补已删 — 旧 docstring "NaN 经 fillna(0) 后视作 0" 已废).
    """
    group_map = {'工行': 'soe', '招行': 'joint', '宁波银行': 'city'}
    out = iv_did.compute_bartik_iv(mini_panel, mini_articles, group_map,
                                    group_prefix='type', base_year=2020)
    iv_col = 'bartik_type_iv_full'
    assert iv_col in out.columns
    # 不应有 inf / 抛异常; 所有值 finite (NaN 可接受, inf 不可)
    finite_or_nan = out[iv_col].apply(lambda x: pd.isna(x) or np.isfinite(x)).all()
    assert finite_or_nan, f"{iv_col} 含 inf"
    # fix(omni-g-ivdid-03): 工行 share_joint=1, 2021 年组 joint 无其他文章
    # (shift_joint=NaN) → IV 应为 NaN 而非伪零 0
    gh_2021 = out.loc[(out['target_bank'] == '工行') & (out['year'] == 2021), iv_col]
    assert gh_2021.isna().all(), f"工行 2021 IV 应 NaN (shift 缺失传播), got {gh_2021.tolist()}"


def test_compute_bartik_iv_base_year_no_data_returns_nan(mini_panel, mini_articles):
    """base_year=2099 (无数据), iv 列应全为 NaN, 不抛异常."""
    group_map = {'工行': 'soe', '招行': 'joint', '宁波银行': 'city'}
    out = iv_did.compute_bartik_iv(mini_panel, mini_articles, group_map,
                                    group_prefix='type', base_year=2099)
    for track in ('_full', '_ctx'):
        col = f'bartik_type_iv{track}'
        assert col in out.columns
        assert out[col].isna().all(), f"{col} 应在缺基期时全 NaN"


# ============================================================================
# 3. compute_bartik_iv_fintech (article-category 维度)
# ============================================================================

def test_compute_bartik_iv_fintech_uses_category_col(mini_panel, mini_articles):
    """compute_bartik_iv_fintech 按 innovation_locus 列分组, 不用 co_mention."""
    cat_map = {'payment': 'pay', 'lending': 'lend'}
    out = iv_did.compute_bartik_iv_fintech(
        mini_panel, mini_articles, cat_map,
        group_prefix='ftcat', base_year=2020,
        category_col='innovation_locus',
    )
    # 应有 share + iv 列
    assert 'bartik_ftcat_share_pay' in out.columns
    assert 'bartik_ftcat_share_lend' in out.columns
    assert 'bartik_ftcat_iv_full' in out.columns
    # share 范围
    assert (out['bartik_ftcat_share_pay'] >= 0).all()
    assert (out['bartik_ftcat_share_pay'] <= 1).all()


# ============================================================================
# 4. compute_zone_leave1out
# ============================================================================

def test_compute_zone_leave1out_returns_zone_column(mini_panel, mini_articles):
    """compute_zone_leave1out 加 bank_zone 标签列, 按 PROVINCE_TO_ZONE 映射."""
    out = iv_did.compute_zone_leave1out(mini_panel, mini_articles, min_group_size=1)
    assert 'bank_zone' in out.columns
    # 北京 -> 京津冀
    assert out.loc[out['target_bank'] == '工行', 'bank_zone'].iloc[0] == '京津冀'
    # 广东 -> 珠三角
    assert out.loc[out['target_bank'] == '招行', 'bank_zone'].iloc[0] == '珠三角'


def test_compute_zone_leave1out_min_group_size_threshold(mini_panel, mini_articles):
    """min_group_size=10 (高于实际经济圈样本量) 让 LOO 全 NaN."""
    out = iv_did.compute_zone_leave1out(mini_panel, mini_articles, min_group_size=10)
    for track in ('_full', '_ctx'):
        col = f'zone_leave1out_tone{track}'
        if col in out.columns:
            assert out[col].isna().all(), (
                f"{col} 在 min_group_size=10 时应全 NaN (实际 < 10 篇)"
            )


def test_compute_zone_leave1out_loo_math(mini_panel):
    """构造 5 篇文章, 验证 LOO 公式: 对工行的 LOO = 其他北京银行得分总和 / 其他北京银行文章数.

    简化版: 4 银行全在 '京津冀' 经济圈, 每行 1 篇文章, score 设计为 1-2-3-4.
    工行 LOO = (2+3+4)/3 = 3.0
    """
    panel = pd.DataFrame([
        {'target_bank': f'bank_{i}', 'year': 2020,
         'bank_province': '北京', 'bank_city': '北京'}
        for i in range(4)
    ])
    articles = pd.DataFrame([
        {'docid': i, 'target_bank': f'bank_{i}', 'year': 2020,
         'llm_vote_score_full': float(i + 1),
         'llm_vote_score_ctx': float(i + 1),
         'co_mentioned_banks': '',
         'innovation_locus': 'payment'}
        for i in range(4)
    ])

    out = iv_did.compute_zone_leave1out(panel, articles, min_group_size=2)
    # bank_0 LOO = (2 + 3 + 4) / 3 = 3.0
    bank_0_loo = out.loc[out['target_bank'] == 'bank_0', 'zone_leave1out_tone_full'].iloc[0]
    assert abs(bank_0_loo - 3.0) < 1e-9, f"bank_0 LOO expected 3.0, got {bank_0_loo}"
    # bank_3 LOO = (1 + 2 + 3) / 3 = 2.0
    bank_3_loo = out.loc[out['target_bank'] == 'bank_3', 'zone_leave1out_tone_full'].iloc[0]
    assert abs(bank_3_loo - 2.0) < 1e-9, f"bank_3 LOO expected 2.0, got {bank_3_loo}"


# ============================================================================
# 5. diagnose_rotemberg_weights
# ============================================================================

def test_diagnose_rotemberg_weights_returns_expected_keys():
    """返回 dict 必须含 weights/hhi/n_negative/top5/share_means 5 个键."""
    n = 30
    rng = np.random.default_rng(42)
    panel = pd.DataFrame({
        'target_bank': [f'b{i//3}' for i in range(n)],
        'year': [2020 + i % 3 for i in range(n)],
        'bartik_t_share_A': rng.random(n),
        'bartik_t_share_B': rng.random(n),
        'bartik_t_share_C': rng.random(n),
        'bartik_t_iv_full': rng.random(n),
    })

    result = iv_did.diagnose_rotemberg_weights(panel, group_prefix='t')

    expected_keys = {'weights', 'hhi', 'n_negative', 'top5', 'share_means',
                     'negative_groups'}
    assert set(result.keys()) == expected_keys
    assert set(result['weights'].keys()) == {'A', 'B', 'C'}


def test_diagnose_rotemberg_weights_hhi_in_unit_interval():
    """HHI 必须 ∈ [1/N, 1] (Herfindahl 性质)."""
    n = 50
    rng = np.random.default_rng(123)
    panel = pd.DataFrame({
        'target_bank': [f'b{i//5}' for i in range(n)],
        'year': [2020 + i % 5 for i in range(n)],
        'bartik_s_share_X': rng.random(n),
        'bartik_s_share_Y': rng.random(n),
        'bartik_s_iv_full': rng.random(n),
    })

    result = iv_did.diagnose_rotemberg_weights(panel, group_prefix='s')

    # 2 维度, HHI 下界 = 1/2 = 0.5 — 但实际可能更高 (集中)
    assert 0 <= result['hhi'] <= 1.0, f"HHI {result['hhi']} 不在 [0,1]"
    # n_negative ∈ {0, 1, 2}
    assert 0 <= result['n_negative'] <= 2


def test_diagnose_rotemberg_weights_missing_iv_returns_empty():
    """iv_col 不存在时 graceful 返回空 dict, 不抛."""
    panel = pd.DataFrame({
        'target_bank': ['a', 'b'],
        'year': [2020, 2021],
        'bartik_x_share_A': [0.5, 0.3],
        # 没有 bartik_x_iv_full 列
    })
    result = iv_did.diagnose_rotemberg_weights(panel, group_prefix='x')
    assert result == {}


# ============================================================================
# 6. merge_policy_shocks (Wave 2 b2)
#    DID 政策冲击 + Event Study (Callaway-Sant'Anna 2021, Sun-Abraham 2021)
# ============================================================================

@pytest.fixture
def policy_shocks_json(tmp_path, monkeypatch) -> dict:
    """构造 tmp policy_shocks.json + monkeypatch CONFIG path, 返回 schema."""
    p = tmp_path / "policy_shocks.json"
    schema = {
        "_doc": "test fixture",
        "policy_X": {
            "prefix": "px",
            "groups": [
                {"year": 2020, "cities": ["北京", "上海"]},
                {"year": 2021, "cities": ["深圳"], "full_province": ["浙江"]},
            ],
        },
    }
    p.write_text(json.dumps(schema, ensure_ascii=False), encoding='utf-8')
    monkeypatch.setitem(iv_did.CONFIG['paths'], 'policy_shocks_file', str(p))
    return schema


@pytest.fixture
def did_panel() -> pd.DataFrame:
    """4 银行 × 3 年 bank-year panel, 含 bank_city + bank_province."""
    rows = []
    banks = [
        ('工行', '北京', '北京'),         # 2020 city match
        ('招行', '深圳', '广东'),         # 2021 city match
        ('宁波银行', '宁波', '浙江'),     # 2021 province match
        ('农行', '武汉', '湖北'),         # 未匹配, 控制组
    ]
    for bk, city, prov in banks:
        for yr in (2019, 2020, 2021, 2022):
            rows.append({
                'target_bank': bk,
                'year': yr,
                'bank_city': city,
                'bank_province': prov,
            })
    return pd.DataFrame(rows)


def test_merge_policy_shocks_creates_treated_post_columns(policy_shocks_json, did_panel):
    """创建 prefix_treated, prefix_post, prefix_treat_year 三个核心 DID 变量."""
    out = iv_did.merge_policy_shocks(did_panel)
    for col in ('px_treated', 'px_post', 'px_treat_year'):
        assert col in out.columns, f"缺 DID 列 {col}"


def test_merge_policy_shocks_city_match_assigns_treat_year(policy_shocks_json, did_panel):
    """工行 (bank_city=北京) 在 policy.cities=['北京'], year=2020 -> treat_year=2020."""
    out = iv_did.merge_policy_shocks(did_panel)
    gh_treat_year = out.loc[out['target_bank'] == '工行', 'px_treat_year'].iloc[0]
    assert gh_treat_year == 2020, f"工行 treat_year 应为 2020 (city match), got {gh_treat_year}"


def test_merge_policy_shocks_province_match_assigns_treat_year(policy_shocks_json, did_panel):
    """宁波银行 (bank_province=浙江) 在 full_province=['浙江'], year=2021 -> treat_year=2021."""
    out = iv_did.merge_policy_shocks(did_panel)
    nb_treat_year = out.loc[out['target_bank'] == '宁波银行', 'px_treat_year'].iloc[0]
    assert nb_treat_year == 2021, f"宁波银行 treat_year 应为 2021 (province match), got {nb_treat_year}"


def test_merge_policy_shocks_control_group_treat_year_zero(policy_shocks_json, did_panel):
    """农行 (武汉/湖北) 不在任何 group -> treat_year=0, treated=0."""
    out = iv_did.merge_policy_shocks(did_panel)
    nh = out.loc[out['target_bank'] == '农行']
    assert (nh['px_treat_year'] == 0).all(), f"农行 treat_year 应全 0"
    assert (nh['px_treated'] == 0).all(), f"农行 treated 应全 0"


def test_merge_policy_shocks_post_indicator_is_year_geq_treat(policy_shocks_json, did_panel):
    """工行 (treat_year=2020): year>=2020 时 post=1, year<2020 时 post=0."""
    out = iv_did.merge_policy_shocks(did_panel)
    gh = out.loc[out['target_bank'] == '工行'].sort_values('year')
    # year 2019 -> post=0; year 2020/2021/2022 -> post=1
    assert gh[gh['year'] == 2019]['px_post'].iloc[0] == 0
    assert gh[gh['year'] == 2020]['px_post'].iloc[0] == 1
    assert gh[gh['year'] == 2022]['px_post'].iloc[0] == 1


def test_merge_policy_shocks_rel_year_nan_for_control(policy_shocks_json, did_panel):
    """控制组的 rel_year 应为 NaN (Stata 中 never-treated baseline)."""
    out = iv_did.merge_policy_shocks(did_panel)
    nh = out.loc[out['target_bank'] == '农行']
    assert nh['px_rel_year'].isna().all(), f"农行 rel_year 应全 NaN"
    # 处理组应有具体数字 (= year - treat_year)
    gh_2022 = out.loc[(out['target_bank'] == '工行') & (out['year'] == 2022), 'px_rel_year'].iloc[0]
    assert gh_2022 == 2, f"工行 2022 (treat 2020) rel_year 应 = 2, got {gh_2022}"


def test_merge_policy_shocks_event_study_lag_lead_dummies_binary(policy_shocks_json, did_panel):
    """Event Study lag/lead 虚拟变量应是 0/1 二值."""
    out = iv_did.merge_policy_shocks(did_panel)
    for col in out.columns:
        if col.startswith('px_lag') or col.startswith('px_lead'):
            assert set(out[col].unique()).issubset({0, 1}), (
                f"{col} 含非 0/1 值: {out[col].unique()}"
            )


def test_merge_policy_shocks_missing_policy_file_returns_panel_unchanged(
    tmp_path, monkeypatch, did_panel,
):
    """policy_shocks.json 路径不存在时, graceful 跳过 DID 变量, 不抛."""
    # 不创建文件, 只 monkeypatch path
    missing_path = tmp_path / "nonexistent.json"
    monkeypatch.setitem(iv_did.CONFIG['paths'], 'policy_shocks_file', str(missing_path))

    out = iv_did.merge_policy_shocks(did_panel.copy())
    # 应返回原 panel (列数不变), 不抛
    assert set(out.columns) >= set(did_panel.columns)
    # 不应出现 DID 列
    did_cols = [c for c in out.columns if c.startswith('px_')]
    assert not did_cols, f"missing file 时不应生成 DID 列, got {did_cols}"
