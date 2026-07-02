"""LLM 分类维度 per-model 梯子 gate 测试 (2026-07-03, ROBUSTNESS_GAP_BACKFILL 计划 §2 A6)。

P3/P4/P5 treatment 来源维度 (共识 sub_frac/tech_frac/collab_frac = canonical headline) 的
跨厂商稳健臂: 三 per-model ``{short}_{metric}{track}`` co-equal 互为稳健性、不分主次
(镜像 tone 梯子 / 政治词权重梯度)。⚠ 各家各自 just-identified 并排, 禁混同一
over-identified Hansen J。

覆盖 (镜像 test_political_weight_ladder / test_llm_model_robustness 八类):
  1. SSOT: encode.LLM_CLASS_SPEC 三元映射为唯一源; tone_llms 侧 byte-sync;
     skip 守卫代表列由**键** (文章级 subst/locus/collab) 派生 — ⚠ 禁用面板 metric 名派生
     (两命名域无字符串变换可达, 错配 → 生产机永久 reject skip)。
  2. 文章级发列: _aggregate_track 的 per_model_parsed 真产解析键 + 三份手抄发列块成对锁
     + 跨常量交叉断言 (守卫要求的列 stage 21 真会发)。
  3. 面板聚合: 指示列语义 (分子=verified∧标签==目标类 / 分母=verified 篇数) + ≤32 字符。
  4. 条件式一致性锚 (F16): 共识 ≠ 存档标签裸多数投票 — verified 门控 / final_v 清票 /
     locus 关键词回退三重语义逐一固化为断言 (含两类反例 fixture)。
  5. Stata 标签非 fallback ≤80B (share 措辞非 tone)。
  6. codebook matcher/label/source-stage + SSOT 全覆盖 + frac 文案不含「语调」。
  7. 四方 matcher 正交 + 既有负例保持。
  8. geography 负例: 跨模型 rollup 不吸收分类 frac 列。
"""
import json
from pathlib import Path

import pandas as pd

from news_process.pipeline.panel import codebook as cb
from news_process.pipeline.panel import encode as enc
from news_process.pipeline.panel import geography as geo
from news_process.pipeline.panel import stata_export as se
from news_process.pipeline.sentiment import tone_llms as tl

LLM_MODELS = ['gpt54nano', 'gemini31', 'deepseekv4']
DIMS = ('subst', 'locus', 'collab')
METRICS = ('sub_frac', 'tech_frac', 'collab_frac')
TARGETS = ('实质性', '底层技术', '外部协同')
PARSE_KEYS = ('innovation_substantiveness', 'innovation_locus', 'innovation_collab_mode')
TRACKS = ('_full', '_ctx', '_ss')

# 三个合成模型 (short_name 与生产一致, model_name 任意)
_MODELS = [
    {'short_name': 'gpt54nano', 'model_name': 'm-a'},
    {'short_name': 'gemini31', 'model_name': 'm-b'},
    {'short_name': 'deepseekv4', 'model_name': 'm-c'},
]


def _resp(verified=True, sentiment='正面', subst=None, locus=None, collab=None, topic=None):
    """构造单模型原始 JSON 响应 (镜像 prompt v8 键)。"""
    d = {
        'is_bank_fintech_news': verified,
        'sentiment': sentiment,
        'verification_confidence': 0.9,
        'sentiment_confidence': 0.8,
    }
    if subst is not None:
        d['innovation_substantiveness'] = subst
    if locus is not None:
        d['innovation_locus'] = locus
    if collab is not None:
        d['innovation_collab_mode'] = collab
    if topic is not None:
        d['fintech_topic'] = topic
    return json.dumps(d, ensure_ascii=False)


def _agg(responses):
    """responses = [(verified, subst, locus, collab, topic), ...] 按 _MODELS 序喂 _aggregate_track。"""
    mrd = {}
    for m, (v, sub, loc, col, top) in zip(_MODELS, responses):
        mrd[m['model_name']] = _resp(verified=v, subst=sub, locus=loc, collab=col, topic=top)
    return tl._aggregate_track(mrd, _MODELS)


