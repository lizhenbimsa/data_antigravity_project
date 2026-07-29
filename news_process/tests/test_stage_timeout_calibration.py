"""tests/test_stage_timeout_calibration.py — 阶段超时表的生产规模校准 gate (F19)。

**为何需要本 gate (两次实弹)**:
  · 2026-07-24: stage 15 因漏配显式 timeout 继承默认 7200s, 在生产语料上跑到 1h48m 被父端
    强杀 (当时只修了 15, **没有回头审整张超时表**);
  · 2026-07-26: stage 23 (BERT) 同一根因复发 —— 跑到 140,000/169,811 (82.4%) 触顶 7200s
    被强杀, 整条 ② 全链 5.8 小时的成果就此中断。
两次都是「超时表按 T=2 dev 规模校准, 从未按生产规模复核」。本 gate 把已实测的生产耗时
钉成断言, 使任何把超时改小 / 新增重阶段忘配超时的改动**在测试期即失败**, 而不是在
一次 6 小时的生产跑里失败。

⚠ 维护约定: 表中数字是**实测**值 (来源见各行注释), 不是估算。新增实测后按 ≥3× 余量更新。
"""
from __future__ import annotations

import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.dag import STAGES_MAIN  # noqa: E402

#: script -> (生产实测秒数, 证据来源)。仅收录**已在生产语料上实测**的阶段。
MEASURED_PRODUCTION_SECONDS = {
    '00_preprocessing.py': (6708, '2026-07-24 冷缓存全量重解析 111.8 min (热缓存趟 3,785s)'),
    '11_news_bank.py': (351, '2026-07-26 ② 全链'),
    '12_news_fintech.py': (173, '2026-07-26 ② 全链'),
    '13_cooccurrence_filter.py': (23, '2026-07-26 ② 全链'),
    '14_materialize_ctx.py': (45, '2026-07-26 ② 全链'),
    '15_fintech_intensity.py': (559, '2026-07-26 ② 全链 (GIL 修复后)'),
    '16_article_policy_alignment.py': (3659, '2026-07-26 ② 全链'),
    '21_tone_llms.py': (1475, '2026-07-26 ② 全链 (缓存全命中)'),
    '22_tone_words.py': (3744, '2026-07-26 ② 全链 (进程并行后)'),
    '23_tone_berts.py': (21400, '2026-07-26 ② 全链实测 (F19 提闸后跑完; 旧行 8717 是被杀时的低估)'),
    '24_herd_decay_processor.py': (5412, '2026-07-26 ② 全链 (F20 进程并行后)'),
    '25_article_sbert.py': (2645, '2026-07-27 ② 续跑 (F15 整篇 v2, 缓存全命中)'),
    '26_article_staleness.py': (6766, '2026-07-27 ② 续跑 (MinHash 三轨串行)'),
    # 🔵 stage 40 (2026-07-28 S8): 由"外推 39,600s"改为**首次完整实测 100,800s**
    # (2026-07-27 11:35:46 → 07-28 15:36:04, 父端自计, EXIT=0)。
    # ⚠ 旧的外推值低估了 **2.55×** —— 这是同一根因第三次复现 (stage 15 / 23 / 40):
    #   **被杀时按已完成比例外推会系统性低估**, 因为没跑到的往往正是最重的部分。
    #   新增实测行时请直接用父端 "执行成功（耗时 Ns）" 那一行, 不要自己按子步骤加总。
    '40_panel_export_main.py': (
        100800, '2026-07-28 ② 首次完整跑通 28.00h (orchestrator 父端自计; 旧行 39600 是被杀后的外推低估)'),
    '46_stata_export.py': (36, '2026-07-28 ② 全链 (35.32s 上取整)'),
    '51_falsification_test.py': (100, '2026-07-28 ② 全链 (99.79s 上取整)'),
}

