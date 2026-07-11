"""tests/test_omni_fix_stata_export.py — omni 审计修复组 g-stata-export 回归锁 (2026-06-11).

锁定 pipeline/panel/stata_export.py 的 15 条 finding 修复行为:
    01      计数列禁 Int8 (非 value-labeled int8/Int8 → Int16) + pyreadstat
            [101,126] extended-missing 损值安全网 (KNOWN-OPEN ⑥)
    02/08   variable label 按 UTF-8 字节边界截断 (CJK 标签不再『越截越长』)
    03/15   双后端差异 WARN 明示 + labels.do backend 指纹
    04/10/13 模块 docstring extended-missing 声称改与实现对齐 (诚实披露)
    04/11   encode_categorical_columns 未登记类别值 fail-loud (不再静默 NaN 合流)
    05/09   shorten/asciify 改名后 value_labels 键同步 + build_variable_labels
            经 rename_map 原名反查
    06      labels.do 标签 compound double quotes + \\$ \\` 转义
    07      [已退役 2026-06-21] core_patterns / assign_core_columns 整体移除
            (codebook 取消 is_core 核心/辅助区分, 全列均为分析列), 对应回归测试已删
    12      shorten used 集合预载全部列名 (截短名不抢占真实同名列)

全部测试用合成 DataFrame, 不依赖盘上大数据, 不调外部 API。

# 白话: 导出 .dta 给 Stata 用时有一堆格式陷阱, 这组测试守住: Stata 的 byte
# 类型只认 -127~100, 101~126 是它的"缺失值暗号", 计数列升级成 int16 免得
# 数值 126 被当成缺失; 中文标签按字节(不是字数)截到 80 字节内, 别越截越长;
# 列名超 32 字符要改短, 但不能撞了别的真实列的名字, 改名后标签/分组/取值
# 标签都要跟着新名字走; 没登记过的分类取值直接报错, 不许悄悄变成缺失。
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

from news_process.pipeline.panel import stata_export as se  # noqa: E402

_LOGGER_NAME = 'news_process.pipeline.panel.stata_export'


# ============================================================================
# omni-01: 计数列禁 Int8 + [101,126] byte 缺失码位安全网
# ============================================================================

def test_upcast_count_int8_to_int16():
    """非 value-labeled int8/Int8 计数列一律升 Int16 (主控裁决)."""
    df = pd.DataFrame({
        'tone_sum': pd.array([1, 100, None], dtype='Int8'),
        'pos_count': np.array([0, 50, 100], dtype='int8'),
        'f': [0.1, 0.2, 0.3],
    })
    out = se.upcast_unsafe_int8_columns(df, value_labels={})
    assert str(out['tone_sum'].dtype) == 'Int16'
    assert str(out['pos_count'].dtype) == 'int16'
    assert str(out['f'].dtype) == 'float64'  # 非 int8 列不动
    # 值逐位保真 (含 NA)
    assert out['tone_sum'].tolist()[:2] == [1, 100]
    assert pd.isna(out.loc[2, 'tone_sum'])


def test_upcast_keeps_value_labeled_byte():
    """value-labeled 0/1 编码列保持 Int8 (构造上 byte 安全)."""
    df = pd.DataFrame({'innovation_locus_full': pd.array([0, 1, None], dtype='Int8')})
    out = se.upcast_unsafe_int8_columns(df, value_labels={'innovation_locus_full': {0: 'a', 1: 'b'}})
    assert str(out['innovation_locus_full'].dtype) == 'Int8'


def test_upcast_value_labeled_out_of_range_defensive():
    """value-labeled 列值越出 [-127, 100] → 防御升型 (不静默损值)."""
    df = pd.DataFrame({'lab': pd.array([0, 120], dtype='Int8')})
    out = se.upcast_unsafe_int8_columns(df, value_labels={'lab': {0: 'a', 1: 'b'}})
    assert str(out['lab'].dtype) == 'Int16'
    assert out['lab'].tolist() == [0, 120]


def test_upcast_range_mode_for_pyreadstat_backend():
    """force_non_labeled=False (pyreadstat 写出前安全网): 仅按值域升型.

    Stata byte 合法值域 [-127, 100]; 101..127 是缺失码位 (`.` + .a-.z) —
    KNOWN-OPEN ⑥ 的损值场景。
    """
    safe = pd.DataFrame({'x': np.array([1, 100], dtype='int8')})
    out_safe = se.upcast_unsafe_int8_columns(safe, {}, force_non_labeled=False)
    assert str(out_safe['x'].dtype) == 'int8'  # max=100 合法上限, 不动

    hazard = pd.DataFrame({'x': np.array([1, 101], dtype='int8')})
    out_hazard = se.upcast_unsafe_int8_columns(hazard, {}, force_non_labeled=False)
    assert str(out_hazard['x'].dtype) == 'int16'  # 101 起即缺失码位 → 升型

    neg = pd.DataFrame({'x': np.array([-128, 0], dtype='int8')})
    out_neg = se.upcast_unsafe_int8_columns(neg, {}, force_non_labeled=False)
    assert str(out_neg['x'].dtype) == 'int16'  # -128 越下界 → 升型


def test_export_roundtrip_int8_count_value_preserved(tmp_path, monkeypatch):
    """端到端: Int8 计数列 (含 126 = byte 缺失码位区) 经 export 后值逐位保真."""
    panel = pd.DataFrame({
        'target_bank': ['工商银行', '建设银行'],
        'year': [2020, 2021],
        'gpt_tone_sum_full': pd.array([100, 126], dtype='Int8'),
    })
    panel_path = tmp_path / 'panel.parquet'
    panel.to_parquet(panel_path)
    monkeypatch.setattr(se, '_select_dta_backend',
                        lambda: ('pandas', se._write_dta_pandas_fallback))
    result = se.export_panel_to_stata(str(panel_path), str(tmp_path))
    back = pd.read_stata(result['full_dta'])
    assert back['gpt_tone_sum_full'].tolist() == [100, 126]
    # 升型后落盘为 int16 (不再是 byte) — 两后端在缺失码位区行为一致
    assert back['gpt_tone_sum_full'].dtype == np.int16


# ============================================================================
# omni-02/08: label 截断按 UTF-8 字节边界
# ============================================================================

def test_label_truncation_byte_safe_cjk_boundary_case():
    """81 字节 CJK 标签 (27 个汉字): 原实现『越截越长』(84 字节) → 修复后 ≤ 80."""
    cjk_col = '中' * 27  # 81 bytes > 80, 但 27 字符 < 77 → 旧逻辑切片不缩短反加 '...'
    df = pd.DataFrame({cjk_col: [1]})
    labels = se.build_variable_labels(df)
    label = labels[cjk_col]
    assert len(label.encode('utf-8')) <= se.STATA_VAR_LABEL_MAXLEN
    assert label.endswith('...')


def test_label_truncation_byte_safe_long_cjk():
    """108 字节中文标签: 截断点落多字节序列中间不抛 UnicodeDecodeError, 结果 ≤ 80 字节."""
    cjk_col = '银行年度面板媒体语调指标' * 3  # 36 字 = 108 bytes
    df = pd.DataFrame({cjk_col: [1]})
    labels = se.build_variable_labels(df)
    assert len(labels[cjk_col].encode('utf-8')) <= 80
    assert labels[cjk_col].endswith('...')


def test_truncated_label_passes_validate_gate():
    """截断与 validate_stata_compat 同口径 — 截断后必过字节门 (不再 stage 46 硬崩)."""
    df = pd.DataFrame({'x_col': [1]})
    # rename_map 让 fallback label = 超长中文原名 → 触发截断路径
    labels = se.build_variable_labels(df, rename_map={'x_col': '中' * 40})
    se.validate_stata_compat(df, labels)  # 不抛


# ============================================================================
# omni-06: labels.do compound quotes + $ ` 转义
# ============================================================================

def test_stata_string_literal_escapes():
    lit = se._stata_string_literal('say "hi" for $100 and `mac')
    assert lit.startswith('`"') and lit.endswith('"\'')
    assert r'\$100' in lit       # $ 转义防 global macro 展开
    assert r'\`mac' in lit       # ` 转义防 local macro / compound 嵌套
    assert '""' not in lit       # 不再用非法的 "" 加倍转义
    assert '"hi"' in lit         # compound 内嵌引号字面保留


def test_stata_string_literal_defuses_close_sequence():
    """标签含 \"' 闭合序列 → 插空格消解, 防 compound 串提前终结."""
    lit = se._stata_string_literal('a"\'b')
    inner = lit[2:-2]  # 掐头 `" 去尾 "'
    assert '"\'' not in inner


