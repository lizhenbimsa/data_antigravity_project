"""news_process.validation.radius_sensitivity_llm — Stage 35 LLM 升级 (v3.2.0)

Plan v14 §3.5 P5.2: stage 35 词典法 → LLM 法升级
    现行 stage 35 (radius_sensitivity.py) 是纯词典法 (6 套 jieba 词典: jiang/yao/bian/du/you/loughran).
    本模块新建 LLM 法 section, 与 dict-based 并存 (plan v14 P5.2 backward-compat).

核心洞察 (plan v14 R11):
    一次 LLM 调用的 unified_cot.txt v8 prompt 同时产出三阶段输出:
      stage 1: verification (is_bank_fintech_news + confidence)
      stage 2: sentiment + confidence
      stage 3: innovation_locus + innovation_substantiveness + innovation_collab_mode + confidences
              (innovation_collab_mode = v8 新增第三创新维度, Chesbrough 2003 自主-外部协同)
    → 一组 LLM 调用产 sentiment + locus + substantiveness 三轴 robustness 报告.

实际 LLM 调用量 (plan v14 修订, 取代 180k 误估):
    N = 1170 (current production stage 14 input rows)
    L = 3 LLMs (roster 读自 config/sentiment.yaml LLM_CONFIG; 下列名仅示例, 以配置为准:
                gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash)
    R_new = 3 (radii ∈ {0, 2, 3}; radius=1 已缓存 baseline)
    T = 1 (仅 ctx 轨; full 轨缓存命中, 不受 radius 影响)
    Total = N × L × R_new × T = 1170 × 3 × 3 × 1 = 10,530

锚定文献:
    Hassan et al. (2019, QJE) Proximity-based Attribution 参数敏感性
    Sautner et al. (2023, JF) firm × topic 邻近化 robustness
    Bingler et al. (2022, FRL) cheap talk segment-level robustness

白话:
    radius_sensitivity.py 用词典法测"窗口几句话"的敏感性, 本模块是它的
    LLM 法姊妹版: 换不同窗口重新让 LLM 判一遍, 看三个维度 (情感/创新
    位点/实质性) 的结论稳不稳。目前是脚手架状态: --dry-run 只估算要花
    多少次 LLM 调用; --launch 真跑路径尚未完整实现, 读缓存解析也刻意
    fail-loud (宁可报错也不返回假数据凑出"通过"报告)。
"""
from __future__ import annotations

import json
import logging
import os
import platform
import sys
import time
from typing import Dict, List

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import sig4

logger = logging.getLogger(__name__)

# 检验参数 (plan v14 §3.5 P5.2)
RADII_TO_TEST: List[int] = [0, 1, 2, 3]
CACHED_RADIUS: int = 1  # 已存在的 baseline 配置, 不重跑

# κ 阈值 (plan v14 §5.2 R5-B, Landis & Koch 1977 substantial)
KAPPA_THRESHOLD_RADIUS = 0.70  # radius 稳健性: 期望高 (同一轨内不同 radius 应稳定)
# 注(三轨, 2026-06-14): radius 扫描是 ctx 窗口提取参数的敏感性 (sentence_radius);
# ss 轨有自己独立的 ss_sentence_radius 参数, 其 radius 敏感性是与本模块平行的
# 未来扩展项 (本 LLM 法升级仍是 scaffold/dry-run, 三轨化无需改本模块扫描逻辑)。


def cohens_kappa_2cat(y1: np.ndarray, y2: np.ndarray) -> Dict[str, float]:
    """二分类标签 (如 locus / substantiveness) 的 Cohen's κ。

    返回 dict: {kappa, observed_agreement, expected_agreement, n}
    """
    mask = (~pd.isna(y1)) & (~pd.isna(y2))
    y1, y2 = y1[mask], y2[mask]
    n = len(y1)
    if n < 2:
        return {'kappa': float('nan'), 'observed_agreement': float('nan'),
                'expected_agreement': float('nan'), 'n': n}
    # 观察一致率
    p_o = np.mean(y1 == y2)
    # 预期一致率 (按 marginal 概率)
    cats = sorted(set(np.concatenate([y1, y2])))
    p_e = 0.0
    for c in cats:
        p_e += (np.mean(y1 == c) * np.mean(y2 == c))
    if p_e >= 1.0:
        return {'kappa': float('nan'), 'observed_agreement': float(p_o),
                'expected_agreement': float(p_e), 'n': int(n)}
    kappa = (p_o - p_e) / (1.0 - p_e)
    return {
        'kappa': float(kappa),
        'observed_agreement': float(p_o),
        'expected_agreement': float(p_e),
        'n': int(n),
    }


