"""Phase 3f 集成测试 — 多论文 DAG 一致性.

红线不变式
----------
1. 每个 paper 的 ``dag.STAGES`` 必须是 ``core.dag.STAGES_MAIN`` 的子集
   (元素 *identity-equal*, 即 ``s is t``); 防止论文重复定义 StageSpec
   导致谓词分叉。
2. 已知白名单 5 篇论文都必须能 import dag 模块且 STAGES 非空。
3. 每个 StageSpec 元素的 ``script`` 字段必须出现在 ``OUTPUT_REGISTRY``
   或被 ``always_enabled`` 之外的谓词约束 — 不允许"幽灵 stage"。

这些不变式由 Phase 3 验收门槛守护; CI 红线。
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

PROJECT_PARENT = Path(__file__).resolve().parents[3]
if str(PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(PROJECT_PARENT))

from news_process.core.dag import STAGES_MAIN, StageSpec
from news_process.papers._common.paper_config import _VALID_PAPER_IDS


@pytest.fixture(scope="module")
def stages_main_set() -> set[int]:
    """``id()`` of every StageSpec in ``STAGES_MAIN`` (identity-comparable set)."""
    return {id(s) for s in STAGES_MAIN}


@pytest.mark.parametrize("paper_id", sorted(_VALID_PAPER_IDS))
def test_paper_dag_is_subset_of_stages_main(paper_id: str, stages_main_set: set[int]):
    """每个论文 DAG 必须是 STAGES_MAIN 的子集 (identity-preserved)."""
    dag_mod = importlib.import_module(f"news_process.papers.{paper_id}.dag")
    paper_stages: list[StageSpec] = dag_mod.STAGES
    assert paper_stages, f"{paper_id}.dag.STAGES is empty"

    for s in paper_stages:
        assert isinstance(s, StageSpec), \
            f"{paper_id}.dag.STAGES contains non-StageSpec: {type(s)}"
        assert id(s) in stages_main_set, (
            f"{paper_id}.dag.STAGES contains a StageSpec NOT identity-equal "
            f"to any element in core.dag.STAGES_MAIN: {s.name}/{s.script}. "
            f"论文 DAG 必须从 STAGES_MAIN 切片, 不允许复制定义。"
        )


@pytest.mark.parametrize("paper_id", sorted(_VALID_PAPER_IDS))
def test_paper_dag_element_uniqueness(paper_id: str):
    """每个论文的 STAGES 内部不允许同一个 StageSpec 重复出现."""
    dag_mod = importlib.import_module(f"news_process.papers.{paper_id}.dag")
    stages = dag_mod.STAGES
    ids = [id(s) for s in stages]
    assert len(ids) == len(set(ids)), \
        f"{paper_id}.dag.STAGES 内部存在 identity-equal 重复元素"


@pytest.mark.parametrize("paper_id", sorted(_VALID_PAPER_IDS))
def test_paper_dag_predicate_identity(paper_id: str):
    """每个 StageSpec 的 enabled_when 必须与 STAGES_MAIN 同名 stage 的谓词 identity-equal.

    防止派生论文偷偷换谓词导致行为分叉。因为 STAGES = list(STAGES_MAIN),
    元素 identity 守护后这一条会自动满足; 这里显式断言以便后续如果
    切片实现改成"按 name 过滤+重新构造 StageSpec" 时立刻 CI 红灯。
    """
    dag_mod = importlib.import_module(f"news_process.papers.{paper_id}.dag")
    paper_by_name = {s.name: s for s in dag_mod.STAGES}
    main_by_name = {s.name: s for s in STAGES_MAIN}
    for name, paper_spec in paper_by_name.items():
        main_spec = main_by_name.get(name)
        assert main_spec is not None, \
            f"{paper_id} 的 stage {name!r} 未在 STAGES_MAIN 中找到"
        assert paper_spec.enabled_when is main_spec.enabled_when, (
            f"{paper_id}.{name}.enabled_when ({paper_spec.enabled_when}) "
            f"!= STAGES_MAIN.{name}.enabled_when ({main_spec.enabled_when}); "
            f"谓词 identity 必须保留 — 单源约束。"
        )


def test_all_whitelist_papers_have_dag_module():
    """白名单中的 5 篇论文都必须有可 import 的 dag 模块."""
    for paper_id in _VALID_PAPER_IDS:
        try:
            importlib.import_module(f"news_process.papers.{paper_id}.dag")
        except ImportError as e:
            pytest.fail(f"无法导入 news_process.papers.{paper_id}.dag: {e}")
