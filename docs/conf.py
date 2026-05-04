"""Sphinx configuration for news_process v2.0.0 documentation site.

Phase D — Documentation Production (2026-05-04).

Architectural choices
---------------------
* **Theme**: Furo (Pradyun Gedam) — modern, mobile-friendly, dark-mode by
  default, used by pip's official docs.
* **Markdown**: ``myst-parser`` lets us write prose in Markdown.  All
  ``.md`` files in this directory tree are first-class doc sources.
* **API auto-extraction**: ``autodoc`` + ``autosummary`` recursively
  enumerate every public symbol in ``news_process.{core,pipeline,
  validation,papers}`` with **zero manual maintenance**.
* **Docstring style**: Napoleon supports both NumPy and Google styles
  simultaneously, matching the v2.0 codebase's mixed conventions.
* **Type hints**: rendered into prose via ``sphinx_autodoc_typehints``.
* **Mocked imports**: heavy ML deps (torch, transformers,
  sentence_transformers) are stubbed during build to keep ``make html``
  under 5 minutes and avoid GPU detection side-effects.

Build commands
--------------
    cd docs
    make html       # build to docs/_build/html/
    make clean      # remove _build/
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — make ``news_process.*`` importable for autodoc
# ---------------------------------------------------------------------------

# docs/conf.py → repo root (parent of docs/)
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

# Inject placeholder env vars so that ``load_config()`` doesn't crash on
# missing ``.env`` keys during autodoc import. These never reach runtime.
os.environ.setdefault("GPT5NANO_API_KEY", "docs-build-placeholder")
os.environ.setdefault("GEMINI3_API_KEY", "docs-build-placeholder")
os.environ.setdefault("CLAUDE4H_API_KEY", "docs-build-placeholder")
os.environ.setdefault("EMBEDDING_API_KEY", "docs-build-placeholder")

# ---------------------------------------------------------------------------
# Project metadata
# ---------------------------------------------------------------------------

project = "news_process"
author = "data_antigravity_project / news_process team"
copyright = "2026, news_process v2.0.0"  # noqa: A001 — Sphinx convention

# Pull version dynamically from the package
try:
    import news_process  # noqa: E402

    release = news_process.__version__
except Exception:  # pragma: no cover — fallback when package import fails
    release = "2.0.0"
version = release

# ---------------------------------------------------------------------------
# General Sphinx configuration
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

# Source files: prefer Markdown, but accept legacy RST if any.
source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

master_doc = "index"
language = "zh_CN"

# UI niceties
html_show_sourcelink = False
html_show_sphinx = True
todo_include_todos = True

# Patterns to ignore during the build
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
    "undoc-members": False,  # keep noise low; prefer documented APIs
    "show-inheritance": True,
    "member-order": "bysource",
}

# Heavy / GPU-bound ML dependencies are mocked during build.
# Their docstrings will still appear via napoleon if we trigger autodoc on
# wrappers, but the heavy module bodies are not imported.
autodoc_mock_imports = [
    "torch",
    "transformers",
    "sentence_transformers",
    "ahocorasick",
    "datasketch",
    "tqdm",
    "openpyxl",
    "matplotlib",
]

# NOTE on autosummary stubs:
#   We disable stub generation because myst-parser's toctree directive does not
#   recognise the stub paths via :glob:, leaving them orphaned. The autosummary
#   tables in api/*.md already render the public-API matrix with auto-extracted
#   module descriptions — sufficient for v2.0 docs scope. Detail-per-symbol
#   pages can be re-enabled in a future docs release if needed.
autosummary_generate = False
autosummary_imported_members = False

# ---------------------------------------------------------------------------
# Napoleon (docstring styles)
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
# myst-parser (Markdown extensions)
# ---------------------------------------------------------------------------

myst_enable_extensions = [
    "deflist",          # definition lists
    "colon_fence",      # ::: admonitions
    "tasklist",         # GitHub-style task lists
    "substitution",     # variable substitution
    "linkify",          # auto-link bare URLs
    "smartquotes",
    "fieldlist",
]
myst_heading_anchors = 4  # generate slugs for h1..h4
myst_substitutions = {
    "version": release,
    "min_python": "3.10",
}

# ---------------------------------------------------------------------------
# Type hints rendering
# ---------------------------------------------------------------------------

always_document_param_types = True
typehints_fully_qualified = False
typehints_document_rtype = True
typehints_use_rtype = True

# ---------------------------------------------------------------------------
# intersphinx — link to upstream docs
# ---------------------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
    "sklearn": ("https://scikit-learn.org/stable/", None),
}

# ---------------------------------------------------------------------------
# HTML output (Furo theme)
# ---------------------------------------------------------------------------

html_theme = "furo"
html_static_path = ["_static"]
html_title = f"{project} v{release}"

html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_buttons": [],  # no public source repo configured
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

# Chinese full-text search support (Sphinx 4.x+ has built-in jieba split).
html_search_language = "zh"

# Copy-button: skip the prompt (>>>) and indent so users get just the code.
copybutton_prompt_text = r">>> |\.\.\. |\$ |# "
copybutton_prompt_is_regexp = True

# Mermaid: use the modern theme for cross-platform rendering.
mermaid_d3_zoom = True
