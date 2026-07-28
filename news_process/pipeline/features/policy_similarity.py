"""
news_process.pipeline.features.policy_similarity — 权威政策战略响应度多维测算模块
(stage 26; 历史脚本名 26_authoritative_similarity.py, 现无独立 shim, 由 panel runner 调用)
============================================================================

【学术支撑 (Academic Foundation)】
本模块严格基于 Hoberg & Phillips (2016, JPE) 以及 Guzman & Li (2023, MS)
确立的“先聚合后向量化 (Pool-then-Vectorize)”文本空间范式。企业战略定位本质上是
Firm-Year 级别的结构化特征。通过汇总该年度单家企业的全部碎片化披露，
消除文章级的特质性白噪音 (Idiosyncratic Noise)，构建“企业年度战略画像”。
同时，依据 Hassan et al. (2019, QJE) 测度宏观风险/政策暴露度的核心逻辑，
将宏观《权威政策文本》注入同构特征空间，测度微观画像与宏观基准的收敛性。

相关支撑文献:
- Brown, S. V., & Tucker, J. W. (2011). Large-sample evidence on firms' year-over-year
  MD&A modifications. Journal of Accounting Research, 49(2), 309-346.
  https://doi.org/10.1111/j.1475-679X.2010.00396.x
- Hassan, T. A., et al. (2019). Firm-level political risk: Measurement and effects.
  The Quarterly Journal of Economics, 134(4), 2135-2202.
  https://doi.org/10.1093/qje/qjz021

【白话说明 (Plain Language)】
任务目标：衡量一家银行在特定年份，其战略方向与国家的“金融科技宏观政策”有多贴合。
核心做法 (fix(omni-g-policy-02/04, 2026-06-11) 口径更新)：
1. 把银行一年的所有新闻碎片拼成一份长篇的“银行年度总结”。
2. 把国家的重磅政策文件（权威语料库）按**发布年份 (vintage)** 切分，年度 t 的
   “标准答案”只拼接发布年份 ≤ t 的文件 — 消除“拿还没出生的政策当标答”的前视构造。
3. 为了保证比对的绝对公平，把这份“标准答案”当成一个虚拟的“幽灵银行”，和所有真实的银行
   放在一模一样的算法标准（同构的字典、相同的主题抽取、超长文本同走 token 分段 +
   均值池化 — 旧注释所称“相同的 8000 字截断”已随 embedding_engine 统一而不存在）下比对。
4. 最终得出至多 5 个相似度指标（TF-IDF 字符级 / TF-IDF 词级 / LDA 主题 / Embedding 主轨
   Qwen / Embedding large `_lg` 活跃 co-primary）× Full/Ctx/Ss 三轨：分数越高，说明这家银行的战略
   步调与（截至当年已发布的）国家政策跟得越紧密。
   注: ss 轨 = content_ss (银行+金科同句共现窗, stage 13 物化; 无共现回退全文,
   镜像 ctx); content_ss 缺失时退回 Full/Ctx 两路 (优雅跳过, 不产 _ss 指标列)。
5. 全年份锚点稳健孪生 (2026-06-21, all_vintage_companion 默认开): 在上面 vintage
   "只用当年及以前政策"主轨之外, 再用"所有年份政策文档"拼成的静态标答并列算一套
   完全同结构的 auth_sim_*_allv 指标, 作 anchor-robustness 对照 (含未来政策文本,
   仅稳健性对照, 绝不替换 vintage 主轨)。
============================================================================
"""

import logging  # 仅用于 log_sink 的 level 常量 (worker 回传告警), 不建 logger
import os
import platform
import sys
import time

import numpy as np
import pandas as pd

# sig4/pct4: 日志四位有效数字单一事实源 (golden-safe, 仅渲染日志, 不入产物)。
from news_process.core.logging import pct4, sig4
from news_process.pipeline.features.strategic_diff import (  # noqa: E402
    _aggregate_bank_year_texts as _aggregate,
)
from news_process.pipeline.features.strategic_diff import (
    _build_embedding_sim_matrix as _build_emb,
)
from news_process.pipeline.features.strategic_diff import (
    _build_lda_jsd_matrix as _build_lda,
)
from news_process.pipeline.features.strategic_diff import (
    _build_tfidf_sim_matrix as _build_tfidf,
)
from news_process.pipeline.features.strategic_diff import (
    # S5: 串/并自适应执行器 (含 OOM 兜底整批回落串行) — 与 strategic_diff 三个
    # 调用点共用同一实现, 不另造轮子。本模块**单向依赖** strategic_diff (上面已
    # import 其四个 _build_*), 故无循环 import 风险。
    _run_year_tasks,
)

# fix(omni-g-policy-01/02, 2026-06-11): 权威语料加载/vintage 切分与 stage 15 共用
# 同一实现 (policy_alignment) — 两 stage 消费同一份语料, 锚点口径必须一致:
# (01) 对称归一化 (与新闻侧 normalize 步骤 2.5 同规则: 领导人姓名 '习近平' 简→繁, 体现而非删除);
# (02) vintage-aware 锚点 (年度 t 只用发布年份 ≤ t 的政策文档, 消除前视构造)。
from news_process.pipeline.filtering.policy_alignment import (  # noqa: E402
    all_vintage_companion_enabled,
    load_policy_corpus_docs,
    vintage_anchor_text,
    vintage_aware_enabled,
)

# --- Phase 2a: 取代旧的 importlib 反射 ---
# 共享配置来自 panel/encode (原 41); Stage 25 算法底层来自 features/strategic_diff (原 25)。
from news_process.pipeline.panel.encode import CONFIG, logger  # noqa: E402

