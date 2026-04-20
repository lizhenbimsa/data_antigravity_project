"""从 45_panel_export_main.py 提取 STATA_LABELS 字典，生成 codebook.md

用法:
    python docs/generate_codebook.py

输出:
    docs/codebook.md — 面板数据变量代码手册
"""
import re, ast, os

src = os.path.join(os.path.dirname(__file__), '..', '45_panel_export_main.py')
with open(src, 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'STATA_LABELS\s*=\s*(\{.*?\n\s*\})', content, re.DOTALL)
if not match:
    raise ValueError("未找到 STATA_LABELS 定义")

dict_text = match.group(1)
dict_text = re.sub(r'#[^\n]*', '', dict_text)  # strip 注释
labels = ast.literal_eval(dict_text)

with open(os.path.join(os.path.dirname(__file__), 'codebook.md'), 'w', encoding='utf-8') as f:
    f.write("# 面板数据变量代码手册\n\n")
    f.write(f"> 自动生成自 `45_panel_export_main.py` STATA_LABELS\n\n")
    f.write(f"共 {len(labels)} 个变量\n\n")
    f.write("| Stata 变量名 | 标签 |\n|---|---|\n")
    for var, label in sorted(labels.items()):
        f.write(f"| `{var}` | {label} |\n")
print(f"[OK] codebook.md generated, {len(labels)} variables")
