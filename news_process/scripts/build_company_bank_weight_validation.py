"""WP5 — 七替代权源构建 + 八权面板批量生产 + 互验 (COMPANY_BANK_COOC_PANEL_EXECUTION_PLAN v34).

三层产物 (DV1, 均不入库, 共 22 个 data/processed 文件):
  ① 七套替代权长表 _company_bank_altweights_{scheme}.parquet (统一 schema company/bank/year/w[+稳健臂])
  ② 七替代权真实面板 company_bank_{scheme}w_panel.{dta,parquet} ×7 (D18 单引擎多权源)
  ③ 互验报告 _company_bank_weight_validation.md (DV5 五件套 + ⑥ 顶刊披露包 + 未映射审计附录)
另: 主 codebook 「七替代权面板」章 section-replace 幂等替换 (v33 J2)。

权源: config/ 四份商业 dta (借款/分支/董监高/股东)。银行名 canonical 化 = DV2 判定序 (本模块
单函数 canon_bank, 七表共用)。DV2_CONSTANTS 由 WP0 序列化入 registry `dv2_constants` 区段 (双向锁)。
独立派生数据脚本, 不注册 DAG; $0 纯 pandas。
"""
from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "processed"
CONFIG = REPO / "config"
TRACKS = ("full", "ctx", "ss")

logger = logging.getLogger("company_bank_weight_validation")
if not logger.handlers:
    _h = logging.StreamHandler(sys.stdout)
    _h.setFormatter(logging.Formatter("[w8] %(levelname)s %(message)s"))
    logger.addHandler(_h)
    logger.setLevel(logging.INFO)


def log(msg: str, warn: bool = False) -> None:
    (logger.warning if warn else logger.info)(msg)


# ================================================================ DV2 常量 (v31 冻结, WP0 落 registry)
DV2_CONSTANTS: dict = {
    # ⓪ 不可名指闸词表 (v27 + v33 扩四词)
    "unnameable": ["银团", "牵头", "等金融机构", "等银行", "或非银行",
                   "参团", "包括但不限于", "在内的多家", "多家银行"],
    # 境外闸最小必含清单 (v29; 国家/地区词段 + 法人尾缀段)
    "overseas_words": ["越南", "新加坡", "香港", "澳门", "台湾", "韩国", "日本", "泰国",
                       "马来西亚", "印尼", "菲律宾", "美国", "英国", "法国", "德国", "瑞士",
                       "荷兰", "澳大利亚", "加拿大", "亚洲", "欧洲", "国际", "海外"],
    "foreign_suffixes": ["AG", "N.A.", "Ltd", "LTD", "BRANCH", "PLC", "S.A.", "N.V.",
                         "Bhd", "Limited"],
    # 泛称黑名单 (head 级施加, v27)
    "generic_heads": ["银行"],
    # 尾段附属实体黑名单 (v29)
    "affiliate_tail": ["村镇", "信托", "证券", "培训", "工会", "劳动服务", "劳司",
                       "房地产", "咨询", "技协", "租赁", "基金", "保险", "服务公司", "服务部",
                       "协会", "委员会", "监督管理"],  # (R2 P2-1) 银行业协会/银监会类穿透封死
    # 股东托管/产品账户闸 (DV4g)
    "custodian_words": ["基金", "资管", "理财", "信托", "计划", "专户", "组合"],
    "custodian_dashes": ["-", "－", "—"],
    # 股东银行三产/工会附属闸 (v29)
    "sanchan_words": ["工会", "劳动服务", "劳司", "培训中心", "房地产", "咨询",
                      "服务公司", "服务部", "技协", "证券"],
    # head 内豁免家族 (v33 S2-P1: 境内法人行 canonical 自含境外词者, 8 家)
    "head_exempt_note": "厦门国际银行/中信银行国际(中国)/法国兴业银行(中国)/法国巴黎银行(中国)/"
                        "摩根士丹利国际银行(中国)/澳大利亚和新西兰银行(中国)/瑞士银行(中国)/宁波通商银行",
    # 公司缺 city 境外占位 (DV4b ③)
    "city_overseas": ["大开曼", "香港特别行政区"],
    "city_placeholder": ["省直辖县级行政区划", "自治区直辖县级行政区划"],
}

MISSING_SET = {"None", "nan", ""}
COMPANY_SUFFIX_RE = re.compile(r"(股份有限公司|有限责任公司|有限公司|股份公司)$")
PAREN_RE = re.compile(r"[（(]([^（）()]*)[)）]")


def norm(s: pd.Series) -> pd.Series:
    """DV4 通则 ⓐ: dtype 规范化 (v29 配方锚定 r'\\.0$' 正则)。"""
    return s.astype(str).str.replace(r"\.0$", "", regex=True)


def is_missing(s: pd.Series) -> pd.Series:
    return norm(s).isin(MISSING_SET)


# ================================================================ DV2 canonical 化 (七表共用单函数)
class BankCanon:
    def __init__(self):
        banks = yaml.safe_load((CONFIG / "bank_names.json").read_text(encoding="utf-8"))
        self.variant_to_canon: dict[str, str] = {}
        for b in banks:
            for v in b["variants"]:
                self.variant_to_canon.setdefault(v, b["bank_name"])
        self.canonicals = {b["bank_name"] for b in banks}
        self.audit: dict[str, int] = {}  # 未映射审计 (名称 → 频次)
        self._memo: dict[str, str | None] = {}
        c = DV2_CONSTANTS
        assert set(c["overseas_words"]) >= {"越南", "新加坡", "亚洲", "国际"}  # DV6 常量 ⊇ 最小集
        self._overseas = c["overseas_words"]
        self._fsuffix = c["foreign_suffixes"]
        self._unname = c["unnameable"]
        self._tail = c["affiliate_tail"]

    def _audit_add(self, name: str) -> None:
        self.audit[name] = self.audit.get(name, 0) + 1

    def _strip_paren(self, name: str):
        """返回 (剥括注后名称, 括注列表)。"""
        parens = PAREN_RE.findall(name)
        return PAREN_RE.sub("", name), parens

    def _overseas_hits(self, name: str) -> list[str]:
        hits = [w for w in self._overseas if w in name]
        hits += [sfx for sfx in self._fsuffix if sfx in name]
        return hits

    def canon(self, raw) -> str | None:
        """DV2 判定序: ⓪₀ → ⓪ → ① (原名/剥公司后缀精确查表, 括注规则) → ② (截断+闸) → ③ 审计。"""
        name = str(raw).strip() if raw is not None else ""
        cached = self._memo.get(name, "\x00")
        if cached != "\x00":
            self._audit_replay(name, cached)
            return cached
        result = self._canon_uncached(name)
        self._memo[name] = result
        self._audit_replay(name, result)
        return result

    def _audit_replay(self, name: str, result) -> None:
        if result is None:
            self._audit_add(name if name not in MISSING_SET else "<MISSING>")

    def _canon_uncached(self, name: str) -> str | None:
        V = self.variant_to_canon
        # ⓪₀ 输入缺失闸 (v32)
        if name in MISSING_SET:
            return None
        # ⓪ 不可名指闸
        if any(w in name for w in self._unname):
            return None
        # ① 原名/剥公司后缀精确查表
        if name in V:
            return V[name]
        base = COMPANY_SUFFIX_RE.sub("", name)
        if base in V:
            return V[base]
        # 括注规则: 仅 '中国' 或 '原*' 可剥 (剥后重试); 其余 = 不可剥括注 → 禁入 ② (v33 S2-P0)
        stripped, parens = self._strip_paren(base)
        if parens:
            if all(p == "中国" or p.startswith("原") for p in parens):
                if stripped in V:
                    return V[stripped]
                sb = COMPANY_SUFFIX_RE.sub("", stripped)
                if sb in V:
                    return V[sb]
                base = sb  # 剥后进入后续判定 (含境外闸/截断)
            else:
                return None  # 不可剥括注 → 精确失败即落审计, 绝不截断
        # 境外主体闸 (v27/v29) + head 内豁免 (v33 S2-P1)
        has_bank = "银行" in base
        head = (base.split("银行", 1)[0] + "银行") if has_bank else base
        tail = base.split("银行", 1)[1] if has_bank else ""
        os_hits = self._overseas_hits(base)
        if os_hits:
            exempt = head in V and all(w in head for w in os_hits)
            if not exempt:
                return None
        if not has_bank:
            return None  # ③
        # ② 泛称黑名单 head 级 (v27): head=="银行" → None (含"银行等金融机构"类复合泛称)
        if head == "银行":
            return None
        # ② 尾段附属实体黑名单 (v29): 截断后尾段非空 ∧ 含黑名单词 → None
        if tail and any(w in tail for w in self._tail):
            return None
        # ② 截至首个"银行"剥分支行再查 (含"中国"前缀增删双向)
        for cand in (head, head[2:] if head.startswith("中国") else "中国" + head):
            if cand in V:
                return V[cand]
        return None  # ③ 未映射审计 (canon() 外壳记账)


