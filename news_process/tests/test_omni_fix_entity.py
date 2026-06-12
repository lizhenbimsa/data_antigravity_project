"""tests/test_omni_fix_entity.py — omni 2026-06-11 g-entity 组修复回归锁.

锁定实体匹配层修复后的行为 (全部合成数据, 不依赖盘上大数据 / 不调外部 API):
  - g-entity-01/08/14: analyze_bank_matches 同行嵌套变体最长匹配去重
    (一次物理提及 '中国工商银行' 不再被计 2 次, 分类门槛不再被击穿)
  - g-entity-02/09/15: 跨行嵌套变体归属最长串对应银行
    ('法国兴业银行' 文章不再为 '兴业银行' 生成幻影 firm-document 行)
  - g-entity-04/07/11: 全文单次扫描 + 起点归半 (跨切分点匹配不再丢失,
    bank 与 fintech 两个分析函数同步)
  - g-entity-10: negation_patterns 补 '中国银行间'/'中国银行保险监督管理委员会'/
    '中国银行保险报' (真实 config 文件)
  - g-entity-03/16: entity_context ctx 锚定套用 stage 11 同款否定/短名排除
  - g-entity-05: canonicalize_topic 置信度分母与注释对齐 (去 max(total,1.0))
  - g-entity-12: news_salience.target_in_lead 全变体匹配 + 排除规则
  - g-entity-13: salience 缺失源字段 (版面/页号/作者) NaN 路径
    + news_bank _cell 守卫 (NaN 不再 str() 成字面 'nan')

# 白话: 这组测试管"认银行名认得准不准": "中国工商银行"出现一次不能因为里面
# 套着"工商银行"被数两次; "法国兴业银行"的新闻不能错算到"兴业银行"头上;
# "中国银行间市场""银保监会"这类机构名里的"中国银行"不算提及; 名字正好跨在
# 文章前后半切分点上也不能漏数; 版面/作者字段缺失时记"不知道"(NaN), 不能把
# 缺失当成字面文字 "nan" 处理。
"""
from __future__ import annotations

import json
import math
import os

import numpy as np
import pandas as pd
import pytest

from news_process.core.text.ahocorasick import (
    analyze_bank_matches,
    analyze_fintech_matches,
    has_unexcluded_occurrence,
    load_bank_names,
    load_exclusion_patterns,
    load_fintech_dict,
)
from news_process.core.text.canonicalization import canonicalize_topic
from news_process.core.text.entity_context import (
    extract_entity_context,
    extract_entity_context_with_distances,
)
from news_process.pipeline.filtering.news_salience import (
    compute_news_salience,
    parse_byline,
    parse_front_page,
    target_in_lead,
)


def _real_config_path(name: str) -> str:
    import news_process
    return os.path.join(os.path.dirname(news_process.__file__), 'config', name)


# ============================================================================
# fixtures (合成词典, 与生产 config 解耦)
# ============================================================================

@pytest.fixture
def bank_setup(tmp_path):
    data = [
        {'bank_name': '中国工商银行',
         'variants': ['中国工商银行', '工商银行', '工行']},
        {'bank_name': '兴业银行', 'variants': ['兴业银行']},
        {'bank_name': '法国兴业银行(中国)',
         'variants': ['法国兴业银行(中国)', '法国兴业银行', '法兴银行']},
        {'bank_name': '中国银行', 'variants': ['中国银行', '中行']},
        {'bank_name': '中国农业银行',
         'variants': ['中国农业银行', '农业银行', '农行']},
    ]
    p = tmp_path / 'bank_names.json'
    p.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    banks, ac, _ = load_bank_names(str(p))
    return banks, ac


@pytest.fixture
def exclusion_setup(tmp_path):
    data = {
        'negation_patterns': ['中国银行业', '中国银行间',
                              '中国银行保险监督管理委员会', '涉农行业'],
        'short_name_context_exclusions': {
            'context_window': 6,
            'exclusions': {'农行': ['涉农行'], '工行': ['施工行']},
        },
    }
    p = tmp_path / 'bank_name_exclusions.json'
    p.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    return load_exclusion_patterns(str(p))


