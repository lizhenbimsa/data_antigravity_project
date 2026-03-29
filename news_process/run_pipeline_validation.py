"""
run_pipeline_validation.py — 新闻处理流水线：评估验证模块
===========================================================

功能：
    单独执行流水线的模块四：评估验证模块。
    包含以下阶段（由 config.yaml 中 validation 节点控制）：
      - 阶段31: 阈值敏感性分析        (31_bank_fintech_threshold.py)
      - 阶段32: 人工抽样验证样本生成  (32_news_llms_human.py)
      - 阶段33: 分类有效性评估        (33_news_llms_evaluation.py)
      - 阶段34: 情感三角验证          (34_tone_validation.py)
      - 阶段35: 窗口半径敏感性检验    (35_radius_sensitivity.py)
      - 阶段36: Entity Masking 稳健性测试 (36_entity_masking_test.py)
      - 阶段37: 金融科技词典覆盖率审计  (37_dict_coverage_audit.py)
      - 阶段38: 媒体名称与地域多样性审计 (38_media_diversity.py)
      - 阶段39: Prompt 措辞敏感度测试  (39_prompt_sensitivity.py)

使用方法::

    python run_pipeline_validation.py
"""

import os
import sys
import time
from utils.helpers import load_config, setup_logging, log_memory_usage, run_stage

# ============================================================================
# 配置与初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "run_pipeline_validation"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])


# 脚本所在目录（用于定位阶段脚本）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_validation():
    """执行模块四：评估验证模块。

    流程：
      1. 阶段31: 阈值敏感性分析（由 validation.threshold_sensitivity 控制）
      2. 阶段32: 人工抽样验证样本生成
      3. 阶段33: 分类有效性评估（由 validation.classification_eval 控制）
      4. 阶段34: 情感三角验证（由 validation.sentiment_validation 控制）
      5. 阶段35: 窗口半径敏感性检验（由 validation.radius_sensitivity 控制）
      6. 阶段36: Entity Masking 稳健性测试（由 validation.entity_masking 控制）
      7. 阶段37: 金融科技词典覆盖率审计（由 validation.dict_coverage_audit 控制）
      8. 阶段38: 媒体名称与地域多样性审计（由 validation.media_diversity 控制）
      9. 阶段39: Prompt 措辞敏感度测试（由 validation.prompt_sensitivity 控制）
    """
    module_start = time.time()

    logger.info("=" * 70)
    logger.info("===    模块四：评估验证模块    ===")
    logger.info("=" * 70)
    logger.info("")
    logger.info("  📌 模块目的")
    logger.info("     对前三模块(预处理→分类→情感分析)的全部关键决策进行系统性验证,")
    logger.info("     确保研究结论不受人为参数选择、模型偏差或数据噪声的影响。")
    logger.info("")
    logger.info("  📖 9 个验证阶段说明")
    logger.info("     31: 阈值敏感性 — 分类参数做网格搜索, 证明当前阈值是稳健的")
    logger.info("     32: 人工抽样   — 生成分层随机样本供人工标注比对")
    logger.info("     33: 分类评估   — 计算 Cohen's κ / Krippendorff's α, 量化 LLM 一致性")
    logger.info("     34: 三角验证   — 词典/BERT/LLM 三种方法交叉验证构建效度")
    logger.info("     35: 窗口敏感性 — 检验上下文提取半径对情感度量的影响")
    logger.info("     36: 实体掩码   — 替换银行名验证情感判定不依赖实体先验")
    logger.info("     37: 词典审计   — 金融科技关键词覆盖率和精确度系统审计")
    logger.info("     38: 媒体多样性 — HHI/Shannon/Gini 多维度量化媒体来源与地域覆盖")
    logger.info("     39: 提示词敏感度 — 系统性改写 Prompt 措辞, 量化标注结果的表述稳健性")
    logger.info("")
    logger.info(f"Python: {sys.version}")
    logger.info(f"工作目录: {os.path.dirname(os.path.abspath(__file__))}")
    log_memory_usage(logger, "模块启动")

    # ── 模块四：评估验证模块 ──
    validation_config = CONFIG.get('validation', {})
    stages = []

    if validation_config.get('threshold_sensitivity', True):
        stages.append(("31_bank_fintech_threshold.py", "阶段31: 阈值敏感性分析"))

    stages.append(("32_news_llms_human.py", "阶段32: 人工抽样验证样本生成"))

    if validation_config.get('classification_eval', True):
        stages.append(("33_news_llms_evaluation.py", "阶段33: 分类有效性评估"))

    if validation_config.get('sentiment_validation', True):
        stages.append(("34_tone_validation.py", "阶段34: 情感三角验证"))

    if validation_config.get('radius_sensitivity', True):
        stages.append(("35_radius_sensitivity.py", "阶段35: 窗口半径敏感性检验"))

    if validation_config.get('entity_masking', True):
        stages.append(("36_entity_masking_test.py", "阶段36: Entity Masking 稳健性测试"))

    if validation_config.get('dict_coverage_audit', True):
        stages.append(("37_dict_coverage_audit.py", "阶段37: 金融科技词典覆盖率审计"))

    if validation_config.get('media_diversity', True):
        stages.append(("38_media_diversity.py", "阶段38: 媒体名称与地域多样性审计"))

    if validation_config.get('prompt_sensitivity', True):
        stages.append(("39_prompt_sensitivity.py", "阶段39: Prompt措辞敏感度测试"))

    logger.info(f"评估验证模块共 {len(stages)} 个阶段")
    for i, (script, name) in enumerate(stages, 1):
        logger.info(f"  {i}. {name} ({script})")

    # ── 逐阶段执行 ──
    stage_timings = []
    all_success = True

    for script, name in stages:
        success, elapsed = run_stage(script, name, logger, SCRIPT_DIR)
        stage_timings.append((name, elapsed, success))

        if not success:
            all_success = False
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
        pct = (elapsed / total_elapsed * 100) if total_elapsed > 0 else 0
        status = "✓" if success else "✗"
        if elapsed == 0.0 and success:
            status = "⏭"
        logger.info(f"  {name:<28} {elapsed:>10.1f}s {pct:>9.1f}% {status:>6}")

    logger.info("-" * 70)
    minutes = total_elapsed / 60
    logger.info(f"  {'总计':<28} {total_elapsed:>10.1f}s ({minutes:.1f} 分钟)")
    logger.info("=" * 70)

    log_memory_usage(logger, "模块完成")

    if all_success:
        logger.info("✓ 评估验证模块全部阶段执行成功！")
    else:
        logger.error("✗ 评估验证模块执行中断，请检查日志。")
        sys.exit(1)


if __name__ == "__main__":
    run_validation()
