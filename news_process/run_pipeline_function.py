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
    │ 11_news_bank → 12_news_fintech → 13_cooccurrence_filter   │
    │ → 14_materialize_ctx → 15_fintech_intensity                │
    │ → 16_article_policy_alignment                              │
    └────────────────────────────────────────────────────────────┘
    (13: 银行×金科邻近共现硬过滤, Andreou et al. 2026; 下游三轨链继承过滤)
                      ↓
    ┌─ 模块三：新闻情感模块 ──────────────────────────────┐
    │ 21_tone_llms → 22_tone_words → 23_tone_berts               │
    │ → 24_herd_decay_processor                                  │
    └────────────────────────────────────────────────────────────┘
                      ↓
    ┌─ 模块五：面板数据构建 ──────────────────────────────┐
    │ 40_panel_export_main (内含 41-44) → 46_stata_export        │
    └────────────────────────────────────────────────────────────┘
                      ↓
    ┌─ 模块六：伪造检验 ────────────────────────────────┐
    │ 51_falsification_test                                      │
    └────────────────────────────────────────────────────────────┘
                      ↓
                pipeline_summary

    情感分析的 LLM (21) / 词典 (22) / BERT (23) / 跟风衰减 (24) 自 2026-06-13 起
    全部为无条件 always-on (用户决策"全部启用而非条件启用", 对齐 2026-06-12 的
    23/24 先例); sentiment_analysis.enabled_methods 仅作启用记录, 不再驱动启停。
    文本嵌入与新颖度 (D 组: 25_article_sbert / 26_article_staleness)
    在情感模块后、面板构建前执行。

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

# Phase 1: 自单一真源导入 DAG, 使本编排器与 core/dag.py 共用同一份阶段定义。
# STAGES 作为模块级常量暴露, 供 tests/integration/test_dag_consistency.py 做静态一致性校验。
# 2026-06-13: 三种情感方法全部 always-on 后 METHOD_TO_PREDICATE 变空, 历史"未启用
# method 陈旧文件清理"循环退役 — 不再 import METHOD_TO_PREDICATE / get_script_for_method。
from news_process.core.dag import (
    STAGES_MAIN as STAGES,
)
from news_process.core.dag import filter_enabled
from news_process.core.locking import PipelineLock
from news_process.core.logging import log_memory_usage, pct4, setup_logging, sig4
from news_process.core.stage import run_stage

