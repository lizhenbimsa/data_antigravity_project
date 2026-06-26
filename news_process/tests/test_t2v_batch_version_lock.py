"""W1: batch_size ↔ text_pipeline_version 版本纪律锁 (FP 敏感超参当版本维度)。

见 core/caching.py docstring §5-C。纯 config 读取, 无 production data / 无 network。
守: 改 config/features.yaml::embedding_robustness.batch_size 必同 diff bump text_pipeline_version,
否则旧 _t2v 缓存静默命中、新批 matmul 舍入路径的值永不落盘 = silent staleness。
"""
import re

from news_process.core.caching import LLMCache
from news_process.core.config import load_config


def _t2v_cfg() -> dict:
    return load_config()["embedding_robustness"]


def test_t2v_batch_and_version_lockstep():
    # 同一断言对锁定: 改 batch_size 或 version 任一而不同步改另一 → 本测试红, 强制
    # reviewer 在同一 diff 处理两者 (FP 敏感超参当版本维度, §5-C)。
    cfg = _t2v_cfg()
    assert (cfg["batch_size"], cfg["text_pipeline_version"]) == (128, "v2-2026-05-29-t2v"), (
        "batch_size 与 text_pipeline_version 必须 lockstep: 改 batch_size / device / dtype / "
        "torch 版本时, 同 diff bump text_pipeline_version 并更新本断言的两个期望值。"
    )


def test_t2v_version_is_lintable():
    # 用 re.search 不加结尾锚 ($): 现值尾部是 -t2v, 加 $ 会误红 (日期段在中间)。
    ver = _t2v_cfg()["text_pipeline_version"]
    assert re.search(r"^v\d+-\d{4}-\d{2}-\d{2}", ver), f"version 须形如 vN-YYYY-MM-DD-...: {ver!r}"


def test_batch_size_not_in_cache_key():
    # 回归锁 (F12 加固): batch_size 根本不是 LLMCache.make_key 的参数 → 它无从进键 →
    # _t2v 缓存键不随 batch_size 变 → 故必须靠 text_pipeline_version 绑定 (W1 的前提)。
    import inspect
    params = set(inspect.signature(LLMCache.make_key).parameters)
    assert "batch_size" not in params, f"make_key 不应含 batch_size 维度: {sorted(params)}"
    # 确定性 sanity: 同实参 → 同键
    k = LLMCache.make_key("m", "txt", prompt_version="v2-2026-05-29-t2v", temperature=0.0)
    assert k == LLMCache.make_key("m", "txt", prompt_version="v2-2026-05-29-t2v", temperature=0.0)
