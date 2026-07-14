"""test_wpr12_stratified_sampler.py — WP-R1.2 两阶段整群分层抽样器 gate 测试
================================================================================

覆盖 `PROMPT_ASSETS_AUDIT_EXECUTION_PLAN_2026-07-12.md` §10 WP-R1.2 与
§10 验收标准第 3 条 "新增 gate 常绿: 分层抽样确定性"（详见
`validation/prompt_sensitivity.py::stratified_two_stage_sample` 模块内
"WP-R1.2 两阶段整群分层抽样器" 段落）。

另起新文件而非追加进 `test_wpr11_full_gate_switch.py` 的理由: 后者严格限定在
S9 文本修复 + WP-R1.1 full-only 总判定切换这一窄主题（见其模块 docstring）；
WP-R1.2 分层抽样器是独立新工作项（新函数、新构念），与既有 gate 文件主题不
重叠。镜像既有先例 `test_wpr3_locus_split.py` 为 WP-R3 单开一个文件的做法，
按工作项切分文件比在无关主题文件里加类更清晰、也更利于未来单独维护/删改。

覆盖:
  (a) 确定性 —— 同一 (df, 参数, seed) 两次调用逐行相等 (DataFrame 与
      frame_meta 均逐字节一致)。
  (b) 分层覆盖 —— 合成 df (3 年 × 4 类型 × 每格 20 篇) 抽样后每个被选中格
      恰 per_cell 篇。
  (c) 缺格退化 —— 请求格数 > 可用格数时全取, frame_meta 如实披露
      cell_shortfall=True 且 n_cells_selected == n_cells_available。
  (d) 未知类型归 0 格 —— bank_type_map 未覆盖的银行归 bank_type_id=0,
      计数进 frame_meta['n_unknown_bank_type']。

全部合成数据, $0, fast, 不依赖盘上大数据/LLM API/bank_list.yaml 磁盘读取
(测试显式传 bank_type_map, 绕开磁盘 IO 依赖)。
"""
import os
import sys

import pandas as pd
import pytest

_PROJECT_PARENT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)


@pytest.fixture(scope='module')
def mod():
    from news_process.validation import prompt_sensitivity
    return prompt_sensitivity


# 合成分层宇宙: 3 年 × 4 类型, 每格恰 20 篇 = 240 行, target_bank 按类型分配
# 一个专属银行名 (不依赖 bank_list.yaml 磁盘内容, 用显式 bank_type_map 注入)。
_YEARS = [2017, 2018, 2019]
_TYPES = [1, 2, 3, 4]
_BANK_BY_TYPE = {1: '国有测试行', 2: '股份测试行', 3: '城商测试行', 4: '农商测试行'}
_ROWS_PER_CELL = 20


def _make_synthetic_df(extra_unknown_rows: int = 0) -> pd.DataFrame:
    rows = []
    rid = 0
    for yr in _YEARS:
        for bt in _TYPES:
            bank = _BANK_BY_TYPE[bt]
            for _ in range(_ROWS_PER_CELL):
                rows.append({'row_id': rid, 'year': yr, 'target_bank': bank, 'val': rid})
                rid += 1
    if extra_unknown_rows:
        # 归属一个 bank_type_map 未覆盖的银行名 -> 应落 bank_type_id=0
        for _ in range(extra_unknown_rows):
            rows.append({'row_id': rid, 'year': 2020, 'target_bank': '未知测试行', 'val': rid})
            rid += 1
    return pd.DataFrame(rows)


_BANK_TYPE_MAP = {v: k for k, v in _BANK_BY_TYPE.items()}


