---
family_id: F522
columns:
- subst_adopt_kw_p75
- subst_adopt_kw_p75_ctx
- subst_adopt_kw_p75_ss
unit: 银行-年占比 (0–1, measured-篇数为分母的比例; 非可加合成分数)
formula: 逐篇先按 year 分组 (跨全部银行的年度截面, 非按 target_bank 分组) 求年度分位阈值 ysim=quantile(policy_cosine_sim, 0.75), yfreq=quantile(fintech_distinct_keywords, 0.75); 定义 high_freq=(freq>=yfreq), high_sim=(sim>=ysim); is_subst=(high_freq & high_sim) 仅在 sim 与 freq 双双非缺失(measured)时取值, 否则记 NaN; 银行-年面板列 subst_adopt_kw_p75 = groupby(target_bank, year)['is_subst'].mean() (聚合粒度=target_bank×year, 与阈值计算粒度是两回事; mean 自动跳过 NaN, 分母=已测量篇数, 全未测量年→NaN, 不填 0)。
producer: "pipeline/panel/runner.py::_classify_policy_quadrants (象限判据原语) + 同文件 L1978 起 逻辑 B: 四象限离散分类 循环 (聚合与列命名)"
upstream:
- 15_article_policy_alignment.parquet::policy_cosine_sim / policy_cosine_sim_ctx / policy_cosine_sim_ss
- 12_news_fintech.parquet::fintech_distinct_keywords (Track A/kw 词频, track-agnostic 元数据)
citations:
- {doi: "10.1111/jofi.13412", type: journal, authors: "Duchin, R., Gao, J., & Xu, Q.", year: 2025, title: "Sustainability or Greenwashing: Evidence from the Asset Market for Industrial Pollution", venue: "The Journal of Finance"}
- {doi: "10.1287/orsc.2014.0949", type: journal, authors: "Kim, E.-H., & Lyon, T. P.", year: 2015, title: "Greenwash vs. Brownwash: Exaggeration and Undue Modesty in Corporate Sustainability Disclosure", venue: "Organization Science"}
- {doi: "10.2307/2393295", type: journal, authors: "Westphal, J. D., & Zajac, E. J.", year: 1994, title: "Substance and Symbolism in CEOs' Long-Term Incentive Plans", venue: "Administrative Science Quarterly"}
- {doi: "10.1287/stsc.2023.0188", type: journal, authors: "Westphal, J. D.", year: 2023, title: "Systemic Symbolic Management, Corporate Social Responsibility, and Corporate Purpose: A Cautionary Tale", venue: "Strategy Science"}
- {doi: "10.1016/j.jbankfin.2024.107191", type: journal, authors: "Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.", year: 2024, title: "How Cheap Talk in Climate Disclosures Relates to Climate Initiatives, Corporate Emissions, and Reputation Risk", venue: "Journal of Banking & Finance"}
- {doi: "10.1073/pnas.2305016120", type: journal, authors: "Gilardi, F., Alizadeh, M., & Kubli, M.", year: 2023, title: "ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks", venue: "Proceedings of the National Academy of Sciences"}
new_dois: []
---

## CORE

