"""
40_panel_export_main.py — 面板导出与主流程编排 (入口文件)
==========================================================

本文件是整个金融科技新闻研究管线的主入口和编排器。

核心功能:
  1. 面板诊断统计 (log_diagnostics): 输出覆盖率、平衡性、缺失值等
  2. 多格式导出 (export_panel): Parquet + Stata .dta (含学术级标签)
  3. 主流程编排 main(): 41→42→43→44→46→47→45 的执行序列

执行序列 (步骤号对应 main() 中的日志标记):
  Step 1-3: 数据加载、情感编码、面板聚合 (41_panel_encode_aggregate)
  Step 4-5: 金融科技注意力 + 媒体异质性 (42_panel_attention_media)
  Step 6:   复合指标 + 地理缓冲 + AI 模仿 (43_panel_indicators_geography)
  Step 7a-e: Bartik IV + DID + 政策冲击 (44_panel_iv_did)
  Step 7f:  同行网络溢出 (46_network_spillovers)
  Step 7g:  网络中心度 22 指标 (46_network_spillovers)
  Step 7h:  经纪网络 + LOO冲击 + 火灾甩卖 (47_network_brokerage)
  Step 8-9: 诊断统计 + 多格式导出 (40_panel_export_main)

拆分自: 40_build_panel.py (L2187-3142)

运行方式:
  python 40_panel_export_main.py

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 40_panel_export_main.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**输入**: 主读 `24_herd_decay.parquet` (df_exploded, stage 21 语义精筛后 article×bank 级 verified 集; 缺则 sys.exit(1)); 步骤 7h-token 段硬读 `16_article_alignment.parquet` (policy_cosine_sim; 缺则 raise RuntimeError, 非静默 skip); 步骤 6b `compute_fintech_attention_index` 内读 `12_fintech_news_full.parquet` (全量银行新闻, 注意力分母); 步骤 8c `_merge_optin_feature_panels` 条件 merge `26_staleness_panel.parquet` / `75_cross_media_alpha.parquet` (含新鲜度 mtime 守卫 + 重复键 fail-loud)。入口处校验关键列 `target_bank` / `llm_sentiment_full` / `日期` / `llm_agreement_rate_full` (main() 数据加载段, 缺则 sys.exit(1))。

**处理步骤 (runner.main(), 串行子步, StageSpec.name 对应 41→42→43→44→46→47→45)**:
- 步骤2 `encode_sentiment` 篇章级情感数值编码。
- 步骤3 多银行特征 (bank_count/is_multi_bank/in_title); 步骤3b/3c/3d 预计算加权列 — VW(mention_density)/MW(media_authority, +tier 并行列)/HW(herd_weight 三轨独立, 缺则 legacy 单轨退化) × 全测度族, 含 `_build_llm_valid_masked_weights` 的 valid-mask 分母列 (`_wd_*`, 修 encode-01 向零衰减); 步骤3d-2 阈值敏感性 HW (`herd_sensitivity_grid`, 仅施于 LLM 投票主测度)。
- 洗稿率前置: 多方法 (A LLM投票/A2 单LLM/B 反向/D/D2 词典/E/E2 BERT argmax/F 高置信) × 三轨篇章级 `_is_*` 标记 + `_svd_*` subst-valid 分母指示 (+ M2 P3 的 sentiment×subst_ctx `_sc` 4-way)。
- 步骤5 `aggregate_panel` → bank-year panel + `_pool_svd_substvalid_counts` 同域分母聚合; 步骤6 `balance_panel` 笛卡尔积补全 + 6a has_coverage。
- 步骤6b `compute_fintech_attention_index` (比值 ft_attn + 总量 ft_vol, 三级地理, 落 3 parquet); 6b-2 `compute_attention_treatments` (verified 域门控); 6b-3 `compute_dedup_sensitivity_treatments`; 6c `compute_media_heterogeneity`。
- 步骤7 综合指标/7b 截面标准化/7c 地理 merge/7d LOO 情感 IV/7d-geo 地理距离缓冲 (`_m43.compute_geo_proximity_buffers`)/7d-imit 区域模仿渗透 (`compute_regional_imitation_pressure`)。
- 步骤7e Bartik shift-share IV (6 类核心: type/scale/fintech_lf+lc/media/mauth/geoprox; GPSS 2020 pre-treatment 基期 T0=max(year.min,2010), cutoff≤T0 强制 raise; _t0/_t1/_t01 基期敏感性带外生性守卫)。7f 经济圈 LOO (`compute_zone_leave1out`); 7g DID 政策冲击 (`merge_policy_shocks`, DCEP+Sandbox)。
- 步骤7g-het 异质性交互 (Tone×SOE/Scale/HighCov, `_base_year_median_split` pre-period 固定切分, DDD 三重差, stress/depins 断点, lag/reversal/rolling SD 波动率, abnormal_tone 残差 dormant 仅当面板含财务基本面列时产出)。
- 步骤7h 网络族: `compute_network_spillovers`/`compute_bank_network_centrality`(22 中心度)/`compute_cognitive_proximity`/`compute_strategic_differentiation`/`compute_authoritative_similarity`/`compute_benefit_society_panel`/四象限政策对齐(`_classify_policy_quadrants` NaN 掩码 + `_filter_to_verified_universe` semi-join)/`compute_brokerage_centrality`/`compute_industry_neg_shock`/`compute_fire_sale_interaction`/`compute_embedding_peer_network`/`compute_llm_peer_iv`。
- 步骤7h 洗稿率 `_safe_ratio`(分子 pos_symb / 分母 `_svd_denom` substvalid 同域); 7i Janis-Fadner; 8b disag; 8c log_sent(`_gated_log_sent` 零覆盖→NaN); 8d algo_cater; 8e 内联 t2v 双模型存在性诊断 (不读外部 parquet)。
- 步骤8z `compute_iv_extensions`(LOO/广义 Bartik/outlet 构成三引擎 IV 族, 须在全部 merge 之后)。
- `log_diagnostics`(只读) → `export_panel`(REQUIRED_PANEL_COLUMNS 缺列 raise; 物化 low_conf_flag; 写 parquet/csv + sanitize 列名后的 .dta + 启发式标签)。

**关键公式**: J-F: P>N → (P²−PN)/t², N>P → (PN−N²)/t², P=N → 0 (t = n_articles_llm_valid = 正+负+中性有效投票数, 旧 schema 缺该列时回退 t=P+N); disag=√(1−((P−N)/(P+N))²); concern_score=ln_news_coverage×(senti_ratio+1)/2, 其中 senti_ratio=(neg−pos)/(neg+pos); Bartik=Σ_k(base-period share × year-shift)。

**外部依赖**: 本阶段不直接调 LLM (消费 stage 21 缓存产物); 7h-emb/llmpeer + 内联 stage 25/27 含 Sentence-Embedding 相似度 (可能触发 embedding API, 故 timeout=7200 留 buffer)。其 7h-emb/内联 25/27 嵌入子步骤与 7h-llmpeer (stage 48) 均受 NEWS_PROCESS_LLM_OFFLINE 守卫 (embedding_engine miss→raise RuntimeError; llm_peer_iv miss→raise LLMCacheMissError); 仅"消费 stage 21 缓存产物"这一步本身无需守卫。

**DAG 位置**: 上游 24_herd_decay(主)+15(硬)+12_full+18/39f(条件); 下游 46_stata_export (读 40_panel_yearly) + 51_falsification (读 40_panel_yearly + 40_article_bank_level + 12_fintech_news_full)。是流水线的扇入汇聚点 (fan-in)。

■ 白话说明

**这一步是什么**: 这是整条流水线的"总装车间"。前面各阶段把每一篇新闻都打好了分 (语调、是不是金融科技、跟政策像不像、谁和谁一起被提到), 这一步把成千上万条 article 级的记录按"哪家银行、哪一年"归拢压缩成一张规整的银行-年度表格 (panel), 每家银行每一年一行, 一行里有上千列指标。可以理解为把一大筐零散单据汇总成一张年度报表。

**为什么需要它**: 经济学论文跑回归必须是"银行×年"这种结构化面板, 不能直接喂原始新闻。所有论文最终用的那张数据表就是这里生出来的; 它还顺手算了几十种稳健性指标 (换语调算法、换聚合权重、换工具变量), 让论文能证明结论不是靠某一个口径碰巧。

**做得好不好的影响**: 这一步是承上启下的咽喉——上游任何阶段缺数据它就报错停下 (故意不让它带病生成残缺面板), 避免论文用错误数据跑出假结论。它把"按比例/计数"的分子分母口径对齐、把没报道的银行年份标成"缺失"而不是"零", 这些细节直接决定回归系数是否可信; 一旦这里口径错了, 后面所有表格和结论都会跟着错。
========================================================================
"""

import json
import os
import platform
import sys
import time
import warnings

import numpy as np
import pandas as pd
from pandas.errors import PerformanceWarning

from news_process.core.config import herd_sensitivity_grid
from news_process.core.logging import log_stage_summary, pct4, sig4
from news_process.pipeline.features.benefit_society import (
    compute_benefit_society_panel,
)
from news_process.pipeline.features.policy_similarity import (
    compute_authoritative_similarity,
)

# Step 4(d-i) 硬化 (致命问题 5 / 红队 v6): 三处 getattr(..., None) 软依赖
# 改为硬 import。这三个特征 (战略差异度 / 权威政策对齐 / 经营效益投影) 是
# v6/F3 主路径的核心计量指标, 缺失会触发 L883/L889/L904 的 else 分支静默
# logger.info("跳过") , 让 panel 缺列, 进而让 stage 51 falsification 测试基
# 于不完整 panel 跑出无意义的对照系数。改为硬 import: 若 features 模块本
# 身有缺陷或 ImportError, 必须立即 fail-loud, 而非降级生产部分 panel.
from news_process.pipeline.features.strategic_diff import (
    compute_strategic_differentiation,
)

# BERT 概率分布形状叶模块 (2026-07-03 执行计划; 零仓内依赖, 模型清单参数注入)
from news_process.pipeline.panel import bert_distribution

# Phase 2a 扫尾：补全 _m43 模块别名，恢复地理距离缓冲 + 区域模仿渗透率两组特征
# （commit 722bc0e 删除 importlib 反射时遗漏对 _m43.foo() 调用点的更新；
# 详见 plan c1：runner.py 中 hasattr(_m43, ...) 调用点位于 ~L446 / ~L455）。
from news_process.pipeline.panel import geography as _m43

# 从 panel.attention_media (原 42)
from news_process.pipeline.panel.attention_media import (
    compute_attention_treatments,
    compute_fintech_attention_index,
    compute_media_heterogeneity,
)
from news_process.pipeline.panel.dedup_sensitivity import (
    compute_dedup_sensitivity_treatments,
)

# Phase 2a: 全部 9 处 importlib.spec_from_file_location 反射已删除,
# 改为正规子包 import (单源真值: news_process.pipeline.panel.encode 取代 41 号文件)。
from news_process.pipeline.panel.encode import (
    BERT_MODELS,
    CONFIG,
    DICT_NAMES,
    FILENAMES,
    LLM_MODELS,
    OUTPUT_DIR,
    PANEL_CFG,
    STAGE_NAME,
    THREE_CLASS_MODELS,
    aggregate_panel,
    balance_panel,
    compute_media_authority_weights,
    compute_media_tier_weights,
    encode_sentiment,
    logger,
    parse_time,
)

# 从 panel.geography (原 43)
from news_process.pipeline.panel.geography import (
    compute_composite_indicators,
    compute_leave_one_out_sentiment,
    merge_bank_geography,
    standardize_panel_variables,
)

# 从 panel.iv_did (原 44)
from news_process.pipeline.panel.iv_did import (
    compute_bartik_iv,
    compute_bartik_iv_fintech,
    compute_zone_leave1out,
    load_bank_group_maps,
    merge_policy_shocks,
)
from news_process.pipeline.panel.iv_extensions import compute_iv_extensions
from news_process.pipeline.panel.llm_peer_iv import compute_llm_peer_iv
from news_process.pipeline.panel.network_brokerage import (
    compute_brokerage_centrality,
    compute_fire_sale_interaction,
    compute_industry_neg_shock,
)

# P0-2 (cleanup/2026-05-13): 三组 getattr(_x, 'foo', None) 软依赖改为硬 import,
# 与上方 strategic_diff / policy_similarity / benefit_society 的硬化策略对齐.
# 实证: 8 个函数全部已定义, fallback 路径从未触发; 硬 import 让缺失立即在 import
# 时 fail-loud, 而非延迟到调用点 silent skip 让 panel 缺列.
from news_process.pipeline.panel.network_spillover import (
    compute_bank_network_centrality,
    compute_cognitive_proximity,
    compute_embedding_peer_network,
    compute_network_spillovers,
)


def _append_columns(frame: pd.DataFrame, columns: dict) -> pd.DataFrame:
    """一次性批量追加多列, 返回去碎片化 (defragmented) 的 DataFrame。

    逐列 ``frame[col] = ...`` 会触发 pandas PerformanceWarning (高度碎片化);
    用单次 concat + copy 合并写入避免该问题。
    """
    if not columns:
        return frame
    return pd.concat([frame, pd.DataFrame(columns, index=frame.index)], axis=1).copy()


# fix(omni-g-runner-05/g-runner-09, 2026-06-11): 方法 F "高置信度子样本" 阈值。
# 3 模型多数投票下 agreement_rate 支撑集仅 {1/3, 2/3, 1.0}; 历史硬编码 0.67 把唯一
# 多数票档 2/3 (=0.6666...) 整类静默排除, 使 _hc 退化为全票一致 (==1.0), 与 L424
# 声明的 "≥ 2/3" (Shapiro et al. 2022, JoE) 构念不符。取 2/3 - 1e-9 浮点下界,
# 使 2/3 档按声明纳入。
HC_AGREEMENT_THRESHOLD = (2.0 / 3.0) - 1e-9

# 洗稿率 substantiveness-measured 标签集合 (LLM 实质性分类成功的两个合法取值;
# NaN 经 astype(str) 变 'nan' 不在其中 → 视为未测量)。
_SUBST_VALID_LABELS = ('实质性', '象征性')


def _bert_argmax_pos_neg(frame: pd.DataFrame, model: str, track: str):
    """逐 BERT 模型的 argmax 极性指示 (类数尺度不变量)。

    fix(omni-g-runner-01, 2026-06-11): 2-class 模型 (finbert2, P(正面) 基线 ~1/2)
    与 3-class 模型 (finbert_cn/fin_sent_zh, 基线 ~1/3) 的裸 P(正面) 概率尺度不可比:
    等权平均后统一 0.5 二值化使均值被 2-class 尺度主导, 0.5 阈值对 3-class 远严于
    argmax。统一为逐模型 argmax 标签: 3-class 取全类 argmax (P(正)>P(负) ∧ P(正)>P(中));
    2-class 取 P>0.5 (softmax 和为 1 时 ⇔ argmax, 保持旧行为逐位一致)。

    Returns:
        (pos, neg): 布尔 Series 二元组; NaN 概率行两者均 False (与旧 >0.5 行为一致)。
            负面概率列缺失时 neg 返回 None (调用方跳过 negative 编码)。
    """
    p_col = f'{model}_正面{track}'
    n_col = f'{model}_负面{track}'
    u_col = f'{model}_中性{track}'
    p = frame[p_col]
    if n_col not in frame.columns:
        return (p > 0.5), None  # 退化: 仅正面概率可用, 无法 argmax
    n = frame[n_col]
    # fix(dta-coverage-audit, 2026-07-03): 2-class 模型 (finbert2) 的 `_中性` 列是
    # 全 NaN 占位 (tone_berts.py:1144, 刻意非 0), 仅凭列存在判 3-class 会使
    # (p>n)&(p>u) 与全 NaN 比较恒 False → 判正 0 篇, 违背上方 2-class P>0.5 设计。
    # 类数判据双锚: SSOT 身份 (encode.THREE_CLASS_MODELS) 优先 — 注册的 3-class 模型
    # 只要中性列在场就恒走 argmax (中性列损坏为全 NaN 时输出全 False 双元组, 与
    # docstring 的 NaN 行契约一致, 绝不静默退到 P>0.5 尺度混用); SSOT 外模型
    # (占位 2-class / 测试合成模型) 按中性列是否真有值数据驱动兜底。
    if u_col in frame.columns and (model in THREE_CLASS_MODELS or frame[u_col].notna().any()):
        u = frame[u_col]  # 3-class: 全类 argmax
        return ((p > n) & (p > u)), ((n > p) & (n > u))
    return (p > 0.5), (n > 0.5)  # 2-class: P>0.5 ⇔ argmax


def _pool_svd_substvalid_counts(frame: pd.DataFrame):
    """聚合 ``_svd_*`` 篇章级指示 → ``{name}_substvalid_count{track}`` bank-year 计数。

    fix(omni-g-runner-10/g-runner-14, 2026-06-11): 洗稿率分子隐式要求
    innovation_substantiveness 已测量 (NaN→astype(str)→'nan' 永 False), 旧分母却数
    全部阳性文章 (valid 分子 / physical 分母失配, 与已修 encode-01 同族)。本函数在
    runner 内自聚合 (encode.build_aggregation_dict 属 g-encode 组文件, 不越界) 产出
    同域分母计数列, 供步骤 7h 洗稿率除法消费。列名以 ``_count_{track}`` 结尾, 命中
    balance_panel 的计数零填正则 (零新闻 bank-year → 0 → _safe_ratio → NaN)。

    Returns:
        bank-year DataFrame (键 target_bank×year) 或 None (无 _svd_ 列时)。
    """
    svd_cols = [c for c in frame.columns if c.startswith('_svd_')]
    if not svd_cols or 'year' not in frame.columns:
        return None
    agg = frame.groupby(['target_bank', 'year'])[svd_cols].sum().reset_index()
    rename = {}
    for c in svd_cols:
        # 三轨 (full/ctx/ss): ss=银行+金科同句轨。'_ss' 后缀不与 '_full'/'_ctx'
        # 撞尾, 顺序无关 (但保持枚举三元一致以防漏列)。
        for tr in ('_full', '_ctx', '_ss'):
            if c.endswith(tr):
                rename[c] = f"{c[len('_svd_'):-len(tr)]}_substvalid_count{tr}"
                break
    return agg.rename(columns=rename)


def _base_year_median_split(panel: pd.DataFrame, value_col: str = 'n_articles',
                            by: str | None = None) -> pd.Series:
    """Pre-period 固定切分: 面板最早年中位数定组员资格, broadcast 到全年份。

    fix(omni-g-runner-12/g-runner-13, 2026-06-11): digital_frontier / high_coverage
    旧实现按【同年】中位数切分, 组员资格逐年随内生新闻覆盖量翻转 (盘上 43/87、
    20/87 银行跨年翻转), 进入 DDD 交互/tone 交互时调节变量与 outcome 同期内生 —
    与本文件对 Bartik 强制的 pre-treatment 固定公理 (Goldsmith-Pinkham et al.
    2020 AER) 自相矛盾, 也偏离 Fang & Peress (2009 JF) 的 predetermined 排序。
    改为: 用基年 (panel['year'].min()) 有覆盖银行的 value_col 中位数 (可按 `by`
    分组, 如 bank_type) 切分一次, 组员资格跨年固定。基年零覆盖银行 → 0。

    Returns:
        与 panel.index 对齐的 0/1 int Series。
    """
    base_yr = int(panel['year'].min())
    cols = ['target_bank', value_col] + ([by] if by else [])
    base = (panel.loc[panel['year'] == base_yr, cols]
            .drop_duplicates('target_bank').reset_index(drop=True))
    has_news = base[value_col] > 0
    member = pd.Series(0, index=base.index, dtype=int)
    if has_news.any():
        if by is not None:
            med = base[has_news].groupby(by)[value_col].transform('median')
        else:
            med = base.loc[has_news, value_col].median()
        member.loc[has_news] = (
            base.loc[has_news, value_col] >= med).astype(int)
    mapping = pd.Series(member.values, index=base['target_bank'])
    return panel['target_bank'].map(mapping).fillna(0).astype(int)


def _filter_to_verified_universe(df_align: pd.DataFrame,
                                 df_exploded: pd.DataFrame) -> pd.DataFrame:
    """7h-token 聚合域对齐: (docid, target_bank) semi-join LLM-verified 集。

    fix(omni-g-runner-02, 2026-06-11): stage 15 输出 = stage 14 规则预筛候选集
    (含 LLM 验证未通过文章), 而面板其余全部文本测度都在 stage 21 语义精筛后的
    verified 集 (df_exploded=24_herd_decay) 上聚合 — 26.8% 假阳性文章曾污染政策
    对齐族 bank-year 均值/分位阈值/象限分母并制造 phantom bank-year。本函数把
    7h-token 全族 (article_sim_*/fintech_intensity_mean/policy_cosine_sim_lg_*/
    四象限) 的输入收敛到同一 verified 聚合域。
    """
    keys = ['docid', 'target_bank']
    if (not all(k in df_align.columns for k in keys)
            or not all(k in df_exploded.columns for k in keys)):
        logger.warning(
            "  ⚠️ verified 域过滤跳过: docid/target_bank 键不齐 — 7h-token 族将在 "
            "pre-LLM-verification 全集上聚合 (与其余面板测度聚合域不一致, 仅限旧 schema)")
        return df_align
    n_before = len(df_align)
    out = df_align.merge(df_exploded[keys].drop_duplicates(), on=keys, how='inner')
    logger.info(f"  verified 域过滤: {n_before} → {len(out)} 篇 "
                f"(semi-join 24_herd_decay; fix(omni-g-runner-02))")
    return out


def _classify_policy_quadrants(df_align: pd.DataFrame, sim_col: str,
                               freq_col: str, pct: int):
    """四象限逐篇分类 (measured 掩码版), 返回 (token, hidden, subst) float 指示。

    fix(omni-g-runner-03/g-runner-11, 2026-06-11): 旧实现 `NaN >= thresh → False`
    把测量失败 (sim/freq=NaN) 文章静默归入低对齐/低词频 — stage 15 三条优雅早退
    路径写出的 policy_cosine_sim 全 NaN parquet 会让全部高词频文章误归 Token
    (由零测量制造非 NaN 面板值), 且逐篇 NaN 滞留物理域分母。改为: 仅对
    sim/freq 双双 notna 的行分类, 未测量行指示=NaN → groupby('mean') 自动跳过
    (占比分母=已测量篇数); 全 NaN 年阈值=NaN → 全行未测量 → 面板输出 NaN,
    与 L1324-1332 既有"无数据=未测量(NaN)"契约对齐。
    分位阈值 (年度 transform quantile 本就跳过 NaN) 与分类定义域就此一致。
    """
    ysim = df_align.groupby('year')[sim_col].transform(
        lambda x, p=pct: x.quantile(p / 100.0))
    yfreq = df_align.groupby('year')[freq_col].transform(
        lambda x, p=pct: x.quantile(p / 100.0))
    measured = df_align[sim_col].notna() & df_align[freq_col].notna()
    high_freq = df_align[freq_col] >= yfreq
    high_sim = df_align[sim_col] >= ysim
    token = (high_freq & ~high_sim).astype(float).where(measured)
    hidden = (~high_freq & high_sim).astype(float).where(measured)
    subst = (high_freq & high_sim).astype(float).where(measured)
    return token, hidden, subst


