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
4. ``esttab`` LaTeX (booktabs) — fix(omni-g-papers-misc-01, 2026-06-11):
   仓库全部 .do.tmpl (2026-06-13 IV 补全后 100 个) 的 esttab 都只写 ``.tex``
   侧通道 (无任何 csv 写出),
   原 CSV-only 解析使 ``papers/<id>/tables.py`` 的 Tables 2-5 全链死接线
   (即使跑通 Stata 也永远 FileNotFoundError)。现新增 ``parse_esttab_tex``
   解析分支, ``read_paper_esttab`` 在 csv 缺失时自动回退同名 .tex。

Not supported (out of scope for P2):
- ``outreg2`` text format (legacy)
- Pre-Stata 14 ``estout`` raw matrix dumps
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import NamedTuple

import pandas as pd

_LOGGER = logging.getLogger(__name__)

# ============================================================================
# Constants
# ============================================================================

# fix(omni-g-papers-misc-07, 2026-06-11): 支持科学计数法 (e-notation)。
# esttab 的 stats 行常用 %9.0g — 全量 T=19 (N≈3000+, ll/aic 大数) 或极小 p 值会
# 产出 '1.23e-05' 形式; 旧 regex r'^[\-\d\.]+' 只截到 '1.23' → 取值静默放大
# 5 个数量级。SE 括号行 regex 同步支持 e-notation (否则 SE 静默丢失)。
_SE_PAREN_RE = re.compile(r'^\s*\(([-+]?[\d\.]+(?:[eE][-+]?\d+)?)\)\s*$')
_STARS_RE = re.compile(r'(\*{1,3})$')
_NUMBER_RE = re.compile(r'^[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')

# esttab 常规输出的表尾统计量名称。
_KNOWN_STATS = frozenset({
    'N', 'r2', 'r2_a', 'F', 'aic', 'bic', 'll', 'rmse', 'p',
    'widstat', 'idstat',  # ivreg2 / ivreghdfe 弱识别检验统计量
    'mss', 'rss',         # 平方和 (模型/残差)
})


# ============================================================================
# 数据类 Data classes
# ============================================================================

class Coefficient(NamedTuple):
    """从 esttab 输出解析出的单个回归系数单元格。"""
    value: float          # 系数值本身
    se: float | None      # 标准误 (来自系数行下方的括号行)
    stars: int            # 0/1/2/3 — 显著性星号个数

    def as_string(self, b_fmt: str = '.3f', se_fmt: str = '.3f') -> str:
        """Render to 'coef*** (se)' style string."""
        star_str = '*' * self.stars
        out = f'{self.value:{b_fmt}}{star_str}'
        if self.se is not None:
            out += f' ({self.se:{se_fmt}})'
        return out


# ============================================================================
# 核心解析器 Core parser
# ============================================================================

def _parse_body_cells(model_labels: list[str],
                      body_rows: list[list[str]],
                      *,
                      source: str = '') -> pd.DataFrame:
    """共享 body 解析核 (CSV 与 .tex 两条入口复用同一行语义).

    ``body_rows``: 已 strip 的单元格行 (首列=变量名/空=SE 行)。
    """
    coef_rows: dict[str, list[Coefficient | None]] = {}
    current_var: str | None = None

    for cells in body_rows:
        first = cells[0].strip() if cells else ''
        rest = [c.strip() for c in cells[1:]]

        # 判断是否为标准误行 (所有单元格都带括号)
        is_se_row = (not first) and all(
            (not c) or _SE_PAREN_RE.match(c) for c in rest
        )

        if is_se_row and current_var is not None:
            # 把标准误挂到上一条系数行上
            existing = coef_rows.get(current_var, [None] * len(model_labels))
            for col_idx, cell in enumerate(rest):
                m = _SE_PAREN_RE.match(cell)
                if m and col_idx < len(existing) and existing[col_idx] is not None:
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

        # fix(omni-g-papers-misc-07, 2026-06-11): 同名变量行守卫 — esttab 多
        # panel 堆叠输出 (Panel A/B / mediation 三方程) 会重复变量名, 旧实现
        # ``coef_rows[var] = row`` 后行静默覆盖前行。现自动加 '__panelN' 后缀
        # 消歧并 warning, 不丢任何 panel 的系数。
        if first in coef_rows:
            n = 2
            while f'{first}__panel{n}' in coef_rows:
                n += 1
            renamed = f'{first}__panel{n}'
            _LOGGER.warning(
                "parse_esttab%s: duplicate variable row %r (multi-panel esttab "
                "output) — renamed to %r to avoid silent overwrite",
                f'[{source}]' if source else '', first, renamed)
            first = renamed

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


