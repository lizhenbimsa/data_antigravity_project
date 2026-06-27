"""news_process.pipeline.panel.stata_export — Stage 46 Stata 数据导出层 (v3.2.0)

功能 (plan v14 §9.1):
    把 stage 45 panel parquet (40_panel_yearly.parquet) 转换为 Stata .dta + labels.

输出 (2026-06-12 起单一全列 .dta; 本机 StataNow/MP 19.5 maxvar≤120,000 直读全列,
不再做 core/aux 双切分 — 原 IC ≤2048 兼容切分仅为外部协作者保留, 已按项目策略移除):
    46_panel_yearly_full.dta    # 全列 (Stata SE/MP; 唯一 .dta 产物)
    46_panel_yearly_labels.do   # variable/value labels Stata 脚本
    46_panel_yearly_codebook.xlsx  # 人类可读变量字典 (2026-06-21: 取消 is_core 核心/辅助列区分, 全列均为分析列)

关键转换 (plan v14 §9.1; v3.4.0 +collab_mode):
    - innovation_locus_{full,ctx,ss} (中文 str) → byte 0=底层技术, 1=应用场景 + value label
    - innovation_substantiveness_{full,ctx,ss} (中文 str) → byte 0=实质性, 1=象征性 + value label
    - innovation_collab_mode_{full,ctx,ss} (中文 str) → byte 0=自主研发, 1=外部协同 + value label  [v3.4.0; ss v3.9.0]
      ⚠ 上述 3 组类别编码仅当列存在时启用 — 当前 bank-year panel 不含这些文章级
      str 列 (仅有派生数值聚合 avg_*_prob_score / *_frac 等), encoder 为 no-op,
      盘上 .dta value label = 0; 保留以服务未来文章级/众数面板导出场景
      [fix(omni-g-stata-export-14, 2026-06-11) 诚实披露]
    - NaN → . (统一 sysmiss; extended missing .a/.b 未实现 — 两后端均不传
      missing_user_values, 缺失原因在 .dta 中不可区分)
      [fix(omni-g-stata-export-04/10/13, 2026-06-11): 原声称 ". / .a / .b
      distinguishable causes" 从未实现, 改为与实现对齐]
    - 非 value-labeled int8/Int8 计数列升 Int16 写出 (Stata byte 合法值域
      [-127,100], 101..127 是缺失码位 `.` + .a-.z; 防 pyreadstat 直写损值)
      [fix(omni-g-stata-export-01, 2026-06-11), KNOWN-OPEN ⑥]
    - 列名 ≤ 32 字符 (Stata 硬限)
    - variable label ≤ 80 字符 (Stata 硬限)

锚定文献:
    Westphal & Zajac (1994, 1998, ASQ) substantive-symbolic
    Gomber, Kauffman, Parker, Weber (2018, JMIS) enabling tech vs business function
    Chesbrough (2003) Open Innovation; Laursen & Salter (2006, SMJ) [v3.4.0 第三维度]
    Hassan, Hollander, van Lent, Tahoun (2019, QJE) entity-proximity attribution

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 46_stata_export.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**输入**: `40_panel_yearly.parquet` (stage 45 产出的 bank-year 全列面板; main() 经 CONFIG['filenames']['output_40_panel_yearly'] 解析路径, 缺失则 FileNotFoundError)。

**处理步骤 (export_panel_to_stata)**:
1. `_select_dta_backend`: 优先 pyreadstat (嵌入 value labels + 中文 column labels), 缺失则 fallback pandas `to_stata` 并 WARN (两后端 .dta 二进制不等价: pandas 路径不嵌 value label, 须手动 run labels.do; nullable Int 存储宽度也可能不同)。
2. `encode_categorical_columns`: 三套中文类别 str → byte 0/1 + value label —— LOCUS (底层技术=0/应用场景=1)、SUBSTANTIVENESS (实质性=0/象征性=1)、COLLAB_MODE (自主研发=0/外部协同=1), 各覆盖 full/ctx/ss 三轨列名。`_map_categorical_failloud` 对未登记类别值 raise (不静默 NaN 化)。当前 bank-year 面板不含这些文章级 str 列 → encoder 为 no-op (value_labels={}, 诚实披露 fix(omni-g-stata-export-14))。
3. `upcast_unsafe_int8_columns`: 非 value-labeled int8/Int8 计数列升 Int16 (Stata byte 合法值域 [-127,100], 101..127 是缺失码位 `.`/.a-.z, 防 pyreadstat 直写损值)。
4. `shorten_long_column_names`(>32 字符缩写→截断→md5 后缀去重) + `asciify_non_ascii_columns`(中文情感标签 正面/负面/中性 → pos/neg/neu, 残留非 ASCII 移除), 全程同步 value_labels 键 + `rename_map` 链式压平 (`_chase_original` 反查最初原名); 写前跑 `_assert_track_triplet_unique` 三轨唯一性断言。
5. `build_variable_labels`(改名列经 rename_map 反查原名命中 codebook meta / HEURISTIC_LABELS / 列名兜底, 按 UTF-8 字节边界截断 ≤80 字节) → `validate_stata_compat` (列名 ≤32 + 合法 Stata 标识符 + label ≤80 字节)。
6. `write_dta` 写单一 `*_full.dta`; `write_labels_do_file` 写 labels.do (compound double quotes 安全转义); `_write_codebook_xlsx` 写 codebook (engine='xlsxwriter', 非阻塞, 失败仅 WARN; 2026-06-21 起 codebook 全列均为分析列, 不再有 is_core 区分 — assign_core_columns/core_patterns 已退役)。

**关键转换规则**: NaN→. (统一 sysmiss, extended missing .a/.b 未实现 — 两后端均不传 missing_user_values); .dta format version=118 (文件格式编号, 非 Stata 应用版本); 列名≤32 + 变量标签≤80 字节。

**外部依赖**: pyreadstat (可选, 推荐) 或 pandas 原生 to_stata; xlsxwriter (codebook)。无 LLM/Embedding/网络。timeout=600 (小面板 ~168 行 < 1 分钟)。确定性: 纯函数转换, 输入 parquet 固定则输出值稳定 (二进制随 backend 选择漂移)。

**DAG 位置**: 上游 stage 45 (40_panel_yearly.parquet); 下游为外部 Stata 研究者 / 11 篇论文的 .do 模板消费 (本机 StataNow/MP 19.5 maxvar≤120,000 直读全列 full.dta)。

■ 白话说明

**这一步是什么**: 这是数据的"出关口岸"。Python 算出来的那张大表格 (parquet 格式) 经济学家的 Stata 软件读不了, 这一步负责把它翻译成 Stata 能直接打开的 .dta 文件, 并且给每一列贴上看得懂的英文标签 (比如把 llm_vote_tone_full 标注成媒体乐观度), 再附一份 Excel 字典告诉人每列是什么意思。打个比方: Python 给数据起了很长的名字, 但古老的 Stata 只认 32 个字母的短名, 这一步就是严格的护照审查员, 把长名字安全剪短、防止两列剪短后撞名、再盖上学术标签。

**为什么需要它**: 全世界经济金融论文几乎都用 Stata 跑回归出表。如果没有这一步, 研究者拿到的就是一堆 Python 才认识的文件, 没法直接做实证。它还把缺失值、中文类别、整数溢出这些水土不服的细节统一处理好, 保证 Stata 一打开就能跑。

**做得好不好的影响**: 标签贴得全不全、列名剪得对不对, 直接决定研究者能不能看懂数据、会不会跑错变量。如果两列名字剪短后撞名 (碰撞) 或某列因整数溢出被 Stata 误读成缺失, 回归结果就会悄悄出错却很难发现。它本身不改数据数值, 但它是最终封印——交付给人手里的那份数据干不干净, 全看这一步。
========================================================================
"""
from __future__ import annotations

import logging
import os
from typing import Dict, List, Tuple

import pandas as pd

from news_process.core.logging import pct4, sig4

logger = logging.getLogger(__name__)

# Stata 硬限 (plan v14 §9.5 / R32-D, R42-A 修复)
STATA_VAR_NAME_MAXLEN = 32      # 变量名最长 32 字符
STATA_VAR_LABEL_MAXLEN = 80     # 变量标签最长 80 字符
# 2026-06-21: STATA_IC_MAX_VARS (Stata IC ≤2048 列守卫) + assign_core_columns +
# core_patterns + codebook is_core 列一并退役 — codebook 取消"分析核心列 vs 辅助列"
# 区分 (所有列均为分析列); 本机 StataNow/MP 19.5 直读全列, 无 IC 列数约束。

# v3.2.0 类别 → byte encoding 映射 (plan v14 §9.1 + R32-B 编码方向论证)
# 关键: 0=baseline, 1=对照 (洗稿率框架天然解释方向)
LOCUS_ENCODING: Dict[str, int] = {
    '底层技术': 0,
    '应用场景': 1,
}

SUBSTANTIVENESS_ENCODING: Dict[str, int] = {
    '实质性': 0,
    '象征性': 1,
}

# v3.4.0: 第三维度 collab_mode (Chesbrough 2003 + L&S 2006 SMJ; positive_class=外部协同)
# 关键: 0=自主研发 (closed innovation / baseline), 1=外部协同 (open innovation / 对照)
# 与 substantiveness/locus 同模式: 0=baseline, 1=对照 (paper 主回归 treatment 焦点)
COLLAB_MODE_ENCODING: Dict[str, int] = {
    '自主研发': 0,
    '外部协同': 1,
}

# v3.5.0 D2: cell_id 1..8 value label (per stage3_v3_5_0_augmentation_plan.md §2.1.3)
# cell_id = subst*4 + locus*2 + collab + 1
# cell 1 = (0, 0, 0) = 实质性·底层技术·自主研发 (三维全 baseline)
# cell 8 = (1, 1, 1) = 象征性·应用场景·外部协同 (三维全 contrast)
# value label 全用 ASCII 字符以保证 Stata 兼容 (value label 总量 32K bytes 软上限).
CELL_ID_VALUE_LABEL: Dict[int, str] = {
    1: 'sub.tech.indep',  2: 'sub.tech.collab',
    3: 'sub.app.indep',   4: 'sub.app.collab',
    5: 'symb.tech.indep', 6: 'symb.tech.collab',
    7: 'symb.app.indep',  8: 'symb.app.collab',
}

# v3.5.0 D4: d4_data_quality_flag 字符串列的取值映射 (per plan §2.3.4 F6)。
# 刻意以 str 列落盘 (不做 byte 编码), 让 Stata 用户直接看到可读值。
# Stata 端典型用法: `keep if d4_data_quality_flag == "ok"` 过滤不可信 ctx coverage.
D4_DATA_QUALITY_FLAG_VALUES = ('ok', 'insufficient')

# Value labels (双语 zh + EN, plan v14 §9.1 普通人版变更 20)
LOCUS_VALUE_LABELS: Dict[int, str] = {
    0: "底层技术 (Technology)",
    1: "应用场景 (Application)",
}

SUBSTANTIVENESS_VALUE_LABELS: Dict[int, str] = {
    0: "实质性 (Substantive)",
    1: "象征性 (Symbolic)",
}

COLLAB_MODE_VALUE_LABELS: Dict[int, str] = {
    0: "自主研发 (Independent R&D / Closed Innovation)",
    1: "外部协同 (External Collaboration / Open Innovation)",
}


def _map_categorical_failloud(series: pd.Series, encoding: Dict[str, int], col: str) -> pd.Series:
    """fix(omni-g-stata-export-04/11, 2026-06-11): 类别映射 + 未登记值 fail-loud 守卫.

    pandas ``.map()`` 对不在映射表内的非空值静默返回 NaN — 上游 LLM 噪声/新类别
    (如 '不适用'、空白变体) 会与『真缺失』在 .dta 中不可区分地合流。此处对账
    notna-before vs isna-after, 任何未登记类别值直接 raise (而非静默丢值)。
    """
    mapped = series.map(encoding)
    unmapped = series.notna() & mapped.isna()
    if unmapped.any():
        samples = series[unmapped].astype(str).unique()[:5].tolist()
        raise ValueError(
            f"encode_categorical_columns: 列 '{col}' 含 {int(unmapped.sum())} 个未登记"
            f"类别值 (不在编码表 {sorted(encoding)} 中), 样本: {samples}. "
            f"静默 NaN 化会与真缺失合流 — 请先在上游清洗或扩充编码映射表."
        )
    return mapped.astype('Int8')


