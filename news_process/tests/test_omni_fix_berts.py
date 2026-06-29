"""tests/test_omni_fix_berts.py — omni 审计 g-berts 组修复回归锁 (2026-06-11)。

锁定 pipeline/sentiment/tone_berts.py 四项修复后行为:

  g-berts-01 (P1): 共享分词组键 max_length → (max_length, 词表指纹) —
      词表不同的模型独立分词, 各自用自身 tokenizer 的 token id 推理
      (历史 bug: finbert2 全程吃 finbert_cn 的跨词表错位 id = 乱码输入)。
  g-berts-02 (P2): 批级推理异常不再整批静默置 '中性'+全0 哨兵 — 逐篇重试
      一次, 仍失败才写失败哨兵 (label=None / 概率 NaN / num_windows=-1,
      与空文本 num_windows=0 严格区分) + 每篇 {sn}_infer_failed 标志列;
      2-class 模型输出端补 中性=NaN 列 (而非 0)。
  g-berts-03 (P3): num_labels 不匹配时不再盲回退 DEFAULT_LABEL_MAP 顺序
      (对在产 checkpoint 是极性翻转) — 改从 checkpoint id2label 极性归一
      推导, 推导失败 fail-loud; 极性顺序守卫 warning-only → raise。
  g-berts-04 (P3): 模型加载失败不再静默吞掉 — 仅"本地私有模型未配置"
      允许 graceful skip; 其余默认 raise (strict_models 开关), 并记录
      skipped_expected / failed_models 清单。

Mock 策略: 不加载真实 BERT 模型 / 不触网 — 以 Fake tokenizer/model 替换
模块命名空间内的 AutoTokenizer / AutoModelForSequenceClassification;
process_all_models 用合成 DataFrame + 桩 run_all_models。

# 白话: 这组测试用"假模型/假分词器"复现四个历史 bug 场景, 确保修复不被改回去:
# 1) 不同词表的模型不能共用一份分词结果; 2) 一篇文章推理失败只标记那一篇,
# 不再整批悄悄填"中性"; 3) 标签顺序对不上时宁可报错也不瞎猜; 4) 模型加载
# 失败默认大声报错, 只有"本地私有模型没配置"才允许安静跳过。
"""

from __future__ import annotations

import math
import os
import sys

import pytest

# CI light matrix 不安装 torch; 与 test_tone_berts_deterministic.py 同约定
torch = pytest.importorskip("torch")

import pandas as pd  # noqa: E402

_PROJECT_PARENT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)


@pytest.fixture(scope="module")
def berts():
    """导入 tone_berts 模块 (规范包路径)。"""
    from news_process.pipeline.sentiment import tone_berts
    return tone_berts


# ============================================================================
# Fakes (不触网, 不加载权重)
# ============================================================================

class FakeTokenizer:
    """字符级假 tokenizer: vocab 可注入, 提供指纹所需的全部属性。"""

    def __init__(self, vocab: dict, do_lower_case: bool = False,
                 cls: int = 101, sep: int = 102, pad: int = 0, unk: int = 1):
        self._vocab = dict(vocab)
        self.do_lower_case = do_lower_case
        self.cls_token_id = cls
        self.sep_token_id = sep
        self.pad_token_id = pad
        self.unk_token_id = unk
        self.bos_token_id = None
        self.eos_token_id = None

    def get_vocab(self):
        return dict(self._vocab)

    def __call__(self, texts, **kwargs):
        return {
            'input_ids': [
                [self._vocab.get(ch, self.unk_token_id) for ch in t]
                for t in texts
            ]
        }


class _FakeOutput:
    def __init__(self, logits):
        self.logits = logits


class _FakeConfig:
    def __init__(self, num_labels, id2label):
        self.num_labels = num_labels
        self.id2label = id2label


