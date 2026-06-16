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
    全量多报源下宜先做各报源叠语义映射 (本版为单一近似)。多字母叠号 (如 'AII06')
    按首个 [字母]?数字 序列解析, 可能误析为后续单字母叠 (page_rank 偏大), 同属
    单一近似披露范围。
  - 导语: target_in_lead 匹配该行【全部名称变体】(经 stage 11 同款否定/短名排除);
    fix(omni-g-entity-12, 2026-06-11) 前仅匹配规范行名 — 实测偏差由各行命名惯例
    决定 (国有大行规范名媒体不用 → 低估至 5 倍), 并非均匀保守下界, 故改全变体集。
  - 署名: has_byline 取自独立的 作者 字段, 不受 stage 00 noise_patterns 内容剥离影响
    (内容剥离只动 内容 列); is_wire 另外扫描正文前 60 字电头, 通讯社判定基于关键词表, 非穷举。
  - 缺失语义: 版面+页号均缺失 → 版位三列 NaN; 作者缺失且无电头通讯社证据 →
    has_byline/is_wire NaN (fix omni-g-entity-13, 2026-06-11) — "字段不适用"
    (网络源无版面概念) 不再与 "未上头版/无署名" 混同, mean 聚合自动跳过 NaN。
"""
from __future__ import annotations

import re

from news_process.core.text.ahocorasick import has_unexcluded_occurrence
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
        版面+页号均缺失 → 三列全 NaN (字段不适用 ≠ 不显著)。

    Note:
        fix(omni-g-entity-13, 2026-06-11): 源字段全缺失时返回 NaN 而非硬编码 0 —
        线上媒体源无版面概念, "不适用" 混入 0 会让 frac_front_page 等 bank-year
        均值被媒体构成混杂; NaN 在 encode 'mean' 聚合下自动跳过。
    """
    banmian = (banmian or '').strip()
    yehao = (yehao or '').strip()
    if not banmian and not yehao:
        _nan = float('nan')
        return {'is_front_page': _nan, 'is_front_section': _nan, 'page_rank': _nan}
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
        作者缺失且电头无通讯社证据 → 两列 NaN (字段缺失 ≠ 无署名)。

    Note:
        fix(omni-g-entity-13, 2026-06-11): 作者字段缺失 (空) 时不再硬编码
        has_byline=0 — 多源全量语料下网络源作者字段缺失非 "无署名" 信号;
        电头命中通讯社时保留 is_wire=1/has_byline=0 (通稿无署名是真信号);
        显式占位符 ('-'/'无'/'佚名') 是字段在场的真 "无署名" 信号, 仍计 0。
    """
    author = (author or '').strip()
    head = (content or '')[:60]  # 正文开头电头 ("新华社北京X日电")
    head_wire = any(a in head for a in _WIRE_AGENCIES)
    if not author:
        if head_wire:
            # 电头证据在场: 通讯社通稿, 无署名为真信号
            return {'has_byline': 0.0, 'is_wire': 1.0}
        # 字段缺失且无任何来源证据 → 不可判 (NaN, mean 聚合自动跳过)
        _nan = float('nan')
        return {'has_byline': _nan, 'is_wire': _nan}
    is_wire = 1 if (any(a in author for a in _WIRE_AGENCIES) or head_wire) else 0
    # 署名: 作者字段非占位符、非纯通讯社
    has_byline = 1 if (
        author not in ('-', '无', '佚名')
        and not any(a in author for a in _WIRE_AGENCIES)
    ) else 0
    return {'has_byline': float(has_byline), 'is_wire': float(is_wire)}


def target_in_lead(title: str, content: str, bank_name: str,
                   k_sentences: int = 2, aliases: list[str] | None = None,
                   negation_ac=None, short_name_exclusions: dict | None = None,
                   context_window: int = 5) -> float:
    """目标行是否在导语 (标题 + 正文前 K 句) 出现 (#9)。

    标题命中即视为 lead 显著。

    fix(omni-g-entity-12, 2026-06-11): 由仅匹配规范行名改为匹配【全部名称变体】
    (aliases, 自动并入规范名), 并按 occurrence 级套用 stage 11 的否定/短名排除
    (has_unexcluded_occurrence, 防 '光大'/'施工行' 类误命中)。原实现的偏差由
    各行命名惯例决定 (农行 0.161 vs 0.828 全变体), 非均匀保守下界。
    aliases=None 时退化为旧行为 (仅规范名, 向后兼容)。
    """
    if not bank_name:
        return float('nan')
    title = title or ''
    content = content or ''
    names = [n for n in (aliases or []) if n]
    if bank_name not in names:
        names.insert(0, bank_name)
    for nm in names:
        if has_unexcluded_occurrence(title, nm, negation_ac,
                                     short_name_exclusions, context_window):
            return 1.0
    lead = ''.join(cn_split_sentence(content)[:k_sentences])
    for nm in names:
        if has_unexcluded_occurrence(lead, nm, negation_ac,
                                     short_name_exclusions, context_window):
            return 1.0
    return 0.0


# article 级显著性列名 (供 news_bank 物化 + encode 聚合引用)
NEWS_SALIENCE_KEYS = (
    'is_front_page', 'is_front_section', 'page_rank',
    'has_byline', 'is_wire', 'target_in_lead',
)


def compute_news_salience(banmian: str, yehao: str, author: str,
                          title: str, content: str, bank_name: str,
                          aliases: list[str] | None = None,
                          negation_ac=None,
                          short_name_exclusions: dict | None = None,
                          context_window: int = 5) -> dict[str, float]:
    """一次性产出 6 个新闻体裁显著性 article 级测度 (#8–#10)。

    fix(omni-g-entity-12, 2026-06-11): 新增 aliases + 排除配置直通参数
    (target_in_lead 全变体匹配); 缺省时与旧调用契约兼容。
    """
    out: dict[str, float] = {}
    out.update(parse_front_page(banmian, yehao))
    out.update(parse_byline(author, content))
    out['target_in_lead'] = target_in_lead(
        title, content, bank_name, aliases=aliases,
        negation_ac=negation_ac, short_name_exclusions=short_name_exclusions,
        context_window=context_window,
    )
    return out
