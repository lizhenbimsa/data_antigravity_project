"""news_process.papers._common.tables — 通用 Stata 安全列名清洗 + .dta 导出 + 描述统计.

定位差异 (vs ``pipeline/panel/export.py:export_panel``)
------------------------------------------------------
- ``pipeline/panel/export.py`` 是 **bank-fintech-tone 主线论文专属**:
   - 含 940+ 行 STATA_LABELS 字典 (硬编码 700+ 银行面板变量的英文标签)
   - 与 ``CONFIG['filenames']['output_40_*']`` 强耦合
   - 写死了输出位置 (``OUTPUT_DIR/40_panel_yearly.dta``)
- ``papers/_common/tables.py`` 是 **跨论文通用**:
   - 接受任意 ``df + label_map``, 不预设业务变量
   - 复用 ``pipeline.panel.export`` 的 32-字符列名规整逻辑 (避免重写)
   - 输出位置由调用方决定

衍生论文 (benefit_society / brokerage_network / llm_peer / strategic_diff)
都应使用本模块导出 .dta; 主线论文继续使用既有的 ``pipeline.panel.export``.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------
# 1. Stata 列名清洗 (32 字符 + ASCII + 防碰撞)
# ----------------------------------------------------------------------------


def sanitize_stata_columns(columns: Sequence[str],
                           max_len: int = 32) -> list[str]:
    """把 pandas 列名规整为 Stata 合法标识符.

    S3 fix v2 (2026-05-30) 起, 本函数 **委托** 给 stage 46 的规范清洗器
    (``stata_export.shorten_long_column_names`` → ``asciify_non_ascii_columns``),
    确保 40-path (stage 45/51 经本函数) 与 46-path 产出**字节级一致**的 Stata 名:

    1. 中英文括号 ``()``/``（）`` 替换为 ``_`` (本函数 pre-process; 46-path 不做)。
    2. 空字符串或全为 ``_`` 的列名替换为 ``col_<i>`` 占位 (同上 pre-process)。
    3. 重复的**输入**名追加 ``_<n>`` 消歧 (DataFrame 列本就唯一, 对真实面板为 no-op;
       仅加固通用工具对重复输入的鲁棒性)。
    4. 缩写 + 截断到 **32 字符** (``stata_export.STATA_VAR_NAME_MAXLEN`` 硬编码),
       保留 ``_full``/``_ctx`` 等判别后缀。
    5. 残留非 ASCII (中文 正面/负面/中性 → pos/neg/neu); 截断后冲突用 6-char md5
       后缀去重 (跨 run 确定性)。

    Args:
        columns:   原始列名列表。
        max_len:   **历史兼容形参, 已不参与截断**。委托后统一走 46-path 的
                   32-字符上限 (``STATA_VAR_NAME_MAXLEN``); 传入非 32 不改变行为。
                   保留仅为不破坏现有 4 处 ``max_len=32`` 调用签名。

    Returns:
        长度等于 ``len(columns)`` 的清洗后列名列表 (全部 ≤32 字符、唯一、合法)。
    """
    # S3 fix v2 (2026-05-30): delegate to the canonical 46-path sanitizer
    # (stata_export.shorten_long_column_names → asciify_non_ascii_columns, IN THAT
    # ORDER, exactly as stage 46 applies them at stata_export.py:643/654) so the
    # 40-path (pipeline/panel/export.py calls THIS function) and the 46-path emit
    # BYTE-IDENTICAL Stata names — eliminating the two-divergent-name-sets defect
    # entirely. The earlier fix only removed pos/neg collisions but still diverged
    # at 125/2129 cols (base_len=28 vs the 46-path's 32-char truncation/abbrev).
    # Single source of truth = stata_export; lazy import keeps it leaf-safe
    # (stata_export imports neither tables nor export → no cycle).
    # max_len is honored as the 46-path's 32-char Stata-14+ cap.
    import pandas as _pd

    from news_process.pipeline.panel.stata_export import (
        asciify_non_ascii_columns as _asciify,
    )
    from news_process.pipeline.panel.stata_export import (
        shorten_long_column_names as _shorten,
    )

    # Pre-process the two things the 46-path does NOT do: ()/（）→ _ and
    # empty / all-underscore → col_<i> (panel & derivative-paper columns may carry
    # parens; the 46-path assumes already-paren-free names).
    pre: list[str] = []
    _seen_pre: dict[str, int] = {}
    for i, raw in enumerate(columns):
        c = str(raw).replace('(', '_').replace(')', '_')
        c = c.replace('（', '_').replace('）', '_')
        if not c or not c.strip('_'):
            c = f'col_{i}'
        # Disambiguate genuine DUPLICATE input names: the 46-path md5 collision
        # suffix hashes the (original) string, so identical inputs would hash to
        # the same name and stay collided. Real DataFrame columns are unique, so
        # this is a no-op on the panel (byte-identity with the 46-path preserved)
        # — it only hardens the general-purpose utility against duplicate inputs.
        if c in _seen_pre:
            _seen_pre[c] += 1
            c = f'{c}_{_seen_pre[c]}'
        else:
            _seen_pre[c] = 0
        pre.append(c)

    _df = _pd.DataFrame(columns=pre)
    _df, _ = _shorten(_df)
    _df, _ = _asciify(_df)
    return list(_df.columns)


# ----------------------------------------------------------------------------
# 2. 通用 Stata .dta 导出
# ----------------------------------------------------------------------------


def export_dta(df: pd.DataFrame,
               output_path: str | Path,
               label_map: Mapping[str, str] | None = None,
               *,
               version: int = 118,
               max_col_len: int = 32) -> Path:
    """把 DataFrame 导出为 Stata .dta, 自动处理常见数据类型陷阱.

    自动应用以下规整:
    1. 列名通过 ``sanitize_stata_columns`` 清洗 (ASCII + 防碰撞)。
    2. ``Float64``/``Int64`` (pandas nullable) 降级为 ``float`` (Stata 不支持)。
    3. 若提供 ``label_map``, 仅保留实际存在于 (清洗后) 列名中的条目。
    4. ``version=118`` 默认对应 Stata 14+ (32-字符列名上限)。

    .. warning::
       S3 fix v2 起 ``sanitize_stata_columns`` 委托 46-path, **硬编码 32-字符**
       列名上限, 不再尊重 ``max_col_len``。因此 **不支持 Stata 13 (version=117,
       30-字符上限)**: 传 ``version=117, max_col_len=30`` 仍会产出 32-字符名,
       写入 v117 .dta 后这些名在 Stata 13 中非法。这与项目 "Stata 19+ only,
       无需向下兼容" 策略 (见 CLAUDE.md) 一致 — 请使用默认 ``version=118``。

    Args:
        df:           待导出的 DataFrame (函数内部 .copy(), 不修改源数据)。
        output_path:  目标 .dta 路径 (会自动创建父目录)。
        label_map:    可选 — ``{cleaned_col_name: variable_label}``,
                      标签 ≤80 字符。
        version:      Stata 文件版本号 (默认 118 = Stata 14+)。
        max_col_len:  **已废弃形参, 不参与截断** (委托后固定 32 字符)。

    Returns:
        实际写入的绝对路径 (Path)。
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df_stata = df.copy()
    df_stata.columns = sanitize_stata_columns(df_stata.columns, max_len=max_col_len)

    nullable_types = ['Float64', 'Int64']
    for col in df_stata.select_dtypes(include=nullable_types).columns:
        df_stata[col] = df_stata[col].astype(float)

    labels = None
    if label_map:
        labels = {k: v for k, v in label_map.items() if k in df_stata.columns}

    df_stata.to_stata(
        os.fspath(output_path),
        write_index=False,
        version=version,
        variable_labels=labels,
    )
    return output_path


