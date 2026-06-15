"""
news_process.validation.entity_masking — 阶段36：Entity Masking 稳健性测试（三轨版）

迁移说明 (Phase 7b)：
    本模块由原 root script ``36_entity_masking_test.py`` body 迁入。
    规范调用方式: ``python -m news_process.validation.entity_masking``

=====================================================================

功能：
    通过将目标银行和共提银行名称替换为匿名占位符，验证 LLM 判定是否依赖
    文本语义内容而非实体先验知识（如 "工商银行 → 国有大行 → 稳健"）。

    【三轨测试】每条新闻同时以全文 (_full)、实体特异性上下文片段 (_ctx) 和
    银行+金科同句共现片段 (_ss) 三种输入分别执行掩码替换与 LLM 重判，生成三套
    独立的一致性指标，验证稳健性结论不受文本输入粒度的影响。

    流程：
      1. 加载全量 LLM 结果（含 verified=True/False）
      2. 随机抽样 N=1000 条
      3. 提取 baseline 判定（full + ctx + ss 三轨已有列）
      4. 银行名 → 匿名占位符替换 + 实体残留检测（三轨, 正文+标题全覆盖;
         ctx/ss 轨掩码前先剥离 stage13 prepend 的标题前缀, 与生产 prompt 构造对齐,
         fix(omni-g-val-mask-01/03, 2026-06-11)）
      5. 掩码文本重新调用 3 模型 LLM 判定（三轨）
      6. 计算四维一致性指标（验证一致率、情感一致率、Cohen's κ、逐模型分解）× 三轨
         （分母双口径: 主口径 per-protocol 剔除调用全失败行 + ITT 披露口径,
         fix(omni-g-val-mask-02/04, 2026-06-11)）
      7. 生成 JSON/CSV/LaTeX/PNG 报告（含三轨对比）

    学术依据：
      - SSRN-4558295 §7.2: Entity substitution robustness check
      - Landis & Koch (1977, Biometrics 33(1):159-174): Cohen's κ 解释标准
        κ ≥ 0.81 → "almost perfect agreement"
        注: 本模块计算的是 Cohen's κ（2 编码者名义一致性），
        解释阈值出自 Landis & Koch (1977)，而非 Krippendorff's α

输入：
    `21_tone_llms_full.parquet`（全量 LLM 判定结果，含 full / ctx / ss 三轨列）

输出：
    `eval_reports/entity_masking_results.json`  — 三轨四维指标 + 判定
    `eval_reports/entity_masking_detail.csv`    — 逐条对比
    `eval_reports/entity_masking_table.tex`     — 论文就绪表格（含三轨 Panel）
    `eval_reports/entity_masking_confusion.png` — 混淆矩阵（full + ctx + ss 并排）

白话:
    担心 LLM 是"看名字下结论"——比如一看到"工商银行"就默认国有大行很稳健,
    而不是真的读懂了新闻内容。本检验把银行名全部涂掉换成"目标银行A/同业
    银行B"这种匿名代号, 再让同一批 LLM 重新判一遍。如果涂名前后的判定
    基本一致 (一致率 ≥90%、κ ≥0.8), 就证明 LLM 靠的是文本语义而非对银行
    的刻板印象。混淆矩阵图展示"涂名前判真/假 × 涂名后判真/假"四格的分布,
    对角线占比越高越好。
"""

import asyncio
import json
import os
import sys
import time
from itertools import combinations

import aiohttp
import matplotlib
import numpy as np
import pandas as pd

matplotlib.use('Agg')
from importlib import import_module

import matplotlib.pyplot as plt

# Phase 7b: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 news_process/validation/entity_masking.py 出发, 上溯 2 层抵达项目父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.caching import LLMCache
from news_process.core.config import load_config
from news_process.core.logging import setup_logging
from news_process.core.plotting import configure_matplotlib_chinese_fonts

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "36_entity_masking_test"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])
configure_matplotlib_chinese_fonts()

# Phase 7a-4: 21_tone_llms 已 thin shim 化, body 迁至 news_process.pipeline.sentiment.tone_llms
# 直接从规范包路径取内部函数, 不再走数字前缀文件名 import_module
_tone_llms = import_module('news_process.pipeline.sentiment.tone_llms')
fetch_llm_async  = _tone_llms.fetch_llm_async
_aggregate_track = _tone_llms._aggregate_track
# fix(omni-g-val-mask-01, 2026-06-11): 复用生产同一标题剥离实现 (只读引用, 不改 tone_llms),
# 保证 ctx 轨掩码输入与生产 prompt 构造 (iter_article_track_prompts) 语义一致。
_strip_prepended_title = _tone_llms._strip_prepended_title
build_llm_connector = _tone_llms.build_llm_connector
build_llm_timeout = _tone_llms.build_llm_timeout
build_model_pacers = _tone_llms.build_model_pacers
AsyncModelAvailability = _tone_llms.AsyncModelAvailability
preflight_model_availability = _tone_llms.preflight_model_availability
MODELS           = _tone_llms.MODELS
PROMPT_TEMPLATE  = _tone_llms.PROMPT_TEMPLATE
MAX_CONCURRENCY  = _tone_llms.MAX_CONCURRENCY

