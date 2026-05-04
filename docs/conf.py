"""news_process v2.0.0 文档站 Sphinx 配置文件。

Phase D — 文档生产化 (2026-05-04)。

架构选型
---------
* **Theme**: Furo (Pradyun Gedam 出品) — 现代化、移动端友好、默认夜间
  模式; pip 官方文档同款。
* **Markdown 源**: ``myst-parser`` 使本目录树下所有 ``.md`` 文件都可以
  作为一等文档源, 让中文 prose 写起来比 reStructuredText 顺手。
* **API 自动抽取**: ``autodoc`` + ``autosummary`` 递归枚举
  ``news_process.{core,pipeline,validation,papers}`` 的全部公开符号,
  **零人工维护**。
* **Docstring 风格**: Napoleon 同时支持 NumPy 与 Google 风格, 匹配
  v2.0 代码库混合约定的实际情况。
* **类型注解**: ``sphinx_autodoc_typehints`` 自动把 type hints 渲染进
  prose。
* **被 mock 的 import**: 重型 ML 依赖 (torch, transformers,
  sentence_transformers) 在构建期被 stub 化, 使 ``make html`` 控制
  在 5 分钟内并避开 GPU 探测副作用。

构建命令
---------
    cd docs
    make html       # 增量构建到 docs/_build/html/
    make clean      # 清空 _build/
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 路径配置 — 让 autodoc 能够 ``import news_process.*``
# ---------------------------------------------------------------------------

# docs/conf.py → repo root (docs/ 的父目录)
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

# 注入占位 env 变量, 使 autodoc import 期间 ``load_config()`` 不会因 .env
# 缺失而崩溃。这些占位值不会进入运行时 (生产配置使用真实 .env)。
os.environ.setdefault("GPT5NANO_API_KEY", "docs-build-placeholder")
os.environ.setdefault("GEMINI3_API_KEY", "docs-build-placeholder")
os.environ.setdefault("CLAUDE4H_API_KEY", "docs-build-placeholder")
os.environ.setdefault("EMBEDDING_API_KEY", "docs-build-placeholder")

# ---------------------------------------------------------------------------
# 项目元数据
# ---------------------------------------------------------------------------

project = "news_process"
author = "data_antigravity_project / news_process team"
copyright = "2026, news_process v2.0.0"  # noqa: A001 — Sphinx 约定字段名

# 动态从包 ``__version__`` 拉取版本号
try:
    import news_process  # noqa: E402

    release = news_process.__version__
except Exception:  # pragma: no cover — 包 import 失败时的兜底
    release = "2.0.0"
version = release

# ---------------------------------------------------------------------------
# Sphinx 通用配置
# ---------------------------------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "myst_parser",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "sphinxcontrib.mermaid",
]

# 文档源文件: 优先 Markdown, 兼顾历史 RST。
source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

master_doc = "index"
language = "zh_CN"

# UI 细节
html_show_sourcelink = False
html_show_sphinx = True
todo_include_todos = True

# 构建期排除模式
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "api/_autosummary",
    "api/generated",
]

# ---------------------------------------------------------------------------
# autodoc / autosummary
# ---------------------------------------------------------------------------

autodoc_default_options = {
    "members": True,
    "undoc-members": False,  # 降噪: 优先收录已 documented 的 API
    "show-inheritance": True,
    "member-order": "bysource",
}

# 重型 / GPU 相关的 ML 依赖在构建期被 mock。
# 它们的 docstring 仍可通过 napoleon 在 wrapper 上正常渲染, 但重型模块
# 本体不会被实际 import。
# 下列包在「仅 requirements-docs.txt」环境中通常不存在; 对其 mock 可让
# autosummary 在 import 各 stage 模块时不因依赖缺失而失败。
autodoc_mock_imports = [
    "torch",
    "transformers",
    "sentence_transformers",
    "ahocorasick",
    "datasketch",
    "tqdm",
    "openpyxl",
    "matplotlib",
    "pandas",
    "numpy",
    "psutil",
    "aiohttp",
    "scipy",
    "sklearn",
    "pyarrow",
    "joblib",
    "jieba",
]

# 关于 autosummary stub:
#   禁用 stub 生成的原因: myst-parser 的 toctree directive 通过 :glob:
#   无法识别 autosummary 生成的 stub 路径, 会导致这些 stub 文件变成
#   孤儿。api/*.md 中的 autosummary 表格已经能渲染出 "公开 API 矩阵 +
#   自动抽取的模块描述", 对 v2.0 的文档范围足够。后续若需要单符号详情
#   页可在未来的 docs release 重新启用。
autosummary_generate = False
autosummary_imported_members = False

# ---------------------------------------------------------------------------
# Napoleon (docstring 风格)
# ---------------------------------------------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True

# ---------------------------------------------------------------------------
# myst-parser (Markdown 扩展能力)
# ---------------------------------------------------------------------------

myst_enable_extensions = [
    "deflist",          # 定义列表
    "colon_fence",      # ::: 围栏式 admonition
    "tasklist",         # GitHub 风格任务清单
    "substitution",     # 变量替换
    "linkify",          # 裸 URL 自动链接
    "smartquotes",
    "fieldlist",
]
myst_heading_anchors = 4  # 为 h1..h4 生成锚点 slug
myst_substitutions = {
    "version": release,
    "min_python": "3.10",
}

# ---------------------------------------------------------------------------
# 类型提示 (type hints) 渲染
# ---------------------------------------------------------------------------

always_document_param_types = True
typehints_fully_qualified = False
typehints_document_rtype = True
typehints_use_rtype = True

# ---------------------------------------------------------------------------
# intersphinx — 指向上游文档的交叉引用映射
# ---------------------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
    "sklearn": ("https://scikit-learn.org/stable/", None),
}

# ---------------------------------------------------------------------------
# HTML 输出 (Furo 主题)
# ---------------------------------------------------------------------------

html_theme = "furo"
html_static_path = ["_static"]
html_title = f"{project} v{release}"

html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_buttons": [],  # 未配置公开源码仓库, 故隐藏顶部按钮
    "footer_icons": [],
    "light_css_variables": {
        "color-brand-primary": "#0066CC",
        "color-brand-content": "#0066CC",
    },
    "dark_css_variables": {
        "color-brand-primary": "#3B9DFF",
        "color-brand-content": "#3B9DFF",
    },
}

# 中文全文检索 (Sphinx 4.x+ 内置 jieba 分词支持)。
html_search_language = "zh"

# copybutton: 剥离提示符 (>>>) 与缩进, 仅复制纯代码正文。
copybutton_prompt_text = r">>> |\.\.\. |\$ |# "
copybutton_prompt_is_regexp = True

# Mermaid: 启用现代主题以获得跨平台一致渲染。
mermaid_d3_zoom = True
