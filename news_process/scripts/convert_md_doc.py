"""把任意 markdown 文档渲染为带样式的 HTML 和 PDF（通用 CLI）。

输入：一个或多个 `<path-to-md>`
输出：同目录的 `<name>.html` 与 `<name>.pdf`

样式：与 `convert_catalog_to_html.py` 同源（学术文档 CSS + MathJax v3 +
Pygments 代码高亮 + TOC 锚点 + 警示 blockquote 高亮）。

PDF 通过 Microsoft Edge headless 渲染（与 `convert_catalog_to_pdf.py` 同
策略：临时 user-data-dir + 轮询 PDF 大小稳定后主动 terminate，规避 Edge
被 Windows 后台 sync 任务挂住不退的问题）。

用法（仓库根目录）：
    F:/Anaconda3/python.exe news_process/scripts/convert_md_doc.py \\
        news_process/docs/项目说明_顶刊版.md \\
        news_process/docs/项目说明书_简明版.md
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

import markdown

# Windows PowerShell 默认 cp936，避免中文进度输出乱码
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# === Edge headless 配置 ===
EDGE_CANDIDATES = [
    Path(r"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
    Path(r"C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
]
VIRTUAL_TIME_BUDGET_MS = 20000
RENDER_TIMEOUT_S = 90
POLL_INTERVAL_S = 1.0
STABLE_TICKS = 2


CSS = r"""
:root {
  --fg: #1a1a1a;
  --bg: #ffffff;
  --muted: #6a737d;
  --link: #0366d6;
  --link-hover: #0246a8;
  --code-bg: #f6f8fa;
  --code-border: #e1e4e8;
  --quote-border: #dfe2e5;
  --table-border: #d0d7de;
  --table-stripe: #f6f8fa;
  --accent: #0a4595;
  --warn-bg: #fff4e5;
  --warn-border: #f5b66a;
}

* { box-sizing: border-box; }

html { scroll-behavior: smooth; }

body {
  max-width: 1080px;
  margin: 0 auto;
  padding: 32px 28px 80px;
  color: var(--fg);
  background: var(--bg);
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei",
               "Segoe UI", "Helvetica Neue", Arial, "Source Han Serif SC",
               "Noto Serif CJK SC", "Source Han Sans SC", sans-serif;
  font-size: 15.5px;
  line-height: 1.75;
  word-wrap: break-word;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
}

h1, h2, h3, h4, h5, h6 {
  font-weight: 600;
  line-height: 1.35;
  margin-top: 1.8em;
  margin-bottom: 0.6em;
  color: var(--accent);
}
h1 { font-size: 2.2em; border-bottom: 2px solid var(--accent); padding-bottom: 0.3em; }
h2 { font-size: 1.6em; border-bottom: 1px solid var(--table-border); padding-bottom: 0.2em; }
h3 { font-size: 1.3em; }
h4 { font-size: 1.1em; }
h5, h6 { font-size: 1em; }

p { margin: 0.7em 0; }

a { color: var(--link); text-decoration: none; }
a:hover { color: var(--link-hover); text-decoration: underline; }

code, kbd, samp, pre {
  font-family: "JetBrains Mono", "Fira Code", Consolas, "Cascadia Code",
               "Source Code Pro", Menlo, Monaco, "Courier New", monospace;
  font-size: 0.92em;
}
code {
  background: var(--code-bg);
  border: 1px solid var(--code-border);
  border-radius: 4px;
  padding: 0.12em 0.4em;
}
pre {
  background: var(--code-bg);
  border: 1px solid var(--code-border);
  border-radius: 6px;
  padding: 14px 16px;
  overflow-x: auto;
  line-height: 1.55;
  white-space: pre;
  tab-size: 4;
}
pre > code {
  background: transparent;
  border: none;
  padding: 0;
}

