"""罕见词频次 cutoff 梯子 gate 测试 (2026-07-03, ROBUSTNESS_GAP_BACKFILL 计划 §5 D1)。

梯子 SSOT = ``lexical_complexity.RARE_WORD_FREQ_CUTOFFS = (2.0, 3.0, 5.0)``;
canonical = 3.0 (中值) ≡ 既有无后缀 ``rare_word_ratio`` (由 ``_rare_word_cutoff()``
分位派生, 实测 3.0 — 本文件锚死该值防 jieba 词典漂移); 变体臂 =
``rare_word_ratio_c{2,5}{track}`` / 面板 ``avg_rare_word_c{2,5}{track}``。
⚠ 为何按频次: 冻结词典低频巨量 tie 使分位梯子 {10,20,30} 数学退化 (p30≡p20)。
⚠ 铁律: 三臂互为稳健、不分主次, 各自 just-identified 并排, 禁混同一
over-identified Hansen J; 与规则消融/政治词权重梯子正交不交叉。

镜像 test_political_weight_ladder 八类 (判别性断言为本梯子特有加固):
SSOT / 文章级列 + canonical 锚 / 三臂判别性 (非恒等) / 面板聚合 ≤32 /
Stata 标签 / codebook / matcher 正交 / 物化链 (LEXICAL_COMPLEXITY_KEYS)。
"""
import math

import pandas as pd

from news_process.pipeline.panel import codebook as cb
from news_process.pipeline.panel import stata_export as se
from news_process.pipeline.panel.encode import build_aggregation_dict
from news_process.pipeline.sentiment import lexical_complexity as lc

TRACKS = ('_full', '_ctx', '_ss')
VARIANT_BASES = ('rare_word_ratio_c2', 'rare_word_ratio_c5')
PANEL_BASES = ('avg_rare_word_c2', 'avg_rare_word_c5')


class TestSSOT:
    def test_ladder_values_and_pairwise_distinct(self):
        assert lc.RARE_WORD_FREQ_CUTOFFS == (2.0, 3.0, 5.0)
        assert len(set(lc.RARE_WORD_FREQ_CUTOFFS)) == 3, '三臂 cutoff 必须两两互异 (防退化假臂)'

    def test_canonical_anchored_to_percentile_cutoff(self):
        # canonical (中值 3.0) ≡ 分位派生 _rare_word_cutoff(); 词典漂移即红
        assert lc._rare_word_cutoff() == 3.0 == lc.RARE_WORD_FREQ_CUTOFFS[1]

    def test_variant_keys_consistent(self):
        assert set(lc._RARE_CUTOFF_VARIANT_KEYS) == {2.0, 5.0}
        assert set(lc._RARE_CUTOFF_VARIANT_KEYS.values()) == set(VARIANT_BASES)

    def test_rationale_present(self):
        assert '互为稳健性' in lc.RARE_WORD_CUTOFF_RATIONALE
        assert '频次' in lc.RARE_WORD_CUTOFF_RATIONALE


def _freq_word(freq_pred, exclude=()):
    """从冻结词典挑一个满足词频谓词的 ≥2 字纯中文词 (真实词典驱动, 无 mock)。"""
    freq = lc._get_pristine_tokenizer().FREQ
    for w, f in freq.items():
        if (f and freq_pred(f) and len(w) >= 2 and w not in exclude
                and not lc._NON_LEXICAL_TOKEN_RE.fullmatch(w)):
            return w
    raise AssertionError('冻结词典中找不到满足谓词的词')


class TestArticleColumns:
    def test_keys_present_and_empty_nan(self):
        r = lc.compute_lexical_complexity('')
        for base in ('rare_word_ratio', *VARIANT_BASES):
            assert base in r and math.isnan(r[base])

    def test_monotone_nesting(self):
        # freq≤2 ⊆ freq≤3 ⊆ freq≤5 → 三臂天然单调 (逐文)
        text = '银行发布金融科技战略, 计划在未来三年持续投入研发资源。'
        r = lc.compute_lexical_complexity(text)
        assert r['rare_word_ratio_c2'] <= r['rare_word_ratio'] <= r['rare_word_ratio_c5']

    def test_three_arms_pairwise_discriminant(self):
        # 判别性 (防谓词层退化): 构造含 freq==3 与 freq∈(3,5] 真实词的文本 → 三臂两两不同
        w3 = _freq_word(lambda f: f == 3)
        w45 = _freq_word(lambda f: f in (4, 5), exclude={w3})
        text = f'{w3}。{w45}。今天银行发展。'
        r = lc.compute_lexical_complexity(text)
        vals = (r['rare_word_ratio_c2'], r['rare_word_ratio'], r['rare_word_ratio_c5'])
        assert len({round(v, 6) for v in vals}) == 3, \
            f'三臂未两两互异 (退化假臂): c2={vals[0]} c3={vals[1]} c5={vals[2]} (w3={w3!r}, w45={w45!r})'

    def test_materialization_chain(self):
        # 物化链 SSOT: 变体键必须在 LEXICAL_COMPLEXITY_KEYS (tone_words 三轨提取循环的唯一源)
        for base in VARIANT_BASES:
            assert base in lc.LEXICAL_COMPLEXITY_KEYS
        assert 'rare_word_ratio' in lc.LEXICAL_COMPLEXITY_KEYS


class TestPanelAggregation:
    def test_agg_entries(self):
        agg = build_aggregation_dict()
        for pb, ab in zip(PANEL_BASES, VARIANT_BASES):
            for tk in TRACKS:
                assert agg[f'{pb}{tk}'] == (f'{ab}{tk}', 'mean')
                assert len(f'{pb}{tk}') <= 32
        # canonical 聚合不受扰动
        for tk in TRACKS:
            assert agg[f'avg_rare_word{tk}'] == (f'rare_word_ratio{tk}', 'mean')


class TestStataLabels:
    def test_non_fallback(self):
        cols = [f'{pb}_{t}' for pb in PANEL_BASES for t in ('full', 'ctx', 'ss')]
        labels = se.build_variable_labels(pd.DataFrame({c: [0.0] for c in cols}))
        for c in cols:
            assert c in labels and labels[c] != c
            assert len(labels[c].encode('utf-8')) <= 80


class TestCodebook:
    def test_metadata_entries(self):
        meta = cb.get_variable_metadata_dict()
        for pb in PANEL_BASES:
            for t in ('full', 'ctx', 'ss'):
                key = f'{pb}_{t}'
                assert key in meta, f'codebook 缺 {key}'
                assert meta[key].source_stage and '未知' not in meta[key].source_stage
        # canonical 条目不受扰动 (WP3 2026-07-10 标签中文化后的中文文案)
        assert meta['avg_rare_word_full'].label == '罕见词比率(词频≤3)(全文轨)'


class TestMatcherOrthogonality:
    def test_not_claimed_by_other_matchers(self):
        for col in ('avg_rare_word_c2_full', 'avg_rare_word_c5_ss'):
            assert cb._llm_model_match(col) is None
            assert cb._bert_model_match(col) is None
            assert cb._political_weight_match(col) is None
            assert cb._rule_ablation_match(col) is None