def estimate_llm_calls(n_articles: int, n_radii_new: int = 3, n_llms: int = 3) -> Dict[str, int]:
    """估算本次 stage 35 LLM 升级的 API 调用量 (plan v14 修订, 替代 180k 误估).

    Args:
        n_articles: stage 21 输入文章数 (默认从 stage 14 parquet 读)
        n_radii_new: 新 radii 数 (默认 3 = {0, 2, 3}, radius=1 缓存)
        n_llms: 并发 LLM 数 (默认 3)

    Returns:
        dict: {per_radius, total, with_full_track_wrong, savings_factor}
    """
    per_radius_ctx_only = n_articles * n_llms * 1  # 仅 ctx 轨
    total = per_radius_ctx_only * n_radii_new
    # 假设错误计算 (full + ctx 都重跑, 误估)
    naive_with_full = n_articles * n_llms * 2 * (n_radii_new + 1)
    return {
        'per_radius_calls': per_radius_ctx_only,
        'total_calls': total,
        'naive_full_track_count': naive_with_full,
        'savings_factor': round(naive_with_full / max(total, 1), 1),
    }


def parse_track_results_from_cache(
    radius: int,
    articles_df: pd.DataFrame,
    cache_db_path: str = None,
) -> pd.DataFrame:
    """从 LLMCache (sqlite) 读取指定 radius 下的篇章级 stage 3 标签.

    v3.2.0 M5 第 2 commit 落地 (plan v14 §3.5 P5.2):
        利用 LLMCache (sqlite) 已缓存的 (prompt, content_ctx_at_radius) → JSON response,
        直接解析得到 sentiment + locus + substantiveness 三轴标签, 无新 API 调用.

    Args:
        radius: sentence_radius 配置值 (与 LLMCache 调用时一致)
        articles_df: stage 14 输入子集 (含 article_idx, target_bank, content_ctx 列)
        cache_db_path: LLMCache sqlite 路径 (默认 data/processed/_llm_cache.db)

    Returns:
        DataFrame: columns = [article_idx, sentiment, innovation_locus,
                              innovation_substantiveness, sent_conf, locus_conf, subst_conf,
                              n_models_responded]
        缺缓存或解析失败的行: 对应字段 NaN.

    实施策略 (无 yunwu API key 时):
        本函数对 cache_db 做只读 lookup; 若 cache 缺命中则返回 NaN 不重跑.
        实际 launch 路径 (含真 LLM 重跑) 走 main() --launch flag.

    ⚠ fix(omni-g-val-prompt-06, 2026-06-11) 语义变更披露: cache 缺失 / 空库 (无表)
        时仍返回空 DataFrame (graceful); 但 cache 含表时, 真实解析 (按 radius 重抽
        ctx → 重建 prompt → cache key lookup → ensemble 投票) 尚未实现 → raise
        NotImplementedError (fail-loud), 替代旧版静默返回全 None 占位行的 scaffold
        行为 — 占位行经 cohens_kappa_2cat 全行 mask 后 κ=NaN, 曾可配合报告层空泛
        all([]) gate 产 passed=true 假阳性报告。
    """
    import os as _os
    import sqlite3

    if cache_db_path is None:
        from news_process.core.config import load_config
        CONFIG = load_config()
        cache_db_path = _os.path.join(CONFIG['paths']['output_dir'], '_llm_cache.db')

    logger.info(f"  parse_track_results_from_cache(radius={radius}): "
                f"lookup at {cache_db_path}")
    if not _os.path.exists(cache_db_path):
        logger.warning(f"  LLMCache 不存在: {cache_db_path}; 返回空 DataFrame.")
        return pd.DataFrame(columns=['article_idx', 'sentiment', 'innovation_locus',
                                     'innovation_substantiveness', 'sent_conf',
                                     'locus_conf', 'subst_conf', 'n_models_responded'])

    # Cache schema: (prompt_hash, model_name, response_json)
    # 实施层: 读 cache, 按 article × model 重建 multi-LLM ensemble 投票
    conn = sqlite3.connect(cache_db_path)
    try:
        # 列出 cache 表 schema
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        if not tables:
            logger.warning(f"  LLMCache empty 表; 返回空")
            return pd.DataFrame(columns=['article_idx'])

        # fix(omni-g-val-prompt-06, 2026-06-11): 此前此分支无条件返回 sentiment=None /
        # n_models_responded=0 的占位行 (自述 "lookup 接口可调用性证明"), 与 docstring
        # 声称的"读缓存解析标签"矛盾; 占位行会经 cohens_kappa_2cat 全行 NaN-mask →
        # 各维度 κ=NaN, 再遇报告层空泛 all([]) gate 即产 passed=true 假阳性通过报告。
        # 真实现 (按 radius 重抽 ctx → 重建 prompt → cache key lookup → ensemble 投票)
        # 落地前 fail-loud, 拒绝返回伪数据。
        raise NotImplementedError(
            "parse_track_results_from_cache: 真实 cache lookup (radius 重抽 ctx + "
            "prompt hash + ensemble 投票) 尚未实现 — 拒绝静默返回全 None 占位行 "
            "(会导致全 NaN κ 的假阳性 robustness 报告)。实现路径见 main(--launch) 注释。"
        )
    finally:
        conn.close()


