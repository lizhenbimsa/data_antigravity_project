"""
36_entity_masking_test.py — 阶段36：Entity Masking 稳健性测试（双轨版）
=====================================================================

功能：
    通过将目标银行和共提银行名称替换为匿名占位符，验证 LLM 判定是否依赖
    文本语义内容而非实体先验知识（如 "工商银行 → 国有大行 → 稳健"）。

    【双轨测试】每条新闻同时以全文 (_full) 和实体特异性上下文片段 (_ctx)
    两种输入分别执行掩码替换与 LLM 重判，生成两套独立的一致性指标，
    验证稳健性结论不受文本输入粒度的影响。

    流程：
      1. 加载全量 LLM 结果（含 verified=True/False）
      2. 随机抽样 N=1000 条
      3. 提取 baseline 判定（full + ctx 双轨已有列）
      4. 银行名 → 匿名占位符替换 + 实体残留检测（双轨）
      5. 掩码文本重新调用 3 模型 LLM 判定（双轨）
      6. 计算四维一致性指标（验证一致率、情感一致率、Cohen's κ、逐模型分解）× 双轨
      7. 生成 JSON/CSV/LaTeX/PNG 报告（含双轨对比）

    学术依据：
      - SSRN-4558295 §7.2: Entity substitution robustness check
      - Landis & Koch (1977, Biometrics 33(1):159-174): Cohen's κ 解释标准
        κ ≥ 0.81 → "almost perfect agreement"
        注: 本模块计算的是 Cohen's κ（2 编码者名义一致性），
        解释阈值出自 Landis & Koch (1977)，而非 Krippendorff's α

输入：
    `21_tone_llms_full.parquet`（全量 LLM 判定结果，含 full 和 ctx 双轨列）

输出：
    `eval_reports/entity_masking_results.json`  — 双轨四维指标 + 判定
    `eval_reports/entity_masking_detail.csv`    — 逐条对比
    `eval_reports/entity_masking_table.tex`     — 论文就绪表格（含双轨 Panel）
    `eval_reports/entity_masking_confusion.png` — 混淆矩阵（full + ctx 并排）
"""

import os
import sys
import time
import json
import logging
import asyncio
import aiohttp
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from importlib import import_module
from utils.helpers import load_config, setup_logging, save_dataset

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "36_entity_masking_test"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 复用 21_tone_llms.py 的 LLM 基础设施
_tone_llms = import_module('21_tone_llms')
fetch_llm_async  = _tone_llms.fetch_llm_async
_aggregate_track = _tone_llms._aggregate_track
MODELS           = _tone_llms.MODELS
PROMPT_TEMPLATE  = _tone_llms.PROMPT_TEMPLATE
MAX_CONCURRENCY  = _tone_llms.MAX_CONCURRENCY

# get_target_aliases + extract_entity_context 在 utils.entity_context 中
from utils.entity_context import get_target_aliases, extract_entity_context

# 复用评估模块的 Cohen's Kappa
_eval = import_module('33_news_llms_evaluation')
compute_cohens_kappa = _eval.compute_cohens_kappa

# Entity Masking 配置
EM_CFG = CONFIG.get('entity_masking_test', {})
PLACEHOLDER = EM_CFG.get('placeholder', '目标银行A')
PEER_TEMPLATE = EM_CFG.get('peer_placeholder_template', '同业银行{}')

# 双轨标识
TRACKS = ['full', 'ctx']


# ============================================================================
# 2. 抽样与 Baseline
# ============================================================================

def random_sample(df: pd.DataFrame, sample_size: int, seed: int) -> pd.DataFrame:
    """简单随机抽样（可复现）。"""
    n = min(sample_size, len(df))
    return df.sample(n=n, random_state=seed)


