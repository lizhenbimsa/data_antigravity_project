"""
news_process.pipeline.sentiment.herd_decay — 跟风/抄袭新闻检测与衰减加权 (三轨版 v3.9.0)
=========================================================================

迁移说明 (Phase 7a-7)：
    本模块由原 root script ``24_herd_decay_processor.py`` body 迁入。
    规范调用方式: ``python -m news_process.pipeline.sentiment.herd_decay``

v3.6.0 (Plan E P1 B3) full/ctx 化升级:
    原实现仅对 '内容' 全文做 TF-IDF 相似度判定, 算出单列 herd_weight,
    被下游同时施加到 _full / _ctx 两条轨道。这是 measurement-treatment
    错配 (Edwards 2001 ORM): 全文相似度 ≠ 对目标银行的报道相似度。
    本版本改为对 '内容' 和 'content_ctx' 分别做 TF-IDF, 输出 full/ctx
    两列权重 herd_weight_full + herd_weight_ctx, 下游按 track 各自施加。
    (本模块现已三轨: full/ctx/ss, 见下方 v3.9.0 段。)

v3.9.0 (第三轨 _ss 同句共现) 三轨化升级:
    在 full / ctx 之外新增第三主轨 ss (银行+金科同句, bank+fintech
    same-sentence co-occurrence): 对 'content_ss' (标题+同句内同时含 目标银行∧
    金科词 的句 ±N 句窗; 无共现→回退全文 body, 镜像 ctx 回退公理) 独立做
    TF-IDF, 输出 herd_weight_ss + n_similar_articles_ss, 下游按 track 各自施加。
    与 ctx 同动因 (Edwards 2001 ORM measurement-treatment matching): 同句共现
    相似度 ≠ 全文相似度, 亦 ≠ 目标银行邻域相似度, 故第三轨各自判定不混用。

功能:
  对同一 target_bank 在同一时间窗口内的多篇新闻进行文本相似度聚类,
  识别"跟风抄袭"新闻并施加衰减权重, 防止重复计数导致情感指标注水。
  v3.6.0 起按 full / ctx 双轨独立判定; v3.9.0 起扩为 full / ctx / ss 三轨。

学术依据:
  - Tetlock (2011, RFS 24(5):1481-1512): 媒体新闻的信息冗余与重复效应
  - Sautner et al. (2023, JF): 文本相似度驱动的曝光度度量
  - Edwards (2001, ORM): measurement-treatment matching (双轨/三轨化动因)

关键设计:
  - TF-IDF 向量化 (max_features=5_000_000, 有效=不截断; 2026-06-24 由 10000 上调以解决 g-herd-02)
    ⚠ 披露 → 解决 (fix(omni-g-herd-02, 2026-06-11 披露 → 2026-06-24 解决)): max_features 按
    **原始词频**截断 top-k — 旧默认 10000 把头部大行 (工农中建) char 2-4 gram 词表 (实测 5–7 万)
    压入高频 boilerplate ngram 子空间, 判别性长尾缺席 → 余弦系统性膨胀, 规模依赖。盘上实测
    (full 轨, content_full, 55 组): capped 10000 vs uncapped 跟风 flag 篇数 313→268 (+16.8% 伪膨胀),
    前驱计数 730→555 (+31.5%), 且高度集中在报道量最大的头部行 (建行 flag 47→24 近腰斩、工行计数
    225→129), 直接破坏 0.35 阈值的跨行可比性 (此前 g-herd-02 误判为 latent 已被实测推翻)。
    **解决**: 上调至 5e6 (远超任何现实 bank-year char 2-4 gram 词表 → 截断不再咬合, 恢复跨行
    可比性)。词表真撞 5e6 时运行期仍记 logger.warning (极端规模 tripwire, 届时改 HashingVectorizer
    或按 IDF 选 top-k)。注: 上调 max_features 几乎无内存代价 — sklearn 无论 cap 多大都先建全量
    计数词表再截断, cap 仅缩窄输出矩阵列宽, 而 CSR 稀疏存储量随 nnz 不随列宽 → 旧 cap 几乎不省内存
    却独自歪曲测度。残余 (未由本修复触及): 词表/IDF 仍按 (bank, 年度前缀) 组内拟合的跨组非同质
    (g-herd-01/05 披露), 0.35 阈值的严格跨行可比性仍不完全成立。
  - df 阈值比例化 (fix(omni-g-herd-01, 2026-06-11)): min_df = min(MIN_DF,
    max(2, ceil(0.01·n))), 消除小组词表塌缩断崖; max_df 守卫 df-band 退化 (详见
    _build_tfidf_vectorizer docstring)。
    ⚠ 披露: 词表/IDF 仍按 (bank, 年度前缀) 组内拟合, 相似度刻度跨组不完全同质 →
    0.35 阈值的跨银行严格可比性不成立 (比例化仅消除 df-band 退化这一最大失真源)。
  - as-of yearly vocab fit (fix(omni-g-herd-05, 2026-06-11)): 年 t 文章的前驱计数仅用
    year ≤ t 文档拟合的向量空间 (前驱构念严格后视, 向量空间不得含未来 DF/IDF);
    年内残余前视为接受粒度 (面板为 bank-year)。
  - ≤2000 篇/前缀 走 dense pairwise; >2000 篇走 7 天窗双指针分桶 O(N·window) (W1 2026-06-05)
  - 相似度阈值 0.35: 相似度 ≥ 此值视为"跟风" (闭边界, 代码用 >=)
  - 衰减公式: weight = 1 / (1 + n_similar_predecessors)
  - **三轨** (full / ctx / ss): full 用 'content_full'(标题+全文), ctx 用 'content_ctx'
    (标题+实体窗口), ss 用 'content_ss'(标题+银行∧金科同句窗); 三者均由 stage 14
    物化、含标题对称 (病根A 已修); 缺 content_full 时 full 回退裸 '内容', 缺 content_ctx
    时 ctx 回退 full, 缺 content_ss 时 ss 回退 full (ss 回退公理由 stage 14 物化时
    镜像 ctx: 无银行∧金科同句共现→content_ss=全文 body, ss_is_fallback=True)

输入: 23_bert_tone.parquet (含 content_ctx / content_ss / ss_is_fallback 列,
      由 stage 14 ctx_materializer 物化后下传)
输出: 24_herd_decay.parquet (追加 8 列: 6 三轨列 herd_weight_full + herd_weight_ctx
      + herd_weight_ss + n_similar_articles_full + n_similar_articles_ctx +
      n_similar_articles_ss, 外加 herd_weight + n_similar_articles 两个单列 ——
      后者作为 _full 轨的 NON-BREAKING 别名保留 (v3.6.0 F-B 修, 见下方主路径),
      供 v3.5.x 既有调用方继续读取, 不强制下游显式指定轨道)

阈值敏感性 (2026-06-13, herd_detection.sensitivity_thresholds):
  0.35 是研究者自由参数 — 构念锚 Tetlock (2011 RFS) 用连续 staleness 不设硬阈值,
  故按预注册网格 (默认 τ ∈ {0.25, 0.30, 0.40, 0.45}) 在同一 TF-IDF/余弦矩阵上
  一遍式复算前驱计数, 额外输出 herd_weight_{track}_thrNN + n_similar_articles_
  {track}_thrNN (默认 4 τ × 3 轨 × 2 列 = +24 列), 并写
  eval_reports/24_herd_threshold_sensitivity.csv
  诊断摘要 (逐 τ flag 率 / 权重均值 / 对基线 Spearman ρ)。下游 runner 步骤 3d →
  encode 把每个 τ 聚合成面板列 llm_vote_tone_hw_thrNN_{track}, 供 Stata 稳健性表
  逐 τ 重估主回归 (网格单一事实源 = core.config.herd_sensitivity_grid)。
  白话: 把"算抄稿"的门槛调松调紧各算一套打折权重, 一路带进最终 .dta,
  论文里用一张表证明回归结论不靠 0.35 这个具体数字。

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 24_herd_decay_processor.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**输入**: **硬依赖** stage 23 输出 `23_bert_tone.parquet` (代码显式禁止回退读 22/21 防磁盘残留污染, 见 main() 顶部硬依赖检查; 缺失即 `raise SystemExit(1)` 让编排器感知 DAG 契约违规; 取 `target_bank`/`日期`/`content_full`(或 '内容')/`content_ctx`/`content_ss`/`ss_is_fallback` 列)。

**处理步骤**: ①`compute_herd_weights(df)`: 按 `target_bank` 分组; ②对每组三轨各做 TF-IDF 向量化 (`max_features=MAX_FEATURES`=10000 按原始词频截断, `min_df` 比例化 min(MIN_DF, max(2, ceil(0.01·n))) 防套话词污染, as-of yearly vocab fit——年 t 文章的前驱计数只用 year≤t 文档拟合的向量空间保证历史不变); ③≤2000 篇/前缀 dense pairwise 余弦 / >2000 篇 7 天窗双指针分桶 O(N·window) 算余弦; ④时间窗 (`TIME_WINDOW_DAYS` 默认 7 天) 内文章 j 与更早文章 i 相似度 ≥ `SIMILARITY_THRESHOLD`(0.35, 闭边界 >=) 记为跟风前驱; ⑤生产路径输出阈值敏感性诊断 CSV (预注册 τ 网格默认 {0.25,0.30,0.40,0.45}, 逐 τ flag 率/权重分布/Spearman ρ vs 基线); ⑥保存。

**关键公式**: 衰减权重 `weight_j = 1 / (1 + n_similar_predecessors)` —— 原创首篇权重 1, 第 10 篇抄稿约 1/10, 防同一消息被各家转抄重复计数给情感指标注水。

**输出列**: `herd_weight_{full/ctx/ss}` + `n_similar_articles_{full/ctx/ss}` (6 列) + `herd_weight`/`n_similar_articles` (full 轨 NON-BREAKING 别名 2 列, v3.6.0 兼容) + 敏感性网格 `herd_weight_{track}_{tag}`/`n_similar_articles_{track}_{tag}` (默认 4 τ × 3 轨 × 2 = 24 列)。

**verified-universe 域门控**: 本阶段对**全部**文章 (含 stage 21 verified=False 的) 算 herd 权重——域门控不在此发生; 真正的'只保留 stage 21 verified 集'的 (docid, target_bank) semi-join 在下游 stage 45 panel runner 里完成 (见 memory panel-universe-consistency-audit: attention 族曾因分子绕过该 semi-join 泄漏 26.8% 伪文章)。本阶段产出是面板聚合情感时的逐文章降权乘子。

**外部依赖**: scikit-learn TfidfVectorizer + scipy (余弦/spearman); 纯 CPU, $0, 无 LLM/网络。确定性来自固定 TF-IDF 参数 + as-of vocab fit。

**DAG 位置**: 上游 stage 23 (硬依赖); 下游 **stage 45 panel runner 硬依赖** `24_herd_decay.parquet` (pipeline/panel/runner.py 的 main() 读取, 缺文件或缺关键列 target_bank/llm_sentiment_full/日期/llm_agreement_rate_full 即 sys.exit(1))——23→24→45 是结构性 always-on 链, 这正是把 23/24 提为 always-on 要消除的脆弱耦合。STAGES_MAIN 阶段24。

■ 白话说明

这一步在解决'同一条新闻被各家媒体抄来抄去导致情绪被重复计算'的问题。同一家银行的一条消息, 往往当天被几十家媒体转载、改写, 内容大同小异。如果把这几十篇都当成独立的'情绪表态'加起来, 这家银行那段时间的情绪就被严重注水了。这一步给每篇新闻数一数'它发出来之前 7 天内, 有几篇内容长得很像的旧文', 然后按这个数量打折: 头一篇原创算满分权重 1, 第十篇抄稿只算约 1/10。打比方就像开会发言, 同一个观点被十个人复述, 只能算一票多一点, 不能算十票。为什么需要它: 没有这个降权, 越是被疯狂转载的大事件 (往往情绪也越极端) 越会主导面板, 让结论被'转载量'而不是'真实信息量'带偏, 这是审稿人会盯的硬伤。它的产出 (每篇的折扣系数) 是后面把逐篇情绪汇总成'银行-年度'面板时必须乘上去的, 所以后续的面板构建那一步硬性依赖它——它一旦缺失或算错, 整张面板和论文里几乎所有回归都会受影响。注意: 这一步对所有文章都算折扣, 而'只统计真正讲银行-金科关系的那批文章'这道筛选是放在更下游的面板汇总环节做的。它同样按全文/银行相关段/银行金科同句段三种范围各算一套折扣, 各算各的不混用。
========================================================================
"""