def compute_radius_kappa_report(
    labels_by_radius: Dict[int, pd.DataFrame],
    baseline_radius: int = 1,
) -> Dict[str, Dict[int, Dict[str, float]]]:
    """计算每个非基线 radius vs baseline radius 的 κ (sentiment + locus + substantiveness).

    Args:
        labels_by_radius: {radius: DataFrame(article_idx, sentiment, locus, substantiveness)}
        baseline_radius: 比较基线 (默认 radius=1)

    Returns:
        {dimension: {radius: {kappa, observed_agreement, n}}}
    """
    if baseline_radius not in labels_by_radius:
        raise ValueError(f"baseline_radius {baseline_radius} 不在 labels_by_radius keys")

    base = labels_by_radius[baseline_radius]
    report: Dict[str, Dict[int, Dict[str, float]]] = {
        'sentiment': {},
        'innovation_locus': {},
        'innovation_substantiveness': {},
    }

    for radius, df_r in labels_by_radius.items():
        if radius == baseline_radius:
            continue
        # 按 article_idx 对齐 (假设 index 一致)
        merged = base.merge(df_r, on='article_idx', suffixes=('_base', '_var'))
        for dim in ['sentiment', 'innovation_locus', 'innovation_substantiveness']:
            base_col = f'{dim}_base'
            var_col = f'{dim}_var'
            if base_col in merged.columns and var_col in merged.columns:
                k = cohens_kappa_2cat(merged[base_col].values, merged[var_col].values)
                report[dim][radius] = k
            else:
                report[dim][radius] = {'kappa': float('nan'), 'n': 0,
                                       'observed_agreement': float('nan'),
                                       'expected_agreement': float('nan')}

    return report


