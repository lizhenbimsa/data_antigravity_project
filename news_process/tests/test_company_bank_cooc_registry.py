"""WP0 registry gate (COMPANY_BANK_COOC_PANEL_EXECUTION_PLAN v34).

锚死: 清单哈希 + 分族小计 + 穷尽性 (40 面板列集变化 → 本测试红 → 有意识重跑 WP0)。
含 WP2 ⑫b 负清单对账锚 / ⑫c 保留在位断言 / ⑫d 铁律组与必要集常量 (repo 内可复跑)。
⚠ 穷尽性断言读盘上 40 面板 — 共享树并发重生会转红, 属"盘上数据态红灯" (计划 §5.1 豁免口径)。
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO / "config" / "company_bank_cooc_registry.yaml"
CUT_LIST_PATH = REPO / "scripts" / "audit" / "COMPANY_BANK_COOC_PANEL_CUT_LIST_v23.txt"
PANEL_40 = REPO / "data" / "processed" / "40_panel_yearly.parquet"

# ---- 哈希锚 (WP0 落盘值; registry/名单/负清单任何内容变化 → 红 → 有意识重跑 WP0 更新)
# 2026-07-16 有意识重跑 WP0: 40 面板并发重生 +9 列 (G9 预登记漂移) → 预注册基名
# cross_media_alpha / cross_outlet_tone_variance / n_events 三者源列到位自动激活
# (emit_tracks []→[full,ctx,ss]) + 51 上游同名 9 列落排除域; 基名集与分族小计不变。
EXPECTED_REGISTRY_SHA256 = "4a2f79fd932974b090db338a1441ea95934e6ff22a5cb61b0ed8c5f29871d4e1"

# ---- 分族小计锚 (WP0 2026-07-06 落盘实测; v33 划分域 702 + C1b 白名单补注册 3 + 域外 25 = 730)
EXPECTED_FAMILY_COUNTS = {
    "AD": 36, "AS": 14, "AT": 14, "B": 6, "BD": 8, "BP": 1, "C1": 6, "C1b": 3, "C2": 9,
    "CL": 18, "CO": 5, "CS": 14, "CT": 20, "CTRL": 6, "CV": 9, "DA": 19, "DP": 12,
    "DS": 76, "F": 2, "F2": 2, "FE": 1, "FOCUS": 2, "GAP_UNPLANNED": 6, "HD": 5, "IN": 1,
    "KW": 5, "MC": 10, "MISC": 5, "NW": 77, "PA": 4, "PC": 6, "PE": 7, "Q": 1, "QD": 6,
    "RW": 3, "S1": 5, "S1b": 5, "S1c": 2, "S2": 56, "S2b": 2, "S3": 9, "S4": 3, "S4b": 23,
    "S5": 67, "S5_GAP": 25, "S6": 5, "S7": 21, "SD": 55, "ST": 6, "TD": 9, "W": 18,
}

# ---- WP2 ⑫d 铁律组全集常量 (D17 点名 6 组 + 嵌入 both-or-neither; "79 项必要集"原清单系
#      v23 审查 scratchpad 产物未留档, 本两常量为其 repo 内可复跑重构 — 归档 §9.10 义务)
IRON_LAW_GROUPS = {
    "llm_three": ["gpt54nano_tone", "gemini31_tone", "deepseekv4_tone"],
    "bert_three": ["finbert_cn_net_tone", "fin_sent_zh_net_tone", "finbert2_net_tone"],
    "polw_two": ["du_2022_polw00_tone", "du_2022_polw10_tone"],
    "c2_nine": [f"{m}_{d}_frac" for m in ("gpt54nano", "gemini31", "deepseekv4")
                for d in ("sub", "tech", "collab")],
    "s5_twelve": [f"llm_vote_tone_{w}" for w in ("vw", "mw", "hw")]
                 + [f"dict_avg_tone_{w}" for w in ("vw", "mw", "hw")]
                 + [f"bert_avg_{p}_{w}" for p in ("pos", "neg") for w in ("vw", "mw", "hw")],
    "td_six": [f"{b}_nt_{k}" for b in ("finbert_cn", "fin_sent_zh", "finbert2")
               for k in ("iyvol", "iytrend")],
}

# ---- WP2 ⑫c 保留在位清单 (救回史 + canonical, 全部 emit_panel=true)
KEEP_IN_PLACE = (
    ["strat_diff_n5", "coh_tfidf_c", "avg_pos_ratio", "avg_neg_ratio",
     "fin_sent_zh_xneg_frac_t95", "finbert2_xneg_frac_t80",
     "finbert_cn_xneg_frac_t80", "finbert_cn_xneg_frac_t95",
     "lazy_jaccard", "lazy_overlap", "lazy_minedit", "llm_vote_tone_std"]
    + [f"{k}_adopt_{m}_p{p}" for k in ("token", "hidden", "subst")
       for m in ("kw", "int") for p in (25, 50, 75)]  # AD 18 (救回 12 + canonical p50 6)
    + [f"{k}_adopt_{m}_p50_allv" for k in ("token", "hidden", "subst") for m in ("kw", "int")]  # 6
)

DCLS_ALIAS = {f"llm_vote_tone_{d}_dcls": f"llm_vote_tone_{d}_dm"
              for d in ("tech", "app", "sub", "symb", "indep", "collab")}


@pytest.fixture(scope="module")
def registry() -> dict:
    return yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))


@pytest.mark.fast
def test_registry_hash_anchor(registry):
    anchor_obj = {k: registry[k] for k in ("entries", "bank_company_map", "excluded", "dv2_constants")}
    recalc = hashlib.sha256(
        json.dumps(anchor_obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    assert recalc == registry["meta"]["registry_sha256"], "registry 内容与 meta 哈希不自洽"
    assert recalc == EXPECTED_REGISTRY_SHA256, "registry 哈希锚翻红 — 有意识重跑 WP0 后更新锚"


@pytest.mark.fast
def test_family_subtotals(registry):
    counts: dict[str, int] = {}
    for e in registry["entries"]:
        counts[e["family"]] = counts.get(e["family"], 0) + 1
    assert counts == EXPECTED_FAMILY_COUNTS


@pytest.mark.fast
def test_name_list_hash_anchor(registry):
    meta = registry["meta"]
    comp = hashlib.sha256((REPO / "config" / "company_listed_names.yaml").read_bytes()).hexdigest()
    bank = hashlib.sha256((REPO / "config" / "bank_names.json").read_bytes()).hexdigest()
    cut = hashlib.sha256(CUT_LIST_PATH.read_bytes()).hexdigest()
    assert comp == meta["company_names_sha256"], "公司名单已重生成 — 有意识重跑 WP0"
    assert bank == meta["bank_names_sha256"], "银行名单已重生成 — 有意识重跑 WP0"
    assert cut == meta["cut_list_sha256"], "负清单已变更 — 有意识重跑 WP0"


@pytest.mark.fast
def test_cut_reconciliation(registry):
    """WP2 ⑫b: cut_code 非空条目恰 410 且与 CUT_LIST 集合恰等 (对账前施 _dcls→_dm 映射)。"""
    lines = CUT_LIST_PATH.read_text(encoding="utf-8").splitlines()
    i = lines.index("===[CUT 410]===")
    cut_file = set()
    for line in lines[i + 1:]:
        if line.startswith("==="):
            break
        if not line.strip() or line.startswith("#"):
            continue
        base = line.split("\t")[1]
        cut_file.add(DCLS_ALIAS.get(base, base))
    cut_reg = {e["basename"] for e in registry["entries"] if e.get("cut_code") == "CUT_V23"}
    assert len(cut_reg) == 410
    assert cut_reg == cut_file
    assert all(not e["emit_panel"] for e in registry["entries"] if e.get("cut_code"))


@pytest.mark.integration
def test_exhaustive_partition_40_panel(registry):
    """穷尽性: 40 面板实读列集 ⊆ registry 纳入源列 ∪ 排除域 (差集非空 → 有意识重跑 WP0)。"""
    import pyarrow.parquet as pq
    cols = {n for n in pq.ParquetFile(PANEL_40).schema_arrow.names if n != "__index_level_0__"}
    used = {c for e in registry["entries"] if e["source"] == "40"
            for c in e["col_by_track"].values() if c}
    excluded40 = {k for k in registry["excluded"] if ":" not in k}
    residual = cols - used - excluded40
    assert not residual, f"40 面板出现无判定新列 (共享树漂移): {sorted(residual)[:20]}"


@pytest.mark.fast
def test_short_names_within_32_and_unique(registry):
    seen = set()
    for e in registry["entries"]:
        if not e["emit_panel"]:
            continue
        for arm in ("cw", "ce"):
            for t in e["emit_tracks"]:
                name = f"{arm}_{e['short_name']}_{t}"
                assert len(name) <= 32, name
                assert name not in seen, f"短名碰撞 {name}"
                seen.add(name)


@pytest.mark.fast
def test_keep_in_place(registry):
    """WP2 ⑫c: 救回与 canonical 全部在位且 emit_panel=true; lazy 恰 3 个标准三轨基名。"""
    by_name = {e["basename"]: e for e in registry["entries"]}
    for base in KEEP_IN_PLACE:
        assert base in by_name, f"保留基名缺席 registry: {base}"
        assert by_name[base]["emit_panel"], f"保留基名被误裁: {base}"
    lazy = [b for b in by_name if b.startswith("lazy_")]
    assert sorted(lazy) == ["lazy_jaccard", "lazy_minedit", "lazy_overlap"]


@pytest.mark.fast
def test_iron_law_groups_whole(registry):
    """WP2 ⑫d: 铁律组全整组保留 + 嵌入 MAIN/_lg 基名对零孤儿 (both-or-neither)。"""
    by_name = {e["basename"]: e for e in registry["entries"]}
    for group, members in IRON_LAW_GROUPS.items():
        emitted = [m for m in members if m in by_name and by_name[m]["emit_panel"]]
        assert len(emitted) in (0, len(members)), f"铁律组 {group} 被拆组: {emitted}"
        assert emitted, f"铁律组 {group} 整组缺席"
    # 嵌入对: 凡 emit 域内存在 X 与 X_lg (或 lg 中置对), 两者 emit 状态一致
    for e in registry["entries"]:
        b = e["basename"]
        if b.endswith("_lg"):
            main = b[:-3]
            if main in by_name:
                assert by_name[main]["emit_panel"] == e["emit_panel"], f"嵌入孤儿: {main}/{b}"


@pytest.mark.fast
def test_d4_bank_company_map(registry):
    m = registry["bank_company_map"]
    assert len(m) == 42, "D4 对照表应恰 42 家"
    # 键必须是 company_listed_name 全称 (R3 P0-1: 证券简称键会让 own-bank 剔除静默 no-op)
    banks_all = {b for v in m.values() for b in v}
    for comp_full, bank in (("江苏常熟农村商业银行股份有限公司", "江苏常熟农村商业银行"),
                            ("浙江绍兴瑞丰农村商业银行股份有限公司", "浙江绍兴瑞丰农村商业银行"),
                            ("江苏江阴农村商业银行股份有限公司", "江苏江阴农村商业银行"),
                            ("江苏张家港农村商业银行股份有限公司", "江苏张家港农村商业银行"),
                            ("青岛农村商业银行股份有限公司", "青岛农村商业银行")):
        assert comp_full in m and bank in m[comp_full], f"人工对照全称键缺席: {comp_full}"
    assert banks_all  # 非空


@pytest.mark.fast
def test_registry_schema_fields(registry):
    required = {"basename", "family", "source", "col_by_track", "track_agnostic", "agg",
                "emit_tracks", "short_name", "label_elems", "emit_panel", "cut_code", "range_gate"}
    for e in registry["entries"]:
        assert required <= set(e), f"条目字段缺失: {e['basename']} {required - set(e)}"
        assert e["range_gate"] in ("tone", "frac", "none")
        assert set(e["emit_tracks"]) <= {"full", "ctx", "ss"}


@pytest.mark.fast
def test_irregular_suffix_mappings(registry):
    """不规则后缀映射定向锁 (WP2): C1/QD/DS-dm/washing/staleness-lg/herd-thr 抽 ≥2 对锚死。"""
    by_name = {e["basename"]: e for e in registry["entries"]}
    # 特别锁 sub_frac_ss = substance-ss 源列而非"标准 ss 后缀"误读
    assert by_name["sub_frac"]["col_by_track"] == {"full": "sub_frac", "ctx": "sub_frac_sc", "ss": "sub_frac_ss"}
    assert by_name["collab_frac"]["col_by_track"]["ss"] == "collab_frac_cm_ss"
    assert by_name["n_articles_tech"]["col_by_track"]["ctx"] == "n_articles_tech_lc_ctx"
    assert by_name["llm_vote_tone_collab_dm"]["col_by_track"] == {
        "full": None, "ctx": "llm_vote_tone_collab_cm_ctx", "ss": "llm_vote_tone_collab_cm_ss"}
    assert by_name["washing_ratio"]["col_by_track"]["full"] == "washing_ratio"  # full 裸名
    assert by_name["washing_asymmetry"]["col_by_track"]["full"] == "washing_asymmetry_full"  # 带缀
    assert by_name["semantic_staleness_lg"]["col_by_track"]["ctx"] == "semantic_staleness_ctx_lg"  # lg 后置
    assert by_name["avg_herd_weight_thr25"]["col_by_track"]["full"] == "avg_herd_weight_full_thr25"
    assert by_name["industry_neg_shock"]["col_by_track"]["full"] == "industry_neg_shock"  # WP0-6 ④
    assert by_name["bank_cogn_mean"]["col_by_track"]["full"] == "bank_cogn_mean"


# ---------------------------------------------------------------- 哈希锚 canonical 式 SSOT (2026-07-07)
@pytest.mark.fast
def test_registry_content_sha256_function(registry):
    """01 的运行时 canonical 式 (registry_content_sha256, 02 启动复算经 importlib 复用) 与
    本文件独立重算式/盘上 meta/测试锚 三方一致 — 双实现互证, 防运行时侧 canonical 式漂移。"""
    import importlib
    import sys
    sys.path.insert(0, str(REPO / "company_listed_bank"))
    wp0 = importlib.import_module("01_build_company_bank_cooc_registry")
    assert wp0.registry_content_sha256(registry) == registry["meta"]["registry_sha256"]
    assert wp0.registry_content_sha256(registry) == EXPECTED_REGISTRY_SHA256