# get_target_aliases + extract_entity_context 在 utils.entity_context 中
from news_process.core.text.entity_context import get_target_aliases

# 复用评估模块的 Cohen's Kappa
_eval = import_module('news_process.validation.llms_evaluation')
compute_cohens_kappa = _eval.compute_cohens_kappa

# Entity Masking 配置
EM_CFG = CONFIG.get('entity_masking_test', {})
PLACEHOLDER = EM_CFG.get('placeholder', '目标银行A')
PEER_TEMPLATE = EM_CFG.get('peer_placeholder_template', '同业银行{}')
ENTITY_MASKING_MAX_CONCURRENCY = max(1, min(MAX_CONCURRENCY, int(EM_CFG.get('max_concurrency', 20))))
ENTITY_MASKING_REQUEST_SPACING = float(EM_CFG.get('request_spacing_seconds', 0.0))
ENTITY_MASKING_REQUEST_TIMEOUT_SECONDS = float(
    EM_CFG.get('request_timeout_seconds', min(60.0, _tone_llms.REQUEST_TIMEOUT_TOTAL))
)
ENTITY_MASKING_MAX_RETRIES = max(1, min(_tone_llms.MAX_RETRIES, int(EM_CFG.get('max_retries', 1))))

# 三轨标识 (full=全文 / ctx=实体上下文窗口 / ss=银行+金科同句共现)
# 下游所有 `for track in TRACKS` 参数化循环 (baseline 提取/掩码/LLM 重判/一致性
# 指标/报告) 随此列表自动扩到三轨; 仅 dict 字面量与混淆矩阵 zip 须显式同步。
TRACKS = ['full', 'ctx', 'ss']


def _build_entity_masking_llm_timeout() -> aiohttp.ClientTimeout:
    timeout_s = max(1.0, ENTITY_MASKING_REQUEST_TIMEOUT_SECONDS)
    return aiohttp.ClientTimeout(
        total=timeout_s,
        connect=min(timeout_s, _tone_llms.REQUEST_TIMEOUT_CONNECT),
        sock_connect=min(timeout_s, _tone_llms.REQUEST_TIMEOUT_SOCK_CONNECT),
        sock_read=timeout_s,
    )


# ============================================================================
# 2. 抽样与 Baseline
# ============================================================================

def random_sample(df: pd.DataFrame, sample_size: int, seed: int) -> pd.DataFrame:
    """简单随机抽样（可复现）。"""
    n = min(sample_size, len(df))
    return df.sample(n=n, random_state=seed)


def extract_baseline(df_sample: pd.DataFrame) -> pd.DataFrame:
    """从样本中提取已有的 LLM 判定作为 baseline（三轨 full/ctx/ss）。"""
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

def build_ctx_masking_input(content_ctx: str, title: str) -> str:
    """ctx/ss 轨掩码输入构造: 剥离 stage13 ``prepend_title`` 拼接的标题前缀。

    note(三轨, 2026-06-14): ss 轨 (``content_ss`` = 标题+银行+金科同句片段) 与 ctx
    轨同构 (都由 prepend_title 拼了标题前缀), 故复用本函数剥标题, 无需 ss 专用变体。

    fix(omni-g-val-mask-01, 2026-06-11): 盘上 ``content_ctx`` = stage13 物化的
    "标题+实体窗口"; 生产 stage 21 (``tone_llms.iter_article_track_prompts``) 喂
    prompt 前经 ``_strip_prepended_title`` 剥标题, 标题仅由 {title} 字段注入 1 次。
    若本模块直接对盘上 content_ctx 整体掩码再与 masked_title 同时填入模板, 掩码
    后 ctx prompt 标题出现 2 次而 baseline prompt 只出现 1 次 → 掩码前后判定差异
    混杂 "实体匿名化" 与 "prompt 结构变化" 两个处理。掩码前先剥标题, 使两 prompt
    仅差实体占位符, ctx 轨一致性指标恢复为纯掩码效应。
    """
    return _strip_prepended_title(str(content_ctx), str(title or ''))


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
                # fix(omni-g-val-mask-03, 2026-06-11): 共提银行替换计数与目标银行
                # 口径对齐 — 标题命中同样计入 n_replacements (替换本身一直双覆盖
                # 正文+标题, 仅计数漏了标题命中, 导致零替换/质量统计偏低)。
                cnt = masked_text.count(alias) + masked_title.count(alias)
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
    masked_title: str = '',
) -> dict:
    """检查掩码后文本 (正文 + 标题) 中是否仍残留原始银行名。

    fix(omni-g-val-mask-03, 2026-06-11): 残留扫描扩展到标题 — mask_entity 对标题
    同样执行替换, 且掩码标题会经 {title} 字段注入 LLM prompt; 漏遮审计只扫正文
    会漏报标题残留 (实体先验经标题泄漏给 LLM, 掩码稳健性结论被高估)。
    """
    scan_text = f"{masked_text}\n{str(masked_title or '')}"
    residuals = [a for a in original_aliases + co_bank_aliases if a in scan_text]
    return {'complete': len(residuals) == 0, 'residual_aliases': residuals}


