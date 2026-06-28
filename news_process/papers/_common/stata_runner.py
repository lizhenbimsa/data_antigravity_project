"""news_process.papers._common.stata_runner — 调用本地 Stata 执行 .do 文件.

设计原则
--------
- **零代码侵入**: 现有 ``.do`` 文件不需要任何改造; 本模块仅做进程调度。
- **可发现 / 可覆盖**: Stata 可执行路径优先级
    1. 函数参数 ``stata_bin``
    2. 环境变量 ``NEWS_PROCESS_STATA_BIN``
    3. 自动探测 (Windows: StataMP/SE/IC.exe; Linux/Mac: stata-mp/se/ic)
- **超时与错误**: ``timeout`` 默认 30 分钟, 超时或非零退出抛出
   带清晰诊断信息的异常。
- **可测**: ``stata_bin`` 是显式参数, 单测可注入虚拟可执行路径。
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Sequence


class StataNotFoundError(RuntimeError):
    """无法定位本地 Stata 可执行文件时抛出."""


# Stata 可执行候选名 — 按"专业版/标准版/初级版"优先级递减.
_STATA_CANDIDATES_WINDOWS = (
    'StataMP-64.exe', 'StataMP.exe',
    'StataSE-64.exe', 'StataSE.exe',
    'StataIC-64.exe', 'StataIC.exe',
    'Stata-64.exe', 'Stata.exe',
)
_STATA_CANDIDATES_UNIX = (
    'stata-mp', 'stata-se', 'stata-ic', 'stata',
)


def _is_windows() -> bool:
    return os.name == 'nt'


def _candidates() -> tuple[str, ...]:
    return _STATA_CANDIDATES_WINDOWS if _is_windows() else _STATA_CANDIDATES_UNIX


def discover_stata_bin() -> str | None:
    """探测系统上的 Stata 可执行路径; 找不到返回 ``None``.

    优先级:
        1. 环境变量 ``NEWS_PROCESS_STATA_BIN``
        2. shutil.which() 在 PATH 中按候选名查找
        3. Windows 常见安装目录 (Program Files\\Stata*)
    """
    env_path = os.environ.get('NEWS_PROCESS_STATA_BIN')
    if env_path and os.path.exists(env_path):
        return env_path

    for cand in _candidates():
        found = shutil.which(cand)
        if found:
            return found

    if _is_windows():
        for prog_files in (
            os.environ.get('ProgramFiles', r'C:\Program Files'),
            os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)'),
        ):
            if not prog_files or not os.path.isdir(prog_files):
                continue
            try:
                for sub in os.listdir(prog_files):
                    if sub.lower().startswith('stata'):
                        sub_dir = os.path.join(prog_files, sub)
                        for cand in _candidates():
                            cand_path = os.path.join(sub_dir, cand)
                            if os.path.exists(cand_path):
                                return cand_path
            except OSError:
                pass

    return None


# ── W11 (2026-06-25): run_do 内容寻址跳过 (默认关; 编排层不进 40_panel = golden-safe) ──
def _rundo_log_path(do_path: Path) -> Path:
    """Stata ``/b do foo.do`` 写的 log 是 ``foo.log`` (去 .do 扩展, 见 scripts/run_stata.ps1)。
    ⚠ 历史易错点 (CF-3): 不是 ``foo.do.log``。"""
    return do_path.with_suffix(".log")


def _rundo_sidecar(do_path: Path) -> Path:
    """跳过 stamp 落 .do 同目录的 ``_rundo_cache/`` 下 (不污染 stata_templates 源树)。"""
    return do_path.parent / "_rundo_cache" / f"{do_path.stem}.skipstamp.json"


def _stata_fingerprint(bin_path: str) -> str:
    """Stata 可执行的轻量指纹 (name|size|mtime; 不启 GUI 探版本, 符合 CLAUDE.md /b 铁律)。
    git checkout / 重装改 mtime → 保守失效 (多重跑, 绝不误命中旧结果)。"""
    try:
        st = Path(bin_path).stat()
        return f"{Path(bin_path).name}|{st.st_size}|{int(st.st_mtime)}"
    except OSError:
        return f"{Path(bin_path).name}|?"


def _rundo_skip_key(do_path: Path, data_deps, bin_path: str, args=None) -> str:
    """内容寻址键 = sha256(do 内容 + 各 .dta 内容 + Stata 指纹 + 传入 args)。复用 data_versioning 同源 helper。"""
    from news_process.core.data_versioning import compute_config_hash, compute_file_hash
    payload = {
        "do": compute_file_hash(do_path),
        "dta": {Path(p).name: compute_file_hash(p) for p in (data_deps or []) if Path(p).exists()},
        "stata": _stata_fingerprint(bin_path),
        # F9 (2026-06-26): args 入键 — 同 .do+.dta 但不同 args (do 内经 `args` 宏读取) 不应误命中跳过。
        "args": [str(a) for a in (args or [])],
    }
    return compute_config_hash(payload)


def run_do(do_path: str | Path,
           args: Sequence[str] | None = None,
           *,
           stata_bin: str | None = None,
           cwd: str | Path | None = None,
           timeout: int = 1800,
           batch_mode: bool = True,
           check: bool = True,
           skip_if_unchanged: bool = False,
           data_deps: Sequence[str | Path] | None = None) -> subprocess.CompletedProcess:
    """执行单个 .do 文件.

    Args:
        do_path:     ``.do`` 文件绝对/相对路径。
        args:        传给 .do 的命令行参数 (在 .do 中通过 ``args`` 宏访问)。
        stata_bin:   覆盖 Stata 可执行路径; 为 None 时调用 ``discover_stata_bin()``。
        cwd:         子进程工作目录; 默认是 ``do_path`` 所在目录
                     (.do 中的相对路径才能找到对应数据文件)。
        timeout:     秒, 默认 30 分钟。
        batch_mode:  使用 ``/b`` 批处理模式 (Windows) 或 ``-b`` (Unix)。
        check:       True (默认) 时非零退出抛 CalledProcessError。

    Returns:
        subprocess.CompletedProcess。

    Raises:
        StataNotFoundError:           没找到 Stata 可执行文件。
        FileNotFoundError:            do_path 不存在。
        subprocess.TimeoutExpired:    超时。
        subprocess.CalledProcessError: ``check=True`` 时进程非零退出。
    """
    do_path = Path(do_path).resolve()
    if not do_path.exists():
        raise FileNotFoundError(f"do 文件不存在: {do_path}")

    bin_path = stata_bin or discover_stata_bin()
    if bin_path is None:
        raise StataNotFoundError(
            "未能定位 Stata 可执行文件. 请通过 stata_bin 参数显式指定, "
            "或设置环境变量 NEWS_PROCESS_STATA_BIN, "
            f"或将以下任一文件加入 PATH: {_candidates()}"
        )

    # W11: 内容寻址跳过 (默认关; 仅当 skip_if_unchanged 且调用方显式传 data_deps 才生效 —
    # 没有数据依赖就无法验证, 保守不跳)。命中需 stamp + log 同在且 key 匹配。
    sidecar = _rundo_sidecar(do_path)
    if skip_if_unchanged and data_deps is not None:
        cur_key = _rundo_skip_key(do_path, data_deps, bin_path, args)
        if sidecar.exists() and _rundo_log_path(do_path).exists():
            try:
                rec = json.loads(sidecar.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                rec = {}
            if rec.get("key") == cur_key:
                return subprocess.CompletedProcess(
                    args=["<skipped:rundo-unchanged>", str(do_path)],
                    returncode=0, stdout="", stderr="",
                )

    if cwd is None:
        cwd = do_path.parent

    batch_flag = '/b' if _is_windows() else '-b'
    cmd: list[str] = [bin_path]
    if batch_mode:
        cmd.append(batch_flag)
    cmd.append('do')
    cmd.append(str(do_path))
    if args:
        cmd.extend(str(a) for a in args)

    cp = subprocess.run(
        cmd,
        cwd=str(cwd),
        timeout=timeout,
        check=check,
        capture_output=True,
        text=True,
    )
    # W11: 成功后写跳过 stamp (供下次 skip_if_unchanged 命中)。
    if skip_if_unchanged and data_deps is not None and cp.returncode == 0:
        try:
            sidecar.parent.mkdir(parents=True, exist_ok=True)
            sidecar.write_text(
                json.dumps({"key": _rundo_skip_key(do_path, data_deps, bin_path, args)}),
                encoding="utf-8",
            )
        except OSError:
            pass
    return cp


# ============================================================================
# v3.2.0 M7 (plan v14 §9.3): build_replication_package
# ============================================================================

# Plan v14 §9.2 已知占位符白名单 (与 test_stata_templates.py 同源).
# P1 (2026-05-15) 扩展: 增加 Tier 2 (paper-level) + Tier 3 (paper-specific)
# 占位符以支持 4 个衍生论文 (benefit_society / brokerage_network /
# strategic_diff / llm_peer) 各自独立的 template 套件. 主线 bank_fintech_tone
# 行为保持完全不变 — 仍只验证 MAIN_LOCUS_TRACK / MAIN_SUBST_TRACK /
# MAIN_SENT_TRACK / PROJECT_ROOT 四项.
_KNOWN_PLACEHOLDERS_MAIN = {
    'MAIN_LOCUS_TRACK',  # lf / lc
    'MAIN_SUBST_TRACK',  # sf / sc
    'MAIN_SENT_TRACK',   # 三轨 (full / ctx / ss); ss = 银行+金科同句共现轨
    'PROJECT_ROOT',      # 绝对路径
}

# Tier 2: paper-level (5 paper 共用, 但每个 paper 取不同默认值)
_KNOWN_PLACEHOLDERS_PAPER_LEVEL = {
    'PAPER_ID',
    'MAIN_DV',           # 规范因变量 (canonical dependent variable)
    'CONTROLS',           # 标准控制变量集 (字符串)
    'CLUSTER_VAR',        # vce(cluster <var>) 的聚类变量
    'HET_VAR',            # 异质性交互变量
    # v3.7.3 Plan A v1.0: paper 级主 treatment 占位符 (供 B-route
    # paper-specific 模板使用)。
    'MAIN_TREAT',         # 主 treatment 变量 (随 paper 而异, 如 P1 = llm_vote_tone_full)
}

# Tier 3: paper-specific (稀疏占位符, 仅需要它的 paper 使用)
_KNOWN_PLACEHOLDERS_PAPER_SPECIFIC = {
    # benefit_society (v3.2.1 起三轨 full/ctx/ss — plan v2.12 双轨基础上
    # 2026-06-14 加入 ss 银行+金科同句共现轨, 与 full/ctx 并列第三主轨)
    'ATTITUDE_VAR',      # 别名 = ATTITUDE_FULL (向后兼容)
    'ATTITUDE_FULL', 'ATTITUDE_CTX',
    'ATTITUDE_SS',       # 第三轨 (银行+金科同句); = ATTITUDE_CTX 的 _ctx→_ss 机械镜像
    'BENEFIT_POS_FRAC_FULL', 'BENEFIT_POS_FRAC_CTX', 'BENEFIT_POS_FRAC_SS',
    'BENEFIT_NEG_FRAC_FULL', 'BENEFIT_NEG_FRAC_CTX', 'BENEFIT_NEG_FRAC_SS',
    'MECHANISM_TOKEN', 'MECHANISM_HIDDEN', 'MECHANISM_SUBST',
    'ROBUSTNESS_DV', 'BOOTSTRAP_REPS', 'RANDOM_SEED',
    # benefit_society 22_tableA9_external_validation 外部效度占位符
    # (derivative_replication.py:111-113 defaults; J-L-M 2026 RFS §3 G4)。
    # 此前漏登记 → build_replication 在 _validate_spec_choices 抛"未知占位符"
    # (980daf74 起潜伏)。三列均为外部财务/监管 sentinel, 模板 capture confirm 守卫。
    'EXT_Y1', 'EXT_Y2', 'EXT_Y3',
    # brokerage_network
    'MAIN_ENDOG', 'MAIN_IV', 'TREATMENT_DCEP', 'TREATMENT_SANDBOX',
    'CENTRALITY_BTW', 'CENTRALITY_CONS', 'CENTRALITY_BROKER',
    # network-roles 多角色化 (network-metrics-elevation 2026-06-13): 主/次/中介中心度 +
    # 跨族第二工具 (over-id) + 网络异质性分组; default 值见 derivative_replication.py:141-146。
    # reaudit-t18-2026-06-15: 此前漏登记 → brokerage build-replication 抛"未知占位符"
    # (烟雾 §四.6); 模板 16/17/19/20 已用, 补登记使全 11 篇可打包。
    'PRIMARY_CENT', 'SECONDARY_CENT', 'MEDIATOR_CENT', 'MOD_CENT', 'OVERID_IV2', 'NET_HET_VAR',
    # strategic_diff
    'MAIN_DIFF_VAR', 'FLUIDITY_VAR', 'SIM_MAX_VAR',
    'BARTIK_IV', 'TONE_VAR', 'COHERENCE_VAR',
    # llm_peer
    'LLM_PEER_IV', 'LLM_PEER_COVERAGE_IV', 'COMPETE_IDX', 'CUTOFF_VARS',
    # (TONE_VAR 与 strategic_diff 共用)
    # 第三轨 ss (银行+金科同句共现, 2026-06-14): strategic_diff / llm_peer 两篇
    # 2SLS 论文的 TONE_VAR ss 镜像 (= TONE_VAR 的 _full→_ss 机械镜像); 全平价
    # 覆盖, 见 THIRD_TRACK_SAME_SENTENCE_PLAN_2026-06-14.md §7.3-A2。
    'TONE_VAR_SS',
}

# 并集 — 任何模板可合法引用的占位符超集。
_KNOWN_PLACEHOLDERS = (
    _KNOWN_PLACEHOLDERS_MAIN
    | _KNOWN_PLACEHOLDERS_PAPER_LEVEL
    | _KNOWN_PLACEHOLDERS_PAPER_SPECIFIC
)

_VALID_SPEC_VALUES = {
    'MAIN_LOCUS_TRACK': {'lf', 'lc'},
    'MAIN_SUBST_TRACK': {'sf', 'sc'},
    # 第三轨 'ss' (银行+金科同句共现) 2026-06-14 加入: 与 full/ctx 并列第三主
    # 情感轨; 全平价覆盖 (见 scripts/audit/THIRD_TRACK_SAME_SENTENCE_PLAN_2026-06-14.md
    # §⑩/§7.3-A2)。模板 foreach sent in full ctx ss 第 3 列以 capture confirm 守卫。
    'MAIN_SENT_TRACK':  {'full', 'ctx', 'ss'},
}

# P1 (2026-05-15): paper_id 白名单 — 与 paper_config._VALID_PAPER_IDS 同步.
# RR8-1 (Review-only audit): 单一可信源 = paper_registry.PAPER_IDS_ALL; 修复
# 原 hardcoded 5-paper drift (RR1-1 fix paper_config + RR7-1 fix
# derivative_replication, 此处是第 3 处 drift). 任何 paper 增删只需改
# paper_registry.PAPER_IDS_ALL 一处.
from news_process.papers._common.paper_registry import (
    PAPER_IDS_ALL as _STATA_RUNNER_PAPER_IDS_ALL,
)

_VALID_PAPER_IDS_BUILD = frozenset(_STATA_RUNNER_PAPER_IDS_ALL)

# Paper 默认占位符值 (项目约定: 银行年度面板 + ROA + reghdfe + cluster bank_id).
# Q1.4 (2026-05-15) 单源化: 4 衍生 paper 的字典 import 自
# derivative_replication._PAPER_DEFAULTS (single source of truth); 本字典只
# 保留 bank_fintech_tone 主线条目, 再 ``**`` 展开衍生字典合并.
# 修改任何衍生 paper 的 default 只需改 derivative_replication.py 一处.
from news_process.papers._common.derivative_replication import (
    _PAPER_DEFAULTS as _DERIVATIVE_PAPER_DEFAULTS,
)

_PAPER_DEFAULTS: dict[str, dict[str, str]] = {
    'bank_fintech_tone': {
        'PAPER_ID': 'bank_fintech_tone',
        'MAIN_DV': 'ROA',
        'CONTROLS': 'ln_news_coverage media_breadth_z fin_media_frac central_media_frac',
        'CLUSTER_VAR': 'bank_id',
        'HET_VAR': 'is_soe',
        # MAIN_TREAT/RANDOM_SEED: paper-level placeholder 默认值。P1 主线用根目录模板,
        # 不引用这两个 placeholder (原引用它们的根级 _title 稳健性模板 25_tableA8_title_robustness.do.tmpl
        # 已随 remove-title-track 删除), 故对 P1 为无害默认值; 该 placeholder 机制仍被
        # attention/locus/substance/collab 等子目录模板消费。
        # P1 main = _full (full-only gating 2026-06-29; _ctx 降为 robustness 孪生).
        'MAIN_TREAT': 'llm_vote_tone_full',
        'RANDOM_SEED': '20260516',
    },
    **_DERIVATIVE_PAPER_DEFAULTS,
}


# Q1.4 (2026-05-15): commit-hash helper 已移至 _git_utils.py。
# 此处 re-export, 兼容仍按旧路径 import 的外部调用方。
from news_process.papers._common._git_utils import (  # noqa: E402
    _get_git_commit_hash_with_dirty,
)


def _validate_spec_choices(main_spec_choices: dict,
                           paper_id: str = 'bank_fintech_tone') -> None:
    """Plan v14 §9.3: 校验 main spec 选择合法 (避免静默错误占位符).

    Args:
        main_spec_choices: 用户提供的占位符字典 (paper defaults 已合并).
        paper_id:          论文标识. 'bank_fintech_tone' (默认) 要求 main-paper
                           三轨化必需占位符; 其它 paper 跳过该要求 (走自己的
                           defaults).
    """
    if paper_id not in _VALID_PAPER_IDS_BUILD:
        raise ValueError(
            f"未知 paper_id={paper_id!r}. 合法值: {sorted(_VALID_PAPER_IDS_BUILD)}"
        )

    for key, value in main_spec_choices.items():
        if key not in _KNOWN_PLACEHOLDERS:
            raise ValueError(
                f"未知占位符 key='{key}'. 合法值: {sorted(_KNOWN_PLACEHOLDERS)}"
            )
        if key in _VALID_SPEC_VALUES and value not in _VALID_SPEC_VALUES[key]:
            raise ValueError(
                f"占位符 {key}='{value}' 非法. 合法值: {sorted(_VALID_SPEC_VALUES[key])}"
            )

    # 主线论文必须提供三轨化 spec; 衍生 paper 无此要求 (走 _PAPER_DEFAULTS).
    if paper_id == 'bank_fintech_tone':
        required = {'MAIN_LOCUS_TRACK', 'MAIN_SUBST_TRACK', 'MAIN_SENT_TRACK'}
        missing = required - set(main_spec_choices.keys())
        if missing:
            raise ValueError(f"缺必需占位符: {sorted(missing)}")


def _substitute_placeholders(content: str, choices: dict) -> str:
    """{{KEY}} → value 直接替换.

    Args:
        content: 模板文件内容
        choices: 占位符值字典
    Returns:
        替换后内容; 未替换的 {{...}} 抛 ValueError (fail-fast)

    白话: 模板 .do.tmpl 里写的是 {{MAIN_DV}} 这类双花括号坑位, 这里逐个
    用真实变量名填进去; 填完若还剩任何 {{...}} 没填上, 说明模板引用了
    未登记的占位符或调用方漏传值, 立即报错而不是生成一个跑不动的 .do。
    """
    result = content
    for key, value in choices.items():
        result = result.replace(f'{{{{{key}}}}}', str(value))
    # fail-fast: 检测残留未替换占位符
    import re
    leftover = re.findall(r'\{\{([A-Z_]+)\}\}', result)
    if leftover:
        raise ValueError(
            f"占位符未替换完整, 残留: {set(leftover)}. "
            f"检查 _KNOWN_PLACEHOLDERS 与 main_spec_choices 一致性."
        )
    return result


def build_replication_package(
    main_spec_choices: dict | None = None,
    output_root: str | Path | None = None,
    template_dir: str | Path | None = None,
    *,
    paper_id: str = 'bank_fintech_tone',
) -> Path:
    """生成 v3.2.0 replication 包 (plan v14 §9.3, Action #9 Stata Recommended scope).

    Args:
        main_spec_choices: 占位符覆盖字典. 主线论文 (paper_id='bank_fintech_tone')
                           必须提供 MAIN_LOCUS_TRACK/MAIN_SUBST_TRACK/MAIN_SENT_TRACK;
                           衍生 paper 可为空 dict / None (使用 _PAPER_DEFAULTS).
                           PROJECT_ROOT 永远可被覆盖.
        output_root:       replication 包父目录 (默认 repo_root).
        template_dir:      模板目录. 默认按 paper_id 解析:
                           - main: papers/_common/stata_templates/
                           - 其它: papers/_common/stata_templates/<paper_id>/
        paper_id:          论文标识. P1 (2026-05-15) 新增, default 主线论文保持
                           历史行为不变.

    Returns:
        生成的 replication 包目录路径.

    工作流:
        1. 与 _PAPER_DEFAULTS[paper_id] 合并占位符 (user 覆盖默认)
        2. 校验 main_spec_choices (paper-aware: 主线要求三轨, 衍生不要求)
        3. 实例化目录 replication_v3.2.0_{<paper>_}<locus>_<subst>_<sent>/
        4. 复制 / 替换 .do.tmpl → .do
        5. 写 README.md 含 git commit hash + dirty 检测
    """
    if paper_id not in _VALID_PAPER_IDS_BUILD:
        raise ValueError(
            f"未知 paper_id={paper_id!r}. 合法值: {sorted(_VALID_PAPER_IDS_BUILD)}"
        )

    # 合并: defaults → user overrides
    user_choices = dict(main_spec_choices or {})
    effective_choices: dict = dict(_PAPER_DEFAULTS.get(paper_id, {}))
    effective_choices.update(user_choices)

    _validate_spec_choices(effective_choices, paper_id=paper_id)

    if template_dir is None:
        base = Path(__file__).resolve().parent / 'stata_templates'
        if paper_id == 'bank_fintech_tone':
            template_dir = base
        elif (base / paper_id).is_dir():
            template_dir = base / paper_id
        else:
            # reaudit-t18-2026-06-15: provisional 两篇 (bank_media_disagreement /
            # bank_news_clarity) 模板在 papers/<paper_id>/stata_templates/ (不在 _common 下,
            # 见 CLAUDE.md "不计入 142")。回退到该路径使全 11 篇均可 build-replication。
            papers_dir = Path(__file__).resolve().parent.parent  # papers/
            template_dir = papers_dir / paper_id / 'stata_templates'
    template_dir = Path(template_dir)
    if not template_dir.is_dir():
        raise FileNotFoundError(f"Template dir not found: {template_dir}")

    if output_root is None:
        output_root = Path(__file__).resolve().parents[3]
    output_root = Path(output_root)

    # 衍生 paper 没有 locus/subst/sent triad → package 名以 paper_id 命名.
    if paper_id == 'bank_fintech_tone':
        locus = effective_choices['MAIN_LOCUS_TRACK']
        subst = effective_choices['MAIN_SUBST_TRACK']
        sent  = effective_choices['MAIN_SENT_TRACK']
        pkg_name = f'replication_v3.2.0_{locus}_{subst}_{sent}'
    else:
        pkg_name = f'replication_v3.2.0_{paper_id}'

    pkg_dir = output_root / pkg_name
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / 'code').mkdir(exist_ok=True)
    (pkg_dir / 'data').mkdir(exist_ok=True)
    (pkg_dir / 'output' / 'tables').mkdir(parents=True, exist_ok=True)
    (pkg_dir / 'output' / 'figures').mkdir(parents=True, exist_ok=True)

    # 实例化模板 .do.tmpl → .do
    n_templates = 0
    for tpl_path in sorted(template_dir.glob('*.do.tmpl')):
        out_name = tpl_path.stem  # 去掉 .tmpl 后缀, e.g., 11_table2_main_m1m6.do
        out_path = pkg_dir / 'code' / out_name
        content = tpl_path.read_text(encoding='utf-8')
        substituted = _substitute_placeholders(content, effective_choices)
        out_path.write_text(substituted, encoding='utf-8')
        n_templates += 1

    # 复制 README.md (附加 spec choices + commit hash)
    readme_src = template_dir / 'README.md'
    commit_hash = _get_git_commit_hash_with_dirty()
    if readme_src.exists():
        readme_content = readme_src.read_text(encoding='utf-8')
        if paper_id == 'bank_fintech_tone':
            appendix = f"""

---

## This replication package / 本复现包

- **Generated at**: {commit_hash}
- **Main spec choices** (locked at generation):
  - locus track: `{locus}` ({'full-text' if locus == 'lf' else 'entity-context'} classification)
  - subst track: `{subst}` ({'full-text' if subst == 'sf' else 'entity-context'} classification)
  - sent track:  `{sent}` ({'Hassan 2019 QJE entity-proximity' if sent == 'ctx' else 'bank+fintech same-sentence co-occurrence' if sent == 'ss' else 'full-text'})
- **Templates instantiated**: {n_templates}
- **Plan version**: v14 (62 rounds audit; user confirmed 9 Action Items)
"""
        else:
            # 衍生 paper: 无主线 triad (locus/subst/sent); 报告 paper_id + 关键默认值。
            keys_used = sorted(effective_choices.keys())
            appendix = f"""

---

## This replication package / 本复现包

- **Generated at**: {commit_hash}
- **Paper**: `{paper_id}`
- **MAIN_DV**: `{effective_choices.get('MAIN_DV', '?')}`
- **CLUSTER_VAR**: `{effective_choices.get('CLUSTER_VAR', '?')}`
- **CONTROLS**: `{effective_choices.get('CONTROLS', '?')}`
- **Placeholders bound** ({len(keys_used)}): {', '.join(keys_used)}
- **Templates instantiated**: {n_templates}
- **Plan version**: v14 + P1 (2026-05-15 derivative-paper extension)
"""
        (pkg_dir / 'README.md').write_text(readme_content + appendix, encoding='utf-8')

    return pkg_dir


__all__ = [
    'StataNotFoundError',
    'discover_stata_bin',
    'run_do',
    'build_replication_package',
    '_validate_spec_choices',  # 测试可见
    '_substitute_placeholders',
]


# ============================================================================
# v3.2.0 M7 CLI: python -m news_process.papers._common.stata_runner build-replication
# ============================================================================

def _cli_build_replication(args) -> int:
    """CLI 子命令: build-replication --locus lc --subst sf --sent ctx --root /path

    P1 (2026-05-15): 增 --paper 选项. 默认 'bank_fintech_tone' 保持历史行为
    完全不变. 其它 paper 时 --locus/--subst/--sent 可省 (取 _PAPER_DEFAULTS).
    """
    import sys
    paper_id = getattr(args, 'paper', None) or 'bank_fintech_tone'
    choices: dict = {
        'PROJECT_ROOT': str(Path(args.root).resolve()),
    }
    # 主线必填 triad; 衍生 paper 可省 (用 defaults).
    if paper_id == 'bank_fintech_tone':
        if not (args.locus and args.subst and args.sent):
            sys.stderr.write(
                "[ERROR] paper=bank_fintech_tone requires --locus/--subst/--sent.\n"
            )
            return 1
        choices['MAIN_LOCUS_TRACK'] = args.locus
        choices['MAIN_SUBST_TRACK'] = args.subst
        choices['MAIN_SENT_TRACK']  = args.sent
    else:
        # 可选覆盖 (衍生 paper 很少用到; 大多数情况不传)。
        if args.locus: choices['MAIN_LOCUS_TRACK'] = args.locus
        if args.subst: choices['MAIN_SUBST_TRACK'] = args.subst
        if args.sent:  choices['MAIN_SENT_TRACK']  = args.sent
    try:
        pkg = build_replication_package(
            main_spec_choices=choices,
            output_root=Path(args.root).parent if args.root != '.' else None,
            paper_id=paper_id,
        )
    except (ValueError, FileNotFoundError) as e:
        sys.stderr.write(f"[ERROR] build_replication_package failed: {e}\n")
        return 1
    # 用 ASCII 输出避免 Windows GBK 控制台 UnicodeError;
    # 中文与 emoji 仅出现在文件内容 (UTF-8), 不在 stdout
    import sys
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass  # python 3.7+ 才有 reconfigure; 失败则 fallback
    print(f"[OK] Replication package: {pkg}")
    print(f"   - code/: {len(list((pkg / 'code').glob('*.do')))} Stata .do files")
    print(f"   - data/: copy 46_panel_yearly_*.dta from data/processed/ here")
    print(f"   - output/: tables/ + figures/ (generated after Stata run)")
    print(f"\nNext steps:")
    print(f"   cd {pkg}")
    print(f"   {'StataMP-64.exe /b' if _is_windows() else 'stata-mp -b'} do code/00_master.do")
    return 0


def _cli_list_templates(args) -> int:
    """CLI 子命令: list-templates — 列举 Stata 模板清单 (plan v14 §9.2)."""
    template_dir = Path(__file__).resolve().parent / 'stata_templates'
    if not template_dir.is_dir():
        print(f"[ERROR] Template dir not found: {template_dir}")
        return 1
    try:
        import sys
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass

    templates = sorted(template_dir.glob('*.do.tmpl'))
    print(f"news_process v3.2.0 Stata templates ({len(templates)} 个, plan v14 §9.2):")
    print()
    for tpl in templates:
        # 读首 3 行注释作为 description
        with open(tpl, encoding='utf-8') as f:
            head = []
            for line in f:
                line = line.rstrip()
                if line.startswith('*') and 'version' not in line.lower():
                    head.append(line.lstrip('* '))
                if len(head) >= 2:
                    break
        desc = head[0] if head else '(no description)'
        print(f"  {tpl.name}")
        print(f"     {desc}")
    print()
    if args.verbose:
        # 加占位符使用情况
        print("Placeholders inventory:")
        for ph in sorted(_KNOWN_PLACEHOLDERS):
            usage_count = sum(
                ('{{' + ph + '}}') in tpl.read_text(encoding='utf-8')
                for tpl in templates
            )
            print(f"  {{{{{ph}}}}}: used in {usage_count}/{len(templates)} templates")
    return 0


def _cli_verify_replication(args) -> int:
    """CLI 子命令: verify-replication — 验证 replication 包结构完整性.

    检查:
        1. 目录结构 (code/ data/ output/{tables,figures}/)
        2. 19 .do 文件全部存在
        3. 各 .do 无占位符残留 ({{ / }})
        4. README.md 含 spec 信息 + commit hash
        5. master.do 引用所有子 .do
    """
    try:
        import sys
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass

    pkg_dir = Path(args.path).resolve()
    if not pkg_dir.is_dir():
        print(f"[ERROR] Not a directory: {pkg_dir}")
        return 1

    n_ok = 0
    n_err = 0
    print(f"news_process v3.2.0 verify-replication: {pkg_dir.name}")
    print("=" * 60)

    # 1. 目录结构
    print("\n[1/5] 目录结构")
    for sub in ['code', 'data', 'output/tables', 'output/figures']:
        if (pkg_dir / sub).is_dir():
            print(f"   [OK] {sub}/")
            n_ok += 1
        else:
            print(f"   [ERR] {sub}/ 缺失")
            n_err += 1

    # 2. 19 .do 文件 (remove-title-track 后 14; 2026-06-13 IV 补全 +25_tableA6 → 15;
    #    agg-toptier-audit 2026-06-13 +26_tableA7_aggregation_robustness → 16;
    #    2026-06-14 顶刊稳健性扩充 +32_tableA8_fe_saturation_robust_est +33_tableA9_subsample_timing → 18;
    #    2026-06-14 T18 重审 era-stability 族 +34_tableA11_era_stability → 19)
    _EXPECTED_ROOT_DO = 19
    print(f"\n[2/5] Stata .do 文件 ({_EXPECTED_ROOT_DO} expected)")
    code_dir = pkg_dir / 'code'
    if code_dir.is_dir():
        do_files = sorted(code_dir.glob('*.do'))
        if len(do_files) == _EXPECTED_ROOT_DO:
            print(f"   [OK] {len(do_files)} .do files ({_EXPECTED_ROOT_DO}/{_EXPECTED_ROOT_DO} 完整)")
            n_ok += 1
        else:
            print(f"   [ERR] {len(do_files)} .do files (expected {_EXPECTED_ROOT_DO})")
            n_err += 1

    # 3. 占位符残留检测
    print("\n[3/5] 占位符 ({{...}}) 残留检测")
    if code_dir.is_dir():
        residue = []
        for do_file in code_dir.glob('*.do'):
            content = do_file.read_text(encoding='utf-8')
            if '{{' in content or '}}' in content:
                residue.append(do_file.name)
        if not residue:
            print("   [OK] 所有 .do 文件占位符零残留")
            n_ok += 1
        else:
            print(f"   [ERR] 占位符残留: {residue}")
            n_err += 1

    # 4. README.md
    print("\n[4/5] README.md")
    readme = pkg_dir / 'README.md'
    if readme.exists():
        content = readme.read_text(encoding='utf-8')
        has_spec = 'locus track' in content or 'Main spec' in content
        has_hash = 'Generated at' in content
        if has_spec and has_hash:
            print("   [OK] README 含 spec choices + commit hash")
            n_ok += 1
        else:
            print(f"   [ERR] README 缺关键 section (spec={has_spec}, hash={has_hash})")
            n_err += 1
    else:
        print("   [ERR] README.md 不存在")
        n_err += 1

    # 5. master.do 引用 18 子 .do (remove-title-track 后 13; 2026-06-13 IV 补全
    #    +25_tableA6_tone_iv_2sls → 14; agg-toptier-audit +26_tableA7_aggregation_robustness → 15;
    #    2026-06-14 顶刊稳健性扩充 +32_tableA8 +33_tableA9 → 17;
    #    2026-06-14 T18 重审 era-stability +34_tableA11_era_stability → 18)
    print("\n[5/5] master.do 引用 18 子 .do")
    master = code_dir / '00_master.do'
    if master.exists():
        content = master.read_text(encoding='utf-8')
        expected = [
            '01_data_prep.do', '10_table1_descriptives.do',
            '11_table2_main_m1m6.do', '12_table3_mechanism.do',
            '13_table4_heterogeneity.do', '14_table5_advanced_robustness.do',
            '20_tableA1_inter_track_kappa.do', '21_tableA2_main_spec_switch.do',
            '22_tableA3_bartik_iv.do', '23_tableA4_radius_sensitivity.do',
            '24_tableA5_dictionary_method.do', '25_tableA6_tone_iv_2sls.do',
            '26_tableA7_aggregation_robustness.do',
            '32_tableA8_fe_saturation_robust_est.do',
            '33_tableA9_subsample_timing.do',
            '34_tableA11_era_stability.do',
            '30_figure1_event_study.do', '31_figure_coefplot_dual.do',
        ]
        missing = [s for s in expected if s not in content]
        if not missing:
            print(f"   [OK] master.do 引用 18/18 子 .do")
            n_ok += 1
        else:
            print(f"   [ERR] master.do 缺引用: {missing}")
            n_err += 1
    else:
        print("   [ERR] master.do 不存在")
        n_err += 1

    print("\n" + "=" * 60)
    print(f"  Summary: {n_ok} OK / {n_err} ERR")
    if n_err:
        print(f"  Action: 重新跑 build-replication --locus ... --root {pkg_dir.name}")
        return 1
    print("  Replication package is valid and ready for Stata execution.")
    return 0


# reaudit-t18-2026-06-15: doctor [6/6] Stata ado 检查所需 — 顶刊稳健性/复现必装包清单。
# 用途: 外部复现者在自己机器跑 `doctor` 即知须 ssc install 哪些包 (空跑稳健性的根因之一)。
_REQUIRED_STATA_ADOS = {
    # name: (purpose, install_cmd)
    'reghdfe':            ('高维固定效应回归 (主回归引擎)', 'ssc install reghdfe'),
    'ftools':             ('reghdfe Mata 依赖', 'ssc install ftools'),
    'require':            ('reghdfe 依赖管理 (新版 reghdfe/ivreghdfe 必需)', 'ssc install require'),
    'ivreghdfe':          ('HDFE 2SLS (IV 主路径)', 'ssc install ivreghdfe'),
    'ivreg2':             ('2SLS + KP F / Hansen J (IV 回退路径)', 'ssc install ivreg2'),
    'weakiv':             ('弱工具 Anderson-Rubin CI (audit IV-2)', 'ssc install weakiv'),
    'boottest':           ('野聚类自助法 wild bootstrap (小 G 推断, audit INFER-3)', 'ssc install boottest'),
    'rwolf':              ('Romano-Wolf FWER 校正 (audit INFER-1)', 'ssc install rwolf'),
    'wyoung':             ('Westfall-Young FWER battery (brokerage 中心度)', 'ssc install wyoung'),
    'csdid':              ('Callaway-SantAnna 错时 DiD (audit DID-1)', 'ssc install csdid'),
    'bacondecomp':        ('Goodman-Bacon 分解 (audit DID-1)', 'ssc install bacondecomp'),
    'eventstudyinteract': ('Sun-Abraham 事件研究 (audit DID-2)', 'ssc install eventstudyinteract'),
    'honestdid':          ('Rambachan-Roth HonestDiD (audit DID-3)', 'ssc install honestdid'),
    'ppmlhdfe':           ('PPML 计数 outcome (P4 专利 / P5 并购)', 'ssc install ppmlhdfe'),
    'xtbreak':            ('结构断点 / 分时代稳定性 (audit CY-2)', 'ssc install xtbreak'),
    'winsor2':            ('缩尾稳健性', 'ssc install winsor2'),
    'estout':             ('esttab/estout 表导出', 'ssc install estout'),
    'coefplot':           ('系数图', 'ssc install coefplot'),
}
_OPTIONAL_STATA_ADOS = {
    'bartik_weight': ('官方 GPSS Rotemberg 权重 — 本 LOO-Bartik 设计用内联投影替代, 非必装',
                      'net install bartik_weight, from(https://raw.githubusercontent.com/paulgp/bartik-weight/master/code)'),
    'condivreg':     ('条件 IV 置信区间 (weakiv 回退层; weakiv 已为首选, 非必装)', 'findit condivreg'),
    'rivtest':       ('弱工具稳健检验 (weakiv 回退层, 非必装)', 'findit rivtest'),
}


def _candidate_ado_dirs() -> list:
    """返回候选 Stata ado 目录 (personal PLUS + Stata 安装 base/site), 供 doctor ado 扫描。

    不启动 Stata (保持 doctor 快): 直接扫文件系统。personal PLUS 是 ssc install 默认落点。
    """
    import os
    dirs = []
    home = os.path.expanduser('~')
    dirs.append(os.path.join(home, 'ado', 'plus'))
    dirs.append(os.path.join(home, 'ado', 'personal'))
    try:
        bin_path = discover_stata_bin()
    except Exception:
        bin_path = None
    if bin_path:
        bdir = os.path.dirname(bin_path)
        for sub in (('ado', 'base'), ('ado', 'site')):
            dirs.append(os.path.join(bdir, *sub))
    return [d for d in dirs if os.path.isdir(d)]


def _ado_installed(name: str, ado_dirs: list) -> bool:
    """启发式: ado 存于 <dir>/<首字母>/<name>.ado 或 <dir>/<name>.ado 或 <dir>/_/<name>.ado。"""
    import os
    for d in ado_dirs:
        for cand in (os.path.join(d, name[0].lower(), name + '.ado'),
                     os.path.join(d, name + '.ado'),
                     os.path.join(d, '_', name + '.ado')):
            if os.path.exists(cand):
                return True
    return False


def _cli_doctor(args) -> int:
    """CLI 子命令: doctor — 诊断 v3.2.0 用户层依赖完整性 (plan v14 §6 风险表 R20-A)."""
    try:
        import sys
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass
    import os

    verbose = getattr(args, 'verbose', False)
    n_ok = 0
    n_warn = 0
    n_err = 0
    print("news_process v3.2.0 doctor (plan v14 §6 launch checklist)")
    if verbose:
        print(f"  verbose mode: showing version info + paths")
    print("=" * 60)

    # 1. Python deps (硬依赖 5 + optional 1)
    print("\n[1/6] Python 依赖")
    REQUIRED_DEPS = ['pandas', 'numpy', 'pyarrow', 'pytest', 'yaml']
    OPTIONAL_DEPS = {
        # v3.2.0 M1/7: pyreadstat 改为 OPTIONAL (pandas to_stata fallback 可代)
        'pyreadstat': 'stage 46 stata_export 全功能 (value labels + extended missing); '
                      'fallback: pandas to_stata 基础 .dta',
    }
    for d in REQUIRED_DEPS:
        try:
            m = __import__(d if d != 'yaml' else 'yaml')
            version = getattr(m, '__version__', '?')
            if verbose:
                print(f"   [OK] {d} ({version})")
            else:
                print(f"   [OK] {d}")
            n_ok += 1
        except ImportError:
            print(f"   [ERR] {d} NOT installed (required)")
            n_err += 1
    for d, reason in OPTIONAL_DEPS.items():
        try:
            m = __import__(d)
            version = getattr(m, '__version__', '?')
            if verbose:
                print(f"   [OK] {d} ({version}) — optional")
            else:
                print(f"   [OK] {d} (optional)")
            n_ok += 1
        except ImportError:
            print(f"   [WARN] {d} NOT installed (optional)")
            print(f"          reason: {reason}")
            n_warn += 1

    # 2. Stage 14 输入 (LLM launch 前置)
    print("\n[2/6] Pipeline 数据")
    try:
        from news_process.core.config import load_config
        CONFIG = load_config()
        for stage, fname in [
            ('15_fintech_intensity', 'output_14_fintech_intensity'),
            ('21_tone_llms', 'output_21_tone_llms'),
            ('40_panel_yearly', 'output_40_panel_yearly'),
        ]:
            f = CONFIG.get('filenames', {}).get(fname, f'{stage}.parquet')
            p = os.path.join(CONFIG['paths']['output_dir'], f)
            if os.path.exists(p):
                print(f"   [OK] {f}")
                n_ok += 1
            else:
                print(f"   [WARN] {f} not yet produced (run pipeline first)")
                n_warn += 1
    except Exception as e:
        print(f"   [ERR] config load: {e}")
        n_err += 1

    # 3. LLM cache (stage 35 LLM 升级前置)
    print("\n[3/6] LLM cache (stage 35 LLM 升级)")
    try:
        from news_process.core.config import load_config
        cache_path = os.path.join(load_config()['paths']['output_dir'], '_llm_cache.db')
        if os.path.exists(cache_path):
            size_mb = os.path.getsize(cache_path) / 1024 / 1024
            print(f"   [OK] _llm_cache.db ({size_mb:.1f} MB)")
            n_ok += 1
        else:
            print("   [WARN] _llm_cache.db not yet created (run stage 21 first)")
            n_warn += 1
    except Exception:
        n_warn += 1

    # 4. YUNWU_API_KEY (LLM launch 前置)
    print("\n[4/6] LLM API access")
    if os.environ.get('YUNWU_API_KEY', '').strip():
        print("   [OK] YUNWU_API_KEY set")
        n_ok += 1
    else:
        print("   [WARN] YUNWU_API_KEY not set (stage 21 + stage 35 LLM 不可跑)")
        n_warn += 1

    # 5. Stata bin (CLI build-replication 后用)
    print("\n[5/6] Stata 可执行")
    try:
        from news_process.papers._common.stata_runner import discover_stata_bin
        bin_path = discover_stata_bin()
        if bin_path:
            print(f"   [OK] {bin_path}")
            n_ok += 1
        else:
            print("   [WARN] Stata bin not detected; set NEWS_PROCESS_STATA_BIN env var")
            n_warn += 1
    except Exception as e:
        print(f"   [WARN] Stata bin check failed: {e}")
        n_warn += 1

    # 6. Stata ado 包 (顶刊稳健性 / 复现必装; reaudit-t18-2026-06-15)
    print("\n[6/6] Stata ado 包 (顶刊稳健性 / 复现必装)")
    ado_dirs = _candidate_ado_dirs()
    if not ado_dirs:
        print("   [WARN] 未定位 Stata ado 目录 (personal PLUS / 安装 base);")
        print("          在 Stata 内对各包跑 `which <pkg>` 自查, 缺则 `ssc install <pkg>`")
        n_warn += 1
    else:
        if verbose:
            print(f"   扫描目录: {', '.join(ado_dirs)}")
        n_ado_miss = 0
        for name, (purpose, install) in _REQUIRED_STATA_ADOS.items():
            if _ado_installed(name, ado_dirs):
                print(f"   [OK] {name}" + (f" — {purpose}" if verbose else ""))
                n_ok += 1
            else:
                print(f"   [WARN] {name} 未装 — {purpose}")
                print(f"          装: {install}")
                n_warn += 1
                n_ado_miss += 1
        for name, (purpose, install) in _OPTIONAL_STATA_ADOS.items():
            if _ado_installed(name, ado_dirs):
                print(f"   [OK] {name} (optional)")
                n_ok += 1
            else:
                print(f"   [INFO] {name} 未装 (optional) — {purpose}")
        if n_ado_miss:
            print(f"   → {n_ado_miss} 个必装 ado 缺失: 对应顶刊稳健性块 (弱工具 AR-CI / FWER /"
                  " 错时 DiD / wild bootstrap 等) 会优雅跳过、不产出承诺统计量, 投稿前须装齐。")

    print("\n" + "=" * 60)
    print(f"  Summary: {n_ok} OK / {n_warn} WARN / {n_err} ERR")
    if n_err:
        print("  Action: 装缺失 Python 包 (pip install -e .)")
        return 1
    if n_warn:
        print("  Action: 跑 run_pipeline_function.py 产数据; 设 YUNWU_API_KEY 为 LLM launch")
    return 0


def _get_version_string() -> str:
    """v3.2.0 M4/7: 返回 "news_process v3.2.0 (commit=<hash>+dirty)" 字符串."""
    commit = _get_git_commit_hash_with_dirty()
    return f"news_process v3.2.0 (commit={commit})"


def main():
    """CLI 入口 (subcommand dispatch)."""
    import argparse
    parser = argparse.ArgumentParser(
        prog='python -m news_process.papers._common.stata_runner',
        description='news_process v3.2.0 Stata orchestration CLI (plan v14 §9). '
                    'Subcommands: build-replication / list-templates / doctor / verify-replication.',
        epilog='Full docs: news_process/papers/_common/stata_templates/README.md',
    )
    parser.add_argument(
        '--version', action='version',
        version=_get_version_string(),
        help='Show news_process version + git commit hash + dirty flag',
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # build-replication
    bp = subparsers.add_parser(
        'build-replication',
        help='Generate v3.2.0 Stata replication package (plan v14 §9.3; P1 +--paper)',
    )
    bp.add_argument('--paper', choices=sorted(_VALID_PAPER_IDS_BUILD),
                    default='bank_fintech_tone',
                    help='Paper id (default: bank_fintech_tone, main paper). P1 added.')
    bp.add_argument('--locus', choices=['lf', 'lc'], default=None,
                    help='Main locus track (required for bank_fintech_tone; ignored else)')
    bp.add_argument('--subst', choices=['sf', 'sc'], default=None,
                    help='Main substantiveness track (required for bank_fintech_tone)')
    bp.add_argument('--sent', choices=['full', 'ctx', 'ss'], default=None,
                    help='Main sentiment track (full/ctx/ss; ss=银行+金科同句共现 '
                         'Bank+FinTech same-sentence; required for bank_fintech_tone)')
    bp.add_argument('--root', type=str, default='.',
                    help='Project root for replication package (default: cwd)')
    bp.set_defaults(func=_cli_build_replication)

    # list-templates (M4/7 新增)
    lt = subparsers.add_parser(
        'list-templates',
        help='List Stata templates inventory (plan v14 §9.2)',
    )
    lt.add_argument('--verbose', action='store_true',
                    help='Show placeholder usage inventory across templates')
    lt.set_defaults(func=_cli_list_templates)

    # doctor (M2/7 新增, plan v14 §6 风险表 launch 前置检查)
    dr = subparsers.add_parser(
        'doctor',
        help='Diagnose v3.2.0 deps + pipeline + LLM + Stata (plan v14 launch checklist)',
    )
    dr.add_argument('--verbose', action='store_true',
                    help='Show package versions + extra diagnostic info')
    dr.set_defaults(func=_cli_doctor)

    # verify-replication (M4/7 新增, 验证 build-replication 产出)
    vr = subparsers.add_parser(
        'verify-replication',
        help='Verify a replication_v3.2.0_* package structure (plan v14 §9.3 + §9.5)',
    )
    vr.add_argument('path', type=str,
                    help='Path to replication package directory (e.g. replication_v3.2.0_lc_sf_ctx/)')
    vr.set_defaults(func=_cli_verify_replication)

    args = parser.parse_args()
    return args.func(args)


if __name__ == '__main__':
    import sys
    sys.exit(main())
