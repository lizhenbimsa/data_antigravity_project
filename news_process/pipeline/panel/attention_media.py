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
import csv

import numpy as np
import pandas as pd

# Phase 2a: 取代旧的 importlib.spec_from_file_location 反射,改为正规子包 import。
from news_process.pipeline.panel.encode import (
    CONFIG, logger, OUTPUT_DIR, FILENAMES, PANEL_CFG,
)

# ── 停刊检测的情感列前缀（动态发现用） ──
# 覆盖: LLM 投票 + 各大模型 + 词典法 + BERT
_SCORE_PATTERNS = [
    'llm_vote_score_', 'gpt5nano_score_', 'gemini3_score_',
    'grok41_score_',  # v6: 从 claude4h_score_ 重命名 (反映真实身份: xAI Grok 4.1)
    'jiang_2021_score_', 'yao_2021_score_', 'bian_2021_score_',
    'du_2022_score_', 'you_2018_score_',
    'finbert_cn_\u6b63\u9762_', 'fin_sent_zh_\u6b63\u9762_',
    'finbert2_\u6b63\u9762_',
]


def detect_defacto_cessation(df, logger, output_dir, threshold_gap=2):
    """数据驱动 + NPPA 交叉验证的隐性停刊检测。

    学术基础:
      报纸停刊导致地方企业监督真空，显著增加公司违规行为
      (Heese et al., 2022, JFE) 及公共财政成本 (Gao et al., 2020, JFE)。
      在以媒体情感为核心变量的面板研究中，必须识别并控制
      因媒体来源消失引入的样本选择偏误 (Wooldridge, 2010, Ch.19)。

    算法:
      1. 计算每家媒体的 first_year, last_year, n_articles
      2. 标记 last_year < sample_max - threshold_gap 为疑似停刊
      3. NPPA 交叉验证: confirmed / suspected / nppa_only / active
      4. 返回 ceased_media_set (confirmed ∪ suspected)

    References:
      Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). JFE, 145(2B),
        445-463. https://doi.org/10.1016/j.jfineco.2021.08.015
      Gao, P., Lee, C., & Murphy, D. (2020). JFE, 135(2), 445-467.
        https://doi.org/10.1016/j.jfineco.2019.06.003
      Wooldridge, J. M. (2010). Ch. 19. MIT Press.
    """
    media_span = df.groupby('媒体(中文)').agg(
        first_year=('year', 'min'),
        last_year=('year', 'max'),
        n_articles=('year', 'size'))
    sample_max = int(df['year'].max())
    cutoff = sample_max - threshold_gap

    data_ceased = set(media_span[
        (media_span['last_year'] < cutoff) &
        (media_span['n_articles'] >= 10)].index)

    # Phase 1 重构: 优先读取 CONFIG['paths']['nppa_newspapers_csv']。
    nppa_path = CONFIG['paths'].get(
        'nppa_newspapers_csv',
        os.path.join(os.path.dirname(__file__),
                     'config', 'nppa_newspapers_all.csv'),
    )
    nppa_ceased = set()
    if os.path.exists(nppa_path):
        try:
            with open(nppa_path, 'r', encoding='utf-8-sig') as f:
                for r in csv.DictReader(f):
                    if r['出版状态'] in ('注销', '停办', '休刊'):
                        nppa_ceased.add(r['机构名称'])
        except Exception as e:
            logger.warning(f"  NPPA CSV 读取失败: {e}")

    confirmed = data_ceased & nppa_ceased
    suspected = data_ceased - nppa_ceased
    nppa_only = (nppa_ceased & set(media_span.index)) - data_ceased
    ceased_all = confirmed | suspected

    logger.info(f"  停刊检测: confirmed={len(confirmed)}, "
                f"suspected={len(suspected)}, "
                f"nppa_only={len(nppa_only)}, "
                f"active={len(set(media_span.index) - data_ceased)}")

    df['_is_ceased_media'] = df['媒体(中文)'].isin(ceased_all).astype(int)

    report = media_span.copy()
    report['cessation_status'] = 'active'
    report.loc[report.index.isin(confirmed), 'cessation_status'] = 'confirmed'
    report.loc[report.index.isin(suspected), 'cessation_status'] = 'suspected'
    report.loc[report.index.isin(nppa_only), 'cessation_status'] = 'nppa_only'
    try:
        report.to_excel(os.path.join(output_dir, '42_cessation_report.xlsx'))
    except Exception:
        report.to_csv(os.path.join(output_dir, '42_cessation_report.csv'))

    return ceased_all, report