def _gated_log_sent(panel: pd.DataFrame, track: str) -> pd.Series:
    """log1p(pos_count) − log1p(neg_count), 零覆盖 bank-year → NaN。

    fix(omni-g-runner-06/g-runner-15, 2026-06-11): balance_panel 契约把计数列零填,
    旧实现对 n_articles==0 (全年无报道, 情感不可测) 的 bank-year 输出 0.0 — 与
    "1正1负完全均衡" 的真实测量 0 不可区分 (盘上 32.2% 行被注入伪中性零)。本文件
    F3 红线 (Allison 2001; Heckman 1979) 规定无文章语调类指标 → NaN, 同族
    jf_coefficient/concern_score/disag 均已遵守, 唯 log_sent 漏网。加覆盖门控:
    仅 n_articles>0 时计算, 否则 NaN (对齐同族缺失语义)。

    fix(F5, 2026-07-16, FATAL_DEFECT_REMEDIATION §2-F5): 上述 g-runner-06 只覆盖
    n_articles==0 情形; ctx/ss 轨"有覆盖但该轨 LLM 全部无效"
    (n_articles_llm_valid_{trk}==0, pos/neg 计数合法为 0) 时仍输出伪中性 0.0
    (盘上实测 ctx 15 行 / ss 11 行), 同族 jf_coefficient (runner.py 步骤 8c,
    per-track valid 分母) 与 disag (P+N=0→NaN) 对同行均正确 NaN — log_sent 是
    家族唯一门控轨失配成员。本修复把 ctx/ss 门控对齐 per-track 有效票分母;
    full 轨为字节稳定保留物理分母 n_articles (⚠ jf 对 full 轨用 valid 分母,
    二者在 full-only 留篇门控下经验恒等 — dev 实测 0 行不等; n_articles='size'
    物理篇数 vs llm_valid='count' 有效票篇数是定义差, 恒等属门控副产; 理论残余
    [full 轨 verified-but-undefined 全年] 登记计划 §7-R6, 生产重生窗口统一)。
    """
    pc, nc = f'pos_count{track}', f'neg_count{track}'
    ls = (np.log1p(panel[pc].fillna(0).astype('float64'))
          - np.log1p(panel[nc].fillna(0).astype('float64')))
    if track == '_full':
        gate = 'n_articles'
    else:
        gate = f'n_articles_llm_valid{track}'
        if gate not in panel.columns:
            logger.warning(
                f"log_sent{track}: 缺 {gate}, 回退 n_articles 门控 (旧 schema)")
            gate = 'n_articles'
    if gate in panel.columns:
        ls = ls.where(panel[gate].fillna(0) > 0)
    return ls


# fix(omni-g-runner-16, 2026-06-11): 8c opt-in 特征面板的登记上游 (新鲜度守卫用)。
# 26_staleness 读 14_news_with_ctx + 25_article_embeddings + 24/21 verified 键
# (article_staleness.py:426-484); 75 读 21_tone_llms[_full] (cross_media_alpha.py:340-347)。
# fix(optin-upstream-config-wiring, 2026-06-25): 登记上游中【config 可改名】的文件名
# (output_13_news_with_ctx / output_24_herd_decay / output_21_tone_llms[_full]) 经
# FILENAMES (= CONFIG['filenames'], encode 导入) 单一真值解析, 默认配置下 == 字面量 →
# golden-safe; 用户在 paths.yaml 改这些上游名时, 新鲜度守卫随之跟随, 不再因硬编码上游名
# 失配而静默退化为 no-op (与 #4 让 stage 25/26 生产者 config-aware 的改动对齐, 闭合其
# 略微扩大的暴露面)。无 config 键者保字面量 = 单一真值: 25_article_embeddings (stage 25,
# schemas._OUTPUT_FILENAME_KEYS=None) + 本 dict 的 feature-file 键 26_staleness_panel
# (stage 26, 经 2026-06-25 改 None 后不可经 config 改名) / 75_cross_media_alpha
# (validation, 不进 OUTPUT_REGISTRY) — 三者恒用默认名。
_OPTIN_FEATURE_UPSTREAMS = {
    '26_staleness_panel.parquet': [
        FILENAMES.get('output_13_news_with_ctx', '14_news_with_ctx.parquet'),
        '25_article_embeddings.parquet',
        FILENAMES.get('output_24_herd_decay', '24_herd_decay.parquet'),
        FILENAMES.get('output_21_tone_llms', '21_tone_llms.parquet'),
    ],
    '75_cross_media_alpha.parquet': [
        FILENAMES.get('output_21_tone_llms_full', '21_tone_llms_full.parquet'),
        FILENAMES.get('output_21_tone_llms', '21_tone_llms.parquet'),
    ],
}


def _merge_optin_feature_panels(panel: pd.DataFrame, output_dir: str) -> pd.DataFrame:
    """8c. Opt-in 特征面板条件左连接 (stage 18 staleness / 39f cross_media)。

    fix(omni-g-runner-16, 2026-06-11): 旧实现仅 `os.path.exists` 守卫 —
    (1) 无新鲜度校验: 实测 06-03 的 39f 被并入 06-10 重生的面板, 而 39f 的上游
        21_tone_llms 已于 06-06 重生 → 面板携带旧数据代际的列 (lineage 不可见)。
        现校验特征文件 mtime ≥ 其登记上游 (_OPTIN_FEATURE_UPSTREAMS); 陈旧 →
        跳过 merge 并 loud-warn 要求重跑 opt-in/validation stage (与 opt-in
        graceful-skip 设计一致: 缺列 = 该 stage 未跑, 而非静默并入陈旧值)。
    (2) drop_duplicates keep='first' 静默取任意首行且使行数守卫永真空转 →
        改为重复键即 raise。
    """
    for _ofile, _otag in [('26_staleness_panel.parquet', 'staleness'),
                          ('75_cross_media_alpha.parquet', 'cross_media')]:
        _opath = os.path.join(output_dir, _ofile)
        if not os.path.exists(_opath):
            continue
        # --- 新鲜度守卫: 特征文件须不早于其全部存在的登记上游 ---
        _feat_mtime = os.path.getmtime(_opath)
        _stale_ups = [
            u for u in _OPTIN_FEATURE_UPSTREAMS.get(_ofile, [])
            if os.path.exists(os.path.join(output_dir, u))
            and os.path.getmtime(os.path.join(output_dir, u)) > _feat_mtime]
        if _stale_ups:
            logger.warning(
                f"  ⚠️ {_ofile} 早于其上游 {_stale_ups} (数据代际陈旧), 跳过 "
                f"{_otag} merge — 请重跑对应 opt-in/validation stage 后再重建面板 "
                f"(fix(omni-g-runner-16))")
            continue
        _odf = pd.read_parquet(_opath)
        if not {'target_bank', 'year'}.issubset(_odf.columns):
            logger.warning(f"  ⚠️ {_ofile} 缺 target_bank/year 键, 跳过 {_otag} merge")
            continue
        # --- 重复键 fail-loud (替代旧 drop_duplicates 静默取首行) ---
        _dup = _odf.duplicated(['target_bank', 'year'])
        if _dup.any():
            raise RuntimeError(
                f"{_ofile} (target_bank, year) 键重复 {int(_dup.sum())} 行 — "
                f"上游 {_otag} 面板非唯一键, 拒绝静默取首行 (fix(omni-g-runner-16))")
        # 只并入面板尚无的新列 (防同名列覆盖; 键除外)
        _bring = ['target_bank', 'year'] + [
            c for c in _odf.columns
            if c not in ('target_bank', 'year') and c not in panel.columns]
        _nb = len(panel)
        panel = panel.merge(_odf[_bring], on=['target_bank', 'year'], how='left')
        if len(panel) != _nb:
            raise RuntimeError(
                f"{_otag} feature merge 改变面板行数 {_nb}->{len(panel)} "
                f"({_ofile} (target_bank,year) 键非 1:1)")
        logger.info(f"  ✅ stage-{_otag} 特征面板已合并: +{len(_bring) - 2} 列 "
                    f"({_ofile}; opt-in, 缺失则 graceful skip)")
    return panel


def _build_llm_valid_masked_weights(frame: pd.DataFrame, weight, wtag: str) -> dict:
    """为 LLM 族 (numerator NA-skip) 构建 valid-mask 权重列, 供 encode 作 VW/MW/HW 加权
    均值的**匹配分母** (Σ weight over valid) —— 修 encode-01: 原 valid-only 分子 ÷ physical
    分母 (Σ weight over all) 使加权语调系统性向 0 衰减 (随 LLM-invalid 占比增大)。

    仅 LLM 族需要: 其 score 为 nullable <NA>(无效行) → 分子 NA-skip。**dict/BERT 族不建**
    (前提更正 reaudit-2026-07-12 WP-A5: dict 族 score 结构性无 NaN — stage 13 硬过滤后
    空文本分支不可达; BERT 族存在失败哨兵 NaN (omni-g-berts-02), 掩码根治 DEFER M0
    窗口 WP-B1, 现行防线 = panel 输入处 infer_failed 观测闸; 见 encode.py VW 段说明)。

    Args:
        frame: 含 llm_vote_score / {short}_score / llm_prob_score {track} 列的篇级 df。
        weight: pd.Series (三轨同权重, 如 VW mention_density / MW media_authority) 或
                dict {track: Series} (如 HW 三轨 (full/ctx/ss) 独立权重 hw_by_track)。
        wtag: 'vw' / 'mw' / 'hw' (列名标签)。

    白话: 算加权平均语调时, 分子只加了"LLM 真给出判断"的文章, 分母却把
    所有文章的权重都加进去 — 等于把没判断的文章当成语调为 0, 平均值被
    人为往 0 拉。这里给每种权重配一个"只数有效文章"的分母列, 让分子分母
    数的是同一批文章。

    Returns:
        dict {col_name: masked_series}; 列名 ``_wd_{wtag}_{group}{track}``,
        group ∈ {llm, <每个模型 short>, prob}。masked = weight.where(score.notna()),
        无效行置 NaN → groupby('sum') 自动跳过 → Σ weight over valid。
    """
    out = {}
    for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
        if f'llm_vote_score{track}' not in frame.columns:
            continue
        wt = weight[track] if isinstance(weight, dict) else weight
        # llm-aggregate validity (llm_vote_score / llm_vote_cont 同一行有效性)
        out[f'_wd_{wtag}_llm{track}'] = wt.where(frame[f'llm_vote_score{track}'].notna())
        # 逐模型 (各自有效性)
        for short in LLM_MODELS:
            sc = f'{short}_score{track}'
            if sc in frame.columns:
                out[f'_wd_{wtag}_{short}{track}'] = wt.where(frame[sc].notna())
        # logit-to-score 概率 (自身有效性)
        sp = f'llm_prob_score{track}'
        if sp in frame.columns:
            out[f'_wd_{wtag}_prob{track}'] = wt.where(frame[sp].notna())
    return out



# ============================================================================
# 8 + 9. 诊断 + 导出 — Phase 2b 按单一职责原则抽离到 export.py;
# 此处 re-export 以保持向后兼容 (旧调用方仍可从 runner import)。
# ============================================================================
from news_process.pipeline.panel.export import export_panel, log_diagnostics  # noqa: E402,F401

# ============================================================================
# 主流程
# ============================================================================


def _log_environment_config_and_methods(input_path: str) -> None:
    """打印 项目/环境 + 输入输出 + 运行配置 + 方法论依据 四大块 (日志富集 2026-06-24)。

    目标 (用户要求"在日志文件中提供尽可能多的项目信息、运行期间信息和运行结果信息"):
    把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数、构念学术出处"一次性
    落进 40_panel_export_main.log, 便于复现核对 / 审计 / 排错。**纯日志, 不读不写
    任何产物, 不改任何值/schema/控制流 (golden-safe)**。整体 try/except 包裹, 任一
    子项异常都降级为 warning, 绝不让日志块崩掉面板总装阶段 (此乃流水线 fan-in 汇聚点)。
    """
    try:
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')

        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (面板导出主入口, STAGES_MAIN; "
                    "内含子步 41+42+43+44+46+47→45 的串行编排; 三轨 full/ctx/ss)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板); "
                    "版本 v3.16.0 (rule-ablation-ladder)")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'}")
        logger.info("     · 成本/确定性: 本阶段不直接调 LLM (消费 stage 21 缓存产物), 主体纯 CPU / $0;"
                    " 仅 7h-emb/llmpeer 内联 Sentence-Embedding 相似度可能触网 (timeout=7200);"
                    " 3 个网络中心度列 (clustering/cfbetween/harmonic) 受 BLAS-FP 影响非逐位确定。")

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 主输入:   {input_path} (24_herd_decay, df_exploded, stage21 语义精筛 verified 集)")
        _align_fn = FILENAMES.get('output_15_article_alignment', '16_article_alignment.parquet')
        _ftfull_fn = FILENAMES.get('output_12_fintech_full', '12_fintech_news_full.parquet')
        logger.info(f"     · 硬依赖:   {os.path.join(OUTPUT_DIR, _align_fn)} (policy_cosine_sim; 7h-token)")
        logger.info(f"     · 注意力分母: {os.path.join(OUTPUT_DIR, _ftfull_fn)} (全量银行新闻; 6b)")
        _panel_fn = FILENAMES.get('output_40_panel_yearly', '40_panel_yearly.parquet')
        logger.info(f"     · 主输出:   {os.path.join(OUTPUT_DIR, _panel_fn)} (+.csv/.dta + 3 张地理注意力副表)")
        logger.info(f"     · 输出目录: {OUTPUT_DIR}")

        logger.info("  ⚙ 运行配置 (config/panel.yaml::panel 等)")
        try:
            _sens_thrs, _sens_tags = herd_sensitivity_grid(CONFIG)
            logger.info(f"     · HW 阈值敏感性网格 herd_sensitivity_grid: "
                        f"阈值={[sig4(t) for t in _sens_thrs]} | 标签={list(_sens_tags)} "
                        "(仅施于 LLM 投票主测度)")
        except Exception as _e1:  # noqa: BLE001
            logger.info(f"     · HW 阈值敏感性网格: (读取跳过: {_e1})")
        _bartik_base = PANEL_CFG.get('bartik_base_year', 'auto')
        _bartik_cut = PANEL_CFG.get('bartik_pre_treatment_cutoff', 2019)
        logger.info(f"     · Bartik IV: base_year={_bartik_base} (auto→max(year.min,2010)) "
                    f"| pre_treatment_cutoff={_bartik_cut} (GPSS 2020 外生性守卫)")
        logger.info(f"     · 模型族: LLM={list(LLM_MODELS)} | 词典={list(DICT_NAMES)} "
                    f"| BERT={list(BERT_MODELS)}")
        logger.info("     · 三轨: ['_full','_ctx','_ss'] 全平价 (ss=银行+金科同句, 缺列优雅跳过); "
                    "语调时序波动率窗口 rolling SD w=3 (min_periods=2)")

        logger.info("  📖 方法论依据 (构念学术出处, 逐字取自经核验注册表; emit 进日志便于审计)")
        logger.info("     · 面板平衡/笛卡尔补全(结构自检): Angrist, J. D., & Pischke, J.-S. (2009). "
                    "Mostly harmless econometrics: An empiricist's companion. Princeton University Press. "
                    "https://doi.org/10.1515/9781400829828")
        logger.info("     · 移位份额/Bartik IV 识别设计①(步骤 7e; pre-treatment 基期外生性公理): "
                    "Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, "
                    "why, and how. American Economic Review, 110(8), 2586-2624. "
                    "https://doi.org/10.1257/aer.20181047")
        logger.info("     · 移位份额/Bartik IV 识别设计②(准实验份额暴露设计的识别条件): Borusyak, K., Hull, P., "
                    "& Jaravel, X. (2022). Quasi-experimental shift-share research designs. The Review of "
                    "Economic Studies, 89(1), 181-213. https://doi.org/10.1093/restud/rdab030")
        logger.info("     · 移位份额/Bartik IV 识别设计③(冲击外生性的非随机暴露校正): Borusyak, K., & Hull, P. "
                    "(2023). Nonrandom exposure to exogenous shocks. Econometrica, 91(6), 2155-2185. "
                    "https://doi.org/10.3982/ECTA19367")
        logger.info("     · 交错 DID 实操准则(步骤 44 政策冲击 merge_policy_shocks 的处理效应解释): "
                    "Baker, A., Callaway, B., Cunningham, S., Goodman-Bacon, A., & Sant'Anna, P. H. C. "
                    "(2026). Difference-in-differences designs: A practitioner's guide. Journal of "
                    "Economic Literature, 64(2), 498-557. https://doi.org/10.1257/jel.20251650")
        logger.info("     · 双向固定效应/Mundlak 与 DID 估计量等价性(异质处理效应下 TWFE 偏误修正): "
                    "Wooldridge, J. M. (2025). Two-way fixed effects, the two-way Mundlak regression, "
                    "and difference-in-differences estimators. Empirical Economics, 69(5), 2545-2587. "
                    "https://doi.org/10.1007/s00181-025-02807-z")
        logger.info("     · 媒体注意力(extensive 覆盖): Fang, L., & Peress, J. (2009). Media coverage and "
                    "the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. "
                    "https://doi.org/10.1111/j.1540-6261.2009.01493.x")
        logger.info("     · 媒体语调/情绪(过度反应基线): De Bondt, W. F. M., & Thaler, R. (1985). Does the "
                    "stock market overreact? The Journal of Finance, 40(3), 793-805. "
                    "https://doi.org/10.1111/j.1540-6261.1985.tb05004.x")
        logger.info("     · 媒体悲观语调→市场: García, D. (2013). Sentiment during recessions. The Journal "
                    "of Finance, 68(3), 1267-1300. https://doi.org/10.1111/jofi.12027")
        logger.info("     · 文本看涨/看跌分歧度(disag): Antweiler, W., & Frank, M. Z. (2004). Is all that "
                    "talk just noise? The information content of internet stock message boards. The Journal "
                    "of Finance, 59(3), 1259-1294. https://doi.org/10.1111/j.1540-6261.2004.00662.x")
        logger.info("     · 媒体声誉(媒体权威性加权依据): Deephouse, D. L. (2000). Media reputation as a "
                    "strategic resource: An integration of mass communication and resource-based theories. "
                    "Journal of Management, 26(6), 1091-1112. https://doi.org/10.1177/014920630002600602")
        logger.info("     · 交互项构建规范(异质性): Brambor, T., Clark, W. R., & Golder, M. (2006). "
                    "Understanding interaction models: Improving empirical analyses. Political Analysis, "
                    "14(1), 63-82. https://doi.org/10.1093/pan/mpi014")
        logger.info("     · 文本沟通可信度(disclosure 计量): Cao, S., Jiang, W., Yang, B., & Zhang, A. L. "
                    "(2023). How to talk when a machine is listening: Corporate disclosure in the age of AI. "
                    "The Review of Financial Studies, 36(9), 3603-3642. https://doi.org/10.1093/rfs/hhad021")
        logger.info("     · 中文金融文本气候/情感测度对标: Bingler, J. A., Kraus, M., Leippold, M., & "
                    "Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on "
                    "corporate climate risk disclosures. Finance Research Letters, 47, 102776. "
                    "https://doi.org/10.1016/j.frl.2022.102776")
        logger.info("     · FinBERT 金融文本信息抽取: Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A "
                    "large language model for extracting information from financial text. Contemporary "
                    "Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832")
        logger.info("     · 政策语料/文本相似(政策对齐): Distel, A. P., Grimpe, C., & Poetz, M. (2026). From "
                    "evidence to impact: The use of scientific research in policy documents. Research Policy, "
                    "55(3), 105426. https://doi.org/10.1016/j.respol.2026.105426")
        logger.info("     · 政策脱耦(象征 vs 实质对齐): Westphal, J. D., & Zajac, E. J. (2001). Decoupling "
                    "policy from practice: The case of stock repurchase programs. Administrative Science "
                    "Quarterly, 46(2), 202-228. https://doi.org/10.2307/2667086")
        logger.info("     · 数字经济(金科测度宏观背景): Goldfarb, A., & Tucker, C. (2019). Digital economics. "
                    "Journal of Economic Literature, 57(1), 3-43. https://doi.org/10.1257/jel.20171452")
        logger.info("     · 文本情绪计量(预期/不确定性): Angelico, C., Marcucci, J., Miccoli, M., & Quarta, F. "
                    "(2022). Can we measure inflation expectations using Twitter? Journal of Econometrics, "
                    "228(2), 259-277. https://doi.org/10.1016/j.jeconom.2021.12.008")
        logger.info("     · 央行/政策沟通文本(中文金融语境): 姜富伟, 李梦如, & 孟令超. (2024). 调预期、防风险："
                    "央行金融稳定沟通效果研究——基于文本分析的视角. 经济学（季刊）, 24(6), 2025-2040. "
                    "https://doi.org/10.13821/j.cnki.ceq.2024.06.19")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法论信息打印失败 (不影响处理): {e}")


