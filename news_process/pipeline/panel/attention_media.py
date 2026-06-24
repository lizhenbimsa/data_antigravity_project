"""
42_panel_attention_media.py — 金融科技注意力指数与媒体异质性
==========================================================

功能:
  - 金融科技公众注意力指数 (主锚 Fang & Peress 2009, JF; 对照 Da et al. 2011)
  - 媒体信息中介异质性 (九维度分析)

拆分自: 40_build_panel.py (L1207-1631)
"""

import csv
import json
import os
import platform
import sys
import time

import numpy as np
import pandas as pd

# 日志富集 (2026-06-24): 全部非整数日志数字统一经 sig4/pct4 渲染为 4 位有效数字
# (单一事实源 = core/logging.py)。整数/计数仍用 :,d。
from news_process.core.logging import pct4, sig4

# Phase 2a: 取代旧的 importlib.spec_from_file_location 反射,改为正规子包 import。
from news_process.pipeline.panel.encode import (
    CONFIG,
    FILENAMES,
    OUTPUT_DIR,
    logger,
)
from news_process.pipeline.panel.verified_universe import (
    parquet_has_columns,
    restrict_to_verified,
)

# ── 停刊检测的情感列前缀（动态发现用） ──
# 覆盖: LLM 投票 + 各大模型 + 词典法 + BERT
_SCORE_PATTERNS = [
    'llm_vote_score_', 'gpt54nano_score_', 'gemini31_score_',
    'deepseekv4_score_',  # v3: 从 claude4h_score_ 重命名 (反映真实身份: DeepSeek V4 Flash;
                          # fix(omni-g-panel-export-01, 2026-06-11): 原注 "DeepSeek Grok 4.1"
                          # 自相矛盾 — Grok 是 xAI 模型, 单一事实源 config/sentiment.yaml)
    'jiang_2021_score_', 'yao_2021_score_', 'bian_2021_score_',
    'du_2022_score_', 'you_2018_score_',
    # v3.10.0 \u7b2c 6 \u90e8 L&M 2011 JF \u4e2d\u6587\u4e3b\u8bd1 (\u5217\u524d\u7f00\u522b\u540d 'loughran', \u6743\u5a01 =
    # tone_words.DICT_COLUMN_ALIAS / encode.DICT_NAMES)\u3002fix(2026-06-20): \u6b64\u524d\u672c\u524d\u7f00\u8868
    # \u6f0f\u5217 loughran (\u65b0\u589e\u7b2c 6 \u90e8\u65f6\u672a\u540c\u6b65), \u81f4 exc_*(\u505c\u520a\u7a33\u5065\u6027; \u76d8\u9762 T=2 \u5373\u7f3a 12 \u5217) \u4e0e
    # bal_*(\u5e73\u8861\u5a92\u4f53; T=18 \u5168\u91cf\u540c\u7406, T=2 \u5e73\u8861\u5b50\u96c6\u4e3a\u7a7a\u6545\u6682\u4e0d\u663e) \u4e24\u65cf loughran \u4e0e\u5176\u4f59 5 \u90e8
    # (jiang/yao/bian/du/you) \u4e0d\u5bf9\u79f0\u3002\u8865\u9f50\u540e\u516d\u90e8\u8d70\u5b8c\u5168\u76f8\u540c\u7684\u52a8\u6001\u53d1\u73b0\u8def\u5f84 (\u5b9e\u6d4b\u4ea7 12 \u4e2a
    # exc_loughran_*, \u540e\u7f00\u7ed3\u6784\u4e0e exc_jiang_2021_* \u5168\u7b49)\u3002
    'loughran_score_',
    'finbert_cn_\u6b63\u9762_', 'fin_sent_zh_\u6b63\u9762_',
    'finbert2_\u6b63\u9762_',
]


def _log_attention_substep_banner(step_tag: str, title: str, refs: list) -> None:
    """called-by-runner 子步骤 banner (日志富集, 2026-06-24, golden-safe)。

    本模块是 panel runner 在 步骤 6b/6b-2/6c 调用的库函数 (无独立 main()/run_stage(),
    复用 encode.logger 写入共享的 40_panel_export_main 日志)。按 ENRICHMENT_PLAYBOOK §0.5
    的 called-by-runner 约定: 不重复打 runner 入口已负责的 ENV/CONFIG 全块, 仅在每个被调
    入口函数起始处打一个**子步骤 banner** —— 步骤名 + 运行环境指纹一行 + 方法论依据引文
    (Author (Year). Journal, vol(issue), pages. DOI, 逐字取自经核验注册表)。纯日志, 不改
    任何写盘值/schema/控制流 (golden-safe)。

    Args:
        step_tag: 步骤标签 (如 '6b' / '6b-2' / '6c')。
        title:    子步骤一句话功能 (中文)。
        refs:     方法论引文串列表 (APA-7 + DOI, 逐字取自 VERIFIED_REFERENCES.md)。
    """
    try:
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info("=" * 60)
        logger.info(f"步骤 {step_tag}: {title}")
        logger.info(f"  🧭 环境: Python {sys.version.split()[0]} | {platform.platform()} | "
                    f"CPU={os.cpu_count()} | PID={os.getpid()} | "
                    f"RUN_ID={_run_id or '(未设置)'} | 纯 CPU/$0 (无 LLM·API)")
        logger.info(f"  📁 模块: {os.path.abspath(__file__)}")
        logger.info(f"  📂 输出目录: {OUTPUT_DIR}")
        logger.info("  📖 方法论依据 (Author (Year). Journal, vol(issue), pages. DOI):")
        for _r in refs:
            logger.info(f"     · {_r}")
        logger.info("=" * 60)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  子步骤 banner 打印失败 (不影响处理): {e}")


def detect_defacto_cessation(df, logger, output_dir, threshold_gap=2):
    """数据驱动 + NPPA 交叉验证的隐性覆盖退出 (de-facto coverage cessation) 检测。

    构念措辞修正 fix(omni-g-attention-03, 2026-06-11): 传入的 df 是银行-fintech 文章
    子集 (runner.py df_exploded), first/last_year 度量的是媒体**退出银行-fintech 话题
    覆盖** (topic exit), 而非经证实的报纸停刊 — 媒体可能仍在正常出版只是不再覆盖该话题。
    三点诚实披露 (latent, T=18 全量语料下显著):
      (a) 排除集 ceased_all = confirmed ∪ suspected — NPPA 交叉验证仅改报告标签,
          **未经 NPPA 证实的 suspected 全量进入排除集**;
      (b) n_articles 按 article × bank 行计数 (多银行文章重复计入), 非 docid 去重;
      (c) 下游 ceased_media_frac / exc_* / n_articles_exc 应解读为"疑似退出覆盖媒体"
          稳健性口径 (保守剔除), 不可在论文中表述为严格停刊 (publication cessation) 口径。

    学术基础:
      报纸停刊导致地方企业监督真空，显著增加公司违规行为
      (Heese et al., 2022, JFE) 及公共财政成本 (Gao et al., 2020, JFE)。
      在以媒体情感为核心变量的面板研究中，必须识别并控制
      因媒体来源消失引入的样本选择偏误 (Wooldridge, 2010, Ch.19)。
      本实现以"话题覆盖退出"为停刊的保守代理 (proxy), 见上方措辞修正。

    算法:
      1. 计算每家媒体的 first_year, last_year, n_articles (银行-fintech 子集口径)
      2. 标记 last_year < sample_max - threshold_gap 为疑似覆盖退出
      3. NPPA 交叉验证: confirmed / suspected / nppa_only / active (仅标签, 不收窄排除集)
      4. 返回 ceased_media_set (confirmed ∪ suspected)

    References:
      Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). JFE, 145(2),
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

    # fix(omni-g-attention-03, 2026-06-11): 日志措辞与构念对齐 (话题覆盖退出代理,
    # suspected 未经 NPPA 证实仍进排除集)
    logger.info(f"  覆盖退出检测 (停刊代理, fintech 子集口径): "
                f"confirmed={len(confirmed)}, "
                f"suspected={len(suspected)} (未证实, 仍入排除集), "
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

    语义变更披露 fix(omni-g-attention-04, 2026-06-11): "全程在刊"判据由端点
    (first_year≤start ∧ last_year≥end) 改为窗口内**逐年覆盖** (每年都有报道);
    且语料域为银行-fintech 文章子集, "在刊"实指"该年有银行-fintech 报道"。

    学术基础:
      在非平衡面板中，媒体来源的进入-退出可能引入样本选择偏误。
      通过构建"全程在刊"的平衡媒体子集，检验基准结果是否受
      幸存者偏差驱动 (Wooldridge, 2010, §19.9.3)。

    References:
      Wooldridge, J. M. (2010). §19.9.3 Attrition. MIT Press.
      Engelberg & Parsons (2011). JF, 66(1), 67-97.
        https://doi.org/10.1111/j.1540-6261.2010.01626.x
    """
    for start_year, end_year, suffix in ROBUSTNESS_WINDOWS:
        df_w = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
        # fix(omni-g-attention-04, 2026-06-11): 平衡判据改逐年覆盖 — 旧端点判据
        # (first_year≤start ∧ last_year≥end, 无逐年检查) 会把间歇媒体 (如 2007 与
        # 2024 各一篇、中间年份全缺) 误纳入"平衡"子集, 与 Wooldridge §19.9.3 每期
        # 观测的平衡面板定义不符 (latent: 盘上 T=2 无满足者, T=18 全量触发)。
        # 窗口内 distinct year 数 == 窗口长度 ⟺ 每年都有报道。
        _window_len = end_year - start_year + 1
        _years_covered = df_w.groupby('媒体(中文)')['year'].nunique()
        balanced = _years_covered[_years_covered == _window_len].index
        df_b = df_w[df_w['媒体(中文)'].isin(balanced)]

        if len(df_b) == 0:
            logger.info(f"  窗口 {suffix}: 无平衡媒体数据, 跳过该稳健性窗口")
            continue

        # (D.a) 三轨道全局情感均值 (平衡子集; full/ctx/ss)
        # _ss = 银行+金科同句共现轨 (llm_vote_score_ss, 文章级 content_ss 派生);
        # 缺列 (ss 未落盘) 时下方 `if src in df_b.columns` 守卫优雅跳过。
        for track in ['_full', '_ctx', '_ss']:
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
                    f"3 轨道 (full/ctx/ss) + {len(_bal_cols)} 全方法列")

    return panel

