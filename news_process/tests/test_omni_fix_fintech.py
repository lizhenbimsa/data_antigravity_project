"""回归测试: omni-fix g-fintech 组修复 (2026-06-11).

锁定以下修复行为 (权威裁决: scripts/audit/_omni_fix/g-fintech.json + 组级裁决):
- g-fintech-01 (P3): IDF 参考语料按唯一文档去重 — (标题,日期) 优先, 缺列回退文本
  自身为键; 同文 × k 银行爆炸行/跨媒体转载不再在 DF 分子与 N_total 分母中计 k 次
- g-fintech-02 (P3): 'SIF 加权质心' 名实不符修正 — 措辞改 IDF 加权质心, Arora 2017
  降格为 "加权质心思想借鉴", Ethayarajh 2019 降格为 "现象动机引用" (源码文本锁)
- g-fintech-03 (P2): DF 与 TF 同分词器 — DF 改 jieba 整词重算
  (_compute_global_df_jieba 替换 AC 子串计数源 _parse_global_df); 子串误命中
  ('网贷' ∈ '互联网贷款') 与重叠双计 ('大数据'+'数据风控') 不再进 DF;
  main() DF 参考语料 = 12_full 全量 (⚠ 14_news_with_ctx 仅 fintech 子集, 禁用)
  + 在线物化 content_full = prepend_title(标题, 内容) (与 TF 打分同语料,
  对齐 tone_words 先例)
- 组级裁决①: 二次熔断零填改 NaN — "未验证" 文章不再以 0.0 计入下游 bank-year
  均值分母 (encode.py avg_ft_intensity* / attention_media mean_*); sum 语义不变
- 组级裁决②: 6/1506 jieba 永不可匹配关键词 (含空格/顿号, 被 jieba 块切分正则在
  词典查找之前切开, add_word 注入技术不可行) 走 "剔除 + 披露" — 从 IDF/质心/
  CosSim 权重宇宙剔除并 WARNING 披露

外部依赖处理: 无网络; v3.14.0 (all-API-embedding) 起本地 sentence_transformers
路径已彻底移除, 关键词语义编码改走统一引擎 _eng.embed_texts(spec) 纯 API 路径 →
质心宇宙/权重宇宙测试改 monkeypatch fi._eng.embed_texts 返回确定性 fake 向量
(3072 维), 隔离网络/缓存依赖; 词典/配置用仓库真实文件 (模块 import 时加载)。

# 白话: 这组测试管"金融科技强度分"的统计口径: 算关键词稀有度(IDF)时,
# 同一篇稿被转载/配多家银行只算一篇; 数词频和算稀有度必须用同一把"切词刀"
# (jieba), 不能一边整词一边子串, 否则"网贷"会被"互联网贷款"误算; 词典里
# 6 个带空格/顿号、jieba 永远切不出来的词, 干脆剔除并公开声明; 没通过校验
# 的文章得分记 NaN, 不能记 0 去拉低银行年均分。
"""
from __future__ import annotations

import math
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import news_process  # noqa: E402
from news_process.pipeline.filtering import fintech_intensity as fi  # noqa: E402

pytestmark = [
    pytest.mark.fast,
    pytest.mark.skipif(
        not fi.FINTECH_KEYWORDS,
        reason='fintech_dict.json 未找到 (词典加载为空), 无法验证 jieba 口径'),
]

_PKG = Path(news_process.__file__).parent
_SRC = (_PKG / 'pipeline' / 'filtering' / 'fintech_intensity.py').read_text(
    encoding='utf-8')

# 审计实证句 (g-fintech-03 evidence): AC 子串扫描命中 3 词
# ['网贷'(子串于互联网贷款), '大数据', '数据风控'(与大数据重叠双计)],
# jieba 整词分词仅命中 ['数据风控']。
_AUDIT_SENTENCE = '商业银行积极发展互联网贷款业务, 推进大数据风控。'


def _require_kws(*kws: str) -> None:
    missing = [kw for kw in kws if kw not in set(fi.FINTECH_KEYWORDS)]
    if missing:
        pytest.skip(f'测试依赖词典关键词缺失: {missing}')


# ════════════════════════════════════════════════════════════════════════
# 组级裁决②: 6/1506 永不可匹配关键词 — 剔除 + 披露
# ════════════════════════════════════════════════════════════════════════

