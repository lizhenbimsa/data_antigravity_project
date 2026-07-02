"""test_embedding_coprimary_parity — Qwen ⟂ large co-primary parity 不变量门 (v3.14.0, D-4a)。

铁律 (执行计划 §11): panel + producer 产物中, **每一个无后缀嵌入派生列 ⟺ 恰存在一个 `_lg`
孪生列, 反之亦然** (schema 层列名双射, 值可 NaN)。carve-out: `surface_staleness`/
`surface_highstale` 是 MinHash (非嵌入) → 禁 `_lg` 孪生; track-agnostic 元数据列 (如
`*_is_fallback`/`headline_frac`) 同。

本测试两层:
  1. 纯函数 `check_coprimary_parity(columns)` 的合成单测 (不需真 panel, 本机即跑): 正常双射通过,
     单边孤儿 (无后缀缺 `_lg` / `_lg` 缺无后缀) 失败, carve-out 误产 `_lg` 失败。
  2. 真 panel 集成断言: 若盘上 panel 含**任何** `_lg` 嵌入列 (= 已重生为 v3.14.0) → 强制全 parity;
     否则 DEFERRED skip (盘上仍为旧 schema, 须生产语料机重生)。

⚠ `_lg` 列命名当前跨 producer 有两种位置 (`policy_cosine_sim_lg_full` = lg 在 track 前 /
`semantic_staleness_full_lg` = lg 在 track 后); 本检查器对两种位置都鲁棒 (按 token 剥离 `_lg`)。
"""
from __future__ import annotations

import re

import pytest

# 嵌入派生列族前缀 (这些列的无后缀本体须有 `_lg` 孪生, 反之亦然)。
# ⚠ 列号约定: 文章级 producer 列与 panel 级聚合列**命名不同** (policy_cosine_sim→article_sim_*,
#   fintech_intensity_score→avg_ft_intensity)。本表同列两套名 (panel + article), 在对应产物上
#   各自匹配, 另一套在该产物缺席即无害。strat_diff 契约别名走 _EMB_EXACT_BASES 精确匹配
#   (防误吞非嵌入 TF-IDF/LDA 列 strat_diff_n3/n4/n5/n5_w/n5_lda/n5_ctx, code-review P1-2)。
# fix(topk-n-expansion, 2026-07-02): strat_diff 的 N-最近邻 embedding 族 (strat_diff_n{N}_emb,
#   全 N∈{5}∪{10,20,30,40,50}) 改由 _is_emb_family 内**正则** `^strat_diff_n\d+_emb` 统一判定,
#   不再靠下方元组前缀 (前缀只认 n5)。TF-IDF/word/LDA 的各 N 列 (strat_diff_n{N} / _w / _lda)
#   一律**非嵌入族、无 _lg 孪生** (正则要求 digits 后紧跟 _emb, 不误吞)。元组内保留的
#   'strat_diff_n5_emb' 条目已被该正则涵盖 (冗余但无害)。
_EMB_FAMILY_PREFIXES = (
    # panel 级 (runner/encode 聚合时重命名)
    "article_sim_mean", "article_sim_std",   # ← policy_cosine_sim (runner rename)
    "avg_ft_intensity",                       # ← fintech_intensity_score (encode rename)
    # article 级原名 (若 parity 跑在文章级产物上; 在 panel 缺席即无害)
    "policy_cosine_sim", "fintech_intensity_score",
    # 保留原名的嵌入族 (panel groupby 后名不变)
    "semantic_staleness",
    "strat_diff_n5_emb", "strat_sim_max_emb", "centroid_diff_emb", "coh_emb",
    "auth_sim_emb",
    "benefit_mean", "benefit_std", "benefit_pos_frac", "benefit_neg_frac",
    "emb_peer_tone_lag1", "bank_emb_sim_mean_lag1",
)
# strat_diff 契约别名 (EXACT 匹配, 非 prefix): 仅 strat_diff_{full,ctx,ss} 是嵌入列
# (= centroid_diff_emb 逐值别名); strat_diff_n5/n3/n5_w/n5_lda 等是 TF-IDF/LDA 非嵌入, 无 _lg。
_EMB_EXACT_BASES = frozenset({"strat_diff_full", "strat_diff_ctx", "strat_diff_ss"})
# carve-out: 非嵌入派生 → 禁 `_lg` 孪生。
_CARVE_OUT_RE = re.compile(
    r"^(surface_staleness|surface_highstale)"
    r"|(_is_fallback)$|^headline_frac"
)


def _strip_lg(col: str) -> str:
    """按 token 剥离 `_lg` (位置无关): policy_cosine_sim_lg_full → policy_cosine_sim_full;
    semantic_staleness_full_lg → semantic_staleness_full。仅剥第一个 `_lg` token。"""
    parts = col.split("_")
    if "lg" in parts:
        parts.remove("lg")
        return "_".join(parts)
    return col


def _is_lg(col: str) -> bool:
    return "lg" in col.split("_")