import os
import sys

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import pairwise_distances

# Phase 7a-7: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 pipeline/sentiment/herd_decay.py 出发, 上溯 3 层抵达 news_process/ 的父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import herd_sensitivity_grid, load_config
from news_process.core.logging import pct4, setup_logging, sig4

# ============================================================================
# 1. 全局配置
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "24_herd_decay_processor"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

OUTPUT_DIR = CONFIG["paths"]["output_dir"]

# 跟风检测参数
HERD_CFG = CONFIG.get('herd_detection', {})
SIMILARITY_THRESHOLD = HERD_CFG.get('similarity_threshold', 0.35)
TIME_WINDOW_DAYS = HERD_CFG.get('time_window_days', 7)
MAX_FEATURES = HERD_CFG.get('max_features', 10000)
MIN_DF = HERD_CFG.get('min_df', 5)
MAX_DF = HERD_CFG.get('max_df', 0.9)
CHUNK_SIZE = HERD_CFG.get('chunk_size', 1000)  # 仅用于日志显示; >2000 篇分支已改 7 天窗双指针分桶 (W1), 不再用 chunked working_memory

# 阈值敏感性网格 (2026-06-13): 0.35 是研究者自由参数 (构念锚 Tetlock 2011 RFS 用
# 连续 staleness 不设硬阈值), 故对网格内每个 τ 在**同一** TF-IDF/余弦矩阵上复算
# 前驱计数 (零额外向量化成本), 输出 herd_weight_{track}_{tag} 供面板层做
# llm_vote_tone_hw_{tag}_{track} 稳健性回归。单一事实源 = core.config.herd_sensitivity_grid。
# 白话: "相似到多少算抄稿"是自己定的门槛, 这里把门槛调松调紧各算一套权重,
# 论文用它证明结论不靠 0.35 这个数。
SENS_THRESHOLDS, SENS_TAGS = herd_sensitivity_grid(CONFIG)


# ============================================================================
# 2. 核心算法: 分块相似度计算
# ============================================================================

def _build_tfidf_vectorizer(n_docs: int, *, relaxed: bool = False) -> TfidfVectorizer:
    """构造 TF-IDF vectorizer, 其 df 阈值随组规模 (n_docs) 自适应保持合法。

    fix(omni-g-herd-01, 2026-06-11): min_df 比例化 (proportional df threshold)。
    原实现 min_df=MIN_DF 为**绝对**文档数: n=6 的组配合 max_df=0.9 (floor(5.4)=5)
    把存活词表压到"恰好 5/6 篇共现"的 boilerplate 子空间 → 余弦相似度系统性膨胀
    (盘上实证 +17%~∞ flags), 且与 n≤MIN_DF 的 relaxed 分支 (min_df=1) 形成断崖
    不连续 → 0.35 阈值跨银行不可比。现改 min(MIN_DF, max(2, ceil(0.01·n))):
    小/中组 min_df=2 (仅剪 hapax 噪声), n≳200 平滑爬升, n≥~500 封顶于 MIN_DF
    (大组与历史行为一致); 另加 max_df 守卫 — 若 floor(max_df·n) ≤ min_df
    (df-band 退化为近全员共现带), 放开 max_df=1.0 而非把 min_df 压回退化带。

    白话: min_df/max_df 是"一个词至少/至多出现在多少篇文章里才保留"的门槛。
    老写法用固定篇数, 对只有几篇新闻的小银行来说门槛过高, 剩下的全是
    "本报讯""记者报道"这类套话词, 任何两篇都显得很像, 跟风被大量误报。
    新写法让门槛随组的大小按比例伸缩: 组小门槛低, 组大门槛逐步升到原值,
    保证不同规模的银行用大致同一把尺子量相似度。
    """
    if relaxed or n_docs < 4:
        # 微型组 (n<4): 任何 df 剪枝都会让词表退化, 直接放开
        min_df = 1
        max_df = 1.0
    else:
        # 比例化下限 2 (剪 hapax), 按 1%·n 爬升, 上限 MIN_DF (config 绝对计数 cap)
        min_df = int(min(MIN_DF, max(2, int(np.ceil(0.01 * n_docs)))))
        max_df = MAX_DF
        if isinstance(max_df, float) and 0 < max_df < 1.0:
            max_allowed_df = int(np.floor(max_df * n_docs))
            if max_allowed_df <= min_df:
                # fix(omni-g-herd-01): df-band 退化守卫 — 小 n 下 max_df 把允许带
                # 收窄到 [min_df, min_df] 或更窄时, 放开 max_df 保留全部 ≥min_df
                # 特征, 避免相似度在近全员共现子空间被强行抬高
                max_df = 1.0

    return TfidfVectorizer(
        max_features=MAX_FEATURES,
        min_df=min_df,
        max_df=max_df,
        analyzer='char_wb',  # 中文友好: 字符级 n-gram
        ngram_range=(2, 4),
        dtype=np.float32,  # 节省内存
    )


def _fit_tfidf_with_fallback(texts: list, *, bank_name=None, track=None):
    """拟合 TF-IDF, 失败时透明降级 relaxed 参数重试; 返回矩阵或 None。

    fix(omni-g-herd-03, 2026-06-11): 原两层 ValueError fallback 均零日志 — 走
    relaxed (min_df=1/max_df=1.0) 的组其相似度刻度 (全词表) 与主参数组不同, 二次
    失败整组 weight 保持 1.0, 用户无法审计哪些 (bank, track) 降级 (违反降级透明
    红线, 同族 F7/F16/F21/F22)。现两分支各记 logger.warning(bank/track/n_docs/原因)。

    fix(omni-g-herd-02, 2026-06-11): max_features 截断咬合 (词表撞 cap) 时记
    logger.warning 披露规模依赖的相似度膨胀风险 (见模块头 ⚠ 披露)。
    """
    n_docs = len(texts)
    try:
        vectorizer = _build_tfidf_vectorizer(n_docs)
        tfidf_matrix = vectorizer.fit_transform(texts)
    except ValueError as exc:
        logger.warning(
            f"  [herd] TF-IDF 主参数 fit 失败, 降级 relaxed (min_df=1/max_df=1.0): "
            f"bank={bank_name}, track={track}, n_docs={n_docs}, 原因: {exc}. "
            f"该组相似度刻度与未降级组不同 (词表带放宽), 审计时注意。"
        )
        try:
            vectorizer = _build_tfidf_vectorizer(n_docs, relaxed=True)
            tfidf_matrix = vectorizer.fit_transform(texts)
        except ValueError as exc2:
            logger.warning(
                f"  [herd] relaxed 重试仍失败, 该组本轨保持 weight=1.0 / count=0: "
                f"bank={bank_name}, track={track}, n_docs={n_docs}, 原因: {exc2}"
            )
            return None
    # max_features 截断透明化 (fix(omni-g-herd-02)): 词表撞 cap 说明按原始词频截断已咬合
    # (高频 boilerplate 子空间, 判别长尾缺席 → 余弦规模依赖膨胀)。2026-06-24 cap 由 10000
    # 上调至 5e6 (远超现实 bank-year 词表), 故此 warning 现为极端规模 tripwire — 正常 run
    # 不应触发; 若触发说明该组词表 >5e6, 须改 HashingVectorizer 或按 IDF 选 top-k。
    if MAX_FEATURES and len(vectorizer.vocabulary_) >= MAX_FEATURES:
        logger.warning(
            f"  [herd] max_features={MAX_FEATURES} 截断咬合: bank={bank_name}, "
            f"track={track}, n_docs={n_docs} — 词表达 cap, 相似度被压入高频 ngram 子空间, "
            f"刻度可能膨胀 (cap 已=5e6 极端 tripwire; 改 HashingVectorizer/IDF top-k 选词)"
        )
    return tfidf_matrix


