"""
51_falsification_test.py — 伪造检验: 非金融科技对照变量构建
============================================================

学术背景与方法论依据:
  本脚本实现基于 Hassan et al. (2019) 伪造检验范式的构造效度验证。
  通过构建 non-fintech 控制变量（volume-based），检验核心 fintech tone
  指标是否具有超越一般媒体关注度的增量解释力。

参考文献:
  [1] Hassan, T.A., Hollander, S., van Lent, L. & Tahoun, A. (2019).
      "Firm-Level Political Risk: Measurement and Effects."
      The Quarterly Journal of Economics, 134(4), 2135-2202.
      → 本脚本核心方法论来源: Table 7 伪造检验范式 (PRisk vs NPRisk)

  [2] Fang, L. & Peress, J. (2009).
      "Media Coverage and the Cross-Section of Stock Returns."
      The Journal of Finance, 64(5), 2023-2052.
      → nf_ln_coverage = log(1 + count) 的对数变换依据

  [3] Tetlock, P.C. (2007).
      "Giving Content to Investor Sentiment: The Role of Media in the Stock Market."
      The Journal of Finance, 62(3), 1139-1168.
      → 新闻量 (volume) 与情感内容 (content) 的概念区分

  [4] Bushee, B.J., Core, J.E., Guay, W. & Hamm, S.J.W. (2010).
      "The Role of the Business Press as an Information Intermediary."
      Journal of Accounting Research, 48(1), 1-19.
      → nf_media_breadth (不同媒体来源数) 作为信息环境指标的依据

假设检验框架:
  H0: fintech tone 的解释力完全来自银行层面一般媒体关注度
  H1: fintech tone 包含金融科技维度的特异性增量信息

数据流:
  Non-Fintech = 12_fintech_news_full.parquet (全量银行新闻)
              MINUS 40_article_bank_level.parquet (最终面板文章)

  命名澄清 (勿因 "fintech" 字样误判): 12_fintech_news_full.parquet 是 stage 12
  在 **过滤之前** 落盘的全量分类结果 (news_fintech.py:295-321), 行集与上游
  11_bank_news.parquet **逐行一致 (1:1, 零删行)**, 仅多出 is_fintech_news 等 7 列
  金融科技标注。即 "_full" = "过滤前全量银行新闻", 而非 "仅金融科技新闻"
  (后者是 filter 后的 12_fintech_news.parquet, 为本文件 _full 的子集)。
  → anti-join 的「全量」基集用本文件正确; 之所以读 _full 而非 11_bank_news,
    是因为下游 build_non_fintech 需 is_fintech_news 列把对照组细分为
    ①关键词未匹配 / ②匹配但 LLM 拒绝 (11_bank_news 无此列, 换之会静默丢失该诊断)。

输入:
  data/processed/12_fintech_news_full.parquet
  data/processed/40_article_bank_level.parquet
  data/processed/40_panel_yearly.parquet

输出:
  data/processed/51_panel_with_controls.parquet
  data/processed/51_panel_with_controls.dta
  data/processed/51_falsification_diagnostics.csv

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 51_falsification_test.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**输入 (load_data, 三个文件硬读, 缺则 sys.exit(1))**: (a) `12_fintech_news_full.parquet` (stage 12 过滤前全量银行新闻, 与 11_bank_news 逐行 1:1, 含 is_fintech_news 标注; 命名带 fintech 但是全量底库); (b) `40_article_bank_level.parquet` (已进面板的金融科技文章); (c) `40_panel_yearly.parquet` (待挂控制变量的 bank-year 面板)。

**处理步骤 (main)**:
1. `build_non_fintech`(anti-join): Non-Fintech = 全量银行新闻 MINUS 面板文章, 复合键 (target_bank, 标题, _date_str) 双侧 drop_duplicates 后集合差集 (Hassan 2019 QJE Table 7 互补划分); 经 attrs 暴露 `nf_media_breadth_physical`(去重前物理口径 distinct-outlet 媒体广度, 转载计入广度) 与 `ft_dedup_agg`(去重 fintech 计数, fintech_share 同基分子)。
2. `aggregate_non_fintech`: 按 (target_bank, year) 聚合 — nf_n_articles(=count, 去重'同稿件'基) / nf_ln_coverage=ln(1+count)(Fang-Peress 2009) / nf_media_breadth(优先 attrs 物理口径 nunique, 缺则去重基回退) / nf_headline_frac=mean(target_bank_in_title)。
3. `merge_to_panel`: left join 挂面板 + 总量变量 — all_n_articles=ft_dedup+nf(同基, 缺 ft_dedup 时回退物理 n_articles+nf 混合基) / all_ln_coverage / fintech_share=ft_dedup/all_n_articles(分母0→NaN, zero_coverage 指示) / ln_ft_articles & ln_nf_articles(挤出弹性对, 两端同基) + 跨源一致性校验(去重 fintech 计数 ≤ 物理 n_articles 逐行)。
4. `run_diagnostics`: Pearson/Spearman 相关矩阵 (情感三轨 × nf_coverage; |r|<0.3 弱相关支持 H1) + 挤出弹性 r(ln_ft,ln_nf) 机械关联检测; 可用诊断列 <2 时返回 None。
5. `export_results`: save_dataset 写 parquet (input_files 记全 3 个 fan-in 源) + sanitize 列名写 .dta (失败 raise 不 swallow, 先删旧 .dta) + 诊断 CSV。
6. `print_stata_template` (读 papers_assets/bank_fintech_tone/do/falsification_template.do.tmpl) + `print_references`。

**注**: 模块还含三个 main() **未调用**的辅助函数 (供下游/测试): `generate_placebo_did_variables`(G-13 安慰剂时点 DID, 窗口截断于真处理年 [ty-k, ty), Callaway-Sant'Anna 2021) / `diagnose_fintech_classification_consistency`(G-09 收敛效度) / `diagnose_alias_matching_quality`(G-11 别名匹配质量)。

**假设框架**: H0 fintech tone 解释力全来自一般媒体关注度 vs H1 含金融科技特异性增量信息 (Hassan 2019 PRisk/NPRisk 范式)。

**外部依赖**: 无 LLM/Embedding/网络; 纯 pandas/numpy。确定性强。默认 timeout=7200。

**DAG 位置**: 上游 stage 12_full + stage 45 (40_panel_yearly + 40_article_bank_level), 三方 fan-in; 是主链末端阶段, 下游为 bank_fintech_tone 论文的 falsification_template.do 消费。

■ 白话说明

**这一步是什么**: 这是给核心结论做打假对照实验的一步。论文想说金融科技新闻的语调对银行有独特影响, 但有人会质疑: 是不是只要新闻多 (不管什么内容) 都有这个效果? 这一步就专门造一个对照组——把所有不是金融科技的银行新闻挑出来 (用减法: 全部银行新闻减掉已算进面板的金融科技新闻), 数一数每家银行每年有多少这种普通新闻、多少家媒体报道过, 当作安慰剂变量挂回面板。

**为什么需要它**: 做对比赛马: 把金融科技语调和普通新闻数量一起放进回归。如果控制了普通新闻量之后, 金融科技语调依然显著, 就证明它确实带了金融科技这一维度的独特信息, 而不只是新闻多的副产品。这是顶刊审稿人必问的稳健性检验。

**做得好不好的影响**: 这一步直接关系到论文核心论点站不站得住。它特别讲究数新闻要用同一把尺子——分子分母如果一个按物理篇数、一个按去重后的稿件数, 算出来的份额就会系统性偏大, 对比就失真。它还把全年没有任何新闻的银行年份标成未定义而不是零份额, 避免污染回归。做得好, 审稿人信服你的指标有独立价值; 做得粗糙, 这道防线一破, 整篇文章的因果解释都会被打问号。
========================================================================
"""

import os
import platform
import sys
import time
import warnings
from pathlib import Path

# Phase 4c: 让 ``python -m news_process.pipeline.falsification.controls`` 与
# pytest / 51_falsification_test.py 根 shim 都能解析包导入。
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

import numpy as np
import pandas as pd

from news_process.core.config import load_config
from news_process.core.logging import log_stage_summary, pct4, setup_logging, sig4
from news_process.core.reporting import save_dataset

warnings.filterwarnings('ignore', category=FutureWarning)

# ============================================================================
# 1. 全局配置与初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "51_falsification_test"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

OUTPUT_DIR = CONFIG["paths"]["output_dir"]
FILENAMES = CONFIG.get("filenames", {})

# ============================================================================
# 参考文献完整引用 (供日志输出)
# ============================================================================
REFERENCES = {
    'Hassan2019': (
        'Hassan, T.A., Hollander, S., van Lent, L. & Tahoun, A. (2019). '
        '"Firm-Level Political Risk: Measurement and Effects." '
        'The Quarterly Journal of Economics, 134(4), 2135-2202.'
    ),
    'Fang2009': (
        'Fang, L. & Peress, J. (2009). '
        '"Media Coverage and the Cross-Section of Stock Returns." '
        'The Journal of Finance, 64(5), 2023-2052.'
    ),
    'Tetlock2007': (
        'Tetlock, P.C. (2007). '
        '"Giving Content to Investor Sentiment: The Role of Media in the Stock Market." '
        'The Journal of Finance, 62(3), 1139-1168.'
    ),
    'Bushee2010': (
        'Bushee, B.J., Core, J.E., Guay, W. & Hamm, S.J.W. (2010). '
        '"The Role of the Business Press as an Information Intermediary." '
        'Journal of Accounting Research, 48(1), 1-19. '
        'doi:10.1111/j.1475-679X.2009.00357.x'  # 审计 2026-06-14 CIT-6: 锁定正确 DOI, 防 .00382 误植回归
    ),
    'Garcia2013': (
        'Garcia, D. (2013). '
        '"Sentiment during Recessions." '
        'The Journal of Finance, 68(3), 1267-1300.'
    ),
    'DimSV2024': (
        'Dim, C., Sangiorgi, I. & Vilkov, G. (2024). '
        '"Media Narratives and Price Informativeness." '
        'SSRN Working Paper No. 4323093.'
    ),
    # ── 以下引用为检验 8-10 (IV 回归, Oster 检验, 地理聚类) 新增 ──
    'LuoLi2025': (
        'Luo, Q. & Li, H. (2025). '
        '"Media sentiment and corporate R&D manipulation." '
        'Finance Research Letters, 81, 107505.'
    ),
    'Oster2019': (
        'Oster, E. (2019). '
        '"Unobservable Selection and Coefficient Stability: '
        'Theory and Evidence." '
        'Journal of Business & Economic Statistics, 37(2), 187-204.'
    ),
    'GurunButler2012': (
        'Gurun, U.G. & Butler, A.W. (2012). '
        '"Don\'t Believe the Hype: Local Media Slant, Local Advertising, '
        'and Firm Value." '
        'The Journal of Finance, 67(2), 561-598.'
    ),
    'CameronMiller2015': (
        'Cameron, A.C. & Miller, D.L. (2015). '
        '"A Practitioner\'s Guide to Cluster-Robust Inference." '
        'Journal of Human Resources, 50(2), 317-372.'
    ),
    # ── 以下引用为残差法稳健性检验新增 ──
    'FangWWY2024': (
        'Fang, Y., Wang, Q., Wang, Y. & Yuan, Y. (2024). '
        '"Media sentiment, deposit stability and bank systemic risk: '
        'Evidence from China." '
        'International Review of Economics & Finance, 91, 1150-1172.'
    ),
    # ── 以下引用为调节效应与异质性检验新增 ──
    'QuYang2025': (
        'Qu, L. & Yang, R. (2025). '
        '"Media sentiment, financial services, and corporate investment levels." '
        'Working Paper / Finance Research Letters series.'
    ),
    'BramborCG2006': (
        'Brambor, T., Clark, W.R. & Golder, M. (2006). '
        '"Understanding Interaction Models: Improving Empirical Analyses." '
        'Political Analysis, 14(1), 63-82.'
    ),
    'Chow1960': (
        'Chow, G.C. (1960). '
        '"Tests of Equality Between Sets of Coefficients in Two Linear Regressions." '
        'Econometrica, 28(3), 591-605.'
    ),
    # ── 以下引用为检验 15 (治理约束型合约控制变量) 新增 ──
    'ZhouCZY2026': (
        'Zhou, Y., Chen, L., Zhou, F. & Ye, M. (2026). '
        '"Contractual arrangements and information consistency: '
        'How ESG executive compensation incentives affect corporate AI disclosure." '
        'Journal of Business Research, 207, 116019. '
        'https://doi.org/10.1016/j.jbusres.2026.116019'
    ),
    'CoreGL2003': (
        'Core, J.E., Guay, W.R. & Larcker, D.F. (2003). '
        '"Executive Equity Compensation and Incentives: A Survey." '
        'FRBNY Economic Policy Review, 9(1), 27-50. '
        'https://www.newyorkfed.org/medialibrary/media/research/epr/03v09n1/0304core.pdf'
    ),
    'FlaBan2017': (
        'Flammer, C. & Bansal, P. (2017). '
        '"Does a Long-Term Orientation Create Value? Evidence from a '
        'Regression Discontinuity." '
        'Strategic Management Journal, 38(9), 1827-1847. '
        'https://doi.org/10.1002/smj.2629'
    ),
    'EdmGL2009': (
        'Edmans, A., Gabaix, X. & Landier, A. (2009). '
        '"A Multiplicative Model of Optimal CEO Incentives in Market Equilibrium." '
        'The Review of Financial Studies, 22(12), 4881-4917. '
        'https://doi.org/10.1093/rfs/hhn117'
    ),
    'IoanSer2015': (
        'Ioannou, I. & Serafeim, G. (2015). '
        '"The Impact of Corporate Social Responsibility on Investment Recommendations: '
        'Analysts\' Perceptions and Shifting Institutional Logics." '
        'Strategic Management Journal, 36(7), 1053-1081. '
        'https://doi.org/10.1002/smj.2268'
    ),
    'FamaJen1983': (
        'Fama, E.F. & Jensen, M.C. (1983). '
        '"Separation of Ownership and Control." '
        'Journal of Law and Economics, 26(2), 301-325. '
        'https://doi.org/10.1086/467037'
    ),
}

