"""news_process.core.reporting — dataset persistence + DataFrame & pipeline reports.

Merges three legacy modules:
  - ``utils/helpers.py``   reporting helpers   → ``save_dataset`` / ``safe_save_preview_csv``
  - ``utils/reporting.py`` DataFrame analysis  → ``generate_dataframe_report`` / ``_format_stat`` / ``_is_categorical``
  - ``utils/pipeline_reporting.py``            → ``generate_pipeline_summary``

Public API surface (forwarded by the legacy ``utils/*.py`` shims):
``save_dataset``, ``safe_save_preview_csv``, ``generate_dataframe_report``,
``_format_stat``, ``_is_categorical``, ``generate_pipeline_summary``.
"""

from __future__ import annotations

import logging
import os

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


# ============================================================================
# 1. Dataset persistence (Parquet + CSV preview).  From utils/helpers.py.
# ============================================================================


def safe_save_preview_csv(df: pd.DataFrame, preview_path: str, logger=None):
    """Save the first 5,000 rows as a CSV preview, swallowing PermissionError.

    CSV preview is a non-critical path: a write failure (typically because
    Excel has the file open) must not abort the main pipeline.  We log a
    warning and continue.
    """
    try:
        df_preview = df.head(5000) if hasattr(df, 'head') else df
        df_preview.to_csv(preview_path, index=False, encoding='utf-8-sig')
        if logger:
            logger.info(f"已生成预览文件: {preview_path}")
    except PermissionError as e:
        if logger:
            logger.warning(
                f"无法保存预览文件 (可能正被其它软件占用): {preview_path} | {e}"
            )
    except Exception as e:
        if logger:
            logger.error(f"保存预览文件时发生未知错误: {preview_path} | {e}")