def parse_esttab_csv(path: str | Path) -> pd.DataFrame:
    """把 esttab 的 CSV 输出解析为以变量名为索引的 DataFrame。

    返回的 DataFrame 以变量名为 index、模型标签为列。每个单元格是一个
    ``Coefficient`` namedtuple, 合并了点估计、标准误和显著性星号数。

    Args:
        path: esttab CSV 文件路径 (通常由 esttab .. using "...".csv 产出)。

    Returns:
        DataFrame[variable -> model -> Coefficient]。表尾统计量 (N, r2 等)
        以单独的行出现, 形如 ``Coefficient(value=N, se=None, stars=0)``。

    Raises:
        FileNotFoundError: 路径不存在。
        ValueError:        CSV 无法识别为 esttab 输出。
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"esttab CSV not found: {path}")

    raw = pd.read_csv(path, header=None, dtype=str, keep_default_na=False)
    if raw.empty:
        raise ValueError(f"esttab CSV is empty: {path}")

    # 第一条非空行 = 表头 (模型标签)。
    header_idx = 0
    while header_idx < len(raw) and not any(raw.iloc[header_idx].astype(str).str.strip()):
        header_idx += 1
    if header_idx == len(raw):
        raise ValueError(f"esttab CSV has no header row: {path}")

    header_row = raw.iloc[header_idx].astype(str).tolist()
    model_labels = [c.strip() for c in header_row[1:]]
    body = raw.iloc[header_idx + 1:].reset_index(drop=True)
    body_rows = [body.iloc[i].astype(str).tolist() for i in range(len(body))]
    return _parse_body_cells(model_labels, body_rows, source=path.name)


# ── esttab LaTeX (booktabs) 解析分支 ─────────────────────────────────────────

_TEX_MULTICOL_RE = re.compile(r'\\multicolumn\{\d+\}\{[^}]*\}\{(.*)\}')
_TEX_SYM_RE = re.compile(r'\\sym\{(\*{1,3})\}')


def _clean_tex_cell(cell: str) -> str:
    """清洗单个 esttab .tex 单元格 → 与 CSV 单元格同语义的纯文本.

    - ``0.123\\sym{**}`` → ``0.123**`` (stars 与 CSV 同记号)
    - 去掉 inline math 定界符 ``\\( \\)`` / ``$``
    - 反转 esttab 的 LaTeX 转义 (``\\_`` → ``_`` 等)
    """
    c = cell.strip()
    c = _TEX_SYM_RE.sub(lambda m: m.group(1), c)
    c = c.replace(r'\(', '').replace(r'\)', '').replace('$', '')
    for esc, raw_ch in ((r'\_', '_'), (r'\&', '&'), (r'\%', '%'), (r'\#', '#')):
        c = c.replace(esc, raw_ch)
    return c.strip()


def parse_esttab_tex(path: str | Path) -> pd.DataFrame:
    """Parse an esttab LaTeX (booktabs) output — 与 ``parse_esttab_csv`` 同形返回.

    fix(omni-g-papers-misc-01, 2026-06-11): 全部 Stata 模板 esttab 只写 .tex,
    本分支让 python 表层 (``papers/<id>/tables.py`` Tables 2-5 与 coefplot 链)
    无需 CSV 侧通道即可消费 Stata 产物。

    解析约定 (esttab 默认 tex 输出):
    - 仅处理含 ``&`` 且以 ``\\\\`` 结尾的表体行。
    - 第一条含 ``\\multicolumn`` 的行 → model labels (通常 ``(1) (2) ...``);
      其余 multicolumn 行 (mtitles 等) 跳过。
    - ``\\sym{**}`` → ``**``; ``\\(N\\)`` → ``N``; ``a\\_b`` → ``a_b``。

    Raises:
        FileNotFoundError: path does not exist.
        ValueError:        .tex 中找不到任何可解析的 esttab 表体。
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"esttab .tex not found: {path}")

    model_labels: list[str] | None = None
    body_rows: list[list[str]] = []
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        s = line.strip()
        if '&' not in s:
            continue
        if s.endswith(r'\\'):
            s = s[:-2]
        raw_cells = s.split('&')
        if any(_TEX_MULTICOL_RE.search(c) for c in raw_cells):
            if model_labels is None:
                model_labels = []
                for c in raw_cells[1:]:
                    m = _TEX_MULTICOL_RE.search(c)
                    model_labels.append(_clean_tex_cell(m.group(1)) if m
                                        else _clean_tex_cell(c))
            continue  # 后续 multicolumn 行 (mtitles / group headers) 跳过
        body_rows.append([_clean_tex_cell(c) for c in raw_cells])

    if model_labels is None or not body_rows:
        raise ValueError(f"not recognizable as esttab LaTeX output: {path}")
    return _parse_body_cells(model_labels, body_rows, source=path.name)


