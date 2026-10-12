"""LLM 留篇误判的测量稳健性检验 (误分类偏倚诊断的后续)。

stage 63 的误分类偏倚诊断 (Carlson & Burbano 2026, SMJ 47(3):699-725) 显示: 在任务一
专家金标准上, LLM「是否银行金科新闻」判错的文章显著更长 (约 2,200 vs 1,400 字, 三轨 p<0.001),
且模型自报的留篇置信度更低 (full/ctx 轨 p<0.01)。误差若与文章特征相关, 银行-年情绪指数
可能随长文/低置信文章的占比而系统偏移。本模块重算银行-年 LLM 投票情绪 (llm_vote_tone 口径:
留篇文章的 正面=1/中性=0/负面=-1 均值) 的四个替代版本, 与主口径比较:

  ① 剔除长文: 去掉正文长度高于全语料 P75 的文章;
  ② 剔除低置信: 去掉三家模型留篇置信度均值低于全语料 P25 的文章;
  ③ 两者都剔除;
  ④ 长度调整: 文章级投票分对 log(正文长度) 做 OLS, 取残差 + 总均值后再聚合。

报告: 各版本与主口径在银行-年格上的 Pearson / Spearman 相关与平均绝对差 (全部格与
文章数≥5 的格两档), 以及全国年度均值序列的相关与最大绝对差 (服务"进程"刻画)。

只读 21_tone_llms_full.parquet 与 40_panel_yearly.parquet, 只写
eval_reports/misclassification_robustness.csv; 不进 DAG、不进面板, golden 无关, $0。
主口径先与面板 llm_vote_tone_{track} 对拍, 复现不一致则报告该偏差。

用法 (repo 根): python -m news_process.validation.misclassification_robustness

白话: 机器在长文章、没把握的文章上更容易判错 "算不算金科新闻"; 把这些文章拿掉或按长度
校正后重算情绪指数, 看结果变不变 —— 不怎么变, 说明这类误判没有把指数带偏。
"""
import os
import sys
import time

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
_PROJECT_PARENT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config  # noqa: E402

SCORE = {'正面': 1, '中性': 0, '负面': -1}
MODELS = ('gpt54nano', 'gemini31', 'deepseekv4')
TRACKS = ('_full', '_ctx', '_ss')


def _article_frame(path: str) -> pd.DataFrame:
    cols = ['docid', 'target_bank', '日期', '内容']
    for t in TRACKS:
        cols += [f'llm_verified{t}', f'llm_sentiment{t}'] + [f'{m}_verification_confidence{t}' for m in MODELS]
    df = pd.read_parquet(path, columns=cols)
    df['year'] = pd.to_datetime(df['日期'], errors='coerce').dt.year
    df['len'] = df['内容'].astype(str).str.len()
    return df.drop(columns=['内容']).dropna(subset=['year'])


def _cell_means(d: pd.DataFrame, score_col: str) -> pd.DataFrame:
    g = d.groupby(['target_bank', 'year'])[score_col]
    return pd.DataFrame({'tone': g.mean(), 'n': g.count()})


def _compare(main: pd.DataFrame, alt: pd.DataFrame, min_n: int):
    j = main.join(alt, how='inner', lsuffix='_m', rsuffix='_a').dropna(subset=['tone_m', 'tone_a'])
    j = j[(j['n_m'] >= min_n) & (j['n_a'] >= min_n)]
    if len(j) < 3:
        return len(j), np.nan, np.nan, np.nan
    return (len(j), j['tone_m'].corr(j['tone_a']), j['tone_m'].corr(j['tone_a'], method='spearman'),
            float((j['tone_m'] - j['tone_a']).abs().mean()))


def run() -> pd.DataFrame:
    cfg = load_config()
    P = cfg['paths']['output_dir']
    df = _article_frame(os.path.join(P, '21_tone_llms_full.parquet'))
    panel = pd.read_parquet(os.path.join(P, '40_panel_yearly.parquet'),
                            columns=['target_bank', 'year'] + [f'llm_vote_tone{t}' for t in TRACKS])
    rows = []
    len_p75 = df['len'].quantile(0.75)
    for t in TRACKS:
        ver = df[f'llm_verified{t}'].fillna(False).astype(bool)
        d = df[ver].copy()
        d['s'] = d[f'llm_sentiment{t}'].map(SCORE)
        d = d.dropna(subset=['s'])
        d['conf'] = d[[f'{m}_verification_confidence{t}' for m in MODELS]].mean(axis=1)
        conf_p25 = d['conf'].quantile(0.25)
        # ④ 长度调整: s = a + b·log(len) + e → 残差 + 总均值
        x = np.log1p(d['len'].to_numpy(dtype=float))
        b = np.polyfit(x, d['s'].to_numpy(dtype=float), 1)
        d['s_adj'] = d['s'] - (b[0] * x + b[1]) + d['s'].mean()

        main = _cell_means(d, 's')
        # 主口径对拍面板
        pj = main.join(panel.set_index(['target_bank', 'year'])[f'llm_vote_tone{t}'], how='inner').dropna()
        rows.append({'轨道': t, '版本': '主口径 vs 面板 llm_vote_tone', '剔除文章占比': 0.0,
                     '文章数门槛': 1, '银行年格数': len(pj),
                     'Pearson': pj['tone'].corr(pj[f'llm_vote_tone{t}']),
                     'Spearman': pj['tone'].corr(pj[f'llm_vote_tone{t}'], method='spearman'),
                     '平均绝对差': float((pj['tone'] - pj[f'llm_vote_tone{t}']).abs().mean()),
                     '年度均值序列_相关': np.nan, '年度均值序列_最大绝对差': np.nan})
        variants = {
            '①剔除长文 (>P75)': d[d['len'] <= len_p75],
            '②剔除低置信 (<P25)': d[d['conf'] >= conf_p25],
            '③长文+低置信都剔除': d[(d['len'] <= len_p75) & (d['conf'] >= conf_p25)],
        }
        yr_main = d.groupby('year')['s'].mean()
        for name, sub in list(variants.items()) + [('④长度调整 (log 长度残差)', None)]:
            alt = _cell_means(d, 's_adj') if sub is None else _cell_means(sub, 's')
            yr_alt = (d.groupby('year')['s_adj'].mean() if sub is None else sub.groupby('year')['s'].mean())
            yj = pd.concat([yr_main, yr_alt], axis=1, keys=['m', 'a']).dropna()
            for min_n in (1, 5):
                n, pr, sp, mad = _compare(main, alt, min_n)
                rows.append({'轨道': t, '版本': name,
                             '剔除文章占比': 0.0 if sub is None else round(1 - len(sub) / len(d), 4),
                             '文章数门槛': min_n, '银行年格数': n, 'Pearson': pr, 'Spearman': sp,
                             '平均绝对差': mad, '年度均值序列_相关': yj['m'].corr(yj['a']),
                             '年度均值序列_最大绝对差': float((yj['m'] - yj['a']).abs().max())})
        print(f'{t}: 留篇文章 {len(d):,}, 长度 P75={len_p75:.0f} 字, 置信度 P25={conf_p25:.3f}, '
              f'log 长度斜率={b[0]:.4f}')
    out = pd.DataFrame(rows).round(4)
    out['生成时间'] = time.strftime('%Y-%m-%d %H:%M:%S')
    path = os.path.join(P, 'eval_reports', 'misclassification_robustness.csv')
    out.to_csv(path, index=False, encoding='utf-8-sig')
    print(f'{len(out)} 行 → {path}')
    return out


if __name__ == '__main__':
    run()
