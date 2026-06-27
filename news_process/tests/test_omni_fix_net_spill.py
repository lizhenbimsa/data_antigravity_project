"""
test_omni_fix_net_spill.py — omni 审计修复回归锁 (g-net-spill 组, 2026-06-11)
================================================================================
锁定 pipeline/panel/network_spillover.py 6 条 confirmed/latent 缺陷的修复后行为
(fix omni-g-net-spill-01..-06), 防静默 revert。全部使用合成 DataFrame + mock
embedding 引擎, 不依赖盘上大数据、不调外部 API。

覆盖:
  -01 共现网络边权口径统一: docid 主路径 both-verified (每篇文章每对恰 +1),
      不再消费 stage-11 陈旧 co_mentioned_banks (phantom 边); 无 docid 旧 schema
      退化兜底保留并告警
  -02 Embedding 超级文档去 8000 字符前缀截断 (全文交 embedding_engine 分块) +
      docid 升序确定性拼接 (行序漂移免疫)
  -03 sim 列重命名 bank_emb_sim_mean → bank_emb_sim_mean_lag1 (_lg co-primary 同步),
      显式披露 t-1 文本口径
  -04 sim_mean 按索引去对角 (np.delete) 取真实 cosine 全均值 (域 [-1,1]),
      不再 sim_row>0 符号筛选; W_emb 构造前负 cosine clip 为 0 (告警披露)
  -05 eigenvector numpy(LCC) fallback 非 LCC 银行兜底 0.0 (原 NaN), 退化语义
      与主路径 (非主分量 ≈0) 跨年一致
  -06 NSP-B 注释勘误源码锁: 删"2SLS 对工具的标度变换不变"错误论证, 改为
      逐观测确定性变换声明 (识别有效性保持, 但第一阶段统计量会变)

# 白话: "银行共现网络溢出"指标的修复锁: 两家银行算"同篇报道共现"要以两边
# 都通过核验为准, 不再信一列过期的旧字段(会造出不存在的连线); 银行年度
# 合并大文档送去向量化时不再砍掉 8000 字以后的内容, 且拼接顺序固定;
# 相似度均值允许为负(余弦本来就有负), 但拿来当权重前负数要归零并声明;
# 算法兜底路径上"不在最大连通块"的银行统一给 0 而不是 NaN。
"""
import os
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

nx = pytest.importorskip('networkx')

from news_process.pipeline.panel import network_spillover as ns  # noqa: E402
from news_process.pipeline.text import embedding_engine as eng  # noqa: E402

pytestmark = pytest.mark.fast


# ============================================================================
# 共用合成数据 / mock
# ============================================================================

def _panel_2yr(tones_2017: dict, tone_col: str = 'llm_vote_tone_full'
               ) -> pd.DataFrame:
    """2017 (lag 年, 带 tone) + 2018 (目标年, tone NaN) 的最小面板。"""
    rows = []
    for year in (2017, 2018):
        for bank, tone in tones_2017.items():
            rows.append({'target_bank': bank, 'year': year,
                         tone_col: tone if year == 2017 else np.nan})
    return pd.DataFrame(rows)


def _recording_fake(store: list):
    """mock embed_texts: 记录传入 texts, 返回确定性随机向量。"""
    def _inner(texts, spec, **kwargs):
        items = [str(t) for t in texts]
        store.append(items)
        rng = np.random.RandomState(7)
        return rng.rand(len(items), 8).astype(np.float32)
    return _inner


def _marker_vector_fake(texts, spec, **kwargs):
    """mock embed_texts: 按文本标记返回工程化 2d 单位向量 (制造负 cosine)。

    VECA=[1,0] / VECB=[0.6,0.8] / VECC=[-1,0] →
    cos(A,B)=0.6, cos(A,C)=-1, cos(B,C)=-0.6。
    """
    vecs = []
    for t in texts:
        t = str(t)
        if 'VECA' in t:
            vecs.append([1.0, 0.0])
        elif 'VECB' in t:
            vecs.append([0.6, 0.8])
        elif 'VECC' in t:
            vecs.append([-1.0, 0.0])
        else:
            vecs.append([0.0, 1.0])
    return np.asarray(vecs, dtype=np.float32)