# ============================================================================
# 6b. 金融科技公众注意力指数 (主锚 Fang & Peress 2009, JF; 对照 Da et al. 2011)
# ============================================================================

# 小地理单元最低文章数阈值 (低于此值的 geo×year 不参与指数计算)
_ATTN_MIN_ARTICLES = 5


def _validate_attention_treatments(panel: pd.DataFrame) -> None:
    """校验 P2 attention 处理变量值域 (仿 _validate_attention_index 的 between(0,1) 模式)。

    三轨 (full/ctx/ss): _ss = 银行+金科同句共现轨; index/density/sd 各产 _ss 孪生
    (源 fintech_intensity_score_ss, stage 14 三轨化), 缺列时下方 `if col not in
    panel.columns: continue` 守卫优雅跳过 (graceful skip)。
    """
    bounded = {
        'attention_index_full': (0.0, None), 'attention_index_ctx': (0.0, None),
        'attention_index_ss': (0.0, None),
        'attention_pct_full': (0.0, 1.0), 'attention_disp_full': (0.0, 1.0),
        'attention_attr_share': (0.0, 1.0),
        'attention_intensity_density_full': (0.0, None),
        'attention_intensity_density_ctx': (0.0, None),
        'attention_intensity_density_ss': (0.0, None),
        'attention_intensity_sd_full': (0.0, None),
        'attention_intensity_sd_ctx': (0.0, None),
        'attention_intensity_sd_ss': (0.0, None),
    }
    for col, (lo, hi) in bounded.items():
        if col not in panel.columns:
            continue
        v = panel[col].dropna()
        if len(v) == 0:
            logger.warning(f"  {col}: 全为 NaN")
            continue
        ok = (v >= lo - 1e-9).all() and (hi is None or (v <= hi + 1e-9).all())
        if ok:
            logger.info(f"  ✓ {col}: n={len(v):,} mean={sig4(v.mean())} "
                        f"[{sig4(v.min())}, {sig4(v.max())}]")
        else:
            rng = f"[{lo}, {hi}]" if hi is not None else f"[{lo}, +inf)"
            logger.error(f"  ✗ {col}: 越界 [{sig4(v.min())}, {sig4(v.max())}], 期望 {rng}")