def _is_emb_family(col: str) -> bool:
    base = _strip_lg(col)  # 位置无关: 对 _lg 与无后缀两形式同判
    if base in _EMB_EXACT_BASES:
        return True
    # fix(topk-n-expansion, 2026-07-02): strat_diff N-最近邻 embedding 族 (strat_diff_n{N}_emb,
    #   全 N∈{5}∪{10,20,30,40,50}, 含 _ctx/_ss 及经 _strip_lg 归一的 _lg 形式) 用**正则**族判。
    #   起因: _EMB_FAMILY_PREFIXES 的前缀 startswith 只认 n5 ('strat_diff_n10_emb'.startswith(
    #   'strat_diff_n5_emb')=False), top-k 扩 N 后新 emb 列会静默逃逸 parity。^ 锚定 + 要求
    #   digits 后紧跟 '_emb', 故绝不误吞 TF-IDF/word/LDA 的 strat_diff_n{N} / _w / _lda (无 _lg 孪生)。
    if re.match(r"^strat_diff_n\d+_emb", base):
        return True
    return any(base.startswith(p) for p in _EMB_FAMILY_PREFIXES)


def _is_carve_out(col: str) -> bool:
    return bool(_CARVE_OUT_RE.search(col))


def check_coprimary_parity(columns) -> list[str]:
    """返回 parity 违例列表 (空 = 通过)。

    (a) 每个 `_lg` 嵌入列, 其剥 lg 后的无后缀本体须在 columns 中 (无孤儿 `_lg`);
    (b) 每个无后缀嵌入派生列, 须存在对应 `_lg` 孪生 (无孤儿无后缀);
    (c) carve-out 列不得出现 `_lg` 变体。
    """
    cols = set(columns)
    violations: list[str] = []
    lg_cols = {c for c in cols if _is_lg(c)}
    lg_bases = {_strip_lg(c) for c in lg_cols}

    # (c) carve-out 误产 _lg
    for c in lg_cols:
        base = _strip_lg(c)
        if _is_carve_out(base):
            violations.append(f"carve-out 列出现 _lg 变体 (禁): {c}")

    # (a) 孤儿 _lg (本体缺失) — 仅对嵌入族判 (跳过 carve-out 已上报; 非嵌入族的偶发 _lg token 不判)
    for c in lg_cols:
        base = _strip_lg(c)
        if _is_carve_out(base) or not _is_emb_family(c):
            continue
        if base not in cols:
            violations.append(f"孤儿 _lg 列 (无对应无后缀本体): {c} (期望 {base})")

    # (b) 孤儿无后缀嵌入列 (缺 _lg 孪生)
    for c in cols:
        if _is_lg(c) or _is_carve_out(c):
            continue
        if not _is_emb_family(c):
            continue
        if c not in lg_bases:
            violations.append(f"孤儿无后缀嵌入列 (无 _lg 孪生): {c}")
    return violations


# ── 合成单测 (本机即跑, 测 parity 检查器逻辑) ──

def test_parity_balanced_passes():
    # panel 级真实命名 (article_sim_mean ← policy / avg_ft_intensity ← fintech) + 契约别名 + carve-out
    cols = [
        "target_bank", "year",
        "article_sim_mean", "article_sim_mean_lg",
        "article_sim_mean_ctx", "article_sim_mean_lg_ctx",
        "article_sim_std", "article_sim_std_lg",
        "avg_ft_intensity_full", "avg_ft_intensity_lg_full",
        "semantic_staleness_full", "semantic_staleness_full_lg",  # lg 在 track 后亦可
        "strat_diff_full", "strat_diff_lg_full",                  # 契约别名 (EXACT 嵌入)
        # 非嵌入 (TF-IDF/LDA) — 不要求 _lg 孪生, 不得被误判
        "strat_diff_n5", "strat_diff_n5_w", "strat_diff_n5_lda", "strat_diff_n3",
        # carve-out (非嵌入, 无 _lg) — 合法
        "surface_staleness_full", "surface_highstale", "ss_is_fallback", "headline_frac",
    ]
    assert check_coprimary_parity(cols) == []


def test_parity_non_embedding_strat_diff_not_required_lg():
    """P1-2 锁: 非嵌入 strat_diff (TF-IDF char/word/LDA) 不得被当作嵌入族要求 _lg 孪生。
    fix(topk-n-expansion): 纳入大 N (n10/n20/n50) 的非嵌入列, 证正则 ^strat_diff_n\\d+_emb 不误吞。
    """
    cols = [
        # 基准 n5 系
        "strat_diff_n5", "strat_diff_n5_w", "strat_diff_n5_lda", "strat_diff_n3",
        # top-k 大 N 的 TF-IDF char/word/LDA (无 _emb → 非嵌入 → 无需 _lg)
        "strat_diff_n10", "strat_diff_n20", "strat_diff_n50",
        "strat_diff_n10_w", "strat_diff_n30_w",
        "strat_diff_n10_lda", "strat_diff_n40_lda",
        # 大 N 的 ctx/ss 非嵌入
        "strat_diff_n10_ctx", "strat_diff_n20_w_ss", "strat_diff_n50_lda_ctx",
    ]
    assert check_coprimary_parity(cols) == []