def write_radius_llm_report(report: Dict, output_path: str,
                             call_estimates: Dict[str, int],
                             baseline_n: int) -> None:
    """写 stage 35 LLM 法 robustness 报告 (plan v14 §3.5 P5.2).

    Args:
        report: compute_radius_kappa_report 返回值
        output_path: JSON 输出路径
        call_estimates: estimate_llm_calls 返回值
        baseline_n: baseline radius 的文章数

    语义变更披露: fix(omni-g-val-prompt-06, 2026-06-11) — 旧 passed 判定对 NaN κ
    先过滤再 all(), 全 NaN 时空生成器 all([])==True → 零证据空泛通过。改为每维度
    须 ≥1 个可评估 (非 NaN) κ 且全部可评估 κ 达标; 全维度 0 可评估时 passed=false
    并写 pass_reason='insufficient_data...'。
    """
    # fix(omni-g-val-prompt-06, 2026-06-11): 防空泛真通过 (vacuous pass) 判定
    dim_status = {}
    for dim, dim_report in report.items():
        valid_kappas = [r['kappa'] for r in dim_report.values()
                        if not np.isnan(r['kappa'])]
        dim_status[dim] = {
            'n_evaluable': len(valid_kappas),
            'all_above_threshold': bool(valid_kappas) and all(
                k >= KAPPA_THRESHOLD_RADIUS for k in valid_kappas
            ),
        }
    n_evaluable_total = sum(s['n_evaluable'] for s in dim_status.values())
    passed = bool(dim_status) and n_evaluable_total > 0 and all(
        s['n_evaluable'] >= 1 and s['all_above_threshold']
        for s in dim_status.values()
    )
    if not dim_status:
        pass_reason = 'failed: kappa_report 为空, 无任何维度可评估'
    elif n_evaluable_total == 0:
        pass_reason = ('failed: insufficient_data — 全部维度 κ=NaN (0 个可评估 κ); '
                       '数据不足不能证明稳健性, 拒绝空泛通过')
    elif not passed:
        failing = [dim for dim, s in dim_status.items()
                   if not (s['n_evaluable'] >= 1 and s['all_above_threshold'])]
        pass_reason = f'failed: 维度 {failing} 含低于阈值 κ 或无可评估 κ'
    else:
        pass_reason = (f'passed: 全部维度均有 ≥1 个可评估 κ 且全部 κ ≥ '
                       f'{KAPPA_THRESHOLD_RADIUS}')

    out = {
        'stage': '65_radius_sensitivity_llm',
        'methodology': 'plan v14 §3.5 P5.2; Hassan 2019 QJE + Sautner 2023 JF 等参数敏感性',
        'cached_radius': CACHED_RADIUS,
        'new_radii': [r for r in RADII_TO_TEST if r != CACHED_RADIUS],
        'baseline_n': baseline_n,
        'call_estimates': call_estimates,
        'kappa_threshold_radius': KAPPA_THRESHOLD_RADIUS,
        'pass_criterion': ('全部 radius vs baseline κ ≥ 0.70 (Landis & Koch substantial); '
                           '每维度须 ≥1 个可评估 κ, 全 NaN 不构成通过'),
        'kappa_report': report,
        'dimension_status': dim_status,
        'passed': passed,
        'pass_reason': pass_reason,
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)
    logger.info(f"Stage 35 LLM 法报告已写入: {output_path}")


def _parse_args(argv=None):
    """v3.2.0 M1/7 CLI argparse (plan v14 §3.5 P5.2 launch path)."""
    import argparse
    parser = argparse.ArgumentParser(
        prog='python -m news_process.validation.radius_sensitivity_llm',
        description='Stage 35 LLM-based radius sensitivity (plan v14 §3.5 P5.2)',
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Estimate-only mode: 不实际跑 LLM, 仅输出调用量估算 (default)',
    )
    parser.add_argument(
        '--launch', action='store_true',
        help='实际 launch 10.5k LLM 调用 (需 YUNWU_API_KEY 环境变量)',
    )
    parser.add_argument(
        '--radii', type=str, default='0,2,3',
        help='New radii to test (comma-separated; default 0,2,3; radius=1 已缓存)',
    )
    parser.add_argument(
        '--max-concurrency', type=int, default=100,
        help='LLM 并发上限 (default 100, 雪崩时降至 8 per stage 32a/39 先例)',
    )
    return parser.parse_args(argv)