# ============================================================================
# fix omni-g-net-spill-01: 邻接矩阵 both-verified docid 口径
# ============================================================================

class TestAdjacencyBothVerified:

    def test_docid_path_one_per_article_no_phantom(self):
        """docid 主路径: 每篇文章每无序对恰 +1; verification 拒绝的银行
        (仅存于陈旧 co_mentioned_banks token) 不产生 phantom 边。"""
        df_ex = pd.DataFrame([
            # d1: A、B twin 行均幸存 → A-B +1 (旧实现双向双行计 2)
            {'year': 2017, 'docid': 'd1', 'target_bank': 'A银行',
             'co_mentioned_banks': 'B银行;C银行'},  # C token 陈旧, 须被忽略
            {'year': 2017, 'docid': 'd1', 'target_bank': 'B银行',
             'co_mentioned_banks': 'A银行'},
            # d2: 仅 A 行幸存 (B 被 verification 拒绝) → 不产生任何边
            {'year': 2017, 'docid': 'd2', 'target_bank': 'A银行',
             'co_mentioned_banks': 'B银行'},
            # d3: A、B、C 三行均幸存 → 三条边各 +1
            {'year': 2017, 'docid': 'd3', 'target_bank': 'A银行',
             'co_mentioned_banks': 'B银行;C银行'},
            {'year': 2017, 'docid': 'd3', 'target_bank': 'B银行',
             'co_mentioned_banks': 'A银行;C银行'},
            {'year': 2017, 'docid': 'd3', 'target_bank': 'C银行',
             'co_mentioned_banks': 'A银行;B银行'},
        ])
        adj, banks = ns.build_adjacency_matrix(df_ex, 2017)

        assert banks == ['A银行', 'B银行', 'C银行']
        # 每篇文章每对恰 +1: A-B 来自 d1+d3 = 2 (旧混合口径会给 5)
        assert adj.loc['A银行', 'B银行'] == 2
        # d2 phantom: A-C 仅 d3 一篇 (若消费 co token 会多算)
        assert adj.loc['A银行', 'C银行'] == 1
        assert adj.loc['B银行', 'C银行'] == 1
        # 对称 + 零对角
        assert (adj.values == adj.values.T).all()
        assert (np.diag(adj.values) == 0).all()

    def test_docid_path_dedups_duplicate_twin_rows(self):
        """同 docid 同 bank 重复行去重 (set), 每篇文章每对仍恰 +1。"""
        df_ex = pd.DataFrame([
            {'year': 2017, 'docid': 'd1', 'target_bank': 'A银行'},
            {'year': 2017, 'docid': 'd1', 'target_bank': 'A银行'},  # 重复行
            {'year': 2017, 'docid': 'd1', 'target_bank': 'B银行'},
        ])
        adj, _ = ns.build_adjacency_matrix(df_ex, 2017)
        assert adj.loc['A银行', 'B银行'] == 1

    def test_fallback_without_docid_keeps_legacy_counting(self):
        """无 docid 旧 schema 退化兜底: co_mentioned_banks 逐行双向计数
        (twin 双行 → 边权 2, 文档化的降级口径, 仅兼容用)。"""
        df_ex = pd.DataFrame([
            {'year': 2017, 'target_bank': 'A银行',
             'co_mentioned_banks': 'B银行'},
            {'year': 2017, 'target_bank': 'B银行',
             'co_mentioned_banks': 'A银行'},
        ])
        adj, _ = ns.build_adjacency_matrix(df_ex, 2017)
        assert adj.loc['A银行', 'B银行'] == 2

    def test_spillover_end_to_end_docid_no_phantom_edge(self):
        """生产函数 compute_network_spillovers 走 docid 主路径:
        phantom token (d3 行 co='C银行') 不得把 C 注入 A 的同行集合。"""
        df_ex = pd.DataFrame([
            {'year': 2017, 'docid': 'd1', 'target_bank': 'A银行',
             'co_mentioned_banks': 'B银行'},
            {'year': 2017, 'docid': 'd1', 'target_bank': 'B银行',
             'co_mentioned_banks': 'A银行'},
            {'year': 2017, 'docid': 'd2', 'target_bank': 'B银行',
             'co_mentioned_banks': 'C银行'},
            {'year': 2017, 'docid': 'd2', 'target_bank': 'C银行',
             'co_mentioned_banks': 'B银行'},
            # d3: 仅 A 幸存, 陈旧 token 指向 C → 不得产生 A-C phantom 边
            {'year': 2017, 'docid': 'd3', 'target_bank': 'A银行',
             'co_mentioned_banks': 'C银行'},
        ])
        panel = _panel_2yr({'A银行': 1.0, 'B银行': 0.0, 'C银行': -0.5})
        out = ns.compute_network_spillovers(panel.copy(), df_ex)

        y18 = out[out['year'] == 2018].set_index('target_bank')
        # A 同行仅 {B} → peer_tone = tone_B = 0.0 (phantom A-C 边会给 -0.25)
        assert abs(y18.loc['A银行', 'peer_tone_lag1_full'] - 0.0) < 1e-12
        # B 同行 {A, C} 等权 → (1.0 + -0.5)/2 = 0.25
        assert abs(y18.loc['B银行', 'peer_tone_lag1_full'] - 0.25) < 1e-12

    def test_docstring_documents_one_per_article(self):
        """docstring '每篇文章每对 +1' 与实现对齐 (组级裁决要求)。"""
        assert '每篇文章每对 +1' in ns.build_adjacency_matrix.__doc__

    def test_hyperedge_normalize_newman_degree_preserving(self):
        """P1-4/NB-01: hyperedge_normalize=True → Newman (2001) degree-preserving 归一
        每篇 N 银行文章每对贡献 1/(N-1), 单篇内每节点行和贡献=1.0; 默认 False 仍 +1
        (golden-safe)。锁定 True 分支语义, 防其作为休眠 opt-in 参数零覆盖回归。"""
        # 单篇 3 银行文章 {A,B,C}: 每对应得 1/(3-1)=0.5
        df_ex = pd.DataFrame([
            {'year': 2017, 'docid': 'd1', 'target_bank': 'A银行'},
            {'year': 2017, 'docid': 'd1', 'target_bank': 'B银行'},
            {'year': 2017, 'docid': 'd1', 'target_bank': 'C银行'},
        ])
        adj_hn, _ = ns.build_adjacency_matrix(df_ex, 2017, hyperedge_normalize=True)
        assert abs(adj_hn.loc['A银行', 'B银行'] - 0.5) < 1e-12
        assert abs(adj_hn.loc['A银行', 'C银行'] - 0.5) < 1e-12
        # degree-preserving: 每节点行和 = (N-1) 对 × 1/(N-1) = 1.0
        assert abs(adj_hn.loc['A银行'].sum() - 1.0) < 1e-12
        # 默认 False = 旧 +1 行为 (golden-safe 逐位等价)
        adj_def, _ = ns.build_adjacency_matrix(df_ex, 2017)
        assert adj_def.loc['A银行', 'B银行'] == 1.0
        # N=2 文章: 1/(2-1)=1.0, 与 +1 等价 (len(uniq)>1 守卫)
        df2 = pd.DataFrame([
            {'year': 2017, 'docid': 'p1', 'target_bank': 'A银行'},
            {'year': 2017, 'docid': 'p1', 'target_bank': 'B银行'},
        ])
        adj2, _ = ns.build_adjacency_matrix(df2, 2017, hyperedge_normalize=True)
        assert abs(adj2.loc['A银行', 'B银行'] - 1.0) < 1e-12


