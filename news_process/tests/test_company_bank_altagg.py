"""WP4 — 替代聚合权面板 (frozenw + mainbankw) 定向锁 (FROZEN_BASE_WEIGHTS_AND_MAINBANK v3)。

全合成 fixture (mini_registry SSOT 复用自 test_company_bank_cooc_panel), 直接调 04 的 build_*
纯函数绕过 main() 的 sha 复算/pair metadata 闸; write_outputs 类用例豁免 mock 用真实名单公司名
(stock_code notna 断言对合成名必崩, 计划 R2-P2-5)。
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
sys.path.insert(0, str(TESTS))

import importlib  # noqa: E402

mod04 = importlib.import_module("04_build_company_bank_altagg_panels")
mod02 = importlib.import_module("02_build_company_bank_cooc_panel")
import test_company_bank_cooc_panel as tp  # noqa: E402  (mini_registry/entry/make_measures SSOT)

pytestmark = pytest.mark.fast

TRACKS = mod04.TRACKS


# ---------------------------------------------------------------- fixture 工具
def pairtab(rows):
    """rows: (company, bank, year, track, n_docs[, n_docs_longhit])。dtype 对齐真 pair 表 (int32)。"""
    norm = [(r + (0,))[:6] for r in rows]
    df = pd.DataFrame(norm, columns=["company", "bank", "year", "track",
                                     "n_docs", "n_docs_longhit"])
    for c in ("year", "n_docs", "n_docs_longhit"):
        df[c] = df[c].astype("int32")
    return df


def engine_panel(weights, measures_data, bases=("x",)):
    reg = tp.mini_registry([tp.entry(b, track_agnostic=True) for b in bases])
    measures = tp.make_measures(measures_data)
    return mod02.compute_weighted_panel(weights, measures, reg), reg


def one(df, comp, year, col):
    m = (df[df.columns[0]] == comp) & (df["year"] == year)
    assert m.sum() == 1
    return df.loc[m, col].iloc[0]


# ---------------------------------------------------------------- (1) frozen: base_year 逐轨
def test_frozen_base_year_per_track_and_no_cross_track_leak():
    pair = pairtab([
        ("甲公司", "银行A", 2017, "full", 3),
        ("甲公司", "银行A", 2018, "ctx", 2),   # ctx 轨基期晚一年
        ("乙公司", "银行B", 2018, "ss", 1),    # 仅 ss 轨有共现的公司
    ])
    w, diag, _ = mod04.build_frozen_weights(pair, 2019)
    d = diag.set_index(["company", "track"])
    assert d.loc[("甲公司", "full"), "base_year"] == 2017
    assert d.loc[("甲公司", "ctx"), "base_year"] == 2018  # 跨轨不同 base_year
    assert ("乙公司", "full") not in d.index  # 无共现轨不产 base_year, 不连坐
    assert ("乙公司", "ss") in d.index
    # 展年: 甲 full 2017–2019 三年 / 甲 ctx 2018–2019 两年
    yrs = w[(w["company"] == "甲公司") & (w["track"] == "full")]["year"].tolist()
    assert yrs == [2017, 2018, 2019]
    assert w[(w["company"] == "甲公司") & (w["track"] == "ctx")]["year"].tolist() == [2018, 2019]
    # G1: 诊断宽表逐轨归位锁 (轨间错位=发布 dta 静默污染, 对称 fixture 探测不到 — R1 评审)
    fwide = mod04.frozen_diag_wide(diag, "company_listed_name")
    assert fwide.loc["甲公司", "base_year_full"] == 2017.0
    assert fwide.loc["甲公司", "base_year_ctx"] == 2018.0
    assert np.isnan(fwide.loc["甲公司", "base_year_ss"])
    assert np.isnan(fwide.loc["乙公司", "base_year_full"]) and fwide.loc["乙公司", "base_year_ss"] == 2018.0


# ---------------------------------------------------------------- (2) frozen: 左截断负例
def test_frozen_left_truncation_all_nan_no_fallback():
    pair = pairtab([("甲公司", "银行A", 2018, "full", 3)])  # 基期 2018, 窗 2017–2019
    w, diag, _ = mod04.build_frozen_weights(pair, 2019)
    assert (w["year"] >= 2018).all()  # t<base_year 不入 frame = 左截断
    weighted, _ = engine_panel(w, {"target_bank": ["银行A"] * 3, "year": [2017, 2018, 2019],
                                   "x": [0.9, 0.5, 0.7]})
    panel = mod04.assemble_panel(weighted, ["甲公司"], 2017, 2019, set(), "company_listed_name")
    fwide = mod04.frozen_diag_wide(diag, "company_listed_name")
    panel = panel.merge(fwide, how="left", left_on="company_listed_name", right_index=True)
    # 负例: 2017 银行A 测度存在 (0.9) — 若静默回退当期权重, 该格会有值; 左截断必须 NaN
    assert np.isnan(one(panel, "甲公司", 2017, "cw_x_full"))
    assert one(panel, "甲公司", 2018, "cw_x_full") == 0.5
    mod04.run_altagg_gates("frozenw", panel, w, 3, 2017, 2019)  # 左截断 gate 自身可过


# ---------------------------------------------------------------- (3) frozen: 解耦有值 + 第三缺失通道
def test_frozen_zero_cooc_year_has_value_and_third_channel_nan():
    pair = pairtab([("甲公司", "银行A", 2017, "full", 3)])
    w, _, _ = mod04.build_frozen_weights(pair, 2019)
    # 2018 无当年共现仍有值 (解耦); 2019 银行A 退出测度面板 → NaN (第三缺失通道)
    weighted, _ = engine_panel(w, {"target_bank": ["银行A", "银行A"], "year": [2017, 2018],
                                   "x": [0.5, 0.8]})
    panel = mod04.assemble_panel(weighted, ["甲公司"], 2017, 2019, set(), "company_listed_name")
    assert one(panel, "甲公司", 2018, "cw_x_full") == 0.8   # 零共现年解耦有值
    assert np.isnan(one(panel, "甲公司", 2019, "cw_x_full"))  # 冻结集合测度全缺 → NaN


# ---------------------------------------------------------------- (4) frozen: 重归一手算
def test_frozen_renormalization_hand_calc():
    pair = pairtab([("甲公司", "银行A", 2017, "full", 3), ("甲公司", "银行B", 2017, "full", 1)])
    w, _, _ = mod04.build_frozen_weights(pair, 2018)
    weighted, _ = engine_panel(w, {
        "target_bank": ["银行A", "银行B", "银行A", "银行B"],
        "year": [2017, 2017, 2018, 2018],
        "x": [0.6, 0.2, 0.6, np.nan],  # 2018 银行B 缺 → 冻结集合内限非缺失重归一
    })
    assert weighted.loc[("甲公司", 2017), "cw_x_full"] == pytest.approx((3 * .6 + 1 * .2) / 4)
    assert weighted.loc[("甲公司", 2018), "cw_x_full"] == pytest.approx(0.6)  # 重归一到银行A


# ---------------------------------------------------------------- (5) frozen: ce = 基期集合等权
def test_frozen_ce_is_base_set_equal_weight():
    pair = pairtab([("甲公司", "银行A", 2017, "full", 3), ("甲公司", "银行B", 2017, "full", 1),
                    ("甲公司", "银行C", 2018, "full", 9)])  # 银行C 2018 才共现, 不入基期集合
    w, _, _ = mod04.build_frozen_weights(pair, 2018)
    weighted, _ = engine_panel(w, {
        "target_bank": ["银行A", "银行B", "银行C"], "year": [2018] * 3, "x": [0.6, 0.2, 0.9]})
    # ce = 基期集合 {A,B} 等权 = 0.4 (主面板当年 ce 会含 C ≠ 本值 — 独立稳健臂)
    assert weighted.loc[("甲公司", 2018), "ce_x_full"] == pytest.approx(0.4)
    assert 0.9 not in (weighted.loc[("甲公司", 2018), "cw_x_full"],)  # C 不入冻结权重


# ---------------------------------------------------------------- (6) mainbank: 三级平票
def test_mainbank_three_level_tiebreak_and_flags():
    pair = pairtab([
        # 格1: n_docs 直接分出 (5>3), 无平票
        ("甲公司", "银行B", 2017, "full", 5, 0), ("甲公司", "银行A", 2017, "full", 3, 2),
        # 格2: n_docs 平 (4=4), longhit 裁决 (2>1)
        ("乙公司", "银行C", 2017, "full", 4, 1), ("乙公司", "银行D", 2017, "full", 4, 2),
        # 格3: 双平, 名序裁决 (码点 银行E < 银行F)
        ("丙公司", "银行F", 2017, "full", 2, 1), ("丙公司", "银行E", 2017, "full", 2, 1),
        # G1: ctx 轨异银行, 锁诊断宽表逐轨归位
        ("甲公司", "银行Z", 2017, "ctx", 1, 0),
    ])
    w, win = mod04.build_mainbank_weights(pair)
    v = win.set_index(["company", "track"])
    assert v.loc[("甲公司", "full"), "bank"] == "银行B" and v.loc[("甲公司", "full"), "main_bank_tie"] == 0.0
    assert v.loc[("乙公司", "full"), "bank"] == "银行D" and v.loc[("乙公司", "full"), "main_bank_tie"] == 1.0
    assert v.loc[("乙公司", "full"), "name_order_decisive"] == 0.0  # 二级已裁决
    assert v.loc[("丙公司", "full"), "bank"] == "银行E" and v.loc[("丙公司", "full"), "name_order_decisive"] == 1.0
    assert v.loc[("甲公司", "full"), "main_bank_share"] == pytest.approx(5 / 8)
    assert (w["w"] == 1.0).all() and len(w) == 4  # 每格单行 (full 三格 + ctx 一格)
    # G1: 诊断宽表逐轨归位 (full 与 ctx 各归其轨, ss 缺→空串)
    mwide = mod04.mainbank_diag_wide(win, "company_listed_name")
    assert mwide.loc[("甲公司", 2017), "main_bank_full"] == "银行B"
    assert mwide.loc[("甲公司", 2017), "main_bank_ctx"] == "银行Z"
    assert mwide.loc[("甲公司", 2017), "main_bank_ss"] == ""


# ---------------------------------------------------------------- (6a) frozen: 窗末年基期退化 ≡ cw
def test_frozen_base_year_at_window_end_equals_current_cw():
    pair = pairtab([("甲公司", "银行A", 2019, "full", 3), ("甲公司", "银行B", 2019, "full", 1)])
    fw, _, _ = mod04.build_frozen_weights(pair, 2019)  # 基期=窗末年 → 单年
    cur = pair.rename(columns={"n_docs": "w"})[["company", "bank", "year", "track", "w"]]
    md = {"target_bank": ["银行A", "银行B"], "year": [2019, 2019], "x": [0.6, 0.2]}
    frozen_w, _ = engine_panel(fw, md)
    current_w, _ = engine_panel(cur, md)
    assert frozen_w.loc[("甲公司", 2019), "cw_x_full"] == current_w.loc[("甲公司", 2019), "cw_x_full"]


# ---------------------------------------------------------------- (7) mainbank: cw ≡ ce 逐位
def test_mainbank_cw_ce_bitwise_identical_including_nan():
    pair = pairtab([("甲公司", "银行A", 2017, "full", 5), ("甲公司", "银行B", 2017, "full", 2),
                    ("乙公司", "银行C", 2017, "full", 1)])
    w, _ = mod04.build_mainbank_weights(pair)
    weighted, _ = engine_panel(w, {"target_bank": ["银行A", "银行B"], "year": [2017, 2017],
                                   "x": [0.7, 0.1]})  # 银行C 无测度 → 乙公司两臂同步 NaN
    cw, ce = weighted["cw_x_full"], weighted["ce_x_full"]
    same = (cw.isna() & ce.isna()) | (cw == ce)
    assert same.all()
    assert weighted.loc[("甲公司", 2017), "cw_x_full"] == 0.7  # = X_main 逐位 (非 share 加权)
    assert np.isnan(weighted.loc[("乙公司", 2017), "cw_x_full"])


# ---------------------------------------------------------------- (8) mainbank: 严格 top-1 负例
def test_mainbank_strict_nan_no_second_place_fallback():
    pair = pairtab([("甲公司", "银行A", 2017, "full", 5), ("甲公司", "银行B", 2017, "full", 2)])
    w, win = mod04.build_mainbank_weights(pair)
    assert win["bank"].iloc[0] == "银行A"
    weighted, _ = engine_panel(w, {"target_bank": ["银行B"], "year": [2017], "x": [0.3]})
    # main bank 银行A 测度缺、次位银行B 有值 (0.3) — 严格 top-1 必须 NaN, 禁顺延
    assert np.isnan(weighted.loc[("甲公司", 2017), "cw_x_full"])


# ---------------------------------------------------------------- (9) 缺失语义 + 满骨架
def test_skeleton_full_grid_and_nan_semantics():
    pair = pairtab([("甲公司", "银行A", 2018, "full", 3)])
    w, diag, _ = mod04.build_frozen_weights(pair, 2019)
    weighted, _ = engine_panel(w, {"target_bank": ["银行A"], "year": [2018], "x": [0.5]})
    comps = sorted(["甲公司", "乙公司"])  # 乙公司全轨零共现
    panel = mod04.assemble_panel(weighted, comps, 2017, 2019, {"乙公司"}, "company_listed_name")
    assert len(panel) == 2 * 3  # 满骨架
    assert panel["year"].dtype == np.dtype("int16")
    zb = panel[panel["company_listed_name"] == "乙公司"]
    assert zb["cw_x_full"].isna().all()  # 全零公司整行 NaN, 非 0
    assert (zb["is_bank_company"] == 1).all()
    assert one(panel, "甲公司", 2018, "cw_x_full") == 0.5


# ---------------------------------------------------------------- (10) 确定性 + weights 键唯一
def test_determinism_double_run_and_uniqueness_gate():
    pair = pairtab([("甲公司", "银行B", 2017, "full", 2, 1), ("甲公司", "银行A", 2017, "full", 2, 1),
                    ("乙公司", "银行C", 2018, "ctx", 4)])
    h = []
    for _ in range(2):
        fw, fd, fl = mod04.build_frozen_weights(pair, 2019)
        mw, win = mod04.build_mainbank_weights(pair)
        blob = b"".join(pd.util.hash_pandas_object(x, index=False).to_numpy().tobytes()
                        for x in (fw, fd, fl, mw, win[["company", "bank", "year", "track"]]))
        h.append(hashlib.sha256(blob).hexdigest())
    assert h[0] == h[1]  # 同输入双跑列内容哈希恒等 (G4: 含 flong 重构载体)
    assert (fl["base_year"] <= fl["year"]).all()  # G4: 载体 base_year/year 赋值不错序
    for frame in (fw, mw):
        assert not frame.duplicated(subset=["company", "bank", "year", "track"]).any()
    dup = pd.concat([mw, mw])  # 负例: 键重复必须被 gate 拦截
    panel = pd.DataFrame({"company_listed_name": ["甲公司"], "year": [2017]})
    with pytest.raises(AssertionError, match="键重复"):
        mod04.run_altagg_gates("mainbankw", panel, dup, 1, 2017, 2019)


# ---------------------------------------------------------------- (11) 列名双射 + 诊断列约束
def test_column_bijection_and_diag_name_limits():
    pair = pairtab([("甲公司", "银行A", 2017, t, 3) for t in TRACKS])
    w, diag, _ = mod04.build_frozen_weights(pair, 2018)
    weighted, reg = engine_panel(w, {"target_bank": ["银行A"], "year": [2017], "x": [0.5]})
    expect = {f"{arm}_x_{t}" for arm in ("cw", "ce") for t in TRACKS}
    assert set(weighted.columns) == expect  # registry emit × 轨 × 臂 双射
    fwide = mod04.frozen_diag_wide(diag, "company_listed_name")
    _, win = mod04.build_mainbank_weights(pair)
    mwide = mod04.mainbank_diag_wide(win, "company_listed_name")
    for c in list(fwide.columns) + list(mwide.columns):
        assert len(c) <= 32  # dta 变量名硬限
    for t in TRACKS:
        assert fwide[f"base_year_{t}"].dtype == np.dtype("float64")
        assert mwide[f"main_bank_{t}"].dtype == object  # str 列, 缺失=空串


# ---------------------------------------------------------------- (12) 原子写 + PYTEST 守卫
def test_write_outputs_atomic_and_pytest_guard(tmp_path):
    import yaml as _yaml
    comp = _yaml.safe_load((REPO / "config" / "company_listed_names.yaml")
                           .read_text(encoding="utf-8"))["companies"][0]["company_listed_name"]
    reg = tp.mini_registry([tp.entry("x", track_agnostic=True)])
    panel = pd.DataFrame({"company_listed_name": [comp], "year": np.array([2017], dtype="int16"),
                          "is_bank_company": np.array([0], dtype="int8"),
                          "cw_x_full": [0.5], "ce_x_full": [0.5]})
    out = tmp_path / "company_bank_frozenw_panel.dta"
    mod02.write_outputs(panel, reg, out, scheme_word="基期冻结",
                        fixed_labels={"company_listed_name": "上市公司中文全称"})
    assert out.exists() and out.with_suffix(".parquet").exists()
    assert not list(tmp_path.glob("*.tmp"))  # 原子写无 .tmp 残留
    mod04._init_stage_logging()  # pytest 下须直接返回, 不接管文件日志
    assert not any(isinstance(h, logging.FileHandler) for h in mod04.logger.handlers)


# ---------------------------------------------------------------- (13) registry sha 锚不变
def test_registry_sha_anchor_unchanged():
    import test_company_bank_cooc_registry as treg
    import yaml as _yaml
    disk = _yaml.safe_load((REPO / "config" / "company_bank_cooc_registry.yaml")
                           .read_text(encoding="utf-8"))["meta"]["registry_sha256"]
    assert disk == treg.EXPECTED_REGISTRY_SHA256  # 04 零 registry 改动, 锚不 bump
    # G3: listed 04 年窗字面量是 02/03 argparse 默认的第三副本, 锚死防漂移
    assert (mod04.PANEL_YEAR_MIN, mod04.PANEL_YEAR_MAX) == (2007, 2025)


# ---------------------------------------------------------------- (14) _upsert_section 三义务
def test_upsert_section_idempotent_preserves_others_appends(tmp_path):
    cb = tmp_path / "codebook.md"
    b03 = "<!-- BEGIN 七替代权面板章 (WP5 生成, 勿手改) -->"
    e03 = "<!-- END 七替代权面板章 -->"
    original = f"# 头部\n\n{b03}\n03 章内容甲\n{e03}\n"
    cb.write_text(original, encoding="utf-8")
    B, E = mod04.CODEBOOK_ALTAGG_BEGIN, mod04.CODEBOOK_ALTAGG_END
    mod04._upsert_section(cb, "04 章 v1", B, E)  # 无标记 → append 到尾
    t1 = cb.read_text(encoding="utf-8")
    assert t1.count(B) == 1 and "04 章 v1" in t1
    assert f"{b03}\n03 章内容甲\n{e03}" in t1  # 03 块逐字节保全
    assert t1.index(b03) < t1.index(B)
    mod04._upsert_section(cb, "04 章 v2", B, E)  # 幂等双跑 → 仅一块且内容替换
    t2 = cb.read_text(encoding="utf-8")
    assert t2.count(B) == 1 and t2.count(E) == 1
    assert "04 章 v2" in t2 and "04 章 v1" not in t2
    assert f"{b03}\n03 章内容甲\n{e03}" in t2
