"""codebook_longdesc — 家族长文库组装引擎 (WP1, 2026-07-10 执行计划 §1/§2/§4)。

权威口径 = scripts/audit/STATA_VARATTR_AND_CODEBOOK_LONGDESC_EXECUTION_PLAN_2026-07-10.md
(v2.9 八轮 21 路评审收口)。本模块是**叶模块** (镜像 bert_distribution.py 先例):
不 import codebook/encode/stata_export, 全部输入参数注入 → panel-无关纯函数,
WP6 可从 company_listed_bank / company_tax_bank 管道传入其 panel 与 longdesc_dir 复用。

核心职责:
1. 家族长文库 loader (config/codebook_longdesc/{_index.json, F*.md}) —
   frontmatter (YAML) + "## CORE" 家族核心长文 + "## VAR: <panel 实名>" 逐列差分段
   + <!-- rendered-citations:begin/end --> 机器渲染尾节 (人工区禁改)。
2. 五段确定性组装 (§1 公式): 家族核心长文 + 变体差分段 + 计算链路段 (机械)
   + 动态统计段 (四态) + 引文段 (frontmatter citations 机器渲染 APA 7)。
3. 字数双闸 (v2.7 汉字口径): CJK 汉字数 gate — standard ≥1000 / core ≥5000;
   段落闸 (standard 核心 ≥700 + 差分 ≥350 / core ≥4200 + ≥900) 同为硬闸 (§1 互锁)。
   fail-loud 分级: 家族 status=='final' 不足 → SystemExit(1); 'draft' → 告警计数。
4. 占位符协议: 动态统计占位符 = `{stats:<panel列名>}`; 一切未知
   `{[A-Za-z_]+:...}` 语法 fail-loud (拼错不许静默穿过, §1 宽残留 gate)。
5. 引文机器渲染 APA 7 (§2): citations 逐条按 type ∈ {journal, wp, arxiv, book}
   分模板渲染, 每条末尾恒带 https://doi.org/<DOI>; 渲染段可物化回写家族 md 尾节
   (materialize_rendered_citations, 幂等)。

⚠ 铁律 (§0): 本模块与 codebook.py::_compose_long_description 挂载点**刻意不进**
get_variable_metadata_dict — 导出路径 (stata_export/export/controls) 不 import 本模块
(gate: tests/test_codebook_longdesc.py::test_export_paths_do_not_import_composer)。
⚠ 字面 CJK 端点字符禁入源码 (GBK 控制台回显崩溃, v2.7 实测) — 一律 \\u 转义。
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ============================================================================
# 常量 (§1 字数闸 / 占位符 / 渲染尾节标记)
# ============================================================================

# CJK 汉字计数 (v2.7 用户修订, 计量单位=汉字): Unicode 基本区 U+4E00–U+9FFF
# + 扩展 A U+3400–U+4DBF; 英文/数字/标点/全角符号/空白均不计。
# ⚠ 必须 \u 转义形式 — 字面 CJK 端点字符在 Windows GBK 控制台回显即 UnicodeEncodeError
#   (计划 §1 v2.7 实测踩中); \u4e00-\u9fff / \u3400-\u4dbf 与计划字面口径逐码点等价。
_CJK_RE = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf]')

# 动态统计占位符 (自定语法, 写入家族 md 模板说明): {stats:<panel列名>}
_STATS_PLACEHOLDER_RE = re.compile(r'\{stats:([A-Za-z0-9_]+)\}')
# 宽占位符残留 gate (§1): 一切 {word:...} 型未知语法 (含拼错 {STAT:...}/{Stats:...})。
# 2026-07-11 P2-④ 收紧: 原 r'\{[A-Za-z_]+:[^}]*\}' 对四类拼错假阴性 —
#   ① 名带数字 '{stats2:col}'/'{2stats:col}'; ② 冒号前空格 '{stats :col}';
#   ③ 未闭合 '{stats:col' (行内到行尾无 }); ④ 全角花括号 '｛stats:col｝'
#   (全角括号一律 ｛/｝ 转义, 镜像 CJK 端点字符禁字面铁律)。
# 主 regex 覆盖闭合形态 (①②); 未闭合/全角另设两条, find_placeholder_residue 三路合并。
_WIDE_PLACEHOLDER_RE = re.compile(r'\{[A-Za-z0-9_]+\s*:[^}\n]*\}')
_UNCLOSED_PLACEHOLDER_RE = re.compile(r'\{[A-Za-z0-9_]+\s*:[^{}\n]*(?=\n|$)')
_FULLWIDTH_PLACEHOLDER_RE = re.compile(
    # U+FF5B/U+FF5D 全角花括号变体: 闭合或未闭合到行尾 (\u 转义, 源码零字面全角括号)
    '\uFF5B[^\uFF5D\n]*(?:\uFF5D|(?=\n)|$)'
)


def find_placeholder_residue(text: str) -> List[str]:
    """宽占位符残留三路合并检测 (§1 拼错不许静默穿过; P2-④ 收紧后的唯一入口)。

    返回全部命中片段 (闭合拼错 / 未闭合 / 全角变体); 空列表 = 干净。
    """
    t = text or ''
    out: List[str] = []
    out.extend(_WIDE_PLACEHOLDER_RE.findall(t))
    # 未闭合形态: 排除已被闭合形态覆盖的位置 (闭合 regex 命中的片段自身含 '}' 不会重报)
    closed_spans = [m.span() for m in _WIDE_PLACEHOLDER_RE.finditer(t)]
    for m in _UNCLOSED_PLACEHOLDER_RE.finditer(t):
        if not any(a <= m.start() < b for a, b in closed_spans):
            out.append(m.group(0))
    out.extend(_FULLWIDTH_PLACEHOLDER_RE.findall(t))
    return out


RENDERED_BEGIN = '<!-- rendered-citations:begin -->'
RENDERED_END = '<!-- rendered-citations:end -->'

# 字数闸地板 (v2.7 汉字口径; 下限=验收地板非写作目标, §6 写手铁律)
TOTAL_CJK_FLOOR = {'standard': 1000, 'core': 5000, 'pending': 1000}
CORE_SEG_CJK_FLOOR = {'standard': 700, 'core': 4200}      # 家族核心长文段
VAR_SEG_CJK_FLOOR = {'standard': 350, 'core': 900}        # 变体差分段
# 引文段自身质量约束 (§1: 条数 + 渲染字符; 汉字贡献≈0 刻意不计入汉字闸)
CITATION_MIN = {'standard': (3, 300), 'core': (10, 1000), 'pending': (3, 300)}

_VALID_TIERS = frozenset({'core', 'standard', 'pending'})
_VALID_CITATION_TYPES = frozenset({'journal', 'wp', 'arxiv', 'book'})

# T=2 dev 尾注 (§7.8 诚实披露, 动态统计段一律带)
_STATS_FOOTNOTE = '注: 以上为生成期从面板实测注入的开发期数值, 生产 T=19 重生后以实读为准。'
_PENDING_SENTINEL = (
    '本列为外部财务面板哨兵列 (tier=pending): 待外部财务面板接入后构造, '
    '当前面板不产生数值, 故本段不注入实测统计; 财务面板接入后本段将自动改为生成期实测统计。'
)

# 组装段落中文小标题 (组装产物格式铁律: 纯文本 + 段首中文小标题, §1 v2.5)。
# ⚠ 契约裁决 (2026-07-11 P1-1 双重标题整改): 前两段 (构念与来源/变体差分) 的段首
# 小标题**归写手/骨架正文** — 组装器不再额外前置, 只负责机械段标题
# (计算链路/动态统计/学术文献)。骨架播种模板与 _TEMPLATE_family.md 已同步带标题;
# 组装器加 _DOUBLE_SEG_TITLE_RE gate: 双重标题 fail-loud (防单侧回归)。
_SEG_TITLES = ('【构念与来源】', '【变体差分】', '【计算链路】', '【动态统计】', '【学术文献】')
# 双重段首标题 gate: 同一【...】标题紧邻重复 (中间至多空白) = 契约两侧同时注入的实锤
_DOUBLE_SEG_TITLE_RE = re.compile(r'【([^】\n]{1,24})】\s*\n\s*【\1】')


# ============================================================================
# 基础工具
# ============================================================================

def count_cjk(text: str) -> int:
    """CJK 汉字数 (§1 唯一字数计量口径)。None/空 → 0。"""
    if not text:
        return 0
    return len(_CJK_RE.findall(text))


def default_longdesc_dir() -> str:
    """主线长文库默认落点 = news_process/config/codebook_longdesc。"""
    _here = os.path.dirname(os.path.abspath(__file__))          # pipeline/panel
    _pkg_root = os.path.dirname(os.path.dirname(_here))          # news_process
    return os.path.join(_pkg_root, 'config', 'codebook_longdesc')


def normalize_doi(doi: str) -> str:
    """DOI 归一 (与 audit_dois.clean_doi().lower() 同口径 — 断言①两侧必须同归一)。"""
    d = str(doi).strip()
    d = re.sub(r'[.,;]+$', '', d)
    if '(' not in d:  # 老式 Elsevier DOI 含 (YY), 不可截断 (镜像 audit_dois.clean_doi)
        d = re.sub(r'[)\]]+$', '', d)
    return d.strip('`*。）)').lower()


# ============================================================================
# 引文机器渲染 (§2.1 APA 7 分模板; 每条末尾恒带 doi.org 链接)
# ============================================================================

def validate_citation(c: Dict[str, Any], family_id: str = '?') -> List[str]:
    """校验单条 citation 条目结构; 返回违规清单 (空=合格)。

    DOI 必填铁律 (§2.1): 无 doi 条目须同时带 no_doi_ack (台账编号) + alt_link
    (替代可访问链接) — 否则该条目同时逃逸差集断言与 extract_refs, fail-loud。
    """
    errs: List[str] = []
    if not isinstance(c, dict):
        return [f'[{family_id}] citation 条目非 dict: {c!r}']
    ctype = c.get('type', '')
    if ctype not in _VALID_CITATION_TYPES:
        errs.append(f"[{family_id}] citation type 非法: {ctype!r} (须 ∈ {sorted(_VALID_CITATION_TYPES)})")
    for k in ('authors', 'year', 'title'):
        if not str(c.get(k, '') or '').strip():
            errs.append(f'[{family_id}] citation 缺必填字段 {k}: {c.get("title", c)!r}')
    doi = str(c.get('doi', '') or '').strip()
    if not doi:
        if not str(c.get('no_doi_ack', '') or '').strip() or not str(c.get('alt_link', '') or '').strip():
            errs.append(
                f'[{family_id}] citation 无 doi 且缺 no_doi_ack/alt_link (DOI 必填铁律 §2.1): '
                f'{c.get("title", "?")!r}'
            )
    return errs


def render_citation_apa(c: Dict[str, Any]) -> str:
    """按 type 分模板渲染单条 APA 7 文本 (纯文本单行, 末尾恒带 doi.org 链接)。"""
    authors = str(c.get('authors', '')).strip().rstrip('.')
    year = c.get('year', '')
    title = str(c.get('title', '')).strip().rstrip('.')
    venue = str(c.get('venue', '') or '').strip().rstrip('.')
    ctype = c.get('type', 'journal')
    doi = str(c.get('doi', '') or '').strip()

    # APA 7 §9.19: 题名以 ?/! 收尾时该终止标点**取代**句点, 不再另加 '.'
    # (2026-07-18 终局签核 P2: 原实现恒加 '.' 致全库 305 处 'Title?.' 违反)。
    _tp = '' if title[-1:] in '?!' else '.'
    head = f'{authors}. ({year}). {title}{_tp}'
    if ctype == 'journal':
        seg = venue
        vol = c.get('vol', '')
        issue = c.get('issue', '')
        pages = c.get('pages_or_artno', '')
        if vol:
            seg += f', {vol}'
            if issue:
                seg += f'({issue})'
        if pages:
            seg += f', {pages}'
        body = f'{head} {seg}.' if seg else head
    elif ctype == 'wp':
        seg = venue or 'Working Paper'
        pages = c.get('pages_or_artno', '')
        if pages:
            seg += f' No. {pages}'
        body = f'{head} {seg} [Working Paper].'
    elif ctype == 'arxiv':
        seg = venue or 'arXiv'
        body = f'{head} {seg} [Preprint].'
    else:  # book
        seg = venue
        body = f'{head} {seg}.' if seg else head

    if doi:
        return f'{body} https://doi.org/{doi}'
    # no-DOI ack 条目: 渲染时带替代链接与 ack 编号 (§2.1)
    ack = str(c.get('no_doi_ack', '') or '').strip()
    alt = str(c.get('alt_link', '') or '').strip()
    return f'{body} [no-DOI ack #{ack}] {alt}'


def render_citations_block(citations: List[Dict[str, Any]]) -> str:
    """渲染引文段 (逐条一行, 保持 frontmatter 次序 — 写手按年份倒序排)。"""
    return '\n'.join(render_citation_apa(c) for c in (citations or []))


def rendered_dois(citations: List[Dict[str, Any]]) -> set:
    """citations 条目的归一 DOI 集 (无 doi 的 ack 条目不入集)。"""
    out = set()
    for c in citations or []:
        d = str(c.get('doi', '') or '').strip()
        if d:
            out.add(normalize_doi(d))
    return out


# ============================================================================
# 家族 md 解析 (frontmatter + CORE/VAR 节 + 渲染尾节)
# ============================================================================

@dataclass
class FamilyDoc:
    """单个家族 md 的解析产物。"""
    family_id: str
    path: str
    frontmatter: Dict[str, Any]
    core_text: str
    var_sections: Dict[str, str]
    rendered_block: Optional[str]        # 尾节内文本 (不含 fence 标记); None=尾节缺失
    human_zone: str                      # 渲染尾节以外的全部正文 (lint 域)
    status: str = 'draft'
    var_notes: Dict[str, str] = field(default_factory=dict)  # VAR 节内联【备注】通道 (P2-②)


_HEADING_RE = re.compile(r'^## (CORE|VAR: .+?)\s*$', re.MULTILINE)
# VAR 节内联备注通道 (P2-② 2026-07-11): 节内行首『【备注】<正文>』被提取为该列的
# codebook 备注字段 (替换 _AUTO_INFER_NOTE); 行本体保留在差分段散文中 (不剥除)。
_VAR_NOTE_RE = re.compile(r'^【备注】\s*(\S.*)$', re.MULTILINE)


def parse_family_md(path: str, family_id: str = '') -> FamilyDoc:
    """解析家族 md。frontmatter 解析失败 = SystemExit(1) (§2.3 fail-loud,
    try/except 跳过 = 与 fail-open 同构的静默漏检)。

    2026-07-11 加固: ① 重复 heading (两个 ## CORE / 同名 ## VAR:) fail-loud —
    原 dict 覆写 last-wins 会静默丢弃前节人工正文 (P2-③); ② UTF-8 BOM 容忍
    (PowerShell 5.1 默认 utf8 写出带 BOM, 原被误诊为"缺 frontmatter 定界")。
    """
    with open(path, encoding='utf-8') as f:
        raw = f.read()
    # UTF-8 BOM 容忍 (utf-8-sig 写出的合法 md 不再误诊; U+FEFF 用转义防不可见字面量)
    raw = raw.lstrip('\ufeff')
    fid = family_id or os.path.basename(path).split('_')[0]

    m = re.match(r'^---\s*\n(.*?)\n---\s*\n?', raw, re.DOTALL)
    if not m:
        raise SystemExit(f'[codebook_longdesc] 家族 md 缺 frontmatter 定界 (---): {path}')
    try:
        import yaml
        fm = yaml.safe_load(m.group(1))
    except Exception as e:  # noqa: BLE001
        raise SystemExit(f'[codebook_longdesc] 家族 md frontmatter YAML 解析失败: {path} — {e}')
    if not isinstance(fm, dict):
        raise SystemExit(f'[codebook_longdesc] 家族 md frontmatter 非 mapping: {path}')

    body = raw[m.end():]

    # 渲染尾节切分 (人工区禁改; 组装时剥除 fence 标记)
    rendered_block: Optional[str] = None
    human_zone = body
    b0 = body.find(RENDERED_BEGIN)
    if b0 >= 0:
        b1 = body.find(RENDERED_END, b0)
        if b1 < 0:
            raise SystemExit(f'[codebook_longdesc] 渲染尾节 begin 无匹配 end: {path}')
        rendered_block = body[b0 + len(RENDERED_BEGIN):b1].strip('\n')
        human_zone = body[:b0] + body[b1 + len(RENDERED_END):]

    # heading 精确匹配切分 (## CORE / ## VAR: <panel 实名>)。
    # P2-③ (2026-07-11): 重复 heading fail-loud — 原 dict 覆写 last-wins 会把前一节
    # 人工正文无声丢弃 (列集合三处全等 gate 与字数闸均察觉不到), 与模块 fail-loud 哲学相悖。
    core_text = ''
    core_seen = False
    var_sections: Dict[str, str] = {}
    var_notes: Dict[str, str] = {}
    matches = list(_HEADING_RE.finditer(human_zone))
    for i, hm in enumerate(matches):
        seg_start = hm.end()
        seg_end = matches[i + 1].start() if i + 1 < len(matches) else len(human_zone)
        seg = human_zone[seg_start:seg_end].strip('\n').strip()
        head = hm.group(1)
        if head == 'CORE':
            if core_seen:
                raise SystemExit(
                    f'[codebook_longdesc] 家族 md 出现重复 "## CORE" 节 '
                    f'(前节人工正文将被静默丢弃, fail-loud P2-③): {path}'
                )
            core_seen = True
            core_text = seg
        else:
            col = head[len('VAR: '):].strip()
            if col in var_sections:
                raise SystemExit(
                    f'[codebook_longdesc] 家族 md 出现重复 "## VAR: {col}" 节 '
                    f'(前节人工正文将被静默丢弃, fail-loud P2-③): {path}'
                )
            var_sections[col] = seg
            # 内联备注通道 (P2-②): 行首【备注】提取, 多行命中取首行 (写手规范一列一条)
            nm = _VAR_NOTE_RE.search(seg)
            if nm:
                var_notes[col] = nm.group(1).strip()

    fm_fid = str(fm.get('family_id', fid))
    # NIT (2026-07-11): frontmatter family_id 与 _index 键双头一致性 — 漂移时全部
    # 告警/违规消息前缀会指向错误家族号, 静默通过所有闸 → fail-loud。
    if family_id and fm.get('family_id') is not None and fm_fid != str(family_id):
        raise SystemExit(
            f'[codebook_longdesc] frontmatter family_id={fm_fid!r} != _index 键 '
            f'{family_id!r} (双头漂移, 报错定位将指向错误家族): {path}'
        )

    return FamilyDoc(
        family_id=fm_fid,
        path=path,
        frontmatter=fm,
        core_text=core_text,
        var_sections=var_sections,
        rendered_block=rendered_block,
        human_zone=human_zone,
        var_notes=var_notes,
    )


# 人工区 markdown 结构语法 lint (§1 组装产物格式铁律: 禁 #/**/表格/fence)
_MD_STRUCT_PATTERNS: Tuple[Tuple[str, re.Pattern], ...] = (
    ('heading(#)', re.compile(r'^#', re.MULTILINE)),
    ('bold(**)', re.compile(r'\*\*')),
    ('table(|)', re.compile(r'^\s*\|', re.MULTILINE)),
    ('fence(```)', re.compile(r'^```', re.MULTILINE)),
)


def lint_markdown_structures(text: str, where: str) -> List[str]:
    """人工区 (CORE/VAR 节正文) markdown 结构语法 lint; 返回违规清单。"""
    out = []
    for name, pat in _MD_STRUCT_PATTERNS:
        if pat.search(text or ''):
            out.append(f'{where}: 人工区含 markdown 结构语法 {name} (§1 纯文本铁律)')
    return out


def lint_doiorg_outside_tail(fam: FamilyDoc) -> List[str]:
    """正文散文禁 doi.org 链接 (§2.6): 只准出现在渲染尾节内。"""
    if 'doi.org/' in (fam.human_zone or ''):
        return [f'{fam.family_id}: 渲染尾节外出现 doi.org 链接 (§2.6 lint, 会污染 extract_refs)']
    return []


# ============================================================================
# 长文库 loader
# ============================================================================

@dataclass
class LongdescLibrary:
    """家族长文库 (loader 产物)。"""
    longdesc_dir: str
    index: Dict[str, Any]
    families: Dict[str, FamilyDoc]                # 仅含 md 实存且解析成功的家族
    missing_families: List[str] = field(default_factory=list)
    col_to_family: Dict[str, str] = field(default_factory=dict)
    structural_whitelist: frozenset = frozenset()
    load_warnings: List[str] = field(default_factory=list)

    def family_of(self, col: str) -> Optional[FamilyDoc]:
        fid = self.col_to_family.get(col)
        return self.families.get(fid) if fid else None

    def tier_of(self, col: str) -> str:
        fid = self.col_to_family.get(col)
        if not fid:
            return 'standard'
        tiers = (self.index.get('families', {}).get(fid, {}) or {}).get('tier_by_col', {}) or {}
        t = tiers.get(col, 'standard')
        return t if t in _VALID_TIERS else 'standard'

    def status_of(self, col: str) -> str:
        fid = self.col_to_family.get(col)
        if not fid:
            return 'draft'
        return str((self.index.get('families', {}).get(fid, {}) or {}).get('status', 'draft'))

    def pending_cols(self) -> List[str]:
        out = []
        for fid, meta in (self.index.get('families', {}) or {}).items():
            for col, t in ((meta or {}).get('tier_by_col', {}) or {}).items():
                if t == 'pending':
                    out.append(col)
        return sorted(set(out))


def verify_family_column_consistency(
    index_entry: Dict[str, Any],
    fam: FamilyDoc,
) -> Tuple[List[str], List[str]]:
    """列集合三处全等 gate (§5 WP1): _index.columns == frontmatter.columns
    == md "## VAR:" 节集。

    Returns:
        (fatal, draft_warnings): index↔frontmatter 不等 / 幻影 VAR 节 = fatal (机械骨架
        必须一致, 拼错面板名不许静默); VAR 节缺失 = draft 告警 (final 由调用方升级为 fatal)。
    """
    fatal: List[str] = []
    warns: List[str] = []
    idx_cols = set(index_entry.get('columns', []) or [])
    fm_cols = set(fam.frontmatter.get('columns', []) or [])
    var_cols = set(fam.var_sections)
    if idx_cols != fm_cols:
        fatal.append(
            f'{fam.family_id}: _index.columns != frontmatter.columns '
            f'(index-only={sorted(idx_cols - fm_cols)}, fm-only={sorted(fm_cols - idx_cols)})'
        )
    phantom = var_cols - fm_cols
    if phantom:
        fatal.append(f'{fam.family_id}: "## VAR:" 节含 frontmatter.columns 外幻影列 {sorted(phantom)}')
    missing = fm_cols - var_cols
    if missing:
        warns.append(f'{fam.family_id}: 缺 "## VAR:" 节 (draft 告警/final 崩): {sorted(missing)}')
    return fatal, warns


def load_library(longdesc_dir: Optional[str]) -> Optional[LongdescLibrary]:
    """加载家族长文库。缺目录 / 缺 _index.json → None (调用方回退现状短描述 + 告警计数)。

    fail-loud: _index.json / frontmatter 解析失败、final 家族 md 缺失或列集不一致
    → SystemExit(1)。draft 家族的缺节/缺文件降级为 load_warnings 告警计数。
    """
    if not longdesc_dir:
        return None
    index_path = os.path.join(longdesc_dir, '_index.json')
    if not os.path.isdir(longdesc_dir) or not os.path.exists(index_path):
        return None
    try:
        with open(index_path, encoding='utf-8') as f:
            index = json.load(f)
    except Exception as e:  # noqa: BLE001
        raise SystemExit(f'[codebook_longdesc] _index.json 解析失败 (fail-loud): {index_path} — {e}')

    lib = LongdescLibrary(
        longdesc_dir=longdesc_dir,
        index=index,
        families={},
        structural_whitelist=frozenset(index.get('structural_whitelist', []) or []),
    )
    for fid, meta in sorted((index.get('families', {}) or {}).items()):
        meta = meta or {}
        status = str(meta.get('status', 'draft'))
        cols = list(meta.get('columns', []) or [])
        # P2-⑥ (2026-07-11): tier_by_col 键须 ⊆ columns — 只登记在 tier_by_col 而漏出
        # columns 的 pending 列会被 pending_cols() 列出但 family_of() 返 None →
        # compose_pending_appendix 静默跳过, 该列从一切产物无声消失 (幽灵列防线)。
        ghost = set(meta.get('tier_by_col') or {}) - set(cols)
        if ghost:
            raise SystemExit(
                f'[codebook_longdesc] {fid}: tier_by_col 含 columns 外幽灵键 '
                f'{sorted(ghost)} (P2-⑥ fail-loud, 防 pending 列无声消失)'
            )
        for c in cols:
            if c in lib.col_to_family:
                raise SystemExit(
                    f'[codebook_longdesc] 列 {c!r} 被两家族重复收录: '
                    f'{lib.col_to_family[c]} 与 {fid} (§6 守恒快检 Σ 盲区)'
                )
            lib.col_to_family[c] = fid
        fpath = os.path.join(longdesc_dir, str(meta.get('file', f'{fid}.md')))
        if not os.path.exists(fpath):
            if status == 'final':
                raise SystemExit(f'[codebook_longdesc] final 家族 md 缺失: {fid} → {fpath}')
            lib.missing_families.append(fid)
            lib.load_warnings.append(f'{fid}: 家族 md 缺失 (draft, 其列回退现状短描述)')
            continue
        fam = parse_family_md(fpath, family_id=fid)
        fam.status = status
        fatal, warns = verify_family_column_consistency(meta, fam)
        if fatal:
            raise SystemExit('[codebook_longdesc] 列集合三处全等 gate 失败:\n  ' + '\n  '.join(fatal))
        if warns:
            if status == 'final':
                raise SystemExit('[codebook_longdesc] final 家族缺 VAR 节:\n  ' + '\n  '.join(warns))
            lib.load_warnings.extend(warns)
        # 人工区 lint: markdown 结构语法 + 尾节外 doi.org (draft 告警 / final 崩)
        lint = (lint_markdown_structures(fam.core_text, f'{fid}/CORE')
                + [v for col, txt in sorted(fam.var_sections.items())
                   for v in lint_markdown_structures(txt, f'{fid}/VAR:{col}')]
                + lint_doiorg_outside_tail(fam))
        if lint:
            if status == 'final':
                raise SystemExit('[codebook_longdesc] final 家族 lint 失败:\n  ' + '\n  '.join(lint))
            lib.load_warnings.extend(lint)
        lib.families[fid] = fam
    return lib


# ============================================================================
# 渲染物化回写 (§2.1 v2.3 P0: audit_dois 核验域的扫描对象 = 渲染尾节)
# ============================================================================

def materialize_rendered_citations(fam: FamilyDoc) -> bool:
    """把 frontmatter citations 的机器渲染段物化回写为家族 md 尾节 (幂等)。

    Returns:
        True = 本次发生了写盘 (尾节缺失或陈旧); False = 已最新, no-op。
    """
    block = render_citations_block(fam.frontmatter.get('citations', []) or [])
    if fam.rendered_block == block:
        return False
    # NIT (2026-07-11): newline='' 按原样字节读 — 原文本模式 universal-newline 读入会把
    # 人工区 CRLF 整文件归一为 LF (与"人工区禁改"承诺相抵 + git diff 噪声); 尾节自身仍写 LF。
    with open(fam.path, encoding='utf-8', newline='') as f:
        raw = f.read()
    new_tail = f'{RENDERED_BEGIN}\n{block}\n{RENDERED_END}'
    b0 = raw.find(RENDERED_BEGIN)
    if b0 >= 0:
        b1 = raw.find(RENDERED_END, b0)
        if b1 < 0:
            raise SystemExit(f'[codebook_longdesc] 渲染尾节 begin 无匹配 end: {fam.path}')
        new_raw = raw[:b0] + new_tail + raw[b1 + len(RENDERED_END):]
    else:
        new_raw = raw.rstrip('\n') + '\n\n' + new_tail + '\n'
    with open(fam.path, 'w', encoding='utf-8', newline='') as f:
        f.write(new_raw)
    fam.rendered_block = block
    return True


def materialize_all(lib: LongdescLibrary) -> int:
    """全库渲染物化 (批收尾/生产入口调用); 返回本次写盘家族数。"""
    n = 0
    for fid in sorted(lib.families):
        if materialize_rendered_citations(lib.families[fid]):
            n += 1
    return n


# ============================================================================
# 动态统计段 (§1 四态)
# ============================================================================

def render_stats_segment(col: str, panel, tier: str) -> str:
    """动态统计段四态渲染 (§1)。

    ④ tier=pending **且列不在 panel** → 哨兵文本 (不触 ①);
    ① col 不在 panel 且非 pending → SystemExit(1);
    ② 全 NaN → "全缺失" + T=2 尾注;
    ③ 正常 → dtype/min/max/mean/缺失率/非缺失 n + "生产 T=19 重生后以实读为准"尾注。

    P2-① (2026-07-11): pending 分支按 **col∈panel 实测**而非 tier 静态判 —
    财务面板接入后 pending 列实存时, 本段自动改渲实测统计 (哨兵文本承诺兑现),
    不再与面板实况矛盾; _index 的 tier 升 core 由重跑 WP0 完成 (告警在组装层)。
    """
    import pandas as pd
    if tier == 'pending' and (panel is None or col not in getattr(panel, 'columns', [])):
        return _PENDING_SENTINEL
    if panel is None or col not in panel.columns:
        raise SystemExit(
            f'[codebook_longdesc] 动态统计段引用列 {col!r} 不在 panel 且非 pending '
            f'(四态①, 生成期 fail-loud)'
        )
    s = panel[col]
    n = len(s)
    n_valid = int(s.notna().sum())
    miss_rate = (1.0 - n_valid / n) if n else 0.0
    if n_valid == 0:
        return f'全缺失 (非缺失 n=0, 观测数={n})。{_STATS_FOOTNOTE}'
    parts = [f'dtype={s.dtype}', f'非缺失 n={n_valid}', f'缺失率={miss_rate:.2%}']
    if pd.api.types.is_numeric_dtype(s):
        v = s.dropna()
        parts += [f'min={v.min():.4f}', f'mean={v.mean():.4f}', f'max={v.max():.4f}']
    else:
        v = s.dropna()
        parts.append(f'唯一值数={v.nunique()}')
    return '; '.join(parts) + f'。{_STATS_FOOTNOTE}'


def substitute_stats_placeholders(text: str, panel, tier_lookup) -> str:
    """替换文本内 {stats:col} 占位符 → 四态渲染; 残留未知占位符 fail-loud (宽 gate)。

    Args:
        tier_lookup: callable(col) -> tier (占位符引用列若为 pending 走哨兵态)。
    """
    def _sub(m: re.Match) -> str:
        ref = m.group(1)
        return render_stats_segment(ref, panel, tier_lookup(ref))

    out = _STATS_PLACEHOLDER_RE.sub(_sub, text or '')
    residue = find_placeholder_residue(out)   # P2-④ 三路合并 (闭合拼错/未闭合/全角)
    if residue:
        raise SystemExit(
            f'[codebook_longdesc] 未知占位符语法残留 (宽 gate, 拼错不许静默穿过): {residue[:5]}'
        )
    return out


# ============================================================================
# 五段组装 (§1 公式) — panel-无关纯函数 (panel 由参数注入)
# ============================================================================

def _mechanical_chain_segment(fam: FamilyDoc, col: str, source_stage: str) -> str:
    """计算链路段 (机械生成): frontmatter producer/upstream + 来源阶段 + 公式。"""
    fm = fam.frontmatter
    parts = []
    if source_stage:
        parts.append(f'来源阶段: {source_stage}。')
    producer = str(fm.get('producer', '') or '').strip()
    if producer:
        parts.append(f'生产函数: {producer}。')
    upstream = fm.get('upstream', []) or []
    if upstream:
        if isinstance(upstream, str):
            upstream = [upstream]
        parts.append('上游依赖: ' + ' -> '.join(str(u) for u in upstream) + '。')
    formula = str(fm.get('formula', '') or '').strip()
    if formula:
        parts.append(f'计算公式: {formula}。')
    parts.append(f'本列 (panel 实名 {col}) 属家族 {fam.family_id}, 由上述链路机械派生。')
    return ' '.join(parts)


def compose_long_description(
    col: str,
    panel,
    library: LongdescLibrary,
    *,
    source_stage: str = '',
    counters: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """五段确定性组装 (§1 公式), 逐列产出唯一文本 (确定性: 同输入 → 字节相等)。

    panel-无关纯函数: col/panel/library 全参数注入, 不读任何主线路径常量 —
    WP6 从 company 管道传入其 panel 与 library 复用。

    Returns:
        None — col 无家族 / 家族 md 缺失 (调用方回退现状短描述 + 告警计数);
        dict — {description, unit, formula, value_range, reference_short,
                tier, family_id, cjk_total, gate_violations}。
        字数闸: status=='final' 不足 → SystemExit(1); 'draft' → 告警计数
        (counters['warnings'] 累积, 组装照常返回, 渐进批次不断链)。
        结构列白名单 (§1a.7) 豁免全部字数闸。
    """
    counters = counters if counters is not None else {}
    counters.setdefault('warnings', [])
    counters.setdefault('composed', 0)

    fam = library.family_of(col)
    if fam is None:
        return None

    tier = library.tier_of(col)
    status = fam.status
    is_structural = col in library.structural_whitelist
    # 传染规则 (§1a): core 列所在家族核心长文按 core 深度写; 其余 standard 变体免费复用
    fam_tiers = {library.tier_of(c) for c in fam.frontmatter.get('columns', []) or []}
    family_depth = 'core' if 'core' in fam_tiers else 'standard'

    tier_lookup = library.tier_of

    core_raw = fam.core_text
    var_raw = fam.var_sections.get(col, '')
    if not var_raw:
        msg = f'{fam.family_id}/{col}: 变体差分段缺失'
        if status == 'final':
            raise SystemExit(f'[codebook_longdesc] final 家族缺 VAR 节: {msg}')
        counters['warnings'].append(msg)
        var_raw = f'{_SEG_TITLES[1]}\n（草稿: 本列变体差分段尚未撰写。）'

    core_txt = substitute_stats_placeholders(core_raw, panel, tier_lookup)
    var_txt = substitute_stats_placeholders(var_raw, panel, tier_lookup)
    chain_txt = _mechanical_chain_segment(fam, col, source_stage)
    stats_txt = render_stats_segment(col, panel, tier)
    citations = fam.frontmatter.get('citations', []) or []
    cite_errs = [e for c in citations for e in validate_citation(c, fam.family_id)]
    if cite_errs:
        # NIT (2026-07-11): fail-loud 分级对齐字数闸/差集闸 — draft 家族单条畸形
        # citation 降级为告警计数 (渐进批次不断链); final 仍无条件 SystemExit。
        if status == 'final':
            raise SystemExit('[codebook_longdesc] citation 结构校验失败:\n  ' + '\n  '.join(cite_errs))
        counters['warnings'].extend(cite_errs)
    cite_txt = render_citations_block(citations)

    # ── 五段组装 (P1-1 契约裁决 2026-07-11): 前两段段首小标题归写手/骨架正文,
    #    组装器只前置机械段标题 (计算链路/动态统计/学术文献) — 双重标题根除 ──
    description = '\n\n'.join((
        core_txt,
        var_txt,
        f'{_SEG_TITLES[2]}\n{chain_txt}',
        f'{_SEG_TITLES[3]}\n{stats_txt}',
        f'{_SEG_TITLES[4]}\n{cite_txt}',
    ))

    # 双重标题 gate (P1-1 防回归): 任一【标题】紧邻自重复 = 契约两侧同时注入, 无条件崩
    dbl = _DOUBLE_SEG_TITLE_RE.search(description)
    if dbl:
        raise SystemExit(
            f'[codebook_longdesc] {fam.family_id}/{col}: 组装产物出现双重段首标题 '
            f'{dbl.group(0)!r} (P1-1 契约: 构念/变体标题归写手正文, 组装器只加机械段标题)'
        )

    # ── 字数双闸 (§1 互锁: 段落闸与总量闸同为硬闸) + 引文段质量约束 ──
    violations: List[str] = []
    if not is_structural:
        # P1-1 契约配套 lint: 写手正文须自带前两段段首小标题 (组装器不再兜底前置)。
        # 刻意降级为纯告警 (不入 violations/不崩 final): 契约裁决只硬约束"零双重标题"
        # (上方 gate); 标题缺失是可读性瑕疵非结构损坏, 入 violations 会连坐
        # batch_longdesc_gate 的 promote 判定 (g2 以 violations 计红)。
        if not core_txt.lstrip().startswith(_SEG_TITLES[0]):
            counters['warnings'].append(
                f'{fam.family_id}/{col}: 家族核心长文段未以{_SEG_TITLES[0]}开头 '
                f'(段首小标题归写手正文, P1-1 契约)'
            )
        if not var_txt.lstrip().startswith(_SEG_TITLES[1]):
            counters['warnings'].append(
                f'{fam.family_id}/{col}: 变体差分段未以{_SEG_TITLES[1]}开头 '
                f'(段首小标题归写手正文, P1-1 契约)'
            )
        cjk_core = count_cjk(core_txt)
        cjk_var = count_cjk(var_txt)
        cjk_total = count_cjk(description)
        col_depth = 'core' if tier == 'core' else 'standard'
        if cjk_core < CORE_SEG_CJK_FLOOR[family_depth]:
            violations.append(
                f'{fam.family_id}/{col}: 家族核心长文段 {cjk_core} 汉字 '
                f'< {CORE_SEG_CJK_FLOOR[family_depth]} ({family_depth} 家族段落闸)'
            )
        if cjk_var < VAR_SEG_CJK_FLOOR[col_depth]:
            violations.append(
                f'{fam.family_id}/{col}: 变体差分段 {cjk_var} 汉字 '
                f'< {VAR_SEG_CJK_FLOOR[col_depth]} ({col_depth} 列段落闸)'
            )
        if cjk_total < TOTAL_CJK_FLOOR[tier]:
            violations.append(
                f'{fam.family_id}/{col}: 组装全文 {cjk_total} 汉字 '
                f'< {TOTAL_CJK_FLOOR[tier]} ({tier} 总量闸)'
            )
        n_min, ch_min = CITATION_MIN[tier if tier in CITATION_MIN else 'standard']
        if len(citations) < n_min or len(cite_txt) < ch_min:
            violations.append(
                f'{fam.family_id}/{col}: 引文段 {len(citations)} 条/{len(cite_txt)} 字符 '
                f'< {n_min} 条/{ch_min} 字符 ({tier} 引文段质量约束)'
            )
    else:
        cjk_total = count_cjk(description)

    if violations:
        if status == 'final':
            raise SystemExit(
                '[codebook_longdesc] final 家族字数/引文闸失败 (fail-loud 分级 §1):\n  '
                + '\n  '.join(violations)
            )
        counters['warnings'].extend(violations)

    # ── 12 字段机械回填 (§4): 单位/公式=frontmatter (防双头: 存在 frontmatter 即
    #    不消费 _index 的 *_draft 字段); 取值范围=动态统计段同源; 学术引用=短版 3-5 条 ──
    unit = str(fam.frontmatter.get('unit', '') or '').strip()
    formula = str(fam.frontmatter.get('formula', '') or '').strip()
    col_in_panel = panel is not None and col in getattr(panel, 'columns', [])
    if tier == 'pending' and not col_in_panel:
        # P2-① (2026-07-11): 按 col∈panel 实测分支 — 未实存才渲染"待接入"哨兵口径
        value_range = '待接入'
        unit = unit or '待接入'
    elif is_structural:
        value_range = ''      # 结构列取值范围由既有 _apply_dynamic_value_ranges 动态实测
    else:
        value_range = _value_range_from_panel(col, panel)
    if tier == 'pending' and col_in_panel:
        # 实存 pending 列: 主体章按实测渲染 (上方分支), 另发告警提示重跑 WP0 升 tier
        counters['warnings'].append(
            f'{fam.family_id}/{col}: tier=pending 但面板已实存 — 已按实测渲染统计/取值范围, '
            f'请重跑 build_codebook_family_map 升 tier (P2-① 实存检查)'
        )
    rendered_lines = cite_txt.split('\n') if cite_txt else []
    reference_short = ' | '.join(rendered_lines[:5])

    # ── 备注回填通道 (P2-② 2026-07-11): VAR 节内联【备注】 > frontmatter notes_zh
    #    (mapping 按列取 / str 家族级广播); 命中即由挂载层替换 _AUTO_INFER_NOTE ──
    fm_notes = fam.frontmatter.get('notes_zh')
    notes_zh = fam.var_notes.get(col, '')
    if not notes_zh:
        if isinstance(fm_notes, dict):
            notes_zh = str(fm_notes.get(col, '') or '').strip()
        elif fm_notes is not None:
            notes_zh = str(fm_notes or '').strip()

    counters['composed'] += 1
    return {
        'description': description,
        'unit': unit,
        'formula': formula,
        'value_range': value_range,
        'reference_short': reference_short,
        'notes_zh': notes_zh,
        'tier': tier,
        'family_id': fam.family_id,
        'cjk_total': cjk_total,
        'gate_violations': violations,
    }


def _value_range_from_panel(col: str, panel) -> str:
    """取值范围机械回填 (§4: 动态统计段同源): 数值列 [min, max] / 枚举列 nunique。"""
    import pandas as pd
    if panel is None or col not in panel.columns:
        return ''
    s = panel[col]
    v = s.dropna()
    if len(v) == 0:
        return '全缺失 (生成时实测)'
    if pd.api.types.is_numeric_dtype(s):
        return f'[{v.min():.4f}, {v.max():.4f}] (生成时实测)'
    return f'{v.nunique()} 个唯一值 (生成时实测)'


def compose_pending_appendix(
    library: LongdescLibrary,
    panel,
    *,
    counters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """待接入变量附录章 (§1a 类别 2): pending 哨兵列不在 panel 中, 其长文经同一
    组装器渲染 (动态统计段走四态④哨兵), 落 codebook markdown 附录。
    """
    out = []
    for col in library.pending_cols():
        if panel is not None and col in getattr(panel, 'columns', []):
            # 已实存 → 主体章按实测渲染覆盖 (P2-① col∈panel 实测分支), 附录不重复;
            # tier 升 core 须重跑 build_codebook_family_map (组装层已发告警提示)
            continue
        entry = compose_long_description(col, panel, library, counters=counters)
        if entry is not None:
            entry['col'] = col
            out.append(entry)
    return out


# ============================================================================
# xlsx 32,767 守卫 (§4: 守卫写在组装层, engine 无关)
# ============================================================================

_XLSX_SOFT_LIMIT = 30000
_XLSX_TRUNC_NOTE = '…【已截断: xlsx 单元格 32,767 字符硬限, 全文见 codebook.md / codebook.json】'


def xlsx_cell_guard(value: Any) -> Tuple[Any, bool]:
    """xlsx 单元格守卫: >30000 字符截断 + 尾注。返回 (安全值, 是否截断)。"""
    if isinstance(value, str) and len(value) > _XLSX_SOFT_LIMIT:
        return value[:_XLSX_SOFT_LIMIT - len(_XLSX_TRUNC_NOTE)] + _XLSX_TRUNC_NOTE, True
    return value, False


def xlsx_safe_dataframe(df):
    """DataFrame 级 xlsx 守卫 (只在 excel 写出前对副本应用); 返回 (副本, 截断计数)。"""
    out = df.copy()
    n_trunc = 0
    for c in out.columns:
        if out[c].dtype == object:
            def _guard(v):
                nonlocal n_trunc
                safe, t = xlsx_cell_guard(v)
                n_trunc += int(t)
                return safe
            out[c] = out[c].map(_guard)
    return out, n_trunc


# ============================================================================
# 三单位分布报告 (§9.2: 汉字/字符/UTF-8 字节 — 诊断引文超重/32767 逼近/note 分段)
# ============================================================================

def size_triplet(text: str) -> Dict[str, int]:
    """逐列三单位: CJK 汉字数 (闸) / 字符数 / UTF-8 字节数。"""
    t = text or ''
    return {'cjk': count_cjk(t), 'chars': len(t), 'utf8_bytes': len(t.encode('utf-8'))}


def build_size_report(desc_by_col: Dict[str, str], tier_by_col: Dict[str, str]) -> Dict[str, Any]:
    """汉字数分布报告 (§9.2): 中位数 / P10 / 距地板距离 (地板 +10% 内聚集 → 抽查复审)。"""
    per_col = {c: dict(size_triplet(t), tier=tier_by_col.get(c, 'standard'))
               for c, t in desc_by_col.items()}
    cjks = sorted(v['cjk'] for v in per_col.values())
    summary: Dict[str, Any] = {'n_cols': len(cjks)}
    if cjks:
        import math
        summary['cjk_median'] = cjks[len(cjks) // 2]
        summary['cjk_p10'] = cjks[max(0, math.ceil(len(cjks) * 0.10) - 1)]
        summary['cjk_min'] = cjks[0]
        summary['cjk_max'] = cjks[-1]
        n_floor10 = sum(
            1 for c, v in per_col.items()
            if v['cjk'] <= TOTAL_CJK_FLOOR.get(v['tier'], 1000) * 1.10
        )
        summary['n_within_10pct_of_floor'] = n_floor10
        summary['floor_note'] = '地板 +10% 内聚集触发抽查复审 (§6 写手铁律: 下限是地板非目标)'
    return {'summary': summary, 'per_col': per_col}
