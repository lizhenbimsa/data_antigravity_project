#!/usr/bin/env python3
"""
generate_codebook.py - 生成完整的变量代码手册（Variable Codebook）

用法:
    python scripts/generate_codebook.py

输出 (WP1 2026-07-10 四格式落点迁移, 计划 §4):
    - data/processed/variable_codebook.xlsx   (可再生品, 不入 git)
    - data/processed/variable_codebook.csv    (可再生品, 不入 git)
    - build/codebook/variable_codebook.md     (权威载体, git 版本化)
    - build/codebook/variable_codebook.json   (权威载体, git 版本化)
    - build/codebook/field_coverage_report.json + longdesc_size_report.json (§9.2)

fix(omni-g-codebook-07, 2026-06-11): 面板源改为优先读 51_panel_with_controls
(stage 51 controls 超集, 含 nf_*/fintech_share 族), 缺失时回退 40_panel_yearly。
历史盘上产物实际生成自 51 面板而本入口只读 40 → 产物不可由文档化入口复现,
且 40/51 列集差异是 codebook 幻影行/漏登记的结构性根因。

WP1 (2026-07-10): 家族长文库 (config/codebook_longdesc/) 存在 (_index.json) 时
启用长文组装 (五段确定性组装, §1), 且 **51 缺失 = 拒跑** (§0: 长文生产/验收模式
禁在回退 40 宇宙 [缺 11 个 51-only 列] 下产出四格式成品); 库缺失时保持既有行为。
生产入口在生成前对全库做引文渲染物化回写 (§2.1, 幂等)。
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 sys.path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 添加父目录到 sys.path（用于导入 news_process）
parent_dir = project_root.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import logging

import pandas as pd

from news_process.core.config import load_config
from news_process.core.logging import sig4
from news_process.pipeline.panel import codebook_longdesc as _cl
from news_process.pipeline.panel.codebook import generate_codebook

# WP1 (2026-07-10) 落点常量 (模块级, 测试可 monkeypatch):
# md/json 权威载体 → build/codebook/ (git 版本化, gitignore 三行组合豁免);
# 家族长文库 → config/codebook_longdesc/ (存在 _index.json 即启用长文模式)。
_VERSIONED_CODEBOOK_DIR = str(project_root / 'build' / 'codebook')
_LONGDESC_DIR = _cl.default_longdesc_dir()

# 初始化配置和日志
CONFIG = load_config()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def _log_environment_and_config(panel_path: str, output_dir: str) -> None:
    """打印 ① 项目/环境信息 + ② 输入输出 + ③ 运行配置 + ④ 方法论依据 (日志富集, 2026-06-24)。

    目标 (用户要求"在日志文件中提供尽可能多的项目信息、运行期间信息和运行结果信息"):
    把"谁在跑、跑在什么环境、读哪份面板、写哪几种格式、按什么数据文档化规范生成"一次性
    落进日志, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 (golden-safe)。
    ④ 方法论引文仅 emit 经 Crossref 真值核验的条目, 含 DOI 可访问链接 (Gebru et al. 2021 CACM
    https://doi.org/10.1145/3458723; Arslan 2019 AMPPS https://doi.org/10.1177/2515245919838783),
    绝不伪造 DOI (playbook §4 铁律)。
    """
    try:
        import platform

        logger.info("  🧭 项目 / 环境信息")
        logger.info("     · 工具: generate_codebook (变量代码手册生成 CLI; 非 DAG 阶段, 文档化入口)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) v3.16.0")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        logger.info(f"     · pandas:   {getattr(pd, '__version__', '?')}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "纯 CPU 读 parquet → 写文档, 无 LLM·Embedding·网络·API ($0) → 逐位可复现")

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 输入面板: {panel_path}")
        # WP1 落点迁移 (§4): xlsx/csv 留 output_dir 可再生; md/json 权威载体入 git
        for _fmt, _dir, _name in (
            ('excel', output_dir, 'variable_codebook.xlsx'),
            ('csv', output_dir, 'variable_codebook.csv'),
            ('markdown', _VERSIONED_CODEBOOK_DIR, 'variable_codebook.md'),
            ('json', _VERSIONED_CODEBOOK_DIR, 'variable_codebook.json'),
        ):
            logger.info(f"     · 输出[{_fmt}]: {os.path.join(_dir, _name)}")

        logger.info("  ⚙ 运行配置")
        logger.info("     · 面板源优先级: 51_panel_with_controls (controls 超集) > 40_panel_yearly (回退)")
        logger.info("     · 输出格式: excel / csv / markdown / json (4 格式同源单遍生成)")
        logger.info("     · codebook 取消 is_core 区分 (2026-06-21): 所有列均为分析列, 无 IC 列数约束")

        logger.info("  📖 方法论依据 (数据文档化规范学术出处)")
        logger.info("     · 数据集文档化规范 (随数据集附带其动机/构成/采集/用途的标准化档案): "
                    "Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., "
                    "Daumé III, H., & Crawford, K. (2021). Datasheets for datasets. "
                    "Communications of the ACM, 64(12), 86-92. https://doi.org/10.1145/3458723")
        logger.info("       → 变量代码手册即面板的'数据表/datasheet': 逐列记录定义/取值/来源阶段, 支撑复现与再利用")
        logger.info("     · 可复现的自动化 codebook 生成 (从数据直接派生变量文档, 减少手工抄录误差): "
                    "Arslan, R. C. (2019). How to automatically document data with the codebook "
                    "package to facilitate data reuse. Advances in Methods and Practices in "
                    "Psychological Science, 2(2), 169-187. https://doi.org/10.1177/2515245919838783")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法信息打印失败 (不影响处理): {e}")


def main():
    """主函数"""
    import time
    _start = time.time()
    phase_durations: dict[str, float] = {}

    logger.info("=" * 72)
    logger.info("变量代码手册 (Variable Codebook) 生成工具 (Gebru 2021 CACM / Arslan 2019 AMPPS)")
    logger.info("=" * 72)
    logger.info(
        "【功能】把最终面板 (bank-year) 的每一列文档化成一份'变量字典': 列名、含义、取值范围、"
    )
    logger.info(
        "        来源阶段、标签等, 同时落 excel/csv/markdown/json 四种格式, 供论文复现包附录使用。"
    )
    logger.info(
        "【方法】读取面板 parquet (优先 51_panel_with_controls controls 超集, 缺失回退 40_panel_yearly),"
    )
    logger.info(
        "        逐列推断/查表生成元信息, 一遍式写出 4 种文档格式 (内容同源)。"
    )
    logger.info(
        "【判读】产物行数 = 面板列数; 若 codebook 行数与面板实际列数不符即提示幻影行/漏登记 (结构性根因)。"
    )
    logger.info(
        "【确定性】纯 CPU 读 parquet → 写文档, 无 LLM/Embedding/网络/API ($0); 同一面板输入 → 逐位可复现。"
    )

    # 读取面板数据
    # fix(omni-g-codebook-07, 2026-06-11): 优先 51_panel_with_controls (controls 超集,
    # 与历史盘上产物的真实祖先一致), 缺失时回退 40_panel_yearly 并显式告警。
    panel51_path = os.path.join(
        CONFIG['paths']['output_dir'],
        CONFIG['filenames'].get('output_51_panel_controls', '51_panel_with_controls.parquet')
    )
    panel40_path = os.path.join(
        CONFIG['paths']['output_dir'],
        CONFIG['filenames'].get('output_40_panel_yearly', '40_panel_yearly.parquet')
    )
    # WP1: 长文模式判定 = 家族长文库 _index.json 实存 (缺库 → 保持既有行为)
    _longdesc_on = os.path.exists(os.path.join(_LONGDESC_DIR, '_index.json'))
    if os.path.exists(panel51_path):
        panel_path = panel51_path
    elif os.path.exists(panel40_path):
        if _longdesc_on:
            # §0 fail-loud: 长文生产/验收模式下 51 缺失 = 拒跑 — 禁在回退 40 宇宙
            # (缺 11 个 51-only 列: nf_*/fintech_share 族) 下产出四格式成品
            logger.error(
                f"长文模式 (家族长文库实存: {_LONGDESC_DIR}) 下 51_panel_with_controls "
                f"缺失 ({panel51_path}) — §0 铁律拒跑, 禁回退 40 宇宙产出四格式成品; "
                "请先重生 stage 51 面板"
            )
            return 1
        panel_path = panel40_path
        logger.warning(
            "51_panel_with_controls 不存在, 回退 40_panel_yearly — "
            "codebook 将缺 stage 51 controls 族列 (nf_*/fintech_share 等)"
        )
    else:
        logger.error(f"面板数据文件不存在: {panel51_path} 与 {panel40_path}")
        logger.error("请先运行数据处理流程生成面板数据")
        return 1

    # WP1 §2.1: 生产入口在生成前对全库做引文渲染物化回写 (幂等; audit_dois 的
    # 机械核验域扫描对象 = 渲染尾节, 不物化则全量闸对长文库提取 0 条 "0 红旗"恒真)
    if _longdesc_on:
        _lib = _cl.load_library(_LONGDESC_DIR)
        if _lib is not None:
            _n_mat = _cl.materialize_all(_lib)
            logger.info(f"引文渲染物化回写: {_n_mat} 个家族尾节更新 (幂等, 0=已最新)")

    # 项目/环境信息 + 输入输出 + 运行配置 + 方法论依据 (日志富集 2026-06-24, 路径确定后打印)
    output_dir = CONFIG['paths']['output_dir']
    _log_environment_and_config(panel_path, output_dir)

    logger.info(f"读取面板数据: {panel_path}")
    _t = time.time()
    panel = pd.read_parquet(panel_path)
    phase_durations['①加载面板parquet'] = time.time() - _t
    logger.info(f"  面板维度: {len(panel):,d} 行 × {len(panel.columns):,d} 列")

    # 生成代码手册 (WP1: md/json 权威载体 → build/codebook/; 长文库显式注入,
    # 库缺失时 generate_codebook 内部逐列回退现状短描述 + 告警计数)
    _t = time.time()
    output_files = generate_codebook(
        panel=panel,
        output_dir=output_dir,
        formats=['excel', 'csv', 'markdown', 'json'],
        versioned_dir=_VERSIONED_CODEBOOK_DIR,
        longdesc_dir=_LONGDESC_DIR if _longdesc_on else None,
    )
    phase_durations['②生成codebook(4格式)'] = time.time() - _t

    # 输出结果
    logger.info("\n" + "=" * 72)
    logger.info("变量代码手册生成完成！")
    logger.info("=" * 72)
    for format_name, file_path in output_files.items():
        logger.info(f"  {format_name.upper()}: {file_path}")

    # ── ⏱ 阶段计时汇总 (墙钟秒, sig4; 纯日志, golden-safe) ──
    _total = time.time() - _start
    logger.info("  ⏱ 阶段计时 (墙钟秒)")
    for _phase, _dur in phase_durations.items():
        _share = _dur / _total if _total > 0 else 0.0
        logger.info(f"     · {_phase}: {sig4(_dur)}s (占比 {sig4(_share * 100)}%)")
    logger.info(f"     · 合计: {sig4(_total)}s")

    return 0


if __name__ == "__main__":
    sys.exit(main())
