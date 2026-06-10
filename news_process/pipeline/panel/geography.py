"""
43_panel_indicators_geography.py — 综合指标、标准化与地理信息
==========================================================

功能:
  - 综合情感指标计算 (compute_composite_indicators)
  - Fama-MacBeth 年度截面标准化 (standardize_panel_variables)
  - 银行地理信息合并 (merge_bank_geography)
  - Leave-One-Out 省/市情感 IV (compute_leave_one_out_sentiment)
  - 四梯度地理距离缓冲 (compute_geo_proximity_buffers)
    → 50/100/150/200 km 下的 28 个媒体接近度指标
    → Gurun & Butler (2012, JF); Engelberg & Parsons (2011, JF)
  - 六层区域 AI 模仿渗透率 (compute_regional_imitation_pressure)
    → 省/市/50/100/150/200 km LOO 同行模仿压力
    → Leary & Roberts (2014, JF); Dahlke et al. (2024, RP)

拆分自: 40_build_panel.py (L1638-2181)
学术依据: Fama & MacBeth (1973, JPE); Luo & Li (2025);
          Coval & Moskowitz (1999, JF)
"""

import json
import math
import os
import re

import numpy as np
import pandas as pd

# Phase 2a: 取代旧的 importlib.spec_from_file_location 反射,改为正规子包 import。
from news_process.pipeline.panel.encode import (
    BERT_MODELS,
    CONFIG,
    DICT_NAMES,
    LLM_MODELS,
    THREE_CLASS_MODELS,
    logger,
)

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

    # 使用字典收集所有新列, 避免逐列原地赋值导致 DataFrame 碎片化
    # (PerformanceWarning: DataFrame is highly fragmented)
    new_cols = {}

    # --- LLM 逐模型综合 ---
    for track in ['_full', '_ctx']:
        new_cols[f'llm_models_avg_tone{track}'] = _safe_mean([f'{s}_tone{track}' for s in LLM_MODELS])
        new_cols[f'llm_models_avg_tone_sum{track}'] = _safe_mean([f'{s}_tone_sum{track}' for s in LLM_MODELS])
        new_cols[f'llm_models_avg_cont{track}'] = _safe_mean([f'{s}_cont_mean{track}' for s in LLM_MODELS])
        new_cols[f'llm_models_avg_cont_sum{track}'] = _safe_mean([f'{s}_cont_sum{track}' for s in LLM_MODELS])
        new_cols[f'llm_models_avg_tone_std{track}'] = _safe_mean([f'{s}_tone_std{track}' for s in LLM_MODELS])

        # --- 词典法综合 ---
        new_cols[f'dict_avg_tone{track}'] = _safe_mean([f'{d}_tone{track}' for d in DICT_NAMES])
        new_cols[f'dict_avg_tone_sum{track}'] = _safe_mean([f'{d}_tone_sum{track}' for d in DICT_NAMES])
        new_cols[f'dict_avg_tone_std{track}'] = _safe_mean([f'{d}_tone_std{track}' for d in DICT_NAMES])

        # --- 词典法 IDF 综合 (Gentzkow, Kelly & Taddy 2019, JEL) ---
        new_cols[f'dict_avg_idf_tone{track}'] = _safe_mean([f'{d}_idf_tone{track}' for d in DICT_NAMES])
        new_cols[f'dict_avg_idf_tone_sum{track}'] = _safe_mean([f'{d}_idf_tone_sum{track}' for d in DICT_NAMES])

        # --- BERT 综合 ---
        new_cols[f'bert_avg_pos{track}'] = _safe_mean([f'{b}_pos{track}' for b in BERT_MODELS])
        new_cols[f'bert_avg_neg{track}'] = _safe_mean([f'{b}_neg{track}' for b in BERT_MODELS])
        new_cols[f'bert_avg_neu{track}'] = _safe_mean([f'{b}_neu{track}' for b in BERT_MODELS if b in THREE_CLASS_MODELS])
        new_cols[f'bert_avg_pos_sum{track}'] = _safe_mean([f'{b}_pos_sum{track}' for b in BERT_MODELS])
        new_cols[f'bert_avg_neg_sum{track}'] = _safe_mean([f'{b}_neg_sum{track}' for b in BERT_MODELS])
        new_cols[f'bert_avg_neu_sum{track}'] = _safe_mean([f'{b}_neu_sum{track}' for b in BERT_MODELS if b in THREE_CLASS_MODELS])
        new_cols[f'bert_avg_pos_std{track}'] = _safe_mean([f'{b}_pos_std{track}' for b in BERT_MODELS])

        # --- VW 综合指标 ---
        new_cols[f'llm_models_avg_tone_vw{track}'] = _safe_mean([f'{s}_tone_vw{track}' for s in LLM_MODELS])
        new_cols[f'dict_avg_tone_vw{track}'] = _safe_mean([f'{d}_tone_vw{track}' for d in DICT_NAMES])
        new_cols[f'dict_avg_idf_tone_vw{track}'] = _safe_mean([f'{d}_idf_tone_vw{track}' for d in DICT_NAMES])
        new_cols[f'bert_avg_pos_vw{track}'] = _safe_mean([f'{b}_pos_vw{track}' for b in BERT_MODELS])
        new_cols[f'bert_avg_neg_vw{track}'] = _safe_mean([f'{b}_neg_vw{track}' for b in BERT_MODELS])

        # --- MW 综合指标 (Holzman et al. 2023, TAR) ---
        new_cols[f'llm_models_avg_tone_mw{track}'] = _safe_mean([f'{s}_tone_mw{track}' for s in LLM_MODELS])
        new_cols[f'dict_avg_tone_mw{track}'] = _safe_mean([f'{d}_tone_mw{track}' for d in DICT_NAMES])
        new_cols[f'dict_avg_idf_tone_mw{track}'] = _safe_mean([f'{d}_idf_tone_mw{track}' for d in DICT_NAMES])
        new_cols[f'bert_avg_pos_mw{track}'] = _safe_mean([f'{b}_pos_mw{track}' for b in BERT_MODELS])
        new_cols[f'bert_avg_neg_mw{track}'] = _safe_mean([f'{b}_neg_mw{track}' for b in BERT_MODELS])

        # --- HW 综合指标 (Tetlock 2011, RFS) ---
        new_cols[f'llm_models_avg_tone_hw{track}'] = _safe_mean([f'{s}_tone_hw{track}' for s in LLM_MODELS])
        new_cols[f'dict_avg_tone_hw{track}'] = _safe_mean([f'{d}_tone_hw{track}' for d in DICT_NAMES])
        new_cols[f'dict_avg_idf_tone_hw{track}'] = _safe_mean([f'{d}_idf_tone_hw{track}' for d in DICT_NAMES])
        new_cols[f'bert_avg_pos_hw{track}'] = _safe_mean([f'{b}_pos_hw{track}' for b in BERT_MODELS])
        new_cols[f'bert_avg_neg_hw{track}'] = _safe_mean([f'{b}_neg_hw{track}' for b in BERT_MODELS])

    logger.info(f"  生成双轨综合指标完成")

    # --- 文章平均长度 ---
    # (a) 字符口径: avg_article_length = ln(1 + bank-year 平均【字符数】).
    #     ⚠ 2026-06-05 引文/单位勘误: 底层 doc_length = len(str(内容)) = Unicode 字符数
    #     (news_bank.py:230), 非 jieba 词数。原注"MLENGTH=ln(文章词数)/avg_words"系单位
    #     误标 (字符≈词数×1.5-1.7)。中文场景字符数是 defensible 长度代理, 但口径是【字符】。
    #     He et al. 2024 IRFA 的 MLENGTH 本是词数定义, 真词口径见下方 (b) ln_word_count。
    if 'avg_doc_length' in panel.columns:
        new_cols['avg_article_length'] = np.log1p(panel['avg_doc_length'])  # ln(1+平均字符数)
        logger.info(f"  avg_article_length (ln(1+平均字符数), 字符口径) 已生成")

    # (b) 词口径: ln_word_count = ln(1 + bank-year 平均【jieba 词数】) — 真 MLENGTH 词口径
    #     (Li 2008 JAE; He et al. 2024 IRFA). 2026-06-05 新增 (批 #7), 与 (a) 字符口径
    #     互为长度稳健 (双轨纪律)。源列 avg_word_count_{full,ctx} 来自 encode H2 段。
    for _track in ('_full', '_ctx'):
        _wc = f'avg_word_count{_track}'
        if _wc in panel.columns:
            new_cols[f'ln_word_count{_track}'] = np.log1p(panel[_wc])
    if 'avg_word_count_full' in panel.columns:
        logger.info(f"  ln_word_count_{{full,ctx}} (ln(1+平均词数), 词口径 MLENGTH) 已生成")

    # --- 分类维度综合指标 ---
    for suffix in ['_tech', '_app']:
        # 仅当分类计数列存在时生成
        if f'n_articles{suffix}' not in panel.columns:
            continue

        for track in ['_full', '_ctx']:
            # LLM 逐模型综合
            new_cols[f'llm_models_avg_tone{suffix}{track}'] = _safe_mean(
                [f'{s}_tone{suffix}{track}' for s in LLM_MODELS])
            new_cols[f'llm_models_avg_cont{suffix}{track}'] = _safe_mean(
                [f'{s}_cont_mean{suffix}{track}' for s in LLM_MODELS])

            # 词典法综合
            new_cols[f'dict_avg_tone{suffix}{track}'] = _safe_mean(
                [f'{d}_tone{suffix}{track}' for d in DICT_NAMES])

            # 词典法 IDF 综合
            new_cols[f'dict_avg_idf_tone{suffix}{track}'] = _safe_mean(
                [f'{d}_idf_tone{suffix}{track}' for d in DICT_NAMES])

            # BERT 综合
            new_cols[f'bert_avg_pos{suffix}{track}'] = _safe_mean(
                [f'{b}_pos{suffix}{track}' for b in BERT_MODELS])
            new_cols[f'bert_avg_neg{suffix}{track}'] = _safe_mean(
                [f'{b}_neg{suffix}{track}' for b in BERT_MODELS])
            new_cols[f'bert_avg_neu{suffix}{track}'] = _safe_mean(
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
            new_cols[f'fintech_exposure{track}'] = coverage * panel[std_col]
            valid = new_cols[f'fintech_exposure{track}'].dropna()
            logger.info(f"  fintech_exposure{track}: "
                        f"mean={valid.mean():.4f}, "
                        f"std={valid.std():.4f}, "
                        f"非空={len(valid):,}")
        else:
            new_cols[f'fintech_exposure{track}'] = pd.Series(np.nan, index=panel.index)
            logger.warning(f"  fintech_exposure{track}: "
                          f"缺少 {std_col} 或 ln_news_coverage, 填 NaN")

    # ── 一次性合并所有新列, 消除 DataFrame 碎片化 ──
    overlap = [c for c in new_cols if c in panel.columns]
    if overlap:
        panel = panel.drop(columns=overlap)
    panel = pd.concat(
        [panel, pd.DataFrame(new_cols, index=panel.index)], axis=1
    )
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
    # HW 加权 (Tetlock 2011)
    'llm_vote_tone_hw_{t}', 'dict_avg_tone_hw_{t}',
    # MSENT (He et al. 2024)
    'avg_msent_{t}',
    # Fintech Exposure (Dim et al. 2024 概念迁移)
    'fintech_exposure_{t}',
    # LLM 置信度 Z-score (信号清晰度调节)
    # 学术依据:
    #   Shapiro, A.H., Sudhof, M. & Wilson, D.J. (2022). Measuring news
    #   sentiment. Journal of Econometrics, 228(2), 221-243.
    #   https://doi.org/10.1016/j.jeconom.2020.07.053
    #   → §4: 情感测量噪声导致回归系数衰减偏误(attenuation bias)
    #   → 置信度越低 → 测量误差越大 → Tone 系数向零衰减
    'avg_llm_conf_{t}',
]
# 无双轨的标量变量
_STANDARDIZE_SCALAR = [
    'ln_news_coverage', 'media_breadth',
    'avg_article_length',
]


