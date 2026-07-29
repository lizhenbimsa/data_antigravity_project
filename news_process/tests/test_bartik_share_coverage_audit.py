"""tests/test_bartik_share_coverage_audit.py — Bartik 份额检验的分层判据 gate。

**事故形态 (2026-07-29 入口⑥ 生产真跑)**: `81_stata_data_audit.py` 报 36 条 WARN,
其中 **14 条 (39%)** 是同一句「份额均值=0.06175偏低, 可能other类占比过高」——
而该诊断在数据上**不成立**:

    实测行和只有两个取值 {0.0, 1.0} (逐族 distinct=2, std≈0.40):
      · ==1.0 → 该 bank-year 在基期 (T0=2010) 在册, 份额**精确归一**,
                'other' 类实际未吃到任何质量;
      · ==0.0 → 该 bank-year 在基期**根本不存在** (1,247 家银行中只有 77 家
                在 2010 年在册; 2010 年零份额占比恰为 0.000000, 且**零家**银行
                出现"跨年时有时无") ⟹ 无份额可分配。

    低均值 100% 由后者占比驱动 (有新闻行里 80.03% 无基期覆盖), 与 'other' 类无关。

旧写法把两个总体混在一起取均值 ⟹ ① 报出错误的原因, 把后人引向一个不存在的
"other 类"问题; ② 真正该被看见的数 (基期覆盖率 —— 它决定 bartik IV 的有效样本)
反被那句错误解释盖住, 从未单独披露。

本 gate 锁三件事:
  ① 归一化判据只在**有基期份额**的行上取均值 (混合总体判据不得回归);
  ② 基期覆盖率**独立成项**披露, 不得再被折叠进归一化那条;
  ③ 「other 类占比过高」这句话只在它真正成立时出现 (有份额但均值 <0.5),
     不得在"整行无份额"的场合复用。

⚠ 附带事实 (勿据本文件反推数据有误): `bartik_*_iv` 在无基期覆盖行上输出的是
**NaN 而非 0** (实测 4,981/4,981 全 NaN, 0 行为 0) —— 回归会正确丢弃这些观测,
**不存在**"缺失被当成零暴露混进第一阶段"的问题。
"""
from __future__ import annotations

import inspect
import os
import sys

import numpy as np
import pandas as pd
import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.pipeline.audit import stata_audit as sa  # noqa: E402

_PREFIX = 'bartik_type'
_SHARES = [f'{_PREFIX}_share_a', f'{_PREFIX}_share_b', f'{_PREFIX}_share_c']


def _panel(n_covered, n_zero, covered_rowsum=1.0):
    """构造生产实测形态: covered 行份额和 = covered_rowsum, 其余行整行 0。"""
    rows = []
    for _ in range(n_covered):
        rows.append([covered_rowsum / 3.0] * 3)
    for _ in range(n_zero):
        rows.append([0.0, 0.0, 0.0])
    df = pd.DataFrame(rows, columns=_SHARES)
    n = len(df)
    df['target_bank'] = [f'b{i}' for i in range(n)]
    df['year'] = 2010 + np.arange(n) % 19
    return df


def _run(panel):
    """跑 IV 检验段, 收集 (check_name, status, detail)。

    `record` 是模块级函数写入模块级 `audit_results` 列表 —— 故本装置**清空并快照**
    该列表, 而不是注入桩 (注入桩会与被测代码的实际调用面脱节)。
    """
    assert hasattr(sa, 'audit_iv_variables'), \
        'audit_iv_variables 被重命名 — 请更新本 gate, 勿让它静默跳过'
    saved = list(sa.audit_results)
    sa.audit_results.clear()
    try:
        sa.audit_iv_variables(panel, '40面板')
        return [(r['check'], r['status'], r['detail']) for r in sa.audit_results]
    finally:
        sa.audit_results.clear()
        sa.audit_results.extend(saved)


# ── ① 归一化判据只在有基期份额的行上取均值 ──

def test_normalization_judged_on_covered_rows_only():
    """80% 行整行为 0、20% 行精确归一 → 归一化项必须 PASS, 不得因混合均值报 WARN。"""
    src = inspect.getsource(sa)
    assert 'covered = row_sums[row_sums > 0]' in src, (
        '归一化判据不再分层 —— 混合总体取均值会把"基期无覆盖"误报成'
        '"other 类占比过高" (2026-07-29 实测 14/36 条 WARN 属此类)。')
    assert 'covered.mean()' in src, '归一化均值未改在 covered 子集上取'


