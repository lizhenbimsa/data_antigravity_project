"""致命问题审计整改 (2026-07-10) 回归锁测试。

覆盖 scripts/audit/FATAL_AUDIT_FIX_EXECUTION_PLAN_2026-07-10.md 的:
  F1 — preprocess ParquetWriter schema 安全网 (cast 前提断言锁)
  F3 — network_spillover 行级 both-or-neither 补强 (_enforce_row_parity)
  F7 — strat_diff MAIN centroid 别名值域桶 [0,2] (负余弦不误崩)

F2/F4/F5/F8 的锁分别在 papers 图路径 / test_five_entrypoint_hardening (gate) /
run_production_regen / test_dual_track。
"""
import numpy as np
import pandas as pd
import pyarrow as pa
import pytest

# ── F3: 行级 both-or-neither 补强 ─────────────────────────────────────────────

@pytest.mark.fast
def test_f3_row_parity_clears_single_sided_orphan():
    """MAIN 有值 / _lg NaN (或反之) 的 (bank,year) 单边孤儿 → 两列同置 NaN。"""
    from news_process.pipeline.panel.network_spillover import _enforce_row_parity
    panel = pd.DataFrame({
        'target_bank': ['A', 'B', 'C'],
        'year': [2018, 2018, 2018],
        'emb_peer_tone_lag1_full': [0.5, 0.3, np.nan],      # canonical
        'emb_peer_tone_lag1_lg_full': [np.nan, 0.2, 0.1],   # _lg
        'bank_emb_sim_mean_lag1': [0.8, np.nan, 0.4],
        'bank_emb_sim_mean_lag1_lg': [0.7, 0.6, 0.4],
    })
    out = _enforce_row_parity(panel.copy())
    # A 行: canonical 有值 lg NaN → 两列 NaN; C 行: canonical NaN lg 有值 → 两列 NaN; B 行不变
    assert out['emb_peer_tone_lag1_full'].isna().tolist() == [True, False, True]
    assert out['emb_peer_tone_lag1_lg_full'].isna().tolist() == [True, False, True]
    # sim: B 行 canonical NaN lg 有值 → 两列 NaN; A/C 行两列俱在 → 保留
    assert out['bank_emb_sim_mean_lag1'].isna().tolist() == [False, True, False]
    assert out['bank_emb_sim_mean_lag1_lg'].isna().tolist() == [False, True, False]


@pytest.mark.fast
def test_f3_row_parity_noop_when_already_parity():
    """两侧 NaN 完全同构 (早期试跑 T=2 现状) → 逐字节 no-op (golden-safe by construction)。"""
    from news_process.pipeline.panel.network_spillover import _enforce_row_parity
    panel = pd.DataFrame({
        'target_bank': ['A', 'B'],
        'year': [2018, 2018],
        'emb_peer_tone_lag1_full': [0.5, np.nan],
        'emb_peer_tone_lag1_lg_full': [0.4, np.nan],   # NaN 位置与 canonical 同构
    })
    out = _enforce_row_parity(panel.copy())
    assert out.equals(panel), "parity 已成立时 helper 必须是 no-op"


@pytest.mark.fast
def test_f3_pairing_boundary_aware():
    """`_lg` 边界感知剥离: lag1 不含 _lg 子串, 唯一 _lg 是孪生标记, 配对不误配。"""
    from news_process.pipeline.panel.network_spillover import _enforce_row_parity
    # emb_peer_tone_diag_lag1_lg_ctx → canonical emb_peer_tone_diag_lag1_ctx
    panel = pd.DataFrame({
        'emb_peer_tone_diag_lag1_ctx': [0.5, np.nan],
        'emb_peer_tone_diag_lag1_lg_ctx': [np.nan, np.nan],
    })
    out = _enforce_row_parity(panel.copy())
    assert out['emb_peer_tone_diag_lag1_ctx'].isna().tolist() == [True, True]


# ── F7: strat_diff MAIN centroid 别名值域桶 ───────────────────────────────────

@pytest.mark.fast
def test_f7_main_centroid_alias_allows_distance_gt1():
    """strat_diff_{full,ctx,ss} 是 centroid_diff_emb 距离别名 δ∈[0,2]; 值 >1 (负余弦)
    不得触发 [0,1] 值域 AssertionError (审计 F7)。"""
    from news_process.pipeline.features import strategic_diff as sd
    # 含 >1 的 MAIN 别名值 (模拟负余弦 δ>1) — 不应抛
    panel = pd.DataFrame({'strat_diff_full': [1.5, 0.3], 'strat_diff_ctx': [1.9, 0.1]})
    sd._log_robustness_diagnostics(panel)  # 不抛即通过


@pytest.mark.fast
def test_f7_still_catches_true_out_of_bounds():
    """值域桶 [0,2] 仍守: δ>2 (真越界) 须触发 AssertionError, 未被过度放宽。"""
    from news_process.pipeline.features import strategic_diff as sd
    panel = pd.DataFrame({'strat_diff_full': [2.5, 0.3]})  # >2 越界
    with pytest.raises(AssertionError):
        sd._log_robustness_diagnostics(panel)


# ── F2: clarity 分布图不得给 load_panel 传 columns= ──────────────────────────

