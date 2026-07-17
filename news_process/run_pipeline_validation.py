"""
run_pipeline_validation.py — 新闻处理流水线: 评估验证模块
===========================================================

功能:
    单独执行流水线的模块四: 评估验证模块。
    包含以下阶段 (2026-06-13 起全部无条件 always-on; validation.* flag 仅作启用记录):
      - 阶段60:  阈值敏感性分析         (60_bank_fintech_threshold.py)
      - 阶段61:  人工抽样验证样本生成   (61_news_llms_human.py)
      - 阶段62: 去重阈值敏感性分析     (62_dedup_threshold_sensitivity.py)
      - 阶段63:  分类有效性评估         (63_news_llms_evaluation.py)
      - 阶段64:  情感三角验证           (64_tone_validation.py)
      - 阶段65:  窗口半径敏感性检验     (65_radius_sensitivity.py)
      - 阶段66:  Entity Masking 稳健性测试 (66_entity_masking_test.py)
      - 阶段67:  金融科技词典覆盖率审计 (67_dict_coverage_audit.py)
      - 阶段68:  媒体名称与地域多样性审计 (68_media_diversity.py)
      - 阶段69: 距离衰减权重敏感性检验 (69_decay_sensitivity.py)
      - 阶段70:  Prompt 措词敏感度测试  (70_prompt_sensitivity.py)
      - 阶段71: 轨间一致性 Cohen's κ    (71_inter_track_kappa.py)
      - 阶段72: NMI construct 正交性     (72_construct_orthogonality.py)
      - 阶段73: lexical HTMT+AVE+κ+α     (73_lexical_discriminant_validity.py)
      - 阶段74: LM 6 子词典 discriminant (74_lm_discriminant_validity.py)
      - 阶段75: cross-media Krippendorff α (75_cross_media_alpha.py)
    (阶段清单以 core/dag.py::STAGES_VALIDATION 为权威真源, 共 16 个。)

复现 / 离线注意 (F6/F10, 2026-07-10 五入口再验证):
    - 阶段 66 (entity_masking) / 70 (prompt_sensitivity) 依赖**在线付费 LLM** 重判变体 prompt
      (离线缓存不覆盖变体 prompt_version)。设 NEWS_PROCESS_LLM_OFFLINE=1 时二者优雅跳过、不产出稳健性表;
      **复现这两张表须配 YUNWU_API_KEY / DEEPSEEK_API_KEY 联网重跑** (F6: 复现包 README/data appendix 须明记)。
    - 66/70 离线跳过时**不清理也不覆写**上一轮遗留在 eval_reports/ 的 entity_masking_* / prompt_* 产物 →
      浏览目录时其新鲜度**以 mtime 为准** (F10: 勿把旧轮产物误当本轮结果; 对比 63 的 _DEMO 文件名纪律)。

设计意图:
    这些验证模块对应经济学顶级期刊审稿中常见的稳健性检验要求:
    - 阈值敏感性(60): 证明结论不依赖特定参数选择
    - 人工标注一致性(61,63): Cohen's κ 和 Krippendorff's α; 误分类系统相关性诊断 Carlson & Burbano (2026, SMJ)
    - 三角验证(64): 开放科学中的 “方法三角化” 原则
    - 实体掩码(66): 实体替换稳健性 (SSRN-4558295 §7.2) + Cohen's κ (Landis & Koch 1977)
    - Prompt 敏感度(70): LLM 研究中的表述稳健性检验

使用方法::

    python run_pipeline_validation.py
"""

import argparse
import os
import sys
import time

# Phase 1: 将项目父目录置于 sys.path, 使任意 cwd 下 ``import news_process`` 均可解析。
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(_HERE)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

# Phase 6a: utils.* → news_process.core.*
from news_process.core.config import load_config

