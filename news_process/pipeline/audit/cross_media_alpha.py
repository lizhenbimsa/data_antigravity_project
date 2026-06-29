"""news_process.pipeline.audit.cross_media_alpha — stage 39f Krippendorff α.

v3.7.0 PR #12 (D3) — 跨媒体源 tone 一致性 Krippendorff α + tone variance.

⚠️  IMPORTANT — 同名异构披露 (fix(omni-g-audit-family-08, 2026-06-11)):
    本模块输出列 ``cross_outlet_tone_variance_{full,ctx,ss}`` 与第 10 篇
    ``bank_media_disagreement`` paper_spec.yaml 冻结的 main treatment **同名但
    不同构** — spec 冻结构造 = bank-year **无条件全年截面** outlet 级均值的
    跨 outlet var (待新建, M2-M3; 矩已于 2026-06-11 统一为 var); 本模块实现 =
    **事件窗条件**子样本逐 episode 跨 outlet 方差 (np.var ddof=1) 再按 episode
    内文章数加权到 bank-year。差异两处: (a) 估计域: 事件窗条件 vs 全年无条件;
    (b) 聚合: episode 文章数加权均值 vs 单一截面计算。
    本列**不是**第 10 篇 spec 承诺的 main treatment; 第 10 篇采用前必须二选一:
    对齐 spec 冻结构造 (新列名), 或重命名本模块产物释放保留名 —
    详见 paper_spec.yaml treatment 块披露注释。

学术依据
--------
Krippendorff, K. (2004). Content analysis: An introduction to its
methodology. SAGE Publications. → α 跨标注者一致性, 比 Cohen κ 更稳健
(多标注者 + 任意测量尺度).

Tetlock, P. C. (2007). Giving content to investor sentiment: The role of
media in the stock market. Journal of Finance, 62(3), 1139-1168.
→ 跨多源 tone 一致性作信号质量代理.

设计
----
对每个 (bank b, event episode) 三元组:
    1. 收集报道该 bank 的媒体集 M (要求 |M| ≥ 2, 否则 NaN)
    2. 每家媒体 m: 算窗口内 tone 均值 T_m,b
    3. 计算 (a) variance(T_m,b across m) — 事件窗条件方差 (见顶部同名异构披露)
            (b) Krippendorff α (interval scale) — α robustness
    4. bank-year 加权均值 (按 episode 内文章数加权)

事件窗口定义
-----------
- bank-level shock 自动检测: bank-day 内 ``n_per_day`` >= 该 bank 日计数 p90
  (注: 当前实现仅按日计数 p90; 设计中的 ``tone_volatility_within_day`` p90 OR 分支尚未实现)
- 窗口 ±3d (与 v2.3 G-D3.1 一致)
- episode 合并 (fix(omni-g-audit-family-01, 2026-06-11)): 同 bank 相邻 peak 日
  gap ≤ 2×window 时 ±window 窗口重叠 → 传递合并为单一 episode (窗口取并集),
  防同一文章跨事件重复计入加权 (持续性 spike 超权) 与 n_events 高估独立事件数。

panel 新增 9 列 (三轨 full/ctx/ss; ss = 银行+金科同句共现轨, 列缺失时该轨优雅跳过)
---------------
``cross_outlet_tone_variance_{full,ctx,ss}``  事件窗条件 tone 方差 (⚠ 与第 10 篇 spec
                                            冻结构造同名异构, 见顶部披露)
``cross_media_alpha_{full,ctx,ss}``           α 度量, robustness
``n_events_{full,ctx,ss}``                     episode 计数 (重叠窗合并后的独立事件数)

依赖
----
krippendorff>=0.5.0 已在 requirements.txt:112 启用 (硬运行依赖, stage 18/39f always-on 后).

D-0 实测项 (v2.3 G-D3.1)
------------------------
valid (bank, event) 三元组覆盖 ≥ 60% bank-year.

白话: 同一家银行出大新闻的那几天, 不同媒体打出来的语调一致吗?
方差衡量"各家媒体说法差多远", Krippendorff α 衡量"把媒体当评分员,
它们打分有多一致"。一致说明信号可靠; 分歧本身也是信息 (媒体分歧度)。
注意: 这里算的是"事件窗口内"的口径, 和第 10 篇论文承诺的"全年口径"
同名不同义, 用之前必须先对齐, 详见顶部披露。

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 75_cross_media_alpha.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**输入**: 优先读 `21_tone_llms_full.parquet`, 回退 `21_tone_llms.parquet`(文章级); 两者均缺 → sys.exit(1)。用列: target_bank、日期、媒体(中文)、llm_vote_tone_{full,ctx,ss}(若该列无但 llm_sentiment_{trk} 存在, 则按 `_SENT_TO_TONE`={'正面':1.0,'中性':0.0,'负面':-1.0}(与 encode.py SENTIMENT_MAP 一致)派生数值 tone, 这是 panel 聚合才有的列在 article 级的补派生; 其它标签 → NaN)。

**处理步骤**(`main`):
- `detect_bank_events`: 按 bank-day 计文章数, 取该 bank 的 p90(N_ARTICLE_PERCENTILE=0.90)峰值日(n_per_day≥p90 且 p90>pmin 排除常量分布), 经 `_merge_overlapping_events` 把相邻 gap≤2×window 的传递重叠 ±3d 窗合并为单一 episode(防同文章跨事件重复计入、防 n_events 高估; 修 omni-g-audit-family-01)。
- 三轨循环: `compute_outlet_tone_aggregates` 对每个 (bank,event_date) 在 episode 并集窗内收集 outlet×day 结构(outlet_tones 1D 供方差、daily_matrix 2D 供 α、n_articles 供加权; 要求 outlet 数≥2)。
- `compute_variance_and_alpha`: variance=np.var(outlet_tones, ddof=1)(事件窗条件 outlet 间方差); Krippendorff α(interval scale, reliability_data=outlet×day matrix, NaN 作 missing, 需至少 1 个 item 有≥2 outlets)。
- `aggregate_to_bank_year`: 按 episode 内 n_articles 加权均值聚到 bank-year(修: 旧版误按 n_outlets, 缺 n_articles 列回退 n_outlets+warning), 三轨 panel outer-merge。
- G-D3.1 诊断: valid bank 覆盖 ≥60% → PASS 否则 WARN(仅日志)。

**关键算法/公式**: Krippendorff(2004) α(多评分员、任意尺度, 比 Cohen κ 稳健); Tetlock(2007) 跨源 tone 一致性作信号质量代理; 事件窗 ±3d、min 2 outlets、p90 峰值。

**输出**: 9 列(见三轨段)。⚠ 同名异构披露: cross_outlet_tone_variance_{full,ctx,ss}(注: 三轨同名异构; ss 轨 v3.9.0 2026-06-14 加入)与第 10 篇 bank_media_disagreement paper_spec 冻结的 main treatment **同名但不同构**(本模块=事件窗条件子样本逐 episode 方差再加权; spec=全年无条件截面 outlet 均值的跨 outlet var)——第 10 篇采用前必须对齐 spec 或重命名释放保留名。

**外部依赖/超时**: 依赖 `krippendorff>=0.5.0`(已在 requirements.txt 启用; 若未装则 α 输出 NaN、仅 variance 可用); 无 LLM/Embedding/_llm_cache.db(只读已落盘 stage 21 + 确定性 _SENT_TO_TONE 派生); DAG timeout=3600(60 分钟, 含事件检测+媒体源聚合)。

**DAG 位置**: 验证阶段 39f(STAGES_VALIDATION), 上游=stage 21 tone_llms, 下游与第 10 篇 bank_media_disagreement 论文重叠(启用前须对齐 spec, 当前仅 validation)。

■ 白话说明

**这一步在做什么**: 同一家银行出大新闻的那几天, 不同媒体打出来的语调一致吗? 这一步先找出每家银行"上头条"的高峰日(某天报道数特别多), 把相邻的高峰并成一个"事件", 然后看这个事件窗口里各家媒体的语调差多远。它算两个东西: 方差(各家媒体说法分歧有多大)和 Krippendorff α(把媒体当评分员、看它们打分有多吻合的一个一致性分数)。

**为什么需要它**: 媒体说法越一致, 说明这条情感信号越可靠(不是某一家媒体的偏见); 反过来, 媒体之间的分歧本身也是有价值的信息("媒体分歧度"恰好是第 10 篇论文的核心变量)。这一步既给主线情感测度提供"信号质量"的稳健性证据, 又为媒体分歧那篇论文铺路。

**对最终面板/论文的影响**: 它给银行-年度面板加了 9 列(语调方差、媒体一致性 α、事件数, 三种文本口径各一份)。一个重要警示: 它产的"跨媒体语调方差"列和第 10 篇论文承诺的主变量"名字一样但算法不一样"(这里是"事件窗口内"算的, 论文要的是"全年"算的)——所以第 10 篇真正动用前, 必须先把口径对齐或改名, 否则会张冠李戴、影响那篇论文的核心识别。
========================================================================
"""

