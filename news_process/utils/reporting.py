"""
utils/reporting.py
==================
DataFrame 统计报告生成器。

为给定的 Pandas DataFrame 生成包含以下内容的详细异构分析报告:
  - 整体维度、内存占用、重复行、数据类型分布
  - 逐列分析: 缺失值、唯一值、数值统计 / 日期范围 / 布尔分布 / 类别频次

主要用于管道结束后的数据质量审查, 由 pipeline_reporting.py 调用。

设计原则:
  - 非关键路径: 报告生成失败不会中断流水线执行
  - 自适应分析: 根据列的 dtype 自动选择合适的统计方法
  - 智能显示: 低基数列(≤ 15)显示完整分布, 高基数列仅显示 Top 5
"""

import logging
import warnings

import numpy as np
import pandas as pd


def _format_stat(value, precision=2):
    """格式化统计数值，优雅地处理 NaN 值。

    Args:
        value:     待格式化的值。
        precision: 浮点数保留的小数位数（默认 2）。

    Returns:
        str: 格式化后的字符串（NaN 返回 ``"N/A"``）。
    """
    if pd.isna(value):
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{value:.{precision}f}"
    return str(value)


def generate_dataframe_report(df: pd.DataFrame, logger: logging.Logger):
    """为 DataFrame 生成详细的统计报告并写入日志。

    报告包含：
      1. 整体概览：维度、重复行数、内存占用、数据类型分布
      2. 逐列分析：根据列的数据类型（数值/日期/布尔/类别/文本），
         输出对应的统计信息

    Args:
        df:     待分析的 DataFrame。
        logger: 用于输出报告的 ``logging.Logger`` 实例。
    """
    try:
        logger.info("\n" + "=" * 60)
        logger.info(" DataFrame 统计报告 (DataFrame Statistics Report)")
        logger.info("=" * 60)

        # 1. 空数据检查
        if df.empty:
            logger.warning("输入数据为空，无法生成详细统计报告。")
            logger.info("=" * 60 + "\n")
            return

        # 2. 整体概览
        total_rows = len(df)
        logger.info(f"数据维度 (Shape): {df.shape[0]:,} 行, {df.shape[1]} 列")

        # 重复行统计
        duplicate_rows = df.duplicated().sum()
        duplicate_percentage = (duplicate_rows / total_rows) * 100 if total_rows > 0 else 0
        logger.info(f"重复行数 (Duplicate Rows): {duplicate_rows:,} ({duplicate_percentage:.2f}%)")

        # 内存占用(自动选择合适单位)
        # deep=True: 计算 object 列中每个字符串的实际内存, 而非仅指针大小。
        # 对于包含大量中文新闻内容的 DataFrame, deep=True 的结果可能是
        # deep=False 的 5-10 倍。
        memory_usage_bytes = df.memory_usage(deep=True).sum()
        if memory_usage_bytes < 1024**2:
            memory_usage, unit = memory_usage_bytes / 1024, "KB"
        elif memory_usage_bytes < 1024**3:
            memory_usage, unit = memory_usage_bytes / (1024**2), "MB"
        else:
            memory_usage, unit = memory_usage_bytes / (1024**3), "GB"
        logger.info(f"内存占用 (Memory Usage): {memory_usage:.2f} {unit}")

        # 数据类型概览
        logger.info("数据类型概览 (Data Types Summary):")
        dtype_counts_str = df.dtypes.value_counts().to_string()
        indented = "\n".join([f"    {line}" for line in dtype_counts_str.split('\n')])
        logger.info(indented)

        # 3. 逐列分析
        logger.info("\n" + "-" * 60)
        logger.info(" 字段逐一分析报告 (Column Analysis Report)")
        logger.info("-" * 60)

        for column in df.columns:
            col_series = df[column]
            dtype = col_series.dtype

            logger.info(f"\n--- 字段 (Column): '{column}' ---")
            logger.info(f"    - 数据类型 (Dtype): {dtype}")

            # 缺失值统计
            missing_count = col_series.isnull().sum()
            if total_rows > 0:
                missing_pct = (missing_count / total_rows) * 100
                logger.info(f"    - 缺失值 (Missing Values): {missing_count:,} ({missing_pct:.2f}%)")
            else:
                logger.info(f"    - 缺失值 (Missing Values): {missing_count:,} (N/A%)")

            unique_count = col_series.nunique()
            logger.info(f"    - 唯一值数量 (Unique Values): {unique_count:,}")

            # 根据数据类型执行不同的统计分析:
            #   数值型 -> 五数概括(min, 25%, 50%, 75%, max) + 均值/标准差
            #   日期型 -> 最早/最晚时间 + 时间跨度
            #   布尔型 -> True/False 分布
            #   文本/类别型 -> 值频次分布(低基数完整显示, 高基数 Top 5)
            if col_series.isnull().all():
                logger.info("    - 该字段所有值均为空。")

            elif np.issubdtype(dtype, np.number):
                # 数值型：均值、标准差、五数概括
                stats = col_series.describe()
                logger.info("    - 数值统计 (Numeric Stats):")
                logger.info(f"      - 均值 (mean): {_format_stat(stats.get('mean'))}")
                logger.info(f"      - 标准差 (std): {_format_stat(stats.get('std'))}")
                logger.info(f"      - 最小值 (min): {_format_stat(stats.get('min'))}")
                logger.info(f"      - 25% 分位数: {_format_stat(stats.get('25%'))}")
                logger.info(f"      - 中位数 (50%): {_format_stat(stats.get('50%'))}")
                logger.info(f"      - 75% 分位数: {_format_stat(stats.get('75%'))}")
                logger.info(f"      - 最大值 (max): {_format_stat(stats.get('max'))}")

            elif pd.api.types.is_datetime64_any_dtype(dtype):
                # 日期型：最早/最晚时间和跨度
                logger.info("    - 日期时间统计 (Datetime Stats):")
                min_date, max_date = col_series.min(), col_series.max()
                logger.info(f"      - 最早时间 (Earliest): {min_date}")
                logger.info(f"      - 最晚时间 (Latest):   {max_date}")
                if pd.notna(min_date) and pd.notna(max_date):
                    logger.info(f"      - 时间跨度 (Duration):  {max_date - min_date}")

            elif pd.api.types.is_bool_dtype(dtype):
                # 布尔型：True/False 分布
                logger.info("    - 布尔值分布 (Boolean Value Counts):")
                logger.info(f"\n{col_series.value_counts(dropna=False).to_string()}")

            elif pd.api.types.is_object_dtype(dtype) or _is_categorical(dtype):
                # 类别/文本型：低基数显示完整分布，高基数显示 Top 5
                if unique_count <= 15:
                    logger.info("    - 值分布 (Value Counts):")
                    logger.info(f"\n{col_series.value_counts(dropna=False).to_string()}")
                else:
                    logger.info("    - 最常见的5个值 (Top 5 Most Common Values):")
                    logger.info(f"\n{col_series.value_counts().head(5).to_string()}")

        logger.info("\n" + "=" * 60)
        logger.info(" 报告结束 (End of Report)")
        logger.info("=" * 60 + "\n")

    except Exception as e:
        # 报告生成是非关键路径, 异常不应阻断管道执行。
        # 设计决策: 使用 warning 而非 error, 因为报告失败不影响数据处理结果。
        # exc_info=True: 记录完整堆栈以便事后排查。
        logger.warning(f"生成统计报告时发生错误（不影响数据处理）: {e}", exc_info=True)


def _is_categorical(dtype):
    """安全检测列是否为分类类型(兼容 pandas >= 2.1 的 API 变更)。

    pandas >= 2.1 废弃了 ``pd.api.types.is_categorical_dtype()``,
    这里改用 isinstance 检查以避免 DeprecationWarning。

    Args:
        dtype: pandas 列的 dtype。

    Returns:
        bool: 是否为 CategoricalDtype。
    """
    return isinstance(dtype, pd.CategoricalDtype)