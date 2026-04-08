"""
42_panel_attention_media.py — 金融科技注意力指数与媒体异质性
==========================================================

功能:
  - 金融科技公众注意力指数 (Da et al. 2011, JF; Fang & Peress 2009, JF)
  - 媒体信息中介异质性 (四维度分析)

拆分自: 40_build_panel.py (L1207-1631)
"""

import os
import json
import importlib.util as _iu

import numpy as np
import pandas as pd

# --- 从 41 导入共享配置 ---
_p41 = os.path.join(os.path.dirname(__file__), '41_panel_encode_aggregate.py')
_s41 = _iu.spec_from_file_location('_41_mod', _p41)
_m41 = _iu.module_from_spec(_s41)
_s41.loader.exec_module(_m41)

CONFIG = _m41.CONFIG
logger = _m41.logger
OUTPUT_DIR = _m41.OUTPUT_DIR
FILENAMES = _m41.FILENAMES
PANEL_CFG = _m41.PANEL_CFG


# ============================================================================
# 6b. 金融科技公众注意力指数 (Da et al. 2011, JF; Fang & Peress 2009, JF)
# ============================================================================

# 小地理单元最低文章数阈值 (低于此值的 geo×year 不参与指数计算)
_ATTN_MIN_ARTICLES = 5