def compute_attention_treatments(panel: pd.DataFrame) -> pd.DataFrame:
    """P2 bank_fintech_attention 处理变量物化。

    ⚠ 锚点更正 (metric-audit 2026-06-10): 主处理 attention_index = ln(1+Σ intensity) 是
    **extensive 累积曝光**(未按文章数/token 归一), 对应 Fang & Peress (2009 JF) 式覆盖量,
    **不是** Hassan et al. (2019 QJE) 的 intensive 归一化份额 (PRisk = 命中 bigram / 总 bigram)。
    若要严格对齐 Hassan QJE intensive 曝光, 应以同函数内的 attention_pct / attention_intensity_density
    (N_ft/N_all 或强度密度) 作 spec primary。attention_index 当前应表述为 extensive 覆盖加权曝光。

    去重口径披露 (预处理去重对关注度指标的影响, 文献依据 2026-06-13):
      本函数全部计数/强度均建立在 stage 00 去重后语料上 (精确去重 + MinHash LSH
      Jaccard≥0.8 + 5 工作日窗口, 保留首发; 见 pipeline/preprocess/dedup.py)。顶刊
      共识: 去重与否取决于构念 —
      ① "信息到达"构念应去重 — 通稿/转载不携带新信息, 计入会系统性高估关注度
         (Tetlock 2011 RFS, "All the News That's Fit to Reprint": 陈旧转载非新信息;
          Hassan/Hollander/van Lent/Tahoun 2019 QJE, doi:10.1093/qje/qjz021:
          文本内份额归一化隐含排斥机械重复计数)。本函数的 attention_index /
          attention_pct / density 属此类, 故用去重基 ✓。
      ② "传播广度/可见度"构念不应去重 — 转载本身就是构念
         (Bushee/Core/Guay/Hamm 2010 JAR press dissemination,
          doi:10.1111/j.1475-679X.2009.00357.x; Fang & Peress 2009 JF coverage 计数,
          doi:10.1111/j.1540-6261.2009.01493.x); 该口径由
          falsification/controls.py::nf_media_breadth 以去重**前**物理行集另行实现,
          勿在本函数混用。
      ③ 时间归属: 跨期转载若保留后发副本日期会错配 bank-year — 去重层已按
         "日期升序保留首发" 消除 (fix omni-g-preprocess-06)。
      ⚠ 含义: 水平类计数 (n_fintech_articles 等) 对去重参数 (Jaccard 0.8 / 5 工作日)
        敏感, 论文须披露去重规则与剔除比例, 并配阈值敏感性稳健性; 份额类
        (attention_pct) 分子分母同基, 去重影响部分相消但非完全免疫。
        阈值敏感性已由 panel/dedup_sensitivity.py (步骤 6b-3) 物化为 attention_*_jXXwY
        变体列; 注意其两处口径限定 (见该模块 docstring METHOD-1/2): 它是"生产去重
        之上的更严两阶段近似"(非 raw-direct 等价), 且只在银行新闻子集重判重 (跨语料
        近似重复不可见)。
      白话: 一条新闻被 50 家网站转载 — 测"发生了多少事"只能算 1 件 (本函数口径,
        不去重会虚增); 测"传得多广"恰恰要数 50 次 (nf_media_breadth 口径)。两套
        口径并存、各管各的, 不是矛盾而是分工。

    产出 spec 钦定 4 列 + 三轨/派生 (三轨 full/ctx/ss = 互为稳健性, 用户裁定 2026-06-05;
    third-track-ss 2026-06-14; _ss = 银行+金科同句共现轨, 源 fintech_intensity_score_ss):
      attention_index_full / _ctx / _ss                   ln(1+Σ intensity) 累积曝光强度 (TRI-TRACK)
      attention_pct_full                                  N_ft/N_all fintech 议程份额 (track-agnostic 单轨)
      attention_intensity_density_full / _ctx / _ss       Σintensity/N_all 强度加权密度 (TRI; 值域[0,+∞) 故非"share"名, B3)
      attention_disp_full                                 跨媒体 outlet 集中度 HHI (高值=集中=低分散, 勿按
                                                          "dispersion"反向解读符号; vectorized, track-agnostic 单轨, H4)
      attention_intensity_sd_full / _ctx / _ss            篇间强度二阶矩 (disp 真三轨; N<2→NaN, H1)
      attention_gap_full_ctx                              mean(full−ctx) full 与 ctx 之差归因借位 (机制变量;
                                                          gap 有意仅锚定 full/ctx 归因窗口对照, ss 不产 gap 孪生)
      attention_attr_share                                Σctx/(Σctx+Σfull) 有界归因占比 (结构性[0,1]无删失, B4 修订;
                                                          attr_share 锚定 full/ctx 归因比, ss 不产 share 孪生)

    语义变更披露 fix(omni-g-attention-01/08, 2026-06-11): attention_attr_share 由
      clip(Σctx/Σfull, 0, 1) 改为 Σctx/(Σctx+Σfull) — 旧比值的分子非分母嵌套子集
      (full 与 ctx 各自做文长归一化, ctx 短文本密度合法更高; attr_share 锚定 full/ctx 归因比,
      不涉 ss), 结构上可 >1, clip 把 11.5% 面板值
      右删失到 1.0; 新构造为同归一化口径的有界 share (= r/(1+r) 单调变换, 保序无删失)。
      另: attention_disp_full 是集中度 (HHI) 非分散度 — fix(omni-g-attention-06)。
      n_fintech_articles / n_outlets                      extensive baseline / HHI 可算性诊断

    回归用法: index/density/sd 各产 _full/_ctx/_ss, main=full、robustness=ctx/ss 分离复跑,
      三轨不同进一个 RHS (三轨各自 just-identified 并排, 严禁 full×ctx×ss 混进同一 over-id Hansen J)。

    防选择偏差 (B1/B2) + verified 域门控 (panel-universe-consistency-audit 2026-06-13,
      ATT-1, 含同函数 HHI 分支): 分子(强度/计数, 取自 15_fintech_intensity)与 HHI 的 outlet 分布
      (取自 12_fintech_news_full is_fintech 子集)经 (docid,target_bank) semi-join 收敛到
      stage-21 verified 集 (24_herd_decay; 与面板政策对齐族 runner.py:_filter_to_verified_universe
      同域, 剔除约 26.8% 被 stage 21 判伪的非真实银行-金融科技文章)。⚠ 而 **分母 N_all +
      全集脊柱 universe** 取自 12_fintech_news_full 全部银行新闻 (含非 fintech), **保持未门控**
      (非 fintech 行从不经 stage 21 验证, 物理不可门控; Fang-Peress 关注度分母; attention_pct =
      已验证 fintech / 全部银行新闻 才是干净的议程份额)。在 12_full 全 bank-year 全集上 LEFT-join
      分子, 零-(verified-)fintech bank-year: index/pct/density → 0 (真零曝光),
      disp/sd/gap/share → NaN (无报道无离散度/借位)。时间维方法 (Da异常/AR/burstiness/月度) 全量后
      opt-in, 此处不产 (T=2 试跑样本不可估, H2)。
      三轨 ss 自动继承门控 (third-track-ss): _ss 列源 fintech_intensity_score_ss 与
      full/ctx 同处经 restrict_to_verified 门控的 s14 帧, semi-join 按 (docid,target_bank)
      track-agnostic → ss 列零额外门控代码即落入同一 verified 宇宙 (与 §⑪ 平价审计一致)。

    ⚠ 顶刊披露 (P2 data/sample): 门控后本族估计样本宇宙 = stage-21 verified 集
      (N≈857 article-bank pairs, 较 1170 候选集剔除约 26.8% LLM 判伪文章); 论文须在
      data/sample 段与 Table 1 注报告该 verified 宇宙与剔除率 (与去重披露义务同级)。
    ⚠ 范围 (勿混): 地理注意力指数族 (compute_fintech_attention_index 的 ft_attn_yr/prov/city
      + 总量孪生 ft_vol_*) 是**另一支**, 其 is_fintech_news 分子已于 2026-06-18 (审计 ATT-2)
      在 compute_fintech_attention_index 内 docid 去重前经同口径 restrict_to_verified
      (docid,target_bank) 门控收敛到同一 verified 集 — 与本函数 (ATT-1) 已对齐, 不再有
      "未门控/deferred" 缺口。本函数 (含 HHI 分支) 仅覆盖 firm-level attention 处理变量族。

    NaN 非对称契约 (须知): panel 是 balance_panel 笛卡尔积, 可含 12_full universe 之外的
      bank-year (该银行该年**完全无银行新闻**, has_coverage=0)。这些行最终 panel.merge LEFT-join
      天然得**全 NaN** (含 index/pct/density)。这与 in-universe 零-fintech 行 (有新闻但无 fintech →
      index/pct=0) **刻意不对称**: 无新闻=注意力不可测 (NaN), 有新闻但零 fintech=真零曝光 (0)。
      回归中前者 listwise 删除 (正确)、后者保留为信息性零。(test_attention_treatments
      test_panel_superset_rows_are_nan 锁定此契约)
    """
    s14_path = os.path.join(OUTPUT_DIR, FILENAMES.get(
        'output_14_fintech_intensity', '15_fintech_intensity.parquet'))
    f12_path = os.path.join(OUTPUT_DIR, FILENAMES.get(
        'output_12_fintech_full', '12_fintech_news_full.parquet'))
    if not (os.path.exists(s14_path) and os.path.exists(f12_path)):
        logger.warning("  15_fintech_intensity / 12_fintech_news_full 缺失, 跳过 "
                       "attention 处理变量物化")
        return panel

    _t0_treat = time.time()
    # fix(omni-g-papers-misc-09, 2026-06-11): 日志锚点与本函数 docstring 锚点更正对齐
    _log_attention_substep_banner(
        '6b-2',
        'P2 attention 处理变量 (Fang-Peress 2009 JF extensive 覆盖; Hassan 2019 仅限 '
        'pct/density 归因; 三轨 full/ctx/ss=互为稳健性)',
        [
            'Fang, L., & Peress, J. (2009). Media coverage and the cross-section of '
            'stock returns. The Journal of Finance, 64(5), 2023-2052. '
            'https://doi.org/10.1111/j.1540-6261.2009.01493.x  (extensive 覆盖加权曝光主锚)',
            'Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). '
            'Firm-level political risk: Measurement and effects. The Quarterly '
            'Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021'
            '  (intensive 归一化份额; 仅限 attention_pct/density)',
        ],
    )
    logger.info("  ⚙ 运行配置: _ATTN_MIN_ARTICLES=%d | 三轨={full,ctx,ss} | "
                "verified 域门控=on (semi-join 24_herd_decay, 剔 ~26.8%% 判伪)",
                _ATTN_MIN_ARTICLES)
    logger.info(f"  📂 输入: 分子={s14_path} | 分母/全集={f12_path}")

    s14 = pd.read_parquet(s14_path)
    # full/ctx 为硬依赖 (缺则整族跳过); ss 为软依赖 — stage 14 三轨化后才落盘
    # fintech_intensity_score_ss, 缺列时仅 ss 轨优雅跳过 (graceful skip), full/ctx 照常。
    need_intensity = {'fintech_intensity_score_full', 'fintech_intensity_score_ctx'}
    if not need_intensity.issubset(s14.columns):
        logger.warning(f"  15_fintech_intensity 缺强度列 {need_intensity - set(s14.columns)}, "
                       f"跳过 attention 处理变量")
        return panel
    _has_ss = 'fintech_intensity_score_ss' in s14.columns  # 三轨 ss 软门控
    # fix(panel-universe-consistency-audit 2026-06-13, ATT-1/ATT-2): 防御式取 docid
    # (verified 域门控需要)。合成测试帧无 docid → 不投影该列, 后续 restrict_to_verified
    # 因缺键 fail-open 未门控 (旧行为不变), 不触发 ArrowInvalid。
    _f12_cols = ['target_bank', '日期', 'is_fintech_news', '媒体(中文)']
    if parquet_has_columns(f12_path, ['docid']):
        _f12_cols = ['docid'] + _f12_cols
    f12 = pd.read_parquet(f12_path, columns=_f12_cols)

    GK = ['target_bank', 'year']
    for df in (s14, f12):  # year 派生 (镜像 compute_fintech_attention_index (:609-611) 的 year 派生, 防 groupby KeyError)
        df['year'] = pd.to_datetime(df['日期'], errors='coerce').dt.year
        df.dropna(subset=['year'], inplace=True)
        df['year'] = df['year'].astype(int)

    # ── 全 bank-year 全集 (防 B1 选择偏差): 来自 12_full 全部银行新闻 ──
    universe = f12.drop_duplicates(GK)[GK].copy()
    n_all = f12.groupby(GK).size().rename('_n_all')

    # ── 分子: 15_fintech_intensity (有 full/ctx/ss 三轨强度分) ──
    # fix(panel-universe-consistency-audit 2026-06-13, ATT-1): 分子收敛到 stage-21
    # verified 集 (与政策对齐族 runner.py:_filter_to_verified_universe 同域), 剔除约
    # 26.8% 被 stage 21 判伪文章。⚠ 仅门控分子; 上方 universe/n_all (分母与全集脊柱)
    # 取自全部银行新闻 12_full, 保持未门控 (保 NaN-vs-0 契约与议程份额语义)。
    s14 = restrict_to_verified(s14, OUTPUT_DIR, FILENAMES,
                               logger=logger, label='attention.s14')
    g = s14.groupby(GK)
    num = pd.DataFrame({
        'sum_full': g['fintech_intensity_score_full'].sum(),
        'sum_ctx': g['fintech_intensity_score_ctx'].sum(),
        'mean_full': g['fintech_intensity_score_full'].mean(),   # NaN-keep (零fintech无gap)
        'mean_ctx': g['fintech_intensity_score_ctx'].mean(),
        'sd_full': g['fintech_intensity_score_full'].std(),       # ddof=1, N=1→NaN (H1)
        'sd_ctx': g['fintech_intensity_score_ctx'].std(),
        'n_ft': g.size(),
    })
    # 三轨 ss (third-track-ss): _ss = 银行+金科同句共现轨; 仅 stage 14 已落盘
    # fintech_intensity_score_ss 时聚合 sum/sd (index/density/sd 三轨孪生)。mean_ss 不需
    # (gap=full−ctx 锚定, ss 不产 gap 孪生)。同 g 分组 → ss 与 full/ctx 同 verified 域。
    if _has_ss:
        num['sum_ss'] = g['fintech_intensity_score_ss'].sum()
        num['sd_ss'] = g['fintech_intensity_score_ss'].std()      # ddof=1, N=1→NaN (H1)

    # ── 跨媒体 HHI (vectorized, 防 H4 groupby-apply 性能炸弹) ──
    f12_ft = f12[f12['is_fintech_news'] == True]
    # fix(ATT-1, HHI 分支): HHI/n_outlets 的 outlet 分布同样收敛到 verified 集 (与分子 s14 同域)。
    # (审计 ATT-2 = 另一支 compute_fintech_attention_index ft_attn_*, 已于 2026-06-18 同口径门控, 勿混。)
    # verified ⊆ f12_ft 经盘面实测 → 门控后 f12_ft 的非空 bank-year 集与门控后 s14 恒一致,
    # 保 n_fintech_articles==0 ⇔ disp_hhi=NaN 契约 (test_disp_hhi_bounded / test_zero_fintech_semantics)。
    f12_ft = restrict_to_verified(f12_ft, OUTPUT_DIR, FILENAMES,
                                  logger=logger, label='attention.f12_ft')
    oc = f12_ft.groupby(GK + ['媒体(中文)']).size().reset_index(name='n')
    oc['_tot'] = oc.groupby(GK)['n'].transform('sum')
    oc['_s2'] = (oc['n'] / oc['_tot']) ** 2
    disp = pd.DataFrame({
        'disp_hhi': oc.groupby(GK)['_s2'].sum(),
        'n_outlets': oc.groupby(GK)['媒体(中文)'].nunique(),
    })

    # ── 在全集脊柱上组装 ──
    t = universe.set_index(GK).join(n_all).join(num).join(disp)
    # 分子缺失 (零-fintech bank-year) → 累积/计数填 0 (真零曝光)
    # 三轨 ss: sum_ss 与 sum_full/ctx 同口径填 0 (零曝光真零); sd_ss 保持 NaN。
    _sum_zero_fill = ['sum_full', 'sum_ctx', 'n_ft'] + (['sum_ss'] if _has_ss else [])
    for c in _sum_zero_fill:
        t[c] = t[c].fillna(0)
    t['n_ft'] = t['n_ft'].astype(int)
    # mean/sd/disp/n_outlets 保持 NaN (零-fintech 无离散度/借位)
    # 防御性下界 (W2 复核 LOW): 上游 stage14 IDF 权重在某 fintech 词近全文档时理论可转负
    # (fintech_intensity.py:157 raw_idf=log10(N/(1+df))) → 篇级 score 可负 → sum 可负 →
    # log1p(负) 产 -inf/NaN 破 index/density [0,+∞) 契约, attr_share 符号翻转被 clip 静默掩盖。
    # 当前数据 intensity min=0 未触发, clip 作结构性保证 (no-op on 非负数据)。
    t['sum_full'] = t['sum_full'].clip(lower=0)
    t['sum_ctx'] = t['sum_ctx'].clip(lower=0)
    if _has_ss:
        t['sum_ss'] = t['sum_ss'].clip(lower=0)  # 同 full/ctx 非负防御 (log1p/density 契约)

    t['attention_index_full'] = np.log1p(t['sum_full'])
    t['attention_index_ctx'] = np.log1p(t['sum_ctx'])
    t['attention_pct_full'] = t['n_ft'] / t['_n_all']            # _n_all≥1 (全集来自12_full)
    t['attention_intensity_density_full'] = t['sum_full'] / t['_n_all']
    t['attention_intensity_density_ctx'] = t['sum_ctx'] / t['_n_all']
    # 三轨 ss (third-track-ss): index/density 镜像 full/ctx 口径, 同 _n_all 分母。
    if _has_ss:
        t['attention_index_ss'] = np.log1p(t['sum_ss'])
        t['attention_intensity_density_ss'] = t['sum_ss'] / t['_n_all']
    t['attention_gap_full_ctx'] = t['mean_full'] - t['mean_ctx']  # 零-fintech → NaN
    # fix(omni-g-attention-01/08, 2026-06-11): 旧 Σctx/Σfull 是两种文长归一化密度之比
    # (fintech_intensity.py score = Σ(1+log tf)/(1+log L_d)×w, ctx 文本更短 → 密度合法
    # 更高), 分子非分母的嵌套子集量, 结构上可 >1 (实测 24/157 bank-year, max 1.22),
    # 旧 clip[0,1] 把越界质量右删失到 1.0 (面板 14/122=11.5% 值恰为 1.0) 并破坏删失区
    # 排序 — 系统性测度后果而非浮点边角。改为同归一化口径的有界 ctx 贡献占比:
    # share = Σctx/(Σctx+Σfull) ∈ [0,1] (= r/(1+r), r=ctx/full 的严格单调变换, 保序、
    # 无删失; 0.5 ⇔ full 与 ctx 密度相等, 越大归因越纯)。Σctx+Σfull=0 (零 fintech) → NaN。
    # sums 已在上方 clip(lower=0), share 结构性落 [0,1], 无需 censor clip。
    # codebook.py/export.py 标签同步交由集中重生 (本组不越界编辑)。
    # 白话: ctx 文本短, 按"密度"算强度天然可能比全文还高, 直接拿 ctx/full
    # 做比值会超过 1, 旧做法把超出部分硬剪到 1 反而抹掉了信息。改成
    # "ctx 占两者之和的份额"后数学上必落在 0~1, 大小排序也不变。
    with np.errstate(divide='ignore', invalid='ignore'):
        _share = t['sum_ctx'] / (t['sum_ctx'] + t['sum_full']).replace(0, np.nan)
    t['attention_attr_share'] = _share
    t['attention_disp_full'] = t['disp_hhi']
    t['attention_intensity_sd_full'] = t['sd_full']
    t['attention_intensity_sd_ctx'] = t['sd_ctx']
    if _has_ss:
        t['attention_intensity_sd_ss'] = t['sd_ss']  # 篇间强度二阶矩 ss 孪生 (N<2→NaN, H1)
    t['n_fintech_articles'] = t['n_ft']

    out_cols = [
        'attention_index_full', 'attention_index_ctx', 'attention_pct_full',
        'attention_intensity_density_full', 'attention_intensity_density_ctx',
        'attention_disp_full', 'attention_intensity_sd_full', 'attention_intensity_sd_ctx',
        'attention_gap_full_ctx', 'attention_attr_share',
        'n_fintech_articles', 'n_outlets',
    ]
    # 三轨 ss (third-track-ss): index/density/sd 的 _ss 孪生仅 stage 14 已落盘
    # fintech_intensity_score_ss 时追加 (graceful skip); gap/share/pct/disp 锚定
    # full-ctx 或 track-agnostic, 不产 ss 孪生。
    if _has_ss:
        out_cols += ['attention_index_ss', 'attention_intensity_density_ss',
                     'attention_intensity_sd_ss']
    treat = t.reset_index()[GK + out_cols]

    drop = [c for c in out_cols if c in panel.columns]
    if drop:
        panel = panel.drop(columns=drop)
    panel = panel.merge(treat, on=GK, how='left')

    matched = panel['attention_index_full'].notna().sum()
    logger.info(f"  attention 处理变量: 匹配 {matched:,}/{len(panel):,} bank-year "
                f"({pct4(matched / len(panel))}); 全集脊柱 {len(universe):,} bank-year")
    _validate_attention_treatments(panel)
    logger.info(f"  ⏱ 步骤 6b-2 (attention 处理变量) 墙钟耗时: {sig4(time.time() - _t0_treat)} 秒")
    return panel


