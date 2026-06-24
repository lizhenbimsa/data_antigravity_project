"""
44_panel_iv_did.py — Bartik IV 与 DID 政策冲击
==========================================================

功能:
  - 银行分组映射加载 (load_bank_group_maps)
  - 通用 Bartik Shift-Share IV (compute_bartik_iv)
  - 文章属性维度 Bartik IV (compute_bartik_iv_fintech)
  - 经济圈 Leave-One-Out IV (compute_zone_leave1out)
  - DID 政策冲击变量合并 (merge_policy_shocks)

拆分自: 40_build_panel.py (L144-652)
学术依据:
  Goldsmith-Pinkham, Sorkin & Swift (2020, AER) — Bartik IV
  Callaway & Sant’Anna (2021, JoE) — Staggered DID

识别设计披露 (metric-audit 2026-06-02, 论文须如实声明, 勿过度宣称):
  1. **shift 是内生 LOO 情感均值, 非准随机外生冲击**: compute_bartik_iv 的
     shift_g = 组 g 内其他银行的 leave-one-out 年度 llm_vote_score 均值
     (L210-218), 与被解释变量(本行情感/绩效)同源、存在 Manski(1993) 反射与共同
     冲击. 故识别**仅依赖 GPSS(2020) "基期 share 外生性"视角**, **不**满足
     Borusyak-Hull-Jaravel(2022) "shift 准随机"视角 — 论文勿主张双重识别;
     诊断走 Rotemberg(share)而非 shift 平衡性. (本模块各函数注释中对 BHJ 的引用
     仅作对比, 非声称满足其前提.)
     ⚠ 三轨铁律: bartik_*_iv_full / _ctx / _ss (ss=银行+金科同句) 是同一识别策略
       在三种文本归因窗口下的并列工具, **各自 just-identified 单独进 2SLS**;
       绝不可把 full+ctx+ss 三轨拼进同一 over-id Hansen J (三轨高度共线, 互为
       稳健性而非独立矩条件 — 与 iv_extensions Hansen J 红线一致)。
  2. **diagnose_rotemberg_weights 是近似, 非 GPSS α_k**: 用 Cov(share,BIV)/
     Var(BIV) 的单变量 OLS 投影代替真正的两阶段 Rotemberg 分解; 其"负权重/HHI"
     仅作快速集中度提示, **正式论文的 Rotemberg 权重须走 Stata bartik_weight 包**
     (函数内已给命令), 不得以本近似冒充 GPSS §5 诊断.
  3. **T=2 面板结构退化**: 当前面板仅 2017-2018 (84 banks × 2y). Bartik share
     在 64%(112/176) bank-year 退化为 own-type one-hot (基期 co-mention 跨组为
     0 → L137-143 兜底 share=1.0), fintech 基期类别 96.7% app vs 3.3% tech →
     工具近共线于 bank-type FE、一阶段 F 弱; DiD(dcep/sandbox) 处理年份均 ≥2019
     (晚于面板末年 2018) 致 _post 恒 0、不可识别 (fix(ivdid-stata-01): 原文误写
     "≤2018", 归因方向倒置, 实为处理年份晚于样本期末). 论文须报告一阶段有效 N/F、
     披露退化并相应降权这些 spec.
  4. **缺失语义 (fix(omni g-ivdid, 2026-06-11))**: 基期无文章的银行 share/IV 保持
     NaN (非 0 — 消除 GPSS 2020 incomplete-shares 伪零暴露); share>0 而该组该年
     shift 不可计算 (LOO 组内仅剩自身) → IV=NaN 传播 (不再零插补); 面板 year <
     基期末年 → IV=NaN (share 前视掩码); zone LOO 'other' 伪经济圈 → NaN。
  5. **DiD 处理分配是 HQ-based (fix(omni-g-ivdid-06))**: merge_policy_shocks 按
     银行总部城市/省份匹配试点名单 — 对城商行/农商行 (经营地≈总部) 近似成立, 对
     全国经营的 soe/joint 银行总部所在地≠业务暴露 (总部北京的全国性银行整体编入
     DCEP 首批)。论文须披露并以剔除 soe/joint 作 robustness。
"""

import json
import os

import numpy as np
import pandas as pd

# 日志四位有效数字规范 (用户决策 2026-06-24): logger 输出的所有非整数一律经 sig4/pct4
# 渲染。纯字符串格式化, 不参与任何产物计算 (golden-safe)。
from news_process.core.logging import pct4, sig4

# Phase 2a: 取代旧的 importlib.spec_from_file_location 反射,改为正规子包 import。
from news_process.pipeline.panel.encode import CONFIG, logger

# ============================================================================
# 方法学参考文献 (single source of truth for IN-LOG citations)
# 经核验注册表 (Crossref/DataCite 真值) 逐字照抄; 仅 emit 进日志, 绝不参与计算。
# ============================================================================
_IV_DID_REFERENCES = (
    "Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: "
    "What, when, why, and how. American Economic Review, 110(8), 2586-2624. "
    "https://doi.org/10.1257/aer.20181047",
    "Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share "
    "research designs. The Review of Economic Studies, 89(1), 181-213. "
    "https://doi.org/10.1093/restud/rdab030",
    "Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-in-Differences with "
    "multiple time periods. Journal of Econometrics, 225(2), 200-230. "
    "https://doi.org/10.1016/j.jeconom.2020.12.001",
)


def _log_iv_did_method_refs(lg=None) -> None:
    """把本模块核心方法 (Bartik shift-share IV / 交错 DiD) 的学术出处 emit 进日志。

    called-by-runner 库模块无独立 main(), 该函数在首个被调入口 (compute_bartik_iv)
    起始处调用一次, 让 .log 而非仅注释承载 DOI 级方法学溯源 (顶刊审计标准)。
    白话: 把"我们的工具变量/双重差分是按哪几篇经典论文做的"写进运行日志, 方便复核。
    """
    try:
        _lg = lg or logger
        _lg.info("  📖 方法论依据 (Bartik shift-share IV + 交错 DiD):")
        _lg.info("    · Bartik IV (share 视角=基期份额外生性): " + _IV_DID_REFERENCES[0])
        _lg.info("    · shift-share (shift 视角=冲击准随机, 仅作对比非双重主张): "
                 + _IV_DID_REFERENCES[1])
        _lg.info("    · 交错 DiD (多期处理时点, ATT 分解): " + _IV_DID_REFERENCES[2])
    except Exception as e:  # noqa: BLE001 — 日志块绝不得让阶段崩溃
        (lg or logger).warning(f"  方法论引用日志块跳过 (非致命): {e}")

# ============================================================================
# 2b. 银行分组映射加载 (Bartik IV 前置依赖)
# ============================================================================

def load_bank_group_maps() -> tuple:
    """从 bank_addresses.json 读取银行分组映射。

    Returns:
        type_map:  {银行名 → 'soe'/'joint'/'city'/'rural'/'private'/'foreign'/'other'}
        scale_map: {银行名 → 'L'/'M'/'S'/'XS'/'other'}
    """
    # Phase 1 重构: 优先读取 CONFIG['paths']['bank_addresses_file']。
    addr_path = CONFIG['paths'].get(
        'bank_addresses_file',
        os.path.join(os.path.dirname(__file__), 'config', 'bank_addresses.json'),
    )
    with open(addr_path, 'r', encoding='utf-8') as f:
        addresses = json.load(f)

    NFRA_TO_SHORT = {
        '国有大型商业银行': 'soe',
        '股份制商业银行':   'joint',
        '城市商业银行':     'city',
        '农村商业银行':     'rural',
        '民营银行':         'private',
        '外资法人银行':     'foreign',
    }
    SCALE_TO_SHORT = {
        'L(大型)': 'L', 'M(中型)': 'M', 'S(小型)': 'S', 'XS(微型)': 'XS',
    }

    type_map, scale_map = {}, {}
    for bank_name, info in addresses.items():
        type_map[bank_name] = NFRA_TO_SHORT.get(info.get('nfra_type', ''), 'other')
        scale_map[bank_name] = SCALE_TO_SHORT.get(info.get('enterprise_scale', ''), 'other')

    return type_map, scale_map


