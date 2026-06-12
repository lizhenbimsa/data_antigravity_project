"""
第四轮审核：极端边界 + 并发安全 + 配置回归深度测试

⚠ 现状注记 (2026-06-12): Test D 读取 docs/codebook.md, 但 docs/ 目录已整体删除
(commit 1698bda5) → 跑到 Test D 会 FileNotFoundError 崩溃。Test A/B/C (LLMCache
并发 / config hash / 向量化边界) 仍可独立验证 canonical core API; Test E 对
CHANGELOG.md 缺失已有优雅跳过。如需完整跑通, 须先重建 docs/codebook.md。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hashlib
import json
import threading
import uuid

import numpy as np
import pandas as pd

passed = 0
failed = 0

def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS: {name}")
    else:
        failed += 1
        print(f"  FAIL: {name} {detail}")


def _make_test_tempdir():
    base_dir = os.path.join(os.getcwd(), ".test_tmp")
    os.makedirs(base_dir, exist_ok=True)
    path = os.path.join(base_dir, uuid.uuid4().hex)
    os.makedirs(path, exist_ok=False)
    return path

# ============================================
# Test A: LLMCache 并发安全 + 极端边界
# ============================================
print("=== Test A: LLMCache Concurrency & Edge Cases ===")
# Phase 6a: utils.llm_cache → news_process.core.caching
from news_process.core.caching import LLMCache

# A1: 空 prompt
db = os.path.join(_make_test_tempdir(), "conc.db")
c = LLMCache(db)
c.put("model", "", "empty_prompt_response")
check("A1: empty prompt", c.get("model", "") == "empty_prompt_response")

# A2: 空 model_id
c.put("", "some prompt", "empty_model_response")
check("A2: empty model_id", c.get("", "some prompt") == "empty_model_response")

# A3: 空 prompt + 空 model_id
c.put("", "", "all_empty")
check("A3: all empty strings", c.get("", "") == "all_empty")

# A4: 超长 prompt (100KB)
long_prompt = "x" * 100_000
c.put("model", long_prompt, "long_resp")
check("A4: 100KB prompt", c.get("model", long_prompt) == "long_resp")

# A5: 特殊字符 prompt  
special = "SELECT * FROM llm_cache; DROP TABLE llm_cache; --"
c.put("model", special, "sql_injection_safe")
check("A5: SQL injection safe", c.get("model", special) == "sql_injection_safe")
check("A5b: table intact", c.size() > 0)

# A6: 多线程并发写入安全
errors = []
def writer(cache, thread_id):
    try:
        for i in range(50):
            cache.put(f"thread_{thread_id}", f"prompt_{i}", f"response_{thread_id}_{i}")
    except Exception as e:
        errors.append(f"Thread {thread_id}: {e}")

threads = []
for t in range(4):
    th = threading.Thread(target=writer, args=(c, t))
    threads.append(th)
    th.start()
for th in threads:
    th.join()

check("A6: concurrent write no errors", len(errors) == 0, str(errors))

# A7: 验证并发写入数据完整性
all_ok = True
for t in range(4):
    for i in range(50):
        r = c.get(f"thread_{t}", f"prompt_{i}")
        if r != f"response_{t}_{i}":
            all_ok = False
            break
check("A7: concurrent data integrity", all_ok)

# A8: close 后 get 应当抛异常 (防御性检查)
c.close()
try:
    c.get("model", "test")
    check("A8: get after close raises", False, "should have raised")
except Exception:
    check("A8: get after close raises", True)

# A9: close 后 put 应当抛异常
try:
    c.put("model", "test", "val")
    check("A9: put after close raises", False, "should have raised")
except Exception:
    check("A9: put after close raises", True)

print()

# ============================================
# Test B: Config Hash — 配置回归 + 字段覆盖
# ============================================
print("=== Test B: Config Hash Regression ===")
# Phase 6a: utils.helpers → news_process.core.config
from news_process.core.config import load_config

CONFIG = load_config()
PARAMS = CONFIG["preprocessing"]

# B1: 验证所有哈希字段确实存在于配置中
hash_fields = [
    "media_types_to_include",
    "media_names_to_exclude",
    "required_columns",
    "key_columns_for_na_check",
    "content_min_length",
    "content_max_length",
    "title_min_length",
]
for field in hash_fields:
    check(f"B1: field '{field}' in config", field in PARAMS, f"missing from config")

# B2: 哈希对字段变更的敏感性
def compute_hash(overrides=None):
    relevant = {f: PARAMS.get(f) for f in hash_fields}
    if overrides:
        relevant.update(overrides)
    return hashlib.md5(
        json.dumps(relevant, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()

base_hash = compute_hash()
check("B2a: hash changes on content_min_length",
      compute_hash({"content_min_length": 999}) != base_hash)
check("B2b: hash changes on title_min_length",
      compute_hash({"title_min_length": 999}) != base_hash)
check("B2c: hash changes on media_types",
      compute_hash({"media_types_to_include": ["new_type"]}) != base_hash)

# B3: 验证 json.dumps 对 list 顺序敏感（期望行为）
h1 = hashlib.md5(json.dumps({"a": [1, 2]}, sort_keys=True).encode()).hexdigest()
h2 = hashlib.md5(json.dumps({"a": [2, 1]}, sort_keys=True).encode()).hexdigest()
check("B3: list order affects hash", h1 != h2)

# B4: PyArrow 元数据读写完整性
import pyarrow as pa
import pyarrow.parquet as pq

test_parquet = os.path.join(_make_test_tempdir(), "test.parquet")
table = pa.table({"col": [1, 2, 3]})
meta = {b"config_hash": b"abc123"}
table = table.replace_schema_metadata(meta)
pq.write_table(table, test_parquet)

# 读回验证
schema = pq.read_schema(test_parquet)
check("B4a: metadata written", schema.metadata is not None)
check("B4b: config_hash readable",
      schema.metadata.get(b"config_hash", b"").decode() == "abc123")
check("B4c: missing key returns empty",
      schema.metadata.get(b"nonexistent", b"").decode() == "")
os.unlink(test_parquet)

print()

# ============================================
# Test C: 向量化 — 极端边界
# ============================================
print("=== Test C: Vectorization Extreme Edge Cases ===")

def loop_compute(dates, sim_matrix, threshold, window):
    n = len(dates)
    counts = np.zeros(n, dtype=int)
    for i in range(n):
        for j in range(i):
            date_i = dates[i]
            date_j = dates[j]
            if pd.notna(date_i) and pd.notna(date_j):
                delta = abs((date_i - date_j).days)
                if delta > window:
                    continue
            if sim_matrix[i, j] >= threshold:
                counts[i] += 1
    return counts

def vec_compute(dates, sim_matrix, threshold, window):
    n = len(dates)
    _epoch = pd.Timestamp('1970-01-01')
    dates_num = np.array(
        [(d - _epoch).days if pd.notna(d) else np.nan for d in dates],
        dtype=np.float64)
    time_diff = np.abs(np.subtract.outer(dates_num, dates_num))
    time_diff = np.nan_to_num(time_diff, nan=0.0)
    valid_mask = (time_diff <= window) & np.tril(
        np.ones((n, n), dtype=bool), k=-1)
    herd_mask = (sim_matrix >= threshold) & valid_mask
    return herd_mask.sum(axis=1)

# C1: 单篇文章(n=1) — 不应崩溃
dates_1 = [pd.Timestamp("2024-01-01")]
sim_1 = np.array([[1.0]])
lr = loop_compute(dates_1, sim_1, 0.35, 7)
vr = vec_compute(dates_1, sim_1, 0.35, 7)
check("C1: single article", np.array_equal(lr, vr) and lr[0] == 0)

# C2: 两篇文章，恰好在窗口边界 (delta == TIME_WINDOW_DAYS)
dates_boundary = [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-08")]
sim_2 = np.array([[1.0, 0.9], [0.9, 1.0]])
lr2 = loop_compute(dates_boundary, sim_2, 0.35, 7)
vr2 = vec_compute(dates_boundary, sim_2, 0.35, 7)
check("C2: exact window boundary", np.array_equal(lr2, vr2), f"loop={lr2} vec={vr2}")

# C3: 恰好超出窗口 (delta == TIME_WINDOW_DAYS + 1)  
dates_out = [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-09")]
lr3 = loop_compute(dates_out, sim_2, 0.35, 7)
vr3 = vec_compute(dates_out, sim_2, 0.35, 7)
check("C3: just outside window", np.array_equal(lr3, vr3), f"loop={lr3} vec={vr3}")

# C4: 全部相同日期
dates_same = [pd.Timestamp("2024-01-01")] * 5
sim_5 = np.ones((5, 5)) * 0.9
np.fill_diagonal(sim_5, 1.0)
lr4 = loop_compute(dates_same, sim_5, 0.35, 7)
vr4 = vec_compute(dates_same, sim_5, 0.35, 7)
check("C4: all same date", np.array_equal(lr4, vr4), f"loop={lr4} vec={vr4}")

# C5: 全部相似度为 0 (无跟风)  
sim_zero = np.zeros((4, 4))
np.fill_diagonal(sim_zero, 1.0)
dates_c5 = [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02"),
            pd.Timestamp("2024-01-03"), pd.Timestamp("2024-01-04")]
lr5 = loop_compute(dates_c5, sim_zero, 0.35, 7)
vr5 = vec_compute(dates_c5, sim_zero, 0.35, 7)
check("C5: zero similarity", np.array_equal(lr5, vr5) and all(v == 0 for v in lr5))

# C6: 全部相似度为 1 (全部跟风)
sim_all = np.ones((4, 4))
lr6 = loop_compute(dates_c5, sim_all, 0.35, 7)
vr6 = vec_compute(dates_c5, sim_all, 0.35, 7)
check("C6: full similarity", np.array_equal(lr6, vr6), f"loop={lr6} vec={vr6}")

# C7: 首项 NaT, 其余日期有效
dates_c7 = [pd.NaT, pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03")]
sim_c7 = np.array([[1, .8, .6], [.8, 1, .9], [.6, .9, 1]])
lr7 = loop_compute(dates_c7, sim_c7, 0.35, 7)
vr7 = vec_compute(dates_c7, sim_c7, 0.35, 7)
check("C7: first NaT rest valid", np.array_equal(lr7, vr7), f"loop={lr7} vec={vr7}")

# C8: NaT 与有效日期交替
dates_c8 = [pd.NaT, pd.Timestamp("2024-01-02"), pd.NaT, pd.Timestamp("2024-01-04"),
            pd.NaT, pd.Timestamp("2024-01-06")]
sim_c8 = np.ones((6, 6)) * 0.5
np.fill_diagonal(sim_c8, 1.0)
lr8 = loop_compute(dates_c8, sim_c8, 0.35, 7)
vr8 = vec_compute(dates_c8, sim_c8, 0.35, 7)
check("C8: alternating NaT", np.array_equal(lr8, vr8), f"loop={lr8} vec={vr8}")

# C9: threshold = 0 (一切都算匹配)
lr9 = loop_compute(dates_c5, sim_c7[:3,:3] if len(dates_c5) == 3 else sim_zero, 0.0, 7)
vr9 = vec_compute(dates_c5, sim_c7[:3,:3] if len(dates_c5) == 3 else sim_zero, 0.0, 7)
check("C9: threshold=0", np.array_equal(lr9, vr9), f"loop={lr9} vec={vr9}")

# C10: threshold = 1.0 (仅自身匹配, 但 tril k=-1 已排除自身)
lr10 = loop_compute(dates_c5, sim_all, 1.0, 7)
vr10 = vec_compute(dates_c5, sim_all, 1.0, 7)
check("C10: threshold=1.0", np.array_equal(lr10, vr10), f"loop={lr10} vec={vr10}")

# C11: window = 0 (仅同日文章)
lr11 = loop_compute(dates_c5, sim_all, 0.35, 0)
vr11 = vec_compute(dates_c5, sim_all, 0.35, 0)
check("C11: window=0", np.array_equal(lr11, vr11), f"loop={lr11} vec={vr11}")

# C12: dates[0]=NaT + 相距很远的有效日期 (曾触发 CRITICAL bug 的场景)
dates_c12 = [pd.NaT, pd.Timestamp("2024-01-02"), pd.Timestamp("2024-12-31")]
sim_c12 = np.array([[1,.9,.4],[.9,1,.8],[.4,.8,1]])
lr12 = loop_compute(dates_c12, sim_c12, 0.35, 7)
vr12 = vec_compute(dates_c12, sim_c12, 0.35, 7)
check("C12: dates[0]=NaT+far valid", np.array_equal(lr12, vr12), f"loop={lr12} vec={vr12}")

print()

# ============================================
# Test D: generate_codebook.py 输出完整性
# ============================================
print("=== Test D: Codebook Completeness ===")
cb_path = os.path.join("docs", "codebook.md")
with open(cb_path, "r", encoding="utf-8") as f:
    cb_content = f.read()
    cb_lines = cb_content.strip().split("\n")

# D1: 每行变量都有管道符分隔
table_lines = [l for l in cb_lines if l.startswith("| `")]
check("D1: variable count matches header",
      f"{len(table_lines)}" in cb_content, f"found {len(table_lines)} var rows")

# D2: 无空标签
empty_labels = [l for l in table_lines if l.strip().endswith("| |")]
check("D2: no empty labels", len(empty_labels) == 0, f"found {len(empty_labels)}")

# D3: 无重复变量
vars_list = [l.split("|")[1].strip() for l in table_lines]
check("D3: no duplicate variables", len(vars_list) == len(set(vars_list)),
      f"total={len(vars_list)} unique={len(set(vars_list))}")

print()

# ============================================
# Test E: CHANGELOG.md 格式
# ============================================
print("=== Test E: CHANGELOG Format ===")
if os.path.exists("CHANGELOG.md"):
    with open("CHANGELOG.md", "r", encoding="utf-8") as f:
        cl = f.read()
    check("E1: has header", cl.startswith("# CHANGELOG"))
    check("E2: has date", "2026-04-20" in cl)
    check("E3: has sections", "### " in cl)
    check("E4: mentions llm_cache.py", "llm_cache.py" in cl)
    check("E5: mentions pandarallel", "pandarallel" in cl)
else:
    check("E0: CHANGELOG.md optional when absent", True)
print()

# ============================================
# Summary (汇总)
# ============================================
print("=" * 50)
print(f"TOTAL: {passed} passed, {failed} failed")
if failed == 0:
    print("ALL DEEP AUDIT TESTS PASSED")
else:
    print("SOME TESTS FAILED")
    sys.exit(1)
