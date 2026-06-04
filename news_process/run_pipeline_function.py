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
    │ 11_news_bank → 12_news_fintech → 13_materialize_ctx        │
    │ → 14_fintech_intensity → 15_article_policy_alignment       │
    │ → 19_executive_ner                                         │
    └────────────────────────────────────────────────────────────┘
                      ↓
    ┌─ 模块三：新闻情感模块 ──────────────────────────────┐
    │ 21_tone_llms → 22_tone_words → 23_tone_berts               │
    │ → 24_herd_decay_processor                                  │
    └────────────────────────────────────────────────────────────┘
                      ↓
    ┌─ 模块五：面板数据构建 ──────────────────────────────┐
    │ 45_panel_export_main (内含 41-44) → 46_stata_export →      │
    │ 49_risk_taking_outcomes                                    │
    └────────────────────────────────────────────────────────────┘
                      ↓
    ┌─ 模块六：伪造检验 ────────────────────────────────┐
    │ 51_falsification_test                                      │
    └────────────────────────────────────────────────────────────┘
                      ↓
                pipeline_summary

    情感分析的三个变体（words/BERT/LLM）由 config/sentiment.yaml 中
    sentiment_analysis.enabled_methods 控制启用。
    文本嵌入与新颖度 (D 组: 30a_article_sbert / 17_article_topic /
    18_article_staleness) 在情感模块后、面板构建前执行。

    注：本图为高层概览；权威阶段清单以 core/dag.py::STAGES_MAIN 为准。

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
from news_process.core.dag import (
    METHOD_TO_PREDICATE,
    filter_enabled,
    get_script_for_method,
)

# Phase 1: 自单一真源导入 DAG, 使本编排器与 core/dag.py 共用同一份阶段定义。
# STAGES 作为模块级常量暴露, 供 tests/integration/test_dag_consistency.py 做静态一致性校验。
# v3 / Fix 2: METHOD_TO_PREDICATE / get_script_for_method 由 dag.py 单源维护,
# orchestrator 仅消费 (取代历史的本地 _sentiment_method_to_script 字典).
from news_process.core.dag import (
    STAGES_MAIN as STAGES,
)
from news_process.core.locking import PipelineLock
from news_process.core.logging import log_memory_usage, setup_logging
from news_process.core.stage import run_stage

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
    """生成本次运行 ID (委托给 core.run_id.generate_run_id)。"""
    from news_process.core.run_id import generate_run_id
    return generate_run_id()


_RUN_ID = _generate_run_id()
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])
logger.info(f"NEWS_PROCESS_RUN_ID = {_RUN_ID}")


# 脚本所在目录(用于定位阶段脚本, 传给 run_stage() 的 base_dir 参数)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def _get_stage_output_files(stage_script: str) -> list:
    """Return the parquet outputs of ``stage_script``.

    OUTPUT_REGISTRY 是单一真值 (Phase 2d 起 + Phase 8 baseline 后).
    Phase 9d 删除历史兜底 dict — 任何 stage 缺登记直接返回空列表.
    v3 / Fix 4: 进一步引入 EXPECTED_NO_OUTPUT_STAGES 显式集合, 区分
    "故意不产 parquet" (validation/audit 等) 与 "忘了登记的真 bug":
      - stage 在 OUTPUT_REGISTRY 中  → 返回登记的文件名列表 (含 _full 变体)
      - stage 在 EXPECTED_NO_OUTPUT_STAGES 中 → 返回空列表 + debug log
      - 二者都不在                      → raise RuntimeError (fail-fast)

    新的 STAGES_MAIN ↔ OUTPUT_REGISTRY 一致性由
    ``tests/integration/test_dag_consistency.py::
    test_stages_main_all_registered_in_output_registry`` 永久守护; v3 又
    新增 ``test_validation_stages_explicitly_marked_no_output`` 守住
    STAGES_VALIDATION ↔ (OUTPUT_REGISTRY ∪ EXPECTED_NO_OUTPUT_STAGES).

    config 传入 ``get_stage_outputs`` 解析用户自定义文件名;
    ``paths.yaml::filenames`` 改名后预清理逻辑自动跟进.
    """
    from news_process.core.schemas import (
        EXPECTED_NO_OUTPUT_STAGES,
        OUTPUT_REGISTRY,
    )
    from news_process.core.schemas import (
        get_stage_outputs as _registry_outputs,
    )
    files = _registry_outputs(stage_script, config=CONFIG)
    if not files:
        if stage_script in EXPECTED_NO_OUTPUT_STAGES:
            logger.debug(
                f"{stage_script} 显式无 parquet 输出 (validation/audit), "
                f"跳过预清理"
            )
        elif stage_script not in OUTPUT_REGISTRY:
            raise RuntimeError(
                f"阶段 {stage_script} 既不在 OUTPUT_REGISTRY 也不在 "
                f"EXPECTED_NO_OUTPUT_STAGES; 请在 news_process/core/schemas.py "
                f"明确登记 (产 parquet) 或加入 EXPECTED_NO_OUTPUT_STAGES (不产)。"
            )
    return files