def encode_categorical_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Dict[int, str]]]:
    """把 stage 3 字符串列编码为 byte 0/1 + 收集 value labels.

    fix(omni-g-stata-export-11/14, 2026-06-11) 披露: 当前 bank-year panel 不含
    这些文章级 str 列 (encode.py 聚合期已消费), 本函数对其恒为 no-op →
    value_labels={} — 保留以服务未来文章级/众数面板导出场景。
    未登记类别值 fail-loud raise 而非静默 NaN (见 _map_categorical_failloud)。

    三轨 (full/ctx/ss): 第三轨 _ss = 银行+金科同句共现轨, 仅当 stage 21 真物化
    innovation_*_ss 文章级 str 列时才编码 (``if col in df.columns`` 守卫, 缺列
    优雅跳过, 与 full/ctx 同义)。

    Args:
        df: panel DataFrame 含 innovation_locus_{full,ctx,ss} 与
            innovation_substantiveness_{full,ctx,ss} 字符串列 (若存在).
    Returns:
        (encoded_df, value_labels_dict): {var_name: {int_code: label_str}}
    """
    df = df.copy()
    value_labels: Dict[str, Dict[int, str]] = {}

    # 三轨 (full/ctx/ss): _ss = 银行+金科同句共现轨, IFF stage 21 物化对应列才编码
    for col in ['innovation_locus_full', 'innovation_locus_ctx', 'innovation_locus_ss']:
        if col in df.columns:
            df[col] = _map_categorical_failloud(df[col], LOCUS_ENCODING, col)
            value_labels[col] = LOCUS_VALUE_LABELS

    for col in ['innovation_substantiveness_full', 'innovation_substantiveness_ctx', 'innovation_substantiveness_ss']:
        if col in df.columns:
            df[col] = _map_categorical_failloud(df[col], SUBSTANTIVENESS_ENCODING, col)
            value_labels[col] = SUBSTANTIVENESS_VALUE_LABELS

    # v3.4.0: 第三维度 collab_mode encoding (Chesbrough 2003); 三轨含 _ss
    for col in ['innovation_collab_mode_full', 'innovation_collab_mode_ctx', 'innovation_collab_mode_ss']:
        if col in df.columns:
            df[col] = _map_categorical_failloud(df[col], COLLAB_MODE_ENCODING, col)
            value_labels[col] = COLLAB_MODE_VALUE_LABELS

    return df, value_labels