# ============================================================================
# fix omni-g-net-spill-02: 去 8000 字符前缀截断 + 确定性拼接
# ============================================================================

class TestEmbeddingSuperdocFullText:

    @staticmethod
    def _df_two_banks(long_body: str) -> pd.DataFrame:
        return pd.DataFrame([
            {'year': 2017, 'docid': 'd1', 'target_bank': 'A银行',
             '标题': 'tA', '内容': long_body},
            {'year': 2017, 'docid': 'd2', 'target_bank': 'B银行',
             '标题': 'tB', '内容': '短文本'},
        ])

    def test_full_superdoc_passed_untruncated(self, monkeypatch):
        """>8000 字符超级文档须整文传入 embedding 引擎 (无前缀截断)。"""
        store: list = []
        monkeypatch.setattr(eng, 'embed_texts', _recording_fake(store))

        long_body = '长' * 9000
        panel = _panel_2yr({'A银行': 0.1, 'B银行': 0.2})
        ns._compute_embedding_peer_network_pass(
            self._df_two_banks(long_body), panel,
            spec={'model': 'fake-spec'}, suffix="")

        assert len(store) == 1, "应只在 2018 (lag=2017) 触发一次嵌入"
        lengths = [len(t) for t in store[0]]
        assert max(lengths) > 8000, (
            f"超级文档被截断: max len={max(lengths)} (旧 8000 前缀截断回归)")

    def test_concat_order_deterministic_under_row_shuffle(self, monkeypatch):
        """拼接按 docid 升序确定性排序: 上游行序漂移不得改变超级文档。"""
        store: list = []
        monkeypatch.setattr(eng, 'embed_texts', _recording_fake(store))

        rows = [
            {'year': 2017, 'docid': 'd1', 'target_bank': 'A银行',
             '标题': 'tA1', '内容': 'alpha'},
            {'year': 2017, 'docid': 'd2', 'target_bank': 'A银行',
             '标题': 'tA2', '内容': 'beta'},
            {'year': 2017, 'docid': 'd3', 'target_bank': 'B银行',
             '标题': 'tB1', '内容': 'gamma'},
        ]
        df_fwd = pd.DataFrame(rows)
        df_rev = pd.DataFrame(rows[::-1])  # 行序反转 (模拟上游漂移)
        panel = _panel_2yr({'A银行': 0.1, 'B银行': 0.2})

        ns._compute_embedding_peer_network_pass(
            df_fwd, panel, spec={'model': 'fake-spec'}, suffix="")
        ns._compute_embedding_peer_network_pass(
            df_rev, panel, spec={'model': 'fake-spec'}, suffix="")

        assert store[0] == store[1], "行序漂移导致超级文档拼接漂移"
        text_a = store[0][0]  # bank_list 升序: A银行 在前
        assert text_a.index('alpha') < text_a.index('beta'), (
            "docid 升序未生效 (d1 文章应拼在 d2 之前)")


