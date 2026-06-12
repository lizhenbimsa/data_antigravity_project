"""news_process.pipeline.audit.stats_excel — 阶段 53: 审计用统计表 Excel 导出。

由历史 ``news_process/53_export_stats_excel.py`` 在 Phase 1.4b **试点**
正文迁移而来。功能行为逐字保留; 仅变更物理路径, 且原 ``utils.helpers``
导入经 Phase 1 转发链解析至 ``news_process.core.*``。

Phase 1 状态: 此处为规范实现体。根目录 ``news_process/53_export_stats_excel.py``
为极薄 CLI 适配层, 仅转调本模块 ``main()``。

Phase 2 规划: (a) 将其余 23 个简易 CLI 正文迁入子包; (b) 将 22/23/35/38b/39
中依赖 ``__file__`` 的资源路径改为 ``CONFIG['paths'][...]`` (并在 ``paths.yaml``
增补 ``models_dir`` / ``eval_reports_dir`` 等键); (c) 原子迁移 15/45/库文件路径。
"""

from __future__ import annotations

import os
import sys

import pandas as pd

from news_process.core.config import load_config


def main():
    """按阶段汇总媒体 / 省域 / 城市分布, 写入 Excel。"""
    # Windows 控制台 GBK 回退 (保持历史行为)。
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

    config = load_config()
    output_dir = config['paths']['output_dir']

    stages = [
        {'label': '00_preprocessing',
         'filename': config['filenames']['output_00_preprocessing']},
        {'label': '11_news_bank',
         'filename': config['filenames']['output_11_bank_news']},
        {'label': '12_news_fintech',
         'filename': config['filenames']['output_12_fintech_news']},
        {'label': '21_tone_llms',
         'filename': config['filenames']['output_21_tone_llms']},
    ]

    stat_fields = [
        ('媒体(中文)', '媒体'),
        ('国家地区/省份', '国家地区_省份'),
        ('城市', '城市'),
    ]

    output_excel = os.path.join(output_dir, '各阶段_媒体_地区_城市_统计.xlsx')
    print(f"输出文件: {output_excel}")

    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        for stage in stages:
            parquet_path = os.path.join(output_dir, stage['filename'])
            label = stage['label']

            if not os.path.exists(parquet_path):
                print(f"[跳过] {label}: 文件不存在 ({parquet_path})")
                continue

            print(f"[读取] {label}: {parquet_path}")
            cols_to_read = [f for f, _ in stat_fields]
            df = pd.read_parquet(parquet_path, columns=cols_to_read)
            print(f"  行数: {len(df):,}")

            for col_name, sheet_suffix in stat_fields:
                if col_name not in df.columns:
                    print(f"  [警告] 列 '{col_name}' 不存在于 {label}，跳过")
                    continue

                sheet_name = f"{label}_{sheet_suffix}"[:31]  # Excel sheet 名上限 31 字符

                vc = df[col_name].fillna('(空值)').value_counts().reset_index()
                vc.columns = [col_name, '数量']
                vc.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"  [OK] Sheet '{sheet_name}': {len(vc)} 个不同值")

    print(f"\n已生成 Excel: {output_excel}")


if __name__ == '__main__':
    main()