from __future__ import annotations

import os
import platform
import sys
import time
from datetime import timedelta

import numpy as np
import pandas as pd

# sys.path 注入 (保证从任意 cwd 直跑本文件时可 import news_process 包)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config  # noqa: E402
from news_process.core.logging import pct4, setup_logging, sig4  # noqa: E402

CONFIG = load_config()
STAGE_NAME = "75_cross_media_alpha"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

EVENT_WINDOW_DAYS = 3
MIN_OUTLETS_PER_EVENT = 2
N_ARTICLE_PERCENTILE = 0.90


def _merge_overlapping_events(
    events: pd.DataFrame,
    window_days: int = EVENT_WINDOW_DAYS,
) -> pd.DataFrame:
    """合并同 bank 重叠 ±window 事件窗为单一 episode (event-clustering).

    fix(omni-g-audit-family-01, 2026-06-11): 每个 ≥p90 peak 日各带 ±window_days
    窗口; 相邻 peak 日 gap ≤ 2×window_days 时窗口重叠 → 同一批文章被重复纳入多个
    事件的 variance/α 计算, 再按事件加权 → 持续性 spike 系统性超权 + n_events
    高估独立事件数. 此处把传递重叠 (transitively overlapping) 的 peak 日合并为
    单一 episode, 窗口取并集 [first_peak − window, last_peak + window];
    ``event_date`` 取 episode 首个 peak 日 (确定性锚点).

    Returns:
        DataFrame [target_bank, event_date, window_start, window_end].
    """
    if events.empty:
        out = events.copy()
        out['window_start'] = pd.Series(dtype='datetime64[ns]')
        out['window_end'] = pd.Series(dtype='datetime64[ns]')
        return out
    ev = events.copy()
    ev['_d'] = pd.to_datetime(ev['event_date'])
    ev = ev.sort_values(['target_bank', '_d'])
    gap = pd.Timedelta(days=2 * window_days)
    win = pd.Timedelta(days=window_days)
    rows = []
    for bank, g in ev.groupby('target_bank', sort=False):
        dates = list(g['_d'])
        first = last = dates[0]
        for d in dates[1:]:
            if d - last <= gap:
                last = d  # 窗口重叠 → 并入当前 episode
            else:
                rows.append({'target_bank': bank, 'event_date': first,
                             'window_start': first - win, 'window_end': last + win})
                first = last = d
        rows.append({'target_bank': bank, 'event_date': first,
                     'window_start': first - win, 'window_end': last + win})
    return pd.DataFrame(rows)


