"""
news_process.validation.llms_human — 阶段32：生成人工“金标准”双任务联合验证包

迁移说明 (Phase 7b)：
    本模块由原 root script ``32_news_llms_human.py`` body 迁入。
    规范调用方式: ``python -m news_process.validation.llms_human``

========================================================================

功能：
    从 `21_tone_llms.parquet` 或后续处理文件中进行简单随机抽样（默认 500 条），
    生成带有数据校验(Data Validation)的 Excel 文件，包含人类判定真伪（Verification）
    和人类判定情感（Sentiment）的双重联合标注列。
    
输出：
    一站式标注工作台 Excel 文件：`32_news_llms_human_samples.xlsx`

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 32_news_llms_human.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**职责**: stage 21 LLM 投票结果的人工"金标准"采样器 —— 抽一批文章给人类编码员复核, 产出可直接填写的 Excel 工作台, 是 stage 33/34 效标效度评估的上游。

**输入 (三级回退, 取第一个存在者)**: ① `21_tone_llms_full.parquet` (config.filenames.output_21_tone_llms_full) → ② `23_bert_tone.parquet` (output_23_bert_tone) → ③ `21_tone_llms.parquet` (output_21_tone_llms)。三者皆缺则 logger.error 并 return (不抛异常)。

**处理步骤** (`main()`):
- `load_config()` 读 `human_validation.sample_size` (默认 500) / `random_seed` (默认 42)。
- 简单随机抽样 `df.sample(n=min(SAMPLE_SIZE,len(df)), random_state=RANDOM_SEED)`; 行数 ≤ 目标量则全选 (`df.copy()`)。确定性由固定 seed 保证。
- 追加 4 个空标注列: `编码者A_验证`/`编码者B_验证` (取值 1/0 = 真/伪) + `编码者A_情感`/`编码者B_情感` (正面/中性/负面)。初值均为空字符串 `''`。
- 列重排: 把 4 个标注列 + 关键展示列 (日期/媒体类型(中文)/标题/内容/target_bank/co_mentioned_banks/fintech_keyword_details, 取存在者) 提到最前。
- 用 `xlsxwriter` 写 Excel (sheet 名 `验证数据`), 并经 `set_excel_data_validation()` 对验证列下拉锁定为 {'1','0'}、情感列锁定为 {正面,中性,负面} (动态范围 行2:行10000); 引擎不可用/写盘异常时回退普通 `to_excel`。

**合并函数 `merge_annotations()`** (编码完成后手动调用): 读回填好的 xlsx, 逐行比对两编码者 —— 验证/情感各自: 两人皆有效且一致 → 写共识 `最终_验证`/`最终_情感`; 分歧 → 写哨兵 (`最终_验证`=-1, `最终_情感`='待仲裁'); 另加空 `裁定备注` 列; 输出 `*_merged.xlsx` + 一致率/分歧数/待仲裁数日志。这些哨兵正是 stage 33 评估时要剔除的 attrition。⚠ **该 merge 子命令仅经模块入口可达** —— `python -m news_process.validation.llms_human merge [in.xlsx] [out.xlsx]` (模块 `__main__` 解析 argv[1]=='merge'); 根 shim `32_news_llms_human.py` 的 `__main__` 只调 `main()` 且不透传 argv, 故 `python 32_news_llms_human.py merge` **不会** 触发合并 (只会跑抽样)。

**关键算法/公式**: 无统计计算, 核心是确定性随机抽样 (pandas `df.sample` + 固定 random_state) + Excel 数据校验下拉规则。

**外部依赖**: pandas / numpy / xlsxwriter (写校验下拉) / openpyxl (回退路径与 merge 读 xlsx)。无 LLM/Embedding API 调用, 无 _llm_cache.db, 无网络, $0。

**DAG 位置**: 验证支线 stage 32, 上游 = stage 21 (LLM) / 23 (BERT) 的文章级产出; 下游 = stage 33 (`llms_evaluation.main` 读 32 产出的填好 Excel 算 precision/recall/κ)。shim 仅 `sys.path` 注入后 `from ...llms_human import main; main()`, 零业务逻辑。

■ 白话说明

这一步是"出考卷": 从全部新闻里随机抽 500 篇 (固定随机种子, 每次抽的都一样), 做成一张 Excel 表 (默认文件名 32_news_llms_human_samples.xlsx) 发给两位人工编码员, 让他们逐篇判断 ①这条新闻是不是真的银行金融科技新闻 ②它的语气是正面/中性/负面。表格里的判断列被锁成下拉菜单, 防止有人手滑填错格式。

为什么需要它: 流水线主要靠 AI 大模型 (LLM) 给每篇新闻打标签, 但我们必须证明"机器打的标签跟人判断的一致", 否则审稿人不信。这张人工答卷就是后面给机器打分用的"标准答案"。编码员填完后, 还有个合并环节把两人的答案对齐 (一致就采纳, 吵架就标"待仲裁")—— 注意这个合并要用模块入口 `python -m news_process.validation.llms_human merge` 触发, 直接跑根脚本带 merge 参数是无效的。

对最终结果的影响: 它本身不直接进银行-年度面板, 也不改任何论文数字。但它的抽样质量决定了 stage 33/34 算出的"机器准确率/κ 一致性"可不可信 —— 抽得有代表性, 验证结论才站得住; 抽偏了 (比如全抽到容易判的), 会高估机器水平。
========================================================================
"""