# ============================================================================
# 经核验 DOI 参考文献 (单一事实源 = VERIFIED_REFERENCES 注册表, 逐字照抄 APA-7 串)
# 日志富集 2026-06-24: 把本阶段核心方法/构念的学术出处 emit 进 .log (不只留注释),
# 形如 "作者 (年). 期刊, 卷(期), 页. https://doi.org/..."。仅引用注册表 status=match/minor
# 的条目, 绝不自创/猜测; 纯日志输出, golden-safe。
# ============================================================================
VERIFIED_REFS_FOR_LOG = (
    # 伪造检验范式 (核心方法论对标; PRisk/NPRisk 互补划分)
    ("伪造检验范式 (PRisk vs NPRisk 互补划分)",
     "Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). "
     "Firm-level political risk: Measurement and effects. The Quarterly "
     "Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021"),
    # nf_ln_coverage = log(1+count) 媒体关注度对数变换
    ("nf_ln_coverage = ln(1+count) 媒体关注度对数变换",
     "Fang, L., & Peress, J. (2009). Media coverage and the cross-section of "
     "stock returns. The Journal of Finance, 64(5), 2023-2052. "
     "https://doi.org/10.1111/j.1540-6261.2009.01493.x"),
    # 新闻量(volume) vs 情感内容(content) 概念区分 + |r| 区分效力诊断
    ("新闻量(volume) vs 情感内容(content) 概念区分 (诊断 |r|<0.3 支持 H1)",
     "Tetlock, P. C. (2007). Giving content to investor sentiment: The role "
     "of media in the stock market. The Journal of Finance, 62(3), 1139-1168. "
     "https://doi.org/10.1111/j.1540-6261.2007.01232.x"),
    # nf_media_breadth (不同媒体来源数) 作为信息环境指标
    ("nf_media_breadth (distinct-outlet 媒体广度) 信息中介依据",
     "Bushee, B. J., Core, J. E., Guay, W., & Hamm, S. J. W. (2010). The role "
     "of the business press as an information intermediary. Journal of "
     "Accounting Research, 48(1), 1-19. "
     "https://doi.org/10.1111/j.1475-679X.2009.00357.x"),
    # 伪造检验 = 现代 DiD 范式的互补划分 (anti-join 构造互斥处理/对照组 + placebo 时点检验)
    ("伪造检验 = DiD 范式互补划分 (anti-join 互斥处理/对照组; placebo 时点检验对标)",
     "Baker, A., Callaway, B., Cunningham, S., Goodman-Bacon, A., & Sant'Anna, "
     "P. H. C. (2026). Difference-in-differences designs: A practitioner's "
     "guide. Journal of Economic Literature, 64(2), 498–557. "
     "https://doi.org/10.1257/jel.20251650"),
    # 治理约束型合约控制变量 (GOV_* 列)
    ("治理约束型合约控制变量 (GOV_* 系列)",
     "Zhou, Y., Chen, L., Zhou, F., & Ye, M. (2026). Contractual arrangements "
     "and information consistency: How ESG executive compensation incentives "
     "affect corporate AI disclosure. Journal of Business Research, 207, "
     "116019. https://doi.org/10.1016/j.jbusres.2026.116019"),
    ("长期导向治理价值 (合约控制变量动机)",
     "Flammer, C., & Bansal, P. (2017). Does a long-term orientation create "
     "value? Evidence from a regression discontinuity. Strategic Management "
     "Journal, 38(9), 1827-1847. https://doi.org/10.1002/smj.2629"),
    ("高管激励合约结构 (GOV_equity_ratio / GOV_top3_pay_gap 依据)",
     "Edmans, A., Gabaix, X., & Landier, A. (2009). A multiplicative model of "
     "optimal CEO incentives in market equilibrium. The Review of Financial "
     "Studies, 22(12), 4881-4917. https://doi.org/10.1093/rfs/hhn117"),
    ("CSR/制度逻辑与分析师感知 (治理控制变量动机)",
     "Ioannou, I., & Serafeim, G. (2015). The impact of corporate social "
     "responsibility on investment recommendations: Analysts' perceptions and "
     "shifting institutional logics. Strategic Management Journal, 36(7), "
     "1053-1081. https://doi.org/10.1002/smj.2268"),
    ("所有权与控制权分离 (董事会独立性/双重身份控制变量)",
     "Fama, E. F., & Jensen, M. C. (1983). Separation of ownership and "
     "control. The Journal of Law and Economics, 26(2), 301-325. "
     "https://doi.org/10.1086/467037"),
)

# ============================================================================
# G-族诊断函数运行期引文 (逐字照抄 APA-7 + DOI; 仅日志用, golden-safe)
# 日志富集 2026-06-29 (Round 8): G-13/G-09 两个 G-族诊断函数原 banner 仅以短名
# (Author Year, Journal §x) 标注方法学锚点, 此处补 emit 完整 APA-7 + DOI, 让 .log
# 自证而非仅留注释 (镜像 pipeline/panel/geography.py::_GEO_REFERENCES 的 📖 习语)。
# 仅引用经核验注册表 (pool.json) 中 byte-identical 的 DOI, 绝不自创/猜测。
# ============================================================================
_G_RUNTIME_REFS = {
    # G-13 placebo-in-time DID: [ty-k, ty) 处理前窗口安慰剂检验 = 交错 DID 平行
    # 趋势 placebo 的正典操作化 (白话: 把政策时间往前挪 k 年再跑一遍, 真政策之前
    # 不该有效应; Callaway & Sant'Anna 2021 §4.3 pre-treatment placebo)。
    "callaway_santanna_did": (
        "Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-in-differences "
        "with multiple time periods. Journal of Econometrics, 225(2), 200-230. "
        "https://doi.org/10.1016/j.jeconom.2020.12.001"),
    # G-09 收敛有效性 (convergent validity): 把文本派生的金科分类测度与面板内部
    # 指标 (n_articles / LLM 情感 / 年度趋势) 互相关, 检验测度是否反映同一构念
    # (白话: 同一概念的多个测度应彼此一致; Gentzkow-Kelly-Taddy 2019 text-as-data
    # 测度有效性范式, 与本仓 geography.py per-dict IDF 引用同一锚点)。
    "gentzkow_text_as_data": (
        "Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of "
        "Economic Literature, 57(3), 535-574. "
        "https://doi.org/10.1257/jel.20181020"),
}


def _log_environment_and_config(df_full_path: str, art_path: str,
                                panel_path: str, output_path: str) -> None:
    """打印项目/环境信息 + 输入输出 + 运行配置 + 方法论引文 (日志富集 2026-06-24)。

    把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数、依据哪些文献"一次性
    落进 .log, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 (golden-safe)。
    所有非整数数字一律经 sig4/pct4 渲染为 4 位有效数字 (项目规范)。
    """
    try:
        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (伪造检验对照变量构建, STAGES_MAIN 主链末端)")
        logger.info("     · 项目: news_process 研究数据流水线 "
                    "(中文银行/金科新闻 → 计量面板); 版本 v3.15.0")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "本阶段纯 pandas/numpy, 无 LLM·Embedding·网络·API ($0), 逐位可复现")

        logger.info("  📂 输入 / 输出文件 (3-way fan-in; 任一缺失 → sys.exit(1))")
        logger.info(f"     · 输入(a) 全量银行新闻:   {df_full_path}")
        logger.info(f"     · 输入(b) 面板 fintech 文章: {art_path}")
        logger.info(f"     · 输入(c) Bank-Year 面板:  {panel_path}")
        logger.info(f"     · 输出   parquet:          {output_path}")
        logger.info(f"     · 输出   Stata .dta:       "
                    f"{os.path.splitext(output_path)[0] + '.dta'}")
        logger.info(f"     · 输出   诊断 CSV:         "
                    f"{os.path.join(OUTPUT_DIR, '51_falsification_diagnostics.csv')}")

        logger.info("  ⚙ 运行配置 (CONFIG['paths'] / CONFIG['filenames'])")
        logger.info(f"     · output_dir: {OUTPUT_DIR}")
        logger.info(f"     · log_dir:    {CONFIG['paths']['log_dir']}")
        logger.info("     · anti-join 复合键: (target_bank, 标题, 日期) 双侧 drop_duplicates")
        logger.info("     · 媒体广度口径: 物理(去重前)distinct-outlet (转载计入广度, Bushee 2010)")
        logger.info("     · 计数基: ft_n_articles_dedup 与 nf_n_articles 同基去重 (Hassan Table 7)")
        logger.info("     · fintech_share 分母0 语义: → NaN (zero_coverage 标记, 不冒充 0 份额)")
        logger.info("     · 区分效力诊断阈值: |r|<0.3 弱相关(支持 H1) / [0.3,0.7) 中等 / ≥0.7 高相关")
        logger.info("     · 挤出弹性阈值(三档, 与运行时分支一致): r(ln_ft,ln_nf)<-0.95 机械约束(坏) / -0.95≤r<-0.50 中等负相关(警告) / r≥-0.50 非机械关联(好)")
        logger.info("     · 假设框架: H0 解释力全来自一般媒体关注度 vs H1 含金融科技特异性增量信息")

        logger.info("  📖 方法论依据 (核心方法/构念学术出处, 经核验注册表逐字照抄)")
        for _tag, _ref in VERIFIED_REFS_FOR_LOG:
            logger.info(f"     · {_tag}:")
            logger.info(f"       {_ref}")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法论信息打印失败 (不影响处理): {e}")


# ============================================================================
# 2. 数据加载
# ============================================================================

def load_data():
    """加载三个输入文件。"""
    logger.info("=" * 70)
    logger.info("步骤 1: 数据加载")
    logger.info("=" * 70)
    logger.info("  说明: 加载三个数据文件,分别代表:")
    logger.info("    (a) 全量银行新闻 (含 fintech 和 non-fintech)")
    logger.info("    (b) 最终进入面板的 fintech 文章")
    logger.info("    (c) 已有的 Bank-Year 面板")

    # --- (a) 全量银行新闻 ---
    full_path = os.path.join(
        OUTPUT_DIR,
        FILENAMES.get('output_12_fintech_full', '12_fintech_news_full.parquet')
    )
    if not os.path.exists(full_path):
        logger.error(f"  ✗ 输入文件不存在: {full_path}")
        logger.error(f"  → 请先运行 12_news_fintech.py 生成此文件")
        sys.exit(1)
    df_full = pd.read_parquet(full_path)
    logger.info(f"  (a) 12_fintech_news_full: {len(df_full):,} 行")
    logger.info(f"      数据粒度: article × target_bank (每篇新闻×每个相关银行)")
    logger.info(f"      唯一银行数: {df_full['target_bank'].nunique()}")
    logger.info(f"      列数: {df_full.shape[1]}")
    logger.info(f"      日期列类型: {df_full['日期'].dtype}")

    # --- (b) 面板文章 ---
    art_path = os.path.join(
        OUTPUT_DIR,
        FILENAMES.get('output_40_article_bank', '40_article_bank_level.parquet')
    )
    if not os.path.exists(art_path):
        logger.error(f"  ✗ 输入文件不存在: {art_path}")
        logger.error(f"  → 请先运行 40_panel_export_main.py 生成此文件")
        sys.exit(1)
    df_art = pd.read_parquet(art_path)
    logger.info(f"  (b) 40_article_bank_level: {len(df_art):,} 行")
    logger.info(f"      说明: 这些是关键词匹配 + LLM 验证通过的金融科技新闻")
    logger.info(f"      唯一银行数: {df_art['target_bank'].nunique()}")
    logger.info(f"      日期列类型: {df_art['日期'].dtype}")
    # 对照组边界的 LLM 标注前提 (日志富集 round 7): df_art = LLM 语义验证通过的
    # 金融科技文章, 是 anti-join 的"被减项" → LLM 标注质量直接决定处理/对照组划界
    # (is_fintech_news=True 但 LLM 拒绝者刻意归入对照组, 见 build_non_fintech)。
    logger.info("      📖 对照组划界的 LLM 标注质量依据 "
                "(temperature=0 锁定 + _llm_cache.db 0-miss 复现锚):")
    logger.info("         · Carlson, N. A., & Burbano, V. (2026). The use of LLMs to "
                "annotate data in management research: Foundational guidelines and "
                "warnings. Strategic Management Journal, 47(3), 699–725. "
                "https://doi.org/10.1002/smj.70023")
    logger.info("         · Lin, H., & Zhang, Y. (2026). Navigating the risks of using "
                "large language models for text annotation in social science research. "
                "Social Science Computer Review, 44(3), 403–427. "
                "https://doi.org/10.1177/08944393251366243")

    # --- (c) 已有面板 ---
    panel_path = os.path.join(
        OUTPUT_DIR,
        FILENAMES.get('output_40_panel_yearly', '40_panel_yearly.parquet')
    )
    if not os.path.exists(panel_path):
        logger.error(f"  ✗ 输入文件不存在: {panel_path}")
        logger.error(f"  → 请先运行 40_panel_export_main.py 生成此文件")
        sys.exit(1)
    panel = pd.read_parquet(panel_path)
    logger.info(f"  (c) 40_panel_yearly: {len(panel):,} 行")
    logger.info(f"      数据粒度: Bank × Year (平衡面板)")
    logger.info(f"      唯一银行数: {panel['target_bank'].nunique()}")
    logger.info(f"      年份范围: {panel['year'].min()} - {panel['year'].max()}")

    return df_full, df_art, panel


# ============================================================================
# 3. 反连接 (anti-join): 定义非金融科技对照组
# ============================================================================

