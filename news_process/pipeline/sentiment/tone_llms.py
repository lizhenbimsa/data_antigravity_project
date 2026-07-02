"""
news_process.pipeline.sentiment.tone_llms — 阶段21：统一 LLM 语义精筛与情感分析（三轨版）
==========================================================================================

迁移说明 (Phase 7a-4)：
    本模块由原 root script ``21_tone_llms.py`` body 迁入。
    规范调用方式: ``python -m news_process.pipeline.sentiment.tone_llms``

功能：
    将早期的 `13_news_llms.py` (真伪精筛) 和 `23_tone_llms.py` (情感分析) 组合，
    使用同一个大模型 Prompt 构建思维链 (Chain-of-Thought)，单次请求获取"真伪"与"情感"。
    采用多模型（如 gpt54nano, gemini31, deepseekv4）逐条并发请求，并使用多数投票（Majority Vote）
    合成最终共识，满足顶级学术期刊的交叉验证和三角验证标准。
    每条新闻独立请求各模型，通过信号量控制并发。

    【三轨输入】每条新闻同时以全文 (_full)、上下文片段 (_ctx) 和银行+金科同句
    片段 (_ss) 三种输入分别请求模型，生成三套完整的验证与情感判定结果，供下游
    消融研究和三角验证使用。
    - full: content_full = 标题 + 全文。
    - ctx:  content_ctx  = 标题 + 含目标银行句 ±窗口 (Hassan 2019 QJE proximity)。
    - ss:   content_ss   = 标题 + 同句内同时含 目标银行∧金科词 的句 ±窗口
            (银行+金科同句共现; 无共现→镜像 ctx 回退全文 body, ss_is_fallback=True)。
    三轨经 ctx_materializer / prepend_title 上游物化, content_ss 由 stage 13
    单一事实源产出 (本模块仅消费); 缺 content_ss 列时 iter_article_track_prompts
    优雅回退 content_full。标题已拼进三轨, 不再存在独立的标题情感轨道
    (remove-title-track 终态)。
    ⚠ 铁律: full × ctx × ss 三轨互为稳健性, 严禁混进同一 over-id Hansen J;
    各轨各自 just-identified 并排 (见 iv_extensions.py 红线注释)。

方法论依据：
    多模型投票共识机制:
      Wang, X., Wei, J., Schuurmans, D., et al. (2023). Self-consistency
      improves chain of thought reasoning in language models. Proceedings
      of ICLR 2023. DOI: https://doi.org/10.48550/arXiv.2203.11171
    三角验证 (Triangulation):
      Denzin, N. K. (1978/2017). The research act: A theoretical introduction
      to sociological methods. Routledge. DOI: https://doi.org/10.4324/9781315134543
    LLM 金融文本分析可复现性:
      Lopez-Lira, A., & Tang, Y. (2023). Can ChatGPT forecast stock price
      movements? Return predictability and large language models. SSRN
      Working Paper No. 4412788. DOI: https://doi.org/10.2139/ssrn.4412788
      (temperature=0 确定性推理锚点; 详见下方 TEMPERATURE 常量学术依据注。
      原引 Bybee "ghost in the machine" 工作论文无可解析标识符且 DOI
      10.1111/jofi.13366 系误植 — 已移除)。

输入：
    模块二前置输出的 `15_fintech_intensity.parquet`
    (该文件在 12_fintech_news.parquet 基础上追加了 fintech_intensity_score 和 intensity_verified 列)
    (硬依赖: 阶段14 缺失即报错终止, 不再静默回退 12; 见 main() 的 "Step 4(a) 硬化")
    
输出：
    筛选后的合法新闻 `21_tone_llms.parquet`

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 21_tone_llms.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**输入**: 读 stage 14 输出 `15_fintech_intensity.parquet` (硬依赖, 缺失即报错终止, 不再静默回退 stage 12; main() Step 4(a) 硬化; 因 LLM 需 stage 14 的 `fintech_intensity_score`/`intensity_verified` 列)。关键输入列: `内容`(全文)、`标题`、`content_ctx`(stage 13 物化, 缺则 main() 调 `_materialize_content_ctx` 兜底)、`content_ss`(stage 13 单一事实源物化, 缺则 `iter_article_track_prompts` 优雅回退 content_full)、`target_bank`、`co_mentioned_banks`。

**处理步骤**: ①`main()` 加载 parquet + schema 守护; ②`LLMCache(_llm_cache.db)` 打开 SQLite 缓存; ③`asyncio.run(run_all_llms(...))` 对每篇文章 × 三轨 × 三个 LLM 家族异步并发请求 (信号量 MAX_CONCURRENCY 控并发); ④`_aggregate_track` 对每轨返回 18 元组聚合 (verified 三角验证投票 + sentiment 投票 + locus/substantiveness/collab_mode 三维分类投票 + logit-to-score 概率分数); ⑤逐模型存档列 + 轨级聚合列写回 DataFrame; ⑥verified_full 全文轨过滤 (full-only) 后写 `21_tone_llms.parquet`, 全量写 `21_tone_llms_full.parquet`。

**关键算法/公式**: 三模型 ensemble 多数决 (`majority_vote_bool` 严格多数 >50%; `majority_vote_sentiment`/`majority_vote_categorical` 分类决); 平局策略可配 (sentiment **verified 轨**平局/空票 tie_default='中性' [用户决策 2026-06-23 保守降级, 不产 None; **逆转** v6/F2 '平局→None 防中性污染'; final_v=False 非金科轨情感仍 None=N/A]; substantiveness 平局 tie_default='象征性'; locus 平局 tie_default='应用场景'; collab_mode 平局 tie_default='自主研发', 均 conservative=uniform-prior MAP 保守降级); `compute_prob_score(label, confidence)` 把 3 类情感标签+置信度映射到 [-1,+1] 连续分 (logit-to-score, config `logit_to_score.enabled=true`; NaN/越界 confidence→P3_INV 拒绝); `compute_prob_score_binary` 对三维创新标签产 [0,1] 二分类分 (P2_BIN/P3_BIN)。verified gate 仅用 `verified_full` (full-only, 用户决策 2026-06-29; ctx/ss 截断可能漏信息, 不参与留篇决定, 降为 conditional-on-full 测度/稳健性轨), 仍产 triple-gate 7 互斥态诊断列 (`llm_verified_triple_*`; 其中含 full 的 4 态闭合输出样本)。

**输出列** (每轨 _full/_ctx/_ss 各一套): `llm_verified_*`、`llm_sentiment_*`、`llm_agreement_rate_v/s_*`、`n_valid_votes_*`/`n_verifying_votes_*`、`innovation_locus_*`(Gomber 2018 JMIS)、`innovation_substantiveness_*`(W&Z 1994/1998 ASQ)、`innovation_collab_mode_*`(Chesbrough 2003 + L&S 2006 SMJ)、各维度 `*_confidence_*`、`llm_prob_score`(avg_prob_score, 轨级聚合主列)、per-model `{short}_prob_score_*`、`avg_subst/locus/collab_prob_score_*`、逐模型 `{short}_verified/sentiment_*` 存档列; 另产 `llm_verified_dual_*`(3 态) / `llm_verified_triple_*`(7 态) 互斥指示列。

**外部依赖**: 三个 LLM 家族经 config/sentiment.yaml 锁定 = gpt-5.4-nano(short_name gpt54nano) / gemini-3.1-flash-lite(gemini31) / deepseek-v4-flash(deepseekv4, 走 api.deepseek.com 直连, 其余两家走 yunwu.ai/v1); 需 YUNWU_API_KEY / DEEPSEEK_API_KEY。**Prompt v8 字节级冻结** (`iter_article_track_prompts` 为生产与缓存覆盖审计共用单一事实源; 缓存键 = 模型名+prompt 文本+prompt_version+temperature (+seed 仅当 temperature>0; 生产 temperature=0.0 下 seed 不进键, 故键与历史 no-seed schema 字节级一致, 零缓存失效))。**确定性锚点 = _llm_cache.db** (~407MB/13.3 万条): 命中即 $0 字节级复现; `NEWS_PROCESS_LLM_OFFLINE=1` 离线守卫下缓存 miss 抛 `LLMCacheMissError` 而非调 API + 跳 preflight 探针。**超时**: 父端子进程硬超时 21600s (3x 安全余量覆盖冷缓存/雪崩退避)。

**DAG 位置**: 上游 stage 14 (fintech_intensity) + stage 13 (content_ctx/content_ss 物化); 下游 stage 22 (词典法读 21 输出 `21_tone_llms.parquet`)、最终经 stage 24/45 进面板。本阶段是全流水线唯一核心付费阶段。

■ 白话说明

这一步是整条流水线里最贵、最关键的一环: 让三个大语言模型 (相当于三位独立的金融分析员) 各自读同一篇新闻, 先判断这篇报道是不是真的在讲'某家银行和金融科技的关系'(精筛/把关), 再判断它的语气是正面、负面还是中性, 顺带给出这条创新是'实质性还是象征性'、'底层技术还是应用场景'、'自己研发还是对外合作'等标签。三位分析员投票, 少数服从多数, 谁都说不准的就标成'未定'而不是硬塞成'中性'。为什么需要它: 后面要算每家银行每年被媒体报道的整体情绪, 必须先有一个可靠、可复盘的逐篇打分, 而大模型比关键词词典更懂上下文 (比如能分清'不看好'是负面)。它做得好不好直接决定面板里'媒体语调'这个主变量的质量, 也就是论文最核心的结论靠不靠得住。为保证'同一篇文章每次跑出来分数都一样'(论文复现的命脉), 项目把每次问大模型的结果都存进一个叫 _llm_cache.db 的账本, 之后离线照查账本就能零成本、一字不差地重跑——所以这个账本千万不能删。它还把同一篇文章按三种取材范围 (全文 / 只看跟银行相关的句子 / 只看银行和金科同句出现的片段) 各算一遍, 互为稳健性印证; 三种范围里只要有一种判定'确实在讲银行-金科'就把这篇保留下来。
========================================================================
"""

import asyncio
import json
import math
import os
import platform
import sys
import time
import warnings
from collections import Counter

import aiohttp
import pandas as pd
from pandas.errors import PerformanceWarning

# Phase 7a-4: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 pipeline/sentiment/tone_llms.py 出发, 上溯 3 层抵达 news_process/ 的父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.caching import LLMCache
from news_process.core.config import load_config
from news_process.core.logging import (
    log_memory_usage,
    log_stage_summary,
    pct4,
    setup_logging,
    sig4,
)
from news_process.core.reporting import save_dataset
from news_process.core.text.canonicalization import canonicalize_topic
from news_process.core.text.entity_context import extract_entity_context, get_target_aliases

# v3.7.0 (DC3 + C1 + M13 修复): LLM raw response archive 集成
# V4 audit F-P2.1 critical + V6 verification 必修.
# 顶刊 reproducibility 硬约束: 即使 LLM 模型升级 (GPT-5.4→5.5),
# 审稿人 fresh API call 时仍能从归档完整复现实验.
# ImportError 时 logger.error (M13 修复): silent skip 会让顶刊复现 fail 但
# 用户不知道. 必须 loud signal.
try:
    from news_process.pipeline.llm_archive import archive_record as _llm_archive_record
    _LLM_ARCHIVE_AVAILABLE = True
except ImportError as _archive_import_exc:
    _llm_archive_record = None
    _LLM_ARCHIVE_AVAILABLE = False
    # 模块 logger 在 line ~94 才 setup_logging() 初始化, 此处用 stdlib 直接拿
    import logging as _logging_for_archive_error
    _logging_for_archive_error.getLogger(__name__).error(
        "CRITICAL v3.7.0: news_process.pipeline.llm_archive 不可用 (%s). "
        "顶刊 reproducibility 受损 — V4 F-P2.1 violation. "
        "Stage 21 (sentiment) / 34/36/39 (3-dim 分类) 将无 raw response 归档. "
        "用户必须修复 import 错误后重跑 pipeline.",
        _archive_import_exc,
    )

# per-model 分类维度梯子 SSOT (2026-07-03, ROBUSTNESS_GAP_BACKFILL 计划 §2 A1):
# 由 encode.LLM_CLASS_SPEC 单源派生文章级发列基名 (键 subst/locus/collab) 与
# per_model_parsed 解析键 (值[2] innovation_*)。encode 不可导入的极端环境用具名
# fallback 常量兜底 (镜像 llm_peer_iv 的 LLMCacheMissError fallback 先例);
# ⚠ fallback 是字面副本 — gate 测试对 _LLM_CLASS_SPEC_FALLBACK 与 encode.LLM_CLASS_SPEC
# 做逐字节断言 (具名常量无论 import 成败都运行时可达, 字面漂移本机即红; 终审 #11)。
_LLM_CLASS_SPEC_FALLBACK = {
    'subst':  ('sub_frac',    '实质性',   'innovation_substantiveness'),
    'locus':  ('tech_frac',   '底层技术', 'innovation_locus'),
    'collab': ('collab_frac', '外部协同', 'innovation_collab_mode'),
}
try:
    from news_process.pipeline.panel.encode import LLM_CLASS_SPEC as _LLM_CLASS_SPEC
except Exception:  # noqa: BLE001 — encode 携带面板级依赖, 极端环境下允许降级
    _LLM_CLASS_SPEC = dict(_LLM_CLASS_SPEC_FALLBACK)

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "21_tone_llms"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])


def redirect_module_logger(new_logger):
    """把本模块的模块级 ``logger`` 重定向到 ``new_logger``, 返回**原 logger** (供恢复)。

    根因 (2026-06-27 诊断): 本模块同时充当 (a) stage 21 的入口 与 (b) 可复用的
    LLM-fetch 库。借用层函数 —— ``fetch_llm_async`` / ``AsyncModelAvailability``
    (``disable`` / ``note_transient_failure``) / ``preflight_model_availability`` /
    ``_log_retryable_transport_issue`` / ``_aggregate_track`` —— 全部经**模块级全局**
    ``logger`` (名为 ``"21_tone_llms"``, 指向 ``logs/21_tone_llms.log``,
    ``file_mode='w'`` 首写截断) 落盘。当 stage 66 (entity_masking) / stage 70
    (prompt_sensitivity) 等验证阶段 import 并在自己的子进程里调用这些借用函数时,
    它们仍按 ``"21_tone_llms"`` logger 写盘 → **第一条 emit 即截断并覆盖真实
    stage 21 的运行日志** (实测: 验证阶段同进程 PID 把 logs/21_tone_llms.log
    覆写成几行 transient-failure, 掩盖整次 stage 21 记录)。

    本函数让借用方在跑 LLM 前显式接管该 logger: 借用函数的运行日志改落入调用方
    自己的日志文件 (如 logs/66_*.log / logs/70_*.log); 真实 ``logs/21_tone_llms.log``
    不再被波及 —— ``delay=True`` 下原 "21_tone_llms" handler 因本进程零 emit 而
    **永不打开/截断**该文件, 完整保留上一次真正 stage 21 运行的记录。

    ⚠ 仅应由**借用本模块 fetch/aggregate 函数的阶段**调用; stage 21 自身运行
    (``main()`` / ``run_all_llms``) **绝不调用** → 其日志一如既往落
    ``logs/21_tone_llms.log``。各阶段为独立子进程, 进程级全局 logger 重绑定彼此
    隔离。**纯日志归属变更, 不动任何数据 / 缓存 / 缓存键 / 控制流 (golden-safe)**。

    Args:
        new_logger: 接管后借用函数使用的 logger (通常是调用方阶段自己的 logger);
            传 ``None`` 为 no-op (保持当前 logger 不变)。

    Returns:
        重定向前的原 logger (调用方可在收尾时传回本函数恢复; 子进程一般无需)。
    """
    global logger
    old_logger = logger
    if new_logger is not None:
        logger = new_logger
    return old_logger


# v3 / Fix 3: 把顶层 sys.exit(1) 改为 raise RuntimeError 以消除"严重档"
# 顶层副作用 — sys.exit 会让任何 import 链路 (包括 pytest 测试套件)
# 被进程级 SystemExit 杀掉, 无法在 pytest 单测粒度被报告; raise RuntimeError
# 保持子进程入口的退出码一致 (未捕获异常 → 非零退出码), 但允许 import
# 路径下的调用方 (如 tests/integration/test_papers_imports.py 通过
# importlib.import_module 间接 import 本模块) 在 pytest 中正常 fail
# 而非杀掉整个 session.
#
# 当前事实: 真实环境下 sentiment.yaml 总能提供 tone_llm_processing 节,
# raise 路径从未触发; 但作为防御性反模式仍应消除. 详见 v3 plan A.3 的
# "副作用三档分级" 论证.
def _ensure_llm_config(cfg: dict) -> dict:
    """读取并校验 tone_llm_processing 配置; 缺失或类型异常时 raise.

    recode 加固: 除"缺失"外, 还守住"YAML 把该节写成非 dict 值"
    (如笔误成字符串/列表) — 此场景下下游 ``LLM_CONFIG.get('models', [])``
    会抛 AttributeError, 错误信息不友好且根因不明。本 helper 在源头
    给出明确诊断。
    """
    llm = cfg.get('tone_llm_processing')
    if not llm:
        # 包含 None / {} / [] / "" / 0 等 falsy 情况 — 都视为"未配置"
        raise RuntimeError(
            "在 sentiment.yaml 中未找到 tone_llm_processing 配置节 (或为空); "
            "请检查 config split 是否完整或 legacy config.yaml 是否包含此节。"
        )
    if not isinstance(llm, dict):
        raise RuntimeError(
            f"tone_llm_processing 配置节类型异常: 期望 dict, 实际 "
            f"{type(llm).__name__} ({llm!r:.80s}); "
            f"请检查 sentiment.yaml 该节的 YAML 缩进与值类型。"
        )
    return llm


LLM_CONFIG = _ensure_llm_config(CONFIG)

# 模型列表: 多模型并行请求以支持多数投票(Majority Vote)共识机制
# 推荐至少 3 个模型, 以实现 2/3 多数投票的稳健共识
# 学术依据: Wang et al. (2023, ICLR) — Self-consistency 要求多路径采样后取多数
MODELS = LLM_CONFIG.get('models', [])
MAX_CONCURRENCY = max(1, int(LLM_CONFIG.get('max_concurrency', 10)))
# Prompt 模板: 包含 {title}, {content}, {target_bank}, {co_mentioned_banks} 占位符
PROMPT_TEMPLATE = LLM_CONFIG.get('prompt_template', '')
# Plan-r3 P3-17 接入: 由 core/config.py::_inline_external_prompts 从
# config/prompts/unified_cot.txt 首行 ``# version: <token>`` 自动解析.
# 用于 LLMCache.get/put 的 prompt_version 维度, 防止改 prompt 模板后旧
# cache 静默命中污染分析结果. 默认 "v0" (与 LLMCache 默认值兼容).
PROMPT_VERSION = LLM_CONFIG.get('prompt_template_version', 'v0')
# G-06: 温度参数锁定 — temperature=0 确保确定性推理输出, 保证可复现性
# 学术依据: Lopez-Lira, A., & Tang, Y. (2023). Can ChatGPT forecast stock price
#           movements? Return predictability and large language models.
#           SSRN Working Paper No. 4412788.
#           DOI: https://doi.org/10.2139/ssrn.4412788
#           "We use temperature = 0 to ensure deterministic outputs for
#           reproducibility of sentiment labels."
# 同见: Carlson & Burbano (2026, SMJ §3.3, forthcoming):
#       "temperature should be fixed and reported"
TEMPERATURE = LLM_CONFIG.get('temperature', 0.0)
RANDOM_SEED = LLM_CONFIG.get('random_seed', 42)
FORCE_JSON = LLM_CONFIG.get('force_json', True)

# 显式记录 LLM 推理参数 (G-06: 审稿人可追溯的参数报告)
# fix(log-round4-2026-06-20): 该参数回显移入 main() —— 模块级 emit 会在【本模块被 import 时】
# (如 stage 45 面板构建经 runner→llm_peer_iv import 本模块取 LLMCacheMissError) 触发
# setup_logging(delay=True) 的首写截断, 把 logs/21_tone_llms.log 覆写成 2 行 import banner
# (掩盖真实 stage 21 运行记录)。移入 main() 后仅真正运行 stage 21 时回显, import 不再截断。

# fallback 对齐生产 config (sentiment.yaml::tone_llm_processing.max_retries=80) —
# 2026-06-23 统一决策: 大模型 API 调用失败一律重试 80 次; 误删 YAML 键也不再静默降级到旧 5。
MAX_RETRIES = LLM_CONFIG.get('max_retries', 80)
# 2026-06-26 全项目统一决策: 大模型 API 每次重试间隔固定 10s (flat), 不再指数退避。
# 原 v6/N4 的 min(retry_delay * 2**attempt, retry_backoff_cap) 已废除 (见 _compute_retry_sleep):
# 该指数退避会使约第 8 次重试起每次 sleep 即封顶 600s, 单个持续失败请求耗尽 80 次重试 ≈ 12h,
# 且退避期间占住并发槽拖垮整阶段。retry_backoff / retry_backoff_cap 配置键一并退役。
RETRY_DELAY = LLM_CONFIG.get('retry_delay', 10)

# 用户决策 (2026-06-24): verified 轨情感**平局/空票**在 _aggregate_track 保守
# 降级为'中性'**之前**, 先对该 (行×轨) 的 3 个模型票**绕过缓存重新调实时
# API 最多 N 轮** (温度=0 不变), 试图打破平局 / 补齐缺票; N 轮仍未决再保守
# 降级。N 默认 **80** (与项目"API 失败统一重试 80 次"同量级, 见 memory
# api-retry-unified-80-2026-06-23); 设 <=0 关闭重试 = 退回改前直接保守降级行为。
# 并发结构 (用户决策 2026-06-24, 第三轮回退第二轮的"各轨独立协程"方案):
# **逐轮全局 barrier + 每轮内并发** —— 每一轮把当前全部待决 (行×轨) × 模型票
# 一次性铺开并发重调 (as_completed), 本轮全部跑完才统一重判 pending、进下一轮
# (所有待决轨同步推进); 某轨被打破即从下一轮 pending 剔除。全局并发受
# MAX_CONCURRENCY 信号量约束 (不会因任务铺开数量暴涨而打爆限流)。
# ⚠ 仅**在线模式**执行 (离线确定性 NEWS_PROCESS_LLM_OFFLINE=1 严格只读, 跳过
#   本重试) — 见 _resolve_unresolved_sentiment_tracks。新票经 cache.put
#   INSERT OR REPLACE **回写**确定性锚点 _llm_cache.db → 下次离线可复现该批
#   新结果 (须并入既有 DEFERRED 批次受控重生 golden, 用户已选"回写缓存")。
SENTIMENT_TIE_RETRY_ROUNDS = max(0, int(LLM_CONFIG.get('sentiment_tie_retry_rounds', 80)))
REQUEST_TIMEOUT_TOTAL = float(LLM_CONFIG.get('timeout', 600))
REQUEST_TIMEOUT_CONNECT = float(LLM_CONFIG.get('connect_timeout', min(120, REQUEST_TIMEOUT_TOTAL)))
REQUEST_TIMEOUT_SOCK_CONNECT = float(LLM_CONFIG.get('sock_connect_timeout', REQUEST_TIMEOUT_CONNECT))
REQUEST_TIMEOUT_SOCK_READ = float(LLM_CONFIG.get('sock_read_timeout', REQUEST_TIMEOUT_TOTAL))
CONNECTOR_TTL_DNS_CACHE = int(LLM_CONFIG.get('ttl_dns_cache', 300))
CONNECTOR_KEEPALIVE = float(LLM_CONFIG.get('keepalive_timeout', 60))
AUTH_PROBE_TIMEOUT = float(LLM_CONFIG.get('auth_probe_timeout', min(30, REQUEST_TIMEOUT_TOTAL)))

# 问题3 (golden 跨-run 确定性): 离线确定性守卫开关。
# 设环境变量 ``NEWS_PROCESS_LLM_OFFLINE=1`` 后, stage 21 在缓存 miss 时
# **raise 而非调用付费 API** — 把 "golden 可能因 LLM 重投票静默漂移" 从
# 一种"祈祷"升级为"结构性保证":
#   - 语料全部命中 _llm_cache.db → 端到端字节级确定性复现, $0 (缓存即锚点);
#   - 任一 (model, prompt) miss → 显式 LLMCacheMissError 立即中止, 杜绝
#     "边缘文章重新投票翻转 → 边缘银行掉出 → 行数漂移" 的隐性付费/不确定。
# 默认关闭 (env 未设) → 生产首跑 / 在线回填行为完全不变, 不影响 frozen
# Prompt v8 缓存命中路径。学术依据: Carlson & Burbano (2026 SMJ §3.3)
# version-aware reproducibility — 复现包必须能在纯缓存下重跑出同一结果。
LLM_OFFLINE = os.environ.get('NEWS_PROCESS_LLM_OFFLINE', '').strip().lower() in (
    '1', 'true', 'yes', 'on',
)


