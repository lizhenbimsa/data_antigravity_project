# ============================================================
# APEP 新论文初始化脚本 — init_new_paper.py
# 用法: python init_new_paper.py <paper_id> <title> <method>
# 示例: python init_new_paper.py 500 "Clean Slate Laws and Employment" DiD
# ============================================================

import os
import sys
import json
from datetime import datetime

def init_paper(paper_num, title, method="DiD", version=1, contributor="anonymous", model="claude-sonnet-4-20250514"):
    """初始化一个新的 APEP 论文目录结构"""
    
    paper_id = f"apep_{paper_num:04d}"
    version_dir = os.path.join(paper_id, f"v{version}")
    
    # 创建目录结构
    dirs = [
        os.path.join(version_dir, "code"),
        os.path.join(version_dir, "data"),
        os.path.join(version_dir, "figures"),
        os.path.join(version_dir, "tables"),
        os.path.join(version_dir, "output"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"✅ 创建目录: {d}")
    
    # 生成 metadata.json
    metadata = {
        "paper_id": f"{paper_id}_v{version}",
        "title": title,
        "method": method,
        "policy_id": None,
        "contributor": contributor,
        "authoring_model": model,
        "published_at": datetime.now().isoformat(),
        "paper_family_id": paper_id,
        "version": version
    }
    metadata_path = os.path.join(version_dir, "metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"✅ 生成: {metadata_path}")
    
    # 复制代码模板
    template_dir = os.path.join(os.path.dirname(__file__), "04_r_templates")
    code_dir = os.path.join(version_dir, "code")
    
    r_templates = {
        "00_packages.R": "00_packages.R",
        "01_fetch_data.R": "01_fetch_data.R",
        "05_figures.R": "05_figures.R",
    }
    
    if method == "DiD":
        r_templates["03_main_analysis.R"] = "03_main_analysis_did.R"
    elif method == "RDD":
        r_templates["03_main_analysis.R"] = "03_main_analysis_rdd.R"
    
    for target_name, source_name in r_templates.items():
        src = os.path.join(template_dir, source_name)
        dst = os.path.join(code_dir, target_name)
        if os.path.exists(src):
            with open(src, 'r', encoding='utf-8') as sf:
                content = sf.read()
            with open(dst, 'w', encoding='utf-8') as df:
                df.write(content)
            print(f"✅ 复制模板: {dst}")
    
    # 生成空的 initial_plan.md
    plan_template = os.path.join(os.path.dirname(__file__), "08_config_templates", "initial_plan_template.md")
    if os.path.exists(plan_template):
        with open(plan_template, 'r', encoding='utf-8') as f:
            plan_content = f.read()
        plan_path = os.path.join(version_dir, "initial_plan.md")
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(plan_content.replace("{论文标题}", title))
        print(f"✅ 生成: {plan_path}")
    
    # 生成空的 research_plan.md
    rp_path = os.path.join(version_dir, "research_plan.md")
    with open(rp_path, 'w', encoding='utf-8') as f:
        f.write(f"# Research Plan: {title}\n\n> 此文件为 initial_plan.md 的可演进版本。\n\n")
    print(f"✅ 生成: {rp_path}")
    
    # 生成 REPLICATION.md
    repl_template = os.path.join(os.path.dirname(__file__), "08_config_templates", "REPLICATION_template.md")
    if os.path.exists(repl_template):
        with open(repl_template, 'r', encoding='utf-8') as f:
            repl_content = f.read()
        repl_path = os.path.join(version_dir, "REPLICATION.md")
        with open(repl_path, 'w', encoding='utf-8') as f:
            f.write(repl_content.replace("apep_XXXX", paper_id).replace("{论文标题}", title))
        print(f"✅ 生成: {repl_path}")
    
    print(f"\n🎉 论文目录初始化完成: {version_dir}")
    print(f"\n下一步:")
    print(f"  1. 编辑 {version_dir}/initial_plan.md — 填写研究计划")
    print(f"  2. 编辑 {code_dir}/01_fetch_data.R — 配置 API 和变量")
    print(f"  3. 运行 Rscript {code_dir}/00_packages.R — 安装依赖")
    print(f"  4. 运行 Rscript {code_dir}/01_fetch_data.R — 获取数据")
    print(f"  5. 运行 Rscript {code_dir}/03_main_analysis.R — 执行分析")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python init_new_paper.py <paper_number> <title> [method] [contributor] [model]")
        print("示例: python init_new_paper.py 500 \"Clean Slate Laws\" DiD")
        sys.exit(1)
    
    paper_num = int(sys.argv[1])
    title = sys.argv[2]
    method = sys.argv[3] if len(sys.argv) > 3 else "DiD"
    contributor = sys.argv[4] if len(sys.argv) > 4 else "anonymous"
    model = sys.argv[5] if len(sys.argv) > 5 else "claude-sonnet-4-20250514"
    
    init_paper(paper_num, title, method, contributor=contributor, model=model)