# ============================================================================
# g-entity-01/08/14: 同行嵌套变体去重
# ============================================================================

class TestNestedVariantDedup:
    def test_nested_same_bank_counts_once(self, bank_setup):
        banks, ac = bank_setup
        content = ('中国工商银行公布财报引发关注热议。'
                   '市场人士表示中国工商银行经营稳健。')
        r = analyze_bank_matches(content, '', ac, banks, split_ratio=0.5,
                                 min_name_occurrences=3,
                                 min_upper=1, min_lower=1)
        icbc = [b for b in r['matched_banks'] if b['bank_name'] == '中国工商银行']
        assert len(icbc) == 1
        # 2 次物理提及 → 2 (旧实现嵌套双计 = 4)
        assert icbc[0]['total_count'] == 2
        counted = {v['variant'] for v in icbc[0]['variant_details'] if v['total'] > 0}
        assert counted == {'中国工商银行'}  # 嵌套 '工商银行' 不再计数
        # 阈值 3 不再被 2 次物理提及击穿 (旧实现 is_bank_news=True)
        assert r['is_bank_news'] is False

    def test_title_nested_dedup(self, bank_setup):
        banks, ac = bank_setup
        r = analyze_bank_matches('', '中国工商银行发布公告', ac, banks,
                                 split_ratio=0.5, min_name_occurrences=3)
        icbc = next(b for b in r['matched_banks']
                    if b['bank_name'] == '中国工商银行')
        # 标题 1 次物理提及只给最长变体记 in_title (total_with_title=1, 非 2)
        assert icbc['total_with_title'] == 1
        in_title_variants = {v['variant'] for v in icbc['variant_details']
                             if v['in_title']}
        assert in_title_variants == {'中国工商银行'}


# ============================================================================
# g-entity-02/09/15: 跨行嵌套变体归属最长串
# ============================================================================

class TestCrossBankAttribution:
    def test_socgen_not_misattributed_to_cib(self, bank_setup, exclusion_setup):
        banks, ac = bank_setup
        neg_ac, short_excl, cw = exclusion_setup
        content = ('法国兴业银行宣布退出俄罗斯市场并完成交割手续。'
                   '据悉法国兴业银行此前已与多方接触。'
                   '分析人士认为法国兴业银行的决定影响有限。')
        title = '法国兴业银行宣布退出'
        r = analyze_bank_matches(content, title, ac, banks, split_ratio=0.5,
                                 negation_ac=neg_ac,
                                 short_name_exclusions=short_excl,
                                 context_window=cw,
                                 min_name_occurrences=3,
                                 min_upper=1, min_lower=1)
        names = {b['bank_name'] for b in r['matched_banks']}
        assert '法国兴业银行(中国)' in names
        # 旧实现: '兴业银行' 同时合格 (total=3, in_title=True) → 幻影行
        assert '兴业银行' not in names
        socgen = next(b for b in r['matched_banks']
                      if b['bank_name'] == '法国兴业银行(中国)')
        assert socgen['total_count'] == 3
        assert socgen['in_title'] is True
        assert r['is_bank_news'] is True

    def test_pure_cib_article_still_matches(self, bank_setup):
        banks, ac = bank_setup
        content = ('兴业银行公布三季度业绩快报。'
                   '业内认为兴业银行资产质量稳定。'
                   '兴业银行表示将持续优化结构。')
        r = analyze_bank_matches(content, '', ac, banks, split_ratio=0.5,
                                 min_name_occurrences=3,
                                 min_upper=1, min_lower=1)
        cib = next(b for b in r['matched_banks'] if b['bank_name'] == '兴业银行')
        assert cib['total_count'] == 3
        assert r['is_bank_news'] is True


# ============================================================================
# g-entity-04/07/11: 跨切分点匹配不再丢失 (全文单次扫描 + 起点归半)
# ============================================================================

