"""news_process.pipeline.audit.cross_media_alpha — stage 39f Krippendorff α.

v3.7.0 PR #12 (D3) — 跨媒体源 tone 一致性 Krippendorff α + tone variance.

⚠️  IMPORTANT — 与 v3.7.0 第 10 篇 ``bank_media_disagreement`` (RFS/JFE 立项)
    重叠. 第 10 篇 main treatment = ``cross_outlet_tone_variance_full``;
    本模块同时输出 variance + Krippendorff α 两个度量, 让第 10 篇可直接消费
    variance 作 main, α 作 robustness. 启用前必须与第 10 篇作者协调 spec.

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
对每个 (bank b, event window) 三元组:
    1. 收集报道该 bank 的媒体集 M (要求 |M| ≥ 2, 否则 NaN)
    2. 每家媒体 m: 算窗口内 tone 均值 T_m,b
    3. 计算 (a) variance(T_m,b across m) — 与第 10 篇 main 对齐
            (b) Krippendorff α (interval scale) — α robustness
    4. bank-year 加权均值 (按 event 内文章数加权)

事件窗口定义
-----------
- bank-level shock 自动检测: bank-year 内 ``n_articles`` > p90 of bank history
  OR ``tone_volatility_within_day`` > p90
- 窗口 ±3d (与 v2.3 G-D3.1 一致)

panel 新增 4 列
---------------
``cross_outlet_tone_variance_{full,ctx}``  第 10 篇 main treatment
``cross_media_alpha_{full,ctx}``           α 度量, robustness

依赖
----
pip install krippendorff>=0.5.0 (默认注释化, 见 requirements.txt:107).

D-0 实测项 (v2.3 G-D3.1)
------------------------
valid (bank, event) 三元组覆盖 ≥ 60% bank-year.
"""

from __future__ import annotations

import os
import sys
import time
from datetime import timedelta

import numpy as np
import pandas as pd

# Path injection
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config  # noqa: E402
from news_process.core.logging import setup_logging  # noqa: E402

CONFIG = load_config()
STAGE_NAME = "39f_cross_media_alpha"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

EVENT_WINDOW_DAYS = 3
MIN_OUTLETS_PER_EVENT = 2
N_ARTICLE_PERCENTILE = 0.90


def detect_bank_events(
    article_df: pd.DataFrame,
    date_col: str = '日期',
) -> pd.DataFrame:
    """检测 bank-level events: bank-year 内文章数高于该 bank p90.

    Returns:
        events DataFrame [target_bank, event_date].
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
    # 每 bank p90
    p90 = by_day.groupby('target_bank')['n_per_day'].quantile(N_ARTICLE_PERCENTILE).reset_index()
    p90.columns = ['target_bank', 'p90']
    by_day = by_day.merge(p90, on='target_bank')
    events = by_day[by_day['n_per_day'] >= by_day['p90']][['target_bank', 'event_date']]
    return events.reset_index(drop=True)


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
      (与第 10 篇 ``cross_outlet_tone_variance`` main 指标对齐).
    - ``daily_matrix``: outlet × day matrix (raters × items), NaN 填充无报道.
      → Krippendorff α 真正可用的 reliability_data 输入.

    Returns:
        ``{(bank, event_date): {'outlet_tones': ndarray, 'daily_matrix': ndarray}}``
    """
    df = article_df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df['_day'] = df[date_col].dt.normalize()

    out = {}
    for _, ev in events.iterrows():
        bank = ev['target_bank']
        ed = pd.Timestamp(ev['event_date'])
        mask = (
            (df['target_bank'] == bank)
            & (df['_day'] >= ed - timedelta(days=EVENT_WINDOW_DAYS))
            & (df['_day'] <= ed + timedelta(days=EVENT_WINDOW_DAYS))
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
        }
    return out


