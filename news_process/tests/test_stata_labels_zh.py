"""test_stata_labels_zh — WP3 标签中文化 gate (STATA_VARATTR 计划 §3a, 2026-07-10).

五道闸 (计划 §3a WP3 行):
    ① 51 宇宙全列 (复算 stage-46 rename 链后经 build_variable_labels) 逐列
       label 含 ≥1 CJK 汉字 — **零豁免** (structural 列 target_bank/year 已按
       提案给中文, 不留白名单);
    ② 全列 label ≤80 UTF-8 字节且零截断 (无 '...' 尾巴 — 截断即意味源头标签
       超预算, 须改写短名而非机械截);
    ③ config/stata_labels_zh.json 键 ⊆ 51 面板列集 (防幻影键);
    ④ codebook「标签」字段与 stata 46-path 同列逐字同源 (meta 两端共享 +
       HEURISTIC/兜底两域经 get_shared_zh_labels 单一 SSOT);
    ⑤ zh JSON 文件缺失 → 优雅回退 (行为与旧四级链一致: 兜底列退列名, 不抛)。
    ⑥ (P1 整改 2026-07-11) 51 dta 真实写路径 (controls.build_stage51_variable_labels)
       终态标签逐列 CJK — 封死「五道闸只模拟 46-path, 51 overlay 分叉假绿」盲区。

字节口径 = UTF-8 (与 validate_stata_compat 一致); CJK 判定 = 基本区 + 扩展 A
(\\u4e00-\\u9fff, \\u3400-\\u4dbf; 与计划 §1 汉字计数口径一致, \\u 转义防 GBK 崩)。
"""
from __future__ import annotations

import json
import os
import re

import pandas as pd
import pytest

from news_process.pipeline.panel import codebook as cb
from news_process.pipeline.panel import stata_export as se

# P2 整改 (2026-07-11): 端点字符改真 \u 转义 (原为字面 CJK 端点字符, 与 docstring
# 自述矛盾; U+9FFF/U+3400/U+4DBF 不在 GBK 码表, 断言失败回显可在 GBK 控制台二次崩)
_CJK_RE = re.compile('[\u4e00-\u9fff\u3400-\u4dbf]')
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
_PANEL_51 = os.path.join(_REPO, 'data', 'processed', '51_panel_with_controls.parquet')
_ZH_JSON = os.path.join(_REPO, 'config', 'stata_labels_zh.json')


def _panel_columns() -> list:
    if not os.path.exists(_PANEL_51):
        pytest.skip('51_panel_with_controls.parquet 不在盘上 (fresh clone)')
    import pyarrow.parquet as pq
    return list(pq.read_schema(_PANEL_51).names)


def _labels_via_stage46_rename_chain(cols: list):
    """镜像 stage-46 写路径: shorten → asciify → 链式压平 rename_map → labels."""
    df = pd.DataFrame(columns=cols)
    df1, m1 = se.shorten_long_column_names(df)
    df2, m2 = se.asciify_non_ascii_columns(df1)
    rename_map = dict(m1)
    rename_map.update(m2)

    def _chase(name, _seen=None):
        seen = set()
        while name in rename_map and name not in seen:
            seen.add(name)
            name = rename_map[name]
        return name

    rename_map = {k: _chase(v) for k, v in rename_map.items()}
    labels = se.build_variable_labels(df2, rename_map)
    return df2, rename_map, labels


class TestCjkAndTruncationGates:
    def test_gate1_all_labels_contain_cjk_no_exemption(self):
        cols = _panel_columns()
        _, _, labels = _labels_via_stage46_rename_chain(cols)
        assert len(labels) == len(cols)
        no_cjk = [(c, labels[c]) for c in labels if not _CJK_RE.search(labels[c])]
        assert not no_cjk, (
            f'{len(no_cjk)} 列标签无汉字 (零豁免口径), 例: {no_cjk[:10]}')

    def test_gate2_all_labels_within_80_bytes_zero_truncation(self):
        cols = _panel_columns()
        _, _, labels = _labels_via_stage46_rename_chain(cols)
        overlong = [(c, len(v.encode('utf-8'))) for c, v in labels.items()
                    if len(v.encode('utf-8')) > 80]
        assert not overlong, f'标签超 80 UTF-8 字节: {overlong[:10]}'
        truncated = [(c, v) for c, v in labels.items() if v.endswith('...')]
        assert not truncated, (
            f'{len(truncated)} 列标签被机械截断 (源头须改写短标签): {truncated[:10]}')

    def test_gate2b_validate_stata_compat_accepts(self):
        """validate_stata_compat 全列过闸 (列名合法性 + label 字节, 端到端兼容)."""
        cols = _panel_columns()
        df2, _, labels = _labels_via_stage46_rename_chain(cols)
        se.validate_stata_compat(df2, labels)  # 不抛即过


