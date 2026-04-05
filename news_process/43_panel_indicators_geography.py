"""
43_panel_indicators_geography.py — 综合指标、标准化与地理信息
==========================================================

功能:
  - 综合情感指标计算 (compute_composite_indicators)
  - Fama-MacBeth 年度截面标准化 (standardize_panel_variables)
  - 银行地理信息合并 (merge_bank_geography)
  - Leave-One-Out 省/市情感 IV (compute_leave_one_out_sentiment)

拆分自: 40_build_panel.py (L1638-2181)
学术依据: Fama & MacBeth (1973, JPE); Luo & Li (2025)
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
LLM_MODELS = _m41.LLM_MODELS
DICT_NAMES = _m41.DICT_NAMES
BERT_MODELS = _m41.BERT_MODELS
THREE_CLASS_MODELS = _m41.THREE_CLASS_MODELS


# ============================================================================
# 7. 面板级综合指标计算
# ============================================================================

def compute_composite_indicators(panel: pd.DataFrame) -> pd.DataFrame:
    """在面板 DataFrame 上计算综合指标。"""
    logger.info("=" * 60)
    logger.info("步骤 7: 面板级综合指标计算")
    logger.info("=" * 60)

    def _safe_mean(cols):
        """取存在列的行均值。"""
        existing = [c for c in cols if c in panel.columns]
        if existing:
            return panel[existing].mean(axis=1)
        return pd.Series(np.nan, index=panel.index)

    # --- LLM 逐模型综合 ---
    for track in ['_full', '_ctx']:
        panel[f'llm_models_avg_tone{track}'] = _safe_mean([f'{s}_tone{track}' for s in LLM_MODELS])
        panel[f'llm_models_avg_tone_sum{track}'] = _safe_mean([f'{s}_tone_sum{track}' for s in LLM_MODELS])
        panel[f'llm_models_avg_cont{track}'] = _safe_mean([f'{s}_cont_mean{track}' for s in LLM_MODELS])
        panel[f'llm_models_avg_cont_sum{track}'] = _safe_mean([f'{s}_cont_sum{track}' for s in LLM_MODELS])
        panel[f'llm_models_avg_tone_std{track}'] = _safe_mean([f'{s}_tone_std{track}' for s in LLM_MODELS])

        # --- 词典法综合 ---
        panel[f'dict_avg_tone{track}'] = _safe_mean([f'{d}_tone{track}' for d in DICT_NAMES])
        panel[f'dict_avg_tone_sum{track}'] = _safe_mean([f'{d}_tone_sum{track}' for d in DICT_NAMES])
        panel[f'dict_avg_tone_std{track}'] = _safe_mean([f'{d}_tone_std{track}' for d in DICT_NAMES])

        # --- 词典法 IDF 综合 (Gentzkow, Kelly & Taddy 2019, JEL) ---
        panel[f'dict_avg_idf_tone{track}'] = _safe_mean([f'{d}_idf_tone{track}' for d in DICT_NAMES])
        panel[f'dict_avg_idf_tone_sum{track}'] = _safe_mean([f'{d}_idf_tone_sum{track}' for d in DICT_NAMES])

        # --- BERT 综合 ---
        panel[f'bert_avg_pos{track}'] = _safe_mean([f'{b}_pos{track}' for b in BERT_MODELS])
        panel[f'bert_avg_neg{track}'] = _safe_mean([f'{b}_neg{track}' for b in BERT_MODELS])
        panel[f'bert_avg_neu{track}'] = _safe_mean([f'{b}_neu{track}' for b in BERT_MODELS if b in THREE_CLASS_MODELS])
        panel[f'bert_avg_pos_sum{track}'] = _safe_mean([f'{b}_pos_sum{track}' for b in BERT_MODELS])
        panel[f'bert_avg_neg_sum{track}'] = _safe_mean([f'{b}_neg_sum{track}' for b in BERT_MODELS])
        panel[f'bert_avg_neu_sum{track}'] = _safe_mean([f'{b}_neu_sum{track}' for b in BERT_MODELS if b in THREE_CLASS_MODELS])
        panel[f'bert_avg_pos_std{track}'] = _safe_mean([f'{b}_pos_std{track}' for b in BERT_MODELS])

        # --- VW 综合指标 ---
        panel[f'llm_models_avg_tone_vw{track}'] = _safe_mean([f'{s}_tone_vw{track}' for s in LLM_MODELS])
        panel[f'dict_avg_tone_vw{track}'] = _safe_mean([f'{d}_tone_vw{track}' for d in DICT_NAMES])
        panel[f'dict_avg_idf_tone_vw{track}'] = _safe_mean([f'{d}_idf_tone_vw{track}' for d in DICT_NAMES])
        panel[f'bert_avg_pos_vw{track}'] = _safe_mean([f'{b}_pos_vw{track}' for b in BERT_MODELS])
        panel[f'bert_avg_neg_vw{track}'] = _safe_mean([f'{b}_neg_vw{track}' for b in BERT_MODELS])

        # --- MW 综合指标 (Holzman et al. 2023, TAR) ---
        panel[f'llm_models_avg_tone_mw{track}'] = _safe_mean([f'{s}_tone_mw{track}' for s in LLM_MODELS])
        panel[f'dict_avg_tone_mw{track}'] = _safe_mean([f'{d}_tone_mw{track}' for d in DICT_NAMES])
        panel[f'dict_avg_idf_tone_mw{track}'] = _safe_mean([f'{d}_idf_tone_mw{track}' for d in DICT_NAMES])
        panel[f'bert_avg_pos_mw{track}'] = _safe_mean([f'{b}_pos_mw{track}' for b in BERT_MODELS])
        panel[f'bert_avg_neg_mw{track}'] = _safe_mean([f'{b}_neg_mw{track}' for b in BERT_MODELS])

    logger.info(f"  生成双轨综合指标完成")

    # --- 文章平均长度 (He et al. 2024, IRFA, Panel A.5: MLENGTH) ---
    # MLENGTH = ln(文章词数), 此处取 Bank-Year 均值后 ln 变换
    if 'avg_doc_length' in panel.columns:
        panel['avg_article_length'] = np.log1p(panel['avg_doc_length'])
        logger.info(f"  avg_article_length (MLENGTH proxy) 已生成")

    # --- 分类维度综合指标 ---
    for suffix in ['_tech', '_app']:
        # 仅当分类计数列存在时生成
        if f'n_articles{suffix}' not in panel.columns:
            continue

        for track in ['_full', '_ctx']:
            # LLM 逐模型综合
            panel[f'llm_models_avg_tone{suffix}{track}'] = _safe_mean(
                [f'{s}_tone{suffix}{track}' for s in LLM_MODELS])
            panel[f'llm_models_avg_cont{suffix}{track}'] = _safe_mean(
                [f'{s}_cont_mean{suffix}{track}' for s in LLM_MODELS])

            # 词典法综合
            panel[f'dict_avg_tone{suffix}{track}'] = _safe_mean(
                [f'{d}_tone{suffix}{track}' for d in DICT_NAMES])

            # 词典法 IDF 综合
            panel[f'dict_avg_idf_tone{suffix}{track}'] = _safe_mean(
                [f'{d}_idf_tone{suffix}{track}' for d in DICT_NAMES])

            # BERT 综合
            panel[f'bert_avg_pos{suffix}{track}'] = _safe_mean(
                [f'{b}_pos{suffix}{track}' for b in BERT_MODELS])
            panel[f'bert_avg_neg{suffix}{track}'] = _safe_mean(
                [f'{b}_neg{suffix}{track}' for b in BERT_MODELS])
            panel[f'bert_avg_neu{suffix}{track}'] = _safe_mean(
                [f'{b}_neu{suffix}{track}' for b in BERT_MODELS if b in THREE_CLASS_MODELS])

        logger.info(f"  分类 {suffix} 综合指标生成完成")

    # ─── Fintech Exposure 复合指标 (Dim et al. 2024, Eq. 3 概念迁移) ───
    # 概念类比:
    #   论文: NarrativeExposure_n = Σ|β_n,l^narr| × σ(θ_l) / Σσ(θ_l)
    #     |β| = 资产对特定叙事注意力冲击的敏感度
    #     σ(θ) = 叙事注意力的时间序列波动率
    #   本项目: FintechExposure_i,t = ln_coverage_i,t × tone_std_i,t
    #     ln_coverage 类比 |β| → 银行在 fintech 叙事中的信息暴露强度
    #     tone_std 类比 σ(θ) → fintech 报道情感的离散程度
    #   乘积含义: 高覆盖 + 高波动 = 高叙事暴露度
    logger.info("  ─── Fintech Exposure 复合指标 ───")
    has_news = panel['n_articles'] > 0
    for track in ['_full', '_ctx']:
        std_col = f'llm_vote_tone_std{track}'
        if std_col in panel.columns and 'ln_news_coverage' in panel.columns:
            # 零新闻行 → NaN (与面板情感变量 NaN 语义一致)
            coverage = panel['ln_news_coverage'].where(has_news, np.nan)
            panel[f'fintech_exposure{track}'] = coverage * panel[std_col]
            valid = panel[f'fintech_exposure{track}'].dropna()
            logger.info(f"  fintech_exposure{track}: "
                        f"mean={valid.mean():.4f}, "
                        f"std={valid.std():.4f}, "
                        f"非空={len(valid):,}")
        else:
            panel[f'fintech_exposure{track}'] = np.nan
            logger.warning(f"  fintech_exposure{track}: "
                          f"缺少 {std_col} 或 ln_news_coverage, 填 NaN")

    return panel


# ============================================================================
# 7b. 年度截面标准化 (Fama & MacBeth 1973)
# ============================================================================

# 核心回归变量白名单 (仅这些列生成 _z 后缀)
_STANDARDIZE_COLS = [
    # LLM 投票 (主指标)
    'llm_vote_tone_{t}', 'llm_vote_cont_{t}',
    # LLM 逐模型综合
    'llm_models_avg_tone_{t}', 'llm_models_avg_cont_{t}',
    # 词典法综合
    'dict_avg_tone_{t}', 'dict_avg_idf_tone_{t}',
    # BERT 综合
    'bert_avg_pos_{t}', 'bert_avg_neg_{t}',
    # VW 加权
    'llm_vote_tone_vw_{t}', 'dict_avg_tone_vw_{t}',
    # MW 加权 (Holzman 2023)
    'llm_vote_tone_mw_{t}', 'dict_avg_tone_mw_{t}',
    # MSENT (He et al. 2024)
    'avg_msent_{t}',
    # Fintech Exposure (Dim et al. 2024 概念迁移)
    'fintech_exposure_{t}',
]
# 无双轨的标量变量
_STANDARDIZE_SCALAR = [
    'ln_news_coverage', 'media_breadth',
    'avg_article_length',
]


def _expand_track_templates(templates: list) -> list:
    """将含 {t} 占位符的模板展开为 _full 和 _ctx 两个变量名。"""
    result = []
    for tmpl in templates:
        if '{t}' in tmpl:
            result.append(tmpl.replace('{t}', 'full'))
            result.append(tmpl.replace('{t}', 'ctx'))
        else:
            result.append(tmpl)
    return result


def standardize_panel_variables(panel: pd.DataFrame) -> pd.DataFrame:
    """年度截面标准化: 核心回归变量在每个年度截面内归至单位方差。

    学术依据:
      Fama, E.F. & MacBeth, J.D. (1973, JPE, 71, 607-636):
        两阶段回归要求截面变量可比, 标准化确保系数
        可直接解读为 "1σ 变化对应 β 个单位的因变量变动"。

    操作:
      1. 仅处理有新闻覆盖的 Bank-Year (n_articles > 0)
      2. 对白名单内的核心回归变量执行年度截面 z-score
      3. 生成 _z 后缀列, 保留原始列不变
      4. 零新闻行保持 NaN

    输出列命名: 原列名 + '_z'
    """
    logger.info("=" * 60)
    logger.info("步骤 7b: 年度截面标准化 (Fama-MacBeth 1973)")
    logger.info("=" * 60)

    # ── 展开白名单 ──
    target_cols = (_expand_track_templates(_STANDARDIZE_COLS)
                   + _STANDARDIZE_SCALAR)
    valid_cols = [c for c in target_cols
                  if c in panel.columns
                  and panel[c].notna().sum() >= 10]
    skipped = [c for c in target_cols
               if c in panel.columns
               and panel[c].notna().sum() < 10]
    missing = [c for c in target_cols if c not in panel.columns]

    logger.info(f"  白名单总数: {len(target_cols)}, "
                f"有效: {len(valid_cols)}, "
                f"观测不足跳过: {len(skipped)}, "
                f"列不存在: {len(missing)}")
    if skipped:
        logger.info(f"    跳过(观测<10): {skipped}")

    # ── 执行年度截面 z-score ──
    has_news = panel['n_articles'] > 0
    z_count = 0

    for col in valid_cols:
        z_col = f'{col}_z'
        panel[z_col] = np.nan

        for year, grp in panel[has_news].groupby('year'):
            vals = grp[col].dropna()
            if len(vals) < 3:
                continue
            mu = vals.mean()
            sigma = vals.std()
            if sigma < 1e-10:
                continue
            idx = grp.index
            panel.loc[idx, z_col] = (panel.loc[idx, col] - mu) / sigma

        z_count += 1

    logger.info(f"  已生成 {z_count} 个 _z 标准化列")

    # ── 校验: 标准化后年内 std ≈ 1 ──
    sample_z_cols = [c for c in panel.columns if c.endswith('_z')][:5]
    for col in sample_z_cols:
        within_std = (panel[has_news].dropna(subset=[col])
                      .groupby('year')[col].std())
        mean_std = within_std.mean()
        if pd.notna(mean_std):
            ok = '✓' if abs(mean_std - 1.0) < 0.1 else '⚠️'
            logger.info(f"  校验 {col}: 年内 std 均值 = "
                        f"{mean_std:.4f} {ok}")

    return panel


# ============================================================================
# 7c. 银行注册地地理信息合并
# ============================================================================
# 学术背景:
#   在面板回归中, 标准误的聚类层级选择直接影响推断的可靠性。
#   当误差项存在组内相关时 (如同省银行受共同的地方政策、媒体生态影响),
#   在银行层级聚类会低估标准误, 导致 t 统计量虚高。
#
#   Luo & Li (2025, FRL, Table A.2 Col. 3) 使用省级聚类标准误
#   作为稳健性检验, 其核心逻辑是: 地理相近的银行面临相似的
#   媒体报道环境 (同一批地方媒体、相似的编辑倾向), 导致
#   情感得分在省内具有正相关性, 需要通过更高层级的聚类来校正。
#
#   本步骤从 bank_addresses.json 提取每家银行总行注册地的省份和城市,
#   供 Stata 回归中灵活选择聚类层级:
#     - vce(cluster bank_city)     → 329 个聚类, 超过 50 个门槛, 推断可靠
#     - vce(cluster bank_province) → 31 个聚类, 低于 50 个门槛, 需补充 wild bootstrap
#
# 参考文献:
#   [1] Luo, Q. & Li, H. (2025). "Media sentiment and corporate R&D manipulation."
#       Finance Research Letters, 81, 107505.
#   [2] Gurun, U.G. & Butler, A.W. (2012). "Don't Believe the Hype."
#       The Journal of Finance, 67(2), 561-598.
#   [3] Cameron, A.C. & Miller, D.L. (2015). "A Practitioner's Guide to
#       Cluster-Robust Inference." Journal of Human Resources, 50(2), 317-372.
# ============================================================================

def merge_bank_geography(panel: pd.DataFrame) -> pd.DataFrame:
    """步骤 7c: 合并银行注册地地理信息 (省份 + 城市)。

    本函数将 bank_addresses.json 中的银行总行注册地信息 (省份、城市)
    通过 target_bank 列名映射到 Bank-Year 面板中。合并后的地理变量
    有两个核心用途:

    用途 1 — 地理层级递进聚类标准误 (Stata):
      标准面板回归使用银行级聚类 vce(cluster target_bank), 但当扰动项
      在地理维度存在空间自相关时 (如同省银行共同受地方媒体生态影响),
      银行级聚类会低估标准误。通过逐级提升聚类层级:
        银行级 (N≈1768) → 城市级 (329) → 省级 (31)
      可检验系数显著性对聚类层级的稳健性。

      ⚠️ Cameron & Miller (2015, JHR) 指出: 聚类数 < 50 时,
      渐近正态近似不准确, 标准聚类标准误可能偏小。
      31 个省级聚类低于此门槛, 建议在 Stata 中补充
      wild cluster bootstrap (boottest 命令) 进行确认。

    用途 2 — Leave-one-out 工具变量的前置依赖:
      步骤 7d 需要知道每家银行所在的省份/城市, 才能计算
      "同省/同城市其他银行的平均情感" (leave-one-out IV)。
      本函数是 7d 的必要前置步骤。

    数据源:
      config/bank_addresses.json
      结构: {bank_name: {province, city, district, address}}
      覆盖: 1768 条记录 (含中国人民银行), 31 个省级行政区, 329 个城市
      匹配: bank_names.json 中 1767 家银行全部包含在 bank_addresses 中
            (addresses 多出的 1 条为 "中国人民银行", 不在面板 target_bank 中)

    新增列:
      bank_province — 银行总行注册所在的省级行政区
                      (直辖市单独列出, 如 "北京"、"上海")
                      Stata 用途: vce(cluster bank_province),
                                  absorb(bank_province) [替换银行FE时]
      bank_city     — 银行总行注册所在的城市
                      Stata 用途: vce(cluster bank_city)

    填充策略:
      未匹配银行 → 空字符串 '' (非 NaN)
      原因: Stata 的 cluster() 对 NaN 会报错, 空字符串可被安全忽略

    Args:
        panel: Bank-Year 面板 DataFrame, 须含 'target_bank' 列。

    Returns:
        panel: 附加 'bank_province' 和 'bank_city' 列的 DataFrame。
    """
    logger.info("=" * 60)
    logger.info("步骤 7c: 合并银行注册地地理信息 (Luo & Li 2025)")
    logger.info("=" * 60)
    logger.info("  学术依据: Luo & Li (2025, FRL, Table A.2)")
    logger.info("  聚类推断: Cameron & Miller (2015, JHR, 50(2), 317-372)")

    # ── 加载 bank_addresses.json ──
    # 路径优先从 config.yaml 的 paths.bank_addresses_file 读取,
    # 未配置时回退到项目默认路径 config/bank_addresses.json
    addr_path = CONFIG['paths'].get(
        'bank_addresses_file',
        os.path.join(os.path.dirname(__file__), 'config', 'bank_addresses.json')
    )
    if not os.path.exists(addr_path):
        logger.warning(f"  bank_addresses_file 不存在: {addr_path}, 跳过")
        # 即使文件不存在也生成空列, 确保后续步骤不会因列缺失报错
        panel['bank_province'] = ''
        panel['bank_city'] = ''
        return panel

    with open(addr_path, 'r', encoding='utf-8') as f:
        addr_data = json.load(f)
    logger.info(f"  已加载 {len(addr_data)} 条银行地址")

    # ── 构建 bank_name → province/city 映射 ──
    # bank_addresses.json 的 key 是银行标准全称 (与 bank_names.json 的
    # bank_name 字段一致), 与面板中的 target_bank 列直接对应
    prov_map = {k: v.get('province', '') for k, v in addr_data.items()}
    city_map = {k: v.get('city', '') for k, v in addr_data.items()}

    # ── 通过 target_bank 列映射到面板 ──
    # 使用 .map() 而非 merge, 因为是简单的 key → value 映射
    # .fillna('') 将未匹配的银行填为空字符串 (非 NaN)
    panel['bank_province'] = panel['target_bank'].map(prov_map).fillna('')
    panel['bank_city'] = panel['target_bank'].map(city_map).fillna('')

    # ── 匹配率诊断 ──
    matched = (panel['bank_province'] != '').sum()
    total = len(panel)
    logger.info(f"  匹配率: {matched}/{total} "
                f"= {matched / max(total, 1) * 100:.1f}%")

    # 输出未匹配银行名单 (帮助调试 bank_names 与 bank_addresses 的不一致)
    unmatched_banks = panel.loc[
        panel['bank_province'] == '', 'target_bank'
    ].unique()
    if len(unmatched_banks) > 0:
        logger.warning(f"  未匹配银行 ({len(unmatched_banks)}): "
                       f"{list(unmatched_banks)[:10]}")
    else:
        logger.info("  ✓ 全部银行匹配成功")

    # ── 聚类数统计 ──
    # Cameron & Miller (2015, JHR) 实证研究表明:
    #   聚类数 ≥ 50: 标准渐近推断 (Wald test, t-test) 可靠
    #   聚类数 < 50: 标准误可能偏小, 建议使用 wild cluster bootstrap
    n_prov = panel[panel['bank_province'] != '']['bank_province'].nunique()
    n_city = panel[panel['bank_city'] != '']['bank_city'].nunique()
    logger.info(f"  省份聚类数: {n_prov} "
                f"{'⚠️ < 50, 建议补充 wild cluster bootstrap' if n_prov < 50 else '✓ ≥ 50'}")
    logger.info(f"  城市聚类数: {n_city} "
                f"{'⚠️ < 50' if n_city < 50 else '✓ ≥ 50'}")

    # ── 分布摘要 (供审查地理覆盖合理性) ──
    prov_dist = panel[panel['bank_province'] != '']['bank_province'].value_counts()
    city_dist = panel[panel['bank_city'] != '']['bank_city'].value_counts()
    logger.info(f"  省份 Top-5: {dict(prov_dist.head())}")
    logger.info(f"  城市 Top-5: {dict(city_dist.head())}")

    return panel


# ============================================================================
# 7d. Leave-one-out 地理平均情感工具变量
# ============================================================================
# 学术背景:
#   在媒体情感 → 企业行为的回归中, 情感变量可能存在内生性:
#     (1) 反向因果: 企业行为 (如 R&D 操纵) 引发媒体报道, 而非相反
#     (2) 遗漏变量: 不可观测的企业特征同时影响媒体报道和企业行为
#
#   工具变量法 (IV) 是处理内生性的标准方法。有效 IV 须满足:
#     相关性 (relevance): IV 与内生变量显著相关
#     排他性 (exclusion): IV 仅通过内生变量影响因变量
#
#   Luo & Li (2025, FRL, Table 3) 使用 Province_news_sentiment 作为 IV:
#     定义: 同省份内排除目标企业后, 其余企业的年度平均新闻情感
#     相关性: 同省银行面临相同的地方媒体生态 (编辑倾向、记者网络),
#             导致情感得分在省内正相关
#     排他性: 其他银行的平均媒体情感反映的是省级媒体环境的整体偏向,
#             不会直接影响目标银行的 R&D 操纵决策
#
#   本步骤同时构建省级和城市级两个层次的 leave-one-out IV:
#     - 省级: 31 个省, 每省包含较多银行, IV 变异来源更宏观
#     - 城市级: 329 个城市, IV 变异更精细, 第一阶段 F 统计量通常更高
#
#   两个层级的 IV 可同时用于过度识别检验 (Hansen J test),
#   检验排他性约束是否同时成立。
#
# 与 ft_attn_prov/city 的区别:
#   ft_attn_prov/city (已在面板, Da et al. 2011; Fang & Peress 2009):
#     = 报道该银行的媒体来源地的金融科技文章占比
#     → 捕获的是 "媒体关注度" 维度的外生变异
#
#   prov/city_leave1out_tone (本步骤构建):
#     = 同省/城市其他银行的平均情感得分 (排除自身)
#     → 捕获的是 "情感溢出" 维度的外生变异 (直接对标论文)
#
#   两者从不同角度提供了外生变异, 可同时作为 IV 进行 overid test。
#
# 参考文献:
#   [1] Luo, Q. & Li, H. (2025). "Media sentiment and corporate R&D
#       manipulation." Finance Research Letters, 81, 107505. Table 3.
# ============================================================================

# 地理列 → 输出变量名前缀的缩写映射
# 避免 geo_col.replace("bank_","") 生成 "province_leave1out_tone_full" (28字符)
# 而 Stata 模板和 LABELS 使用 "prov_leave1out_tone_full" (25字符) 的不一致
_GEO_SHORT = {'bank_province': 'prov', 'bank_city': 'city'}

def compute_leave_one_out_sentiment(panel: pd.DataFrame) -> pd.DataFrame:
    """步骤 7d: 构建 Leave-one-out 地理平均情感工具变量。

    对于面板中每个 Bank-Year 观测 (i, t), 计算同省/同城市内
    排除银行 i 后其余银行的年度平均情感得分:

      leave1out_{i,t} = (Σ_{j≠i, j∈G} tone_{j,t}) / (N_{G,t} - 1)

    其中 G 是银行 i 所在的省份或城市, N_{G,t} 是该年度 G 内
    有有效情感得分 (非 NaN) 的银行数量。

    计算使用向量化 leave-one-out 公式 (O(N) 复杂度):
      group_sum = Σ tone_j (组内所有银行含自身)
      group_cnt = N (组内有效银行数)
      leave1out_i = (group_sum - tone_i) / (group_cnt - 1)

    边界情况处理:
      - 某省/城市某年仅 1 家银行有情感数据 → leave-one-out 为 NaN
        (无法从自身推断同地区媒体生态, 这是方法论上正确的处理)
      - 银行无新闻报道 (tone = NaN) → 不参与分组计算且自身结果为 NaN
      - 银行无地理标识 (bank_province = '') → 不参与计算

    依赖:
      须在 merge_bank_geography() (步骤 7c) 之后调用,
      因为需要 bank_province 和 bank_city 列。
      须在 balance_panel() (步骤 6) 之后调用,
      因为 leave-one-out 公式假设每家银行在 (geo, year) 内
      仅出现一次 (balance_panel 保证 target_bank×year 唯一)。

    新增列 (双层 × 双轨道 = 4 个变量):
      prov_leave1out_tone_full — 省级 leave-one-out, Full 轨道
      prov_leave1out_tone_ctx  — 省级 leave-one-out, Ctx 轨道
      city_leave1out_tone_full — 城市级 leave-one-out, Full 轨道
      city_leave1out_tone_ctx  — 城市级 leave-one-out, Ctx 轨道

    变量命名:
      使用 _GEO_SHORT 映射确保缩写一致:
        bank_province → 'prov', bank_city → 'city'
      避免 .replace("bank_","") 生成过长的 "province_" 前缀

    Stata 用途:
      ivreghdfe Y (llm_vote_tone_full = prov_leave1out_tone_full) X,
        absorb(target_bank year) cluster(target_bank)

    Args:
        panel: Bank-Year 面板, 须含 bank_province, bank_city,
               llm_vote_tone_full, llm_vote_tone_ctx, year 列。

    Returns:
        panel: 附加 4 个 leave-one-out 列的 DataFrame。
    """
    logger.info("=" * 60)
    logger.info("步骤 7d: Leave-one-out 地理平均情感 (Luo & Li 2025)")
    logger.info("=" * 60)
    logger.info("  对标: Province_news_sentiment (Table 3)")
    logger.info("  公式: leave1out_i = (Σ tone_j - tone_i) / (N - 1), j ≠ i")

    for geo_col, geo_label in [('bank_province', '省级'),
                                ('bank_city', '城市级')]:
        # 检查地理列是否可用 (非空)
        if geo_col not in panel.columns or (panel[geo_col] == '').all():
            logger.warning(f"  {geo_col} 不可用, 跳过 {geo_label}")
            continue

        for track in ['_full', '_ctx']:
            tone_col = f'llm_vote_tone{track}'
            # 使用 _GEO_SHORT 缩写映射, 确保变量名与 Stata 模板一致
            # bank_province → prov_leave1out_tone_full (25字符)
            # bank_city     → city_leave1out_tone_full (24字符)
            out_col = f'{_GEO_SHORT[geo_col]}_leave1out_tone{track}'

            if tone_col not in panel.columns:
                continue

            # ── 筛选有效子集 ──
            # 条件 1: 有地理标识 (排除未匹配银行)
            # 条件 2: 有情感得分 (排除零新闻观测)
            mask = (panel[geo_col] != '') & panel[tone_col].notna()
            subset = panel.loc[mask]

            # ── 向量化 Leave-one-out 计算 ──
            # transform('sum'/'count') 在 groupby 后广播回原索引,
            # 每行获得其所属组 (省/城市 × 年度) 的组内总和和计数
            grp_sum = subset.groupby(
                [geo_col, 'year']
            )[tone_col].transform('sum')
            grp_cnt = subset.groupby(
                [geo_col, 'year']
            )[tone_col].transform('count')

            # ── 赋值 (仅对组内 ≥ 2 家银行的观测) ──
            # grp_cnt == 1: 某省/城市某年仅此一家银行有数据,
            #   leave-one-out 分母为 0, 赋 NaN (方法论正确)
            panel[out_col] = np.nan
            valid_idx = subset.index[grp_cnt > 1]
            panel.loc[valid_idx, out_col] = (
                (grp_sum.loc[valid_idx]
                 - subset.loc[valid_idx, tone_col])
                / (grp_cnt.loc[valid_idx] - 1)
            )

            # ── 诊断日志 ──
            n_valid = panel[out_col].notna().sum()
            n_singleton = mask.sum() - len(valid_idx)
            logger.info(f"  {out_col}: "
                        f"有效={n_valid}, "
                        f"单一银行组={n_singleton}")

    return panel

