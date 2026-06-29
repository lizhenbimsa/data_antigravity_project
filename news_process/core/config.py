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

from news_process.core.logging import sig4

# ----------------------------------------------------------------------------
# Phase 4d: split-mode 相关常量
# ----------------------------------------------------------------------------

_SPLIT_DOMAINS: tuple[str, ...] = (
    'paths', 'preprocessing', 'filtering', 'sentiment',
    'features', 'panel', 'validation',
)

# ── 经核验参考文献 (VERIFIED_REFERENCES 注册表, 逐字照抄 APA-7 + DOI; 仅日志用) ──
# 运行期 emit 进配置加载日志, 让 .log 自证"prompt 版本登记纪律"的方法学锚点 (非仅
# 留注释)。白话: prompt 文件首行 ``# version: <token>`` 派生 ``<key>_version`` 作为
# LLMCache 失效键 ("改 prompt → cache miss → 重新标注"的可见性根基, 见
# ``_inline_external_prompts``); 这套"LLM 标注前登记 prompt/温度版本以保可复现"的
# 纪律出处即下文 Carlson & Burbano (2026, SMJ) —— 与本文件 L113-116 已埋的注释锚点
# 同源, 此处把它升格为运行期可 emit 的依据。
_CONFIG_REFERENCES = {
    "carlson_burbano_llm_annotation": (
        "Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate "
        "data in management research: Foundational guidelines and warnings. "
        "Strategic Management Journal, 47(3), 699–725. "
        "https://doi.org/10.1002/smj.70023"
    ),
}


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


_PROMPT_VERSION_HEADER = re.compile(r'^#\s*version:\s*(\S+)\s*\r?\n')


