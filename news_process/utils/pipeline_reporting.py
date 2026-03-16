"""
utils/pipeline_reporting.py
============================
管道执行摘要报告生成器。

在整个流水线运行完成后，读取各阶段的 Parquet 输出文件，
生成包含数据量流转统计和最终数据详细分析的综合报告。

使用 ``pyarrow.parquet.read_metadata()`` 高效获取行数，
避免将整个文件加载到内存。
"""

import os
import pandas as pd
import pyarrow.parquet as pq
from utils.reporting import generate_dataframe_report


def generate_pipeline_summary(config, logger):
    """生成管道执行摘要报告，包括各阶段数据量变化和最终数据详细统计。

    通过读取各阶段输出 Parquet 文件的元数据来获取行数，
    仅在生成最终详细报告时才完整加载最后一个阶段的数据。

    Args:
        config: 已解析的配置字典（由 ``load_config()`` 返回）。
        logger: 用于输出报告的 ``logging.Logger`` 实例。
    """
    logger.info("\n" + "=" * 70)
    logger.info("===          数据管道执行摘要报告 (Pipeline Summary)         ===")
    logger.info("=" * 70)

    # 定义阶段和对应的输出文件名键名（按管道执行顺序排列）
    stages = [
        ("模块一: 00_preprocessing", "output_00_preprocessing"),
        ("模块二: 11_news_bank", "output_11_bank_news"),
        ("模块二: 12_news_fintech", "output_12_fintech_news"),
        ("模块三: 21_tone_llms", "output_21_tone_llms"),
        ("模块三: 22_tone_words", "output_22_words_tone"),
        ("模块三: 23_tone_berts", "output_23_bert_tone"),
    ]

    summary_data = []
    previous_count = 0
    initial_count = 0

    output_dir = config['paths']['output_dir']

    for stage_name, filename_key in stages:
        filename = config['filenames'].get(filename_key)
        if not filename:
            logger.warning(
                f"阶段 {stage_name} 的输出文件名未在配置中找到 (key: {filename_key})。"
            )
            continue

        file_path = os.path.join(output_dir, filename)

        try:
            current_count = 0
            if os.path.exists(file_path):
                # 使用 pyarrow 读取 Parquet 元数据获取行数，无需加载任何数据
                # 这比 pd.read_parquet(columns=[]) 更高效
                metadata = pq.read_metadata(file_path)
                current_count = metadata.num_rows
            else:
                logger.warning(f"文件未找到: {file_path}")

            # 计算各阶段数据量变化
            if stage_name == "模块一: 00_preprocessing":
                change = 0
                pct_change = 0.0
                initial_count = current_count
                retention_rate = 100.0
            else:
                change = current_count - previous_count
                pct_change = (change / previous_count * 100) if previous_count > 0 else 0.0
                retention_rate = (current_count / initial_count * 100) if initial_count > 0 else 0.0

            summary_data.append({
                "Stage": stage_name,
                "Rows": current_count,
                "Change": change,
                "Change (%)": f"{pct_change:+.2f}%",
                "Retention (vs Initial)": f"{retention_rate:.2f}%"
            })

            previous_count = current_count

        except Exception as e:
            logger.error(f"无法读取阶段 {stage_name} 的输出文件: {e}")
            summary_data.append({
                "Stage": stage_name,
                "Rows": "Error",
                "Change": "N/A",
                "Change (%)": "N/A",
                "Retention (vs Initial)": "N/A"
            })

    # 打印摘要表格
    summary_df = pd.DataFrame(summary_data)
    logger.info("\n数据流转统计 (Data Flow Summary):")
    logger.info("\n" + summary_df.to_string(index=False))

    # --- 最终数据详细统计 ---
    # 查找最后一个实际存在的阶段输出
    final_stage_key = stages[-1][1]
    final_filename = config['filenames'].get(final_stage_key)
    if final_filename:
        final_file_path = os.path.join(output_dir, final_filename)
        if os.path.exists(final_file_path):
            logger.info(f"\n正在生成最终数据 ({final_filename}) 的详细统计报告...")
            try:
                final_df = pd.read_parquet(final_file_path)
                generate_dataframe_report(final_df, logger)
            except Exception as e:
                logger.error(f"生成最终详细报告失败: {e}")
        else:
            logger.warning(f"最终输出文件不存在，无法生成详细统计: {final_file_path}")