【构念与来源】
本家族属于 P3 (bank_fintech_substance, W&Z substance-symbolic 传统) 的机制检验/稳健性象限分类列族, 是家族 canonical subst_adopt 系列在 Track A (kw, 关键词词频轨) × P75 (第 75 百分位, 高阈值稳健性检验) 处的落点。构念根源是组织理论中"实质采纳 (substantive adoption) 对符号采纳 (symbolic/decoupled adoption)"的经典区分 (Westphal & Zajac 1994 ASQ; Westphal 2023 Strategy Science): 一家企业围绕某项政策/技术议题的对外传播 (报道中词频高低) 是否与其传播内容跟该政策议题的语义贴近程度 (与政策文本的余弦相似度) 同步偏离常态, 而非仅有词汇堆砌却无实质内容对齐 (即"漂绿"/"洗科技"式脱耦, Kim & Lyon 2015; Bingler et al. 2024 对气候披露的 cheap-talk 检验思路可类比迁移)。在本项目语境下, "政策议题"具体化为金融科技(FinTech)相关的银行报道: 词频维度 (Track A/kw) 取自 12_news_fintech.parquet 的 `fintech_distinct_keywords` — 该词是 Aho-Corasick (AC) 词典命中的去重关键词计数, track-agnostic (不随 full/ctx/ss 轨切换, 因其是文章级元数据而非情感/相似度测度); 语义对齐维度取自 15_article_policy_alignment.parquet 的 `policy_cosine_sim` (及其 `_ctx`/`_ss` 变体) — 文章嵌入与政策锚点文本嵌入的余弦相似度。
【方法学与计算】
逐篇分类判据由 `_classify_policy_quadrants` 原语实现, 阈值计算粒度与占比聚合粒度是两个不同步骤、不同分组键, 不可混同: ① 阈值计算 — 对每个 year 分组 (跨全部银行的年度截面 `df_align.groupby('year')[col].transform(...)`, 并非按 target_bank 分组), 分别对相似度列与词频列求当年分位数阈值 (P75 处 quantile(0.75)), 定义 high_freq = (freq >= yfreq)、high_sim = (sim >= ysim), 由二值组合产生四象限: Token (高词频·低相似, "洗科技" — 只堆词不贴题)、Hidden (低词频·高相似, "闷声干大事" — 悄悄做实事但报道提及少)、Substantive (高词频·高相似, 言行一致的实质采纳)、Irrelevant (低词频·低相似, 隐含未落列, 无对应面板列)。② 占比聚合 — subst_adopt_kw_p75 取 Substantive 象限的逐篇 0/1 指示, 再按 (target_bank, year) 分组求均值得到银行-年占比 (`df_align.groupby(['target_bank','year'])[...].mean()`); 换言之, 一家银行某年的"是否落入 Substantive"是拿该银行当年逐篇的 sim/freq 去比对"全体银行当年"的分位阈值, 而非该银行自身历史分布的分位阈值, 阈值本身不因银行而异, 只因年份而异。⚠ 关键防御性设计 (2026-06-11 修复, fix(omni-g-runner-03/g-runner-11)): 早期实现对 sim/freq 缺失行用 `NaN >= 阈值 → False` 隐式归类, 会把 stage 15 优雅早退产出的全 NaN `policy_cosine_sim` 静默判成"低相似", 使高词频文章系统性误归 Token 象限, 制造伪造的非 NaN 面板值。现实现改为仅对 sim 与 freq 双双非缺失 (measured) 的行分类, 未测量行指示值记 NaN, 交由 `groupby.mean()` 自动跳过 (占比分母 = 该银行-年内已测量篇数, 而非总发文篇数); 全年未测量则该银行-年面板值直接为 NaN, 绝不回填 0 (v6/F3 修复: 0 会把"未测量"误读成"零采纳", 污染 TWFE 系数估计, 参照 Allison 2001 §3 缺失值处理原则)。P75 相对 canonical P50 (家族 F520) 是更严格的双高门槛 — 只有词频与相似度都排进当年 (全体银行截面) 前 25% 的文章才落入 Substantive, 用于检验主结论对"实质采纳"定义严格程度的敏感性, 与 P25 (更宽松) 一起构成 {P25, P50, P75} 三档稳健性梯子 (`config/filtering.yaml::article_alignment.quadrant_percentiles`, SSOT)。
【文献定位】
方法论传承自组织理论中实质/象征采纳的区分文献: Westphal & Zajac (1994, ASQ) 首次系统区分 CEO 长期激励计划的采纳是否伴随实质性治理变化; Westphal (2023, Strategy Science) 将系统性符号管理概念延展至企业社会责任与企业目标声明领域。文本层面的"言行是否一致"判定借鉴气候/ESG 披露文献中的 cheap-talk 检验设计 (Bingler et al. 2024, Journal of Banking & Finance) 与漂绿/漂棕对比框架 (Kim & Lyon 2015, Organization Science)。金融文献中同一逻辑的最新应用是 Duchin, Gao & Xu (2025, The Journal of Finance) 对"可持续性还是漂绿"的资产市场证据检验, 与本列族在"报道语言 vs. 实际行为"证伪逻辑上同构。文本测度层面, 关键词词频与语义相似度分别对应两类经典文本分析原语: 前者是词典/AC 自动机式浅层匹配, 后者依赖 LLM/嵌入语义理解, 二者互证的设计思路呼应 LLM 文本标注可靠性文献 (Gilardi, Alizadeh & Kubli 2023, PNAS) 对"表层特征 vs. 语义理解"两条独立证据链互补价值的论证。
【口径铁律复述】
subst_adopt_kw_p75/_ctx/_ss 三列对应家族三轨 (full/ctx/ss) 判据, 三轨各自基于本轨的相似度列 (policy_cosine_sim / `_ctx` / `_ss`) 与本轨可得的词频列独立分类、独立聚合, 是各自 just-identified 并排、互为稳健性、不分主次的三条测度, 禁止混入同一 over-identified Hansen J 设定。三轨与 Track B (int, 家族 F515–F517 `subst_adopt_int_p*`) 以及 P25/P50 (家族 F518/F519/F520/F521) 同为"四象限分类判据敏感性"梯子的并列臂, 之间同样互为稳健性不分主次, 不应挑选单一档次作为"主"结果而弃用其余档次。ss 轨回退语义镜像 ctx: 词频侧优先取同轨变体 `{freq_col}_ss` (若存在), kw 轨的 `fintech_distinct_keywords` 因是 track-agnostic 元数据 (无 ctx/ss 独立版本) 而复用 full 列并在日志中披露; 相似度侧严格取 `policy_cosine_sim_ss`, 该列继承 stage 14 `ctx_materializer` 对 `content_ss` 的回退语义 (无银行∧金科同句共现的文章 `content_ss` 回退为全文 body、`ss_is_fallback=True`), 因此 `_ss` 轨的分位阈值与分类结果天然把回退文章计入同一分母, 而非单独剔除。留篇门控口径 (full-only, 2026-06-29) 对本列族的约束是直接的显式过滤, 而非仅下游行范围恰好一致的弱耦合: `_classify_policy_quadrants` 的输入 df_align 在分类前已先经 `_filter_to_verified_universe` 按 (docid, target_bank) 键与 24_herd_decay (stage 21 LLM full-only 门控产出的 verified 域 df_exploded) 做 inner semi-join (fix(omni-g-runner-02, 2026-06-11): stage 15 输出含 LLM 验证未通过文章, 若不过滤会让 26.8% 假阳性文章污染分位阈值与象限分母、制造 phantom bank-year), 本列族与 article_sim_*/fintech_intensity_mean/policy_cosine_sim_lg_* 同属该 semi-join 收敛到同一 verified 聚合域的 "7h-token 全族"。因此分位阈值 (年度截面) 与四象限分类判据均已建立在 verified 域之上, 三轨 (full/ctx/ss) 共享同一份 full-only 门控后的行宇宙, 三轨内部差异只来自各自轨道的相似度/词频列, 不来自行范围。

