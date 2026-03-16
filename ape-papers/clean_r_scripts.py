import re
from pathlib import Path

def clean_file(path_str):
    p = Path(path_str)
    if not p.exists():
        return
    text = p.read_text(encoding="utf-8").strip()
    text = re.sub(r"^```[rR]?\s*\n", "", text)
    text = re.sub(r"\n```\s*$", "", text)
    p.write_text(text, encoding="utf-8")
    print(f"Cleaned {path_str}")

clean_file("apep_0500/v1/code/01_fetch_data.R")
clean_file("apep_0500/v1/code/03_main_analysis.R")
clean_file("apep_0500/v1/code/05_figures.R")
