import re
from pathlib import Path

def clean_file(path_str):
    p = Path(path_str)
    if not p.exists():
        return
    text = p.read_text(encoding="utf-8").strip()
    # 匹配 ```stata 以及 ```
    text = re.sub(r"^```(stata)?\s*\n", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n```\s*$", "", text)
    p.write_text(text, encoding="utf-8")
    print(f"Cleaned {path_str}")

# 您可以根据纸张ID批量清理
clean_file("paper_0500/v1/code/01_fetch_data.do")
clean_file("paper_0500/v1/code/03_main_analysis.do")
clean_file("paper_0500/v1/code/05_figures.do")