class TestUnmatchableKeywordExclusion:
    """fix(omni-g-fintech 组级②): 含空格/顿号关键词从权重宇宙剔除并披露."""

    def test_partition_is_exact_and_consistent(self):
        matchable, unmatchable = fi._ensure_keywords_injected()
        assert len(matchable) + len(unmatchable) == len(fi.FINTECH_KEYWORDS)
        assert not (set(matchable) & set(unmatchable))
        # 永不可匹配判据: 注入后 jieba 仍无法将其切为单 token
        import jieba
        for kw in unmatchable:
            assert list(jieba.cut(kw)) != [kw], (
                f'{kw!r} 实际可整词匹配, 不应被剔除')

    def test_known_six_unmatchable_on_current_dict(self):
        # 当前词典实证 (2026-06-11): 恰 6 词, 全部含空格/顿号块切分边界字符
        _, unmatchable = fi._ensure_keywords_injected()
        expected = {'Open Banking', 'ISO 20022', 'Swift GPI',
                    'MSCI ESG', 'MiFID II', '治理、风险与合规'}
        if not expected <= set(fi.FINTECH_KEYWORDS):
            pytest.skip('词典已变更, 6 词实证锁不再适用')
        assert set(unmatchable) == expected

    def test_disclosure_warning_emitted(self, monkeypatch):
        class _Rec:
            def __init__(self):
                self.warnings = []

            def warning(self, msg, *a, **k):
                self.warnings.append(str(msg))

            def info(self, msg, *a, **k):
                pass

            def error(self, msg, *a, **k):
                pass

        rec = _Rec()
        monkeypatch.setattr(fi, 'logger', rec)
        # 重置进程内缓存, 强制重跑划分 + 披露
        monkeypatch.setitem(fi._KW_STATE, 'injected', False)
        monkeypatch.setitem(fi._KW_STATE, 'matchable', None)
        monkeypatch.setitem(fi._KW_STATE, 'unmatchable', None)
        _, unmatchable = fi._ensure_keywords_injected()
        if not unmatchable:
            pytest.skip('当前词典无不可匹配词, 无披露可断言')
        disclosed = [m for m in rec.warnings if '词典披露' in m]
        assert disclosed, '剔除发生但无 WARNING 披露'
        assert all(kw in disclosed[0] for kw in unmatchable), (
            '披露文本须逐词列出被剔除关键词')

    def test_weight_universe_excludes_unmatchable(self, monkeypatch):
        _require_kws('区块链')
        # v3.14.0 (all-API-embedding): 本地 sentence_transformers 路径已彻底移除,
        # 关键词语义编码改走统一引擎 _eng.embed_texts(spec) 纯 API 路径。mock 该
        # 函数返回确定性 fake 向量 (3072 维) 以隔离网络/缓存依赖, 只验权重宇宙。
        def _fake_embed(kw_list, spec, **kwargs):
            kw_list = list(kw_list)
            rng = np.random.default_rng(0)
            return rng.normal(size=(len(kw_list), 3072)).astype(np.float32)

        monkeypatch.setattr(fi._eng, 'embed_texts', _fake_embed)
        matchable, unmatchable = fi._ensure_keywords_injected()
        weights = fi._build_intensity_weights(Counter({'区块链': 5}), 10)
        assert set(weights) == set(matchable)
        for kw in unmatchable:
            assert kw not in weights

    def test_degraded_fallback_universe_also_matchable_only(self):
        # DF 为空降级支: 全 1.0 权重宇宙同样不含不可匹配词
        # (DF 为空 → 提前 return, 不触发任何嵌入路径, 无需 mock embed_texts)
        matchable, _ = fi._ensure_keywords_injected()
        weights = fi._build_intensity_weights(Counter(), 0)
        assert set(weights) == set(matchable)

    def test_centroid_kw_list_excludes_unmatchable(self, monkeypatch):
        _require_kws('区块链', '云计算')
        recorded = {}

        # v3.14.0: 关键词嵌入宇宙现经 _eng.embed_texts(kw_list, spec) 传入 (零本地模型);
        # mock 该函数记录实际传入的 kw_list, 验证幻影 (不可匹配) 词不进质心嵌入宇宙。
        def _fake_embed(kw_list, spec, **kwargs):
            recorded['kws'] = list(kw_list)
            rng = np.random.default_rng(0)
            return rng.normal(size=(len(kw_list), 3072)).astype(np.float32)

        monkeypatch.setattr(fi._eng, 'embed_texts', _fake_embed)
        matchable, unmatchable = fi._ensure_keywords_injected()
        weights = fi._build_intensity_weights(
            Counter({'区块链': 3, '云计算': 1}), 10)
        # 质心嵌入宇宙 = matchable (幻影词不进质心 / CosSim min-max 缩放)
        assert set(recorded['kws']) == set(matchable)
        for kw in unmatchable:
            assert kw not in recorded['kws']
        assert set(weights) == set(matchable)


