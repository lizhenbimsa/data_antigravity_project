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
        xl = pd.ExcelFile(input_path)
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
