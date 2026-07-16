"""WP-gate registry gate (COMPANY_TAX_BANK_COOC_PANEL_EXECUTION_PLAN_2026-07-08 v4, §3 T-D14).

镜像 listed registry gate (tests/test_company_bank_cooc_registry.py) 的 12 项结构, 税调化:
锚死 registry_sha256 (税调常量名 `EXPECTED_TAX_REGISTRY_SHA256` **刻意与 listed 的
`EXPECTED_REGISTRY_SHA256` 不同名** — run_pipeline._expected_registry_anchor 正则以行首+全名
匹配为前提, 同名会误锚姊妹管线) + 分族小计 + 三输入名单哈希 (税调名单读 company_tax_names.yaml) +
CUT 对账 410 (KEEP 不锚) + 40 面板穷尽划分 + 短名 ≤32 唯一 + schema 字段 + 不规则后缀映射 +
registry_content_sha256 函数级复算。
新增 T-D3 三负例 (支配规则夹具 / 空列表值 no-op / 空值键无子串命中 fail-loud)。

⚠ 穷尽性断言读盘上 40 面板 — 共享树并发重生会转红, 属"盘上数据态红灯" (计划 §5.1 豁免口径)。
⚠ 与 listed registry gate 零交集: 不 import listed 模块、不读 listed registry (T-D18 边界铁律)。
"""
from __future__ import annotations

import hashlib
import importlib
import json
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO / "config" / "company_tax_bank_cooc_registry.yaml"
CUT_LIST_PATH = REPO / "scripts" / "audit" / "COMPANY_BANK_COOC_PANEL_CUT_LIST_v23.txt"
PANEL_40 = REPO / "data" / "processed" / "40_panel_yearly.parquet"

# ---- 哈希锚 (WP-gate 期从 registry meta.registry_sha256 单次写入; 有意识重跑 WP0 后 bump)
#      ⚠ 常量名禁与 listed 的 EXPECTED_REGISTRY_SHA256 同名 (run_pipeline 锚正则行首+全名匹配; T-D8/R3 P1-2)
# 2026-07-16 有意识重跑 WP0: 40 面板并发重生 +9 列 (G9 预登记漂移) → 预注册基名
# cross_media_alpha / cross_outlet_tone_variance / n_events 源列到位自动激活 (+9 emit 列,
# 51 上游同名 9 列落排除域); 基名集与分族小计不变。
EXPECTED_TAX_REGISTRY_SHA256 = "b246471097a600ff5341fc46621c90f1739902338ec5fd9e578469cde9394162"

# ---- 分族小计锚 (与 listed 逐字节同一份 CUT 负清单 + 同一 40 面板 → 域内条目族分布恒等;
#      税调与 listed 的唯一差异 = bank_company_map/两名单哈希/dv2_constants, 不改族小计)
EXPECTED_FAMILY_COUNTS = {
    "AD": 36, "AS": 14, "AT": 14, "B": 6, "BD": 8, "BP": 1, "C1": 6, "C1b": 3, "C2": 9,
    "CL": 18, "CO": 5, "CS": 14, "CT": 20, "CTRL": 6, "CV": 9, "DA": 19, "DP": 12,
    "DS": 76, "F": 2, "F2": 2, "FE": 1, "FOCUS": 2, "GAP_UNPLANNED": 6, "HD": 5, "IN": 1,
    "KW": 5, "MC": 10, "MISC": 5, "NW": 77, "PA": 4, "PC": 6, "PE": 7, "Q": 1, "QD": 6,
    "RW": 3, "S1": 5, "S1b": 5, "S1c": 2, "S2": 56, "S2b": 2, "S3": 9, "S4": 3, "S4b": 23,
    "S5": 67, "S5_GAP": 25, "S6": 5, "S7": 21, "SD": 55, "ST": 6, "TD": 9, "W": 18,
}

# ---- 铁律组全集常量 (D17 点名 6 组 + 嵌入 both-or-neither; listed 同源, CUT 中立性 F8 保恒等)
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