# ============================================================================
# 配置与初始化
#
# 加载顺序:
#   1. load_config(): 解析 config.yaml + .env 环境变量
#   2. _generate_run_id(): 生成本次运行的唯一 ID 并写入 NEWS_PROCESS_RUN_ID 环境变量
#                          (子进程经环境变量继承同一 ID, 仅作日志行内的运行关联标记)
#   3. setup_logging(): 创建日志文件 + 控制台输出
#                       (扁平路径 <log_dir>/<stage>.log; 每次运行覆盖同名日志, 只保留最新一次运行)
# 注意: 这是主调度器进程, 使用完整的文件+控制台双通道日志。
# 各阶段子进程各自写独立的 <log_dir>/<stage>.log (本次运行从头截断上一次同名日志).
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "run_pipeline_function"
# W5 通用 --skip-unchanged: config 目录 (与 core/config.py 同源: news_process/config)。
CONFIG_DIR = os.path.join(_HERE, 'config')


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
    """返回 ``stage_script`` 登记的 parquet 输出文件名列表.

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


# ── W5 通用 --skip-unchanged: 阶段 → 它消费的 split YAML 文件 (用文件名, 不用 CONFIG dict 键) ──
# golden-safe: 改某 YAML 内容 → 哈希变 → 相关 stage 失效。未登记 / 多源 fan-in 的 stage 走保守
# (未登记 → 不跳)。资源 (词典/anchor/prompt) 由 compute_resource_hashes 全量门另管。
STAGE_CONFIG_FILES: dict[str, tuple[str, ...]] = {
    "00_preprocessing.py": ("preprocessing.yaml", "paths.yaml"),
    "11_news_bank.py": ("filtering.yaml", "paths.yaml"),
    "12_news_fintech.py": ("filtering.yaml", "paths.yaml"),
    "13_cooccurrence_filter.py": ("filtering.yaml", "paths.yaml"),
    "14_materialize_ctx.py": ("filtering.yaml", "paths.yaml"),
    "15_fintech_intensity.py": ("filtering.yaml", "features.yaml", "paths.yaml"),
    "16_article_policy_alignment.py": ("filtering.yaml", "features.yaml", "paths.yaml"),
    "22_tone_words.py": ("sentiment.yaml", "paths.yaml"),
    "23_tone_berts.py": ("sentiment.yaml", "paths.yaml"),
    "24_herd_decay_processor.py": ("sentiment.yaml", "paths.yaml"),
    "25_article_sbert.py": ("features.yaml", "paths.yaml"),
    "26_article_staleness.py": ("features.yaml", "paths.yaml"),
    "40_panel_export_main.py": ("panel.yaml", "features.yaml", "paths.yaml"),
    "46_stata_export.py": ("panel.yaml", "paths.yaml"),
    "51_falsification_test.py": ("panel.yaml", "paths.yaml"),
}
# 注: stage 21 (LLM) 故意不在此表 — 它由专用 --skip-21-if-exists (三重指纹安检) 处理, 不走通用 skip。


# ── W5: DAG 根阶段的"原始输入"目录 glob (非上游 parquet) ──
# 仅根阶段 (stage 00) 的输入是 raw_data_dir 下 glob 的原始文件而非上游产物。根阶段没有
# 上游 → 前缀守卫 (any_stage_ran) 无从保护它 → 必须显式比对"当前 glob 集合 vs 已记
# input_hashes 集合"以检出**新增**文件 (内容变/删除由通用 input_hashes 循环覆盖)。
# (key, glob 模式) 须与 pipeline/preprocess/runner.enumerate_raw_xlsx / runner.py 处理 glob 一致。
STAGE_RAW_INPUT_GLOBS: dict[str, tuple[str, str]] = {
    "00_preprocessing.py": ("raw_data_dir", "*.xlsx"),
}


# ── W5: 阶段 → 暴露其"代码语义版本号"常量的 (module, attribute) ──
# --skip-unchanged 默认按 config/资源/输入内容寻址, **不**检测纯代码逻辑变更 —— 这是 opt-in
# 跳过对全部阶段的固有边界 (gate 在 git_commit 上会因每次提交都变而使跳过近乎失效)。但 DAG 根
# 阶段 stage 00 有项目既有的 PREPROCESS_CODE_VERSION 纪律 (compute_preprocess_cache_key 已用它
# 失效 per-file 缓存) → 在此把它接入跳过判据: 改预处理代码逻辑 (dedup/normalize/filter) 并 bump
# 该版本号后, --skip-unchanged 会正确失效根阶段跳过, 杜绝代码层 silent-staleness 在最关键的根阶段
# 发生。其余阶段无此类常量, 仍依赖 opt-in 契约 (改阶段代码勿配 --skip-unchanged, 或全量重跑)。
STAGE_CODE_VERSION: dict[str, tuple[str, str]] = {
    "00_preprocessing.py": (
        "news_process.pipeline.preprocess._constants", "PREPROCESS_CODE_VERSION",
    ),
}


def _stage_skip_unchanged_is_safe(script: str) -> tuple[bool, str]:
    """通用 --skip-unchanged 单阶段跳过判据 (保守, golden-safe; 纯读元数据不产数据)。

    全满足才跳: 登记产物全存在 + 元数据含 config_file_hashes/resource_hashes + 该 stage 相关
    split YAML 未变 + config/ 全部资源 (词典/anchor/prompt) 未变 + 已记 input_hashes 对当前文件
    全匹配 (任一被删/不可读/内容变 → 不跳) + (根阶段) 原始语料无新增文件 + (有 code_version 的阶段)
    代码版本未变。资源门是全量比对防"改词典却被错跳"。⚠ 主循环另有"前缀守卫" (任一上游阶段本次
    真跑过 → 下游一律不跳) 作数据依赖的根本安全网。判据**只读不抛**: 任一文件无法哈希核验 → 保守
    返 False (绝不让跳过判据本身 abort 整条 pipeline)。

    ✅ W5 已激活 (2026-06-26): stage 00 主产物现经 save_parquet_with_metadata 写 data_version
    元数据 (含原始 *.xlsx 语料的 input_hashes + PREPROCESS_CODE_VERSION)。

    覆盖边界 (诚实声明, 勿 overclaim):
      ✓ 检出 = 语料层 (xlsx 内容变/新增/删除/改名) + config split YAML 内容 + config/ 资源
        (词典/anchor/prompt) + 上游产物内容 + (stage 00) 预处理代码版本 PREPROCESS_CODE_VERSION。
      ✗ 不检出 = **非根阶段的纯代码逻辑变更** 与 **依赖/jieba/Python 版本变更** —— 这是 opt-in
        跳过对全部阶段的固有边界 (gate 在 git_commit 上会因每次提交都变而使跳过失效)。改了流水线
        代码而 config/语料未变时, **请勿配 --skip-unchanged** (或全量重跑); stage 00 例外已由
        STAGE_CODE_VERSION 接入版本门保护。
    """
    import glob as _glob

    from news_process.core.data_versioning import (
        compute_config_file_hashes,
        compute_file_hash,
        compute_resource_hashes,
        read_parquet_metadata,
    )
    outputs = _get_stage_output_files(script)
    if not outputs:
        return False, "无登记 parquet 产物 (validation/audit), 不参与增量跳过"
    want_yaml = STAGE_CONFIG_FILES.get(script)
    if want_yaml is None:
        return False, f"{script} 未登记 STAGE_CONFIG_FILES, 保守重跑"
    out_dir = CONFIG['paths']['output_dir']
    cur_cfg = compute_config_file_hashes(CONFIG_DIR)
    cur_res = compute_resource_hashes(CONFIG_DIR)
    raw_glob = STAGE_RAW_INPUT_GLOBS.get(script)
    # W5: 该阶段代码版本门 (仅 stage 00; 见 STAGE_CODE_VERSION)。一次性解析当前版本号。
    code_spec = STAGE_CODE_VERSION.get(script)
    cur_code_version = None
    if code_spec is not None:
        import importlib
        _mod_name, _attr = code_spec
        try:
            cur_code_version = getattr(importlib.import_module(_mod_name), _attr, None)
        except Exception as _e:  # noqa: BLE001 — 解析失败即保守重跑, 绝不 abort
            return False, f"{script} 无法解析当前代码版本 {_mod_name}.{_attr} ({_e.__class__.__name__}), 保守重跑"
    # 单次调用内文件哈希记忆 (多产物阶段避免对同一上游输入重复哈希; 也省 stage00 全语料重算)。
    _hash_memo: dict[str, str] = {}
    for fn in outputs:
        path = os.path.join(out_dir, fn)
        if not os.path.exists(path):
            return False, f"产物缺失 {fn}"
        meta = read_parquet_metadata(path)
        if not meta or 'config_file_hashes' not in meta or 'resource_hashes' not in meta:
            return False, f"{fn} 缺 config_file_hashes/resource_hashes 元数据 (旧产物), 保守重跑"
        for wf in want_yaml:
            if meta['config_file_hashes'].get(wf) != cur_cfg.get(wf):
                return False, f"config 文件 {wf} 内容已变"
        if meta['resource_hashes'] != cur_res:
            return False, "config/ 下资源文件 (词典/anchor/prompt) 内容已变"
        # 代码版本门 (仅 STAGE_CODE_VERSION 内阶段; 旧产物无 code_version → None ≠ 当前 → 保守不跳)。
        if code_spec is not None and meta.get('code_version') != cur_code_version:
            return False, (
                f"代码版本变 (记录={meta.get('code_version')} 当前={cur_code_version})"
            )
        rec_inputs = meta.get('input_hashes') or {}
        for rec_path, rec_hash in rec_inputs.items():
            # 已记输入被删/移动 → 不跳 (旧实现 os.path.exists 为 False 时静默放行, 是 silent-staleness 漏洞)。
            if not os.path.exists(rec_path):
                return False, f"已记输入 {os.path.basename(rec_path)} 已不存在 (被删/移动)"
            if rec_path not in _hash_memo:
                try:
                    _hash_memo[rec_path] = compute_file_hash(rec_path)
                except OSError as _e:
                    # 文件存在但不可读 (Windows 上被 Excel/杀软/OneDrive 锁) → 无法核验 → 保守重跑;
                    # 绝不让跳过判据本身抛异常 abort 整条 pipeline (与"保守=跑该阶段"一致)。
                    return False, (
                        f"输入 {os.path.basename(rec_path)} 无法读取核验 "
                        f"({_e.__class__.__name__}), 保守重跑"
                    )
            if _hash_memo[rec_path] != rec_hash:
                return False, f"输入 {os.path.basename(rec_path)} 内容已变"
        # ── DAG 根阶段专属: 原始语料"集合新增"门 (内容变/删除已由上方 input_hashes 循环覆盖) ──
        if raw_glob is not None:
            cfg_key, pattern = raw_glob
            raw_dir = CONFIG['paths'].get(cfg_key, '') or ''
            if not raw_dir:
                return False, f"{script} 原始输入目录 ({cfg_key}) 未配置, 保守重跑"
            suffix = pattern.lstrip('*').lower()
            cur_raw = {
                os.path.abspath(p)
                for p in _glob.glob(os.path.join(raw_dir, pattern))
            }
            rec_raw = {
                os.path.abspath(k) for k in rec_inputs
                if str(k).lower().endswith(suffix)
            }
            added = cur_raw - rec_raw
            if added:
                return False, (
                    f"原始语料新增 {len(added)} 个 {pattern} "
                    f"(如 {os.path.basename(sorted(added)[0])})"
                )
    return True, "config/资源/代码版本/原始与上游输入均未变"


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

# v3.2.0 双轨独立标签 — 下游 stage 40 (panel build) 强依赖. 若 --skip-21-if-exists
# 命中旧 (v3.1.x) 产物且这些列缺失, 下游会抛 KeyError. 见 CLAUDE.md / CHANGELOG.md
# v3.2.0 节: innovation_locus_{full,ctx} + innovation_substantiveness_{full,ctx}.
# legacy (full/ctx) by design: 这两族是 cell_id (D2/D4) 分类的 LLM 创新属性, 锚定
# full/ctx, v3.9.0 第三轨 ss (银行+金科同句) 是纯情感轨、有意不分解 substantiveness/
# locus, 故此处刻意只列 full/ctx 两轨 (无 *_ss 必需列; 见 encode_collab.py
# cell_id intentionally NOT produced)。
_STAGE21_REQUIRED_OUTPUT_COLUMNS = (
    'innovation_locus_full',
    'innovation_locus_ctx',
    'innovation_substantiveness_full',
    'innovation_substantiveness_ctx',
)


def _fingerprint_dataframe_rows(df, columns: tuple[str, ...]) -> tuple[int, str]:
    """对选定列返回确定性的 (行数, 内容 sha256 摘要) 二元组。"""
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
    """检查既有 stage 21 输出是否与当前 stage 14 输入匹配。

    只有当 stage 21 的 full 输出确实由当前 stage 14 parquet 生成时,
    ``--skip-21-if-exists`` 才是安全的; 否则上游重生后, 下游各 stage
    会静默消费过期的 LLM 标签。

    白话: 这是"跳过付费 LLM 阶段"的安检 — 对比上游输入和已有输出的
    行数与内容指纹, 对得上才允许跳过, 防止省钱省出旧数据。
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
        '15_fintech_intensity.parquet',
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
        # orchestrator skip-check 必须与实际 stage 21 留篇门控**逐字节同步**
        # (tone_llms.py 的 `df_filtered = df[df['llm_verified_full'] == True]` 留篇门控).
        # full-only 门控 (用户决策 2026-06-29; 逆转 v3.2.0 R1-A + v3.9.0 三轨并集):
        # main parquet filter = (verified_full == True) only —— ctx/ss 截断可能漏信息,
        # 不参与留篇 (降为 conditional-on-full)。⚠ 此处与 producer 是门控的**两份副本**,
        # 必须同改: 若 producer 改 full-only 而此处仍用并集, expected_rows(并集) !=
        # main_rows(full-only) → reject skip 永久, 每次重跑付费 stage 21。
        # (注: 旧并集副本本就漏 verified_ss, full-only 后该不一致一并消失。)
        full_cols = list(_STAGE21_FILTERED_FINGERPRINT_COLUMNS) + [
            'llm_verified_full',
        ]
        full_verify_df = pd.read_parquet(full_path, columns=full_cols)
        expected_main_df = full_verify_df[
            full_verify_df['llm_verified_full'] == True  # noqa: E712 - pandas boolean mask
        ].drop(columns=['llm_verified_full'])
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

    # v3.2.0 schema 漂移防护: fingerprint 一致也未必意味着旧产物含 v3.2.0
    # cell_id 创新属性列 (legacy full/ctx by design — 见 _STAGE21_REQUIRED_OUTPUT_COLUMNS
    # 注释: ss 第三轨不分解这两族)。若任一必需列缺失, reject skip → 触发
    # stage 21 重跑刷新 schema。
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
    parser.add_argument(
        "--skip-unchanged",
        action="store_true",
        help=(
            "通用阶段级增量: 跳过'输入未变'的阶段 (登记产物已存在 + 其 split YAML 内容 + "
            "config/ 资源 + 已记 input_hashes + (根阶段) 原始语料集合 + (stage00) 代码版本 均未变, "
            "且本次无上游阶段真跑过)。默认关 (不改生产首跑语义); 纯读 parquet 元数据决定是否 spawn, "
            "不进 stage 内存 = golden 中性。 ✅ 已激活 (2026-06-26): stage 00 经 save_parquet_with_metadata "
            "写 data_version 元数据 (原始 *.xlsx 语料 input_hashes + PREPROCESS_CODE_VERSION); 命中时其"
            "上游链 (00–16, stage21 走专用 --skip-21 + 前缀守卫) 可跳。检出: 语料内容变/删除/新增 + config/"
            "资源 + (stage00) 预处理代码版本。⚠ 不检出: **非根阶段的纯代码逻辑变更**与依赖/jieba 版本变 "
            "(opt-in 跳过的固有边界) — 改流水线代码请勿配本 flag 或全量重跑。机制经 tests/test_w5_skip_unchanged.py 覆盖。"
        ),
    )
    return parser.parse_args(argv)


