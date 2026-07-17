"""WP4 — 税调替代聚合权面板 (frozenw + mainbankw) 定向锁 (FROZEN_BASE_WEIGHTS_AND_MAINBANK v3)。

镜像 test_company_bank_altagg (税调 04 的纯函数系照搬母本 04 的独立副本, 须独立锁定);
mini_registry SSOT 复用; write_outputs 类用例用真实税调企业名 (usci 断言对合成名必崩)。
"""
from __future__ import annotations

import hashlib
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "company_listed_bank"))
sys.path.insert(0, str(REPO / "company_tax_bank"))
sys.path.insert(0, str(TESTS))

import importlib  # noqa: E402

mod04 = importlib.import_module("04_build_company_tax_bank_altagg_panels")
mod02t = importlib.import_module("02_build_company_tax_bank_cooc_panel")
import test_company_bank_cooc_panel as tp  # noqa: E402  (mini_registry/entry/make_measures SSOT)

pytestmark = pytest.mark.fast

TRACKS = mod04.TRACKS


def pairtab(rows):
    norm = [(r + (0,))[:6] for r in rows]
    df = pd.DataFrame(norm, columns=["company", "bank", "year", "track",
                                     "n_docs", "n_docs_longhit"])
    for c in ("year", "n_docs", "n_docs_longhit"):
        df[c] = df[c].astype("int32")
    return df


def engine_panel(weights, measures_data, bases=("x",)):
    reg = tp.mini_registry([tp.entry(b, track_agnostic=True) for b in bases])
    measures = tp.make_measures(measures_data)
    return mod02t.engine().compute_weighted_panel(weights, measures, reg), reg


def one(df, comp, year, col):
    m = (df[df.columns[0]] == comp) & (df["year"] == year)
    assert m.sum() == 1
    return df.loc[m, col].iloc[0]


# ---------------------------------------------------------------- (1) frozen: base_year 逐轨
def test_frozen_base_year_per_track_and_no_cross_track_leak():
    pair = pairtab([
        ("甲企业", "银行A", 2013, "full", 3),
        ("甲企业", "银行A", 2014, "ctx", 2),
        ("乙企业", "银行B", 2014, "ss", 1),
    ])
    w, diag, _ = mod04.build_frozen_weights(pair, 2015)
    d = diag.set_index(["company", "track"])
    assert d.loc[("甲企业", "full"), "base_year"] == 2013
    assert d.loc[("甲企业", "ctx"), "base_year"] == 2014
    assert ("乙企业", "full") not in d.index
    assert w[(w["company"] == "甲企业") & (w["track"] == "full")]["year"].tolist() == \
        [2013, 2014, 2015]
    # G1: 诊断宽表逐轨归位锁 (轨间错位=发布 dta 静默污染, 对称 fixture 探测不到 — R1 评审)
    fwide = mod04.frozen_diag_wide(diag, "company_tax_name")
    assert fwide.loc["甲企业", "base_year_full"] == 2013.0
    assert fwide.loc["甲企业", "base_year_ctx"] == 2014.0
    assert np.isnan(fwide.loc["甲企业", "base_year_ss"])
    assert np.isnan(fwide.loc["乙企业", "base_year_full"]) and fwide.loc["乙企业", "base_year_ss"] == 2014.0


# ---------------------------------------------------------------- (2) frozen: 左截断负例
def test_frozen_left_truncation_all_nan_no_fallback():
    pair = pairtab([("甲企业", "银行A", 2014, "full", 3)])
    w, diag, _ = mod04.build_frozen_weights(pair, 2015)
    assert (w["year"] >= 2014).all()
    weighted, _ = engine_panel(w, {"target_bank": ["银行A"] * 3, "year": [2013, 2014, 2015],
                                   "x": [0.9, 0.5, 0.7]})
    panel = mod04.assemble_panel(weighted, ["甲企业"], 2013, 2015, set(), "company_tax_name")
    fwide = mod04.frozen_diag_wide(diag, "company_tax_name")
    panel = panel.merge(fwide, how="left", left_on="company_tax_name", right_index=True)
    assert np.isnan(one(panel, "甲企业", 2013, "cw_x_full"))
    assert one(panel, "甲企业", 2014, "cw_x_full") == 0.5
    mod04.run_altagg_gates("frozenw", panel, w, 3, 2013, 2015)