def _dense_similar_counts(tfidf_matrix, dates: list, thresholds=None) -> np.ndarray:
    """≤2000 篇稠密分支 (参照实现): 全 N×N 余弦 + 7 天窗下三角 mask 的前驱计数。

    语义: 对每篇 i, 计 {j : j<i (index, 已排序故=日期序), |date_i-date_j|<=window,
    cos_sim(i,j) >= 阈值}; NaT 篇不计数也不作候选。

    Args:
        thresholds: 阈值敏感性 (2026-06-13)。None (默认) → 单阈值
            SIMILARITY_THRESHOLD, 返回 1D (n,) — 与历史签名/语义逐位兼容;
            list[float] → 同一余弦矩阵上逐阈值计数, 返回 2D (n, len(thresholds)),
            列序与入参一致 (多阈值零额外向量化成本, 只多 K-1 次比较)。
    """
    n_articles = len(dates)
    thr_list = [SIMILARITY_THRESHOLD] if thresholds is None else list(thresholds)
    _epoch = pd.Timestamp('1970-01-01')
    dates_num = np.array(
        [(d - _epoch).days if pd.notna(d) else np.nan for d in dates],
        dtype=np.float64)
    time_diff = np.abs(np.subtract.outer(dates_num, dates_num))
    time_diff = np.nan_to_num(time_diff, nan=float(TIME_WINDOW_DAYS + 1))
    valid_mask = (time_diff <= TIME_WINDOW_DAYS) & np.tril(
        np.ones((n_articles, n_articles), dtype=bool), k=-1)
    sim_matrix = 1.0 - pairwise_distances(tfidf_matrix, metric='cosine')
    counts = np.stack(
        [((sim_matrix >= thr) & valid_mask).sum(axis=1) for thr in thr_list],
        axis=1).astype(int)
    return counts[:, 0] if thresholds is None else counts


def _bucketed_similar_counts(tfidf_matrix, dates: list, thresholds=None) -> np.ndarray:
    """>2000 篇 M0 规模分支: 7 天窗双指针分桶, O(N·window), 与 _dense_similar_counts 数值逐位等价。

    thresholds 语义与 _dense_similar_counts 一致: None → 1D 基线 (历史兼容);
    list[float] → 2D (n, K), 同一窗内余弦向量上逐阈值计数。

    前置: dates 已升序排序 (NaT 末尾) — 由 compute_herd_weights 的 sort_values('日期')
    保证。因 index 序 = 日期序, 每篇 i 的候选前驱仅落在 [date_i-window, date_i] 的连续
    滑窗 [lo, i) 内; 双指针使左界 lo 单调右移, 每篇只对窗内候选算余弦, 把 per-bank 成本
    从 O(N^2) 降到 O(N*window)。NaT 篇不计数也不作候选 (与稠密分支一致)。

    白话: 要判断一篇新闻是不是"跟风", 只需和它前 7 天内的旧文比相似度,
    没必要和几年前的全部文章两两都比一遍。文章已按日期排好队, 用一个
    左指针标记"7 天窗口的起点", 它只会往右走不回头, 于是每篇文章只和
    窗口内的几十篇邻居比较, 几十万篇的银行也算得动, 且结果与笨办法
    (全两两比较) 逐位相同。
    """
    n_articles = len(dates)
    thr_list = [SIMILARITY_THRESHOLD] if thresholds is None else list(thresholds)
    _epoch = pd.Timestamp('1970-01-01')
    dates_num = np.array(
        [(d - _epoch).days if pd.notna(d) else np.nan for d in dates],
        dtype=np.float64)
    similar_counts = np.zeros((n_articles, len(thr_list)), dtype=int)
    lo = 0
    for i in range(n_articles):
        di = dates_num[i]
        if np.isnan(di):
            continue  # NaT: 与稠密分支 nan_to_num>window 一致, 不计数
        # 双指针: 左界右移直到 dates_num[lo] 落入 [di-window, di]
        # (有效前缀里无 NaN; isnan 守卫纯防御以兼容任意 NaT 排序)
        while lo < i and (np.isnan(dates_num[lo])
                          or di - dates_num[lo] > TIME_WINDOW_DAYS):
            lo += 1
        if lo >= i:
            continue
        # 仅对窗内候选 [lo, i) 算余弦 (稀疏行 × 稀疏块, 窗口仅几十~几百篇)
        # i:i+1 切片保持 2D (稀疏 CSR 与 numpy dense 通用; 裸 [i] 在 dense 下退化 1D)
        sims = 1.0 - pairwise_distances(
            tfidf_matrix[i:i + 1], tfidf_matrix[lo:i], metric='cosine')[0]
        # fix(herd-bucket-nat, metric-audit 2026-06-10): 排除窗内 NaT 候选, 与 _dense
        # (nan_to_num>window 已排除 NaT) 逐位对齐。生产 sort 使 NaT 末位故一般不触发, 但
        # 任意 NaT 排列下双指针窗 [lo,i) 可能含内部 NaT, 此守卫保证无条件等价 (3rd-layer P3)。
        _cand_valid = ~np.isnan(dates_num[lo:i])
        for k, thr in enumerate(thr_list):
            similar_counts[i, k] = int(
                np.count_nonzero((sims >= thr) & _cand_valid))
    return similar_counts[:, 0] if thresholds is None else similar_counts


# ============================================================================
# 进程并行 worker + 工况自适应后端 (perf fix 2026-07-26, F20)
# ============================================================================
# 病根: 逐银行的 TF-IDF + 余弦是纯 Python/BLAS 混合的**单线程**循环。生产实测:
#   1,247 家银行 (991 家 ≥2 篇可算), 前 50 家 (遍历序含工/建/农/中/中信五大行,
#   占全部文章 62.3%) 耗时 **103 分钟仍未走完** → 按逐年度前缀成本模型 (前 50 家
#   = 29.75% 总成本) 外推**全程 ≈5.8 小时**, 撞穿父端超时被强杀。
# ⚠ 反直觉的成本结构 (实测): 最贵的**不是**巨型行而是**卡在 2000 篇以下的中型行** ——
#   超 2000 篇的年度前缀走 7 天窗双指针 O(N·window), 而 2000 篇以下走 dense O(n²);
#   故北京银行(1,855篇)/深圳前海微众(1,676篇)/江苏银行(1,802篇) 反比工行(24,684篇) 贵。
# 修法 (镜像 stage 15 §1b / stage 22 已验证范式): 各银行**完全独立** (无跨行状态,
#   TF-IDF 逐行拟合, as-of 年度前缀亦在行内) → 提升 worker 为模块级走 loky 进程后端。
# 字节等价 (byte-equivalent-by-construction):
#   · 逐银行计算彼此无依赖, worker 内排序键/算法与串行分支**同一函数**;
#   · 结果按**提交序**回收并逐银行 `df.loc[indices, col] = ...` 写回 —— 各银行 indices
#     两两不交, 故写回顺序不改任何格的值;
#   · 三个 herd 计数累加器是**整数求和**, order-independent。
# ⚠ worker 绝不写日志: 本模块**模块级**调 `setup_logging` (L137), 子进程 import 时其
#   首条日志会把父进程 24_herd_decay_processor.log 从头截断 (2026-07-24 实弹先例);
#   已核实 `_compute_similar_counts_for_track` 内**零** logger 调用 → 静音无诊断损失。
_PROC_PARALLEL_MIN_BANKS = 200   # ≥200 家可算银行才切进程后端 (之下串行, 免 spawn 开销)
_PROC_PARALLEL_MAX_WORKERS = 12  # 同 stage 22: 严禁 -1 (每 worker 各持 TF-IDF 矩阵)


def _proc_workers() -> int:
    """进程臂 worker 数 = min(配置值, CPU 核数); config: herd_detection.proc_workers。"""
    try:
        _v = HERD_CFG.get('proc_workers', _PROC_PARALLEL_MAX_WORKERS)
        _v = int(_v) if not isinstance(_v, bool) else _PROC_PARALLEL_MAX_WORKERS
    except (TypeError, ValueError):
        _v = _PROC_PARALLEL_MAX_WORKERS
    return max(1, min(_v, os.cpu_count() or _PROC_PARALLEL_MAX_WORKERS))


def _parallel_kwargs(n_banks: int) -> dict:
    """按工况规模选 joblib 后端: 大 → 进程 (真并行); 小 → 串行 (免 spawn 开销)。"""
    if n_banks >= _PROC_PARALLEL_MIN_BANKS:
        return {'n_jobs': _proc_workers(), 'prefer': 'processes'}
    return {'n_jobs': 1, 'prefer': 'threads'}


def _silence_worker_logging() -> None:
    """**仅在 loky/mp 子进程内**彻底静音 logging (防首条日志截断父进程 <stage>.log)。幂等。

    F42 (2026-07-31): 补一道进程身份闸。原实现无条件执行, 而
    ``logging.disable(CRITICAL)`` 与 ``removeHandler`` 都是**进程级全局状态**, 一旦在
    父进程里执行就**再不恢复** —— 而本函数确实会在父进程里被执行: `_herd_bank_worker`
    在串行回落臂 (``_par['prefer'] != 'processes'``, 即可算银行 < 200 家) 是被父进程
    **直接调用**的。后果: 该阶段自那一行起**整条日志全哑**, 后面的「已回写 N/M」
    「三轨跟风检测完成」及三轨汇总统计一个字都不落盘。而 CLAUDE.md 已记载过
    「文件不存在」与「阶段一个字没写」在终端上不可区分的踩坑形态 —— 这正是同一类。
    生产 T=19 (1,247 家银行) 走并行臂不触发, 故它只在 **dev/小样/单测**里咬人,
    也就是最需要看日志的场合。
    ``multiprocessing.parent_process()`` 是可靠判据 (实测: 父进程与 joblib 线程臂均
    返回 None, loky worker 返回进程对象; 阶段自身由 ``subprocess.Popen`` 拉起, 同样
    是 None)。
    """
    import logging as _logging
    import multiprocessing as _mp

    if _mp.parent_process() is None:
        return  # 父进程 (含线程臂 / 串行回落臂): 绝不摘 handler, 绝不 disable
    for _h in list(logger.handlers):
        logger.removeHandler(_h)
    _logging.disable(_logging.CRITICAL)


def _herd_bank_worker(bank_df, full_col: str, has_ctx: bool, has_ss: bool,
                      thresholds: list, bank_name=None):
    """单银行三轨跟风计数 worker (模块级, 供 loky pickle-by-ref)。

    返回 (indices, full_counts, ctx_counts, ss_counts); 与串行分支**同一算法同一函数**,
    仅执行位置不同。调用方按提交序回收后写回 df (各银行 indices 不交 → 写回序无关)。"""
    _silence_worker_logging()
    _sort_keys = ['日期'] + [c for c in ('标题', '内容') if c in bank_df.columns]
    bank_df = bank_df.sort_values(_sort_keys, kind='stable').copy()
    indices = bank_df.index.tolist()
    dates = bank_df['日期'].tolist()
    full_counts = _compute_similar_counts_for_track(
        bank_df, full_col, dates, bank_name=bank_name, thresholds=thresholds)
    ctx_counts = _compute_similar_counts_for_track(
        bank_df, 'content_ctx', dates, bank_name=bank_name,
        thresholds=thresholds) if has_ctx else full_counts
    ss_counts = _compute_similar_counts_for_track(
        bank_df, 'content_ss', dates, bank_name=bank_name,
        thresholds=thresholds) if has_ss else full_counts
    return indices, full_counts, ctx_counts, ss_counts