def detect_bank_events(
    article_df: pd.DataFrame,
    date_col: str = '日期',
) -> pd.DataFrame:
    """检测 bank-level events: bank-day 内文章数高于该 bank p90.

    fix(omni-g-audit-family-01, 2026-06-11): peak 日检出后经
    ``_merge_overlapping_events`` 合并重叠 ±3d 窗口为 episode (语义变更:
    返回值从逐 peak 日事件改为去重叠 episode, 含窗口并集列).

    Returns:
        events DataFrame [target_bank, event_date, window_start, window_end].
    """
    df = article_df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    # 按 bank-day 计文章数
    by_day = (
        df.groupby(['target_bank', df[date_col].dt.date])
        .size()
        .reset_index(name='n_per_day')
    )
    by_day.columns = ['target_bank', 'event_date', 'n_per_day']
    # 每 bank p90 + 每 bank min (方差守卫用)
    _agg = (by_day.groupby('target_bank')['n_per_day']
            .agg(p90=lambda s: s.quantile(N_ARTICLE_PERCENTILE), pmin='min')
            .reset_index())
    by_day = by_day.merge(_agg, on='target_bank')
    # fix(cmalpha-p90, review-closure 2026-06-10 F2): 用 '>=' p90 保真顶分位 spike(含落在 max
    # 的合法峰值, 整数小样本日计数下 p90 常 == max), 但仅对**有方差**的 bank (p90 > pmin) 判
    # 事件 —— 退化源是常量/近常量分布 (p90==pmin, 如每日恒 1 篇), 该守卫使其 0 事件; 真分布
    # 仍取 >= 高分位的全部峰值。修正前版严格 '>' 会漏掉 p90==max 的真峰值 (over-correction)。
    events = by_day[(by_day['n_per_day'] >= by_day['p90'])
                    & (by_day['p90'] > by_day['pmin'])][['target_bank', 'event_date']]
    events = events.reset_index(drop=True)
    # fix(omni-g-audit-family-01, 2026-06-11): 重叠窗口合并为 episode (见 helper docstring)
    return _merge_overlapping_events(events)


def compute_outlet_tone_aggregates(
    article_df: pd.DataFrame,
    events: pd.DataFrame,
    tone_col: str,
    media_col: str = '媒体(中文)',
    date_col: str = '日期',
) -> dict[tuple, dict]:
    """对每个 (bank, event_date) 收集 outlet × day 的 tone 二维结构.

    修 S2.3: 原版返回 ``np.ndarray`` (1 item × N raters, Krippendorff α 未定义),
    现版返回 ``{outlet_tones, daily_matrix}`` 两份数据:

    - ``outlet_tones``: outlet-level tone 均值 1D 数组 → 用于 variance 计算
      (事件窗条件方差; 与第 10 篇 spec 冻结构造同名异构, 见模块顶部披露).
    - ``daily_matrix``: outlet × day matrix (raters × items), NaN 填充无报道.
      → Krippendorff α 真正可用的 reliability_data 输入.
    - ``n_articles``: 窗口内非缺 tone 文章数 → bank-year 加权用
      (fix(omni-g-audit-family-01, 2026-06-11), 对齐模块 docstring 加权契约).

    事件窗: ``events`` 含 ``window_start``/``window_end`` 列 (episode 并集窗口,
    来自 ``detect_bank_events``) 时优先使用; 缺列时回退 ``event_date`` ±3d
    (向后兼容旧调用方).

    Returns:
        ``{(bank, event_date): {'outlet_tones': ndarray, 'daily_matrix': ndarray,
        'n_articles': int}}``
    """
    df = article_df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df['_day'] = df[date_col].dt.normalize()

    has_window = {'window_start', 'window_end'}.issubset(events.columns)
    out = {}
    for _, ev in events.iterrows():
        bank = ev['target_bank']
        ed = pd.Timestamp(ev['event_date'])
        # fix(omni-g-audit-family-01, 2026-06-11): episode 并集窗口优先 (防重叠重复计入)
        if has_window and pd.notna(ev['window_start']) and pd.notna(ev['window_end']):
            w_start = pd.Timestamp(ev['window_start'])
            w_end = pd.Timestamp(ev['window_end'])
        else:
            w_start = ed - timedelta(days=EVENT_WINDOW_DAYS)
            w_end = ed + timedelta(days=EVENT_WINDOW_DAYS)
        mask = (
            (df['target_bank'] == bank)
            & (df['_day'] >= w_start)
            & (df['_day'] <= w_end)
        )
        sub = df.loc[mask, [media_col, '_day', tone_col]].dropna(subset=[tone_col])
        if sub[media_col].nunique() < MIN_OUTLETS_PER_EVENT:
            continue
        # outlet-level mean (供 variance 用)
        outlet_tones = sub.groupby(media_col)[tone_col].mean().values
        # outlet × day matrix (raters × items, 供 Krippendorff α 用)
        # missing cell = NaN, 表示该 outlet 在该 day 无报道
        daily_matrix = sub.pivot_table(
            index=media_col, columns='_day', values=tone_col, aggfunc='mean',
        ).values  # shape (n_outlets, n_days), 含 NaN
        out[(bank, ev['event_date'])] = {
            'outlet_tones': outlet_tones,
            'daily_matrix': daily_matrix,
            'n_articles': int(len(sub)),
        }
    return out


