"""
news_process.pipeline.filtering.fintech_intensity — 阶段14：金融科技技术重度评分
=================================================================================

功能：
    在阶段 12 的 AC 关键词分类（二元判定）基础上，使用 TF-IDF + IDF 加权关键词
    向量质心（IDF-weighted keyword embedding centroid）计算连续型技术强度得分
    `fintech_intensity_score`，消除三类系统性偏差：
      1. 复读机刷分（Cheap Talk）— Bingler et al. (2022, FRL)
      2. 长文体量偏差（Document Length Bias）— Manning et al. (2008, Ch 6.4)
      3. 术语区分度缺失（Term Discriminability Loss）— Loughran & McDonald (2011, JF)

    核心公式（双重对数方程）:
      Score_d = Σ_{i: TF_{d,i}>0} [ (1 + ln(TF_{d,i})) / (1 + ln(L_d)) ] × W_i
      其中 W_i = IDF_i × CosSim_scaled_i

    白话解释:
      给每个金融科技关键词加上"含金量权重"（IDF稀缺度 × 语义纯粹度），
      同时防复读机刷分和长文偏差。产出连续型"真实技术强度分"。

    **阶段 12 零修改。** 本文件完全独立，删除即可回滚。

输入：
    阶段 12 输出的 `12_fintech_news_full.parquet`（全量含非金融科技, 用于全局 IDF;
      fix omni-g-fintech-01/-03, 2026-06-11: DF 按唯一文档 (标题,日期) 去重后以
      jieba 整词统计 — 与 TF 同分词器, 替换原 AC 子串计数源; 语料列在线物化
      content_full = 标题 + 内容, 与 TF 打分文本同语义。⚠ 参考语料必须是全量:
      14_news_with_ctx 仅含 fintech 子集, 不可用作 IDF 语料; 此 _full 全量语料在
      stage 12b 上游、不受 12b 邻近共现过滤影响 — 保 IDF 区分度不塌缩）
    打分语料: 优先 `14_news_with_ctx.parquet`（自 2026-06-15 起 stage 13 读 stage 12b
      输出 = 12_fintech_news 经邻近共现硬过滤后的邻近相关金科子集 → 打分天然继承 12b;
      含 content_full/ctx/ss 三轨）; 缺失时回退 `12_fintech_news.parquet`（pre-12b, degraded）

输出：
    `15_fintech_intensity.parquet`（= 12 filtered + fintech_intensity_score + intensity_verified
      + 三轨列 fintech_intensity_score_{full,ctx,ss} / intensity_verified_{full,ctx,ss};
      无后缀列 = _full alias 向后兼容。ss 轨 = 银行+金科同句共现, 回退镜像 ctx→全文 body。
      v3.14.0 起关键词语义权重走 co-primary 双 API 模型 → 另产 _lg 孪生族
      fintech_intensity_score_lg_{full,ctx,ss} / intensity_verified_lg_{full,ctx,ss}
      (text-embedding-3-large; 与无后缀 Qwen 族严格 parity, both-or-neither 同损同有)）

学术依据：
    Li, K., Mai, F., Shen, R., & Yan, X. (2021). Measuring corporate culture using
      machine learning. The Review of Financial Studies, 34(7), 3265-3315.
    Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to Information
      Retrieval. Cambridge University Press.
    Arora, S., Liang, Y., & Ma, T. (2017). A simple but tough-to-beat baseline for
      sentence embeddings. Proceedings of ICLR 2017.
      — fix(omni-g-fintech-02, 2026-06-11): 仅为 "加权质心" 思想借鉴, **非 SIF 实现**。
        本实现无 a/(a+p(w)) 平滑逆频率权重、无首主成分 (common component) 去除,
        实际为 IDF 加权普通质心 (np.average(embeddings, weights=idf))。
    Ethayarajh, K. (2019). How contextual are contextualized word representations?
      Proceedings of EMNLP-IJCNLP 2019.
      — fix(omni-g-fintech-02, 2026-06-11): 仅作各向异性 **现象的动机引用**; 下文
        min-max + floor 重标定是工程化 ad hoc 处理, 非该文提出的校准方法。
    Singhal, A., Buckley, C., & Mitra, M. (1996). Pivoted document length normalization.
      Proceedings of SIGIR '96, pp. 21-29.

迁移说明 (Phase 7a-3)：
    本模块由原 root script ``15_fintech_intensity.py`` body 迁入。
    规范调用方式：
        python -m news_process.pipeline.filtering.fintech_intensity

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 15_fintech_intensity.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**在 DAG 中的位置**: STAGES_MAIN 阶段14, kind=filter, 无显式 timeout (取 StageSpec 默认)。上游 = stage 12 (news_fintech) + stage 13 (materialize_ctx), 下游 = stage 15 (policy_alignment, 直接读 14 的 parquet)。

**输入**:
- `12_fintech_news_full.parquet` — 全量(含非金科)新闻, 仅用作全局 IDF 参考语料(Gentzkow-Kelly-Taddy 2019 JEL §2.2 "full reference corpus" 语义)。⚠ 注释明确警告勿改用 14_news_with_ctx(它只含 is_fintech_news=True 子集会塌缩 IDF 区分度)。
- 逐篇打分语料: 优先 `14_news_with_ctx.parquet`(含 content_ctx/content_ss, 读后按 `is_fintech_news==True` 筛金科子集), 缺失则回退 `12_fintech_news.parquet`。
- 金科词典经 `core.text.ahocorasick.load_fintech_dict` 加载(与 stage 12 共享同一份)。

**处理步骤**:
1. **全局 DF (Module A)** `_compute_global_df_jieba`: 把词典全部关键词 `jieba.add_word` 注入, `_ensure_keywords_injected` 划分 matchable / unmatchable(历史语境: 旧 1506 词表有 6 词含空格/顿号 jieba 整词永不可命中; 现 607 词典 (2026-07-21 换血) 实测 0 特殊字符词, 机制不变, 实际剔除数由 `len(unmatchable)` 运行期计算 → 从权重宇宙剔除并 WARNING 披露)。在全量参考语料上按 **(标题,日期) 去重的唯一文档** 用 jieba 整词统计每个关键词的文档频率 DF 与 N_total(joblib `prefer='threads'` 并行, 分批 2000)。DF 语料列经 `_materialize_df_corpus_column` 在线物化 content_full(prepend_title) 与 TF 端同口径。
2. **综合权重 (Module B)** `_build_intensity_weights`:
   - 步骤A IDF: `raw_idf = log10(N_total/(1+df))` → 均值归一化 → Winsorize(默认 [1,99] 分位)。
   - 步骤B 语义纯度 (v3.14.0: 零本地模型, 走统一引擎 `_eng.embed_texts(spec)`): 用 co-primary spec(MAIN=Qwen/Qwen3-Embedding-8B 无后缀 / `_lg`=text-embedding-3-large) 各编码一遍关键词表(词表级一次性 ~607 词, LLMCache 穿透) → IDF 加权普通质心 `np.average(embeddings, axis=0, weights=idf)`(维度无关, 由 `emb.shape[1]` 驱动; 名为 "SIF" 实非 SIF, 无 a/(a+p(w)) 平滑与首主成分去除) → 各关键词对质心余弦 → min-max + floor(anisotropy_floor 默认 0.1) 重标定。
   - 步骤C: `W_i = IDF_i × CosSim_scaled_i` 预乘。
   - 数据退化守卫(DF 空 / IDF 均值≤0 / CosSim 全相同)统一 logger.error 披露降级为纯词频或纯 IDF, 防同名列静默漂移; **嵌入 API 硬失败(embed_texts 返回 None)不降级而回传 None** → main() 走 both-or-neither: 该 spec 三轨 score 全置 NaN(parity: 无后缀族 ⟺ `_lg` 族同损同有, 绝不留单边孤儿列)。
3. **逐文档打分 (Module C)** `_compute_intensity_scores`, 双重对数核公式:
   `Score_d = Σ_{i:TF>0} [(1 + ln(TF_{d,i})) / (1 + ln(L_d))] × W_i`
   - 防长文偏差(分母 1+ln(L_d))、防复读机刷分(对 TF 取对数)。
   - **二次熔断**: distinct 关键词数 < min_distinct_keywords_jieba(默认 2) → score=NaN, verified=False(NaN 在下游 bank-year 均值中自动剔除, 避免把未验证文章当零强度系统性拉低均值)。

**输出列**: `fintech_intensity_score_{full,ctx,ss}` + `intensity_verified_{full,ctx,ss}`, 加无后缀 `fintech_intensity_score` / `intensity_verified`(= _full 别名); v3.14.0 起另加 `_lg` co-primary 孪生族 `fintech_intensity_score_lg_{full,ctx,ss}` + `intensity_verified_lg_{full,ctx,ss}`(text-embedding-3-large, 与无后缀 Qwen 族严格 parity)。

**外部依赖/确定性**: jieba(整词分词, 注入态单源, 锁 jieba==0.42.1)、joblib 线程并行、统一引擎 `pipeline/text/embedding_engine.py::embed_texts`(关键词级语义权重经 co-primary 双 API 模型 Qwen + text-embedding-3-large 各算一遍, 词表级一次性 ~607 词, 经 LLMCache(_llm_cache.db) 穿透缓存; v3.14.0 起**零本地嵌入模型**, text2vec 已整体移除)。嵌入在线 miss 才付费调 API、命中即 $0(嵌入亦受 NEWS_PROCESS_LLM_OFFLINE 离线守卫: 设=1 时 miss 即 raise RuntimeError 零网络/$0, 与 stage 21 LLMCacheMissError 对称但异常类型不同; 裸环境须设 SSL_CERT_FILE=certifi 修 api.siliconflow.cn / yunwu.ai 证书); 确定性取决于 jieba 版本与嵌入 API 返回。配置节 = config/filtering.yaml::fintech_intensity + config/features.yaml::embedding_api / embedding_large (代码 CONFIG.get('fintech_intensity') / CONFIG.get('embedding_api') / CONFIG.get('embedding_large'))。

■ 白话说明

这一步给每篇'金融科技'新闻打一个连续的'技术含金量分数'。

打个比方: stage 12 只是判断一篇新闻'是不是'谈金融科技(是/否的开关); 这一步则进一步衡量它谈得'有多硬核'。它给每个金科关键词配一个'权重': 越稀有的词(很多文章不提的, 比如'联邦学习')权重越高, 越泛泛的词(篇篇都有的)权重越低; 同时还看这个词在语义上'是不是真的很金科'。然后把一篇文章里出现的关键词按权重加起来, 还特意做两件事: 长文章不会因为字多就自动得高分, 同一个词重复刷十遍也不会线性加分(防'复读机刷分')。如果一篇文章翻来覆去只提一两个孤立的金科词(很可能是顺带一提), 就判定为'没通过验证', 分数记为空缺而不是0, 免得把它当成'零强度'拖累整体平均。

为什么需要它: 后面要研究'银行对金融科技的关注/实质投入'到底强不强, 光数关键词容易被注水的稿件骗到。这个连续分数让'真干事'和'喊口号'能被区分开。

对最终面板/论文的影响: 这个分数(三条轨道的版本)会被聚合成银行-年度的平均金科强度, 直接进入 P2(注意力强度)等论文的核心解释变量。如果权重算偏了或验证门槛没把住, 银行的'金科活跃度'就会被高估或低估, 回归系数随之失真; 反过来, 做扎实了, 论文里'媒体对某银行金科报道越强 → 后续某结果'这类结论才站得住。
========================================================================
"""

