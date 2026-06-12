"""tests/test_omni_fix_preprocess.py — omni 审计 g-preprocess 组修复回归锁 (2026-06-11).

锁定 7 条 finding 的修复后行为 (防静默 revert):
  - omni-g-preprocess-01: TAIL_CLEANUP_PATTERN 重复压缩支排除数字 ([^0-9])
  - omni-g-preprocess-02: phone_pattern 两支加 (?<!\\d)/(?!\\d) 数字边界锚
  - omni-g-preprocess-03: 互动计数 noise 族 + pagination 裸 \\d+/\\d+ 支 config 开关 (报纸默认关闭)
  - omni-g-preprocess-04: 增量缓存键纳入 normalization 段 + 资源文件 sha256 + 代码版本
  - omni-g-preprocess-05: 广告高误伤词对标题行尾锚定 (AD_PATTERN_TITLE)
  - omni-g-preprocess-06: 精确去重保留首发 (日期第一键) + 媒体权重覆盖率 sidecar
  - omni-g-preprocess-07: 银行关键词 AC 自动机注入繁体/全角括号变体

全部用合成 DataFrame / 合成资源文件, 不依赖盘上大数据; opencc/selectolax 缺失的
环境对依赖它们的用例 importorskip (与既有 test_preprocess_normalize.py 行为一致)。

# 白话: 预处理(洗数据)环节的修复锁: 清"aaaa"这类重复字符时不能把 "1000亿"
# 压成 "100亿"; 删电话号码不能把长数字串(股票代码/金额)截一段走; "阅读量
# 点赞数"清理规则对报纸语料默认关掉, 免得误删正文里的"推荐30只银行股";
# 标题里的"公告"只有出现在行尾才当广告删; 同稿多家转载时保留最早发表的那份
# (不再保留权重最高的, 否则跨年转载会算错年份); 繁体/全角括号写法的银行名
# 也要认得出。
"""
from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path

import pandas as pd
import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


def _tail_repl(m: re.Match) -> str:
    """``normalize._tail_cleanup_repl`` 的纯逻辑副本.

    normalize.py 顶部 import opencc/selectolax, 在缺这两个依赖的环境不可导入;
    回调逻辑本身与生产逐分支一致 (g1*2 / g2 / 空格), 真模块版本另有
    importorskip 用例覆盖。
    """
    if m.group(1):
        return m.group(1) * 2
    elif m.group(2):
        return m.group(2)
    return ' '


# ============================================================================
# omni-g-preprocess-01 — 重复字符压缩排除数字
# ============================================================================

class TestOmni01TailCleanupDigitsPreserved:
    """重复压缩支 ([^0-9])\\1{2,} — 连零量级不再被吞."""

    def _sub(self, text: str) -> str:
        from news_process.pipeline.preprocess._constants import TAIL_CLEANUP_PATTERN
        return TAIL_CLEANUP_PATTERN.sub(_tail_repl, text)

    def test_round_amounts_preserved(self):
        # 旧行为: '1000亿' → '100亿', '5000万' → '500万'
        assert self._sub('净利润达1000亿元') == '净利润达1000亿元'
        assert self._sub('注册资本5000万元') == '注册资本5000万元'

    def test_years_preserved(self):
        # 旧行为: '2000年' → '200年', '1999年' → '199年'
        assert self._sub('2000年成立') == '2000年成立'
        assert self._sub('1999年上市') == '1999年上市'

    def test_stock_code_preserved(self):
        # 旧行为: '600000' → '600'
        assert self._sub('A股代码600000') == 'A股代码600000'

    def test_growth_rate_preserved(self):
        # 旧行为: '30000%' → '300%'
        assert self._sub('增速30000%') == '增速30000%'

    def test_letter_repeat_still_compressed(self):
        assert self._sub('aaaaa') == 'aa'

    def test_punct_branches_unchanged(self):
        # 标点/空白两支行为保持不变 (与既有 test_preprocess_normalize 口径一致)
        assert self._sub('。。。') == '。。'
        assert self._sub('。。') == '。'
        assert self._sub(' \t ') == ' '
        assert self._sub('a  b') == 'a b'

    def test_real_callback_when_importable(self):
        """真模块回调 (需 opencc + selectolax 可导入)."""
        pytest.importorskip('opencc')
        pytest.importorskip('selectolax.parser')
        from news_process.pipeline.preprocess._constants import TAIL_CLEANUP_PATTERN
        from news_process.pipeline.preprocess.normalize import _tail_cleanup_repl
        assert TAIL_CLEANUP_PATTERN.sub(_tail_cleanup_repl, '1000亿') == '1000亿'
        assert TAIL_CLEANUP_PATTERN.sub(_tail_cleanup_repl, 'aaaaa') == 'aa'


