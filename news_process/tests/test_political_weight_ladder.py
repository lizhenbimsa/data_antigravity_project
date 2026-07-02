"""政治词权重敏感性梯度 (political-weight sensitivity, du_2022 only) 测试。

Du et al. (2022, Review of Finance) 的 political_positive(1,434 词) 生产口径以 0.5 权重计入
正侧; 0.5 为研究者选择, 故并排物化政治词权重 ∈ {0.0, 0.5, 1.0} 三者**互为稳健性、不分主次**
(polw05 ≡ canonical du_2022_score/du_2022_tone)。覆盖:
  · 变体谱 SSOT + 跨模块 suffix 同步 (tone_words ↔ encode) + 两句话依据字符串
  · 变体词典构造 (polw00 剔除政治词 / polw10 全权 / polw05 恒等 base) + id 缓存
  · polw05 与 du_2022_score 字节一致; 三权重在极性对冲文本上取值互异 (jieba-free 引擎级)
  · du_2022-only scoping (其余 5 词典不产 polw 列, article + panel 两级)
  · article → panel 全列存在 + 32 字符 + 空文本 NaN + 三轨提取
  · rule-ablation 与 political-weight 两轴正交 (matcher 互斥)
  · stata 标签 (≤80 字节, 非 fallback) + codebook 推断 (label / source-stage / SSOT 覆盖)
"""
import pandas as pd
import pytest

from news_process.pipeline.panel import codebook as cb
from news_process.pipeline.panel import encode as enc
from news_process.pipeline.panel import stata_export as se
from news_process.pipeline.sentiment import tone_words as tone

SUFFIXES = ['polw00', 'polw05', 'polw10']
TRACKS = ('_full', '_ctx', '_ss')
OTHER_DICTS = ['jiang_2021', 'yao_2021', 'bian_2021', 'you_2018', 'loughran']


class TestVariantSpec:
    def test_suffixes_and_weights(self):
        assert tone.POLITICAL_WEIGHT_SUFFIXES == SUFFIXES
        assert [w for _, w in tone.POLITICAL_WEIGHT_VARIANTS] == [0.0, 0.5, 1.0]

    def test_only_du_2022_carries_political(self):
        assert set(tone.POLITICAL_WEIGHT_DICTS) == {'du_2022'}

    def test_cross_module_suffix_sync(self):
        # 不一致会致 encode 聚合静默漏列 → panel 全 NaN
        assert enc.POLITICAL_WEIGHT_SUFFIXES == tone.POLITICAL_WEIGHT_SUFFIXES
        # set-equal (非仅成员): encode 侧列表口径须与 tone 侧 frozenset 完全同集,
        # 未来新增第二部政治词典时防 encode 单侧漏聚合。
        assert set(enc.POLITICAL_WEIGHT_DICTS) == set(tone.POLITICAL_WEIGHT_DICTS)

    def test_rationale_two_sentences(self):
        r = tone.POLITICAL_WEIGHT_RATIONALE
        assert 'Du et al. (2022' in r and 'Review of Finance' in r
        assert '不分主次' in r and '{0.0, 0.5, 1.0}' in r


class TestVariantDict:
    BASE = {'好': 1.0, '差': -1.0, '政治': 0.5, '重叠': 1.0}  # 政治=0.5 唯一政治词

    def test_polw00_drops_political(self):
        v = tone._political_variant_dict(dict(self.BASE), 'polw00', 0.0)
        assert '政治' not in v
        assert v['好'] == 1.0 and v['差'] == -1.0 and v['重叠'] == 1.0

    def test_polw10_full_weight(self):
        v = tone._political_variant_dict(dict(self.BASE), 'polw10', 1.0)
        assert v['政治'] == 1.0
        assert v['好'] == 1.0 and v['差'] == -1.0

    def test_polw05_identity(self):
        base = dict(self.BASE)
        assert tone._political_variant_dict(base, 'polw05', 0.5) == base

    def test_cache_returns_same_object(self):
        base = dict(self.BASE)
        a = tone._political_variant_dict(base, 'polw00', 0.0)
        b = tone._political_variant_dict(base, 'polw00', 0.0)
        assert a is b  # 按 (id(base), suffix) 缓存, 不逐篇重建

    def test_non_political_dict_unchanged(self):
        base = {'好': 1.0, '差': -1.0}  # 无 0.5 词
        for sfx, w in [('polw00', 0.0), ('polw10', 1.0)]:
            assert tone._political_variant_dict(dict(base), sfx, w) == base


