"""tests/test_news_salience.py — 新闻体裁显著性 (版位/导语/署名, 批 #8–#10) 单测."""
from __future__ import annotations

import math

from news_process.pipeline.filtering.news_salience import (
    NEWS_SALIENCE_KEYS,
    compute_news_salience,
    parse_byline,
    parse_front_page,
    target_in_lead,
)


def test_front_page_keyword_and_first_page():
    assert parse_front_page('头版', 'A01')['is_front_page'] == 1.0
    assert parse_front_page('要闻', '')['is_front_page'] == 1.0  # 关键词命中, 页号缺失
    r = parse_front_page('财经', 'A05')
    assert r['is_front_page'] == 0.0 and r['page_rank'] == 5.0
    # B 叠 → 叠序偏移 100
    assert parse_front_page('金融', 'B02')['page_rank'] == 102.0
    # 页号无法解析 → page_rank nan
    assert math.isnan(parse_front_page('财经', '')['page_rank'])


def test_byline_named_vs_wire():
    staff = parse_byline('本报记者 张三', '本行今日宣布……')
    assert staff['has_byline'] == 1.0 and staff['is_wire'] == 0.0
    agency = parse_byline('新华社', '……')
    assert agency['has_byline'] == 0.0 and agency['is_wire'] == 1.0
    # 作者空但正文电头是通讯社 → is_wire=1, has_byline=0
    lead_wire = parse_byline('', '新华社北京1月1日电 本行宣布……')
    assert lead_wire['is_wire'] == 1.0 and lead_wire['has_byline'] == 0.0
    # 占位符作者不算署名
    assert parse_byline('佚名', '内容')['has_byline'] == 0.0


def test_target_in_lead():
    # 标题命中
    assert target_in_lead('工商银行发布年报', '正文内容。', '工商银行') == 1.0
    # 前 2 句命中
    assert target_in_lead('某标题', '工商银行今日宣布。第二句话。第三句。', '工商银行') == 1.0
    # 仅出现在第 3 句之后 → 不在导语
    assert target_in_lead('某标题', '第一句无关。第二句无关。后面才提到工商银行。',
                          '工商银行', k_sentences=2) == 0.0
    # 空行名 → nan
    assert math.isnan(target_in_lead('t', 'c', ''))


def test_compute_news_salience_all_keys():
    r = compute_news_salience('头版', 'A01', '本报记者 李四',
                              '工商银行年报', '工商银行今日宣布利润增长。', '工商银行')
    assert set(r.keys()) == set(NEWS_SALIENCE_KEYS)
    assert r['is_front_page'] == 1.0
    assert r['has_byline'] == 1.0
    assert r['target_in_lead'] == 1.0


def test_news_bank_imports_salience():
    # 回归: news_bank 现 import news_salience, 确认无循环导入/语法错误
    import news_process.pipeline.filtering.news_bank as nb
    assert hasattr(nb, 'compute_news_salience')