def test_labels_do_uses_compound_quotes(tmp_path):
    var_labels = {
        'col_a': 'plain label',
        'col_b': 'has "quotes" and $dollar',
    }
    out = tmp_path / 'labels.do'
    se.write_labels_do_file(str(out), var_labels, {})
    content = out.read_text(encoding='utf-8')
    assert 'capture label var col_a `"plain label"\'' in content
    # 旧实现产物 `"a""b"` (r198 非法语法被 capture 吞掉) 不得再出现
    assert '""' not in content
    assert r'\$dollar' in content
    # value label define 行仍在 (回归保护)
    assert 'label define locus_lbl' in content
    assert '底层技术 (Technology)' in content


def test_labels_do_backend_fingerprint(tmp_path):
    """omni-03/15: labels.do 头部带 backend 产物指纹."""
    out = tmp_path / 'labels.do'
    se.write_labels_do_file(str(out), {'c': 'lbl'}, {}, backend_name='pandas')
    content = out.read_text(encoding='utf-8')
    assert '* .dta writer backend: pandas' in content
    assert 'embedded value labels' in content  # fallback 差异明示
    # 不传 backend_name (向后兼容) → 无指纹行, 不抛
    out2 = tmp_path / 'labels2.do'
    se.write_labels_do_file(str(out2), {'c': 'lbl'}, {})
    assert 'writer backend' not in out2.read_text(encoding='utf-8')


