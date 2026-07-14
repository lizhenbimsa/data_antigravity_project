import pandas as pd
import numpy as np
from pathlib import Path

def fleiss_kappa(ratings, n_categories):
    """
    计算 Fleiss' Kappa 系数
    :param ratings: 形状为 (N, k) 的数组，N 是被评估项目的数量，k 是评估者的数量
                    或者形状为 (N, n_categories) 的数组，表示每个项目被评为某个类别的次数
    :param n_categories: 类别的总数
    """
    ratings = np.asarray(ratings)
    # 输入的是原始评分，需要转换为频数矩阵
    N, k = ratings.shape
    freq_matrix = np.zeros((N, n_categories), dtype=int)
    for i in range(N):
        for j in range(k):
            freq_matrix[i, int(ratings[i, j])] += 1
    
    # 计算 p_j (每个类别被分配的整体比例)
    p_j = freq_matrix.sum(axis=0) / (N * k)

    # 计算 P_i (每个项目上评估者达成一致的程度)
    P_i = (np.sum(freq_matrix**2, axis=1) - k) / (k * (k - 1))

    # 计算 P_bar (P_i 的平均值)
    P_bar = np.mean(P_i)

    # 计算 P_e (期望一致性随机发生的一致性)
    P_e = np.sum(p_j**2)

    # 计算 Kappa
    if P_e == 1:
        # fix(D10, 2026-07-14): 原分支返回裸标量 1.0, 与下方正常路径返回
        # (kappa, P_bar, P_e) 三元组不一致 — 调用方 `k, p_bar, p_e = fleiss_kappa(...)`
        # 解包裸 float 会抛 TypeError ('float' object is not iterable)。P_e==1 意味着
        # 全部评估者对每个项目都给出完全相同的单一分类 (期望一致性已饱和), 该退化情形下
        # P_bar 与 P_e 数学上同为 1.0 (自洽), kappa 按惯例记完全一致 = 1.0 (0/0 不定式的
        # 约定取值), 一并以三元组返回保持接口形状恒定。
        return 1.0, 1.0, 1.0
    kappa = (P_bar - P_e) / (1 - P_e)

    return kappa, P_bar, P_e

try:
    df = pd.read_excel(Path(__file__).resolve().parent / 'data_processed' / 'bank_keywords_20260302_011050.xlsx', sheet_name='判别-金融科技')
    # 提取所有模型评分列
    score_cols = [col for col in df.columns if col.endswith('_score') and col != 'total_score']
    print(f"找到的评分列 ({len(score_cols)} 个):")
    for col in score_cols:
        print(f"  - {col}")
    
    # 构造评分矩阵 ratings 形状为 (N, k) 
    # N = 词语数量, k = 模型数量 (8)
    # 取值为 0 或 1，表示类别总数为 2 (0=非金融科技, 1=金融科技)
    ratings = df[score_cols].values
    
    # 保证所有的值都在 0, 1 之间且没有缺失值
    ratings = np.nan_to_num(ratings, 0)
    ratings = np.clip(ratings, 0, 1)

    k, p_bar, p_e = fleiss_kappa(ratings, n_categories=2)
    print(f"\n--- Fleiss' Kappa 计算结果 ---")
    print(f"N (词语总数): {ratings.shape[0]}")
    print(f"k (模型数量): {ratings.shape[1]}")
    print(f"P_bar (实际观测一致性): {p_bar:.4f}")
    print(f"P_e (偶然预期一致性): {p_e:.4f}")
    print(f"Fleiss' Kappa 系数: {k:.4f}")
    
except Exception as e:
    print(f"Error: {e}")