# ============================================================================
# 4. LLM 调用（掩码后文本，三轨 full/ctx/ss）
# ============================================================================

async def run_masked_llms(
    df_masked: pd.DataFrame,
    models: list,
    cache: LLMCache | None = None,
    model_availability: AsyncModelAvailability | None = None,
) -> dict:
    """对掩码后数据执行 LLM 判定（full + ctx + ss 三轨）。

    Args:
        df_masked: 必须包含 masked_text_full, masked_title, masked_target,
                   masked_co_mentioned, masked_text_ctx, masked_text_ss 列。
                   fix(omni-g-val-mask-01, 2026-06-11): masked_text_ctx / masked_text_ss
                   须为 **去标题** 实体窗口/同句片段 (main() 已在掩码前剥离 prepend
                   标题前缀), 使 {title}+{content} 注入后标题恰出现 1 次, 与生产
                   baseline prompt (iter_article_track_prompts) 同构。

    Returns:
        dict: {row_idx: {'full': {model_id: response_text},
                         'ctx':  {model_id: response_text},
                         'ss':   {model_id: response_text}}}
    """
    semaphore = asyncio.Semaphore(ENTITY_MASKING_MAX_CONCURRENCY)
    # 三轨投票桶: 随 TRACKS 自动扩 (full/ctx/ss), 每轨独立模型应答字典。
    results_map = {i: {track: {} for track in TRACKS} for i in df_masked.index}

    connector = build_llm_connector(ENTITY_MASKING_MAX_CONCURRENCY)
    request_pacers = build_model_pacers(models, ENTITY_MASKING_REQUEST_SPACING)
    request_timeout = _build_entity_masking_llm_timeout()
    if model_availability is None:
        model_availability = AsyncModelAvailability()
    async with aiohttp.ClientSession(connector=connector, timeout=request_timeout) as session:
        await preflight_model_availability(session, models, model_availability)
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
                        fetch_llm_async(
                            session, semaphore, prompt, m, idx, track, cache=cache,
                            request_pacer=request_pacers.get(m['model_name']),
                            model_availability=model_availability,
                            request_timeout=request_timeout,
                            max_retries=ENTITY_MASKING_MAX_RETRIES,
                        )
                    )

        logger.info(f"🔬 Entity Masking LLM 三轨请求: "
                    f"{len(df_masked)} 条 × {len(models)} 模型 × {len(TRACKS)} 轨道 = {len(tasks)} 请求, "
                    f"concurrency={ENTITY_MASKING_MAX_CONCURRENCY}, "
                    f"per_model_spacing={ENTITY_MASKING_REQUEST_SPACING:.2f}s, "
                    f"timeout={ENTITY_MASKING_REQUEST_TIMEOUT_SECONDS:.0f}s, "
                    f"retries={ENTITY_MASKING_MAX_RETRIES}")

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

def _call_failure_mask(df: pd.DataFrame, track: str) -> pd.Series:
    """返回该轨 LLM 调用全失败行的布尔掩码 (掩码重判 + baseline 双侧)。

    fix(omni-g-val-mask-02, 2026-06-11): 共用助手 — 聚合一致性指标与混淆矩阵图
    用同一 per-protocol 过滤口径; 列缺失时 (旧 detail 数据) 优雅退化为不过滤。
    """
    fail = pd.Series(False, index=df.index)
    for cf_col in (f'masked_call_failure_{track}', f'llm_call_failure_{track}'):
        if cf_col in df.columns:
            fail |= (
                pd.to_numeric(df[cf_col], errors='coerce').fillna(0).astype(int) == 1
            )
    return fail