# ============================================================================
# Renderers
# ============================================================================

def to_markdown_table(df: pd.DataFrame,
                      *,
                      b_fmt: str = '.3f',
                      se_fmt: str = '.3f',
                      include_se: bool = True,
                      stats_separator: bool = True) -> str:
    """把解析后的 esttab DataFrame 渲染为 Markdown 表格。

    Args:
        df:               parse_esttab_csv 返回的 DataFrame。
        b_fmt:            系数的格式化 spec。
        se_fmt:           标准误的格式化 spec。
        include_se:       为 True 时在下一行以括号追加标准误。
        stats_separator:  为 True 时在表尾统计量 (N / r2 等) 前插入分隔线。
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
    """把解析后的 esttab DataFrame 渲染为 LaTeX booktabs 表格。"""
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
    """对变量名做最小集 LaTeX 特殊字符转义。"""
    return (s.replace('_', r'\_')
             .replace('&', r'\&')
             .replace('%', r'\%')
             .replace('$', r'\$')
             .replace('#', r'\#'))


# ============================================================================
# 便捷封装: 全流程 (csv → markdown / latex)
# ============================================================================

def esttab_csv_to_markdown(csv_path: str | Path, **kwargs) -> str:
    """Shortcut: parse + render markdown."""
    return to_markdown_table(parse_esttab_csv(csv_path), **kwargs)


def esttab_csv_to_latex(csv_path: str | Path, **kwargs) -> str:
    """Shortcut: parse + render LaTeX."""
    return to_latex_booktabs(parse_esttab_csv(csv_path), **kwargs)


# ============================================================================
# 感知论文目录的路径解析 (P2.2: 桥接到 papers/<id>/tables.py)
# ============================================================================

def read_paper_esttab(paper_id: str,
                      csv_filename: str,
                      paper_config=None,
                      *,
                      tables_subdir: str = 'tables') -> pd.DataFrame:
    """Read an esttab output from a paper's standard output location.

    Default path: ``papers_assets/<paper_id>/output/<tables_subdir>/<csv_filename>``.

    fix(omni-g-papers-misc-01, 2026-06-11): 全部 .do.tmpl (2026-06-13 后 100 个) 的 esttab 一律
    ``using ".../<name>.tex"`` (无 csv 写出), 故 csv 缺失时自动回退解析**同名
    .tex** (``parse_esttab_tex``) — 否则即使完整跑通 Stata 复现包, 本函数也
    永远 FileNotFoundError (CSV 桥死接线)。

    Args:
        paper_id:      e.g. 'llm_peer'.
        csv_filename:  e.g. 'table2_main_iv_2sls.csv' (同名 .tex 自动回退).
        paper_config:  Optional PaperConfig (else built from paper_id).
        tables_subdir: Override 'tables' subdir if needed.

    Returns:
        DataFrame from parse_esttab_csv / parse_esttab_tex.

    Raises:
        FileNotFoundError: 同名 csv 与 tex 均未产出 (run Stata first).
    """
    from news_process.papers._common.paper_config import get_paper_config

    pc = paper_config or get_paper_config(paper_id)
    csv_path = pc.output_dir / tables_subdir / csv_filename
    if csv_path.exists():
        return parse_esttab_csv(csv_path)
    tex_path = csv_path.with_suffix('.tex')
    if tex_path.exists():
        _LOGGER.info("read_paper_esttab[%s]: csv 缺失, 回退同名 .tex → %s",
                     paper_id, tex_path.name)
        return parse_esttab_tex(tex_path)
    raise FileNotFoundError(
        f"esttab output not found: {csv_path} (nor sibling {tex_path.name}). "
        f"Run the Stata .do for paper={paper_id!r} first "
        f"(e.g. via build_derivative_replication_package + StataMP-64.exe /b do <do_file>)."
    )


__all__ = [
    'Coefficient',
    'parse_esttab_csv',
    'parse_esttab_tex',
    'to_markdown_table',
    'to_latex_booktabs',
    'esttab_csv_to_markdown',
    'esttab_csv_to_latex',
    'read_paper_esttab',
]
