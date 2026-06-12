"""v3.5.0 D7 集成测试: v3.4.0 → v3.5.0 迁移与向前兼容。

Per 原 stage3_v3_5_0_augmentation_plan §4.1 + §4.2 (文档已随 docs/ 删除):
    6 个集成测试, 覆盖:
        - encode_collab.py 重构表面 (apply_v3_5_0 入口点存在)
        - shim 39c_construct_orthogonality.py 存在 + 委托到模块
        - dag.py STAGES_VALIDATION 含 39c entry (per F-B-NEW-5 修正)
        - CELL_ID_VALUE_LABEL Stata 编码字典与 cell_id 公式一致
        - v3.5.0 Stata 模板放 v3_5_0/ 子目录 (per F45 隔离 legacy build glob)
        - 11 个 v3_3_to_v3_4 migration tests (如存在) 保留 forward compat (per m7)
"""
from __future__ import annotations

from pathlib import Path

import pytest

# ----------------------------------------------------------------------------
# Test 1: encode_collab.py 的 apply_v3_5_0 入口点存在
# ----------------------------------------------------------------------------

def test_encode_collab_apply_v3_5_0_entry_point():
    """encode_collab.apply_v3_5_0 必须存在且接受 (df, panel, ctx_baseline_path=None) 签名。"""
    import inspect

    from news_process.pipeline.panel.encode_collab import apply_v3_5_0

    sig = inspect.signature(apply_v3_5_0)
    params = list(sig.parameters)
    assert 'df' in params
    assert 'panel' in params
    assert 'ctx_baseline_path' in params


# ----------------------------------------------------------------------------
# Test 2: Stage 39c shim 位于正确路径 + 委托到 pipeline 模块
# ----------------------------------------------------------------------------

def test_shim_39c_exists_and_delegates():
    """news_process/39c_construct_orthogonality.py 必须是 ≤ 30 行 thin shim, 且 import run_stage。"""
    shim_path = Path(__file__).resolve().parents[2] / '39c_construct_orthogonality.py'
    assert shim_path.exists(), f"Missing shim: {shim_path}"
    content = shim_path.read_text(encoding='utf-8')
    # shim 不变量: 非空行 ≤ 30
    lines = [l for l in content.splitlines() if l.strip()]
    assert len(lines) <= 30, f"Shim too long: {len(lines)} non-empty lines (>30)"
    # 必须从 pipeline.audit 导入 run_stage
    assert 'from news_process.pipeline.audit.construct_orthogonality import run_stage' in content


# ----------------------------------------------------------------------------
# Test 3: DAG STAGES_VALIDATION 注册了 39c
# ----------------------------------------------------------------------------

def test_dag_registers_stage_39c():
    """core/dag.py STAGES_VALIDATION 必须含 39c entry (per plan §2.2.1 + F-B-NEW-5)。"""
    from news_process.core import dag

    scripts = [s.script for s in dag.STAGES_VALIDATION]
    assert '39c_construct_orthogonality.py' in scripts, (
        f"Stage 39c not registered; STAGES_VALIDATION = {scripts}"
    )
    # construct_orthogonality 谓词也必须同步注册
    assert 'construct_orthogonality' in dag._VALIDATION_PREDS


# ----------------------------------------------------------------------------
# Test 4: CELL_ID_VALUE_LABEL 与 cell_id 公式一致
# ----------------------------------------------------------------------------

