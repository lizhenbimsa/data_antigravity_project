"""news_process.pipeline.audit.stats_excel — 阶段 53: 审计用统计表 Excel 导出。

由历史 ``news_process/53_export_stats_excel.py`` 在 Phase 1.4b **试点**
正文迁移而来。功能行为逐字保留; 仅变更物理路径, 且原 ``utils.helpers``
导入经 Phase 1 转发链解析至 ``news_process.core.*``。

Phase 1 状态: 此处为规范实现体。根目录 ``news_process/53_export_stats_excel.py``
为极薄 CLI 适配层, 仅转调本模块 ``main()``。

Phase 2 规划: (a) 将其余 23 个简易 CLI 正文迁入子包; (b) 将 22/23/35/38b/39
中依赖 ``__file__`` 的资源路径改为 ``CONFIG['paths'][...]`` (并在 ``paths.yaml``
增补 ``models_dir`` / ``eval_reports_dir`` 等键); (c) 原子迁移 15/45/库文件路径。

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 53_export_stats_excel.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**输入**: 按 4 个阶段读对应 parquet 的 3 个元数据列 (columns 限定读, 省内存) — 00_preprocessing / 11_bank_news / 12_fintech_news / 21_tone_llms (文件名经 config['filenames'] 的 output_00_preprocessing / output_11_bank_news / output_12_fintech_news / output_21_tone_llms 解析); 缺文件则 print 跳过该阶段。

**处理步骤 (main)**:
1. Windows 控制台 utf-8 重配 (失败静默 pass)。
2. 对每个阶段 × 每个统计字段 (媒体(中文) / 国家地区/省份 / 城市) 做 `df[col].fillna('(空值)').value_counts().reset_index()`, 列名命名为 [原字段名, 数量]; 字段列不存在则 print 警告跳过。
3. 经 openpyxl ExcelWriter 各写一个 sheet (sheet 名 `{label}_{中文后缀}` 截断 31 字符, Excel 上限), 输出单一 Excel `各阶段_媒体_地区_城市_统计.xlsx`。

**关键算法**: 纯 value_counts 频次分布, 无回归/聚合公式。

**外部依赖**: pandas + openpyxl; 无 LLM/Embedding/网络。无 timeout (不在 DAG)。确定性强。规范调用: `python -m news_process.pipeline.audit.stats_excel` 或 `python news_process/53_export_stats_excel.py`。

**DAG 位置**: 不在 DAG。是横切多阶段的描述性统计便利工具, 由用户手动触发, 与主链解耦。

■ 白话说明

**这一步是什么**: 这是个统计小帮手。它把流水线四个关键阶段 (原始预处理、银行新闻、金融科技新闻、LLM 打分后) 的新闻, 按哪家媒体发的、来自哪个省、哪个城市分别数一数各有多少条, 然后整理成一个多页的 Excel 表格, 每一页是一个阶段、一个维度的分布清单。打个比方: 就是把一大堆新闻按媒体/地区/城市分类点名, 做成一份花名册。

**为什么需要它**: 研究者想快速了解我的新闻数据都来自哪些媒体、覆盖哪些地区、各阶段筛选后样本怎么变化, 不用自己写代码, 跑一下就能拿到一份现成的 Excel 概览。论文的样本描述、数据来源说明、附录里的覆盖范围表常常要用到这些数字。

**做得好不好的影响**: 它不参与任何回归计算, 也不改面板数据, 纯粹是给人看的描述性统计。所以它好不好不会影响论文的核心结果, 但它能帮研究者快速发现样本是否偏向某几家媒体或某个地区 (代表性问题), 以及各阶段筛选掉了多少数据。属于了解自己数据家底的辅助工具, 想用就用、不用也不影响主流程。
========================================================================
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
        # 注 (2026-06-15): 读 stage 12b 邻近共现硬过滤【之前】的关键词金科阶段 (pre-12b);
        #   本审计逐阶段统计原始关键词口径, 非 12b 过滤后的分析宇宙 (后者经 13→21 链)。
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
