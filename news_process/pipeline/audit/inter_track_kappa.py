"""news_process.pipeline.audit.inter_track_kappa — Stage 39a (三维借用计划 v1.37 的 P1)。

在 ``llm_verified_dual_both == True`` 子集上, 对三个创新维度 (locus,
substantiveness, collab_mode) 计算三轨 (full / ctx / ss) 两两之间的文章级
Cohen's κ; 三轨共 3 个 pair (full_ctx / full_ss / ctx_ss) × 3 维 = 9 行,
输出机器可读 CSV + 论文可用 TeX 到 ``eval_reports/``。

与 Stata 模板 ``20_tableA1_inter_track_kappa.do.tmpl`` 互为镜像。

学术锚点:
  - Cohen (1960) — κ 公式。
  - Landis & Koch (1977) — κ 解释阈值。
  - 预期 κ ∈ [0.50, 0.70] (不是"越高越好"); κ > 0.70 提示轨间冗余;
    κ < 0.30 提示噪声 (Landis & Koch 1977 区间 + 项目内部约定;
    原解释文档随 docs/ 目录于 commit 1698bda5 删除)。
  - Plan v1.37 §4.3.1: bootstrap CI, NaN-aware percentile + 50%
    有限值占比守卫 (R30A-01/R30B-01)。
  - Holm (1979) — 跨 3 个 pair 的 FWER step-down 校正 (每维度 family=3 pair)。

白话: 同一篇文章我们用三种文本口径 (full=全文, ctx=目标银行实体上下文窗口,
ss=银行+金科同句共现窗口) 各打一次标签。κ 衡量任意两套标签的一致程度。
太一致 (>0.70) 提示这两个口径可能测的是同一个东西; 太不一致 (<0.30) 提示
至少有一轨是噪声。落在中间区间说明三轨互补、各有信息。注意: 这只是诊断披露
(供论文中讨论), 三轨的去留不由相关性决定 — 项目立场是 full/ctx/ss 互为
稳健性, 高相关 = 对归因窗口稳健。bootstrap p 值检验 H0: κ=0 (单侧), 同维度
3 个 pair 之间用 Holm step-down 控制族错误率 (FWER)。

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 71_inter_track_kappa.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**输入**: 从 config['paths']['output_dir'] 读 `21_tone_llms.parquet`(文章级 LLM 标注), 按 `llm_verified_dual_both == True` 过滤到"双向验证 both"子集。读三个创新维度的三轨列: `innovation_locus_{full,ctx,ss}` / `innovation_substantiveness_{full,ctx,ss}` / `innovation_collab_mode_{full,ctx,ss}`。输入缺失 / 缺 llm_verified_dual_both 列 / dual_both 子集为空 → 发空占位表(全 NaN / n_obs=0 行)而非崩溃。

**处理步骤**(`run_stage` → `compute_inter_track_kappa`):
- 对每个维度 × 每个轨道 pair, 取两列 dropna() 后调 `_compute_kappa_with_bootstrap(return_pvalue=True)`(返回 5 元组 kp/lo/hi/n/pv)。
- 点估计 κ 经 `validation.radius_sensitivity_llm.cohens_kappa_2cat(y1,y2)['kappa']`。
- Bootstrap: `np.random.default_rng(seed=42)`, n_boot=1000 次有放回重抽, 每次重算 κ; 取 2.5%/97.5% nanpercentile 为 95% CI; 守卫: n_obs<3 或点估计常量列 NaN → 直接 NaN 元组; 有限重抽 <50% → CI 报 NaN + RuntimeWarning。
- 单侧 bootstrap p 值: H0 κ=0 vs κ>0, = 有限重抽中 κ≤0 的占比。
- 同维度内对 3 个 pair 的 raw p 值做 Holm(1979) step-down FWER 校正(`_holm_correct`, family=3; NaN 不参与排序, clip 到 [0,1] 并强制单调非降)。

**关键算法/公式**: Cohen(1960) κ=(p_o−p_e)/(1−p_e); Landis&Koch(1977) 解释阈值; 预期 κ∈[0.50,0.70](非越高越好, >0.70 提示轨间冗余、<0.30 提示某轨噪声); Holm step-down(第 k 小 p 值 ×(m−rank) 并强制单调非降)。阈值 _THRESHOLDS: locus 0.50 / substantiveness 0.45 / collab_mode 0.45。

**输出列**(9 行表): field, pair, kappa_point, ci_95_low, ci_95_high, n_obs, threshold, passes_threshold, p_value, p_value_holm。κ 落在 [0.30,0.70] 之外时 warnings.warn(RuntimeWarning)+ logger.warning。

**外部依赖/确定性**: 纯 numpy/pandas, 无 LLM/Embedding API、无 BERT/faiss; seed=42 + NaN-aware 守卫保证确定性可复现; 不触 _llm_cache.db(只读上游已落盘的 stage 21 parquet)。

**DAG 位置**: 验证阶段 39a(STAGES_VALIDATION), 上游=stage 21 tone_llms, 下游=Stata 表 20_tableA1(诊断披露用, 不进主面板)。

■ 白话说明

**这一步在做什么**: 同一篇新闻, 我们用三种不同"取景方式"读它——full(读全文)、ctx(只读目标银行附近那一小段)、ss(只读"银行和金融科技出现在同一句"的那几句)——然后各自给它打三个创新标签(这家银行报道讲的是真创新还是装样子、是底层技术还是表层应用、是自己研发还是找外人合作)。这一步像"让三位评委独立打分, 再两两比对他们的吻合程度"。这个吻合程度叫 Cohen's κ(一个一致性分数)。

**为什么需要它**: 如果三种取景方式打出来的标签几乎一模一样(κ>0.70), 说明它们其实在量同一个东西、白白多算了一遍; 如果差得离谱(κ<0.30), 说明至少有一种取景方式在乱打、是噪声。落在中间才说明三种口径各有各的信息、互相补充。bootstrap 和 Holm 校正是为了说"这个吻合程度不是碰巧得来的", 让审稿人信服。

**对最终面板/论文的影响**: 它本身不改银行-年度面板里的任何数字, 只产一张诊断表放进论文附录。它的价值是为论文"三轨互为稳健性"这个核心主张背书——证明三种文本口径既不是冗余重复, 也不是某一轨在添乱, 从而让主回归结论更可信。
========================================================================
"""
import os
import platform
import sys
import time
import warnings