def compute_masking_consistency(df_result: pd.DataFrame, track: str) -> dict:
    """计算 Entity Masking 某一轨道的四维一致性指标。

    四维:
      1. 验证一致率 — is_bank_fintech_news 掩码前后一致比例
      2. 情感一致率 — sentiment 一致比例（仅对双方均判真子集）
      3. Cohen's κ   — 排除随机一致后的验证一致度
      4. 逐模型分解 — 每个 LLM 独立的一致率

    分母双口径 (fix(omni-g-val-mask-02, 2026-06-11) + fix(omni-g-val-mask-04, 2026-06-11)):
      LLM 调用全失败行的 masked_verified 由空票 ``majority_vote_bool([])`` 判 False
      (tone_llms.py), 属测量缺失而非掩码翻转。主口径 = per-protocol (valid 分母):
      排除掩码重判 ``masked_call_failure_{track}=1`` 行及 baseline 同类失败行
      (``llm_call_failure_{track}=1``), 与逐模型分解的 notna 双侧过滤口径对齐;
      ITT (intent-to-treat, physical 分母) 口径以 ``*_itt`` 键并行披露, 两个数同时报告。

    Args:
        df_result: 含 baseline_verified_{track}, masked_verified_{track} 等列。
        track: 'full' / 'ctx' / 'ss'。

    Returns:
        dict: 四维一致性指标 (含 ITT 披露键 + n_call_failure)。

    白话: 两个分母口径的区别 — 有些行 LLM 调用全失败, 系统默认记为
    "判否", 这是测量缺失不是真的"判定翻转"。per-protocol 口径把这些
    失败行剔出分母 (只算真测到的), ITT 口径保留全部行 (失败算不一致)。
    两个数都报告, 主结论用 per-protocol, ITT 作诚实披露。Cohen's κ 是
    "扣掉碰巧一致后的真实一致度": 即使两边瞎猜也会有一定比例碰巧相同,
    κ 把这部分剔掉, 0.81 以上视为几乎完全一致。
    """
    b_ver = f'baseline_verified_{track}'
    m_ver = f'masked_verified_{track}'
    b_sen = f'baseline_sentiment_{track}'
    m_sen = f'masked_sentiment_{track}'

    # fix(omni-g-val-mask-02, 2026-06-11): 识别调用全失败行 (掩码重判 + baseline),
    # 主口径分母剔除 (共用 _call_failure_mask, 与混淆矩阵口径一致)。
    fail_mask = _call_failure_mask(df_result, track)
    n_call_failure = int(fail_mask.sum())
    df_valid = df_result.loc[~fail_mask]

    # 1. 验证一致率 (主口径 per-protocol + ITT 披露口径)
    ver_match_itt = (df_result[b_ver] == df_result[m_ver]).mean()
    ver_match = (
        (df_valid[b_ver] == df_valid[m_ver]).mean()
        if len(df_valid) > 0 else float('nan')
    )

    # 2. 情感一致率（条件子集, per-protocol; 失败行 masked_verified=False 本就进不了
    #    both_true 子集, 此处显式用 df_valid 保持与聚合分母口径自洽）
    both_true = df_valid[b_ver] & df_valid[m_ver]
    n_both_true = int(both_true.sum())
    sen_match = (
        (df_valid.loc[both_true, b_sen] ==
         df_valid.loc[both_true, m_sen]).mean()
        if n_both_true > 0 else float('nan')
    )

    # 3. Cohen's Kappa (主口径 per-protocol + ITT 披露口径)
    kappa = compute_cohens_kappa(
        df_valid[b_ver].astype(int).values,
        df_valid[m_ver].astype(int).values,
    )
    kappa_itt = compute_cohens_kappa(
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
        # 主口径 = per-protocol (valid 分母, 调用失败行已剔除)。全失败退化场景下为
        # NaN (非 None): Step 8 判定 nan>=threshold → False, 保守不通过且不抛 TypeError。
        'verification_consistency': round(ver_match, 4),
        'sentiment_consistency': round(sen_match, 4) if not pd.isna(sen_match) else None,
        'cohens_kappa': kappa,
        # ITT 披露口径 (physical 分母, 含调用失败行) — 双口径两个数并行报告
        'verification_consistency_itt': round(ver_match_itt, 4),
        'cohens_kappa_itt': kappa_itt,
        'per_model_consistency': per_model,
        'n_samples': len(df_result),
        'n_samples_valid': int(len(df_valid)),
        'n_call_failure': n_call_failure,
        'n_both_true': n_both_true,
        'n_zero_replacements': int((df_result[f'n_replacements_{track}'] == 0).sum()),
        'denominator_note': (
            'primary metrics use the per-protocol (valid) denominator: rows with LLM '
            'call failure in the masked re-query or the baseline are excluded as '
            'measurement missingness; *_itt keys report the intent-to-treat '
            '(physical) denominator for disclosure.'
        ),
    }


# ============================================================================
# 6. 报告生成（三轨对比）
# ============================================================================