def build_non_fintech(df_full: pd.DataFrame,
                      df_art: pd.DataFrame) -> pd.DataFrame:
    """通过 anti-join 定义非金融科技对照组。

    逻辑: Non-Fintech = 全量银行新闻 MINUS 最终面板文章
    这确保 LLM 拒绝的文章 (keyword=True, llm_verified=False) 也归入对照组。

    对标学术依据:
      Hassan et al. (2019, QJE, Table 7):
      PRisk 和 NPRisk 通过对同一文本语料的互补划分构建,
      确保两组指标穷尽全部文本信息。
      本脚本中 Fintech tone + Non-fintech volume = 全量银行新闻,
      遵循同一穷举原则。

    白话: anti-join 就是"从全量银行新闻里减掉已进面板的金融科技新闻,
    剩下的全归对照组"。这样保证每篇新闻必属两组之一、不重不漏 —
    后面才能问"金融科技语调是不是真的比一般新闻量多解释了点什么"。
    """
    logger.info("=" * 70)
    logger.info("步骤 2: Anti-join 构建非金融科技对照组")
    logger.info("=" * 70)
    logger.info("  方法论说明:")
    logger.info("    学术依据: Hassan et al. (2019, QJE, 134(4), 2135-2202)")
    logger.info("    → Table 7 伪造检验: PRisk 与 NPRisk 对同一语料互补划分")
    logger.info("    本脚本等价操作: Fintech 面板文章 + Non-Fintech 对照组 = 全量银行新闻")
    logger.info("")
    logger.info("  数据处理说明:")
    logger.info("    关键技术细节: 40_article_bank_level 中 '日期' 列已被")
    logger.info("      pipeline/panel/encode.py parse_time() 转为 datetime64 类型,")
    logger.info("      而 12_fintech_news_full 中 '日期' 仍为原始 string 类型。")
    logger.info("      为避免类型不匹配导致 anti-join 静默失败,")
    logger.info("      统一转为 YYYY-MM-DD 格式字符串后再匹配。")

    # 防止修改调用方的原始 DataFrame (消除副作用)
    df_full = df_full.copy()
    df_art = df_art.copy()

    # 统一日期为标准化字符串 (避免 string vs datetime64 不匹配)
    df_full['_date_str'] = pd.to_datetime(
        df_full['日期'], errors='coerce'
    ).dt.strftime('%Y-%m-%d')
    df_art['_date_str'] = pd.to_datetime(
        df_art['日期'], errors='coerce'
    ).dt.strftime('%Y-%m-%d')

    # 检查日期转换中的 NaT
    full_nat = df_full['_date_str'].isna().sum()
    art_nat = df_art['_date_str'].isna().sum()
    if full_nat > 0:
        logger.warning(f"  12_fintech_news_full 中 {full_nat:,} 条日期解析为 NaT")
    if art_nat > 0:
        logger.warning(f"  40_article_bank_level 中 {art_nat:,} 条日期解析为 NaT")

    # 构建面板文章的复合键集合
    logger.info("")
    logger.info("  复合键组成: (target_bank, 标题, 日期)")
    logger.info("    说明: 两个文件均为 article × bank 粒度,")
    logger.info("          继承自 11_news_bank.py 的提早展开逻辑,")
    logger.info("          因此 (target_bank, 标题, 日期) 可作为可靠的匹配键。")

    # ── plan s2 修复: 集合 anti-join 在多重集场景下会破坏类划分 ──
    # 原始实现 `df_full[~_key.isin(panel_keys)]` 用 set 包装 df_art 的键,
    # 当同一 (target_bank, 标题, 日期) 在 df_art 出现多行时, df_full 中所有
    # 同键副本会被一律排除, 但 df_art 端只折叠为 1 行, 导致 panel + nf != total
    # 且互补划分被破坏。修复策略 (plan s2 方案 A): 双侧按复合键 drop_duplicates,
    # 显式约定"同 (target_bank, 标题, 日期) = 同一稿件"的集合语义, 报告被去重比例。
    _key_cols = ['target_bank', '标题', '_date_str']

    # 双侧去重诊断 (在 drop 之前) 与执行
    _df_art_before = len(df_art)
    df_art = df_art.drop_duplicates(subset=_key_cols, keep='first').copy()
    _df_art_dropped = _df_art_before - len(df_art)

    _df_full_before = len(df_full)
    # fix(omni-g-controls-02, 2026-06-11): 在复合键去重**之前**留物理行快照 (仅取
    # breadth 所需列, 控制内存) — nf_media_breadth (Bushee et al. 2010 JAR) 的构念
    # 是"多少家不同信息中介覆盖该银行", 跨媒体转载正是广度的体现; 复合键
    # (target_bank,标题,日期, 不含媒体列) keep='first' 会把同稿跨媒体副本折叠,
    # 系统性低估广度。nf_n_articles 的"同稿件"集合语义维持去重基不变。
    _media_col = '媒体(中文)'
    if _media_col in df_full.columns:
        _df_full_physical = df_full[
            ['target_bank', '标题', '_date_str', '日期', _media_col]
        ].copy()
    else:
        _df_full_physical = None
    df_full = df_full.drop_duplicates(subset=_key_cols, keep='first').copy()
    _df_full_dropped = _df_full_before - len(df_full)

    logger.info("")
    logger.info("  ─── 双侧 drop_duplicates(subset=复合键) 去重诊断 ───")
    logger.info(
        f"    40_article_bank_level: {_df_art_before:,} → {len(df_art):,} "
        f"(去重 {_df_art_dropped:,} 行, "
        f"{pct4(_df_art_dropped / max(_df_art_before, 1))})"
    )
    logger.info(
        f"    12_fintech_news_full:  {_df_full_before:,} → {len(df_full):,} "
        f"(去重 {_df_full_dropped:,} 行, "
        f"{pct4(_df_full_dropped / max(_df_full_before, 1))})"
    )
    # 去重影响对 Hassan PRisk/(PRisk+NPRisk) 互补划分的结构性诊断 (日志富集 round 7):
    # 两侧去重率若显著不同, 提示"同稿件"集合语义在处理/对照侧不对称 → 须警惕划分偏移。
    # 局部变量仅服务日志, 绝不回写 df / 任何产物 (golden-safe)。
    _art_dr = _df_art_dropped / max(_df_art_before, 1)
    _full_dr = _df_full_dropped / max(_df_full_before, 1)
    logger.info(
        f"    去重率口径对比: fintech 面板侧 {pct4(_art_dr)} vs 全量底库侧 {pct4(_full_dr)} "
        f"(差 {sig4(_art_dr - _full_dr)}); 两侧同按 (target_bank,标题,日期) 折叠'同稿件', "
        f"口径对称 → 不破坏互斥处理/对照组划分。"
    )
    if _df_art_dropped > 0 or _df_full_dropped > 0:
        logger.info(
            "    说明: 同 (target_bank, 标题, 日期) 视为同一稿件 (集合语义)。"
            "如需多重集差集 (按行级配对), 见 plan s2 方案 B/C。"
        )

    # 反连接 (anti-join, 集合差集)
    panel_keys = set(zip(
        df_art['target_bank'],
        df_art['标题'],
        df_art['_date_str']
    ))
    logger.info(f"  面板文章唯一键数 (= 行数): {len(panel_keys):,}")
    # 用显式 raise 替代 assert (assert 在 ``python -O`` 模式下被禁用),
    # 这是 drop_duplicates 之后必然成立的不变量; 一旦失败说明 pandas 行为
    # 异常或上游数据存在不可序列化的复合 NaN 类型, 必须立即停下排查。
    if len(panel_keys) != len(df_art):
        raise RuntimeError(
            f"drop_duplicates 后 panel_keys ({len(panel_keys):,}) 与 "
            f"df_art ({len(df_art):,}) 行数不一致, 数据异常 — 可能是 "
            f"_date_str 中存在不同 NaT 实例或 pandas 行为异常"
        )

    df_full['_key'] = list(zip(
        df_full['target_bank'],
        df_full['标题'],
        df_full['_date_str']
    ))
    df_nf = df_full[~df_full['_key'].isin(panel_keys)].copy()
    df_nf.drop(columns=['_key', '_date_str'], inplace=True)
    df_full.drop(columns=['_key', '_date_str'], inplace=True)

    # fix(omni-g-controls-02, 2026-06-11): 物理 (去重前) NF 行集 = 物理 df_full 对
    # 去重后 df_art 键集的 anti-join (anti-join 不要求先物理去重 df_full); 在其上
    # 按 bank-year 计算 distinct-outlet 媒体广度, 经 attrs 暴露给
    # aggregate_non_fintech 替代去重基 nunique (Bushee 2010 JAR: 转载属于广度)。
    if _df_full_physical is not None:
        _phys_key = pd.Series(
            list(zip(_df_full_physical['target_bank'],
                     _df_full_physical['标题'],
                     _df_full_physical['_date_str'])),
            index=_df_full_physical.index,
        )
        _nf_phys = _df_full_physical.loc[~_phys_key.isin(panel_keys)].copy()
        _nf_phys['_year'] = pd.to_datetime(_nf_phys['日期'], errors='coerce').dt.year
        _nf_phys = _nf_phys.dropna(subset=['_year'])
        if len(_nf_phys) > 0:
            _nf_phys['_year'] = _nf_phys['_year'].astype(int)
            _breadth_phys = (
                _nf_phys.groupby(['target_bank', '_year'])[_media_col]
                .nunique().reset_index()
            )
            _breadth_phys.columns = ['target_bank', 'year', 'nf_media_breadth']
        else:
            _breadth_phys = pd.DataFrame({
                'target_bank': pd.Series(dtype=object),
                'year': pd.Series(dtype='int64'),
                'nf_media_breadth': pd.Series(dtype='int64'),
            })
        df_nf.attrs['nf_media_breadth_physical'] = _breadth_phys
        logger.info(
            f"  nf_media_breadth 物理口径聚合 (去重前行集, 含跨媒体转载): "
            f"{len(_breadth_phys):,} bank-year [fix omni-g-controls-02]"
        )

    # --- 三分类校验与详细统计 ---
    n_total = len(df_full)  # 已去重
    n_panel = len(df_art)   # 已去重
    n_nf = len(df_nf)
    logger.info("")
    logger.info("  ─── 三分类统计 (基于双侧去重后的口径) ───")
    logger.info(f"    ③ Fintech 面板文章 (keyword=True + LLM通过): {n_panel:,} 条")
    logger.info(f"    ①+② Non-Fintech 对照组:                     {n_nf:,} 条")
    logger.info(f"    全量银行新闻:                                 {n_total:,} 条")
    logger.info(f"    恒等校验: {n_panel:,} + {n_nf:,} = {n_panel + n_nf:,} "
                f"{'== ✓' if n_panel + n_nf == n_total else '!= ✗'} {n_total:,}")
    logger.info(f"    Fintech 占比: {pct4(n_panel / max(n_total, 1))}")
    logger.info(f"    Non-Fintech 占比: {pct4(n_nf / max(n_total, 1))}")

    if n_panel + n_nf != n_total:
        # 双侧 drop_duplicates 后理论上必有 panel + nf == total; 仍不等说明
        # df_art 中存在 (target_bank, 标题, 日期) 落在 df_full 之外的"幽灵键"
        diff = n_panel + n_nf - n_total
        logger.warning(f"  去重后三分类不等式仍不成立! panel+nf-total = {diff:,} 条。")
        logger.warning("     可能原因: df_art 中存在 df_full 未覆盖的 (target_bank, 标题, 日期) 组合,")
        logger.warning("              即上游 ETL 漏抓部分稿件; 请检查 12 与 40 的覆盖一致性。")
        logger.warning(f"     影响评估: 差异量占总量 {pct4(abs(diff) / max(n_total, 1))}, 通常可忽略。")

    # 子分类统计 (区分 ① 和 ②)
    if 'is_fintech_news' in df_nf.columns:
        n_kw_false = (df_nf['is_fintech_news'] == False).sum()
        n_kw_true_llm_reject = (df_nf['is_fintech_news'] == True).sum()
        logger.info("")
        logger.info("  ─── Non-Fintech 子分类 ───")
        logger.info(f"    ① 关键词未匹配 (is_fintech_news=False):  {n_kw_false:,} 条 "
                     f"({pct4(n_kw_false / max(n_nf, 1))})")
        logger.info(f"    ② 关键词匹配但 LLM 拒绝:                  {n_kw_true_llm_reject:,} 条 "
                     f"({pct4(n_kw_true_llm_reject / max(n_nf, 1))})")
        logger.info(f"    说明: ①是完全不涉及金融科技的银行新闻,")
        logger.info(f"          ②是规则预筛通过但经 LLM 语义验证后被认定为非金融科技的新闻。")
        logger.info(f"          两者合并构成伪造检验的对照组。")

    # fix(fintech-share-counting-basis, metric-audit 2026-06-10): 计算**去重口径**的
    # fintech bank-year 篇数 (与 nf_n_articles 同基), 供 merge_to_panel 作 fintech_share
    # 分子 —— 替代面板物理 n_articles (无复合键去重), 消除分子(物理)/分母 NF(去重)计数基
    # 不一致 (Hassan 2019 QJE Table 7 要求 PRisk/(PRisk+NPRisk) 同一计数域)。df_art 此处
    # 已按 (target_bank,标题,_date_str) 去重 (line 339), 故 groupby size = 去重 fintech 篇数。
    if 'year' in df_art.columns:
        ft_dedup_agg = (df_art.groupby(['target_bank', 'year']).size()
                        .reset_index(name='ft_n_articles_dedup'))
        df_nf.attrs['ft_dedup_agg'] = ft_dedup_agg
        logger.info(f"  ft_n_articles_dedup (去重 fintech 篇数, fintech_share 分子): "
                    f"{int(ft_dedup_agg['ft_n_articles_dedup'].sum()):,} 条 / "
                    f"{len(ft_dedup_agg):,} bank-year")

    return df_nf


# ============================================================================
# 4. 非金融科技 Bank–Year 聚合
# ============================================================================

