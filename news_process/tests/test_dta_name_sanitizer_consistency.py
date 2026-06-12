"""S3 fix v2 (2026-05-30) 回归守卫 — .dta 列名 sanitizer 一致性.

S3 缺陷: 同一份 bank-year panel 在 40_panel_yearly.dta (stage 45, 经
papers/_common/tables.py::sanitize_stata_columns) 与 46_panel_yearly_full.dta
(stage 46, 经 stata_export.shorten→asciify) 中得到了**不同**的 Stata 变量名 —
两条路径的长度/缩写规则各自为政, 且 40 路径会把中文情感标签 (正面/负面)
剥成空词干 → pos/neg 被混叠成 _1/_2 冲突名.

修复: 让**所有** .dta 写出方 (40 经 export.py, 51 经 controls.py, 衍生 paper 经
export_dta, scripts/convert_parquet_to_stata.py) 统一走**唯一**规范 sanitizer
(stata_export.shorten_long_column_names → asciify_non_ascii_columns).

本测试锁定契约:
  1. sanitize_stata_columns 输出 == 规范 46 路径输出 (逐字节一致).
  2. 中文情感标签映射到**互异**的 ascii 词干 (正面→pos, 负面→neg); 零冲突.
  3. 对真实在盘 panel (若存在): 所有列名唯一、≤32 字符、合法 Stata 标识符,
     且两条路径完全一致.

既有测试 (test_papers_common.py::test_equivalence_with_pipeline_panel_export_
algorithm) 只查自洽性 (唯一性/长度), 不查跨路径等价 — 所以 125 个列名静默漂移
它也照样通过. 本文件补上这个缺口.

# 白话: 以前同一张面板表导出成两个 .dta 文件时, 同一列在两个文件里名字不一样,
# 中文"正面/负面"还会被砍成一样的名字互相顶撞。修复后全项目只用一套改名规则,
# 这个文件就是盯着"两条导出路径必须产出一模一样的列名"不许再裂开。
"""
from __future__ import annotations

import os

import pandas as pd
import pytest

from news_process.papers._common.tables import sanitize_stata_columns
from news_process.pipeline.panel.stata_export import (
    asciify_non_ascii_columns,
    shorten_long_column_names,
)

_SAMPLE = [
    'finbert_cn_正面_w_sum_full', 'finbert_cn_负面_w_sum_full',
    'finbert_cn_正面_hw_sum_ctx', 'finbert_cn_负面_hw_sum_ctx',
    'jiang_2021_idf_score_w_sum_full', 'jiang_2021_idf_score_w_sum_ctx',
    'jiang_2021_idf_score_w_sum_title',
    'llm_vote_tone_full', 'mean_clarity_score_ctx', 'target_bank', 'year',
    'media_(中文)_breadth', '', '___',  # 括号 + 空串 + 全下划线 三个边角 case
]


def _preprocess(columns):
    """复刻 40 路径独有、46 路径没有的预处理 (括号替换/空名兜底)."""
    out = []
    for i, raw in enumerate(columns):
        c = str(raw).replace('(', '_').replace(')', '_')
        c = c.replace('（', '_').replace('）', '_')
        if not c or not c.strip('_'):
            c = f'col_{i}'
        out.append(c)
    return out


def _canonical_46(columns):
    """规范的 stage-46 sanitizer: 先 shorten 再 asciify (stata_export 的顺序)."""
    df = pd.DataFrame(columns=_preprocess(columns))
    df, _ = shorten_long_column_names(df)
    df, _ = asciify_non_ascii_columns(df)
    return list(df.columns)


def test_tables_path_matches_canonical_46_path_on_sample():
    """40 路径 sanitize_stata_columns 必须与 46 路径输出逐位相等."""
    assert sanitize_stata_columns(_SAMPLE) == _canonical_46(_SAMPLE)


def test_pos_neg_labels_map_to_distinct_stems():
    """正面/负面 绝不可坍缩成同一个名字 (S3 数据损坏的核心)."""
    out = sanitize_stata_columns(_SAMPLE)
    assert len(set(out)) == len(out), f"collision in sanitized names: {out}"
    pos_full, neg_full = out[0], out[1]
    assert pos_full != neg_full
    assert 'pos' in pos_full and 'neg' in neg_full
    # full 与 ctx 轨后缀须保留 (不可被截成无法区分的词干)
    assert out[0] != out[2] and out[1] != out[3]


def test_all_names_valid_stata_identifiers():
    import re
    ident = re.compile(r'^[A-Za-z_][A-Za-z0-9_]{0,31}$')
    out = sanitize_stata_columns(_SAMPLE)
    for name in out:
        assert ident.match(name), f"invalid Stata identifier: {name!r}"


@pytest.mark.parametrize("parquet", ["40_panel_yearly.parquet"])
def test_real_panel_40_path_equals_46_path(parquet):
    """对真实在盘 panel: 40 路径 ≡ 46 路径, 所有列名唯一且 ≤32 字符."""
    path = os.path.join("news_process", "data", "processed", parquet)
    if not os.path.exists(path):
        pytest.skip(f"{parquet} not on disk")
    cols = list(pd.read_parquet(path).columns)
    out = sanitize_stata_columns(cols)
    assert len(set(out)) == len(out), "collisions on real panel columns"
    assert all(len(c) <= 32 for c in out), "name >32 chars on real panel"
    assert out == _canonical_46(cols), "40-path diverges from 46-path on real panel"