import numpy as np
import pandas as pd

from news_process.core.config import load_config
from news_process.core.logging import pct4, setup_logging, sig4
from news_process.validation.radius_sensitivity_llm import cohens_kappa_2cat

STAGE_NAME = "71_inter_track_kappa"

# Plan v1.37 §4.3.1 thresholds (Landis & Koch 1977 区间 + 项目内部约定; 原 docs/ 解释文档已删).
# v3.4.0 §J.4: 第三维度 collab_mode κ ≥ 0.45 (mirrors substantiveness fair-to-moderate
# 标准; Chesbrough 2003 + L&S 2006 SMJ; additive supplementation per Nosek 2018 PNAS).
_THRESHOLDS = {
    'innovation_locus': 0.50,
    'innovation_substantiveness': 0.45,
    'innovation_collab_mode': 0.45,
}

# 三轨两两 pair (plan §⑧ / §7.3-A3): 每个 pair = (左轨后缀, 右轨后缀, pair 标签)。
# ss = 银行+金科同句共现轨 (content_ss / suffix _ss); 三轨 → 3 个 pair。
# 每维度对这 3 个 pair 各算一行 κ → 9 行总表 (含 'pair' 列)。
_TRACK_PAIRS = [
    ('_full', '_ctx', 'full_ctx'),
    ('_full', '_ss', 'full_ss'),
    ('_ctx', '_ss', 'ctx_ss'),
]


def _holm_correct(pvals):
    """Holm (1979) step-down FWER 校正。

    输入原始 p 值列表 (可含 NaN; NaN 不参与排序与计数, 输出仍 NaN);
    返回与输入等长的校正后 p 值列表 (已 clip 到 [0, 1], 强制单调非降)。

    白话: 同一维度下我们对 3 个轨道 pair 各做一次"κ 是否 > 0"的检验, 做了
    多次检验就更容易碰巧显著。Holm 把 p 值从小到大排, 第 k 小的乘以 (m-k+1)
    (m=有效检验数), 再保证序列不下降 — 比 Bonferroni 更不保守但同样控制 FWER。
    """
    idx_valid = [i for i, p in enumerate(pvals) if p is not None and not np.isnan(p)]
    m = len(idx_valid)
    out = [float('nan')] * len(pvals)
    if m == 0:
        return out
    # 按原始 p 升序排序有效项
    order = sorted(idx_valid, key=lambda i: pvals[i])
    prev = 0.0
    for rank, i in enumerate(order):
        adj = (m - rank) * pvals[i]
        adj = min(1.0, max(adj, prev))  # 单调非降 + clip 上界 1
        out[i] = float(adj)
        prev = adj
    return out


