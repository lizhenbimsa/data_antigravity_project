"""test_omni_fix_val_prompt.py — omni 审计修复组 g-val-prompt 回归锁 (2026-06-11)
==============================================================================

锁定以下修复后行为 (全部 mock 外部 API, 合成 DataFrame, 不依赖盘上大数据):

  omni-g-val-prompt-01: run_variant_llms ctx 轨变体 prompt 构造前剥离 prepend 标题
                        (镜像生产 tonellms-01, 防标题双重注入污染对照)
  omni-g-val-prompt-02: V1-V4 变体 JSON schema 升级 v8 (innovation_collab_mode 三字段);
                        collab 维度进聚合/baseline/pairwise/criteria;
                        PASS_THRESHOLD_INNOVATION_COLLAB_MODE 接入 (原死阈值)
  omni-g-val-prompt-03: pass/fail gate 双轨 AND (evaluate_track_criteria 单轨评估;
                        JSON 报 passed_full / passed_ctx)
  omni-g-val-prompt-04: 变体 locus 空票回退与生产对齐
                        (fix(omni-gapfill-18, 2026-06-12) 升级: 直接 import 生产
                        tone_llms._resolve_locus_track 同一函数对象 — 零证据空票
                        → None, keyword 有真实证据时回退 keyword 类目, 规则永久同源)
  omni-g-val-prompt-05: API 全失败行旗标列 + 一致性计算掩码 + detail CSV call_failure 列
                        + 重试缺省对齐生产 (config 覆盖须显式)
  omni-g-val-prompt-06: radius_sensitivity_llm 全 NaN κ → passed=false + pass_reason;
                        parse_track_results_from_cache scaffold 路径 fail-loud

# 白话: prompt 敏感性检验是换几种问法问 LLM 同一批文章, 看结论稳不稳。这组
# 测试确保: 换问法的对照实验和正式生产用同一套文本预处理和同一套聚合规则
# (否则比较没意义); 新增的"协同模式"维度全程接进对照; 全失败的调用要打旗标
# 不冒充有效票; 结果全是空值时要判不通过并说明原因, 不能静默放行。
"""
import asyncio
import json
import os
import sqlite3
import sys

import numpy as np
import pandas as pd
import pytest

_PROJECT_PARENT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

_MOD39_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'validation', 'prompt_sensitivity.py'
)


@pytest.fixture(scope='module')
def mod39():
    from news_process.validation import prompt_sensitivity
    return prompt_sensitivity


@pytest.fixture(scope='module')
def source_code():
    with open(_MOD39_PATH, 'r', encoding='utf-8') as f:
        return f.read()


# 18-tuple _aggregate_track 契约的可参数化 fake (v3.4.0 BREAKING)
def _make_fake_aggregate(final_v=True, final_s='正面', call_failure=0, undefined=0,
                         topics=None, innov_loci=None, innov_substs=None,
                         innov_collab_modes=None, n_fail=0):
    def fake_aggregate(_model_res, _models):
        return (
            final_v, final_s,
            1.0, 1.0,
            3, 3,
            call_failure, undefined,
            {}, list(topics or []), list(innov_loci or []), list(innov_substs or []),
            n_fail, 0.75,
            0.5, 0.5,
            list(innov_collab_modes or []), 0.5,
        )
    return fake_aggregate


_FAKE_MODELS = [
    {'model_name': f'm{i}', 'short_name': f'm{i}',
     'base_url': 'http://mock.invalid', 'api_key': 'k'}
    for i in range(3)
]


# ============================================================================
# omni-g-val-prompt-02: V1-V4 变体 v8 schema (innovation_collab_mode)
# ============================================================================

