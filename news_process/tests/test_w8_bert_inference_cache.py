"""tests/test_w8_bert_inference_cache.py — W8 BERT 推理缓存 (LLM/嵌入/BERT 三族统一缓存收口) 守卫。

验证 2026-06-29 W8 落地的 BERT 推理缓存:
  - default-off 字节中性 (run_all_models dispatch → 逐字旧实现 _run_all_models_uncached);
  - 启用路径正确性 (命中免重算 / 只前向 miss 子集 / 逐模型部分命中整文重算);
  - 复合键对全部 11 维敏感 (anti silent-stale);
  - no-NaN 写边界 (失败哨兵绝不进缓存; allow_nan=False fail-loud);
  - enabled 须确定性模式 (fail-fast);
  - 三库路径统一 helper resolve_cache_db_path。

测试本身轻量: 不加载真实模型、不做 stage 23 真推理。用假 models/loaded_configs/composites +
stub _run_all_models_uncached 演练缓存**管道**。cold==warm / partial-miss==full 的**数值等价**
无法在本机 (无真实模型) 测, 唯由执行计划 §5.2② 受控实证门把关 (DEFERRED 生产机)。

torch 在 tone_berts 模块顶层 import, 故需 torch 的用例经 ``_berts()`` 内 importorskip 跳过;
``resolve_cache_db_path`` (core/caching, torch-free) 的用例无条件运行。
"""

from __future__ import annotations

import json
import math
import os

import pytest

from news_process.core.caching import LLMCache, resolve_cache_db_path

_BERT_VER = None  # 由 _berts() 填充, 供模块外引用


def _berts():
    """惰性 import tone_berts (需 torch); CI light 无 torch 时跳过相关用例。"""
    pytest.importorskip("torch")
    import news_process.pipeline.sentiment.tone_berts as m
    return m


def _make_engine(Mod, tmp_path, names=("m1",), enabled=True):
    """构造一个绕过 load_all 的引擎: 注入假 models/loaded_configs/composites + (可选) 打开缓存。"""
    cfgs = [
        {"short_name": n, "model_id": f"/x/{n}", "max_length": 512,
         "label_map": {0: "负面", 1: "正面"}, "description": n}
        for n in names
    ]
    eng = Mod.MultiModelSentimentEngine(cfgs)
    eng.models = {n: object() for n in names}
    eng.loaded_configs = {
        n: {"short_name": n, "max_length": 512, "num_labels": 2,
            "label_map": {0: "负面", 1: "正面"}}
        for n in names
    }
    if enabled:
        eng._cache_enabled = True
        eng._cache = LLMCache(str(tmp_path / "lm.db"))
        eng._composites = {n: f"comp-{n}" for n in names}
    return eng


def _result(label="正面", num_windows=1):
    return {"label": label, "probabilities": {"负面": 0.1, "正面": 0.9},
            "num_windows": num_windows}


# ── 三库统一路径 helper (torch-free, 无条件运行) ──

def test_resolve_cache_db_path():
    assert os.path.basename(resolve_cache_db_path("/d", "production")) == "_llm_cache.db"
    assert os.path.basename(resolve_cache_db_path("/d", "validation")) == "_llm_cache_validation.db"
    assert os.path.basename(resolve_cache_db_path("/d", "local_model")) == "_local_model_cache.db"
    # 默认 kind = production
    assert os.path.basename(resolve_cache_db_path("/d")) == "_llm_cache.db"
    with pytest.raises(ValueError):
        resolve_cache_db_path("/d", "nope")


# ── default-off 字节中性 (golden-safe 的承重) ──

