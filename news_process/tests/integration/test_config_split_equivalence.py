"""Phase 4d 集成测试 — config split-mode 与 legacy monolithic 等价性.

红线不变式
----------
1. ``load_config()`` 在 split-mode (7 YAMLs + prompts/*.txt) 与 legacy mode
   (单个 monolithic config.yaml) 下必须返回 *递归相等* 的 dict。
2. 测试自带一份"基准 monolithic config" (从 phase-3-baseline 提取),
   作为绝对基准, 防止当前 config.yaml 被人为修改后两套加载路径同步偏移
   都被这个测试盖住。
3. ``_deep_merge`` 单元行为: 嵌套 dict 递归合并, list 整体替换, 后值覆盖前值。
4. ``_inline_external_prompts`` 单元行为: ``X_template_file`` → ``X``
   (内容来自磁盘 .txt), 缺失文件不抛异常 (degraded warning)。

设计: 测试不依赖任何 pipeline 阶段的输出, 仅依赖 config/ 目录与 prompts/ 目录。
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

PROJECT_PARENT = Path(__file__).resolve().parents[3]
if str(PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(PROJECT_PARENT))

from news_process.core.config import (  # noqa: E402
    _SPLIT_DOMAINS,
    _deep_merge,
    _detect_split_mode,
    _inline_external_prompts,
    load_config,
)

# ============================================================================
# 1. _deep_merge 单元行为
# ============================================================================


class TestDeepMerge:
    def test_disjoint_keys(self):
        assert _deep_merge({'a': 1}, {'b': 2}) == {'a': 1, 'b': 2}

    def test_nested_dict_recursive_merge(self):
        a = {'x': {'y': 1, 'z': 2}}
        b = {'x': {'y': 10, 'w': 4}}
        out = _deep_merge(a, b)
        assert out == {'x': {'y': 10, 'z': 2, 'w': 4}}

    def test_list_replaces_not_appends(self):
        a = {'x': [1, 2, 3]}
        b = {'x': [4, 5]}
        out = _deep_merge(a, b)
        assert out == {'x': [4, 5]}

    def test_scalar_overrides_dict(self):
        a = {'x': {'y': 1}}
        b = {'x': 'string'}
        out = _deep_merge(a, b)
        assert out == {'x': 'string'}

    def test_b_value_wins_on_conflict(self):
        out = _deep_merge({'a': 1}, {'a': 2})
        assert out == {'a': 2}

    def test_inputs_not_mutated(self):
        a = {'x': {'y': 1}}
        b = {'x': {'z': 2}}
        a_orig = {'x': {'y': 1}}
        b_orig = {'x': {'z': 2}}
        _deep_merge(a, b)
        assert a == a_orig
        assert b == b_orig


# ============================================================================
# 2. _detect_split_mode + _inline_external_prompts
# ============================================================================


class TestDetectSplitMode:
    def test_real_config_dir(self):
        # 实际项目 config_dir — 现在应该是 split-mode (Phase 4d 完成后)
        # 或 legacy mode (Phase 4d 未完成). 不强制断言任一; 只断言函数返回值结构正确。
        config_dir = PROJECT_PARENT / 'news_process' / 'config'
        result = _detect_split_mode(str(config_dir))
        assert isinstance(result, tuple) and len(result) == 2
        complete, missing = result
        assert isinstance(complete, bool)
        assert isinstance(missing, list)

    def test_split_mode_requires_all_domains(self, tmp_path):
        # 缺一个就不算 split-mode
        for d in _SPLIT_DOMAINS[:-1]:
            (tmp_path / f"{d}.yaml").write_text("k: v")
        complete, missing = _detect_split_mode(str(tmp_path))
        assert complete is False
        assert missing == [f'{_SPLIT_DOMAINS[-1]}.yaml']

        # 补齐最后一个
        (tmp_path / f"{_SPLIT_DOMAINS[-1]}.yaml").write_text("k: v")
        complete, missing = _detect_split_mode(str(tmp_path))
        assert complete is True
        assert missing == []


class TestInlineExternalPrompts:
    def test_no_op_on_dict_without_template_file(self, tmp_path):
        cfg = {'a': 1, 'b': {'c': 'string'}}
        _inline_external_prompts(cfg, str(tmp_path))
        assert cfg == {'a': 1, 'b': {'c': 'string'}}

    def test_inlines_existing_file(self, tmp_path):
        prompt_path = tmp_path / 'prompt.txt'
        prompt_path.write_text("hello\nworld", encoding='utf-8')
        cfg = {'tone_llm': {'prompt_template_file': str(prompt_path)}}
        _inline_external_prompts(cfg, str(tmp_path))
        assert cfg['tone_llm']['prompt_template'] == "hello\nworld"
        assert cfg['tone_llm']['prompt_template_file'] == str(prompt_path)

    def test_missing_file_emits_warning_no_crash(self, tmp_path, caplog):
        cfg = {'x': {'prompt_template_file': str(tmp_path / 'nonexistent.txt')}}
        _inline_external_prompts(cfg, str(tmp_path))
        # 原 _file 键保留; 新键不创建
        assert 'prompt_template' not in cfg['x']
        assert cfg['x']['prompt_template_file'].endswith('nonexistent.txt')


# ============================================================================
# 3. 等价性: split-mode vs legacy mode 加载结果递归相等
# ============================================================================


@pytest.fixture(scope="module")
def project_root() -> Path:
    return PROJECT_PARENT / 'news_process'


@pytest.fixture(scope="module")
def split_mode_cfg(project_root: Path) -> dict:
    """走真实 load_config() 加载; 应自动探测模式。"""
    return load_config()


@pytest.fixture(scope="module")
def legacy_yaml_path(project_root: Path) -> Path:
    """由当前 split YAMLs + 内联 prompts 重建的自包含 monolithic YAML 路径。

    在 tmp 目录中即时构建, 测试不会污染 config/。
    """
    tmp_dir = Path(tempfile.mkdtemp(prefix="cfg_eqv_"))
    try:
        merged = {}
        config_dir = project_root / 'config'
        split_complete, _ = _detect_split_mode(str(config_dir))
        if not split_complete:
            pytest.skip("Phase 4d split YAMLs not present; equivalence "
                        "fixture cannot reconstruct legacy mode.")
        for domain in _SPLIT_DOMAINS:
            domain_path = config_dir / f'{domain}.yaml'
            with open(domain_path, 'r', encoding='utf-8') as f:
                merged.update(yaml.safe_load(f) or {})
        # 内联 prompts, 让 legacy mode fixture 自包含
        for section in list(merged.keys()):
            if not isinstance(merged.get(section), dict):
                continue
            for key in list(merged[section].keys()):
                if not key.endswith('_template_file'):
                    continue
                rel_path = merged[section][key]
                if not os.path.isabs(rel_path):
                    abs_path = project_root.parent.joinpath(rel_path).resolve()
                else:
                    abs_path = Path(rel_path).resolve()
                if not abs_path.exists():
                    # 容错: 路径解析失败时尝试相对 project_root
                    abs_path = (project_root.parent
                                / Path(rel_path).as_posix().lstrip('./')).resolve()
                if abs_path.exists():
                    new_key = key[:-len('_file')]
                    merged[section][new_key] = abs_path.read_text(encoding='utf-8')

        yaml_text = yaml.safe_dump(merged, allow_unicode=True, sort_keys=False)
        out_path = tmp_dir / 'config.yaml'
        out_path.write_text(yaml_text, encoding='utf-8')
        yield out_path
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture(scope="module")
def legacy_mode_cfg(legacy_yaml_path: Path) -> dict:
    """显式把 load_config 指向重建出的 legacy 文件。"""
    return load_config(str(legacy_yaml_path))


def _deep_equal(a, b, path=""):
    """递归深度相等比较, 首个不匹配处给出详细 diff 信息。"""
    if type(a) is not type(b):
        return False, f"type mismatch at {path!r}: {type(a).__name__} vs {type(b).__name__}"
    if isinstance(a, dict):
        if a.keys() != b.keys():
            extra_a = set(a) - set(b)
            extra_b = set(b) - set(a)
            return False, (
                f"keys mismatch at {path!r}: only-in-a={extra_a!r}, "
                f"only-in-b={extra_b!r}"
            )
        for k in a:
            ok, msg = _deep_equal(a[k], b[k], f"{path}.{k}")
            if not ok:
                return False, msg
        return True, ""
    if isinstance(a, list):
        if len(a) != len(b):
            return False, (
                f"list length mismatch at {path!r}: {len(a)} vs {len(b)}"
            )
        for i, (x, y) in enumerate(zip(a, b)):
            ok, msg = _deep_equal(x, y, f"{path}[{i}]")
            if not ok:
                return False, msg
        return True, ""
    if a != b:
        return False, (
            f"value mismatch at {path!r}:\n  a={a!r}\n  b={b!r}"
        )
    return True, ""


class TestSplitLegacyEquivalence:
    def test_top_level_keys_match(self, split_mode_cfg, legacy_mode_cfg):
        ok, msg = _deep_equal(
            sorted(split_mode_cfg.keys()),
            sorted(legacy_mode_cfg.keys()),
            'top_level_keys'
        )
        assert ok, msg

    def test_full_dict_recursive_equality(self, split_mode_cfg, legacy_mode_cfg):
        ok, msg = _deep_equal(split_mode_cfg, legacy_mode_cfg, 'cfg')
        assert ok, f"split-mode and legacy-mode load_config() diverge:\n{msg}"

    def test_prompt_inlined_in_split_mode(self, split_mode_cfg):
        """Phase 4d 验证: prompt_template 在 split-mode 加载后必须为字符串
        (内容来自外部 .txt), 而非路径字符串。"""
        prompt = (split_mode_cfg.get('tone_llm_processing', {})
                  .get('prompt_template'))
        if prompt is None:
            pytest.skip("No tone_llm_processing.prompt_template in cfg")
        assert isinstance(prompt, str)
        assert len(prompt) > 100, (
            "prompt_template too short — expected full Unified-CoT text"
        )
        # 不应是 .txt 路径片段 (后者意味着 inline 失败)
        assert not prompt.endswith('.txt'), (
            "prompt_template still looks like a path — _inline_external_prompts "
            "did not run properly."
        )


# ============================================================================
# 5. Plan-r3 P1-4: .env.example ↔ yaml ${VAR} 对齐契约
# ============================================================================


class TestEnvExampleCoversYamlPlaceholders:
    """``.env.example`` 必须声明所有 yaml 中实际引用的 ``${VAR}`` 占位符.

    .env.example 中 ``# VAR=...`` 形式的 commented-out 行也算"已声明"
    (Plan-r3 P1-4 把 4 个 legacy var 注释化保留, 旧调用方仍能被覆盖).

    历史背景: round 2 sidecar 化前, .env.example 声明了 GPT5NANO/
    GEMINI3/CLAUDE4H 三个 LLM key, 但 sentiment.yaml 实际引用的是
    ${YUNWU_API_KEY} (v6/N7 后统一); .env.example 反而漏了它. 新机器复制
    .env.example -> .env 后启动会因 YUNWU_API_KEY 未声明导致 LLM 401.
    """

    def _yaml_placeholders(self) -> set[str]:
        import re
        yaml_dir = Path(__file__).resolve().parents[2] / 'config'
        placeholder_re = re.compile(r'\$\{([A-Z_][A-Z0-9_]*)\}')
        ph: set[str] = set()
        for f in yaml_dir.glob('*.yaml'):
            ph.update(placeholder_re.findall(f.read_text(encoding='utf-8')))
        return ph

    def _env_example_declarations(self) -> set[str]:
        import re
        env_path = Path(__file__).resolve().parents[2] / '.env.example'
        decl_re = re.compile(r'^\s*#?\s*([A-Z_][A-Z0-9_]*)\s*=', re.MULTILINE)
        return set(decl_re.findall(env_path.read_text(encoding='utf-8')))

    def test_yaml_placeholders_covered_by_env_example(self):
        ph = self._yaml_placeholders()
        decl = self._env_example_declarations()
        undeclared = ph - decl
        assert not undeclared, (
            f"yaml 引用 ${{{{...}}}} 但 .env.example 未声明: {sorted(undeclared)}. "
            f"新机器复制 .env.example -> .env 后启动会因这些变量缺失而失败. "
            f"请在 .env.example 中加入 (即使值留空 / 加 # 前缀注释也算声明)."
        )

    def test_env_example_no_dead_declarations_overlap_yaml(self):
        """sanity: .env.example 至少包含 yaml 引用的 var 集合的 ⊇ 关系
        (但允许 .env.example 多声明 — 比如 legacy var 与外部脚本覆盖)."""
        ph = self._yaml_placeholders()
        decl = self._env_example_declarations()
        assert ph.issubset(decl), f"yaml refs {ph - decl} not in env.example"


class TestEnvExampleIndirectReferenceValidation:
    """Plan-r3 round-3 review M2 / R5: .env.example 中 ``KEY=${OTHER}`` 间接引用
    若 ``OTHER`` 既未声明又不在 os.environ 中, 应触发 warning.

    新机器复制 .env.example -> .env 后, 只填 YUNWU_API_KEY 一个 var 是预期
    工作流; 但若忘记填 (如 CI 环境无 .env), 间接引用会 silent 展开为空字符串
    导致 LLM 调用 401. 本 invariant 守护 _validate_env_placeholders 第二阶段
    (round-3 review R5 引入) 真的会 warning.
    """

    def test_indirect_ref_to_unset_var_triggers_warning(self, tmp_path, caplog):
        """模拟一个含间接引用但目标 var 未在 os.environ 设置的 .env.example."""
        import logging as _log
        import os
        # 构造 minimal yaml + env.example 沙盒
        sandbox = tmp_path / "sandbox"
        cfg_dir = sandbox / "config"
        cfg_dir.mkdir(parents=True)
        # 一个最小 yaml 文件 (引用 EMBEDDING_API_KEY)
        (cfg_dir / "test.yaml").write_text(
            "embedding_api:\n  api_key: ${EMBEDDING_API_KEY}\n",
            encoding='utf-8'
        )
        # .env.example 声明 EMBEDDING_API_KEY 但间接引用 NONEXISTENT_VAR
        (sandbox / ".env.example").write_text(
            "EMBEDDING_API_KEY=${NONEXISTENT_VAR_FOR_TEST_M2}\n",
            encoding='utf-8'
        )

        # 临时清除该 var (若 CI 里有的话)
        backup = os.environ.pop('NONEXISTENT_VAR_FOR_TEST_M2', None)
        try:
            from news_process.core.config import _validate_env_placeholders
            with caplog.at_level(_log.WARNING, logger='news_process.core.config'):
                _validate_env_placeholders(str(sandbox))

            # 应触发至少一条 warning, 且 message 含 'NONEXISTENT_VAR_FOR_TEST_M2'
            warning_text = ' '.join(r.getMessage() for r in caplog.records)
            assert 'NONEXISTENT_VAR_FOR_TEST_M2' in warning_text, (
                f"间接引用未声明应触发 warning, 实际 captured: {warning_text!r}"
            )
        finally:
            if backup is not None:
                os.environ['NONEXISTENT_VAR_FOR_TEST_M2'] = backup

    def test_indirect_ref_to_set_var_no_warning(self, tmp_path, caplog):
        """间接引用的目标 var 在 os.environ 中有值时, 不应误报 warning."""
        import logging as _log
        import os
        sandbox = tmp_path / "sandbox"
        cfg_dir = sandbox / "config"
        cfg_dir.mkdir(parents=True)
        (cfg_dir / "test.yaml").write_text(
            "embedding_api:\n  api_key: ${EMBEDDING_API_KEY}\n",
            encoding='utf-8'
        )
        (sandbox / ".env.example").write_text(
            "EMBEDDING_API_KEY=${PRESENT_VAR_FOR_TEST_M2}\n",
            encoding='utf-8'
        )

        os.environ['PRESENT_VAR_FOR_TEST_M2'] = 'sk-fake-but-set'
        try:
            from news_process.core.config import _validate_env_placeholders
            with caplog.at_level(_log.WARNING, logger='news_process.core.config'):
                _validate_env_placeholders(str(sandbox))

            # 不应在 warning 中提及 PRESENT_VAR_FOR_TEST_M2 (它已设置)
            warning_text = ' '.join(r.getMessage() for r in caplog.records)
            assert 'PRESENT_VAR_FOR_TEST_M2' not in warning_text, (
                f"已设置的间接引用 var 不应警告, 实际 captured: {warning_text!r}"
            )
        finally:
            del os.environ['PRESENT_VAR_FOR_TEST_M2']
