"""LLM 三家 (gpt54nano/gemini31/deepseekv4) 逐模型语调「互为稳健性」gate 测试 (2026-07-02)。

投票共识 ``llm_vote_tone`` = canonical headline (paper_spec.primary); 三 per-model
``{short}_tone`` co-equal 互为稳健性、不分主次 (镜像 du_2022 政治词权重梯度)。⚠ 三家各自
just-identified 并排, 禁混同一 over-identified Hansen J。覆盖 (镜像 test_political_weight_ladder
全 6 类):
  · SSOT 跨模块同步 (encode.LLM_MODELS == config == codebook)
  · panel 聚合逐 track 列存在 (per-model tone + llm_vote_tone 共识) + ≤32 字符
  · stata 标签非 fallback (依赖 stata_export G1 机械块)
  · codebook matcher / _infer_label / _infer_source_stage (宽前缀 → Stage 21, 尤其 deepseekv4)
  · 四方 matcher 互斥 (_llm/_bert/_rule_ablation/_political_weight)
  · NOTE 含铁律短语
"""
import pandas as pd

from news_process.core.config import load_config
from news_process.pipeline.panel import codebook as cb
from news_process.pipeline.panel import encode as enc
from news_process.pipeline.panel import stata_export as se

LLM_MODELS = ['gpt54nano', 'gemini31', 'deepseekv4']
TRACKS = ('_full', '_ctx', '_ss')
METRICS = ['tone', 'tone_sum', 'tone_std', 'cont_mean', 'cont_sum']


class TestSSOTSync:
    def test_encode_llm_models(self):
        assert enc.LLM_MODELS == LLM_MODELS

    def test_config_sync(self):
        # 不同步会致 encode 聚合静默漏列 → panel 全 NaN
        cfg = load_config().get('tone_llm_processing', {}).get('models', [])
        assert [m['short_name'] for m in cfg] == enc.LLM_MODELS

    def test_codebook_sync(self):
        # codebook 模块级导入 encode.LLM_MODELS (C1); 防 SSOT 单侧漂移
        assert cb.LLM_MODELS == enc.LLM_MODELS


class TestPanelAggregation:
    def test_per_model_tone_cols_present(self):
        agg = enc.build_aggregation_dict()
        for m in LLM_MODELS:
            for tk in TRACKS:
                assert f'{m}_tone{tk}' in agg, f'panel agg 缺 {m}_tone{tk}'
                assert agg[f'{m}_tone{tk}'] == (f'{m}_score{tk}', 'mean')

    def test_vote_consensus_present(self):
        agg = enc.build_aggregation_dict()
        for tk in TRACKS:
            assert f'llm_vote_tone{tk}' in agg, f'panel agg 缺共识 llm_vote_tone{tk}'

    def test_names_within_32(self):
        for m in LLM_MODELS:
            for mt in METRICS:
                for tk in TRACKS:
                    name = f'{m}_{mt}{tk}'
                    assert len(name) <= 32, f'{name} = {len(name)} > 32'


class TestStataLabels:
    def test_per_model_labels_non_fallback(self):
        cols = [f'{m}_tone_{t}' for m in LLM_MODELS for t in ('full', 'ctx', 'ss')]
        cols += [f'{m}_tone_vw_full' for m in LLM_MODELS]  # 加权臂亦须有标签
        labels = se.build_variable_labels(pd.DataFrame({c: [0.0] for c in cols}))
        for c in cols:
            assert c in labels and labels[c].strip(), f'{c} 无标签'
            assert labels[c] != c, f'{c} 退化为列名 fallback'
            assert len(labels[c].encode('utf-8')) <= 80


class TestCodebookInference:
    def test_llm_model_match(self):
        assert cb._llm_model_match('gpt54nano_tone_full') == ('gpt54nano', 'tone', '')
        assert cb._llm_model_match('deepseekv4_tone_vw_ctx') == ('deepseekv4', 'tone', '_vw')
        assert cb._llm_model_match('gemini31_cont_sum_ss') == ('gemini31', 'cont_sum', '')
        assert cb._llm_model_match('llm_vote_tone_full') is None        # 共识, 不吞
        assert cb._llm_model_match('gpt54nano_tone_sub_full') is None   # 实质性子集, 不吞
        assert cb._llm_model_match('gpt54nano_tone_symb_ctx') is None

    def test_infer_label_specific(self):
        # WP3 (2026-07-10): _infer_label 先查两端同源层 → per-model 中文标签
        # (模型显示名 GPT-5.4nano, 见 stata_export._PM_MODEL_ZH)
        lbl = cb._infer_label('gpt54nano_tone_full')
        assert 'GPT-5.4nano' in lbl
        assert 'Sentiment Tone' not in lbl                       # 未落泛型
        assert lbl != cb._infer_label('llm_vote_tone_full')      # 与共识标签相异

    def test_infer_source_stage_broad_prefix(self):
        # 宽前缀: deepseekv4 无 llm/gpt/gemini 子串, 仍须 Stage 21 (含加权变体)
        for m in LLM_MODELS:
            assert cb._infer_source_stage(f'{m}_tone_full') == 'Stage 21'
            assert cb._infer_source_stage(f'{m}_tone_vw_full') == 'Stage 21'
        assert cb._infer_source_stage('deepseekv4_cont_sum_ss') == 'Stage 21'

    def test_note_iron_rule(self):
        note = cb._LLM_MODEL_NOTE
        assert '不分主次' in note and 'over-identified Hansen J' in note


class TestMatcherOrthogonality:
    """四方 matcher (_llm/_bert/_rule_ablation/_political_weight) 对彼此列互斥。"""

    def test_disjoint(self):
        owners = {
            'gpt54nano_tone_full': 'llm',
            'finbert_cn_pos_full': 'bert',
            'du_2022_polw00_tone_full': 'polw',
            'jiang_2021_negonly_tone_full': 'abl',
        }
        matchers = {
            'llm': cb._llm_model_match, 'bert': cb._bert_model_match,
            'polw': cb._political_weight_match, 'abl': cb._rule_ablation_match,
        }
        for col, owner in owners.items():
            for name, fn in matchers.items():
                hit = fn(col)
                if name == owner:
                    assert hit is not None, f'{name} matcher 应认领 {col}'
                else:
                    assert hit is None, f'{name} matcher 误认领 {col}'
