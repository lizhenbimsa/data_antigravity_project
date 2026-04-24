"""
25_strategic_differentiation.py — 金融科技战略差异度指数
=======================================================

改进 A: 构建基于文本距离的"金融科技战略差异度指数"
      (FinTech Strategic Differentiation Score)

论文依据 (核心公式映射):
  严格映射 Guzman & Li (2023, MS) Section 3 "From similarity to founding
  strategy" 中关于计算企业文本表述的余弦相似度并聚合至最近竞争者的规则:

      Ŝ_i = (1/N) Σ_{j ∈ J_i^N} δ_ij
      (Guzman & Li 2023, MS, Eq. in §3; 本模块 N=5 为基准, N=3~7 为敏感性检验)

  其中:
    - δ_ij = 1 - cosine_similarity(TF-IDF_i, TF-IDF_j) 为银行 i 与银行 j
      之间的文本距离
    - J_i^N 为银行 i 在文本向量空间中的 N 个最近邻集合
    - Ŝ_i 值越大, 表明银行 i 的金融科技战略与同业差异越大, 即占据更独特的
      "战略生态位" (strategic niche)

  Hoberg & Phillips (2016, JPE, §III) 原始框架使用 10-K 产品描述构建
  Text-based Network Industry Classifications (TNIC), 本模块将其迁移至
  银行金融科技新闻文本场景, 将每家银行的年度新闻聚合文档视为其"产品描述"
  的代理变量。

预期的边际贡献 / 解决的内生性问题:
  引入该指数作为全新的分析维度。将所有银行当年的金融科技新闻文本聚合,
  并计算其与其他所有银行的 TF-IDF (及 LDA+JSD / Embedding) 文本相似度,
  通过测度每家银行在向量空间中与其最近的几家同业的文本"距离", 能够揭示
  银行业金融科技创新的战略生态位。这解决了当前研究中粗颗粒度加权方法
  (单纯比拼新闻数量和情感得分) 所带来的内生性问题 — 数量和情感指标
  容易受银行规模、媒体关注度等混杂因素驱动, 而文本距离度量的是战略内容
  本身的差异性, 能更精准地分离出差异化战略所带来的超额边际贡献。

本模块实现基于新闻文本的银行战略差异度量化框架, 核心思路是:
  1. 按 (银行, 年度) 聚合新闻文本 → 构建 "企业-年" 文档
  2. 使用多种文本表征方法 (TF-IDF / LDA / Embedding) 计算银行间文本距离
  3. 对每家银行取 N-最近邻 (N=3~7) 的平均距离作为差异度指标 → Ŝ_i
  4. 计算 Fluidity (市场流动性) 衡量竞争环境变化速度

方法论来源:
  - [核心] 创业战略度量: Guzman, J., & Li, A. (2023). Measuring founding
    strategy. Management Science, 69(1), 101–118.
    https://doi.org/10.1287/mnsc.2022.4369
    → Section 3: 余弦相似度 + N-最近邻聚合公式, 本模块的核心算法来源
  - [核心] 文本产品空间: Hoberg, G., & Phillips, G. (2016). Text-based
    network industries and endogenous product differentiation. Journal of
    Political Economy, 124(5), 1423–1465. https://doi.org/10.1086/688176
    → §III: TNIC 框架, 逐年重建文本相似度矩阵的方法论基础
  - 产品市场流动性: Hoberg, G., Phillips, G., & Prabhala, N. (2014). Product
    market threats, payouts, and financial flexibility. The Journal of Finance,
    69(1), 293–324. https://doi.org/10.1111/jofi.12050
    → Eq. 2: Fluidity 指标定义, 衡量竞争环境动态变化
  - 文本创新度量: Bellstam, G., Bhagat, S., & Cookson, J. A. (2021). A
    text-based analysis of corporate innovation. Management Science, 67(7),
    4004–4031. https://doi.org/10.1287/mnsc.2020.3682
  - JSD 距离: Lin, J. (1991). Divergence measures based on the Shannon
    entropy. IEEE Transactions on Information Theory, 37(1), 145–151.
    https://doi.org/10.1109/18.61115
  - 句向量表征: Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence
    embeddings using Siamese BERT-networks. Proceedings of EMNLP 2019,
    3982–3992. https://doi.org/10.18653/v1/D19-1410
  - LDA 主题模型: Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent
    Dirichlet allocation. Journal of Machine Learning Research, 3, 993–1022.
    https://www.jmlr.org/papers/v3/blei03a.html
  - 文本数据方法论: Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as
    data. Journal of Economic Literature, 57(3), 535–574.
    https://doi.org/10.1257/jel.20181020

输出列 (18 列, 值域均为 [0, 1]):
  strat_diff_n{3..7}       TF-IDF char N-近邻差异度 (Ŝ_i, N=3~7)
  strat_diff_n{3..7}_w     TF-IDF jieba 词级 N-近邻差异度 (稳健性检验)
  strat_sim_max / _w       最大同行相似度 (max cosine sim to any peer)
  strat_fluidity / _w      市场流动性 (Hoberg et al. 2014, Eq. 2)
  strat_diff_n5_lda        LDA+JSD N=5 差异度 (主题分布距离, 稳健性检验)
  strat_sim_max_lda        LDA+JSD 最大同行相似度
  strat_diff_n5_emb        Embedding N=5 差异度 (稠密语义距离, 稳健性检验)
  strat_sim_max_emb        Embedding 最大同行相似度

局限性:
  1. 原始文献 (Hoberg & Phillips 2016) 使用企业自有 10-K 披露文本,
     本项目使用第三方新闻报道, 测量的是"媒体感知差异"而非"自我披露差异"
  2. 银行样本量 (~54 家/年) 远小于 TNIC 数据集 (~5000 家/年),
     N=5 近邻占样本比例 ~10%, 需注意小样本偏差
  3. Embedding 输入截断为 8000 字符, 可能丢失超长文本的尾部信息
"""
# ── 导入依赖库 ──
# 【白话】下面这些 import 就是"引入工具箱":
#   - numpy/pandas: 数据处理的基础工具，类似 Excel 的高级版
#   - jieba: 中文分词器，能把"银行金融科技"切成"银行""金融""科技"
#   - TfidfVectorizer: 把文本转成数字向量（想象成把文章变成坐标点）
#   - cosine_similarity: 计算两个向量的"方向相似度"（0=完全不同, 1=完全相同）
#   - LDA: 主题模型，自动发现文本中隐藏的"话题"（如"移动支付""区块链"）
#   - jensenshannon: 衡量两个概率分布有多不同的数学工具
import os, logging, asyncio
import numpy as np, pandas as pd, jieba
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import LatentDirichletAllocation
from scipy.spatial.distance import jensenshannon
import importlib.util as _iu

