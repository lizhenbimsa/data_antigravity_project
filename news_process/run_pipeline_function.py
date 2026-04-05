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
    │ 11_news_bank → 12_news_fintech                             │
    └────────────────────────────────────────────────────────────┘
                      ↓
    ┌─ 模块三：新闻情感模块 ──────────────────────────────┐
    │ 21_tone_llms → 22_tone_words → 23_tone_berts               │
    └────────────────────────────────────────────────────────────┘
                      ↓
    ┌─ 模块五：面板数据构建 ──────────────────────────────┐
    │ 40_build_panel                                             │
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

import os
import sys
import time
import psutil
from utils.helpers import load_config, setup_logging, log_memory_usage, log_stage_summary, run_stage

# ============================================================================
# 配置与初始化
#
# 加载顺序:
#   1. load_config(): 解析 config.yaml + .env 环境变量
#   2. setup_logging(): 创建带时间戳的日志文件 + 控制台输出
# 注意: 这是主调度器进程, 使用完整的文件+控制台双通道日志。
# 各阶段子进程会各自创建独立的日志文件。
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "run_pipeline_function"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])


# 脚本所在目录(用于定位阶段脚本, 传给 run_stage() 的 base_dir 参数)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_pipeline():
    """执行完整的数据处理流水线。

    流程：
      1. 执行模块一：新闻预处理模块 (00)
      2. 执行模块二：新闻筛选模块 (11, 12)
      3. 执行模块三：新闻情感模块 (21, 22, 23, 视配置启动)
      4. 执行模块五：面板数据构建 (40)
      5. 执行模块六：伪造检验对照变量构建 (41)
      6. 生成管道执行摘要报告和耗时统计

    注：模块四（评估验证）已独立为 run_pipeline_validation.py，
        请单独执行：python run_pipeline_validation.py
    """
    pipeline_start = time.time()

    logger.info("=" * 70)
    logger.info("===    新闻处理流水线 (News Processing Pipeline)    ===")
    logger.info("==" * 35)
    logger.info(f"Python: {sys.version}")
    logger.info(f"工作目录: {os.path.dirname(os.path.abspath(__file__))}")
    log_memory_usage(logger, "管道启动")

    # ── 流水线执行顺序(模块一至三 + 模块五至六) ──
    # 严格递进流转: 预处理 → 筛选 → 情感 → 面板构建 → 伪造检验
    # 每个阶段的输入依赖前一阶段的输出, 因此必须严格顺序执行。

    stages = []

    # ── 模块一：新闻预处理模块 ──
    stages.append(("00_preprocessing.py", "阶段00: 数据预处理"))

    # ── 模块二：新闻筛选模块 ──
    stages.extend([
        ("11_news_bank.py",          "阶段11: 银行新闻判断"),
        ("12_news_fintech.py",       "阶段12: 金融科技新闻判断 + 全量分类结果"),
    ])

    # ── 模块三：新闻情感模块 ──
    enabled_methods = CONFIG.get('sentiment_analysis', {}).get('enabled_methods', [])
    logger.info(f"启用的情感分析方法: {enabled_methods}")

    sentiment_stages = {
        'tone_llms':  ("21_tone_llms.py",  "阶段21: 统一 LLM 语义精筛与情感分析"),
        'tone_words': ("22_tone_words.py", "阶段22: 词典法情感分析"),
        'tone_berts': ("23_tone_berts.py", "阶段23: BERT模型情感分析"),
    }
    # 根据 config.yaml 中的 sentiment_analysis.enabled_methods 动态确定
    # 哪些情感分析方法需要执行。可选方法:
    #   tone_llms:  LLM 语义精筛 + 情感分析(依赖外部 API)
    #   tone_words: 词典法情感分析(无外部依赖, 速度最快)
    #   tone_berts: BERT 模型情感分析(依赖 GPU/CPU, 计算量最大)
    for method in enabled_methods:
        if method in sentiment_stages:
            stages.append(sentiment_stages[method])
        else:
            logger.warning(f"未知的情感分析方法: {method}，已跳过")

    # ── 模块五：面板数据构建 ──
    stages.append(("40_build_panel.py", "阶段40: Bank-Year 面板数据构建"))

    # ── 模块六：伪造检验 ──
    stages.append(("51_falsification_test.py", "阶段51: 伪造检验对照变量构建"))

    logger.info(f"管道共 {len(stages)} 个阶段")
    for i, (script, name) in enumerate(stages, 1):
        status = "待执行"
        logger.info(f"  {i}. {name} ({script}) [{status}]")

    # ── 逐阶段执行 ──
    # Fail-fast 策略: 任何阶段失败即立中断整个管道。
    # 这样的设计确保不会基于错误的中间数据继续执行,
    # 避免产生难以追溯的级联错误。
    stage_timings = []
    all_success = True

    for script, name in stages:
        success, elapsed = run_stage(script, name, logger, SCRIPT_DIR)
        stage_timings.append((name, elapsed, success))

        if not success:
            all_success = False
            logger.error(f"管道在 {name} 处中断。后续阶段将跳过。")
            break

    # ── 生成管道摘要报告 ──
    if all_success:
        try:
            from utils.pipeline_reporting import generate_pipeline_summary
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
    run_pipeline()
