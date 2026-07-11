"""规则消融梯度 (rule-ablation ladder, v3.11.1) 测试。

逐 token 状态机三规则 (① 否定窗口 / ② 程度副词六级权重 / ③ 转折增强) 的**全 powerset**
中间变量稳健性梯度。覆盖:
  · 变体谱完整性 + 跨模块 suffix 同步 (tone_words ↔ encode)
  · apply_negation gating + 向后兼容 (默认 True → 现有 call site 字节不变)
  · 退化不变量 (无否定词 → raw == negonly; 计数口径 msent **不入**梯度)
  · article → panel 全列存在 + 32 字符合规
  · stata 标签覆盖 (≤80 字节) + codebook rule-specific 推断
"""
import pandas as pd
import pytest

from news_process.pipeline.panel import codebook as cb
from news_process.pipeline.panel import encode as enc
from news_process.pipeline.panel import stata_export as se
from news_process.pipeline.sentiment import tone_words as tone

DICTS = ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018', 'loughran']
ALL_VARIANTS = ['raw', 'negonly', 'degonly', 'advonly', 'negdeg', 'negadv', 'degadv']
NEW_VARIANTS = ['raw', 'degonly', 'advonly', 'negdeg', 'negadv', 'degadv']  # negonly 已存在
TRACKS = ('_full', '_ctx', '_ss')


class TestVariantSpec:
    def test_suffix_set_is_full_powerset_minus_full(self):
        assert tone.RULE_ABLATION_SUFFIXES == ALL_VARIANTS
        combos = {(n, d, a) for _, n, d, a in tone._RULE_ABLATION_VARIANTS}
        assert len(tone._RULE_ABLATION_VARIANTS) == 7
        assert len(combos) == 7  # 全部 distinct
        assert (True, True, True) not in combos   # full 单独物化为 {dict}_score
        assert (False, False, False) in combos    # raw 零规则基线
        spec = {s: (n, d, a) for s, n, d, a in tone._RULE_ABLATION_VARIANTS}
        assert spec['negonly'] == (True, False, False)
        assert spec['raw'] == (False, False, False)
        assert spec['degadv'] == (False, True, True)  # = full − negation (LOO)

    def test_cross_module_suffix_sync(self):
        # 不一致会致 encode 聚合静默漏列 → panel 全 NaN
        assert enc.RULE_ABLATION_SUFFIXES == tone.RULE_ABLATION_SUFFIXES