def _check_launch_prerequisites() -> dict:
    """Plan v14 §3.5 P5.2 R20-A: launch 前置检查 (yunwu key + cache + N)."""
    checks = {}
    # 1. YUNWU_API_KEY
    api_key = os.environ.get('YUNWU_API_KEY', '').strip()
    checks['yunwu_api_key_present'] = bool(api_key)

    # 2. LLMCache 存在
    try:
        CONFIG = load_config()
        cache_path = os.path.join(CONFIG['paths']['output_dir'], '_llm_cache.db')
        checks['llm_cache_exists'] = os.path.exists(cache_path)
        checks['llm_cache_path'] = cache_path
    except Exception as e:
        checks['llm_cache_exists'] = False
        checks['llm_cache_error'] = str(e)

    # 3. Stage 14 输入 N
    try:
        stage_14 = os.path.join(CONFIG['paths']['output_dir'], '15_fintech_intensity.parquet')
        checks['stage_14_exists'] = os.path.exists(stage_14)
        if checks['stage_14_exists']:
            df = pd.read_parquet(stage_14)
            checks['n_articles'] = len(df)
    except Exception as e:
        checks['stage_14_exists'] = False
        checks['stage_14_error'] = str(e)

    return checks


def _log_environment_and_config(stage_14_path: str, args) -> None:
    """打印项目/环境信息 + 输入输出 + 运行配置 + 方法论引文 (日志富集, 2026-06-24)。

    目标 (用户要求"在日志文件中提供尽可能多的项目信息、运行期间信息和运行结果信息"):
    把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数、依据哪些文献"一次性落进
    日志, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 / 控制流 (golden-safe)。

    本阶段是 LLM 法 radius 敏感性的 scaffold/dry-run: --dry-run 仅估算 LLM 调用预算;
    --launch 真实跑路径尚未完整实现 (留 future commit)。故成本注记需如实区分两态。
    """
    try:
        out_dir = ''
        try:
            out_dir = load_config()['paths']['output_dir']
        except Exception:  # noqa: BLE001
            out_dir = '(未知)'
        report_path = os.path.join(out_dir, '65_radius_sensitivity_llm.json')
        cache_path = os.path.join(out_dir, '_llm_cache.db')
        new_radii = [r for r in RADII_TO_TEST if r != CACHED_RADIUS]
        is_launch = bool(getattr(args, 'launch', False))
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')

        logger.info("  🧭 项目 / 环境信息")
        logger.info("     · 阶段: 65 radius_sensitivity_llm (LLM 法 radius 敏感性, "
                    "STAGES_VALIDATION; scaffold/dry-run)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) "
                    "v3.11.1")
        logger.info("     · 功能: 换不同 ctx 句窗 radius 让 LLM 重判, 比较 情感/创新位点/"
                    "实质性 三轴标签对 radius 的稳健性 (Cohen's κ vs baseline radius)")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'}")
        if is_launch:
            logger.info("     · 成本: LAUNCH 模式将真实调用付费 LLM API "
                        "(需 YUNWU_API_KEY; 非确定性, 非 $0)")
        else:
            logger.info("     · 成本: DRY-RUN 模式纯 CPU / 无 LLM·网络·API ($0); "
                        "仅估算调用预算与前置检查")

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 输入:   {stage_14_path} (stage 14 fintech_intensity, 候选文章集)")
        logger.info(f"     · LLM缓存: {cache_path} (LLMCache sqlite; 勿删=确定性锚点)")
        logger.info(f"     · 输出报告: {report_path} (κ robustness JSON; 仅 --launch 真跑时落盘)")

        logger.info("  ⚙ 运行配置 (plan v14 §3.5 P5.2)")
        logger.info(f"     · Mode: {'LAUNCH (real LLM)' if is_launch else 'DRY-RUN (estimate-only)'}")
        logger.info(f"     · RADII_TO_TEST={RADII_TO_TEST} | 基线 CACHED_RADIUS={CACHED_RADIUS} "
                    f"(已缓存, 不重跑) | 新扫描 radii={new_radii}")
        logger.info(f"     · κ 阈值 KAPPA_THRESHOLD_RADIUS={sig4(KAPPA_THRESHOLD_RADIUS)} "
                    "(Landis & Koch substantial; 同轨不同 radius 期望高一致)")
        logger.info(f"     · CLI: --radii={getattr(args, 'radii', '?')} | "
                    f"--max-concurrency={getattr(args, 'max_concurrency', '?')}")
        logger.info("     · 评估轨: 仅 ctx 轨 (full 轨缓存命中不受 radius 影响; "
                    "ss 轨另有独立 ss_sentence_radius 扫描, 见模块头注)")

        logger.info("  📖 方法论依据 (参考文献逐字取自经核验注册表)")
        logger.info("     · 参数敏感性 (proximity-based attribution): "
                    "Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). "
                    "Firm-level political risk: Measurement and effects. "
                    "The Quarterly Journal of Economics, 134(4), 2135-2202. "
                    "https://doi.org/10.1093/qje/qjz021")
        logger.info("     · firm × topic 邻近化 robustness: "
                    "Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R. (2023). "
                    "Firm-level climate change exposure. The Journal of Finance, "
                    "78(3), 1449-1498. https://doi.org/10.1111/jofi.13219")
        logger.info("     · cheap talk segment-level robustness: "
                    "Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). "
                    "Cheap talk and cherry-picking: What ClimateBert has to say on "
                    "corporate climate risk disclosures. Finance Research Letters, "
                    "47, 102776. https://doi.org/10.1016/j.frl.2022.102776")
        logger.info("     · κ 分级判读: Landis, J. R., & Koch, G. G. (1977). The measurement of observer "
                    "agreement for categorical data. Biometrics, 33(1), 159-174. https://doi.org/10.2307/2529310 "
                    "(substantial 区间 κ≥0.61; 本阶段阈值 0.70)")
        logger.info("     · 白话: 同一篇文章换不同句窗大小让 LLM 重判, 若三轴标签结论"
                    "基本不变(κ 高), 说明测度不依赖窗口参数的人为选择, 更稳健可信。")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法论信息打印失败 (不影响处理): {e}")