table {
  display: block;
  width: max-content;
  max-width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
  overflow-x: auto;
}
table th, table td {
  border: 1px solid var(--table-border);
  padding: 8px 12px;
  vertical-align: top;
  text-align: left;
}
table th {
  background: var(--code-bg);
  font-weight: 600;
}
table tbody tr:nth-child(2n) {
  background: var(--table-stripe);
}

blockquote {
  margin: 1em 0;
  padding: 0.4em 1em;
  color: var(--muted);
  border-left: 4px solid var(--quote-border);
  background: #fafbfc;
}
blockquote p { margin: 0.4em 0; }
blockquote strong { color: var(--accent); }

blockquote.warn {
  background: var(--warn-bg);
  border-left-color: var(--warn-border);
  color: #5a3a00;
}

ul, ol { padding-left: 1.6em; }
li { margin: 0.25em 0; }

hr {
  border: none;
  border-top: 1px solid var(--table-border);
  margin: 2.4em 0;
}

.toc {
  background: #fafbfc;
  border: 1px solid var(--table-border);
  border-radius: 8px;
  padding: 12px 18px;
  margin: 1em 0;
  font-size: 0.95em;
}
.toc > ul {
  margin: 0;
  padding-left: 1.4em;
}

.headerlink {
  margin-left: 0.4em;
  color: var(--muted);
  font-size: 0.85em;
  text-decoration: none;
  visibility: hidden;
}
h1:hover .headerlink, h2:hover .headerlink, h3:hover .headerlink,
h4:hover .headerlink, h5:hover .headerlink, h6:hover .headerlink {
  visibility: visible;
}

