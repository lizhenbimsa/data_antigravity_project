"""
run_pipeline_function.py — 新闻处理流水线调度器
================================================

功能：
    按顺序执行数据处理流水线的各个阶段，每阶段作为独立子进程运行。
    子进程隔离确保：
      1. 单阶段异常不影响其他阶段的已完成输出
      2. 各阶段的内存在进程退出后完全释放
      3. 全局状态（如 jieba 词典）不会在阶段间冲突

流水线架构::

    ┌─ 模块一：新闻预处理模块 ────────────────────────────┐
    │ 00_preprocessing                                           │
    └────────────────────────────────────────────────────────────┘
                      ↓
    ┌─ 模块二：新闻筛选模块 ──────────────────────────────┐
    │ 11_news_bank → 12_news_fintech → 14_fintech_intensity      │
    │ → 15_article_policy_alignment                              │
    └────────────────────────────────────────────────────────────┘
                      ↓
    ┌─ 模块三：新闻情感模块 ──────────────────────────────┐
    │ 21_tone_llms → 22_tone_words → 23_tone_berts               │
    │ → 24_herd_decay_processor                                  │
    └────────────────────────────────────────────────────────────┘
                      ↓
    ┌─ 模块五：面板数据构建 ──────────────────────────────┐
    │ 41→42→43→44→45 (面板数据构建)                              │
    └────────────────────────────────────────────────────────────┘
                      ↓
    ┌─ 模块六：伪造检验 ────────────────────────────────┐
    │ 51_falsification_test                                      │
    └────────────────────────────────────────────────────────────┘
                      ↓
                pipeline_summary

    情感分析的三个变体（words/BERT/LLM）由 config.yaml 中
    sentiment_analysis.enabled_methods 控制启用。

    模块四（评估验证）可单独运行：
      python run_pipeline_validation.py

使用方法::


    python run_pipeline_function.py
"""

import argparse
import os
import sys
import time

# Phase 1: 将项目父目录置于 sys.path, 使任意 cwd 下 ``import news_process`` 均可解析
# (子进程可能从其它工作目录启动)。
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(_HERE)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

# Phase 6a: utils.* → news_process.core.*
from news_process.core.config import load_config
from news_process.core.logging import setup_logging, log_memory_usage, log_stage_summary
from news_process.core.stage import run_stage
from news_process.core.locking import PipelineLock

# Phase 1: 自单一真源导入 DAG, 使本编排器与 core/dag.py 共用同一份阶段定义。
# STAGES 作为模块级常量暴露, 供 tests/integration/test_dag_consistency.py 做静态一致性校验。
from news_process.core.dag import STAGES_MAIN as STAGES, filter_enabled

# ============================================================================
# 配置与初始化
#
# 加载顺序:
#   1. load_config(): 解析 config.yaml + .env 环境变量
#   2. _generate_run_id(): 生成本次运行的唯一 ID 并写入 NEWS_PROCESS_RUN_ID 环境变量
#                          (Phase 1.5; 子进程通过环境变量继承, 共享同一个 logs/runs/<run_id>/)
#   3. setup_logging(): 创建带时间戳的日志文件 + 控制台输出
#                       (若 NEWS_PROCESS_RUN_ID 已设置, 路径解析为 <log_dir>/runs/<run_id>/<stage>.log;
#                        否则回退至 legacy <log_dir>/<stage>.log)
# 注意: 这是主调度器进程, 使用完整的文件+控制台双通道日志。
# 各阶段子进程会各自创建独立的日志文件 (相同 run_id 子目录内).
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "run_pipeline_function"


def _generate_run_id() -> str:
    """生成本次运行的唯一标识符, 并写入环境变量供子进程继承。

    格式: ``YYYYMMDDTHHMMSSZ-<hostname>-<pid>``, 例如
    ``20260503T231245Z-DESKTOP-1234``。

    若环境变量 ``NEWS_PROCESS_RUN_ID`` 已存在 (例如上游 CI 已注入),
    则原样保留; 否则生成新值。
    """
    import datetime as _dt
    import socket as _socket

    existing = os.environ.get("NEWS_PROCESS_RUN_ID")
    if existing:
        return existing

    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    host = _socket.gethostname().split(".")[0][:24]  # 截断过长 FQDN
    rid = f"{ts}-{host}-{os.getpid()}"
    os.environ["NEWS_PROCESS_RUN_ID"] = rid
    return rid