# ================================================================ 通则 ⓑ 年窗两层
def year_two_layer(years: pd.Series, year_min: int, year_max: int, tag: str,
                   sys_exit_frac: float = 0.005) -> pd.Series:
    """返回 keep mask; 第一层 (解析失败 ∨ ∉[1990,2035]) 剔+WARNING (>0.5%→SystemExit);
    第二层 (窗外真实年) 剔+INFO。"""
    bad = years.isna() | (years < 1990) | (years > 2035)
    n_bad = int(bad.sum())
    if n_bad:
        frac = n_bad / len(years)
        log(f"{tag}: 第一层脏年剔除 {n_bad} ({frac:.3%})", warn=True)
        if frac > sys_exit_frac:
            raise SystemExit(f"{tag} 第一层脏年占比 {frac:.3%} > {sys_exit_frac:.1%}")
    outwin = ~bad & ((years < year_min) | (years > year_max))
    if outwin.any():
        log(f"{tag}: 第二层窗外年裁剪 {int(outwin.sum())} (INFO, 属预期)")
    return ~bad & ~outwin


def parse_year(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s.astype(str), errors="coerce").dt.year


# ================================================================ 公司键 (DV3)
def load_companies() -> tuple[dict[str, str], pd.DataFrame]:
    comp = yaml.safe_load((CONFIG / "company_listed_names.yaml").read_text(encoding="utf-8"))["companies"]
    code_map = {str(c["stock_code"]).zfill(6): c["company_listed_name"] for c in comp}
    geo = pd.DataFrame([{"company": c["company_listed_name"],
                         "city": c.get("city") or "", "district": c.get("district") or ""}
                        for c in comp])
    return code_map, geo


# ================================================================ DV4a 贷款权 (四臂)
def _syndicate_split(loanbank: str) -> list[tuple[str, bool]]:
    """银团四则 (v31/v33/v34): 括注平衡拆分 + 预清洗四则。返回 [(成员串, is_lead)]。"""
    s = loanbank
    # ⓐ 行级先剥整串括注、括注内容并回成员串再拆 (括注内分隔符不作分隔)。
    # (R2 P2-4) 纯修饰括注 '(牵头行)'/'(牵头)' 不并回 — 就地换成修饰词标在宿主成员上
    s = re.sub(r"[（(](牵头行|牵头)[)）]", r"\1", s)
    inner = "、".join(PAREN_RE.findall(s))
    s = PAREN_RE.sub("", s)
    if inner:
        s = (s + "、" + inner) if s.strip("、,，") else inner
    members = [m for m in re.split(r"[、,，]", s) if m.strip()]
    cleaned: list[tuple[str, bool]] = []
    for m in members:
        m = m.strip()
        is_lead = "牵头" in m  # ⓕ (v33 J1) 剥"牵头"前记录 lead 身份
        m = re.sub(r"(等金融机构|等银行)$", "", m)          # ① 剥串尾列举尾缀
        m = m.replace("牵头行", "").replace("牵头", "")      # ② 剥修饰词
        m = re.sub(r"^银团[（(]?", "", m)                    # ③ 剥串首 银团(/银团 前缀
        m = m.strip("()（）")                                # ③ 孤立括号残片
        m = re.sub(r"^其中", "", m)                          # ④ (v34) 剥串首 其中
        m = re.sub(r"为$", "", m)                            # ④ (v34) 剥串尾孤立 为
        m = m.strip()
        # ⓒ 连接词 和|及 不作二次分隔符 (防误伤含"和"行名)
        if m:
            cleaned.append((m, is_lead))
    return cleaned


