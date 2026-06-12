"""news_process.papers._common.paper_registry — 11 paper spec.yaml 注册中心.

Plan v2.x §5.2 M0.2: 把 11 篇论文 (5 existing + 3 new + 3 provisional) 的 ``paper_spec.yaml``
集中加载并验证。下游 (analysis CLI / tables / figures / Stata template
substitution / replication packaging / paper_config 白名单) 通过这里的
``list_paper_ids()`` / ``get_spec(paper_id)`` 拿到结构化 spec。

设计原则:
- 单一可信源 = ``papers/<paper_id>/paper_spec.yaml`` 文件本身;
- registry 在导入时一次性扫描 + lazy 缓存, 不写盘;
- 验证 schema (per plan §5.2.3.bis required + optional 字段) 但不强制
  schema 完整 (R12-M01 schema 是 design contract, real specs 允许多态);
- 与 ``paper_config.py::_VALID_PAPER_IDS`` 协同 — registry 是 spec 来源,
  paper_config 是路径解析; registry 在 M0 G0 时 expand whitelist 到 8 paper。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore[import-untyped]
except ImportError as _exc:  # pragma: no cover
    raise ImportError(
        "paper_registry requires PyYAML (already in pyproject.toml dependencies)"
    ) from _exc


# ----------------------------------------------------------------------------
# 11 paper id 完整白名单 (5 existing + 3 new + 3 provisional;
# plan §3.3 + §B.1-B.4 + 2026-06-01 provisional 接线)
# ----------------------------------------------------------------------------

PAPER_IDS_EXISTING: tuple[str, ...] = (
    'bank_fintech_tone',   # P1 (retrofit per §B.1)
    'benefit_society',     # 衍生 1
    'brokerage_network',   # 衍生 2
    'llm_peer',            # 衍生 3
    'strategic_diff',      # 衍生 4
)

PAPER_IDS_NEW: tuple[str, ...] = (
    'bank_fintech_attention',   # P2 (per §B.2)
    'bank_fintech_substance',   # P3 (per §B.3)
    'bank_fintech_locus',       # P4 (per §B.4)
)

# Provisional 临时档 / onboarding 未完成的论文 (2026-06-01 接线)。
# 这 3 篇 paper_spec.yaml 已 frozen 且通过 REQUIRED_FIELDS + schema 校验, 故纳入
# PAPER_IDS_ALL 使其经 run_paper.py 可调度 (analysis.py 已建, 表/图为 Phase-3 契约
# 占位骨架)。它们刻意 *不* 进 PAPER_IDS_NEW — 因为 B-route NEW 契约 (test_papers_b_route)
# 还要求 en/zh manuscript + refs.bib + derivative_replication 注册 + Stata 四件套全集,
# 这些待 P5 / M5 / M7 完整 onboarding 后补齐。PROVISIONAL 这一层精确表达
# "可调度但尚未完成全部 B-route 交付物" 的状态, 避免谎称其为完整 NEW paper。
PAPER_IDS_PROVISIONAL: tuple[str, ...] = (
    'bank_fintech_collab',        # P5 (v3.4.0 立项; 缺 manuscript/refs.bib/derivative 注册)
    'bank_media_disagreement',    # 第 10 篇 (M0 立项; analysis/tables/figures 待 M5 填实)
    'bank_news_clarity',          # 第 11 篇 (M0 立项; analysis/tables/figures 待 M7 填实)
)

PAPER_IDS_ALL: tuple[str, ...] = (
    PAPER_IDS_EXISTING + PAPER_IDS_NEW + PAPER_IDS_PROVISIONAL
)


# schema 必填字段, 依 plan §5.2.3.bis。
# 按 RR1-2 设为 public (M0.3 test_paper_spec_schema 跨模块直接 import 此集合验证 schema)。
REQUIRED_FIELDS: frozenset[str] = frozenset({
    'paper_id',
    'spec_version',
    'status',
    'differentiation_claim',
    'outcome',
    'treatment',
    'controls',
    'identification',
    'event_studies',
    'targets',
    'sample',
    'audit_rounds_target_min',
})

# 旧私有名的向后兼容别名 (计划在 v3.0 plan major 删除)。
_REQUIRED_FIELDS = REQUIRED_FIELDS


@dataclass(frozen=True)
class PaperSpec:
    """单篇论文的结构化 spec (从 paper_spec.yaml 加载).

    Attributes:
        paper_id:    论文标识 (snake_case, 与 papers/<paper_id>/ 一致)
        spec_version: semver string (e.g. "2.0.0")
        status:      enum [existing, new, skeleton]
        spec_path:   yaml file 绝对路径 (用于 traceback)
        raw:         dict 形式的完整 spec (供下游随取随用)
    """

    paper_id: str
    spec_version: str
    status: str
    spec_path: Path
    raw: dict[str, Any] = field(repr=False)

    def get(self, key: str, default: Any = None) -> Any:
        """从 ``raw`` spec dict 取顶层字段 (dict.get 透传)。"""
        return self.raw.get(key, default)

    @property
    def differentiation_claim(self) -> str:
        """spec 的 ``differentiation_claim`` 字段（plan §5.2.3.bis 必填），缺失时返回空串。"""
        return self.raw.get('differentiation_claim', '')

    @property
    def primary_outlet(self) -> str:
        """spec 的 ``targets.primary_outlet`` 字段；若 targets 非 dict（yaml 缩进异常）安全 fallback 空串。"""
        # RR2-1: defensive — yaml schema 偶尔可能把 targets 误解析为 list (e.g. 缩进
        # 异常), .get() on list 会 raise AttributeError. 安全 fallback 返回空 str.
        targets = self.raw.get('targets')
        if not isinstance(targets, dict):
            return ''
        return str(targets.get('primary_outlet', '') or '')

    @property
    def event_study_ids(self) -> list[str]:
        """spec 的 ``event_studies`` 字段；非 list 时返回 ``[]``。"""
        ev = self.raw.get('event_studies') or []
        return list(ev) if isinstance(ev, list) else []


# ----------------------------------------------------------------------------
# 路径解析
# ----------------------------------------------------------------------------


def _papers_root() -> Path:
    """``news_process/papers/`` 绝对路径 (本文件向上两级)."""
    # paper_registry.py -> _common/ -> papers/
    return Path(__file__).resolve().parent.parent


def _spec_path_for(paper_id: str) -> Path:
    return _papers_root() / paper_id / 'paper_spec.yaml'


# ----------------------------------------------------------------------------
# 加载器 Loader (懒加载 + 模块级缓存)
# ----------------------------------------------------------------------------


_CACHE: dict[str, PaperSpec] = {}


def _load_one(paper_id: str) -> PaperSpec:
    if paper_id in _CACHE:
        return _CACHE[paper_id]

    spec_path = _spec_path_for(paper_id)
    if not spec_path.is_file():
        raise FileNotFoundError(
            f"paper_spec.yaml missing for {paper_id!r}: expected at {spec_path}"
        )

    with spec_path.open('r', encoding='utf-8') as fh:
        raw = yaml.safe_load(fh)

    if not isinstance(raw, dict):
        raise ValueError(
            f"paper_spec.yaml for {paper_id!r} must be a YAML mapping, "
            f"got {type(raw).__name__}"
        )

    # 轻量 schema 校验 (只查必填字段是否存在; 类型检查留给 M0.3 test)
    missing = REQUIRED_FIELDS - set(raw.keys())
    if missing:
        raise ValueError(
            f"paper_spec.yaml for {paper_id!r} missing required fields: "
            f"{sorted(missing)}; required = {sorted(_REQUIRED_FIELDS)}"
        )

    # paper_id 字段必须与目录名一致
    declared_id = raw.get('paper_id')
    if declared_id != paper_id:
        raise ValueError(
            f"paper_spec.yaml paper_id mismatch: "
            f"directory={paper_id!r} vs declared={declared_id!r}"
        )

    # 2026-06-01: 接入 paper_spec_schema 轻量校验 (原为纯文档引用的 sleeping asset)。
    # validate_paper_spec 校验 v3.7.4 title_robustness.* 字段; remove-title-track 后对
    # 当前 8+3 spec 恒返回 [] (字段已移除 → no-op), 但保留为未来字段的防御性门控。
    # 非致命: 仅 logger.warning, 不 raise (schema 是 design contract, real specs 允许多态;
    # 见 RR1-2 / R12-M01)。
    from news_process.papers._common.paper_spec_schema import validate_paper_spec
    _schema_warnings = validate_paper_spec(raw)
    if _schema_warnings:
        import logging
        logging.getLogger(__name__).warning(
            "paper_spec.yaml %r schema 校验警告 (非致命): %s",
            paper_id, _schema_warnings,
        )

    spec = PaperSpec(
        paper_id=paper_id,
        spec_version=str(raw['spec_version']),
        status=str(raw['status']),
        spec_path=spec_path,
        raw=raw,
    )
    _CACHE[paper_id] = spec
    return spec


def list_paper_ids() -> tuple[str, ...]:
    """返回 11 paper id 元组 (existing 5 + new 3 + provisional 3, order preserved)."""
    return PAPER_IDS_ALL


def get_spec(paper_id: str) -> PaperSpec:
    """加载 + 验证单篇 paper_spec.yaml; 缓存命中后续调用零开销."""
    if paper_id not in PAPER_IDS_ALL:
        raise ValueError(
            f"Unknown paper_id={paper_id!r}; "
            f"valid choices: {sorted(PAPER_IDS_ALL)}"
        )
    return _load_one(paper_id)


def load_all_specs() -> dict[str, PaperSpec]:
    """加载全部 11 paper specs (5 existing + 3 new + 3 provisional)."""
    return {pid: get_spec(pid) for pid in PAPER_IDS_ALL}


def clear_cache() -> None:
    """测试场景: 强制重新加载 spec yaml."""
    _CACHE.clear()


# ----------------------------------------------------------------------------
# 公开 API
# ----------------------------------------------------------------------------


__all__ = [
    'PAPER_IDS_ALL',
    'PAPER_IDS_EXISTING',
    'PAPER_IDS_NEW',
    'PAPER_IDS_PROVISIONAL',
    'PaperSpec',
    'REQUIRED_FIELDS',
    'clear_cache',
    'get_spec',
    'list_paper_ids',
    'load_all_specs',
]