# ============================================================================
# omni-12 + omni-09: shorten used 预载 + 同前缀前瞻碰撞
# ============================================================================

def test_shorten_no_identity_swap_with_existing_column():
    """截短名不得抢占 df 中靠后的真实同名列 (旧行为: 列身份静默交换)."""
    long_name = 'a_very_long_column_name_that_will_be_truncated_full'
    short_name = long_name[:se.STATA_VAR_NAME_MAXLEN]  # 恰为长列的裸截断名
    df = pd.DataFrame({long_name: [1], short_name: [2]})
    df_new, rename_map = se.shorten_long_column_names(df)
    # 真实列保住自己的名字 + 数据
    assert short_name in df_new.columns
    assert df_new[short_name].iloc[0] == 2
    # 长列让位: 拿 md5 后缀名, 反查映射正确
    new_long = [c for c in df_new.columns if c != short_name][0]
    assert new_long != short_name and len(new_long) <= 32
    assert rename_map[new_long] == long_name


def test_shorten_twin_prefix_both_get_discriminating_suffix():
    """omni-09: 32-char 前缀相同的双轨列 — 两列都拿 md5 后缀 (含先到的第一列).

    旧行为: 首列独占裸截断名 'innovation_collab_mode_confidenc' (track 不可辨),
    P-063 的 md5 方案只救了后到的第二列。
    """
    twins = ['innovation_collab_mode_confidence_full',
             'innovation_collab_mode_confidence_ctx']
    df = pd.DataFrame({twins[0]: [1], twins[1]: [2]})
    df_new, rename_map = se.shorten_long_column_names(df)
    bare_trunc = twins[0][:se.STATA_VAR_NAME_MAXLEN]
    assert bare_trunc not in df_new.columns          # 裸截断歧义名不复存在
    assert len(set(df_new.columns)) == 2             # 两列名互异
    for c in df_new.columns:
        assert len(c) <= 32
        assert rename_map[c] in twins                # 反查链完整