# Phase 1: 导入验证 DAG 单一真源; STAGES 作为模块级常量供
# tests/integration/test_dag_consistency.py 静态一致性校验。
from news_process.core.dag import STAGES_VALIDATION as STAGES
from news_process.core.dag import filter_enabled
from news_process.core.locking import PipelineLock
from news_process.core.logging import log_memory_usage, setup_logging, sig4
from news_process.core.stage import run_stage

# ============================================================================
# 配置与初始化  (Phase 1.5: NEWS_PROCESS_RUN_ID 生成与 env 注入)
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "run_pipeline_validation"


def _generate_run_id() -> str:
    """生成本次运行 ID (委托给 core.run_id.generate_run_id)。"""
    from news_process.core.run_id import generate_run_id
    return generate_run_id()


_RUN_ID = _generate_run_id()
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])
# A3 修复 (2026-07-09 五入口诊断): RUN_ID emit 下沉到 run_validation() 入口。原在模块级立即 emit 会
# 触发 _DelayedTruncatingRotatingHandler 首写以 mode='w' 截断上次 .log —— 连 --help / pytest import
# 都会截断日志。setup_logging(delay=True) 本身 import 不截断, 仅这条 emit 是首写触发者; 下沉后 import
# 不再截断, 实跑时在函数入口正常 emit。


# 脚本所在目录（用于定位阶段脚本）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _log_environment_and_config(stages: list) -> None:
    """打印 ① 项目/环境信息 + ② 输入输出 + ③ 运行配置 + ④ 方法论依据 (日志富集, 2026-06-24)。

    目标 (用户要求"在日志文件中提供尽可能多的项目信息、运行期间信息和运行结果信息"):
    把"谁在跑、跑在什么环境、读写哪些目录、用了哪些可调参数、方法学出处"一次性落进
    日志, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物或控制流 (golden-safe)。
    ④ 方法论引文仅 emit 经 Crossref 真值核验的条目, 含 DOI 可访问链接 (Simonsohn et al. 2020
    NHB https://doi.org/10.1038/s41562-020-0912-z; Steegen et al. 2016 PPS
    https://doi.org/10.1177/1745691616658637; Landis & Koch 1977 Biometrics
    https://doi.org/10.2307/2529310), 绝不伪造 DOI (playbook §4 铁律)。
    """
    try:
        import platform

        paths = CONFIG.get("paths", {})
        output_dir = paths.get("output_dir", "(未配置)")
        log_dir = paths.get("log_dir", "(未配置)")

        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (评估验证编排器; 调度 STAGES_VALIDATION 全部 "
                    f"{len(STAGES):,d} 个稳健性/规格检验子阶段)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) v3.16.0")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID') or _RUN_ID
        _offline = os.environ.get('NEWS_PROCESS_LLM_OFFLINE')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    f"NEWS_PROCESS_LLM_OFFLINE={_offline or '(未设置)'}")
        logger.info("     · 成本/确定性: 编排器自身 $0/纯调度; 子阶段中含 LLM 探针的 (66/70) 在 "
                    "OFFLINE=1 下缓存命中即 $0, 其余纯 CPU 逐位可复现")

        logger.info("  📂 输入 / 输出目录")
        logger.info(f"     · 产物输出目录: {output_dir} (各子阶段读写 data/processed/*.parquet 与 eval_reports/*.csv)")
        logger.info(f"     · 日志目录:     {log_dir} (扁平布局, 每子阶段一文件, 覆盖式只留最新一次运行)")

        logger.info("  ⚙ 运行配置 (core/dag.py::STAGES_VALIDATION 为权威真源)")
        logger.info(f"     · 待执行子阶段数={len(stages):,d} (全部无条件 always-on; "
                    "filter_enabled 恒返回全集, validation.* flag 仅作启用记录)")
        logger.info("     · 执行策略: 逐阶段子进程隔离 + 速败 (任一阶段失败即中止后续, "
                    "因验证阶段间存在隐式依赖)")

        logger.info("  📖 方法论依据 (核心方法/构念学术出处)")
        logger.info("     · 规格曲线 / 多元宇宙稳健性报告范式: Simonsohn, U., Simmons, J. P., & Nelson, "
                    "L. D. (2020). Specification curve analysis. Nature Human Behaviour, 4(11), 1208-1214. "
                    "https://doi.org/10.1038/s41562-020-0912-z")
        logger.info("       → 把'结论是否依赖某一特定参数/规格选择'物化为一族合理规格上的稳健性分布 (本模块"
                    "阈值/半径/衰减/prompt 敏感性子阶段即此范式的离散网格实现)")
        logger.info("     · 透明度多元宇宙分析: Steegen, S., Tuerlinckx, F., Gelman, A., & Vanpaemel, W. "
                    "(2016). Increasing transparency through a multiverse analysis. Perspectives on "
                    "Psychological Science, 11(5), 702-712. https://doi.org/10.1177/1745691616658637")
        logger.info("     · 标注者一致性 (Cohen's κ / Krippendorff's α 量表): Landis, J. R., & Koch, G. G. "
                    "(1977). The measurement of observer agreement for categorical data. Biometrics, 33(1), "
                    "159-174. https://doi.org/10.2307/2529310 — 子阶段 63/66/71/75 一致性判读基准")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法信息打印失败 (不影响处理): {e}")