def build_weight_loan(raw_df: pd.DataFrame, canon: BankCanon, companies: dict[str, str],
                      year_min: int, year_max: int, check_anchors: bool = True) -> pd.DataFrame:
    df = raw_df
    # 行数锚 (v27, 精确等值, 载入规范化后、漏斗前; mock 测试传 check_anchors=False)
    if check_anchors:
        n_issign = int((norm(df["IsSign"]) == "1").sum())
        assert n_issign == 14929, f"贷款 IsSign=='1' 锚 {n_issign} ≠ 14,929 (数据商改版信号)"
        assert df["EventID"].nunique() == len(df), "EventID 零重复断言失败"
    f = df[norm(df["IsSign"]) == "1"]
    f = f[norm(f["IsTermination"]) != "1"]
    f = f[f["RelateToLoanCompanyCode"].isin(["P7514", "P7502"])].copy()
    if check_anchors:
        n_cny = int((norm(f["CurrencyCode"]) == "CNY").sum())
        assert n_cny == 14127, f"贷款 CNY 臂锚 {n_cny} ≠ 14,127 (v31 R4 剧本1封死)"
    # 年份三级回退 y0 (逐级传递: 非空但解析失败视同缺失落下一级); 三级全失败按通则 ⓑ 第一层剔
    y0 = parse_year(f["LoanStarDate"]).fillna(parse_year(f["SignDate"])).fillna(
        parse_year(f["DeclareDate"]))
    bad = y0.isna() | (y0 < 1990) | (y0 > 2035)
    if bad.any():
        frac = bad.sum() / len(f)
        log(f"贷款 y0: 第一层脏年剔除 {int(bad.sum())} ({frac:.3%})", warn=True)
        if frac > 0.005:
            raise SystemExit(f"贷款 y0 第一层脏年占比 {frac:.3%} > 0.5%")
    f, y0 = f[~bad], y0[~bad]
    # 存续终点 y1 三级: LoanEndDate → y0+ceil(LoanTerm) → y0 单年 (v27 P0; LoanTerm 单位=年)
    y_end = parse_year(f["LoanEndDate"])
    term = pd.to_numeric(f["LoanTerm"], errors="coerce")
    y1 = y_end.copy()
    use_term = y1.isna() & term.notna()
    y1[use_term] = y0[use_term] + np.ceil(term[use_term])
    dur_observed = y1.notna()  # w_dur 臂判据 (v33): y1 来自 LoanEndDate/LoanTerm 的事件
    y1 = y1.fillna(y0)
    y1 = np.minimum(y1, y0 + 30)  # 30 年帽 (LoanTerm=1000 脏值/y1 max=2056 双依据)
    y1 = np.maximum(y1, y0)       # y1≥y0 守卫 (v28)
    f["ev_y0"], f["ev_y1"], f["ev_dur"] = y0.astype(int), y1.astype(int), dur_observed
    f["company"] = norm(f["Symbol"]).str.zfill(6).map(companies)
    n_unmapped = int(f["company"].isna().sum())
    if n_unmapped:
        log(f"贷款: 公司码未命中清单 {n_unmapped} 行 (清单外退市/新主体)")
    f = f.dropna(subset=["company"])
    f["ev_cny"] = norm(f["CurrencyCode"]) == "CNY"
    f["ev_amt"] = pd.to_numeric(f["MaxLoan"], errors="coerce")
    f["ev_synd"] = norm(f["IsBankGroup"]) == "1"
    f["ev_own"] = f["RelateToLoanCompanyCode"] == "P7514"
    rows: list[tuple] = []
    audit_rows: list[str] = []
    for r in f.itertuples(index=False):
        lb = str(r.LoanBank)
        a_cny = r.ev_amt if (r.ev_cny and pd.notna(r.ev_amt)) else np.nan
        if r.ev_synd and re.search(r"[、,，]", lb):
            members = _syndicate_split(lb)
            uniq: dict[str, bool] = {}  # ⓔ k = canonical 去重后成功映射数
            n_mapped_str = 0
            for m, lead in members:
                c = canon.canon(m)
                if c:
                    uniq[c] = uniq.get(c, False) or lead
                    n_mapped_str += 1
                elif re.search(r"[和及]", m):  # ⓒ 双行名成员串仅部分可名指 → 落审计
                    audit_rows.append(f"银团连接词成员串待裁决: {m} (原串 {lb})")
            k = len(uniq)
            if k == 0:  # (v30) k=0 守卫: 整笔落未映射审计, 禁除零
                audit_rows.append(f"银团整笔 k=0: {lb}")
                continue
            for c, lead in uniq.items():
                if lead:  # ⓕ (v33 J1) 牵头行身份物化入审计附录 (canonical 仍 1/k)
                    audit_rows.append(f"银团牵头行: {c} (k={k}, 原串 {lb})")
                rows.append((r.company, c, r.ev_y0, r.ev_y1,
                             (a_cny / k) if pd.notna(a_cny) else np.nan,
                             r.ev_own, r.ev_dur, lead, 1.0 / k))
        elif r.ev_synd:
            c = canon.canon(lb)  # 无分隔符银团: ⓪ 闸多数拦; canon 成功 → 强制审计不入权 (v33)
            if c:
                audit_rows.append(f"银团无分隔符 canon 成功 (强制人工裁决, 不入权): {lb} → {c}")
            continue
        else:  # 非银团勿拆 (外资行英文名内标点)
            c = canon.canon(lb)
            if c is None:
                continue
            rows.append((r.company, c, r.ev_y0, r.ev_y1, a_cny, r.ev_own, r.ev_dur, False, 1.0))
    ev = pd.DataFrame(rows, columns=["company", "bank", "y0", "y1", "amt", "own", "dur_obs",
                                     "is_lead", "cnt_share"])
    canon.audit_extra = getattr(canon, "audit_extra", []) + audit_rows
    if ev.empty:
        return pd.DataFrame(columns=["company", "bank", "year", "w", "w_cnt", "w_own", "w_dur"])
    # 存续展开: 闭区间年集 {y0..min(y1, y0+30)} 每年一行 (存量暴露, v28)
    ev = ev.reset_index(drop=True)
    reps = (ev["y1"] - ev["y0"] + 1).astype(int)
    exp = ev.loc[ev.index.repeat(reps)].copy()
    exp["year"] = (exp["y0"] + exp.groupby(level=0).cumcount()).astype(int)
    n_out = int(((exp["year"] < year_min) | (exp["year"] > year_max)).sum())
    if n_out:
        log(f"贷款: 展开年窗外裁剪 {n_out} 行 (INFO, 通则 ⓑ 第二层)")
    exp = exp[(exp["year"] >= year_min) & (exp["year"] <= year_max)]
    g = exp.groupby(["company", "bank", "year"])
    # w_own 缺失语义 (v33 S1): 组内有 P7514 但其金额贡献全被剔 → NaN; 无 P7514 → 0 真零
    def own_agg(x: pd.DataFrame) -> float:
        if not x["own"].any():
            return 0.0
        s = x.loc[x["own"], "amt"].sum(min_count=1)
        return s if pd.notna(s) else np.nan

    out = pd.DataFrame({
        "w": g["amt"].sum(min_count=1),          # 组级全缺 → NaN (v31 R3 P0); 同组多事件 sum
        "w_cnt": g["cnt_share"].sum(),           # 事件计数臂 (全币种, 银团 1/k 分摊)
        "w_own": g[["own", "amt"]].apply(own_agg),
        "w_dur": g[["dur_obs", "amt"]].apply(
            lambda x: x.loc[x["dur_obs"], "amt"].sum(min_count=1) if x["dur_obs"].any() else np.nan),
    }).reset_index()
    bad_w = out["w"].notna() & (out["w"] <= 0)   # 通则 ⓒ
    assert not bad_w.any(), "贷款 w 非缺失值 ≤0 (数据商改版信号)"
    return out


# ================================================================ DV4b 分支机构权
def build_weight_branch(raw_df: pd.DataFrame, canon: BankCanon, geo: pd.DataFrame,
                        year_min: int, year_max: int) -> pd.DataFrame:
    df = raw_df.copy()
    uniq = {u: canon.canon(u) for u in df["HeadofficeName"].unique()}
    df["bank"] = df["HeadofficeName"].map(uniq)
    df = df.dropna(subset=["bank"])
    # CityName 预清洗三则 (v29): 剥括注 / 'null'+空串按缺失 / 未对齐落审计
    city = df["CityName"].astype(str).str.replace(PAREN_RE, "", regex=True).str.strip()
    city = city.where(~city.isin(["null", "None", "nan", ""]), "")
    df["city_key"] = city.str.replace(r"市$", "", regex=True)  # 正则 市$ 单次, 禁 rstrip
    status = norm(df["Status"])
    ap_y = parse_year(df["ApprovalDate"])
    quit_y = parse_year(df["QuitDate"])
    run_y = parse_year(df["RunawayDate"])
    # 端点失败率闸 (v33 J2): Status=退出/失控 ∧ 配套日期解析失败
    exit_mask = status.isin(["2", "1"])
    fail = (status == "2") & quit_y.isna() | (status == "1") & run_y.isna()
    frac_fail = fail.sum() / max(int(exit_mask.sum()), 1)
    if frac_fail > 0.05:
        raise SystemExit(f"分支端点失败率 {frac_fail:.1%} > 5%")
    if frac_fail > 0.01:
        log(f"分支端点失败率 {frac_fail:.1%} > 1%", warn=True)
    # 公司城市键三层 (v29 D3 P0)
    g = geo.copy()
    placeholder = g["city"].isin(DV2_CONSTANTS["city_placeholder"])
    g["key"] = np.where(placeholder, g["district"], g["city"])
    g["key"] = g["key"].str.replace(r"市$", "", regex=True)
    overseas_or_missing = (g["key"] == "") | g["city"].isin(DV2_CONSTANTS["city_overseas"])
    g_ok = g[~overseas_or_missing]
    n_audit = int(overseas_or_missing.sum())
    if n_audit:
        log(f"分支: 缺 city 审计通道公司 {n_audit} 家 (分支权全缺失)")
    # 逐年存续网点计数: w(c,b,t) = 公司城市内该行存续网点数
    rows = []
    yrs = np.arange(year_min, year_max + 1)
    b = pd.DataFrame({"bank": df["bank"], "city": df["city_key"],
                      "ap": ap_y, "quit": quit_y, "run": run_y, "status": status})
    b = b[b["city"] != ""]
    for t in yrs:
        # 存续 = approval≤t ∧ NOT(退出∧quit≤t) ∧ NOT(失控∧run≤t); 端点解析失败="未发生" (v29)
        alive = (b["ap"].notna() & (b["ap"] <= t)
                 & ~((b["status"] == "2") & b["quit"].notna() & (b["quit"] <= t))
                 & ~((b["status"] == "1") & b["run"].notna() & (b["run"] <= t)))
        cnt = b[alive].groupby(["city", "bank"]).size().rename("w").reset_index()
        cnt["year"] = t
        rows.append(cnt)
    net = pd.concat(rows, ignore_index=True)
    out = g_ok.merge(net, left_on="key", right_on="city")[["company", "bank", "year", "w"]]
    out = out[out["w"] > 0]
    # 覆盖锚 A∧B (v29/v31, SystemExit 级) — 由调用方在 dev 真跑 gate 执行 (需知有键公司全集)
    out.attrs["companies_with_key"] = g_ok["company"].tolist()
    out.attrs["city_hit_rate"] = float(g_ok["key"].isin(set(b["city"])).mean())
    return out


