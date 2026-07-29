"""tests/test_stage_log_filename_mapping.py — 阶段脚本名 ↔ 日志文件名映射 gate。

**为何需要 (2026-07-29 实弹)**: CLAUDE.md 把日志约定写成无例外的普适规则 ——
「日志 `logs/<stage>.log` (扁平, 每阶段一文件, 每次运行覆盖)」。审计入口③ 时我据此
去 `tail logs/62_dedup_threshold_sensitivity.log`, 得到**空输出**, 差点判成
「阶段 62 跑了 30 分钟一个字没写 = 疑似卡死」。实际该文件**根本不存在**:
真实日志是 `logs/62_dedup_sensitivity.log` (当时 10,417 字节且在增长)。
`tail` 对不存在的文件配上 `2>/dev/null` 就是静默空 —— **文件不存在与阶段无输出
在终端上长得一模一样**, 这是最会骗人的一类观测。

全 32 个注册阶段普查, 只有 2 个不遵守:
    40_panel_export_main.py          → logs/40_build_panel.log
    62_dedup_threshold_sensitivity.py → logs/62_dedup_sensitivity.log

⚠ **这两个不能改名**, 已逐一核实是刻意保留:
  · `pipeline/panel/encode.py:47` 明写 `STAGE_NAME = "40_build_panel"
    # 保留原名, 兼容日志文件命名约定`;
  · `pipeline/filtering/policy_alignment.py:1189` 有一处注释专门交代 stage 16
    如何避免日志落进 `40_build_panel.log` —— 该名字是承重的;
  · `tests/test_subprocess_log_isolation.py` (F27/F29b gate) 有 6 处按
    `'40_build_panel'` 做命名空间归属断言, 改名会连坐。
故本 gate 的作用**不是**逼它们改名, 而是:
  ① 把这 2 个例外**冻结成显式白名单** —— 出现第 3 个例外当场红;
  ② 白名单里的映射本身也钉死 —— 谁把 `40_build_panel` 悄悄改了同样红;
  ③ 让 CLAUDE.md 的例外记载与代码保持同步 (文档漏记正是本次踩坑的根因)。
"""
from __future__ import annotations

import ast
import os
import re
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_NP = os.path.dirname(_HERE)
_PROJECT_PARENT = os.path.dirname(_NP)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.dag import STAGES_MAIN, STAGES_VALIDATION  # noqa: E402

#: script -> 实际 STAGE_NAME (= 日志文件名去掉 .log)。**仅**收录与脚本名不一致者。
#: 新增条目前请先确认真的改不动 —— 默认应当是让 STAGE_NAME 跟脚本名走。
KNOWN_LOGNAME_EXCEPTIONS = {
    '40_panel_export_main.py': '40_build_panel',
    '62_dedup_threshold_sensitivity.py': '62_dedup_sensitivity',
}

_IMPORT_RE = re.compile(r'from\s+(news_process\.[\w.]+)\s+import\s+main')


def _module_path_for(script):
    """从 thin shim 里解析出底层实现模块的磁盘路径。"""
    p = os.path.join(_NP, script)
    if not os.path.exists(p):
        pytest.fail(f'DAG 登记的 {script} 不在盘上')
    with open(p, encoding='utf-8') as f:
        m = _IMPORT_RE.search(f.read())
    if not m:
        return None
    rel = m.group(1).split('.', 1)[1].replace('.', os.sep) + '.py'
    return os.path.join(_NP, rel)


