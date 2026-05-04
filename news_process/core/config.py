"""news_process.core.config — YAML 配置 + .env 加载器。

Phase 1: 由历史 ``utils/helpers.py:1-194`` 拆分而来。
Phase 4d: 新增 split-mode 检测 (7 域 YAML + 外部化 prompt) +
          deep-merge 加载 + 自动从磁盘注入 prompt 模板。

保留的公开 API: ``load_config()``。
"""

from __future__ import annotations

import logging
import os
import re

import yaml


# ----------------------------------------------------------------------------
# Phase 4d: split-mode 相关常量
# ----------------------------------------------------------------------------

_SPLIT_DOMAINS: tuple[str, ...] = (
    'paths', 'preprocessing', 'filtering', 'sentiment',
    'features', 'panel', 'validation',
)


def _detect_split_mode(config_dir: str) -> bool:
    """当 ``config_dir`` 下 7 个域 YAML 全部存在时返回 True。"""
    for domain in _SPLIT_DOMAINS:
        if not os.path.exists(os.path.join(config_dir, f'{domain}.yaml')):
            return False
    return True


def _deep_merge(a: dict, b: dict) -> dict:
    """将 ``b`` 深度合并进 ``a`` 的副本。

    - 嵌套字典递归合并。
    - 列表整体 *替换* (不做追加) — 与 etcd / k8s configmap 语义一致。
    - 标量整体替换。
    - key 冲突时 ``b`` 胜出。

    返回新字典; 两个入参均不被修改。
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
    """递归遍历 config, 将 ``X_template_file`` 键替换为对应磁盘内容。

    约定: 任何以 ``_template_file`` 结尾的叶节点键 (其值是 YAML 中指向某个
    ``.txt`` 文件的路径), 会被读取后将文件内容写到 *同名键去掉 ``_file``
    后缀* 的位置上, 然后保留 ``_file`` 元数据 (供下游可追溯)。

    这样下游代码 (例如 ``cfg['tone_llm_processing']['prompt_template']``)
    无论 prompt 是 YAML 内联 (legacy mode) 还是外部 ``.txt`` (Phase 4d
    split mode) 均能透明使用。

    原地修改 ``config``。
    """
    if not isinstance(config, dict):
        return

    for k in list(config.keys()):
        v = config[k]
        if isinstance(v, dict):
            _inline_external_prompts(v, project_root)
        elif isinstance(v, str) and k.endswith('_template_file'):
            target_key = k[:-len('_file')]  # 仅去掉 '_file' 后缀
            file_path = v
            # `v` 已经被 resolve_paths() 路径化; 接受绝对路径输入
            if not os.path.isabs(file_path):
                file_path = os.path.normpath(os.path.join(project_root, file_path))
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                config[target_key] = content
                # 保留 *_file 元数据供可追溯性使用 (下游若忽略此键, 仍向后兼容)。
            except FileNotFoundError:
                logging.getLogger(__name__).warning(
                    f"Prompt 模板文件未找到: {file_path} (键 {k}); "
                    f"保留原始路径字符串。"
                )


# ----------------------------------------------------------------------------
# 公开 API
# ----------------------------------------------------------------------------


def load_config(config_path=None):
    """加载 YAML 配置, 并将相对路径解析为绝对路径。

    模式
    -----
    1. **Phase 4d split-mode** (优先): 当
       ``config/{paths,preprocessing,filtering,sentiment,features,panel,
       validation}.yaml`` 7 个文件全部存在时, 逐个加载并 *deep-merge*
       合并; 历史的 ``config.yaml`` 已退化为 stub, 此模式下被跳过。
    2. **Legacy monolithic mode** (向后兼容): 当任一 split YAML 缺失时,
       回退到把 ``config.yaml`` 当作单文件读取。

    两种模式下返回的字典**语义等价**, 由
    ``tests/integration/test_config_split_equivalence.py`` 保证。

    对合并后字典做的后处理:

    - ``${VAR_NAME}`` 占位符替换为 env 变量值 (自动从项目根加载 ``.env``)。
    - 相对路径 (``./...``) 解析为基于项目根的绝对路径。
    - Phase 4d: 任何以 ``_template_file`` 结尾的叶节点键, 其指向的
      ``.txt`` 内容会被读取并写到同名键去掉 ``_file`` 后缀的位置 (使得
      ``cfg['x']['prompt_template']`` 在 YAML 内联 prompt 和外部 ``.txt``
      两种情形下行为一致)。

    Args:
        config_path: 可选; 指向单个 YAML 文件的路径 (强制 legacy 模式);
                     不传时默认走 ``<project_root>/config/config.yaml``。

    Returns:
        dict: 解析完毕的配置 (字符串均已规范化)。
    """
    # core/config.py -> core/ -> news_process/  (上溯一层)
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
        # Legacy monolithic 模式 (或显式 config_path 覆盖)
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

    # Phase 4d: 把任何外部 prompt 模板文件内联到 config dict 中
    _inline_external_prompts(config, project_root)

    return config


def _load_dotenv(project_root: str):
    """把 ``project_root/.env`` 加载到 os.environ; 已存在的值不覆盖。

    若已安装 ``python-dotenv`` 则优先调用; 否则退化为最小化解析器。
    ``.env`` 不存在时静默无操作。
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
