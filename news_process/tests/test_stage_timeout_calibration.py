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
    # 🔴 stage 40: 迄今**从未跑完**。21600s 处被强杀时才做到「相邻期连贯性」第 3 个算子。
    # 下方数字是按逐子步骤实测归因外推的**完成需求**, 非直接实测 —— 一旦真跑完须改成实测值。
    '40_panel_export_main.py': (
        39600, '2026-07-27 ② 逐子步骤归因外推 ≈11h (战略差异度 12,530s 实测 + 连贯性三轨 ≈5h 外推); 尚无完整实测'),
}

#: 最小安全余量 (timeout / 实测)。3× 覆盖机器争用、语料增长、缓存冷启动。
MIN_MARGIN = 3.0


def _spec(script):
    for s in STAGES_MAIN:
        if s.script == script:
            return s
    raise AssertionError(f'STAGES_MAIN 中找不到 {script}')


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