class LLMCacheMissError(RuntimeError):
    """离线确定性模式 (``NEWS_PROCESS_LLM_OFFLINE=1``) 下遭遇缓存 miss。

    含义: 当前语料存在未被 ``_llm_cache.db`` 覆盖的 ``(model, prompt)`` 组合,
    意味着 golden 无法在 *不调用付费 API* 的前提下确定性复现。

    修复路径:
    1. 显式在线跑一次 stage 21 (env 不设此开关) 回填缺失缓存; 或
    2. 检查语料 / ``prompt_template_version`` / 模型清单是否相对 golden 漂移
       (漂移会改变缓存键 → 全 miss)。
    """


def _compute_retry_sleep(attempt: int) -> float:
    """计算第 attempt 次重试的 sleep 秒数 — 全项目统一固定间隔。

    2026-06-26 决策: 大模型 API 每次重试间隔统一固定为 ``RETRY_DELAY`` 秒 (默认 10s),
    不再执行原 v6/N4 的指数退避 ``min(RETRY_DELAY * 2**attempt, RETRY_BACKOFF_CAP)``
    (该公式会使第 7 次起每次 sleep 封顶 600s, 单个持续失败请求耗尽 80 次重试 ≈ 12h,
    并在退避期间占住并发槽拖垮整阶段)。``attempt`` 参数保留 (签名稳定供调用方) 但不再参与计算。
    """
    return RETRY_DELAY


def build_llm_timeout() -> aiohttp.ClientTimeout:
    """为大批量验证调用构造保守的超时配置 (total/connect/sock 各维独立)。"""
    return aiohttp.ClientTimeout(
        total=REQUEST_TIMEOUT_TOTAL,
        connect=REQUEST_TIMEOUT_CONNECT,
        sock_connect=REQUEST_TIMEOUT_SOCK_CONNECT,
        sock_read=REQUEST_TIMEOUT_SOCK_READ,
    )


def build_llm_connector(limit: int) -> aiohttp.TCPConnector:
    """构建共享 LLM TCP connector, 显式限制单 host 连接数上限。"""
    safe_limit = max(1, int(limit))
    return aiohttp.TCPConnector(
        limit=safe_limit,
        limit_per_host=safe_limit,
        ttl_dns_cache=CONNECTOR_TTL_DNS_CACHE,
        keepalive_timeout=CONNECTOR_KEEPALIVE,
        enable_cleanup_closed=True,
    )


class AsyncRequestPacer:
    """串行化请求起跑时刻, 防止大批量验证请求瞬时突发 (burst) 打爆限流。"""

    def __init__(self, spacing_seconds: float = 0.0):
        self.spacing_seconds = max(0.0, float(spacing_seconds or 0.0))
        self._lock = asyncio.Lock()
        self._last_started_at = 0.0

    async def wait(self) -> None:
        """阻塞直到距离上一次 ``wait()`` 至少 ``spacing_seconds`` 秒；零间距时立即返回。"""
        if self.spacing_seconds <= 0:
            return
        async with self._lock:
            now = time.monotonic()
            sleep_s = self._last_started_at + self.spacing_seconds - now
            if sleep_s > 0:
                await asyncio.sleep(sleep_s)
            self._last_started_at = time.monotonic()


def build_model_pacers(models: list, spacing_seconds: float = 0.0) -> dict:
    """为每个模型各建一个请求起跑节流器 (pacer); 间距为 0 时返回空 dict。"""
    spacing = max(0.0, float(spacing_seconds or 0.0))
    return {m['model_name']: AsyncRequestPacer(spacing) for m in models} if spacing > 0 else {}


class AsyncModelAvailability:
    """单轮 run 级断路器 (circuit breaker): 标记永久失败模型, 跳过其后续请求。"""

    def __init__(self):
        self._disabled: dict[str, str] = {}
        self._preflighted: set[str] = set()
        self._lock = asyncio.Lock()

    def is_disabled(self, model_id: str) -> bool:
        """True iff ``model_id`` 已被 ``disable()`` 标记为本轮永久失败。"""
        return model_id in self._disabled

    def is_preflighted(self, model_id: str) -> bool:
        """True iff ``model_id`` 已通过预飞行（preflight）健康检查。"""
        return model_id in self._preflighted

    async def disable(self, model_id: str, reason: str) -> None:
        """断路器：把 ``model_id`` 标记为本轮永久失败；幂等，重复调用不重复日志。"""
        async with self._lock:
            if model_id in self._disabled:
                return
            self._disabled[model_id] = reason
            logger.info(
                f"[{model_id}] 模型本轮停用: {reason}; "
                "后续缺缓存请求将跳过，已缓存响应仍会复用"
            )

    async def mark_preflighted(self, model_id: str) -> None:
        """记录 ``model_id`` 已通过 preflight；后续 worker 可跳过冷启动健康检查。"""
        async with self._lock:
            self._preflighted.add(model_id)

    async def note_transient_failure(self, model_id: str, reason: str, row_idx: int) -> None:
        """记录一次性传输/服务端故障 (不停用模型, 仅把该次结果从投票剔除)。"""
        logger.info(f"[{model_id}] 行 {row_idx}: {reason}，该次结果将从投票中排除")


AUTH_FAILURE_STATUSES = {401, 403}


def _summarize_auth_failure(status: int, resp_text: str) -> str:
    """返回简洁且不含密钥的授权失败摘要 (截断长消息, 剥离 request id)。"""
    message = ""
    try:
        payload = json.loads(resp_text or "{}")
        err = payload.get("error", payload)
        if isinstance(err, dict):
            message = str(err.get("message") or err.get("type") or "").strip()
    except (json.JSONDecodeError, TypeError):
        message = str(resp_text or "").strip()
    if "(request id:" in message:
        message = message.split("(request id:", 1)[0].strip()
    if len(message) > 120:
        message = message[:117] + "..."
    return f"状态码 {status} 授权失败" + (f" ({message})" if message else "")


def _strip_prepended_title(text: str, title: str) -> str:
    """剥离 prepend_title 拼接的标题前缀 (entity_context.prepend_title 的近似逆操作)。

    fix(tonellms-01): content_ctx 由 stage13 prepend_title 拼成 ``title + [。] + body``;
    喂 LLM prompt 前需还原为去标题 body, 避免与 {title} 字段重复注入标题。

    fix(omni-g-tonellms-03, 2026-06-11) 披露: 本函数按**文本前缀**剥离, 不是
    prepend_title 的精确逆 — prepend_title 在 body 已以 title 开头时跳过拼接,
    而此处无条件剥离前缀。当实体窗口/正文本身恰以标题文本开头时 (盘上实测
    7/1170 ≈ 0.6%), 剥掉的是窗口真实首句内容 (标题为首句严格前缀时留下断句
    残文)。Prompt 构造与缓存键已字节级冻结 (v8, $0 铁律), 行为不可更改 —
    本条仅作如实披露; 双路径 (stage 13 / stage 21 兜底) 经函数复合验证产出
    逐字相同 prompt, 不构成缓存键分歧。
    """
    from news_process.core.text.entity_context import _TITLE_SEP
    title = str(title or '').strip()
    if not title or not text.startswith(title):
        return text
    rest = text[len(title):]
    if rest.startswith(_TITLE_SEP):
        rest = rest[len(_TITLE_SEP):]
    return rest


# 验证键 SSOT (单一事实源): stage 21 prompt v8 要求 LLM 在 JSON 中返回
# is_bank_fintech_news (真伪精筛主字段)。重试闸门 (_is_cacheable_llm_response,
# 写入侧) 与读取侧缺席判定 (_aggregate_track) **共用此常量** — 二者必须对同
# 一字段达成一致, 否则"通过重试闸门写入缓存"的响应可能在聚合侧仍被判为模型
# 缺席 (或反之), 两处 key 名一旦漂移即静默错配。
_VERIFICATION_KEY = "is_bank_fintech_news"


def _is_cacheable_llm_response(result_text, force_json: bool | None = None) -> bool:
    """HTTP 200 响应写缓存 / 是否触发重试的内容校验 (write-side + retry gate)。

    判为「合格可缓存响应」需同时满足:
      ① result_text 是非空字符串 (非 None / 非纯空白);
      ② 若 FORCE_JSON: 内容 JSON 可解析 **且** 含 ``is_bank_fintech_news`` 键。
    任一不满足 → 视为可重试瞬时失败: ``fetch_llm_async`` 在 200 分支不
    ``cache.put``、不归档, 走现有重试流程**重新调用 API** (上限
    ``MAX_RETRIES`` = 80 次); 耗尽重试仍不合格则返回 ``None``, 由
    ``_aggregate_track`` 按「模型缺席」处理 (与本函数共用 ``_VERIFICATION_KEY``,
    口径严格一致)。

    fix(omni-g-tonellms-02/15, 2026-06-11): 空串 / 纯空白 / (FORCE_JSON 时)
    JSON 不可解析的 200 响应一旦 ``cache.put`` 即被永久冻结为合法命中 —
    ``LLMCache.get`` 的 ``is not None`` 判定把 ``''`` 当有效命中短路返回,
    该 (model, prompt) 格永无重试机会 (实测盘上 idx 982 ctx×deepseekv4 的
    空串已被固化为伪 False 票)。本守卫只在**写入侧**把关: 校验失败按可重试
    瞬时失败处理, 不写缓存、不归档; 既有缓存库 (确定性锚点, 勿删铁律) 中
    已冻结的空串/截断响应**不动**, 由 ``_aggregate_track`` 在读取侧按
    "模型缺席"处理 (见 fix omni-g-tonellms-01/08/15)。

    扩展(2026-06-23): 在「JSON 可解析」之外**追加** ``is_bank_fintech_news``
    键存在性校验 — 缺该键的可解析响应 (如 ``{"sentiment": "正面"}``) 此前
    直接写缓存并在聚合侧记为模型缺席, 现改为同样触发 80 次重试, 给 API 重新
    返回合格响应的机会; 80 次仍缺则落回原模型缺席处理 (按现有问题处理方式)。
    **golden-safe**: 离线确定性复现路径在 ``cache.get`` 命中即短路返回 (早于
    本函数), 既有已缓存条目 (含历史缺键响应) 一律不动; 本扩展仅影响未来
    cache-miss 的在线重跑, 不改 prompt / 缓存键, 不触碰 frozen v8 命中路径。

    Args:
        result_text: API 200 响应的 message.content。
        force_json: 覆盖模块级 FORCE_JSON (测试注入用); None = 取全局值。

    Returns:
        bool: True = 内容非空且 (FORCE_JSON 时) JSON 可解析且含验证键, 允许 cache.put。
    """
    if force_json is None:
        force_json = FORCE_JSON
    if not isinstance(result_text, str) or not result_text.strip():
        return False
    if not force_json:
        return True
    parsed = parse_json_response(result_text)
    return bool(parsed) and _VERIFICATION_KEY in parsed


def _build_llm_request(model_id: str, api_key: str, prompt: str) -> tuple[dict, dict]:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE,
        "seed": RANDOM_SEED,
    }
    if FORCE_JSON:
        payload["response_format"] = {"type": "json_object"}
    return headers, payload


async def preflight_model_availability(
    session: aiohttp.ClientSession,
    models: list,
    model_availability: AsyncModelAvailability,
) -> None:
    """大批量请求开跑前对各模型做一次授权探活 (preflight); 401/403 即停用该模型。"""
    probe_timeout = aiohttp.ClientTimeout(
        total=AUTH_PROBE_TIMEOUT,
        connect=min(AUTH_PROBE_TIMEOUT, REQUEST_TIMEOUT_CONNECT),
        sock_connect=min(AUTH_PROBE_TIMEOUT, REQUEST_TIMEOUT_SOCK_CONNECT),
        sock_read=AUTH_PROBE_TIMEOUT,
    )
    prompt = '请只返回 JSON: {"ok": true}'

    for m in models:
        model_id = m['model_name']
        if model_availability.is_disabled(model_id) or model_availability.is_preflighted(model_id):
            continue
        base_url = m.get('base_url', '')
        api_key = m.get('api_key', '')
        if not base_url or not api_key:
            await model_availability.disable(model_id, "base_url 或 api_key 为空")
            continue
        headers, payload = _build_llm_request(model_id, api_key, prompt)
        try:
            async with session.post(
                f"{base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=probe_timeout,
            ) as resp:
                if resp.status == 200:
                    await model_availability.mark_preflighted(model_id)
                    continue
                resp_text = await resp.text()
                if resp.status in AUTH_FAILURE_STATUSES:
                    await model_availability.disable(
                        model_id, _summarize_auth_failure(resp.status, resp_text)
                    )
                else:
                    await model_availability.mark_preflighted(model_id)
                    logger.info(
                        f"[{model_id}] 模型预检返回状态码 {resp.status}; "
                        "保留正式请求路径以复用重试策略"
                    )
        except asyncio.TimeoutError:
            await model_availability.mark_preflighted(model_id)
            logger.info(f"[{model_id}] 模型预检等待超过时限，保留正式请求路径")
        except Exception:
            await model_availability.mark_preflighted(model_id)
            logger.info(f"[{model_id}] 模型预检暂不可达，保留正式请求路径")


def _log_retryable_transport_issue(
    model_id: str,
    attempt: int,
    sleep_s: float,
    max_attempts: int = MAX_RETRIES,
) -> None:
    logger.debug(
        f"[{model_id}] 连接暂不可用 "
        f"(attempt {attempt + 1:,d}/{max_attempts:,d}) - 等待 {sig4(sleep_s)}s 后重试..."
    )

# ── Logit-to-Score 概率映射法（稳健性检验指标）──────────────────────────
# 将 LLM 三分类标签 + sentiment_confidence 转化为 [-1, +1] 连续分数。
# 学术依据:
#   Törnberg, P. (2023). arXiv:2307.13106. DOI: 10.48550/arXiv.2307.13106
#   Shapiro, A.H. et al. (2022). JoE, 228(2). DOI: 10.1016/j.jeconom.2020.07.053
LOGIT_SCORE_CFG = LLM_CONFIG.get('logit_to_score', {})
LOGIT_SCORE_ENABLED = LOGIT_SCORE_CFG.get('enabled', False)
# fix(log-round4-2026-06-20): 同上, 该回显移入 main() 防 import 期截断 21 日志。


# ============================================================================
# 2. 异步请求大模型 API
# ============================================================================

async def fetch_llm_async(session: aiohttp.ClientSession, semaphore: asyncio.Semaphore,
                          prompt: str, model_cfg: dict, row_idx: int, track: str,
                          cache: LLMCache = None,
                          request_pacer: AsyncRequestPacer | None = None,
                          model_availability: AsyncModelAvailability | None = None,
                          request_timeout: aiohttp.ClientTimeout | None = None,
                          max_retries: int | None = None,
                          prompt_version: str = "v0",
                          force_refresh: bool = False) -> tuple:
    """异步请求单个模型的单篇文章，自带重试保护和缓存。

    model_cfg 结构示例：
        {model_name: ..., short_name: ..., base_url: ..., api_key: ...}
    每个模型可独立指定 base_url 和 api_key。

    Args:
        track: 'full' / 'ctx' / 'ss'，标识本次请求使用的文本轨道。
        cache: LLMCache 实例，用于查询/写入缓存。
        prompt_version: prompt 模板版本字符串 (例如 ``"v8-2026-05-17"``),
            传给 ``LLMCache.get/put`` 用作缓存键命名空间。full/ctx/ss 三轨
            统一使用 PROMPT_VERSION。
        force_refresh: 用户决策 (2026-06-24) verified 轨情感平局/空票重试用 —
            True 时**跳过缓存读取侧** (含命中坏条目自愈删除), 强制走实时 API
            重新求一票; 写入侧 ``cache.put`` (INSERT OR REPLACE) 仍照常回写,
            **覆盖**该 (model, prompt) 的旧缓存条目 → 新票成为确定性锚点。
            ⚠ 仅应在**在线模式** (非 NEWS_PROCESS_LLM_OFFLINE) 下置 True;
            离线模式下置 True 会因缓存 miss 直接 raise LLMCacheMissError
            (调用方 _resolve_unresolved_sentiment_tracks 已用 LLM_OFFLINE 守卫)。

    Returns:
        tuple: (row_idx, model_id, result_text, track)

    白话: 每次问大模型之前先查"账本"(_llm_cache.db): 账本的索引由
    模型名 + 完整 prompt 文本 + prompt 版本号 + temperature 共同决定,
    任何一个字符变了都算新问题。查到了就直接用旧答案 (不花钱、结果
    永远一样); 查不到才真去调付费 API, 拿到合格答案后先记归档再记账本。
    这也是为什么 prompt 模板一个字都不能改 —— 改了索引就全对不上,
    13 万条旧答案全部作废, 得重新花钱问一遍。
    """
    model_id = model_cfg['model_name']
    base_url = model_cfg.get('base_url', '')
    api_key  = model_cfg.get('api_key', '')

    # 缓存查询（sqlite3 同步调用为微秒级，不阻塞事件循环）
    # audit S2 修复: 传入 temperature/random_seed, 让缓存键反映实际推理参数。
    # temperature=0.0 时键与历史一致 (seed 不进键), 改 config 做温度/种子稳健性
    # 扫描时键随之变化, 避免静默命中旧响应。
    #
    # force_refresh (2026-06-24 平局/空票重试): 跳过整个缓存读取侧 (含命中 +
    # 命中坏条目自愈删除), 强制落入下方实时 API 重试路径; 温度=0 下命中缓存
    # 会原样返回首跑那一票 → 平局永不可能被打破, 故重试必须绕过读取。写入侧
    # cache.put (INSERT OR REPLACE) 不受影响, 新票仍回写覆盖旧条目。
    if cache is not None and not force_refresh:
        cached_response = cache.get(model_id, prompt, prompt_version=prompt_version,
                                    temperature=TEMPERATURE, random_seed=RANDOM_SEED)
        if cached_response is not None:
            # 缓存命中读取侧自愈 (2026-06-23): 在线模式下校验命中的缓存响应,
            # 若为坏条目 (空 / 纯空白 / 不可解析 / 缺 is_bank_fintech_news 键,
            # 与写入侧 _is_cacheable_llm_response 同口径) 则**删除该缓存条目并
            # 落入下方实时 API 重试路径重取** (重取成功后回写好响应; 80 次仍坏
            # 则 return None → _aggregate_track 按模型缺席处理)。
            # ⚠ 离线确定性模式 (LLM_OFFLINE) 严格只读 — 不校验不删除, 坏条目
            # 原样返回交 _aggregate_track 按模型缺席处理, 保证离线复现路径字节
            # 不变 (历史 idx 982 等冻结坏条目在离线下行为与改前一致)。
            if LLM_OFFLINE or _is_cacheable_llm_response(cached_response):
                return row_idx, model_id, cached_response, track
            removed = cache.delete(model_id, prompt, prompt_version=prompt_version,
                                   temperature=TEMPERATURE, random_seed=RANDOM_SEED)
            logger.warning(
                f"[{model_id}] 行 {row_idx} ({track} 轨): 缓存命中坏条目 "
                f"(空/不可解析/缺 {_VERIFICATION_KEY} 键, rawlen="
                f"{len(str(cached_response))}); 已删除 {removed} 条缓存, "
                "将重新调用 API 重取"
            )
            # 注意: 不 return, 落入下方实时 API 重试路径 (此处 LLM_OFFLINE 必为
            # False — 离线分支已在上方 return)。

    # 问题3: 离线确定性守卫 — 缓存 miss 且开启离线模式时拒绝任何付费 API
    # 调用, 显式 raise 让 run 经 asyncio.as_completed (run_all_llms) 立即
    # loud-fail。这一步发生在 semaphore / session.post 之前, 保证 $0 与零网络。
    if LLM_OFFLINE:
        raise LLMCacheMissError(
            f"离线确定性模式缓存 miss: model={model_id} row_idx={row_idx} "
            f"track={track} prompt_version={prompt_version}; "
            "需在线回填 _llm_cache.db 或检查语料/prompt_version 漂移"
        )

    if model_availability is not None and model_availability.is_disabled(model_id):
        return row_idx, model_id, None, track

    # 准备请求
    headers, payload = _build_llm_request(model_id, api_key, prompt)

    req_timeout = request_timeout or build_llm_timeout()
    max_attempts = MAX_RETRIES if max_retries is None else max(1, int(max_retries))

    last_failure_reason = f"连续 {max_attempts} 次请求未成功"

    async with semaphore:
        for attempt in range(max_attempts):
            if model_availability is not None and model_availability.is_disabled(model_id):
                return row_idx, model_id, None, track

            sleep_s = _compute_retry_sleep(attempt)
            has_more_attempts = attempt < max_attempts - 1
            try:
                if request_pacer is not None:
                    await request_pacer.wait()
                async with session.post(f"{base_url}/chat/completions", json=payload, headers=headers, timeout=req_timeout) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        result_text = data['choices'][0]['message']['content']
                        # fix(omni-g-tonellms-02/15, 2026-06-11) + 扩展(2026-06-23):
                        # 200 但 completion 为空 / 不可解析 / 缺 is_bank_fintech_news
                        # 键 → 按可重试瞬时失败处理, 走 continue 重新调用 API (上限
                        # MAX_RETRIES=80), **绝不 cache.put**。这是"全力避免坏记录进入
                        # 缓存"的**唯一闸门**: 下方 archive + cache.put 仅在通过本校验后
                        # 可达 (校验失败即 continue), 故空 / 不可解析 / 缺验证键的响应
                        # 永不写入确定性锚点 _llm_cache.db (否则缓存命中后该格永不重试,
                        # 被固化为伪 False 票 / 模型缺席, 即用户实测 rawlen=806/933 现象)。
                        if not _is_cacheable_llm_response(result_text):
                            last_failure_reason = (
                                f"连续 {max_attempts} 次请求未成功，"
                                f"最后一次 200 响应内容为空、不可解析或缺 "
                                f"{_VERIFICATION_KEY} 键"
                            )
                            if has_more_attempts:
                                logger.debug(
                                    f"[{model_id}] 200 响应内容为空/不可解析/缺 "
                                    f"{_VERIFICATION_KEY} 键 "
                                    f"(attempt {attempt+1:,d}/{max_attempts:,d}) "
                                    f"- 等待 {sig4(sleep_s)}s 后重试..."
                                )
                                await asyncio.sleep(sleep_s)
                            continue
                        # v3.7.0 (C1): LLM raw response archive (V4 F-P2.1 critical)
                        # fix(omni-g-tonellms-04, 2026-06-11): archive append 移到
                        # cache.put **之前**, 且归档失败时跳过 put — 消除"先 put 后
                        # archive 异常 → 响应被永久缓存、后续命中短路、归档一次性
                        # 永久漏档"的窗口。归档失败按 warning 处理 (本次投票仍用该
                        # 响应, 不阻塞 pipeline), 下次 run 因未缓存会重调并重试归档。
                        # 注: archive 模块 import 失败 (_LLM_ARCHIVE_AVAILABLE=False)
                        # 时已在模块加载期 loud error, 此处仍照常缓存 (历史行为)。
                        _archive_ok = True
                        if _LLM_ARCHIVE_AVAILABLE:
                            try:
                                # data['model'] 字段为 API 返回的 actual version
                                # (e.g. "gpt-5.4-nano-2026-01"), 与配置 model_id
                                # ("gpt-5.4-nano") 分离 — 顶刊复现关键 critical.
                                actual_version = data.get('model', model_id)
                                # audit S2 修复: cache_key 与上面 get/put 同参,
                                # 保证 archive 反查键与缓存键一致 (temp=0.0 时不变)。
                                cache_key = LLMCache.make_key(
                                    model_id, prompt,
                                    prompt_version=prompt_version,
                                    temperature=TEMPERATURE,
                                    random_seed=RANDOM_SEED,
                                )
                                _llm_archive_record(
                                    cache_key=cache_key,
                                    model_id=model_id,
                                    model_version=actual_version,
                                    prompt=prompt,
                                    response_raw=json.dumps(data, ensure_ascii=False),
                                    prompt_version=prompt_version,
                                    # audit S2 修复: 记录真实 config 温度而非硬编码
                                    # 0.0 — 顶刊复现账本不得对推理参数撒谎。
                                    temperature=TEMPERATURE,
                                    api_endpoint=f"{base_url}/chat/completions",
                                    http_status=resp.status,
                                )
                            except Exception as _arch_exc:
                                _archive_ok = False
                                logger.warning(
                                    f"LLM archive 失败 (不阻塞 pipeline, 本响应不写缓存"
                                    f"以待下次 run 重调+重试归档): {_arch_exc!r}"
                                )
                        if cache is not None and _archive_ok:
                            cache.put(model_id, prompt, result_text,
                                      prompt_version=prompt_version,
                                      temperature=TEMPERATURE,
                                      random_seed=RANDOM_SEED)
                        return row_idx, model_id, result_text, track
                    elif resp.status in (429, 500, 502, 503, 504):
                        last_failure_reason = f"连续 {max_attempts} 次请求未成功，最后状态码 {resp.status}"
                        if has_more_attempts:
                            logger.debug(
                                f"[{model_id}] API 状态码 {resp.status} "
                                f"(attempt {attempt+1:,d}/{max_attempts:,d}) - 等待 {sig4(sleep_s)}s 后重试..."
                            )
                            await asyncio.sleep(sleep_s)
                    else:
                        resp_text = await resp.text()
                        if resp.status in AUTH_FAILURE_STATUSES:
                            reason = _summarize_auth_failure(resp.status, resp_text)
                            if model_availability is not None:
                                await model_availability.disable(model_id, reason)
                            else:
                                logger.info(
                                    f"[{model_id}] 模型本轮停用: {reason}; "
                                    "后续缺缓存请求将跳过，已缓存响应仍会复用"
                                )
                            return row_idx, model_id, None, track
                        logger.error(f"[{model_id}] API 错误 {resp.status}: {resp_text}")
                        break
            except asyncio.TimeoutError:
                last_failure_reason = f"连续 {max_attempts} 次请求等待超过时限"
                if has_more_attempts:
                    logger.debug(
                        f"[{model_id}] 请求等待超过时限 "
                        f"(attempt {attempt+1:,d}/{max_attempts:,d}) - 等待 {sig4(sleep_s)}s 后重试..."
                    )
                    await asyncio.sleep(sleep_s)
            except Exception:
                last_failure_reason = f"连续 {max_attempts} 次连接暂不可用"
                if has_more_attempts:
                    _log_retryable_transport_issue(model_id, attempt, sleep_s, max_attempts)
                    await asyncio.sleep(sleep_s)

    # 所有重试均失败，返回 None 标记（区别于空 JSON，避免影响多数投票）。
    # 5xx/429/网络抖动通常是瞬时问题，不能因此停用整轮模型；否则大样本验证会
    # 因单次故障跳过后续缺缓存请求，扭曲稳健性指标。
    if model_availability is not None:
        await model_availability.note_transient_failure(model_id, last_failure_reason, row_idx)
    else:
        logger.info(f"[{model_id}] 行 {row_idx}: {last_failure_reason}，该模型结果将从投票中排除")
    return row_idx, model_id, None, track