# ---- 保留在位清单 (救回史 + canonical, 全部 emit_panel=true; listed 同源)
KEEP_IN_PLACE = (
    ["strat_diff_n5", "coh_tfidf_c", "avg_pos_ratio", "avg_neg_ratio",
     "fin_sent_zh_xneg_frac_t95", "finbert2_xneg_frac_t80",
     "finbert_cn_xneg_frac_t80", "finbert_cn_xneg_frac_t95",
     "lazy_jaccard", "lazy_overlap", "lazy_minedit", "llm_vote_tone_std"]
    + [f"{k}_adopt_{m}_p{p}" for k in ("token", "hidden", "subst")
       for m in ("kw", "int") for p in (25, 50, 75)]
    + [f"{k}_adopt_{m}_p50_allv" for k in ("token", "hidden", "subst") for m in ("kw", "int")]
)

DCLS_ALIAS = {f"llm_vote_tone_{d}_dcls": f"llm_vote_tone_{d}_dm"
              for d in ("tech", "app", "sub", "symb", "indep", "collab")}

# ---------------------------------------------------------------- T-D8 grep-clean 跨管道 token 白名单
# 税调四脚本 (01/02/03 + run_pipeline) 的**非注释非 docstring 代码行**里, 只允许出现下列跨管道
# listed 引用 (只读复用 listed 02 加权引擎的 importlib 目标串 + logger 名, T-D10/T-D18)。任何新出现
# 的 company_bank / company_listed_name / stock_code 代码行命中 = listed 管线污染信号 → 翻红重审。
# key = (脚本 basename, 剥空白后整行代码); value = 该处合法性说明。实测命中恰 4 处 (2026-07-08)。
# (docstring/注释里的 listed 引用是合法 provenance/说明, tokenize 精确剔除三引号区间后不入命中集。)
# ⚠ 含结构耦合字面量 company_listed_bank (listed 引擎目录锚, R1 P2-6): 既捕获又白名单留痕, 消覆盖不对称。
_XPIPE_TOKENS = ("company_bank", "company_listed_name", "stock_code", "company_listed_bank")
_TAX_SCRIPTS = (
    "01_build_company_tax_bank_cooc_registry.py",
    "02_build_company_tax_bank_cooc_panel.py",
    "03_build_company_tax_bank_weight_validation.py",
    "04_build_company_tax_bank_altagg_panels.py",
    "run_pipeline.py",
)
_XPIPE_TOKEN_WHITELIST = {
    # 跨管道 importlib 目标串: 只读复用 listed 02 加权引擎模块 (T-D18 引擎复用, 禁第二份实现)
    ("02_build_company_tax_bank_cooc_panel.py",
     '_ENGINE = importlib.import_module("02_build_company_bank_cooc_panel")'),
    # listed 02 引擎 logger 名: 跨管道日志接管 attach 目标 (T-D10 redirect, budget/chunk WARNING 落税调日志)
    ("02_build_company_tax_bank_cooc_panel.py",
     'eng_logger = logging.getLogger("02_build_company_bank_cooc_panel")'),
    # listed 02 引擎 logger 名: 03 侧跨管道日志接管 attach 目标 (T-D10 redirect, 与 02 侧对称)
    ("03_build_company_tax_bank_weight_validation.py",
     'eng_logger = logging.getLogger("02_build_company_bank_cooc_panel")'),
    # listed 引擎目录锚: sys.path 注入 company_listed_bank/ 以只读 import listed 02 加权引擎 (T-D10/T-D18)
    ("02_build_company_tax_bank_cooc_panel.py",
     'LISTED_DIR = REPO / "company_listed_bank"  # 跨管道引擎所在 (只读 import, T-D18 零字节改动)'),
}


def _code_line_token_hits() -> set[tuple[str, str]]:
    """扫税调四脚本非注释非 docstring 代码行, 返回 {(basename, 剥空白整行)} 命中集。

    docstring/多行三引号字面量区间用 tokenize 精确剔除 (三引号 STRING token 覆盖行), 纯注释行按
    strip 起首 `#` 剔除; inline 双引号单行字面量 (importlib/logger 目标串) 保留 → 正是白名单点名的
    合法命中。tokenize 失败 (理论上不发生, 脚本均可运行) 则退化为不剔 docstring, 对当前内容仍安全
    (税调脚本 docstring 无 listed 字面量, 只中文表述)。"""
    import io
    import tokenize
    tax_dir = REPO / "company_tax_bank"
    hits: set[tuple[str, str]] = set()
    for name in _TAX_SCRIPTS:
        src = (tax_dir / name).read_text(encoding="utf-8")
        triple_lines: set[int] = set()
        try:
            toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
        except (tokenize.TokenError, IndentationError, SyntaxError):
            toks = []
        for tok in toks:
            if tok.type == tokenize.STRING:
                q = tok.string.lstrip("rRbBuUfF")  # 剥 r/f/b/u 前缀组合后判三引号
                if q[:3] in ('"""', "'''"):
                    for ln in range(tok.start[0], tok.end[0] + 1):
                        triple_lines.add(ln)
        for i, raw in enumerate(src.splitlines(), 1):
            if i in triple_lines or raw.strip().startswith("#"):
                continue
            if any(t in raw for t in _XPIPE_TOKENS):
                hits.add((name, raw.strip()))
    return hits