class TestBoundaryCrossing:
    def test_crossing_bank_mention_not_lost(self, bank_setup):
        banks, ac = bank_setup
        content = '中国工商银行公布业绩。'  # len=11, split=5: 唯一提及横跨切分点
        r = analyze_bank_matches(content, '工商银行发布公告', ac, banks,
                                 split_ratio=0.5, min_name_occurrences=2,
                                 min_upper=1, min_lower=1)
        icbc = next(b for b in r['matched_banks']
                    if b['bank_name'] == '中国工商银行')
        assert icbc['total_count'] == 1   # 旧实现: 两半都不完整 → 0
        assert icbc['upper_count'] == 1   # 起点 0 < split_pos → 归上半
        assert r['is_bank_news'] is True  # in_title + 正文 1 次

    def test_crossing_with_position_attribution(self, bank_setup):
        banks, ac = bank_setup
        content = '12345678工商银行工商银行报道工商银行'  # len=22, split=11
        r = analyze_bank_matches(content, '', ac, banks, split_ratio=0.5,
                                 min_name_occurrences=3,
                                 min_upper=1, min_lower=1)
        icbc = next(b for b in r['matched_banks']
                    if b['bank_name'] == '中国工商银行')
        assert icbc['total_count'] == 3   # 旧实现: 跨界者丢失 → 2
        assert icbc['upper_count'] == 1 and icbc['lower_count'] == 2
        assert r['is_bank_news'] is True

    def test_fintech_crossing_not_lost(self, tmp_path):
        p = tmp_path / 'fintech_dict.json'
        p.write_text(json.dumps(['人工智能', '大数据'], ensure_ascii=False),
                     encoding='utf-8')
        _, ac = load_fintech_dict(str(p))
        content = '12人工智能34'  # len=8, split=4: 唯一出现横跨切分点
        r = analyze_fintech_matches(content, '', ac, split_ratio=0.5,
                                    min_distinct_keywords=1,
                                    min_upper=1, min_lower=0)
        assert r['total_count'] == 1      # 旧实现: 0 (双侧丢失)
        assert r['upper_count'] == 1      # 起点 2 < split_pos=4 → 上半
        assert r['is_fintech_news'] is True


# ============================================================================
# g-entity-10: negation_patterns 缺口 (真实 config 文件)
# ============================================================================

class TestNegationGaps:
    @pytest.fixture
    def real_exclusions(self):
        return load_exclusion_patterns(
            _real_config_path('bank_name_exclusions.json'))

    def test_config_contains_new_patterns(self):
        with open(_real_config_path('bank_name_exclusions.json'),
                  encoding='utf-8') as f:
            raw = json.load(f)
        neg = raw['negation_patterns']
        for p in ('中国银行间', '中国银行保险监督管理委员会', '中国银行保险报'):
            assert p in neg, f'negation_patterns 缺 {p}'

    def test_nafmii_article_not_boc(self, bank_setup, real_exclusions):
        banks, ac = bank_setup
        neg_ac, short_excl, cw = real_exclusions
        content = ('中国银行间市场交易商协会发布新规并公开征求意见。'
                   '中国银行间市场交易商协会表示将加强自律管理。'
                   '中国银行间债券市场整体运行平稳。')
        r = analyze_bank_matches(content, '', ac, banks, split_ratio=0.5,
                                 negation_ac=neg_ac,
                                 short_name_exclusions=short_excl,
                                 context_window=cw,
                                 min_name_occurrences=3,
                                 min_upper=1, min_lower=1)
        names = {b['bank_name'] for b in r['matched_banks']}
        assert '中国银行' not in names  # 旧实现: total=3 → 纯幻影 BOC 行
        assert r['is_bank_news'] is False

    def test_cbirc_article_not_boc(self, bank_setup, real_exclusions):
        banks, ac = bank_setup
        neg_ac, short_excl, cw = real_exclusions
        content = ('中国银行保险监督管理委员会召开年度工作会议。'
                   '中国银行保险监督管理委员会部署下阶段任务。'
                   '中国银行保险监督管理委员会强调防范金融风险。')
        r = analyze_bank_matches(content, '', ac, banks, split_ratio=0.5,
                                 negation_ac=neg_ac,
                                 short_name_exclusions=short_excl,
                                 context_window=cw,
                                 min_name_occurrences=3,
                                 min_upper=1, min_lower=1)
        assert '中国银行' not in {b['bank_name'] for b in r['matched_banks']}
        assert r['is_bank_news'] is False

    def test_genuine_boc_article_unaffected(self, bank_setup, real_exclusions):
        banks, ac = bank_setup
        neg_ac, short_excl, cw = real_exclusions
        content = ('中国银行公布年度报告利润稳增。'
                   '投资者关注中国银行海外布局。'
                   '中国银行回应称经营保持稳健。')
        r = analyze_bank_matches(content, '', ac, banks, split_ratio=0.5,
                                 negation_ac=neg_ac,
                                 short_name_exclusions=short_excl,
                                 context_window=cw,
                                 min_name_occurrences=3,
                                 min_upper=1, min_lower=1)
        boc = next(b for b in r['matched_banks'] if b['bank_name'] == '中国银行')
        assert boc['total_count'] == 3
        assert r['is_bank_news'] is True


