"""把 PROJECT_DESCRIPTION.md 转换为带样式与 MathJax 的 HTML。

⚠ 暂不可用: docs/ 目录已整体删除 (commit 1698bda5), 源文件 PROJECT_DESCRIPTION.md 不存在,
main() 会在 SRC.exists() 检查处 SystemExit。待 PROJECT_DESCRIPTION.md 重建后方可启用。

输入：news_process/docs/PROJECT_DESCRIPTION.md
输出：news_process/docs/PROJECT_DESCRIPTION.html

特性：
- markdown 表格 / fenced code / TOC / attr_list / sane_lists 扩展
- Pygments 代码语法高亮（默认主题）
- LaTeX 数学公式（$$...$$ 与 $...$）通过 MathJax v3 CDN 渲染
- ASCII art 在 ```pre``` 与 ` ```` 围栏内保留等宽字体
- 学术文档风格 CSS（serif 正文 / 灰底代码 / 边框表格 / 折叠目录）
- 自动生成目录（TOC）与锚点
"""
from __future__ import annotations

import re
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / "docs" / "PROJECT_DESCRIPTION.md"
DST = ROOT / "docs" / "PROJECT_DESCRIPTION.html"


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
  max-width: 980px;
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

/* 代码：行内 与 围栏 */
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

/* 表格 */
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

/* 引用块 */
blockquote {
  margin: 1em 0;
  padding: 0.4em 1em;
  color: var(--muted);
  border-left: 4px solid var(--quote-border);
  background: #fafbfc;
}
blockquote p { margin: 0.4em 0; }
blockquote strong { color: var(--accent); }

/* 警示与决策记录块（含 ⚠ / 决策记录 关键词的 blockquote 高亮） */
blockquote.warn {
  background: var(--warn-bg);
  border-left-color: var(--warn-border);
  color: #5a3a00;
}

/* 列表 */
ul, ol { padding-left: 1.6em; }
li { margin: 0.25em 0; }

/* 分隔线 */
hr {
  border: none;
  border-top: 1px solid var(--table-border);
  margin: 2.4em 0;
}

/* 文档元信息 */
.doc-header {
  background: linear-gradient(180deg, #f7faff 0%, #ffffff 100%);
  border: 1px solid var(--table-border);
  border-radius: 8px;
  padding: 16px 22px;
  margin-bottom: 28px;
  font-size: 0.95em;
}
.doc-header .meta {
  color: var(--muted);
  margin-top: 6px;
}

/* TOC 悬浮（如需可扩展） */
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

/* 标题锚点 */
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

/* 顶部返回 */
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

/* Pygments 代码高亮（github-like 子集） */
.highlight .hll { background-color: #ffffcc }
.highlight  { background: var(--code-bg); }
.highlight .c  { color: #6a737d; font-style: italic } /* Comment */
.highlight .k  { color: #d73a49; } /* Keyword */
.highlight .o  { color: #d73a49; } /* Operator */
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

/* 移动端优化 */
@media (max-width: 720px) {
  body { padding: 16px 12px 60px; font-size: 15px; }
  h1 { font-size: 1.8em; }
  h2 { font-size: 1.4em; }
  pre { font-size: 0.85em; }
}

/* 打印优化 */
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


def post_process_html(html: str) -> str:
    """对 markdown 转换后的 HTML 做后处理：
    - 在含"决策记录" / "⚠" / "决策" 关键词的 blockquote 上加 .warn class，
      让它高亮显示。
    - 标题加 anchor 链接（id 由 toc 扩展生成）。
    """
    # blockquote 高亮：含 "决策记录" / "⚠" 关键词的加 .warn class
    def warn_blockquote(match: re.Match) -> str:
        inner = match.group(1)
        if re.search(r"(决策记录|⚠|配套版本治理|存储治理|披露口径|致谢)", inner):
            return f'<blockquote class="warn">{inner}</blockquote>'
        return match.group(0)

    html = re.sub(r"<blockquote>(.*?)</blockquote>", warn_blockquote,
                  html, flags=re.DOTALL)

    return html


def build_html(md_text: str) -> str:
    md = markdown.Markdown(
        extensions=[
            "extra",          # tables / fenced_code / attr_list / abbr / footnotes
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

    body_html = md.convert(md_text)
    body_html = post_process_html(body_html)

    # 顶部文档头（meta info）
    # 版本/commit 不再硬编码 (旧值 v3.6.0/1cd99574 早已过期且易失真);
    # 以源 MD 顶部声明为准, 此处仅标注来源与生成方式。
    header_html = (
        '<div class="doc-header">\n'
        '  <strong>news_process 项目说明书</strong>\n'
        '  <div class="meta">'
        'Markdown 源文件：<code>PROJECT_DESCRIPTION.md</code> · '
        '本 HTML 由 <code>scripts/convert_project_description_to_html.py</code> 自动生成'
        '</div>\n'
        '</div>\n'
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>news_process 项目说明书</title>
<meta name="description"
      content="基于中文财经新闻的银行-金融科技互动效应面板数据流水线">
<meta name="generator" content="Python markdown 3.8 + MathJax v3">
<style>{CSS}</style>
{MATHJAX_CONFIG}
</head>
<body>
{header_html}
{body_html}
<a href="#" class="back-to-top" title="返回顶部">↑</a>
</body>
</html>
"""


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"源文件不存在：{SRC}")

    md_text = SRC.read_text(encoding="utf-8")
    html = build_html(md_text)
    DST.write_text(html, encoding="utf-8")

    size_kb = DST.stat().st_size / 1024
    print(f"OK: 写出 {DST}  ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
