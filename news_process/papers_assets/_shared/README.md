# `papers_assets/_shared/` — Shared LaTeX preambles for paper drafts

> P4.1 (plan-r3 derivative-paper extension, 2026-05-15; 当前组合共 11 篇 = 5 主线 + 4 衍生 + 2 provisional，其中 8 篇 fully-coded paper 产出 .tex 草稿并消费本 preamble，bank_fintech_collab 用 Markdown 草稿、2 篇 provisional 暂无 LaTeX 草稿，均不引用本 preamble)

## Files

| File | Used by |
|---|---|
| `preamble_en.tex` | `papers_assets/<id>/drafts/en/manuscript.tex` |
| `preamble_zh.tex` | `papers_assets/<id>/drafts/zh/manuscript.tex` |

## Why a shared preamble

Eight papers × two languages = 16 manuscript drafts (the 8 of 9 portfolio papers that ship LaTeX; bank_fintech_collab uses Markdown drafts and does not consume this preamble). Each one shares ~30 lines
of package imports (booktabs, biblatex, hyperref, etc.). Centralizing in
`_shared/` keeps the diff focused on actual content when revising the
manuscript layer.

## Manuscript structure (per paper)

```
papers_assets/<paper_id>/drafts/
├── en/
│   ├── manuscript.tex   # \input{../../../_shared/preamble_en.tex} + paper body
│   ├── refs.bib         # Paper-specific BibLaTeX entries (partially populated; TODO: complete bibliography)
│   └── (output PDF after compile)
└── zh/
    ├── manuscript.tex
    ├── refs.bib
    └── ...
```

## Compile command

```bash
cd papers_assets/<paper_id>/drafts/en
xelatex manuscript.tex
biber manuscript
xelatex manuscript.tex
xelatex manuscript.tex
```

## V6 methodology injection

Section 3 (Method) of every paper includes the four V6 methodology declarations
(F1 LLM 3-family validation, F2 article-level coding, F3 NaN semantics, F4
Bartik IV pruning) per `papers_assets/V6_METHODOLOGY_CHANGES.md`. Authors
should adapt wording per paper but keep the four facts.
