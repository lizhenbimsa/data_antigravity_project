"""tests/test_balanced_media_family_registry.py — BAL 平衡媒体稳健性族 gate。

**事故 (2026-07-29 入口⑧⑨ 生产真跑)**: 两条银企共现管道的步骤 01 registry 在
生产 T=19 面板上**当场崩**:

    40 面板残差 741 列无判定 (穷尽性断言失败): bal_w0725_tone_full ...
    步骤 01 失败 (exit=1, 墙钟 0.9102s) — fail-loud 中断, 后续步骤未跑

根因是一类**T=2 → 生产规模的漏网**, 与超时表同型:
`attention_media.py::compute_balanced_media_robustness` 在平衡子集为空时 `continue`,
而盘上 T=2 dev **无任何媒体满足窗口内逐年覆盖** ⟹ 该族列从未落地过, v23 权威负清单
(按 T=2 面板干跑定稿, CUT 410 / KEEP 294) 因此从未见过它们。2026-07-27/28 生产 T=19
面板跑通后 741 列首次出现 → 穷尽性断言 (每列须 ∈ 纳入源列 ∪ 排除域) 无判据可用。
源码 `attention_media.py:237` 早已预言: "(latent: 盘上 T=2 无满足者, T=19 全量触发)"。

**处置 (2026-07-29 用户裁定)**: 738 个测度列**全部纳入**; 另 3 个 `n_media_bal_*`
的零变异缺陷在上游根治 —— 旧实现 `panel[col_n] = len(balanced)` 把语料级标量广播到
全部 23,693 行 (实测 nunique==1, 与常数项完全共线), 改为逐 bank-year 计数。

本 gate 锁五件事:
  ① 基名**从盘上列集派生**而非硬编码 (词典×规则消融网格是数据驱动的 82 底层基名 × 3 窗口);
  ② 面板无该族时返回空列表而**不 fail** —— 小样本下列不落地是**预期**行为;
  ③ 短名压缩后满足 D16 预算 (发射列 "cw_"+short+"_full" ≤ 32 ⟹ short ≤ 24) 且零碰撞;
  ④ 短名替换串**不误伤非 BAL 基名** (str.replace 无锚定, 会作用于所有需缩名的基名);
  ⑤ `n_media_bal_*` 必须逐 bank-year 有变异, 不得退回广播常量。

⚠ 已知不对称 (待裁定, 本 gate 只记录不断言): 同源孪生族 `exc_*` (停刊稳健性,
**完全相同的 82 个底层基名** × 3 轨 = 246 列, 非空率 25.42% vs bal 的 10.97%)
仍被 EXCLUDE_RULES ① `^exc_` 判为 D15_1_PEER 排除。另注该理由码本身错配:
D15_1_PEER 名为"他行/同组测度", 而此处 `exc` 实指"剔除停刊媒体"非"剔除同业银行"。
"""
from __future__ import annotations

import importlib.util
import os
import sys

import pandas as pd
import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_NP = os.path.dirname(_HERE)
_PROJECT_PARENT = os.path.dirname(_NP)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

_REGISTRIES = {
    'listed': os.path.join(_NP, 'company_listed_bank',
                           '01_build_company_bank_cooc_registry.py'),
    'tax': os.path.join(_NP, 'company_tax_bank',
                        '01_build_company_tax_bank_cooc_registry.py'),
}