class TestSSOTSync:
    def test_spec_shape(self):
        assert tuple(enc.LLM_CLASS_SPEC) == DIMS
        assert tuple(v[0] for v in enc.LLM_CLASS_SPEC.values()) == METRICS
        assert tuple(v[1] for v in enc.LLM_CLASS_SPEC.values()) == TARGETS
        assert tuple(v[2] for v in enc.LLM_CLASS_SPEC.values()) == PARSE_KEYS

    def test_tone_llms_side_byte_sync(self):
        # tone_llms 侧 import (或 fallback 字面量) 必须与 encode SSOT 逐字节一致
        assert tl._LLM_CLASS_SPEC == enc.LLM_CLASS_SPEC
        # 具名 fallback 常量逐字节锁 (终审 #11: import 成功时匿名 fallback 漂移不可测的盲区)
        assert tl._LLM_CLASS_SPEC_FALLBACK == enc.LLM_CLASS_SPEC

    def test_codebook_class_metrics_sync(self):
        assert frozenset(METRICS) == cb._LLM_CLASS_METRICS

    def test_skip_guard_columns_derivable_from_dims(self):
        # ⚠ 守卫代表列基名必须是文章级维度名 (LLM_CLASS_SPEC 键), 不是面板 metric 名
        from news_process import run_pipeline_function as rpf
        guard = set(rpf._STAGE21_REQUIRED_OUTPUT_COLUMNS)
        expected = {'gpt54nano_subst_full', 'gemini31_locus_ctx', 'deepseekv4_collab_ss'}
        assert expected <= guard
        for col in expected:
            model, rest = col.split('_', 1)
            dim, track = rest.rsplit('_', 1)
            assert model in LLM_MODELS and dim in enc.LLM_CLASS_SPEC
            assert f'_{track}' in TRACKS
        # 面板 metric 名绝不出现在守卫 (文章级 parquet 永不发它们)
        for metric in METRICS:
            assert not any(metric in c for c in guard), f'守卫混入面板 metric 名 {metric}'


class TestArticleEmission:
    def test_per_model_parsed_has_all_dims(self):
        out = _agg([(True, '实质性', '底层技术', '外部协同', '区块链')] * 3)
        parsed = out[8]
        for m in LLM_MODELS:
            for pk in PARSE_KEYS:
                assert f'{m}_{pk}' in parsed
        assert parsed['gpt54nano_innovation_substantiveness'] == '实质性'

    def test_three_emission_blocks_locked(self):
        # 三份手抄发列块成对锁 (F1 教训): full/ctx/ss 各恰一处 + init 恰一处;
        # LHS + RHS 全片段锁 (终审 #6: 只锁 LHS 时串轨 parsed_ctx→parsed_full /
        # 解析键索引 _cspec[2]→[1] 的值侧突变全绿)
        src = Path(tl.__file__).read_text(encoding='utf-8')
        for trk in ('full', 'ctx', 'ss'):
            full_line = ('per_model_cols[f"{short}_{_dim}_' + trk + '"]'
                         '.append(parsed_' + trk + '.get(f"{short}_{_cspec[2]}"))')
            assert src.count(full_line) == 1, \
                f'{trk} 轨 per-model 分类发列行缺失/重复/串轨/错索引: 期望恰 1 处 {full_line!r}'
        assert src.count('per_model_cols[f"{short}_{_dim}{track}"]') == 1, 'init 块缺失或重复'

    def test_consensus_callsite_tie_params_locked(self):
        # 终审 #9: 锁 production 共识 call-site 的 tie 参数 (一致性锚是"自带参数复算",
        # 生产参数漂移时锚测试不红 — 源码字面量计数补此盲区): subst 三轨 tie_default='象征性',
        # collab 三轨 tie_default='自主研发', locus 经 _resolve_locus_track (tie_default='应用场景' 恰 1 处)
        # 计数模式带 ',\n' 尾 (真实 call-site 该参数独占一行以逗号收尾; 模块 docstring 的
        # 同名散文字面量以 ';'/', ' 收尾, 不计入)
        src = Path(tl.__file__).read_text(encoding='utf-8')
        assert src.count("tie_default='象征性',\n") == 3
        assert src.count("tie_default='自主研发',\n") == 3
        assert src.count("tie_default='应用场景',\n") == 1

    def test_guard_columns_actually_emitted(self):
        # 跨常量交叉断言: 守卫要求的列, stage 21 发列路径真会发 (堵 fixture 自洽盲区)
        from news_process import run_pipeline_function as rpf
        out = _agg([(True, '实质性', '底层技术', '外部协同', None)] * 3)
        parsed = out[8]
        emitted_bases = {
            f'{m}_{dim}' for m in LLM_MODELS for dim in enc.LLM_CLASS_SPEC
            if f'{m}_{enc.LLM_CLASS_SPEC[dim][2]}' in parsed
        }
        new_guard = [c for c in rpf._STAGE21_REQUIRED_OUTPUT_COLUMNS
                     if c.split('_', 1)[0] in LLM_MODELS]
        assert new_guard, '守卫未包含 per-model 分类代表列'
        for col in new_guard:
            base = col.rsplit('_', 1)[0]  # 去轨后缀
            assert base in emitted_bases, f'守卫列 {col} 的基名 {base} 不在发列集 — 永久 reject skip 风险'