# ============================================================================
# 2c. 通用 Bartik Shift-Share IV 计算
#     学术依据:
#       [1] Goldsmith-Pinkham, Sorkin & Swift (2020, AER)
#           DOI: 10.1257/aer.20181047  — Share 视角: 基期份额外生性
#       [2] Borusyak, Hull & Jaravel (2022, RES)
#           DOI: 10.1093/restud/rdab030 — Shift 视角: 冲击准随机性
# ============================================================================

def compute_bartik_iv(panel: pd.DataFrame,
                      df_exploded: pd.DataFrame,
                      bank_group_map: dict,
                      group_prefix: str,
                      base_year: int = None,
                      base_years: list = None) -> pd.DataFrame:
    """通用 Bartik Shift-Share IV 计算。

    参数:
        panel:          Bank-Year 面板
        df_exploded:    文章级数据 (含 target_bank, co_mentioned_banks)
        bank_group_map: {银行名 → 组别标签} (如 type_map 或 scale_map)
        group_prefix:   输出列名前缀 ('type' 或 'scale')
        base_year:      基期年份 (None 且 base_years 未给时 = 面板最早年份)
        base_years:     基期年份集合 (fix(omni, 2026-06-11): 多年时 share 在基期年
                        集合上池化, 供 _t01 等基期敏感性变体使用; 与 base_year
                        同时给定时以 base_years 为准)

    输出列:
        bartik_{prefix}_iv_full / _ctx / _ss   — Bartik IV 值 (三轨; ss=银行+金科同句,
                                                 ⚠ 三轨各自 just-identified, 禁混进
                                                 同一 over-id Hansen J)
        bartik_{prefix}_share_{group}          — 基期份额
        bank_{prefix}                          — 银行分组标签

    缺失语义 (fix(omni-g-ivdid-01/-02/-03, 2026-06-11), 行为变更披露):
        - 基期无文章的银行: share/IV 保持 NaN (原 fillna(0) 制造伪零暴露);
        - share>0 但该组该年 shift 不可计算 (LOO 组内仅剩自身): IV=NaN 传播;
        - 面板 year < max(基期年): IV=NaN (share 测自未来 → 前视掩码)。

    索引安全: 全程 merge-based, 不依赖行序。

    白话: Bartik (shift-share) 工具变量 = "基期份额 × 别人的变化"。先在基期
    (样本最早年) 量好每家银行和哪些同业类别走得近 (share, 之后冻结不变),
    再用"同类别里**除自己以外**其他银行"当年的平均语调当外生推力 (shift),
    两者相乘得到一个"与本行自身决策无关、但能预测本行所受舆论冲击"的工具,
    用来缓解情感与结果互为因果的内生性。份额必须用基期冻结值, 否则份额
    本身就被当期结果污染了。
    """
    # fix(omni-g-ivdid-02, 2026-06-11): base_years 池化基期 (真 _t01); None 时退回
    # base_year 单年, 再退回面板最早年 — 兼容旧语义。
    if base_years is not None:
        resolved_base_years = sorted({int(y) for y in base_years})
    elif base_year is not None:
        resolved_base_years = [int(base_year)]
    else:
        resolved_base_years = [int(panel['year'].min())]
    groups = sorted(set(v for v in bank_group_map.values() if v != 'other'))
    # ── 子步骤 banner: Bartik shift-share IV (called-by-runner, 共享 panel-export 日志) ──
    try:
        logger.info("=" * 60)
        logger.info(f"步骤 7e/8z: Bartik Shift-Share IV [{group_prefix}] — 缓解情感↔结果内生性")
        logger.info("  方法: 基期份额 (冻结) × 同组其他银行 LOO 情感 shift; 三轨 full/ctx/ss "
                    "各自 just-identified, 禁混进同一 over-id Hansen J")
        logger.info("=" * 60)
        _log_iv_did_method_refs()
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  Bartik IV banner 跳过 (非致命): {e}")
    logger.info(f"  Bartik IV [{group_prefix}]: 基期 T0={resolved_base_years}, "
                f"组别={groups} ({len(groups)} 维)")
    panel = panel.copy()

    # --- Step 1: 银行分组标签 ---
    panel[f'bank_{group_prefix}'] = (
        panel['target_bank'].map(bank_group_map).fillna('other')
    )

    # --- Step 2: 基期份额 (通过 co_mentioned_banks 计算跨组暴露) ---
    base = df_exploded[df_exploded['year'].isin(resolved_base_years)].copy()
    if len(base) == 0:
        logger.warning(f"  基期 T0={resolved_base_years} 无数据, "
                       f"Bartik IV [{group_prefix}] 跳过")
        # 三轨 (full/ctx/ss): ss=银行+金科同句, 基期无数据时三轨同置 NaN
        for track in ['_full', '_ctx', '_ss']:
            panel[f'bartik_{group_prefix}_iv{track}'] = np.nan
        return panel

    # perf(accel-ivdid-01): explode + map + groupby 替代 apply(get_co_groups) + 逐 bank
    # O(|base|) 布尔重扫 (base[base['target_bank']==bank]) + 嵌套 python 计数。跨组共现
    # 计数向量化; 份额公式 / total==0 own-group one-hot 兜底 / 'other' 排除 / own_group
    # ∉groups→skip(NaN) / 基期无文章→NaN 语义逐位保留 (int 计数 + int/int→float)。
    def _split_cobanks(co_banks_str):
        if not co_banks_str or str(co_banks_str).strip() in ('', 'nan'):
            return []
        return [b.strip() for b in str(co_banks_str).split(';') if b.strip()]

    _ex = base[['target_bank', 'co_mentioned_banks']].copy()
    _ex['_cobank'] = _ex['co_mentioned_banks'].apply(_split_cobanks)
    _ex = _ex.explode('_cobank').dropna(subset=['_cobank'])
    if len(_ex) > 0:
        _ex['_grp'] = _ex['_cobank'].map(bank_group_map).fillna('other')
        _ex = _ex[_ex['_grp'] != 'other']
    if len(_ex) > 0:
        _cnt = _ex.groupby(['target_bank', '_grp']).size()  # (bank, group) → 非 other 计数
        _tot = _ex.groupby('target_bank').size().to_dict()  # bank → total (非 other 共现)
    else:
        _cnt = pd.Series(dtype='int64')
        _tot = {}

    # 计算每家银行在基期的跨组暴露份额。遍历**有基期文章的银行** (base 的 unique target_bank,
    # = 原 panel-bank ∩ base-bank: 原对 panel bank 无 base 行者 continue → 同效; base-only
    # bank 的多余 share 行在下游按 target_bank 的 panel merge 中被自然丢弃, 不影响结果)。
    shares_data = []
    for bank in base['target_bank'].unique():
        total = _tot.get(bank, 0)
        if total == 0:
            own_group = bank_group_map.get(bank, 'other')
            # fix(omni-g-ivdid-01, 2026-06-11): own_group=='other' (未映射银行) 时
            # one-hot 兜底退化为全 0 行 (own group 不在 kept groups) → Σshare=0≠1,
            # IV 输出伪零 — 与基期无文章同口径保持 NaN (skip → merge 后 share NaN);
            # 与 compute_bartik_iv_fintech "基期文章全 'other'/未映射 → NaN" 一致。
            if own_group not in groups:
                continue
            for g in groups:
                shares_data.append({
                    'target_bank': bank, 'group': g,
                    'share': 1.0 if g == own_group else 0.0
                })
        else:
            for g in groups:
                shares_data.append({
                    'target_bank': bank, 'group': g,
                    'share': _cnt.get((bank, g), 0) / total
                })

    # 显式列名: shares_data 为空时仍保有 schema, 下游按列筛选不抛 KeyError
    shares_df = pd.DataFrame(shares_data, columns=['target_bank', 'group', 'share'])

    for g in groups:
        g_shares = shares_df[shares_df['group'] == g][['target_bank', 'share']]
        col_name = f'bartik_{group_prefix}_share_{g}'
        g_shares = g_shares.rename(columns={'share': col_name})
        # 防止多次调用时重复列: 先删除已有列
        if col_name in panel.columns:
            panel = panel.drop(columns=[col_name])
        panel = panel.merge(g_shares, on='target_bank', how='left')
        # fix(omni-g-ivdid-01, 2026-06-11): 基期无文章的银行 share 保持 NaN —
        # 原 fillna(0) 把"工具缺失"伪装成"零暴露", 7 族 IV 输出 12σ/50σ 离群伪零
        # 直接污染 2SLS 一阶段 (GPSS 2020 incomplete-shares); IV 经 Step 4 随之 NaN。

    # --- Step 3: 组别×年份 shift (关键: 自身组=LOO, 其他组=FULL) ---
    df_with_group = pd.concat(
        [
            df_exploded.copy(),
            pd.DataFrame({
                '_group': df_exploded['target_bank'].map(bank_group_map).fillna('other')
            }, index=df_exploded.index),
        ],
        axis=1,
    ).copy()

    # 三轨 (full/ctx/ss): ss=银行+金科同句轨, 消费 llm_vote_score_ss 文章列;
    # 缺列 (stage 21 未产 ss) 时下方守卫置 NaN 优雅跳过 (镜像 ctx)。
    for track in ['_full', '_ctx', '_ss']:
        score_col = f'llm_vote_score{track}'
        if score_col not in df_with_group.columns:
            panel[f'bartik_{group_prefix}_iv{track}'] = np.nan
            continue

        # Step 3a: 组×年份 的聚合统计 (文章级)
        group_year_stats = (df_with_group[df_with_group['_group'].isin(groups)]
                           .groupby(['_group', 'year'])[score_col]
                           .agg(['sum', 'count'])
                           .reset_index())

        # Step 3b: 银行×组×年份 的贡献量 (用于 LOO 减除)
        bank_group_contrib = (df_with_group[df_with_group['_group'].isin(groups)]
                             .groupby(['target_bank', '_group', 'year'])[score_col]
                             .agg(['sum', 'count'])
                             .reset_index()
                             .rename(columns={'sum': '_bi_sum', 'count': '_bi_cnt'}))

        # Step 3c: 为每个 (bank, year) 构建各组 shift
        all_banks_df = panel[['target_bank', 'year']].drop_duplicates()

        for g in groups:
            # 组 g 的年度聚合
            g_stats = group_year_stats[group_year_stats['_group'] == g][['year', 'sum', 'count']]
            g_stats = g_stats.rename(columns={'sum': f'_sum_{g}', 'count': f'_cnt_{g}'})
            all_banks_df = all_banks_df.merge(g_stats, on='year', how='left')

            # 银行 i 在组 g 中的贡献 (仅当 bank i ∈ g 时有值)
            bi_g = bank_group_contrib[bank_group_contrib['_group'] == g][
                ['target_bank', 'year', '_bi_sum', '_bi_cnt']]
            bi_g = bi_g.rename(columns={'_bi_sum': f'_bi_sum_{g}', '_bi_cnt': f'_bi_cnt_{g}'})
            all_banks_df = all_banks_df.merge(bi_g, on=['target_bank', 'year'], how='left')
            all_banks_df[f'_bi_sum_{g}'] = all_banks_df[f'_bi_sum_{g}'].fillna(0)
            all_banks_df[f'_bi_cnt_{g}'] = all_banks_df[f'_bi_cnt_{g}'].fillna(0)

            # LOO: (组总和 - 银行贡献) / (组计数 - 银行计数)
            # fix(omni-g-ivdid-07, 2026-06-11): float64 转换前移到减法【之前】—
            # pandas (实测 3.0.3) 对 masked Int8 的 groupby sum 按值降型 (组和落
            # [-128,127] 内时 'sum' 保持 Int8, 原 v6/F2 注释 "returns Int64
            # nullable" 前提为假), Int8−Int8 元素级减法静默回绕 (实测 124−(−6)
            # =−126) 可致 LOO shift 完整符号翻转且零警告。
            remain_sum = (all_banks_df[f'_sum_{g}'].astype('float64')
                          - all_banks_df[f'_bi_sum_{g}'].astype('float64'))
            remain_cnt = (all_banks_df[f'_cnt_{g}'].astype('float64')
                          - all_banks_df[f'_bi_cnt_{g}'].astype('float64'))
            all_banks_df[f'shift_{g}'] = np.where(
                remain_cnt > 0,
                remain_sum / remain_cnt,
                np.nan  # 组内仅有自己 → 无法 LOO
            )

        # --- Step 4: BIV = Σ share × shift (merge-based) ---
        share_cols = [f'bartik_{group_prefix}_share_{g}' for g in groups]
        biv = panel[['target_bank', 'year'] + share_cols].copy()
        shift_cols_needed = [f'shift_{g}' for g in groups]
        biv = biv.merge(
            all_banks_df[['target_bank', 'year'] + shift_cols_needed],
            on=['target_bank', 'year'], how='left')

        biv_val = pd.Series(0.0, index=biv.index)
        for g in groups:
            share_col = f'bartik_{group_prefix}_share_{g}'
            shift_col = f'shift_{g}'
            if shift_col in biv.columns:
                # fix(omni-g-ivdid-03/-09, 2026-06-11): share>0 而该组该年 shift
                # 不可计算 (LOO 组内仅剩自身) → BIV=NaN 传播, 不再 fillna(0) 零插补
                # (原注释误用 exclusion restriction 术语为零插补辩护 — 排他性约束
                # 是工具不直接进结果方程的假设, 与缺失插补无关); share 全 NaN (基期无文章) 同样
                # 传播 NaN。share==0 的维度: shift 缺失无贡献 (0×缺失 → 0)。
                _share = biv[share_col].astype('float64')
                _shift = biv[shift_col].astype('float64')
                biv_val = biv_val + (_share * _shift).mask(_share == 0, 0.0)

        # 通过 target_bank+year 对齐回 panel，确保行序安全
        biv_result = biv[['target_bank', 'year']].copy()
        biv_result[f'bartik_{group_prefix}_iv{track}'] = biv_val.values
        # 先删除已有列(若存在)再 merge
        iv_col = f'bartik_{group_prefix}_iv{track}'
        if iv_col in panel.columns:
            panel = panel.drop(columns=[iv_col])
        panel = panel.merge(biv_result[['target_bank', 'year', iv_col]],
                            on=['target_bank', 'year'], how='left')

    # fix(omni-g-ivdid-02, 2026-06-11): share 前视掩码 — share 测自基期年集合,
    # year < max(基期年) 的面板行携带"未来"测得的 share (T=18 全量下 T0=2010 时
    # 2007-2009 行触发), GPSS(2020) "基期份额预定"外生性论证对这些行结构性失效
    # → IV 置 NaN (share 列保留, 仅供诊断)。
    _pre_base_mask = panel['year'] < max(resolved_base_years)
    if _pre_base_mask.any():
        # 三轨 (full/ctx/ss) 前视掩码同步
        for track in ['_full', '_ctx', '_ss']:
            iv_col = f'bartik_{group_prefix}_iv{track}'
            if iv_col in panel.columns:
                panel.loc[_pre_base_mask, iv_col] = np.nan
        logger.warning(
            f"  [{group_prefix}] {int(_pre_base_mask.sum())} 行面板年份早于基期末年 "
            f"{max(resolved_base_years)} → IV 置 NaN (share 前视掩码)")

    # 诊断
    group_dist = panel.drop_duplicates('target_bank')[f'bank_{group_prefix}'].value_counts()
    logger.info(f"  分组分布: {dict(group_dist)}")

    return panel