class TestEngineDistinct:
    """极性对冲文本上三权重归一化取值互异 (jieba-free, 直接以变体词典调引擎)。"""

    def test_three_weights_distinct(self):
        base = {'政治': 0.5, '差': -1.0}
        toks = ['政治', '差']
        d00 = tone._political_variant_dict(base, 'polw00', 0.0)
        d10 = tone._political_variant_dict(base, 'polw10', 1.0)
        s00 = tone._compute_sentiment_with_rules(toks, d00)[1]
        s05 = tone._compute_sentiment_with_rules(toks, base)[1]
        s10 = tone._compute_sentiment_with_rules(toks, d10)[1]
        assert s00 == pytest.approx(-1.0)      # 政治词剔除 → 仅 差
        assert s05 == pytest.approx(-1 / 3)    # (0.5 − 1.0) / 1.5
        assert s10 == pytest.approx(0.0)       # (1.0 − 1.0) / 2.0
        assert len({round(s00, 4), round(s05, 4), round(s10, 4)}) == 3


class _DuFixture:
    @pytest.fixture(autouse=True)
    def _setup(self, monkeypatch):
        monkeypatch.setattr(tone, 'ALL_DICTIONARIES', [
            ('du_2022', {'好': 1.0, '差': -1.0, '政治': 0.5}),
            ('jiang_2021', {'好': 1.0, '差': -1.0}),
        ])
        monkeypatch.setattr(tone, 'IDF_DICTIONARIES', None)
        monkeypatch.setattr(tone, '_UNION_DICT_CACHE', None)
        tone._POLW_DICT_CACHE.clear()


class TestArticleColumns(_DuFixture):
    def test_du_gets_all_polw_columns(self):
        res = tone._analyze_single_article('政治 差 好 。')
        for sfx in SUFFIXES:
            assert f'du_2022_score_{sfx}' in res, f"缺 du_2022_score_{sfx}"
        assert 'du_2022_score' in res  # canonical 主列仍在

    def test_polw05_byte_identical_to_score(self):
        # polw05 与 canonical du_2022_score 同词典同规则 → 恒相等 (与 token 化无关)
        res = tone._analyze_single_article('政治 差 好 但是 差 。')
        assert res['du_2022_score_polw05'] == res['du_2022_score']

    def test_other_dict_no_polw_columns(self):
        res = tone._analyze_single_article('政治 差 。')
        for sfx in SUFFIXES:
            assert f'jiang_2021_score_{sfx}' not in res

    def test_empty_text_polw_nan(self):
        res = tone._analyze_single_article('')
        for sfx in SUFFIXES:
            assert pd.isna(res[f'du_2022_score_{sfx}']), f"du_2022_score_{sfx} 空文本应 NaN"


class TestClassifyBatchExtraction(_DuFixture):
    def test_du_three_tracks_extracted(self):
        df = pd.DataFrame({
            '标题': [''], '内容': ['政治 差 好 。'],
            'content_ctx': ['好 。'], 'content_ss': ['差 。'],
        })
        out, _ = tone.classify_batch(df)
        for sfx in SUFFIXES:
            for tk in TRACKS:
                assert f'du_2022_score_{sfx}{tk}' in out.columns, \
                    f"classify_batch 漏 du_2022_score_{sfx}{tk}"

    def test_other_dict_no_polw_tracks(self):
        df = pd.DataFrame({
            '标题': [''], '内容': ['政治 差 好 。'],
            'content_ctx': ['好 。'], 'content_ss': ['差 。'],
        })
        out, _ = tone.classify_batch(df)
        for sfx in SUFFIXES:
            for tk in TRACKS:
                assert f'jiang_2021_score_{sfx}{tk}' not in out.columns

    def test_polw05_equals_canonical_across_batch(self):
        # Gap-2 (panel 前置锁): 批处理后, 三轨 polw05 列须逐行等于 canonical du_2022_score 列
        # (agg 对二者施同一 mean → panel du_2022_polw05_tone ≡ du_2022_tone 传递成立)。
        df = pd.DataFrame({
            '标题': ['银行 金科'], '内容': ['政治 差 好 但是 差 。', '政治 好 。'][:1] * 1,
            'content_ctx': ['好 差 。'], 'content_ss': ['差 政治 。'],
        })
        out, _ = tone.classify_batch(df)
        for tk in TRACKS:
            assert (out[f'du_2022_score_polw05{tk}'] == out[f'du_2022_score{tk}']).all(), \
                f"polw05 与 canonical du_2022_score 在 {tk} 轨批处理下不逐行相等"


class TestPanelAggregation:
    def test_du_polw_panel_cols_present(self):
        agg = enc.build_aggregation_dict()
        for sfx in SUFFIXES:
            for tk in TRACKS:
                pcol = f'du_2022_{sfx}_tone{tk}'
                assert pcol in agg, f"panel agg 缺 {pcol}"
                assert agg[pcol] == (f'du_2022_score_{sfx}{tk}', 'mean')

    def test_other_dicts_no_polw_panel_cols(self):
        agg = enc.build_aggregation_dict()
        for d in OTHER_DICTS:
            for sfx in SUFFIXES:
                for tk in TRACKS:
                    assert f'{d}_{sfx}_tone{tk}' not in agg, \
                        f"非 du_2022 词典 {d} 误产政治词权重列"

    def test_panel_names_within_32_chars(self):
        for sfx in SUFFIXES:
            for tk in TRACKS:
                name = f'du_2022_{sfx}_tone{tk}'
                assert len(name) <= 32, f"{name} = {len(name)} 字符 > 32"


