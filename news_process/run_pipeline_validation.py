"""
run_pipeline_validation.py - 新闻处理流水线: 评估验证模块
===========================================================

功能:
    单独执行流水线的模块四: 评估验证模块。
    包含以下阶段(由 config.yaml 中 validation 节点控制):
      - 阶段31:  阈值敏感性分析         (31_bank_fintech_threshold.py)
      - 阶段32:  人工抽样验证样本生成   (32_news_llms_human.py)
      - 阶段32a: 去重阈值敏感性分析     (32a_dedup_threshold_sensitivity.py)
      - 阶段33:  分类有效性评估         (33_news_llms_evaluation.py)
      - 阶段34:  情感三角验证           (34_tone_validation.py)
      - 阶段35:  窗口半径敏感性检验     (35_radius_sensitivity.py)
      - 阶段36:  Entity Masking 稳健性测试 (36_entity_masking_test.py)
      - 阶段37:  金融科技词典覆盖率审计 (37_dict_coverage_audit.py)
      - 阶段38:  媒体名称与地域多样性审计 (38_media_diversity.py)
      - 阶段38a: 时间掩码前视偏误检验   (38a_temporal_mask_test.py)
      - 阶段38b: 距离衰减权重敏感性检验 (38b_decay_sensitivity.py)
      - 阶段39:  Prompt 措词敏感度测试  (39_prompt_sensitivity.py)

设计意图:
    这些验证模块对应经济学顶级期刊审稿中常见的稳健性检验要求:
    - 阈值敏感性(31): 证明结论不依赖特定参数选择
    - 人工标注一致性(32-33): Cohen's κ 和 Krippendorff's α
    - 三角验证(34): 开放科学中的 “方法三角化” 原则
    - 实体掩码(36): Carlson & Burbano (2026, SMJ) LLM 偏差诊断
    - Prompt 敏感度(39): LLM 研究中的表述稳健性检验

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
      2a.阶段32a: 去重阈值敏感性分析（由 validation.dedup_sensitivity 控制）
      3. 阶段33: 分类有效性评估（由 validation.classification_eval 控制）
      4. 阶段34: 情感三角验证（由 validation.sentiment_validation 控制）
      5. 阶段35: 窗口半径敏感性检验（由 validation.radius_sensitivity 控制）
      6. 阶段36: Entity Masking 稳健性测试（由 validation.entity_masking 控制）
      7. 阶段37: 金融科技词典覆盖率审计（由 validation.dict_coverage_audit 控制）
      8. 阶段38: 媒体名称与地域多样性审计（由 validation.media_diversity 控制）
      9. 阶段38a: 时间掩码前视偏误检验（由 temporal_mask_test.enabled 控制）
     10. 阶段38b: 距离衰减权重敏感性检验（始终执行）
     11. 阶段39: Prompt 措辞敏感度测试（由 validation.prompt_sensitivity 控制）
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
    logger.info("  📖 12 个验证阶段说明")
    logger.info("     31:  阈值敏感性  — 分类参数做网格搜索, 证明当前阈值是稳健的")
    logger.info("     32:  人工抽样    — 生成分层随机样本供人工标注比对")
    logger.info("     32a: 去重敏感性  — Jaccard MinHash 多阈值去重, 证明去重参数稳健 (Broder 1997)")
    logger.info("     33:  分类评估    — 计算 Cohen's κ / Krippendorff's α, 量化 LLM 一致性")
    logger.info("     34:  三角验证    — 词典/BERT/LLM 三种方法交叉验证构建效度")
    logger.info("     35:  窗口敏感性  — 检验上下文提取半径对情感度量的影响")
    logger.info("     36:  实体掩码    — 替换银行名验证情感判定不依赖实体先验")
    logger.info("     37:  词典审计    — 金融科技关键词覆盖率和精确度系统审计")
    logger.info("     38:  媒体多样性  — HHI/Shannon/Gini 多维度量化媒体来源与地域覆盖")
    logger.info("     38a: 时间掩码    — 逐步掩码最新N年新闻, 检验前视偏误 (Tetlock 2008)")
    logger.info("     38b: 衰减敏感性  — 比较 uniform/inverse/exponential 权重, 检验结果稳健性")
    logger.info("     39:  提示词敏感度 — 系统性改写 Prompt 措辞, 量化标注结果的表述稳健性")
    logger.info("")
    logger.info(f"Python: {sys.version}")
    logger.info(f"工作目录: {os.path.dirname(os.path.abspath(__file__))}")
    log_memory_usage(logger, "模块启动")

    # ── 模块四: 评估验证模块 ──
    # 每个阶段由 config.yaml 中的 validation.<key> 开关控制:
    #   值为 true(默认) -> 执行
    #   值为 false -> 跳过
    # 这允许研究者根据需要选择性执行耗时较长的验证模块
    validation_config = CONFIG.get('validation', {})
    stages = []

    if validation_config.get('threshold_sensitivity', True):
        stages.append(("31_bank_fintech_threshold.py", "阶段31: 阈值敏感性分析"))

    stages.append(("32_news_llms_human.py", "阶段32: 人工抽样验证样本生成"))

    # 阶段32a: 去重阈值敏感性分析 (Broder 1997, IEEE SEQUENCES)
    # 全量数据 MinHash 运行耗时约 2.5 小时
    # 输出: eval_reports/dedup_sensitivity_report.csv (供论文附录参数稳健性表格)
    if validation_config.get('dedup_sensitivity', True):
        stages.append(("32a_dedup_threshold_sensitivity.py",
                       "阶段32a: 去重阈值敏感性分析"))

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

    # B2-1: 时间掩码前视偏误检验 (Tetlock et al. 2008, JF)
    if CONFIG.get('temporal_mask_test', {}).get('enabled', False):
        stages.append(("38a_temporal_mask_test.py", "阶段38a: 时间掩码前视偏误检验"))

    # G-14: 距离衰减权重敏感性检验 (Sautner et al. 2023, JF)
    stages.append(("38b_decay_sensitivity.py", "阶段38b: 距离衰减权重敏感性检验"))

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
            # Fail-fast: 与主流水线相同的中断策略.
            # 验证模块间存在隐式依赖(如 36 依赖 21 的输出),
            # 因此前置模块失败后续结果无意义。
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
