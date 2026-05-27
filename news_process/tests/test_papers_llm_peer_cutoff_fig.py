"""tests/test_papers_llm_peer_cutoff_fig.py — Round 48 quality-hardening.

`papers/llm_peer/figures.py::plot_cutoff_sensitivity` (lines 17-48) 此前完全
未被测试. 通过 mock load_panel + 真实写 matplotlib 文件验证图表生成走通.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

# Force Agg backend before importing pyplot (headless safe)
os.environ.setdefault('MPLBACKEND', 'Agg')
import matplotlib  # noqa: E402

matplotlib.use('Agg', force=True)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


def test_plot_cutoff_sensitivity_writes_pdf(tmp_path):
    """plot_cutoff_sensitivity 用 mock load_panel 跑通完整路径 (lines 17-48)."""
    from news_process.papers.llm_peer import figures as fig_mod
    # 合成 panel: 5 个 cutoff 列各 50 行
    cutoffs = (70, 75, 80, 85, 90)
    rng = np.random.default_rng(seed=0)
    panel = pd.DataFrame({
        f'llm_peer_tone_iv_full_{c}': rng.normal(0.1, 0.05, 50)
        for c in cutoffs
    })

    # 用 tmp_path 作 paper output_dir
    from news_process.papers._common.paper_config import PaperConfig
    fake_pc = PaperConfig(
        paper_id='llm_peer',
        project_root=tmp_path,
        panel_dir=tmp_path / 'panel',
        output_dir=tmp_path / 'output',
        do_dir=tmp_path / 'do',
        drafts_dir=tmp_path / 'drafts',
        config={'paths': {'output_dir': str(tmp_path / 'panel')}},
    )
    fake_pc.output_dir.mkdir(parents=True, exist_ok=True)
    fake_pc.panel_dir.mkdir(parents=True, exist_ok=True)

    with patch.object(fig_mod, 'load_panel', return_value=panel):
        out = fig_mod.plot_cutoff_sensitivity(fake_pc)
    assert out.exists()
    assert out.suffix == '.pdf'


def test_plot_cutoff_sensitivity_handles_missing_columns(tmp_path):
    """部分 cutoff 列在 panel 中缺失 → 用 nan 填 mean/std, 不抛."""
    from news_process.papers.llm_peer import figures as fig_mod
    # panel 只有 2/5 个 cutoff 列
    panel = pd.DataFrame({
        'llm_peer_tone_iv_full_70': [0.1, 0.2, 0.15],
        'llm_peer_tone_iv_full_90': [0.05, 0.1, 0.08],
    })

    from news_process.papers._common.paper_config import PaperConfig
    fake_pc = PaperConfig(
        paper_id='llm_peer',
        project_root=tmp_path,
        panel_dir=tmp_path / 'panel',
        output_dir=tmp_path / 'output',
        do_dir=tmp_path / 'do',
        drafts_dir=tmp_path / 'drafts',
        config={'paths': {'output_dir': str(tmp_path / 'panel')}},
    )
    fake_pc.output_dir.mkdir(parents=True, exist_ok=True)
    fake_pc.panel_dir.mkdir(parents=True, exist_ok=True)

    with patch.object(fig_mod, 'load_panel', return_value=panel):
        out = fig_mod.plot_cutoff_sensitivity(
            fake_pc, filename='custom_cutoff.pdf')
    assert out.name == 'custom_cutoff.pdf'
    assert out.exists()