import logging
import math
import multiprocessing
import os
import platform
import sys
import time

import jieba
import numpy as np
import pandas as pd

# v3.14.0 (2026-06-27): 移除 HF 离线 env (HF_HUB_OFFLINE/TRANSFORMERS_OFFLINE) —— 本阶段
# 已彻底拔掉本地 SentenceTransformer(text2vec) 词向量, 关键词语义权重改走统一引擎
# _eng.embed_texts(co-primary 双 API 模型), 不再加载任何本地 HF 模型 → 该离线 env 失效。

jieba.setLogLevel(logging.WARNING)

from collections import Counter

from joblib import Parallel, delayed

# Phase 7a-3: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import (
    log_memory_usage,
    log_stage_summary,
    pct4,
    setup_logging,
    sig4,
)
from news_process.core.reporting import save_dataset
from news_process.core.text.ahocorasick import load_fintech_dict
from news_process.pipeline.text import embedding_engine as _eng

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "15_fintech_intensity"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 读取技术重度评分配置 (config/filtering.yaml → fintech_intensity 节)
INTENSITY_CONFIG = CONFIG.get('fintech_intensity', {})
MIN_DISTINCT_KEYWORDS_JIEBA = INTENSITY_CONFIG.get('min_distinct_keywords_jieba', 2)
WINSORIZE_PERCENTILES = INTENSITY_CONFIG.get('winsorize_percentiles', [1, 99])
ANISOTROPY_FLOOR = INTENSITY_CONFIG.get('anisotropy_floor', 0.1)

# ── 嵌入 spec (v3.14.0: 零本地模型, 统一引擎 co-primary 双 API 模型) ──────────────
# 关键词级语义纯度权重 CosSim_scaled_i 改走统一引擎 _eng.embed_texts(spec=…), 不再用
# 本地 SentenceTransformer(text2vec)。两 spec 各嵌一遍 ~607 金科词表 (词表级一次性,
# 非逐文档), 互为 co-primary:
#   MAIN  = embedding_api    (Qwen/Qwen3-Embedding-8B, 无后缀) → fintech_intensity_score
#   _lg   = embedding_large  (text-embedding-3-large)             → fintech_intensity_score_lg
# both-or-neither: 任一 spec embed_texts 返回 None → 两个 score 族同置 NaN (不留单边孤儿列)。
# 质心/余弦数学全程维度无关 (np.average(emb, axis=0) 由 emb.shape[1] 驱动), 不假设 768/1536/3072/4096。
EMBEDDING_CONFIG = CONFIG.get('embedding_api', {})           # CO-PRIMARY ① (canonical, Qwen)
_LARGE_SPEC = CONFIG.get('embedding_large', {})              # CO-PRIMARY ② (_lg, text-embedding-3-large)
# 缓存库路径 (与 policy_alignment/benefit_society 同口径: 缺 llm_cache_db 键时回退 output_dir/_llm_cache.db)
CACHE_DB_PATH = CONFIG['paths'].get(
    'llm_cache_db', os.path.join(CONFIG['paths']['output_dir'], '_llm_cache.db'))

# 加载金融科技词典（与阶段 12 共享同一份词典）
FINTECH_KEYWORDS, _ = load_fintech_dict(CONFIG['paths'].get('fintech_dict_file', ''))
# fix(2026-07-24): 词典规模横幅只在主进程 emit — loky 进程后端 worker import 本模块时
# 也会执行模块级代码, worker 侧首条 logger 写入会触发本阶段 .log 的延迟截断 handler,
# NUL 填充 + 截掉主进程已写的环境/配置横幅 (2026-07-24 04:40 生产真跑实证: worker
# PID 29708 的横幅写入毁掉了 PID 22648 主进程的日志头)。判据 = multiprocessing
# parent_process() 主进程恒 None、任何 spawn/loky 子进程恒非 None (与 §1b "worker
# 绝不 log" 同一安全约束, 补齐 silent=True 之外遗漏的最后一处模块级写点)。
if multiprocessing.parent_process() is None:
    logger.info(f"金融科技词典: 共 {len(FINTECH_KEYWORDS)} 个词汇")

# fix(omni-g-fintech-03 组级裁决, 2026-06-11): jieba 注入态单源 — DF 与 TF 共用同一
# 注入 + 同一可匹配词集 (同分词器原则, 对齐 tone_words._get_tone_tokenizer 先例)。
# 历史语境: 旧 1506 词典中 6 词含空格/顿号 (如 'Open Banking' / '治理、风险与合规') 会被
# jieba 块切分正则在词典查找之前切开, jieba.add_word 注入也**永不可能**成为单 token
# ("注入" 路径技术不可行) → 按裁决走 "剔除 + 披露": 从权重宇宙 (IDF 归一化 / 质心 /
# CosSim 重标定) 剔除并 WARNING 披露, 避免 DF=0 的幻影词拉高 IDF 均值、扭曲质心与
# min-max 缩放 (TF 端 jieba 本就不可见这些词, 剔除不改任何单篇 TF 命中)。
# 白话: 个别带空格/顿号的关键词, jieba 分词器天生切不出来、文章里永远数不到它们;
# 如果还让它们参与算权重, 等于拿一批"永远命中 0 次的幽灵词"去拉偏所有词的权重,
# 所以干脆把它们从权重计算里踢掉, 并在日志里说明踢了哪些。
_KW_STATE: dict = {'injected': False, 'matchable': None, 'unmatchable': None}


def _ensure_keywords_injected(silent: bool = False) -> tuple:
    """注入全部关键词到 jieba 并划分可匹配/永不可匹配两类 (幂等, 进程内缓存)。

    Args:
        silent: True 时抑制 unmatchable 披露 warning。⚠ loky 进程后端 worker 必须传
            silent=True 调用 — worker 侧任何 logger 写入都会触发本阶段 .log 的
            ``_DelayedTruncatingRotatingHandler`` 首写截断, 毁掉主进程取证日志
            (与 stage 12 "worker 不写日志" 同一安全约束)。主进程调用 silent=False,
            unmatchable 披露恰好在主进程 emit 一次。

    Returns:
        tuple: (matchable: list[str], unmatchable: list[str])
    """
    if not _KW_STATE['injected']:
        for kw in FINTECH_KEYWORDS:
            jieba.add_word(kw)
        unmatchable = [kw for kw in FINTECH_KEYWORDS
                       if list(jieba.cut(kw)) != [kw]]
        _unmatch_set = set(unmatchable)
        matchable = [kw for kw in FINTECH_KEYWORDS if kw not in _unmatch_set]
        _KW_STATE['matchable'] = matchable
        _KW_STATE['unmatchable'] = unmatchable
        _KW_STATE['injected'] = True
        if unmatchable and not silent:
            logger.warning(
                f"⚠ 词典披露[fintech_intensity] (fix omni-g-fintech 组级, 2026-06-11): "
                f"{len(unmatchable)}/{len(FINTECH_KEYWORDS)} 个关键词含 jieba 块切分"
                f"边界字符 (空格/标点), 整词分词永不可命中, 已从 IDF/质心/CosSim "
                f"权重宇宙剔除 (TF 端本就不可见, 不影响单篇得分命中): {unmatchable}")
    return _KW_STATE['matchable'], _KW_STATE['unmatchable']