# ════════════════════════════════════════════════════════════════════════
# g-fintech-03: DF 与 TF 同分词器 (jieba 整词替换 AC 子串计数源)
# ════════════════════════════════════════════════════════════════════════

class TestGlobalDFJiebaSameTokenizer:
    """fix(omni-g-fintech-03): DF 统计与 TF 同分词器 — jieba 整词, 非 AC 子串."""

    def test_substring_and_overlap_hits_not_counted(self):
        # 审计句: AC 计 3 词 (网贷子串 + 大数据/数据风控重叠双计),
        # jieba 整词口径只允许 1 词 (数据风控) 进 DF
        _require_kws('网贷', '大数据', '数据风控')
        df = pd.DataFrame({'内容': [_AUDIT_SENTENCE]})
        freq, n = fi._compute_global_df_jieba(df, text_col='内容')
        assert n == 1
        assert freq.get('网贷', 0) == 0, "子串误命中 ('网贷'∈'互联网贷款') 不得进 DF"
        assert freq.get('大数据', 0) == 0, "重叠双计 ('大数据'+'数据风控') 不得进 DF"
        assert freq.get('数据风控', 0) == 1

    def test_whole_word_hits_counted_once_per_doc(self):
        _require_kws('区块链', '云计算')
        df = pd.DataFrame({'内容': ['区块链区块链与云计算', '区块链技术应用广泛']})
        freq, n = fi._compute_global_df_jieba(df, text_col='内容')
        assert n == 2
        assert freq.get('区块链', 0) == 2  # 文档频率: 同篇多次只计 1
        assert freq.get('云计算', 0) == 1

    def test_text_col_missing_falls_back_to_content(self):
        _require_kws('区块链')
        df = pd.DataFrame({'内容': ['区块链技术应用广泛']})
        freq, n = fi._compute_global_df_jieba(df, text_col='content_full')
        assert n == 1
        assert freq.get('区块链', 0) == 1

    def test_ac_substring_source_fully_replaced(self):
        # 源码文本锁: AC 计数源 (_parse_global_df 的 fintech_keyword_details
        # JSON 消费) 已被 jieba 重算替换, 防静默 revert。
        # 注: '_parse_global_df'/'fintech_keyword_details' 词面仍允许出现在修复
        # 说明 docstring 中 (历史披露), 锁的是定义与消费代码模式本身。
        assert 'def _parse_global_df' not in _SRC
        assert "df_full['fintech_keyword_details']" not in _SRC
        assert 'json.loads' not in _SRC
        assert 'def _compute_global_df_jieba' in _SRC
        assert 'fix(omni-g-fintech-03' in _SRC

    def test_main_df_corpus_is_full_corpus_with_materialized_title(self):
        # 源码文本锁: main() 的 DF 参考语料 = stage 12 全量 (含非金融科技,
        # GKT "full reference corpus") + 在线物化 content_full (prepend_title
        # 单源, 与 TF 打分文本同语义)。⚠ 防回归: 14_news_with_ctx 盘上实证仅含
        # is_fintech_news=True 子集 (1170/4054), 绝不可用作 IDF 参考语料。
        assert 'df_ref = pd.read_parquet(full_path)' in _SRC
        assert '_materialize_df_corpus_column(df_ref)' in _SRC
        assert '_compute_global_df_jieba(df_ref, text_col=ref_text_col)' in _SRC
        # DF 段 (main 内 '加载 IDF 参考语料' 至权重构建之间) 不得读 ctx 文件
        _df_block = _SRC.split('加载 IDF 参考语料')[1].split(
            'combined_weights = _build_intensity_weights')[0]
        assert 'read_parquet(ctx_path)' not in _df_block

    def test_materialize_corpus_column_prepends_title(self):
        # 功能锁: 标题词须进 DF 语料 (tone_words "标题词 df 被低估" 同型修复)
        _require_kws('区块链', '云计算')
        df = pd.DataFrame({
            '标题': ['区块链新政发布'],   # 关键词只在标题
            '日期': ['2017-01-01'],
            '内容': ['云计算服务稳步推进'],
        })
        df2, col = fi._materialize_df_corpus_column(df)
        assert col == 'content_full'
        freq, n = fi._compute_global_df_jieba(df2, text_col=col)
        assert n == 1
        assert freq.get('区块链', 0) == 1, '仅标题出现的关键词须计入 DF'
        assert freq.get('云计算', 0) == 1
        # 调用方 frame 不被污染 (assign 浅拷贝)
        assert 'content_full' not in df.columns

    def test_materialize_corpus_column_passthrough_and_fallback(self):
        # 已有 content_full → 原样直通; 缺标题/内容 → 回退 '内容'
        df_a = pd.DataFrame({'content_full': ['x'], '内容': ['y']})
        out_a, col_a = fi._materialize_df_corpus_column(df_a)
        assert col_a == 'content_full' and out_a is df_a
        df_b = pd.DataFrame({'内容': ['y']})
        out_b, col_b = fi._materialize_df_corpus_column(df_b)
        assert col_b == '内容' and out_b is df_b

    def test_injection_single_source_shared_by_df_and_tf(self):
        # DF (_compute_global_df_jieba)、权重 (_build_intensity_weights)、
        # TF (_compute_intensity_scores) 三处共用同一注入态 helper
        assert _SRC.count('_ensure_keywords_injected()') >= 3

    def test_lineage_contract_string_preserved(self):
        # 既有锁 (test_lineage_input_contract) 依赖的字面量未被重构破坏
        assert 'input_files=[full_path, _primary_src]' in _SRC