## VAR: subst_adopt_kw_p75

【变体差分】
本列是家族 canonical (无 `_ctx`/`_ss` 后缀) 落点, 对应 full 轨: 相似度取 `policy_cosine_sim` (标题+正文全文嵌入与政策锚点的余弦相似度), 词频取 `fintech_distinct_keywords` (AC 词典在全文范围命中的去重关键词数)。P75 分位阈值逐年独立计算 (`groupby('year')[col].transform(quantile(0.75))`), 意味着阈值随年份浮动、不同年份间不可跨年直接比较原始阈值水平, 但占比列本身 (银行-年 Substantive 占比) 是可跨年比较的相对位次口径。与 canonical P50 (家族 F520 `subst_adopt_kw_p50`) 相比, P75 对词频与相似度均要求排进当年前 25% (而非前 50%), 因此该占比在样本内天然更小、更稀疏, 是对主结果 (P50) 的高阈值端稳健性检验, 用于排除"结论仅由中位数附近临界样本驱动"的顾虑。与 Track B 同档 (`subst_adopt_int_p75`, 家族 F516) 相比, 本列词频维度用离散去重关键词计数 (kw, 侧重"提到了哪些不同的金融科技概念"), 而非 TF-IDF×SIF 加权强度 (int, 侧重"金融科技相关表述的加权浓度"), 两条词频构念口径不同、互为稳健性并排, 不应合并入同一回归设定的同一个内生变量位置。本列同时是 `_allv` 全语料静态锚点孪生列 (家族 F523 `subst_adopt_kw_p75_allv`) 的对照臂: `_allv` 用 `policy_cosine_sim_allv` (跨全部年份固定的政策锚点嵌入) 计算相似度, 而本列 (vintage 主轨) 每年独立锚定当年政策文本, 两者刻画的是"锚点是否随年份漂移"这一构造判据敏感性维度, 与三轨 (full/ctx/ss) 维度正交, 互不替代。读者在解读该占比时应注意其分母仅含 sim 与 freq 同时非缺失的篇数, 与 `n_articles` 或其他以留篇门控为分母的面板列口径不同, 不可直接相除做交叉验证。

## VAR: subst_adopt_kw_p75_ctx

