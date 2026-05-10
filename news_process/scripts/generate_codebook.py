#!/usr/bin/env python3
"""
generate_codebook.py - 生成完整的变量代码手册（Variable Codebook）

用法:
    python scripts/generate_codebook.py

输出:
    - data/processed/variable_codebook.xlsx
    - data/processed/variable_codebook.csv
    - data/processed/variable_codebook.md
    - data/processed/variable_codebook.json
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 sys.path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 添加父目录到 sys.path（用于导入 news_process）
parent_dir = project_root.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import pandas as pd
import logging
from news_process.core.config import load_config
from news_process.pipeline.panel.codebook import generate_codebook

# 初始化配置和日志
CONFIG = load_config()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    logger.info("=" * 70)
    logger.info("变量代码手册（Variable Codebook）生成工具")
    logger.info("=" * 70)

    # 读取面板数据
    panel_path = os.path.join(
        CONFIG['paths']['output_dir'],
        CONFIG['filenames'].get('output_40_panel_yearly', '40_panel_yearly.parquet')
    )

    if not os.path.exists(panel_path):
        logger.error(f"面板数据文件不存在: {panel_path}")
        logger.error("请先运行数据处理流程生成面板数据")
        return 1

    logger.info(f"读取面板数据: {panel_path}")
    panel = pd.read_parquet(panel_path)
    logger.info(f"  面板维度: {len(panel)} 行 × {len(panel.columns)} 列")

    # 生成代码手册
    output_dir = CONFIG['paths']['output_dir']
    output_files = generate_codebook(
        panel=panel,
        output_dir=output_dir,
        formats=['excel', 'csv', 'markdown', 'json']
    )

    # 输出结果
    logger.info("\n" + "=" * 70)
    logger.info("变量代码手册生成完成！")
    logger.info("=" * 70)
    for format_name, file_path in output_files.items():
        logger.info(f"  {format_name.upper()}: {file_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