class TestAxisOrthogonality:
    """rule-ablation 与 political-weight 两轴 matcher 互斥 (禁串味)。"""

    def test_matchers_disjoint(self):
        # 政治词列不被 rule-ablation matcher 认领
        assert cb._rule_ablation_match('du_2022_polw00_tone_full') is None
        # 规则消融列不被 political matcher 认领
        assert cb._political_weight_match('du_2022_raw_tone_full') is None
        assert cb._political_weight_match('du_2022_negonly_tone_ss') is None


class TestStataLabels:
    def test_polw_labels_non_fallback(self):
        cols = [f'du_2022_{sfx}_tone_{tk}'
                for sfx in SUFFIXES for tk in ('full', 'ctx', 'ss')]
        labels = se.build_variable_labels(pd.DataFrame({c: [0.0] for c in cols}))
        for c in cols:
            assert c in labels and labels[c].strip(), f"{c} 无标签"
            assert labels[c] != c, f"{c} 退化为列名 fallback"
            assert len(labels[c].encode('utf-8')) <= 80, \
                f"{c} 标签 {len(labels[c].encode('utf-8'))} > 80 字节"


class TestCodebookInference:
    def test_political_weight_match(self):
        assert cb._political_weight_match('du_2022_polw00_tone_full') == ('du_2022', 'polw00')
        assert cb._political_weight_match('du_2022_polw05_tone_ctx') == ('du_2022', 'polw05')
        assert cb._political_weight_match('du_2022_polw10_tone_ss') == ('du_2022', 'polw10')
        assert cb._political_weight_match('du_2022_tone_full') is None       # canonical 主列
        assert cb._political_weight_match('jiang_2021_polw00_tone_full') is None  # 非 du_2022

    def test_infer_label_political_specific(self):
        lbl = cb._infer_label('du_2022_polw10_tone_full')
        assert 'du_2022' in lbl and '政治词权重' in lbl
        # 泛型 tone 列不被政治分支吞掉, 且与 canonical 主列标签相异
        assert cb._infer_label('du_2022_polw10_tone_full') != cb._infer_label('du_2022_tone_full')

    def test_infer_source_stage(self):
        for sfx in SUFFIXES:
            assert cb._infer_source_stage(f'du_2022_{sfx}_tone_full') == 'Stage 22'

    def test_sfx_desc_covers_ssot(self):
        missing = set(tone.POLITICAL_WEIGHT_SUFFIXES) - set(cb._POLITICAL_WEIGHT_SFX_DESC)
        assert not missing, f"codebook._POLITICAL_WEIGHT_SFX_DESC 缺变体 {missing}"

    def test_regex_matches_every_ssot_variant(self):
        for sfx in tone.POLITICAL_WEIGHT_SUFFIXES:
            for tk in ('full', 'ctx', 'ss'):
                assert cb._political_weight_match(f'du_2022_{sfx}_tone_{tk}') == ('du_2022', sfx)


class TestGeographyNoPolwRollup:
    """Gap-1 (承重负向防线): geography 跨词典均值 dict_avg 绝不卷入政治词权重 polw 列 —
    守 'polw 禁入跨词典均值 / 同一 over-identified Hansen J' 的唯一未测防线。
    面板结构镜像 test_rule_ablation_ladder.TestCrossDictRollup._panel + 注入 polw 列。"""
    ALL_VARIANTS = ['raw', 'negonly', 'degonly', 'advonly', 'negdeg', 'negadv', 'degadv']
    DICTS = ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018', 'loughran']

    def _panel_with_polw(self):
        cols = {'target_bank': ['A', 'B'], 'year': [2017, 2018], 'n_articles': [10, 10]}
        for d in self.DICTS:
            for s in self.ALL_VARIANTS:
                for t in TRACKS:
                    cols[f'{d}_{s}_tone{t}'] = [0.5, -0.5]
        # 注入政治词权重列 (du_2022 独有) — 检验 geography 是否会误卷入
        for s in SUFFIXES:
            for t in TRACKS:
                cols[f'du_2022_{s}_tone{t}'] = [0.5, -0.5]
        return pd.DataFrame(cols)

    def test_geography_excludes_polw_from_dict_avg(self):
        from news_process.pipeline.panel import geography as geo
        out = geo.compute_composite_indicators(self._panel_with_polw())
        polw_avg = [c for c in out.columns if c.startswith('dict_avg') and 'polw' in c]
        assert not polw_avg, f"geography 误把政治词权重卷入跨词典均值: {polw_avg}"
        # 正向健全: 既有 dict_avg 规则消融 roll-up 仍在 → 确认 roll-up 路径确已执行
        assert 'dict_avg_negonly_tone_full' in out.columns
