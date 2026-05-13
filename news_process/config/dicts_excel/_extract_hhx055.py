"""
最终版：精确提取 hhx055_supp.pdf 中四个面板词汇，生成 Excel 并验证数量
"""
import sys

sys.stdout.reconfigure(encoding='utf-8')
import re
from pathlib import Path

import pandas as pd
import pdfplumber
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

PDF_PATH = Path(__file__).parent / "hhx055_supp.pdf"
OUT_PATH = Path(__file__).parent / "hhx055_supp_words.xlsx"

EXPECTED = {
    "Panel A": ("积极词汇", 1425),
    "Panel B": ("消极词汇", 1583),
    "Panel C": ("明确词汇",  388),
    "Panel D": ("模糊词汇",  178),
}
PANEL_COLORS = {
    "Panel A": "C6EFCE",
    "Panel B": "FFC7CE",
    "Panel C": "DDEBF7",
    "Panel D": "FFEB9C",
}

# ────────────────────────────────────────────────────────────────────────────
# 1. 基于坐标提取：按 (page, row_y, x0) 排序后拼行
# ────────────────────────────────────────────────────────────────────────────
def extract_lines_by_coord(pdf_path: Path, y_tol: float = 2.0):
    """按坐标排序，把同一y的词拼成一行文本。"""
    all_w = []
    with pdfplumber.open(pdf_path) as pdf:
        for pno, page in enumerate(pdf.pages):
            ws = page.extract_words(keep_blank_chars=False)
            for w in ws:
                all_w.append((pno, round(w['top'] / y_tol), w['x0'], w['text']))
    all_w.sort()   # (page, row_key, x0, text) —— 多列从左到右

    lines = []
    cur_key, cur_toks = None, []
    for pno, rk, x0, text in all_w:
        key = (pno, rk)
        if key != cur_key:
            if cur_toks:
                lines.append(' '.join(cur_toks))
            cur_toks = [text]
            cur_key  = key
        else:
            cur_toks.append(text)
    if cur_toks:
        lines.append(' '.join(cur_toks))
    return lines


# ────────────────────────────────────────────────────────────────────────────
# 2. 识别面板标题行（"Panel X: ..." 或 "Panel X Positive/Negative/..." 形式）
#    要求在同一行中 Panel 和字母之后紧跟 ":" 或 英文描述词
# ────────────────────────────────────────────────────────────────────────────
# 面板标题行特征：行中含 "Panel X:" 或以 "Panel X " 开头且后面有英文
TITLE_PAT = re.compile(
    r'\bPanel\s+([A-D])\s*[:\-]?\s*(Positive|Negative|Definite|Ambiguous)',
    re.I
)
# 也兼容格式 "Panel A: Positive Words" 可能被split成两行，但一般在同一行

def find_panel_starts(lines):
    """返回 {letter: line_index}，只取第一次出现的标题行"""
    starts = {}
    for i, line in enumerate(lines):
        m = TITLE_PAT.search(line)
        if m:
            letter = m.group(1).upper()
            if letter not in starts:
                starts[letter] = i
    return starts


# ────────────────────────────────────────────────────────────────────────────
# 3. 从面板块中提取中文词汇（去重保序）
# ────────────────────────────────────────────────────────────────────────────
STRIP_CHARS = ',.;:()（）【】[]、。！？""''·—…'
HAN      = re.compile(r'[\u4e00-\u9fff]')
SKIP_PAT = re.compile(r'Internet\s+Appendix|Page\s+\d+', re.I)
# 词典行中与汉字词并列的全大写英文词（如 TOP），也视为词典词汇
DICT_EN  = re.compile(r'^[A-Z]{2,}$')   # 全大写，≥2字母

def extract_han_words(lines_block):
    words = []
    for line in lines_block:
        if SKIP_PAT.search(line):
            continue
        # 判断本行是否是词典数据行（含汉字）
        is_dict_line = bool(HAN.search(line))
        for tok in re.split(r'\s+', line):
            tok = tok.strip(STRIP_CHARS)
            if not tok:
                continue
            if HAN.search(tok):
                words.append(tok)
            elif is_dict_line and DICT_EN.match(tok):
                # 词典行中的全大写英文词（如 TOP）也纳入
                words.append(tok)
    seen, uniq = set(), []
    for w in words:
        if w not in seen:
            seen.add(w); uniq.append(w)
    return uniq