.back-to-top {
  position: fixed;
  right: 24px;
  bottom: 24px;
  background: var(--accent);
  color: #fff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  box-shadow: 0 2px 8px rgba(0,0,0,0.18);
  font-size: 18px;
  opacity: 0.85;
  z-index: 100;
}
.back-to-top:hover { color: #fff; opacity: 1; }

/* Pygments 代码高亮 (github-like 子集) */
.highlight .hll { background-color: #ffffcc }
.highlight  { background: var(--code-bg); }
.highlight .c  { color: #6a737d; font-style: italic }
.highlight .k  { color: #d73a49; }
.highlight .o  { color: #d73a49; }
.highlight .ch { color: #6a737d; font-style: italic }
.highlight .cm { color: #6a737d; font-style: italic }
.highlight .cp { color: #d73a49 }
.highlight .cpf{ color: #6a737d; font-style: italic }
.highlight .c1 { color: #6a737d; font-style: italic }
.highlight .cs { color: #6a737d; font-style: italic }
.highlight .gd { color: #b31d28; background: #ffeef0 }
.highlight .ge { font-style: italic }
.highlight .gr { color: #b31d28 }
.highlight .gh { color: #005cc5; font-weight: bold }
.highlight .gi { color: #22863a; background: #f0fff4 }
.highlight .go { color: #6a737d }
.highlight .gp { color: #6a737d }
.highlight .gs { font-weight: bold }
.highlight .gu { color: #6f42c1; font-weight: bold }
.highlight .gt { color: #b31d28 }
.highlight .kc { color: #005cc5 }
.highlight .kd { color: #d73a49 }
.highlight .kn { color: #d73a49 }
.highlight .kp { color: #d73a49 }
.highlight .kr { color: #d73a49 }
.highlight .kt { color: #d73a49 }
.highlight .m  { color: #005cc5 }
.highlight .s  { color: #032f62 }
.highlight .na { color: #6f42c1 }
.highlight .nb { color: #005cc5 }
.highlight .nc { color: #6f42c1; font-weight: bold }
.highlight .no { color: #005cc5 }
.highlight .nd { color: #6f42c1 }
.highlight .ni { color: #6f42c1 }
.highlight .ne { color: #6f42c1; font-weight: bold }
.highlight .nf { color: #6f42c1; font-weight: bold }
.highlight .nl { color: #735c0f }
.highlight .nn { color: #24292e }
.highlight .nt { color: #22863a }
.highlight .nv { color: #e36209 }
.highlight .ow { color: #d73a49; font-weight: bold }
.highlight .w  { color: #bbbbbb }
.highlight .mf { color: #005cc5 }
.highlight .mh { color: #005cc5 }
.highlight .mi { color: #005cc5 }
.highlight .mo { color: #005cc5 }
.highlight .sa { color: #032f62 }
.highlight .sb { color: #032f62 }
.highlight .sc { color: #032f62 }
.highlight .dl { color: #032f62 }
.highlight .sd { color: #032f62 }
.highlight .s2 { color: #032f62 }
.highlight .se { color: #032f62 }
.highlight .sh { color: #032f62 }
.highlight .si { color: #005cc5 }
.highlight .sx { color: #032f62 }
.highlight .sr { color: #032f62 }
.highlight .s1 { color: #032f62 }
.highlight .ss { color: #005cc5 }
.highlight .bp { color: #005cc5 }
.highlight .vc { color: #e36209 }
.highlight .vg { color: #e36209 }
.highlight .vi { color: #e36209 }
.highlight .il { color: #005cc5 }

@media (max-width: 720px) {
  body { padding: 16px 12px 60px; font-size: 15px; }
  h1 { font-size: 1.8em; }
  h2 { font-size: 1.4em; }
  pre { font-size: 0.85em; }
}

@media print {
  .back-to-top { display: none; }
  body { font-size: 11pt; max-width: none; padding: 0; }
  pre, table { page-break-inside: avoid; }
  h1, h2, h3 { page-break-after: avoid; }
}
"""


MATHJAX_CONFIG = r"""
<script>
  window.MathJax = {
    tex: {
      inlineMath: [['$', '$'], ['\\(', '\\)']],
      displayMath: [['$$', '$$'], ['\\[', '\\]']],
      processEscapes: true,
      packages: {'[+]': ['ams']}
    },
    options: {
      skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'],
      ignoreHtmlClass: 'tex2jax_ignore',
      processHtmlClass: 'tex2jax_process'
    },
    svg: { fontCache: 'global' }
  };
</script>
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async
        src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
</script>
"""


def extract_title(md_text: str, fallback: str) -> str:
    """从 markdown 提取第一个 `#` H1 作为 <title>；失败用 fallback。"""
    for line in md_text.splitlines():
        m = re.match(r"^#\s+(.+?)\s*$", line)
        if m:
            # 去掉标题中的 markdown 粗体 / 斜体标记
            return re.sub(r"[*_`]", "", m.group(1)).strip()
    return fallback


def post_process_html(html: str) -> str:
    """把含警示关键词的 blockquote 加上 .warn class。"""
    def warn_blockquote(match: re.Match) -> str:
        inner = match.group(1)
        if re.search(
            r"(决策记录|⚠|陷阱|BREAKING|fail-loud|警告|critical|重要)",
            inner,
        ):
            return f'<blockquote class="warn">{inner}</blockquote>'
        return match.group(0)

    return re.sub(
        r"<blockquote>(.*?)</blockquote>",
        warn_blockquote,
        html,
        flags=re.DOTALL,
    )


def build_html(md_text: str, title: str) -> str:
    md = markdown.Markdown(
        extensions=[
            "extra",
            "sane_lists",
            "toc",
            "codehilite",
            "admonition",
        ],
        extension_configs={
            "codehilite": {
                "css_class": "highlight",
                "guess_lang": False,
            },
            "toc": {
                "permalink": "¶",
                "permalink_class": "headerlink",
                "permalink_title": "Permalink to this section",
                "toc_depth": "2-3",
                "anchorlink": False,
            },
        },
        output_format="html5",
    )

    body_html = post_process_html(md.convert(md_text))

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="generator" content="Python markdown + MathJax v3">
<style>{CSS}</style>
{MATHJAX_CONFIG}
</head>
<body>
{body_html}
<a href="#" class="back-to-top" title="返回顶部">↑</a>
</body>
</html>
"""


def render_html(md_path: Path, html_path: Path) -> None:
    md_text = md_path.read_text(encoding="utf-8")
    title = extract_title(md_text, fallback=md_path.stem)
    html_path.write_text(build_html(md_text, title), encoding="utf-8")
    kb = html_path.stat().st_size / 1024
    print(f"  [HTML] {html_path.name}  ({kb:.1f} KB)")


def find_edge() -> Path:
    for p in EDGE_CANDIDATES:
        if p.exists():
            return p
    raise SystemExit(
        f"未找到 msedge.exe；候选：{[str(p) for p in EDGE_CANDIDATES]}"
    )


def render_pdf(html_path: Path, pdf_path: Path, edge: Path) -> None:
    # Edge `--print-to-pdf=<path>` 必须收到绝对路径，否则它会在自己的工作
    # 目录下解析，导致 PDF 写不到我们期望的位置（且没有任何错误提示）。
    pdf_path = pdf_path.resolve()
    if pdf_path.exists():
        pdf_path.unlink()

    file_url = html_path.resolve().as_uri()

    # 实测：`--user-data-dir=<临时目录>` 与中文 `--print-to-pdf=<路径>` 在
    # Edge headless 上有兼容问题，会让 Edge 正常退出但根本没写 PDF。
    # 因此这里走最朴素的命令，把 Edge 不肯退出的兜底交给 Popen 轮询逻辑。
    cmd = [
        str(edge),
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--virtual-time-budget={VIRTUAL_TIME_BUDGET_MS}",
        "--run-all-compositor-stages-before-draw",
        "--no-first-run",
        "--no-default-browser-check",
        f"--print-to-pdf={pdf_path}",
        file_url,
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    try:
        _wait_for_pdf(pdf_path)
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    mb = pdf_path.stat().st_size / (1024 * 1024)
    print(f"  [PDF]  {pdf_path.name}  ({mb:.2f} MB)")


def _wait_for_pdf(pdf_path: Path) -> None:
    """只盯 PDF 文件大小稳定 — 不在 Edge 主进程 returncode 一变就退出。

    实测 Edge headless 的 print 子进程会**晚于**主进程 returncode 标记几秒
    才把 PDF 刷到磁盘，过早判定会误报失败。改成 RENDER_TIMEOUT_S 总闸 +
    STABLE_TICKS 检测，对 Edge 退出与否完全不依赖。
    """
    deadline = time.monotonic() + RENDER_TIMEOUT_S
    last_size = -1
    stable = 0
    while time.monotonic() < deadline:
        if pdf_path.exists():
            size = pdf_path.stat().st_size
            if size > 0 and size == last_size:
                stable += 1
                if stable >= STABLE_TICKS:
                    return
            else:
                stable = 0
                last_size = size
        time.sleep(POLL_INTERVAL_S)

    raise SystemExit(
        f"等待 PDF 渲染超时（{RENDER_TIMEOUT_S}s）；最后大小 {last_size}"
    )


def convert_one(md_path: Path, edge: Path) -> None:
    if not md_path.exists():
        raise SystemExit(f"源文件不存在：{md_path}")
    if md_path.suffix.lower() != ".md":
        raise SystemExit(f"非 markdown 文件：{md_path}")

    html_path = md_path.with_suffix(".html")
    pdf_path = md_path.with_suffix(".pdf")

    render_html(md_path, html_path)
    render_pdf(html_path, pdf_path, edge)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="把 markdown 文档批量转成同目录 HTML + PDF。",
    )
    parser.add_argument(
        "markdown",
        nargs="+",
        type=Path,
        help="待转换的 .md 文件路径（可传多个）",
    )
    args = parser.parse_args()

    edge = find_edge()
    for md in args.markdown:
        print(f"\n>>> {md}")
        convert_one(md, edge)
    print("\n全部完成。")


if __name__ == "__main__":
    main()