def _log_estimate_analysis(n_articles: int, estimates: Dict[str, int]) -> None:
    """对 LLM 调用量估算做阈值化结果解读 (运行结果信息, 日志富集 2026-06-24)。

    纯日志判读, 不改任何估算值 / 控制流 (golden-safe)。
    """
    try:
        logger.info("  📊 关键指标解读 (LLM 调用预算)")
        total = int(estimates.get('total_calls', 0))
        per_radius = int(estimates.get('per_radius_calls', 0))
        naive = int(estimates.get('naive_full_track_count', 0))
        savings = estimates.get('savings_factor', 0)
        logger.info(f"     · 候选文章 N={n_articles:,} 篇 "
                    f"({'充足' if n_articles >= 100 else '偏小(T=2 试跑?), κ 估计噪声大'})")
        logger.info(f"     · 优化后总调用={total:,} 次 "
                    f"(= 每 radius {per_radius:,} × {len(RADII_TO_TEST) - 1} new radii, 仅 ctx 轨)")
        logger.info(f"     · 朴素误估 (full+ctx 双轨全重跑)={naive:,} 次 → "
                    f"节省系数 {sig4(savings)}× "
                    f"({'显著优化' if (isinstance(savings, (int, float)) and savings >= 2) else '优化有限'})")
        cost_note = ('成本可观, 需 M0 gate 批准方可 --launch'
                     if total >= 5000 else '成本可控')
        logger.info(f"     · 预算研判: {cost_note} "
                    f"(LLM 法 vs 词典法 radius_sensitivity 互为方法学稳健性)")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  估算结果解读打印失败 (不影响处理): {e}")