class FakeModel:
    """假分类模型: 记录收到的 input_ids, 返回恒定 logits (偏向类 0)。"""

    def __init__(self, num_labels=3, id2label=None):
        if id2label is None:
            id2label = {0: '负面', 1: '中性', 2: '正面'}
        self.config = _FakeConfig(num_labels, id2label)
        self.seen_input_ids: list = []

    def to(self, device):
        return self

    def eval(self):
        return self

    def __call__(self, **inputs):
        ids = inputs['input_ids']
        self.seen_input_ids.append(ids.detach().cpu().tolist())
        logits = torch.zeros(ids.shape[0], self.config.num_labels,
                             device=ids.device)
        logits[:, 0] = 1.0
        return _FakeOutput(logits)


def _install_fake_hf(monkeypatch, berts, tokenizer_by_path: dict, model_by_path: dict):
    """把模块命名空间内的 HF Auto* 替换为按 model_path 分发的假实现。"""

    class FakeAutoTokenizer:
        @staticmethod
        def from_pretrained(path, **kwargs):
            obj = tokenizer_by_path[path]
            if isinstance(obj, Exception):
                raise obj
            return obj

    class FakeAutoModel:
        @staticmethod
        def from_pretrained(path, **kwargs):
            obj = model_by_path[path]
            if isinstance(obj, Exception):
                raise obj
            return obj

    monkeypatch.setattr(berts, 'AutoTokenizer', FakeAutoTokenizer)
    monkeypatch.setattr(berts, 'AutoModelForSequenceClassification', FakeAutoModel)


def _mc(short_name, model_id, label_map=None, max_length=512):
    if label_map is None:
        label_map = {0: '负面', 1: '中性', 2: '正面'}
    return {
        'model_id': model_id,
        'short_name': short_name,
        'description': 'fake',
        'max_length': max_length,
        'label_map': label_map,
    }


VOCAB_A = {'银': 10, '行': 11, '不': 12, '错': 13}
VOCAB_B = {'银': 20, '行': 21, '不': 22, '错': 23}


# ============================================================================
# g-berts-01: 词表指纹 + 分组隔离
# ============================================================================

class TestTokenizerFingerprint:
    """_tokenizer_fingerprint: 词表/大小写/特殊 token 任一不同 → 指纹不同。"""

    def test_identical_tokenizers_same_fingerprint(self, berts):
        fp1 = berts._tokenizer_fingerprint(FakeTokenizer(VOCAB_A))
        fp2 = berts._tokenizer_fingerprint(FakeTokenizer(VOCAB_A))
        assert fp1 == fp2

    def test_different_vocab_different_fingerprint(self, berts):
        fp_a = berts._tokenizer_fingerprint(FakeTokenizer(VOCAB_A))
        fp_b = berts._tokenizer_fingerprint(FakeTokenizer(VOCAB_B))
        assert fp_a != fp_b

    def test_do_lower_case_changes_fingerprint(self, berts):
        fp_keep = berts._tokenizer_fingerprint(FakeTokenizer(VOCAB_A, do_lower_case=False))
        fp_lower = berts._tokenizer_fingerprint(FakeTokenizer(VOCAB_A, do_lower_case=True))
        assert fp_keep != fp_lower

    def test_no_get_vocab_never_shares(self, berts):
        class WeirdTok:
            pass
        fp1 = berts._tokenizer_fingerprint(WeirdTok())
        fp2 = berts._tokenizer_fingerprint(WeirdTok())
        assert fp1 != fp2  # 不可证明等价 → 按对象身份隔离


