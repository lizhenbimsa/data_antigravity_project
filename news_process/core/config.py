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


def _detect_split_mode(config_dir: str) -> tuple[bool, list[str]]:
    """检查 split-mode 7 个域 YAML 的存在情况。

    Returns:
        ``(all_present, missing)``:
            - ``all_present``: 7 个文件是否全部存在;
            - ``missing``: 缺失的 ``<domain>.yaml`` 文件名列表
              (全部存在时为空列表; 全部缺失时长度等于
              ``len(_SPLIT_DOMAINS)``)。
    """
    missing: list[str] = []
    for domain in _SPLIT_DOMAINS:
        if not os.path.exists(os.path.join(config_dir, f'{domain}.yaml')):
            missing.append(f'{domain}.yaml')
    return len(missing) == 0, missing


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

    if config_path is None:
        split_complete, split_missing = _detect_split_mode(config_dir)
        if split_complete:
            # Phase 4d split-mode (优先, 7 个域 YAML 全部存在)
            config = {}
            for domain in _SPLIT_DOMAINS:
                domain_path = os.path.join(config_dir, f'{domain}.yaml')
                with open(domain_path, 'r', encoding='utf-8') as f:
                    domain_cfg = yaml.safe_load(f) or {}
                config = _deep_merge(config, domain_cfg)
        elif len(split_missing) < len(_SPLIT_DOMAINS):
            # 部分 split YAML 存在但不齐全 → 不可恢复, 显式抛错
            # (避免静默回退到空 stub config.yaml 触发下游隐晦 KeyError)
            existing = [
                f'{d}.yaml' for d in _SPLIT_DOMAINS
                if f'{d}.yaml' not in split_missing
            ]
            raise RuntimeError(
                f"配置目录 {config_dir} 处于不一致状态: split-mode 检测到 "
                f"{len(existing)}/{len(_SPLIT_DOMAINS)} 个域 YAML 存在 "
                f"({existing}), 但缺失 {split_missing}。\n"
                f"请补齐缺失文件; 或删除全部 split YAML 让系统回退到 legacy "
                f"config.yaml 单文件模式。"
            )
        else:
            # 全部 split YAML 都缺失 → 走 legacy 单文件模式
            config_path = os.path.join(config_dir, 'config.yaml')
            if not os.path.exists(config_path):
                raise FileNotFoundError(
                    f"配置文件未找到: {config_path} (且 split-mode 7 个域 "
                    f"YAML 也全部不存在: {split_missing})"
                )
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            if not config:
                # config.yaml 为空 stub (Phase 4d 后的常见状态) — 显式报错
                # 否则下游 CONFIG['paths'] 等会触发隐晦 KeyError, 用户难以诊断
                raise RuntimeError(
                    f"Legacy 配置文件 {config_path} 为空或仅含注释 (空 stub)。\n"
                    f"自 Phase 4d 起该文件已被拆分为 7 个域 YAML; "
                    f"请在 {config_dir} 下提供 "
                    f"{[f'{d}.yaml' for d in _SPLIT_DOMAINS]}, "
                    f"或将原始 config.yaml 内容恢复进单文件以继续使用 legacy 模式。"
                )
    else:
        # 显式指定 config_path → 强制单文件模式 (绕过 split-mode 检测)
        if not os.path.isabs(config_path):
            config_path = os.path.join(project_root, config_path)

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件未找到: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}

        if not config:
            raise RuntimeError(
                f"显式指定的配置文件 {config_path} 为空或仅含注释; "
                f"请检查文件内容是否正确。"
            )

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

    # plan s4 漏洞 A 修复: 把 env 替换与 path resolve 拆为两遍
    # ─────────────────────────────────────────────────────────────────
    # 旧实现是 if/elif 互斥: 若一个字符串既含 ${VAR} 又是 ./xxx 形式 (env 值
    # 本身是相对路径), env 替换后不会再走 ./ join project_root 分支, 结果残留
    # 相对 CWD 的字符串。
    # 修复策略: 第一遍仅做 env 替换并把结果写回; 第二遍重新检测 ./ 前缀做
    # path resolve。这样两类规范化语义独立, 任何 env→相对路径的中转都能命中。
    #
    # ⚠️严禁简化为"去掉 ./ 前缀过滤后对所有字符串 join project_root":
    # media_types_to_include: ['报纸'] / enabled_methods: [tone_llms] /
    # model_name: gpt-... 等非路径字符串会被错误解析成 <project_root>/报纸,
    # 整个配置层秒崩。./ 前缀是项目内部"这是项目根相对路径"的约定标记,
    # 不能去掉。漏洞 B (YAML 中部分路径缺 ./ 前缀) 由数据层独立修复。

    def _resolve_env_in_place(d):
        """第一遍: 仅做 ${VAR} 替换, 原地写回。"""
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, str):
                    if _env_pattern.search(v):
                        d[k] = _resolve_env_vars(v)
                elif isinstance(v, (dict, list)):
                    _resolve_env_in_place(v)
        elif isinstance(d, list):
            for i, v in enumerate(d):
                if isinstance(v, str):
                    if _env_pattern.search(v):
                        d[i] = _resolve_env_vars(v)
                elif isinstance(v, (dict, list)):
                    _resolve_env_in_place(v)

    def _resolve_paths_in_place(d, root):
        """第二遍: 检测 ``./`` / ``.\\`` 前缀并 join project_root。"""
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, str):
                    if v.startswith('./') or v.startswith('.\\'):
                        d[k] = os.path.normpath(os.path.join(root, v))
                elif isinstance(v, (dict, list)):
                    _resolve_paths_in_place(v, root)
        elif isinstance(d, list):
            for i, v in enumerate(d):
                if isinstance(v, str):
                    if v.startswith('./') or v.startswith('.\\'):
                        d[i] = os.path.normpath(os.path.join(root, v))
                elif isinstance(v, (dict, list)):
                    _resolve_paths_in_place(v, root)

    _resolve_env_in_place(config)
    _resolve_paths_in_place(config, project_root)

    # Phase 4d: 把任何外部 prompt 模板文件内联到 config dict 中
    _inline_external_prompts(config, project_root)

    return config


