"""回归测试: omni-fix g-herd 组修复 (2026-06-11).

锁定以下修复行为 (权威裁决: scripts/audit/_omni_fix/g-herd.json):
- g-herd-01: TF-IDF min_df 比例化 min(MIN_DF, max(2, ceil(0.01·n))) — 消除小组
  词表塌缩断崖 (n=6 df-band [5,5] 退化) 与 relaxed↔主参数断崖不连续; max_df
  守卫 df-band 退化时放开 1.0; 大组 (n≥~500) 仍封顶 MIN_DF 与历史一致。
- g-herd-02: max_features 按词频截断的规模依赖效应披露 — 截断咬合 (vocab 撞 cap)
  时运行期 logger.warning + 模块头/yaml 披露文本锁。
- g-herd-03: relaxed 降级与二次失败不再静默 — 两层 fallback 各记 logger.warning
  (bank/track/n_docs/原因), 对齐降级透明红线 (F7/F16/F21/F22 同族)。
- g-herd-04: 文档同步 — ctx 物化归属 stage 21→13; compute_herd_weights docstring
  轨1 用 content_full; 阈值闭边界 (≥/>=); sentiment.yaml chunk_size 注释去
  "分块运算" 死语义。
- g-herd-05: as-of yearly vocab fit — 年 t 文章的前驱计数仅用 year ≤ t 文档拟合
  的向量空间 (前驱构念严格后视, 不得用未来 DF/IDF); 追加未来年份文档不改变
  历史年份的计数 (as-of 不变性); 跨年 7 天窗前驱仍被覆盖。

⚠ 同时锁定既有修复不被本组改动破坏:
  fix(herd-decay-01) stable 排序 + fix(herd-bucket-nat) 内部 NaT 窗守卫。

# 白话: "跟风权重"是看一篇新闻前 7 天有没有相似报道。这组测试守住: 文章很少
# 的小银行不能因为参数一刀切导致词表被剪光(算不出相似度); 算某年的相似度只能
# 用当年及更早的文章建词表, 不许"偷看未来"; 各种降级兜底必须在日志里说清楚,
# 不许悄悄降级; 注释文档要和代码实际行为一致。
"""
from __future__ import annotations

import logging
import os
import sys

import numpy as np
import pandas as pd
import pytest

pytestmark = pytest.mark.fast

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.pipeline.sentiment import herd_decay as herd_module  # noqa: E402

_SRC_PATH = os.path.abspath(herd_module.__file__)
_YAML_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(_SRC_PATH))),
    'config', 'sentiment.yaml')


def _read_src(path: str) -> str:
    with open(path, encoding='utf-8') as fh:
        return fh.read()


@pytest.fixture(autouse=True)
def _quiet_logger(monkeypatch):
    """替换模块级 logger 为可被 caplog 捕获的普通 logger (propagate=True)。"""
    test_logger = logging.getLogger('test_omni_fix_herd')
    test_logger.handlers.clear()
    test_logger.setLevel(logging.DEBUG)
    monkeypatch.setattr(herd_module, 'logger', test_logger)


@pytest.fixture(autouse=True)
def _production_params(monkeypatch):
    """钉死生产默认参数, 防 config 漂移使断言失真。"""
    monkeypatch.setattr(herd_module, 'SIMILARITY_THRESHOLD', 0.35)
    monkeypatch.setattr(herd_module, 'TIME_WINDOW_DAYS', 7)
    monkeypatch.setattr(herd_module, 'MAX_FEATURES', 10000)
    monkeypatch.setattr(herd_module, 'MIN_DF', 5)
    monkeypatch.setattr(herd_module, 'MAX_DF', 0.9)


# ════════════════════════════════════════════════════════════════════════
# g-herd-01: min_df 比例化 + max_df 退化守卫
# ════════════════════════════════════════════════════════════════════════