def run_validation():
    """执行模块四：评估验证模块。

    流程：
      1. 阶段60: 阈值敏感性分析（always-on）
      2. 阶段61: 人工抽样验证样本生成（always-on）
      2a.阶段62: 去重阈值敏感性分析（always-on）
      3. 阶段63: 分类有效性评估（always-on）
      4. 阶段64: 情感三角验证（always-on）
      5. 阶段65: 窗口半径敏感性检验（always-on）
      6. 阶段66: Entity Masking 稳健性测试（always-on）
      7. 阶段67: 金融科技词典覆盖率审计（always-on）
      8. 阶段68: 媒体名称与地域多样性审计（always-on）
      9. 阶段69: 距离衰减权重敏感性检验（always-on）
     10. 阶段70: Prompt 措辞敏感度测试（always-on）
     11. 阶段71: 轨间一致性 Cohen's κ
     12. 阶段72: NMI construct 正交性
     13. 阶段73: lexical HTMT+AVE+κ+α
     14. 阶段74: LM 6 子词典 discriminant
     15. 阶段75: cross-media Krippendorff α

    阶段清单以 core/dag.py::STAGES_VALIDATION 为权威真源, 共 16 个;
    2026-06-13: 全部 16 阶段均为无条件 always-on (用户决策: 全部启用而非条件启用),
    filter_enabled(STAGES, CONFIG) 恒返回全集 (机制保留供未来扩展); validation.* flag
    仅作启用记录, 不再驱动启停。
    """
    module_start = time.time()
    # A3+F4: RUN_ID emit 下沉到 with PipelineLock 块内 (见下方) — 防被拒并发实例截断在跑实例 .log。

    # ── 并发运行保护 (plan s3): 与主流水线对称, 共享同一锁文件 ──
    # validation 与 main pipeline 都会读写 output_dir/, 共享 logger / 中间 cache;
    # 同时跑两个进程会产生数据竞争与日志互踩, 必须互斥。
    with PipelineLock(logger, CONFIG["paths"]["output_dir"],
                      console_only_on_reject=True):
        logger.info(f"NEWS_PROCESS_RUN_ID = {_RUN_ID}")  # A3/F4: 获锁后首条 file emit
        logger.info("=" * 72)
        logger.info("模块四: 评估验证编排器 (规格曲线/多元宇宙稳健性; Simonsohn 2020 NHB / Steegen 2016 PPS)")
        logger.info("=" * 72)
        logger.info(
            "【功能】对前三模块(预处理→分类→情感分析)的每一个关键人为决策(阈值/窗口半径/"
        )
        logger.info(
            "        去重门槛/衰减形式/prompt 措辞/实体名)逐一做稳健性检验, 输出诊断表证明"
        )
        logger.info(
            "        研究结论不依赖任一特定参数选择, 对应顶刊审稿常见的 robustness 要求。"
        )
        logger.info(
            "【方法】以子进程隔离逐一调度 STAGES_VALIDATION 的全部子阶段 (敏感性网格 / Cohen's κ"
        )
        logger.info(
            "        / Krippendorff's α / NMI 正交性 / HTMT-AVE 判别效度 / 多样性 HHI-Shannon),"
        )
        logger.info(
            "        各阶段独写 eval_reports/*.csv 诊断表; 速败=任一失败即中止 (阶段间隐式依赖)。"
        )
        logger.info(
            "【判读】κ/α 落入 Landis-Koch 量表 (>0.6=substantial) = 一致性达标; 敏感性 ρ_vs_baseline"
        )
        logger.info(
            "        越高(≥0.9) = 排序对该参数门槛越不敏感(结论越稳健); 正交性 NMI 越低 = 构念越独立。"
        )
        logger.info(
            "【确定性】编排器自身纯调度 $0; 子阶段除 66/70 含 LLM 探针(OFFLINE 下缓存命中即 $0)外"
        )
        logger.info(
            "        均纯 CPU; 固定参数 + 稳定排序 → 逐位可复现。"
        )
        logger.info("")
        logger.info("  📌 模块目的")
        logger.info("     对前三模块(预处理→分类→情感分析)的全部关键决策进行系统性验证,")
        logger.info("     确保研究结论不受人为参数选择、模型偏差或数据噪声的影响。")
        logger.info("")
        logger.info("  📖 16 个验证阶段说明 (core/dag.py::STAGES_VALIDATION 为权威真源)")
        logger.info("     60:  阈值敏感性  — 分类参数做网格搜索, 证明当前阈值是稳健的")
        logger.info("     61:  人工抽样    — 生成分层随机样本供人工标注比对")
        logger.info("     62: 去重敏感性  — Jaccard MinHash 多阈值去重, 证明去重参数稳健 (Broder 1997)")
        logger.info("     63:  分类评估    — 计算 Cohen's κ / Krippendorff's α, 量化 LLM 一致性")
        logger.info("     64:  三角验证    — 词典/BERT/LLM 三种方法交叉验证构建效度")
        logger.info("     65:  窗口敏感性  — 检验上下文提取半径对情感度量的影响")
        logger.info("     66:  实体掩码    — 替换银行名验证情感判定不依赖实体先验")
        logger.info("     67:  词典审计    — 金融科技关键词覆盖率和精确度系统审计")
        logger.info("     68:  媒体多样性  — HHI/Shannon/Gini 多维度量化媒体来源与地域覆盖")
        logger.info("     69: 衰减敏感性  — 比较 uniform/inverse/exponential 权重, 检验结果稳健性")
        logger.info("     70:  提示词敏感度 — 系统性改写 Prompt 措辞, 量化标注结果的表述稳健性")
        logger.info("     71: 轨间一致性  — full/ctx/ss 三轨两两 Cohen's κ (3 pair × 3 维 = 9 行)")
        logger.info("     72: 正交性      — 三 construct 的 NMI 正交性 + permutation null")
        logger.info("     73: 词汇判别效度 — HTMT+AVE+Cohen's κ+Cronbach's α")
        logger.info("     74: LM 判别效度 — LM 2011 JF 6 子词典 discriminant validity")
        logger.info("     75: 跨媒体一致性 — outlet×day Krippendorff's α")
        logger.info("")
        logger.info(f"Python: {sys.version}")
        logger.info(f"工作目录: {os.path.dirname(os.path.abspath(__file__))}")
        log_memory_usage(logger, "模块启动")

        # ── 模块四: 评估验证模块 ──
        # Phase 1 重构: 阶段定义已迁移至 news_process/core/dag.py:STAGES_VALIDATION,
        # 旧的内联 12 处 if-append 链已被 filter_enabled() 取代。
        # 2026-06-13: 全部验证阶段谓词改为 always_enabled (用户决策: 全部启用而非条件
        # 启用), filter_enabled 恒返回全集; 旧 validation.* flag 仅作配置记录保留。
        active_specs = filter_enabled(STAGES, CONFIG)
        stages = [(s.script, s.name, s.timeout) for s in active_specs]

        # 项目/环境信息 + 目录 + 运行配置 + 方法论依据 (日志富集 2026-06-24, stages 确定后打印)
        _log_environment_and_config(stages)

        logger.info(f"评估验证模块共 {len(stages)} 个阶段")
        for i, (script, name, _to) in enumerate(stages, 1):
            logger.info(f"  {i}. {name} ({script})")

        # ── 逐阶段执行 ──
        stage_timings = []
        all_success = True

        for script, name, timeout in stages:
            success, elapsed = run_stage(script, name, logger, SCRIPT_DIR, timeout=timeout)
            stage_timings.append((name, elapsed, success))

            if not success:
                all_success = False
                # 速败策略: 与主流水线一致, 任一阶段失败即中止。
                # 验证模块间存在隐式依赖 (如 36 依赖 21 的输出),
                # 前置失败则后续结果无解释意义。
                logger.error(f"评估验证模块在 {name} 处中断。后续阶段将跳过。")
                break

        # ── 耗时统计 ──
        total_elapsed = time.time() - module_start
        logger.info("\n" + "=" * 70)
        logger.info("===    评估验证模块耗时统计    ===")
        logger.info("=" * 70)
        logger.info(f"{'阶段':<30} {'耗时(秒)':>12} {'耗时占比':>10} {'状态':>6}")
        logger.info("-" * 70)

        for name, elapsed, success in stage_timings:
            pct = (elapsed / total_elapsed) if total_elapsed > 0 else 0
            status = "✓" if success else "✗"
            if elapsed == 0.0 and success:
                status = "⏭"
            logger.info(f"  {name:<28} {sig4(elapsed):>10}s {sig4(pct * 100):>9}% {status:>6}")

        logger.info("-" * 70)
        minutes = total_elapsed / 60
        logger.info(f"  {'总计':<28} {sig4(total_elapsed):>10}s ({sig4(minutes)} 分钟)")
        logger.info("=" * 70)

        log_memory_usage(logger, "模块完成")

        if all_success:
            logger.info("✓ 评估验证模块全部阶段执行成功！")
        else:
            logger.error("✗ 评估验证模块执行中断，请检查日志。")
            sys.exit(1)


