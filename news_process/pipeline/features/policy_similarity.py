"""
26_authoritative_similarity.py — 权威政策战略响应度多维测算模块
============================================================================

【学术支撑 (Academic Foundation)】
本模块严格基于 Hoberg & Phillips (2016, JPE) 以及 Guzman & Li (2023, MS)
确立的“先聚合后向量化 (Pool-then-Vectorize)”文本空间范式。企业战略定位本质上是
Firm-Year 级别的结构化特征。通过汇总该年度单家企业的全部碎片化披露，
消除文章级的特质性白噪音 (Idiosyncratic Noise)，构建“企业年度战略画像”。
同时，依据 Hassan et al. (2019, QJE) 测度宏观风险/政策暴露度的核心逻辑，
将宏观《权威政策文本》注入同构特征空间，测度微观画像与宏观基准的收敛性。

相关支撑文献:
- Brown, S. V., & Tucker, J. W. (2011). Large-sample evidence on firms' year-over-year
  MD&A modifications. Journal of Accounting Research, 49(2), 309-346.
  https://doi.org/10.1111/j.1475-679X.2010.00396.x
- Hassan, T. A., et al. (2019). Firm-level political risk: Measurement and effects.
  The Quarterly Journal of Economics, 134(4), 2135-2202.
  https://doi.org/10.1093/qje/qjz021

【白话说明 (Plain Language)】
任务目标：衡量一家银行在特定年份，其战略方向与国家的“金融科技宏观政策”有多贴合。
核心做法：
1. 把银行一年的所有新闻碎片拼成一份长篇的“银行年度总结”。
2. 把国家的 6 份重磅政策文件（权威语料库）视为一份“终极标准答案”。
3. 为了保证比对的绝对公平，把这份“标准答案”当成一个虚拟的“幽灵银行”，和所有真实的银行
   放在一模一样的算法标准（如同构的字典、相同的主题抽取、相同的 8000 字截断）下比对。
4. 最终得出 4 种算法的“相似度评分”，分数越高，说明这家银行的战略步调与国家政策跟得越紧密。
============================================================================
"""

import os

import numpy as np
import pandas as pd

from news_process.pipeline.features.strategic_diff import (  # noqa: E402
    _aggregate_bank_year_texts as _aggregate,
)
from news_process.pipeline.features.strategic_diff import (
    _build_embedding_sim_matrix as _build_emb,
)
from news_process.pipeline.features.strategic_diff import (
    _build_lda_jsd_matrix as _build_lda,
)
from news_process.pipeline.features.strategic_diff import (
    _build_tfidf_sim_matrix as _build_tfidf,
)

# --- Phase 2a: 取代旧的 importlib 反射 ---
# 共享配置来自 panel/encode (原 41); Stage 25 算法底层来自 features/strategic_diff (原 25)。
from news_process.pipeline.panel.encode import CONFIG, logger  # noqa: E402

# 2026-05-29 双模型: 稳健 twin spec (text2vec local), 经 _build_emb(spec=...) 复用 stage 25 同算法
_ROBUSTNESS_SPEC = CONFIG.get('embedding_robustness', {})

# ============================================================================
# 核心计算函数
# ============================================================================