【变体差分】
本列对应 ctx 轨: 相似度取 `policy_cosine_sim_ctx` (标题+实体窗口文本的嵌入相似度), 词频优先取同轨变体 (若 `fintech_distinct_keywords_ctx` 存在则用之, 否则因该词频列是 track-agnostic 元数据而复用 full 轨 `fintech_distinct_keywords` 并在生成日志中披露此复用, 该披露路径由 runner.py `_freq_eff` 回退分支实现)。ctx 轨聚焦银行与金科实体邻近窗口内的文本, 排除了正文中与银行-金科议题无关的段落对相似度计算的稀释效应, 因此其 P75 高阈值分类结果反映的是"在实体密集片段内, 词频与语义对齐是否同步处于高位", 与 full 轨 (全文视角) 相比是范围更聚焦、噪声更小但覆盖度可能更低的并排测度。与本列同一 kw 词频轨、不同判据严格度的 P25/P50 ctx 变体 (家族 F518/F520 的 `_ctx` 列) 构成同轨内部的阈值敏感性梯子, 与 full/ss 轨的 P75 变体构成跨轨稳健性梯子, 两个梯子方向正交, 均各自 just-identified 并排、互为稳健性、不进同一 over-identified 设定。ctx 轨相似度依赖上游 stage 15 `article_policy_alignment` 对 `content_ctx` 的嵌入, 若该阶段以优雅早退路径写出全 NaN 相似度列 (如政策锚点文本缺失), 则本列继承 `_classify_policy_quadrants` 的 measured 掩码防御, 未测量篇一律记 NaN 不计入分母, 不会因早退而被误判为低相似 (对应 Token 象限) 从而污染面板估计, 该防御逻辑对三轨完全一致、无 ctx 独有分支。

## VAR: subst_adopt_kw_p75_ss

【变体差分】
本列对应 ss 轨: 相似度取 `policy_cosine_sim_ss` (标题+银行∧金科同句 ±N 窗口文本的嵌入相似度, `config/filtering.yaml::context_window.ss_sentence_radius` 默认 1), 词频判据与 ctx 轨同规则优先取同轨变体、否则回退复用 full 轨的 track-agnostic `fintech_distinct_keywords`。ss 轨是三轨中范围最窄的一支: 仅在银行与金科词严格同句共现时才取窗口文本, 无该共现的文章 `content_ss` 回退为全文 body 且 `ss_is_fallback=True` (回退语义镜像 ctx 轨的"无实体窗口→全文"设计, 是 stage 14 物化时确定、本列族聚合阶段直接继承的既有语义, 并非本列单独引入的新回退规则), 回退文章仍计入分类与占比分母、不单独剔除。相对 ctx 轨的"实体邻近窗口", ss 轨的"严格同句"判据更苛刻, 因此其相似度与词频分布可能因窗口极窄样本 (尤其在 T=2 开发集上) 而更易出现同质化或零方差, 属预期的小样本退化, 生产全量语料 (T=18) 上应恢复有效区分度。ss 轨的 P75 变体与 full/ctx 轨的 P75 变体、以及本轨自身的 P25/P50 变体 (家族 F518/F520 `_ss` 列) 各自 just-identified 并排, 互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 设定。使用者在生产全量语料 (T=18) 上解读本列时, 应结合 `ss_is_fallback` 占比一并披露: 若某银行-年回退比例极高, 则该年 ss 轨分类结果实质上退化为接近 full 轨口径, 稳健性检验的边际信息量随之下降, 建议与 ctx 轨结果联合报告而非单独依赖 ss 轨下结论。

<!-- rendered-citations:begin -->
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or Greenwashing: Evidence from the Asset Market for Industrial Pollution. The Journal of Finance. https://doi.org/10.1111/jofi.13412
Kim, E.-H., & Lyon, T. P. (2015). Greenwash vs. Brownwash: Exaggeration and Undue Modesty in Corporate Sustainability Disclosure. Organization Science. https://doi.org/10.1287/orsc.2014.0949
Westphal, J. D., & Zajac, E. J. (1994). Substance and Symbolism in CEOs' Long-Term Incentive Plans. Administrative Science Quarterly. https://doi.org/10.2307/2393295
Westphal, J. D. (2023). Systemic Symbolic Management, Corporate Social Responsibility, and Corporate Purpose: A Cautionary Tale. Strategy Science. https://doi.org/10.1287/stsc.2023.0188
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How Cheap Talk in Climate Disclosures Relates to Climate Initiatives, Corporate Emissions, and Reputation Risk. Journal of Banking & Finance. https://doi.org/10.1016/j.jbankfin.2024.107191
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks. Proceedings of the National Academy of Sciences. https://doi.org/10.1073/pnas.2305016120
<!-- rendered-citations:end -->