class TestV8VariantSchema:
    def test_all_variants_contain_collab_json_fields(self, mod39):
        """4 个变体 JSON schema 均含 v8 第三维度三字段 (对齐 unified_cot.txt v8)。"""
        for vk, prompt in mod39.VARIANT_PROMPTS.items():
            for field in ('"innovation_collab_mode_reason"',
                          '"innovation_collab_mode"',
                          '"innovation_collab_mode_confidence"'):
                assert field in prompt, f"{vk}: 缺 v8 字段 {field}"
            assert '自主研发' in prompt and '外部协同' in prompt, \
                f"{vk}: 缺 Chesbrough 自主研发/外部协同 判定标准"

    def test_variants_format_safe_after_v8_upgrade(self, mod39):
        """v8 升级后 format() 仍安全 ({{/}} 转义未破坏)。"""
        kwargs = {
            'target_bank': '工商银行',
            'co_mentioned_banks': '建设银行',
            'title': '测试标题',
            'content': '测试内容',
        }
        for vk, prompt in mod39.VARIANT_PROMPTS.items():
            rendered = prompt.format(**kwargs)
            assert '"innovation_collab_mode"' in rendered, f"{vk}: 渲染丢失 collab 字段"
            assert '工商银行' in rendered

    def test_collab_threshold_defined_and_consumed(self, mod39, source_code):
        """PASS_THRESHOLD_INNOVATION_COLLAB_MODE 不再是死配置 (criteria 消费)。"""
        assert hasattr(mod39, 'PASS_THRESHOLD_INNOVATION_COLLAB_MODE')
        # 定义行之外至少一处消费 (evaluate_track_criteria + generate_reports thresholds)
        n_refs = source_code.count('PASS_THRESHOLD_INNOVATION_COLLAB_MODE')
        assert n_refs >= 3, f"collab 阈值引用 {n_refs} 处, 期望 ≥ 3 (定义+criteria+thresholds)"

    def test_aggregate_collab_majority_vote(self, mod39, monkeypatch):
        """聚合层 collab 多数票, tie→自主研发 / 空票→None (与生产 stage 21 一致)。"""
        cases = [
            (['外部协同', '外部协同', '自主研发'], '外部协同'),
            (['外部协同', '自主研发'], '自主研发'),  # 平票 → 保守默认
            ([], None),                              # 空票 → None (对齐 substantiveness)
        ]
        for votes, expected in cases:
            monkeypatch.setattr(
                mod39, '_aggregate_track',
                _make_fake_aggregate(innov_collab_modes=votes))
            df = pd.DataFrame(index=[0])
            out = mod39.aggregate_variant_results(
                df.copy(), {0: {'full': {}, 'ctx': {}}}, _FAKE_MODELS, 'VX')
            assert out['VX_innovation_collab_mode_full'].iloc[0] == expected, \
                f"votes={votes}: 期望 {expected}"

    def test_extract_baseline_includes_collab(self, mod39):
        """extract_baseline 把生产 innovation_collab_mode_full/ctx 纳入 V0 baseline。"""
        df = pd.DataFrame({
            'llm_verified_full': [True], 'llm_verified_ctx': [True],
            'llm_sentiment_full': ['正面'], 'llm_sentiment_ctx': ['正面'],
            'innovation_collab_mode_full': ['外部协同'],
            'innovation_collab_mode_ctx': ['自主研发'],
        })
        out = mod39.extract_baseline(df)
        assert out['V0_baseline_innovation_collab_mode_full'].iloc[0] == '外部协同'
        assert out['V0_baseline_innovation_collab_mode_ctx'].iloc[0] == '自主研发'

    def test_pairwise_collab_dimension_computed(self, mod39):
        """compute_pairwise_consistency 输出 collab κ/agreement (verified∩verified 子集)。"""
        n = 10
        df = pd.DataFrame({
            'V0_baseline_verified_full': [True] * n,
            'V0_baseline_sentiment_full': ['正面'] * n,
            'VX_verified_full': [True] * n,
            'VX_sentiment_full': ['正面'] * n,
            'V0_baseline_innovation_collab_mode_full': ['外部协同', '自主研发'] * 5,
            'VX_innovation_collab_mode_full': ['外部协同', '自主研发'] * 5,
        })
        r = mod39.compute_pairwise_consistency(df, 'VX', '_full')
        assert r['innovation_collab_mode_agreement'] == 1.0
        assert r['cohens_kappa_innovation_collab_mode'] == 1.0
        assert r['innovation_collab_mode_n'] == n