def test_shorten_car3day_template_convention():
    """模板组约定: car_3day_window_fintech_announcement → car_3day_window_ft_announce."""
    df = pd.DataFrame({'car_3day_window_fintech_announcement': [0.01]})
    df_new, rename_map = se.shorten_long_column_names(df)
    assert list(df_new.columns) == ['car_3day_window_ft_announce']
    assert rename_map['car_3day_window_ft_announce'] == 'car_3day_window_fintech_announcement'


def test_shorten_deterministic_across_calls():
    cols = {
        'innovation_collab_mode_confidence_full': [1],
        'innovation_collab_mode_confidence_ctx': [2],
        'car_3day_window_fintech_announcement': [3],
        'target_bank': ['工行'],
    }
    out1, _ = se.shorten_long_column_names(pd.DataFrame(cols))
    out2, _ = se.shorten_long_column_names(pd.DataFrame(cols))
    assert list(out1.columns) == list(out2.columns)


def test_shorten_short_names_unchanged():
    """≤32 字符列名不改 (回归保护, 现 panel 列名零漂移)."""
    df = pd.DataFrame({'target_bank': [1], 'llm_vote_tone_full': [2]})
    df_new, rename_map = se.shorten_long_column_names(df)
    assert list(df_new.columns) == ['target_bank', 'llm_vote_tone_full']
    assert rename_map == {}


# ============================================================================
# [omni-07 已退役 2026-06-21] core_patterns / assign_core_columns / STATA_IC_MAX_VARS
# 整体移除 (codebook 取消 is_core 核心/辅助区分) — 原 4 个 assign_core_columns 回归测试
# (test_core_contains_real_bartik_iv_names / test_core_phantom_bartik_name_retired /
#  test_core_missing_patterns_warn / test_assign_core_resolves_renamed_columns) 已删。
# ============================================================================
# omni-05/09: rename_map 元数据反查 (labels)
# ============================================================================

def test_build_labels_resolves_renamed_via_original_name():
    """HEURISTIC_LABELS 以原名为键 — 改名列经 rename_map 反查命中人工标签."""
    orig = 'innovation_collab_mode_confidence_full'
    df = pd.DataFrame({orig: [0.9]})
    df_new, rename_map = se.shorten_long_column_names(df)
    short = df_new.columns[0]
    labels = se.build_variable_labels(df_new, rename_map=rename_map)
    # WP3 (2026-07-10) 标签中文化后的 HEURISTIC 文案
    assert labels[short] == "协同模式分类置信度(原始LLM,全文轨)"


def test_build_labels_fallback_uses_original_name():
    """meta/HEURISTIC 均 miss 时 fallback 标签用原名 (保留被截断吃掉的判别后缀)."""
    orig = 'some_obscure_metric_with_a_really_long_name_full'
    df = pd.DataFrame({'some_obscure_metric_w_x1': [1]})
    labels = se.build_variable_labels(df, rename_map={'some_obscure_metric_w_x1': orig})
    assert labels['some_obscure_metric_w_x1'] == orig