def main():
    """40_panel_export_main 主流程。

    .. todo:: v3.0-split (Plan-r3 P1-7 锚点, god function)

        本函数当前是项目最大的 monolithic 主流程, 串行执行 7 个 stage 子步,
        与 ``core.dag.py:STAGES_MAIN`` 的"阶段40 (内含 41+42+43+44+46+47)"
        StageSpec.name 一一对应:

            41 编码聚合          → encode.aggregate_panel
            42 媒体注意力        → attention_media.compute_media_heterogeneity
            43 地理缓冲          → geography.compute_geo_proximity_buffers
            44 Bartik IV/DID    → iv_did.compute_bartik_iv + merge_policy_shocks
            46 网络溢出          → network_spillover.compute_bank_network_centrality
            47 经纪网络          → network_brokerage.<...>
            45 诊断与多格式导出   → export.export_panel

        v3.0 拆分策略:
        1. 把每个子步提升为独立 ``StageSpec`` (子进程隔离, 便于失败定位)
        2. 各子步 OUTPUT_REGISTRY 独立, 实现"中途断点续跑"
        3. 本 main() 退化为薄编排器 (~50 行, 仅 dispatch + summary)

        约束: 拆分必须与 thin shim 退役 (Plan-r3 P3-18) 同期, 否则会破坏
        ``python news_process/40_panel_export_main.py`` 这个外部 CLI 契约.
    """
    start_time = time.time()

    # fix(2026-06-19 run-check F13): 面板总装在多处对宽表 (~2700 列) 逐列 panel[col]=...
    # 赋值 (如 disag/cater 三轨族, runner.py:~2120-2205), 会反复触发 pandas
    # PerformanceWarning(DataFrame is highly fragmented) —— 本模块 docstring (L168) 与
    # L987 早已记录此为预期的良性碎片化提示, 不影响 40_panel_yearly.parquet 任一列的
    # 值/dtype/列序 (golden 锚点字节不变, 已实证)。在主流程入口按 message+category 精确
    # 抑制 (函数级, 不在 import 期污染测试; 与 stage 21 F3 同口径)。
    warnings.filterwarnings(
        "ignore",
        category=PerformanceWarning,
        message="DataFrame is highly fragmented",
    )

    # ── 阶段功能 banner (黄金范式: 让 <stage>.log 自带说明书) ──
    logger.info("=" * 72)
    logger.info("阶段 40: 面板导出 (主, 三轨承载) — Bank-Year 面板总装 (41+42+43+44+46+47→45)")
    logger.info("=" * 72)
    logger.info("【功能】整条流水线的'总装车间': 把 stage 21 语义精筛后的 article×bank 级")
    logger.info("        记录 (24_herd_decay) 按 (银行, 年份) 归拢压缩成 bank-year 面板,")
    logger.info("        每家银行每年一行, 一行上千列指标 (情感/注意力/网络/IV/稳健性),")
    logger.info("        最终落 40_panel_yearly.parquet(+.csv/.dta) + 3 张地理注意力副表。")
    logger.info("【方法】串行 7 子步 (StageSpec 41→42→43→44→46→47→45): 篇章级情感编码 →")
    logger.info("        VW/MW/HW 三类加权 → aggregate_panel 聚合 → balance_panel 笛卡尔积")
    logger.info("        补全 (无报道行标 has_coverage=0, 不填零) → 注意力/地理/Bartik IV/DID/")
    logger.info("        网络族; 三轨 ['_full','_ctx','_ss'] 全平价 (ss=银行+金科同句, 缺列优雅跳过)。")
    logger.info("        关键公式: J-F P>N→(P²−PN)/t²; Bartik=Σ_k(base-share×year-shift)。")
    logger.info("【判读】结构自检: 行数应==banks×years笛卡尔积(post-balance_panel恒成立);")
    logger.info("        真实信号密度看 has_coverage=1 占比; 零新闻行=故意标缺失而非零(护回归口径);")
    logger.info("        P1 主规格主处理变量(treatment)=llm_vote_tone_full (full-only 2026-06-29); 上游缺数据→fail-loud 停。")
    logger.info("【确定性】本阶段不直接调 LLM (消费 stage 21 缓存); 仅 7h-emb/llmpeer 内联")
    logger.info("        Sentence-Embedding 相似度可能触网 (timeout=7200 留 buffer); 其余纯 CPU。")

    # 运行期 per-phase 墙钟计时累计 (各主要子步耗时, 末尾汇总打印; 纯日志)
    phase_durations: dict[str, float] = {}

    # --- 1. 数据加载与验证 ---
    logger.info("=" * 60)
    logger.info("步骤 1: 数据加载与验证")
    logger.info("=" * 60)

    input_filename = FILENAMES.get('output_24_herd_decay', '24_herd_decay.parquet')
    input_path = os.path.join(OUTPUT_DIR, input_filename)

    # 项目/环境 + 输入输出 + 运行配置 + 方法论依据 四大块 (日志富集 2026-06-24, golden-safe)
    _log_environment_config_and_methods(input_path)

    if not os.path.exists(input_path):
        logger.error(f"输入文件不存在: {input_path}")
        sys.exit(1)

    _t_load = time.time()
    df = pd.read_parquet(input_path)
    logger.info(f"  已加载: {input_path}")
    logger.info(f"  行数: {len(df):,}, 列数: {df.shape[1]}")

    # fix(reaudit-2026-07-12 WP-A1): BERT 推理失败哨兵可观测性闸 (golden-safe 纯日志)。
    # tone_berts._failure_result 的概率哨兵 = NaN (omni-g-berts-02, 2026-06-11), 而 encode 的
    # BERT vw/mw/hw 加权族分母仍为物理域权重和 (encode-01 carve-out): 任一 infer_failed 行
    # 会使分子 NA-skip、分母仍含其权重 → 该 bank-year 格向 0 偏。根治 (镜像
    # _build_llm_valid_masked_weights 给 BERT 建掩码) 属改测度, DEFER 至 M0/golden 重生窗口
    # (见 FATAL_REAUDIT_CLOSEOUT_EXECUTION_PLAN_2026-07-12 §3 WP-B1); 本闸保证失败率 > 0
    # 时 fail-loud 可见, 绝不静默。判真用 == True (防 NaN 经 astype(bool) 误判)。
    _if_cols = [c for c in df.columns
                if c.endswith(('_infer_failed_full', '_infer_failed_ctx', '_infer_failed_ss'))]
    _if_total = int((df[_if_cols] == True).sum().sum()) if _if_cols else 0  # noqa: E712
    if _if_total > 0:
        logger.error(
            f"  ⚠ BERT 推理失败哨兵: {_if_total} 篇×轨 (infer_failed=True) — "
            f"{{b}}_pos/neg_{{vw,mw,hw}} 加权族物理域分母将使受影响格向 0 偏 "
            f"(掩码根治 DEFER M0, 见 WP-B1); 请核查 stage 23 日志定位失败篇")
    elif _if_cols:
        logger.info("  BERT 推理失败哨兵: 0 篇 (加权族物理域分母无向-0-偏风险)")

    # 校验关键列
    required_cols = ['target_bank', 'llm_sentiment_full', '日期', 'llm_agreement_rate_full']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        logger.error(f"  缺失关键列: {missing}")
        sys.exit(1)
    logger.info(f"  关键列校验通过 ✓")
    phase_durations['①数据加载+校验'] = time.time() - _t_load

    # --- 2. 篇章级情感数值编码 ---
    _t_enc = time.time()
    df = encode_sentiment(df)
    phase_durations['②篇章级情感编码 encode_sentiment'] = time.time() - _t_enc

    # --- 3. 多银行特征提取（展开已在阶段 11 完成） ---
    logger.info("=" * 60)
    logger.info("步骤 3: 多银行特征提取（展开已在阶段 11 完成）")
    logger.info("=" * 60)
    logger.info(f"  target_bank 列已存在, 唯一银行数: {df['target_bank'].nunique()}")
    # 计算多银行特征（基于 co_mentioned_banks）
    if 'co_mentioned_banks' in df.columns:
        df['bank_count'] = df['co_mentioned_banks'].apply(
            lambda x: len(str(x).split(';')) + 1 if x and str(x).strip() else 1
        )
    else:
        df['bank_count'] = 1
    df['is_multi_bank'] = (df['bank_count'] > 1).astype(int)
    df['ln_bank_count'] = np.log1p(df['bank_count'])
    # in_title 已在 11_news_bank.py 中作为 target_bank_in_title 生成
    if 'target_bank_in_title' in df.columns:
        df['in_title'] = df['target_bank_in_title'].astype(int)
    elif 'in_title' not in df.columns:
        df['in_title'] = 0

    # --- 3b. 提及密度加权列预计算 (Value-weighted Exposure, Hassan 2019 QJE) ---
    if 'mention_density' in df.columns:
        logger.info("=" * 60)
        logger.info("步骤 3b: 提及密度加权列预计算 (VW, 三轨 full/ctx/ss)")
        logger.info("=" * 60)
        w = df['mention_density'].fillna(0)
        weighted_cols = {}
        for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
            if f'llm_vote_score{track}' not in df.columns:
                continue
            # 情感离散/连续
            weighted_cols[f'llm_vote_score_w{track}'] = df[f'llm_vote_score{track}'] * w
            weighted_cols[f'llm_vote_cont_w{track}'] = df[f'llm_vote_cont{track}'] * w
            # 频次
            weighted_cols[f'is_positive_w{track}'] = df[f'is_positive{track}'] * w
            weighted_cols[f'is_negative_w{track}'] = df[f'is_negative{track}'] * w
            # LLM 逐模型
            for short in LLM_MODELS:
                for sfx in ['_score', '_cont']:
                    src = f'{short}{sfx}{track}'
                    if src in df.columns:
                        weighted_cols[f'{short}{sfx}_w{track}'] = df[src] * w
            # 词典
            for d in DICT_NAMES:
                src = f'{d}_score{track}'
                if src in df.columns:
                    weighted_cols[f'{d}_score_w{track}'] = df[src] * w
            # 词典 IDF (Gentzkow, Kelly & Taddy 2019, JEL)
            for d in DICT_NAMES:
                src = f'{d}_idf_score{track}'
                if src in df.columns:
                    weighted_cols[f'{d}_idf_score_w{track}'] = df[src] * w
            # BERT
            for b in BERT_MODELS:
                for label in ['_正面', '_负面']:
                    src = f'{b}{label}{track}'
                    if src in df.columns:
                        weighted_cols[f'{b}{label}_w{track}'] = df[src] * w
            # Logit-to-Score 概率分数
            src_prob = f'llm_prob_score{track}'
            if src_prob in df.columns:
                weighted_cols[f'llm_prob_score_w{track}'] = df[src_prob] * w
        # fix(encode-01, metric-audit 2026-06-10): 为 LLM 族建 valid-mask 权重 (Σ w over
        # valid), 供 encode 作匹配分母, 消除 valid-only 分子/physical 分母失配 (向零衰减)。
        weighted_cols.update(_build_llm_valid_masked_weights(df, w, 'vw'))
        df = _append_columns(df, weighted_cols)
        logger.info(f"  已生成 {len(weighted_cols)} 个加权列")
    else:
        logger.info("  mention_density 列不存在, 跳过加权列预计算")

    # --- 3c. 媒体权威性加权列预计算 (Holzman et al. 2023, TAR) ---
    df = compute_media_authority_weights(df)
    # v3.6.1 PR #6 (C1): 媒体 3 级 tier 权重并行列 (Solomon 2012 RFS;
    # Engelberg-Parsons 2011 JF). 不替换 'media_authority_weight' main,
    # 仅追加 'media_authority_weight_tier' + 'media_tier_label' 作
    # paper Table A8 sensitivity. Append-only 不破坏现契约.
    df = compute_media_tier_weights(df)
    mw = df['media_authority_weight'].fillna(1.0)
    weighted_cols = {}
    for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
        if f'llm_vote_score{track}' not in df.columns:
            continue
        weighted_cols[f'llm_vote_score_mw{track}'] = df[f'llm_vote_score{track}'] * mw
        weighted_cols[f'llm_vote_cont_mw{track}'] = df[f'llm_vote_cont{track}'] * mw
        for short in LLM_MODELS:
            for sfx in ['_score', '_cont']:
                src = f'{short}{sfx}{track}'
                if src in df.columns:
                    weighted_cols[f'{short}{sfx}_mw{track}'] = df[src] * mw
        for d in DICT_NAMES:
            src = f'{d}_score{track}'
            if src in df.columns:
                weighted_cols[f'{d}_score_mw{track}'] = df[src] * mw
            src_idf = f'{d}_idf_score{track}'
            if src_idf in df.columns:
                weighted_cols[f'{d}_idf_score_mw{track}'] = df[src_idf] * mw
        for b in BERT_MODELS:
            for label in ['_正面', '_负面']:
                src = f'{b}{label}{track}'
                if src in df.columns:
                    weighted_cols[f'{b}{label}_mw{track}'] = df[src] * mw
        # Logit-to-Score 概率分数
        src_prob = f'llm_prob_score{track}'
        if src_prob in df.columns:
            weighted_cols[f'llm_prob_score_mw{track}'] = df[src_prob] * mw
    # fix(encode-01, 2026-06-10): LLM 族 valid-mask 媒体权威权重分母
    weighted_cols.update(_build_llm_valid_masked_weights(df, mw, 'mw'))
    df = _append_columns(df, weighted_cols)
    logger.info(f"  已生成 {len(weighted_cols)} 个媒体权威性加权列")

    # --- 3d. 跟风衰减加权列预计算 (Tetlock 2011, RFS; Edwards 2001 ORM) ---
    # v3.6.0 (Plan E P1 B3): 三轨 (full/ctx/ss) 权重独立施加 (remove-title-track
    # 后 full/ctx, v3.9.0 增 ss=银行+金科同句轨)
    #   _full track → herd_weight_full
    #   _ctx  track → herd_weight_ctx
    #   _ss   track → herd_weight_ss   (stage 24 镜像 ctx 产出; 缺则回退 hw_full)
    # 向后兼容: 若仅存在历史的 herd_weight 单列 (v3.5.0 及更早), 退化为
    # 旧行为 (三轨用同一权重), 但记 WARN 提示用户重跑 stage 24。
    has_dual_hw = ('herd_weight_full' in df.columns and
                   'herd_weight_ctx' in df.columns)
    has_legacy_hw = 'herd_weight' in df.columns
    if has_dual_hw or has_legacy_hw:
        logger.info("=" * 60)
        if has_dual_hw:
            logger.info("步骤 3d: 跟风衰减加权列预计算 (HW, 三轨独立 v3.9.0)")
            hw_full = df['herd_weight_full'].fillna(1.0)
            hw_ctx = df['herd_weight_ctx'].fillna(1.0)
        else:
            logger.warning(
                "步骤 3d: 检测到 v3.5.0 legacy herd_weight 单列, "
                "退化为单轨加权 — 建议重跑 stage 24 (herd_decay) 升级到三轨")
            hw_full = df['herd_weight'].fillna(1.0)
            hw_ctx = hw_full
        # ss 轨权重: stage 24 镜像 ctx 产 herd_weight_ss; 缺列 (旧 schema / ss
        # 未上线) 优雅回退 hw_full (与 legacy 单轨退化同口径)。
        hw_ss = (df['herd_weight_ss'].fillna(1.0)
                 if 'herd_weight_ss' in df.columns else hw_full)
        logger.info("=" * 60)
        hw_by_track = {'_full': hw_full, '_ctx': hw_ctx, '_ss': hw_ss}
        weighted_cols = {}
        for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
            if f'llm_vote_score{track}' not in df.columns:
                continue
            hw = hw_by_track[track]
            # 情感离散/连续 (遵循 MW 命名模式: _hw 在 track 之前)
            weighted_cols[f'llm_vote_score_hw{track}'] = df[f'llm_vote_score{track}'] * hw
            weighted_cols[f'llm_vote_cont_hw{track}'] = df[f'llm_vote_cont{track}'] * hw
            # LLM 逐模型
            for short in LLM_MODELS:
                for sfx in ['_score', '_cont']:
                    src = f'{short}{sfx}{track}'
                    if src in df.columns:
                        weighted_cols[f'{short}{sfx}_hw{track}'] = df[src] * hw
            # 词典
            for d in DICT_NAMES:
                src = f'{d}_score{track}'
                if src in df.columns:
                    weighted_cols[f'{d}_score_hw{track}'] = df[src] * hw
                src_idf = f'{d}_idf_score{track}'
                if src_idf in df.columns:
                    weighted_cols[f'{d}_idf_score_hw{track}'] = df[src_idf] * hw
            # BERT
            for b in BERT_MODELS:
                for label in ['_正面', '_负面']:
                    src = f'{b}{label}{track}'
                    if src in df.columns:
                        weighted_cols[f'{b}{label}_hw{track}'] = df[src] * hw
            # Logit-to-Score 概率分数
            src_prob = f'llm_prob_score{track}'
            if src_prob in df.columns:
                weighted_cols[f'llm_prob_score_hw{track}'] = df[src_prob] * hw
        # fix(encode-01, 2026-06-10): LLM 族 valid-mask 跟风衰减权重分母 (三轨独立权重)
        weighted_cols.update(_build_llm_valid_masked_weights(df, hw_by_track, 'hw'))
        df = _append_columns(df, weighted_cols)
        logger.info(f"  已生成 {len(weighted_cols)} 个跟风衰减加权列 "
                    f"({'三轨独立权重' if has_dual_hw else '单轨 legacy 权重'})")

        # --- 3d-2. 阈值敏感性 HW 加权列 (2026-06-13) ---
        # stage 24 按 herd_detection.sensitivity_thresholds 网格输出
        # herd_weight_{track}_thrNN; 此处仅为 LLM 投票主测度族 (score/cont)
        # 生成逐 τ 加权列 + valid-mask 分母 (与 _build_llm_valid_masked_weights
        # 的 'llm' 组同构, encode-01 分子分母同域) — 网格 × 全 11 测度族会列爆炸,
        # 稳健性表只需主回归 DV 的逐 τ 变体。legacy 单列 herd_weight 场景
        # (v3.5.x parquet) 无 thr 列, 自动整体跳过。
        # 白话: 每个备选门槛的打折权重, 只乘到 LLM 投票语调这一个主指标上,
        # 聚合后在 Stata 里逐列重跑主回归, 证明结论不靠 0.35 这个门槛。
        _sens_thrs, _sens_tags = herd_sensitivity_grid(CONFIG)
        sens_cols = {}
        for _tag in _sens_tags:
            for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
                w_src = f'herd_weight{track}_{_tag}'
                if (w_src not in df.columns
                        or f'llm_vote_score{track}' not in df.columns):
                    continue
                hw_t = df[w_src].fillna(1.0)
                sens_cols[f'llm_vote_score_hw_{_tag}{track}'] = (
                    df[f'llm_vote_score{track}'] * hw_t)
                sens_cols[f'llm_vote_cont_hw_{_tag}{track}'] = (
                    df[f'llm_vote_cont{track}'] * hw_t)
                sens_cols[f'_wd_hw_{_tag}_llm{track}'] = hw_t.where(
                    df[f'llm_vote_score{track}'].notna())
        if sens_cols:
            df = _append_columns(df, sens_cols)
            logger.info(f"  已生成 {len(sens_cols)} 个阈值敏感性 HW 加权列 "
                        f"(tags={_sens_tags})")

    # --- 4. 时间解析 ---
    df = parse_time(df)

    # =========================================================================
    # 洗稿率前置列: 多方法 × 三轨 (full/ctx/ss) 篇章级标记
    # =========================================================================
    # 学术依据:
    #   Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022).
    #   Cheap talk and cherry-picking: What ClimateBert has to say on corporate
    #   climate risk disclosures. Finance Research Letters, 47(Part B), 102776.
    #   https://doi.org/10.1016/j.frl.2022.102776
    #
    # 构造 多方法 × 三轨 (Full/Ctx/SS) 洗稿率变体的篇章级标记列
    # (fix(omni-g-runner-08, 2026-06-11): 历史注释硬编码 "40 种/5 模型" 与实现漂移 —
    #  实际变体数随启用模型/词典数浮动, 以步骤 7h 的 wr_variants 诊断日志为准):
    #   A:  LLM 多数投票 (is_positive{track}, 三轨)
    #   A2: 单个 LLM (逐 LLM 情感{track} > 0, LLM_MODELS 当前 3 个)
    #   B:  反向验证 (负面{track} ∧ 实质性)
    #   D/D2: 词典均值 / 单词典 ({dict}_score{track} > 0, DICT_NAMES 6 本)
    #   E/E2: BERT 均值 (逐模型 argmax 多数票) / 单 BERT (argmax 标签,
    #         BERT_MODELS 当前 3 个; 见 fix(omni-g-runner-01))
    #   F:  高置信度子样本 (agreement_rate{track} ≥ 2/3, 实现= 2/3 - 1e-9 浮点下界)
    # 方法 C 和 G 无需篇章级标记, 直接使用面板级已有变量计算
    # v3.2.0 BREAKING (plan v14 §3.3 P3): bare innovation_substantiveness 删除, 单独使用 _full 作 main spec
    # M2 P3 后续展开 count 4-way (sentiment × subst 三轨乘积)
    _tt = df['innovation_substantiveness_full'].astype(str).str.strip() if 'innovation_substantiveness_full' in df.columns else None
    _is_symb = (_tt == '象征性') if _tt is not None else None
    _is_sub  = (_tt == '实质性') if _tt is not None else None
    # fix(omni-g-runner-10/g-runner-14, 2026-06-11): substantiveness-measured 掩码。
    # 分子侧 NaN 经 astype(str) 变 'nan' → _is_symb/_is_sub 恒 False (测量失败永不入
    # 分子), 但旧分母数全部阳性文章 → LLM 实质性分类失败率上升时洗稿率系统性下偏
    # (valid 分子 / physical 分母失配, 与已修 encode-01 同族)。此处为每个方法的分母
    # 构造 `_svd_*` (subst-valid denominator) 篇章级指示, 步骤 7h 聚合后作同域分母。
    # 白话: 洗稿率 = "正面且象征性"的文章 ÷ 正面文章。如果一篇文章 LLM 没能判出
    # 实质性/象征性, 它进不了分子, 那分母也不该数它 — 否则分类失败越多, 洗稿率
    # 被稀释得越低, 这是假象不是事实。_svd_* 列就是"分母只数判出来的那批"。
    _subst_measured = _tt.isin(_SUBST_VALID_LABELS) if _tt is not None else None

    washing_cols = {}
    for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
        pos_col = f'is_positive{track}'
        neg_col = f'is_negative{track}'
        if pos_col not in df.columns or _is_symb is None:
            continue

        # --- 方法 A: LLM 投票 (正面 ∧ 象征性) ---
        # v6/F2: is_positive 现在是 nullable Int8 (NaN = 测量失败/平局/拒绝)。
        # NaN 行不应被视为"正面描述"，等价于 fillna(0) 后 == 1 比较为 False。
        washing_cols[f'_is_pos_symb{track}'] = (
            (df[pos_col].fillna(0) == 1) & _is_symb
        ).astype(int)
        # fix(omni-g-runner-10): 方法 A 分母同域计数 (正面 ∧ 实质性已测量)
        washing_cols[f'_svd_pos{track}'] = (
            (df[pos_col].fillna(0) == 1) & _subst_measured
        ).astype(int)

        # --- 方法 B: 反向验证 (负面 ∧ 实质性) ---
        # 学术依据: Deephouse, D.L. (2000). Media reputation as a strategic
        #   resource. Journal of Management, 26(6), 1091-1112.
        #   https://doi.org/10.1177/014920630002600602
        if neg_col in df.columns and _is_sub is not None:
            washing_cols[f'_is_neg_sub{track}'] = (
                (df[neg_col].fillna(0) == 1) & _is_sub
            ).astype(int)
            # fix(omni-g-runner-10): 方法 B 分母同域计数
            washing_cols[f'_svd_neg{track}'] = (
                (df[neg_col].fillna(0) == 1) & _subst_measured
            ).astype(int)

        # --- 方法 A2: 单个 LLM (Loughran & McDonald 2016, JAR) ---
        for llm in LLM_MODELS:
            src_col = f'{llm}_score{track}'
            if src_col in df.columns:
                # v6/F2: per-model score 是 nullable Int8，NaN 等价于"模型缺席"
                _src = df[src_col].fillna(0)
                _llm_pos = (_src > 0)
                washing_cols[f'_is_{llm}_positive{track}'] = _llm_pos.astype(int)
                washing_cols[f'_is_{llm}_pos_symb{track}'] = (
                    _llm_pos & _is_symb).astype(int)
                # fix(omni-g-runner-14): 方法 A2 分母同域计数
                washing_cols[f'_svd_{llm}_pos{track}'] = (
                    _llm_pos & _subst_measured).astype(int)
                # negative 编码 (Garcia 2013, JF → disag 输入)
                washing_cols[f'_is_{llm}_negative{track}'] = (_src < 0).astype(int)

        # --- 方法 D: 词典均值 (Loughran & McDonald 2011, JF) ---
        _dict_cols = [f'{d}_score{track}' for d in DICT_NAMES
                      if f'{d}_score{track}' in df.columns]
        if _dict_cols:
            _dict_avg = df[_dict_cols].mean(axis=1)
            _dict_pos = (_dict_avg > 0)
            washing_cols[f'_dict_avg_score{track}'] = _dict_avg
            washing_cols[f'_is_dict_positive{track}'] = _dict_pos.astype(int)
            washing_cols[f'_is_dict_pos_symb{track}'] = (
                _dict_pos & _is_symb).astype(int)
            # fix(omni-g-runner-14): 方法 D 分母同域计数
            washing_cols[f'_svd_dict_pos{track}'] = (
                _dict_pos & _subst_measured).astype(int)

        # --- 方法 D2: 单个词典 (Gentzkow et al. 2019, JEL) ---
        for d in DICT_NAMES:
            src_col = f'{d}_score{track}'
            if src_col in df.columns:
                _d_pos = (df[src_col] > 0)
                washing_cols[f'_is_{d}_positive{track}'] = _d_pos.astype(int)
                washing_cols[f'_is_{d}_pos_symb{track}'] = (
                    _d_pos & _is_symb).astype(int)
                # fix(omni-g-runner-14): 方法 D2 分母同域计数
                washing_cols[f'_svd_{d}_pos{track}'] = (
                    _d_pos & _subst_measured).astype(int)
                # negative 编码 (Garcia 2013, JF → disag 输入)
                washing_cols[f'_is_{d}_negative{track}'] = (
                    df[src_col] < 0).astype(int)

        # --- 方法 E/E2 共用: 逐 BERT argmax 极性指示 ---
        # fix(omni-g-runner-01, 2026-06-11): 旧实现等权平均 2-class 与 3-class 模型的
        # 裸 P(正面) 后统一 0.5 二值化 — 跨类数概率尺度不可比 (盘上 _bert_avg 被
        # finbert2 的 2-class 尺度主导, E2 的 0.5 阈值对 3-class 远严于 argmax,
        # disag 输入被尺度差污染)。统一为逐模型 argmax 标签 (类数不变量, 见
        # _bert_argmax_pos_neg), E 改为模型间 argmax 多数票。
        _bert_pos_by_model = {}
        _bert_neg_by_model = {}
        for b in BERT_MODELS:
            if f'{b}_正面{track}' not in df.columns:
                continue
            _bp, _bn = _bert_argmax_pos_neg(df, b, track)
            _bert_pos_by_model[b] = _bp
            _bert_neg_by_model[b] = _bn

        # --- 方法 E: BERT 均值 (Huang et al. 2023, CAR) — argmax 多数票 ---
        if _bert_pos_by_model:
            # _bert_avg 现语义 = 投正面 (argmax) 的模型占比 (尺度不变), 多数票 > 0.5
            _bert_avg = (pd.concat(_bert_pos_by_model.values(), axis=1)
                         .astype(float).mean(axis=1))
            _bert_pos = (_bert_avg > 0.5)
            washing_cols[f'_bert_avg_pos{track}'] = _bert_avg
            washing_cols[f'_is_bert_positive{track}'] = _bert_pos.astype(int)
            washing_cols[f'_is_bert_pos_symb{track}'] = (
                _bert_pos & _is_symb).astype(int)
            # fix(omni-g-runner-14): 方法 E 分母同域计数
            washing_cols[f'_svd_bert_pos{track}'] = (
                _bert_pos & _subst_measured).astype(int)

        # --- 方法 E2: 单个 BERT — argmax 标签 (fix(omni-g-runner-01)) ---
        for b, _b_pos in _bert_pos_by_model.items():
            washing_cols[f'_is_{b}_positive{track}'] = _b_pos.astype(int)
            washing_cols[f'_is_{b}_pos_symb{track}'] = (
                _b_pos & _is_symb).astype(int)
            # fix(omni-g-runner-14): 方法 E2 分母同域计数
            washing_cols[f'_svd_{b}_pos{track}'] = (
                _b_pos & _subst_measured).astype(int)
            # negative 编码 (Garcia 2013, JF → disag 输入)
            _b_neg = _bert_neg_by_model[b]
            if _b_neg is not None:
                washing_cols[f'_is_{b}_negative{track}'] = _b_neg.astype(int)

        # --- 方法 F: 高置信度子样本 (Shapiro et al. 2022, JoE) ---
        agr_col = f'llm_agreement_rate{track}'
        if agr_col in df.columns:
            # fix(omni-g-runner-05/g-runner-09, 2026-06-11): 0.67 → 2/3 - 1e-9,
            # 使唯一多数票档 2/3 (=0.6667) 按声明的 "≥ 2/3" 构念纳入 HC 子样本
            # (旧阈值把该档整类静默排除, _hc 退化为全票一致)。
            _hc = df[agr_col].fillna(0) >= HC_AGREEMENT_THRESHOLD
            # v6/F2: pos_col nullable Int8 → fillna(0)
            washing_cols[f'_is_pos_hc{track}'] = (
                (df[pos_col].fillna(0) == 1) & _hc).astype(int)
            washing_cols[f'_is_pos_symb_hc{track}'] = (
                (df[pos_col].fillna(0) == 1) & _is_symb & _hc
            ).astype(int)
            # fix(omni-g-runner-10): 方法 F 分母同域计数
            washing_cols[f'_svd_pos_hc{track}'] = (
                (df[pos_col].fillna(0) == 1) & _hc & _subst_measured
            ).astype(int)


    # ── v3.2.0 M2 P3 (plan v14 §2.3 + Action #5 count 4-way) ──
    # Sentiment × Substantiveness 笛卡尔积: 现有列 = sentiment{track} × subst_full (隐式 _sf),
    # 此处追加 sentiment{track} × subst_ctx (_sc) 完成 4-way.
    # 文献依据: Bingler et al. (2022 FRL) cheap talk 定义在 disclosure-segment 邻近;
    # 4-way 让论文 Robustness Appendix 可呈现"main spec switch sensitivity" 4 specs.
    _tt_ctx = df['innovation_substantiveness_ctx'].astype(str).str.strip() if 'innovation_substantiveness_ctx' in df.columns else None
    _is_symb_ctx = (_tt_ctx == '象征性') if _tt_ctx is not None else None
    _is_sub_ctx  = (_tt_ctx == '实质性') if _tt_ctx is not None else None

    if _is_symb_ctx is not None:
        for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
            pos_col = f'is_positive{track}'
            neg_col = f'is_negative{track}'
            if pos_col not in df.columns:
                continue

            # 方法 A (4-way): _is_pos_symb_<sent_track>_sc
            washing_cols[f'_is_pos_symb{track}_sc'] = (
                (df[pos_col].fillna(0) == 1) & _is_symb_ctx
            ).astype(int)

            # 方法 B (4-way): _is_neg_sub_<sent_track>_sc
            if neg_col in df.columns and _is_sub_ctx is not None:
                washing_cols[f'_is_neg_sub{track}_sc'] = (
                    (df[neg_col].fillna(0) == 1) & _is_sub_ctx
                ).astype(int)

            # 方法 A2 逐 LLM (4-way) — 不重复 _is_{llm}_positive (已存在)
            for llm in LLM_MODELS:
                src_col = f'{llm}_score{track}'
                if src_col in df.columns:
                    _llm_pos = (df[src_col].fillna(0) > 0)
                    washing_cols[f'_is_{llm}_pos_symb{track}_sc'] = (
                        _llm_pos & _is_symb_ctx).astype(int)

            # 方法 F (4-way): HC × subst_ctx
            agr_col = f'llm_agreement_rate{track}'
            if agr_col in df.columns:
                # fix(omni-g-runner-05/g-runner-09): 与主洗稿循环同步 2/3 - 1e-9
                _hc = df[agr_col].fillna(0) >= HC_AGREEMENT_THRESHOLD
                washing_cols[f'_is_pos_symb_hc{track}_sc'] = (
                    (df[pos_col].fillna(0) == 1) & _is_symb_ctx & _hc
                ).astype(int)

    df = _append_columns(df, washing_cols)


    _wr_flag_cols = [c for c in df.columns if c.startswith('_is_')]
    logger.info(f"  洗稿率前置列生成完毕: {len(_wr_flag_cols)} 列 (三轨 full/ctx/ss)")

    # --- 4z. BERT 概率分布形状: 逐篇中间列 (2026-07-03 执行计划) ---
    # WP-A 熵 / WP-B 极端负面指示 / WP-C 逐篇净语调 + WP-D 跨模型分歧双轨,
    # 由叶模块 bert_distribution 计算 (模型清单参数注入, 防循环导入), 一次性
    # concat 并入 (防 fragmentation)。聚合条目由 encode.build_aggregation_dict
    # 经 iter_agg_entries 无条件注册, 缺源 valid_agg 过滤。中间列 (非 `_is_`
    # 前缀, 不被 6c sweep 清理) **仅被步骤 5 aggregate_panel 消费** (WP-E 从
    # 概率列重算 nt, 不依赖 `_nt_art_*`, 终审 F2 勘误); 存活至步骤 9 前统一
    # drop 是单点挂载取舍 (省的内存 < 双 call site 维护漂移风险)。
    _bd_cols = bert_distribution.compute_article_distribution_cols(
        df, BERT_MODELS, THREE_CLASS_MODELS)
    _bd_cols.update(bert_distribution.compute_xmodel_dispersion(df, BERT_MODELS))
    if _bd_cols:
        df = _append_columns(df, _bd_cols)
    logger.info(f"  BERT 分布形状逐篇中间列: {len(_bd_cols)} 列 "
                f"(声明全集 {len(bert_distribution.iter_intermediate_cols(BERT_MODELS))}, "
                f"差额=概率源列合法缺席轨)")

    # --- 5. Bank-Year 聚合 (df 为只读: groupby/filter/merge) ---
    _t_agg = time.time()
    panel = aggregate_panel(df)

    # fix(omni-g-runner-10/g-runner-14, 2026-06-11): _svd_* subst-valid 分母计数
    # 聚合并入 (encode.build_aggregation_dict 属 g-encode 组文件, runner 内自聚合;
    # 步骤 7h 洗稿率除法消费这些同域分母)。
    _svd_panel = _pool_svd_substvalid_counts(df)
    if _svd_panel is not None:
        panel = panel.merge(_svd_panel, on=['target_bank', 'year'], how='left')
        logger.info(f"  subst-valid 分母计数已合并: {len(_svd_panel.columns) - 2} 列")

    # 引用转移: aggregate_panel 已完成, 后续全部使用 df_exploded
    df_exploded = df
    del df  # 防止后续误用, 对象由 df_exploded 持有不会被回收

    # --- 6. 面板平衡 ---
    panel = balance_panel(panel)

    # 去碎片化: aggregate_panel + balance_panel 经多次单列插入后 DataFrame 高度碎片化,
    # 下方 has_coverage 等单列赋值会触发 pandas PerformanceWarning。copy() 合并内存块,
    # 不改数据/列序/取值, 仅消除非预期告警 (audit 2026-05-30)。
    panel = panel.copy()

    phase_durations['③聚合+平衡 aggregate/balance_panel'] = time.time() - _t_agg

    # --- 6a. has_coverage 哑变量 ---
    panel['has_coverage'] = (panel['n_articles'] > 0).astype(int)
    logger.info(f"  has_coverage: 有报道={panel['has_coverage'].sum()}, "
                f"无报道={len(panel) - panel['has_coverage'].sum()}")

    _t_attn = time.time()

    # --- 6b. 金融科技注意力指数 (三级地理: 年/省/市) ---
    # 每档并行产 比值 ft_attn_* (fintech/total, intensive 份额) 与 总量 ft_vol_*
    #   (ln(1+fintech 篇数), extensive 规模) 互为稳健性 (2026-06-13)。
    # ⚠️ 必须在 balance_panel() 之后调用 (确保完全笛卡尔积)
    # ⚠️ 不使用 df_exploded (仅含 fintech 文章), 而是直接读取
    #    12_fintech_news_full.parquet (含全量银行新闻)
    panel = compute_fintech_attention_index(panel)

    # --- 6b-2. P2 attention 处理变量 (Fang-Peress 2009 JF extensive 覆盖加权曝光;
    #     Hassan 2019 QJE 仅限 pct/density/ctx 归因 — fix(omni-g-papers-misc-09, 2026-06-11)
    #     锚点更正, 同步 attention_media.py docstring; 三轨 (full/ctx/ss)=互为稳健性) ---
    # spec 钦定 attention_index_full/ctx/ss + attention_pct_full + attention_disp_full +
    # 三轨派生 (density/sd/gap/share)。防选择偏差: 全集脊柱 LEFT-join + 零-fintech 填 0 (index/pct)。
    panel = compute_attention_treatments(panel)

    # --- 6b-3. 去重阈值敏感性处理变量 (Tetlock 2011 RFS; Hassan 2019 QJE) ---
    # 严格方向网格 (J×W) 在 12_full 文章全集上追加判重 → 重算 index/pct/计数,
    # 每变体 5 列 (_j70w5 等)。宽松方向需从 raw 重跑 stage 00, 模块 docstring 披露。
    panel = compute_dedup_sensitivity_treatments(panel)

    # --- 6c. 媒体异质性变量 (四维度) ---
    panel = compute_media_heterogeneity(df_exploded, panel)

    # --- 7. 综合指标 ---
    panel = compute_composite_indicators(panel)

    # --- 7b. 年度截面标准化 ---
    panel = standardize_panel_variables(panel)

    # --- 7c. 银行注册地地理信息 ---
    # 从 bank_addresses.json 合并省份和城市, 用于:
    #   (1) 省级/城市级聚类标准误 (Luo & Li 2025, Table A.2)
    #   (2) 步骤 7d leave-one-out IV 的前置依赖
    panel = merge_bank_geography(panel)

    # --- 7d. Leave-one-out 地理平均情感 (IV) ---
    # 构建同省/同城市其他银行的平均情感 → 工具变量
    # (Luo & Li 2025, Table 3: Province_news_sentiment)
    panel = compute_leave_one_out_sentiment(panel)

    # --- 7d-geo. 四梯度地理距离缓冲 (Gurun & Butler 2012; Engelberg & Parsons 2011) ---
    # P0-2 (cleanup/2026-05-13): try/hasattr/except 三明治改为直调.
    # 实证: 两函数均在 geography.py 中定义 (line 749 / 974), fallback 路径从未触发.
    # 计算异常应 propagate, 而非 silent warning 让 panel 缺地理列.
    panel = _m43.compute_geo_proximity_buffers(df_exploded, panel)

    # --- 7d-imit. 区域 AI 模仿渗透率 (六层 LOO, Leary & Roberts 2014) ---
    panel = _m43.compute_regional_imitation_pressure(panel)

    # --- 7e. Bartik IV (v3: 修剪至 6 类核心维度) ---
    # v6/F4 修复 (Goldsmith-Pinkham, Sorkin & Swift 2020, AER):
    #   原 29 套 IV 中 28 类违反 share 在 pre-treatment 期固定外生性公理。
    #   v6 保留 6 类：
    #     - type / scale  : 银行属性（pre-treatment 固定）
    #     - fintech       : LLM 主题分类（须配合论证）
    #     - media         : 媒体三方类型（fin/comp/other，pre-treatment 媒体属性）
    #     - geoprox       : 银行注册地 vs 媒体省份地理邻近性
    #     - mauth         : 媒体权威性档位（high/mid/low）
    #   删除 28 类的内生性 IV（doclen/kwdiv/kwden/mden/sentlen/ttr/author/
    #   page/pgnum/half/qtr/month/wkday/excl/title/mcount/mcentral/mfin/
    #   mcomp/mofficial/mmarket/mfreq/mdeep/mdaily/mprov/breadth/pubfmt等）。
    #   IV 数量 ≥ 6 类 → 论文主表强制使用 Romano-Wolf step-down p 值校正。
    # 基期约束 (v6/F4-3): bartik_base_year = max(panel.year.min(), 2010)；
    #   若计算所得基期 ≥ 2019 (DCEP 沙盒里程碑) 强制抛错。
    logger.info("=" * 60)
    logger.info("步骤 7e: Bartik Shift-Share IV (v3: 6 类核心)")
    logger.info("=" * 60)
    type_map, scale_map = load_bank_group_maps()
    # v6/F4-3 基期参数化：取 panel 起始年与 2010 中较晚者；强制 < 2019
    _bartik_base_year_cfg = PANEL_CFG.get('bartik_base_year', 'auto')
    _bartik_pre_cutoff = PANEL_CFG.get('bartik_pre_treatment_cutoff', 2019)
    _panel_min = int(panel['year'].min())
    if _bartik_base_year_cfg == 'auto' or _bartik_base_year_cfg is None:
        T0 = max(_panel_min, 2010)
    else:
        T0 = int(_bartik_base_year_cfg)
    if _bartik_pre_cutoff <= T0:
        raise RuntimeError(
            f"Bartik 基期 T0={T0} ≥ 政策冲击里程碑 {_bartik_pre_cutoff}：share "
            f"已在 post-treatment 区间，违反 Goldsmith-Pinkham et al. (2020) "
            f"外生性公理。请检查 panel.yaml::panel_building.bartik_base_year 设置。"
        )
    logger.info(f"  Bartik 基期: T0={T0} (panel.year.min={_panel_min}, "
                f"cfg={_bartik_base_year_cfg}, cutoff={_bartik_pre_cutoff})")

    # --- 主 Bartik: 银行类型 (6类, 5有效IV) ---
    # v3: 显式传基期 T0
    panel = compute_bartik_iv(panel, df_exploded, type_map, 'type',
                               base_year=T0)
    # 基期敏感性 (T0, T0+1, T0&T0+1) — 检验 IV 对基期选择的稳健性
    # ⚠️ 使用 merge-based 赋值，避免 .values 行序错配
    for suffix, base_yr in [('_t0', T0), ('_t1', T0+1)]:
        # fix(omni-g-runner-04, 2026-06-11): _t1 基期外生性守卫 — 主 IV 仅检
        # T0 < cutoff, _t1 基期=T0+1 可落入 post-treatment 区间 (panel 起始
        # 2018 时 _t1 基期=2019 绕过红线)。基期 ≥ cutoff → 该敏感性变体置
        # NaN 并告警 (share 已在 post-treatment, 违反 GPSS 2020 公理)。
        if base_yr >= _bartik_pre_cutoff:
            logger.warning(
                f"  Bartik {suffix} 变体基期 {base_yr} ≥ 政策冲击里程碑 "
                f"{_bartik_pre_cutoff}, 违反外生性公理 → 置 NaN 跳过 "
                f"(fix(omni-g-runner-04))")
            for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
                panel[f'bartik_type_iv{track}{suffix}'] = np.nan
            continue
        ptmp = compute_bartik_iv(panel[['target_bank', 'year']].copy(),
                                 df_exploded, type_map, 'type',
                                 base_year=base_yr)
        for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
            src_col = f'bartik_type_iv{track}'
            dst_col = f'bartik_type_iv{track}{suffix}'
            ptmp = ptmp.rename(columns={src_col: dst_col})
        # fix(bartik-ss-merge-parity, 2026-06-25): merge-select 改为程序化三轨列表,
        # 补回 _ss 轨。此前只回选 full/ctx → 上面 rename 循环造出的
        # bartik_type_iv_ss{suffix} 被丢弃 (死计算 + 三轨平价破坏); v3.9.0 引入 _ss
        # 时漏改 merge-select (git blame 实证)。与上方 rename 循环同序三轨。
        _bartik_sel = ['target_bank', 'year'] + [
            f'bartik_type_iv{track}{suffix}' for track in ('_full', '_ctx', '_ss')]
        panel = panel.merge(
            ptmp[_bartik_sel],
            on=['target_bank', 'year'], how='left')
    # fix(omni-g-runner-04, 2026-06-11): 真·池化基期 _t01 — 旧实现把 {T0,T0+1}
    # 年份子集当全量文章传入, 而 compute_bartik_iv 内部 share 仍只取 year==T0
    # (池化从未发生, _t01 与 _t0 字节级相同的幻影变体); 且 shift 聚合域被截断
    # 到基期两年, 其余年份 shift NaN 经旧 fillna(0) 制成 IV 精确伪零。改为传
    # 全量 df_exploded + base_years=[T0, T0+1] (iv_did 池化基期接口,
    # fix(omni-g-ivdid-02) 实现)。池化基期含 T0+1 → 同样受 cutoff 外生性守卫。
    if _bartik_pre_cutoff <= T0 + 1:
        logger.warning(
            f"  Bartik _t01 池化基期含 {T0 + 1} ≥ 政策冲击里程碑 "
            f"{_bartik_pre_cutoff}, 违反外生性公理 → 置 NaN 跳过 "
            f"(fix(omni-g-runner-04))")
        for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
            panel[f'bartik_type_iv{track}_t01'] = np.nan
    else:
        ptmp = compute_bartik_iv(panel[['target_bank', 'year']].copy(),
                                 df_exploded, type_map, 'type',
                                 base_years=[T0, T0 + 1])
        for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
            src_col = f'bartik_type_iv{track}'
            ptmp = ptmp.rename(columns={src_col: f'bartik_type_iv{track}_t01'})
        # fix(bartik-ss-merge-parity, 2026-06-25): 同上, _t01 池化基期 merge-select 补回
        # _ss 轨 (此前丢弃 bartik_type_iv_ss_t01)。
        _bartik_sel_t01 = ['target_bank', 'year'] + [
            f'bartik_type_iv{track}_t01' for track in ('_full', '_ctx', '_ss')]
        panel = panel.merge(
            ptmp[_bartik_sel_t01],
            on=['target_bank', 'year'], how='left')

    # --- 稳健性 1: 银行规模 (4类, 3有效IV) — v3: 显式基期 T0 ---
    panel = compute_bartik_iv(panel, df_exploded, scale_map, 'scale',
                               base_year=T0)

    # --- 7e-digfront. 数字化前沿距离代理变量 ---
    # 按同类型银行【基年】中位数新闻覆盖量划分一次, 组员资格跨年固定
    # (仅基年有新闻覆盖的银行参与切分; 基年零覆盖 → 0)
    # 概念迁移自:
    #   Goldfarb, A. & Tucker, C. (2019). Digital economics.
    #   Journal of Economic Literature, 57(1), 3-43.
    #   https://doi.org/10.1257/jel.20171452
    # 用途: DDD 三重差分 — 数字化前沿 × 政策冲击 (步骤 7g 后构建)
    # fix(omni-g-runner-12, 2026-06-11): 旧实现按【同年】中位数切分, frontier
    # 身份逐年随内生覆盖量翻转 (盘上 43/87 银行 2017→2018 翻转), post 期身份由
    # post 期自身实现值决定 — 与上方 Bartik 的 pre-treatment 固定公理 (GPSS
    # 2020 AER) 自相矛盾。改为 pre-period 固定切分 (见 _base_year_median_split)。
    if 'bank_type' in panel.columns:
        panel['digital_frontier'] = _base_year_median_split(
            panel, value_col='n_articles', by='bank_type')
        logger.info(f"  digital_frontier (基年 {int(panel['year'].min())} "
                    f"固定切分): "
                    f"1={panel['digital_frontier'].sum()}, "
                    f"0={(panel['digital_frontier'] == 0).sum()}")
    else:
        logger.warning("  bank_type 不存在, 跳过 digital_frontier 构建")

    # --- 稳健性 2: 金融科技类型 (2类, 1有效IV) — v3: 显式基期 T0 ---
    # 注意: innovation_locus_full (v7, 原 fintech_category) 由 LLM 决定，须配合论证 (v6/F4-2 须论证清单)
    # v3.2.0 M3 P4 (plan v14 §3.4): Bartik IV 双套独立
    #   - bartik_fintech_lf_*: share = innovation_locus_full 基期占比 (与 Sautner 2023 JF 不同框架)
    #   - bartik_fintech_lc_*: share = innovation_locus_ctx 基期占比 (Hassan 2019 QJE entity-proximity)
    # 论文用法: main spec 选 _lf 或 _lc 之一 (Methods §4 决定), 另一作 robustness
    fintech_map = {'底层技术': 'tech', '应用场景': 'app'}
    panel = compute_bartik_iv_fintech(panel, df_exploded, fintech_map, 'fintech_lf',
                                      base_year=T0,
                                      category_col='innovation_locus_full')
    if 'innovation_locus_ctx' in df_exploded.columns:
        panel = compute_bartik_iv_fintech(panel, df_exploded, fintech_map, 'fintech_lc',
                                          base_year=T0,
                                          category_col='innovation_locus_ctx')
    else:
        logger.warning("  innovation_locus_ctx 不存在, 跳过 lc Bartik IV (M2 P2 加性后应已存在)")

    # --- 稳健性 3: 媒体三方分类 Bartik (财经/综合/其他) ---
    # v6/F4: 仅保留 3a 三方分类。删除 3b/3c/3d/3e/3f/3g/3h/3i 等 8 类
    #   二分变体（文献依据：与 3a 高度相关，且二分组对处理变量的外生性
    #   通道未在文献中独立验证；删除以避免 multiple testing inflation）。
    # 学术依据 Snyder & Strömberg (2010, JPE 118(2)) — 媒体类型分布在
    #   pre-treatment 期固定时可作为 share。
    cls_path = CONFIG['paths'].get(
        'media_classification_file',
        os.path.join(os.path.dirname(__file__),
                     'config', 'media_classification.json'),
    )
    if os.path.exists(cls_path):
        with open(cls_path, 'r', encoding='utf-8') as f:
            media_cls = json.load(f)
        FIN = set(media_cls.get('financial_media', []))
        COMP = set(media_cls.get('comprehensive_media', []))
        media_col = '媒体(中文)'

        if '_media_type' not in df_exploded.columns:
            df_exploded = _append_columns(df_exploded, {
                '_media_type': df_exploded[media_col].apply(
                    lambda x: 'fin' if x in FIN else ('comp' if x in COMP else 'other')
                )
            })
        media_map = {'fin': 'fin', 'comp': 'comp', 'other': 'other'}
        panel = compute_bartik_iv_fintech(
            panel, df_exploded, media_map, 'media',
            base_year=T0,
            category_col='_media_type'
        )
        logger.info(f"  媒体分类 Bartik: 3a(fin/comp/other) — v6 仅保留三方")
    else:
        logger.warning("  media_classification.json 不存在, 跳过媒体分类 Bartik")

    # --- 稳健性 4: 媒体权威性 (Holzman et al. 2023, TAR) ---
    # v6/F4: 保留。媒体权威性档位由 media_weights.json 评分决定，
    #   档位划分 (high≥80 / mid≥60 / low) 在 pre-treatment 期固定。
    # Phase 1 重构: 优先读取 CONFIG['paths']['media_weights_file']。
    mw_path = CONFIG['paths'].get(
        'media_weights_file',
        os.path.join(os.path.dirname(__file__),
                     'config', 'media_weights.json'),
    )
    if os.path.exists(mw_path):
        with open(mw_path, 'r', encoding='utf-8') as f:
            mw = json.load(f)
        mw = {k: v for k, v in mw.items() if not k.startswith('//')}
        media_col = '媒体(中文)'
        if '_media_authority' in df_exploded.columns:
            df_exploded = df_exploded.drop(columns=['_media_authority'])
        df_exploded = _append_columns(df_exploded, {
            '_media_authority': df_exploded[media_col].apply(
                lambda x: 'high' if mw.get(x, 10) >= 80
                else ('mid' if mw.get(x, 10) >= 60 else 'low')
            )
        })
        mauth_map = {'high': 'high', 'mid': 'mid', 'low': 'low'}
        panel = compute_bartik_iv_fintech(
            panel, df_exploded, mauth_map, 'mauth',
            base_year=T0,
            category_col='_media_authority'
        )
    else:
        logger.warning("  media_weights.json 不存在, 跳过媒体权威性 Bartik")

    # --- 稳健性 5: 地理邻近性 (Engelberg & Parsons 2011, JF) ---
    # v6/F4: 保留。银行注册地 pre-treatment 固定，媒体省份是文章属性，
    #   两者交叉的二分变量 (local/nonlocal) 在 pre-treatment 期固定。
    media_prov_col = '国家地区/省份'
    if media_prov_col in df_exploded.columns:
        addr_path = CONFIG['paths'].get(
            'bank_addresses_file',
            os.path.join(os.path.dirname(__file__),
                         'config', 'bank_addresses.json'),
        )
        if os.path.exists(addr_path):
            with open(addr_path, 'r', encoding='utf-8') as f:
                _addr = json.load(f)
            _prov_map = {k: v.get('province', '') for k, v in _addr.items()}
            _bank_prov = df_exploded['target_bank'].map(_prov_map)
            df_exploded = df_exploded.drop(
                columns=[c for c in ['_bank_prov', '_geo_proximity']
                         if c in df_exploded.columns]
            )
            df_exploded = _append_columns(df_exploded, {
                '_bank_prov': _bank_prov,
                '_geo_proximity': np.where(
                    df_exploded[media_prov_col] == _bank_prov,
                    'local', 'nonlocal'
                )
            })
            geoprox_map = {'local': 'local', 'nonlocal': 'nonlocal'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, geoprox_map, 'geoprox',
                base_year=T0,
                category_col='_geo_proximity'
            )

    # ============================================================
    # v6/F4 删除清单 (28 类违反外生性公理的 IV，已从 panel 输出移除)
    # ------------------------------------------------------------
    # 删除原因 (Goldsmith-Pinkham, Sorkin & Swift 2020, AER §2):
    #   share 必须在 pre-treatment 期固定且独立于结果变量。
    #   下列 IV 维度均违反此约束：
    #     - doclen / kwdiv / kwden / mden / sentlen / ttr
    #         → 文章特征是结果变量属性 (post-treatment article-level)
    #     - author / page / pgnum
    #         → 编辑事后决策 (post-treatment editorial decisions)
    #     - half / qtr / month / wkday
    #         → 时间切分与处理变量无清晰因果通道
    #     - excl / title / mcount
    #         → 编辑事后决策 + 直接结果变量
    #     - mcentral / mfin / mcomp / mofficial / mmarket /
    #       mfreq / mdeep / mdaily
    #         → 媒体类型二分组与已保留的三方分类 (media) 高度相关，
    #           multiple testing 通胀；删除以避免 p-hacking
    #     - mprov
    #         → 媒体省份与 geoprox 已保留的二分形式相关
    #     - breadth / pubfmt
    #         → 与 media / mauth 已保留维度高度相关
    # ============================================================
    logger.info(f"  Bartik IV (v6 修剪版): 6 类核心维度已完成 "
                f"(type/scale/fintech/media/geoprox/mauth)")

    # --- 7f. 经济圈 Leave-One-Out IV ---
    logger.info("=" * 60)
    logger.info("步骤 7f: 经济圈 Leave-One-Out IV")
    logger.info("=" * 60)
    panel = compute_zone_leave1out(panel, df_exploded)

    # --- 7g. DID 政策冲击变量 ---
    logger.info("=" * 60)
    logger.info("步骤 7g: DID 政策冲击变量 (DCEP + Sandbox)")
    logger.info("=" * 60)
    panel = merge_policy_shocks(panel)

    # =========================================================================
    # 步骤 7g-het: 异质性分析交互项预计算
    # =========================================================================
    # 总体学术依据:
    #   Angrist, J.D. & Pischke, J.-S. (2009). Mostly Harmless Econometrics:
    #   An Empiricist's Companion. Princeton University Press.
    #   https://doi.org/10.1515/9781400829828
    #   → §3.4.2: 交互项优于中介回归，避免"Bad Controls"问题
    #
    #   Brambor, T., Clark, W.R. & Golder, M. (2006). Understanding interaction
    #   models: Improving empirical analyses. Political Analysis, 14(1), 63-82.
    #   https://doi.org/10.1093/pan/mpi014
    #   → 交互项模型中主效应 (constituent terms) 必须同时进入回归，否则系数有偏
    # =========================================================================
    logger.info("=" * 60)
    logger.info("步骤 7g-het: 异质性分析交互项预计算")
    logger.info("=" * 60)

    # --- (a) SOE 哑变量 ---
    # bank_type 由步骤 7e compute_bartik_iv() 生成
    if 'bank_type' in panel.columns:
        panel['is_soe'] = (panel['bank_type'] == 'soe').astype(int)
        logger.info(f"  is_soe: SOE={panel['is_soe'].sum()}, "
                    f"非SOE={(panel['is_soe'] == 0).sum()}")
    else:
        logger.warning("  bank_type 不存在, is_soe 设为 0")
        panel['is_soe'] = 0

    # --- (b) bank_scale 有序编码 ---
    # scale_map: 'L'/'M'/'S'/'XS'/'other' (44_panel_iv_did.py L58-59)
    scale_map_ord = {'XS': 1, 'S': 2, 'M': 3, 'L': 4}
    if 'bank_scale' in panel.columns:
        panel['bank_scale_ord'] = panel['bank_scale'].map(
            scale_map_ord).fillna(0).astype(int)
        logger.info(f"  bank_scale_ord 分布: "
                    f"{panel['bank_scale_ord'].value_counts().sort_index().to_dict()}")
    else:
        logger.warning("  bank_scale 不存在, bank_scale_ord 设为 0")
        panel['bank_scale_ord'] = 0

    # --- (c) 覆盖强度分组 (替代二元 has_coverage) ---
    # 仅在基年有新闻覆盖的银行中按【基年】中位数分组一次, 跨年固定
    # 学术依据:
    #   Fang, L.H. & Peress, J. (2009). Media coverage and the cross-section
    #   of stock returns. Journal of Finance, 64(5), 2023-2052.
    #   https://doi.org/10.1111/j.1540-6261.2009.01493.x
    #   → 媒体覆盖的边际效应递减，需区分高低覆盖强度; 原文用 t 期覆盖排序
    #     预测 t+1 收益 (predetermined sort)
    # ⚠️ 注意: 原始 has_coverage (0/1) 与 tone 的交互项无额外信息 (冗余):
    #   零新闻行 tone=NaN → tone×has_coverage=NaN (非0);
    #   有新闻行 tone×1=tone → 交互项退化为 tone 本身，无增量信息
    # fix(omni-g-runner-13, 2026-06-11): 旧实现按【同年】中位数切分 (含自身观测),
    # 组员资格逐年随内生覆盖量翻转 (盘上 20/87 银行跨年翻转), 与同年 tone 相乘
    # 进回归 — 调节变量与 outcome 完全同期内生。改为 pre-period 固定切分
    # (面板最早年中位数, 见 _base_year_median_split), 对齐 predetermined 口径。
    panel['high_coverage'] = _base_year_median_split(
        panel, value_col='n_articles', by=None)
    logger.info(f"  high_coverage (基年 {int(panel['year'].min())} 固定切分): "
                f"1={panel['high_coverage'].sum()}, "
                f"0={(panel['high_coverage'] == 0).sum()}")

    # --- (d) 交互项构建 (三轨: _full + _ctx + _ss) ---
    het_count = 0
    for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
        tone = f'llm_vote_tone{track}'
        if tone not in panel.columns:
            continue
        panel[f'tone_x_soe{track}'] = panel[tone] * panel['is_soe']
        panel[f'tone_x_scale{track}'] = panel[tone] * panel['bank_scale_ord']
        panel[f'tone_x_highcov{track}'] = panel[tone] * panel['high_coverage']
        het_count += 3
    logger.info(f"  已生成 {het_count} 个异质性交互项 (Tone × SOE/Scale/HighCov)")

    # --- (e) DDD 三重差分交互项 ---
    # 学术依据:
    #   Wooldridge, J.M. (2010). Econometric Analysis of Cross Section and
    #   Panel Data (2nd ed.). MIT Press. ISBN: 978-0-262-23258-6
    #   → §10.4: 三重差分要求 Stata 中同时纳入所有低阶交互项 (## 语法自动满足)
    ddd_count = 0
    for prefix in ['dcep', 'sandbox']:
        t_col, p_col = f'{prefix}_treated', f'{prefix}_post'
        if (t_col in panel.columns and p_col in panel.columns
                and 'digital_frontier' in panel.columns):
            panel[f'{prefix}_ddd_digfront'] = (
                panel[t_col] * panel[p_col] * panel['digital_frontier']
            )
            ddd_count += 1
    if ddd_count > 0:
        logger.info(f"  已生成 {ddd_count} 个 DDD 三重差分交互项 "
                    f"(Treated × Post × DigFrontier)")
    else:
        logger.info("  DDD 交互项跳过 (DID 变量或 digital_frontier 不存在)")

    # --- (f) 银行业压力期非对称效应 ---
    # 学术依据:
    #   García, D. (2013). Sentiment during recessions. Journal of Finance,
    #   68(3), 1267-1300. https://doi.org/10.1111/jofi.12027
    #   → 衰退/压力期间情感指标的统计特征显著不同于常规期
    # 压力年份定义与 51_falsification_test.py L897-899 一致
    STRESS_YEARS = {2015, 2018, 2020}  # 股灾、去杠杆、疫情
    panel['stress_period'] = panel['year'].isin(STRESS_YEARS).astype(int)
    stress_count = 0
    for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
        tone = f'llm_vote_tone{track}'
        if tone in panel.columns:
            panel[f'tone_x_stress{track}'] = panel[tone] * panel['stress_period']
            stress_count += 1
    logger.info(f"  stress_period: 压力年={panel['stress_period'].sum()}, "
                f"常规年={(panel['stress_period'] == 0).sum()} "
                f"({stress_count} 个交互项)")

    # --- (g) 存款保险制度时间断点调节项 ---
    # 《存款保险条例》(国务院令第660号) 2015.05.01 全国统一施行
    # 设计: 时间断点调节项, 非 DID (全国统一实施, 无处理/控制分组)
    # ⚠️ 不可通过 policy_shocks.json 实现:
    #   merge_policy_shocks() 通过 panel['bank_province'].isin(provs) 匹配,
    #   "全国" 不是有效省份名 (44_panel_iv_did.py L513-517)
    panel['depins_post'] = (panel['year'] >= 2015).astype(int)
    depins_count = 0
    for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
        tone = f'llm_vote_tone{track}'
        if tone in panel.columns:
            panel[f'tone_x_depins{track}'] = panel[tone] * panel['depins_post']
            depins_count += 1
    logger.info(f"  depins_post: 实施后={panel['depins_post'].sum()}, "
                f"实施前={(panel['depins_post'] == 0).sum()} "
                f"({depins_count} 个交互项)")
    # fix(log-reaudit-2026-06-20, P2-C): 零方差检测 (与 network_brokerage R18 对称)。
    # 早期试跑盘面 T=2 仅 {2017,2018} 全 ≥2015 → depins_post 恒为常量 1, tone_x_depins* 退化为
    # tone×1 无识别力 (下游会被共线性/FE 吸收); 显式告警, 避免被误读为可用时间断点。
    # 生产 T=19 (2007–2025) 跨越 2015 断点后自然有方差, 守卫不触发。
    if panel['depins_post'].nunique() <= 1:
        logger.warning(
            f"  ⚠ depins_post 退化为常量 (唯一值={sorted(panel['depins_post'].unique().tolist())}): "
            f"样本年份未跨越 2015 实施断点 (早期试跑盘面 T=2 常见), tone_x_depins* 交互项零方差、"
            f"下游无识别力; 生产 T=19 跨 2007–2025 后恢复方差。"
        )

    # --- (h) 复合关注度指数 (Concern Score) ---
    # 公式: concern_score = ln_news_coverage × (senti_ratio + 1) / 2
    # 其中 senti_ratio = (neg_count - pos_count) / (neg_count + pos_count) ∈ [-1, 1]
    # → concern_score ∈ [0, ∞): 越高 = 越多负面新闻 + 越多报道量
    # ⚠️ 全中性文章 (pos=neg=0): total_pn=0 → senti_ratio=NaN → concern_score=NaN
    #   (语义合理: 无正/负方向性信息时, 关注度方向未定义)
    concern_count = 0
    for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
        pos_c, neg_c = f'pos_count{track}', f'neg_count{track}'
        if pos_c in panel.columns and neg_c in panel.columns:
            # fix(completeness-03): Int8 计数转 float64 防 (pos+neg)≥128 静默回绕致 senti_ratio
            # 翻符号 (当前 max~100 不触发, 0 值变化; 防御 production)。
            _pos = panel[pos_c].astype('float64')
            _neg = panel[neg_c].astype('float64')
            total_pn = _pos + _neg
            safe_total = total_pn.replace(0, np.nan)
            senti_ratio = (_neg - _pos) / safe_total
            panel[f'concern_score{track}'] = (
                panel['ln_news_coverage'] * (senti_ratio + 1) / 2
            )
            concern_count += 1
    logger.info(f"  已生成 {concern_count} 个 concern_score 变量")

    # --- (i) 情感滞后与反转效应 ---
    # 学术依据:
    #   De Bondt, W.F.M. & Thaler, R. (1985). Does the stock market overreact?
    #   Journal of Finance, 40(3), 793-805.
    #   https://doi.org/10.1111/j.1540-6261.1985.tb05004.x
    #   → 过度反应假说: 前期极端情感 → 后期均值回归/反转
    # ⚠️ balance_panel() 确保面板为完全笛卡尔积 (银行×年份),
    #   shift(1) 不会跳过年份。首年滞后值为 NaN (预期行为)
    panel = panel.sort_values(['target_bank', 'year'])
    lag_count = 0
    for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
        tone = f'llm_vote_tone{track}'
        if tone in panel.columns:
            panel[f'{tone}_lag1'] = panel.groupby('target_bank')[tone].shift(1)
            panel[f'tone_reversal{track}'] = panel[tone] - panel[f'{tone}_lag1']
            lag_count += 2
    logger.info(f"  已生成 {lag_count} 个滞后/反转变量 (lag1 + reversal)")

    # --- (i2) 语调时序波动率 (rolling SD, 批 #11, 2026-06-05) ---
    # 二阶矩补全: 一阶反转 tone_reversal 之外的【时间维】语调不稳定性。与年内跨文章 SD
    # (*_tone_std) / 跨媒体方差 (cross_outlet) 正交 (论文须明写以防冗余质疑)。用
    # 按银行分组的 rolling().std() 范式; window=3,
    # min_periods=2 → ≥2 年即出值, 优雅降级 (全量 T=19 充分, 磁盘早期试跑 T=2 仅末年有值)。
    TONE_VOL_WINDOW, TONE_VOL_MINP = 3, 2
    vol_count = 0
    for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
        tone = f'llm_vote_tone{track}'
        if tone in panel.columns:
            panel[f'tone_volatility{track}'] = (
                panel.groupby('target_bank')[tone]
                .rolling(TONE_VOL_WINDOW, min_periods=TONE_VOL_MINP).std()
                .reset_index(level=0, drop=True)
            )
            vol_count += 1
    logger.info(f"  已生成 {vol_count} 个语调时序波动率变量 (rolling SD, w={TONE_VOL_WINDOW})")

    # --- (i3) 异常/残差语调 (Huang, Teoh & Zhang 2014 TAR "Tone Management"; 批 #15) ---
    # abnormal_tone = tone 对【银行基本面 + 年份 FE】回归后的残差 (剔除基本面可解释部分,
    # 留下"异常"语调). ⚠ 阻塞: 当前面板无银行财务基本面列 (资产/杠杆/ROA/NPL), 须外部 merge
    # CSMAR 年报财务 (非 LLM 付费, 但非现成). 优雅降级: 基本面就位则自动产出 abnormal_tone
    # _{full,ctx} (dormant, 缺则不产列; 批 #15, 2026-06-05)。
    _FUNDAMENTAL_CANDS = ['ln_assets', 'ln_total_assets', 'leverage', 'roa', 'roe',
                          'npl', 'npl_ratio', 'car', 'capital_ratio']
    _funds = [c for c in _FUNDAMENTAL_CANDS if c in panel.columns]
    if _funds:
        import numpy as _np
        _yd = pd.get_dummies(panel['year'].astype('Int64'), prefix='yr', drop_first=True)
        _X = pd.concat([panel[_funds].astype(float), _yd.astype(float)], axis=1)
        _X.insert(0, '_const', 1.0)
        abn_count = 0
        for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
            tone = f'llm_vote_tone{track}'
            if tone not in panel.columns:
                continue
            _y = panel[tone].astype(float)
            _mask = _y.notna() & _X.notna().all(axis=1)
            resid = pd.Series(_np.nan, index=panel.index, dtype=float)
            if int(_mask.sum()) > _X.shape[1] + 1:  # 自由度充足才回归
                Xm = _X.loc[_mask].to_numpy(dtype=float)
                ym = _y.loc[_mask].to_numpy(dtype=float)
                beta, *_ = _np.linalg.lstsq(Xm, ym, rcond=None)
                resid.loc[_mask] = ym - Xm @ beta
            panel[f'abnormal_tone{track}'] = resid
            abn_count += 1
        logger.info(f"  已生成 {abn_count} 个异常语调残差变量 (基本面={_funds})")
    else:
        logger.info("  异常语调 (abnormal_tone) 跳过: 面板无银行财务基本面列 "
                    "(需外部 merge CSMAR 财务; dormant, 批 #15)")

    logger.info(f"  ── 异质性分析交互项预计算完成 ──")

    # --- 7h-net. 同行网络传染/溢出效应 (Leary & Roberts 2014, JF) ---
    if compute_network_spillovers is not None:
        logger.info("=" * 60)
        logger.info("步骤 7h-net: 同行网络传染/溢出效应")
        logger.info("=" * 60)
        panel = compute_network_spillovers(panel, df_exploded)
    else:
        logger.info("  46_network_spillovers.py 不存在, 跳过网络溢出计算")

    # --- 7h-bd. BERT 净语调年内时序 (2026-07-03 执行计划 WP-E) ---
    # iyvol = 噪声校正年内波动 (剔稀疏月均值抽样噪声, 否则低覆盖格机械虚高);
    # iytrend = 月均值对实际月号的闭式 OLS 斜率 (≥6 有效月)。三向正交:
    # vs tone_volatility(跨年 rolling) 真正交 / vs {b}_pos_std 仅校正后近似
    # 正交 (codebook notes 详)。merge 时序在 balance_panel 零填之后 → 结构上
    # 不经 zero-fill, 无新闻格天然 NaN; 先 pre-drop 既存同名列防重跑 _x/_y
    # 污染 (先例 attention_media 媒体异质 merge)。
    _bd_iy = bert_distribution.compute_intrayear_dynamics(df_exploded, BERT_MODELS)
    _bd_iy_cols = [c for c in _bd_iy.columns if c not in ('target_bank', 'year')]
    _bd_iy_existing = [c for c in _bd_iy_cols if c in panel.columns]
    if _bd_iy_existing:
        panel = panel.drop(columns=_bd_iy_existing)
    _bd_rows_before = len(panel)
    panel = panel.merge(_bd_iy, on=['target_bank', 'year'], how='left')
    if len(panel) != _bd_rows_before:  # fail-loud (裸 assert 在 -O 下被剥, 终审 F3)
        raise RuntimeError(
            f"WP-E merge 行数漂移 {_bd_rows_before}→{len(panel)} (键重复?)")
    logger.info(f"  BERT 年内时序 merge: {len(_bd_iy_cols)} 列 "
                f"(源 {len(_bd_iy):,} 个 bank-year 格, 行数不变 {_bd_rows_before:,})")

    # --- 7h-cent. 银行共现网络中心度 (Freeman 1979; Billio et al. 2012) ---
    if compute_bank_network_centrality is not None:
        panel = compute_bank_network_centrality(panel, df_exploded)
        # 网络构造判据敏感性 (2026-07-03, 计划 NETWORK_TRITRACK_AND_CRITERIA):
        # 同一 33 指标按银行∧银行共现判据分轨 — _win1 (±1 句窗) / _sent
        # (严格同句), 与无后缀 canonical (同篇) 互为稳健性、不分主次;
        # 三判据各自 just-identified, 禁混同一 over-identified Hansen J。
        panel = compute_bank_network_centrality(
            panel, df_exploded, criterion='win1', suffix='_win1')
        panel = compute_bank_network_centrality(
            panel, df_exploded, criterion='sent', suffix='_sent')
    else:
        logger.info("  compute_bank_network_centrality 不可用, 跳过")

    # --- 7h-cogn. 认知邻近度 (Boschma 2005; 操作化=本项目自定义 TF-IDF cosine) ---
    if compute_cognitive_proximity is not None:
        panel = compute_cognitive_proximity(df_exploded, panel)
    else:
        logger.info("  compute_cognitive_proximity 不可用, 跳过")

    # --- 7h-strat. 战略差异度指数 (Guzman & Li 2023; Hoberg & Phillips 2016) ---
    # Step 4(d-ii) 硬化: 删除原 if/else None-check, 配合 L89 硬 import
    # 共同保证 fail-loud 而非降级跑出缺列 panel.
    panel = compute_strategic_differentiation(df_exploded, panel)

    # --- 7h-auth. 权威政策战略响应度 (Hassan et al. 2019, QJE) ---
    # v6/F3 修复 (主路径全 NaN)：删除原"零向量数学正交"熔断填充。
    # 学术依据 (Allison 2001 §3 / Heckman 1979 ECMA)：当某 bank-year
    # 在该 track 下无文章可计算余弦相似度时，正确语义是"未测量"
    # (NaN)，而非"测量值为 0"。强行填 0 会在 TWFE 中制造伪零质心、
    # 扭曲系数并低估标准误。Stata 端通过 listwise deletion 自然处理。
    # 旧注释"零向量数学正交"为虚假学术依据：余弦相似度对零向量未定义。
    panel = compute_authoritative_similarity(df_exploded, panel)

    # --- 7h-benefit. 经营效益情感态度投影 (Jha, Liu & Manela 2026, RFS) ---
    # 【学术依据】Jha et al. (2026, RFS §1.3.2 Eq. 1): 双极连续余弦投影
    #   a_j = cos(s_j, mean(pos) - mean(neg))
    # 【白话】用"利好经营 vs 损害经营"方向轴给每篇新闻打态度分
    # v6/F3 修复 (主路径全 NaN)：删除原 fillna(0.0) 熔断填充。
    # 与 auth_sim_* 同：无文章观测 → 投影未定义 → NaN。
    panel = compute_benefit_society_panel(panel, df_exploded)

    # --- 7h-token. 文章级政策对齐 + Token/Hidden 四象限分类 ---
    # 【学术支撑】
    #   Distel, A. P., Grimpe, C., & Poetz, M. (2026). From evidence to
    #   impact. Research Policy, 55(3), 105426.
    #   https://doi.org/10.1016/j.respol.2026.105426
    #   -> S3.2.1: 解耦"显性引用"(Token) 与"文本级语义实质借鉴"(Hidden)
    #
    #   Westphal, J. D. & Zajac, E. J. (2001). Decoupling policy from practice.
    #   ASQ, 46(2), 202-228. https://doi.org/10.2307/2667086
    #   -> Token Adoption = 象征性采用 (合法性功能)
    #
    # 【白话说明】
    #   读取 Stage 15 的逐篇文章政策对齐分数 (policy_cosine_sim),
    #   结合词频维度(kw/int 两条词频轨, 非 full/ctx/ss 情感轨), 把每篇文章分到四个象限:
    #     Token(说得多+没落地) / Hidden(说得少+做得真) /
    #     Substantive(言行一致) / Irrelevant(不相关)
    #   然后按(银行,年)统计各象限的文章占比, 作为面板变量.
    # -----------------------------------------------------------------------
    logger.info("=" * 60)
    logger.info("步骤 7h-token: 文章级政策对齐 + Token/Hidden 四象限分类")
    logger.info("=" * 60)

    # 尝试加载 Stage 15 输出
    _align_filename = FILENAMES.get(
        'output_15_article_alignment', '16_article_alignment.parquet')
    _align_path = os.path.join(OUTPUT_DIR, _align_filename)

    # Step 4(b) 硬化 (致命问题 5 / 红队 v6): 删除原"文件不存在则静默 skip"的
    # 容错。Stage 15 (文章级政策对齐) 输出 policy_cosine_sim 是 7h-token 四
    # 象限分类的硬依赖, skip 会让 panel 缺失 token_share / hidden_share 等列,
    # 落到下游 stage 51 falsification 测试时会用 "缺列即 0" 的隐性默认值,
    # 制造伪零样本污染计量结论。必须 fail-loud 让 orchestrator 立即停止.
    if not os.path.exists(_align_path):
        raise RuntimeError(
            f"[stage 45/7h-token] 上游输入缺失: {_align_path} 不存在。"
            f" Stage 45 的 7h-token 四象限分类硬依赖 stage 15 输出的 "
            f"policy_cosine_sim 列。请先运行 "
            f"`python -m news_process.pipeline.filtering.policy_alignment` "
            f"产出 {_align_filename} 后再重试。"
        )

    if os.path.exists(_align_path):
        df_align = pd.read_parquet(_align_path)
        logger.info(f"  加载 Stage 15: {len(df_align)} 篇, "
                    f"policy_cosine_sim 非空率: "
                    f"{pct4(df_align['policy_cosine_sim'].notna().mean())}")

        # 【关键】Stage 15 的输出基于 Stage 14 (15_fintech_intensity.parquet),
        #   该文件不含 'year' 列 — year 由 Stage 45 的 parse_time() 从 '日期' 派生。
        #   因此必须在此处自行从 '日期' 列计算 year, 否则 groupby('year') 会 KeyError。
        if 'year' not in df_align.columns and '日期' in df_align.columns:
            df_align['日期'] = pd.to_datetime(df_align['日期'], errors='coerce')
            df_align['year'] = df_align['日期'].dt.year
            df_align = df_align.dropna(subset=['year'])
            df_align['year'] = df_align['year'].astype(int)
            logger.info(f"  从 '日期' 列派生 year: {df_align['year'].nunique()} 个年份")

        # fix(omni-g-runner-02, 2026-06-11): 聚合域对齐 — 7h-token 全族 (article_sim_*/
        # fintech_intensity_mean/policy_cosine_sim_lg_*/四象限) 此前在 stage 14 规则
        # 预筛全集 (含 LLM 验证未通过文章) 上聚合, 与全仓其余面板测度的 verified 聚合域
        # (df_exploded=24_herd_decay) 结构性不一致 (盘上孪生对 60/118 取值不同,
        # max|Δ|=0.437, 4 个 phantom bank-year)。semi-join 收敛到 verified 子集。
        df_align = _filter_to_verified_universe(df_align, df_exploded)

        # --- 逻辑 A: 连续聚合变量 (主回归) ---
        # 【术语】按 (target_bank, year) 聚合文章级 policy_cosine_sim
        #   为 mean 和 std, 以及 fintech_intensity_score 的 mean
        #   参考: Royston, Altman & Sauerbrei (2006, Stat Med) --
        #   连续变量优于离散化
        # 【白话】算每家银行每年的平均政策对齐分和平均技术强度分
        if 'target_bank' in df_align.columns and 'year' in df_align.columns:
            # multi-track parity (2026-06-08 ctx; v3.9.0 ss): MAIN/API spec 的
            # policy_cosine_sim_ctx/_ss 在文章级产出 (stage 15 与 _full 对称), 须聚合进
            # 面板 (只聚合 _full alias policy_cosine_sim 会让面板层 MAIN 模型单边缺 ctx/ss,
            # 而 co-primary _lg 轨三轨聚合, 见下方)。三轨 (full/ctx/ss): ss=银行+金科同句轨,
            # 缺列 (旧 schema / ss 未上线) 优雅跳过。
            _agg_spec = {
                'article_sim_mean': ('policy_cosine_sim', 'mean'),
                'article_sim_std': ('policy_cosine_sim', 'std'),
                'fintech_intensity_mean': ('fintech_intensity_score', 'mean'),
            }
            if 'policy_cosine_sim_ctx' in df_align.columns:
                _agg_spec['article_sim_mean_ctx'] = ('policy_cosine_sim_ctx', 'mean')
                _agg_spec['article_sim_std_ctx'] = ('policy_cosine_sim_ctx', 'std')
            if 'policy_cosine_sim_ss' in df_align.columns:
                _agg_spec['article_sim_mean_ss'] = ('policy_cosine_sim_ss', 'mean')
                _agg_spec['article_sim_std_ss'] = ('policy_cosine_sim_ss', 'std')
            # 全年份锚点稳健孪生 (_allv, 2026-06-21): stage 15 并列产 policy_cosine_sim_allv*
            # (全语料静态锚点) 时, 同口径聚合为 article_sim_mean/std_allv* (与主轨对称,
            # 缺列优雅跳过 = companion 关闭 / 旧 schema)。
            if 'policy_cosine_sim_allv' in df_align.columns:
                _agg_spec['article_sim_mean_allv'] = ('policy_cosine_sim_allv', 'mean')
                _agg_spec['article_sim_std_allv'] = ('policy_cosine_sim_allv', 'std')
            if 'policy_cosine_sim_allv_ctx' in df_align.columns:
                _agg_spec['article_sim_mean_allv_ctx'] = ('policy_cosine_sim_allv_ctx', 'mean')
                _agg_spec['article_sim_std_allv_ctx'] = ('policy_cosine_sim_allv_ctx', 'std')
            if 'policy_cosine_sim_allv_ss' in df_align.columns:
                _agg_spec['article_sim_mean_allv_ss'] = ('policy_cosine_sim_allv_ss', 'mean')
                _agg_spec['article_sim_std_allv_ss'] = ('policy_cosine_sim_allv_ss', 'std')
            _agg = df_align.groupby(['target_bank', 'year']).agg(
                **_agg_spec).reset_index()
            # fix(omni-group-std-singleobs, 2026-06-11, 组级裁决): 删除旧
            # `article_sim_std(_ctx).fillna(0.0)` — 单篇文章的 bank-year 其
            # std (ddof=1) 数学上未定义, 强填 0 把"离散度不可估计"伪装成
            # "零分歧"假观测; 保持 NaN 与本函数下方 v6/F3 "无数据=未测量"
            # 契约及同族 *_std 缺失语义一致 (benefit_std 同型缺陷在
            # features/benefit_society.py, 归 g-features 组)。
            panel = panel.merge(_agg, on=['target_bank', 'year'], how='left')
            logger.info(f"  连续聚合: article_sim_mean/std, "
                        f"fintech_intensity_mean 已合并")

            # co-primary ② (embedding_large, text-embedding-3-large, 3072 维): stage 15
            # 在 _LARGE_SPEC 非空时额外产出 article 级 policy_cosine_sim_lg_{full,ctx,ss}
            # 及其全年份锚点孪生 _lg_allv_*。v3.14.0 起 Qwen(MAIN, 无后缀) 与 large(_lg)
            # 为对等 co-primary 双轨 (跨厂商互证); 此处按 (bank, year) 取均值聚合为 bank-year
            # 同名列。MAIN(无后缀) policy_cosine_sim_* 已在上方连续聚合块合并 (article_sim_*
            # 同源), _lg 孪生在此并列。_lg 为软诊断/可 NaN → producer both-or-neither 保证
            # 列名双射 (有 Qwen 处必有 large); 列表推导自动按存在性过滤, 缺则优雅跳过。
            # code-review P1-1: _lg 聚合必须按 MAIN 同名约定 **rename** 为 article_sim_*_lg
            # (而非 raw policy_cosine_sim_lg_*), 否则面板层 MAIN=article_sim_mean 与 _lg=
            # policy_cosine_sim_lg 名不对称 → co-primary 列名双射破 (parity 门红)。mean+std
            # 双统计与 MAIN 对称; 缺源列优雅跳过 (producer both-or-neither 保双射)。
            _lg_map = [
                ('policy_cosine_sim_lg_full', 'article_sim_mean_lg', 'article_sim_std_lg'),
                ('policy_cosine_sim_lg_ctx', 'article_sim_mean_lg_ctx', 'article_sim_std_lg_ctx'),
                ('policy_cosine_sim_lg_ss', 'article_sim_mean_lg_ss', 'article_sim_std_lg_ss'),
                ('policy_cosine_sim_lg_allv_full', 'article_sim_mean_lg_allv', 'article_sim_std_lg_allv'),
                ('policy_cosine_sim_lg_allv_ctx', 'article_sim_mean_lg_allv_ctx', 'article_sim_std_lg_allv_ctx'),
                ('policy_cosine_sim_lg_allv_ss', 'article_sim_mean_lg_allv_ss', 'article_sim_std_lg_allv_ss'),
            ]
            _lg_agg_spec = {}
            for _src, _mean_name, _std_name in _lg_map:
                if _src in df_align.columns:
                    _lg_agg_spec[_mean_name] = (_src, 'mean')
                    _lg_agg_spec[_std_name] = (_src, 'std')
            if _lg_agg_spec:
                _lg_agg = (df_align.groupby(['target_bank', 'year'])
                           .agg(**_lg_agg_spec).reset_index())
                panel = panel.merge(_lg_agg, on=['target_bank', 'year'], how='left')
                logger.info(f"  co-primary: article_sim_*_lg 聚合 ({len(_lg_agg_spec)} 列) 已合并")

            # --- 逻辑 B: 四象限离散分类 (机制检验 / 稳健性) ---
            # 【术语】
            #   两条词频轨 (此处指 kw/int 词频测度, 非 full/ctx/ss 情感轨):
            #     Track A (kw): fintech_distinct_keywords (AC 原始去重关键词数)
            #     Track B (int): fintech_intensity_score (TF-IDF x SIF 加权)
            #   分位数阈值: P={25, 50, 75}
            #     P50 = 机制检验基准 (与项目 10+ 处中位数分割惯例一致)
            #     P25/P75 = 稳健性检验
            #
            #   四象限定义 (逐篇文章级):
            #     Substantive: 词频 >= 分位数 AND 相似度 >= 分位数 (言行一致)
            #     Token:       词频 >= 分位数 AND 相似度 <  分位数 (洗科技)
            #     Hidden:      词频 <  分位数 AND 相似度 >= 分位数 (闷声干大事)
            #     Irrelevant:  词频 <  分位数 AND 相似度 <  分位数 (不相关)
            #
            # 【白话】把每篇新闻放进四个格子里:
            #   纵轴 = 关键词多不多, 横轴 = 跟政策像不像
            #   然后数每家银行每年各有多少比例的新闻在每个格子里

            _tracks = [
                ('kw', 'fintech_distinct_keywords'),
                ('int', 'fintech_intensity_score'),
            ]
            _align_cfg = CONFIG.get('article_alignment', {})
            _percentiles = _align_cfg.get('quadrant_percentiles', [25, 50, 75])

            # fix(omni-g-runner-03/g-runner-11, 2026-06-11): NaN 掩码分类 —
            # 旧实现 `NaN >= thresh → False` 把测量失败文章静默归入低对齐/低词频:
            # stage 15 三条优雅早退路径写出的 policy_cosine_sim 全 NaN parquet 会让
            # 全部高词频文章误归 Token (由零测量制造非 NaN 面板值), 逐篇 NaN 滞留
            # 物理域分母。改经 _classify_policy_quadrants: 仅 sim/freq 双双 notna
            # 行分类, 未测量行指示=NaN → groupby mean 跳过 (分母=已测量篇数);
            # 全 NaN 年 → 面板 NaN, 与下方 v6/F3 "无数据=未测量" 契约对齐。
            if df_align['policy_cosine_sim'].notna().sum() == 0:
                logger.warning(
                    "  ⚠️ policy_cosine_sim 全 NaN (stage 15 优雅早退产物?) — "
                    "四象限/相似度面板列将全部输出 NaN 而非伪零 "
                    "(fix(omni-g-runner-03))")

            # fix(omni-g-runner-07, 2026-06-11): ctx 孪生 — 旧四象限仅 full 轨
            # (sim/freq 全用 full alias), 而同函数上方 sim mean/std 已有 ctx 分支。
            # 补 *_adopt_{kw,int}_p{pct}_ctx: sim 用 policy_cosine_sim_ctx, 词频
            # 优先 {freq_col}_ctx (int 轨存在); kw 轨的 AC 去重关键词数为
            # track-agnostic 元数据 (无 ctx 变体) 时复用 full 列并披露。
            # v3.9.0: 三轨 (full/ctx/ss) — ss=银行+金科同句轨, sim 用
            # policy_cosine_sim_ss, 词频优先 {freq_col}_ss; 缺列优雅跳过 (旧 schema)。
            # 全年份锚点稳健孪生 (_allv, 2026-06-21): anchor 变体外层循环 — '' = vintage
            # 主轨 (sim 用 policy_cosine_sim*); '_allv' = 全语料静态锚点 (sim 用
            # policy_cosine_sim_allv*)。两变体共用**完全一致**的 track(full/ctx/ss) ×
            # 词频(kw/int) × 分位(P) 四象限构造, 唯 sim 阈值列基名不同 → 占比列名插入
            # `_allv` (在 track 后缀前, 如 token_adopt_kw_p25_allv_ctx)。⚠ 词频侧后缀
            # 只随 track (_ctx/_ss) 变, 与 anchor 无关 (词频不依赖政策锚点)。
            _anchor_variants = [('', 'policy_cosine_sim')]
            if 'policy_cosine_sim_allv' in df_align.columns:
                _anchor_variants.append(('_allv', 'policy_cosine_sim_allv'))
            else:
                logger.info("  四象限: policy_cosine_sim_allv 缺失 "
                            "(companion 关闭 / 旧 schema), 跳过 _allv 全年份锚点孪生")

            for _anc_sfx, _anc_base in _anchor_variants:
                _sim_tracks = [('', _anc_base)]
                if f'{_anc_base}_ctx' in df_align.columns:
                    _sim_tracks.append(('_ctx', f'{_anc_base}_ctx'))
                elif _anc_sfx == '':
                    logger.warning("  ⚠️ policy_cosine_sim_ctx 缺失, 四象限 ctx 孪生"
                                   "跳过 (旧 schema)")
                if f'{_anc_base}_ss' in df_align.columns:
                    _sim_tracks.append(('_ss', f'{_anc_base}_ss'))
                elif _anc_sfx == '':
                    logger.warning("  ⚠️ policy_cosine_sim_ss 缺失, 四象限 ss 孪生"
                                   "跳过 (旧 schema / ss 未上线)")

                for _sim_sfx, _sim_col in _sim_tracks:
                    for track_name, freq_col in _tracks:
                        _freq_eff = freq_col
                        # ctx/ss 轨: 词频优先同轨变体 {freq_col}{_sim_sfx}; kw 轨的 AC
                        # 去重关键词数为 track-agnostic 元数据 (无同轨变体) 时复用 full 列。
                        if _sim_sfx in ('_ctx', '_ss'):
                            if f'{freq_col}{_sim_sfx}' in df_align.columns:
                                _freq_eff = f'{freq_col}{_sim_sfx}'
                            elif _anc_sfx == '':
                                logger.info(
                                    f"  Track {track_name} ({_sim_sfx}): 词频列无同轨变体 "
                                    f"(track-agnostic), 复用 {freq_col}")
                        if _freq_eff not in df_align.columns:
                            if _anc_sfx == '':
                                logger.warning(f"  {_freq_eff} 列缺失, "
                                               f"跳过 Track {track_name}{_sim_sfx}")
                            continue

                        for pct in _percentiles:
                            _tok, _hid, _sub = _classify_policy_quadrants(
                                df_align, _sim_col, _freq_eff, pct)
                            _k = f'{track_name}_p{pct}{_anc_sfx}{_sim_sfx}'
                            df_align[f'_is_token_{_k}'] = _tok
                            df_align[f'_is_hidden_{_k}'] = _hid
                            df_align[f'_is_subst_{_k}'] = _sub

                            # 按 (银行, 年) 聚合为占比 (mean 跳过 NaN →
                            # 分母 = 已测量篇数; 全未测量 bank-year → NaN)
                            _quadrant_agg = df_align.groupby(
                                ['target_bank', 'year']).agg(
                                **{f'token_adopt_{_k}': (f'_is_token_{_k}', 'mean'),
                                   f'hidden_adopt_{_k}': (f'_is_hidden_{_k}', 'mean'),
                                   f'subst_adopt_{_k}': (f'_is_subst_{_k}', 'mean'),
                                   }
                            ).reset_index()

                            panel = panel.merge(
                                _quadrant_agg, on=['target_bank', 'year'], how='left')

                        logger.info(f"  Track {track_name}{_anc_sfx}{_sim_sfx}: "
                                    f"P={_percentiles} 四象限占比已合并")

            # v6/F3 修复 (主路径全 NaN)：删除原 fillna(0.0)。
            # token_adopt / hidden_adopt / subst_adopt / article_sim_ / fintech_intensity_mean
            # 这些都是"率/均值/相似度"类指标，无 Stage 15 数据的 bank-year
            # 真实语义是"未测量"，强填 0 会污染 TWFE 系数 (Allison 2001 §3)。
            _token_cols = [c for c in panel.columns
                          if c.startswith(('token_adopt_', 'hidden_adopt_',
                                           'subst_adopt_', 'article_sim_',
                                           'fintech_intensity_mean'))]
            logger.info(f"  Token/Hidden 面板变量: 共 {len(_token_cols)} 列 (NaN 保持，listwise 处理)")

            # 清理临时列
            _tmp_cols = [c for c in df_align.columns if c.startswith('_is_')]
            df_align.drop(columns=_tmp_cols, inplace=True, errors='ignore')

        else:
            logger.warning("  Stage 15 数据缺少 target_bank/year 列, 跳过")
    else:
        logger.info(f"  Stage 15 文件不存在 ({_align_path}), 跳过 Token/Hidden 计算")

    # --- 7h-brok. 信息经纪网络中心度 (Han et al. 2024, RFS) ---
    if compute_brokerage_centrality is not None:
        panel = compute_brokerage_centrality(panel, df_exploded)
    else:
        logger.info("  compute_brokerage_centrality 不可用, 跳过")

    # --- 7h-neg. 行业负面冲击指数 (LOO, Manski 1993) ---
    if compute_industry_neg_shock is not None:
        panel = compute_industry_neg_shock(panel)
    else:
        logger.info("  compute_industry_neg_shock 不可用, 跳过")

    # --- 7h-fire. 火灾甩卖交乘项 (依赖 brokerage + neg_shock) ---
    if compute_fire_sale_interaction is not None:
        panel = compute_fire_sale_interaction(panel)
    else:
        logger.info("  compute_fire_sale_interaction 不可用, 跳过")

    # --- 7h-emb. Embedding 同业网络控制 (Hoberg & Phillips 2016; Reimers 2019) ---
    # 基于 Sentence Embedding 向量相似度构建动态同业网络权重矩阵,
    # 计算加权同行情感作为控制变量, 补充共现网络的语义维度。
    if compute_embedding_peer_network is not None:
        panel = compute_embedding_peer_network(df_exploded, panel)
    else:
        logger.info("  compute_embedding_peer_network 不可用, 跳过")

    # --- 7h-llmpeer. LLM-Peer 动态竞争网络 IV (Cao et al. 2025) ---
    # 基于 LLM 语义判断构建竞争同行网络, 加权同行情感作为 IV。
    # 双重筛选句子 (2+ 银行名 + 金融科技关键词) → GPT → 模糊匹配 → 滞后 IV
    if compute_llm_peer_iv is not None:
        panel = compute_llm_peer_iv(panel, df_exploded)
    else:
        logger.info("  compute_llm_peer_iv 不可用, 跳过")

    # =========================================================================
    # 步骤 7h: 洗稿率 (Washing Ratio) — 多方法 × 三轨 (full/ctx/ss) 构造
    # =========================================================================
    # 学术依据:
    #   Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022).
    #   Cheap talk and cherry-picking. Finance Research Letters, 47(B), 102776.
    #   https://doi.org/10.1016/j.frl.2022.102776
    #
    # 构造 多方法 × 三轨 (Full/Ctx/SS) 洗稿率变体 (ss=银行+金科同句轨)
    # (fix(omni-g-runner-08, 2026-06-11): 旧注释硬编码 "40 种/5模型" 与实现漂移,
    #  实际变体数随启用模型/词典数浮动, 以下方 wr_variants 动态诊断日志为准):
    #   A/A2: LLM 投票 + 单 LLM (LLM_MODELS 当前 3 个) × 三轨
    #   B:    反向验证 + 非对称性 × 三轨
    #   C:    情感纯度缺口 × 三轨
    #   D/D2: 词典均值 + 单词典 (DICT_NAMES 6 本) × 三轨
    #   E/E2: BERT 均值 + 单 BERT (BERT_MODELS 当前 3 个) × 三轨
    #   F:    高置信度子样本 × 三轨
    #   G:    象征性文章情感偏移 × 三轨
    # =========================================================================
    logger.info("=" * 60)
    logger.info("步骤 7h: 洗稿率 (Washing Ratio) — 多方法 × 三轨 (full/ctx/ss) 构造")
    logger.info("=" * 60)

    def _safe_ratio(numer, denom):
        """安全除法: 分母 <= 0 时返回 NaN, 使用 np.divide + where 避免 RuntimeWarning。"""
        out = np.full(len(denom), np.nan)
        mask = np.asarray(denom) > 0
        np.divide(np.asarray(numer), np.asarray(denom), out=out, where=mask)
        return out

    def _svd_denom(svd_col, phys_col):
        """洗稿率分母同域化 (fix(omni-g-runner-10/g-runner-14, 2026-06-11))。

        分子隐式要求 innovation_substantiveness 已测量 (NaN→astype(str)→'nan'
        永 False), 旧分母却数全部阳性文章 → LLM 实质性分类失败率上升时洗稿率
        系统性下偏 (valid 分子 / physical 分母失配, 与已修 encode-01 同族)。
        分母改用 `{name}_substvalid_count{track}` (阳性 ∧ 实质性已测量, 步骤 5
        由 _pool_svd_substvalid_counts 聚合); 旧 schema 缺该列时回退物理分母
        (保持旧行为) 并告警。
        """
        if svd_col in panel.columns:
            return panel[svd_col]
        logger.warning(f"  ⚠️ {svd_col} 缺失, 洗稿率分母回退物理计数 "
                       f"{phys_col} (旧 schema; fix(omni-g-runner-10/14))")
        return panel[phys_col]

    wr_variants = {}  # {变量名: 描述}

    for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
        # 变量名后缀: full 不加后缀 (主指标), ctx→_ctx, ss→_ss (银行+金科同句轨)。
        # ⚠ 不可写成 '' if full else '_ctx' (会把 ss 误并到 ctx 列名)。
        _sfx = '' if track == '_full' else track
        pos_col = f'pos_count{track}'

        # --- 方法 A: LLM 投票极化条件法 ---
        # fix(omni-g-runner-10, 2026-06-11): 分母改 substvalid 同域计数 (下同各方法)
        pd_col = f'pos_symb_count{track}'
        vn = f'washing_ratio{_sfx}'
        if pos_col in panel.columns and pd_col in panel.columns:
            panel[vn] = _safe_ratio(
                panel[pd_col],
                _svd_denom(f'pos_substvalid_count{track}', pos_col))
            wr_variants[vn] = f'A: LLM投票{track}'

        # --- 方法 A2: 单个 LLM ---
        for llm in LLM_MODELS:
            pc = f'{llm}_pos_count{track}'
            pdc = f'{llm}_pos_symb_count{track}'
            vn = f'washing_ratio_{llm}{_sfx}'
            if pc in panel.columns and pdc in panel.columns:
                panel[vn] = _safe_ratio(
                    panel[pdc],
                    _svd_denom(f'{llm}_pos_substvalid_count{track}', pc))
                wr_variants[vn] = f'A2: {llm}{track}'

        # --- 方法 B: 反向验证 ---
        neg_col = f'neg_count{track}'
        ns_col = f'neg_sub_count{track}'
        if neg_col in panel.columns and ns_col in panel.columns:
            vn_r = f'neg_sub_ratio{track}'
            panel[vn_r] = _safe_ratio(
                panel[ns_col],
                _svd_denom(f'neg_substvalid_count{track}', neg_col))
            wr_variants[vn_r] = f'B: 负面实质性{track}'
            # 非对称性
            wr_a = f'washing_ratio{_sfx}'
            if wr_a in panel.columns:
                vn_asym = f'washing_asymmetry{track}'
                panel[vn_asym] = panel[vn_r] - (1 - panel[wr_a])
                wr_variants[vn_asym] = f'B: 非对称性{track}'

        # --- 方法 C: 情感纯度缺口 (实质性 vs 象征性) ---
        sub_col = f'llm_vote_tone_sub{track}'
        symb_col = f'llm_vote_tone_symb{track}'
        if sub_col in panel.columns and symb_col in panel.columns:
            vn = f'tone_gap_symb_sub{track}'
            panel[vn] = panel[symb_col] - panel[sub_col]
            wr_variants[vn] = f'C: 情感缺口{track}'

        # --- 方法 D: 词典均值 ---
        dpc = f'dict_pos_count{track}'
        dpdc = f'dict_pos_symb_count{track}'
        if dpc in panel.columns and dpdc in panel.columns:
            vn = f'washing_ratio_dict{_sfx}'
            panel[vn] = _safe_ratio(
                panel[dpdc],
                _svd_denom(f'dict_pos_substvalid_count{track}', dpc))
            wr_variants[vn] = f'D: 词典均值{track}'

        # --- 方法 D2: 单个词典 ---
        for d in DICT_NAMES:
            pc = f'{d}_pos_count{track}'
            pdc = f'{d}_pos_symb_count{track}'
            vn = f'washing_ratio_{d}{_sfx}'
            if pc in panel.columns and pdc in panel.columns:
                panel[vn] = _safe_ratio(
                    panel[pdc],
                    _svd_denom(f'{d}_pos_substvalid_count{track}', pc))
                wr_variants[vn] = f'D2: {d}{track}'

        # --- 方法 E: BERT 均值 ---
        bpc = f'bert_pos_count{track}'
        bpdc = f'bert_pos_symb_count{track}'
        if bpc in panel.columns and bpdc in panel.columns:
            vn = f'washing_ratio_bert{_sfx}'
            panel[vn] = _safe_ratio(
                panel[bpdc],
                _svd_denom(f'bert_pos_substvalid_count{track}', bpc))
            wr_variants[vn] = f'E: BERT均值{track}'

        # --- 方法 E2: 单个 BERT ---
        for b in BERT_MODELS:
            pc = f'{b}_pos_count{track}'
            pdc = f'{b}_pos_symb_count{track}'
            vn = f'washing_ratio_{b}{_sfx}'
            if pc in panel.columns and pdc in panel.columns:
                panel[vn] = _safe_ratio(
                    panel[pdc],
                    _svd_denom(f'{b}_pos_substvalid_count{track}', pc))
                wr_variants[vn] = f'E2: {b}{track}'

        # --- 方法 F: 高置信度子样本 ---
        hpc = f'pos_hc_count{track}'
        hpdc = f'pos_symb_hc_count{track}'
        if hpc in panel.columns and hpdc in panel.columns:
            vn = f'washing_ratio_hc{_sfx}'
            panel[vn] = _safe_ratio(
                panel[hpdc],
                _svd_denom(f'pos_hc_substvalid_count{track}', hpc))
            wr_variants[vn] = f'F: 高置信{track}'

        # --- 方法 G: 情感偏移 ---
        symb_tone = f'llm_vote_tone_symb{track}'
        all_tone = f'llm_vote_tone{track}'
        if symb_tone in panel.columns and all_tone in panel.columns:
            vn = f'washing_tone_shift{track}'
            panel[vn] = panel[symb_tone] - panel[all_tone]
            wr_variants[vn] = f'G: 情感偏移{track}'

    # --- Dummy: 全年无正面新闻 ---
    if 'pos_count_full' in panel.columns:
        # v6/F2: pos_count_full 可能为 nullable Int64 (sum of Int8)。NaN → 视为 0 (无观测)。
        panel['dummy_no_positive_news'] = (panel['pos_count_full'].fillna(0) <= 0).astype(int)
        logger.info(f"  dummy_no_positive_news=1: {panel['dummy_no_positive_news'].sum():,} 个 Bank-Year")

    # --- 诊断日志 ---
    logger.info(f"  洗稿率变体数: {len(wr_variants)}")
    for var_name, desc in wr_variants.items():
        if var_name in panel.columns:
            valid = panel[var_name].dropna()
            if len(valid) > 0:
                logger.info(f"    {var_name} [{desc}]: "
                            f"n={len(valid):,}, mean={sig4(valid.mean())}, "
                            f"std={sig4(valid.std())}")
            else:
                logger.info(f"    {var_name} [{desc}]: 全部 NaN")


    # =========================================================================
    # 步骤 7i: Janis-Fadner (J-F) 情绪系数 — 稳健性替代指标
    # 学术依据: Janis & Fadner (1965); Deephouse (2000, J. of Management 26(6):1091-1112)
    # 公式:
    #   若 P > N: JF = (P² - P×N) / (P+N)²
    #   若 N > P: JF = (P×N - N²) / (P+N)²
    #   若 P = N: JF = 0
    # 取值范围: [-1, +1], 克服简单均值的零分悖论
    # =========================================================================
    logger.info("=" * 60)
    logger.info("步骤 7i: Janis-Fadner (J-F) 情绪系数")
    logger.info("=" * 60)

    for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
        pos_col = f'pos_count{track}'
        neg_col = f'neg_count{track}'
        if pos_col in panel.columns and neg_col in panel.columns:
            # fix(jf-int8): pos_count/neg_count 为 Int8 dtype, 直接 P**2 / (P+N)**2
            # 在 Int8 算术下静默整数回绕 (P+N≥12 即溢出 127), 致 jf_coefficient 越界 [-1,1]
            # (实测 max=2.387)。先转 float64 再算, 数学域恢复 [-1,1]。
            P = panel[pos_col].fillna(0).astype('float64')
            N = panel[neg_col].fillna(0).astype('float64')
            # fix(jf-denominator, metric-audit 2026-06-10): canonical Janis-Fadner (1965) /
            # Deephouse (2000, J.Mgmt 26(6)) 的分母是 t² (t = 全部有效编码数 = 正+负+**中性**),
            # 而非 (P+N)²。原 (P+N)² 丢弃中性覆盖, 对中性主导的 bank-year 系统性高估 |JF|
            # (P=10/N=0/中性90: 原式=1.0 vs canonical=0.01)。t 取 n_articles_llm_valid{track}
            # (= pos+neg+neu 有效投票数, 已验证 (P+N)≤该列)。范围仍守 [-1,1] (下方 assert)。
            # 白话: J-F 系数衡量"报道倒向一边的程度"。正确分母要把中性报道也
            # 算进总数, 否则一家银行 100 篇里 90 篇中性、10 篇正面会被误判成
            # "舆论一边倒"满分 1.0, 实际只有 0.01。
            _tcol = 'n_articles_llm_valid' if track == '_full' else f'n_articles_llm_valid{track}'
            if _tcol in panel.columns:
                T = panel[_tcol].fillna(0).astype('float64')
            else:
                T = P + N  # 回退 (旧 schema 无 valid 计数): 退化为有效方向口径
            total_sq = T ** 2
            # 安全除法: 防止 0/0
            safe_denom = total_sq.replace(0, np.nan)

            jf = np.where(
                P > N,
                (P**2 - P * N) / safe_denom,
                np.where(
                    N > P,
                    (P * N - N**2) / safe_denom,
                    0.0  # P == N
                )
            )
            panel[f'jf_coefficient{track}'] = np.where(
                safe_denom.isna(), np.nan, jf
            )
            # fix(jf-int8): Janis-Fadner 理论域守卫 — 越界即溢出回归未根治
            _jf_valid = panel[f'jf_coefficient{track}'].dropna()
            if len(_jf_valid) and not _jf_valid.between(-1.0, 1.0).all():
                raise ValueError(
                    f"jf_coefficient{track} 越界 [-1,1]: "
                    f"min={sig4(_jf_valid.min())}, max={sig4(_jf_valid.max())} "
                    f"(疑似整数溢出未根治)")
            logger.info(f"  jf_coefficient{track}: "
                        f"mean={sig4(panel[f'jf_coefficient{track}'].mean())}, "
                        f"std={sig4(panel[f'jf_coefficient{track}'].std())}")
        else:
            logger.warning(f"  {pos_col} 或 {neg_col} 不存在, 跳过 J-F 系数{track}")

    # ═══ 8b. 情感意见分歧 (Disagreement Index) ═══
    # 姜富伟, 李梦如, 孟令超 (2024). 调预期、防风险：央行金融稳定沟通效果研究.
    #   经济学（季刊）, 24(6), 2025-2040. DOI: 10.13821/j.cnki.ceq.2024.06.19
    # Antweiler, W., & Frank, M. Z. (2004). Is all that talk just noise?
    #   The Journal of Finance, 59(3), 1259-1294. DOI: 10.1111/j.1540-6261.2004.00662.x
    # 公式: disag = sqrt(1 - ((pos - neg) / (pos + neg))²)  ∈ [0, 1]
    #   0 = 完全一致 (全正或全负), 1 = 最大分歧 (正负相等)
    def _compute_disag(p_col, n_col, _panel):
        """通用 disag 计算, 处理 denom=0 边界 → NaN"""
        if p_col not in _panel.columns or n_col not in _panel.columns:
            return pd.Series(np.nan, index=_panel.index)
        # fix(completeness-03): 计数轨(pos_count/neg_count)为 Int8, (p+n) 在 ≥128 时
        # 静默整数回绕(同 JF 溢出类)。先转 float64 防御(当前 max~100 不触发, 故 0 值变化;
        # production 负面覆盖上升后避免 disag 翻错)。对 float 输入(ratio/bert)是 no-op。
        p = _panel[p_col].astype('float64')
        n = _panel[n_col].astype('float64')
        denom = p + n
        ratio = ((p - n) / denom.replace(0, np.nan)) ** 2
        return np.sqrt(1 - ratio)

    for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
        # (a) 词典综合 (词级比率)
        panel[f'disag{track}'] = _compute_disag(
            f'avg_pos_ratio{track}', f'avg_neg_ratio{track}', panel)
        # (b) 单词典 (词级比率)
        for d in DICT_NAMES:
            panel[f'disag_{d}{track}'] = _compute_disag(
                f'avg_{d}_pos_ratio{track}', f'avg_{d}_neg_ratio{track}', panel)
        # (c) LLM 投票综合 (篇章计数)
        panel[f'disag_llm{track}'] = _compute_disag(
            f'pos_count{track}', f'neg_count{track}', panel)
        # (d) 单 LLM (篇章计数)
        for llm in LLM_MODELS:
            panel[f'disag_{llm}{track}'] = _compute_disag(
                f'{llm}_pos_count{track}', f'{llm}_neg_count{track}', panel)
        # (e) BERT 综合 (概率均值, 43 L86 生成)
        panel[f'disag_bert{track}'] = _compute_disag(
            f'bert_avg_pos{track}', f'bert_avg_neg{track}', panel)
        # (f) 单 BERT (概率均值)
        for b in BERT_MODELS:
            panel[f'disag_{b}{track}'] = _compute_disag(
                f'{b}_pos{track}', f'{b}_neg{track}', panel)
    # fix(omni-g-runner-08, 2026-06-11): 旧硬编码 "(32 变量)" 实为 28
    # (BERT_MODELS=3 非注释所称 5) — 改动态计数, 防再漂移。
    _disag_n = len([c for c in panel.columns if c.startswith('disag')])
    logger.info(f"  disag 指标计算完成 ({_disag_n} 变量)")

    # ═══ 8c. 对数降噪定向情感 (Log-Transformed Sentiment) ═══
    # Angelico, C., Marcucci, J., Miccoli, M., & Quarta, F. (2022).
    #   Can we measure inflation expectations using Twitter?
    #   Journal of Econometrics, 228(2), 259-277. DOI: 10.1016/j.jeconom.2021.12.008
    # 公式: log_sent = log(1 + pos_count) - log(1 + neg_count)
    # fix(omni-g-runner-06/g-runner-15, 2026-06-11): 加覆盖门控 — balance_panel
    # 零填计数使零覆盖 bank-year (盘上 32.2% 行) 得伪中性 0.0, 与"1正1负完全均衡"
    # 的真测量 0 不可区分; 同族 jf/concern/disag 均已对无文章行输出 NaN (F3 红线,
    # Allison 2001; Heckman 1979), 唯 log_sent 漏网。改经 _gated_log_sent
    # (n_articles==0 → NaN, 对齐同族缺失语义)。
    _log_sent_n = 0
    for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
        pc, nc = f'pos_count{track}', f'neg_count{track}'
        if pc in panel.columns and nc in panel.columns:
            panel[f'log_sent{track}'] = _gated_log_sent(panel, track)
            _log_sent_n += 1
    logger.info(f"  log_sent 指标计算完成 ({_log_sent_n} 变量, 零覆盖→NaN)")

    # ═══ 8d. 算法迎合度 (Algorithmic Catering) — 全展开 ═══
    # Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk
    #   when a machine is listening. RFS, 36(9), 3603-3642. DOI: 10.1093/rfs/hhad021
    # Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT.
    #   CAR, 40(2), 806-841. DOI: 10.1111/1911-3846.12832
    # 公式: algo_cater = dict_tone - deep_model_tone
    #   正值 → 词典比深层模型更正面 (潜在迎合)
    _cater_count = 0
    for track in ['_full', '_ctx', '_ss']:  # 三轨 (full/ctx/ss): ss=银行+金科同句
        dc = f'dict_avg_tone{track}'
        lc = f'llm_vote_tone{track}'
        bp, bn = f'bert_avg_pos{track}', f'bert_avg_neg{track}'

        # A. 综合词典 vs 综合 LLM
        if dc in panel.columns and lc in panel.columns:
            panel[f'algo_cater{track}'] = panel[dc] - panel[lc]
            _cater_count += 1
        # A2. 综合词典 vs 综合 BERT
        if dc in panel.columns and bp in panel.columns and bn in panel.columns:
            panel[f'algo_cater_b{track}'] = panel[dc] - (panel[bp] - panel[bn])
            _cater_count += 1

        # B. 单词典 vs 综合深层模型
        for d in DICT_NAMES:
            d_col = f'{d}_tone{track}'
            if d_col in panel.columns:
                if lc in panel.columns:
                    panel[f'{d}_cater{track}'] = panel[d_col] - panel[lc]
                    _cater_count += 1
                if bp in panel.columns and bn in panel.columns:
                    panel[f'{d}_cater_b{track}'] = panel[d_col] - (panel[bp] - panel[bn])
                    _cater_count += 1

        # C. 综合词典 vs 单深层模型
        if dc in panel.columns:
            for llm in LLM_MODELS:
                llm_s = f'{llm}_tone{track}'
                if llm_s in panel.columns:
                    panel[f'cater_{llm}{track}'] = panel[dc] - panel[llm_s]
                    _cater_count += 1
            for b in BERT_MODELS:
                b_p, b_n = f'{b}_pos{track}', f'{b}_neg{track}'
                if b_p in panel.columns and b_n in panel.columns:
                    panel[f'cater_{b}{track}'] = panel[dc] - (panel[b_p] - panel[b_n])
                    _cater_count += 1
    logger.info(f"  algo_cater 指标计算完成 ({_cater_count} 变量)")

    # ═══ 8e. 嵌入 co-primary 双轨 (Embedding Co-Primary) 存在性诊断 (v3.14.0) ═══
    # ⚠ 此处"双轨"= Qwen ⟂ text-embedding-3-large 两个 API 嵌入模型 (非 full/ctx/ss
    # 文本情感轨)。v3.14.0 (2026-06-27, all-API-embedding): 本地 text2vec(_t2v)/bge(_bge)
    # 整体移除, 嵌入主轨改为 Qwen(MAIN, 无后缀) ⟂ text-embedding-3-large(_lg) 跨厂商对等
    # CO-PRIMARY 双轨 (跨厂商互证, 应对单一嵌入模型潜在的"幻觉偏移" Hallucination Bias)。
    #
    # 这些列由 stage 15 (policy alignment, 面板聚合后名 article_sim_mean*) / stage 25 (strat_diff_*) 主流程直接产出;
    # 此处不读取/merge 外部 parquet, 仅做存在性诊断 (保留自然缺失 NaN, 不 0 填充 —
    # Allison 2001 / Heckman 1979 listwise deletion 原则)。
    # parity (Qwen ⟂ _lg 列名双射) 由 test_embedding_coprimary_parity 测试门 +
    # producer both-or-neither 强制, *不*由本诊断或 export 运行期 raise; 故此处任何列缺失
    # 仅记 WARNING (软诊断, 不报错; _ss 同句轨与 _lg 孪生在上线/播种前可能整体缺失)。
    # ⚠ 命名注记 (fix 2026-06-28): policy alignment 的文章级 policy_cosine_sim* 在上方
    # "逻辑 A 连续聚合"块已按 (bank, year) 聚合并 **重命名** 为面板列 article_sim_mean*
    # (MAIN) / article_sim_mean_lg* (co-primary _lg); 故本诊断须按 **面板层** 实名核查,
    # 不能再找文章级旧名 policy_cosine_sim_*(永不在面板 → 历史每跑必误报"列缺失")。
    # strat_diff* 由 stage 25 inline 以原名落面板, 不改。
    emb_main_cols = [
        'strat_diff_full', 'strat_diff_ctx',
        'article_sim_mean', 'article_sim_mean_ctx'
    ]
    emb_lg_cols = [
        'strat_diff_lg_full', 'strat_diff_lg_ctx',
        'article_sim_mean_lg', 'article_sim_mean_lg_ctx'
    ]
    emb_cols_ss = ['strat_diff_ss', 'article_sim_mean_ss',
                   'strat_diff_lg_ss', 'article_sim_mean_lg_ss']  # 软诊断, 缺则不报错
    # 全年份锚点 _allv 孪生 (2026-06-21): 纯软诊断 (companion 开启时出现)。
    emb_cols_allv = ['article_sim_mean_allv', 'article_sim_mean_allv_ctx',
                     'article_sim_mean_allv_ss',
                     'article_sim_mean_lg_allv', 'article_sim_mean_lg_allv_ctx',
                     'article_sim_mean_lg_allv_ss']
    _all_emb_cols = emb_main_cols + emb_lg_cols + emb_cols_ss + emb_cols_allv
    _present = [c for c in _all_emb_cols if c in panel.columns]
    _missing = [c for c in emb_main_cols + emb_lg_cols if c not in panel.columns]
    if _missing:
        logger.warning(
            f"  ⚠️ 嵌入 co-primary 双轨: 以下内联 Qwen/_lg 列缺失 {_missing} "
            f"(检查 stage 15/25 embedding_api/embedding_large 配置与运行)。"
        )
    logger.info(f"  ✅ 嵌入 co-primary 双轨存在性特征 (保留自然缺失值 NaN): present={_present}")

    # --- 8c. Opt-in 特征面板 merge (stage 18; orphan-panel fix 2026-05-30) ---
    # 这些 opt-in stage 产出 bank-year FEATURE 面板, 其列为下游 Stata/codebook
    # 既有契约期待 (*_staleness 等), 但此前无任何代码把它们
    # 并入 40_panel_yearly。条件左连接 (opt-in stage 未运行 → 文件缺失 → graceful no-op)。
    # 39f (cross_media_alpha) 同属此孤儿类 (bank-year; cross_outlet_tone_variance_* 为
    # 下游 Stata 契约列 — ⚠ 与 paper 10 spec 冻结 main treatment 同名异构,
    # 事件窗条件方差而非 spec 的全年截面口径, 见 cross_media_alpha.py 模块 docstring
    # 披露 fix(omni-g-audit-family-08, 2026-06-11)), 但它是 validation-class
    # (run_pipeline_validation 中, 排在 stage 45 之后)。故正常单趟主链运行时其文件尚不
    # 存在 → graceful skip; 仅当 validation 已先产出 39f 后再 (重)建面板时才并入。
    # fix(omni-g-runner-16, 2026-06-11): merge 逻辑收敛到
    # _merge_optin_feature_panels — 在旧 exists 守卫之上加 (1) 新鲜度守卫
    # (特征文件 mtime ≥ 其登记上游, 陈旧代际 → 跳过并 loud-warn, 防 06-03 的
    # 39f 被并入 06-10 重生面板的 run-顺序依赖) + (2) 重复键 fail-loud
    # (替代旧 drop_duplicates keep='first' 静默取首行, 旧行为使行数守卫永真空转)。
    panel = _merge_optin_feature_panels(panel, OUTPUT_DIR)

    phase_durations['④注意力+地理+IV/DID+网络族 (6b→8e)'] = time.time() - _t_attn

    # --- 8z. IV 扩展族 (11 论文工具变量补全, 2026-06-13) ---
    # 必须在全部面板 merge 之后: 消费 attention_index (步骤 6) / sub_frac 等
    # 分类 frac (步骤 5) / benefit_mean_full (7h-benefit) / bank_type+share
    # (7e) / bank_zone (7f)。引擎与引用见 pipeline/panel/iv_extensions.py。
    _t_ivx = time.time()
    _ivx_type_map, _ = load_bank_group_maps()
    # 基期解析与步骤 7e 完全同口径 (share 复用 7e 产物, 掩码须一致)
    _ivx_base_cfg = PANEL_CFG.get('bartik_base_year', 'auto')
    if _ivx_base_cfg == 'auto' or _ivx_base_cfg is None:
        _ivx_T0 = max(int(panel['year'].min()), 2010)
    else:
        _ivx_T0 = int(_ivx_base_cfg)
    panel = compute_iv_extensions(panel, df_exploded,
                                  _ivx_type_map, [_ivx_T0])
    phase_durations['⑤IV 扩展族 compute_iv_extensions (8z)'] = time.time() - _t_ivx

    # ── 【结果分析】(仅日志, 不回写 panel/产物; golden-safe) ──
    # 取最终 panel 的真实产出指标, 对照阈值/预期方向给出好/坏/临界判读,
    # 让 <stage>.log 自带"这次跑出来对不对"的体检报告。
    # crash-guard: 整块仅做"读数据算指标"的诊断, 全部包进 try/except —— 本块在
    # export_panel 写盘之前执行, 若任一指标计算抛异常 (空 Series / 缺列 / int(NaN)),
    # 绝不能让阶段崩溃丢产物 (这才是真 golden-safe)。
    try:
        logger.info("-" * 72)
        logger.info("【结果分析】Bank-Year 面板总装收尾, 关键产出指标体检:")

        _n_rows = len(panel)
        _n_banks = panel['target_bank'].nunique() if 'target_bank' in panel.columns else 0
        # NaN-guard: year 列全空 (空面板 / 上游异常) 时 min()/max() 为 NaN,
        # int(NaN) 会 ValueError → 用 notna 守卫退化为 0 跨度, 不进数值判断。
        if 'year' in panel.columns and panel['year'].notna().sum() > 0:
            _y_min, _y_max = int(panel['year'].min()), int(panel['year'].max())
            _n_years = _y_max - _y_min + 1
            _yr_span = f"{_y_min}-{_y_max}"
        else:
            _y_min, _y_max, _n_years, _yr_span = 0, 0, 0, "无有效年份(全 NaN)"
        logger.info(
            f"  · 面板维度: {_n_rows:,} 行 = {_n_banks} 银行 × {_n_years} 年 "
            f"({_yr_span}); 入站文章-银行级行数 {len(df_exploded):,}"
        )

        # (1) 结构完整性自检: 实际行 vs 理论笛卡尔积 (Wooldridge 2010 / Baltagi 2021)
        # ⚠ 这不是"名册对齐质量"指标: balance_panel (encode.py:2017-2021) 已用
        #   MultiIndex.from_product([all_banks, all_years]) 把 panel 强制补成完整
        #   笛卡尔积, 且下游无删行/删银行/删年份操作 → 干净 run 上 _n_rows 结构性
        #   恒 = _theo, 平衡率应 ==100.0%。故此处只作二值自检: 偏离 100% 即下游
        #   merge 产生了重复/丢失 (bank,year) 键 (而 _merge_optin_feature_panels
        #   L2247 已对重复键 fail-loud 拦截), 是异常告警而非"规整度"度量。
        _theo = _n_banks * _n_years
        _bal = _n_rows / _theo if _theo > 0 else 0.0
        if _theo <= 0:
            _bal_verdict = "无法计算 (银行数或年份跨度为 0, 见上方维度行)"
        elif _n_rows == _theo:
            _bal_verdict = "✅ 通过 (==100.0%, post-balance_panel 笛卡尔积; 行=banks×years)"
        else:
            _bal_verdict = ("🔴 异常 (≠100%, 下游 merge 产生重复/丢失 (bank,year) 键; "
                            "正常应被 _merge_optin_feature_panels fail-loud 拦截)")
        logger.info(
            f"  · 结构完整性自检: 实际 {_n_rows:,} / 理论笛卡尔积 {_theo:,} = "
            f"{pct4(_bal)} → {_bal_verdict}"
        )
        # 真实覆盖率 (信号密度): 有报道 bank-year 占完整笛卡尔积比例 —— 这才是有信息量
        # 的口径 (零报道行已笛卡尔补全为缺失, has_coverage=0); 越高=真实信号越密。
        if 'has_coverage' in panel.columns and _theo > 0:
            _cov_frac = int(panel['has_coverage'].sum()) / _theo
            logger.info(
                f"  · 真实信号密度: 有报道 bank-year 占完整笛卡尔积 = {pct4(_cov_frac)} "
                f"(越高信号越密; 零报道格已笛卡尔补全为缺失行)"
            )

        # (2) 新闻覆盖: 零新闻行应为"缺失"而非数值零 (护回归口径)
        if 'n_articles' in panel.columns:
            _no_news = int((panel['n_articles'] == 0).sum())
            _no_news_pct = _no_news / _n_rows if _n_rows > 0 else 0.0
            _cov_rows = _n_rows - _no_news
            _na = panel['n_articles']
            _na_pos = _na[_na > 0]
            _na_mean = float(_na_pos.mean()) if len(_na_pos) > 0 else 0.0
            logger.info(
                f"  · 新闻覆盖: 有报道 bank-year {_cov_rows:,} / 零报道 {_no_news:,} "
                f"({pct4(_no_news_pct)}); 有报道行均篇数 {sig4(_na_mean)}"
            )
            if 'has_coverage' in panel.columns:
                _hc = int(panel['has_coverage'].sum())
                logger.info(
                    f"    has_coverage=1 共 {_hc:,} 行 (仅这些行带情感信号; 零报道行 tone=NaN, "
                    f"刻意不填零以防回归口径污染)"
                )

        # (3) 主处理变量 (treatment; P1 注册主规格): llm_vote_tone_full (entity-attributed, full 轨;
        #     CLAUDE.md / papers/bank_fintech_tone/paper_spec 锁定 main=llm_vote_tone_full (full-only 2026-06-29),
        #     Tetlock 2007 / Loughran-McDonald 2016); llm_vote_tone_ctx 为 conditional-on-full 稳健性轨,
        #     此处一并报告作 robustness 对照, 但不冠以"P1 主线"避免误判落盘主回归 treatment。
        for _tone_col, _tone_lab in (
            ('llm_vote_tone_full', '媒体语调主测度 llm_vote_tone_full (full 轨, P1 注册主规格)'),
            ('llm_vote_tone_ctx', '媒体语调 llm_vote_tone_ctx (ctx 轨, conditional-on-full 稳健性对照)'),
        ):
            if _tone_col not in panel.columns:
                # full 缺列才告警 (主规格); ctx 缺列降级 info
                if _tone_col == 'llm_vote_tone_full':
                    logger.warning(
                        "  · ⚠️ 主处理变量(treatment) llm_vote_tone_full (P1 主规格) 列缺失: "
                        "stage 21 产物可能未就绪"
                    )
                continue
            _tone = panel[_tone_col].dropna()
            if _tone.notna().sum() == 0:
                logger.warning(
                    f"  · ⚠️ {_tone_col} 该轨无有效数据(全 NaN): "
                    "检查上游 stage 21 LLM 投票是否落盘"
                )
                continue
            _tm = float(_tone.mean())
            _dir = "整体偏乐观(>0)" if _tm > 0 else ("整体偏悲观(<0)" if _tm < 0 else "中性(≈0)")
            logger.info(
                f"  · {_tone_lab}: mean={sig4(_tm)} ({_dir}), "
                f"std={sig4(_tone.std())}, 非缺 {len(_tone):,}/{_n_rows:,} 行"
            )

        # (4) 内容属性二元分割 (P4 locus): 底层技术占比偏向
        if 'tech_frac' in panel.columns:
            _tf = panel['tech_frac'].dropna()
            if _tf.notna().sum() == 0:
                logger.info("  · tech_frac 该轨无有效数据(全 NaN; 盘面或无 locus 二元分类标注, 优雅降级)")
            else:
                _tfm = float(_tf.mean())
                logger.info(
                    f"  · 底层技术占比 tech_frac: mean={sig4(_tfm)} "
                    f"({'偏底层技术' if _tfm > 0.5 else '偏应用场景'}; 0=应用/1=底层), "
                    f"非缺 {len(_tf):,} 行"
                )
        for _sfx, _lab in [('_tech', '底层技术'), ('_app', '应用场景')]:
            _col = f'n_articles{_sfx}'
            if _col in panel.columns and 'n_articles' in panel.columns:
                _has_cat = int((panel[_col] > 0).sum())
                _tot = int((panel['n_articles'] > 0).sum())
                if _tot > 0:
                    logger.info(
                        f"    {_lab} ({_col}): 有该类文章 bank-year = {_has_cat}/{_tot} "
                        f"({pct4(_has_cat / _tot)})"
                    )

        # (5) P2 注意力指数 (Fang-Peress 2009 extensive 覆盖; 全集脊柱 LEFT-join 零填 0)
        if 'attention_index_full' in panel.columns:
            _ai = panel['attention_index_full'].dropna()
            if _ai.notna().sum() == 0:
                logger.info("  · attention_index_full 该轨无有效数据(全 NaN), 跳过")
            else:
                _ai_nz = int((_ai > 0).sum())
                logger.info(
                    f"  · 金科注意力指数 attention_index_full: mean={sig4(float(_ai.mean()))}, "
                    f"max={sig4(float(_ai.max()))}; >0 的 bank-year {_ai_nz:,}/{len(_ai):,} "
                    f"(零-fintech 行被刻意填 0, 非 NaN)"
                )

        # (6) 三轨承载体检: 统计实际落盘的 _full/_ctx/_ss 列数 (ss 首跑前可整体缺)
        _track_counts = {}
        for _tk in ('_full', '_ctx', '_ss'):
            _track_counts[_tk] = sum(1 for _c in panel.columns if _c.endswith(_tk))
        logger.info(
            f"  · 三轨列承载: _full={_track_counts['_full']} / _ctx={_track_counts['_ctx']} / "
            f"_ss={_track_counts['_ss']} 列; 面板总列数 {panel.shape[1]:,} "
            f"(导出前计数, 不含导出期无条件物化的 low_conf_flag — 阶段摘要处 +1 为 "
            f"by-design, 见 export._materialize_low_conf_flag)"
        )
        if _track_counts['_ss'] == 0:
            logger.warning(
                "    ⚠️ _ss 三轨列为 0: stage 21 付费 ss 跑尚未播种缓存属预期 "
                "(REQUIRED_PANEL_COLUMNS 刻意不含 _ss, 不阻塞导出); 全量上线后应非零。"
            )
        elif _track_counts['_ss'] < _track_counts['_ctx'] * 0.5:
            logger.warning(
                f"    ⚠️ _ss({_track_counts['_ss']}) 远少于 _ctx({_track_counts['_ctx']}): "
                "ss 轨可能部分缺列, 检查 stage 21 ss 缓存覆盖率。"
            )

        # (6b) IV 家族列承载诊断 (Bartik/LOO/LLM-peer; 纯计数+平均有效率, golden-safe)
        #   IV 列多由 LLM/嵌入派生 → 第一阶段识别力随生产 T=19 才充分 (早期试跑盘面 T=2 偏弱)。
        try:
            _iv_fams = {
                'Bartik 移位份额': [c for c in panel.columns if 'bartik' in c.lower()],
                'LOO 同组留一': [c for c in panel.columns
                               if 'leave_one_out' in c.lower() or 'leave1out' in c.lower()
                               or 'l1o' in c.lower() or 'leave1' in c.lower()],
                'LLM-peer 工具': [c for c in panel.columns
                                if c.startswith('llm_peer_tone_iv')
                                or c.startswith('llm_peer_coverage_iv')],
            }
            for _fam, _cols in _iv_fams.items():
                if _cols:
                    _vfrac = sum(float(panel[c].notna().mean()) for c in _cols) / len(_cols)
                    logger.info(
                        f"  · IV 家族 {_fam}: {len(_cols):,} 列, 平均有效率 {pct4(_vfrac)} "
                        "(第一阶段识别力诊断; 早期试跑盘面 T=2 偏弱, 生产 T=19 方充分)"
                    )
        except Exception as _eiv:  # noqa: BLE001 — IV 诊断块绝不崩阶段
            logger.info(f"  · IV 家族诊断跳过 (不影响产物): {_eiv}")

        # (7) 小样本(早期试跑盘面 T=2)守卫: 提醒结论以全量 约1,819万/T=19 为准
        if 0 < _n_years <= 3 or _n_rows < 300:
            logger.info(
                f"  · ⚠️ 小样本盘面 (T={_n_years}, {_n_rows:,} 行): 本次仅验证管道正确性与 "
                "schema 完整性, 一切回归级数值结论以全量 约1,819万 语料 / T=19 (2007-2025) 实测为准。"
            )
        logger.info("-" * 72)
    except Exception as _e:
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")

    _t_export = time.time()

    # --- 8z-bd. BERT 分布形状文章级中间列单点 drop (2026-07-03 执行计划 §2.6) ---
    # 挂载点 = 步骤 9 导出块入口 (log_diagnostics 之前): 中间列 (`_ent_*`/
    # `_xneg_ind_*`/`_nt_art_*`/`_xmd_art*`/`_lblhet_art*`, 非 `_is_` 前缀故
    # 6c sweep 不清) 若不显式 drop 会随 export_panel 全列写入
    # 40_article_bank_level.parquet。交集清单天然容忍合法缺席轨; 单点挂载
    # (显式否决双 call site — 省的内存 < 两处维护漂移风险)。
    _bd_drop = [c for c in bert_distribution.iter_intermediate_cols(BERT_MODELS)
                if c in df_exploded.columns]
    if _bd_drop:
        df_exploded.drop(columns=_bd_drop, inplace=True)
        logger.info(f"  BERT 分布形状中间列已清理: {len(_bd_drop)} 列 (导出前单点 drop)")

    log_diagnostics(panel, df_exploded)

    # --- 9. 导出 ---
    export_panel(panel, df_exploded)
    phase_durations['⑥诊断+多格式导出 log_diagnostics/export_panel'] = time.time() - _t_export

    # ── ⏱ per-phase 墙钟计时汇总 (纯日志, golden-safe) ──
    try:
        _total_phase = sum(phase_durations.values())
        logger.info("-" * 72)
        logger.info("  ⏱ 各子步墙钟耗时 (秒, 4 位有效数字):")
        for _pname, _pdur in phase_durations.items():
            _share = (_pdur / _total_phase) if _total_phase > 0 else 0.0
            logger.info(f"     · {_pname}: {sig4(_pdur)} 秒 ({pct4(_share)})")
        logger.info(f"     · 计时子步合计: {sig4(_total_phase)} 秒 "
                    f"(阶段总墙钟见下方 stage summary, 含 banner/方法块/结果分析等未计时段)")
        logger.info("-" * 72)
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"[计时汇总] 打印异常, 跳过(不影响产物): {_e}")

    # --- 阶段摘要 ---
    log_stage_summary(
        logger, STAGE_NAME, start_time,
        input_rows=len(df_exploded),
        output_rows=len(panel),
        extra_info={
            '唯一银行数': panel['target_bank'].nunique(),
            '年份跨度': f"{panel['year'].min()}-{panel['year'].max()}",
            '零新闻观测占比': pct4((panel['n_articles'] == 0).mean()),
            '面板总列数': panel.shape[1],
            '分类指标': '已生成' if 'n_articles_tech' in panel.columns else '未生成',
        }
    )

    logger.info("40_panel_export_main 执行完毕 ✓")


if __name__ == '__main__':
    main()