# ============================================================================
# omni-g-preprocess-02 — 电话号码正则数字边界锚
# ============================================================================

class TestOmni02PhonePatternAnchored:
    """phone_pattern 加 (?<!\\d)/(?!\\d) — 长数字串不再被部分截删."""

    def _sub(self, text: str) -> str:
        from news_process.pipeline.preprocess._constants import phone_pattern
        return phone_pattern.sub('', text)

    def test_long_digit_strings_untouched(self):
        # 旧行为: '20171231084500' → '00' (部分截删)
        assert self._sub('注册资本20171231084500') == '注册资本20171231084500'
        # 13 位 (超出座机支 12 位上限) 完全不动
        assert self._sub('市值1234567890123元') == '市值1234567890123元'
        # 旧行为: 13 开头 11 位子串被截删 → 残留尾部数字
        assert self._sub('贷款余额139000000000000元') == '贷款余额139000000000000元'

    def test_no_partial_truncation_residual(self):
        # 12 位 '138000000000' 恰好整体命中座机支 (4+8 切分, 与真实电话格式
        # 不可区分, 已知保守行为) — 锁定: 要么整体删除要么不动, 绝不部分截删
        # 拼出 '0元' 之类的错误残值 (旧行为)。
        out = self._sub('公司总资产138000000000元')
        assert out in ('公司总资产元', '公司总资产138000000000元')
        assert out != '公司总资产0元'

    def test_mobile_phone_still_removed(self):
        assert self._sub('联系电话13800138000请拨打') == '联系电话请拨打'
        assert self._sub('+8613800138000') == ''

    def test_landline_still_removed(self):
        assert self._sub('热线0755-12345678转') == '热线转'
        assert self._sub('电话010 12345678') == '电话'


# ============================================================================
# omni-g-preprocess-03 — 互动计数噪声族 config 开关 (报纸默认关闭)
# ============================================================================

_PAGINATION_PROD_VALUE = r'(第\s*\d+\s*页|共\s*\d+\s*页|\d+\s*/\s*\d+|页码|翻页|上页|下页)'