def _compute_similar_counts_for_track(
    bank_df: pd.DataFrame, text_col: str, dates: list, *, bank_name=None,
    thresholds=None,
) -> np.ndarray | None:
    """对单一文本列计算同银行 + 时间窗口内的"前驱跟风计数"向量。

    抽出 v3.5.0 单轨实现的核心算法以支持多轨复用 (Plan E P1 B3 双轨; v3.9.0 三轨,
    full / ctx / ss 每轨各调一次)。text_col 参数化 → 同一算法供三轨复用。
    返回 None 表示无法向量化 (空文本 / TF-IDF 失败), 调用方应保留 weight=1.0。

    fix(omni-g-herd-05, 2026-06-11): as-of yearly vocab fit — 原实现对单银行
    **全历史** texts 一次 fit_transform, 历史文章对的余弦使用了由未来文档频率决定
    的 IDF 权重与 df 词表剪裁 (前驱计数构念严格后视, 向量空间却含前视) → 样本扩展
    时历史 herd_weight 非不变 (0.35 阈值附近计数可翻转)。现按年截断: 年 t 文章的
    计数仅在 year ≤ t 文档拟合的向量空间内计算 (前驱候选集不变 — 7 天窗下三角本就
    只看更早文章); 年内残余前视为接受粒度 (面板为 bank-year, 年级 as-of 已足)。
    NaT 日期文章排除出 fit (年份未知; 既有语义下其本就不计数、不作候选)。

    Args:
        bank_df: 单银行子集, 已按日期升序排序 (NaT 末位, 由调用方 sort_values 保证)。
        text_col: 文本列名 ('content_full' for full, 'content_ctx' for ctx,
            'content_ss' for ss 银行+金科同句; 三者均含标题)。
        dates:    与 bank_df 对齐的日期列表 (含 NaT)。
        bank_name: 银行名, 仅用于降级/截断透明日志 (fix(omni-g-herd-03))。
        thresholds: 阈值敏感性 (2026-06-13)。None → 单基线阈值, 返回 1D (历史
            兼容); list[float] → 同一年度前缀 TF-IDF 空间上逐阈值计数, 返回
            2D (n, K), 列序与入参一致。

    Returns:
        np.ndarray[int] 形状 (n,) 或 (n, K), 每元素为 i 的"早于 i 且相似 ≥ 阈值"
        前驱数; 完全无法向量化 (全空文本) 返回 None。
    """
    thr_list = [SIMILARITY_THRESHOLD] if thresholds is None else list(thresholds)
    texts = bank_df[text_col].fillna('').astype(str).tolist()
    non_empty = [t for t in texts if len(t.strip()) > 0]
    if len(non_empty) < 2:
        return None

    n_articles = len(texts)
    counts = np.zeros((n_articles, len(thr_list)), dtype=int)

    # 非 NaT 前缀: 调用方已按日期升序排序 (NaT 末位), 故有效日期文档构成连续前缀
    # [0, dated_n); 首个 NaT 即截断 (防御任意排列 — NaT 后的文档不进任何年度 fit)。
    years: list[int] = []
    for d in dates:
        if pd.isna(d):
            break
        years.append(int(pd.Timestamp(d).year))
    dated_n = len(years)
    if dated_n < 2:
        # 可计数文档不足 2 篇 (其余皆 NaT): 与旧实现等价 (NaT 不计数), 全 0
        return counts[:, 0] if thresholds is None else counts

    years_arr = np.asarray(years)
    for t in np.unique(years_arr):
        # 年度前缀 [0, prefix_end) = 全部 year ≤ t 文档; 本年文章区间 [target_lo, prefix_end)
        prefix_end = int(np.searchsorted(years_arr, t, side='right'))
        target_lo = int(np.searchsorted(years_arr, t, side='left'))
        if prefix_end < 2:
            continue  # 首年仅 1 篇: 无前驱对可计
        sub_texts = texts[:prefix_end]
        if sum(1 for s in sub_texts if s.strip()) < 2:
            continue
        tfidf_matrix = _fit_tfidf_with_fallback(
            sub_texts, bank_name=bank_name, track=text_col)
        if tfidf_matrix is None:
            continue  # 该年度前缀 fit 失败 (已 warning): 本年文章保持 count=0
        sub_dates = dates[:prefix_end]
        if prefix_end <= 2000:
            sub_counts = _dense_similar_counts(tfidf_matrix, sub_dates,
                                               thresholds=thr_list)
        else:
            # M0 规模 (>2000 篇/前缀): 7 天窗双指针分桶替换原 O(N^2) 纯 Python 双循环。
            # 头部银行 (工农中建招) 全量 2007-2025 可达数十万篇, 原 O(N^2) 是 stage 24
            # 的 wall-clock cliff + N×N 余弦 OOM 悬崖。_bucketed 与 _dense 数值逐位等价,
            # 由 tests/test_24_herd_decay_bucketing.py 在 >2000 fixture 上对拍守护。
            sub_counts = _bucketed_similar_counts(tfidf_matrix, sub_dates,
                                                  thresholds=thr_list)
        # 仅采纳本年文章的计数 (前驱候选 = 前缀内更早文章, 跨年 7 天窗自然覆盖)
        counts[target_lo:prefix_end] = sub_counts[target_lo:prefix_end]
    return counts[:, 0] if thresholds is None else counts