def test_zero_coverage_no_longer_blamed_on_other_category():
    """「other类占比过高」不得出现在"整行无份额"的分支里。"""
    src = inspect.getsource(sa)
    idx = src.find('other 类占比过高')
    assert idx > 0, '该措辞被整体删除 — 它在真正成立的场合仍应保留'
    window = src[max(0, idx - 700):idx]
    assert 'mean_cov < 0.5' in window, (
        '「other 类占比过高」不再由 mean_cov<0.5 守卫 —— 该措辞只在'
        '"有基期份额但导出类别不足半数质量"时成立, 不得在零覆盖场合复用。')


# ── ② 基期覆盖率独立成项 ──

def test_base_period_coverage_is_a_separate_check():
    src = inspect.getsource(sa)
    assert 'Bartik基期覆盖-' in src, (
        '基期覆盖率未独立成项 —— 它决定 bartik IV 的有效样本量, '
        '折叠进归一化那条会让它继续隐身 (旧版正是如此)。')
    assert 'zero_frac' in src, '未计算基期无份额行占比'


def test_coverage_check_reports_effective_sample():
    """覆盖率项必须报出有效样本量, 否则读者无从判断 IV 还剩多少可识别观测。"""
    src = inspect.getsource(sa)
    idx = src.find('Bartik基期覆盖-')
    seg = src[idx:idx + 900]
    assert 'len(covered)' in seg and 'len(row_sums)' in seg, \
        '覆盖率项未披露 有效样本/总行数'


# ── ③ 真实数据形态的端到端行为 ──

@pytest.mark.parametrize('n_cov,n_zero,expect_cov_status', [
    (200, 800, 'WARN'),   # 生产形态: 80% 无基期覆盖
    (900, 100, 'PASS'),   # 覆盖良好
])
def test_coverage_status_tracks_zero_fraction(n_cov, n_zero, expect_cov_status):
    got = _run(_panel(n_cov, n_zero))
    cov = [g for g in got if g[0].startswith('Bartik基期覆盖-')]
    assert cov, f'未产出基期覆盖项; 实得 {[g[0] for g in got]}'
    assert cov[0][1] == expect_cov_status, (
        f'zero_frac={n_zero/(n_cov+n_zero):.0%} 时覆盖项应为 {expect_cov_status}, '
        f'实得 {cov[0][1]} ({cov[0][2]})')


def test_perfectly_normalized_covered_rows_pass_despite_low_mixed_mean():
    """生产实测形态的核心回归用例: 混合均值 0.2 但 covered 行精确 =1.0 → 归一化 PASS。"""
    got = _run(_panel(200, 800))
    norm = [g for g in got if g[0].startswith('Bartik份额归一-')]
    assert norm, f'未产出归一化项; 实得 {[g[0] for g in got]}'
    assert norm[0][1] == 'PASS', (
        f'covered 行份额和精确为 1.0 却判 {norm[0][1]} ({norm[0][2]}) —— '
        '这正是旧版把 80% 零覆盖行拖进均值造成的误报。')


def test_genuine_other_category_shortfall_still_warns():
    """真的 other 占比过高 (covered 行只到 0.3) 必须仍报 WARN —— 不是把闸放松。"""
    got = _run(_panel(1000, 0, covered_rowsum=0.3))
    norm = [g for g in got if g[0].startswith('Bartik份额归一-')]
    assert norm and norm[0][1] == 'WARN', \
        f'covered 行均值 0.3 应报 WARN (other 类真的占比过高), 实得 {norm}'
    assert 'other' in norm[0][2], 'WARN 详情应指出 other 类'


def test_share_overflow_still_fails():
    """份额和 >1.01 (溢出) 仍必须 FAIL —— 分层重构不得削弱这条硬判据。"""
    got = _run(_panel(1000, 0, covered_rowsum=1.5))
    norm = [g for g in got if g[0].startswith('Bartik份额归一-')]
    assert norm and norm[0][1] == 'FAIL', f'份额溢出应 FAIL, 实得 {norm}'


def test_all_zero_family_fails_not_passes():
    """整族全零 = 基期份额未生成, 属真错误, 必须 FAIL 而非静默 PASS。"""
    got = _run(_panel(0, 1000))
    norm = [g for g in got if g[0].startswith('Bartik份额归一-')]
    assert norm and norm[0][1] == 'FAIL', \
        f'整族份额全为 0 应 FAIL (基期份额未生成/全丢失), 实得 {norm}'
