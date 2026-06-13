"""
iv_extensions.py — 顶刊 IV 扩展族 (11 论文工具变量补全, 2026-06-13)
============================================================================

管线位置:
  45_panel_export_main → 步骤 8z (全部面板 merge 之后, export 之前)。
  与 iv_did.py (Bartik type/scale/fintech) / geography.py (省市 LOO) /
  llm_peer_iv.py (LLM-peer) / network_spillover.py (W² 二阶) 并列, 为
  此前缺 IV 的论文 (P2/P3/P4/P5/benefit_society/P10/P11) 物化工具变量列。

三类引擎 (全部 $0, 仅消费既有列, 无新 LLM/embedding 调用):

  1. compute_peer_loo_iv — 同组 (银行类型/经济圈) × 年 leave-one-out 均值
     白话: 拿"同类型其他银行"当年该指标的平均值 (剔除自己) 当工具。
     同业的曝光/策略推动焦点银行跟进, 但同业取值不直接进入焦点银行的
     结果方程 (排他性假设, 须在论文中披露 Manski 反射与共同冲击风险;
     _lag1 变体以滞后一期缓解同期反射)。
     学术依据:
       Manski, C. F. (1993). Identification of endogenous social effects:
         The reflection problem. The Review of Economic Studies, 60(3),
         531-542. https://doi.org/10.2307/2298123
       Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate
         financial policy? The Journal of Finance, 69(1), 139-178.
         https://doi.org/10.1111/jofi.12094
         → 同行均值 IV 的排他性局限讨论; 论文须如实披露, 勿过度宣称。
       Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of
         peer effects through social networks. Journal of Econometrics,
         150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021

  2. compute_bartik_shift_iv — 广义 Bartik: 复用步骤 7e 的基期 share 列
     (bartik_type_share_*, GPSS 基期份额外生性), shift 改为任意文章级
     变量 (fintech 强度 / 实质性占比 / 协同占比) 的组×年 LOO 均值。
     白话: "基期和哪类银行走得近"(冻结不变) × "那类银行今年在该维度的
     平均水平 (剔除自己)" = 与本行自身决策无关的外生推力。
     学术依据:
       Bartik, T. J. (1991). Who Benefits from State and Local Economic
         Development Policies? W.E. Upjohn Institute.
       Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik
         instruments: What, when, why, and how. American Economic Review,
         110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
       Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental
         shift-share research designs. The Review of Economic Studies,
         89(1), 181-213. https://doi.org/10.1093/restud/rdab030
         → 仅作 share/shift 两视角对比引用; 本引擎与 iv_did.py 同口径,
           识别仅依赖 GPSS "基期 share 外生性"视角 (shift 是 LOO 组均值,
           非准随机冲击), 论文勿主张 BHJ 双重识别。

  3. compute_outlet_composition_iv — 媒体来源构成 IV: 基期"该银行被哪些
     媒体报道"的份额 (冻结) × 各媒体当年的 house-style 水平 (剔除焦点
     银行自己的报道后计算)。
     白话: 媒体有各自稳定的"笔法风格"(有的爱用模糊词, 有的立场极端)。
     一家银行基期碰巧被哪些媒体盯上, 决定了它后来"被写得清楚不清楚 /
     被吵得凶不凶", 而这套媒体组合是基期形成的历史存量, 与银行当期
     基本面无关 (排他性: 媒体风格只经"报道文本特征"渠道作用于结果)。
     学术依据:
       Gentzkow, M., & Shapiro, J. M. (2010). What drives media slant?
         Evidence from U.S. daily newspapers. Econometrica, 78(1), 35-71.
         https://doi.org/10.3982/ECTA7195
         → 媒体立场/风格是 outlet 层面持久特征 (由需求端决定), 支撑
           "outlet house style 外生于单个被报道银行"的识别前提。
       Dougal, C., Engelberg, J., García, D., & Parsons, C. A. (2012).
         Journalists and the stock market. The Review of Financial Studies,
         25(3), 639-679. https://doi.org/10.1093/rfs/hhr133
         → 作者/媒体写作风格的准随机轮换对市场结果有因果力, 是
           "写作风格作为外生变异源"的经典识别先例。
       Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local
         media slant, local advertising, and firm value. The Journal of
         Finance, 67(2), 561-598.
         https://doi.org/10.1111/j.1540-6261.2012.01725.x
         → 媒体 slant 由媒体-企业关系 (广告) 而非企业基本面驱动的证据。
       share 外生性视角同 Goldsmith-Pinkham et al. (2020, AER)。

弱工具诊断 (全部下游 2SLS 模板统一):
  Kleibergen, F., & Paap, R. (2006). Generalized reduced rank tests using
    the singular value decomposition. Journal of Econometrics, 133(1),
    97-126. https://doi.org/10.1016/j.jeconom.2005.02.011
  Stock, J. H., & Yogo, M. (2005). Testing for weak instruments in linear
    IV regression. In Andrews & Stock (Eds.), Identification and Inference
    for Econometric Models (pp. 80-108). Cambridge University Press.
  Andrews, I., Stock, J. H., & Sun, L. (2019). Weak instruments in
    instrumental variables regression: Theory and practice. Annual Review
    of Economics, 11, 727-753.
    https://doi.org/10.1146/annurev-economics-080218-025643
    → KP rk Wald F < 临界值时模板自动追加 Anderson-Rubin 弱工具稳健 CI。

缺失语义 (与 iv_did.py fix(omni-g-ivdid) 完全同口径):
  - 组别 'other'/未映射 → NaN (不构成真实同业组, 拒绝伪零);
  - LOO 后组内剩余有效观测 < min_peers → NaN (单一同业不构成组均值);
  - share>0 × shift 缺失 → IV=NaN 传播 (不零插补);
  - 基期无文章 → share NaN → IV NaN;
  - 面板 year < max(基期年) → IV NaN (share 前视掩码);
  - 全程 float64 算术 (防 masked Int8 groupby 降型回绕, 见 iv_did.py
    fix(omni-g-ivdid-07) 同型披露)。

T=2 试跑样本披露: 当前磁盘面板 2017-2018 (T=2, 176 行) 下, _lag1 变体仅
2018 年有值、Bartik share 大面积 one-hot 退化 (iv_did.py 模块头第 3 条)。
全量语料 (2007-2024, T=18) 下自然恢复。论文须报告一阶段有效 N 与 KP F。
"""

