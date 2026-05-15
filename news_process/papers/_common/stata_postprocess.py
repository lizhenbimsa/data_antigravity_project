"""news_process.papers._common.stata_postprocess — Stata esttab CSV → pandas.

P2.1 (plan-r3 derivative-paper extension, 2026-05-15)

Bridges Stata's ``esttab`` regression output (LaTeX/CSV) back into a pandas
DataFrame that can be:
  - Re-formatted to Markdown for README integration
  - Re-formatted to LaTeX booktabs for manuscript inclusion
  - Compared programmatically (e.g., for cross-paper sensitivity tests)

This is the "esttab postprocess" layer the audit memo flagged as missing
(plan §Tier 3). It lets ``papers/<id>/tables.py`` build Table 2-N functions
by reading Stata's CSV side-channel, eliminating the need to re-implement
regression logic in Python (which is hard to keep synchronized with .do).

Supported input formats
-----------------------
1. ``esttab`` CSV (default) — variable + (SE) rows, model columns.
2. ``esttab`` with ``stats`` footer rows (N, r2, F, etc.).
3. Significance stars in ``*``/``**``/``***`` notation.

Not supported (out of scope for P2):
- ``outreg2`` text format (legacy)
- Pre-Stata 14 ``estout`` raw matrix dumps
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple

import pandas as pd

# ============================================================================
# Constants
# ============================================================================

_SE_PAREN_RE = re.compile(r'^\s*\(([\-\d\.]+)\)\s*$')
_STARS_RE = re.compile(r'(\*{1,3})$')
_NUMBER_RE = re.compile(r'^[\-\d\.]+')

# Standard footer stat names that esttab emits.
_KNOWN_STATS = frozenset({
    'N', 'r2', 'r2_a', 'F', 'aic', 'bic', 'll', 'rmse', 'p',
    'widstat', 'idstat',  # ivreg2 / ivreghdfe weak-id stats
    'mss', 'rss',         # sum of squares
})


# ============================================================================
# Data classes
# ============================================================================

class Coefficient(NamedTuple):
    """A single regression coefficient cell parsed from esttab output."""
    value: float          # the coefficient itself
    se: float | None      # standard error (from parenthesized row below)
    stars: int            # 0/1/2/3 — number of significance stars

    def as_string(self, b_fmt: str = '.3f', se_fmt: str = '.3f') -> str:
        """Render to 'coef*** (se)' style string."""
        star_str = '*' * self.stars
        out = f'{self.value:{b_fmt}}{star_str}'
        if self.se is not None:
            out += f' ({self.se:{se_fmt}})'
        return out


# ============================================================================
# Core parser
# ============================================================================

def parse_esttab_csv(path: str | Path) -> pd.DataFrame:
    """Parse an esttab CSV output into a DataFrame indexed by variable name.

    The returned DataFrame has variable names as the index and model labels
    as columns. Each cell contains a ``Coefficient`` namedtuple combining the
    point estimate, standard error, and significance star count.

    Args:
        path: Path to esttab CSV file (typically esttab .. using "...".csv).

    Returns:
        DataFrame[variable -> model -> Coefficient]. Footer stats (N, r2,
        etc.) appear as separate rows with ``Coefficient(value=N, se=None,
        stars=0)``.

    Raises:
        FileNotFoundError: path does not exist.
        ValueError:        CSV not recognizable as esttab output.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"esttab CSV not found: {path}")

    raw = pd.read_csv(path, header=None, dtype=str, keep_default_na=False)
    if raw.empty:
        raise ValueError(f"esttab CSV is empty: {path}")

    # First non-empty row = header (model labels).
    header_idx = 0
    while header_idx < len(raw) and not any(raw.iloc[header_idx].astype(str).str.strip()):
        header_idx += 1
    if header_idx == len(raw):
        raise ValueError(f"esttab CSV has no header row: {path}")

    header_row = raw.iloc[header_idx].astype(str).tolist()
    model_labels = [c.strip() for c in header_row[1:]]
    body = raw.iloc[header_idx + 1:].reset_index(drop=True)

    coef_rows: dict[str, list[Coefficient | None]] = {}
    current_var: str | None = None

    for i in range(len(body)):
        cells = body.iloc[i].astype(str).tolist()
        first = cells[0].strip()
        rest = [c.strip() for c in cells[1:]]

        # Check if this is a SE row (all cells parenthesized)
        is_se_row = (not first) and all(
            (not c) or _SE_PAREN_RE.match(c) for c in rest
        )

        if is_se_row and current_var is not None:
            # Attach SEs to previous coefficient row
            existing = coef_rows.get(current_var, [None] * len(model_labels))
            for col_idx, cell in enumerate(rest):
                m = _SE_PAREN_RE.match(cell)
                if m and existing[col_idx] is not None:
                    se_val = float(m.group(1))
                    existing[col_idx] = Coefficient(
                        value=existing[col_idx].value,
                        se=se_val,
                        stars=existing[col_idx].stars,
                    )
            coef_rows[current_var] = existing
            current_var = None
            continue

        if not first:
            continue  # blank row

        current_var = first
        row: list[Coefficient | None] = []
        for cell in rest:
            if not cell or cell == '.':
                row.append(None)
                continue
            stars_m = _STARS_RE.search(cell)
            stars = len(stars_m.group(1)) if stars_m else 0
            num_m = _NUMBER_RE.match(cell)
            if num_m:
                try:
                    val = float(num_m.group(0))
                    row.append(Coefficient(value=val, se=None, stars=stars))
                except ValueError:
                    row.append(None)
            else:
                row.append(None)
        coef_rows[current_var] = row

    df = pd.DataFrame(coef_rows).T
    df.columns = model_labels[:df.shape[1]] if df.shape[1] <= len(model_labels) else df.columns
    df.index.name = 'variable'
    return df