# ============================================================================
# omni-g-val-prompt-01: ctx 轨变体 prompt 剥离 prepend 标题
# ============================================================================

class TestCtxTitleStrip:
    def test_run_variant_llms_strips_prepended_title_on_ctx(self, mod39, monkeypatch):
        """ctx 轨 content_ctx = prepend(标题, 窗口) → prompt 中标题只出现 1 次 (来自 {title} 字段)。"""
        from news_process.core.text.entity_context import _TITLE_SEP

        title = 'XYZ独特测试标题QWE'
        body = '工商银行发布区块链平台, 用于供应链金融。'
        df = pd.DataFrame({
            '内容': [body],
            'content_ctx': [f'{title}{_TITLE_SEP}{body}'],  # stage 13 prepend 形态
            'target_bank': ['工商银行'],
            'co_mentioned_banks': ['建设银行'],
            '标题': [title],
        })

        captured = []

        async def fake_fetch(session, semaphore, prompt, m, idx, track, **kwargs):
            captured.append((track, prompt))
            return idx, m['model_name'], None, track

        async def fake_preflight(session, models, availability):
            return None

        monkeypatch.setattr(mod39, 'fetch_llm_async', fake_fetch)
        monkeypatch.setattr(mod39, 'preflight_model_availability', fake_preflight)

        models = _FAKE_MODELS[:1]
        asyncio.run(mod39.run_variant_llms(
            df, mod39.VARIANT_PROMPTS['V1_role'], models, 'V1_role'))

        prompts = dict(captured)  # {'full': ..., 'ctx': ..., 'ss': ...}
        # fix(log-reaudit-2026-06-20, P1-A): run_variant_llms 自 v3.9.0 起硬迭代三轨
        # (full/ctx/ss, prompt_sensitivity.py:634-637); 本断言建于 _ss 第三轨之前 (写死
        # {'full','ctx'}), 已陈旧 → 现实返回 {'full','ctx','ss'}, 与 content_ss 缺列时
        # 回退 content_full (镜像 full) 的设计一致 (源 :630-631)。
        assert set(prompts) == {'full', 'ctx', 'ss'}
        # 修复前 ctx prompt 标题出现 2 次 ({title} 字段 + content_ctx 前缀); 修复后均为 1 次
        assert prompts['ctx'].count(title) == 1, \
            f"ctx 轨标题双重注入未剥离: {prompts['ctx'].count(title)} 次"
        assert prompts['full'].count(title) == 1
        # ss 轨: 本样本无 content_ss 列 → 回退 content_full (镜像 full), 标题应仅 1 次
        assert prompts['ss'].count(title) == 1, \
            f"ss 轨标题注入异常: {prompts['ss'].count(title)} 次"
        assert body in prompts['ctx']  # 正文窗口本体保留


# ============================================================================
# omni-g-val-prompt-04 (+ omni-gapfill-18 升级): locus 聚合与生产同源
# ============================================================================