def aggregate_non_fintech(df_nf: pd.DataFrame) -> pd.DataFrame:
    """按 (target_bank, year) 聚合非金融科技对照变量。

    生成变量及学术依据:
      nf_n_articles    — 非金融科技新闻篇数 (去重基"同稿件"集合语义)
      nf_ln_coverage   — log(1 + count), Fang & Peress (2009, JF, 64(5), 2023-2052)
      nf_media_breadth — 不同媒体来源数, Bushee et al. (2010, JAR, 48(1), 1-19);
                         fix(omni-g-controls-02, 2026-06-11): 改在物理 (去重前)
                         NF 行集上 nunique (转载属于广度), 经
                         df_nf.attrs['nf_media_breadth_physical'] 注入;
                         attrs 缺失时回退去重基 nunique (已知低估, 仅兼容直调)
      nf_headline_frac — 平均标题提及率 (目标银行在标题中出现的比例)

    技术注意:
      - 12_fintech_news_full 中列名为 target_bank_in_title (非 in_title)
      - 媒体列名为 '媒体(中文)' (含中文括号)
    """
    logger.info("=" * 70)
    logger.info("步骤 3: Non-Fintech Bank-Year 聚合")
    logger.info("=" * 70)
    logger.info("  说明: 将文章级 non-fintech 新闻聚合为 Bank-Year 级别的对照变量。")
    logger.info("")
    logger.info("  ─── 变量定义与学术依据 ───")
    logger.info(f"  [1] nf_n_articles: 非金融科技新闻篇数 (原始计数)")
    logger.info(f"")
    logger.info(f"  [2] nf_ln_coverage = ln(1 + nf_n_articles)")
    logger.info(f"      学术依据: {REFERENCES['Fang2009']}")
    logger.info(f"      说明: Fang & Peress (2009) 使用 ln(1+媒体报道数) 作为")
    logger.info(f"            媒体关注度的连续变量,对数变换缓解右偏分布问题。")
    logger.info(f"")
    logger.info(f"  [3] nf_media_breadth: 不同媒体来源数 (nunique, 物理/去重前口径)")
    logger.info(f"      学术依据: {REFERENCES['Bushee2010']}")
    logger.info(f"      说明: Bushee et al. (2010) 指出信息中介的多样性")
    logger.info(f"            (媒体广度) 影响信息扩散效率,")
    logger.info(f"            不同媒体来源数量反映信息环境的丰富程度。")
    logger.info(f"")
    logger.info(f"  [4] nf_headline_frac: 标题提及率 = mean(target_bank_in_title)")
    logger.info(f"      说明: 目标银行出现在新闻标题中的比例,")
    logger.info(f"            标题提及通常意味着更高的新闻显著性和读者关注度。")

    # fix(omni-g-controls-02, 2026-06-11): 在 df_nf 被 copy/过滤前先取
    # build_non_fintech 暴露的物理 (去重前) 口径媒体广度聚合。
    _breadth_physical = df_nf.attrs.get('nf_media_breadth_physical')

    # 处理空输入
    if len(df_nf) == 0:
        logger.warning("  Non-Fintech 组为空, 将返回空聚合结果")
        return pd.DataFrame(columns=[
            'target_bank', 'year', 'nf_n_articles', 'nf_ln_coverage',
            'nf_media_breadth', 'nf_headline_frac'
        ])

    # 防止修改调用方的原始 DataFrame (消除副作用)
    df_nf = df_nf.copy()

    # 解析年份
    logger.info("")
    logger.info("  ─── 年份解析 ───")
    df_nf['_year'] = pd.to_datetime(df_nf['日期'], errors='coerce').dt.year
    before_drop = len(df_nf)
    df_nf = df_nf.dropna(subset=['_year']).copy()
    df_nf['_year'] = df_nf['_year'].astype(int)
    after_drop = len(df_nf)
    dropped = before_drop - after_drop
    if dropped > 0:
        logger.warning(f"  丢弃 {dropped:,} 条无效日期记录 "
                        f"({pct4(dropped / max(before_drop, 1))})")
    logger.info(f"  有效记录: {after_drop:,} 条")

    # 聚合
    logger.info("")
    logger.info("  ─── 执行聚合 ───")

    # 媒体广度列名确认
    media_col = '媒体(中文)'
    has_media = media_col in df_nf.columns
    logger.info(f"  媒体列 '{media_col}' {'✓ 存在' if has_media else '✗ 不存在'}")

    # 标题提及率列名确认 (注意: 是 target_bank_in_title, 不是 in_title)
    headline_col = 'target_bank_in_title'
    has_headline = headline_col in df_nf.columns
    logger.info(f"  标题提及列 '{headline_col}' {'✓ 存在' if has_headline else '✗ 不存在'}")
    if has_headline:
        logger.info(f"    技术备注: 列名是 '{headline_col}' (来自 11_news_bank.py),")
        logger.info(f"       而非 'in_title' (40_panel_export_main.py main() 中的重命名版本)")

    nf_agg = df_nf.groupby(['target_bank', '_year']).agg(
        nf_n_articles=('target_bank', 'count'),
    ).reset_index()
    nf_agg.rename(columns={'_year': 'year'}, inplace=True)

    # 媒体广度 (需要单独 nunique)
    if _breadth_physical is not None:
        # fix(omni-g-controls-02, 2026-06-11): 用物理 (去重前) NF 行集的
        # distinct-outlet 计数 — 转载属于广度 (Bushee 2010 JAR 构念); 去重基
        # nunique (复合键不含媒体列, keep='first') 会折叠同稿跨媒体副本,
        # 系统性低估广度且与新闻显著性相关 (非经典测量误差)。
        nf_agg = nf_agg.merge(_breadth_physical, on=['target_bank', 'year'],
                              how='left')
        nf_agg['nf_media_breadth'] = nf_agg['nf_media_breadth'].fillna(0).astype(int)
        logger.info("  nf_media_breadth: 物理 (去重前) 行集口径 "
                    "[fix omni-g-controls-02]")
    elif has_media:
        # legacy 去重基 fallback (直接调用本函数、无 attrs 注入时):
        # 已知会折叠跨媒体转载、低估广度, 仅为向后兼容保留。
        media_breadth = df_nf.groupby(
            ['target_bank', '_year']
        )[media_col].nunique().reset_index()
        media_breadth.columns = ['target_bank', 'year', 'nf_media_breadth']
        nf_agg = nf_agg.merge(media_breadth, on=['target_bank', 'year'], how='left')
        logger.warning("  nf_media_breadth: 去重基 fallback (物理口径 attrs 缺失) — "
                       "跨媒体转载被折叠, 广度可能低估")
    else:
        logger.warning(f"  列 '{media_col}' 不存在, nf_media_breadth 将为 0")
        nf_agg['nf_media_breadth'] = 0

    # 标题提及率
    if has_headline:
        headline_frac = df_nf.groupby(
            ['target_bank', '_year']
        )[headline_col].mean().reset_index()
        headline_frac.columns = ['target_bank', 'year', 'nf_headline_frac']
        nf_agg = nf_agg.merge(headline_frac, on=['target_bank', 'year'], how='left')
    else:
        # fix(nf-headline-frac-ratio-nan, 2026-06-25): nf_headline_frac 是比率 (二元
        # target_bank_in_title 的组内均值), 标题列缺失时其值未定义 → NaN (非 0); 填 0
        # 会被回归/相关诊断当作"标题提及率真为 0"误读 (Allison 2001 / Heckman 1979)。
        logger.warning(f"  列 '{headline_col}' 不存在, nf_headline_frac 将为 NaN (比率未定义)")
        nf_agg['nf_headline_frac'] = np.nan

    # 对数覆盖量 [Fang & Peress 2009]
    nf_agg['nf_ln_coverage'] = np.log1p(nf_agg['nf_n_articles'])

    # --- 描述性统计 ---
    logger.info("")
    logger.info("  ─── 聚合结果描述性统计 ───")
    logger.info(f"  聚合后行数 (Bank-Year): {len(nf_agg):,}")
    logger.info(f"  唯一银行数: {nf_agg['target_bank'].nunique()}")
    logger.info(f"  年份范围: {nf_agg['year'].min()} - {nf_agg['year'].max()}")
    logger.info(f"  nf_n_articles:    mean={sig4(nf_agg['nf_n_articles'].mean())}, "
                f"median={sig4(nf_agg['nf_n_articles'].median())}, "
                f"std={sig4(nf_agg['nf_n_articles'].std())}, "
                f"min={int(nf_agg['nf_n_articles'].min()):,}, "
                f"max={int(nf_agg['nf_n_articles'].max()):,}")
    logger.info(f"  nf_ln_coverage:   mean={sig4(nf_agg['nf_ln_coverage'].mean())}, "
                f"median={sig4(nf_agg['nf_ln_coverage'].median())}")
    logger.info(f"  nf_media_breadth: mean={sig4(nf_agg['nf_media_breadth'].mean())}, "
                f"median={sig4(nf_agg['nf_media_breadth'].median())}")
    logger.info(f"  nf_headline_frac: mean={sig4(nf_agg['nf_headline_frac'].mean())}, "
                f"median={sig4(nf_agg['nf_headline_frac'].median())}")

    return nf_agg


# ============================================================================
# 5. 合并到面板 + 总量变量 + 校验
# ============================================================================

