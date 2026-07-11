"""read_dta_notes — dta `<characteristics>` 区二进制解析 (WP2, 2026-07-10, 计划 §3b)。

背景 (probe 实证, 见执行计划 §3b probe 结果台账):
    Stata variable notes 存 dta 的 characteristics 层 (`<ch>` 块, char 名
    note0=计数 / note1..noteN=正文)。**pyreadstat 1.3.4 与 pandas read_stata
    均无 variable notes 读回通道** (pyreadstat `meta.notes` 仅 `_dta` 文件级)。
    本工具直接解析 dta117/118/119 二进制 `<characteristics>` 区, 作为
    `notes list` log 扫描之外的**第三重独立核验通道** (WP5 注入后硬验收用)。

用法 (从 repo 根):
    python -m news_process.scripts.audit.read_dta_notes <dta_path>            # 逐变量 note 计数
    python -m news_process.scripts.audit.read_dta_notes <dta_path> --var X    # 单变量全文
    python -m news_process.scripts.audit.read_dta_notes <dta_path> --json OUT # 全量 JSON 导出
    python -m news_process.scripts.audit.read_dta_notes <dta_path> --reassemble --var X
                                                       # 按 note# 排序拼回完整长注释

格式依据 (Stata dta 文件格式 spec):
    <ch> 块 = 4 字节内容长度 (按 <byteorder> LSF/MSF) + 内容; 内容 = varname
    (118/119: 129 字节 / 117: 33 字节, NUL 截断) + charname (同宽) + 数据。
    `_dta` 伪变量名 = 文件级 notes。本工具只读不写, 对生产 dta 零风险。
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from typing import Dict, Tuple


def _detect_layout(raw: bytes) -> Tuple[int, str]:
    """返回 (name_field_width, endian_char)。fail-loud: 非 117/118/119 拒解析。"""
    m = re.search(br'<release>(\d+)</release>', raw[:200])
    if not m:
        raise SystemExit('[read_dta_notes] 非 dta117/118/119 XML 头 (无 <release>) — 拒解析')
    release = int(m.group(1))
    if release in (118, 119):
        width = 129
    elif release == 117:
        width = 33
    else:
        raise SystemExit(f'[read_dta_notes] 不支持的 dta release={release} (仅 117/118/119)')
    mo = re.search(br'<byteorder>(MSF|LSF)</byteorder>', raw[:200])
    endian = '<' if (mo is None or mo.group(1) == b'LSF') else '>'
    return width, endian


def read_characteristics(dta_path: str) -> Dict[str, Dict[str, str]]:
    """解析 <characteristics> 区 → {varname: {charname: content}} (含 `_dta` 文件级)。"""
    with open(dta_path, 'rb') as f:
        raw = f.read()
    width, endian = _detect_layout(raw)
    start = raw.find(b'<characteristics>')
    if start < 0:
        raise SystemExit('[read_dta_notes] 无 <characteristics> 区 — dta 损坏或格式异常')
    # NIT 整改 (2026-07-11): 不再预先 find(b'</characteristics>') 取**首次出现**
    # 定界 — note 正文若字面含该 ASCII 序列 (生成端全角中和规则不拦 '<' '>' '/')
    # 会使解析提前截断、少计 note 段 (对账伪红)。<ch> 块自带 4 字节长度前缀 →
    # 逐块跳读, 块内容里的任何字面量都不会被误认作区定界; 循环终止后强校验
    # 紧邻的闭合标记 (fail-loud, 防长度字段损坏时静默半读)。
    out: Dict[str, Dict[str, str]] = {}
    pos = start + len(b'<characteristics>')
    while raw[pos:pos + 4] == b'<ch>':
        pos += 4
        (length,) = struct.unpack(endian + 'I', raw[pos:pos + 4])
        pos += 4
        payload = raw[pos:pos + length]
        pos += length
        if raw[pos:pos + 5] != b'</ch>':
            raise SystemExit(f'[read_dta_notes] <ch> 块闭合标记缺失 @ offset {pos} — 长度字段损坏?')
        pos += 5
        varname = payload[:width].split(b'\0')[0].decode('utf-8', 'replace')
        charname = payload[width:2 * width].split(b'\0')[0].decode('utf-8', 'replace')
        content = payload[2 * width:].split(b'\0')[0].decode('utf-8', 'replace')
        out.setdefault(varname, {})[charname] = content
    if raw[pos:pos + len(b'</characteristics>')] != b'</characteristics>':
        raise SystemExit(f'[read_dta_notes] </characteristics> 闭合标记缺失 @ offset {pos} '
                         '— <ch> 块序列后未紧跟区闭合, dta 损坏或格式异常')
    return out


_NOTE_NUM_RE = re.compile(r'^note(\d+)$')


def notes_only(chars: Dict[str, Dict[str, str]]) -> Dict[str, Dict[int, str]]:
    """滤出 note 型 characteristics → {varname: {note#: text}} (note0 计数不含)。"""
    out: Dict[str, Dict[int, str]] = {}
    for var, d in chars.items():
        for cname, content in d.items():
            m = _NOTE_NUM_RE.match(cname)
            if m and int(m.group(1)) > 0:
                out.setdefault(var, {})[int(m.group(1))] = content
    return out


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, OSError):
        pass
    ap = argparse.ArgumentParser(
        prog='python -m news_process.scripts.audit.read_dta_notes',
        description='dta characteristics 区二进制解析 — Stata variable notes 独立读回通道 (只读)')
    ap.add_argument('dta_path')
    ap.add_argument('--var', help='只输出该变量 (dta 短名) 的 notes 全文')
    ap.add_argument('--json', dest='json_out', help='全量 notes 导出为 JSON 文件')
    ap.add_argument('--reassemble', action='store_true',
                    help='按 note# 排序把各段拼回连续文本 (段间无分隔符, 生成端按字节切段)。'
                         '⚠ 拼回结果 ≠ 中和后源文本的字节级全等: ① 段首守卫注入的 U+3000 '
                         '全角空格混在正文里 (生成端 _guard_note_segment); ② 纯空白段在生成端'
                         '被丢弃 (_split_note_segments)。做全等断言须先剥 U+3000/容忍空白段缺失。')
    args = ap.parse_args(argv)

    chars = read_characteristics(args.dta_path)
    notes = notes_only(chars)
    dta_level = notes.pop('_dta', None)

    if args.json_out:
        with open(args.json_out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump({v: {str(k): t for k, t in sorted(d.items())} for v, d in sorted(notes.items())},
                      f, ensure_ascii=False, indent=2)
        print(f'JSON written: {args.json_out}')

    if args.var:
        d = notes.get(args.var)
        if d is None:
            print(f'NO_NOTES_FOR_VAR={args.var}')
            return 1
        if args.reassemble:
            print(''.join(t for _, t in sorted(d.items())))
        else:
            for k, t in sorted(d.items()):
                print(f'{args.var}:note{k}: {t}')
        return 0

    total_notes = sum(len(d) for d in notes.values())
    for var in sorted(notes):
        print(f'{var}\t{len(notes[var])}')
    print(f'SUMMARY vars_with_notes={len(notes)} total_note_segments={total_notes}'
          + (f' dta_level_notes={len(dta_level)}' if dta_level else ''))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
