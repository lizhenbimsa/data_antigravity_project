#!/usr/bin/env python3
"""步骤 04: 税调替代聚合权面板 — frozenw 基期冻结权重 + mainbankw top-1 主办银行 (WP2, 镜像 listed 04)。

计划 SSOT = scripts/audit/FROZEN_BASE_WEIGHTS_AND_MAINBANK_EXECUTION_PLAN_2026-07-10.md (v3)。
输入 = 02 pair 长表 (metadata stale 校验) + 五上游测度 (经步骤 02 的 engine() 间接取用, 本文件
零跨管道 token) + registry (只读, 零改动零 bump)。
输出 = company_tax_bank_{frozenw,mainbankw}_panel.{dta,parquet} + _company_tax_bank_altagg_{frozen,mainbank}.parquet
     + codebook「替代聚合面板章」(参数化 _upsert_section, 幂等)。

纯函数 (build_frozen_weights / build_mainbank_weights / 装配 / gate) 构造口径逐条照搬母本 04
(T-D4 同款镜像纪律; 管道内自包含, 禁跨管道 import 防 token 扫描)。年窗 = 本管道 02 的
PANEL_YEAR_MIN/MAX (2011–2020) 直接 import, 禁从 pair 数据推年窗。
铁律: 与既有三权/三轨/cw-ce 两臂互为稳健性、不分主次, 各自 just-identified 并排,
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
CONFIG = HERE.parent / "config"
TRACKS = ("full", "ctx", "ss")

CODEBOOK_ALTAGG_BEGIN = "<!-- BEGIN 替代聚合面板章 (04 生成, 勿手改) -->"
CODEBOOK_ALTAGG_END = "<!-- END 替代聚合面板章 -->"

logger = logging.getLogger("04_build_company_tax_bank_altagg_panels")
if not logger.handlers:  # console 兜底 (被测试/importlib 导入时); main() 实跑时由 setup_logging 接管
    _h = logging.StreamHandler(sys.stdout)
    _h.setFormatter(logging.Formatter("[tax_altagg_panel] %(levelname)s %(message)s"))
    _h.setLevel(logging.INFO)
    logger.addHandler(_h)
    logger.setLevel(logging.INFO)


# ---------------------------------------------------------------- 本管道 02 载入 (D1, importlib 单例)
_TAX02 = None


def tax02():
    """税调 02 模块 (importlib 惰性单例): write_outputs (含 emit_dta)/load_name_assets/年窗常量,
    以及经其 engine() 间接取加权引擎与五上游载入函数 (本文件零跨管道 token, T-D10 授权路径)。"""
    global _TAX02
    if _TAX02 is None:
        if str(HERE) not in sys.path:
            sys.path.insert(0, str(HERE))
        import importlib
        _TAX02 = importlib.import_module("02_build_company_tax_bank_cooc_panel")
    return _TAX02


class _EngineLogRename(logging.Filter):
    """把借用的加权引擎 logger 记录改名为本阶段名 (R2-P2-6, 镜像本管道 03 姿势): 02 的 engine()
    只挂 02-stem 改名 Filter, 本步不自带则引擎 budget/chunk WARNING 错归 02 阶段名或失捕。
    Filter 按挂载序执行、后挂者最终改写 record.name → 本步 stem 胜出。"""

    def __init__(self, stage_name: str) -> None:
        super().__init__()
        self._stage = stage_name

    def filter(self, record: logging.LogRecord) -> bool:
        record.name = self._stage
        return True


def _attach_engine_logging(eng_logger_name: str) -> None:
    import os
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return  # 测试进程绝不接管文件日志 (与 _init_stage_logging 对称)
    eng_logger = logging.getLogger(eng_logger_name)
    if not any(isinstance(f, _EngineLogRename) for f in eng_logger.filters):
        eng_logger.addFilter(_EngineLogRename(Path(__file__).stem))
    for h in logger.handlers:
        if h not in eng_logger.handlers:
            eng_logger.addHandler(h)
    eng_logger.setLevel(logging.INFO)


def _init_stage_logging() -> None:
    """接入主管道日志基建 (core/logging.py::setup_logging): 写 company_tax_bank/logs/<stem>.log,
    每次运行覆盖, 与主管道各阶段日志完全一致。"""
    import os
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return  # WP-A: 测试进程绝不接管文件日志 (2026-07-07 审计教训)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_np_core_logging", HERE.parent / "core" / "logging.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.setup_logging(Path(__file__).stem, str(HERE / "logs"))
    logging.getLogger(Path(__file__).stem).propagate = True


def log(msg: str, warn: bool = False) -> None:
    (logger.warning if warn else logger.info)(msg)


# ---------------------------------------------------------------- codebook 幂等 upsert (镜像本管道 03 四参版)
def _upsert_section(codebook_path: Path, section_md: str, begin: str, end: str) -> None:
    """参数化 section-upsert: 只替换自己标记段, 03 双替代权章/其余正文原样保留; 无标记 → append。"""
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


# ---------------------------------------------------------------- frozenw 权重构造 (D2, 照搬母本 04)
def build_frozen_weights(pair: pd.DataFrame, year_max: int):
    """基期冻结权重长表 (口径逐条照搬母本 04, 见其 docstring): base_year=窗内首个共现年, 基期行
    展年到 [base_year, year_max], 归一化交引擎逐年限非缺失重归一; t<base_year 左截断不回退。"""
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
    """diag → company 宽表: base_year_{t} / frozen_n_banks_{t} (float64, NaN=该轨窗内无共现)。"""
    cols: dict[str, pd.Series] = {}
    for t in TRACKS:
        sub = diag[diag["track"] == t].set_index("company")
        cols[f"base_year_{t}"] = sub["base_year"].astype("float64")
        cols[f"frozen_n_banks_{t}"] = sub["n_banks"].astype("float64")
    wide = pd.DataFrame(cols)
    wide.index.name = company_col
    return wide


# ---------------------------------------------------------------- mainbankw 权重构造 (D3, 照搬母本 04)
def build_mainbank_weights(pair: pd.DataFrame):
    """top-1 主办银行权重长表 (口径逐条照搬母本 04): 当年 n_docs argmax, 三级确定性平票
    (n_docs → n_docs_longhit → 银行名码点序; sort+drop_duplicates 行原子, 禁 groupby.first)。"""
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
    win["name_order_decisive"] = (win["_n_tie2"] > 1).astype("float64")
    win = win.reset_index(drop=True)
    weights = win[["company", "bank", "year", "track"]].assign(w=1.0)
    return weights, win


def mainbank_diag_wide(win: pd.DataFrame, company_col: str) -> pd.DataFrame:
    """win → (company, year) 宽表: main_bank_{t} (str, 缺失=空串) / share / tie (float64, NaN=无共现)。"""
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


# ---------------------------------------------------------------- 面板装配 + 内联 gate (照搬母本 04)
def assemble_panel(weighted: pd.DataFrame, companies_all: list[str], y0: int, y1: int,
                   bank_company_set: set[str], company_col: str) -> pd.DataFrame:
    """满骨架 (sorted 公司序 × 年窗) 承载固定列; 加权列按值 merge (引擎输出 index 名硬编码为母本
    公司列名, 按值不按名 merge — 镜像本管道 03 姿势); ⚠ 禁 weighted.reindex(骨架) (R2-P1-1)。"""
    skeleton = pd.MultiIndex.from_product([companies_all, range(y0, y1 + 1)],
                                          names=[company_col, "year"])
    panel = pd.DataFrame(index=skeleton).reset_index()
    panel["year"] = panel["year"].astype("int16")
    panel["is_bank_company"] = panel[company_col].isin(bank_company_set).astype("int8")
    if len(weighted.columns):
        panel = panel.merge(weighted, how="left", left_on=[company_col, "year"], right_index=True)
    return panel


def run_altagg_gates(scheme: str, panel: pd.DataFrame, weights: pd.DataFrame,
                     n_rows_expect: int, y0: int, y1: int) -> None:
    """本步自带 gate (禁复用 02 run_gates — 其 n_cooc==0⇒全 NaN 闸对 frozenw 结构性不成立)。"""
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


# ---------------------------------------------------------------- codebook 章 (D11, 照搬母本 04)
def build_codebook_section(fro_diag: pd.DataFrame, win: pd.DataFrame,
                           fro_panel: pd.DataFrame, main_panel_path: Path,
                           company_col: str, y0: int, y1: int,
                           panel_prefix: str, n_alt_weights: int) -> str:
    alt_word = "七权" if n_alt_weights == 7 else "双替代权"
    n_total = 1 + n_alt_weights + 2
    L: list[str] = [
        "",
        "## 替代聚合面板 (frozenw 基期冻结 + mainbankw top-1 主办银行, 步骤 04 生成)",
        "",
        f"两面板 `{panel_prefix}_{{frozenw,mainbankw}}_panel.{{dta,parquet}}` 与媒体主面板同引擎同列名",
        "(`cw_/ce_{基名}_{track}`, 同一短名表), scheme 身份由文件名承载。**本章 2 面板与主面板/",
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
        "⚠ 税调窗 2011–2020: 窗前 2007–2010 语料存在但 pair 表不含 (ABS⟂PANEL 分离), 窗前基期臂",
        "DEFER 生产机 — 对 2011 前已有媒体关系的企业, initial share 是窗口截断首年非真 pre-period 快照。",
        "",
        "### frozenw 发表义务五句 (D10, 非可选)",
        "① shift-share 推断须 exposure-robust SE (Adão, Kolesár & Morales 2019, QJE), 常规聚类 SE 过窄。",
        "② 基期 = 首个入样共现年属研究者选择 (Goldsmith-Pinkham, Sorkin & Swift 2020, AER 的",
        "initial-share 构造); pair 长表在, 可 $0 重定基期 (D17 重构通道)。",
        "③ 识别假设 = 基期份额对企业结果的影响仅经银行冲击通道 (exogenous shares 叙事)。",
        "④ staggered 基期三重偏离: 基期年逐企业异质且与媒体首次可见时点相关 (非统一 pre-period 快照)",
        "— 识别叙事须条件于企业首现年成立; 基期时点本身内生于媒体可见度; 基期越晚 frozen 与当期权重",
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
        "与 cw 臂并排 + main_bank_share 低值格降权判读。中小企业单一主办行构念在税调样本 (44,771 家)",
        "贴合度高于上市样本。构念谱系 = Petersen & Rajan (1994, JF 49(1), 3-37) 关系借贷; Hoshi,",
        "Kashyap & Scharfstein (1991, QJE 106(1), 33-60) 主银行制; Bharath, Dahiya, Saunders &",
        "Srinivasan (2011, RFS 24(4), 1141-1203) 关系强度。",
        "",
        "### 诊断列与缺失语义 (D4)",
        "| 列 | dtype | 缺失语义 |",
        "|---|---|---|",
        "| `base_year_{track}` | float64 | NaN = 该轨窗内无共现 (逐企业恒定, 随骨架广播全年) |",
        "| `frozen_n_banks_{track}` | float64 | 基期银行家数; NaN 同上 (不填 0) |",
        "| `main_bank_{track}` | str | **缺失 = 空串 \"\"** (pyreadstat 字符串缺失落 Stata 空串非 `.`, 与数值列 NaN=`.` 不同套) |",
        "| `main_bank_share_{track}` | float64 | ∈(0,1]; NaN = 无共现 |",
        "| `main_bank_tie_{track}` | float64 | 0/1; NaN = 无共现 |",
        "",
        "ss 轨基期/主办行判定按 `n_docs` 含 fallback 口径 (`n_docs_strict`/`n_docs_longhit` 口径变体臂",
        "经 pair 表 $0 可重构, 刻意不物化)。权重逐轨 (与媒体主面板同语义, 与双替代权面板 track-less",
        "权重不同, 勿套错)。级联义务: pair 长表重生 (重跑 02) ⇒ 本章两面板与本章内容 stale, 且 02 整",
        "文件重写 codebook 只保留 03 标记块、本章会被抹掉 — **重跑 02 后须补跑 04**。",
        "",
        "### 刻意不做 (§1b 归档, 一句话理由)",
        "GIV (cw−ce; 估计框架另立门户, 依赖 Gabaix-Koijen 因子结构假设) / leave-one-out (真 LOO 须回",
        "文章级重算, 窄版被上游 D4 剔除天然覆盖) / 关系存量-时间衰减权重 (与 frozenw 答同一威胁, 冗余",
        "梯子 — 先验判断, 质疑时经 pair 表实测) / frozen×mainbank 交叉臂 (梯子禁交叉) / 窗前 2007–2010",
        "基期臂 (pair 表被 02 裁到面板窗, DEFER 生产机) / mainbank top-k≥2 (top-1 与 cw 的插值臂, 冗余) /",
        "strict-longhit 口径变体 (pair 表 $0 可重构) / Stata 2SLS+AKM 模板 (papers 侧财务面板接入时)。",
        "",
    ]
    L += ["### base_year 分布 (frozenw; 逐轨, 判真零 vs 左截断)", "",
          "| base_year | " + " | ".join(TRACKS) + " |", "|---|---|---|---|"]
    byr = {t: fro_diag.loc[fro_diag["track"] == t, "base_year"].value_counts() for t in TRACKS}
    years_seen = sorted(set().union(*[set(v.index) for v in byr.values()])) if len(fro_diag) else []
    for y in years_seen:
        L.append(f"| {y} | " + " | ".join(str(int(byr[t].get(y, 0))) for t in TRACKS) + " |")
    comp_multi = fro_diag.groupby("company")["base_year"].nunique()
    n_multi = int((comp_multi > 1).sum())
    L += ["", f"三轨 base_year 不一致企业数 = {n_multi} / 有共现企业 {len(comp_multi)} "
          f"({100 * n_multi / max(len(comp_multi), 1):.4g}%)。", ""]
    L += ["### mainbankw 覆盖 (逐年非缺格点数 / tie 率 / 第三级名序承重率)", "",
          "| 年 | 非缺格点 (full/ctx/ss) | tie 率 | 名序承重率 |", "|---|---|---|---|"]
    for y in sorted(win["year"].unique()):
        wy = win[win["year"] == y]
        per_t = "/".join(str(int((wy["track"] == t).sum())) for t in TRACKS)
        L.append(f"| {int(y)} | {per_t} | {100 * float(wy['main_bank_tie'].mean()):.4g}% "
                 f"| {100 * float(wy['name_order_decisive'].mean()):.4g}% |")
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
    L += ["", f"面板年窗 [{y0}, {y1}]; dev 语料窗内 8/10 年零共现属预期退化 (生产语料恢复),",
          "base_year=窗末年企业 frozen≡cw 逐点恒等属构造退化非 bug。生产机回填义务: 重归一触发占比 /",
          "main-bank 测度缺失格点占比 / frozen-cw 权重向量逐年 Spearman / main bank 翻转率 (§9)。", ""]
    return "\n".join(L)


# ---------------------------------------------------------------- 文献锚点 (D9: 仅审计白名单内 5 条入日志)
def _log_citations() -> None:
    logger.info("【文献锚点】shift-share / 关系借贷设计谱系 (5 条, 全部在 audit_dois 白名单池;")
    logger.info("  Chodorow-Reich 2014 / HKS 1991 / Bharath 2011 三条池缺, 仅入 codebook 散文不入日志):")
    logger.info("  · Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when,")
    logger.info("    why, and how. American Economic Review, 110(8), 2586–2624.")
    logger.info("    https://doi.org/10.1257/aer.20181047 — initial-share 冻结构造与 exogenous shares 叙事")
    logger.info("  · Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share research")
    logger.info("    designs. The Review of Economic Studies, 89(1), 181–213.")
    logger.info("    https://doi.org/10.1093/restud/rdab030 — shift-share 拟实验识别框架")
    logger.info("  · Adão, R., Kolesár, M., & Morales, E. (2019). Shift-share designs: Theory and inference.")
    logger.info("    The Quarterly Journal of Economics, 134(4), 1949–2010.")
    logger.info("    https://doi.org/10.1093/qje/qjz025 — exposure-robust SE (frozenw 推断义务)")
    logger.info("  · Petersen, M. A., & Rajan, R. G. (1994). The benefits of lending relationships: Evidence")
    logger.info("    from small business data. The Journal of Finance, 49(1), 3–37.")
    logger.info("    https://doi.org/10.1111/j.1540-6261.1994.tb04418.x — 主办银行/关系借贷构念 (mainbankw)")
    logger.info("  · Khwaja, A. I., & Mian, A. (2008). Tracing the impact of bank liquidity shocks: Evidence")
    logger.info("    from an emerging market. American Economic Review, 98(4), 1413–1442.")
    logger.info("    https://doi.org/10.1257/aer.98.4.1413 — 银企配对传导设计先例")


# ---------------------------------------------------------------- main
def main(argv=None) -> int:
    if sys.flags.optimize:  # 本脚本 fail-fast 闸为 assert, -O/PYTHONOPTIMIZE 下会静默失效并照常落盘
        raise SystemExit("禁以 -O/PYTHONOPTIMIZE 运行 (assert 闸失效 → 无防线静默落盘)")
    _init_stage_logging()
    w2 = tax02()
    ap = argparse.ArgumentParser(description="步骤 04: 税调替代聚合权面板 (frozenw + mainbankw)")
    ap.add_argument("--pairs", default=str(OUT_DATA / "_company_tax_bank_cooc_pairs.parquet"))
    ap.add_argument("--registry", default=str(CONFIG / "company_tax_bank_cooc_registry.yaml"))
    ap.add_argument("--output-dir", default=str(OUT_DATA))
    ap.add_argument("--year-min", type=int, default=w2.PANEL_YEAR_MIN)
    ap.add_argument("--year-max", type=int, default=w2.PANEL_YEAR_MAX)
    ap.add_argument("--no-emit-dta", action="store_true",
                    help="dev 快速模式: 跳过 dta 落盘只写 parquet (dev 产物不可回归; 生产勿用)")
    args = ap.parse_args(argv)
    if args.year_min > args.year_max:
        raise SystemExit(2)
    t_start = time.monotonic()
    eng = w2.engine()
    _attach_engine_logging(eng.logger.name)  # 后挂 Filter 胜出 → 引擎行归本阶段名 (R2-P2-6)
    reg_path = Path(args.registry)
    outdir = Path(args.output_dir)

    logger.info("--- 开始执行阶段: %s ---", Path(__file__).stem)
    logger.info("=" * 72)
    logger.info("步骤 04: 税调替代聚合权面板构建 (frozenw 基期冻结 + mainbankw top-1 主办银行; 计划 v3 WP2)")
    logger.info("=" * 72)
    logger.info("【功能】pair 长表 (02 产物) + 五上游银行×年测度 → 2 替代聚合权面板 (同引擎同列名,")
    logger.info("        scheme 身份由文件名承载); 与既有三权/三轨/cw-ce 两臂互为稳健性、不分主次,")
    logger.info("        各自 just-identified 并排, 禁混同一 Hansen J、禁横向 merge、禁同一 RHS 并置。")
    logger.info("【口径】frozenw: 逐 (company,track) 首个共现年份额冻结 (GPSS initial-share), 左截断不")
    logger.info("        回退, 引擎逐年限非缺失重归一; mainbankw: 当年 n_docs argmax, 三级确定性平票")
    logger.info("        (n_docs→longhit→名序), 严格 top-1 测度缺失不顺延; own-bank 上游 D4 已剔零特判。")
    _log_citations()

    # registry 载入 + 哈希锚复算 (镜像 02; 复用税调 01 SSOT 函数, 禁第二份实现)
    if not reg_path.exists():
        raise SystemExit(f"registry 缺失: {reg_path} — 先跑 --steps 01")
    registry = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
    import importlib
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    wp0 = importlib.import_module("01_build_company_tax_bank_cooc_registry")
    recalc = wp0.registry_content_sha256(registry)
    if recalc != registry["meta"]["registry_sha256"]:
        raise SystemExit("registry 内容与 meta.registry_sha256 不自洽 — 重跑 01")
    logger.info("registry 哈希锚启动复算通过: %s… (04 只读 registry, 零改动零 bump)", recalc[:16])

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
    logger.info("pair 长表载入: %s 行 (metadata registry 锚同代 ✓) | 年窗 [%d, %d] (来源 = 本管道 02 "
                "PANEL_YEAR_MIN/MAX 常量 import; 禁从 pair 推年窗 — dev pair max=%d)",
                f"{len(pair):,}", args.year_min, args.year_max, int(pair["year"].max()))

    # 五上游测度库 (经 engine() 与 02/03 完全同源; 含一次完整测度库构建, 纯 CPU $0 非轻量)
    dp = eng.default_paths()
    for k in ("input", "panel"):
        if not dp[k].exists():
            raise SystemExit(f"必需上游缺失: {dp[k]}")
    _, _, bank_canonical, _, _, bank_company_set, company_names = w2.load_name_assets(registry)
    input21 = eng.load_input21(dp["input"], bank_canonical)
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
    measures = eng.build_measure_library(input21, panel40, align, benefit, controls, registry)
    logger.info("银行×年测度库构建 (五上游统一, 经 engine() SSOT 复用): %s 键 × %s 列",
                f"{len(measures):,}", f"{len(measures.columns):,}")

    companies_all = sorted(company_names)  # D4: 公司序钉死 sorted (归 03 替代面板族先例)
    company_col = "company_tax_name"
    n_expect = len(companies_all) * (args.year_max - args.year_min + 1)

    # ---- scheme 1: frozenw
    t0 = time.monotonic()
    fw, fdiag, flong = build_frozen_weights(pair, args.year_max)
    n_base_rows = int((flong["year"] == flong["base_year"]).sum())
    logger.info("frozenw 权重长表: 基期行 %s → 展年后 %s 行 | (company,track) base_year 单元 %s 个 "
                "(逐年分布入 codebook 覆盖表)", f"{n_base_rows:,}", f"{len(fw):,}", f"{len(fdiag):,}")
    weighted_f = eng.compute_weighted_panel(fw, measures, registry)
    panel_f = assemble_panel(weighted_f, companies_all, args.year_min, args.year_max,
                             bank_company_set, company_col)
    fwide = frozen_diag_wide(fdiag, company_col)
    panel_f = panel_f.merge(fwide, how="left", left_on=company_col, right_index=True)
    fixed_f = [company_col, "year", "is_bank_company"] + list(fwide.columns)
    panel_f = panel_f[[c for c in fixed_f if c in panel_f.columns]
                      + [c for c in panel_f.columns if c not in fixed_f]]
    run_altagg_gates("frozenw", panel_f, fw, n_expect, args.year_min, args.year_max)
    fro_labels = {company_col: "税调企业名称 (全称)", "year": "年",
                  "is_bank_company": "银行系税调企业 (D4)"}
    for t in TRACKS:
        fro_labels[f"base_year_{t}"] = f"基期年({t}轨): 窗内首个共现年, 份额冻结时点"
        fro_labels[f"frozen_n_banks_{t}"] = f"基期冻结银行家数({t}轨)"
    w2.write_outputs(panel_f, registry, outdir / "company_tax_bank_frozenw_panel.dta",
                     scheme_word="基期冻结", fixed_labels=fro_labels,
                     emit_dta=not args.no_emit_dta)
    logger.info("frozenw 面板落盘: %s 行 × %s 列 (%.4g 秒) — cw=基期冻结份额加权 / ce=基期集合等权 "
                "(独立稳健臂); 左截断格与第三缺失通道详见 codebook 章",
                f"{len(panel_f):,}", f"{len(panel_f.columns):,}", time.monotonic() - t0)

    # ---- scheme 2: mainbankw
    t0 = time.monotonic()
    mw, win = build_mainbank_weights(pair)
    logger.info("mainbankw 权重长表: %s 格 (每格单行 w=1.0) | tie 率 %.4g%% | 第三级名序承重率 %.4g%%",
                f"{len(mw):,}", 100 * float(win["main_bank_tie"].mean()),
                100 * float(win["name_order_decisive"].mean()))
    weighted_m = eng.compute_weighted_panel(mw, measures, registry)
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
    mb_labels = {company_col: "税调企业名称 (全称)", "year": "年",
                 "is_bank_company": "银行系税调企业 (D4)"}
    for t in TRACKS:
        mb_labels[f"main_bank_{t}"] = f"主办银行({t}轨): 当年共现argmax; 缺失=空串"
        mb_labels[f"main_bank_share_{t}"] = f"主办银行共现份额({t}轨)"
        mb_labels[f"main_bank_tie_{t}"] = f"主办行判定第一级平票旗标({t}轨)"
    w2.write_outputs(panel_m, registry, outdir / "company_tax_bank_mainbankw_panel.dta",
                     scheme_word="主办银行", fixed_labels=mb_labels,
                     emit_dta=not args.no_emit_dta)
    logger.info("mainbankw 面板落盘: %s 行 × %s 列 (%.4g 秒) — cw≡ce 单银行退化恒等 (结构冗余非 bug,"
                " ce 无独立信息勿计臂数); 严格 top-1 测度缺失不顺延",
                f"{len(panel_m):,}", f"{len(panel_m.columns):,}", time.monotonic() - t0)

    # ---- 权重长表落盘 (重构载体, metadata 内嵌 registry 锚, 镜像 pair 表)
    import pyarrow as pa
    for name, df in (("frozen", flong), ("mainbank", win)):
        tbl = pa.Table.from_pandas(df.reset_index(drop=True), preserve_index=False)
        tbl = tbl.replace_schema_metadata({**(tbl.schema.metadata or {}),
                                           b"registry_sha256": recalc.encode(),
                                           b"input_fingerprint": fp_now.encode()})
        _dst = outdir / f"_company_tax_bank_altagg_{name}.parquet"
        _tmp = _dst.with_name(_dst.name + ".tmp")  # F8 crash-safe: tmp+replace 原子写
        pq.write_table(tbl, _tmp)
        _tmp.replace(_dst)
    logger.info("权重长表落盘 ×2: _company_tax_bank_altagg_{frozen,mainbank}.parquet "
                "(metadata 内嵌 registry 锚; frozen 含 base_year 列 / mainbank 含平票诊断列)")

    section = build_codebook_section(fdiag, win, panel_f,
                                     outdir / "company_tax_bank_cooc_panel.parquet",
                                     company_col, args.year_min, args.year_max,
                                     "company_tax_bank", n_alt_weights=2)
    _upsert_section(outdir / "company_tax_bank_cooc_panel_codebook.md", section,
                    CODEBOOK_ALTAGG_BEGIN, CODEBOOK_ALTAGG_END)
    logger.info("codebook「替代聚合面板章」upsert 完成 (幂等 section-replace, 保全 03 双替代权章)")

    logger.info("【判读】dev 语料仅 2017–2018 非零 (税调窗 2011–2020 内 8/10 年零共现) → frozen 的")
    logger.info("  2011–2016 全左截断 NaN、mainbank 同年大面积 NaN — 全部属预期退化 (生产语料恢复), 非 bug。")
    logger.info("--- 阶段完成: %s (%.4g 秒) ---", Path(__file__).stem, time.monotonic() - t_start)
    return 0


if __name__ == "__main__":
    sys.exit(main())