import numpy as np
import pandas as pd

from news_process.pipeline.panel.encode import logger

# 媒体来源列 (与 network_brokerage.py L108 同一单一事实源列名)
OUTLET_COL = '媒体(中文)'


# ============================================================================
# 1. 同组 Leave-One-Out 均值 IV (panel 级变量)
# ============================================================================

def compute_peer_loo_iv(panel: pd.DataFrame,
                        var_col: str,
                        out_col: str,
                        group_col: str = 'bank_type',
                        min_peers: int = 2,
                        add_lag1: bool = True) -> pd.DataFrame:
    """同组×年 leave-one-out 均值 IV (panel 级变量通用引擎)。

    LOO_{i,t} = ( Σ_{j∈g(i), 有效} x_{j,t} − x_{i,t}·1[x_{i,t} 有效] )
                / ( n_{g(i),t}^{有效} − 1[x_{i,t} 有效] )
    其中 g(i) = panel[group_col]; 剩余有效同业数 < min_peers → NaN;
    group=='other'/NaN → NaN (伪组拒绝, 与 iv_did compute_zone_leave1out 同口径)。

    add_lag1=True 时额外产出 ``{out_col}_lag1`` = LOO_{i,t-1} (滞后一期,
    规避 Manski 1993 同期反射; 面板首年自然 NaN)。

    Args:
        panel:    Bank-Year 面板 (每 bank-year 一行)
        var_col:  内生变量所在 panel 列 (如 attention_index_full)
        out_col:  输出 IV 列名
        group_col: 分组列 (默认 bank_type, 亦可 bank_zone / bank_province)
        min_peers: LOO 后组内最少有效同业数 (默认 2)
        add_lag1:  是否产出 _lag1 滞后变体

    Returns:
        panel (追加 out_col [+ out_col_lag1])
    """
    panel = panel.copy()
    if var_col not in panel.columns or group_col not in panel.columns:
        logger.warning(f"  [peer-LOO] 缺列 {var_col!r} 或 {group_col!r}, "
                       f"{out_col} 置 NaN")
        panel[out_col] = np.nan
        if add_lag1:
            panel[f'{out_col}_lag1'] = np.nan
        return panel

    # float64 强制 (防 masked Int8 groupby 降型回绕, iv_did g-ivdid-07 同型)
    v = pd.to_numeric(panel[var_col], errors='coerce').astype('float64')
    g = panel[group_col].astype('object')
    valid_group = g.notna() & (g != 'other')

    work = pd.DataFrame({
        'target_bank': panel['target_bank'].values,
        'year': panel['year'].values,
        '_g': g.values,
        '_v': v.values,
    })
    work['_valid'] = work['_v'].notna() & valid_group.values

    # 组×年 聚合 (仅有效行进入分子分母)
    agg = (work[work['_valid']]
           .groupby(['_g', 'year'])['_v']
           .agg(_g_sum='sum', _g_cnt='count')
           .reset_index())
    work = work.merge(agg, on=['_g', 'year'], how='left')
    work['_g_sum'] = work['_g_sum'].astype('float64')
    work['_g_cnt'] = work['_g_cnt'].astype('float64')

    own_valid = work['_valid'].astype('float64')
    own_val = work['_v'].fillna(0.0) * own_valid
    remain_cnt = work['_g_cnt'].fillna(0.0) - own_valid
    remain_sum = work['_g_sum'].fillna(0.0) - own_val

    loo = np.where(
        valid_group.values & (remain_cnt >= min_peers),
        remain_sum / remain_cnt.replace(0.0, np.nan),
        np.nan,
    )
    panel[out_col] = loo

    if add_lag1:
        # LOO_{i,t-1}: 同一银行上一年的 LOO 值 (merge-based, 不依赖行序)
        lag_src = panel[['target_bank', 'year', out_col]].copy()
        lag_src['year'] = lag_src['year'] + 1
        lag_src = lag_src.rename(columns={out_col: f'{out_col}_lag1'})
        if f'{out_col}_lag1' in panel.columns:
            panel = panel.drop(columns=[f'{out_col}_lag1'])
        panel = panel.merge(lag_src, on=['target_bank', 'year'], how='left')

    n_valid = int(panel[out_col].notna().sum())
    logger.info(f"  [peer-LOO] {out_col} ← {var_col} × {group_col}: "
                f"{n_valid}/{len(panel)} 有效")
    return panel