class TestProportionalMinDf:
    """fix(omni-g-herd-01): df 阈值比例化, 消除小组词表塌缩断崖。"""

    def test_n6_no_longer_degenerate_band(self):
        # 旧实现: n=6 → min_df=5 + floor(0.9*6)=5 → 存活带 [5,5] (恰好 5/6 篇共现)。
        # 新实现: min_df = min(5, max(2, ceil(0.06))) = 2。
        vec = herd_module._build_tfidf_vectorizer(6)
        assert vec.min_df == 2, f"n=6 min_df 应为 2 (比例化), 实际 {vec.min_df}"

    def test_no_cliff_across_group_sizes(self):
        # 旧实现: n=5 (relaxed, min_df=1) → n=6 (min_df=5) 断崖跳 4。
        # 新实现: min_df 随 n 单调不减且步长 ≤1 (1→2 平滑, 之后 1%·n 爬升)。
        min_dfs = []
        for n in range(2, 600):
            vec = herd_module._build_tfidf_vectorizer(n)
            min_dfs.append(vec.min_df if isinstance(vec.min_df, int) else 1)
        arr = np.asarray(min_dfs)
        steps = np.diff(arr)
        assert (steps >= 0).all(), "min_df 必须随 n 单调不减"
        assert steps.max() <= 1, f"min_df 断崖跳变 (max step={steps.max()}), 比例化失效"

    def test_large_group_caps_at_config_min_df(self):
        # 大组 (ceil(0.01·n) ≥ MIN_DF=5 即 n ≥ 401) 封顶于 config 值, 与历史一致。
        vec = herd_module._build_tfidf_vectorizer(1000)
        assert vec.min_df == 5, f"大组 min_df 应封顶 MIN_DF=5, 实际 {vec.min_df}"

    def test_micro_group_relaxed(self):
        # 微型组 n<4: 任何 df 剪枝都会退化, 直接放开。
        for n in (2, 3):
            vec = herd_module._build_tfidf_vectorizer(n)
            assert vec.min_df == 1 and vec.max_df == 1.0

    def test_max_df_guard_releases_on_degenerate_band(self, monkeypatch):
        # df-band 退化守卫: floor(max_df·n) ≤ min_df 时放开 max_df=1.0,
        # 而非旧实现把 min_df 压回退化带。用 MAX_DF=0.4, n=5:
        # min_df=2, floor(0.4*5)=2 ≤ 2 → 守卫触发。
        monkeypatch.setattr(herd_module, 'MAX_DF', 0.4)
        vec = herd_module._build_tfidf_vectorizer(5)
        assert vec.max_df == 1.0, "df-band 退化时应放开 max_df=1.0"
        assert vec.min_df == 2, "守卫不得把 min_df 压回 1 (保留 hapax 剪枝)"

    def test_discriminative_df2_features_survive_n6(self):
        # 旧 [5,5] 退化带会剪除全部 df=2 判别性特征; 新 min_df=2 必须保留。
        # 文档 0/1 共享独有短语 "量子加密支付" (df=2); 其余 4 篇互不相同。
        docs = [
            '量子加密支付技术落地试点',
            '量子加密支付通道完成测试',
            '绿色信贷余额稳步增长报告',
            '县域普惠金融服务网点扩容',
            '跨境清算系统接入新成员行',
            '理财子公司产品净值化转型',
        ]
        vec = herd_module._build_tfidf_vectorizer(len(docs))
        vec.fit(docs)
        assert any('量子' in term for term in vec.vocabulary_), (
            "df=2 判别性特征 (量子加密支付) 应存活于 n=6 词表 (旧退化带会剪除)")

    def test_small_group_pairwise_discrimination_end_to_end(self):
        # 端到端判别性: n=6 小组 (生产参数) 含 3 个主题对 (α/β/γ, 各对内相似)。
        # 新 min_df=2 保留 df=2 判别特征 → 仅对内第二篇计 1 个前驱, 跨主题不误标。
        # 旧退化带 [5,5] 把 df=2 主题特征全剪 → 要么全员落入 boilerplate 子空间
        # 互相误标, 要么词表空转 relaxed — 两者都无法给出本判别模式。
        # (注: 比例化不消除全部投影膨胀 — 跨组 0.35 可比性仍是披露项, 故不断言
        #  "任意不相似组零跟风", 只锁判别结构。)
        texts = [
            '量子加密支付系统白皮书发布会现场实录',   # α-1
            '量子加密支付系统白皮书发布会要点回顾',   # α-2
            '县域乡村振兴信贷投放规模创新高纪录',     # β-1
            '县域乡村振兴信贷投放规模再创新高了',     # β-2
            '理财净值化转型产品货架全面升级换代',     # γ-1
            '理财净值化转型产品货架升级换代完成',     # γ-2
        ]
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * 6,
            '日期': pd.to_datetime([f'2023-05-0{d}' for d in range(1, 7)]),
            'content_full': texts,
            'content_ctx': texts,
        })
        out = herd_module.compute_herd_weights(df)
        assert out['n_similar_articles_full'].tolist() == [0, 1, 0, 1, 0, 1], (
            f"n=6 主题对判别失效: {out['n_similar_articles_full'].tolist()} "
            f"(期望仅各对第二篇计 1 前驱)")