class TestZhJsonHygiene:
    def test_gate3_zh_json_keys_subset_of_panel(self):
        cols = set(_panel_columns())
        with open(_ZH_JSON, encoding='utf-8') as f:
            zh = json.load(f)
        phantom = sorted(set(zh) - cols)
        assert not phantom, f'zh JSON 幻影键 (不在 51 面板): {phantom[:20]}'

    def test_zh_json_values_cjk_and_bytes(self):
        with open(_ZH_JSON, encoding='utf-8') as f:
            zh = json.load(f)
        assert len(zh) > 2000, '兜底列中文标签数据层意外缩水'
        bad = [k for k, v in zh.items()
               if not _CJK_RE.search(v) or len(v.encode('utf-8')) > 80]
        assert not bad, f'zh JSON 值违反 CJK/80B 约束: {bad[:10]}'


class TestTwoEndsSameSource:
    def test_gate4_codebook_label_equals_stata_label_full_universe(self):
        """④ 全量: codebook「标签」字段 == stata 46-path 标签 (逐列逐字).

        codebook 侧口径 = generate_codebook 循环的真实取标签路径
        (meta.to_dict()['标签'] / _infer_label 兜底, codebook.py:2261-2266);
        stata 侧 = build_variable_labels 以 panel 原名调用 (orig==col)。
        """
        cols = _panel_columns()
        stata_labels = se.build_variable_labels(pd.DataFrame(columns=cols))
        meta = cb.get_variable_metadata_dict()
        mismatch = []
        for c in cols:
            m = meta.get(c)
            cb_label = m.label if m is not None else cb._infer_label(c)
            if cb_label != stata_labels[c]:
                mismatch.append((c, cb_label, stata_labels[c]))
        assert not mismatch, (
            f'{len(mismatch)} 列 codebook 与 stata 标签分叉, 例: {mismatch[:8]}')

    def test_shared_zh_labels_priority_mirrors_chain(self):
        """get_shared_zh_labels 的 HEURISTIC > zh JSON 优先序与五级链 2>3 级一致."""
        shared = se.get_shared_zh_labels()
        heur = se.build_heuristic_labels({})
        # HEURISTIC 键在 shared 中必须以 HEURISTIC 值胜出 (meta 依赖键除外 —
        # F9 基名标签源含 meta, 传 {} 与生产 meta 结果可异, 故排除 F9 判据键)
        crit_sfx = ('_win1', '_sent')
        for k in list(heur)[:500]:
            if k.endswith(crit_sfx):
                continue
            assert shared.get(k) == heur[k], f'{k}: shared 未按 HEURISTIC 优先'