# ============================================================================
# 2d. 文章属性维度 Bartik IV (基于文章自身分类列, 而非 co_mentioned_banks)
#     适用于 innovation_locus, _media_type, _half_year 等维度
# ============================================================================

def compute_bartik_iv_fintech(panel: pd.DataFrame,
                              df_exploded: pd.DataFrame,
                              category_map: dict,
                              group_prefix: str,
                              base_year: int = None,
                              category_col: str = 'innovation_locus',
                              base_years: list = None) -> pd.DataFrame:
    """文章属性维度 Bartik IV (基于文章自身分类列, 而非 co_mentioned_banks)。

    通用接口: 可接受任意文章级分类列 (innovation_locus, _media_type,
    _half_year, _doclen_type 等), 将文章按 category_col 分组后计算
    Bartik Shift-Share IV。

    share_{i,k,T0} = 银行 i 在基期文章中, category_col=k 的占比
    shift_{k,t}    = 类别 k 中其他银行的 leave-one-out 年度情感均值

    缺失语义 (fix(omni-g-ivdid-01/-02/-03, 2026-06-11), 行为变更披露, 与
    compute_bartik_iv 同口径): 基期无文章或基期文章全 'other'/未映射的银行
    share/IV 保持 NaN (原 fillna(0) 伪零); share>0 × shift 缺失 → IV=NaN 传播;
    year < max(基期年) → IV=NaN (前视掩码); base_years 给定时基期池化。
    """
    # fix(omni-g-ivdid-02, 2026-06-11): 基期解析与 compute_bartik_iv 一致
    if base_years is not None:
        resolved_base_years = sorted({int(y) for y in base_years})
    elif base_year is not None:
        resolved_base_years = [int(base_year)]
    else:
        resolved_base_years = [int(panel['year'].min())]
    # 修正5: 排除兜底类别 'other', 与 compute_bartik_iv 保持一致
    groups = sorted(set(v for v in category_map.values() if v != 'other'))
    panel = panel.copy()

    # Step 1: 基期份额 (直接从文章的分类列计算)
    base = df_exploded[df_exploded['year'].isin(resolved_base_years)].copy()
    base['_cat_short'] = base[category_col].map(category_map)

    shares = (base.groupby(['target_bank', '_cat_short']).size()
              .unstack(fill_value=0))
    # fix(ivdid-05, metric-audit 2026-06-10): 分母须仅含 kept groups (排除 'other'/未映射 NaN),
    # 与 compute_bartik_iv (type/scale) 的 total=sum-over-non-other 口径一致; 否则 'other' 计入
    # 分母却不进分子 → 基期份额和 <1, 与 type/scale 轨 (份额和=1) 归一化不可比, 跨工具系数
    # 失真 (media 轨实测 present-row 行和 0.73 vs type/scale 1.0)。reindex 到 kept 列后再归一。
    # fix(omni-g-ivdid-01, 2026-06-11): reindex 到全部非-other groups (基期未出现的
    # 类别补 0 列, 分母口径不变); total==0 (基期文章全 'other'/未映射) 的银行 share
    # 保持 NaN, 基期无文章的银行 map 后亦为 NaN — 不再 fillna(0) 制造伪零暴露。
    shares = shares.reindex(columns=groups, fill_value=0)
    total = shares.sum(axis=1).replace(0, np.nan)
    shares = shares.div(total, axis=0)

    for g in groups:
        col_name = f'bartik_{group_prefix}_share_{g}'
        panel[col_name] = panel['target_bank'].map(shares[g]).astype('float64')

    # Step 2: shift (用 bank×category×year 的贡献做 LOO 减除)
    df_cat = pd.concat(
        [
            df_exploded.copy(),
            pd.DataFrame({
                '_cat_short': df_exploded[category_col].map(category_map)
            }, index=df_exploded.index),
        ],
        axis=1,
    ).copy()

    # 三轨 (full/ctx/ss): ss=银行+金科同句轨, 消费 llm_vote_score_ss; 缺列时
    # 守卫置 NaN 优雅跳过 (镜像 ctx)。
    for track in ['_full', '_ctx', '_ss']:
        score_col = f'llm_vote_score{track}'
        if score_col not in df_cat.columns:
            panel[f'bartik_{group_prefix}_iv{track}'] = np.nan
            continue

        # 类别×年份 聚合
        gys = (df_cat[df_cat['_cat_short'].isin(groups)]
               .groupby(['_cat_short', 'year'])[score_col]
               .agg(['sum', 'count']).reset_index())

        # 银行×类别×年份 的贡献量
        bgc = (df_cat[df_cat['_cat_short'].isin(groups)]
               .groupby(['target_bank', '_cat_short', 'year'])[score_col]
               .agg(['sum', 'count']).reset_index()
               .rename(columns={'sum': '_bi_sum', 'count': '_bi_cnt'}))

        abd = panel[['target_bank', 'year']].drop_duplicates()

        for g in groups:
            gs = gys[gys['_cat_short'] == g][['year', 'sum', 'count']]
            gs = gs.rename(columns={'sum': f'_sum_{g}', 'count': f'_cnt_{g}'})
            abd = abd.merge(gs, on='year', how='left')

            bi_g = bgc[bgc['_cat_short'] == g][['target_bank', 'year', '_bi_sum', '_bi_cnt']]
            bi_g = bi_g.rename(columns={'_bi_sum': f'_bi_sum_{g}', '_bi_cnt': f'_bi_cnt_{g}'})
            abd = abd.merge(bi_g, on=['target_bank', 'year'], how='left')
            abd[f'_bi_sum_{g}'] = abd[f'_bi_sum_{g}'].fillna(0)
            abd[f'_bi_cnt_{g}'] = abd[f'_bi_cnt_{g}'].fillna(0)

            # fix(omni-g-ivdid-07, 2026-06-11): float64 转换前移到减法【之前】 —
            # masked Int8 groupby sum 按值降型, Int8−Int8 减法静默回绕可翻转
            # LOO 符号 (详见 compute_bartik_iv 同型注释)。
            remain_sum = (abd[f'_sum_{g}'].astype('float64')
                          - abd[f'_bi_sum_{g}'].astype('float64'))
            remain_cnt = (abd[f'_cnt_{g}'].astype('float64')
                          - abd[f'_bi_cnt_{g}'].astype('float64'))
            abd[f'shift_{g}'] = np.where(
                remain_cnt > 0,
                remain_sum / remain_cnt,
                np.nan
            )

        # BIV = Σ share × shift
        biv = panel[['target_bank', 'year']].copy()
        for g in groups:
            biv[f's_{g}'] = panel[f'bartik_{group_prefix}_share_{g}']
        biv = biv.merge(
            abd[['target_bank', 'year'] + [f'shift_{g}' for g in groups]],
            on=['target_bank', 'year'], how='left')
        # fix(omni-g-ivdid-03/-09, 2026-06-11): NaN share (基期无文章/全 'other') 与
        # share>0 × NaN shift (LOO 不可计算) → BIV=NaN 传播, 消除 fillna(0) 伪零;
        # share==0 的维度: shift 缺失无贡献 (与 compute_bartik_iv 同口径)。
        biv_val = pd.Series(0.0, index=biv.index)
        for g in groups:
            _share = biv[f's_{g}'].astype('float64')
            _shift = biv[f'shift_{g}'].astype('float64')
            biv_val = biv_val + (_share * _shift).mask(_share == 0, 0.0)
        # 通过 target_bank+year 对齐回 panel，确保行序安全
        biv_result = biv[['target_bank', 'year']].copy()
        biv_result[f'bartik_{group_prefix}_iv{track}'] = biv_val.values
        iv_col = f'bartik_{group_prefix}_iv{track}'
        if iv_col in panel.columns:
            panel = panel.drop(columns=[iv_col])
        panel = panel.merge(biv_result[['target_bank', 'year', iv_col]],
                            on=['target_bank', 'year'], how='left')

    # fix(omni-g-ivdid-02, 2026-06-11): share 前视掩码 (与 compute_bartik_iv 同口径)
    _pre_base_mask = panel['year'] < max(resolved_base_years)
    if _pre_base_mask.any():
        # 三轨 (full/ctx/ss) 前视掩码同步
        for track in ['_full', '_ctx', '_ss']:
            iv_col = f'bartik_{group_prefix}_iv{track}'
            if iv_col in panel.columns:
                panel.loc[_pre_base_mask, iv_col] = np.nan
        logger.warning(
            f"  [{group_prefix}] {int(_pre_base_mask.sum())} 行面板年份早于基期末年 "
            f"{max(resolved_base_years)} → IV 置 NaN (share 前视掩码)")

    # 诊断日志 (三轨 full/ctx/ss) + 结果判读: IV 覆盖率与区分度对照阈值
    for track in ['_full', '_ctx', '_ss']:
        iv_col = f'bartik_{group_prefix}_iv{track}'
        if iv_col in panel.columns:
            n_valid = int(panel[iv_col].notna().sum())
            n_rows = len(panel)
            valid_frac = n_valid / n_rows if n_rows else 0.0
            iv_mean = panel[iv_col].mean()
            iv_std = panel[iv_col].std()
            logger.info(f"  [{group_prefix}] {iv_col}: "
                        f"{n_valid:,d}/{n_rows:,d} 有效 ({pct4(valid_frac)}), "
                        f"mean={sig4(iv_mean)}, std={sig4(iv_std)}")
            # 结果判读: 覆盖率 (一阶段有效 N) + 区分度 (std=0 → 工具退化近共线于 FE)
            try:
                if valid_frac < 0.5:
                    logger.warning(f"    ⚠ {iv_col} 有效率 {pct4(valid_frac)} < 50% — "
                                   "基期退化/前视掩码致工具大面积缺失, 一阶段 N 偏低, "
                                   "相应 2SLS spec 须降权并披露 (T=2 退化, GPSS 2020)")
                if iv_std is not None and float(np.nan_to_num(iv_std)) == 0.0 and n_valid > 0:
                    logger.warning(f"    ⚠ {iv_col} std=0 — 工具零方差 (近共线于 bank-type FE), "
                                   "一阶段弱工具风险高")
            except Exception as e:  # noqa: BLE001
                logger.warning(f"    IV 结果判读跳过 (非致命): {e}")

    return panel

