"""news_process.pipeline.filtering.news_salience — 新闻体裁显著性 $0 测度族.

2026-06-05 新增 (顶刊文本测度缺口报告批 #8–#10)。原始数据现成 (版面/页号/作者) 却
此前仅用于广告过滤、从未派生为特征。全部 $0 (纯字符串/正则解析, 无 LLM、无新依赖),
在 news_bank stage 11 物化为 article 级列, 经 encode 聚合到 bank-year。

测度与锚点:
  #8 版位显著性  is_front_page / is_front_section / page_rank
       — Tetlock (2007) JF 62(3); Boudoukh et al. (2019) RFS. 报纸版位=读者注意力物理
         代理 (头版=高显著, 后叠=被埋没)。
  #9 导语显著性  target_in_lead
       — Tetlock (2008); Boudoukh et al. (2019) RFS relevance/centrality. 倒金字塔写法
         下"目标行是否在导语点名"= 本行是否报道主角 (vs 文末顺带提及的路人)。
  #10 署名原创性 has_byline / is_wire
       — 来源权威/原创性. 署名记者深度稿 vs 无名通稿转载; 与 media_authority (媒体级)、
         herd_decay (产出端重复) 正交 (作者级、投入端)。

诚实限定 (写入论文须披露):
  - 版位: 不同报纸 A/B 叠语义不同, 本版用 (叠字母序*100 + 页码) 作 page_rank 的粗规范化;
    全量多报源下宜先做各报源叠语义映射 (本版为单一近似)。
  - 导语: target_in_lead 仅匹配【规范行名 bank_name】(非全部别名), 是保守下界代理。
  - 署名: 作者字段须在 noise_patterns 剥离【之前】抽取 (本 stage 11 早于预处理剥离, 安全);
    通讯社判定基于关键词表, 非穷举。
"""
from __future__ import annotations

import re

from news_process.core.text.cn_text_utils import cn_split_sentence

# ── 版位 ─────────────────────────────────────────────────────────────────────
# 头版/要闻类版面关键词 (高显著)
_FRONT_SECTION_KW = ('头版', '封面', '要闻', '头条', '焦点')
# 页号解析: 可选叠字母 (A/B/C..) + 前导 0 + 页码数字, 如 'A05' / 'B2' / '03'
_PAGE_RE = re.compile(r'([A-Za-z]?)\s*0*(\d+)')

# ── 署名 ─────────────────────────────────────────────────────────────────────
# 通讯社/通稿来源 (无原创署名信号)
_WIRE_AGENCIES = (
    '新华社', '中新社', '中国新闻网', '中新网', '人民网', '央视', '央广',
    '综合报道', '综合', '本报讯', '电讯', '通讯社', '路透', '彭博',
)


def parse_front_page(banmian: str, yehao: str) -> dict[str, float]:
    """从 版面/页号 解析版位显著性 (#8)。

    Returns:
        is_front_page(0/1): 头版/要闻 或 A 叠首页;
        is_front_section(0/1): 版面命中头版关键词;
        page_rank(float): 叠字母序*100 + 页码, 越小越显著; 解析失败 → nan。
    """
    banmian = (banmian or '').strip()
    yehao = (yehao or '').strip()
    is_front_section = 1 if any(kw in banmian for kw in _FRONT_SECTION_KW) else 0

    section_letter = ''
    page_num = None
    m = _PAGE_RE.search(yehao)
    if m:
        section_letter = m.group(1).upper()
        try:
            page_num = int(m.group(2))
        except ValueError:
            page_num = None

    if page_num is not None:
        sec_idx = (ord(section_letter) - ord('A')) if section_letter.isalpha() else 0
        page_rank = float(sec_idx * 100 + page_num)
    else:
        page_rank = float('nan')

    # 头版: 版面关键词命中, 或 (A 叠/无叠) 第 1 页
    on_first_page = (
        page_num is not None and page_num <= 1
        and (not section_letter or section_letter == 'A')
    )
    is_front_page = 1 if (is_front_section or on_first_page) else 0
    return {
        'is_front_page': float(is_front_page),
        'is_front_section': float(is_front_section),
        'page_rank': page_rank,
    }


def parse_byline(author: str, content: str) -> dict[str, float]:
    """从 作者 + 正文电头解析署名原创性 (#10)。

    Returns:
        has_byline(0/1): 有具名作者 (非空且非通讯社占位);
        is_wire(0/1): 作者或正文开头命中通讯社/通稿来源。
    """
    author = (author or '').strip()
    head = (content or '')[:60]  # 正文开头电头 ("新华社北京X日电")
    is_wire = 1 if (
        any(a in author for a in _WIRE_AGENCIES)
        or any(a in head for a in _WIRE_AGENCIES)
    ) else 0
    # 署名: 作者字段非空、非纯通讯社、非占位符
    has_byline = 1 if (
        author and author not in ('-', '无', '佚名')
        and not any(a in author for a in _WIRE_AGENCIES)
    ) else 0
    return {'has_byline': float(has_byline), 'is_wire': float(is_wire)}


def target_in_lead(title: str, content: str, bank_name: str,
                   k_sentences: int = 2) -> float:
    """目标行是否在导语 (标题 + 正文前 K 句) 出现 (#9)。

    保守代理: 仅匹配规范行名 bank_name (非全部别名)。标题命中即视为 lead 显著。
    """
    if not bank_name:
        return float('nan')
    title = title or ''
    content = content or ''
    if bank_name in title:
        return 1.0
    lead = ''.join(cn_split_sentence(content)[:k_sentences])
    return 1.0 if bank_name in lead else 0.0


# article 级显著性列名 (供 news_bank 物化 + encode 聚合引用)
NEWS_SALIENCE_KEYS = (
    'is_front_page', 'is_front_section', 'page_rank',
    'has_byline', 'is_wire', 'target_in_lead',
)


def compute_news_salience(banmian: str, yehao: str, author: str,
                          title: str, content: str, bank_name: str) -> dict[str, float]:
    """一次性产出 6 个新闻体裁显著性 article 级测度 (#8–#10)。"""
    out: dict[str, float] = {}
    out.update(parse_front_page(banmian, yehao))
    out.update(parse_byline(author, content))
    out['target_in_lead'] = target_in_lead(title, content, bank_name)
    return out
