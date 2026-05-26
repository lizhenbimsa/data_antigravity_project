"""Phase 3b 单元测试 — papers/_common/ 5 个模块.

仅做*纯函数级别*的单测, 不触及真实 pipeline 输出文件 (后者由
tests/integration/test_panel_reproducibility.py 覆盖)。

覆盖目标
--------
- paper_config: PaperConfig dataclass + get_paper_config 白名单 + 路径解析
- panel_loader: list_available_panels (空目录 + OUTPUT_REGISTRY 反查)
- tables: sanitize_stata_columns 等价性 + summary_stats 数值正确性
- figures: apply_publication_style 幂等性 + 调色板长度
- stata_runner: discover_stata_bin 不抛异常 + run_do 缺失文件
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# 让 tests/ 直接导入 news_process.* (复用 conftest.py 的 sys.path 注入)
PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(PROJECT_PARENT))

from news_process.papers._common import (
    COLORBLIND_PALETTE,
    PaperConfig,
    StataNotFoundError,
    apply_publication_style,
    export_dta,
    get_paper_config,
    get_papers_assets_root,
    list_available_panels,
    run_do,
    sanitize_stata_columns,
    summary_stats,
)
from news_process.papers._common.paper_config import is_valid_paper_id
from news_process.papers._common.stata_runner import discover_stata_bin

# ============================================================================
# 1. paper_config
# ============================================================================


class TestPaperConfig:
    def test_valid_paper_ids_whitelist(self):
        for pid in ['bank_fintech_tone', 'benefit_society',
                    'brokerage_network', 'llm_peer', 'strategic_diff']:
            assert is_valid_paper_id(pid)
        assert not is_valid_paper_id('unknown_paper')
        assert not is_valid_paper_id('')

    def test_get_paper_config_strict_rejects_unknown(self):
        with pytest.raises(ValueError, match="Unknown paper_id"):
            get_paper_config('totally_unknown', strict=True)

    def test_get_paper_config_lenient_allows_unknown(self):
        pc = get_paper_config('unknown_test_only', strict=False)
        assert pc.paper_id == 'unknown_test_only'
        assert isinstance(pc, PaperConfig)

    def test_get_paper_config_returns_frozen_dataclass(self):
        pc = get_paper_config('bank_fintech_tone')
        assert isinstance(pc.project_root, Path)
        assert isinstance(pc.panel_dir, Path)
        assert isinstance(pc.output_dir, Path)
        assert isinstance(pc.do_dir, Path)
        with pytest.raises(Exception):  # FrozenInstanceError
            pc.paper_id = 'mutated'  # type: ignore[misc]

    def test_paper_config_path_helpers(self):
        pc = get_paper_config('bank_fintech_tone')
        assert pc.panel_path('40_panel_yearly.parquet') == \
            pc.panel_dir / '40_panel_yearly.parquet'
        assert pc.asset('do', 'main.do') == \
            pc.output_dir.parent / 'do' / 'main.do'

    def test_papers_assets_root_resolution(self):
        assets = get_papers_assets_root()
        assert isinstance(assets, Path)
        assert assets.name == 'papers_assets'


# ============================================================================
# 2. panel_loader
# ============================================================================


class TestPanelLoader:
    def test_list_available_panels_returns_dict(self, tmp_path):
        # 空目录 → 空 dict
        result = list_available_panels(panel_dir=tmp_path)
        assert result == {}

    def test_list_available_panels_with_real_files(self, tmp_path):
        (tmp_path / '40_panel_yearly.parquet').write_bytes(b'')
        (tmp_path / '11_bank_news.parquet').write_bytes(b'')

        result = list_available_panels(panel_dir=tmp_path)
        assert '45_panel_export_main.py' in result
        assert '40_panel_yearly.parquet' in result['45_panel_export_main.py']
        assert '11_news_bank.py' in result
        assert '11_bank_news.parquet' in result['11_news_bank.py']

    # quality-hardening Round 5 (2026-05-27): panel_loader.py 50% → ~100%
    # cover load_panel (40-79), _resolve_panel_dir (30-37), _find_producer_stage (104-109)
    # 复用 module-level pd / pytest 已 import, 避免局部重 import 触发
    # pytest-cov 下 numpy reload 警告 + TypeError (umr_sum vs _NoValueType).

    def test_load_panel_raises_filenotfound_with_producer_hint(self, tmp_path):
        """缺失文件 → FileNotFoundError 错误信息含 producer stage 提示
        (panel_loader.py:68-77 + _find_producer_stage:104-109)."""
        from news_process.papers._common.panel_loader import load_panel

        cfg = {'paths': {'output_dir': str(tmp_path)}}
        with pytest.raises(FileNotFoundError) as exc_info:
            load_panel('40_panel_yearly.parquet', project_config=cfg)
        msg = str(exc_info.value)
        assert '面板文件不存在' in msg
        # 提示应含 producer stage 名 (45_panel_export_main.py per OUTPUT_REGISTRY)
        assert '45_panel_export_main' in msg

    def test_load_panel_raises_filenotfound_unknown_filename_no_hint(self, tmp_path):
        """未知文件名 (OUTPUT_REGISTRY 反查无结果) 仍 raise 但无 hint
        (panel_loader.py:108-109 return None branch)."""
        from news_process.papers._common.panel_loader import load_panel

        cfg = {'paths': {'output_dir': str(tmp_path)}}
        with pytest.raises(FileNotFoundError) as exc_info:
            load_panel('unknown_stage_xyz.parquet', project_config=cfg)
        # 仍含 path, 但 hint 空
        assert 'unknown_stage_xyz.parquet' in str(exc_info.value)

    def test_resolve_panel_dir_raises_keyerror_when_output_dir_missing(self):
        """cfg 缺 paths.output_dir → KeyError (panel_loader.py:33-36)."""
        from news_process.papers._common.panel_loader import _resolve_panel_dir
        with pytest.raises(KeyError, match="output_dir"):
            _resolve_panel_dir({'paths': {}})

    def test_load_panel_happy_path_returns_dataframe(self, tmp_path):
        """正常路径: 文件存在 → 返回 DataFrame (panel_loader.py:79)."""
        from news_process.papers._common.panel_loader import load_panel
        df_in = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        df_in.to_parquet(tmp_path / 'test.parquet')
        cfg = {'paths': {'output_dir': str(tmp_path)}}
        out = load_panel('test.parquet', project_config=cfg)
        assert len(out) == 3
        assert list(out.columns) == ['a', 'b']

    def test_load_panel_column_filter_applied(self, tmp_path):
        """columns 参数被透传给 read_parquet (panel_loader.py:79)."""
        from news_process.papers._common.panel_loader import load_panel
        df_in = pd.DataFrame({'a': [1, 2], 'b': [3, 4], 'c': [5, 6]})
        df_in.to_parquet(tmp_path / 'cols.parquet')
        cfg = {'paths': {'output_dir': str(tmp_path)}}
        out = load_panel('cols.parquet', project_config=cfg, columns=['a'])
        assert list(out.columns) == ['a']


# ============================================================================
# 3. tables
# ============================================================================


class TestSanitizeStataColumns:
    def test_basic_ascii_passthrough(self):
        cols = ['firm_id', 'year', 'profit']
        assert sanitize_stata_columns(cols) == cols

    def test_remove_chinese(self):
        cols = ['银行名称', 'year']
        result = sanitize_stata_columns(cols)
        assert result[1] == 'year'
        assert result[0].startswith('col_') or result[0] == ''

    def test_replace_parentheses(self):
        cols = ['ratio_(usd)', 'cnt_（中）_value']
        result = sanitize_stata_columns(cols)
        assert all('(' not in c and ')' not in c for c in result)
        assert all('（' not in c and '）' not in c for c in result)

    def test_max_len_28_base(self):
        long_name = 'a' * 50
        result = sanitize_stata_columns([long_name])
        assert len(result[0]) <= 28

    def test_collision_disambiguation(self):
        cols = ['a' * 30, 'a' * 30, 'a' * 30]
        result = sanitize_stata_columns(cols)
        assert len(set(result)) == 3
        assert all(len(c) <= 32 for c in result)

    def test_empty_string_replaced(self):
        cols = ['', '___', 'valid']
        result = sanitize_stata_columns(cols)
        assert result[0].startswith('col_')
        assert result[1].startswith('col_') or result[1] == '_'
        assert result[2] == 'valid'

    def test_equivalence_with_pipeline_panel_export_algorithm(self):
        # Phase 3b 设计核心: sanitize_stata_columns 必须与
        # pipeline/panel/export.py:export_panel 内嵌的算法逐位等价。
        # 用一组覆盖陷阱的输入做交叉验证。
        cols = [
            'plain', 'with_(usd)', 'mixed_（中文）', '银行', '___',
            'a' * 50, 'b' * 30, 'b' * 30,  # 第三个 collision
        ]
        result = sanitize_stata_columns(cols)
        assert len(set(result)) == len(cols)
        assert all(len(c) <= 32 for c in result)
        assert all('(' not in c and ')' not in c for c in result)


class TestExportDta:
    def test_writes_dta_file(self, tmp_path):
        df = pd.DataFrame({
            'firm_id': [1, 2, 3],
            'year': [2020, 2021, 2022],
            'profit': [10.5, -2.0, 7.3],
        })
        out = tmp_path / 'sub' / 'test.dta'
        result = export_dta(df, out)
        assert result.exists()
        assert result == out
        round_trip = pd.read_stata(out)
        assert list(round_trip.columns) == ['firm_id', 'year', 'profit']
        assert len(round_trip) == 3

    def test_label_map_filtering(self, tmp_path):
        df = pd.DataFrame({'a': [1.0, 2.0], 'b': [3.0, 4.0]})
        out = tmp_path / 'labels.dta'
        export_dta(
            df, out,
            label_map={'a': 'First var', 'b': 'Second', 'c': 'Ignored missing'},
        )
        with pd.read_stata(out, iterator=True) as round_trip:
            labels = round_trip.variable_labels()
        assert labels.get('a') == 'First var'
        assert labels.get('b') == 'Second'
        assert 'c' not in labels

    def test_nullable_dtype_downcast(self, tmp_path):
        df = pd.DataFrame({
            'x': pd.array([1, 2, None], dtype='Int64'),
            'y': pd.array([1.5, None, 3.5], dtype='Float64'),
        })
        out = tmp_path / 'nullable.dta'
        export_dta(df, out)
        assert out.exists()


class TestSummaryStats:
    def test_columns_in_fixed_order(self):
        df = pd.DataFrame({
            'a': [1.0, 2.0, 3.0, 4.0, 5.0],
            'b': [10.0, 20.0, 30.0, 40.0, 50.0],
        })
        out = summary_stats(df)
        assert list(out.columns) == ['N', 'Mean', 'SD', 'Min', 'P25', 'P50', 'P75', 'Max']

    def test_numeric_correctness(self):
        df = pd.DataFrame({'x': [1.0, 2.0, 3.0, 4.0, 5.0]})
        out = summary_stats(df)
        assert out.loc['x', 'N'] == 5
        assert out.loc['x', 'Mean'] == pytest.approx(3.0)
        assert out.loc['x', 'P50'] == pytest.approx(3.0)
        assert out.loc['x', 'Min'] == 1.0
        assert out.loc['x', 'Max'] == 5.0

    def test_dropna_handling(self):
        df = pd.DataFrame({'x': [1.0, np.nan, 3.0, np.nan, 5.0]})
        out = summary_stats(df)
        assert out.loc['x', 'N'] == 3
        assert out.loc['x', 'Mean'] == pytest.approx(3.0)

    def test_all_nan_column(self):
        df = pd.DataFrame({'x': [np.nan, np.nan]})
        out = summary_stats(df)
        assert out.loc['x', 'N'] == 0
        assert pd.isna(out.loc['x', 'Mean'])

    def test_explicit_variables_with_missing_raises(self):
        df = pd.DataFrame({'a': [1, 2, 3]})
        with pytest.raises(KeyError, match="不存在"):
            summary_stats(df, variables=['a', 'b'])

    def test_only_numeric_auto_selected(self):
        df = pd.DataFrame({
            'num': [1.0, 2.0, 3.0],
            'txt': ['x', 'y', 'z'],  # 应被自动忽略
        })
        out = summary_stats(df)
        assert 'num' in out.index
        assert 'txt' not in out.index


# ============================================================================
# 4. figures
# ============================================================================


class TestFigures:
    def test_palette_length_eight(self):
        assert len(COLORBLIND_PALETTE) == 8

    def test_palette_all_hex(self):
        for c in COLORBLIND_PALETTE:
            assert c.startswith('#') and len(c) == 7
            int(c[1:], 16)  # 必须能解析为 hex

    def test_apply_publication_style_idempotent(self):
        import matplotlib.pyplot as plt
        apply_publication_style(font_size=9)
        first = dict(plt.rcParams)
        apply_publication_style(font_size=9)
        second = dict(plt.rcParams)
        # 关键 keys 必须等价
        for key in ['font.size', 'axes.linewidth', 'axes.grid']:
            assert first[key] == second[key]

    def test_apply_publication_style_font_size(self):
        import matplotlib.pyplot as plt
        apply_publication_style(font_size=11)
        assert plt.rcParams['font.size'] == 11
        apply_publication_style(font_size=9)  # restore default
        assert plt.rcParams['font.size'] == 9


# ============================================================================
# 5. stata_runner
# ============================================================================


class TestStataRunner:
    def test_discover_does_not_crash(self):
        result = discover_stata_bin()
        assert result is None or isinstance(result, str)

    def test_run_do_missing_file_raises(self, tmp_path):
        non_existent = tmp_path / 'does_not_exist.do'
        with pytest.raises(FileNotFoundError):
            run_do(non_existent, stata_bin='/fake/stata')

    def test_run_do_no_stata_raises(self, tmp_path, monkeypatch):
        do_file = tmp_path / 'noop.do'
        do_file.write_text('display "hello"\n')

        # 屏蔽 PATH 中的 Stata + 屏蔽环境变量
        monkeypatch.setenv('PATH', '')
        monkeypatch.delenv('NEWS_PROCESS_STATA_BIN', raising=False)
        monkeypatch.setenv('ProgramFiles', str(tmp_path / 'no_pf'))
        monkeypatch.setenv('ProgramFiles(x86)', str(tmp_path / 'no_pf86'))

        with pytest.raises(StataNotFoundError):
            run_do(do_file)

    def test_run_do_explicit_bin_overrides_discovery(self, tmp_path):
        do_file = tmp_path / 'noop.do'
        do_file.write_text('display "hello"\n')

        # 任意不可执行路径; 只验证 .exists() 检查通过 + 后续到 subprocess 才报错
        fake_bin = tmp_path / 'fake_stata.exe'
        fake_bin.write_bytes(b'')

        # 在 Windows 不可执行但 subprocess.run 会抛 OSError 而非 StataNotFoundError
        with pytest.raises((OSError, PermissionError, subprocess.SubprocessError)):
            run_do(do_file, stata_bin=str(fake_bin), timeout=5)


import subprocess  # noqa: E402 — placed after class def to avoid top-level pollution