# ============================================================================
# 2e. 经济圈 Leave-One-Out IV
# ============================================================================

PROVINCE_TO_ZONE = {
    '北京': '京津冀', '天津': '京津冀', '河北': '京津冀',
    '上海': '长三角', '江苏': '长三角', '浙江': '长三角', '安徽': '长三角',
    '广东': '珠三角',
    '四川': '成渝', '重庆': '成渝',
    '辽宁': '东北', '吉林': '东北', '黑龙江': '东北',
    '湖北': '中部', '湖南': '中部', '江西': '中部', '山西': '中部', '河南': '中部',
    '陕西': '西北', '甘肃': '西北', '青海': '西北', '宁夏': '西北', '新疆': '西北',
    '云南': '西南', '贵州': '西南', '广西': '西南', '西藏': '西南',
    '福建': '东南', '海南': '东南',
    '山东': '环渤海', '内蒙古': '环渤海',
}


def compute_zone_leave1out(panel: pd.DataFrame,
                          df_exploded: pd.DataFrame,
                          min_group_size: int = 3) -> pd.DataFrame:
    """经济圈维度 Leave-One-Out 情感均值，作为省级 LOO 的补充 IV。

    与省级 LOO 的区别:
        - 省级 LOO: 同省内其他银行 → 粒度细，但省内银行数可能太少
        - 经济圈 LOO: 同经济圈(跨省)内其他银行 → 样本更充足，捕捉区域共同冲击

    输出列:
        zone_leave1out_tone_full / zone_leave1out_tone_ctx / zone_leave1out_tone_ss
        (三轨; ss=银行+金科同句轨; 缺 llm_vote_score_ss 时优雅置 NaN)
        bank_zone (银行所属经济圈标签)
    """
    # Step 1: 为面板加上经济圈标签
    bank_zone = panel['bank_province'].map(PROVINCE_TO_ZONE).fillna('other')
    panel = pd.concat(
        [panel.copy(), pd.DataFrame({'bank_zone': bank_zone}, index=panel.index)],
        axis=1,
    ).copy()

    # Step 2: 文章级数据也打上经济圈标签 (通过 target_bank merge)
    bank_zone_map = panel.drop_duplicates('target_bank').set_index('target_bank')['bank_zone']
    df_z = pd.concat(
        [
            df_exploded.copy(),
            pd.DataFrame({
                '_zone': df_exploded['target_bank'].map(bank_zone_map).fillna('other')
            }, index=df_exploded.index),
        ],
        axis=1,
    ).copy()
    # fix(omni-g-ivdid-04, 2026-06-11): 'other' 伪经济圈 (bank_province 未映射
    # PROVINCE_TO_ZONE) 不构成真实"区域共同冲击"组 — 其文章不进 zone 聚合, 'other'
    # 银行的 zone LOO 输出 NaN, 镜像 compute_bartik_iv 排除 'other' 的口径。
    df_z = df_z[df_z['_zone'] != 'other']

    # 三轨 (full/ctx/ss): ss=银行+金科同句轨, 消费 llm_vote_score_ss; 缺列时
    # 置 NaN 优雅跳过 (镜像 ctx)。
    for track in ['_full', '_ctx', '_ss']:
        score_col = f'llm_vote_score{track}'
        out_col = f'zone_leave1out_tone{track}'
        if score_col not in df_z.columns:
            panel[out_col] = np.nan
            continue

        # 经济圈×年份 聚合
        zone_agg = (df_z.groupby(['_zone', 'year'])[score_col]
                    .agg(['sum', 'count']).reset_index())

        # 银行×经济圈×年份 的贡献量
        bank_agg = (df_z.groupby(['target_bank', '_zone', 'year'])[score_col]
                    .agg(['sum', 'count']).reset_index()
                    .rename(columns={'sum': '_bi_sum', 'count': '_bi_cnt'}))

        # merge: 面板 ← 经济圈聚合 ← 银行贡献
        tmp = panel[['target_bank', 'year', 'bank_zone']].drop_duplicates()
        tmp = tmp.merge(zone_agg, left_on=['bank_zone', 'year'],
                        right_on=['_zone', 'year'], how='left')
        tmp = tmp.merge(bank_agg[['target_bank', 'year', '_bi_sum', '_bi_cnt']],
                        on=['target_bank', 'year'], how='left')
        tmp['_bi_sum'] = tmp['_bi_sum'].fillna(0)
        tmp['_bi_cnt'] = tmp['_bi_cnt'].fillna(0)

        # LOO: (经济圈总和 - 自身贡献) / (经济圈计数 - 自身计数)
        # fix(omni-g-ivdid-07, 2026-06-11): float64 转换前移到减法【之前】 —
        # masked Int8 groupby sum 按值降型, Int8−Int8 减法静默回绕可翻转
        # LOO 符号 (详见 compute_bartik_iv 同型注释)。
        remain_sum = tmp['sum'].astype('float64') - tmp['_bi_sum'].astype('float64')
        remain_cnt = tmp['count'].astype('float64') - tmp['_bi_cnt'].astype('float64')
        # 门槛语义披露 (g-ivdid-04): min_group_size 计的是组内(排除自身后)的
        # 【文章数】而非银行数 — 3 篇可全部来自同一家其他银行, 此时 LOO 退化为
        # 单一银行语调, "区域共同冲击"构念弱化; codebook/论文按此口径披露。
        tmp[out_col] = np.where(
            (remain_cnt >= min_group_size)
            & (tmp['bank_zone'] != 'other'),  # fix(omni-g-ivdid-04): 'other' 伪圈 → NaN
            remain_sum / remain_cnt,
            np.nan
        )
        panel = panel.merge(tmp[['target_bank', 'year', out_col]],
                            on=['target_bank', 'year'], how='left')

    # 诊断 (三轨 full/ctx/ss) + 结果判读: 区域 LOO IV 覆盖率
    zone_dist = panel.drop_duplicates('target_bank')['bank_zone'].value_counts()
    logger.info(f"  经济圈分布: {dict(zone_dist)} (min_group_size={min_group_size} 篇文章)")
    for track in ['_full', '_ctx', '_ss']:
        out_col = f'zone_leave1out_tone{track}'
        if out_col in panel.columns:
            n_valid = int(panel[out_col].notna().sum())
            n_rows = len(panel)
            valid_frac = n_valid / n_rows if n_rows else 0.0
            logger.info(f"  {out_col}: {n_valid:,d}/{n_rows:,d} 有效 ({pct4(valid_frac)})")
            if valid_frac < 0.5:
                logger.warning(f"    ⚠ {out_col} 有效率 {pct4(valid_frac)} < 50% — "
                               "经济圈内 LOO 文章数不足 min_group_size 或 'other' 伪圈致缺失, "
                               "区域共同冲击工具偏弱, 须披露")

    return panel

