"""
news_process.validation.entity_masking — 阶段66：Entity Masking 稳健性测试（三轨版）

迁移说明 (Phase 7b)：
    本模块由原 root script ``66_entity_masking_test.py`` body 迁入。
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
        ⚠ 引用核验 (2026-06-20 日志审计): 该 SSRN 裸编号 (无作者/标题/年) 经 web/SSRN
        检索未能独立解析, 投稿前须核验其作者/标题/年或降级为 working paper。实体替换
        稳健性方法本身有可验证的已发表锚点: "Robustness of Named-Entity Replacements
        for In-Context Learning" (Findings of EMNLP 2023, aclanthology 2023.findings-emnlp.728)。
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

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 66_entity_masking_test.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**核心问题**: 验证 LLM 是否靠'读懂文本'而非'看到银行名的刻板印象' (如'工商银行→国有大行→稳健') 下判定。

**输入**: `21_tone_llms_full.parquet` (CONFIG['filenames']['output_21_tone_llms_full']; 全量含 verified=True/False, 三轨 full/ctx/ss 列)。随机抽样 N=1000 (EM_CFG sample_size, seed=42)。

**处理步骤**:
1. `extract_baseline` 取样本已有的 full/ctx/ss 三轨 LLM 判定 (整体投票 llm_verified/llm_sentiment + 逐模型)。
2. `mask_entity` 三轨各做掩码: 目标银行别名→'目标银行A' (PLACEHOLDER, EM_CFG 可配); 共提银行→'同业银行B/C/D...'; 别名按长度降序替换防短名先匹配; 正文+标题双覆盖; `verify_masking_completeness` 扫正文+标题残留 (残留则 warning)。
3. `run_masked_llms` 异步对掩码文本调 3 模型 × 3 轨 LLM 重判 (PROMPT_TEMPLATE 字节级冻结, 只换 title/content/target_bank/co_mentioned_banks 实参), 走 `fetch_llm_async`。
4. `_aggregate_track` 把三模型应答聚合为 masked_verified/sentiment 等 (18-tuple, v3.4.0 BREAKING)。
5. `compute_masking_consistency` 算四维指标 × 三轨: ①验证一致率 ②情感一致率 (双方均判真子集) ③Cohen's κ ④逐模型一致率。

**关键算法/分母双口径**: 主口径 per-protocol (valid 分母, `_call_failure_mask` 剔除掩码重判或 baseline 调用全失败行 — 空票被默认判 False 属测量缺失非翻转); ITT (physical 分母, 含失败行) 以 `*_itt` 键并行披露。混淆矩阵与主口径对齐 (失败行不进图)。`compute_cohens_kappa` 复用 `news_process.validation.llms_evaluation` (返回含 'kappa' 键的 dict)。判定: 三轨各须 验证一致率≥0.90 + 情感一致率≥0.85 + κ≥0.80, 整体 = full/ctx/ss AND; sentiment_consistency is None (n_both_true==0 子集空) 视为'不可判定'不计通过 (degradation F24 修复, 防伪装通过)。三轨两两 pairwise (combinations) 验证一致率/κ 差异 >5pp 则提示文本粒度敏感。

**外部依赖**: LLM API (yunwu, 经 tone_llms.fetch_llm_async), 3 模型 × 3 轨 × 1000 = 最多 9000 请求; aiohttp 异步, ENTITY_MASKING_MAX_CONCURRENCY 限流。确定性锚点 = `_llm_cache_validation.db` (验证变体库, 用 LLMCache 命中缓存; 但掩码文本 prompt 与生产不同 → 这些是增量 LLM 请求, 冷缓存需付费跑)。timeout=21600s (6h) 因冷缓存+限流。matplotlib 三轨混淆矩阵。

**学术依据**: SSRN-4558295 §7.2 entity substitution; Landis & Koch (1977, Biometrics) κ 解释阈值。

■ 白话说明

**这一步在做什么**: 把每篇新闻里的银行名字全部涂掉换成匿名代号 ('目标银行A'、'同业银行B'), 再让同一批 AI 模型重新判一遍这篇新闻的真伪和褒贬。然后对比涂名前后 AI 的答案变没变。

**为什么需要它**: 用 AI (大语言模型) 给新闻打情感分, 最怕 AI 不是真读懂文章, 而是一看到'工商银行'就条件反射地觉得'国有大行肯定稳健'。这就好比考试时学生不解题、光看题目里的名字猜答案。涂掉名字后如果 AI 给出的判定还基本一致 (一致率≥90%、扣掉碰巧一致后的 κ≥0.8), 就证明 AI 靠的是文章内容而非对银行的成见。

**对面板和论文的影响**: 整篇论文的情感/注意力指标都建立在'AI 判定可信'之上。如果 AI 其实在凭银行名字下结论, 那银行-年度面板里所有情感变量都掺了'银行身份偏见', 因果推断会被严重质疑。这一步是核心方法论防线之一: 三条文本轨道 (整篇/上下文/同句) 都通过, 才能在论文里宣称'AI 标注稳健、不受银行身份干扰'。它要真跑会花钱 (调 AI 接口), 所以放在最长的 6 小时超时阶段。
========================================================================
"""