# v3.14.0: 移除两条本地嵌入稳健轨 (_t2v text2vec / _bge bge-m3); 保留 API 轨 _lg。
# 第三嵌入模型 (large, text-embedding-3-large): _LARGE_SPEC 非空 (config 配 embedding_large)
# 时产 _lg 列, 现为活跃 co-primary (与无后缀 MAIN Qwen 并列)。
_LARGE_SPEC = CONFIG.get('embedding_large', {})


def _ghost_anchor_metrics(texts, n_banks, year, anchor_text, track_suffix,
                          log_sink=None):
    """对单一锚点文本计算 ghost-anchor 相似度指标 (TF-IDF c/w · LDA · emb · 可选 emb_lg)。

    幽灵锚点 (Ghost Anchor): 将 anchor_text 作为 (N+1)-th 元素挂载至银行文本列表末尾,
    送入与 stage 25 绝对同构的 _build_* 矩阵提取器, 取对称矩阵最后一列 sim[:-1, -1]
    即各银行相对该锚点的相似度 (O(1) 同构提取)。

    本助手抽离自原 compute_authoritative_similarity 的逐年内联块 (2026-06-21), 使
    **同一年同一批银行文本**能用不同锚点各算一遍: vintage 主轨 (≤t) 与全年份 `_allv`
    静态锚点共用此助手, 保证两轨下游构造**完全一致**, 唯锚点不同。

    Args:
        texts: 该年度各银行的聚合文本 (长 n_banks)。
        n_banks: 银行数 (= len(texts), 显式传入避免重算)。
        year: 年份 (仅日志)。
        anchor_text: 锚点文本; None → 全 NaN (vintage 前视守卫年份, 该锚点不可用)。
        track_suffix: 日志标签 (如 '_full' / '_full/allv')。
        log_sink: 可选 ``list``; 给出时本助手 (及其调用的 ``_build_lda``) 产生的
            日志一律**追加为 ``(level, msg)``** 而非直接 emit, 由父端顺序回放。
            ``None`` (默认) = 直接落日志, 与旧码逐字节同路径。
            存在理由: 本助手会在 **loky worker 内**被调用 (S5 逐年并行), 而
            ``strategic_diff`` 既有护栏要求 "worker 体内零 logger 调用"。

    Returns:
        dict[str, Sequence[float]]: 键 ∈ {tfidf_c, tfidf_w, lda, emb},
        各值为长 n_banks 的相似度序列 (anchor_text=None 时全 NaN)。
        ⚠ _LARGE_SPEC 非空 (config 配 embedding_large) 时**额外**带 'emb_lg' 键
        (活跃 co-primary, 与 MAIN emb 同结构); 键存在性由 _LARGE_SPEC 单点决定 →
        全 nan 早退分支与正常分支一致, 防 KeyError。
        both-or-neither: emb 与 emb_lg 任一 None 则两者同置 NaN (无单边孤儿列)。
    """
    def _warn(msg):
        """WARNING 出口单点: sink 存在则回传父端, 否则原样直接 emit。"""
        if log_sink is None:
            logger.warning(msg)
        else:
            log_sink.append((logging.WARNING, msg))

    nan_vec = [np.nan] * n_banks
    if anchor_text is None:
        _d = {'tfidf_c': list(nan_vec), 'tfidf_w': list(nan_vec),
              'lda': list(nan_vec), 'emb': list(nan_vec)}
        if _LARGE_SPEC:
            _d['emb_lg'] = list(nan_vec)
        return _d

    texts_with_auth = texts + [anchor_text]
    n_total = len(texts_with_auth)

    # --- 方法 A/B: TF-IDF 字符级 (char_wb) / 词级 (jieba) ---
    sim_c, _ = _build_tfidf(texts_with_auth, 'char')
    auth_c = sim_c[:-1, -1] if sim_c is not None else list(nan_vec)
    sim_w, _ = _build_tfidf(texts_with_auth, 'word')
    auth_w = sim_w[:-1, -1] if sim_w is not None else list(nan_vec)

    # --- 方法 C: LDA 主题空间 (JSD 散度 → 1 - sqrt(JSD)) ---
    try:
        # log_sink 透传: _build_lda 内的 "LDA K=…, perplexity=…" 一行同走回传口,
        # 否则 worker 里那行会跑到子进程 console 上, 行序错乱且不入阶段日志文件。
        jsd_mat, _ = _build_lda(texts_with_auth, n_total, log_sink=log_sink)
        auth_lda = 1.0 - jsd_mat[:-1, -1]
    except Exception as e:
        _warn(f"    LDA ({year}{track_suffix}) 失败: {type(e).__name__}")
        auth_lda = list(nan_vec)

    # --- 方法 D: Semantic Embedding (主轨 MAIN — Qwen/Qwen3-Embedding-8B, 无后缀) ---
    se_mat, _ = _build_emb(texts_with_auth)

    # --- 方法 D-lg: 第三嵌入 twin (large, text-embedding-3-large; 活跃 co-primary, _LARGE_SPEC 开才算) ---
    # 稳健轨 raise 不炸 stage, 仅置 NaN; 维度无关 (emb.shape[1] 驱动)。
    se_mat_lg = None
    if _LARGE_SPEC:
        try:
            se_mat_lg, _ = _build_emb(texts_with_auth, spec=_LARGE_SPEC)
        except Exception as _lg_exc:
            _warn(f"    Embedding lg ({year}{track_suffix}) 异常: "
                  f"{type(_lg_exc).__name__}: {_lg_exc} → emb_lg 置 NaN")
            se_mat_lg = None

    # both-or-neither parity (家族内 MAIN/_lg 同生共死): 若 _LARGE_SPEC 开 且 MAIN(emb)
    # 或 _lg 任一返回 None, 则两者同置 NaN — 杜绝单边孤儿列 (parity test 会捕获)。
    if _LARGE_SPEC and (se_mat is None or se_mat_lg is None):
        se_mat = None
        se_mat_lg = None

    auth_emb = se_mat[:-1, -1] if se_mat is not None else list(nan_vec)

    _out = {'tfidf_c': auth_c, 'tfidf_w': auth_w, 'lda': auth_lda,
            'emb': auth_emb}

    if _LARGE_SPEC:
        _out['emb_lg'] = se_mat_lg[:-1, -1] if se_mat_lg is not None else list(nan_vec)

    return _out