class TestLocusKeywordFallback:
    def test_locus_resolver_is_production_function(self, mod39):
        """fix(omni-gapfill-18): 变体侧绑定的就是生产模块级 _resolve_locus_track
        本体 (同一函数对象), 任何生产侧规则演进自动同源, 不再手工内联对齐。"""
        from news_process.pipeline.sentiment import tone_llms
        assert mod39._resolve_locus_track is tone_llms._resolve_locus_track

    def test_empty_locus_votes_fall_back_to_keyword_category(self, mod39, monkeypatch):
        """LLM 空票 + keyword 有真实证据 (conf>0) → keyword 类目 (生产同款)。"""
        monkeypatch.setattr(
            mod39, '_aggregate_track',
            _make_fake_aggregate(topics=['区块链'], innov_loci=[]))
        df = pd.DataFrame(index=[0])
        out = mod39.aggregate_variant_results(
            df.copy(), {0: {'full': {}, 'ctx': {}}}, _FAKE_MODELS, 'VX')
        expected_cat, expected_conf = mod39.canonicalize_topic('区块链')
        assert expected_conf > 0  # 前提: '区块链' 是真实 keyword 证据
        assert out['VX_innovation_locus_full'].iloc[0] == expected_cat
        assert out['VX_innovation_locus_full'].iloc[0] is not None

    def test_empty_votes_and_zero_evidence_yield_none(self, mod39, monkeypatch):
        """fix(omni-gapfill-18): 空票 + 零 keyword 证据 → None (生产 g-tonellms-10
        行为; 旧断言 '应用场景' 锁的是已被生产推翻的 keyword 硬默认)。"""
        monkeypatch.setattr(
            mod39, '_aggregate_track',
            _make_fake_aggregate(topics=[], innov_loci=[]))
        df = pd.DataFrame(index=[0])
        out = mod39.aggregate_variant_results(
            df.copy(), {0: {'full': {}, 'ctx': {}}}, _FAKE_MODELS, 'VX')
        assert out['VX_innovation_locus_full'].iloc[0] is None

    def test_nonempty_locus_votes_unchanged(self, mod39, monkeypatch):
        """多数票非空时行为与修复前一致 (keyword 回退不干预)。"""
        monkeypatch.setattr(
            mod39, '_aggregate_track',
            _make_fake_aggregate(topics=['区块链'],
                                 innov_loci=['底层技术', '底层技术', '应用场景']))
        df = pd.DataFrame(index=[0])
        out = mod39.aggregate_variant_results(
            df.copy(), {0: {'full': {}, 'ctx': {}}}, _FAKE_MODELS, 'VX')
        assert out['VX_innovation_locus_full'].iloc[0] == '底层技术'


# ============================================================================
# omni-g-val-prompt-05: 调用失败旗标 + 掩码 + 重试对齐/披露
# ============================================================================

