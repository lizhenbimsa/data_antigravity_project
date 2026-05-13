#!/usr/bin/env python3
"""
convert_parquet_to_stata.py - 将parquet面板数据转换为Stata dta格式

用法:
    python scripts/convert_parquet_to_stata.py

输入: data/processed/40_panel_yearly.parquet
输出: data/processed/40_panel_yearly.dta

作者: Claude Code
日期: 2026-05-10
"""

import os
import sys
from pathlib import Path

import pandas as pd


def convert_parquet_to_stata(
    input_path: str = "data/processed/40_panel_yearly.parquet",
    output_path: str = "data/processed/40_panel_yearly.dta",
    stata_version: int = 118,  # Stata 14/15/16
) -> None:
    """
    将parquet文件转换为Stata dta格式。

    Args:
        input_path: 输入parquet文件路径
        output_path: 输出dta文件路径
        stata_version: Stata版本号
            - 118: Stata 14/15/16 (推荐)
            - 117: Stata 13
            - 115: Stata 12
    """
    print("=" * 70)
    print("Parquet to Stata 转换工具")
    print("=" * 70)
    print()

    # 检查输入文件是否存在
    if not os.path.exists(input_path):
        print(f"错误: 输入文件不存在: {input_path}")
        sys.exit(1)

    print(f"输入文件: {input_path}")
    print(f"输出文件: {output_path}")
    print(f"Stata版本: {stata_version}")
    print()

    # 读取parquet文件
    print("正在读取parquet文件...")
    try:
        df = pd.read_parquet(input_path)
        print("[OK] 读取成功")
        print(f"  数据维度: {df.shape[0]:,} 行 × {df.shape[1]:,} 列")
        print()
    except Exception as e:
        print(f"[ERROR] 读取失败: {str(e)}")
        sys.exit(1)

    # 显示数据信息
    print("数据概览:")
    print(f"  列数: {len(df.columns)}")
    print(f"  行数: {len(df)}")
    print(f"  内存使用: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print()

    # 检查关键列
    key_cols = ['target_bank', 'year']
    missing_keys = [col for col in key_cols if col not in df.columns]
    if missing_keys:
        print(f"[WARNING] 缺失关键列: {missing_keys}")
    else:
        print(f"[OK] 关键列存在: {key_cols}")
        print(f"  唯一银行数: {df['target_bank'].nunique()}")
        print(f"  年份范围: {df['year'].min()} - {df['year'].max()}")
    print()

    # 数据类型处理
    print("正在处理数据类型...")

    # 将 nullable Int64 转换为 float64 (Stata不支持nullable integer)
    for col in df.columns:
        if df[col].dtype == 'Int64':
            df[col] = df[col].astype('float64')
            print(f"  转换 {col}: Int64 -> float64")

    # 将 object 类型的数值列转换为 float64
    for col in df.select_dtypes(include=['object']).columns:
        try:
            # 修复FutureWarning: 使用errors='coerce'替代errors='ignore'
            numeric_col = pd.to_numeric(df[col], errors='coerce')
            # 只有当转换成功（不全是NaN）时才替换
            if not numeric_col.isna().all():
                df[col] = numeric_col
        except:
            pass

    print("[OK] 数据类型处理完成")
    print()

    # 检查变量名长度 (Stata限制为32字符)
    long_names = [col for col in df.columns if len(col) > 32]
    if long_names:
        print(f"[WARNING] {len(long_names)} 个变量名超过32字符:")
        for name in long_names[:5]:  # 只显示前5个
            print(f"  - {name} ({len(name)}字符)")
        if len(long_names) > 5:
            print(f"  ... 还有 {len(long_names) - 5} 个")
        print()
        print("[INFO] 建议: 在Stata中使用 rename 命令缩短变量名")
        print()

    # 转换为Stata格式
    print("正在转换为Stata格式...")
    try:
        # 创建输出目录（如果不存在）
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"  创建输出目录: {output_dir}")

        # 转换
        df.to_stata(
            output_path,
            write_index=False,
            version=stata_version,
            convert_dates=None,  # 保持原始格式
        )
        print("[OK] 转换成功")
        print()
    except Exception as e:
        print(f"[ERROR] 转换失败: {str(e)}")
        sys.exit(1)

    # 显示输出文件信息
    output_size = os.path.getsize(output_path) / 1024**2
    print("输出文件信息:")
    print(f"  文件路径: {output_path}")
    print(f"  文件大小: {output_size:.2f} MB")
    print()

    # 生成Stata加载命令
    print("=" * 70)
    print("转换完成!")
    print("=" * 70)
    print()
    print("在Stata中使用以下命令加载数据:")
    print()
    print(f'  use "{output_path}", clear')
    print()
    print("或者运行主控文件:")
    print()
    print('  do stata/99_master.do')
    print()


def main():
    """主函数"""
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # 切换到项目根目录
    os.chdir(project_root)

    # 执行转换
    convert_parquet_to_stata()


if __name__ == "__main__":
    main()
