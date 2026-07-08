"""WP1 — 税调企业×年 银企共现面板定向锁 (COMPANY_TAX_BANK_COOC_PANEL_EXECUTION_PLAN_2026-07-08 v4)。

镜像母本 `tests/test_company_bank_cooc_panel.py` 全谱 58 项 + 税调新增件 (usci 三联断言),
行键换 `company_tax_name` / 固定列换税调 20 列 (含 usci str18 + is_bank_company)。

全 mock 数据, 不碰盘上 parquet (仅 registry yaml / 税调名单 yaml 只读)。加权引擎经
`mod.engine()` (importlib 惰性单例) 只读复用 listed 02 (T-D10, 跨管道禁第二份实现):
公司相关件 (scan_hits/build_pair_table/build_counts/add_hhi/make_label/main/usci_map/run_gates)
在税调 02 本地 (mod); 公司无关加权引擎件 (compute_weighted_panel/_compute_weighted_panel_percol/
build_measure_library/load_input21/INPUT_COLS/compute_wt_base) 在 listed 引擎 (eng)。

⚠ 并发安全 (T-D18 铁律): pytest 运行期绝不写 company_tax_bank/data|logs (03 可能后台在跑);
读取仅限 exists()/stat() 只读; test_pytest_never_touches_stage_logs 聚焦本模块自身 stem 日志
(03 并发只 append 自身 log、不新建/截断他 stem 日志) + FileHandler 断言 (并发无关的权威确证)。
"""
from __future__ import annotations

import importlib.util
import logging
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
TAX_DIR = REPO / "company_tax_bank"
if str(TAX_DIR) not in sys.path:
    sys.path.insert(0, str(TAX_DIR))