class TestOmni03InteractionNoiseGating:

    def test_disabled_removes_interaction_family_and_bare_fraction(self):
        from news_process.pipeline.preprocess._constants import filter_noise_patterns
        noise_data = {
            '_comment': '注释键应跳过',
            'view_count': 'VIEW_RE',
            'like_count': 'LIKE_RE',
            'comment_count': 'COMMENT_RE',
            'share_count': 'SHARE_RE',
            'collect_count': 'COLLECT_RE',
            'count_suffix': 'SUFFIX_RE',
            'pagination': _PAGINATION_PROD_VALUE,
            'navigation': 'NAV_RE',
        }
        out = filter_noise_patterns(noise_data, interaction_enabled=False)
        for gated in ('VIEW_RE', 'LIKE_RE', 'COMMENT_RE', 'SHARE_RE',
                      'COLLECT_RE', 'SUFFIX_RE'):
            assert gated not in out
        assert 'NAV_RE' in out
        # pagination 保留但裸 \d+/\d+ 支被摘除
        pag = next(p for p in out if '第' in p)
        assert r'\d+\s*/\s*\d+' not in pag
        assert re.search(pag, '第 3 页') is not None    # 锚定支保留
        assert re.search(pag, '3/4季度') is None        # 裸分数支已摘除

    def test_enabled_keeps_everything(self):
        from news_process.pipeline.preprocess._constants import filter_noise_patterns
        noise_data = {
            '_comment': 'x',
            'view_count': 'VIEW_RE',
            'pagination': _PAGINATION_PROD_VALUE,
        }
        out = filter_noise_patterns(noise_data, interaction_enabled=True)
        assert 'VIEW_RE' in out
        assert _PAGINATION_PROD_VALUE in out  # 原样保留

    def test_production_default_is_disabled_for_newspaper_corpus(self):
        from news_process.pipeline.preprocess._constants import INTERACTION_NOISE_ENABLED
        assert INTERACTION_NOISE_ENABLED is False

    def test_production_combined_pattern_preserves_substance(self):
        # 报纸正文实质性陈述不再被互动计数族误删 (finding 实测样例)
        from news_process.pipeline.preprocess._constants import combined_removal_pattern
        for text in (
            '专家推荐30只银行股',
            '央行就此回复12条意见',
            '不良率从3/4季度开始下降',
            '浏览4000次的报道',
        ):
            assert combined_removal_pattern.sub('', text) == text

    def test_production_combined_pattern_still_removes_web_noise(self):
        from news_process.pipeline.preprocess._constants import combined_removal_pattern
        # 非互动计数的网页噪声仍正常清除
        assert combined_removal_pattern.sub('', '阅读原文') == ''

    def test_real_noise_json_pagination_branch_present(self):
        """守卫: noise_patterns.json 的 pagination 须含预期裸分数支 (否则摘除落空)."""
        from news_process.pipeline.preprocess._constants import CONFIG
        with open(CONFIG['paths']['noise_patterns_file'], encoding='utf-8') as f:
            data = json.load(f)
        assert r'|\d+\s*/\s*\d+' in data['pagination']


# ============================================================================
# omni-g-preprocess-04 — 增量缓存键覆盖 normalization 段 + 资源内容 + 代码版本
# ============================================================================

class TestOmni04CacheKeyCoverage:

    @staticmethod
    def _key(**kw):
        from news_process.pipeline.preprocess.runner import compute_preprocess_cache_key
        defaults = dict(
            params={'p': 1},
            normalization={'opencc_config': 't2s'},
            noise_patterns_path='__no_such_noise__.json',
            bank_keywords_path='__no_such_bank__.json',
            code_version='v-test',
        )
        defaults.update(kw)
        return compute_preprocess_cache_key(**defaults)

    def test_returns_hex_sha256_and_stable(self):
        k1, k2 = self._key(), self._key()
        assert re.fullmatch(r'[0-9a-f]{64}', k1)
        assert k1 == k2  # 同输入确定性

    def test_key_changes_with_normalization_section(self):
        # 旧实现 normalization 段不入哈希 → 改 opencc_config 缓存仍命中 (缺陷)
        assert self._key(normalization={'opencc_config': 't2s'}) != \
            self._key(normalization={'opencc_config': 's2t'})

    def test_key_changes_with_resource_file_content(self, tmp_path):
        noise = tmp_path / 'noise.json'
        noise.write_text('{"a": "X"}', encoding='utf-8')
        k_before = self._key(noise_patterns_path=str(noise))
        noise.write_text('{"a": "Y"}', encoding='utf-8')
        k_after = self._key(noise_patterns_path=str(noise))
        assert k_before != k_after

    def test_key_changes_with_bank_keywords_content(self, tmp_path):
        bank = tmp_path / 'bank.json'
        bank.write_text('["工商银行"]', encoding='utf-8')
        k1 = self._key(bank_keywords_path=str(bank))
        bank.write_text('["工商银行", "建设银行"]', encoding='utf-8')
        k2 = self._key(bank_keywords_path=str(bank))
        assert k1 != k2

    def test_key_changes_with_code_version(self):
        assert self._key(code_version='v1') != self._key(code_version='v2')

    def test_key_changes_with_params(self):
        assert self._key(params={'p': 1}) != self._key(params={'p': 2})

    def test_missing_resource_files_fail_soft(self):
        # 资源缺失不抛异常 (哨兵入哈希), 与 _constants 加载失败回退一致
        k = self._key(noise_patterns_path='__definitely_missing__.json')
        assert re.fullmatch(r'[0-9a-f]{64}', k)

    def test_default_invocation_uses_production_config(self):
        from news_process.pipeline.preprocess.runner import compute_preprocess_cache_key
        k = compute_preprocess_cache_key()
        assert re.fullmatch(r'[0-9a-f]{64}', k)


