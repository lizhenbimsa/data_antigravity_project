"""news_process.core.reporting — 数据集持久化 + DataFrame 与流水线报告。

由三个历史模块合并而来:
  - ``utils/helpers.py``   reporting helpers   → ``save_dataset`` / ``safe_save_preview_csv``
  - ``utils/reporting.py`` DataFrame 分析      → ``generate_dataframe_report`` / ``_format_stat`` / ``_is_categorical``
  - ``utils/pipeline_reporting.py``            → ``generate_pipeline_summary``

公开 API 表面 (历史 ``utils/*.py`` shim 已转发):
``save_dataset``、``safe_save_preview_csv``、``generate_dataframe_report``、
``_format_stat``、``_is_categorical``、``generate_pipeline_summary``。
"""

from __future__ import annotations

import logging
import os

import pandas as pd
import pyarrow.parquet as pq

# ============================================================================
# 1. 数据集持久化 (Parquet + CSV 预览)。来源于 utils/helpers.py。
# ============================================================================


def safe_save_preview_csv(df: pd.DataFrame, preview_path: str, logger=None):
    """保存前 5,000 行为 CSV 预览, 静默吞掉 PermissionError。

    CSV 预览是非关键路径: 写入失败 (典型情形是 Excel 已打开占用) 不应该
    中断主流水线。本函数记录 warning 并继续执行。
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


def save_dataset(
    df: pd.DataFrame,
    output_path: str,
    logger=None,
    stage_name: str = None,
    config: dict = None,
    input_files: list = None,
):
    """将 ``df`` 同时持久化为 Parquet + CSV 预览, 两者共享 ``output_path`` 词干。

    ``.parquet`` 是契约格式, 失败会抛异常; 同词干的 ``.csv`` 是非关键预览,
    写入失败不会抛异常。

    Args:
        df: 要保存的 DataFrame
        output_path: 输出文件路径
        logger: 日志记录器
        stage_name: 阶段名称（可选，用于数据版本控制）
        config: 配置字典（可选，用于数据版本控制）
        input_files: 依赖的输入文件列表（可选，用于数据版本控制）
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        # 如果提供了版本控制参数，使用save_parquet_with_metadata
        if stage_name and config is not None:
            from news_process.core.data_versioning import save_parquet_with_metadata
            save_parquet_with_metadata(
                df=df,
                output_path=output_path,
                stage_name=stage_name,
                config=config,
                input_files=input_files,
            )
        else:
            # 向后兼容：没有版本控制参数时使用原始方法
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
# 2. DataFrame 分析报告。逐字搬运自 utils/reporting.py。
# ============================================================================


def _format_stat(value, precision=2):
    """格式化数值用于日志输出; NaN 返回 ``"N/A"``。"""
    if pd.isna(value):
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{value:.{precision}f}"
    return str(value)


def _is_categorical(dtype):
    """pandas >= 2.1 兼容的 categorical-dtype 检测。"""
    return isinstance(dtype, pd.CategoricalDtype)


def generate_dataframe_report(df: pd.DataFrame, logger: logging.Logger):
    """向 ``logger`` 输出 ``df`` 的详细统计报告。

    报告分两节:
      1. 整体概览: shape、重复行数、内存占用、dtype 分布。
      2. 逐列分析: 缺失率、唯一值数、类型自适应统计
         (数值五数概括 / datetime 范围 / 布尔值计数 /
         categorical-or-object 值分布)。

    防御性设计: 任何内部失败均以 WARNING 级别打印, 不抛异常 — 保证
    报告生成不会破坏宿主流水线。
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

            elif pd.api.types.is_numeric_dtype(dtype):
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
# 3. 流水线收尾的数据流转摘要。来源于 utils/pipeline_reporting.py。
# ============================================================================


def generate_pipeline_summary(config, logger):
    """打印一次完整运行结束后的流水线摘要报告。

    报告分两个粒度:
      1. 文章级数据流转 (00 -> 24): 每阶段的行数、与上一阶段的差值、
         相对最初阶段的保留率。
      2. Bank-Year 面板摘要 (45 / 51): 行数 x 列数。

    使用 ``pyarrow.parquet.read_metadata`` 进行廉价行计数 (只读 parquet
    footer, 不全量加载); 然后对最终阶段全量加载, 调用
    ``generate_dataframe_report`` 输出完整统计。
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

            # plan m3: initial_count == 0 时分母为零, 旧实现强行返回 0.0%,
            # 容易被运维误读为"全丢光"; 现改为显式 "N/A" 字符串
            if stage_name == "模块一: 00_preprocessing":
                change = 0
                pct_change_str = "+0.00%"
                initial_count = current_count
                if initial_count > 0:
                    retention_str = "100.00%"
                else:
                    retention_str = "N/A"
            else:
                change = current_count - previous_count
                if previous_count > 0:
                    pct_change_str = f"{change / previous_count * 100:+.2f}%"
                else:
                    pct_change_str = "N/A"
                if initial_count > 0:
                    retention_str = f"{current_count / initial_count * 100:.2f}%"
                else:
                    retention_str = "N/A"

            summary_data.append({
                "Stage": stage_name,
                "Rows": current_count,
                "Change": change,
                "Change (%)": pct_change_str,
                "Retention (vs Initial)": retention_str,
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