class TestPanelAggregation:
    def test_agg_dict_entries(self):
        agg = enc.build_aggregation_dict()
        for m in LLM_MODELS:
            for metric in METRICS:
                for tk in TRACKS:
                    key = f'{m}_{metric}{tk}'
                    assert key in agg, f'panel agg 缺 {key}'
                    assert agg[key] == (f'{m}_{metric}_src{tk}', 'mean')

    def test_names_within_32(self):
        for m in LLM_MODELS:
            for metric in METRICS:
                for tk in TRACKS:
                    for name in (f'{m}_{metric}{tk}', f'{m}_{metric}_src{tk}',):
                        assert len(name) <= 32, f'{name} = {len(name)} > 32'
            for dim in DIMS:
                for tk in TRACKS:
                    name = f'{m}_{dim}{tk}'
                    assert len(name) <= 32

    def test_indicator_semantics_gated(self):
        # 分子 = verified ∧ 标签==目标类; 分母 = verified 篇数; unverified 标签零贡献
        df = pd.DataFrame({
            'llm_sentiment_full': ['正面'] * 4,
            'llm_verified_full': [True] * 4,
            'gpt54nano_sentiment_full': ['正面'] * 4,
            'gpt54nano_verified_full': [True, True, False, True],
            'gpt54nano_subst_full': ['实质性', '象征性', '实质性', None],
            'gpt54nano_locus_full': [None] * 4,
            'gpt54nano_collab_full': [None] * 4,
        })
        out = enc.encode_sentiment(df)
        src = out['gpt54nano_sub_frac_src_full']
        # verified+目标类=1 / verified+非目标(含缺标)=0 / unverified=NA (不入分母)
        assert src.iloc[0] == 1 and src.iloc[1] == 0
        assert pd.isna(src.iloc[2])
        assert src.iloc[3] == 0  # verified 但缺标 → 计入分母不计分子 (缺标残差)
        assert float(src.mean()) == 1.0 / 3.0  # mean ≡ 分子/分母 (verified 3 篇中 1 篇目标类)


class TestConsistencyAnchor:
    """条件式一致性锚 (F16): 共识 ≠ 存档标签裸多数投票。"""

    def test_unverified_label_excluded_from_consensus(self):
        # 反例 1: verified=[T,T,F], 两 verified 缺标 + unverified 标'实质性'
        # → 共识票池空 → None; per-model 存档保留 unverified 的标签 (审计不门控)
        out = _agg([
            (True, None, None, None, None),
            (True, None, None, None, None),
            (False, '实质性', None, None, None),
        ])
        innov_substs, parsed = out[11], out[8]
        assert innov_substs == []  # verified 门控: unverified 标签不入票
        consensus = tl.majority_vote_categorical(
            innov_substs, tie_strategy='conservative', tie_default='象征性', empty_fallback=None)
        assert consensus is None
        assert parsed['deepseekv4_innovation_substantiveness'] == '实质性'  # 存档不门控

    def test_final_v_false_clears_votes_keeps_archive(self):
        # 反例 2: 多数判非金科 (final_v=False) → 共识票池整体清空, 存档保留
        out = _agg([
            (False, '实质性', '底层技术', '外部协同', '区块链'),
            (False, '实质性', '底层技术', '外部协同', '区块链'),
            (True, '实质性', '底层技术', '外部协同', '区块链'),
        ])
        final_v, parsed = out[0], out[8]
        topics, innov_loci, innov_substs, innov_collabs = out[9], out[10], out[11], out[16]
        assert final_v is False
        assert topics == [] and innov_loci == [] and innov_substs == [] and innov_collabs == []
        assert parsed['gpt54nano_innovation_substantiveness'] == '实质性'

    def test_gated_majority_reproduces_consensus_subst_collab(self):
        # final_v=True 时: verified 子集标签多数票 (conservative tie_default) == 共识
        out = _agg([
            (True, '实质性', None, '外部协同', None),
            (True, '实质性', None, '自主研发', None),
            (True, '象征性', None, '外部协同', None),
        ])
        innov_substs, innov_collabs = out[11], out[16]
        assert tl.majority_vote_categorical(
            innov_substs, tie_strategy='conservative', tie_default='象征性',
            empty_fallback=None) == '实质性'
        assert tl.majority_vote_categorical(
            innov_collabs, tie_strategy='conservative', tie_default='自主研发',
            empty_fallback=None) == '外部协同'

    def test_tie_conservative_default(self):
        out = _agg([
            (True, '实质性', None, None, None),
            (True, '象征性', None, None, None),
            (False, '实质性', None, None, None),  # unverified 不入票 → 1:1 平局
        ])
        assert tl.majority_vote_categorical(
            out[11], tie_strategy='conservative', tie_default='象征性',
            empty_fallback=None) == '象征性'

    def test_locus_keyword_fallback_not_reproducible_from_votes(self):
        # locus 共识经 _resolve_locus_track 关键词回退: LLM 零票 + 关键词证据 → 有标签,
        # 不来自任何 per-model 票 → locus 排除出纯多数投票不变量 (import 级单测覆盖)
        label, conf = tl._resolve_locus_track([], ['区块链技术平台'])
        assert label is not None and conf > 0
        # 零证据对称分支: 空票 + 空 topics → (None, 0.0)
        assert tl._resolve_locus_track([], []) == (None, 0.0)