def extract_baseline(df_sample: pd.DataFrame) -> pd.DataFrame:
    """从样本中提取已有的 LLM 判定作为 baseline（双轨）。"""
    df = df_sample.copy()

    for track in TRACKS:
        suffix = f'_{track}'

        # 整体投票结果
        df[f'baseline_verified_{track}'] = df[f'llm_verified{suffix}']
        df[f'baseline_sentiment_{track}'] = df[f'llm_sentiment{suffix}']

        # 逐模型结果
        for m in MODELS:
            short = m['short_name']
            df[f'{short}_baseline_verified_{track}'] = df[f'{short}_verified{suffix}']
            df[f'{short}_baseline_sentiment_{track}'] = df[f'{short}_sentiment{suffix}']

    return df


# ============================================================================
# 3. 银行名替换与残留检测
# ============================================================================

def mask_entity(
    text: str,
    title: str,
    target_bank: str,
    target_aliases: list,
    co_mentioned_banks: str,
    bank_names_file: str,
) -> dict:
    """将目标银行及共提银行名称替换为匿名占位符。

    关键实现:
      1. 按别名长度降序替换（防短别名先匹配导致长别名残留）
      2. 共提银行各用不同占位符（同业银行B, C, D...）
      3. 标题和正文均执行替换
      4. 统计替换次数用于质量验证

    Returns:
        dict: masked_text, masked_title, masked_target, masked_co_mentioned, n_replacements
    """
    masked_text, masked_title = text, title
    n_replacements = 0

    # 1. 替换目标银行（按长度降序）
    for alias in sorted(target_aliases, key=len, reverse=True):
        cnt = masked_text.count(alias) + masked_title.count(alias)
        masked_text = masked_text.replace(alias, PLACEHOLDER)
        masked_title = masked_title.replace(alias, PLACEHOLDER)
        n_replacements += cnt

    # 2. 替换共提银行
    masked_peers = []
    if co_mentioned_banks and str(co_mentioned_banks).strip():
        for i, peer in enumerate(
            b.strip() for b in str(co_mentioned_banks).split(';') if b.strip()
        ):
            peer_ph = PEER_TEMPLATE.format(chr(66 + i))  # B, C, D...
            peer_aliases = get_target_aliases(peer, bank_names_file)
            for alias in sorted(peer_aliases, key=len, reverse=True):
                cnt = masked_text.count(alias)
                masked_text = masked_text.replace(alias, peer_ph)
                masked_title = masked_title.replace(alias, peer_ph)
                n_replacements += cnt
            masked_peers.append(peer_ph)

    return {
        'masked_text': masked_text,
        'masked_title': masked_title,
        'masked_target': PLACEHOLDER,
        'masked_co_mentioned': ';'.join(masked_peers) if masked_peers else '无',
        'n_replacements': n_replacements,
    }


def verify_masking_completeness(
    masked_text: str,
    original_aliases: list,
    co_bank_aliases: list,
) -> dict:
    """检查掩码文本中是否仍残留原始银行名。"""
    residuals = [a for a in original_aliases + co_bank_aliases if a in masked_text]
    return {'complete': len(residuals) == 0, 'residual_aliases': residuals}


# ============================================================================
# 4. LLM 调用（掩码后文本，双轨）
# ============================================================================