def test_export_value_labels_synced_after_shorten(tmp_path, monkeypatch):
    """端到端: >32 字符 value-labeled 列改名后, labels.do apply 行引用短名 (不悬空)."""
    long_col = 'innovation_locus_extended_variant_full'  # 38 chars, 含 'innovation_locus'
    panel = pd.DataFrame({
        'target_bank': ['工商银行', '建设银行'],
        'year': [2020, 2021],
        long_col: ['底层技术', '应用场景'],
    })
    panel_path = tmp_path / 'panel.parquet'
    panel.to_parquet(panel_path)

    def fake_encode(df):
        df = df.copy()
        df[long_col] = df[long_col].map({'底层技术': 0, '应用场景': 1}).astype('Int8')
        return df, {long_col: dict(se.LOCUS_VALUE_LABELS)}

    monkeypatch.setattr(se, 'encode_categorical_columns', fake_encode)
    monkeypatch.setattr(se, '_select_dta_backend',
                        lambda: ('pandas', se._write_dta_pandas_fallback))
    result = se.export_panel_to_stata(str(panel_path), str(tmp_path))
    content = Path(result['labels_do']).read_text(encoding='utf-8')
    apply_lines = [ln for ln in content.splitlines() if 'label values' in ln and 'locus_lbl' in ln]
    assert apply_lines, "应有 locus value-label apply 行"
    assert long_col not in apply_lines[0], "apply 行不得引用已改名的悬空原名"
    short = long_col[:se.STATA_VAR_NAME_MAXLEN]
    assert short in apply_lines[0], f"apply 行应引用 shorten 后的短名 {short}"


# ============================================================================
# omni-04/11: encode 未登记类别 fail-loud
# ============================================================================

def test_encode_unmapped_category_raises():
    df = pd.DataFrame({'innovation_locus_full': ['底层技术', '不适用', '应用场景']})
    with pytest.raises(ValueError, match='未登记'):
        se.encode_categorical_columns(df)


def test_encode_valid_values_and_none_preserved():
    """合法类别 + None (真缺失) → 正常编码, NA 保留, 不抛."""
    df = pd.DataFrame({'innovation_locus_full': ['底层技术', None, '应用场景']})
    out, vlabels = se.encode_categorical_columns(df)
    assert out['innovation_locus_full'].tolist()[0] == 0
    assert pd.isna(out.loc[1, 'innovation_locus_full'])
    assert out['innovation_locus_full'].tolist()[2] == 1
    assert 'innovation_locus_full' in vlabels


# ============================================================================
# omni-04/10/13/14: docstring 诚实披露 (轻量锁, 防回退)
# ============================================================================

def test_module_docstring_no_longer_claims_extended_missing():
    doc = se.__doc__
    assert '未实现' in doc and 'missing_user_values' in doc, \
        "模块 docstring 须披露 extended missing .a/.b 未实现 (omni-04/10/13)"
    assert 'no-op' in doc, "模块 docstring 须披露类别编码器对当前 panel 为 no-op (omni-14)"


# ============================================================================
# omni-03/15: backend fallback WARN 明示差异
# ============================================================================

def test_select_backend_fallback_warns_value_label_gap(monkeypatch, caplog):
    import builtins
    orig_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == 'pyreadstat':
            raise ImportError('simulated missing pyreadstat')
        return orig_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, '__import__', fake_import)
    with caplog.at_level(logging.WARNING, logger=_LOGGER_NAME):
        name, writer = se._select_dta_backend()
    assert name == 'pandas'
    msgs = ' | '.join(r.getMessage() for r in caplog.records)
    assert 'embedded value labels' in msgs
    assert '不可跨' in msgs  # 二进制不可跨后端复现的漂移明示


def test_export_labels_do_carries_backend_fingerprint(tmp_path, monkeypatch):
    panel = pd.DataFrame({'target_bank': ['A'], 'year': [2020], 'n_articles': [3]})
    panel_path = tmp_path / 'panel.parquet'
    panel.to_parquet(panel_path)
    monkeypatch.setattr(se, '_select_dta_backend',
                        lambda: ('pandas', se._write_dta_pandas_fallback))
    result = se.export_panel_to_stata(str(panel_path), str(tmp_path))
    content = Path(result['labels_do']).read_text(encoding='utf-8')
    assert '* .dta writer backend: pandas' in content