def _expand_track_templates(templates: list) -> list:
    """将含 {t} 占位符的模板展开为 _full、_ctx 双轨变量名 (remove-title-track)。"""
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
    # 使用字典收集所有 _z 列, 避免逐列原地赋值导致 DataFrame 碎片化
    has_news = panel['n_articles'] > 0
    z_count = 0
    new_cols = {}

    # nullable dtype 加固 (metric-audit 2026-06-02): pandas 3.0 下, 把 nullable
    # Float64/Int64 (ExtensionArray) 的算术结果赋值进 numpy float64 Series 会触发
    # LossySetitemError (旧 pandas silent up-cast). 下方逐列先 to_numeric→float64
    # 归一, 既消除崩溃又使 z-score 对上游列 dtype-agnostic (NA→NaN, 零新闻行仍 NaN).
    _nullable = [c for c in valid_cols
                 if pd.api.types.is_extension_array_dtype(panel[c])]
    if _nullable:
        logger.info(f"    nullable(ExtensionArray) 白名单列 (已 float64 归一): {_nullable}")

    for col in valid_cols:
        z_col = f'{col}_z'
        z_series = pd.Series(np.nan, index=panel.index)
        # nullable→numpy float64 归一, 使后续算术与 .loc 赋值在统一 dtype 下进行
        col_numeric = pd.to_numeric(panel[col], errors='coerce').astype('float64')

        for year, grp in panel[has_news].groupby('year'):
            vals = col_numeric.loc[grp.index].dropna()
            if len(vals) < 3:
                continue
            mu = vals.mean()
            sigma = vals.std()
            if sigma < 1e-10:
                continue
            idx = grp.index
            z_series.loc[idx] = (col_numeric.loc[idx] - mu) / sigma

        new_cols[z_col] = z_series
        z_count += 1

    # ── 一次性合并所有 _z 列 ──
    overlap = [c for c in new_cols if c in panel.columns]
    if overlap:
        panel = panel.drop(columns=overlap)
    panel = pd.concat(
        [panel, pd.DataFrame(new_cols, index=panel.index)], axis=1
    )

    logger.info(f"  已生成 {z_count} 个 _z 标准化列")

    # ── 校验: 标准化后年内 std ≈ 1 ──
    sample_z_cols = [c for c in panel.columns if c.endswith('_z')][:5]
    for col in sample_z_cols:
        within_std = (panel[has_news].dropna(subset=[col])
                      .groupby('year')[col].std())
        mean_std = within_std.mean()
        if pd.notna(mean_std):
            ok = '✓' if abs(mean_std - 1.0) < 0.1 else '需关注'
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

      注意: Cameron & Miller (2015, JHR) 指出: 聚类数 < 50 时,
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
                f"{'< 50, 建议补充 wild cluster bootstrap' if n_prov < 50 else '✓ ≥ 50'}")
    logger.info(f"  城市聚类数: {n_city} "
                f"{'< 50' if n_city < 50 else '✓ ≥ 50'}")

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
#     - 城市级: 329 个城市, IV 变异更精细
#
#   ⚠ 弱工具变量警告 (实测, T=2 当前面板): 两级 LOO-IV 的一阶段 F
#     统计量均极弱, 远低于 10 的弱工具阈值 (Staiger-Stock 1997):
#       省级 (prov)  F ≈ 0.25
#       城市级 (city) F ≈ 0.037   ← 城市级反而 *更弱*, 非"通常更高"
#     根因: T=2 面板深度 + 地理稀疏 (每个 (geo, year) 单元内有效银行
#     数极少, leave-one-out 后变异几乎枯竭) → 工具相关性接近于零。
#     因此这两个 LOO-IV **不得**作为强因果识别的主 IV 使用; 仅可
#     作为 falsification / 稳健性展示。production run (spec 声明 T=18)
#     下地理单元年度内银行数增加, 工具强度才可能改善, 需届时重测。
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
    logger.info("步骤 7d: Leave-one-out 地理平均情感 (Luo & Li 2025; Manski 1993; Bramoullé 2009)")
    logger.info("=" * 60)
    logger.info("  [文献支撑 1]: Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies. https://doi.org/10.2307/2298123")
    logger.info("  [文献支撑 2]: Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics. https://doi.org/10.1016/j.jeconom.2008.12.021")
    logger.info("  对标: Province_news_sentiment (Table 3)")
    logger.info("  公式: leave1out_i = (Σ tone_j - tone_i) / (N - 1), j ≠ i")

    # 使用字典收集所有新列, 避免逐列原地赋值导致 DataFrame 碎片化
    new_cols = {}

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
            out_series = pd.Series(np.nan, index=panel.index)
            valid_idx = subset.index[grp_cnt > 1]
            
            # [白盒安全加固] 强校验：绝不信任外部 groupby 广播的返回，确保参与计算的值无任何空值或负分母
            if len(valid_idx) > 0:
                assert subset.loc[valid_idx, tone_col].notna().all(), "LOO IV 计算前置校验失败: 存在空值情感分数"
                assert grp_cnt.loc[valid_idx].notna().all(), "LOO IV 计算前置校验失败: 组频数存在 NaN"
                assert (grp_cnt.loc[valid_idx] - 1 > 0).all(), "LOO IV 分母出现非法非正值！"
                
            out_series.loc[valid_idx] = (
                (grp_sum.loc[valid_idx]
                 - subset.loc[valid_idx, tone_col])
                / (grp_cnt.loc[valid_idx] - 1)
            )
            new_cols[out_col] = out_series

            # ── 诊断日志 ──
            n_valid = out_series.notna().sum()
            n_singleton = mask.sum() - len(valid_idx)
            logger.info(f"  {out_col}: "
                        f"有效={n_valid}, "
                        f"单一银行组={n_singleton}")

    # ── G-08: 多情感度量 LOO IV 扩展 ──
    # 学术依据: 过度识别检验 (Hansen J test) 要求至少 2 个独立 IV。
    #   若 llm_vote_tone, dict_avg_tone, bert_avg_pos 的 LOO IV 均可用,
    #   则可在 Stata 中执行 overid 检验。
    # 参考: Luo & Li (2025, FRL, Table 3), Goldsmith-Pinkham (2020, AER, §4)
    logger.info("  ── G-08: 多情感度量 LOO IV 扩展 ──")
    extra_tone_cols = {
        'dict_avg_tone': '词典法综合',
        'bert_avg_pos': 'BERT正面概率',
    }
    for base_col, desc in extra_tone_cols.items():
        for geo_col, geo_label in [('bank_province', '省级'),
                                    ('bank_city', '城市级')]:
            if geo_col not in panel.columns or (panel[geo_col] == '').all():
                continue
            for track in ['_full', '_ctx']:
                tone_col = f'{base_col}{track}'
                out_col = f'{_GEO_SHORT[geo_col]}_leave1out_{base_col}{track}'

                if tone_col not in panel.columns:
                    continue

                mask = (panel[geo_col] != '') & panel[tone_col].notna()
                subset = panel.loc[mask]
                if len(subset) < 5:
                    continue

                grp_sum = subset.groupby(
                    [geo_col, 'year']
                )[tone_col].transform('sum')
                grp_cnt = subset.groupby(
                    [geo_col, 'year']
                )[tone_col].transform('count')

                out_series = pd.Series(np.nan, index=panel.index)
                valid_idx = subset.index[grp_cnt > 1]
                out_series.loc[valid_idx] = (
                    (grp_sum.loc[valid_idx]
                     - subset.loc[valid_idx, tone_col])
                    / (grp_cnt.loc[valid_idx] - 1)
                )
                new_cols[out_col] = out_series

                n_valid = out_series.notna().sum()
                logger.info(f"    {out_col} ({desc}): 有效={n_valid}")

    # 输出 Stata over-identification 检验命令
    logger.info("  ── G-08: Stata 过度识别检验命令 ──")
    logger.info("    * ivreghdfe Y (llm_vote_tone_full = "
                "prov_leave1out_tone_full "
                "prov_leave1out_dict_avg_tone_full "
                "prov_leave1out_bert_avg_pos_full), "
                "absorb(target_bank year) cluster(target_bank)")
    logger.info("    * estat overid  // Hansen J test")

    # ── 一次性合并所有 leave-one-out 列 ──
    overlap = [c for c in new_cols if c in panel.columns]
    if overlap:
        panel = panel.drop(columns=overlap)
    panel = pd.concat(
        [panel, pd.DataFrame(new_cols, index=panel.index)], axis=1
    )

    return panel


