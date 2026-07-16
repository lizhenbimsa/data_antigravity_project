#!/usr/bin/env python3
"""步骤 04: 替代聚合权面板 — frozenw 基期冻结权重 + mainbankw top-1 主办银行 (WP1)。

计划 SSOT = scripts/audit/FROZEN_BASE_WEIGHTS_AND_MAINBANK_EXECUTION_PLAN_2026-07-10.md (v3)。
输入 = 02 pair 长表 (metadata stale 校验) + 五上游测度 (与 02 同源同读法) + registry (只读, 零改动零 bump)。
输出 = company_bank_{frozenw,mainbankw}_panel.{dta,parquet} + _company_bank_altagg_{frozen,mainbank}.parquet
     + codebook「替代聚合面板章」(自带参数化 _upsert_section, 幂等)。

两 scheme 与主 cw 各差恰一个自由度 (D2/D3): frozenw 只动权重时点 (GPSS initial-share, 基期份额冻结,
左截断不回退), mainbankw 只动聚合函数 (当年 n_docs argmax, 三级确定性平票, 严格 top-1 测度缺失不顺延)。
own-bank 处置四臂同源 (pair 长表上游 02 D4 已剔自身银行, 本步零特判)。
铁律: 与既有八权/三轨/cw-ce 两臂互为稳健性、不分主次, 各自 just-identified 并排,
禁混同一 over-identified Hansen J、禁面板横向 merge、禁同一 RHS 并置 (horse-race 显式标注豁免)。
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT_DATA = HERE / "data"
TRACKS = ("full", "ctx", "ss")
# 面板年窗 (WP1.5a): 02/03 argparse 默认的第三副本 (listed 侧无模块常量可 import; ABS≡PANEL);
# ⚠ 禁从 pair 数据推年窗 (dev pair max=2018, 推导必产窄面板)。
PANEL_YEAR_MIN, PANEL_YEAR_MAX = 2007, 2025

CODEBOOK_ALTAGG_BEGIN = "<!-- BEGIN 替代聚合面板章 (04 生成, 勿手改) -->"
CODEBOOK_ALTAGG_END = "<!-- END 替代聚合面板章 -->"

logger = logging.getLogger("04_build_company_bank_altagg_panels")
if not logger.handlers:  # console 兜底 (被测试/importlib 导入时); main() 实跑时由 setup_logging 接管
    _h = logging.StreamHandler(sys.stdout)
    _h.setFormatter(logging.Formatter("[altagg_panel] %(levelname)s %(message)s"))
    _h.setLevel(logging.INFO)
    logger.addHandler(_h)
    logger.setLevel(logging.INFO)


# ---------------------------------------------------------------- 步骤 02 引擎载入 (D1, importlib 单例)
_WP1 = None


def wp1():
    """listed 02 模块 (importlib 惰性单例): 加权引擎/write_outputs/五上游载入 SSOT 函数, 只读复用,
    管道内禁重抄。序号前缀模块名非法 import 标识符 → importlib (镜像 03 惯例)。"""
    global _WP1
    if _WP1 is None:
        if str(HERE) not in sys.path:
            sys.path.insert(0, str(HERE))
        import importlib
        _WP1 = importlib.import_module("02_build_company_bank_cooc_panel")
        _attach_engine_logging()
    return _WP1


class _EngineLogRename(logging.Filter):
    """把借用的 02 加权引擎 logger 记录改名为本阶段名 (R2-P2-6, 镜像 tax 03 姿势; listed 03 未做勿抄):
    引擎自身 emit 的 budget 生效值/chunk 收缩 WARNING 若不改名, 会携带 02 阶段名混入本日志或干脆失捕。"""

    def __init__(self, stage_name: str) -> None:
        super().__init__()
        self._stage = stage_name

    def filter(self, record: logging.LogRecord) -> bool:
        record.name = self._stage
        return True


def _attach_engine_logging() -> None:
    import os
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return  # 测试进程绝不接管文件日志 (与 _init_stage_logging 对称)
    eng_logger = logging.getLogger("02_build_company_bank_cooc_panel")
    if not any(isinstance(f, _EngineLogRename) for f in eng_logger.filters):
        eng_logger.addFilter(_EngineLogRename(Path(__file__).stem))
    for h in logger.handlers:
        if h not in eng_logger.handlers:
            eng_logger.addHandler(h)
    eng_logger.setLevel(logging.INFO)


def _init_stage_logging() -> None:
    """接入主管道日志基建 (core/logging.py::setup_logging): 写 company_listed_bank/logs/<stem>.log,
    每次运行覆盖, 与主管道各阶段日志完全一致。"""
    import os
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return  # WP-A: 测试进程绝不接管文件日志 (2026-07-07 审计教训)
    import importlib.util
    # ⚠ 此处禁借道 wp1() 取 REPO: wp1() 会触发 _attach_engine_logging, 而本函数尚未建立文件
    # handler → 引擎日志 attach 到空手柄集、永久失捕。REPO = news_process 根 = HERE.parent。
    spec = importlib.util.spec_from_file_location(
        "_np_core_logging", HERE.parent / "core" / "logging.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.setup_logging(Path(__file__).stem, str(HERE / "logs"))
    logging.getLogger(Path(__file__).stem).propagate = True


def log(msg: str, warn: bool = False) -> None:
    (logger.warning if warn else logger.info)(msg)


# ---------------------------------------------------------------- codebook 幂等 upsert (D1 自带, ≤12 行)
def _upsert_section(codebook_path: Path, section_md: str, begin: str, end: str) -> None:
    """参数化 section-upsert (语义镜像 tax 03 四参版 pre+block+post; listed 03 版标记硬编码不可复用)。
    只替换自己标记段, 03 七权章/其余正文原样保留; 无标记 → append; 文件缺 → 新建。"""
    block = f"{begin}\n{section_md}\n{end}"
    if codebook_path.exists():
        text = codebook_path.read_text(encoding="utf-8")
        if begin in text and end in text:
            text = text.split(begin)[0] + block + text.split(end, 1)[1]
        else:
            text = text.rstrip("\n") + "\n\n" + block + "\n"
    else:
        text = block + "\n"
    codebook_path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- frozenw 权重构造 (D2, 纯函数)
def build_frozen_weights(pair: pd.DataFrame, year_max: int):
    """基期冻结权重长表: 逐 (company, track) 取窗内首个共现年 (pair 无 n_docs=0 行, min(year) 即
    base_year), 基期行按当年 n_docs 作份额、复制展年到 [base_year, year_max] (归一化交引擎 D12
    逐年限非缺失重归一); t<base_year 不入 frame = 左截断不回退 (fail-closed)。
    返回 (weights[company,bank,year,track,w], diag[company,track,base_year,n_banks], 长表载体)。"""
    p = pair[["company", "bank", "year", "track", "n_docs"]].copy()
    base_yr = p.groupby(["company", "track"], sort=False)["year"].transform("min")
    base = p.loc[p["year"] == base_yr].sort_values(["company", "track", "bank"],
                                                   kind="mergesort").reset_index(drop=True)
    reps = (int(year_max) - base["year"].to_numpy() + 1)
    assert (reps >= 1).all(), "base_year > year_max — 年窗与 pair 表窗不一致 (禁从 pair 推年窗)"
    out = base.iloc[np.repeat(np.arange(len(base)), reps)].copy()
    offs = (np.concatenate([np.arange(n) for n in reps]) if len(reps)
            else np.array([], dtype=np.int64))
    out["base_year"] = out["year"].astype("int16")
    out["year"] = (out["year"].to_numpy() + offs).astype(np.int32)
    out["w"] = out["n_docs"].astype("float64")
    out = out.reset_index(drop=True)
    weights = out[["company", "bank", "year", "track", "w"]]
    diag = (base.groupby(["company", "track"], sort=False)
            .agg(base_year=("year", "min"), n_banks=("bank", "nunique")).reset_index())
    return weights, diag, out


def frozen_diag_wide(diag: pd.DataFrame, company_col: str) -> pd.DataFrame:
    """diag (company×track 长) → company 宽表: base_year_{t} / frozen_n_banks_{t} (float64, NaN=该轨
    窗内无共现; 不填 0 — 计数填 0 语义仅适用主面板 n_cooc 族, D4)。列值逐公司恒定、随骨架广播到全年。"""
    cols: dict[str, pd.Series] = {}
    for t in TRACKS:
        sub = diag[diag["track"] == t].set_index("company")
        cols[f"base_year_{t}"] = sub["base_year"].astype("float64")
        cols[f"frozen_n_banks_{t}"] = sub["n_banks"].astype("float64")
    wide = pd.DataFrame(cols)
    wide.index.name = company_col
    return wide


# ---------------------------------------------------------------- mainbankw 权重构造 (D3, 纯函数)
def build_mainbank_weights(pair: pd.DataFrame):
    """top-1 主办银行权重长表: 逐 (company, year, track) 当年 n_docs argmax; 三级确定性平票 =
    n_docs → n_docs_longhit → 银行名码点升序 (D8: sort_values 多键 lexsort 稳定 + drop_duplicates
    行原子; 禁 groupby.first 逐列非 NaN 拼装 / 禁裸 idxmax)。每格单行 w=1.0 → 引擎 N=1 短路给出
    cw=X_main 逐位、ce≡cw 逐位; 测度缺失两臂同步 NaN (严格 top-1 不顺延次位)。
    返回 (weights[company,bank,year,track,w], diag 含 share/tie/第三级裁决旗标)。"""
    key = ["company", "year", "track"]
    p = pair[key[:1] + ["bank"] + key[1:] + ["n_docs", "n_docs_longhit"]].copy()
    g = p.groupby(key, sort=False)
    nmax = g["n_docs"].transform("max")
    top1 = p[p["n_docs"] == nmax]
    lh_max = top1.groupby(key, sort=False)["n_docs_longhit"].transform("max")
    top2 = top1[top1["n_docs_longhit"] == lh_max]
    n_tie1 = top1.groupby(key, sort=False)["bank"].size().rename("_n_tie1")
    n_tie2 = top2.groupby(key, sort=False)["bank"].size().rename("_n_tie2")
    n_tot = g["n_docs"].sum().rename("_n_docs_tot")
    win = (p.sort_values(key + ["n_docs", "n_docs_longhit", "bank"],
                         ascending=[True, True, True, False, False, True], kind="mergesort")
           .drop_duplicates(subset=key, keep="first"))
    win = (win.merge(n_tie1, left_on=key, right_index=True)
              .merge(n_tie2, left_on=key, right_index=True)
              .merge(n_tot, left_on=key, right_index=True))
    win["main_bank_share"] = win["n_docs"] / win["_n_docs_tot"]
    win["main_bank_tie"] = (win["_n_tie1"] > 1).astype("float64")
    # 第三级名序实际承重旗标 (R2-P2-4 披露: 一二级双平, 靠码点序裁决)
    win["name_order_decisive"] = (win["_n_tie2"] > 1).astype("float64")
    win = win.reset_index(drop=True)
    weights = win[["company", "bank", "year", "track"]].assign(w=1.0)
    return weights, win


def mainbank_diag_wide(win: pd.DataFrame, company_col: str) -> pd.DataFrame:
    """win 长表 → (company, year) 宽表: main_bank_{t} (str, 缺失=空串 — pyreadstat 字符串缺失落
    Stata 空串非 `.`, codebook 披露) / main_bank_share_{t} / main_bank_tie_{t} (float64, NaN=无共现)。"""
    cols: dict[str, pd.Series] = {}
    for t in TRACKS:
        sub = win[win["track"] == t].set_index(["company", "year"])
        cols[f"main_bank_{t}"] = sub["bank"]
        cols[f"main_bank_share_{t}"] = sub["main_bank_share"].astype("float64")
        cols[f"main_bank_tie_{t}"] = sub["main_bank_tie"].astype("float64")
    wide = pd.DataFrame(cols)
    wide.index.names = [company_col, "year"]
    for t in TRACKS:
        wide[f"main_bank_{t}"] = wide[f"main_bank_{t}"].fillna("")
    return wide


# ---------------------------------------------------------------- 面板装配 (WP1.5, 姿势钉死)
def assemble_panel(weighted: pd.DataFrame, companies_all: list[str], y0: int, y1: int,
                   bank_company_set: set[str], company_col: str) -> pd.DataFrame:
    """满骨架 (sorted 公司序 × 年窗, D4) 承载固定列; 加权列一律按值 merge (镜像 02 L1415/03 L1184);
    ⚠ 禁 weighted.reindex(骨架) — 混 dtype level 的 get_indexer 有全 -1 静默全 NaN 雷 (R2-P1-1)。"""
    skeleton = pd.MultiIndex.from_product([companies_all, range(y0, y1 + 1)],
                                          names=[company_col, "year"])
    panel = pd.DataFrame(index=skeleton).reset_index()
    panel["year"] = panel["year"].astype("int16")
    panel["is_bank_company"] = panel[company_col].isin(bank_company_set).astype("int8")
    if len(weighted.columns):
        panel = panel.merge(weighted, how="left", left_on=[company_col, "year"], right_index=True)
    return panel


# ---------------------------------------------------------------- 内联 gate (WP1.5; 禁复用 02 run_gates)
def run_altagg_gates(scheme: str, panel: pd.DataFrame, weights: pd.DataFrame,
                     n_rows_expect: int, y0: int, y1: int) -> None:
    """02 run_gates 的 gate⑧ (n_cooc==0⇒cw/ce 全 NaN) 对 frozenw 结构性不成立 (解耦构念特征),
    故本步自带 gate 集, fail-loud。"""
    assert len(panel) == n_rows_expect, f"{scheme}: 行数 {len(panel)} ≠ 骨架 {n_rows_expect}"
    dup = weights.duplicated(subset=["company", "bank", "year", "track"])
    assert not dup.any(), f"{scheme}: weights frame (company,bank,year,track) 键重复 (引擎会双计)"
    cw_cols = [c for c in panel.columns if c.startswith("cw_")]
    ce_cols = [c for c in panel.columns if c.startswith("ce_")]
    assert len(cw_cols) == len(ce_cols), f"{scheme}: cw/ce 列数不对偶"
    log(f"  gate[{scheme}]① 行数不变量 {len(panel):,} == 骨架 ✓ | ② weights 键唯一 "
        f"{len(weights):,} 行 ✓ | cw/ce 对偶 {len(cw_cols)} 对 ✓")
    if scheme == "frozenw":
        assert len(cw_cols) > 0, "frozenw: 面板无任何 cw 列 — 引擎输出为空 (weights 空/registry 空)"
        assert len(weights) > 0, "frozenw: weights frame 为空 — pair 表空或基期构造失败"
        assert panel[cw_cols].notna().any().any(), \
            "frozenw: 加权列全 NaN — merge 键错配静默雷 (R2-P1-1 锚) 或冻结集合测度全代缺失"
        # 左截断 gate: 逐轨 year<base_year 行该轨加权列必全 NaN
        for t in TRACKS:
            by = panel.get(f"base_year_{t}")
            if by is None:
                continue
            m = by.notna() & (panel["year"] < by)
            tcols = [c for c in cw_cols + ce_cols if c.endswith(f"_{t}")]
            if m.any() and tcols:
                assert panel.loc[m, tcols].isna().all().all(), \
                    f"frozenw: {t} 轨左截断格出现非缺失 (禁回退当期权重)"
            byv = by.dropna()
            if len(byv):
                assert ((byv >= y0) & (byv <= y1)).all(), f"frozenw: base_year_{t} 值域违例"
        log("  gate[frozenw]③ 非 NaN 存在锚 ✓ | ④ 左截断全 NaN (不回退) ✓ | ⑤ base_year 值域 ✓")
    if scheme == "mainbankw":
        for cw_c in cw_cols:
            ce_c = "ce_" + cw_c[3:]
            a, b = panel[cw_c].to_numpy(), panel[ce_c].to_numpy()
            same = (np.isnan(a) & np.isnan(b)) | (a == b)
            assert same.all(), f"mainbankw: {cw_c} 与 {ce_c} 非逐位恒等 (N=1 短路失效?)"
        for t in TRACKS:
            sh = panel.get(f"main_bank_share_{t}")
            if sh is not None:
                v = sh.dropna()
                assert ((v > 0) & (v <= 1 + 1e-12)).all(), f"mainbankw: share_{t} 值域违例"
            mb = panel.get(f"main_bank_{t}")
            tcols = [c for c in cw_cols if c.endswith(f"_{t}")]
            if mb is not None and tcols:
                m = mb == ""
                if m.any():
                    assert panel.loc[m, tcols].isna().all().all(), \
                        f"mainbankw: {t} 轨无共现格出现非缺失加权值"
        log("  gate[mainbankw]③ cw≡ce 逐位恒等 (单银行退化, 结构冗余非 bug) ✓ | "
            "④ share∈(0,1] ✓ | ⑤ 无共现格全 NaN ✓")


# ---------------------------------------------------------------- codebook 章 (D11)
def build_codebook_section(fro_diag: pd.DataFrame, win: pd.DataFrame,
                           fro_panel: pd.DataFrame, main_panel_path: Path,
                           company_col: str, y0: int, y1: int,
                           panel_prefix: str, n_alt_weights: int) -> str:
    """「替代聚合面板章」md (覆盖表运行时实算; 主面板 parquet 缺失时交并集表降级为占位并 WARN)。"""
    alt_word = "七权" if n_alt_weights == 7 else "双替代权"
    n_total = 1 + n_alt_weights + 2
    L: list[str] = [
        "",
        "## 替代聚合面板 (frozenw 基期冻结 + mainbankw top-1 主办银行, 步骤 04 生成)",
        "",
        f"两面板 `{panel_prefix}_{{frozenw,mainbankw}}_panel.{{dta,parquet}}` 与媒体主面板同引擎同列名",
        "(`cw_/ce_{基名}_{track}`, 同一 D16 短名表), scheme 身份由文件名承载。**本章 2 面板与主面板/",
        f"{alt_word}面板并排 — 合计聚合臂 {n_total}; 03 生成的『禁面板横向 merge』铁律与 02 产物总览表",
        "『×N』计数不含本章产物, 铁律对全体面板成立**: 各自 just-identified 并排, 禁混同一",
        "over-identified Hansen J、禁横向 merge、禁同一 RHS 并置多权重版本同名测度 (horse-race 显式",
        "标注豁免); frozen×mainbank 禁交叉。报告层 canonical 仍为主面板 cw (headline)。",
        "",
        "### frozenw 口径 (D2)",
        "逐 (company, track): base_year = 面板窗内首个 n_docs>0 年 (canonical 不门控计数, GPSS",
        "initial-share); 基期份额冻结、逐年 × 当年银行测度 (引擎逐年限非缺失重归一 — 重归一后非严格",
        "shift-share, 触发占比生产机回填)。t<base_year 全列 NaN (左截断, 不回退当期权重);",
        "t≥base_year 权重恒有定义, **加权值有值的前提 = 冻结集合内至少一家银行该年测度非缺**",
        "(银行退出面板 → NaN, 第三缺失通道); 当年零共现不影响有值 (冻结暴露与当年新闻流量刻意解耦,",
        "构念特征非 bug)。ce 臂 = 基期银行集合等权 (独立稳健臂, 与主 ce 的当年集合等权不同)。",
        "三轨 base_year 逐轨独立可不同 (轨内自包含; 跨轨并排判读时基期时点差是额外差异源)。",
        "own-bank: pair 长表上游 02 D4 已剔自身银行, 本步零特判, 四臂同源承接。",
        "",
        "### frozenw 发表义务五句 (D10, 非可选)",
        "① shift-share 推断须 exposure-robust SE (Adão, Kolesár & Morales 2019, QJE), 常规聚类 SE 过窄。",
        "② 基期 = 首个入样共现年属研究者选择 (Goldsmith-Pinkham, Sorkin & Swift 2020, AER 的",
        "initial-share 构造); pair 长表在, 可 $0 重定基期 (D17 重构通道)。",
        "③ 识别假设 = 基期份额对企业结果的影响仅经银行冲击通道 (exogenous shares 叙事)。",
        "④ staggered 基期三重偏离: 基期年逐公司异质且与媒体首次可见时点相关 (非统一 pre-period 快照)",
        "— 识别叙事须条件于公司首现年成立; 基期时点本身内生于媒体可见度; 基期越晚 frozen 与当期权重",
        "越收敛 (去内生化力度异质衰减; frozen-vs-当期 Spearman 稀释诊断生产机回填)。",
        "⑤ **共同样本对齐义务**: frozenw 与主 cw/ce 的非缺失格点集合互不包含 (左截断 / 零共现年解耦",
        "有值 / 第三缺失通道三向错位) — 两臂并排对比一律先取共同非缺失样本 (common support) 再估计,",
        "禁在各自全样本上直接比系数。构造原型 = Chodorow-Reich (2014). The employment effects of",
        "credit market disruptions: Firm-level evidence from the 2008-9 financial crisis. QJE, 129(1),",
        "1-59 (危机前借贷关系份额作冻结暴露权重)。",
        "",
        "### mainbankw 口径 (D3)",
        "逐 (company, year, track): main bank = 当年 n_docs argmax (与主 cw 同时点, 与 frozenw 正交);",
        "三级确定性平票 = n_docs → n_docs_longhit → 银行名码点升序 (tie 旗标 + 名序承重旗标见覆盖表)。",
        "**main bank 当年某测度在银行面板缺失 → 该格该列 NaN (严格 top-1, 不顺延次位)** — 顺延即按测度",
        "可得性重选银行 (重新引入选择内生性)。**mainbankw 的 ce 列无独立信息** (单银行退化恒等 cw,",
        "结构冗余非 bug, 分析端任取一臂 — 与 frozenw 的 ce=独立臂不同, 勿计入臂数)。top-1 聚合对单篇",
        "计数噪声的击穿点为 0 (单篇误配可翻转主办行, 均值臂仅被稀释) — 构念代价非 bug; 稳健读法 =",
        "与 cw 臂并排 + main_bank_share 低值格降权判读。构念谱系 = Petersen & Rajan (1994, JF 49(1),",
        "3-37) 关系借贷; Hoshi, Kashyap & Scharfstein (1991, QJE 106(1), 33-60) 主银行制; Bharath,",
        "Dahiya, Saunders & Srinivasan (2011, RFS 24(4), 1141-1203) 关系强度。",
        "",
        "### 诊断列与缺失语义 (D4)",
        "| 列 | dtype | 缺失语义 |",
        "|---|---|---|",
        "| `base_year_{track}` | float64 | NaN = 该轨窗内无共现 (逐公司恒定, 随骨架广播全年) |",
        "| `frozen_n_banks_{track}` | float64 | 基期银行家数; NaN 同上 (不填 0) |",
        "| `main_bank_{track}` | str | **缺失 = 空串 \"\"** (pyreadstat 字符串缺失落 Stata 空串非 `.`, 与数值列 NaN=`.` 不同套) |",
        "| `main_bank_share_{track}` | float64 | ∈(0,1]; NaN = 无共现 |",
        "| `main_bank_tie_{track}` | float64 | 0/1; NaN = 无共现 |",
        "",
        "ss 轨基期/主办行判定按 `n_docs` 含 fallback 口径 (`n_docs_strict`/`n_docs_longhit` 口径变体臂",
        "经 pair 表 $0 可重构, 刻意不物化)。权重逐轨 (与媒体主面板同语义, 与替代权面板 track-less",
        "权重不同, 勿套错)。级联义务: pair 长表重生 (重跑 02) ⇒ 本章两面板与本章内容 stale, 且 02 整",
        "文件重写 codebook 只保留 03 标记块、本章会被抹掉 — **重跑 02 后须补跑 04**。",
        "",
        "### 刻意不做 (§1b 归档, 一句话理由)",
        "GIV (cw−ce; 估计框架另立门户, 依赖 Gabaix-Koijen 因子结构假设) / leave-one-out (真 LOO 须回",
        "文章级重算, 窄版被上游 D4 剔除天然覆盖) / 关系存量-时间衰减权重 (与 frozenw 答同一威胁, 冗余",
        "梯子 — 先验判断, 质疑时经 pair 表实测) / frozen×mainbank 交叉臂 (梯子禁交叉) / tax 窗前基期臂",
        "(pair 表被 02 裁到面板窗, DEFER 生产机) / mainbank top-k≥2 (top-1 与 cw 的插值臂, 冗余) /",
        "strict-longhit 口径变体 (pair 表 $0 可重构) / Stata 2SLS+AKM 模板 (papers 侧财务面板接入时)。",
        "",
    ]
    # ---- 覆盖表 (运行时实算)
    L += ["### base_year 分布 (frozenw; 逐轨, 判真零 vs 左截断)", "",
          "| base_year | " + " | ".join(TRACKS) + " |", "|---|---|---|---|"]
    byr = {t: fro_diag.loc[fro_diag["track"] == t, "base_year"].value_counts() for t in TRACKS}
    years_seen = sorted(set().union(*[set(v.index) for v in byr.values()])) if len(fro_diag) else []
    for y in years_seen:
        L.append(f"| {y} | " + " | ".join(str(int(byr[t].get(y, 0))) for t in TRACKS) + " |")
    comp_multi = fro_diag.groupby("company")["base_year"].nunique()
    n_multi = int((comp_multi > 1).sum())
    L += ["", f"三轨 base_year 不一致公司数 = {n_multi} / 有共现公司 {len(comp_multi)} "
          f"({100 * n_multi / max(len(comp_multi), 1):.4g}%)。", ""]
    L += ["### mainbankw 覆盖 (逐年非缺格点数 / tie 率 / 第三级名序承重率)", "",
          "| 年 | 非缺格点 (full/ctx/ss) | tie 率 | 名序承重率 |", "|---|---|---|---|"]
    for y in sorted(win["year"].unique()):
        wy = win[win["year"] == y]
        per_t = "/".join(str(int((wy["track"] == t).sum())) for t in TRACKS)
        L.append(f"| {int(y)} | {per_t} | {100 * float(wy['main_bank_tie'].mean()):.4g}% "
                 f"| {100 * float(wy['name_order_decisive'].mean()):.4g}% |")
    # ---- 共同样本交并集 (D10⑤ 载体; 主面板 parquet 缺失则降级)
    L += ["", "### frozenw × 主面板 共同样本 (D10⑤; 格点 = 该轨任一 cw 列非缺的 company×year)", ""]
    if main_panel_path.exists():
        mainp = pd.read_parquet(main_panel_path)
        L += ["| 轨 | 交集 | 并集 | 仅 frozenw (解耦有值) | 仅主面板 (左截断/第三通道) |",
              "|---|---|---|---|---|"]
        for t in TRACKS:
            fc = [c for c in fro_panel.columns if c.startswith("cw_") and c.endswith(f"_{t}")]
            mc = [c for c in mainp.columns if c.startswith("cw_") and c.endswith(f"_{t}")]
            fset = set(map(tuple, fro_panel.loc[fro_panel[fc].notna().any(axis=1),
                                                [company_col, "year"]].to_numpy()))
            mset = set(map(tuple, mainp.loc[mainp[mc].notna().any(axis=1),
                                            [company_col, "year"]].to_numpy()))
            L.append(f"| {t} | {len(fset & mset)} | {len(fset | mset)} | {len(fset - mset)} "
                     f"| {len(mset - fset)} |")
    else:
        L.append("(主面板 parquet 缺席, 交并集表待 02+04 同代产物后由 04 重跑回填。)")
    L += ["", f"面板年窗 [{y0}, {y1}]; dev 语料窗内大面积零共现年属预期退化 (生产语料恢复),",
          "base_year=窗末年公司 frozen≡cw 逐点恒等属构造退化非 bug。生产机回填义务: 重归一触发占比 /",
          "main-bank 测度缺失格点占比 / frozen-cw 权重向量逐年 Spearman / main bank 翻转率 (§9)。", ""]
    return "\n".join(L)


# ---------------------------------------------------------------- 结果统计 (纯日志, 无计算副作用)
def _rss_mb() -> float:
    import psutil
    return psutil.Process().memory_info().rss / 1024 / 1024


def _pkg_ver(name: str) -> str:
    try:
        from importlib.metadata import version
        return version(name)
    except Exception:
        return "n/a"


def _log_result_stats(scheme: str, panel: pd.DataFrame, company_col: str) -> None:
    """逐面板结果统计段 (镜像 02 统计报告口径; 全部非整数 %.4g)。只消费已算出的面板, 零副作用。"""
    n = len(panel)
    cw_cols = [c for c in panel.columns if c.startswith("cw_")]
    logger.info("  【%s 结果统计】面板 %s 行 × %s 列 (cw/ce 对偶 %d 对 + 诊断列)",
                scheme, f"{n:,}", f"{len(panel.columns):,}", len(cw_cols))
    for t in TRACKS:
        tcols = [c for c in cw_cols if c.endswith(f"_{t}")]
        if not tcols:
            continue
        nz = panel[tcols].notna().any(axis=1)
        n_nz = int(nz.sum())
        logger.info("    · %s 轨: 非缺格点 %s (%.4g%% of 骨架) | 该轨 cw 列均值覆盖率 %.4g%%",
                    t, f"{n_nz:,}", 100.0 * n_nz / n,
                    100.0 * float(panel[tcols].notna().mean().mean()))
    if scheme == "frozenw":
        for t in TRACKS:
            by = panel.get(f"base_year_{t}")
            if by is None or not by.notna().any():
                continue
            m_trunc = by.notna() & (panel["year"] < by)
            covered = panel[company_col].isin(panel.loc[by.notna(), company_col].unique())
            logger.info("    · %s 轨: 左截断格 %s (基期前, 恒 NaN 不回退) | 有基期公司覆盖行 %s | "
                        "基期年跨度 [%.4g, %.4g]",
                        t, f"{int(m_trunc.sum()):,}", f"{int(covered.sum()):,}",
                        float(by.min()), float(by.max()))
    if scheme == "mainbankw":
        for t in TRACKS:
            sh = panel.get(f"main_bank_share_{t}")
            tie = panel.get(f"main_bank_tie_{t}")
            if sh is None or not sh.notna().any():
                continue
            v = sh.dropna()
            logger.info("    · %s 轨: 主办行格 %s | share 分布 均值 %.4g / p50 %.4g / p90 %.4g / "
                        "全 1.0 (单银行) 占比 %.4g%% | tie 率 %.4g%%",
                        t, f"{len(v):,}", float(v.mean()), float(v.quantile(0.5)),
                        float(v.quantile(0.9)), 100.0 * float((v == 1.0).mean()),
                        100.0 * float(tie.dropna().mean()))


# ---------------------------------------------------------------- 文献锚点 (D9: 仅审计白名单内条目入日志)
def _log_citations() -> None:
    """📖 方法论依据 — APA 引文逐字取自审定引文池 (audit_dois 白名单, 仅整理换行, 0 自造);
    白话注解落到本脚本的具体设计决策。Chodorow-Reich 2014/HKS 1991/Bharath 2011 池缺,
    仅入 codebook 散文不入日志 (待 litanchor 补池后可扩)。"""
    logger.info("-" * 70)
    logger.info("📖 方法论依据 (22 条, 全部在 audit_dois 白名单池)")
    logger.info("[shift-share 识别谱系 — frozenw 基期冻结权重]")
    logger.info("  1. Bartik, T. J. (1991). Who benefits from state and local economic development")
    logger.info("     policies? W.E. Upjohn Institute. https://doi.org/10.17848/9780585223940")
    logger.info("     → 白话: \"基期份额 × 外生增量\"加权范式的原始出处 — frozenw 把共现份额冻结在基期、")
    logger.info("       逐年只乘银行侧测度, 正是该构造在银企面板上的落地, 亦是 scheme 命名的方法源头。")
    logger.info("  2. Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when,")
    logger.info("     why, and how. American Economic Review, 110(8), 2586–2624.")
    logger.info("     https://doi.org/10.1257/aer.20181047")
    logger.info("     → 白话: 把 Bartik 识别正式化为\"份额外生\"路径 — frozenw 的基期 = 首个入样共现年")
    logger.info("       (initial share), 冻结即为满足份额前定的 GPSS 处方; 基期属研究者选择已按其框架披露。")
    logger.info("  3. Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share research")
    logger.info("     designs. The Review of Economic Studies, 89(1), 181–213.")
    logger.info("     https://doi.org/10.1093/restud/rdab030")
    logger.info("     → 白话: \"冲击外生\"的互补识别路径 — frozenw 的\"冻结份额 × 逐年银行测度\"恰是其")
    logger.info("       share×shift 分解结构, shift 外生时基期份额允许残余内生。")
    logger.info("  4. Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share")
    logger.info("     instruments. Journal of Economic Perspectives, 39(1), 181–204.")
    logger.info("     https://doi.org/10.1257/jep.20231370")
    logger.info("     → 白话: 2025 最新实操检查表 (含 incomplete shares 与重归一的正面处理) — frozenw 的")
    logger.info("       基期选择、冻结集合测度缺失时引擎逐年限非缺失重归一 (D12), 逐项可对到该清单。")
    logger.info("  5. Adão, R., Kolesár, M., & Morales, E. (2019). Shift-share designs: Theory and inference.")
    logger.info("     The Quarterly Journal of Economics, 134(4), 1949–2010.")
    logger.info("     https://doi.org/10.1093/qje/qjz025")
    logger.info("     → 白话: 份额相关使常规标准误失效 — frozenw 冻结后各公司共享同一基期权重结构, 下游")
    logger.info("       回归须 exposure-robust SE (codebook 章 D10① 发表义务, 非可选)。")
    logger.info("  6. Borusyak, K., & Hull, P. (2023). Nonrandom exposure to exogenous shocks.")
    logger.info("     Econometrica, 91(6), 2155–2185. https://doi.org/10.3982/ECTA19367")
    logger.info("     → 白话: 暴露非随机时的遗漏变量偏差与 recentering 修正 — 本面板现阶段为描述性暴露")
    logger.info("       测度, 引作\"若未来将 frozenw 升格为处理/工具\"时的偏差诊断参照, 非现行构造依据。")
    logger.info("  7. Apfel, N. (2024). Relaxing the exclusion restriction in shift-share instrumental")
    logger.info("     variable estimation. Journal of the Royal Statistical Society Series A: Statistics")
    logger.info("     in Society, 187(3), 748–771. https://doi.org/10.1093/jrsssa/qnad148")
    logger.info("     → 白话: 允许部分份额违反排他仍可识别 — 基期共现并非随机, frozenw 下游若作 IV, 残余")
    logger.info("       \"基期份额内生\"疑虑的敏感性论证工具即此。")
    logger.info("  8. Hahn, J., Kuersteiner, G., Santos, A., & Willigrod, W. (2024). Overidentification in")
    logger.info("     shift-share designs. arXiv. https://doi.org/10.48550/arXiv.2404.17049")
    logger.info("     → 白话: shift-share 设计中不同识别假设隐含不同过度识别约束 — 本步两 scheme 与八权/")
    logger.info("       三轨\"各自 just-identified 并排、禁混同一 Hansen J\"铁律的直接计量支撑。(arXiv 未评审)")
    logger.info("  9. Greenstone, M., Mas, A., & Nguyen, H.-L. (2020). Do credit market shocks affect the")
    logger.info("     real economy? Quasi-experimental evidence from the Great Recession and \"normal\"")
    logger.info("     economic times. American Economic Journal: Economic Policy, 12(1), 200–225.")
    logger.info("     https://doi.org/10.1257/pol.20160005")
    logger.info("     → 白话: 以\"银行本地份额 × 信贷供给移动\"构造 county 级暴露的直接先例 — 与 frozenw")
    logger.info("       同构且同用前定份额; 此处仅取其暴露构造方法, 不引其结论方向。")
    logger.info("[关系借贷与主办银行谱系 — mainbankw top-1 主办银行]")
    logger.info("  10. Petersen, M. A., & Rajan, R. G. (1994). The benefits of lending relationships:")
    logger.info("      Evidence from small business data. The Journal of Finance, 49(1), 3–37.")
    logger.info("      https://doi.org/10.1111/j.1540-6261.1994.tb04418.x")
    logger.info("      → 白话: 关系借贷谱系奠基 — \"银行对企业的影响经由既存关系传导\"是两 scheme 共同的")
    logger.info("        经济学前提; 关系集中于少数银行的收益证据支撑 top-1 口径的构念效度。")
    logger.info("  11. Berger, A. N., & Udell, G. F. (1995). Relationship lending and lines of credit in")
    logger.info("      small firm finance. The Journal of Business, 68(3), 351–381.")
    logger.info("      https://doi.org/10.1086/296668")
    logger.info("      → 白话: 关系强度→信贷条件的原始证据 — mainbankw 以共现计数 argmax 代理\"最强关系")
    logger.info("        银行\", 其经济学前提即关系强度单调映射到银企互动密度。")
    logger.info("  12. Boot, A. W. A. (2000). Relationship banking: What do we know? Journal of Financial")
    logger.info("      Intermediation, 9(1), 7–25. https://doi.org/10.1006/jfin.2000.0282")
    logger.info("      → 白话: relationship banking 权威综述, 界定\"与一家主要银行长期专属互动\"构念 —")
    logger.info("        top-1 主办行定义的理论出处。")
    logger.info("  13. Bolton, P., Freixas, X., Gambacorta, L., & Mistrulli, P. E. (2016). Relationship and")
    logger.info("      transaction lending in a crisis. The Review of Financial Studies, 29(10), 2643–2676.")
    logger.info("      https://doi.org/10.1093/rfs/hhw041")
    logger.info("      → 白话: 关系型 vs 交易型借贷的构念边界 — 主办行 (关系型) 与其余共现银行 (更接近")
    logger.info("        交易型) 的二分依据; cw 均值臂与 top-1 臂并排恰暴露这一构念差。")
    logger.info("  14. Khwaja, A. I., & Mian, A. (2008). Tracing the impact of bank liquidity shocks:")
    logger.info("      Evidence from an emerging market. American Economic Review, 98(4), 1413–1442.")
    logger.info("      https://doi.org/10.1257/aer.98.4.1413")
    logger.info("      → 白话: 以冲击前既存银企配对追踪银行冲击传导的识别范式 — frozenw 冻结基期权重与")
    logger.info("        mainbankw 主办行×银行测度都是该传导算术的落地。")
    logger.info("  15. Amiti, M., & Weinstein, D. E. (2018). How much do idiosyncratic bank shocks affect")
    logger.info("      investment? Evidence from matched bank-firm loan data. Journal of Political Economy,")
    logger.info("      126(2), 525–587. https://doi.org/10.1086/696272")
    logger.info("      → 白话: matched 银企数据下按贷款份额加权分解银行特异冲击 — cw/frozenw 的份额加权")
    logger.info("        传导框架与 mainbank 主办行识别策略的方法奠基。")
    logger.info("  16. Berger, A. N., Bouwman, C. H. S., Norden, L., Roman, R. A., Udell, G. F., & Wang, T.")
    logger.info("      (2024). Piercing through opacity: Relationships and credit card lending to consumers")
    logger.info("      and small businesses during normal times and the COVID-19 crisis. Journal of")
    logger.info("      Political Economy, 132(2), 484–551. https://doi.org/10.1086/726236")
    logger.info("      → 白话: 2024 顶刊最新证据 — 关系持有人在危机中获更优条件, 主办行关系价值构念在")
    logger.info("        当代信贷市场仍成立。")
    logger.info("  17. Huang, J., Matthews, K., & Zhou, P. (2020). What causes Chinese listed firms to")
    logger.info("      switch bank loan provider? Evidence from a survival analysis. Emerging Markets")
    logger.info("      Review, 43, Article 100678. https://doi.org/10.1016/j.ememar.2020.100678")
    logger.info("      → 白话: 中国上市公司主贷款银行存续/切换的直接证据 — mainbankw 逐年 argmax 允许")
    logger.info("        主办行跨年变动, 其变动率可与该文切换率互为参照 (main bank 翻转率生产机回填)。")
    logger.info("[测度构造披露·时点纪律·复现工程]")
    logger.info("  18. Huntington-Klein, N., Arenas, A., Beam, E., Bertoni, M., Bloem, J. R., Burli, P.,")
    logger.info("      Chen, N., Grieco, P., Ekpe, G., Pugatch, T., Saavedra, M., & Stopnitzky, Y. (2021).")
    logger.info("      The influence of hidden researcher decisions in applied microeconomics. Economic")
    logger.info("      Inquiry, 59(3), 944–960. https://doi.org/10.1111/ecin.12992")
    logger.info("      → 白话: 隐藏的构造决策足以改变结论 — 本步把\"权重取哪年 (frozenw)\"与\"聚合用均值")
    logger.info("        还是取最大 (mainbankw)\"两个隐藏自由度物化为并排面板, 显式化而非择一隐藏。")
    logger.info("  19. Steegen, S., Tuerlinckx, F., Gelman, A., & Vanpaemel, W. (2016). Increasing")
    logger.info("      transparency through a multiverse analysis. Perspectives on Psychological Science,")
    logger.info("      11(5), 702–712. https://doi.org/10.1177/1745691616658637")
    logger.info("      → 白话: multiverse = 把数据构造分叉全部展开 — frozenw/mainbankw 正是同一共现构念")
    logger.info("        的构造分叉, 与八权并成规格曲线的两根新支。")
    logger.info("  20. Banz, R. W., & Breen, W. J. (1986). Sample-dependent results using accounting and")
    logger.info("      market data: Some evidence. The Journal of Finance, 41(4), 779–793.")
    logger.info("      https://doi.org/10.1111/j.1540-6261.1986.tb04548.x")
    logger.info("      → 白话: look-ahead 偏差的首次系统论证 — frozenw \"只用基期已可得的共现信息定权\"")
    logger.info("        即防前视纪律在权重矩阵上的应用 (左截断不回退同源)。")
    logger.info("  21. Gabaix, X., & Koijen, R. S. J. (2024). Granular instrumental variables. Journal of")
    logger.info("      Political Economy, 132(7), 2274–2303. https://doi.org/10.1086/728743")
    logger.info("      → 白话: 规模加权和 vs 等权和的识别差异正式化 — 本步 cw (份额加权) 与 ce (等权) 两")
    logger.info("        臂并排的理论出处; frozenw 的 ce=基期集合等权是独立稳健臂, mainbankw 的 ce 单银行")
    logger.info("        退化恒等 (勿计臂数)。")
    logger.info("  22. Fišar, M., Greiner, B., Huber, C., Katok, E., Ozkes, A. I., & the Management Science")
    logger.info("      Reproducibility Collaboration. (2024). Reproducibility in Management Science.")
    logger.info("      Management Science, 70(3), 1343–1356. https://doi.org/10.1287/mnsc.2023.03556")
    logger.info("      → 白话: 大规模复现协作确立的工程规范 — 本步 registry 哈希锚复算 + pair 双向锁")
    logger.info("        (sha+input_fingerprint) + 同输入双跑列哈希恒等 gate, 即按该规范落的确定性防线。")
    logger.info("-" * 70)


# ---------------------------------------------------------------- main
def main(argv=None) -> int:
    if sys.flags.optimize:  # 本脚本 fail-fast 闸为 assert, -O/PYTHONOPTIMIZE 下会静默失效并照常落盘
        raise SystemExit("禁以 -O/PYTHONOPTIMIZE 运行 (assert 闸失效 → 无防线静默落盘)")
    _init_stage_logging()
    ap = argparse.ArgumentParser(description="步骤 04: 替代聚合权面板 (frozenw + mainbankw)")
    ap.add_argument("--pairs", default=str(OUT_DATA / "_company_bank_cooc_pairs.parquet"))
    ap.add_argument("--registry", default="")
    ap.add_argument("--output-dir", default=str(OUT_DATA))
    ap.add_argument("--year-min", type=int, default=PANEL_YEAR_MIN)
    ap.add_argument("--year-max", type=int, default=PANEL_YEAR_MAX)
    args = ap.parse_args(argv)
    if args.year_min > args.year_max:
        raise SystemExit(2)
    t_start = time.monotonic()
    w1 = wp1()
    reg_path = Path(args.registry) if args.registry else (w1.CONFIG / "company_bank_cooc_registry.yaml")
    outdir = Path(args.output_dir)

    logger.info("--- 开始执行阶段: %s ---", Path(__file__).stem)
    logger.info("=" * 72)
    logger.info("步骤 04: 替代聚合权面板构建 (frozenw 基期冻结 + mainbankw top-1 主办银行; 计划 v3 WP1)")
    logger.info("=" * 72)
    logger.info("【功能】pair 长表 (02 产物) + 五上游银行×年测度 → 2 替代聚合权面板 (同引擎同列名,")
    logger.info("        scheme 身份由文件名承载); 与既有八权/三轨/cw-ce 两臂互为稳健性、不分主次,")
    logger.info("        各自 just-identified 并排, 禁混同一 Hansen J、禁横向 merge、禁同一 RHS 并置。")
    logger.info("【口径】frozenw: 逐 (company,track) 首个共现年份额冻结 (GPSS initial-share), 左截断不")
    logger.info("        回退, 引擎逐年限非缺失重归一; mainbankw: 当年 n_docs argmax, 三级确定性平票")
    logger.info("        (n_docs→longhit→名序), 严格 top-1 测度缺失不顺延; own-bank 上游 D4 已剔零特判。")
    logger.info("【识别定位】frozenw 只动权重时点 (堵当期共现份额与结果同源共动的 shift-share 时点内生),")
    logger.info("        mainbankw 只动聚合函数 (堵加权均值被长尾共现稀释) — 两臂正交、各与主 cw 差恰一个")
    logger.info("        自由度; frozenw 推断须 exposure-robust SE, 共同样本对齐义务见 codebook 章 D10⑤。")
    logger.info("【确定性】纯 pandas groupby/argmax (n_docs=int32 无浮点歧义), 无 BLAS 重矩阵, mergesort")
    logger.info("        稳定排序 + drop_duplicates 行原子; PYTHONHASHSEED 由 orchestrator 注入; $0 零 LLM。")
    logger.info("  ⚙ 运行配置")
    logger.info("     · 面板年窗 = [%d, %d] (来源: argparse 默认字面量, 02/03 默认的第三副本, gate 锚死;"
                " 禁从 pair 推年窗) | 三轨 = %s", args.year_min, args.year_max, "/".join(TRACKS))
    logger.info("     · 输入(pair 长表): %s | 输入(registry): %s", args.pairs, reg_path)
    logger.info("     · 输出目录: %s (面板 dta+parquet ×2 + 权重长表 ×2 + codebook 章)", outdir)
    logger.info("     · 关键库版本: pandas=%s | numpy=%s | pyarrow=%s | pyreadstat=%s",
                _pkg_ver("pandas"), _pkg_ver("numpy"), _pkg_ver("pyarrow"), _pkg_ver("pyreadstat"))
    logger.info("     · 启动 RSS %.4g MB (psutil 驻留集读数)", _rss_mb())
    _log_citations()

    # registry 载入 + 哈希锚复算 (镜像 02 L1290; 复用 01 SSOT 函数, 禁第二份实现)
    if not reg_path.exists():
        raise SystemExit(f"registry 缺失: {reg_path} — 先跑 --steps 01")
    registry = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
    import importlib
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    wp0 = importlib.import_module("01_build_company_bank_cooc_registry")
    recalc = wp0.registry_content_sha256(registry)
    if recalc != registry["meta"]["registry_sha256"]:
        raise SystemExit("registry 内容与 meta.registry_sha256 不自洽 — 重跑 01")
    logger.info("registry 哈希锚启动复算通过: %s… (04 只读 registry, 零改动零 bump)", recalc[:16])

    # pair 长表载入 + metadata stale 校验 (镜像 03: 无锚即无面板)
    pairs_path = Path(args.pairs)
    if not pairs_path.exists():
        raise SystemExit(f"pair 长表缺失: {pairs_path} — 先跑 --steps 02")
    import pyarrow.parquet as pq
    # 只读 footer 取 metadata (镜像 03 姿势, 勿 read_table 全表解压)
    meta = pq.ParquetFile(pairs_path).schema_arrow.metadata or {}
    pair_sha = (meta.get(b"registry_sha256") or b"").decode()
    pair_fp = (meta.get(b"input_fingerprint") or b"").decode()
    if pair_sha != registry["meta"]["registry_sha256"]:
        raise SystemExit(f"pair 长表 registry_sha256 ({pair_sha[:16]}…) 与盘上 registry "
                         f"({recalc[:16]}…) 不同代 — 先重跑 02 (stale 锚拒跑)")
    pair = pd.read_parquet(pairs_path)
    logger.info("pair 长表载入: %s 行 (metadata registry 锚同代 ✓) | 年窗 [%d, %d] (⚠ 来源=argparse "
                "默认字面量 2007/2025, 02/03 默认的第三副本; 禁从 pair 推年窗 — dev pair max=%d)",
                f"{len(pair):,}", args.year_min, args.year_max, int(pair["year"].max()))

    # 五上游测度库 (与 02/03 完全同源; 含一次完整测度库构建, 纯 CPU $0 非轻量)
    dp = w1.default_paths()
    for k in ("input", "panel"):
        if not dp[k].exists():
            raise SystemExit(f"必需上游缺失: {dp[k]}")
    _, _, bank_canonical, _, _, bank_company_set, company_names = w1.load_name_assets(registry)
    input21 = w1.load_input21(dp["input"], bank_canonical)
    # 双向锁第二把 (R1-P1-2): pair 的 input_fingerprint 必须与现场重建测度库的 21_full 同代 —
    # 否则"旧共现权 × 新测度"混代面板会静默落盘 (registry sha 不动时 sha 锚探不到这类漂移)
    import hashlib
    fp_now = hashlib.sha256(f"{dp['input'].stat().st_size}|{len(input21)}".encode()).hexdigest()
    if pair_fp != fp_now:
        raise SystemExit(f"pair 长表 input_fingerprint ({pair_fp[:16] or '缺失'}…) 与现场 21_full "
                         f"({fp_now[:16]}…) 缺失或不同代 — 先重跑 02 (禁旧权重×新测度混代)")
    logger.info("pair 双向锁通过: registry sha 同代 ✓ + input_fingerprint 同代 ✓ (%s…)", fp_now[:16])
    panel40 = pd.read_parquet(dp["panel"])
    align = pd.read_parquet(dp["alignment"]) if dp["alignment"].exists() else None
    benefit = pd.read_parquet(dp["benefit"]) if dp["benefit"].exists() else None
    controls = pd.read_parquet(dp["controls"]) if dp["controls"].exists() else None
    measures = w1.build_measure_library(input21, panel40, align, benefit, controls, registry)
    logger.info("银行×年测度库构建 (五上游统一, SSOT import 自 02): %s 键 × %s 列",
                f"{len(measures):,}", f"{len(measures.columns):,}")

    companies_all = sorted(company_names)  # D4: 公司序钉死 sorted (归 03 替代面板族先例)
    company_col = "company_listed_name"
    n_expect = len(companies_all) * (args.year_max - args.year_min + 1)

    # ---- scheme 1: frozenw
    t0 = time.monotonic()
    fw, fdiag, flong = build_frozen_weights(pair, args.year_max)
    n_base_rows = int((flong["year"] == flong["base_year"]).sum())
    logger.info("frozenw 权重长表: 基期行 %s → 展年后 %s 行 | (company,track) base_year 单元 %s 个 "
                "(逐年分布入 codebook 覆盖表)",
                f"{n_base_rows:,}", f"{len(fw):,}", f"{len(fdiag):,}")
    weighted_f = w1.compute_weighted_panel(fw, measures, registry)
    panel_f = assemble_panel(weighted_f, companies_all, args.year_min, args.year_max,
                             bank_company_set, company_col)
    fwide = frozen_diag_wide(fdiag, company_col)
    panel_f = panel_f.merge(fwide, how="left", left_on=company_col, right_index=True)
    fixed_f = [company_col, "year", "is_bank_company"] + list(fwide.columns)
    panel_f = panel_f[[c for c in fixed_f if c in panel_f.columns]
                      + [c for c in panel_f.columns if c not in fixed_f]]
    run_altagg_gates("frozenw", panel_f, fw, n_expect, args.year_min, args.year_max)
    fro_labels = {company_col: "上市公司中文全称", "year": "年",
                  "is_bank_company": "该公司自身是否为银行"}
    for t in TRACKS:
        fro_labels[f"base_year_{t}"] = f"基期年({t}轨): 窗内首个共现年, 份额冻结时点"
        fro_labels[f"frozen_n_banks_{t}"] = f"基期冻结银行家数({t}轨)"
    w1.write_outputs(panel_f, registry, outdir / "company_bank_frozenw_panel.dta",
                     scheme_word="基期冻结", fixed_labels=fro_labels)
    logger.info("frozenw 面板落盘: %s 行 × %s 列 (%.4g 秒) — cw=基期冻结份额加权 / ce=基期集合等权 "
                "(独立稳健臂); 左截断格与第三缺失通道详见 codebook 章",
                f"{len(panel_f):,}", f"{len(panel_f.columns):,}", time.monotonic() - t0)
    _log_result_stats("frozenw", panel_f, company_col)

    # ---- scheme 2: mainbankw
    t0 = time.monotonic()
    mw, win = build_mainbank_weights(pair)
    logger.info("mainbankw 权重长表: %s 格 (每格单行 w=1.0) | tie 率 %.4g%% | 第三级名序承重率 %.4g%%",
                f"{len(mw):,}", 100 * float(win["main_bank_tie"].mean()),
                100 * float(win["name_order_decisive"].mean()))
    weighted_m = w1.compute_weighted_panel(mw, measures, registry)
    panel_m = assemble_panel(weighted_m, companies_all, args.year_min, args.year_max,
                             bank_company_set, company_col)
    mwide = mainbank_diag_wide(win, company_col)
    mdiag = mwide.reset_index()
    mdiag["year"] = mdiag["year"].astype("int16")
    panel_m = panel_m.merge(mdiag, how="left", on=[company_col, "year"])
    for t in TRACKS:
        panel_m[f"main_bank_{t}"] = panel_m[f"main_bank_{t}"].fillna("")
    fixed_m = [company_col, "year", "is_bank_company"] + list(mwide.columns)
    panel_m = panel_m[[c for c in fixed_m if c in panel_m.columns]
                      + [c for c in panel_m.columns if c not in fixed_m]]
    run_altagg_gates("mainbankw", panel_m, mw, n_expect, args.year_min, args.year_max)
    mb_labels = {company_col: "上市公司中文全称", "year": "年",
                 "is_bank_company": "该公司自身是否为银行"}
    for t in TRACKS:
        mb_labels[f"main_bank_{t}"] = f"主办银行({t}轨): 当年共现argmax; 缺失=空串"
        mb_labels[f"main_bank_share_{t}"] = f"主办银行共现份额({t}轨)"
        mb_labels[f"main_bank_tie_{t}"] = f"主办行判定第一级平票旗标({t}轨)"
    w1.write_outputs(panel_m, registry, outdir / "company_bank_mainbankw_panel.dta",
                     scheme_word="主办银行", fixed_labels=mb_labels)
    logger.info("mainbankw 面板落盘: %s 行 × %s 列 (%.4g 秒) — cw≡ce 单银行退化恒等 (结构冗余非 bug,"
                " ce 无独立信息勿计臂数); 严格 top-1 测度缺失不顺延",
                f"{len(panel_m):,}", f"{len(panel_m.columns):,}", time.monotonic() - t0)
    _log_result_stats("mainbankw", panel_m, company_col)
    logger.info("  [Memory] 双面板装配+gate 后 RSS %.4g MB (psutil 驻留集读数, 非峰值)", _rss_mb())

    # ---- 权重长表落盘 (重构载体, metadata 内嵌 registry 锚, 镜像 pair 表)
    import pyarrow as pa
    for name, df in (("frozen", flong), ("mainbank", win)):
        tbl = pa.Table.from_pandas(df.reset_index(drop=True), preserve_index=False)
        tbl = tbl.replace_schema_metadata({**(tbl.schema.metadata or {}),
                                           b"registry_sha256": recalc.encode(),
                                           b"input_fingerprint": fp_now.encode()})
        _dst = outdir / f"_company_bank_altagg_{name}.parquet"
        _tmp = _dst.with_name(_dst.name + ".tmp")  # F8 crash-safe: tmp+replace 原子写
        pq.write_table(tbl, _tmp)
        _tmp.replace(_dst)
    logger.info("权重长表落盘 ×2: _company_bank_altagg_{frozen,mainbank}.parquet "
                "(metadata 内嵌 registry 锚; frozen 含 base_year 列 / mainbank 含平票诊断列)")

    # ---- codebook 章 upsert (幂等; 02 重写只保 03 块 → 重跑 02 后须补跑本步, README 级联义务)
    section = build_codebook_section(fdiag, win, panel_f,
                                     outdir / "company_bank_cooc_panel.parquet",
                                     company_col, args.year_min, args.year_max,
                                     "company_bank", n_alt_weights=7)
    _upsert_section(outdir / "company_bank_cooc_panel_codebook.md", section,
                    CODEBOOK_ALTAGG_BEGIN, CODEBOOK_ALTAGG_END)
    logger.info("codebook「替代聚合面板章」upsert 完成 (幂等 section-replace, 保全 03 七权章)")

    logger.info("【判读】dev T=2 语料仅 2017–2018 非零 → frozen 基期几乎全 2017、仅 2018 有非平凡冻结差,"
                " base_year=窗末年格 frozen≡cw 恒等 — 全部属预期构造退化 (生产 T=19 恢复), 非 bug。")
    logger.info("--- 阶段完成: %s (%.4g 秒) ---", Path(__file__).stem, time.monotonic() - t_start)
    return 0


if __name__ == "__main__":
    sys.exit(main())