# ============================================================================
# fix omni-g-net-spill-03/04: sim 列重命名 + 真 cosine 均值 + 负权重 clip
# ============================================================================

class TestSimMeanRenameAndTrueCosine:

    @staticmethod
    def _df_marker_banks() -> pd.DataFrame:
        return pd.DataFrame([
            {'year': 2017, 'docid': 'd1', 'target_bank': 'A银行',
             '标题': 't', '内容': 'VECA'},
            {'year': 2017, 'docid': 'd2', 'target_bank': 'B银行',
             '标题': 't', '内容': 'VECB'},
            {'year': 2017, 'docid': 'd3', 'target_bank': 'C银行',
             '标题': 't', '内容': 'VECC'},
        ])

    def test_renamed_lag1_columns_and_old_names_absent(self, monkeypatch):
        """-03: 输出列为 bank_emb_sim_mean_lag1(_lg co-primary); 旧无 lag 名 + 已删
        本地稳健轨 _t2v 名不得再产出 (v3.14.0: gemini MAIN + text-embedding-3-large _lg)。"""
        monkeypatch.setattr(eng, 'embed_texts', _marker_vector_fake)
        panel = _panel_2yr({'A银行': 0.4, 'B银行': -0.5, 'C银行': 0.9})
        out = ns.compute_embedding_peer_network(self._df_marker_banks(), panel)

        assert 'bank_emb_sim_mean_lag1' in out.columns
        assert 'bank_emb_sim_mean_lag1_lg' in out.columns
        assert 'bank_emb_sim_mean' not in out.columns, "旧无-lag 列名回归"
        assert 'bank_emb_sim_mean_t2v' not in out.columns, "已删除的本地 _t2v 轨不得回归"

    def test_sim_mean_true_offdiagonal_mean_allows_negative(self, monkeypatch):
        """-04: sim_mean = 按索引去对角的全同行 cosine 均值 (可为负),
        [-1,1] 域断言不触发 (旧 [0,1] + sim_row>0 自我掩蔽结构已除)。"""
        monkeypatch.setattr(eng, 'embed_texts', _marker_vector_fake)
        panel = _panel_2yr({'A银行': 0.4, 'B银行': -0.5, 'C银行': 0.9})
        out = ns.compute_embedding_peer_network(self._df_marker_banks(), panel)

        y18 = out[out['year'] == 2018].set_index('target_bank')
        # A: mean(0.6, -1) = -0.2  (旧符号筛选给 0.6)
        assert abs(y18.loc['A银行', 'bank_emb_sim_mean_lag1'] - (-0.2)) < 1e-5
        # B: mean(0.6, -0.6) = 0.0
        assert abs(y18.loc['B银行', 'bank_emb_sim_mean_lag1'] - 0.0) < 1e-5
        # C: mean(-1, -0.6) = -0.8  (旧符号筛选给 NaN)
        assert abs(y18.loc['C银行', 'bank_emb_sim_mean_lag1'] - (-0.8)) < 1e-5

    def test_w_emb_clips_negative_cosine_weights(self, monkeypatch):
        """-04: W_emb 构造前负 cosine clip 为 0 — 负"权重"不得进入加权均值;
        clip 后全零行 (C 与所有同行负相关) → emb_peer_tone NaN 而非符号翻转值。"""
        monkeypatch.setattr(eng, 'embed_texts', _marker_vector_fake)
        panel = _panel_2yr({'A银行': 0.4, 'B银行': -0.5, 'C银行': 0.9})
        out = ns.compute_embedding_peer_network(self._df_marker_banks(), panel)

        y18 = out[out['year'] == 2018].set_index('target_bank')
        # A: clip 后唯一正权同行 B → peer_tone = tone_B = -0.5
        assert abs(y18.loc['A银行', 'emb_peer_tone_lag1_full'] - (-0.5)) < 1e-7
        # B: clip 后唯一正权同行 A → peer_tone = tone_A = 0.4
        assert abs(y18.loc['B银行', 'emb_peer_tone_lag1_full'] - 0.4) < 1e-7
        # C: 全部同行负 cosine → clip 后孤立 → NaN (负权重语义破坏不得入值)
        assert pd.isna(y18.loc['C银行', 'emb_peer_tone_lag1_full'])