# ============================================================================
# 1b. jieba 分词并行 worker + 工况自适应后端 (perf fix 2026-07-24)
# ============================================================================
# 病根: jieba.cut 是纯 Python、持 GIL, 原 `Parallel(prefer='threads')` 在多核上退化
#   为单核 —— 生产 164 万篇全局 DF 分词曾耗时 1h48m (占 stage 15 墙钟 90%, 逼爆父端
#   7200s 超时)。对比 stage 11/12 走 loky 进程后端 (news_bank/news_fintech) 同规模语料
#   仅 5-6 分钟。
# 修法: 分词 worker 提升为模块级 (loky 需 pickle-by-ref) + 工况自适应后端:
#   · 大工况 (batch 数 >= _PROC_PARALLEL_MIN_BATCHES, 生产语料) → loky 进程后端, 真并行
#     绕过 GIL;
#   · 小工况 (测试 / 小样本) → 保持 threads, 免 Windows 进程 spawn 开销 + pytest 多进程
#     怪癖 (test_omni_fix_fintech 逐调直接命中)。
# 字节等价 (byte-equivalent-by-construction, 经 scripts/audit/verify 真数据 A/B 实证):
#   · worker 侧 silent 自注入 jieba (_ensure_keywords_injected(silent=True)) + 自算 kw_set
#     → 每个 loky worker 的 jieba 分词态与主进程逐字节一致 (jieba.cut 确定, 注入同序同集);
#   · DF = set(jieba.cut) & kw_set 的**整数**计数, 跨块 Counter 求和 order-independent →
#     n_jobs / 后端无关;
#   · TF = 逐 doc 独立 Counter (整数), loky 保持结果顺序 (按提交序返回) → 下游打分的
#     浮点求和 `score += (ln_tf/ln_L)*W` 在**主进程串行**执行、tf.items() 迭代序不变 →
#     逐字节一致 (与 sklearn LDA 那种 n_jobs 依赖的浮点切片累加**不同**, 本阶段并行段纯
#     整数、零浮点累加, 故后端切换零数值副作用)。
_PROC_PARALLEL_MIN_BATCHES = 16   # >= 16 批 (~3.2 万篇) 才切进程后端; 之下用线程


def _parallel_kwargs(num_batches: int) -> dict:
    """按工况规模选 joblib 后端: 大 → 进程 (绕 GIL 真并行); 小 → 线程 (免 spawn 开销)。

    两后端对本阶段分词输出严格字节等价 (见上方 §1b 论证), 仅影响墙钟, 不影响任何产物列。
    """
    if num_batches >= _PROC_PARALLEL_MIN_BATCHES:
        return {'n_jobs': -1, 'prefer': 'processes'}
    return {'n_jobs': -1, 'prefer': 'threads'}


def _df_chunk_worker(chunk_texts: list) -> Counter:
    """全局 DF 分块 worker (模块级, 供 loky 进程后端 pickle-by-ref)。

    worker 侧 **silent** 自注入 jieba + 自算 kw_set (进程后端每 worker 一份, 幂等缓存),
    使分词态与主进程逐字节一致; 绝不 logger 写入 (防 .log 延迟截断)。返回本块的
    {关键词: 命中该词的唯一文档数} 局部 Counter, 由调用方跨块求和 (order-independent)。
    """
    matchable, _ = _ensure_keywords_injected(silent=True)
    kw_set = set(matchable)
    local = Counter()
    for text in chunk_texts:
        local.update(set(jieba.cut(text)) & kw_set)
    return local


def _tokenize_chunk_worker(chunk_texts: list) -> list:
    """逐文档 TF 分块 worker (模块级, 供 loky 进程后端 pickle-by-ref)。

    同 _df_chunk_worker: worker 侧 silent 自注入 jieba + 自算 kw_set, 绝不 log。
    返回本块逐 doc 的 Counter(整词命中金科词); loky 按提交序保序返回 → 下游打分浮点
    求和顺序与线程后端逐字节一致。
    """
    matchable, _ = _ensure_keywords_injected(silent=True)
    kw_set = set(matchable)
    chunk_results = []
    for text in chunk_texts:
        tokens = list(jieba.cut(text))
        tf = Counter(t for t in tokens if t in kw_set)
        chunk_results.append(tf)
    return chunk_results


# ============================================================================
# 2. 全局文档频率解析 (Module A)
# ============================================================================

def _materialize_df_corpus_column(df_ref: pd.DataFrame) -> tuple:
    """为 DF 统计在线物化与 TF 同语义的语料列, 返回 (frame, 列名)。

    fix(omni-g-fintech-03, 2026-06-11): TF 打分文本 (full 轨) 是 content_full
    (= 标题 + 内容, stage 13 经 prepend_title 物化), 而 DF 参考语料
    12_fintech_news_full.parquet 无该列 → 此处用同一单一事实源 prepend_title
    在线物化 (逐字同口径), 使 DF 与 TF 同语料 (tone_words 2026-06-10 "IDF 在与
    TF 加权同一语料上统一计算" 先例; 否则标题词 df 被低估)。只进 DF 统计,
    不写盘。缺 '标题'/'内容' 列时回退 '内容' (与打分侧单轨退化路径同口径)。

    Returns:
        tuple: (df: pd.DataFrame, text_col: str)
    """
    if 'content_full' in df_ref.columns:
        return df_ref, 'content_full'
    if '标题' in df_ref.columns and '内容' in df_ref.columns:
        from news_process.core.text.entity_context import prepend_title
        titles = df_ref['标题'].fillna('').astype(str)
        bodies = df_ref['内容'].fillna('').astype(str)
        # .assign 浅拷贝其余列 (零数据复制), 不污染调用方 frame
        df_ref = df_ref.assign(
            content_full=[prepend_title(t, b) for t, b in zip(titles, bodies)])
        return df_ref, 'content_full'
    return df_ref, '内容'


