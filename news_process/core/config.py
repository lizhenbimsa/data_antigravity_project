"""news_process.core.config — YAML config + .env loader.

Split from legacy ``utils/helpers.py:1-194``.
Public API preserved: ``load_config()``.
"""

from __future__ import annotations

import logging
import os

import yaml


def load_config(config_path=None):
    """Load YAML config and resolve relative paths to absolute.

    Substitutes ``${VAR_NAME}`` placeholders with the corresponding env-var
    value (auto-loads ``.env`` from project root). Recursively converts
    ``./`` -prefixed paths to absolute paths under the project root.

    The project root is computed from this file's location:
    ``core/config.py`` → ``news_process/core/`` → ``news_process/``.

    Args:
        config_path: optional path to a YAML file; defaults to
                     ``<project_root>/config/config.yaml``.

    Returns:
        dict: resolved config (all strings normalized).
    """
    import re

    # core/config.py -> core/ -> news_process/  (one level up)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    _load_dotenv(project_root)

    if config_path is None:
        config_path = os.path.join(project_root, 'config', 'config.yaml')
    else:
        if not os.path.isabs(config_path):
            config_path = os.path.join(project_root, config_path)

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件未找到: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

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