# ════════════════════════════════════════════════════════════════════════
# g-fintech-01: IDF 参考语料唯一文档去重
# ════════════════════════════════════════════════════════════════════════

class TestGlobalDFUniqueDocDedup:
    """fix(omni-g-fintech-01): DF/N_total 按唯一文档 (标题,日期) 统计."""

    def test_multibank_explosion_rows_counted_once(self):
        _require_kws('数据风控', '区块链', '云计算')
        df = pd.DataFrame({
            '标题': ['t1', 't1', 't1', 't2'],  # t1 三行 = 同文配 3 银行爆炸行
            '日期': ['2017-01-01'] * 3 + ['2017-01-02'],
            '内容': [_AUDIT_SENTENCE] * 3 + ['区块链与云计算赋能银行数字化转型'],
        })
        freq, n = fi._compute_global_df_jieba(df, text_col='内容')
        assert n == 2, 'N_total 须为唯一文档数 (旧实现: 4)'
        assert freq.get('数据风控', 0) == 1, '同文档 DF 不得计 k 次 (旧实现: 3)'
        assert freq.get('区块链', 0) == 1

    def test_same_title_different_date_are_distinct_docs(self):
        _require_kws('区块链')
        df = pd.DataFrame({
            '标题': ['t1', 't1'],
            '日期': ['2017-01-01', '2018-01-01'],
            '内容': ['区块链技术应用广泛'] * 2,
        })
        freq, n = fi._compute_global_df_jieba(df, text_col='内容')
        assert n == 2
        assert freq.get('区块链', 0) == 2

    def test_fallback_dedup_on_text_when_no_title_date(self):
        _require_kws('区块链')
        df = pd.DataFrame({'内容': ['区块链技术应用广泛'] * 3 + ['云计算服务']})
        freq, n = fi._compute_global_df_jieba(df, text_col='内容')
        assert n == 2, '缺 (标题,日期) 列时回退文本自身为唯一键'
        assert freq.get('区块链', 0) == 1

    def test_empty_corpus_returns_zero(self):
        freq, n = fi._compute_global_df_jieba(
            pd.DataFrame({'内容': []}), text_col='内容')
        assert n == 0
        assert len(freq) == 0


# ════════════════════════════════════════════════════════════════════════
# 组级裁决①: 二次熔断零填改 NaN (avg_ft_intensity 均值分母修复)
# ════════════════════════════════════════════════════════════════════════