def _load(which):
    """按路径加载 registry 模块 (文件名以数字开头, 不能常规 import)。"""
    path = _REGISTRIES[which]
    if not os.path.exists(path):
        pytest.skip(f'{which} registry 不在盘上: {path}')
    spec = importlib.util.spec_from_file_location(f'_reg_{which}', path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


#: 生产面板实测形态 (82 底层基名 × 3 窗口 × 3 轨 = 738 + 3 计数列)
_SAMPLE_COLS = {
    'bal_w0725_tone_full', 'bal_w0725_tone_ctx', 'bal_w0725_tone_ss',
    'bal_w1025_jiang_2021_score_advonly_full',
    'bal_w1125_loughran_score_negdeg_ss',
    'bal_w0725_du_2022_score_polw00_ctx',
    'bal_w0725_fin_sent_zh_正面_hw_full',
    'n_media_bal_w0725', 'n_media_bal_w1025', 'n_media_bal_w1125',
    'target_bank', 'year', 'llm_vote_tone_full',   # 非 BAL 干扰项
}


@pytest.mark.parametrize('which', sorted(_REGISTRIES))
class TestRegistry:

    # ── ① 派生而非硬编码 ──
    def test_discovers_basenames_from_panel(self, which):
        m = _load(which)
        # 返回的是 (family, basename) 对 (与负清单 (fam, base) 同序), 故反转建索引
        got = {b: f for f, b in m.discover_balanced_basenames(_SAMPLE_COLS)}
        assert 'bal_w0725_tone' in got, '未从三轨列剥出测度基名'
        assert 'bal_w1025_jiang_2021_score_advonly' in got, '未剥出词典消融基名'
        assert 'n_media_bal_w0725' in got, '计数列未入册'
        assert all(v == m.BAL_FAMILY for v in got.values()), '族码不一致'
        assert 'llm_vote_tone_full' not in got, '误吞非 BAL 列'
        assert 'target_bank' not in got and 'year' not in got, '误吞键列'

    def test_track_suffix_stripped_not_duplicated(self, which):
        m = _load(which)
        bases = [b for _, b in m.discover_balanced_basenames(_SAMPLE_COLS)]
        assert len([b for b in bases if b.startswith('bal_w0725_tone')]) == 1, \
            '三轨列应折叠为 1 个基名 (full/ctx/ss 各出一个说明轨后缀没剥干净)'
        assert not any(b.endswith(('_full', '_ctx', '_ss')) for b in bases), \
            '基名仍带轨后缀'

    # ── ② 无该族时不 fail ──
    def test_empty_panel_returns_empty_not_error(self, which):
        m = _load(which)
        assert m.discover_balanced_basenames({'target_bank', 'year'}) == [], (
            '面板无 bal_w 列时应返回空列表 —— T=2 小样本下"无媒体满足逐年覆盖"是**预期**, '
            '不是缺陷, 不得 fail (否则 dev 环境永远跑不了 registry)。')

    # ── ③ 短名预算 + 零碰撞 ──
    def test_short_names_fit_d16_budget(self, which):
        m = _load(which)
        bases = [b for _, b in m.discover_balanced_basenames(_SAMPLE_COLS)]
        # 真实的 82 底层基名里最长的几个 (生产实测)
        bases += [f'bal_w{w}_{u}' for w in ('0725', '1025', '1125') for u in (
            'jiang_2021_score_advonly', 'jiang_2021_score_degonly',
            'bian_2021_score_negonly', 'loughran_score_advonly',
            'you_2018_score_negdeg', 'deepseekv4_score_hw', 'du_2022_score_polw00')]
        bad = []
        for b in bases:
            short = m.apply_short_name(b)
            longest = max(len(f'{arm}_{short}_{t}')
                          for arm in ('cw', 'ce') for t in m.TRACKS)
            if longest > 32:
                bad.append((b, short, longest))
        assert not bad, (
            'BAL 短名压缩后仍超 D16 的 32 字符预算:\n'
            + '\n'.join(f'  {b} -> {s} (发射列 {n} 字符)' for b, s, n in bad))

    def test_short_names_collision_free(self, which):
        m = _load(which)
        bases = [f'bal_w{w}_{u}' for w in ('0725', '1025', '1125') for u in (
            'tone', 'jiang_2021_score', 'jiang_2021_score_raw', 'jiang_2021_score_negonly',
            'yao_2021_score', 'bian_2021_score', 'du_2022_score', 'you_2018_score',
            'loughran_score', 'gpt54nano_score', 'gemini31_score', 'deepseekv4_score')]
        shorts = [m.apply_short_name(b) for b in bases]
        dup = {s for s in shorts if shorts.count(s) > 1}
        assert not dup, f'BAL 短名碰撞: {sorted(dup)} — 会触发 D16 全局唯一断言'

    # ── ④ 不误伤非 BAL 基名 ──
    def test_bal_replacements_do_not_touch_non_bal_basenames(self, which):
        """str.replace 无锚定 —— 必须确认 BAL 的替换串在非 BAL 基名域中零出现。"""
        m = _load(which)
        # 负清单里真实存在的 jiang/du/you 系基名 (均不含 "_score")
        untouched = [
            'jiang_2021_cater', 'jiang_2021_cater_b', 'disag_jiang_2021',
            'avg_jiang_2021_neg_ratio', 'llm_vote_tone_std', 'avg_subst_prob_score',
        ]
        changed = [(b, m.apply_short_name(b)) for b in untouched
                   if m.apply_short_name(b) != b]
        # 允许被**既有**规则改写, 但不得被本次新增的 BAL 规则改写
        bal_pairs = [(o, n) for o, n in m.SHORT_NAME_REPLACEMENTS
                     if o.startswith('bal_w') or o in
                     ('_2021_score', '_2022_score', '_2018_score', 'loughran_score')]
        assert bal_pairs, 'BAL 短名规则不在替换表里 — 修复被回退'
        for b in untouched:
            for old, _new in bal_pairs:
                assert old not in b, (
                    f'BAL 替换串 {old!r} 出现在非 BAL 基名 {b!r} 中 —— '
                    f'str.replace 无锚定会跨族误伤。当前实测改写: {changed}')

    def test_bal_family_in_tone_families(self, which):
        """BAL 入 TONE_FAMILIES: 仅 base 含 'tone' 的走 tone 值域闸, 词典分/计数落 none。"""
        m = _load(which)
        assert 'BAL' in m.TONE_FAMILIES, 'BAL 未入 TONE_FAMILIES — bal_w*_tone 会漏值域闸'
        assert m.range_gate_for('bal_w0725_tone', 'BAL') == 'tone'
        assert m.range_gate_for('bal_w0725_jiang_2021_score_raw', 'BAL') == 'none'
        assert m.range_gate_for('n_media_bal_w0725', 'BAL') == 'none'


# ── ⑤ 上游: n_media_bal_* 必须逐 bank-year 有变异 ──

def _toy_articles():
    """两家银行 × 三年 × 若干媒体; 媒体 A/B 逐年在刊 (平衡), C 只在一年 (非平衡)。"""
    rows = []
    for year in (2007, 2008, 2009):
        for media in ('A', 'B'):
            rows.append(('bank1', year, media, 0.5))
        rows.append(('bank2', year, 'A', -0.2))       # bank2 只被 A 报道
    rows.append(('bank2', 2008, 'C', 0.9))            # C 非平衡, 应被剔除
    return pd.DataFrame(rows, columns=['target_bank', 'year', '媒体(中文)',
                                       'llm_vote_score_full'])


def test_n_media_bal_varies_by_bank_year(monkeypatch):
    """回归用例: 旧实现 `panel[col_n] = len(balanced)` 全表只有 1 个取值。"""
    from news_process.pipeline.panel import attention_media as am
    monkeypatch.setattr(am, 'ROBUSTNESS_WINDOWS', [(2007, 2009, 'w0709')], raising=False)
    df = _toy_articles()
    panel = pd.DataFrame({
        'target_bank': ['bank1', 'bank1', 'bank1', 'bank2', 'bank2', 'bank2'],
        'year': [2007, 2008, 2009, 2007, 2008, 2009],
    })

    class _L:
        def __getattr__(self, _):
            return lambda *a, **k: None

    out = am.compute_balanced_media_robustness(df, panel, _L(), ['llm_vote_score_'])
    col = 'n_media_bal_w0709'
    assert col in out.columns, f'{col} 未落地'
    assert out[col].nunique(dropna=True) > 1, (
        f'{col} 全表只有 {out[col].nunique(dropna=True)} 个取值 —— 退回了'
        f'"语料级标量广播"的旧实现, 该列与常数项完全共线, 进任何回归都会被 omit。'
        f'实得: {out[col].tolist()}')
    # bank1 被 A、B 两家平衡媒体报道; bank2 只被 A 报道 (C 非平衡已剔)
    b1 = out.loc[out['target_bank'] == 'bank1', col].tolist()
    b2 = out.loc[out['target_bank'] == 'bank2', col].tolist()
    assert set(b1) == {2}, f'bank1 应为 2 家平衡媒体, 实得 {b1}'
    assert set(b2) == {1}, f'bank2 应为 1 家 (C 非平衡须剔除), 实得 {b2}'


def test_out_of_window_years_stay_nan(monkeypatch):
    """窗口外年份 = 不适用 → NaN; 窗口内无覆盖 = 0 (计数语义)。"""
    from news_process.pipeline.panel import attention_media as am
    monkeypatch.setattr(am, 'ROBUSTNESS_WINDOWS', [(2008, 2009, 'w0809')], raising=False)
    df = _toy_articles()
    panel = pd.DataFrame({
        'target_bank': ['bank1'] * 4,
        'year': [2006, 2007, 2008, 2009],     # 2006/2007 在窗口外
    })

    class _L:
        def __getattr__(self, _):
            return lambda *a, **k: None

    out = am.compute_balanced_media_robustness(df, panel, _L(), ['llm_vote_score_'])
    col = 'n_media_bal_w0809'
    oow = out.loc[out['year'].isin([2006, 2007]), col]
    assert oow.isna().all(), f'窗口外年份应为 NaN (不适用), 实得 {oow.tolist()}'
    inw = out.loc[out['year'].isin([2008, 2009]), col]
    assert inw.notna().all(), f'窗口内应有值 (无覆盖记 0), 实得 {inw.tolist()}'


def test_source_no_longer_broadcasts_scalar():
    import inspect

    from news_process.pipeline.panel import attention_media as am
    src = inspect.getsource(am.compute_balanced_media_robustness)
    # ⚠ 必须先剥注释: 修复处的注释里**逐字引用了旧代码**作为事故记录, 直接子串匹配
    #   会匹到自己的说明文字 (本 gate 初版即如此自伤)。
    code = '\n'.join(ln.split('#', 1)[0] for ln in src.splitlines())
    assert 'panel[col_n] = len(balanced)' not in code, (
        '零变异广播被回退 —— `panel[col_n] = len(balanced)` 把语料级标量写满全表。')
    assert "groupby(['target_bank', 'year'])['媒体(中文)']" in src, \
        'n_media_bal_* 不再逐 bank-year 计数'


def test_two_registries_share_identical_bal_block():
    """⑧⑨ 是镜像管道 —— BAL 块必须逐字节一致, 否则两条线会各自漂移。"""
    import re
    srcs = {}
    for which, path in _REGISTRIES.items():
        if not os.path.exists(path):
            pytest.skip(f'{which} registry 缺失')
        with open(path, encoding='utf-8') as f:
            txt = f.read()
        m = re.search(r'BAL_FAMILY = "BAL".*?return \[\(BAL_FAMILY, b\) for b in sorted\(bases\)\]',
                      txt, re.S)
        assert m, f'{which}: 找不到 BAL 发现函数块'
        srcs[which] = m.group(0)
    vals = list(srcs.values())
    assert vals[0] == vals[1], (
        '⑧⑨ 的 BAL 块已漂移 —— 两条镜像管道必须逐字节同源, '
        '否则同一面板在两侧得到不同的注册结果。')