# ────────────────────────────────────────────────────────────────────────────
# 4. 主解析函数
# ────────────────────────────────────────────────────────────────────────────
def parse_all(pdf_path: Path):
    lines = extract_lines_by_coord(pdf_path)

    starts = find_panel_starts(lines)
    print(f'找到面板标题行：{ {f"Panel {k}": v for k,v in starts.items()} }')

    # 如果没找到四个面板，尝试更宽松的正则
    if len(starts) < 4:
        loose = re.compile(r'\bPanel\s+([A-D])\b', re.I)
        for i, line in enumerate(lines):
            m = loose.search(line)
            if m and m.group(1).upper() not in starts:
                # 排除描述性句子（含 "lists N positive/negative"）
                if not re.search(r'lists\s+[\d,]+', line, re.I):
                    starts[m.group(1).upper()] = i
        print(f'宽松匹配后：{ {f"Panel {k}": v for k,v in starts.items()} }')

    letters = sorted(starts.keys())
    panels  = {}
    for idx, letter in enumerate(letters):
        s = starts[letter]
        e = starts[letters[idx+1]] if idx+1 < len(letters) else len(lines)
        words = extract_han_words(lines[s:e])
        panels[f'Panel {letter}'] = words

    return panels, lines


# ────────────────────────────────────────────────────────────────────────────
# 5. Excel 写入 + 格式美化
# ────────────────────────────────────────────────────────────────────────────
def write_excel(panels, out_path: Path):
    thin   = Side(style="thin", color="BFBFBF")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    h_font = Font(bold=True, size=11, color="FFFFFF")
    h_fill = PatternFill("solid", fgColor="4472C4")
    c_align= Alignment(horizontal="center", vertical="center", wrap_text=True)
    l_align= Alignment(horizontal="left",   vertical="center")

    summary_rows = []
    for pk, (label, exp) in EXPECTED.items():
        words  = panels.get(pk, [])
        actual = len(words)
        summary_rows.append({
            "面板": pk, "类别": label,
            "预期数量": exp, "实际数量": actual,
            "差异": actual - exp,
            "状态": "匹配" if actual == exp else "不匹配",
        })

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        pd.DataFrame(summary_rows).to_excel(
            writer, sheet_name="数量验证", index=False)
        for pk, (label, _) in EXPECTED.items():
            words = panels.get(pk, [])
            df = pd.DataFrame({"词汇": words})
            df.index = df.index + 1
            df.index.name = "序号"
            df.to_excel(writer, sheet_name=f"{pk} {label}")

    # 美化
    wb = load_workbook(out_path)

    # 验证汇总
    ws = wb["数量验证"]
    for col, w in zip("ABCDEF", [12,12,12,12,10,14]):
        ws.column_dimensions[col].width = w
    for cell in ws[1]:
        cell.font=h_font; cell.fill=h_fill
        cell.alignment=c_align; cell.border=border
    for row in ws.iter_rows(min_row=2):
        pk    = row[0].value
        color = PANEL_COLORS.get(pk, "F2F2F2")
        fill  = PatternFill("solid", fgColor=color)
        for cell in row:
            cell.fill=fill; cell.border=border; cell.alignment=c_align
        sc = row[5]
        if sc.value == "匹配":
            sc.font = Font(bold=True, color="375623")
        else:
            sc.font = Font(bold=True, color="9C0006")
    ws.freeze_panes = "A2"

    # 各面板
    for pk, (label, _) in EXPECTED.items():
        sn = f"{pk} {label}"
        if sn not in wb.sheetnames:
            continue
        ws2 = wb[sn]
        ws2.column_dimensions["A"].width = 8
        ws2.column_dimensions["B"].width = 22
        color = PANEL_COLORS[pk]
        fill  = PatternFill("solid", fgColor=color)
        for cell in ws2[1]:
            cell.font=h_font; cell.fill=h_fill
            cell.alignment=c_align; cell.border=border
        for row in ws2.iter_rows(min_row=2):
            for cell in row:
                cell.fill=fill; cell.border=border
                cell.alignment = c_align if cell.column==1 else l_align
        ws2.freeze_panes = "A2"

    wb.save(out_path)


# ────────────────────────────────────────────────────────────────────────────
# 6. 主流程
# ────────────────────────────────────────────────────────────────────────────
def main():
    print(f'读取 PDF: {PDF_PATH}')
    panels, lines = parse_all(PDF_PATH)
    print(f'总行数: {len(lines)}')

    print('\n' + '='*54)
    print('  数量验证')
    print('='*54)
    all_ok = True
    for pk, (label, exp) in EXPECTED.items():
        actual = len(panels.get(pk, []))
        ok     = (actual == exp)
        if not ok: all_ok = False
        status = 'OK' if ok else f'DIFF {actual-exp:+d}'
        print(f'  {pk} {label}: {actual:5d}/{exp}  [{status}]')
    print('='*54)
    print('  全部验证通过!' if all_ok else '  存在差异，请检查!')

    # 若 Panel A 仍差-1，打印前5行和末5行辅助调试
    pa = panels.get('Panel A', [])
    if len(pa) != 1425:
        print(f'\n[调试] Panel A 前5词: {pa[:5]}')
        print(f'[调试] Panel A 末5词: {pa[-5:]}')

    write_excel(panels, OUT_PATH)
    print(f'\nExcel 已保存: {OUT_PATH}')


if __name__ == '__main__':
    main()