# ════════════════════════════════════════════════════════════════════════
# g-herd-02: max_features 截断咬合披露
# ════════════════════════════════════════════════════════════════════════

class TestMaxFeaturesTruncationDisclosure:
    """fix(omni-g-herd-02): 截断咬合时 warning 披露 + 文本锁。"""

    def test_warning_when_cap_bites(self, monkeypatch, caplog):
        monkeypatch.setattr(herd_module, 'MAX_FEATURES', 50)
        caplog.set_level(logging.WARNING, logger='test_omni_fix_herd')
        texts = [
            '招商银行零售金融数字化转型战略全面提速覆盖财富管理信用卡多元场景',
            '招商银行公司金融科技赋能供应链票据融资服务中小企业降本增效显著',
            '招商银行金融市场业务量化交易系统升级风控模型迭代优化资本占用',
        ]
        mat = herd_module._fit_tfidf_with_fallback(
            texts, bank_name='招商银行', track='content_full')
        assert mat is not None
        bite_warns = [r for r in caplog.records if '截断咬合' in r.getMessage()]
        assert bite_warns, "vocab 撞 max_features cap 时必须 warning 披露"
        assert '招商银行' in bite_warns[0].getMessage()

    def test_no_warning_when_cap_not_bites(self, caplog):
        caplog.set_level(logging.WARNING, logger='test_omni_fix_herd')
        texts = ['银行公告一', '银行公告二', '银行公告三']
        herd_module._fit_tfidf_with_fallback(texts, bank_name='b', track='t')
        assert not [r for r in caplog.records if '截断咬合' in r.getMessage()]

    def test_disclosure_text_locks(self):
        src = _read_src(_SRC_PATH)
        assert 'fix(omni-g-herd-02' in src
        # 模块头必须披露规模依赖效应 (boilerplate 子空间), 不再仅称内存动机
        assert 'boilerplate' in src
        yaml_src = _read_src(_YAML_PATH)
        assert '截断咬合' in yaml_src, "yaml max_features 注释应披露截断咬合 warning"


# ════════════════════════════════════════════════════════════════════════
# g-herd-03: relaxed 降级透明化
# ════════════════════════════════════════════════════════════════════════

class TestRelaxedFallbackTransparency:
    """fix(omni-g-herd-03): 两层 fallback 各记 warning, 不再静默。"""

    # 4 篇字符集完全不相交的文档: min_df=2 剪光全部特征 → 主参数 ValueError
    _DISJOINT = ['甲乙丙丁戊甲乙丙丁', '己庚辛壬癸己庚辛壬', '子丑寅卯辰子丑寅卯', '巳午未申酉巳午未申']

    def test_relaxed_fallback_logs_warning(self, caplog):
        caplog.set_level(logging.WARNING, logger='test_omni_fix_herd')
        mat = herd_module._fit_tfidf_with_fallback(
            self._DISJOINT, bank_name='边缘银行', track='content_full')
        assert mat is not None, "relaxed 重试应成功 (min_df=1 全词表)"
        warns = [r for r in caplog.records if '降级 relaxed' in r.getMessage()]
        assert warns, "relaxed 降级必须 logger.warning (降级透明红线)"
        msg = warns[0].getMessage()
        assert '边缘银行' in msg and 'content_full' in msg and 'n_docs=4' in msg

    def test_double_failure_logs_warning_and_returns_none(self, caplog):
        caplog.set_level(logging.WARNING, logger='test_omni_fix_herd')
        # 纯空白文本: relaxed 仍 empty-vocabulary ValueError → 二次失败
        mat = herd_module._fit_tfidf_with_fallback(
            [' ', ' ', ' '], bank_name='空文本行', track='content_ctx')
        assert mat is None
        warns = [r for r in caplog.records
                 if 'weight=1.0' in r.getMessage() and '空文本行' in r.getMessage()]
        assert warns, "二次失败 (整组保持 weight=1.0) 必须 warning 留痕"

    def test_bank_name_plumbed_from_compute_herd_weights(self, caplog):
        # 端到端: compute_herd_weights 必须把 bank_name 传入透明日志
        caplog.set_level(logging.WARNING, logger='test_omni_fix_herd')
        df = pd.DataFrame({
            'target_bank': ['透明银行'] * 4,
            '日期': pd.to_datetime(['2023-03-01', '2023-03-02',
                                    '2023-03-03', '2023-03-04']),
            'content_full': self._DISJOINT,
            'content_ctx': self._DISJOINT,
        })
        herd_module.compute_herd_weights(df)
        warns = [r for r in caplog.records if '降级 relaxed' in r.getMessage()]
        assert warns, "端到端应触发 relaxed 降级 warning"
        assert any('透明银行' in r.getMessage() for r in warns), (
            "调用点必须传 bank_name (bank=None 等于没披露)")