def iter_article_track_prompts(df: pd.DataFrame):
    """逐 (行 × 轨道) yield ``(row_idx, track, prompt)`` — prompt 构造的单一事实源。

    问题3 (确定性): ``run_all_llms`` (生产) 与缓存覆盖审计
    (``scripts/audit/verify_stage21_cache_coverage.py``) **共用此生成器**,
    保证两者构造的 prompt 字节级一致 → ``LLMCache`` 键一致 → 离线确定性
    (缓存全命中 ⟺ golden 可 $0 复现) 可被审计如实证明, 不会因 prompt
    构造在两处各写一遍而悄悄漂移。

    要求 df 含 ``content_ctx`` / ``content_ss`` 列 (stage 13 物化); 缺失时分别
    回退到 ``内容`` (content_full)。
    与历史 full/ctx 行为字节级等价 (原 run_all_llms 内联构造), 不改任何既有
    缓存键; 第三轨 ss (银行+金科同句共现) 是纯加性新增, 仅多 yield 一组
    ('ss', ...) prompt, 不触动 full/ctx 既有命中路径。
    """
    for idx, row in df.iterrows():
        content_full = str(row.get('内容', ''))
        content_ctx = str(row.get('content_ctx', content_full))
        # ss 轨 (银行+金科同句共现): 缺 content_ss 列时优雅回退 content_full
        # (镜像 ctx 的 content_full 回退, 兼容跳过 stage 13 的非标准跑)。
        content_ss = str(row.get('content_ss', content_full))
        target_bank = str(row.get('target_bank', ''))
        title = str(row.get('标题', ''))
        # fix(tonellms-01): content_ctx 已由 stage13 prepend 标题, 若再把 {title} 作独立
        # 字段注入会致 ctx 轨标题双重注入 (full 轨 1 次 / ctx 轨 2 次), 污染 full↔ctx
        # 对照 — 而 llm_vote_tone_ctx 是 P1 G3 主处理。剥离 content_ctx 的标题前缀, 使
        # 三轨 (full/ctx/ss)**近似**对称: 均由 {title} 字段提供标题 1 次 + content
        # 提供去标题正文/窗口 (ss 轨剥离见下方)。
        # fix(omni-g-tonellms-03, 2026-06-11) 披露: "full 轨 (内容 无标题)" 的原声称
        # 仅近似成立 — 实测 7/1170 (0.6%) 文章的原始 `内容` 本身以 `标题` 开头, 这些
        # 文章 full 轨 prompt 标题注入 2 次而 ctx 轨 1 次 (full 轨 content 不经剥离)。
        # Prompt 构造已字节级冻结 (v8 缓存键铁律, $0), 不可改行为修正, 仅如实披露;
        # _strip_prepended_title 的非精确逆局限见该函数 docstring。
        content_ctx_body = _strip_prepended_title(content_ctx, title)
        # ss 轨与 ctx 轨同源 prepend_title (stage 13): content_ss 同样以 {title}
        # 开头, 须按同一逻辑剥离前缀, 使 ss 轨与 ctx/full 三轨**近似**对称 —
        # 均由 {title} 字段提供标题 1 次 + content 提供去标题正文/窗口
        # (_strip_prepended_title 的非精确逆局限见其 docstring, 同样适用 ss)。
        content_ss_body = _strip_prepended_title(content_ss, title)

        # frozen prompt v8: 三轨共用同一 PROMPT_TEMPLATE, content 是唯一变参
        # (full/ctx/ss 交换 content 实参不触模板文本) → 缓存键仅随 content 文本
        # 与 track 命名空间分区, ss 为纯加性新增、不污染 full/ctx 既有命中。
        for track, content in [
            ('full', content_full),
            ('ctx', content_ctx_body),
            ('ss', content_ss_body),  # 银行+金科同句共现轨
        ]:
            prompt = PROMPT_TEMPLATE.format(
                title=title,
                content=content,
                target_bank=target_bank,
                co_mentioned_banks=str(row.get('co_mentioned_banks', '无')),
            )
            yield idx, track, prompt