def test_default_off_delegates_to_uncached():
    Mod = _berts()
    eng = Mod.MultiModelSentimentEngine(
        [{"short_name": "m1", "model_id": "/x/m1", "max_length": 512,
          "label_map": {0: "负面", 1: "正面"}, "description": "m1"}])
    # 无 config inference_cache → 默认关
    assert eng._cache_enabled is False
    assert eng._cache is None
    calls = []
    sentinel = {"m1": [_result()]}
    eng._run_all_models_uncached = lambda texts: (calls.append(list(texts)) or sentinel)
    out = eng.run_all_models(["a", "b"])
    assert out is sentinel, "off 路径必须原样转发 _run_all_models_uncached 的返回"
    assert calls == [["a", "b"]], "off 路径每次都直调 uncached, 无缓存介入"


# ── 启用路径: 命中免重算 ──

def test_enabled_caches_and_skips_uncached_on_second_call(tmp_path):
    Mod = _berts()
    eng = _make_engine(Mod, tmp_path, names=("m1",))
    calls = []

    def stub(texts):
        calls.append(list(texts))
        return {"m1": [_result() for _ in texts]}

    eng._run_all_models_uncached = stub
    r1 = eng.run_all_models(["a", "b"])
    assert calls == [["a", "b"]], "首跑全 miss → 整批前向"
    calls.clear()
    r2 = eng.run_all_models(["a", "b"])
    assert calls == [], "二跑全命中 → uncached 不再被调"
    assert r2["m1"][0]["label"] == "正面" and r2["m1"][0]["num_windows"] == 1
    # 命中值经 JSON 往返与首跑逐字段相等
    assert r2["m1"][0] == r1["m1"][0]


# ── 启用路径: 只前向 miss 子集 ──

def test_partial_miss_only_forwards_missing(tmp_path):
    Mod = _berts()
    eng = _make_engine(Mod, tmp_path, names=("m1",))
    calls = []

    def stub(texts):
        calls.append(list(texts))
        return {"m1": [_result() for _ in texts]}

    eng._run_all_models_uncached = stub
    eng.run_all_models(["a", "b"])          # 播种 2 篇
    assert calls[-1] == ["a", "b"]
    calls.clear()
    eng.run_all_models(["a", "b", "c", "d", "e"])  # 2 旧 + 3 新
    assert calls == [["c", "d", "e"]], "只前向 3 篇 miss 子集 (有序), 旧 2 篇命中不重算"


# ── 启用路径: 逐模型部分命中 → 整文重算全部模型 (确定性下逐字段相等) ──

def test_per_model_partial_hit_reforwards_all_models(tmp_path):
    Mod = _berts()
    eng = _make_engine(Mod, tmp_path, names=("m1", "m2"))
    # 仅给 m1 播种文本 X (m2 仍 miss)
    eng._cache.put("comp-m1", "X", json.dumps(_result(), ensure_ascii=False, allow_nan=False),
                   prompt_version=Mod._BERT_CACHE_VERSION)
    calls = []

    def stub(texts):
        calls.append(list(texts))
        return {sn: [_result(label="负面") for _ in texts] for sn in ("m1", "m2")}

    eng._run_all_models_uncached = stub
    out = eng.run_all_models(["X"])
    assert calls == [["X"]], "X 对 m2 miss → 整文重算全部模型 (含已命中的 m1)"
    assert out["m1"][0] is not None and out["m2"][0] is not None
    # m1 被 fresh 覆盖 (确定性下与缓存值相等; 此处 stub 给不同值以证'整文重算'确实发生)
    assert out["m1"][0]["label"] == "负面"


# ── 复合键对全部 11 维敏感 (anti silent-stale) ──

def test_compute_composite_sensitive_to_every_dim():
    Mod = _berts()
    base = dict(short_name="m1", max_length=512, num_labels=2,
                label_map={0: "负面", 1: "正面"}, vocab_fp="vfp",
                det_mode="cpu_strict", amp=False, stride=0.5,
                inf_batch=128, art_batch=200, ckpt="ck")
    k0 = Mod._compute_composite(**base)
    # 同参 → 同键
    assert Mod._compute_composite(**base) == k0
    variations = {
        "short_name": "m2", "max_length": 256, "num_labels": 3,
        "label_map": {0: "正面", 1: "负面"},  # 极性重排 (num_labels 不变) 仍须改键
        "vocab_fp": "vfp2", "det_mode": "gpu_strict", "amp": True,
        "stride": 0.25, "inf_batch": 64, "art_batch": 100, "ckpt": "ck2",
    }
    for dim, val in variations.items():
        d = dict(base)
        d[dim] = val
        assert Mod._compute_composite(**d) != k0, f"复合键对 {dim} 不敏感 → silent stale 风险"