# ============================================================================
# 2f. DID 政策冲击变量合并
#     学术依据: Callaway & Sant'Anna (2021, JoE)
#     DOI: 10.1016/j.jeconom.2020.12.001
# ============================================================================

def merge_policy_shocks(panel: pd.DataFrame) -> pd.DataFrame:
    """合并政策冲击 DID 变量（仅年份维度，不区分波次/月份）。

    设计思路:
        面板为 Bank-Year 年度频率，因此政策冲击只需定位到"年份"即可。
        同一年内若有多批次（如 DCEP 2022年3月第三批 + 12月第四批），
        统一视为该年处理。

    对每个政策(dcep / sandbox)生成 3 个变量:
        {prefix}_treated:    处理组哑变量 (0/1)
        {prefix}_post:       政策后哑变量 (0/1)
        {prefix}_treat_year: 首次被处理的年份 (0=控制组, 用于交错DID的 gvar)

    匹配规则（按优先级从高到低）:
        1. cities:         按 bank_city 精确匹配
        2. full_province:  按 bank_province 匹配整个省份的全部银行
        3. new_cities:     按 bank_city 匹配零散新增城市
        先入为主: 一旦银行已被某年份匹配, 后续年份不再覆盖。

    识别局限披露 (fix(omni-g-ivdid-05/-06), 2026-06-11):
        1. **HQ-based 处理分配**: 试点按银行【总部注册地】城市/省份匹配。对
           城商行/农商行 (经营地≈总部) 近似成立; 对全国经营的 soe/joint 银行,
           总部所在地≠业务暴露 (如总部北京的全国性银行整体编入 DCEP 首批),
           处理强度与地方性银行不可比。robustness: 剔除 soe/joint 重估, 或仅以
           city/rural 地方性银行定义处理组。
        2. **never-treated 控制组趋空**: 政策覆盖面广 (sandbox 2022 后 23 省级
           辖区) 时 never-treated 银行结构性稀少, csdid 默认 never-treated
           baseline 由极少数特异银行驱动 — 应改用 `notyet` (not-yet-treated)。
    """
    # Phase 1 重构: 优先读取 CONFIG['paths']['policy_shocks_file']。
    shock_path = CONFIG['paths'].get(
        'policy_shocks_file',
        os.path.join(os.path.dirname(__file__), 'config', 'policy_shocks.json'),
    )
    if not os.path.exists(shock_path):
        logger.warning("  policy_shocks.json 不存在, 跳过 DID 变量")
        return panel

    with open(shock_path, 'r', encoding='utf-8') as f:
        shocks = json.load(f)

    # ── 子步骤 banner: 交错 DiD 政策冲击合并 (DCEP / 监管沙盒) ──
    try:
        logger.info("=" * 60)
        logger.info("步骤 DiD: 政策冲击处理变量合并 (treated/post/treat_year + event-study lead/lag)")
        logger.info("  方法依据: " + _IV_DID_REFERENCES[2])
        logger.info("  白话: 给每家银行标注它哪一年起被数字货币/监管沙盒试点覆盖, "
                    "生成交错 DiD 所需的处理组/政策后哑变量与事件期 (lead/lag)。")
        logger.info("=" * 60)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  DiD banner 跳过 (非致命): {e}")

    # fix(omni-g-ivdid-06, 2026-06-11): HQ-based 处理分配假设显式披露 (详见 docstring)
    logger.warning(
        "  [DiD 处理分配假设] 试点匹配基于银行总部城市/省份 (HQ-based): 全国性银行 "
        "(soe/joint) 的总部所在地≠业务暴露, 其 treat_year 系统性偏向最早处理波次; "
        "论文须披露此假设并以剔除 soe/joint (或仅 city/rural 定义处理组) 作 robustness")

    # 城市名别名映射 (雄安新区行政上属保定市)
    CITY_ALIASES = {
        '雄安': ['雄安', '保定'],
    }

    for policy_name, cfg in shocks.items():
        if policy_name.startswith('_'):
            continue
        prefix = cfg['prefix']

        # 前置校验: bank_city 是 DID 匹配的必要列
        if 'bank_city' not in panel.columns:
            logger.warning(f"  bank_city 列不存在, 跳过 {policy_name} DID 匹配"
                           " (请确保 merge_bank_geography 已在前序步骤中执行)")
            continue

        panel[f'{prefix}_treat_year'] = 0
        panel_city = panel['bank_city'].fillna('').str.rstrip('市')

        for group in cfg['groups']:
            treat_year = group['year']

            # (a) 城市级匹配
            if 'cities' in group:
                for city in group['cities']:
                    city_clean = city.rstrip('市')
                    aliases = CITY_ALIASES.get(city_clean, [city_clean])
                    for alias in aliases:
                        mask = (panel_city == alias) & (panel[f'{prefix}_treat_year'] == 0)
                        panel.loc[mask, f'{prefix}_treat_year'] = treat_year

            # (b) 省级匹配
            if 'full_province' in group and 'bank_province' in panel.columns:
                provs = set(group['full_province'])
                mask = (panel['bank_province'].isin(provs)
                        & (panel[f'{prefix}_treat_year'] == 0))
                panel.loc[mask, f'{prefix}_treat_year'] = treat_year

            # (c) 零散新增城市
            if 'new_cities' in group:
                new_city_set = set(c.rstrip('市') for c in group['new_cities'])
                if '西双版纳' in new_city_set:
                    new_city_set.add('景洪')
                mask = (panel_city.isin(new_city_set)
                        & (panel[f'{prefix}_treat_year'] == 0))
                panel.loc[mask, f'{prefix}_treat_year'] = treat_year

        # 生成最终 DID 变量
        panel[f'{prefix}_treated'] = (panel[f'{prefix}_treat_year'] > 0).astype(int)
        panel[f'{prefix}_post'] = np.where(
            panel[f'{prefix}_treat_year'] > 0,
            (panel['year'] >= panel[f'{prefix}_treat_year']).astype(int),
            0
        )

        # fix(ivdid-01): T=2 面板 + 处理年份均 ≥2019 (晚于面板末年) → _post 恒 0,
        # DiD/event-study 在当前 corpus 上结构性不可识别。fail-loud 披露, 提醒下游
        # 回归勿在 post≡0 spec 上估计 ATT (production T≥3 面板下自然恢复可识别)。
        if not (panel[f'{prefix}_post'] == 1).any():
            logger.warning(
                f"  [DiD 不可识别] {prefix}_post 全为 0 — 处理年份均晚于面板末年 "
                f"{int(panel['year'].max())}; 下游勿在此 spec 上估计 ATT")

        # ── G-01: Event Study 动态效应支持 ──
        # 学术依据: Callaway & Sant'Anna (2021, JoE), Sun & Abraham (2021, JoE)
        # relative_year = year - treat_year (控制组设为 NaN，Stata 中自动排除)
        # 用于:
        #   1. Event Study Plot: 逐期 ATT 估计
        #   2. 平行趋势检验: relative_year < 0 的系数应不显著
        #   3. 动态效应: relative_year >= 0 的系数变化趋势
        panel[f'{prefix}_rel_year'] = np.where(
            panel[f'{prefix}_treat_year'] > 0,
            panel['year'] - panel[f'{prefix}_treat_year'],
            # 控制组: NaN (Stata 自动排除)。fix(omni-g-ivdid-05): 控制组基准勿默认
            # never-treated — 该组结构性趋空时须用 csdid 的 notyet 选项 (见下方日志)
            np.nan
        )

        # 生成 Event Study lead/lag 虚拟变量 (k = -3 到 +3, 以 k=-1 为基期)
        # 设计: 覆盖 pre-treatment 3 期 + post-treatment 3 期
        #   Stata 用法:
        #     * 方法一 (csdid): csdid Y X, ivar(bank_id) time(year) gvar({prefix}_treat_year)
        #     * 方法二 (手动): reghdfe Y {prefix}_lead3 ... {prefix}_lag3 X, absorb(bank_id year)
        for k in range(-3, 4):
            if k == -1:
                continue  # k=-1 为基期 (omitted)
            col_name = f'{prefix}_lag{k}' if k >= 0 else f'{prefix}_lead{abs(k)}'
            panel[col_name] = np.where(
                panel[f'{prefix}_rel_year'] == k,
                1, 0
            ).astype(int)
            # 控制组的 lead/lag 全为 0 (因为 rel_year 是 NaN, == k 为 False)

        # Endpoint binning: k <= -4 合并为 lead4plus, k >= 4 合并为 lag4plus
        panel[f'{prefix}_lead4plus'] = np.where(
            panel[f'{prefix}_rel_year'].fillna(0) <= -4,
            (panel[f'{prefix}_treat_year'] > 0).astype(int),
            0
        ).astype(int)
        panel[f'{prefix}_lag4plus'] = np.where(
            panel[f'{prefix}_rel_year'].fillna(0) >= 4,
            (panel[f'{prefix}_treat_year'] > 0).astype(int),
            0
        ).astype(int)

        # 诊断日志
        n_treated = panel.loc[panel[f'{prefix}_treated'] == 1, 'target_bank'].nunique()
        n_control = panel.loc[panel[f'{prefix}_treated'] == 0, 'target_bank'].nunique()
        year_dist = (panel.drop_duplicates('target_bank')
                     .groupby(f'{prefix}_treat_year')['target_bank'].count()
                     .to_dict())
        logger.info(f"  {policy_name}: 处理组 {n_treated} 家, "
                    f"控制组 {n_control} 家, 年份分布 {year_dist}")

        # fix(omni-g-ivdid-05, 2026-06-11): never-treated 控制组规模守卫 — 政策
        # 覆盖面广 (sandbox 2022 后 23 省级辖区) 时 never-treated 组结构性趋空
        # (盘上实测仅 2/87 家), csdid 默认 never-treated baseline 由极少数特异
        # 银行驱动, 不可估或不可信 → 显式提醒改用 notyet。
        if 0 < n_control < 5:
            logger.warning(
                f"  [{policy_name}] never-treated 控制组仅 {n_control} 家银行 — "
                f"csdid 默认 never-treated baseline 不可靠, 请改用 notyet "
                f"(not-yet-treated 控制组) 并在论文披露")

        # Event Study 诊断
        if panel[f'{prefix}_rel_year'].notna().any():
            rel_year_dist = panel.loc[
                panel[f'{prefix}_rel_year'].notna(),
                f'{prefix}_rel_year'
            ].value_counts().sort_index().to_dict()
            logger.info(f"  {policy_name} Event Study relative_year 分布: "
                        f"{rel_year_dist}")
            logger.info(f"  {policy_name} Stata Event Study 命令:")
            # fix(omni-g-ivdid-05, 2026-06-11): 推荐 notyet (not-yet-treated 控制组) —
            # csdid 默认 never-treated baseline 在该组趋空时不可估/由特异银行驱动
            logger.info(f"    * csdid Y X, ivar(bank_id) time(year) "
                        f"gvar({prefix}_treat_year) notyet")
            logger.info(f"      // notyet = not-yet-treated 控制组; never-treated "
                        f"组过小时勿用默认 baseline")
            logger.info(f"    * estat event  // 绘制 Event Study Plot")
            logger.info(f"    * estat pretrend  // 平行趋势检验")

    # ── G-05: 多政策处理组正交性诊断 ──
    # 学术依据: Callaway & Sant'Anna (2021, JoE, §6.1):
    #   当面板中存在多个政策冲击时, 需检验处理组是否高度重叠 (overlapping treatments)。
    #   若重叠过高, DiD 估计量可能混淆多个政策效应, 导致因果识别失效。
    policy_prefixes = [cfg['prefix'] for name, cfg in shocks.items()
                       if not name.startswith('_')
                       and f"{cfg['prefix']}_treated" in panel.columns]
    if len(policy_prefixes) >= 2:
        logger.info("=" * 60)
        logger.info("G-05: 多政策处理组正交性诊断")
        logger.info("  对标: DID 标准假设 — 处理组交叉独立性")
        logger.info("=" * 60)

        from itertools import combinations
        for p1, p2 in combinations(policy_prefixes, 2):
            t1 = panel[f'{p1}_treated']
            t2 = panel[f'{p2}_treated']
            crosstab = pd.crosstab(t1, t2, margins=True)
            logger.info(f"  {p1} × {p2} 交叉表:")
            for idx in crosstab.index:
                logger.info(f"    {p1}={idx}: {dict(crosstab.loc[idx])}")

            # 计算 Cramér's V (关联强度)
            n_obs = t1.notna().sum()
            chi2 = 0
            for v1 in [0, 1]:
                for v2 in [0, 1]:
                    obs = ((t1 == v1) & (t2 == v2)).sum()
                    exp = ((t1 == v1).sum() * (t2 == v2).sum()) / max(n_obs, 1)
                    if exp > 0:
                        chi2 += (obs - exp) ** 2 / exp
            cramers_v = (chi2 / max(n_obs, 1)) ** 0.5
            logger.info(f"  Cramér's V = {sig4(cramers_v)}"
                        f" {'✓ < 0.3 弱相关 (处理组近似独立)' if cramers_v < 0.3 else '≥ 0.3 中强相关'}")
            if cramers_v >= 0.3:
                logger.info(f"  → 建议: 在论文中讨论 {p1} 与 {p2} 的处理组重叠问题,")
                logger.info(f"    或在稳健性检验中单独估计各政策效应")

    return panel