def merge_to_panel(panel: pd.DataFrame,
                   nf_agg: pd.DataFrame,
                   ft_dedup_agg: pd.DataFrame | None = None) -> pd.DataFrame:
    """将非金融科技对照变量合并到面板, 构造总量变量。

    总量变量学术依据 (fix(omni-g-controls-03/05/07, 2026-06-11) 计数基统一 + 份额
    缺失语义):
      all_n_articles  = ft_n_articles_dedup + nf_n_articles (穷举, 去重同基;
                        ft_dedup_agg=None 时回退 n_articles(物理) + nf(去重) 的
                        **混合基**, 仅向后兼容旧调用/测试, 注释如实不再称物理覆盖)
      all_ln_coverage = log(1 + all_n_articles), Fang & Peress (2009)
      fintech_share   = ft_n_articles_dedup / (ft_n_articles_dedup + nf_n_articles)
                        (fix 2026-06-10: 分子去重口径与分母同基; fix omni-g-controls-05:
                         分母 0 → NaN, 未定义份额不再与真实 0 份额同值混淆)
      zero_coverage   = 1{all_n_articles == 0} (零新闻指示, 标记 fintech_share 无定义行)
      ln_ft_articles / ln_nf_articles — 挤出弹性对, 两端同基 (去重可用时均去重)

    对标 Hassan et al. (2019) Table 7:
      all_ln_coverage 类似于 Risk_it (总体风险暴露),
      fintech tone 类似于 PRisk_it (特异性风险暴露)。

    白话: "计数基统一"是说算份额时分子分母必须用同一把尺子数新闻 —
    分子若数的是物理行 (同一篇稿被多家媒体转载算多篇)、分母却按
    "同稿件只算一篇"去重, 份额就会系统性偏大。fintech_share 在全年
    零新闻时是 0/0, 数学上没意义, 所以记 NaN 让回归自动剔除,
    而不是填 0 冒充"有新闻但都不是金融科技"。
    """
    logger.info("=" * 70)
    logger.info("步骤 4: 合并到面板 + 总量变量")
    logger.info("=" * 70)
    logger.info("  说明: 将步骤3的对照变量通过 left join 合并到已有面板,")
    logger.info("        并构建总量指标用于赛马回归检验。")

    panel_before_cols = set(panel.columns)

    # Left join
    panel = panel.merge(nf_agg, on=['target_bank', 'year'], how='left')
    logger.info(f"  合并方式: left join on (target_bank, year)")

    # 缺失填充为 0 (与 pipeline/panel/encode.py balance_panel 的零新闻逻辑一致): 仅
    # 计数 / 对数覆盖量 / 媒体广度等"流量类"列在零 NF 新闻行填 0 (无新闻 = 0 篇 / 0 家
    # 媒体, 语义正确)。
    # fix(nf-headline-frac-ratio-nan, 2026-06-25): nf_headline_frac 是【比率】
    # (mean(target_bank_in_title)), 零 NF 新闻行上为 0/0 未定义, 必须保 NaN — 与
    # balance_panel 让所有 *_frac 比率列零新闻行保 NaN 的契约一致 (此前误填 0, 致 51
    # 个零-NF bank-year 的 nf_headline_frac 伪 0, 污染 run_diagnostics 相关系数; F3
    # 红线: 零报道 ≠ 零比率, Allison 2001 / Heckman 1979)。故移出 fill_cols, 零 NF 行
    # 随 left join 自然保留 NaN。
    fill_cols = ['nf_n_articles', 'nf_ln_coverage', 'nf_media_breadth']
    filled_count = 0
    for c in fill_cols:
        if c in panel.columns:
            na_count = panel[c].isna().sum()
            filled_count += na_count
            panel[c] = panel[c].fillna(0)
    logger.info(f"  NaN 填充: {filled_count:,} 个单元格填为 0")
    logger.info(f"    说明: 某些 Bank-Year 在非金融科技组中没有新闻报道,")
    logger.info(f"          与 pipeline/panel/encode.py balance_panel 的零新闻处理一致。")

    # --- 总量变量 ---
    logger.info("")
    logger.info("  ─── 总量变量构建 ───")
    # fix(omni-g-controls-03/07, 2026-06-11): 计数基统一 (counting-basis unification)。
    # 2026-06-10 修复仅改了 fintech_share 分子分母, all_n_articles / ln_ft_articles
    # 仍是 fintech 物理 + NF 去重的混合基, 且旧注释误把 NF 侧称作"物理覆盖" (NF 侧
    # 实经 build_non_fintech 复合键去重)。现统一: ft_dedup_agg 可用 → 总量/份额/
    # 弹性对全部用去重基 (ft_n_articles_dedup 与 nf_n_articles 同按
    # (target_bank,标题,日期) 去重); 不可用 → 回退 fintech 物理 n_articles + NF
    # 去重的**混合基** (仅向后兼容旧调用/测试, 如实披露, 不再谎称物理覆盖)。
    _has_dedup = (ft_dedup_agg is not None
                  and 'ft_n_articles_dedup' in ft_dedup_agg.columns)
    if _has_dedup:
        panel = panel.drop(columns=['ft_n_articles_dedup'], errors='ignore')
        panel = panel.merge(ft_dedup_agg, on=['target_bank', 'year'], how='left')
        panel['ft_n_articles_dedup'] = panel['ft_n_articles_dedup'].fillna(0)
        _ft_count = panel['ft_n_articles_dedup']
        logger.info("  计数基: 去重同基 (fintech=ft_n_articles_dedup, "
                    "NF=nf_n_articles) [fix omni-g-controls-03/07]")
    else:
        _ft_count = panel['n_articles']
        logger.warning("  ft_dedup_agg 缺失 → all_n_articles/ln_ft_articles 回退"
                       "混合基 (fintech 物理 + NF 去重), 仅限旧调用兼容")

    panel['all_n_articles'] = _ft_count + panel['nf_n_articles']
    logger.info("  all_n_articles = fintech 计数 + nf_n_articles (同基相加)")

    panel['all_ln_coverage'] = np.log1p(panel['all_n_articles'])
    logger.info(f"  all_ln_coverage = ln(1 + all_n_articles)")
    logger.info(f"    依据: Fang & Peress (2009, JF, 64(5), 2023-2052)")

    # fix(fintech-share-counting-basis, metric-audit 2026-06-10): 分子用**去重口径**
    # ft_n_articles_dedup (与分母 NF 同基), 消除分子(物理)/分母(去重)计数基不一致
    # (Hassan 2019 QJE Table 7 要求 PRisk/(PRisk+NPRisk) 同一计数域)。
    # 数据来源澄清 (2026-06-13): 分母"全部银行新闻"不读单一文件, 而是
    # fintech(40_article_bank_level.parquet 去重) + NF(12_fintech_news_full.parquet
    # 过滤前全量银行新闻 anti-join 减去面板文章后去重) 两块同基相加 —
    # 即"全量底库" = 12_fintech_news_full.parquet (与 11_bank_news 行集 1:1,
    # 详见模块 docstring「命名澄清」段, 勿因文件名 "fintech" 误判)。
    # fix(omni-g-controls-05, 2026-06-11): 分母为 0 (该 bank-year 全年零新闻, 份额
    # 无定义) → NaN (回归自然剔除), 不再填 0 与"有新闻但全为非金融科技"的真实
    # 0 份额同值混淆; 配套 zero_coverage 指示列供使用者条件化/诊断。
    panel['zero_coverage'] = (panel['all_n_articles'] == 0).astype(int)
    panel['fintech_share'] = np.where(
        panel['all_n_articles'] > 0,
        _ft_count / panel['all_n_articles'],
        np.nan,
    )
    if _has_dedup:
        logger.info("  fintech_share = ft_n_articles_dedup / (ft_dedup + nf_n_articles) "
                    "[去重同基口径, fix 2026-06-10; 分母0→NaN, fix omni-g-controls-05]")
    else:
        logger.warning("  fintech_share 回退物理分子口径 (ft_dedup_agg 缺失; "
                       "分母0→NaN 同样生效)")
    logger.info("  zero_coverage = 1{all_n_articles == 0} "
                "(fintech_share 无定义指示, fix omni-g-controls-05)")
    logger.info(f"    学术意义: 金融科技新闻在全部银行新闻中的信息密集度,")
    logger.info(f"              类似 Hassan (2019) PRisk / (PRisk + NPRisk)。")

    # --- 挤出效应弹性变量 (避免百分比回归机械 β=-1) ---
    # fix(omni-g-controls-03, 2026-06-11): ln_ft 与 ln_nf 两端同基 (去重可用时均
    # 去重) — 弹性回归 ln(nf) ~ ln(ft) 与 run_diagnostics 的 r(ln_ft, ln_nf)
    # 校验不再两端口径不同。
    panel['ln_ft_articles'] = np.log1p(_ft_count)
    panel['ln_nf_articles'] = np.log1p(panel['nf_n_articles'])
    logger.info(f"  ln_ft_articles  = ln(1 + fintech 计数"
                f"{'[去重]' if _has_dedup else '[物理, 回退]'})")
    logger.info(f"  ln_nf_articles  = ln(1 + nf_n_articles)")
    logger.info(f"    依据: 对数弹性 ln(nf) ~ ln(ft) 避免 fintech% + nf% ≡ 100% 约束")

    # --- 跨源一致性校验 ---
    # fix(omni-g-controls-04, 2026-06-11): 旧"恒等式校验" (all == n_articles + nf)
    # 是把上面刚算出的和与同一表达式再比一次的同义反复 (tautology), 永不可能检出
    # 数据不一致, 却在日志中呈现为数据一致性闸门 (虚假验证保证; 真正有信息量的
    # 文章级恒等式在 build_non_fintech 三分类校验已存在)。改为有信息量的跨源
    # 不变量: 去重 fintech 计数 (源自 40_article_bank_level 复合键去重聚合) 必须
    # 逐行 ≤ 面板物理计数 n_articles (源自 stage 45 聚合) — 违反即 merge 键错位
    # 或上游计数源分叉。
    logger.info("")
    logger.info("  ─── 跨源一致性校验 (fix omni-g-controls-04) ───")
    if _has_dedup:
        _viol = panel['ft_n_articles_dedup'] > panel['n_articles']
        if _viol.any():
            logger.error(f"  ✗ 跨源校验失败: {int(_viol.sum())} 行去重 fintech 计数 > "
                         f"物理 n_articles — merge 键错位或上游计数源分叉, "
                         f"请检查 40_article_bank_level 与 40_panel_yearly 一致性!")
            # fix(controls-cross-source-fail-loud, 2026-06-25): 该不变量 (去重 fintech
            # 计数 ≤ 物理 n_articles) 是复合键去重后构造性恒真的硬契约, 违反必为
            # 40_article_bank_level 与 40_panel_yearly 计数源分叉 / merge 键错位的数据
            # 损坏。此前仅 logger.error 后 return panel → 退出码 0 → orchestrator 判成功
            # → 错位面板静默流入 11 篇 falsification 回归。改为与同模块 anti-join (L538)
            # 及 .dta 导出 (L1227) 的完整性闸门一致, 在写盘 (export_results) 前 fail-loud
            # raise (golden-safe: 生产正常时 _viol 全 False, 本分支永不进入, 不改写出列)。
            raise RuntimeError(
                f"跨源一致性校验失败: {int(_viol.sum())} 行 ft_n_articles_dedup > "
                f"n_articles — 构造性不可能的不变量被违反, 40_article_bank_level 与 "
                f"40_panel_yearly 计数源分叉或 (target_bank, year) merge 键错位, "
                f"必须排查上游后重建面板 (拒绝写出错位 falsification 面板)"
            )
        else:
            _shrink = float((panel['n_articles'] - panel['ft_n_articles_dedup']).sum())
            logger.info(f"  ✓ 去重计数 ≤ 物理计数 逐行成立 ({len(panel):,} 行); "
                        f"复合键去重收缩合计 {int(round(_shrink)):,} 篇")
    else:
        logger.info("  (跳过: ft_dedup_agg 缺失, 无跨源可比计数)")

    # --- 变量名冲突检查 ---
    new_cols = set(panel.columns) - panel_before_cols
    conflict_cols = new_cols & panel_before_cols
    if conflict_cols:
        logger.warning(f"  变量名冲突 (已覆盖原面板列): {conflict_cols}")
    else:
        logger.info(f"  变量名冲突检查: ✓ 无冲突 (所有新变量使用 nf_/all_/fintech_ 前缀)")

    # --- 描述性统计 ---
    logger.info("")
    logger.info("  ─── 合并后描述性统计 ───")
    logger.info(f"  面板行数: {len(panel):,}")
    logger.info(f"  新增列: {sorted(new_cols)}")
    logger.info(f"  fintech_share: mean={sig4(panel['fintech_share'].mean())}, "
                f"median={sig4(panel['fintech_share'].median())}, "
                f"p25={sig4(panel['fintech_share'].quantile(0.25))}, "
                f"p75={sig4(panel['fintech_share'].quantile(0.75))}")

    zero_all = (panel['all_n_articles'] == 0).sum()
    zero_ft = (panel['n_articles'] == 0).sum()
    zero_nf = (panel['nf_n_articles'] == 0).sum()
    logger.info(f"  零新闻行: 全部={zero_all:,}, fintech={zero_ft:,}, non-fintech={zero_nf:,}")

    return panel


# ============================================================================
# 6. 诊断报告: 相关矩阵
# ============================================================================

def run_diagnostics(panel: pd.DataFrame):
    """输出 Pearson/Spearman 相关矩阵与自动解读。

    诊断目的 (Hassan 2019 方法论):
      相关矩阵帮助判断 fintech tone 与 non-fintech coverage 之间的线性关联程度。
      如果两者高度相关 (|r| > 0.7), 则伪造检验的区分效力可能减弱。
      理想情况下 |r| < 0.3, 表明两组指标捕获了不同的信息维度。

    同时参考 Tetlock (2007, JF, 62(3), 1139-1168):
      新闻量 (volume) 和情感内容 (content) 是两个概念上独立的维度,
      volume 衡量关注度, content 衡量正/负面倾向。
    """
    logger.info("=" * 70)
    logger.info("步骤 5: 诊断报告 — 相关矩阵")
    logger.info("=" * 70)
    logger.info("  目的: 检验 fintech 情感指标与 non-fintech 新闻量之间的相关性。")
    logger.info("  理论基础:")
    logger.info(f"    {REFERENCES['Tetlock2007']}")
    logger.info(f"    → Tetlock (2007) 指出新闻 volume 和 content 是独立维度。")
    logger.info(f"    → 如果 |r(tone, nf_coverage)| 较低, 支持 H1。")

    # 选取核心变量 (情感 LLM 三轨 full/ctx/ss; ss=银行+金科同句共现, 缺列优雅跳过)
    diag_cols = []
    for c in ['llm_vote_tone_full', 'llm_vote_tone_ctx', 'llm_vote_tone_ss',
              'dict_avg_tone_full', 'bert_avg_pos_full']:
        if c in panel.columns:
            diag_cols.append(c)
    for c in ['nf_ln_coverage', 'nf_media_breadth', 'nf_headline_frac']:
        if c in panel.columns:
            diag_cols.append(c)
    for c in ['all_ln_coverage', 'fintech_share', 'n_articles']:
        if c in panel.columns:
            diag_cols.append(c)

    if len(diag_cols) < 2:
        logger.warning("  可用诊断列不足, 跳过相关矩阵")
        return None

    # 仅保留有新闻的行
    mask = panel['all_n_articles'] > 0
    # 披露 (fix nf-headline-frac-ratio-nan, 2026-06-25): diag_cols 含比率列
    # nf_headline_frac, 其在【有新闻但零 NF 新闻】(all_n_articles>0 ∧ nf_n_articles==0)
    # 的行上为 NaN (本次修复将其由伪 0 改回"未定义")。此处沿用 listwise dropna
    # (complete-case), 故这些行会从【整张】相关矩阵 (含与 nf_headline_frac 无关的
    # tone×nf_coverage 对) 一并剔除 → 有效 N 略缩。这是诊断层 (log +
    # 51_falsification_diagnostics.csv) 的【预期副作用】, 非数据错误 (诊断本就只取
    # complete-case 行); 主回归不消费 nf_headline_frac, 系数不受影响。若需为 nf_coverage
    # 对保留更多观测, 可改 pairwise (.corr 原生按对处理 NaN, 无需 dropna)。
    diag_df = panel.loc[mask, diag_cols].dropna()

    logger.info(f"")
    logger.info(f"  用于相关分析的有效观测数: {len(diag_df):,}")
    logger.info(f"  排除的零新闻行: {(~mask).sum():,}")
    logger.info(f"  分析变量: {diag_cols}")

    # Pearson
    pearson = diag_df.corr(method='pearson')
    logger.info("")
    logger.info("  ─── Pearson 相关矩阵 (线性相关) ───")
    for line in pearson.to_string().split('\n'):
        logger.info(f"  {line}")

    # Spearman
    spearman = diag_df.corr(method='spearman')
    logger.info("")
    logger.info("  ─── Spearman 相关矩阵 (秩相关) ───")
    for line in spearman.to_string().split('\n'):
        logger.info(f"  {line}")

    # 自动解读
    logger.info("")
    logger.info("  ─── 自动解读 (基于 Pearson 系数) ───")
    for c in ['nf_ln_coverage', 'nf_media_breadth']:
        if c not in pearson.columns:
            continue
        # 情感 LLM 三轨 full/ctx/ss (ss=银行+金科同句共现) + 词典 full; 缺列优雅跳过
        for tone_col in ['llm_vote_tone_full', 'llm_vote_tone_ctx',
                         'llm_vote_tone_ss', 'dict_avg_tone_full']:
            if tone_col not in pearson.columns:
                continue
            r = pearson.loc[tone_col, c]
            r_abs = abs(r)
            if r_abs < 0.3:
                logger.info(f"  ✅ r({tone_col}, {c}) = {sig4(r)}")
                logger.info(f"     |r| = {sig4(r_abs)} < 0.30 → 弱相关")
                logger.info(f"     解读: 金融科技情感与非金融科技新闻量相对独立,")
                logger.info(f"           支持 H1 (fintech tone 具有特异性信息)。")
            elif r_abs < 0.7:
                logger.info(f"  ℹ️  r({tone_col}, {c}) = {sig4(r)}")
                logger.info(f"     |r| = {sig4(r_abs)} ∈ [0.30, 0.70) → 中等相关")
                logger.info(f"     解读: 存在一定关联,Stata 回归中应同时控制 non-fintech 变量。")
            else:
                logger.info(f"  r({tone_col}, {c}) = {sig4(r)}")
                logger.info(f"     |r| = {sig4(r_abs)} ≥ 0.70 → 高度相关")
                logger.info(f"     解读: 需警惕多重共线性,可能削弱赛马回归的区分效力。")

    # ── 挤出弹性相关性校验 (方案断言 4) ──
    if 'ln_ft_articles' in panel.columns and 'ln_nf_articles' in panel.columns:
        valid_pair = panel[['ln_ft_articles', 'ln_nf_articles']].dropna()
        if len(valid_pair) >= 2:
            r_elast = valid_pair.corr().iloc[0, 1]
            logger.info("")
            logger.info("  ─── 挤出弹性校验 ───")
            logger.info(f"  r(ln_ft, ln_nf) = {sig4(r_elast)}")
            logger.info("    机理: fintech% + nf% ≡ 100% 的单位和约束会让对数弹性对趋于 "
                        "r→-1 的机械负关联; r 远离 -1 表明对数变换已解除该恒等约束 "
                        "(此为测量层诊断, 非因果效应)。")
            if r_elast < -0.95:
                logger.error("  ✗ r < -0.95: 疑似机械关联, "
                             "百分比约束未被对数变换消除!")
            elif r_elast < -0.5:
                logger.warning(f"  r ∈ (-0.95, -0.50): 中等负相关, "
                               f"回归中应注意共线性")
            else:
                logger.info(f"  ✓ r > -0.50: 非机械关联, "
                            f"对数弹性策略有效")

    return pearson