def build_variable_labels(
    df: pd.DataFrame,
    rename_map: Dict[str, str] = None,
) -> Dict[str, str]:
    """为每列生成 ≤ 80 字节英文 variable label.

    fix(omni-g-stata-export-05/09, 2026-06-11): 新增 rename_map 参数
    ({short_stata_name: original_panel_name}) — codebook meta 与
    HEURISTIC_LABELS 均以原始 panel 列名为键, 此前被 shorten/asciify 改名的
    列按短名查找必 miss, 人工标签静默退化为列名 fallback。

    优先级:
        1. codebook meta[原名].label (若改名, 先按原名查)
        2. HEURISTIC_LABELS[原名]
        3. codebook meta[短名].label / HEURISTIC_LABELS[短名] (兜底)
        4. fallback: 原始列名本身 (保留被截断吃掉的判别后缀信息)

    所有 label 强制按 UTF-8 字节边界截断至 80 字节 (R32-H + R40-A;
    fix(omni-g-stata-export-02/08, 2026-06-11): 原实现字节判定+字符切片,
    CJK 标签『越截越长』并触发 validate_stata_compat raise).
    """
    rename_map = rename_map or {}
    labels: Dict[str, str] = {}
    try:
        from news_process.pipeline.panel.codebook import get_variable_metadata_dict
        meta = get_variable_metadata_dict()
    except Exception as e:
        logger.warning(f"codebook metadata 不可用 ({e}), 使用启发式标签")
        meta = {}

    # 启发式映射 (覆盖三轨 (full/ctx/ss) 列, codebook 未及时同步时的 fallback)
    HEURISTIC_LABELS: Dict[str, str] = {
        'n_articles_llm_valid':             "News count, LLM-valid (category-frac denominator)",
        'n_articles_llm_valid_ctx':         "News count, ctx-track LLM-valid (ctx category-frac denom)",
        'innovation_locus_full':            "Innovation Locus (Full-text, Gomber 2018 JMIS)",
        'innovation_locus_ctx':             "Innovation Locus (Entity-context, Hassan 2019 QJE)",
        'innovation_substantiveness_full':  "Innov. Substantiveness (Full-text, W&Z 1998 ASQ)",
        'innovation_substantiveness_ctx':   "Innov. Substantiveness (Entity-ctx, Hassan 2019 QJE)",
        'innovation_collab_mode_full':      "Innov. Collab Mode (Full-text, Chesbrough 2003)",
        'innovation_collab_mode_ctx':       "Innov. Collab Mode (Entity-ctx, Hassan 2019 QJE)",
        'innovation_collab_mode_confidence_full': "Collab Mode Confidence (Full-text, raw LLM)",
        'innovation_collab_mode_confidence_ctx':  "Collab Mode Confidence (Entity-ctx, raw LLM)",
        'category_confidence_full':         "Locus Confidence (Full-text, hybrid LLM+keyword)",
        'category_confidence_ctx':          "Locus Confidence (Entity-ctx, hybrid LLM+keyword)",
        'llm_verified_dual_full_only':      "Dual Gate: Full-track only verified",
        'llm_verified_dual_ctx_only':       "Dual Gate: Ctx-track only verified",
        'llm_verified_dual_both':           "Dual Gate: Both tracks verified",
        'tone_gap_tech_app_lc_ctx':         "Tone Gap: Tech-App (Loc=Ctx, ctx sentiment)",
        'tone_gap_sub_symb_sc_ctx':         "Tone Gap: Sub-Symb (Subst=Ctx, ctx sentiment)",
        'tech_frac_lc':                     "Frac of Tech-locus articles (ctx classification)",
        'app_frac_lc':                      "Frac of App-locus articles (ctx classification)",
        'sub_frac_sc':                      "Frac of Substantive articles (ctx classification)",
        'symb_frac_sc':                     "Frac of Symbolic articles (ctx classification)",
        # Plan v1.37 P2 §5.3.4: 二元 prob_score 列的标签 (每条 ≤ 80 UTF-8
        # 字节; em-dash 占 3 字节; positive_class = 象征性 / 应用场景 / 外部协同, 与
        # stata_export 编码 1=对照 一致)。三维对称补 collab (2026-06-14)。
        'avg_subst_prob_score_full':        "Avg Subst P_BIN (full-track) — 1=symbolic, max-ent map",
        'avg_subst_prob_score_std_full':    "Std Subst P_BIN (full-track, bank-year SD)",
        'avg_subst_prob_score_ctx':         "Avg Subst P_BIN (ctx-track) — 1=symbolic, max-ent map",
        'avg_subst_prob_score_std_ctx':     "Std Subst P_BIN (ctx-track, bank-year SD)",
        'avg_locus_prob_score_full':        "Avg Locus P_BIN (full-track) — 1=application, max-ent map",
        'avg_locus_prob_score_std_full':    "Std Locus P_BIN (full-track, bank-year SD)",
        'avg_locus_prob_score_ctx':         "Avg Locus P_BIN (ctx-track) — 1=application, max-ent map",
        'avg_locus_prob_score_std_ctx':     "Std Locus P_BIN (ctx-track, bank-year SD)",
        'avg_collab_prob_score_full':       "Avg Collab P_BIN (full-track) — 1=external/open, max-ent map",
        'avg_collab_prob_score_std_full':   "Std Collab P_BIN (full-track, bank-year SD)",
        'avg_collab_prob_score_ctx':        "Avg Collab P_BIN (ctx-track) — 1=external/open, max-ent map",
        'avg_collab_prob_score_std_ctx':    "Std Collab P_BIN (ctx-track, bank-year SD)",
        # v3.5.1 A1 Lexical Clarity (LM 2011 JF 66:1; You 2018 hhx055 Panel C/D)
        # 三轨 (full/ctx/ss) 独立扫描; 每条 ≤ 80 UTF-8 bytes (per plan v0.3 §2.4.1 frozen at D0).
        'mean_clarity_score_full':          "Mean Clarity Score from indep Full-text scan (LM 2011 JF; You 2018)",
        'mean_clarity_score_ctx':           "Mean Clarity Score from indep Ctx-text scan (LM 2011 JF; You 2018)",
        # v3.10.0: L&M 2011 JF 中文主译第 6 部主词典 tone + 纯计数版 (negonly) + 2 新非情感子集.
        'loughran_tone_full':               "Avg Tone Loughran-McDonald 2011 JF Chinese 6th dict (full-track)",
        'loughran_tone_ctx':                "Avg Tone Loughran-McDonald 2011 JF Chinese 6th dict (ctx-track)",
        'loughran_tone_ss':                 "Avg Tone L-M 2011 JF Chinese (bank+fintech same-sentence track)",
        'loughran_negonly_tone_full':       "Avg Tone L-M counts-faithful (negonly, rule-reduced) full-track",
        'loughran_negonly_tone_ctx':        "Avg Tone L-M counts-faithful (negonly, rule-reduced) ctx-track",
        'loughran_negonly_tone_ss':         "Avg Tone L-M counts-faithful (negonly) same-sentence track",
        'modal_weak_frac_full':             "Frac Weak-Modal words (L-M 2011 JF; Bochkay 2020) full-track",
        'modal_weak_frac_ctx':              "Frac Weak-Modal words (L-M 2011 JF; Bochkay 2020) ctx-track",
        'modal_weak_frac_ss':               "Frac Weak-Modal words (L-M 2011 JF) same-sentence track",
        'complexity_frac_full':             "Frac Complexity words (L-M 2011 JF complexity list) full-track",
        'complexity_frac_ctx':              "Frac Complexity words (L-M 2011 JF complexity list) ctx-track",
        'complexity_frac_ss':               "Frac Complexity words (L-M 2011 JF) same-sentence track",
        # 2026-06-20 对称补全: 其余 5 部情感词典的 headline 极性 tone + negonly 列 curated
        # 标签 (此前唯 loughran 有这 6 个 headline 标签, 其余 5 部回退泛型 codebook 推断 →
        # Stata 标签层不对称)。仅补 6 个 headline 列/部 (与 loughran 同口径);
        # sum/std/vw/mw/hw/tech/app/idf 衍生列对全部 6 部一律走泛型推断 (loughran 亦然), 保持对称。
        'jiang_2021_tone_full':             "Avg Tone Jiang et al. 2021 CN-fin dict (full-track)",
        'jiang_2021_tone_ctx':              "Avg Tone Jiang et al. 2021 CN-fin dict (ctx-track)",
        'jiang_2021_tone_ss':               "Avg Tone Jiang et al. 2021 (bank+fintech same-sentence track)",
        'jiang_2021_negonly_tone_full':     "Avg Tone Jiang et al. 2021 (negonly, rule-reduced) full-track",
        'jiang_2021_negonly_tone_ctx':      "Avg Tone Jiang et al. 2021 (negonly, rule-reduced) ctx-track",
        'jiang_2021_negonly_tone_ss':       "Avg Tone Jiang et al. 2021 (negonly) same-sentence track",
        'yao_2021_tone_full':               "Avg Tone Yao et al. 2021 CN-fin dict (full-track)",
        'yao_2021_tone_ctx':                "Avg Tone Yao et al. 2021 CN-fin dict (ctx-track)",
        'yao_2021_tone_ss':                 "Avg Tone Yao et al. 2021 (bank+fintech same-sentence track)",
        'yao_2021_negonly_tone_full':       "Avg Tone Yao et al. 2021 (negonly, rule-reduced) full-track",
        'yao_2021_negonly_tone_ctx':        "Avg Tone Yao et al. 2021 (negonly, rule-reduced) ctx-track",
        'yao_2021_negonly_tone_ss':         "Avg Tone Yao et al. 2021 (negonly) same-sentence track",
        'bian_2021_tone_full':              "Avg Tone Bian et al. 2021 LM-CN-extended (full-track)",
        'bian_2021_tone_ctx':               "Avg Tone Bian et al. 2021 LM-CN-extended (ctx-track)",
        'bian_2021_tone_ss':                "Avg Tone Bian et al. 2021 (bank+fintech same-sentence track)",
        'bian_2021_negonly_tone_full':      "Avg Tone Bian et al. 2021 (negonly, rule-reduced) full-track",
        'bian_2021_negonly_tone_ctx':       "Avg Tone Bian et al. 2021 (negonly, rule-reduced) ctx-track",
        'bian_2021_negonly_tone_ss':        "Avg Tone Bian et al. 2021 (negonly) same-sentence track",
        'du_2022_tone_full':                "Avg Tone Du et al. 2022 (+political-pos) (full-track)",
        'du_2022_tone_ctx':                 "Avg Tone Du et al. 2022 (+political-pos) (ctx-track)",
        'du_2022_tone_ss':                  "Avg Tone Du et al. 2022 (bank+fintech same-sentence track)",
        'du_2022_negonly_tone_full':        "Avg Tone Du et al. 2022 (negonly, rule-reduced) full-track",
        'du_2022_negonly_tone_ctx':         "Avg Tone Du et al. 2022 (negonly, rule-reduced) ctx-track",
        'du_2022_negonly_tone_ss':          "Avg Tone Du et al. 2022 (negonly) same-sentence track",
        'you_2018_tone_full':               "Avg Tone You et al. 2018 CN-fin dict (full-track)",
        'you_2018_tone_ctx':                "Avg Tone You et al. 2018 CN-fin dict (ctx-track)",
        'you_2018_tone_ss':                 "Avg Tone You et al. 2018 (bank+fintech same-sentence track)",
        'you_2018_negonly_tone_full':       "Avg Tone You et al. 2018 (negonly, rule-reduced) full-track",
        'you_2018_negonly_tone_ctx':        "Avg Tone You et al. 2018 (negonly, rule-reduced) ctx-track",
        'you_2018_negonly_tone_ss':         "Avg Tone You et al. 2018 (negonly) same-sentence track",
        'mean_frac_definite_full':          "Mean Frac Definite from indep Full scan (You 2018 Panel C 388 words)",
        'mean_frac_definite_ctx':           "Mean Frac Definite from indep Ctx scan (You 2018 Panel C 388 words)",
        'frac_amb_articles_full':           "Frac Articles Ambiguous Full (>=D0 median, You 2018 Panel D)",
        'frac_amb_articles_ctx':            "Frac Articles Ambiguous Ctx (>=D0 median, You 2018 Panel D)",
        # v3.5.1 A3 Numerical Intensity (数值披露强度; 引文勘误见 codebook reference) 三轨 (full/ctx/ss)
        'mean_num_intensity_full':          "Mean Numerical Intensity Full (three-track)",
        'mean_num_intensity_ctx':           "Mean Numerical Intensity Ctx (three-track)",
        # nonpolarity-dims (2026-06-20): Named-Entity Density (Hope-Hu-Lu 2016 RAS; specificity 实体面)
        'avg_named_entity_full':            "Named-Entity Density Full (specificity 实体子集; Hope 2016)",
        'avg_named_entity_ctx':             "Named-Entity Density Ctx (specificity 实体子集; Hope 2016)",
        'avg_named_entity_ss':              "Named-Entity Density same-sentence (specificity 实体子集; Hope 2016)",
        # nonpolarity-dims WS-B2 (2026-06-20): Boilerplate Phrase Ratio 单轨 (Lang-Stice-Lawrence 2015 JAE)
        'avg_boilerplate_full':             "Boilerplate Phrase Ratio Full (跨文档套话; LSL 2015)",
        # remove-title-track: title-indicator labels 已移除
        # ─────────────────────────────────────────────────────────────
        # v3.14.0 (2026-06-27, all-API-embedding): 嵌入主轨改为 gemini(MAIN, 无后缀)
        # ⟂ text-embedding-3-large(_lg) 跨厂商对等 CO-PRIMARY 双轨 (本地 text2vec/_t2v
        # 与 _bge 整体移除)。这批 MAIN (无后缀) anchor 嵌入族标签是 _lg 派生循环 (下方
        # _MAIN_ANCHOR_KEYS) 与 _allv 派生循环的输入源 —— 删 _t2v 后必须存在, 否则两循环
        # 输入归零、_lg/_allv 标签全失。每条 base 文案恰带一个 "(co-primary:
        # gemini-embedding-2-preview)" 对称标注 (_lg 派生时整体 replace 为
        # text-embedding-3-large; 严禁 "robust/robustness check" 措辞 —— 二者对等互证)。
        # full 轨命名遵循 producer 列约定: n5_emb/sim_max_emb/centroid_diff_emb 的 full
        # 为裸名 (无 _full 后缀), 其余族 full 带 _full。≤80 UTF-8 bytes。
        # ─────────────────────────────────────────────────────────────
        'strat_diff_full':                  "Strat Diff (full) (co-primary: gemini-embedding-2-preview)",
        'strat_diff_ctx':                   "Strat Diff (ctx) (co-primary: gemini-embedding-2-preview)",
        'strat_diff_n5_emb':                "Strat Diff N5 Emb (full) (co-primary: gemini-embedding-2-preview)",
        'strat_diff_n5_emb_ctx':            "Strat Diff N5 Emb (ctx) (co-primary: gemini-embedding-2-preview)",
        'strat_sim_max_emb':                "Strat Max Sim Emb (full) (co-primary: gemini-embedding-2-preview)",
        'strat_sim_max_emb_ctx':            "Strat Max Sim Emb (ctx) (co-primary: gemini-embedding-2-preview)",
        'centroid_diff_emb':                "Centroid Diff Emb (full) (co-primary: gemini-embedding-2-preview)",
        'centroid_diff_emb_ctx':            "Centroid Diff Emb (ctx) (co-primary: gemini-embedding-2-preview)",
        'coh_emb_full':                     "Temporal Coherence Emb (full) (co-primary: gemini-embedding-2-preview)",
        'coh_emb_ctx':                      "Temporal Coherence Emb (ctx) (co-primary: gemini-embedding-2-preview)",
        'policy_cosine_sim_full':           "Policy Cosine Sim (full) (co-primary: gemini-embedding-2-preview)",
        'policy_cosine_sim_ctx':            "Policy Cosine Sim (ctx) (co-primary: gemini-embedding-2-preview)",
        'auth_sim_emb_full':                "Auth Policy Sim Emb (full) (co-primary: gemini-embedding-2-preview)",
        'auth_sim_emb_ctx':                 "Auth Policy Sim Emb (ctx) (co-primary: gemini-embedding-2-preview)",
        'benefit_mean_full':                "Benefit Attitude Mean (full) (co-primary: gemini-embedding-2-preview)",
        'benefit_mean_ctx':                 "Benefit Attitude Mean (ctx) (co-primary: gemini-embedding-2-preview)",
        'benefit_std_full':                 "Benefit Attitude SD (full) (co-primary: gemini-embedding-2-preview)",
        'benefit_std_ctx':                  "Benefit Attitude SD (ctx) (co-primary: gemini-embedding-2-preview)",
        'benefit_pos_frac_full':            "Benefit Pos Frac (full) (co-primary: gemini-embedding-2-preview)",
        'benefit_pos_frac_ctx':             "Benefit Pos Frac (ctx) (co-primary: gemini-embedding-2-preview)",
        'benefit_neg_frac_full':            "Benefit Neg Frac (full) (co-primary: gemini-embedding-2-preview)",
        'benefit_neg_frac_ctx':             "Benefit Neg Frac (ctx) (co-primary: gemini-embedding-2-preview)",
        'emb_peer_tone_lag1_full':          "Emb Peer Tone Lag1 (full) (co-primary: gemini-embedding-2-preview)",
        'bank_emb_sim_mean_lag1':           "Bank Emb Sim Mean (L1) (co-primary: gemini-embedding-2-preview)",
        'industry_neg_shock_lag1':          "Industry Neg Shock LOO (L1, year-FE-safe)",
        # 网络指标扩展 2026-06-21 (WS-A net 级 6 / WS-C GF 5 / WS-B 二分图 5);
        # .dta 标签经此 HEURISTIC_LABELS (build_variable_labels 优先级 2) 命中,
        # export.py STATA_LABELS 不入 stage-46 .dta 路径 (MISSING_SCHEMA-1)。各 ≤80 字节。
        'net_modularity_yr':                "Annual Co-mention Modularity (CNM 2004; year-FE absorbed)",
        'net_assortativity_yr':             "Annual Degree Assortativity (Newman 2002; year-FE absorbed)",
        'net_transitivity_yr':              "Annual Global Transitivity (Watts-Strogatz 1998)",
        'net_diameter_yr':                  "Annual Co-mention Diameter (LCC, unweighted)",
        'net_giant_share_yr':               "Annual Giant Component Share",
        'net_n_components_yr':              "Annual Number of Connected Components",
        'gf_coordinator':                   "GF Coordinator Brokerage (Gould-Fernandez 1989)",
        'gf_itinerant':                     "GF Itinerant Brokerage (Gould-Fernandez 1989)",
        'gf_gatekeeper_rep':                "GF Gatekeeper-Representative (undirected merge, 1989)",
        'gf_liaison':                       "GF Liaison Brokerage (Gould-Fernandez 1989)",
        'gf_total':                         "GF Total Brokerage (Gould-Fernandez 1989)",
        'brok_bip_degree_cent':             "Bipartite Media-Bank Degree (Borgatti-Everett 1997)",
        'brok_bip_between_cent':            "Bipartite Media-Bank Betweenness Brokerage (Freeman 1979)",
        'brok_bip_closeness_cent':          "Bipartite Media-Bank Closeness (LCC-restricted)",
        'brok_bip_clustering_ra':           "Bipartite Clustering Robins-Alexander (2004)",
        'brok_bip_node_redundancy':         "Bipartite Node Redundancy (Latapy et al. 2008)",
        # IV 扩展族 LOO 同业工具 (2026-06-13): full 轨 leave_one_out_peer_* +
        # ctx 轨镜像 lpeer_*_ctx (实体窗口归因, Hassan 2019 QJE). 各 ≤ 80 字节.
        'leave_one_out_peer_attention_iv':  "Same-type peer LOO attention IV (full; Manski 1993 caveat)",
        'leave_one_out_peer_subst_iv':      "Same-type peer LOO substantive-share IV (full)",
        'leave_one_out_peer_locus_iv':      "Same-type peer LOO tech-locus IV (full)",
        'leave_one_out_peer_collab_iv':     "Same-type peer LOO collaboration-share IV (full)",
        'leave_one_out_peer_benefit_iv':    "Same-type peer LOO benefit-attitude IV (full)",
        'zone_leave1out_benefit_iv':        "Same-zone (cross-prov) LOO benefit-attitude IV (full)",
        'zone_leave1out_benefit_iv_ctx':    "Same-zone (cross-prov) LOO benefit-attitude IV (ctx)",
        'lpeer_attention_iv_ctx':           "Same-type peer LOO attention IV (ctx/entity-window)",
        'lpeer_subst_iv_ctx':               "Same-type peer LOO substantive-share IV (ctx)",
        'lpeer_locus_iv_ctx':               "Same-type peer LOO tech-locus IV (ctx)",
        'lpeer_collab_iv_ctx':              "Same-type peer LOO collaboration-share IV (ctx)",
        'lpeer_benefit_iv_ctx':             "Same-type peer LOO benefit-attitude IV (ctx)",
        # ─────────────────────────────────────────────────────────────
        # 三轨 (full/ctx/ss): 第三轨 _ss = 银行+金科同句共现轨 (content_ss; 同句内
        # 同时含 目标银行∧金科词 的句 ±N 句窗, 无共现→回退全文镜像 ctx)。锚点:
        # Gentzkow & Shapiro (2010) ECMA / Dougal et al. (2012) RFS 媒体共提及计量,
        # 与 ctx 的 Hassan (2019) QJE proximity 谱系并列。下列每条 = 其 _ctx 孪生
        # 标签的机械 `_ctx→_ss` 镜像 + 中文后缀 "(银行+金科同句)" (用户可见标签平价);
        # 英文描述压缩为 "SS-track"/"same-sent" 以预留后缀字节 (≤ 80 UTF-8 bytes;
        # build_variable_labels 仍按字节边界兜底截断)。三轨各自 just-identified IV
        # 并排, full×ctx×ss 禁混进同一 over-id Hansen J (镜像 ctx 红线)。
        # ─────────────────────────────────────────────────────────────
        'n_articles_llm_valid_ss':          "News count, SS-track LLM-valid (银行+金科同句; ss category-frac denom)",
        'innovation_locus_ss':              "Innovation Locus (SS-track 银行+金科同句, Gentzkow-Shapiro 2010)",
        'innovation_substantiveness_ss':    "Innov. Substantiveness (SS-track 银行+金科同句, W&Z 1998 ASQ)",
        'innovation_collab_mode_ss':        "Innov. Collab Mode (SS-track 银行+金科同句, Chesbrough 2003)",
        'innovation_collab_mode_confidence_ss': "Collab Mode Confidence (SS-track 银行+金科同句, raw LLM)",
        'category_confidence_ss':           "Locus Confidence (SS-track 银行+金科同句, hybrid LLM+keyword)",
        'tone_gap_tech_app_ls_ss':          "Tone Gap: Tech-App (Loc=SS, ss sentiment 银行+金科同句)",
        'tone_gap_sub_symb_ss_ss':          "Tone Gap: Sub-Symb (Subst=SS, ss sentiment 银行+金科同句)",
        # 二元 prob_score 三维 × ss 轨 (positive_class = 象征性/应用场景/外部协同)
        'avg_subst_prob_score_ss':          "Avg Subst P_BIN (SS-track 银行+金科同句) — 1=symbolic",
        'avg_subst_prob_score_std_ss':      "Std Subst P_BIN (SS-track 银行+金科同句, bank-year SD)",
        'avg_locus_prob_score_ss':          "Avg Locus P_BIN (SS-track 银行+金科同句) — 1=application",
        'avg_locus_prob_score_std_ss':      "Std Locus P_BIN (SS-track 银行+金科同句, bank-year SD)",
        'avg_collab_prob_score_ss':         "Avg Collab P_BIN (SS-track 银行+金科同句) — 1=external/open",
        'avg_collab_prob_score_std_ss':     "Std Collab P_BIN (SS-track 银行+金科同句, bank-year SD)",
        # A1 Lexical Clarity (LM 2011 JF; You 2018) ss 独立扫描
        'mean_clarity_score_ss':            "Mean Clarity Score from indep SS-text scan (银行+金科同句, LM 2011 JF)",
        'mean_frac_definite_ss':            "Mean Frac Definite from indep SS scan (银行+金科同句, You 2018)",
        'frac_amb_articles_ss':             "Frac Articles Ambiguous SS (银行+金科同句, >=D0 median, You 2018)",
        # A3 Numerical Intensity ss 轨
        'mean_num_intensity_ss':            "Mean Numerical Intensity SS (三轨 full/ctx/ss; 银行+金科同句)",
        # MAIN (无后缀) anchor 嵌入族 ss 轨 (gemini-embedding-2-preview; v3.14.0
        # 起 _lg 派生循环 + _allv 循环的 ss-轨输入源, 镜像上方 full/ctx MAIN 块)。
        # 每条恰带一个 "(co-primary: gemini-embedding-2-preview)" 对称标注。
        'strat_diff_ss':                    "Strat Diff (ss) (co-primary: gemini-embedding-2-preview)",
        'strat_diff_n5_emb_ss':             "Strat Diff N5 Emb (ss) (co-primary: gemini-embedding-2-preview)",
        'strat_sim_max_emb_ss':             "Strat Max Sim Emb (ss) (co-primary: gemini-embedding-2-preview)",
        'centroid_diff_emb_ss':             "Centroid Diff Emb (ss) (co-primary: gemini-embedding-2-preview)",
        'coh_emb_ss':                       "Temporal Coherence Emb (ss) (co-primary: gemini-embedding-2-preview)",
        'policy_cosine_sim_ss':             "Policy Cosine Sim (ss) (co-primary: gemini-embedding-2-preview)",
        'auth_sim_emb_ss':                  "Auth Policy Sim Emb (ss) (co-primary: gemini-embedding-2-preview)",
        'benefit_mean_ss':                  "Benefit Attitude Mean (ss) (co-primary: gemini-embedding-2-preview)",
        'benefit_std_ss':                   "Benefit Attitude SD (ss) (co-primary: gemini-embedding-2-preview)",
        'benefit_pos_frac_ss':              "Benefit Pos Frac (ss) (co-primary: gemini-embedding-2-preview)",
        'benefit_neg_frac_ss':              "Benefit Neg Frac (ss) (co-primary: gemini-embedding-2-preview)",
        # IV 扩展族 ss 轨镜像 lpeer_*_ss / zone_leave1out_benefit_iv_ss
        # (各自 just-identified 并排, 禁与 full/ctx 混 over-id Hansen J)
        'zone_leave1out_benefit_iv_ss':     "Same-zone (cross-prov) LOO benefit-attitude IV (ss 银行+金科同句)",
        'lpeer_attention_iv_ss':            "Same-type peer LOO attention IV (ss 银行+金科同句, same-sent window)",
        'lpeer_subst_iv_ss':                "Same-type peer LOO substantive-share IV (ss 银行+金科同句)",
        'lpeer_locus_iv_ss':                "Same-type peer LOO tech-locus IV (ss 银行+金科同句)",
        'lpeer_collab_iv_ss':               "Same-type peer LOO collaboration-share IV (ss 银行+金科同句)",
        'lpeer_benefit_iv_ss':              "Same-type peer LOO benefit-attitude IV (ss 银行+金科同句)",
    }

    # ═══ co-primary ② "_lg" 标签机械派生 (text-embedding-3-large; v3.14.0 起 ACTIVE) ═══
    # v3.14.0 (2026-06-27, all-API-embedding): 本地 text2vec(_t2v)/bge(_bge) 整体移除,
    # 嵌入主轨改为 gemini(MAIN, 无后缀) ⟂ text-embedding-3-large(_lg) 跨厂商对等 CO-PRIMARY
    # 双轨。删 _t2v 字面键后, 旧"从 _t2v 派生 _lg"机制输入归零 → 改从上方手写的 MAIN (无后缀)
    # anchor 嵌入族键集 _MAIN_ANCHOR_KEYS 派生 _lg 孪生标签 (对等命名机制, 后缀无主次含义)。
    #   · _lg KEY: 在 track 后缀 (_full/_ctx/_ss) 之前插 `_lg`; 无 track 后缀的裸名 (如
    #     strat_diff_n5_emb / bank_emb_sim_mean_lag1) 则 append `_lg` —— 与 producer 列名
    #     (strat_diff_n5_emb_lg / bank_emb_sim_mean_lag1_lg) 1:1 对齐。
    #   · _lg LABEL: 把 MAIN base 文案里的 "(co-primary: gemini-embedding-2-preview)"
    #     整体 REPLACE 为 "(co-primary: text-embedding-3-large)" (replacive 非 append →
    #     MAIN 与 _lg 各带恰一个对称 co-primary 标注; 严禁 "robust/robustness check" 措辞)。
    # 位置在 MAIN 字面 dict 之后、_allv 派生循环之前 → 下方 _allv 循环可自动为 MAIN+_lg
    # 两套键补 _allv (anchor-dependent 政策族, 如 policy_cosine_sim)。
    _MAIN_ANCHOR_KEYS = frozenset({
        # full/ctx (full 命名遵循 producer: n5_emb/sim_max_emb/centroid_diff_emb 裸名)
        'strat_diff_full', 'strat_diff_ctx',
        'strat_diff_n5_emb', 'strat_diff_n5_emb_ctx',
        'strat_sim_max_emb', 'strat_sim_max_emb_ctx',
        'centroid_diff_emb', 'centroid_diff_emb_ctx',
        'coh_emb_full', 'coh_emb_ctx',
        'policy_cosine_sim_full', 'policy_cosine_sim_ctx',
        'auth_sim_emb_full', 'auth_sim_emb_ctx',
        'benefit_mean_full', 'benefit_mean_ctx',
        'benefit_std_full', 'benefit_std_ctx',
        'benefit_pos_frac_full', 'benefit_pos_frac_ctx',
        'benefit_neg_frac_full', 'benefit_neg_frac_ctx',
        'emb_peer_tone_lag1_full',
        'bank_emb_sim_mean_lag1',
        # ss 轨 (银行+金科同句)
        'strat_diff_ss',
        'strat_diff_n5_emb_ss', 'strat_sim_max_emb_ss', 'centroid_diff_emb_ss',
        'coh_emb_ss', 'policy_cosine_sim_ss', 'auth_sim_emb_ss',
        'benefit_mean_ss', 'benefit_std_ss', 'benefit_pos_frac_ss', 'benefit_neg_frac_ss',
    })
    _GEMINI_ANNOT = '(co-primary: gemini-embedding-2-preview)'
    _LARGE_ANNOT = '(co-primary: text-embedding-3-large)'
    # P2-D 防御 (code-review): 每个 _MAIN_ANCHOR_KEYS 须存在于 HEURISTIC_LABELS 且含 gemini
    # 标注, 否则下方 replacive 派生会 0-迭代 / 产未替换标签 → 整族 _lg 标签静默丢失。手写键
    # typo 时立即 fail-loud (而非到生产才发现 .dta 缺标签)。
    _missing_annot = [k for k in _MAIN_ANCHOR_KEYS if _GEMINI_ANNOT not in HEURISTIC_LABELS.get(k, '')]
    assert not _missing_annot, (
        f"_MAIN_ANCHOR_KEYS 中 {_missing_annot} 缺失或无 '{_GEMINI_ANNOT}' 标注 → _lg 派生会漏整族; "
        f"检查 _MAIN_ANCHOR_KEYS 与手写 HEURISTIC_LABELS 是否 1:1"
    )
    for _k, _v in [(k, v) for k, v in HEURISTIC_LABELS.items() if k in _MAIN_ANCHOR_KEYS]:
        # _lg KEY: 在 track 后缀前插 `_lg` (裸名则 append)
        if _k.endswith(('_full', '_ctx', '_ss')):
            _base, _trk = _k.rsplit('_', 1)
            _lg_key = f'{_base}_lg_{_trk}'
        else:
            _lg_key = f'{_k}_lg'
        if _lg_key not in HEURISTIC_LABELS:
            _lg_label = _v.replace(_GEMINI_ANNOT, _LARGE_ANNOT)
            HEURISTIC_LABELS[_lg_key] = _lg_label[:80]

    # ═══ 全年份锚点 "_allv" 标签机械派生 (all-vintage anchor robustness, 2026-06-21) ═══
    # 与 export.py STATA_LABELS 的 _allv 派生同逻辑 (codebook + .dta 标签兜底共用此源)。
    # 仅对 anchor-dependent 政策族 (6 前缀: article_sim_ / auth_sim_ / token_adopt_ /
    # hidden_adopt_ / subst_adopt_ / policy_cosine_sim) 派生; _allv 插在 track 后缀
    # (_full/_ctx/_ss) 之前 (无 track 则 append), 标签 = 主轨标签 + " (All-Vintage anchor)"
    # (≤80 字节, codebook UTF-8 友好)。
    _ALLV_PREFIXES = ('article_sim_', 'auth_sim_', 'token_adopt_',
                      'hidden_adopt_', 'subst_adopt_', 'policy_cosine_sim')
    for _k, _v in [(k, v) for k, v in HEURISTIC_LABELS.items()
                   if k.startswith(_ALLV_PREFIXES) and '_allv' not in k]:
        if _k.endswith(('_full', '_ctx', '_ss')):
            _base, _trk = _k.rsplit('_', 1)
            _allv_key = f'{_base}_allv_{_trk}'
        else:
            _allv_key = f'{_k}_allv'
        if _allv_key not in HEURISTIC_LABELS:
            HEURISTIC_LABELS[_allv_key] = f'{_v} (All-Vintage anchor)'[:80]

    # ═══ 规则消融梯度 "{d}_{suffix}_tone{track}" 标签机械生成 (rule-ablation ladder, v3.11.1) ═══
    # 6 新变体 (negonly 已上方手写, 此处不重复) × 7 键 (6 词典 + dict_avg 跨词典均值) × 3 轨 = 126 标签。变体语义 / 计数口径
    # 不入梯度的理由见 tone_words._RULE_ABLATION_VARIANTS。标签 ≤80 字节 ASCII (最长 ~53 字符);
    # 列名最长 jiang_2021_degonly_tone_full=28 ≤32 → 不被 shorten 改名, 按 orig 命中。
    _ABL_DICT_REF = {
        'loughran': 'L-M 2011 JF Chinese', 'jiang_2021': 'Jiang et al. 2021',
        'yao_2021': 'Yao et al. 2021', 'bian_2021': 'Bian et al. 2021',
        'du_2022': 'Du et al. 2022', 'you_2018': 'You et al. 2018',
        'dict_avg': 'across 6 dicts',  # 跨词典均值 dict_avg_{sfx}_tone (geography.py, v3.11.1)
    }
    _ABL_VARIANT_DESC = {
        'raw': 'raw no-rule baseline', 'degonly': 'degree-only',
        'advonly': 'adversative-only', 'negdeg': 'neg+degree',
        'negadv': 'neg+adversative', 'degadv': 'degree+adversative',
    }
    for _abl_d, _abl_ref in _ABL_DICT_REF.items():
        for _abl_sfx, _abl_desc in _ABL_VARIANT_DESC.items():
            for _abl_trk in ('full', 'ctx', 'ss'):
                _abl_key = f'{_abl_d}_{_abl_sfx}_tone_{_abl_trk}'
                if _abl_key not in HEURISTIC_LABELS:
                    HEURISTIC_LABELS[_abl_key] = (
                        f'Avg Tone {_abl_ref} ({_abl_desc}, {_abl_trk})')[:80]

    for col in df.columns:
        # fix(omni-g-stata-export-05/09, 2026-06-11): 改名列先按原名查
        # (meta/HEURISTIC 以原始 panel 名为键), 短名兜底, fallback 用原名
        orig = rename_map.get(col, col)
        if orig in meta and hasattr(meta[orig], 'label') and meta[orig].label:
            label = meta[orig].label
        elif orig in HEURISTIC_LABELS:
            label = HEURISTIC_LABELS[orig]
        elif col != orig and col in meta and hasattr(meta[col], 'label') and meta[col].label:
            label = meta[col].label
        elif col != orig and col in HEURISTIC_LABELS:
            label = HEURISTIC_LABELS[col]
        else:
            # fallback: 原始列名 (改名列保留判别后缀; 中文 column 名直接用)
            label = orig

        # fix(omni-g-stata-export-02/08, 2026-06-11): 按 UTF-8 字节边界截断 —
        # 与 validate_stata_compat 的字节口径一致。原实现 label[:77]+'...'
        # 按字符切片, 对 CJK 标签 (3 字节/字符) 字节数可不减反增 (81→84 字节
        # 『越截越长』), 必触发下游 validate raise → stage 46 硬崩。
        if len(label.encode('utf-8')) > STATA_VAR_LABEL_MAXLEN:
            truncated = label.encode('utf-8')[:STATA_VAR_LABEL_MAXLEN - 3]
            # errors='ignore' 丢弃截断点处不完整的多字节序列 → 合法 UTF-8 边界
            label = truncated.decode('utf-8', errors='ignore') + '...'

        labels[col] = label
    return labels


