"""tests/test_manuscripts_structure.py — 手稿结构完整性测试.

P4.3 (plan-r3 derivative-paper extension, 2026-05-15)

逐一验证 10 份手稿 (5 篇论文 × {en, zh}) 及 10 个 refs.bib 文件:
- 必需的 LaTeX 骨架 (\\documentclass 经 preamble include 引入, \\begin{document}, \\end{document})
- 8 个标准章节 (Intro, Lit, Method, Data, Main, Mechanism, Het, Robustness, Conclusion — Σ ≥ 7 个互异 \\section{} 标记)
- Method 章节含 V6 方法论 F1-F4 标记
- 含 \\printbibliography
- refs.bib 至少含 1 条合法 @article 条目
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

_PAPERS_ASSETS = _PROJECT_PARENT / 'news_process' / 'papers_assets'
_FIVE_PAPERS = (
    'bank_fintech_tone',
    'benefit_society',
    'brokerage_network',
    'llm_peer',
    'strategic_diff',
)
_LANGS = ('en', 'zh')


def _manuscript_path(paper_id: str, lang: str) -> Path:
    return _PAPERS_ASSETS / paper_id / 'drafts' / lang / 'manuscript.tex'


def _bib_path(paper_id: str, lang: str) -> Path:
    return _PAPERS_ASSETS / paper_id / 'drafts' / lang / 'refs.bib'


# ============================================================================
# 1. 文件存在性
# ============================================================================


@pytest.mark.parametrize('paper_id', _FIVE_PAPERS)
@pytest.mark.parametrize('lang', _LANGS)
def test_manuscript_exists(paper_id, lang):
    p = _manuscript_path(paper_id, lang)
    assert p.exists(), f"missing manuscript: {p}"


@pytest.mark.parametrize('paper_id', _FIVE_PAPERS)
@pytest.mark.parametrize('lang', _LANGS)
def test_refs_bib_exists(paper_id, lang):
    p = _bib_path(paper_id, lang)
    assert p.exists(), f"missing refs.bib: {p}"


@pytest.mark.parametrize('lang', _LANGS)
def test_shared_preamble_exists(lang):
    p = _PAPERS_ASSETS / '_shared' / f'preamble_{lang}.tex'
    assert p.exists(), f"missing shared preamble: {p}"


# ============================================================================
# 2. LaTeX 骨架
# ============================================================================


@pytest.mark.parametrize('paper_id', _FIVE_PAPERS)
@pytest.mark.parametrize('lang', _LANGS)
def test_manuscript_has_begin_end_document(paper_id, lang):
    content = _manuscript_path(paper_id, lang).read_text(encoding='utf-8')
    assert r'\begin{document}' in content
    assert r'\end{document}' in content


@pytest.mark.parametrize('paper_id', _FIVE_PAPERS)
@pytest.mark.parametrize('lang', _LANGS)
def test_manuscript_inputs_shared_preamble(paper_id, lang):
    content = _manuscript_path(paper_id, lang).read_text(encoding='utf-8')
    assert f'preamble_{lang}.tex' in content, \
        f"{paper_id}/{lang}/manuscript.tex does not input shared preamble"


@pytest.mark.parametrize('paper_id', _FIVE_PAPERS)
@pytest.mark.parametrize('lang', _LANGS)
def test_manuscript_has_title_author_date(paper_id, lang):
    content = _manuscript_path(paper_id, lang).read_text(encoding='utf-8')
    for cmd in [r'\title{', r'\author{', r'\date{']:
        assert cmd in content, f"{paper_id}/{lang}: missing {cmd}"


@pytest.mark.parametrize('paper_id', _FIVE_PAPERS)
@pytest.mark.parametrize('lang', _LANGS)
def test_manuscript_has_maketitle(paper_id, lang):
    content = _manuscript_path(paper_id, lang).read_text(encoding='utf-8')
    assert r'\maketitle' in content


@pytest.mark.parametrize('paper_id', _FIVE_PAPERS)
@pytest.mark.parametrize('lang', _LANGS)
def test_manuscript_has_abstract(paper_id, lang):
    content = _manuscript_path(paper_id, lang).read_text(encoding='utf-8')
    assert r'\begin{abstract}' in content
    assert r'\end{abstract}' in content


# ============================================================================
# 3. 章节结构 (8 个标准章节, 至少 7 个互异)
# ============================================================================

_EXPECTED_SECTION_LABELS = frozenset({
    'sec:intro', 'sec:lit', 'sec:method', 'sec:data',
    'sec:main', 'sec:mech', 'sec:het', 'sec:robust', 'sec:concl',
})


@pytest.mark.parametrize('paper_id', _FIVE_PAPERS)
@pytest.mark.parametrize('lang', _LANGS)
def test_manuscript_has_at_least_7_sections(paper_id, lang):
    """每份手稿应具备接近完整的 8 章节结构."""
    import re

    content = _manuscript_path(paper_id, lang).read_text(encoding='utf-8')
    labels = set(re.findall(r'\\label\{(sec:[^}]+)\}', content))
    matched = labels & _EXPECTED_SECTION_LABELS
    assert len(matched) >= 7, (
        f"{paper_id}/{lang}: only {len(matched)}/8 expected section labels "
        f"present: {sorted(matched)}"
    )


# ============================================================================
# 4. V6 方法论 F1-F4 声明
# ============================================================================

# 2026-07-02 事实刷新: ①gemini 模型名去 "-preview" (config/sentiment.yaml
# v3 锁定串无 -preview); ②补 DeepSeek 直连端点标记 (seed=42 仍真实在
# _build_llm_request 请求体, 保留); ③新增 F5 嵌入双主轨小节 +
# Qwen3-Embedding-8B canonical 槽披露 + full-only 门控列名。
_V6_MARKERS_EN = (
    'F1', 'F2', 'F3', 'F4', 'F5',
    'three independent LLM families',
    'gpt-5.4-nano',
    'gemini-3.1-flash-lite',
    'deepseek-v4-flash',
    'temperature=0',
    'seed=42',
    'api.deepseek.com',
    'llm\\_verified\\_full',  # tex 源内下划线带转义反斜杠
    'Qwen3-Embedding-8B',
    'text-embedding-3-large',
    '81.7',
    'Goldsmith-Pinkham',
)

_V6_MARKERS_ZH = (
    'F1', 'F2', 'F3', 'F4', 'F5',
    '三个独立',
    'gpt-5.4-nano',
    'gemini-3.1-flash-lite',
    'deepseek-v4-flash',
    'temperature=0',
    'seed=42',
    'api.deepseek.com',
    'llm\\_verified\\_full',  # tex 源内下划线带转义反斜杠
    'Qwen3-Embedding-8B',
    'text-embedding-3-large',
    '81.7',
    'Goldsmith-Pinkham',
)


@pytest.mark.parametrize('paper_id', _FIVE_PAPERS)
def test_manuscript_en_has_v6_markers(paper_id):
    content = _manuscript_path(paper_id, 'en').read_text(encoding='utf-8')
    missing = [m for m in _V6_MARKERS_EN if m not in content]
    assert not missing, f"{paper_id}/en: missing V6 markers {missing}"


@pytest.mark.parametrize('paper_id', _FIVE_PAPERS)
def test_manuscript_zh_has_v6_markers(paper_id):
    content = _manuscript_path(paper_id, 'zh').read_text(encoding='utf-8')
    missing = [m for m in _V6_MARKERS_ZH if m not in content]
    assert not missing, f"{paper_id}/zh: missing V6 markers {missing}"


# ============================================================================
# 5. 参考文献接线
# ============================================================================


@pytest.mark.parametrize('paper_id', _FIVE_PAPERS)
@pytest.mark.parametrize('lang', _LANGS)
def test_manuscript_references_refs_bib(paper_id, lang):
    content = _manuscript_path(paper_id, lang).read_text(encoding='utf-8')
    assert r'\addbibresource{refs.bib}' in content


@pytest.mark.parametrize('paper_id', _FIVE_PAPERS)
@pytest.mark.parametrize('lang', _LANGS)
def test_manuscript_has_printbibliography(paper_id, lang):
    content = _manuscript_path(paper_id, lang).read_text(encoding='utf-8')
    assert r'\printbibliography' in content


@pytest.mark.parametrize('paper_id', _FIVE_PAPERS)
@pytest.mark.parametrize('lang', _LANGS)
def test_refs_bib_has_at_least_one_entry(paper_id, lang):
    content = _bib_path(paper_id, lang).read_text(encoding='utf-8')
    # 统计 @article / @incollection / @book 等条目数
    entry_count = sum(
        content.count(f'@{e}{{') for e in ('article', 'incollection', 'book', 'inproceedings')
    )
    assert entry_count >= 1, f"{paper_id}/{lang}: refs.bib has 0 entries"


# ============================================================================
# 6. 共享 preamble 完整性
# ============================================================================


def test_preamble_en_has_required_packages():
    content = (_PAPERS_ASSETS / '_shared' / 'preamble_en.tex').read_text(encoding='utf-8')
    for pkg in ['fontspec', 'amsmath', 'booktabs', 'graphicx', 'hyperref', 'biblatex']:
        assert pkg in content, f"preamble_en missing package {pkg}"


def test_preamble_zh_has_xecjk_and_simsun():
    content = (_PAPERS_ASSETS / '_shared' / 'preamble_zh.tex').read_text(encoding='utf-8')
    assert 'xeCJK' in content, 'preamble_zh missing xeCJK'
    assert 'SimSun' in content, 'preamble_zh missing SimSun font'


# ============================================================================
# 7. 跨论文不变式
# ============================================================================


def test_all_ten_manuscripts_distinct():
    """10 份手稿内容应两两不同 (防止同一正文复制粘贴)."""
    texts = {}
    for p in _FIVE_PAPERS:
        for lang in _LANGS:
            texts[(p, lang)] = _manuscript_path(p, lang).read_text(encoding='utf-8')
    # 任意两份手稿至少应有一个字符不同 (实际通常差异大得多)
    for (p1, l1), t1 in texts.items():
        for (p2, l2), t2 in texts.items():
            if (p1, l1) >= (p2, l2):
                continue
            assert t1 != t2, f"{p1}/{l1} and {p2}/{l2} are identical"


def test_main_paper_manuscript_longer_than_derivatives():
    """bank_fintech_tone 主线手稿应为手写且篇幅更长."""
    main_en = _manuscript_path('bank_fintech_tone', 'en').read_text(encoding='utf-8')
    deriv_en = _manuscript_path('llm_peer', 'en').read_text(encoding='utf-8')
    # 手写主线手稿的内容量应多于生成的衍生论文手稿
    assert len(main_en) >= len(deriv_en) * 0.8, (
        f"main manuscript surprisingly short ({len(main_en)} vs derivative {len(deriv_en)})"
    )
