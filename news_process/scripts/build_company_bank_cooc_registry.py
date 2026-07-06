"""WP0 — 银企共现面板测度注册表对账脚本 (COMPANY_BANK_COOC_PANEL_EXECUTION_PLAN v33).

职责 (计划 §4 WP0):
  1. 读五上游 (40/51/27/16/21_full) 全列名, 按 D15 排除规则 (正则+白名单) 与
     D11 族规则做**全划分** — 每列判 {纳入某基名的源列 | 排除+理由代码}, 残差非零 → SystemExit(1)。
  2. 产出 config/company_bank_cooc_registry.yaml (加权引擎与 schema gate 的唯一 SSOT):
     条目 schema = {basename, family, source, col_by_track, track_agnostic, agg,
                    emit_tracks, short_name, label_elems, emit_panel, cut_code, range_gate}
     + 顶层 bank_company_map (D4 42 家) + excluded (列名→理由代码) + dv2_constants (v33 J2, WP5 常量区段)。
  3. emit 判定从负清单 COMPANY_BANK_COOC_PANEL_CUT_LIST_v23.txt 机械落值 (D17 ②;
     解析规格见计划 WP0-5: 段头全等匹配 / 数据行 = 族\t基名 / 对账前施 *_dcls→*_dm 别名映射 /
     仅锚 CUT 侧 410, 禁 keep==294/domain==704 断言)。
  4. D16 短名: 基名级判定与施加, 全列 ≤32 且全局唯一断言 fail-loud。
  5. 哈希锚 = sha256(canonical JSON, 键排序、剔除易变字段) + 两份名单文件内容哈希 (v20 防呆)。

用法: python scripts/build_company_bank_cooc_registry.py [--panel PATH] [--out PATH]
独立派生数据脚本, 不注册 DAG (镜像 generate_company_listed_names.py 定位)。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "processed"
CONFIG = REPO / "config"
CUT_LIST_PATH = REPO / "scripts" / "audit" / "COMPANY_BANK_COOC_PANEL_CUT_LIST_v23.txt"

TRACKS = ("full", "ctx", "ss")

# ---------------------------------------------------------------- D16 短名替换表
# 应用序 = 表序、单遍替换 (计划 D16 + v19 xneg 补丁); 基名级判定与施加 (v20 封口)。
SHORT_NAME_REPLACEMENTS = [
    ("policy_cosine_sim", "polsim"),
    ("avg_fintech_distinct_keywords", "avg_ft_dkw"),
    ("avg_within_doc_redund", "avg_wdred"),
    ("avg_redund_han_log_length", "avg_redhan_ll"),
    ("avg_redund_log_length", "avg_red_ll"),
    ("attention_intensity_density", "attn_int_dens"),
    ("attention_intensity_sd", "attn_int_sd"),
    ("attention_attr_share", "attn_attr_shr"),
    ("washing_ratio_", "wash_"),
    ("washing_asymmetry", "wash_asym"),
    ("washing_tone_shift", "wash_tshift"),
    ("hidden_adopt_", "hid_adopt_"),
    ("assortativity", "assort"),
    ("cross_outlet_tone_variance", "xoutlet_tone_var"),
    ("_cont_mean_", "_cont_"),
    ("xneg_frac_t", "xnegf_t"),
    ("semantic_staleness", "sem_stale"),
    ("semantic_highstale", "sem_histale"),
    ("surface_staleness", "surf_stale"),
    ("surface_highstale", "surf_histale"),
    ("nominalization", "nominaliz"),
    ("_effective_size", "_eff_size"),
    ("coverage_continuity", "cov_contin"),
    ("coverage_active_days", "cov_act_days"),
    ("_net_tone_", "_nt_"),
    ("industry_neg_shock", "ind_neg_shock"),
    ("_target_mention_count", "_tgt_mention_cnt"),
    ("mean_num_intensity_word", "mean_numint_w"),
    ("_within_doc_", "_wd_"),
]

# 负清单 _dcls → _dm 固定别名映射 (恰 6 条, 计划 WP0-5)
DCLS_ALIAS = {f"llm_vote_tone_{d}_dcls": f"llm_vote_tone_{d}_dm"
              for d in ("tech", "app", "sub", "symb", "indep", "collab")}

# D4 人工维护对照表 (5 家逃逸, v18/v23 逐家查定; 与机器 variant 交集并成 42 家)。
# ⚠ 键为证券简称 (计划原文形态), 构建时经 variant 表解析归一到 company_listed_name 全称 —
# 直接当键用会对 own-bank 剔除静默 no-op (结果评审 R3 P0-1 实弹)。
MANUAL_BANK_COMPANY_MAP = {
    "常熟银行": ["江苏常熟农村商业银行"],
    "瑞丰银行": ["浙江绍兴瑞丰农村商业银行"],
    "江阴银行": ["江苏江阴农村商业银行"],
    "张家港行": ["江苏张家港农村商业银行"],
    "青农商行": ["青岛农村商业银行"],
}

# ---------------------------------------------------------------- DV2 常量 (v33 J2: WP0 import WP5 模块常量落 registry 区段, 双向锁)
def _load_dv2_constants() -> dict:
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        from build_company_bank_weight_validation import DV2_CONSTANTS  # noqa: PLC0415
        return DV2_CONSTANTS
    except Exception:  # WP5 脚本未就绪时 (WP0 首跑早于 WP5) 用空占位, WP5 落地后重跑 WP0 回填
        return {}


# ---------------------------------------------------------------- 上游列名读取
def read_cols(path: Path) -> list[str]:
    import pyarrow.parquet as pq
    names = pq.ParquetFile(path).schema_arrow.names
    return [n for n in names if n != "__index_level_0__"]


# ---------------------------------------------------------------- 负清单解析 (计划 WP0-5 规格)
def parse_cut_list(path: Path) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    lines = path.read_text(encoding="utf-8").splitlines()

    def segment(header: str) -> list[tuple[str, str]]:
        try:
            i = lines.index(header)  # 全等段头 (禁前缀匹配)
        except ValueError:
            raise SystemExit(f"负清单缺段头 {header!r}")
        rows: list[tuple[str, str]] = []
        for line in lines[i + 1:]:
            if line.startswith("==="):
                break
            if not line.strip() or line.startswith("#"):
                continue
            fam, base = line.split("\t")
            rows.append((fam, base))
        return rows

    return segment("===[CUT 410]==="), segment("===[KEEP 294]===")


# ---------------------------------------------------------------- 源列解析 (不规则后缀显式映射, 引擎零推断)
# C1/QD/DS 不规则轨后缀 (D11 C1/QD 行 + D11c DS 行)
C1_TRACK_SUFFIX = {
    "tech_frac": ("", "_lc", "_ls"), "app_frac": ("", "_lc", "_ls"),
    "sub_frac": ("", "_sc", "_ss"), "symb_frac": ("", "_sc", "_ss"),
    "indep_frac": ("", "_cm", "_cm_ss"), "collab_frac": ("", "_cm", "_cm_ss"),
}
QD_TRACK_SUFFIX = {
    "n_articles_tech": ("", "_lc_ctx", "_ls_ss"), "n_articles_app": ("", "_lc_ctx", "_ls_ss"),
    "n_articles_sub": ("", "_sc_ctx", "_ss_ss"), "n_articles_symb": ("", "_sc_ctx", "_ss_ss"),
    "n_articles_indep": ("", "_cm_ctx", "_cm_ss"), "n_articles_collab": ("", "_cm_ctx", "_cm_ss"),
}
DS_DM_SUFFIX = {  # _dm 孪生: 无 full 轨 (v23 终审: 源列实存 12 列)
    "llm_vote_tone_tech_dm": ("llm_vote_tone_tech_lc_ctx", "llm_vote_tone_tech_ls_ss"),
    "llm_vote_tone_app_dm": ("llm_vote_tone_app_lc_ctx", "llm_vote_tone_app_ls_ss"),
    "llm_vote_tone_sub_dm": ("llm_vote_tone_sub_sc_ctx", "llm_vote_tone_sub_ss_ss"),
    "llm_vote_tone_symb_dm": ("llm_vote_tone_symb_sc_ctx", "llm_vote_tone_symb_ss_ss"),
    "llm_vote_tone_indep_dm": ("llm_vote_tone_indep_cm_ctx", "llm_vote_tone_indep_cm_ss"),
    "llm_vote_tone_collab_dm": ("llm_vote_tone_collab_cm_ctx", "llm_vote_tone_collab_cm_ss"),
}
# DEFERRED 承诺缺轨全集 (计划 D11b AT 行/v23 判定程序; 缺源列仍照出全 NaN 列)
DEFERRED_BASENAMES = {
    "du_2022_polw00_tone", "du_2022_polw10_tone",
    "gpt54nano_sub_frac", "gpt54nano_tech_frac", "gpt54nano_collab_frac",
    "gemini31_sub_frac", "gemini31_tech_frac", "gemini31_collab_frac",
    "deepseekv4_sub_frac", "deepseekv4_tech_frac", "deepseekv4_collab_frac",
    "avg_boilerplate", "avg_rare_word_c2", "avg_rare_word_c5",
}


def resolve_cols(base: str, colset: set[str]) -> tuple[dict, bool]:
    """基名 → {full/ctx/ss: 源列名或 None}, track_agnostic。不规则后缀全部显式。"""
    # C1 / QD / DS-dm 显式映射
    if base in C1_TRACK_SUFFIX or base in QD_TRACK_SUFFIX:
        sfx = (C1_TRACK_SUFFIX | QD_TRACK_SUFFIX)[base]
        cols = {t: (base + s if base + s in colset else None) for t, s in zip(TRACKS, sfx)}
        return cols, False
    if base in DS_DM_SUFFIX:
        c, s = DS_DM_SUFFIX[base]
        return {"full": None, "ctx": c if c in colset else None, "ss": s if s in colset else None}, False
    # track 后置参数后缀族: herd thr / attention j 梯子 (avg_herd_weight_full_thr25 / attention_index_full_j70w5)
    m = re.match(r"^(.*)_((?:thr|j)\d+(?:w\d+)?)$", base)
    if m:
        stem, sfx = m.groups()
        cols = {t: (f"{stem}_{t}_{sfx}" if f"{stem}_{t}_{sfx}" in colset else None) for t in TRACKS}
        if any(cols.values()):
            return cols, False
    # 嵌入 lg 后置族: semantic_staleness_lg → semantic_staleness_{t}_lg (track 中置)
    if base.endswith("_lg"):
        stem = base[:-3]
        cols = {t: (f"{stem}_{t}_lg" if f"{stem}_{t}_lg" in colset else None) for t in TRACKS}
        if any(cols.values()):
            return cols, False
    # 标准 _{track} 后缀
    std = {t: (f"{base}_{t}" if f"{base}_{t}" in colset else None) for t in TRACKS}
    # full 轨裸名族 (washing_ratio 系/strat 带 N/AS 扩/IN/NW-cogn 等): 裸名在列集且 _full 缺席 → full=裸名
    if std["full"] is None and base in colset:
        if std["ctx"] is not None or std["ss"] is not None:
            std["full"] = base
            return std, False
        # 三轨全无 + 裸名在 → track-agnostic 单列
        return {t: base for t in TRACKS}, True
    if any(std.values()):
        return std, False
    return std, False  # 全 None → DEFERRED 或结构缺席, 调用方判


# ---------------------------------------------------------------- D15 排除规则 (正则+白名单, 全列双评)
# 白名单强制纳入 (排除正则命中但属测度, D15 ⑦ 豁免 + ③ 豁免)
INCLUDE_WHITELIST = {
    "avg_subst_prob_score", "avg_locus_prob_score", "avg_collab_prob_score",  # C1b (D11e)
    "mean_frac_definite", "frac_amb_articles",  # CL (D11f)
    "llm_vote_tone_std",  # DA 分歧构念本体 (D15 ③ 唯一豁免; WP0-6 ③ 核查义务)
    "avg_bank_count", "max_bank_count",  # CS 族, 恰以 _count 结尾
}
# ⑪ 银行不变式候选枚举清单 (作用域定死, v21)
INVARIANT_CANDIDATES_PREFIX = ("net_",)
INVARIANT_CANDIDATES_EXACT = {"stress_period"}
POLICY_INVARIANT_RE = re.compile(r"^(dcep|sandbox|depins)_(treated|post)(_|$)")

TRACK_STRIP_RE = re.compile(r"_(full|ctx|ss)(?=(_|$))")

EXCLUDE_RULES: list[tuple[str, re.Pattern]] = [
    # ① 他行/同组测度 (含 _exc 后缀补丁)
    ("D15_1_PEER", re.compile(r"(_leave1out_|^lpeer_|^leave_one_out_|^exc_|^prox_.*km_|^peer_tone|^emb_peer|^llm_peer_|_exc$)")),
    # ② IV 族
    ("D15_2_IV", re.compile(r"(^bartik_|^outlet_.*_iv|_iv$|_iv_)")),
    # ③ _std/_sum/_count/_skew 伴生 (先剥轨后缀, 双向正则)
    ("D15_3_MOMENT", re.compile(r"_(std|sum|count|skew)(_|$)")),
    # ④ z-score 孪生
    ("D15_4_Z", re.compile(r"_z$")),
    # ⑤ gap 差分
    ("D15_5_GAP", re.compile(r"(^tone_gap_|^attention_gap_|_gap_|_gap$)")),
    # ⑥ 立方胞与交互 + per-BERT-model 维度切片 (D15 ⑥ 收窄条款: ensemble 级 bert_avg_*_{dim} 纳入, per-model 仍除外)
    ("D15_6_INTERACT", re.compile(
        r"(^n_articles_cell_(\d|NA)|^tone_x_|_ddd(_|$)|_x_dcep|_x_sandbox|_x_depins"
        r"|^(finbert_cn|fin_sent_zh|finbert2)_(pos|neg|neu)_(tech|app|sub|symb|indep|collab)$)")),
    # ⑦ 质量诊断
    ("D15_7_DIAG", re.compile(
        r"(_confidence|_prob_|_conf$|_conf_|avg_agreement_rate|_disagree_frac|_freerider_frac|_quietworker_frac"
        r"|^frac_(ctx|ss)_fallback|_bothvalid|_independence|prox_geo_imputed_frac"
        r"|_(disagree|freerider|quietworker)(_frac)?$"
        r"|^has_coverage|^high_coverage|^dummy_no_positive_news|^low_conf_flag|^d4_data_quality_flag)")),
    # ⑧ 别名与纯变换
    ("D15_8_ALIAS", re.compile(
        r"(^ln_|_ln_coverage|^zero_coverage|^fintech_intensity_mean|^n_fintech_articles"
        r"|^du_2022_polw05_tone|^avg_ft_intensity(_lg)?$)")),
    # ⑨ 预烘焙滞后与 event-time 簿记
    ("D15_9_LAG_EVENT", re.compile(
        r"(_lag\d|_lead\d|_lead4plus|_lag4plus|_rel_year|_treat_year|_lag0(_|$))")),
    # ⑩ 环境/规制/静态属性/地理聚合层/分母簿记
    ("D15_10_ENV_STATIC", re.compile(
        r"(^ai_reg_|^bank_(type|scale|zone|province|city|scale_ord)$|^ft_(attn|vol)_(yr|prov|city)"
        r"|^n_articles_llm_valid|^n_words_real|^n_han_real)")),
]


def classify_excluded(col: str) -> str | None:
    """对未被任何基名源列引用的列给排除理由码; 无匹配 → None (残差)。"""
    stripped = TRACK_STRIP_RE.sub("", col)
    # 键列
    if col in {"target_bank", "year"}:
        return "KEY"
    # ⑪ 银行不变式候选清单 (族命中优先于 ⑪ — 本函数只对未纳入列调用, 天然满足)
    if col.startswith(INVARIANT_CANDIDATES_PREFIX) or stripped in INVARIANT_CANDIDATES_EXACT \
            or POLICY_INVARIANT_RE.match(stripped):
        return "D15_11_INVARIANT"
    for code, pat in EXCLUDE_RULES:
        if pat.search(stripped) or pat.search(col):
            return code
    # sum_/min_ 前缀簿记族 (D15 漏网修正)
    if re.match(r"^(sum|min)_", col):
        return "D15_3_MOMENT"
    return None


# ---------------------------------------------------------------- range_gate 判定 (v23: WP3 值域断言载体)
TONE_FAMILIES = {"S1", "S2", "S3", "S4", "S1b", "S5", "DS"}
FRAC_FAMILIES = {"C1", "C2", "S1c", "S6"}


def range_gate_for(base: str, family: str) -> str:
    if family in {"DA", "TD", "CS"}:
        return "none"
    if family in FRAC_FAMILIES:
        return "frac"
    if family in TONE_FAMILIES and ("tone" in base or "_cont" in base or base.endswith("_cont")):
        return "tone"
    if family == "S4" or re.search(r"_net_tone$", base):
        return "tone"
    if family == "S4b" and re.search(r"_(pos|neg|neu)$", base):
        return "frac"
    if re.search(r"_frac$|_frac_", base) and family not in {"DA", "TD", "CS", "MC", "CV"}:
        return "frac"
    return "none"


# ---------------------------------------------------------------- 域外条目 (PA/KW/FOCUS/BD/CTRL, ~25 基名)
def build_offpanel_entries(cols16: set[str], cols27: set[str], cols51: set[str]) -> list[dict]:
    entries: list[dict] = []
    # PA 政策对齐 (16 号文章级, 自聚合 mean; 中缀序 lg 先 allv 后)
    for stem in ("policy_cosine_sim", "policy_cosine_sim_allv",
                 "policy_cosine_sim_lg", "policy_cosine_sim_lg_allv"):
        cols = {t: (f"{stem}_{t}" if f"{stem}_{t}" in cols16 else None) for t in TRACKS}
        entries.append(dict(basename=stem, family="PA", source="16", col_by_track=cols,
                            track_agnostic=False, agg="mean"))
    # KW 金科关键词 (21_full 文章级, track-agnostic 自聚合; 输出基名加 avg_ 前缀)
    kw_map = {
        "avg_fintech_total_count": ("fintech_total_count", "mean"),
        "avg_fintech_upper_count": ("fintech_upper_count", "mean"),
        "avg_fintech_lower_count": ("fintech_lower_count", "mean"),
        "avg_fintech_distinct_keywords": ("fintech_distinct_keywords", "mean"),
        "avg_fintech_in_title": ("fintech_in_title", "share"),
    }
    for out, (src, agg) in kw_map.items():
        entries.append(dict(basename=out, family="KW", source="21", track_agnostic=True,
                            col_by_track={t: src for t in TRACKS}, agg=agg))
    # 聚焦度 (21_full 自聚合, D11e CS 扩; 归 FOCUS 族标签便于对账, 语义属 CS 报道形态)
    for out, src in (("avg_mention_density", "mention_density"),
                     ("avg_target_mention_count", "target_bank_mention_count")):
        entries.append(dict(basename=out, family="FOCUS", source="21", track_agnostic=True,
                            col_by_track={t: src for t in TRACKS}, agg="mean"))
    # BD 社会效益 4 维度 (27 号银行×年, 六轨齐 lg 中置)
    for dim in ("core_op", "growth", "resource", "compliance"):
        for lg in ("", "_lg"):
            stem = f"benefit_{dim}{lg}"
            cols = {t: (f"benefit_{dim}{lg}_{t}" if f"benefit_{dim}{lg}_{t}" in cols27 else None)
                    for t in TRACKS}
            entries.append(dict(basename=stem, family="BD", source="27", col_by_track=cols,
                                track_agnostic=False, agg=None))
    # CTRL 覆盖控制增量 (51 号相对 40 新增 level 量, track-agnostic 直读)
    for stem in ("fintech_share", "nf_n_articles", "all_n_articles",
                 "ft_n_articles_dedup", "nf_headline_frac", "nf_media_breadth"):
        if stem in cols51:
            entries.append(dict(basename=stem, family="CTRL", source="51", track_agnostic=True,
                                col_by_track={t: stem for t in TRACKS}, agg=None))
        else:
            cols = {t: (f"{stem}_{t}" if f"{stem}_{t}" in cols51 else None) for t in TRACKS}
            entries.append(dict(basename=stem, family="CTRL", source="51",
                                track_agnostic=False, col_by_track=cols, agg=None))
    for e in entries:
        e.setdefault("emit_panel", True)
        e.setdefault("cut_code", None)
    return entries


# ---------------------------------------------------------------- D4 42 家对照表
def build_bank_company_map(companies: list[dict], banks: list[dict]) -> dict[str, list[str]]:
    bank_variant_owner: dict[str, set[str]] = {}
    for b in banks:
        for v in b["variants"]:
            bank_variant_owner.setdefault(v, set()).add(b["bank_name"])
    company_variant_owner: dict[str, list[str]] = {}
    for c in companies:
        for v in c["variants"]:
            company_variant_owner.setdefault(v, []).append(c["company_listed_name"])
    mapping: dict[str, set[str]] = {}
    name_flag_set: set[str] = set()
    for c in companies:
        name = c["company_listed_name"]
        hit = set()
        for v in c["variants"]:
            hit |= bank_variant_owner.get(v, set())
        if hit:
            mapping[name] = hit
        if ("银行" in name) or ("农商" in name):
            name_flag_set.add(name)
    # 人工 5 家: 证券简称经 variant 表解析归一到 company_listed_name 全称 (R3 P0-1 修复)
    for alias, extra in MANUAL_BANK_COMPANY_MAP.items():
        owners = company_variant_owner.get(alias, [])
        if len(owners) != 1:
            raise SystemExit(f"D4 人工对照键 {alias!r} 解析到 {len(owners)} 家公司 (须唯一) — 人工目检")
        mapping.setdefault(owners[0], set()).update(extra)
    # 覆盖性断言 (D4, R3 P0-1 升级为集合相等 — 计数锚对成员错位盲):
    # 对照表键集合 == 全称含银行/农商的公司集合
    if set(mapping) != name_flag_set:
        diff = set(mapping) ^ name_flag_set
        raise SystemExit(
            f"D4 覆盖性断言失败: 对照表键集合 ≠ 全称含银行/农商公司集合, 对称差 {sorted(diff)} — 逐家人工目检")
    return {k: sorted(v) for k, v in sorted(mapping.items())}


# ---------------------------------------------------------------- 短名
def apply_short_name(base: str) -> str:
    s = base
    for old, new in SHORT_NAME_REPLACEMENTS:
        s = s.replace(old, new)
    return s


def finalize_short_names(entries: list[dict]) -> None:
    for e in entries:
        base = e["basename"]
        longest = max(len(f"{arm}_{base}_{t}") for arm in ("cw", "ce") for t in TRACKS)
        if longest <= 32:
            e["short_name"] = base
        else:
            short = apply_short_name(base)
            if max(len(f"{arm}_{short}_{t}") for arm in ("cw", "ce") for t in TRACKS) > 32:
                raise SystemExit(f"D16 短名替换后仍超 32: {base} -> {short}")
            e["short_name"] = short
    # 全局唯一断言 (投影列级)
    seen: dict[str, str] = {}
    for e in entries:
        if not e["emit_panel"]:
            continue
        for arm in ("cw", "ce"):
            for t in e["emit_tracks"]:
                name = f"{arm}_{e['short_name']}_{t}"
                if len(name) > 32:
                    raise SystemExit(f"D16 断言失败: 投影列 {name} 超 32 字符")
                if name in seen:
                    raise SystemExit(f"D16 断言失败: 短名碰撞 {name} ({seen[name]} vs {e['basename']})")
                seen[name] = e["basename"]


# ---------------------------------------------------------------- 主流程
def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", default=str(DATA / "40_panel_yearly.parquet"))
    ap.add_argument("--out", default=str(CONFIG / "company_bank_cooc_registry.yaml"))
    args = ap.parse_args(argv)

    cols40 = read_cols(Path(args.panel))
    cols51 = read_cols(DATA / "51_panel_with_controls.parquet")
    cols27 = read_cols(DATA / "27_benefit_dimensions_panel.parquet")
    cols16 = read_cols(DATA / "16_article_alignment.parquet")
    cols21 = read_cols(DATA / "21_tone_llms_full.parquet")
    set40, set51, set27, set16, set21 = map(set, (cols40, cols51, cols27, cols16, cols21))

    cut_rows, keep_rows = parse_cut_list(CUT_LIST_PATH)
    # 对账前施 _dcls→_dm 别名映射 (仅按基名集合)
    cut_bases = [(fam, DCLS_ALIAS.get(b, b)) for fam, b in cut_rows]
    if len({b for _, b in cut_bases}) != 410:
        raise SystemExit(f"负清单 CUT 段物化后应恰 410 基名, 实得 {len({b for _, b in cut_bases})}")
    cut_set = {b for _, b in cut_bases}

    # WP0-6 修正: ② lazy 幽灵基名并入标准三轨注册 (KEEP 段 6 条 lazy → 3 真基名)
    keep_bases: list[tuple[str, str]] = []
    seen_keep: set[str] = set()
    for fam, b in keep_rows:
        b2 = re.sub(r"^(lazy_(?:jaccard|overlap|minedit))_full$", r"\1", b)
        if b2 not in seen_keep:
            keep_bases.append((fam, b2))
            seen_keep.add(b2)
    # WP0-6 ③ llm_vote_tone_std 白名单入 DA 族纳入域 (负清单缺席即保留);
    # 同机制 (v21 干跑被 ⑦ 正则吞掉) 的 C1b 三基名一并核查补注册 — 白名单豁免列须证入纳入域
    for fam, wl in (("DA", "llm_vote_tone_std"), ("C1b", "avg_subst_prob_score"),
                    ("C1b", "avg_locus_prob_score"), ("C1b", "avg_collab_prob_score")):
        if wl not in seen_keep and wl not in cut_set:
            keep_bases.append((fam, wl))
            seen_keep.add(wl)
            print(f"[WP0] WARNING: 白名单豁免基名 {wl} 不在负清单域, 按 WP0-6 ③ 先例补注册"
                  f" (族 {fam}, emit_panel=true)", file=sys.stderr)

    # 40 面板域条目构造 (KEEP + CUT 全在划分域; CUT 打 emit_panel=false)
    entries: list[dict] = []
    domain_rows = [(fam, b, True) for fam, b in keep_bases] + [(fam, b, False) for fam, b in cut_bases]
    unresolved: list[str] = []
    for fam, base, emit in domain_rows:
        cols, ta = resolve_cols(base, set40)
        present = [t for t in TRACKS if cols.get(t)]
        if not present:
            # 注册在案基名盘上缺源列 → 缺列容错 (全缺失列 + loud WARNING, schema 恒等 registry
            # 推导值跨环境不变 — 计划 D11 缺列容错条款; DEFERRED 与共享树 40 面板漂移缺席同待遇)
            cols, ta = {t: None for t in TRACKS}, False
            present = list(TRACKS)
            if base not in DEFERRED_BASENAMES:
                unresolved.append(base)
        if ta:
            emit_tracks = list(TRACKS)  # track-agnostic 按权重轨照出三列
        elif base in DEFERRED_BASENAMES:
            emit_tracks = list(TRACKS)  # DEFERRED 承诺缺轨照出全 NaN
        elif base in DS_DM_SUFFIX:
            emit_tracks = [t for t in TRACKS if cols.get(t)]  # _dm 无 full 结构缺席
        elif base == "avg_boilerplate" or base.startswith("avg_rare_word"):
            emit_tracks = list(TRACKS)  # DEFERRED 家族
        else:
            emit_tracks = [t for t in TRACKS if cols.get(t)]  # 结构性缺席不出列 (AT 等)
        entries.append(dict(
            basename=base, family=fam, source="40", col_by_track=cols, track_agnostic=ta,
            agg=None, emit_tracks=emit_tracks, emit_panel=emit,
            cut_code=("CUT_V23" if not emit else None)))
    if unresolved:
        print(f"[WP0] WARNING: {len(unresolved)} 个注册在案基名盘上缺全部源列 (共享树 40 面板漂移/DEFERRED),"
              " 按缺列容错出全 NaN 列:", file=sys.stderr)
        for b in unresolved:
            print("   ", b, file=sys.stderr)

    # 域外条目 (PA/KW/FOCUS/BD/CTRL)
    off = build_offpanel_entries(set16, set27, set51)
    for e in off:
        if e.get("track_agnostic"):
            e["emit_tracks"] = list(TRACKS)
        else:
            e["emit_tracks"] = [t for t in TRACKS if e["col_by_track"].get(t)]
    entries.extend(off)

    # range_gate 落值
    for e in entries:
        e["range_gate"] = range_gate_for(e["basename"], e["family"])
        if e["family"] == "PA":
            e["range_gate"] = "none"
        e["label_elems"] = {"family": e["family"], "base": e["basename"]}

    # 冲突断言: 基名唯一
    all_bases = [e["basename"] for e in entries]
    if len(all_bases) != len(set(all_bases)):
        dup = sorted({b for b in all_bases if all_bases.count(b) > 1})
        raise SystemExit(f"基名冲突 (一列命中多族/重复注册): {dup}")

    # 穷尽性全划分: 40 面板每列 ∈ 纳入源列 ∪ 排除域
    used40: set[str] = set()
    for e in entries:
        if e["source"] == "40":
            used40.update(c for c in e["col_by_track"].values() if c)
    excluded: dict[str, str] = {}
    residual: list[str] = []
    for col in cols40:
        if col in used40:
            continue
        code = classify_excluded(col)
        if code is None:
            residual.append(col)
        else:
            excluded[col] = code
    if residual:
        print(f"[WP0] 40 面板残差 {len(residual)} 列无判定 (穷尽性断言失败):", file=sys.stderr)
        for c in residual:
            print("   ", c, file=sys.stderr)
        raise SystemExit(1)

    # 51 号: CTRL 6 列纳入; 与 40 重复列 DUP_OF_40; 其余走排除
    used51 = {c for e in entries if e["source"] == "51" for c in e["col_by_track"].values() if c}
    residual51 = []
    for col in cols51:
        if col in used51:
            continue
        if col in set40:
            excluded[f"51:{col}"] = "DUP_OF_40"
            continue
        code = classify_excluded(col)
        if code is None:
            residual51.append(col)
        else:
            excluded[f"51:{col}"] = code
    if residual51:
        print(f"[WP0] 51 号残差 {len(residual51)} 列:", file=sys.stderr)
        for c in residual51:
            print("   ", c, file=sys.stderr)
        raise SystemExit(1)

    # 27 号: BD 24 轨列纳入 + 键
    used27 = {c for e in entries if e["source"] == "27" for c in e["col_by_track"].values() if c}
    for col in cols27:
        if col in used27:
            continue
        if col in {"target_bank", "year"}:
            excluded[f"27:{col}"] = "KEY"
        else:
            code = classify_excluded(col) or "DIAG"
            excluded[f"27:{col}"] = code

    # 16 号: PA 12 轨列纳入; 2 裸别名 ALIAS; 键; 其余 TEXT (文章级)
    used16 = {c for e in entries if e["source"] == "16" for c in e["col_by_track"].values() if c}
    for col in cols16:
        if col in used16:
            continue
        if col in {"policy_cosine_sim", "policy_cosine_sim_allv"}:
            excluded[f"16:{col}"] = "D15_8_ALIAS"
        elif col in {"docid", "target_bank"}:
            excluded[f"16:{col}"] = "KEY"
        else:
            excluded[f"16:{col}"] = "TEXT"

    # 21_full: KW 5 + 聚焦度 2 纳入; 其余 TEXT
    used21 = {c for e in entries if e["source"] == "21" for c in e["col_by_track"].values() if c}
    for col in cols21:
        if col in used21:
            continue
        excluded[f"21:{col}"] = "KEY" if col in {"docid", "target_bank", "日期"} else "TEXT"

    # 白名单核查 (WP0-6 ③): 强制纳入清单每项须在纳入域
    for w in INCLUDE_WHITELIST:
        if not any(e["basename"] == w or w in (e["col_by_track"].get(t) or "" for t in TRACKS)
                   for e in entries):
            hit = [e["basename"] for e in entries
                   if any((e["col_by_track"].get(t) or "").startswith(w) for t in TRACKS)]
            if not hit:
                raise SystemExit(f"白名单豁免列 {w} 未入纳入域 (疑被排除正则吞掉)")

    # 短名
    finalize_short_names(entries)

    # 排序: 条目顺序 = 输出列序 SSOT (负清单族/入表序 → 域外族按 PA/KW/FOCUS/BD/CTRL 追加)
    # (domain_rows 构造序 = KEEP→CUT 的负清单原序, off 按构造序 — 已是确定序, 不再重排)

    # 名单内容哈希 (v20 防呆) + registry 哈希
    comp_bytes = (CONFIG / "company_listed_names.yaml").read_bytes()
    bank_bytes = (CONFIG / "bank_names.json").read_bytes()
    cut_bytes = CUT_LIST_PATH.read_bytes()
    companies = yaml.safe_load(comp_bytes.decode("utf-8"))["companies"]
    banks = json.loads(bank_bytes.decode("utf-8"))
    bank_company_map = build_bank_company_map(companies, banks)

    dv2_constants = _load_dv2_constants()

    registry = {
        "meta": {
            "plan": "COMPANY_BANK_COOC_PANEL_EXECUTION_PLAN_2026-07-03 v34",
            "n_entries": len(entries),
            "n_emit": sum(1 for e in entries if e["emit_panel"]),
            "n_cut": sum(1 for e in entries if e["cut_code"] == "CUT_V23"),
            "n_cols_40_panel": len(cols40),
            "company_names_sha256": hashlib.sha256(comp_bytes).hexdigest(),
            "bank_names_sha256": hashlib.sha256(bank_bytes).hexdigest(),
            "cut_list_sha256": hashlib.sha256(cut_bytes).hexdigest(),
        },
        "entries": entries,
        "bank_company_map": bank_company_map,
        "excluded": dict(sorted(excluded.items())),
        "dv2_constants": dv2_constants,
    }
    # 哈希锚 = sha256(canonical JSON, 键排序; 剔除易变字段 — meta 不入锚)
    anchor_obj = {k: registry[k] for k in ("entries", "bank_company_map", "excluded", "dv2_constants")}
    anchor = hashlib.sha256(
        json.dumps(anchor_obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    registry["meta"]["registry_sha256"] = anchor

    out = Path(args.out)
    out.write_text(yaml.safe_dump(registry, allow_unicode=True, sort_keys=False, width=200),
                   encoding="utf-8")

    # 人读审计表
    fam_counts: dict[str, int] = {}
    for e in entries:
        fam_counts[e["family"]] = fam_counts.get(e["family"], 0) + 1
    n_proj = sum(2 * len(e["emit_tracks"]) for e in entries if e["emit_panel"])
    print(f"[WP0] 条目 {len(entries)} (emit {registry['meta']['n_emit']} / cut {registry['meta']['n_cut']})"
          f" | 40 面板 {len(cols40)} 列全划分 (排除 {sum(1 for k in excluded if ':' not in k)})"
          f" | 加权投影列 {n_proj} | registry_sha256 {anchor[:16]}…")
    print("[WP0] 分族小计:", dict(sorted(fam_counts.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
