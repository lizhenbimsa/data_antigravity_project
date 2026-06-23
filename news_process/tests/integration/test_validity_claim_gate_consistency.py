"""tests/integration/test_validity_claim_gate_consistency.py

WS-E (R-P0-2 + R3-01): per-dimension `validity_claim_gate` 的**可机械执行**护栏,
把 manuscript 级效度声明门从纸面变 T=2 可跑回归。复用 paper_registry 加载 spec。

规则:
  - 对每篇有 `validation:` 块的 spec, 读 evidence_status;
  - 若 == 'pending_T18_human_annotation': 断言其自由文本声称字段
    (differentiation_claim) 不含越权 validity 短语 (防 evidence pending 却宣称已验证);
  - per-dim 锚: validity_claim_gate.requires_real_human_kappa_for == 该篇主测度维度
    (防 tone κ 越权解锁三创新维);
  - manuscript 守卫**条件激活**: 仅当 paper 目录出现 manuscript 文件时才扫正文,
    缺席则 skip-with-reason (显式可见, 非永真, 杜绝护栏本身静默漂移);
  - 无 validation 块的 spec → skip-with-reason。
"""
from __future__ import annotations

import os
import sys

import pytest
import yaml

_PROJECT_PARENT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.papers._common.paper_registry import PAPER_IDS_ALL  # noqa: E402

# paper_id → 该篇主测度维度 (validity_claim_gate 须绑此维, 不可跨维解锁)
_PAPER_DIM = {
    'bank_fintech_locus': 'locus',
    'bank_fintech_collab': 'collab',
    'bank_fintech_substance': 'substantiveness',
    'bank_fintech_tone': 'tone',
}

# evidence pending 时正文/声称字段禁出现的越权短语 (大小写不敏感)
_OVERCLAIM_PHRASES = (
    'criterion validity',
    'construct validity established',
    'validated against human',
    '效标效度(已建立)',
    '构念效度成立',
)


def _spec_dir(paper_id: str):
    return os.path.join(_PROJECT_PARENT, 'news_process', 'papers', paper_id)


def _load_raw(paper_id: str):
    p = os.path.join(_spec_dir(paper_id), 'paper_spec.yaml')
    if not os.path.isfile(p):
        return None
    with open(p, encoding='utf-8') as fh:
        return yaml.safe_load(fh)


@pytest.mark.parametrize('paper_id', sorted(PAPER_IDS_ALL))
def test_validity_claim_gate_consistency(paper_id):
    raw = _load_raw(paper_id)
    if not raw or 'validation' not in raw:
        pytest.skip(f"{paper_id}: 无 validation 块 (greenfield, 未承诺效度门)")

    v = raw['validation']
    evidence_status = v.get('evidence_status')

    # per-dim 锚: 门必须绑该篇主测度维度
    gate = v.get('validity_claim_gate', {})
    bound_dim = gate.get('requires_real_human_kappa_for')
    expected_dim = _PAPER_DIM.get(paper_id)
    if expected_dim is not None:
        assert bound_dim == expected_dim, (
            f"{paper_id}: validity_claim_gate 绑定维度 {bound_dim!r} != "
            f"该篇主测度维度 {expected_dim!r} (防跨维越权解锁)")

    # evidence pending → 声称字段不得出现越权 validity 短语。
    # R9b-F1: 用 startswith('pending') 覆盖两种状态值 (pending_T18_human_annotation /
    # pending_human_annotation = tone 现盘可启动语义), 防 tone 越权守卫被静默架空。
    is_pending = str(evidence_status or '').startswith('pending')
    if is_pending:
        claim_text = str(raw.get('differentiation_claim', '')).lower()
        for phrase in _OVERCLAIM_PHRASES:
            assert phrase.lower() not in claim_text, (
                f"{paper_id}: evidence pending 却在 differentiation_claim 出现"
                f"越权短语 {phrase!r} (criterion/construct validity 须有真 κ 方可声称)")

    # manuscript 守卫: 条件激活 (有正文文件才扫), 否则显式 skip (非永真)
    manuscript_found = []
    for root, _dirs, files in os.walk(_spec_dir(paper_id)):
        for f in files:
            if f.endswith('.tex') or f.startswith('manuscript'):
                manuscript_found.append(os.path.join(root, f))
    if not manuscript_found:
        pytest.skip(f"{paper_id}: 无 manuscript 文件 (onboarding 后激活正文越权扫描)")
    # R9b-F3 (落实计划 §115): manuscript 存在 ⟹ evidence_status 不得仍 pending
    # (有正文却仍标 pending = 状态矛盾)。
    assert not is_pending, (
        f"{paper_id}: manuscript 已就绪却仍 evidence_status={evidence_status!r} pending "
        f"(状态矛盾, 计划 §115)")
    for mpath in manuscript_found:
        try:
            txt = open(mpath, encoding='utf-8', errors='ignore').read().lower()
        except OSError:
            continue
        for phrase in _OVERCLAIM_PHRASES:
            assert phrase.lower() not in txt, (
                f"{paper_id}: 正文出现越权短语 {phrase!r}")