import os
import sys
import time

import numpy as np
import pandas as pd

# Phase 7b: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 news_process/validation/llms_human.py 出发, 上溯 2 层抵达项目父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import log_memory_usage, log_stage_summary, setup_logging

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "32_news_llms_human"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 读取配置
HUMAN_VAL_CONFIG = CONFIG.get('human_validation', {})
SAMPLE_SIZE = HUMAN_VAL_CONFIG.get('sample_size', 500)
RANDOM_SEED = HUMAN_VAL_CONFIG.get('random_seed', 42)


def set_excel_data_validation(writer, sheet_name, df, start_row=1):
    """
    为生成的 Excel 文件设置 Data Validation，避免人类标注重格式随意。
    """
    try:
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        # 定义验证格式
        validate_verif = {
            'validate': 'list',
            'source': ['1', '0'] # 1=真, 0=伪
        }
        
        validate_senti = {
            'validate': 'list',
            'source': ['正面', '中性', '负面']
        }
        
        # 寻找对应的列索引
        col_names = list(df.columns)
        
        # 获取字母列号 (A, B, C...)
        def get_col_letter(idx):
            res = ""
            while idx >= 0:
                res = chr((idx % 26) + 65) + res
                idx = (idx // 26) - 1
            return res
            
        for name in ['编码者A_验证', '编码者B_验证']:
            if name in col_names:
                idx = col_names.index(name)
                col_letter = get_col_letter(idx)
                # 对整列动态范围 (表头除外) 应用数据校验
                worksheet.data_validation(f'{col_letter}2:{col_letter}10000', validate_verif)
        
        for name in ['编码者A_情感', '编码者B_情感']:
            if name in col_names:
                idx = col_names.index(name)
                col_letter = get_col_letter(idx)
                worksheet.data_validation(f'{col_letter}2:{col_letter}10000', validate_senti)
                
    except Exception as e:
        logger.warning(f"设置 Excel 数据验证失败，但不影响结果生成: {e}")

def main():
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")

    # 功能说明 banner — 写入 <stage>.log, 让日志自带阶段用途说明 (仿 39c)。
    logger.info("=" * 72)
    logger.info("阶段 32: LLM×人工金标准采样器 (人工抽样验证样本生成; criterion validity 上游)")
    logger.info("=" * 72)
    logger.info(f"【功能】从全部新闻里随机抽一批文章 (本次 SAMPLE_SIZE={SAMPLE_SIZE} 篇, 受 config 控制), 做成可直接")
    logger.info("        填写的 Excel 标注工作台 (sheet=验证数据), 发给两位人工编码员逐篇判定")
    logger.info("        ①是否真银行金科新闻 (验证 1/0) ②语气 (正面/中性/负面)。")
    logger.info("        产出 = 人工'标准答案'考卷, 是 stage 33/34 评 LLM 精度/κ 的上游 (本阶段不进面板)。")
    logger.info(
        f"【方法】简单随机抽样 df.sample(n=min({SAMPLE_SIZE},N), random_state={RANDOM_SEED}); "
        "固定种子保证逐位可复现。"
    )
    logger.info("        追加 4 空标注列 + 关键展示列提到最前; xlsxwriter 写下拉数据校验 (验证锁{1,0}/")
    logger.info("        情感锁{正面,中性,负面}), 引擎不可用时回退普通 to_excel。无统计计算。")
    logger.info("【判读】抽样代表性是 stage 33/34 结论可信度的前提: 抽偏 (全抽易判篇) 会高估机器水平;")
    logger.info("        抽样率应≈目标量/总量, 全选 (N≤目标量) 时下游金标准覆盖度受限须披露。")
    logger.info("【确定性】纯 CPU, 无 LLM/Embedding/网络调用, $0; 固定 random_state → 逐位可复现。")

    # 优先使用全量 LLM 结果
    input_filename = CONFIG.get('filenames', {}).get('output_21_tone_llms_full', '21_tone_llms_full.parquet')
    input_path = os.path.join(CONFIG["paths"]["output_dir"], input_filename)
    
    # 退回到已过滤版本
    if not os.path.exists(input_path):
        input_filename = CONFIG.get('filenames', {}).get('output_23_bert_tone', '23_bert_tone.parquet')
        input_path = os.path.join(CONFIG["paths"]["output_dir"], input_filename)
    
    # 再退回到 tone_llms
    if not os.path.exists(input_path):
        input_filename = CONFIG.get('filenames', {}).get('output_21_tone_llms', '21_tone_llms.parquet')
        input_path = os.path.join(CONFIG["paths"]["output_dir"], input_filename)
        
    if not os.path.exists(input_path):
        logger.error(f"无法找到可作为抽样源的 parquet 文件: {input_path}")
        return
        
    logger.info(f"加载数据以供抽样: {input_path}")
    df = pd.read_parquet(input_path)
    logger.info(f"总数据量: {len(df)}")
    log_memory_usage(logger, "数据加载后")
    
    # 抽样
    target_sample_size = min(SAMPLE_SIZE, len(df))
    logger.info(f"计划抽样数量: {target_sample_size} (基于随机种子 {RANDOM_SEED})")
    
    if len(df) <= target_sample_size:
        sample_df = df.copy()
        logger.info("数据量少于或等于目标抽样量，直接全选。")
    else:
        # 全样本简单随机抽样
        logger.info("执行简单随机抽样")
        sample_df = df.sample(n=target_sample_size, random_state=RANDOM_SEED)

    # 追加人工标注“一站式”作业台的四列
    # 新规定：用 1/0 代表真假，直接用中文表示情感
    col_names = [
        '编码者A_验证', '编码者B_验证', '编码者A_情感', '编码者B_情感'
    ]
    sample_df = sample_df.copy()
    for col in col_names:
        sample_df[col] = ''
    
    # 重排列表将验证列放在标题与内容之前，让标注者第一眼就能填
    desired_front = col_names + ['日期', '媒体类型(中文)', '标题', '内容', 'target_bank', 'co_mentioned_banks', 'fintech_keyword_details']
    front_cols = [c for c in desired_front if c in sample_df.columns]
    other_cols = [c for c in sample_df.columns if c not in front_cols]
    sample_df = sample_df[front_cols + other_cols]
    
    # 导出
    output_filename = CONFIG.get('filenames', {}).get('output_32_human_sample', '32_news_llms_human_samples.xlsx')
    output_path = os.path.join(CONFIG["paths"]["output_dir"], output_filename)
        
    logger.info(f"正在保存带有数据校验规则的 Excel: {output_path}")
    
    try:
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            sample_df.to_excel(writer, sheet_name='验证数据', index=False)
            set_excel_data_validation(writer, '验证数据', sample_df)
    except Exception as e:
        logger.warning(f"写入 xlsxwriter 带验证失败 ({e}), 回退到普通 Excel 写入")
        sample_df.to_excel(output_path, index=False)

    # 结果分析 — 写入日志: 抽样源/抽样率/标注列就绪情况 + 判读 (仿 39c)。
    # crash-guard: 本块仅"读数据算计数+打日志", 不写盘/不改产物 (Excel 已于上方落盘);
    # 但仍整体包 try/except, 防未来取数异常 (如缺列/空 Series) 冒泡崩掉阶段、误伤 golden-safe 性质。
    try:
        n_total = len(df)
        n_sample = len(sample_df)
        sample_frac = (n_sample / n_total * 100) if n_total > 0 else 0.0
        full_select = n_total <= target_sample_size  # 全选 (未真正抽样) 标记
        # 展示列就绪度: desired_front 里真正落入 Excel 的关键列 (供编码员判读用)
        display_present = [c for c in front_cols if c not in col_names]
        n_display = len(display_present)
        n_display_expected = 7  # 日期/媒体类型(中文)/标题/内容/target_bank/co_mentioned_banks/fintech_keyword_details

        logger.info("-" * 72)
        logger.info("【结果分析】人工金标准考卷已生成 (抽样代表性 → 下游 stage 33/34 结论可信度):")
        logger.info(
            f"  抽样源 = {input_filename} (三级回退取第一存在者: 21_full → 23_bert → 21_tone_llms)"
        )
        logger.info(
            f"  总语料 N = {n_total:,} 篇; 目标抽样量 = {target_sample_size} (config SAMPLE_SIZE={SAMPLE_SIZE})"
        )
        if n_total == 0:
            # NaN/空数据 guard: 空语料时不落进抽样率方向判读 (否则除零/恒为 0 误判)
            logger.warning("  ⚠ 总语料 N=0 (无有效数据): 无样本可抽, 跳过抽样率判读; 请检查抽样源是否为空。")
        elif full_select:
            logger.warning(
                f"  ⚠ 全选: N({n_total:,}) ≤ 目标量({target_sample_size}), 未真正随机抽样 → "
                "抽样率=100%; 盘面 T=2 小语料下属预期, 全量 17M 不会触发。"
            )
        else:
            logger.info(
                f"  实际抽样 = {n_sample:,} 篇, 抽样率 = {sample_frac:.2f}% "
                f"(简单随机, random_state={RANDOM_SEED}, 逐位可复现)"
            )
            # 仅作记录: 抽样率 = 实际抽样量/总量, 由 .sample(n=target) 构造保证抽样量恒等于目标量
            # (故抽样率与目标占比恒相等, 非代表性检验)。⚠ 本行不下'无偏'结论 —— 抽样量等于请求量
            # 是构造性事实, 并未检验样本在银行/年份/媒体维度上是否代表总体; 代表性须 stage 33/34 实测。
            logger.info(
                "    判读: 抽样量=配置目标量 (由 df.sample(n=) 构造保证); "
                "此处仅记录抽样规模, 维度代表性 (银行/年份/媒体) 不在本阶段检验。"
            )
        logger.info(
            f"  标注列 = {len(col_names)}/4 就绪 ({', '.join(col_names)}, 初值空待人工回填)"
        )
        if n_display < n_display_expected:
            logger.warning(
                f"  ⚠ 展示列 {n_display}/{n_display_expected} 就绪 (实有: {display_present}); "
                "缺列会降低编码员判读上下文, 但不影响抽样确定性。"
            )
        else:
            logger.info(
                f"  展示列 {n_display}/{n_display_expected} 就绪 ({display_present}) → 编码员上下文充分。"
            )
        logger.info(f"  产出 Excel = {output_path} (sheet=验证数据, 验证/情感列已锁下拉; 不进面板, golden 无关)")
        logger.info(
            "  ⚠ 本阶段只产'考卷'不算指标: 精度/κ 在 stage 33 评; 抽样若偏 (全抽易判篇) 会高估机器水平。"
        )
        if n_sample < 50:
            logger.warning(
                f"  ⚠ 样本仅 {n_sample} 篇 (盘面 T=2 小样本): 仅验证管道正确性, "
                "criterion validity 结论以全量 17M/T=18 实测为准。"
            )
        logger.info("-" * 72)
    except Exception as _e:
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")

    log_stage_summary(logger, STAGE_NAME, stage_start, len(df), len(sample_df))
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


# ============================================================================
# 3. 人工标注合并（编码完成后使用）
# ============================================================================

def merge_annotations(input_path: str = None, output_path: str = None):
    """合并两位编码者的人工判定，生成黄金标准列。

    合并规则：
      - 一致：取共识值写入 ``最终_验证`` / ``最终_情感``
      - 分歧：标记为 ``待仲裁``（验证列写 -1，情感列写 "待仲裁"）

    同时生成合并统计摘要（一致率、分歧条目数），供研究者参考。

    Args:
        input_path:  已标注的 Excel 文件路径。默认自动从配置读取。
        output_path: 合并后的输出文件路径。默认在同目录生成 ``_merged`` 后缀文件。
    """
    merge_start = time.time()
    logger.info(f"--- 开始人工标注合并 ---")

    # 解析路径
    if input_path is None:
        input_filename = CONFIG.get('filenames', {}).get(
            'output_32_human_sample', '32_news_llms_human_samples.xlsx'
        )
        input_path = os.path.join(CONFIG["paths"]["output_dir"], input_filename)

    if not os.path.exists(input_path):
        logger.error(f"标注文件未找到: {input_path}")
        return

    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_merged{ext}"

    # 读取已标注数据
    logger.info(f"读取标注文件: {input_path}")
    try:
        # fix(2026-06-19 run-check F5 兄弟泄漏): with 上下文确保 ExcelFile 句柄关闭 (消除 ResourceWarning)
        with pd.ExcelFile(input_path) as xl:
            sheet_name = '验证数据' if '验证数据' in xl.sheet_names else xl.sheet_names[0]
            df = pd.read_excel(xl, sheet_name=sheet_name)
    except Exception as e:
        logger.error(f"读取标注文件失败: {e}")
        return

    logger.info(f"共 {len(df)} 条标注记录")

    # --- 合并验证判定 ---
    ver_a_col, ver_b_col = '编码者A_验证', '编码者B_验证'
    final_ver_col = '最终_验证'

    if ver_a_col in df.columns and ver_b_col in df.columns:
        df[ver_a_col] = pd.to_numeric(df[ver_a_col], errors='coerce')
        df[ver_b_col] = pd.to_numeric(df[ver_b_col], errors='coerce')

        both_valid = df[ver_a_col].notna() & df[ver_b_col].notna()
        agree_mask = both_valid & (df[ver_a_col] == df[ver_b_col])
        disagree_mask = both_valid & (df[ver_a_col] != df[ver_b_col])

        df[final_ver_col] = np.nan
        df.loc[agree_mask, final_ver_col] = df.loc[agree_mask, ver_a_col]
        df.loc[disagree_mask, final_ver_col] = -1  # 待仲裁标记

        n_agree_ver = int(agree_mask.sum())
        n_disagree_ver = int(disagree_mask.sum())
        n_total_ver = int(both_valid.sum())
        agree_rate_ver = n_agree_ver / n_total_ver * 100 if n_total_ver > 0 else 0

        logger.info(f"[验证] 合并完成: 一致={n_agree_ver}, 分歧={n_disagree_ver}, "
                     f"一致率={agree_rate_ver:.1f}%")
    else:
        logger.warning(f"未找到验证判定列（{ver_a_col}, {ver_b_col}），跳过验证合并")

    # --- 合并情感判定 ---
    sen_a_col, sen_b_col = '编码者A_情感', '编码者B_情感'
    final_sen_col = '最终_情感'

    if sen_a_col in df.columns and sen_b_col in df.columns:
        df[sen_a_col] = df[sen_a_col].astype(str).str.strip()
        df[sen_b_col] = df[sen_b_col].astype(str).str.strip()

        # 将空字符串和 'nan' 视为缺失
        for col in [sen_a_col, sen_b_col]:
            df.loc[df[col].isin(['', 'nan', 'None']), col] = np.nan

        both_valid_sen = df[sen_a_col].notna() & df[sen_b_col].notna()
        agree_mask_sen = both_valid_sen & (df[sen_a_col] == df[sen_b_col])
        disagree_mask_sen = both_valid_sen & (df[sen_a_col] != df[sen_b_col])

        df[final_sen_col] = pd.array([pd.NA] * len(df), dtype='object')
        df.loc[agree_mask_sen, final_sen_col] = df.loc[agree_mask_sen, sen_a_col]
        df.loc[disagree_mask_sen, final_sen_col] = '待仲裁'

        n_agree_sen = int(agree_mask_sen.sum())
        n_disagree_sen = int(disagree_mask_sen.sum())
        n_total_sen = int(both_valid_sen.sum())
        agree_rate_sen = n_agree_sen / n_total_sen * 100 if n_total_sen > 0 else 0

        logger.info(f"[情感] 合并完成: 一致={n_agree_sen}, 分歧={n_disagree_sen}, "
                     f"一致率={agree_rate_sen:.1f}%")
    else:
        logger.warning(f"未找到情感判定列（{sen_a_col}, {sen_b_col}），跳过情感合并")

    # --- 添加裁定备注列（如不存在） ---
    if '裁定备注' not in df.columns:
        df['裁定备注'] = ''

    # --- 输出 ---
    try:
        df.to_excel(output_path, index=False)
        logger.info(f"合并结果已保存: {output_path}")
    except Exception as e:
        logger.error(f"保存合并结果失败: {e}")
        return

    # 统计摘要
    logger.info("--- 合并统计摘要 ---")
    if final_ver_col in df.columns:
        pending_ver = int((df[final_ver_col] == -1).sum())
        logger.info(f"  验证: 待仲裁 {pending_ver} 条")
    if final_sen_col in df.columns:
        pending_sen = int((df[final_sen_col] == '待仲裁').sum())
        logger.info(f"  情感: 待仲裁 {pending_sen} 条")

    elapsed = time.time() - merge_start
    logger.info(f"--- 标注合并完毕 (耗时 {elapsed:.1f}s) ---")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'merge':
        # 用法: python 32_news_llms_human.py merge [input.xlsx] [output.xlsx]
        inp = sys.argv[2] if len(sys.argv) > 2 else None
        out = sys.argv[3] if len(sys.argv) > 3 else None
        merge_annotations(inp, out)
    else:
        main()
