"""
news_process.validation.text2vec — 基于 text2vec 的稳健性检验模块与数据双轨验证方案

迁移说明 (Phase 7b)：
    本模块由原 root script ``30_robustness_text2vec.py`` body 迁入。
    规范调用方式: ``python -m news_process.validation.text2vec``

================================================================================

本文件实现了 Data Dual-Track Perfection 方案。
对 全文本（Full Text）与 上下文切片（Context）两条数据流同时进行特征张量提取，
产出独立于主线的稳健性指标。

核心特征：
- 战略差异度 (Strategic Differentiation): strat_diff_t2v_full / strat_diff_t2v_ctx
- 权威政策相似度 (Policy Authoritative Proximity): policy_cosine_sim_t2v_full / policy_cosine_sim_t2v_ctx

【学术机制 (Academic Mechanism)】
本模块基于“数据双轨” (Dual-Track) 范式，以局部静态文本向量 (Local Static Embedding) 对抗动态 LLM 生成的主线数据，构建“方法论防火墙”。
- 权威政策相似度依据 Hassan et al. (2019, QJE) 的文本相似度锚定法（Distance-to-Anchor），度量微观企业对宏观政策指令的响应程度。
- 战略差异度依据 Hoberg & Phillips (2016, JPE) 及 Guzman & Li (2023) 的行业质心距离法，度量企业在金融网络中的离群性（Outlierness）。

【通俗应用 (Layman's Terms)】
简而言之，本代码相当于一个“交叉检查”裁判。它不依赖外部 API（如 GPT/Gemini），而是用本地纯数理模型，在“全文”和“切片”两组文本上重新算一遍：
1. 某银行的话术离“官方政策”有多近？（权威响应）
2. 某银行的话术离“行业平均水平”有多远？（战略差异）
以此来证明我们的核心结论并非由于特定大模型的某种偏好所导致。

【方法论演变与学术辩护 (Methodological Evolution & Academic Defense)】
- 演变背景：主流文献多依赖单一字典或单一预训练语言模型（如 FinBERT），面临严重的样本外泛化性衰减（Out-of-sample Decay）与大模型独有的“幻觉敏感性”。引入本地轻量级 Text2Vec 构建第二轨道（Dual-Track），不仅对齐了 Guzman & Li (2023) 的静态高维映射范式，更为大模型动态生成的特征提供了零方差（Zero-variance）的基准锚点。
- 前置假设条件 (A Priori Assumptions)：采用分块均值池化（Chunk Mean Pooling）隐含假设金融科技信息在长文本中的分布是相对均匀且可加和的（Additive Compositionality），即局部的语义切片平均后能有效表征全局宏观语境。
- 潜在局限性 (Potential Limitations)：Text2Vec 模型的原生最大上下文通常受限于 512 Tokens，即便通过 Chunking 切块缓解了 OOM（Out-Of-Memory）溢出，但其由于缺乏跨块注意力（Cross-chunk Attention），无法像 Claude 3 / GPT-4 一样捕获长篇幅内极度隐晦的因果倒装或嵌套转折逻辑。这正是保留 LLM 主轨与 Text2Vec 辅轨对照的原因。
"""

import os
import sys
import time
import math
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Phase 7b: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 news_process/validation/text2vec.py 出发, 上溯 2 层抵达项目父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import setup_logging
from news_process.core.reporting import save_dataset

CONFIG = load_config()
STAGE_NAME = "30_robustness_text2vec"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

