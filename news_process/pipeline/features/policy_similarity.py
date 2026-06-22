"""
news_process.pipeline.features.policy_similarity — 权威政策战略响应度多维测算模块
(stage 26; 历史脚本名 26_authoritative_similarity.py, 现无独立 shim, 由 panel runner 调用)
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
核心做法 (fix(omni-g-policy-02/04, 2026-06-11) 口径更新)：
1. 把银行一年的所有新闻碎片拼成一份长篇的“银行年度总结”。
2. 把国家的重磅政策文件（权威语料库）按**发布年份 (vintage)** 切分，年度 t 的
   “标准答案”只拼接发布年份 ≤ t 的文件 — 消除“拿还没出生的政策当标答”的前视构造。
3. 为了保证比对的绝对公平，把这份“标准答案”当成一个虚拟的“幽灵银行”，和所有真实的银行
   放在一模一样的算法标准（同构的字典、相同的主题抽取、超长文本同走 token 分段 +
   均值池化 — 旧注释所称“相同的 8000 字截断”已随 embedding_engine 统一而不存在）下比对。
4. 最终得出 5 个相似度指标（TF-IDF 字符级 / TF-IDF 词级 / LDA 主题 / Embedding 主轨
   / Embedding text2vec 稳健 twin）× Full/Ctx/Ss 三轨：分数越高，说明这家银行的战略
   步调与（截至当年已发布的）国家政策跟得越紧密。
   注: ss 轨 = content_ss (银行+金科同句共现窗, stage 13 物化; 无共现回退全文,
   镜像 ctx); content_ss 缺失时退回 Full/Ctx 两路 (优雅跳过, 不产 _ss 指标列)。
5. 全年份锚点稳健孪生 (2026-06-21, all_vintage_companion 默认开): 在上面 vintage
   "只用当年及以前政策"主轨之外, 再用"所有年份政策文档"拼成的静态标答并列算一套
   完全同结构的 auth_sim_*_allv 指标, 作 anchor-robustness 对照 (含未来政策文本,
   仅稳健性对照, 绝不替换 vintage 主轨)。
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

# fix(omni-g-policy-01/02, 2026-06-11): 权威语料加载/vintage 切分与 stage 15 共用
# 同一实现 (policy_alignment) — 两 stage 消费同一份语料, 锚点口径必须一致:
# (01) 对称归一化 (与新闻侧 normalize 步骤 2.5 同规则: 领导人姓名 '习近平' 简→繁, 体现而非删除);
# (02) vintage-aware 锚点 (年度 t 只用发布年份 ≤ t 的政策文档, 消除前视构造)。
from news_process.pipeline.filtering.policy_alignment import (  # noqa: E402
    all_vintage_companion_enabled,
    load_policy_corpus_docs,
    vintage_anchor_text,
    vintage_aware_enabled,
)

# --- Phase 2a: 取代旧的 importlib 反射 ---
# 共享配置来自 panel/encode (原 41); Stage 25 算法底层来自 features/strategic_diff (原 25)。
from news_process.pipeline.panel.encode import CONFIG, logger  # noqa: E402

# 2026-05-29 双模型: 稳健 twin spec (text2vec local), 经 _build_emb(spec=...) 复用 stage 25 同算法
_ROBUSTNESS_SPEC = CONFIG.get('embedding_robustness', {})


def _ghost_anchor_metrics(texts, n_banks, year, anchor_text, track_suffix):
    """对单一锚点文本计算 5 个 ghost-anchor 相似度指标 (TF-IDF c/w · LDA · emb · emb_t2v)。

    幽灵锚点 (Ghost Anchor): 将 anchor_text 作为 (N+1)-th 元素挂载至银行文本列表末尾,
    送入与 stage 25 绝对同构的 _build_* 矩阵提取器, 取对称矩阵最后一列 sim[:-1, -1]
    即各银行相对该锚点的相似度 (O(1) 同构提取)。

    本助手抽离自原 compute_authoritative_similarity 的逐年内联块 (2026-06-21), 使
    **同一年同一批银行文本**能用不同锚点各算一遍: vintage 主轨 (≤t) 与全年份 `_allv`
    静态锚点共用此助手, 保证两轨下游构造**完全一致**, 唯锚点不同。

    Args:
        texts: 该年度各银行的聚合文本 (长 n_banks)。
        n_banks: 银行数 (= len(texts), 显式传入避免重算)。
        year: 年份 (仅日志)。
        anchor_text: 锚点文本; None → 全 NaN (vintage 前视守卫年份, 该锚点不可用)。
        track_suffix: 日志标签 (如 '_full' / '_full/allv')。

    Returns:
        dict[str, Sequence[float]]: 键 ∈ {tfidf_c, tfidf_w, lda, emb, emb_t2v},
        各值为长 n_banks 的相似度序列 (anchor_text=None 时全 NaN)。
    """
    nan_vec = [np.nan] * n_banks
    if anchor_text is None:
        return {'tfidf_c': list(nan_vec), 'tfidf_w': list(nan_vec),
                'lda': list(nan_vec), 'emb': list(nan_vec),
                'emb_t2v': list(nan_vec)}

    texts_with_auth = texts + [anchor_text]
    n_total = len(texts_with_auth)

    # --- 方法 A/B: TF-IDF 字符级 (char_wb) / 词级 (jieba) ---
    sim_c, _ = _build_tfidf(texts_with_auth, 'char')
    auth_c = sim_c[:-1, -1] if sim_c is not None else list(nan_vec)
    sim_w, _ = _build_tfidf(texts_with_auth, 'word')
    auth_w = sim_w[:-1, -1] if sim_w is not None else list(nan_vec)

    # --- 方法 C: LDA 主题空间 (JSD 散度 → 1 - sqrt(JSD)) ---
    try:
        jsd_mat, _ = _build_lda(texts_with_auth, n_total)
        auth_lda = 1.0 - jsd_mat[:-1, -1]
    except Exception as e:
        logger.warning(f"    LDA ({year}{track_suffix}) 失败: {type(e).__name__}")
        auth_lda = list(nan_vec)

    # --- 方法 D: Semantic Embedding (主轨 text-embedding-3-small) ---
    se_mat, _ = _build_emb(texts_with_auth)
    auth_emb = se_mat[:-1, -1] if se_mat is not None else list(nan_vec)

    # --- 方法 D-t2v: 稳健 twin (text2vec, 同 ghost-anchor 算法只换模型) ---
    # g-policy-05 契约: 稳健轨 raise 不炸 stage, 仅 emb_t2v 置 NaN。
    try:
        se_mat_t2v, _ = _build_emb(texts_with_auth, spec=_ROBUSTNESS_SPEC)
    except Exception as _t2v_exc:
        logger.warning(f"    Embedding t2v ({year}{track_suffix}) 异常: "
                       f"{type(_t2v_exc).__name__}: {_t2v_exc} → emb_t2v 置 NaN")
        se_mat_t2v = None
    auth_emb_t2v = se_mat_t2v[:-1, -1] if se_mat_t2v is not None else list(nan_vec)

    return {'tfidf_c': auth_c, 'tfidf_w': auth_w, 'lda': auth_lda,
            'emb': auth_emb, 'emb_t2v': auth_emb_t2v}


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

    fix(omni-g-policy-02, 2026-06-11) 语义变更: 锚点改为 vintage-aware — 年度 t 的
    “标答”只拼接发布年份 ≤ t 的政策文档 (load_policy_corpus_docs 解析 vintage);
    无 ≤t 文档的年份 auth_sim_* 置 NaN (前视守卫); vintage 不可用时降级静态锚点并披露。

    【白话说明】
    我们怎样判断一家银行是不是在“响应国家号召”？最客观的办法，就是把国家发布的
    “宏观政策原文”当成一个完美的满分标答（也就是这里的虚拟锚点），然后让所有
    银行当年的“新闻汇总”和这个标答去比对。相似度越高，说明这家银行在战略上越贴合国家政策。
    比对只用“当年已经发布”的政策文件 — 2017 年的银行画像不会拿 2022 年才发布的
    规划当标答 (vintage-aware, 见上)。

    【工程实现：幽灵锚点 (Ghost Anchor)】
    为保证与 Stage 25 (同行战略差异度) 采用绝对同构的度量空间，我们将政策文本作为
    (N+1)-th 元素挂载至各年度的银行文本列表中，送入共享底层的 _build_* 矩阵提取器。
    随后仅提取对称矩阵的最后一列切片 `sim[:-1, -1]`，即以 O(1) 逻辑提取了各微观
    银行相对于宏观基准的距离，实现了零冗余且 100% 同构。

    Args:
        df_exploded (pd.DataFrame): 包含新闻原文的文章级数据集
        panel (pd.DataFrame): 准备挂载结果的 Bank-Year 面板数据

    fix(2026-06-21, all_vintage_companion): companion 开启 (默认) 时, 在 vintage 主轨
    之外并列再产一套全年份(静态全语料)锚点指标 auth_sim_*_allv{track} (anchor-robustness
    对照; 含未来政策文本, 绝不替换 vintage 主轨)。逐年 ghost-anchor 计算抽至
    _ghost_anchor_metrics 助手, vintage / 全年份 各调一次 → 下游构造完全一致, 唯锚点不同。

    Returns:
        pd.DataFrame: 合并了至多 15 列 vintage 主轨 权威政策相似度指标的最新 panel
        (5 指标 × Full/Ctx/Ss 三轨; content_ss 缺失时退回 10 列 = 5 指标 × Full/Ctx)。
        all_vintage_companion 开启时再并列至多 15 列 `_allv` 全年份锚点孪生 (同结构),
        合计至多 30 列。
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

    # fix(omni-g-policy-01/02, 2026-06-11): 改经 load_policy_corpus_docs 加载 —
    # 对称归一化 (领导人姓名简→繁) + 按发布年份切分; 静态全语料拼接仅作 vintage 不可用时的降级锚点。
    auth_docs = load_policy_corpus_docs(auth_path)
    auth_text_static = '\n\n'.join(d['text'] for d in auth_docs).strip()

    if not auth_text_static:
        logger.warning("  权威政策语料为空。跳过 Stage 26 计算。")
        return panel

    use_vintage = (vintage_aware_enabled()
                   and any(d['year'] is not None for d in auth_docs))
    if not use_vintage:
        logger.warning(
            "  vintage 前视守卫: 关闭 (opt-out 或语料年份全部未知) → "
            "静态全语料锚点 (含未来政策文本, 前视披露)")

    # 全年份锚点稳健孪生 (2026-06-21): companion 开启时, 在 vintage 主轨之外并列再用
    # 全语料(所有年份)静态锚点 auth_text_static 算一套 auth_sim_*_allv{track} 指标
    # (anchor-robustness; 含未来政策文本, 仅稳健性对照, 绝不替换 vintage 主轨)。
    # vintage 不可用 (use_vintage=False) 时主轨本就 = 静态锚点 → _allv ≡ 主轨 (诚实退化)。
    _companion = all_vintage_companion_enabled()
    if _companion:
        logger.info("  全年份锚点稳健孪生 (_allv): 开启 — 并列产出 auth_sim_*_allv{track} "
                    "(全语料静态锚点, anchor-robustness 对照)")

    # 2. 准备 Full / Ctx / Ss 三轨池化数据
    # fix(completeness-04): full 轨读 content_full(含标题, v3.8.0 full/ctx 命名契约), 与 ctx 轨
    # (content_ctx 含标题) 对称; 原读裸 '内容'(无标题) 致 full↔ctx 不对称 (病根A 同型)。
    # ss 轨 (银行+金科同句): content_ss 由 stage 13 物化 (无共现回退全文 body, 镜像
    # ctx); 缺列优雅跳过 (镜像 ctx 缺列守卫) → 退回 Full/Ctx 两路, 不产 _ss 指标列。
    _full_text_col = 'content_full' if 'content_full' in df_exploded.columns else '内容'
    tracks = [('_full', _aggregate(df_exploded, text_col=_full_text_col))]
    if 'content_ctx' in df_exploded.columns:
        tracks.append(('_ctx', _aggregate(df_exploded, text_col='content_ctx')))
    else:
        logger.info("  未发现 'content_ctx' 列，将仅计算 Full 轨战略响应度。")
    if 'content_ss' in df_exploded.columns:
        tracks.append(('_ss', _aggregate(df_exploded, text_col='content_ss')))
    else:
        logger.info("  未发现 'content_ss' 列 (stage 13 未物化同句共现轨?)，"
                    "将跳过 Ss 轨战略响应度 (镜像 ctx 缺列优雅跳过)。")

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
                # fix(omni-g-policy-05, 2026-06-11): 裸 continue → 显式 warning
                # (镜像 stage 25 同守卫), T=18 早期稀疏年份不再"静默 NaN"无迹可寻
                logger.warning(f"  年度={year}{track_suffix}: 仅 {len(banks)} 家"
                               f"银行, 跳过 auth_sim 计算 (最低要求 3)")
                continue

            n_banks = len(banks)

            # fix(omni-g-policy-02, 2026-06-11): vintage-aware 锚点 — 年度 t 只用
            # 发布年份 ≤ t 的政策文档拼接; 无可用文档 → 该年 auth_sim_* 全 NaN (前视守卫)
            if use_vintage:
                auth_text_vin = vintage_anchor_text(auth_docs, year)
            else:
                auth_text_vin = auth_text_static
            if auth_text_vin is None:
                logger.warning(f"  年度={year}{track_suffix}: 无发布年份 ≤ "
                               f"{year} 的政策文档 (前视守卫), auth_sim_* 置 NaN")
                # companion 关闭时保持原行为: 直接跳过该年 (merge 后留 NaN);
                # companion 开启时不跳过 — 仍要用全年份静态锚点产 _allv (2014 等也出值)。
                if not _companion:
                    continue

            # vintage 主轨指标 (auth_text_vin=None → 全 NaN); 经助手统一同构计算
            vin = _ghost_anchor_metrics(
                texts, n_banks, year, auth_text_vin, track_suffix)
            # 全年份 _allv 孪生 (companion 开启时): 用全语料静态锚点再算一遍 (下游完全一致)。
            # 短路对称 (镜像 stage15 _cosine_for_spec non-vintage 分支 return _wrap(static,static)):
            # 当 vintage 锚点 == 全年份静态锚点 (晚年 ≤t 已含全部政策文档 / use_vintage=False 退化时
            # auth_text_vin==auth_text_static) → allv 与 vin byte-identical, 复用 vin 副本即可, 免重算
            # TF-IDF/LDA/embedding (golden-safe: 同锚点同输入确定性产同值; 生产 T=18 多数年锚点真不同则正常重算)。
            if not _companion:
                allv = None
            elif auth_text_vin is not None and auth_text_vin == auth_text_static:
                allv = {k: list(v) for k, v in vin.items()}
            else:
                allv = _ghost_anchor_metrics(
                    texts, n_banks, year, auth_text_static, f'{track_suffix}/allv')

            # 打包记录 (vintage 主轨 + 可选 _allv 孪生)
            for i, bank in enumerate(banks):
                rec = {
                    'target_bank': bank,
                    'year': year,
                    f'auth_sim_tfidf_c{track_suffix}': float(vin['tfidf_c'][i]),
                    f'auth_sim_tfidf_w{track_suffix}': float(vin['tfidf_w'][i]),
                    f'auth_sim_lda{track_suffix}': float(vin['lda'][i]),
                    f'auth_sim_emb{track_suffix}': float(vin['emb'][i]),
                    f'auth_sim_emb_t2v{track_suffix}': float(vin['emb_t2v'][i]),
                }
                if allv is not None:
                    rec.update({
                        f'auth_sim_tfidf_c_allv{track_suffix}': float(allv['tfidf_c'][i]),
                        f'auth_sim_tfidf_w_allv{track_suffix}': float(allv['tfidf_w'][i]),
                        f'auth_sim_lda_allv{track_suffix}': float(allv['lda'][i]),
                        f'auth_sim_emb_allv{track_suffix}': float(allv['emb'][i]),
                        f'auth_sim_emb_t2v_allv{track_suffix}': float(allv['emb_t2v'][i]),
                    })
                all_results.append(rec)

    # 4. 汇总挂载至 Panel
    if all_results:
        res_df = pd.DataFrame(all_results)
        # 多轨道结果会自动产生相同的 (target_bank, year) 行，必须合并
        res_df = res_df.groupby(['target_bank', 'year'], as_index=False).first()
        
        # 挂载到现有 panel
        panel = panel.merge(res_df, on=['target_bank', 'year'], how='left')
        _n_allv = sum(1 for c in res_df.columns if '_allv' in c)
        logger.info(f"  ✅ 权威政策相似度: 成功合并 {len(res_df)} 行记录 "
                    f"({sum(1 for c in res_df.columns if c.startswith('auth_sim_'))} 指标列, "
                    f"其中 {_n_allv} 列为全年份锚点 _allv 孪生)")
    else:
        logger.warning("  ⚠️ 权威政策相似度: 无任何有效计算结果产出")

    return panel