# ============================================================================
# omni-g-preprocess-05 — 广告高误伤词标题行尾锚定
# ============================================================================

class TestOmni05AdTitleAnchoring:

    def test_regulatory_news_titles_survive(self):
        # 旧行为: 无锚定子串匹配 → 这些真监管新闻被整篇删除
        from news_process.pipeline.preprocess._constants import AD_PATTERN_TITLE
        assert AD_PATTERN_TITLE is not None
        for title in (
            '央行公告下调存准率',            # '公告' 在标题中部
            '上市银行年度报告显示盈利改善',  # '年度报告' 在标题中部
            '监管声明引发市场关注',          # '声明' 在标题中部
        ):
            assert AD_PATTERN_TITLE.search(title) is None, title

    def test_disclosure_titles_still_matched(self):
        from news_process.pipeline.preprocess._constants import AD_PATTERN_TITLE
        # 高误伤词在行尾 → 仍删 (真公告类标题)
        assert AD_PATTERN_TITLE.search('XX银行关于变更注册地址的公告') is not None
        assert AD_PATTERN_TITLE.search('2017年度第三期金融债券发行公告') is not None
        # 低误伤词无锚定 → 任意位置仍删
        assert AD_PATTERN_TITLE.search('XX银行半年报摘要发布') is not None

    def test_layout_pattern_unchanged_unanchored(self):
        # 版面/栏名用 AD_PATTERN 仍无锚定 (付费公告版面全量排除)
        from news_process.pipeline.preprocess._constants import AD_PATTERN
        assert AD_PATTERN.search('央行公告下调存准率') is not None
        assert AD_PATTERN.search('公告专版') is not None

    @staticmethod
    def _arrow_str_regex_quirk() -> bool:
        """检测 pandas str 后端是否拒绝 \\uXXXX 正则转义 (filter.py 步骤 8 使用).

        pandas 3.x 默认 arrow-backed str dtype 走 re2 引擎, 不支持 ``\\u4e00``
        转义 → ``_clean_and_filter_dataframe`` 步骤 8 (媒体名称清理, 与本修复
        无关的既有代码) 在该环境崩溃 (pre-existing)。生产 venv (pandas 2.x,
        object dtype + Python re) 不受影响, 本集成用例在生产环境正常执行。
        """
        try:
            # 探针与 filter.py 步骤 8 同款 \uXXXX 转义 (raw string, 字面反斜杠
            # 传给引擎) — Python re 接受, arrow/re2 后端抛 ArrowInvalid
            pd.Series(['x']).str.replace('[' + chr(92) + 'u4e00-' + chr(92) + 'u9fa5]', 'y', regex=True)
            return False
        except Exception:
            return True

    def test_filter_dataframe_title_vs_layout_behavior(self):
        """_clean_and_filter_dataframe 步骤 5: 标题锚定 / 版面无锚定."""
        if self._arrow_str_regex_quirk():
            pytest.skip('pandas arrow str 后端不支持步骤 8 的 \\u 转义 (pre-existing, '
                        '与 omni-g-preprocess-05 修复无关); 生产 venv 中执行本用例')
        from news_process.pipeline.preprocess.filter import _clean_and_filter_dataframe
        base = {
            '国家地区/省份': '北京',
            '媒体类型(中文)': '报纸',
            '媒体(中文)': '测试日报',
            '内容': '工商银行今日发布新产品, 市场反响积极。',
            '日期': '2017-06-01',
            '栏名': '财经',
        }
        rows = [
            {**base, '标题': '央行公告下调存准率', '版面': 'A01'},          # 应存活
            {**base, '标题': '关于变更注册地址的公告', '版面': 'A02'},      # 标题行尾公告 → 删
            {**base, '标题': '正常银行新闻一则', '版面': '公告专版'},        # 版面含公告 → 删
        ]
        df = pd.DataFrame(rows)
        out = _clean_and_filter_dataframe(df)
        assert list(out['标题']) == ['央行公告下调存准率']


