"""news_process.pipeline.audit.stats_excel — Stage 53 (audit/export stats Excel).

Migrated from legacy ``news_process/53_export_stats_excel.py`` during
Phase 1.4b as the **pilot** body relocation.  Functional behavior preserved
verbatim; only the location changed and the legacy ``utils.helpers`` import
now resolves through the Phase 1 forward-shim chain.

Phase 1 status: this is the canonical body.  The root file
``news_process/53_export_stats_excel.py`` is a thin shim that calls
``main()`` here.

Phase 2 will: (a) move the remaining 23 simple CLI bodies here, (b) refactor
``__file__``-dependent resource paths in 22/23/35/38b/39 to read from
``CONFIG['paths'][...]`` (with new keys ``models_dir`` / ``eval_reports_dir``
added to ``paths.yaml``), and (c) atomically migrate 15/45/library files.
"""

from __future__ import annotations

import os
import sys

import pandas as pd

from news_process.core.config import load_config


def main():
    """Build the Excel of media / region / city distribution per stage."""
    # Windows console GBK fallback (preserve legacy behavior).
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

                sheet_name = f"{label}_{sheet_suffix}"[:31]  # Excel sheet name limit

                vc = df[col_name].fillna('(空值)').value_counts().reset_index()
                vc.columns = [col_name, '数量']
                vc.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"  [OK] Sheet '{sheet_name}': {len(vc)} 个不同值")

    print(f"\n已生成 Excel: {output_excel}")


if __name__ == '__main__':
    main()