class TestCallFailureMasking:
    def _df_with_failures(self):
        n_ok, n_fail = 10, 2
        n = n_ok + n_fail
        return pd.DataFrame({
            'V0_baseline_verified_full': [True] * n,
            'V0_baseline_sentiment_full': ['正面'] * n,
            # 失败行落到默认 False/'None' — 修复前会计为"措辞不一致"
            'VX_verified_full': [True] * n_ok + [False] * n_fail,
            'VX_sentiment_full': ['正面'] * n_ok + ['None'] * n_fail,
            'VX_call_failure_full': [0] * n_ok + [1] * n_fail,
        })

    def test_aggregate_keeps_failure_flags(self, mod39, monkeypatch):
        """_call_failure/_undefined 旗标不再丢弃, 物化为列。"""
        monkeypatch.setattr(
            mod39, '_aggregate_track',
            _make_fake_aggregate(final_v=False, final_s=None,
                                 call_failure=1, undefined=0, n_fail=3))
        df = pd.DataFrame(index=[0])
        out = mod39.aggregate_variant_results(
            df.copy(), {0: {'full': {}, 'ctx': {}}}, _FAKE_MODELS, 'VX')
        assert out['VX_call_failure_full'].iloc[0] == 1
        assert out['VX_undefined_full'].iloc[0] == 0

    def test_pairwise_masks_call_failure_rows(self, mod39):
        """失败行掩码后一致率 1.0 (API 噪声不再计入措辞不一致), 剔除量披露。"""
        r = mod39.compute_pairwise_consistency(self._df_with_failures(), 'VX', '_full')
        assert r['verification_agreement'] == 1.0
        assert r['sentiment_agreement'] == 1.0
        assert r['n_call_failures_excluded'] == 2
        assert r['n_compared'] == 10

    def test_pairwise_backcompat_without_flag_column(self, mod39):
        """旗标列缺失时向后兼容: 不掩码, n_call_failures_excluded=0。"""
        df = self._df_with_failures().drop(columns=['VX_call_failure_full'])
        r = mod39.compute_pairwise_consistency(df, 'VX', '_full')
        assert r['verification_agreement'] < 1.0  # 失败行未掩码 → 计入不一致
        assert r['n_call_failures_excluded'] == 0
        assert r['n_compared'] == 12

    def test_pairwise_all_failed_returns_nan(self, mod39):
        """全失败 → 指标 NaN (fail-loud), 不产伪一致率。"""
        df = self._df_with_failures()
        df['VX_call_failure_full'] = 1
        r = mod39.compute_pairwise_consistency(df, 'VX', '_full')
        assert np.isnan(r['verification_agreement'])
        assert r['n_compared'] == 0
        assert r['n_call_failures_excluded'] == 12

    def test_multivariant_masks_any_variant_failure(self, mod39):
        """任一变体失败的行从 α/Fleiss κ 剔除, n_items 披露。"""
        n = 10
        rng = np.random.RandomState(0)
        df = pd.DataFrame({
            'V0_baseline_verified_full': rng.choice([True, False], n),
            'VA_verified_full': rng.choice([True, False], n),
            'VB_verified_full': rng.choice([True, False], n),
            'VA_call_failure_full': [0] * 9 + [1],
            'VB_call_failure_full': [0] * n,
        })
        multi = mod39.compute_multivariant_consistency(df, ['VA', 'VB'], '_full')
        assert multi['n_items'] == 9
        assert multi['n_call_failures_excluded'] == 1

    def test_prompt_max_retries_default_aligned_to_production(self, mod39, source_code):
        """重试缺省对齐生产 MAX_RETRIES (config 显式 max_retries 仍可覆盖, 已在 YAML 披露)。"""
        assert "PS_CFG.get('max_retries', _tone_llms.MAX_RETRIES)" in source_code, \
            "缺省值应为生产 MAX_RETRIES 而非硬编码 1"
        cfg_val = mod39.PS_CFG.get('max_retries', mod39._tone_llms.MAX_RETRIES)
        expected = max(1, min(mod39._tone_llms.MAX_RETRIES, int(cfg_val)))
        assert expected == mod39.PROMPT_MAX_RETRIES


# ============================================================================
# omni-g-val-prompt-03: 双轨 pass/fail gate
# ============================================================================

def _mk_pairwise(v_agree=0.95, s_agree=0.95, kappa=0.9, iss_k=0.9, il_k=0.9, icm_k=0.9):
    return {
        'verification_agreement': v_agree,
        'sentiment_agreement': s_agree,
        'cohens_kappa_verification': kappa,
        'cohens_kappa_innovation_substantiveness': iss_k,
        'cohens_kappa_innovation_locus': il_k,
        'cohens_kappa_innovation_collab_mode': icm_k,
    }


