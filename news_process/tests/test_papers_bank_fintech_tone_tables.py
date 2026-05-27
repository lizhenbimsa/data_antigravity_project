"""tests/test_papers_bank_fintech_tone_tables.py — Round 36 quality-hardening.

`bank_fintech_tone/tables.py` 此前仅 import smoke test (test_papers_bank_fintech_tone.py),
build_table1 / write_table1 两个 wrapper 未被任何测试覆盖 (per Round 34 cov report
该文件 81.82%, 11 stmts / 2 miss).

设计:
  - Mock `build_summary_table` / `write_summary_table` (位于 _common.tables);
    验证 wrapper 把 'bank_fintech_tone' + _TABLE1_VARIABLES + 可选 paper_config /
    filename / dta_filename 正确透传.
  - 同 P2/P3/P4 tables.py 测试 (Round 33) 的 pattern: 仅验 delegate 契约,
    不验 Stata 数学正确性 (后者需真实 panel).
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pandas as pd

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


def test_build_table1_delegates_with_paper_id_and_variables():
    """build_table1() 必须用 paper_id='bank_fintech_tone' + _TABLE1_VARIABLES 调 _common."""
    from news_process.papers.bank_fintech_tone import tables as t_mod

    fake_df = pd.DataFrame({'mean': [0.1, 0.2]}, index=['a', 'b'])
    with patch.object(t_mod, 'build_summary_table', return_value=fake_df) as mock_build:
        result = t_mod.build_table1()
        assert mock_build.called
        args, kwargs = mock_build.call_args
        # positional args: (paper_id, variables)
        assert args[0] == 'bank_fintech_tone'
        assert args[1] == t_mod._TABLE1_VARIABLES
        # paper_config 走 kwarg None 默认
        assert kwargs.get('paper_config') is None
        assert result is fake_df


def test_build_table1_propagates_paper_config():
    """传入自定义 paper_config 时 wrapper 必须透传."""
    from news_process.papers.bank_fintech_tone import tables as t_mod

    sentinel = object()  # 仅用作 identity check, 不需 PaperConfig 真实例
    fake_df = pd.DataFrame()
    with patch.object(t_mod, 'build_summary_table', return_value=fake_df) as mock_build:
        t_mod.build_table1(paper_config=sentinel)
        kwargs = mock_build.call_args.kwargs
        assert kwargs['paper_config'] is sentinel


def test_write_table1_default_filenames():
    """write_table1() 默认: filename='table1_summary_stats.csv', dta_filename='table1_summary_stats.dta'."""
    from news_process.papers.bank_fintech_tone import tables as t_mod

    fake_path = Path('/tmp/fake_table1.csv')
    with patch.object(t_mod, 'write_summary_table', return_value=fake_path) as mock_write:
        result = t_mod.write_table1()
        assert mock_write.called
        args, kwargs = mock_write.call_args
        assert args[0] == 'bank_fintech_tone'
        assert args[1] == t_mod._TABLE1_VARIABLES
        assert kwargs.get('filename') == 'table1_summary_stats.csv'
        assert kwargs.get('dta_filename') == 'table1_summary_stats.dta'
        assert result is fake_path


def test_write_table1_custom_filenames_propagate():
    """custom filename + dta_filename=None (仅 CSV) 正确透传."""
    from news_process.papers.bank_fintech_tone import tables as t_mod

    fake_path = Path('/tmp/custom.csv')
    with patch.object(t_mod, 'write_summary_table', return_value=fake_path) as mock_write:
        t_mod.write_table1(filename='custom.csv', dta_filename=None)
        kwargs = mock_write.call_args.kwargs
        assert kwargs.get('filename') == 'custom.csv'
        assert kwargs.get('dta_filename') is None


def test_table1_variables_inventory_stable():
    """_TABLE1_VARIABLES 锚定核心 16 变量 — 任何无意修改 (rename/drop) 立即报错."""
    from news_process.papers.bank_fintech_tone.tables import _TABLE1_VARIABLES

    # 不强制顺序, 但锚定关键变量必须存在 (这些是论文 spec 的 main treatments).
    must_have = {
        'llm_vote_tone_full',
        'llm_vote_tone_ctx',
        'n_articles',
        'auth_sim_emb_full',
        'auth_sim_emb_ctx',
        'benefit_mean_full',
        'benefit_mean_ctx',
        'prov_leave1out_tone_full',
        'bartik_type_iv_full',
    }
    actual = set(_TABLE1_VARIABLES)
    missing = must_have - actual
    assert not missing, f"_TABLE1_VARIABLES 丢失锚定变量: {missing}"
    # 总数 == 16 (Phase 3c 交付契约, 任何增减需同步修改 Stata 50_robustness_text2vec_stata.do)
    assert len(_TABLE1_VARIABLES) == 16


def test_module_exports_only_two_public_names():
    """__all__ 锁定 = ['build_table1', 'write_table1']; 防止意外暴露内部 helper."""
    from news_process.papers.bank_fintech_tone import tables as t_mod

    assert set(t_mod.__all__) == {'build_table1', 'write_table1'}