# ============================================================================
# G-03: Rotemberg 权重诊断
# ============================================================================
# 学术依据:
#   Goldsmith-Pinkham, Sorkin & Swift (2020, AER, §5):
#     "The Rotemberg weights α_k decompose the just-identified Bartik
#      estimator into a weighted sum of group-specific estimators.
#      Negative weights indicate potential misspecification."
#   DOI: 10.1257/aer.20181047
#
#   Borusyak, Hull & Jaravel (2022, RES, §4.2):
#     "Under the shift-share interpretation, one should verify that
#      no single industry (share) dominates the variation."
#   DOI: 10.1093/restud/rdab030
# ============================================================================

def diagnose_rotemberg_weights(panel: pd.DataFrame,
                                group_prefix: str,
                                groups: list = None,
                                logger_inst=None) -> dict:
    """计算 Bartik IV 的 Rotemberg (1983) 权重分解。

    Rotemberg 权重 α_k 衡量每个 share 维度 k 对整体 Bartik IV 的贡献。
    诊断目标:
      1. 识别 α_k < 0 的"负权重"维度 (Goldsmith-Pinkham 2020 §5 核心检验)
      2. 识别贡献集中度 (HHI of α_k): HHI > 0.25 表示少数维度主导
      3. 报告前 5 大权重维度及其基期份额均值

    参数:
        panel:        Bank-Year 面板
        group_prefix: Bartik IV 系列前缀 (如 'type', 'scale', 'ft_cat')
        groups:       组别列表 (None 时从面板 share 列推断)
        logger_inst:  日志实例 (None 时使用模块级 logger)

    返回:
        dict: {
          'weights': {group_k: alpha_k, ...},
          'hhi': float,
          'n_negative': int,
          'top5': [(group, weight), ...],
          'share_means': {group_k: mean_share, ...},
        }
    """
    lg = logger_inst or logger

    lg.info("=" * 60)
    lg.info(f"G-03: Rotemberg 权重诊断 [{group_prefix}]")
    lg.info("  对标: Goldsmith-Pinkham et al. (2020, AER, §5, Table 3)")
    lg.info("=" * 60)
    # 方法论引用入日志 (Rotemberg 权重分解 = GPSS §5 核心诊断; BHJ 提供 shift 视角对比)
    try:
        lg.info("  📖 方法依据:")
        lg.info("    · " + _IV_DID_REFERENCES[0])
        lg.info("    · " + _IV_DID_REFERENCES[1])
        lg.info("  注: 本函数用 Cov(share,BIV)/Var(BIV) 单变量 OLS 近似 α_k, 仅作集中度提示; "
                "正式论文须走 Stata bartik_weight 包跑真 GPSS §5 分解。")
    except Exception as e:  # noqa: BLE001
        lg.warning(f"  Rotemberg 方法引用日志块跳过 (非致命): {e}")

    # 推断组别列表
    if groups is None:
        share_cols = [c for c in panel.columns
                      if c.startswith(f'bartik_{group_prefix}_share_')]
        groups = [c.replace(f'bartik_{group_prefix}_share_', '')
                  for c in share_cols]
    if not groups:
        lg.warning(f"  未找到 bartik_{group_prefix}_share_* 列，跳过诊断")
        return {}

    # --- 计算近似 Rotemberg 权重 ---
    # α_k ≈ Cov(share_k, BIV) / Var(BIV)
    # 这是 Rotemberg (1983) 权重的 OLS 分解近似
    iv_col = f'bartik_{group_prefix}_iv_full'
    if iv_col not in panel.columns:
        lg.warning(f"  {iv_col} 不存在，跳过诊断")
        return {}

    biv = panel[iv_col].dropna()
    if biv.var() == 0 or len(biv) < 10:
        lg.warning(f"  {iv_col} 方差为 0 或样本太小，跳过诊断")
        return {}

    var_biv = biv.var()
    weights = {}
    share_means = {}
    for g in groups:
        share_col = f'bartik_{group_prefix}_share_{g}'
        if share_col not in panel.columns:
            continue
        valid = panel[[share_col, iv_col]].dropna()
        if len(valid) < 10:
            continue
        cov = valid[share_col].cov(valid[iv_col])
        alpha_k = cov / var_biv
        weights[g] = round(alpha_k, 6)
        share_means[g] = round(valid[share_col].mean(), 4)

    if not weights:
        lg.warning("  无法计算权重，跳过")
        return {}

    # --- 诊断指标 ---
    # (1) 负权重检查
    n_negative = sum(1 for v in weights.values() if v < 0)
    neg_groups = [g for g, v in weights.items() if v < 0]

    # (2) HHI 集中度 (α_k 归一化后的 Herfindahl)
    total_abs = sum(abs(v) for v in weights.values())
    if total_abs > 0:
        hhi = sum((abs(v) / total_abs) ** 2 for v in weights.values())
    else:
        hhi = 0.0

    # (3) Top-5 排序
    top5 = sorted(weights.items(), key=lambda x: abs(x[1]), reverse=True)[:5]

    # --- 日志输出 ---
    lg.info(f"  ── Rotemberg 权重 α_k (共 {len(weights):,d} 个维度) ──")
    for g, alpha in sorted(weights.items(), key=lambda x: -abs(x[1])):
        flag = " NEGATIVE" if alpha < 0 else ""
        _alpha_s = ('+' if alpha >= 0 else '-') + sig4(abs(alpha))
        lg.info(f"    {g:>15s}: α = {_alpha_s}, "
                f"E[share] = {sig4(share_means.get(g, 0))}{flag}")

    lg.info(f"  ── 诊断汇总 ──")
    lg.info(f"    负权重维度: {n_negative}/{len(weights)}"
            f"{' → ' + str(neg_groups) if neg_groups else ''}")
    if n_negative > 0:
        lg.info(f"    负权重提示可能的排他性约束违背 "
                f"(Goldsmith-Pinkham 2020, AER §5.2)")
        lg.info(f"    → 建议: 在论文稳健性检验中移除负权重维度后重新估计")
    lg.info(f"    HHI(|α|) = {sig4(hhi)}"
            f" {'✓ < 0.25 分散 (无单一 share 维度主导)' if hhi < 0.25 else '≥ 0.25 集中 (少数维度主导, BHJ 2022 §4.2 警示)'}")
    lg.info(f"    Top-5 权重维度: "
            f"{[(g, ('+' if a >= 0 else '-') + sig4(abs(a))) for g, a in top5]}")

    # Stata 命令建议
    lg.info(f"  ── Stata 验证命令 ──")
    lg.info(f"    * 使用 bartik_weight 包 (Goldsmith-Pinkham 2020 官方):")
    lg.info(f"      ssc install bartik_weight")
    lg.info(f"      bartik_weight Y bartik_{group_prefix}_iv_full "
            f"{' '.join(f'bartik_{group_prefix}_share_{g}' for g in groups[:5])}, "
            f"absorb(target_bank year)")

    result = {
        'weights': weights,
        'hhi': round(hhi, 6),
        'n_negative': n_negative,
        'negative_groups': neg_groups,
        'top5': top5,
        'share_means': share_means,
    }
    return result