# ---------------------------------------------------------------- (3) frozen: 解耦有值 + 第三通道
def test_frozen_zero_cooc_year_has_value_and_third_channel_nan():
    pair = pairtab([("甲企业", "银行A", 2013, "full", 3)])
    w, _, _ = mod04.build_frozen_weights(pair, 2015)
    weighted, _ = engine_panel(w, {"target_bank": ["银行A", "银行A"], "year": [2013, 2014],
                                   "x": [0.5, 0.8]})
    panel = mod04.assemble_panel(weighted, ["甲企业"], 2013, 2015, set(), "company_tax_name")
    assert one(panel, "甲企业", 2014, "cw_x_full") == 0.8
    assert np.isnan(one(panel, "甲企业", 2015, "cw_x_full"))


# ---------------------------------------------------------------- (4) frozen: 重归一手算
def test_frozen_renormalization_hand_calc():
    pair = pairtab([("甲企业", "银行A", 2013, "full", 3), ("甲企业", "银行B", 2013, "full", 1)])
    w, _, _ = mod04.build_frozen_weights(pair, 2014)
    weighted, _ = engine_panel(w, {
        "target_bank": ["银行A", "银行B", "银行A", "银行B"],
        "year": [2013, 2013, 2014, 2014],
        "x": [0.6, 0.2, 0.6, np.nan],
    })
    assert weighted.loc[("甲企业", 2013), "cw_x_full"] == pytest.approx((3 * .6 + 1 * .2) / 4)
    assert weighted.loc[("甲企业", 2014), "cw_x_full"] == pytest.approx(0.6)


# ---------------------------------------------------------------- (5) frozen: ce = 基期集合等权
def test_frozen_ce_is_base_set_equal_weight():
    pair = pairtab([("甲企业", "银行A", 2013, "full", 3), ("甲企业", "银行B", 2013, "full", 1),
                    ("甲企业", "银行C", 2014, "full", 9)])
    w, _, _ = mod04.build_frozen_weights(pair, 2014)
    weighted, _ = engine_panel(w, {
        "target_bank": ["银行A", "银行B", "银行C"], "year": [2014] * 3, "x": [0.6, 0.2, 0.9]})
    assert weighted.loc[("甲企业", 2014), "ce_x_full"] == pytest.approx(0.4)


# ---------------------------------------------------------------- (6) mainbank: 三级平票
def test_mainbank_three_level_tiebreak_and_flags():
    pair = pairtab([
        ("甲企业", "银行B", 2013, "full", 5, 0), ("甲企业", "银行A", 2013, "full", 3, 2),
        ("乙企业", "银行C", 2013, "full", 4, 1), ("乙企业", "银行D", 2013, "full", 4, 2),
        ("丙企业", "银行F", 2013, "full", 2, 1), ("丙企业", "银行E", 2013, "full", 2, 1),
        # G1: ctx 轨异银行, 锁诊断宽表逐轨归位
        ("甲企业", "银行Z", 2013, "ctx", 1, 0),
    ])
    w, win = mod04.build_mainbank_weights(pair)
    v = win.set_index(["company", "track"])
    assert v.loc[("甲企业", "full"), "bank"] == "银行B" and v.loc[("甲企业", "full"), "main_bank_tie"] == 0.0
    assert v.loc[("乙企业", "full"), "bank"] == "银行D" and v.loc[("乙企业", "full"), "main_bank_tie"] == 1.0
    assert v.loc[("乙企业", "full"), "name_order_decisive"] == 0.0
    assert v.loc[("丙企业", "full"), "bank"] == "银行E" and v.loc[("丙企业", "full"), "name_order_decisive"] == 1.0
    assert v.loc[("甲企业", "full"), "main_bank_share"] == pytest.approx(5 / 8)
    assert (w["w"] == 1.0).all() and len(w) == 4
    # G1: 诊断宽表逐轨归位
    mwide = mod04.mainbank_diag_wide(win, "company_tax_name")
    assert mwide.loc[("甲企业", 2013), "main_bank_full"] == "银行B"
    assert mwide.loc[("甲企业", 2013), "main_bank_ctx"] == "银行Z"
    assert mwide.loc[("甲企业", 2013), "main_bank_ss"] == ""