# ============================================================================
# 2. 广义 Bartik (复用 7e 基期 share, shift = 任意文章级列)
# ============================================================================

def compute_bartik_shift_iv(panel: pd.DataFrame,
                            df_exploded: pd.DataFrame,
                            group_map: dict,
                            group_prefix: str,
                            shift_col_by_track: dict,
                            base_years: list,
                            share_prefix: str = 'bartik_type_share_',
                            value_map: dict = None) -> pd.DataFrame:
    """广义 Bartik Shift-Share IV: 基期 share (复用 7e) × 任意文章级 shift。

    BIV_{i,t} = Σ_g share_{i,g,T0} × shift_{g,t}^{LOO(i)}
    share 直接复用面板上已有的 ``{share_prefix}{g}`` 列 (步骤 7e
    compute_bartik_iv 产出, GPSS 2020 基期共现份额, 缺失语义已就位);
    shift_{g,t}^{LOO(i)} = 组 g 内【其他银行】文章级 shift 变量的年度均值。

    Args:
        panel:       Bank-Year 面板 (须已含 share 列与 bank_type)
        df_exploded: 文章级数据
        group_map:   {银行名 → 组别} (iv_did.load_bank_group_maps 的 type_map)
        group_prefix: 输出前缀, 产 ``bartik_{group_prefix}_iv_full/_ctx``
        shift_col_by_track: {'_full': 文章级列名, '_ctx': 文章级列名};
                     值为 None 的轨跳过 (输出 NaN)
        base_years:  与步骤 7e 相同的基期年集合 (前视掩码用)
        share_prefix: 面板上基期 share 列前缀 (默认复用 type 维度)
        value_map:   分类列 → 数值指示的映射 (如 {'实质性':1.0,'象征性':0.0});
                     None 时按数值列直接使用; 映射外取值 → NaN (不进分子分母)

    Returns:
        panel (追加 bartik_{group_prefix}_iv_full/_ctx)
    """
    panel = panel.copy()
    groups = sorted({v for v in group_map.values() if v != 'other'})
    share_cols = {g: f'{share_prefix}{g}' for g in groups}
    missing_share = [c for c in share_cols.values() if c not in panel.columns]
    if missing_share:
        logger.warning(f"  [bartik-{group_prefix}] 基期 share 列缺失 "
                       f"{missing_share} (步骤 7e 未运行?) → IV 置 NaN")
        for track in ['_full', '_ctx']:
            panel[f'bartik_{group_prefix}_iv{track}'] = np.nan
        return panel

    df = df_exploded[['target_bank', 'year']].copy()
    df['_g'] = df_exploded['target_bank'].map(group_map).fillna('other')

    for track in ['_full', '_ctx']:
        iv_col = f'bartik_{group_prefix}_iv{track}'
        src = shift_col_by_track.get(track)
        if src is None or src not in df_exploded.columns:
            logger.warning(f"  [bartik-{group_prefix}] 轨 {track} 缺 shift 源列 "
                           f"{src!r} → {iv_col} 置 NaN")
            panel[iv_col] = np.nan
            continue

        if value_map is not None:
            sv = df_exploded[src].map(value_map)
        else:
            sv = pd.to_numeric(df_exploded[src], errors='coerce')
        df['_s'] = sv.astype('float64').values

        sub = df[df['_g'].isin(groups) & df['_s'].notna()]
        gys = (sub.groupby(['_g', 'year'])['_s']
               .agg(_sum='sum', _cnt='count').reset_index())
        bgc = (sub.groupby(['target_bank', '_g', 'year'])['_s']
               .agg(_bi_sum='sum', _bi_cnt='count').reset_index())

        abd = panel[['target_bank', 'year']].drop_duplicates()
        for g in groups:
            gs = gys[gys['_g'] == g][['year', '_sum', '_cnt']]
            gs = gs.rename(columns={'_sum': f'_sum_{g}', '_cnt': f'_cnt_{g}'})
            abd = abd.merge(gs, on='year', how='left')
            bi = bgc[bgc['_g'] == g][['target_bank', 'year', '_bi_sum', '_bi_cnt']]
            bi = bi.rename(columns={'_bi_sum': f'_bi_sum_{g}',
                                    '_bi_cnt': f'_bi_cnt_{g}'})
            abd = abd.merge(bi, on=['target_bank', 'year'], how='left')
            abd[f'_bi_sum_{g}'] = abd[f'_bi_sum_{g}'].fillna(0.0)
            abd[f'_bi_cnt_{g}'] = abd[f'_bi_cnt_{g}'].fillna(0.0)
            # float64 已保证; LOO: 组内仅剩自身 → NaN
            remain_sum = (abd[f'_sum_{g}'].astype('float64')
                          - abd[f'_bi_sum_{g}'])
            remain_cnt = (abd[f'_cnt_{g}'].astype('float64')
                          - abd[f'_bi_cnt_{g}'])
            abd[f'shift_{g}'] = np.where(remain_cnt > 0,
                                         remain_sum / remain_cnt, np.nan)

        biv = panel[['target_bank', 'year']].copy()
        for g in groups:
            biv[f's_{g}'] = panel[share_cols[g]].astype('float64')
        biv = biv.merge(
            abd[['target_bank', 'year'] + [f'shift_{g}' for g in groups]],
            on=['target_bank', 'year'], how='left')

        biv_val = pd.Series(0.0, index=biv.index)
        for g in groups:
            _share = biv[f's_{g}']
            _shift = biv[f'shift_{g}'].astype('float64')
            # share>0 × shift 缺失 → NaN 传播; share==0 → 该维零贡献;
            # share NaN (基期无文章) → NaN 传播 (iv_did 同口径)
            biv_val = biv_val + (_share * _shift).mask(_share == 0, 0.0)

        biv_result = biv[['target_bank', 'year']].copy()
        biv_result[iv_col] = biv_val.values
        if iv_col in panel.columns:
            panel = panel.drop(columns=[iv_col])
        panel = panel.merge(biv_result, on=['target_bank', 'year'], how='left')

    # share 前视掩码 (iv_did fix(omni-g-ivdid-02) 同口径)
    _pre_base = panel['year'] < max(int(y) for y in base_years)
    if _pre_base.any():
        for track in ['_full', '_ctx']:
            iv_col = f'bartik_{group_prefix}_iv{track}'
            if iv_col in panel.columns:
                panel.loc[_pre_base, iv_col] = np.nan
        logger.warning(f"  [bartik-{group_prefix}] {int(_pre_base.sum())} 行早于"
                       f"基期末年 → IV 置 NaN (share 前视掩码)")

    for track in ['_full', '_ctx']:
        iv_col = f'bartik_{group_prefix}_iv{track}'
        if iv_col in panel.columns:
            n_valid = int(panel[iv_col].notna().sum())
            logger.info(f"  [bartik-{group_prefix}] {iv_col}: "
                        f"{n_valid}/{len(panel)} 有效")
    return panel


