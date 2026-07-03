"""BERT 概率分布形状指标 — 叶模块 (leaf module, 零仓内依赖)。

执行计划: scripts/audit/BERT_DISTRIBUTION_METRICS_EXECUTION_PLAN_2026-07-03.md (v3-final)。

白话: stage 23 的三个中文金融 BERT 只被面板用了"概率平均值/标准差"; 本模块把
逐篇概率分布的**形状信息**也算出来 — 模型有多犹豫 (熵)、有没有极端唱衰 (尾部
占比)、坏话是不是集中爆发 (偏度)、三个模型互相吵不吵架 (跨模型分歧)、年内
语调是平稳还是先扬后抑 (年内波动/趋势)。全部是已落盘概率列的 $0 纯后处理,
不重跑任何推理。

构念家族锚点 (动机, **非构造出处**, 构造=本模块公式):
- 熵: Epstein & Schneider (2008, JF, doi:10.1111/j.1540-6261.2008.01314.x)
  信息质量与模糊厌恶; Ilut & Schneider (2014, AER, doi:10.1257/aer.104.8.2368)。
- 极端负面尾部: Baker, Bloom & Davis (2016, QJE, doi:10.1093/qje/qjw024)
  计数式指数; Engle et al. (2020, RFS, doi:10.1093/rfs/hhz072) 负面新闻指数。
- 净语调偏度: Chen, Hong & Stein (2001, JFE, doi:10.1016/S0304-405X(01)00066-6)
  方法论移植 (⚠ 本列 = raw skew 正=右偏, **非 NCSKEW** 无负号; 对象从收益率
  移植到情感得分, 构念含义不继承)。
- 跨模型分歧: Diether, Malloy & Scherbina (2002, JF,
  doi:10.1111/0022-1082.00490) 直接类比 (标准化方案与 DMS 不同);
  Cookson & Niessner (2020, JF, doi:10.1111/jofi.12852)。
- 年内时序: Tetlock (2007, JF, doi:10.1111/j.1540-6261.2007.01232.x);
  Da, Engelberg & Gao (2015, RFS, doi:10.1093/rfs/hhu072) 月频构造前提。

架构合同 (计划 §2.6):
- 真叶模块: 仅依赖 numpy/pandas; ``BERT_MODELS``/``THREE_CLASS_MODELS`` 由
  调用方参数注入 (encode/codebook/stata_export 可安全模块级 import 本模块;
  本模块**绝不** import encode — codebook.py 已模块级 import encode, 反向
  即成真环)。
- 三轨循环在模块内 (``TRACKS``), 调用方对每个 compute_* 只调一次。
- per-(model, track) 守卫: ``{b}_正面{trk}``/``{b}_负面{trk}`` 任一缺席 →
  该 (model, track) 的全部中间列**不出现在返回 dict** (键也不产, per-model
  独立降级, 镜像 finbert2 优雅跳过语义); ``iter_*`` 声明器与 df 无关, 恒返回
  声明全集 — 声明集 − 实际产出集 = 合法缺席轨。
- 中间列生命周期: 文章级中间列 (``_ent_*``/``_xneg_ind_*``/``_nt_art_*``/
  ``_xmd_art*``/``_lblhet_art*``) 由 runner 在 log_diagnostics 之前按
  ``iter_intermediate_cols() ∩ df.columns`` 单点 drop, 绝不落入
  40_article_bank_level.parquet; 面板级临时列 ``_nt_n_*`` 由 encode 在
  skew 掩码后即刻 drop。
- ⚠ NaN 反模式点名: ``np.where(p > 0, p*log(p), 0)`` 会把 NaN 静默映 0
  (NaN>0 == False) — 本模块所有熵项先算后按行级 valid 掩码统一置 NaN。

计量铁律 (计划 §2.1/§2.2/§2.4/§5):
- 三阈值梯子 / per-model / 三轨 / WP-D 双轨各自 just-identified 并排,
  **禁混同一 over-identified Hansen J**。
- 跨模型水平比较禁令: finbert2 (二分类, 中性概率质量重归一) 的熵与 xneg
  占比与三分类模型**构念不可比**, 只比各自回归的标准化 β (Table A5 口径)。
- ``bert_xmodel_disp`` 的 z 参数取本次 run 文章宇宙 (样本依赖, 前视/不可
  逐篇复现), 故降为稳健轨; canonical = 逐篇局部确定的 ``bert_xmodel_lblhet``。
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# ---- SSOT 常量 (gate: tests/test_bert_distribution_metrics.py 锚死字面量) ----
TRACKS = ('_full', '_ctx', '_ss')
XNEG_THRESHOLDS = (0.80, 0.90, 0.95)
XNEG_CANONICAL = 0.90              # canonical ≡ 无后缀 (镜像 RARE_WORD_FREQ_CUTOFFS=3)
SKEW_MIN_N = 10                    # n<10 样本偏度纯噪声 (|G1| 上界 n=3→√3, n=4→2)
IYVOL_MIN_MONTHS = 3               # 年内波动: 有效月下限
IYTREND_MIN_MONTHS = 6             # 年内趋势: 3 点回归 df=1 纯噪声, 半年跨度起判

# 阈值 → 列名 tag (canonical 0.90 无后缀)
_XNEG_TAGS = {0.80: '_t80', 0.90: '', 0.95: '_t95'}


def _xneg_tag(tau: float) -> str:
    return _XNEG_TAGS[tau]


# ---------------------------------------------------------------------------
# 列名声明器 (与 df 无关, 恒返回声明全集)
# ---------------------------------------------------------------------------

def iter_intermediate_cols(models, three_class=None):
    """文章级中间列声明全集 (51 = 9 熵 + 27 xneg + 9 nt + 3 disp + 3 lblhet)。

    ``three_class`` 只影响计算路径 (finbert2 双列熵), **不影响键集** —
    参数保留仅为签名对称, 传 None 等价。
    """
    cols = []
    for trk in TRACKS:
        for b in models:
            cols.append(f'_ent_{b}{trk}')
            for tau in XNEG_THRESHOLDS:
                cols.append(f'_xneg_ind_{b}{_xneg_tag(tau)}{trk}')
            cols.append(f'_nt_art_{b}{trk}')
        cols.append(f'_xmd_art{trk}')
        cols.append(f'_lblhet_art{trk}')
    return cols


def iter_panel_cols(models):
    """面板列声明全集 (69 = 9 熵 + 27 xneg + 9 skew + 6 xmodel + 18 年内)。"""
    cols = []
    for trk in TRACKS:
        for b in models:
            cols.append(f'{b}_tone_entropy{trk}')
            for tau in XNEG_THRESHOLDS:
                cols.append(f'{b}_xneg_frac{_xneg_tag(tau)}{trk}')
            cols.append(f'{b}_net_tone_skew{trk}')
            cols.append(f'{b}_nt_iyvol{trk}')
            cols.append(f'{b}_nt_iytrend{trk}')
        cols.append(f'bert_xmodel_lblhet{trk}')
        cols.append(f'bert_xmodel_disp{trk}')
    return cols


def iter_agg_entries(models):
    """encode.build_aggregation_dict 消费的聚合条目 SSOT。

    yield (panel_col, src_col, func)。含 9 条 ``_nt_n_{b}{trk}`` 辅助计数
    (count = _nt_art 非 NaN 篇数, 与 groupby 'skew' 的 n 恰同口径) — 供
    post-agg SKEW_MIN_N 掩码, 掩码后由 encode 即刻 drop (禁用 pos_count:
    其语义 = argmax 判正篇数, 以语调为条件的内生样本选择)。
    WP-E 的 18 列不在此 (二次聚合走 compute_intrayear_dynamics + merge)。
    """
    for trk in TRACKS:
        for b in models:
            yield (f'{b}_tone_entropy{trk}', f'_ent_{b}{trk}', 'mean')
            for tau in XNEG_THRESHOLDS:
                tag = _xneg_tag(tau)
                yield (f'{b}_xneg_frac{tag}{trk}', f'_xneg_ind_{b}{tag}{trk}', 'mean')
            yield (f'{b}_net_tone_skew{trk}', f'_nt_art_{b}{trk}', 'skew')
            yield (f'_nt_n_{b}{trk}', f'_nt_art_{b}{trk}', 'count')
        yield (f'bert_xmodel_lblhet{trk}', f'_lblhet_art{trk}', 'mean')
        yield (f'bert_xmodel_disp{trk}', f'_xmd_art{trk}', 'mean')


# ---------------------------------------------------------------------------
# WP-A/B/C: 逐篇分布派生列
# ---------------------------------------------------------------------------

def _prob_cols(b: str, trk: str):
    return f'{b}_正面{trk}', f'{b}_负面{trk}', f'{b}_中性{trk}'


def compute_article_distribution_cols(df: pd.DataFrame, models, three_class) -> dict:
    """WP-A 归一化熵 + WP-B 极端负面指示 + WP-C 逐篇净语调。

    输入合同: df 须含 (或部分含) ``{b}_正面{trk}``/``{b}_负面{trk}``
    (三分类另加 ``{b}_中性{trk}``); 正/负任一缺席 → 该 (model, track) 全部
    键不产。返回 dict[str, pd.Series] (index 与 df 对齐)。

    - 熵 = −Σ p·ln(p) / ln(K_b), K_b 按 ``three_class`` 成员资格取 3/2;
      **finbert2 只读 pos/neg 两列** (其 ``_中性`` 列是全 NaN 占位,
      tone_berts.py 刻意非 0, 凭列存在判类数即静默清零 — 先例
      fix(dta-coverage-audit) runner._bert_argmax_pos_neg)。p=0 项记 0
      (lim p→0⁺ p·ln p = 0); 参与类任一 NaN → 整篇 NaN。
      ⚠ 二分类熵 = H((1+nt)/2) 是 |nt| 的严格单调**递减**变换 (Spearman
      ρ ≡ −1), "模糊度"构念仅在三分类模型上为主解释。
    - xneg 指示 = (P(负面) > τ) 的 float, **NaN 保持 NaN 禁 fillna(0)**
      (分母 = 概率非缺篇数; 三阈值同源同掩码 → 面板占比逐格精确单调)。
    - _nt_art = P(正面) − P(负面) ∈ [−1,1]; mean(_nt_art) ≡ 面板
      {b}_net_tone (pos/neg 同 NaN 掩码, encode.py net_tone 块注释明文)。
    """
    out: dict = {}
    three_class = set(three_class or ())
    for trk in TRACKS:
        for b in models:
            p_col, n_col, u_col = _prob_cols(b, trk)
            if p_col not in df.columns or n_col not in df.columns:
                continue  # per-(model, track) 独立降级: 键不产
            pos = pd.to_numeric(df[p_col], errors='coerce')
            neg = pd.to_numeric(df[n_col], errors='coerce')

            # --- WP-C 逐篇净语调 ---
            nt = pos - neg
            out[f'_nt_art_{b}{trk}'] = nt

            # --- WP-B 极端负面指示 (float 保 NaN) ---
            for tau in XNEG_THRESHOLDS:
                ind = (neg > tau).astype(float)
                ind[neg.isna()] = np.nan
                out[f'_xneg_ind_{b}{_xneg_tag(tau)}{trk}'] = ind

            # --- WP-A 归一化熵 ---
            if b in three_class and u_col in df.columns:
                probs = [pos, neg, pd.to_numeric(df[u_col], errors='coerce')]
            else:
                probs = [pos, neg]  # finbert2: 显式只读两列, K=2 Bernoulli 熵
            k = len(probs)
            valid = probs[0].notna()
            for p in probs[1:]:
                valid &= p.notna()
            acc = np.zeros(len(df), dtype=float)
            for p in probs:
                arr = p.to_numpy(dtype=float)
                mask = arr > 0  # NaN>0 == False → 该行贡献 0, 但随后被 valid 掩码置 NaN
                term = np.zeros_like(acc)
                term[mask] = arr[mask] * np.log(arr[mask])
                acc += term
            ent = pd.Series(-acc / np.log(k), index=df.index)
            ent[~valid] = np.nan
            out[f'_ent_{b}{trk}'] = ent
    return out


# ---------------------------------------------------------------------------
# WP-D: 跨模型逐篇分歧双轨
# ---------------------------------------------------------------------------

def compute_xmodel_dispersion(df: pd.DataFrame, models) -> dict:
    """canonical ``_lblhet_art{trk}`` (sign 两两不一致对占比) + 稳健轨
    ``_xmd_art{trk}`` (z 标准化净语调跨模型样本 SD)。

    - sign(0) 定音: 不一致 := sign_a ≠ sign_b, **0 与 ±1 记不一致、
      0 与 0 记一致** (finbert2 重归一后 0.5/0.5 真实可达); near-zero 符号
      翻转噪声属标签基测度固有, 刻意不设 deadband (计划 §6#12)。
    - 逐篇可用模型 < 2 → 双列该行 NaN; 某轨可用模型列 < 2 → 该轨双列不产
      (合法缺席)。2-模型 vs 3-模型逐篇口径混合 (全局缺席或 infer_failed)
      属已记账测量特征 (codebook notes)。
    - z 与跨模型 SD 均 **ddof=1**; z 参数 = 本次 run 文章宇宙按 模型×轨
      (σ=0 或全 NaN 的模型退出该轨 disp)。
    """
    out: dict = {}
    for trk in TRACKS:
        nts = {}
        for b in models:
            p_col, n_col, _ = _prob_cols(b, trk)
            if p_col in df.columns and n_col in df.columns:
                nts[b] = (pd.to_numeric(df[p_col], errors='coerce')
                          - pd.to_numeric(df[n_col], errors='coerce'))
        if len(nts) < 2:
            continue  # 该轨不足两模型 → 双列不产
        nt_frame = pd.DataFrame(nts, index=df.index)

        # --- canonical: sign 两两不一致对占比 ---
        signs = np.sign(nt_frame)
        cols = list(signs.columns)
        n_pairs = pd.Series(0.0, index=df.index)
        n_dis = pd.Series(0.0, index=df.index)
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                si, sj = signs[cols[i]], signs[cols[j]]
                valid = si.notna() & sj.notna()
                n_pairs += valid.astype(float)
                n_dis += ((si != sj) & valid).astype(float)
        lblhet = n_dis / n_pairs.replace(0, np.nan)  # <2 可用模型 (0 对) → NaN
        out[f'_lblhet_art{trk}'] = lblhet

        # --- 稳健轨: z 标准化跨模型样本 SD (ddof=1) ---
        zcols = {}
        for b, nt in nt_frame.items():
            mu = nt.mean()
            sd = nt.std(ddof=1)
            if pd.notna(sd) and sd > 0:
                zcols[b] = (nt - mu) / sd
        if len(zcols) >= 2:
            zframe = pd.DataFrame(zcols, index=df.index)
            out[f'_xmd_art{trk}'] = zframe.std(axis=1, ddof=1)  # 非缺 <2 → NaN
    return out


# ---------------------------------------------------------------------------
# WP-E: 年内时序 (bank-year 级独立 frame, runner merge)
# ---------------------------------------------------------------------------

def _intrayear_col_names(models):
    cols = []
    for trk in TRACKS:
        for b in models:
            cols.append(f'{b}_nt_iyvol{trk}')
            cols.append(f'{b}_nt_iytrend{trk}')
    return cols


def compute_intrayear_dynamics(df: pd.DataFrame, models) -> pd.DataFrame:
    """年内噪声校正波动 iyvol + 闭式月度趋势 iytrend, 18+2 列 (含键)。

    iyvol = √max(0, Var₁(m_t) − (1/T)·Σ_t σ̂²/n_t):
      Var₁ = 月均值样本方差 (ddof=1); 有效月 = ≥1 篇非 NaN 净语调 (含单篇
      月), T = 有效月数; σ̂² = 池化文章级方差 Σ_{n_t≥2}(n_t−1)s²_t /
      Σ_{n_t≥2}(n_t−1) (s²_t ddof=1, 池化假设月间方差同质); 校正项对
      **全部**有效月 (含 n_t=1, 其噪声最大恰最须校正) 求和。门槛:
      T ≥ IYVOL_MIN_MONTHS **且** ≥1 月 n_t≥2 (否则 σ̂² 不可估 → NaN,
      宁缺勿噪)。无偏性仅指开方/max(0,·) 截断前的方差差 (双 ddof=1 下
      E[Var₁(m_t)] = Var₁(μ_t) + (1/T)Σσ²/n_t 对逐月异质 n_t/σ²_t 成立)。
      白话: 直接算月均值的波动会把"报道少的月份均值本身不准"当成真波动,
      低覆盖银行机械虚高 — 先扣掉这部分抽样噪声再开方。
    iytrend = 月均值对实际月号 x∈{1..12} 的闭式 OLS 斜率
      Σ(x−x̄)(m−m̄)/Σ(x−x̄)², 有效月 ≥ IYTREND_MIN_MONTHS; 分母 > 0 由
      月号互异 + 门槛 6 结构保证 (勿加多余守卫); **禁 lstsq/polyfit**
      (LAPACK 破确定性口径, 先例 abnormal_tone 的 _KNOWN_BLAS_RE 问题族)。

    schema 合同: **0 行输入也返回含 target_bank/year + 全部 18 指标列
    (float64) 的 frame** (wire-ahead; 空 object 列会触发 export 崩溃先例);
    某 (model, track) 概率列缺席 → 该 2 列全 NaN 但**在位**。
    正交声明: vs tone_volatility(跨年 rolling) 真正交; vs {b}_pos_std 仅
    校正后近似正交。本 frame 由 runner 在 7h-net 之后 merge (how='left',
    先 pre-drop 既存同名列防 _x/_y), 时序在 balance_panel 零填之后 →
    结构上不经 zero-fill, 无新闻格天然 NaN。
    """
    metric_cols = _intrayear_col_names(models)
    empty = pd.DataFrame({
        'target_bank': pd.Series(dtype=object),
        'year': pd.Series(dtype='int64'),
        **{c: pd.Series(dtype='float64') for c in metric_cols},
    })
    if df is None or len(df) == 0:
        return empty
    if 'target_bank' not in df.columns or 'year' not in df.columns or '日期' not in df.columns:
        return empty

    month = pd.to_datetime(df['日期'], errors='coerce').dt.month
    pieces = []
    for trk in TRACKS:
        for b in models:
            p_col, n_col, _ = _prob_cols(b, trk)
            iyvol_col = f'{b}_nt_iyvol{trk}'
            trend_col = f'{b}_nt_iytrend{trk}'
            if p_col not in df.columns or n_col not in df.columns:
                continue  # 合法缺席 → 该 2 列由最终 reindex 补全 NaN
            nt = (pd.to_numeric(df[p_col], errors='coerce')
                  - pd.to_numeric(df[n_col], errors='coerce'))
            tmp = pd.DataFrame({
                'target_bank': df['target_bank'], 'year': df['year'],
                'month': month, 'nt': nt,
            }).dropna(subset=['month', 'nt'])
            if len(tmp) == 0:
                continue
            monthly = (tmp.groupby(['target_bank', 'year', 'month'])['nt']
                       .agg(['mean', 'count', 'var']).reset_index())  # var: ddof=1, n=1→NaN
            monthly['w'] = np.where(monthly['count'] >= 2, monthly['count'] - 1, 0.0)
            monthly['ws2'] = np.where(monthly['count'] >= 2,
                                      monthly['w'] * monthly['var'].fillna(0.0), 0.0)
            monthly['invn'] = 1.0 / monthly['count']
            monthly['x'] = monthly['month'].astype(float)
            monthly['xm'] = monthly['x'] * monthly['mean']
            monthly['x2'] = monthly['x'] ** 2
            g = monthly.groupby(['target_bank', 'year'])
            stats = g.agg(
                T=('mean', 'count'), var1_m=('mean', 'var'),
                w_sum=('w', 'sum'), ws2_sum=('ws2', 'sum'),
                invn_sum=('invn', 'sum'),
                sx=('x', 'sum'), sm=('mean', 'sum'),
                sxm=('xm', 'sum'), sx2=('x2', 'sum'),
            )
            sigma2 = stats['ws2_sum'] / stats['w_sum'].replace(0, np.nan)
            correction = sigma2 * stats['invn_sum'] / stats['T']
            iyvol = np.sqrt(np.maximum(0.0, stats['var1_m'] - correction))
            iyvol[(stats['T'] < IYVOL_MIN_MONTHS) | stats['var1_m'].isna()
                  | sigma2.isna()] = np.nan
            sxx = stats['sx2'] - stats['sx'] ** 2 / stats['T']
            sxy = stats['sxm'] - stats['sx'] * stats['sm'] / stats['T']
            trend = sxy / sxx  # 分母>0 由月号互异+门槛 6 结构保证
            trend[stats['T'] < IYTREND_MIN_MONTHS] = np.nan
            pieces.append(pd.DataFrame({iyvol_col: iyvol.astype('float64'),
                                        trend_col: trend.astype('float64')}))
    if not pieces:
        return empty
    result = pd.concat(pieces, axis=1)
    result = result.reindex(columns=metric_cols)  # 缺席 (model,track) 补全 NaN 列
    result = result.astype('float64').reset_index()
    return result