def test_parity_topk_emb_bijection_full():
    """fix(topk-n-expansion): 大 N 的 emb 列须与 _lg 孪生双射 (full 轨)。"""
    cols = [
        "strat_diff_n10_emb", "strat_diff_n10_emb_lg",
        "strat_diff_n50_emb", "strat_diff_n50_emb_lg",
    ]
    assert check_coprimary_parity(cols) == []


def test_parity_topk_emb_bijection_ctx_ss():
    """fix(topk-n-expansion): ⚠ 最非平凡路径 — ctx/ss 的 _lg 在 track 后缀**之前**
    (strat_diff_n10_emb_lg_ctx), 须靠 _strip_lg 位置无关剥离才与 base strat_diff_n10_emb_ctx 对齐。
    """
    cols = [
        "strat_diff_n10_emb_ctx", "strat_diff_n10_emb_lg_ctx",
        "strat_diff_n10_emb_ss", "strat_diff_n10_emb_lg_ss",
        "strat_diff_n30_emb_ctx", "strat_diff_n30_emb_lg_ctx",
    ]
    assert check_coprimary_parity(cols) == []


def test_parity_topk_emb_orphan_fails():
    """fix(topk-n-expansion): 大 N 的 emb 单边孤儿 (缺 _lg 或缺无后缀本体) 必须被抓。"""
    # 缺 _lg 孪生
    v1 = check_coprimary_parity(["strat_diff_n10_emb"])
    assert any("孤儿无后缀" in x for x in v1), v1
    # 缺无后缀本体 (孤儿 _lg)
    v2 = check_coprimary_parity(["strat_diff_n20_emb_lg"])
    assert any("孤儿 _lg" in x for x in v2), v2
    # ctx 轨大 N 单边缺失
    v3 = check_coprimary_parity(["strat_diff_n50_emb_lg_ctx"])
    assert any("孤儿 _lg" in x for x in v3), v3


def test_parity_regression_n5_emb_still_enforced():
    """回归锁: 既有 strat_diff_n5_emb 的双射强制不得被本次正则改动削弱。
    (n5_emb 由 _EMB_FAMILY_PREFIXES 元组前缀 + 新正则 ^strat_diff_n\\d+_emb 双重覆盖;
    此测试锁定其 "缺 _lg 孪生即违例" 语义, 防未来任一路径回归。)"""
    v = check_coprimary_parity(["strat_diff_n5_emb"])
    assert any("孤儿无后缀" in x for x in v), v
    # 完整双射通过
    assert check_coprimary_parity(
        ["strat_diff_n5_emb", "strat_diff_n5_emb_lg"]) == []


def test_parity_orphan_no_suffix_fails():
    cols = ["article_sim_mean"]  # 缺 _lg 孪生
    v = check_coprimary_parity(cols)
    assert any("孤儿无后缀" in x for x in v), v


def test_parity_orphan_lg_fails():
    cols = ["article_sim_mean_lg"]  # 缺无后缀本体
    v = check_coprimary_parity(cols)
    assert any("孤儿 _lg" in x for x in v), v


def test_parity_carveout_with_lg_fails():
    cols = ["surface_staleness_full", "surface_staleness_lg_full"]  # MinHash 列禁 _lg
    v = check_coprimary_parity(cols)
    assert any("carve-out" in x for x in v), v


# ── 真 panel 集成断言 (重生后强制; 旧 schema → DEFERRED skip) ──

def _load_panel_columns():
    """读盘上最宽 panel 的列名 (40_panel_yearly / 51_panel_with_controls)。缺则 None。"""
    import os

    import pyarrow.parquet as pq  # noqa: PLC0415

    from news_process.core.config import load_config  # noqa: PLC0415
    out_dir = load_config()["paths"]["output_dir"]
    for fn in ("51_panel_with_controls.parquet", "40_panel_yearly.parquet"):
        p = os.path.join(out_dir, fn)
        if os.path.exists(p):
            return list(pq.ParquetFile(p).schema.names)
    return None


def test_real_panel_coprimary_parity():
    cols = _load_panel_columns()
    if cols is None:
        pytest.skip("DEFERRED: 盘上无 panel 产物")
    has_lg_emb = any(_is_lg(c) and _is_emb_family(_strip_lg(c)) for c in cols)
    if not has_lg_emb:
        pytest.skip(
            "DEFERRED: 盘上 panel 仍为 v3.14.0 前 schema (无 _lg 嵌入列); "
            "须在生产语料机重生为 Qwen⟂large co-primary 双轨后此门方生效"
        )
    violations = check_coprimary_parity(cols)
    assert not violations, "co-primary parity 违例:\n" + "\n".join(violations)
