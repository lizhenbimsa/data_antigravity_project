"""
data_quality.py — 数据质量监控工具
====================================

功能：
    提供数据质量监控函数，记录类型强制转换等操作的影响。

使用方法：
    from utils.data_quality import to_numeric_with_logging

    df['column'] = to_numeric_with_logging(df['column'], 'column_name', logger)
"""

import pandas as pd
import numpy as np


def to_numeric_with_logging(series: pd.Series, column_name: str, logger) -> pd.Series:
    """将Series转换为数值类型，并记录转换统计。

    Args:
        series: 待转换的Series
        column_name: 列名（用于日志）
        logger: 日志对象

    Returns:
        pd.Series: 转换后的Series
    """
    # 记录转换前的状态
    original_count = len(series)
    original_non_null = series.notna().sum()

    # 执行转换
    converted = pd.to_numeric(series, errors='coerce')

    # 记录转换后的状态
    converted_non_null = converted.notna().sum()
    coerced_count = original_non_null - converted_non_null

    if coerced_count > 0:
        logger.warning(
            f"列 '{column_name}' 类型强制转换: "
            f"{coerced_count}/{original_count} 个值被转为NaN "
            f"({coerced_count/original_count*100:.2f}%)"
        )

        # 记录被强制转换的样本值（前5个）
        invalid_mask = series.notna() & converted.isna()
        if invalid_mask.any():
            invalid_samples = series[invalid_mask].head(5).tolist()
            logger.warning(f"  无效值样本: {invalid_samples}")
    else:
        logger.debug(f"列 '{column_name}' 类型转换: 全部成功")

    return converted


def validate_numeric_columns(df: pd.DataFrame, columns: list, logger) -> dict:
    """批量验证数值列的数据质量。

    Args:
        df: DataFrame
        columns: 待验证的列名列表
        logger: 日志对象

    Returns:
        dict: 验证结果统计
    """
    results = {}

    for col in columns:
        if col not in df.columns:
            logger.warning(f"列 '{col}' 不存在，跳过验证")
            continue

        series = df[col]
        total = len(series)
        non_null = series.notna().sum()
        null_count = total - non_null

        # 尝试转换为数值
        numeric = pd.to_numeric(series, errors='coerce')
        numeric_non_null = numeric.notna().sum()
        invalid_count = non_null - numeric_non_null

        results[col] = {
            'total': total,
            'null': null_count,
            'invalid': invalid_count,
            'valid': numeric_non_null,
            'null_pct': null_count / total * 100 if total > 0 else 0,
            'invalid_pct': invalid_count / total * 100 if total > 0 else 0,
        }

        if invalid_count > 0:
            logger.warning(
                f"列 '{col}' 数据质量: "
                f"有效={numeric_non_null}, 无效={invalid_count}, "
                f"缺失={null_count} (无效率={invalid_count/total*100:.2f}%)"
            )

    return results
