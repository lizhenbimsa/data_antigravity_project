"""news_process/run_paper.py — 多论文统一调度入口 (Phase 3e).

把 ``papers/<paper_id>/analysis.main()`` 暴露成统一的 CLI 接口, 配合
``papers/_common/paper_config._VALID_PAPER_IDS`` 做严格白名单检查 (防止
任意路径反射攻击 / 拼写错误)。

CLI 用法
--------
    python news_process/run_paper.py <paper_id> [--stage pipeline|tables|figures|all]
                                                [--dry-run]
    python -m news_process.run_paper <paper_id> [...]

可选 paper_id (与 ``papers/<paper_id>/`` 一一对应):
    bank_fintech_tone   — 主线: 银行金融科技语调 → 银行行为
    benefit_society     — 衍生 1: 经营效益态度投影 (Jha-Liu-Manela 2026)
    brokerage_network   — 衍生 2: 信息经纪网络 (Han et al. 2024)
    llm_peer            — 衍生 3: LLM 同业 IV (Cao et al. 2025)
    strategic_diff      — 衍生 4: 战略差异度 (Guzman-Li 2023)

    --list              列出全部白名单 paper_id 及简介, 不执行其它动作。

设计约束
--------
- *白名单优先*: 只允许 ``papers._common.paper_config._VALID_PAPER_IDS``
   集合中的论文 ID, 阻止误用反射调用任意子模块。
- *零反射动态加载*: 用普通 ``importlib.import_module`` 而非
   ``importlib.util.spec_from_file_location``, 让导入路径完全可静态分析。
- *退出码契约*: 子论文 ``analysis.main()`` 返回 int 直接转 process exit code。
"""

from __future__ import annotations

import argparse
import importlib
import logging
import sys
from typing import Final

if __name__ == "__main__" and __package__ is None:
    # 让 ``python news_process/run_paper.py ...`` 能正确解析包导入 ——
    # 把 news_process/ 的父目录注入 sys.path 头部。
    import os as _os
    _project_parent = _os.path.dirname(
        _os.path.dirname(_os.path.abspath(__file__))
    )
    if _project_parent not in sys.path:
        sys.path.insert(0, _project_parent)

from news_process.papers._common.paper_config import (  # noqa: E402
    is_valid_paper_id,
    _VALID_PAPER_IDS,
)


_LOGGER = logging.getLogger('run_paper')


# Paper-id → 一行简介 (供 --list 显示)
_PAPER_SUMMARIES: Final[dict[str, str]] = {
    'bank_fintech_tone':
        '主线: 媒体银行金融科技语调 → 银行行为 (整条 pipeline 的产品化封装)',
    'benefit_society':
        '衍生 1: 经营效益态度投影 (Jha, Liu & Manela 2026, RFS §1.3.2)',
    'brokerage_network':
        '衍生 2: 信息经纪网络与企业表现 (Han, Jiang, Zhang & Zhu 2024)',
    'llm_peer':
        '衍生 3: LLM 生成同业竞争 IV (Cao, Li, Wang & Zhao 2025)',
    'strategic_diff':
        '衍生 4: 银行金融科技战略差异度 (Guzman-Li 2023; Hoberg-Phillips 2016)',
}


def _print_paper_list() -> None:
    """打印所有可调度论文。"""
    print("Available papers:\n")
    for pid in sorted(_VALID_PAPER_IDS):
        summary = _PAPER_SUMMARIES.get(pid, '(no summary)')
        print(f"  {pid:24s}  {summary}")
    print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='python -m news_process.run_paper',
        description='Multi-paper dispatcher — invoke a paper-specific analysis CLI.',
    )
    parser.add_argument(
        'paper_id', nargs='?',
        help='论文标识 (与 papers/<paper_id>/ 一一对应)。',
    )
    parser.add_argument(
        '--list', action='store_true', dest='list_papers',
        help='列出全部白名单 paper_id, 不执行其它动作。',
    )
    parser.add_argument(
        '--stage', choices=['pipeline', 'tables', 'figures', 'all'],
        default='all',
        help='转发给论文 analysis.main() 的 --stage 参数 (默认 all)。',
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='转发给论文 analysis.main() 的 --dry-run。',
    )
    args, unknown = parser.parse_known_args(argv)

    if args.list_papers:
        _print_paper_list()
        return 0

    if args.paper_id is None:
        parser.print_help()
        print("\nERROR: 必须提供 paper_id (或使用 --list 查看可选值)。",
              file=sys.stderr)
        return 2

    if not is_valid_paper_id(args.paper_id):
        valid = sorted(_VALID_PAPER_IDS)
        print(
            f"ERROR: 未知 paper_id={args.paper_id!r}. "
            f"白名单: {valid}\n请用 --list 查看可选值。",
            file=sys.stderr,
        )
        return 2

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(name)s] %(levelname)s %(message)s',
    )
    _LOGGER.info("Dispatching to news_process.papers.%s.analysis.main()",
                 args.paper_id)

    module_path = f"news_process.papers.{args.paper_id}.analysis"
    try:
        analysis_mod = importlib.import_module(module_path)
    except ImportError as e:
        _LOGGER.error("Failed to import %s: %s", module_path, e)
        return 1

    if not hasattr(analysis_mod, 'main'):
        _LOGGER.error(
            "%s 缺少 main() 入口; paper 包不符合 Phase 3 契约。",
            module_path,
        )
        return 1

    forwarded: list[str] = ['--stage', args.stage]
    if args.dry_run:
        forwarded.append('--dry-run')
    forwarded.extend(unknown)

    return int(analysis_mod.main(forwarded) or 0)


if __name__ == '__main__':
    sys.exit(main())