def compute_variance_and_alpha(
    event_data: dict[tuple, dict],
) -> pd.DataFrame:
    """对每个三元组算 variance (outlet 间) 与 Krippendorff α (outlet × day).

    修 S2.3: variance 走 outlet-level 1D (事件窗条件方差, 见模块顶部同名异构披露),
    α 走 outlet × day 二维 matrix (raters × items, NaN 填充无报道).

    Returns:
        DataFrame [target_bank, event_date, n_outlets, n_days, n_articles,
        variance, alpha].
    """
    try:
        import krippendorff
        has_krip = True
    except ImportError:
        logger.warning(
            "krippendorff 未装 (已在 requirements.txt 启用); "
            "pip install krippendorff 后可用. α 输出 NaN, 仅 variance 可用"
        )
        has_krip = False

    rows = []
    for (bank, ed), data in event_data.items():
        tones = data['outlet_tones']
        matrix = data['daily_matrix']  # shape (n_outlets, n_days)
        if len(tones) < MIN_OUTLETS_PER_EVENT:
            continue
        var = float(np.var(tones, ddof=1)) if len(tones) > 1 else 0.0
        alpha = float('nan')
        if has_krip and matrix.shape[0] >= 2 and matrix.shape[1] >= 1:
            try:
                # krippendorff α: reliability_data shape (raters, items) = (outlets, days)
                # NaN 自动作 missing data (α 算法原生支持).
                # 仅当至少 1 个 item 有 ≥ 2 outlets 报道时 α 才有信号.
                n_valid_items = int(np.sum(np.sum(~np.isnan(matrix), axis=0) >= 2))
                if n_valid_items >= 1:
                    # fix(2026-06-19 run-check F8): T=2 退化数据 (方差为零/评分不足) 喂给
                    # krippendorff 会在库内触发 numpy "invalid value encountered in scalar
                    # divide" RuntimeWarning; 结果本就是 NaN (已被 try/except 与下游消费正确处理),
                    # 故仅在 FP 错误态层面消噪, 不改任何 alpha 取值 → golden 安全。
                    with np.errstate(invalid='ignore', divide='ignore'):
                        alpha = float(krippendorff.alpha(
                            reliability_data=matrix,
                            level_of_measurement='interval',
                        ))
            except Exception as e:
                logger.debug(f"  α fail for ({bank}, {ed}): {type(e).__name__}: {e}")
        rows.append({
            'target_bank': bank,
            'event_date': ed,
            'n_outlets': int(matrix.shape[0]),
            'n_days': int(matrix.shape[1]),
            # fix(omni-g-audit-family-01, 2026-06-11): episode 内文章数 → bank-year 加权用
            'n_articles': int(data.get('n_articles', 0)),
            'variance': var,
            'alpha': alpha,
        })
    return pd.DataFrame(rows)


def aggregate_to_bank_year(
    events_metrics: pd.DataFrame,
    suffix: str,
) -> pd.DataFrame:
    """bank-year 加权均值 (按 episode 内文章数 ``n_articles`` 加权).

    fix(omni-g-audit-family-01, 2026-06-11): 语义变更 — 旧实现按 ``n_outlets``
    加权, 与模块 docstring 设计契约 ("按 event 内文章数加权") 不符; 现对齐契约
    用 ``n_articles``. 旧格式 events_metrics 缺 ``n_articles`` 列时回退
    ``n_outlets`` 并 warning (向后兼容).
    """
    df = events_metrics.copy()
    df['year'] = pd.to_datetime(df['event_date']).dt.year
    if 'n_articles' in df.columns:
        df['_w'] = df['n_articles'].astype(float)
    else:
        logger.warning(
            "  aggregate_to_bank_year: events_metrics 缺 n_articles 列, "
            "回退 n_outlets 加权 (旧格式兼容; 设计契约为文章数加权)")
        df['_w'] = df['n_outlets'].astype(float)

    def _wmean(g, col):
        w = g['_w'].values
        v = g[col].values
        mask = ~np.isnan(v)
        if mask.sum() == 0 or w[mask].sum() == 0:
            return np.nan
        return float(np.average(v[mask], weights=w[mask]))

    panel = (
        df.groupby(['target_bank', 'year'])
        # fix(2026-06-19 run-check F4): include_groups=False 消除 pandas 2.2 弃用警告
        # "DataFrameGroupBy.apply operated on the grouping columns"。lambda 不引用分组列
        # (target_bank/year 经 reset_index 从组索引恢复) → 输出值/dtype/列序逐位不变 (已验
        # old.equals(new)==True on pandas 2.2.3)。⚠ pandas 3.0 该参数将默认行为并移除。
        .apply(lambda g: pd.Series({
            f'cross_outlet_tone_variance_{suffix}': _wmean(g, 'variance'),
            f'cross_media_alpha_{suffix}': _wmean(g, 'alpha'),
            f'n_events_{suffix}': int(len(g)),
        }), include_groups=False)
        .reset_index()
    )
    return panel


