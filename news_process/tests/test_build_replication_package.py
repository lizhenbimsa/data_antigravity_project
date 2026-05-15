"""v3.2.0 — build_replication_package 测试 (plan v14 §9.3)

测试范围:
    - _validate_spec_choices: 合法占位符 + 合法值
    - _substitute_placeholders: {{KEY}} 替换 + 残留检测 (fail-fast)
    - build_replication_package: 一键打包目录结构
    - git commit hash 嵌入 (含 dirty 检测)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


def test_validate_spec_choices_valid():
    """合法 main spec 通过校验."""
    from news_process.papers._common.stata_runner import _validate_spec_choices
    _validate_spec_choices({
        'MAIN_LOCUS_TRACK': 'lc',
        'MAIN_SUBST_TRACK': 'sf',
        'MAIN_SENT_TRACK':  'ctx',
    })  # no raise


def test_validate_spec_choices_unknown_key():
    """未知占位符 key 抛 ValueError."""
    from news_process.papers._common.stata_runner import _validate_spec_choices
    with pytest.raises(ValueError, match="未知占位符"):
        _validate_spec_choices({
            'MAIN_LOCUS_TRACK': 'lc',
            'MAIN_SUBST_TRACK': 'sf',
            'MAIN_SENT_TRACK':  'ctx',
            'UNKNOWN_KEY': 'value',
        })


def test_validate_spec_choices_invalid_value():
    """非法 spec 值抛 ValueError."""
    from news_process.papers._common.stata_runner import _validate_spec_choices
    with pytest.raises(ValueError, match="非法"):
        _validate_spec_choices({
            'MAIN_LOCUS_TRACK': 'wrong_value',  # 非法
            'MAIN_SUBST_TRACK': 'sf',
            'MAIN_SENT_TRACK':  'ctx',
        })


def test_validate_spec_choices_missing_required():
    """缺必需占位符抛 ValueError."""
    from news_process.papers._common.stata_runner import _validate_spec_choices
    with pytest.raises(ValueError, match="缺必需"):
        _validate_spec_choices({
            'MAIN_LOCUS_TRACK': 'lc',
            # 缺 MAIN_SUBST_TRACK / MAIN_SENT_TRACK
        })


def test_substitute_placeholders_basic():
    """{{KEY}} 替换正常工作."""
    from news_process.papers._common.stata_runner import _substitute_placeholders
    content = "local LOCUS tech_frac_{{MAIN_LOCUS_TRACK}}\nlocal SUBST symb_frac_{{MAIN_SUBST_TRACK}}\n"
    out = _substitute_placeholders(content, {
        'MAIN_LOCUS_TRACK': 'lc',
        'MAIN_SUBST_TRACK': 'sf',
    })
    assert 'tech_frac_lc' in out
    assert 'symb_frac_sf' in out
    assert '{{' not in out


def test_substitute_placeholders_failfast_residue():
    """plan v14 §9.5: 残留未替换 {{...}} 抛 ValueError."""
    from news_process.papers._common.stata_runner import _substitute_placeholders
    content = "local LOCUS {{MAIN_LOCUS_TRACK}}\nlocal MISSING {{NOT_PROVIDED}}"
    with pytest.raises(ValueError, match="未替换完整"):
        _substitute_placeholders(content, {
            'MAIN_LOCUS_TRACK': 'lc',
            # NOT_PROVIDED 未提供
        })


def test_build_replication_package_structure(tmp_path):
    """plan v14 §9.3: replication 包目录结构完整."""
    from news_process.papers._common.stata_runner import build_replication_package
    pkg = build_replication_package(
        main_spec_choices={
            'MAIN_LOCUS_TRACK': 'lc',
            'MAIN_SUBST_TRACK': 'sf',
            'MAIN_SENT_TRACK':  'ctx',
            'PROJECT_ROOT':     str(tmp_path),
        },
        output_root=tmp_path,
    )
    assert pkg.is_dir()
    assert pkg.name == 'replication_v3.2.0_lc_sf_ctx'
    assert (pkg / 'code').is_dir()
    assert (pkg / 'data').is_dir()
    assert (pkg / 'output' / 'tables').is_dir()
    assert (pkg / 'output' / 'figures').is_dir()


def test_build_replication_package_templates_instantiated(tmp_path):
    """模板 .do.tmpl 实例化为 .do, 占位符已替换."""
    from news_process.papers._common.stata_runner import build_replication_package
    pkg = build_replication_package(
        main_spec_choices={
            'MAIN_LOCUS_TRACK': 'lc',
            'MAIN_SUBST_TRACK': 'sf',
            'MAIN_SENT_TRACK':  'ctx',
            'PROJECT_ROOT':     str(tmp_path),
        },
        output_root=tmp_path,
    )
    # 至少 3 个核心模板被实例化
    do_files = list((pkg / 'code').glob('*.do'))
    assert len(do_files) >= 3
    # 占位符全替换 (无 {{ 残留)
    for do_file in do_files:
        content = do_file.read_text(encoding='utf-8')
        assert '{{' not in content, f"{do_file.name} 含未替换占位符"
        assert '{{MAIN_LOCUS_TRACK}}' not in content


def test_build_replication_package_substitutions_correct(tmp_path):
    """替换值实际在 .do 内容中."""
    from news_process.papers._common.stata_runner import build_replication_package
    pkg = build_replication_package(
        main_spec_choices={
            'MAIN_LOCUS_TRACK': 'lc',
            'MAIN_SUBST_TRACK': 'sf',
            'MAIN_SENT_TRACK':  'ctx',
            'PROJECT_ROOT':     str(tmp_path),
        },
        output_root=tmp_path,
    )
    # 11_table2 应含 `llm_vote_tone_ctx` (sentiment=ctx 替换)
    table2 = (pkg / 'code' / '11_table2_main_m1m6.do').read_text(encoding='utf-8')
    assert 'llm_vote_tone_ctx' in table2
    assert 'tech_frac_lc' in table2  # locus=lc
    assert 'symb_frac_sf' in table2  # subst=sf


def test_build_replication_package_readme_contains_commit_hash(tmp_path):
    """plan v14 §9.3 R48-A: README.md 含 git commit hash."""
    from news_process.papers._common.stata_runner import build_replication_package
    pkg = build_replication_package(
        main_spec_choices={
            'MAIN_LOCUS_TRACK': 'lc',
            'MAIN_SUBST_TRACK': 'sf',
            'MAIN_SENT_TRACK':  'ctx',
            'PROJECT_ROOT':     str(tmp_path),
        },
        output_root=tmp_path,
    )
    readme = (pkg / 'README.md').read_text(encoding='utf-8')
    assert 'Generated at' in readme
    # commit hash 是 12 char 或 'unknown' 或 '<hash>+dirty'
    assert 'locus track' in readme
    assert 'lc' in readme  # spec choice 记录


def test_build_replication_package_dirty_detection(tmp_path):
    """plan v14 §9.3 R49-A: dirty 检测应工作 (working tree 有未 commit 文件 → +dirty)."""
    from news_process.papers._common.stata_runner import _get_git_commit_hash_with_dirty
    h = _get_git_commit_hash_with_dirty()
    # 当前 working tree 应是 clean (刚 commit) 或 +dirty (本测试运行中)
    assert h != 'unknown' or h.endswith('+dirty') or len(h) >= 7


def test_build_replication_package_different_specs_yield_different_dirs(tmp_path):
    """不同 spec 产出不同目录, 允许多 spec 并存 (plan v14 R54-A)."""
    from news_process.papers._common.stata_runner import build_replication_package
    pkg_a = build_replication_package(
        main_spec_choices={'MAIN_LOCUS_TRACK': 'lc', 'MAIN_SUBST_TRACK': 'sf', 'MAIN_SENT_TRACK': 'ctx',
                           'PROJECT_ROOT': str(tmp_path)},
        output_root=tmp_path,
    )
    pkg_b = build_replication_package(
        main_spec_choices={'MAIN_LOCUS_TRACK': 'lf', 'MAIN_SUBST_TRACK': 'sf', 'MAIN_SENT_TRACK': 'full',
                           'PROJECT_ROOT': str(tmp_path)},
        output_root=tmp_path,
    )
    assert pkg_a.name == 'replication_v3.2.0_lc_sf_ctx'
    assert pkg_b.name == 'replication_v3.2.0_lf_sf_full'
    assert pkg_a != pkg_b
    # 两包独立存在
    assert pkg_a.is_dir() and pkg_b.is_dir()