class TestDualTrackGate:
    VARIANTS = ['V1_role', 'V2_structure']

    def _results(self, ctx_icm_k=0.9):
        pairwise = {
            '_full': {vk: _mk_pairwise() for vk in self.VARIANTS},
            '_ctx': {vk: _mk_pairwise(icm_k=ctx_icm_k) for vk in self.VARIANTS},
        }
        multi = {
            '_full': {'krippendorffs_alpha': 0.9, 'fleiss_kappa': 0.9},
            '_ctx': {'krippendorffs_alpha': 0.9, 'fleiss_kappa': 0.9},
        }
        return pairwise, multi

    def test_both_tracks_good_passes(self, mod39):
        pairwise, multi = self._results()
        for track in ['_full', '_ctx']:
            criteria, _ = mod39.evaluate_track_criteria(
                pairwise, multi, self.VARIANTS, track)
            assert all(criteria.values()), f"{track} 应全过: {criteria}"

    def test_full_pass_ctx_fail_overall_fail(self, mod39):
        """full 过而 ctx 不过 → 总判定 (AND) 必须不过 — 修复前仅看 full 会误报通过。"""
        pairwise, multi = self._results(ctx_icm_k=0.4)
        crit_full, _ = mod39.evaluate_track_criteria(pairwise, multi, self.VARIANTS, '_full')
        crit_ctx, _ = mod39.evaluate_track_criteria(pairwise, multi, self.VARIANTS, '_ctx')
        passed_full = all(crit_full.values())
        passed_ctx = all(crit_ctx.values())
        assert passed_full is True
        assert passed_ctx is False
        assert (passed_full and passed_ctx) is False

    def test_collab_criterion_present_and_gating(self, mod39):
        """collab κ 低于阈值时 collab criterion=False (死阈值已接线)。"""
        pairwise, multi = self._results(ctx_icm_k=0.4)
        criteria, summary = mod39.evaluate_track_criteria(
            pairwise, multi, self.VARIANTS, '_ctx')
        collab_keys = [k for k in criteria if 'innovation_collab_mode' in k]
        assert len(collab_keys) == 1, f"criteria 缺 collab 项: {list(criteria)}"
        assert criteria[collab_keys[0]] is False
        assert summary['min_kappa_innovation_collab_mode'] == 0.4

    def test_nan_collab_kappa_fails_criterion(self, mod39):
        """collab κ 全 NaN (无可评估样本) → criterion False, 不空泛通过。"""
        pairwise, multi = self._results()
        for vk in self.VARIANTS:
            pairwise['_ctx'][vk]['cohens_kappa_innovation_collab_mode'] = float('nan')
        criteria, _ = mod39.evaluate_track_criteria(pairwise, multi, self.VARIANTS, '_ctx')
        collab_key = [k for k in criteria if 'innovation_collab_mode' in k][0]
        assert criteria[collab_key] is False

    def test_generate_reports_per_track_passed_fields(self, mod39, tmp_path):
        """JSON 报 passed/passed_full/passed_ctx 三字段 + collab 阈值 + 重试披露;
        detail CSV 含 call_failure 列。"""
        n = 6
        df = pd.DataFrame({
            'V0_baseline_verified_full': [True] * n,
            'V0_baseline_verified_ctx': [True] * n,
            'V0_baseline_sentiment_full': ['正面'] * n,
            'V0_baseline_sentiment_ctx': ['正面'] * n,
            'VX_verified_full': [True] * n,
            'VX_verified_ctx': [True] * n,
            'VX_sentiment_full': ['正面'] * n,
            'VX_sentiment_ctx': ['正面'] * n,
            'VX_call_failure_full': [0] * (n - 1) + [1],
            'VX_call_failure_ctx': [0] * n,
        })
        pairwise = {'_full': {'VX': _mk_pairwise()}, '_ctx': {'VX': _mk_pairwise()}}
        multi = {
            '_full': {'krippendorffs_alpha': 0.9, 'fleiss_kappa': 0.9},
            '_ctx': {'krippendorffs_alpha': 0.9, 'fleiss_kappa': 0.9},
        }
        variance = {'_full': {'true_rate_std': 0.01}, '_ctx': {'true_rate_std': 0.01}}

        mod39.generate_reports(
            df, ['VX'], pairwise, multi, variance, False, str(tmp_path),
            passed_by_track={'_full': True, '_ctx': False},
        )

        with open(os.path.join(str(tmp_path), 'prompt_sensitivity_results.json'),
                  encoding='utf-8') as f:
            rpt = json.load(f)
        assert rpt['passed'] is False
        assert rpt['passed_full'] is True
        assert rpt['passed_ctx'] is False
        assert 'innovation_collab_mode_kappa' in rpt['thresholds']
        assert 'prompt_max_retries' in rpt and 'production_max_retries' in rpt

        csv_df = pd.read_csv(
            os.path.join(str(tmp_path), 'prompt_sensitivity_detail.csv'))
        assert 'call_failure' in csv_df.columns
        full_rows = csv_df[csv_df['track'] == 'full']
        assert int(full_rows['call_failure'].sum()) == 1


# ============================================================================
# omni-g-val-prompt-06: radius_sensitivity_llm 空泛通过 + scaffold fail-loud
# ============================================================================

