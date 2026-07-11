"""BERT 三模型 (finbert_cn/fin_sent_zh/finbert2) 逐模型「互为稳健性」gate 测试 (2026-07-02)。

三 per-model co-equal 互为稳健性、不分主次 (无 ensemble headline; BERT 整体是相对 LLM 的
cross-method 稳健臂)。per-model 独立降级 (finbert2 缺席仅掉自身族)。⚠ 三模型各自
just-identified 并排, 禁混同一 over-identified Hansen J。分类数: finbert_cn/fin_sent_zh = 3 类
(含中性), finbert2 = 2 类 (无中性)。覆盖 (镜像 test_political_weight_ladder 全 6 类 + geography):
  · SSOT 跨模块同步 (encode.BERT_MODELS == config == codebook) + THREE_CLASS_MODELS
  · panel 聚合 per-model pos/neg 逐 track; neu 仅三分类; ≤32 字符
  · stata 标签非 fallback (含 net_tone Phase 2 前置)
  · codebook matcher / _infer_source_stage (宽前缀 → Stage 23, 尤其 fin_sent_zh 无 'bert' 子串)
  · NOTE 含铁律短语 · geography 不误卷 net_tone
"""
import pandas as pd

from news_process.core.config import load_config
from news_process.pipeline.panel import codebook as cb
from news_process.pipeline.panel import encode as enc
from news_process.pipeline.panel import stata_export as se

BERT_MODELS = ['finbert_cn', 'fin_sent_zh', 'finbert2']
THREE_CLASS = {'finbert_cn', 'fin_sent_zh'}
TRACKS = ('_full', '_ctx', '_ss')


class TestSSOTSync:
    def test_encode_bert_models(self):
        assert enc.BERT_MODELS == BERT_MODELS

    def test_config_sync(self):
        cfg = load_config().get('sentiment_analysis', {}).get('tone_berts', {}).get('models', [])
        assert [m['short_name'] for m in cfg] == enc.BERT_MODELS

    def test_codebook_sync(self):
        # codebook 模块级导入 encode.BERT_MODELS (C1, 堵审计发现的不同步缺口)
        assert cb.BERT_MODELS == enc.BERT_MODELS

    def test_three_class_set(self):
        assert enc.THREE_CLASS_MODELS == THREE_CLASS
        assert 'finbert2' not in enc.THREE_CLASS_MODELS  # 2 分类无中性


class TestPanelAggregation:
    def test_per_model_prob_cols_present(self):
        agg = enc.build_aggregation_dict()
        for m in BERT_MODELS:
            for tk in TRACKS:
                assert f'{m}_pos{tk}' in agg, f'panel agg 缺 {m}_pos{tk}'
                assert f'{m}_neg{tk}' in agg, f'panel agg 缺 {m}_neg{tk}'

    def test_neu_only_three_class(self):
        agg = enc.build_aggregation_dict()
        for tk in TRACKS:
            for m in THREE_CLASS:
                assert f'{m}_neu{tk}' in agg
            assert f'finbert2_neu{tk}' not in agg  # 2 分类不产中性

    def test_names_within_32(self):
        for m in BERT_MODELS:
            for mt in ['net_tone', 'pos', 'neg', 'pos_std', 'pos_sum', 'neg_sum']:
                for tk in TRACKS:
                    assert len(f'{m}_{mt}{tk}') <= 32


class TestStataLabels:
    def test_labels_non_fallback(self):
        cols = []
        for m in BERT_MODELS:
            for mt in ['pos', 'neg', 'net_tone', 'pos_std']:
                for t in ('full', 'ctx', 'ss'):
                    cols.append(f'{m}_{mt}_{t}')
        for m in THREE_CLASS:
            for t in ('full', 'ctx', 'ss'):
                cols.append(f'{m}_neu_{t}')
        labels = se.build_variable_labels(pd.DataFrame({c: [0.0] for c in cols}))
        for c in cols:
            assert labels.get(c, c) != c, f'{c} 退化为 fallback'
            assert len(labels[c].encode('utf-8')) <= 80


class TestCodebookInference:
    def test_bert_model_match(self):
        assert cb._bert_model_match('finbert_cn_pos_full') == ('finbert_cn', 'pos', '')
        assert cb._bert_model_match('fin_sent_zh_net_tone_ctx') == ('fin_sent_zh', 'net_tone', '')
        assert cb._bert_model_match('finbert2_pos_vw_full') == ('finbert2', 'pos', '_vw')
        assert cb._bert_model_match('finbert_cn_neu_ss') == ('finbert_cn', 'neu', '')
        assert cb._bert_model_match('llm_vote_tone_full') is None

    def test_infer_source_stage_fin_sent_zh(self):
        # fin_sent_zh 无 'bert' 子串 → 宽前缀须救回 Stage 23 (含加权/net_tone)
        for m in BERT_MODELS:
            assert cb._infer_source_stage(f'{m}_pos_full') == 'Stage 23'
        assert cb._infer_source_stage('fin_sent_zh_net_tone_ss') == 'Stage 23'
        assert cb._infer_source_stage('fin_sent_zh_pos_vw_full') == 'Stage 23'

    def test_infer_label_specific(self):
        # WP3 (2026-07-10): _infer_label 先查两端同源层 → per-model 中文标签
        # (模型显示名 FinBERT-CN, 见 stata_export._PM_MODEL_ZH)
        lbl = cb._infer_label('finbert_cn_pos_full')
        assert 'FinBERT-CN' in lbl
        assert lbl != 'Finbert_Cn Pos Full'  # 未落 Title-case 兜底

    def test_note_iron_rule(self):
        assert 'over-identified Hansen J' in cb._BERT_MODEL_NOTE


class TestPhase2NetTone:
    """Phase 2 (BERT signed net_tone) 门控: net_tone 由 encode post-agg 派生 (非
    build_aggregation_dict), Phase 1 未落盘 → 此处仅验 stata 标签已就位; 真面板恒等
    net_tone == pos − neg 待 Phase 2 encode B3 + 真面板 (DEFERRED skip)。"""

    def test_net_tone_label_ready(self):
        cols = [f'{m}_net_tone_{t}' for m in BERT_MODELS for t in ('full', 'ctx', 'ss')]
        labels = se.build_variable_labels(pd.DataFrame({c: [0.0] for c in cols}))
        for c in cols:
            assert labels.get(c, c) != c, f'{c} net_tone 无标签源 (Phase 2 前置)'


class TestGeographyNoNetToneRollup:
    """geography 用显式列名清单 (非 regex sweep) → 新 net_tone 不被误卷入任何跨模型均值。"""

    def _panel(self):
        cols = {'target_bank': ['A', 'B'], 'year': [2017, 2018], 'n_articles': [10, 10]}
        for m in BERT_MODELS:
            for t in TRACKS:
                cols[f'{m}_pos{t}'] = [0.5, 0.4]
                cols[f'{m}_neg{t}'] = [0.2, 0.3]
                cols[f'{m}_net_tone{t}'] = [0.3, 0.1]  # Phase 2 新列, 注入检验是否误卷
            for t in TRACKS:
                if m in THREE_CLASS:
                    cols[f'{m}_neu{t}'] = [0.3, 0.3]
        return pd.DataFrame(cols)

    def test_net_tone_not_rolled_up(self):
        from news_process.pipeline.panel import geography as geo
        out = geo.compute_composite_indicators(self._panel())
        leaked = [c for c in out.columns if 'net_tone' in c and c.startswith(('bert_avg', 'dict_avg', 'llm_models_avg'))]
        assert not leaked, f'geography 误把 net_tone 卷入跨模型均值: {leaked}'