class TestGroupingByFingerprint:
    """load_all 分组键 = (max_length, 词表指纹)。"""

    def test_different_vocab_models_get_separate_groups(self, berts, monkeypatch):
        _install_fake_hf(
            monkeypatch, berts,
            tokenizer_by_path={'org/fake-a': FakeTokenizer(VOCAB_A),
                               'org/fake-b': FakeTokenizer(VOCAB_B)},
            model_by_path={'org/fake-a': FakeModel(), 'org/fake-b': FakeModel()},
        )
        engine = berts.MultiModelSentimentEngine(
            [_mc('fake_a', 'org/fake-a'), _mc('fake_b', 'org/fake-b')]
        )
        loaded = engine.load_all()
        assert loaded == ['fake_a', 'fake_b']
        # 同 max_length 但词表不同 → 两个独立分词组
        assert len(engine._groups) == 2
        for key in engine._groups:
            assert isinstance(key, tuple) and len(key) == 2  # (max_length, fp)

    def test_identical_vocab_models_share_one_group(self, berts, monkeypatch):
        _install_fake_hf(
            monkeypatch, berts,
            tokenizer_by_path={'org/fake-a': FakeTokenizer(VOCAB_A),
                               'org/fake-c': FakeTokenizer(VOCAB_A)},
            model_by_path={'org/fake-a': FakeModel(), 'org/fake-c': FakeModel()},
        )
        engine = berts.MultiModelSentimentEngine(
            [_mc('fake_a', 'org/fake-a'), _mc('fake_c', 'org/fake-c')]
        )
        engine.load_all()
        assert len(engine._groups) == 1
        assert sorted(next(iter(engine._groups.values()))) == ['fake_a', 'fake_c']

    def test_each_model_inferences_on_own_token_ids(self, berts, monkeypatch):
        """核心回归锁: 词表不同的模型各自收到自身 tokenizer 的 token id。

        历史 bug: finbert2 收到 finbert_cn 的 token id (跨词表逐 id 错位)。
        """
        model_a, model_b = FakeModel(), FakeModel()
        _install_fake_hf(
            monkeypatch, berts,
            tokenizer_by_path={'org/fake-a': FakeTokenizer(VOCAB_A),
                               'org/fake-b': FakeTokenizer(VOCAB_B)},
            model_by_path={'org/fake-a': model_a, 'org/fake-b': model_b},
        )
        engine = berts.MultiModelSentimentEngine(
            [_mc('fake_a', 'org/fake-a'), _mc('fake_b', 'org/fake-b')]
        )
        # 本测试验未缓存前向的逐 token-id 路由 (跨词表回归锁); 显式禁用 W8 推理缓存
        # (config 默认 2026-06-29 已翻转为 on) 以确定性走 _run_all_models_uncached。
        engine._cache_enabled = False
        engine.load_all()
        results = engine.run_all_models(['银行不错'])

        assert model_a.seen_input_ids[0][0] == [101, 10, 11, 12, 13, 102]
        assert model_b.seen_input_ids[0][0] == [101, 20, 21, 22, 23, 102]
        # 两个模型都正常出数 (各 1 窗口)
        assert results['fake_a'][0]['num_windows'] == 1
        assert results['fake_b'][0]['num_windows'] == 1


# ============================================================================
# g-berts-02: 失败哨兵 + 逐篇重试 + 标志列 + 2-class 中性=NaN
# ============================================================================

class TestFailureResult:
    """_failure_result 与 _empty_result 严格区分。"""

    def test_failure_result_sentinel_shape(self, berts):
        engine = berts.MultiModelSentimentEngine([])
        engine.loaded_configs['m'] = {
            'label_map': {0: '负面', 1: '中性', 2: '正面'}, 'num_labels': 3,
        }
        r = engine._failure_result('m')
        assert r['num_windows'] == -1
        assert r['label'] is None  # 不冒充 '中性'
        assert all(math.isnan(v) for v in r['probabilities'].values())

    def test_failure_distinct_from_empty(self, berts):
        engine = berts.MultiModelSentimentEngine([])
        empty = engine._empty_result('m')
        failure = engine._failure_result('m')
        assert empty['num_windows'] == 0 and failure['num_windows'] == -1
        assert empty['label'] == '中性' and failure['label'] is None
        # 空文本概率仍是 0.0 (既有契约不变), 失败概率是 NaN
        assert all(v == 0.0 for v in empty['probabilities'].values())
        assert all(math.isnan(v) for v in failure['probabilities'].values())