# ============================================================================
# 7. 导出
# ============================================================================

# fix(omni-g-controls-06, 2026-06-11): 字典提升为模块级常量 (原藏在 export_results
# 函数体内), 供 build_stage51_variable_labels 与测试共同消费。
# 挤出弹性与总量变量标签 (stage 51 专属, 覆盖优先于共享标签构建器)
STATA_LABELS_41 = {
    'ln_ft_articles':  'ln(1 + Fintech Articles, dedup basis)',
    'ln_nf_articles':  'ln(1 + Non-Fintech Articles)',
    'fintech_share':   'Fintech News Share',
    # fix(omni-g-controls-05, 2026-06-11): 零新闻指示 (fintech_share 无定义行)
    'zero_coverage':   'No-News Bank-Year (fintech_share undefined)',
    # fix(omni-g-controls-03/07, 2026-06-11): 去重 fintech 计数 (总量/份额同基分子)
    'ft_n_articles_dedup': 'Fintech Articles (dedup by bank-title-date)',
    # 银行注册地 (步骤 40 的 7c 生成)
    'bank_province':               'Bank HQ Province',
    'bank_city':                   'Bank HQ City',
    # Leave-one-out 情感 IV (步骤 40 的 7d 生成; 三轨 full/ctx/ss)
    # 用途: ivreghdfe Y (tone = prov_leave1out_tone_full) X, ...
    # ⚠ full×ctx×ss 三轨各自 just-identified, 禁混进同一 over-id Hansen J。
    'prov_leave1out_tone_full':     'Prov Leave-1-Out Tone (Full)',
    'prov_leave1out_tone_ctx':      'Prov Leave-1-Out Tone (Ctx)',
    'prov_leave1out_tone_ss':       'Prov Leave-1-Out Tone (Bank+FinTech same-sentence)',
    'city_leave1out_tone_full':     'City Leave-1-Out Tone (Full)',
    'city_leave1out_tone_ctx':      'City Leave-1-Out Tone (Ctx)',
    'city_leave1out_tone_ss':       'City Leave-1-Out Tone (Bank+FinTech same-sentence)',
    # 治理约束型合约 (Zhou et al., 2026, JBR §2.1; Core et al. 2003)
    'GOV_equity_ratio':             'Equity Comp / Total Comp Ratio',
    'GOV_cash_ratio':               'Cash Comp / Total Comp Ratio',
    'GOV_top3_pay_gap':             'ln(Top3 Exec Pay / Avg Emp Pay)',
    'GOV_esg_kpi':                  'ESG-KPI in Exec Comp (0/1)',
    'GOV_board_indep':              'Independent Director Ratio',
    'GOV_dual_chair':               'CEO-Chair Duality (0/1)',
    'GOV_comp_committee':           'Compensation Committee (0/1)',
    'GOV_ceo_tenure':               'CEO Tenure (Years)',
}


def build_stage51_variable_labels(sanitized_cols, original_cols) -> dict:
    """fix(omni-g-controls-06, 2026-06-11): stage 51 .dta 变量标签构建。

    此前 51_panel_with_controls.dta 只传 17 键局部字典 (盘上实测 9/1668 列有
    标签), 与 40.dta (666 条策展标签) / 46_*.dta 断崖式不一致 — 而 CLAUDE.md
    恰推荐 MP 用户直接读本文件。改为消费 stage 46 的共享标签构建器
    ``stata_export.build_variable_labels`` (codebook meta → HEURISTIC_LABELS →
    zh JSON → 列名兜底, ≤80 UTF-8 字节), 以 rename_map(短名→原名) 桥接
    sanitize 改名。

    WP3 整改 (2026-07-11, 评审 P1): STATA_LABELS_41 (英文) 从"覆盖优先"降为
    **兜底补位层** — 旧口径 ``{**shared, **overlay}`` 让英文 overlay 覆盖中文
    共享标签, 其中 5 个 51-only 列 (ln_ft_articles/ln_nf_articles/fintech_share/
    zero_coverage/ft_n_articles_dedup) 不在 46_panel_yearly_labels.do 宇宙 →
    终态永久英文, 违反「标签均使用中文」硬口径且与 codebook 两端分叉。现口径:
    shared 产出真标签 (≠裸列名兜底) 时中文胜出; 仅当 shared 对该列退化为裸列名
    (如 zh JSON 意外缺失 / 未来财务列 GOV_* 尚无中文条目) 时 overlay 补位 —
    保留其安全网职能, 不再遮蔽中文。gate:
    tests/test_stata_labels_zh.py::TestStage51RealWritePath。

    注: 真正的单一事实源 (export.py 函数内 STATA_LABELS 提升为模块级共享)
    须改 pipeline/panel/export.py (本轮另组负责文件), 留待主控统一落地。

    参数:
        sanitized_cols: sanitize_stata_columns 之后的列名序列 (.dta 实际列名)
        original_cols:  sanitize 之前的原始 panel 列名序列 (与上一一对应)
    返回:
        {sanitized_col: label} — 每列必有非空标签 (兜底为原始列名)
    """
    from news_process.pipeline.panel.stata_export import build_variable_labels
    sanitized_cols = list(sanitized_cols)
    original_cols = list(original_cols)
    rename_map = {new: old for new, old in zip(sanitized_cols, original_cols)
                  if new != old}
    shared = build_variable_labels(pd.DataFrame(columns=sanitized_cols),
                                   rename_map=rename_map)
    overlay = {k: v for k, v in STATA_LABELS_41.items()
               if k in set(sanitized_cols)}
    # WP3 整改 (2026-07-11): 中文共享标签优先; overlay 仅补 shared 裸列名兜底位
    # (shared 对每列必有值, 裸兜底 = label == 该列的原名/列名本身)。
    sanitized2orig = dict(zip(sanitized_cols, original_cols))
    merged = dict(shared)
    for k, v in overlay.items():
        bare_fallbacks = {k, sanitized2orig.get(k, k)}
        if merged.get(k, k) in bare_fallbacks:
            merged[k] = v
    return merged


def export_results(panel: pd.DataFrame, pearson_corr: pd.DataFrame):
    """多格式导出。"""
    logger.info("=" * 70)
    logger.info("步骤 6: 多格式导出")
    logger.info("=" * 70)

    # Parquet
    output_filename = FILENAMES.get(
        'output_51_panel_controls', '51_panel_with_controls.parquet'
    )
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    # 血缘修复 (audit-fixes 2026-05-29): stage 51 是 3-way fan-in, load_data()
    # 硬读三个文件 (12_fintech_full / 40_article_bank / 40_panel_yearly, 各
    # sys.exit(1) on missing), 故 input_files 须记全部三者, 否则
    # verify_data_integrity 对前两者 (定义对照组的 anti-join 源) 的篡改/陈旧
    # 检测不到 (与 test_lineage_input_contract.py 强制的 fan-in 全记约定一致).
    _od = CONFIG['paths']['output_dir']
    _fn = CONFIG['filenames']
    input_files = [
        os.path.join(_od, _fn['output_40_panel_yearly']),
        os.path.join(_od, _fn.get('output_12_fintech_full', '12_fintech_news_full.parquet')),
        os.path.join(_od, _fn.get('output_40_article_bank', '40_article_bank_level.parquet')),
    ]
    save_dataset(panel, output_path, logger,
                stage_name="51_falsification_test",
                config=CONFIG,
                input_files=input_files)

    # Stata .dta
    dta_path = os.path.splitext(output_path)[0] + '.dta'
    logger.info(f"  正在生成 Stata .dta 文件...")
    logger.info(f"    说明: Stata 列名不支持中文和特殊字符,")
    logger.info(f"          将自动清理列名 (去除中文、替换括号、截断32字符)。")
    # B-3 同精神 (audit-fixes 2026-05-29): 先删旧 .dta, 避免本次写出失败时
    # 陈旧 .dta 与新 .parquet 错位被 falsification_template.do 当新数据消费.
    if os.path.exists(dta_path):
        os.remove(dta_path)
        logger.info(f"  已删除旧 .dta (避免与新 .parquet 错位): {dta_path}")
    try:
        panel_stata = panel.copy()
        # v6/F2 Stata 兼容: pandas Int*/boolean nullable → Float64 (NaN 保留)
        for _col in panel_stata.select_dtypes(include=['Int8','Int16','Int32','Int64','boolean']).columns:
            panel_stata[_col] = panel_stata[_col].astype('Float64')
        # S3 fix v2 (2026-05-30): stage 51 的 .dta 列名走与 stage 45/46 **同一个**
        # 规范 sanitizer (export.py 用 sanitize_stata_columns, 内部委托
        # stata_export.shorten→asciify)。单一事实源 → 51_panel_with_controls.dta
        # 的列名与 40/46 逐字节一致。旧的内联循环只做了中文映射, 在 >32 字符
        # 列名上仍会分叉 (中文映射后超 32 字符时轨道后缀被截毁)。
        from news_process.papers._common.tables import sanitize_stata_columns
        # fix(omni-g-controls-06, 2026-06-11): 记录 sanitize 前原始列名, 供共享
        # 标签构建器按原名查 codebook/HEURISTIC (改名列否则必 miss)。
        _orig_cols = list(panel_stata.columns)
        panel_stata.columns = sanitize_stata_columns(panel_stata.columns, max_len=32)
        for col in panel_stata.select_dtypes(include=['Float64', 'Int64']).columns:
            panel_stata[col] = panel_stata[col].astype(float)
        # fix(omni-g-controls-06, 2026-06-11): 共享标签构建器 + STATA_LABELS_41
        # 覆盖 — 替代仅 17 键局部字典 (实测 9/1668 列有标签, 与 40/46 .dta 断崖)。
        labels_41 = build_stage51_variable_labels(panel_stata.columns, _orig_cols)
        panel_stata.to_stata(dta_path, write_index=False, version=118,
                             variable_labels=labels_41)
        logger.info(f"  ✓ 已导出 Stata 文件: {dta_path}")
        logger.info(f"    Stata 列数: {len(panel_stata.columns)}")
        _n_labeled = sum(1 for c in panel_stata.columns
                         if labels_41.get(c) and labels_41[c] != c)
        logger.info(f"    变量标签覆盖 (非列名兜底): {_n_labeled}/"
                    f"{len(panel_stata.columns)} 列 [fix omni-g-controls-06]")
    except Exception as e:
        # B-2 同精神 (audit-fixes 2026-05-29): 根除 swallow-errors 反模式.
        # 旧代码仅 logger.warning 让 stage 51 退出码假装 0, 但 .dta 未写出 (或
        # 残留陈旧版), 与 .parquet 形成"语义错位"灾难 —
        # falsification_template.do `use "51_panel_with_controls.dta"` 会静默
        # 消费陈旧数据. 改为 raise 让 orchestrator 立即停止 (与 export.py:1013
        # stage 45 同精神; 注册输出是先写成功的 .parquet, orchestrator 存在性
        # 检查无法捕获 .dta 失败, 故 swallow 在此尤其危险). 上方已先删旧 .dta,
        # 故 raise 后不会残留语义错位的半成品.
        raise RuntimeError(
            f"[export_results] Stage 51 Stata 导出失败: {e}; "
            f"已删除旧 .dta 避免与新 .parquet 错位; "
            f"请检查 panel 中是否有 to_stata 不兼容的 dtype/数据."
        ) from e

    # 相关矩阵 CSV
    if pearson_corr is not None:
        diag_path = os.path.join(OUTPUT_DIR, '51_falsification_diagnostics.csv')
        pearson_corr.to_csv(diag_path)
        logger.info(f"  ✓ 已导出诊断文件: {diag_path}")


# ============================================================================
# 8. Stata 回归模板
# ============================================================================

def print_stata_template():
    """在日志中输出 Stata 回归模板。"""
    logger.info("=" * 70)
    logger.info("步骤 7: Stata 回归模板")
    logger.info("=" * 70)
    logger.info("")
    logger.info("  ─── 方法论说明 ───")
    logger.info(f"  本模板对标: {REFERENCES['Hassan2019']}")
    logger.info(f"  → Table 7: PRisk vs NPRisk 非对称预测检验")
    logger.info(f"")
    logger.info(f"  核心思想 (Tetlock 2007, JF):")
    logger.info(f"    新闻量 (volume) 和情感内容 (content) 是不同维度。")
    logger.info(f"    如果 tone 仅仅是 volume 的代理变量,")
    logger.info(f"    控制 volume 后 tone 的系数应变得不显著。")
    logger.info(f"    反之,如果 tone 保持显著,则证明其包含独立的增量信息。")
    logger.info("")
    logger.info("  ─── 聚类稳健推断依据 (cluster(bank_id) + absorb(bank_id year) 设定) ───")
    logger.info("  本检验/placebo 回归在 bank-year 面板上以 cluster(bank_id) 计标准误、")
    logger.info("  吸收 bank/year 双向固定效应; 该聚类与时间效应推断对标 2023-2026 前沿:")
    logger.info("    · Hansen, B. E. (2026). Jackknife standard errors for clustered "
                "regression. The Review of Economic Studies. Advance online "
                "publication. https://doi.org/10.1093/restud/rdag050")
    logger.info("      (白话: CV3 cluster-jackknife SE, 锚定 cluster(bank_id) 标准误选择,"
                "在簇数有限时比经典 CRVE 更稳健。)")
    logger.info("    · Hounyo, U., & Lin, J. (2026). Wild bootstrap inference with "
                "multiway clustering and serially correlated time effects. Journal "
                "of Business & Economic Statistics, 44(2), 601-612. "
                "https://doi.org/10.1080/07350015.2025.2546454")
    logger.info("      (白话: 多维聚类 wild cluster bootstrap 允许时间效应序相关, "
                "锚定本面板赛马回归在 cluster(bank_id) 之外对时间维度的稳健推断。)")

    template_path = (
        Path(__file__).resolve().parents[2]
        / 'papers_assets' / 'bank_fintech_tone' / 'do'
        / 'falsification_template.do.tmpl'
    )
    if not template_path.exists():
        logger.error(f"Stata 模板文件未找到: {template_path}")
        return

    template = template_path.read_text(encoding='utf-8')
    for line in template.strip().splitlines():
        logger.info(f"  {line}")