def _inline_external_prompts(config: dict, project_root: str) -> None:
    """递归遍历 config, 将 ``X_template_file`` 键替换为对应磁盘内容。

    约定: 任何以 ``_template_file`` 结尾的叶节点键 (其值是 YAML 中指向某个
    ``.txt`` 文件的路径), 会被读取后将文件内容写到 *同名键去掉 ``_file``
    后缀* 的位置上, 然后保留 ``_file`` 元数据 (供下游可追溯)。

    Plan-r3 P3-17 续: 若文件首行匹配 ``# version: <token>\\n``, 则:
    - 把版本 token 写入 ``<target_key>_version`` 键 (供 callsite 传给
      ``LLMCache.get/put`` 的 ``prompt_version`` 参数);
    - 从 content 中剥离该首行, 避免把版本头当作 prompt 内容污染模型输入。
    若无版本头, ``<target_key>_version`` 默认为 ``"v0"`` (与 caching.py
    LLMCache 默认值一致, 与历史无关键值兼容)。

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
                # 📖 prompt 版本化纪律 (可复现 LLM 标注): 从 prompt 文件首行
                #    ``# version: <token>`` 派生 ``<key>_version`` 作为 LLMCache 失效键,
                #    是"改 prompt → cache miss → 重新标注"可见性的根基 (无版本头则 fallback
                #    'v0' 并 warning, 见下方)。该纪律的方法学依据:
                #    Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data
                #    in management research: Foundational guidelines and warnings. Strategic
                #    Management Journal, 47(3), 699–725. https://doi.org/10.1002/smj.70023
                #    (§ prompt/温度 的版本登记与可复现纪律)。
                m = _PROMPT_VERSION_HEADER.match(content)
                if m is not None:
                    config[target_key + '_version'] = m.group(1)
                    content = content[m.end():]
                else:
                    config[target_key + '_version'] = 'v0'
                    # P1-1 (cleanup/2026-05-13): prompt 文件无 ``# version:`` 头
                    # 时 fallback 到 'v0'. 这破坏 Plan-r3 P3-17 "改 prompt → cache
                    # miss" 的可见性保证 — 编辑文件却忘 bump 版本时, 旧 cache 静默
                    # 命中 (注: prompt 文本本身在 cache key 内, 仅当模板字符串渲
                    # 染结果 byte-identical 时此 bug 才显现, 边角但真实).
                    # 用 warning 提示 — 不改默认值 (改哈希反而引入不可控变量, 见
                    # cleanup plan 审-1 的方向性逆转论证). lint 工具
                    # ``scripts/lint/check_prompt_headers.py`` 在 CI / 本地强制.
                    logging.getLogger(__name__).warning(
                        f"Prompt 模板 {file_path} 缺 '# version: <token>' 首行头; "
                        f"将 fallback 到 ``{target_key}_version='v0'``. "
                        f"编辑该 prompt 但保留 byte-identical 渲染结果时, LLMCache "
                        f"会静默命中旧条目. 建议在 prompt 文件首行加 "
                        f"'# version: vX-YYYY-MM-DD' 以确保 cache 可控失效."
                    )
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

    # ── 纯日志富集 (golden-safe, log-only): prompt 版本登记可复现性自证 ──
    # ``_inline_external_prompts`` 已为每个外部 prompt 写入 ``<key>_template_version``
    # (LLMCache 失效键)。此处 ONCE-per-load 汇总: emit 每个已内联 prompt 键及其解析出的
    # 版本号 + 该纪律的方法学依据 (Carlson & Burbano 2026, SMJ), 把 L113-116 仅注释的
    # 锚点升格为"本次加载注册了哪些 prompt 版本作为缓存失效键"的自文档化复现日志。
    # 键/版本均为字符串 → 无裸 float, 无需 sig4/pct4。
    # ⚠ 仅 logger.* 输出, 不改 config / 不改控制流; 在 load_config 非递归调用点 emit,
    #   天然保证"每次加载只打一次", 不随 ``_inline_external_prompts`` 递归逐文件重复。
    # 注意 (caveat): 这发生在 import 时 (``CONFIG = load_config()`` 为模块级), 主要落在
    #   import-期日志, 未必进入某 stage ``setup_logging`` 的文件 handler; 价值因此有限,
    #   但 golden-safe 不受影响。
    try:
        _cfg_log = logging.getLogger(__name__)

        def _collect_prompt_versions(d, prefix, acc):
            """递归收集 ``<...>_template_version`` 键 → (dotted-path 去 _version, 版本值)。"""
            if isinstance(d, dict):
                for _k, _v in d.items():
                    _path = f"{prefix}.{_k}" if prefix else str(_k)
                    if isinstance(_k, str) and _k.endswith('_template_version'):
                        # 去掉 ``_version`` 后缀还原对应 prompt 模板键; 其值即解析出的版本号
                        acc.append((_path[:-len('_version')], _v))
                    elif isinstance(_v, (dict, list)):
                        _collect_prompt_versions(_v, _path, acc)
            elif isinstance(d, list):
                for _i, _v in enumerate(d):
                    if isinstance(_v, (dict, list)):
                        _collect_prompt_versions(_v, f"{prefix}[{_i}]", acc)

        _prompt_versions = []
        _collect_prompt_versions(config, "", _prompt_versions)
        if _prompt_versions:
            _cfg_log.info(
                "prompt 模板内联完成: 已注册 %d 个 prompt 版本作为 LLMCache 失效键 "
                "(改 prompt → cache miss → 重新标注)",
                len(_prompt_versions))
            for _pk, _pv in sorted(_prompt_versions):
                _cfg_log.info(f"  prompt 模板内联: {_pk} → {_pv}")
            # 📖 prompt/温度 版本登记的可复现纪律 (LLM 标注数据的基础指南与告警)
            _cfg_log.info(
                f"  📖 {_CONFIG_REFERENCES['carlson_burbano_llm_annotation']}")
    except Exception as _e:  # noqa: BLE001 — 日志块绝不让配置加载崩
        logging.getLogger(__name__).debug(
            f"(prompt 版本登记日志失败, 忽略不影响配置加载): {_e}")

    # Plan-r3 P1-4: 校验 yaml 引用的 ${VAR} 是否都在 .env.example 中声明
    # (落地 .env.example 头部第 7-12 行原本承诺但未实现的"Phase 1 校验").
    _validate_env_placeholders(project_root)

    # P0-3 (cleanup/2026-05-13): cross-stage enabled_methods 一致性提示.
    # 原为暴露 stage 24 → 45 隐式硬依赖 (配错会跑 8 小时才在 stage 45 崩).
    # 2026-06-12 起 stage 23/24 已改无条件 always-on, 该崩溃路径消除, 本检查
    # 降级为纯信息提示 (见函数 docstring).
    _validate_enabled_methods_consistency(config)

    # P1-2 (cleanup/2026-05-13): 三域 YAML schema 校验
    # tone_llm_processing / panel_building / herd_detection
    # 类型错误 raise; 未知字段 warning (防 typo silent fallback).
    from .schemas_yaml import validate_config_schema
    validate_config_schema(config)

    # ── 纯日志富集 (golden-safe, log-only): 配置加载面 (configuration surface) 复现摘要 ──
    # load_config 成功路径原本静默 (仅失败时 warning)。此处在 return 前补一行可复现性
    # provenance: 实际走的加载模式 (split-mode 7 域 deep-merge / legacy 单文件)、合并的
    # 域 YAML 数 (present ``_SPLIT_DOMAINS`` 计数)、产出的顶层 config 键数、已内联外部
    # prompt 模板数。全为整数计数 → :,d 打印 (无裸 float, 故无需 sig4/pct4)。记录"本次到底
    # 加载了怎样一张配置面", 是真正可复现 provenance。
    # ⚠ 仅 logger.* 输出, 不改 config / 控制流; split-mode 下 ``config_path`` 保持 None,
    #   据此判别模式。import-期 emit 未必进某 stage 文件 handler, 但 golden-safe 不受影响。
    try:
        _cfg_log = logging.getLogger(__name__)
        _is_split = config_path is None  # split-mode 下 config_path 始终保持 None
        _n_domains_merged = len(_SPLIT_DOMAINS) if _is_split else 0
        _n_prompts_inlined = 0
        _stk = [config]
        while _stk:
            _cur = _stk.pop()
            if isinstance(_cur, dict):
                for _k, _v in _cur.items():
                    if isinstance(_k, str) and _k.endswith('_template_version'):
                        _n_prompts_inlined += 1
                    if isinstance(_v, (dict, list)):
                        _stk.append(_v)
            elif isinstance(_cur, list):
                for _v in _cur:
                    if isinstance(_v, (dict, list)):
                        _stk.append(_v)
        _cfg_log.info(
            "配置加载完成 (复现 provenance): 模式=%s | 合并域 YAML=%d/%d | "
            "顶层 config 键=%d | 内联 prompt 模板=%d",
            "split-mode 7 域 deep-merge" if _is_split else "legacy 单文件",
            _n_domains_merged, len(_SPLIT_DOMAINS), len(config), _n_prompts_inlined)
    except Exception as _e:  # noqa: BLE001 — 日志块绝不让配置加载崩
        logging.getLogger(__name__).debug(
            f"(配置加载 provenance 日志失败, 忽略不影响配置): {_e}")

    return config


def herd_sensitivity_grid(config: dict) -> tuple[list[float], list[str]]:
    """herd 相似度阈值敏感性网格的单一事实源 (2026-06-13)。

    读 ``herd_detection.sensitivity_thresholds`` (sentiment.yaml), 返回
    ``(thresholds, tags)`` 两个等长列表:
      - thresholds: 升序去重后的 τ 网格, 已剔除基线 similarity_threshold
        (基线列就是现有 herd_weight_{track}, 不重复生成) 与 (0,1) 区间外的非法值;
      - tags: 与 thresholds 一一对应的列名后缀, ``thr{round(τ*100):02d}``
        (0.25 → 'thr25')。τ*100 非整数 (如 0.275) 会因 tag 碰撞风险被剔除并告警。

    消费方 (列名契约依赖本函数, 勿各自解析 config):
      - stage 24 ``pipeline/sentiment/herd_decay.py`` → 文章列
        ``herd_weight_{track}_{tag}`` / ``n_similar_articles_{track}_{tag}``
      - ``pipeline/panel/runner.py`` 步骤 3d → 加权列 ``llm_vote_*_hw_{tag}{track}``
      - ``pipeline/panel/encode.py`` → 聚合与面板比值 ``llm_vote_tone_hw_{tag}{track}``

    白话: "相似到 0.35 算抄稿"这个门槛是自选的, 这里统一登记一组松紧不同的
    备选门槛 (默认 0.25/0.30/0.40/0.45), 管道把每个门槛都算一遍, 最后在 Stata
    面板里各留一列加权语调, 用来证明回归结论不依赖 0.35 这个具体取值。
    """
    _log = logging.getLogger(__name__)
    herd_cfg = config.get('herd_detection', {}) or {}
    baseline = float(herd_cfg.get('similarity_threshold', 0.35))
    raw = herd_cfg.get('sensitivity_thresholds', [0.25, 0.30, 0.40, 0.45])
    if not isinstance(raw, (list, tuple)):
        _log.warning(
            "herd_detection.sensitivity_thresholds 非 list (%r), 阈值敏感性网格禁用",
            raw)
        return [], []

    thresholds: list[float] = []
    tags: list[str] = []
    seen_tags: set[str] = set()
    for item in raw:
        try:
            thr = float(item)
        except (TypeError, ValueError):
            _log.warning("sensitivity_thresholds 含非数值项 %r, 已跳过", item)
            continue
        if not (0.0 < thr < 1.0):
            _log.warning(
                "sensitivity_thresholds 项 %s 超出 (0,1) 开区间, 已跳过", sig4(thr))
            continue
        if abs(thr - baseline) < 1e-9:
            continue  # 基线已有 herd_weight_{track} 列, 不重复
        scaled = thr * 100
        if abs(scaled - round(scaled)) > 1e-6:
            _log.warning(
                "sensitivity_thresholds 项 %s 非 0.01 粒度, tag 无法唯一编码, 已跳过",
                sig4(thr))
            continue
        tag = f"thr{int(round(scaled)):02d}"
        if tag in seen_tags:
            continue  # 去重
        seen_tags.add(tag)
        thresholds.append(thr)
        tags.append(tag)

    order = sorted(range(len(thresholds)), key=lambda i: thresholds[i])
    sorted_thr = [thresholds[i] for i in order]
    sorted_tags = [tags[i] for i in order]
    # 纯日志富集 (golden-safe): 汇总最终解析出的稳健性阈值网格, 让"回归结论不依赖
    # 基线 τ 这一具体取值"的稳健性列覆盖范围在日志中自解释 (基线 τ 已剔除, 复用
    # 既有 herd_weight_{track} 列; 此处仅另登记备选门槛与其列名后缀)。所有非整数
    # 阈值经 sig4 渲染为四位有效数字 (项目规范 2026-06-24); 仅打印, 不改返回值。
    _log.info(
        "herd 相似度阈值敏感性网格已解析: 基线 τ=%s (已剔除/复用既有列), "
        "另登记 %d 个备选阈值 [%s] → 列名后缀 [%s]",
        sig4(baseline), len(sorted_thr),
        ", ".join(sig4(t) for t in sorted_thr) or "无",
        ", ".join(sorted_tags) or "无",
    )
    return sorted_thr, sorted_tags


# P0-3 (cleanup/2026-05-13): 决定"panel 构建是否启用"的 compute_* 标识集合.
# 任一为 True 即视为 panel_active. 加新 panel 主开关时必须扩本列表 (见
# ``_validate_enabled_methods_consistency`` docstring R3-2 note).
_PANEL_ACTIVE_KEYS: tuple[str, ...] = (
    'compute_attention_index',
    'compute_bartik_iv',
    'compute_policy_shocks',
)


def _validate_enabled_methods_consistency(config: dict) -> None:
    """软提示 (warning 级, 不阻断): 启用 panel 但 enabled_methods 未列 ``tone_berts`` 时提醒用户。

    历史背景: 早期 stage 23/24 受 ``berts_method_enabled`` 谓词条件启停 ——
    若禁用 tone_berts 而仍构建 panel, ``pipeline/panel/runner.py::main()`` 入口
    会因缺 ``24_herd_decay.parquet`` 而 ``sys.exit(1)`` (配错跑 8 小时才崩)。

    2026-06-12 变更: stage 23 (BERT 文章级情感) 与硬依赖它的 stage 24 已改为
    **无条件 always-on** (见 ``core/dag.py`` 二者均取 ``always_enabled`` 默认谓词)。
    无论 enabled_methods 如何配置, BERT 与 herd_decay 输出始终生成 → 上述
    ``sys.exit(1)`` 失败模式已消除。本函数因此降级为软提示 (仍走 ``logger.warning``,
    但不再阻断): 当配置未显式列出 tone_berts 时, 提醒用户 BERT 轨实际仍会运行
    (结构性阶段), 以免误以为已关闭。本提示不 raise, 也不再阻断任何配置。

    .. note:: maintenance
       ``_PANEL_ACTIVE_KEYS`` 是 3 个 compute_* 标识的硬编码列表 (R3-2);
       仍由 ``test_cleanup_2026_05_13`` 校验其为 PanelBuildingSchema 合法字段。
    """
    sentiment = config.get('sentiment_analysis', {}) or {}
    enabled_methods = sentiment.get('enabled_methods', []) or []

    panel_cfg = config.get('panel_building', {}) or {}
    # 任一 panel 子步启用即视为 panel 构建启用; 全部禁用才视为 panel 关闭.
    panel_active = any(
        panel_cfg.get(k, True)
        for k in _PANEL_ACTIVE_KEYS
    )

    if panel_active and 'tone_berts' not in enabled_methods:
        logging.getLogger(__name__).warning(
            "sentiment_analysis.enabled_methods 未列出 'tone_berts'; 注意 stage 23 "
            "(BERT 文章级情感) 与 stage 24 (跟风衰减) 自 2026-06-12 起为无条件 "
            "always-on 结构性阶段, 仍会照常运行并生成 24_herd_decay.parquet, "
            "stage 45 不会因此 sys.exit(1)。如需保持配置自洽, 可在 enabled_methods "
            "中补回 'tone_berts' 显式登记 BERT 轨。"
        )


def _validate_env_placeholders(project_root: str) -> None:
    """扫描 ``config/*.yaml`` 中所有 ``${VAR}`` 占位符, 与 ``.env.example``
    声明清单 (含 commented-out 行) 对比, 未声明的 var 报 warning。

    Plan-r3 P1-4 落地: 此函数实现了 ``.env.example`` 头部承诺的"未声明
    占位符警告"功能。

    Plan-r3 round-3 review R5 升级: 加第二阶段递归扫描 — ``.env.example``
    中 ``KEY=${OTHER_KEY}`` 形式的间接引用, 若 ``OTHER_KEY`` 既未在
    ``.env.example`` 声明, 也不在 ``os.environ`` 中, 同样报 warning. 防止
    新机器复制 .env.example -> .env 后只填 YUNWU_API_KEY, 但 EMBEDDING_API_KEY
    间接引用空值的 silent failure.

    设计要点:

    - 仅做 warning 不 raise — 避免过严打断 pipeline 运行 (尤其新 yaml
      字段试错期); CI 可通过 ``-W error::UserWarning`` 升级为强校验。
    - .env.example 中 ``# VAR=...`` 形式的 commented-out 行也算"已声明"
      — Plan-r3 P1-4 把 4 个 legacy var (GPT5NANO_API_KEY 等) 注释化保留,
      不是删除, 这样旧调用方 (scripts/audit/_replan_v5_evidence/*) 仍能
      被覆盖.
    - 间接引用扫描仅看 .env.example 中**未注释**的赋值行 (commented-out
      行的间接引用语义上是"模板示意", 不强制可解析).
    """
    import re
    yaml_dir = os.path.join(project_root, 'config')
    env_example = os.path.join(project_root, '.env.example')
    if not os.path.isdir(yaml_dir) or not os.path.isfile(env_example):
        return

    placeholder_re = re.compile(r'\$\{([A-Z_][A-Z0-9_]*)\}')

    # 阶段 1: yaml 中所有 ${VAR}
    placeholders: set[str] = set()
    for fname in os.listdir(yaml_dir):
        if not fname.endswith('.yaml'):
            continue
        try:
            with open(os.path.join(yaml_dir, fname), 'r', encoding='utf-8') as f:
                txt = f.read()
        except OSError:
            continue
        placeholders.update(placeholder_re.findall(txt))

    # 阶段 2: .env.example 解析 (含 commented-out 也算声明)
    declared: set[str] = set()
    indirect_refs: set[str] = set()
    decl_re = re.compile(r'^\s*#?\s*([A-Z_][A-Z0-9_]*)\s*=', re.MULTILINE)
    # 仅未注释行的 KEY=${OTHER} 才算 production-binding 的间接引用
    indirect_re = re.compile(
        r'^\s*([A-Z_][A-Z0-9_]*)\s*=\s*[^#\n]*\$\{([A-Z_][A-Z0-9_]*)\}',
        re.MULTILINE
    )
    try:
        with open(env_example, 'r', encoding='utf-8') as f:
            ex_text = f.read()
    except OSError:
        return
    declared.update(decl_re.findall(ex_text))
    for _key, ref in indirect_re.findall(ex_text):
        indirect_refs.add(ref)

    logger = logging.getLogger(__name__)

    # warning 1: yaml 引用未在 .env.example 声明
    undeclared = placeholders - declared
    if undeclared:
        logger.warning(
            "yaml 中引用的环境变量未在 .env.example 中声明: %s. "
            "请在 .env.example 中加入声明 (即使 value 留空) 以满足部署契约; "
            "或检查 yaml 中的 ${%s} 是否拼写错误。",
            sorted(undeclared), next(iter(undeclared))
        )

    # warning 2 (round-3 review R5): .env.example 间接引用未声明且 os.environ 也无
    indirect_missing = {
        ref for ref in indirect_refs
        if ref not in declared and not os.environ.get(ref)
    }
    if indirect_missing:
        logger.warning(
            ".env.example 中 KEY=${%s} 形式的间接引用既未声明也未在 os.environ "
            "中设置: %s. 复制 .env.example -> .env 后这些间接引用会展开为空字符串, "
            "导致 LLM/Embedding 调用 401 等 silent failure. 请确保被引用的 var "
            "在 .env / os.environ 中有值.",
            next(iter(indirect_missing)), sorted(indirect_missing)
        )


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