class LocalEmbeddingEngine:
    """本地 OOM 防御与分块均值池化 (Chunk Mean Pooling) 引擎"""
    def __init__(self, model_name='shibing624/text2vec-base-chinese', max_tokens=512):
        logger.info(f"加载本地 Embedding 模型: {model_name}")
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
        except ImportError:
            logger.error("未安装 sentence_transformers，无法初始化 LocalEmbeddingEngine")
            raise
        self.max_tokens = max_tokens
        
    def encode_with_chunk_pooling(self, texts, batch_size=32):
        if not texts:
            return np.array([])
            
        all_embeddings = []
        dim = self.model.get_sentence_embedding_dimension()
        
        n_texts = len(texts)
        logger.info(f"开始推断 {n_texts} 条文本...")
        
        for i in range(0, n_texts, batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_embs = []
            
            for text in batch_texts:
                if not isinstance(text, str) or not text.strip():
                    batch_embs.append(np.zeros(dim))
                    continue
                    
                # 粗略按字符分块，1 token 约对应 1.5~2 汉字
                chunk_size = int(self.max_tokens * 1.5)
                chunks = [text[j:j+chunk_size] for j in range(0, len(text), chunk_size)]
                
                try:
                    # 分块池化
                    chunk_vectors = self.model.encode(chunks, show_progress_bar=False)
                    mean_vec = np.mean(chunk_vectors, axis=0)
                    batch_embs.append(mean_vec)
                except Exception as e:
                    logger.warning(f"OOM 熔断或异常 ({e})，返回零向量")
                    batch_embs.append(np.zeros(dim))
                    
            all_embeddings.extend(batch_embs)
            if (i + batch_size) % (batch_size * 10) == 0:
                logger.info(f"  已处理 {i + batch_size} / {n_texts}")
                
        return np.array(all_embeddings)

def main():
    stage_start = time.time()
    logger.info("=" * 60)
    logger.info("阶段启动: 30_robustness_text2vec (双轨联合测算引擎)")
    logger.info("=" * 60)
    
    output_dir = CONFIG['paths']['output_dir']
    input_path = os.path.join(output_dir, '14_fintech_intensity.parquet')
    
    if not os.path.exists(input_path):
        logger.error(f"输入文件缺失: {input_path}")
        return
        
    logger.info("加载 14_fintech_intensity.parquet ...")
    df = pd.read_parquet(input_path)
    # 强制重置索引，杜绝因上游导致重复索引引发的 .loc 布尔掩码赋值错位或广播失败
    df = df.reset_index(drop=True)

    # Step 3b 修复 (致命缺陷 D1): 上游 14 不输出 content_ctx 列, 复用
    # tone_llms._materialize_content_ctx 物化上下文 (与 prompt_sensitivity.py 同模式),
    # 避免 _ctx 轨道在 L162-165 被静默 skip 致使列永久缺失、Step 5 必然 raise.
    if 'content_ctx' not in df.columns:
        from news_process.pipeline.sentiment.tone_llms import _materialize_content_ctx
        logger.info("content_ctx 列缺失, 调用 _materialize_content_ctx 物化上下文 ...")
        df = _materialize_content_ctx(df)
        logger.info(f"content_ctx 物化完成, df 列数: {len(df.columns)}")

    # 1. [时序修复] 载入后使用 pd.to_datetime(df['日期']).dt.year 从底层规避 KeyError
    if 'year' not in df.columns and '日期' in df.columns:
        df['year'] = pd.to_datetime(df['日期'], errors='coerce').dt.year
        logger.info("已修复 'year' 时序特征。")
        
    # 载入权威政策文本 (使用 utf-8-sig 免疫 BOM 零宽字符乱码)
    # Phase 1 重构: 优先读取 CONFIG['paths']['authoritative_corpus_file']。
    auth_path = CONFIG['paths'].get(
        'authoritative_corpus_file',
        os.path.join(os.path.dirname(__file__), 'config', 'authoritative_corpus.txt'),
    )
    auth_text = ""
    if os.path.exists(auth_path):
        with open(auth_path, 'r', encoding='utf-8-sig') as f:
            auth_text = '\n'.join([line for line in f if not line.strip().startswith('#')]).strip()
    
    if not auth_text:
        logger.warning("未找到有效权威政策文本。")
        
    engine = LocalEmbeddingEngine()
    
    # 编码权威锚点
    auth_vec = None
    if auth_text:
        logger.info("正在编码权威政策锚点...")
        auth_vec = engine.encode_with_chunk_pooling([auth_text])[0]
        
    # 双轨配置 (容错实际列名: 正文/内容)
    full_col = '内容' if '内容' in df.columns else '正文'
    ctx_col = 'content_ctx' if 'content_ctx' in df.columns else 'context'
    
    tracks = [
        ('_full', full_col),
        ('_ctx', ctx_col)
    ]
    
    for suffix, col_name in tracks:
        if col_name not in df.columns:
            logger.warning(f"数据轨 '{suffix}' 的目标列 '{col_name}' 不存在，跳过。")
            continue
            
        logger.info(f"=== 开始处理轨道: {suffix} (列: {col_name}) ===")
        texts = df[col_name].fillna('').astype(str).tolist()
        
        # 2. 计算篇章级张量
        if len(texts) == 0:
            logger.warning(f"轨道 {suffix} 文本数为 0，跳过推断。")
            continue
            
        embs = engine.encode_with_chunk_pooling(texts)
        
        # 识别有效文本（非空），强制转换为 str 以防止 .str 访问器在混合类型列上引发 AttributeError
        valid_mask = df[col_name].fillna('').astype(str).str.strip() != ''

        # 4. 计算政策锚点余弦相似度: policy_cosine_sim_t2v_full/ctx
        # 【学术机制】Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019).
        # Firm-Level Political Risk: Measurement and Effects. The Quarterly Journal of Economics, 134(4), 2135-2202.
        # DOI: 10.1093/qje/qjz021
        # 推导逻辑：通过预设的外生权威锚点 (Exogenous Anchor)，计算各文档向量与其在余弦空间中的夹角。
        # 【通俗应用】量化每篇新闻对官方政策指导文件（如央行发文）的跟随紧密度。
        df[f'policy_cosine_sim_t2v{suffix}'] = np.nan
        if auth_vec is not None and len(embs) > 0:
            # np.tile 效率低，直接算内积更优
            auth_vec_2d = auth_vec.reshape(1, -1)
            sims = cosine_similarity(embs, auth_vec_2d).flatten()
            # 仅对有效文本赋值，空文本保持 NaN 避免 0.0 污染
            # 强制使用 .values 提取底层 Numpy 数组进行索引，规避 Pandas Series 引发的新版 Numpy 广播异常
            df.loc[valid_mask, f'policy_cosine_sim_t2v{suffix}'] = sims[valid_mask.values]
        else:
            df[f'policy_cosine_sim_t2v{suffix}'] = np.nan
            
        # 3. 计算行业质心距离: strat_diff_t2v_full/ctx
        # 【学术机制】Hoberg, G., & Phillips, G. (2016). Text-Based Network Industries and Endogenous Product Differentiation.
        # Journal of Political Economy, 124(5), 1423-1465. DOI: 10.1086/688176
        # Kelly, B., Papanikolaou, D., Seru, A., & Taddy, M. (2021). Measuring Technological Innovation over the Long Run.
        # American Economic Review: Insights, 3(3), 303-320. DOI: 10.1257/aeri.20190499
        # 推导逻辑：在跨年度横截面上，先计算年度维度下全体企业文本向量的均值质心（Centroid），
        # 然后测量单一观测值到质心的距离 (1.0 - Cosine Similarity)，用以捕捉其非同质化倾向。
        # 【通俗应用】量化某条新闻与当年“行业大众脸（平均水平）”的差异度，值越接近 1 说明越“特立独行”。
        df[f'strat_diff_t2v{suffix}'] = np.nan
        for year in df['year'].dropna().unique():
            mask = df['year'] == year
            # 仅使用当年有效文本计算行业质心，避免零向量拉低质心均值
            year_valid_mask = mask & valid_mask
            # 强制使用 .values 提取 Numpy 布尔数组以策安全
            year_embs_valid = embs[year_valid_mask.values]
            
            if len(year_embs_valid) > 0:
                centroid = np.mean(year_embs_valid, axis=0, keepdims=True)
                y_sims = cosine_similarity(year_embs_valid, centroid).flatten()
                y_dists = np.clip(1.0 - y_sims, 0.0, 1.0)
                # 仅将距离赋值给有效文本，空文本保持 NaN
                df.loc[year_valid_mask, f'strat_diff_t2v{suffix}'] = y_dists
                
        logger.info(f"轨道 {suffix} 计算完成。")
        
    # 5. 按 ['target_bank', 'year'] 聚合平均
    logger.info("按 Bank-Year 聚合平均...")
    agg_cols = {}
    for suffix, _ in tracks:
        c1 = f'strat_diff_t2v{suffix}'
        c2 = f'policy_cosine_sim_t2v{suffix}'
        if c1 in df.columns:
            agg_cols[c1] = 'mean'
        if c2 in df.columns:
            agg_cols[c2] = 'mean'
            
    if not agg_cols:
        logger.error("无指标生成，退出。")
        return
        
    panel = df.groupby(['target_bank', 'year'], as_index=False).agg(agg_cols)
    
    out_path = os.path.join(output_dir, '30_text2vec_indicators.parquet')
    input_file = os.path.join(cfg['paths']['output_dir'],
                              cfg['filenames']['output_21_tone_llms'])
    save_dataset(panel, out_path, logger,
                stage_name="30_robustness_text2vec",
                config=cfg,
                input_files=[input_file])
    
    elapsed = time.time() - stage_start
    logger.info(f"--- 阶段 30_robustness_text2vec 完成 (耗时 {elapsed:.1f} 秒) ---")

if __name__ == '__main__':
    main()