# ================================================================ DV4c–f 董监高四臂
def build_board_family(raw_df: pd.DataFrame, canon: BankCanon, companies: dict[str, str],
                       year_min: int, year_max: int,
                       check_anchors: bool = True) -> dict[str, pd.DataFrame]:
    """调用方读表一次 + 规范化 + 银行类过滤 + 行数锚; 四 builder 接同一份 df 分臂 (v33 S1)。"""
    df = raw_df[raw_df["FinInstitutionTypeCode"].isin(["S8002", "S8003"])].copy()
    if check_anchors:
        assert len(df) == 139753, f"董监高银行类锚 {len(df)} ≠ 139,753"
        n_exec = int((norm(df["IsExsacutive"]) == "1").sum())
        assert n_exec == 64263, f"IsExsacutive 锚 {n_exec} ≠ 64,263"
        n_strict = int((norm(df["ServiceStatus"]) == "1").sum())
        assert n_strict == 27974, f"strict 臂锚 {n_strict} ≠ 27,974 (银行类内口径)"
    uniq = {u: canon.canon(u) for u in df["ServInstitution"].unique()}
    df["bank"] = df["ServInstitution"].map(uniq)  # 源列钉死 ServInstitution (禁 FullName 人名列)
    df = df.dropna(subset=["bank"])
    df["company"] = norm(df["Symbol"]).str.zfill(6).map(companies)
    df = df.dropna(subset=["company"])
    yr = parse_year(df["EndDate"])
    keep = year_two_layer(yr, year_min, year_max, "董监高 EndDate")
    df, yr = df[keep], yr[keep]
    df["year"] = yr.astype(int)
    pos = df["SpecificPosition"].astype(str)  # 分臂源列钉死 SpecificPosition (v27)
    is_sup = pos.str.contains("监事")
    is_dir = pos.str.contains("董事") & ~is_sup  # 双含 → 监事臂
    is_exec = norm(df["IsExsacutive"]) == "1"
    strict = norm(df["ServiceStatus"]) == "1"    # strict 臂 (v29 记号统一)
    arms = {"board": is_dir, "supervisor": is_sup, "exec": is_exec,
            "dsg": pd.Series(True, index=df.index)}
    out: dict[str, pd.DataFrame] = {}
    for name, mask in arms.items():
        sub = df[mask]  # canonical 臂对 ServiceStatus 一律不过滤 (v29 D3 P1)
        g = sub.groupby(["company", "bank", "year"])
        t = pd.DataFrame({"w": g["PersonID"].nunique().astype(float)})
        gs = sub[strict.reindex(sub.index, fill_value=False)].groupby(["company", "bank", "year"])
        t["w_strict"] = gs["PersonID"].nunique().astype(float)
        t["w_strict"] = t["w_strict"].fillna(0.0)  # 该组无现任 → strict=0 (子集语义)
        out[name] = t.reset_index()
    return out


# ================================================================ DV4g 银行股东权
def build_weight_shareholder(raw_df: pd.DataFrame, canon: BankCanon, companies: dict[str, str],
                             year_min: int, year_max: int,
                             check_anchors: bool = True) -> pd.DataFrame:
    df = raw_df.copy()
    if check_anchors:
        n_p2202 = int((df["CategoryID"] == "P2202").sum())
        assert n_p2202 == 4822, f"股东通道一锚 {n_p2202} ≠ 4,822"
    df["company"] = norm(df["Stkcd"]).str.zfill(6).map(companies)
    df = df.dropna(subset=["company"])
    rept = pd.to_datetime(df["Reptdt"].astype(str), errors="coerce")
    df["_rept"], df["_year"] = rept, rept.dt.year
    keep = year_two_layer(df["_year"], year_min, year_max, "股东 Reptdt")
    df = df[keep]
    name = df["S0301a"].astype(str)  # 名称源列钉死 S0301a (v31 R3)
    cat = norm(df["CategoryID"])
    # 四闸 (v33 S1 枚举): 托管闸 / 三产闸 / 境外闸 (DV2 内嵌) / 名称映射成功
    c = DV2_CONSTANTS
    # 性能: 仅候选行 (P2202 ∪ 名称含"银行") 走闸与映射, 其余行天然不入两通道
    cand = (cat == "P2202") | name.str.contains("银行", na=False)
    name_c = name[cand]
    custodian = pd.Series(False, index=df.index)
    custodian.loc[cand] = name_c.apply(lambda x: any(w in x for w in c["custodian_words"])
                                       or any(d in x for d in c["custodian_dashes"]))
    sanchan = pd.Series(False, index=df.index)
    sanchan.loc[cand] = name_c.apply(lambda x: any(w in x for w in c["sanchan_words"]))
    uniq = {u: canon.canon(u) for u in name_c.unique()}
    mapped = pd.Series(None, index=df.index, dtype="object")
    mapped.loc[cand] = name_c.map(uniq)
    ch1 = cat == "P2202"
    ch2 = mapped.notna() & (cat.isin(["P2239"]) | cat.isin(list(MISSING_SET)))
    is_bank_row = (ch1 | ch2) & ~custodian & ~sanchan & mapped.notna()
    # (c,t) 年内最晚可观测报告期快照 — 最晚期在全表全量报告期集上取 (不限通道不施闸, v31 两宇宙)
    latest = df.groupby(["company", "_year"])["_rept"].transform("max")
    at_latest = df["_rept"] == latest
    snap = df[at_latest & is_bank_row].copy()
    snap["bank"] = mapped[snap.index]
    share = pd.to_numeric(snap["S0304a"], errors="coerce")
    snap["_share"] = share
    # 同名并列取 max (dev 0 组守备) → 先在 (c,t,原始名) 级 max, 再同 canonical 折叠 sum (v33 J1)
    by_name = (snap.groupby(["company", "_year", "bank", snap["S0301a"].astype(str)])["_share"]
               .max().reset_index())
    g = by_name.groupby(["company", "_year", "bank"])["_share"].sum()
    out = g.rename("w").reset_index().rename(columns={"_year": "year"})
    out = out[out["w"].notna() & (out["w"] > 0)]
    return out[["company", "bank", "year", "w"]]


# ================================================================ provider 注册 (v28 契约)
SCHEMES = ("loan", "branch", "board", "supervisor", "exec", "dsg", "shareholder")