class TestFusedNaNNotZero:
    """fix(omni-g-fintech 组级①): 熔断文章得分 = NaN, 不再污染均值分母."""

    @staticmethod
    def _scores(texts):
        if fi.MIN_DISTINCT_KEYWORDS_JIEBA < 2:
            pytest.skip('min_distinct_keywords_jieba < 2, 熔断场景不成立')
        weights = {'区块链': 1.0, '云计算': 1.0, '银行数字化': 1.0}
        return fi._compute_intensity_scores(
            pd.DataFrame({'内容': texts}), weights)

    def test_fused_doc_score_is_nan_verified_false(self):
        _require_kws('区块链', '云计算')
        scores, verified = self._scores(
            ['区块链技术应用广泛',              # 1 distinct < 2 → 熔断
             '区块链与云计算赋能银行数字化转型'])  # ≥2 distinct → verified
        assert math.isnan(scores[0]), '熔断得分须为 NaN (旧行为: 0.0 污染均值分母)'
        assert verified[0] is False
        assert scores[1] > 0
        assert verified[1] is True

    def test_downstream_mean_denominator_excludes_fused(self):
        _require_kws('区块链', '云计算')
        scores, _ = self._scores(
            ['区块链技术应用广泛', '区块链与云计算赋能银行数字化转型'])
        # 模拟 encode.py: agg['avg_ft_intensity*'] = (col, 'mean')
        panel = pd.DataFrame({'bank': ['A', 'A'],
                              'fintech_intensity_score_full': scores})
        avg = panel.groupby('bank').agg(
            avg=('fintech_intensity_score_full', 'mean'))['avg'].iloc[0]
        assert avg == pytest.approx(scores[1]), (
            '均值分母须只含 verified 文章 (旧 0 填行为: avg 被腰斩为 score/2)')

    def test_sum_semantics_unchanged(self):
        _require_kws('区块链', '云计算')
        scores, _ = self._scores(
            ['区块链技术应用广泛', '区块链与云计算赋能银行数字化转型'])
        # attention_media.py sum_* / codebook ln_sum_*: NaN 在 pandas sum
        # (skipna 默认) 中视同 0 → 熔断文章贡献 0, 与旧行为一致
        assert pd.Series(scores).sum() == pytest.approx(scores[1])

    def test_all_fused_bank_year_mean_is_missing_not_zero(self):
        _require_kws('区块链')
        scores, verified = self._scores(['区块链技术应用广泛'] * 2)
        assert all(math.isnan(s) for s in scores)
        assert not any(verified)
        # 全熔断 bank-year: avg 为缺失 (NaN) 而非伪零 — 信息性缺失披露
        assert math.isnan(pd.Series(scores).mean())


# ════════════════════════════════════════════════════════════════════════
# g-fintech-02: SIF / Arora / Ethayarajh 引用名实不符 — 源码文本锁
# ════════════════════════════════════════════════════════════════════════

class TestCitationDowngradeSourceLock:
    """fix(omni-g-fintech-02): 'SIF 加权质心' 改述 + 引用降格 (防静默 revert)."""

    def test_sif_claim_rephrased_as_idf_weighted_centroid(self):
        assert 'IDF 加权质心' in _SRC
        assert 'IDF-weighted keyword embedding centroid' in _SRC
        # 旧的名实不符措辞不得复活
        assert 'SIF 词向量质心' not in _SRC
        assert 'SIF 加权质心 + 各向异性校准' not in _SRC

    def test_arora_citation_downgraded_to_inspiration(self):
        assert 'Arora' in _SRC  # 引用保留但降格
        assert '非 SIF 实现' in _SRC
        assert 'a/(a+p(w))' in _SRC  # 明示缺失的 SIF 定义性要素
        assert '首主成分' in _SRC
        assert 'fix(omni-g-fintech-02' in _SRC

    def test_ethayarajh_citation_downgraded_to_motivation(self):
        assert 'Ethayarajh' in _SRC
        assert '动机引用' in _SRC
        assert '非该文提出的校准方法' in _SRC

    def test_implementation_unchanged_idf_weighted_average(self):
        # 措辞修正不动数值: IDF 加权平均质心实现保持原样
        assert 'np.average(embeddings, axis=0, weights=weights_arr)' in _SRC
