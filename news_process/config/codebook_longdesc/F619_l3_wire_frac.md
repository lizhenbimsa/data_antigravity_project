---
family_id: F619
columns:
- wire_frac
unit: 比率/占比 (proportion, [0,1]; bank-year 层面对该行当年全部报道求 is_wire 均值)
formula: 'wire_frac_{i,t} = mean(is_wire_{a}), a 取 bank i 在年份 t 下全部有效文章; is_wire 由 news_salience.py::parse_byline() 依据"作者"字段与正文前 60 字电头关键词扫描判定 (0/1/NaN): 作者字段非空即判定; 作者字段为空时再扫描电头证据, 命中记 1、未命中记 NaN (不涉及版面/页号字段, 版面/页号是 is_front_page/page_rank 的输入, 与 is_wire 判定无关); stage 11 news_bank 物化为文章级列后经 encode 层 (Stage 40) 聚合为 bank-year 均值; 聚合按 mean 自动跳过 NaN 行, 不计入分母'
producer: pipeline\filtering\news_salience.py (Stage 11, 文章级 is_wire 判定) ; pipeline\panel\encode.py (Stage 40, bank-year 聚合 agg['wire_frac'] = ('is_wire','mean'))
upstream: []
citations:
- doi: 10.1111/1475-679X.12349
  type: journal
  authors: Guest, N. M.
  year: 2021
  title: The information role of the media in earnings news
  venue: Journal of Accounting Research
  vol: '59'
  issue: '3'
  pages_or_artno: 1021-1076
- doi: 10.52202/079017-1575
  type: wp
  authors: Silcock, E., Arora, A., D'Amico-Wong, L., & Dell, M.
  year: 2024
  title: 'Newswire: A large-scale structured database of a century of historical news'
  venue: Advances in Neural Information Processing Systems 37 (NeurIPS 2024)
  pages_or_artno: 49768-49779
- doi: 10.1002/widm.70019
  type: journal
  authors: Alva Principe, R., Chiarini, N., & Viviani, M.
  year: 2025
  title: 'Long document classification in the transformer era: A survey on challenges, advances, and open issues'
  venue: WIREs Data Mining and Knowledge Discovery
  vol: '15'
  issue: '2'
  pages_or_artno: e70019
- doi: "10.1016/j.frl.2024.105128"
  type: "journal"
  authors: "Zhang, Z., & Shen, D."
  year: 2024
  title: "Not all the news fitting to reprint: Evidence from price-volume relationship"
  venue: "Finance Research Letters"
  vol: "62"
  pages_or_artno: "105128"
new_dois: []
---

## CORE

【构念与来源】
wire_frac 度量的是一家银行在给定年份的全部报道样本中, 由通讯社通稿转载而非记者原创署名撰写的比例, 是"署名原创性"维度的银行—年聚合测度。其文章级原语 is_wire 产自 pipeline\filtering\news_salience.py, 是 2026-06-05 新增的一批 $0 体裁显著性特征之一 (同批还包括版位显著性 is_front_page/is_front_section/page_rank 与导语显著性 target_in_lead); 之所以称为"$0", 是因为它们全部通过纯字符串/正则解析已有的原始字段 (版面、页号、作者) 得到, 既不调用 LLM 也不引入新依赖, 只是把此前"仅用于广告过滤、从未派生为特征"的既有字段重新利用起来。is_wire 的判定方式是扫描文章正文前 60 个字符, 用一份通讯社关键词表检测是否存在典型的"电头"标记 (如新华社/中新社等通稿开篇惯用的来源声明句式); 该关键词表基于常见通讯社命名与惯用表述整理, 非穷举式覆盖, 因此存在漏判未登记通讯社或误判罕见措辞的可能。判定依据的"作者"字段与内容剥离流程相互独立: stage 00 的 noise_patterns 内容剥离只作用于"内容"列本身, 不影响作者字段, 因此 has_byline/is_wire 不会因为正文清洗而系统性失真。is_wire 在缺失语义上做了明确区分: 当作者字段缺失且电头扫描也未检出任何通讯社证据时, 记为 NaN 而非 0——这是刻意设计 (fix omni-g-entity-13, 2026-06-11), 目的是把"字段本身不适用"(例如网络原生渠道天然没有版面/作者概念的情形) 同"确实署名缺失、判定为非通讯社原创"的语义区分开, 避免把结构性缺失误读成实质结论。bank-year 聚合层用 mean 对该行当年全部文章的 is_wire 求均值, NaN 行会被 mean 自动跳过、不进入分母, 因此 wire_frac 反映的是"有判定依据的文章中通讯社转载占比", 而非"全部文章 (含不适用) 中通讯社转载占比"。