DTA_FILES = {
    "loan": CONFIG / "上市公司向金融机构借款表.dta",
    "branch": CONFIG / "银行业金融机构基本信息表.dta",
    "board": CONFIG / "上市公司董监高金融机构背景表.dta",
    "shareholder": CONFIG / "上市公司十大股东.dta",
}
DTA_USECOLS = {
    "loan": ["Symbol", "EventID", "RelateToLoanCompanyCode", "IsBankGroup", "LoanBank",
             "IsSign", "IsTermination", "SignDate", "CurrencyCode", "MaxLoan", "LoanTerm",
             "LoanStarDate", "LoanEndDate", "DeclareDate", "LoanProcess"],
    "branch": ["HeadofficeName", "CityName", "Status", "ApprovalDate", "QuitDate", "RunawayDate"],
    "board": ["Symbol", "EndDate", "PersonID", "SpecificPosition", "IsExsacutive",
              "ServInstitution", "FinInstitutionTypeCode", "ServiceStatus"],
    "shareholder": ["Stkcd", "Reptdt", "S0301a", "S0304a", "CategoryID"],
}

SCHEME_LABEL_WORD = {"loan": "贷款", "branch": "网点", "board": "董事", "supervisor": "监事",
                     "exec": "高管", "dsg": "董监高", "shareholder": "股东"}
ROBUST_ARM_COLS = {"loan": ["w_cnt", "w_own", "w_dur"], "branch": [],
                   "board": ["w_strict"], "supervisor": ["w_strict"], "exec": ["w_strict"],
                   "dsg": ["w_strict"], "shareholder": []}


# ================================================================ 固定列 (D18 ②) + own-bank 剔除
def drop_own_bank(longtab: pd.DataFrame, registry: dict) -> pd.DataFrame:
    """DV3: own-bank 对在长表构建时剔除、七长表落盘即已剔 (v31 R3 P1)。"""
    own = registry["bank_company_map"]
    mask = longtab.apply(lambda r: r["bank"] in own.get(r["company"], []), axis=1) \
        if len(longtab) else pd.Series(dtype=bool)
    n = int(mask.sum()) if len(longtab) else 0
    if n:
        log(f"own-bank 对剔除 {n} 行 (D4 继承)")
        return longtab[~mask]
    return longtab


def fixed_cols_for(longtab: pd.DataFrame, measures: pd.DataFrame,
                   skeleton: pd.MultiIndex) -> pd.DataFrame:
    """rel_n_banks / rel_hhi / rel_wt_base (D18 ②, 引擎边界外调用方计算)。"""
    lt = longtab.dropna(subset=["w"])
    g = lt.groupby(["company", "year"])
    n_banks = g["bank"].nunique()
    tot = g["w"].sum()
    sh2 = (lt["w"] / lt.set_index(["company", "year"]).index.map(tot).values) ** 2
    hhi = sh2.groupby([lt["company"], lt["year"]]).sum()
    in_panel = pd.MultiIndex.from_frame(lt[["bank", "year"]]).isin(set(measures.index))
    wq = (lt["w"] * in_panel).groupby([lt["company"], lt["year"]]).sum() / tot
    out = pd.DataFrame({"rel_n_banks": n_banks, "rel_hhi": hhi, "rel_wt_base": wq})
    out.index.names = ["company_listed_name", "year"]
    out = out.reindex(skeleton)
    out["rel_n_banks"] = out["rel_n_banks"].fillna(0).astype("int32")
    return out


# ================================================================ 互验 DV5
def _fold_pairs(w: pd.DataFrame) -> set[tuple[str, str]]:
    return set(map(tuple, w.dropna(subset=["w"])[["company", "bank"]].drop_duplicates().values))


def _shares(w: pd.DataFrame) -> pd.Series:
    """份额 s(c,b) = Σ_t w / Σ_{b',t} w (先窗口求和, v33 S1 公式)。"""
    ws = w.dropna(subset=["w"]).groupby(["company", "bank"])["w"].sum()
    tot = ws.groupby(level=0).sum()
    return ws / ws.index.get_level_values(0).map(tot)


def enrichment(pairs_m: set, pairs_alt: set) -> dict:
    """④ 富集度双基准 (均匀 + v33 边际保持解析式, 零随机)。"""
    C = {c for c, _ in pairs_m} & {c for c, _ in pairs_alt}
    pm = {(c, b) for c, b in pairs_m if c in C}
    pa = {(c, b) for c, b in pairs_alt if c in C}
    B_m = {b for _, b in pairs_m}  # 媒体银行宇宙 = 当窗 distinct bank 全集 (DV5 ④ 计划式, 不限 C)
    if not pm or not pa or not C:
        return {"n/a": True}
    hit = len(pm & pa) / len(pm)
    base_uniform = len(pa & {(c, b) for c in C for b in B_m}) / (len(C) * len(B_m))
    # 边际保持: Σ_b m_b·a_b / (|C|·|pairs_m|)
    mb: dict[str, int] = {}
    ab: dict[str, int] = {}
    for c, b in pm:
        mb[b] = mb.get(b, 0) + 1
    for c, b in pa:
        ab[b] = ab.get(b, 0) + 1
    base_marg = sum(mb.get(b, 0) * ab.get(b, 0)
                    for b in sorted(set(mb) | set(ab))) / (len(C) * len(pm))  # sorted: HASHSEED 免疫
    return {"n_common_companies": len(C), "n_pairs_m": len(pm), "n_pairs_alt": len(pa),
            "hit_rate": hit, "base_uniform": base_uniform,
            "enrich_uniform": hit / base_uniform if base_uniform > 0 else float("nan"),
            "base_marginal": base_marg,
            "enrich_marginal": hit / base_marg if base_marg > 0 else float("nan")}


def spearman_common(sa: pd.Series, sb: pd.Series) -> tuple[float | None, int]:
    """③ 份额 Spearman — 仅共同支撑口径, 禁 union 补 0。"""
    common = sa.index.intersection(sb.index)
    if len(common) < 10:
        return None, len(common)
    from scipy.stats import spearmanr
    rho, _ = spearmanr(sa.loc[common], sb.loc[common])
    return float(rho), len(common)


def top1_stats(sa: pd.Series, sb: pd.Series) -> dict:
    """⑤ Top-1 同银行率 + 包含率 (argmax, 并列取字典序首)。"""
    def top1(s: pd.Series) -> dict[str, str]:
        d: dict[str, tuple] = {}
        for (c, b), v in s.items():
            cur = d.get(c)
            if cur is None or v > cur[0] or (v == cur[0] and b < cur[1]):
                d[c] = (v, b)
        return {c: b for c, (v, b) in d.items()}
    ta, tb = top1(sa), top1(sb)
    C = set(ta) & set(tb)
    if not C:
        return {"same": None, "n": 0}
    same = sum(ta[c] == tb[c] for c in C) / len(C)
    supp_b = {}
    for c, b in sb.index:
        supp_b.setdefault(c, set()).add(b)
    incl = sum(ta[c] in supp_b.get(c, set()) for c in C) / len(C)
    return {"same": same, "incl_a_in_b": incl, "n": len(C)}


# ================================================================ codebook 七权章 (幂等 section-replace)
SECTION_BEGIN = "<!-- BEGIN 七替代权面板章 (WP5 生成, 勿手改) -->"
SECTION_END = "<!-- END 七替代权面板章 -->"


def upsert_codebook_section(codebook_path: Path, section_md: str) -> None:
    block = f"{SECTION_BEGIN}\n{section_md}\n{SECTION_END}"
    if codebook_path.exists():
        text = codebook_path.read_text(encoding="utf-8")
        if SECTION_BEGIN in text and SECTION_END in text:
            pre = text.split(SECTION_BEGIN)[0]
            post = text.split(SECTION_END, 1)[1]
            text = pre + block + post
        else:
            text = text.rstrip("\n") + "\n\n" + block + "\n"
    else:
        text = block + "\n"
    codebook_path.write_text(text, encoding="utf-8")