# 序号前缀模块名 (02_*) 非合法 import 语句标识符 → 走 importlib; 且 listed/税调 02 均以 "02_" 起,
# 用 spec_from_file_location 按绝对路径加载防 sys.modules 键碰撞 (镜像 listed panel 测试加载方式)。
def _load_tax_module(stem: str):
    spec = importlib.util.spec_from_file_location(stem, TAX_DIR / f"{stem}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[stem] = m
    spec.loader.exec_module(m)
    return m


mod = _load_tax_module("02_build_company_tax_bank_cooc_panel")  # 税调 02 (公司相关本地件)
eng = mod.engine()  # listed 加权引擎 (公司无关件; pytest 守卫下 _attach_engine_logging 早退无副作用)

pytestmark = pytest.mark.fast


# ---------------------------------------------------------------- mock 资产
def make_automaton(variant_owner: dict[str, list[str]]):
    import ahocorasick
    A = ahocorasick.Automaton()
    for v, owners in variant_owner.items():
        A.add_word(v, (v, owners))
    A.make_automaton()
    return A


def make_input(rows: list[dict]) -> pd.DataFrame:
    """rows: dicts with docid, year, bank, full, ctx, ss, ss_fb, verified。"""
    return pd.DataFrame({
        "docid": [r["docid"] for r in rows],
        "_year": [r["year"] for r in rows],
        "target_bank": [r["bank"] for r in rows],
        "content_full": [r.get("full", "") for r in rows],
        "content_ctx": [r.get("ctx", "") for r in rows],
        "content_ss": [r.get("ss", "") for r in rows],
        "ss_is_fallback": [r.get("ss_fb", False) for r in rows],
        "_verified": [r.get("verified", True) for r in rows],
    })


def run_pipeline(rows, variant_owner, bank_substr=None, own_map=None, companies=None,
                 y0=2017, y1=2018):
    A = make_automaton(variant_owner)
    df = make_input(rows)
    hits = mod.scan_hits(df, A, bank_substr or {}, own_map or {})
    if hits.empty:
        comps = companies or sorted({c for os_ in variant_owner.values() for c in os_})
        idx = pd.MultiIndex.from_product([comps, range(y0, y1 + 1)],
                                         names=["company_tax_name", "year"])
        return hits, pd.DataFrame(), pd.DataFrame(index=idx).reset_index()
    _, hits = mod.build_year_map(hits)
    pair = mod.build_pair_table(hits, y0, y1)
    comps = companies or sorted({c for os_ in variant_owner.values() for c in os_})
    panel = mod.build_counts(hits, comps, y0, y1, set())
    panel = mod.add_hhi(panel, pair)
    return hits, pair, panel


VO = {"甲税企": ["甲税企"], "乙税企": ["乙税企"]}


def row(docid, bank, text, year=2017, **kw):
    return dict(docid=docid, year=year, bank=bank, full=text, ctx=text, ss=text, **kw)


def cell(panel, comp, year, col):
    m = (panel["company_tax_name"] == comp) & (panel["year"] == year)
    return panel.loc[m, col].iloc[0]


# ---------------------------------------------------------------- (A) 计数锁
def test_docid_dedup_across_banks():
    """同 docid 双 target_bank 只计 1 篇, 但 n_banks_full 计 2。"""
    rows = [row(1, "银行A", "甲税企获两行贷款"), row(1, "银行B", "甲税企获两行贷款")]
    _, _, panel = run_pipeline(rows, VO)
    assert cell(panel, "甲税企", 2017, "n_cooc_full") == 1
    assert cell(panel, "甲税企", 2017, "n_banks_full") == 2


def test_own_bank_exclusion_d4():
    """D4: 银行系企业 vs 自家银行=0, vs 他行=1 (对照表覆盖锁 ④b)。"""
    vo = {"民生银行": ["民生银行股份"]}  # variant → owners
    own = {"民生银行股份": {"中国民生银行"}}
    rows = [row(1, "中国民生银行", "民生银行发布金科战略"),
            row(2, "银行B", "民生银行与银行B合作")]
    _, _, panel = run_pipeline(rows, vo, own_map=own)
    assert cell(panel, "民生银行股份", 2017, "n_cooc_full") == 1  # 仅 docid 2


def test_duplicate_variant_multi_owner_d5():
    vo = {"东风": ["东风汽车", "东风科技"]}
    rows = [row(1, "银行A", "东风入场")]
    _, _, panel = run_pipeline(rows, vo)
    assert cell(panel, "东风汽车", 2017, "n_cooc_full") == 1
    assert cell(panel, "东风科技", 2017, "n_cooc_full") == 1


def test_ss_strict_and_verified_gate():
    rows = [row(1, "银行A", "甲税企", ss_fb=True, verified=True),
            row(2, "银行A", "甲税企", ss_fb=False, verified=False)]
    _, _, panel = run_pipeline(rows, VO)
    assert cell(panel, "甲税企", 2017, "n_cooc_ss") == 2
    assert cell(panel, "甲税企", 2017, "n_cooc_ss_strict") == 1  # 剔 fallback
    assert cell(panel, "甲税企", 2017, "n_cooc_full_v") == 1     # 剔 unverified


def test_panel_skeleton_zero_fill():
    rows = [row(1, "银行A", "甲税企")]
    _, _, panel = run_pipeline(rows, VO, y0=2017, y1=2019)
    assert len(panel) == 2 * 3  # 2 企业 × 3 年
    assert cell(panel, "乙税企", 2018, "n_cooc_full") == 0
    for t in ("full", "ctx", "ss"):
        nb, nc = panel[f"n_banks_{t}"], panel[f"n_cooc_{t}"]
        assert ((nb >= 1) == (nc >= 1)).all()


def test_panel_year_window_2011_2020():
    """v7 口径修正守卫: 面板年窗默认 = 税调数据可得域 2011–2020 (10 年); 绝对合法年域保持
    新闻语料发表域 2007–2025 不动 (两概念刻意分离, 见 02 ABS/PANEL 分叉铁律)。防未来静默回退窗口。"""
    assert (mod.PANEL_YEAR_MIN, mod.PANEL_YEAR_MAX) == (2011, 2020), "面板年窗须 = 2011–2020"
    assert (mod.ABS_YEAR_MIN, mod.ABS_YEAR_MAX) == (2007, 2025), "绝对合法域须保持语料域 2007–2025"
    assert mod.PANEL_YEAR_MAX - mod.PANEL_YEAR_MIN + 1 == 10
    # 骨架 math: 默认窗上 n_firms × 10 行 (乘式恒等, 非写死行数); 窗内命中年 2017 计入
    _, _, panel = run_pipeline([row(1, "银行A", "甲税企", year=2017)], VO,
                               y0=mod.PANEL_YEAR_MIN, y1=mod.PANEL_YEAR_MAX)
    assert len(panel) == 2 * 10, "满骨架 = 2 企业 × 10 年"
    assert set(panel["year"]) == set(range(2011, 2021))


def test_three_tracks_independent():
    rows = [dict(docid=1, year=2017, bank="银行A", full="甲税企", ctx="无", ss="无")]
    _, _, panel = run_pipeline(rows, VO)
    assert cell(panel, "甲税企", 2017, "n_cooc_full") == 1
    assert cell(panel, "甲税企", 2017, "n_cooc_ctx") == 0
    assert cell(panel, "甲税企", 2017, "n_cooc_ss") == 0


# ---------------------------------------------------------------- D4b 子串自共现
def test_mudanjiang_d4b():
    """牡丹江锁: 对子串银行 (canonical 龙江银行)=0, 对他行=1 (注入式合成夹具, 不依赖盘上名单)。"""
    vo = {"牡丹江": ["卧龙实业"]}
    sub = {"龙江银行": frozenset({"牡丹江"})}
    rows = [row(1, "龙江银行", "牡丹江市商业银行发布"), row(2, "银行B", "牡丹江地区新闻")]
    _, _, panel = run_pipeline(rows, vo, bank_substr=sub)
    assert cell(panel, "卧龙实业", 2017, "n_cooc_full") == 1  # 仅 docid 2


def test_d4b_kept_when_nonsubstr_variant_hits():
    """命中含非子串 variant 则保留 (逐轨判定)。"""
    # 企业 X 有两个 variant: "牡丹江" 是子串、"某税企" 不是 → 非子串 variant 命中即保留
    variant_owner = {"牡丹江": ["某税企"], "某税企": ["某税企"]}
    sub = {"龙江银行": frozenset({"牡丹江"})}
    rows = [row(1, "龙江银行", "牡丹江市商业银行与某税企合作")]
    _, _, panel = run_pipeline(rows, variant_owner, bank_substr=sub)
    assert cell(panel, "某税企", 2017, "n_cooc_full") == 1  # 非子串 variant 命中 → 保留


def test_variant_substring_double_count():
    """④ 子串双计: 命中长名同时命中其子串短 variant → 两企业各 +1 属预期。"""
    vo = {"中国石化": ["中国石化"], "中国石化上海石油化工": ["上海石化公司"]}
    rows = [row(1, "银行A", "中国石化上海石油化工获贷")]
    _, _, panel = run_pipeline(rows, vo)
    assert cell(panel, "中国石化", 2017, "n_cooc_full") == 1
    assert cell(panel, "上海石化公司", 2017, "n_cooc_full") == 1


# ---------------------------------------------------------------- 跨年/混合 docid
def test_cross_year_docid_min_year():
    """⑤ 同 docid 两年 → 全局去重后只计 min(年) 1 篇; pair 表同锁。"""
    rows = [row(1, "银行A", "甲税企", year=2018), row(1, "银行B", "甲税企", year=2017)]
    _, pair, panel = run_pipeline(rows, VO)
    assert cell(panel, "甲税企", 2017, "n_cooc_full") == 1
    assert cell(panel, "甲税企", 2018, "n_cooc_full") == 0
    p = pair[(pair["track"] == "full")]
    assert set(p["year"]) == {2017}  # pair 侧同落 min 年 (v22)


def test_mixed_docid_v_row_level():
    """⑦ 混合 docid: 企业名只命中 unverified 行文本 → 计 canonical 不计 _v。"""
    rows = [dict(docid=1, year=2017, bank="银行A", full="无", ctx="无", ss="无", verified=True),
            dict(docid=1, year=2017, bank="银行B", full="无", ctx="甲税企", ss="无", verified=False)]
    _, _, panel = run_pipeline(rows, VO)
    assert cell(panel, "甲税企", 2017, "n_cooc_ctx") == 1
    assert cell(panel, "甲税企", 2017, "n_cooc_ctx_v") == 0


def test_verified_divergence():
    """⑥ verified 分化: 含 unverified 行 → _v 严格小于 canonical。"""
    rows = [row(1, "银行A", "甲税企", verified=True), row(2, "银行A", "甲税企", verified=False)]
    _, _, panel = run_pipeline(rows, VO)
    assert cell(panel, "甲税企", 2017, "n_cooc_full_v") < cell(panel, "甲税企", 2017, "n_cooc_full")


# ---------------------------------------------------------------- v22 增量包锁
def test_hhi_three_locks():
    """⑧ HHI: 两银行 3:1 → 0.625 手算 / 单银行无容差 ==1.0 / 零共现 NaN。"""
    rows = ([row(i, "银行A", "甲税企") for i in range(1, 4)]  # 3 篇 A
            + [row(4, "银行B", "甲税企")]                      # 1 篇 B
            + [row(5, "银行A", "乙税企")])                     # 乙单银行
    _, _, panel = run_pipeline(rows, VO)
    assert cell(panel, "甲税企", 2017, "cooc_hhi_full") == pytest.approx(0.625)
    assert cell(panel, "乙税企", 2017, "cooc_hhi_full") == 1.0
    assert np.isnan(cell(panel, "乙税企", 2018, "cooc_hhi_full"))


def test_frac_identity():
    """⑨ frac 恒等: 5 银行联播 1 篇 + 独家 1 篇 → Σ_b n_docs_frac = 2 (isclose 禁精确)。"""
    rows = [row(1, f"银行{i}", "甲税企") for i in "ABCDE"] + [row(2, "银行A", "甲税企")]
    _, pair, panel = run_pipeline(rows, VO)
    p = pair[pair["track"] == "full"]
    assert np.isclose(p["n_docs_frac"].sum(), 2.0)
    assert cell(panel, "甲税企", 2017, "n_cooc_full") == 2


def test_frac_v_row_gate():
    """⑩ 混合 docid → k_v < k 且 Σ_b frac_v = n_cooc_v。"""
    rows = [row(1, "银行A", "甲税企", verified=True), row(1, "银行B", "甲税企", verified=False)]
    _, pair, panel = run_pipeline(rows, VO)
    p = pair[pair["track"] == "full"]
    assert np.isclose(p["n_docs_frac_v"].sum(), cell(panel, "甲税企", 2017, "n_cooc_full_v"))
    assert p.loc[p["bank"] == "银行A", "n_docs_frac_v"].iloc[0] == 1.0  # k_v=1
    assert p.loc[p["bank"] == "银行A", "n_docs_frac"].iloc[0] == 0.5    # k=2


def test_longhit():
    """⑪ 3 字 variant 不入 longhit; ≥4 字入; 混合命中 → 计入 (任一 ≥4 即计)。"""
    vo = {"东风": ["丙税企"], "丙税企全称名": ["丙税企"]}
    rows = [row(1, "银行A", "东风来了"),                 # 仅 2 字
            row(2, "银行A", "丙税企全称名与东风")]        # 混合: ≥4 字 + 短
    _, pair, _ = run_pipeline(rows, vo, companies=["丙税企"])
    p = pair[(pair["track"] == "full") & (pair["bank"] == "银行A")]
    assert p["n_docs"].iloc[0] == 2
    assert p["n_docs_longhit"].iloc[0] == 1  # 仅 docid 2 (混合命中计入)
    assert (pair["n_docs_longhit"] <= pair["n_docs"]).all()


# ---------------------------------------------------------------- (B) 加权引擎锁 (eng 复用 listed 02)
def mini_registry(entries):
    return {"entries": entries, "bank_company_map": {}, "excluded": {},
            "meta": {"registry_sha256": "x", "n_entries": len(entries)}}


def entry(base, track_agnostic=False, emit=True, gate="none", source="40"):
    return dict(basename=base, family="Q", source=source,
                col_by_track={t: (base if track_agnostic else f"{base}_{t}") for t in mod.TRACKS},
                track_agnostic=track_agnostic, agg=None, emit_tracks=list(mod.TRACKS),
                emit_panel=emit, cut_code=None if emit else "CUT_V23", range_gate=gate,
                label_elems={"family": "Q", "base": base}, short_name=base)


def make_measures(data: dict) -> pd.DataFrame:
    df = pd.DataFrame(data)
    return df.set_index(["target_bank", "year"])


def wtab(rows):
    return pd.DataFrame(rows, columns=["company", "bank", "year", "track", "w"])


def test_weighted_two_bank_hand_calc():
    """手算两银行不等权重 + 测度缺失重归一 + ce 等权。"""
    reg = mini_registry([entry("x")])
    meas = make_measures({"target_bank": ["A", "B", "C"], "year": [2017] * 3,
                          "x_full": [1.0, 3.0, np.nan],
                          "x_ctx": [1.0, 3.0, np.nan], "x_ss": [1.0, 3.0, np.nan]})
    w = wtab([("甲", "A", 2017, "full", 3), ("甲", "B", 2017, "full", 1), ("甲", "C", 2017, "full", 9)])
    out = eng.compute_weighted_panel(w, meas, reg)
    # C 测度缺失 → 重归一后 cw = (3*1 + 1*3)/4 = 1.5; ce = mean(1,3)=2
    assert out.loc[("甲", 2017), "cw_x_full"] == pytest.approx(1.5, rel=1e-12)
    assert out.loc[("甲", 2017), "ce_x_full"] == pytest.approx(2.0)


def test_single_bank_cw_eq_ce_and_nan():
    reg = mini_registry([entry("x")])
    meas = make_measures({"target_bank": ["A", "B"], "year": [2017, 2017],
                          "x_full": [5.0, np.nan], "x_ctx": [5.0, np.nan], "x_ss": [5.0, np.nan]})
    w = wtab([("甲", "A", 2017, "full", 2), ("乙", "B", 2017, "full", 2)])
    out = eng.compute_weighted_panel(w, meas, reg)
    assert out.loc[("甲", 2017), "cw_x_full"] == 5.0  # N=1 短路精确
    assert out.loc[("甲", 2017), "ce_x_full"] == 5.0
    assert np.isnan(out.loc[("乙", 2017), "cw_x_full"])  # 全缺测度 → NaN 非 0


def test_independent_renormalization_per_measure():
    reg = mini_registry([entry("x"), entry("y")])
    meas = make_measures({"target_bank": ["A", "B"], "year": [2017] * 2,
                          "x_full": [1.0, np.nan], "y_full": [1.0, 2.0],
                          "x_ctx": [np.nan] * 2, "y_ctx": [np.nan] * 2,
                          "x_ss": [np.nan] * 2, "y_ss": [np.nan] * 2})
    w = wtab([("甲", "A", 2017, "full", 1), ("甲", "B", 2017, "full", 3)])
    out = eng.compute_weighted_panel(w, meas, reg)
    assert out.loc[("甲", 2017), "cw_x_full"] == 1.0            # B 缺 x → 全权重落 A
    assert out.loc[("甲", 2017), "cw_y_full"] == pytest.approx(1.75)  # (1+6)/4


def test_track_no_crossmix_and_agnostic():
    """权重与测度同轨不串轨; track-agnostic 源列三轨权重产三个不同值。"""
    reg = mini_registry([entry("q", track_agnostic=True)])
    meas = make_measures({"target_bank": ["A", "B"], "year": [2017] * 2, "q": [10.0, 20.0]})
    w = wtab([("甲", "A", 2017, "full", 1), ("甲", "B", 2017, "full", 1),
              ("甲", "A", 2017, "ctx", 3), ("甲", "B", 2017, "ctx", 1),
              ("甲", "A", 2017, "ss", 1), ("甲", "B", 2017, "ss", 3)])
    out = eng.compute_weighted_panel(w, meas, reg)
    assert out.loc[("甲", 2017), "cw_q_full"] == pytest.approx(15.0)
    assert out.loc[("甲", 2017), "cw_q_ctx"] == pytest.approx(12.5)
    assert out.loc[("甲", 2017), "cw_q_ss"] == pytest.approx(17.5)


def test_nan_mask_lock():
    """② NaN 掩码: 分子 fillna(0)·notna, 不被 NaN 传播污染。"""
    reg = mini_registry([entry("x")])
    meas = make_measures({"target_bank": ["A", "B"], "year": [2017] * 2,
                          "x_full": [2.0, np.nan], "x_ctx": [2.0, np.nan], "x_ss": [2.0, np.nan]})
    w = wtab([("甲", "A", 2017, "full", 1), ("甲", "B", 2017, "full", 99)])
    out = eng.compute_weighted_panel(w, meas, reg)
    assert out.loc[("甲", 2017), "cw_x_full"] == 2.0  # 非 NaN


def test_missing_source_col_all_nan():
    """缺源列 → 输出全缺失列, schema 恒等 registry 推导值。"""
    reg = mini_registry([entry("ghost")])
    meas = make_measures({"target_bank": ["A"], "year": [2017], "other": [1.0]})
    w = wtab([("甲", "A", 2017, "full", 1)])
    out = eng.compute_weighted_panel(w, meas, reg)
    assert "cw_ghost_full" in out.columns
    assert out["cw_ghost_full"].isna().all()


def test_emit_false_no_projection():
    """⑫a emit 负例: emit_panel=false 基名零投影列。"""
    reg = mini_registry([entry("keep"), entry("cut", emit=False)])
    meas = make_measures({"target_bank": ["A"], "year": [2017],
                          **{f"{b}_{t}": [1.0] for b in ("keep", "cut") for t in mod.TRACKS}})
    w = wtab([("甲", "A", 2017, "full", 1)])
    out = eng.compute_weighted_panel(w, meas, reg)
    assert "cw_keep_full" in out.columns
    assert not any("cut" in c for c in out.columns)


def test_broadcast_trackless_weights():
    """DV1 契约: 无 track 列 → 同一 W 对三轨广播。"""
    reg = mini_registry([entry("x")])
    meas = make_measures({"target_bank": ["A"], "year": [2017],
                          "x_full": [1.0], "x_ctx": [2.0], "x_ss": [3.0]})
    w = pd.DataFrame([("甲", "A", 2017, 5.0)], columns=["company", "bank", "year", "w"])
    out = eng.compute_weighted_panel(w, meas, reg)
    assert out.loc[("甲", 2017), "cw_x_full"] == 1.0
    assert out.loc[("甲", 2017), "cw_x_ctx"] == 2.0
    assert out.loc[("甲", 2017), "cw_x_ss"] == 3.0


# ---------------------------------------------------------------- PA semi-join 锁 ①
def test_pa_semijoin_lock():
    """① 16 号多余 docid (极端值) 不进 PA 聚合。"""
    reg = mini_registry([dict(basename="policy_cosine_sim", family="PA", source="16",
                              col_by_track={t: f"policy_cosine_sim_{t}" for t in mod.TRACKS},
                              track_agnostic=False, agg="mean", emit_tracks=list(mod.TRACKS),
                              emit_panel=True, cut_code=None, range_gate="none",
                              label_elems={}, short_name="polsim")])
    input21 = make_input([row(1, "银行A", "x", verified=True), row(2, "银行A", "x", verified=False)])
    align = pd.DataFrame({"docid": [1, 2, 3], "target_bank": ["银行A"] * 3,
                          **{f"policy_cosine_sim_{t}": [0.5, 99.0, 99.0] for t in mod.TRACKS}})
    lib = eng.build_measure_library(input21, pd.DataFrame({"target_bank": [], "year": []}),
                                    align, None, None, reg)
    col = "__agg16__policy_cosine_sim_full"
    assert lib.loc[("银行A", 2017), col] == 0.5  # docid 2 (unverified) 与 3 (16 号多余) 均不进


# ---------------------------------------------------------------- fail-loud 负例 ③
def test_year_range_systemexit():
    with pytest.raises(SystemExit):
        mod.main(["--year-min", "2020", "--year-max", "2018"])


def test_explicit_path_missing_systemexit(tmp_path):
    with pytest.raises(SystemExit):
        mod.main(["--input", str(tmp_path / "nope.parquet")])


def test_input_zero_rows_systemexit(tmp_path):
    p = tmp_path / "empty.parquet"
    pd.DataFrame({c: pd.Series(dtype="object") for c in eng.INPUT_COLS}).to_parquet(p)
    with pytest.raises(SystemExit):
        eng.load_input21(p, set())


def test_docid_null_systemexit(tmp_path):
    p = tmp_path / "nulldoc.parquet"
    df = pd.DataFrame({c: [None] for c in eng.INPUT_COLS})
    df["日期"] = ["2017-01-01"]
    df.to_parquet(p)
    with pytest.raises(SystemExit):
        eng.load_input21(p, set())


def test_bad_date_raises(tmp_path):
    p = tmp_path / "baddate.parquet"
    df = pd.DataFrame({c: ["x"] for c in eng.INPUT_COLS})
    df["docid"] = [1]
    df["日期"] = ["not-a-date"]
    df.to_parquet(p)
    with pytest.raises((ValueError, SystemExit)):
        eng.load_input21(p, {"x"})


def test_target_bank_outside_canonical_systemexit(tmp_path):
    p = tmp_path / "outside.parquet"
    df = pd.DataFrame({c: ["y"] for c in eng.INPUT_COLS})
    df["docid"] = [1]
    df["日期"] = ["2017-01-01"]
    df["target_bank"] = ["野银行"]
    df.to_parquet(p)
    with pytest.raises(SystemExit):
        eng.load_input21(p, {"正规银行"})


def test_abs_year_domain_systemexit():
    A = make_automaton(VO)
    rows = [row(i, "银行A", "甲税企", year=1970) for i in range(2000)]
    df = make_input(rows)
    hits = mod.scan_hits(df, A, {}, {})
    with pytest.raises(SystemExit):
        mod.build_year_map(hits)


def test_cross_year_warning(caplog):
    rows = [row(1, "银行A", "甲税企", year=2018), row(1, "银行B", "甲税企", year=2017)]
    A = make_automaton(VO)
    hits = mod.scan_hits(make_input(rows), A, {}, {})
    with caplog.at_level(logging.WARNING, logger="02_build_company_tax_bank_cooc_panel"):
        mod.build_year_map(hits)
    assert any("跨年" in r.message for r in caplog.records)


# ---------------------------------------------------------------- 标签
def test_labels_dual_gate():
    lbl = mod.make_label("cw", "avg_fintech_distinct_keywords", "full", "KW")
    assert len(lbl) <= 80 and len(lbl.encode("utf-8")) <= 320
    lbl2 = mod.make_label("cw", "x", "full", "Q", scheme_word="贷款")
    assert "贷款加权" in lbl2 and "共现" not in lbl2


# ---------------------------------------------------------------- 税调新增: usci 三联断言 (F1)
def test_usci_map_triple_invariant():
    """税调面板核心接入键 usci: 18 位全填 (str18) + 全唯一 + 非空 (F1 契约, 44,771 家)。
    直读 config/company_tax_names.yaml SSOT (只读, 不碰 company_tax_bank/data)。"""
    um = mod.usci_map()
    vals = list(um.values())
    assert len(vals) == 44771, f"税调名单家数 {len(vals)} ≠ 44,771 (F1)"
    assert all(isinstance(v, str) for v in vals), "usci 非字符串 (str 契约破)"
    assert all(len(v) == 18 for v in vals), "usci 长度 ≠ 18 (str18 契约破)"
    assert all(v and v.strip() for v in vals), "usci 空/纯空白 (F1 全填破)"
    assert len(set(vals)) == len(vals), "usci 非全局唯一 (F1 唯一破; usci×year merge 键前提)"


def test_write_outputs_emit_dta_flag(tmp_path):
    """WP-S3 (--no-emit-dta dev 快速模式): emit_dta=False → 只写 parquet 跳 dta; True (默认) → 双出;
    两模式 parquet 内容一致 (证 dta 门控不污染 parquet 伴生, 生产默认行为零变化)。"""
    um = mod.usci_map()
    name = next(iter(um))  # 真实税调企业名 → usci 契约 (str18/notna) 满足
    base_panel = pd.DataFrame({
        "company_tax_name": [name, name], "usci": [um[name], um[name]],
        "year": [2011, 2012], "rel_n_banks": [0, 1], "rel_hhi": [np.nan, 1.0],
        "cw_x_full": [np.nan, 0.5], "ce_x_full": [np.nan, 0.5]})
    reg = mini_registry([entry("x")])
    out_no = tmp_path / "p_nodta.dta"
    mod.write_outputs(base_panel.copy(), reg, out_no, emit_dta=False)
    assert not out_no.exists(), "emit_dta=False 仍写了 dta (WP-S3 门控失效)"
    assert out_no.with_suffix(".parquet").exists(), "emit_dta=False 未写 parquet (伴生须恒出)"
    out_yes = tmp_path / "p_dta.dta"
    mod.write_outputs(base_panel.copy(), reg, out_yes, emit_dta=True)
    assert out_yes.exists() and out_yes.with_suffix(".parquet").exists(), "emit_dta=True 应双出 dta+parquet"
    a = pd.read_parquet(out_no.with_suffix(".parquet"))
    b = pd.read_parquet(out_yes.with_suffix(".parquet"))
    pd.testing.assert_frame_equal(a, b)  # parquet 内容与 emit_dta 无关


# ---------------------------------------------------------------- WP-A log-clobber 防复发 gate
# (2026-07-07 日志审计: 负例测试调 main() 曾三次首写截断覆盖生产 02 日志; 守卫=PYTEST_CURRENT_TEST 早退)
# ⚠ 并发安全 (T-D18): 03 可能后台在写自身 03_*.log → 全目录 mtime 快照会被并发写污染。
# 故断言聚焦本模块自身 stem 日志 (守卫失效才会新建/截断它; 03 并发只 append 自身 log、不碰他 stem)
# + FileHandler 断言 (与并发完全无关的权威确证; 镜像 listed test 第二断言)。
@pytest.mark.parametrize("stem", [
    "01_build_company_tax_bank_cooc_registry",
    "02_build_company_tax_bank_cooc_panel",
    "03_build_company_tax_bank_weight_validation",
    "run_pipeline",
])
def test_pytest_never_touches_stage_logs(stem):
    """pytest 进程内调 _init_stage_logging 绝不接管/写 company_tax_bank/logs (四脚本逐一验)。"""
    assert os.environ.get("PYTEST_CURRENT_TEST"), "守卫前提失效: pytest 未设 PYTEST_CURRENT_TEST"
    m = mod if stem == "02_build_company_tax_bank_cooc_panel" else _load_tax_module(stem)
    stem_name = Path(m.__file__).stem
    logs_dir = Path(m.__file__).resolve().parent / "logs"
    stem_log = logs_dir / f"{stem_name}.log"
    existed = stem_log.exists()               # 只读 exists/stat (T-D18: pytest 绝不写该目录)
    size_before = stem_log.stat().st_size if existed else None
    m._init_stage_logging()  # 守卫在位 → 早退, 不 attach 文件 handler
    m.logger.warning("WP-A gate probe — 本行绝不应落盘")
    # 权威断言 (并发无关): 守卫在位 → 该 stem logger 不挂任何 FileHandler
    assert not any(  # mtime 快照可能被并发缓冲干扰, 故 handler 断言为主
        isinstance(h, logging.FileHandler) for h in logging.getLogger(stem_name).handlers
    ), f"pytest 进程内 logger {stem_name} 挂上了 FileHandler — 守卫失效"
    # 兜底 (并发安全): 守卫失效才会新建 (先前不存在) 或截断 (size 缩小) 本 stem 日志;
    # 03 并发只 append 自身 03_*.log (size 单调增, 且是不同 stem) → 本断言不误判并发写
    if not existed:
        assert not stem_log.exists(), f"pytest 新建了 {stem_log.name} — 守卫失效"
    else:
        assert stem_log.stat().st_size >= size_before, f"{stem_log.name} 被截断 — 守卫失效"


# ---------------------------------------------------------------- (B2) COOC_SPEEDUP 位级参照臂 gate
# 2026-07-07 引擎提速重构 (一次对齐 + int-codes 分组 + 宽内核) 的位级等价锁 (跨管道复用 listed 引擎):
# 生产路径 compute_weighted_panel 必须与冻结参照臂 _compute_weighted_panel_percol 逐位相等
# (含 ±0.0 符号位 — assert_frame_equal 分不出, 故加 uint 视图断言)。本 gate 存在即禁删参照臂。
def _assert_bitwise_equal(a: pd.DataFrame, b: pd.DataFrame):
    pd.testing.assert_frame_equal(a, b, check_exact=True)
    for c in a.columns:
        av, bv = a[c], b[c]
        dt = str(av.dtype)
        if dt in ("float64", "float32"):
            u = "uint64" if dt == "float64" else "uint32"
            assert np.array_equal(av.to_numpy().view(u), bv.to_numpy().view(u)), \
                f"float 位级分叉 (±0.0/NaN 位型): {c}"
        elif dt in ("Float64", "Float32", "Int64"):
            am, bm = av.array._mask, bv.array._mask
            assert np.array_equal(am, bm), f"nullable 掩码分叉: {c}"
            ad, bd = av.array._data, bv.array._data
            if ad.dtype.kind == "f":
                u = "uint64" if ad.dtype.itemsize == 8 else "uint32"
                assert np.array_equal(ad[~am].view(u), bd[~bm].view(u)), \
                    f"nullable float 位级分叉: {c}"
            else:
                assert np.array_equal(ad[~am], bd[~bm]), f"nullable int 值分叉: {c}"


def _speedup_case(seed: int, with_track: bool, unmatched: bool = True):
    """钉 seed 的随机样本, 覆盖 COOC_SPEEDUP G1③ 清单: 混 dtype (float64/float32/
    Float64/Float32/int64/Int64) / 缺源列 / track-agnostic / N=1 与 den>0 边界 /
    w=0 行 / 负值测度 / 含 NaN 列 / year=int32 探针 / 空轨 (with_track 时剔 ss) /
    unmatched=True 含未匹配 (bank,year) (升格分支), False 全匹配 (保源 dtype 分支,
    结果评审 F-3 补强)。"""
    rng = np.random.default_rng(seed)
    banks, years = list("ABCDE"), [2016, 2017, 2018]
    idx = pd.MultiIndex.from_product([banks, years], names=["target_bank", "year"])
    n = len(idx)

    def fcol(kind):
        v = rng.normal(0, 3, n)
        v[rng.random(n) < 0.35] = np.nan
        if kind == "float32":
            return v.astype("float32")
        if kind == "Float64":
            return pd.array([None if np.isnan(x) else x for x in v], dtype="Float64")
        return v

    meas = pd.DataFrame(index=idx)
    for base in ("x", "y"):
        for t in mod.TRACKS:
            meas[f"{base}_{t}"] = fcol("float64")
    for t in mod.TRACKS:
        meas[f"xf_{t}"] = fcol("float32")
        meas[f"xn_{t}"] = fcol("Float64")
        meas[f"xg_{t}"] = pd.array(
            [None if rng.random() < 0.3 else np.float32(v)
             for v in rng.normal(0, 2, n)], dtype="Float32")
        meas[f"xi_{t}"] = pd.array(rng.integers(-5, 5, n), dtype="int64")
        meas[f"xI_{t}"] = pd.array(
            [None if rng.random() < 0.3 else int(v) for v in rng.integers(0, 9, n)],
            dtype="Int64")
    meas["q"] = fcol("float64")
    reg = mini_registry([entry("x"), entry("y"), entry("xf"), entry("xn"),
                         entry("xg"), entry("xi"), entry("xI"),
                         entry("q", track_agnostic=True), entry("ghost")])
    rows = []
    tracks = list(mod.TRACKS) if with_track else [None]
    bank_pool = banks + ["Z"] if unmatched else banks   # Z → 未匹配银行
    year_pool = years + [2030] if unmatched else years  # 2030 → 未匹配年
    for t in tracks:
        for c in ["甲", "乙", "丙", "丁", "戊"]:
            k = int(rng.integers(1, 5))  # k=1 → N=1 短路面
            picks = rng.choice(bank_pool, size=k, replace=False)
            for b in picks:
                yv = int(rng.choice(year_pool))
                wv = float(rng.choice([0.0, 1.0, 2.5, 7.0]))  # 0.0 → den 边界
                rows.append((c, b, yv, t, wv))
    w = pd.DataFrame(rows, columns=["company", "bank", "year", "track", "w"])
    if with_track:
        w = w[w["track"] != "ss"]  # 空轨路径 (R2 P2-2 补列)
    else:
        w = w.drop(columns=["track"])
    w["year"] = w["year"].astype("int32")  # 生产 pair 实态: int32 vs 测度库 int64 (G1⑥)
    return w.reset_index(drop=True), meas, reg


@pytest.mark.parametrize("seed", [0, 1, 2])
@pytest.mark.parametrize("with_track", [True, False])
def test_engine_bitwise_equiv_percol(seed, with_track):
    """G1①②③: 生产路径 vs 冻结参照臂 逐位相等 (钉 seed 随机样本 ×6)。"""
    w, meas, reg = _speedup_case(seed, with_track)
    _assert_bitwise_equal(eng.compute_weighted_panel(w, meas, reg),
                          eng._compute_weighted_panel_percol(w, meas, reg))


@pytest.mark.parametrize("with_track", [True, False])
def test_engine_bitwise_equiv_no_unmatched(with_track):
    """G1③ 补强 (结果评审 F-3): 全匹配情形 — int/float32 列保源 dtype 分支的位级锁。"""
    w, meas, reg = _speedup_case(11, with_track, unmatched=False)
    _assert_bitwise_equal(eng.compute_weighted_panel(w, meas, reg),
                          eng._compute_weighted_panel_percol(w, meas, reg))


@pytest.mark.parametrize("chunk", [1, 3, 100])
def test_engine_chunk_invariance_bitwise(chunk):
    """G1④: chunk 划分只切"哪些列同批", 不改任何列的行集/行序 → 结果位级不随 chunk 变。"""
    w, meas, reg = _speedup_case(7, True)
    _assert_bitwise_equal(eng.compute_weighted_panel(w, meas, reg, chunk=chunk),
                          eng._compute_weighted_panel_percol(w, meas, reg))


def test_engine_mixed_n1_bitwise():
    """G1③ 混合 N=1 判别用例: 同组对列 x nvalid==1、对列 y nvalid>1 —
    掩码若误用单列命中集做全 chunk 掩码, 此例翻红。"""
    reg = mini_registry([entry("x"), entry("y")])
    meas = make_measures({"target_bank": ["A", "B"], "year": [2017] * 2,
                          "x_full": [4.25, np.nan], "y_full": [1.0, 2.0],
                          "x_ctx": [np.nan] * 2, "y_ctx": [np.nan] * 2,
                          "x_ss": [np.nan] * 2, "y_ss": [np.nan] * 2})
    w = wtab([("甲", "A", 2017, "full", 3), ("甲", "B", 2017, "full", 5)])
    out = eng.compute_weighted_panel(w, meas, reg)
    ref = eng._compute_weighted_panel_percol(w, meas, reg)
    _assert_bitwise_equal(out, ref)
    assert out.loc[("甲", 2017), "cw_x_full"] == 4.25  # N=1 短路取原值 (非 3*4.25/3 浮点路径)
    assert out.loc[("甲", 2017), "cw_y_full"] == pytest.approx((3 * 1 + 5 * 2) / 8)


def test_engine_duplicate_measure_key_raises():
    """G1⑤ 重复键负例: 新路径 fail-fast raise (参照臂保留 merge 静默扩张属刻意, 不测)。"""
    reg = mini_registry([entry("x")])
    meas = make_measures({"target_bank": ["A", "A"], "year": [2017, 2017],
                          "x_full": [1.0, 2.0], "x_ctx": [1.0, 2.0], "x_ss": [1.0, 2.0]})
    w = wtab([("甲", "A", 2017, "full", 1)])
    with pytest.raises(AssertionError, match="键重复"):
        eng.compute_weighted_panel(w, meas, reg)


# ---------------------------------------------------------------- 启动哈希锚复算闸 + 入口防御补全 (2026-07-07)
def test_registry_hash_tamper_systemexit(tmp_path):
    """手改 registry 内容而不改 meta.registry_sha256 → 02 启动复算即拒 (fail-closed,
    兑现 README/01 日志"启动校验哈希锚"承诺; 此前只查 n_entries≥600, 手改可静默跑通)。"""
    import yaml
    reg = yaml.safe_load((REPO / "config" / "company_tax_bank_cooc_registry.yaml")
                         .read_text(encoding="utf-8"))
    reg["entries"][0]["basename"] = reg["entries"][0]["basename"] + "_tampered"
    p = tmp_path / "tampered.yaml"
    p.write_text(yaml.safe_dump(reg, allow_unicode=True), encoding="utf-8")
    with pytest.raises(SystemExit, match="不自洽"):
        mod.main(["--registry", str(p)])


def test_pa_duplicate_keys_systemexit():
    """16 号 alignment 重复 (docid,target_bank) 键且值分歧 → fail-loud
    (语义镜像 21 号入口: 分歧才杀; inner merge 后 mean 会双计同篇且取值随行序漂移)。"""
    reg = mini_registry([dict(basename="policy_cosine_sim", family="PA", source="16",
                              col_by_track={t: f"policy_cosine_sim_{t}" for t in mod.TRACKS},
                              track_agnostic=False, agg="mean", emit_tracks=list(mod.TRACKS),
                              emit_panel=True, cut_code=None, range_gate="none",
                              label_elems={}, short_name="polsim")])
    input21 = make_input([row(1, "银行A", "x", verified=True)])
    align = pd.DataFrame({"docid": [1, 1], "target_bank": ["银行A"] * 2,
                          **{f"policy_cosine_sim_{t}": [0.5, 0.7] for t in mod.TRACKS}})
    with pytest.raises(SystemExit, match="重复键"):
        eng.build_measure_library(input21, pd.DataFrame({"target_bank": [], "year": []}),
                                  align, None, None, reg)


@pytest.mark.parametrize("col,vals", [("日期", ["2017-01-01", "2018-06-30"]),
                                      ("llm_verified_full", [True, False])])
def test_dedup_divergent_metadata_systemexit(tmp_path, col, vals):
    """(docid,target_bank) 重复行三轨文本一致但 日期/llm_verified_full 分歧 → fail-loud
    (keep='first' 下 _year 归年与 _v 口径会随读入序静默漂移 — 一致性闸原只锁三轨文本)。"""
    p = tmp_path / "dup_meta.parquet"
    df = pd.DataFrame({c: ["x", "x"] for c in eng.INPUT_COLS})
    df["docid"] = [1, 1]
    df["日期"] = ["2017-01-01"] * 2
    df["target_bank"] = ["正规银行"] * 2
    df["llm_verified_full"] = [True, True]
    df[col] = vals
    df.to_parquet(p)
    with pytest.raises(SystemExit, match="不一致"):
        eng.load_input21(p, {"正规银行"})


def test_dedup_identical_rows_pass(tmp_path):
    """正例对照: 重复行全字段一致 → 一致性闸放行, 去重后恰 1 行 (防新增两列误伤合法重复)。"""
    p = tmp_path / "dup_ok.parquet"
    df = pd.DataFrame({c: ["x", "x"] for c in eng.INPUT_COLS})
    df["docid"] = [1, 1]
    df["日期"] = ["2017-01-01"] * 2
    df["target_bank"] = ["正规银行"] * 2
    df["llm_verified_full"] = [True, True]
    df.to_parquet(p)
    out = eng.load_input21(p, {"正规银行"})
    assert len(out) == 1


def test_registry_missing_systemexit(tmp_path):
    """registry 文件缺失 → 显式 SystemExit 带排障指引 (非裸 FileNotFoundError)。"""
    with pytest.raises(SystemExit, match="registry 缺失"):
        mod.main(["--registry", str(tmp_path / "nonexistent.yaml")])


def test_pa_identical_duplicate_keys_dedup_pass():
    """正例对照: 16 号同值重复键 → 去重放行 (镜像 21 号语义), PA 均值不双计。"""
    reg = mini_registry([dict(basename="policy_cosine_sim", family="PA", source="16",
                              col_by_track={t: f"policy_cosine_sim_{t}" for t in mod.TRACKS},
                              track_agnostic=False, agg="mean", emit_tracks=list(mod.TRACKS),
                              emit_panel=True, cut_code=None, range_gate="none",
                              label_elems={}, short_name="polsim")])
    input21 = make_input([row(1, "银行A", "x", verified=True), row(2, "银行A", "y", verified=True)])
    align = pd.DataFrame({"docid": [1, 1, 2], "target_bank": ["银行A"] * 3,
                          **{f"policy_cosine_sim_{t}": [0.5, 0.5, 1.0] for t in mod.TRACKS}})
    lib = eng.build_measure_library(input21, pd.DataFrame({"target_bank": [], "year": []}),
                                    align, None, None, reg)
    # 同值重复 docid=1 去重后单计: mean(0.5, 1.0) = 0.75 (双计则为 (0.5+0.5+1.0)/3 ≈ 0.667)
    assert lib.loc[("银行A", 2017), "__agg16__policy_cosine_sim_full"] == pytest.approx(0.75)