# ---------------------------------------------------------------- (6a) frozen: 窗末年基期退化 ≡ cw
def test_frozen_base_year_at_window_end_equals_current_cw():
    pair = pairtab([("甲企业", "银行A", 2015, "full", 3), ("甲企业", "银行B", 2015, "full", 1)])
    fw, _, _ = mod04.build_frozen_weights(pair, 2015)
    cur = pair.rename(columns={"n_docs": "w"})[["company", "bank", "year", "track", "w"]]
    md = {"target_bank": ["银行A", "银行B"], "year": [2015, 2015], "x": [0.6, 0.2]}
    frozen_w, _ = engine_panel(fw, md)
    current_w, _ = engine_panel(cur, md)
    assert frozen_w.loc[("甲企业", 2015), "cw_x_full"] == current_w.loc[("甲企业", 2015), "cw_x_full"]


# ---------------------------------------------------------------- (7) mainbank: cw ≡ ce 逐位
def test_mainbank_cw_ce_bitwise_identical_including_nan():
    pair = pairtab([("甲企业", "银行A", 2013, "full", 5), ("甲企业", "银行B", 2013, "full", 2),
                    ("乙企业", "银行C", 2013, "full", 1)])
    w, _ = mod04.build_mainbank_weights(pair)
    weighted, _ = engine_panel(w, {"target_bank": ["银行A", "银行B"], "year": [2013, 2013],
                                   "x": [0.7, 0.1]})
    cw, ce = weighted["cw_x_full"], weighted["ce_x_full"]
    assert ((cw.isna() & ce.isna()) | (cw == ce)).all()
    assert weighted.loc[("甲企业", 2013), "cw_x_full"] == 0.7
    assert np.isnan(weighted.loc[("乙企业", 2013), "cw_x_full"])


# ---------------------------------------------------------------- (8) mainbank: 严格 top-1 负例
def test_mainbank_strict_nan_no_second_place_fallback():
    pair = pairtab([("甲企业", "银行A", 2013, "full", 5), ("甲企业", "银行B", 2013, "full", 2)])
    w, win = mod04.build_mainbank_weights(pair)
    assert win["bank"].iloc[0] == "银行A"
    weighted, _ = engine_panel(w, {"target_bank": ["银行B"], "year": [2013], "x": [0.3]})
    assert np.isnan(weighted.loc[("甲企业", 2013), "cw_x_full"])


# ---------------------------------------------------------------- (9) 缺失语义 + 满骨架
def test_skeleton_full_grid_and_nan_semantics():
    pair = pairtab([("甲企业", "银行A", 2014, "full", 3)])
    w, _, _ = mod04.build_frozen_weights(pair, 2015)
    weighted, _ = engine_panel(w, {"target_bank": ["银行A"], "year": [2014], "x": [0.5]})
    comps = sorted(["甲企业", "乙企业"])
    panel = mod04.assemble_panel(weighted, comps, 2013, 2015, {"乙企业"}, "company_tax_name")
    assert len(panel) == 2 * 3
    assert panel["year"].dtype == np.dtype("int16")
    zb = panel[panel["company_tax_name"] == "乙企业"]
    assert zb["cw_x_full"].isna().all()
    assert (zb["is_bank_company"] == 1).all()
    assert one(panel, "甲企业", 2014, "cw_x_full") == 0.5


# ---------------------------------------------------------------- (10) 确定性 + weights 键唯一
def test_determinism_double_run_and_uniqueness_gate():
    pair = pairtab([("甲企业", "银行B", 2013, "full", 2, 1), ("甲企业", "银行A", 2013, "full", 2, 1),
                    ("乙企业", "银行C", 2014, "ctx", 4)])
    h = []
    for _ in range(2):
        fw, fd, fl = mod04.build_frozen_weights(pair, 2015)
        mw, win = mod04.build_mainbank_weights(pair)
        blob = b"".join(pd.util.hash_pandas_object(x, index=False).to_numpy().tobytes()
                        for x in (fw, fd, fl, mw, win[["company", "bank", "year", "track"]]))
        h.append(hashlib.sha256(blob).hexdigest())
    assert h[0] == h[1]  # (G4: 含 flong 重构载体)
    assert (fl["base_year"] <= fl["year"]).all()  # G4: 载体 base_year/year 赋值不错序
    assert not mw.duplicated(subset=["company", "bank", "year", "track"]).any()
    dup = pd.concat([mw, mw])
    panel = pd.DataFrame({"company_tax_name": ["甲企业"], "year": [2013]})
    with pytest.raises(AssertionError, match="键重复"):
        mod04.run_altagg_gates("mainbankw", panel, dup, 1, 2013, 2015)