# ============================================================================
# 11. Haversine 距离公式
# ============================================================================

_GEO_SUFFIXES_DIST = re.compile(
    r'省|市|维吾尔自治区|回族自治区|壮族自治区|自治区|特别行政区|地区|林区'
)

_DISTANCE_THRESHOLDS_KM = [50, 100, 150, 200]


def _clean_geo_name(name: str) -> str:
    """移除行政区划后缀, 标准化城市/省份名称。"""
    return _GEO_SUFFIXES_DIST.sub('', str(name)).strip()


def _haversine(lat1: float, lon1: float,
               lat2: float, lon2: float) -> float:
    """Haversine 公式计算两点间球面距离 (km)。

    学术依据:
      Coval, J. D., & Moskowitz, T. J. (1999). Home bias at home:
      Local equity preference in domestic portfolios. The Journal of
      Finance, 54(6), 2045-2073. DOI: 10.1111/0022-1082.00181
      → 使用多距离阈值方法论需要精确距离计算

    Args:
        lat1, lon1: 点 A 的纬度/经度 (度)
        lat2, lon2: 点 B 的纬度/经度 (度)

    Returns:
        距离 (km)
    """
    R = 6371.0  # 地球半径 (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ============================================================================
# 12. 四梯度地理距离缓冲
# ============================================================================

