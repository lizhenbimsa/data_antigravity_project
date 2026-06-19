"""news_process.pipeline.panel.stata_export — Stage 46 Stata 数据导出层 (v3.2.0)

功能 (plan v14 §9.1):
    把 stage 45 panel parquet (40_panel_yearly.parquet) 转换为 Stata .dta + labels.

输出 (2026-06-12 起单一全列 .dta; 本机 StataNow/MP 19.5 maxvar≤120,000 直读全列,
不再做 core/aux 双切分 — 原 IC ≤2048 兼容切分仅为外部协作者保留, 已按项目策略移除):
    46_panel_yearly_full.dta    # 全列 (Stata SE/MP; 唯一 .dta 产物)
    46_panel_yearly_labels.do   # variable/value labels Stata 脚本
    46_panel_yearly_codebook.xlsx  # 人类可读变量字典 (is_core 列仍标注分析核心变量子集)

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
6. `assign_core_columns`(STATA_IC_MAX_VARS=2048 守卫分析核心列别膨胀; 2026-06-12 起仅供 codebook is_core 标注, 不再驱动文件切分; 声明却缺席的 pattern 记 WARN 监测 schema 漂移)。
7. `write_dta` 写单一 `*_full.dta`; `write_labels_do_file` 写 labels.do (compound double quotes 安全转义); `_write_codebook_xlsx` 写 codebook (engine='xlsxwriter', 非阻塞, 失败仅 WARN)。

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

logger = logging.getLogger(__name__)

# Stata 硬限 (plan v14 §9.5 / R32-D, R42-A 修复)
STATA_VAR_NAME_MAXLEN = 32      # 变量名最长 32 字符
STATA_VAR_LABEL_MAXLEN = 80     # 变量标签最长 80 字符
STATA_IC_MAX_VARS = 2048        # Stata IC license 最大列数
# 白话: 2048 是给外部协作者用低配 Stata IC 版预留的兼容上限, 不是本机限制
# (本机 StataNow/MP 19.5 上限 12 万列)。2026-06-12 起已不再按它拆 core/aux
# 两个 .dta, 只剩 assign_core_columns 用它做"分析核心列别膨胀过头"的守卫。

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
        'mean_frac_definite_full':          "Mean Frac Definite from indep Full scan (You 2018 Panel C 388 words)",
        'mean_frac_definite_ctx':           "Mean Frac Definite from indep Ctx scan (You 2018 Panel C 388 words)",
        'frac_amb_articles_full':           "Frac Articles Ambiguous Full (>=D0 median, You 2018 Panel D)",
        'frac_amb_articles_ctx':            "Frac Articles Ambiguous Ctx (>=D0 median, You 2018 Panel D)",
        # v3.5.1 A3 Numerical Intensity (数值披露强度; 引文勘误见 codebook reference) 三轨 (full/ctx/ss)
        'mean_num_intensity_full':          "Mean Numerical Intensity Full (three-track)",
        'mean_num_intensity_ctx':           "Mean Numerical Intensity Ctx (three-track)",
        # remove-title-track: title-indicator labels 已移除
        # ─────────────────────────────────────────────────────────────
        # 2026-05-29 双模型嵌入: text2vec 稳健 twin (主轨=text-embedding-3-small,
        # 这些 _t2v 列=shibing624/text2vec-base-chinese 同算法只换模型)。落 aux。
        # ─────────────────────────────────────────────────────────────
        'strat_diff_t2v_full':              "Strat Diff (T2V robust=text2vec, full)",
        'strat_diff_t2v_ctx':               "Strat Diff (T2V robust=text2vec, ctx)",
        'strat_diff_n5_emb_t2v':            "Strat Diff N5 Emb (T2V robust, full)",
        'strat_diff_n5_emb_t2v_ctx':        "Strat Diff N5 Emb (T2V robust, ctx)",
        'strat_sim_max_emb_t2v':            "Strat Max Sim Emb (T2V robust, full)",
        'strat_sim_max_emb_t2v_ctx':        "Strat Max Sim Emb (T2V robust, ctx)",
        'centroid_diff_emb_t2v':            "Centroid Diff Emb (T2V robust, full)",
        'centroid_diff_emb_t2v_ctx':        "Centroid Diff Emb (T2V robust, ctx)",
        'coh_emb_t2v_full':                 "Temporal Coherence Emb (T2V robust, full)",
        'coh_emb_t2v_ctx':                  "Temporal Coherence Emb (T2V robust, ctx)",
        'policy_cosine_sim_t2v_full':       "Policy Cosine Sim (T2V robust, full)",
        'policy_cosine_sim_t2v_ctx':        "Policy Cosine Sim (T2V robust, ctx)",
        'auth_sim_emb_t2v_full':            "Auth Policy Sim Emb (T2V robust, full)",
        'auth_sim_emb_t2v_ctx':             "Auth Policy Sim Emb (T2V robust, ctx)",
        'benefit_mean_t2v_full':            "Benefit Attitude Mean (T2V robust, full)",
        'benefit_mean_t2v_ctx':             "Benefit Attitude Mean (T2V robust, ctx)",
        'benefit_std_t2v_full':             "Benefit Attitude SD (T2V robust, full)",
        'benefit_std_t2v_ctx':              "Benefit Attitude SD (T2V robust, ctx)",
        'benefit_pos_frac_t2v_full':        "Benefit Pos Frac (T2V robust, full)",
        'benefit_pos_frac_t2v_ctx':         "Benefit Pos Frac (T2V robust, ctx)",
        'benefit_neg_frac_t2v_full':        "Benefit Neg Frac (T2V robust, full)",
        'benefit_neg_frac_t2v_ctx':         "Benefit Neg Frac (T2V robust, ctx)",
        'emb_peer_tone_lag1_t2v_full':      "Emb Peer Tone Lag1 (T2V robust, full)",
        'bank_emb_sim_mean_lag1':           "Bank Emb Sim Mean (L1)",
        'bank_emb_sim_mean_lag1_t2v':       "Bank Emb Sim Mean (L1, T2V robust)",
        'industry_neg_shock_lag1':          "Industry Neg Shock LOO (L1, year-FE-safe)",
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
        # text2vec 稳健 twin ss 轨 (shibing624/text2vec-base-chinese)
        'strat_diff_t2v_ss':                "Strat Diff (T2V robust=text2vec, ss 银行+金科同句)",
        'strat_diff_n5_emb_t2v_ss':         "Strat Diff N5 Emb (T2V robust, ss 银行+金科同句)",
        'strat_sim_max_emb_t2v_ss':         "Strat Max Sim Emb (T2V robust, ss 银行+金科同句)",
        'centroid_diff_emb_t2v_ss':         "Centroid Diff Emb (T2V robust, ss 银行+金科同句)",
        'coh_emb_t2v_ss':                   "Temporal Coherence Emb (T2V robust, ss 银行+金科同句)",
        'policy_cosine_sim_t2v_ss':         "Policy Cosine Sim (T2V robust, ss 银行+金科同句)",
        'auth_sim_emb_t2v_ss':              "Auth Policy Sim Emb (T2V robust, ss 银行+金科同句)",
        'benefit_mean_t2v_ss':              "Benefit Attitude Mean (T2V robust, ss 银行+金科同句)",
        'benefit_std_t2v_ss':               "Benefit Attitude SD (T2V robust, ss 银行+金科同句)",
        'benefit_pos_frac_t2v_ss':          "Benefit Pos Frac (T2V robust, ss 银行+金科同句)",
        'benefit_neg_frac_t2v_ss':          "Benefit Neg Frac (T2V robust, ss 银行+金科同句)",
        # IV 扩展族 ss 轨镜像 lpeer_*_ss / zone_leave1out_benefit_iv_ss
        # (各自 just-identified 并排, 禁与 full/ctx 混 over-id Hansen J)
        'zone_leave1out_benefit_iv_ss':     "Same-zone (cross-prov) LOO benefit-attitude IV (ss 银行+金科同句)",
        'lpeer_attention_iv_ss':            "Same-type peer LOO attention IV (ss 银行+金科同句, same-sent window)",
        'lpeer_subst_iv_ss':                "Same-type peer LOO substantive-share IV (ss 银行+金科同句)",
        'lpeer_locus_iv_ss':                "Same-type peer LOO tech-locus IV (ss 银行+金科同句)",
        'lpeer_collab_iv_ss':               "Same-type peer LOO collaboration-share IV (ss 银行+金科同句)",
        'lpeer_benefit_iv_ss':              "Same-type peer LOO benefit-attitude IV (ss 银行+金科同句)",
    }

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


def assign_core_columns(df: pd.DataFrame, rename_map: Dict[str, str] = None) -> List[str]:
    """按 plan v14 §9.1 (R42-A + R44-A): 划分 core 列 (≤ 2048, Stata IC 兼容).

    fix(omni-g-stata-export-09, 2026-06-11): 新增 rename_map 参数
    ({short_stata_name: original_panel_name}) — core_patterns 以原始列名声明,
    此前 >32 字符的声明列被 shorten 改名后按原名匹配必 miss → 静默落 aux。
    fix(omni-g-stata-export-07, 2026-06-11): 声明却缺席的 pattern 记 warning
    (此前 ``if c in df.columns`` 静默吞掉 schema 漂移, 23 个死 pattern 零告警)。

    Core 列规则:
        - 主键 (target_bank, year)
        - sentiment 三轨 (full/ctx/ss) 主指标 (llm_sentiment_*, llm_vote_*, llm_prob_score_*)
        - stage 3 三轨标签 + confidence (innovation_*_{full,ctx,ss})
        - dual gate 三互斥指示
        - 主子集 mean 列 (_lf × _full 隐式 + _lc × _ctx 显式对角线)
        - 主洗稿率 count
        - 主 Bartik IV (bartik_type_iv_*, full/ctx) + fintech 稳健套 (lf)
        - 基础统计 (n_articles, frac, ln_news_coverage)

    Aux 列:
        - 4-way 洗稿率非主组合 (sentiment × subst 笛卡尔积非对角)
        - inter-track κ
        - 历史保留列

    白话: 这个函数从上千列的面板里挑出"做主回归真正要用的核心列"清单。
    早期会按这份清单把数据拆成 core.dta (≤2048 列, 低配 Stata IC 也能打开)
    和 aux.dta 两个文件; 2026-06-12 起不再拆分、只写单一全列 .dta, 这份
    清单现在只用来 (1) 在 codebook 里给核心列打 is_core 标记, (2) 守卫
    核心列数量别无节制膨胀超过 2048。
    """
    rename_map = rename_map or {}
    core_patterns = [
        # 主键
        'target_bank', 'year',
        # 基础统计 + bank 属性
        'n_articles', 'n_articles_llm_valid', 'n_articles_llm_valid_ctx', 'n_articles_llm_valid_ss', 'media_breadth', 'ln_news_coverage', 'bank_type',
        'bank_size', 'bank_age', 'bank_province', 'bank_zone',
        'digital_frontier',
        # sentiment 三轨 (full/ctx/ss) 主指标 — ss = 银行+金科同句共现轨
        'llm_sentiment_full', 'llm_sentiment_ctx', 'llm_sentiment_ss',
        'llm_vote_tone_full', 'llm_vote_tone_ctx', 'llm_vote_tone_ss',
        'llm_prob_score_full', 'llm_prob_score_ctx', 'llm_prob_score_ss',
        'avg_llm_prob_score_full', 'avg_llm_prob_score_ctx', 'avg_llm_prob_score_ss',
        # stage 3 三轨标签 + confidence (v3.4.0: 加 collab_mode 第三维度; ss = 同句共现)
        'innovation_locus_full', 'innovation_locus_ctx', 'innovation_locus_ss',
        'innovation_substantiveness_full', 'innovation_substantiveness_ctx', 'innovation_substantiveness_ss',
        'innovation_collab_mode_full', 'innovation_collab_mode_ctx', 'innovation_collab_mode_ss',
        'innovation_collab_mode_confidence_full', 'innovation_collab_mode_confidence_ctx', 'innovation_collab_mode_confidence_ss',
        'category_confidence_full', 'category_confidence_ctx', 'category_confidence_ss',
        # fix(omni-g-stata-export-07, 2026-06-11; three-track-verify 2026-06-18): panel 级
        # 聚合列名。avg_category_confidence(=_full 别名) + _full/_ctx; ss 轨刻意不做该分类
        # 置信度聚合 (与 encode.py:1331-1332/1752-1754 cell_id 口径一致: ss 当纯情感轨, LLM
        # 分类属性仅 full/ctx) → 删去原 _ss 过度声明 (producer 不产出 avg_category_confidence_ss)。
        'avg_category_confidence',
        'avg_category_confidence_full', 'avg_category_confidence_ctx',
        'avg_il_confidence_full', 'avg_il_confidence_ctx', 'avg_il_confidence_ss',
        'avg_iss_confidence_full', 'avg_iss_confidence_ctx', 'avg_iss_confidence_ss',
        'avg_icm_confidence_full', 'avg_icm_confidence_ctx', 'avg_icm_confidence_ss',
        # dual gate = full×ctx 二元互斥划分 (数学上只有 3 态 _full_only/_ctx_only/_both;
        # fix(three-track-verify 2026-06-18): 删去原 'llm_verified_dual_ss_only' — dual 是二元,
        # 无 ss_only 态; 第三轨 ss 验证态由独立的 llm_verified_triple_ss_only 覆盖, tone_llms.py:2146)
        'llm_verified_dual_full_only', 'llm_verified_dual_ctx_only', 'llm_verified_dual_both',
        # 主子集对角线 (_lf × _full 隐式 + _lc × _ctx 显式; ss 轨情感 × ss-锚定分类对角 _ls/_ss)
        'tech_frac', 'app_frac', 'sub_frac', 'symb_frac',
        'tech_frac_lc', 'app_frac_lc', 'sub_frac_sc', 'symb_frac_sc',
        # fix(three-track-verify, 2026-06-18): 补 ss 轨对角 frac 主测度, 恢复
        # full(:上行 tech_frac)/ctx(_lc/_sc)/ss 三轨 is_core 平价 (encode.py 实产
        # tech_frac_ls/app_frac_ls/sub_frac_ss/symb_frac_ss; 此前漏注册 → ss 主测度未标 is_core)
        'tech_frac_ls', 'app_frac_ls', 'sub_frac_ss', 'symb_frac_ss',
        'n_articles_tech', 'n_articles_app', 'n_articles_sub', 'n_articles_symb',
        'n_articles_tech_lc_ctx', 'n_articles_app_lc_ctx',
        'n_articles_sub_sc_ctx', 'n_articles_symb_sc_ctx',
        # fix(three-track-verify, 2026-06-18): ss 轨对角计数真名用 _ls_ss/_ss_ss 中缀
        # (encode.py:1433/1436/1578/1581); 原 _lc_ss/_sc_ss 是 ctx 中缀误抄, 永不命中→schema-drift WARN
        'n_articles_tech_ls_ss', 'n_articles_app_ls_ss',
        'n_articles_sub_ss_ss', 'n_articles_symb_ss_ss',
        'llm_vote_tone_tech_full', 'llm_vote_tone_app_full',
        'llm_vote_tone_tech_lc_ctx', 'llm_vote_tone_app_lc_ctx',
        'llm_vote_tone_tech_ls_ss', 'llm_vote_tone_app_ls_ss',
        'llm_vote_tone_sub_full', 'llm_vote_tone_symb_full',
        'llm_vote_tone_sub_sc_ctx', 'llm_vote_tone_symb_sc_ctx',
        'llm_vote_tone_sub_ss_ss', 'llm_vote_tone_symb_ss_ss',
        # tone gap (full/ctx/ss 三轨; ss = 银行+金科同句情感差)
        'tone_gap_tech_app', 'tone_gap_tech_app_lc_ctx', 'tone_gap_tech_app_ls_ss',
        'tone_gap_sub_symb', 'tone_gap_sub_symb_sc_ctx', 'tone_gap_sub_symb_ss_ss',
        # 主 Bartik IV (full/ctx/ss; _title 列已随标题情感轨删除)
        # fix(omni-g-stata-export-07, 2026-06-11): 原声明 'bartik_fintech_iv_*'
        # 是幻影列名 (生产代码从不产出) → 改真实列名: 主 Bartik = 银行类型
        # bartik_type_iv_* (runner.py 'type'; iv_did.py f'bartik_{prefix}_iv{track}'),
        # fintech 稳健套 = bartik_fintech_lf_iv_* (share=innovation_locus_full 基期占比)
        # 三轨 (full/ctx/ss): ss 镜像 bartik_*_iv_ss; full×ctx×ss 各自 just-identified
        # 并排, 禁混进同一 over-id Hansen J (镜像 ctx 红线)。
        'bartik_type_iv_full', 'bartik_type_iv_ctx', 'bartik_type_iv_ss',
        'bartik_fintech_lf_iv_full', 'bartik_fintech_lf_iv_ctx', 'bartik_fintech_lf_iv_ss',
        # 主洗稿率 count (sentiment × _full/_ctx/_ss)
        'pos_symb_count_full', 'pos_symb_count_ctx', 'pos_symb_count_ss',
        'neg_sub_count_full', 'neg_sub_count_ctx', 'neg_sub_count_ss',
        # Plan v1.37 P2 §5.3.4: 二元 prob_score 列 (归入分析核心列, 非 aux);
        # 三维对称补 collab (2026-06-14) → 18 列 = 3 维 × 3 轨 (full/ctx/ss) × {mean, std}。
        'avg_subst_prob_score_full', 'avg_subst_prob_score_ctx', 'avg_subst_prob_score_ss',
        'avg_subst_prob_score_std_full', 'avg_subst_prob_score_std_ctx', 'avg_subst_prob_score_std_ss',
        'avg_locus_prob_score_full', 'avg_locus_prob_score_ctx', 'avg_locus_prob_score_ss',
        'avg_locus_prob_score_std_full', 'avg_locus_prob_score_std_ctx', 'avg_locus_prob_score_std_ss',
        'avg_collab_prob_score_full', 'avg_collab_prob_score_ctx', 'avg_collab_prob_score_ss',
        'avg_collab_prob_score_std_full', 'avg_collab_prob_score_std_ctx', 'avg_collab_prob_score_std_ss',
        # v3.5.1 A1 Lexical Clarity (LM 2011 JF; You 2018) — 9 列 (三轨 full/ctx/ss) 全进 core
        # (per plan v0.3 §1.3 invariant + §2.4.1; core 仍远低于 IC 2048).
        'mean_clarity_score_full', 'mean_clarity_score_ctx', 'mean_clarity_score_ss',
        'mean_frac_definite_full', 'mean_frac_definite_ctx', 'mean_frac_definite_ss',
        'frac_amb_articles_full', 'frac_amb_articles_ctx', 'frac_amb_articles_ss',
        # v3.5.1 A3 Numerical Intensity (数值披露强度) — 3 列 (三轨 full/ctx/ss) 全进 core
        'mean_num_intensity_full', 'mean_num_intensity_ctx', 'mean_num_intensity_ss',
        # v3.7.2 R8-H1 全管道延伸: ctx 独立度信号 (entity-miss → ctx ≡ full → 该轨退化为 full)
        # ⚠ 与 intensity_verified_{full,ctx} 不同义:
        #    - frac_ctx_fallback: 上游 entity_context 提取失败 (Hassan 2019 QJE proximity)
        #    - intensity_verified_*: stage 14 fintech 关键词 IDF 验证失败
        # n_articles_for_ctx_independence: 绝对独立文章数, 避免按比例 filter 时的银行规模偏差
        # 论文用途: P1 (llm_vote_tone_ctx) / P11 (mean_clarity_score_ctx) measurement-error robustness
        'frac_ctx_fallback', 'n_articles_for_ctx_independence',
        # remove-title-track: 原 v3.7.4 P3.1.6 的 title indicator 列 (Panel D/E
        # 分层稳健性) 已随标题情感轨整体移除, 此处不再声明对应 pattern。
        # 历史锚点留档: Antweiler-Frank (2004) JF subject-relevance threshold;
        #               Da-Engelberg-Gao (2011) JF attention-channel separation.
        # ─────────────────────────────────────────────────────────────
        # v3.5.2 PR #14 集成 — A1 LM 6 子词典 + A2 FLS (本批列在 v3.5.2
        # PR #3 panel 集成完成前会被 ``if c in df.columns`` 过滤; append-only
        # 不破坏 v3.6.0 已 frozen 契约).
        # ─────────────────────────────────────────────────────────────
        # A1 LM 2011 JF non-sentiment 6 子词典 (18 列三轨 full/ctx/ss; v3.10.0 +modal_weak/complexity)
        'uncert_frac_full', 'uncert_frac_ctx', 'uncert_frac_ss',
        'litig_frac_full', 'litig_frac_ctx', 'litig_frac_ss',
        'constr_frac_full', 'constr_frac_ctx', 'constr_frac_ss',
        'modal_strong_frac_full', 'modal_strong_frac_ctx', 'modal_strong_frac_ss',
        'modal_weak_frac_full', 'modal_weak_frac_ctx', 'modal_weak_frac_ss',
        'complexity_frac_full', 'complexity_frac_ctx', 'complexity_frac_ss',
        # A2 Forward-Looking Statements (Li 2010 JAR) — 3 列三轨 full/ctx/ss
        'frac_fls_full', 'frac_fls_ctx', 'frac_fls_ss',
        # ─────────────────────────────────────────────────────────────
        # v3.6.1 PR #14 集成 — C1 媒体 3 级 tier
        # ─────────────────────────────────────────────────────────────
        # C1 媒体 tier 加权 (sensitivity, 不替换原 media_authority_weight)
        'media_authority_weight_tier', 'media_tier_label',
        # ─────────────────────────────────────────────────────────────
        # v3.7.0 PR #14 集成 — D 组 (staleness / α)
        # ─────────────────────────────────────────────────────────────
        # D2 staleness 双指标 (三轨 full/ctx/ss; surface_staleness_ss 免费加,
        # semantic_staleness_ss 依赖 ss SBERT (stage 30a 未上线时优雅缺席→落 NaN/被过滤))
        'surface_staleness_full', 'surface_staleness_ctx', 'surface_staleness_ss',
        'semantic_staleness_full', 'semantic_staleness_ctx', 'semantic_staleness_ss',
        # D3 Krippendorff α (与第 10 篇 bank_media_disagreement 对齐; 三轨 full/ctx/ss)
        'cross_outlet_tone_variance_full', 'cross_outlet_tone_variance_ctx', 'cross_outlet_tone_variance_ss',
        'cross_media_alpha_full', 'cross_media_alpha_ctx', 'cross_media_alpha_ss',
        # ─────────────────────────────────────────────────────────────
        # IV 扩展族 LOO 同业工具 (2026-06-13 iv_extensions.py; 单一 .dta 下
        # 仅作 is_core 标记 + 计数守卫, 不影响落盘)。名以"原始 panel 名"声明:
        # full 轨 _lag1 (>32 字符) 经 rename_map 反查短名匹配; ctx/ss 轨 lpeer_*
        # (≤32) 直名匹配。三轨 (full/ctx/ss) 镜像各自 just-identified 并排, 非 overid
        # (full×ctx×ss 禁混进同一 over-id Hansen J — 镜像 ctx 红线)。
        # ─────────────────────────────────────────────────────────────
        'leave_one_out_peer_attention_iv', 'leave_one_out_peer_attention_iv_lag1',
        'leave_one_out_peer_subst_iv', 'leave_one_out_peer_subst_iv_lag1',
        'leave_one_out_peer_locus_iv', 'leave_one_out_peer_locus_iv_lag1',
        'leave_one_out_peer_collab_iv', 'leave_one_out_peer_collab_iv_lag1',
        'leave_one_out_peer_benefit_iv', 'leave_one_out_peer_benefit_iv_lag1',
        'zone_leave1out_benefit_iv', 'zone_leave1out_benefit_iv_ctx', 'zone_leave1out_benefit_iv_ss',
        'lpeer_attention_iv_ctx', 'lpeer_attention_iv_ctx_lag1',
        'lpeer_subst_iv_ctx', 'lpeer_subst_iv_ctx_lag1',
        'lpeer_locus_iv_ctx', 'lpeer_locus_iv_ctx_lag1',
        'lpeer_collab_iv_ctx', 'lpeer_collab_iv_ctx_lag1',
        'lpeer_benefit_iv_ctx', 'lpeer_benefit_iv_ctx_lag1',
        # ss 轨镜像 lpeer_*_ss (银行+金科同句 same-sentence window)
        'lpeer_attention_iv_ss', 'lpeer_attention_iv_ss_lag1',
        'lpeer_subst_iv_ss', 'lpeer_subst_iv_ss_lag1',
        'lpeer_locus_iv_ss', 'lpeer_locus_iv_ss_lag1',
        'lpeer_collab_iv_ss', 'lpeer_collab_iv_ss_lag1',
        'lpeer_benefit_iv_ss', 'lpeer_benefit_iv_ss_lag1',
    ]

    # fix(omni-g-stata-export-09, 2026-06-11): 改名列经 rename_map 反查原名匹配 —
    # pattern 命中原名时返回 df 中的短名 (如 innovation_collab_mode_confidence_*
    # 38/37 字符, shorten 后才存在于 df)
    orig2short = {orig: short for short, orig in rename_map.items()}
    core: List[str] = []
    seen: set = set()
    missing: List[str] = []
    for pattern in core_patterns:
        if pattern in df.columns:
            target = pattern
        elif pattern in orig2short and orig2short[pattern] in df.columns:
            target = orig2short[pattern]
        else:
            missing.append(pattern)
            continue
        if target not in seen:
            seen.add(target)
            core.append(target)

    # fix(omni-g-stata-export-07, 2026-06-11): 声明却缺席的 pattern 不再静默吞掉 —
    # 记 warning 监测 schema 漂移 (列改名/退役后 core_patterns 未同步即在此暴露)
    if missing:
        logger.warning(
            f"  assign_core_columns: {len(missing)} 个声明的 core pattern 在 panel 中缺席 "
            f"(schema 漂移监测; 样本: {missing[:8]})"
        )

    if len(core) > STATA_IC_MAX_VARS:
        raise ValueError(
            f"分析核心列数 {len(core)} 超过 STATA_IC_MAX_VARS={STATA_IC_MAX_VARS} 守卫上限. "
            f"core/aux 双切分已于 2026-06-12 移除, 此守卫现仅防 codebook is_core 的"
            f"分析核心列清单无节制膨胀 — 请精简 assign_core_columns 的 core_patterns "
            f"或上调 STATA_IC_MAX_VARS (本机 StataNow/MP 19.5 直读全列, 无 IC 列数约束)."
        )

    logger.info(f"  Core 列数: {len(core)} / {len(df.columns)} (IC 余量 {STATA_IC_MAX_VARS - len(core)})")
    return core


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
    value_labels 键全程同步 + rename_map 链式压平, build_variable_labels /
    assign_core_columns 经原名反查 (改名列标签/core 归属不再静默丢失);
    ③ labels.do 头部带 backend 指纹。

    Args:
        panel_path: 输入 40_panel_yearly.parquet 路径
        output_dir: 输出目录 (data/processed/)
        output_prefix: 文件名前缀 (默认 46_panel_yearly)
    Returns:
        dict 含产出文件路径: {'full_dta', 'labels_do', 'codebook_xlsx', 'backend'}
        (2026-06-12: 移除 core/aux 双切分 — 本机 StataNow/MP 19.5 直读全列 full.dta;
         codebook is_core 列仍标注分析核心变量子集供参考)
    """
    backend_name, write_dta = _select_dta_backend()

    logger.info("=== Stage 46 Stata Export (plan v14 §9.1) ===")
    logger.info(f"  Backend: {backend_name}")
    logger.info(f"  输入: {panel_path}")

    if not os.path.exists(panel_path):
        raise FileNotFoundError(f"panel parquet 不存在: {panel_path}")

    df = pd.read_parquet(panel_path)
    logger.info(f"  panel 载入: {len(df)} 行 × {len(df.columns)} 列")

    # 1. 类别变量编码 (中文 str → byte 0/1)
    df_encoded, value_labels = encode_categorical_columns(df)

    # 1a'. fix(omni-g-stata-export-01, 2026-06-11): 计数列禁 Int8 — 非 value-labeled
    # int8/Int8 列升 Int16 (Stata byte 上限 100 零余量; 101..127 是缺失码位,
    # pyreadstat 直写损值 / pandas 静默升型 → 两后端在此统一)
    df_encoded = upcast_unsafe_int8_columns(df_encoded, value_labels)

    # 1b. v3.2.0 M3/7: 自动缩短超 32 字符列名 (Stata 硬限) + 记录 mapping
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

    # 2. 生成 variable labels (改名列经 rename_map 反查原名命中 codebook/HEURISTIC)
    var_labels = build_variable_labels(df_encoded, rename_map=rename_map)

    # 3. Stata 兼容性校验 (plan v14 §9.5; 缩短后应全过)
    validate_stata_compat(df_encoded, var_labels)

    # 4. 计算分析核心列归属 (2026-06-12: 不再写独立 core.dta; 仅供 codebook is_core
    #    列标注核心变量子集 — 主键 + 三轨 (full/ctx/ss) 主指标 + stage3 标签 + 主 Bartik 等)。
    #    本机 StataNow/MP 19.5 (maxvar≤120,000) 直读全列 full.dta, 无需 IC core/aux 切分。
    #    assign_core_columns 内的 ≤2048 守卫保留为分析核心规模回归监测 (当前 ~100 列)。
    core_cols = assign_core_columns(df_encoded, rename_map=rename_map)

    # 5. 写单一全列 .dta (经 backend 抽象, 兼容 pyreadstat / pandas)
    full_path = os.path.join(output_dir, f'{output_prefix}_full.dta')
    write_dta(df_encoded, full_path, value_labels, var_labels)
    logger.info(f"  Full .dta 已写入: {full_path} ({len(df_encoded.columns)} 列; "
                f"含 {len(core_cols)} 个分析核心列, 单一全列导出不再拆分 core/aux)")

    # 6. labels .do (omni-03/15: 带 backend 指纹)
    labels_path = os.path.join(output_dir, f'{output_prefix}_labels.do')
    write_labels_do_file(labels_path, var_labels, value_labels, backend_name=backend_name)

    # 7. codebook .xlsx (依赖 codebook.py)
    codebook_path = os.path.join(output_dir, f'{output_prefix}_codebook.xlsx')
    try:
        _write_codebook_xlsx(df_encoded, var_labels, value_labels, core_cols, codebook_path,
                              rename_map=rename_map)
    except Exception as e:
        logger.warning(f"  codebook .xlsx 写入失败 (非阻塞): {e}")

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
    core_cols: List[str],
    out_path: str,
    rename_map: Dict[str, str] = None,
) -> None:
    """生成人类可读 codebook .xlsx.

    Args:
        rename_map: v3.2.0 M3/7 新增: {short_stata_name: original_panel_name}
                    用户可在 codebook 反查 Stata 短名对应的原 panel 列名.
    """
    if rename_map is None:
        rename_map = {}
    rows = []
    core_set = set(core_cols)
    for col in df.columns:
        rows.append({
            'var_name': col,
            'original_name': rename_map.get(col, col),  # M3/7: 缩短前原名 (用户反查)
            'label': var_labels.get(col, col),
            'data_type': str(df[col].dtype),
            'is_core': col in core_set,
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


def main():
    """Stage 46 CLI 入口 (由 thin shim 46_stata_export.py 调用)."""
    from news_process.core.config import load_config
    from news_process.core.logging import setup_logging

    CONFIG = load_config()
    STAGE_NAME = '46_stata_export'
    log = setup_logging(STAGE_NAME, CONFIG['paths']['log_dir'])

    # ── 【功能】banner (黄金范式: 紧随 setup_logging 之后, 替换而非叠加旧短 banner) ──
    log.info("=" * 72)
    log.info("阶段 46: Stata 数据导出 (parquet → .dta + value labels, plan v14 §9.1)")
    log.info("=" * 72)
    log.info("【功能】数据的「出关口岸」: 把 stage 45 的 bank-year 全列面板 (40_panel_yearly.parquet)")
    log.info("        翻译成经济学家 Stata 能直读的 .dta, 并附 variable/value labels 的 .do 脚本")
    log.info("        与人类可读的 codebook.xlsx 变量字典 (含 is_core/original_name 反查)。")
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

    results = export_panel_to_stata(panel_path, output_dir)
    log.info(f"Stage 46 完成. 产出:")
    for k, v in results.items():
        log.info(f"  {k}: {v}")

    _log_export_result_analysis(log, panel_path, results)


if __name__ == '__main__':
    main()