async def run_all_llms(df: pd.DataFrame, models: list, cache: LLMCache = None) -> dict:
    """逐条并发执行 DataFrame 中所有行对所有配置模型的三轨请求。

    为每行 × 每模型 × 每轨道 生成独立 prompt，通过信号量控制并发数。
    要求 df 中已包含 'content_ctx' / 'content_ss' 列（标准 DAG 由 stage 13
    ctx_materializer 物化; 跳过 stage 13 时由 main() 备援路径兜底物化 ctx /
    由 iter_article_track_prompts 把 content_ss 回退 content_full）。

    Returns:
        dict: {row_idx: {'full': {model_id: res_text}, 'ctx': {...}, 'ss': {...}}}
    """
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    # B3: results_map 三键初始化 — ss 键必须预置, 否则 as_completed 回填
    # results_map[row_idx]['ss'] 时 KeyError。镜像 full/ctx。
    results_map = {i: {'full': {}, 'ctx': {}, 'ss': {}} for i in df.index}

    total_tasks = len(df) * len(models) * 3  # ×3 因为三轨 (full/ctx/ss)
    logger.info(f"逐条请求: {len(df)} 条新闻 × {len(models)} 模型 × 3 轨道 = {total_tasks} 个请求")
    
    # 连接池优化：复用 TCP 连接 + keepalive，减少握手和 TLS 协商开销
    connector = build_llm_connector(MAX_CONCURRENCY)
    request_pacers = build_model_pacers(models, LLM_CONFIG.get('request_spacing_seconds', 0.0))
    model_availability = AsyncModelAvailability()
    async with aiohttp.ClientSession(connector=connector, timeout=build_llm_timeout()) as session:
        # 问题3: 离线确定性模式跳过 preflight 探针 (它本身会 session.post 探活),
        # 保证缓存全命中场景下零网络、$0; 缓存命中发生在 model_availability 检查
        # 之前 (fetch_llm_async), 故跳过 preflight 不影响命中行的返回。
        if not LLM_OFFLINE:
            await preflight_model_availability(session, models, model_availability)
        # 构建任务列表：每行 x 每轨道 x 每模型 (prompt 经 iter_article_track_prompts
        # 单一事实源构造, 与缓存覆盖审计字节级一致)
        real_tasks = []
        for idx, track, prompt in iter_article_track_prompts(df):
            for m in models:
                real_tasks.append(
                    fetch_llm_async(
                        session, semaphore, prompt, m, idx, track, cache=cache,
                        request_pacer=request_pacers.get(m['model_name']),
                        model_availability=model_availability,
                        prompt_version=PROMPT_VERSION,
                    )
                )
        
        completed = 0
        total = len(real_tasks)
        report_interval = max(1, total // 20)  # 每 5% 汇报一次
        next_report = report_interval
        logger.info(f"📡 LLM 三轨逐条请求开始: 共 {total} 个请求")
        
        for coro in asyncio.as_completed(real_tasks):
            row_idx, model_id, res_text, track = await coro
            results_map[row_idx][track][model_id] = res_text
            completed += 1
            if completed >= next_report or completed == total:
                logger.info(
                    f"📡 LLM 请求进度: {completed:,d}/{total:,d} "
                    f"({pct4(completed / total) if total else 'n/a'})"
                )
                next_report += report_interval
        
        logger.info(f"📡 LLM 三轨逐条请求完成: 共 {total} 个请求全部处理完毕")

        # 用户决策 (2026-06-24): verified 轨情感平局/空票, 在 _aggregate_track
        # 保守降级'中性'之前, 先绕过缓存重新调 LLM 最多 SENTIMENT_TIE_RETRY_ROUNDS
        # 轮 (温度=0) 试图打破平局 / 补齐缺票, 仍未决再交保守降级。仅在线模式
        # 执行 (离线确定性模式严格只读, 不在此重新付费调 API)。session 仍存活,
        # 复用同一连接池 / semaphore / pacer / 断路器。
        if not LLM_OFFLINE:
            await _resolve_unresolved_sentiment_tracks(
                session, semaphore, df, models, results_map, cache,
                request_pacers, model_availability,
            )

    return results_map


async def _resolve_unresolved_sentiment_tracks(
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
    df: pd.DataFrame,
    models: list,
    results_map: dict,
    cache: LLMCache | None,
    request_pacers: dict,
    model_availability: "AsyncModelAvailability",
) -> None:
    """对 verified 轨情感平局/空票的 (行×轨) 重新调 LLM, 试图打破平局/补齐缺票。

    用户决策 (2026-06-24): 命中 ``_verified_sentiment_unresolved`` 条件
    (final_v=True 且 verified-only 情感票在 'undefined' 策略下多数决为 None,
    即平局或空票) 的 (行×轨), 在 ``_aggregate_track`` 保守降级为'中性'**之前**,
    先对该轨 3 个模型票**绕过缓存** (``force_refresh=True``) 重新调实时 API,
    最多 ``SENTIMENT_TIE_RETRY_ROUNDS`` 轮 (默认 80, 温度=0 不变); 每轮后重判,
    一旦某轨不再平局/空票即移出待重试集 (并保留其新票); 耗尽仍未决的轨保持
    原样, 由 ``_aggregate_track`` 兜底保守降级。

    **逐轮全局 barrier + 每轮内并发** (用户决策 2026-06-24 第三轮, 回退第二轮的
    "各轨独立协程"方案): 每一轮把**当前全部待决 (行×轨) × 模型票**一次性铺开,
    经 ``asyncio.as_completed`` **并发**重调 (全局并发受 ``fetch_llm_async`` 内
    ``MAX_CONCURRENCY`` 信号量约束); 这一轮的全部请求**跑完才**统一重判 pending、
    进下一轮 (轮与轮之间是 barrier, 所有待决轨同步推进)。某轨某轮被打破即从下
    一轮的 pending 中剔除 (不再重复重调), 故已解析轨不会白跑后续轮次。

    缓存 / 确定性 (用户选"回写缓存"):
        新票经 ``fetch_llm_async`` 写入侧 ``cache.put`` (INSERT OR REPLACE)
        **覆盖**旧条目, 回写确定性锚点 ``_llm_cache.db`` → 下次离线 ($0) 可
        复现该批新结果。代价 = 须并入既有 DEFERRED 批次受控重生 golden。

    ⚠ 仅**在线模式**调用 (调用方已用 ``if not LLM_OFFLINE`` 守卫); 离线确定性
      模式严格只读, 绝不在此重新付费调 API (保证缓存全命中场景字节级复现)。

    副作用披露: 重新调 API 拿到的是该 (model, prompt) 的**全新整条响应**
    (含 verification + sentiment + 创新三维), 温度=0 下通常与首跑近似但 API
    非严格确定 → 可能微调创新维度标签, 极端情况下甚至翻转该轨 final_v
    (新票多数改判非金科 → 该轨退化为 Case B 情感 N/A, 视作"已解析"移出待重试)。
    这是"绕过缓存重新求一票"的固有代价, 与用户意图 (给平局/缺票二次机会) 一致。
    """
    if SENTIMENT_TIE_RETRY_ROUNDS <= 0:
        return

    # prompt 单一事实源: 与首跑 (iter_article_track_prompts) 字节级一致 → 缓存键
    # 一致 → force_refresh 回写命中并覆盖同一条目 (而非另起新键留下旧坏票)。
    prompt_lookup = {
        (idx, track): prompt
        for idx, track, prompt in iter_article_track_prompts(df)
    }

    pending = [
        (idx, track)
        for idx in df.index
        for track in ('full', 'ctx', 'ss')
        if _verified_sentiment_unresolved(results_map[idx][track], models)
    ]
    if not pending:
        logger.info("verified 轨情感平局/空票: 0 个 (行×轨), 无需重试")
        return

    logger.info(
        f"⚖️ verified 轨情感平局/空票: {len(pending)} 个 (行×轨) 待重试 "
        f"(逐轮全局 barrier, 每轮内并发, 最多 {SENTIMENT_TIE_RETRY_ROUNDS} 轮, "
        f"force_refresh 绕过缓存, 温度={TEMPERATURE}); "
        "仍未决者交 _aggregate_track 保守降级'中性'"
    )

    for round_no in range(1, SENTIMENT_TIE_RETRY_ROUNDS + 1):
        if not pending:
            break
        # 这一轮: 当前全部待决 (行×轨) × 模型票一次性铺开, 并发重调 (绕过缓存);
        # as_completed 让本轮请求并发跑, 信号量限全局并发。
        retry_tasks = [
            fetch_llm_async(
                session, semaphore, prompt_lookup[(idx, track)], m, idx, track,
                cache=cache,
                request_pacer=request_pacers.get(m['model_name']),
                model_availability=model_availability,
                prompt_version=PROMPT_VERSION,
                force_refresh=True,
            )
            for (idx, track) in pending
            for m in models
        ]
        for coro in asyncio.as_completed(retry_tasks):
            row_idx, model_id, res_text, track = await coro
            results_map[row_idx][track][model_id] = res_text

        # barrier: 本轮全部请求跑完后再统一重判, 已解析轨剔除出下一轮 pending
        still = [
            (idx, track)
            for (idx, track) in pending
            if _verified_sentiment_unresolved(results_map[idx][track], models)
        ]
        logger.info(
            f"  第 {round_no}/{SENTIMENT_TIE_RETRY_ROUNDS} 轮重试后: "
            f"{len(pending)} → {len(still)} 仍平局/空票"
        )
        pending = still

    if pending:
        logger.info(
            f"⚖️ 重试 {SENTIMENT_TIE_RETRY_ROUNDS} 轮后仍有 {len(pending)} 个 "
            "(行×轨) 平局/空票, 保留原票交 _aggregate_track 保守降级为'中性'"
        )


# ============================================================================
# 3. 结果提取与多数投票聚合
# ============================================================================

def parse_json_response(res_text: str) -> dict:
    """尝试从大模型结果中解析 JSON。

    容错策略:
    1. 自动去除 markdown 代码块包围(```json ... ```),
       因为部分模型(如 GPT 系列)倾向于在 JSON 响应外添加代码块标记。
    2. 若解析结果是 list (DeepSeek Grok 偶尔返回 [{...}] 数组包裹形式),
       且首元素为 dict, 则解包返回首元素。
    3. 任何其他非 dict 解析结果统一返回 {}, 由上层视为"模型缺席"通道。
    """
    try:
        # 去除 markdown json 代码块包围
        text = res_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        result = json.loads(text.strip())
        if isinstance(result, dict):
            return result
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
            return result[0]
        return {}
    except Exception:
        return {}

def majority_vote_bool(bools: list) -> bool:
    """严格多数决判断真伪（超过半数才通过）。
    
    采用严格多数（strict majority, >50%）而非简单多数（plurality）：
    投票数必须**严格超过**总票数的一半才判定为通过。
    例如 2 票中 1 票为 True → 不通过（1 不超过 2/2=1.0）。
    
    学术依据:
      Wang, X., et al. (2023). Self-consistency improves chain of thought
      reasoning in language models. ICLR 2023.
      DOI: https://doi.org/10.48550/arXiv.2203.11171
      该文提出多路径采样后取多数投票作为最终答案的共识机制。
    """
    if not bools: return False
    return sum(bools) > (len(bools) / 2.0)

def majority_vote_categorical(
    votes: list,
    tie_strategy: str,
    tie_default=None,
    empty_fallback=None,
):
    """统一分类多数投票，参数化平局策略与空票回退。

    本函数为 sentiment / innovation_locus / innovation_substantiveness
    三种分类投票的统一入口；策略差异通过参数显式声明（而非分散在 inline
    Counter 中），便于论文 Methods 章节直接 quote。

    平局策略 (tie_strategy)
    -----------------------
    - 'undefined':    平局 → None
                      适用 3-class 含独立中性类的场景（如 sentiment）。
                      v6/F2 修订要求严格未定义而非污染独立中性类。
    - 'conservative': 平局 → tie_default
                      适用 2-class，归 modal class prior，等价于 uniform
                      prior 下的 MAP (Maximum A Posteriori) decision。

    Args:
        votes:          标签列表（元素须 hashable；Counter 不支持 list/dict 元素）
        tie_strategy:   'undefined' | 'conservative'
        tie_default:    'conservative' 策略必需；'undefined' 时忽略
        empty_fallback: votes 为空时返回值（默认 None）

    Returns:
        多数决结果；空票返回 empty_fallback；平局按 tie_strategy 处理

    Raises:
        ValueError: tie_strategy 未知；或 'conservative' 缺 tie_default
                    （fail-fast: 入口即校验，不延迟到平局时）

    学术依据:
        Wang et al. (2023) ICLR. Self-consistency improves chain of
          thought reasoning in language models.
          DOI: https://doi.org/10.48550/arXiv.2203.11171
        v6/F2 内部决策: 平局 → None 严格未定义，避免污染独立中性类。
        Bayesian MAP rationale: Bishop, C.M. (2006). Pattern Recognition
          and Machine Learning. Springer. §1.5 (Decision Theory).
    """
    # fail-fast 入口校验：比延迟到平局更易调试，且生产 callsite 全部 hardcoded
    if tie_strategy not in ('undefined', 'conservative'):
        raise ValueError(f"Unknown tie_strategy: {tie_strategy!r}")
    if tie_strategy == 'conservative' and tie_default is None:
        raise ValueError(
            "tie_strategy='conservative' requires tie_default to be specified"
        )

    if not votes:
        return empty_fallback
    c = Counter(votes)
    top = c.most_common(2)
    if len(top) > 1 and top[0][1] == top[1][1]:
        if tie_strategy == 'undefined':
            return None
        return tie_default  # 'conservative' 已 fail-fast 保证 tie_default 非 None
    return top[0][0]


def _resolve_locus_track(innov_loci_track: list, topics_track: list) -> tuple:
    """解析单一轨道 (full / ctx / ss) 的 locus 标签 + 置信度。

    Returns (label, confidence)。Plan v14 §3.1 P1.5: 三轨 (full/ctx/ss) 平局策略对称。
    原为 main() 内联闭包, 提取为模块级以便 import-based 回归测试。

    fix(omni-g-tonellms-10, 2026-06-11): 零证据路径返回 (None, 0.0) —
    此前 empty_fallback=_kw_cat 接住 canonicalize_topic 的硬默认
    ('应用场景', 0.0) (空入参/三轮匹配全失败的基率归类, 见
    canonicalization.py fix omni-g-entity-05 披露), 致 LLM 零票 + 零关键词
    证据的文章 (含全部未验证文章, topics 按 prompt 为 null) 也被分类为
    '应用场景' (盘上实证 null=0/857 而 subst/collab 分别有 234/295 null;
    ctx 轨 62 个未验证行 60 个获标签, 其中 30 个 category_confidence==0
    纯零证据默认)。与 subst/collab 的 empty_fallback=None 对称化:
    - LLM 票为空且关键词分类器零证据 (_kw_conf == 0) → (None, 0.0);
    - LLM 票为空但关键词有真实证据 (_kw_conf > 0) → keyword 回退保留;
    - 有 LLM 票时平局 tie_default='应用场景' 保留 (有票的 MAP 是另一回事),
      LLM × keyword 交叉验证 boost/penalty 行为不变。
    """
    _combined_topic = ' '.join(topics_track) if topics_track else ''
    _kw_cat, _kw_conf = canonicalize_topic(_combined_topic)
    if not innov_loci_track:
        # 空 LLM 票: 仅当 keyword 分类器有真实证据 (conf > 0) 时回退 keyword
        # 类目; canonicalize_topic 的零证据基率默认 ('应用场景', 0.0) 不再
        # 冒充分类信号 → 与 subst/collab 一致返回 None。
        if _kw_conf > 0:
            return _kw_cat, _kw_conf
        return None, 0.0
    _majority = majority_vote_categorical(
        innov_loci_track,
        tie_strategy='conservative',
        tie_default='应用场景',
        empty_fallback=None,  # unreachable: 上方已处理空票
    )
    # LLM × keyword 交叉验证：一致 → +0.2 boost；分歧 → ×0.5 penalty
    if _majority == _kw_cat:
        _final_conf = min(_kw_conf + 0.2, 1.0)
    else:
        _final_conf = round(_kw_conf * 0.5, 3)
    return _majority, _final_conf


def _avg_innovation_confidence(parsed: dict, dim: str, models: list) -> float:
    """行级创新维度置信度均值 (W&Z + Gomber + Chesbrough 维度, 三轨 full/ctx/ss 独立)。

    原为 main() 内联闭包 ``_avg_conf``, 提取为模块级以便 import-based 回归测试。

    fix(omni-g-tonellms-13, 2026-06-11): 聚合域与标签聚合域对齐 — 仅纳入对应
    维度标签非 None (canonical 集接受) 的模型置信度。prompt 仅对标签写
    "false 时填 null" 指示, 模型判 false/标签 null 时仍 emit 置信度数值,
    此前无条件进均值, 致分子 (标签投票) 与伴随置信度 (信号强度) 来自不同
    模型子集 (盘上实证 "无标签却有置信度" 行 subst full=7/ctx=13,
    collab full=7/ctx=11)。镜像 H1 "sentiment-not-None 过滤" 语义。

    Args:
        parsed: _aggregate_track 的 per_model_parsed 字典。
        dim: 'innovation_substantiveness' | 'innovation_locus'
             | 'innovation_collab_mode'。
        models: MODELS 配置列表 (含 short_name)。

    Returns:
        float: 被接受标签模型的 confidence(>0) 均值; 无有效项时 0.0。
    """
    confs = [
        parsed.get(f"{m['short_name']}_{dim}_confidence", 0.0)
        for m in models
        if parsed.get(f"{m['short_name']}_{dim}") is not None
    ]
    valid = [c for c in confs if c and c > 0]
    return sum(valid) / len(valid) if valid else 0.0


def majority_vote_sentiment(sents: list, tie_strategy: str = 'undefined'):
    """多数决判断情感（v6/F2: 平局策略可配置）。

    v6 改动 (F2 修复)：
    ----------------
    历史行为：平局 → 强制返回 "中性"，与"全员中性"在数据上不可区分，
              且与上层 verified=False → forced "中性" 共同污染 is_neutral 列。
              诊断显示 81.7%(_full) / 84.1%(_ctx) 的中性标签源自污染，
              而非真实中性新闻。
    v6 新行为：默认平局返回 None，交由上层标记为 llm_undefined=1，与真实
            中性严格区分；保留 'neutral' 作 robustness 备选。

    ⚠ 生产现状 (用户决策 2026-06-23, 见 _aggregate_track 的 final_v 分支)：
        **本函数默认 ('undefined') 保持不变** (供单测/稳健性), 但 stage 21 生产
        callsite 已 **promote** 到 `tie_strategy='neutral'` (平局→保守"中性") + 对
        空票显式补降级"中性" —— 即 v6/F2 的"平局→None"在生产侧已被逆转, verified
        轨不再产 llm_undefined。改本函数默认会破坏 test_aggregate_track_decoupling /
        test_majority_vote_categorical 的 'undefined' 断言, 故**勿改默认**, 仅生产
        callsite 选策略。

    Implementation note:
        2026-05-14 重构：内部委托给 majority_vote_categorical 以统一三处
        分类投票实现；本函数签名与行为 100% 向后兼容（已 byte-level 边界验证）。

    Args:
        sents: list of "正面"/"中性"/"负面" labels
        tie_strategy: 'undefined' (返回 None) / 'neutral' (历史行为，返回"中性")
                      其它值沿用历史"安全回退到 undefined"语义

    Returns:
        str | None: 多数决结果；None 表示空票或平局-undefined 策略
    """
    if tie_strategy == 'neutral':
        return majority_vote_categorical(
            sents, tie_strategy='conservative', tie_default='中性'
        )
    # 默认 'undefined'；其它未知策略沿用历史"安全回退到 undefined"语义
    return majority_vote_categorical(sents, tie_strategy='undefined')


def compute_prob_score(sentiment_label: str, confidence: float) -> dict:
    """基于情感标签和置信度计算概率映射连续分数 [-1, +1]。

    【白话解释】
      把大模型输出的"正面/中性/负面"标签 + 它自己报的置信度数字，
      转换成一个 -1 到 +1 之间的连续分数。分数越接近 +1 表示越正面，
      越接近 -1 表示越负面，0 表示中性。

    【学术依据】
      概率映射法 (Logit-to-Score):
        Törnberg, P. (2023). How to use large language models for text analysis.
        arXiv:2307.13106. DOI: 10.48550/arXiv.2307.13106
        → 利用 LLM 分类输出构建连续分析指标的方法论框架

      连续情感度量在金融计量中的必要性:
        Shapiro, A.H., Sudhof, M. & Wilson, D.J. (2022). Measuring news
        sentiment. Journal of Econometrics, 228(2), 221-243.
        DOI: 10.1016/j.jeconom.2020.07.053

      剩余概率均分 (1-c)/2 的理论基础 — 最大熵原理:
        Jaynes, E.T. (1957). Information theory and statistical mechanics.
        Physical Review, 106(4), 620-630. DOI: 10.1103/PhysRev.106.620
        → 在已知主类概率 c 的约束下，最大化 Shannon 熵的
          唯一解为其余类均匀分布: P(其余) = (1-c)/2

    【局限性声明】
      sentiment_confidence 是 LLM 生成的文本数值（verbalized confidence），
      非内部 softmax 概率。它作为分类确信度的**序数代理变量**使用，
      不可直接解释为校准后的概率。

      已知局限 — 系统性过度自信:
        Xiong, M. et al. (2024). Can LLMs express their uncertainty?
        ICLR 2024. DOI: 10.48550/arXiv.2306.13063
        → LLM verbalized confidence 倾向过度自信，但保序性基本成立，
          即 conf(A) > conf(B) 时 acc(A) > acc(B)，
          因此作为序数代理变量（ordinal proxy）在排序层面可靠。

      LLM 文本标注能力的基准验证:
        Gilardi, F. et al. (2023). PNAS, 120(30), e2305016120.
        DOI: 10.1073/pnas.2305016120

    【概率模拟策略】
      P2 路径 (0 < confidence ≤ 1):
        主类概率 = c, 其余两类概率 = (1-c)/2
        公式: Score = P(正面) - P(负面)
      P3 路径 (confidence == 0 或 None/falsy 缺失):
        one-hot: 主类=1.0, 其余=0.0
        Score ∈ {+1.0, 0.0, -1.0}
      P3_INV 路径 (confidence 为 NaN 或 ∉[0,1] — 无效输入域):
        fix(omni-g-tonellms-07/11, 2026-06-11): 与 compute_prob_score_binary
        的输入域政策对齐 — 显式拒绝, 返回 prob_score=NaN / prob_source="P3_INV",
        由聚合层按 isnan 剔除。此前 NaN 因 CPython ``min(1.0, nan)`` 返回 1.0
        被静默编码为满置信 ±1.0 (P2), 越界值 (如百分制误报 confidence=95) 被
        静默 clip 成最强信号 — 而 binary 版对同类输入返回 NaN/"P3_BIN" 拒绝,
        同一构念双政策不一致。

    【数学性质】（已数学证明，P2 路径 c ∈ (0, 1]）
      - label="中性" → Score ≡ 0（∀ c，因 P_pos = P_neg = (1-c)/2）
      - label="正面" → Score = (3c-1)/2 ∈ (-0.5, 1.0]
        当 c > 1/3 时 Score > 0（符合直觉）
        当 c = 1/3 时 Score = 0（三类等概率，信号消失）
        当 c < 1/3 时 Score < 0（模型不确定性压倒分类标签）
        实践中 LLM confidence 通常 ∈ [0.6, 0.95]，Score 始终 > 0
      - label="负面" → Score = (1-3c)/2 ∈ [-1.0, 0.5)
        对称于"正面"，c > 1/3 时 Score < 0
      - Σ(P_pos + P_neu + P_neg) = 1（概率公理）

    Args:
        sentiment_label: "正面" / "中性" / "负面"
        confidence: LLM 自报 sentiment_confidence ∈ [0, 1];
            NaN / 越界 ([0,1] 之外) 属无效输入域 → P3_INV 拒绝 (见上)。

    Returns:
        dict: prob_pos, prob_neu, prob_neg (各∈[0,1], Σ=1),
              prob_score ∈ [-1, +1],
              prob_source: "P2" / "P3" / "P3_INV" (无效输入域, 全 NaN)
    """
    LABEL_MAP = {"正面": "positive", "中性": "neutral", "负面": "negative"}
    cls = LABEL_MAP.get(sentiment_label, "neutral")

    # fix(omni-g-tonellms-07/11, 2026-06-11): NaN / 越界 confidence 显式拒绝
    # (镜像 compute_prob_score_binary 的 NaN/"P3_BIN" 路径), 不再静默映射为
    # 满置信 c=1.0 (NaN) 或 clip (越界)。None/0.0 等 falsy 缺失保持历史 P3
    # one-hot 语义 (生产 caller 默认 0.0, 与盘上值兼容)。
    if confidence:
        try:
            _c_float = float(confidence)
        except (TypeError, ValueError):
            _c_float = float('nan')
        if math.isnan(_c_float) or _c_float < 0.0 or _c_float > 1.0:
            _nan = float('nan')
            return {
                "prob_pos": _nan,
                "prob_neu": _nan,
                "prob_neg": _nan,
                "prob_score": _nan,
                "prob_source": "P3_INV",
            }
        c = _c_float
    else:
        c = 0.0
    if c > 0:
        probs = {k: (1.0 - c) / 2.0 for k in ["positive", "neutral", "negative"]}
        probs[cls] = c
        source = "P2"
    else:
        probs = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
        probs[cls] = 1.0
        source = "P3"

    score = probs["positive"] - probs["negative"]

    return {
        "prob_pos": probs["positive"],
        "prob_neu": probs["neutral"],
        "prob_neg": probs["negative"],
        "prob_score": round(score, 6),
        "prob_source": source,
    }


# 创新维度 binary 标签的 canonical 集合
# - W&Z 1994/1998 ASQ: 实质性 / 象征性 (innovation_substantiveness)
# - Gomber, Koch & Siering 2017 (Digital Finance Cube) 二元直接出处 / Gomber et al. 2018 JMIS 领域综述背景: 底层技术 / 应用场景 (innovation_locus)
# - v3.4.0 新增 Chesbrough 2003 + L&S 2006 SMJ: 自主研发 / 外部协同 (innovation_collab_mode)
VALID_BINARY_LABELS = {
    "实质性", "象征性",
    "底层技术", "应用场景",
    "自主研发", "外部协同",
}


def compute_prob_score_binary(label, confidence, positive_class) -> dict:
    """二分类 prob_score ∈ [0, 1], 用于 innovation_substantiveness / innovation_locus / innovation_collab_mode。

    Plan v1.37 P2 §5.2-5.3.1; 镜像 3-class compute_prob_score 在二分类
    标签下的语义。返回 {prob_score, prob_source}, 其中
    prob_source ∈ {"P2_BIN", "P3_BIN"} (与既有 P2/P3 代码并行)。

    学术锚点 (原文保留):
      - Cover & Thomas (2006) §2 — Bernoulli/binary entropy.
      - Jaynes (1957) — 最大熵的历史框架; 二分类情形退化为直接归一化
        (单一线性约束)。
      - Törnberg (2023) — LLM verbalized confidence → 连续指标。
      - Shapiro/Sudhof/Wilson (2022 J.Econometrics) — 连续因变量。
      - Platt 1999 未使用; De Kok 2025 不适用 (仅 3-class)。

    推导: LLM 输出预测标签 ℓ ∈ {0, 1} 与自报置信度 c (解释为 P(ℓ|x) = c)。
    归一化得 P(¬ℓ|x) = 1 − c。下游重标记: prob_score = P(positive_class|x),
    若 ℓ == positive_class 则等于 c, 否则等于 1 − c。positive_class 的指定
    仅是下游计量编码约定, 不含价值判断。

    输入域校验 (plan §5.3.1, R29A-01 / R20A-01):
      - positive_class ∉ VALID_BINARY_LABELS → (NaN, "P3_BIN")  [Rule 0]
      - label 为 None / confidence 为 None → (NaN, "P3_BIN")
      - label ∉ VALID_BINARY_LABELS → (NaN, "P3_BIN")
      - confidence 越出 [0, 1] (如 1.0001 / -0.0001 舍入) → (NaN, "P3_BIN")
      - confidence == 0 → one-hot 回退 (label==positive_class → 1.0;
        否则 → 0.0), "P3_BIN"。该不连续点为 plan §5.3.1 设计澄清的刻意
        行为 (与 3-class P3 路径平行)。
      - label == positive_class 且 0 < c ≤ 1 → (c, "P2_BIN")
      - label != positive_class 且 0 < c ≤ 1 → (1 − c, "P2_BIN")

    白话: 模型只在两个选项里二选一并附一个把握度 c。若它选的是我们
    编码为 1 的那一类, 分数就是 c; 选的是另一类, 分数就是 1−c
    (它有 c 的把握不是这一类)。把握度缺失或不在 0~1 之间属于答非所问,
    直接记 NaN 不入聚合。
    """
    if positive_class not in VALID_BINARY_LABELS:
        return {"prob_score": float("nan"), "prob_source": "P3_BIN"}
    if label is None or confidence is None:
        return {"prob_score": float("nan"), "prob_source": "P3_BIN"}
    if label not in VALID_BINARY_LABELS:
        return {"prob_score": float("nan"), "prob_source": "P3_BIN"}
    try:
        c = float(confidence)
    except (TypeError, ValueError):
        return {"prob_score": float("nan"), "prob_source": "P3_BIN"}
    if c < 0.0 or c > 1.0:
        return {"prob_score": float("nan"), "prob_source": "P3_BIN"}
    if c == 0.0:
        # one-hot 回退 (plan §5.3.1 设计澄清的刻意不连续点)
        return {
            "prob_score": 1.0 if label == positive_class else 0.0,
            "prob_source": "P3_BIN",
        }
    if label == positive_class:
        return {"prob_score": c, "prob_source": "P2_BIN"}
    return {"prob_score": 1.0 - c, "prob_source": "P2_BIN"}


def _verified_sentiment_unresolved(model_res_dict: dict, models: list) -> bool:
    """判定某轨是否为「verified 轨情感平局/空票」(平局/空票重试的触发条件)。

    口径与 ``_aggregate_track`` **严格一致** (复用同一 SSOT: ``_VERIFICATION_KEY``
    / 三类情感标签 ``正面/中性/负面`` / ``majority_vote_bool`` /
    ``majority_vote_sentiment``), 仅抽取判定平局/空票所需的最小解析, 不构建
    per_model_parsed / 创新维度 / 置信度 (那些由 ``_aggregate_track`` 负责)。
    ⚠ 若 ``_aggregate_track`` 的 v/s 解析口径变动, 本谓词须同步 (二者必须对
       "哪些是 verified-only 情感票"达成一致, 否则重试触发集与最终降级集错位)。

    返回 True ⟺ ``final_v=True`` (整篇被多数判为银行金科) **且** verified-only
    情感票在 'undefined' 策略下多数决为 None —— 'undefined' 策略对**平局**
    (无严格多数) 与**空票** (无任一可解析情感票) 均返回 None, 恰好覆盖用户
    指定的两种待重试态。``final_v=False`` (Case B 非金科) → 情感本就 N/A,
    返回 False (不触发重试; 用户决策 2026-06-24 范围明确限 verified 轨)。
    """
    v_votes = []
    s_votes_verified_only = []
    for m in models:
        raw_text = model_res_dict.get(m['model_name'])
        # call-failure / 空串: 与 _aggregate_track 同, 按"模型缺席"跳过 (不投票)
        if raw_text is None or not str(raw_text).strip():
            continue
        jd = parse_json_response(raw_text)
        # 不可解析 / 缺验证键: 同 _aggregate_track 按"模型缺席"跳过
        if not isinstance(jd, dict) or not jd or _VERIFICATION_KEY not in jd:
            continue
        v = jd.get(_VERIFICATION_KEY, False)
        if isinstance(v, str):
            v = v.strip().lower() in ('true', '1', 'yes')
        v = bool(v)
        v_votes.append(v)
        s_raw = jd.get('sentiment')
        s = s_raw.strip() if isinstance(s_raw, str) else None
        if s not in ('正面', '中性', '负面'):
            s = None
        # v6/F2 门控: 仅通过 verification 的模型情感票计入 (镜像 _aggregate_track)
        if s is not None and v:
            s_votes_verified_only.append(s)
    if not majority_vote_bool(v_votes):
        return False  # Case B (非金科): 情感 N/A, 不重试
    return majority_vote_sentiment(s_votes_verified_only, tie_strategy='undefined') is None


def _aggregate_track(model_res_dict: dict, models: list) -> tuple:
    """对某一轨道的模型响应进行解析和多数投票聚合。

    v6/F2 改动 (篇章级编码契约重写)
    ----------------------------------
    1. **解除 verification 与 sentiment 的耦合**：单模型 verified=False 不再
       强制改写其 sentiment 为 "中性"。每个模型独立保留自己的 sentiment 判定。
    2. **聚合 sentiment 投票仅纳入"通过 verification 的模型"**：避免拒绝该
       新闻为金融科技的模型对情感投票产生噪声贡献。
    3. **平局/空票 → 保守降级"中性"** (用户决策 2026-06-23, 逆转原 v6/F2 平局→None)：
       verified 轨 (final_v=True) 情感平局/空票一律保守降级为"中性" (与创新三维
       tie_default 同款 conservative MAP); llm_undefined_* 因此结构性恒 0, 下游
       is_neutral_* 正常编码。**仅** final_v=False (整文被多数判非金科) 轨情感仍为
       None (N/A, 不注入伪中性)。
    4. **新增 4 个状态指标**：n_valid_votes / n_verifying_votes /
       call_failure / undefined，用于下游精细化掩码。
    5. **agree_rate 拆分**：agree_rate_v (验证投票一致率) /
       agree_rate_s (情感投票一致率，仅在 verifying 子集上计算)。

    Returns:
        tuple (18 elements, v3.4.0 BREAKING from v1.37 P2 16-tuple):
                (final_v, final_s, agree_rate_v, agree_rate_s,
                 n_valid_votes, n_verifying_votes,
                 call_failure, undefined,
                 per_model_parsed, topics, innov_loci, innov_substs,
                 n_failures, avg_prob_score,
                 avg_subst_prob_score, avg_locus_prob_score,
                 innov_collab_modes, avg_collab_prob_score)
            per_model_parsed: {f'{short}_verified': v, ...} 的字典；v7 起亦含
                              {short}_innovation_substantiveness_confidence /
                              {short}_innovation_locus_confidence 每模型独立置信度;
                              v3.4.0 起追加 {short}_innovation_collab_mode +
                              {short}_innovation_collab_mode_confidence (Chesbrough 2003).
            innov_loci:       LLM 创新位点投票列表 (底层技术 / 应用场景)
            innov_substs:     LLM 创新实质性投票列表 (实质性 / 象征性)；v3.0.0
                              (v8) 起翻译层已废除, panel 列值即 LLM 原始输出, 列后缀
                              统一为 _sub / _symb (Westphal & Zajac 1994/1998 ASQ
                              substantive-symbolic 框架)
            innov_collab_modes (v3.4.0): LLM 创新协作模式投票列表 (自主研发 / 外部协同);
                              Chesbrough 2003 Open Innovation + Laursen & Salter 2006 SMJ;
                              additive supplementation per Nosek 2018 PNAS, v7 双维语义不变.
            avg_prob_score:   Logit-to-Score 多模型平均概率分数 (sentiment, 3-class) ∈ [-1, +1]
            avg_subst_prob_score: Binary prob_score for substantiveness (positive_class=象征性) ∈ [0, 1]
            avg_locus_prob_score: Binary prob_score for locus (positive_class=应用场景) ∈ [0, 1]
            avg_collab_prob_score (v3.4.0): Binary prob_score for collab_mode
                                            (positive_class=外部协同) ∈ [0, 1]

    白话: 三个大模型各自独立读同一篇新闻, 各投两票: 第一票"这是不是
    银行金融科技新闻"(真伪), 第二票"语气是正面/中性/负面"(情感)。
    真伪票按"过半数"裁定; 情感票只数那些第一票投了"是"的模型 (认为
    新闻不相关的模型, 它的情感意见不作数)。情感票打成平手 (或验证通过却
    没人给得出情感) 时, 保守判为"中性"而不再标"未定"(用户决策 2026-06-23:
    跟"实质性/应用场景/自主研发"三维平局降级同款保守口径, 下游不再因
    "未定"剔除这些 verified 文章)。但**整篇被多数判为"非银行金科"**的, 情感
    仍留空 (None/N/A) —— 不给判为不相关的文章硬塞中性。模型调用失败或
    答非所问 (JSON 解析不出) 按"缺席"处理, 既不投票也不充当反对票。
    """
    v_votes = []
    s_votes_all = []           # 所有成功调用模型的 sentiment（含 verified=False 模型）
    s_votes_verified_only = [] # 仅含 verified=True 模型的 sentiment（v6/F2 新逻辑）
    topics = []
    innov_loci = []            # v7: 原 llm_categories (Gomber, Koch & Siering 2017 Digital Finance Cube 技术-应用层; Gomber et al. 2018 JMIS 为领域综述背景)
    innov_substs = []          # v7: 原 text_types (W&Z 1994/1998 ASQ 实质-象征)
    innov_collab_modes = []    # v8 新增 (Chesbrough 2003 + L&S 2006 SMJ 自主-外部协同)
    per_model_parsed = {}
    n_failures = 0

    for m in models:
        short = m['short_name']
        # Plan v1.37 P2 §5.3.1 Step A (R19B-01 + R20A-01): 每轮模型迭代开头
        # 无条件 default-init 全部 innovation 键 — 同时覆盖 API 失败的
        # `continue` 分支与正常解析分支 (合法标签在下方覆写)。
        # v3.4.0 BREAKING: 第三维度 innovation_collab_mode 加入 (additive supplementation
        # per Nosek 2018 PNAS; v7 substantiveness/locus 语义不变).
        per_model_parsed[f"{short}_innovation_locus"] = None
        per_model_parsed[f"{short}_innovation_substantiveness"] = None
        per_model_parsed[f"{short}_innovation_collab_mode"] = None
        per_model_parsed[f"{short}_innovation_locus_confidence"] = 0.0
        per_model_parsed[f"{short}_innovation_substantiveness_confidence"] = 0.0
        per_model_parsed[f"{short}_innovation_collab_mode_confidence"] = 0.0

        m_id = m['model_name']
        raw_text = model_res_dict.get(m_id)

        # fix(omni-g-tonellms-15, 2026-06-11): 缓存层历史冻结的空串响应 ('')
        # 在读取侧与 None (call-failure) 同路径按"模型缺席"处理 — 不动缓存库
        # (确定性锚点), 写入侧守卫见 _is_cacheable_llm_response。
        if raw_text is None or not str(raw_text).strip():
            n_failures += 1
            per_model_parsed[f"{short}_verified"] = None
            per_model_parsed[f"{short}_sentiment"] = None
            per_model_parsed[f"{short}_verification_confidence"] = 0.0
            per_model_parsed[f"{short}_sentiment_confidence"] = 0.0
            continue

        jd = parse_json_response(raw_text)
        # 双重保险：parse_json_response 已统一返回 dict，但仍防御 LLM 异常输出
        if not isinstance(jd, dict):
            jd = {}

        # fix(omni-g-tonellms-01/08, 2026-06-11): 解析失败 (jd=={}) 或缺
        # is_bank_fintech_news 键的响应 = "模型缺席", 与 call-failure 同口径
        # (verified=None / 不入 v_votes / 不计 n_valid_votes / n_failures+1) —
        # 兑现 parse_json_response docstring 的"模型缺席"契约。此前被静默编码
        # 为 verified=False 拒绝有效票, 污染 n_valid_votes / agree_rate_v /
        # 下游连续 DV (encode 的 ×agreement_rate 衰减) 与 HC 子样本 (agr≥0.67
        # 剔除); 与 sentiment 通道 (s=None 不入票) 编码不一致, 叠加 call-failure
        # 可翻转 final_v (盘上 8 例 deepseekv4 截断/空响应坐实)。
        if not jd or _VERIFICATION_KEY not in jd:
            n_failures += 1
            logger.warning(
                f"[{m_id}] 响应不可解析或缺 {_VERIFICATION_KEY} 键 "
                f"(rawlen={len(str(raw_text))}), 按模型缺席处理, "
                f"该模型本篇判定从投票中排除"
            )
            per_model_parsed[f"{short}_verified"] = None
            per_model_parsed[f"{short}_sentiment"] = None
            per_model_parsed[f"{short}_verification_confidence"] = 0.0
            per_model_parsed[f"{short}_sentiment_confidence"] = 0.0
            continue

        v = jd.get(_VERIFICATION_KEY, False)
        if isinstance(v, str):
            v = v.strip().lower() in ('true', '1', 'yes')
        v = bool(v)

        s_raw = jd.get('sentiment')
        if isinstance(s_raw, str):
            s = s_raw.strip()
            if s not in ('正面', '中性', '负面'):
                s = None
        else:
            s = None

        v_votes.append(v)

        if s is not None:
            s_votes_all.append(s)
            if v:
                s_votes_verified_only.append(s)

        per_model_parsed[f"{short}_verified"] = v
        per_model_parsed[f"{short}_sentiment"] = s
        try:
            per_model_parsed[f"{short}_verification_confidence"] = float(jd.get('verification_confidence', 0.0) or 0.0)
        except (ValueError, TypeError):
            per_model_parsed[f"{short}_verification_confidence"] = 0.0
        try:
            per_model_parsed[f"{short}_sentiment_confidence"] = float(jd.get('sentiment_confidence', 0.0) or 0.0)
        except (ValueError, TypeError):
            per_model_parsed[f"{short}_sentiment_confidence"] = 0.0

        topic = jd.get('fintech_topic')
        if topic and str(topic).strip().lower() not in ('null', 'none', ''):
            topics.append(str(topic))

        # v7: innovation_locus (原 fintech_category, Gomber, Koch & Siering 2017 Digital Finance Cube technology-application 层; Gomber et al. 2018 JMIS 领域综述背景)
        # fix(omni-g-tonellms-09, 2026-06-11): 创新三维度补模型级 verified 门控 —
        # 仅 verified=True 模型的标签入票 (镜像 sentiment 的 s_votes_verified_only
        # `if v:` 门控, v6/F2 契约), 不再依赖 prompt "false 时填 null" 的软约束
        # (模型违规即漏)。per-model 存档列不门控 (审计保留原始输出)。
        llm_cat = jd.get('innovation_locus')
        if llm_cat:
            cat_str = str(llm_cat).strip().replace('；', ';')
            for part in cat_str.split(';'):
                part = part.strip()
                if part in ('底层技术', '应用场景'):
                    if v:
                        innov_loci.append(part)
                    # Plan v1.37 P2 §5.3.1 Step A: 用 canonical 接受值
                    # 覆写逐模型 default-None 标签。
                    per_model_parsed[f"{short}_innovation_locus"] = part
                    break

        # v3.0.0 (v8): innovation_substantiveness 翻译层已废除, panel 列值即 LLM 原始输出
        # (Westphal & Zajac 1994/1998 ASQ substantive-symbolic 框架). 列后缀 _sub / _symb.
        llm_tt = jd.get('innovation_substantiveness')
        if llm_tt:
            tt_str = str(llm_tt).strip()
            if tt_str in ('实质性', '象征性'):
                if v:  # fix(omni-g-tonellms-09): verified 门控, 同上
                    innov_substs.append(tt_str)
                # Plan v1.37 P2 §5.3.1 Step A: 用 canonical 接受值
                # 覆写逐模型 default-None 标签。
                per_model_parsed[f"{short}_innovation_substantiveness"] = tt_str

        # v3.4.0: innovation_collab_mode (Chesbrough 2003 Open Innovation + L&S 2006 SMJ
        # search breadth & depth; additive supplementation 第三维度, v7 双维语义不变).
        # 列后缀 _indep (自主研发) / _collab (外部协同), Stata byte 编码 0=自主研发 / 1=外部协同.
        llm_cm = jd.get('innovation_collab_mode')
        if llm_cm:
            cm_str = str(llm_cm).strip()
            if cm_str in ('自主研发', '外部协同'):
                if v:  # fix(omni-g-tonellms-09): verified 门控, 同上
                    innov_collab_modes.append(cm_str)
                per_model_parsed[f"{short}_innovation_collab_mode"] = cm_str

        # v7: per-model stage 3 confidence (用于 row-level avg 聚合, 对应论文 W&Z 框架信号强度)
        try:
            per_model_parsed[f"{short}_innovation_substantiveness_confidence"] = float(
                jd.get('innovation_substantiveness_confidence', 0.0) or 0.0
            )
        except (ValueError, TypeError):
            per_model_parsed[f"{short}_innovation_substantiveness_confidence"] = 0.0
        try:
            per_model_parsed[f"{short}_innovation_locus_confidence"] = float(
                jd.get('innovation_locus_confidence', 0.0) or 0.0
            )
        except (ValueError, TypeError):
            per_model_parsed[f"{short}_innovation_locus_confidence"] = 0.0
        # v3.4.0: innovation_collab_mode 第三维度置信度
        try:
            per_model_parsed[f"{short}_innovation_collab_mode_confidence"] = float(
                jd.get('innovation_collab_mode_confidence', 0.0) or 0.0
            )
        except (ValueError, TypeError):
            per_model_parsed[f"{short}_innovation_collab_mode_confidence"] = 0.0

    final_v = majority_vote_bool(v_votes)

    # v6/F2 + 用户决策 (2026-06-23): 仅在通过 verification 的模型子集上计算情感多数票。
    if final_v:
        # 用户决策 (2026-06-23): verified 轨情感**平局/空票一律保守降级为"中性", 不产 None**
        # —— promote 既有 'neutral' 稳健性策略到生产 (与创新三维 tie_default 象征性/应用场景/
        # 自主研发 同款 conservative MAP, uniform prior)。**逆转** v6/F2「平局→None 防中性污染」
        # (该决策曾诊断 81.7%(_full)/84.1%(_ctx) 中性源自污染; 用户已知情并明确选择保守降级,
        # 接受这些 verified 文章以 is_neutral=1 进面板)。范围铁律 = **仅 verified 轨**
        # (final_v=True):
        #   · 平局 → 中性 ('neutral' 策略即 conservative + tie_default='中性');
        #   · 空票 (无任一可解析情感票) → 'neutral' 经 majority_vote_categorical 仍回
        #     empty_fallback=None, 故下方显式补降级为中性, 彻底兑现"verified 轨不产 None"。
        # final_s 非 None ⟹ 下游 llm_undefined_* 恒 0、is_neutral_* 正常编码、
        # agree_rate_s / avg_prob_score 取自然值 (平局→中性时 agree_s=投中性票占比、prob≈0,
        # 整行内部自洽)。函数 majority_vote_sentiment 默认仍为 'undefined' (保留作稳健性/单测)。
        final_s = majority_vote_sentiment(s_votes_verified_only, tie_strategy='neutral')
        if final_s is None:
            final_s = '中性'
    else:
        # Case B: 整篇被多数判为非金融科技 → 情感无意义, **保持 None** (N/A, 非"未定";
        # 用户决策范围明确排除本轨 — 不给判为非金科的文章注入伪中性。下游 encode 经
        # verified=False 掩码置 NaN, panel 不计入)。
        final_s = None

    # fix(omni-g-tonellms-09, 2026-06-11): 文章级 final_v 门控 (标签层, 镜像
    # 上方 final_s=None) — 整文被 ensemble 多数判非 fintech 时, 创新三维度
    # (locus/subst/collab) 标签票与 fintech_topic 关键词证据同步清空, 下游
    # 标签解析 (main 的 _resolve_locus_track / majority_vote_categorical
    # empty_fallback) 对空票得 None, 未验证文章不再获得 innovation_* 标签;
    # per-model 存档列 ({short}_innovation_*) 不受影响 (审计保留原始输出)。
    if not final_v:
        topics = []
        innov_loci = []
        innov_substs = []
        innov_collab_modes = []

    n_valid_votes = len(v_votes)
    n_verifying_votes = sum(1 for v in v_votes if v == final_v) if final_v else 0
    agree_v_count = sum(1 for x in v_votes if x == final_v)
    agree_rate_v = agree_v_count / n_valid_votes if n_valid_votes > 0 else 0.0
    if s_votes_verified_only and final_s is not None:
        agree_rate_s = sum(1 for x in s_votes_verified_only if x == final_s) / len(s_votes_verified_only)
    else:
        agree_rate_s = float('nan')

    call_failure = 1 if n_valid_votes == 0 else 0
    # 用户决策 (2026-06-23) 后: final_v=True ⟹ final_s 永不 None (平局/空票→保守"中性"),
    # 故本式对 verified 轨**结构性恒 0**; final_v=False 时被 `final_v and` 短路同样得 0。
    # ⇒ llm_undefined_* 列现全 0 (保留供 schema 稳定 + encode 掩码兼容)。保留防御式写法:
    # 万一未来 final_s 在 final_v=True 下意外为 None, 仍会被如实标记为 undefined。
    undefined = 1 if (final_v and final_s is None) else 0

    prob_scores = []
    # Plan v1.37 P2 §5.3.1 Step B: 逐模型 binary prob_score —
    # substantiveness (positive_class="象征性") / locus
    # (positive_class="应用场景") / v3.4.0 collab_mode
    # (positive_class="外部协同")。positive_class 选取与
    # stata_export.py value_labels 对齐 (1=对照 / 1=象征性 / 1=应用场景 / 1=外部协同)。
    subst_prob_scores = []
    locus_prob_scores = []
    collab_prob_scores = []
    import numpy as _np  # 局部 import, 避免顶层依赖冲突
    for m in models:
        short = m['short_name']
        s_label = per_model_parsed.get(f"{short}_sentiment")
        s_conf = per_model_parsed.get(f"{short}_sentiment_confidence", 0.0)
        if s_label is not None:
            ps_result = compute_prob_score(s_label, s_conf)
            per_model_parsed[f"{short}_prob_score"] = ps_result['prob_score']
            per_model_parsed[f"{short}_prob_source"] = ps_result['prob_source']
            # fix(tonellms-prob-score, metric-audit 2026-06-10 升级 P1): 仅 verified=True 模型
            # 计入 avg_prob_score —— 镜像离散投票 s_votes_verified_only 的 `if v:` 门控
            # (v6/F2 契约), 使连续稳健/falsification 主 DV (avg_prob_score) 与离散主 DV
            # (final_s) 算在**同一模型子集**上, 修复二者子集不一致对 falsification 的结构性破坏
            # (盘实测 28.9% 情感票来自 verified=False 模型)。{short}_prob_score 仍逐模型存档供
            # 审计; 仅聚合的 prob_scores 列表收紧。$0 (暖缓存) 但变 panel 值 → 落盘待 production
            # run (stage 21 piecemeal 重跑注入行噪声, 见 memory stage21-determinism-anchor)。
            # fix(omni-g-tonellms-07, 2026-06-11): P3_INV (无效 confidence 域) 的
            # NaN 分数不入聚合均值 (镜像下方 binary 轨的 isnan 守卫)。
            if (per_model_parsed.get(f"{short}_verified") is True
                    and not _np.isnan(ps_result['prob_score'])):
                prob_scores.append(ps_result['prob_score'])
        # fix(omni-g-tonellms-09, 2026-06-11): 三维度 binary prob_score 聚合补
        # verified 门控 (镜像上方 sentiment prob_scores 的 verified-only 门控) —
        # 未验证模型的分数仍逐模型存档 ({short}_*_prob_score), 仅聚合列表收紧。
        _model_verified = per_model_parsed.get(f"{short}_verified") is True
        # Binary prob_score for substantiveness
        subst_label = per_model_parsed.get(f"{short}_innovation_substantiveness")
        subst_conf = per_model_parsed.get(f"{short}_innovation_substantiveness_confidence", 0.0)
        subst_bin = compute_prob_score_binary(subst_label, subst_conf, "象征性")
        per_model_parsed[f"{short}_subst_prob_score"] = subst_bin["prob_score"]
        per_model_parsed[f"{short}_subst_prob_source"] = subst_bin["prob_source"]
        if _model_verified and not _np.isnan(subst_bin["prob_score"]):
            subst_prob_scores.append(subst_bin["prob_score"])
        # Binary prob_score for locus
        locus_label = per_model_parsed.get(f"{short}_innovation_locus")
        locus_conf = per_model_parsed.get(f"{short}_innovation_locus_confidence", 0.0)
        locus_bin = compute_prob_score_binary(locus_label, locus_conf, "应用场景")
        per_model_parsed[f"{short}_locus_prob_score"] = locus_bin["prob_score"]
        per_model_parsed[f"{short}_locus_prob_source"] = locus_bin["prob_source"]
        if _model_verified and not _np.isnan(locus_bin["prob_score"]):
            locus_prob_scores.append(locus_bin["prob_score"])
        # v3.4.0: Binary prob_score for collab_mode (positive_class="外部协同")
        collab_label = per_model_parsed.get(f"{short}_innovation_collab_mode")
        collab_conf = per_model_parsed.get(f"{short}_innovation_collab_mode_confidence", 0.0)
        collab_bin = compute_prob_score_binary(collab_label, collab_conf, "外部协同")
        per_model_parsed[f"{short}_collab_prob_score"] = collab_bin["prob_score"]
        per_model_parsed[f"{short}_collab_prob_source"] = collab_bin["prob_source"]
        if _model_verified and not _np.isnan(collab_bin["prob_score"]):
            collab_prob_scores.append(collab_bin["prob_score"])

    avg_prob_score = sum(prob_scores) / len(prob_scores) if prob_scores else float('nan')
    # fix(tonellms-probgate-articlelevel, review-closure 2026-06-10 PROBGATE-1) + 用户决策更新
    # (2026-06-23): 连续 DV avg_prob_score 须与离散 DV final_s 在同一观测子集。
    # final_s is None 现**仅** = Case B (final_v=False, 整文被多数判非 fintech) — 此时连续 DV
    # 同步置 nan (杜绝"多数拒但少数 verified 模型仍投情感"的泄漏)。verified 轨平局已保守降级
    # 为"中性"(final_s 非 None), 其 avg_prob_score = 各 verified 模型 prob 均值 (正/负平局≈0,
    # 与中性自洽), 不再 nan ⇒ 离散/连续仍同子集。**可忽略例外**: verified 但**空票**(零可解析
    # 情感票) 时 final_s 显式=中性 而 prob_scores 为空 ⟹ avg_prob_score 经上方 line 已是 nan;
    # 此极罕见态 (verified 却无任一模型给情感) 下离散=中性/连续=nan 轻微不同子集, 可接受
    # (连续 DV 无数据时诚实置 nan)。
    if final_s is None:
        avg_prob_score = float('nan')
    avg_subst_prob_score = (sum(subst_prob_scores) / len(subst_prob_scores)
                            if subst_prob_scores else float('nan'))
    avg_locus_prob_score = (sum(locus_prob_scores) / len(locus_prob_scores)
                            if locus_prob_scores else float('nan'))
    avg_collab_prob_score = (sum(collab_prob_scores) / len(collab_prob_scores)
                             if collab_prob_scores else float('nan'))
    # fix(omni-g-tonellms-09, 2026-06-11): 文章级 final_v 门控 (镜像 PROBGATE-1
    # 的 final_s→avg_prob_score 同步置 nan) — 整文被多数判非 fintech 时, 创新
    # 三维度连续分数同步 NaN, 不让少数 verified 模型的判定泄入 panel。
    if not final_v:
        avg_subst_prob_score = float('nan')
        avg_locus_prob_score = float('nan')
        avg_collab_prob_score = float('nan')

    return (
        final_v, final_s,
        agree_rate_v, agree_rate_s,
        n_valid_votes, n_verifying_votes,
        call_failure, undefined,
        per_model_parsed, topics, innov_loci, innov_substs,
        n_failures, avg_prob_score,
        avg_subst_prob_score, avg_locus_prob_score,
        innov_collab_modes, avg_collab_prob_score,
    )


def _materialize_content_ctx(df: pd.DataFrame) -> pd.DataFrame:
    """预计算并物化 content_full / content_ctx 列，供 full/ctx 轨分析和下游阶段复用。

    对每个 (文章, 目标银行) 对调用 extract_entity_context() 提取
    实体特异性上下文片段，结果存入 'content_ctx' 列。下游阶段
    22_tone_words 和 23_tone_berts 直接读取此列，避免重复计算
    并确保多种情感分析方法对完全一致的文本进行分析。

    ⚠ 第三轨 ss (content_ss, 银行+金科同句共现) 的单一事实源是 **stage 13**
    (ctx_materializer.materialize_content_ctx), 本备援路径**不产** content_ss —
    仅在跳过 stage 13 的非标准跑触发, 此时 iter_article_track_prompts 对缺失的
    content_ss 优雅回退 content_full (ss 轨退化为 full 轨)。标准 DAG 由 stage 13
    在前物化三轨, 本备援不触发, 故无需在此重复 ss 抽取逻辑。

    窗口参数从 config/filtering.yaml 的 context_window 节读取 (经
    load_config 合并; legacy 单文件 config.yaml 仅为 stub)，确保参数
    可追溯性和审计透明度：
      - sentence_radius: 句子级窗口半径（默认 1 = 命中句前后各1句）
      - fallback_char_radius: 文本过短时的字符级回退半径

    学术依据:
      Hassan et al. (2019, QJE) Proximity-based Attribution。
      敏感性检验: 65_radius_sensitivity.py 验证 radius ∈ {0,1,2,3} 的稳健性。

    fix(omni-g-tonellms-14, 2026-06-11): 备援路径与 stage 13
    (ctx_materializer.materialize_content_ctx) 语义对齐 — content_ctx 同样经
    prepend_title 注入标题, 并补产 content_full (= 标题 + 正文) 列, 兑现
    "双路径必须产同名同语义列" 不变量 (此前备援不 prepend 也不产 content_full,
    跳过 stage 13 时下游 22/23/herd_decay 等 ctx/full 消费者一含标题一不含)。
    Stage 21 自身 prompt 不受影响: iter_article_track_prompts 经
    _strip_prepended_title 按文本前缀剥离, 两路径产出逐字相同 prompt → 缓存键
    不变 (经函数复合验证)。ctx_is_fallback 判定改为比较去标题 body (与
    ctx_materializer 同口径)。残留差异 (诚实披露): 本备援的实体匹配仍未套用
    stage 11 否定/短名排除配置 (stage 13 已套用, 见 fix omni-g-entity-03/16);
    标准 DAG 跑 stage 13 在前, 本备援仅在跳过 stage 13 的非标准跑触发。

    Args:
        df: 含 '内容' / '标题' / 'target_bank' 列的 DataFrame。

    Returns:
        pd.DataFrame: 增加了 'content_full' / 'content_ctx' / 'ctx_is_fallback'
        列的 DataFrame。
    """
    # 从 config (split: filtering.yaml) 读取窗口参数（显式参数化，取代函数默认值）
    _ctx_cfg = CONFIG.get('context_window', {})
    _sentence_radius = _ctx_cfg.get('sentence_radius', 1)
    _fallback_char_radius = _ctx_cfg.get('fallback_char_radius', 150)

    logger.info(f"物化 content_full + content_ctx 列（实体特异性上下文提取 + 标题注入）"
                f"— sentence_radius={_sentence_radius}, "
                f"fallback_char_radius={_fallback_char_radius}")
    _bnf = CONFIG['paths'].get('bank_names_file', '')
    _alias_cache = {}

    # fix(omni-g-tonellms-14, 2026-06-11): 与 ctx_materializer 同语义 —
    # legacy (full/ctx) 示例 — 本备援路径仅产 full/ctx 两路文本, content_ss
    # 由 stage 13 ctx_materializer 物化 (非此备援), 故此处不补 ss 轨 (# no-ss-track)。
    # full/ctx 两路文本均经 prepend_title 注入标题; 缺失标题 (NaN/None) 按空标题处理
    # (与 ctx_materializer fix omni-g-misc-04 口径一致)。
    from news_process.core.text.entity_context import prepend_title

    full_list = []       # full 轨: 标题 + 正文
    ctx_list = []        # ctx 轨: 标题 + 实体窗口 (或 fallback)
    ctx_body_list = []   # ctx 的纯 body 部分 (无标题前缀), 仅用于 fallback 判定
    for _, row in df.iterrows():
        body_full = str(row.get('内容', ''))
        _t = row.get('标题', '')
        title = '' if pd.isna(_t) else str(_t)
        target_bank = str(row.get('target_bank', ''))

        # 防御性检查：当 target_bank 为 NaN 时 str() 会产出 'nan'，
        # 需将其视为空值以避免冗余的别名查找和文件读取
        if target_bank and target_bank not in ('nan', 'None'):
            if target_bank not in _alias_cache:
                _alias_cache[target_bank] = get_target_aliases(target_bank, _bnf)
            ctx_body = extract_entity_context(
                body_full, _alias_cache[target_bank],
                sentence_radius=_sentence_radius,
                fallback_char_radius=_fallback_char_radius,
            )
            if not ctx_body:
                ctx_body = body_full  # 回退公理：无匹配时保留全文
        else:
            ctx_body = body_full  # 无目标银行时回退至全文

        ctx_body_list.append(ctx_body)
        full_list.append(prepend_title(title, body_full))
        ctx_list.append(prepend_title(title, ctx_body))

    df['content_full'] = full_list
    df['content_ctx'] = ctx_list
    # v3.7.2 R8-H1 全管道延伸: 与 ctx_materializer.py 同源 (R8 audit 锚定)
    # 双路径必须产同名同语义列, 防止"跳过 stage 13 直接跑 stage 21"导致列缺失
    # fix(omni-g-tonellms-14): full/ctx 两路均含标题后, fallback 判定改比较去标题
    # body (ctx_body vs 全文 body), 与 ctx_materializer.py 的判定口径一致。  # no-ss-track
    _bodies = df['内容'].astype(str).tolist()
    df['ctx_is_fallback'] = pd.Series(
        [cb == fb for cb, fb in zip(ctx_body_list, _bodies)],
        index=df.index,
    ).astype('bool')
    n_fallback = sum(1 for cb, fb in zip(ctx_body_list, _bodies) if cb == fb)
    assert int(df['ctx_is_fallback'].sum()) == n_fallback, \
        "ctx_is_fallback 列计数与 batch 统计不一致 (stage 21 fallback path)"
    # 统计逻辑与 L404 的 NaN 防御保持一致：排除 'nan'/'None'/空字符串
    _bank_strs = df['target_bank'].astype(str).str.strip()
    n_with_bank = ((_bank_strs != '') & (_bank_strs != 'nan') & (_bank_strs != 'None')).sum()
    logger.info(f"  content_ctx 列物化完成: {len(df):,d} 行, "
                f"回退至全文: {n_fallback:,d}/{n_with_bank:,d} 条"
                f"（{pct4(n_fallback / max(n_with_bank, 1))}）")
    logger.info(f"  ctx_is_fallback 列已写入 (bool, fallback path): "
                f"{int(df['ctx_is_fallback'].sum()):,d}/{len(df):,d} True")
    return df


def _write_run_lineage(stage_start: float):
    """v6/N8: 写入本次 stage 21 运行的 LLM 配置 lineage 清单。

    解决"换模型不留痕"问题：每次重跑覆盖写入固定文件名 21_tone_llms_lineage.json，
    持久化记录 (slot, model_name, base_url, run_start_ts) 三元组。
    文件名不再带时间戳 (避免每次重跑堆积新文件)；本次运行时间已记录在
    run_start_iso / run_start_ts 字段内, 只保留最新一次运行的快照。
    """
    lineage = {
        "stage": STAGE_NAME,
        "run_start_iso": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(stage_start)),
        "run_start_ts": stage_start,
        "models": [
            {
                "short_name": m.get("short_name"),
                "model_name": m.get("model_name"),
                "description": m.get("description"),
                "base_url": m.get("base_url"),
            }
            for m in MODELS
        ],
        "concurrency": MAX_CONCURRENCY,
        "max_retries": MAX_RETRIES,
        "retry_delay": RETRY_DELAY,
        "retry_backoff": "flat",  # 2026-06-26 全项目统一固定间隔, 不再指数退避
        "temperature": TEMPERATURE,
        "random_seed": RANDOM_SEED,
        "force_json": FORCE_JSON,
        "logit_to_score_enabled": LOGIT_SCORE_ENABLED,
    }
    out_dir = CONFIG["paths"]["output_dir"]
    # 固定文件名 → 每次重跑覆盖旧文件, 只保留最新一次运行的 lineage 快照
    # (原 21_tone_llms_lineage_<ts>.json 带时间戳会无限堆积; run_start_ts 字段内已留痕).
    out_path = os.path.join(out_dir, "21_tone_llms_lineage.json")
    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(lineage, f, ensure_ascii=False, indent=2)
        logger.info(f"  [N8 lineage] 已写入: {out_path}")
    except Exception as e:
        logger.warning(f"  [N8 lineage] 写入失败 (非阻塞): {e}")