# ============================================================================
# omni-g-preprocess-06 — 精确去重保留首发 + 媒体权重覆盖率 sidecar
# ============================================================================

def _make_dedup(tmp_path, weights):
    from news_process.pipeline.preprocess.dedup import ArticleDeduplicator
    wfile = tmp_path / 'media_weights.json'
    wfile.write_text(json.dumps(weights, ensure_ascii=False), encoding='utf-8')
    config = {
        'deduplication': {
            'jaccard_similarity_threshold': 0.8,
            'minhash_permutations': 16,
            'ngram_size': 3,
            'parallel_workers': 1,
        },
        'paths': {
            'media_weights_file': str(wfile),
            'output_dir': str(tmp_path / 'out'),
        },
    }
    return ArticleDeduplicator(
        config=config, logger_instance=logging.getLogger('test_omni_dedup'))


class TestOmni06ExactDedupFirstPublication:

    def test_keeps_earliest_date_not_highest_weight(self, tmp_path):
        # 旧行为: 按权重降序保留人民日报 (2018-01-02) → 跨年转载年度归属错位
        dd = _make_dedup(tmp_path, {'人民日报': 100, '地方小报': 20, '其他媒体': 10})
        df = pd.DataFrame({
            '标题': ['同一新闻', '同一新闻'],
            '内容': ['完全相同的正文', '完全相同的正文'],
            '媒体(中文)': ['地方小报', '人民日报'],
            '日期': ['2017-12-28', '2018-01-02'],
            'docid': ['b2', 'a1'],
        })
        out = dd._perform_exact_deduplication(dd._prepare_dataframe(df))
        assert len(out) == 1
        assert out.iloc[0]['媒体(中文)'] == '地方小报'
        assert out.iloc[0]['日期'] == '2017-12-28'

    def test_same_date_tiebreak_by_weight(self, tmp_path):
        # 同日重复 → 媒体权重仍作 tiebreak (保留高权重副本)
        dd = _make_dedup(tmp_path, {'人民日报': 100, '地方小报': 20, '其他媒体': 10})
        df = pd.DataFrame({
            '标题': ['同一新闻', '同一新闻'],
            '内容': ['完全相同的正文', '完全相同的正文'],
            '媒体(中文)': ['地方小报', '人民日报'],
            '日期': ['2018-01-02', '2018-01-02'],
            'docid': ['b2', 'a1'],
        })
        out = dd._perform_exact_deduplication(dd._prepare_dataframe(df))
        assert len(out) == 1
        assert out.iloc[0]['媒体(中文)'] == '人民日报'

    def test_nat_date_copy_loses_to_dated_copy(self, tmp_path):
        # 日期不可解析 (NaT) 的副本排末 → 有效日期副本优先保留
        dd = _make_dedup(tmp_path, {'人民日报': 100, '其他媒体': 10})
        df = pd.DataFrame({
            '标题': ['同一新闻', '同一新闻'],
            '内容': ['完全相同的正文', '完全相同的正文'],
            '媒体(中文)': ['人民日报', '地方小报'],
            '日期': ['无效日期', '2018-01-02'],
            'docid': ['a1', 'b2'],
        })
        out = dd._perform_exact_deduplication(dd._prepare_dataframe(df))
        assert len(out) == 1
        assert out.iloc[0]['媒体(中文)'] == '地方小报'

    def test_weight_coverage_sidecar_written(self, tmp_path):
        dd = _make_dedup(tmp_path, {'人民日报': 100, '其他媒体': 10})
        df = pd.DataFrame({
            '标题': ['新闻A', '新闻B', '新闻C'],
            '内容': ['正文A', '正文B', '正文C'],
            '媒体(中文)': ['人民日报', '无名晚报', '无名晚报'],
            '日期': ['2018-01-01', '2018-01-02', '2018-01-03'],
            'docid': ['a', 'b', 'c'],
        })
        dd._prepare_dataframe(df)
        dd._write_weight_coverage_sidecar()  # run() 主流程中自动调用
        sidecar = tmp_path / 'out' / 'media_weight_coverage.json'
        assert sidecar.exists()
        payload = json.loads(sidecar.read_text(encoding='utf-8'))
        assert payload['total_rows'] == 3
        assert payload['matched_rows'] == 1
        assert payload['unmatched_media'] == {'无名晚报': 2}
        assert payload['default_weight'] == 10

    def test_prepare_alone_does_not_write_sidecar(self, tmp_path):
        # validation (32a dedup_threshold) 直接复用 _prepare_dataframe 时
        # 不得覆写 stage 00 的 sidecar — 落盘仅发生在 run() 主流程
        dd = _make_dedup(tmp_path, {'人民日报': 100, '其他媒体': 10})
        df = pd.DataFrame({
            '标题': ['新闻B'],
            '内容': ['正文B'],
            '媒体(中文)': ['无名晚报'],
            '日期': ['2018-01-02'],
            'docid': ['b'],
        })
        dd._prepare_dataframe(df)
        sidecar = tmp_path / 'out' / 'media_weight_coverage.json'
        assert not sidecar.exists()
        assert dd.weight_coverage_ is not None  # payload 已暂存待 run() 落盘

    def test_full_coverage_writes_no_sidecar(self, tmp_path):
        dd = _make_dedup(tmp_path, {'人民日报': 100, '其他媒体': 10})
        df = pd.DataFrame({
            '标题': ['新闻A'],
            '内容': ['正文A'],
            '媒体(中文)': ['人民日报'],
            '日期': ['2018-01-01'],
            'docid': ['a'],
        })
        dd._prepare_dataframe(df)
        dd._write_weight_coverage_sidecar()
        sidecar = tmp_path / 'out' / 'media_weight_coverage.json'
        assert not sidecar.exists()