# ============================================================================
# g-entity-03/16: ctx 锚定套用 stage 11 排除规则
# ============================================================================

class TestEntityContextExclusions:
    AGRI_ALIASES = ['中国农业银行', '农业银行', '农行']
    FALSE_ANCHOR_TEXT = ('与当地财政、农业、林业、海洋、涉农行业协会等部门开展对接。'
                         '相关工作正在按计划推进。'
                         '下一步将继续加强协作。'
                         '此事与银行业务无关。')

    def test_false_anchor_filtered(self, exclusion_setup):
        neg_ac, short_excl, cw = exclusion_setup
        # 旧行为 (无排除参数, 向后兼容): '涉农行业'⊂'农行' 锚定假窗口
        assert extract_entity_context(
            self.FALSE_ANCHOR_TEXT, self.AGRI_ALIASES) != ''
        # 新行为: occurrence 级排除后无有效锚 → 空串
        assert extract_entity_context(
            self.FALSE_ANCHOR_TEXT, self.AGRI_ALIASES,
            negation_ac=neg_ac, short_name_exclusions=short_excl,
            context_window=cw) == ''

    def test_with_distances_false_anchor_filtered(self, exclusion_setup):
        neg_ac, short_excl, cw = exclusion_setup
        assert extract_entity_context_with_distances(
            self.FALSE_ANCHOR_TEXT, self.AGRI_ALIASES) != []
        assert extract_entity_context_with_distances(
            self.FALSE_ANCHOR_TEXT, self.AGRI_ALIASES,
            negation_ac=neg_ac, short_name_exclusions=short_excl,
            context_window=cw) == []

    def test_char_fallback_false_anchor_filtered(self, exclusion_setup):
        neg_ac, short_excl, cw = exclusion_setup
        short_text = '与涉农行业协会开展对接'  # 无句读 → 字符级回退路径
        assert extract_entity_context(short_text, ['农行']) != ''
        assert extract_entity_context(
            short_text, ['农行'], negation_ac=neg_ac,
            short_name_exclusions=short_excl, context_window=cw) == ''

    def test_genuine_anchor_survives(self, exclusion_setup):
        neg_ac, short_excl, cw = exclusion_setup
        text = ('中国农业银行公布三季报。'
                '净利润同比增长。'
                '资产质量保持稳定。'
                '同业机构亦表现良好。')
        ctx = extract_entity_context(
            text, self.AGRI_ALIASES, negation_ac=neg_ac,
            short_name_exclusions=short_excl, context_window=cw)
        assert '中国农业银行公布三季报。' in ctx
        assert '同业机构亦表现良好' not in ctx  # radius=1 窗口外

    def test_ctx_materializer_wires_exclusions(self, monkeypatch, exclusion_setup):
        import news_process.pipeline.text.ctx_materializer as cm
        neg_ac, short_excl, cw = exclusion_setup
        monkeypatch.setattr(cm, 'NEGATION_AC', neg_ac)
        monkeypatch.setattr(cm, 'SHORT_NAME_EXCLUSIONS', short_excl)
        monkeypatch.setattr(cm, 'CONTEXT_WINDOW', cw)
        df = pd.DataFrame({
            '内容': [self.FALSE_ANCHOR_TEXT],
            '标题': ['某地工作动态'],
            'target_bank': ['中国农业银行'],
        })
        out = cm.materialize_content_ctx(df)
        # 全部 alias 出现均为假锚 → ctx 退回全文 body (回退公理)
        assert bool(out['ctx_is_fallback'].iloc[0]) is True