def _compute_global_df_jieba(df_full: pd.DataFrame, text_col: str = '内容') -> tuple:
    """在全量参考语料上以 jieba 整词重算每个关键词的文档频率 (DF)。

    学术依据: Gentzkow, Kelly & Taddy (2019, JEL, §2.2):
      "IDF must be computed on the full reference corpus"

    fix(omni-g-fintech-03, 2026-06-11, P2): 旧实现 (_parse_global_df) 从 stage 12
      fintech_keyword_details 解析 DF — 该 DF 源自 AC 子串扫描, 允许子串误命中
      (如 '网贷' ∈ '互联网贷款') 与重叠双计 (如 '大数据'+'数据风控'), 而 TF 走
      jieba 整词 → 同一关键词两侧 "出现" 定义不同, DF 系统性偏大 → 子串高发
      关键词 IDF/权重系统性偏低, 违 GKT 同语料原则。tone_words.py 已为同一问题
      "坚决废除 Aho-Corasick 子匹配" (build_idf_weights), 本函数与其对齐:
      DF 与 TF 同分词器 (jieba 整词, 同注入态)、同语料列 (caller 传 content_full
      优先, 回退 '内容')。

    fix(omni-g-fintech-01, 2026-06-11, P3): DF 与 N_total 按**唯一文档**统计 —
      全量表每行 = (文章 × target_bank) 爆炸行 + 跨媒体转载 (盘上 4054 行 vs
      3646 唯一 (标题,日期)), 旧实现同一物理文档在 DF 分子与 N_total 分母中计
      k 次。现按 ['标题','日期'] 去重 (缺列回退文本内容自身为唯一键, 同
      tone_words fix omni-g-tonewords-04), 与 fintech_share 2026-06-10 确立的
      去重计数基对齐。

    Args:
        df_full: 全量参考语料 DataFrame（含非金融科技文档）。
        text_col: DF 统计语料列 — 与 TF 打分同列 (content_full 优先, 回退 '内容')。

    Returns:
        tuple: (keyword_doc_freq: Counter, N_total: int)
    """
    # 主进程注入 (幂等) + 一次 unmatchable 披露 warning; DF 分词走 _df_chunk_worker
    # (worker 侧 silent 自注入 + 自算 kw_set, 见 §1b), 故此处不再需要把 kw_set 传进 worker。
    _ensure_keywords_injected()

    if text_col not in df_full.columns:
        logger.warning(f"  DF 语料列 '{text_col}' 不存在, 回退至 '内容'")
        text_col = '内容'

    # 唯一文档去重 (g-fintech-01): (标题, 日期) 优先; 缺列回退文本自身为键
    if {'标题', '日期'}.issubset(df_full.columns):
        texts = (df_full.drop_duplicates(subset=['标题', '日期'])[text_col]
                 .fillna('').astype(str).tolist())
    else:
        texts = (df_full[text_col].fillna('').astype(str)
                 .drop_duplicates().tolist())

    N_total = len(texts)
    keyword_doc_freq = Counter()
    if N_total == 0:
        logger.info("全局 DF 解析完成: 0 篇唯一文档")
        return keyword_doc_freq, 0

    batch_size = 2000
    num_batches = max(1, (N_total - 1) // batch_size + 1)
    chunks = [texts[i * batch_size:(i + 1) * batch_size]
              for i in range(num_batches)]
    _pk = _parallel_kwargs(num_batches)
    logger.info(f"全局 DF (jieba 整词, 唯一文档语料): {N_total} 篇, {num_batches} 批次 "
                f"[joblib 后端={_pk['prefer']}]")
    results = Parallel(**_pk)(
        delayed(_df_chunk_worker)(chunk) for chunk in chunks
    )
    for local in results:
        keyword_doc_freq.update(local)

    logger.info(f"全局 DF 解析完成: {N_total} 篇唯一文档, "
                f"{len(keyword_doc_freq)} 个不同关键词")
    return keyword_doc_freq, N_total


# ============================================================================
# 3. 综合权重构建 (Module B)
# ============================================================================

def _build_intensity_weights(
    keyword_doc_freq: Counter,
    N_total: int,
    spec: dict | None = None,
) -> dict | None:
    """构建 IDF × CosSim 综合权重 (v3.14.0: 关键词语义编码改走统一引擎 spec)。

    步骤 A: 全局 IDF 计算 + 均值归一化 + Winsorization
    步骤 B: IDF 加权质心 + 各向异性重标定 —— 用 spec 经 _eng.embed_texts 嵌入关键词表
      (词表级一次性 ~607 词; 维度无关, np.average(emb, axis=0) 由 emb.shape[1] 驱动)
      (fix omni-g-fintech-02, 2026-06-11: 原称 "SIF 加权质心" 名实不符 — 无
      a/(a+p(w)) 频率权重、无首主成分去除, 实为 IDF 加权普通质心, 措辞已修正)
    步骤 C: 预乘综合权重

    fix(omni-g-fintech-03 组级裁决, 2026-06-11): 权重宇宙 = jieba 可匹配关键词
      (_ensure_keywords_injected 的 matchable 集)。永不可匹配的 6 个含空格/顿号
      关键词被剔除 — 它们 TF 端恒不可见, 留在宇宙内只会以 DF=0 的最大 IDF 拉高
      均值归一化分母、并把幻影向量混入质心与 CosSim min-max 缩放。

    Args:
        keyword_doc_freq: {关键词: 出现该词的文档数} (jieba 整词口径)。
        N_total: 全量唯一文档总数。
        spec: 嵌入模型 spec (默认 EMBEDDING_CONFIG = Qwen MAIN); 传 _LARGE_SPEC
            可构造 _lg co-primary 孪生权重。

    Returns:
        dict {关键词: 综合权重 (float)}; 当 embed_texts 硬失败返回 None 时回传 None
        (供 main() 走 both-or-neither: 任一 spec 失败则两族 score 同置 NaN)。
        DF 空 / IDF 均值≤0 / 余弦全相同等数据退化路径仍返回有效权重字典 (非 None),
        与 API 硬失败 (None) 语义区分。
    """
    spec = spec if spec is not None else EMBEDDING_CONFIG
    matchable, _ = _ensure_keywords_injected()
    if not keyword_doc_freq or N_total == 0:
        # 审计修复 (degradation F11): 升 ERROR — 同名 fintech_intensity_score
        # 此时由"语义加权"静默退化为纯词频, 列名不变, 下游回归无从察觉口径漂移
        # (R7 测量一致性). 全权重 1.0 的数值不可用于发表对比。
        logger.error("⚠ 口径降级[fintech_intensity]: DF 为空或文档数为零，"
                     "所有权重降级为 1.0 → 评分退化为纯词频, 与语义加权设计不一致, "
                     "勿用于发表/跨样本对比。")
        # fix(omni-g-fintech-03 组级): 降级宇宙同样限 matchable (不可匹配词无意义)
        return {kw: 1.0 for kw in matchable}

    # ── 步骤 A: 全局 IDF 计算 ──
    raw_idf = {}
    for kw in matchable:
        df_w = keyword_doc_freq.get(kw, 0)
        raw_idf[kw] = math.log10(N_total / (1 + df_w))

    values = list(raw_idf.values())
    mean_val = float(np.mean(values)) if values else 1.0
    if mean_val > 0:
        normed_idf = {w: v / mean_val for w, v in raw_idf.items()}
    else:
        # 审计修复 (degradation F11, 第5个同型支闭合): IDF 均值≤0 (绝大多数关键词
        # 近乎篇篇出现, 极小/退化样本可达) → 归一化 IDF 全塌缩为 1.0, IDF 维度静默
        # 失效, 评分退化。原先此支连 warning 都无 (可见性低于其余 4 支), 补 ERROR。
        logger.error("⚠ 口径降级[fintech_intensity]: IDF 均值≤0，归一化 IDF 全回退 1.0 "
                     "→ IDF 维度失效, 评分退化, 与设计不一致, 勿用于发表/跨样本对比")
        normed_idf = {w: 1.0 for w in raw_idf}

    normed_vals = np.array(list(normed_idf.values()))
    p_lo, p_hi = WINSORIZE_PERCENTILES
    if len(normed_vals) >= 2:
        p1 = float(np.percentile(normed_vals, p_lo))
        p99 = float(np.percentile(normed_vals, p_hi))
        idf_weights = {w: float(np.clip(v, p1, p99)) for w, v in normed_idf.items()}
    else:
        idf_weights = dict(normed_idf)

    logger.info(f"IDF 权重: mean={sig4(np.mean(list(idf_weights.values())))}, "
                f"std={sig4(np.std(list(idf_weights.values())))}")

    # ── 步骤 B: IDF 加权质心 + 各向异性重标定 ──
    # fix(omni-g-fintech-02, 2026-06-11): 原注释 "SIF 加权质心" 名实不符, 见模块
    # docstring Arora et al. (2017) 引用降格说明。
    # v3.14.0: 关键词语义编码改走统一引擎 _eng.embed_texts(spec) (零本地模型);
    # 词表级一次性嵌 ~607 金科词, 由 LLMCache 穿透 (model_id+文本+version 为键),
    # 跨 run 命中即 $0; 维度无关 (centroid/cosine 由 emb.shape[1] 驱动)。
    _kw_model = _eng.spec_model(spec) if spec else '(未配置)'
    kw_list = list(idf_weights.keys())
    logger.info(f"关键词语义编码: 统一引擎 embed_texts, model={_kw_model}, "
                f"{len(kw_list):,} 词 (词表级一次性, co-primary spec)")
    embeddings = _eng.embed_texts(
        kw_list, spec, cache_db_path=CACHE_DB_PATH,
        log_prefix=f"FintechIntensityKW[{_kw_model}]")

    if embeddings is None:
        # both-or-neither (v3.14.0): API 硬失败 (embed_texts 返回 None) — 不静默退化为
        # 纯 IDF (那会留下与另一 co-primary 不对称的口径), 而是回传 None 让 main()
        # 把本 spec 的全部 score 列置 NaN (parity: 两 co-primary 同损/同有)。
        logger.error(
            f"⚠ 嵌入硬失败[fintech_intensity]: embed_texts 返回 None "
            f"(model={_kw_model}) → 本 spec 权重不可构, 回传 None (main 将置该族 score=NaN, "
            "both-or-neither 保 co-primary parity, 勿降级为纯 IDF)")
        return None
    if embeddings.shape[0] != len(kw_list):
        # 形状契约失配 (引擎理应等长返回) — 同样按硬失败处理, 防错位质心。
        logger.error(
            f"⚠ 嵌入形状失配[fintech_intensity]: embed_texts 返回 {embeddings.shape[0]} 行, "
            f"期望 {len(kw_list)} (model={_kw_model}) → 回传 None (both-or-neither)")
        return None
    logger.info(f"  关键词嵌入形状: {embeddings.shape} (dim={embeddings.shape[1]}, 维度无关)")

    weights_arr = np.array([idf_weights[kw] for kw in kw_list])
    centroid = np.average(embeddings, axis=0, weights=weights_arr)

    centroid_norm = centroid / (np.linalg.norm(centroid) + 1e-10)
    emb_norms = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-10)
    cos_sims = emb_norms @ centroid_norm

    # ── 各向异性重标定 (min-max + floor; fix omni-g-fintech-02: 工程化 ad hoc
    #    处理, Ethayarajh 2019 仅为现象动机引用, 非该文提出的校准方法) ──
    min_sim, max_sim = float(cos_sims.min()), float(cos_sims.max())

    cos_sim_scaled = {}
    if max_sim > min_sim:
        for i, kw in enumerate(kw_list):
            scaled = ANISOTROPY_FLOOR + (1.0 - ANISOTROPY_FLOOR) * \
                     (cos_sims[i] - min_sim) / (max_sim - min_sim)
            cos_sim_scaled[kw] = float(scaled)
    else:
        # 审计修复 (degradation F11, 复核补全): 第 4 个同型降级支 — 全部关键词
        # 余弦相似度相同时 CosSim 亦塌缩为 1.0 (评分退化为纯 IDF), 升 ERROR 闭合。
        # 注: 此为数据退化 (非 API 硬失败) → 仍返回有效权重 (不走 both-or-neither None)。
        logger.error("⚠ 口径降级[fintech_intensity]: 所有关键词余弦相似度相同，"
                     "CosSim 权重回退为 1.0 → 评分退化为纯 IDF, 与语义加权设计不一致, "
                     "勿用于发表/跨样本对比")
        cos_sim_scaled = {kw: 1.0 for kw in kw_list}

    logger.info(f"CosSim 校准: min={sig4(min_sim)}, max={sig4(max_sim)}, "
                f"floor={sig4(ANISOTROPY_FLOOR)}")
    del embeddings

    # ── 步骤 C: 预乘综合权重 ──
    # fix(omni-g-fintech-03 组级): 宇宙限 matchable — 不可匹配词 TF 恒 0, 无需权重
    combined_weights = {}
    for kw in matchable:
        combined_weights[kw] = idf_weights.get(kw, 1.0) * cos_sim_scaled.get(kw, 1.0)

    sorted_weights = sorted(combined_weights.items(), key=lambda x: x[1], reverse=True)
    logger.info("综合权重 Top 20 (硬核词):")
    for kw, w in sorted_weights[:20]:
        logger.info(f"  {kw}: {sig4(w)} (IDF={sig4(idf_weights.get(kw, 0))}, "
                    f"CosSim={sig4(cos_sim_scaled.get(kw, 0))})")
    logger.info("综合权重 Bottom 20 (泛化词):")
    for kw, w in sorted_weights[-20:]:
        logger.info(f"  {kw}: {sig4(w)} (IDF={sig4(idf_weights.get(kw, 0))}, "
                    f"CosSim={sig4(cos_sim_scaled.get(kw, 0))})")

    return combined_weights