def main():
    stage_start = time.time()
    # 功能说明 banner — 写入 <stage>.log, 让日志自带阶段用途说明 (仿 39c)。
    logger.info("=" * 72)
    logger.info("阶段 39f: 跨媒体源 tone 一致性 (Krippendorff α + 事件窗方差; v3.7.0 PR #12, D3)")
    logger.info("=" * 72)
    logger.info("【功能】同一家银行出大新闻的那几天, 不同媒体打出来的语调一致吗? 找出每家银行的")
    logger.info("        报道高峰日 (event episode), 在事件窗内度量各媒体语调的分歧度与一致性,")
    logger.info("        给 bank-year 面板加 9 列 (variance/α/n_events × full/ctx/ss 三轨)。")
    logger.info("【方法】bank-day 文章数 ≥ 该 bank p90 (N_ARTICLE_PERCENTILE=0.90) 为峰值日 → 相邻")
    logger.info(f"        gap ≤ 2×{EVENT_WINDOW_DAYS}d 的重叠 ±{EVENT_WINDOW_DAYS}d 窗合并为 episode; "
                f"每事件要求 ≥{MIN_OUTLETS_PER_EVENT} 家媒体。")
    logger.info("        variance=outlet 间 tone 方差 (np.var ddof=1, 事件窗条件); Krippendorff(2004)")
    logger.info("        α (interval scale, outlet×day matrix, NaN 作 missing); 按 episode 文章数加权聚合。")
    logger.info("【判读】α 越高 (→1) = 各媒体语调越吻合, 情感信号越可靠 (Tetlock 2007 信号质量代理);")
    logger.info("        variance 越高 = 媒体分歧越大 (本身也是信息, 第 10 篇媒体分歧度核心变量)。")
    logger.info("【确定性】无 LLM/Embedding, 纯 CPU 只读已落盘 stage 21 + 确定性 _SENT_TO_TONE 派生 → 逐位可复现。")
    logger.info("⚠️  cross_outlet_tone_variance_{full,ctx,ss} 与第 10 篇 bank_media_disagreement spec 冻结")
    logger.info("    main treatment **同名异构** (本模块=事件窗条件; spec=全年无条件截面); 采用前须对齐, 当前仅 validation。")
    logger.info("=" * 72)

    output_dir = CONFIG['paths']['output_dir']
    # fix(stage21-read-config-wiring, 2026-06-25): stage 21 输出名经 config 单一真值解析
    # (output_21_tone_llms[_full]; 键存在值=默认 → golden-safe), 与 runner 新鲜度守卫
    # (_OPTIN_FEATURE_UPSTREAMS, 同日 config 化) 同口径, 替代硬编码字面量。
    _fn = CONFIG['filenames']
    src_path = os.path.join(output_dir, _fn.get('output_21_tone_llms_full', '21_tone_llms_full.parquet'))
    if not os.path.exists(src_path):
        src_path = os.path.join(output_dir, _fn.get('output_21_tone_llms', '21_tone_llms.parquet'))
    if not os.path.exists(src_path):
        logger.error(f"  stage 21 tone 未跑")
        sys.exit(1)

    panel_path = os.path.join(output_dir, '75_cross_media_alpha.parquet')

    # 🧭 项目 / 环境信息 + ⚙ 运行配置 + 📖 方法论依据 (仿 tone_words.py 金标准; 纯日志, golden-safe)。
    try:
        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (跨媒体源 tone 一致性 Krippendorff α; 验证支线 39f)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板); 版本 v3.11.1")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "纯 CPU / 无 LLM·Embedding·网络·API ($0) / 逐位可复现")
        try:
            import krippendorff as _krip_probe  # noqa: F401
            _krip_ver = getattr(_krip_probe, '__version__', '?')
            logger.info(f"     · krippendorff: {_krip_ver} (硬运行依赖; 缺失则 α 输出 NaN, 仅 variance 可用)")
        except ImportError:
            logger.warning("     · krippendorff: 未装 → cross_media_alpha_* 全 NaN, 仅 variance 可用")

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 输入:   {src_path} (优先 21_tone_llms_full, 回退 21_tone_llms)")
        logger.info(f"     · 输出:   {panel_path} (bank-year 面板 9 列: variance/α/n_events × 三轨)")

        logger.info("  ⚙ 运行配置 (模块常量)")
        logger.info(f"     · 事件窗: ±{EVENT_WINDOW_DAYS}d | 峰值分位 N_ARTICLE_PERCENTILE="
                    f"{sig4(N_ARTICLE_PERCENTILE)} (p90) | 每事件最少媒体 MIN_OUTLETS_PER_EVENT="
                    f"{MIN_OUTLETS_PER_EVENT}")
        logger.info(f"     · episode 合并: 相邻 peak gap ≤ 2×{EVENT_WINDOW_DAYS}d 窗重叠 → 传递合并 (取窗口并集)")
        logger.info("     · 轨道集: full / ctx / ss (银行+金科同句); ss 列缺失时该轨优雅跳过")
        logger.info(f"     · α 门槛: 可接受 ≥ {sig4(0.667)} / 良好 ≥ {sig4(0.80)} (Krippendorff 2004)")
        logger.info(f"     · G-D3.1 覆盖目标: valid bank-year ≥ {pct4(0.60)} (D-0 实测项)")

        logger.info("  📖 方法论依据")
        logger.info("     · 跨多源 tone 一致性作信号质量代理: Tetlock, P. C. (2007). Giving content to "
                    "investor sentiment: The role of media in the stock market. The Journal of "
                    "Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x")
        logger.info("     · 跨标注者一致性度量: Krippendorff, K. (2004). Content analysis: An "
                    "introduction to its methodology. SAGE Publications. "
                    "(多评分员+任意测量尺度, 比 Cohen κ 稳健; 专著无 DOI)")
        logger.info("     · Krippendorff α 计算实现 (近期工具锚, inter-coder reliability): Marzi, G., "
                    "Balzano, M., & Marchiori, D. (2024). K-Alpha Calculator–Krippendorff's Alpha "
                    "Calculator: A user-friendly tool for computing Krippendorff's Alpha inter-rater "
                    "reliability coefficient. MethodsX, 12, 102545. "
                    "https://doi.org/10.1016/j.mex.2023.102545")
        logger.info("       (白话: Krippendorff α 2024 计算工具综述, 锚定本模块 outlet×day "
                    "reliability_data 的 inter-coder 信度计算口径。)")
        logger.info("     · reliability-data 结构 (raters × items, 缺失数据自然处理 → α 可估性): "
                    "Hayes, A. F., & Krippendorff, K. (2007). Answering the call for a standard "
                    "reliability measure for coding data. Communication Methods and Measures, "
                    "1(1), 77-89. https://doi.org/10.1080/19312450709336664")
        logger.info("       (白话: α 究竟在『平均多少 outlet × 多少 day』的可靠性矩阵上算出 —— "
                    "raters-per-item 密度直接决定 α 能否稳健估计, 故逐轨记录该密度分布。)")
        logger.info("     · 跨源 tone 方差作媒体分歧度测度: Li, S. Z., & Luan, Z. (2025). "
                    "News-based investor disagreement and stock returns. Review of Accounting "
                    "Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1")
        logger.info("       → 本模块 cross_outlet_tone_variance 即新闻级『媒体分歧度』的事件窗操作化 "
                    "(第 10 篇 bank_media_disagreement 核心变量), 分歧本身即定价信息。")
        logger.info("     · 多 outlet 媒体结构对覆盖的影响: Dyer, T., Lang, M., & Oh, J. (2025). "
                    "Media conglomeration, local news, and capital market consequences. "
                    "Management Science, 71(8), 6602-6626. https://doi.org/10.1287/mnsc.2023.02247")
        logger.info("       → 锚定跨媒体源 (多 outlet) 一致性/分歧作为信号质量与覆盖结构的代理。")
        logger.info("     · 白话: 把各家媒体当『评分员』, α 衡量它们对同一银行事件的语调打分有多吻合 —— "
                    "越吻合=情感信号越可靠; 分歧本身也是信息 (媒体分歧度)。")
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法信息打印失败 (不影响处理): {_e}")

    _t_load = time.time()
    art_df = pd.read_parquet(src_path)
    logger.info(f"  article-level tone: {len(art_df):,d} 行 (加载耗时 {sig4(time.time() - _t_load)} s)")

    # 📂 输入 schema / 关键列命中 provenance (log-only, golden-safe): 本模块控制流分支于
    # llm_vote_tone_{full,ctx,ss} 是否存在 (存在=直接用; 否则尝试 llm_sentiment_{trk}
    # → _SENT_TO_TONE 派生)。在加载点记录列数与关键列存在性, 文档化本次将走哪条派生
    # 路径 (stage-boundary 复现性 provenance)。仅读 columns/shape, 不改任何数据。
    try:
        _expect_cols = [
            'target_bank', '日期', '媒体(中文)',
            'llm_vote_tone_full', 'llm_vote_tone_ctx', 'llm_vote_tone_ss',
            'llm_sentiment_full', 'llm_sentiment_ctx', 'llm_sentiment_ss',
        ]
        _present = [c for c in _expect_cols if c in art_df.columns]
        _missing = [c for c in _expect_cols if c not in art_df.columns]
        logger.info(
            f"    📂 输入 schema: {art_df.shape[1]:,d} 列 × {len(art_df):,d} 行; "
            f"stage-21 关键列命中 {len(_present)}/{len(_expect_cols)} → 存在 {_present}"
        )
        if _missing:
            logger.info(
                f"      └ 缺失关键列 {_missing} "
                "(缺 llm_vote_tone_* 但有 llm_sentiment_* 时走确定性 _SENT_TO_TONE 派生)"
            )
    except Exception as _se:  # noqa: BLE001
        logger.debug(f"    输入 schema provenance 跳过 (不影响处理): {_se}")

    _t_events = time.time()
    events = detect_bank_events(art_df)
    logger.info(f"  检测到 {len(events):,d} 个 bank-level events "
                f"(事件检测耗时 {sig4(time.time() - _t_events)} s)")

    # 39f fix (2026-05-30): panel 级 llm_vote_tone_{full,ctx,ss} 是 bank-year 聚合阶段
    # 才产生的列, article 级 parquet 没有 (只有 llm_sentiment_{full,ctx,ss})。此前
    # 三轨都因列缺失而 graceful-skip, stage 39f 永不产出。这里按 encode_sentiment
    # 同款映射 (正面=+1 / 中性=0 / 负面=-1) 派生 article 级数值 tone, 让 cross-media
    # variance + Krippendorff α 真正计算。ss = 银行+金科同句共现轨, 其
    # llm_sentiment_ss 缺失时该轨不派生 tone 列 → 下游 panels 循环优雅跳过。
    # 与 encode.py SENTIMENT_MAP 一致 (LLM 仅产 正面/中性/负面; 其它标签 → NaN)
    _SENT_TO_TONE = {'正面': 1.0, '中性': 0.0, '负面': -1.0}
    for _trk in ('full', 'ctx', 'ss'):
        _tcol, _scol = f'llm_vote_tone_{_trk}', f'llm_sentiment_{_trk}'
        if _tcol not in art_df.columns and _scol in art_df.columns:
            art_df[_tcol] = art_df[_scol].map(_SENT_TO_TONE)
            logger.info(f"  派生 article 级 {_tcol} ← {_scol} "
                        f"(非空 {int(art_df[_tcol].notna().sum())}/{len(art_df)})")

    # 三轨各算一次 (full/ctx/ss); ss = 银行+金科同句共现轨, tone 列缺失时跳过该轨
    _t_tracks = time.time()
    panels = []
    for suffix, tone_col in (
        ('full', 'llm_vote_tone_full'),
        ('ctx', 'llm_vote_tone_ctx'),
        ('ss', 'llm_vote_tone_ss'),
    ):
        if tone_col not in art_df.columns:
            logger.warning(f"  {tone_col} 不在 art_df.columns; 跳过 {suffix}")
            continue
        _t_trk = time.time()
        logger.info(f"  ── 轨道 {suffix} ──")
        outlet_tones = compute_outlet_tone_aggregates(art_df, events, tone_col)
        logger.info(f"    valid 三元组 (n_outlets ≥ 2): {len(outlet_tones):,d}")
        events_metrics = compute_variance_and_alpha(outlet_tones)
        if events_metrics.empty:
            logger.info(f"    轨道 {suffix} 无有效事件指标 (耗时 {sig4(time.time() - _t_trk)} s); 跳过")
            continue
        # 📊 reliability-data 密度分布 (log-only, golden-safe; Hayes & Krippendorff 2007):
        # Krippendorff α 的可估性临界依赖"每个 item 有几个 rater"——这里 outlet=rater /
        # day=item / article=底层标注。逐轨报每事件 raters(outlets)/items(days)/articles 的
        # 中位与极值, 让审稿人知道该轨 α 究竟"在平均多少 outlet × 多少 day 上算出来"
        # (顶刊 α 报告必备的密度诊断, 此前仅落 n_units/total_events 聚合数, 中间矩阵密度未暴露)。
        try:
            _dn_out = events_metrics['n_outlets']
            _dn_day = events_metrics['n_days']
            _dn_art = events_metrics['n_articles']
            logger.info(
                f"    📊 reliability-data 密度 (n={len(events_metrics):,d} events): "
                f"raters/event(outlets) 中位={sig4(_dn_out.median())} "
                f"[min={int(_dn_out.min()):,d}, max={int(_dn_out.max()):,d}]; "
                f"items/event(days) 中位={sig4(_dn_day.median())} "
                f"[min={int(_dn_day.min()):,d}, max={int(_dn_day.max()):,d}]; "
                f"articles/event 中位={sig4(_dn_art.median())} "
                f"[min={int(_dn_art.min()):,d}, max={int(_dn_art.max()):,d}]"
            )
        except Exception as _de:  # noqa: BLE001
            logger.debug(f"    reliability-data 密度诊断跳过 (不影响产物): {_de}")
        panel_s = aggregate_to_bank_year(events_metrics, suffix)
        panels.append(panel_s)

        # G-D3.1 valid 覆盖诊断
        bank_year_total = art_df.groupby(['target_bank']).size().shape[0]
        cov = panel_s['target_bank'].nunique() / max(bank_year_total, 1)
        logger.info(
            f"    G-D3.1: valid bank 覆盖 = {pct4(cov)} "
            f"({'PASS' if cov >= 0.60 else 'WARN'}); 轨道耗时 {sig4(time.time() - _t_trk)} s"
        )
    logger.info(f"  三轨计算合计耗时 {sig4(time.time() - _t_tracks)} s")

    if not panels:
        # graceful skip: stage 21 article-level parquet 早期版本 schema 缺
        # llm_vote_tone_full / ctx / ss (该列名为 panel 聚合阶段加上). 此时三轨
        # 都无法计算 cross-media variance, 返回 exit 0 而非中断 validation.
        logger.warning("  三轨均无有效输出 (article-level tone 列缺失); 跳过 stage 39f")
        return

    panel = panels[0]
    for p in panels[1:]:
        panel = panel.merge(p, on=['target_bank', 'year'], how='outer')

    # 结果分析 — 写入日志: 逐轨 variance/α/n_events 实测值 + 对照阈值/预期方向判读。
    # 仅用于日志, 不回写 panel (golden-safe)。
    # crash-guard (硬化 A): 本分析块在 panel.to_parquet 写盘之前执行, 任何读数/算指标
    # 异常 (空 Series 聚合 / 缺列 KeyError / dtype 边缘 case) 都不得拖垮整个阶段而丢产物;
    # 整体包 try/except, 失败仅告警跳过, 写盘照常进行 (保证 golden-safe)。
    try:
        try:
            import krippendorff  # noqa: F401
            _krip_ok = True
        except ImportError:
            _krip_ok = False
        logger.info("-" * 72)
        logger.info(f"【结果分析】跨媒体 tone 一致性 (bank-year 面板 {len(panel)} 行; 三轨 full/ctx/ss):")
        if not _krip_ok:
            logger.warning(
                "  krippendorff 未装 → 所有 cross_media_alpha_* 列为 NaN, 仅 variance 可用; "
                "α 一致性证据缺失 (优雅降级, pip install krippendorff 后可恢复)"
            )
        for _trk in ('full', 'ctx', 'ss'):
            _vcol = f'cross_outlet_tone_variance_{_trk}'
            _acol = f'cross_media_alpha_{_trk}'
            _ncol = f'n_events_{_trk}'
            # column-guard (硬化 C): ss 轨缓存常未播种 → variance 列缺失即跳过该轨
            if _vcol not in panel.columns:
                logger.info(f"  轨道 {_trk}: 未产出 (article 级 tone 列缺失, 该轨优雅跳过)")
                continue
            _var_s = panel[_vcol].dropna()
            _alpha_s = panel[_acol].dropna() if _acol in panel.columns else pd.Series(dtype=float)
            _n_units = int(panel[_vcol].notna().sum())
            _total_events = int(panel[_ncol].sum()) if _ncol in panel.columns else 0
            logger.info(
                f"  轨道 {_trk}: {_n_units} 个 bank-year 单元有有效输出, 合计 {_total_events} 个 event episode"
            )
            # variance: 越高 = 媒体分歧越大 (无绝对阈值, 报均值/极值供横向对比)
            # NaN-guard (硬化 B): dropna 后 len==0 走 "全 NaN" 分支, 不落进数值统计
            if len(_var_s) > 0:
                logger.info(
                    f"    cross_outlet_tone_variance: 均值={sig4(_var_s.mean())} "
                    f"中位={sig4(_var_s.median())} [min={sig4(_var_s.min())}, max={sig4(_var_s.max())}]  "
                    "(越高=各媒体语调分歧越大; 0=完全一致)"
                )
                # 分布展宽诊断 (log-only, sig4): std 越大 = 各事件的分歧程度本身差异越大。
                _v_std = float(_var_s.std()) if len(_var_s) > 1 else 0.0
                logger.info(
                    f"      └ 标准差={sig4(_v_std)} (n={len(_var_s):,d} 个有效 bank-year; "
                    "分布展宽, 越大=事件间分歧程度异质性越高)"
                )
            else:
                logger.info(f"    cross_outlet_tone_variance: 全 NaN (无 ≥{MIN_OUTLETS_PER_EVENT} 媒体的事件)")
            # α: 越高(→1)=越一致, 越好。常用门槛 α≥0.667 可接受 / ≥0.80 良好 (Krippendorff 2004)
            # NaN-guard (硬化 B): 仅 dropna 后非空才进方向判读, 否则 mean=nan 且 ternary 恒 False 误判
            if len(_alpha_s) > 0:
                _a_mean = float(_alpha_s.mean())
                if _a_mean >= 0.80:
                    _verdict = "良好 (媒体高度一致, 信号可靠)"
                elif _a_mean >= 0.667:
                    _verdict = "可接受 (Krippendorff 2004 最低门槛)"
                else:
                    _verdict = "偏低/分歧 (信号一致性弱, 或本身即媒体分歧信息)"
                logger.info(
                    f"    cross_media_alpha: 均值={sig4(_a_mean)} 中位={sig4(_alpha_s.median())} "
                    f"(非空 {len(_alpha_s):,d}/{_n_units:,d})  → {_verdict}"
                )
                # 一致性稳定度诊断 (log-only, sig4): α 标准差越小 = 跨事件一致性越稳定。
                _a_std = float(_alpha_s.std()) if len(_alpha_s) > 1 else 0.0
                logger.info(
                    f"      └ α 标准差={sig4(_a_std)} [min={sig4(_alpha_s.min())}, "
                    f"max={sig4(_alpha_s.max())}] (越小=媒体一致性跨事件越平稳)"
                )
            elif _krip_ok:
                logger.info(
                    "    cross_media_alpha: 全 NaN (无 item 满足 ≥2 outlets 同日报道, α 不可估)"
                )
        # G-D3.1 总覆盖判读 (用 full 轨; D-0 实测项要求 valid bank-year 覆盖 ≥60%)
        # 口径修正 (P1): panel 以 (target_bank, year) 为单元, full variance 的
        # notna().sum() 是**有效 bank-year 行数**; 分母须同口径取**总 bank-year 单元数**,
        # 否则 (分子=bank-year 行 / 分母=去重 bank 数) 在 T>1 时比值可 >100%, 且与
        # 注释 'bank-year 覆盖' / 行内 G-D3.1 'bank 覆盖' 自相矛盾, 误导 D-0≥60% 判读。
        # 分母从 art_df 的日期列派生 year, drop_duplicates 取 bank-year 总数; 缺日期列
        # 时优雅降级为 'bank 覆盖' 口径 (分子=有效 bank 数, 与 line 442 自洽口径对齐)。
        # column-guard (硬化 C): full variance 列缺失 / 总单元数为 0 时不算覆盖率。
        if 'cross_outlet_tone_variance_full' in panel.columns and 'target_bank' in art_df.columns:
            _date_col = '日期'
            if _date_col in art_df.columns:
                # bank-year 口径 (与 panel 单元一致, 比值 ≤100%, 对齐注释 'bank-year 覆盖')
                _by = art_df[['target_bank', _date_col]].copy()
                _by['_y'] = pd.to_datetime(_by[_date_col], errors='coerce').dt.year
                _bank_year_total = int(_by[['target_bank', '_y']].dropna().drop_duplicates().shape[0])
                _cov_label = "full 轨有效 bank-year 数 / 总 bank-year 数"
                _cov_denom = _bank_year_total
            else:
                # 降级: 缺日期列 → bank 口径 (分子分母均以银行为单元, 与 line 442 自洽口径对齐)
                _cov_label = "full 轨有效 bank 数 / 总 bank 数"
                _cov_denom = int(art_df['target_bank'].nunique())
            if _cov_denom > 0:
                # 分子: full variance 非空的 panel 行数 (bank-year 单元); 降级口径下亦以
                # 有效 bank 数为分子, 与降级分母同口径 (line 442 范式)。
                if _cov_label.endswith("总 bank 数"):
                    _cov_num = int(
                        panel.loc[panel['cross_outlet_tone_variance_full'].notna(),
                                  'target_bank'].nunique()
                    )
                else:
                    _cov_num = int(panel['cross_outlet_tone_variance_full'].notna().sum())
                _cov_full = _cov_num / _cov_denom
                logger.info(
                    f"  G-D3.1 覆盖: {_cov_label} = {pct4(_cov_full)} "
                    f"({'PASS (≥60%)' if _cov_full >= 0.60 else 'WARN (<60%, 事件/媒体稀疏)'})"
                )
        logger.info(
            f"  检测到 {len(events)} 个 bank-level events (合并重叠 ±{EVENT_WINDOW_DAYS}d 窗后的独立 episode)"
        )
        logger.info(
            "  ⚠ 盘面 T=2 小样本: 事件检测/媒体覆盖均稀疏, 仅验证管道正确性; "
            "全量 17M/T=18 实测 α 与覆盖率以生产 run 为准。"
        )
        logger.info("-" * 72)
    except Exception as _e:
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")

    _t_write = time.time()
    panel.to_parquet(panel_path, index=False)
    logger.info(f"  panel → {panel_path} ({len(panel):,d} 行 × {panel.shape[1]:,d} 列; "
                f"写盘耗时 {sig4(time.time() - _t_write)} s)")
    logger.info(f"  ⏱ 阶段总耗时: {sig4(time.time() - stage_start)} s")


if __name__ == '__main__':
    main()
