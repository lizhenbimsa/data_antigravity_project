"""v3.2.0 — Stage 46 stata_export 测试 (plan v14 §9.5)

测试范围:
    - 类别变量编码 (中文 str → byte 0/1)
    - variable labels ≤ 80 字符
    - 列名 ≤ 32 字符
    - core 列归属 (assign_core_columns, 供 codebook is_core; 2026-06-12 起单一全列 .dta, 不再写独立切分)
    - labels .do 文件生成
    - 编码方向 (R32-B: 0=baseline, 1=对照)

注: 不依赖 pyreadstat 安装 (除集成测试外, pyreadstat 调用以 ImportError skip)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


@pytest.fixture
def mock_panel():
    """模拟 panel DataFrame, 含双轨 stage 3 字段."""
    return pd.DataFrame({
        'target_bank': ['工商银行', '建设银行', '招商银行'] * 4,
        'year': [2020, 2021, 2022, 2023] * 3,
        'n_articles': [100, 80, 60, 50, 120, 90, 70, 55, 110, 85, 65, 52],
        'innovation_locus_full': ['底层技术', '应用场景', '底层技术', None,
                                  '应用场景', '应用场景', '底层技术', '应用场景',
                                  '底层技术', '应用场景', '底层技术', '应用场景'],
        'innovation_locus_ctx': ['应用场景', '应用场景', '底层技术', '底层技术',
                                 '应用场景', '底层技术', '底层技术', '应用场景',
                                 '应用场景', '应用场景', '底层技术', None],
        'innovation_substantiveness_full': ['实质性', '象征性', '实质性', '象征性',
                                            '实质性', '实质性', '象征性', '实质性',
                                            '象征性', '实质性', '实质性', '象征性'],
        'innovation_substantiveness_ctx':  ['象征性', '象征性', '实质性', '实质性',
                                            '实质性', '象征性', '象征性', '实质性',
                                            '象征性', '实质性', '象征性', '实质性'],
        'llm_vote_tone_full': np.random.RandomState(42).uniform(-1, 1, 12),
        'llm_vote_tone_ctx':  np.random.RandomState(43).uniform(-1, 1, 12),
        'llm_verified_dual_full_only': [False] * 12,
        'llm_verified_dual_ctx_only':  [False] * 12,
        'llm_verified_dual_both':      [True] * 12,
        'category_confidence_full': np.random.RandomState(44).uniform(0.6, 0.95, 12),
        'category_confidence_ctx':  np.random.RandomState(45).uniform(0.6, 0.95, 12),
    })


def test_encoding_direction_locus():
    """R32-B 编码方向: 0=底层技术 (baseline), 1=应用场景 (对照)."""
    from news_process.pipeline.panel.stata_export import LOCUS_ENCODING
    assert LOCUS_ENCODING['底层技术'] == 0
    assert LOCUS_ENCODING['应用场景'] == 1


def test_encoding_direction_substantiveness():
    """R32-B 编码方向: 0=实质性 (baseline), 1=象征性 (对照).

    天然解释方向: 洗稿率框架下 β 解释 "象征性相对实质性的差异".
    """
    from news_process.pipeline.panel.stata_export import SUBSTANTIVENESS_ENCODING
    assert SUBSTANTIVENESS_ENCODING['实质性'] == 0
    assert SUBSTANTIVENESS_ENCODING['象征性'] == 1


def test_encode_categorical_columns(mock_panel):
    """中文 str 列编码为 Int8 0/1."""
    from news_process.pipeline.panel.stata_export import encode_categorical_columns
    encoded_df, value_labels = encode_categorical_columns(mock_panel)
    # 类别列变 Int8
    assert encoded_df['innovation_locus_full'].dtype.name == 'Int8'
    assert encoded_df['innovation_locus_ctx'].dtype.name == 'Int8'
    assert encoded_df['innovation_substantiveness_full'].dtype.name == 'Int8'
    assert encoded_df['innovation_substantiveness_ctx'].dtype.name == 'Int8'
    # value labels 包含 4 个类别列
    assert 'innovation_locus_full' in value_labels
    assert 'innovation_locus_ctx' in value_labels
    assert 'innovation_substantiveness_full' in value_labels
    assert 'innovation_substantiveness_ctx' in value_labels
    # value labels 内容正确 (R32-B 双语)
    assert value_labels['innovation_locus_full'][0] == "底层技术 (Technology)"
    assert value_labels['innovation_substantiveness_full'][1] == "象征性 (Symbolic)"


def test_encoded_none_becomes_nan(mock_panel):
    """plan v14 §9.1: None 类别 → pd.NA (extended missing 在 pyreadstat 层映射 . / .a / .b)."""
    from news_process.pipeline.panel.stata_export import encode_categorical_columns
    encoded_df, _ = encode_categorical_columns(mock_panel)
    # mock_panel 在 innovation_locus_full 行 3 = None → encoded 应为 pd.NA
    assert pd.isna(encoded_df.loc[3, 'innovation_locus_full'])


def test_variable_label_length_under_80(mock_panel):
    """plan v14 §9.5: 全部 variable label ≤ 80 字节 (UTF-8)."""
    from news_process.pipeline.panel.stata_export import STATA_VAR_LABEL_MAXLEN, build_variable_labels
    labels = build_variable_labels(mock_panel)
    too_long = [(c, l, len(l.encode('utf-8'))) for c, l in labels.items()
                if len(l.encode('utf-8')) > STATA_VAR_LABEL_MAXLEN]
    assert not too_long, f"Labels 超 80 字节: {too_long[:5]}"


def test_column_name_length_under_32(mock_panel):
    """plan v14 §9.5 + §2.5: 全部列名 ≤ 32 字符 (Stata 硬限)."""
    from news_process.pipeline.panel.stata_export import STATA_VAR_NAME_MAXLEN
    too_long = [c for c in mock_panel.columns if len(c) > STATA_VAR_NAME_MAXLEN]
    assert not too_long, f"列名超 32 字符: {too_long}"


def test_core_columns_fit_ic(mock_panel):
    """plan v14 §9.1 + §9.5 (R42-A): core 列 ≤ 2048 (Stata IC 兼容)."""
    from news_process.pipeline.panel.stata_export import STATA_IC_MAX_VARS, assign_core_columns
    core = assign_core_columns(mock_panel)
    assert len(core) <= STATA_IC_MAX_VARS, f"Core 列数 {len(core)} 超 IC 限 {STATA_IC_MAX_VARS}"


def test_labels_do_file_generated(mock_panel, tmp_path):
    """plan v14 §9.1: labels .do 含 label var + label define + label values."""
    from news_process.pipeline.panel.stata_export import (
        build_variable_labels,
        encode_categorical_columns,
        write_labels_do_file,
    )
    encoded, value_labels = encode_categorical_columns(mock_panel)
    var_labels = build_variable_labels(encoded)
    do_path = tmp_path / "test_labels.do"
    write_labels_do_file(str(do_path), var_labels, value_labels)
    content = do_path.read_text(encoding='utf-8')
    # 必含三类 Stata 命令
    assert 'label var ' in content
    assert 'label define locus_lbl' in content
    assert 'label define subst_lbl' in content
    assert 'label values' in content
    # 双语 value labels
    assert '底层技术 (Technology)' in content
    assert '实质性 (Substantive)' in content


def test_validate_stata_compat_rejects_long_name():
    """validate_stata_compat 必须拒绝 > 32 字符列名."""
    from news_process.pipeline.panel.stata_export import validate_stata_compat
    bad_df = pd.DataFrame({
        'a_column_name_that_is_definitely_longer_than_32_chars': [1, 2, 3]
    })
    with pytest.raises(ValueError, match="Stata 兼容性"):
        validate_stata_compat(bad_df, {})


def test_validate_stata_compat_rejects_long_label():
    """validate_stata_compat 必须拒绝 > 80 字节 label."""
    from news_process.pipeline.panel.stata_export import validate_stata_compat
    df = pd.DataFrame({'col': [1, 2]})
    long_label = "X" * 90
    with pytest.raises(ValueError, match="Stata 兼容性"):
        validate_stata_compat(df, {'col': long_label})


def test_shorten_long_column_names_idf_score():
    """v3.2.0 M3/7: idf_score → idfsc 缩写覆盖 33-char 列名."""
    from news_process.pipeline.panel.stata_export import shorten_long_column_names
    df = pd.DataFrame({
        'jiang_2021_idf_score_hw_sum_title': [1.0, 2.0],
        'target_bank': ['工行', '建行'],
    })
    df_new, rename_map = shorten_long_column_names(df)
    # 应缩短到 ≤ 32 字符
    for col in df_new.columns:
        assert len(col) <= 32, f"col '{col}' still {len(col)} chars"
    # rename_map 记录反向映射
    assert 'jiang_2021_idf_score_hw_sum_title' in rename_map.values()


def test_shorten_long_column_names_leave1out():
    """v3.2.0 M3/7: leave1out → l1o 缩写覆盖 33+ char 列名."""
    from news_process.pipeline.panel.stata_export import shorten_long_column_names
    df = pd.DataFrame({
        'prov_leave1out_dict_avg_tone_full': [1.0],  # 33 chars
        'city_leave1out_dict_avg_tone_title': [2.0],  # 34 chars
    })
    df_new, rename_map = shorten_long_column_names(df)
    for col in df_new.columns:
        assert len(col) <= 32
    assert len(rename_map) == 2


def test_shorten_long_column_names_handles_conflicts(tmp_path):
    """v3.2.0 M3/7: 截断后冲突自动加 _1/_2 后缀防覆盖."""
    from news_process.pipeline.panel.stata_export import shorten_long_column_names
    # 两个超长 col 在截断到 32 字符时会冲突
    df = pd.DataFrame({
        'a_very_long_column_name_that_will_be_truncatedX': [1],
        'a_very_long_column_name_that_will_be_truncatedY': [2],
    })
    df_new, rename_map = shorten_long_column_names(df)
    assert len(set(df_new.columns)) == len(df_new.columns), "冲突未防止"


def test_shorten_long_column_names_short_unchanged():
    """≤ 32 char 列名不改."""
    from news_process.pipeline.panel.stata_export import shorten_long_column_names
    df = pd.DataFrame({
        'target_bank': [1],
        'innovation_locus_full': [1],
        'short_col': [1],
    })
    df_new, rename_map = shorten_long_column_names(df)
    assert list(df_new.columns) == ['target_bank', 'innovation_locus_full', 'short_col']
    assert rename_map == {}


def test_select_dta_backend():
    """v3.2.0 M1/7: backend 探测 — pyreadstat 优先, pandas fallback."""
    from news_process.pipeline.panel.stata_export import _select_dta_backend
    name, writer = _select_dta_backend()
    assert name in ('pyreadstat', 'pandas')
    assert callable(writer)


def test_export_panel_pandas_fallback_when_no_pyreadstat(tmp_path, mock_panel, monkeypatch):
    """v3.2.0 M1/7: pyreadstat 未装时 fallback 到 pandas to_stata (graceful)."""
    panel_path = tmp_path / "panel.parquet"
    mock_panel.to_parquet(panel_path)

    # 通过 patch _select_dta_backend 模拟 "pyreadstat 未安装"
    from news_process.pipeline.panel import stata_export
    monkeypatch.setattr(stata_export, '_select_dta_backend',
                        lambda: ('pandas', stata_export._write_dta_pandas_fallback))

    result = stata_export.export_panel_to_stata(str(panel_path), str(tmp_path))

    # 验证产出文件存在 (2026-06-12: 单一全列 full.dta, 不再产 core/aux 双切分)
    import os
    assert os.path.exists(result['full_dta'])
    assert os.path.exists(result['labels_do'])
    assert 'core_dta' not in result and 'aux_dta' not in result
    assert result['backend'] == 'pandas'


def test_export_panel_returns_backend_info(tmp_path, mock_panel):
    """v3.2.0 M1/7: export_panel_to_stata 返回 dict 含 backend 字段."""
    panel_path = tmp_path / "panel.parquet"
    mock_panel.to_parquet(panel_path)
    from news_process.pipeline.panel.stata_export import export_panel_to_stata
    result = export_panel_to_stata(str(panel_path), str(tmp_path))
    assert 'backend' in result
    assert result['backend'] in ('pyreadstat', 'pandas')


# ============================================================================
# quality-hardening Round 43 (2026-05-27): stata_export.py 覆盖率 81% → ≥90%
# 补漏: collab_mode 编码 (121-122) + codebook fallback (141-143) +
# HEURISTIC label 命中 (198) + label 截断 (205) + collab label 取值
# (464) + pyreadstat ImportError fallback (504-510) + panel 不存在 (538) +
# rename_map > 3 时的日志 (549-553) + aux dta 写出 (578-581) +
# codebook xlsx 异常 (592-593) + rename_map None fallback (620) +
# main() CLI 入口 (642-657)
# ============================================================================


def test_encode_categorical_columns_with_collab_mode():
    """innovation_collab_mode 编码: 0=自主研发, 1=外部协同 (lines 121-122 + 464)."""
    from news_process.pipeline.panel.stata_export import (
        COLLAB_MODE_ENCODING,
        COLLAB_MODE_VALUE_LABELS,
        encode_categorical_columns,
    )
    df = pd.DataFrame({
        'target_bank': ['A'] * 4,
        'year': [2020, 2021, 2022, 2023],
        'innovation_collab_mode_full': ['自主研发', '外部协同', '自主研发', None],
        'innovation_collab_mode_ctx':  ['外部协同', '外部协同', '自主研发', '自主研发'],
    })
    encoded, value_labels = encode_categorical_columns(df)
    assert encoded['innovation_collab_mode_full'].dtype.name == 'Int8'
    assert encoded.loc[0, 'innovation_collab_mode_full'] == 0
    assert encoded.loc[1, 'innovation_collab_mode_full'] == 1
    assert value_labels['innovation_collab_mode_full'] == COLLAB_MODE_VALUE_LABELS
    # 编码方向 sanity check
    assert COLLAB_MODE_ENCODING['自主研发'] == 0
    assert COLLAB_MODE_ENCODING['外部协同'] == 1


def test_build_variable_labels_codebook_fallback_when_unavailable(monkeypatch):
    """codebook get_variable_metadata_dict 抛 → fallback HEURISTIC (lines 141-143)."""
    import news_process.pipeline.panel.stata_export as se

    # 让 codebook import 路径抛 → 走 except
    def raising_import():
        raise ImportError("simulated codebook unavailable")
    monkeypatch.setattr(
        'news_process.pipeline.panel.codebook.get_variable_metadata_dict',
        raising_import,
    )
    df = pd.DataFrame({'target_bank': [1], 'year': [2020]})
    labels = se.build_variable_labels(df)
    # fallback 仍能生成 labels
    assert 'target_bank' in labels
    assert 'year' in labels


def test_build_variable_labels_heuristic_hit():
    """HEURISTIC_LABELS 命中走 line 198."""
    from news_process.pipeline.panel.stata_export import build_variable_labels
    df = pd.DataFrame({
        'innovation_locus_full': [1, 2],
        'mean_clarity_score_full': [0.1, 0.2],
    })
    labels = build_variable_labels(df)
    assert 'Innovation Locus' in labels['innovation_locus_full']
    assert 'Clarity Score' in labels['mean_clarity_score_full']


def test_build_variable_labels_truncates_long_label():
    """label > 80 UTF-8 bytes → 截断 + '...' (line 205)."""
    from news_process.pipeline.panel.stata_export import (
        STATA_VAR_LABEL_MAXLEN,
        build_variable_labels,
    )
    # fallback 路径 (列名既不在 codebook 也不在 HEURISTIC): label = col_name 本身
    super_long_name = 'a' * 100  # 100 字符 > 80, 触发截断
    # 注: shorten_long_column_names 会让真实流水线先缩短列名; 但 build_variable_labels
    # 独立调用时不缩短, 直接走 truncation 逻辑.
    df = pd.DataFrame({super_long_name: [1, 2]})
    labels = build_variable_labels(df)
    assert len(labels[super_long_name].encode('utf-8')) <= STATA_VAR_LABEL_MAXLEN
    assert labels[super_long_name].endswith('...')


def test_select_dta_backend_falls_back_when_pyreadstat_missing(monkeypatch):
    """pyreadstat 抛 ImportError → 回退 pandas backend (lines 504-510)。"""
    import builtins

    import news_process.pipeline.panel.stata_export as se

    orig_import = builtins.__import__

    def faking_import(name, *args, **kwargs):
        if name == 'pyreadstat':
            raise ImportError("simulated missing pyreadstat")
        return orig_import(name, *args, **kwargs)
    monkeypatch.setattr(builtins, '__import__', faking_import)

    name, writer = se._select_dta_backend()
    assert name == 'pandas'
    assert writer is se._write_dta_pandas_fallback


def test_export_panel_raises_when_parquet_missing(tmp_path):
    """panel parquet 不存在 → FileNotFoundError (line 538)."""
    from news_process.pipeline.panel.stata_export import export_panel_to_stata
    nonexistent = tmp_path / "no_such.parquet"
    with pytest.raises(FileNotFoundError, match="panel parquet 不存在"):
        export_panel_to_stata(str(nonexistent), str(tmp_path))


def test_export_panel_rename_map_more_than_three_logged(tmp_path, monkeypatch, caplog):
    """rename_map > 3 项时走 549-553 (only first 3 logged + total)."""
    import logging

    from news_process.pipeline.panel import stata_export as se

    # 构造 panel 含 4 个超长列名 → rename_map 有 4 项
    panel = pd.DataFrame({
        'target_bank': ['A', 'B'],
        'year': [2020, 2021],
        # 4 个 > 32 字符的列, shorten_long_column_names 都会改名
        'a_very_long_column_one_xxxxxxxxxxxx': [1, 2],
        'a_very_long_column_two_xxxxxxxxxxxx': [3, 4],
        'a_very_long_column_three_xxxxxxxxxxxx': [5, 6],
        'a_very_long_column_four_xxxxxxxxxxxx': [7, 8],
    })
    panel_path = tmp_path / "p.parquet"
    panel.to_parquet(panel_path)

    # 强制 pandas backend (避免 pyreadstat 写入需 numeric 唯一列等额外约束)
    monkeypatch.setattr(se, '_select_dta_backend',
                        lambda: ('pandas', se._write_dta_pandas_fallback))

    with caplog.at_level(logging.INFO,
                          logger='news_process.pipeline.panel.stata_export'):
        se.export_panel_to_stata(str(panel_path), str(tmp_path))
    msgs = ' | '.join(r.getMessage() for r in caplog.records)
    assert 'more' in msgs.lower() or 'Renamed' in msgs


def test_export_panel_only_full_dta_no_core_aux_split(tmp_path,
                                                      monkeypatch,
                                                      mock_panel):
    """2026-06-12: stage 46 仅产单一全列 full.dta — 不再写 core/aux 双切分
    (本机 StataNow/MP 19.5 maxvar≤120,000 直读 full); aux-only 指标列仍在 full 内."""
    import os

    from news_process.pipeline.panel import stata_export as se

    # 在 mock_panel 上加些 (历史上会落 aux 的) 非核心列
    panel = mock_panel.copy()
    panel['some_aux_metric_1'] = 1.0
    panel['another_aux_metric'] = 2.0
    panel_path = tmp_path / 'panel.parquet'
    panel.to_parquet(panel_path)

    monkeypatch.setattr(se, '_select_dta_backend',
                        lambda: ('pandas', se._write_dta_pandas_fallback))
    result = se.export_panel_to_stata(str(panel_path), str(tmp_path))

    # 返回 dict 不含 core_dta/aux_dta 键, 盘上无 core/aux 切分文件
    assert 'core_dta' not in result
    assert 'aux_dta' not in result
    assert os.path.exists(result['full_dta'])
    assert not os.path.exists(tmp_path / '46_panel_yearly_core.dta')
    assert not os.path.exists(tmp_path / '46_panel_yearly_aux.dta')
    # 全列保真: 原本会落 aux 的指标列也在 full.dta 内
    back = pd.read_stata(result['full_dta'])
    assert 'some_aux_metric_1' in back.columns
    assert 'another_aux_metric' in back.columns


def test_export_panel_codebook_write_failure_non_blocking(tmp_path, monkeypatch,
                                                           mock_panel):
    """codebook xlsx 写入失败应记 warning 不阻塞导出 (lines 592-593)."""
    from news_process.pipeline.panel import stata_export as se
    panel_path = tmp_path / 'panel.parquet'
    mock_panel.to_parquet(panel_path)

    monkeypatch.setattr(se, '_select_dta_backend',
                        lambda: ('pandas', se._write_dta_pandas_fallback))

    def raising_codebook(*args, **kwargs):
        raise RuntimeError("simulated codebook write failure")
    monkeypatch.setattr(se, '_write_codebook_xlsx', raising_codebook)

    # 不应抛
    result = se.export_panel_to_stata(str(panel_path), str(tmp_path))
    assert result['backend'] == 'pandas'


def test_write_codebook_rename_map_none_default(tmp_path, mock_panel):
    """_write_codebook_xlsx rename_map=None 默认值 (line 620)."""
    from news_process.pipeline.panel.stata_export import (
        _write_codebook_xlsx,
        build_variable_labels,
    )
    var_labels = build_variable_labels(mock_panel)
    out = tmp_path / 'codebook.xlsx'
    # 不传 rename_map → 走 None 默认值 + line 619-620 fallback
    _write_codebook_xlsx(mock_panel, var_labels, {}, list(mock_panel.columns),
                          str(out), rename_map=None)
    assert out.exists()


def test_write_labels_do_includes_collab_mode(tmp_path):
    """collab_cols 触发 'label values ... collab_mode_lbl' 输出 (line 464)."""
    from news_process.pipeline.panel.stata_export import (
        COLLAB_MODE_VALUE_LABELS,
        write_labels_do_file,
    )
    value_labels = {
        'innovation_collab_mode_full': COLLAB_MODE_VALUE_LABELS,
        'innovation_collab_mode_ctx': COLLAB_MODE_VALUE_LABELS,
    }
    var_labels = {
        'innovation_collab_mode_full': 'Innov. Collab Mode (Full-text)',
        'innovation_collab_mode_ctx': 'Innov. Collab Mode (Ctx)',
    }
    out_do = tmp_path / 'collab_labels.do'
    write_labels_do_file(str(out_do), var_labels, value_labels)
    content = out_do.read_text(encoding='utf-8')
    assert 'collab_mode_lbl' in content
    assert 'innovation_collab_mode_full' in content
    assert 'innovation_collab_mode_ctx' in content


def test_main_cli_entry(tmp_path, monkeypatch, mock_panel):
    """main() CLI 入口走 load_config → export_panel_to_stata 全链路 (642-657)."""
    from news_process.pipeline.panel import stata_export as se
    output_dir = tmp_path / 'out'
    output_dir.mkdir()
    log_dir = tmp_path / 'logs'
    log_dir.mkdir()
    panel_path = output_dir / '40_panel_yearly.parquet'
    mock_panel.to_parquet(panel_path)

    fake_cfg = {
        'paths': {
            'output_dir': str(output_dir),
            'log_dir': str(log_dir),
        },
        'filenames': {'output_45_panel_main': '40_panel_yearly.parquet'},
    }
    monkeypatch.setattr('news_process.core.config.load_config', lambda: fake_cfg)
    monkeypatch.setattr(se, '_select_dta_backend',
                        lambda: ('pandas', se._write_dta_pandas_fallback))

    se.main()
    # 2026-06-12: 仅产单一全列 full.dta, 不再产 core/aux 双切分
    assert (output_dir / '46_panel_yearly_full.dta').exists()
    assert not (output_dir / '46_panel_yearly_core.dta').exists()
    assert not (output_dir / '46_panel_yearly_aux.dta').exists()