# ============================================================================
# 3. 媒体来源构成 IV (outlet composition / house-style exposure)
# ============================================================================

def compute_outlet_composition_iv(panel: pd.DataFrame,
                                  df_exploded: pd.DataFrame,
                                  shift_values_by_track: dict,
                                  out_prefix: str,
                                  base_years: list,
                                  outlet_col: str = OUTLET_COL,
                                  min_outlet_loo: int = 1) -> pd.DataFrame:
    """媒体来源构成 IV: 基期 outlet 份额 × outlet-year house-style LOO 水平。

    IV_{i,t} = Σ_o share_{i,o,T0} × style_{o,t}^{排除银行 i 的文章}
      share_{i,o,T0} = 基期银行 i 文章中来自媒体 o 的占比 (分母 = 基期
                       outlet 可识别的全部文章; 基期无文章 → NaN);
      style_{o,t}    = 媒体 o 在年 t 全部文章 (剔除报道焦点银行 i 的文章)
                       的 shift 变量均值; 剩余文章数 < min_outlet_loo → NaN。
    缺失传播: 任一 share>0 的 outlet 当年 style 不可计算 → IV NaN (strict,
    与 iv_did 同口径, 不做 available-renormalize — 后者会让"哪些媒体还在
    报道"这一内生选择回流进工具)。

    Args:
        panel:        Bank-Year 面板
        df_exploded:  文章级数据 (须含 outlet_col)
        shift_values_by_track: {'_full': pd.Series, '_ctx': pd.Series} —
                      与 df_exploded 行对齐的文章级 style 取值 (调用方
                      预构造, 如 clarity 分或 |tone − 年均| 离散度);
                      值为 None 的轨跳过
        out_prefix:   输出前缀, 产 ``{out_prefix}_full/_ctx``
        base_years:   基期年集合 (share 冻结 + 前视掩码)
        outlet_col:   媒体来源列
        min_outlet_loo: LOO 后 outlet-year 最少剩余文章数 (默认 1)

    Returns:
        panel (追加 {out_prefix}_full/_ctx)
    """
    panel = panel.copy()
    resolved_base = sorted({int(y) for y in base_years})

    if outlet_col not in df_exploded.columns:
        logger.warning(f"  [outlet-IV {out_prefix}] 缺媒体来源列 {outlet_col!r} "
                       f"→ 全轨置 NaN")
        for track in ['_full', '_ctx']:
            panel[f'{out_prefix}{track}'] = np.nan
        return panel

    outlet = df_exploded[outlet_col].astype('object')
    outlet_ok = outlet.notna() & (outlet.astype(str).str.strip() != '')

    # --- 基期 outlet 份额 (冻结) ---
    base_mask = df_exploded['year'].isin(resolved_base) & outlet_ok
    base = pd.DataFrame({
        'target_bank': df_exploded.loc[base_mask, 'target_bank'].values,
        '_outlet': outlet[base_mask].astype(str).values,
    })
    if base.empty:
        logger.warning(f"  [outlet-IV {out_prefix}] 基期 {resolved_base} 无可识别"
                       f"媒体来源文章 → 全轨置 NaN")
        for track in ['_full', '_ctx']:
            panel[f'{out_prefix}{track}'] = np.nan
        return panel

    cnt_io = (base.groupby(['target_bank', '_outlet'])
              .size().rename('_n_io').reset_index())
    cnt_i = (base.groupby('target_bank')
             .size().rename('_n_i').reset_index())
    shares = cnt_io.merge(cnt_i, on='target_bank')
    shares['_share'] = (shares['_n_io'].astype('float64')
                        / shares['_n_i'].astype('float64'))

    # 银行 × 面板年份 的 (bank, outlet, year) 长表骨架
    bank_years = panel[['target_bank', 'year']].drop_duplicates()
    long = shares[['target_bank', '_outlet', '_share']].merge(
        bank_years, on='target_bank', how='inner')

    for track in ['_full', '_ctx']:
        iv_col = f'{out_prefix}{track}'
        sv = shift_values_by_track.get(track)
        if sv is None:
            logger.warning(f"  [outlet-IV {out_prefix}] 轨 {track} 无 shift 值 "
                           f"→ {iv_col} 置 NaN")
            panel[iv_col] = np.nan
            continue

        art = pd.DataFrame({
            'target_bank': df_exploded['target_bank'].values,
            'year': df_exploded['year'].values,
            '_outlet': outlet.astype(str).values,
            '_v': pd.to_numeric(sv, errors='coerce').astype('float64').values,
        })
        art = art[outlet_ok.values & art['_v'].notna()]

        # outlet×year 聚合 + 银行×outlet×year 贡献 (LOO 减除)
        oy = (art.groupby(['_outlet', 'year'])['_v']
              .agg(_sum='sum', _cnt='count').reset_index())
        boy = (art.groupby(['target_bank', '_outlet', 'year'])['_v']
               .agg(_bi_sum='sum', _bi_cnt='count').reset_index())

        tl = long.merge(oy, on=['_outlet', 'year'], how='left')
        tl = tl.merge(boy, on=['target_bank', '_outlet', 'year'], how='left')
        tl['_bi_sum'] = tl['_bi_sum'].fillna(0.0)
        tl['_bi_cnt'] = tl['_bi_cnt'].fillna(0.0)
        remain_sum = tl['_sum'].astype('float64') - tl['_bi_sum']
        remain_cnt = tl['_cnt'].astype('float64') - tl['_bi_cnt']
        tl['_style'] = np.where(remain_cnt >= min_outlet_loo,
                                remain_sum / remain_cnt.replace(0.0, np.nan),
                                np.nan)
        tl['_term'] = tl['_share'] * tl['_style']

        # strict NaN 传播: 任一 share>0 项 style 缺失 → 该 bank-year IV NaN
        grp = tl.groupby(['target_bank', 'year'])
        total = grp['_term'].sum(min_count=1)
        has_nan = grp['_term'].apply(lambda s: bool(s.isna().any()))
        iv_series = total.mask(has_nan).rename(iv_col).reset_index()

        if iv_col in panel.columns:
            panel = panel.drop(columns=[iv_col])
        panel = panel.merge(iv_series, on=['target_bank', 'year'], how='left')

    # share 前视掩码
    _pre_base = panel['year'] < max(resolved_base)
    if _pre_base.any():
        for track in ['_full', '_ctx']:
            iv_col = f'{out_prefix}{track}'
            if iv_col in panel.columns:
                panel.loc[_pre_base, iv_col] = np.nan
        logger.warning(f"  [outlet-IV {out_prefix}] {int(_pre_base.sum())} 行早于"
                       f"基期末年 → IV 置 NaN (share 前视掩码)")

    for track in ['_full', '_ctx']:
        iv_col = f'{out_prefix}{track}'
        if iv_col in panel.columns:
            n_valid = int(panel[iv_col].notna().sum())
            logger.info(f"  [outlet-IV] {iv_col}: {n_valid}/{len(panel)} 有效")
    return panel