# ════════════════════════════════════════════════════════════════════════════
# S5 (2026-07-28): 逐 (轨, 年) 任务进程并行
# ════════════════════════════════════════════════════════════════════════════
# **为何选这里**: stage 40 生产实测 28.12h, 本函数 (步骤 7h-policy) 独占
# **38,066s = 37.8%** —— 单一最大极。三轨墙钟 _full 19,571s / _ctx 14,760s /
# _ss 3,727s (同为 6,224 行, 差异来自文本长度)。
#
# **先归因后并行 (2026-07-28 真数据实测, probe_s5_split.py, 2018/_full/478 银行)**:
#     LDA 76.74s 39.9% · TF-IDF char 51.76s 26.9% · TF-IDF word 31.09s 16.2%
#     Embedding MAIN 17.29s 9.0% · Embedding _lg 15.28s 7.9%
#   把 Embedding 那 32.57s 再拆开 (靠 F18 新增的分段计时):
#     SQLite 缓存读 8.43s · **API 段 0.0004s (0.003%)** · 其余 ~24s 是切块/JSON
#     解码/均值池化/矩阵组装 —— 同样是 CPU。
#   ⟹ 真实构成 ≈ **95.6% CPU / 4.4% SQLite 读 / ~0% API**。
#
# **这条归因决定了设计**, 而且推翻了一个很自然的担心:
#   ① **TPM 不是风险**。生产日志佐证: 本步骤 10.57 小时**零 429**, 而相邻窗口
#      (strategic_diff / 7h-emb) 每小时 15,282 条。原因是 `strategic_diff` 先跑并
#      把同一批 bank-year 文本播了种, 本步骤到达时已全命中。故并行**不会**重演
#      F28 (两次 Qwen 重试耗尽 → 面板 4 列全 NaN)。
#   ② **内存也不binding**。实测单任务峰值 RSS Δ = **2.18 GB** (最大年 2015,
#      307 银行 / 19,432,456 字), 本机 127.7 GB ⟹ 50% 预算下 n_jobs ≤ 29。
#   ③ 真正该防的是**任务间 10× 的负载不均** (2007 年 29 家银行 vs 2022 年 584 家) →
#      故用**跨轨扁平任务池 + joblib 动态分派**, 不做静态切分。
#
# **确定性**: LDA 曾因 BLAS 线程数差异漂 ~1e-13, 已由 F26 在 `_build_lda_jsd_matrix`
# 的 fit 现场 `threadpool_limits(1)` 根治 —— 本函数用的正是那一个 (共享实现),
# 故父/子进程算的是同一个 canonical 值。TF-IDF / embedding 走稀疏与简单 numpy
# 路径, 同批 A/B 已证不吃这个。
#
# **护栏 (沿用 strategic_diff 既有四条)**: ① 任务切分与串行循环同序同筛选;
# ② joblib 按提交序返回; ③ 任务数 < 阈值回落串行; ④ **worker 体内零 logger 调用**,
# 告警与 "LDA K=…" 行一律经 log_sink 回传, 父端按提交序回放 ⟹ 日志内容与顺序
# 与串行**逐行一致**。
# ⚠ 阈值**刻意不复用** `strategic_diff._PROC_PARALLEL_MIN_YEARS` (=4): 本池是
#   「3 轨 × N 年」扁平池, N≥2 就 ≥6 个任务, 用 4 会让**现存单测也走进并行分支** ——
#   而单测靠 monkeypatch 打桩, 桩不传播进 loky 子进程 ⟹ 测试当场失真。
#   12 这个值把 T=2 dev (3×2=6) 与 toy fixture 一律留在串行, 生产 (3×19=57) 走并行。
_AUTH_PARALLEL_MIN_TASKS = 12

#: 并行度运维旁路。stage 40 单跑 28 小时, 出事重跑代价极高 —— 留一个不改代码就能
#: 下调的口子 (设计评审要求的 "首跑 P=8 观测 RSS, 确认后再上 12")。
#: 未设 / 非法 → None ⟹ 走 `_proc_workers()` 默认 min(12, 核数-2, 任务数)。
_AUTH_JOBS_ENV = 'NEWS_PROCESS_AUTH_JOBS'


def _auth_jobs_override():
    """读 ``NEWS_PROCESS_AUTH_JOBS``; 非正整数或未设 → None (用默认并行度)。"""
    raw = os.environ.get(_AUTH_JOBS_ENV, '').strip()
    if not raw:
        return None
    try:
        v = int(raw)
    except ValueError:
        logger.warning(f"  {_AUTH_JOBS_ENV}='{raw}' 非整数, 忽略 (用默认并行度)")
        return None
    if v < 1:
        logger.warning(f"  {_AUTH_JOBS_ENV}={v} < 1, 忽略 (用默认并行度)")
        return None
    return v


