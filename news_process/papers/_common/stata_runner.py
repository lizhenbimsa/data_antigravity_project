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


def run_do(do_path: str | Path,
           args: Sequence[str] | None = None,
           *,
           stata_bin: str | None = None,
           cwd: str | Path | None = None,
           timeout: int = 1800,
           batch_mode: bool = True,
           check: bool = True) -> subprocess.CompletedProcess:
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

    return subprocess.run(
        cmd,
        cwd=str(cwd),
        timeout=timeout,
        check=check,
        capture_output=True,
        text=True,
    )


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
    'MAIN_SENT_TRACK',   # full / ctx
    'PROJECT_ROOT',      # absolute path
}

# Tier 2: paper-level (5 paper 共用, 但每个 paper 取不同默认值)
_KNOWN_PLACEHOLDERS_PAPER_LEVEL = {
    'PAPER_ID',
    'MAIN_DV',           # canonical dependent variable
    'CONTROLS',           # standard control set (string)
    'CLUSTER_VAR',        # vce(cluster <var>) target
    'HET_VAR',            # heterogeneity interaction variable
    # v3.7.3 Plan A v1.0: paper-level main treatment placeholder (used by
    # 25_tableA8_title_robustness.do.tmpl + B-route paper-specific templates).
    'MAIN_TREAT',         # main treatment variable (per paper, e.g. P1 = llm_vote_tone_ctx)
}

# Tier 3: paper-specific (sparse, only the paper that needs it)
_KNOWN_PLACEHOLDERS_PAPER_SPECIFIC = {
    # benefit_society (v3.2.1 dual-track expansion — plan v2.12)
    'ATTITUDE_VAR',      # alias = ATTITUDE_FULL (backwards compat)
    'ATTITUDE_FULL', 'ATTITUDE_CTX',
    'BENEFIT_POS_FRAC_FULL', 'BENEFIT_POS_FRAC_CTX',
    'BENEFIT_NEG_FRAC_FULL', 'BENEFIT_NEG_FRAC_CTX',
    'MECHANISM_TOKEN', 'MECHANISM_HIDDEN', 'MECHANISM_SUBST',
    'ROBUSTNESS_DV', 'BOOTSTRAP_REPS', 'RANDOM_SEED',
    # brokerage_network
    'MAIN_ENDOG', 'MAIN_IV', 'TREATMENT_DCEP', 'TREATMENT_SANDBOX',
    'CENTRALITY_BTW', 'CENTRALITY_CONS', 'CENTRALITY_BROKER',
    # strategic_diff
    'MAIN_DIFF_VAR', 'FLUIDITY_VAR', 'SIM_MAX_VAR',
    'BARTIK_IV', 'TONE_VAR', 'COHERENCE_VAR',
    # llm_peer
    'LLM_PEER_IV', 'LLM_PEER_COVERAGE_IV', 'COMPETE_IDX', 'CUTOFF_VARS',
    # (TONE_VAR shared with strategic_diff)
}

# Union — superset that any template may legally reference.
_KNOWN_PLACEHOLDERS = (
    _KNOWN_PLACEHOLDERS_MAIN
    | _KNOWN_PLACEHOLDERS_PAPER_LEVEL
    | _KNOWN_PLACEHOLDERS_PAPER_SPECIFIC
)

_VALID_SPEC_VALUES = {
    'MAIN_LOCUS_TRACK': {'lf', 'lc'},
    'MAIN_SUBST_TRACK': {'sf', 'sc'},
    'MAIN_SENT_TRACK':  {'full', 'ctx'},
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
        # v3.7.3 Plan A v1.0: MAIN_TREAT + RANDOM_SEED for _title robustness template
        # (25_tableA8_title_robustness.do.tmpl, P1 共用主线根目录).
        # P1 G3 main = _ctx (v3.6.0 Plan E P4 G3 锁定).
        'MAIN_TREAT': 'llm_vote_tone_ctx',
        'RANDOM_SEED': '20260516',
    },
    **_DERIVATIVE_PAPER_DEFAULTS,
}


# Q1.4 (2026-05-15): commit-hash helper moved to _git_utils.py.
# Re-export for any external callers that imported by old path.
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
        template_dir = base if paper_id == 'bank_fintech_tone' else base / paper_id
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
  - sent track:  `{sent}` ({'Hassan 2019 QJE entity-proximity' if sent == 'ctx' else 'full-text'})
- **Templates instantiated**: {n_templates}
- **Plan version**: v14 (62 rounds audit; user confirmed 9 Action Items)
"""
        else:
            # Derivative paper: no main-paper triad; report paper_id + key defaults.
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
        # Optional override (rare for derivative papers; mostly unused).
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
    print(f"   stata -b do code/00_master.do")
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
        2. 14 .do 文件全部存在
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

    # 2. 15 .do 文件 (v3.7.3 Plan A v1.0: +1 from 25_tableA8_title_robustness)
    print("\n[2/5] Stata .do 文件 (15 expected)")
    code_dir = pkg_dir / 'code'
    if code_dir.is_dir():
        do_files = sorted(code_dir.glob('*.do'))
        if len(do_files) == 15:
            print(f"   [OK] {len(do_files)} .do files (15/15 完整)")
            n_ok += 1
        else:
            print(f"   [ERR] {len(do_files)} .do files (expected 15)")
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

    # 5. master.do 引用 14 子 .do (v3.7.3 Plan A v1.0: +1 from 25_tableA8_title_robustness)
    print("\n[5/5] master.do 引用 14 子 .do")
    master = code_dir / '00_master.do'
    if master.exists():
        content = master.read_text(encoding='utf-8')
        expected = [
            '01_data_prep.do', '10_table1_descriptives.do',
            '11_table2_main_m1m6.do', '12_table3_mechanism.do',
            '13_table4_heterogeneity.do', '14_table5_advanced_robustness.do',
            '20_tableA1_inter_track_kappa.do', '21_tableA2_main_spec_switch.do',
            '22_tableA3_bartik_iv.do', '23_tableA4_radius_sensitivity.do',
            '24_tableA5_dictionary_method.do',
            '25_tableA8_title_robustness.do',  # v3.7.3 Plan A v1.0
            '30_figure1_event_study.do', '31_figure_coefplot_dual.do',
        ]
        missing = [s for s in expected if s not in content]
        if not missing:
            print(f"   [OK] master.do 引用 14/14 子 .do")
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
    print("\n[1/5] Python 依赖")
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
    print("\n[2/5] Pipeline 数据")
    try:
        from news_process.core.config import load_config
        CONFIG = load_config()
        for stage, fname in [
            ('14_fintech_intensity', 'output_14_fintech_intensity'),
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
    print("\n[3/5] LLM cache (stage 35 LLM 升级)")
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
    print("\n[4/5] LLM API access")
    if os.environ.get('YUNWU_API_KEY', '').strip():
        print("   [OK] YUNWU_API_KEY set")
        n_ok += 1
    else:
        print("   [WARN] YUNWU_API_KEY not set (stage 21 + stage 35 LLM 不可跑)")
        n_warn += 1

    # 5. Stata bin (CLI build-replication 后用)
    print("\n[5/5] Stata 可执行")
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
    bp.add_argument('--sent', choices=['full', 'ctx'], default=None,
                    help='Main sentiment track (required for bank_fintech_tone)')
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