# ============================================================================
# 4. 编排入口 (runner 步骤 8z 调用)
# ============================================================================

def compute_iv_extensions(panel: pd.DataFrame,
                          df_exploded: pd.DataFrame,
                          type_map: dict,
                          base_years: list) -> pd.DataFrame:
    """11 论文 IV 补全编排 (2026-06-13)。

    逐论文产出 (列名与 paper_spec.yaml::identification.iv 一一对应):
      P2  attention: leave_one_out_peer_attention_iv(_lag1)
                     + bartik_attention_iv / bartik_attention_iv_ctx
      P3  substance: leave_one_out_peer_subst_iv(_lag1)
                     + bartik_subst_iv_full/_ctx
      P4  locus:     leave_one_out_peer_locus_iv(_lag1)
      P5  collab:    leave_one_out_peer_collab_iv(_lag1)
                     + bartik_collab_iv_full/_ctx
      BS  benefit_society: leave_one_out_peer_benefit_iv(_lag1)
                     + zone_leave1out_benefit_iv (+ zone_leave1out_benefit_iv_ctx)
      P10 disagreement: outlet_disp_exposure_iv_full/_ctx
      P11 clarity:   outlet_style_clarity_iv_full/_ctx
    (P1/llm_peer/brokerage/strategic_diff 既有 IV 不在此处, 见 geography.py /
     llm_peer_iv.py / network_spillover.py / iv_did.py。)

    ctx 轨同业 LOO 工具 (2026-06-13 四 agent 对抗终审落地, lpeer_* 前缀):
      lpeer_attention_iv_ctx(_lag1)  ← attention_index_ctx
      lpeer_subst_iv_ctx(_lag1)      ← sub_frac_sc
      lpeer_locus_iv_ctx(_lag1)      ← tech_frac_lc
      lpeer_collab_iv_ctx(_lag1)     ← collab_frac_cm
      lpeer_benefit_iv_ctx(_lag1)    ← benefit_mean_ctx
      zone_leave1out_benefit_iv_ctx  ← benefit_mean_ctx (bank_zone 分组, 无 _lag1)
    与各论文 full 轨 LOO (leave_one_out_peer_*_iv / zone_leave1out_benefit_iv) 一一
    镜像; 紧凑前缀 lpeer_
    使全部 ≤32 字符 (含 _ctx_lag1=27), 绕开 stata_export 32-char 截断歧义、
    模板可直接引名 (codebook 约定见 stata_export HEURISTIC_LABELS)。
    用法 (审计裁决): ctx 轨内生变量 (sub_frac_sc 等) 配 ctx LOO 工具, 与 full
    轨【各自 just-identified、并排成列】表达双轨互为稳健性 (dualtrack-is-
    mutual-robustness); 严禁把 full+ctx 两支 LOO 拼成一对工具跑 Hansen J —
    二者源自同一篇文章的两个剪裁窗口 (full=标题+全文 / ctx=标题+实体窗口),
    bank_type×year 共同冲击逐字同污染两轨 → J 对真实威胁功效≈0、近共线还拖垮
    KP rk F (Parente & Santos Silva 2012 EL)。要做 overid 用跨族工具 (LOO ×
    Bartik / LOO × zone-LOO, 见各 2SLS 模板既有 overid 列)。
    """
    logger.info("=" * 60)
    logger.info("步骤 8z: IV 扩展族 (11 论文工具变量补全, 2026-06-13)")
    logger.info("=" * 60)

    # ── P2: attention (Hassan et al. 2019 QJE 注意力测度的同业/Bartik 工具) ──
    panel = compute_peer_loo_iv(panel, 'attention_index_full',
                                'leave_one_out_peer_attention_iv')
    # ctx 轨镜像 (实体窗口归因; 与 full 轨各自 just-identified 并排, 勿合成 overid)
    panel = compute_peer_loo_iv(panel, 'attention_index_ctx',
                                'lpeer_attention_iv_ctx')
    panel = compute_bartik_shift_iv(
        panel, df_exploded, type_map, 'attention',
        {'_full': 'fintech_intensity_score_full',
         '_ctx': 'fintech_intensity_score_ctx'},
        base_years)
    # 模板/spec 契约名: 主名无轨后缀 = full 轨 (与 llm_peer_iv 主名约定一致)
    if 'bartik_attention_iv_full' in panel.columns:
        panel['bartik_attention_iv'] = panel['bartik_attention_iv_full']

    # ── P3: substance (W&Z 实质性 vs 象征性) ──
    panel = compute_peer_loo_iv(panel, 'sub_frac',
                                'leave_one_out_peer_subst_iv')
    panel = compute_peer_loo_iv(panel, 'sub_frac_sc',
                                'lpeer_subst_iv_ctx')
    panel = compute_bartik_shift_iv(
        panel, df_exploded, type_map, 'subst',
        {'_full': 'innovation_substantiveness_full',
         '_ctx': 'innovation_substantiveness_ctx'},
        base_years,
        value_map={'实质性': 1.0, '象征性': 0.0})

    # ── P4: locus (Gomber 底层技术 vs 应用场景; spec primary) ──
    panel = compute_peer_loo_iv(panel, 'tech_frac',
                                'leave_one_out_peer_locus_iv')
    panel = compute_peer_loo_iv(panel, 'tech_frac_lc',
                                'lpeer_locus_iv_ctx')

    # ── P5: collab (Chesbrough 自主研发 vs 外部协同) ──
    panel = compute_peer_loo_iv(panel, 'collab_frac',
                                'leave_one_out_peer_collab_iv')
    panel = compute_peer_loo_iv(panel, 'collab_frac_cm',
                                'lpeer_collab_iv_ctx')
    panel = compute_bartik_shift_iv(
        panel, df_exploded, type_map, 'collab',
        {'_full': 'innovation_collab_mode_full',
         '_ctx': 'innovation_collab_mode_ctx'},
        base_years,
        value_map={'外部协同': 1.0, '自主研发': 0.0})

    # ── benefit_society: 经营效益态度 (Jha, Liu & Manela 2026 RFS 测度) ──
    panel = compute_peer_loo_iv(panel, 'benefit_mean_full',
                                'leave_one_out_peer_benefit_iv')
    panel = compute_peer_loo_iv(panel, 'benefit_mean_ctx',
                                'lpeer_benefit_iv_ctx')
    if 'bank_zone' in panel.columns:
        panel = compute_peer_loo_iv(panel, 'benefit_mean_full',
                                    'zone_leave1out_benefit_iv',
                                    group_col='bank_zone', add_lag1=False)
        # ctx 轨镜像 (2026-06-13 缺口补全): 内生孪生 benefit_mean_ctx 配同经济圈
        # ctx LOO 工具, 与 full 轨 zone LOO【各自 just-identified、并排成列】表达双轨
        # 互为稳健性 (实体窗口 vs 全文归因); 严禁与 full 轨 zone LOO 合成 overid —
        # 同篇两窗共同冲击同污染, Hansen J 零功效 (Parente & Santos Silva 2012 EL)。
        # benefit_mean_ctx 缺列时 compute_peer_loo_iv 内置守卫优雅置 NaN。
        # ⚠ zone_leave1out_benefit_iv_ctx 是真新面板列 → 落盘须重跑 stage 45/46 +
        #   golden 重生 (CLAUDE.md 约束 6; 本机不可安全 regen, 留受控生产 run)。
        panel = compute_peer_loo_iv(panel, 'benefit_mean_ctx',
                                    'zone_leave1out_benefit_iv_ctx',
                                    group_col='bank_zone', add_lag1=False)
    else:
        panel['zone_leave1out_benefit_iv'] = np.nan
        panel['zone_leave1out_benefit_iv_ctx'] = np.nan
        logger.warning("  bank_zone 缺失 (7f 未运行?), "
                       "zone_leave1out_benefit_iv(_ctx) 置 NaN")

    # ── P10: 跨媒体分歧 — 媒体组合"立场离散度"暴露 ──
    # 文章级 style = |tone − 该年全样本均值| (媒体 house-style 极端度;
    # Gentzkow & Shapiro 2010 媒体立场持久性)。年内 demean 防把"年份级
    # 共同情绪水平"误装进 style。
    disp_vals = {}
    for track in ['_full', '_ctx']:
        sc = f'llm_vote_score{track}'
        if sc in df_exploded.columns:
            s = pd.to_numeric(df_exploded[sc], errors='coerce').astype('float64')
            year_mean = s.groupby(df_exploded['year']).transform('mean')
            disp_vals[track] = (s - year_mean).abs()
        else:
            disp_vals[track] = None
    panel = compute_outlet_composition_iv(
        panel, df_exploded, disp_vals, 'outlet_disp_exposure_iv', base_years)

    # ── P11: 清晰度 — 媒体组合"笔法清晰度"暴露 (Dougal et al. 2012 RFS) ──
    clarity_vals = {
        track: (df_exploded[f'clarity_clarity_score{track}']
                if f'clarity_clarity_score{track}' in df_exploded.columns
                else None)
        for track in ['_full', '_ctx']
    }
    panel = compute_outlet_composition_iv(
        panel, df_exploded, clarity_vals, 'outlet_style_clarity_iv', base_years)

    logger.info("  IV 扩展族完成 ✓")
    return panel