def _auth_year_worker(task, auth_text_static, companion):
    """单个 (轨, 年) 的 ghost-anchor 计算 —— 原逐年循环体**逐字节照搬**。

    ⚠ 与串行循环唯一的差别: 所有 ``logger.*`` 改为写入本地 ``logs`` 列表回传,
    由父端按提交序统一 emit (见上方护栏 ④)。两个早退守卫 (银行数 <3 / vintage
    锚点为 None) **刻意留在 worker 内**而非提到父端 —— 提到父端会让守卫告警与
    计算类日志的交错顺序偏离串行 (父端会先把所有守卫行打完再回放计算行)。

    Args:
        task: ``(track_suffix, year, banks, texts, auth_text_vin)``。
        auth_text_static: 全年份静态锚点 (常量, 由 ``*extra`` 透传)。
        companion: ``all_vintage_companion_enabled()`` 的取值 (常量)。

    Returns:
        ``(records, logs)`` — records 为该年的 ``dict`` 列表 (可能为空),
        logs 为 ``(level, msg)`` 列表。
    """
    track_suffix, year, banks, texts, auth_text_vin = task
    logs: list[tuple[int, str]] = []
    records: list[dict] = []

    # 如果当年的银行数过少，跳过（为保持与 Stage 25 LDA K值的最小计算稳定性一致）
    if len(banks) < 3:
        # fix(omni-g-policy-05, 2026-06-11): 裸 continue → 显式 warning
        # (镜像 stage 25 同守卫), T=19 早期稀疏年份不再"静默 NaN"无迹可寻
        logs.append((logging.WARNING,
                     f"  年度={year}{track_suffix}: 仅 {len(banks)} 家"
                     f"银行, 跳过 auth_sim 计算 (最低要求 3)"))
        return records, logs

    n_banks = len(banks)

    # fix(omni-g-policy-02, 2026-06-11): vintage-aware 锚点 — 年度 t 只用
    # 发布年份 ≤ t 的政策文档拼接; 无可用文档 → 该年 auth_sim_* 全 NaN (前视守卫)
    if auth_text_vin is None:
        logs.append((logging.WARNING,
                     f"  年度={year}{track_suffix}: 无发布年份 ≤ "
                     f"{year} 的政策文档 (前视守卫), auth_sim_* 置 NaN"))
        # companion 关闭时保持原行为: 直接跳过该年 (merge 后留 NaN);
        # companion 开启时不跳过 — 仍要用全年份静态锚点产 _allv (2014 等也出值)。
        if not companion:
            return records, logs

    # vintage 主轨指标 (auth_text_vin=None → 全 NaN); 经助手统一同构计算
    vin = _ghost_anchor_metrics(
        texts, n_banks, year, auth_text_vin, track_suffix, log_sink=logs)
    # 全年份 _allv 孪生 (companion 开启时): 用全语料静态锚点再算一遍 (下游完全一致)。
    # 短路对称 (镜像 stage15 _cosine_for_spec non-vintage 分支 return _wrap(static,static)):
    # 当 vintage 锚点 == 全年份静态锚点 (晚年 ≤t 已含全部政策文档 / use_vintage=False 退化时
    # auth_text_vin==auth_text_static) → allv 与 vin byte-identical, 复用 vin 副本即可, 免重算
    # TF-IDF/LDA/embedding (golden-safe: 同锚点同输入确定性产同值; 生产 T=19 多数年锚点真不同则正常重算)。
    if not companion:
        allv = None
    elif auth_text_vin is not None and auth_text_vin == auth_text_static:
        allv = {k: list(v) for k, v in vin.items()}
    else:
        allv = _ghost_anchor_metrics(
            texts, n_banks, year, auth_text_static, f'{track_suffix}/allv',
            log_sink=logs)

    # 打包记录 (vintage 主轨 + 可选 _allv 孪生)
    for i, bank in enumerate(banks):
        rec = {
            'target_bank': bank,
            'year': year,
            f'auth_sim_tfidf_c{track_suffix}': float(vin['tfidf_c'][i]),
            f'auth_sim_tfidf_w{track_suffix}': float(vin['tfidf_w'][i]),
            f'auth_sim_lda{track_suffix}': float(vin['lda'][i]),
            f'auth_sim_emb{track_suffix}': float(vin['emb'][i]),
        }
        # 第三嵌入 _lg (活跃 co-primary; 键存在性由 _LARGE_SPEC 经助手单点决定 → 与早退分支一致)
        if 'emb_lg' in vin:
            rec[f'auth_sim_emb_lg{track_suffix}'] = float(vin['emb_lg'][i])
        if allv is not None:
            rec.update({
                f'auth_sim_tfidf_c_allv{track_suffix}': float(allv['tfidf_c'][i]),
                f'auth_sim_tfidf_w_allv{track_suffix}': float(allv['tfidf_w'][i]),
                f'auth_sim_lda_allv{track_suffix}': float(allv['lda'][i]),
                f'auth_sim_emb_allv{track_suffix}': float(allv['emb'][i]),
            })
            # _allv 是 vin 整 dict copy 或同助手再算 → emb_lg 自动随 _LARGE_SPEC 传播
            if 'emb_lg' in allv:
                rec[f'auth_sim_emb_lg_allv{track_suffix}'] = float(allv['emb_lg'][i])
        records.append(rec)

    return records, logs


# ============================================================================
# 核心计算函数
# ============================================================================

