"""dedup_sensitivity.py — 去重阈值敏感性稳健性检验 (panel 处理变量物化, 步骤 6b-3)
================================================================================

动机 (顶刊依据, 同 attention_media.py::compute_attention_treatments "去重口径披露"):
  预处理去重 (precision dedup + MinHash LSH Jaccard≥0.8 + 5 工作日窗口,
  pipeline/preprocess/dedup.py) 直接决定关注度指标的计数基。水平类计数对
  (Jaccard 阈值 × 时间窗口) 两个调谐参数敏感, 顶刊审稿惯例要求披露去重规则
  并证明主结论对参数扰动稳健:
    - Tetlock (2011 RFS, "All the News That's Fit to Reprint"): 转载非新信息,
      去重不足 → 信息到达构念被系统性高估;
    - Hassan/Hollander/van Lent/Tahoun (2019 QJE, doi:10.1093/qje/qjz021):
      份额归一化测度隐含排斥机械重复计数;
    - Fang & Peress (2009 JF, doi:10.1111/j.1540-6261.2009.01493.x) /
      Bushee, Core, Guay & Hamm (2010 JAR, doi:10.1111/j.1475-679X.2009.00357.x):
      传播广度构念则不去重 (由 falsification/controls.py::nf_media_breadth
      另行实现, 不在本模块)。

设计 — "更严格方向"的两阶段近似扰动 (two-stage stricter re-dedup):
  生产语料已按 (J=0.8, W=5 工作日) 去重落盘 (stage 00), 被剔除的原文不可恢复
  → **宽松方向 (J=0.85/0.9, W=3) 需从 data/raw 重跑 stage 00, 本模块不做**,
  论文中如实披露此限制。本模块在 12_fintech_news_full 的文章全集上, 复用
  ArticleDeduplicator 的 MinHash 签名 (一次计算, 参数无关) 按更严格参数网格
  追加判重, 再按 bank-year 重算关注度指标。

  ⚠ 口径诚实声明 (METHOD-1, 审稿人视角): 本模块在**已去重产物**上叠加更严去重,
    其存活集 **不严格等于** 在 data/raw 上直接按该严参数 dedup 的存活集。机理:
    时间窗口判重是 keep-greedy (簇内按日期升序, 后发文若落在任一**已保留**文的
    窗口内即删), 而低阈值下 LSH 簇是高阈值簇的超集; 某文档可能在生产 (0.8) 小簇
    里被删, 而在 raw-direct (0.7) 大簇里因锚点更早/超窗反而存活 — 两阶段已永久
    丢弃它无法复活。故本结果应表述为 **"在生产去重之上施加更严扰动的保守下界"**,
    而非 "等价于从 raw 重跑"。它仍是合法稳健性探针 (直接回答"去重更激进时结论是否
    稳"), 只是不可解释为 from-scratch 重导。sidecar 落 two_stage_approximation 标记
    供 Stata 表脚注引用。

  ⚠ 跨语料盲区 (METHOD-2): 生产去重在 **全语料** (stage 00, 银行/fintech 分类之前)
    上做; 本模块只在 12_fintech_news_full (银行新闻子集) 上重判重。故"银行新闻 ×
    非银行新闻"的跨子集近似重复 (某银行稿是某非银行稿的 0.7–0.8 近似副本) 在本
    敏感性里**看不到**, 会系统性低估 raw-direct 严格去重本会捕获的剔除量。属本
    模块对 attention (银行新闻覆盖) 构念的有意范围限定, 论文须如实披露。

  变体重算关注度指标:

    变体 (默认, config/panel.yaml::panel_building.dedup_sensitivity.variants 可覆盖):
      j70w5   Jaccard 0.70 × 5 工作日   (更低相似度阈值 → 更激进合并)
      j75w5   Jaccard 0.75 × 5 工作日
      j80w10  Jaccard 0.80 × 10 工作日  (更长转载窗口)
      j70w10  Jaccard 0.70 × 10 工作日  (双向最严格)
    生产锚点 j80w5 = 既有 attention_index_full / attention_pct_full 等列本身。

  ⚠ verified 域门控 (DEDUP-1, panel-universe-consistency-audit 2026-06-13): 自该日起本
    模块的 fintech 分子源 s14 与生产锚点 compute_attention_treatments 一致, 经
    (docid,target_bank) semi-join 收敛到 stage-21 verified 集 → n_ft_articles_<v> =
    (verified ∩ 变体存活)。分母 n_all_articles_<v> 与全集脊柱仍取 12_full 全部银行新闻
    (未门控)。注意 sidecar 的 surviving_articles / retained_share 仍是**全 docid 域**的
    去重存活率诊断 (与 n_ft 的 verified∩survivor 域不同, 勿混读)。生产锚点本身亦已 verified
    门控, 故 corr_index_full_vs_production 两侧同域 (DEDUP-2 同域不变量)。

  每变体产 5 列 (suffix = 变体名):
    attention_index_full_<v> / attention_index_ctx_<v>   ln(1+Σ intensity) (变体存活集)
    attention_pct_full_<v>                               N_ft/N_all (分子分母同基, 同变体)
    n_ft_articles_<v> / n_all_articles_<v>               水平计数 (披露用)

  NaN/零契约 (镜像 compute_attention_treatments): 变体全集内零-fintech bank-year
  → index/pct = 0 (真零曝光); bank-year 在变体下失去全部银行新闻 (或本不在
  12_full 全集) → 全 NaN (不可测)。单调性不变量: 变体存活篇数 ≤ 生产篇数。

Stata 用法 (敏感性检验本体): 主回归逐一以 attention_index_full_<v> 替换
  attention_index_full 复跑, 系数符号/显著性稳定 ⇒ 结论对去重参数稳健;
  配 esttab 并列成 Table A 形式。变量标签未登记 codebook 前回退列名 (集中重生时补)。

白话: 生产线把"5 个工作日内、相似度 80% 以上"的转载当重复删掉了。审稿人会问
  "你这 80% 和 5 天是拍脑袋定的吗?" — 本模块把刀拧得更狠 (70%/75%、10 天) 各算
  一遍关注度, 如果回归结论不变, 就证明结果不是靠这两个参数凑出来的。三个诚实提醒:
  ① 只能往"删得更多"方向拧 — 已经删掉的原文找不回来, 想往松了拧得从原始数据重跑;
  ② 这是"在已删基础上再多删"的近似, 跟"一开始就用 70% 删"不完全是一回事 (个别
     文章的去留可能不同), 是个保守的扰动检验而非精确重来;
  ③ 试跑样本只动了 1–3% 文章, 所以算出来的相关性高到 0.999 是必然的、不算"强稳健
     性证据" — 真正的证据是把每个变体的列丢进主回归, 看系数符号和显著性稳不稳。

⚠ 试跑样本 caveat (METHOD-3): 当前盘上 T=2 / ~176 bank-year, 变体仅追加剔除 1–3%
  文章 → 与生产锚点的 Pearson 相关接近 1.0 是低剔除率下的**预期平凡结果**, 非充分
  稳健性证据。真正的稳健性结论须来自主回归系数在各变体下的稳定性 (Stata Table A),
  而非面板内相关性; 全量 17M/T=18 下剔除率与相关性都可能很不同, 当前数字不可外推。
"""