# ============================================================================
# fix(network-metrics-audit 2026-06-13, P1-1): bank_eigen_cent 改按连通分量计算
# (取代 omni-g-net-spill-05 的"非 LCC 银行兜底 0.0"): 整图 power 迭代在断连图上给
# 非主导分量银行写 ~1e-42 数值残渣 → 改每分量 (≥_CMNT_MIN_COMPONENT_SIZE 节点) 内
# 单独 eigenvector + 分量内归一, 微小分量置 NaN (与 network_brokerage NaN 约定一致)。
# ============================================================================

class TestEigenvectorByComponent:

    def test_non_dominant_component_gets_real_values_not_residue(self):
        """P1-1 核心回归: 断连图上**非主导**大分量 (谱半径较小) 银行应得分量内真实
        中心度 (triangle ≈0.577), 而非旧整图 power 迭代的 ~1e-42 数值残渣;
        微小分量 (<3 节点) 银行 NaN。"""
        rows = []
        # 分量1: 重权三角 {A,B,C} (每对 5 篇 → 谱半径大, 主导)
        for k in range(5):
            rows += [
                {'year': 2017, 'docid': f'a{k}1', 'target_bank': 'A银行'},
                {'year': 2017, 'docid': f'a{k}1', 'target_bank': 'B银行'},
                {'year': 2017, 'docid': f'a{k}2', 'target_bank': 'B银行'},
                {'year': 2017, 'docid': f'a{k}2', 'target_bank': 'C银行'},
                {'year': 2017, 'docid': f'a{k}3', 'target_bank': 'A银行'},
                {'year': 2017, 'docid': f'a{k}3', 'target_bank': 'C银行'},
            ]
        # 分量2: 轻权三角 {D,E,F} (每对 1 篇 → 谱半径小, 非主导)
        rows += [
            {'year': 2017, 'docid': 'd1', 'target_bank': 'D银行'},
            {'year': 2017, 'docid': 'd1', 'target_bank': 'E银行'},
            {'year': 2017, 'docid': 'd2', 'target_bank': 'E银行'},
            {'year': 2017, 'docid': 'd2', 'target_bank': 'F银行'},
            {'year': 2017, 'docid': 'd3', 'target_bank': 'D银行'},
            {'year': 2017, 'docid': 'd3', 'target_bank': 'F银行'},
        ]
        # 分量3: 单边 {G,H} (微小, <3 节点)
        rows += [
            {'year': 2017, 'docid': 'g1', 'target_bank': 'G银行'},
            {'year': 2017, 'docid': 'g1', 'target_bank': 'H银行'},
        ]
        df_ex = pd.DataFrame(rows)
        banks = ['A银行', 'B银行', 'C银行', 'D银行', 'E银行', 'F银行', 'G银行', 'H银行']
        panel = pd.DataFrame({'target_bank': banks, 'year': [2017] * len(banks)})

        out = ns.compute_bank_network_centrality(panel.copy(), df_ex)
        idx = out.set_index('target_bank')['bank_eigen_cent']

        # 主导分量内银行: 分量内归一正中心度
        assert idx.loc['A银行'] > 0.1
        # 非主导大分量 (D/E/F): 真实分量内中心度, **不是** ~1e-42 残渣 (P1-1 修复点)
        assert idx.loc['D银行'] > 0.1, (
            f"非主导分量 bank_eigen_cent={idx.loc['D银行']:.2e} 像数值残渣 → P1-1 回归")
        assert idx.loc['F银行'] > 0.1
        # 微小分量 (<3 节点): NaN (不再写 0/残渣)
        assert pd.isna(idx.loc['G银行'])
        assert pd.isna(idx.loc['H银行'])

    def test_tiny_component_banks_are_nan(self):
        """孤立/微小分量 (<_CMNT_MIN_COMPONENT_SIZE 节点) 的 bank_eigen_cent 置 NaN。"""
        df_ex = pd.DataFrame([
            {'year': 2017, 'docid': 'a1', 'target_bank': 'A银行'},
            {'year': 2017, 'docid': 'a1', 'target_bank': 'B银行'},
            {'year': 2017, 'docid': 'a2', 'target_bank': 'B银行'},
            {'year': 2017, 'docid': 'a2', 'target_bank': 'C银行'},
            {'year': 2017, 'docid': 'a3', 'target_bank': 'A银行'},
            {'year': 2017, 'docid': 'a3', 'target_bank': 'C银行'},
            {'year': 2017, 'docid': 'z1', 'target_bank': 'Z银行'},
            {'year': 2017, 'docid': 'z1', 'target_bank': 'Y银行'},
        ])
        banks = ['A银行', 'B银行', 'C银行', 'Z银行', 'Y银行']
        panel = pd.DataFrame({'target_bank': banks, 'year': [2017] * 5})
        out = ns.compute_bank_network_centrality(panel.copy(), df_ex)
        idx = out.set_index('target_bank')['bank_eigen_cent']
        assert idx.loc['A银行'] > 0.1
        assert pd.isna(idx.loc['Z银行'])
        assert pd.isna(idx.loc['Y银行'])


