"""migrate_data_layout.py — Phase 2e 数据目录迁移辅助脚本 (已推迟; Phase 8 后部分目标已作废)。

Phase 8 状态 (2026-05-04)
---------------------------
已交付的 Phase 8 执行了**单层**目录重命名 ``data_processed/`` → ``data/processed/``,
**未**实施原方案中的按业务组再分子目录 (``00_preprocess/``、``10_filter/`` 等)。
理由: 跨阶段 parquet 读取 (例如阶段 21 读阶段 14 输出、阶段 24 读阶段 23 输出)
会迫使 ``CONFIG['filenames']`` 携带组前缀, 反而**提高**耦合、违背 DRY。
``data/processed/`` 下保持扁平布局, 继续沿用 ``NN_xxx.parquet`` 数字前缀编码业务组,
无路径重复。

本脚本保留为**档案级 / 可选**工具: 若未来确有存储分层或按组冷归档等需求,
可显式启用更深目录结构; 调用时目标路径位于 ``data/processed/<group>/``。

原始设计意图 (Phase 2e 蓝图)
----------------------------
由扁平 ``news_process/data_processed/`` 迁至按阶段组分目录::

    data/processed/00_preprocess/    # 00 产出
    data/processed/10_filter/        # 11/12/14/15 产出
    data/processed/20_sentiment/     # 21/22/23/24 产出
    data/processed/30_features/      # 25/26/27/30 产出
    data/processed/40_panel/         # 41–48 与 45 产出
    data/processed/50_falsification/ # 51 产出
    data/processed/validation/       # 31–39 产出
    data/processed/reports/          # eval_reports/

本仓库提交中的 Phase 2e 刻意**非破坏性**: 脚本为未来执行预留, 默认不调用。
推迟原因摘要:

1. ``tests/fixtures/golden_panel_v0.json`` 曾按 ``data_processed/<file>.parquet`` 建基线;
   若移动 parquet 而不同步更新快照, 将破坏 Phase 2g 可复现性测试。
2. 现有 ``stata/*.do`` 中部分路径 (如 ``output/40_panel_data.dta``) 本身已陈旧;
   完整迁移需协调重快照、改写 .do 与 Stata 用户通知。
3. 编排侧 ``OUTPUT_REGISTRY`` (Phase 2d) 当前仅登记**文件名**; 待其与目录前缀
   协同扩展后, 本辅助脚本可在一轮原子 ``mv`` 中完成磁盘搬迁。

在解冻 Phase 2e 之前, 运行时语义以 Phase 8 为准: 各阶段读写的根目录为
``CONFIG['paths']['output_dir']`` 所解析的 ``data/processed/`` 扁平布局。

调用示例 (解冻后):
    python news_process/scripts/migrate/migrate_data_layout.py [--apply]
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

# 阶段文件名 → ``data/processed/`` 下目标子目录名。
TARGET_LAYOUT = {
    "00_preprocessing.parquet":          "00_preprocess",
    "11_bank_news.parquet":              "10_filter",
    "12_fintech_news.parquet":           "10_filter",
    "12_fintech_news_full.parquet":      "10_filter",
    "15_fintech_intensity.parquet":      "10_filter",
    "16_article_alignment.parquet":      "10_filter",
    "21_tone_llms.parquet":              "20_sentiment",
    "21_tone_llms_full.parquet":         "20_sentiment",
    "22_words_tone.parquet":             "20_sentiment",
    "23_bert_tone.parquet":              "20_sentiment",
    "24_herd_decay.parquet":             "20_sentiment",
    "27_benefit_embeddings_anchors.npy": "30_features",
    "27_benefit_embeddings_ctx.npy":     "30_features",
    "27_benefit_embeddings_full.npy":    "30_features",
    "40_panel_yearly.parquet":           "40_panel",
    "40_panel_yearly.dta":               "40_panel",
    "40_article_bank_level.parquet":     "40_panel",
    "40_attn_index_year.parquet":        "40_panel",
    "40_attn_index_province_year.parquet": "40_panel",
    "40_attn_index_city_year.parquet":   "40_panel",
    "41_panel_with_controls.parquet":    "40_panel",
    "41_panel_with_controls.dta":        "40_panel",
    "51_panel_with_controls.parquet":    "50_falsification",
    "51_panel_with_controls.dta":        "50_falsification",
}


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def plan_moves() -> list[tuple[Path, Path]]:
    """返回拟执行的 (源路径, 目标路径) 列表。

    Phase 8 更新: 源根已由 ``data_processed/`` 迁至 ``data/processed/`` (单层重命名)。
    本辅助脚本若被调用, 将在该单层之下再细分至 ``data/processed/<group>/``。
    """
    root = _project_root()
    # Phase 8 (2026-05-04): 源目录已由 data_processed/ 迁至 data/processed/
    src_dir = root / "data" / "processed"
    dst_root = root / "data" / "processed"
    moves: list[tuple[Path, Path]] = []
    for fname, sub in TARGET_LAYOUT.items():
        src = src_dir / fname
        if src.exists():
            dst = dst_root / sub / fname
            moves.append((src, dst))
    return moves


def main():
    parser = argparse.ArgumentParser(
        description="Phase 2e 数据目录迁移 (默认仅 dry-run 打印计划)"
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="实际移动文件 (默认仅打印迁移计划)。",
    )
    args = parser.parse_args()

    moves = plan_moves()
    if not moves:
        print("无可移动文件 (data/processed/ 为空或目录结构已符合计划)。")
        return 0

    print(f"Phase 2e 计划: 共 {len(moves)} 次移动")
    for src, dst in moves:
        print(f"  {src.name:<42s} -> data/processed/{dst.parent.name}/")

    if not args.apply:
        print("\n(dry-run) 若确认无误, 请加 --apply 执行实际移动。")
        print("警告: 执行后请重生成 tests/fixtures/golden_panel_v0.json,")
        print("      并审计 stata/*.do 内硬编码路径。")
        return 0

    print("\n正在执行移动...")
    for src, dst in moves:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        print(f"  moved: {src.name}")
    print(f"\n完成。共重定位 {len(moves)} 个文件。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