def _assert_track_triplet_unique(orig_cols: List[str], new_cols: List[str]) -> None:
    """三轨 (full/ctx/ss) 写前唯一性断言: 同一 base 的轨家族 sanitize 后不撞名.

    plan §0/§7.1/M1 前瞻护栏。机制: 把每个轨后缀列 (``*_full``/``*_ctx``/``*_ss``)
    按 track-stripped base 分组, 断言组内不同原始轨 (full/ctx/ss) 的最终 Stata
    短名两两互异。sanitizer 用 md5 后缀而非裸截断, 全局短名集本就无碰撞 → 正常
    路径恒通过; 此断言仅在未来引入裸截断/手工缩写规则误把其中两条轨坍缩到同名时
    fail-loud (而非静默列身份交换)。

    白话: full/ctx/ss 三条轨道的同一个指标 (比如 llm_vote_tone_*), 缩短列名后
    必须仍是三个不同的名字; 万一哪天改了缩写规则把其中两条挤成同一个名字,
    这里直接报错, 不让这两条轨的数据悄悄串味。
    """
    _TRACK_SUFFIXES = ('_full', '_ctx', '_ss')
    # base → {track: 最终短名}
    family: Dict[str, Dict[str, str]] = {}
    for orig, new in zip(orig_cols, new_cols):
        for suf in _TRACK_SUFFIXES:
            if orig.endswith(suf):
                base = orig[: -len(suf)]
                family.setdefault(base, {})[suf] = new
                break
    collisions: List[str] = []
    for base, track_map in family.items():
        if len(track_map) < 2:
            continue  # 单轨 base 无三元组撞名风险
        # 反查: 同一最终短名是否被 ≥2 个不同轨占用
        short2tracks: Dict[str, List[str]] = {}
        for suf, short in track_map.items():
            short2tracks.setdefault(short, []).append(suf)
        for short, tracks in short2tracks.items():
            if len(tracks) > 1:
                collisions.append(f"base '{base}' 的 {tracks} 轨 sanitize 后同名 '{short}'")
    if collisions:
        raise ValueError(
            "shorten_long_column_names: 三轨 (full/ctx/ss) 唯一性断言失败 "
            f"({len(collisions)} 处轨家族坍缩) — 列身份会静默交换:\n  - "
            + "\n  - ".join(collisions[:10])
        )