def _stage_name_of(script):
    """AST 取模块级 `STAGE_NAME = "..."` (不 import — 阶段模块 import 代价高且有副作用)。"""
    mp = _module_path_for(script)
    if mp is None or not os.path.exists(mp):
        return None
    with open(mp, encoding='utf-8') as f:
        tree = ast.parse(f.read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == 'STAGE_NAME':
                    return node.value.value
    return None


_ALL = list(STAGES_MAIN) + list(STAGES_VALIDATION)


@pytest.mark.parametrize('script', sorted(s.script for s in _ALL))
def test_stage_name_matches_script_or_is_whitelisted(script):
    """STAGE_NAME 必须等于脚本名去掉 .py, 或落在冻结白名单里。"""
    got = _stage_name_of(script)
    if got is None:
        pytest.skip(f'{script}: 底层模块无模块级 STAGE_NAME (由 runner 传入)')
    stem = script[:-3]
    if script in KNOWN_LOGNAME_EXCEPTIONS:
        assert got == KNOWN_LOGNAME_EXCEPTIONS[script], (
            f'{script} 的 STAGE_NAME 由 {KNOWN_LOGNAME_EXCEPTIONS[script]!r} 变成了 {got!r} —— '
            f'白名单映射被改动。日志文件名随之改变, 按旧名找日志的人会看到"文件不存在"的'
            f'静默空 (与"阶段无输出"在终端上不可区分)。要么改回, 要么同步更新白名单与 CLAUDE.md。')
    else:
        assert got == stem, (
            f'{script} 的 STAGE_NAME={got!r} ≠ 脚本名 {stem!r} ⟹ 日志会落到 '
            f'logs/{got}.log 而非 logs/{stem}.log, 违反 CLAUDE.md 的「每阶段一文件」约定。'
            f'这是第 3 个例外 —— 默认应当改成跟脚本名走; 若确实改不动, 须同时登记进 '
            f'KNOWN_LOGNAME_EXCEPTIONS 并在 CLAUDE.md 明写, 不得静默新增。')


def test_exception_whitelist_has_no_stale_entries():
    """白名单不得残留已消失/已改好的条目 (否则它会掩护真正的新增例外)。"""
    scripts = {s.script for s in _ALL}
    stale = sorted(set(KNOWN_LOGNAME_EXCEPTIONS) - scripts)
    assert not stale, f'白名单引用了不在 DAG 中的 script: {stale}'
    fixed = [k for k in KNOWN_LOGNAME_EXCEPTIONS if _stage_name_of(k) == k[:-3]]
    assert not fixed, (
        f'以下条目的 STAGE_NAME 已与脚本名一致, 应从白名单删除: {fixed}')


def test_disk_logs_match_expected_names():
    """证据型互补检查: 用**盘上真实日志文件**复核, 覆盖 AST 查不到 STAGE_NAME 的阶段。

    AST 那条对「STAGE_NAME 由 runner 传入」的阶段只能 skip; 而 skip 不是守卫。
    本条改用真实产物: 凡本机跑过的阶段, `logs/` 里必须存在**期望名**的文件。
    没跑过的阶段无从取证, 跳过该条目 (而非整个用例)。
    """
    logdir = os.path.join(_NP, 'logs')
    if not os.path.isdir(logdir):
        pytest.skip('logs/ 不存在 — 本机尚未跑过任何阶段')
    have = {f[:-4] for f in os.listdir(logdir) if f.endswith('.log')}
    if not have:
        pytest.skip('logs/ 为空')
    offenders = []
    for s in _ALL:
        expect = KNOWN_LOGNAME_EXCEPTIONS.get(s.script, s.script[:-3])
        if expect in have:
            continue
        # 期望名不在盘上: 若同号段有别的日志, 说明该阶段跑过但写去了别处 ⟹ 真违规
        same_num = sorted(h for h in have if h[:2] == s.script[:2] and h != expect)
        if same_num:
            offenders.append((s.script, expect, same_num))
    assert not offenders, (
        '以下阶段的日志写去了非期望文件名 (期望名在盘上缺失, 却存在同号段的其它日志):\n'
        + '\n'.join(f'  {sc}: 期望 logs/{exp}.log, 实见 {alt}' for sc, exp, alt in offenders)
        + '\n新增例外必须同时登记 KNOWN_LOGNAME_EXCEPTIONS 与 CLAUDE.md。')


def test_claude_md_documents_the_exceptions():
    """CLAUDE.md 必须明写这两个例外 —— 文档漏记正是 2026-07-29 踩坑的直接根因。"""
    p = os.path.join(_NP, 'CLAUDE.md')
    with open(p, encoding='utf-8') as f:
        txt = f.read()
    missing = [v for v in KNOWN_LOGNAME_EXCEPTIONS.values() if v not in txt]
    assert not missing, (
        f'CLAUDE.md 未记载日志名例外 {missing}。约定被写成"每阶段一文件"而不提例外时, '
        f'按约定去 tail 会得到静默空 —— 文件不存在与阶段无输出在终端上不可区分。')