def _stub_engine(berts, label_map=None, short_name='fake_m'):
    """构造带桩配置的 engine (跳过真实加载)。"""
    if label_map is None:
        label_map = {0: '负面', 1: '中性', 2: '正面'}
    engine = berts.MultiModelSentimentEngine([_mc(short_name, 'org/x', label_map)])
    engine.models[short_name] = object()
    engine.loaded_configs[short_name] = {
        **_mc(short_name, 'org/x', label_map),
        'num_labels': len(label_map),
    }
    return engine


_GOOD = {'label': '正面',
         'probabilities': {'负面': 0.1, '中性': 0.2, '正面': 0.7},
         'num_windows': 1}


class TestBatchFailureRetry:
    """process_all_models: 批级异常 → 逐篇重试一次 → 仅真失败篇写哨兵。"""

    def _run(self, berts, texts):
        engine = _stub_engine(berts)
        calls = {'n': 0}

        def fake_run(batch_texts):
            calls['n'] += 1
            if len(batch_texts) > 1:
                raise RuntimeError('simulated transient GPU failure')
            if batch_texts[0] == 'BAD':
                raise RuntimeError('article-level failure')
            return {'fake_m': [dict(_GOOD)]}

        engine.run_all_models = fake_run
        df = pd.DataFrame({'内容': texts})
        return berts.process_all_models(df, engine, texts), calls

    def test_per_article_retry_isolates_failure(self, berts):
        output, calls = self._run(berts, ['好文', 'BAD', '棒文'])
        cols = output['fake_m']['columns']

        # 1 次批级 + 3 次单篇重试 = 4 次调用 (重试恰好一次)
        assert calls['n'] == 4
        # 仅真失败篇写哨兵; 其余两篇保留真实结果
        assert cols['fake_m_label'] == ['正面', None, '正面']
        assert cols['fake_m_infer_failed'] == [False, True, False]
        assert math.isnan(cols['fake_m_正面'][1])
        assert cols['fake_m_正面'][0] == 0.7
        assert output['fake_m']['num_windows_list'] == [1, -1, 1]

    def test_avg_windows_excludes_failure_sentinel(self, berts):
        output, _ = self._run(berts, ['好文', 'BAD', '棒文'])
        # 均值只算 num_windows >= 0 的篇: mean([1, 1]) == 1.0 (而非含 -1 的 1/3)
        assert output['fake_m']['avg_windows'] == pytest.approx(1.0)

    def test_successful_batch_has_no_failure_flags(self, berts):
        engine = _stub_engine(berts)
        engine.run_all_models = lambda batch_texts: {
            'fake_m': [dict(_GOOD) for _ in batch_texts]
        }
        df = pd.DataFrame({'内容': ['a', 'b']})
        output = berts.process_all_models(df, engine, ['a', 'b'])
        cols = output['fake_m']['columns']
        assert cols['fake_m_infer_failed'] == [False, False]
        assert cols['fake_m_label'] == ['正面', '正面']


class TestTwoClassNeutralNaN:
    """2-class 模型输出端补 中性=NaN 列 (而非 0); 3-class 不受影响。"""

    def test_two_class_model_gets_nan_neutral_column(self, berts):
        engine = _stub_engine(berts, label_map={0: '负面', 1: '正面'},
                              short_name='fake2')
        engine.run_all_models = lambda batch_texts: {
            'fake2': [{'label': '正面',
                       'probabilities': {'负面': 0.3, '正面': 0.7},
                       'num_windows': 1} for _ in batch_texts]
        }
        df = pd.DataFrame({'内容': ['a', 'b']})
        output = berts.process_all_models(df, engine, ['a', 'b'])
        cols = output['fake2']['columns']
        assert 'fake2_中性' in cols
        assert all(math.isnan(v) for v in cols['fake2_中性'])
        # 真实维度不受影响
        assert cols['fake2_正面'] == [0.7, 0.7]

    def test_three_class_model_keeps_real_neutral(self, berts):
        engine = _stub_engine(berts)
        engine.run_all_models = lambda batch_texts: {
            'fake_m': [dict(_GOOD) for _ in batch_texts]
        }
        df = pd.DataFrame({'内容': ['a']})
        output = berts.process_all_models(df, engine, ['a'])
        cols = output['fake_m']['columns']
        assert cols['fake_m_中性'] == [0.2]  # 真实概率, 非 NaN 占位