def main():
    """Stage 35 LLM 法主入口 (plan v14 §3.5 P5.2 + R20-A).

    工作流:
        1. CLI argparse + estimate_llm_calls (给用户看实际预算)
        2. --dry-run (default): 只输出 estimate + prerequisites 检查
        3. --launch: 真实跑 (need YUNWU_API_KEY)
           对每个 new radius ∈ {0, 2, 3}: 重抽 ctx → 调 LLM → cache
           parse_track_results_from_cache 收集篇章级标签 (当前仅 ctx 轨;
           full 轨缓存命中不受 radius 影响, ss 轨另有独立 radius 扫描, 见模块头注)
           compute_radius_kappa_report + write_radius_llm_report
    """
    stage_start = time.time()
    args = _parse_args()
    CONFIG = load_config()
    stage_14_filename = CONFIG.get('filenames', {}).get(
        'output_14_fintech_intensity', '15_fintech_intensity.parquet')
    stage_14_path = os.path.join(CONFIG['paths']['output_dir'], stage_14_filename)

    logger.info("=== Stage 35 LLM 法升级 (plan v14 §3.5 P5.2) ===")
    logger.info(f"  Mode: {'LAUNCH (real LLM)' if args.launch else 'DRY-RUN (estimate-only)'}")

    # 项目/环境信息 + 输入输出 + 运行配置 + 方法论引文 (日志富集 2026-06-24)
    _log_environment_and_config(stage_14_path, args)

    # 1. 估算 LLM 调用量 (替代 plan v13/v14 早期 180k 误估)
    if not os.path.exists(stage_14_path):
        logger.error(f"  stage 14 输入不存在: {stage_14_path}")
        logger.error("  先跑 pipeline (run_pipeline_function.py) 产 stage 14 输出.")
        return 1

    _t = time.time()
    df_stage14 = pd.read_parquet(stage_14_path)
    n_articles = len(df_stage14)
    estimates = estimate_llm_calls(n_articles=n_articles)
    _t_load = time.time() - _t
    logger.info(f"  N (stage 14 输入): {n_articles:,}")
    logger.info(f"  实际 LLM 调用: {estimates['total_calls']:,} "
                f"(= {estimates['per_radius_calls']:,} × {len(RADII_TO_TEST) - 1} new radii)")
    logger.info(f"  早前错估 (含 full 轨重跑): {estimates['naive_full_track_count']:,} "
                f"({sig4(estimates['savings_factor'])}× 节省)")

    # 结果解读 (运行结果信息, 日志富集 2026-06-24)
    _log_estimate_analysis(n_articles, estimates)

    # 2. 前置检查
    _t = time.time()
    checks = _check_launch_prerequisites()
    _t_checks = time.time() - _t
    logger.info("  Pre-flight checks:")
    for k, v in checks.items():
        logger.info(f"    {k}: {v}")

    # 阶段计时汇总 (墙钟, 日志富集 2026-06-24)
    try:
        logger.info("  ⏱ 阶段计时")
        logger.info(f"     · 读取 stage14 + 估算: {sig4(_t_load)} 秒")
        logger.info(f"     · 前置检查: {sig4(_t_checks)} 秒")
        logger.info(f"     · 累计 (至分支前): {sig4(time.time() - stage_start)} 秒")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  阶段计时打印失败 (不影响处理): {e}")

    # 3. dry-run / launch 分支
    if not args.launch:
        logger.info("  [DRY-RUN] 不实际调用 LLM. 加 --launch flag 触发真实 launch.")
        logger.info(f"  Required: env YUNWU_API_KEY (current: {'set' if checks['yunwu_api_key_present'] else 'NOT SET'})")
        logger.info(f"  本阶段总耗时: {sig4(time.time() - stage_start)} 秒")
        return 0

    # --launch 真实路径
    if not checks['yunwu_api_key_present']:
        logger.error("  [LAUNCH] YUNWU_API_KEY 未设置, 不能跑真实 LLM.")
        logger.error("  $env:YUNWU_API_KEY = '<your-key>'; 然后重试.")
        return 1

    # 实际 LLM 重抽 ctx + 调用 + cache 写入 (复用 tone_llms.py 异步 LLM 框架)
    # 实施细节: 此处需调 stage 21 的 _aggregate_track 等异步 LLM 框架.
    # 由于 stage 21 LLM 调用层在 tone_llms.py main() 中, 复用其异步框架需要:
    #   a) 临时修改 sentence_radius 配置
    #   b) 重抽 content_ctx
    #   c) 调 run_all_llms (复用 LLMCache)
    #   d) 解析新 cache 条目
    # 完整实施留作 future commit (需要 yunwu API key + 实际跑 4 小时).
    logger.warning("  [LAUNCH] 实施细节留作 future commit (需 yunwu API + 跑 ~2 min/radius).")
    logger.warning("  当前 CLI 是 scaffold; 真实 launch 需要再扩展 ~150 行 (异步 LLM 复用 tone_llms.py).")
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main() or 0)