# ============================================================================
# Renderers
# ============================================================================

def to_markdown_table(df: pd.DataFrame,
                      *,
                      b_fmt: str = '.3f',
                      se_fmt: str = '.3f',
                      include_se: bool = True,
                      stats_separator: bool = True) -> str:
    """Render the parsed esttab DataFrame as a Markdown table.

    Args:
        df:               DataFrame returned by parse_esttab_csv.
        b_fmt:            Format spec for coefficients.
        se_fmt:           Format spec for SEs.
        include_se:       If True, append SE on next row in parens.
        stats_separator:  If True, insert a horizontal rule before footer
                          stats (N / r2 / etc.).
    """
    header = ['Variable'] + list(df.columns)
    lines = ['| ' + ' | '.join(header) + ' |']
    lines.append('|' + '|'.join(['---'] * len(header)) + '|')

    stats_started = False
    for var, row in df.iterrows():
        if stats_separator and not stats_started and var in _KNOWN_STATS:
            lines.append('|' + '|'.join(['---'] * len(header)) + '|')
            stats_started = True
        coef_cells = []
        se_cells = []
        for col in df.columns:
            cell = row[col]
            if isinstance(cell, Coefficient):
                stars = '*' * cell.stars
                coef_cells.append(f'{cell.value:{b_fmt}}{stars}')
                if cell.se is not None and include_se:
                    se_cells.append(f'({cell.se:{se_fmt}})')
                else:
                    se_cells.append('')
            else:
                coef_cells.append('')
                se_cells.append('')
        lines.append('| ' + var + ' | ' + ' | '.join(coef_cells) + ' |')
        if include_se and any(se_cells) and var not in _KNOWN_STATS:
            lines.append('|  | ' + ' | '.join(se_cells) + ' |')

    return '\n'.join(lines)


