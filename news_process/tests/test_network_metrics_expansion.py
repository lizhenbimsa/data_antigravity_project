"""网络指标扩展 (WS-A/B/C, 2026-06-21) 单元测试。

权威执行计划: scripts/audit/NETWORK_METRICS_EXPANSION_EXECUTION_PLAN_2026-06-21.md
v3 实现评审 (wf_448c19fe-d24) 加固: GF 独立重算总计 (非重和) / 实键匹配 /
monkeypatch 非空守恒 / WS-A 直测各拓扑分支 (assortativity NaN 守卫 + modularity
weight= 口径 + 精确 diameter/分量)。

覆盖:
  WS-C  Gould-Fernandez (_gould_fernandez_roles): 独立重算守恒 / 无向坍缩
        gatekeeper≡representative / 经典排除直连端点 (clique→0) / 缺失分组→NaN /
        实键匹配 (load_bank_group_maps) / 面板守恒分支真跑 (monkeypatch)。
  WS-B  二分图 (_bipartite_bank_metrics): degree<2→NaN 不崩 / closeness 限 LCC /
        仅 bank_nodes 输出。
  WS-A  net 级 (_net_level_extra_metrics + 集成): 精确拓扑值 / assortativity NaN
        守卫 / modularity weight= 口径一致 / 确定性。
"""
import math

import networkx as nx
import numpy as np
import pandas as pd
import pytest

from news_process.pipeline.panel.network_brokerage import _bipartite_bank_metrics
from news_process.pipeline.panel.network_spillover import (
    _gould_fernandez_roles,
    _net_level_extra_metrics,
    compute_bank_network_centrality,
)

_GF_KEYS = ('gf_coordinator', 'gf_itinerant', 'gf_gatekeeper_rep',
            'gf_liaison', 'gf_total')


def _net_inputs(G):
    """从任意 G 造 _net_level_extra_metrics 所需的 (G,G_lcc,lcc,components,n)。"""
    comps = list(nx.connected_components(G))
    lcc = max(comps, key=len) if comps else set()
    return G, G.subgraph(lcc).copy(), lcc, comps, G.number_of_nodes()


def _gf_independent_total(G, grp, i):
    """**独立**重算 broker i 的 gf_total = 非邻接、双端有分组的无序邻居对数
    (不分类角色, 故非重和实现的四角色; 真正交叉验证总计)。"""
    if grp.get(i) is None:
        return None
    nbrs = sorted(G.neighbors(i))
    tot = 0
    for ia in range(len(nbrs)):
        if grp.get(nbrs[ia]) is None:
            continue
        for ib in range(ia + 1, len(nbrs)):
            if grp.get(nbrs[ib]) is None:
                continue
            if not G.has_edge(nbrs[ia], nbrs[ib]):
                tot += 1
    return tot


# ───────────────────────── WS-C: Gould-Fernandez ─────────────────────────

def test_gf_roles_and_independent_total():
    """具体角色按群正确归类; gf_total 经**独立重算**交叉验证 (非重和实现)。"""
    G = nx.Graph()
    grp = {'a': 1, 'c': 2, 'e': 3, 'x': 1, 'y': 1, 'p': 1, 'q': 1,
           'z': 2, 'b': 1}
    G.add_edges_from([('x', 'a'), ('x', 'c'), ('x', 'e')])   # x: gk_rep,gk_rep,liaison
    G.add_edges_from([('y', 'p'), ('y', 'q')])               # y: coordinator
    G.add_edges_from([('z', 'a'), ('z', 'b')])               # z(g2): itinerant
    roles = _gould_fernandez_roles(G, grp)

    # 角色归类
    assert roles['x']['gf_gatekeeper_rep'] == 2
    assert roles['x']['gf_liaison'] == 1
    assert roles['x']['gf_coordinator'] == 0 and roles['x']['gf_itinerant'] == 0
    assert roles['y']['gf_coordinator'] == 1
    assert roles['z']['gf_itinerant'] == 1
    # 独立重算总计 (交叉验证, 防 GF-CONSERV-TAUTOLOGY)
    for n in G.nodes():
        indep = _gf_independent_total(G, grp, n)
        assert roles[n]['gf_total'] == indep, f"{n}: {roles[n]['gf_total']} != {indep}"