def compute_herd_weights(df: pd.DataFrame) -> pd.DataFrame:
    """对同一银行在时间窗口内的新闻进行**三轨**跟风检测 (Plan E P1 B3, v3.6.0; ss v3.9.0)。

    算法流程 (对 full / ctx / ss 三轨各跑一次):
      1. 按 target_bank 分组
      2. 对每组新闻进行 TF-IDF 向量化 (轨 1 用 'content_full' 标题+全文, 缺列回退
         '内容'/'正文'/'content'; 轨 2 用 'content_ctx'; 轨 3 用 'content_ss'
         标题+银行∧金科同句窗, 缺列回退 full)
         — fix(omni-g-herd-04, 2026-06-11): 原文档误称轨 1 为裸正文列, 与病根A修复
         后的实现 (优先 content_full) 不符, 已同步
      3. 计算余弦距离 (≤2000 篇 dense / >2000 篇 7 天窗双指针分桶, W1 2026-06-05)
      4. 在时间窗口内, 若文章 j 与更早的文章 i 的相似度 ≥ 阈值 (闭边界, 代码 >=),
         则 j 被标记为"跟风", 衰减权重递减
      5. 衰减公式: weight_j = 1 / (1 + n_similar_predecessors)

    v3.6.0 / v3.9.0 修复 (Edwards 2001 ORM measurement-treatment matching):
      原 v3.5.0 仅对全文计算 herd_weight 单列, 被下游同时施加到
      _full / _ctx 两条轨道, 造成 _ctx 路径被"全文相似度"惩罚。
      v3.6.0 输出 herd_weight_full + herd_weight_ctx 两列;
      v3.9.0 再加 herd_weight_ss (银行+金科同句相似度) → 现为
      full/ctx/ss 三轨, 下游按轨匹配。

    Args:
        df: 篇章级 DataFrame, 须含 'target_bank', '日期', 'content_full'(或 '内容') 列;
            'content_ctx' 可选 — 缺失时 ctx 轨回退到 full 轨文本 (即与 full 同值);
            'content_ss' 可选 — 缺失时 ss 轨回退到 full 轨文本; 'ss_is_fallback' 可选
            (由 stage 14 物化, =True 表示该行 content_ss 镜像回退到了全文 body)。

    Returns:
        df: 附加 'herd_weight_full' / 'herd_weight_ctx' / 'herd_weight_ss' /
            'n_similar_articles_full' / 'n_similar_articles_ctx' /
            'n_similar_articles_ss' 六列;
            另按 SENS_TAGS 网格 (2026-06-13 阈值敏感性) 附加
            'herd_weight_{track}_{tag}' / 'n_similar_articles_{track}_{tag}'
            每轨每 τ 两列 (默认网格 4 τ × 3 轨 = +24 列)。

    白话: 同一家银行的新闻常被各家媒体转抄, 同一条消息若被算 10 遍,
    情感指标就被注了水。这里给每篇文章数一数"它发布前 7 天内有几篇
    长得很像的前文" (记为 n), 然后把它的权重打折成 1/(1+n): 头一篇原创
    权重 1, 第 10 篇抄稿权重只剩约 1/10。full 轨看标题+全文的相似,
    ctx 轨只看与目标银行相关的那段文字的相似, ss 轨只看"银行和金科同句出现"
    的那段文字的相似, 三轨各自打分互不混用。
    """
    logger.info("=" * 60)
    logger.info("步骤 1: 跟风/抄袭新闻检测与衰减加权 (三轨 v3.9.0)")
    logger.info("=" * 60)
    logger.info(f"  参数: similarity_threshold={sig4(SIMILARITY_THRESHOLD)}, "
                f"time_window={TIME_WINDOW_DAYS}天, "
                f"max_features={MAX_FEATURES}, chunk_size={CHUNK_SIZE}")
    if SENS_TAGS:
        logger.info(f"  阈值敏感性网格: {SENS_THRESHOLDS} → 列后缀 {SENS_TAGS} "
                    f"(同一 TF-IDF/余弦一遍式复算, 基线列不变)")

    # 确保日期列为 datetime
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')

    # 三轨文本列解析
    # full 轨: 优先 content_full (含标题), 缺列回退 '内容' / '正文' / 'content'
    # P1 修复 (metric-audit 2026-06-02, 病根A): full 轨优先 content_full (含标题, 与
    # 加权对象 _full 情感同源), 缺列回退 '内容'/'正文'/'content'.
    full_col = 'content_full' if 'content_full' in df.columns else (
        '内容' if '内容' in df.columns else (
            '正文' if '正文' in df.columns else 'content'))
    has_full = full_col in df.columns
    # ctx 轨: 来自 stage 14 ctx_materializer (fix(omni-g-herd-04, 2026-06-11):
    # 原注释错标到 stage 21, 与本文件头部/现行架构矛盾); 缺失则回退 full
    has_ctx = 'content_ctx' in df.columns
    # ss 轨 (v3.9.0 第三轨, 银行+金科同句): 同来自 stage 14 ctx_materializer 物化的
    # 'content_ss' (标题+银行∧金科同句窗); 缺失则回退 full (镜像 ctx 回退语义)。
    # 'ss_is_fallback' 由 stage 14 物化 (=True 表示该行无共现已回退全文 body), 供
    # 下方独立性诊断门控 (回退行 ss≡full 不参与相关性判定); 缺该 flag 列时下方
    # 诊断按"全部非回退"宽松处理 (graceful)。
    has_ss = 'content_ss' in df.columns

    if not has_full:
        logger.warning(f"  文本列 '{full_col}' 不存在, 所有 herd_weight 设为 1.0")
        df['herd_weight_full'] = 1.0
        df['herd_weight_ctx'] = 1.0
        df['herd_weight_ss'] = 1.0
        df['n_similar_articles_full'] = 0
        df['n_similar_articles_ctx'] = 0
        df['n_similar_articles_ss'] = 0
        # NON-BREAKING alias (F-B 修)
        df['herd_weight'] = 1.0
        df['n_similar_articles'] = 0
        return df

    if not has_ctx:
        logger.warning(
            "  'content_ctx' 列不存在 (stage 14 ctx_materializer 未跑?), "
            "ctx 轨回退至全文计算 — 此时 herd_weight_ctx ≡ herd_weight_full, "
            "ctx 轨退化为 full 轨同值 (非独立轨)。建议先执行 stage 14 物化 content_ctx。"
        )

    if not has_ss:
        # ss 轨缺列警告镜像 ctx (v3.9.0 第三轨): 缺 content_ss → ss 轨回退全文,
        # herd_weight_ss ≡ herd_weight_full, 不构成真三轨。
        logger.warning(
            "  'content_ss' 列不存在 (stage 14 ctx_materializer 未物化同句轨?), "
            "ss 轨回退至全文计算 — 此时 herd_weight_ss ≡ herd_weight_full, "
            "不构成真三轨。建议先执行 stage 14 物化 content_ss。"
        )

    # 初始化结果列 (基线 + 阈值敏感性网格; 无新闻/无法向量化组保持 weight=1.0)
    df['herd_weight_full'] = 1.0
    df['herd_weight_ctx'] = 1.0
    df['herd_weight_ss'] = 1.0  # v3.9.0 第三轨 (银行+金科同句) 基线权重
    df['n_similar_articles_full'] = 0
    df['n_similar_articles_ctx'] = 0
    df['n_similar_articles_ss'] = 0  # v3.9.0 第三轨 (银行+金科同句) 基线计数
    for _tag in SENS_TAGS:
        for _tn in ('full', 'ctx', 'ss'):
            df[f'herd_weight_{_tn}_{_tag}'] = 1.0
            df[f'n_similar_articles_{_tn}_{_tag}'] = 0

    if 'target_bank' not in df.columns:
        logger.warning("  'target_bank' 列不存在, 所有 herd_weight 设为 1.0")
        # NON-BREAKING alias (F-B 修)
        df['herd_weight'] = df['herd_weight_full']
        df['n_similar_articles'] = df['n_similar_articles_full']
        return df

    bank_groups = df.groupby('target_bank')
    n_banks = len(bank_groups)
    logger.info(f"  共 {n_banks} 家银行待处理 (三轨)")

    # 规模画像 (deepen_runtime, round8 2026-06-29): articles-per-bank 分布 (p50/p90/max) +
    # 触发 >2000 篇分支 (7 天窗双指针分桶 O(N·window)) 而非 dense pairwise (O(N^2)) 的银行数,
    # 让"本次实际走哪条计算路径主导"自文档化, 便于全量 run 审计计算复杂度 regime。盘面 T=2
    # 小样下全部走 dense; 全量 约1,819万/T=19 头部大行 (工农中建招) 才进分桶分支。⚠ 注: 真正的
    # dense/bucketed 切换在 _compute_similar_counts_for_track 按**年度前缀** (prefix_end<=2000)
    # 逐年判定, 故 bank 级篇数是其上界代理 (年度切分后实际更小)。纯只读 groupby 规模, 整块
    # try/except, 绝不回写 df/产物 (golden-safe)。
    try:
        _grp_sizes = bank_groups.size()
        if not _grp_sizes.empty:
            _n_over = int((_grp_sizes > 2000).sum())
            _n_calc = int((_grp_sizes >= 2).sum())  # <2 篇组直接 continue, 不算 herd
            logger.info(
                f"  规模画像: articles/bank 分布 p50={sig4(float(_grp_sizes.quantile(0.50)))} "
                f"p90={sig4(float(_grp_sizes.quantile(0.90)))} max={int(_grp_sizes.max()):,d}; "
                f"可算银行 (≥2 篇)={_n_calc:,d}/{n_banks:,d}; "
                f"超 2000 篇 (→7天窗双指针分桶分支, bank 级上界代理) 银行={_n_over:,d} "
                f"({'全部走 dense pairwise (O(N^2))' if _n_over == 0 else '部分进分桶分支 (O(N·window))'})"
            )
    except Exception as _e_sz:  # noqa: BLE001  纯日志, 绝不影响产物
        logger.warning(f"  规模画像打印失败 (不影响产物): {_e_sz}")

    total_herd_full = 0
    total_herd_ctx = 0
    total_herd_ss = 0  # v3.9.0 第三轨 (银行+金科同句) 跟风篇数累计

    # 阈值敏感性 (2026-06-13): 第 0 列 = 基线 SIMILARITY_THRESHOLD, 第 1.. 列
    # = SENS_THRESHOLDS — 同一 TF-IDF/余弦矩阵一遍式复算, 不重复向量化。
    _all_thr = [SIMILARITY_THRESHOLD] + SENS_THRESHOLDS

    # ── 工况自适应后端 (F20, 2026-07-26): 各银行完全独立 → 大工况走 loky 进程后端 ──
    # 与串行逐字节等价 (见 _herd_bank_worker 上方论证); IPC 只传 worker 真正用到的列
    # (排序键 日期/标题/内容 + 三轨文本), 避免把 stage 23 的宽表整片 pickle 过去。
    # 列裁剪在**建表时**即做: 否则 1,247 份全宽切片 (stage 23 宽表) 会在内存里再复制一份 df。
    _need = [c for c in dict.fromkeys(
        ['日期', '标题', '内容', full_col, 'content_ctx', 'content_ss'])
        if c in df.columns]
    _calc_banks = [(_n, _g[_need]) for _n, _g in bank_groups if len(_g) >= 2]
    _n_calc_banks = len(_calc_banks)
    _par = _parallel_kwargs(_n_calc_banks)
    logger.info(
        f"  跟风计数后端={_par['prefer']} (n_jobs={_par['n_jobs']}), "
        f"可算银行 {_n_calc_banks:,d}/{n_banks:,d} (<2 篇者跳过); "
        f"IPC 列={_need} — 与串行逐字节等价, 仅墙钟")

    if _par['prefer'] == 'processes':
        from joblib import Parallel, delayed
        _results = Parallel(**_par)(
            delayed(_herd_bank_worker)(_g, full_col, has_ctx, has_ss, _all_thr, _n)
            for _n, _g in _calc_banks)
    else:
        _results = [_herd_bank_worker(_g, full_col, has_ctx, has_ss, _all_thr, _n)
                    for _n, _g in _calc_banks]

    # 按**提交序**回收写回 (各银行 indices 两两不交 → 写回序不改任何格的值)
    for bank_idx, (indices, full_counts, ctx_counts, ss_counts) in enumerate(_results):
        # 按银行向量化赋值 (.loc[标签列表] 与 counts 行序一致 — bank_df 排序序;
        # 替换原逐行 .at 循环, 数值等价, 多阈值下避免 (1+K)×3 列 × n 行的逐格写)
        for _tn, _counts in (('full', full_counts), ('ctx', ctx_counts),
                             ('ss', ss_counts)):
            if _counts is None:
                continue
            _base = _counts[:, 0]
            df.loc[indices, f'n_similar_articles_{_tn}'] = _base
            df.loc[indices, f'herd_weight_{_tn}'] = 1.0 / (1.0 + _base)
            if _tn == 'full':
                total_herd_full += int((_base > 0).sum())
            elif _tn == 'ctx':
                total_herd_ctx += int((_base > 0).sum())
            else:  # ss (v3.9.0 第三轨)
                total_herd_ss += int((_base > 0).sum())
            for _j, _tag in enumerate(SENS_TAGS, start=1):
                _cj = _counts[:, _j]
                df.loc[indices, f'n_similar_articles_{_tn}_{_tag}'] = _cj
                df.loc[indices, f'herd_weight_{_tn}_{_tag}'] = 1.0 / (1.0 + _cj)

        if (bank_idx + 1) % 50 == 0:
            logger.info(f"  已回写 {bank_idx + 1}/{_n_calc_banks} 家可算银行")

    n_total = len(df)
    logger.info(f"  三轨跟风检测完成:")
    logger.info(f"    总新闻数: {n_total:,}")
    logger.info(f"    full 轨跟风: {total_herd_full:,} "
                f"({pct4(total_herd_full/max(n_total,1))})")
    logger.info(f"    ctx  轨跟风: {total_herd_ctx:,} "
                f"({pct4(total_herd_ctx/max(n_total,1))})")
    logger.info(f"    ss   轨跟风: {total_herd_ss:,} "
                f"({pct4(total_herd_ss/max(n_total,1))})")
    logger.info(f"    herd_weight_full mean={sig4(df['herd_weight_full'].mean())}, "
                f"min={sig4(df['herd_weight_full'].min())}")
    logger.info(f"    herd_weight_ctx  mean={sig4(df['herd_weight_ctx'].mean())}, "
                f"min={sig4(df['herd_weight_ctx'].min())}")
    logger.info(f"    herd_weight_ss   mean={sig4(df['herd_weight_ss'].mean())}, "
                f"min={sig4(df['herd_weight_ss'].min())}")

    # 前驱计数分布画像 (deepen_runtime, 2026-06-29 round7): 三轨各报 n_similar_articles
    # 的分位 (p50/p75/p90/max) + 命中前驱 (>0) 篇占比, 让"每篇前面压着几篇相似旧文"
    # 自文档化。纯只读日志局部量 (绝不回写 df/产物), 整块 try/except 防边缘数据崩。
    try:
        for _tn in ('full', 'ctx', 'ss'):
            _ncol = f'n_similar_articles_{_tn}'
            if _ncol not in df.columns:
                continue
            _ns = pd.to_numeric(df[_ncol], errors='coerce').dropna()
            if _ns.empty:
                continue
            _herd_ns = _ns[_ns > 0]  # 仅被判跟风 (有前驱) 的篇
            _p50 = float(_ns.quantile(0.50))
            _p75 = float(_ns.quantile(0.75))
            _p90 = float(_ns.quantile(0.90))
            _mx = int(_ns.max())
            _flag_frac = float((_ns > 0).mean())
            _herd_mean = float(_herd_ns.mean()) if not _herd_ns.empty else float('nan')
            logger.info(
                f"    前驱计数分布 [{_tn}]: p50={sig4(_p50)} p75={sig4(_p75)} p90={sig4(_p90)} "
                f"max={_mx:,d}; 跟风篇(>0)占比={pct4(_flag_frac)}, 其前驱计数均值={sig4(_herd_mean)} "
                f"(越大=该轨转抄链越长, 头篇相对降权越重)"
            )
    except Exception as _e_dist:  # noqa: BLE001  纯日志, 绝不影响产物
        logger.warning(f"    前驱计数分布画像打印失败 (不影响产物): {_e_dist}")

    # v3.6.0 NON-BREAKING 兼容层 (F-B 修): 保留 herd_weight / n_similar_articles
    # 单列 alias = _full 路径, 让 v3.5.x 既有调用方 (paper Stata 模板 / 测试套件 /
    # legacy panel reader) 不破坏. 下游若想用 ctx 路径必须显式引用 _ctx 后缀列.
    df['herd_weight'] = df['herd_weight_full']
    df['n_similar_articles'] = df['n_similar_articles_full']

    # 三轨独立性诊断 (Plan E P1 B3 验收门 #2; v3.9.0 扩 3 路 pairwise):
    # 对 (full, ctx) / (full, ss) / (ctx, ss) 三对各算一次 Spearman ρ。
    # 若 ρ < 0.95, 视为该对"真双/三轨"; ≥ 0.95 提示两轨文本几乎相同
    # (可能对应 content_ctx / content_ss fallback 比例过高)。
    # ⚠ ss 腿门控 ss_is_fallback==False (镜像 ctx 回退公理): 回退行 content_ss≡全文
    # body → herd_weight_ss≡herd_weight_full, 若计入会人为抬高 ss 相关性、污染独立性
    # 判定; 故凡涉及 ss 的对 (full-ss / ctx-ss) 仅在 ss_is_fallback==False 的行上算
    # (缺 ss_is_fallback 列时按全部行非回退宽松处理, graceful)。
    try:
        from scipy.stats import spearmanr
        # ss 非回退掩码: 仅在 ss 真共现 (非镜像全文回退) 的行上评估 ss 相关性。
        # 缺 ss_is_fallback 列 → _ss_real 全 True (即将 ss_is_fallback 视作全 False / 全部行非回退, 宽松)。
        if 'ss_is_fallback' in df.columns:
            _ss_real = ~df['ss_is_fallback'].fillna(False).astype(bool)
        else:
            _ss_real = pd.Series(True, index=df.index)
        # ss 轨回退率画像 (deepen_runtime, round8 2026-06-29): content_ss 因"无银行∧金科
        # 同句共现"而镜像回退到全文 body 的篇占比 (= frac_ss_fallback)。CLAUDE.md 把该回退率
        # 的坍缩 (stage 13 radius / match_in_title 交互) 列为一阶可披露现象 — 它直接决定 ss 是否
        # 真第三轨: 回退率越高, content_ss≡全文 → herd_weight_ss≡herd_weight_full 的行越多,
        # 下方 full-ss/ctx-ss Spearman 的门控有效 n (= ss_real 篇数) 越小、第三轨独立性信号越弱。
        # 该列虽已在上方为 _ss_real 门控读取, 其磁盘值却从未 emit; 此处直接 emit 以量化 ss 真三轨
        # 程度。纯只读既有列, 仅喂日志、绝不回写 df/产物 (自带 try/except, golden-safe)。
        try:
            if 'ss_is_fallback' in df.columns:
                _ss_fb_rate = float(df['ss_is_fallback'].fillna(False).astype(bool).mean())
                logger.info(
                    f"    ss 轨回退率: {pct4(_ss_fb_rate)} 的篇 content_ss 回退全文 body "
                    f"(无银行∧金科同句共现); ss 真共现篇 n={int(_ss_real.sum()):,} "
                    f"(= 下方 full-ss/ctx-ss Spearman 的门控有效集; 回退率越高 → ss 越退化为 "
                    f"full 同值、第三轨独立性越弱)"
                )
            else:
                logger.info(
                    "    ss 轨回退率: (ss_is_fallback 列缺失 → 全部行按非回退宽松处理; "
                    "无法量化 content_ss 回退占比, 建议先执行 stage 14 物化 ss_is_fallback)"
                )
        except Exception as _e_ssfb:  # noqa: BLE001  纯日志, 绝不影响产物
            logger.warning(f"    ss 轨回退率画像打印失败 (不影响产物): {_e_ssfb}")
        # (轨对名, 列 a, 列 b, 该对是否门控 ss 非回退)
        _pairs = [
            ('full-ctx', 'herd_weight_full', 'herd_weight_ctx', False),
            ('full-ss', 'herd_weight_full', 'herd_weight_ss', True),
            ('ctx-ss', 'herd_weight_ctx', 'herd_weight_ss', True),
        ]
        for _pair_name, _col_a, _col_b, _gate_ss in _pairs:
            valid = df[_col_a].notna() & df[_col_b].notna()
            if _gate_ss:
                valid = valid & _ss_real
            # 需 col_a 有方差 (全等值时 ρ 无定义)
            if valid.sum() >= 50 and df.loc[valid, _col_a].nunique() > 1:
                rho, _ = spearmanr(
                    df.loc[valid, _col_a], df.loc[valid, _col_b])
                logger.info(
                    f"    三轨独立性诊断 [{_pair_name}]: Spearman ρ = {sig4(rho)} "
                    f"(n={int(valid.sum()):,}; "
                    f"{'真双/三轨' if abs(rho) < 0.95 else '⚠ 高度相关, 检查 fallback 比例'})")
    except ImportError:
        pass

    return df