def to_latex_booktabs(df: pd.DataFrame,
                      *,
                      b_fmt: str = '.3f',
                      se_fmt: str = '.3f',
                      include_se: bool = True,
                      caption: str = '',
                      label: str = '') -> str:
    """Render the parsed esttab DataFrame as a LaTeX booktabs table."""
    n_cols = len(df.columns)
    col_spec = 'l' + 'c' * n_cols
    out_lines = [
        r'\begin{table}[!ht]',
        r'\centering',
        f'\\caption{{{caption}}}' if caption else '',
        f'\\label{{{label}}}' if label else '',
        f'\\begin{{tabular}}{{{col_spec}}}',
        r'\toprule',
        ' & ' + ' & '.join(str(c) for c in df.columns) + r' \\',
        r'\midrule',
    ]
    stats_split = False
    for var, row in df.iterrows():
        if not stats_split and var in _KNOWN_STATS:
            out_lines.append(r'\midrule')
            stats_split = True
        coef_row = [_latex_escape(var)]
        se_row = ['']
        any_se = False
        for col in df.columns:
            cell = row[col]
            if isinstance(cell, Coefficient):
                stars = '$^{' + '*' * cell.stars + '}$' if cell.stars else ''
                coef_row.append(f'{cell.value:{b_fmt}}{stars}')
                if cell.se is not None and include_se and var not in _KNOWN_STATS:
                    se_row.append(f'({cell.se:{se_fmt}})')
                    any_se = True
                else:
                    se_row.append('')
            else:
                coef_row.append('')
                se_row.append('')
        out_lines.append(' & '.join(coef_row) + r' \\')
        if include_se and any_se:
            out_lines.append(' & '.join(se_row) + r' \\')
    out_lines.extend([
        r'\bottomrule',
        r'\end{tabular}',
        r'\end{table}',
    ])
    return '\n'.join(line for line in out_lines if line)


def _latex_escape(s: str) -> str:
    """Minimal LaTeX-special-character escape for variable names."""
    return (s.replace('_', r'\_')
             .replace('&', r'\&')
             .replace('%', r'\%')
             .replace('$', r'\$')
             .replace('#', r'\#'))


# ============================================================================
# Convenience: full pipeline (csv → markdown / latex)
# ============================================================================

def esttab_csv_to_markdown(csv_path: str | Path, **kwargs) -> str:
    """Shortcut: parse + render markdown."""
    return to_markdown_table(parse_esttab_csv(csv_path), **kwargs)


def esttab_csv_to_latex(csv_path: str | Path, **kwargs) -> str:
    """Shortcut: parse + render LaTeX."""
    return to_latex_booktabs(parse_esttab_csv(csv_path), **kwargs)


# ============================================================================
# Paper-aware path resolution (P2.2: bridge to papers/<id>/tables.py)
# ============================================================================

def read_paper_esttab(paper_id: str,
                      csv_filename: str,
                      paper_config=None,
                      *,
                      tables_subdir: str = 'tables') -> pd.DataFrame:
    """Read an esttab CSV from a paper's standard output location.

    Default path: ``papers_assets/<paper_id>/output/<tables_subdir>/<csv_filename>``.

    Args:
        paper_id:      e.g. 'llm_peer'.
        csv_filename:  e.g. 'table2_main_iv_2sls.csv'.
        paper_config:  Optional PaperConfig (else built from paper_id).
        tables_subdir: Override 'tables' subdir if needed.

    Returns:
        DataFrame from parse_esttab_csv.

    Raises:
        FileNotFoundError: csv not yet produced (run Stata first).
    """
    from news_process.papers._common.paper_config import get_paper_config

    pc = paper_config or get_paper_config(paper_id)
    csv_path = pc.output_dir / tables_subdir / csv_filename
    if not csv_path.exists():
        raise FileNotFoundError(
            f"esttab CSV not found: {csv_path}. "
            f"Run the Stata .do for paper={paper_id!r} first "
            f"(e.g. via build_derivative_replication_package + StataMP-64 -b do <do_file>)."
        )
    return parse_esttab_csv(csv_path)


__all__ = [
    'Coefficient',
    'parse_esttab_csv',
    'to_markdown_table',
    'to_latex_booktabs',
    'esttab_csv_to_markdown',
    'esttab_csv_to_latex',
    'read_paper_esttab',
]