class TestEngineApplyNegation:
    def test_apply_negation_gates_flip(self):
        sd = {'乐观': 1.0}
        toks = ['不', '乐观']
        raw = tone._compute_sentiment_with_rules(
            toks, sd, apply_negation=False, apply_degree=False, apply_adversative=False)
        negonly = tone._compute_sentiment_with_rules(
            toks, sd, apply_negation=True, apply_degree=False, apply_adversative=False)
        assert raw[1] == pytest.approx(1.0)       # 不翻号
        assert negonly[1] == pytest.approx(-1.0)  # 翻号

    def test_default_apply_negation_true_backward_compat(self):
        # 不传 apply_negation = True → 现有 5 个 call site 行为字节不变
        sd = {'乐观': 1.0}
        toks = ['不', '乐观']
        default = tone._compute_sentiment_with_rules(toks, sd, apply_degree=False, apply_adversative=False)
        explicit = tone._compute_sentiment_with_rules(
            toks, sd, apply_negation=True, apply_degree=False, apply_adversative=False)
        assert default == explicit

    def test_no_negation_word_raw_equals_negonly(self):
        sd = {'乐观': 1.0, '差': -1.0}
        toks = ['乐观', '差', '好']  # 无否定词
        raw = tone._compute_sentiment_with_rules(
            toks, sd, apply_negation=False, apply_degree=False, apply_adversative=False)
        negonly = tone._compute_sentiment_with_rules(
            toks, sd, apply_negation=True, apply_degree=False, apply_adversative=False)
        assert raw == negonly

    def test_negation_window_consumed_even_when_flip_off(self):
        # 骨架共享铁律: apply_negation=False 仍走否定词识别+continue+窗口递减 →
        # 否定窗口外的程度词作用域不被污染 (与全规则同 scoping)。
        sd = {'乐观': 1.0}
        toks = ['不', '填', '乐观']  # window=2 覆盖 distance-2 → negonly 翻号
        negonly = tone._compute_sentiment_with_rules(
            toks, sd, apply_negation=True, apply_degree=False, apply_adversative=False)
        assert negonly[1] == pytest.approx(-1.0)

    def test_degree_changes_magnitude_score(self):
        sd = {'乐观': 1.0, '差': -1.0}
        toks = ['非常', '乐观', '但是', '差']  # 非常=2.5; 但是 boost 差
        full = tone._compute_sentiment_with_rules(
            toks, sd, apply_negation=True, apply_degree=True, apply_adversative=True)
        no_degree = tone._compute_sentiment_with_rules(
            toks, sd, apply_negation=True, apply_degree=False, apply_adversative=True)
        assert abs(full[1] - no_degree[1]) > 1e-9

    def test_negation_degree_interaction_on_total(self):
        # 否定×程度交互 (MATH-1 crux): '不 非常 乐观' → 程度 2.5 作用于翻转后的幅度。
        # 用 raw_score (total, 单词归一化恒 ±1 故看 total) 精确锁四变体的交互值。
        sd = {'乐观': 1.0}
        toks = ['不', '非常', '乐观']  # 不→翻转窗口; 非常=2.5; 乐观=+1
        full = tone._compute_sentiment_with_rules(
            toks, sd, apply_negation=True, apply_degree=True, apply_adversative=False)
        raw = tone._compute_sentiment_with_rules(
            toks, sd, apply_negation=False, apply_degree=False, apply_adversative=False)
        negonly = tone._compute_sentiment_with_rules(
            toks, sd, apply_negation=True, apply_degree=False, apply_adversative=False)
        degonly = tone._compute_sentiment_with_rules(
            toks, sd, apply_negation=False, apply_degree=True, apply_adversative=False)
        assert full[0] == pytest.approx(-2.5)     # 2.5 × (−1): 否定×程度交互
        assert raw[0] == pytest.approx(1.0)        # 零规则
        assert negonly[0] == pytest.approx(-1.0)   # 仅翻转
        assert degonly[0] == pytest.approx(2.5)    # 仅程度 (不翻转)
        # 显式 gate 回归: 文本含否定词时 raw 与 negonly 必不同
        assert raw[1] != negonly[1]


class _DictFixture:
    @pytest.fixture(autouse=True)
    def _setup(self, monkeypatch):
        monkeypatch.setattr(tone, 'ALL_DICTIONARIES', [('a', {'好': 1.0, '差': -1.0})])
        monkeypatch.setattr(tone, 'IDF_DICTIONARIES', None)
        monkeypatch.setattr(tone, '_UNION_DICT_CACHE', None)


class TestArticleLadderColumns(_DictFixture):
    def test_all_ablation_columns_present(self):
        res = tone._analyze_single_article('业绩 非常 好 但是 差 。')
        for sfx in ALL_VARIANTS:
            assert f'a_score_{sfx}' in res, f"缺 a_score_{sfx}"
        assert 'a_score' in res  # full 主列仍在

    def test_msent_count_ladder_not_extended(self):
        # 计数口径 msent 不入梯度 (程度/转折严格正乘子永不翻号 → 退化)
        res = tone._analyze_single_article('业绩 非常 好 但是 差 。')
        msent_keys = {k for k in res if k.startswith('msent')}
        assert msent_keys == {'msent_score', 'msent_negonly'}, f"msent 口径被错误扩展: {msent_keys}"

    def test_empty_text_ablation_nan(self):
        res = tone._analyze_single_article('')
        for sfx in ALL_VARIANTS:
            assert pd.isna(res[f'a_score_{sfx}']), f"a_score_{sfx} 空文本应 NaN"

    def test_negonly_byte_stable_via_loop(self):
        # negonly 经梯度 loop 物化的值 == 直接以 (T,F,F) 调引擎 (golden-safe 折入)
        text = '不 好 业绩 非常 差 但是 好 。'
        res = tone._analyze_single_article(text)
        toks = [t for t in tone._get_tone_tokenizer().cut(text) if t.strip()]
        _, direct, _, _, _ = tone._compute_sentiment_with_rules(
            toks, {'好': 1.0, '差': -1.0}, apply_negation=True, apply_degree=False, apply_adversative=False)
        assert res['a_score_negonly'] == pytest.approx(round(direct, 4))