def shorten_long_column_names(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """v3.2.0 M3/7: 自动缩短超 32 字符列名 (Stata 硬限).

    缩写规则:
        1. 常见模式替换 (idf_score → idfsc, leave1out → l1o, 等)
        2. 若仍 > 32, 截断到 32 字符
        3. 截断后冲突 → 6-char md5 hash 后缀 (跨 run 确定性)
        4. 返回 (df_renamed, mapping) 让 codebook 记录原名

    fix(omni-g-stata-export-12, 2026-06-11): used 集合预载全部原列名 (镜像
    asciify_non_ascii_columns 的预载) — 此前 used 从空集累加, 截短名可抢占 df
    中靠后的真实同名列, 造成 core 选列时的列身份静默交换 (值级错配)。
    fix(omni-g-stata-export-09, 2026-06-11): 两遍式前瞻碰撞检测 — 多个长列截断
    后 32-char 前缀相同时 (如 innovation_collab_mode_confidence_full/_ctx),
    全部 (含先到的第一列) 加 md5 后缀; 此前首列独占裸截断名, 彻底丢失
    _full/_ctx 判别轨后缀 (P-063 修复只救了碰撞的第二列)。

    三轨 (full/ctx/ss): _ss(3) 短于 _ctx(4) → 任何 ctx 能塞进 32 字符的列, ss
    一定也能, **无需新增缩写规则** (实测活面板 1658 列零 _ss 超 32、零三元组截断
    撞名)。但保留**写前三元组唯一性断言** (见函数末 _assert_track_triplet_unique)
    作前瞻护栏: 同一 base 的 {full, ctx, ss} 三轨 sanitize 后绝不可坍缩到同名
    (sanitizer 用 md5 后缀非裸截断, 全局已无碰撞, 此断言专项核验轨家族层)。

    Returns:
        (renamed_df, {short_name: original_name}) — codebook 可反查
    """
    abbreviations = [
        ('_idf_score_', '_idfsc_'),
        ('_leave1out_', '_l1o_'),
        # fix(iv-final-audit CONS-6, 2026-06-13): IV 扩展族 full 轨 _lag1 缩写。
        # leave_one_out_peer_{attention,collab,benefit}_iv_lag1 = 36/33/34 字符
        # (>32), 旧裸截断丢失 lag1 判别符 (..._iv_ / ..._iv_la)。此规则仅命中
        # 这 3 个溢出 _lag1 列 (base 名 ≤31 不进 shorten 循环, 故 19_attention
        # 等模板对 base 名的 live confirm 引用零影响), 缩为
        # l1o_peer_attention_iv_lag1(26) 等, 完整保留 lag1 语义; rename_map 回传
        # 原名供 HEURISTIC_LABELS / export.py 标签反查, codebook 记原名。
        ('leave_one_out_peer_', 'l1o_peer_'),
        ('_dict_avg_tone_', '_davg_t_'),
        ('_bert_avg_pos_', '_bavg_p_'),
        # fix(omni-g-stata-export, 2026-06-11) 模板组约定: 36-char 事件研究列
        # car_3day_window_fintech_announcement → car_3day_window_ft_announce
        # (27 字符; 三轨 (full/ctx/ss) 后缀 _full/_ctx/_ss 仍 ≤ 32, 免触发裸截断歧义)
        ('_fintech_announcement', '_ft_announce'),
    ]
    # P-063 修复 (v3.7.1): 旧 dedup 用 _1/_2 numeric suffix 截断 base
    # (`base[:MAX-2] + '_1'`), 把 32-char 区间内的关键 suffix (_full/_ctx/
    # _t0/_t1) 吃掉, 破坏 track 语义. 改用 6-char md5 hash suffix 保留尽量
    # 多的 discriminating chars + 跨 run 确定性 (同 col 总产同 hash).
    import hashlib as _hashlib  # 局部 import 避免 module-level 污染
    from collections import Counter as _Counter

    # Pass 1: 计算每列暂定短名 (缩写 → 截断), 不做去重
    tentative: List[str] = []
    for col in df.columns:
        new_col = col
        if len(new_col) > STATA_VAR_NAME_MAXLEN:
            for old, new in abbreviations:
                if old in new_col:
                    new_col = new_col.replace(old, new)
                    if len(new_col) <= STATA_VAR_NAME_MAXLEN:
                        break
        # 仍超 → 截断
        if len(new_col) > STATA_VAR_NAME_MAXLEN:
            new_col = new_col[:STATA_VAR_NAME_MAXLEN]
        tentative.append(new_col)

    # Pass 2: 碰撞消解 — used 预载全部原列名 + 暂定名计数前瞻
    tentative_counts = _Counter(tentative)
    used: set = set(df.columns)  # omni-12: 不得抢占任何既有真实列名
    rename_map: Dict[str, str] = {}  # short → original
    new_cols: List[str] = []
    for col, new_col in zip(df.columns, tentative):
        if new_col != col:
            collides = (
                tentative_counts[new_col] > 1   # omni-09: 与其他列暂定短名相撞 (含首列)
                or new_col in used              # omni-12: 与既有列名 / 已分配短名相撞
            )
            if collides:
                base = new_col[:STATA_VAR_NAME_MAXLEN - 7]
                h = _hashlib.md5(col.encode('utf-8')).hexdigest()[:6]
                new_col = f"{base}_{h}"
                if new_col in used:  # md5 仍撞 (理论上几乎不可能) → fail loud
                    raise ValueError(
                        f"shorten_long_column_names: md5 去重后仍冲突 '{new_col}' "
                        f"(原列 '{col}') — 请人工指定缩写映射."
                    )
        used.add(new_col)
        new_cols.append(new_col)
        if new_col != col:
            rename_map[new_col] = col

    # plan §0/§7.1/M1: 三轨 (full/ctx/ss) 写前唯一性断言 — 同一 base 的轨家族
    # sanitize 后绝不可坍缩到同名 (前瞻护栏; _ss 短于 _ctx, 正常路径恒通过)
    _assert_track_triplet_unique(list(df.columns), new_cols)

    df_renamed = df.copy()
    df_renamed.columns = new_cols
    return df_renamed, rename_map


# 中文情感标签 → ASCII 确定性映射 (与既有 fin_sent_zh_pos/neg 命名约定一致)
_CN_LABEL_ASCII = {
    '正面': 'pos', '负面': 'neg', '中性': 'neu',
    '积极': 'pos', '消极': 'neg', '中立': 'neu',
}


def asciify_non_ascii_columns(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """H3 (audit-fixes 2026-05-29): 把含非 ASCII 字符的列名转写为合法 Stata 变量名.

    Stata 变量名即使在 Unicode 版 (14+/19) 也必须匹配
    ``^[A-Za-z_][A-Za-z0-9_]{0,31}$`` (Unicode 仅允许出现在值/标签, 不允许在
    变量名)。此前 ``shorten_long_column_names`` 仅按长度截断、不处理非 ASCII,
    导致 117 个中文后缀列 (如 ``finbert_cn_正面_w_sum_full``) 以非法名写入
    full/aux .dta, 且 labels.do 的 ``capture label var <中文>`` 静默 no-op 丢标签.

    sentiment-label 段 (正面/负面/中性) 用确定性映射 → pos/neg/neu (不丢信息,
    与既有 ASCII 变体 fin_sent_zh_pos/neg 一致); 残留非 ASCII 字符移除;
    清理重复下划线 + 保证合法首字符 + 截断 32 + md5 后缀去重 (跨 run 确定性).

    Returns:
        (df_renamed, {new_name: original_name}) — 供 codebook 反查.
    """
    import hashlib as _hashlib
    import re as _re

    mapping: Dict[str, str] = {}
    new_cols: List[str] = []
    used = {c for c in df.columns if c.isascii()}
    for col in df.columns:
        if col.isascii():
            new_cols.append(col)
            continue
        new = col
        for cn, asc in _CN_LABEL_ASCII.items():
            new = new.replace(cn, asc)
        # 残留非 ASCII → 移除
        new = ''.join(ch for ch in new if ord(ch) < 128)
        new = _re.sub(r'_+', '_', new).strip('_')
        if not new or not (new[0].isalpha() or new[0] == '_'):
            new = 'v_' + new
        new = new[:STATA_VAR_NAME_MAXLEN]
        if new in used:
            base = new[:STATA_VAR_NAME_MAXLEN - 7]
            h = _hashlib.md5(col.encode('utf-8')).hexdigest()[:6]
            new = f"{base}_{h}"
        used.add(new)
        new_cols.append(new)
        mapping[new] = col
    df_renamed = df.copy()
    df_renamed.columns = new_cols
    return df_renamed, mapping


def validate_stata_compat(df: pd.DataFrame, var_labels: Dict[str, str]) -> None:
    """plan v14 §9.5 验收门: 列名 ≤ 32 字符 + 合法 Stata 标识符 + label ≤ 80 字符."""
    import re as _re
    _ident_re = _re.compile(r'^[A-Za-z_][A-Za-z0-9_]{0,31}$')
    issues: List[str] = []
    for col in df.columns:
        if len(col) > STATA_VAR_NAME_MAXLEN:
            issues.append(f"列名超 32 字符: '{col}' ({len(col)} chars)")
        elif not _ident_re.match(col):
            # H3 (audit-fixes 2026-05-29): 非 ASCII / 非法字符 / 非字母下划线起始
            # 都是 Stata 拒绝的变量名 — 此前仅查长度, 放过了 117 个中文列名。
            issues.append(f"非法 Stata 变量名 (非 ASCII 或含非法字符): '{col}'")
        if col in var_labels:
            label_bytes = len(var_labels[col].encode('utf-8'))
            if label_bytes > STATA_VAR_LABEL_MAXLEN:
                issues.append(f"label 超 80 字节: '{col}' ({label_bytes} bytes)")
    if issues:
        raise ValueError(
            f"Stata 兼容性校验失败 ({len(issues)} 处):\n  - " +
            "\n  - ".join(issues[:10])
        )


def _stata_string_literal(text: str) -> str:
    """fix(omni-g-stata-export-06, 2026-06-11): 生成 Stata 安全字符串字面量.

    Stata 简单双引号串不支持 ``""`` 加倍转义 (``"a""b"`` 解析为两个相邻 token
    → r(198) invalid syntax, 行首 capture 静默吞掉 → 标签丢失且无报错), 嵌入
    引号必须用 compound double quotes ``\\`"..."'``。另: 双引号串 (含 compound)
    内 ``$`` / ``\\``` 触发 Stata macro 展开 → 反斜杠转义 ([U] 18.3.11);
    转义 ``\\``` 同时阻止内嵌 ``\\`"`` 抬高 compound 嵌套层级。
    """
    safe = text.replace('$', r'\$').replace('`', r'\`')
    # 残余 `"'` 闭合序列 (" 紧跟 ') 会提前终结 compound 串 → 插空格消解
    safe = safe.replace('"\'', '" \'')
    return '`"' + safe + '"\''


def write_labels_do_file(
    out_path: str,
    var_labels: Dict[str, str],
    value_labels: Dict[str, Dict[int, str]],
    backend_name: str = '',
) -> None:
    """生成 Stata .do 脚本: variable labels + value labels + apply.

    fix(omni-g-stata-export-06, 2026-06-11): 标签输出改 compound double quotes
    (原 ``""`` 加倍转义非 Stata 合法语法, 含 ``"``/``$`` 的标签被 capture 静默丢弃)。

    Args:
        out_path: 输出 .do 路径
        var_labels: {var_name: english_label}
        value_labels: {var_name: {int_code: label_string}}
        backend_name: fix(omni-g-stata-export-03/15, 2026-06-11) 产物指纹 —
            实际写 .dta 的 backend ('pyreadstat' | 'pandas'), 空串则省略该注释行
    """
    lines: List[str] = [
        '* news_process v3.2.0 — Stata variable/value labels (plan v14 §9.1)',
        '* Generated by news_process.pipeline.panel.stata_export.write_labels_do_file',
    ]
    if backend_name:
        # omni-03/15: backend 指纹 — pandas fallback 产物不含 embedded value labels
        # (须跑本 .do apply), 且 nullable Int 存储宽度与 pyreadstat 不同 (byte vs long)
        lines.append(f'* .dta writer backend: {backend_name}'
                     + (' (fallback; .dta 无 embedded value labels — 须 run 本脚本 apply)'
                        if backend_name == 'pandas' else ''))
    lines.extend([
        '',
        '* Section 1: Variable labels (每列加 ≤ 80 字节英文说明)',
    ])
    for col, label in var_labels.items():
        # Stata `label var` 语法: label var <name> `"<label>"' (compound quotes)
        lines.append(f'capture label var {col} {_stata_string_literal(label)}')

    lines.extend([
        '',
        '* Section 2: Value labels (类别变量 0=baseline / 1=对照, 双语)',
    ])

    # locus_lbl (共享)
    lines.append('capture label drop locus_lbl')
    lines.append(
        f'label define locus_lbl 0 {_stata_string_literal("底层技术 (Technology)")} '
        f'1 {_stata_string_literal("应用场景 (Application)")}'
    )

    # subst_lbl (共享)
    lines.append('capture label drop subst_lbl')
    lines.append(
        f'label define subst_lbl 0 {_stata_string_literal("实质性 (Substantive)")} '
        f'1 {_stata_string_literal("象征性 (Symbolic)")}'
    )

    # v3.4.0: collab_mode_lbl (Chesbrough 2003 + L&S 2006 SMJ; 第三维度)
    lines.append('capture label drop collab_mode_lbl')
    lines.append(
        f'label define collab_mode_lbl 0 {_stata_string_literal("自主研发 (Independent R&D)")} '
        f'1 {_stata_string_literal("外部协同 (External Collab)")}'
    )

    lines.append('')
    lines.append('* Apply value labels to encoded columns')
    # v3.4.0 ordering: collab_mode 必须先于 substantiveness 检测, 避免子串误匹配
    # ('innovation_substantiveness' 与 'innovation_collab_mode' 互不包含, 但保留显式过滤)
    locus_cols = [c for c in value_labels if 'innovation_locus' in c]
    subst_cols = [c for c in value_labels if 'innovation_substantiveness' in c]
    collab_cols = [c for c in value_labels if 'innovation_collab_mode' in c]
    if locus_cols:
        lines.append(f'capture label values {" ".join(locus_cols)} locus_lbl')
    if subst_cols:
        lines.append(f'capture label values {" ".join(subst_cols)} subst_lbl')
    if collab_cols:
        lines.append(f'capture label values {" ".join(collab_cols)} collab_mode_lbl')

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    logger.info(f"  Stata labels .do 已写入: {out_path} ({len(lines)} 行)")


def upcast_unsafe_int8_columns(
    df: pd.DataFrame,
    value_labels: Dict[str, Dict[int, str]] = None,
    force_non_labeled: bool = True,
) -> pd.DataFrame:
    """fix(omni-g-stata-export-01, 2026-06-11): 计数列导出禁止 Int8 (KNOWN-OPEN ⑥).

    Stata byte 类型合法值域为 [-127, 100]; 101..127 是缺失码位
    (`.`=101, .a-.z=102..127)。pyreadstat 直写 int8∈[101,127] 会被 Stata 读成缺失码 (值静默损坏);
    pandas fallback 的 ``_cast_to_stata_types`` 则自动升 int16 — 两后端语义分叉。

    统一策略 (主控裁决 2026-06-11):
        - 非 value-labeled 的 int8/Int8 计数列 (tone_sum / pos_count / neg_count
          等) 一律升 Int16 — 实测 gpt54nano_tone_sum_full max=100 已压满 byte
          上限零余量, 任何增长即触雷 (``force_non_labeled=True``);
        - value-labeled 0/1 编码列保持 byte (构造上安全), 但实际值越出
          [-127, 100] 时仍防御性升型 + warning。

    Args:
        df: 待写出 DataFrame
        value_labels: {var_name: {code: label}} — 键为当前 df 列名
        force_non_labeled: True=非 value-labeled int8 全升 (export 主流程);
            False=仅按值域升 (backend 写出前的最终安全网)

    白话: Stata 最小的整数类型 byte 只能存 -127 到 100, 101 到 127 被 Stata
    征用作缺失码 (`.`=101, `.a`–`.z`=102–127, 共 27 个)。如果一个计数列 (比如某年某银行的篇数) 以 int8
    直写, 值一旦超过 100 就会被 Stata 当成缺失值, 数字无声损坏。所以这里
    把这类列统一升级成 16 位整数再写盘, 宁可多占一点空间也不丢数。
    """
    value_labels = value_labels or {}
    out = df.copy()
    for col in out.columns:
        dtype_name = str(out[col].dtype)
        if dtype_name not in ('int8', 'Int8'):
            continue
        target = 'Int16' if dtype_name == 'Int8' else 'int16'
        if force_non_labeled and col not in value_labels:
            out[col] = out[col].astype(target)
            continue
        s = out[col]
        mx, mn = s.max(skipna=True), s.min(skipna=True)
        if pd.notna(mx) and (mx > 100 or mn < -127):
            logger.warning(
                f"  upcast_unsafe_int8_columns: 列 '{col}' int8 值域 [{mn}, {mx}] "
                f"越出 Stata byte 合法域 [-127, 100] → 防御升型 {target} "
                f"(101..126 直写会被读成 extended missing 码)"
            )
            out[col] = out[col].astype(target)
    return out


def _write_dta_pyreadstat(df, path, value_labels, var_labels):
    """Backend 1 (推荐): pyreadstat 写入 (embedded value labels + 中文 labels).

    fix(omni-g-stata-export-10/13, 2026-06-11): 移除原 docstring 的 extended
    missing 声称 — 本后端不传 missing_user_values, 全部 NaN 落盘为 sysmiss '.'。
    fix(omni-g-stata-export-01, 2026-06-11): 写出前对越出 byte 合法值域的 int8
    列防御升型 (与 pandas _cast_to_stata_types 语义对齐), 防 101..127 损值。
    """
    import pyreadstat
    df = upcast_unsafe_int8_columns(df, value_labels, force_non_labeled=False)
    pyreadstat.write_dta(
        df, path,
        variable_value_labels=value_labels,
        column_labels=[var_labels.get(c, c) for c in df.columns],
    )


def _write_dta_pandas_fallback(df, path, value_labels, var_labels):
    """Backend 2 (fallback): pandas 原生 .to_stata().

    与 pyreadstat 后端的行为差异 (fix(omni-g-stata-export-03, 2026-06-11)
    docstring 与事实对齐):
        - 不嵌入 value labels — pandas≥1.4 ``to_stata(value_labels=)`` 原生支持,
          但本项目刻意不传 (主控裁决 2026-06-11): labels.do 是唯一 apply 路径,
          避免两后端各自半套 value-label 语义; 差异在 _select_dta_backend WARN 明示
        - 无 extended missing (.a/.b/.c) — pyreadstat 路径同样未实现, 两后端
          一致全写 sysmiss '.'
        - nullable Int 存储宽度可能不同 (pandas 写 byte/int 最小宽度;
          pyreadstat 写 nullable Int 升格 long) → .dta 二进制随后端漂移
    但不需要额外安装 pyreadstat, 让用户在 minimal install 下也能跑 stage 46.
    """
    # pandas to_stata 接受 dict-form variable_labels
    df.to_stata(
        path,
        write_index=False,
        variable_labels={k: v for k, v in var_labels.items() if k in df.columns},
        version=118,  # Stata 14+ format (与 pyreadstat write_dta 默认对齐)
    )


def _select_dta_backend():
    """探测可用 .dta 写入 backend; 优先 pyreadstat (功能更全).

    fix(omni-g-stata-export-03/15, 2026-06-11): backend 由 import 探测静默决定,
    产物语义随环境漂移 (embedded value labels 有/无 + 存储宽度 byte vs long) —
    fallback 时 WARN 明示差异, 并由 export 主流程把 backend 名写进 labels.do
    头注释与日志作产物指纹。
    """
    try:
        import pyreadstat  # noqa: F401
        return 'pyreadstat', _write_dta_pyreadstat
    except ImportError:
        logger.warning(
            "  pyreadstat 未装, fallback 到 pandas to_stata — 产物与 pyreadstat 后端"
            "不等价: (1) .dta 不含 embedded value labels, 须手动 run labels.do apply; "
            "(2) nullable Int 存储宽度可能不同 (byte/int vs long), .dta 二进制不可跨"
            "后端复现; (3) extended missing 两后端均不支持. "
            "推荐: pip install pyreadstat>=1.2 锁定单一后端."
        )
        return 'pandas', _write_dta_pandas_fallback


def export_panel_to_stata(
    panel_path: str,
    output_dir: str,
    output_prefix: str = '46_panel_yearly',
) -> Dict[str, str]:
    """主导出函数: 从 panel parquet 产出 .dta + labels.do + codebook.xlsx.

    v3.2.0 M1/7 (此 commit): pyreadstat 改为 OPTIONAL, fallback 到 pandas to_stata.
    解除 plan v14 §9.4 的"硬依赖"约束, 让用户在 minimal install 下也能产 .dta.

    fix(omni-g-stata-export, 2026-06-11) 语义变更披露: ① 非 value-labeled 计数
    Int8 列升 Int16 写出 (byte 缺失码位防损值); ② shorten/asciify 改名后
    value_labels 键全程同步 + rename_map 链式压平, build_variable_labels
    经原名反查 (改名列标签不再静默丢失);
    ③ labels.do 头部带 backend 指纹。

    Args:
        panel_path: 输入 40_panel_yearly.parquet 路径
        output_dir: 输出目录 (data/processed/)
        output_prefix: 文件名前缀 (默认 46_panel_yearly)
    Returns:
        dict 含产出文件路径: {'full_dta', 'labels_do', 'codebook_xlsx', 'backend'}
        (2026-06-12: 移除 core/aux 双切分 — 本机 StataNow/MP 19.5 直读全列 full.dta;
         2026-06-21: codebook 取消 is_core 核心/辅助列区分, 全列均为分析列)
    """
    import time as _time
    backend_name, write_dta = _select_dta_backend()

    logger.info("=== Stage 46 Stata Export (plan v14 §9.1) ===")
    logger.info(f"  Backend: {backend_name}")
    logger.info(f"  输入: {panel_path}")
    logger.info(f"  输出目录: {output_dir} | 产物前缀: {output_prefix}")

    if not os.path.exists(panel_path):
        raise FileNotFoundError(f"panel parquet 不存在: {panel_path}")

    # ⏱ per-phase 墙钟计时 (纯日志, golden-safe; 末尾汇总打印)
    _phase: Dict[str, float] = {}

    _t = _time.time()
    df = pd.read_parquet(panel_path)
    _phase['①载入parquet'] = _time.time() - _t
    logger.info(f"  panel 载入: {len(df)} 行 × {len(df.columns)} 列")

    # 1. 类别变量编码 (中文 str → byte 0/1)
    _t = _time.time()
    df_encoded, value_labels = encode_categorical_columns(df)
    _phase['②类别编码'] = _time.time() - _t

    # 1a'. fix(omni-g-stata-export-01, 2026-06-11): 计数列禁 Int8 — 非 value-labeled
    # int8/Int8 列升 Int16 (Stata byte 上限 100 零余量; 101..127 是缺失码位,
    # pyreadstat 直写损值 / pandas 静默升型 → 两后端在此统一)
    _t = _time.time()
    df_encoded = upcast_unsafe_int8_columns(df_encoded, value_labels)
    _phase['③int8升型'] = _time.time() - _t

    # 1b. v3.2.0 M3/7: 自动缩短超 32 字符列名 (Stata 硬限) + 记录 mapping
    _t = _time.time()
    df_encoded, rename_map = shorten_long_column_names(df_encoded)
    if rename_map:
        logger.info(f"  Renamed {len(rename_map)} long columns (>32 chars) to Stata-compatible names")
        for short, orig in list(rename_map.items())[:3]:
            logger.info(f"    {orig} → {short}")
        if len(rename_map) > 3:
            logger.info(f"    ... +{len(rename_map) - 3} more (full mapping in codebook.xlsx)")
        # fix(omni-g-stata-export-05/09, 2026-06-11): shorten 改名后同步 value_labels
        # 键 (此前仅 asciify 后同步 → 未来 >32 字符 value-labeled 列的 value label
        # 悬空: pyreadstat 引用不存在列 / labels.do apply 被 capture 静默吞掉)
        if value_labels:
            _orig2short = {orig: short for short, orig in rename_map.items()}
            value_labels = {_orig2short.get(k, k): v for k, v in value_labels.items()}

    # 1c. H3 (audit-fixes 2026-05-29): 把残留非 ASCII (中文) 列名转写为合法
    # Stata 变量名 (正面/负面/中性 → pos/neg/neu)。此前缺该步, 117 个中文列名
    # 以非法 Stata 标识符写入 full/aux .dta, labels.do 静默丢标签。
    df_encoded, ascii_map = asciify_non_ascii_columns(df_encoded)
    if ascii_map:
        logger.info(
            f"  Transliterated {len(ascii_map)} non-ASCII (中文) column names "
            f"to Stata-legal ASCII"
        )
        # 同步 value_labels 键 (若被改名的列恰有 value label)
        if value_labels:
            _orig2new = {orig: new for new, orig in ascii_map.items()}
            value_labels = {_orig2new.get(k, k): v for k, v in value_labels.items()}
        rename_map.update(ascii_map)
        # fix(omni-g-stata-export-05, 2026-06-11): 链式改名压平 — 列被 shorten 又
        # asciify 时 ascii_map 的 value 是中间名, 反查需指回最初 panel 原名
        def _chase_original(name: str) -> str:
            seen = set()
            while name in rename_map and name not in seen:
                seen.add(name)
                name = rename_map[name]
            return name
        rename_map = {k: _chase_original(v) for k, v in rename_map.items()}
    _phase['④列名缩短/转写'] = _time.time() - _t

    # 2. 生成 variable labels (改名列经 rename_map 反查原名命中 codebook/HEURISTIC)
    _t = _time.time()
    var_labels = build_variable_labels(df_encoded, rename_map=rename_map)
    _phase['⑤变量标签构建'] = _time.time() - _t
    _n_labeled = sum(1 for c in df_encoded.columns if var_labels.get(c, c) != c)
    try:
        _label_cov = _n_labeled / max(len(df_encoded.columns), 1)
        logger.info(f"  variable label 覆盖: {_n_labeled:,d}/{len(df_encoded.columns):,d} 列 "
                    f"({pct4(_label_cov)}) 有非列名兜底标签 (越高越好)")
    except Exception:  # noqa: BLE001
        pass

    # 3. Stata 兼容性校验 (plan v14 §9.5; 缩短后应全过)
    _t = _time.time()
    validate_stata_compat(df_encoded, var_labels)
    _phase['⑥兼容性校验'] = _time.time() - _t

    # 4. 写单一全列 .dta (经 backend 抽象, 兼容 pyreadstat / pandas)
    #    2026-06-21: codebook 取消"分析核心列 vs 辅助列"区分 (assign_core_columns /
    #    core_patterns 整体退役); .dta 本就写全列, 与该退役无关。
    full_path = os.path.join(output_dir, f'{output_prefix}_full.dta')
    _t = _time.time()
    write_dta(df_encoded, full_path, value_labels, var_labels)
    _phase['⑦写.dta'] = _time.time() - _t
    logger.info(f"  Full .dta 已写入: {full_path} ({len(df_encoded.columns)} 列; "
                f"单一全列导出不再拆分 core/aux)")

    # 5. labels .do (omni-03/15: 带 backend 指纹)
    labels_path = os.path.join(output_dir, f'{output_prefix}_labels.do')
    _t = _time.time()
    write_labels_do_file(labels_path, var_labels, value_labels, backend_name=backend_name)
    _phase['⑧写labels.do'] = _time.time() - _t

    # 6. codebook .xlsx (依赖 codebook.py)
    codebook_path = os.path.join(output_dir, f'{output_prefix}_codebook.xlsx')
    _t = _time.time()
    try:
        _write_codebook_xlsx(df_encoded, var_labels, value_labels, codebook_path,
                              rename_map=rename_map)
    except Exception as e:
        logger.warning(f"  codebook .xlsx 写入失败 (非阻塞): {e}")
    _phase['⑨写codebook.xlsx'] = _time.time() - _t

    # ⏱ per-phase 墙钟汇总 (纯日志, 数字 sig4 秒; golden-safe)
    try:
        logger.info("  ⏱ 阶段计时 (墙钟, 秒):")
        for _name, _sec in _phase.items():
            logger.info(f"     · {_name}: {sig4(_sec)} s")
        logger.info(f"     · 合计: {sig4(sum(_phase.values()))} s")
    except Exception as _te:  # noqa: BLE001
        logger.warning(f"  计时汇总打印失败 (不影响产物): {_te}")

    return {
        'full_dta': full_path,
        'labels_do': labels_path,
        'codebook_xlsx': codebook_path,
        'backend': backend_name,  # v3.2.0 M1/7: 'pyreadstat' | 'pandas'
    }


def _write_codebook_xlsx(
    df: pd.DataFrame,
    var_labels: Dict[str, str],
    value_labels: Dict[str, Dict[int, str]],
    out_path: str,
    rename_map: Dict[str, str] = None,
) -> None:
    """生成人类可读 codebook .xlsx.

    2026-06-21: 取消 is_core 列 — codebook 不再区分"分析核心列 vs 辅助列",
    所有列均为分析列 (assign_core_columns / core_patterns / STATA_IC_MAX_VARS 已整体退役)。

    Args:
        rename_map: v3.2.0 M3/7 新增: {short_stata_name: original_panel_name}
                    用户可在 codebook 反查 Stata 短名对应的原 panel 列名.
    """
    if rename_map is None:
        rename_map = {}
    rows = []
    for col in df.columns:
        rows.append({
            'var_name': col,
            'original_name': rename_map.get(col, col),  # M3/7: 缩短前原名 (用户反查)
            'label': var_labels.get(col, col),
            'data_type': str(df[col].dtype),
            'value_labels': '; '.join(f'{k}={v}' for k, v in value_labels.get(col, {}).items()),
            'n_non_null': df[col].notna().sum(),
            'n_unique': df[col].nunique() if df[col].dtype.kind != 'f' else None,
        })
    codebook_df = pd.DataFrame(rows)
    codebook_df.to_excel(out_path, index=False, engine='xlsxwriter')
    logger.info(f"  Codebook .xlsx 已写入: {out_path} ({len(rows)} 列条目; "
                f"含 {len(rename_map)} 个 Stata-shortened names 反查映射)")


def _log_export_result_analysis(log, panel_path: str, results: Dict[str, str]) -> None:
    """【结果分析】(黄金范式): 对 stage 46 产出做只读体检并打印判读。

    纯增量日志: 仅读取 panel parquet / 产出 .dta 的元信息, 计算服务于日志的
    局部指标 (行列数 / 主键唯一性 / 三轨主指标齐备性 / 类别 str 列存在性 / round-trip
    行数), 对照阈值/预期方向给好/坏/临界判读。不修改任何返回值或落盘内容; 全程
    try/except 包裹, 分析失败仅 WARNING, 绝不影响已写盘的产物。

    注: fintech_share 不在本阶段输入 40_panel_yearly.parquet 中 (它由下游
    stage 51 controls.py::merge_to_panel 构造), 故本体检不检查它 (避免对错文件
    做误导性诊断, 见 controls.py:789)。
    """
    # crash-guard: 整个【结果分析】块包 try/except — 本块在 export_panel_to_stata 写盘
    # 之后执行 (产物已落地), 但仍兜底防御任何读数/算指标异常 (如 read_stata 后端差异 /
    # 意外 dtype), 失败仅 WARNING, 绝不让纯日志诊断把已交付的 stage 反噬成崩溃。
    try:
        try:
            df = pd.read_parquet(panel_path)
        except Exception as e:  # pragma: no cover - 分析层防御
            log.warning(f"【结果分析】跳过: 无法回读 panel parquet 做体检 ({e})")
            return

        log.info("-" * 72)
        log.info("【结果分析】对交付产物做只读体检 (不改任何数值):")

        n_rows, n_cols = len(df), len(df.columns)
        log.info(f"  · 面板规模: {n_rows} 行 × {n_cols} 列 (bank-year 面板)。")

        # 1) 主键唯一性 (Wooldridge 2010: (target_bank, year) 应唯一)
        if {'target_bank', 'year'}.issubset(df.columns):
            n_dup = int(df.duplicated(subset=['target_bank', 'year']).sum())
            n_banks = int(df['target_bank'].nunique())
            years = sorted(pd.Series(df['year'].dropna().unique()).tolist())
            span = f"{years[0]}–{years[-1]}" if years else "?"
            verdict = "好 (主键唯一)" if n_dup == 0 else f"坏 (有 {n_dup} 个重复 (bank,year) 键)"
            log.info(f"  · 主键唯一性: 重复键数={n_dup} → {verdict}; "
                     f"覆盖 {n_banks} 家银行 × 年份跨度 {span} ({len(years)} 个年度)。")
            if len(years) <= 2:
                log.info("    ⚠ 小样本 (T≤2): 这是开发盘面占位样本, 仅验证管道正确性; "
                         "全量结论以 17M 文 / T=18 (2007–2024) 实测为准。")

        # 2) fintech 情感三轨 (full/ctx/ss) 主指标齐备性 — 缺则下游论文该轨回归空跑
        track_metrics = {
            'full': 'llm_vote_tone_full',
            'ctx':  'llm_vote_tone_ctx',
            'ss':   'llm_vote_tone_ss',
        }
        present, missing = [], []
        for trk, col in track_metrics.items():
            if col in df.columns:
                nn = int(df[col].notna().sum())
                present.append(f"{trk}({col}: 非空 {nn}/{n_rows})")
            else:
                missing.append(f"{trk}({col})")
        if present:
            log.info(f"  · 主语调三轨齐备: {'; '.join(present)} → 好 (论文 P1 主指标可消费)。")
        if missing:
            log.warning(f"  · 主语调三轨缺列 (ss 缓存常未播种, 缺属预期): {', '.join(missing)} "
                        "→ 该轨回归会空跑, 须确认 stage 21 是否产出。")

        # 3) 三轨类别编码 (LOCUS/SUBSTANTIVENESS/COLLAB_MODE) 文章级 str 列在 bank-year 面板的存在性
        #    (原 fintech_share 体检块已删: 该列不在 stage 46 输入 40_panel_yearly.parquet,
        #     由下游 stage 51 controls.py::merge_to_panel 构造, 在此检查恒为死分支且误导, 见 finding f_46)
        cat_str_cols = [c for c in df.columns
                        if c.startswith(('innovation_locus', 'innovation_substantiveness', 'innovation_collab_mode'))
                        and df[c].dtype == object]
        if cat_str_cols:
            log.info(f"  · 类别 str 列: 发现 {len(cat_str_cols)} 个文章级中文类别列 → encoder 会做 str→byte 0/1 编码。")
        else:
            log.info("  · 类别 str 列: 0 个 (bank-year 面板只含派生数值聚合) → 类别 encoder no-op, "
                     "value_labels={} (诚实披露 omni-g-stata-export-14, 符合预期)。")

        # 4) .dta round-trip 行数一致性 (写盘后回读, 须与 parquet 完全相等)
        full_dta = results.get('full_dta')
        backend = results.get('backend', '?')
        if full_dta and os.path.exists(full_dta):
            try:
                dta_df = pd.read_stata(full_dta)
                dta_rows, dta_cols = len(dta_df), len(dta_df.columns)
                row_ok = (dta_rows == n_rows)
                verdict = "好 (无丢行)" if row_ok else f"坏 (.dta {dta_rows} 行 ≠ parquet {n_rows} 行!)"
                log.info(f"  · .dta round-trip (backend={backend}): {dta_rows} 行 × {dta_cols} 列 → {verdict}。")
            except Exception as e:  # pragma: no cover - 回读后端差异防御
                log.info(f"  · .dta round-trip 跳过 (pandas read_stata 无法回读 backend={backend} 产物: {e})。")
        if backend == 'pandas':
            log.warning("  · 后端=pandas (pyreadstat 缺失): .dta 未内嵌 value label, 研究者须手动 run "
                        "46_panel_yearly_labels.do 才有标签; 优雅降级但建议安装 pyreadstat。")

        log.info("-" * 72)
    except Exception as _e:  # pragma: no cover - 纯日志诊断兜底, 绝不影响产物
        log.warning(f"【结果分析】日志诊断计算异常, 跳过(不影响产物): {_e}")


def _log_environment_and_config(log, stage_name: str, panel_path: str, output_dir: str) -> None:
    """【项目/环境/配置/方法论】banner (日志富集, 2026-06-24, golden-safe)。

    把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数、方法学出处"一次性
    落进 .log, 对齐 tone_words.py 黄金范式。纯日志, 不改任何产物。emit 在函数体内
    (绝不在模块顶层 import 时执行 — 防生产日志首写截断)。
    """
    try:
        import platform
        import sys

        # ① 🧭 项目 / 环境信息
        log.info("  🧭 项目 / 环境信息")
        log.info(f"     · 阶段: {stage_name} (Stata 数据导出层; STAGES_MAIN 末端「出关口岸」)")
        log.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板; v3.11.1)")
        log.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        log.info(f"     · 工作目录: {os.getcwd()}")
        log.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        log.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        log.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                 "本阶段纯 CPU 函数转换 / 无 LLM·Embedding·网络·API ($0)")

        # ② 📂 输入 / 输出文件
        log.info("  📂 输入 / 输出文件")
        log.info(f"     · 输入:   {panel_path} (stage 45 产出 bank-year 全列面板)")
        log.info(f"     · 输出.dta:      {os.path.join(output_dir, '46_panel_yearly_full.dta')}")
        log.info(f"     · 输出labels.do: {os.path.join(output_dir, '46_panel_yearly_labels.do')}")
        log.info(f"     · 输出codebook:  {os.path.join(output_dir, '46_panel_yearly_codebook.xlsx')}")

        # ③ ⚙ 运行配置 (本阶段 Stata 硬限 + 类别编码方向 + backend 选择策略)
        log.info("  ⚙ 运行配置 (Stata 硬限 + 类别编码; 来源=本模块常量 + config/paths.yaml)")
        log.info(f"     · Stata 硬限: 变量名 ≤{STATA_VAR_NAME_MAXLEN} 字符 | "
                 f"变量标签 ≤{STATA_VAR_LABEL_MAXLEN} 字节 | .dta format version=118 (文件格式编号≠Stata 版本)")
        log.info(f"     · 类别编码方向 (0=baseline / 1=对照): LOCUS={LOCUS_ENCODING} | "
                 f"SUBST={SUBSTANTIVENESS_ENCODING} | COLLAB={COLLAB_MODE_ENCODING}")
        log.info("     · backend 优先级: pyreadstat (嵌入 value labels + 中文 column labels) → "
                 "fallback pandas to_stata (WARN; 须手动 run labels.do)")
        log.info("     · int8/Int8 非 value-labeled 计数列一律升 Int16 (避开 Stata byte 缺失码位 101..127)")
        log.info("     · codebook 全列均为分析列 (2026-06-21 起取消 is_core 核心/辅助列区分)")

        # ④ 📖 方法论依据 (参考文献 emit 进日志; 仅引经核验注册表条目, 逐字照抄 DOI)
        log.info("  📖 方法论依据 (本阶段类别编码 / 三轨归因 / 词典-清晰度标签的学术出处)")
        log.info("     · 实体邻近归因 (ctx 轨): Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). "
                 "Firm-level political risk: Measurement and effects. The Quarterly Journal of Economics, "
                 "134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021")
        log.info("       → ctx 轨用实体窗口截取文本, 把语调归因到目标银行而非全文背景, 降低主题串味。")
        log.info("     · 媒体共提及计量 (ss 轨): Gentzkow, M., & Shapiro, J. M. (2010). What drives media "
                 "slant? Evidence from U.S. daily newspapers. Econometrica, 78(1), 35–71. "
                 "https://doi.org/10.3982/ECTA7195")
        log.info("     · 媒体共提及计量 (ss 轨): Dougal, C., Engelberg, J., García, D., & Parsons, C. A. (2012). "
                 "Journalists and the stock market. The Review of Financial Studies, 25(3), 639-679. "
                 "https://doi.org/10.1093/rfs/hhr133")
        log.info("       → ss 轨 (银行+金科同句共现) 与 ctx 的 proximity 谱系并列, 度量银行-金科共提及强度。")
        log.info("     · 文本清晰度词典: Loughran, T., & McDonald, B. (2011). When is a liability not a "
                 "liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), "
                 "35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x")
        log.info("     · 文本清晰度词典: You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of "
                 "the pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055")
        log.info("       → clarity / definite / ambiguous 三轨标签的学术锚点 (本阶段为这些派生列贴 Stata 标签)。")
    except Exception as e:  # noqa: BLE001
        log.warning(f"  环境/配置/方法论 banner 打印失败 (不影响导出): {e}")