def _compute_kappa_with_bootstrap(y1, y2, n_boot=1000, seed=42, return_pvalue=False):
    """返回 (kappa_point, ci_low, ci_high, n_obs) 4 元组, bootstrap 对 NaN 安全。

    ``return_pvalue=True`` 时返回 5 元组 (..., p_value) — 单侧 bootstrap p 值
    供 Holm FWER 用 (plan §⑧ 三轨化新增; 默认 False 保持旧 4 元组契约, 不破
    既有 4 元组解包调用方 / 测试)。

    实现遵循 plan v1.37 §4.3.1 步骤 1-5:
      1. n_obs < 3 时短路 → (nan, nan, nan, n_obs)。
      2. 点估计 κ 经 cohens_kappa_2cat(...)['kappa'] (R29C-01 dict 取值)。
      3. Bootstrap 重抽 n_boot 次; 每次重抽追加 ['kappa']。
      4. NaN-aware percentile (R30A-01/R30B-01): 要求 ≥50% 的 κ 为有限值,
         否则返回 (kappa_point, nan, nan, n_obs) + WARN。
      5. 边界: 原始输入某列为常量 → (nan, nan, nan, n_obs)。
      6. p_value (return_pvalue=True): 单侧 bootstrap 检验 H0: κ=0 vs κ>0,
         = 有限重抽中 κ ≤ 0 的比例 (供 Holm step-down 跨 3 个 pair 校正)。

    白话: bootstrap 就是"有放回地反复抽自己的样本再算一遍 κ", 用上千次
    结果的 2.5%/97.5% 分位数当置信区间。如果一半以上的重抽算不出有效 κ
    (比如抽到的子样本里某个标签全是同一个值), 区间就不可信, 直接报 NaN。
    p 值则数"有多少次重抽的 κ ≤ 0", 占比越小说明 κ 越稳健地大于 0。
    """
    y1 = np.asarray(y1)
    y2 = np.asarray(y2)
    n_obs = len(y1)
    if n_obs < 3:
        base = (float('nan'), float('nan'), float('nan'), int(n_obs))
        return (*base, float('nan')) if return_pvalue else base

    point = cohens_kappa_2cat(y1, y2)
    kappa_point = point['kappa']
    # 原始输入常量列边界 (点估计已是 NaN → 直接返回 NaN 元组)
    if np.isnan(kappa_point):
        base = (float('nan'), float('nan'), float('nan'), int(n_obs))
        return (*base, float('nan')) if return_pvalue else base

    rng = np.random.default_rng(seed)
    kappas = []
    for _ in range(n_boot):
        idx = rng.choice(n_obs, size=n_obs, replace=True)
        kb = cohens_kappa_2cat(y1[idx], y2[idx])['kappa']
        kappas.append(kb)

    finite = [k for k in kappas if not np.isnan(k)]
    if len(finite) < 0.5 * n_boot:
        warnings.warn(
            f"Bootstrap degenerate: only {len(finite)}/{n_boot} finite κ "
            f"resamples (< 50%); CI bounds returned as NaN.",
            RuntimeWarning,
            stacklevel=2,
        )
        base = (float(kappa_point), float('nan'), float('nan'), int(n_obs))
        return (*base, float('nan')) if return_pvalue else base

    ci_low = float(np.nanpercentile(kappas, 2.5))
    ci_high = float(np.nanpercentile(kappas, 97.5))
    base = (float(kappa_point), ci_low, ci_high, int(n_obs))
    if not return_pvalue:
        return base
    # 单侧 bootstrap p 值: H0 κ=0; = 有限重抽中 κ ≤ 0 的占比
    p_value = float(sum(1 for k in finite if k <= 0.0) / len(finite))
    return (*base, p_value)