def _log_environment_and_config(stages: list, enabled_methods: list) -> None:
    """打印 ① 项目/环境信息 + ② 输入输出根目录 + ③ 运行配置 + ④ 方法论依据 (日志富集 2026-06-24)。

    目标 (用户要求"在日志文件中提供尽可能多的项目信息、运行期间信息和运行结果信息"):
    把"谁在跑、跑在什么环境、读写哪些根目录、用了哪些可调参数、复现/溯源出处"一次性
    落进主调度器日志, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 (golden-safe)。
    ④ 方法论引文仅 emit 经 Crossref 真值核验的条目, 含 DOI 可访问链接 (FAIR 原则 Wilkinson
    et al. 2016 https://doi.org/10.1038/sdata.2016.18; Stodden et al. 2018 PNAS
    https://doi.org/10.1073/pnas.1708290115; Wilson et al. 2017 PLOS CB
    https://doi.org/10.1371/journal.pcbi.1005510), 绝不伪造 DOI (playbook §4 铁律)。
    """
    try:
        import platform

        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (主流水线编排器; 子进程隔离顺序执行 STAGES_MAIN)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) v3.11.1")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "编排器本身纯 CPU/无网络; LLM 成本由各子阶段决定 "
                    "(stage 21 离线缓存命中 $0; NEWS_PROCESS_LLM_OFFLINE=1 强制离线)")

        logger.info("  📂 输入 / 输出根目录")
        logger.info(f"     · 阶段脚本目录: {SCRIPT_DIR} (run_stage base_dir, 定位 NN_*.py thin shim)")
        logger.info(f"     · 产物输出目录: {CONFIG['paths']['output_dir']} (各阶段 *.parquet 中间产物)")
        logger.info(f"     · 日志目录:     {CONFIG['paths']['log_dir']} (扁平 <stage>.log; 每次运行覆盖)")

        logger.info("  ⚙ 运行配置")
        logger.info(f"     · DAG 阶段数: {len(stages):,d} (来源 core/dag.py::STAGES_MAIN, filter_enabled 后)")
        logger.info(f"     · 启用情感方法: {enabled_methods} (2026-06-13 起 21/22/23/24 全 always-on, 仅作记录)")
        logger.info("     · 执行策略: 子进程隔离 + fail-fast (任一阶段失败立即中止) + 阶段前输出预清理")

        logger.info("  📖 方法论依据 (可复现计算流水线 / 科研软件 / 数据出处)")
        logger.info("     · 可复现计算流水线设计: Stodden, V., Seiler, J., & Ma, Z. (2018). An empirical "
                    "analysis of journal policy effectiveness for computational reproducibility. PNAS, "
                    "115(11), 2584-2589. https://doi.org/10.1073/pnas.1708290115")
        logger.info("     · 科研软件工程良好实践 (DAG/隔离/日志溯源): Wilson, G., Bryan, J., Cranston, K., "
                    "Kitzes, J., Nederbragt, L., & Teal, T. K. (2017). Good enough practices in scientific "
                    "computing. PLOS Computational Biology, 13(6), e1005510. "
                    "https://doi.org/10.1371/journal.pcbi.1005510")
        logger.info("     · 数据可发现/可复用 (FAIR) 原则: Wilkinson, M. D., Dumontier, M., Aalbersberg, "
                    "I. J., et al. (2016). The FAIR Guiding Principles for scientific data management and "
                    "stewardship. Scientific Data, 3, 160018. https://doi.org/10.1038/sdata.2016.18")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法信息打印失败 (不影响处理): {e}")