def compute_fintech_attention_index(panel: pd.DataFrame) -> pd.DataFrame:
    """构建金融科技公众注意力指数 — 三级地理维度。

    对标: Da, Z., Engelberg, J. & Gao, P. (2011). In Search of Attention.
          The Journal of Finance, 66(5), 1461-1499.
          https://doi.org/10.1111/j.1540-6261.2011.01679.x
          → 公众注意力代理变量 (attention proxy) 的经典范式

          Fang, L. & Peress, J. (2009). Media Coverage and the Cross-Section
          of Stock Returns. The Journal of Finance, 64(5), 2023-2052.
          https://doi.org/10.1111/j.1540-6261.2009.01493.x
          → 媒体覆盖率 (coverage ratio) 作为信息中介的度量

    数据源:
      12_fintech_news_full.parquet — 全量银行新闻 (含 is_fintech_news 标记)。
      该文件为 article × bank 粒度。统一作为指数和权重的数据源，
      避免 df_exploded (仅含 fintech 文章) 导致的地理曝露偏差。

    去重策略:
      - 计算注意力指数 → 按 docid 去重到唯一文章级
      - 计算银行地理曝露权重 → 不去重 (每个 target_bank 行算一次曝露)

    NaN 语义:
      某 Bank-Year 的全部文章均缺失地理信息时，
      ft_attn_prov / ft_attn_city 为 NaN (不填充)。

    操作序列:
      在 balance_panel() 之后、compute_composite_indicators() 之前调用。

    Returns:
        panel: 附加 ft_attn_yr, ft_attn_prov, ft_attn_city 三列的面板。
    """
    full_path = os.path.join(OUTPUT_DIR, FILENAMES.get(
        'output_12_fintech_full', '12_fintech_news_full.parquet'))
    if not os.path.exists(full_path):
        logger.warning("  12_fintech_news_full.parquet 不存在, 跳过注意力指数")
        return panel

    logger.info("=" * 60)
    logger.info("步骤 6b: 金融科技公众注意力指数 (Da et al. 2011; Fang & Peress 2009)")
    logger.info("=" * 60)

    # ── 加载 ──
    core_cols = ['docid', 'target_bank', '日期', 'is_fintech_news']
    geo_cols = ['国家地区/省份', '城市']
    # 仅加载 parquet 中实际存在的列 (地理列可选)
    import pyarrow.parquet as pq
    available = set(pq.read_schema(full_path).names)
    need_cols = [c for c in core_cols + geo_cols if c in available]
    missing_core = [c for c in core_cols if c not in available]
    if missing_core:
        logger.error(f"  12_fintech_news_full 缺少核心列: {missing_core}, 跳过")
        return panel
    missing_geo = [c for c in geo_cols if c not in available]
    if missing_geo:
        logger.warning(f"  12_fintech_news_full 缺少地理列: {missing_geo}, "
                       f"仅计算 Year-level 指数")
    df_all = pd.read_parquet(full_path, columns=need_cols)
    df_all['year'] = pd.to_datetime(df_all['日期'], errors='coerce').dt.year
    df_all = df_all.dropna(subset=['year'])
    df_all['year'] = df_all['year'].astype(int)
    logger.info(f"  加载: {len(df_all):,} 行 (article × bank)")

    # 标准化地理列
    _GEO_NAN_VALUES = frozenset({'', 'nan', 'None', '未知', 'NaN', '<NA>'})
    for col in ['国家地区/省份', '城市']:
        if col in df_all.columns:
            df_all[col] = (df_all[col].astype(str).str.strip()
                           .str.replace(r'\s+', '', regex=True))
            df_all.loc[df_all[col].isin(_GEO_NAN_VALUES), col] = np.nan

    # ── 按 docid 去重 → 唯一文章 (计算注意力指数) ──
    df_unique = df_all.drop_duplicates(subset=['docid'])
    logger.info(f"  唯一文章: {len(df_unique):,}")

    # ═══════════════════════════════════════════════════════
    # (A) Year-level 指数 (基准 / 稳健性参照)
    # ═══════════════════════════════════════════════════════
    yr_total = df_unique.groupby('year').size().rename('_total')
    yr_ft = (df_unique[df_unique['is_fintech_news'] == True]
             .groupby('year').size().rename('_ft'))
    idx_yr = pd.concat([yr_total, yr_ft], axis=1).fillna(0)
    idx_yr['ft_attn_yr'] = idx_yr['_ft'] / idx_yr['_total']
    idx_yr = idx_yr.reset_index()

    logger.info("  ─── Year-level ───")
    for _, r in idx_yr.iterrows():
        logger.info(f"    {int(r['year'])}: "
                     f"{int(r['_ft']):,}/{int(r['_total']):,} "
                     f"= {r['ft_attn_yr']:.4f}")

    # 保存中间数据
    _save_attn_index(idx_yr.rename(columns={'_total': 'total_articles',
                                             '_ft': 'fintech_articles'}),
                     '40_attn_index_year')

    panel = panel.merge(idx_yr[['year', 'ft_attn_yr']],
                        on='year', how='left')

    # ═══════════════════════════════════════════════════════
    # (B) Province × Year 指数
    # ═══════════════════════════════════════════════════════
    prov_col = '国家地区/省份'
    if prov_col in df_unique.columns:
        idx_prov = _build_geo_index(df_unique, prov_col, 'ft_attn_prov',
                                    min_articles=_ATTN_MIN_ARTICLES)
        # 保存中间数据
        _save_attn_index(idx_prov.rename(columns={
            prov_col: 'province', '_total': 'total_articles',
            '_ft': 'fintech_articles'}), '40_attn_index_province_year')

        panel = _merge_geo_index_to_panel(
            df_all, panel, idx_prov[[prov_col, 'year', 'ft_attn_prov']],
            prov_col, 'ft_attn_prov')
        n_prov = idx_prov[prov_col].nunique()
        logger.info(f"  Province × Year: {n_prov} 省 × "
                     f"{idx_prov['year'].nunique()} 年 "
                     f"= {len(idx_prov)} 组")
    else:
        logger.warning(f"  列 '{prov_col}' 不存在, 跳过")

    # ═══════════════════════════════════════════════════════
    # (C) City × Year 指数
    # ═══════════════════════════════════════════════════════
    city_col = '城市'
    if city_col in df_unique.columns:
        idx_city = _build_geo_index(df_unique, city_col, 'ft_attn_city',
                                    min_articles=_ATTN_MIN_ARTICLES)
        # 保存中间数据
        _save_attn_index(idx_city.rename(columns={
            city_col: 'city', '_total': 'total_articles',
            '_ft': 'fintech_articles'}), '40_attn_index_city_year')

        panel = _merge_geo_index_to_panel(
            df_all, panel, idx_city[[city_col, 'year', 'ft_attn_city']],
            city_col, 'ft_attn_city')
        n_city = idx_city[city_col].nunique()
        logger.info(f"  City × Year: {n_city} 市 × "
                     f"{idx_city['year'].nunique()} 年 "
                     f"= {len(idx_city)} 组")
    else:
        logger.warning(f"  列 '{city_col}' 不存在, 跳过")

    # ── 释放内存 ──
    del df_all, df_unique

    # ── 校验 ──
    _validate_attention_index(panel)
    return panel


