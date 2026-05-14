"""v7 灰度验证样本采样 (R8-K 5+3+2 分布)

从 21_tone_llms.parquet v6 输出中抽取 10 行用于 v7 prompt 灰度验证。
不进入 git commit (临时工具)。

采样原则 (R8-K, 第 8 轮审查):
  A 组 (5 样本): v6 = '实质性' + 含具体数据
                  关键测试 - v7 W&Z 框架下含数据但 PR 包装的样本是否被重判为 'symbolic'?
                  期望: 1-3 样本翻 symbolic; 若 >4 说明 W&Z 过严
  B 组 (3 样本): v6 = '描述性' + 含口号词
                  期望: 全部 v7 仍判 symbolic
  C 组 (2 样本): v6 = '描述性' + 含具体数据
                  期望: 边缘案例; 用作人工抽查核心

输出: news_process/data/processed/gray_v7_samples.csv
"""
import re
import pandas as pd

INPUT  = 'news_process/data/processed/21_tone_llms.parquet'
OUTPUT = 'news_process/data/processed/gray_v7_samples.csv'

# 启发式 1: 含具体数据 (数字 + 量词)
HAS_DATA = re.compile(r'\d+(\.\d+)?\s*(亿|万|百万|百分点|%|笔|户|家|个|台)')
# 启发式 2: 含口号词
SLOGAN = re.compile('|'.join(['布局', '打造', '推进', '积极探索', '致力于', '拥抱', '迈向', '赋能']))


def main():
    df = pd.read_parquet(INPUT)
    print(f"v6 parquet 总行数: {len(df)}; 列数: {len(df.columns)}")

    # v6 schema: text_type 列名仍存在 (parquet 是 v6 重跑前的)
    if 'text_type' not in df.columns:
        # v7 重跑后已是 innovation_substantiveness, 用新列名
        tt_col = 'innovation_substantiveness'
    else:
        tt_col = 'text_type'
    print(f"使用列: {tt_col}")

    verified = df[df.get('llm_verified_full', True) == True].copy()
    print(f"verified=True 行数: {len(verified)}")

    text_col = '内容' if '内容' in verified.columns else 'content'
    verified['has_data'] = verified[text_col].fillna('').astype(str).str.contains(HAS_DATA, regex=True)
    verified['has_slogan'] = verified[text_col].fillna('').astype(str).str.contains(SLOGAN, regex=True)

    # R8-K 5+3+2 采样
    pool_a = verified[(verified[tt_col] == '实质性') & verified['has_data']]
    pool_b = verified[(verified[tt_col] == '描述性') & verified['has_slogan']]
    pool_c = verified[(verified[tt_col] == '描述性') & verified['has_data']]
    print(f"采样池 A (sub+data): {len(pool_a)} | B (desc+slogan): {len(pool_b)} | C (desc+data): {len(pool_c)}")

    g_a = pool_a.sample(n=min(5, len(pool_a)), random_state=42).assign(group='A_sub_data')
    g_b = pool_b.sample(n=min(3, len(pool_b)), random_state=42).assign(group='B_desc_slogan')
    g_c = pool_c.sample(n=min(2, len(pool_c)), random_state=42).assign(group='C_desc_data')

    samples = pd.concat([g_a, g_b, g_c])
    title_col = '标题' if '标题' in samples.columns else 'title'
    cat_col = 'innovation_locus' if 'innovation_locus' in samples.columns else 'fintech_category'

    out_cols = ['target_bank', title_col, text_col, tt_col, cat_col, 'group']
    out_cols = [c for c in out_cols if c in samples.columns]
    samples[out_cols].to_csv(OUTPUT, index=False, encoding='utf-8-sig')
    print(f"\n采样完成: {len(samples)} 行 (A={len(g_a)} B={len(g_b)} C={len(g_c)})")
    print(f"输出: {OUTPUT}")


if __name__ == '__main__':
    main()
