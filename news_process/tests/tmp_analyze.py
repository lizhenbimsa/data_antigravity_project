import os
import re

doc_dir = r"docs\paper"
keywords = ["不足", "局限性", "卡点", "致命卡点", "落差", "待改进", "未能实现", "局限", "改进空间", "致命风险", "致命缺陷", "缺点", "问题", "优化空间"]
report = {}

for root, _, files in os.walk(doc_dir):
    for f in files:
        if f.endswith('.md'):
            fpath = os.path.join(root, f)
            try:
                with open(fpath, 'r', encoding='utf-8') as file:
                    content = file.readlines()
            except:
                continue
            
            for i, line in enumerate(content):
                if any(kw in line for kw in keywords) and ("项目" in line or "当前" in line or "本项目" in line or "未实现" in line or "缺乏" in line or "风险" in line or "落差" in line or "缺陷" in line or "卡点" in line):
                    if f not in report:
                        report[f] = []
                    report[f].append((i+1, line.strip()))

with open(r"limitations_summary.txt", "w", encoding='utf-8') as out:
    for f, lines in report.items():
        out.write(f"\n--- {f} ---\n")
        for num, line in lines:
            out.write(f"L{num}: {line}\n")
print(f"Found matches in {len(report)} files.")