from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

from news_process.pipeline.panel.encode import (
    CONFIG,
    FILENAMES,
    OUTPUT_DIR,
    logger,
)
from news_process.pipeline.panel.verified_universe import restrict_to_verified
from news_process.pipeline.preprocess.dedup import ArticleDeduplicator

# 默认网格: (jaccard_threshold, window_busdays), 仅严格方向 (见模块 docstring)
DEFAULT_VARIANTS = [(0.70, 5), (0.75, 5), (0.80, 10), (0.70, 10)]

# 生产锚点 (stage 00 实际参数), 仅作单调性校验与披露
PRODUCTION_JACCARD = 0.80
PRODUCTION_WINDOW = 5


def _variant_suffix(threshold: float, window: int) -> str:
    """(0.70, 5) → 'j70w5' (列名后缀, Stata 合法标识符)。"""
    return f"j{int(round(threshold * 100))}w{window}"


def _load_variants() -> list:
    """读 config 变体网格, 缺失回退默认; 越界参数剔除并告警。"""
    cfg = (CONFIG.get('panel_building', {}) or {}).get('dedup_sensitivity', {}) or {}
    raw = cfg.get('variants', DEFAULT_VARIANTS)
    variants = []
    for item in raw:
        try:
            th, w = float(item[0]), int(item[1])
        except (TypeError, ValueError, IndexError):
            logger.warning(f"  dedup_sensitivity: 变体 {item!r} 不可解析, 跳过")
            continue
        if not (0 < th < 1) or w < 0:
            logger.warning(f"  dedup_sensitivity: 变体 {item!r} 越界, 跳过")
            continue
        if th > PRODUCTION_JACCARD or (th == PRODUCTION_JACCARD
                                       and w <= PRODUCTION_WINDOW):
            # 宽松方向在已去重语料上无法识别 (被删原文不可恢复) — 拒绝并披露
            logger.warning(
                f"  dedup_sensitivity: 变体 (J={th}, W={w}) 不严格于生产锚点 "
                f"(J={PRODUCTION_JACCARD}, W={PRODUCTION_WINDOW}), 在已去重语料上"
                f"不可识别, 跳过 (宽松方向需从 data/raw 重跑 stage 00)")
            continue
        variants.append((th, w))
    return variants


