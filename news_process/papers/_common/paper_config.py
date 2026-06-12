"""news_process.papers._common.paper_config — PaperConfig + 路径解析.

每篇论文对应一份 ``PaperConfig``: 它把 *项目级* (``core.config.load_config()``
返回的全局 cfg) 和 *论文级* (``papers_assets/<paper_id>/{do,output,drafts}``)
两层路径桥接起来。论文代码包以 ``get_paper_config('paper_id')`` 拿到这份
record，无需关心 YAML 字段或绝对路径解析细节。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from news_process.core.config import load_config

# RR1-1: 11 paper id 白名单的单一可信源 (5 existing + 3 new
# + 3 provisional, 2026-06-01; 此处原为 hardcode 重复)。
from news_process.papers._common.paper_registry import PAPER_IDS_ALL as _PAPER_IDS_ALL

# ----------------------------------------------------------------------------
# 不可变记录 — 任何地方拿到 PaperConfig 后，可以信任其字段在生命周期内
# 不被改写。frozen=True 让我们能把 PaperConfig 用作 dict key / set 元素。
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class PaperConfig:
    """单篇论文的本地化配置.

    Attributes:
        paper_id:      论文标识，与 ``papers/<paper_id>/`` 包名一一对应
                       (snake_case)。
        project_root:  ``news_process/`` 目录绝对路径。
        panel_dir:     pipeline 阶段输出的 parquet 落盘目录
                       (默认 ``data/processed/``，Phase 8 重命名后)。
        output_dir:    本论文专属表/图最终输出目录
                       (``papers_assets/<paper_id>/output/``)。
        do_dir:        本论文专属 .do 脚本目录
                       (``papers_assets/<paper_id>/do/``)。
        drafts_dir:    本论文专属手稿目录
                       (``papers_assets/<paper_id>/drafts/``)。
        config:        ``load_config()`` 返回的整套项目 cfg
                       (用于读 ``filenames``、``panel_building`` 等其它键)。
    """

    paper_id: str
    project_root: Path
    panel_dir: Path
    output_dir: Path
    do_dir: Path
    drafts_dir: Path
    config: dict[str, Any] = field(repr=False)

    def panel_path(self, filename: str) -> Path:
        """快捷访问 ``panel_dir / filename``。"""
        return self.panel_dir / filename

    def asset(self, *parts: str) -> Path:
        """构造 ``papers_assets/<paper_id>/<parts>`` 路径 (不创建目录)。"""
        return self.output_dir.parent.joinpath(*parts)


# ----------------------------------------------------------------------------
# 路径解析工具
# ----------------------------------------------------------------------------


def _resolve_project_root(cfg: dict[str, Any]) -> Path:
    """从 cfg 推断 ``news_process/`` 绝对路径。

    优先用 ``cfg['paths']['output_dir']`` 已被 ``core.config.load_config``
    解析后的绝对路径回溯一级，确保和项目根目录一致。
    """
    output_dir = cfg.get('paths', {}).get('output_dir')
    if output_dir:
        return Path(output_dir).parent
    # 兜底: 从本文件位置向上回溯
    # paper_config.py -> _common/ -> papers/ -> news_process/
    return Path(__file__).resolve().parents[2]


def get_papers_assets_root(project_config: dict[str, Any] | None = None) -> Path:
    """解析 ``papers_assets_root``。

    优先级:
        1. cfg['paths']['papers_assets_root']  (Phase 3b 新增 key)
        2. <project_root>/papers_assets/        (fallback)
    """
    cfg = project_config if project_config is not None else load_config()
    explicit = cfg.get('paths', {}).get('papers_assets_root')
    if explicit:
        return Path(explicit)
    return _resolve_project_root(cfg) / 'papers_assets'


# 论文 ID 白名单 — 与 papers/<paper_id>/ 目录一一对应。
# Phase 3c/3d 实际建包后逐项启用；Phase 3e 的 run_paper.py CLI 也复用这份集合。
# Plan v2.x M0.2 + RR1-1 (Review-only audit): 单一可信源 = paper_registry.PAPER_IDS_ALL;
# 这里仅做 frozenset 包装供快速 ID 校验入口, 消除原双源 drift risk (历史 5→8 升级时
# 曾在两处分别 hardcode, 现统一从 paper_registry import; import 在文件顶部).
_VALID_PAPER_IDS: frozenset[str] = frozenset(_PAPER_IDS_ALL)


def is_valid_paper_id(paper_id: str) -> bool:
    """判断 paper_id 是否在白名单中。"""
    return paper_id in _VALID_PAPER_IDS


def get_paper_config(paper_id: str,
                     project_config: dict[str, Any] | None = None,
                     *,
                     strict: bool = True) -> PaperConfig:
    """构造 ``PaperConfig``.

    Args:
        paper_id:        论文标识 (snake_case，与 ``papers/<paper_id>/`` 一致)。
        project_config:  可选 — 已加载的项目 cfg，避免重复 YAML I/O。
        strict:          True (默认) 时校验 paper_id 是否在白名单中。
                         单元测试可传 ``strict=False`` 测试任意 ID。

    Returns:
        PaperConfig 不可变记录。

    Raises:
        ValueError: ``strict=True`` 且 paper_id 不在白名单中。
    """
    if strict and not is_valid_paper_id(paper_id):
        valid = sorted(_VALID_PAPER_IDS)
        raise ValueError(
            f"Unknown paper_id={paper_id!r}; valid choices: {valid}"
        )

    cfg = project_config if project_config is not None else load_config()
    paths = cfg.get('paths', {})
    project_root = _resolve_project_root(cfg)
    # Phase 8 (2026-05-04): 默认 fallback 路径已迁移到 ``data/processed/``
    panel_dir = Path(paths.get('output_dir', project_root / 'data' / 'processed'))
    assets_root = get_papers_assets_root(cfg)
    paper_root = assets_root / paper_id

    return PaperConfig(
        paper_id=paper_id,
        project_root=project_root,
        panel_dir=panel_dir,
        output_dir=paper_root / 'output',
        do_dir=paper_root / 'do',
        drafts_dir=paper_root / 'drafts',
        config=cfg,
    )


__all__ = [
    'PaperConfig',
    'get_paper_config',
    'get_papers_assets_root',
    'is_valid_paper_id',
]
