#!/usr/bin/env bash
# Round 1 / Item 8 — triple-run audit driver.
# Runs each of the 3 entrypoints three times consecutively, captures exit code
# and a digest of key deterministic outputs. Writes a single audit log.

set +e
LOG=logs/audit/round1_item8_$(date +%Y%m%d_%H%M%S).log
mkdir -p logs/audit

PY="/f/Anaconda3/python.exe"

print() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

digest_parquets() {
    # SHA256 of all key panel parquets after a run
    "$PY" -c "
import hashlib, os, sys
PATHS = [
    'data/processed/00_preprocessing.parquet',
    'data/processed/11_bank_news.parquet',
    'data/processed/12_fintech_news.parquet',
    'data/processed/14_news_with_ctx.parquet',
    'data/processed/15_fintech_intensity.parquet',
    'data/processed/16_article_alignment.parquet',
    'data/processed/21_tone_llms.parquet',
    'data/processed/22_tone_words.parquet',
    'data/processed/24_herd_decay.parquet',
    'data/processed/40_panel_yearly.parquet',
]
for p in PATHS:
    if not os.path.exists(p):
        print(f'  MISS  {p}')
        continue
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1<<20), b''):
            h.update(chunk)
    print(f'  {h.hexdigest()[:16]}  {p}  {os.path.getsize(p)}')
"
}

run_n() {
    local label="$1"; shift
    local cmd="$*"
    print "===== START $label ====="
    print "CMD: $cmd"
    eval "$cmd" >> "$LOG" 2>&1
    rc=$?
    print "EXIT: $rc"
    print "DIGEST after $label:"
    digest_parquets | tee -a "$LOG"
    print "===== END   $label ====="
    return $rc
}

print "Audit log: $LOG"
print "Repository state: $(git rev-parse HEAD)"

# Group A: main pipeline x 3
for i in 1 2 3; do
    run_n "A.$i run_pipeline_function" "$PY run_pipeline_function.py" || {
        print "A.$i FAILED with rc=$?"; exit 11
    }
done

# Group B: validation pipeline x 3
for i in 1 2 3; do
    run_n "B.$i run_pipeline_validation" "$PY run_pipeline_validation.py" || {
        print "B.$i FAILED with rc=$?"; exit 12
    }
done

# Group C: run_paper x 3 (no-arg = list mode, deterministic exit 0)
for i in 1 2 3; do
    run_n "C.$i run_paper" "$PY run_paper.py" || {
        print "C.$i FAILED with rc=$?"; exit 13
    }
done

print "ALL 9 INVOCATIONS PASSED"
exit 0