def build_codebook_section(coverage: dict[str, pd.Series], canon: BankCanon) -> str:
    lines = [
        "## 七替代权面板 (D18)",
        "",
        "七替代权面板 `company_bank_{loan,branch,board,supervisor,exec,dsg,shareholder}w_panel.dta`",
        "与媒体主面板同引擎同列名 (`cw_/ce_{基名}_{track}`, 同一 D16 短名表), scheme 身份由文件名承载。",
        "**禁八面板横向 merge 成单文件; 八权各自 just-identified 并排, 禁混同一 over-identified",
        "Hansen J、禁同一回归 RHS 并置多权重版本的同名测度** (horse-race 检验经显式标注豁免)。",
        "",
        "### track 双语义 (D18 ①)",
        "媒体主面板: 权重逐轨三矩阵。七替代面板: 权重 track-less, `cw_X_{track}` 的 track 含义 =",
        "**测度 X 自身的轨**, 权重恒同一; track-agnostic 测度 (Q/QD/MC 等) 在替代面板三轨列逐字节恒等",
        "(结构冗余非 bug, 分析端任取一列)。",
        "",
        "### 四臂不可加 (董监高)",
        "董事/监事/高管/董监高四臂高度重叠 (dev 董事∧高管 39.7%), 各自独立面板并排, 禁求和当总量。",
        "canonical 臂对 ServiceStatus 不过滤; strict 稳健臂 (ServiceStatus=='1' 现任) 在各长表 `w_strict` 列。",
        "",
        "### 贷款权口径与披露 (DV4a/§7)",
        "以披露授信上限 (MaxLoan) 恒额代理存续暴露 (授信恒额 ≠ 余额, 非 KM 信贷存量); 左截断 (2007 前",
        "签约在贷不可观测, 稳健窗建议自 ~2010); 单年回退 ~52% 事件流量口径 (`w_dur` 期限可观测臂承接);",
        "银团 1/k 等分 (成员 canonical 去重; 牵头行 lead 旗标在审计附录); 零映射银团合并缺失口径 ≈40%",
        "(k=0 + 无分隔符 ⓪ 剔, 分解表见互验报告); 提前终止信号 <0.1% 不可校正; 政策性银行不在 canonical",
        "宇宙一致排除。中信银行国际(中国) 分支形态系 DV2 豁免判据已知残留 (四表未见实例, 代价近零)。",
        "",
        "### 董监高左端缺口 (v32)",
        "银行类 EndDate 年域 2008–2026, 面板首年 2007 四臂结构性无观测; 2008–2017 覆盖爬坡",
        "(数据商覆盖扩张非真实关联增长), 稳健窗建议自 2008 (窄窗臂 ~2018)。表更新截止 ~2024 年报。",
        "",
        "### 股东权已知覆盖损失 (R2 实测)",
        "P2202 中名称不含'银行'字样的缩写/外文名行 (合肥工行/Hong Leong Bank Berhad 类, dev 实测",
        "120/4,822 ≈2.5%) canonical 化失败、关系丢失但全部落未映射审计附录 (非静默); 刻意不加缩写",
        "映射词表 (引入新裁量自由度), 生产复测后如占比显著再议。",
        "",
        "### 股东快照口径 (DV4g)",
        "(c,t) 年内最晚可观测报告期快照 (非严格年末态); 最晚期在公司当年全表全量报告期集上取;",
        "同 (c,t) 最晚期内同 canonical 折叠 S0304a 取 sum (分行+总行并存 = 同一银行体系合计持股)。",
        "制度性稀疏 (《商业银行法》43 条) 属预期 — 现存持股经历史遗留/债转股/特批例外通道存在,",
        "条款解释稀疏性而非样本合法性。P2201 QFII 刻意不纳 (境外母行错映射)。",
        "",
        "### 分支权口径",
        "w = 公司注册/办公城市内该行存续网点数 (单城市代理, 多地经营公司失真与规模相关; 城市键 2026",
        "快照, 历史迁址按现址计); rel_hhi≈0.05–0.10 稠密结构下 cw_branch 近似城市层银行构成均值,",
        "公司 FE 后识别变异仅网点进入退出 (与城市/公司 FE 共线性警示)。",
        "",
        "### 权源逐年关系对数覆盖表 (真无关系 vs 权源覆盖假零)",
        "| 年 | " + " | ".join(SCHEMES) + " |",
        "|---|" + "---|" * len(SCHEMES),
    ]
    years = sorted({y for s in coverage.values() for y in s.index})
    for y in years:
        lines.append(f"| {y} | " + " | ".join(str(int(coverage[s].get(y, 0))) for s in SCHEMES) + " |")
    lines += [
        "",
        "### 数据谱系 (DV5 ⑥(e) 承接; 字段终值 §9.4 回填)",
        "四权源表 = 商业数据库 dta (供应商/库名/表编号/提取日期/过滤条件/许可/第三方获取路径 —",
        "生产机回填); 两份随复现包分发的商业派生名单 SSOT = company_listed_names.yaml (iFind 源)",
        "与 bank_names.json, 再分发许可判定 §9.4 回填; 许可不明时降级 = 派生聚合面板可分发、",
        "行级长表按需申请。四权源 dta 恒不入库 (.gitignore config/*.dta)。",
    ]
    return "\n".join(lines)