_RUN_ID = _generate_run_id()
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])
logger.info(f"NEWS_PROCESS_RUN_ID = {_RUN_ID}")


# 脚本所在目录(用于定位阶段脚本, 传给 run_stage() 的 base_dir 参数)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def _get_stage_output_files(stage_script: str) -> list:
    """Return the parquet outputs of ``stage_script``.

    Phase 2d: delegates to ``news_process.core.schemas.get_stage_outputs`` —
    the single-source registry — eliminating the prior
    duplicate-hardcoding hazard.  The legacy local mapping below is preserved
    only as a safety net for stage names not in the registry; in normal
    operation the registry returns first and the local map is unreachable.

    Phase 9 (plan m2): 把 ``CONFIG`` 传入 ``get_stage_outputs``, 使其按
    ``CONFIG['filenames'][filename_key]`` 解析用户自定义文件名;
    用户在 ``paths.yaml::filenames`` 中改名后预清理逻辑能自动跟进。
    """
    from news_process.core.schemas import get_stage_outputs as _registry_outputs
    files = _registry_outputs(stage_script, config=CONFIG)
    if files:
        return files

    # 历史兜底映射 (逐字保留 — Phase 2d 弃用期安全网)。
    stage_num = stage_script.split('_')[0]
    output_map = {
        '00': ['00_preprocessing.parquet'],
        '11': ['11_bank_news.parquet'],
        '12': ['12_fintech_news.parquet', '12_fintech_news_full.parquet'],
        '14': ['14_fintech_intensity.parquet'],
        '15': ['15_article_alignment.parquet'],
        '21': ['21_tone_llms.parquet', '21_tone_llms_full.parquet'],
        '22': ['22_words_tone.parquet'],
        '23': ['23_bert_tone.parquet'],
        '24': ['24_herd_decay.parquet'],
        '45': ['40_panel_yearly.parquet', '40_article_bank_level.parquet',
               '40_attn_index_year.parquet', '40_attn_index_province_year.parquet',
               '40_attn_index_city_year.parquet'],
        '51': ['51_panel_with_controls.parquet'],
    }
    files = output_map.get(stage_num, [])
    if not files and stage_num not in output_map:
        logger.debug(f"未知阶段 {stage_num}，无预定义输出文件")
    return files

def _parse_cli_args(argv: list[str] | None = None) -> argparse.Namespace:
    """解析主流水线 CLI 参数。

    Phase 9 (plan m1 方案 C): 引入 ``--skip-21-if-exists`` 单 stage 增量执行 flag,
    覆盖 80% "LLM 阶段已跑完, 想从下游重跑" 的实际痛点。完整 ``--resume-from`` /
    ``--skip-existing`` 通用方案延后至 plan m1 方案 A; ``config_hash`` 元数据级
    自动失效方案延后至 plan m1 方案 B。
    """
    parser = argparse.ArgumentParser(
        prog="run_pipeline_function",
        description="新闻处理主流水线 (模块一/二/三/五/六)",
    )
    parser.add_argument(
        "--skip-21-if-exists",
        action="store_true",
        help=(
            "若 stage 21 (LLM tone) 的输出 parquet 已存在 (含 _full 变体), "
            "跳过该阶段的预清理与子进程执行。常用场景: LLM 已花费 7200s 跑完, "
            "想增量重跑下游 stage 而不重新调用 LLM API。"
        ),
    )
    return parser.parse_args(argv)