# ============================================================================
# 9. 参考文献汇总
# ============================================================================

def print_references():
    """在日志中输出完整参考文献列表。"""
    logger.info("=" * 70)
    logger.info("参考文献 (完整引用)")
    logger.info("=" * 70)
    for key, ref in REFERENCES.items():
        logger.info(f"  [{key}] {ref}")


# ============================================================================
# G-13: Placebo 时点检验
# ============================================================================
# 学术依据 (fix(omni-g-controls-01, 2026-06-11): 移除 Hassan et al. 2019 QJE
# Table 7 错配引用 — 该表是 PRisk/NPRisk 伪造检验, 与 placebo-in-time 无关):
#   Callaway & Sant'Anna (2021, JoE, §4.3):
#     "Pre-treatment placebo tests are essential for validating
#      the parallel trends assumption in staggered DID."
#     伪处理窗口必须落在真实处理之前 (year < treat_year)。
#   La Ferrara, Chong & Duryea (2012, AEJ:Applied): placebo-in-time 设计,
#     将处理年份提前 k 年并仅在处理前样本中估计伪效应。
# ============================================================================

def generate_placebo_did_variables(panel: pd.DataFrame,
                                   placebo_shifts: list = None,
                                   logger_inst=None) -> pd.DataFrame:
    """G-13: 构建 Placebo 时点 DID 变量。

    对面板中每个 DID 政策冲击, 将 treat_year 提前 k 年 (k ∈ placebo_shifts),
    生成伪处理变量 {prefix}_placebo{k}_post, 供回归检验使用。

    fix(omni-g-controls-01, 2026-06-11) 语义变更披露: 伪处理窗口加上界
    placebo_post = 1{treat_year-k <= year < treat_year} — 旧实现 1{year >= ty-k}
    是真实 post 的严格超集, placebo 系数混入真实处理效应 → 只要真实效应存在
    placebo 必显著, 会机械性误判平行趋势违反 (Callaway & Sant'Anna 2021 §4.3
    pre-treatment placebo 要求窗口落在处理前)。

    参数:
        panel:           Bank-Year 面板 (须已包含 {prefix}_treat_year 列)
        placebo_shifts:  提前年数列表 (默认 [1, 2, 3])
        logger_inst:     日志实例

    新增列 (每个政策 × 每个 shift):
        {prefix}_placebo{k}_post:  伪政策后哑变量 (仅处理前窗口 [ty-k, ty) 内=1)
        {prefix}_placebo{k}_did:   伪 DID 交互项 (treated × placebo_post)

    Stata 用法:
      * 检验 placebo DID 是否显著 (应不显著); 须同时控制真实 DID 项,
        或将样本限于处理前期间:
        reghdfe Y dcep_placebo2_did dcep_did X, absorb(bank_id year) cluster(bank_id)
        * 或: reghdfe Y dcep_placebo2_did X if year < dcep_treat_year | ///
              dcep_treat_year == 0, absorb(bank_id year) cluster(bank_id)
      * 若显著 → 处理前已有趋势分化, 平行趋势假设可能违反

    白话: placebo (安慰剂) 检验 = 故意把政策时间往前挪 k 年再跑一遍 DID。
    那几年其实什么都没发生, 如果"假政策"也跑出显著效应, 说明处理组和
    对照组在政策之前就已经走势不同, 真实 DID 的结果就不可信。关键是
    假窗口必须截止在真政策之前 (year < treat_year), 否则会把真效应
    混进来, 假检验必然显著、白测。

    返回:
        panel: 附加 placebo DID 变量的 DataFrame
    """
    lg = logger_inst or logger
    if placebo_shifts is None:
        placebo_shifts = [1, 2, 3]

    lg.info("=" * 70)
    lg.info("G-13: Placebo 时点检验变量生成")
    lg.info("  对标: Callaway & Sant'Anna (2021, JoE, §4.3) pre-treatment placebo")
    lg.info(f"  📖 {_G_RUNTIME_REFS['callaway_santanna_did']}")
    lg.info("  对标: La Ferrara, Chong & Duryea (2012, AEJ:Applied) placebo-in-time")
    lg.info(f"  Placebo shifts: {placebo_shifts} (提前 k 年, 窗口截断于真实处理年)")
    lg.info("=" * 70)

    # 找到所有 DID 政策前缀
    treat_year_cols = [c for c in panel.columns if c.endswith('_treat_year')]
    if not treat_year_cols:
        lg.warning("  未找到 *_treat_year 列, 跳过 Placebo 检验")
        return panel

    for ty_col in treat_year_cols:
        prefix = ty_col.replace('_treat_year', '')

        for k in placebo_shifts:
            # 伪治疗年份 = 真实治疗年份 - k
            placebo_ty = np.where(
                panel[ty_col] > 0,
                panel[ty_col] - k,
                0
            )

            # 伪政策后哑变量 — fix(omni-g-controls-01, 2026-06-11): 窗口加上界
            # year < 真实 treat_year。旧实现 1{year >= ty-k} 是真实 post 的严格
            # 超集 → placebo 系数 = 前趋势效应与真实处理效应的加权平均, 全量
            # T=18 下处理后年份主导窗口, 真实效应存在则 placebo 必显著, 按
            # "若显著则平行趋势不成立"的解读会机械性误判。现仅覆盖处理前窗口
            # [ty-k, ty) (Callaway & Sant'Anna 2021 pre-trend placebo)。
            plac_post_col = f'{prefix}_placebo{k}_post'
            panel[plac_post_col] = np.where(
                placebo_ty > 0,
                ((panel['year'] >= placebo_ty)
                 & (panel['year'] < panel[ty_col])).astype(int),
                0
            )

            # 伪 DID 交互项
            plac_did_col = f'{prefix}_placebo{k}_did'
            treated_col = f'{prefix}_treated'
            if treated_col in panel.columns:
                panel[plac_did_col] = (
                    panel[treated_col] * panel[plac_post_col]
                )
            else:
                panel[plac_did_col] = 0

            n_treated_plac = (panel[plac_did_col] == 1).sum()
            lg.info(f"  {plac_did_col}: treated×post = {n_treated_plac}")

        # Stata 命令建议 — fix(omni-g-controls-01, 2026-06-11): 同时控制真实
        # DID 项 (或限处理前样本), 避免伪效应吸收真实处理效应。
        lg.info(f"  ── {prefix} Placebo Stata 命令 ──")
        for k in placebo_shifts:
            lg.info(f"    reghdfe Y {prefix}_placebo{k}_did {prefix}_did X, "
                    f"absorb(bank_id year) cluster(bank_id)")
        lg.info(f"    * 替代: 限处理前样本 keep if year < {prefix}_treat_year "
                f"| {prefix}_treat_year == 0")
        lg.info(f"    * 预期: 所有 placebo DID 系数应不显著 (p > 0.10)")
        lg.info(f"    * 若显著: 处理前已有趋势分化, 平行趋势假设可能不成立")

    return panel


# ============================================================================
# G-09: 金融科技分类外部交叉验证诊断
# ============================================================================
# 学术依据:
#   胡俊, 李强, 戴嘉诚, & 曾勇 (2024, 中国管理科学 32(1):31-41): 银行金融科技关键词测度
#   Gentzkow et al. (2019, JEL): "Text as Data" — 测度有效性验证
# ============================================================================

def diagnose_fintech_classification_consistency(panel: pd.DataFrame,
                                                 logger_inst=None) -> dict:
    """G-09: 诊断金融科技分类指标的内部一致性。

    在无外部数据源的情况下, 通过面板内部指标间的相关性
    检验金融科技分类的收敛有效性 (convergent validity):
      1. tech_frac vs fintech_article_count: 应高度正相关
      2. tech_frac vs LLM 情感: 应有合理的相关模式
      3. 年度均值趋势: 应呈上升趋势 (金融科技投入逐年增加)

    返回:
        dict: 诊断结果
    """
    lg = logger_inst or logger

    lg.info("=" * 70)
    lg.info("G-09: 金融科技分类内部一致性诊断")
    lg.info("  对标: Gentzkow et al. (2019, JEL §3): 测度收敛有效性")
    lg.info(f"  📖 {_G_RUNTIME_REFS['gentzkow_text_as_data']}")
    lg.info("=" * 70)

    result = {}

    # (1) tech_frac vs n_articles 相关性
    if 'tech_frac' in panel.columns and 'n_articles' in panel.columns:
        valid = panel[['tech_frac', 'n_articles']].dropna()
        if len(valid) > 10:
            corr = valid['tech_frac'].corr(valid['n_articles'])
            result['tech_frac_vs_n_articles'] = round(corr, 4)
            lg.info(f"  tech_frac × n_articles: r = {sig4(corr)}"
                    f" {'✓ 正相关' if corr > 0.1 else '低相关'}")

    # (2) 年度均值趋势
    if 'tech_frac' in panel.columns and 'year' in panel.columns:
        trend = panel.groupby('year')['tech_frac'].mean()
        result['yearly_trend'] = trend.to_dict()
        lg.info(f"  tech_frac 年度均值趋势:")
        for y, v in trend.items():
            lg.info(f"    {y}: {sig4(v)}")

        # 简单线性趋势检验 (年份与均值的相关性)
        if len(trend) >= 3:
            years = np.array(list(trend.index), dtype=float)
            vals = np.array(list(trend.values), dtype=float)
            if np.std(years) > 0 and np.std(vals) > 0:
                trend_corr = np.corrcoef(years, vals)[0, 1]
                result['trend_correlation'] = round(trend_corr, 4)
                lg.info(f"  时间趋势相关系数: r = {sig4(trend_corr)}"
                        f" {'✓ 上升趋势' if trend_corr > 0.3 else '无明显趋势'}")

    # (3) 外部验证建议
    lg.info("  ── 外部验证建议 (如有数据可用) ──")
    lg.info("    * 与北大数字金融普惠指数 (Peking University DFIIC) 相关性分析")
    lg.info("    * 与各银行年报中 '金融科技' 章节词频的 Pearson/Spearman 相关")
    lg.info("    * 与银保监会金融科技监管评级 (如有) 的序数相关")

    return result


# ============================================================================
# G-11: 别名系统精确率-召回率定量报告
# ============================================================================
# 学术依据: 标准分类评估 (Precision / Recall / F1)
# ============================================================================

def diagnose_alias_matching_quality(panel: pd.DataFrame,
                                     logger_inst=None) -> dict:
    """G-11: 别名系统匹配质量诊断。

    通过面板中的匹配统计间接评估别名系统的质量:
      1. 银行覆盖率: 有多少银行至少匹配到 1 篇文章
      2. 匹配浓度: 每家银行的年均文章数分布 (检测异常值)
      3. 零匹配年份: Bank-Year 中无文章的观测比例

    返回:
        dict: 诊断结果
    """
    lg = logger_inst or logger

    lg.info("=" * 70)
    lg.info("G-11: 别名匹配质量诊断")
    lg.info("=" * 70)

    result = {}

    if 'n_articles' not in panel.columns:
        lg.warning("  n_articles 列不存在, 跳过诊断")
        return result

    # (1) 银行覆盖率
    bank_has_articles = panel.groupby('target_bank')['n_articles'].sum() > 0
    n_covered = bank_has_articles.sum()
    n_total = len(bank_has_articles)
    result['bank_coverage'] = f"{n_covered}/{n_total}"
    lg.info(f"  银行覆盖率: {n_covered:,}/{n_total:,} "
            f"({pct4(n_covered / max(n_total, 1))})")

    # (2) 匹配浓度
    bank_avg = panel.groupby('target_bank')['n_articles'].mean()
    result['articles_per_bank_mean'] = round(bank_avg.mean(), 2)
    result['articles_per_bank_median'] = round(bank_avg.median(), 2)
    result['articles_per_bank_p95'] = round(bank_avg.quantile(0.95), 2)
    lg.info(f"  年均文章数: mean={sig4(bank_avg.mean())}, "
            f"median={sig4(bank_avg.median())}, "
            f"P95={sig4(bank_avg.quantile(0.95))}")

    # (3) 异常值检测 (>3σ)
    threshold = bank_avg.mean() + 3 * bank_avg.std()
    outliers = bank_avg[bank_avg > threshold]
    if len(outliers) > 0:
        result['outlier_banks'] = list(outliers.index[:5])
        lg.info(f"  高匹配异常值 (>3σ={sig4(threshold)}): "
                f"{list(outliers.index[:5])}")
    else:
        lg.info(f"  ✓ 无高匹配异常值 (3σ={sig4(threshold)})")

    # (4) 零匹配年份比例
    zero_pct = (panel['n_articles'] == 0).sum() / max(len(panel), 1)
    result['zero_article_pct'] = round(zero_pct, 4)
    lg.info(f"  零匹配 Bank-Year: {int((panel['n_articles']==0).sum()):,}/{len(panel):,} "
            f"({pct4(zero_pct)})")
    if zero_pct > 0.5:
        lg.info(f"  零匹配比例较高, 建议检查关键词阈值或银行名称覆盖度")

    return result


# ============================================================================
# 主流程
# ============================================================================