_STAGE21_UPSTREAM_FINGERPRINT_COLUMNS = (
    'docid',
    'pubcode',
    'target_bank',
    'co_mentioned_banks',
    '日期',
    '标题',
    '内容',
    'fintech_intensity_score',
    'intensity_verified',
)

_STAGE21_FILTERED_FINGERPRINT_COLUMNS = (
    'docid',
    'target_bank',
    '日期',
    '标题',
    '内容',
)

# v3.2.0 双轨独立标签 — 下游 stage 45 (panel build) 强依赖. 若 --skip-21-if-exists
# 命中旧 (v3.1.x) 产物且这些列缺失, 下游会抛 KeyError. 见 CLAUDE.md / CHANGELOG.md
# v3.2.0 节: innovation_locus_{full,ctx} + innovation_substantiveness_{full,ctx}.
_STAGE21_REQUIRED_OUTPUT_COLUMNS = (
    'innovation_locus_full',
    'innovation_locus_ctx',
    'innovation_substantiveness_full',
    'innovation_substantiveness_ctx',
)


def _fingerprint_dataframe_rows(df, columns: tuple[str, ...]) -> tuple[int, str]:
    """Return a deterministic row-count + content digest for selected columns."""
    import hashlib

    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"missing columns for fingerprint: {missing}")

    key_df = df.loc[:, list(columns)].copy()
    key_df = key_df.astype("string").fillna("<NA>")
    key_df = key_df.sort_values(list(columns), kind="mergesort").reset_index(drop=True)
    payload = key_df.to_csv(index=False, lineterminator="\n").encode("utf-8")
    return len(key_df), hashlib.sha256(payload).hexdigest()


