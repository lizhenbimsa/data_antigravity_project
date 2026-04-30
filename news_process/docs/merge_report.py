import os

docs_dir = r"f:\WiseSearch\data_antigravity_project\news_process\docs"
chapters = [
    "Project_Report_Chapter_1.md",
    "Project_Report_Chapter_2.md",
    "Project_Report_Chapter_3.md",
    "Project_Report_Chapter_4.md",
    "Project_Report_Chapter_5.md",
    "Project_Report_Chapter_6.md",
    "Project_Report_Chapter_7.md",
    "Project_Report_Chapter_8.md",
]

full_report_path = os.path.join(docs_dir, "Project_Report_Full.md")

with open(full_report_path, "w", encoding="utf-8") as outfile:
    for chapter in chapters:
        chapter_path = os.path.join(docs_dir, chapter)
        if os.path.exists(chapter_path):
            with open(chapter_path, "r", encoding="utf-8") as infile:
                outfile.write(infile.read())
                outfile.write("\n\n")

print(f"✅ Successfully merged {len(chapters)} chapters into {full_report_path}")