def compute_authoritative_similarity(df_exploded, panel):
    """
    计算基于权威政策的战略响应度 (Authoritative Policy Strategic Alignment)。

    【学术基础】
    本模块的测度范式严格依据以下顶刊文献的 "Text-based Anchor Vectorization" 框架构建：
    - Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level
      political risk: Measurement and effects. The Quarterly Journal of Economics,
      134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
      (注 [锚点勘误 2026-06-10]: Hassan et al. 2019 仅提供"将宏观政策文本嵌入与微观企业
       共享向量空间"的概念动因; 其 firm-level political risk 实为窗口 bigram 频率, 并非
       "微观向量与宏观锚向量的余弦相似度"。本模块实际采用的 cosine-to-anchor 操作化
       归功于下方 Hoberg & Phillips (2016) / Guzman & Li (2023), 勿将余弦公式归 Hassan。)
    - Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous
      product differentiation. Journal of Political Economy, 124(5), 1423-1465.
      https://doi.org/10.1086/688176
      (注: 沿用其高维 TF-IDF 文本相似度矩阵提取与产品空间定位方法论)

    fix(omni-g-policy-02, 2026-06-11) 语义变更: 锚点改为 vintage-aware — 年度 t 的
    “标答”只拼接发布年份 ≤ t 的政策文档 (load_policy_corpus_docs 解析 vintage);
    无 ≤t 文档的年份 auth_sim_* 置 NaN (前视守卫); vintage 不可用时降级静态锚点并披露。

    【白话说明】
    我们怎样判断一家银行是不是在“响应国家号召”？最客观的办法，就是把国家发布的
    “宏观政策原文”当成一个完美的满分标答（也就是这里的虚拟锚点），然后让所有
    银行当年的“新闻汇总”和这个标答去比对。相似度越高，说明这家银行在战略上越贴合国家政策。
    比对只用“当年已经发布”的政策文件 — 2017 年的银行画像不会拿 2022 年才发布的
    规划当标答 (vintage-aware, 见上)。

    【工程实现：幽灵锚点 (Ghost Anchor)】
    为保证与 Stage 25 (同行战略差异度) 采用绝对同构的度量空间，我们将政策文本作为
    (N+1)-th 元素挂载至各年度的银行文本列表中，送入共享底层的 _build_* 矩阵提取器。
    随后仅提取对称矩阵的最后一列切片 `sim[:-1, -1]`，即以 O(1) 逻辑提取了各微观
    银行相对于宏观基准的距离，实现了零冗余且 100% 同构。

    Args:
        df_exploded (pd.DataFrame): 包含新闻原文的文章级数据集
        panel (pd.DataFrame): 准备挂载结果的 Bank-Year 面板数据

    fix(2026-06-21, all_vintage_companion): companion 开启 (默认) 时, 在 vintage 主轨
    之外并列再产一套全年份(静态全语料)锚点指标 auth_sim_*_allv{track} (anchor-robustness
    对照; 含未来政策文本, 绝不替换 vintage 主轨)。逐年 ghost-anchor 计算抽至
    _ghost_anchor_metrics 助手, vintage / 全年份 各调一次 → 下游构造完全一致, 唯锚点不同。

    Returns:
        pd.DataFrame: 合并了 vintage 主轨 权威政策相似度指标的最新 panel
        (指标 = TF-IDF c/w · LDA · emb 主轨 [+ emb_lg 当 _LARGE_SPEC 开] × Full/Ctx/Ss 三轨;
        content_ss 缺失时退回 Full/Ctx 两轨)。all_vintage_companion 开启时再并列同结构的
        `_allv` 全年份锚点孪生。
    """
    _t_start = time.time()
    logger.info("=" * 60)
    logger.info("开始计算: 权威政策战略响应度 (Stage 26 · authoritative_similarity)")
    logger.info("=" * 60)

    # ── 子步骤 banner (called-by-runner helper; ENV/CONFIG/方法论/结果判读) ──
    # 全程 try/except 包裹 — 日志块绝不允许炸 stage (铁律)。数字一律 sig4/pct4。
    try:
        logger.info("  🧭 项目/环境  news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板, v3.16.0)")
        logger.info("     · 子步骤 7h(policy): 银行年度战略画像 vs 宏观权威政策锚点的 ghost-anchor 余弦响应度")
        logger.info(f"     · Python {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · {platform.platform()} | CPU={os.cpu_count()} | PID={os.getpid()}")
        logger.info(f"     · RUN_ID={os.environ.get('NEWS_PROCESS_RUN_ID', '(unset)')} | cwd={os.getcwd()}")
        logger.info(f"     · 模块: {os.path.abspath(__file__)}")
        logger.info("     · 确定性/成本: 纯 CPU 文本相似度 (TF-IDF/LDA 确定); embedding 主轨/(_lg) 经穿透缓存,"
                    " 在线冷缓存须付费嵌入 (Qwen / text-embedding-3-large) — 命中则 $0; "
                    "离线 NEWS_PROCESS_LLM_OFFLINE=1 时 miss→raise 零网络")
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  环境信息打印失败 (不影响计算): {_e}")

    try:
        logger.info("  📖 方法论依据 (运行期引文; 逐字取自经核验注册表 + DOI 可访问链接)")
        logger.info("     · 文本锚点向量化 (TF-IDF 相似度矩阵 / 产品空间定位):")
        logger.info("       Hoberg, G., & Phillips, G. (2016). Text-based network industries and "
                    "endogenous product differentiation. Journal of Political Economy, 124(5), "
                    "1423-1465. https://doi.org/10.1086/688176")
        logger.info("     · LDA 主题空间分布相似度 (方法 C; 财务披露文本主题建模 → 主题分布散度):")
        logger.info("       Dyer, T., Lang, M., & Stice-Lawrence, L. (2017). The evolution of "
                    "10-K textual disclosure: Evidence from Latent Dirichlet Allocation. Journal "
                    "of Accounting and Economics, 64(2-3), 221-245. "
                    "https://doi.org/10.1016/j.jacceco.2017.07.002")
        logger.info("       (白话: 把银行年度披露/新闻汇总投到 LDA 主题分布上, 用主题分布间的 JSD "
                    "散度度量与政策锚点的主题贴合度 — auth_sim_lda 的算法出处)")
        logger.info("     · 宏观政策文本注入共享向量空间 (测度微观画像与宏观基准收敛性, 概念动因):")
        logger.info("       Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). "
                    "Firm-level political risk: Measurement and effects. The Quarterly Journal of "
                    "Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021")
        logger.info("     · 企业年度战略画像跨年比对 (先聚合后向量化, 消除文章级特质白噪音):")
        logger.info("       Brown, S. V., & Tucker, J. W. (2011). Large-sample evidence on firms' "
                    "year-over-year MD&A modifications. Journal of Accounting Research, 49(2), "
                    "309-346. https://doi.org/10.1111/j.1475-679X.2010.00396.x")
        logger.info("     · 以监管政策原文为参照语料 / 机器文本测度量化进面板 (锚点语料构念, 近期 JF 发展):")
        logger.info("       Kalmenovitz, J., Lowry, M., & Volkova, E. (2025). Regulatory "
                    "fragmentation. The Journal of Finance, 80(2), 1081-1126. "
                    "https://doi.org/10.1111/jofi.13423")
        logger.info("       (白话: 用监管全文做机器文本测度量化碎片化进面板, 锚定以监管/政策原文为参照语料的范式)")
        logger.info("     · embedding 主轨 (方法 D) 余弦对锚 — 金融文本嵌入基准 (含中英监管文件 STS):")
        logger.info("       Tang, Y., & Yang, Y. (2025). FinMTEB: Finance Massive Text Embedding "
                    "Benchmark. In Proceedings of the 2025 Conference on Empirical Methods in "
                    "Natural Language Processing (pp. 3620-3638). Association for Computational "
                    "Linguistics. https://doi.org/10.18653/v1/2025.emnlp-main.179")
        logger.info("       (白话: 金融文本嵌入基准含中英监管文件 STS, 锚定嵌入余弦做金融/政策相似度)")
        logger.info("     · 政策文本嵌入向量化 (央行/监管沟通 → 向量, 近期应用):")
        logger.info("       Araujo, D., Bokan, N., Comazzi, F., & Lenza, M. (2025). Word2Prices: "
                    "Embedding central bank communications for inflation prediction. SSRN "
                    "Electronic Journal. https://doi.org/10.2139/ssrn.5201335")
        logger.info("       (白话: 词嵌入表征央行政策沟通, 政策文本嵌入向量化的最新央行应用)")
        logger.info("     · 嵌入主轨金融域适配 (domain-specific SBERT, 锚点政策/披露文本嵌入):")
        logger.info("       Jehnen, S., Villalba-Díez, J., & Ordieres-Meré, J. (2026). FinTextSim: A "
                    "domain-specific sentence-transformer for extracting predictive latent topics from "
                    "financial disclosures. Frontiers in Artificial Intelligence, 9, Article 1752103. "
                    "https://doi.org/10.3389/frai.2026.1752103")
        logger.info("       (白话: 对金融披露/政策文本微调 sentence-transformer, 锚定本模块方法 D 嵌入轨"
                    "把权威政策与银行画像嵌入同构语义空间做余弦对锚的域适配依据)")
        logger.info("     → 为何用: 把国家政策原文当满分标答(虚拟幽灵锚点), 银行年度新闻汇总越贴近 → 战略响应度越高")
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  方法论引文打印失败 (不影响计算): {_e}")

    # 1. 载入权威政策文本锚点 (Phase 2a: 通过 CONFIG['paths'][...] 解析)
    auth_path = CONFIG['paths'].get(
        'authoritative_corpus_file',
        os.path.join(os.path.dirname(__file__), 'config', 'authoritative_corpus.txt'),
    )
    if not os.path.exists(auth_path):
        logger.warning(f"  找不到权威政策语料: {auth_path}。跳过 Stage 26 计算。")
        return panel

    # fix(omni-g-policy-01/02, 2026-06-11): 改经 load_policy_corpus_docs 加载 —
    # 对称归一化 (领导人姓名简→繁) + 按发布年份切分; 静态全语料拼接仅作 vintage 不可用时的降级锚点。
    auth_docs = load_policy_corpus_docs(auth_path)
    auth_text_static = '\n\n'.join(d['text'] for d in auth_docs).strip()

    if not auth_text_static:
        logger.warning("  权威政策语料为空。跳过 Stage 26 计算。")
        return panel

    use_vintage = (vintage_aware_enabled()
                   and any(d['year'] is not None for d in auth_docs))
    if not use_vintage:
        logger.warning(
            "  vintage 前视守卫: 关闭 (opt-out 或语料年份全部未知) → "
            "静态全语料锚点 (含未来政策文本, 前视披露)")

    # 全年份锚点稳健孪生 (2026-06-21): companion 开启时, 在 vintage 主轨之外并列再用
    # 全语料(所有年份)静态锚点 auth_text_static 算一套 auth_sim_*_allv{track} 指标
    # (anchor-robustness; 含未来政策文本, 仅稳健性对照, 绝不替换 vintage 主轨)。
    # vintage 不可用 (use_vintage=False) 时主轨本就 = 静态锚点 → _allv ≡ 主轨 (诚实退化)。
    _companion = all_vintage_companion_enabled()
    if _companion:
        logger.info("  全年份锚点稳健孪生 (_allv): 开启 — 并列产出 auth_sim_*_allv{track} "
                    "(全语料静态锚点, anchor-robustness 对照)")

    # ── ⚙ 运行配置 (CONFIG block; 可调参数 + 输入路径 + 锚点口径) ──
    try:
        _n_doc_yr = sum(1 for d in auth_docs if d['year'] is not None)
        _yrs = sorted({d['year'] for d in auth_docs if d['year'] is not None})
        logger.info("  ⚙ 运行配置 (config: paths.authoritative_corpus_file / policy_alignment 共享口径)")
        logger.info(f"     · 权威政策语料: {auth_path}")
        logger.info(f"     · 政策文档数={len(auth_docs):,d} | 带发布年份 vintage={_n_doc_yr:,d} | "
                    f"静态全语料字数={len(auth_text_static):,d}")
        logger.info(f"     · 覆盖发布年份: {_yrs if _yrs else '(全部未知)'}")
        logger.info(f"     · vintage-aware 前视守卫={use_vintage} (年度 t 只用发布年份 ≤ t 的政策) | "
                    f"all_vintage_companion(_allv)={_companion}")
        logger.info("     · 相似度指标: 至多 5 维 (TF-IDF 字符级/词级 · LDA 主题 JSD · embedding 主轨 · "
                    "embedding large _lg co-primary)")
        # fix(N10, 2026-07-18): 旧写法读不存在的顶层键 'embedding_model' 恒打印 '(default)';
        # 真实路径 = embedding_api.model (features.yaml), 与 _lg 轨对称。
        logger.info(f"     · embedding 主轨={CONFIG.get('embedding_api', {}).get('model', '(default)')} | "
                    f"large _lg spec={_LARGE_SPEC.get('model', '(unset)') if _LARGE_SPEC else '(unset)'}")
        logger.info("     · 最低银行门槛=3 家/年 (镜像 stage 25 LDA K 值稳定性守卫, 不足则该年跳过)")
        # 输入文章级数据 provenance (仅日志; _ftc/_has_* 为本地副本, 与 @341 真正决策列各算各不复用)
        _ftc = 'content_full' if 'content_full' in df_exploded.columns else '内容'
        _has_ctx = 'content_ctx' in df_exploded.columns
        _has_ss = 'content_ss' in df_exploded.columns
        logger.info(f"     · 输入文章级数据集 df_exploded: {df_exploded.shape[0]:,d} 行 × "
                    f"{df_exploded.shape[1]:,d} 列")
        logger.info(f"     · full 轨文本列={_ftc} (content_ctx 存在={_has_ctx}, "
                    f"content_ss 存在={_has_ss}; 缺 content_ctx/ss 则该轨优雅跳过)")
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  配置信息打印失败 (不影响计算): {_e}")

    # 2. 准备 Full / Ctx / Ss 三轨池化数据
    # fix(completeness-04): full 轨读 content_full(含标题, v3.8.0 full/ctx 命名契约), 与 ctx 轨
    # (content_ctx 含标题) 对称; 原读裸 '内容'(无标题) 致 full↔ctx 不对称 (病根A 同型)。
    # ss 轨 (银行+金科同句): content_ss 由 stage 13 物化 (无共现回退全文 body, 镜像
    # ctx); 缺列优雅跳过 (镜像 ctx 缺列守卫) → 退回 Full/Ctx 两路, 不产 _ss 指标列。
    _full_text_col = 'content_full' if 'content_full' in df_exploded.columns else '内容'
    tracks = [('_full', _aggregate(df_exploded, text_col=_full_text_col))]
    if 'content_ctx' in df_exploded.columns:
        tracks.append(('_ctx', _aggregate(df_exploded, text_col='content_ctx')))
    else:
        logger.info("  未发现 'content_ctx' 列，将仅计算 Full 轨战略响应度。")
    if 'content_ss' in df_exploded.columns:
        tracks.append(('_ss', _aggregate(df_exploded, text_col='content_ss')))
    else:
        logger.info("  未发现 'content_ss' 列 (stage 13 未物化同句共现轨?)，"
                    "将跳过 Ss 轨战略响应度 (镜像 ctx 缺列优雅跳过)。")

    all_results = []

    # 3. 逐轨、逐年计算 — S5 (2026-07-28): 切成 (轨, 年) 任务后进程并行。
    #    任务切分**必须与旧串行循环同序同筛选**: 轨按 tracks 原序, 年按
    #    sorted(unique)。任何漂移都是静默改测度 (少算/多算年份或改列序)。
    #    ⚠ 早退守卫 (银行数<3 / vintage 锚点 None) 刻意留在 worker 内 —— 提到这里
    #      会把守卫告警与计算日志的交错顺序打乱 (见 _auth_year_worker docstring)。
    _tasks = []
    for track_suffix, agg_df in tracks:
        if agg_df.empty:
            continue

        logger.info(f"  正在处理轨道 {track_suffix}...")

        # 该轨喂入 ghost-anchor 计算的数据规模 (仅日志, 整数计数 :,d, 算完即弃)
        try:
            _n_units = len(agg_df)
            _n_years = int(agg_df['year'].nunique())
            _y_lo, _y_hi = int(agg_df['year'].min()), int(agg_df['year'].max())
            logger.info(f"  轨 {track_suffix}: {_n_units:,d} 个 bank-year 聚合单元 "
                        f"跨 {_n_years:,d} 年 (年范围 {_y_lo}-{_y_hi}) 喂入 ghost-anchor 余弦对锚")
        except Exception as _e:  # noqa: BLE001
            logger.warning(f"  轨 {track_suffix} 聚合统计打印失败 (不影响计算): {_e}")

        for year in sorted(agg_df['year'].unique()):
            dy = agg_df[agg_df['year'] == year]
            # fix(omni-g-policy-02, 2026-06-11): vintage-aware 锚点 — 年度 t 只用
            # 发布年份 ≤ t 的政策文档拼接; 无可用文档 → None (worker 侧走前视守卫)。
            # 锚点在父端算: 纯字符串拼接 (零日志零 IO), 且免得把 auth_docs 复制进
            # 每个 worker。
            _vin_anchor = (vintage_anchor_text(auth_docs, year) if use_vintage
                           else auth_text_static)
            _tasks.append((track_suffix, year,
                           dy['target_bank'].tolist(),
                           dy['agg_text'].tolist(),
                           _vin_anchor))

    if _tasks:
        _jobs = _auth_jobs_override()
        _par = len(_tasks) >= _AUTH_PARALLEL_MIN_TASKS
        logger.info(f"  逐年计算: {len(_tasks):,d} 个 (轨, 年) 任务, "
                    f"执行方式={'进程并行' if _par else '串行'}"
                    f"{f' (n_jobs={_jobs}, 经 {_AUTH_JOBS_ENV} 指定)' if _jobs else ''}"
                    f"; 阈值 min_tasks={_AUTH_PARALLEL_MIN_TASKS}")

        def _emit(out):
            """单任务完成即回放 —— **流式**, 不缓冲到最后。

            ⚠ 流式是硬需求不是优化: 生产上本步骤跑 10.57 小时, 其间 111 条
            "LDA K=…" 是唯一进度信号; 若缓冲到最后统一吐, 十小时日志全空白, 且一旦
            像 2026-07-27 那样被超时闸强杀, 缓冲的日志连同进度**全部丢失**。
            `_run_year_tasks(on_result=...)` 用 joblib `return_as='generator'`,
            仍按**提交序**产出 ⟹ 行序/归并序与串行逐行一致。

            ⚠ 必须按级别分派回 `logger.warning` / `logger.info` 这些**原调用面**,
            不能图省事统一走 `logger.log(lvl, msg)`: 二者输出的日志行完全相同, 但
            调用面不同 —— 既有单测 (test_omni_fix_policy) 用 Mock 断言
            `logger.warning` 被调用, 统一走 log() 会让守卫披露的测试当场变红。
            ⚠ 这个差异 **A/B 的"日志逐行比对"抓不到** (logging.Handler 分辨不出
            `warning(m)` 与 `log(WARNING, m)`), 2026-07-28 是被既有单测抓到的。
            ⚠ `logger` 在此**按名解析** (模块全局), 不提前绑定成局部变量, 否则
            monkeypatch 打的桩就失效了。
            """
            _recs, _logs = out
            for _lvl, _msg in _logs:
                if _lvl >= logging.ERROR:
                    logger.error(_msg)
                elif _lvl >= logging.WARNING:
                    logger.warning(_msg)
                else:
                    logger.info(_msg)
            all_results.extend(_recs)

        _run_year_tasks(_tasks, _auth_year_worker,
                        auth_text_static, _companion,
                        min_tasks=_AUTH_PARALLEL_MIN_TASKS,
                        n_jobs=_jobs, on_result=_emit)

    # 4. 汇总挂载至 Panel
    if all_results:
        res_df = pd.DataFrame(all_results)
        # 多轨道结果会自动产生相同的 (target_bank, year) 行，必须合并
        res_df = res_df.groupby(['target_bank', 'year'], as_index=False).first()

        # 挂载到现有 panel
        panel = panel.merge(res_df, on=['target_bank', 'year'], how='left')
        _metric_cols = [c for c in res_df.columns if c.startswith('auth_sim_')]
        _n_allv = sum(1 for c in _metric_cols if '_allv' in c)
        logger.info(f"  ✅ 权威政策相似度: 成功合并 {len(res_df):,d} 行记录 "
                    f"({len(_metric_cols):,d} 指标列, 其中 {_n_allv:,d} 列为全年份锚点 _allv 孪生)")

        # ── 📊 关键指标解读 (RESULT-ANALYSIS; 逐指标对照阈值给好/临界/坏判读) ──
        try:
            logger.info("  📊 关键指标解读 (权威政策相似度 ∈ [0,1]; 越高=战略步调越贴合国家政策)")
            for col in _metric_cols:
                s = pd.to_numeric(res_df[col], errors='coerce')
                n_valid = int(s.notna().sum())
                n_tot = len(s)
                nan_rate = 1.0 - (n_valid / n_tot) if n_tot else 1.0
                if n_valid < 3:
                    logger.info(f"     · {col}: 有效 {n_valid:,d}/{n_tot:,d} (前视守卫/小样本, 暂无判读)")
                    continue
                mu, sd = float(s.mean()), float(s.std())
                lo, hi = float(s.min()), float(s.max())
                # 判读: 余弦相似度族典型在 [0,1]; std 反映银行间区分度, 0 方差 = 退化无信息
                if sd < 1e-6:
                    verdict = "⚠ 零方差(全部相同→无横截面区分度)"
                elif sd < 0.02:
                    verdict = "⚠ 区分度偏弱"
                else:
                    verdict = "✓ 区分度正常"
                if nan_rate > 0.5:
                    verdict += f" | ⚠ 缺失偏高 {pct4(nan_rate)}(前视守卫/回退)"
                logger.info(f"     · {col}: μ={sig4(mu)} σ={sig4(sd)} "
                            f"范围=[{sig4(lo)}, {sig4(hi)}] 有效={n_valid:,d}/{n_tot:,d} "
                            f"缺失={pct4(nan_rate)} → {verdict}")
            # _allv 孪生与 vintage 主轨的相关性 (高度相关=锚点稳健; 用 emb 主轨作代表对)
            for sfx in ('_full', '_ctx', '_ss'):
                vin_c, allv_c = f'auth_sim_emb{sfx}', f'auth_sim_emb_allv{sfx}'
                if vin_c in res_df.columns and allv_c in res_df.columns:
                    pair = res_df[[vin_c, allv_c]].apply(pd.to_numeric, errors='coerce').dropna()
                    if len(pair) >= 3 and pair[vin_c].std() > 0 and pair[allv_c].std() > 0:
                        r = float(pair[vin_c].corr(pair[allv_c]))
                        rv = "✓ 锚点高度稳健" if r > 0.8 else ("临界" if r > 0.5 else "⚠ 锚点敏感")
                        logger.info(f"     · 锚点稳健性 corr(vintage, _allv){sfx} (emb 主轨)="
                                    f"{sig4(r)} (n={len(pair):,d}) → {rv}")
        except Exception as _e:  # noqa: BLE001
            logger.warning(f"  结果分析打印失败 (不影响计算): {_e}")
    else:
        logger.warning("  ⚠️ 权威政策相似度: 无任何有效计算结果产出")

    try:
        logger.info(f"  ⏱ Stage 26 (authoritative_similarity) 墙钟耗时: {sig4(time.time() - _t_start)} 秒 "
                    f"| 处理轨道={len(tracks):,d} (full/ctx/ss 视 content 列存在性)")
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  计时打印失败 (不影响计算): {_e}")

    return panel