def compute_dedup_sensitivity_treatments(panel: pd.DataFrame) -> pd.DataFrame:
    """去重阈值敏感性处理变量物化 (panel in → panel out, 步骤 6b-3)。

    机制: 12_full 文章全集 (docid 去重) → 一次性 MinHash 签名 → 按变体网格
    find_near_duplicate_indices 追加判重 → 变体存活集上按 bank-year 重算
    attention index/pct/计数 → LEFT-join 回 panel。$0, 纯本地计算。
    """
    s14_path = os.path.join(OUTPUT_DIR, FILENAMES.get(
        'output_14_fintech_intensity', '14_fintech_intensity.parquet'))
    f12_path = os.path.join(OUTPUT_DIR, FILENAMES.get(
        'output_12_fintech_full', '12_fintech_news_full.parquet'))
    if not (os.path.exists(s14_path) and os.path.exists(f12_path)):
        logger.warning("  14_fintech_intensity / 12_fintech_news_full 缺失, "
                       "跳过去重敏感性处理变量")
        return panel

    variants = _load_variants()
    if not variants:
        logger.warning("  dedup_sensitivity: 变体网格为空, 跳过")
        return panel

    logger.info("=" * 60)
    logger.info("步骤 6b-3: 去重阈值敏感性 (Tetlock 2011 RFS; Hassan 2019 QJE; "
                f"严格方向网格 {[_variant_suffix(t, w) for t, w in variants]}, "
                f"生产锚点 j{int(PRODUCTION_JACCARD * 100)}w{PRODUCTION_WINDOW})")
    logger.info("=" * 60)

    f12 = pd.read_parquet(f12_path, columns=[
        'docid', 'target_bank', '日期', '媒体(中文)', '标题', '内容',
        'is_fintech_news'])
    s14 = pd.read_parquet(s14_path, columns=[
        'docid', 'target_bank', '日期',
        'fintech_intensity_score_full', 'fintech_intensity_score_ctx'])

    GK = ['target_bank', 'year']
    for df in (s14, f12):  # year 派生 (镜像 attention_media.py compute_attention_treatments)
        df['year'] = pd.to_datetime(df['日期'], errors='coerce').dt.year
        df.dropna(subset=['year'], inplace=True)
        df['year'] = df['year'].astype(int)

    # fix(panel-universe-consistency-audit 2026-06-13, DEDUP-1): 分子源 s14 一次性收敛到
    # stage-21 verified 集 (与生产锚点 compute_attention_treatments 同域, 见 ATT-1)。
    # ⚠ 仅门控 s14(分子); arts/f12 (MinHash 判重语料 + 分母/全集脊柱) 保持 12_full 全集
    # — 去重判定如 IDF 须在全语料上做, 分母为全部银行新闻。下游 n_ft_articles_<v> 因此
    # = (verified ∩ survivor); 而 sidecar 的 surviving_articles / retained_share 仍是全
    # docid 域诊断 (去重存活率, 与 n_ft 的 verified∩survivor 不同域, 勿混读)。
    s14 = restrict_to_verified(s14, OUTPUT_DIR, FILENAMES,
                               logger=logger, label='dedup.s14')

    # ── 文章全集 (docid 粒度; 12_full 是 article×bank, 同 docid 多银行行去重) ──
    arts = f12.drop_duplicates('docid')[
        ['docid', '标题', '内容', '日期', '媒体(中文)']].reset_index(drop=True)
    n_prod_articles = len(arts)
    logger.info(f"  文章全集: {n_prod_articles:,} 篇 (生产去重后存活)")

    # ── MinHash 签名一次计算 (参数无关), 变体间复用 ──
    dedup = ArticleDeduplicator(CONFIG, logger)
    arts_prep = dedup._prepare_dataframe(arts.copy())
    minhashes = dedup.compute_minhashes(arts_prep)

    all_docids = set(arts_prep['docid'])
    new_cols: list = []
    summary: dict = {}
    merged = panel
    for th, w in variants:
        sfx = _variant_suffix(th, w)
        drop_idx = dedup.find_near_duplicate_indices(
            arts_prep, minhashes, threshold=th, window_busdays=w)
        dropped_docids = set(arts_prep.loc[list(drop_idx), 'docid'])
        survivors = all_docids - dropped_docids
        # 单调性不变量: 严格参数只会删更多, 存活 ≤ 生产
        if len(survivors) > n_prod_articles:
            logger.error(f"  ✗ {sfx}: 存活 {len(survivors)} > 生产 "
                         f"{n_prod_articles}, 单调性破坏 (不应发生)")
        retained = len(survivors) / n_prod_articles if n_prod_articles else np.nan
        logger.info(f"  {sfx}: 追加剔除 {len(dropped_docids):,} 篇, "
                    f"存活 {len(survivors):,}/{n_prod_articles:,} "
                    f"({retained:.1%})")

        f12_v = f12[f12['docid'].isin(survivors)]
        s14_v = s14[s14['docid'].isin(survivors)]

        # 变体全集脊柱 + 分母 (镜像 compute_attention_treatments, 防 B1 选择偏差)
        universe_v = f12_v.drop_duplicates(GK)[GK].copy()
        n_all_v = f12_v.groupby(GK).size().rename('_n_all')
        g = s14_v.groupby(GK)
        num_v = pd.DataFrame({
            'sum_full': g['fintech_intensity_score_full'].sum(),
            'sum_ctx': g['fintech_intensity_score_ctx'].sum(),
            'n_ft': g.size(),
        })
        t = universe_v.set_index(GK).join(n_all_v).join(num_v)
        for c in ('sum_full', 'sum_ctx', 'n_ft'):
            t[c] = t[c].fillna(0)  # 在-全集零-fintech → 真零曝光
        # 防御性下界 (镜像 attention_media.py W2 复核: IDF 理论可负 → sum 可负)
        t['sum_full'] = t['sum_full'].clip(lower=0)
        t['sum_ctx'] = t['sum_ctx'].clip(lower=0)

        t[f'attention_index_full_{sfx}'] = np.log1p(t['sum_full'])
        t[f'attention_index_ctx_{sfx}'] = np.log1p(t['sum_ctx'])
        t[f'attention_pct_full_{sfx}'] = t['n_ft'] / t['_n_all']  # _n_all≥1 (脊柱来自 f12_v)
        t[f'n_ft_articles_{sfx}'] = t['n_ft'].astype(int)
        t[f'n_all_articles_{sfx}'] = t['_n_all'].astype(int)

        cols = [f'attention_index_full_{sfx}', f'attention_index_ctx_{sfx}',
                f'attention_pct_full_{sfx}', f'n_ft_articles_{sfx}',
                f'n_all_articles_{sfx}']
        new_cols.extend(cols)
        treat = t.reset_index()[GK + cols]
        merged = merged.drop(
            columns=[c for c in cols if c in merged.columns])
        merged = merged.merge(treat, on=GK, how='left')

        summary[sfx] = {
            'jaccard_threshold': th, 'window_busdays': w,
            'extra_dropped_articles': len(dropped_docids),
            'surviving_articles': len(survivors),
            'retained_share': round(retained, 4),
            # METHOD-1: 本结果是"生产去重之上的更严两阶段近似", 非 raw-direct 等价
            'two_stage_approximation': True,
            'raw_equivalent': False,
        }
        # 与生产锚点指标的相关性 + 逐 bank-year Δ 分布 (METHOD-3/4: 单一相关性在低
        # 剔除率/T=2 下接近平凡, 故并报 Δ 分布"谁受影响多大"; 真稳健性证据须来自
        # 主回归系数稳定性 (Stata Table A), 非面板内相关性)。
        if 'attention_index_full' in merged.columns:
            base = merged['attention_index_full']
            var = merged[f'attention_index_full_{sfx}']
            corr = base.corr(var)
            delta = (var - base).abs()
            _pair = base.notna() & var.notna()
            summary[sfx]['corr_index_full_vs_production'] = (
                round(float(corr), 4) if pd.notna(corr) else None)
            summary[sfx]['delta_index_full'] = {
                'n_pairs': int(_pair.sum()),
                'n_changed': int((delta[_pair] > 1e-9).sum()),
                'mean_abs': round(float(delta[_pair].mean()), 6) if _pair.any() else None,
                'p90_abs': round(float(delta[_pair].quantile(0.90)), 6) if _pair.any() else None,
                'max_abs': round(float(delta[_pair].max()), 6) if _pair.any() else None,
            }
            logger.info(f"    corr(attention_index_full, _{sfx}) = "
                        f"{corr if pd.notna(corr) else float('nan'):.4f} "
                        f"[低剔除率下接近平凡, 非充分稳健性证据 — 见 docstring METHOD-3]; "
                        f"Δ: {int((delta[_pair] > 1e-9).sum())} bank-year 变化, "
                        f"max|Δ|={float(delta[_pair].max()) if _pair.any() else 0:.4f}")

    _validate(merged, new_cols)
    _write_summary_sidecar(summary)
    # METHOD-6: matched 把"真零曝光(index=0)"与"有 fintech(index>0)"同计为匹配,
    # 只排除"无任何银行新闻(NaN)"; 三分报告便于审计 (镜像 attention_treatments 口径)。
    _first = merged[new_cols[0]]
    matched = int(_first.notna().sum())
    _pos = int((_first > 0).sum())
    logger.info(f"  去重敏感性: {len(variants)} 变体 × 5 列 = {len(new_cols)} 列并入 "
                f"panel; 首列匹配 {matched}/{len(merged)} bank-year "
                f"(其中 index>0 有曝光 {_pos}, index=0 真零 {matched - _pos}, "
                f"NaN 全集外 {len(merged) - matched})")
    return merged


