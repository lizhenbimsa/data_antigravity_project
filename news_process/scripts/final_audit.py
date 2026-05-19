#!/usr/bin/env python3
"""最终审查脚本"""
import os
import re

import pandas as pd

print('=' * 70)
print('FINAL AUDIT - Stata Integration Review')
print('=' * 70)
print()

# 1. Panel data
df = pd.read_parquet('data/processed/40_panel_yearly.parquet')
print('[1] Panel Data Verification')
print('-' * 70)
print(f'  Shape:       {df.shape[0]:,} rows x {df.shape[1]:,} cols')
print(f'  Banks:       {df["target_bank"].nunique()}')
print(f'  Year range:  {df["year"].min()} - {df["year"].max()}')
print(f'  Missing key: target_bank={df["target_bank"].isna().sum()}, year={df["year"].isna().sum()}')
print()

# 2. Stata do files
print('[2] Stata Do Files')
print('-' * 70)
do_files = sorted([f for f in os.listdir('stata') if f.endswith('.do')])
print(f'  Total files: {len(do_files)}')

total_lines = 0
total_labels = 0
label_counts = {}

for f in do_files:
    path = os.path.join('stata', f)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
        lines = len(content.split('\n'))
        matches = re.findall(r'^label variable (\S+)', content, re.MULTILINE)
        total_lines += lines
        total_labels += len(matches)
        label_counts[f] = (lines, len(matches))

print(f'  Total lines: {total_lines:,}')
print(f'  Total labels: {total_labels:,}')
print()
print('  File breakdown:')
for f, (lines, labels) in sorted(label_counts.items()):
    print(f'    {f:40s} {lines:4d} lines  {labels:5d} labels')
print()

# 3. Label coverage
print('[3] Label Coverage Analysis')
print('-' * 70)
all_cols = set(df.columns)
labeled_vars = set()

for f in do_files:
    path = os.path.join('stata', f)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
        matches = re.findall(r'label variable (\S+)', content)
        labeled_vars.update(matches)

# Only count labels for actual dataset columns
labeled_in_dataset = labeled_vars & all_cols
coverage = len(labeled_in_dataset) / len(all_cols) * 100
unlabeled = all_cols - labeled_vars

print(f'  Dataset columns:     {len(all_cols)}')
print(f'  Labels in files:     {len(labeled_vars)}')
print(f'  Labels in dataset:   {len(labeled_in_dataset)}')
print(f'  Coverage:            {coverage:.1f}%')
print(f'  Unlabeled:           {len(unlabeled)}')

if unlabeled:
    print()
    print('  WARNING: Unlabeled variables found:')
    for v in sorted(unlabeled)[:10]:
        print(f'    - {v}')
    if len(unlabeled) > 10:
        print(f'    ... and {len(unlabeled)-10} more')
else:
    print('  [OK] All dataset variables are labeled!')
print()

# 4. Check for duplicate labels
print('[4] Duplicate Label Check')
print('-' * 70)
all_labels = []
for f in do_files:
    path = os.path.join('stata', f)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
        matches = re.findall(r'label variable (\S+)', content)
        all_labels.extend(matches)

from collections import Counter

label_counts_dict = Counter(all_labels)
duplicates = {k: v for k, v in label_counts_dict.items() if v > 1}
if duplicates:
    print(f'  Found {len(duplicates)} duplicate labels:')
    for var, count in sorted(duplicates.items())[:10]:
        print(f'    {var}: {count} times')
    if len(duplicates) > 10:
        print(f'    ... and {len(duplicates)-10} more')
else:
    print('  [OK] No duplicate labels')
print()

# 5. Documents
print('[5] Documentation Check')
print('-' * 70)
docs = [
    'stata/README.md',
    'STATA_INTEGRATION_SUMMARY.md',
    'PROBLEM_RESOLUTION_REPORT.md',
    'FINAL_COMPLETION_REPORT.md',
]
total_doc_size = 0
for doc in docs:
    if os.path.exists(doc):
        size = os.path.getsize(doc) / 1024
        total_doc_size += size
        print(f'  [OK] {doc:45s} {size:6.1f} KB')
    else:
        print(f'  [--] {doc:45s} MISSING')
print(f'  Total docs size: {total_doc_size:.1f} KB')
print()

# 6. Python scripts
print('[6] Python Scripts')
print('-' * 70)
scripts = [
    'scripts/convert_parquet_to_stata.py',
    'scripts/generate_all_labels.py',
]
for script in scripts:
    if os.path.exists(script):
        size = os.path.getsize(script) / 1024
        with open(script, 'r', encoding='utf-8') as f:
            lines = len(f.readlines())
        print(f'  [OK] {script:45s} {lines:4d} lines  {size:6.1f} KB')
    else:
        print(f'  [--] {script:45s} MISSING')
print()

# 7. Final summary
print('=' * 70)
print('AUDIT SUMMARY')
print('=' * 70)

checks = {
    'Panel data complete': df.shape[0] > 0 and df.shape[1] > 0,
    'All key cols present': 'target_bank' in df.columns and 'year' in df.columns,
    'No key missing values': df['target_bank'].isna().sum() == 0 and df['year'].isna().sum() == 0,
    'All do files present': len(do_files) >= 17,
    '100% label coverage': len(unlabeled) == 0,
    'No duplicate labels': len(duplicates) == 0,
    'All docs present': all(os.path.exists(d) for d in docs),
    'All scripts present': all(os.path.exists(s) for s in scripts),
}

passed = sum(checks.values())
total = len(checks)

for check, result in checks.items():
    status = '[PASS]' if result else '[FAIL]'
    print(f'  {status} {check}')

print()
print(f'Result: {passed}/{total} checks passed')
if passed == total:
    print('[OK] ALL CHECKS PASSED - Project is production-ready!')
else:
    print(f'[!] {total-passed} checks failed - review needed')