def _load_dotenv(project_root: str):
    """把 ``project_root/.env`` 加载到 os.environ; 已存在的值不覆盖。

    若已安装 ``python-dotenv`` 则优先调用; 否则退化为最小化解析器。
    ``.env`` 不存在时静默无操作。

    Fallback 解析器与 python-dotenv 行为对齐 (Phase 9 / Plan P0-1):
        - 行内 ``#`` 注释剥离 (要求注释前至少一个空白, 与 ``KEY=#hash`` 区分)
        - ``${VAR}`` 嵌套展开 (使 ``CLAUDE_KEY=${YUNWU_KEY}`` 在缺 dotenv 时也工作)
        - 已存在的 env 值不覆盖 (与 dotenv ``override=False`` 一致)
    早期 fallback 不展开 ``${VAR}`` 会让字面量 ``"${YUNWU_API_KEY}"`` 污染
    env, 后续 LLM 调用得到 401; 该 bug 在生产恰好被 requirements.txt 锁
    住的 ``python-dotenv>=1.0.0`` 掩盖, 但 ImportError 一旦命中即崩。
    """
    env_path = os.path.join(project_root, '.env')
    if not os.path.exists(env_path):
        return

    try:
        from dotenv import load_dotenv
        load_dotenv(env_path, override=False)
        return
    except ImportError:
        pass

    _var_pattern = re.compile(r'\$\{([^}]+)\}')

    def _expand_vars(value: str) -> str:
        return _var_pattern.sub(
            lambda m: os.environ.get(m.group(1), ''), value
        )

    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, _, value = line.partition('=')
            key = key.strip()
            if not key:
                continue
            for sep in (' #', '\t#'):
                if sep in value:
                    value = value.split(sep, 1)[0]
                    break
            value = value.strip().strip('"').strip("'")
            value = _expand_vars(value)
            if key not in os.environ:
                os.environ[key] = value