class TestStage51RealWritePath:
    """⑥ 新闸 (P1 整改 2026-07-11): 51 dta **真实写路径** 终态标签逐列 CJK.

    背景: 旧五道闸全部只模拟 46-path builder (se.build_variable_labels), 而
    51 dta 真实写路径是 controls.py::export_results → build_stage51_variable_labels
    → to_stata — 其英文 STATA_LABELS_41 overlay 曾覆盖中文共享标签, 且 5 个
    51-only 列 (含 fintech_share) 不在 46 labels.do 宇宙 → 终态永久英文, 五道闸
    全绿的同时真实写路径假绿。本闸走与生产完全相同的构建函数封死盲区。
    三条真实写路径终态覆盖: 40/46 = gate①(labels.do 源=build_variable_labels,
    40 列宇宙 ⊆ 51 宇宙) + 40-path 兜底已随 latin-1 守卫移除透传中文; 51 = 本闸。
    """

    def test_gate6_stage51_write_path_labels_cjk_within_budget(self):
        cols = _panel_columns()
        from news_process.papers._common.tables import sanitize_stata_columns
        from news_process.pipeline.falsification.controls import (
            build_stage51_variable_labels,
        )
        sanitized = sanitize_stata_columns(cols, max_len=32)
        labels = build_stage51_variable_labels(sanitized, cols)
        assert set(labels) >= set(sanitized)
        no_cjk = [(c, labels[c]) for c in sanitized if not _CJK_RE.search(labels[c])]
        assert not no_cjk, (
            f'{len(no_cjk)} 列 51 真实写路径标签无汉字 (英文 overlay 回潮?), '
            f'例: {no_cjk[:10]}')
        overlong = [(c, len(labels[c].encode('utf-8'))) for c in sanitized
                    if len(labels[c].encode('utf-8')) > 80]
        assert not overlong, f'51 写路径标签超 80 UTF-8 字节: {overlong[:10]}'

    def test_stage51_five_only_cols_get_zh_labels(self):
        """5 个 51-only 列 (不在 46 labels.do 宇宙, 无终态救回通道) 逐列锁中文."""
        from news_process.pipeline.falsification.controls import (
            build_stage51_variable_labels,
        )
        five = ['ln_ft_articles', 'ln_nf_articles', 'fintech_share',
                'zero_coverage', 'ft_n_articles_dedup']
        labels = build_stage51_variable_labels(five, five)
        with open(_ZH_JSON, encoding='utf-8') as f:
            zh = json.load(f)
        for c in five:
            assert _CJK_RE.search(labels[c]), f'{c}: 51-only 列标签仍英文 → 终态永久英文'
            if c in zh:
                assert labels[c] == zh[c], (
                    f'{c}: 51 写路径与 zh JSON 分叉 ({labels[c]!r} != {zh[c]!r})')

    def test_stage51_overlay_still_fills_bare_fallback(self, monkeypatch):
        """overlay 安全网职能保留: 中文层缺失时英文 STATA_LABELS_41 补位 (不退裸列名)."""
        from news_process.pipeline.falsification import controls as ctl
        monkeypatch.setattr(se, '_ZH_LABELS_CACHE', {})
        monkeypatch.setattr(se, '_SHARED_ZH_CACHE', None)
        try:
            labels = ctl.build_stage51_variable_labels(['zero_coverage'], ['zero_coverage'])
            assert labels['zero_coverage'] == ctl.STATA_LABELS_41['zero_coverage']
        finally:
            monkeypatch.undo()
            se._ZH_LABELS_CACHE = None
            se._SHARED_ZH_CACHE = None


class TestGracefulFallback:
    def test_gate5_missing_zh_json_behaves_like_legacy_chain(self, monkeypatch):
        """⑤ zh JSON 缺失 → load 返回 {} + 兜底列退列名 (与 WP3 前行为一致), 不抛."""
        monkeypatch.setattr(se, '_STATA_LABELS_ZH_PATH',
                            os.path.join(_REPO, 'config', '_no_such_labels.json'))
        monkeypatch.setattr(se, '_ZH_LABELS_CACHE', None)
        monkeypatch.setattr(se, '_SHARED_ZH_CACHE', None)
        try:
            assert se.load_stata_labels_zh() == {}
            # 兜底域列 (不在 meta/HEURISTIC): 文件缺失 → 退列名 (旧四级链行为)
            fake = 'zz_definitely_not_a_known_col_full'
            labels = se.build_variable_labels(pd.DataFrame(columns=[fake]))
            assert labels[fake] == fake
        finally:
            # 还原缓存 (monkeypatch 撤 attr 后首次调用重建真实缓存)
            monkeypatch.undo()
            se._ZH_LABELS_CACHE = None
            se._SHARED_ZH_CACHE = None

    def test_zh_json_layer_hits_fallback_domain_column(self):
        """正向对照: zh JSON 命中兜底域列 (washing_ratio ∈ 提案 fallback 域)."""
        labels = se.build_variable_labels(pd.DataFrame(columns=['washing_ratio']))
        assert labels['washing_ratio'] == '创新漂洗率(象征性正面占比)'
        # 裁决语义锁: 「洗稿」措辞 (抄袭歧义) 不得回潮
        with open(_ZH_JSON, encoding='utf-8') as f:
            zh = json.load(f)
        offenders = [k for k, v in zh.items() if '洗稿' in v]
        assert not offenders, f'「洗稿」措辞回潮: {offenders[:10]}'


if __name__ == '__main__':
    raise SystemExit(pytest.main([__file__, '-v']))