# --- 从 41 导入共享配置 ---
# 【白话】项目的"总开关"配置（数据路径、模型参数等）统一在 41 号文件里管理，
#   这里把它读进来，所有模块共用同一套设置，避免各自为政。
_p41 = os.path.join(os.path.dirname(__file__), '41_panel_encode_aggregate.py')
_s41 = _iu.spec_from_file_location('_41', _p41)
_m41 = _iu.module_from_spec(_s41); _s41.loader.exec_module(_m41)
logger = _m41.logger; CONFIG = _m41.CONFIG
LLM_CONFIG = CONFIG.get('tone_llm_processing', {})

# 中文停用词表 — 排除高频虚词以提高 TF-IDF 区分度
# 【白话】"的""了""在"这些词几乎每篇文章都有，不能帮我们区分不同银行，
#   所以要去掉，只保留有实际含义的词（如"区块链""风控""支付"）。
# 参考: Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data.
# Journal of Economic Literature, 57(3), 535–574.
# https://doi.org/10.1257/jel.20181020
_STOPWORDS = {'的', '了', '在', '是', '和', '与', '为', '对', '等',
              '将', '也', '及', '到', '从', '中', '上', '下', '不'}


def _jieba_tokenizer(text: str) -> list[str]:
    """jieba 中文分词器, 过滤单字和停用词。

    【白话】把一段中文文本切成一个个词语，然后：
      - 扔掉单个字（如"的""了"），因为单字没啥意义
      - 扔掉停用词（如"和""在"），只保留有意义的词
    例如: "银行的金融科技" → ["银行", "金融", "科技"]
    """
    return [w for w in jieba.lcut(text) if len(w) >= 2 and w not in _STOPWORDS]


