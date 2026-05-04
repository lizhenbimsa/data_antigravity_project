"""
审核测试脚本 — 对本次所有变更进行白盒测试
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hashlib
import json
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
# Test 1: LLMCache
# ============================================
print("=== Test 1: LLMCache ===")
# Phase 6a: utils.llm_cache → news_process.core.caching
from news_process.core.caching import LLMCache

db_path = os.path.join(_make_test_tempdir(), "test_cache.db")
cache = LLMCache(db_path)

check("T1.1: empty size", cache.size() == 0)
check("T1.2: miss returns None", cache.get("gpt-4", "hello") is None)

cache.put("gpt-4", "hello", "response_1")
check("T1.3: hit after put", cache.get("gpt-4", "hello") == "response_1")
check("T1.4: size after put", cache.size() == 1)

cache.put("claude-4", "hello", "response_2")
check("T1.5a: model isolation gpt", cache.get("gpt-4", "hello") == "response_1")
check("T1.5b: model isolation claude", cache.get("claude-4", "hello") == "response_2")
check("T1.5c: size 2", cache.size() == 2)

cache.put("gpt-4", "hello", "response_updated")
check("T1.6: idempotent overwrite", cache.get("gpt-4", "hello") == "response_updated")
check("T1.6b: size unchanged", cache.size() == 2)

cache.put("gpt-4", "中文提示词", "中文结果")
check("T1.7: unicode prompt", cache.get("gpt-4", "中文提示词") == "中文结果")

cache.close()
cache.close()  # double close should not error
check("T1.8: double close safe", True)

# Key collision test
c2 = LLMCache(os.path.join(_make_test_tempdir(), "test2.db"))
c2.put("model_a:extra", "prompt", "r1")
c2.put("model_a", "extra:prompt", "r2")
check("T1.9a: key collision prevention",
      c2.get("model_a:extra", "prompt") == "r1")
check("T1.9b: key collision prevention 2",
      c2.get("model_a", "extra:prompt") == "r2")
c2.close()

os.unlink(db_path)
print()

# ============================================
# Test 2: Config Hash
# ============================================
print("=== Test 2: Config Hash ===")
# Phase 6a: utils.helpers → news_process.core.config
from news_process.core.config import load_config
CONFIG = load_config()
PARAMS = CONFIG["preprocessing"]

def _compute_config_hash():
    relevant = {
        "media_types_to_include": PARAMS.get("media_types_to_include"),
        "media_names_to_exclude": PARAMS.get("media_names_to_exclude"),
        "required_columns": PARAMS.get("required_columns"),
        "key_columns_for_na_check": PARAMS.get("key_columns_for_na_check"),
        "content_min_length": PARAMS.get("content_min_length"),
        "content_max_length": PARAMS.get("content_max_length"),
        "title_min_length": PARAMS.get("title_min_length"),
    }
    return hashlib.md5(
        json.dumps(relevant, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()

h1 = _compute_config_hash()
h2 = _compute_config_hash()
check("T2.1: hash stability", h1 == h2)
check("T2.2: MD5 length", len(h1) == 32)

# Verify list/None serialization safety
relevant_test = {
    "media_types_to_include": ["newspaper"],
    "content_min_length": None,
    "title_min_length": 2,
}
s = json.dumps(relevant_test, sort_keys=True, ensure_ascii=False)
h_test = hashlib.md5(s.encode()).hexdigest()
check("T2.3: list/None serialization", len(h_test) == 32)
print()

# ============================================
# Test 3: Vectorized NaT handling (critical)
# ============================================
print("=== Test 3: Vectorized NaT ===")

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

# T3.1: all valid dates
dates1 = [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-03"),
          pd.Timestamp("2024-01-05"), pd.Timestamp("2024-01-20")]
sim = np.array([[1,.9,.8,.7],[.9,1,.85,.6],[.8,.85,1,.5],[.7,.6,.5,1]])
lr = loop_compute(dates1, sim, 0.35, 7)
vr = vec_compute(dates1, sim, 0.35, 7)
check("T3.1: all valid dates", np.array_equal(lr, vr), f"loop={lr} vec={vr}")

# T3.2: mixed NaT
dates2 = [pd.Timestamp("2024-01-01"), pd.NaT,
          pd.Timestamp("2024-01-03"), pd.NaT]
lr2 = loop_compute(dates2, sim, 0.35, 7)
vr2 = vec_compute(dates2, sim, 0.35, 7)
check("T3.2: mixed NaT", np.array_equal(lr2, vr2), f"loop={lr2} vec={vr2}")

# T3.3: all NaT
dates3 = [pd.NaT, pd.NaT, pd.NaT, pd.NaT]
lr3 = loop_compute(dates3, sim, 0.35, 7)
vr3 = vec_compute(dates3, sim, 0.35, 7)
check("T3.3: all NaT", np.array_equal(lr3, vr3), f"loop={lr3} vec={vr3}")

# T3.4: dates far apart
dates4 = [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-03-01"),
          pd.Timestamp("2024-06-01"), pd.Timestamp("2024-12-01")]
lr4 = loop_compute(dates4, sim, 0.35, 7)
vr4 = vec_compute(dates4, sim, 0.35, 7)
check("T3.4: far apart dates", np.array_equal(lr4, vr4), f"loop={lr4} vec={vr4}")

# T3.5: NaT + far valid date (critical edge case from plan review round 7)
dates5 = [pd.Timestamp("2024-01-01"), pd.NaT, pd.Timestamp("2024-12-31")]
sim3 = np.array([[1,.9,.4],[.9,1,.8],[.4,.8,1]])
lr5 = loop_compute(dates5, sim3, 0.35, 7)
vr5 = vec_compute(dates5, sim3, 0.35, 7)
check("T3.5: NaT+far date mix", np.array_equal(lr5, vr5), f"loop={lr5} vec={vr5}")

# T3.6: only 2 articles
dates6 = [pd.Timestamp("2024-01-01"), pd.NaT]
sim2 = np.array([[1,.9],[.9,1]])
lr6 = loop_compute(dates6, sim2, 0.35, 7)
vr6 = vec_compute(dates6, sim2, 0.35, 7)
check("T3.6: 2 articles with NaT", np.array_equal(lr6, vr6), f"loop={lr6} vec={vr6}")

# T3.7: threshold boundary
dates7 = [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")]
sim_boundary = np.array([[1, 0.35],[0.35, 1]])
lr7 = loop_compute(dates7, sim_boundary, 0.35, 7)
vr7 = vec_compute(dates7, sim_boundary, 0.35, 7)
check("T3.7: exact threshold", np.array_equal(lr7, vr7), f"loop={lr7} vec={vr7}")

# T3.8: below threshold
sim_below = np.array([[1, 0.349],[0.349, 1]])
lr8 = loop_compute(dates7, sim_below, 0.35, 7)
vr8 = vec_compute(dates7, sim_below, 0.35, 7)
check("T3.8: below threshold", np.array_equal(lr8, vr8), f"loop={lr8} vec={vr8}")
print()

# ============================================
# Test 4: generate_codebook.py
# ============================================
print("=== Test 4: Codebook ===")
cb_path = os.path.join("docs", "codebook.md")
check("T4.1: codebook exists", os.path.exists(cb_path))
if os.path.exists(cb_path):
    with open(cb_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    check("T4.2: >200 lines", len(lines) > 200, f"lines={len(lines)}")
    check("T4.3: header present", lines[0].startswith("#"))
    check("T4.4: table header",
          any("Stata" in l and "|" in l for l in lines[:10]))
print()

# ============================================
# Test 5: requirements.txt
# ============================================
print("=== Test 5: requirements.txt ===")
with open("requirements.txt", "r", encoding="utf-8") as f:
    req_content = f.read()
check("T5.1: pandarallel removed", "pandarallel" not in req_content)
check("T5.2: joblib still present", "joblib" in req_content)
check("T5.3: scikit-learn present", "scikit-learn" in req_content)
print()

# ============================================
# Summary
# ============================================
print("=" * 50)
print(f"TOTAL: {passed} passed, {failed} failed")
if failed == 0:
    print("ALL TESTS PASSED")
else:
    print("SOME TESTS FAILED")
    sys.exit(1)
