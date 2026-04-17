"""
export_stats_excel.py — 导出各阶段数据的"媒体/地区/城市"分布统计至 Excel
====================================================================

为 00_preprocessing / 11_news_bank / 12_news_fintech / 21_tone_llms
各生成 3 个 Sheet：
  1. 媒体(中文) 及其数量
  2. 国家地区/省份 及其数量
  3. 城市 及其数量
"""

import os
import sys
import pandas as pd
from utils.helpers import load_config

# 修复 Windows 控制台 GBK 编码问题
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

CONFIG = load_config()
OUTPUT_DIR = CONFIG['paths']['output_dir']

# 定义要统计的 4 个 Parquet 文件
STAGES = [
    {
        'label': '00_preprocessing',
        'filename': CONFIG['filenames']['output_00_preprocessing'],
    },
    {
        'label': '11_news_bank',
        'filename': CONFIG['filenames']['output_11_bank_news'],
    },
    {
        'label': '12_news_fintech',
        'filename': CONFIG['filenames']['output_12_fintech_news'],
    },
    {
        'label': '21_tone_llms',
        'filename': CONFIG['filenames']['output_21_tone_llms'],
    },
]

# 要统计的 3 个字段
STAT_FIELDS = [
    ('媒体(中文)', '媒体'),
    ('国家地区/省份', '国家地区_省份'),
    ('城市', '城市'),
]

def build_value_counts_df(series: pd.Series, col_label: str) -> pd.DataFrame:
    """对 Series 做 value_counts 并返回格式化的 DataFrame。"""
    vc = series.value_counts().reset_index()
    vc.columns = [col_label, '数量']
    return vc


def main():
    output_excel = os.path.join(OUTPUT_DIR, '各阶段_媒体_地区_城市_统计.xlsx')
    print(f"输出文件: {output_excel}")

    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        for stage in STAGES:
            parquet_path = os.path.join(OUTPUT_DIR, stage['filename'])
            label = stage['label']

            if not os.path.exists(parquet_path):
                print(f"[跳过] {label}: 文件不存在 ({parquet_path})")
                continue

            print(f"[读取] {label}: {parquet_path}")
            # 只读取需要的列，节省内存
            cols_to_read = [f for f, _ in STAT_FIELDS]
            df = pd.read_parquet(parquet_path, columns=cols_to_read)
            print(f"  行数: {len(df):,}")

            for col_name, sheet_suffix in STAT_FIELDS:
                if col_name not in df.columns:
                    print(f"  [警告] 列 '{col_name}' 不存在于 {label}，跳过")
                    continue

                sheet_name = f"{label}_{sheet_suffix}"
                # Excel Sheet 名称最长 31 字符
                sheet_name = sheet_name[:31]

                vc_df = build_value_counts_df(df[col_name].fillna('(空值)'), col_name)
                vc_df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"  [OK] Sheet '{sheet_name}': {len(vc_df)} 个不同值")

    print(f"\n已生成 Excel: {output_excel}")


if __name__ == '__main__':
    main()
