"""最终完整性检查：验证所有修改文件的最终状态"""
import sys, os, threading
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import numpy as np
import pandas as pd

passed = 0
failed = 0

def check(n, c, d=''):
    global passed, failed
    if c:
        passed += 1
        print(f'  PASS: {n}')
    else:
        failed += 1
        print(f'  FAIL: {n} {d}')


def _make_test_tempdir():
    base_dir = os.path.join(os.getcwd(), ".test_tmp")
    os.makedirs(base_dir, exist_ok=True)
    path = os.path.join(base_dir, uuid.uuid4().hex)
    os.makedirs(path, exist_ok=False)
    return path

# === F1: llm_cache.py 完整性 ===
print("=== F1: llm_cache final state ===")
from utils.llm_cache import LLMCache

db = os.path.join(_make_test_tempdir(), "f.db")
c = LLMCache(db)
check("has _lock", hasattr(c, "_lock") and isinstance(c._lock, type(threading.Lock())))
check("has _conn", c._conn is not None)
c.put("m", "p", "r")
check("basic flow", c.get("m", "p") == "r")
c.close()
check("close sets None", c._conn is None)
c.close()  # double close
check("double close safe", True)
print()

# === F2: epoch path ===
print("=== F2: epoch path final ===")
dates = [pd.NaT, pd.Timestamp("2024-01-02"), pd.Timestamp("2024-12-31")]
_epoch = pd.Timestamp("1970-01-01")
dates_num = np.array(
    [(d - _epoch).days if pd.notna(d) else np.nan for d in dates],
    dtype=np.float64)
check("valid dates get real values",
      not np.isnan(dates_num[1]) and not np.isnan(dates_num[2]))
check("NaT gets NaN", np.isnan(dates_num[0]))
td = np.abs(dates_num[2] - dates_num[1])
check("time diff correct (364 days)", td == 364, f"got {td}")
print()

# === F3: 21_tone_llms.py structure ===
print("=== F3: 21_tone_llms structure ===")
with open("21_tone_llms.py", "r", encoding="utf-8") as f:
    src = f.read()
check("import LLMCache", "from utils.llm_cache import LLMCache" in src)
check("cache init", "cache = LLMCache(cache_db)" in src)
close_count = src.count("cache.close()")
check(f"cache.close() count={close_count}",
      close_count == 4, "should be 4 (3 early + 1 normal)")
check("no try/finally residue", "finally:" not in src)
# L431 在 if 块内合法有 8 空格缩进，只检查 main 末尾的缩进
lines = src.split('\n')
for i, line in enumerate(lines):
    if 'log_stage_summary' in line and 'cache.close()' in lines[i+1] if i+1 < len(lines) else False:
        check('normal-path log_stage_summary has 4-space indent',
              line.startswith('    log_stage_summary') and not line.startswith('        log_stage_summary'))
print()

# === F4: config.yaml ===
print("=== F4: config.yaml ===")
with open("config/config.yaml", "r", encoding="utf-8") as f:
    cfg = f.read()
check("no pandarallel in comments", "pandarallel" not in cfg)
check("herd_detection section exists", "herd_detection:" in cfg)
check("similarity_threshold: 0.35", "similarity_threshold: 0.35" in cfg)
check("time_window_days: 7", "time_window_days: 7" in cfg)
print()

# === F5: run_pipeline_function.py ===
print("=== F5: pipeline OSError ===")
with open("run_pipeline_function.py", "r", encoding="utf-8") as f:
    rp = f.read()
check("OSError handling", "OSError" in rp)
print()

# === F6: requirements.txt ===
print("=== F6: requirements.txt ===")
with open("requirements.txt", "r", encoding="utf-8") as f:
    req = f.read()
check("no pandarallel", "pandarallel" not in req)
check("scikit-learn present", "scikit-learn" in req)
print()

# === F7: 24_herd_decay_processor.py ===
print("=== F7: herd_decay structure ===")
with open("24_herd_decay_processor.py", "r", encoding="utf-8") as f:
    hd = f.read()
check("pairwise_distances imported", "pairwise_distances" in hd)
check("epoch approach used", "1970-01-01" in hd)
check("no dates[0] in code (ok in comments)",
      hd.replace('#', '').count('dates[0]') == 0 or
      all('# ' in line for line in hd.split('\n') if 'dates[0]' in line))
check("dual path exists", "n_articles <= 2000" in hd)
print()

# === F8: 00_preprocessing.py ===
print("=== F8: preprocessing config hash ===")
with open("00_preprocessing.py", "r", encoding="utf-8") as f:
    pp = f.read()
check("config_hash function", "_compute_config_hash" in pp)
check("MD5 hash", "hashlib.md5" in pp)
check("sort_keys=True", "sort_keys=True" in pp)
check("Parquet metadata", "config_hash" in pp)
print()

print("=" * 50)
print(f"TOTAL: {passed} passed, {failed} failed")
if failed == 0:
    print("ALL FINAL INTEGRITY CHECKS PASSED")
else:
    print("SOME CHECKS FAILED")
    sys.exit(1)