# ----------------------------------------------------------------------------
# 3. 描述统计 (Table 1 模板)
# ----------------------------------------------------------------------------


def summary_stats(df: pd.DataFrame,
                  variables: Sequence[str] | None = None,
                  *,
                  percentiles: Sequence[float] = (0.25, 0.5, 0.75)) -> pd.DataFrame:
    """生成发表级描述统计表 (N / Mean / SD / Min / P25 / P50 / P75 / Max).

    Args:
        df:           输入面板。
        variables:    可选 — 仅统计这批列; 默认统计所有数值列。
        percentiles:  分位数 (默认四分位)。

    Returns:
        以 variable 为 index 的描述统计 DataFrame, 列顺序固定为
        ``['N', 'Mean', 'SD', 'Min', *Pxx, 'Max']``。
    """
    if variables is None:
        variables = list(df.select_dtypes(include=np.number).columns)
    else:
        variables = list(variables)
        missing = [v for v in variables if v not in df.columns]
        if missing:
            raise KeyError(f"variables 中以下列在 df 中不存在: {missing}")

    rows = []
    for v in variables:
        s = df[v].dropna()
        n = len(s)
        if n == 0:
            row = {'variable': v, 'N': 0, 'Mean': np.nan, 'SD': np.nan,
                   'Min': np.nan, 'Max': np.nan}
            for p in percentiles:
                row[f'P{int(p * 100)}'] = np.nan
        else:
            row = {
                'variable': v,
                'N': n,
                'Mean': float(s.mean()),
                'SD': float(s.std(ddof=1)) if n > 1 else np.nan,
                'Min': float(s.min()),
                'Max': float(s.max()),
            }
            for p in percentiles:
                row[f'P{int(p * 100)}'] = float(s.quantile(p))
        rows.append(row)

    pcols = [f'P{int(p * 100)}' for p in percentiles]
    column_order = ['N', 'Mean', 'SD', 'Min', *pcols, 'Max']
    out = pd.DataFrame(rows).set_index('variable')[column_order]
    return out


