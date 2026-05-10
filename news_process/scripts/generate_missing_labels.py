#!/usr/bin/env python3
"""
generate_missing_labels.py - 自动生成缺失的变量标签

用法:
    python scripts/generate_missing_labels.py

输出: stata/15_label_supplementary_full.do
"""

import pandas as pd
import re
import os
from typing import Dict, List, Tuple


def get_labeled_vars() -> set:
    """获取已标注的变量"""
    labeled_vars = set()
    stata_dir = 'stata'

    for f in os.listdir(stata_dir):
        if f.endswith('.do'):
            with open(os.path.join(stata_dir, f), 'r', encoding='utf-8') as file:
                content = file.read()
                matches = re.findall(r'label variable (\S+)', content)
                labeled_vars.update(matches)

    return labeled_vars


def infer_label(var_name: str) -> str:
    """根据变量名推断中文标签"""

    # 基础映射
    track_map = {
        '_full': '(全文)',
        '_ctx': '(上下文)',
        '_title': '(标题)',
    }

    agg_map = {
        '_sum': '总和',
        '_mean': '均值',
        '_std': '标准差',
        '_frac': '占比',
        '_count': '数量',
        'avg_': '平均',
        'sum_': '总',
    }

    weight_map = {
        '_vw': 'VW',
        '_w_': 'VW',
        '_mw': 'MW',
        '_hw': 'HW',
    }

    model_map = {
        'gpt5nano': 'GPT5nano',
        'gemini3': 'Gemini3',
        'grok41': 'Grok4.1',
        'llm': 'LLM',
        'jiang_2021': '江2021',
        'yao_2021': '姚2021',
        'bian_2021': '卞2021',
        'du_2022': '杜2022',
        'you_2018': '尤2018',
        'finbert_cn': 'FinBERT-CN',
        'fin_sent_zh': 'FinSent-ZH',
        'erlangshen': 'Erlangshen',
        'hw2942': 'HW2942',
        'finbert2': 'FinBERT2',
        'bert': 'BERT',
    }

    metric_map = {
        'tone': '情感',
        'cont': '连续情感',
        'conf': '置信度',
        'score': '得分',
        'pos': '正面',
        'neg': '负面',
        'neu': '中性',
        'ratio': '占比',
        'idf': 'IDF',
        'sent_len': '句子长度',
        'ttr': '词汇丰富度',
        'cpw': '每词字符数',
        'msent': '情感强度',
        'tech': '技术类',
        'app': '应用类',
        'prob': '概率',
    }

    # 构建标签
    label_parts = []

    # 识别前缀
    if var_name.startswith('avg_'):
        label_parts.append('平均')
        var_name = var_name[4:]
    elif var_name.startswith('sum_'):
        label_parts.append('总')
        var_name = var_name[4:]

    # 识别模型
    for model_key, model_label in model_map.items():
        if model_key in var_name:
            label_parts.append(model_label)
            break

    # 识别指标类型
    for metric_key, metric_label in metric_map.items():
        if metric_key in var_name:
            label_parts.append(metric_label)

    # 识别聚合类型
    for agg_key, agg_label in agg_map.items():
        if agg_key in var_name and not var_name.startswith('avg_'):
            label_parts.append(agg_label)

    # 识别加权类型
    for weight_key, weight_label in weight_map.items():
        if weight_key in var_name:
            label_parts.append(weight_label)

    # 识别轨道
    track = ''
    for track_key, track_label in track_map.items():
        if var_name.endswith(track_key):
            track = track_label
            break

    # 组合标签
    if label_parts:
        label = ''.join(label_parts) + track
    else:
        # 如果无法推断，使用变量名
        label = var_name.replace('_', ' ') + track

    return label


