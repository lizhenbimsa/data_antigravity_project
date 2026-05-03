"""news_process.papers.bank_fintech_tone.dag — 主线论文 DAG.

设计原则 (Phase 3c)
-------------------
- *单源约束*: ``STAGES`` 必须由 ``core.dag.STAGES_MAIN`` 派生, 不复制定义。
   每个 StageSpec 元素都是 ``STAGES_MAIN`` 中对应对象的 *identity-equal*
   引用 (``is`` 关系), 这样 ``tests/integration/test_papers_dag_consistency``
   能验证子集关系与谓词共享。
- *主线特例*: bank_fintech_tone 是项目主线, 其 STAGES 当前等同于
   ``STAGES_MAIN`` 全集 (即"主管线 = 主论文")。Phase 3d 衍生论文会按
   名字过滤切片更窄的子集。
- *验收门槛*: 后续 Phase 3 任意阶段 *不允许* 在论文 DAG 与 ``STAGES_MAIN``
   之间出现 *谓词不一致* — 该不变式由 dag-consistency 测试守护。
"""

from __future__ import annotations

from news_process.core.dag import STAGES_MAIN, StageSpec

# 主线论文复用全套 main pipeline.  保持 list 而非引用 STAGES_MAIN 本身,
# 是为了让"论文 DAG"与"项目 DAG"在语义上独立 (论文未来若加专属阶段,
# 直接 append 即可), 但每个元素仍保持 identity-equal.
STAGES: list[StageSpec] = list(STAGES_MAIN)


__all__ = ['STAGES']