# 3 个时间窗口: 全样本 / 排除金融危机恢复期 / 排除四万亿刺激期
ROBUSTNESS_WINDOWS = [
    (2007, 2024, 'w0724'),
    (2010, 2024, 'w1024'),
    (2011, 2024, 'w1124'),
]


def compute_balanced_media_robustness(df, panel, logger, score_patterns):
    """3 个时间窗口的平衡媒体面板稳健性检验。

    学术基础:
      在非平衡面板中，媒体来源的进入-退出可能引入样本选择偏误。
      通过构建"全程在刊"的平衡媒体子集，检验基准结果是否受
      幸存者偏差驱动 (Wooldridge, 2010, §19.9.3)。

    References:
      Wooldridge, J. M. (2010). §19.9.3 Attrition. MIT Press.
      Engelberg & Parsons (2011). JF, 66(1), 67-97.
        https://doi.org/10.1111/j.1540-6261.2010.01626.x
    """
    media_span = df.groupby('媒体(中文)').agg(
        first_year=('year', 'min'),
        last_year=('year', 'max'))

    for start_year, end_year, suffix in ROBUSTNESS_WINDOWS:
        df_w = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
        balanced = media_span[
            (media_span['first_year'] <= start_year) &
            (media_span['last_year'] >= end_year)].index
        df_b = df_w[df_w['媒体(中文)'].isin(balanced)]

        if len(df_b) == 0:
            logger.warning(f"  窗口 {suffix}: 无平衡媒体数据")
            continue

        # (D.a) 三轨道全局情感均值 (平衡子集)
        for track in ['_full', '_ctx', '_title']:
            src = f'llm_vote_score{track}'
            col = f'bal_{suffix}_tone{track}'
            if src in df_b.columns:
                tone = (df_b.groupby(['target_bank', 'year'])[src]
                        .mean().reset_index(name=col))
                if col in panel.columns:
                    panel = panel.drop(columns=[col])
                panel = panel.merge(
                    tone, on=['target_bank', 'year'], how='left')

        # (D.b) 全方法情感均值 (平衡子集) — 动态发现
        _bal_cols = []
        for src in df_b.columns:
            if any(src.startswith(pat) for pat in score_patterns):
                # 排除已加权变体和已在 D.a 单独处理的 llm_vote_score
                if (src.endswith('_w') or '_mw_' in src or '_idf_' in src
                        or src.startswith('llm_vote_score_')):
                    continue
                col = f'bal_{suffix}_{src}'
                if len(col) > 32:
                    logger.warning(f"  变量名过长({len(col)}): {col}")
                tone = (df_b.groupby(['target_bank', 'year'])[src]
                        .mean().reset_index(name=col))
                if col in panel.columns:
                    panel = panel.drop(columns=[col])
                panel = panel.merge(
                    tone, on=['target_bank', 'year'], how='left')
                _bal_cols.append(col)

        col_n = f'n_media_bal_{suffix}'
        if col_n in panel.columns:
            panel = panel.drop(columns=[col_n])
        panel[col_n] = len(balanced)
        logger.info(f"  窗口 {suffix}: {len(balanced)} 家平衡媒体, "
                    f"3 轨道 + {len(_bal_cols)} 全方法列")

    return panel

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

    .. todo:: v3.0-split (Plan-r3 P1-7 锚点, 497 行 god function)

        本函数将四个独立维度的计算耦合在一个流程中. 学术上每维度的
        测度方法 / 引用文献 / 标准误聚类层级都不同, 拆分理由充分:

        - ``_compute_financial_vs_other`` -- 财经 / 综合 媒体语调差
        - ``_compute_breadth_index`` -- Bushee et al. 2010 媒体广度
        - ``_compute_central_periphery`` -- 央媒 / 非央媒 注意力差
        - ``_compute_temporal_attention`` -- 月度注意力衰减权重

        拆分后每个子函数独立可测 (合成 panel 行 + 各自断言), 现状只能
        端到端测.

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
    OFFICIAL = set(media_cls.get('official_media', []))
    MARKET = set(media_cls.get('market_media', []))
    DEEPDIVE = set(media_cls.get('deep_dive_periodicals', []))
    DAILY = set(media_cls.get('high_frequency_dailies', []))
    logger.info(f"  财经类: {len(FIN)} 家, 综合性: {len(COMP)} 家, "
                f"中央级: {len(CENTRAL)} 家")
    logger.info(f"  官方: {len(OFFICIAL)} 家, 市场化: {len(MARKET)} 家, "
                f"深度期刊: {len(DEEPDIVE)} 家, 高频日报: {len(DAILY)} 家")

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

    # ── 维度⑤: 官方 vs 非官方 ──
    # 理论基础: 国有控制媒体受政治激励影响, 报道倾向性与市场化媒体显著不同
    #   - You, Zhang & Zhang (2018, RFS): 官方媒体负面报道不影响高管更替,
    #     市场化媒体则有显著治理效应 (doi: 10.1093/rfs/hhx055)
    #   - Piotroski, Wong & Zhang (2015, JAR): 政治激励导致关联企业负面信息
    #     被暂时压制 (doi: 10.1111/1475-679X.12071)
    # 操作化: official_media 名单来自 NPPA 数据库, 以主管单位为党政机关为判据
    df['_is_official'] = df['媒体(中文)'].isin(OFFICIAL).astype(int)
    n_official = df['_is_official'].sum()
    logger.info(f"    政治取向 - 官方: {n_official:,} "
                f"({n_official/len(df)*100:.1f}%)")

    frac_off = (df.groupby(['target_bank', 'year'])['_is_official']
                .mean().reset_index(name='official_media_frac'))
    panel = panel.merge(frac_off, on=['target_bank', 'year'], how='left')

    for track in ['_full', '_ctx', '_title']:
        src = f'llm_vote_score{track}'
        if src not in df.columns:
            continue
        for is_o, sfx in [(1, 'official'), (0, 'nonoff')]:
            tone = (df[df['_is_official'] == is_o]
                    .groupby(['target_bank', 'year'])[src]
                    .mean().reset_index(name=f'tone_{sfx}_media{track}'))
            panel = panel.merge(tone, on=['target_bank', 'year'], how='left')
        panel[f'tone_gap_official_nonoff{track}'] = (
            panel.get(f'tone_official_media{track}', np.nan)
            - panel.get(f'tone_nonoff_media{track}', np.nan))

    # ── 维度⑥: 市场化 vs 非市场化 ──
    # 理论基础: 市场化媒体依赖广告和发行收入, 报道更独立、批判性更强
    #   - You, Zhang & Zhang (2018, RFS): 市场化媒体负面报道显著促进高管更替,
    #     体现了媒体治理功能 (doi: 10.1093/rfs/hhx055)
    #   - Fang & Peress (2009, JF): 媒体覆盖度越高, 信息不对称越低,
    #     无覆盖股票存在回报溢价 (doi: 10.1111/j.1540-6261.2009.01493.x)
    # 操作化: market_media 名单来自 NPPA 数据库, 以主办单位为企业/商业集团为判据
    df['_is_market'] = df['媒体(中文)'].isin(MARKET).astype(int)
    n_market = df['_is_market'].sum()
    logger.info(f"    政治取向 - 市场化: {n_market:,} "
                f"({n_market/len(df)*100:.1f}%)")

    frac_mkt = (df.groupby(['target_bank', 'year'])['_is_market']
                .mean().reset_index(name='market_media_frac'))
    panel = panel.merge(frac_mkt, on=['target_bank', 'year'], how='left')

    for track in ['_full', '_ctx', '_title']:
        src = f'llm_vote_score{track}'
        if src not in df.columns:
            continue
        for is_m, sfx in [(1, 'market'), (0, 'nonmkt')]:
            tone = (df[df['_is_market'] == is_m]
                    .groupby(['target_bank', 'year'])[src]
                    .mean().reset_index(name=f'tone_{sfx}_media{track}'))
            panel = panel.merge(tone, on=['target_bank', 'year'], how='left')
        panel[f'tone_gap_market_nonmkt{track}'] = (
            panel.get(f'tone_market_media{track}', np.nan)
            - panel.get(f'tone_nonmkt_media{track}', np.nan))

    # ── 维度⑦: 深度期刊 vs 非深度 ──
    # 理论基础: 低频出版的深度期刊具有更强的信息分析与原创内容创造能力
    #   - Bushee, Core, Guay & Hamm (2010, JAR): 媒体信息中介功能中,
    #     原创信息创造比简单转载传播更具治理效力 (doi: 10.1111/j.1475-679X.2009.00357.x)
    #   - Guest (2021, JAR): 深度分析型媒体的新闻原创性越高,
    #     对公司治理的改善效果越显著 (doi: 10.1111/1475-679X.12349)
    # 操作化: deep_dive_periodicals 基于 NPPA 出版周期≥周报的非日刊出版物
    df['_is_deepdive'] = df['媒体(中文)'].isin(DEEPDIVE).astype(int)
    n_deepdive = df['_is_deepdive'].sum()
    logger.info(f"    出版频率 - 深度期刊: {n_deepdive:,} "
                f"({n_deepdive/len(df)*100:.1f}%)")

    frac_dd = (df.groupby(['target_bank', 'year'])['_is_deepdive']
               .mean().reset_index(name='deepdive_media_frac'))
    panel = panel.merge(frac_dd, on=['target_bank', 'year'], how='left')

    for track in ['_full', '_ctx', '_title']:
        src = f'llm_vote_score{track}'
        if src not in df.columns:
            continue
        for is_d, sfx in [(1, 'deepdive'), (0, 'nondeep')]:
            tone = (df[df['_is_deepdive'] == is_d]
                    .groupby(['target_bank', 'year'])[src]
                    .mean().reset_index(name=f'tone_{sfx}_media{track}'))
            panel = panel.merge(tone, on=['target_bank', 'year'], how='left')
        panel[f'tone_gap_deepdive_nondeep{track}'] = (
            panel.get(f'tone_deepdive_media{track}', np.nan)
            - panel.get(f'tone_nondeep_media{track}', np.nan))

    # ── 维度⑧: 高频日报 vs 非日报 ──
    # 理论基础: 日报具有更高的出版频率和时效性, 是日频情感指标的主要驱动
    #   - Tetlock (2007, JF): 基于 WSJ 每日专栏构建悲观指数,
    #     证明日频媒体情感可预测市场回报 (doi: 10.1111/j.1540-6261.2007.01232.x)
    #   - Tetlock, Saar-Tsechansky & Macskassy (2008, JF): 每日新闻中的负面词汇比例
    #     能预测企业盈余和回报 (doi: 10.1111/j.1540-6261.2008.01362.x)
    # 操作化: high_frequency_dailies 基于 NPPA 出版周期为日报的出版物
    df['_is_daily'] = df['媒体(中文)'].isin(DAILY).astype(int)
    n_daily = df['_is_daily'].sum()
    logger.info(f"    出版频率 - 高频日报: {n_daily:,} "
                f"({n_daily/len(df)*100:.1f}%)")

    frac_dl = (df.groupby(['target_bank', 'year'])['_is_daily']
               .mean().reset_index(name='daily_media_frac'))
    panel = panel.merge(frac_dl, on=['target_bank', 'year'], how='left')

    for track in ['_full', '_ctx', '_title']:
        src = f'llm_vote_score{track}'
        if src not in df.columns:
            continue
        for is_dl, sfx in [(1, 'daily'), (0, 'nondaily')]:
            tone = (df[df['_is_daily'] == is_dl]
                    .groupby(['target_bank', 'year'])[src]
                    .mean().reset_index(name=f'tone_{sfx}_media{track}'))
            panel = panel.merge(tone, on=['target_bank', 'year'], how='left')
        panel[f'tone_gap_daily_nondaily{track}'] = (
            panel.get(f'tone_daily_media{track}', np.nan)
            - panel.get(f'tone_nondaily_media{track}', np.nan))

    # ── (5) 媒体来源 HHI ──
    def _hhi(group):
        s = group.value_counts(normalize=True)
        return (s ** 2).sum()
    hhi = (df.groupby(['target_bank', 'year'])['媒体(中文)']
           .apply(_hhi).reset_index(name='media_hhi'))
    panel = panel.merge(hhi, on=['target_bank', 'year'], how='left')

    # ── 维度⑨: 地理邻近性 — 本地 vs 异地媒体 (同省/同城双层) ──
    # 理论基础: 本地媒体因广告收入依赖、地方政府关系等因素,
    #   倾向于对本地企业进行系统性正面倾斜 (media slant)。
    #   Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype:
    #   Local media slant, local advertising, and firm value.
    #   The Journal of Finance, 67(2), 561-598.
    #   DOI: 10.1111/j.1540-6261.2012.01725.x
    # 操作化: 以银行注册地省份/城市 vs 媒体来源省份/城市进行匹配,
    #   在省级 (Prov) 和市级 (City) 两个层面平行构建三组核心指标。
    #   命名采用 homeprov/homecity 前缀, 与现有 central/local (行政层级) 正交。
    logger.info("  ── 维度⑨: 地理邻近性 (同省/同城双层) ──")

    # (9a) 加载银行注册地信息
    addr_path = os.path.join(config_dir, 'bank_addresses.json')
    if os.path.exists(addr_path):
        with open(addr_path, 'r', encoding='utf-8') as f:
            _addr_data = json.load(f)
        _bank_prov_map = {k: v.get('province', '') for k, v in _addr_data.items()}
        _bank_city_map = {k: v.get('city', '') for k, v in _addr_data.items()}
        logger.info(f"    银行注册地: {len(_bank_prov_map)} 家 "
                    f"({len(set(_bank_prov_map.values()))} 省, "
                    f"{len(set(_bank_city_map.values()))} 市)")

        # (9b) 映射到文章级数据
        df['_bank_prov'] = df['target_bank'].map(_bank_prov_map)
        df['_bank_city'] = df['target_bank'].map(_bank_city_map)

        # (9c) 地名后缀清洗 — 解决 "杭州市" ≠ "杭州" 匹配问题
        _GEO_SUFFIXES = (r'省|市|维吾尔自治区|回族自治区|壮族自治区'
                         r'|自治区|特别行政区')

        def _clean_geo(s):
            """移除行政区划后缀, 使省市名称标准化。"""
            return (s.astype(str)
                    .str.replace(_GEO_SUFFIXES, '', regex=True)
                    .str.strip())

        _news_prov_clean = _clean_geo(df['国家地区/省份'])
        _bank_prov_clean = _clean_geo(df['_bank_prov'])
        _news_city_clean = _clean_geo(df['城市']) if '城市' in df.columns else pd.Series('', index=df.index)
        _bank_city_clean = _clean_geo(df['_bank_city'])

        df['_is_homeprov'] = (_news_prov_clean == _bank_prov_clean).astype(int)
        df['_is_homecity'] = (_news_city_clean == _bank_city_clean).astype(int)

        # (9d) NaN / 空值 显式守卫
        #   防止 _clean_geo(NaN) → "nan" == "nan" 假阳性
        #   以及 "" == "" 假阳性 (当 bank_addresses 或新闻数据缺省份/城市时)
        _prov_invalid = (df['_bank_prov'].isna()
                         | df['国家地区/省份'].isna()
                         | (df['_bank_prov'].astype(str).str.strip() == '')
                         | (df['国家地区/省份'].astype(str).str.strip() == ''))
        df.loc[_prov_invalid, '_is_homeprov'] = 0
        if '城市' in df.columns:
            _city_invalid = (df['_bank_city'].isna()
                             | df['城市'].isna()
                             | (df['_bank_city'].astype(str).str.strip() == '')
                             | (df['城市'].astype(str).str.strip() == ''))
            df.loc[_city_invalid, '_is_homecity'] = 0
        else:
            df['_is_homecity'] = 0

        # (9e) 拓扑不变量: 同城 ⊆ 同省
        df['_is_homeprov'] = np.maximum(df['_is_homeprov'], df['_is_homecity'])

        # 诊断
        n_total = len(df)
        n_homeprov = df['_is_homeprov'].sum()
        n_homecity = df['_is_homecity'].sum()
        logger.info(f"    同省报道: {n_homeprov:,} ({n_homeprov/n_total*100:.1f}%), "
                    f"同城报道: {n_homecity:,} ({n_homecity/n_total*100:.1f}%)")

        # (9f) 三项核心指标 × Prov/City 双轨
        #   指标1: 偏袒度 (tone_gap) — 均值层面的系统性倾斜
        #   指标2: 封闭度 (media_frac) — 本地报道占比
        #   指标3: 负面过滤 (neg_frac) — 负面消息尾部的选择性抑制
        #     Core, J. E., Guay, W., & Larcker, D. F. (2008).
        #     The power of the pen and executive compensation.
        #     Journal of Financial Economics, 88(1), 1-25.
        #     DOI: 10.1016/j.jfineco.2007.05.001
        for geo_tag, geo_col, geo_label in [
            ('prov', '_is_homeprov', '省级'),
            ('city', '_is_homecity', '市级'),
        ]:
            home_sfx = f'home{geo_tag}'
            away_sfx = f'non{geo_tag}'

            # ── 指标2: 封闭度 ──
            frac_col = f'{home_sfx}_media_frac'
            frac = (df.groupby(['target_bank', 'year'])[geo_col]
                    .mean().reset_index(name=frac_col))
            panel = panel.merge(frac, on=['target_bank', 'year'], how='left')

            # ── 指标1: 偏袒度 + 指标3: 负面过滤 ──
            for track in ['_full', '_ctx', '_title']:
                src_tone = f'llm_vote_score{track}'
                src_neg = f'is_negative{track}'
                if src_tone not in df.columns:
                    continue

                for is_h, sfx in [(1, home_sfx), (0, away_sfx)]:
                    sub = df[df[geo_col] == is_h]
                    if sub.empty:
                        continue

                    # 指标1: 情感均值
                    tone = (sub.groupby(['target_bank', 'year'])[src_tone]
                            .mean().reset_index(
                                name=f'tone_{sfx}_media{track}'))
                    panel = panel.merge(
                        tone, on=['target_bank', 'year'], how='left')

                    # 指标3: 负面比例
                    if src_neg in df.columns:
                        neg = (sub.groupby(['target_bank', 'year'])[src_neg]
                               .mean().reset_index(
                                   name=f'neg_frac_{sfx}{track}'))
                        panel = panel.merge(
                            neg, on=['target_bank', 'year'], how='left')

                # 指标1: 偏袒度缺口
                panel[f'tone_gap_{home_sfx}_{away_sfx}{track}'] = (
                    panel.get(f'tone_{home_sfx}_media{track}', np.nan)
                    - panel.get(f'tone_{away_sfx}_media{track}', np.nan))

            logger.info(f"    {geo_label}: {frac_col} 均值="
                        f"{panel[frac_col].dropna().mean():.4f}")

        # (9g) 拓扑断言: 同省占比 >= 同城占比
        if ('homeprov_media_frac' in panel.columns
                and 'homecity_media_frac' in panel.columns):
            _valid_both = panel.dropna(
                subset=['homeprov_media_frac', 'homecity_media_frac'])
            if len(_valid_both) > 0:
                _violation = (_valid_both['homeprov_media_frac']
                              < _valid_both['homecity_media_frac'] - 1e-10)
                if _violation.any():
                    logger.error(f"  ✗ 拓扑违规: {_violation.sum()} 行 "
                                 f"homeprov_frac < homecity_frac!")
                else:
                    logger.info("  ✓ 拓扑不变量: "
                                "homeprov_media_frac >= homecity_media_frac")

        logger.info("  已生成: homeprov/homecity_media_frac, "
                    "tone_gap, neg_frac (地理邻近性)")
    else:
        logger.warning(f"  {addr_path} 不存在, 跳过维度⑨")

    # ── 隐性停刊检测 ──
    # 学术动机: 媒体来源消失引入幸存者偏差 (survivorship bias)，
    # 导致情感指标向存活媒体倾斜，污染 Bartik IV 工具变量。
    # 参考: Gentzkow et al. (2011). AER, 101(7), 2980-3018.
    #   https://doi.org/10.1257/aer.101.7.2980
    ceased_set, cessation_report = detect_defacto_cessation(
        df, logger, OUTPUT_DIR)

    # ── 停刊稳健性变量 ──
    # 构建排除停刊媒体后的替代指标，供 Stata 端系数稳定性检验。
    # 参考: Fang & Peress (2009). JF, 64(5), 2023-2052.
    #   https://doi.org/10.1111/j.1540-6261.2009.01493.x

    # (C.1) bank-year 级: 停刊媒体文章占比
    ceased_frac = (df.groupby(['target_bank', 'year'])['_is_ceased_media']
                   .mean().reset_index(name='ceased_media_frac'))
    panel = panel.merge(ceased_frac, on=['target_bank', 'year'], how='left')

    # (C.2) 排除停刊后文章数
    n_ex = (df[df['_is_ceased_media'] == 0]
            .groupby(['target_bank', 'year']).size()
            .reset_index(name='n_articles_exc'))
    panel = panel.merge(n_ex, on=['target_bank', 'year'], how='left')

    # (C.3) bank-year 三轨道全局情感均值（排除停刊）
    df_alive = df[df['_is_ceased_media'] == 0]
    for track in ['_full', '_ctx', '_title']:
        src = f'llm_vote_score{track}'
        col = f'exc_tone{track}'
        if src in df_alive.columns:
            tone = (df_alive.groupby(['target_bank', 'year'])[src]
                    .mean().reset_index(name=col))
            if col in panel.columns:
                panel = panel.drop(columns=[col])
            panel = panel.merge(tone, on=['target_bank', 'year'], how='left')

    # (C.4) 排除停刊后的全方法情感均值 — 动态发现
    # 覆盖: LLM 投票 + 各大模型 + 词典法 + BERT
    _exc_cols = []
    for src in df_alive.columns:
        if any(src.startswith(pat) for pat in _SCORE_PATTERNS):
            # 排除已加权变体和已在 C.3 单独处理的 llm_vote_score
            if (src.endswith('_w') or '_mw_' in src or '_idf_' in src
                    or src.startswith('llm_vote_score_')):
                continue
            col = f'exc_{src}'
            if len(col) > 32:
                logger.warning(f"  变量名过长({len(col)}): {col}")
            tone = (df_alive.groupby(['target_bank', 'year'])[src]
                    .mean().reset_index(name=col))
            if col in panel.columns:
                panel = panel.drop(columns=[col])
            panel = panel.merge(tone, on=['target_bank', 'year'], how='left')
            _exc_cols.append(col)
    logger.info(f"  停刊稳健性: ceased_media_frac, n_articles_exc, "
                f"exc_tone_{{full/ctx/title}}, {len(_exc_cols)} 个 exc_* 列")

    # ── 平衡媒体面板 ──
    # 参考 Wooldridge (2010, §19.9): 比较平衡/非平衡面板系数稳定性
    panel = compute_balanced_media_robustness(df, panel, logger, _SCORE_PATTERNS)

    # ── 清理 ──
    temp = [c for c in df.columns
            if c.startswith('_is_') or c == '_media_type'
            or c in ('_bank_prov', '_bank_city')]
    df.drop(columns=temp, inplace=True)
    logger.info("  已生成: fin/comp/central/official/market/deepdive/daily_media_frac, "
                "八维度 tone_gap, media_hhi")

    # ── 校验 (方案断言 5-7) ──
    # (5) 占比值域 [0, 1]
    for col in ['fin_media_frac', 'comp_media_frac', 'central_media_frac',
                'official_media_frac', 'market_media_frac',
                'deepdive_media_frac', 'daily_media_frac',
                'homeprov_media_frac', 'homecity_media_frac',
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

    # (7) deepdive + daily 互斥: deepdive + daily <= 1
    if 'deepdive_media_frac' in panel.columns and 'daily_media_frac' in panel.columns:
        _sum_dd = panel['deepdive_media_frac'].fillna(0) + panel['daily_media_frac'].fillna(0)
        if (_sum_dd > 1.0001).any():
            logger.error("  ✗ deepdive + daily 占比之和超过 1!")
        else:
            logger.info("  ✓ deepdive + daily 互斥约束成立")

    # (8) 正交分类说明
    logger.info("  ✓ 中央级/official/market 与内容分类为正交分类 (无互斥约束)")
    logger.info("  ✓ deepdive/daily 与其他维度正交")

    return panel
