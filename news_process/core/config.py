"""news_process.core.config — YAML config + .env loader.

Phase 1: split from legacy ``utils/helpers.py:1-194``.
Phase 4d: added split-mode (7-domain YAMLs + externalized prompts) detection
          + deep-merge loading + automatic prompt-from-disk injection.

Public API preserved: ``load_config()``.
"""

from __future__ import annotations

import logging
import os
import re

import yaml


# ----------------------------------------------------------------------------
# Phase 4d: split-mode constants
# ----------------------------------------------------------------------------

_SPLIT_DOMAINS: tuple[str, ...] = (
    'paths', 'preprocessing', 'filtering', 'sentiment',
    'features', 'panel', 'validation',
)


def _detect_split_mode(config_dir: str) -> bool:
    """Return True iff all 7 domain YAMLs exist under ``config_dir``."""
    for domain in _SPLIT_DOMAINS:
        if not os.path.exists(os.path.join(config_dir, f'{domain}.yaml')):
            return False
    return True


def _deep_merge(a: dict, b: dict) -> dict:
    """Deep-merge ``b`` into a copy of ``a``.

    - Nested dicts merge recursively.
    - Lists are *replaced* (not appended) — same semantic as etcd / k8s configmap.
    - Scalars are replaced.
    - Conflicting keys: ``b`` wins.

    Returns a new dict; neither input is mutated.
    """
    if not isinstance(a, dict):
        return b if b is not None else a
    if not isinstance(b, dict):
        return b if b is not None else a
    result = dict(a)
    for k, v in b.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def _inline_external_prompts(config: dict, project_root: str) -> None:
    """Walk config and replace ``X_template_file`` keys with their disk content.

    Convention: any leaf key ending in ``_template_file`` (sibling YAML field
    pointing to a ``.txt`` on disk) is opened and its content placed under
    the same key minus the ``_file`` suffix.  The ``_file`` key is then removed.

    This makes downstream code (``cfg['tone_llm_processing']['prompt_template']``)
    work identically whether the prompt was inline (legacy mode) or in a
    separate ``.txt`` (Phase 4d split mode).

    Mutates ``config`` in place.
    """
    if not isinstance(config, dict):
        return

    for k in list(config.keys()):
        v = config[k]
        if isinstance(v, dict):
            _inline_external_prompts(v, project_root)
        elif isinstance(v, str) and k.endswith('_template_file'):
            target_key = k[:-len('_file')]  # strip the '_file' suffix only
            file_path = v
            # `v` was already path-resolved by resolve_paths(); accept abs
            if not os.path.isabs(file_path):
                file_path = os.path.normpath(os.path.join(project_root, file_path))
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                config[target_key] = content
                # Keep the *_file metadata for traceability (downstream code
                # ignoring it remains backward compatible).
            except FileNotFoundError:
                logging.getLogger(__name__).warning(
                    f"Prompt 模板文件未找到: {file_path} (键 {k}); "
                    f"保留原始路径字符串。"
                )


# ----------------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------------


def load_config(config_path=None):
    """Load YAML config and resolve relative paths to absolute.

    Modes
    -----
    1. **Phase 4d split-mode** (preferred): when ``config/{paths,preprocessing,
       filtering,sentiment,features,panel,validation}.yaml`` all exist, load
       each one and *deep-merge* them. The legacy ``config.yaml`` is treated
       as a stub and skipped.
    2. **Legacy monolithic mode** (backwards compat): when any split YAML
       is missing, fall back to reading ``config.yaml`` as a single file.

    In both modes, the returned dict is semantically identical (verified by
    ``tests/integration/test_config_split_equivalence.py``).

    Post-processing applied to the merged dict:

    - ``${VAR_NAME}`` placeholders are substituted with env-var values
      (auto-loads ``.env`` from project root).
    - Relative paths (``./...``) are resolved to absolute paths under the
      project root.
    - Phase 4d: any leaf key ending in ``_template_file`` is read from disk
      and its content placed under the corresponding key without the
      ``_file`` suffix (so ``cfg['x']['prompt_template']`` works whether the
      prompt was inline in YAML or external in a ``.txt``).

    Args:
        config_path: optional path to a single YAML file (forces legacy mode);
                     defaults to ``<project_root>/config/config.yaml``.

    Returns:
        dict: resolved config (all strings normalized).
    """
    # core/config.py -> core/ -> news_process/  (one level up)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    _load_dotenv(project_root)

    config_dir = os.path.join(project_root, 'config')

    if config_path is None and _detect_split_mode(config_dir):
        # Phase 4d split-mode
        config = {}
        for domain in _SPLIT_DOMAINS:
            domain_path = os.path.join(config_dir, f'{domain}.yaml')
            with open(domain_path, 'r', encoding='utf-8') as f:
                domain_cfg = yaml.safe_load(f) or {}
            config = _deep_merge(config, domain_cfg)
    else:
        # Legacy monolithic mode (or explicit config_path override)
        if config_path is None:
            config_path = os.path.join(config_dir, 'config.yaml')
        else:
            if not os.path.isabs(config_path):
                config_path = os.path.join(project_root, config_path)

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件未找到: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}

    _env_pattern = re.compile(r'\$\{([^}]+)\}')

    def _resolve_env_vars(value: str) -> str:
        def _replacer(match):
            var_name = match.group(1)
            env_val = os.environ.get(var_name, '')
            if not env_val:
                logging.getLogger(__name__).warning(
                    f"环境变量 {var_name} 未设置，配置值将为空。"
                    f"请在 .env 文件或系统环境变量中设置该值。"
                )
            return env_val
        return _env_pattern.sub(_replacer, value)

    def resolve_paths(d, root):
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, str):
                    if _env_pattern.search(v):
                        d[k] = _resolve_env_vars(v)
                    elif v.startswith('./') or v.startswith('.\\'):
                        d[k] = os.path.normpath(os.path.join(root, v))
                elif isinstance(d[k], (dict, list)):
                    resolve_paths(d[k], root)
        elif isinstance(d, list):
            for i, v in enumerate(d):
                if isinstance(v, str):
                    if _env_pattern.search(v):
                        d[i] = _resolve_env_vars(v)
                    elif v.startswith('./') or v.startswith('.\\'):
                        d[i] = os.path.normpath(os.path.join(root, v))
                elif isinstance(d[i], (dict, list)):
                    resolve_paths(d[i], root)

    resolve_paths(config, project_root)

    # Phase 4d: inline any external prompt template files into the dict
    _inline_external_prompts(config, project_root)

    return config


def _load_dotenv(project_root: str):
    """Load ``project_root/.env`` into os.environ; existing values not overwritten.

    Prefers ``python-dotenv`` if installed; falls back to a minimal parser.
    Silent no-op when ``.env`` is absent.
    """
    env_path = os.path.join(project_root, '.env')
    if not os.path.exists(env_path):
        return

    try:
        from dotenv import load_dotenv
        load_dotenv(env_path, override=False)
    except ImportError:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, _, value = line.partition('=')
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = value