def generate_label_file():
    """生成完整的补充标签文件"""

    print("=" * 70)
    print("自动生成缺失变量标签")
    print("=" * 70)
    print()

    # 读取面板数据
    df = pd.read_parquet('data/processed/40_panel_yearly.parquet')
    all_vars = set(df.columns)
    print(f"数据集总变量数: {len(all_vars)}")

    # 获取已标注变量
    labeled_vars = get_labeled_vars()
    print(f"已标注变量数: {len(labeled_vars)}")

    # 找出未标注变量
    unlabeled_vars = sorted(all_vars - labeled_vars)
    print(f"未标注变量数: {len(unlabeled_vars)}")
    print()

    # 按类型分组
    groups = {
        'LLM置信度': [],
        'LLM概率分数': [],
        'LLM其他': [],
        '词典比率': [],
        '词典IDF': [],
        '词典其他': [],
        'BERT技术应用': [],
        'BERT聚合': [],
        'BERT其他': [],
        '文本特征': [],
        '聚合统计': [],
        '加权指标': [],
        '其他': [],
    }

    for var in unlabeled_vars:
        if 'conf' in var and any(x in var for x in ['gpt', 'gemini', 'grok', 'llm']):
            groups['LLM置信度'].append(var)
        elif 'prob' in var and any(x in var for x in ['gpt', 'gemini', 'grok', 'llm']):
            groups['LLM概率分数'].append(var)
        elif any(x in var for x in ['gpt', 'gemini', 'grok', 'llm']):
            groups['LLM其他'].append(var)
        elif 'ratio' in var and any(x in var for x in ['jiang', 'yao', 'bian', 'du_', 'you_']):
            groups['词典比率'].append(var)
        elif 'idf' in var and any(x in var for x in ['jiang', 'yao', 'bian', 'du_', 'you_']):
            groups['词典IDF'].append(var)
        elif any(x in var for x in ['jiang', 'yao', 'bian', 'du_', 'you_']):
            groups['词典其他'].append(var)
        elif ('app' in var or 'tech' in var) and 'bert' in var.lower():
            groups['BERT技术应用'].append(var)
        elif var.startswith('bert_avg'):
            groups['BERT聚合'].append(var)
        elif 'bert' in var.lower() or 'erlangshen' in var.lower():
            groups['BERT其他'].append(var)
        elif any(x in var for x in ['sent_len', 'ttr', 'cpw', 'msent']):
            groups['文本特征'].append(var)
        elif any(x in var for x in ['_vw', '_mw', '_hw', '_w_']):
            groups['加权指标'].append(var)
        elif var.startswith('avg_') or var.startswith('sum_'):
            groups['聚合统计'].append(var)
        else:
            groups['其他'].append(var)

    # 生成do文件
    output_file = 'stata/15_label_supplementary_full.do'

    with open(output_file, 'w', encoding='utf-8') as f:
        # 文件头
        f.write('/*' + '=' * 76 + '\n')
        f.write('  文件: 15_label_supplementary_full.do\n')
        f.write('  目的: 补充所有遗漏的变量标签（自动生成）\n')
        f.write('  作者: Claude Code (自动生成)\n')
        f.write('  日期: 2026-05-10\n')
        f.write('\n')
        f.write(f'  说明: 本文件包含 {len(unlabeled_vars)} 个未标注变量的标签\n')
        f.write('=' * 76 + '*/\n\n')

        # 按组生成标签
        section_num = 1
        for group_name, vars_list in groups.items():
            if not vars_list:
                continue

            f.write('* ' + '=' * 76 + '\n')
            f.write(f'* {section_num}. {group_name} ({len(vars_list)}个变量)\n')
            f.write('* ' + '=' * 76 + '\n\n')

            for var in sorted(vars_list):
                label = infer_label(var)
                f.write(f'label variable {var} "{label}"\n')

            f.write('\n')
            section_num += 1

    print(f"[OK] 已生成补充标签文件: {output_file}")
    print()

    # 输出统计
    print("各组变量数量:")
    for group_name, vars_list in groups.items():
        if vars_list:
            print(f"  {group_name}: {len(vars_list)} 个")

    print()
    print("=" * 70)
    print("完成!")
    print("=" * 70)
    print()
    print("下一步:")
    print("1. 检查生成的标签文件: stata/15_label_supplementary_full.do")
    print("2. 运行主控文件: do stata/99_master.do")
    print("3. 验证所有变量都已标注")


if __name__ == "__main__":
    generate_label_file()