def compute_geo_proximity_buffers(
    df_exploded: pd.DataFrame,
    panel: pd.DataFrame
) -> pd.DataFrame:
    """计算多梯度地理距离缓冲下的媒体接近度指标。

    对 50/100/150/200 km 四个阈值, 分别计算 10 个变量, 共 40 个
    (2026-06-08 dual-track parity: 情感三项补 _ctx 孪生, 28→40):
      - prox_{d}km_n_media:    距离圈内的媒体来源数 (track-agnostic 单轨)
      - prox_{d}km_n_articles: 距离圈内的文章数 (track-agnostic 单轨)
      - prox_{d}km_frac:       距离圈内文章占比 (track-agnostic 单轨)
      - prox_{d}km_is_local:   是否存在距离圈内媒体 (0/1, track-agnostic 单轨)
      - prox_{d}km_tone_full / _ctx:   距离圈内文章的平均情感 (双轨)
      - prox_{d}km_pos_frac / _ctx:    距离圈内正面文章比例 (双轨; full 沿用无后缀历史名)
      - prox_{d}km_neg_frac / _ctx:    距离圈内负面文章比例 (双轨; full 沿用无后缀历史名)

    学术依据:
      Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype:
      Local media slant, local advertising, and firm value. The Journal
      of Finance, 67(2), 561-598. DOI: 10.1111/j.1540-6261.2012.01725.x
      → 本地媒体对本地公司有正面偏差

      Engelberg, J. E., & Parsons, C. A. (2011). The causal impact of
      media in financial markets. The Journal of Finance, 66(1), 67-97.
      DOI: 10.1111/j.1540-6261.2010.01626.x
      → 多距离梯度方法论

    Args:
        df_exploded: 篇章级 DataFrame
        panel: Bank-Year 面板

    Returns:
        panel: 追加 28 个距离缓冲变量
    """
    logger.info("=" * 60)
    logger.info("步骤: 四梯度地理距离缓冲 "
                "(Gurun & Butler 2012; Engelberg & Parsons 2011)")
    logger.info("=" * 60)

    # ── 加载坐标数据 (Phase 2a: 通过 CONFIG['paths'][...] 解析) ──
    coord_path = CONFIG['paths'].get('city_coordinates_file')
    capital_path = CONFIG['paths'].get('province_capital_map_file')
    bank_addr_path = CONFIG['paths'].get('bank_addresses_file')

    if not coord_path or not os.path.exists(coord_path):
        logger.warning(f"  {coord_path} 不存在, 跳过距离缓冲。"
                       " 请先运行: python scripts/build_city_coordinates.py")
        return panel

    with open(coord_path, 'r', encoding='utf-8') as f:
        city_coords = json.load(f)

    clean_to_raw = {}
    for raw_name in city_coords:
        clean_to_raw[_clean_geo_name(raw_name)] = raw_name

    province_capital = {}
    if os.path.exists(capital_path):
        with open(capital_path, 'r', encoding='utf-8') as f:
            province_capital = json.load(f)

    bank_city_map = {}
    if os.path.exists(bank_addr_path):
        with open(bank_addr_path, 'r', encoding='utf-8') as f:
            bank_addr = json.load(f)
        for bank, info in bank_addr.items():
            c = info.get('city', '').strip()
            if c:
                bank_city_map[bank] = c

    logger.info(f"  坐标数据: {len(city_coords)} 城市, "
                f"{len(province_capital)} 省会映射, "
                f"{len(bank_city_map)} 银行地址")

    # ── 城市坐标查找辅助函数 (三级退化: 精确→清洗→省会) ──
    def _lookup_coords(city_name, province_name=None):
        """三级查找: 精确匹配 → 清洗后匹配 → 省会退化。"""
        if city_name is not None and not pd.isna(city_name):
            cn = str(city_name).strip()
            # Level 1: 精确
            if cn in city_coords:
                c = city_coords[cn]
                return c['lat'], c['lon']
            # Level 2: 清洗
            clean = _clean_geo_name(cn)
            if clean in clean_to_raw:
                c = city_coords[clean_to_raw[clean]]
                return c['lat'], c['lon']
        # Level 3: 省会退化
        if province_name is not None and not pd.isna(province_name):
            prov_clean = _clean_geo_name(str(province_name).strip())
            capital = province_capital.get(prov_clean)
            if capital and capital in clean_to_raw:
                c = city_coords[clean_to_raw[capital]]
                return c['lat'], c['lon']
        return None, None

    # ── 媒体地理列发现 ──
    media_city_col = '城市' if '城市' in df_exploded.columns else None
    media_prov_col = None
    for candidate in ['国家地区/省份', '省份']:
        if candidate in df_exploded.columns:
            media_prov_col = candidate
            break

    if media_city_col is None and media_prov_col is None:
        logger.warning("  无媒体地理信息列 ('城市'/'省份'), 跳过距离缓冲")
        return panel

    logger.info(f"  媒体地理列: city={media_city_col}, prov={media_prov_col}")

    # ── 逐 bank-year 计算 ──
    buf_results = {}  # {(bank, year): {col_name: value}}

    for year in sorted(panel['year'].unique()):
        df_year = df_exploded[df_exploded['year'] == year]
        if df_year.empty:
            continue

        for bank in df_year['target_bank'].unique():
            bank_city = bank_city_map.get(bank)
            b_lat, b_lon = _lookup_coords(bank_city)
            if b_lat is None:
                continue

            df_bank = df_year[df_year['target_bank'] == bank]
            n_total = len(df_bank)
            if n_total == 0:
                continue

            # 计算每篇文章与银行的距离
            distances = []
            for _, row in df_bank.iterrows():
                m_city = row.get(media_city_col) if media_city_col else None
                m_prov = row.get(media_prov_col) if media_prov_col else None
                m_lat, m_lon = _lookup_coords(m_city, m_prov)
                if m_lat is not None:
                    distances.append(_haversine(b_lat, b_lon, m_lat, m_lon))
                else:
                    distances.append(np.nan)

            df_bank = df_bank.copy()
            df_bank['_dist_km'] = distances
            # fix(prox-frac-denominator, metric-audit 2026-06-10): prox_frac 分子(圈内)只含
            # 可定位文章, 分母应同口径取**可定位文章数**而非全部 n_total(含媒体无法地理编码
            # 的文章), 否则地理覆盖度被未定位文章稀释(valid-vs-physical 域不匹配, P3)。
            n_geocoded = int(df_bank['_dist_km'].notna().sum())

            key = (bank, year)
            buf_results[key] = {}

            for threshold in _DISTANCE_THRESHOLDS_KM:
                prefix = f'prox_{threshold}km'
                within = df_bank[df_bank['_dist_km'] <= threshold]
                n_within = len(within)

                buf_results[key][f'{prefix}_n_articles'] = n_within
                buf_results[key][f'{prefix}_frac'] = (
                    n_within / n_geocoded if n_geocoded > 0 else np.nan)
                buf_results[key][f'{prefix}_is_local'] = (
                    1 if n_within > 0 else 0)

                # 媒体来源数
                if '媒体(中文)' in within.columns:
                    buf_results[key][f'{prefix}_n_media'] = (
                        within['媒体(中文)'].nunique())
                else:
                    buf_results[key][f'{prefix}_n_media'] = 0

                # 情感聚合 (LLM 投票分数) — dual-track parity (2026-06-08):
                # 此前仅聚合 _full 文章列 (硬编码 llm_vote_score_full / is_positive_full /
                # is_negative_full), 无 _ctx 孪生; 而同模块 LOO-IV (compute_*_leave_one_out)
                # 已 `for track in ['_full','_ctx']` 双轨。此处复用该双轨惯用法补 _ctx 孪生。
                # 命名: 保留既有列名作 full 轨 (tone 既有 _full 后缀; pos_frac/neg_frac 既有
                # 无后缀=隐式 full, 沿用项目 _lc/_sc 对角线"隐式 full + 显式 ctx"约定 → 零
                # 重命名、不破坏下游 Stata 模板/golden), ctx 轨统一加 _ctx 后缀。
                for _track, _pn_suffix in (('_full', ''), ('_ctx', '_ctx')):
                    _tone_col = f'llm_vote_score{_track}'
                    if _tone_col in within.columns and n_within > 0:
                        buf_results[key][f'{prefix}_tone{_track}'] = (
                            within[_tone_col].mean())
                    else:
                        buf_results[key][f'{prefix}_tone{_track}'] = np.nan

                    _pos_col = f'is_positive{_track}'
                    if _pos_col in within.columns and n_within > 0:
                        buf_results[key][f'{prefix}_pos_frac{_pn_suffix}'] = (
                            within[_pos_col].mean())
                    else:
                        buf_results[key][f'{prefix}_pos_frac{_pn_suffix}'] = np.nan

                    _neg_col = f'is_negative{_track}'
                    if _neg_col in within.columns and n_within > 0:
                        buf_results[key][f'{prefix}_neg_frac{_pn_suffix}'] = (
                            within[_neg_col].mean())
                    else:
                        buf_results[key][f'{prefix}_neg_frac{_pn_suffix}'] = np.nan

    # ── 合并至面板 ──
    if buf_results:
        buf_rows = []
        for (bank, year), vals in buf_results.items():
            row = {'target_bank': bank, 'year': year}
            row.update(vals)
            buf_rows.append(row)
        buf_df = pd.DataFrame(buf_rows)
        panel = panel.merge(buf_df, on=['target_bank', 'year'], how='left')

        # ── 拓扑断言: prox_50km ≤ prox_100km ≤ prox_150km ≤ prox_200km ──
        for col_type in ['_n_articles', '_frac']:
            prev_col = None
            for threshold in _DISTANCE_THRESHOLDS_KM:
                col = f'prox_{threshold}km{col_type}'
                if col in panel.columns and prev_col is not None:
                    violations = panel[
                        panel[col].notna() & panel[prev_col].notna() &
                        (panel[col] < panel[prev_col] - 1e-10)
                    ]
                    if len(violations) > 0:
                        logger.warning(
                            f"  拓扑违规: {prev_col} > {col} "
                            f"({len(violations)} 行)")
                prev_col = col

        n_vars = len([c for c in buf_df.columns if c.startswith('prox_')])
        logger.info(f"  距离缓冲已合并: {len(buf_df):,} 个 Bank-Year, "
                    f"{n_vars} 个变量")
    else:
        logger.warning("  未生成任何距离缓冲变量")

    return panel