# ============================================================================
# g-berts-03: num_labels 回退 fail-loud + 极性顺序守卫 raise
# ============================================================================

class TestDeriveLabelMapFromCheckpoint:
    def test_derives_from_english_id2label(self, berts):
        cfg = _FakeConfig(3, {0: 'positive', 1: 'neutral', 2: 'negative'})
        assert berts._derive_label_map_from_checkpoint(cfg, 3) == {
            0: '正面', 1: '中性', 2: '负面'
        }

    def test_string_keys_accepted(self, berts):
        cfg = _FakeConfig(2, {'0': 'negative', '1': 'positive'})
        assert berts._derive_label_map_from_checkpoint(cfg, 2) == {
            0: '负面', 1: '正面'
        }

    def test_unresolvable_labels_return_none(self, berts):
        cfg = _FakeConfig(3, {0: 'LABEL_0', 1: 'LABEL_1', 2: 'LABEL_2'})
        assert berts._derive_label_map_from_checkpoint(cfg, 3) is None

    def test_duplicate_polarity_returns_none(self, berts):
        cfg = _FakeConfig(2, {0: 'positive', 1: 'pos'})
        assert berts._derive_label_map_from_checkpoint(cfg, 2) is None

    def test_count_mismatch_returns_none(self, berts):
        cfg = _FakeConfig(3, {0: 'positive', 1: 'negative'})
        assert berts._derive_label_map_from_checkpoint(cfg, 3) is None


class TestNumLabelsMismatchFailLoud:
    def test_mismatch_with_resolvable_id2label_derives(self, berts, monkeypatch):
        """条数不匹配但 checkpoint id2label 可归一 → 以 checkpoint 顺序推导。"""
        model = FakeModel(num_labels=3,
                          id2label={0: 'neutral', 1: 'positive', 2: 'negative'})
        _install_fake_hf(monkeypatch, berts,
                         {'org/m3': FakeTokenizer(VOCAB_A)}, {'org/m3': model})
        engine = berts.MultiModelSentimentEngine(
            [_mc('m3', 'org/m3', label_map={0: '负面', 1: '正面'})]  # 配置只有 2 条
        )
        loaded = engine.load_all()
        assert loaded == ['m3']
        assert engine.loaded_configs['m3']['label_map'] == {
            0: '中性', 1: '正面', 2: '负面'
        }
        assert engine.loaded_configs['m3']['num_labels'] == 3

    def test_mismatch_with_unresolvable_id2label_raises(self, berts, monkeypatch):
        """条数不匹配且 id2label 不可归一 → 拒绝盲回退 DEFAULT 顺序, raise。"""
        model = FakeModel(num_labels=3,
                          id2label={0: 'LABEL_0', 1: 'LABEL_1', 2: 'LABEL_2'})
        _install_fake_hf(monkeypatch, berts,
                         {'org/mbad': FakeTokenizer(VOCAB_A)}, {'org/mbad': model})
        engine = berts.MultiModelSentimentEngine(
            [_mc('mbad', 'org/mbad', label_map={0: '负面', 1: '正面'})]
        )
        with pytest.raises(RuntimeError, match='无法从'):
            engine.load_all()

    def test_polarity_flip_guard_raises(self, berts, monkeypatch):
        """条数一致但极性顺序对调 (checkpoint 0=pos vs 配置 0=负面) → raise,
        不得以可疑映射出数 (历史仅 warning 放行)。"""
        model = FakeModel(num_labels=3,
                          id2label={0: 'positive', 1: 'neutral', 2: 'negative'})
        _install_fake_hf(monkeypatch, berts,
                         {'org/flip': FakeTokenizer(VOCAB_A)}, {'org/flip': model})
        engine = berts.MultiModelSentimentEngine(
            [_mc('flip', 'org/flip', label_map={0: '负面', 1: '中性', 2: '正面'})]
        )
        with pytest.raises(RuntimeError, match='极性顺序'):
            engine.load_all()

    def test_consistent_config_loads_silently(self, berts, monkeypatch):
        """在产场景 (配置与 checkpoint 逐一吻合) 行为不变: 正常加载。"""
        model = FakeModel(num_labels=3,
                          id2label={0: 'Neutral', 1: 'Positive', 2: 'Negative'})
        _install_fake_hf(monkeypatch, berts,
                         {'org/ok': FakeTokenizer(VOCAB_A)}, {'org/ok': model})
        engine = berts.MultiModelSentimentEngine(
            [_mc('ok', 'org/ok', label_map={0: '中性', 1: '正面', 2: '负面'})]
        )
        assert engine.load_all() == ['ok']
        assert engine.loaded_configs['ok']['label_map'] == {
            0: '中性', 1: '正面', 2: '负面'
        }