def compute_fintech_attention_index(panel: pd.DataFrame) -> pd.DataFrame:
    """构建金融科技公众注意力指数 — 三级地理维度。

    锚点 (claim-fit 已订正, 审计 2026-06-14 CIT-2/3):
      主锚 — Fang, L. & Peress, J. (2009). Media Coverage and the Cross-Section
          of Stock Returns. The Journal of Finance, 64(5), 2023-2052.
          https://doi.org/10.1111/j.1540-6261.2009.01493.x
          → 报纸覆盖率 (coverage ratio) 作为信息中介/关注度的度量, 本指数据此构建。

      对照 (非主锚) — Da, Z., Engelberg, J. & Gao, P. (2011). In Search of
          Attention. The Journal of Finance, 66(5), 1461-1499.
          https://doi.org/10.1111/j.1540-6261.2011.01679.x
          → DEG 以 Google 搜索量 (SVI) 作 *直接* 注意力代理, 并论证报纸覆盖是其取代的
            *间接* 代理。本项目无搜索量数据 (报纸语料), 以报纸覆盖作间接关注度代理,
            DEG 仅作搜索量替代方案的 *对照* 引用, 非本覆盖比值的奠基范式。

    数据源:
      12_fintech_news_full.parquet — 全量银行新闻 (含 is_fintech_news 标记)。
      该文件为 article × bank 粒度。统一作为指数和权重的数据源，
      避免 df_exploded (仅含 fintech 文章) 导致的地理曝露偏差。

    verified 域门控 (ATT-2 修复 2026-06-18, panel-universe-consistency-audit):
      本族比值 ft_attn = 单元 fintech 篇数 / **全部银行新闻**篇数 (Fang-Peress 议程份额),
      故仅门控**分子** (is_fintech_news 计数), 分母 _total 须保持全部银行新闻全集。实现:
      对 fintech 子集按 (docid, target_bank) semi-join 到 stage-21 verified 集
      (24_herd_decay), 把**未通过验证的 fintech 行就地重标为非 fintech** (is_fintech_news=
      False) — 行数不变, 故分母 _total 仍是全部银行新闻、分子 _ft 仅含 verified fintech,
      与 compute_attention_treatments (ATT-1) 同 verified 域, 剔约 26.8% 被 stage 21 判伪。
      该单次重标经 is_fintech_news 向下游传播 (year-level / _build_geo_index 的 _ft /
      _merge LOO 扣减全部 key 于 is_fintech_news==True) → 一处覆盖全部六列。此前该支直读未
      验证 12_full、与 ATT-1 不一致 (审计 ATT-2), 现已修复, 不再 deferred/待决。
      ⚠ **不可**对整个 df_all 做 semi-join: 非 fintech 银行新闻行从不经 stage 21 验证、不在
      24_herd_decay (verified_universe.py:15-18), inner-join 整 df_all 会删全部非 fintech 行
      → 分母塌成 fintech-only → ft_attn≈1 退化。缺 docid (更早 ERROR) / 缺 24_herd_decay 时
      restrict_to_verified 响亮 fail-open → 无重标 → 未门控全集, 不新增回退逻辑。

    去重策略:
      - 计算注意力指数 → 按 docid 去重到唯一文章级 (门控后)
      - 计算银行地理曝露权重 → 不去重 (每个 target_bank 行算一次曝露)

    NaN 语义:
      某 Bank-Year 的全部文章均缺失地理信息时，
      ft_attn_prov / ft_attn_city 为 NaN (不填充)。

    比值 vs 总量 两测度互为稳健性 (2026-06-13, 用户裁定; 互为稳健性同源原则,
    memory dualtrack-is-mutual-robustness):
    # no-ss-track: ft_attn_*/ft_vol_* 族建立在 is_fintech_news 计数上 (无 llm_vote_score),
    # 非情感轨 → 无 full/ctx/ss 三轨分裂; 这里的"两测度"指 比值 vs 总量, 与 §⑥/§⑪ 三轨
    # 化无关 (ATT-2 另一支, 见下方 ⚠ 范围注释)。
      每档 (年/省/市) 除产 **比值** ft_attn_* (= fintech/total, intensive 议程份额,
      ∈[0,1]) 外, 再并行产一个 **总量** ft_vol_* (= ln(1+fintech 覆盖篇数), extensive
      覆盖规模, ∈[0,+∞), Fang & Peress 2009 JF 覆盖计数范式):
        ft_vol_yr   = ln(1 + 当年 fintech 唯一篇数)              (year-level 常量, 无 LOO)
        ft_vol_prov = ln(1 + 曝露加权 LOO fintech 篇数, 省级)     (与 ft_attn_prov 同样本)
        ft_vol_city = ln(1 + 曝露加权 LOO fintech 篇数, 市级)     (与 ft_attn_city 同样本)
      比值对样本规模不敏感但忽略绝对热度; 总量反之。两者分别进各自回归、不同进一
      个 RHS (避免与比值高度共线), 互为稳健性。prov/city 的总量复用与比值**完全相同**
      的 geo×year 单元 / min_articles=5 守卫 / 曝露加权 LOO 映射 → 两测度同非缺样本,
      可直接对照。

    操作序列:
      在 balance_panel() 之后、compute_composite_indicators() 之前调用。

    Returns:
        panel: 附加 ft_attn_yr/prov/city (比值) + ft_vol_yr/prov/city (总量) 六列的面板。
    """
    full_path = os.path.join(OUTPUT_DIR, FILENAMES.get(
        'output_12_fintech_full', '12_fintech_news_full.parquet'))
    if not os.path.exists(full_path):
        logger.warning("  12_fintech_news_full.parquet 不存在, 跳过注意力指数")
        return panel

    _t0_geo = time.time()
    _log_attention_substep_banner(
        '6b',
        '金融科技公众注意力指数 — 三级地理维度 (主锚 Fang & Peress 2009; 对照 Da et al. 2011)',
        [
            'Fang, L., & Peress, J. (2009). Media coverage and the cross-section of '
            'stock returns. The Journal of Finance, 64(5), 2023-2052. '
            'https://doi.org/10.1111/j.1540-6261.2009.01493.x  (主锚: 报纸覆盖率作关注度度量)',
            'Da, Z., Engelberg, J., & Gao, P. (2011). In search of attention. The '
            'Journal of Finance, 66(5), 1461-1499. '
            'https://doi.org/10.1111/j.1540-6261.2011.01679.x  (对照: 直接注意力代理, 本项目以报纸覆盖作间接代理)',
            'Gurun, U. G., & Butler, A. W. (2012). Don\'t believe the hype: Local '
            'media slant, local advertising, and firm value. The Journal of Finance, '
            '67(2), 561-598. https://doi.org/10.1111/j.1540-6261.2012.01725.x  (地理本地媒体偏斜)',
        ],
    )

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

    # ── verified 域门控 (panel-universe-consistency-audit, ATT-2 修复 2026-06-18) ──
    # 地理注意力比值 ft_attn = 单元 fintech 篇数 / **全部银行新闻**篇数 (Fang-Peress 议程份额),
    # 故只能门控**分子** (is_fintech_news 计数), 分母 _total 须保持全部银行新闻全集。
    # ⚠ 不可对整个 df_all 做 semi-join: 非 fintech 银行新闻行从不经 stage 21 验证、不在
    #   24_herd_decay (verified_universe.py:15-18), inner-join 整 df_all 会把全部非 fintech 行
    #   删掉 → 分母 _total 塌成 fintech-only → ft_attn≈1 退化。改为: 仅对 fintech 子集做
    #   verified semi-join, 把未通过验证的 fintech 行就地重标为非 fintech (is_fintech_news=
    #   False) — 行数不变 → 分母 _total 仍是全部银行新闻、分子 _ft 仅含 verified fintech。
    #   该单次重标经 is_fintech_news 向下游传播 (year-level / _build_geo_index 的 _ft /
    #   _merge_geo_index_to_panel 的 LOO 扣减全部 key 于 is_fintech_news==True) → 一处覆盖
    #   全部六列, 与 ATT-1 (compute_attention_treatments) 同 verified 域。
    #   fail-open: 缺 docid 在 :578-590 已更早 ERROR; 缺 24_herd_decay → restrict_to_verified
    #   响亮 fail-open 返回原 fintech 子集 → verified 对集 == 原 fintech 对集 → 无重标 →
    #   未门控全集 (与 ATT-1 同 fail-open 语义), 不新增回退逻辑。
    _ft_mask = df_all['is_fintech_news'] == True
    _ft_verified = restrict_to_verified(
        df_all.loc[_ft_mask], OUTPUT_DIR, FILENAMES,
        keys=['docid', 'target_bank'], logger=logger,
        label='attention.geo_numerator')
    _verified_ft_pairs = set(zip(_ft_verified['docid'], _ft_verified['target_bank']))
    _n_ft_before = int(_ft_mask.sum())
    _keep_ft = pd.MultiIndex.from_arrays(
        [df_all['docid'], df_all['target_bank']]).isin(_verified_ft_pairs)
    df_all['is_fintech_news'] = (df_all['is_fintech_news'] == True).to_numpy() & _keep_ft
    logger.info("  verified 域门控 (ATT-2, 仅分子重标): fintech 篇 %d → %d (分母全集 %d 不变)",
                _n_ft_before, int((df_all['is_fintech_news'] == True).sum()), len(df_all))

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
    # 总量孪生 (互为稳健性): ft_vol_yr = ln(1 + 当年 fintech 唯一篇数) — 绝对覆盖规模,
    # year-level 常量、无 LOO (与 ft_attn_yr 同口径: 宏观年度序列, 不按 bank 留一)。
    idx_yr['ft_vol_yr'] = np.log1p(idx_yr['_ft'])
    idx_yr = idx_yr.reset_index()

    logger.info("  ─── Year-level ───")
    for _, r in idx_yr.iterrows():
        logger.info(f"    {int(r['year'])}: "
                     f"{int(r['_ft']):,}/{int(r['_total']):,} "
                     f"= {sig4(r['ft_attn_yr'])} (议程份额)")

    # 保存中间数据
    _save_attn_index(idx_yr.rename(columns={'_total': 'total_articles',
                                             '_ft': 'fintech_articles'}),
                     '40_attn_index_year')

    panel = panel.merge(idx_yr[['year', 'ft_attn_yr', 'ft_vol_yr']],
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

        # fix(omni-g-attention-05, 2026-06-11): 传入 _total/_ft 全单元计数供 LOO 扣减
        # vol_col: 同一 LOO 映射并行产总量孪生 ft_vol_prov (互为稳健性, 2026-06-13)
        panel = _merge_geo_index_to_panel(
            df_all, panel,
            idx_prov[[prov_col, 'year', '_total', '_ft', 'ft_attn_prov']],
            prov_col, 'ft_attn_prov', vol_col='ft_vol_prov')
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

        # fix(omni-g-attention-05, 2026-06-11): 传入 _total/_ft 全单元计数供 LOO 扣减
        # vol_col: 同一 LOO 映射并行产总量孪生 ft_vol_city (互为稳健性, 2026-06-13)
        panel = _merge_geo_index_to_panel(
            df_all, panel,
            idx_city[[city_col, 'year', '_total', '_ft', 'ft_attn_city']],
            city_col, 'ft_attn_city', vol_col='ft_vol_city')
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

    # ── 📊 关键指标解读 (运行结果信息, 日志富集 2026-06-24) ──
    try:
        logger.info("  📊 关键指标解读 (地理注意力指数族)")
        for _col, _lbl in [('ft_attn_yr', '年度议程份额'),
                            ('ft_attn_prov', '省级 LOO 份额'),
                            ('ft_attn_city', '市级 LOO 份额')]:
            if _col not in panel.columns:
                continue
            _v = panel[_col].dropna()
            if len(_v) == 0:
                logger.warning(f"     · {_col} ({_lbl}): 全为 NaN — 该地理层级无可估样本")
                continue
            _cov = len(_v) / len(panel)
            _mean = _v.mean()
            # 议程份额∈[0,1]: 偏高 (>0.5) 提示 fintech 话题主导, 偏低 (<0.05) 提示稀疏覆盖
            if _mean > 0.5:
                _vd = '偏高 (fintech 话题在该层级新闻中主导)'
            elif _mean < 0.05:
                _vd = '偏低 (fintech 覆盖稀疏, 多数为非 fintech 银行新闻)'
            else:
                _vd = '正常区间'
            logger.info(f"     · {_col} ({_lbl}): 覆盖 {len(_v):,}/{len(panel):,} "
                        f"({pct4(_cov)}), 均值={sig4(_mean)} → {_vd}")
        for _col, _lbl in [('ft_vol_yr', '年度总量'),
                           ('ft_vol_prov', '省级 LOO 总量'),
                           ('ft_vol_city', '市级 LOO 总量')]:
            if _col not in panel.columns:
                continue
            _v = panel[_col].dropna()
            if len(_v) == 0:
                continue
            logger.info(f"     · {_col} ({_lbl}, ln(1+篇数)): 覆盖 {len(_v):,}/{len(panel):,}, "
                        f"均值={sig4(_v.mean())} [{sig4(_v.min())}, {sig4(_v.max())}]")
        logger.info(f"  ⏱ 步骤 6b (地理注意力指数) 墙钟耗时: {sig4(time.time() - _t0_geo)} 秒")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  地理注意力指数结果解读打印失败 (不影响处理): {e}")

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
    # 使用数据版本控制保存
    from news_process.core.data_versioning import save_parquet_with_metadata
    # 血缘修复 (audit-fixes 2026-05-29): 注意力指数的唯一数据源是
    # 12_fintech_news_full.parquet (本模块 :254 唯一 read_parquet); 此前误记
    # 24_herd_decay 属 mis-attribution — 校正为真实源, 否则完整性校验验的是
    # 一个无关文件而真实源无保护.
    input_file = os.path.join(CONFIG['paths']['output_dir'],
                              CONFIG['filenames'].get('output_12_fintech_full',
                                                      '12_fintech_news_full.parquet'))
    save_parquet_with_metadata(
        df=df,
        output_path=parquet_path,
        stage_name="40_panel_export_main",
        config=CONFIG,
        input_files=[input_file],
    )
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    logger.info(f"    已保存: {basename} ({len(df)} 行)")


def _merge_geo_index_to_panel(df_all, panel, idx_geo,
                               geo_col, target_col,
                               min_articles=_ATTN_MIN_ARTICLES,
                               vol_col=None):
    """将地理注意力指数通过曝露度加权合并到 Bank-Year 面板 (leave-one-out)。

    语义变更披露 fix(omni-g-attention-05, 2026-06-11): geo×year 指数由全单元值改为
    逐 (geo, year, bank) leave-one-out — 剔除提及焦点银行的唯一文章后再取比值,
    消除"银行自身 fintech 报道越多 → 其 ft_attn_* 机械越高"的反射性内生
    (市级 min_articles=5 小单元曾可被单一银行支配, own-share 实测 max=0.875)。

    合并策略 (Exposure-weighted leave-one-out average):
      1. df_all 中每行 = (article, target_bank), 含媒体来源地
      2. 为每行计算其来源地的 LOO attention index:
         (cell_ft − own_ft) / (cell_total − own_total), 唯一 docid 口径;
         LOO 分母 < min_articles → NaN (沿用小样本噪声守卫, 与 _build_geo_index
         的 cell 级过滤同理 — 自身支配单元剔除后剩余样本过小同样产 0/1 噪声)
      3. 按 (target_bank, year) 取均值
         → "报道该银行的全部媒体所在地区的 (剔除自身报道后) 平均金融科技关注度"

    注意: 权重基于 df_all (含 fintech + non-fintech 全量银行新闻),
       确保地理曝露反映银行的真实媒体环境, 而非仅金融科技新闻的分布。

    总量孪生 vol_col (互为稳健性, 2026-06-13): 给定 vol_col 时, 复用**完全相同**的
      LOO 分子 (cell_ft − own_ft) 与 **同一 min_articles 守卫** (而非除以分母), 按
      (target_bank, year) 曝露加权均值后取 ln(1+·) → 绝对覆盖总量列。与比值 target_col
      共享分母守卫 → 两列同非缺样本 (互为稳健性可比性前提); 曝露加权天然由 df_all 未
      去重的 article×bank 行频次提供 (报道越多的地区在均值里权重越大)。

    Args:
        idx_geo: 含 [geo_col, 'year', '_total', '_ft', target_col] 的指数表
                 (_total/_ft 为该 geo×year 全单元唯一文章计数, 供 LOO 扣减)。
        vol_col: 可选; 给定则并行产 ln(1+LOO fintech 篇数) 总量孪生列 (默认 None →
                 仅产比值, 行为与历史完全一致, 保持向后兼容)。

    Returns:
        panel: 附加 target_col (+ vol_col, 若给定) 列的面板。
    """
    # 1. 选取需要的列并清洗
    work = df_all[['docid', 'target_bank', 'year', geo_col,
                   'is_fintech_news']].copy()
    work = work.dropna(subset=[geo_col])

    # 2. fix(omni-g-attention-05, 2026-06-11): 该 geo×year×bank 自身文章计数
    #    (唯一 (docid, bank) 口径, 与 _build_geo_index 的 df_unique 分母同口径)
    own = work.drop_duplicates(subset=['docid', 'target_bank'])
    own_tot = (own.groupby([geo_col, 'year', 'target_bank'])
               .size().reset_index(name='_own_total'))
    own_ft = (own[own['is_fintech_news'] == True]
              .groupby([geo_col, 'year', 'target_bank'])
              .size().reset_index(name='_own_ft'))

    # 3. 匹配地理指数 (含全单元 _total/_ft) + 自身计数 → 逐行 LOO 指数
    work = work.merge(idx_geo, on=[geo_col, 'year'], how='left')
    # left join miss → 该 geo×year 被 min_articles 过滤掉, 值为 NaN, 不参与均值
    work = work.merge(own_tot, on=[geo_col, 'year', 'target_bank'], how='left')
    work = work.merge(own_ft, on=[geo_col, 'year', 'target_bank'], how='left')
    _loo_den = work['_total'] - work['_own_total'].fillna(0)
    _loo_num = work['_ft'] - work['_own_ft'].fillna(0)
    # 防御性下界 (review 2026-06-13, 同 compute_attention_treatments 的 clip 先例):
    # _loo_num 的非负性依赖一条未显式断言的不变量 — docid 内 geo 与 is_fintech 恒定
    # (⇒ own ⊆ cell ⇒ own_ft ≤ cell_ft)。当前语料经核 0 例违反 → clip 为 no-op (min=0)。
    # 但若未来数据源破坏该不变量 (同 docid 跨 geo/标记), own_ft>cell_ft 会令 _loo_num<0,
    # 进而比值转负 (逃过 [0,1] 校验) 且 ln1p(负)→NaN 污染总量孪生; clip 从根上封死。
    _loo_num = _loo_num.clip(lower=0)
    with np.errstate(divide='ignore', invalid='ignore'):
        # NaN >= min_articles → False → NaN (被 cell 级过滤的单元保持 NaN)
        work[target_col] = np.where(
            _loo_den >= min_articles, _loo_num / _loo_den, np.nan)
        if vol_col is not None:
            # 总量孪生: LOO fintech 篇数 (分子, 不除分母); 同 min_articles 守卫 →
            # 与比值 target_col 同 NaN 模式 / 同非缺样本 (互为稳健性可比性)。
            work['_loo_ft'] = np.where(
                _loo_den >= min_articles, _loo_num, np.nan)

    # 4. Bank-Year 均值 (vol_col 给定时一并聚合 LOO 篇数, 再 ln(1+·))
    _agg = [target_col] + (['_loo_ft'] if vol_col is not None else [])
    bank_yr = (work.groupby(['target_bank', 'year'])[_agg]
               .mean().reset_index())
    if vol_col is not None:
        # 曝露加权 LOO 篇数均值 → ln(1+·) (extensive 总量, 镜像 attention_index 口径)
        bank_yr[vol_col] = np.log1p(bank_yr['_loo_ft'])
        bank_yr = bank_yr.drop(columns=['_loo_ft'])

    # 5. 安全合并到 panel (避免 .values 位置赋值的脆弱性)
    _out_cols = [c for c in [target_col, vol_col] if c is not None]
    drop = [c for c in _out_cols if c in panel.columns]
    if drop:
        panel = panel.drop(columns=drop)
    panel = panel.merge(bank_yr[['target_bank', 'year'] + _out_cols],
                        on=['target_bank', 'year'], how='left')

    matched = panel[target_col].notna().sum()
    logger.info(f"    {target_col}: 匹配 {matched:,}/{len(panel):,} "
                f"({pct4(matched / len(panel))}) [leave-one-out]")
    if vol_col is not None:
        vmatched = panel[vol_col].notna().sum()
        logger.info(f"    {vol_col}: 匹配 {vmatched:,}/{len(panel):,} "
                    f"({pct4(vmatched / len(panel))}) [LOO 总量 ln(1+篇数)]")
    return panel


def _validate_attention_index(panel):
    """校验注意力指数变量。"""
    for col in ['ft_attn_yr', 'ft_attn_prov', 'ft_attn_city']:
        if col not in panel.columns:
            continue
        valid = panel[col].dropna()
        if len(valid) == 0:
            logger.warning(f"  {col}: 全为 NaN")
            continue
        if not valid.between(0, 1).all():
            logger.error(f"  ✗ {col}: 含超出 [0,1] 的值!")
        else:
            logger.info(f"  ✓ {col}: mean={sig4(valid.mean())}, "
                         f"std={sig4(valid.std())}, "
                         f"[{sig4(valid.min())}, {sig4(valid.max())}]")

    # 总量孪生校验 ([0, +∞), ln(1+篇数) 故 ≥0; 非 share 不查上界 1)
    for col in ['ft_vol_yr', 'ft_vol_prov', 'ft_vol_city']:
        if col not in panel.columns:
            continue
        valid = panel[col].dropna()
        if len(valid) == 0:
            logger.warning(f"  {col}: 全为 NaN")
            continue
        if (valid < -1e-9).any():
            logger.error(f"  ✗ {col}: 含负值 (ln(1+篇数) 应 ≥0)!")
        else:
            logger.info(f"  ✓ {col}: mean={sig4(valid.mean())}, "
                         f"std={sig4(valid.std())}, "
                         f"[{sig4(valid.min())}, {sig4(valid.max())}]")

    # year-level 常量校验 (比值与总量两个 year 档均应同年常量)
    for _yc in ['ft_attn_yr', 'ft_vol_yr']:
        if _yc not in panel.columns:
            continue
        _std = (panel.dropna(subset=[_yc])
                .groupby('year')[_yc].std())
        max_std = _std.max()  # 若所有分组均仅 1 个观测则为 NaN
        if pd.isna(max_std) or max_std <= 1e-10:
            logger.info(f"  ✓ {_yc} 为 year-level 常量")
        else:
            logger.error(f"  ✗ {_yc} 在同年内取值不一致!")

    # 地理指数截面变异校验
    for col in ['ft_attn_prov', 'ft_attn_city']:
        if col not in panel.columns:
            continue
        within_std = (panel.dropna(subset=[col])
                      .groupby('year')[col].std())
        mean_std = within_std.mean()  # 若所有分组均仅 1 个观测则为 NaN
        if pd.isna(mean_std):
            logger.info(f"  ✓ {col}: 各年均仅 1 个银行, 无法计算年内 std")
        elif mean_std < 1e-6:
            logger.warning(f"  {col}: 年内几乎无变异 (退化为 year-level)")
        else:
            logger.info(f"  ✓ {col}: 年内 std 均值={sig4(mean_std)}")


# ============================================================================
# 6c. 媒体信息中介异质性 - 九维度 (Bushee et al. 2010, JAR)
# ============================================================================

def compute_media_heterogeneity(df, panel):
    """计算媒体信息中介异质性变量 - 九维度分析。

    .. todo:: v3.0-split (Plan-r3 P1-7 锚点, god function)

        本函数将多个独立维度的计算耦合在一个流程中 (原始 4 大维度族, 现已扩至 9 维). 学术上每维度的
        测度方法 / 引用文献 / 标准误聚类层级都不同, 拆分理由充分:

        - ``_compute_financial_vs_other`` -- 财经 / 综合 媒体语调差
        - ``_compute_breadth_index`` -- Bushee et al. 2010 媒体广度
        - ``_compute_central_periphery`` -- 央媒 / 非央媒 注意力差
        - ``_compute_temporal_attention`` -- 月度注意力衰减权重

        拆分后每个子函数独立可测 (合成 panel 行 + 各自断言), 现状只能
        端到端测.

    九维度:
      1. 财经 vs 其他: 财经类报章 (15家) 与非财经类
      2. 综合 vs 其他: 综合性报章 (27家) 与非综合性
      3. 财经 vs 综合 vs 其他: 三方分拆
      4. 中央级 vs 地方级: CNKI 171家中央级 vs 其余
         (Qin, Strömberg & Wu 2018, AER)
      5. 官方 vs 非官方
      6. 市场化 vs 非市场化
      7. 深度期刊 vs 非深度
      8. 高频日报 vs 非日报
      9. 地理邻近性 (同省/同城)

    数据源: config/media_classification.json

    语义变更披露 (omni 2026-06-11):
      - fix(omni-g-attention-02): 维度⑤⑥改互斥构造 official := OFF−MKT /
        market := MKT−OFF (NPPA 主管/主办双判据非互斥, 重叠媒体落入两对照组);
      - fix(omni-g-attention-07): 维度⑨地理元数据缺失 → NaN 出域 (而非编码为
        "非本地" 0), frac 分母 = 可判定篇数, away 对照组不再混入未知来源文章。
    """
    if '媒体(中文)' not in df.columns:
        logger.warning("  媒体列不存在, 跳过")
        return panel

    df = df.copy()
    panel = panel.copy()

    _t0_het = time.time()
    _log_attention_substep_banner(
        '6c',
        '媒体信息中介异质性 — 九维度分析 (Bushee et al. 2010 媒体中介; 维度④⑤⑥⑨ 各有学术依据)',
        [
            'Bushee, B. J., Core, J. E., Guay, W., & Hamm, S. J. W. (2010). The role '
            'of the business press as an information intermediary. Journal of '
            'Accounting Research, 48(1), 1-19. '
            'https://doi.org/10.1111/j.1475-679X.2009.00357.x  (维度⑦ 媒体广度/原创信息)',
            'You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the '
            'pen? The Review of Financial Studies, 31(1), 43-96. '
            'https://doi.org/10.1093/rfs/hhx055  (维度⑤⑥ 官方 vs 市场化媒体治理效应)',
            'Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives '
            'to suppress negative information: Evidence from Chinese listed firms. '
            'Journal of Accounting Research, 53(2), 405-459. '
            'https://doi.org/10.1111/1475-679X.12071  (政治激励压制负面信息)',
            'Guest, N. M. (2021). The information role of the media in earnings news. '
            'Journal of Accounting Research, 59(3), 1021-1076. '
            'https://doi.org/10.1111/1475-679X.12349  (维度⑦ 深度分析型媒体原创性)',
            'Tetlock, P. C. (2007). Giving content to investor sentiment: The role of '
            'media in the stock market. The Journal of Finance, 62(3), 1139-1168. '
            'https://doi.org/10.1111/j.1540-6261.2007.01232.x  (维度⑧ 日频媒体情感)',
            'Tetlock, P. C., Saar-Tsechansky, M., & Macskassy, S. (2008). More than '
            'words: Quantifying language to measure firms\' fundamentals. The Journal '
            'of Finance, 63(3), 1437-1467. '
            'https://doi.org/10.1111/j.1540-6261.2008.01362.x  (维度⑧ 负面词汇预测基本面)',
            'Gurun, U. G., & Butler, A. W. (2012). Don\'t believe the hype: Local '
            'media slant, local advertising, and firm value. The Journal of Finance, '
            '67(2), 561-598. https://doi.org/10.1111/j.1540-6261.2012.01725.x  (维度⑨ 本地媒体偏斜)',
            'Core, J. E., Guay, W., & Larcker, D. F. (2008). The power of the pen and '
            'executive compensation. Journal of Financial Economics, 88(1), 1-25. '
            'https://doi.org/10.1016/j.jfineco.2007.05.001  (维度⑨ 负面信息选择性抑制)',
        ],
    )

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
        logger.warning(f"  FIN ∩ COMP 重叠: {overlap_fc} (将归类为 fin)")
    # 信息性日志: 中央级与财经/综合的交叉
    fc_in_central = (FIN | COMP) & CENTRAL
    if fc_in_central:
        logger.info(f"  ℹ️ 财经/综合 ∩ 中央级: {len(fc_in_central)} 家 "
                    f"(正交分类, 合理)")
    # fix(omni-g-attention-02, 2026-06-11): OFF ∩ MKT 重叠检查日志 — NPPA 双判据
    # (官方=主管单位为党政机关; 市场化=主办单位为企业) 非互斥, 实测重叠 386 家
    # (82% MARKET ⊂ OFFICIAL)。此前仅查 FIN∩COMP 从未查 OFF∩MKT, 维度⑤⑥的
    # YZZ (2018 RFS) 对立构念被重叠 dummy 掩盖。重叠媒体 (双判据) 从两维度
    # dummy 中互斥剔除 (official := OFF−MKT, market := MKT−OFF, 见维度⑤⑥)。
    overlap_om = OFFICIAL & MARKET
    if overlap_om:
        logger.info(f"  ℹ️ OFFICIAL ∩ MARKET 重叠: {len(overlap_om)} 家 "
                    f"(双判据媒体, 已从两维度 dummy 互斥剔除, 归入各自对照组)")

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
        logger.info(f"    内容分类 - {mt}: {n:,} ({pct4(n / len(df))})")

    # (1) 占比 - 维度①②
    for mt, col in [('fin', 'fin_media_frac'), ('comp', 'comp_media_frac')]:
        df[f'_is_{mt}'] = (df['_media_type'] == mt).astype(int)
        frac = (df.groupby(['target_bank', 'year'])[f'_is_{mt}']
                .mean().reset_index(name=col))
        panel = panel.merge(frac, on=['target_bank', 'year'], how='left')

    # (2) 三类型情感均值 + 三维度缺口 - 维度①②③
    # 三轨 (full/ctx/ss): _ss = 银行+金科同句共现轨 (llm_vote_score_ss); 缺列时
    # `if src not in df.columns: continue` 守卫优雅跳过 (graceful skip)。
    for track in ['_full', '_ctx', '_ss']:
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
                f"({pct4(n_central / len(df))})")

    # (3) 中央级占比
    frac_c = (df.groupby(['target_bank', 'year'])['_is_central']
              .mean().reset_index(name='central_media_frac'))
    panel = panel.merge(frac_c, on=['target_bank', 'year'], how='left')

    # (4) 中央/地方情感均值 + 缺口 (三轨 full/ctx/ss; _ss=银行+金科同句, 缺列优雅跳过)
    for track in ['_full', '_ctx', '_ss']:
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
    # 操作化: official_media 名单来自 NPPA 数据库, 以主管单位为党政机关为判据。
    # fix(omni-g-attention-02, 2026-06-11): YZZ (2018 RFS) 的对立构念是互斥窄集
    # (党委机关报 vs 市场化报), 而 NPPA 双判据 OFF (2208 家, 近全集) 与 MKT (471 家)
    # 重叠 386 家 — 旧 dummy 下 official_media_frac 近退化 (均值 0.873), 且 nonoff
    # 对照组反而剔除了大部分市场化媒体。改互斥构造: official := OFF − MKT (纯官方;
    # 企业主办的市场化媒体不再计入官方组, 归入 nonoff 对照, 修正 tone_gap_official_nonoff
    # 的 nonoff 组定义 — nonoff 现含**全部**市场化媒体)。与维度⑥ market := MKT − OFF
    # 结构性互斥, official_frac + market_frac ≤ 1 (校验见文末 (7b))。
    # 披露: 双判据媒体 (OFF∩MKT, 主管党政 + 主办企业) 不计入任一处理组,
    # 落入 nonoff / nonmkt 两对照组 — 论文层应重述操作化 (主管 vs 主办 双判据非互斥)。
    df['_is_official'] = df['媒体(中文)'].isin(OFFICIAL - MARKET).astype(int)
    n_official = df['_is_official'].sum()
    logger.info(f"    政治取向 - 纯官方 (OFF−MKT): {n_official:,} "
                f"({pct4(n_official / len(df))})")

    frac_off = (df.groupby(['target_bank', 'year'])['_is_official']
                .mean().reset_index(name='official_media_frac'))
    panel = panel.merge(frac_off, on=['target_bank', 'year'], how='left')

    # 三轨 (full/ctx/ss; _ss=银行+金科同句, 缺列优雅跳过)
    for track in ['_full', '_ctx', '_ss']:
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
    # 操作化: market_media 名单来自 NPPA 数据库, 以主办单位为企业/商业集团为判据。
    # fix(omni-g-attention-02, 2026-06-11): market := MKT − OFF (纯市场化), 与维度⑤
    # official := OFF − MKT 结构性互斥 — 旧 dummy 直接 isin(MARKET) 时 82% MARKET ⊂
    # OFFICIAL (重叠 386 家), YZZ (2018 RFS) 对立构念被重叠掩盖。双判据媒体 (OFF∩MKT)
    # 不计入任一处理组, 落入 nonoff / nonmkt 两对照组 (披露见维度⑤ 注释)。
    df['_is_market'] = df['媒体(中文)'].isin(MARKET - OFFICIAL).astype(int)
    n_market = df['_is_market'].sum()
    logger.info(f"    政治取向 - 纯市场化 (MKT−OFF): {n_market:,} "
                f"({pct4(n_market / len(df))})")

    frac_mkt = (df.groupby(['target_bank', 'year'])['_is_market']
                .mean().reset_index(name='market_media_frac'))
    panel = panel.merge(frac_mkt, on=['target_bank', 'year'], how='left')

    # 三轨 (full/ctx/ss; _ss=银行+金科同句, 缺列优雅跳过)
    for track in ['_full', '_ctx', '_ss']:
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
                f"({pct4(n_deepdive / len(df))})")

    frac_dd = (df.groupby(['target_bank', 'year'])['_is_deepdive']
               .mean().reset_index(name='deepdive_media_frac'))
    panel = panel.merge(frac_dd, on=['target_bank', 'year'], how='left')

    # 三轨 (full/ctx/ss; _ss=银行+金科同句, 缺列优雅跳过)
    for track in ['_full', '_ctx', '_ss']:
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
                f"({pct4(n_daily / len(df))})")

    frac_dl = (df.groupby(['target_bank', 'year'])['_is_daily']
               .mean().reset_index(name='daily_media_frac'))
    panel = panel.merge(frac_dl, on=['target_bank', 'year'], how='left')

    # 三轨 (full/ctx/ss; _ss=银行+金科同句, 缺列优雅跳过)
    for track in ['_full', '_ctx', '_ss']:
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

        # float 编码 (1.0=本地 / 0.0=异地 / NaN=不可判), 见下方 (9d) 出域守卫
        df['_is_homeprov'] = (_news_prov_clean == _bank_prov_clean).astype(float)
        df['_is_homecity'] = (_news_city_clean == _bank_city_clean).astype(float)

        # (9d) NaN / 空值 显式守卫
        #   防止 _clean_geo(NaN) → "nan" == "nan" 假阳性
        #   以及 "" == "" 假阳性 (当 bank_addresses 或新闻数据缺省份/城市时)
        # fix(omni-g-attention-07, 2026-06-11): 地理元数据缺失 → NaN (出域) 而非 0 —
        # 旧编码把"来源不可知"强制归入非本地: (a) homeprov/homecity_media_frac 的
        # 分母含地理不可判文章而分子只能来自确认本地 → 本地占比低估;
        # (b) away 组 (==0) 混入未知来源文章 → tone_gap_home*_non* 衰减;
        # (c) 银行总部省缺失时整行全 0 → frac 伪零而非 NaN。
        # 改 NaN 后: frac 的 groupby.mean 自动跳 NA (分母 = 可判定篇数, 全不可判 →
        # NaN), home/away 子组过滤 (==1 / ==0) 天然排除 NaN 行 (NaN==x 恒 False)。
        # (latent: 盘上试跑 857 篇地理列 0 缺失不触发; 17M 全量元数据缺失必现)
        _prov_invalid = (df['_bank_prov'].isna()
                         | df['国家地区/省份'].isna()
                         | (df['_bank_prov'].astype(str).str.strip() == '')
                         | (df['国家地区/省份'].astype(str).str.strip() == ''))
        df.loc[_prov_invalid, '_is_homeprov'] = np.nan
        if '城市' in df.columns:
            _city_invalid = (df['_bank_city'].isna()
                             | df['城市'].isna()
                             | (df['_bank_city'].astype(str).str.strip() == '')
                             | (df['城市'].astype(str).str.strip() == ''))
            df.loc[_city_invalid, '_is_homecity'] = np.nan
        else:
            # 城市列整列缺失 → 同城性整体不可判 (NaN), 而非全体"非同城"
            df['_is_homecity'] = np.nan

        # (9e) 拓扑不变量: 确认同城 (==1) ⇒ 同省 (提升为 1)。
        # fix(omni-g-attention-07): NaN 编码下不可再用 np.maximum (NaN 传播会抹掉
        # 已判定的 prov 值), 也不可用 np.fmax (fmax(NaN, 0)=0 会把"省不可判"错误
        # 改写为非同省 — 非同城不蕴含非同省)。只在 city==1 时改写。
        df['_is_homeprov'] = np.where(
            df['_is_homecity'] == 1, 1.0, df['_is_homeprov'])

        # 诊断 (sum/isna 均 skipna; NaN = 地理不可判, 不计入本地/异地任一侧)
        n_total = len(df)
        n_homeprov = int(df['_is_homeprov'].sum())
        n_homecity = int(df['_is_homecity'].sum())
        n_geo_na = int(df['_is_homeprov'].isna().sum())
        logger.info(f"    同省报道: {n_homeprov:,} ({pct4(n_homeprov / n_total)}), "
                    f"同城报道: {n_homecity:,} ({pct4(n_homecity / n_total)}), "
                    f"地理不可判 (出域): {n_geo_na:,} ({pct4(n_geo_na / n_total)})")

        # (9f) 三项核心指标 × Prov/City 双层 (geo 层级, 与情感 full/ctx/ss 三轨正交)
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
            # 三轨 (full/ctx/ss): _ss = 银行+金科同句共现轨 (llm_vote_score_ss /
            # is_negative_ss); 缺列时 `if src_tone not in df.columns: continue` 优雅跳过。
            for track in ['_full', '_ctx', '_ss']:
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
                        f"{sig4(panel[frac_col].dropna().mean())}")

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
    # fix(omni-g-attention-zerofill, 2026-06-11 组级裁决): 计数零填契约补齐 —
    # 本函数在 balance_panel (encode.py "计数/和类填 0" 契约, 含 n_articles* 前缀
    # 通配) **之后** 运行, 上方 left-join 对零文章 bank-year 留 NaN, 逃过该契约
    # (.dta 显 . 而非 0, 与兄弟列 n_articles=0 矛盾)。计数 Σ over ∅ = 0 → 填 0
    # 并恢复整型 (merge 产生 NaN 时 size 的 int64 已漂移为 float64)。
    # ceased_media_frac (比例类) / exc_*tone* (情感类) 按契约保持 NaN, 勿连带零填。
    panel['n_articles_exc'] = panel['n_articles_exc'].fillna(0).astype('int64')

    # (C.3) bank-year 三轨道全局情感均值（排除停刊; full/ctx/ss）
    # _ss = 银行+金科同句共现轨 (llm_vote_score_ss); 缺列时 `if src in df_alive.columns`
    # 守卫优雅跳过 (graceful skip)。
    df_alive = df[df['_is_ceased_media'] == 0]
    for track in ['_full', '_ctx', '_ss']:
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
                f"exc_tone_{{full/ctx/ss}}, {len(_exc_cols)} 个 exc_* 列")

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
                logger.info(f"  ✓ {col}: [{sig4(valid.min())}, {sig4(valid.max())}]")

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

    # (7b) fix(omni-g-attention-02, 2026-06-11): official/market 互斥校验 —
    # official := OFF−MKT 与 market := MKT−OFF 结构性不交 ⟹ 占比之和 ≤ 1
    # (旧重叠 dummy 下两占比之和实测 1.53, 该校验永不成立故从未存在)
    if ('official_media_frac' in panel.columns
            and 'market_media_frac' in panel.columns):
        _sum_om = (panel['official_media_frac'].fillna(0)
                   + panel['market_media_frac'].fillna(0))
        if (_sum_om > 1.0001).any():
            logger.error("  ✗ official + market 占比之和超过 1 (互斥构造被破坏)!")
        else:
            logger.info("  ✓ official + market 互斥约束成立 (OFF−MKT / MKT−OFF)")

    # (8) 正交分类说明 — fix(omni-g-attention-02, 2026-06-11): official/market 之间
    # 是互斥构造 (见 7b) 而非正交; 旧日志"central/official/market 正交分类"曾掩盖
    # OFF∩MKT 重叠。此处"正交"仅指与内容分类 (fin/comp) 的关系。
    logger.info("  ✓ 中央级/official/market 与内容分类 (fin/comp) 为正交分类; "
                "official ⊥ market 为互斥构造 (见 7b)")
    logger.info("  ✓ deepdive/daily 与其他维度正交")

    # ── 📊 关键指标解读 (运行结果信息, 日志富集 2026-06-24) ──
    try:
        logger.info("  📊 关键指标解读 (媒体异质性九维度占比)")
        for _col, _lbl in [
            ('fin_media_frac', '财经媒体占比'), ('comp_media_frac', '综合媒体占比'),
            ('central_media_frac', '中央级占比'), ('official_media_frac', '纯官方占比'),
            ('market_media_frac', '纯市场化占比'), ('deepdive_media_frac', '深度期刊占比'),
            ('daily_media_frac', '高频日报占比'), ('homeprov_media_frac', '同省占比'),
            ('homecity_media_frac', '同城占比'),
        ]:
            if _col not in panel.columns:
                continue
            _v = panel[_col].dropna()
            if len(_v) == 0:
                logger.warning(f"     · {_col} ({_lbl}): 全为 NaN — 该维度无可估样本")
                continue
            _mean = _v.mean()
            # 占比∈[0,1]: 近 0 或近 1 提示该类媒体在样本中近乎缺失/主导 (退化风险)
            if _mean < 0.02:
                _vd = '近零 (该类媒体几乎缺席, 对照组检验功效弱)'
            elif _mean > 0.95:
                _vd = '近饱和 (该类媒体近乎主导, 对照组样本稀薄)'
            else:
                _vd = '区分度健康'
            logger.info(f"     · {_col} ({_lbl}): 覆盖 {len(_v):,}/{len(panel):,}, "
                        f"均值={sig4(_mean)} [{sig4(_v.min())}, {sig4(_v.max())}] → {_vd}")
        if 'media_hhi' in panel.columns:
            _h = panel['media_hhi'].dropna()
            if len(_h) > 0:
                _hm = _h.mean()
                # HHI∈[0,1]: >0.25 高度集中 (来源单一), <0.15 分散 (来源多元)
                if _hm > 0.25:
                    _hvd = '高度集中 (媒体来源单一, 注意信息冗余/同源风险)'
                elif _hm < 0.15:
                    _hvd = '来源多元 (媒体覆盖分散)'
                else:
                    _hvd = '中等集中'
                logger.info(f"     · media_hhi (媒体来源集中度): 均值={sig4(_hm)} "
                            f"[{sig4(_h.min())}, {sig4(_h.max())}] → {_hvd}")
        logger.info(f"  ⏱ 步骤 6c (媒体异质性九维度) 墙钟耗时: {sig4(time.time() - _t0_het)} 秒")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  媒体异质性结果解读打印失败 (不影响处理): {e}")

    return panel