# ── 创新三维构念出处 (VERIFIED_REFERENCES 注册表; 逐字照抄 APA-7 + DOI, 仅日志用) ──
# 把下游 P3/P4/P5 三篇论文主因变量(实质性/创新位点/协同模式)的二元构念出处 emit
# 进运行期日志 (main() 块 ⑥ 标签分布旁), 让 21_tone_llms.log 自证测度的理论锚点,
# 而非只把出处留在 docstring 注释里。键 = 面板列基名 (innovation_*), 便于在分布
# 日志循环里按维度直接索引。镜像 pipeline/panel/geography.py::_GEO_REFERENCES 的
# house idiom (模块级 verbatim 注册表 + logger.info(f"  📖 {...}") 运行期 emit)。
_INNOV_CONSTRUCT_REFERENCES = {
    # 实质性 (substantiveness, P3): 实质 vs 象征二分的原始构念 — 白话: 一项金科举措
    # 是真投入(改流程/上系统/真砸钱)还是只挂个名作姿态, 正对应 W&Z 的"实质 vs 象征"区分。
    "innovation_substantiveness": (
        "Westphal, J. D., & Zajac, E. J. (1994). Substance and symbolism in "
        "CEOs' long-term incentive plans. Administrative Science Quarterly, "
        "39(3), 367–390. https://doi.org/10.2307/2393295"
    ),
    # 创新位点 (locus, P4): 底层技术 vs 应用场景二分 — 白话: 这条金科新闻讲的是银行
    # 在搭底层技术(算法/架构/中台)还是在落地某个应用(某 App/某业务场景), 即 Gomber
    # 等"数字金融立方体"按技术层 vs 业务功能层的切分。
    "innovation_locus": (
        "Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital finance and "
        "FinTech: Current research and future research directions. Journal of "
        "Business Economics, 87(5), 537–580. https://doi.org/10.1007/s11573-017-0852-x"
    ),
    # 协同模式 (collab, P5): 自主研发 vs 外部协同二分 — 白话: 银行是自己闷头做还是
    # 拉外部伙伴(科技公司/平台)一起做金科, 对应开放式创新的"外部搜索广度"。Chesbrough
    # 2003 是书无 DOI 不可引, 此处锚到其可核验 DOI 的实证半边 Laursen & Salter (2006)。
    "innovation_collab_mode": (
        "Laursen, K., & Salter, A. (2006). Open for innovation: The role of "
        "openness in explaining innovation performance among U.K. manufacturing "
        "firms. Strategic Management Journal, 27(2), 131–150. "
        "https://doi.org/10.1002/smj.507"
    ),
}