def generate_report(
    results: dict,
    df_sample: pd.DataFrame,
    df_valids: dict,
):
    """生成 JSON/CSV/LaTeX/PNG 报告（三轨对比 full/ctx/ss）。

    Args:
        results: {track: consistency_dict} 按 TRACKS 键入 (full/ctx/ss)。
        df_valids: {track: df_valid} 各轨经零替换过滤后的有效子样本。
    """
    report_dir = os.path.join(CONFIG['paths']['output_dir'], 'eval_reports')
    os.makedirs(report_dir, exist_ok=True)

    # 三轨综合 JSON: 随 TRACKS 自动展开 (full/ctx/ss)。
    combined = {track: results[track] for track in TRACKS}

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
            # fix(omni-g-val-mask-02, 2026-06-11): 导出调用失败旗标供逐行审计
            # (此前生成后无任何消费), 支撑 ITT vs per-protocol 双口径复算。
            f'masked_call_failure_{track}',
        ])
        for m in MODELS:
            short = m['short_name']
            detail_cols.extend([
                f'{short}_baseline_verified_{track}', f'{short}_masked_verified_{track}',
            ])
    available_cols = [c for c in detail_cols if c in df_sample.columns]
    df_sample[available_cols].to_csv(csv_path, index=True, encoding='utf-8-sig')
    logger.info(f"CSV 详情已保存: {csv_path}")

    # 6.3 LaTeX 表格（三轨 Panel 对比 Full / Ctx / SS）
    # 三轨后弃单一 Δ 列 (轨数 >2 无单一基准), 改一轨一列并排。
    tex_path = os.path.join(report_dir, 'entity_masking_table.tex')
    n_total = results['full']['n_samples']
    # 表头文案: 每轨一列, ss = "Bank+FinTech same-sentence" (银行+金科同句)。
    _TRACK_TEX_HEADER = {'full': 'Full Track', 'ctx': 'Ctx Track', 'ss': 'SS Track'}
    col_spec = 'l' + 'c' * len(TRACKS)
    header_cells = ' & '.join(_TRACK_TEX_HEADER.get(t, t.upper()) for t in TRACKS)
    n_cols = len(TRACKS) + 1

    def _pct_cell(v):
        return f'{v*100:.1f}\\%' if v is not None else 'N/A'

    tex_lines = [
        r'\begin{table}[htbp]',
        r'\centering',
        r'\caption{Entity Masking Robustness Test --- Three-Track Comparison ($N=' + str(n_total) + r'$)}',
        r'\label{tab:entity_masking}',
        r'\begin{tabular}{' + col_spec + r'}',
        r'\hline',
        r'Metric & ' + header_cells + r' \\',
        r'\hline',
        r'\multicolumn{' + str(n_cols) + r'}{l}{\textit{Panel A: Aggregate Consistency}} \\',
    ]

    for label_name, key in [
        ('Verification Agreement', 'verification_consistency'),
        # fix(omni-g-val-mask-02, 2026-06-11): ITT (physical 分母, 含调用失败行)
        # 口径并行披露 — 主行为 per-protocol (valid 分母), 两个数同时进表。
        ('Verification Agreement (ITT)', 'verification_consistency_itt'),
        ('Sentiment Agreement (cond.)', 'sentiment_consistency'),
    ]:
        # 注: 不使用 Python format spec '.1%'，因为其输出的裸 '%' 在 LaTeX 中是
        # 注释符，会导致同行后续列被吞掉。改为手动 ×100 + \\% 转义。
        cells = ' & '.join(_pct_cell(results[t].get(key)) for t in TRACKS)
        tex_lines.append(f'\\quad {label_name} & {cells} \\\\')

    # Cohen's κ — 一轨一列
    kappa_cells = ' & '.join(
        f"{results[t]['cohens_kappa']['kappa']:.4f}" for t in TRACKS
    )
    tex_lines.append(f"\\quad Cohen's $\\kappa$ (Verification) & {kappa_cells} \\\\")

    tex_lines.append(r'\hline')
    tex_lines.append(
        r'\multicolumn{' + str(n_cols) + r'}{l}{\textit{Panel B: Per-Model Breakdown (Full / Ctx / SS)}} \\'
    )
    for m in MODELS:
        short = m['short_name']
        per_model_vals = [results[t]['per_model_consistency'].get(short) for t in TRACKS]
        if all(v is not None for v in per_model_vals):
            cells = ' & '.join(f'{v*100:.1f}\\%' for v in per_model_vals)
            tex_lines.append(f'\\quad {short} & {cells} \\\\')

    tex_lines.extend([
        r'\hline',
        r'\end{tabular}',
        r'\begin{tablenotes}[flushleft]\footnotesize',
        r"  \item Each article's target bank name and co-mentioned bank names",
        r'  are replaced with anonymized placeholders. The LLM ensemble is',
        r'  re-queried on the full-text, entity-context and bank+fintech',
        r'  same-sentence tracks. Agreement is computed between original and',
        r'  masked predictions for each track.',
        # fix(omni-g-val-mask-02, 2026-06-11): 分母双口径披露 (ITT vs per-protocol)
        r'  \item Primary agreement rates use the per-protocol (valid) denominator:',
        r'  rows with LLM call failures in the masked re-query or the baseline are',
        r'  excluded as measurement missingness. ITT rows retain the full physical',
        r'  denominator (call-failure rows counted as disagreement).',
        r'\end{tablenotes}',
        r'\end{table}',
    ])
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(tex_lines))
    logger.info(f"LaTeX 表格已保存: {tex_path}")

    # 6.4 混淆矩阵 (PNG) — 三轨并排 (full/ctx/ss)
    try:
        _generate_confusion_matrix_per_track(df_valids, report_dir)
    except Exception as e:
        logger.warning(f"混淆矩阵生成失败: {e}")