def compute_inter_track_kappa(df):
    """返回 9 行 DataFrame: field, pair, kappa_point, ci_95_low, ci_95_high,
    n_obs, threshold, passes_threshold, p_value, p_value_holm。

    每个创新维度 (locus, substantiveness, collab_mode [v3.4.0]) × 3 个轨道
    pair (full_ctx / full_ss / ctx_ss) = 9 行 (plan §⑧ 三轨化)。p_value_holm
    在同维度的 3 个 pair 之间做 Holm step-down FWER 校正。

    ss = 银行+金科同句共现轨 (content_ss); ss 列缺失时该 pair 行优雅退化为
    NaN κ (镜像 col_full/col_ctx 缺失守卫)。"""
    rows = []
    for field, threshold in _THRESHOLDS.items():
        # 同维度内逐 pair 计算 κ, 收集 p 值后再 Holm 校正 (family = 3 pair)
        field_rows = []
        raw_pvals = []
        for left_sfx, right_sfx, pair_label in _TRACK_PAIRS:
            col_l = f"{field}{left_sfx}"
            col_r = f"{field}{right_sfx}"
            if col_l not in df.columns or col_r not in df.columns:
                # 任一轨列缺失 (典型: ss 列尚未物化) → NaN 行优雅跳过
                field_rows.append({
                    'field': field,
                    'pair': pair_label,
                    'kappa_point': float('nan'),
                    'ci_95_low': float('nan'),
                    'ci_95_high': float('nan'),
                    'n_obs': 0,
                    'threshold': threshold,
                    'passes_threshold': False,
                    'p_value': float('nan'),
                })
                raw_pvals.append(float('nan'))
                continue
            # 丢弃任一轨为 NaN 的成对行
            sub = df[[col_l, col_r]].dropna()
            kp, lo, hi, n, pv = _compute_kappa_with_bootstrap(
                sub[col_l].to_numpy(),
                sub[col_r].to_numpy(),
                return_pvalue=True,
            )
            passes = (not np.isnan(kp)) and (kp >= threshold)
            field_rows.append({
                'field': field,
                'pair': pair_label,
                'kappa_point': kp,
                'ci_95_low': lo,
                'ci_95_high': hi,
                'n_obs': n,
                'threshold': threshold,
                'passes_threshold': bool(passes),
                'p_value': pv,
            })
            raw_pvals.append(pv)
        # Holm step-down 跨同维度 3 个 pair (plan §7.3-A3 FWER)
        holm = _holm_correct(raw_pvals)
        for r, ph in zip(field_rows, holm):
            r['p_value_holm'] = ph
        rows.extend(field_rows)
    return pd.DataFrame(rows, columns=[
        'field', 'pair', 'kappa_point', 'ci_95_low', 'ci_95_high',
        'n_obs', 'threshold', 'passes_threshold', 'p_value', 'p_value_holm',
    ])