def compute_variance_and_alpha(
    event_data: dict[tuple, dict],
) -> pd.DataFrame:
    """对每个三元组算 variance (outlet 间) 与 Krippendorff α (outlet × day).

    修 S2.3: variance 走 outlet-level 1D (与第 10 篇 main 对齐),
    α 走 outlet × day 二维 matrix (raters × items, NaN 填充无报道).

    Returns:
        DataFrame [target_bank, event_date, n_outlets, n_days, variance, alpha].
    """
    try:
        import krippendorff
        has_krip = True
    except ImportError:
        logger.warning(
            "krippendorff 未装; v3.7.0 启用步骤: 取消 requirements.txt 中 "
            "krippendorff 行注释后 pip install. α 输出 NaN, 仅 variance 可用"
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
            'variance': var,
            'alpha': alpha,
        })
    return pd.DataFrame(rows)


def aggregate_to_bank_year(
    events_metrics: pd.DataFrame,
    suffix: str,
) -> pd.DataFrame:
    """bank-year 加权均值 (按 n_outlets 加权)."""
    df = events_metrics.copy()
    df['year'] = pd.to_datetime(df['event_date']).dt.year
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
        .apply(lambda g: pd.Series({
            f'cross_outlet_tone_variance_{suffix}': _wmean(g, 'variance'),
            f'cross_media_alpha_{suffix}': _wmean(g, 'alpha'),
            f'n_events_{suffix}': int(len(g)),
        }))
        .reset_index()
    )
    return panel


def main():
    stage_start = time.time()
    logger.info("=" * 60)
    logger.info("阶段 39f: Cross-Media tone variance + α (v3.7.0 PR #12, D3)")
    logger.info("⚠️  与第 10 篇 bank_media_disagreement 重叠; spec 对齐前仅 validation")
    logger.info("=" * 60)

    output_dir = CONFIG['paths']['output_dir']
    src_path = os.path.join(output_dir, '21_tone_llms_full.parquet')
    if not os.path.exists(src_path):
        src_path = os.path.join(output_dir, '21_tone_llms.parquet')
    if not os.path.exists(src_path):
        logger.error(f"  stage 21 tone 未跑")
        sys.exit(1)

    art_df = pd.read_parquet(src_path)
    logger.info(f"  article-level tone: {len(art_df)} 行")

    events = detect_bank_events(art_df)
    logger.info(f"  检测到 {len(events)} 个 bank-level events")

    panels = []
    for suffix, tone_col in (
        ('full', 'llm_vote_tone_full'),
        ('ctx', 'llm_vote_tone_ctx'),
    ):
        if tone_col not in art_df.columns:
            logger.warning(f"  {tone_col} 不在 art_df.columns; 跳过 {suffix}")
            continue
        logger.info(f"  ── 轨道 {suffix} ──")
        outlet_tones = compute_outlet_tone_aggregates(art_df, events, tone_col)
        logger.info(f"    valid 三元组 (n_outlets ≥ 2): {len(outlet_tones)}")
        events_metrics = compute_variance_and_alpha(outlet_tones)
        if events_metrics.empty:
            continue
        panel_s = aggregate_to_bank_year(events_metrics, suffix)
        panels.append(panel_s)

        # G-D3.1 valid 覆盖诊断
        bank_year_total = art_df.groupby(['target_bank']).size().shape[0]
        cov = panel_s['target_bank'].nunique() / max(bank_year_total, 1)
        logger.info(
            f"    G-D3.1: valid bank 覆盖 = {cov:.1%} "
            f"({'PASS' if cov >= 0.60 else 'WARN'})"
        )

    if not panels:
        # graceful skip: stage 21 article-level parquet 早期版本 schema 缺
        # llm_vote_tone_full / ctx (该列名为 panel 聚合阶段加上). 此时双轨
        # 都无法计算 cross-media variance, 返回 exit 0 而非中断 validation.
        logger.warning("  双轨均无有效输出 (article-level tone 列缺失); 跳过 stage 39f")
        return

    panel = panels[0]
    for p in panels[1:]:
        panel = panel.merge(p, on=['target_bank', 'year'], how='outer')

    panel_path = os.path.join(output_dir, '39f_cross_media_alpha.parquet')
    panel.to_parquet(panel_path, index=False)
    logger.info(f"  panel → {panel_path}")
    logger.info(f"  耗时: {time.time() - stage_start:.1f} s")


if __name__ == '__main__':
    main()