# ════════════════════════════════════════════════════════════════════════
# g-herd-04: 文档同步 (源码/Yaml 文本锁)
# ════════════════════════════════════════════════════════════════════════

class TestDocSyncLocks:
    """fix(omni-g-herd-04): stage 14 归属 / content_full / 闭边界 / chunk_size。"""

    def test_no_stale_stage21_materialization_claims(self):
        src = _read_src(_SRC_PATH)
        assert 'stage 21 物化' not in src
        assert 'stage 21 _materialize_content_ctx' not in src
        assert 'stage 14' in src, "ctx 物化归属应为 stage 14 ctx_materializer"

    def test_compute_herd_weights_docstring_says_content_full(self):
        doc = herd_module.compute_herd_weights.__doc__
        assert 'content_full' in doc, "docstring 轨1 应为 content_full (病根A后实现)"
        assert "轨 1 用 '内容'" not in doc

    def test_threshold_closed_boundary_documented(self):
        src = _read_src(_SRC_PATH)
        assert '闭边界' in src, "阈值语义应注明 ≥ (闭边界), 与代码 >= 一致"
        # 代码本体仍是闭边界 (防止文档修复时误改语义)。
        # 2026-06-13 阈值敏感性: 比较对象由单值 SIMILARITY_THRESHOLD 改为
        # thr_list 循环变量 thr (基线在第 0 列), 闭边界 >= 语义不变。
        assert 'sim_matrix >= thr' in src
        assert 'sims >= thr' in src
        assert "thr_list = [SIMILARITY_THRESHOLD] if thresholds is None" in src

    def test_yaml_chunk_size_no_compute_semantics(self):
        yaml_src = _read_src(_YAML_PATH)
        assert '分块运算大小 (控制内存)' not in yaml_src, (
            "chunk_size 死参数不得在 yaml 层宣称运算语义")
        assert '仅日志显示' in yaml_src

    def test_yaml_min_df_documents_cap_semantics(self):
        yaml_src = _read_src(_YAML_PATH)
        assert 'cap' in yaml_src and 'fix(omni-g-herd-01' in yaml_src, (
            "yaml min_df 注释应说明其为比例化公式的上限 (cap)")


# ════════════════════════════════════════════════════════════════════════
# g-herd-05: as-of yearly vocab fit (前视消除)
# ════════════════════════════════════════════════════════════════════════

def _counts(df: pd.DataFrame, col: str = 'content_full') -> np.ndarray:
    """按生产路径排序后直调 _compute_similar_counts_for_track。"""
    df = df.copy()
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
    df = df.sort_values('日期', kind='stable')
    return herd_module._compute_similar_counts_for_track(
        df, col, df['日期'].tolist(), bank_name='asof-test')