def main():
    """Stage 46 CLI 入口 (由 thin shim 46_stata_export.py 调用)."""
    import time as _time

    from news_process.core.config import load_config
    from news_process.core.logging import log_stage_summary, setup_logging

    _stage_start = _time.time()
    CONFIG = load_config()
    STAGE_NAME = '46_stata_export'
    log = setup_logging(STAGE_NAME, CONFIG['paths']['log_dir'])

    # ── 【功能】banner (黄金范式: 紧随 setup_logging 之后, 替换而非叠加旧短 banner) ──
    log.info("=" * 72)
    log.info("阶段 46: Stata 数据导出 (parquet → .dta + value labels, plan v14 §9.1)")
    log.info("=" * 72)
    log.info("【功能】数据的「出关口岸」: 把 stage 45 的 bank-year 全列面板 (40_panel_yearly.parquet)")
    log.info("        翻译成经济学家 Stata 能直读的 .dta, 并附 variable/value labels 的 .do 脚本")
    log.info("        与人类可读的 codebook.xlsx 变量字典 (含 original_name 反查)。")
    log.info("【方法】① 三套中文类别 str→byte 0/1 + value label (LOCUS/SUBSTANTIVENESS/COLLAB_MODE,")
    log.info("        当前 bank-year 面板无文章级 str 列 → no-op); ② 非 value-labeled int8 计数列升")
    log.info("        Int16 (避开 Stata byte 缺失码位 101..127); ③ 列名超 32 字符缩写+md5 去重, 中文")
    log.info("        列名转写为合法 ASCII; ④ 写前 _assert_track_triplet_unique 断言 full/ctx/ss 三轨")
    log.info("        缩短后不撞名; ⑤ NaN→. (sysmiss); .dta format version=118 (文件格式编号≠Stata 版本)。")
    log.info("【判读】是格式转换层, 不改任何数值。看产出健康度: 列名缩短/撞名=0 为好; 标签覆盖率越高越好;")
    log.info("        .dta 行数须与 parquet 完全一致 (round-trip 无丢行); fintech 三轨主指标 (_full/_ctx/_ss)")
    log.info("        在面板里齐备为好, 缺则下游论文该轨回归空跑。")
    log.info("【确定性】纯 CPU 函数转换, 无 LLM/Embedding/网络; 输入 parquet 固定则输出值稳定")
    log.info("        (仅 .dta 二进制随 backend pyreadstat/pandas 选择漂移)。")

    panel_filename = CONFIG.get('filenames', {}).get('output_40_panel_yearly', '40_panel_yearly.parquet')
    panel_path = os.path.join(CONFIG['paths']['output_dir'], panel_filename)
    output_dir = CONFIG['paths']['output_dir']

    # ── 项目/环境/配置/方法论 banner (日志富集 2026-06-24; 函数体内 emit, golden-safe) ──
    _log_environment_and_config(log, STAGE_NAME, panel_path, output_dir)

    results = export_panel_to_stata(panel_path, output_dir)
    log.info(f"Stage 46 完成. 产出:")
    for k, v in results.items():
        log.info(f"  {k}: {v}")

    _log_export_result_analysis(log, panel_path, results)

    # ⏱ 阶段总墙钟 + RSS (log_stage_summary; 行数取产出 .dta 视产物存在性)
    try:
        log_stage_summary(log, STAGE_NAME, _stage_start)
    except Exception as _se:  # noqa: BLE001
        log.warning(f"  log_stage_summary 失败 (不影响产物): {_se}")


if __name__ == '__main__':
    main()