# ── no-NaN 写边界: 失败哨兵绝不进缓存; allow_nan=False fail-loud ──

def test_no_nan_boundary_and_json_roundtrip(tmp_path):
    Mod = _berts()
    eng = _make_engine(Mod, tmp_path, names=("m1",), enabled=False)
    # _empty_result: 全有限, 无 NaN (run_all_models 内合法的"空文本"结果)
    empty = eng._empty_result("m1")
    assert all(math.isfinite(v) for v in empty["probabilities"].values())
    assert empty["num_windows"] == 0
    # _failure_result: NaN 概率 / num_windows=-1 (仅 process_all_models 异常兜底产生, 不在 run_all_models 内)
    fail = eng._failure_result("m1")
    assert all(math.isnan(v) for v in fail["probabilities"].values())
    assert fail["num_windows"] == -1
    # 写边界硬门: 用 allow_nan=False 序列化哨兵 → 直接 raise (绝不静默写 NaN token 污染 golden)
    with pytest.raises(ValueError):
        json.dumps(fail, ensure_ascii=False, allow_nan=False)
    # 有限真实结果经 allow_nan=False 往返字节无损
    real = {"label": "正面", "probabilities": {"负面": 0.1234, "正面": 0.8766}, "num_windows": 2}
    assert json.loads(json.dumps(real, ensure_ascii=False, allow_nan=False)) == real


# ── enabled 异常路径: 失败哨兵不进缓存 + good 行入缓存 (process_all_models 集成) ──

def test_failure_sentinel_never_cached(tmp_path):
    Mod = _berts()
    pd = pytest.importorskip("pandas")
    eng = _make_engine(Mod, tmp_path, names=("m1",))
    POISON = "POISON_TEXT"
    GOOD, GOOD2 = "good_a", "good_b"

    def stub(texts):
        if any(t == POISON for t in texts):
            raise RuntimeError("forced forward failure on poison text")
        return {"m1": [_result() for _ in texts]}

    eng._run_all_models_uncached = stub
    df = pd.DataFrame({"内容": [GOOD, POISON, GOOD2]})
    out = Mod.process_all_models(df, eng, [GOOD, POISON, GOOD2])

    # poison 行写失败哨兵 (num_windows=-1 → infer_failed True), good 行正常
    failed_flags = out["m1"]["columns"]["m1_infer_failed"]
    assert failed_flags == [False, True, False]
    # good 行入缓存; poison 绝不入缓存 (uncached raise 前无 put)
    assert eng._cache.get("comp-m1", GOOD, prompt_version=Mod._BERT_CACHE_VERSION) is not None
    assert eng._cache.get("comp-m1", GOOD2, prompt_version=Mod._BERT_CACHE_VERSION) is not None
    assert eng._cache.get("comp-m1", POISON, prompt_version=Mod._BERT_CACHE_VERSION) is None


# ── enabled 须确定性模式 (fail-fast) ──

def test_fail_fast_requires_deterministic_mode(tmp_path, monkeypatch):
    Mod = _berts()
    monkeypatch.setattr(Mod, "_DETERMINISTIC_MODE", "off")
    # 用一个不存在的本地路径 model → load_all graceful skip 全部模型 (loaded_names 空),
    # 但 _cache_enabled=True 仍触发 fail-fast (与 loaded_names 无关)。
    eng = Mod.MultiModelSentimentEngine(
        [{"short_name": "x", "model_id": "Z:\\nonexistent_w8_path",
          "max_length": 512, "label_map": {0: "负面", 1: "正面"}, "description": "x"}])
    eng._cache_enabled = True
    with pytest.raises(RuntimeError, match="deterministic_mode"):
        eng.load_all()