class TestAsOfYearlyVocabFit:
    """fix(omni-g-herd-05): 年 t 计数仅用 ≤t 文档拟合的向量空间。"""

    @staticmethod
    def _hist_df():
        # 2023: A/B 共享短语 (7 天窗内, 应互判相似)
        return pd.DataFrame({
            '日期': ['2023-06-01', '2023-06-03'],
            'content_full': [
                '数字人民币试点扩容公告全文发布',
                '数字人民币试点扩容公告解读分析',
            ],
        })

    @staticmethod
    def _future_df():
        # 2024: 10 篇高度同质文档, 含 2023 短语 → 全历史 fit 会拉低其 IDF
        rows = []
        for k in range(10):
            rows.append({
                '日期': f'2024-03-{k + 10:02d}',
                'content_full': '数字人民币试点扩容公告全文发布' * 3 + f'第{k}批',
            })
        return pd.DataFrame(rows)

    def test_historical_counts_invariant_to_future_docs(self):
        # as-of 不变性: 追加未来年份文档后, 历史年份计数逐位不变。
        # (旧全历史 fit 下 2024 语料改变 IDF/df 剪裁 → 2023 计数可翻转。)
        hist = self._hist_df()
        combined = pd.concat([hist, self._future_df()], ignore_index=True)
        c_hist = _counts(hist)
        c_comb = _counts(combined)
        n_hist = len(hist)
        assert c_hist is not None and c_comb is not None
        assert np.array_equal(c_comb[:n_hist], c_hist), (
            f"2023 年计数随未来文档漂移: 单独 {c_hist.tolist()} vs "
            f"合并后 {c_comb[:n_hist].tolist()} — as-of yearly fit 失效")
        # 非平凡性: 2023 相似对必须真的命中
        assert c_hist.sum() > 0, "fixture 空转: 2023 相似对未命中阈值"

    def test_cross_year_window_predecessors_still_counted(self):
        # 跨年 7 天窗: 2024-01-02 文章的 2023-12-30 前驱仍计数
        # (年度前缀 [0, prefix_end) 含全部更早年份文档)。
        df = pd.DataFrame({
            '日期': ['2023-12-30', '2024-01-02'],
            'content_full': [
                '央行发布支付机构监管新规细则全文',
                '央行发布支付机构监管新规细则解读',
            ],
        })
        c = _counts(df)
        assert c is not None
        assert c[1] >= 1, "跨年 7 天窗内的前驱必须仍被计数 (年度前缀含更早年份)"
        assert c[0] == 0, "首篇无前驱"

    def test_first_year_single_doc_no_crash(self):
        # 首年仅 1 篇 (prefix_end<2 跳过), 次年正常计数
        df = pd.DataFrame({
            '日期': ['2022-05-01', '2024-04-01', '2024-04-03'],
            'content_full': [
                '年度股东大会决议公告披露分红预案',
                '绿色金融债券发行获批规模百亿元整',
                '绿色金融债券发行获批规模百亿元整再披露',
            ],
        })
        c = _counts(df)
        assert c is not None
        assert c[0] == 0
        assert c[2] >= 1, "2024 相似对应命中 (向量空间含 2022-2024 前缀)"

    def test_nat_rows_keep_weight_one_end_to_end(self):
        # NaT 行不进任何年度 fit, 端到端保持 weight=1.0/count=0;
        # 有效行为不受 NaT 影响 (NaT 末位排序前置)。
        df = pd.DataFrame({
            'target_bank': ['平安银行'] * 3,
            '日期': ['2023-08-01', '2023-08-02', None],
            'content_full': [
                '信用卡分期业务费率调整公告说明',
                '信用卡分期业务费率调整公告补充',
                '信用卡分期业务费率调整公告说明',
            ],
        })
        df['content_ctx'] = df['content_full']
        out = herd_module.compute_herd_weights(df)
        nat_mask = out['日期'].isna()
        assert (out.loc[nat_mask, 'herd_weight_full'] == 1.0).all()
        assert (out.loc[nat_mask, 'n_similar_articles_full'] == 0).all()
        assert out.loc[~nat_mask, 'n_similar_articles_full'].sum() >= 1, (
            "有效日期相似对仍须命中 (NaT 不应抹掉计数)")

    def test_fix_marker_present(self):
        src = _read_src(_SRC_PATH)
        assert 'fix(omni-g-herd-05' in src


# ════════════════════════════════════════════════════════════════════════
# 既有修复保持锁 (任务红线: 勿破坏 stable 排序 + NaT 内部窗修复)
# ════════════════════════════════════════════════════════════════════════

class TestPriorFixesPreserved:
    def test_stable_sort_fix_intact(self):
        src = _read_src(_SRC_PATH)
        assert 'fix(herd-decay-01' in src
        assert "kind='stable'" in src

    def test_bucket_nat_guard_intact(self):
        src = _read_src(_SRC_PATH)
        assert 'fix(herd-bucket-nat' in src
        assert '_cand_valid' in src

    def test_all_omni_markers_present(self):
        src = _read_src(_SRC_PATH)
        for marker in ('fix(omni-g-herd-01', 'fix(omni-g-herd-02',
                       'fix(omni-g-herd-03', 'fix(omni-g-herd-04',
                       'fix(omni-g-herd-05'):
            assert marker in src, f"缺修复标记 {marker}"

    def test_legacy_alias_columns_intact(self):
        # NON-BREAKING alias: herd_weight / n_similar_articles ≡ _full 轨
        texts = ['银行公告甲', '银行公告甲乙', '银行公告丙']
        df = pd.DataFrame({
            'target_bank': ['中国银行'] * 3,
            '日期': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']),
            'content_full': texts,
            'content_ctx': texts,
        })
        out = herd_module.compute_herd_weights(df)
        assert (out['herd_weight'] == out['herd_weight_full']).all()
        assert (out['n_similar_articles'] == out['n_similar_articles_full']).all()