__all__ = ['sanitize_stata_columns', 'export_dta', 'summary_stats',
           'build_summary_table', 'write_summary_table']


# ----------------------------------------------------------------------------
# 4. 通用 Table 1 骨架 (消除 5 个论文包的 build_table1/write_table1 重复)
# ----------------------------------------------------------------------------

def build_summary_table(paper_id: str,
                        variables: list[str],
                        panel_filename: str = '40_panel_yearly.parquet',
                        paper_config=None) -> pd.DataFrame:
    """通用 Table 1 描述统计。

    Args:
        paper_id:        论文标识 (如 'bank_fintech_tone')。
        variables:       论文专属变量列表。
        panel_filename:  面板文件名 (默认年度面板)。
        paper_config:    可选已实例化的 PaperConfig。
    """
    from news_process.papers._common import get_paper_config, load_panel

    pc = paper_config or get_paper_config(paper_id)
    panel = load_panel(panel_filename, paper_id=pc.paper_id,
                       project_config=pc.config)
    available = [v for v in variables if v in panel.columns]
    return summary_stats(panel, variables=available)


def write_summary_table(paper_id: str,
                        variables: list[str],
                        paper_config=None,
                        *,
                        filename: str = 'table1_summary_stats.csv',
                        dta_filename: str | None = 'table1_summary_stats.dta') -> Path:
    """计算 Table 1 并写入 ``paper.output_dir``。"""
    from news_process.papers._common import get_paper_config

    pc = paper_config or get_paper_config(paper_id)
    pc.output_dir.mkdir(parents=True, exist_ok=True)
    table = build_summary_table(paper_id, variables, paper_config=pc)
    csv_path = pc.output_dir / filename
    table.to_csv(csv_path, encoding='utf-8-sig')
    if dta_filename:
        export_dta(table.reset_index(), pc.output_dir / dta_filename)
    return csv_path