def main():
    """51_falsification_test 主流程。"""
    start_time = time.time()
    # ── 黄金范式单 banner (替换旧短阶段头, 让 <stage>.log 自带说明书; 不叠加旧 banner) ──
    logger.info("=" * 72)
    logger.info("阶段 51: 伪造检验对照变量构建 (Hassan et al. 2019 QJE Table 7 范式)")
    logger.info("=" * 72)
    logger.info("【功能】给核心结论做'打假对照实验': 用 anti-join 把所有非金融科技银行新闻")
    logger.info("        (全量银行新闻 MINUS 已进面板的金融科技文章) 挑出来, 数清每家银行")
    logger.info("        每年的普通新闻篇数/媒体广度/标题提及率, 当作安慰剂(volume)对照变量")
    logger.info("        挂回 bank-year 面板, 产出 51_panel_with_controls.{parquet,dta} +")
    logger.info("        51_falsification_diagnostics.csv (情感×新闻量相关矩阵)。")
    logger.info("【假设】H0: fintech tone 的解释力完全来自银行层面一般媒体关注度;")
    logger.info("        H1: fintech tone 包含金融科技维度的特异性增量信息 (本检验欲支持 H1)。")
    logger.info("【方法】anti-join 复合键 (target_bank, 标题, 日期) 双侧去重后集合差集 (互补划分);")
    logger.info("        nf_ln_coverage=ln(1+count) (Fang-Peress 2009); nf_media_breadth=物理口径")
    logger.info("        distinct-outlet (Bushee 2010); fintech_share=ft_dedup/(ft_dedup+nf) 同基,")
    logger.info("        分母0→NaN(zero_coverage 标记); 诊断阈值 |r|<0.3 弱相关支持 H1。")
    logger.info(f"        核心方法论对标: {REFERENCES['Hassan2019']}")
    logger.info("        → Table 7: 通过 PRisk vs NPRisk 的非对称预测验证构造效度。")
    logger.info("【判读】fintech_share 与 nf_* 越是弱相关 (|r|<0.3) → fintech tone 越像独立信号(好);")
    logger.info("        |r|≥0.7 高相关→赛马回归区分力存疑(坏); 挤出弹性三档 r<-0.95 机械约束(坏)/-0.95≤r<-0.50 中等(警告)/r≥-0.50 有效(好)。")
    logger.info("【确定性】纯 pandas/numpy, 无 LLM/Embedding/网络, 逐位可复现。")
    logger.info("")

    # ── 黄金范式【项目/环境信息 + 输入输出 + 运行配置 + 方法论引文】(日志富集 2026-06-24) ──
    # 提前解析输出路径, 供环境块一次性披露读写路径; 纯日志, 不改任何产物 (golden-safe)。
    _output_path = os.path.join(
        OUTPUT_DIR,
        FILENAMES.get('output_51_panel_controls', '51_panel_with_controls.parquet'),
    )
    _full_path = os.path.join(
        OUTPUT_DIR,
        FILENAMES.get('output_12_fintech_full', '12_fintech_news_full.parquet'))
    _art_path = os.path.join(
        OUTPUT_DIR,
        FILENAMES.get('output_40_article_bank', '40_article_bank_level.parquet'))
    _panel_path = os.path.join(
        OUTPUT_DIR,
        FILENAMES.get('output_40_panel_yearly', '40_panel_yearly.parquet'))
    _log_environment_and_config(_full_path, _art_path, _panel_path, _output_path)
    logger.info("")

    # 运行期阶段计时累计 (各主要子步墙钟耗时, 末尾汇总打印; 仅服务日志, golden-safe)
    phase_durations: dict[str, float] = {}

    # 1-7. 主流程 (逐步 wall-clock 计时)
    _t = time.time()
    df_full, df_art, panel = load_data()
    phase_durations['①数据加载(3-way fan-in)'] = time.time() - _t

    _t = time.time()
    df_nf = build_non_fintech(df_full, df_art)
    phase_durations['②anti-join 构建 NF 对照组'] = time.time() - _t

    _t = time.time()
    nf_agg = aggregate_non_fintech(df_nf)
    phase_durations['③NF Bank-Year 聚合'] = time.time() - _t

    # fix(fintech-share-counting-basis): 取去重口径 fintech 计数 (build_non_fintech 经 attrs
    # 暴露) 作 fintech_share 分子, 与 NF 分母同基。
    _ft_dedup = df_nf.attrs.get('ft_dedup_agg') if hasattr(df_nf, 'attrs') else None
    _t = time.time()
    panel = merge_to_panel(panel, nf_agg, ft_dedup_agg=_ft_dedup)
    phase_durations['④合并到面板+总量变量'] = time.time() - _t

    _t = time.time()
    pearson_corr = run_diagnostics(panel)
    phase_durations['⑤诊断(相关矩阵)'] = time.time() - _t

    _t = time.time()
    export_results(panel, pearson_corr)
    phase_durations['⑥多格式导出(parquet/dta/csv)'] = time.time() - _t

    print_stata_template()
    print_references()

    # ── 黄金范式【结果分析】: 取真实产出指标, 对照阈值/预期方向给好/坏/临界判读 ──
    # 注: 以下局部变量仅用于日志解读, 绝不回写 panel / 任何产物 (golden-safe)。
    # crash-guard: 本分析块虽在 export_results 写盘**之后**执行 (产物不会因此丢失),
    # 但仍整体包 try/except, 任何缺列/空 Series/NaN 比较异常都降级为 WARNING, 决不
    # 中断阶段收尾 (log_stage_summary)。
    try:
        logger.info("-" * 72)
        logger.info("【结果分析】伪造检验对照变量产出质量评估 (相对 Hassan 2019 H0 vs H1)")

        # (1) 对照组规模与互补划分 — Non-Fintech 占比应远高于 fintech (对照组须够大)
        # 注: 覆盖率分子须取 left-join 后**落到面板内**的 NF 行 (nf_n_articles>0),
        # 而非 len(nf_agg) — 后者按 (target_bank,year) 聚合自全量 NF 语料, 含面板外
        # 银行/年份, 直接除以 len(panel) 会得 >100% 的无意义比率。
        _n_panel = len(panel)
        if 'nf_n_articles' in panel.columns:
            _n_nf_rows = int((panel['nf_n_articles'] > 0).sum())
        else:
            _n_nf_rows = 0
        _nf_cover_rate = _n_nf_rows / max(_n_panel, 1) * 100
        logger.info(f"  ① 对照组覆盖: {_n_nf_rows:,}/{_n_panel:,} 个面板 bank-year 有非金融科技新闻 "
                    f"({pct4(_nf_cover_rate, fraction=False)})。")
        if _nf_cover_rate >= 50:
            logger.info("     判读: 多数 bank-year 有 NF 对照新闻 → 安慰剂 volume 变量有足量变异 (好)。")
        elif _nf_cover_rate > 0:
            logger.info("     判读: NF 覆盖偏稀疏 → 赛马回归中 nf_* 变异有限, 控制效力受限 (临界)。")
        else:
            logger.warning("     判读: NF 对照组为空 → 伪造检验无法执行, 须检查 anti-join 与上游覆盖 (坏)。")

        # (2) fintech_share 信息密集度 — 越接近 Hassan PRisk/(PRisk+NPRisk) 的合理低值越好
        if 'fintech_share' in panel.columns:
            _fs = panel['fintech_share'].dropna()
            # NaN-guard: 全 NaN (无有效份额) 时不落进数值方向判断 (否则 mean=nan 且
            # 方向 ternary 因 nan 比较恒 False 误落 "占少数(合理)" 档)。
            if len(_fs) == 0:
                logger.info(f"  ② fintech_share: 该列全 NaN (0/{_n_panel:,} 行有定义) → "
                            "无有效份额, 跳过密集度判读 (多因面板全为零新闻 bank-year)。")
            else:
                _fs_mean = float(_fs.mean())
                _fs_med = float(_fs.median())
                logger.info(f"  ② fintech_share: mean={sig4(_fs_mean)}, median={sig4(_fs_med)} "
                            f"(有定义行 {len(_fs):,}/{_n_panel:,})。")
                if _fs_mean < 0.5:
                    logger.info("     判读: 金融科技新闻在全部银行新闻中占少数 → 与制度先验一致, "
                                "对照组(NF)主导信息环境 (合理)。")
                else:
                    logger.warning("     判读: fintech_share 均值 ≥0.5 偏高 → 警惕 anti-join 漏切或"
                                   "分子分母计数基不一致 (须复核去重同基)。")
            # zero_coverage: 全年零新闻被标 NaN 而非 0 份额, 应占少数
            if 'zero_coverage' in panel.columns:
                _zc = int(panel['zero_coverage'].sum())
                _zc_rate = _zc / max(_n_panel, 1) * 100
                logger.info(f"     zero_coverage (全年零新闻, fintech_share 无定义): {_zc:,} 行 "
                            f"({pct4(_zc_rate, fraction=False)})。")
                if _zc_rate > 50:
                    logger.warning("     判读: 过半 bank-year 零新闻 → 面板稀疏, 份额类变量样本严重缩水 (坏)。")
                else:
                    logger.info("     判读: 零新闻行已正确记 NaN (而非冒充 0 份额), 回归将自然剔除 (好)。")

        # (3) 区分效力 — 情感三轨 × NF 新闻量相关; |r|<0.3 支持 H1 (tone 含特异性增量信息)
        # column-guard: 相关矩阵为方阵 (行列对称); _tc/_nc 均先核 in columns 再 .loc
        # 取值 (ss 轨缓存常未播种 → llm_vote_tone_ss 缺列时自然不进列表, 优雅跳过)。
        if pearson_corr is not None:
            _tone_cols = [c for c in ['llm_vote_tone_full', 'llm_vote_tone_ctx',
                                      'llm_vote_tone_ss', 'dict_avg_tone_full']
                          if c in pearson_corr.columns]
            _nf_diag_cols = [c for c in ['nf_ln_coverage', 'nf_media_breadth']
                             if c in pearson_corr.columns]
            _r_abs_list = []
            for _tc in _tone_cols:
                for _nc in _nf_diag_cols:
                    _rv = pearson_corr.loc[_tc, _nc]
                    if pd.notna(_rv):
                        _r_abs_list.append(abs(float(_rv)))
            if _r_abs_list:
                _max_r = max(_r_abs_list)
                _n_weak = sum(1 for v in _r_abs_list if v < 0.3)
                logger.info(f"  ③ 区分效力: 情感×NF新闻量 共 {len(_r_abs_list)} 对相关, "
                            f"其中 {_n_weak} 对 |r|<0.3 (弱相关), 最大 |r|={sig4(_max_r)}。")
                if _max_r < 0.3:
                    logger.info("     判读: 全部弱相关 → fintech tone 与一般媒体关注度独立, 强支持 H1 (好)。")
                elif _max_r < 0.7:
                    logger.info("     判读: 存在中等相关 → Stata 赛马回归须同时控制 nf_* 变量 (临界)。")
                else:
                    logger.warning("     判读: 出现高度相关 (|r|≥0.7) → 多重共线性威胁伪造检验区分效力 (坏)。")
            else:
                logger.info("  ③ 区分效力: 情感×NF新闻量 相关全 NaN/无可用配对 → 跳过区分判读 "
                            "(多因情感轨列未物化或样本不足)。")
            # 挤出弹性: r(ln_ft, ln_nf) 不应趋于 -1 (否则 fintech%+nf%≡100% 机械约束未消除)
            if ('ln_ft_articles' in panel.columns and 'ln_nf_articles' in panel.columns):
                _vp = panel[['ln_ft_articles', 'ln_nf_articles']].dropna()
                if len(_vp) >= 2:
                    _r_elast = float(_vp.corr().iloc[0, 1])
                    # NaN-guard: 任一列常数 (零方差) 时 corr 返回 NaN, 不能落进
                    # r<-0.95 比较 (nan 比较恒 False 会误判 "非机械关联(好)")。
                    if pd.isna(_r_elast):
                        logger.info("     挤出弹性 r(ln_ft, ln_nf) = NaN (某列零方差/常数) → "
                                    "无法判读机械关联, 跳过。")
                    else:
                        logger.info(f"     挤出弹性 r(ln_ft, ln_nf) = {sig4(_r_elast)}。")
                        if _r_elast < -0.95:
                            logger.warning("     判读: r<-0.95 → 疑似机械关联, 对数变换未消除百分比约束 (坏)。")
                        else:
                            logger.info("     判读: 非机械关联 (r>-0.95), 对数弹性策略有效 (好)。")
        else:
            logger.warning("  ③ 区分效力: run_diagnostics 返回 None (可用诊断列<2) → "
                           "相关矩阵未生成, 伪造检验区分判读缺失; 多因情感轨列尚未物化 (优雅降级)。")

        # (4) 小样本警告 — 盘面 T=2 仅验证管道正确性, 全量结论以 17M/T=18 为准
        if 'year' in panel.columns and 'target_bank' in panel.columns:
            _n_years = int(panel['year'].nunique())
            _n_banks = int(panel['target_bank'].nunique())
            logger.info(f"  ④ 面板深度: {_n_banks} 家银行 × {_n_years} 年 = {_n_panel:,} 行。")
            if _n_years <= 2:
                logger.info(f"     ⚠ 小样本 (T={_n_years}): 本机盘面为伪两年片段, 相关系数与份额分布"
                            "仅验证管道正确性, 弱/高相关结论以全量 17M/T=18 实测为准。")

        logger.info("-" * 72)
    except Exception as _e:
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")

    # ── ⏱ 运行期阶段计时 (墙钟; 纯日志, golden-safe) ──
    try:
        logger.info("⏱ 运行期阶段计时 (墙钟):")
        _total_phase = sum(phase_durations.values()) or 1.0
        for _name, _dur in phase_durations.items():
            logger.info(f"     · {_name}: {sig4(_dur)} 秒 "
                        f"({pct4(_dur / _total_phase)})")
        logger.info(f"     · 子步合计: {sig4(sum(phase_durations.values()))} 秒")
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"[阶段计时] 打印异常, 跳过(不影响产物): {_e}")

    # 阶段摘要
    log_stage_summary(
        logger, STAGE_NAME, start_time,
        input_rows=len(df_full),
        output_rows=len(panel),
        extra_info={
            '新增控制变量': 'nf_n_articles, nf_ln_coverage, nf_media_breadth, '
                           'nf_headline_frac, all_n_articles, all_ln_coverage, '
                           'fintech_share',
            '面板列数': panel.shape[1],
        }
    )

    logger.info("51_falsification_test 执行完毕 ✓")


if __name__ == '__main__':
    main()