# ============================================================================
# 13. 区域 AI 模仿渗透率 (六层 LOO)
# ============================================================================

def compute_regional_imitation_pressure(
    panel: pd.DataFrame
) -> pd.DataFrame:
    """计算六层区域 AI 模仿渗透率 (Leave-One-Out)。

    六层:
      1. ai_reg_province: 同省 LOO
      2. ai_reg_city: 同城 LOO
      3-6. ai_reg_50km/100km/150km/200km: 距离圈 LOO

    指标定义:
      ai_reg_X_i,t = mean_{j!=i, j in Region_X}(has_fintech_news_j,t)
      其中 has_fintech_news = I(n_articles > 0)

    学术依据:
      Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect
      corporate financial policy? The Journal of Finance, 69(1), 139-178.
      https://doi.org/10.1111/jofi.12094
      → 同行模仿效应的操作化

      Dahlke, J., et al. (2024). Epidemic effects in the diffusion
      of emerging digital technologies. Research Policy, 53(2), 104917.
      DOI: 10.1016/j.respol.2023.104917
      → AI 技术扩散传染病模型

    Args:
        panel: Bank-Year 面板

    Returns:
        panel: 追加 6 个 ai_reg_* 变量
    """
    logger.info("=" * 60)
    logger.info("步骤: 区域 AI 模仿渗透率 (六层 LOO, Leary & Roberts 2014)")
    logger.info("=" * 60)

    # 指示变量: 该银行该年是否有 fintech 新闻
    if 'n_articles' not in panel.columns:
        logger.warning("  n_articles 不存在, 跳过区域模仿渗透率")
        return panel

    panel['_has_fintech'] = (panel['n_articles'] > 0).astype(int)

    # ── 省/市级 LOO ──
    for geo_col, var_name in [('bank_province', 'ai_reg_province'),
                               ('bank_city', 'ai_reg_city')]:
        if geo_col not in panel.columns:
            logger.warning(f"  {geo_col} 不存在, 跳过 {var_name}")
            continue

        vals = pd.Series(np.nan, index=panel.index)
        for (region, year), grp in panel.groupby([geo_col, 'year']):
            # fix(regional-phantom-guard, metric-audit 2026-06-10): 地理未匹配银行若填 ''/NaN,
            # groupby 会把它们聚成一个伪区域 ('' , year) 并互算 LOO 同行压力 (Leary-Roberts
            # 2014 要求真实同省/市参照集, 非残差桶)。当前盘上 0 未匹配故不触发(latent), 但
            # 全量新增银行可能触发 → 显式跳过空/缺失区域。
            if region is None or (isinstance(region, float) and pd.isna(region)) or str(region).strip() == '':
                continue
            if len(grp) < 2:
                continue
            total = grp['_has_fintech'].sum()
            for idx in grp.index:
                own = panel.at[idx, '_has_fintech']
                vals.at[idx] = (total - own) / (len(grp) - 1)

        panel[var_name] = vals
        valid = vals.notna().sum()
        logger.info(f"  {var_name}: {valid:,} 有效值, "
                    f"mean={vals.mean():.4f}")

    # ── 距离级 LOO (Phase 2a: 通过 CONFIG['paths'][...] 解析) ──
    coord_path = CONFIG['paths'].get('city_coordinates_file')
    bank_addr_path = CONFIG['paths'].get('bank_addresses_file')

    if not coord_path or not bank_addr_path \
       or not os.path.exists(coord_path) or not os.path.exists(bank_addr_path):
        logger.warning("  坐标/银行地址不存在, 跳过距离级 LOO")
        panel.drop('_has_fintech', axis=1, inplace=True, errors='ignore')
        return panel

    with open(coord_path, 'r', encoding='utf-8') as f:
        city_coords = json.load(f)
    with open(bank_addr_path, 'r', encoding='utf-8') as f:
        bank_addr = json.load(f)

    clean_to_raw_loc = {}
    for raw_name in city_coords:
        clean_to_raw_loc[_clean_geo_name(raw_name)] = raw_name

    # 银行 → 坐标
    bank_coords = {}
    for bank, info in bank_addr.items():
        c = info.get('city', '').strip()
        if c:
            if c in city_coords:
                bank_coords[bank] = (city_coords[c]['lat'],
                                     city_coords[c]['lon'])
            else:
                clean = _clean_geo_name(c)
                if clean in clean_to_raw_loc:
                    cc = city_coords[clean_to_raw_loc[clean]]
                    bank_coords[bank] = (cc['lat'], cc['lon'])

    logger.info(f"  银行坐标匹配: {len(bank_coords)}/{len(bank_addr)}")

    # 逐年计算距离级 LOO
    for threshold in _DISTANCE_THRESHOLDS_KM:
        var_name = f'ai_reg_{threshold}km'
        vals = pd.Series(np.nan, index=panel.index)

        for year in panel['year'].unique():
            mask = panel['year'] == year
            year_panel = panel.loc[mask]

            for idx in year_panel.index:
                bank_i = panel.at[idx, 'target_bank']
                if bank_i not in bank_coords:
                    continue

                lat_i, lon_i = bank_coords[bank_i]
                peers_ft = []

                for idx_j in year_panel.index:
                    if idx_j == idx:
                        continue
                    bank_j = panel.at[idx_j, 'target_bank']
                    if bank_j not in bank_coords:
                        continue

                    lat_j, lon_j = bank_coords[bank_j]
                    dist = _haversine(lat_i, lon_i, lat_j, lon_j)
                    if dist <= threshold:
                        peers_ft.append(panel.at[idx_j, '_has_fintech'])

                if peers_ft:
                    vals.at[idx] = np.mean(peers_ft)

        panel[var_name] = vals
        valid = vals.notna().sum()
        logger.info(f"  {var_name}: {valid:,} 有效值, "
                    f"mean={vals.mean():.4f}")

    # ── 拓扑断言 ──
    for i in range(len(_DISTANCE_THRESHOLDS_KM) - 1):
        t1 = _DISTANCE_THRESHOLDS_KM[i]
        t2 = _DISTANCE_THRESHOLDS_KM[i + 1]
        col1 = f'ai_reg_{t1}km'
        col2 = f'ai_reg_{t2}km'
        if col1 in panel.columns and col2 in panel.columns:
            n1 = panel[col1].notna().sum()
            n2 = panel[col2].notna().sum()
            if n1 > n2:
                logger.warning(
                    f"  拓扑警告: {col1} 有效样本 ({n1}) > {col2} ({n2})")

    panel.drop('_has_fintech', axis=1, inplace=True, errors='ignore')
    return panel