def _stage21_skip_is_compatible(stage21_outputs: list[str]) -> tuple[bool, str]:
    """Check whether existing stage 21 outputs match the current stage 14 input.

    ``--skip-21-if-exists`` is only safe if the full stage-21 output was produced
    from the current stage-14 parquet. Otherwise downstream stages would silently
    consume stale LLM labels after upstream stages were regenerated.
    """
    import pandas as pd

    if len(stage21_outputs) < 2:
        return False, "stage 21 output registry is incomplete"

    output_dir = CONFIG['paths']['output_dir']
    main_path = os.path.join(output_dir, stage21_outputs[0])
    full_path = os.path.join(output_dir, stage21_outputs[1])
    missing_outputs = [
        path for path in (main_path, full_path)
        if not os.path.exists(path)
    ]
    if missing_outputs:
        return False, f"missing stage 21 outputs: {missing_outputs}"

    upstream_name = CONFIG.get('filenames', {}).get(
        'output_14_fintech_intensity',
        '14_fintech_intensity.parquet',
    )
    upstream_path = os.path.join(output_dir, upstream_name)
    if not os.path.exists(upstream_path):
        return False, f"stage 21 upstream is missing: {upstream_path}"

    try:
        upstream_df = pd.read_parquet(
            upstream_path,
            columns=list(_STAGE21_UPSTREAM_FINGERPRINT_COLUMNS),
        )
        full_input_df = pd.read_parquet(
            full_path,
            columns=list(_STAGE21_UPSTREAM_FINGERPRINT_COLUMNS),
        )
        upstream_rows, upstream_digest = _fingerprint_dataframe_rows(
            upstream_df,
            _STAGE21_UPSTREAM_FINGERPRINT_COLUMNS,
        )
        full_rows, full_digest = _fingerprint_dataframe_rows(
            full_input_df,
            _STAGE21_UPSTREAM_FINGERPRINT_COLUMNS,
        )
    except Exception as exc:
        return False, f"failed to compare stage 14 and stage 21 full output: {exc}"

    if upstream_rows != full_rows:
        return False, (
            f"stage 14 row count ({upstream_rows}) != "
            f"21_tone_llms_full row count ({full_rows})"
        )
    if upstream_digest != full_digest:
        return False, "stage 14 fingerprint differs from 21_tone_llms_full"

    try:
        # O2.5 修复 (2026-05-25): orchestrator skip-check 与实际 stage 21 OR-filter
        # 语义对齐. 自 v3.2.0 R1-A 致命修复 (tone_llms.py:1744-1746) 起,
        # stage 21 main parquet filter = (verified_full == True) | (verified_ctx == True),
        # 让 ctx 轨独立可作 main spec (Hassan 2019 QJE entity-proximity). 旧 skip-check
        # 用 AND-only (verified_full=True) 会把 ctx-only 行排除 → fingerprint mismatch
        # (实测 ctx-only 15 行覆盖 2 cohort 银行 → n_banks 82 vs 84 test fail).
        full_cols = list(_STAGE21_FILTERED_FINGERPRINT_COLUMNS) + [
            'llm_verified_full', 'llm_verified_ctx',
        ]
        full_verify_df = pd.read_parquet(full_path, columns=full_cols)
        expected_main_df = full_verify_df[
            (full_verify_df['llm_verified_full'] == True)  # noqa: E712 - pandas boolean mask
            | (full_verify_df['llm_verified_ctx'] == True)
        ].drop(columns=['llm_verified_full', 'llm_verified_ctx'])
        main_df = pd.read_parquet(
            main_path,
            columns=list(_STAGE21_FILTERED_FINGERPRINT_COLUMNS),
        )
        expected_rows, expected_digest = _fingerprint_dataframe_rows(
            expected_main_df,
            _STAGE21_FILTERED_FINGERPRINT_COLUMNS,
        )
        main_rows, main_digest = _fingerprint_dataframe_rows(
            main_df,
            _STAGE21_FILTERED_FINGERPRINT_COLUMNS,
        )
    except Exception as exc:
        return False, f"failed to compare stage 21 filtered and full outputs: {exc}"

    if expected_rows != main_rows:
        return False, (
            f"21_tone_llms row count ({main_rows}) != verified rows in "
            f"21_tone_llms_full ({expected_rows})"
        )
    if expected_digest != main_digest:
        return False, "21_tone_llms does not match verified rows in 21_tone_llms_full"

    # v3.2.0 schema 漂移防护: fingerprint 一致也未必意味着旧产物含 v3.2.0 双轨列.
    # 若任一必需列缺失, reject skip → 触发 stage 21 重跑刷新 schema.
    try:
        import pyarrow.parquet as pq
        full_schema_names = set(pq.read_schema(full_path).names)
        main_schema_names = set(pq.read_schema(main_path).names)
    except Exception as exc:
        return False, f"failed to read stage 21 parquet schema: {exc}"

    missing_required = [
        col for col in _STAGE21_REQUIRED_OUTPUT_COLUMNS
        if col not in full_schema_names or col not in main_schema_names
    ]
    if missing_required:
        return False, (
            f"stage 21 outputs missing v3.2.0 required columns: {missing_required}; "
            f"prompt/aggregator schema has changed, must re-run"
        )

    return True, f"stage 21 outputs match current stage 14 input ({upstream_rows} rows)"


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
        #
        # v3 / Fix 2: method → script 映射统一从 dag.METHOD_TO_PREDICATE
        # + get_script_for_method() 反推, 不再在本文件内重复维护字典.
        for method in METHOD_TO_PREDICATE:
            if method in enabled_methods:
                continue
            _script = get_script_for_method(method)
            if _script is None:
                # 防御性: METHOD_TO_PREDICATE 与 STAGES_MAIN 漂移由
                # test_method_to_predicate_covers_sentiment_specs 守护;
                # 这里仅做 best-effort 跳过, 避免单点失败阻塞清理流程.
                logger.warning(
                    f"  ⚠️ method '{method}' 在 dag.METHOD_TO_PREDICATE 已登记 "
                    f"但 STAGES_MAIN 中找不到对应 stage; 跳过陈旧文件清理"
                )
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

        # Plan P1-4: stage 24 现已通过 enabled_when=berts_method_enabled 谓词
        # 与 stage 23 同步启停 (见 core/dag.py StageSpec). 历史的"无条件预清理
        # stage 24 输出"特例已撤销 — 它原是为补救"stage 24 在 tone_berts 未启用
        # 但磁盘有残留 23_bert_tone.parquet 时静默用过期数据"这一缺陷而存在,
        # 谓词化后该路径被 filter_enabled() 直接排除, 不再需要特例补丁.
        # 通用 stage 输出预清理由下方 ``for script,...: _get_stage_output_files``
        # 循环 + STAGES 启用过滤共同覆盖, 维持 OUTPUT_REGISTRY 单一真值.

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
                can_skip_stage21, skip_reason = _stage21_skip_is_compatible(stage21_outputs)
                if can_skip_stage21:
                    logger.info(
                        f"  ⏭ {name}: --skip-21-if-exists 命中, 已跳过 "
                        f"({skip_reason})"
                    )
                    stage_timings.append((name, 0.0, True))
                    continue
                else:
                    logger.warning(
                        f"  --skip-21-if-exists 已启用, 但 {name} 不能安全跳过: "
                        f"{skip_reason}; 将重新执行该阶段"
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

            if success and output_files:
                missing_outputs = [
                    filename for filename in output_files
                    if not os.path.exists(os.path.join(CONFIG['paths']['output_dir'], filename))
                ]
                if missing_outputs:
                    logger.error(
                        f"{name} 子进程返回成功，但登记输出未生成: {missing_outputs}. "
                        f"按失败处理以避免下游读取陈旧或缺失数据。"
                    )
                    success = False

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