# ============================================================================
# 3. 主流程
# ============================================================================

def _log_environment_and_config(input_file: str, output_file: str) -> None:
    """打印 ① 项目/环境信息 + ② 输入输出 + ③ 运行配置 + ④ 方法论依据 (日志富集, 2026-06-24)。

    目标 (用户要求"在日志文件中提供尽可能多的项目信息、运行期间信息和运行结果信息"):
    把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数、方法学出处"一次性落进
    日志, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 (golden-safe)。
    ④ 方法论引文仅 emit 经 Crossref 真值核验的条目, 含 DOI 可访问链接 (Sautner et al. 2023 JF
    https://doi.org/10.1111/jofi.13219; Tetlock 2011 RFS https://doi.org/10.1093/rfs/hhq141;
    Edwards 2001 ORM https://doi.org/10.1177/109442810142004; Fedyk & Hodson 2023 JFE
    https://doi.org/10.1016/j.jfineco.2023.04.008; Cagé et al. 2020 RES
    https://doi.org/10.1093/restud/rdz061; Glasserman et al. 2025 JFQA
    https://doi.org/10.1017/S0022109023001369; Liu et al. 2024 Econ.Lett.
    https://doi.org/10.1016/j.econlet.2024.111823; Kumar et al. 2025 WWW
    https://doi.org/10.1145/3701716.3715303; Tumre et al. 2025 NAACL
    https://doi.org/10.18653/v1/2025.naacl-industry.73), 绝不伪造 DOI (playbook §4 铁律)。
    """
    try:
        import platform

        import sklearn

        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (跟风/抄袭新闻衰减加权, STAGES_MAIN 阶段24; 三轨 full/ctx/ss)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) v3.16.0")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        logger.info(f"     · scikit-learn: {getattr(sklearn, '__version__', '?')} "
                    "(TfidfVectorizer + 余弦; 确定性来源=固定 TF-IDF 参数 + as-of vocab fit + 稳定排序)")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "本阶段纯 CPU / 无 LLM·Embedding·网络·API ($0) → 逐位可复现")

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 输入:   {input_file} (硬依赖 stage 23; 禁回退读 22/21)")
        logger.info(f"     · 输出:   {output_file}")
        logger.info(f"     · 敏感性诊断: {os.path.join(OUTPUT_DIR, 'eval_reports', '24_herd_threshold_sensitivity.csv')}")

        logger.info("  ⚙ 运行配置 (config/*.yaml::herd_detection)")
        logger.info(f"     · similarity_threshold={sig4(SIMILARITY_THRESHOLD)} (闭边界 >=) "
                    f"| time_window_days={TIME_WINDOW_DAYS:,d}天")
        logger.info(f"     · max_features={MAX_FEATURES:,d} (有效不截断: 5e6≫现实 bank-year 词表; fix omni-g-herd-02) "
                    f"| min_df(cap)={MIN_DF:,d} | max_df={sig4(MAX_DF)} | chunk_size={CHUNK_SIZE:,d}")
        logger.info(f"     · TF-IDF: analyzer=char_wb, ngram_range=(2,4); "
                    f"dense pairwise (≤2000篇/前缀) / 7天窗双指针分桶 (>2000篇, 数值逐位等价)")
        if SENS_TAGS:
            logger.info(f"     · 阈值敏感性网格 (herd_sensitivity_grid): τ∈{SENS_THRESHOLDS} → 列后缀 {SENS_TAGS} "
                        f"({len(SENS_TAGS):,d} τ × 3 轨 × 2 列; 同一 TF-IDF/余弦一遍式复算, 基线列不变)")
        else:
            logger.info("     · 阈值敏感性网格: (空) — 仅算基线阈值")

        logger.info("  📖 方法论依据 (核心方法/构念学术出处)")
        logger.info("     · 文本相似度驱动的曝光度度量: "
                    "Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R. (2023). Firm-level climate "
                    "change exposure. The Journal of Finance, 78(3), 1449–1498. https://doi.org/10.1111/jofi.13219")
        logger.info("       → 同一构念在同时段被多家媒体高相似度转抄会重复计数; 据文本相似度衰减加权可还原真实信息量")
        logger.info("     · 媒体新闻信息冗余/重复效应: Tetlock, P. C. (2011). All the news that's fit to reprint: "
                    "Do investors react to stale information? The Review of Financial Studies, 24(5), 1481-1512. "
                    "https://doi.org/10.1093/rfs/hhq141 — 连续 staleness 度量")
        logger.info("     · 双/三轨化动因 (measurement-treatment matching): Edwards, J. R. (2001). Multidimensional "
                    "constructs in organizational behavior research: An integrative analytical framework. "
                    "Organizational Research Methods, 4(2), 144-192. https://doi.org/10.1177/109442810142004 "
                    "— 全文相似度 ≠ 银行邻域/同句相似度")
        logger.info("     · 旧闻识别/转载 vs 重组 (跟风构念直接范式): Fedyk, A., & Hodson, J. (2023). When can the "
                    "market identify old news? Journal of Financial Economics, 149(1), 92-113. "
                    "https://doi.org/10.1016/j.jfineco.2023.04.008")
        logger.info("       → 1700万 Bloomberg 新闻按文本相似度区分 reprints (转载旧闻) 与 recombinations (重组旧闻); "
                    "本阶段 TF-IDF 余弦 ≥ 阈值即判前驱跟风, 与之同口径区分首发与高相似转抄")
        logger.info("     · 复制式跟风识别 (copy-paste 检测方法源): Cagé, J., Hervé, N., & Viaud, M.-L. (2020). "
                    "The production of information in an online world. Review of Economic Studies, 87(5), "
                    "2126-2164. https://doi.org/10.1093/restud/rdz061")
        logger.info("       → 全量在线新闻事件检测约 2/3 为复制粘贴; 锚定本阶段'首发-跟进链'与复制式转抄的文本相似度识别")
        logger.info("     · 滞后新闻项与时变跟进赋权: Glasserman, P., Li, F., & Mamaysky, H. (2025). Time variation "
                    "in the news-returns relationship. Journal of Financial and Quantitative Analysis, 60(1), "
                    "258-294. https://doi.org/10.1017/S0022109023001369")
        logger.info("       → 滞后新闻项刻画价格延迟反应及其时变; 锚定本阶段按 7 天窗内当期/滞后前驱计数施加衰减核赋权")
        logger.info("     · 文本相似度测度与定价 (TF-IDF/余弦操作化锚): Liu, Y., Cao, Z., & Wen, F. (2024). "
                    "Textual similarity between firm and government: Measurement and pricing. Economics Letters, "
                    "241, 111823. https://doi.org/10.1016/j.econlet.2024.111823")
        logger.info("       → 以文本相似度作可定价的计量度量; 锚定本阶段用 TF-IDF + 余弦距离判定'跟风'转抄的操作化选择")
        logger.info("     · 大规模新闻流近似重复检测 (基准): Kumar, A., Tumre, S., & Patil, S. (2025). "
                    "Benchmarking near-duplicate detection in the era of pay-walled news. In Companion "
                    "Proceedings of the ACM on Web Conference 2025 (WWW '25 Companion) (pp. 745-748). "
                    "Association for Computing Machinery. https://doi.org/10.1145/3701716.3715303")
        logger.info("     · 聚合新闻近似重复检测改进: Tumre, S., Patil, S., & Kumar, A. (2025). Improved "
                    "near-duplicate detection for aggregated and paywalled news-feeds. In Proceedings of the "
                    "2025 Conference of the Nations of the Americas Chapter of the ACL: Human Language "
                    "Technologies (Vol. 3: Industry Track) (pp. 979-987). Association for Computational "
                    "Linguistics. https://doi.org/10.18653/v1/2025.naacl-industry.73")
        logger.info("       → 大规模新闻聚合流的近似重复检测算法; 锚定本阶段 7 天窗双指针分桶 O(N·window) "
                    "的工程学/计算复杂度依据 (>2000 篇/前缀的可扩展去重)")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法信息打印失败 (不影响处理): {e}")


