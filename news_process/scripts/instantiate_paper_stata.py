"""scripts/instantiate_paper_stata.py — 第 10/11 篇 Stata 模板实例化.

把 papers/<paper_id>/stata_templates/*.do.tmpl 复制到
papers/<paper_id>/replication/code/*.do (无 {{}} 占位符的情况下等价于 copy).

设计:
- 默认实例化两篇 paper (bank_media_disagreement + bank_news_clarity)
- 输出到 papers/<paper_id>/replication/code/, output/tables/, output/figures/
- README.md 含运行指南

用户运行:
    python news_process/scripts/instantiate_paper_stata.py
    # 然后在 Stata 19:
    cd "F:/WiseSearch/data_antigravity_project"
    do "news_process/papers/bank_media_disagreement/replication/code/00_master.do"
"""
from __future__ import annotations

import argparse
from pathlib import Path

PAPERS = ['bank_media_disagreement', 'bank_news_clarity']


def instantiate_paper(paper_id: str, project_root: Path) -> Path:
    """实例化单 paper 的所有 .do.tmpl 到 replication/code/."""
    tmpl_dir = project_root / 'news_process' / 'papers' / paper_id / 'stata_templates'
    repl_dir = project_root / 'news_process' / 'papers' / paper_id / 'replication'
    code_dir = repl_dir / 'code'
    out_tables = repl_dir / 'output' / 'tables'
    out_figures = repl_dir / 'output' / 'figures'

    if not tmpl_dir.exists():
        print(f"  [FAIL] {paper_id}: template dir 不存在 {tmpl_dir}")
        return None

    for d in (code_dir, out_tables, out_figures):
        d.mkdir(parents=True, exist_ok=True)

    n_files = 0
    for tpl_path in sorted(tmpl_dir.glob('*.do.tmpl')):
        out_name = tpl_path.stem  # 去 .tmpl 后缀
        out_path = code_dir / out_name
        content = tpl_path.read_text(encoding='utf-8')
        # V3.7.0 第 10/11 篇模板暂无 {{}} 占位符 (Stata local 替代),
        # 此处仅 copy. 未来若加 PROJECT_ROOT 等占位符, 在此 substitute.
        out_path.write_text(content, encoding='utf-8')
        n_files += 1
        print(f"  [OK]{tpl_path.name} -> {out_path.relative_to(project_root)}")

    # 生成 README.md
    readme = repl_dir / 'README.md'
    readme.write_text(_make_readme(paper_id, n_files), encoding='utf-8')
    print(f"  [OK]README.md -> {readme.relative_to(project_root)}")

    return repl_dir


def _make_readme(paper_id: str, n_files: int) -> str:
    title_zh = {
        'bank_media_disagreement': '第 10 篇 bank_media_disagreement',
        'bank_news_clarity': '第 11 篇 bank_news_clarity',
    }.get(paper_id, paper_id)

    return f"""# {title_zh} Stata Replication Package

> instantiated from `news_process/papers/{paper_id}/stata_templates/`
> Stata 19+ required ({n_files} .do files).

## 运行步骤

### 前置准备（用户必做）

1. **数据准备**:
   - `data/processed/40_panel_yearly.dta` (stage 45/46 输出, 含 treatment 列)

2. **Stata 19** 已安装并在 PATH (StataMP-64.exe 或 stata-mp).

### 跑通

```stata
* 启动 Stata 19, 修改 00_master.do 中 project_root 为本地路径
cd "F:/WiseSearch/data_antigravity_project"
do "news_process/papers/{paper_id}/replication/code/00_master.do"
```

或命令行批处理 (Windows, /b = 后台批处理, 跑完自动退出不弹「已完成」框):
```
"C:\\Program Files\\StataNow19\\StataMP-64.exe" /b do "news_process/papers/{paper_id}/replication/code/00_master.do"
```

### 输出

- `output/tables/*.tex` — booktabs LaTeX (esttab 生成)
- `output/figures/*.eps` — 事件研究 / coefficient plots (如有 figure 模板)
- Stata log → 默认 stdout, 重定向到 `replication/log_{paper_id}.smcl`

## 输出文件清单

本包共实例化 {n_files} 个 .do 文件, 内容来自 `news_process/papers/{paper_id}/stata_templates/`
下实际存在的 *.do.tmpl (各 paper 模板集不同)。完整清单请直接查看 `code/` 目录,
或运行 `papers/_common/stata_runner.py` 的 `list-templates` 子命令。一般包含
orchestrator (`00_master.do`) + 包安装 + 数据准备 + 各表格/图脚本。

## 故障排除

- **`use *.dta` fail**: 检查 stage 45/46 已跑且 `40_panel_yearly.dta` 已生成
- **`reghdfe not found`**: `00_install_packages.do` 失败, 手动 ssc install reghdfe
- **encoding 错误**: Stata 19 默认 UTF-8, 旧版本需 `set unicode_locale_default zh-CN`

## 学术锚定（per paper_spec.yaml）

- {paper_id == 'bank_media_disagreement' and 'Diether-Malloy-Scherbina (2002) JF + Cookson-Niessner (2020) JF (DOI 10.1111/jofi.12852) + Bushman-Williams (2012) JAE + Acharya 2016 RFS' or 'Bushman-Williams (2012) JAE + Bushee (2010) JAR + Loughran-McDonald (2014) JF + Acharya 2016 RFS'}
- Risk-taking outcome: Laeven-Levine (2009) JFE Z-score framework

## 维护说明

本 replication 包由 `scripts/instantiate_paper_stata.py` 实例化.
未来若 paper_spec.yaml::treatment 变更或模板增删, 重新跑此脚本即可.
"""


def main():
    parser = argparse.ArgumentParser(description='Instantiate paper 10/11 Stata templates')
    parser.add_argument('--papers', nargs='+', default=PAPERS,
                        help='Paper IDs to instantiate (default: both)')
    parser.add_argument('--project-root', type=Path,
                        default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()

    print(f"Project root: {args.project_root}")
    print(f"Papers: {args.papers}")
    print()

    for paper_id in args.papers:
        print(f"=== Instantiating {paper_id} ===")
        result = instantiate_paper(paper_id, args.project_root)
        if result:
            print(f"  Replication package: {result.relative_to(args.project_root)}")
        print()

    print("Done. Run in Stata:")
    for paper_id in args.papers:
        print(f"  cd \"{args.project_root.as_posix()}\"")
        print(f"  do \"news_process/papers/{paper_id}/replication/code/00_master.do\"")
        print()


if __name__ == '__main__':
    main()