# ---------------------------------------------------------------- (11) 列名双射 + 诊断列约束
def test_column_bijection_and_diag_name_limits():
    pair = pairtab([("甲企业", "银行A", 2013, t, 3) for t in TRACKS])
    w, diag, _ = mod04.build_frozen_weights(pair, 2014)
    weighted, reg = engine_panel(w, {"target_bank": ["银行A"], "year": [2013], "x": [0.5]})
    expect = {f"{arm}_x_{t}" for arm in ("cw", "ce") for t in TRACKS}
    assert set(weighted.columns) == expect
    fwide = mod04.frozen_diag_wide(diag, "company_tax_name")
    _, win = mod04.build_mainbank_weights(pair)
    mwide = mod04.mainbank_diag_wide(win, "company_tax_name")
    for c in list(fwide.columns) + list(mwide.columns):
        assert len(c) <= 32
    for t in TRACKS:
        assert fwide[f"base_year_{t}"].dtype == np.dtype("float64")
        assert mwide[f"main_bank_{t}"].dtype == object


# ---------------------------------------------------------------- (12) 原子写 + emit_dta + 守卫
def test_write_outputs_atomic_emit_dta_and_pytest_guard(tmp_path):
    comp = mod02t.tax_companies()[0]["company_tax_name"]  # 名单 SSOT 函数 (模块级缓存)
    reg = tp.mini_registry([tp.entry("x", track_agnostic=True)])
    panel = pd.DataFrame({"company_tax_name": [comp], "year": np.array([2013], dtype="int16"),
                          "is_bank_company": np.array([0], dtype="int8"),
                          "cw_x_full": [0.5], "ce_x_full": [0.5]})
    out = tmp_path / "company_tax_bank_frozenw_panel.dta"
    mod02t.write_outputs(panel, reg, out, scheme_word="基期冻结",
                         fixed_labels={"company_tax_name": "税调企业名称 (全称)"}, emit_dta=True)
    assert out.exists() and out.with_suffix(".parquet").exists()
    assert not list(tmp_path.glob("*.tmp"))
    # --no-emit-dta 语义 (WP-S3): dta 跳过且陈旧 dta 被清除, parquet 照写
    mod02t.write_outputs(panel, reg, out, scheme_word="基期冻结",
                         fixed_labels={"company_tax_name": "税调企业名称 (全称)"}, emit_dta=False)
    assert not out.exists() and out.with_suffix(".parquet").exists()
    mod04._init_stage_logging()
    assert not any(isinstance(h, logging.FileHandler) for h in mod04.logger.handlers)


# ---------------------------------------------------------------- (13) registry sha 锚不变
def test_registry_sha_anchor_unchanged():
    import test_company_tax_bank_cooc_registry as treg
    import yaml as _yaml
    disk = _yaml.safe_load((REPO / "config" / "company_tax_bank_cooc_registry.yaml")
                           .read_text(encoding="utf-8"))["meta"]["registry_sha256"]
    assert disk in treg.FROZEN_TAX_REGISTRY_SHAS


# ---------------------------------------------------------------- (14) _upsert_section 三义务
def test_upsert_section_idempotent_preserves_others_appends(tmp_path):
    cb = tmp_path / "codebook.md"
    b03 = "<!-- BEGIN 双替代权面板章 (03 生成, 勿手改) -->"
    e03 = "<!-- END 双替代权面板章 -->"
    cb.write_text(f"# 头部\n\n{b03}\n03 章内容甲\n{e03}\n", encoding="utf-8")
    B, E = mod04.CODEBOOK_ALTAGG_BEGIN, mod04.CODEBOOK_ALTAGG_END
    mod04._upsert_section(cb, "04 章 v1", B, E)
    t1 = cb.read_text(encoding="utf-8")
    assert t1.count(B) == 1 and f"{b03}\n03 章内容甲\n{e03}" in t1
    mod04._upsert_section(cb, "04 章 v2", B, E)
    t2 = cb.read_text(encoding="utf-8")
    assert t2.count(B) == 1 and "04 章 v2" in t2 and "04 章 v1" not in t2
    assert f"{b03}\n03 章内容甲\n{e03}" in t2