def _generate_confusion_matrix_per_track(
    df_valids: dict,
    report_dir: str,
):
    """生成验证任务的掩码前后混淆矩阵（三轨并排 full/ctx/ss）。

    df_valids: {track: df_valid} 按 TRACKS 键入; 子图数随轨数自动扩展。
    """
    n_tracks = len(TRACKS)
    fig, axes = plt.subplots(1, n_tracks, figsize=(6.5 * n_tracks, 5))
    # 轨数==1 时 subplots 返回单 Axes 而非数组, 统一转 list 便于 zip。
    if n_tracks == 1:
        axes = [axes]

    for ax, track in zip(axes, TRACKS):
        df_valid = df_valids[track]
        # fix(omni-g-val-mask-02, 2026-06-11): 混淆矩阵与主口径 (per-protocol) 对齐 —
        # 调用全失败行 (空票判 False, 属测量缺失) 不进图, 否则图与主指标分母矛盾。
        df_valid = df_valid.loc[~_call_failure_mask(df_valid, track)]
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
    logger.info("--- 开始执行 Entity Masking 稳健性测试（三轨版） ---")
    logger.info("=" * 60)
    logger.info("")
    logger.info("  📌 阶段目的")
    logger.info("     将目标银行名替换为匿名占位符(如 '工商银行'→'[BANK_A]'),")
    logger.info("     验证 LLM 情感判定是否依赖文本语义, 而非实体先验知识。")
    logger.info("     同时在全文(full)、上下文片段(ctx)和银行+金科同句(ss)三条轨道上")
    logger.info("     独立验证, 确保稳健性结论不受文本输入粒度的影响。")
    logger.info("")
    logger.info("  📖 方法论依据")
    logger.info("     · SSRN-4558295 §7.2: Entity substitution robustness check")
    logger.info("     · Landis & Koch (1977, Biometrics 33(1):159-174): Cohen's κ 解释标准")
    logger.info("")
    logger.info("  📊 关键指标解读")
    logger.info("     · 验证一致率 ≥ 90%: 判定不受实体身份干扰, 稳健性优秀")
    logger.info("     · Cohen's κ: ≥0.81 almost perfect, 0.61-0.80 substantial, 0.41-0.60 moderate")
    logger.info("     · 实体残留率: 应为 0%, 否则掩码替换不完整")
    logger.info("     · 三轨差异: full/ctx/ss 各轨指标两两差异应 <5pp, 否则提示文本粒度敏感")
    logger.info("")

    # ── 配置 ──
    # 2026-06-13: stage 36 已改为无条件 always-on (用户决策: 全部启用而非条件启用),
    # 移除 entity_masking_test.enabled 早退门; enabled flag 仅作记录, 启停由
    # core/dag.py 的 always_enabled 谓词决定。
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

    # 确认 content_ss 列存在 (镜像 ctx 回退: 缺列→全文 body, 与 ss_is_fallback=True 同义)
    if 'content_ss' not in df.columns:
        logger.warning("输入数据缺少 content_ss 列，ss 轨道将回退至全文")
        df['content_ss'] = df['内容'].astype(str)

    # ── Step 2: 随机抽样 ──
    df_sample = random_sample(df, sample_size, seed)
    logger.info(f"随机抽样 {len(df_sample)} 条 (seed={seed})")

    # ── Step 3: 提取 baseline（三轨 full/ctx/ss）──
    df_sample = extract_baseline(df_sample)

    # ── Step 4: 执行掩码替换（三轨 full/ctx/ss）──
    n_incomplete = {track: 0 for track in TRACKS}
    for idx, row in df_sample.iterrows():
        aliases = get_target_aliases(str(row['target_bank']), bnf)
        co_banks_str = str(row.get('co_mentioned_banks', ''))

        # 预计算共提银行别名（三轨共用）
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
            result_full['masked_text'], aliases, co_aliases,
            masked_title=result_full['masked_title'],
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
        # fix(omni-g-val-mask-01, 2026-06-11): 掩码前剥离 prepend 标题前缀, 与生产
        # stage 21 prompt 构造对齐 — 掩码后 ctx prompt 与 baseline prompt 仅差实体
        # 占位符, 一致性指标不再混杂标题双重注入的 prompt 结构变化 (详见
        # build_ctx_masking_input docstring)。
        content_ctx = build_ctx_masking_input(
            str(row.get('content_ctx', row['内容'])), str(row['标题'])
        )
        result_ctx = mask_entity(
            content_ctx, str(row['标题']),
            str(row['target_bank']), aliases, co_banks_str, bnf,
        )
        completeness_ctx = verify_masking_completeness(
            result_ctx['masked_text'], aliases, co_aliases,
            masked_title=result_ctx['masked_title'],
        )
        if not completeness_ctx['complete']:
            n_incomplete['ctx'] += 1
            logger.warning(f"行 {idx} [ctx]: 实体残留 {completeness_ctx['residual_aliases']}")

        df_sample.at[idx, 'masked_text_ctx'] = result_ctx['masked_text']
        df_sample.at[idx, 'n_replacements_ctx'] = result_ctx['n_replacements']

        # ── SS 轨道掩码 (银行+金科同句共现) ──
        # 镜像 ctx 轨: content_ss 同样由 stage13 prepend_title 拼了标题前缀,
        # 掩码前先剥离 (与生产 stage 21 prompt 构造对齐), 使掩码后 ss prompt 与
        # baseline prompt 仅差实体占位符, 一致性指标不混杂标题双重注入 (复用
        # build_ctx_masking_input, 标题剥离逻辑 ctx 与 ss 两路共用, 详见其 docstring)。
        content_ss = build_ctx_masking_input(
            str(row.get('content_ss', row['内容'])), str(row['标题'])
        )
        result_ss = mask_entity(
            content_ss, str(row['标题']),
            str(row['target_bank']), aliases, co_banks_str, bnf,
        )
        completeness_ss = verify_masking_completeness(
            result_ss['masked_text'], aliases, co_aliases,
            masked_title=result_ss['masked_title'],
        )
        if not completeness_ss['complete']:
            n_incomplete['ss'] += 1
            logger.warning(f"行 {idx} [ss]: 实体残留 {completeness_ss['residual_aliases']}")

        df_sample.at[idx, 'masked_text_ss'] = result_ss['masked_text']
        df_sample.at[idx, 'n_replacements_ss'] = result_ss['n_replacements']

    for track in TRACKS:
        n_zero = int((df_sample[f'n_replacements_{track}'] == 0).sum())
        logger.info(f"[{track}] 掩码替换完成: {len(df_sample)} 条, "
                    f"残留异常 {n_incomplete[track]} 条, "
                    f"零替换 {n_zero} 条")

    # ── Step 5: 调用 LLM（掩码后文本，三轨 full/ctx/ss）──
    cache_db = os.path.join(CONFIG["paths"]["output_dir"], '_llm_cache.db')
    with LLMCache(cache_db) as cache:
        logger.info(f"Entity Masking LLM 缓存: {cache.size()} 条已缓存, 路径: {cache_db}")
        masked_llm_results = asyncio.run(
            run_masked_llms(
                df_sample, MODELS, cache=cache,
                model_availability=AsyncModelAvailability(),
            )
        )

    # ── Step 6: 解析 + 投票（三轨 full/ctx/ss）──
    _empty_row_res = {track: {} for track in TRACKS}
    for idx in df_sample.index:
        row_res = masked_llm_results.get(idx, _empty_row_res)

        for track in TRACKS:
            (
                final_v, final_s,
                agree_rate_v, agree_rate_s,
                n_valid_votes, n_verifying_votes,
                call_failure, undefined,
                parsed, topics, innov_loci, innov_substs,
                n_fail, avg_prob_score,
                _avg_subst_prob_score, _avg_locus_prob_score,
                _innov_collab_modes, _avg_collab_prob_score,  # v3.4.0 BREAKING: 18-tuple
            ) = _aggregate_track(row_res.get(track, {}), MODELS)

            df_sample.at[idx, f'masked_verified_{track}'] = final_v
            df_sample.at[idx, f'masked_sentiment_{track}'] = final_s
            df_sample.at[idx, f'masked_agreement_rate_v_{track}'] = agree_rate_v
            df_sample.at[idx, f'masked_agreement_rate_s_{track}'] = agree_rate_s
            df_sample.at[idx, f'masked_n_valid_votes_{track}'] = n_valid_votes
            df_sample.at[idx, f'masked_n_verifying_votes_{track}'] = n_verifying_votes
            df_sample.at[idx, f'masked_call_failure_{track}'] = call_failure
            df_sample.at[idx, f'masked_undefined_{track}'] = undefined
            df_sample.at[idx, f'masked_n_failures_{track}'] = n_fail
            df_sample.at[idx, f'masked_avg_prob_score_{track}'] = avg_prob_score
            df_sample.at[idx, f'masked_topics_{track}'] = ';'.join(topics)
            # v7: 原 masked_llm_categories_* / masked_text_types_*; 列名后缀升级与 schema 同步
            df_sample.at[idx, f'masked_innov_loci_{track}'] = ';'.join(innov_loci)
            df_sample.at[idx, f'masked_innov_substs_{track}'] = ';'.join(innov_substs)

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

    # ── Step 8: 判定（三轨 full/ctx/ss 均须通过）──
    thresholds = {
        'verification': EM_CFG.get('pass_threshold_verification', 0.90),
        'sentiment': EM_CFG.get('pass_threshold_sentiment', 0.85),
        'kappa': EM_CFG.get('pass_threshold_kappa', 0.80),
    }

    for track in TRACKS:
        c = results[track]
        # 审计修复 (degradation F24): sentiment_consistency is None 表示双方均判
        # verified=True 的条件子集为空 (n_both_true==0) — 即"无法测量"情感一致性。
        # 旧逻辑 ``is None or >= threshold`` 把"未测量"短路成"通过该子准则", 会在
        # 空子集时伪装情感掩码稳健性成立 (R6 伪装通过). 现把 None 视为"不可判定",
        # 不计通过 (保守且诚实: 无法宣称未曾测量的稳健性); n_both_true 已在结果
        # 字典中暴露, sentiment_inconclusive 显式标记供下游/读者区分。
        sentiment_inconclusive = c['sentiment_consistency'] is None
        sentiment_ok = (not sentiment_inconclusive
                        and c['sentiment_consistency'] >= thresholds['sentiment'])
        passed = (
            c['verification_consistency'] >= thresholds['verification']
            and sentiment_ok
            and c['cohens_kappa']['kappa'] >= thresholds['kappa']
        )
        c['passed'] = passed
        c['sentiment_inconclusive'] = sentiment_inconclusive
        c['thresholds'] = thresholds

        sen_display = (f"{c['sentiment_consistency']:.1%}"
                       if c['sentiment_consistency'] is not None
                       else 'N/A(子集为空,不可判定)')
        # fix(omni-g-val-mask-02, 2026-06-11): 主口径=per-protocol, 同时报 ITT 双口径
        logger.info(f"[{track.upper()}] {'✅ 通过' if passed else '❌ 未通过'}"
                    f"{' [情感不可判定]' if sentiment_inconclusive else ''}: "
                    f"验证一致率={c['verification_consistency']:.1%} "
                    f"(ITT={c['verification_consistency_itt']:.1%}, "
                    f"call_failure 排除 {c['n_call_failure']} 行), "
                    f"情感一致率={sen_display}, "
                    f"κ={c['cohens_kappa']['kappa']:.4f}")

    # 三轨综合判定 (full/ctx/ss 全过才算整体通过)
    overall_pass = all(results[track]['passed'] for track in TRACKS)
    track_summary = ', '.join(
        f"{track}={'通过' if results[track]['passed'] else '未通过'}" for track in TRACKS
    )
    logger.info(f"{'✅' if overall_pass else '❌'} 三轨综合判定: {track_summary}")

    # 三轨差异诊断 — 两两 pairwise (full↔ctx / full↔ss / ctx↔ss), 任一对超 5pp 即提示
    max_delta_flagged = False
    for t1, t2 in combinations(TRACKS, 2):
        delta_ver = abs(
            results[t1]['verification_consistency'] - results[t2]['verification_consistency']
        )
        delta_kappa = abs(
            results[t1]['cohens_kappa']['kappa'] - results[t2]['cohens_kappa']['kappa']
        )
        if delta_ver > 0.05 or delta_kappa > 0.05:
            max_delta_flagged = True
            logger.info(f"   {t1}↔{t2} 差异较大: Δ验证一致率={delta_ver:.1%}, Δκ={delta_kappa:.4f}")
        else:
            logger.info(f"   {t1}↔{t2} 差异正常: Δ验证一致率={delta_ver:.1%}, Δκ={delta_kappa:.4f}")
    if max_delta_flagged:
        logger.info("   提示: 文本输入粒度可能影响稳健性，建议检查 ctx/ss 提取质量")

    # ── Step 9: 输出报告 (三轨) ──
    generate_report(results, df_sample, df_valids)
    logger.info(f"Entity Masking 三轨测试完成, 耗时 {time.time()-stage_start:.1f}s")


if __name__ == "__main__":
    main()