if __name__ == "__main__":
    # A2 修复 (2026-07-09 五入口诊断): 原文件无 argparse, --help/任何参数被静默忽略直接全量实跑
    # 并获 PipelineLock(覆写 eval_reports/parquet 产物)。加 argparse 提供 -h/--help + --dry-run 预检;
    # 无参数=全量默认(向后兼容)。dry-run 用 print(非 logger, 避免触发日志层截断/落盘), 且在
    # run_validation() 之前 branch(该函数 with PipelineLock 获锁实跑)。
    _parser = argparse.ArgumentParser(
        prog="run_pipeline_validation",
        description="新闻处理流水线: 评估验证模块 (模块四, STAGES_VALIDATION 全 always-on; 无参数=全量实跑)",
    )
    _parser.add_argument(
        "--dry-run", action="store_true",
        help="只打印将执行的 STAGES_VALIDATION 阶段清单, 不获锁、不实跑、不写产物 (冒烟/预检)。",
    )
    _args = _parser.parse_args()
    if _args.dry_run:
        _stages = [(s.script, s.name) for s in filter_enabled(STAGES, CONFIG)]
        print(f"[dry-run] run_pipeline_validation 将执行 {len(_stages)} 个验证阶段 "
              f"(STAGES_VALIDATION, 全 always-on):")
        for _i, (_script, _name) in enumerate(_stages, 1):
            print(f"  {_i:2d}. {_name} ({_script})")
        print("[dry-run] 未获锁、未实跑、未写任何产物。")
    else:
        run_validation()