def run_pipeline(args: argparse.Namespace | None = None):
    """执行完整的数据处理流水线。

    流程：
      1. 执行模块一：新闻预处理模块 (00)
      2. 执行模块二：新闻筛选模块 (11, 12, 13, 14, 15, 16)
      3. 执行模块三：新闻情感模块 (21/22/23/24 全部无条件 always-on)
      4. 执行模块五：面板数据构建 (40 面板编排, 内含 41-47)
      5. 执行模块六：伪造检验对照变量构建 (51)
      6. 生成管道执行摘要报告和耗时统计

    注：模块四（评估验证）已独立为 run_pipeline_validation.py，
        请单独执行：python run_pipeline_validation.py

    Args:
        args: argparse.Namespace, 由 ``_parse_cli_args`` 解析得到; 默认 None
              表示按默认全量执行 (向后兼容旧调用方式)。
    """
    if args is None:
        args = argparse.Namespace(skip_21_if_exists=False, skip_unchanged=False)

    pipeline_start = time.time()
    # 运行期阶段计时累计 (编排器自身各子阶段墙钟耗时, 末尾汇总打印; 纯日志, golden-safe)。
    # 注: 各 pipeline stage 的耗时由下方 stage_timings 逐条记录; 此 dict 记编排器框架开销。
    phase_durations: dict[str, float] = {}

    # ── 并发运行保护：确保同一时间只有一个管道实例运行 ──
    with PipelineLock(logger, CONFIG["paths"]["output_dir"]):
        # ── 【功能】banner (黄金范式, 对齐 herd_decay.main() 单 banner 范式) ──
        logger.info("=" * 72)
        logger.info("新闻处理流水线编排器 (News Processing Pipeline Orchestrator, v3.11.1)")
        logger.info("=" * 72)
        logger.info(
            "【功能】把'一堆原始中文银行/金科新闻 Excel'端到端加工成'可做计量回归的"
        )
        logger.info(
            "        银行-年面板 (.parquet/.dta)'。本脚本不亲自算, 而是按依赖顺序逐个"
        )
        logger.info(
            "        把各阶段 (预处理→筛选→情感→面板→伪造检验) 作为独立子进程拉起来跑。"
        )
        logger.info(
            "【方法】声明式 DAG (core/dag.py::STAGES_MAIN) 单一真源驱动; 每阶段子进程隔离"
        )
        logger.info(
            "        (异常不串、内存释放、jieba 等全局态不冲突); fail-fast (任一阶段失败"
        )
        logger.info(
            "        立即中止); 阶段执行前按 OUTPUT_REGISTRY 预清理旧产物防陈旧污染。"
        )
        logger.info(
            "【判读】末尾耗时统计表逐阶段列墙钟秒+占比: ✓=成功 / ✗=失败 / ⏭=已跳过 (如"
        )
        logger.info(
            "        --skip-21-if-exists 命中); 占比最高者即流水线瓶颈 (通常为 LLM 阶段 21)。"
        )
        logger.info(
            "        '✓ 管道全部阶段执行成功' 才表示全链产物齐备, 可进 Stata 复现。"
        )
        logger.info(
            "【确定性】编排器自身纯 CPU/无网络; 全链可复现性取决于各子阶段 (jieba==0.42.1 冻结"
        )
        logger.info(
            "          + stage 21 _llm_cache.db 离线命中 $0 + 固定 HASHSEED/BLAS 线程)。"
        )

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

        # ── 数据流防护：通用 stage 输出预清理 ──
        # 2026-06-13: 三种情感方法 (21 LLM / 22 词典 / 23 BERT) 已全部 always-on,
        # 不再有"被配置关掉"的 method → 历史"未启用 method 陈旧文件清理"循环
        # (依赖 dag.METHOD_TO_PREDICATE + get_script_for_method) 已退役。所有 stage
        # 的输出预清理统一由下方通用循环 (``for script,...: _get_stage_output_files``)
        # + STAGES 启用过滤覆盖, 维持 OUTPUT_REGISTRY 单一真值。
        # 白话: 以前要把"被关掉的情感方法"留在硬盘上的旧结果删掉; 现在三种方法都
        #       焊死常开, 没有被关掉的方法了, 这段专门的清理循环就不需要了。

        # ── Phase 1: 从 core/dag.py 加载完整 DAG (主线阶段现已全部 always_enabled,
        #    filter_enabled 恒返回全集; 机制保留供未来扩展 / 对称 validation) ──
        active_specs = filter_enabled(STAGES, CONFIG)
        # 兼容下方既有迭代结构: 每条 (script, name, timeout)。
        stages = [(s.script, s.name, s.timeout) for s in active_specs]

        logger.info(f"管道共 {len(stages)} 个阶段")
        for i, (script, name, _to) in enumerate(stages, 1):
            status = "待执行"
            logger.info(f"  {i}. {name} ({script}) [{status}]")

        # 项目/环境信息 + 输入输出根目录 + 运行配置 + 方法论依据 (日志富集 2026-06-24,
        # DAG/config 解析完成后打印; 纯日志, golden-safe)
        _log_environment_and_config(stages, enabled_methods)

        # ── 逐阶段执行 ──
        # 速败 (fail-fast) 策略: 任一阶段失败则立即中止整条管道。
        # 避免在错误中间结果上继续执行, 降低级联错误难以溯源的风险。
        stage_timings = []
        all_success = True
        # W5 前缀守卫: 一旦某阶段本次真跑过, 其后阶段一律不可走 --skip-unchanged
        # (上游可能改了下游输入)。这是通用 skip 的数据依赖根本安全网。
        any_stage_ran = False

        # Phase 1: 超时现取自 StageSpec (经 core/dag.py 单一真源)。
        # 重构前此处曾有本地 stage_timeouts 字典; 已上收为 StageSpec.timeout。

        for script, name, timeout in stages:
            # W5: 通用 --skip-unchanged (前缀守卫 + 三重哈希门; stage21 走专用 --skip-21, 不在此)
            if (args.skip_unchanged and not any_stage_ran
                    and script != '21_tone_llms.py'):
                can_skip_unchanged, unchanged_reason = _stage_skip_unchanged_is_safe(script)
                if can_skip_unchanged:
                    logger.info(
                        f"  ⏭ {name}: --skip-unchanged 命中, 已跳过 ({unchanged_reason})"
                    )
                    stage_timings.append((name, 0.0, True))
                    continue

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
            # W5 前缀守卫: 本阶段真跑过 → 其后阶段不可再走 --skip-unchanged。
            any_stage_ran = True

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
            logger.info(f"  {name:<28} {sig4(elapsed):>10}s {pct4(pct, fraction=False):>10} {status:>6}")

        logger.info("-" * 70)
        minutes = total_elapsed / 60
        hours = total_elapsed / 3600
        logger.info(
            f"  {'总计':<28} {sig4(total_elapsed):>10}s "
            f"({sig4(minutes)} 分钟 / {sig4(hours)} 小时)"
        )
        # 编排器框架开销 = 总墙钟 − 各阶段子进程墙钟之和 (锁/预清理/摘要/IO 等; 纯日志)
        _stage_sum = sum(e for _n, e, _s in stage_timings)
        phase_durations['①编排器框架开销(锁/预清理/摘要)'] = max(total_elapsed - _stage_sum, 0.0)
        phase_durations['②各阶段子进程合计'] = _stage_sum
        logger.info("  ⏱ 阶段计时 (墙钟秒, 4 位有效数字)")
        for _phase, _dur in phase_durations.items():
            logger.info(f"     · {_phase}: {sig4(_dur)}s")
        logger.info("=" * 70)

        log_memory_usage(logger, "管道完成")

        if all_success:
            logger.info("✓ 管道全部阶段执行成功！")
        else:
            logger.error("✗ 管道执行中断，请检查日志。")
            sys.exit(1)


if __name__ == "__main__":
    run_pipeline(_parse_cli_args())
