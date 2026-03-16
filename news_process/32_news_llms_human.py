"""
32_news_llms_human.py — 第三十二阶段：生成人工“金标准”双任务联合验证包
========================================================================

功能：
    从 `21_tone_llms.parquet` 或后续处理文件中抽样（默认 500 条），生成带有
    数据校验(Data Validation)的 Excel 文件，包含人类判定真伪（Verification）和
    人类判定情感（Sentiment）的双重联合标注列。
    
输出：
    一站式标注工作台 Excel 文件：`32_news_llms_human_samples.xlsx`
"""

import os
import time
import numpy as np
import pandas as pd
from utils.helpers import load_config, setup_logging, log_memory_usage, log_stage_summary

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
STRATIFY_BY = HUMAN_VAL_CONFIG.get('stratify_by', ['媒体类型(中文)'])


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
                # Apply validation to the entire dynamic column except header
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
    
    # 优先使用全量 LLM 结果（含 llm_verified=True/False），使分层抽样有效
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
        # 分层抽样尝试
        valid_stratify = [col for col in STRATIFY_BY if col in df.columns]
        if valid_stratify:
            logger.info(f"根据 {valid_stratify} 进行分层抽样")
            try:
                sample_df = df.groupby(valid_stratify, group_keys=False).apply(
                    lambda x: x.sample(int(np.rint(target_sample_size * len(x) / len(df))), random_state=RANDOM_SEED)
                )
                if len(sample_df) < target_sample_size:
                    rem = target_sample_size - len(sample_df)
                    add_df = df.drop(sample_df.index).sample(rem, random_state=RANDOM_SEED)
                    sample_df = pd.concat([sample_df, add_df])
                elif len(sample_df) > target_sample_size:
                    sample_df = sample_df.sample(target_sample_size, random_state=RANDOM_SEED)
            except ValueError as e:
                logger.warning(f"分层抽样失败 ({e})，回退到随机抽样。")
                sample_df = df.sample(n=target_sample_size, random_state=RANDOM_SEED)
        else:
            logger.info("未发现有效的分层字段，执行简单随机抽样")
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
    desired_front = col_names + ['日期', '媒体类型(中文)', '标题', '内容', 'matched_bank_names', 'fintech_keyword_details']
    front_cols = [c for c in desired_front if c in sample_df.columns]
    other_cols = [c for c in sample_df.columns if c not in front_cols]
    sample_df = sample_df[front_cols + other_cols]
    
    # 导出
    output_filename = CONFIG.get('filenames', {}).get('output_32_human_sample', '32_news_llms_human_samples.xlsx')
    output_path = os.path.join(CONFIG["paths"]["output_dir"], output_filename)
        
    logger.info(f"正在保存带有数据校验规则的 Excel: {output_path}")
    
    try:
        import xlsxwriter
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            sample_df.to_excel(writer, sheet_name='验证数据', index=False)
            set_excel_data_validation(writer, '验证数据', sample_df)
    except Exception as e:
        logger.warning(f"写入 xlsxwriter 带验证失败 ({e}), 回退到普通 Excel 写入")
        sample_df.to_excel(output_path, index=False)

    log_stage_summary(logger, STAGE_NAME, stage_start, len(df), len(sample_df))
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


if __name__ == "__main__":
    main()