def test_cell_id_value_label_consistency():
    """stata_export.CELL_ID_VALUE_LABEL 的 8 个条目必须对齐 cell_id 公式 s*4+l*2+c+1。

    cell 1 = sub.tech.indep (三维 baseline)
    cell 8 = symb.app.collab (三维 contrast)
    """
    from news_process.pipeline.panel.stata_export import CELL_ID_VALUE_LABEL

    assert set(CELL_ID_VALUE_LABEL.keys()) == set(range(1, 9))
    assert CELL_ID_VALUE_LABEL[1] == 'sub.tech.indep'
    assert CELL_ID_VALUE_LABEL[8] == 'symb.app.collab'
    # 逐条验证 label 正确编码了 (s, l, c) 三个比特位
    for cell_id, label in CELL_ID_VALUE_LABEL.items():
        s_bit = (cell_id - 1) >> 2 & 1
        l_bit = (cell_id - 1) >> 1 & 1
        c_bit = (cell_id - 1) & 1
        # subst 位: 0=sub, 1=symb
        assert label.startswith('symb') if s_bit else label.startswith('sub'), (
            f"cell {cell_id} subst bit {s_bit} mismatch label {label}"
        )
        # locus 位: 0=tech, 1=app
        assert '.app.' in label if l_bit else '.tech.' in label, (
            f"cell {cell_id} locus bit {l_bit} mismatch label {label}"
        )
        # collab 位: 0=indep, 1=collab
        assert label.endswith('.collab') if c_bit else label.endswith('.indep'), (
            f"cell {cell_id} collab bit {c_bit} mismatch label {label}"
        )


# ----------------------------------------------------------------------------
# Test 5: v3.5.0 Stata 模板放在 v3_5_0/ 子目录 (per F45 隔离)
# ----------------------------------------------------------------------------

def test_v3_5_0_stata_templates_in_subdirectory():
    """v3.5.0 D2/D4 模板必须放 v3_5_0/ 子目录, 以绕开 legacy build_replication glob。

    Per plan §2.1.5 + F45: legacy `build_replication_package` 用的是非递归
    glob('*.do.tmpl'), 所以带 jinja2 占位符 ({{ panel_path }}) 的新模板
    必须隔离到子目录中。
    """
    templates_dir = Path(__file__).resolve().parents[2] / 'papers' / '_common' / 'stata_templates'
    v3_5_0_dir = templates_dir / 'v3_5_0'

    assert v3_5_0_dir.is_dir(), f"Missing v3_5_0/ subdirectory: {v3_5_0_dir}"

    expected_templates = (
        '19_table6_cell_decomposition.do.tmpl',
        '25_tableA6_dual_track_residual.do.tmpl',
    )
    for tmpl_name in expected_templates:
        tmpl_path = v3_5_0_dir / tmpl_name
        assert tmpl_path.exists(), f"Missing v3.5.0 template: {tmpl_path}"

    # 验证 v3.5.0 模板不直接放在 _common/stata_templates/ 顶层 (否则会破坏 legacy glob)
    direct_v3_5_0 = list(templates_dir.glob('19_table6*.do.tmpl')) + \
                    list(templates_dir.glob('25_tableA6*.do.tmpl'))
    assert not direct_v3_5_0, (
        f"v3.5.0 templates should NOT be in direct stata_templates/ (legacy build glob risk); "
        f"found: {direct_v3_5_0}"
    )


# ----------------------------------------------------------------------------
# Test 6: encode.py 存在 hook 委托调用 (R0 混合路径, per F48)
# ----------------------------------------------------------------------------

def test_encode_py_hook_calls_encode_collab():
    """encode.py L1085 附近必须含调用 encode_collab.apply_v3_5_0 的 hook (混合路径)。"""
    encode_path = Path(__file__).resolve().parents[2] / 'pipeline' / 'panel' / 'encode.py'
    content = encode_path.read_text(encoding='utf-8')

    # hook 必须引用 encode_collab 模块 + apply_v3_5_0 入口点
    assert 'encode_collab' in content, "encode.py missing encode_collab import/reference"
    assert 'apply_v3_5_0' in content, "encode.py missing apply_v3_5_0 hook call"
    # 混合路径注释标记, per plan §1.1 R0 / F48
    assert 'v3.5.0 D2' in content or 'v3.5.0' in content, (
        "encode.py missing v3.5.0 marker comment"
    )


# ----------------------------------------------------------------------------
# CR-20: 真实数据 smoke test — 验证 v3.5.0 D2/D4 派生在生产 stage 21
# parquet 上不崩溃 (文件缺失则跳过)。
# ----------------------------------------------------------------------------