def _validate(panel: pd.DataFrame, new_cols: list) -> None:
    """值域校验 (仿 _validate_attention_treatments): pct∈[0,1], index/计数 ≥0。"""
    for c in new_cols:
        if c not in panel.columns:
            logger.error(f"  ✗ {c}: 列缺失")
            continue
        v = panel[c].dropna()
        if v.empty:
            logger.warning(f"  ⚠ {c}: 全 NaN (变体全集与面板无交集?)")
            continue
        if c.startswith('attention_pct_full_'):
            ok = v.between(0, 1).all()
        else:
            ok = (v >= 0).all()
        if ok:
            logger.info(f"  ✓ {c}: [{v.min():.4f}, {v.max():.4f}]")
        else:
            logger.error(f"  ✗ {c}: 越界 [{v.min():.4f}, {v.max():.4f}]")


def _write_summary_sidecar(summary: dict) -> None:
    """语料层诊断 sidecar (fail-soft, 不进 OUTPUT_REGISTRY/golden)。"""
    try:
        path = os.path.join(OUTPUT_DIR, 'dedup_sensitivity_summary.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        logger.info(f"  去重敏感性语料层诊断已落盘: {path}")
    except Exception as e:  # noqa: BLE001 — sidecar 失败不阻断面板主流程
        logger.warning(f"  dedup_sensitivity_summary.json 写入失败: {e}")