#: 🔴 S11 (2026-07-29): **本表原先只覆盖 STAGES_MAIN, 16 个验证阶段一格没有** ——
#: 于是同一根因第 4 次从这个缺口漏出去: 入口③ 生产真跑时阶段 72 被 10,800s 强杀,
#: 73/74/75 连坐跳过, 整个评估验证管道判 ✗。补上验证侧实测。
MEASURED_VALIDATION_SECONDS = {
    '60_bank_fintech_threshold.py': (50, '2026-07-29 ③ 生产 (49.33s 上取整)'),
    '61_news_llms_human.py': (14, '2026-07-29 ③ 生产 (13.25s)'),
    '62_dedup_threshold_sensitivity.py': (9190, '2026-07-29 ③ 生产 (多阈值 LSH 扫描, 4,097,326 文档)'),
    '63_news_llms_evaluation.py': (5, '2026-07-29 ③ 生产 (4.5s)'),
    '64_tone_validation.py': (259, '2026-07-29 ③ 生产'),
    '65_radius_sensitivity.py': (1159, '2026-07-29 ③ 生产'),
    '66_entity_masking_test.py': (2, '2026-07-29 ③ 生产 (1.33s)'),
    '67_dict_coverage_audit.py': (66, '2026-07-29 ③ 生产'),
    '68_media_diversity.py': (93, '2026-07-29 ③ 生产'),
    '69_decay_sensitivity.py': (503, '2026-07-29 ③ 生产'),
    '70_prompt_sensitivity.py': (2, '2026-07-29 ③ 生产 (1.27s)'),
    '71_inter_track_kappa.py': (185, '2026-07-29 ③ 生产'),
    # ⚠ 72 号是**被杀时的下界**不是完成耗时。真实需求由真数据微基准实测得出:
    #   bootstrap 单次 754ms × 48 cell × 1000 = 10.05h;
    #   permutation 单次 774ms × 48 cell × 1000 = 10.32h ⟹ 串行 20.4h。
    #   S11 (上三角镜像 + 逐 cell 并行) 后期望 ≈1.3h, 但闸门按**串行兜底路径**定。
    '72_construct_orthogonality.py': (
        73440, '2026-07-29 真数据微基准实测串行需求 20.4h (旧 10800s 闸把它强杀; '
               'S11 并行后期望 ≈1.3h, 闸按 OOM 兜底的串行路径定)'),
}

#: 最小安全余量 (timeout / 实测)。3× 覆盖机器争用、语料增长、缓存冷启动。
MIN_MARGIN = 3.0

#: 72 号例外: 分母取的是**串行兜底**需求 (20.4h) 而非期望值 (1.3h), 再压 3× 会到 61h,
#: 属过度保守。按 1.47× 收 —— 这不是放宽判据, 而是分母口径不同 (期望值口径下余量是 23×)。
MARGIN_OVERRIDES = {'72_construct_orthogonality.py': 1.4}


def _spec(script):
    for s in STAGES_MAIN:
        if s.script == script:
            return s
    raise AssertionError(f'STAGES_MAIN 中找不到 {script}')


def _spec_validation(script):
    from news_process.core.dag import STAGES_VALIDATION
    for s in STAGES_VALIDATION:
        if s.script == script:
            return s
    raise AssertionError(f'STAGES_VALIDATION 中找不到 {script}')


@pytest.mark.parametrize('script', sorted(MEASURED_PRODUCTION_SECONDS))
def test_timeout_covers_measured_production_runtime(script):
    measured, src = MEASURED_PRODUCTION_SECONDS[script]
    spec = _spec(script)
    margin = spec.timeout / measured
    assert margin >= MIN_MARGIN, (
        f'{script}: timeout={spec.timeout}s 对生产实测 {measured}s ({src}) 仅 {margin:.2f}× 余量, '
        f'低于 {MIN_MARGIN}× 下限 —— stage 15 (2026-07-24) 与 stage 23 (2026-07-26) '
        f'都是这样被父端强杀的。请按实测重校, 勿调低本 gate。')


