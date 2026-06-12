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
    - Fang & Peress (2009 JF) / Bushee et al. (2010 JAR): 传播广度构念则不去重
      (由 falsification/controls.py::nf_media_breadth 另行实现, 不在本模块)。

设计 — 单调"更严格方向"网格 (monotone re-dedup):
  生产语料已按 (J=0.8, W=5 工作日) 去重落盘 (stage 00), 被剔除的原文不可恢复
  → **宽松方向 (J=0.85/0.9, W=3) 需从 data/raw 重跑 stage 00, 本模块不做**,
  论文中如实披露此限制。本模块在 12_fintech_news_full 的文章全集上, 复用
  ArticleDeduplicator 的 MinHash 签名 (一次计算, 参数无关) 按更严格参数网格
  追加判重, 再按 bank-year 重算关注度指标:

    变体 (默认, config/panel.yaml::panel_building.dedup_sensitivity.variants 可覆盖):
      j70w5   Jaccard 0.70 × 5 工作日   (更低相似度阈值 → 更激进合并)
      j75w5   Jaccard 0.75 × 5 工作日
      j80w10  Jaccard 0.80 × 10 工作日  (更长转载窗口)
      j70w10  Jaccard 0.70 × 10 工作日  (双向最严格)
    生产锚点 j80w5 = 既有 attention_index_full / attention_pct_full 等列本身。

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
  一遍关注度, 如果回归结论不变, 就证明结果不是靠这两个参数凑出来的。注意只能
  往"删得更多"方向拧 — 已经删掉的原文找不回来, 想往松了拧得从原始数据重跑。
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
        }
        # 与生产锚点指标的相关性 (面板内快速诊断; 高相关 = 对参数稳健的初证)
        if 'attention_index_full' in merged.columns:
            corr = merged['attention_index_full'].corr(
                merged[f'attention_index_full_{sfx}'])
            summary[sfx]['corr_index_full_vs_production'] = (
                round(float(corr), 4) if pd.notna(corr) else None)
            logger.info(f"    corr(attention_index_full, _{sfx}) = "
                        f"{corr if pd.notna(corr) else float('nan'):.4f}")

    _validate(merged, new_cols)
    _write_summary_sidecar(summary)
    matched = merged[new_cols[0]].notna().sum()
    logger.info(f"  去重敏感性: {len(variants)} 变体 × 5 列 = {len(new_cols)} 列并入 "
                f"panel; 首列匹配 {matched}/{len(merged)} bank-year")
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