async def run_masked_llms(df_masked: pd.DataFrame, models: list) -> dict:
    """对掩码后数据执行 LLM 判定（full + ctx 双轨）。

    Args:
        df_masked: 必须包含 masked_text_full, masked_title, masked_target,
                   masked_co_mentioned, masked_text_ctx 列。

    Returns:
        dict: {row_idx: {'full': {model_id: response_text},
                         'ctx':  {model_id: response_text}}}
    """
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    results_map = {i: {'full': {}, 'ctx': {}} for i in df_masked.index}

    connector = aiohttp.TCPConnector(
        limit=MAX_CONCURRENCY, keepalive_timeout=30, enable_cleanup_closed=True,
    )
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for idx, row in df_masked.iterrows():
            for track in TRACKS:
                content_col = f'masked_text_{track}'
                prompt = PROMPT_TEMPLATE.format(
                    title=row['masked_title'],
                    content=row[content_col],
                    target_bank=row['masked_target'],
                    co_mentioned_banks=row['masked_co_mentioned'],
                )
                for m in models:
                    tasks.append(
                        fetch_llm_async(session, semaphore, prompt, m, idx, track)
                    )

        logger.info(f"🔬 Entity Masking LLM 双轨请求: "
                    f"{len(df_masked)} 条 × {len(models)} 模型 × 2 轨道 = {len(tasks)} 请求")

        completed = 0
        total = len(tasks)
        report_interval = max(1, total // 20)
        next_report = report_interval

        for coro in asyncio.as_completed(tasks):
            row_idx, model_id, res_text, track = await coro
            results_map[row_idx][track][model_id] = res_text
            completed += 1
            if completed >= next_report or completed == total:
                pct = completed / total * 100
                logger.info(f"📡 Entity Masking 进度: {completed}/{total} ({pct:.1f}%)")
                next_report += report_interval

    return results_map


# ============================================================================
# 5. 四维一致性指标（支持轨道后缀参数化）
# ============================================================================

def compute_masking_consistency(df_result: pd.DataFrame, track: str) -> dict:
    """计算 Entity Masking 某一轨道的四维一致性指标。

    四维:
      1. 验证一致率 — is_bank_fintech_news 掩码前后一致比例
      2. 情感一致率 — sentiment 一致比例（仅对双方均判真子集）
      3. Cohen's κ   — 排除随机一致后的验证一致度
      4. 逐模型分解 — 每个 LLM 独立的一致率

    Args:
        df_result: 含 baseline_verified_{track}, masked_verified_{track} 等列。
        track: 'full' 或 'ctx'。

    Returns:
        dict: 四维一致性指标。
    """
    b_ver = f'baseline_verified_{track}'
    m_ver = f'masked_verified_{track}'
    b_sen = f'baseline_sentiment_{track}'
    m_sen = f'masked_sentiment_{track}'

    # 1. 验证一致率
    ver_match = (df_result[b_ver] == df_result[m_ver]).mean()

    # 2. 情感一致率（条件子集）
    both_true = df_result[b_ver] & df_result[m_ver]
    n_both_true = int(both_true.sum())
    sen_match = (
        (df_result.loc[both_true, b_sen] ==
         df_result.loc[both_true, m_sen]).mean()
        if n_both_true > 0 else float('nan')
    )

    # 3. Cohen's Kappa
    kappa = compute_cohens_kappa(
        df_result[b_ver].astype(int).values,
        df_result[m_ver].astype(int).values,
    )

    # 4. 逐模型一致率
    per_model = {}
    for m in MODELS:
        short = m['short_name']
        b_col = f'{short}_baseline_verified_{track}'
        m_col = f'{short}_masked_verified_{track}'
        if b_col in df_result.columns and m_col in df_result.columns:
            valid = df_result[b_col].notna() & df_result[m_col].notna()
            if valid.sum() > 0:
                per_model[short] = round(
                    (df_result.loc[valid, b_col] == df_result.loc[valid, m_col]).mean(), 4
                )

    return {
        'track': track,
        'verification_consistency': round(ver_match, 4),
        'sentiment_consistency': round(sen_match, 4) if not pd.isna(sen_match) else None,
        'cohens_kappa': kappa,
        'per_model_consistency': per_model,
        'n_samples': len(df_result),
        'n_both_true': n_both_true,
        'n_zero_replacements': int((df_result[f'n_replacements_{track}'] == 0).sum()),
    }


# ============================================================================
# 6. 报告生成（双轨对比）
# ============================================================================

def generate_report(
    consistency_full: dict,
    consistency_ctx: dict,
    df_sample: pd.DataFrame,
    df_valid_full: pd.DataFrame,
    df_valid_ctx: pd.DataFrame,
):
    """生成 JSON/CSV/LaTeX/PNG 报告（双轨对比）。"""
    report_dir = os.path.join(CONFIG['paths']['output_dir'], 'eval_reports')
    os.makedirs(report_dir, exist_ok=True)

    combined = {
        'full': consistency_full,
        'ctx': consistency_ctx,
    }

    # 6.1 JSON 报告
    json_path = os.path.join(report_dir, 'entity_masking_results.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=2, default=str)
    logger.info(f"JSON 报告已保存: {json_path}")

    # 6.2 CSV 逐条对比
    csv_path = os.path.join(report_dir, 'entity_masking_detail.csv')
    detail_cols = []
    for track in TRACKS:
        detail_cols.extend([
            f'baseline_verified_{track}', f'masked_verified_{track}',
            f'baseline_sentiment_{track}', f'masked_sentiment_{track}',
            f'n_replacements_{track}',
        ])
        for m in MODELS:
            short = m['short_name']
            detail_cols.extend([
                f'{short}_baseline_verified_{track}', f'{short}_masked_verified_{track}',
            ])
    available_cols = [c for c in detail_cols if c in df_sample.columns]
    df_sample[available_cols].to_csv(csv_path, index=True, encoding='utf-8-sig')
    logger.info(f"CSV 详情已保存: {csv_path}")

    # 6.3 LaTeX 表格（双轨 Panel 对比）
    tex_path = os.path.join(report_dir, 'entity_masking_table.tex')
    n_total = consistency_full['n_samples']

    tex_lines = [
        r'\begin{table}[htbp]',
        r'\centering',
        r'\caption{Entity Masking Robustness Test --- Dual-Track Comparison ($N=' + str(n_total) + r'$)}',
        r'\label{tab:entity_masking}',
        r'\begin{tabular}{lccc}',
        r'\hline',
        r'Metric & Full Track & Ctx Track & $\Delta$ \\',
        r'\hline',
        r'\multicolumn{4}{l}{\textit{Panel A: Aggregate Consistency}} \\',
    ]

    for label_name, key in [
        ('Verification Agreement', 'verification_consistency'),
        ('Sentiment Agreement (cond.)', 'sentiment_consistency'),
    ]:
        v_full = consistency_full[key]
        v_ctx = consistency_ctx[key]
        if v_full is not None and v_ctx is not None:
            delta = v_full - v_ctx
            # 注: 不使用 Python format spec '.1%'，因为其输出的裸 '%' 在
            # LaTeX 中是注释符，会导致同行后续列被吞掉。
            # 改为手动 ×100 + \\% 转义，与 per-model 行一致。
            tex_lines.append(
                f'\\quad {label_name} & {v_full*100:.1f}\\% & {v_ctx*100:.1f}\\% & {delta*100:+.1f}pp \\\\'
            )
        else:
            v_full_s = f'{v_full*100:.1f}\\%' if v_full is not None else 'N/A'
            v_ctx_s = f'{v_ctx*100:.1f}\\%' if v_ctx is not None else 'N/A'
            tex_lines.append(f'\\quad {label_name} & {v_full_s} & {v_ctx_s} & --- \\\\')

    # Cohen's κ
    kf = consistency_full['cohens_kappa']['kappa']
    kc = consistency_ctx['cohens_kappa']['kappa']
    dk = kf - kc
    tex_lines.append(
        f"\\quad Cohen's $\\kappa$ (Verification) & {kf:.4f} & {kc:.4f} & {dk:+.4f} \\\\"
    )

    tex_lines.append(r'\hline')
    tex_lines.append(r'\multicolumn{4}{l}{\textit{Panel B: Per-Model Breakdown (Full / Ctx)}} \\')
    for m in MODELS:
        short = m['short_name']
        vf = consistency_full['per_model_consistency'].get(short)
        vc = consistency_ctx['per_model_consistency'].get(short)
        if vf is not None and vc is not None:
            tex_lines.append(f'\\quad {short} & {vf*100:.1f}\\% & {vc*100:.1f}\\% & {(vf-vc)*100:+.1f}pp \\\\')

    tex_lines.extend([
        r'\hline',
        r'\end{tabular}',
        r'\begin{tablenotes}[flushleft]\footnotesize',
        r"  \item Each article's target bank name and co-mentioned bank names",
        r'  are replaced with anonymized placeholders. The LLM ensemble is',
        r'  re-queried on both full-text and entity-context tracks. Agreement',
        r'  is computed between original and masked predictions for each track.',
        r'\end{tablenotes}',
        r'\end{table}',
    ])
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(tex_lines))
    logger.info(f"LaTeX 表格已保存: {tex_path}")

    # 6.4 混淆矩阵 (PNG) — 双轨并排
    try:
        _generate_confusion_matrix_dual(df_valid_full, df_valid_ctx, report_dir)
    except Exception as e:
        logger.warning(f"混淆矩阵生成失败: {e}")


def _generate_confusion_matrix_dual(
    df_valid_full: pd.DataFrame,
    df_valid_ctx: pd.DataFrame,
    report_dir: str,
):
    """生成验证任务的掩码前后混淆矩阵（双轨并排）。"""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    for ax, df_valid, track in zip(axes, [df_valid_full, df_valid_ctx], TRACKS):
        b = df_valid[f'baseline_verified_{track}'].astype(int).values
        m = df_valid[f'masked_verified_{track}'].astype(int).values

        # 2×2 混淆矩阵
        tp = int(((b == 1) & (m == 1)).sum())
        tn = int(((b == 0) & (m == 0)).sum())
        fp = int(((b == 0) & (m == 1)).sum())
        fn = int(((b == 1) & (m == 0)).sum())
        cm = np.array([[tn, fp], [fn, tp]])

        im = ax.imshow(cm, cmap='Blues', interpolation='nearest')
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(['False', 'True'], fontsize=11)
        ax.set_yticklabels(['False', 'True'], fontsize=11)
        ax.set_xlabel('Masked Prediction', fontsize=12)
        ax.set_ylabel('Baseline Prediction', fontsize=12)
        ax.set_title(f'Entity Masking: {track.upper()} Track', fontsize=13)

        for i in range(2):
            for j in range(2):
                color = 'white' if cm[i, j] > cm.max() / 2 else 'black'
                ax.text(j, i, str(cm[i, j]), ha='center', va='center',
                        fontsize=15, fontweight='bold', color=color)

        fig.colorbar(im, ax=ax, shrink=0.8)

    plt.tight_layout()
    png_path = os.path.join(report_dir, 'entity_masking_confusion.png')
    fig.savefig(png_path, dpi=150)
    plt.close(fig)
    logger.info(f"混淆矩阵已保存: {png_path}")


# ============================================================================
# 7. 主流程
# ============================================================================

def main():
    stage_start = time.time()
    logger.info("=" * 60)
    logger.info("--- 开始执行 Entity Masking 稳健性测试（双轨版） ---")
    logger.info("=" * 60)
    logger.info("")
    logger.info("  📌 阶段目的")
    logger.info("     将目标银行名替换为匿名占位符(如 '工商银行'→'[BANK_A]'),")
    logger.info("     验证 LLM 情感判定是否依赖文本语义, 而非实体先验知识。")
    logger.info("     同时在全文(full)和上下文片段(ctx)两条轨道上独立验证,")
    logger.info("     确保稳健性结论不受文本输入粒度的影响。")
    logger.info("")
    logger.info("  📖 方法论依据")
    logger.info("     · SSRN-4558295 §7.2: Entity substitution robustness check")
    logger.info("     · Landis & Koch (1977, Biometrics 33(1):159-174): Cohen's κ 解释标准")
    logger.info("")
    logger.info("  📊 关键指标解读")
    logger.info("     · 验证一致率 ≥ 90%: 判定不受实体身份干扰, 稳健性优秀")
    logger.info("     · Cohen's κ: ≥0.81 almost perfect, 0.61-0.80 substantial, 0.41-0.60 moderate")
    logger.info("     · 实体残留率: 应为 0%, 否则掩码替换不完整")
    logger.info("     · 双轨差异(Δ): full 与 ctx 指标差异应 <5pp, 否则提示文本粒度敏感")
    logger.info("")

    # ── 配置 ──
    if not EM_CFG.get('enabled', False):
        logger.info("Entity Masking 测试已禁用 (enabled=false)，跳过")
        return

    sample_size = EM_CFG.get('sample_size', 1000)
    seed = EM_CFG.get('random_seed', 42)
    bnf = CONFIG['paths'].get('bank_names_file', '')

    # ── Step 1: 加载全量 LLM 结果 ──
    input_path = os.path.join(
        CONFIG['paths']['output_dir'],
        CONFIG.get('filenames', {}).get('output_21_tone_llms_full', '21_tone_llms_full.parquet')
    )
    if not os.path.exists(input_path):
        logger.error(f"输入文件不存在: {input_path}")
        return
    df = pd.read_parquet(input_path)
    logger.info(f"加载全量 LLM 结果: {len(df)} 条")

    # 确认 content_ctx 列存在
    if 'content_ctx' not in df.columns:
        logger.warning("输入数据缺少 content_ctx 列，ctx 轨道将回退至全文")
        df['content_ctx'] = df['内容'].astype(str)

    # ── Step 2: 随机抽样 ──
    df_sample = random_sample(df, sample_size, seed)
    logger.info(f"随机抽样 {len(df_sample)} 条 (seed={seed})")

    # ── Step 3: 提取 baseline（双轨）──
    df_sample = extract_baseline(df_sample)

    # ── Step 4: 执行掩码替换（双轨）──
    n_incomplete = {'full': 0, 'ctx': 0}
    for idx, row in df_sample.iterrows():
        aliases = get_target_aliases(str(row['target_bank']), bnf)
        co_banks_str = str(row.get('co_mentioned_banks', ''))

        # 预计算共提银行别名（两轨共用）
        co_aliases = []
        if co_banks_str.strip():
            for peer in co_banks_str.split(';'):
                peer_stripped = peer.strip()
                if peer_stripped:
                    co_aliases.extend(get_target_aliases(peer_stripped, bnf))

        # ── Full 轨道掩码 ──
        result_full = mask_entity(
            str(row['内容']), str(row['标题']),
            str(row['target_bank']), aliases, co_banks_str, bnf,
        )
        completeness_full = verify_masking_completeness(
            result_full['masked_text'], aliases, co_aliases
        )
        if not completeness_full['complete']:
            n_incomplete['full'] += 1
            logger.warning(f"行 {idx} [full]: 实体残留 {completeness_full['residual_aliases']}")

        df_sample.at[idx, 'masked_text_full'] = result_full['masked_text']
        df_sample.at[idx, 'masked_title'] = result_full['masked_title']
        df_sample.at[idx, 'masked_target'] = result_full['masked_target']
        df_sample.at[idx, 'masked_co_mentioned'] = result_full['masked_co_mentioned']
        df_sample.at[idx, 'n_replacements_full'] = result_full['n_replacements']

        # ── Ctx 轨道掩码 ──
        content_ctx = str(row.get('content_ctx', row['内容']))
        result_ctx = mask_entity(
            content_ctx, str(row['标题']),
            str(row['target_bank']), aliases, co_banks_str, bnf,
        )
        completeness_ctx = verify_masking_completeness(
            result_ctx['masked_text'], aliases, co_aliases
        )
        if not completeness_ctx['complete']:
            n_incomplete['ctx'] += 1
            logger.warning(f"行 {idx} [ctx]: 实体残留 {completeness_ctx['residual_aliases']}")

        df_sample.at[idx, 'masked_text_ctx'] = result_ctx['masked_text']
        df_sample.at[idx, 'n_replacements_ctx'] = result_ctx['n_replacements']

    for track in TRACKS:
        n_zero = int((df_sample[f'n_replacements_{track}'] == 0).sum())
        logger.info(f"[{track}] 掩码替换完成: {len(df_sample)} 条, "
                    f"残留异常 {n_incomplete[track]} 条, "
                    f"零替换 {n_zero} 条")

    # ── Step 5: 调用 LLM（掩码后文本，双轨）──
    masked_llm_results = asyncio.run(run_masked_llms(df_sample, MODELS))

    # ── Step 6: 解析 + 投票（双轨）──
    for idx in df_sample.index:
        row_res = masked_llm_results.get(idx, {'full': {}, 'ctx': {}})

        for track in TRACKS:
            final_v, final_s, agree_rate, parsed, _, _, n_fail = \
                _aggregate_track(row_res.get(track, {}), MODELS)

            df_sample.at[idx, f'masked_verified_{track}'] = final_v
            df_sample.at[idx, f'masked_sentiment_{track}'] = final_s

            for m in MODELS:
                short = m['short_name']
                df_sample.at[idx, f'{short}_masked_verified_{track}'] = parsed.get(f'{short}_verified')
                df_sample.at[idx, f'{short}_masked_sentiment_{track}'] = parsed.get(f'{short}_sentiment')

    # ── Step 7: 计算一致性（排除零替换异常条）──
    results = {}
    df_valids = {}
    for track in TRACKS:
        df_valid = df_sample[df_sample[f'n_replacements_{track}'] > 0].copy()
        if len(df_valid) == 0:
            logger.error(f"[{track}] 零替换条数等于总样本数，无法计算一致性指标")
            return
        df_valids[track] = df_valid
        results[track] = compute_masking_consistency(df_valid, track)

    # ── Step 8: 判定（双轨均须通过）──
    thresholds = {
        'verification': EM_CFG.get('pass_threshold_verification', 0.90),
        'sentiment': EM_CFG.get('pass_threshold_sentiment', 0.85),
        'kappa': EM_CFG.get('pass_threshold_kappa', 0.80),
    }

    for track in TRACKS:
        c = results[track]
        passed = (
            c['verification_consistency'] >= thresholds['verification']
            and (c['sentiment_consistency'] is None
                 or c['sentiment_consistency'] >= thresholds['sentiment'])
            and c['cohens_kappa']['kappa'] >= thresholds['kappa']
        )
        c['passed'] = passed
        c['thresholds'] = thresholds

        sen_display = (f"{c['sentiment_consistency']:.1%}"
                       if c['sentiment_consistency'] is not None else 'N/A')
        logger.info(f"[{track.upper()}] {'✅ 通过' if passed else '❌ 未通过'}: "
                    f"验证一致率={c['verification_consistency']:.1%}, "
                    f"情感一致率={sen_display}, "
                    f"κ={c['cohens_kappa']['kappa']:.4f}")

    # 双轨综合判定
    overall_pass = results['full']['passed'] and results['ctx']['passed']
    logger.info(f"{'✅' if overall_pass else '❌'} 双轨综合判定: "
                f"full={'通过' if results['full']['passed'] else '未通过'}, "
                f"ctx={'通过' if results['ctx']['passed'] else '未通过'}")

    # 双轨差异诊断
    delta_ver = abs(results['full']['verification_consistency'] - results['ctx']['verification_consistency'])
    delta_kappa = abs(results['full']['cohens_kappa']['kappa'] - results['ctx']['cohens_kappa']['kappa'])
    if delta_ver > 0.05 or delta_kappa > 0.05:
        logger.warning(f"⚠️ 双轨差异较大: Δ验证一致率={delta_ver:.1%}, Δκ={delta_kappa:.4f}")
        logger.warning("   提示: 文本输入粒度可能影响稳健性，建议检查 ctx 提取质量")
    else:
        logger.info(f"   双轨差异正常: Δ验证一致率={delta_ver:.1%}, Δκ={delta_kappa:.4f}")

    # ── Step 9: 输出报告 ──
    generate_report(
        results['full'], results['ctx'],
        df_sample,
        df_valids['full'], df_valids['ctx'],
    )
    logger.info(f"Entity Masking 双轨测试完成, 耗时 {time.time()-stage_start:.1f}s")


if __name__ == "__main__":
    main()