【方法学与计算】
wire_frac 的构造管线是: stage 00 保留原始"作者"字段与正文 → stage 11 news_bank 在文章级调用 news_salience.py 的电头关键词扫描, 生成文章级 is_wire (0/1/NaN) 并随该阶段产出物化 → encode 层在 bank-year 聚合步骤对同一 (bank, year) 下的全部有效文章取 is_wire 均值, 得到 wire_frac。该测度与家族命名前缀 l3 一致, 是 bank-year (level 3) 聚合列, 不是文章级列本身——文章级原语是 is_wire, wire_frac 是其在银行—年维度上的占比化产物。需要特别说明的是, wire_frac 与同批派生的版位显著性 (is_front_page 等)、导语显著性 (target_in_lead) 是三个正交的显著性/原创性维度: 版位度量"编辑把这篇报道放在多显眼的位置", 导语度量"这篇报道是否把目标银行当作叙事主角", 而 wire_frac (经由 is_wire) 度量的是"这篇报道的信息生产端是原创采写还是通稿转载", 三者分别对应读者注意力的物理代理、叙事中心度、以及来源权威/原创性, 互不替代、亦不应合并进同一构念。此外 wire_frac 与 herd_decay.py 产出的跟风衰减权重 (herd_weight_full/ctx/ss) 也是正交关系: herd_decay 度量的是"产出端"的文本重复 (同一时间窗内多篇报道彼此高度相似, 疑似互相抄袭或被同一通稿源头带动), 是基于 TF-IDF 余弦相似度的跨文章比较; 而 wire_frac 度量的是"投入端"的单篇文章生产方式 (记者原创 vs 通讯社供稿), 是基于电头关键词的单篇文章判定。两者常常相关 (通讯社通稿更容易在多家媒体间被重复转载, 从而推高相似度), 但构念上分属不同环节, 不能把 wire_frac 当作 herd_decay 权重的代理变量使用, 也不应在同一回归中把两者当作可互换的稳健性检验。wire_frac 本身没有阈值、没有三轨切分、也没有梯子结构 (不涉及 full/ctx/ss 判据敏感性, 不涉及 co-primary 嵌入双轨, 不涉及消融或权重梯度), 是该家族内唯一的标准列。

【文献定位】
通讯社供稿与记者原创报道在信息含量上的系统性差异, 是媒体经济学与会计信息学交叉领域长期关注的问题。Guest (2021, Journal of Accounting Research) 系统考察了媒体在盈余新闻传播中的信息角色, 区分了不同来源报道对市场反应的差异化贡献, 为"署名原创 vs 通稿转载"这一区分提供了实证支持——原创深度报道往往承载增量信息, 而通稿转载更接近信息的被动扩散渠道而非信息生产本身, wire_frac 正是尝试在中国财经新闻语境下捕捉这一区分的低成本代理。需要明确的是, is_wire 采用的纯正则电头关键词扫描, 与近年基于 Transformer 的长文档分类方法学 (Alva Principe et al., 2025, WIREs Data Mining and Knowledge Discovery, 对该领域的挑战、进展与开放问题做了系统综述) 并无直接的方法学继承关系——后者关注的是深度模型在长文档表征与分类上的技术演进, 而 is_wire 恰恰是刻意回避此类模型、只依赖字符串/正则规则的轻量判定; 两者仅在"体裁/来源等元数据可先于内容语义被廉价提取和利用"这一粗粒度问题意识上存在类比性的呼应, 引用于此仅为标注这一相邻方法论脉络的参照系, 而非声称 is_wire 的设计借鉴或沿用了该综述中的具体技术路线。同时, 新闻通讯社供稿在结构化数据库建设中的规模与历史延续性 (Silcock et al., 2024, NeurIPS) 也印证了通讯社稿件在新闻生态中占比可观、值得作为独立维度单独度量, 而非笼统并入"媒体报道"这一整体范畴。综合而言, wire_frac 的文献定位是: 在中国财经新闻的银行—金科报道语境下, 以最低成本 (纯正则、不依赖 LLM 判定) 捕捉信息生产端的原创性差异, 服务于后续把"媒体关注度"进一步拆解为"原创深度报道关注"与"通稿被动扩散关注"两个可能具有不同经济含义的子维度。 更为直接的前沿参照来自 Zhang 与 Shen (2024): 该文明确把新闻区分为「转载/再刊」与非转载两类, 并证明二者在价量关系上的市场含义不同, 从而佐证「同一条报道究竟是原创产制还是二次分发」本身即是有信息含量的文章级属性——这正是 is_wire 与 has_byline 二分及其 bank-year 均值 wire_frac / staff_written_frac 所要捕捉的对象。迁移边界须诚实交代: 原文的转载判定直接取自新闻数据库自带的转载标记, 而本项目的 is_wire 由 parse_byline() 扫描「作者」字段与正文前 60 字电头关键词的规则判定 (作者字段为空且电头未命中时记 NaN、不入分母), 两者判据完全不同; 且该文停在文章级并以价量关系为被解释变量, 既未做主体-年度的均值聚合, 也未触及署名 (byline) 这一独立维度, 故其援用仅止于「原创/转载之分具有信息含量」这一层的实证支撑。
## VAR: wire_frac