def _l2_normalize(m: np.ndarray) -> np.ndarray:
    """L2 行归一化, 零向量保持不变 (避免除零)。

    【白话】把每行向量"拉"成长度为 1，这样比较方向时不受"长度"影响。
    就像比较两个人走的方向，不管他们走了多远，只看方向是否一致。
    """
    norms = np.linalg.norm(m, axis=1, keepdims=True)
    return m / np.where(norms == 0, 1, norms)


# ============================================================================
# 1. 文本聚合: 按 (银行, 年度) 拼接新闻标题+正文
# 【白话】把同一家银行、同一年的所有新闻全部拼在一起，变成一篇"大文章"。
#   就像把某银行 2023 年所有新闻合并成一份"年度总结"，用来代表它这一年的
#   金融科技战略方向。
# ============================================================================

def _aggregate_bank_year_texts(df_exploded):
    """按 (target_bank, year) 聚合新闻文本。

    将同一银行同一年度的所有新闻标题和正文拼接为单一文档,
    构成 Hoberg & Phillips (2016) 框架中"企业产品描述"的代理变量。

    Args:
        df_exploded: 文章-银行级 DataFrame, 需包含 target_bank, year, 内容 列

    Returns:
        DataFrame[target_bank, year, agg_text], 已过滤空文本行
    """
    # 守卫: 空输入直接返回空 DataFrame，避免 groupby 空集引发异常
    if df_exploded.empty or '内容' not in df_exploded.columns:
        logger.info("  文本聚合: 0 个 Bank-Year 文档 (覆盖 0 银行, 0 年)")
        return pd.DataFrame(columns=['target_bank', 'year', 'agg_text'])

    def _concat(group):
        bodies = group['内容'].fillna('').astype(str)
        titles = group['标题'].fillna('').astype(str) if '标题' in group.columns else bodies
        return ' '.join(titles + ' ' + bodies)

    agg = df_exploded.groupby(['target_bank', 'year']).apply(
        _concat, include_groups=False).reset_index(name='agg_text')
    result = agg[agg['agg_text'].str.strip().str.len() > 0]
    logger.info(f"  文本聚合: {len(result)} 个 Bank-Year 文档 "
                f"(覆盖 {result['target_bank'].nunique()} 银行, "
                f"{result['year'].nunique()} 年)")
    return result


# ============================================================================
# 2. TF-IDF 相似度矩阵 (Hoberg & Phillips 2016, §III)
# 【白话】把每家银行的"年度总结"文本变成数字向量，然后两两比较。
#   就像把 54 家银行放在一个"坐标系"里，离得近的银行说明它们做的
#   金融科技战略很像，离得远的说明很不一样。
# ============================================================================

def _build_tfidf_sim_matrix(texts, mode='char'):
    """构建逐年独立的 TF-IDF cosine 相似度矩阵。

    两种模式:
      - char: char_wb(2,4) 字符 n-gram, 不依赖分词质量
      - word: jieba 词级, 语义粒度更高

    参数设置依据:
      - max_features=5000: 控制词表大小, 平衡信息量与噪声
      - min_df=1: 保留所有出现过的词, 避免小样本/高差异文本清空词表
      - max_df=0.95: 排除出现在 95% 以上文档的超高频词 (高度相似时降级为 1.0)
      - sublinear_tf=True: log(1+tf) 降低词频极端值的影响
        (Manning, C. D., Raghavan, P., & Schütze, H. (2008).
        Introduction to Information Retrieval. Cambridge University Press.
        https://doi.org/10.1017/CBO9780511809071, §6.4)

    Args:
        texts: 文本列表 (逐年切片)
        mode: 'char' 或 'word'

    Returns:
        np.ndarray: 相似度矩阵, 对角线 NaN (排除自身比较)
    """
    # min_df=1: 保留所有出现过的词, 防止小样本/高差异文本清空词表
    # 噪声控制依赖 max_df=0.95 和 max_features=5000
    _mdf = 1
    _max_df = 0.95
    if mode == 'char':
        _kw = dict(analyzer='char_wb', ngram_range=(2, 4),
                   max_features=5000, min_df=_mdf, sublinear_tf=True)
    else:
        _kw = dict(tokenizer=_jieba_tokenizer,
                   max_features=5000, min_df=_mdf, sublinear_tf=True)
    try:
        vec = TfidfVectorizer(max_df=_max_df, **_kw)
        sim = cosine_similarity(vec.fit_transform(texts))
    except ValueError:
        # max_df=0.95 过滤后词表为空 (如文档高度相似), 降级为不过滤
        logger.warning(f"    TF-IDF {mode}: max_df=0.95 词表清空, 降级为 max_df=1.0")
        vec = TfidfVectorizer(max_df=1.0, **_kw)
        sim = cosine_similarity(vec.fit_transform(texts))
    np.fill_diagonal(sim, np.nan)
    return sim  # similarity ∈ [0,1]: 值越大 → 越相似


