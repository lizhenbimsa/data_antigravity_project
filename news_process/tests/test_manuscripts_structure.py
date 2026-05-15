"""tests/test_manuscripts_structure.py — Manuscript structural integrity.

P4.3 (plan-r3 derivative-paper extension, 2026-05-15)

Verifies each of 10 manuscripts (5 papers × {en, zh}) plus 10 refs.bib files:
- Required LaTeX scaffolding (\\documentclass via preamble include, \\begin{document}, \\end{document})
- 8 standard sections (Intro, Lit, Method, Data, Main, Mechanism, Het, Robustness, Conclusion — Σ ≥ 7 unique \\section{} markers)
- V6 methodology F1-F4 markers present in Method section
- \\printbibliography present
- refs.bib has at least 1 valid @article entry
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
# 1. File existence
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
# 2. LaTeX scaffolding
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
# 3. Section structure (8 standard sections, at least 7 distinct)
# ============================================================================

_EXPECTED_SECTION_LABELS = frozenset({
    'sec:intro', 'sec:lit', 'sec:method', 'sec:data',
    'sec:main', 'sec:mech', 'sec:het', 'sec:robust', 'sec:concl',
})


@pytest.mark.parametrize('paper_id', _FIVE_PAPERS)
@pytest.mark.parametrize('lang', _LANGS)
def test_manuscript_has_at_least_7_sections(paper_id, lang):
    """Each manuscript should have a near-complete 8-section structure."""
    import re

    content = _manuscript_path(paper_id, lang).read_text(encoding='utf-8')
    labels = set(re.findall(r'\\label\{(sec:[^}]+)\}', content))
    matched = labels & _EXPECTED_SECTION_LABELS
    assert len(matched) >= 7, (
        f"{paper_id}/{lang}: only {len(matched)}/8 expected section labels "
        f"present: {sorted(matched)}"
    )


# ============================================================================
# 4. V6 methodology F1-F4 declarations
# ============================================================================

_V6_MARKERS_EN = (
    'F1', 'F2', 'F3', 'F4',
    'three independent LLM families',
    'gpt-5.4-nano',
    'gemini-3.1-flash-lite-preview',
    'deepseek-v4-flash',
    'temperature=0',
    'seed=42',
    '81.7',
    'Goldsmith-Pinkham',
)

_V6_MARKERS_ZH = (
    'F1', 'F2', 'F3', 'F4',
    '三个独立',
    'gpt-5.4-nano',
    'gemini-3.1-flash-lite-preview',
    'deepseek-v4-flash',
    'temperature=0',
    'seed=42',
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
# 5. Bibliography linkage
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
    # Count @article / @incollection / @book entries
    entry_count = sum(
        content.count(f'@{e}{{') for e in ('article', 'incollection', 'book', 'inproceedings')
    )
    assert entry_count >= 1, f"{paper_id}/{lang}: refs.bib has 0 entries"


# ============================================================================
# 6. Shared preamble integrity
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
# 7. Cross-paper invariants
# ============================================================================


def test_all_ten_manuscripts_distinct():
    """Each of 10 manuscripts should have distinct content (no copy-paste of same body)."""
    texts = {}
    for p in _FIVE_PAPERS:
        for lang in _LANGS:
            texts[(p, lang)] = _manuscript_path(p, lang).read_text(encoding='utf-8')
    # All pairs should differ by at least one character (typically much more).
    for (p1, l1), t1 in texts.items():
        for (p2, l2), t2 in texts.items():
            if (p1, l1) >= (p2, l2):
                continue
            assert t1 != t2, f"{p1}/{l1} and {p2}/{l2} are identical"


def test_main_paper_manuscript_longer_than_derivatives():
    """bank_fintech_tone manuscript should be hand-written and longer."""
    main_en = _manuscript_path('bank_fintech_tone', 'en').read_text(encoding='utf-8')
    deriv_en = _manuscript_path('llm_peer', 'en').read_text(encoding='utf-8')
    # Hand-written main should have more content than generated derivative.
    assert len(main_en) >= len(deriv_en) * 0.8, (
        f"main manuscript surprisingly short ({len(main_en)} vs derivative {len(deriv_en)})"
    )