# ── checkpoint 指纹: 本地内容/大小敏感 + hub/不存在退化 ──

def test_checkpoint_fingerprint_local_and_hub(tmp_path):
    Mod = _berts()
    d = tmp_path / "mdl"
    d.mkdir()
    (d / "config.json").write_text('{"a": 1}', encoding="utf-8")
    (d / "model.safetensors").write_bytes(b"x" * 100)
    fp1 = Mod._checkpoint_fingerprint(str(d))
    assert fp1.startswith("local:")
    assert Mod._checkpoint_fingerprint(str(d)) == fp1, "同盘内容 → 指纹稳定"
    (d / "model.safetensors").write_bytes(b"x" * 200)   # 改权重文件大小
    assert Mod._checkpoint_fingerprint(str(d)) != fp1, "权重大小变 → 指纹变"
    (d / "model.safetensors").write_bytes(b"x" * 100)   # 还原大小
    (d / "config.json").write_text('{"a": 2}', encoding="utf-8")  # 改 config 内容
    assert Mod._checkpoint_fingerprint(str(d)) != fp1, "config 内容变 → 指纹变"
    # hub id (非本地路径) / 不存在路径 → no-ckpt: 退化
    assert Mod._checkpoint_fingerprint("yiyanghkust/finbert-tone-chinese") == \
        "no-ckpt:yiyanghkust/finbert-tone-chinese"
    assert Mod._checkpoint_fingerprint(str(tmp_path / "nope")).startswith("no-ckpt:")


# ── 第 12 维: _BERT_CACHE_VERSION (经 prompt_version) bump → 旧条目 miss ──

def test_cache_version_bump_invalidates(tmp_path):
    Mod = _berts()
    cache = LLMCache(str(tmp_path / "v.db"))
    payload = json.dumps(_result(), ensure_ascii=False, allow_nan=False)
    cache.put("comp-m1", "txt", payload, prompt_version=Mod._BERT_CACHE_VERSION)
    assert cache.get("comp-m1", "txt", prompt_version=Mod._BERT_CACHE_VERSION) is not None
    assert cache.get("comp-m1", "txt", prompt_version=Mod._BERT_CACHE_VERSION + "-BUMPED") is None


# ── load_all 字段接线: _build_composites 把运行期值喂进复合键 (无需真实模型) ──

def test_build_composites_wires_runtime_values():
    Mod = _berts()

    class _FakeTok:
        def get_vocab(self):
            return {"a": 0, "b": 1}

    eng = Mod.MultiModelSentimentEngine(
        [{"short_name": "m1", "model_id": "/x/m1", "max_length": 512,
          "label_map": {0: "负面", 1: "正面"}, "description": "m1"}])
    eng.loaded_configs = {"m1": {"short_name": "m1", "max_length": 512, "num_labels": 2,
                                 "label_map": {0: "负面", 1: "正面"}}}
    eng.tokenizers = {"m1": _FakeTok()}
    eng._model_paths = {"m1": "/x/m1"}
    eng._build_composites(["m1"])
    comp = eng._composites["m1"]
    assert comp.startswith("m1|maxlen=512|labels=2|"), "短名/maxlen/num_labels 字段接线正确"
    assert f"ibs={Mod.INFERENCE_BATCH_SIZE}" in comp and f"apb={Mod.ARTICLES_PER_BATCH}" in comp
    # 改 cfg max_length → 复合串变 (证 cfg 字段真实接入, 非硬编码)
    eng.loaded_configs["m1"]["max_length"] = 256
    eng._build_composites(["m1"])
    assert eng._composites["m1"] != comp