def _build_geo_index(df_unique, geo_col, val_col, min_articles=5):
    """从唯一文章计算 地理×年度 注意力指数。

    Args:
        df_unique:    按 docid 去重后的唯一文章 DataFrame。
        geo_col:      地理列名 ('国家地区/省份' 或 '城市')。
        val_col:      输出值列名 ('ft_attn_prov' 或 'ft_attn_city')。
        min_articles: 最低文章数阈值。低于此值的 geo×year 不参与
                      指数计算 (避免 1 篇文章产生 0/1 噪声指数)。

    Returns:
        pd.DataFrame: 含 [geo_col, 'year', '_total', '_ft', val_col] 的指数表。
    """
    df_geo = df_unique.dropna(subset=[geo_col])
    total = df_geo.groupby([geo_col, 'year']).size().reset_index(name='_total')
    ft = (df_geo[df_geo['is_fintech_news'] == True]
          .groupby([geo_col, 'year']).size().reset_index(name='_ft'))
    idx = total.merge(ft, on=[geo_col, 'year'], how='left')
    idx['_ft'] = idx['_ft'].fillna(0)

    # 过滤小样本 (避免噪声)
    before = len(idx)
    idx = idx[idx['_total'] >= min_articles]
    dropped = before - len(idx)
    if dropped > 0:
        logger.info(f"    过滤 {dropped} 个 {geo_col}×Year 组 "
                     f"(文章数 < {min_articles})")

    idx[val_col] = idx['_ft'] / idx['_total']
    return idx  # 返回完整列 (含 _total, _ft), 供保存中间数据使用


def _save_attn_index(df, basename):
    """保存注意力指数中间数据 (Parquet + CSV)。"""
    parquet_path = os.path.join(OUTPUT_DIR, f'{basename}.parquet')
    csv_path = os.path.join(OUTPUT_DIR, f'{basename}.csv')
    df.to_parquet(parquet_path, index=False)
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    logger.info(f"    已保存: {basename} ({len(df)} 行)")


def _merge_geo_index_to_panel(df_all, panel, idx_geo,
                               geo_col, target_col):
    """将地理注意力指数通过曝露度加权合并到 Bank-Year 面板。

    合并策略 (Exposure-weighted average):
      1. df_all 中每行 = (article, target_bank), 含媒体来源地
      2. 为每行匹配其来源地的 attention index
      3. 按 (target_bank, year) 取均值
         → "报道该银行的全部媒体所在地区的平均金融科技关注度"

    ⚠️ 权重基于 df_all (含 fintech + non-fintech 全量银行新闻),
       确保地理曝露反映银行的真实媒体环境, 而非仅金融科技新闻的分布。

    Returns:
        panel: 附加 target_col 列的面板。
    """
    # 1. 选取需要的列并清洗
    work = df_all[['target_bank', 'year', geo_col]].copy()
    work = work.dropna(subset=[geo_col])

    # 2. 匹配地理指数
    work = work.merge(idx_geo, on=[geo_col, 'year'], how='left')
    # left join miss → 该 geo×year 被 min_articles 过滤掉, 值为 NaN, 不参与均值

    # 3. Bank-Year 均值
    bank_yr = (work.groupby(['target_bank', 'year'])[target_col]
               .mean().reset_index())

    # 4. 安全合并到 panel (避免 .values 位置赋值的脆弱性)
    if target_col in panel.columns:
        panel = panel.drop(columns=[target_col])
    panel = panel.merge(bank_yr, on=['target_bank', 'year'], how='left')

    matched = panel[target_col].notna().sum()
    logger.info(f"    {target_col}: 匹配 {matched}/{len(panel)} "
                f"({matched/len(panel)*100:.1f}%)")
    return panel