class TestDeterminism:
    """(a) 同一 (df, 参数, seed) 两次调用逐字节相等。"""

    def test_same_call_twice_yields_identical_result(self, mod):
        df = _make_synthetic_df()
        sampled1, meta1 = mod.stratified_two_stage_sample(
            df, n_cells=70, per_cell=5, seed=42, bank_type_map=_BANK_TYPE_MAP,
        )
        sampled2, meta2 = mod.stratified_two_stage_sample(
            df, n_cells=70, per_cell=5, seed=42, bank_type_map=_BANK_TYPE_MAP,
        )
        pd.testing.assert_frame_equal(sampled1, sampled2)
        assert meta1 == meta2

    def test_different_seed_can_change_result(self, mod):
        """反向对照: 换 seed 后 (格内 20>per_cell=5 触发真随机抽样) 结果应可
        能不同 —— 证明上面的相等不是巧合的"总是全取"退化案例。"""
        df = _make_synthetic_df()
        sampled_a, _ = mod.stratified_two_stage_sample(
            df, n_cells=70, per_cell=5, seed=42, bank_type_map=_BANK_TYPE_MAP,
        )
        sampled_b, _ = mod.stratified_two_stage_sample(
            df, n_cells=70, per_cell=5, seed=1234, bank_type_map=_BANK_TYPE_MAP,
        )
        # 两次选中的具体行集合不必然相同 (row_id 集合可能有差异)
        assert set(sampled_a['row_id']) != set(sampled_b['row_id']) or \
            len(sampled_a) == 0, "换种子后应有能力产生不同的行选取 (否则确定性实现退化为常量)"


class TestStratifiedCoverage:
    """(b) 分层覆盖: 每个被选中格恰 per_cell 篇 (格内可用数 20 > per_cell)。"""

    def test_each_selected_cell_has_exactly_per_cell_rows(self, mod):
        df = _make_synthetic_df()
        per_cell = 7
        sampled, meta = mod.stratified_two_stage_sample(
            df, n_cells=70, per_cell=per_cell, seed=42, bank_type_map=_BANK_TYPE_MAP,
        )
        # 12 格 (3 年 × 4 类型) 全部非空, 20 > per_cell=7 -> 每格恰抽 7 篇
        assert meta['n_cells_available'] == len(_YEARS) * len(_TYPES) == 12
        for cell in meta['cells']:
            assert cell['n_available'] == _ROWS_PER_CELL
            assert cell['n_sampled'] == per_cell
            assert cell['shortfall'] is False
        assert len(sampled) == meta['n_cells_selected'] * per_cell
        assert meta['n_sampled_total'] == len(sampled)

        # 交叉核验: 用 groupby 重新数一遍抽样结果, 确认每格确实恰好 per_cell 行
        counts = sampled.groupby(['year', 'target_bank']).size()
        assert (counts == per_cell).all()


class TestCellShortfallDegradation:
    """(c) 缺格退化: 请求格数 > 可用格数(12) 时全取, 如实披露。"""

    def test_n_cells_exceeds_available_takes_all_cells(self, mod):
        df = _make_synthetic_df()
        sampled, meta = mod.stratified_two_stage_sample(
            df, n_cells=100, per_cell=5, seed=42, bank_type_map=_BANK_TYPE_MAP,
        )
        assert meta['n_cells_available'] == 12
        assert meta['n_cells_selected'] == 12
        assert meta['cell_shortfall'] is True
        assert len(meta['cells']) == 12

    def test_per_cell_exceeds_available_rows_takes_all_rows(self, mod):
        """格内可用篇数 < per_cell 时格内也应全取, 且该格标 shortfall=True。"""
        df = _make_synthetic_df()
        sampled, meta = mod.stratified_two_stage_sample(
            df, n_cells=70, per_cell=999, seed=42, bank_type_map=_BANK_TYPE_MAP,
        )
        for cell in meta['cells']:
            assert cell['n_sampled'] == _ROWS_PER_CELL
            assert cell['shortfall'] is True
        assert meta['n_cells_with_row_shortfall'] == 12
        assert len(sampled) == 12 * _ROWS_PER_CELL