class TestClassifyBatchExtraction(_DictFixture):
    def test_all_variants_three_tracks_extracted(self):
        df = pd.DataFrame({
            '标题': [''], '内容': ['不 好 业绩 非常 差 。'],
            'content_ctx': ['业绩 非常 好 。'], 'content_ss': ['不 差 。'],
        })
        out, _ = tone.classify_batch(df)
        for sfx in ALL_VARIANTS:
            for tk in TRACKS:
                assert f'a_score_{sfx}{tk}' in out.columns, f"classify_batch 漏 a_score_{sfx}{tk}"


class TestPanelAggregation:
    def test_build_aggregation_dict_has_all_ladder_panel_cols(self):
        agg = enc.build_aggregation_dict()
        for sfx in ALL_VARIANTS:
            for d in DICTS:
                for tk in TRACKS:
                    pcol = f'{d}_{sfx}_tone{tk}'
                    assert pcol in agg, f"panel agg 缺 {pcol}"
                    assert agg[pcol] == (f'{d}_score_{sfx}{tk}', 'mean')

    def test_panel_names_within_32_chars(self):
        for sfx in ALL_VARIANTS:
            for d in DICTS:
                for tk in TRACKS:
                    name = f'{d}_{sfx}_tone{tk}'
                    assert len(name) <= 32, f"{name} = {len(name)} 字符 > 32"

    def test_no_msent_ladder_panel_cols(self):
        # 计数口径不入梯度: panel 无 msent_{raw,degonly,...} 列
        agg = enc.build_aggregation_dict()
        for k in agg:
            if 'msent' in k:
                assert not any(s in k for s in NEW_VARIANTS), f"msent 口径被错误加梯度: {k}"


class TestStataLabels:
    def test_heuristic_labels_cover_new_panel_cols(self):
        cols = [f'{d}_{sfx}_tone_{tk}'
                for d in DICTS for sfx in NEW_VARIANTS for tk in ('full', 'ctx', 'ss')]
        df = pd.DataFrame({c: [0.0] for c in cols})
        labels = se.build_variable_labels(df)
        for c in cols:
            assert c in labels and labels[c].strip(), f"{c} 无标签"
            assert len(labels[c].encode('utf-8')) <= 80, f"{c} 标签 {len(labels[c].encode('utf-8'))} > 80 字节"
            # 非泛型 fallback (列名本身)
            assert labels[c] != c, f"{c} 退化为列名 fallback"


class TestCodebookInference:
    def test_rule_ablation_match(self):
        assert cb._rule_ablation_match('loughran_raw_tone_ss') == ('loughran', 'raw')
        assert cb._rule_ablation_match('jiang_2021_negonly_tone_full') == ('jiang_2021', 'negonly')
        assert cb._rule_ablation_match('du_2022_degadv_tone_ctx') == ('du_2022', 'degadv')
        assert cb._rule_ablation_match('du_2022_tone_full') is None       # full 主列不匹配
        assert cb._rule_ablation_match('avg_msent_negonly_full') is None  # 计数口径不匹配

    def test_infer_label_rule_specific(self):
        # WP3 (2026-07-10): _infer_label 先查两端同源层 (stata_export HEURISTIC),
        # 消融列命中 F3 中文模板 (变体语义仍在标签文本内, 非泛型)
        lbl = cb._infer_label('jiang_2021_negdeg_tone_full')
        assert '否定+程度' in lbl and 'Jiang2021' in lbl
        # 共识 headline 列不被消融分支吞掉 (得 F7 共识专属标签, 非消融/泛型文案)
        vote_lbl = cb._infer_label('llm_vote_tone_full')
        assert vote_lbl == 'LLM三家投票正向倾向(共识主测度,全文轨)'
        assert vote_lbl != lbl

    def test_infer_source_stage_all_six_dicts(self):
        for d in DICTS:
            assert cb._infer_source_stage(f'{d}_raw_tone_full') == 'Stage 22'