# ============================================================================
# has_unexcluded_occurrence (共享 occurrence 级排除助手)
# ============================================================================

class TestHasUnexcludedOccurrence:
    def test_naive_fallback_without_config(self):
        assert has_unexcluded_occurrence('涉农行业协会', '农行') is True
        assert has_unexcluded_occurrence('完全无关文本', '农行') is False
        assert has_unexcluded_occurrence('', '农行') is False
        assert has_unexcluded_occurrence('文本', '') is False

    def test_excluded_occurrence_filtered(self, exclusion_setup):
        neg_ac, short_excl, cw = exclusion_setup
        assert has_unexcluded_occurrence(
            '涉农行业协会', '农行', neg_ac, short_excl, cw) is False
        # 同句同时含假出现与真出现 → True (occurrence 级, 非句级一刀切)
        assert has_unexcluded_occurrence(
            '涉农行业协会与农行签约', '农行', neg_ac, short_excl, cw) is True


# ============================================================================
# g-entity-05: canonicalize_topic 置信度公式
# ============================================================================

class TestCanonicalizeConfidence:
    def test_low_weight_single_keyword_full_confidence(self):
        # '合规' 权重 0.5 → total=0.5 < 1.0; 旧实现 0.5/max(0.5,1.0)=0.5
        cat, conf = canonicalize_topic('合规')
        assert cat == '应用场景'
        assert conf == 1.0

    def test_fallback_design_unchanged(self):
        # 兜底基率归类是设计 (披露项): 空输入仍 ('应用场景', 0.0)
        assert canonicalize_topic('') == ('应用场景', 0.0)
        assert canonicalize_topic(None) == ('应用场景', 0.0)
        assert canonicalize_topic('null') == ('应用场景', 0.0)

    def test_mixed_keywords_ratio(self):
        # 人工智能(tech 2.0) + 智能风控(app 2.0) → app 平局败, tech 胜
        # conf = 2.0/4.0 = 0.5 (公式与旧实现一致, 锁定无回归)
        cat, conf = canonicalize_topic('人工智能智能风控')
        assert cat == '底层技术'
        assert conf == 0.5


# ============================================================================
# g-entity-12: target_in_lead 全变体匹配
# ============================================================================

class TestTargetInLeadVariants:
    AGRI_ALIASES = ['中国农业银行', '农业银行', '农行']

    def test_variant_in_title_detected(self):
        # 旧行为 (仅规范名): 媒体惯用简称漏检
        assert target_in_lead('农业银行发布年报', '正文。', '中国农业银行') == 0.0
        assert target_in_lead('农业银行发布年报', '正文。', '中国农业银行',
                              aliases=self.AGRI_ALIASES) == 1.0

    def test_variant_in_lead_sentences(self):
        content = '农行今日宣布新政策。第二句话补充。第三句无关。'
        assert target_in_lead('无关标题', content, '中国农业银行',
                              aliases=self.AGRI_ALIASES) == 1.0
        # 第 3 句之后才出现 → 不算导语
        content2 = '第一句无关。第二句无关。后文才提到农业银行。'
        assert target_in_lead('无关标题', content2, '中国农业银行',
                              aliases=self.AGRI_ALIASES, k_sentences=2) == 0.0

    def test_exclusion_rules_applied(self, exclusion_setup):
        neg_ac, short_excl, cw = exclusion_setup
        # '涉农行业' 中的 '农行' 经排除规则不计 (裸匹配会误报)
        assert target_in_lead('涉农行业协会发布报告', '正文无关。',
                              '中国农业银行', aliases=self.AGRI_ALIASES) == 1.0
        assert target_in_lead('涉农行业协会发布报告', '正文无关。',
                              '中国农业银行', aliases=self.AGRI_ALIASES,
                              negation_ac=neg_ac,
                              short_name_exclusions=short_excl,
                              context_window=cw) == 0.0

    def test_empty_bank_name_nan(self):
        assert math.isnan(target_in_lead('t', 'c', ''))