def test_gf_excludes_adjacent_endpoints_clique_robust():
    """经典 GF: 端点直连不计 → K4 完全图 GF 经纪全 0 (clique-鲁棒)。"""
    G = nx.complete_graph(['a', 'b', 'c', 'd'])
    grp = {'a': 1, 'b': 2, 'c': 3, 'd': 1}
    roles = _gould_fernandez_roles(G, grp)
    for n in G.nodes():
        assert roles[n]['gf_total'] == 0


def test_gf_output_keys_are_merged_set_no_directed_roles():
    """实测函数输出键 == _GF_KEYS; 无独立 gatekeeper/representative (无向坍缩)。"""
    G = nx.Graph([('i', 'a'), ('i', 'b')])
    roles = _gould_fernandez_roles(G, {'i': 1, 'a': 2, 'b': 3})
    assert set(roles['i'].keys()) == set(_GF_KEYS)
    assert 'gf_gatekeeper' not in roles['i']
    assert 'gf_representative' not in roles['i']


def test_gf_missing_group_yields_nan():
    """broker 分组缺失 → 全 NaN; 邻居分组缺失 → 跳过该 2-path。"""
    G = nx.Graph([('i', 'a'), ('i', 'b')])
    roles = _gould_fernandez_roles(G, {'a': 1, 'b': 2})  # i 无分组
    assert all(math.isnan(roles['i'][k]) for k in _GF_KEYS)
    assert roles['a']['gf_total'] == 0  # a 唯一邻居 i 无组 → 无可用 2-path


def test_gf_real_group_map_namekey_matching():
    """复用真实 load_bank_group_maps(): 真实银行名命中→非 NaN; 伪造名→NaN。"""
    from news_process.pipeline.panel.iv_did import load_bank_group_maps
    type_map, _ = load_bank_group_maps()
    if len(type_map) < 3:
        pytest.skip("group map 空, 跳过实键匹配测试")
    names = list(type_map.keys())[:3]
    G = nx.Graph([(names[0], names[1]), (names[0], names[2])])
    roles = _gould_fernandez_roles(G, type_map)
    assert not math.isnan(roles[names[0]]['gf_total'])  # 真名命中
    G2 = nx.Graph([('___FAKE_BANK___', names[0]), ('___FAKE_BANK___', names[1])])
    roles2 = _gould_fernandez_roles(G2, type_map)
    assert math.isnan(roles2['___FAKE_BANK___']['gf_total'])  # 伪名缺组


# ───────────────────────── WS-B: 二分图原生中心度 ─────────────────────────

def _toy_bipartite():
    """2 连通分量: comp1 {m0,m1}×{b0,b1} (b0,b1 deg2); comp2 m2-b2 (b2 deg1)。"""
    G = nx.Graph()
    G.add_nodes_from(['m0', 'm1', 'm2'], bipartite=0)
    G.add_nodes_from(['b0', 'b1', 'b2'], bipartite=1)
    G.add_edges_from([('m0', 'b0'), ('m0', 'b1'),
                      ('m1', 'b0'), ('m1', 'b1'), ('m2', 'b2')])
    return G, {'b0', 'b1', 'b2'}


def test_bipartite_node_redundancy_degree_lt2_nan_no_crash():
    """node_redundancy 对 degree<2 银行返 NaN 且不崩 (degree>=2 预过滤铁律)。"""
    G, banks = _toy_bipartite()
    out = _bipartite_bank_metrics(G, banks)
    assert math.isnan(out['b2']['brok_bip_node_redundancy'])
    assert not math.isnan(out['b0']['brok_bip_node_redundancy'])
    assert not math.isnan(out['b1']['brok_bip_node_redundancy'])


def test_bipartite_closeness_restricted_to_lcc():
    """closeness 限制 LCC → 孤立分量银行 b2 返 NaN, LCC 内银行有值。"""
    G, banks = _toy_bipartite()
    out = _bipartite_bank_metrics(G, banks)
    assert math.isnan(out['b2']['brok_bip_closeness_cent'])
    assert not math.isnan(out['b0']['brok_bip_closeness_cent'])


def test_bipartite_returns_only_bank_nodes_all_metrics():
    """输出键 = bank_nodes; 每行含全部 5 指标; degree 对所有银行有限。"""
    G, banks = _toy_bipartite()
    out = _bipartite_bank_metrics(G, banks)
    assert set(out.keys()) == banks
    need = {'brok_bip_degree_cent', 'brok_bip_between_cent',
            'brok_bip_closeness_cent', 'brok_bip_clustering_ra',
            'brok_bip_node_redundancy'}
    for b in banks:
        assert need <= set(out[b].keys())
    assert all(not math.isnan(out[b]['brok_bip_degree_cent']) for b in banks)


