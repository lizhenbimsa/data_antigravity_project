#!/usr/bin/env python3
"""
批量生成所有缺失变量的Stata标签
"""

import pandas as pd
import re
import os

# 读取未标注变量列表
with open('unlabeled_vars_final.txt', 'r', encoding='utf-8') as f:
    unlabeled_vars = [line.strip() for line in f if line.strip()]

print(f'需要生成标签的变量数: {len(unlabeled_vars)}')

# 定义标签推断规则
def infer_label(var):
    """根据变量名推断中文标签"""

    # 轨道映射
    if var.endswith('_full'):
        track = '(全文)'
    elif var.endswith('_ctx'):
        track = '(上下文)'
    elif var.endswith('_title'):
        track = '(标题)'
    else:
        track = ''

    # 模型映射
    models = {
        'gpt54nano': 'GPT5nano',
        'gemini31111': 'Gemini3',
        'deepseekv4': 'Grok4.1',
        'jiang_2021': '江2021',
        'yao_2021': '姚2021',
        'bian_2021': '卞2021',
        'du_2022': '杜2022',
        'you_2018': '尤2018',
        'finbert_cn': 'FinBERT-CN',
        'fin_sent_zh': 'FinSent-ZH',
        'erlangshen': 'Erlangshen',
        'hw2942': 'HW2942',
    }

    # 指标映射
    metrics = {
        'tone': '情感',
        'cont': '连续情感',
        'conf': '置信度',
        'score': '得分',
        'prob': '概率',
        'pos': '正面',
        'neg': '负面',
        'neu': '中性',
        'ratio': '占比',
        'count': '数量',
        'idf': 'IDF',
        'sent_len': '句子长度',
        'ttr': '词汇丰富度',
        'cpw': '每词字符数',
        'msent': '情感强度',
    }

    # 聚合映射
    aggs = {
        'avg_': '平均',
        'sum_': '总',
        '_sum': '总和',
        '_mean': '均值',
        '_std': '标准差',
    }

    # 加权映射
    weights = {
        '_hw': 'HW',
        '_mw': 'MW',
        '_vw': 'VW',
        '_w_': 'VW',
    }

    # 分类映射
    cats = {
        '_tech': '技术类',
        '_app': '应用类',
        '_desc': '描述性',
        '_sub': '实质性',
    }

    # 构建标签
    parts = []

    # 前缀聚合
    for agg_key, agg_val in aggs.items():
        if var.startswith(agg_key):
            parts.append(agg_val)
            break

    # 模型
    for model_key, model_val in models.items():
        if model_key in var:
            parts.append(model_val)
            break

    # 指标
    for metric_key, metric_val in metrics.items():
        if metric_key in var:
            parts.append(metric_val)
            break

    # 分类
    for cat_key, cat_val in cats.items():
        if cat_key in var:
            parts.append(cat_val)
            break

    # 加权
    for weight_key, weight_val in weights.items():
        if weight_key in var:
            parts.append(weight_val)
            break

    # 后缀聚合
    for agg_key, agg_val in aggs.items():
        if agg_key.startswith('_') and var.endswith(agg_key + track.replace('(', '').replace(')', '')):
            if agg_val not in parts:
                parts.append(agg_val)
            break

    label = ''.join(parts) + track

    # 如果标签为空，使用变量名
    if not parts:
        label = var.replace('_', ' ') + track

    return label

# 按类型分组
groups = {}
for var in unlabeled_vars:
    # 确定分组
    if any(x in var for x in ['gpt54nano', 'gemini31111', 'deepseekv4']) and 'conf' in var:
        group = 'LLM置信度指标'
    elif any(x in var for x in ['gpt54nano', 'gemini31111', 'deepseekv4']) and 'prob' in var:
        group = 'LLM概率指标'
    elif any(x in var for x in ['gpt54nano', 'gemini31111', 'deepseekv4']):
        group = 'LLM情感指标'
    elif any(x in var for x in ['jiang', 'yao', 'bian', 'du_', 'you_']) and 'ratio' in var:
        group = '词典比率指标'
    elif any(x in var for x in ['jiang', 'yao', 'bian', 'du_', 'you_']) and 'idf' in var:
        group = '词典IDF指标'
    elif any(x in var for x in ['jiang', 'yao', 'bian', 'du_', 'you_']):
        group = '词典情感指标'
    elif 'bert' in var.lower() and ('tech' in var or 'app' in var):
        group = 'BERT技术应用指标'
    elif 'bert' in var.lower():
        group = 'BERT情感指标'
    elif any(x in var for x in ['sent_len', 'ttr', 'cpw', 'msent']):
        group = '文本特征指标'
    elif any(x in var for x in ['_hw', '_mw', '_vw', '_w_']):
        group = '加权指标'
    elif var.startswith('avg_') or var.startswith('sum_'):
        group = '聚合统计指标'
    else:
        group = '其他指标'

    if group not in groups:
        groups[group] = []
    groups[group].append(var)

# 生成do文件
output_file = 'stata/16_label_complete.do'

with open(output_file, 'w', encoding='utf-8') as f:
    f.write('/*' + '=' * 76 + '\n')
    f.write('  文件: 16_label_complete.do\n')
    f.write('  目的: 补充所有剩余未标注的变量标签（自动生成）\n')
    f.write('  作者: Claude Code\n')
    f.write('  日期: 2026-05-10\n')
    f.write('\n')
    f.write(f'  说明: 本文件包含 {len(unlabeled_vars)} 个未标注变量的标签\n')
    f.write('=' * 76 + '*/\n\n')

    section = 1
    for group_name, vars_list in sorted(groups.items()):
        f.write('* ' + '=' * 76 + '\n')
        f.write(f'* {section}. {group_name} ({len(vars_list)}个)\n')
        f.write('* ' + '=' * 76 + '\n\n')

        for var in sorted(vars_list):
            label = infer_label(var)
            f.write(f'label variable {var} "{label}"\n')

        f.write('\n')
        section += 1

print(f'[OK] 已生成: {output_file}')
print(f'[OK] 共生成 {len(unlabeled_vars)} 个变量标签')
print()
print('各组统计:')
for group_name, vars_list in sorted(groups.items()):
    print(f'  {group_name}: {len(vars_list)} 个')