# ============================================================================
# 4. 逐文档得分计算 (Module C)
# ============================================================================

def _compute_intensity_scores(
    df: pd.DataFrame,
    combined_weights: dict,
    text_col: str = '内容',
) -> tuple:
    """计算每篇文档的技术重度得分 (v3.6.0 Plan E P4 B1: 支持多轨)。

    核函数（双重对数方程）:
      Score_d = Σ_{i: TF>0} [ (1 + ln(TF_{d,i})) / (1 + ln(L_d)) ] × W_i

    v3.6.0 升级:
      text_col 参数让同一函数可对 '内容' / 'content_ctx' / 'content_ss' 三种
      输入计算, 实现 fintech_intensity_score_{full,ctx,ss} 三轨。doc_length 仍按
      text_col 实际长度推算 (避免用全文长度归一化 ctx/ss 短文本)。

    Args:
        df: 金融科技子集 DataFrame。
        combined_weights: {关键词: 综合权重}。
        text_col: 文本列名 — '内容' (full 轨) / 'content_ctx' (ctx 轨) /
            'content_ss' (ss 轨, 银行+金科同句共现)。

    Returns:
        tuple: (scores: list[float], verified_flags: list[bool])
    """
    # fix(omni-g-fintech-03 组级, 2026-06-11): 注入走单源 helper, TF 匹配集与
    # DF 统计集 (_compute_global_df_jieba) 严格同一 (不可匹配词本就不可能命中)
    # 主进程注入 (幂等); TF 分词走 _tokenize_chunk_worker (worker 侧 silent 自注入 +
    # 自算 kw_set, 见 §1b), 此处不再需要把 kw_set 传进 worker。
    _ensure_keywords_injected()

    if text_col not in df.columns:
        # 缺失时回退到 '内容' (保证 ctx/ss 轨在 stage 13 未跑时不崩)
        logger.warning(f"  '{text_col}' 列不存在, 回退至 '内容' (单轨退化)")
        text_col = '内容'
    contents = df[text_col].fillna('').astype(str).tolist()

    batch_size = 2000
    n_docs = len(contents)
    num_batches = max(1, (n_docs - 1) // batch_size + 1)
    chunks = [contents[i * batch_size:(i + 1) * batch_size] for i in range(num_batches)]

    _pk = _parallel_kwargs(num_batches)
    logger.info(f"Jieba 并行分词: {n_docs} 篇, {num_batches} 批次 [joblib 后端={_pk['prefer']}]")
    parallel_results = Parallel(**_pk)(
        delayed(_tokenize_chunk_worker)(chunk) for chunk in chunks
    )

    all_tfs = []
    for chunk_res in parallel_results:
        all_tfs.extend(chunk_res)

    scores = []
    verified_flags = []

    # v3.6.0 P4 B1: doc_length 按 text_col 实际长度推算 (ctx/ss 短文本不能用全文长度)
    if text_col == '内容' and 'doc_length' in df.columns:
        doc_lengths = df['doc_length'].values
    else:
        doc_lengths = df[text_col].fillna('').str.len().clip(lower=1).values

    n_fused = 0

    for idx in range(n_docs):
        tf = all_tfs[idx]
        L_d = max(int(doc_lengths[idx]), 1)

        distinct = len(tf)

        if distinct < MIN_DISTINCT_KEYWORDS_JIEBA:
            # fix(omni-g-fintech 组级裁决, 2026-06-11): 二次熔断由零填改 NaN —
            # 旧 0.0 会计入下游 bank-year 均值分母 (encode.py avg_ft_intensity* /
            # attention_media mean_*), 把 "未通过验证" 的文章当 "零强度" 系统性
            # 拉低均值。NaN 在 pandas mean/std 聚合中自动剔除 (sum 仍视同 0,
            # ln_sum_* 语义不变); intensity_verified=False 标志保持不变。
            scores.append(float('nan'))
            verified_flags.append(False)
            n_fused += 1
            continue

        score = 0.0
        ln_L = 1.0 + math.log(L_d) if L_d > 1 else 1.0
        for kw, count in tf.items():
            if count > 0 and kw in combined_weights:
                ln_tf = 1.0 + math.log(count)
                score += (ln_tf / ln_L) * combined_weights[kw]

        scores.append(round(score, 6))
        verified_flags.append(True)

    logger.info(f"得分计算完成: {n_docs:,} 篇, 二次熔断降级: {n_fused:,} 篇 "
                f"({pct4(n_fused / max(n_docs, 1))})")

    valid_scores = [s for s, v in zip(scores, verified_flags) if v]
    if valid_scores:
        logger.info(f"得分分布 (verified=True): "
                    f"mean={sig4(np.mean(valid_scores))}, "
                    f"std={sig4(np.std(valid_scores))}, "
                    f"min={sig4(np.min(valid_scores))}, "
                    f"max={sig4(np.max(valid_scores))}, "
                    f"median={sig4(np.median(valid_scores))}")

    return scores, verified_flags


# ============================================================================
# 5. 主流程编排 (Module D)
# ============================================================================

def _log_environment_and_config(full_path: str, ctx_path: str,
                                filtered_path: str, output_path: str) -> None:
    """打印项目/环境信息 + 输入输出 + 运行配置 + 方法论引文 (日志富集, 2026-06-24)。

    目标 (用户要求"在日志文件中提供尽可能多的项目信息、运行期间信息和运行结果信息"):
    把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数、方法学出处"一次性落进
    日志, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 (golden-safe)。所有学术
    引文逐字取自经核验参考文献注册表 (Crossref/DataCite 真值), 含期刊卷(期):页 + DOI。
    """
    try:
        intensity_cfg_keys = sorted(INTENSITY_CONFIG.keys()) if INTENSITY_CONFIG else []

        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (金融科技技术重度评分, STAGES_MAIN 阶段15; 三轨 full/ctx/ss)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) v3.16.0")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        logger.info(f"     · jieba:    {getattr(jieba, '__version__', '?')} (冻结锚点 0.42.1; "
                    "确定性来源=jieba版本 + 关键词嵌入 API 向量)")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "本阶段 jieba+joblib 线程 + 关键词级 co-primary 双 API 嵌入 "
                    "(Qwen + text-embedding-3-large; LLMCache 命中即 $0)")

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · IDF 参考语料 (stage 12 全量): {full_path}")
        logger.info(f"     · 打分语料 (优先 stage 13): {ctx_path}")
        logger.info(f"     · 打分语料回退 (stage 12 子集): {filtered_path}")
        logger.info(f"     · 输出: {output_path}")
        logger.info("     · 金科词典: core.text.ahocorasick.load_fintech_dict (与 stage 12 共享同一份)")

        logger.info("  ⚙ 运行配置 (config/filtering.yaml::fintech_intensity + config/features.yaml::embedding_api/embedding_large)")
        _main_kw_model = _eng.spec_model(EMBEDDING_CONFIG) if EMBEDDING_CONFIG else '(未配置)'
        _lg_kw_model = _eng.spec_model(_LARGE_SPEC) if _LARGE_SPEC else '(未配置)'
        logger.info(f"     · 关键词嵌入 co-primary 双 API 模型 (词表级语义纯度权重, 非文章嵌入): "
                    f"MAIN(无后缀)={_main_kw_model} | _lg={_lg_kw_model}")
        logger.info(f"     · 二次熔断阈值 MIN_DISTINCT_KEYWORDS_JIEBA={MIN_DISTINCT_KEYWORDS_JIEBA:,} "
                    "(distinct 金科词 < 此值 → score=NaN, verified=False)")
        logger.info(f"     · Winsorize 分位 WINSORIZE_PERCENTILES={WINSORIZE_PERCENTILES} "
                    f"| 各向异性下限 ANISOTROPY_FLOOR={sig4(ANISOTROPY_FLOOR)}")
        logger.info(f"     · 金科词典规模: {len(FINTECH_KEYWORDS):,} 个词汇 "
                    f"| 并行 n_jobs=-1 (joblib 自适应: >= {_PROC_PARALLEL_MIN_BATCHES} 批走"
                    "进程后端绕 GIL, 之下走线程), batch_size=2000")
        logger.info(f"     · 完整配置键: {intensity_cfg_keys}")

        logger.info("  📖 方法论依据 (引文逐字取自经核验注册表; 中文白话=本阶段为何用该方法)")
        logger.info("     · IDF 在全量参考语料上统一计算 (full reference corpus):")
        logger.info("       Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. "
                    "Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020")
        logger.info("       → 越稀有的金科词区分度越高: IDF 给罕见术语加权、压低篇篇出现的泛词")
        logger.info("     · TF-IDF 词项加权的理论基础:")
        logger.info("       Salton, G., & Buckley, C. (1988). Term-weighting approaches in automatic "
                    "text retrieval. Information Processing & Management, 24(5), 513-523. "
                    "https://doi.org/10.1016/0306-4573(88)90021-0")
        logger.info("       → 对 TF 取对数 (1+ln(TF)) 防同词重复刷分, 分母 1+ln(L) 防长文偏差")
        logger.info("     · 文档长度归一化 / IDF 计算范式:")
        logger.info("       Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to "
                    "information retrieval. Cambridge University Press. "
                    "https://doi.org/10.1017/CBO9780511809071")
        logger.info("       → 长文不会因字数多就自动得高分 (Ch 6.4 文档长度偏差校正)")
        logger.info("     · 金融文本词典/术语区分度缺失问题:")
        logger.info("       Loughran, T., & McDonald, B. (2011). When is a liability not a liability? "
                    "Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. "
                    "https://doi.org/10.1111/j.1540-6261.2010.01625.x")
        logger.info("       → 泛用词典在金融语境失真, 故叠加语义纯度权重区分'硬核词'与'泛化词'")
        logger.info("     · 复读机刷分 (cheap talk / cherry-picking) 防御:")
        logger.info("       Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk "
                    "and cherry-picking: What ClimateBert has to say on corporate climate risk "
                    "disclosures. Finance Research Letters, 47, 102776. "
                    "https://doi.org/10.1016/j.frl.2022.102776")
        logger.info("       → 翻来覆去喊口号不应线性加分, 对 TF 取对数压制注水稿件")
        logger.info("     · 关键词级语义编码 (统一引擎 co-primary 双 API 嵌入, v3.14.0 起零本地模型):")
        logger.info("       Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using "
                    "Siamese BERT-networks. In Proceedings of the 2019 Conference on Empirical Methods "
                    "in Natural Language Processing and the 9th International Joint Conference on Natural "
                    "Language Processing (EMNLP-IJCNLP) (pp. 3980-3990). Association for Computational "
                    "Linguistics. https://doi.org/10.18653/v1/D19-1410")
        logger.info("       → 用句向量模型给每个金科词取语义向量, 对质心余弦度量其'语义纯度' "
                    "(现走 Qwen + text-embedding-3-large 两 API 模型各算一遍, 互为 co-primary)")
        logger.info("     · 银行金融科技测度 (本任务直接对标的中文研究):")
        logger.info("       胡俊, 李强, 戴嘉诚, & 曾勇. (2024). 基于文本分析的商业银行金融科技测度及赋能效果检验. "
                    "中国管理科学, 32(1), 31-41. "
                    "https://doi.org/10.16381/j.cnki.issn1003-207x.2021.1714")
        logger.info("       → 用文本关键词构造银行金科强度, 与本阶段连续型 intensity 测度同源")
        logger.info("     · 近期 firm-level 文本暴露测度范式 (2023-2026, 关键词命中 + 嵌入加权):")
        logger.info("       Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R. (2023). Firm-level "
                    "climate change exposure. The Journal of Finance, 78(3), 1449-1498. "
                    "https://doi.org/10.1111/jofi.13219")
        logger.info("       → ML 关键词发现 + 二元组命中构 firm-level exposure, 本阶段金科词表/命中计数同范式模板")
        logger.info("       Wu, D. (A.). (2024). Text-based measure of supply chain risk exposure. "
                    "Management Science, 70(7), 4781-4801. https://doi.org/10.1287/mnsc.2023.4927")
        logger.info("       → 种子词嵌入 + 词袋构 firm-level 文本暴露 (并以波动率验证), 与本阶段"
                    "IDF 加权关键词质心 + jieba 整词计数同法, 2024 近期实例")
        logger.info("       Kalyani, A., Bloom, N., Carvalho, M., Hassan, T. A., Lerner, J., & "
                    "Tahoun, A. (2025). The diffusion of new technologies. The Quarterly Journal "
                    "of Economics, 140(2), 1299-1365. https://doi.org/10.1093/qje/qjaf002")
        logger.info("       → 文本 bigram 识别新兴技术并追踪扩散, 支撑'锚定金科技术词命中作技术关注强度'设计")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法论信息打印失败 (不影响处理): {e}")