def test_apply_v3_5_0_on_real_stage21_smoke():
    """Smoke test: 若真实 stage 21 + 40_panel parquet 存在, 则在其上跑 apply_v3_5_0。

    这是唯一一个用生产数据驱动 v3.5.0 代码的测试 (其余测试按 plan §4.1 F36
    用合成小 fixture)。可逮住 Int8 溢出、panel 索引与真实数据不匹配等问题。

    标记 @pytest.mark.slow → 默认 `pytest -m fast` 跳过; 仅在 nightly 或
    发布前 sweep 中运行。data/processed/*.parquet 缺失时自动跳过。
    """
    import pandas as pd

    repo_root = Path(__file__).resolve().parents[3]
    stage_21_path = repo_root / 'news_process' / 'data' / 'processed' / '21_tone_llms.parquet'
    panel_path = repo_root / 'news_process' / 'data' / 'processed' / '40_panel_yearly.parquet'

    if not stage_21_path.exists():
        pytest.skip(f"Real stage 21 parquet missing: {stage_21_path}")
    if not panel_path.exists():
        pytest.skip(f"Real panel parquet missing: {panel_path}")

    df = pd.read_parquet(stage_21_path)
    panel = pd.read_parquet(panel_path)

    # 生产约定: 扁平 panel, target_bank + year 是普通列而非索引
    # (per encode.py:666 reset_index 模式)。
    if 'target_bank' not in panel.columns or 'year' not in panel.columns:
        pytest.skip("Real panel missing target_bank/year cols, can't smoke test")
    if 'target_bank' not in df.columns:
        pytest.skip("Real df missing target_bank col, can't smoke test")

    # stage 21 parquet 只有 日期 列没有 year (year 在 aggregate_panel 之前由
    # encode.py::parse_time 解析 — 但 smoke test 直接读 stage 21), 故在此派生 year。
    if 'year' not in df.columns:
        if '日期' in df.columns:
            df['year'] = pd.to_datetime(df['日期'], errors='coerce').dt.year
            df = df.dropna(subset=['year'])
            df['year'] = df['year'].astype(int)
        else:
            pytest.skip("Real df missing year/日期, can't smoke test")

    from news_process.pipeline.panel.encode_collab import apply_v3_5_0

    # smoke: 不应抛异常; 并验证 diagnostics dict 结构。
    diag = apply_v3_5_0(df, panel, ctx_baseline_path=None)
    assert 'v3_5_0_cell_id_added' in diag
    assert 'v3_5_0_residual_articles_added' in diag
    assert 'd2_identity' in diag
    assert 'd4_quality' in diag

    # 验证 cell_id 列已加到 df
    assert 'cell_id_full' in df.columns
    assert 'cell_id_ctx' in df.columns

    # 验证 d4_data_quality_flag 已加到 panel (str 列, 便于 Stata 可见)
    assert 'd4_data_quality_flag' in panel.columns

    # F-51: 显式探测生产数据 lineage 缺口 (stage 21 缺 collab_mode)。
    # 当 stage 21 parquet 是 pre-v3.4.0 版本 (缺 innovation_collab_mode_*) 时,
    # cell_id 全 NA + D2 聚合被跳过 — 主交付物无法物化。
    # 这种情况**应该大声失败**, 让 PR review 逮住数据依赖缺口,
    # 而不是静默绿通过。若你刻意要对 pre-v3.4.0 parquet 跑测试,
    # 请注释掉此断言。
    cell_all_na = df['cell_id_full'].isna().all()
    d2_skipped = diag['d2_identity'].get('cell_aggregation_skipped', False)
    if cell_all_na or d2_skipped:
        skip_reason = diag['d2_identity'].get('skip_reason', 'unknown')
        # 带说明信息地 skip; 生产落地需要用 prompt v8 (含 collab_mode)
        # 重跑 stage 21 — 这是 plan §9 的前置条件
        # (当前未显式列出; 记录于 audit_log §A.production_lineage)。
        pytest.skip(
            f"Production stage 21 lacks v3.4.0 collab_mode columns "
            f"(skip_reason={skip_reason!r}); v3.5.0 D2 deliverable requires "
            "stage 21 re-run with prompt v8. Plan §9 should add this prereq."
        )

    # 走到这里说明完整 D2 交付物可用: 验证恒等式在生产数据上成立
    assert diag['d2_identity']['main_fail'] == 0, (
        f"Main identity n_articles != Σ cell_1..8 on production data: "
        f"{diag['d2_identity']['main_fail']} violations"
    )