def _validate_attention_index(panel):
    """校验注意力指数变量。"""
    for col in ['ft_attn_yr', 'ft_attn_prov', 'ft_attn_city']:
        if col not in panel.columns:
            continue
        valid = panel[col].dropna()
        if len(valid) == 0:
            logger.warning(f"  ⚠️ {col}: 全为 NaN")
            continue
        if not valid.between(0, 1).all():
            logger.error(f"  ✗ {col}: 含超出 [0,1] 的值!")
        else:
            logger.info(f"  ✓ {col}: mean={valid.mean():.4f}, "
                         f"std={valid.std():.4f}, "
                         f"[{valid.min():.4f}, {valid.max():.4f}]")

    # year-level 常量校验
    if 'ft_attn_yr' in panel.columns:
        _std = (panel.dropna(subset=['ft_attn_yr'])
                .groupby('year')['ft_attn_yr'].std())
        max_std = _std.max()  # NaN if all groups have n=1
        if pd.isna(max_std) or max_std <= 1e-10:
            logger.info("  ✓ ft_attn_yr 为 year-level 常量")
        else:
            logger.error("  ✗ ft_attn_yr 在同年内取值不一致!")

    # 地理指数截面变异校验
    for col in ['ft_attn_prov', 'ft_attn_city']:
        if col not in panel.columns:
            continue
        within_std = (panel.dropna(subset=[col])
                      .groupby('year')[col].std())
        mean_std = within_std.mean()  # NaN if all groups have n=1
        if pd.isna(mean_std):
            logger.info(f"  ✓ {col}: 各年均仅 1 个银行, 无法计算年内 std")
        elif mean_std < 1e-6:
            logger.warning(f"  ⚠️ {col}: 年内几乎无变异 (退化为 year-level)")
        else:
            logger.info(f"  ✓ {col}: 年内 std 均值={mean_std:.6f}")


# ============================================================================
# 6c. 媒体信息中介异质性 - 四维度 (Bushee et al. 2010, JAR)
# ============================================================================