# ============================================================================
# g-berts-04: 预期跳过 vs 非预期失败分流
# ============================================================================

class TestLoadFailureFailLoud:
    def test_empty_model_id_is_expected_skip(self, berts, monkeypatch):
        """FINBERT2_MODEL_DIR 未设 → model_id 空串 → graceful skip 不 raise。"""
        _install_fake_hf(monkeypatch, berts, {}, {})
        engine = berts.MultiModelSentimentEngine(
            [_mc('fake_local', '', label_map={0: '负面', 1: '正面'})]
        )
        loaded = engine.load_all()
        assert loaded == []
        assert engine.skipped_expected == ['fake_local']
        assert engine.failed_models == []

    def test_nonexistent_local_path_is_expected_skip(self, berts, monkeypatch):
        _install_fake_hf(monkeypatch, berts, {}, {})
        bad_path = r'C:\nonexistent\finbert2_model_dir_xyz'
        engine = berts.MultiModelSentimentEngine(
            [_mc('fake_local2', bad_path, label_map={0: '负面', 1: '正面'})]
        )
        loaded = engine.load_all()
        assert loaded == []
        assert engine.skipped_expected == ['fake_local2']

    def test_hub_model_failure_raises_by_default(self, berts, monkeypatch):
        """hub 模型瞬态故障 (如 HF 不可达) → strict_models=true (默认) raise。"""
        _install_fake_hf(
            monkeypatch, berts,
            {'org/hub-m': ConnectionError('hf.co unreachable')},
            {'org/hub-m': FakeModel()},
        )
        engine = berts.MultiModelSentimentEngine([_mc('hub_m', 'org/hub-m')])
        with pytest.raises(ConnectionError):
            engine.load_all()
        assert engine.failed_models == ['hub_m']

    def test_strict_models_false_tolerates_failure(self, berts, monkeypatch):
        """strict_models=false: 失败仅记录 (failed_models), 不 raise。"""
        monkeypatch.setitem(berts.BERT_PARAMS, 'strict_models', False)
        _install_fake_hf(
            monkeypatch, berts,
            {'org/hub-m': ConnectionError('hf.co unreachable'),
             'org/ok': FakeTokenizer(VOCAB_A)},
            {'org/hub-m': FakeModel(),
             'org/ok': FakeModel(num_labels=3,
                                 id2label={0: '负面', 1: '中性', 2: '正面'})},
        )
        engine = berts.MultiModelSentimentEngine(
            [_mc('hub_m', 'org/hub-m'), _mc('ok', 'org/ok')]
        )
        loaded = engine.load_all()
        assert loaded == ['ok']
        assert engine.failed_models == ['hub_m']
        assert engine.skipped_expected == []
