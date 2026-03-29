"""
36_entity_masking_test.py — 第三十六阶段：Entity Masking 稳健性测试
=====================================================================

功能：
    通过将目标银行和共提银行名称替换为匿名占位符，验证 LLM 判定是否依赖
    文本语义内容而非实体先验知识（如 "工商银行 → 国有大行 → 稳健"）。

    流程：
      1. 加载全量 LLM 结果（含 verified=True/False）
      2. 随机抽样 N=1000 条
      3. 提取 baseline 判定（已有列，无需重算）
      4. 银行名 → 匿名占位符替换 + 实体残留检测
      5. 掩码文本重新调用 3 模型 LLM 判定
      6. 计算四维一致性指标（验证一致率、情感一致率、Cohen's κ、逐模型分解）
      7. 生成 JSON/CSV/LaTeX/PNG 报告

    学术依据：
      - SSRN-4558295 §7.2: Entity substitution robustness check
      - Landis & Koch (1977, Biometrics 33(1):159-174): Cohen's κ 解释标准
        κ ≥ 0.81 → "almost perfect agreement"
        注: 本模块计算的是 Cohen's κ（2 编码者名义一致性），
        解释阈值出自 Landis & Koch (1977)，而非 Krippendorff's α

输入：
    `21_tone_llms_full.parquet`（全量 LLM 判定结果）

输出：
    `eval_reports/entity_masking_results.json`  — 四维指标 + 判定
    `eval_reports/entity_masking_detail.csv`    — 逐条对比
    `eval_reports/entity_masking_table.tex`     — 论文就绪表格
    `eval_reports/entity_masking_confusion.png` — 混淆矩阵
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

# get_target_aliases 在 utils.entity_context 中
from utils.entity_context import get_target_aliases

# 复用评估模块的 Cohen's Kappa
_eval = import_module('33_news_llms_evaluation')
compute_cohens_kappa = _eval.compute_cohens_kappa

# Entity Masking 配置
EM_CFG = CONFIG.get('entity_masking_test', {})
PLACEHOLDER = EM_CFG.get('placeholder', '目标银行A')
PEER_TEMPLATE = EM_CFG.get('peer_placeholder_template', '同业银行{}')


# ============================================================================
# 2. 抽样与 Baseline
# ============================================================================

def random_sample(df: pd.DataFrame, sample_size: int, seed: int) -> pd.DataFrame:
    """简单随机抽样（可复现）。"""
    n = min(sample_size, len(df))
    return df.sample(n=n, random_state=seed)


def extract_baseline(df_sample: pd.DataFrame) -> pd.DataFrame:
    """从样本中提取已有的 LLM 判定作为 baseline。"""
    df = df_sample.copy()

    # 整体投票结果
    df['baseline_verified'] = df['llm_verified_full']
    df['baseline_sentiment'] = df['llm_sentiment_full']

    # 逐模型结果
    for m in MODELS:
        short = m['short_name']
        df[f'{short}_baseline_verified'] = df[f'{short}_verified_full']
        df[f'{short}_baseline_sentiment'] = df[f'{short}_sentiment_full']

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
# 4. LLM 调用（掩码后文本）
# ============================================================================

async def run_masked_llms(df_masked: pd.DataFrame, models: list) -> dict:
    """对掩码后数据执行 LLM 判定（仅 full 轨道）。

    Args:
        df_masked: 必须包含 masked_text, masked_title, masked_target, masked_co_mentioned 列。

    Returns:
        dict: {row_idx: {model_id: response_text}}
    """
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    results_map = {i: {} for i in df_masked.index}

    connector = aiohttp.TCPConnector(
        limit=MAX_CONCURRENCY, keepalive_timeout=30, enable_cleanup_closed=True,
    )
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for idx, row in df_masked.iterrows():
            prompt = PROMPT_TEMPLATE.format(
                title=row['masked_title'],
                content=row['masked_text'],
                target_bank=row['masked_target'],
                co_mentioned_banks=row['masked_co_mentioned'],
            )
            for m in models:
                tasks.append(
                    fetch_llm_async(session, semaphore, prompt, m, idx, 'full')
                )

        logger.info(f"🔬 Entity Masking LLM 请求: "
                    f"{len(df_masked)} 条 × {len(models)} 模型 = {len(tasks)} 请求")

        completed = 0
        total = len(tasks)
        report_interval = max(1, total // 20)
        next_report = report_interval

        for coro in asyncio.as_completed(tasks):
            row_idx, model_id, res_text, _ = await coro
            results_map[row_idx][model_id] = res_text
            completed += 1
            if completed >= next_report or completed == total:
                pct = completed / total * 100
                logger.info(f"📡 Entity Masking 进度: {completed}/{total} ({pct:.1f}%)")
                next_report += report_interval

    return results_map


# ============================================================================
# 5. 四维一致性指标
# ============================================================================

def compute_masking_consistency(df_result: pd.DataFrame) -> dict:
    """计算 Entity Masking 四维一致性指标。

    四维:
      1. 验证一致率 — is_bank_fintech_news 掩码前后一致比例
      2. 情感一致率 — sentiment 一致比例（仅对双方均判真子集）
      3. Cohen's κ   — 排除随机一致后的验证一致度
      4. 逐模型分解 — 每个 LLM 独立的一致率
    """
    # 1. 验证一致率
    ver_match = (df_result['baseline_verified'] == df_result['masked_verified']).mean()

    # 2. 情感一致率（条件子集）
    both_true = df_result['baseline_verified'] & df_result['masked_verified']
    n_both_true = int(both_true.sum())
    sen_match = (
        (df_result.loc[both_true, 'baseline_sentiment'] ==
         df_result.loc[both_true, 'masked_sentiment']).mean()
        if n_both_true > 0 else float('nan')
    )

    # 3. Cohen's Kappa
    kappa = compute_cohens_kappa(
        df_result['baseline_verified'].astype(int).values,
        df_result['masked_verified'].astype(int).values,
    )

    # 4. 逐模型一致率
    per_model = {}
    for m in MODELS:
        short = m['short_name']
        b_col, m_col = f'{short}_baseline_verified', f'{short}_masked_verified'
        if b_col in df_result.columns and m_col in df_result.columns:
            valid = df_result[b_col].notna() & df_result[m_col].notna()
            if valid.sum() > 0:
                per_model[short] = round(
                    (df_result.loc[valid, b_col] == df_result.loc[valid, m_col]).mean(), 4
                )

    return {
        'verification_consistency': round(ver_match, 4),
        'sentiment_consistency': round(sen_match, 4) if not pd.isna(sen_match) else None,
        'cohens_kappa': kappa,
        'per_model_consistency': per_model,
        'n_samples': len(df_result),
        'n_both_true': n_both_true,
        'n_zero_replacements': int((df_result['n_replacements'] == 0).sum()),
    }


# ============================================================================
# 6. 报告生成
# ============================================================================

def generate_report(consistency: dict, df_sample: pd.DataFrame, df_valid: pd.DataFrame):
    """生成 JSON/CSV/LaTeX/PNG 报告。"""
    report_dir = os.path.join(CONFIG['paths']['output_dir'], 'eval_reports')
    os.makedirs(report_dir, exist_ok=True)

    # 6.1 JSON 报告
    json_path = os.path.join(report_dir, 'entity_masking_results.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(consistency, f, ensure_ascii=False, indent=2, default=str)
    logger.info(f"JSON 报告已保存: {json_path}")

    # 6.2 CSV 逐条对比
    csv_path = os.path.join(report_dir, 'entity_masking_detail.csv')
    detail_cols = ['baseline_verified', 'masked_verified',
                   'baseline_sentiment', 'masked_sentiment', 'n_replacements']
    for m in MODELS:
        short = m['short_name']
        detail_cols.extend([
            f'{short}_baseline_verified', f'{short}_masked_verified',
        ])
    available_cols = [c for c in detail_cols if c in df_sample.columns]
    df_sample[available_cols].to_csv(csv_path, index=True, encoding='utf-8-sig')
    logger.info(f"CSV 详情已保存: {csv_path}")

    # 6.3 LaTeX 表格
    tex_path = os.path.join(report_dir, 'entity_masking_table.tex')
    ver_pct = consistency['verification_consistency'] * 100
    sen_pct = (consistency['sentiment_consistency'] * 100
               if consistency['sentiment_consistency'] is not None else 'N/A')
    kappa_val = consistency['cohens_kappa']['kappa']

    tex_lines = [
        r'\begin{table}[htbp]',
        r'\centering',
        r'\caption{Entity Masking Robustness Test ($N=' + str(consistency['n_samples']) + r'$)}',
        r'\label{tab:entity_masking}',
        r'\begin{tabular}{lcc}',
        r'\hline',
        r'Metric & Value & Threshold \\',
        r'\hline',
        r'\multicolumn{3}{l}{\textit{Panel A: Aggregate Consistency}} \\',
    ]
    tex_lines.append(f'\\quad Verification Agreement & {ver_pct:.1f}\\% & $\\geq$90\\% \\\\')
    if isinstance(sen_pct, (int, float)):
        tex_lines.append(f'\\quad Sentiment Agreement (cond.) & {sen_pct:.1f}\\% & $\\geq$85\\% \\\\')
    else:
        tex_lines.append(f'\\quad Sentiment Agreement (cond.) & {sen_pct} & $\\geq$85\\% \\\\')
    tex_lines.append(f"\\quad Cohen's $\\kappa$ (Verification) & {kappa_val:.4f} & $\\geq$0.80 \\\\")
    tex_lines.append(r'\hline')
    tex_lines.append(r'\multicolumn{3}{l}{\textit{Panel B: Per-Model Breakdown}} \\')
    for m in MODELS:
        short = m['short_name']
        if short in consistency['per_model_consistency']:
            val = consistency['per_model_consistency'][short] * 100
            tex_lines.append(f'\\quad {short} & {val:.1f}\\% & \\\\')
    tex_lines.extend([
        r'\hline',
        r'\end{tabular}',
        r'\begin{tablenotes}[flushleft]\footnotesize',
        r"  \item Each article's target bank name and co-mentioned bank names",
        r'  are replaced with anonymized placeholders. The same LLM ensemble',
        r'  is re-queried. Agreement is computed between original and masked predictions.',
        r'\end{tablenotes}',
        r'\end{table}',
    ])
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(tex_lines))
    logger.info(f"LaTeX 表格已保存: {tex_path}")

    # 6.4 混淆矩阵 (PNG)
    try:
        _generate_confusion_matrix(df_valid, report_dir)
    except Exception as e:
        logger.warning(f"混淆矩阵生成失败: {e}")


def _generate_confusion_matrix(df_valid: pd.DataFrame, report_dir: str):
    """生成验证任务的掩码前后混淆矩阵。"""
    b = df_valid['baseline_verified'].astype(int).values
    m = df_valid['masked_verified'].astype(int).values

    # 2×2 混淆矩阵
    tp = int(((b == 1) & (m == 1)).sum())
    tn = int(((b == 0) & (m == 0)).sum())
    fp = int(((b == 0) & (m == 1)).sum())
    fn = int(((b == 1) & (m == 0)).sum())
    cm = np.array([[tn, fp], [fn, tp]])

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, cmap='Blues', interpolation='nearest')
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['False', 'True'], fontsize=12)
    ax.set_yticklabels(['False', 'True'], fontsize=12)
    ax.set_xlabel('Masked Prediction', fontsize=13)
    ax.set_ylabel('Baseline Prediction', fontsize=13)
    ax.set_title('Entity Masking: Verification Confusion Matrix', fontsize=14)

    for i in range(2):
        for j in range(2):
            color = 'white' if cm[i, j] > cm.max() / 2 else 'black'
            ax.text(j, i, str(cm[i, j]), ha='center', va='center',
                    fontsize=16, fontweight='bold', color=color)

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
    logger.info("--- 开始执行 Entity Masking 稳健性测试 ---")
    logger.info("=" * 60)
    logger.info("")
    logger.info("  📌 阶段目的")
    logger.info("     将目标银行名替换为匿名占位符(如 '工商银行'→'[BANK_A]'),")
    logger.info("     验证 LLM 情感判定是否依赖文本语义, 而非实体先验知识。")
    logger.info("     若掩码后判定一致率高, 说明情感度量的构建效度强。")
    logger.info("")
    logger.info("  📖 方法论依据")
    logger.info("     · SSRN-4558295 §7.2: Entity substitution robustness check")
    logger.info("     · Landis & Koch (1977, Biometrics 33(1):159-174): Cohen's κ 解释标准")
    logger.info("")
    logger.info("  📊 关键指标解读")
    logger.info("     · 验证一致率 ≥ 90%: 判定不受实体身份干扰, 稳健性优秀")
    logger.info("     · Cohen's κ: ≥0.81 almost perfect, 0.61-0.80 substantial, 0.41-0.60 moderate")
    logger.info("     · 实体残留率: 应为 0%, 否则掩码替换不完整")
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

    # ── Step 2: 随机抽样 ──
    df_sample = random_sample(df, sample_size, seed)
    logger.info(f"随机抽样 {len(df_sample)} 条 (seed={seed})")

    # ── Step 3: 提取 baseline ──
    df_sample = extract_baseline(df_sample)

    # ── Step 4: 执行掩码替换 ──
    n_incomplete = 0
    for idx, row in df_sample.iterrows():
        aliases = get_target_aliases(str(row['target_bank']), bnf)
        result = mask_entity(
            str(row['内容']), str(row['标题']),
            str(row['target_bank']), aliases,
            str(row.get('co_mentioned_banks', '')), bnf,
        )

        # 残留检测
        co_aliases = []
        if str(row.get('co_mentioned_banks', '')).strip():
            for peer in str(row['co_mentioned_banks']).split(';'):
                peer_stripped = peer.strip()
                if peer_stripped:
                    co_aliases.extend(get_target_aliases(peer_stripped, bnf))
        completeness = verify_masking_completeness(
            result['masked_text'], aliases, co_aliases
        )
        if not completeness['complete']:
            n_incomplete += 1
            logger.warning(f"行 {idx}: 实体残留 {completeness['residual_aliases']}")

        df_sample.at[idx, 'masked_text'] = result['masked_text']
        df_sample.at[idx, 'masked_title'] = result['masked_title']
        df_sample.at[idx, 'masked_target'] = result['masked_target']
        df_sample.at[idx, 'masked_co_mentioned'] = result['masked_co_mentioned']
        df_sample.at[idx, 'n_replacements'] = result['n_replacements']

    logger.info(f"掩码替换完成: {len(df_sample)} 条, "
                f"残留异常 {n_incomplete} 条, "
                f"零替换 {int((df_sample['n_replacements']==0).sum())} 条")

    # ── Step 5: 调用 LLM（掩码后文本）──
    masked_llm_results = asyncio.run(run_masked_llms(df_sample, MODELS))

    # ── Step 6: 解析 + 投票 ──
    for idx in df_sample.index:
        row_res = masked_llm_results.get(idx, {})
        final_v, final_s, agree_rate, parsed, _, _, n_fail = \
            _aggregate_track(row_res, MODELS)

        df_sample.at[idx, 'masked_verified'] = final_v
        df_sample.at[idx, 'masked_sentiment'] = final_s

        for m in MODELS:
            short = m['short_name']
            df_sample.at[idx, f'{short}_masked_verified'] = parsed.get(f'{short}_verified')
            df_sample.at[idx, f'{short}_masked_sentiment'] = parsed.get(f'{short}_sentiment')

    # ── Step 7: 计算一致性（排除零替换异常条）──
    df_valid = df_sample[df_sample['n_replacements'] > 0].copy()
    if len(df_valid) == 0:
        logger.error("零替换条数等于总样本数，无法计算一致性指标")
        return

    consistency = compute_masking_consistency(df_valid)

    # ── Step 8: 判定 ──
    thresholds = {
        'verification': EM_CFG.get('pass_threshold_verification', 0.90),
        'sentiment': EM_CFG.get('pass_threshold_sentiment', 0.85),
        'kappa': EM_CFG.get('pass_threshold_kappa', 0.80),
    }
    passed = (
        consistency['verification_consistency'] >= thresholds['verification']
        and (consistency['sentiment_consistency'] is None
             or consistency['sentiment_consistency'] >= thresholds['sentiment'])
        and consistency['cohens_kappa']['kappa'] >= thresholds['kappa']
    )
    consistency['passed'] = passed
    consistency['thresholds'] = thresholds

    sen_display = (f"{consistency['sentiment_consistency']:.1%}"
                   if consistency['sentiment_consistency'] is not None else 'N/A')
    logger.info(f"{'✅ 通过' if passed else '❌ 未通过'}: "
                f"验证一致率={consistency['verification_consistency']:.1%}, "
                f"情感一致率={sen_display}, "
                f"κ={consistency['cohens_kappa']['kappa']:.4f}")

    # ── Step 9: 输出报告 ──
    generate_report(consistency, df_sample, df_valid)
    logger.info(f"Entity Masking 测试完成, 耗时 {time.time()-stage_start:.1f}s")


if __name__ == "__main__":
    main()