def _render_tex(table_df, out_path):
    """Booktabs 风格 TeX 表; 满足 plan v1.37 §4.7 验收正则
    (\\toprule / \\midrule / \\bottomrule; 列数随 schema, 现 10 列含 pair/p_value/
    p_value_holm; plan 原文写 2 数据行, v3.4.0 增 collab_mode → 每维度一行,
    第三轨 ss 三轨化后为 3 维 × 3 个 pair (full_ctx/full_ss/ctx_ss) = 9 行)。"""
    cols = list(table_df.columns)
    n_cols = len(cols)
    lines = [
        "\\begin{tabular}{" + "l" + "r" * (n_cols - 1) + "}",
        "\\toprule",
        " & ".join(cols) + " \\\\",
        "\\midrule",
    ]
    for _, r in table_df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, float):
                cells.append("NaN" if np.isnan(v) else f"{v:.4f}")
            elif isinstance(v, (bool, np.bool_)):
                cells.append("True" if bool(v) else "False")
            else:
                cells.append(str(v))
        lines.append(" & ".join(cells) + " \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    out_path_str = str(out_path)
    with open(out_path_str, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")


def _log_environment_config_methods(logger, config, input_path, csv_path, tex_path):
    """打印 项目/环境 + 输入输出 + 运行配置 + 方法论依据 四块 (日志富集 2026-06-24)。

    把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数、方法学出处"一次性落进
    日志, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 / schema / 控制流 (golden-safe)。

    参考文献策略: 本模块核心方法 (Cohen 1960 κ / Landis & Koch 1977 解释阈值 /
    Holm 1979 FWER) 的 DOI 不在本工作流"经核验参考文献注册表"中, 故按铁律仅 emit
    作者-年份-期刊方法名 (不伪造 DOI 链接); 完整出处见模块顶部 docstring 注释。
    """
    try:
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')

        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (轨间一致性 Cohen's κ; STAGES_VALIDATION 71)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) v3.11.1")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "纯 numpy/pandas, 无 LLM·Embedding·BERT·网络 ($0); seed=42 确定性逐位可复现")

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 输入:     {input_path} (文章级 LLM 标注; 过滤 llm_verified_dual_both==True)")
        logger.info(f"     · 输出 CSV: {csv_path} (机器可读 9 行诊断表)")
        logger.info(f"     · 输出 TeX: {tex_path} (论文附录 Table A1 booktabs)")
        logger.info("     · config 来源键: paths.output_dir / paths.log_dir")

        logger.info("  ⚙ 运行配置")
        logger.info("     · bootstrap: n_boot=1000 | seed=42 | 95% CI=NaN-aware [2.5%, 97.5%] nanpercentile")
        logger.info("     · CI 守卫: n_obs<3 短路 NaN | 有限重抽 <50% → CI=NaN + RuntimeWarning")
        logger.info(f"     · bootstrap p 值: 单侧 H0 κ=0 vs κ>0; 同维度 family={len(_TRACK_PAIRS)} pair 做 Holm 校正")
        logger.info("     · 三轨 pair: " + " / ".join(p[2] for p in _TRACK_PAIRS)
                    + " (full=全文 / ctx=银行实体窗 / ss=银行+金科同句窗)")
        for fld, thr in _THRESHOLDS.items():
            logger.info(f"     · 阈值 {fld.replace('innovation_', ''):<16}: κ ≥ {sig4(thr)} "
                        "(passes_threshold 判定线)")
        logger.info("     · 哨兵区间: κ∈[0.30, 0.70] 为期望区 (<0.30 某轨噪声 / >0.70 轨间冗余)")

        logger.info("  📖 方法论依据 (核心构念学术出处, 经 logger 落入 .log)")
        logger.info("     · Cohen, J. (1960). A coefficient of agreement for nominal scales. "
                    "Educational and Psychological Measurement, 20(1), 37-46. "
                    "https://doi.org/10.1177/001316446002000104  [κ=(p_o−p_e)/(1−p_e)]")
        logger.info("       → 两评分者名义类别一致性的偶然校正度量 (此处=两文本口径标签一致程度)")
        logger.info("     · Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement "
                    "for categorical data. Biometrics, 33(1), 159-174. https://doi.org/10.2307/2529310")
        logger.info("       → fair/moderate/substantial 分级; 项目约定期望 κ∈[0.50, 0.70] (非越高越好)")
        logger.info("     · Holm (1979). step-down FWER 校正, Scandinavian Journal of Statistics")
        logger.info("       → 同维度 3 个 pair 多重检验族错误率控制 (比 Bonferroni 更不保守)")
        logger.info("     · 现代补充 (经 Crossref 核验, 锚定一致性/判别效度报告标准):")
        logger.info("     · Rönkkö, M., & Cho, E. (2022). An updated guideline for assessing "
                    "discriminant validity. Organizational Research Methods, 25(1), 6-14. "
                    "https://doi.org/10.1177/1094428120968614")
        logger.info("       → (白话: 判别效度准则现代更新指南; 锚定本阶段 κ>0.70=轨间冗余/不可判别 的判读标准)")
        logger.info("     · Moons, F., & Vandervieren, E. (2025). Measuring agreement among several "
                    "raters classifying subjects into one or more (hierarchical) categories: A "
                    "generalization of Fleiss' kappa. Behavior Research Methods, 57(10), Article 287. "
                    "https://doi.org/10.3758/s13428-025-02746-8")
        logger.info("       → (白话: Fleiss κ 向多评分者/多标签/层级类别的现代直接扩展; 三轨 = 多'评分者'一致性的概念依据)")
        logger.info("     · Marzi, G., Balzano, M., & Marchiori, D. (2024). K-Alpha Calculator-"
                    "Krippendorff's Alpha Calculator: A user-friendly tool for computing "
                    "Krippendorff's Alpha inter-rater reliability coefficient. MethodsX, 12, 102545. "
                    "https://doi.org/10.1016/j.mex.2023.102545")
        logger.info("       → (白话: Krippendorff α 的 2024 实现工具; 与 Cohen κ 并列的 inter-coder 信度系数对照锚点)")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法信息打印失败 (不影响处理): {e}")


def run_stage(config=None, logger=None):
    """Stage 39a 入口。

    从配置的 output dir 读 ``21_tone_llms.parquet``, 按
    ``llm_verified_dual_both == True`` 过滤, 对全部三个创新维度计算
    轨间 κ, 写 CSV + TeX 到 ``eval_reports/``。
    """
    if config is None:
        config = load_config()
    if logger is None:
        logger = setup_logging(STAGE_NAME, config["paths"].get("log_dir", "logs"))

    # 功能说明 banner — 写入 <stage>.log, 让日志自带阶段用途说明 (仿 39c)。
    logger.info("=" * 72)
    logger.info("阶段 71: 轨间一致性 Cohen's κ (inter-track kappa; Plan v1.37 P1)")
    logger.info("=" * 72)
    logger.info("【功能】同一篇文章用三种文本口径 (full=全文 / ctx=银行实体上下文窗口 /")
    logger.info("        ss=银行+金科同句共现窗口) 各打一次创新标签, 对 locus / substantiveness /")
    logger.info("        collab_mode 三维, 在 llm_verified_dual_both 子集上两两比对一致程度,")
    logger.info("        产 9 行诊断表 (3 维 × full_ctx/full_ss/ctx_ss 3 个 pair) 供论文附录 (Table A1)。")
    logger.info("【方法】Cohen(1960) κ=(p_o−p_e)/(1−p_e); bootstrap 1000 次 (seed=42) 取 2.5%/97.5%")
    logger.info("        为 95% CI, 单侧 bootstrap p 值检验 H0:κ=0; 同维度 3 个 pair 做 Holm(1979)")
    logger.info("        step-down FWER 校正。阈值: locus≥0.50 / substantiveness≥0.45 / collab≥0.45。")
    logger.info("【判读】预期 κ∈[0.50,0.70] (非越高越好): κ>0.70 提示两轨冗余 (测同一东西),")
    logger.info("        κ<0.30 提示某轨噪声; 落中间区间=三轨互补、各有信息 (项目立场: 三轨互为稳健性)。")
    logger.info("【确定性】纯 numpy/pandas, 无 LLM/Embedding/BERT 调用, seed=42 + NaN-aware 守卫保证逐位可复现。")

    output_dir = config["paths"]["output_dir"]
    # fix(stage-input-config-wiring, 2026-06-25): 经 config 单一真值解析 stage 21 输出名
    # (output_21_tone_llms; 键存在值=默认 → golden-safe), 替代硬编码字面量。
    input_path = os.path.join(output_dir, config.get("filenames", {}).get("output_21_tone_llms", "21_tone_llms.parquet"))
    eval_dir = os.path.join(output_dir, "eval_reports")
    csv_path = os.path.join(eval_dir, "inter_track_kappa_table.csv")
    tex_path = os.path.join(eval_dir, "inter_track_kappa_table.tex")

    # 项目/环境 + 输入输出 + 配置 + 方法论依据 四块 (日志富集 2026-06-24)
    _log_environment_config_methods(logger, config, input_path, csv_path, tex_path)

    # 运行期阶段计时累计 (各主要阶段墙钟耗时, 末尾汇总打印)
    phase_durations: dict[str, float] = {}

    # ① 读取 + dual_both 过滤
    _t = time.perf_counter()
    if not os.path.exists(input_path):
        logger.warning(f"Input not found: {input_path}; emitting NaN row table.")
        # 三轨占位列 (full/ctx/ss); ss = 银行+金科同句共现轨
        df_subset = pd.DataFrame(columns=[
            'innovation_locus_full', 'innovation_locus_ctx', 'innovation_locus_ss',
            'innovation_substantiveness_full', 'innovation_substantiveness_ctx',
            'innovation_substantiveness_ss',
            'innovation_collab_mode_full', 'innovation_collab_mode_ctx',
            'innovation_collab_mode_ss',
            'llm_verified_dual_both',
        ])
    else:
        df = pd.read_parquet(input_path)
        if 'llm_verified_dual_both' not in df.columns:
            logger.warning(
                "Column 'llm_verified_dual_both' absent; emitting NaN rows."
            )
            df_subset = df.iloc[0:0]
        else:
            df_subset = df[df['llm_verified_dual_both'] == True].copy()
            if len(df_subset) == 0:
                logger.warning("dual_both subset empty; emitting NaN rows.")
        # 📥 I/O 溯源 (日志富集 Round 8, log-only golden-safe): 读盘形状 + dual_both
        # 门留存率 + 9 个三轨创新列在场审计。把"读进来多少行列、dual_both 门过了多大
        # 比例、哪几个 ss/创新轨列缺失 (= 下游若干行 κ=NaN 退化的直接成因)"一次性落日志,
        # 供复现核对 / 审计 / 排错。所有局部量仅喂 logger 后丢弃, 不参与任何计算。
        try:
            logger.info("  📥 I/O 溯源 (读盘形状 / dual_both 留存 / 三轨创新列在场)")
            logger.info(
                f"     · 读入 parquet: {df.shape[0]:,d} 行 × {df.shape[1]:,d} 列 "
                f"({os.path.basename(input_path)})"
            )
            _n_total = len(df)
            _n_sub = len(df_subset)
            logger.info(
                f"     · llm_verified_dual_both 门: {_n_total:,d} → {_n_sub:,d} 行留存 "
                f"(留存率 {pct4(_n_sub / max(_n_total, 1))}; 双向验证 both 子集占全语料比例)"
            )
            _innov_cols = [
                f"innovation_{_dim}_{_trk}"
                for _dim in ('locus', 'substantiveness', 'collab_mode')
                for _trk in ('full', 'ctx', 'ss')
            ]
            _present = [c for c in _innov_cols if c in df.columns]
            _absent = [c for c in _innov_cols if c not in df.columns]
            logger.info(
                f"     · 三轨创新列在场: {len(_present):,d}/{len(_innov_cols):,d} 存在"
                + (f" | 缺失 {len(_absent):,d}: {', '.join(_absent)}"
                   if _absent else " (9 列全部齐备)")
            )
            if _absent:
                logger.info(
                    "       → 缺失列 (典型: ss 轨尚未付费播种物化) 对应的 pair 行将优雅退化为 "
                    "NaN κ (本阶段 compute_inter_track_kappa 已内建该守卫); 这正是下游若干行 "
                    "κ=NaN 的成因, 非异常。"
                )
        except Exception as e:  # noqa: BLE001
            logger.warning(f"  I/O 溯源打印失败 (不影响处理): {e}")
    phase_durations['①读取+dual_both过滤'] = time.perf_counter() - _t

    # ② κ 点估计 + bootstrap CI + Holm FWER (本阶段计算主体)
    _t = time.perf_counter()
    table = compute_inter_track_kappa(df_subset)
    phase_durations['②κ+bootstrap+Holm'] = time.perf_counter() - _t

    # ③ 写 CSV + TeX
    _t = time.perf_counter()
    os.makedirs(eval_dir, exist_ok=True)
    table.to_csv(csv_path, index=False, encoding='utf-8')
    _render_tex(table, tex_path)
    phase_durations['③写CSV+TeX'] = time.perf_counter() - _t

    # 阈值区间告警, 按 plan v1.37 §4.3.1 step 6 (三轨化: 含 pair 标签)
    for _, r in table.iterrows():
        k = r['kappa_point']
        if not np.isnan(k) and (k < 0.30 or k > 0.70):
            warnings.warn(
                f"{r['field']} [{r['pair']}] κ={k:.4f} outside expected "
                f"[0.30, 0.70]; <0.30 = one track noise; >0.70 = tracks redundant.",
                RuntimeWarning,
                stacklevel=2,
            )
            logger.warning(
                f"{r['field']} [{r['pair']}] κ={sig4(k)} outside [0.30, 0.70] sentinel range."
            )

    # 结果分析 — 写入日志: 逐行 κ 点估计 + CI + Holm p 值 + 阈值/区间判读。
    logger.info("-" * 72)
    n_dual_both = int(len(df_subset))
    logger.info(
        f"【结果分析】轨间 κ 诊断 (双向验证 both 子集 n={n_dual_both} 篇; "
        f"共 {len(table)} 行 = 3 维 × 3 个 pair):"
    )
    # 逐行解读: κ 点估计 + 95% CI + Holm 校正 p 值, 对照阈值与 [0.30,0.70] 哨兵区间。
    n_valid = 0          # 非 NaN κ 的行数 (实际算出 κ 的 pair)
    n_pass = 0           # 达到本维度阈值的行数 (好)
    n_redundant = 0      # κ>0.70 轨间冗余 (临界, 提示测同一东西)
    n_noise = 0          # κ<0.30 某轨噪声 (不利)
    for _, r in table.iterrows():
        fld = str(r['field']).replace('innovation_', '')
        k = r['kappa_point']
        lo = r['ci_95_low']
        hi = r['ci_95_high']
        n_obs = int(r['n_obs'])
        thr = r['threshold']
        ph = r['p_value_holm']
        if np.isnan(k):
            # 典型: ss 轨列尚未物化, 该 pair 优雅退化为 NaN (n_obs=0)
            logger.info(
                f"  {fld} [{r['pair']}]: κ=NaN (n_obs={n_obs}) → 轨列缺失/样本不足, 优雅跳过"
            )
            continue
        n_valid += 1
        # 方向判读: 落在 [0.30,0.70] 哨兵区间内且达阈值=好; >0.70 冗余; <0.30 噪声
        if k > 0.70:
            verdict = "κ>0.70 → 轨间冗余 (临界, 提示两轨测同一东西)"
            n_redundant += 1
        elif k < 0.30:
            verdict = "κ<0.30 → 某轨噪声 (不利)"
            n_noise += 1
        elif k >= thr:
            verdict = f"达阈值 (≥{sig4(thr)}) 且落 [0.30,0.70] 互补区间 (好)"
            n_pass += 1
        else:
            verdict = f"未达阈值 (<{sig4(thr)}) 但落 [0.30,0.70] (临界偏弱)"
        ph_str = "NaN" if (ph is None or np.isnan(ph)) else sig4(ph)
        sig = "" if (ph is None or np.isnan(ph)) else (
            " [Holm 后 κ>0 显著]" if ph < 0.05 else " [Holm 后不显著]"
        )
        logger.info(
            f"  {fld} [{r['pair']}]: κ={sig4(k)}  95%CI=[{sig4(lo)}, {sig4(hi)}]  "
            f"n_obs={n_obs}  Holm_p={ph_str}{sig} → {verdict}"
        )
    # 汇总判读 (达阈值占比 pct4)
    pass_frac = (n_pass / n_valid) if n_valid else float('nan')
    pass_str = "n/a" if np.isnan(pass_frac) else pct4(pass_frac)
    logger.info(
        f"  汇总: 有效行 {n_valid}/{len(table)} | 达阈值(好) {n_pass} (占有效行 {pass_str}) | "
        f"冗余 κ>0.70 {n_redundant} | 噪声 κ<0.30 {n_noise}"
    )
    # κ 点估计分布速览 (日志富集 Round 8, log-only golden-safe): 跨 ≤9 行有效 κ 的
    # mean/median/min/max, 给审稿人"三轨整体落在哨兵区间 [0.30,0.70] 哪个位置"的一眼
    # 概览 (诚实次要 — 每行 κ 已逐行单独打印; 本行仅作单瞥汇总, 局部量喂 logger 后丢弃)。
    try:
        _kv = [float(x) for x in table['kappa_point'].dropna().tolist()]
        if _kv:
            logger.info(
                f"  κ 点估计分布 (n={len(_kv):,d} 有效行): "
                f"mean={sig4(sum(_kv) / len(_kv))} median={sig4(float(np.median(_kv)))} "
                f"min={sig4(min(_kv))} max={sig4(max(_kv))} (对照哨兵区间 [0.30, 0.70])"
            )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  κ 分布速览打印失败 (不影响处理): {e}")
    if n_valid == 0:
        logger.warning(
            "  ⚠ 全部 9 行 κ 均为 NaN — 上游 21_tone_llms 缺失 / 缺 llm_verified_dual_both 列 / "
            "dual_both 子集为空 / 三轨创新列均未物化; 本次仅发空占位表, 无可用诊断结论 (优雅降级)。"
        )
    elif n_valid < len(table):
        logger.warning(
            f"  ⚠ 仅 {n_valid}/{len(table)} 行算出 κ — 多为 ss 轨 (full_ss/ctx_ss) 列尚未物化所致; "
            "ss 缓存付费播种 + 全量重跑后该缺口闭合。"
        )
    # 小样本警告: 盘面 dual_both 子集偏小时只验证管道正确性
    if 0 < n_dual_both < 100:
        logger.info(
            f"  ⚠ dual_both 子集仅 {n_dual_both} 篇 (盘面 T=2 小样本), κ 点估计与 CI 仅验证管道正确性; "
            "全量结论以 17M/T=18 实测为准。"
        )
    logger.info("-" * 72)

    # ⏱ 阶段计时汇总 (各子阶段墙钟耗时; 数值 sig4 秒)
    try:
        logger.info("  ⏱ 阶段计时 (墙钟秒)")
        for _name, _dur in phase_durations.items():
            logger.info(f"     · {_name}: {sig4(_dur)} 秒")
        logger.info(f"     · 合计: {sig4(sum(phase_durations.values()))} 秒")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  计时汇总打印失败 (不影响处理): {e}")

    logger.info(f"Wrote {csv_path} + {tex_path} (n_obs={int(table['n_obs'].iloc[0] if len(table) else 0)})")
    return table