【变体差分】
wire_frac 是该家族 (F619) 内唯一的一列, 因此不存在与家族内其他列的差分语义——它本身即是 canonical、也是唯一的测度口径。在此明确其精确边界, 以避免与相邻家族/相邻测度混淆: 第一, wire_frac 不是三轨测度, 其文章级原语 is_wire 只依据"作者"字段与正文前 60 字电头扫描得到, 不区分 content_full/content_ctx/content_ss, 因此不适用"各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J"的三轨铁律——该铁律约束的是情感/态度类的三轨或 co-primary 嵌入双轨测度, wire_frac 是体裁/来源元数据, 天然 track-agnostic (参见既有先例: track-agnostic 的元数据度量恰是不可强行双轨化的例外情形)。第二, wire_frac 与留篇门控的关系: bank-year 聚合分母遵循 full-only 留篇门控口径 (2026-06-29 起, 是否判定为"一篇银行金科报道"仅看 llm_verified_full == True), 即 wire_frac 的聚合样本框与其余 bank-year 面板列共享同一套留篇集合, 不额外引入自己的样本筛选规则。第三, wire_frac 与 herd_weight_full/ctx/ss (herd_decay.py 产出) 不可混同: 后者是三轨化的产出端相似度衰减权重, 需要 content_full/ctx/ss 三份物化文本分别做 TF-IDF, 而 wire_frac 是单一的投入端来源判定, 无轨道切分, 二者应作为两个独立正交维度分别进入分析, 不应彼此替代或合并稳健性检验。第四, wire_frac 的缺失处理承袭 is_wire 的 NaN 语义: 当某银行—年份下全部文章均因"作者字段缺失且无电头证据"而记为 is_wire=NaN 时, wire_frac 本身也应为 NaN (而非误算为 0), 使用前需检查该行是否存在有效判定样本, 避免把"无法判定"误读为"全部原创"。

<!-- rendered-citations:begin -->
Guest, N. M. (2021). The information role of the media in earnings news. Journal of Accounting Research, 59(3), 1021-1076. https://doi.org/10.1111/1475-679X.12349
Silcock, E., Arora, A., D'Amico-Wong, L., & Dell, M. (2024). Newswire: A large-scale structured database of a century of historical news. Advances in Neural Information Processing Systems 37 (NeurIPS 2024) No. 49768-49779 [Working Paper]. https://doi.org/10.52202/079017-1575
Alva Principe, R., Chiarini, N., & Viviani, M. (2025). Long document classification in the transformer era: A survey on challenges, advances, and open issues. WIREs Data Mining and Knowledge Discovery, 15(2), e70019. https://doi.org/10.1002/widm.70019
Zhang, Z., & Shen, D. (2024). Not all the news fitting to reprint: Evidence from price-volume relationship. Finance Research Letters, 62, 105128. https://doi.org/10.1016/j.frl.2024.105128
<!-- rendered-citations:end -->