def compute_media_heterogeneity(df, panel):
    """计算媒体信息中介异质性变量 - 四维度分析。

    四维度:
      1. 财经 vs 其他: 财经类报章 (15家) 与非财经类
      2. 综合 vs 其他: 综合性报章 (27家) 与非综合性
      3. 财经 vs 综合 vs 其他: 三方分拆
      4. 中央级 vs 地方级: CNKI 171家中央级 vs 其余
         (Qin, Strömberg & Wu 2018, AER)

    数据源: config/media_classification.json
    """
    if '媒体(中文)' not in df.columns:
        logger.warning("  媒体列不存在, 跳过")
        return panel

    logger.info("=" * 60)
    logger.info("步骤 6c: 媒体信息中介异质性 - 四维度")
    logger.info("=" * 60)

    # ── 加载媒体分类名单 ──
    config_dir = os.path.dirname(os.path.abspath(
        CONFIG['paths'].get('media_weights_file', '')))
    cls_path = os.path.join(config_dir, 'media_classification.json')
    if not os.path.exists(cls_path):
        logger.warning(f"  {cls_path} 不存在, 跳过")
        return panel

    with open(cls_path, 'r', encoding='utf-8') as f:
        media_cls = json.load(f)
    FIN = set(media_cls.get('financial_media', []))
    COMP = set(media_cls.get('comprehensive_media', []))
    CENTRAL = set(media_cls.get('central_media', []))
    logger.info(f"  财经类: {len(FIN)} 家, 综合性: {len(COMP)} 家, "
                f"中央级: {len(CENTRAL)} 家")

    # 防御性检查: 财经/综合不应重叠 (中央级与其正交, 允许重叠)
    overlap_fc = FIN & COMP
    if overlap_fc:
        logger.warning(f"  ⚠️ FIN ∩ COMP 重叠: {overlap_fc} (将归类为 fin)")
    # 信息性日志: 中央级与财经/综合的交叉
    fc_in_central = (FIN | COMP) & CENTRAL
    if fc_in_central:
        logger.info(f"  ℹ️ 财经/综合 ∩ 中央级: {len(fc_in_central)} 家 "
                    f"(正交分类, 合理)")

    # ── 维度①②③: 财经/综合/其他 三方分类 ──
    def _classify_content(name):
        if name in FIN:
            return 'fin'
        elif name in COMP:
            return 'comp'
        else:
            return 'other'
    df['_media_type'] = df['媒体(中文)'].apply(_classify_content)

    # 诊断
    vc = df['_media_type'].value_counts()
    for mt in ['fin', 'comp', 'other']:
        n = vc.get(mt, 0)
        logger.info(f"    内容分类 - {mt}: {n:,} ({n/len(df)*100:.1f}%)")

    # (1) 占比 - 维度①②
    for mt, col in [('fin', 'fin_media_frac'), ('comp', 'comp_media_frac')]:
        df[f'_is_{mt}'] = (df['_media_type'] == mt).astype(int)
        frac = (df.groupby(['target_bank', 'year'])[f'_is_{mt}']
                .mean().reset_index(name=col))
        panel = panel.merge(frac, on=['target_bank', 'year'], how='left')

    # (2) 三类型情感均值 + 三维度缺口 - 维度①②③
    for track in ['_full', '_ctx', '_title']:
        src = f'llm_vote_score{track}'
        if src not in df.columns:
            continue
        for mt, sfx in [('fin', 'fin'), ('comp', 'comp'), ('other', 'other')]:
            tone = (df[df['_media_type'] == mt]
                    .groupby(['target_bank', 'year'])[src]
                    .mean().reset_index(name=f'tone_{sfx}_media{track}'))
            panel = panel.merge(tone, on=['target_bank', 'year'], how='left')
        # 缺口
        panel[f'tone_gap_fin_other{track}'] = (
            panel.get(f'tone_fin_media{track}', np.nan)
            - panel.get(f'tone_other_media{track}', np.nan))
        panel[f'tone_gap_comp_other{track}'] = (
            panel.get(f'tone_comp_media{track}', np.nan)
            - panel.get(f'tone_other_media{track}', np.nan))
        panel[f'tone_gap_fin_comp{track}'] = (
            panel.get(f'tone_fin_media{track}', np.nan)
            - panel.get(f'tone_comp_media{track}', np.nan))

    # ── 维度④: 中央级 vs 地方级 (行政层级分类, 与①②③正交) ──
    df['_is_central'] = df['媒体(中文)'].isin(CENTRAL).astype(int)
    n_central = df['_is_central'].sum()
    logger.info(f"    行政分类 - 中央级: {n_central:,} "
                f"({n_central/len(df)*100:.1f}%)")

    # (3) 中央级占比
    frac_c = (df.groupby(['target_bank', 'year'])['_is_central']
              .mean().reset_index(name='central_media_frac'))
    panel = panel.merge(frac_c, on=['target_bank', 'year'], how='left')

    # (4) 中央/地方情感均值 + 缺口
    for track in ['_full', '_ctx', '_title']:
        src = f'llm_vote_score{track}'
        if src not in df.columns:
            continue
        for is_c, sfx in [(1, 'central'), (0, 'local')]:
            tone = (df[df['_is_central'] == is_c]
                    .groupby(['target_bank', 'year'])[src]
                    .mean().reset_index(name=f'tone_{sfx}_media{track}'))
            panel = panel.merge(tone, on=['target_bank', 'year'], how='left')
        panel[f'tone_gap_central_local{track}'] = (
            panel.get(f'tone_central_media{track}', np.nan)
            - panel.get(f'tone_local_media{track}', np.nan))

    # ── (5) 媒体来源 HHI ──
    def _hhi(group):
        s = group.value_counts(normalize=True)
        return (s ** 2).sum()
    hhi = (df.groupby(['target_bank', 'year'])['媒体(中文)']
           .apply(_hhi).reset_index(name='media_hhi'))
    panel = panel.merge(hhi, on=['target_bank', 'year'], how='left')

    # ── 清理 ──
    temp = [c for c in df.columns
            if c.startswith('_is_') or c == '_media_type']
    df.drop(columns=temp, inplace=True)
    logger.info("  已生成: fin/comp/central_media_frac, "
                "四维度 tone_gap, media_hhi")

    # ── 校验 (方案断言 5-7) ──
    # (5) 占比值域 [0, 1]
    for col in ['fin_media_frac', 'comp_media_frac', 'central_media_frac',
                'media_hhi']:
        if col in panel.columns:
            valid = panel[col].dropna()
            if len(valid) > 0 and not valid.between(0, 1).all():
                logger.error(f"  ✗ {col}: 含超出 [0,1] 的值!")
            elif len(valid) > 0:
                logger.info(f"  ✓ {col}: [{valid.min():.4f}, {valid.max():.4f}]")

    # (6) 内容分类互斥: fin + comp <= 1
    if 'fin_media_frac' in panel.columns and 'comp_media_frac' in panel.columns:
        _sum = panel['fin_media_frac'].fillna(0) + panel['comp_media_frac'].fillna(0)
        if (_sum > 1.0001).any():
            logger.error("  ✗ fin + comp 占比之和超过 1!")
        else:
            logger.info("  ✓ fin + comp 互斥约束成立")

    # (7) 中央级与内容分类正交 (无需 <= 1 校验, 仅记录交叉统计)
    logger.info("  ✓ 中央级与内容分类为正交分类 (无互斥约束)")

    return panel
