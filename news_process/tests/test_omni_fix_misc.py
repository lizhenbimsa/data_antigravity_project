"""回归测试: omni-fix g-misc 组修复 (2026-06-11).

锁定以下修复行为 (权威裁决: scripts/audit/_omni_fix/g-misc.json):
- g-misc-01: export.py peer_fintech_exposure 段头注释 Berger 2022 误引清除
  (正确锚点 = LeSage-Pace 2009 + Leary-Roberts 2014, 与 network_spillover.py 勘误对齐)
- g-misc-02: difflib 名归一 cutoff 的 TNIC 误标清除 (export.py 注释 /
  llm_peer paper_spec.yaml / figures.py fig1 出版图轴标签)
- g-misc-03: 补齐回归锁缺口 — IDF 调用点 (tone_words.py:1302 content_full 接线)
  + JF Int8/t² 生产接线 (runner.py 步骤 7i) 源码级锁; W² 去对角生产函数级锁
- g-misc-04: ctx_materializer 主物化路径缺失标题 (np.nan/pd.NA/None) 不再注入
  字面 'nan' 前缀 / 不再 TypeError, 与旧 schema 分支 fillna('') 口径一致

注: g-misc-01/02 属引文/标注勘误 (注释与出版图标签), 用源码文本锁防 revert;
g-misc-03 的 JF 块内联于 runner.py 大函数 (他组核心文件, 本组只读不改),
同样用源码接线锁 + 既有运行时域守卫 (runner.py:1568 raise) 兜底。

# 白话: 杂项组修复锁: 标题缺失的文章不能把缺失值变成字面文字 "nan" 拼进正文;
# 两处把论文引错的注释/图轴标签已改正, 锁住不许改回去; 还有几个早先修过但
# 没上锁的点(IDF 语料接线、二阶网络去自反馈、JF 分歧指数防溢出)这次补上锁。
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

pytestmark = pytest.mark.fast

# news_process 包根 (源码文本锁用; 不 import 重模块, 避免模块级 load_config 副作用)
import news_process  # noqa: E402

_PKG = Path(news_process.__file__).parent


def _read_src(*rel_parts: str) -> str:
    return (_PKG.joinpath(*rel_parts)).read_text(encoding='utf-8')


# ════════════════════════════════════════════════════════════════════════
# g-misc-04: ctx_materializer 缺失标题处理
# ════════════════════════════════════════════════════════════════════════

class TestCtxMaterializerMissingTitle:
    """fix(omni-g-misc-04): 主物化路径 (无 content_ctx) 的标题缺失处理.

    旧行为: `str(row.get('标题', '') or '')` — np.nan (truthy float) 漏网 →
    str() 成字面 'nan' 静默注入两轨; pd.NA 在 `or` 布尔语境 TypeError 崩溃。
    新行为: 显式 pd.isna 判缺 → 空标题, 与 L98 旧 schema 路径 fillna('') 一致。
    """

    @staticmethod
    def _make_df(titles):
        bodies = [f'银行公告正文第{i}句。' for i in range(len(titles))]
        return pd.DataFrame({
            '内容': bodies,
            '标题': pd.Series(titles, dtype='object'),
            'target_bank': [''] * len(titles),  # 空 target → 跳过实体窗口/alias 查找
        })

    def test_nan_title_no_literal_nan_prefix(self):
        from news_process.pipeline.text.ctx_materializer import materialize_content_ctx
        df = self._make_df([np.nan])
        out = materialize_content_ctx(df)
        body = df['内容'].iloc[0]
        # 旧 bug: content_full == 'nan。' + body
        assert out['content_full'].iloc[0] == body, \
            f"np.nan 标题应按空标题处理, 实际: {out['content_full'].iloc[0]!r}"
        assert out['content_ctx'].iloc[0] == body
        assert not out['content_full'].iloc[0].startswith('nan')

    def test_pd_na_title_does_not_raise(self):
        from news_process.pipeline.text.ctx_materializer import materialize_content_ctx
        df = self._make_df([pd.NA])
        out = materialize_content_ctx(df)  # 旧 bug: `pd.NA or ''` → TypeError
        body = df['内容'].iloc[0]
        assert out['content_full'].iloc[0] == body
        assert out['content_ctx'].iloc[0] == body

    def test_none_and_empty_title_unchanged(self):
        from news_process.pipeline.text.ctx_materializer import materialize_content_ctx
        df = self._make_df([None, ''])
        out = materialize_content_ctx(df)
        for i in range(2):
            assert out['content_full'].iloc[i] == df['内容'].iloc[i]

    def test_real_title_still_prepended(self):
        """防过度修正: 正常标题仍须注入两轨前缀."""
        from news_process.pipeline.text.ctx_materializer import materialize_content_ctx
        df = self._make_df(['某银行数字化转型'])
        out = materialize_content_ctx(df)
        body = df['内容'].iloc[0]
        assert out['content_full'].iloc[0] == f'某银行数字化转型。{body}'
        assert out['content_ctx'].iloc[0] == f'某银行数字化转型。{body}'


# ════════════════════════════════════════════════════════════════════════
# g-misc-01: export.py Berger 2022 误引清除 (源码文本锁)
# ════════════════════════════════════════════════════════════════════════

class TestExportPeerFintechCitation:
    """fix(omni-g-misc-01): peer_fintech_exposure_lag1 标签段头不再引 Berger 2022."""

    def test_no_berger_misattribution_in_export(self):
        src = _read_src('pipeline', 'panel', 'export.py')
        # 旧段头 '=== 同行金融科技溢出 (Berger et al. 2022) ===' 必须消失
        assert '溢出 (Berger' not in src, \
            "export.py 段头不应再以 Berger 2022 作锚点 (正确 = LeSage-Pace/Leary-Roberts)"
        # Berger 仅允许出现在勘误说明语境 (与 network_spillover.py:309 同口径),
        # 不允许再以肯定语气作引文锚点
        for line in src.splitlines():
            if 'Berger' in line:
                assert '误引' in line, \
                    f'export.py 中 Berger 只能在勘误语境出现, 违例行: {line.strip()!r}'

    def test_correct_anchor_near_peer_fintech_label(self):
        src = _read_src('pipeline', 'panel', 'export.py')
        i_label = src.find("'peer_fintech_exposure_lag1'")
        assert i_label > 0, 'peer_fintech_exposure_lag1 标签应仍在 export.py'
        window = src[max(0, i_label - 600):i_label]
        assert 'LeSage' in window and 'Leary' in window, \
            'peer_fintech_exposure_lag1 段头应锚定 LeSage & Pace 2009 + Leary & Roberts 2014'


# ════════════════════════════════════════════════════════════════════════
# g-misc-02: difflib cutoff 的 TNIC 误标清除 (3 处残留)
# ════════════════════════════════════════════════════════════════════════

class TestDifflibCutoffNotMislabeledTnic:
    """fix(omni-g-misc-02): difflib 名归一 cutoff ≠ TNIC 相似度阈值 (3 处残留勘误)."""

    def test_export_comment_no_tnic_standard_claim(self):
        src = _read_src('pipeline', 'panel', 'export.py')
        assert 'TNIC 标准' not in src, \
            "export.py 不应再把 difflib cutoff=0.80 标注为 'TNIC 标准'"

    def test_paper_spec_no_tnic_cutoff_claim(self):
        text = _read_src('papers', 'llm_peer', 'paper_spec.yaml')
        assert 'TNIC cutoff' not in text, \
            'paper_spec.yaml fallback IV 注释不应标 TNIC cutoff (是 difflib 名归一严格度)'

    def test_fig1_xlabel_not_tnic(self):
        """figures.py:41 原 set_xlabel('TNIC similarity cutoff $c$') 直接印入出版图
        fig1 (非注释级) — 锁定改为 name-matching 口径."""
        src = _read_src('papers', 'llm_peer', 'figures.py')
        assert 'TNIC similarity cutoff' not in src
        assert re.search(r"set_xlabel\('Peer name-matching cutoff \$c\$'\)", src), \
            'fig1 x 轴标签应为 difflib 名归一口径 (Peer name-matching cutoff)'

    def test_llm_peer_iv_erratum_still_in_place(self):
        """防连带 revert: llm_peer_iv.py 的原勘误注释 (L692/L755) 仍在位."""
        src = _read_src('pipeline', 'panel', 'llm_peer_iv.py')
        assert 'difflib.get_close_matches' in src
        assert '命名勘误' in src


# ════════════════════════════════════════════════════════════════════════
# g-misc-03: 回归锁缺口补齐
# ════════════════════════════════════════════════════════════════════════

class TestIdfCallPointWiring:
    """g-misc-03 缺口 1: IDF 修复此前仅锁 build_idf_weights 机制, 未锁调用点
    (tone_words.py:1302) — golden-deferred 期一旦 revert 为裸 '内容' 无测试报警。
    源码接线锁: IDF 语料须与 TF 语料同源 (content_full 优先, Gentzkow-Kelly-Taddy
    2019 JEL §2.2 同语料要求)。"""

    def test_idf_text_col_prefers_content_full(self):
        src = _read_src('pipeline', 'sentiment', 'tone_words.py')
        assert re.search(
            r"_idf_text_col\s*=\s*'content_full'\s+if\s+'content_full'\s+in\s+"
            r"df\.columns\s+else\s+'内容'", src), \
            'tone_words.py IDF 调用点必须优先取 content_full (与 TF 打分语料同源)'

    def test_build_idf_weights_call_passes_text_col(self):
        src = _read_src('pipeline', 'sentiment', 'tone_words.py')
        assert re.search(
            r"build_idf_weights\(\s*df,\s*ALL_DICTIONARIES,\s*text_col=_idf_text_col\s*\)",
            src), \
            'build_idf_weights 调用必须传 text_col=_idf_text_col (防 revert 回默认裸语料)'


class TestW2SelfFeedbackProductionLock:
    """g-misc-03 缺口 2a: 旧 test_w2_diagonal_zeroed 是纯 numpy demo 不调生产。
    本测试调生产 compute_network_spillovers: 2 节点环网中, 任一银行的全部二阶
    路径 (A→B→A) 均回到自身 → 去对角后无非自二阶邻居 → peer_tone_2nd 必为 NaN。
    若 W² 自反馈 revert, peer_tone_2nd[A] 会等于 A 自身滞后 tone (0.7) — 可区分。"""

    def test_two_node_ring_second_order_is_nan(self):
        from news_process.pipeline.panel.network_spillover import (
            compute_network_spillovers,
        )
        tones = {'Abank': 0.7, 'Bbank': -0.3}
        rows = []
        for y in (2017, 2018):
            for b in ('Abank', 'Bbank'):
                rows.append({'target_bank': b, 'year': y,
                             'llm_vote_tone_full': tones[b] if y == 2017 else np.nan})
        panel = pd.DataFrame(rows)
        df_ex = pd.DataFrame([
            {'year': 2017, 'target_bank': 'Abank', 'co_mentioned_banks': 'Bbank'},
            {'year': 2017, 'target_bank': 'Bbank', 'co_mentioned_banks': 'Abank'},
        ])
        out = compute_network_spillovers(panel.copy(), df_ex)

        def get(bank, col):
            m = (out['target_bank'] == bank) & (out['year'] == 2018)
            return out.loc[m, col].iloc[0]

        # 一阶完好 (防过度断言): A 的唯一同行 B → peer_tone[A] = -0.3
        assert abs(get('Abank', 'peer_tone_lag1_full') - (-0.3)) < 1e-9
        # 二阶: 唯一 length-2 路径回自身, 去对角后必 NaN (自反馈 revert 则 = 0.7)
        v_a = get('Abank', 'peer_tone_2nd_lag1_full')
        assert pd.isna(v_a), \
            f'peer_tone_2nd[A]={v_a}: 非 NaN 说明 W² 对角自反馈回归 (Bramoullé 排他性破)'
        assert pd.isna(get('Bbank', 'peer_tone_2nd_lag1_full'))


class TestJfRunnerWiringLock:
    """g-misc-03 缺口 2b: 旧 JF 测试用本地 _jf 重实现 (demo) 不调生产。JF 块内联
    于 runner.py 大函数 (他组核心文件, 只读), 故用源码接线锁锁定三件套:
    Int8→float64 转换 + t² 分母 (n_articles_llm_valid) + [-1,1] 运行时域守卫。"""

    @staticmethod
    def _jf_block() -> str:
        src = _read_src('pipeline', 'panel', 'runner.py')
        i0 = src.find('步骤 7i: Janis-Fadner')
        assert i0 > 0, 'runner.py 应仍含步骤 7i Janis-Fadner 块'
        i1 = src.find('情感意见分歧', i0)
        assert i1 > i0, 'JF 块终点锚 (8b 情感意见分歧) 未找到'
        return src[i0:i1]

    def test_jf_uses_float64_counts(self):
        block = self._jf_block()
        # fix(jf-int8): Int8 算术下 (P+N)**2 静默回绕 → 必须先 astype float64
        assert block.count(".astype('float64')") >= 2, \
            'JF 块的 P/N 计数必须先转 float64 (防 Int8 回绕越界)'

    def test_jf_denominator_uses_valid_count_t_squared(self):
        block = self._jf_block()
        # fix(jf-denominator): canonical Janis-Fadner 分母 = t² (t = 正+负+中性有效数)
        assert 'n_articles_llm_valid' in block, \
            'JF 分母须用 n_articles_llm_valid (t², 含中性), 非 (P+N)²'

    def test_jf_runtime_domain_guard_present(self):
        block = self._jf_block()
        assert 'between(-1.0, 1.0)' in block and 'raise ValueError' in block, \
            'JF [-1,1] 理论域运行时守卫 (越界即 raise) 不得移除'