# ───────────────────────── WS-A: net 级 (直测各拓扑分支) ─────────────────────────

def test_net_assortativity_nan_guard_regular_vs_variance():
    """度方差=0 (4-cycle 正则图) → assortativity NaN; 有方差 (星图) → 有限 (-1.0)。"""
    c4 = nx.cycle_graph(4)  # 2-regular
    nx.set_edge_attributes(c4, 1.0, 'weight')
    out_c4 = _net_level_extra_metrics(*_net_inputs(c4))
    assert math.isnan(out_c4['net_assortativity_yr'])  # NaN 守卫触发
    assert out_c4['net_transitivity_yr'] == 0.0        # 无三角

    star = nx.star_graph(4)  # 度 {4,1,1,1,1}, 完全异配
    nx.set_edge_attributes(star, 1.0, 'weight')
    out_star = _net_level_extra_metrics(*_net_inputs(star))
    assert not math.isnan(out_star['net_assortativity_yr'])
    assert abs(out_star['net_assortativity_yr'] - (-1.0)) < 1e-9


def test_net_modularity_weight_consistency():
    """modularity 检测+打分均 weight='weight' (一致口径); 该图上加权≠无权打分
    (证明 weight= 口径关键, 防 greedy(None)+modularity('weight') 不一致)。"""
    G = nx.Graph()
    # 两强三角簇 (intra weight=10) + 一弱跨边 (weight=1)
    for u, v in [('a', 'b'), ('b', 'c'), ('a', 'c'),
                 ('d', 'e'), ('e', 'f'), ('d', 'f')]:
        G.add_edge(u, v, weight=10.0)
    G.add_edge('c', 'd', weight=1.0)
    out = _net_level_extra_metrics(*_net_inputs(G))
    m_helper = out['net_modularity_yr']
    comms_w = nx.community.greedy_modularity_communities(G, weight='weight')
    m_consistent = nx.community.modularity(G, comms_w, weight='weight')
    m_mismatch = nx.community.modularity(G, comms_w, weight=None)
    assert abs(m_helper - m_consistent) < 1e-9       # helper = 一致加权口径
    assert m_helper > 0.3                              # 两簇 → 高模块度
    assert abs(m_consistent - m_mismatch) > 1e-6       # 该图上口径确实影响数值


def test_net_exact_topology_values_path_and_disconnected():
    """精确拓扑值: 路径图 diameter/分量; 断连图 giant_share/n_components。"""
    p4 = nx.path_graph(['a', 'b', 'c', 'd'])  # a-b-c-d
    nx.set_edge_attributes(p4, 1.0, 'weight')
    out = _net_level_extra_metrics(*_net_inputs(p4))
    assert out['net_diameter_yr'] == 3.0
    assert out['net_n_components_yr'] == 1.0
    assert out['net_giant_share_yr'] == 1.0
    assert out['net_transitivity_yr'] == 0.0

    # 断连: 三角(3) + 孤立对(2) → 2 分量, 巨片 3/5
    dis = nx.Graph()
    for u, v in [('a', 'b'), ('b', 'c'), ('a', 'c'), ('d', 'e')]:
        dis.add_edge(u, v, weight=1.0)
    out2 = _net_level_extra_metrics(*_net_inputs(dis))
    assert out2['net_n_components_yr'] == 2.0
    assert abs(out2['net_giant_share_yr'] - 3 / 5) < 1e-9
    assert out2['net_diameter_yr'] == 1.0  # 巨片=三角, 直径 1


def test_net_modularity_zero_edge_graph_nan():
    """无边图 → modularity NaN (守卫); 全孤立点。"""
    G = nx.Graph()
    G.add_nodes_from(['a', 'b', 'c'])
    out = _net_level_extra_metrics(*_net_inputs(G))
    assert math.isnan(out['net_modularity_yr'])
    assert out['net_n_components_yr'] == 3.0


# ───────────────────────── 集成: compute_bank_network_centrality ─────────────────────────

def _toy_panel_and_exploded():
    """两年小样: 文章1 A,B,C 共现(三角); 文章2 A,B; 文章3 D 孤立。"""
    rows = []
    docid = 0
    for year in (2017, 2018):
        for banks in (['A', 'B', 'C'], ['A', 'B'], ['D']):
            for bk in banks:
                rows.append({'docid': f'd{docid}', 'year': year, 'target_bank': bk})
            docid += 1
    df = pd.DataFrame(rows)
    panel = df[['target_bank', 'year']].drop_duplicates().reset_index(drop=True)
    return panel, df