# ================================================================ 主流程
def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--loan-dta"); ap.add_argument("--branch-dta")
    ap.add_argument("--board-dta"); ap.add_argument("--shareholder-dta")
    ap.add_argument("--pairs", default=str(DATA / "_company_bank_cooc_pairs.parquet"))
    ap.add_argument("--input"); ap.add_argument("--panel"); ap.add_argument("--alignment")
    ap.add_argument("--benefit"); ap.add_argument("--controls")
    ap.add_argument("--registry", default=str(CONFIG / "company_bank_cooc_registry.yaml"))
    ap.add_argument("--output-dir", default=str(DATA))
    ap.add_argument("--year-min", type=int, default=2007)
    ap.add_argument("--year-max", type=int, default=2025)
    args = ap.parse_args(argv)
    if args.year_min > args.year_max:
        raise SystemExit(2)
    y0, y1 = args.year_min, args.year_max
    outdir = Path(args.output_dir)

    import build_company_bank_cooc_panel as wp1  # SSOT 双函数复用 (禁第二份实现)

    registry = yaml.safe_load(Path(args.registry).read_text(encoding="utf-8"))
    # DV2 常量双向锁 (v33 J2): WP5 启动断言自身常量 == registry 区段
    reg_dv2 = registry.get("dv2_constants") or {}
    if reg_dv2 and reg_dv2 != DV2_CONSTANTS:
        raise SystemExit("DV2_CONSTANTS 与 registry dv2_constants 区段不一致 — 重跑 WP0")

    pairs_path = Path(args.pairs)
    if not pairs_path.exists():
        raise SystemExit(f"pair 长表缺失: {pairs_path} (互验以媒体为锚, 无锚即无互验)")
    import pyarrow.parquet as pq
    meta = pq.ParquetFile(pairs_path).schema_arrow.metadata or {}
    reg_sha = (meta.get(b"registry_sha256") or b"").decode()
    if reg_sha and reg_sha != registry["meta"]["registry_sha256"]:
        raise SystemExit("pair 长表 registry 指纹与当前 registry 不一致 (stale, 先重跑 WP1)")
    pair = pd.read_parquet(pairs_path)

    canon = BankCanon()
    code_map, geo = load_companies()
    dp = wp1.default_paths()

    def resolve_dta(scheme: str) -> Path | None:
        given = getattr(args, f"{scheme}_dta".replace("-", "_"), None)
        if given:
            p = Path(given)
            if not p.exists():
                raise SystemExit(f"显式传参 --{scheme}-dta 路径不存在: {p}")
            return p
        p = DTA_FILES[scheme]
        if not p.exists():
            log(f"默认路径缺 {p.name} → 跳过该权 (含其面板)", warn=True)
            return None
        return p

    import pyreadstat

    def read_dta(scheme: str, path: Path) -> pd.DataFrame:
        df, _ = pyreadstat.read_dta(str(path), usecols=DTA_USECOLS[scheme])
        return df

    # ---- 七权长表构建
    longtabs: dict[str, pd.DataFrame] = {}
    p_loan = resolve_dta("loan")
    if p_loan:
        longtabs["loan"] = build_weight_loan(read_dta("loan", p_loan), canon, code_map, y0, y1)
    p_branch = resolve_dta("branch")
    if p_branch:
        longtabs["branch"] = build_weight_branch(read_dta("branch", p_branch), canon, geo, y0, y1)
    p_board = resolve_dta("board")
    if p_board:
        fam = build_board_family(read_dta("board", p_board), canon, code_map, y0, y1)
        longtabs.update(fam)
    p_sh = resolve_dta("shareholder")
    if p_sh:
        longtabs["shareholder"] = build_weight_shareholder(read_dta("shareholder", p_sh),
                                                           canon, code_map, y0, y1)
    # own-bank 长表落盘即已剔 (DV3/v31 R3)
    for k in list(longtabs):
        longtabs[k] = drop_own_bank(longtabs[k], registry)
        assert len(longtabs[k]) > 0, f"{k} 权长表为空 (SystemExit 级锚)"
        longtabs[k].to_parquet(outdir / f"_company_bank_altweights_{k}.parquet")

    # 分支覆盖锚 A∧B (v29/v31, dev 真跑 SystemExit 级)
    if "branch" in longtabs:
        br = longtabs["branch"]
        keyed = set(br.attrs.get("companies_with_key", [])) if br.attrs else None
        if keyed:
            nonzero = br["company"].nunique() / len(keyed)
            hit = br.attrs.get("city_hit_rate", 1.0)
            # 双断言 A∧B (v31 R3 P1, 废"或"字; A 必断 — 拦"存续判定全错→全零"剧本)
            if nonzero < 0.90:
                raise SystemExit(f"分支覆盖锚 A: 非零关系公司占比 {nonzero:.1%} < 90%")
            if hit < 0.95:
                raise SystemExit(f"分支覆盖锚 B: 城市命中率 {hit:.1%} < 95% (双侧去市尾疑失效)")

    # ---- 测度库一次构建八面板复用 (v28)
    p_input = Path(args.input) if args.input else dp["input"]
    p_panel = Path(args.panel) if args.panel else dp["panel"]
    input21 = wp1.load_input21(p_input, canon.canonicals)
    panel40 = pd.read_parquet(p_panel)
    align = pd.read_parquet(Path(args.alignment) if args.alignment else dp["alignment"]) \
        if (args.alignment or dp["alignment"].exists()) else None
    benefit = pd.read_parquet(Path(args.benefit) if args.benefit else dp["benefit"]) \
        if (args.benefit or dp["benefit"].exists()) else None
    controls = pd.read_parquet(Path(args.controls) if args.controls else dp["controls"]) \
        if (args.controls or dp["controls"].exists()) else None
    measures = wp1.build_measure_library(input21, panel40, align, benefit, controls, registry)

    companies_all = sorted({c["company_listed_name"] for c in yaml.safe_load(
        (CONFIG / "company_listed_names.yaml").read_text(encoding="utf-8"))["companies"]})
    skeleton = pd.MultiIndex.from_product([companies_all, range(y0, y1 + 1)],
                                          names=["company_listed_name", "year"])
    bank_company_set = set(registry["bank_company_map"])

    # ---- 七面板批量生产 (D18 单引擎)
    coverage: dict[str, pd.Series] = {}
    for scheme in SCHEMES:
        if scheme not in longtabs:
            coverage[scheme] = pd.Series(dtype=int)
            continue
        lt = longtabs[scheme]
        coverage[scheme] = lt.dropna(subset=["w"]).groupby("year").size()
        weights = lt[["company", "bank", "year", "w"]]  # 引擎入口: 丢稳健臂列 + drop w 缺失 (引擎内)
        weighted = wp1.compute_weighted_panel(weights, measures, registry)
        fixed = fixed_cols_for(lt, measures, skeleton)
        panel = fixed.reset_index()
        panel["is_bank_company"] = panel["company_listed_name"].isin(bank_company_set).astype("int8")
        panel["year"] = panel["year"].astype("int16")
        panel = panel[["company_listed_name", "year", "is_bank_company",
                       "rel_n_banks", "rel_hhi", "rel_wt_base"]]
        panel = panel.merge(weighted, how="left", left_on=["company_listed_name", "year"],
                            right_index=True)
        # 八面板批量 gate (DV6 末段)
        assert len(panel) == len(skeleton), f"{scheme} 面板行数 ≠ 骨架"
        cwce = [c for c in panel.columns if c.startswith(("cw_", "ce_"))]
        zero = panel["rel_n_banks"] == 0
        assert panel.loc[zero, cwce].isna().all().all(), f"{scheme}: rel_n_banks=0 行出现非缺失 cw/ce"
        assert panel[cwce].notna().any().any(), f"{scheme} 面板全缺失 (SystemExit 级锚)"
        hhi = panel["rel_hhi"].dropna()
        assert ((hhi > 0) & (hhi <= 1 + 1e-12)).all(), f"{scheme}: rel_hhi 值域违例"
        single = panel[(panel["rel_n_banks"] == 1) & panel["rel_hhi"].notna()]
        assert np.isclose(single["rel_hhi"], 1.0).all(), f"{scheme}: 单银行 rel_hhi ≠ 1"
        # 值域 gate 按 registry range_gate (同 WP3)
        for e in registry["entries"]:
            if not e["emit_panel"] or e["range_gate"] == "none":
                continue
            lo, hi = (-1.0, 1.0) if e["range_gate"] == "tone" else (0.0, 1.0)
            for t in e["emit_tracks"]:
                col = f"cw_{e['basename']}_{t}"
                if col in panel.columns:
                    v = panel[col].dropna()
                    if len(v):
                        assert (v >= lo - 1e-9).all() and (v <= hi + 1e-9).all(), \
                            f"{scheme}: 值域违例 {col}"
        out_dta = outdir / f"company_bank_{scheme}w_panel.dta"
        wp1.write_outputs(panel, registry, out_dta, scheme_word=SCHEME_LABEL_WORD[scheme],
                          fixed_labels={
                              "company_listed_name": "上市公司中文全称", "year": "年",
                              "is_bank_company": "该公司自身是否为银行",
                              "rel_n_banks": f"{SCHEME_LABEL_WORD[scheme]}权当年支撑银行数",
                              "rel_hhi": f"{SCHEME_LABEL_WORD[scheme]}权重集中度HHI",
                              "rel_wt_base": f"{SCHEME_LABEL_WORD[scheme]}权重落在银行面板比例"})
        log(f"{scheme} 面板: {len(panel)} 行 × {len(panel.columns)} 列 → {out_dta.name}")

    # ---- 互验报告 (DV5)
    media_pairs = {}
    media_shares = {}
    mp = pair[pair["track"] == "full"].rename(columns={"n_docs": "w"})
    media_pairs["media"] = _fold_pairs(mp)
    media_shares["media"] = _shares(mp)
    alt_pairs = {k: _fold_pairs(v) for k, v in longtabs.items()}
    alt_shares = {k: _shares(v) for k, v in longtabs.items()}

    rl = ["# 八权互验报告 (WP5 / DV5)", "",
          f"窗口 {y0}–{y1}; 媒体锚 = pair 长表 canonical n_docs full 轨。", "",
          "## ① 覆盖概览", "| 权源 | 公司数 | 银行数 | (c,b) 对数 |", "|---|---|---|---|"]
    for k in ["media"] + [s for s in SCHEMES if s in longtabs]:
        ps = media_pairs.get(k) or alt_pairs.get(k)
        rl.append(f"| {k} | {len({c for c, _ in ps})} | {len({b for _, b in ps})} | {len(ps)} |")
    rl += ["", "## ② 支撑集重合 (稀疏权两两; 分支稠密权不进本件)",
           "| A×B | P(∈B|∈A) | Jaccard | 共见公司 |", "|---|---|---|---|"]
    sparse_schemes = [s for s in SCHEMES if s in longtabs and s != "branch"]
    for i, a in enumerate(sparse_schemes):
        for b in sparse_schemes[i + 1:]:
            C = {c for c, _ in alt_pairs[a]} & {c for c, _ in alt_pairs[b]}
            pa_ = {(c, x) for c, x in alt_pairs[a] if c in C}
            pb_ = {(c, x) for c, x in alt_pairs[b] if c in C}
            if pa_ and pb_:
                rl.append(f"| {a}×{b} | {len(pa_ & pb_)/len(pa_):.3f} | "
                          f"{len(pa_ & pb_)/len(pa_ | pb_):.3f} | {len(C)} |")
    rl += ["", "## ③ 份额 Spearman (共同支撑口径, 禁 union 补 0)",
           "| 媒体×权源 | ρ | n 共同对 |", "|---|---|---|"]
    for s in SCHEMES:
        if s not in longtabs:
            continue
        rho, n = spearman_common(media_shares["media"], alt_shares[s])
        rl.append(f"| media×{s} | {'n/a' if rho is None else f'{rho:+.3f}'} | {n} |")
    rl += ["", "## ④ 富集度 (双向双基准; 叙事以边际保持版为准, gate 按均匀基准 1.5×)",
           "(富集倍数按未舍入底数计算, 用表内 4 位小数机械复算存在尾差属预期)",
           "| 方向 | 命中率 | 均匀基准 | 富集(均匀) | 边际保持基准 | 富集(边际保持) |",
           "|---|---|---|---|---|---|"]
    warn_schemes = []
    for s in SCHEMES:
        if s not in longtabs:
            continue
        fwd = enrichment(media_pairs["media"], alt_pairs[s])
        rev = enrichment(alt_pairs[s], media_pairs["media"])
        for tag, e in ((f"media→{s}", fwd), (f"{s}→media", rev)):
            if e.get("n/a"):
                rl.append(f"| {tag} | n/a | | | | |")
                continue
            rl.append(f"| {tag} | {e['hit_rate']:.3f} | {e['base_uniform']:.4f} | "
                      f"{e['enrich_uniform']:.2f}× | {e['base_marginal']:.4f} | "
                      f"{e['enrich_marginal']:.2f}× |")
        if not fwd.get("n/a") and fwd["enrich_uniform"] < 1.5:
            warn_schemes.append(s)
    if warn_schemes:
        rl.append("")
        rl.append(f"⚠ WARNING: {warn_schemes} 均匀基准富集度 <1.5× — 待生产复审 (dev 不判失败)。")
        for s in warn_schemes:
            log(f"富集度方向锚 <1.5× (均匀口径): {s} — 待生产复审", warn=True)
    # ④b (⑥(a)③, v33): 媒体对篇数在有无各权源关系子集的均值差 (within-relationship, pair 表 $0)
    rl += ["", "## ④b 媒体对篇数按有无权源关系分组均值差 (⑥(a)③, 收敛效度第三件)",
           "| 权源 | 有关系媒体对均值 n_docs | 无关系媒体对均值 | 比值 | 有关系对数 |",
           "|---|---|---|---|---|"]
    media_ndocs = mp.groupby(["company", "bank"])["w"].sum()  # 媒体对窗口总篇数
    for s in SCHEMES:
        if s not in longtabs:
            continue
        in_rel = media_ndocs.index.isin(alt_pairs[s])
        if in_rel.any() and (~in_rel).any():
            a_mean, b_mean = media_ndocs[in_rel].mean(), media_ndocs[~in_rel].mean()
            rl.append(f"| {s} | {a_mean:.2f} | {b_mean:.2f} | "
                      f"{a_mean / b_mean:.2f}× | {int(in_rel.sum())} |")
    rl += ["", "## ⑤ Top-1 同银行率 / 包含率",
           "| media×权源 | 同银行率 | media Top1 ∈ 权源支撑 | n |", "|---|---|---|---|"]
    for s in SCHEMES:
        if s not in longtabs:
            continue
        st = top1_stats(media_shares["media"], alt_shares[s])
        if st["n"]:
            rl.append(f"| media×{s} | {st['same']:.3f} | {st['incl_a_in_b']:.3f} | {st['n']} |")
    rl += [
        "", "## ⑥ 顶刊效度证据与披露包",
        "(a) 富集度 = 收敛效度证据 (信号存在性), 非'媒体权是信贷关系的有效代理'; 措辞钉死 =",
        "\"captures real relationships at N× random baseline while measuring a distinct construct\";",
        "~90% 媒体对无对应披露贷款系构念区分的 feature。叙事以边际保持基准为准 (机械边际集中已扣除)。",
        "(b) 八权 specification-curve: 同一 (测度,DV) 报八权系数森林图, 禁挑臂单报; 免 FWER 依据 =",
        "八权测量不同关系构念上的暴露 (Top-1 同银行率 <0.1 实证), 非同一假设替代检验;",
        "primary 权源由研究问题构念决定并预先声明; 森林图系描述性证据, 假设检验以 primary 单臂,",
        "正文禁将其余七权系数引作同一假设支持 (v33 J1 推断地位)。",
        "(c) 逐权内生性处方: 全部内生 — frozen-share 基期份额 (贷款权基期 ≥2010)/等权 ce 臂",
        "(仅对冲规模假设)/公司与年 FE/exposure-robust SE (AKM 2019); 媒体权共源反射通道",
        "(权重与被加权测度同语料) 处方 = 重叠占比 n_cooc/n_articles 分位披露 + leave-company-out 扩展臂;",
        "分支稠密权变异来源与城市/公司 FE 共线; 董监高爬坡期警示 (~2018 窄窗稳健臂)。",
        "(d) 存量-流量与截断: 贷款授信恒额代理+左截断+无提前终止+短贷 ceil+银团合并缺失 ≈40%",
        "(禁只报 19.7%)+单年回退 ~52%; 董监高 2025+ 悬崖与 2007 左端缺口; 股东制度性稀疏+最晚快照;",
        "分支 2026 城市键快照。政策性银行截除份额/八权共同稳健窗 §9.4 生产回填。",
        "(e) 数据谱系: 四权源表 + 两名单 SSOT + 源 xlsx, 七字段逐表 §9.4 回填。",
        "", "## 未映射审计附录 (top-50 频次)",
        "| 名称 | 频次 |", "|---|---|"]
    for name, cnt in sorted(canon.audit.items(), key=lambda kv: -kv[1])[:50]:
        rl.append(f"| {name} | {cnt} |")
    for extra in getattr(canon, "audit_extra", [])[:50]:
        rl.append(f"| {extra} | - |")
    (outdir / "_company_bank_weight_validation.md").write_text("\n".join(rl) + "\n",
                                                               encoding="utf-8")
    # codebook 七权章 (幂等 section-replace)
    upsert_codebook_section(outdir / "company_bank_cooc_panel_codebook.md",
                            build_codebook_section(coverage, canon))
    log(f"完成: 七权长表 {len(longtabs)} 份 + 面板 + 互验报告 → {outdir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