@pytest.fixture(scope="module")
def registry() -> dict:
    return yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def wp0():
    """importlib 加载税调 01 模块 (模块名唯一, 不与 listed 01 碰撞; sys.path 注入 company_tax_bank/)。"""
    sys.path.insert(0, str(REPO / "company_tax_bank"))
    return importlib.import_module("01_build_company_tax_bank_cooc_registry")


@pytest.mark.fast
def test_registry_hash_anchor(registry):
    anchor_obj = {k: registry[k] for k in ("entries", "bank_company_map", "excluded", "dv2_constants")}
    recalc = hashlib.sha256(
        json.dumps(anchor_obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    assert recalc == registry["meta"]["registry_sha256"], "registry 内容与 meta 哈希不自洽"
    assert recalc == EXPECTED_TAX_REGISTRY_SHA256, "registry 哈希锚翻红 — 有意识重跑 WP0 后更新锚"


@pytest.mark.fast
def test_family_subtotals(registry):
    counts: dict[str, int] = {}
    for e in registry["entries"]:
        counts[e["family"]] = counts.get(e["family"], 0) + 1
    assert counts == EXPECTED_FAMILY_COUNTS


@pytest.mark.fast
def test_name_list_hash_anchor(registry):
    """三输入内容哈希锚 (v20 防呆): 税调名单读 company_tax_names.yaml (非 listed 名单)。"""
    meta = registry["meta"]
    comp = hashlib.sha256((REPO / "config" / "company_tax_names.yaml").read_bytes()).hexdigest()
    bank = hashlib.sha256((REPO / "config" / "bank_names.json").read_bytes()).hexdigest()
    cut = hashlib.sha256(CUT_LIST_PATH.read_bytes()).hexdigest()
    assert comp == meta["company_names_sha256"], "税调公司名单已重生成 — 有意识重跑 WP0"
    assert bank == meta["bank_names_sha256"], "银行名单已重生成 — 有意识重跑 WP0"
    assert cut == meta["cut_list_sha256"], "负清单已变更 — 有意识重跑 WP0"


@pytest.mark.fast
def test_cut_reconciliation(registry):
    """cut_code 非空条目恰 410 且与 CUT_LIST 集合恰等 (对账前施 _dcls→_dm 映射; KEEP 不锚)。"""
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
    """救回与 canonical 全部在位且 emit_panel=true; lazy 恰 3 个标准三轨基名。"""
    by_name = {e["basename"]: e for e in registry["entries"]}
    for base in KEEP_IN_PLACE:
        assert base in by_name, f"保留基名缺席 registry: {base}"
        assert by_name[base]["emit_panel"], f"保留基名被误裁: {base}"
    lazy = [b for b in by_name if b.startswith("lazy_")]
    assert sorted(lazy) == ["lazy_jaccard", "lazy_minedit", "lazy_overlap"]


@pytest.mark.fast
def test_iron_law_groups_whole(registry):
    """铁律组全整组保留 + 嵌入 MAIN/_lg 基名对零孤儿 (both-or-neither)。"""
    by_name = {e["basename"]: e for e in registry["entries"]}
    for group, members in IRON_LAW_GROUPS.items():
        emitted = [m for m in members if m in by_name and by_name[m]["emit_panel"]]
        assert len(emitted) in (0, len(members)), f"铁律组 {group} 被拆组: {emitted}"
        assert emitted, f"铁律组 {group} 整组缺席"
    for e in registry["entries"]:
        b = e["basename"]
        if b.endswith("_lg"):
            main = b[:-3]
            if main in by_name:
                assert by_name[main]["emit_panel"] == e["emit_panel"], f"嵌入孤儿: {main}/{b}"


@pytest.mark.fast
def test_d4_bank_company_map(registry):
    """D4 对照表: 恰 280 家 (名称含 银行/农商 的税调企业全集; 246 非空 + 34 空列表值容忍)。

    键必须是 company_tax_name 全称 (分/支行法人名) — 精确相等对 listed 是查表, 对税调必然子串命中,
    键仍为全称 (R3 P0-1: 证券简称/短名键会让 own-bank 剔除静默 no-op)。"""
    m = registry["bank_company_map"]
    assert len(m) == 280, "D4 对照表应恰 280 家 (名称含 银行/农商 的税调企业全集)"
    empty = [k for k, v in m.items() if not v]
    nonempty = [k for k, v in m.items() if v]
    assert len(empty) == 34, "空列表值 (NOT_IN_CANON, 剔除 no-op) 应恰 34 家"
    assert len(nonempty) == 246
    # 键的 name_flag_set 定义性质: 恒含 银行/农商 token (集合相等已由 01 构建期 SystemExit 强制)
    for k in m:
        assert ("银行" in k) or ("农商" in k), f"D4 键非 name_flag_set 成员 (无 银行/农商): {k}"
    # 人工对照全称键 → canonical 银行名 抽锚 (盘上实测)
    for comp_full, bank in (("上海银行股份有限公司杭州分行", "上海银行"),
                            ("上海浦东发展银行股份有限公司深圳分行", "上海浦东发展银行"),
                            ("东莞银行股份有限公司深圳分行", "东莞银行"),
                            ("中信银行股份有限公司东莞分行", "中信银行")):
        assert comp_full in m and bank in m[comp_full], f"人工对照全称键缺席: {comp_full}"
    # 空列表值容忍抽锚 (MANUAL 空值键在案, own-bank 剔除对空列表天然 no-op)
    for k in ("上海商业银行有限公司深圳分行", "中国农业发展银行安乡县支行"):
        assert k in m and m[k] == [], f"空值键应在案且值为空列表: {k}"


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
    """不规则后缀映射定向锁: C1/QD/DS-dm/washing/staleness-lg/herd-thr 抽 ≥2 对锚死 (listed 同源)。"""
    by_name = {e["basename"]: e for e in registry["entries"]}
    assert by_name["sub_frac"]["col_by_track"] == {"full": "sub_frac", "ctx": "sub_frac_sc", "ss": "sub_frac_ss"}
    assert by_name["collab_frac"]["col_by_track"]["ss"] == "collab_frac_cm_ss"
    assert by_name["n_articles_tech"]["col_by_track"]["ctx"] == "n_articles_tech_lc_ctx"
    assert by_name["llm_vote_tone_collab_dm"]["col_by_track"] == {
        "full": None, "ctx": "llm_vote_tone_collab_cm_ctx", "ss": "llm_vote_tone_collab_cm_ss"}
    assert by_name["washing_ratio"]["col_by_track"]["full"] == "washing_ratio"  # full 裸名
    assert by_name["washing_asymmetry"]["col_by_track"]["full"] == "washing_asymmetry_full"  # 带缀
    assert by_name["semantic_staleness_lg"]["col_by_track"]["ctx"] == "semantic_staleness_ctx_lg"  # lg 后置
    assert by_name["avg_herd_weight_thr25"]["col_by_track"]["full"] == "avg_herd_weight_full_thr25"
    assert by_name["industry_neg_shock"]["col_by_track"]["full"] == "industry_neg_shock"
    assert by_name["bank_cogn_mean"]["col_by_track"]["full"] == "bank_cogn_mean"


@pytest.mark.fast
def test_registry_content_sha256_function(registry, wp0):
    """01 的运行时 canonical 式 (registry_content_sha256, 02/03 启动经 importlib 复用) 与
    本文件独立重算式/盘上 meta/测试锚 三方一致 — 双实现互证, 防运行时侧 canonical 式漂移。"""
    assert wp0.registry_content_sha256(registry) == registry["meta"]["registry_sha256"]
    assert wp0.registry_content_sha256(registry) == EXPECTED_TAX_REGISTRY_SHA256

    # ---- T-D8 grep-clean 边界守卫 (与本文件 T-D18 零交集主题同源, 顺带同断言): 税调脚本代码行
    #      (剔注释/docstring) 里的跨管道 listed token 命中须恰 == 白名单 (集合相等, 双向漂移探测器)。
    hits = _code_line_token_hits()
    unexpected = hits - _XPIPE_TOKEN_WHITELIST  # 命中 ⊆ 白名单 (新命中 = listed 管线污染信号)
    assert not unexpected, f"税调脚本代码行出现非白名单 listed 引用 (listed 污染?): {sorted(unexpected)}"
    stale = _XPIPE_TOKEN_WHITELIST - hits  # 反向: 白名单条目须真实在盘 (防脚本重构后僵尸白名单静默放行)
    assert not stale, f"白名单条目已不在盘 (脚本重构? 须同步白名单): {sorted(stale)}"


# ---------------------------------------------------------------- T-D3 三负例 (计划 T-D14 新增)
@pytest.mark.fast
def test_d4_dominance_rule_fixture(wp0, monkeypatch):
    """T-D3① 最长匹配支配规则夹具 (注入式合成夹具, 不依赖盘上名单): 一企业命中两银行、其一命中
    variant 为另一命中 variant 的真子串 → 支配归一到最长匹配单值; 独立非嵌套 variant 则不误杀
    (杀'长兴农商 ⊃ 农商'型假阳性而不误杀真多关联)。"""
    # 单元级: _dominated_by 真子串判据 (X 被 Y 支配 ⟺ X 全部 variant 均为 Y 某 variant 真子串)
    assert wp0._dominated_by({"农村商业银行"}, {"长兴农村商业银行"}) is True
    assert wp0._dominated_by({"长兴农村商业银行"}, {"农村商业银行"}) is False
    # 独立非嵌套 variant → 不支配 (真多关联不误杀)
    assert wp0._dominated_by({"农村商业银行", "兴县信用社"}, {"长兴农村商业银行"}) is False
    # 集成级: build_bank_company_map 支配归一 (MANUAL 置空以隔离合成夹具)
    monkeypatch.setattr(wp0, "MANUAL_TAX_BANK_COMPANY_MAP", {})
    comps = [{"company_tax_name": "长兴农村商业银行股份有限公司",
              "variants": ["长兴农村商业银行股份有限公司"]}]
    banks = [{"bank_name": "长兴农村商业银行", "variants": ["长兴农村商业银行"]},
             {"bank_name": "农村商业银行本部", "variants": ["农村商业银行"]}]
    res = wp0.build_bank_company_map(comps, banks)
    assert res == {"长兴农村商业银行股份有限公司": ["长兴农村商业银行"]}, \
        "支配规则应保留最长匹配银行、弃嵌套 variant 银行"


@pytest.mark.fast
def test_d4_empty_list_value_noop(wp0, monkeypatch):
    """T-D3② 零命中人工表值=[] 空列表: own-bank 剔除对空列表天然 no-op, 但企业仍作
    is_bank_company (键保留在 bank_company_map — 面板端据此置 is_bank_company=1)。"""
    monkeypatch.setattr(wp0, "MANUAL_TAX_BANK_COMPANY_MAP",
                        {"某零命中银行股份有限公司": []})
    comps = [{"company_tax_name": "某零命中银行股份有限公司",
              "variants": ["某零命中银行股份有限公司"]}]
    banks = [{"bank_name": "完全无关银行", "variants": ["完全无关银行"]}]
    res = wp0.build_bank_company_map(comps, banks)
    assert "某零命中银行股份有限公司" in res, "空值键须保留 (is_bank_company 语义)"
    assert res["某零命中银行股份有限公司"] == [], "空列表值 = own-bank 剔除 no-op"


@pytest.mark.fast
def test_d4_empty_key_bank_substring_hit_fails_loud(wp0, monkeypatch):
    """T-D3③/⑤ 负例 gate: 人工空值键企业名若出现 bank variant 子串命中 (bank_names.json 扩充信号),
    构建须 fail-loud SystemExit 提示重审, 绝不静默改判。盘上 registry 的 34 空值键均无命中
    (由 01 首跑成功隐证), 本负例把该 gate 锁死为翻红提示。"""
    monkeypatch.setattr(wp0, "MANUAL_TAX_BANK_COMPANY_MAP",
                        {"测试村镇银行股份有限公司": []})
    comps = [{"company_tax_name": "测试村镇银行股份有限公司",
              "variants": ["测试村镇银行股份有限公司"]}]
    banks = [{"bank_name": "测试村镇银行", "variants": ["测试村镇银行"]}]
    with pytest.raises(SystemExit, match="出现机器子串命中"):
        wp0.build_bank_company_map(comps, banks)