def main():
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")
    log_memory_usage(logger, "阶段启动")

    # 功能说明 banner — 写入 <stage>.log, 让日志自带阶段用途说明 (仿 39c/13)。
    logger.info("=" * 72)
    logger.info("阶段 15: 金融科技技术重度评分 (TF-IDF + IDF 加权关键词质心, 三轨 full/ctx/ss)")
    logger.info("=" * 72)
    logger.info("【功能】给每篇'金融科技'新闻打一个连续的'技术含金量分数' fintech_intensity_score —")
    logger.info("        在 stage 12 二元'是不是金科'判定之上, 进一步衡量它谈得'有多硬核'。")
    logger.info("        产出三轨 fintech_intensity_score_{full,ctx,ss} + intensity_verified_{full,ctx,ss},")
    logger.info("        下游聚合为银行-年度平均金科强度, 直接进入 P2(注意力强度)等论文核心解释变量。")
    logger.info("【方法】双重对数核公式 Score_d = Σ_{i:TF>0} [(1+ln(TF_d,i)) / (1+ln(L_d))] × W_i,")
    logger.info("        其中 W_i = IDF_i × CosSim_scaled_i (越稀有+语义越纯的金科词权重越高)。")
    logger.info(f"        分母 1+ln(L_d) 防长文偏差; 对 TF 取对数防'复读机刷分'; distinct 关键词 "
                f"< {MIN_DISTINCT_KEYWORDS_JIEBA} → 二次熔断 score=NaN(不计入下游均值)。")
    logger.info("【判读】分数越高 = 技术含金量越硬核; verified=True 占比越高 = 越多文章通过验证门槛。")
    logger.info("        三轨分歧(full vs ctx vs ss)越大 = ss/ctx 带来越独立的聚焦信号(支撑三轨稳健性)。")
    logger.info("【确定性】jieba 整词 + joblib 线程并行 (CPU) + 关键词级 co-primary 双 API 嵌入 "
                "(Qwen 无后缀 + text-embedding-3-large _lg; 词表级一次性 ~607 词, LLMCache 穿透)。"
                "嵌入在线 miss 才付费, 命中即 $0; 离线(NEWS_PROCESS_LLM_OFFLINE=1) miss 即 "
                "raise RuntimeError 零网络; 确定性取决于 jieba==0.42.1 与嵌入 API 返回。")

    # 运行期阶段计时累计 (各主要子阶段墙钟耗时, 末尾汇总打印; 仅服务于日志)
    phase_durations: dict[str, float] = {}

    output_dir = CONFIG['paths']['output_dir']

    full_filename = CONFIG['filenames'].get('output_12_fintech_full', '12_fintech_news_full.parquet')
    full_path = os.path.join(output_dir, full_filename)

    filtered_filename = CONFIG['filenames'].get('output_12_fintech_news', '12_fintech_news.parquet')
    filtered_path = os.path.join(output_dir, filtered_filename)
    ctx_filename = CONFIG['filenames'].get(
        'output_13_news_with_ctx', '14_news_with_ctx.parquet')
    ctx_path = os.path.join(output_dir, ctx_filename)
    output_filename = CONFIG['filenames'].get(
        'output_14_fintech_intensity', '15_fintech_intensity.parquet')
    output_path = os.path.join(output_dir, output_filename)

    # 项目/环境信息 + 输入输出 + 运行配置 + 方法论引文 (日志富集 2026-06-24)
    _log_environment_and_config(full_path, ctx_path, filtered_path, output_path)

    if not os.path.exists(full_path):
        logger.error(f"全量分类结果文件未找到: {full_path}")
        logger.error("请确保阶段 12 已执行且生成了全量输出文件。")
        raise SystemExit(1)

    # fix(omni-g-fintech-03, 2026-06-11): IDF 参考语料 = stage 12 全量 (含非金融科技
    # 文档, GKT "full reference corpus" 语义) — ⚠ 勿改用 14_news_with_ctx: 盘上实证
    # 其仅含 is_fintech_news=True 子集 (1170/4054 行), 用它会把参考语料塌缩为命中
    # 子集、摧毁 IDF 区分度。语料列与 TF 同语义: 在线物化 content_full (= 标题 +
    # 内容, prepend_title 单一事实源, 与 stage 13 物化口径逐字一致), 只进 DF 统计
    # 不写盘。DF 以 jieba 整词重算 (_compute_global_df_jieba), 不再消费 AC 子串计数。
    logger.info(f"加载 IDF 参考语料 (stage 12 全量): {full_path}")
    _t = time.time()
    df_ref = pd.read_parquet(full_path)
    df_ref, ref_text_col = _materialize_df_corpus_column(df_ref)
    keyword_doc_freq, N_total = _compute_global_df_jieba(df_ref, text_col=ref_text_col)
    del df_ref
    phase_durations['①全局DF解析(jieba整词)'] = time.time() - _t
    log_memory_usage(logger, "全量 DF 解析后(已释放)")

    # ── ② 综合权重构建 (IDF×CosSim) — co-primary 双 API 模型 (v3.14.0) ──
    # MAIN (Qwen, 无后缀) + _lg (text-embedding-3-large) 各构一套权重 (词表级一次性嵌)。
    # both-or-neither (parity 铁律): 任一 spec 的 embed_texts 硬失败 (_build 返回 None)
    # → 两族 score 列全置 NaN, 绝不留单边孤儿列。_LARGE_SPEC 缺失 (config 未配 embedding_large)
    # 时退化为单 MAIN (与其余 producer "config 缺块退化" 同口径)。
    _t = time.time()
    combined_weights = _build_intensity_weights(keyword_doc_freq, N_total, spec=EMBEDDING_CONFIG)
    combined_weights_lg = (
        _build_intensity_weights(keyword_doc_freq, N_total, spec=_LARGE_SPEC)
        if _LARGE_SPEC else None)

    # both-or-neither: MAIN 或 _lg 任一硬失败 (None) → 两族同时作废 (置 NaN)。
    # (_LARGE_SPEC 未配置时 combined_weights_lg=None 是"无 _lg 轨"语义, 不触发 both-or-neither;
    #  仅当 _LARGE_SPEC 已配置但 embed_texts 硬失败才连坐 MAIN。)
    _lg_enabled = bool(_LARGE_SPEC)
    if combined_weights is None or (_lg_enabled and combined_weights_lg is None):
        logger.error(
            "⚠ both-or-neither[fintech_intensity]: co-primary 至少一轨嵌入硬失败 "
            f"(MAIN={'OK' if combined_weights is not None else 'FAIL'}, "
            f"_lg={'OK' if combined_weights_lg is not None else ('FAIL' if _lg_enabled else 'N/A')}) "
            "→ 两族 fintech_intensity_score 列全置 NaN (parity 保护, 勿单边落列)")
        combined_weights = None
        combined_weights_lg = None
    phase_durations['②综合权重构建(IDF×CosSim, co-primary 双 API)'] = time.time() - _t

    # 存在性 gate: 校验 stage 12 原始金科子集仍在盘。2026-06-15 插入 stage 12b
    # (邻近共现硬过滤) 后, 12_fintech_news.parquet 仍由 stage 12 产出 (12b 只读它、
    # 不删) → 本 gate 照常通过; 真正的【打分语料】走下方 stage 13 输出 (已是 12b
    # 过滤后物化的子集, 故评分天然继承 12b)。仅当 stage 13 输出缺失才回退读此文件
    # (degraded 模式, 会绕过 12b; 全量 run 下 stage 13 always-on, 不触发)。
    if not os.path.exists(filtered_path):
        logger.error(f"金融科技子集文件未找到: {filtered_path}")
        raise SystemExit(1)

    # v3.6.0 (Plan E P4 A1/B1): 优先读 stage 13 输出 (含 content_ctx 列; 2026-06-15
    # 起 stage 13 读 12b 输出 → 此处 df 已是 12b 邻近共现过滤后子集, 评分继承过滤),
    # 缺失则 fallback 到 stage 12 输出 (无 ctx, 触发 _ctx 轨回退; 且绕过 12b)
    _t = time.time()
    if os.path.exists(ctx_path):
        logger.info(f"加载 stage 13 输出 (含 content_ctx): {ctx_path}")
        df = pd.read_parquet(ctx_path)
        # stage 13 现读 stage 12b 输出 (= 12_fintech_news 经邻近共现硬过滤, 本就是
        # is_fintech_news==True 金科子集) → 下面这道筛选自 2026-06-15 起为防御性恒真
        # no-op, 保留仅作 schema 兼容 (旧产物可能含非金科行时仍正确)。
        if 'is_fintech_news' in df.columns:
            df = df[df['is_fintech_news'].astype(bool)].reset_index(drop=True)
            logger.info(f"  筛选 is_fintech_news=True: {len(df)} 篇")
    else:
        logger.warning(f"  stage 13 输出未找到 ({ctx_path}), fallback 至 stage 12 "
                       f"(ctx 轨将退化为 full)")
        logger.info(f"加载金融科技子集: {filtered_path}")
        df = pd.read_parquet(filtered_path)
    phase_durations['③打分语料加载'] = time.time() - _t
    logger.info(f"金融科技子集: {len(df)} 篇文档")

    _t = time.time()
    # v3.6.0 (Plan E P4 B1): 三轨计算 — full 用 content_full (回退 '内容'),
    # ctx 用 'content_ctx', ss 用 'content_ss' (银行+金科同句共现, 回退镜像 ctx→全文 body)
    # 输出列: fintech_intensity_score{suffix}_{full,ctx,ss} + intensity_verified{suffix}_{full,ctx,ss}
    #   suffix='' → MAIN(Qwen, canonical 无后缀); suffix='_lg' → co-primary text-embedding-3-large
    # 向后兼容: MAIN 同时保留无后缀 fintech_intensity_score = _full alias
    # P1 修复 (metric-audit 2026-06-02, 病根A): full 轨改读 content_full (含标题), 与
    # ctx 轨 (content_ctx) 对称; 缺列回退 '内容' (_compute_intensity_scores 内亦有兜底).
    _full_col = 'content_full' if 'content_full' in df.columns else '内容'
    _n_rows = len(df)
    _nan_scores = [float('nan')] * _n_rows
    _false_verified = [False] * _n_rows

    def _score_one_track(weights, text_col: str):
        """对单轨算分; weights=None (both-or-neither 失败) → 全 NaN/False。"""
        if weights is None:
            return list(_nan_scores), list(_false_verified)
        return _compute_intensity_scores(df, weights, text_col=text_col)

    def _emit_spec_three_tracks(weights, suffix: str) -> None:
        """对一个 co-primary spec 算三轨并落列 (suffix='' = MAIN; '_lg' = large)。

        weights=None (该 spec 嵌入硬失败 / both-or-neither 连坐) → 三轨全 NaN/False,
        但**列仍落齐** (parity: schema 层无后缀族 ⟺ _lg 族列名双射, 值可 NaN)。
        """
        _tag = "MAIN(Qwen, 无后缀)" if suffix == '' else f"CO-PRIMARY(text-embedding-3-large, {suffix})"
        logger.info("=" * 60)
        logger.info(f"co-primary 三轨打分 [{_tag}]: fintech_intensity_score{suffix}_{{full,ctx,ss}}")
        logger.info("=" * 60)

        # full 轨 (content_full, 回退 '内容')
        s_full, v_full = _score_one_track(weights, _full_col)
        df[f'fintech_intensity_score{suffix}_full'] = s_full
        df[f'intensity_verified{suffix}_full'] = v_full

        # ctx 轨 (content_ctx; 缺列回退 = full)
        if 'content_ctx' in df.columns:
            s_ctx, v_ctx = _score_one_track(weights, 'content_ctx')
        else:
            logger.warning(
                f"  [{_tag}] content_ctx 列缺失 (stage 13 _materialize_ctx 未跑?), "
                f"ctx 轨回退 = full — fintech_intensity_score{suffix}_ctx ≡ _full")
            s_ctx, v_ctx = s_full, v_full
        df[f'fintech_intensity_score{suffix}_ctx'] = s_ctx
        df[f'intensity_verified{suffix}_ctx'] = v_ctx

        # ss 轨 (content_ss, 银行+金科同句共现; 缺列回退 = full)
        if 'content_ss' in df.columns:
            s_ss, v_ss = _score_one_track(weights, 'content_ss')
        else:
            logger.warning(
                f"  [{_tag}] content_ss 列缺失 (stage 13 ss 物化未跑?), "
                f"ss 轨回退 = full — fintech_intensity_score{suffix}_ss ≡ _full")
            s_ss, v_ss = s_full, v_full
        df[f'fintech_intensity_score{suffix}_ss'] = s_ss
        df[f'intensity_verified{suffix}_ss'] = v_ss

        # MAIN 历史无后缀别名 (= _full; 待各论文迁移到 _full/_ctx 列后弃用)。仅 MAIN 落别名。
        if suffix == '':
            df['fintech_intensity_score'] = s_full
            df['intensity_verified'] = v_full

    # MAIN (Qwen) — 必落 (无后缀 canonical 族 + 别名)
    _emit_spec_three_tracks(combined_weights, '')
    # _lg co-primary (text-embedding-3-large) — 仅当 config 配了 embedding_large 才落列。
    # both-or-neither 已保证: 若 MAIN 与 _lg 任一硬失败, 两套 weights 均为 None → 两族全 NaN。
    if _lg_enabled:
        _emit_spec_three_tracks(combined_weights_lg, '_lg')
    phase_durations['④三轨逐文档打分(full/ctx/ss × co-primary)'] = time.time() - _t

    # 取 MAIN full 轨 verified 标志供下方诊断计数 (历史变量名沿用)
    verified_full = df['intensity_verified_full'].tolist()

    assert 'is_fintech_news' in df.columns, "原有列 is_fintech_news 丢失!"
    assert 'fintech_intensity_score' in df.columns
    assert 'fintech_intensity_score_full' in df.columns
    assert 'fintech_intensity_score_ctx' in df.columns
    assert 'fintech_intensity_score_ss' in df.columns
    assert 'intensity_verified' in df.columns
    if _lg_enabled:
        # parity 自检: _lg 三轨列必与无后缀族双射落齐 (值可 NaN, 列名不可缺)
        for _trk in ('full', 'ctx', 'ss'):
            assert f'fintech_intensity_score_lg_{_trk}' in df.columns, \
                f"co-primary parity 破: 缺 fintech_intensity_score_lg_{_trk} 孪生列"
            assert f'intensity_verified_lg_{_trk}' in df.columns

    # 使用数据版本控制保存
    _t = time.time()
    # P1→P2 fix (2026-06-26): 把真实主打分语料纳入血缘 (与 stage 13/14/16 "读=记" 约定一致)。
    # 上方 df 优先读 ctx_path(=stage13 输出, 真实评分行源), 缺失才 fallback filtered_path;
    # full_path 仅作 IDF 参考语料。原 input_files 漏掉主源 ctx_path, 致 --skip-unchanged 内容门
    # 对 14_news_with_ctx 变更失明 (stage15-only 分跑静默陈旧窗口)。
    _primary_src = ctx_path if os.path.exists(ctx_path) else filtered_path
    save_dataset(
        df=df,
        output_path=output_path,
        logger=logger,
        stage_name="15_fintech_intensity",
        config=CONFIG,
        input_files=[full_path, _primary_src],
    )
    phase_durations['⑤写盘(save_dataset)'] = time.time() - _t

    n_verified_full = sum(verified_full)
    n_verified_ctx = sum(df['intensity_verified_ctx'])
    n_verified_ss = sum(df['intensity_verified_ss'])
    n_total = len(df)
    logger.info(f"intensity_verified_full=True: {n_verified_full:,}/{n_total:,} "
                f"({pct4(n_verified_full / max(n_total, 1))})")
    logger.info(f"intensity_verified_ctx=True:  {n_verified_ctx:,}/{n_total:,} "
                f"({pct4(n_verified_ctx / max(n_total, 1))})")
    logger.info(f"intensity_verified_ss=True:   {n_verified_ss:,}/{n_total:,} "
                f"({pct4(n_verified_ss / max(n_total, 1))})")

    # ── 结果分析 (仿 39c): 把真实算出的产出指标逐个打印 + 对照阈值/预期方向给判读 ──
    # 仅用于日志, 不回写 df / 不改任何产物 (golden-safe 纯增量)。本块整体在 save_dataset
    # 之后执行 (产物已落盘), 但仍 try/except 兜底: 即便诊断计算抛异常 (如缺列 KeyError /
    # 空 Series 统计) 也只打 WARNING、绝不让阶段崩溃丢已写产物 (crash-guard)。
    try:
        _verif_rate_full = n_verified_full / max(n_total, 1)
        _verif_rate_ctx = n_verified_ctx / max(n_total, 1)
        _verif_rate_ss = n_verified_ss / max(n_total, 1)
        # verified=True 行的得分分布 (NaN 自动剔除, 与下游 bank-year mean 同口径)。
        # 三列在上方三轨分支中必被赋值 (缺 content 列时回退 = full), 故 column-guard 下
        # 仍兜底用 .get-式存在判断, 缺列则记 None 并给"全 NaN"路径 (双保险)。
        def _coerce(_col):
            return pd.to_numeric(df[_col], errors='coerce') if _col in df.columns else None
        _sc_full = _coerce('fintech_intensity_score_full')
        _sc_ctx = _coerce('fintech_intensity_score_ctx')
        _sc_ss = _coerce('fintech_intensity_score_ss')

        # NaN-guard: 全 NaN / 缺列 → mean=NaN, 不落进任何数值方向判断
        def _safe_mean(_s):
            if _s is None or _s.notna().sum() == 0:
                return float('nan')
            return float(np.nanmean(_s))
        _mean_full = _safe_mean(_sc_full)
        _mean_ctx = _safe_mean(_sc_ctx)
        _mean_ss = _safe_mean(_sc_ss)
        # 三轨是否真正分歧 (是否退化为 ≡ full): ctx/ss 与 full 列是否逐元素相等
        _ctx_distinct = (_sc_ctx is not None and _sc_full is not None
                         and not _sc_ctx.equals(_sc_full))
        _ss_distinct = (_sc_ss is not None and _sc_full is not None
                        and not _sc_ss.equals(_sc_full))
        # 权重宇宙规模 (matchable 关键词数) + 区分度: 综合权重的离散程度
        _w_vals = (np.array(list(combined_weights.values()), dtype=float)
                   if combined_weights else np.array([]))
        _w_mean = float(np.mean(_w_vals)) if _w_vals.size else float('nan')
        _w_std = float(np.std(_w_vals)) if _w_vals.size else float('nan')

        logger.info("-" * 72)
        logger.info("【结果分析】技术重度评分质量解读:")
        logger.info(f"  IDF 参考语料: N_total={N_total:,} 篇唯一文档, "
                    f"命中 {len(keyword_doc_freq):,} 个不同金科关键词 (jieba 整词口径)")
        # both-or-neither: combined_weights 可能为 None (co-primary 嵌入硬失败 → 全 NaN)
        _n_weights = len(combined_weights) if combined_weights else 0
        logger.info(f"  综合权重宇宙: {_n_weights:,} 个可匹配关键词, "
                    f"W mean={sig4(_w_mean)}, std={sig4(_w_std)}")
        # NaN-guard: _w_std 为 NaN (空权重) 时不进 ">0" 方向判读, 单列降级提示
        if not np.isfinite(_w_std):
            logger.info("    → ⚠ 权重宇宙为空 (combined_weights 为空), 评分将全部熔断/降级, 见上方口径降级日志")
        elif _w_std > 0:
            logger.info("    → 权重有区分度 (std>0), 稀有/语义纯的硬核词与泛化词被有效拉开")
        else:
            logger.info("    → ⚠ 权重几乎无区分度 (std≈0), 评分可能已降级为纯词频/纯 IDF, 见上方口径降级日志")
        logger.info(f"  full 轨 verified=True: {n_verified_full:,}/{n_total:,} "
                    f"({pct4(_verif_rate_full)}), 通过验证文章 mean score={sig4(_mean_full)}")
        logger.info("    → " + ("验证通过率健康, 多数金科文章含 ≥2 个 distinct 金科词, 强度信号可用"
                                if _verif_rate_full >= 0.50 else
                                "⚠ 验证通过率偏低, 大量文章仅孤立提及 1 个金科词 → 被熔断为 NaN "
                                "(核查 stage 12 关键词判定是否过宽 / 语料是否多顺带一提)"))
        # column-guard: ss 缓存常未播种 → content_ss 缺列时 ss 轨退化为 full, 据实标注
        if _sc_ctx is None:
            logger.info(f"  ctx 轨: 列 fintech_intensity_score_ctx 缺失, 跳过 (verified={n_verified_ctx:,})")
        else:
            logger.info(f"  ctx 轨 verified=True: {n_verified_ctx:,}/{n_total:,} ({pct4(_verif_rate_ctx)}), "
                        f"mean score={sig4(_mean_ctx)}, 独立于 full: {_ctx_distinct}")
        if _sc_ss is None:
            logger.info(f"  ss  轨: 列 fintech_intensity_score_ss 缺失, 跳过 (verified={n_verified_ss:,})")
        else:
            logger.info(f"  ss  轨 verified=True: {n_verified_ss:,}/{n_total:,} ({pct4(_verif_rate_ss)}), "
                        f"mean score={sig4(_mean_ss)}, 独立于 full: {_ss_distinct}")
        if _sc_ctx is not None and not _ctx_distinct:
            logger.warning("  ⚠ ctx 轨得分逐元素 ≡ full → content_ctx 列缺失或全回退 "
                           "(stage 13 _materialize_ctx 未跑?), ctx 轨此次不提供独立信号")
        if _sc_ss is not None and not _ss_distinct:
            logger.warning("  ⚠ ss 轨得分逐元素 ≡ full → content_ss 列缺失或全回退 "
                           "(stage 13 ss 物化未跑?), ss 轨此次不提供独立信号")
        if _ctx_distinct and _ss_distinct:
            logger.info("    → 三轨得分互不相同, full/ctx/ss 各自携带独立的文本聚焦视角 (支撑三轨稳健性设计)")
        if n_total < 5000:
            logger.info(f"  ⚠ 金科子集行数偏少 ({n_total:,}), 多为盘面小样本 (如早期试跑 T=2): "
                        "上述率/分布仅供验证管道正确性, 全量结论以 约1,819万/T=19 实测为准")
        logger.info("-" * 72)
    except Exception as _e:
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")

    # ── ⏱ 阶段计时 (各主要子阶段墙钟耗时; 仅服务于日志, golden-safe) ──
    try:
        logger.info("  ⏱ 阶段计时 (各子阶段墙钟耗时, 秒)")
        _phase_total = sum(phase_durations.values()) if phase_durations else 0.0
        for _name, _dur in phase_durations.items():
            _pct = (_dur / _phase_total) if _phase_total > 0 else float('nan')
            logger.info(f"     · {_name}: {sig4(_dur)} 秒 ({pct4(_pct)})")
        logger.info(f"     · 计时子阶段合计: {sig4(_phase_total)} 秒")
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  阶段计时打印失败 (不影响产物): {_e}")

    log_stage_summary(logger, STAGE_NAME, stage_start, n_total, n_total)
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


if __name__ == "__main__":
    main()
