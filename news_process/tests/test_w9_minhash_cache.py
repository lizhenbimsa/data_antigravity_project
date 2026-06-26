"""W9: MinHash 签名 sidecar — bytes 序列化正确性 (CF-9) + save/load 往返 + 键敏感性。

纯 CPU, 不走 multiprocessing (直接构造 MinHash, 测缓存读写/键逻辑)。
"""
import logging

import numpy as np
import pandas as pd
from datasketch import MinHash

from news_process.pipeline.preprocess.dedup import ArticleDeduplicator


def test_bytes_roundtrip_preserves_uint64_incl_over_2_63():
    # CF-9: hashvalues 是 uint64; bytes 路径逐位保留 (含 >2^63), list[int]→int64 会符号回绕。
    arr = np.array([0, 1, 2**32 - 1, 2**63 + 7, 2**64 - 1], dtype=np.uint64)
    back = np.frombuffer(arr.astype("<u8").tobytes(), dtype="<u8").astype(np.uint64)
    assert np.array_equal(arr, back)


def test_minhash_reconstruct_from_hashvalues_preserves_signature():
    m = MinHash(num_perm=64)
    for tok in ("ab", "bc", "cd", "de"):
        m.update(tok.encode("utf-8"))
    back = np.frombuffer(m.hashvalues.astype("<u8").tobytes(), dtype="<u8").astype(np.uint64)
    m2 = MinHash(num_perm=64, hashvalues=back)
    assert np.array_equal(m.hashvalues, m2.hashvalues)
    assert m.jaccard(m2) == 1.0  # 重建签名与原签名 Jaccard=1 (逐位等价)


def _make_dedup(tmp_path):
    cfg = {
        "deduplication": {"minhash_permutations": 32, "ngram_size": 3,
                          "jaccard_similarity_threshold": 0.8},
        "paths": {"media_weights_file": str(tmp_path / "none.json")},
    }
    return ArticleDeduplicator(cfg, logging.getLogger("test_w9"))


def test_cache_save_load_roundtrip_and_key_sensitivity(tmp_path):
    d = _make_dedup(tmp_path)
    df = pd.DataFrame({d.COL_COMBINED: ["银行金科一二三", "another news text", "第三条内容"]})
    sigs = {}
    for idx, txt in df[d.COL_COMBINED].items():
        m = MinHash(num_perm=32)
        m.update(str(txt).encode("utf-8"))
        sigs[idx] = m
    series = pd.Series(sigs)
    cdir = str(tmp_path / "mh")

    assert d._load_minhash_cache(df, cdir) is None          # 冷: 无缓存
    d._save_minhash_cache(df, series, cdir)                 # 落盘 (bytes)
    loaded = d._load_minhash_cache(df, cdir)                # 命中
    assert loaded is not None
    for i in series.index:
        assert np.array_equal(series[i].hashvalues, loaded[i].hashvalues)  # 逐位等价

    # 改语料 → 键变 → 缓存 miss (内容寻址敏感性)
    df2 = pd.DataFrame({d.COL_COMBINED: ["银行金科一二三", "another news text", "CHANGED"]})
    assert d._load_minhash_cache(df2, cdir) is None


def test_save_load_handles_uint64_over_2_63(tmp_path):
    # F6: 真 _save/_load 走合成 >2^63 hashvalues — 证 bytes 路径逐位保 uint64。
    # 若回退到 list[int]→parquet int64, >2^63 会符号回绕, 本测试必红 (CF-9 守护)。
    d = _make_dedup(tmp_path)
    df = pd.DataFrame({d.COL_COMBINED: ["t1", "t2"]})
    sigs = {}
    for idx in df.index:
        m = MinHash(num_perm=32)
        arr = np.arange(32, dtype=np.uint64)
        arr[0] = 2**63 + 7        # > 2^63: int64 会变负
        arr[1] = 2**64 - 1        # uint64 上界
        m.hashvalues = arr
        sigs[idx] = m
    series = pd.Series(sigs)
    cdir = str(tmp_path / "mh")
    d._save_minhash_cache(df, series, cdir)
    loaded = d._load_minhash_cache(df, cdir)
    assert loaded is not None
    for i in series.index:
        assert loaded[i].hashvalues.dtype == np.uint64
        assert np.array_equal(series[i].hashvalues, loaded[i].hashvalues)  # >2^63 逐位等价


def test_datasketch_version_gate(tmp_path, monkeypatch):
    # F6: datasketch 版本入键作版本门 — 换版本 → key 变 → 不命中 (防跨版本 banding 阈值漂移误命中)。
    d = _make_dedup(tmp_path)
    df = pd.DataFrame({d.COL_COMBINED: ["t1", "t2"]})
    m = MinHash(num_perm=32)
    m.update(b"x")
    series = pd.Series({i: m for i in df.index})
    cdir = str(tmp_path / "mh")
    d._save_minhash_cache(df, series, cdir)
    assert d._load_minhash_cache(df, cdir) is not None            # 同版本命中
    import importlib.metadata as md
    real = md.version
    monkeypatch.setattr(md, "version", lambda pkg: "999.99" if pkg == "datasketch" else real(pkg))
    assert d._load_minhash_cache(df, cdir) is None                # 版本门: 换 datasketch 版本不命中


def test_tokenizer_code_version_gate(tmp_path, monkeypatch):
    # F2: 分词代码版本入键 — bump _MINHASH_TOKENIZER_VERSION → key 变 → 不命中
    # (防改 _clean_and_tokenize/CLEANING_TABLE 后陈旧签名掩盖测度变更)。
    d = _make_dedup(tmp_path)
    df = pd.DataFrame({d.COL_COMBINED: ["t1", "t2"]})
    m = MinHash(num_perm=32)
    m.update(b"x")
    series = pd.Series({i: m for i in df.index})
    cdir = str(tmp_path / "mh")
    d._save_minhash_cache(df, series, cdir)
    assert d._load_minhash_cache(df, cdir) is not None
    monkeypatch.setattr(type(d), "_MINHASH_TOKENIZER_VERSION", "v2-test-bump")
    assert d._load_minhash_cache(df, cdir) is None                # 分词代码版本门生效