def run_pipeline(args: argparse.Namespace | None = None):
    """执行完整的数据处理流水线。

    流程：
      1. 执行模块一：新闻预处理模块 (00)
      2. 执行模块二：新闻筛选模块 (11, 12, 14, 15)
      3. 执行模块三：新闻情感模块 (21, 22, 23, 视配置启动)
      4. 执行模块五：面板数据构建 (41-45)
      5. 执行模块六：伪造检验对照变量构建 (51)
      6. 生成管道执行摘要报告和耗时统计

    注：模块四（评估验证）已独立为 run_pipeline_validation.py，
        请单独执行：python run_pipeline_validation.py

    Args:
        args: argparse.Namespace, 由 ``_parse_cli_args`` 解析得到; 默认 None
              表示按默认全量执行 (向后兼容旧调用方式)。
    """
    if args is None:
        args = argparse.Namespace(skip_21_if_exists=False)

    pipeline_start = time.time()

    # ── 并发运行保护：确保同一时间只有一个管道实例运行 ──
    with PipelineLock(logger, CONFIG["paths"]["output_dir"]):
        logger.info("=" * 70)
        logger.info("===    新闻处理流水线 (News Processing Pipeline)    ===")
        logger.info("==" * 35)
        logger.info(f"Python: {sys.version}")
        logger.info(f"工作目录: {os.path.dirname(os.path.abspath(__file__))}")
        log_memory_usage(logger, "管道启动")

        # ── 流水线执行顺序(模块一至三 + 模块五至六) ──
        # 严格递进流转: 预处理 → 筛选 → 情感 → 面板构建 → 伪造检验
        # 每个阶段的输入依赖前一阶段的输出, 因此必须严格顺序执行。
        #
        # Phase 1 重构: 阶段定义已迁移至 news_process/core/dag.py:STAGES_MAIN,
        # 这里通过 filter_enabled() 按当前 config 的 enabled_when 谓词筛选,
        # 替代旧的 ``for method in enabled_methods: stages.append(...)`` 内联分支。

        enabled_methods = CONFIG.get('sentiment_analysis', {}).get('enabled_methods', [])
        logger.info(f"启用的情感分析方法: {enabled_methods}")

        # ── 数据流防护：清理未启用的情感分析阶段的残留输出 ──
        # 阶段 24 硬编码读取阶段 23 的输出，若 tone_berts 未启用但
        # 磁盘上残留旧的 23 输出文件，会导致阶段 24 静默读取过期数据。
        #
        # plan m5 修复: 改用 OUTPUT_REGISTRY 取阶段全部输出 (含 _full 变体),
        # 否则 21_tone_llms_full.parquet 会被遗漏 → 验证阶段 32/36/37/39
        # 静默读取上一次 LLM 的旧结果, 与本次配置不一致。
        _sentiment_method_to_script = {
            'tone_llms':  '21_tone_llms.py',
            'tone_words': '22_tone_words.py',
            'tone_berts': '23_tone_berts.py',
        }
        for method, _script in _sentiment_method_to_script.items():
            if method in enabled_methods:
                continue
            for filename in _get_stage_output_files(_script):
                stale_path = os.path.join(
                    CONFIG['paths']['output_dir'], filename)
                if os.path.exists(stale_path):
                    try:
                        os.remove(stale_path)
                        logger.info(f"  🧹 已清理未启用阶段的残留文件: {filename}")
                    except OSError as e:
                        logger.warning(f"  ⚠️ 清理残留文件失败: {filename} ({e})")

        # 无条件预清理阶段 24 自身输出，防止其失败后旧文件残留误导下游
        _stage24_output = os.path.join(
            CONFIG['paths']['output_dir'],
            CONFIG.get('filenames', {}).get(
                'output_24_herd_decay', '24_herd_decay.parquet'))
        if os.path.exists(_stage24_output):
            try:
                os.remove(_stage24_output)
                logger.info(f"  🧹 已预清理阶段 24 输出: {os.path.basename(_stage24_output)}")
            except OSError as e:
                logger.warning(f"  ⚠️ 预清理阶段 24 输出失败: {e}")

        # ── Phase 1: 从 core/dag.py 加载完整 DAG，按 enabled_when 谓词过滤 ──
        active_specs = filter_enabled(STAGES, CONFIG)
        # 兼容下方既有迭代结构: 每条 (script, name, timeout)。
        stages = [(s.script, s.name, s.timeout) for s in active_specs]

        logger.info(f"管道共 {len(stages)} 个阶段")
        for i, (script, name, _to) in enumerate(stages, 1):
            status = "待执行"
            logger.info(f"  {i}. {name} ({script}) [{status}]")

        # ── 逐阶段执行 ──
        # 速败 (fail-fast) 策略: 任一阶段失败则立即中止整条管道。
        # 避免在错误中间结果上继续执行, 降低级联错误难以溯源的风险。
        stage_timings = []
        all_success = True

        # Phase 1: 超时现取自 StageSpec (经 core/dag.py 单一真源)。
        # 重构前此处曾有本地 stage_timeouts 字典; 已上收为 StageSpec.timeout。

        for script, name, timeout in stages:
            # plan m1 方案 C: stage 21 增量跳过开关
            # 若 --skip-21-if-exists 启用, 且 stage 21 主输出 + _full 变体均已存在,
            # 跳过预清理与 run_stage 调用 (视作 success+0s, 与已 skip 的阶段同状态符号)。
            if (args.skip_21_if_exists and script == '21_tone_llms.py'):
                stage21_outputs = _get_stage_output_files(script)
                stage21_paths = [
                    os.path.join(CONFIG['paths']['output_dir'], f)
                    for f in stage21_outputs
                ]
                if stage21_paths and all(os.path.exists(p) for p in stage21_paths):
                    logger.info(
                        f"  ⏭ {name}: --skip-21-if-exists 命中, 已跳过 "
                        f"(检测到 {len(stage21_paths)} 个输出: "
                        f"{[os.path.basename(p) for p in stage21_paths]})"
                    )
                    stage_timings.append((name, 0.0, True))
                    continue
                else:
                    logger.info(
                        f"  --skip-21-if-exists 已启用, 但 {name} 输出不全, "
                        f"仍执行该阶段"
                    )

            # ── 数据流防护：预清理阶段输出，防止陈旧数据污染 ──
            # 在每个阶段执行前，清理其输出文件，确保不会读取上次失败残留的旧数据
            output_files = _get_stage_output_files(script)
            for filename in output_files:
                output_path = os.path.join(CONFIG['paths']['output_dir'], filename)
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                        logger.info(f"  🧹 预清理阶段输出: {filename}")
                    except OSError as e:
                        logger.warning(f"  ⚠️ 预清理失败: {filename} ({e})")

            success, elapsed = run_stage(
                script,
                name,
                logger,
                SCRIPT_DIR,
                timeout=timeout,
            )
            stage_timings.append((name, elapsed, success))

            if not success:
                all_success = False
                logger.error(f"管道在 {name} 处中断。后续阶段将跳过。")
                break

        # ── 生成管道摘要报告 ──
        if all_success:
            try:
                # Phase 6a: utils.pipeline_reporting → news_process.core.reporting
                from news_process.core.reporting import generate_pipeline_summary
                generate_pipeline_summary(CONFIG, logger)
            except Exception as e:
                logger.error(f"生成管道摘要报告失败: {e}")

        # ── 耗时统计 ──
        total_elapsed = time.time() - pipeline_start
        logger.info("\n" + "=" * 70)
        logger.info("===    管道执行耗时统计    ===")
        logger.info("=" * 70)
        logger.info(f"{'阶段':<30} {'耗时(秒)':>12} {'耗时占比':>10} {'状态':>6}")
        logger.info("-" * 70)

        # 耗时统计符号说明:
        #   ✓: 执行成功
        #   ✗: 执行失败
        #   ⏭: 已跳过(配置未启用或前置条件未满足)
        for name, elapsed, success in stage_timings:
            pct = (elapsed / total_elapsed * 100) if total_elapsed > 0 else 0
            status = "✓" if success else "✗"
            if elapsed == 0.0 and success:
                status = "⏭"  # 已跳过
            logger.info(f"  {name:<28} {elapsed:>10.1f}s {pct:>9.1f}% {status:>6}")

        logger.info("-" * 70)
        minutes = total_elapsed / 60
        hours = total_elapsed / 3600
        logger.info(f"  {'总计':<28} {total_elapsed:>10.1f}s ({minutes:.1f} 分钟 / {hours:.2f} 小时)")
        logger.info("=" * 70)

        log_memory_usage(logger, "管道完成")

        if all_success:
            logger.info("✓ 管道全部阶段执行成功！")
        else:
            logger.error("✗ 管道执行中断，请检查日志。")
            sys.exit(1)


if __name__ == "__main__":
    run_pipeline(_parse_cli_args())
