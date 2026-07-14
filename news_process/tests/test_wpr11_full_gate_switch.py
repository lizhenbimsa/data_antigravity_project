"""test_wpr11_full_gate_switch.py — WP-R1.1 full-only 总判定切换 + S9 文本修复回归锁
================================================================================

覆盖 PROMPT_ASSETS_AUDIT_EXECUTION_PLAN_2026-07-12.md §2 表 S9 全部文本修复 +
§10 WP-R1.1 ①②③（详见模块头 prompt_sensitivity.py 的 "WP-R1.1 收口" 段落）:

  (a) 总判定 full-only 语义: full 全过 + ctx 挂 → passed=True；
      full 挂 + ctx 全过 → passed=False（镜像修复前"三轨 AND"会得到相反结论）。
  (b) results.json 含 per-track 分判定字段 (passed_full/passed_ctx/passed_ss)，
      且总 passed 不再等于三轨 AND。
  (c) 源码回归闸: run_variant_llms 内 fetch_llm_async 调用显式传 prompt_version
      (WP-R1.1③, 防回退到缺省 'v0' 命名空间); main() 总判定计算点用
      passed_by_track.get('_full', ...) 而非 all(... for track in active_tracks)。
  (d) 变体文本 gate: 4 变体头部计数词（"三项"/"三阶段"）与生产 prompt (unified_cot.txt)
      的三阶段数动态比对 (不硬编码 "3", 从 <stepN_...> 标签数派生, 防 16/17 教训式
      写死数字与源漂移); 8 处 *_reason 字段 "须引用文章具体内容" 指示在位。

全部 mock/合成数据, $0, fast, 不依赖盘上大数据或 LLM API。
"""
import os
import re
import sys

import pytest

_PROJECT_PARENT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

_MOD_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'validation', 'prompt_sensitivity.py'
)
_UNIFIED_COT_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'config', 'prompts', 'unified_cot.txt'
)

_CN_NUM = {'一': 1, '两': 2, '二': 2, '三': 3, '四': 4, '五': 5}


@pytest.fixture(scope='module')
def mod():
    from news_process.validation import prompt_sensitivity
    return prompt_sensitivity