# ============================================================================
# omni-g-preprocess-07 — 银行关键词繁体/全角括号变体
# ============================================================================

class TestOmni07BankKeywordVariants:

    def test_fullwidth_bracket_variant_without_opencc(self):
        # 全角括号变体是纯字符串操作, 不依赖 opencc
        from news_process.pipeline.preprocess.load import _expand_keyword_variants
        out = _expand_keyword_variants(['联合银行(中国)'])
        assert '联合银行(中国)' in out
        assert '联合银行（中国）' in out

    def test_original_keywords_always_retained(self):
        from news_process.pipeline.preprocess.load import _expand_keyword_variants
        kws = ['工商银行', '建设银行']
        out = _expand_keyword_variants(kws)
        for kw in kws:
            assert kw in out

    def test_s2t_traditional_variants(self):
        pytest.importorskip('opencc')
        from news_process.pipeline.preprocess.load import (
            _ac_contains_any,
            _build_ac_automaton,
            _expand_keyword_variants,
        )
        out = _expand_keyword_variants(['中国银行'])
        assert '中國銀行' in out
        auto = _build_ac_automaton(out)
        # 繁体原文 (规范化之前) 也能命中 → 不再被静默丢弃
        assert _ac_contains_any('中國銀行宣布上调利率', auto) is True
        assert _ac_contains_any('中国银行宣布上调利率', auto) is True
        assert _ac_contains_any('完全无关文本', auto) is False

    def test_s2t_and_fullwidth_bracket_combination(self):
        pytest.importorskip('opencc')
        from news_process.pipeline.preprocess.load import _expand_keyword_variants
        out = _expand_keyword_variants(['联合银行(中国)'])
        # 繁体 × 全角括号组合形态
        assert '聯合銀行（中國）' in out

    def test_production_automaton_matches_traditional(self):
        pytest.importorskip('opencc')
        from news_process.pipeline.preprocess.load import (
            BANK_KW_AUTOMATON,
            _ac_contains_any,
        )
        if BANK_KW_AUTOMATON is None:
            pytest.skip('生产 bank_keywords 资源未加载')
        assert _ac_contains_any('中國銀行公告', BANK_KW_AUTOMATON) is True