def main():
    """主入口: 加载数据 → 跟风检测 → 保存。"""
    import time
    start_time = time.time()
    # 运行期阶段计时累计 (各主要子阶段墙钟耗时, 末尾汇总打印; 纯日志, golden-safe)
    phase_durations: dict[str, float] = {}

    # ── 【功能】banner (黄金范式, 摘自 PIPELINE_NUMBERED_PY_REFERENCE 白话/详细说明;
    #     替换而非叠加旧的 "="*60 短启动头, 对齐 39c construct_orthogonality 单 banner 范式) ──
    logger.info("=" * 72)
    logger.info("阶段 24: 跟风/抄袭新闻衰减加权 (三轨 v3.9.0; Tetlock 2011 RFS / Edwards 2001 ORM)")
    logger.info("=" * 72)
    logger.info(
        "【功能】解决'同一条新闻被各家媒体抄来抄去导致情绪被重复计算'。给每篇新闻数"
    )
    logger.info(
        "        '它发布前 7 天内有几篇内容长得很像的旧文', 据此打折后输出逐篇降权乘子,"
    )
    logger.info(
        "        供下游 stage 45 面板聚合情感时乘上去 (硬依赖, 缺/错则整张面板回归受影响)。"
    )
    logger.info(
        f"【方法】按 target_bank 分组 → 三轨 (full/ctx/ss) 各做 char_wb (2,4) TF-IDF + 余弦; "
        f"as-of 年度前缀拟合 (历史不变);"
    )
    logger.info(
        f"        7 天窗 (TIME_WINDOW_DAYS={TIME_WINDOW_DAYS}) 内相似度 >= "
        f"SIMILARITY_THRESHOLD={SIMILARITY_THRESHOLD} (闭边界) 记为跟风前驱;"
    )
    logger.info(
        "        衰减公式 weight_j = 1/(1+n_similar_predecessors) — 原创首篇=1, 第 10 篇抄稿≈1/10;"
    )
    logger.info(
        f"        ≤2000 篇/前缀走 dense pairwise, >2000 篇走 7 天窗双指针分桶 (数值逐位等价); "
        f"max_features={MAX_FEATURES:,d} (有效不截断, 恢复跨行可比性; fix omni-g-herd-02)。"
    )
    logger.info(
        "【判读】跟风占比/均值: herd_weight mean 越接近 1 = 转抄越少(信息越独立); 越低 = 转抄"
    )
    logger.info(
        "        越密集(降权越重)。三轨独立性 Spearman ρ<0.95 = 真三轨(各轨各自打分); ρ≥0.95"
    )
    logger.info(
        "        = 两轨文本几近相同(多因 ctx/ss fallback 占比过高)。阈值敏感性 ρ_vs_baseline 越高(≥0.9)"
    )
    logger.info(f"        = 权重排序对 {SIMILARITY_THRESHOLD} 这个具体门槛越不敏感(结论稳健)。")
    logger.info(
        "【确定性】纯 CPU, $0, 无 LLM/Embedding/网络; 固定 TF-IDF 参数 + as-of vocab fit + "
        "稳定排序 → 逐位可复现。"
    )

    # 加载篇章级数据: 固定读取阶段 23 (BERT情感分析) 的输出
    # 严禁回退读取 22/21 的输出，避免磁盘残留旧文件导致静默数据污染
    filenames = CONFIG.get('filenames', {})
    input_filename = filenames.get('output_23_bert_tone', '23_bert_tone.parquet')
    output_filename = filenames.get('output_24_herd_decay', '24_herd_decay.parquet')
    input_file = os.path.join(OUTPUT_DIR, input_filename)
    output_file = os.path.join(OUTPUT_DIR, output_filename)

    if not os.path.exists(input_file):
        logger.error(
            f"输入文件未找到: {input_file}。"
            f"stage 23 (tone_berts) 自 2026-06-12 起为无条件 always-on, 正常应已产出"
            f"该文件; 若缺失, 说明 stage 23 本次执行失败或被显式跳过, 请检查其日志。"
        )
        # 显式以非零返回码退出, 让上游编排器能感知"DAG 24 依赖 23"契约违规,
        # 避免父进程把 'silent return' 误判为 stage 24 成功 (详见 plan c2)。
        raise SystemExit(1)

    # 项目/环境信息 + 输入输出 + 运行配置 + 方法论依据 (日志富集 2026-06-24, 路径确定后打印)
    _log_environment_and_config(input_file, output_file)

    # 记录输入文件修改时间，便于数据溯源审计
    import datetime as _dt
    _mtime = os.path.getmtime(input_file)
    logger.info(
        f"  📁 输入文件: {input_filename} "
        f"(修改时间: {_dt.datetime.fromtimestamp(_mtime).strftime('%Y-%m-%d %H:%M:%S')})"
    )

    _t = time.time()
    df = pd.read_parquet(input_file)
    phase_durations['①加载parquet'] = time.time() - _t
    logger.info(f"  加载 {len(df):,} 条新闻 (来源: {input_filename})")

    # 执行跟风检测
    _t = time.time()
    df = compute_herd_weights(df)
    phase_durations['②三轨跟风检测+衰减加权'] = time.time() - _t

    # ── 阈值敏感性诊断摘要 (2026-06-13): 逐 τ flag 率 / 权重分布 / 对基线相关 ──
    # 生产路径专属 (单测直调 compute_herd_weights 不落盘); 供论文 Appendix
    # 阈值敏感性表引用。Spearman ρ 高 (≥0.9) ⇒ 文章级权重排序对 τ 不敏感。
    _t = time.time()
    if SENS_TAGS:
        try:
            from scipy.stats import spearmanr
        except ImportError:
            spearmanr = None
        diag_rows = []
        for _tn in ('full', 'ctx', 'ss'):  # v3.9.0: ss 第三轨 (银行+金科同句) 同出诊断行
            base_w = df[f'herd_weight_{_tn}']
            for _thr, _tag in zip(SENS_THRESHOLDS, SENS_TAGS):
                w = df[f'herd_weight_{_tn}_{_tag}']
                rho = np.nan
                if (spearmanr is not None and base_w.nunique() > 1
                        and w.nunique() > 1):
                    rho = float(spearmanr(base_w, w)[0])
                diag_rows.append({
                    'track': _tn,
                    'threshold': _thr,
                    'baseline_threshold': SIMILARITY_THRESHOLD,
                    'flag_rate': float(
                        (df[f'n_similar_articles_{_tn}_{_tag}'] > 0).mean()),
                    'mean_weight': float(w.mean()),
                    'min_weight': float(w.min()),
                    'spearman_vs_baseline': rho,
                })
                logger.info(
                    f"  [阈值敏感性] track={_tn} τ={sig4(_thr)}: "
                    f"flag={pct4(diag_rows[-1]['flag_rate'])}, "
                    f"mean_w={sig4(diag_rows[-1]['mean_weight'])}, "
                    f"ρ_vs_baseline={sig4(rho)}")
        eval_dir = os.path.join(OUTPUT_DIR, 'eval_reports')
        os.makedirs(eval_dir, exist_ok=True)
        diag_path = os.path.join(eval_dir, '24_herd_threshold_sensitivity.csv')
        pd.DataFrame(diag_rows).to_csv(diag_path, index=False,
                                       encoding='utf-8-sig')
        logger.info(f"  阈值敏感性诊断已写出: {diag_path}")
    phase_durations['③阈值敏感性诊断'] = time.time() - _t

    # ── 【结果分析】(黄金范式, 紧随写盘前; 仅读 df 既有列, 不回写任何产物) ──
    # crash-guard: 整块包 try/except — 该块在最终 to_parquet 之前执行, 若因边缘
    # 数据 (空 Series.min() / 全 NaN / 缺列) 抛异常会丢失产物 → 直接证伪 golden-safe;
    # 任何异常仅记 warning 后跳过, 绝不阻断写盘 (本块为纯日志, 不回写 df)。
    try:
        logger.info("-" * 72)
        logger.info("【结果分析】跟风衰减权重产出体检 (篇数/占比/降权强度/三轨独立性):")
        _n_total = len(df)
        # column-guard: 6 列由 compute_herd_weights 必产 (见其初始化块), 但仍逐轨检测
        # 以防上游契约变更; 缺列轨记 info 跳过, 不落进数值判读。
        _have = {_tn: (f'n_similar_articles_{_tn}' in df.columns
                       and f'herd_weight_{_tn}' in df.columns)
                 for _tn in ('full', 'ctx', 'ss')}
        for _tn in ('full', 'ctx', 'ss'):
            if not _have[_tn]:
                logger.info(
                    f"  [跳过 {_tn} 轨] herd_weight_{_tn}/n_similar_articles_{_tn} 列缺失 "
                    f"(上游 compute_herd_weights 未产出该轨?), 不纳入体检。"
                )

        def _flag_rate(_tn):
            # 跟风占比 = n_similar_articles_{track} > 0 的篇数 / 总篇数 (转抄越多占比越高)
            return float((df[f'n_similar_articles_{_tn}'] > 0).mean()) if _have[_tn] else float('nan')

        def _mean_w(_tn):
            # 平均降权乘子 = herd_weight_{track}.mean(); NaN-guard: 全 NaN 轨返回 nan
            if not _have[_tn]:
                return float('nan')
            _s = df[f'herd_weight_{_tn}']
            return float(_s.mean()) if _s.notna().sum() > 0 else float('nan')

        _flag_full, _flag_ctx, _flag_ss = (_flag_rate('full'), _flag_rate('ctx'), _flag_rate('ss'))
        _mw_full, _mw_ctx, _mw_ss = (_mean_w('full'), _mean_w('ctx'), _mean_w('ss'))
        # min 仅在 full 轨有有效数据时计算 (空/全 NaN Series.min() 会抛/返 nan)
        _mn_full = (float(df['herd_weight_full'].min())
                    if _have['full'] and df['herd_weight_full'].notna().sum() > 0
                    else float('nan'))

        logger.info(f"  样本: 总新闻 {_n_total:,} 篇 (banks × T)")
        logger.info(
            f"  跟风占比: full={pct4(_flag_full)}  ctx={pct4(_flag_ctx)}  ss={pct4(_flag_ss)} "
            f"— 占比越高=该范围内转抄越普遍; 三轨候选前驱集合相同 (同银行 7 天窗内更早文章), "
            f"占比差异仅反映各轨文本 (全文/实体窗/同句窗) 的余弦重叠差异, 不预设 full/ctx/ss 间"
            f"单调方向 (窄文本既可因内容重叠减少而降 flag, 也可因样板句跨媒体高度相似而升 flag)"
        )
        logger.info(
            f"  平均降权乘子 herd_weight.mean: full={sig4(_mw_full)}  ctx={sig4(_mw_ctx)}  ss={sig4(_mw_ss)} "
            f"(min_full={sig4(_mn_full)}) — 接近 1.0=信息独立基本不降权; 显著<1=存在密集转抄被打折"
        )
        # 判读 (NaN-guard 优先): full 轨全 NaN/缺列 → 不落进数值方向判断
        if _mw_full != _mw_full:  # NaN
            logger.info(
                "  判读: full 轨无有效 herd_weight 数据 (全 NaN 或缺列), 跳过降权方向判读。"
            )
        elif _mw_full >= 0.9995 and _flag_full == _flag_full and _flag_full < 0.001:
            # 退化为全 1.0 (无任何降权) 往往意味着上游文本列缺失或样本过稀, 需告警
            logger.warning(
                "  ⚠ full 轨 herd_weight≈1.0 且跟风占比≈0 — 几乎未检出任何转抄。盘面 T=2 小样本"
                "下属预期(每银行每年文章稀疏, 7 天窗内难凑相似前驱); 但若全量 run 出现, 须排查"
                "文本列是否缺失/向量化是否大面积降级。"
            )
        elif _mw_full < 1.0:
            logger.info(
                "  判读: full 轨已检出转抄并施加降权 (mean<1) — 符合预期方向, 转载量被压缩为真实信息量。"
            )
        # ctx/ss 是否退化为 full 同值 (fallback 比例过高时两轨与 full 逐位相同);
        # 仅在两轨列均存在时比较, 否则记 info 跳过 (column-guard)。
        _ctx_eq_full = (_have['full'] and _have['ctx'] and bool(np.allclose(
            df['herd_weight_ctx'].to_numpy(dtype=float),
            df['herd_weight_full'].to_numpy(dtype=float), equal_nan=True)))
        _ss_eq_full = (_have['full'] and _have['ss'] and bool(np.allclose(
            df['herd_weight_ss'].to_numpy(dtype=float),
            df['herd_weight_full'].to_numpy(dtype=float), equal_nan=True)))
        if _ctx_eq_full:
            logger.warning(
                "  ⚠ ctx 轨 herd_weight 与 full 轨逐位相同 — content_ctx 缺列或全 fallback, "
                "ctx 退化为非独立轨 (盘面 T=2 全无跟风时三轨权重同为 1.0 亦会逐位相同, 非必然 "
                "content_ctx 缺列/fallback; 若全量 run 出现再查 stage 14 ctx_materializer 是否物化 content_ctx)。"
            )
        if _ss_eq_full:
            logger.warning(
                "  ⚠ ss 轨 herd_weight 与 full 轨逐位相同 — content_ss 缺列或全 fallback (无银行∧"
                "金科同句共现), ss 退化为非独立轨 (盘面 T=2 / 同句共现稀疏时可能发生)。"
            )
        if _have['full'] and _have['ctx'] and _have['ss'] and not _ctx_eq_full and not _ss_eq_full:
            logger.info(
                "  三轨各自独立打分 (ctx/ss 均不与 full 逐位相同) — measurement-treatment matching 成立。"
            )
        # 阈值敏感性: ρ_vs_baseline 越高 = 权重排序对 SIMILARITY_THRESHOLD 越不敏感 (取 full 轨各 τ 的 ρ 概览)
        if SENS_TAGS:
            _rhos = [r['spearman_vs_baseline'] for r in diag_rows
                     if r['track'] == 'full' and r['spearman_vs_baseline'] == r['spearman_vs_baseline']]
            if _rhos:
                _rho_min = min(_rhos)
                logger.info(
                    f"  阈值敏感性 (full 轨, τ∈{SENS_THRESHOLDS}): ρ_vs_baseline 最低={sig4(_rho_min)} "
                    f"— {f'≥0.9 权重排序对阈值稳健, 结论不靠 {SIMILARITY_THRESHOLD} 这个具体数' if _rho_min >= 0.9 else '<0.9 权重排序随 τ 漂移, 须在论文披露阈值敏感性'}"
                )
            else:
                logger.info(
                    "  阈值敏感性: 各 τ 权重无方差或 spearman 不可用 (盘面 T=2 小样本下常见, ρ 无定义)。"
                )
        # 小样本 / 全量提醒
        if _n_total < 5000:
            logger.info(
                f"  ⚠ 小样本提醒: 当前 {_n_total:,} 篇属盘面 T=2 规模, 上述跟风占比/降权强度仅验证"
                "管道正确性; 全量结论 (转抄密集度/三轨分化) 以 约1,819万/T=19 实测为准 (max_features "
                "已上调至 5e6 不再截断咬合, fix omni-g-herd-02; 词表撞 5e6 才记 warning)。"
            )
        logger.info("-" * 72)
    except Exception as _e:
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")

    # 保存 (追加 herd_weight 列后写入独立输出文件)
    # 使用数据版本控制保存
    _t = time.time()
    from news_process.core.data_versioning import save_parquet_with_metadata
    save_parquet_with_metadata(
        df=df,
        output_path=output_file,
        stage_name="24_herd_decay",
        config=CONFIG,
        input_files=[input_file],
    )
    phase_durations['④写盘parquet'] = time.time() - _t
    logger.info(f"  已保存至 {output_file}")

    # ── ⏱ 阶段计时汇总 (各主要子阶段墙钟耗时; 纯日志, golden-safe) ──
    try:
        elapsed = time.time() - start_time
        logger.info("  ⏱ 阶段计时 (墙钟秒, 4 位有效数字):")
        for _pname, _pdur in phase_durations.items():
            _frac = _pdur / elapsed if elapsed > 0 else 0.0
            logger.info(f"     · {_pname}: {sig4(_pdur)}s ({pct4(_frac)})")
        logger.info(f"     · 合计: {sig4(elapsed)}s")
    except Exception as _te:  # noqa: BLE001
        logger.warning(f"  阶段计时汇总打印失败 (不影响产物): {_te}")
        elapsed = time.time() - start_time

    logger.info(f"  耗时: {sig4(elapsed)}秒")
    logger.info(f"阶段 {STAGE_NAME} 完成 ✓")


if __name__ == '__main__':
    main()