def test_ws_a_columns_present_and_deterministic():
    """net 级 6 新列进面板, 两次调用逐值一致 (确定性)。"""
    panel, df = _toy_panel_and_exploded()
    p1 = compute_bank_network_centrality(panel.copy(), df)
    p2 = compute_bank_network_centrality(panel.copy(), df)
    new_net = ['net_modularity_yr', 'net_assortativity_yr', 'net_transitivity_yr',
               'net_diameter_yr', 'net_giant_share_yr', 'net_n_components_yr']
    for c in new_net:
        assert c in p1.columns
    a = p1[new_net].sort_index().fillna(-999).to_numpy()
    b = p2[new_net].sort_index().fillna(-999).to_numpy()
    assert np.array_equal(a, b)


def _gf_cycle_fixture():
    """单年 4-cycle A-E-B-F-A: 每节点邻居非邻接 → 真 broker (GF>0)。"""
    rows, docid = [], 0
    for u, v in [('A', 'E'), ('E', 'B'), ('B', 'F'), ('F', 'A')]:
        for bk in (u, v):
            rows.append({'docid': f'd{docid}', 'year': 2018, 'target_bank': bk})
        docid += 1
    df = pd.DataFrame(rows)
    panel = df[['target_bank', 'year']].drop_duplicates().reset_index(drop=True)
    return panel, df


def test_ws_c_gf_panel_conservation_runs(monkeypatch):
    """monkeypatch 真实 group map → gf_total 非空 (守恒分支真跑) + 守恒成立 + GF>0。"""
    panel, df = _gf_cycle_fixture()
    fake_map = {'A': 'soe', 'B': 'soe', 'E': 'city', 'F': 'city'}
    monkeypatch.setattr(
        'news_process.pipeline.panel.iv_did.load_bank_group_maps',
        lambda: (fake_map, {}))
    p = compute_bank_network_centrality(panel.copy(), df)
    for c in _GF_KEYS:
        assert c in p.columns
    sub = p.dropna(subset=['gf_total'])
    assert len(sub) > 0, "守恒分支应真跑 (非 vacuous)"
    rhs = (sub['gf_coordinator'] + sub['gf_itinerant']
           + sub['gf_gatekeeper_rep'] + sub['gf_liaison'])
    assert np.allclose(sub['gf_total'], rhs)
    # 4-cycle 每节点 broker 1 个非邻接同/异群对 → GF>0 可达
    assert sub['gf_total'].max() >= 1


# ───────────────────────── 标签接线 (MISSING_SCHEMA-1/-2) ─────────────────────────

_NEW16 = [
    'net_modularity_yr', 'net_assortativity_yr', 'net_transitivity_yr',
    'net_diameter_yr', 'net_giant_share_yr', 'net_n_components_yr',
    'gf_coordinator', 'gf_itinerant', 'gf_gatekeeper_rep', 'gf_liaison',
    'gf_total', 'brok_bip_degree_cent', 'brok_bip_between_cent',
    'brok_bip_closeness_cent', 'brok_bip_clustering_ra', 'brok_bip_node_redundancy',
]


def test_dta_labels_reach_new_columns_not_colname_fallback():
    """16 新列经 stata_export.build_variable_labels 命中描述标签 (非列名兜底,
    MISSING_SCHEMA-1: export.py STATA_LABELS 不入 stage-46 .dta 路径)。"""
    from news_process.pipeline.panel.stata_export import build_variable_labels
    df = pd.DataFrame({c: [0.0] for c in _NEW16})
    labels = build_variable_labels(df)
    for c in _NEW16:
        assert c in labels and labels[c] != c, f"{c} 退化为列名 (无描述标签)"
        assert len(labels[c].encode('latin-1', 'ignore')) <= 80


def test_infer_label_does_not_regress_brokerage_fire_sale():
    """_infer_label brok_bip 分支不改写既有 brokerage_fire_sale (MISSING_SCHEMA-2)。"""
    from news_process.pipeline.panel.codebook import _infer_label
    assert 'Bipartite' not in _infer_label('brokerage_fire_sale')
    assert _infer_label('brok_bip_between_cent').startswith('Bipartite')
    assert _infer_label('gf_total').startswith('GF Brokerage Role')
    assert _infer_label('net_modularity_yr') == 'Network-Level Structure (annual)'


if __name__ == '__main__':
    raise SystemExit(pytest.main([__file__, '-v']))