def test_no_main_stage_silently_inherits_default_timeout():
    """重阶段不得靠 StageSpec 默认值兜底 —— 两次强杀事故的共同根因就是"漏配显式超时"。

    判据: 凡已实测 >600s 的阶段, 其 timeout 必须**不等于**默认值 (即显式配过)。
    """
    from news_process.core.dag import StageSpec
    default = StageSpec.__dataclass_fields__['timeout'].default
    offenders = [
        s.script for s in STAGES_MAIN
        if s.timeout == default
        and MEASURED_PRODUCTION_SECONDS.get(s.script, (0, ''))[0] > 600
    ]
    assert not offenders, (
        f'以下重阶段仍在吃 StageSpec 默认 timeout={default}s (未显式配置): {offenders}')


def test_measured_table_scripts_all_exist_in_dag():
    """防表与 DAG 漂移: 表中每个 script 都必须仍在 STAGES_MAIN 里 (阶段重编号时会红)。"""
    scripts = {s.script for s in STAGES_MAIN}
    missing = sorted(set(MEASURED_PRODUCTION_SECONDS) - scripts)
    assert not missing, f'实测表引用了 STAGES_MAIN 中不存在的 script: {missing}'


# ════════════════════════════════════════════════════════════════════════════
# 验证侧 (STAGES_VALIDATION) —— S11 (2026-07-29) 补齐
# ════════════════════════════════════════════════════════════════════════════
# 本文件此前**只覆盖 STAGES_MAIN**, 16 个验证阶段一格没有。同一根因 (超时按估算/
# T=2 定, 从未按生产规模复核) 第 4 次复发就是从这个缺口漏出去的: 2026-07-29 入口③
# 生产真跑, 阶段 72 被 10,800s 强杀 → 73/74/75 连坐跳过 → 整个管道判 ✗。

@pytest.mark.parametrize('script', sorted(MEASURED_VALIDATION_SECONDS))
def test_validation_timeout_covers_measured_runtime(script):
    measured, src = MEASURED_VALIDATION_SECONDS[script]
    spec = _spec_validation(script)
    margin = spec.timeout / measured
    floor = MARGIN_OVERRIDES.get(script, MIN_MARGIN)
    assert margin >= floor, (
        f'{script}: timeout={spec.timeout}s 对生产实测 {measured}s ({src}) 仅 {margin:.2f}× 余量, '
        f'低于 {floor}× 下限 —— 阶段 72 (2026-07-29) 就是这样被强杀且连坐掉 73/74/75 的。'
        f'请按实测重校, 勿调低本 gate。')


def test_validation_table_scripts_all_exist_in_dag():
    from news_process.core.dag import STAGES_VALIDATION
    scripts = {s.script for s in STAGES_VALIDATION}
    missing = sorted(set(MEASURED_VALIDATION_SECONDS) - scripts)
    assert not missing, f'验证实测表引用了 STAGES_VALIDATION 中不存在的 script: {missing}'


def test_validation_table_covers_every_measured_stage():
    """凡在 2026-07-29 ③ 真跑里跑出过耗时的验证阶段, 都必须进表。

    73/74/75 因 72 号被杀而**从未在生产上跑过**, 故暂缺 —— 一旦补跑出实测值必须入表。
    """
    from news_process.core.dag import STAGES_VALIDATION
    known_unmeasured = {
        '73_lexical_discriminant_validity.py',
        '74_lm_discriminant_validity.py',
        '75_cross_media_alpha.py',
    }
    scripts = {s.script for s in STAGES_VALIDATION}
    gap = scripts - set(MEASURED_VALIDATION_SECONDS) - known_unmeasured
    assert not gap, (
        f'以下验证阶段既无实测也未登记为"未跑过": {sorted(gap)} —— '
        '要么补实测入表, 要么显式登记原因, 不得静默失守。')