class TestStataLabels:
    def test_frac_labels_non_fallback(self):
        cols = [f'{m}_{metric}_{t}' for m in LLM_MODELS for metric in METRICS
                for t in ('full', 'ctx', 'ss')]
        labels = se.build_variable_labels(pd.DataFrame({c: [0.0] for c in cols}))
        for c in cols:
            assert c in labels and labels[c].strip() and labels[c] != c, f'{c} 标签 fallback'
            assert len(labels[c].encode('utf-8')) <= 80
            assert 'share' in labels[c], f'{c} 英文标签未用 share 措辞: {labels[c]}'


class TestCodebookInference:
    def test_llm_model_match_frac(self):
        assert cb._llm_model_match('gpt54nano_sub_frac_full') == ('gpt54nano', 'sub_frac', '')
        assert cb._llm_model_match('deepseekv4_collab_frac_ss') == ('deepseekv4', 'collab_frac', '')
        assert cb._llm_model_match('gemini31_tech_frac_ctx') == ('gemini31', 'tech_frac', '')

    def test_ssot_full_coverage(self):
        for m in LLM_MODELS:
            for metric in METRICS:
                for t in ('full', 'ctx', 'ss'):
                    assert cb._llm_model_match(f'{m}_{metric}_{t}') is not None

    def test_label_is_classification_not_tone(self):
        lbl = cb._infer_label('gpt54nano_sub_frac_full')
        desc = cb._infer_description('gpt54nano_sub_frac_full')
        assert '分类占比' in lbl and '语调' not in lbl
        assert '语调' not in desc and '不分主次' in desc and 'Hansen J' in desc
        # 分母口径披露 (计划 R2)
        assert 'verified' in desc

    def test_tone_label_unchanged(self):
        lbl = cb._infer_label('gpt54nano_tone_full')
        assert '语调' in lbl and '分类占比' not in lbl

    def test_source_stage(self):
        for m in LLM_MODELS:
            assert cb._infer_source_stage(f'{m}_sub_frac_full') == 'Stage 21'


class TestMatcherOrthogonality:
    def test_frac_owned_by_llm_matcher_only(self):
        col = 'gpt54nano_sub_frac_full'
        assert cb._llm_model_match(col) is not None
        assert cb._bert_model_match(col) is None
        assert cb._political_weight_match(col) is None
        assert cb._rule_ablation_match(col) is None

    def test_legacy_negatives_hold(self):
        # 扩 metric 组后既有负例不得翻转 (test_llm_model_robustness.py:78 同款)
        assert cb._llm_model_match('gpt54nano_tone_sub_full') is None
        assert cb._llm_model_match('gpt54nano_tone_symb_ctx') is None
        assert cb._llm_model_match('llm_vote_tone_full') is None
        # 共识 frac 不以模型名开头, 不被吞
        assert cb._llm_model_match('sub_frac') is None


class TestTableA12PanelC:
    """27_tableA12 模板文本 gate (计划 §2 A5): 锁矩阵容量与 Panel C 块, 防第四族再撞硬编码。"""

    _TMPL = (Path(__file__).resolve().parents[1] / 'papers' / '_common'
             / 'stata_templates' / '27_tableA12_cross_model_fwer.do.tmpl')

    def test_matrix_capacity_expanded(self):
        src = self._TMPL.read_text(encoding='utf-8')
        assert 'J(9, 1, .)' in src, 'RES 矩阵未扩容 J(9,1) — 三族满提取时越界中断整表'
        assert 'J(6, 1, .)' not in src

    def test_cls_family_block_present(self):
        src = self._TMPL.read_text(encoding='utf-8')
        assert 'cls_fam' in src and 'CLS:' in src
        assert '_sub_frac_`SENT' in src, 'CLS 族列名须按 {short}_sub_frac_<track> 拼'
        # 三族分别 rwolf: LLM/BERT/CLS 各自 rwolf 调用存在 (逐族紧邻提取防 e() 覆写)
        assert src.count('capture noisily rwolf') == 3


class TestGeographyNoRollup:
    def test_cross_model_rollup_excludes_class_fracs(self):
        # geography 的 llm_models_avg_* 只滚 tone/cont 族; 分类 frac 不做均值-ensemble
        src = Path(geo.__file__).read_text(encoding='utf-8')
        for metric in METRICS:
            assert f"{{s}}_{metric}" not in src, f'geography rollup 误吸 {metric}'
            assert f'llm_models_avg_{metric}' not in src