def _nan_kappa_entry():
    return {'kappa': float('nan'), 'observed_agreement': float('nan'),
            'expected_agreement': float('nan'), 'n': 0}


def _good_kappa_entry(k=0.85):
    return {'kappa': k, 'observed_agreement': 0.9,
            'expected_agreement': 0.5, 'n': 100}


class TestRadiusLLMGate:
    DIMS = ['sentiment', 'innovation_locus', 'innovation_substantiveness']

    def _write(self, report, tmp_path):
        from news_process.validation.radius_sensitivity_llm import write_radius_llm_report
        out_path = os.path.join(str(tmp_path), 'radius_report.json')
        write_radius_llm_report(report, out_path, {'total_calls': 0}, baseline_n=0)
        with open(out_path, encoding='utf-8') as f:
            return json.load(f)

    def test_all_nan_kappa_not_passed(self, tmp_path):
        """全 NaN κ (零证据) → passed=false + insufficient_data 原因, 不再 all([])==True。"""
        report = {dim: {0: _nan_kappa_entry(), 2: _nan_kappa_entry()}
                  for dim in self.DIMS}
        data = self._write(report, tmp_path)
        assert data['passed'] is False
        assert 'insufficient_data' in data['pass_reason']

    def test_one_dim_all_nan_not_passed(self, tmp_path):
        """单维度全 NaN (其余达标) → 整体不过 (每维度须 ≥1 个可评估 κ)。"""
        report = {dim: {0: _good_kappa_entry()} for dim in self.DIMS}
        report['innovation_locus'] = {0: _nan_kappa_entry()}
        data = self._write(report, tmp_path)
        assert data['passed'] is False
        assert 'innovation_locus' in data['pass_reason']

    def test_all_dims_evaluable_and_above_threshold_passes(self, tmp_path):
        report = {dim: {0: _good_kappa_entry(0.85), 2: _good_kappa_entry(0.92)}
                  for dim in self.DIMS}
        data = self._write(report, tmp_path)
        assert data['passed'] is True
        assert data['pass_reason'].startswith('passed')

    def test_below_threshold_fails(self, tmp_path):
        report = {dim: {0: _good_kappa_entry(0.85)} for dim in self.DIMS}
        report['sentiment'][0] = _good_kappa_entry(0.5)
        data = self._write(report, tmp_path)
        assert data['passed'] is False
        assert 'sentiment' in data['pass_reason']

    def test_dimension_status_disclosed(self, tmp_path):
        report = {dim: {0: _good_kappa_entry(0.85)} for dim in self.DIMS}
        data = self._write(report, tmp_path)
        assert set(data['dimension_status']) == set(self.DIMS)
        for s in data['dimension_status'].values():
            assert s['n_evaluable'] == 1


class TestParseCacheFailLoud:
    def test_raises_not_implemented_when_cache_has_tables(self, tmp_path):
        """cache 含表时 fail-loud, 不再静默返回全 None 占位行 (假阳性源头)。"""
        from news_process.validation.radius_sensitivity_llm import (
            parse_track_results_from_cache,
        )
        db = tmp_path / '_cache_with_table.db'
        conn = sqlite3.connect(str(db))
        conn.execute('CREATE TABLE cache (k TEXT, v TEXT)')
        conn.commit()
        conn.close()
        with pytest.raises(NotImplementedError):
            parse_track_results_from_cache(
                radius=0,
                articles_df=pd.DataFrame({'article_idx': [1], 'target_bank': ['工商银行']}),
                cache_db_path=str(db),
            )

    def test_cache_missing_still_graceful_empty_df(self, tmp_path):
        """cache 不存在 → 仍返回空 DataFrame (graceful, 既有行为不回归)。"""
        from news_process.validation.radius_sensitivity_llm import (
            parse_track_results_from_cache,
        )
        df = parse_track_results_from_cache(
            radius=0,
            articles_df=pd.DataFrame({'article_idx': [], 'target_bank': []}),
            cache_db_path=str(tmp_path / '_nope.db'),
        )
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
