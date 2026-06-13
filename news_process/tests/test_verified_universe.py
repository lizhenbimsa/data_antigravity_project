"""单元测试: pipeline/panel/verified_universe.py::restrict_to_verified / parquet_has_columns。

不依赖盘上试跑产物 (合成 tmp parquet), 覆盖:
  - 正常门控: (docid,target_bank) inner-join 收敛, 剔除非 verified 行;
  - fail-open ①: 24_herd_decay 缺失 → 原样返回未门控 + warning;
  - fail-open ②: 输入帧缺键 (docid/target_bank) → 原样返回 + warning (合成帧路径);
  - 无行膨胀: verified 端 drop_duplicates → df 即便重复键也不放大;
  - parquet_has_columns schema 探测。
"""
from __future__ import annotations

import logging

import pandas as pd

from news_process.pipeline.panel.verified_universe import (
    parquet_has_columns,
    restrict_to_verified,
)

_FN = {'output_24_herd_decay': '24_herd_decay.parquet'}


def _write_herd(tmp_path, pairs):
    df = pd.DataFrame(pairs, columns=['docid', 'target_bank'])
    df.to_parquet(tmp_path / '24_herd_decay.parquet')
    return str(tmp_path)


def test_gate_drops_unverified_rows(tmp_path):
    out_dir = _write_herd(tmp_path, [(1, 'A'), (2, 'B')])
    df = pd.DataFrame({'docid': [1, 2, 3], 'target_bank': ['A', 'B', 'C'],
                       'x': [10, 20, 30]})
    gated = restrict_to_verified(df, out_dir, _FN, label='t')
    assert set(zip(gated['docid'], gated['target_bank'])) == {(1, 'A'), (2, 'B')}
    assert 30 not in gated['x'].values  # (3,'C') 非 verified → 剔除


def test_gate_is_per_docid_target_bank(tmp_path):
    # 同 docid 对 A 验证、对 B 拒绝 → 仅 (1,'A') 留, (1,'B') 剔 (docid 单键会误留)
    out_dir = _write_herd(tmp_path, [(1, 'A')])
    df = pd.DataFrame({'docid': [1, 1], 'target_bank': ['A', 'B'], 'x': [1, 2]})
    gated = restrict_to_verified(df, out_dir, _FN, label='t')
    assert list(zip(gated['docid'], gated['target_bank'])) == [(1, 'A')]


def test_no_row_inflation_on_duplicate_input_keys(tmp_path):
    # verified 端 drop_duplicates → df 重复键不放大 (每行至多匹配一条)
    out_dir = _write_herd(tmp_path, [(1, 'A'), (1, 'A')])  # verified 含重复, 会被 dedup
    df = pd.DataFrame({'docid': [1, 1], 'target_bank': ['A', 'A'], 'x': [1, 2]})
    gated = restrict_to_verified(df, out_dir, _FN, label='t')
    assert len(gated) == 2  # df 原 2 行保留, 不因 verified 重复键膨胀到 4


def test_failopen_missing_herd_file(tmp_path, caplog):
    # 24_herd_decay 缺失 → 原样返回未门控 + 响亮 warning
    df = pd.DataFrame({'docid': [1, 2], 'target_bank': ['A', 'B'], 'x': [1, 2]})
    with caplog.at_level(logging.WARNING):
        out = restrict_to_verified(df, str(tmp_path), _FN, label='miss')
    pd.testing.assert_frame_equal(out, df)
    assert 'VERIFIED 域门控跳过' in caplog.text


def test_failopen_missing_keys(tmp_path, caplog):
    # 输入帧缺 docid → 原样返回 (合成帧路径, 不触发 ArrowInvalid)
    _write_herd(tmp_path, [(1, 'A')])
    df = pd.DataFrame({'target_bank': ['A', 'B'], 'x': [1, 2]})  # 无 docid
    with caplog.at_level(logging.WARNING):
        out = restrict_to_verified(df, str(tmp_path), _FN, label='nokey')
    pd.testing.assert_frame_equal(out, df)
    assert '输入帧缺键' in caplog.text


def test_parquet_has_columns(tmp_path):
    p = tmp_path / 'f.parquet'
    pd.DataFrame({'a': [1], 'docid': [2]}).to_parquet(p)
    assert parquet_has_columns(str(p), ['docid']) is True
    assert parquet_has_columns(str(p), ['docid', 'a']) is True
    assert parquet_has_columns(str(p), ['nope']) is False