def save_dataset(df: pd.DataFrame, output_path: str, logger=None):
    """Persist ``df`` as Parquet + CSV preview at ``output_path``.

    The ``.parquet`` is the contract format; the same-stem ``.csv`` is a
    non-critical preview (failure to write CSV does not raise).
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        df.to_parquet(output_path, index=False)
        if logger:
            logger.info(
                f"已保存 parquet 文件: {output_path}  ({len(df):,} 行)"
            )
    except Exception as e:
        if logger:
            logger.error(f"保存 parquet 文件失败: {output_path} | {e}")
        raise

    csv_path = os.path.splitext(output_path)[0] + ".csv"
    safe_save_preview_csv(df, csv_path, logger)


# ============================================================================
# 2. DataFrame analysis report.  From utils/reporting.py (verbatim).
# ============================================================================


def _format_stat(value, precision=2):
    """Format a numeric value for log output, returning ``"N/A"`` for NaN."""
    if pd.isna(value):
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{value:.{precision}f}"
    return str(value)


def _is_categorical(dtype):
    """pandas >= 2.1 compatible categorical-dtype check."""
    return isinstance(dtype, pd.CategoricalDtype)


def generate_dataframe_report(df: pd.DataFrame, logger: logging.Logger):
    """Emit a verbose statistical report for ``df`` to ``logger``.

    Sections:
      1. Overall: shape, duplicate-row count, memory footprint, dtype mix.
      2. Per-column: missing rate, unique count, type-aware stats
         (numeric five-number summary / datetime range / boolean counts /
         categorical-or-object value distribution).

    Designed to be defensive: any internal failure is logged at WARNING level
    rather than raised, so report generation cannot break the host pipeline.
    """
    try:
        logger.info("\n" + "=" * 60)
        logger.info(" DataFrame 统计报告 (DataFrame Statistics Report)")
        logger.info("=" * 60)

        if df.empty:
            logger.warning("输入数据为空，无法生成详细统计报告。")
            logger.info("=" * 60 + "\n")
            return

        total_rows = len(df)
        logger.info(
            f"数据维度 (Shape): {df.shape[0]:,} 行, {df.shape[1]} 列"
        )

        duplicate_rows = df.duplicated().sum()
        duplicate_percentage = (
            (duplicate_rows / total_rows) * 100 if total_rows > 0 else 0
        )
        logger.info(
            f"重复行数 (Duplicate Rows): {duplicate_rows:,} "
            f"({duplicate_percentage:.2f}%)"
        )

        memory_usage_bytes = df.memory_usage(deep=True).sum()
        if memory_usage_bytes < 1024 ** 2:
            memory_usage, unit = memory_usage_bytes / 1024, "KB"
        elif memory_usage_bytes < 1024 ** 3:
            memory_usage, unit = memory_usage_bytes / (1024 ** 2), "MB"
        else:
            memory_usage, unit = memory_usage_bytes / (1024 ** 3), "GB"
        logger.info(f"内存占用 (Memory Usage): {memory_usage:.2f} {unit}")

        logger.info("数据类型概览 (Data Types Summary):")
        dtype_counts_str = df.dtypes.value_counts().to_string()
        indented = "\n".join(
            [f"    {line}" for line in dtype_counts_str.split('\n')]
        )
        logger.info(indented)

        logger.info("\n" + "-" * 60)
        logger.info(" 字段逐一分析报告 (Column Analysis Report)")
        logger.info("-" * 60)

        for column in df.columns:
            col_series = df[column]
            dtype = col_series.dtype

            logger.info(f"\n--- 字段 (Column): '{column}' ---")
            logger.info(f"    - 数据类型 (Dtype): {dtype}")

            missing_count = col_series.isnull().sum()
            if total_rows > 0:
                missing_pct = (missing_count / total_rows) * 100
                logger.info(
                    f"    - 缺失值 (Missing Values): "
                    f"{missing_count:,} ({missing_pct:.2f}%)"
                )
            else:
                logger.info(
                    f"    - 缺失值 (Missing Values): {missing_count:,} (N/A%)"
                )

            unique_count = col_series.nunique()
            logger.info(f"    - 唯一值数量 (Unique Values): {unique_count:,}")

            if col_series.isnull().all():
                logger.info("    - 该字段所有值均为空。")

            elif np.issubdtype(dtype, np.number):
                stats = col_series.describe()
                logger.info("    - 数值统计 (Numeric Stats):")
                logger.info(
                    f"      - 均值 (mean): {_format_stat(stats.get('mean'))}"
                )
                logger.info(
                    f"      - 标准差 (std): {_format_stat(stats.get('std'))}"
                )
                logger.info(
                    f"      - 最小值 (min): {_format_stat(stats.get('min'))}"
                )
                logger.info(
                    f"      - 25% 分位数: {_format_stat(stats.get('25%'))}"
                )
                logger.info(
                    f"      - 中位数 (50%): {_format_stat(stats.get('50%'))}"
                )
                logger.info(
                    f"      - 75% 分位数: {_format_stat(stats.get('75%'))}"
                )
                logger.info(
                    f"      - 最大值 (max): {_format_stat(stats.get('max'))}"
                )

            elif pd.api.types.is_datetime64_any_dtype(dtype):
                logger.info("    - 日期时间统计 (Datetime Stats):")
                min_date, max_date = col_series.min(), col_series.max()
                logger.info(f"      - 最早时间 (Earliest): {min_date}")
                logger.info(f"      - 最晚时间 (Latest):   {max_date}")
                if pd.notna(min_date) and pd.notna(max_date):
                    logger.info(
                        f"      - 时间跨度 (Duration):  {max_date - min_date}"
                    )

            elif pd.api.types.is_bool_dtype(dtype):
                logger.info("    - 布尔值分布 (Boolean Value Counts):")
                logger.info(
                    f"\n{col_series.value_counts(dropna=False).to_string()}"
                )

            elif pd.api.types.is_object_dtype(dtype) or _is_categorical(dtype):
                if unique_count <= 15:
                    logger.info("    - 值分布 (Value Counts):")
                    logger.info(
                        f"\n{col_series.value_counts(dropna=False).to_string()}"
                    )
                else:
                    logger.info(
                        "    - 最常见的5个值 (Top 5 Most Common Values):"
                    )
                    logger.info(
                        f"\n{col_series.value_counts().head(5).to_string()}"
                    )

        logger.info("\n" + "=" * 60)
        logger.info(" 报告结束 (End of Report)")
        logger.info("=" * 60 + "\n")

    except Exception as e:
        logger.warning(
            f"生成统计报告时发生错误（不影响数据处理）: {e}",
            exc_info=True,
        )


# ============================================================================
# 3. End-of-pipeline data-flow summary.  From utils/pipeline_reporting.py.
# ============================================================================


def generate_pipeline_summary(config, logger):
    """Print an end-of-run pipeline summary report.

    Two granularities:
      1. Article-level data-flow (00 -> 24): row count per stage,
         delta vs previous, retention vs initial.
      2. Bank-Year panel summary (45 / 51): row x column counts.

    Uses ``pyarrow.parquet.read_metadata`` for cheap row counts (only
    reads the parquet footer, no full load), then loads the final stage
    fully for ``generate_dataframe_report``.
    """
    logger.info("\n" + "=" * 70)
    logger.info("===          数据管道执行摘要报告 (Pipeline Summary)         ===")
    logger.info("=" * 70)

    stages = [
        ("模块一: 00_preprocessing", "output_00_preprocessing"),
        ("模块二: 11_news_bank", "output_11_bank_news"),
        ("模块二: 12_news_fintech", "output_12_fintech_news"),
        ("模块二: 14_fintech_intensity", "output_14_fintech_intensity"),
        ("模块三: 21_tone_llms", "output_21_tone_llms"),
        ("模块三: 21_tone_llms(全量)", "output_21_tone_llms_full"),
        ("模块三: 22_tone_words", "output_22_words_tone"),
        ("模块三: 23_tone_berts", "output_23_bert_tone"),
        ("模块三: 24_herd_decay", "output_24_herd_decay"),
    ]

    summary_data = []
    previous_count = 0
    initial_count = 0

    output_dir = config['paths']['output_dir']

    for stage_name, filename_key in stages:
        filename = config['filenames'].get(filename_key)
        if not filename:
            logger.warning(
                f"阶段 {stage_name} 的输出文件名未在配置中找到 "
                f"(key: {filename_key})。"
            )
            continue

        file_path = os.path.join(output_dir, filename)

        try:
            current_count = 0
            if os.path.exists(file_path):
                metadata = pq.read_metadata(file_path)
                current_count = metadata.num_rows
            else:
                logger.warning(f"文件未找到: {file_path}")

            if stage_name == "模块一: 00_preprocessing":
                change = 0
                pct_change = 0.0
                initial_count = current_count
                retention_rate = 100.0
            else:
                change = current_count - previous_count
                pct_change = (
                    (change / previous_count * 100)
                    if previous_count > 0 else 0.0
                )
                retention_rate = (
                    (current_count / initial_count * 100)
                    if initial_count > 0 else 0.0
                )

            summary_data.append({
                "Stage": stage_name,
                "Rows": current_count,
                "Change": change,
                "Change (%)": f"{pct_change:+.2f}%",
                "Retention (vs Initial)": f"{retention_rate:.2f}%",
            })

            previous_count = current_count

        except Exception as e:
            logger.error(f"无法读取阶段 {stage_name} 的输出文件: {e}")
            summary_data.append({
                "Stage": stage_name,
                "Rows": "Error",
                "Change": "N/A",
                "Change (%)": "N/A",
                "Retention (vs Initial)": "N/A",
            })

    summary_df = pd.DataFrame(summary_data)
    logger.info("\n数据流转统计 (Data Flow Summary):")
    logger.info("\n" + summary_df.to_string(index=False))

    final_stage_key = stages[-1][1]
    final_filename = config['filenames'].get(final_stage_key)
    if final_filename:
        final_file_path = os.path.join(output_dir, final_filename)
        if os.path.exists(final_file_path):
            logger.info(
                f"\n正在生成最终数据 ({final_filename}) 的详细统计报告..."
            )
            try:
                final_df = pd.read_parquet(final_file_path)
                generate_dataframe_report(final_df, logger)
            except Exception as e:
                logger.error(f"生成最终详细报告失败: {e}")
        else:
            logger.warning(
                f"最终输出文件不存在，无法生成详细统计: {final_file_path}"
            )

    panel_stages = [
        ("模块五: 45_panel_export_main", "output_40_panel_yearly"),
        ("模块五: 45_article_bank", "output_40_article_bank"),
        ("模块六: 51_falsification", "output_51_panel_controls"),
    ]

    panel_data = []
    for stage_name, filename_key in panel_stages:
        filename = config['filenames'].get(filename_key)
        if not filename:
            continue
        file_path = os.path.join(output_dir, filename)
        try:
            if os.path.exists(file_path):
                metadata = pq.read_metadata(file_path)
                panel_data.append({
                    "Stage": stage_name,
                    "Rows": metadata.num_rows,
                    "Columns": metadata.num_columns,
                })
            else:
                panel_data.append({
                    "Stage": stage_name,
                    "Rows": "未生成",
                    "Columns": "N/A",
                })
        except Exception as e:
            logger.error(
                f"无法读取面板阶段 {stage_name} 的输出: {e}"
            )
            panel_data.append({
                "Stage": stage_name,
                "Rows": "Error",
                "Columns": "N/A",
            })

    if panel_data:
        panel_summary_df = pd.DataFrame(panel_data)
        logger.info(
            "\n面板构建阶段统计 (Panel Construction Summary, Bank-Year 级):"
        )
        logger.info("\n" + panel_summary_df.to_string(index=False))