# ============================================================================
# 3. LDA + Jensen-Shannon 距离矩阵 (Lin 1991; Blei et al. 2003)
# 【白话】另一种比较方法。先用 LDA 发现每家银行新闻的"主题比例"
#   （比如: 30% 讲移动支付, 20% 讲区块链, 50% 讲智能风控），
#   然后用 JSD 距离衡量两家银行的主题比例有多不同。
#   这是 TF-IDF 方法的稳健性检验，看换一种方法结果是否一致。
# ============================================================================

def _build_lda_jsd_matrix(texts, n_banks):
    """jieba 词级 → LDA 主题分布 → pairwise JSD 距离。

    使用 Jensen-Shannon divergence (Lin 1991) 度量主题分布差异,
    JSD 是 KLD 的对称化平滑版本, 满足度量公理 (三角不等式)。

    主题数 K 的选取:
      - K = max(10, n_banks // 30), 确保主题数不低于 10
      - 当银行数 ~54 时 K=10, 每个主题约覆盖 5-6 家银行

    Args:
        texts: 文本列表
        n_banks: 银行数量

    Returns:
        np.ndarray: JSD 距离矩阵 ∈ [0,1], 对角线 NaN
    """
    K = max(10, n_banks // 30)
    cv = CountVectorizer(
        tokenizer=_jieba_tokenizer,
        max_features=5000, min_df=1, max_df=0.95)
    try:
        dtm = cv.fit_transform(texts)
    except ValueError:
        # max_df=0.95 过滤后词表为空, 降级
        logger.warning("    LDA: max_df=0.95 词表清空, 降级为 max_df=1.0")
        cv = CountVectorizer(
            tokenizer=_jieba_tokenizer,
            max_features=5000, min_df=1, max_df=1.0)
        dtm = cv.fit_transform(texts)
    lda = LatentDirichletAllocation(
        n_components=K, random_state=42,
        max_iter=50, learning_method='online', n_jobs=-1)
    theta = lda.fit_transform(dtm)
    logger.info(f"    LDA K={K}, perplexity={lda.perplexity(cv.transform(texts)):.1f}")

    # 计算 pairwise JSD (对称半矩阵)
    jsd_mat = np.zeros((n_banks, n_banks))
    for i in range(n_banks):
        for j in range(i + 1, n_banks):
            d = jensenshannon(theta[i], theta[j])  # sqrt(JSD) ∈ [0,1]
            jsd_mat[i, j] = jsd_mat[j, i] = d
    np.fill_diagonal(jsd_mat, np.nan)
    return jsd_mat  # distance: 值越小 → 越相似


# ============================================================================
# 4. Embedding 相似度矩阵 (Reimers & Gurevych 2019)
# 【白话】第三种比较方法。用 AI 模型把文本变成"语义向量"，能理解
#   "移动支付"和"手机银行"意思很像（而 TF-IDF 只能看字面）。
#   这也是稳健性检验，看不同方法结果是否一致。
# ============================================================================

async def _get_embeddings_api(texts):
    """通过 API 获取文本 Embedding 向量。

    复用 tone_llm_processing 配置中的第一个模型的 base_url 和 api_key。
    采用批量请求 (每批 100 条) 以控制单次请求大小。

    Raises:
        RuntimeError: API 返回非 200 状态码
    """
    import aiohttp
    cfg = LLM_CONFIG.get('models', [{}])[0]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {cfg['api_key']}"
    }
    all_emb = []
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(texts), 100):
            batch = texts[i:i + 100]
            async with session.post(
                f"{cfg['base_url']}/embeddings",
                json={"model": "text-embedding-3-small", "input": batch},
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Embedding API HTTP {resp.status}")
                data = await resp.json()
                all_emb.extend([
                    d['embedding']
                    for d in sorted(data['data'], key=lambda x: x['index'])
                ])
    return np.array(all_emb)


def _build_embedding_sim_matrix(texts):
    """构建 Embedding cosine 相似度矩阵, 三层降级策略。

    降级顺序:
      1. API (text-embedding-3-small) — 首选, 质量最高
      2. sentence-transformers (shibing624/text2vec-base-chinese) — 本地备选
      3. None — 跳过 Embedding 方法

    文本截断为 8000 字符以适配 API token 限制。

    Returns:
        np.ndarray | None: 相似度矩阵, 降级失败时返回 None
    """
    truncated = [t[:8000] for t in texts]
    # 策略 1: API Embedding
    try:
        emb = asyncio.run(_get_embeddings_api(truncated))
        logger.info("    Embedding: API (text-embedding-3-small) 成功")
    except Exception as e:
        logger.warning(f"    Embedding API 降级: {type(e).__name__}: {e}")
        # 策略 2: 本地 sentence-transformers
        try:
            from sentence_transformers import SentenceTransformer
            emb = SentenceTransformer('shibing624/text2vec-base-chinese').encode(truncated)
            logger.info("    Embedding: 本地 text2vec-base-chinese 成功")
        except Exception as e2:
            logger.warning(f"    Embedding 完全降级: {type(e2).__name__}: {e2}")
            return None
    sim = cosine_similarity(emb)
    np.fill_diagonal(sim, np.nan)
    return sim


# ============================================================================
# 5. N-最近邻聚合 (Hoberg & Phillips 2016, §III.B)
# 【白话】这是核心步驤！对每家银行，找到和它最像的 N 家同行，
#   然后看它与这 N 家同行的"平均距离"。
#   比喻: 就像在班级里找到和你成绩最接近的 5 个同学，
#   然后看你们的平均差距有多大 — 差距越大，说明你越"与众不同"。
# ============================================================================

def _compute_nn_scores(matrix, bank_list, N_list, is_distance=False):
    """N-最近邻差异度聚合 — 实现 Guzman & Li (2023) Section 3 核心公式。

    本函数直接实现论文中从相似度到战略差异度的转换规则:

        Ŝ_i = (1/N) Σ_{j ∈ J_i^N} δ_ij
        (Guzman & Li 2023, Management Science, §3 "From similarity to
         founding strategy")

    其中 δ_ij = 1 - cosine_similarity(v_i, v_j) 为文本距离,
    J_i^N 为银行 i 的 N 个最近邻 (文本空间中相似度最高的 N 家同行)。

    对于每家银行, 找到文本空间中最近的 N 个同行:
      - similarity 矩阵: 取最大 N 个, 差异度 = mean(1 - sim_topN) → Ŝ_i
      - distance 矩阵: 取最小 N 个, 差异度 = mean(dist_topN) → Ŝ_i

    N=5 为基准 (与论文一致), N=3,4,6,7 为敏感性检验。
    N 值敏感性检验的理论基础:
      Bresnahan, T. F., & Reiss, P. C. (1991). Entry and competition in
      concentrated markets. Journal of Political Economy, 99(5), 977–1009.
      https://doi.org/10.1086/261786

    Args:
        matrix: 相似度或距离矩阵 (n×n), 对角线为 NaN
        bank_list: 银行名称列表
        N_list: N 值列表 (如 [3,4,5,6,7])
        is_distance: True=距离矩阵, False=相似度矩阵

    Returns:
        dict: {f'n{N}': {bank: Ŝ_i}, 'sim_max': {bank: max_similarity}}
    """
    results = {f'n{N}': {} for N in N_list}
    results['sim_max'] = {}
    for i, bank in enumerate(bank_list):
        valid = matrix[i][~np.isnan(matrix[i])]
        if len(valid) == 0:
            for N in N_list:
                results[f'n{N}'][bank] = np.nan
            results['sim_max'][bank] = np.nan
            continue
        if is_distance:
            # 距离矩阵: 升序排列, 取最小 N 个 (LDA+JSD 路径)
            idx = np.argsort(valid)
            results['sim_max'][bank] = float(1.0 - valid[idx[0]])
            for N in N_list:
                k = min(N, len(valid))
                # Ŝ_i = mean(dist_topK), K = min(N, |peers|)
                results[f'n{N}'][bank] = float(np.mean(valid[idx[:k]]))
        else:
            # 相似度矩阵: 降序排列, 取最大 N 个
            # Guzman & Li (2023, §3): δ_ij = 1 - sim_ij → Ŝ_i = mean(δ_topN)
            idx = np.argsort(valid)[::-1]
            results['sim_max'][bank] = float(valid[idx[0]])
            for N in N_list:
                k = min(N, len(valid))
                # Ŝ_i = (1/k) Σ_{j ∈ J_i^k} (1 - sim_ij)
                results[f'n{N}'][bank] = float(np.mean(1.0 - valid[idx[:k]]))
    return results


# ============================================================================
# 6. 产品市场流动性 Fluidity (Hoberg et al. 2014, JF)
# 【白话】衡量竞争者是否正在向你的"领地"移动。
#   想象你开了一家奶茶店，如果别人也纷纷开始卖奶茶，那就是"Fluidity 高"，
#   说明竞争加剧了。反之如果别人都在做咖啡，没人跟你抢奶茶生意，
#   那就是"Fluidity 低"。
# ============================================================================

def _compute_fluidity(agg_df, mode='char'):
    """计算产品市场流动性指标。

    定义 (Hoberg et al. 2014, Eq. 2):
      Fluidity_i,t = cosine(N_i,t, Σ_{j≠i} |N_j,t - N_j,t-1|)

    直觉: 衡量银行 i 当前的文本"位置"与市场整体"变化方向"的一致性。
    高 Fluidity 意味着竞争对手正向银行 i 所在的文本空间移动。

    注意: 首年无前期数据, 返回 NaN。

    Args:
        agg_df: 聚合文本 DataFrame[target_bank, year, agg_text]
        mode: 'char' 或 'word'

    Returns:
        dict: {(bank, year): fluidity_score}
    """
    fluidity = {}
    for year in sorted(agg_df['year'].unique()):
        df_t = agg_df[agg_df['year'] == year]
        df_t1 = agg_df[agg_df['year'] == year - 1]
        if df_t1.empty:
            continue  # 首年无前期数据

        # min_df: 跨 t 和 t-1 合并后的文档池，动态调整
        # min_df=1: 与 _build_tfidf_sim_matrix 保持一致
        _mdf_flu = 1
        kw = (dict(analyzer='char_wb', ngram_range=(2, 4),
                   max_features=5000, min_df=_mdf_flu)
              if mode == 'char'
              else dict(tokenizer=_jieba_tokenizer,
                        max_features=5000, min_df=_mdf_flu))
        try:
            vec = TfidfVectorizer(max_df=0.95, **kw).fit(
                pd.concat([df_t['agg_text'], df_t1['agg_text']]))
        except ValueError:
            logger.warning(f"    Fluidity {mode}: max_df=0.95 词表清空, 降级为 1.0")
            vec = TfidfVectorizer(max_df=1.0, **kw).fit(
                pd.concat([df_t['agg_text'], df_t1['agg_text']]))
        vt = _l2_normalize(vec.transform(df_t['agg_text'].values).toarray())
        vt1 = _l2_normalize(vec.transform(df_t1['agg_text'].values).toarray())

        # 建立 t-1 期银行索引映射
        t1_map = {b: i for i, b in enumerate(df_t1['target_bank'].values)}
        for i, bank in enumerate(df_t['target_bank'].values):
            # 计算市场变化向量: Σ_{j≠i} |N_j,t - N_j,t-1|
            change = np.zeros(vt.shape[1])
            for j, other in enumerate(df_t['target_bank'].values):
                if other != bank and other in t1_map:
                    change += np.abs(vt[j] - vt1[t1_map[other]])
            d = np.linalg.norm(vt[i]) * np.linalg.norm(change)
            fluidity[(bank, year)] = float(np.dot(vt[i], change) / d) if d > 0 else np.nan
    return fluidity


# ============================================================================
# 7. 主入口 + 诊断
# 【白话】下面是这个模块的"总指挥"，调用上面所有工具函数，
#   按顺序执行: 聚合文本 → 计算距离 → 找最近邻 → 算 Fluidity → 合并到面板
# ============================================================================

def compute_strategic_differentiation(df_exploded, panel):
    """计算金融科技战略差异度指数 (FinTech Strategic Differentiation Score)。

    改进 A: 构建基于文本距离的全新分析维度
    ─────────────────────────────────────
    论文依据:
      严格映射 Guzman & Li (2023, MS) Section 3 "From similarity to founding
      strategy" 中关于计算企业文本表述的余弦相似度并聚合至最近竞争者的规则:

          Ŝ_i = (1/N) Σ_{j ∈ J_i^N} δ_ij
          (N=5 为基准, N=3~7 为敏感性检验)

    边际贡献 / 解决的内生性问题:
      将所有银行当年的金融科技新闻文本聚合, 计算其与其他所有银行的
      TF-IDF (及 LDA+JSD / Embedding) 文本相似度。通过测度每家银行在
      向量空间中与其最近的几家同业的文本"距离", 揭示银行业金融科技
      创新的战略生态位。这解决了当前粗颗粒度加权方法 (单纯比拼新闻
      数量和情感得分) 所带来的内生性问题 — 数量和情感指标容易受银行
      规模、媒体关注度等混杂因素驱动, 而文本距离度量的是战略内容本身
      的差异性, 能更精准地分离出差异化战略所带来的超额边际贡献。

    处理流程:
      1. 按 (银行, 年度) 聚合新闻文本 → "企业产品描述"代理变量
      2. 逐年计算 4 种文本距离矩阵 (TF-IDF char/word, LDA+JSD, Embedding)
         → Hoberg & Phillips (2016, JPE, §III) 逐年重建方法
      3. N-最近邻聚合 → Ŝ_i (N=3,4,5,6,7 for TF-IDF; N=5 for LDA/Embedding)
      4. 计算 Fluidity → Hoberg et al. (2014, JF, Eq. 2)
      5. 合并到面板并执行四方法收敛效度诊断

    Args:
        df_exploded: 文章-银行级 DataFrame
        panel: 银行-年面板 DataFrame

    Returns:
        panel: 新增 18 列战略差异度指标的面板 DataFrame
    """
    logger.info("=" * 60)
    logger.info("战略差异度指数 (Guzman & Li 2023; Hoberg & Phillips 2016)")
    logger.info("=" * 60)

    # 【白话】N_LIST = [3,4,5,6,7] 表示分别看最像的 3/4/5/6/7 家同行
    #   N=5 是论文推荐的基准值，其他是"换个数字看结果是否稳定"
    N_LIST = [3, 4, 5, 6, 7]
    # 第一步: 把所有新闻按 (银行, 年) 合并成"年度总结"大文档
    agg_df = _aggregate_bank_year_texts(df_exploded)
    all_results = []  # 用来收集所有年度、所有银行的计算结果

    # 【白话】逐年计算 — 每一年独立建模，不跨年混合
    #   这样做是因为金融科技领域变化很快，2020年的"热词"和2024年可能完全不同
    for year in sorted(agg_df['year'].unique()):
        dy = agg_df[agg_df['year'] == year]
        banks = dy['target_bank'].tolist()   # 这一年有哪些银行
        texts = dy['agg_text'].tolist()       # 每家银行的"年度总结"文本
        if len(banks) < 3:
            # 少于 3 家银行没法比较，跳过
            logger.warning(f"  年度={year}: 仅 {len(banks)} 家银行, 跳过 (最低要求 3)")
            continue
        logger.info(f"  年度={year}, 银行数={len(banks)}")

        # 方法 A: TF-IDF 字符级 — 看字符组合的相似度（不依赖分词）
        sc = _compute_nn_scores(
            _build_tfidf_sim_matrix(texts, 'char'), banks, N_LIST)
        # 方法 B: TF-IDF 词级 — 用 jieba 分词后比较（语义更精准）
        sw = _compute_nn_scores(
            _build_tfidf_sim_matrix(texts, 'word'), banks, N_LIST)
        # 方法 C: LDA + JSD — 比较"主题分布"的差异（稳健性检验）
        try:
            sl = _compute_nn_scores(
                _build_lda_jsd_matrix(texts, len(banks)),
                banks, [5], is_distance=True)
        except Exception as e:
            logger.warning(f"    LDA+JSD 失败 ({type(e).__name__}), 跳过")
            sl = None
        # 方法 D: Embedding — 用 AI 理解语义后比较（稳健性检验）
        se_mat = _build_embedding_sim_matrix(texts)
        se = _compute_nn_scores(se_mat, banks, [5]) if se_mat is not None else None

        # 【白话】把这一年每家银行的计算结果打包成一行行数据
        #   每一行 = 一家银行在这一年的所有差异度分数
        for bank in banks:
            row = {'target_bank': bank, 'year': year}
            for N in N_LIST:
                # strat_diff_n5 = 和最像的5家同行的平均"距离"（字符级）
                row[f'strat_diff_n{N}'] = sc[f'n{N}'][bank]
                # strat_diff_n5_w = 同上，但用词级方法（稳健性）
                row[f'strat_diff_n{N}_w'] = sw[f'n{N}'][bank]
            # strat_sim_max = 和最像的那一家同行的相似度
            row['strat_sim_max'] = sc['sim_max'][bank]
            row['strat_sim_max_w'] = sw['sim_max'][bank]
            if sl:  # LDA 方法成功时才有
                row['strat_diff_n5_lda'] = sl['n5'].get(bank, np.nan)
                row['strat_sim_max_lda'] = sl['sim_max'].get(bank, np.nan)
            if se:  # Embedding 方法成功时才有
                row['strat_diff_n5_emb'] = se['n5'].get(bank, np.nan)
                row['strat_sim_max_emb'] = se['sim_max'].get(bank, np.nan)
            all_results.append(row)

    # 【白话】Fluidity: 衡量竞争者是否在向你的"领地"移动
    #   char/word 双模式 = 用两种不同的文本分析方法各算一遍
    flu_c = _compute_fluidity(agg_df, 'char')
    flu_w = _compute_fluidity(agg_df, 'word')

    # 【白话】最终组装: 把所有计算结果合并到面板数据里
    #   面板(panel) = 每行是一家银行的一年，这里把差异度分数填进去
    if all_results:
        res = pd.DataFrame(all_results)
        # 把 Fluidity 分数也加上
        res['strat_fluidity'] = res.apply(
            lambda r: flu_c.get((r['target_bank'], r['year']), np.nan), axis=1)
        res['strat_fluidity_w'] = res.apply(
            lambda r: flu_w.get((r['target_bank'], r['year']), np.nan), axis=1)
        # 用银行名+年份做"钥匙"，把新列合并到面板
        panel = panel.merge(res, on=['target_bank', 'year'], how='left')
        # 跑诊断: 检查四种方法的结果是否大致一致（收敛效度）
        _log_robustness_diagnostics(panel)
        logger.info(f"  ✅ 战略差异度: 成功合并 {len(res)} 行, "
                    f"新增 {len(res.columns) - 2} 列")
    else:
        logger.warning("  ⚠️ 无有效结果 (所有年度银行数不足 3)")
    return panel


def _log_robustness_diagnostics(panel):
    """输出四方法相关矩阵 + 值域断言。

    【白话】这是"质量检查"函数，做两件事：
      1. 看四种方法（TF-IDF字符/词级、LDA、Embedding）算出来的分数
         是否大致一致 — 如果四种方法都说某银行很独特，说明结果可靠
      2. 检查所有分数是否在 0~1 之间 — 超出范围说明计算有 Bug
    """
    cols = [c for c in ['strat_diff_n5', 'strat_diff_n5_w',
                        'strat_diff_n5_lda', 'strat_diff_n5_emb']
            if c in panel.columns]
    if len(cols) >= 2:
        logger.info(f"  四方法相关矩阵:\n{panel[cols].corr().round(3).to_string()}")

    # 值域断言: 所有 strat_* 列 ∈ [0, 1] (含浮点误差容忍)
    for col in [c for c in panel.columns if c.startswith('strat_')]:
        v = panel[col].dropna()
        if len(v) > 0:
            assert (v >= -1e-10).all() and (v <= 1 + 1e-10).all(), \
                f"{col} 超出 [0,1] 值域: min={v.min():.6f}, max={v.max():.6f}"