# ============================================================================
# fix omni-g-net-spill-06: NSP-B 注释勘误源码锁 (2SLS 标度声明)
# ============================================================================

class TestNspBCommentCorrection:

    def test_wrong_invariance_claim_removed(self):
        """旧错误论证 '2SLS 对工具的标度变换不变' 须从源码移除 — 行特定重归一
        非全局标量缩放, 工具截面变异/第一阶段相关性会变。"""
        src = Path(ns.__file__).read_text(encoding='utf-8')
        assert '标度变换不变' not in src, (
            'NSP-B 旧错误论证回归: 行特定重归一不是 2SLS 不变的标度变换')

    def test_corrected_rowwise_transform_disclosure_present(self):
        """新声明: 逐观测确定性变换 + 第一阶段统计量会变; P1-5 进一步勘误旧
        "外生性不受影响/识别有效性保持"为技术不准确 (支撑集 obs_mask 内生于媒体覆盖)。"""
        src = Path(ns.__file__).read_text(encoding='utf-8')
        assert '逐观测 (row-specific) 确定性变换' in src
        assert '旧注释"相关性不变"不成立' in src
        # P1-5 (network-metrics-audit 2026-06-13): 取代旧"识别有效性保持"笼统声称
        assert '支撑集选择性' in src
        assert 'P1-5' in src