class TestUnknownBankTypeFallback:
    """(d) 未知类型归 0 格, 计数进 frame_meta['n_unknown_bank_type']。"""

    def test_unmapped_bank_falls_into_type_zero_and_is_disclosed(self, mod):
        df = _make_synthetic_df(extra_unknown_rows=6)
        sampled, meta = mod.stratified_two_stage_sample(
            df, n_cells=70, per_cell=5, seed=42, bank_type_map=_BANK_TYPE_MAP,
        )
        assert meta['n_unknown_bank_type'] == 6
        # 新增的 (2020, type=0) 格应计入非空格总数 (12 + 1 = 13)
        assert meta['n_cells_available'] == 13
        zero_type_cells = [c for c in meta['cells'] if c['bank_type_id'] == 0]
        assert len(zero_type_cells) == 1
        assert zero_type_cells[0]['year'] == 2020
        assert zero_type_cells[0]['n_available'] == 6


class TestInputValidationAndYearFallback:
    """边界: 缺列 fail-loud、'日期' 派生年份、n_cells/per_cell 非法值。"""

    def test_missing_target_bank_column_raises(self, mod):
        df = pd.DataFrame({'year': [2017, 2018]})
        with pytest.raises(ValueError, match='target_bank'):
            mod.stratified_two_stage_sample(df, bank_type_map=_BANK_TYPE_MAP)

    def test_missing_year_and_date_columns_raises(self, mod):
        df = pd.DataFrame({'target_bank': ['国有测试行', '股份测试行']})
        with pytest.raises(ValueError, match='日期'):
            mod.stratified_two_stage_sample(df, bank_type_map=_BANK_TYPE_MAP)

    def test_date_column_fallback_derives_year(self, mod):
        """无 'year' 列时应从 '日期' 派生 (镜像 encode.py 既有范式)。"""
        df = pd.DataFrame({
            '日期': pd.to_datetime(['2017-03-01', '2018-05-01', '2017-06-01']),
            'target_bank': ['国有测试行', '股份测试行', '国有测试行'],
        })
        sampled, meta = mod.stratified_two_stage_sample(
            df, n_cells=70, per_cell=5, seed=42, bank_type_map=_BANK_TYPE_MAP,
        )
        years_seen = {c['year'] for c in meta['cells']}
        assert years_seen == {2017, 2018}

    def test_non_positive_n_cells_or_per_cell_raises(self, mod):
        df = _make_synthetic_df()
        with pytest.raises(ValueError):
            mod.stratified_two_stage_sample(df, n_cells=0, bank_type_map=_BANK_TYPE_MAP)
        with pytest.raises(ValueError):
            mod.stratified_two_stage_sample(df, per_cell=0, bank_type_map=_BANK_TYPE_MAP)


class TestExportSamplingFrame:
    """`export_sampling_frame` sidecar CSV 写出 (生产窗口消费, 此处只测函数本身)。"""

    def test_export_writes_csv_with_cell_rows(self, mod, tmp_path):
        df = _make_synthetic_df()
        _, meta = mod.stratified_two_stage_sample(
            df, n_cells=70, per_cell=5, seed=42, bank_type_map=_BANK_TYPE_MAP,
        )
        out_path = os.path.join(str(tmp_path), 'nested', 'frame.csv')
        mod.export_sampling_frame(meta, out_path)
        assert os.path.exists(out_path)
        frame_df = pd.read_csv(out_path)
        assert len(frame_df) == len(meta['cells'])
        assert list(frame_df.columns) == ['year', 'bank_type_id', 'n_available', 'n_sampled', 'shortfall']


class TestDoesNotTouchRandomSample:
    """防误用: random_sample 既有函数字节级未被本工作项改动 (向后兼容闸)。"""

    def test_random_sample_still_uses_df_sample_random_state(self, mod):
        import inspect
        src = inspect.getsource(mod.random_sample)
        assert 'df.sample(n=n, random_state=seed)' in src, (
            "random_sample 实现被意外改动 —— WP-R1.2 要求不改动既有函数"
        )