# ============================================================================
# g-entity-13: salience 缺失源字段 NaN 路径
# ============================================================================

class TestSalienceMissingFields:
    def test_front_page_all_missing_nan(self):
        r = parse_front_page('', '')
        assert all(math.isnan(r[k]) for k in
                   ('is_front_page', 'is_front_section', 'page_rank'))

    def test_front_page_present_unchanged(self):
        r = parse_front_page('财经', 'A05')
        assert r['is_front_page'] == 0.0
        assert r['page_rank'] == 5.0
        assert parse_front_page('头版', 'A01')['is_front_page'] == 1.0
        # 版面在场但页号缺失 → page_rank NaN, 二值列仍可判
        assert math.isnan(parse_front_page('财经', '')['page_rank'])

    def test_byline_missing_author_nan(self):
        r = parse_byline('', '普通正文开头没有电头线索可循')
        assert math.isnan(r['has_byline']) and math.isnan(r['is_wire'])

    def test_byline_missing_author_with_wire_head(self):
        r = parse_byline('', '新华社北京6月11日电 据报道……')
        assert r['is_wire'] == 1.0 and r['has_byline'] == 0.0

    def test_byline_placeholder_still_zero(self):
        # 显式占位符 = 字段在场的真 "无署名" 信号, 不走 NaN 路径
        assert parse_byline('佚名', '正文')['has_byline'] == 0.0
        assert parse_byline('本报记者 张三', '正文')['has_byline'] == 1.0

    def test_compute_news_salience_passthrough(self, exclusion_setup):
        neg_ac, short_excl, cw = exclusion_setup
        r = compute_news_salience(
            '', '', '', '农行公告', '农行发布消息。详情后续公布。',
            '中国农业银行',
            aliases=['中国农业银行', '农行'],
            negation_ac=neg_ac, short_name_exclusions=short_excl,
            context_window=cw)
        assert r['target_in_lead'] == 1.0
        assert math.isnan(r['is_front_page'])
        assert math.isnan(r['has_byline'])


# ============================================================================
# news_bank 集成: 去重计数 + _cell NaN 守卫 (真实 config 词典)
# ============================================================================

class TestNewsBankIntegration:
    def test_dedup_count_and_nan_salience(self):
        from news_process.pipeline.filtering import news_bank as nb
        if not nb.BANKS:
            pytest.skip('真实 bank_names.json 不可用')
        content = ('中国工商银行宣布推出新服务方案。'
                   '客户反馈良好市场反响积极正面。'
                   '中国工商银行表示将持续投入资源。'
                   '业内人士看好中国工商银行的前景。')
        df = pd.DataFrame({
            '内容': [content],
            '标题': ['中国工商银行新服务'],
            '版面': [np.nan], '页号': [np.nan], '作者': [np.nan],
        })
        out, _stats = nb.classify_batch(df)
        rows = out[out['target_bank'] == '中国工商银行']
        assert len(rows) == 1
        row = rows.iloc[0]
        # 物理 3 次提及 → 3 (旧实现嵌套双计 = 6)
        assert row['target_bank_mention_count'] == 3
        # mention_density 同步以物理计数为分子
        assert row['mention_density'] == pytest.approx(3 / len(content))
        # NaN 源字段不再 str() 成 'nan' (旧实现 'nan' 作者 → has_byline=1)
        assert math.isnan(row['is_front_page'])
        assert math.isnan(row['has_byline'])
        assert row['target_in_lead'] == 1.0