def _log_environment_and_methodology(input_path: str) -> None:
    """打印项目/环境信息 + 运行配置 + 方法论依据 (含 DOI) — 日志富集 (2026-06-24)。

    把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数、核心方法的学术出处"
    一次性落进 logs/21_tone_llms.log, 达到顶刊审计标准 (gold = tone_words.py)。
    **纯日志, 不改任何产物 / schema / 控制流 / 缓存键 (golden-safe)**; 整体 try/except
    包裹, 任何日志诊断异常绝不拖垮阶段。所有非整数数字经 sig4/pct4 渲染 (4 位有效数字)。

    ⚠ 必须由 main() 在运行期调用 (绝不在模块顶层 emit) — import 期 emit 会触发
    setup_logging(delay=True) 首写截断, 把生产 stage 21 日志覆盖 (历史事故, 见 :202 注)。
    """
    try:
        out_dir = CONFIG["paths"]["output_dir"]
        cache_db = os.path.join(out_dir, "_llm_cache.db")
        out_full = os.path.join(
            out_dir,
            CONFIG.get("filenames", {}).get("output_21_tone_llms_full", "21_tone_llms_full.parquet"),
        )
        out_main = os.path.join(
            out_dir,
            CONFIG.get("filenames", {}).get("output_21_tone_llms", "21_tone_llms.parquet"),
        )

        logger.info("  🧭 项目 / 环境信息")
        logger.info(
            f"     · 阶段: {STAGE_NAME} (统一 LLM 语义精筛与情感分析, STAGES_MAIN; "
            "三轨 full/ctx/ss; 全流水线唯一核心付费阶段)"
        )
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板); 版本 v3.11.1")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get("NEWS_PROCESS_RUN_ID")
        logger.info(
            f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
            f"OFFLINE 离线确定性守卫={'ON (缓存 miss→raise, 零网络/$0)' if LLM_OFFLINE else 'OFF (在线模式, 缓存 miss 会付费调 API)'}"
        )
        logger.info(
            "     · 确定性/成本: 命中 _llm_cache.db 即 $0 字节级复现; 缓存键=模型名+prompt 文本"
            f"+prompt_version({PROMPT_VERSION})+temperature({sig4(TEMPERATURE)}) (temperature=0 下 seed 不进键)。"
        )

        logger.info("  📂 输入 / 输出文件 (config/paths.yaml::output_dir + filenames)")
        logger.info(f"     · 输入:     {input_path} (stage 14 fintech_intensity, 硬依赖)")
        logger.info(f"     · 缓存:     {cache_db} (确定性锚点, 勿删铁律)")
        logger.info(f"     · 输出全量: {out_full} (含 verified True/False, 供验证模块)")
        logger.info(f"     · 输出主表: {out_main} (verified_full 全文轨过滤 full-only, 下游 stage 22/24/45 消费)")

        logger.info("  ⚙ 运行配置 (config/sentiment.yaml::tone_llm_processing)")
        logger.info(
            f"     · LLM 推理: temperature={sig4(TEMPERATURE)} | seed={RANDOM_SEED:,d} | "
            f"force_json={FORCE_JSON} | models={len(MODELS):,d} 家族 | 并发 MAX_CONCURRENCY={MAX_CONCURRENCY:,d}"
        )
        logger.info(
            f"     · 模型清单: {[m.get('short_name') for m in MODELS]} "
            "(gpt54nano/gemini31/deepseekv4; Prompt v8 字节冻结)"
        )
        logger.info(
            f"     · 重试: max_retries={MAX_RETRIES:,d} (API 失败统一 80 次) | "
            f"retry_delay={sig4(RETRY_DELAY)}s 固定间隔 (flat, 2026-06-26 全项目统一, 不再指数退避)"
        )
        logger.info(
            f"     · 平局重试: sentiment_tie_retry_rounds={SENTIMENT_TIE_RETRY_ROUNDS:,d} "
            "(verified 轨情感平局/空票保守降级前先逐轮 barrier 绕缓存重调实时 API; ≤0 关闭; 仅在线模式)"
        )
        logger.info(
            f"     · 超时: total={sig4(REQUEST_TIMEOUT_TOTAL)}s | connect={sig4(REQUEST_TIMEOUT_CONNECT)}s | "
            f"sock_read={sig4(REQUEST_TIMEOUT_SOCK_READ)}s"
        )
        logger.info(f"     · Logit-to-Score 概率映射: enabled={LOGIT_SCORE_ENABLED} (logit→[-1,+1] 连续分稳健性指标)")

        # 📖 方法论依据 (核心方法/构念学术出处 emit 进日志; 逐字取自经核验参考文献注册表) ──
        logger.info("  📖 方法论依据 (Author (Year). Journal, vol(issue), pages. DOI)")
        logger.info(
            "     · 多模型投票共识 (self-consistency): Wang, X., Wei, J., Schuurmans, D., Le, Q., Chi, E., "
            "Narang, S., Chowdhery, A., & Zhou, D. (2022). Self-consistency improves chain of thought "
            "reasoning in language models. arXiv. https://doi.org/10.48550/arXiv.2203.11171"
        )
        logger.info(
            "       → 三模型各跑思维链后取多数票, 替代单模型采样, 提升判定稳健性。"
        )
        logger.info(
            "     · 三角验证 (triangulation): Denzin, N. K. (2017). The research act: A theoretical "
            "introduction to sociological methods. Routledge. https://doi.org/10.4324/9781315134543"
        )
        logger.info(
            "       → 三轨(全文/邻近句/同句)× 三模型多源交叉, 满足顶刊三角验证标准。"
        )
        logger.info(
            "     · LLM 文本标注可复现性 / temperature=0 锚点: Lopez-Lira, A., & Tang, Y. (2023). "
            "Can ChatGPT forecast stock price movements? Return predictability and large language "
            "models. SSRN Electronic Journal. https://doi.org/10.2139/ssrn.4412788"
        )
        logger.info(
            "       → temperature=0 确定性推理 + 缓存锚点, 保证情感标签可 $0 复现。"
        )
        logger.info(
            "     · LLM 优于众包标注 (annotation quality): Gilardi, F., Alizadeh, M., & Kubli, M. (2023). "
            "ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National "
            "Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120"
        )
        logger.info(
            "       → 支撑以 LLM 取代人工逐篇标注金融新闻语气/真伪的方法选择。"
        )
        logger.info(
            "     · logit-to-score 连续分映射 (置信加权): Törnberg, P. (2023). How to use LLMs for "
            "text analysis. arXiv. https://doi.org/10.48550/arXiv.2307.13106; "
            "Shapiro, A. H., Sudhof, M., & Wilson, D. J. (2022). Measuring news sentiment. Journal "
            "of Econometrics, 228(2), 221-243. https://doi.org/10.1016/j.jeconom.2020.07.053"
        )
        logger.info(
            "       → 把(三分类标签 × 置信度)映射到 [-1,+1] 连续语气分, 作词典法之外的稳健性度量。"
        )
        logger.info(
            "     · 不确定性表达 / 置信度引出: Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & "
            "Hooi, B. (2023). Can LLMs express their uncertainty? An empirical evaluation of confidence "
            "elicitation in LLMs. arXiv. https://doi.org/10.48550/arXiv.2306.13063"
        )
        logger.info(
            "     · 最大熵/信息论 (类先验保守降级理据): Jaynes, E. T. (1957). Information theory and "
            "statistical mechanics. Physical Review, 106(4), 620-630. https://doi.org/10.1103/PhysRev.106.620"
        )
        logger.info(
            "     · LLM 文本测度最佳实践 (temperature=0 / prompt 冻结 / 缓存确定性): de Kok, T. (2025). "
            "ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management "
            "Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253"
        )
        logger.info(
            "       → 顶刊会计/金融 LLM 文本测度规范, 锚定本阶段 temperature=0 + Prompt v8 字节冻结 + "
            "_llm_cache.db 确定性复现的设计纪律。"
        )
        logger.info(
            "     · 前视偏误检验 (lookahead / 复现性威胁): Gao, Z., Jiang, W., & Yan, Y. (2026). "
            "A test of lookahead bias in LLM forecasts (SSRN Working Paper No. 5985277; arXiv:2512.23847). "
            "https://doi.org/10.2139/ssrn.5985277"
        )
        logger.info(
            "       → 直接锚定本阶段 _llm_cache.db 离线确定性守卫 (NEWS_PROCESS_LLM_OFFLINE=1) 的动因: "
            "用缓存固定历史响应以杜绝模型版本漂移/前视污染, 保证 golden 字节级可复现。"
        )
        logger.info(
            "     · LLM 记忆/数据污染 (验证门动因): Lopez-Lira, A., Tang, Y., & Zhu, M. (2025). "
            "The memorization problem: Can we trust LLMs' economic forecasts? (SSRN Working Paper "
            "No. 5217505; arXiv:2504.14765). https://doi.org/10.2139/ssrn.5217505"
        )
        logger.info(
            "       → 锚定本阶段缓存键四维 (模型名+prompt 文本+prompt_version+temperature) 与严格响应"
            "校验 (_is_cacheable_llm_response) 的必要性: 防止 LLM 记忆/泄漏污染情感标注。"
        )
        logger.info(
            "     · LLM 作计量框架 (生成式回归元/generated regressor): Ludwig, J., Mullainathan, S., & "
            "Rambachan, A. (2025). Large language models: An applied econometric framework (NBER "
            "Working Paper No. 33344). National Bureau of Economic Research. https://doi.org/10.3386/w33344"
        )
        logger.info(
            "       → 框定本阶段角色: 三模型投票产出的 verified/sentiment/创新三维标签是下游面板的"
            "'生成式回归元', 须按 LLM 计量框架审慎对待其测量误差与下游推断有效性。"
        )
        logger.info(
            "     · LLM 数据标注基础指南 / 误分类偏置与 prompt 敏感性: Carlson, N. A., & Burbano, V. (2026). "
            "The use of LLMs to annotate data in management research: Foundational guidelines and warnings. "
            "Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023"
        )
        logger.info(
            "       → 把 LLM 当标注器须报告并锚定 temperature / prompt 版本、警惕误分类偏置与 prompt 敏感性 "
            "(本阶段 prompt_version + 三模型投票 + 缓存键四维即此纪律的工程化)。"
        )
        logger.info(
            "     · 生成式 AI 作金融研究测度工具 (领域综述): Eisfeldt, A. L., & Schubert, G. (2025). "
            "Generative AI and finance. Annual Review of Financial Economics, 17(1), 363-393. "
            "https://doi.org/10.1146/annurev-financial-112923-020503"
        )
        logger.info(
            "       → 领域级引用锚: 以生成式 AI 从非结构化金融新闻抽取结构化语气/创新属性变量。"
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法论信息打印失败 (不影响处理): {e}")


def main():
    """Stage 21 LLM 三模型 ensemble 情感分析主入口.

    .. todo:: v3.0-split (Plan-r3 P1-7 锚点, god function)

        本函数是 stage 21 的三轨 (full + ctx + ss) LLM 调用主流程, 内部职责:
        1. 加载 stage 12/14 上游 + schema 守护 (含 ``stage 14 fallback to 12``
           硬化反模式根除, 见下方 "Step 4(a) 硬化" 注释)
        2. 三轨数据准备 + content/ctx/ss 物化 (content_ss 由 stage 13 单一事实源)
        3. 三家族 LLM (gpt54nano / gemini31 / deepseekv4) 并发请求 +
           majority-vote ensemble (logit-to-score)
        4. SQLite 缓存读写 (缓存键含 prompt_version 命名空间, 已实现于 fetch_llm_async)
        5. N8 lineage 记录 + parquet 三轨 (full/ctx/ss) 输出

        v3.0 拆分应让 LLM 调用层独立可测 (mock yunwu API), 与上下游
        IO 解耦.
    """
    stage_start = time.time()
    # ── 【功能】banner (golden 范式; 取自 PIPELINE_NUMBERED_PY_REFERENCE 21 小节; 替换旧短头) ──
    logger.info("=" * 72)
    logger.info(f"阶段 21: 统一 LLM 语义精筛与情感分析 (三轨 full/ctx/ss; prompt {PROMPT_VERSION} 字节冻结)")
    logger.info("=" * 72)
    # 参数回显 (G-06; 自模块级移入, 见 :199/:496 注释 fix(log-round4-2026-06-20)):
    logger.info(f"LLM 推理参数: temperature={sig4(TEMPERATURE)}, seed={RANDOM_SEED}, "
                f"force_json={FORCE_JSON}, models={len(MODELS)}, "
                f"concurrency={MAX_CONCURRENCY}")
    logger.info(f"Logit-to-Score 概率映射: enabled={LOGIT_SCORE_ENABLED}")
    logger.info("【功能】让 3 个 LLM 家族 (相当于 3 位独立金融分析员) 各读同一篇新闻: 先精筛")
    logger.info("        判定是否真在讲'目标银行×金融科技'(verified 把关), 再判语气 正面/负面/中性,")
    logger.info("        顺带给 创新位点(底层/应用)、实质性(实质/象征)、协同模式(自研/外部) 三维标签;")
    logger.info("        三轨各跑一遍并各自 majority-vote, 产 _full/_ctx/_ss 整套列, 是面板'媒体语调'主变量之源。")
    logger.info("【方法】三模型 ensemble 多数决 (>50% 严格多数); sentiment(verified 轨) 平局/空票→保守'中性'(不产未定; 非金科轨 None=N/A),")
    logger.info("        创新三维平局→保守 MAP 降级(象征性/应用场景/自主研发); logit-to-score 把"
                f"(标签×置信度) 映射到 [-1,+1] 连续分 (enabled={LOGIT_SCORE_ENABLED})。")
    logger.info("        verified gate = 仅全文轨 verified_full (full-only; ctx/ss 截断可能漏信息, 故只由全文 3-LLM 多数决定留篇)。")
    logger.info("【判读】verified 率高=语料金科相关度高; 情绪三类占比看方向; 三轨样本各自 just-identified")
    logger.info("        不混同一 Hansen J。Triple-gate 含 full 的 4 态之和 == 输出样本数 (恒等校验); 7 态全和 = 任一轨 verified 的诊断并集。")
    logger.info(f"【确定性】核心付费阶段, 但确定性锚点 = _llm_cache.db (temperature={sig4(TEMPERATURE)}, prompt {PROMPT_VERSION});")
    logger.info(f"          缓存全命中 ⟺ 零 API 调用 ⟺ golden 字节级可复现 (并发 MAX_CONCURRENCY={MAX_CONCURRENCY};"
                + ("  OFFLINE 离线守卫 ON" if LLM_OFFLINE else "  在线模式") + ")。")
    logger.info("=" * 72)
    _write_run_lineage(stage_start)

    # Step 4(a) 硬化 (致命问题 5 / 红队 v6 修订): 删除"14 不存在则回退 12"的
    # 静默 fallback。Stage 14 输出 fintech_intensity_score / intensity_verified
    # 是 LLM 三轨语义筛选的关键信号; fallback 到 12 会让 LLM 失去 TF-IDF 强度
    # 锚点, 静默降级为旧版"无强度筛选"模式, 与 v6 三家族 LLM 设计假设矛盾。
    # 若 stage 14 真的缺失, 必须通过 raise 让 orchestrator 立即停止并修复上游,
    # 而非继续生产含有"未见过的隐性降级"标签的 21_tone_llms.parquet。
    input_14 = CONFIG['filenames'].get('output_14_fintech_intensity', '15_fintech_intensity.parquet')
    path_14 = os.path.join(CONFIG["paths"]["output_dir"], input_14)

    if not os.path.exists(path_14):
        raise RuntimeError(
            f"[stage 21] 上游输入缺失: {path_14} 不存在。"
            f" Stage 21 (LLM 三轨情感分析) 硬依赖 stage 14 输出的 "
            f"fintech_intensity_score 列。请先运行 "
            f"`python -m news_process.pipeline.filtering.fintech_intensity` "
            f"产出 {input_14} 后再重试。"
        )
    input_path = path_14
    logger.info(f"使用阶段14输出: {input_14}")

    # 项目/环境信息 + 运行配置 + 方法论依据 (含 DOI) — 日志富集 2026-06-24, golden-safe
    _log_environment_and_methodology(input_path)

    # 运行期各主要子阶段墙钟耗时累计 (末尾汇总; 纯日志, 不影响产物)
    phase_durations: dict[str, float] = {}

    _t = time.time()
    logger.info(f"加载预筛数据: {input_path}")
    df = pd.read_parquet(input_path)
    logger.info(f"总计候选新闻: {len(df):,d}")
    # 输入边界 provenance (io 富集 2026-06-29, golden-safe 纯日志): 落 shape + 关键
    # 输入列在位情况。⚠ content_ss 缺失会让 ss(银行+金科同句)稳健性轨在
    # iter_article_track_prompts 静默回退 content_full (见 :845-847) → 三轨退化为
    # 双轨, 审稿人须能从日志判断 ss 轨是真同句轨还是 full 的副本。content_ctx 在位
    # 已在下方物化分支记录, 此处补 content_ss 的在位/非空诊断。整体 try/except 包裹,
    # 任何诊断异常绝不拖垮阶段; 计数用 :,d, 非整数经 pct4 (四位有效数字)。
    try:
        _nrow_in, _ncol_in = df.shape
        _key_in_cols = ['内容', 'content_ctx', 'content_ss', 'target_bank', '标题',
                        'fintech_intensity_score']
        _present_in = {c: (c in df.columns) for c in _key_in_cols}
        logger.info(f"  · 输入 DataFrame 形状: {_nrow_in:,d} 行 × {_ncol_in:,d} 列")
        logger.info(
            "  · 关键输入列在位: "
            + ", ".join(f"{c}={'✓' if _present_in[c] else '✗缺失'}" for c in _key_in_cols)
        )
        if not _present_in['content_ss']:
            logger.warning(
                "  ⚠ content_ss 列缺失 → ss(银行+金科同句)稳健性轨将由 "
                "iter_article_track_prompts 回退 content_full (:845-847), ss 轨退化为 "
                "full 副本而非真同句轨; 复现/审稿前须确认 stage 13 已物化 content_ss。"
            )
        else:
            # ss 轨真实性诊断: content_ss 非空率 (ss_is_fallback=True 行回退全文 body, 虽非空
            # 但非真同句窗口); 纯日志, 结果只喂 logger 后丢弃, 不参与任何下游计算。
            _ss_nonempty = int(df['content_ss'].notna().sum())
            logger.info(
                f"  · content_ss 非空 {_ss_nonempty:,d} 行 "
                f"({pct4(_ss_nonempty / _nrow_in) if _nrow_in else 'N/A'}); "
                "ss_is_fallback=True 行虽有值但回退全文 (见 stage 13 物化)。"
            )
    except Exception as _e_io:
        logger.debug(f"  · 输入 provenance 诊断跳过 (非阻塞): {_e_io}")
    log_memory_usage(logger, "数据加载完成")
    phase_durations['①加载+ctx物化'] = time.time() - _t
    
    # 物化 content_ctx 列（供 LLM 三轨请求的 ctx 轨 + 下游阶段 22/23 直接复用）
    # v3.6.0 (Plan E P4 A1): idempotent — 若 stage 13 已物化, 跳过重复计算
    # (避免 stage 13/21 用不同参数算两次 ctx 造成下游 _ctx 列内部不一致)
    # 注: 第三轨 content_ss 的单一事实源是 stage 13 (本备援只兜底 ctx); 缺
    # content_ss 时由 iter_article_track_prompts 回退 content_full (ss→full)。
    if 'content_ctx' in df.columns:
        logger.info("  'content_ctx' 已存在 (v3.6.0 stage 13 上游已物化), 跳过重复物化")
    else:
        df = _materialize_content_ctx(df)
    
    # 初始化 LLM 请求级 SQLite 缓存
    cache_db = os.path.join(CONFIG["paths"]["output_dir"], '_llm_cache.db')
    with LLMCache(cache_db) as cache:
        logger.info(f"LLM 缓存: {cache.size()} 条已缓存, 路径: {cache_db}")

        # 异步并发大模型（三轨 full/ctx/ss）
        logger.info(f"开始分发三轨组合模型处理任务，包含模型: {[m['short_name'] for m in MODELS]}")
        _t = time.time()
        results_map = asyncio.run(run_all_llms(df, MODELS, cache=cache))
        phase_durations['②三轨LLM并发请求'] = time.time() - _t

        # 问题3: 缓存命中统计摘要 — 让确定性可观测。misses=0 & writes=0
        # ⟺ 本次 run 全部命中 _llm_cache.db (无新 API 调用) → golden 字节级
        # 可复现。离线模式下 (NEWS_PROCESS_LLM_OFFLINE=1) miss 会先 raise, 故
        # 此处能打印即代表零 miss。
        _cstats = cache.stats()
        logger.info(
            f"LLM 缓存命中统计: lookups={_cstats['lookups']:,d} hits={_cstats['hits']:,d} "
            f"v0_hits={_cstats['v0_hits']:,d} misses={_cstats['misses']:,d} "
            f"writes={_cstats['writes']:,d} hit_rate={sig4(_cstats['hit_rate'])}"
            + ("  [OFFLINE 确定性模式]" if LLM_OFFLINE else "")
        )

        # 提取与投票（三轨 full/ctx/ss）
        logger.info("开始聚合各模型 JSON 响应并执行三轨多数投票三角验证...")
        _t = time.time()

        llm_verified_full_arr = []
        llm_verified_ctx_arr = []
        llm_verified_ss_arr = []           # ss 轨 (银行+金科同句共现)
        llm_sentiment_full_arr = []
        llm_sentiment_ctx_arr = []
        llm_sentiment_ss_arr = []
        agreement_rate_full_arr = []
        agreement_rate_ctx_arr = []
        agreement_rate_ss_arr = []
        # v6/F2 新增掩码列
        agreement_rate_s_full_arr = []
        agreement_rate_s_ctx_arr = []
        agreement_rate_s_ss_arr = []
        n_valid_votes_full_arr = []
        n_valid_votes_ctx_arr = []
        n_valid_votes_ss_arr = []
        n_verifying_votes_full_arr = []
        n_verifying_votes_ctx_arr = []
        n_verifying_votes_ss_arr = []
        call_failure_full_arr = []
        call_failure_ctx_arr = []
        call_failure_ss_arr = []
        undefined_full_arr = []
        undefined_ctx_arr = []
        undefined_ss_arr = []
        # v3.2.0 双轨化 (plan v14 §3.1 P1) + v3.9.0 三轨化: innovation_locus /
        # substantiveness 各自 full/ctx/ss 独立产出
        innovation_locus_full_arr = []     # Gomber, Koch & Siering 2017 Digital Finance Cube (Gomber et al. 2018 JMIS 背景), full-text classification
        innovation_locus_ctx_arr = []      # Gomber, Koch & Siering 2017 Digital Finance Cube (Gomber et al. 2018 JMIS 背景), entity-context classification (Hassan 2019 QJE)
        innovation_locus_ss_arr = []       # Gomber, Koch & Siering 2017 Digital Finance Cube (Gomber et al. 2018 JMIS 背景), 银行+金科同句共现 classification
        category_confidence_full_arr = []  # LLM × keyword cross-validation, full track
        category_confidence_ctx_arr = []   # LLM × keyword cross-validation, ctx track
        category_confidence_ss_arr = []    # LLM × keyword cross-validation, ss track (同句共现)
        innov_subst_full_arr = []          # W&Z 1994/1998 ASQ, full-text judgment
        innov_subst_ctx_arr = []           # W&Z 1994/1998 ASQ, entity-context judgment
        innov_subst_ss_arr = []            # W&Z 1994/1998 ASQ, 银行+金科同句共现 judgment
        # v3.4.0 第三维度 (Chesbrough 2003 + L&S 2006 SMJ, additive supplementation):
        innov_collab_full_arr = []         # 自主研发 / 外部协同 (full track)
        innov_collab_ctx_arr = []          # 自主研发 / 外部协同 (ctx track)
        innov_collab_ss_arr = []           # 自主研发 / 外部协同 (ss track, 同句共现)
        # v7 (保留): row-level avg confidence per track per dimension (R6-H 下游聚合源)
        innov_subst_conf_full_arr = []
        innov_subst_conf_ctx_arr = []
        innov_subst_conf_ss_arr = []
        innov_locus_conf_full_arr = []
        innov_locus_conf_ctx_arr = []
        innov_locus_conf_ss_arr = []
        # v3.4.0 第三维度 row-level avg confidence
        innov_collab_conf_full_arr = []
        innov_collab_conf_ctx_arr = []
        innov_collab_conf_ss_arr = []

        # 预分配每个模型 × 每轨道的独立判断列表 (三轨 full/ctx/ss)
        per_model_cols = {}
        for m in MODELS:
            short = m['short_name']
            for track in ['_full', '_ctx', '_ss']:  # _ss = 银行+金科同句共现轨
                per_model_cols[f"{short}_verified{track}"] = []
                per_model_cols[f"{short}_sentiment{track}"] = []
                per_model_cols[f"{short}_verification_confidence{track}"] = []
                per_model_cols[f"{short}_sentiment_confidence{track}"] = []
                # per-model 分类维度存档列 (2026-07-03, ROBUSTNESS_GAP_BACKFILL §2 A1):
                # 基名 = _LLM_CLASS_SPEC 键 (subst/locus/collab)。**不门控**审计存档
                # (镜像 {short}_sentiment 先例, 见 _aggregate_track L1684 注释); verified
                # 门控延迟到 encode 层聚合 (encode_sentiment 指示列)。⚠ 与共识列口径差:
                # 共识票池只纳 verified=True 标签且 final_v=False 清票, 存档列保留原始输出。
                for _dim in _LLM_CLASS_SPEC:
                    per_model_cols[f"{short}_{_dim}{track}"] = []
                if LOGIT_SCORE_ENABLED:
                    per_model_cols[f"{short}_prob_score{track}"] = []
                    per_model_cols[f"{short}_prob_source{track}"] = []

        # Logit-to-Score 轨道级数组 (三轨 full/ctx/ss)
        prob_score_full_arr = []
        prob_score_ctx_arr = []
        prob_score_ss_arr = []
        # Plan v1.37 P2: 文章级 binary prob_score 数组
        # (avg_subst_prob_score_{full,ctx,ss} + avg_locus_prob_score_{full,ctx,ss})。
        # v3.4.0: 另加 collab_prob_score 数组 (Chesbrough 2003); v3.9.0 三轨化。
        subst_prob_score_full_arr = []
        subst_prob_score_ctx_arr = []
        subst_prob_score_ss_arr = []
        locus_prob_score_full_arr = []
        locus_prob_score_ctx_arr = []
        locus_prob_score_ss_arr = []
        collab_prob_score_full_arr = []
        collab_prob_score_ctx_arr = []
        collab_prob_score_ss_arr = []

        n_api_failures = 0

        for idx, row in df.iterrows():
            row_results = results_map.get(idx, {'full': {}, 'ctx': {}, 'ss': {}})

            # ── Full 轨道聚合 (v6/F2: 14 元组; plan v1.37 P2: 16 元组; v3.4.0: 18 元组 + collab_mode) ──
            (final_v_full, final_s_full,
             agree_rate_full, agree_rate_s_full,
             n_valid_full, n_verifying_full,
             call_failure_full, undefined_full,
             parsed_full, topics_full, innov_loci_full, innov_substs_full,
             n_fail_full, avg_prob_full,
             avg_subst_prob_full, avg_locus_prob_full,
             innov_collab_modes_full, avg_collab_prob_full) = _aggregate_track(row_results.get('full', {}), MODELS)
            n_api_failures += n_fail_full

            llm_verified_full_arr.append(final_v_full)
            llm_sentiment_full_arr.append(final_s_full)
            agreement_rate_full_arr.append(agree_rate_full)
            agreement_rate_s_full_arr.append(agree_rate_s_full)
            n_valid_votes_full_arr.append(n_valid_full)
            n_verifying_votes_full_arr.append(n_verifying_full)
            call_failure_full_arr.append(call_failure_full)
            undefined_full_arr.append(undefined_full)

            for m in MODELS:
                short = m['short_name']
                per_model_cols[f"{short}_verified_full"].append(parsed_full.get(f"{short}_verified"))
                per_model_cols[f"{short}_sentiment_full"].append(parsed_full.get(f"{short}_sentiment"))
                per_model_cols[f"{short}_verification_confidence_full"].append(parsed_full.get(f"{short}_verification_confidence", 0.0))
                per_model_cols[f"{short}_sentiment_confidence_full"].append(parsed_full.get(f"{short}_sentiment_confidence", 0.0))
                # per-model 分类维度存档 (2026-07-03 §2 A1; ⚠ full/ctx/ss 三块手抄副本须成对改)
                for _dim, _cspec in _LLM_CLASS_SPEC.items():
                    per_model_cols[f"{short}_{_dim}_full"].append(parsed_full.get(f"{short}_{_cspec[2]}"))
                if LOGIT_SCORE_ENABLED:
                    # fix(omni-g-tonellms-12, 2026-06-11): 失败/解析失败模型的逐模型
                    # 存档列 default 从 (0.0, 'P3') 改 (NaN, 'MISSING') — 0.0+'P3'
                    # 与真实零置信中性的 P3 one-hot 同值不可区分 ("失败≠中性",
                    # 镜像 2026-05-29 H1 title 轨语义)。聚合 avg_prob_score 已被
                    # verified-gate 正确排除, 本修仅存档列 (无下游回归消费)。
                    per_model_cols[f"{short}_prob_score_full"].append(parsed_full.get(f"{short}_prob_score", float('nan')))
                    per_model_cols[f"{short}_prob_source_full"].append(parsed_full.get(f"{short}_prob_source", 'MISSING'))
            prob_score_full_arr.append(avg_prob_full)
            subst_prob_score_full_arr.append(avg_subst_prob_full)
            locus_prob_score_full_arr.append(avg_locus_prob_full)
            collab_prob_score_full_arr.append(avg_collab_prob_full)

            # ── Ctx 轨道聚合 (v6/F2: 14 元组; plan v1.37 P2: 16 元组; v3.4.0: 18 元组 + collab_mode) ──
            (final_v_ctx, final_s_ctx,
             agree_rate_ctx, agree_rate_s_ctx,
             n_valid_ctx, n_verifying_ctx,
             call_failure_ctx, undefined_ctx,
             parsed_ctx, topics_ctx, innov_loci_ctx, innov_substs_ctx,
             n_fail_ctx, avg_prob_ctx,
             avg_subst_prob_ctx, avg_locus_prob_ctx,
             innov_collab_modes_ctx, avg_collab_prob_ctx) = _aggregate_track(row_results.get('ctx', {}), MODELS)
            n_api_failures += n_fail_ctx

            llm_verified_ctx_arr.append(final_v_ctx)
            llm_sentiment_ctx_arr.append(final_s_ctx)
            agreement_rate_ctx_arr.append(agree_rate_ctx)
            agreement_rate_s_ctx_arr.append(agree_rate_s_ctx)
            n_valid_votes_ctx_arr.append(n_valid_ctx)
            n_verifying_votes_ctx_arr.append(n_verifying_ctx)
            call_failure_ctx_arr.append(call_failure_ctx)
            undefined_ctx_arr.append(undefined_ctx)

            for m in MODELS:
                short = m['short_name']
                per_model_cols[f"{short}_verified_ctx"].append(parsed_ctx.get(f"{short}_verified"))
                per_model_cols[f"{short}_sentiment_ctx"].append(parsed_ctx.get(f"{short}_sentiment"))
                per_model_cols[f"{short}_verification_confidence_ctx"].append(parsed_ctx.get(f"{short}_verification_confidence", 0.0))
                per_model_cols[f"{short}_sentiment_confidence_ctx"].append(parsed_ctx.get(f"{short}_sentiment_confidence", 0.0))
                # per-model 分类维度存档 (2026-07-03 §2 A1; 三块手抄副本之二, 与 full/ss 成对)
                for _dim, _cspec in _LLM_CLASS_SPEC.items():
                    per_model_cols[f"{short}_{_dim}_ctx"].append(parsed_ctx.get(f"{short}_{_cspec[2]}"))
                if LOGIT_SCORE_ENABLED:
                    # fix(omni-g-tonellms-12, 2026-06-11): 同上 full 轨 — 缺席模型
                    # 存档列 (NaN, 'MISSING'), 与真实 P3 零置信中性可区分。
                    per_model_cols[f"{short}_prob_score_ctx"].append(parsed_ctx.get(f"{short}_prob_score", float('nan')))
                    per_model_cols[f"{short}_prob_source_ctx"].append(parsed_ctx.get(f"{short}_prob_source", 'MISSING'))
            prob_score_ctx_arr.append(avg_prob_ctx)
            subst_prob_score_ctx_arr.append(avg_subst_prob_ctx)
            locus_prob_score_ctx_arr.append(avg_locus_prob_ctx)
            collab_prob_score_ctx_arr.append(avg_collab_prob_ctx)

            # ── SS 轨道聚合 (银行+金科同句共现; _aggregate_track 第三次调用,
            #    与 full/ctx 同 18 元组契约; v3.9.0 三轨化) ──
            (final_v_ss, final_s_ss,
             agree_rate_ss, agree_rate_s_ss,
             n_valid_ss, n_verifying_ss,
             call_failure_ss, undefined_ss,
             parsed_ss, topics_ss, innov_loci_ss, innov_substs_ss,
             n_fail_ss, avg_prob_ss,
             avg_subst_prob_ss, avg_locus_prob_ss,
             innov_collab_modes_ss, avg_collab_prob_ss) = _aggregate_track(row_results.get('ss', {}), MODELS)
            n_api_failures += n_fail_ss

            llm_verified_ss_arr.append(final_v_ss)
            llm_sentiment_ss_arr.append(final_s_ss)
            agreement_rate_ss_arr.append(agree_rate_ss)
            agreement_rate_s_ss_arr.append(agree_rate_s_ss)
            n_valid_votes_ss_arr.append(n_valid_ss)
            n_verifying_votes_ss_arr.append(n_verifying_ss)
            call_failure_ss_arr.append(call_failure_ss)
            undefined_ss_arr.append(undefined_ss)

            for m in MODELS:
                short = m['short_name']
                per_model_cols[f"{short}_verified_ss"].append(parsed_ss.get(f"{short}_verified"))
                per_model_cols[f"{short}_sentiment_ss"].append(parsed_ss.get(f"{short}_sentiment"))
                per_model_cols[f"{short}_verification_confidence_ss"].append(parsed_ss.get(f"{short}_verification_confidence", 0.0))
                per_model_cols[f"{short}_sentiment_confidence_ss"].append(parsed_ss.get(f"{short}_sentiment_confidence", 0.0))
                # per-model 分类维度存档 (2026-07-03 §2 A1; 三块手抄副本之三, 与 full/ctx 成对)
                for _dim, _cspec in _LLM_CLASS_SPEC.items():
                    per_model_cols[f"{short}_{_dim}_ss"].append(parsed_ss.get(f"{short}_{_cspec[2]}"))
                if LOGIT_SCORE_ENABLED:
                    # fix(omni-g-tonellms-12, 2026-06-11): 同上 full/ctx 轨 — 缺席模型
                    # 存档列 (NaN, 'MISSING'), 与真实 P3 零置信中性可区分。
                    per_model_cols[f"{short}_prob_score_ss"].append(parsed_ss.get(f"{short}_prob_score", float('nan')))
                    per_model_cols[f"{short}_prob_source_ss"].append(parsed_ss.get(f"{short}_prob_source", 'MISSING'))
            prob_score_ss_arr.append(avg_prob_ss)
            subst_prob_score_ss_arr.append(avg_subst_prob_ss)
            locus_prob_score_ss_arr.append(avg_locus_prob_ss)
            collab_prob_score_ss_arr.append(avg_collab_prob_ss)

            # ── 金融科技主题标准化分类（v3.2.0 双轨独立 + v3.9.0 三轨 full/ctx/ss，plan v14 §3.1 P1）──
            # 三轨平局策略对称：locus → 应用场景；substantiveness → 象征性（plan v14 §3.1 P1.5）
            # 三轨各自独立运行关键词分类器 (canonicalize_topic) 交叉验证 (R3-B)
            # fix(omni-g-tonellms-10): _resolve_locus_track 已提取为模块级
            # (import-based 回归测试), 行为见该函数 docstring。

            # Full 轨 locus + confidence
            _loc_full, _conf_full = _resolve_locus_track(innov_loci_full, topics_full)
            innovation_locus_full_arr.append(_loc_full)
            category_confidence_full_arr.append(_conf_full)

            # Ctx 轨 locus + confidence (独立运行 canonicalize_topic(topics_ctx))
            _loc_ctx, _conf_ctx = _resolve_locus_track(innov_loci_ctx, topics_ctx)
            innovation_locus_ctx_arr.append(_loc_ctx)
            category_confidence_ctx_arr.append(_conf_ctx)

            # Ss 轨 locus + confidence (独立运行 canonicalize_topic(topics_ss), 同句共现)
            _loc_ss, _conf_ss = _resolve_locus_track(innov_loci_ss, topics_ss)
            innovation_locus_ss_arr.append(_loc_ss)
            category_confidence_ss_arr.append(_conf_ss)

            # ── 创新实质性分类多数决（v3.2.0 双轨独立 + v3.9.0 三轨 full/ctx/ss; W&Z 1994/1998 ASQ; 二分类） ──
            # 三轨平局策略对称: 平局保守降为 '象征性' (W&Z framework 下实质性需充分证据,
            # 平局倾向象征性是保守审慎判定; MAP under uniform prior); 空票返回 None.
            innov_subst_full_arr.append(majority_vote_categorical(
                innov_substs_full,
                tie_strategy='conservative',
                tie_default='象征性',
                empty_fallback=None,
            ))
            innov_subst_ctx_arr.append(majority_vote_categorical(
                innov_substs_ctx,
                tie_strategy='conservative',
                tie_default='象征性',
                empty_fallback=None,
            ))
            innov_subst_ss_arr.append(majority_vote_categorical(
                innov_substs_ss,
                tie_strategy='conservative',
                tie_default='象征性',
                empty_fallback=None,
            ))

            # v7 R6-H: row-level avg per-model confidence (W&Z + Gomber 维度), 三轨独立
            # fix(omni-g-tonellms-13, 2026-06-11): 原内联闭包 _avg_conf 提取为
            # 模块级 _avg_innovation_confidence (聚合域与标签域对齐, 行为见其
            # docstring; import-based 回归测试)。
            innov_subst_conf_full_arr.append(_avg_innovation_confidence(parsed_full, 'innovation_substantiveness', MODELS))
            innov_subst_conf_ctx_arr.append(_avg_innovation_confidence(parsed_ctx, 'innovation_substantiveness', MODELS))
            innov_subst_conf_ss_arr.append(_avg_innovation_confidence(parsed_ss, 'innovation_substantiveness', MODELS))
            innov_locus_conf_full_arr.append(_avg_innovation_confidence(parsed_full, 'innovation_locus', MODELS))
            innov_locus_conf_ctx_arr.append(_avg_innovation_confidence(parsed_ctx, 'innovation_locus', MODELS))
            innov_locus_conf_ss_arr.append(_avg_innovation_confidence(parsed_ss, 'innovation_locus', MODELS))

            # v3.4.0: 第三维度 innovation_collab_mode 多数决 + confidence (Chesbrough 2003)
            # tie_strategy: 保守 fallback 至 "自主研发" (与 W&Z substantiveness tie→"象征性" 同样
            # 是 MAP under uniform prior; 自主研发是 fintech 银行的默认归因状态, 外部协同需充分
            # 证据). empty_fallback=None 与 substantiveness 对齐.
            innov_collab_full_arr.append(majority_vote_categorical(
                innov_collab_modes_full,
                tie_strategy='conservative',
                tie_default='自主研发',
                empty_fallback=None,
            ))
            innov_collab_ctx_arr.append(majority_vote_categorical(
                innov_collab_modes_ctx,
                tie_strategy='conservative',
                tie_default='自主研发',
                empty_fallback=None,
            ))
            innov_collab_ss_arr.append(majority_vote_categorical(
                innov_collab_modes_ss,
                tie_strategy='conservative',
                tie_default='自主研发',
                empty_fallback=None,
            ))
            innov_collab_conf_full_arr.append(_avg_innovation_confidence(parsed_full, 'innovation_collab_mode', MODELS))
            innov_collab_conf_ctx_arr.append(_avg_innovation_confidence(parsed_ctx, 'innovation_collab_mode', MODELS))
            innov_collab_conf_ss_arr.append(_avg_innovation_confidence(parsed_ss, 'innovation_collab_mode', MODELS))

        phase_durations['③三轨聚合+多数投票'] = time.time() - _t
        _t = time.time()

        # fix(2026-06-19 run-check F3): 以下向宽表一次性批量加 ~80 列 (per-model 独立判断 +
        # 三轨 verified/sentiment/agreement/innovation/prob_score 等; 所有值均预先算好,
        # 段内无 read-after-write) 会反复触发 pandas PerformanceWarning(DataFrame is highly
        # fragmented) —— 纯性能提示, 不改 21_tone_llms.parquet 任一列的值/dtype/列序 (golden
        # 锚点字节不变)。按 message+category 精确抑制该提示 (而非重构为 pd.concat: 后者可能改
        # dtype/列序破坏 golden 列哈希, 两位 golden-safety 评审已 BLOCK Option B)。
        warnings.filterwarnings(
            "ignore",
            category=PerformanceWarning,
            message="DataFrame is highly fragmented",
        )
        # 批量赋值各模型独立判断列
        for col_name, col_values in per_model_cols.items():
            df[col_name] = col_values

        df['llm_verified_full'] = llm_verified_full_arr
        df['llm_verified_ctx'] = llm_verified_ctx_arr
        df['llm_verified_ss'] = llm_verified_ss_arr            # ss 轨 (银行+金科同句共现)
        df['llm_sentiment_full'] = llm_sentiment_full_arr
        df['llm_sentiment_ctx'] = llm_sentiment_ctx_arr
        df['llm_sentiment_ss'] = llm_sentiment_ss_arr
        df['llm_agreement_rate_full'] = agreement_rate_full_arr
        df['llm_agreement_rate_ctx'] = agreement_rate_ctx_arr
        df['llm_agreement_rate_ss'] = agreement_rate_ss_arr
        # v6/F2 新增掩码 / 元数据列
        df['llm_agreement_rate_s_full'] = agreement_rate_s_full_arr
        df['llm_agreement_rate_s_ctx'] = agreement_rate_s_ctx_arr
        df['llm_agreement_rate_s_ss'] = agreement_rate_s_ss_arr
        df['n_valid_votes_full'] = n_valid_votes_full_arr
        df['n_valid_votes_ctx'] = n_valid_votes_ctx_arr
        df['n_valid_votes_ss'] = n_valid_votes_ss_arr
        df['n_verifying_votes_full'] = n_verifying_votes_full_arr
        df['n_verifying_votes_ctx'] = n_verifying_votes_ctx_arr
        df['n_verifying_votes_ss'] = n_verifying_votes_ss_arr
        df['llm_call_failure_full'] = call_failure_full_arr
        df['llm_call_failure_ctx'] = call_failure_ctx_arr
        df['llm_call_failure_ss'] = call_failure_ss_arr
        df['llm_undefined_full'] = undefined_full_arr
        df['llm_undefined_ctx'] = undefined_ctx_arr
        df['llm_undefined_ss'] = undefined_ss_arr
        # v3.2.0 BREAKING (plan v14 §2.1 Action #2): bare innovation_locus / innovation_substantiveness 删除,
        # 重命名为 _full / _ctx 双轨独立列 (W&Z 1998 ASQ + Gomber, Koch & Siering 2017 Digital Finance Cube [Gomber et al. 2018 JMIS 背景] + Hassan 2019 QJE);
        # v3.9.0 三轨化: 追加 _ss (银行+金科同句共现) 独立列。
        df['innovation_locus_full'] = innovation_locus_full_arr
        df['innovation_locus_ctx'] = innovation_locus_ctx_arr
        df['innovation_locus_ss'] = innovation_locus_ss_arr
        df['category_confidence_full'] = category_confidence_full_arr
        df['category_confidence_ctx'] = category_confidence_ctx_arr
        df['category_confidence_ss'] = category_confidence_ss_arr
        df['innovation_substantiveness_full'] = innov_subst_full_arr
        df['innovation_substantiveness_ctx'] = innov_subst_ctx_arr
        df['innovation_substantiveness_ss'] = innov_subst_ss_arr
        # plan v14 §3.1 P1 (Action #6) + v3.9.0 三轨化: triple gate 7 互斥指示列。
        # 历史保留 dual (full/ctx) 三列名 (下游消费), 加性扩 7 态三轨互斥指示
        # (full_only/ctx_only/ss_only/full_ctx/full_ss/ctx_ss/all_three), 与下方
        # 7 行诊断日志同口径。
        _vf = pd.Series(llm_verified_full_arr).astype(bool)
        _vc = pd.Series(llm_verified_ctx_arr).astype(bool)
        _vs = pd.Series(llm_verified_ss_arr).astype(bool)
        # 既有 dual 列 (向后兼容, 仅 full↔ctx 二元, 不含 ss): 下游 encode 仍消费
        df['llm_verified_dual_full_only'] = (_vf & ~_vc).values
        df['llm_verified_dual_ctx_only']  = (~_vf & _vc).values
        df['llm_verified_dual_both']      = (_vf & _vc).values
        # v3.9.0 triple gate 7 互斥态 (full/ctx/ss verified 的 7 种非空组合)
        df['llm_verified_triple_full_only'] = (_vf & ~_vc & ~_vs).values
        df['llm_verified_triple_ctx_only']  = (~_vf & _vc & ~_vs).values
        df['llm_verified_triple_ss_only']   = (~_vf & ~_vc & _vs).values
        df['llm_verified_triple_full_ctx']  = (_vf & _vc & ~_vs).values
        df['llm_verified_triple_full_ss']   = (_vf & ~_vc & _vs).values
        df['llm_verified_triple_ctx_ss']    = (~_vf & _vc & _vs).values
        df['llm_verified_triple_all_three'] = (_vf & _vc & _vs).values
        # v7 R6-H: 三轨 × 三维度的 row-level avg confidence (encode.py 下游聚合源)
        df['innovation_substantiveness_confidence_full'] = innov_subst_conf_full_arr
        df['innovation_substantiveness_confidence_ctx'] = innov_subst_conf_ctx_arr
        df['innovation_substantiveness_confidence_ss'] = innov_subst_conf_ss_arr
        df['innovation_locus_confidence_full'] = innov_locus_conf_full_arr
        df['innovation_locus_confidence_ctx'] = innov_locus_conf_ctx_arr
        df['innovation_locus_confidence_ss'] = innov_locus_conf_ss_arr
        # v3.4.0: 第三维度 innovation_collab_mode 三轨写回 (additive supplementation,
        # Chesbrough 2003 + L&S 2006 SMJ; v7 dual gate (locus 闸门) 语义不变)
        df['innovation_collab_mode_full'] = innov_collab_full_arr
        df['innovation_collab_mode_ctx'] = innov_collab_ctx_arr
        df['innovation_collab_mode_ss'] = innov_collab_ss_arr
        df['innovation_collab_mode_confidence_full'] = innov_collab_conf_full_arr
        df['innovation_collab_mode_confidence_ctx'] = innov_collab_conf_ctx_arr
        df['innovation_collab_mode_confidence_ss'] = innov_collab_conf_ss_arr

        # ── Logit-to-Score 概率分数写入 DataFrame (三轨 full/ctx/ss) ──
        if LOGIT_SCORE_ENABLED:
            df['llm_prob_score_full'] = prob_score_full_arr
            df['llm_prob_score_ctx'] = prob_score_ctx_arr
            df['llm_prob_score_ss'] = prob_score_ss_arr
            # Plan v1.37 P2: 文章级 binary prob_score 列 (subst / locus, 三轨)
            # v3.4.0: + collab_mode prob_score 列 (Chesbrough 2003 + L&S 2006)
            df['avg_subst_prob_score_full'] = subst_prob_score_full_arr
            df['avg_subst_prob_score_ctx'] = subst_prob_score_ctx_arr
            df['avg_subst_prob_score_ss'] = subst_prob_score_ss_arr
            df['avg_locus_prob_score_full'] = locus_prob_score_full_arr
            df['avg_locus_prob_score_ctx'] = locus_prob_score_ctx_arr
            df['avg_locus_prob_score_ss'] = locus_prob_score_ss_arr
            df['avg_collab_prob_score_full'] = collab_prob_score_full_arr
            df['avg_collab_prob_score_ctx'] = collab_prob_score_ctx_arr
            df['avg_collab_prob_score_ss'] = collab_prob_score_ss_arr
            n_rows = len(prob_score_full_arr)
            # fix(2026-06-19 run-check F12): 原 sum(arr)/n 对含 NaN 的 prob_score 列恒得 NaN,
            # 诊断日志永远打印 'mean=nan' (掩盖真实分布)。改为 NaN-aware 均值 (v==v 滤除 NaN),
            # 纯日志行, 不写 21_tone_llms.parquet → golden 安全; 无新依赖、不触发空切片告警。
            _pf = [v for v in prob_score_full_arr if v == v]
            _pc = [v for v in prob_score_ctx_arr if v == v]
            _ps = [v for v in prob_score_ss_arr if v == v]
            mean_full = sum(_pf) / len(_pf) if _pf else float('nan')
            mean_ctx = sum(_pc) / len(_pc) if _pc else float('nan')
            mean_ss = sum(_ps) / len(_ps) if _ps else float('nan')
            logger.info(f"Logit-to-Score (NaN-aware 均值, 分母=非空数): "
                        f"full mean={sig4(mean_full)} (n={len(_pf):,d}), "
                        f"ctx mean={sig4(mean_ctx)} (n={len(_pc):,d}), "
                        f"ss mean={sig4(mean_ss)} (n={len(_ps):,d}), n_total={n_rows:,d}")

        if n_api_failures > 0:
            logger.warning(f"共有 {n_api_failures} 次模型 API 调用失败，已从对应投票中排除")

        # 统计创新位点分布 (v3.2.0 双轨独立 + v3.9.0 三轨; Gomber, Koch & Siering 2017 Digital Finance Cube [Gomber et al. 2018 JMIS 背景] + Hassan 2019 QJE)
        for _track, _ver_col, _loc_col in [
            ('full', 'llm_verified_full', 'innovation_locus_full'),
            ('ctx',  'llm_verified_ctx',  'innovation_locus_ctx'),
            ('ss',   'llm_verified_ss',   'innovation_locus_ss'),  # 银行+金科同句共现
        ]:
            if df[_ver_col].sum() > 0:
                _vdf = df[df[_ver_col]]
                _counts = _vdf[_loc_col].value_counts()
                for _label, _cnt in _counts.items():
                    logger.info(f"  创新位点 [{_track}] [{_label}]: {_cnt}")

        # 结果统计（三轨对比 full/ctx/ss）
        total_len = len(df)
        for track in ['_full', '_ctx', '_ss']:
            ver_col = f'llm_verified{track}'
            sent_col = f'llm_sentiment{track}'
            passed_len = df[ver_col].sum()
            logger.info(
                f"[{track}] 多数决判定为真: {passed_len:,d}/{total_len:,d} "
                f"({pct4(passed_len / total_len) if total_len else 'n/a'})"
            )

            if passed_len > 0:
                sent_counts = df[df[ver_col]][sent_col].value_counts()
                for s_type, cnt in sent_counts.items():
                    logger.info(f"  [{track}] [{s_type}]: {cnt:,d} ({pct4(cnt / passed_len)})")

        # 保存全量结果（含 llm_verified=True 和 False），供验证模块使用
        full_output_filename = CONFIG.get('filenames', {}).get(
            'output_21_tone_llms_full', '21_tone_llms_full.parquet')
        full_output_path = os.path.join(CONFIG["paths"]["output_dir"], full_output_filename)
        input_file = os.path.join(CONFIG['paths']['output_dir'],
                                  CONFIG['filenames']['output_14_fintech_intensity'])
        save_dataset(df, full_output_path, logger,
                    stage_name="21_tone_llms",
                    config=CONFIG,
                    input_files=[input_file])
        logger.info(f"全量 LLM 结果已保存: {full_output_path} ({len(df)} 行)")

        # full-only 留篇门控 (用户决策 2026-06-29; 逆转 v3.2.0 R1-A + v3.9.0 三轨并集门):
        #   是否属于"目标银行×金融科技"媒体报道, **仅由全文轨 3-LLM 多数决
        #   `llm_verified_full` 决定**。理由: ctx 轨 (银行邻近句) 与 ss 轨 (银行∧金科
        #   同句) 都对正文做窗口截断, 可能漏掉决定金科相关性的信息 → 窄窗口的
        #   verified 不足以单独把一篇文章拉进样本。ctx/ss 由此从"各自独立识别的
        #   并列主轨"降为 conditional-on-full 的测度/稳健性轨: 其 per-track 列照常
        #   计算 (本行只筛行, 不动列), 仅在 full 已留篇的行内、各自经 encode 的
        #   per-track 掩码 (llm_vote_score_{ctx,ss} 在该轨 verified=False 处置 NaN)
        #   进 ctx/ss 聚合。
        #
        # ⚠ 这恢复了 v3.2.0 R1-A 之前的 conditional-on-full 状态 (该 R1-A 注释原是
        #   为消除此状态而写, 现按用户口径回退)。"三轨各自 just-identified 并排、
        #   不混同一 over-identified Hansen J"的铁律**不受影响** —— 三轨仍各自分开
        #   报回归, 改变的只是 ctx/ss 的样本宇宙变为 full 留篇集的子集。
        df_filtered = df[df['llm_verified_full'] == True].copy()  # noqa: E712 - pandas boolean mask
        # Triple gate 7 互斥态诊断 (full/ctx/ss verified 的 7 种非空组合; 互斥且穷尽
        # "任一轨 verified"的诊断并集)。注: full-only 门控下真正进入输出样本的只是
        # **含 full 的 4 态** (full_only/full_ctx/full_ss/all_three); ctx_only/ss_only/
        # ctx_ss 三态 (full 未过) 是被排除的篇, 仅作诊断 (见下方含-full 恒等校验)。
        _n_full_only = int(df['llm_verified_triple_full_only'].sum())
        _n_ctx_only  = int(df['llm_verified_triple_ctx_only'].sum())
        _n_ss_only   = int(df['llm_verified_triple_ss_only'].sum())
        _n_full_ctx  = int(df['llm_verified_triple_full_ctx'].sum())
        _n_full_ss   = int(df['llm_verified_triple_full_ss'].sum())
        _n_ctx_ss    = int(df['llm_verified_triple_ctx_ss'].sum())
        _n_all_three = int(df['llm_verified_triple_all_three'].sum())
        logger.info("  Triple gate (7 互斥态分解; full-only 下仅含-full 4 态进入输出):")
        logger.info(f"    full-only  = {_n_full_only}")
        logger.info(f"    ctx-only   = {_n_ctx_only}   (full 未过 → full-only 下排除)")
        logger.info(f"    ss-only    = {_n_ss_only}   (full 未过 → full-only 下排除)")
        logger.info(f"    full+ctx   = {_n_full_ctx}")
        logger.info(f"    full+ss    = {_n_full_ss}")
        logger.info(f"    ctx+ss     = {_n_ctx_ss}   (full 未过 → full-only 下排除)")
        logger.info(f"    all-three  = {_n_all_three}")
        _gate_full_states = _n_full_only + _n_full_ctx + _n_full_ss + _n_all_three
        _gate_all_states = _gate_full_states + _n_ctx_only + _n_ss_only + _n_ctx_ss
        logger.info(f"  含-full 4 态之和 = 输出样本 = {len(df_filtered)} (= full verified {_gate_full_states})")
        logger.info(f"  7 态全和 (任一轨 verified 的诊断并集, ≥ 输出) = {_gate_all_states}")

        # remove-title-track (v3.8.0): 独立标题情感轨已移除, 标题改 prepend 进
        # full/ctx/ss 三轨 (v3.9.0); 原 B1-2 标题批量提取块在 TITLE_PROMPT_TEMPLATE=''
        # 守卫下永不执行 (死代码, 无下游消费), 连同 _avg_valid_title_prob_score helper 清理。

        # ======================================================================
        # 4. 保存文件与报告
        # ======================================================================
        output_filename = CONFIG.get('filenames', {}).get('output_21_tone_llms', '21_tone_llms.parquet')
        output_path = os.path.join(CONFIG["paths"]["output_dir"], output_filename)

        logger.info(f"正在保存处理结果至 {output_path}...")
        input_file = os.path.join(CONFIG['paths']['output_dir'],
                                  CONFIG['filenames']['output_14_fintech_intensity'])
        save_dataset(df_filtered, output_path, logger,
                    stage_name="21_tone_llms",
                    config=CONFIG,
                    input_files=[input_file])

        # ── 【结果分析】: 对真实产出指标对照阈值/预期方向给判读 (golden 范式; 纯只读日志) ──
        # 所有局部量仅服务于日志, 不回写 df/产物。本块整体 try/except 包裹:
        # 即便在最终写盘之后, 任何只读诊断异常 (缺列/类型/除零等) 也不得拖垮阶段或丢失产物。
        logger.info("-" * 72)
        logger.info("【结果分析】LLM 三轨语义精筛与情感产出解读 (对照阈值/预期方向):")
        # 说明: 以下 ②④ 为对上方 2200-2217 既有三轨循环统计 (verified 计数 + 情绪 value_counts)
        # 的判读性复述, 取值与既有块 df[df[ver_col]] 真值索引同口径 (不存在两份相左统计)。
        try:
            _total = total_len  # = len(df) = 全量候选篇数

            # ① 确定性/成本闸门 — 缓存命中 == golden 可复现的充要条件
            _miss = _cstats.get('misses', 0)
            _writes = _cstats.get('writes', 0)
            _hit_rate = _cstats.get('hit_rate', 0.0)
            logger.info(
                f"  · 缓存命中: hit_rate={sig4(_hit_rate)}, misses={_miss:,d}, writes={_writes:,d} "
                f"(lookups={_cstats.get('lookups', 0):,d})。"
            )
            if _miss == 0 and _writes == 0:
                logger.info("    → 零 miss/零 write = 本次全部命中 _llm_cache.db, 无新 API 调用, golden 字节级可复现(好)。")
            else:
                logger.warning(
                    f"    ⚠ 存在 {_miss} 次缓存 miss / {_writes} 次新写入 — 本次有新 API 调用(付费), "
                    "投票可能与历史盘面漂移; 复现 golden 前须确认这些新条目已稳定播种回 _llm_cache.db。"
                )
            if n_api_failures > 0:
                logger.warning(
                    f"    ⚠ {n_api_failures} 次模型 API 调用失败已从投票中剔除 — 若失败集中于单一模型/单一轨, "
                    "对应 verified/sentiment 多数决会退化为双模型决, 建议核查网络/限流后重跑。"
                )

            # ② verified 精筛闸门 — 三轨各自通过率 + full-only 输出 (下游主消费样本)
            _n_output = len(df_filtered)
            logger.info(
                f"  · verified 输出 (仅全文轨 verified_full 过即留, full-only): {_n_output:,d}/{_total:,d} "
                f"({pct4(_n_output / _total) if _total else 'n/a'}) → 即 21_tone_llms.parquet 下游样本。"
            )
            for _trk, _vcol in [('_full', 'llm_verified_full'),
                                ('_ctx', 'llm_verified_ctx'),
                                ('_ss (银行+金科同句)', 'llm_verified_ss')]:
                if _vcol not in df.columns:
                    logger.info(f"    · 轨道 {_trk}: 列 {_vcol} 缺失, 跳过该轨。")
                    continue
                _passed = int(df[_vcol].sum())
                _pct = pct4(_passed / _total) if _total else 'n/a'
                logger.info(f"    · 轨道 {_trk}: verified {_passed:,d}/{_total:,d} ({_pct})。")
            logger.info(
                "    判读: verified 率越高=语料越聚焦'银行×金科', 率过低(经验上 <10%)再结合金科词典缺失/语料漂移排查; "
                "三轨取材窗口不同(全文 / 银行邻近句 / 银行∧金科同句)且回退比例各异 — ss 无共现时回退全文(镜像 ctx), "
                "故三轨 verified 率互为稳健性印证、不存在固定大小关系(ss 可能高于或低于 full)。"
                "注: 自 2026-06-29 full-only gating 起, 是否留篇仅由全文轨 verified_full 决定 — "
                "ctx/ss verified 率仅作测度稳健性参考, 不再独立决定下游样本 (其行宇宙现为 full 留篇集的子集)。"
            )

            # ③ Triple-gate 恒等校验 (full-only): 含 full 的 4 态之和应 == 输出样本数;
            #    7 态全和 = "任一轨 verified"的诊断并集 (≥ 输出, 含被 full-only 排除的
            #    ctx-only / ss-only / ctx+ss 篇)。
            _gate_full = _n_full_only + _n_full_ctx + _n_full_ss + _n_all_three
            _gate_sum = (_n_full_only + _n_ctx_only + _n_ss_only + _n_full_ctx
                         + _n_full_ss + _n_ctx_ss + _n_all_three)
            logger.info(
                f"  · Triple-gate 含-full 4 态之和={_gate_full:,d}, 输出样本={_n_output:,d} → "
                + ("一致(full-only 恒等校验通过, 好)。" if _gate_full == _n_output
                   else "不一致(异常! 含-full 态分解与输出不闭合, 须排查 verified_full 列对齐)。")
            )
            logger.info(
                f"  · (诊断) 7 互斥态全和={_gate_sum:,d} = 任一轨 verified 的并集 "
                f"(含被 full-only 排除的 {_gate_sum - _n_output:,d} 篇 ctx-only/ss-only/ctx+ss)。"
            )
            if _gate_full != _n_output:
                logger.warning(
                    f"    ⚠ Triple-gate 恒等校验失败: 含-full 4 态和 {_gate_full:,d} != 输出 {_n_output:,d}; "
                    "互斥/穷尽假设被破坏, 下游 triple-gate 诊断列不可信。"
                )
            _n_three_track = _n_all_three
            if _n_output > 0:
                logger.info(
                    f"    三轨全 verified (all-three) {_n_three_track:,d} 篇 "
                    f"({pct4(_n_three_track / _n_output)} of 输出样本); 占比越高=三种归因窗口判定越一致, 测度越稳。"
                )

            # ④ 情绪极性方向 — full-only 输出样本各轨情绪占比 (主变量信号)
            for _trk, _vcol, _scol in [('_full', 'llm_verified_full', 'llm_sentiment_full'),
                                       ('_ctx', 'llm_verified_ctx', 'llm_sentiment_ctx'),
                                       ('_ss', 'llm_verified_ss', 'llm_sentiment_ss')]:
                if _vcol not in df.columns or _scol not in df.columns:
                    logger.info(f"    · 轨道 {_trk} 情绪分布: 列 {_vcol}/{_scol} 缺失, 跳过该轨。")
                    continue
                _vsub = df[df[_vcol]]  # 真值索引, 与既有 2200/2214 块同口径
                _n_v = len(_vsub)
                if _n_v == 0:
                    logger.info(f"    · 轨道 {_trk} 情绪分布: 无 verified 篇, 跳过。")
                    continue
                _sc = _vsub[_scol].value_counts(dropna=False)
                _pos = int(_sc.get('正面', 0))
                _neg = int(_sc.get('负面', 0))
                _neu = int(_sc.get('中性', 0))
                _undef = _n_v - _pos - _neg - _neu  # None/未定: 用户决策 2026-06-23 后 verified 轨平局/空票→中性, 此项结构性≈0 (残留非0 即异常态)
                logger.info(
                    f"    · 轨道 {_trk} (verified={_n_v:,d}): 正面 {pct4(_pos / _n_v)} / "
                    f"负面 {pct4(_neg / _n_v)} / 中性 {pct4(_neu / _n_v)} / "
                    f"未定 {pct4(_undef / _n_v)}。"
                )
            logger.info(
                "    判读: 用户决策 (2026-06-23) 后 verified 轨情感平局/空票已保守降级为'中性'(不再产'未定'), "
                "故'未定'占比应≈0 (残留非0 即异常态, 需排查); '中性'占比已含原平局降级部分; "
                "正负面方向跨轨一致=测度收敛(好)。"
            )

            # ⑤ logit-to-score 连续分 — full-only 输出样本的轨级分布 (均值 + 离散度 + 极性桶)
            if LOGIT_SCORE_ENABLED:
                for _trk, _pcol in [('_full', 'llm_prob_score_full'),
                                    ('_ctx', 'llm_prob_score_ctx'),
                                    ('_ss', 'llm_prob_score_ss')]:
                    if _pcol in df_filtered.columns and len(df_filtered) > 0:
                        _ser = pd.to_numeric(df_filtered[_pcol], errors='coerce').dropna()
                        _nn = int(_ser.shape[0])
                        if _nn == 0:
                            logger.info(f"    · llm_prob_score{_trk}: 该轨无有效数据(全 NaN), 跳过分布判读。")
                        else:
                            _mean = float(_ser.mean())
                            _std = float(_ser.std()) if _nn > 1 else 0.0
                            _pos = int((_ser > 0).sum())
                            _neg = int((_ser < 0).sum())
                            _zero = _nn - _pos - _neg
                            logger.info(
                                f"    · llm_prob_score{_trk} 输出(full-only) mean={sig4(_mean)} sd={sig4(_std)} "
                                f"范围[{sig4(_ser.min())},{sig4(_ser.max())}] (非空 {_nn:,d}); "
                                f"极性桶 >0 {pct4(_pos / _nn)} / <0 {pct4(_neg / _nn)} / "
                                f"≈0 {pct4(_zero / _nn)}。"
                            )
                logger.info(
                    "    判读: [-1,+1] 连续分(置信加权), >0 偏正面、<0 偏负面、|值| 越大语气越强; "
                    "sd 越小=语气越集中(本语料近全正面故 mean 高、sd 小属预期), <0 桶占比即负面信号密度; "
                    "回归前据此判断 DV 是否有足够变异 — 过度集中(sd≈0)会削弱识别力。"
                )
            else:
                logger.info("    · logit-to-score 已禁用 (LOGIT_SCORE_ENABLED=False), 无 llm_prob_score_* 连续分输出。")

            # ⑥ 创新三维标签分布 — verified 子样本上 locus/substantiveness/collab 的二元构成
            #    (下游 P4 locus / P3 substance / P5 collab 三篇论文 main DV 之源; 二元标签即面板列编码)。
            #    positive_class 与 stata_export value_labels / prob_score 对齐:
            #    locus→应用场景 / subst→象征性 / collab→外部协同 (1=对照类)。
            _innov_dims = [
                ('创新位点', '底层技术/应用场景', 'P4 locus', 'innovation_locus', ('应用场景', '底层技术')),
                ('实质性', '实质性/象征性', 'P3 substance', 'innovation_substantiveness', ('象征性', '实质性')),
                ('协同模式', '自主研发/外部协同', 'P5 collab', 'innovation_collab_mode', ('外部协同', '自主研发')),
            ]
            logger.info("  · 创新三维标签分布 (各轨 verified 子样本; 平局/低置信→保守 MAP 降级):")
            for _dname, _dlab, _paper, _base, (_lab_a, _lab_b) in _innov_dims:
                _parts = []
                for _trk, _vcol in [('full', 'llm_verified_full'),
                                    ('ctx', 'llm_verified_ctx'),
                                    ('ss', 'llm_verified_ss')]:
                    _dcol = f"{_base}_{_trk}"
                    if _vcol not in df.columns or _dcol not in df.columns:
                        _parts.append(f"{_trk} N/A")
                        continue
                    _sub = df[df[_vcol]]
                    if len(_sub) == 0:
                        _parts.append(f"{_trk} 无verified")
                        continue
                    _vc = _sub[_dcol].value_counts(dropna=True)
                    _na = int(_vc.get(_lab_a, 0))
                    _nb = int(_vc.get(_lab_b, 0))
                    _den = _na + _nb
                    if _den == 0:
                        _parts.append(f"{_trk} 标签全空")
                        continue
                    _parts.append(f"{_trk} {_lab_a}{pct4(_na / _den)}/{_lab_b}{pct4(_nb / _den)}")
                logger.info(f"    - {_dname} ({_dlab} → {_paper}): " + " | ".join(_parts))
                # 📖 该维度二元构念的学术出处 (runtime emit; 逐字取自经核验注册表 pool):
                # substantiveness→W&Z 1994 实质 vs 象征 / locus→Gomber 等 2017 数字金融立方体
                # 底层 vs 应用 / collab→Laursen & Salter 2006 开放式创新外部搜索广度。
                if _base in _INNOV_CONSTRUCT_REFERENCES:
                    logger.info(f"      📖 {_dname}构念源: {_INNOV_CONSTRUCT_REFERENCES[_base]}")
            logger.info(
                "    判读: 二元构成是下游 P3/P4/P5 论文主因变量之源; 因平局/低置信票按保守 MAP 降级到"
                "基类(应用场景/象征性/自主研发), 该方向占比天然偏高 — 极端单边(如某类>99%)在 T=2 小样本"
                "属正常退化, 须以全量 T=18 占比为准, 不可据盘面下实质结论。"
            )

            # ⑦ 模型间一致性 (ensemble inter-model agreement) — 3-LLM 多数决的可靠性 / inter-rater 替代量
            #    llm_agreement_rate_*   = verified 票与最终判定一致的(有效)模型占比;
            #    llm_agreement_rate_s_* = verified 子样本上情感票与最终情感一致占比 (NaN=无有效情感票)。
            _n_models = len(MODELS) if MODELS else 3
            logger.info(f"  · 模型间一致性 (ensemble, n_models={_n_models}; 越接近 1=三模型越趋同, 测度越可靠):")
            for _trk, _vcol, _arv, _ars in [
                ('_full', 'llm_verified_full', 'llm_agreement_rate_full', 'llm_agreement_rate_s_full'),
                ('_ctx', 'llm_verified_ctx', 'llm_agreement_rate_ctx', 'llm_agreement_rate_s_ctx'),
                ('_ss', 'llm_verified_ss', 'llm_agreement_rate_ss', 'llm_agreement_rate_s_ss'),
            ]:
                if _vcol not in df.columns:
                    continue
                _sub = df[df[_vcol]]
                if len(_sub) == 0:
                    logger.info(f"    · 轨道 {_trk}: 无 verified 篇, 跳过。")
                    continue
                _msg = f"    · 轨道 {_trk} (verified={len(_sub):,d}): "
                if _arv in _sub.columns:
                    _rv = pd.to_numeric(_sub[_arv], errors='coerce').dropna()
                    if len(_rv) > 0:
                        _unan_v = float((_rv >= 0.999).mean()) * 100
                        _msg += f"verified 票一致率 mean={sig4(_rv.mean())} (全票一致 {pct4(_unan_v, fraction=False)})"
                    else:
                        _msg += "verified 票一致率 N/A"
                if _ars in _sub.columns:
                    _rs = pd.to_numeric(_sub[_ars], errors='coerce').dropna()
                    if len(_rs) > 0:
                        _unan_s = float((_rs >= 0.999).mean()) * 100
                        _msg += f"; 情感票一致率 mean={sig4(_rs.mean())} (非空 {len(_rs):,d}, 全票一致 {pct4(_unan_s, fraction=False)})"
                    else:
                        _msg += "; 情感票一致率 N/A(无有效情感票)"
                logger.info(_msg)
            logger.info(
                "    判读: 一致率是 3-LLM 评分员的 inter-rater reliability 替代量 — mean 越高 / 全票一致占比"
                "越大 = 三模型对'是否金科×语气'判断越收敛, 主变量越可信; 某轨显著低于其他轨说明该轨边界"
                "样本更多(语义更模糊), 解释其回归时需谨慎。下游 encode 以 agreement_rate 作连续衰减权重。"
            )

            # ⑧ 三轨情感收敛 (convergent validity) — all-three verified 子样本上三轨情感是否一致
            _scols = ['llm_sentiment_full', 'llm_sentiment_ctx', 'llm_sentiment_ss']
            if all(c in df.columns for c in _scols) and 'llm_verified_triple_all_three' in df.columns:
                _at = df[df['llm_verified_triple_all_three']]
                _nat = len(_at)
                if _nat > 0:
                    _agree3 = int(((_at['llm_sentiment_full'] == _at['llm_sentiment_ctx'])
                                   & (_at['llm_sentiment_ctx'] == _at['llm_sentiment_ss'])).sum())
                    logger.info(
                        f"  · 三轨情感收敛 (all-three verified={_nat:,d} 篇): 三轨情感标签完全一致 "
                        f"{_agree3:,d}/{_nat:,d} ({pct4(_agree3 / _nat)})。"
                    )
                    _pcols = ['llm_prob_score_full', 'llm_prob_score_ctx', 'llm_prob_score_ss']
                    if LOGIT_SCORE_ENABLED and all(c in df.columns for c in _pcols):
                        _pf = pd.to_numeric(_at['llm_prob_score_full'], errors='coerce')
                        _pc = pd.to_numeric(_at['llm_prob_score_ctx'], errors='coerce')
                        _ps = pd.to_numeric(_at['llm_prob_score_ss'], errors='coerce')
                        logger.info(
                            f"    连续分跨轨 Pearson r: full~ctx={sig4(_pf.corr(_pc))}, "
                            f"full~ss={sig4(_pf.corr(_ps))}, ctx~ss={sig4(_pc.corr(_ps))}。"
                        )
                    logger.info(
                        "    判读: 同一篇在三种归因窗口(全文 / 银行邻近句 / 银行∧金科同句)下情感判定高度一致 = "
                        "测度对窗口选择稳健(收敛效度好); 一致率/相关偏低则窗口口径会实质改变语气测度 — 三轨更应"
                        "作为彼此独立的稳健性各自进回归(铁律: 禁混同一 Hansen J), 而非互相替代。"
                    )

            # ⑨ 投票完整性 / API 退化诊断 — 每篇有多少模型成功返回 (满票=n_models)
            logger.info(f"  · 投票完整性 (满票=n_models={_n_models}; 缺票轨多数决退化为双/单模型):")
            for _trk, _nvc, _cfc, _udc in [
                ('_full', 'n_valid_votes_full', 'llm_call_failure_full', 'llm_undefined_full'),
                ('_ctx', 'n_valid_votes_ctx', 'llm_call_failure_ctx', 'llm_undefined_ctx'),
                ('_ss', 'n_valid_votes_ss', 'llm_call_failure_ss', 'llm_undefined_ss'),
            ]:
                if _nvc not in df.columns:
                    continue
                _nv = pd.to_numeric(df[_nvc], errors='coerce')
                _full_vote = int((_nv >= _n_models).sum())
                _pct_full = pct4(_full_vote / _total) if _total else 'n/a'
                _cf = int(df[_cfc].sum()) if _cfc in df.columns else 0
                _ud = int(df[_udc].sum()) if _udc in df.columns else 0
                logger.info(
                    f"    · 轨道 {_trk}: 满票 {_full_vote:,d}/{_total:,d} ({_pct_full}), "
                    f"全模型缺席 {_cf:,d} 篇, undefined(平局未决) {_ud:,d} 篇。"
                )
            logger.info(
                "    判读: 离线/缓存全命中时满票应≈100%、全模型缺席=0; undefined 在 2026-06-23 决策后结构性"
                "恒 0(verified 轨平局已降级中性), 非 0 即异常须排查。满票率显著 <100% = 有模型响应缺失, "
                "该批投票从 3 票退化为 2/1 票, 可靠性下降, 需核查网络/限流后重跑。"
            )

            # ⑩ 小样本/盘面规模警告
            if _total <= 2000:
                logger.info(
                    f"  · 样本规模 {_total:,} 行 (盘面 T=2 小样本): 本次仅验证三轨 LLM 管道正确性, "
                    "全量结论以 17M 篇 / T=18 (2007–2024) 实测为准。"
                )
            logger.info("-" * 72)
        except Exception as _e:  # noqa: BLE001  (只读诊断, 异常绝不拖垮阶段/丢失已落盘产物)
            logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")

        phase_durations['④写回+过滤+写盘+结果分析'] = time.time() - _t

        # ── ⏱ 运行期各主要子阶段墙钟耗时汇总 (便于性能定位; 纯日志, 不影响产物) ──
        try:
            if phase_durations:
                _tot = sum(phase_durations.values()) or 1.0
                logger.info("  ⏱ 运行期阶段计时 (墙钟):")
                for _pname, _pdur in phase_durations.items():
                    logger.info(f"     {_pname}: {sig4(_pdur)}s ({pct4(_pdur / _tot)})")
                logger.info(f"     合计(子阶段和): {sig4(_tot)}s")
        except Exception as _te:  # noqa: BLE001
            logger.warning(f"  阶段计时汇总打印失败 (不影响产物): {_te}")

        log_stage_summary(logger, STAGE_NAME, stage_start, len(df), len(df_filtered))

if __name__ == "__main__":
    main()