@pytest.mark.fast
def test_f2_clarity_figure_no_columns_filter():
    """F2: plot_clarity_distribution 不得给 load_panel 传 columns= —— pd.read_parquet 对缺列
    raise ArrowInvalid (非 FileNotFoundError, 逃逸 analysis.py 的 except), 而 ss 轨在 P4 付费
    run 前盘上必缺。须整盘加载后用 `col in panel.columns` skip-if-missing (镜像 bank_media_disagreement)。"""
    import inspect
    import re

    from news_process.papers.bank_news_clarity import figures as fig
    src = inspect.getsource(fig.plot_clarity_distribution)
    # 精确检查 load_panel(...) 调用参数内无 columns= (注释里的 'columns=' 字样不算)
    call = re.search(r'load_panel\((.*?)\)', src, re.S)
    assert call is not None, "未找到 load_panel 调用"
    assert 'columns=' not in call.group(1), \
        "clarity 分布图不得给 load_panel 传 columns= (缺列 ArrowInvalid 崩 CLI); 须整盘加载 skip-if-missing"
    assert 'in panel.columns' in src, "须保留 `col in panel.columns` skip-if-missing 守卫"


# ── F1: preprocess ParquetWriter schema 安全网前提锁 ─────────────────────────

@pytest.mark.fast
def test_f1_cast_safety_net_premises():
    """安全网依赖的 pyarrow cast 语义 (回归锁, 防 pyarrow 升级改行为):
    (1) float64(含NaN, from_pandas null-masked) → int64 成功 (NaN→null, 不 raise);
    (2) fractional float → int64 raise (safe=True);
    (3) 上述 raise 类型被 F1 except 元组覆盖。"""
    schema_int = pa.schema([('docid', pa.int64())])
    # (1) NaN → null 成功
    t1 = pa.Table.from_pandas(pd.DataFrame({'docid': [1.0, 2.0, float('nan')]}))
    casted = t1.cast(schema_int)
    assert casted.column('docid').null_count == 1
    assert casted.schema.field('docid').type == pa.int64()
    # (2)+(3) fractional → raise, 且属 F1 except 元组
    t2 = pa.Table.from_pandas(pd.DataFrame({'docid': [1.7, 2.9]}))
    with pytest.raises((pa.ArrowInvalid, pa.ArrowTypeError,
                        pa.ArrowNotImplementedError, ValueError)):
        t2.cast(schema_int)
    # 列集不匹配 → raise (亦被元组覆盖)
    t3 = pa.Table.from_pandas(pd.DataFrame({'other': [1, 2]}))
    with pytest.raises((pa.ArrowInvalid, pa.ArrowTypeError,
                        pa.ArrowNotImplementedError, ValueError)):
        t3.cast(schema_int)


@pytest.mark.fast
def test_f1_preprocess_schema_divergence_no_crash(monkeypatch, tmp_path):
    """F1 集成路径回归锁 (计划 §F1 line72 承诺的 test_preprocess_schema_divergence_no_crash;
    R2 对抗评审 confirmed P2: premise-only 测试只锁 pyarrow cast 语义, 回退 runner 的
    try/except 仍全绿 → 本测真正驱动 load_and_process_data 写循环, 锁住集成路径)。

    两源列集分歧 (a=2列 / b=3列): cast 双向皆 ValueError → 无论 as_completed 完成序如何,
    恰一源建 writer 成功、另一源被跳 → total 恒 = 2 (确定性, 中和完成序非确定)。断言:
    ① 不冒泡崩 DAG 根阶段 (F1 CRITICAL 本体); ② 分歧源被跳、已锁源正常落盘 (total==2);
    ③ source_reconciliation.json 把被跳源计入 failed_files + zero_contribution (对账可见)。
    回退 runner.py 的 try/except → ArrowInvalid/ValueError 冒泡, 本测立即变红。
    """
    import concurrent.futures as cf
    import json
    import os

    from news_process.pipeline.preprocess import runner

    # a=2列(docid,内容); b=3列(多 extra) — 列集不匹配, cast 双向皆 ValueError。
    df_a = pd.DataFrame({'docid': [1, 2], '内容': ['x', 'y']})
    df_b = pd.DataFrame({'docid': [3, 4], '内容': ['p', 'q'], 'extra': [9, 9]})

    def _fake_process(path):
        return df_b if os.path.basename(path).startswith('b') else df_a

    class _SyncExecutor:  # ProcessPool 跨进程 monkeypatch 在 Windows spawn 下失效 → 换同步 executor
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def submit(self, fn, arg):
            fut = cf.Future()
            try:
                fut.set_result(fn(arg))
            except Exception as e:  # noqa: BLE001 — 镜像真 Future 的异常捕获语义
                fut.set_exception(e)
            return fut

    raw = tmp_path / 'raw'
    raw.mkdir()
    (raw / 'a.xlsx').write_bytes(b'stub')  # 内容无关 (_process_single_file 已 patch)
    (raw / 'b.xlsx').write_bytes(b'stub')
    out = tmp_path / 'out' / '00_preprocessing.parquet'
    out.parent.mkdir()

    monkeypatch.setattr(cf, 'ProcessPoolExecutor', _SyncExecutor)
    monkeypatch.setattr(runner, '_process_single_file', _fake_process)
    monkeypatch.delenv('NEWS_PROCESS_STRICT_SOURCES', raising=False)  # 确保 strict 关 (否则跳源→raise)

    # ① 核心断言: schema 分歧不再冒泡崩根阶段
    total = runner.load_and_process_data(str(raw), str(out))

    # ② 分歧源被跳、恰一 2 行源落盘
    assert total == 2, f"分歧源应被跳、仅一 2 行源落盘, got total={total}"
    assert out.is_file(), "已锁 schema 源须正常落盘"
    assert len(pd.read_parquet(out)) == 2

    # ③ 被跳源计入 source_reconciliation.json 对账 (failed_files + zero_contribution)
    recon = json.loads((out.parent / 'source_reconciliation.json').read_text(encoding='utf-8'))
    assert recon['n_found'] == 2 and recon['n_contributed'] == 1
    assert recon['n_zero_contribution'] == 1
    assert len(recon['failed_files']) == 1
    assert 'schema mismatch' in recon['failed_files'][0]['error']