import asyncio
import json
import os
import platform
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
from news_process.core.logging import pct4, setup_logging, sig4
from news_process.core.plotting import configure_matplotlib_chinese_fonts

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "66_entity_masking_test"
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
ENTITY_MASKING_MAX_CONCURRENCY = max(1, min(MAX_CONCURRENCY, int(EM_CFG.get('max_concurrency', 250))))  # 2026-07-21 用户决策: 项目统一 250 并发 (fallback 同步, 原 20)
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
                    f"{len(df_masked):,d} 条 × {len(models):,d} 模型 × {len(TRACKS):,d} 轨道 = {len(tasks):,d} 请求, "
                    f"concurrency={ENTITY_MASKING_MAX_CONCURRENCY}, "
                    f"per_model_spacing={sig4(ENTITY_MASKING_REQUEST_SPACING)}s, "
                    f"timeout={sig4(ENTITY_MASKING_REQUEST_TIMEOUT_SECONDS)}s, "
                    f"retries={ENTITY_MASKING_MAX_RETRIES}")

        # round-7 富集 (2026-06-29): 掩码质量 sig4 概览 — 纯日志, 仅只读 main() 已物化的
        # n_replacements_{track} 列, 不改任何产物/控制流 (golden-safe)。零替换的篇本就被
        # Step 7 排除出一致性分母, 此处提前暴露其占比便于审计涂名有效性。
        try:
            for _trk in TRACKS:
                _col = f'n_replacements_{_trk}'
                if _col in df_masked.columns:
                    _nr = pd.to_numeric(df_masked[_col], errors='coerce').fillna(0)
                    _mx = int(_nr.max()) if len(_nr) else 0
                    _zero_share = float((_nr == 0).mean()) if len(_nr) else 0.0
                    logger.info(f"   掩码替换量 [{_trk}]: 均值={sig4(_nr.mean())} / 中位={sig4(_nr.median())} / "
                                f"最大={_mx:,d} 处每篇 | 零替换占比={pct4(_zero_share)}")
        except Exception as _e:  # noqa: BLE001
            logger.warning(f"   掩码质量概览打印异常 (不影响处理): {_e}")

        completed = 0
        total = len(tasks)
        report_interval = max(1, total // 20)
        next_report = report_interval

        for coro in asyncio.as_completed(tasks):
            row_idx, model_id, res_text, track = await coro
            results_map[row_idx][track][model_id] = res_text
            completed += 1
            if completed >= next_report or completed == total:
                pct = completed / total if total else 0.0
                logger.info(f"📡 Entity Masking 进度: {completed:,d}/{total:,d} ({pct4(pct)})")
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

def _log_environment_and_config(input_path: str) -> None:
    """打印项目/环境信息 + 输入输出 + 运行配置 + 方法论引文 (日志富集, 2026-06-24)。

    目标 (用户要求"在日志文件中提供尽可能多的项目信息、运行期间信息和运行结果信息"):
    把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数、方法学出处"一次性落进
    日志, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 (golden-safe)。

    note(参考文献): 本阶段核心方法 (实体替换稳健性检验 / Cohen's κ 解释阈值) 的学术
    锚点 (SSRN-4558295 §7.2; Landis & Koch 1977 Biometrics 33(1):159-174) 在经核验
    参考文献注册表中**无对应 DOI 条目**, 按手册"表中查不到的 DOI 不得 emit"铁律, 仅
    emit Author-Year/期刊卷(期):页, 不伪造 DOI。
    """
    try:
        report_dir = os.path.join(CONFIG['paths']['output_dir'], 'eval_reports')

        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (Entity Masking 实体掩码稳健性, STAGES_VALIDATION; "
                    "三轨 full/ctx/ss)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) v3.16.0")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'}")
        logger.info("     · 确定性/成本: 在线付费 LLM 重判 (掩码文本 prompt 与生产不同 → 增量请求, "
                    "冷缓存需付费; 命中 _llm_cache_validation.db 则 $0); 离线守卫 NEWS_PROCESS_LLM_OFFLINE=1 优雅跳过")

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 输入:   {input_path}")
        logger.info(f"     · 报告目录: {report_dir}")
        logger.info("     · 产物:   entity_masking_results.json / _detail.csv / _table.tex / _confusion.png")
        logger.info(f"     · LLM缓存(验证库): {os.path.join(CONFIG['paths']['output_dir'], '_llm_cache_validation.db')}")
        logger.info(f"     · 银行名表: {CONFIG['paths'].get('bank_names_file', '(默认)')}")

        logger.info("  ⚙ 运行配置 (config::entity_masking_test)")
        logger.info(f"     · 抽样: sample_size={EM_CFG.get('sample_size', 1000):,d} | "
                    f"random_seed={EM_CFG.get('random_seed', 42)} | 轨道集 TRACKS={TRACKS}")
        logger.info(f"     · 占位符: 目标行={PLACEHOLDER!r} | 共提行模板={PEER_TEMPLATE!r}")
        logger.info(f"     · LLM: 模型数={len(MODELS)} | concurrency={ENTITY_MASKING_MAX_CONCURRENCY} | "
                    f"per_model_spacing={sig4(ENTITY_MASKING_REQUEST_SPACING)}s | "
                    f"timeout={sig4(ENTITY_MASKING_REQUEST_TIMEOUT_SECONDS)}s | "
                    f"retries={ENTITY_MASKING_MAX_RETRIES}")
        logger.info(f"     · 通过门槛: 验证一致率≥{pct4(EM_CFG.get('pass_threshold_verification', 0.90))} | "
                    f"情感一致率≥{pct4(EM_CFG.get('pass_threshold_sentiment', 0.85))} | "
                    f"κ≥{sig4(EM_CFG.get('pass_threshold_kappa', 0.80))}")

        logger.info("  📖 方法论依据 (参考文献; 注: SSRN-4558295 裸编号无可核验 DOI 仅 emit 题录, 其余条目附经核验 DOI)")
        logger.info("     · 实体替换稳健性: SSRN-4558295 §7.2 (entity substitution robustness check) "
                    "→ 把银行名换匿名代号, 检验 LLM 是否靠'读懂文本'而非'银行身份先验'下判定")
        logger.info("       可发表锚点: Robustness of Named-Entity Replacements for In-Context Learning "
                    "(Findings of EMNLP 2023, 2023.findings-emnlp.728)")
        # round-8 富集 (2026-06-29): 补 κ 统计量本体的奠基定义文献 (Cohen 1960), 与下行
        # Landis-Koch (1977) 解释带配对 = 'κ 统计量定义 (Cohen 1960) + κ 解释带 (Landis-Koch 1977)'。
        # 白话: 本模块 compute_cohens_kappa 算的就是 Cohen 这个名义尺度一致性系数本身, 故引其定义原文。
        logger.info("     · κ 统计量定义 (本模块 compute_cohens_kappa 所算统计量之原始定义): "
                    "Cohen, J. (1960). A coefficient of agreement for nominal scales. "
                    "Educational and Psychological Measurement, 20(1), 37-46. "
                    "https://doi.org/10.1177/001316446002000104")
        logger.info("     · κ 解释阈值: Landis, J. R., & Koch, G. G. (1977). The measurement of observer "
                    "agreement for categorical data. Biometrics, 33(1), 159-174. "
                    "https://doi.org/10.2307/2529310")
        logger.info("       → κ≥0.81 almost-perfect / 0.61-0.80 substantial / 0.41-0.60 moderate")
        # round-7 富集 (2026-06-29): 当代 LLM-标注安全 / 实体中性化文献 (经 Crossref 核验 DOI),
        # 锚定本阶段"涂名→检验 LLM 是否靠身份先验走捷径"的方法学正当性。
        logger.info("     · LLM 标注的实体先验风险 (本检验直接动机): Carlson, N. A., & Burbano, V. (2026). "
                    "The use of LLMs to annotate data in management research: Foundational guidelines and "
                    "warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023")
        logger.info("       → 管理学用 LLM 标注须防模型借实体身份('国有大行→稳健')走捷径; 实体掩码即此防线。")
        logger.info("     · 实体中性化 (entity neutering, 与本掩码同构的因果识别手段): Engelberg, J., Manela, A., "
                    "Mullins, W., & Vulicevic, L. (2025). Entity neutering [Working paper]. SSRN. "
                    "https://doi.org/10.2139/ssrn.5182756")
        logger.info("       → 把实体名替换为占位符以隔离'文本语义'与'实体先验'两条信息通道, 与本阶段三轨掩码同源。")
        logger.info("     · 社会科学 LLM 标注风险指南: Lin, H., & Zhang, Y. (2026). Navigating the risks of "
                    "using large language models for text annotation in social science research. Social "
                    "Science Computer Review, 44(3), 403-427. https://doi.org/10.1177/08944393251366243")
        logger.info("     · LLM hacking / prompt 配置隐藏风险量化: Baumann, J., Röttger, P., Urman, A., "
                    "Wendsjö, A., Plaza-del-Arco, F. M., Gruber, J. B., & Hovy, D. (2025). Large language "
                    "model hacking: Quantifying the hidden risks of using LLMs for text annotation. arXiv. "
                    "https://doi.org/10.48550/arXiv.2509.08825")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法信息打印失败 (不影响处理): {e}")


def main():
    # fix(log-clobber-2026-06-27): 本阶段 import 并复用 tone_llms 的 LLM-fetch/聚合
    # 函数 (fetch_llm_async / AsyncModelAvailability / preflight / _aggregate_track),
    # 它们默认经 tone_llms 模块级 "21_tone_llms" logger 落盘 → 会截断覆盖真实
    # stage 21 的 logs/21_tone_llms.log。把 tone_llms 模块 logger 重定向到本阶段
    # 自己的 logger, 借用函数日志改落 logs/66_entity_masking_test.log (纯日志归属,
    # golden-safe; 详见 tone_llms.redirect_module_logger 的根因说明)。
    _tone_llms.redirect_module_logger(logger)

    stage_start = time.time()
    phase_durations: dict[str, float] = {}

    # fix(2026-06-19 run-check F7): 离线确定性模式下本阶段必为冷缓存 (掩码文本 prompt 与生产不同),
    # 强行运行会抛大量 LLMCacheMissError + "Task exception was never retrieved" 异步噪声。
    # 阶段 66 是在线付费 only 的稳健性验证 (EXPECTED_NO_OUTPUT, 不写面板) → 离线优雅跳过,
    # 在线 (生产) 行为完全不变。复用 tone_llms.LLM_OFFLINE 单一事实源 (勿重解析 env)。
    if _tone_llms.LLM_OFFLINE:
        logger.warning(
            "阶段 66 (Entity Masking) 需在线 LLM 重判掩码文本 (变体 prompt 冷缓存); "
            "NEWS_PROCESS_LLM_OFFLINE=1 离线守卫下优雅跳过 — 在线运行不受影响。"
        )
        return

    # ── 黄金范式标准化 banner (功能/方法/判读/确定性) ──
    # fix(C7-V-004, 2026-06-17): 删除旧短 banner (📌/📖/📊 三段, 其中 '[BANK_A]'
    # 是陈旧示例, 实际占位符为 '目标银行A'/PLACEHOLDER), 替换为下方黄金范式单
    # banner (对齐 39c construct_orthogonality.py: 替换而非叠加, 占位符与代码一致)。
    # 仅供 banner 文案展示的预读 (源同 Step 8 thresholds / 配置块 sample_size·seed,
    # EM_CFG 单一事实源, 不改任何下游取值)。
    sample_size_preview = EM_CFG.get('sample_size', 1000)
    seed_preview = EM_CFG.get('random_seed', 42)
    thresholds_preview_ver = EM_CFG.get('pass_threshold_verification', 0.90)
    thresholds_preview_kappa = EM_CFG.get('pass_threshold_kappa', 0.80)
    logger.info("=" * 72)
    logger.info("阶段 66: Entity Masking 实体掩码稳健性测试 (SSRN-4558295 §7.2 / 三轨)")
    logger.info("=" * 72)
    logger.info("【功能】把每篇新闻里的目标银行名和共提银行名全部涂掉换成匿名代号")
    logger.info("        ('工商银行'→'目标银行A'、共提行→'同业银行B/C/D'), 再让同一批 3 个")
    logger.info("        LLM 重判真伪与褒贬, 对比涂名前后判定是否一致 — 验证 LLM 靠'读懂")
    logger.info("        文本'而非'看到银行名的刻板印象'(国有大行→稳健)下结论。产出三轨")
    logger.info("        四维一致性指标 + JSON/CSV/LaTeX 报告 + 三轨混淆矩阵 PNG。")
    logger.info(f"【方法】随机抽样 N={sample_size_preview} (seed={seed_preview}); 别名按长度降序替换(防短名先匹配)+正文标题双覆盖;")
    logger.info("        四维指标 × 三轨(full/ctx/ss): ①验证一致率 ②情感一致率(双方均判真子集)")
    logger.info("        ③Cohen's κ(扣随机一致) ④逐模型分解; 分母双口径(per-protocol 主 / ITT 披露,")
    logger.info("        调用全失败行属测量缺失剔出主口径)。Landis & Koch (1977) κ 解释阈值。")
    logger.info(f"【判读】验证一致率↑=好(≥{pct4(thresholds_preview_ver)} 视为不受身份干扰); "
                f"κ↑=好(≥{sig4(thresholds_preview_kappa)} 通过门槛; 落 0.61-0.80 substantial 高度一致, "
                f"≥0.81 才 almost-perfect, Landis-Koch 1977);")
    logger.info("        实体残留率应=0%(否则掩码不完整, 稳健性被高估); 三轨两两差异 <5pp 为好")
    logger.info("        (否则提示文本输入粒度敏感)。三轨须全过(full∧ctx∧ss)才算整体通过。")
    logger.info("【确定性】调 LLM API(yunwu 3 模型 × 3 轨 × 样本量, 经 _llm_cache_validation.db 命中缓存);")
    logger.info("          掩码文本 prompt 与生产不同 → 这些是增量请求, 冷缓存需付费跑(timeout 6h)。")
    logger.info("=" * 72)
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

    # 项目/环境信息 + 输入输出 + 运行配置 + 方法论引文 (日志富集 2026-06-24)
    _log_environment_and_config(input_path)
    logger.info("")

    if not os.path.exists(input_path):
        logger.error(f"输入文件不存在: {input_path}")
        # fix(D2, 2026-07-18): 缺输入=检验未执行, 静默 return 会让入口假绿; fail-loud 速败。
        sys.exit(1)
    _t_load = time.time()
    df = pd.read_parquet(input_path)
    logger.info(f"加载全量 LLM 结果: {len(df):,d} 条")

    # 确认 content_ctx 列存在
    if 'content_ctx' not in df.columns:
        logger.warning("输入数据缺少 content_ctx 列，ctx 轨道将回退至全文")
        df['content_ctx'] = df['内容'].astype(str)

    # 确认 content_ss 列存在 (镜像 ctx 回退: 缺列→全文 body, 与 ss_is_fallback=True 同义)
    if 'content_ss' not in df.columns:
        logger.warning("输入数据缺少 content_ss 列，ss 轨道将回退至全文")
        df['content_ss'] = df['内容'].astype(str)

    phase_durations['①加载+列检查'] = time.time() - _t_load

    # ── Step 2: 随机抽样 ──
    df_sample = random_sample(df, sample_size, seed)
    logger.info(f"随机抽样 {len(df_sample):,d} 条 (seed={seed})")

    # ── Step 3: 提取 baseline（三轨 full/ctx/ss）──
    df_sample = extract_baseline(df_sample)

    # ── Step 4: 执行掩码替换（三轨 full/ctx/ss）──
    _t_mask = time.time()
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

    n_sample = len(df_sample)
    for track in TRACKS:
        n_zero = int((df_sample[f'n_replacements_{track}'] == 0).sum())
        zero_rate = n_zero / n_sample if n_sample else 0.0
        logger.info(f"[{track}] 掩码替换完成: {n_sample:,d} 条, "
                    f"残留异常 {n_incomplete[track]:,d} 条 ({pct4(n_incomplete[track] / n_sample if n_sample else 0.0)}), "
                    f"零替换 {n_zero:,d} 条 ({pct4(zero_rate)})")
    phase_durations['②三轨掩码替换'] = time.time() - _t_mask

    # ── Step 5: 调用 LLM（掩码后文本，三轨 full/ctx/ss）──
    _t_llm = time.time()
    # W4 (2026-06-25): 掩码变体响应隔离到独立库 (不写生产 golden 锚点 _llm_cache.db);
    # 见 prompt_sensitivity 同款注释 (hygiene 隔离, 变体键与生产互异不影响复现)。
    cache_db = os.path.join(CONFIG["paths"]["output_dir"], '_llm_cache_validation.db')
    with LLMCache(cache_db) as cache:
        logger.info(f"Entity Masking LLM 缓存: {cache.size():,d} 条已缓存, 路径: {cache_db}")
        masked_llm_results = asyncio.run(
            run_masked_llms(
                df_sample, MODELS, cache=cache,
                model_availability=AsyncModelAvailability(),
            )
        )
    phase_durations['③掩码文本 LLM 重判'] = time.time() - _t_llm

    # ── Step 6: 解析 + 投票（三轨 full/ctx/ss）──
    _t_agg = time.time()
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

    phase_durations['④聚合解析+投票'] = time.time() - _t_agg

    # ── Step 7: 计算一致性（排除零替换异常条）──
    _t_metric = time.time()
    results = {}
    df_valids = {}
    for track in TRACKS:
        df_valid = df_sample[df_sample[f'n_replacements_{track}'] > 0].copy()
        if len(df_valid) == 0:
            logger.error(f"[{track}] 零替换条数等于总样本数，无法计算一致性指标")
            return
        df_valids[track] = df_valid
        results[track] = compute_masking_consistency(df_valid, track)
    phase_durations['⑤四维一致性指标'] = time.time() - _t_metric

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

        sen_display = (pct4(c['sentiment_consistency'])
                       if c['sentiment_consistency'] is not None
                       else 'N/A(子集为空,不可判定)')
        # fix(omni-g-val-mask-02, 2026-06-11): 主口径=per-protocol, 同时报 ITT 双口径
        logger.info(f"[{track.upper()}] {'✅ 通过' if passed else '❌ 未通过'}"
                    f"{' [情感不可判定]' if sentiment_inconclusive else ''}: "
                    f"验证一致率={pct4(c['verification_consistency'])} "
                    f"(ITT={pct4(c['verification_consistency_itt'])}, "
                    f"call_failure 排除 {c['n_call_failure']:,d} 行), "
                    f"情感一致率={sen_display}, "
                    f"κ={sig4(c['cohens_kappa']['kappa'])}")

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
            logger.info(f"   {t1}↔{t2} 差异较大: Δ验证一致率={pct4(delta_ver)}, Δκ={sig4(delta_kappa)}")
        else:
            logger.info(f"   {t1}↔{t2} 差异正常: Δ验证一致率={pct4(delta_ver)}, Δκ={sig4(delta_kappa)}")
    if max_delta_flagged:
        logger.info("   提示: 文本输入粒度可能影响稳健性，建议检查 ctx/ss 提取质量")

    # ── 黄金范式【结果分析】(只读 results/n_incomplete/df_sample, 不改任何产物) ──
    # crash-guard (硬化 A): 本分析块在 Step 9 generate_report (写盘 JSON/CSV/LaTeX/PNG)
    # 之前执行, 纯日志诊断; 一旦此处抛异常 (如缺键/NaN 比较/格式化) 会令整个 stage 36
    # 崩溃并丢失产物 → 故整体包 try/except, 异常仅告警跳过, 不影响产物落盘。
    try:
        _KAPPA_BANDS = [
            (0.81, "almost perfect (几乎完全一致)"),
            (0.61, "substantial (高度一致)"),
            (0.41, "moderate (中等一致)"),
            (0.21, "fair (尚可)"),
            (0.0, "slight (微弱)"),
        ]

        def _kappa_band(k: float) -> str:
            # NaN-guard (硬化 B): κ 理论上恒为 float (n==0→0.0), 仍防御性兜底 NaN
            if pd.isna(k):
                return "N/A (无有效数据)"
            for lo, name in _KAPPA_BANDS:
                if k >= lo:
                    return name
            return "poor (差, κ<0, 比随机还差)"

        logger.info("-" * 72)
        logger.info("【结果分析】涂名前后 LLM 判定一致性 — 越一致 = LLM 越靠文本语义而非银行身份先验")
        n_total_sample = len(df_sample)
        th_ver = thresholds['verification']
        th_sen = thresholds['sentiment']
        th_kap = thresholds['kappa']
        logger.info(f"  样本规模: 抽样 {n_total_sample:,d} 条; 通过门槛 验证一致率≥{pct4(th_ver)} / "
                    f"情感一致率≥{pct4(th_sen)} / κ≥{sig4(th_kap)}")

        for track in TRACKS:
            c = results[track]
            ver = c['verification_consistency']
            ver_itt = c['verification_consistency_itt']
            kap = c['cohens_kappa']['kappa']
            kap_itt = c['cohens_kappa_itt']['kappa']
            sen = c['sentiment_consistency']
            # NaN-guard (硬化 B): 全 call_failure 退化场景 verification_consistency=NaN,
            # 不能落进 ver>=th_ver 的方向判读 (NaN 比较恒 False 会误判"❌弱(身份偏见)")。
            ver_is_nan = pd.isna(ver)
            ver_disp = "NaN(无有效数据)" if ver_is_nan else pct4(ver)
            if ver_is_nan:
                ver_verdict = "⚪该轨无有效数据(全 NaN, 调用全失败)"
            else:
                ver_verdict = ("✅好(身份无关)" if ver >= th_ver
                               else ("⚠临界" if ver >= th_ver - 0.05 else "❌弱(疑似身份偏见)"))
            kap_verdict = f"{_kappa_band(kap)}"
            if pd.isna(kap):
                kap_flag = "⚪N/A"
            else:
                kap_flag = "✅好" if kap >= th_kap else ("⚠临界" if kap >= th_kap - 0.10 else "❌弱")
            if c['sentiment_inconclusive']:
                sen_line = ("情感一致率=N/A — 双方均判真子集为空(n_both_true=0), 不可判定, "
                            "保守计为不通过(防伪装通过)")
            else:
                sen_verdict = ("✅好" if sen >= th_sen
                               else ("⚠临界" if sen >= th_sen - 0.05 else "❌弱"))
                sen_line = (f"情感一致率(双方均判真 n_both_true={c['n_both_true']:,d} 子集)="
                            f"{pct4(sen)} {sen_verdict}")
            logger.info(f"  [{track.upper()}] {'✅整体通过' if c['passed'] else '❌整体未通过'}")
            logger.info(f"     · 验证一致率(per-protocol)={ver_disp} {ver_verdict} "
                        f"| ITT={pct4(ver_itt)} (剔除 call_failure {c['n_call_failure']:,d} 行)")
            logger.info(f"     · Cohen's κ(per-protocol)={sig4(kap)} [{kap_verdict}] {kap_flag} "
                        f"| ITT κ={sig4(kap_itt)}")
            logger.info(f"     · {sen_line}")
            # 逐模型分解 (哪个模型对掩码最敏感)
            pm = c['per_model_consistency']
            if pm:
                pm_str = ', '.join(f"{k}={pct4(v)}" for k, v in pm.items())
                pm_min = min(pm.values())
                pm_flag = ("(全模型稳健)" if pm_min >= th_ver
                           else f"(最低 {pct4(pm_min)}, 该模型对掩码偏敏感)")
                logger.info(f"     · 逐模型一致率: {pm_str} {pm_flag}")
            # 掩码质量: 残留率 + 零替换率
            n_resid = n_incomplete[track]
            n_zero = c['n_zero_replacements']
            resid_rate = n_resid / n_total_sample if n_total_sample else 0.0
            zero_rate = n_zero / n_total_sample if n_total_sample else 0.0
            if n_resid > 0:
                logger.warning(f"     · ⚠掩码不完整: 残留 {n_resid:,d} 条 ({pct4(resid_rate)}) — "
                               f"银行名经标题/正文泄漏给 LLM, 该轨稳健性结论被高估, 须排查别名表")
            else:
                logger.info("     · 掩码完整性: 残留 0 条 (0.000%) ✅ 别名全部涂净")
            if zero_rate > 0.10:
                logger.warning(f"     · ⚠零替换 {n_zero:,d} 条 ({pct4(zero_rate)}) 偏高 — "
                               f"这些文未命中任何目标行别名, 涂名对其无效, 已排除出一致性分母")
            else:
                logger.info(f"     · 零替换: {n_zero:,d} 条 ({pct4(zero_rate)}); 有效子样本 "
                            f"n_valid={c['n_samples_valid']:,d}")

        # 整体方向判读
        if overall_pass:
            logger.info("  ▶ 整体结论: 三轨(full∧ctx∧ss)全部通过 — LLM 判定不受银行身份先验干扰, "
                        "情感/注意力测度稳健, 可在论文中宣称'实体匿名化后判定一致'。")
        else:
            failed_tracks = [t for t in TRACKS if not results[t]['passed']]
            logger.warning(f"  ▶ 整体结论: 轨道 {failed_tracks} 未通过 — 提示 LLM 可能部分依赖银行身份, "
                           "下游情感变量或掺'身份偏见', 须在论文如实披露并加附录敏感性。")

        # 小样本警告 (早期试跑盘面 T=2 退化场景)
        if n_total_sample < 200:
            logger.info(f"  ⚠小样本提示: 本次仅 {n_total_sample:,d} 条 (远小于 EM_CFG.sample_size 目标), "
                        "一致率/κ 抽样方差大、混淆矩阵稀疏, 仅用于验证管道正确性; "
                        "稳健性结论以全量 约1,819万/T=19 实测 N=1000 为准。")
        logger.info("-" * 72)
    except Exception as _e:
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")

    # ── Step 9: 输出报告 (三轨) ──
    _t_report = time.time()
    generate_report(results, df_sample, df_valids)
    phase_durations['⑥报告生成(JSON/CSV/LaTeX/PNG)'] = time.time() - _t_report

    # ── 阶段计时汇总 (各主要子阶段墙钟耗时; 纯日志, golden-safe) ──
    try:
        total_elapsed = time.time() - stage_start
        logger.info("  ⏱ 阶段计时 (各子阶段墙钟耗时)")
        for _phase, _dur in phase_durations.items():
            _share = _dur / total_elapsed if total_elapsed > 0 else 0.0
            logger.info(f"     · {_phase}: {sig4(_dur)}s ({pct4(_share)})")
        logger.info(f"     · 合计: {sig4(total_elapsed)}s")
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  [阶段计时] 汇总打印异常 (不影响处理): {_e}")

    logger.info(f"Entity Masking 三轨测试完成, 耗时 {sig4(time.time()-stage_start)}s")


if __name__ == "__main__":
    main()
