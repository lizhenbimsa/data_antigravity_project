"""scripts/audit/check_static_enums.py
========================================

第三轨 (`_ss` 银行+金科同句) **静默漏列护栏** — 计划 §7.3-A1 + §⑬-D 的强制落地。

背景 (为什么需要本工具)
----------------------
新增第三条情感轨 `_ss` (content_ss, 银行+金科同句共现) 时, 大量 `for track in
['_full', '_ctx']` **参数化循环** grep 一抓就到、加一个 `'_ss'` 即可级联; 真正的
#1 风险是 **静态枚举** (static enumeration): 那些把 full/ctx **写死成字面量** 的
地方 ——

  - track 字面量列表/元组: ``['_full', '_ctx']`` / ``('full', 'ctx')`` /
    ``['full', 'ctx']`` / ``TRACKS = (...)`` ;
  - 以 track 为键的 **dict 字面量**: ``{'_full': ..., '_ctx': ...}`` /
    ``_ART_TONE_BY_TRACK = {...}`` ;
  - "按替换派生" 的列表推导: ``[d.replace('_full', '_ctx') for d in DIMS_FULL]`` 。

漏掉其中任意一个 → **无报错、静默缺 `_ss` 列**, 直到下游某张 Stata 表里第三列
凭空消失才被人肉发现。计划明确: 把 "强制自动扫描" 从不可信的 **人工 review**
升级为一个 **pytest 红线** —— 漏一个静态枚举, ``test_no_unconverted_two_track_enums``
直接 FAIL。

本工具做什么
------------
扫描 pipeline / validation / papers 三个源码子树, 对每一处 **双轨静态枚举** 断言:

  (1) 邻近 (同表达式 / 同 dict 体 / 紧邻数行内) 存在 `_ss` / `ss` 兄弟项; **或**
  (2) 该处带有显式 **豁免标记** (opt-out marker), 表示 "此处有意保持 full/ctx 两轨"。

二者皆无 → 记为 finding (静默漏列嫌疑)。

另外按计划 §⑬-D 做一道 **注释平价** 扫描: 任何含裸 ``双轨`` / ``两轨`` /
``two-track`` 的注释/docstring 行, 若所在文件未带 "legacy 示例" 豁免标记, 也记为
finding (提醒 coder 把陈旧的 "双轨" 措辞订正为 "三轨 (full/ctx/ss)")。

豁免标记 (opt-out markers, 任一即放行)
--------------------------------------
- ``# no-ss-track``                         (静态枚举护栏专用; 见 network_brokerage.py)
- ``intentionally NOT produced``            (encode_collab.py cell_id / LM-FLS 族)
- ``legacy (full/ctx)``                     (run_pipeline_function.py 设计性两轨)

这些标记可在 **命中行本身** 或 **其上方 ``_MARKER_LOOKBACK`` 行内** 任意位置出现
(允许把豁免理由写在枚举上一行的注释里)。

为何只有这三类有意保持两轨
--------------------------
``cell_id`` (D2/D4 collab-cell 分解) 分类的是 substantiveness / locus / collab
这类 **full/ctx 锚定的 LLM 属性**, ss 是 **纯情感轨**, 不参与 cell 分解 (计划
§7.3-A1 决策); LM/FLS 非情感 lexicon 族同理。这些位置必须用豁免标记显式声明,
而不是默默漏掉 —— 区别在于 "有意 (marked)" vs "遗漏 (silent)"。

依赖
----
**仅纯标准库** (re / pathlib / argparse / sys / dataclasses; 无 pandas / 无项目内
import) → 不受其它模块并行编辑影响, ``python -m ruff check`` 与单独 import 都不会
被半成品上游拖累。

用法
----
    # CLI 报告 (人读)
    python -m news_process.scripts.audit.check_static_enums
    python news_process/scripts/audit/check_static_enums.py --no-prose         # 只查枚举
    python news_process/scripts/audit/check_static_enums.py --enum-only-exit   # 退出码只看枚举

    # pytest 红线 (testpaths 默认不收 scripts/, 须显式给路径或经 tests/ 薄包装)
    pytest news_process/scripts/audit/check_static_enums.py

白话
----
给三轨改造当"漏列报警器": 凡是把 full/ctx **写死** 的地方, 要么旁边补上 ss, 要么
明确贴个"这里就只要两轨"的标签; 两样都没有就报警。顺带挑出还写着"双轨/两轨"的
旧注释, 提醒改成"三轨"。全程只读源码、不碰数据、不跑流水线、一分钱不花。
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# --------------------------------------------------------------------------- #
# 路径锚定: 本文件位于 news_process/scripts/audit/ → 上溯 3 层即 news_process/    #
# --------------------------------------------------------------------------- #
_HERE = Path(__file__).resolve()
_NEWS_PROCESS_ROOT = _HERE.parents[2]  # .../news_process

# 扫描范围: 三轨改造涉及的源码子树 (计划 §7.3-A1)。tests/ 不在内
# (测试码的 ['_full','_ctx'] 由 §⑫ parametrize 处理, 不是漏列风险)。
SCAN_SUBTREES = ('pipeline', 'validation', 'papers')

# 豁免标记 (opt-out markers): 命中行或其上方 _MARKER_LOOKBACK 行内任一出现即放行。
# - no-ss-track:               静态枚举护栏专用标记 (计划 §7.3-A1)
# - intentionally NOT produced: encode_collab cell_id / LM-FLS 族 (有意两轨)
# - legacy (full/ctx):         run_pipeline_function 等设计性两轨
_ENUM_OPT_OUT_MARKERS = (
    'no-ss-track',
    'intentionally not produced',
    'legacy (full/ctx)',
)
_MARKER_LOOKBACK = 3  # 豁免标记最多可写在枚举上方几行
# ss 兄弟项 (DIMS_SS / INDICATORS_SS / .append('_ss') / 条件 "'_ss' in cols" 等)
# 常紧跟在 ctx 派生 / 双轨字面量 / dict 体之后数行 (中间夹注释), 故前向探测窗口
# 放宽到 8 行: 把"已三轨化但不在同一行"的优雅/条件覆盖识别为通过, 减少误报,
# 同时仍能逮住真正零 ss 处理的漏列。
_SS_SIBLING_LOOKAHEAD = 8

# 注释平价豁免: 文件含此标记 → 该文件内裸 双轨/两轨 注释不再报 (用于刻意保留的
# "full/ctx 两轨示例" 文档片段)。计划 §⑬-D。
_PROSE_OPT_OUT_MARKER = 'legacy (full/ctx) 示例'

# --------------------------------------------------------------------------- #
# 检测正则                                                                      #
# --------------------------------------------------------------------------- #
# 双元 track 序列字面量: ['_full', '_ctx'] / ('full', 'ctx') / [ 'full' , 'ctx' ] …
# 仅匹配 **恰好两元** 的 full+ctx 序列 (三元含 ss 的不命中, 即已转换)。
_TWO_TRACK_SEQ = re.compile(
    r"""[\[(]\s*"""
    r"""['"]_?(?:full)['"]\s*,\s*"""
    r"""['"]_?(?:ctx)['"]\s*"""
    r"""[\])]""",
    re.VERBOSE,
)

# 已转换的三元序列 (含 ss): 用于二次确认, 避免对同一行的两元子串误报。
_THREE_TRACK_SEQ = re.compile(
    r"""['"]_?(?:full)['"]\s*,\s*"""
    r"""['"]_?(?:ctx)['"]\s*,\s*"""
    r"""['"]_?(?:ss)['"]""",
    re.VERBOSE,
)

# list-comprehension 派生: [... .replace('_full', '_ctx') ...]
_REPLACE_FULL_TO_CTX = re.compile(
    r"""\.replace\(\s*['"]_full['"]\s*,\s*['"]_ctx['"]\s*\)""",
    re.VERBOSE,
)
_REPLACE_FULL_TO_SS = re.compile(
    r"""\.replace\(\s*['"]_full['"]\s*,\s*['"]_ss['"]\s*\)""",
    re.VERBOSE,
)

# dict 字面量起始: 行内含 `{` (track-keyed dict 开括号); 命中后由
# _dict_body_has_ss_key 做大括号深度配平扫 dict 体并检查 track 键。
_DICT_OPEN = re.compile(r"\{")

# track 作为 dict 键: 'full':  /  '_ctx':  …
_TRACK_KEY = re.compile(r"""['"](?P<pfx>_?)(?P<name>full|ctx|ss)['"]\s*:""")

# 裸 双轨/两轨/two-track 注释扫描 (注释平价)
_PROSE_TWO_TRACK = re.compile(r"双轨|两轨|two[\s\-]?track", re.IGNORECASE)

# prose 误报豁免: 同一注释片段若也提到 三轨 / full/ctx/ss / _ss / three-track,
# 说明该注释是在 **描述向三轨的转换** (如 "由双轨改为三轨"), 而非陈旧的"仅双轨"
# 措辞 → 放行 (鲁棒性: 避免把记录转换过程的注释误报为待订正)。
_PROSE_THREE_TRACK_OK = re.compile(
    r"三轨|three[\s\-]?track|full\s*/\s*ctx\s*/\s*ss|_ss\b|同句", re.IGNORECASE)


@dataclass
class Finding:
    """一处疑似静默漏列 / 陈旧注释。"""

    path: str          # 相对 news_process/ 的路径
    line: int          # 1-based 行号
    category: str      # 'static_enum' | 'replace_derive' | 'dict_keys' | 'prose'
    snippet: str       # 命中行 (strip 后, 截断)
    reason: str        # 为何被记 + 修复指引

    def render(self) -> str:
        return (f"{self.path}:{self.line} [{self.category}] {self.reason}\n"
                f"      | {self.snippet}")


# --------------------------------------------------------------------------- #
# 辅助                                                                          #
# --------------------------------------------------------------------------- #
def _iter_source_files() -> list[Path]:
    """枚举三个子树下所有 .py (跳过 __pycache__ / 本审计文件自身)。"""
    files: list[Path] = []
    for sub in SCAN_SUBTREES:
        root = _NEWS_PROCESS_ROOT / sub
        if not root.is_dir():
            continue
        for p in sorted(root.rglob('*.py')):
            if '__pycache__' in p.parts:
                continue
            files.append(p)
    return files


def _rel(path: Path) -> str:
    try:
        return path.relative_to(_NEWS_PROCESS_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _has_opt_out_marker(lines: list[str], idx: int) -> bool:
    """命中行 (idx, 0-based) 或其上方 _MARKER_LOOKBACK 行内是否带豁免标记。"""
    lo = max(0, idx - _MARKER_LOOKBACK)
    window = '\n'.join(lines[lo:idx + 1]).lower()
    return any(m in window for m in _ENUM_OPT_OUT_MARKERS)


def _docstring_line_flags(lines: list[str]) -> list[bool]:
    """逐行标注 "该行起始时是否处于三引号块内" (轻量 docstring 检测)。

    用途: 把 **代码模式** 检测限定在真代码行 —— docstring 里描述 dict 形状 /
    track 列表的散文不是"静默漏列"风险, 不应进 static_enum 硬门。

    简化模型 (非完整 tokenizer, 依赖轻量): 逐行计 ``\"\"\"`` 与 ``'''`` 的出现次数,
    奇偶切换块内/外状态。同一行内成对开合 (``\"\"\"x\"\"\"``) 自动抵消 → 该行后仍在
    块外。返回 list[bool], 第 i 项 = 第 i 行 *开始时* 是否在块内。误差 (含引号的
    字符串字面量内出现三引号) 极罕见, 且只会 *少报* 代码模式 finding, 由 prose
    扫描与豁免标记兜底, 不影响漏列红线的保守性。
    """
    flags: list[bool] = []
    in_doc = False
    for line in lines:
        flags.append(in_doc)
        # 该行内每出现一次三引号 token 即翻转一次状态
        toggles = line.count('"""') + line.count("'''")
        if toggles % 2 == 1:
            in_doc = not in_doc
    return flags


def _line_has_ss_sibling(line: str) -> bool:
    """同一行内是否已含 ss 轨 token (`_ss`/`'ss'`/`"ss"`/ 三元序列)。"""
    if _THREE_TRACK_SEQ.search(line):
        return True
    if re.search(r"""['"]_?ss['"]""", line):
        return True
    return '_ss' in line


def _dict_body_has_ss_key(lines: list[str], open_idx: int) -> tuple[bool, bool, int]:
    """从 open_idx 行的第一个 '{' 起做 **大括号深度配平**, 检查 dict 体内的 track 键。

    轻量实现 (不做完整 AST / 不剥字符串内括号 — track-keyed dict 的键值里几乎不会
    出现裸 ``{``/``}``, 误差由豁免标记兜底): 把 open_idx 起的若干行拼成一段文本,
    逐字符数 ``{``/``}`` 深度, 深度归零即 dict 闭合, 在闭合内文本上 finditer 找
    track 键。

    Returns (is_two_track_dict, has_ss_key, close_idx):
      - is_two_track_dict: dict 体内同时出现 full 与 ctx 键 (track-keyed dict)
      - has_ss_key:        dict 体内出现 ss 键
      - close_idx:         dict 闭合 '}' 所在行 (0-based; 配平失败则 = 文本末行)
    """
    brace_start = lines[open_idx].find('{')
    if brace_start < 0:
        return (False, False, open_idx)

    depth = 0
    body_parts: list[str] = []
    close_idx = open_idx
    closed = False
    for offset, line in enumerate(lines[open_idx:]):
        # 第一行只从 '{' 起算, 其余行整行参与
        seg = line[brace_start:] if offset == 0 else line
        for ch in seg:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    closed = True
                    break
        body_parts.append(seg)
        if closed:
            close_idx = open_idx + offset
            break

    body = '\n'.join(body_parts)
    names = {m.group('name') for m in _TRACK_KEY.finditer(body)}
    is_two_track = ('full' in names) and ('ctx' in names)
    has_ss = 'ss' in names
    return (is_two_track, has_ss, close_idx)


# --------------------------------------------------------------------------- #
# 主扫描                                                                        #
# --------------------------------------------------------------------------- #
def scan(check_prose: bool = True) -> list[Finding]:
    """扫描源码子树, 返回所有 finding。

    Args:
        check_prose: 是否同时做注释平价 (裸 双轨/两轨) 扫描。默认 True。

    Returns:
        Finding 列表 (空 = 全部双轨枚举均已三轨化或显式豁免)。
    """
    findings: list[Finding] = []

    for path in _iter_source_files():
        try:
            text = path.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            continue
        lines = text.splitlines()
        rel = _rel(path)
        prose_exempt = _PROSE_OPT_OUT_MARKER in text
        # 逐行 docstring 状态 (line 开始时是否处于三引号块内): 用于把 **代码模式**
        # 检测 (枚举/replace/dict) 限定在真代码行, 避免对 docstring 里描述 dict 形状
        # 的散文 (如 "dict: {row_idx: {'full': ...}}") 误报为 dict_keys。prose 扫描
        # 不受此限 (docstring 里的 双轨 措辞正是要订正的目标)。
        in_doc_flags = _docstring_line_flags(lines)

        # 已扫描过 dict 体的行区间, 避免对同一 dict 多行重复报
        dict_scanned_through = -1

        for idx, raw in enumerate(lines):
            lineno = idx + 1
            snippet = raw.strip()[:160]
            in_doc = in_doc_flags[idx]

            # --- (1) 两元 track 序列字面量 ['_full','_ctx'] / ('full','ctx') ---
            if not in_doc and _TWO_TRACK_SEQ.search(raw) and not _THREE_TRACK_SEQ.search(raw):
                # 前向窗口含 ss 兄弟 (如 active_tracks=['_full','_ctx'] 后数行条件
                # .append('_ss') / "if ..._ss in columns") → 优雅三轨化, 不报。
                _fwd = '\n'.join(lines[idx + 1:min(len(lines),
                                                   idx + _SS_SIBLING_LOOKAHEAD + 1)])
                _fwd_has_ss = ("_ss" in _fwd) or ("'ss'" in _fwd) or ('"ss"' in _fwd)
                if (not _line_has_ss_sibling(raw) and not _fwd_has_ss
                        and not _has_opt_out_marker(lines, idx)):
                    findings.append(Finding(
                        path=rel, line=lineno, category='static_enum',
                        snippet=snippet,
                        reason="双轨字面量序列未含 '_ss'/'ss' (加第三轨, 或贴 "
                               "'# no-ss-track' 豁免)",
                    ))

            # --- (2) .replace('_full','_ctx') 派生但无 .replace('_full','_ss') ---
            if not in_doc and _REPLACE_FULL_TO_CTX.search(raw):
                lo = max(0, idx - _MARKER_LOOKBACK)
                hi = min(len(lines), idx + _SS_SIBLING_LOOKAHEAD + 1)
                window = '\n'.join(lines[lo:hi])
                if (not _REPLACE_FULL_TO_SS.search(window)
                        and not _has_opt_out_marker(lines, idx)):
                    findings.append(Finding(
                        path=rel, line=lineno, category='replace_derive',
                        snippet=snippet,
                        reason="派生列表 .replace('_full','_ctx') 缺 ss 孪生 "
                               ".replace('_full','_ss') (邻近补一条)",
                    ))

            # --- (3) track-keyed dict 字面量 {'_full':.., '_ctx':..} 缺 ss 键 ---
            if not in_doc and idx > dict_scanned_through and _DICT_OPEN.search(raw) and _TRACK_KEY.search(
                    '\n'.join(lines[idx:min(len(lines), idx + 12)])):
                is_two, has_ss, close_idx = _dict_body_has_ss_key(lines, idx)
                dict_scanned_through = max(dict_scanned_through, close_idx)
                # dict 体后数行条件补 ss 键 (如 "if 'sum_herd_weight_ss' in cols:
                # d['_ss']=...") → 优雅三轨化, 不报。
                _fwd2 = '\n'.join(lines[close_idx:min(len(lines),
                                                      close_idx + _SS_SIBLING_LOOKAHEAD + 1)])
                _fwd2_has_ss = '_ss' in _fwd2
                if (is_two and not has_ss and not _fwd2_has_ss
                        and not _has_opt_out_marker(lines, idx)):
                    findings.append(Finding(
                        path=rel, line=lineno, category='dict_keys',
                        snippet=snippet,
                        reason="track-keyed dict 含 full+ctx 键但缺 'ss'/'_ss' 键 "
                               "(补 ss 键, 或贴 '# no-ss-track' 豁免)",
                    ))

            # --- (4) 注释平价: 裸 双轨/两轨/two-track ---
            if check_prose and not prose_exempt:
                comment_part = _comment_or_doc_fragment(raw)
                if (comment_part and _PROSE_TWO_TRACK.search(comment_part)
                        and not _PROSE_THREE_TRACK_OK.search(comment_part)):
                    findings.append(Finding(
                        path=rel, line=lineno, category='prose',
                        snippet=snippet,
                        reason="陈旧注释含 '双轨/两轨/two-track' (订正为 '三轨 "
                               "(full/ctx/ss)', 或在文件加 'legacy (full/ctx) 示例' 豁免)",
                    ))

    return findings


_COMMENT_RE = re.compile(r"#(.*)$")


def _comment_or_doc_fragment(line: str) -> str:
    """提取行内可能的注释/文档文本片段 (用于 prose 扫描)。

    简化策略 (依赖轻量, 不做完整 AST): 取 ``#`` 之后的注释; 若无 ``#`` 但行内
    含中文 双轨/两轨 (典型出现在三引号 docstring 行内), 也返回整行 —— docstring
    行通常不含会误判的代码 token, 由 ``_PROSE_OPT_OUT_MARKER`` 文件级豁免兜底。
    """
    m = _COMMENT_RE.search(line)
    if m:
        return m.group(1)
    if _PROSE_TWO_TRACK.search(line):
        return line
    return ''


# --------------------------------------------------------------------------- #
# pytest 红线                                                                   #
# --------------------------------------------------------------------------- #
def test_no_unconverted_two_track_enums() -> None:
    """pytest 红线: 任何 **未转换的双轨静态枚举** (缺 ss 且无豁免标记) → FAIL。

    替代不可信的"人工 review": 漏一个静态枚举 (silent missing _ss column) 即在此
    断言处报错, 并打印精确的 文件:行号 + 修复指引。

    注: 本断言只对 **静态枚举三类** (static_enum / replace_derive / dict_keys)
    硬失败; 注释平价 (prose) finding 由下方 ``test_no_stale_two_track_comments``
    单独把关, 二者分离以便 prose sweep 可在过渡期单独 xfail/skip 而不掩盖真正的
    漏列红线。
    """
    # scan(check_prose=False) 已只返回静态枚举三类 (不含 prose) → 直接即为红线集
    enum_findings = scan(check_prose=False)
    assert not enum_findings, (
        f"发现 {len(enum_findings)} 处未转换的双轨静态枚举 "
        f"(缺 '_ss'/'ss' 且无 '# no-ss-track' 豁免标记):\n"
        + "\n".join(f.render() for f in enum_findings)
    )


def test_no_stale_two_track_comments() -> None:
    """pytest 红线 (注释平价, 计划 §⑬-D): 触及文件含裸 '双轨/两轨/two-track'
    注释 (无 'legacy (full/ctx) 示例' 文件级豁免) → FAIL。

    与枚举红线分离: prose finding 量大且分布于尚未由本 PR 触及的文件, 过渡期可对
    本测试单独 ``-k 'not stale_two_track'`` 跳过而不影响 ``static_enum`` 硬门。
    """
    prose_findings = [f for f in scan(check_prose=True) if f.category == 'prose']
    assert not prose_findings, (
        f"发现 {len(prose_findings)} 处陈旧 '双轨/两轨/two-track' 注释 "
        f"(应订正为 '三轨 (full/ctx/ss)'):\n"
        + "\n".join(f.render() for f in prose_findings)
    )


# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #
def _print_report(findings: list[Finding], check_prose: bool) -> None:
    enum_findings = [f for f in findings if f.category != 'prose']
    prose_findings = [f for f in findings if f.category == 'prose']

    print("=" * 78)
    print("  静态枚举三轨化护栏 (check_static_enums) — 第三轨 _ss 漏列扫描")
    print("=" * 78)
    print(f"扫描子树: {', '.join(SCAN_SUBTREES)}  (根: {_NEWS_PROCESS_ROOT})")
    print(f"豁免标记: {', '.join(_ENUM_OPT_OUT_MARKERS)}")
    print("-" * 78)

    print(f"[静态枚举] 疑似漏列: {len(enum_findings)} 处")
    for f in enum_findings:
        print("  " + f.render())
    if not enum_findings:
        print("  ✅ 0 处 — 全部双轨静态枚举均已三轨化或显式豁免。")

    if check_prose:
        print("-" * 78)
        print(f"[注释平价] 陈旧 '双轨/两轨/two-track': {len(prose_findings)} 处")
        for f in prose_findings:
            print("  " + f.render())
        if not prose_findings:
            print("  ✅ 0 处 — 无陈旧双轨注释。")

    print("=" * 78)


def main() -> int:
    # Windows 控制台默认 GBK 无法编码命中行里的 ⚠/特殊字符 → 报告会 UnicodeEncodeError
    # 崩溃。把 stdout 切到 UTF-8 + errors='replace', 保证 CLI 报告在任何终端都能打印
    # (纯打印鲁棒性, 不影响 scan()/pytest 逻辑)。
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except (ValueError, OSError):
            pass

    ap = argparse.ArgumentParser(
        description="第三轨 _ss 静态枚举漏列护栏 (计划 §7.3-A1 / §⑬-D)")
    ap.add_argument('--no-prose', action='store_true',
                    help="只扫静态枚举, 跳过 双轨/两轨 注释平价扫描")
    ap.add_argument('--enum-only-exit', action='store_true',
                    help="退出码只取决于静态枚举 finding (prose 仅报告不影响退出码)")
    args = ap.parse_args()

    check_prose = not args.no_prose
    findings = scan(check_prose=check_prose)
    _print_report(findings, check_prose)

    if args.enum_only_exit:
        gating = [f for f in findings if f.category != 'prose']
    else:
        gating = findings
    return 2 if gating else 0


if __name__ == '__main__':
    sys.exit(main())