@pytest.fixture(scope='module')
def source_code():
    with open(_MOD_PATH, 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture(scope='module')
def production_stage_count():
    """从 unified_cot.txt 派生生产 prompt 的阶段数 (<step1_..>/<step2_..>/<step3_..>),
    不硬编码 "3" —— 防止测试锚点与源文件未来演进 (若 v9 升级增删阶段) 漂移脱节。
    """
    with open(_UNIFIED_COT_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    step_tags = set(re.findall(r'<step(\d+)_', text))
    assert step_tags, "unified_cot.txt 未找到 <stepN_...> 标签, 无法派生阶段数"
    return len(step_tags)


def _mk_pairwise(v_agree=0.95, s_agree=0.95, kappa=0.9, iss_k=0.9, il_k=0.9, icm_k=0.9):
    return {
        'verification_agreement': v_agree,
        'sentiment_agreement': s_agree,
        'cohens_kappa_verification': kappa,
        'cohens_kappa_innovation_substantiveness': iss_k,
        'cohens_kappa_innovation_locus': il_k,
        'cohens_kappa_innovation_collab_mode': icm_k,
    }


_VARIANTS = ['V1_role', 'V2_structure']


def _pairwise_multi(full_ok: bool, ctx_ok: bool):
    """构造最小 per-track pairwise/multi 结果: full/ctx 各自全过或至少一项不过。"""
    pairwise = {
        '_full': {vk: _mk_pairwise() for vk in _VARIANTS} if full_ok
                 else {vk: _mk_pairwise(kappa=0.1) for vk in _VARIANTS},
        '_ctx': {vk: _mk_pairwise() for vk in _VARIANTS} if ctx_ok
                else {vk: _mk_pairwise(icm_k=0.1) for vk in _VARIANTS},
    }
    multi = {
        '_full': {'krippendorffs_alpha': 0.9 if full_ok else 0.1, 'fleiss_kappa': 0.9},
        '_ctx': {'krippendorffs_alpha': 0.9 if ctx_ok else 0.1, 'fleiss_kappa': 0.9},
    }
    return pairwise, multi


class TestFullOnlyGateSemantics:
    """(a) 总判定 full-only 语义 —— 与修复前"三轨 AND"直接相反的两个案例。"""

    def _passed_by_track(self, mod, full_ok, ctx_ok):
        pairwise, multi = _pairwise_multi(full_ok, ctx_ok)
        passed_by_track = {}
        for track in ('_full', '_ctx'):
            criteria, _ = mod.evaluate_track_criteria(pairwise, multi, _VARIANTS, track)
            passed_by_track[track] = all(criteria.values())
        return passed_by_track

    def test_full_pass_ctx_fail_yields_total_pass(self, mod):
        """full 全过 + ctx 挂 → full-only 总判定 = True (修复前三轨 AND 会是 False)。"""
        passed_by_track = self._passed_by_track(mod, full_ok=True, ctx_ok=False)
        assert passed_by_track['_full'] is True
        assert passed_by_track['_ctx'] is False
        # fix(WP-R1.1②, 2026-07-14): main() 的唯一计算点等价于此表达式
        total_passed = passed_by_track.get('_full', False)
        assert total_passed is True, "full-only 语义下 full 全过应总判定通过"
        # 与修复前语义对比: 若仍是三轨 AND, 总判定会是 False —— 确认两者确实不同
        legacy_and = all(passed_by_track[t] for t in ('_full', '_ctx'))
        assert legacy_and is False
        assert total_passed != legacy_and, "本用例应能区分 full-only 与三轨 AND 两种语义"

    def test_full_fail_ctx_pass_yields_total_fail(self, mod):
        """full 挂 + ctx 全过 → full-only 总判定 = False (即便 ctx 满分也不能救总判定)。"""
        passed_by_track = self._passed_by_track(mod, full_ok=False, ctx_ok=True)
        assert passed_by_track['_full'] is False
        assert passed_by_track['_ctx'] is True
        total_passed = passed_by_track.get('_full', False)
        assert total_passed is False, "full 轨未过线时, ctx 再好也不能让总判定通过"


class TestPerTrackResultStructure:
    """(b) results.json 含 per-track 分判定字段, 且总 passed 独立于 ctx/ss。"""

    def test_generate_reports_passed_full_only_semantics(self, mod, tmp_path):
        """passed_full=True/passed_ctx=False 时, 传入的总 passed (由调用方按
        full-only 规则算好) 应被原样落盘, 不因 ctx=False 被拖累。"""
        import json

        import pandas as pd

        n = 4
        df = pd.DataFrame({
            'V0_baseline_verified_full': [True] * n,
            'V0_baseline_verified_ctx': [True] * n,
            'V0_baseline_sentiment_full': ['正面'] * n,
            'V0_baseline_sentiment_ctx': ['正面'] * n,
            'VX_verified_full': [True] * n,
            'VX_verified_ctx': [True] * n,
            'VX_sentiment_full': ['正面'] * n,
            'VX_sentiment_ctx': ['正面'] * n,
        })
        pairwise = {'_full': {'VX': _mk_pairwise()}, '_ctx': {'VX': _mk_pairwise()}}
        multi = {
            '_full': {'krippendorffs_alpha': 0.9, 'fleiss_kappa': 0.9},
            '_ctx': {'krippendorffs_alpha': 0.9, 'fleiss_kappa': 0.9},
        }
        variance = {'_full': {'true_rate_std': 0.01}, '_ctx': {'true_rate_std': 0.01}}

        # full-only 总判定: passed=True 即便 passed_ctx=False (镜像 main() 的
        # passed = passed_by_track.get('_full', False))
        mod.generate_reports(
            df, ['VX'], pairwise, multi, variance, True, str(tmp_path),
            passed_by_track={'_full': True, '_ctx': False},
        )
        with open(os.path.join(str(tmp_path), 'prompt_sensitivity_results.json'),
                  encoding='utf-8') as f:
            rpt = json.load(f)

        assert rpt['passed'] is True
        assert rpt['passed_full'] is True
        assert rpt['passed_ctx'] is False
        # ss 未传轨道时字段仍存在且为 None (向后兼容, 非缺失 key)
        assert 'passed_ss' in rpt
        assert rpt['passed_ss'] is False or rpt['passed_ss'] is None


class TestSourceRegressionGuards:
    """(c) 源码回归闸: 防止 full-only 切换 / prompt_version 补传被悄悄改回去。"""

    def test_total_passed_computed_from_full_track_only(self, source_code):
        """main() 的总判定计算点须是 full 轨单轨驱动, 不再是三轨 all(...) AND。"""
        assert "passed = passed_by_track.get('_full', False)" in source_code, (
            "总判定计算点应为 full-only (WP-R1.1②); 未找到该行, "
            "可能被改回三轨 AND 或改成了其他形式"
        )
        # 防回归: 旧的三轨 AND 计算式不应再出现在源码中
        assert "passed = all(passed_by_track[track] for track in active_tracks)" \
            not in source_code, "发现旧的三轨 AND 计算式残留, full-only 切换未彻底"

    def test_fetch_llm_async_call_passes_prompt_version(self, source_code):
        """WP-R1.1③: run_variant_llms 内 fetch_llm_async 调用须显式传 prompt_version
        (防回退到 fetch_llm_async 缺省 'v0' 命名空间)。"""
        run_start = source_code.find('async def run_variant_llms')
        assert run_start != -1, "run_variant_llms 函数未找到"
        run_end = source_code.find('\ndef ', run_start + 1)
        if run_end == -1:
            run_end = source_code.find('\nasync def ', run_start + 1)
        body = source_code[run_start:run_end if run_end != -1 else run_start + 6000]

        assert 'variant_prompt_version' in body, \
            "run_variant_llms 内未见 variant_prompt_version 构造"
        assert 'prompt_version=variant_prompt_version' in body, (
            "fetch_llm_async 调用未显式传 prompt_version=variant_prompt_version "
            "(WP-R1.1③ 回归: 会落缺省 'v0' 命名空间)"
        )
        # 构造须挂靠生产 PROMPT_VERSION (命名空间可读溯源), 不是裸写死字符串
        assert '_tone_llms.PROMPT_VERSION' in body


class TestVariantTextGate:
    """(d) S9 变体文本 gate: 计数词与任务数动态比对 + 8 处 reason 指示在位。"""

    _HEADER_RE = re.compile(r'完成(?:以下)?(?:顺序)?([两三四五六七八九十]+)(?:项|阶段)')

    def test_variant_headers_task_count_matches_production_stages(
        self, mod, production_stage_count,
    ):
        """4 变体头部计数词 (原"两项/两阶段", v8 升级漏改) 须等于生产 prompt 的
        阶段数 (从 unified_cot.txt <stepN_...> 标签动态派生, 当前 = 3;
        不硬编码 "3" 以防未来 v9 阶段数变化时测试跟着漂移失效)。"""
        assert production_stage_count >= 2, "派生阶段数异常, 检查 unified_cot.txt"
        for vk, prompt in mod.VARIANT_PROMPTS.items():
            header = prompt[:200]
            m = self._HEADER_RE.search(header)
            assert m is not None, f"{vk}: 头部未找到计数词 (完成...项/阶段模式): {header!r}"
            cn_num = m.group(1)
            assert cn_num in _CN_NUM, f"{vk}: 未识别的中文数词 '{cn_num}'"
            assert _CN_NUM[cn_num] == production_stage_count, (
                f"{vk}: 头部计数词 '{cn_num}'({_CN_NUM[cn_num]}) 与生产阶段数 "
                f"{production_stage_count} 不一致 (S9: 应为 '三项'/'三阶段')"
            )

    def test_reason_fields_carry_cite_article_instruction(self, mod):
        """8 处 (4 变体 × innovation_substantiveness_reason/innovation_collab_mode_reason)
        须含 "须引用文章具体内容" (对齐 unified_cot.txt:105,111 生产口径)。"""
        target_keys = (
            'innovation_substantiveness_reason',
            'innovation_collab_mode_reason',
        )
        n_checked = 0
        for vk, prompt in mod.VARIANT_PROMPTS.items():
            for key in target_keys:
                pat = re.compile(rf'"{key}"\s*:\s*"([^"]*)"')
                m = pat.search(prompt)
                assert m is not None, f"{vk}: 未找到字段 {key}"
                assert '须引用文章具体内容' in m.group(1), (
                    f"{vk}.{key} 缺少 '须引用文章具体内容' 指示 (S9 遗漏)"
                )
                n_checked += 1
        assert n_checked == len(mod.VARIANT_PROMPTS) * len(target_keys) == 8

    def test_deliberate_perturbations_untouched(self, mod):
        """§4-3 铁律: V1-V4 各自刻意扰动 (角色改写/结构调序/精简/整句改写) 一个字
        不许被 S9 修字连带改动 —— 抽查每个变体仍保有其设计特征关键词。"""
        assert '角色' in mod.VARIANT_LABELS['V1_role'] or 'Role' in mod.VARIANT_LABELS['V1_role']
        v2 = mod.VARIANT_PROMPTS['V2_structure']
        assert '## 第一步' in v2 and '## 第二步' in v2 and '## 第三步' in v2, \
            "V2 结构重组 (调序 + Markdown 标题) 特征应保留"
        v3 = mod.VARIANT_PROMPTS['V3_concise']
        assert len(v3) < len(mod.VARIANT_PROMPTS['V1_role']), \
            "V3 精简变体应仍明显短于 V1 (精简特征未被误改)"
        v4 = mod.VARIANT_PROMPTS['V4_paraphrase']
        assert '<step1_verification>' in v4 and '<role>' in v4, \
            "V4 XML 标签改写特征应保留"
