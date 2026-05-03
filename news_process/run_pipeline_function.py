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

import os
import sys
import time
from utils.helpers import load_config, setup_logging, log_memory_usage, log_stage_summary, run_stage
from utils.pipeline_lock import PipelineLock

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

def _get_stage_output_files(stage_script: str) -> list:
    """根据阶段脚本名获取其输出文件列表。

    Args:
        stage_script: 阶段脚本文件名（如 "00_preprocessing.py"）

    Returns:
        list: 该阶段输出的文件名列表
    """
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

def run_pipeline():
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
    """
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

        stages = []

        # ── 模块一：新闻预处理模块 ──
        stages.append(("00_preprocessing.py", "阶段00: 数据预处理"))

        # ── 模块二：新闻筛选模块 ──
        stages.extend([
            ("11_news_bank.py",          "阶段11: 银行新闻判断"),
            ("12_news_fintech.py",       "阶段12: 金融科技新闻判断 + 全量分类结果"),
            ("14_fintech_intensity.py",  "阶段14: 金融科技技术重度评分 (TF-IDF)"),
            ("15_article_policy_alignment.py", "阶段15: 文章级政策语义对齐度"),
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

        # ── 数据流防护：清理未启用的情感分析阶段的残留输出 ──
        # 阶段 24 硬编码读取阶段 23 的输出，若 tone_berts 未启用但
        # 磁盘上残留旧的 23 输出文件，会导致阶段 24 静默读取过期数据。
        _sentiment_output_map = {
            'tone_llms':  CONFIG.get('filenames', {}).get(
                'output_21_tone_llms', '21_tone_llms.parquet'),
            'tone_words': CONFIG.get('filenames', {}).get(
                'output_22_words_tone', '22_words_tone.parquet'),
            'tone_berts': CONFIG.get('filenames', {}).get(
                'output_23_bert_tone', '23_bert_tone.parquet'),
        }
        for method, filename in _sentiment_output_map.items():
            if method not in enabled_methods:
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

        # ── 模块四b：跟风衰减权重 (Tetlock 2011, JF) ──
        stages.append(("24_herd_decay_processor.py", "阶段24: 跟风衰减权重"))

        # ── 模块五：面板数据构建 ──
        stages.append(("45_panel_export_main.py", "阶段40-45: Bank-Year 面板数据构建"))

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

        stage_timeouts = {
            "00_preprocessing.py": 10000,
            "15_article_policy_alignment.py": 7200,  # 含 Embedding API 调用
            "45_panel_export_main.py": 7200,          # 含 Stage 25/26/27 Embedding 计算
        }

        for script, name in stages:
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
                timeout=stage_timeouts.get(script, 3600),
            )
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