def compute_authoritative_similarity(df_exploded, panel):
    """
    计算基于权威政策的战略响应度 (Authoritative Policy Strategic Alignment)。

    【学术基础】
    本模块的测度范式严格依据以下顶刊文献的 "Text-based Anchor Vectorization" 框架构建：
    - Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level
      political risk: Measurement and effects. The Quarterly Journal of Economics,
      134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
      (注 [锚点勘误 2026-06-10]: Hassan et al. 2019 仅提供"将宏观政策文本嵌入与微观企业
       共享向量空间"的概念动因; 其 firm-level political risk 实为窗口 bigram 频率, 并非
       "微观向量与宏观锚向量的余弦相似度"。本模块实际采用的 cosine-to-anchor 操作化
       归功于下方 Hoberg & Phillips (2016) / Guzman & Li (2023), 勿将余弦公式归 Hassan。)
    - Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous
      product differentiation. Journal of Political Economy, 124(5), 1423-1465.
      https://doi.org/10.1086/688176
      (注: 沿用其高维 TF-IDF 文本相似度矩阵提取与产品空间定位方法论)

    【白话说明】
    我们怎样判断一家银行是不是在“响应国家号召”？最客观的办法，就是把国家发布的
    “宏观政策原文”当成一个完美的满分标答（也就是这里的虚拟锚点），然后让所有
    银行当年的“新闻汇总”和这个标答去比对。相似度越高，说明这家银行在战略上越贴合国家政策。

    【工程实现：幽灵锚点 (Ghost Anchor)】
    为保证与 Stage 25 (同行战略差异度) 采用绝对同构的度量空间，我们将政策文本作为
    (N+1)-th 元素挂载至各年度的银行文本列表中，送入共享底层的 _build_* 矩阵提取器。
    随后仅提取对称矩阵的最后一列切片 `sim[:-1, -1]`，即以 O(1) 逻辑提取了各微观
    银行相对于宏观基准的距离，实现了零冗余且 100% 同构。

    Args:
        df_exploded (pd.DataFrame): 包含新闻原文的文章级数据集
        panel (pd.DataFrame): 准备挂载结果的 Bank-Year 面板数据

    Returns:
        pd.DataFrame: 合并了 10 列权威政策相似度指标的最新 panel (5 指标 × Full/Ctx 双轨)
    """
    logger.info("=" * 60)
    logger.info("开始计算: 权威政策战略响应度 (Stage 26)")
    logger.info("=" * 60)

    # 1. 载入权威政策文本锚点 (Phase 2a: 通过 CONFIG['paths'][...] 解析)
    auth_path = CONFIG['paths'].get(
        'authoritative_corpus_file',
        os.path.join(os.path.dirname(__file__), 'config', 'authoritative_corpus.txt'),
    )
    if not os.path.exists(auth_path):
        logger.warning(f"  找不到权威政策语料: {auth_path}。跳过 Stage 26 计算。")
        return panel

    with open(auth_path, 'r', encoding='utf-8') as f:
        auth_lines = [line for line in f if not line.strip().startswith('#')]
        auth_text = '\n'.join(auth_lines).strip()
    
    if not auth_text:
        logger.warning("  权威政策语料为空。跳过 Stage 26 计算。")
        return panel

    # 2. 准备 Full 轨与 Ctx 轨池化数据
    # fix(completeness-04): full 轨读 content_full(含标题, v3.8.0 两轨契约), 与 ctx 轨
    # (content_ctx 含标题) 对称; 原读裸 '内容'(无标题) 致 full↔ctx 不对称 (病根A 同型)。
    _full_text_col = 'content_full' if 'content_full' in df_exploded.columns else '内容'
    tracks = [('_full', _aggregate(df_exploded, text_col=_full_text_col))]
    if 'content_ctx' in df_exploded.columns:
        tracks.append(('_ctx', _aggregate(df_exploded, text_col='content_ctx')))
    else:
        logger.info("  未发现 'content_ctx' 列，将仅计算 Full 轨战略响应度。")

    all_results = []

    # 3. 逐轨、逐年计算
    for track_suffix, agg_df in tracks:
        if agg_df.empty:
            continue
            
        logger.info(f"  正在处理轨道 {track_suffix}...")
        
        for year in sorted(agg_df['year'].unique()):
            dy = agg_df[agg_df['year'] == year]
            banks = dy['target_bank'].tolist()
            texts = dy['agg_text'].tolist()
            
            # 如果当年的银行数过少，跳过（为保持与 Stage 25 LDA K值的最小计算稳定性一致）
            if len(banks) < 3:
                continue
                
            # 【极简同构映射】: 将政策文本挂载至列表末尾，构成 (N+1) 全集
            texts_with_auth = texts + [auth_text]
            n_banks = len(banks)
            n_total = len(texts_with_auth)
            
            # --- 方法 A: TF-IDF 字符级 (char_wb) ---
            # sim_c 为 (N+1)x(N+1) 的相似度对称矩阵 (对角线为 NaN)
            # 提取最后一列 [:-1, -1] 即各银行与政策的相似度
            sim_c, _ = _build_tfidf(texts_with_auth, 'char')
            auth_c = sim_c[:-1, -1] if sim_c is not None else [np.nan] * n_banks
            
            # --- 方法 B: TF-IDF 词级 (jieba) ---
            sim_w, _ = _build_tfidf(texts_with_auth, 'word')
            auth_w = sim_w[:-1, -1] if sim_w is not None else [np.nan] * n_banks
            
            # --- 方法 C: LDA 主题空间 (JSD 散度) ---
            try:
                # 距离转换为相似度: 1 - sqrt(JSD)
                jsd_mat, _ = _build_lda(texts_with_auth, n_total)
                auth_lda = 1.0 - jsd_mat[:-1, -1]
            except Exception as e:
                logger.warning(f"    LDA ({year}) 失败: {type(e).__name__}")
                auth_lda = [np.nan] * n_banks
                
            # --- 方法 D: Semantic Embedding (主轨, text-embedding-3-small) ---
            se_mat, _ = _build_emb(texts_with_auth)
            if se_mat is not None:
                auth_emb = se_mat[:-1, -1]
            else:
                auth_emb = [np.nan] * n_banks

            # --- 方法 D-t2v: 稳健 twin (text2vec, 同 ghost-anchor 算法只换模型) ---
            se_mat_t2v, _ = _build_emb(texts_with_auth, spec=_ROBUSTNESS_SPEC)
            if se_mat_t2v is not None:
                auth_emb_t2v = se_mat_t2v[:-1, -1]
            else:
                auth_emb_t2v = [np.nan] * n_banks

            # 打包记录
            for i, bank in enumerate(banks):
                all_results.append({
                    'target_bank': bank,
                    'year': year,
                    f'auth_sim_tfidf_c{track_suffix}': float(auth_c[i]),
                    f'auth_sim_tfidf_w{track_suffix}': float(auth_w[i]),
                    f'auth_sim_lda{track_suffix}': float(auth_lda[i]),
                    f'auth_sim_emb{track_suffix}': float(auth_emb[i]),
                    f'auth_sim_emb_t2v{track_suffix}': float(auth_emb_t2v[i]),
                })

    # 4. 汇总挂载至 Panel
    if all_results:
        res_df = pd.DataFrame(all_results)
        # 多轨道结果会自动产生相同的 (target_bank, year) 行，必须合并
        res_df = res_df.groupby(['target_bank', 'year'], as_index=False).first()
        
        # 挂载到现有 panel
        panel = panel.merge(res_df, on=['target_bank', 'year'], how='left')
        logger.info(f"  ✅ 权威政策相似度: 成功合并 {len(res_df)} 行记录")
    else:
        logger.warning("  ⚠️ 权威政策相似度: 无任何有效计算结果产出")

    return panel