class TestSSOTSync:
    """SSOT = tone_words.RULE_ABLATION_SUFFIXES。另有 3 处派生副本须与之同步, 否则未来加变体会:
      · codebook._RULE_ABLATION_SFX_DESC 缺键 → _infer_label/_infer_description 抛 KeyError;
      · codebook._RULE_ABLATION_RE 漏匹配 → 该列退泛型 codebook 推断 (无 MATH-1 披露);
      · stata_export 函数内 _ABL_VARIANT_DESC 漏登记 → 该列 .dta 标签退列名 fallback。
    本类锁死全链同步 (final-audit 完整性 critic 加固项)。"""

    def test_test_module_constants_are_ssot_derived(self):
        # 本测试文件的 ALL_VARIANTS/NEW_VARIANTS 必须就是 SSOT (− negonly), 防测试常量自身陈旧
        expected_new = [s for s in tone.RULE_ABLATION_SUFFIXES if s != 'negonly']
        assert ALL_VARIANTS == tone.RULE_ABLATION_SUFFIXES
        assert expected_new == NEW_VARIANTS

    def test_codebook_sfx_desc_covers_ssot(self):
        missing = set(tone.RULE_ABLATION_SUFFIXES) - set(cb._RULE_ABLATION_SFX_DESC)
        assert not missing, f"codebook._RULE_ABLATION_SFX_DESC 缺变体 {missing} → _infer_label 会 KeyError"

    def test_codebook_regex_matches_every_ssot_variant(self):
        for d in DICTS:
            for sfx in tone.RULE_ABLATION_SUFFIXES:
                for tk in ('full', 'ctx', 'ss'):
                    assert cb._rule_ablation_match(f'{d}_{sfx}_tone_{tk}') == (d, sfx), \
                        f"codebook._RULE_ABLATION_RE 漏匹配 {d}_{sfx}_tone_{tk}"

    def test_stata_labels_cover_every_ssot_new_variant(self):
        # stata_export 的 _ABL_VARIANT_DESC 是函数内局部, 经 build_variable_labels 间接守:
        # 全部 SSOT 新变体 (negonly 除外, 其标签手写) 的 panel 列须得非 fallback 标签。
        new = [s for s in tone.RULE_ABLATION_SUFFIXES if s != 'negonly']
        cols = [f'{d}_{sfx}_tone_{tk}' for d in DICTS for sfx in new for tk in ('full', 'ctx', 'ss')]
        labels = se.build_variable_labels(pd.DataFrame({c: [0.0] for c in cols}))
        for c in cols:
            assert labels.get(c) and labels[c] != c, \
                f"stata_export 漏标签 {c} (变体未登记 _ABL_VARIANT_DESC?)"


class TestCrossDictRollup:
    """跨词典均值 dict_avg_{sfx}_tone (geography.py) — 镜像既有 dict_avg_negonly_tone 三点谱,
    扩为全 powerset (v3.11.1)。负载列 = encode 的 per-dict {d}_{sfx}_tone。"""
    NEW = ['raw', 'degonly', 'advonly', 'negdeg', 'negadv', 'degadv']

    def _panel(self):
        cols = {'target_bank': ['A', 'B'], 'year': [2017, 2018], 'n_articles': [10, 10]}
        for d in DICTS:
            for s in ALL_VARIANTS:
                for t in TRACKS:
                    cols[f'{d}_{s}_tone{t}'] = [0.5, -0.5]
        return pd.DataFrame(cols)

    def test_geography_rolls_up_all_new_variants(self):
        from news_process.pipeline.panel import geography as geo
        out = geo.compute_composite_indicators(self._panel())
        for s in self.NEW:
            for t in TRACKS:
                col = f'dict_avg_{s}_tone{t}'
                assert col in out.columns, f"geography 漏跨词典 roll-up {col}"
        # 既有 negonly 跨词典列未被破坏
        assert 'dict_avg_negonly_tone_full' in out.columns

    def test_cross_dict_names_within_32_chars(self):
        for s in self.NEW:
            for t in TRACKS:
                name = f'dict_avg_{s}_tone{t}'
                assert len(name) <= 32, f"{name} = {len(name)} > 32"

    def test_codebook_labels_cross_dict_rule_specific(self):
        assert cb._rule_ablation_match('dict_avg_raw_tone_full') == ('dict_avg', 'raw')
        # WP3 (2026-07-10): _infer_label 先查两端同源层 → F3 中文模板
        # (dict_avg 词典名=六词典均值, 变体语义=程度+转折, 非泛型)
        lbl = cb._infer_label('dict_avg_degadv_tone_ctx')
        assert '六词典均值' in lbl and '程度+转折' in lbl

    def test_stata_labels_cross_dict(self):
        cols = [f'dict_avg_{s}_tone_{tk}' for s in self.NEW for tk in ('full', 'ctx', 'ss')]
        labels = se.build_variable_labels(pd.DataFrame({c: [0.0] for c in cols}))
        for c in cols:
            assert labels.get(c) and labels[c] != c and len(labels[c].encode('utf-8')) <= 80, \
                f"stata 跨词典标签缺失/超长: {c} → {labels.get(c)!r}"
