# 文献理论锚点扩充报告 · 第六补编(v3.15.0 后新增指标专项 · 2024–2026 最新文献优先 · 9 主题桶 · APA 第 7 版 · Crossref/DataCite DOI→标题回比 + 权威元数据回填全核验)

- **日期**: 2026-07-06
- **定位**: 本文件是 `LITERATURE_ANCHORS_2026-06-13.md`(主编, 143 条)、`LITERATURE_ANCHORS_SUPPLEMENT_2026-06-21.md`(补编, 102 条)、`LITERATURE_ANCHORS_EXPANSION_2026-06-22.md`(第二补编, 63 条)、`LITERATURE_ANCHORS_SUPPLEMENT_III_2026-06-24.md`(第三补编, 108 条)、`LITERATURE_ANCHORS_SUPPLEMENT_IV_2026-06-26.md`(第四补编, 2 条)、`LITERATURE_ANCHORS_SUPPLEMENT_V_2026-07-01.md`(第五补编, 111 条)之后的 **第六补编**, 七者**合为一套**。前六份已建成 **527 条已核验锚点 / 507 个唯一 doi.org DOI**。
- **本补编专项**: 补齐 **2026-07-01(第五补编)之后落地的一批新指标/新方法/新阈值**的学术出处。这些是 07-02 至 07-06 六天内提交的功能, 第五补编尚未覆盖:
  1. **政治词权重敏感性梯度** (du_2022 `political_positive` 权重 ∈ {0.0, 0.5, 1.0} 三者互为稳健性, commit 9455f64d)
  2. **BERT 概率分布形状五族** (归一化熵 `tone_entropy` / 极端负面阈值梯子 `xneg_frac` τ∈{.80,.90,.95} / 净语调偏度 `net_tone_skew` / 跨模型分歧 `bert_xmodel_{lblhet,disp}` / 年内噪声校正波动 `nt_iyvol` + 趋势 `nt_iytrend`, commit 56118801)
  3. **LLM 三家 / BERT 三模型互为稳健性 + 跨模型 FWER (Romano–Wolf) + z-score 标准化可比** (commit 6805475a)
  4. **多设定稳健性梯子的方法论正当性** (规格曲线 / 多元宇宙 / 研究者自由度 —— 政治权重/规则消融/阈值/cutoff/窗口/top-k 六族梯子共同的方法学依据)
  5. **网络构造判据敏感性** (同篇/±1 句窗/严格同句三判据并排, commit 17c8f0d4)
  6. **罕见词频次 cutoff 梯子 + 前视陈述 FLS 单/双门二臂** (`rare_word_ratio` cutoff∈{2,3,5} / `frac_fls` 双门 vs `frac_fls_fonly` 单门, commit 41886246)
  7. **strategic_diff top-k N 邻居敏感性** (N∈{10,20,30,40,50}, commit 6857c068)
  8. **人工标注选择性抽样加权** (负面类过采样 + Manski–Lerman 型再加权, commit fbacc13c)
- **规模**: 9 主题桶并行动态多智能体工作流发现 → 每候选 Crossref/DataCite DOI→标题自核验 + claim-fit 诚实性检验 → 主控**逐条直连 Crossref/DataCite 回填权威元数据**(作者序/年份/卷期/页码/标题) → 全语料去重(剔与前六份重叠 20+ 条 + 桶间自重)= **净增 85 条唯一锚点**, 其中 **≥2020 者约 55 条、2024–2026 者 39 条**; 工作论文 16 条(arXiv 13 + NBER 2 + SSRN 1)。
- **核验铁律**: "查不实=不存在", **严禁自我生成参考文献**。本补编经**三道独立核验 + 一道元数据回填**:
  1. 发现层每候选提名前实时 `GET api.crossref.org/works/{DOI}`(arXiv 走 `api.datacite.org`)读回标题自比对;
  2. 主控**逐条直连 Crossref/DataCite 回填权威书目元数据**(不采信智能体转写), 据此撰写 APA —— 此步**捕获并剔除 2 条**: ① `10.1002/ijfe.3113` Crossref 作者字段错乱/倒置(书目不可靠, 避险剔除); ② `10.48550/arXiv.1812.09522`(智能体误报为 Cong "Textual Factors", DataCite 实际解析为物理论文 "How to produce new superheavy nuclei?" —— DOI 张冠李戴, 剔除, 且 Cong "Textual Factors" 已由第五补编 NBER w33168 版收录);
  3. 全语料本地核验(决定性闸): `scripts/audit/audit_dois.py` 直连 Crossref/DataCite, 对全套唯一 DOI 逐条 DOI→标题逐字回比 + 年份核验;
  4. 元数据回填同时**修正多条年份为最新印刷年**(Athanasakou–Walker → 2025、Anastasiou 等 → 2026、Chae–Davidson → 2026 等), 使 APA 年份与 Crossref 回读年一致、零 YEAR_DIFF。
- **合计**: 527(前六份)+ **85(本补编净增)** = **612 条**唯一文献锚点 / **592 个唯一 doi.org DOI**(全语料 `audit_dois.py` 实测为准)。

---

## 〇、白话导读

**这份补的是什么**: 前六份把项目到 v3.15.0 为止的方法都配齐了(527 条)。但 7 月 2 日到 6 日这几天又新做了一批**指标和阈值**——尤其是把三个中文 BERT 的概率分布"形状"(它有多犹豫=熵、有没有极端唱衰=尾部、坏话集不集中=偏度、三个模型吵不吵架=分歧、年内先扬后抑=趋势)全算成了面板列, 又把"政治正面词打半权""罕见词频次门槛""前视句单门/双门""top-k 邻居个数""共现窗口宽窄"等一串**研究者自由度**都做成了并排梯子。这些新东西需要各自的学术出处。这份就专门补这些。

**和"严禁自我生成"的关系**: 每一条**都不是编的**。发现时智能体先查一遍官方接口, 之后主控又**逐条直连 Crossref/DataCite 把作者、年份、卷期、页码、标题原样拉回来**再写 APA(不信智能体的转写)。这一步当场抓出并扔掉了 2 条——一条作者字段乱、一条 DOI 指到了一篇**物理学论文**。最后本地脚本再全量复核一遍。每条后面的"回读标题"就是接口实际回读值。

**怎么用**: 写论文时按 §一各主题桶直接引用; 参考文献表抄各条 APA(已是第 7 版成品、DOI 全可点开)。**勿沿用代码注释里的旧版引用**。

**一句话铁律提醒**: 本补编覆盖的六族稳健性梯子(政治权重/规则消融/阈值/cutoff/窗口/top-k/跨模型)——**各梯级各自 just-identified 并排, 严禁混进同一 over-identified Hansen J**。这条与代码里的铁律一致, 引用时须在方法节写明。

---

## 一、9 主题桶 × 新增已核验锚点(2024–2026 优先)

### 六补-1. 分类器输出熵 / 模糊性-不确定性构念 (BERT `tone_entropy`)

> 净增 13 条(其中 6 条 2024–2026)。构念家族: Shannon 熵作模型不确定性(核心公式 Shannon 1948 已在前编收录, 此处不重列)。

- 【2024–2026】Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y. (2024). Detecting hallucinations in large language models using semantic entropy. *Nature, 630*(8017), 625–630. https://doi.org/10.1038/s41586-024-07421-0
  - *锚定* — `{bert}_tone_entropy` 的顶刊级近期背书(method-analog): 证明"模型输出分布的熵"是可用的不确定性信号。注: 该文对采样生成做语义聚类后算熵, 与本项目对固定情感类 softmax 向量算 Shannon 熵的输出空间不同, 属"输出熵=不确定性"同一原理的不同实现。
  - 〔Crossref 回读标题: Detecting hallucinations in large language models using semantic entropy〕
- Hüllermeier, E., & Waegeman, W. (2021). Aleatoric and epistemic uncertainty in machine learning: An introduction to concepts and methods. *Machine Learning, 110*(3), 457–506. https://doi.org/10.1007/s10994-021-05946-3
  - *锚定* — `{bert}_tone_entropy` 的构念形式化锚(method-formalization): 确立"分类器 softmax 预测分布的 Shannon 熵度量总预测不确定性"这一 ML 标准解释(熵公式本身源自 Shannon 1948, 已在前编收录; 本文非熵的数学起源而是其"作预测不确定性"的权威表述)。注: 该文进一步把熵分解为 aleatoric+epistemic 两分量, 本项目只用未分解的总熵。
  - 〔Crossref 回读标题: Aleatoric and epistemic uncertainty in machine learning: an introduction to concepts and methods〕
- 【2024–2026】Peng, C.-Y. (2025). Information-processing entropy and heterogeneous sentiment reaction windows: Evidence from S&P 500 stocks. *Entropy, 27*(12), Article 1234. https://doi.org/10.3390/e27121234
  - *锚定* — 最贴近的近期金融平行: 把 FinBERT 情感分类与信息论熵耦合进资产定价。注: 熵用于跨股信息传导/反应动态, 非逐篇 softmax 向量的熵, 属平行构念。
  - 〔Crossref 回读标题: Information-Processing Entropy and Heterogeneous Sentiment Reaction Windows: Evidence from S&P 500 Stocks〕
- 【2024–2026】Black, J. R., Irtisam, R., & Jain, P. K. (2025). Textual uncertainty in financial disclosures and information asymmetry among investors. *Financial Review, 60*(3), 799–829. https://doi.org/10.1111/fire.12430
  - *锚定* — 文本不确定性经济后果的近期证据(为何篇级语调模糊在银行-年层面重要)。注: 其"文本不确定性"为词典法(uncertainty/modal 词), 非分类器输出熵, 锚经济构念而非估计量。
  - 〔Crossref 回读标题: Textual uncertainty in financial disclosures and information asymmetry among investors〕
- 【2024–2026】Eggen, S., Espe, T. J., Grude, K., Risstad, M., & Sandberg, R. (2026). Financial time series uncertainty: A review of probabilistic AI applications. *Journal of Economic Surveys, 40*(2), 915–953. https://doi.org/10.1111/joes.70018
  - *锚定* — 把概率式 AI 不确定性量化(含熵基测度)置于金融机器学习不确定性文献之中的近期综述, 定位分类器熵的文献坐标。注: 综述, 非对新闻情感分类器熵的直接应用。
  - 〔Crossref 回读标题: Financial Time Series Uncertainty: A Review of Probabilistic AI Applications〕
- 【2024–2026】Frijns, B., Indriawan, I., Tourani-Rad, A., & Zhang, H. (2026). Analyst forecast dispersion and market quality surrounding the FOMC announcement. *Financial Review, 61*(2), 513–531. https://doi.org/10.1111/fire.70030
  - *锚定* — 近期金融用跨预测者离散度(分歧)作不确定性代理, 平行支撑"离散/分歧=不确定性"逻辑(呼应熵作模糊信号)。注: 离散度跨人类分析师点预测, 非单分类器概率输出的熵; 该"分歧=不确定性"构念与六补-5(跨模型分歧)邻接, 此处仅取"离散→不确定性"的动机层类比。
  - 〔Crossref 回读标题: Analyst Forecast Dispersion and Market Quality Surrounding the FOMC Announcement〕
- 【2024–2026】Wei, X., & Zhang, Q. (2025). *Narrative ambiguity matters* (SSRN Working Paper No. 5337268). SSRN. https://doi.org/10.2139/ssrn.5337268
  - *锚定* — 近期工作论文把文本/叙事模糊性作可定价构念, 支撑把模型语调模糊解读为经济上有信息。注: SSRN 工作论文(未经同行评审); 模糊在叙事/行业层操作化, 非逐篇分类器熵。
  - 〔Crossref 回读标题: Narrative Ambiguity Matters〕
- Epstein, L. G., & Schneider, M. (2008). Ambiguity, information quality, and asset pricing. *The Journal of Finance, 63*(1), 197–228. https://doi.org/10.1111/j.1540-6261.2008.01314.x
  - *锚定* — 模糊(Knightian 不确定性)被资产市场定价的经济构念根基, 支撑"模型对语调的模糊也可能载有经济内容"。注: 结构式模糊厌恶资产定价模型, 非文本测度。
  - 〔Crossref 回读标题: Ambiguity, Information Quality, and Asset Pricing〕
- Ilut, C. L., & Schneider, M. (2014). Ambiguous business cycles. *American Economic Review, 104*(8), 2368–2399. https://doi.org/10.1257/aer.104.8.2368
  - *锚定* — 模糊驱动宏观波动, 支撑把模型模糊看作有意义的不确定性通道而非噪声。注: 含模糊厌恶主体的 DSGE 模型, 非文本测度。
  - 〔Crossref 回读标题: Ambiguous Business Cycles〕
- Ellsberg, D. (1961). Risk, ambiguity, and the Savage axioms. *The Quarterly Journal of Economics, 75*(4), 643–669. https://doi.org/10.2307/1884324
  - *锚定* — 风险 vs 模糊(Knightian 不确定性)的奠基性区分, 为"模型对语调有多模糊"作为信息量提供理论根基。注: 理论根基, 非测度方法。
  - 〔Crossref 回读标题: Risk, Ambiguity, and the Savage Axioms〕
- Ertugrul, M., Lei, J., Qiu, J., & Wan, C. (2017). Annual report readability, tone ambiguity, and the cost of borrowing. *Journal of Financial and Quantitative Analysis, 52*(2), 811–836. https://doi.org/10.1017/S0022109017000187
  - *锚定* — 最贴近"语调模糊 → 融资成本"链条的构念+结果匹配(呼应 P1 `funding_cost` DV)。注: 模糊为词典法(不确定/弱情态词计数), 非分类器输出熵。
  - 〔Crossref 回读标题: Annual Report Readability, Tone Ambiguity, and the Cost of Borrowing〕
- Jurado, K., Ludvigson, S. C., & Ng, S. (2015). Measuring uncertainty. *American Economic Review, 105*(3), 1177–1216. https://doi.org/10.1257/aer.20131193
  - *锚定* — 把不确定性定义为结果的条件离散/不可预测度, 与熵操作化的"预测分布展开=不确定性"信息论直觉同源。注: 宏观序列的预测误差方差估计量, 非文本分类器熵。
  - 〔Crossref 回读标题: Measuring Uncertainty〕
- Bloom, N. (2009). The impact of uncertainty shocks. *Econometrica, 77*(3), 623–685. https://doi.org/10.3982/ECTA6248
  - *锚定* — 已测不确定性有真实经济效应的经典证据, 支撑把不确定性/模糊测度作为经济上有意义的回归变量。注: 不确定性以股市波动率代理, 非文本熵。
  - 〔Crossref 回读标题: The Impact of Uncertainty Shocks〕

### 六补-2. 极端负面尾部占比 / 阈值超越 (BERT `xneg_frac` τ∈{.80,.90,.95} 梯子)

> 净增 7 条(其中 4 条 2024–2026)。

- 【2024–2026】van Binsbergen, J. H., Bryzgalova, S., Mukhopadhyay, M., & Sharma, V. (2024). *(Almost) 200 years of news-based economic sentiment* (NBER Working Paper No. 32026). National Bureau of Economic Research. https://doi.org/10.3386/w32026
  - *锚定* — 近期大规模先例: 逐篇机器分类新闻再聚合成情感指数, 与把逐篇 BERT 负面性聚合成银行-年测度平行。注: 报连续情感分, 非尾部/阈值超越占比; 且为未评审工作论文。
  - 〔Crossref 回读标题: (Almost) 200 Years of News-Based Economic Sentiment〕
- 【2024–2026】Derrien, F., Krüger, P., Landier, A., & Yao, T. (2025). ESG news, future cash flows, and firm value. *The Journal of Finance, 80*(6), 3499–3554. https://doi.org/10.1111/jofi.13498
  - *锚定* — 近期顶刊证据: **负面**新闻(而非净语调)载有独特、更大的经济效应, 支撑单独刻画"强负面尾部"而非对称情感均值。注: 负面性为 ESG 新闻事件/分类, 非 BERT 概率越阈。
  - 〔Crossref 回读标题: ESG News, Future Cash Flows, and Firm Value〕
- 【2024–2026】Pham, X. T. T., Huynh, D. T., Nguyen, N. T. K., & Luu, T. B. (2025). Investor negativity derived from news shapes firm distress dynamics under bounded rationality. *Journal of Economics and Development, 27*(4), 309–321. https://doi.org/10.1108/JED-06-2025-0296
  - *锚定* — 直接对口的近期应用: LLM 导出的公司层新闻**负面性**测度对困境有记录在案的**非线性/阈值**效应, 同时支撑负面尾部聚焦与阈值梯度。注: 其阈值作用于结果关系, 非定义本测度的分类器概率。
  - 〔Crossref 回读标题: Investor negativity derived from news shapes firm distress dynamics under bounded rationality〕
- 【2024–2026】Isler, C. (2025). *Words matter: Forecasting economic downside risks with corporate textual data* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2511.04935
  - *锚定* — 2025 先例: 文本语调指标专门用于预测经济结果的**下行/下尾**, 镜像本项目极端负面构念。注: 用 Loughran–McDonald 词计数语调 + 分位(GaR)回归, 非 BERT 概率越阈计数; 未评审 preprint。
  - 〔DataCite 回读标题: Words Matter: Forecasting Economic Downside Risks with Corporate Textual Data〕
- Baker, S. R., Bloom, N., & Davis, S. J. (2016). Measuring economic policy uncertainty. *The Quarterly Journal of Economics, 131*(4), 1593–1636. https://doi.org/10.1093/qje/qjw024
  - *锚定* — **计数式新闻指数的 method-origin**: 指数=满足固定文本判据的报道**占比**, 是"负面性越阈报道占比"最贴近的结构类比。注: EPU 计关键词共现, 非分类器打分越阈。
  - 〔Crossref 回读标题: Measuring Economic Policy Uncertainty〕
- García, D. (2013). Sentiment during recessions. *The Journal of Finance, 68*(3), 1267–1300. https://doi.org/10.1111/jofi.12027
  - *锚定* — 证明新闻的负面语调占比载有增量、状态依赖(危机期)信息, 支撑设专门的强负面测度而非对称均值。注: 连续负面词占比, 非概率越阈计数。
  - 〔Crossref 回读标题: Sentiment during Recessions〕
- Manela, A., & Moreira, A. (2017). News implied volatility and disaster concerns. *Journal of Financial Economics, 123*(1), 137–162. https://doi.org/10.1016/j.jfineco.2016.01.032
  - *锚定* — 纯从新闻文本提取尾部/灾难风险信号(NVIX)的奠基例, 与极端负面占比同源"文本→极端风险"直觉。注: NVIX 是对隐含波动率的 SVR, 类比在尾部构念而非阈值占比构造。
  - 〔Crossref 回读标题: News implied volatility and disaster concerns〕

### 六补-3. 情感得分偏度 / 分布高阶矩 (BERT `net_tone_skew`, ⚠ raw skew 非 NCSKEW)

> 净增 10 条(其中 4 条 2024–2026)。⚠ 本列为 raw Fisher–Pearson 偏度(正=右偏), **非**金融 NCSKEW(收益率负偏系数); 崩盘风险谱系仅作分布矩方法学移植, 构念含义不继承。

- 【2024–2026】Babiak, M., Baruník, J., & Kurka, J. (2026). *Skewness dispersion and stock market returns* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2604.07870
  - *锚定* — 支撑"分布偏度是可利用信息量"的一般前提(该文用已实现收益率偏度的截面离散度)。注: 为收益率偏度(及其离散度)非情感偏度、非 NCSKEW; 共享的只是"偏度载有信息"。
  - 〔DataCite 回读标题: Skewness Dispersion and Stock Market Returns〕
- 【2024–2026】Anastasiou, D., Katsafados, A., & Tzomakas, C. (2026). Banks' stock price crash risk prediction with textual analysis: A machine learning approach. *Annals of Operations Research, 357*(1), 89–111. https://doi.org/10.1007/s10479-025-06567-y
  - *锚定* — 同域(银行)把文本特征连到崩盘风险/左尾结果, 支撑"银行新闻文本→坏消息集中"的直觉。注: 预测收益率崩盘风险结果, 非情感分布偏度; 谱系/类比而非同构。
  - 〔Crossref 回读标题: Banks' stock price crash risk prediction with textual analysis: a machine learning approach〕
- 【2024–2026】Xiang, R., Song, C., Lin, R., & Shen, L. (2025). Visual annual reports and stock price crash risk. *Accounting & Finance, 65*(2), 2035–2064. https://doi.org/10.1111/acfi.13402
  - *锚定* — 近期中国市场证据把披露文本/视觉特征连到崩盘风险(收益率左偏), 强化披露语调→偏态结果谱系。注: 结果为收益率崩盘风险, 非公司内语调分布偏度; raw-skew vs NCSKEW 之别适用。
  - 〔Crossref 回读标题: Visual annual reports and stock price crash risk〕
- 【2024–2026】Athanasakou, V., & Walker, M. (2025). A measure of management's withholding of bad news. *European Accounting Review, 34*(2), 601–635. https://doi.org/10.1080/09638180.2023.2268677
  - *锚定* — 构造公司层坏消息隐瞒测度并对标 NCSKEW/DUVOL 崩盘代理, 直接关系"集中(左偏)负面覆盖=隐瞒/爆发坏消息"的解读。注: 关乎坏消息隐瞒与收益率崩盘代理, 非情感分布偏度。
  - 〔Crossref 回读标题: A Measure of Management's Withholding of Bad News〕
- Chen, J., Hong, H., & Stein, J. C. (2001). Forecasting crashes: Trading volume, past returns, and conditional skewness in stock prices. *Journal of Financial Economics, 61*(3), 345–381. https://doi.org/10.1016/S0304-405X(01)00066-6
  - *锚定* — NCSKEW 的经典起源, "用(条件)偏度作为公司分布信息量"的范式案例, 启发"坏消息集中→偏度"的读法。注: 本项目仅移植分布矩方法学; 本列为 raw 偏度(正=右偏), **非** NCSKEW(取负三阶矩使高=更易崩), 符号约定与构念皆异。
  - 〔Crossref 回读标题: Forecasting crashes: trading volume, past returns, and conditional skewness in stock prices〕
- Kim, J.-B., Li, Y., & Zhang, L. (2011). Corporate tax avoidance and stock price crash risk: Firm-level analysis. *Journal of Financial Economics, 100*(3), 639–662. https://doi.org/10.1016/j.jfineco.2010.07.007
  - *锚定* — 用 NCSKEW/DUVOL 证明坏消息囤积产生收益率左偏, 直接激励把银行覆盖的左偏读为"坏消息爆发"。注: 度量收益率偏度(NCSKEW/DUVOL), 非情感分布偏度; 仅崩盘谱系, raw-skew≠NCSKEW。
  - 〔Crossref 回读标题: Corporate tax avoidance and stock price crash risk: Firm-level analysis〕
- Kim, J.-B., Li, Y., & Zhang, L. (2011). CFOs versus CEOs: Equity incentives and crashes. *Journal of Financial Economics, 101*(3), 713–730. https://doi.org/10.1016/j.jfineco.2011.03.013
  - *锚定* — NCSKEW/DUVOL 坏消息囤积谱系第二支柱, 正当化"分布偏度作公司层风险测度"。注: 崩盘收益率偏度, 非情感偏度; 方法谱系, raw-skew≠NCSKEW。
  - 〔Crossref 回读标题: CFOs versus CEOs: Equity incentives and crashes〕
- Hutton, A. P., Marcus, A. J., & Tehranian, H. (2009). Opaque financial reports, R2, and crash risk. *Journal of Financial Economics, 94*(1), 67–86. https://doi.org/10.1016/j.jfineco.2008.10.003
  - *锚定* — 从不透明度操作化收益率负偏(NCSKEW/DUVOL)的奠基崩盘论文, 确立"收益率偏度"为信息对象, 本项目语调偏度方法学呼应。注: 收益率偏度, 非情感偏度; raw-skew vs NCSKEW 之别适用。
  - 〔Crossref 回读标题: Opaque financial reports, R2, and crash risk〕
- Wright, D. B., & Herrington, J. A. (2011). Problematic standard errors and confidence intervals for skewness and kurtosis. *Behavior Research Methods, 43*(1), 8–17. https://doi.org/10.3758/s13428-010-0044-x
  - *锚定* — 直接支撑 `SKEW_MIN_N=10` 掩码: 证明样本三阶矩在小/非正态 n 下估计不精、闭式标准误不可靠(建议 bootstrap)。注: 统计方法学(非金融), 正当化最小-n 掩码的可靠性关切, 但不背书具体阈值 10。
  - 〔Crossref 回读标题: Problematic standard errors and confidence intervals for skewness and kurtosis〕
- Piovesana, A., & Senior, G. (2018). How small is big: Sample size and skewness. *Assessment, 25*(6), 793–800. https://doi.org/10.1177/1073191116669784
  - *锚定* — 量化样本量如何支配偏态下矩估计稳定性, 为小 n 掩码提供概念根据。注: 心理测量/常模语境; 其稳定性阈约 n>85, 故本项目 n≥10 只是宽松噪声地板, **非**"可靠估计"门槛——引用其原则而非验证 10。
  - 〔Crossref 回读标题: How Small Is Big: Sample Size and Skewness〕

### 六补-4. 组内噪声校正方差 / 情感波动 / 年内趋势 (BERT `nt_iyvol` / `nt_iytrend`)

> 净增 10 条(其中 5 条 2024–2026)。构念: `nt_iyvol` = 减去池化组内抽样方差(双 ddof=1)的年内月度净语调方差; `nt_iytrend` = 闭式 OLS 斜率(≥6 有效月)。

- Chetty, R., Friedman, J. N., & Rockoff, J. E. (2014). Measuring the impacts of teachers I: Evaluating bias in teacher value-added estimates. *American Economic Review, 104*(9), 2593–2632. https://doi.org/10.1257/aer.104.9.2593
  - *锚定* — `nt_iyvol` 估计量最干净的教科书实例: 真效应方差 = 观测跨单元方差 **减去** 噪声逐单元估计的平均抽样方差。注: 单元是教师非年内月度语调, 锚方法非金融应用。
  - 〔Crossref 回读标题: Measuring the Impacts of Teachers I: Evaluating Bias in Teacher Value-Added Estimates〕
- Kane, T. J., & Staiger, D. O. (2002). The promise and pitfalls of using imprecise school accountability measures. *Journal of Economic Perspectives, 16*(4), 91–114. https://doi.org/10.1257/089533002320950993
  - *锚定* — `nt_iyvol` 尤其其小-n 门槛: 奠基性陈述——每单元计数小时, 实测跨单元离散被抽样噪声抬高, 须向下调整原始方差。注: 教育问责语境, 方法学先例非情感论文。
  - 〔Crossref 回读标题: The Promise and Pitfalls of Using Imprecise School Accountability Measures〕
- Zhang, L., Mykland, P. A., & Aït-Sahalia, Y. (2005). A tale of two time scales: Determining integrated volatility with noisy high-frequency data. *Journal of the American Statistical Association, 100*(472), 1394–1411. https://doi.org/10.1198/016214505000000169
  - *锚定* — "估计波动率 = 真波动率 + 噪声方差; 减噪声还原真量"的金融计量原型, 与减池化组内抽样方差直接结构类比。注: 高频价格微结构噪声非月度篇数噪声, 代数可移、设定不同。
  - 〔Crossref 回读标题: A Tale of Two Time Scales: Determining Integrated Volatility With Noisy High-Frequency Data〕
- 【2024–2026】Walters, C. (2024). *Empirical Bayes methods in labor economics* (NBER Working Paper No. 33091). National Bureau of Economic Research. https://doi.org/10.3386/w33091
  - *锚定* — `nt_iyvol` 所处收缩/信号加噪声方差成分机制的当代综述(真方差=总方差−抽样方差)。注: NBER 工作论文, 劳动经济学框架, 支撑方法时新性而非情感应用。
  - 〔Crossref 回读标题: Empirical Bayes Methods in Labor Economics〕
- Da, Z., Engelberg, J., & Gao, P. (2015). The sum of all FEARS investor sentiment and asset prices. *The Review of Financial Studies, 28*(1), 1–32. https://doi.org/10.1093/rfs/hhu072
  - *锚定* — `nt_iyvol` + `nt_iytrend` 共同的**月频构造前提**: 构造月度文本情感序列并研究其动态(水平/波动/漂移)的经典先例。注: 搜索量 FEARS 非银行新闻 BERT 语调, 立月度聚合实践非噪声调整。
  - 〔Crossref 回读标题: The Sum of All FEARS Investor Sentiment and Asset Prices〕
- 【2024–2026】Garcia, J. (2025). Beyond the headlines: Sentiment divergence and financial distress. *Global Finance Journal, 66*, Article 101126. https://doi.org/10.1016/j.gfj.2025.101126
  - *锚定* — `nt_iyvol` 近期同类: 用跨源情感离散/分歧作公司层困境信号, 最贴近"语调离散有意义"。注: 其离散轴为**跨源(横截面)分歧**, 与 `nt_iyvol` 的**年内月度时间序列方差**是不同离散轴; 中层期刊, 仅作"语调离散载有信息"的动机层参照。
  - 〔Crossref 回读标题: Beyond the headlines: Sentiment divergence and financial distress〕
- 【2024–2026】Bodilsen, S. T., & Lunde, A. (2025). Exploiting news analytics for volatility forecasting. *Journal of Applied Econometrics, 40*(1), 18–36. https://doi.org/10.1002/jae.3095
  - *锚定* — `nt_iyvol` 近期证据: 聚合新闻情感分析载有关于**波动率**的信息, 支撑把语调导出的波动特征当作有信息。注: 从新闻预测价格波动, 非语调序列自身的方差。
  - 〔Crossref 回读标题: Exploiting News Analytics for Volatility Forecasting〕
- 【2024–2026】Baker, S. R., Bloom, N., Davis, S. J., & Kost, K. (2026). Policy news and stock market volatility. *Journal of Financial Economics, 175*, Article 104187. https://doi.org/10.1016/j.jfineco.2025.104187
  - *锚定* — `nt_iyvol` 近期顶刊: 新闻文本→市场波动, 强化"新闻语言变动是合法的波动相关信号"。注: 宏观/政策新闻→总波动, 非银行内语调方差。
  - 〔Crossref 回读标题: Policy news and stock market volatility〕
- 【2024–2026】Aksoy-Yurdagul, D., Buchner, A., & Zareei, A. (2026). The persistence of news sentiment: Implications for return predictability. *Economics Letters, 260*, Article 112803. https://doi.org/10.1016/j.econlet.2025.112803
  - *锚定* — `nt_iytrend` 近期直接相关: 关注新闻情感的**时间轨迹**(持续/动量 vs 反转), 即年内斜率所刻画的语调漂移。注: 建模持续/动量非字面年内 OLS 斜率; 短文 Economics Letters。
  - 〔Crossref 回读标题: The persistence of news sentiment: Implications for return predictability〕
- Heston, S. L., & Sinha, N. R. (2017). News vs. sentiment: Predicting stock returns from news stories. *Financial Analysts Journal, 73*(3), 67–83. https://doi.org/10.2469/faj.v73.n3.3
  - *锚定* — `nt_iytrend`: 研究情感在一段跨度上聚合(其持续/衰减)如何预测收益, 即年内斜率背后的语调漂移思想。注: 跨度聚合与衰减, 非显式拟合趋势线。
  - 〔Crossref 回读标题: News vs. Sentiment: Predicting Stock Returns from News Stories〕

### 六补-5. 跨模型分歧作为测度 · 多分类器一致性 · 跨模型 FWER(Romano–Wolf) · 标准化可比 (`bert_xmodel_{lblhet,disp}`, 三家 LLM/三 BERT 互为稳健性)

> 净增 14 条(其中 6 条 2024–2026)。⚠ 各家/各模型各自 just-identified 并排, 禁混同一 over-identified Hansen J; 真 FWER=根级 `27_tableA12` Romano–Wolf 模板。

- Diether, K. B., Malloy, C. J., & Scherbina, A. (2002). Differences of opinion and the cross section of stock returns. *The Journal of Finance, 57*(5), 2113–2141. https://doi.org/10.1111/0022-1082.00490
  - *锚定* — `bert_xmodel_{lblhet,disp}` 的典范类比: "知情主体分歧时, 分歧本身被定价/有信息", 对应把跨模型符号分歧当信号。注: 其分歧为分析师预测离散, 非模型标签异质; 概念类比非同构。
  - 〔Crossref 回读标题: Differences of Opinion and the Cross Section of Stock Returns〕
- Hong, H., & Stein, J. C. (2007). Disagreement and the stock market. *Journal of Economic Perspectives, 21*(2), 109–128. https://doi.org/10.1257/jep.21.2.109
  - *锚定* — 综述级正当性: 异质信念/分歧是一阶、有信息的经济量, 支撑把跨分类器分歧看作实质有意义而非纯噪声。注: 投资者信念离散, 非测度模型分歧。
  - 〔Crossref 回读标题: Disagreement and the Stock Market〕
- Cen, L., Wei, K. C. J., & Yang, L. (2017). Disagreement, underreaction, and stock returns. *Management Science, 63*(4), 1214–1231. https://doi.org/10.1287/mnsc.2015.2405
  - *锚定* — 分歧载有条件、可分解信息(与反应不足交互), 平行"把分歧报成独立测度而非坍缩为共识票"。注: 分析师预测分歧。
  - 〔Crossref 回读标题: Disagreement, Underreaction, and Stock Returns〕
- Uma, A. N., Fornaciari, T., Hovy, D., Paun, S., Plank, B., & Poesio, M. (2021). Learning from disagreement: A survey. *Journal of Artificial Intelligence Research, 72*, 1385–1470. https://doi.org/10.1613/jair.1.12752
  - *锚定* — NLP 侧最贴近: 形式化"标注者分歧是信号非误差", 为 `bert_xmodel_lblhet` 提供 NLP 理论。注: 关乎人类标注者变异, 本项目外推到独立模型标注者(合理但非同一)。
  - 〔Crossref 回读标题: Learning from Disagreement: A Survey〕
- Plaza-del-Arco, F. M., Nozza, D., & Hovy, D. (2023). *Wisdom of instruction-tuned language model crowds: Exploring model label variation* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2307.12973
  - *锚定* — 最紧的同类: 明确研究跨指令微调 LLM 的**模型**(非人类)标签变异, 对应度量三分类器间离散。注: preprint; LLM 而非微调中文金融 BERT。
  - 〔DataCite 回读标题: Wisdom of Instruction-Tuned Language Model Crowds. Exploring Model Label Variation〕
- 【2024–2026】Ziems, C., Held, W., Shaikh, O., Chen, J., Zhang, Z., & Yang, D. (2024). Can large language models transform computational social science? *Computational Linguistics, 50*(1), 237–291. https://doi.org/10.1162/coli_a_00502
  - *锚定* — 同行评审基准: LLM 作文本分类器跨 CSS 任务, 激励社科测度管线中的多模型评估与一致性报告。注: 方法学基准综述, 非跨模型分歧测度构造。
  - 〔Crossref 回读标题: Can Large Language Models Transform Computational Social Science?〕
- 【2024–2026】Bavaresco, A., Bernardi, R., Bertolazzi, L., Elliott, D., Fernández, R., Gatt, A., Ghaleb, E., Giulianelli, M., Hanna, M., Koller, A., Martins, A. F. T., Mondorf, P., Neplenbroek, V., Pezzelle, S., Plank, B., Schlangen, D., Suglia, A., Surikuchi, A. K., Takmaz, E., & Testoni, A. (2024). *LLMs instead of human judges? A large scale empirical study across 20 NLP evaluation tasks* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2406.18403
  - *锚定* — 大规模多模型多厂商一致性研究, 为"多模型并排、不分主次"并报跨模型一致性提供经验根据。注: preprint; 评审-judge 设定非金融情感。
  - 〔DataCite 回读标题: LLMs instead of Human Judges? A Large Scale Empirical Study across 20 NLP Evaluation Tasks〕
- 【2024–2026】Amiri-Margavi, A., Jebellat, I., Jebellat, E., & Mousavi Davoudi, S. P. (2024). *Enhancing answer reliability through inter-model consensus of large language models* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2411.16797
  - *锚定* — 构念最紧: 明确把"跨独立 LLM 的模型间共识 vs 分歧"作信息量/可靠性信号, 近乎逐字对应 `bert_xmodel_*` 动机。注: preprint, 中等场所; QA 可靠性非情感分类。
  - 〔DataCite 回读标题: Enhancing Answer Reliability Through Inter-Model Consensus of Large Language Models〕
- 【2024–2026】Niimi, J. (2025). *A simple ensemble strategy for LLM inference: Towards more stable text classification* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2504.18884
  - *锚定* — 多次/多模型聚合(多数票式)稳定文本分类, 支撑"三 co-equal 子测度/互为稳健"设计。注: preprint; 推断稳定性非分歧作结果测度。
  - 〔DataCite 回读标题: A Simple Ensemble Strategy for LLM Inference: Towards More Stable Text Classification〕
- 【2024–2026】Schlee, M., Weisser, C., Kivimäki, T., Mashiku, M., & Saefken, B. (2025). *LabelFusion: Fusing large language models with transformer encoders for robust financial news classification* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2512.10793
  - *锚定* — 直接同域: 组合多模型做**稳健金融新闻**分类, 是把多模型稳健性系到本项目确切任务的最佳近期锚。注: preprint; 融合/集成而非分歧测度构造。
  - 〔DataCite 回读标题: LabelFusion: Fusing Large Language Models with Transformer Encoders for Robust Financial News Classification〕
- 【2024–2026】Chae, Y., & Davidson, T. (2026). Large language models for text classification: From zero-shot learning to instruction-tuning. *Sociological Methods & Research, 55*(2), 501–567. https://doi.org/10.1177/00491241251325243
  - *锚定* — 同行评审方法参照: 在社科测度中用(多个)LLM 作文本分类器, 支撑 co-equal 多分类器框架。注: 本身不构造跨模型分歧测度。
  - 〔Crossref 回读标题: Large Language Models for Text Classification: From Zero-Shot Learning to Instruction-Tuning〕
- Clarke, D., Romano, J. P., & Wolf, M. (2020). The Romano–Wolf multiple-hypothesis correction in Stata. *The Stata Journal, 20*(4), 812–843. https://doi.org/10.1177/1536867X20976314
  - *锚定* — `27_tableA12_cross_model_fwer` 模板底层 `rwolf` 命令的**确切软件实现**参照。注: 实现引文——与 Romano & Wolf(2005/2016, 已在前编)并引。
  - 〔Crossref 回读标题: The Romano–Wolf multiple-hypothesis correction in Stata〕
- Harvey, C. R., Liu, Y., & Zhu, H. (2016). … and the cross-section of expected returns. *The Review of Financial Studies, 29*(1), 5–68. https://doi.org/10.1093/rfs/hhv059
  - *锚定* — 金融侧多重检验纪律权威: 检验众多候选信号时须控 FWER(含 Romano–Wolf), 正当化对 co-equal 跨模型 β 族做 FWER。注: 关乎因子多重性; 在线 2015-10 印刷 2016。
  - 〔Crossref 回读标题: … and the Cross-Section of Expected Returns〕
- Gelman, A. (2008). Scaling regression inputs by dividing by two standard deviations. *Statistics in Medicine, 27*(15), 2865–2873. https://doi.org/10.1002/sim.3107
  - *锚定* — 跨模型/规格比较前标准化系数的经典正当性: 支撑对 β z-score 化, 使 2 分类 vs 3 分类模型估计可比。注: 该文主张 2-SD 缩放, 本项目 1-SD z-score 是同一原理的常见变体。
  - 〔Crossref 回读标题: Scaling regression inputs by dividing by two standard deviations〕

### 六补-6. 多设定稳健性 / 规格曲线 / 多元宇宙 / 研究者自由度 (政治权重·规则消融·阈值·cutoff·窗口·top-k 六族梯子共同方法学)

> 净增 14 条(其中 2 条 2024–2026, 但方法奠基文献不可替代)。为并排物化全部合理分析选择(而非单一任意选)的方法学正当性 —— 抗规格搜索/p-hacking。

- Simonsohn, U., Simmons, J. P., & Nelson, L. D. (2020). Specification curve analysis. *Nature Human Behaviour, 4*(11), 1208–1214. https://doi.org/10.1038/s41562-020-0912-z
  - *锚定* — 并排报告全部合理设定(项目各梯子)+跨设定联合推断的直接锚。注: 其第 3 步联合推断检验强于本项目"互为稳健、不分主次"的描述性并列——引用其报告哲学, 非主张运行了其置换推断。
  - 〔Crossref 回读标题: Specification curve analysis〕
- Steegen, S., Tuerlinckx, F., Gelman, A., & Vanpaemel, W. (2016). Increasing transparency through a multiverse analysis. *Perspectives on Psychological Science, 11*(5), 702–712. https://doi.org/10.1177/1745691616658637
  - *锚定* — 把每个研究者自由度(窗口判据/cutoff/权重)当分支、报告整格合理数据处理选择。注: 其多元宇宙侧重数据构造分叉; 本项目权重/阈值梯子是其合法子集, 非全笛卡尔多元宇宙。
  - 〔Crossref 回读标题: Increasing Transparency Through a Multiverse Analysis〕
- Del Giudice, M., & Gangestad, S. W. (2021). A traveler's guide to the multiverse: Promises, pitfalls, and a framework for the evaluation of analytic decisions. *Advances in Methods and Practices in Psychological Science, 4*(1), Article 2515245920954925. https://doi.org/10.1177/2515245920954925
  - *锚定* — 要求梯子分支须为等价/可辩护选择(非任意), 支撑"不分主次"框架与只对理论合理选项设梯子的纪律。注: 批判性框架, 用以正当化"哪些"选项设梯而非全盘背书。
  - 〔Crossref 回读标题: A Traveler's Guide to the Multiverse: Promises, Pitfalls, and a Framework for the Evaluation of Analytic Decisions〕
- Simonsohn, U., Nelson, L. D., & Simmons, J. P. (2014). P-curve: A key to the file-drawer. *Journal of Experimental Psychology: General, 143*(2), 534–547. https://doi.org/10.1037/a0033242
  - *锚定* — 支撑 p-hacking 可诊断这一动机(为何未报告的灵活性应以全量报告预先杜绝)。注: p-curve 是对一片文献的检测工具, 非本项目梯子模板; 类比 p-hacking 关切。
  - 〔Crossref 回读标题: P-curve: A key to the file-drawer.〕
- Gelman, A., & Loken, E. (2014). The statistical crisis in science. *American Scientist, 102*(6), 460–465. https://doi.org/10.1511/2014.111.460
  - *锚定* — "分叉小径花园"锚: 即便无有意捞取, 潜在数据依赖选择也使单一报告设定失效, 支撑预枚举分叉集为梯子。注: 短评/观点文(American Scientist), 引概念非正式程序。
  - 〔Crossref 回读标题: The Statistical Crisis in Science〕
- Young, C., & Holsteen, K. (2017). Model uncertainty and robustness: A computational framework for multimodel analysis. *Sociological Methods & Research, 46*(1), 3–40. https://doi.org/10.1177/0049124115610347
  - *锚定* — 最贴近计量用法的社科计算稳健性锚: 估计系数跨全部可辩护模型变体的分布而非独尊其一。注: 其框架另报建模分布/稳健比, 略多于并排展示; 在线 2016 印刷 2017。
  - 〔Crossref 回读标题: Model Uncertainty and Robustness: A Computational Framework for Multimodel Analysis〕
- Muñoz, J., & Young, C. (2018). We ran 9 billion regressions: Eliminating false positives through computational model robustness. *Sociological Methodology, 48*(1), 1–33. https://doi.org/10.1177/0081175018777988
  - *锚定* — 强化"跨全部可辩护设定组合空间报告估计"传统及其减假阳性理据, 是本项目梯子的规模化类比。注: 侧重控制集/模型形式枚举; 本项目梯子变的是测度超参数, 精神类比。
  - 〔Crossref 回读标题: We Ran 9 Billion Regressions: Eliminating False Positives through Computational Model Robustness〕
- Angrist, J. D., & Pischke, J.-S. (2010). The credibility revolution in empirical economics: How better research design is taking the con out of econometrics. *Journal of Economic Perspectives, 24*(2), 3–30. https://doi.org/10.1257/jep.24.2.3
  - *锚定* — 无 DOI 的 Leamer(1983)"take the con out"论点的可解析承载: 经济学关于敏感性/规格脆弱性的经典表述, 本项目梯子对其作答。注: 其主旨是研究设计(非多报设定)恢复可信度, 引作经济学传统触石并诚实注明张力。
  - 〔Crossref 回读标题: The Credibility Revolution in Empirical Economics: How Better Research Design is Taking the Con out of Econometrics〕
- Brodeur, A., Cook, N., & Heyes, A. (2020). Methods matter: p-hacking and publication bias in causal analysis in economics. *American Economic Review, 110*(11), 3634–3660. https://doi.org/10.1257/aer.20190687
  - *锚定* — 经济学特定经验证据: 分析/方法灵活性产生可检测的 p-hacking, 是预先承诺梯子而非单一调优设定的领域动机。注: 记录问题(2.1 万检验), 不处方规格曲线报告。
  - 〔Crossref 回读标题: Methods Matter: p-Hacking and Publication Bias in Causal Analysis in Economics〕
- Brodeur, A., Lé, M., Sangnier, M., & Zylberberg, Y. (2016). Star wars: The empirics strike back. *American Economic Journal: Applied Economics, 8*(1), 1–32. https://doi.org/10.1257/app.20150044
  - *锚定* — 经济学显著性阈附近规格/膨胀的互补证据, 支撑"经济学中 p-hacking"前提。注: 关乎已发表检验统计量总体分布, 非稳健性报告配方; 与 Brodeur et al.(2020)并用。
  - 〔Crossref 回读标题: Star Wars: The Empirics Strike Back〕
- Silberzahn, R., Uhlmann, E. L., Martin, D. P., Anselmi, P., Aust, F., Awtrey, E., … Nosek, B. A. (2018). Many analysts, one data set: Making transparent how variations in analytic choices affect results. *Advances in Methods and Practices in Psychological Science, 1*(3), 337–356. https://doi.org/10.1177/2515245917747646
  - *锚定* — 奠基性"多分析者"演示: 仅可辩护分析选择变异即移动结果, 为把自由度暴露为梯子(而非隐藏)提供直接经验依据。注: 研究跨独立团队离散; 本项目梯子是单团队枚举选择, 激励实践而非模板化。
  - 〔Crossref 回读标题: Many Analysts, One Data Set: Making Transparent How Variations in Analytic Choices Affect Results〕
- Breznau, N., Rinke, E. M., Wuttke, A., Nguyen, H. H. V., Adem, M., Adriaans, J., … Żółtak, T. (2022). Observing many researchers using the same data and hypothesis reveals a hidden universe of uncertainty. *Proceedings of the National Academy of Sciences, 119*(44), Article e2203150119. https://doi.org/10.1073/pnas.2203150119
  - *锚定* — 大规模(73 队)近期证据: 分析选择不确定性在很大程度不可约、单一设定不可见, 是报告全梯子作诚实不确定性披露的当代强动机。注: 多分析者设计, 引"隐藏的不确定性宇宙"动机非方法。
  - 〔Crossref 回读标题: Observing many researchers using the same data and hypothesis reveals a hidden universe of uncertainty〕
- 【2024–2026】Valdenegro, D., Yan, J., Dai, D., & Rahal, C. (2025). *RobustiPy: An efficient next generation multiversal library with model selection, averaging, resampling, and explainable artificial intelligence* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2506.19958
  - *锚定* — 2025 多元宇宙/规格曲线工具锚, 证明该法是当下活跃方法学标准(跨设定空间的模型平均+重采样)。注: arXiv preprint(未评审)且为软件论文, 引作实践在续的证据非同行评审权威。
  - 〔DataCite 回读标题: RobustiPy: An efficient next generation multiversal library with model selection, averaging, resampling, and explainable artificial intelligence〕
- 【2024–2026】Mandl, M. M., Becker-Pennrich, A. S., Hinske, L. C., Hoffmann, S., & Boulesteix, A.-L. (2024). *Addressing researcher degrees of freedom through minP adjustment* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2401.11537
  - *锚定* — 2024 方法进展: 对一梯子设定作**联合推断**(minP 多重性调整), 与"若需对并排梯子作有效推断"直接相关。注: arXiv preprint; 其调整比"不分主次"报告更正式, 引作推断前沿并诚实注明本项目作描述性报告而非施 minP。
  - 〔DataCite 回读标题: Addressing researcher degrees of freedom through minP adjustment〕

### 六补-7. 政治语言弱信号 / 政治关联 (du_2022 `political_positive` 0.5 权重)

> 净增 7 条(其中 6 条 2024–2026)。⚠ Du et al.(2022, RoF, doi:10.1093/rof/rfab036)自身已由主编收录, 此处不重列; 本桶锚"政治语言=独特/更弱信号"前提与"按信号强度差异化词权"方法学。

- Piotroski, J. D., Wong, T. J., & Zhang, T. (2017). Political bias in corporate news: The role of conglomeration reform in China. *The Journal of Law and Economics, 60*(1), 173–207. https://doi.org/10.1086/693096
  - *锚定* — 与 0.5 权重理据最贴近的实证陈述: 证明政治偏向/官媒内容比商业内容**增量信息更弱**(发布后市场反应弱、语调-未来绩效相关弱)——正是"政治语言信号更弱→降权"机制。注: 2017(非近年); 作用于报道而非逐词, 支撑机制非具体 0.5。
  - 〔Crossref 回读标题: Political Bias in Corporate News: The Role of Conglomeration Reform in China〕
- 【2024–2026】Xu, Z., Hua, X., & Zhang, T. (2025). Does official media sentiment matter for the stock market? Evidence from China. *Emerging Markets Review, 64*, Article 101234. https://doi.org/10.1016/j.ememar.2024.101234
  - *锚定* — 中国语境证据: 官方/国家媒体情感相对普通情感有独特(常偏反转、少锚定基本面)信息量, 支撑把政治来源/官方语调作应单独加权的不同信号类。注: 度量媒体情感→收益, 非公司文本政治正面词; 支撑"独特/更弱信号类"前提非 0.5。
  - 〔Crossref 回读标题: Does official media sentiment matter for the stock market? Evidence from China〕
- 【2024–2026】Xu, Z., Li, J., Hua, X., & Ren, P. (2024). Is the tone of the government-controlled media valuable for capital market? Evidence from China's new energy industry. *Energy Policy, 184*, Article 113917. https://doi.org/10.1016/j.enpol.2023.113917
  - *锚定* — 直接拷问政府控制(政治对齐)媒体语调是否有资本市场价值, 发现有界/条件信号, 支撑把政治/官方语调与普通语调分离并校准权重。注: 行业特定(新能源); 媒体语调而非公司披露政治正面词。
  - 〔Crossref 回读标题: Is the tone of the government-controlled media valuable for capital market? Evidence from China's new energy industry〕
- 【2024–2026】Ge, E. (2025). Political speeches and stock market performance: Evidence from China. *Journal of Economic Behavior & Organization, 236*, Article 107122. https://doi.org/10.1016/j.jebo.2025.107122
  - *锚定* — 近期中国语境证据: 政治/政府语言(领导人讲话)是独立于普通情感的市场相关信号通道, 支撑把政治词作可分离类而非与普通正面等权合并。注: 政治讲话非公司报告政治正面词; 确立政治语言为独立通道非降权系数。
  - 〔Crossref 回读标题: Political speeches and stock market performance: Evidence from China〕
- 【2024–2026】Gong, T., & Sun, S. (2026). *Slogans or stance? A label-light diagnostic for entrepreneurial-discourse measurement on Chinese SOE speeches* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2605.29188
  - *锚定* — 明确区分中国国企话语中的象征/政治"口号"语言与实质立场, 证明政治-象征措辞载有更弱实质信号, 有力概念支撑对政治正面词降权。注: preprint(未评审); 目标构念为国企话语"企业家精神", 非银行/金科新闻情感打分, 类比在构念层。
  - 〔DataCite 回读标题: Slogans or Stance? A Label-Light Diagnostic for Entrepreneurial-Discourse Measurement on Chinese SOE Speeches〕
- 【2024–2026】Chen, B. (2026). *When certainty is an artifact: Keyword lexicon blindness and the (mis)measurement of rhetorical stance* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2606.26062
  - *锚定* — 证明扁平关键词计数词典会对特定词类过度归因信号(测度赝象), 激励类别特定的再/降权而非等权, 方法学支撑对弱信号类打折。注: preprint; 关乎修辞确定性非政治词, 一般词典加权类比。
  - 〔DataCite 回读标题: When Certainty Is an Artifact: Keyword Lexicon Blindness and the (Mis)Measurement of Rhetorical Stance〕
- 【2024–2026】Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2024). *Sentiment analysis of economic text: A lexicon-based approach* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2411.13958
  - *锚定* — 给词典词赋分级人工标注情感权重于 [−1,1] 而非等权 ±1 的典范, 是"按测得信号强度给词类加权"(此处把弱类折至 0.5)的直接方法学先例。注: preprint; 英文经济文本; 其分级权来自标注非固定政治折扣。
  - 〔DataCite 回读标题: Sentiment Analysis of Economic Text: A Lexicon-Based Approach〕

### 六补-8. 前视陈述 FLS 单/双门 + 罕见词/词频 cutoff 梯子 (`frac_fls`/`frac_fls_fonly`, `rare_word_ratio` cutoff∈{2,3,5})

> 净增 5 条(其中 3 条 2024–2026)。注: FLS method-origin 中 Li(2010, JAR)/Bozanic 等(2018, JAE)及罕见词 method-origin(Loughran–McDonald 2011/2014/2016/2020)已在前编收录; **Muslu 等(2015, MS)为本桶新补的 FLS method-origin**(dedup 实测唯见于本补编)。本桶补齐尚缺者与近期。

- Muslu, V., Radhakrishnan, S., Subramanyam, K. R., & Lim, D. (2015). Forward-looking MD&A disclosures and the information environment. *Management Science, 61*(5), 931–948. https://doi.org/10.1287/mnsc.2014.1921
  - *锚定* — `frac_fls` 的 method-origin: 确立"前视 MD&A 句的分数/强度"作披露测度并连到信息环境, 直接先例于把 FLS 密度作比率型协变量。
  - 〔Crossref 回读标题: Forward-Looking MD&A Disclosures and the Information Environment〕
- 【2024–2026】Wu, Y. (2026). Forward-looking disclosure with and without time frames: Determinants, market responses, and implications. *Journal of Risk and Financial Management, 19*(6), Article 391. https://doi.org/10.3390/jrfm19060391
  - *锚定* — `frac_fls`(双门) vs `frac_fls_fonly`(单门)最直接正当性: 明确按是否带**时间框架线索**区分前视句, 即"未来词∧时间词"(双门) vs 单线索之别。注: 财报电话会语境, 美国企业; 单作者(Yiyang Wu)。
  - 〔Crossref 回读标题: Forward-Looking Disclosure with and Without Time Frames: Determinants, Market Responses, and Implications〕
- 【2024–2026】Liu, T., Zhang, J., & Wu, J. (2026). Forward-looking statements in annual reports and firms' financing constraints: A machine learning approach. *The International Journal of Accounting, 61*(1), Article 2550006. https://doi.org/10.1142/S1094406025500064
  - *锚定* — `frac_fls` 近期先例: 度量年报 FLS 强度比率并连到公司结果(融资约束), 与本项目"前视句占比→银行-年协变量"管线同型。注: ML 分类器操作化, 非规则式双门。
  - 〔Crossref 回读标题: Forward-Looking Statements in Annual Reports and Firms' Financing Constraints: A Machine Learning Approach〕
- 【2024–2026】Loughran, T., & McDonald, B. (2024). Measuring firm complexity. *Journal of Financial and Quantitative Analysis, 59*(6), 2487–2514. https://doi.org/10.1017/S0022109023000716
  - *锚定* — `rare_word_ratio`(cutoff 梯子): 金融文本词基复杂度测量的权威近期处理, 验证罕见/生僻词代理所属族。注: 建具体复杂度指数(商业/技术术语基), 非频次 cutoff 梯子; 在线 2023 印刷 2024。
  - 〔Crossref 回读标题: Measuring Firm Complexity〕
- Brown, S. V., & Tucker, J. W. (2011). Large-sample evidence on firms' year-over-year MD&A modifications. *Journal of Accounting Research, 49*(2), 309–346. https://doi.org/10.1111/j.1475-679X.2010.00396.x
  - *锚定* — `rare_word_ratio`/新颖度: 引入余弦式文本变动测度、把新颖/改动语言当有信息, 支撑新颖词表代理。注: 度量修改幅度, 非词汇罕见度。
  - 〔Crossref 回读标题: Large-Sample Evidence on Firms' Year-over-Year MD&A Modifications〕

### 六补-9. 共现窗口/构造判据敏感性 · top-k 邻居敏感性 · 选择性抽样加权 (网络三判据 / strategic_diff N∈{10..50} / Manski–Lerman 标注加权)

> 净增 5 条(其中 3 条 2024–2026)。注: Manski–Lerman(1977) / King–Zeng(2001) / Hassan(2019) / Sautner(2023) / Hoberg–Phillips(2016) / Li-Mai-Shen-Yan(2021) / Gentzkow-Kelly-Taddy(2019) / Ash-Hansen(2023) / Angelopoulos(2023 PPI)均已在前编收录, 此处不重列。

- Levy, O., Goldberg, Y., & Dagan, I. (2015). Improving distributional similarity with lessons learned from word embeddings. *Transactions of the Association for Computational Linguistics, 3*, 211–225. https://doi.org/10.1162/tacl_a_00134
  - *锚定* — 网络共现窗口 + top-k 判据敏感性的最强锚: 直接把共现上下文窗口大小(及邻居个数)当会实质改变相似度结果的可调超参数, 支撑"窗口/邻居选择是研究者自由度→设梯子"。注: NLP/分布语义场所非经济学; 支撑自由度/梯子逻辑非金融应用。
  - 〔Crossref 回读标题: Improving Distributional Similarity with Lessons Learned from Word Embeddings〕
- Hoberg, G., & Phillips, G. (2010). Product market synergies and competition in mergers and acquisitions: A text-based analysis. *The Review of Financial Studies, 23*(10), 3773–3811. https://doi.org/10.1093/rfs/hhq053
  - *锚定* — strategic_diff top-k 相似度测度的 method-origin(原始文本对相似度): 基于文本余弦的产品市场邻近度奠基测度。注: 基于相似度分而非严格 top-K, 是文本相似度公司测度的经典起源。
  - 〔Crossref 回读标题: Product Market Synergies and Competition in Mergers and Acquisitions: A Text-Based Analysis〕
- 【2024–2026】Steck, H., Ekanadham, C., & Kallus, N. (2024). Is cosine-similarity of embeddings really about similarity? In *Companion Proceedings of the ACM Web Conference 2024* (pp. 887–890). ACM. https://doi.org/10.1145/3589335.3651526
  - *锚定* — strategic_diff top-k: 近期(2024)证据表明嵌入余弦相似度对建模选择敏感、可能"任意", 激励报告 K 梯子而非信任单一邻居集。注: 推荐系统/ML 场所; 支撑敏感性理据非具体 K 梯子。
  - 〔Crossref 回读标题: Is Cosine-Similarity of Embeddings Really About Similarity?〕
- 【2024–2026】You, K. (2025). *Semantics at an angle: When cosine similarity works until it doesn't* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2504.16318
  - *锚定* — strategic_diff top-k: 2025 preprint 重申余弦相似度基邻居测度对选择敏感。注: 未评审 arXiv preprint(DataCite 核验), 仅作支撑/时新引用。
  - 〔DataCite 回读标题: Semantics at an Angle: When Cosine Similarity Works Until It Doesn't〕
- 【2024–2026】Rister Portinari Maranca, A., Chung, J., Hinck, M., Wolsky, A. D., Egami, N., & Stewart, B. M. (2025). Correcting the measurement errors of AI-assisted labeling in image analysis using design-based supervised learning. *Sociological Methods & Research, 54*(3), 984–1016. https://doi.org/10.1177/00491241251333372
  - *锚定* — 人工标注选择性抽样加权(Manski–Lerman 型)的近期顶刊方法邻近参照: 用抽样设计权校正从"设计式"人工标注子集计算的指标, 呼应"对目的抽样标注集再加权"。注: 该文为设计式监督学习(DSL, Egami 系)的图像/AI 标注框架, **与 Manski–Lerman(1977)选择性抽样再加权非同一方法**, 仅共享"以设计权校正非随机标注子集"的精神(Manski–Lerman 已在前编收录, 为本项目加权的直接命名来源); 首作者 Crossref 姓氏为 "Rister Portinari Maranca"。
  - 〔Crossref 回读标题: Correcting the Measurement Errors of AI-Assisted Labeling in Image Analysis Using Design-Based Supervised Learning〕

---

## 二、核验记录(三道独立核验 + 一道元数据回填)

1. **发现层自核验**: 9 主题桶并行 FIND 智能体, 提名每条前实时 `GET api.crossref.org/works/{DOI}`(arXiv 走 `api.datacite.org`)读回标题自比对; 解析失败/标题不符当场弃。各桶智能体额外主动弃掉数条错 DOI(如 Manela–Moreira 的错猜 DOI 解析到 Robinson–Sensoy、Hüllermeier–Waegeman 的错猜 DOI 解析到无关论文等), 均已在源头剔除。
2. **元数据回填(决定性质检)**: 主控**逐条直连 Crossref/DataCite 回填权威书目**(作者序/年份/卷期/页码/标题), 据此撰写 APA, **不采信智能体转写**。此步捕获并**剔除 2 条**: ① `10.1002/ijfe.3113`(Crossref 作者字段错乱/倒置, 书目不可靠, 避险剔除); ② `10.48550/arXiv.1812.09522`(智能体误报为 Cong "Textual Factors", DataCite 实际解析到物理论文 "How to produce new superheavy nuclei?" —— DOI 张冠李戴; 且 Cong "Textual Factors" 已由第五补编 NBER w33168 版收录)。同步修正多条年份为最新印刷年(Athanasakou–Walker 2023→2025、Anastasiou 2025→2026、Chae–Davidson 2025→2026、Baker et al. 2025→2026 等)使 APA 与 Crossref 回读年一致。
3. **全语料本地核验(决定性闸)**: `scripts/audit/audit_dois.py` 直连 Crossref/DataCite, 对全套唯一 DOI 逐条 DOI→标题逐字回比 + 年份核验。本补编 **85 条新增 0 flag**(全部 resolved, 0 UNRESOLVED / 0 TITLE_MISMATCH / 0 YEAR_DIFF); 前六份既有 3 条 pre-existing benign(① CNKI DOI 不进 Crossref; ② 老 ACL Anthology deposit `10.18653/v1/N19-1423` 标题字段空缺但 DOI 真实可解析; ③ SSRN 工作论文张贴年差 1 年)仍为既有裁定 benign。任何不能解析或解析到另一篇的 DOI 一律不入本文件。
4. **claim-fit 诚实性**: 每条按 method-origin / recent-application / methodological-analogy 分级并写明与所锚指标的确切关系及局限; 崩盘风险谱系(六补-3)一律注明"raw skew 非 NCSKEW、仅移植分布矩方法学"; 熵/尾部/分歧/趋势诸桶注明构念家族锚(动机)与本模块构造公式(SSOT)之别。

> **合计**: 527(前六份)+ **85(本补编净增)** = **612 条**唯一文献锚点 / **592 个唯一 doi.org DOI**(以 `audit_dois.py` 全语料实测为准)。**六族稳健性梯子铁律**(政治权重/规则消融/阈值/cutoff/窗口/top-k/跨模型)——各梯级各自 just-identified 并排, **禁混同一 over-identified Hansen J** —— 与代码注释及 CLAUDE.md「当前状态铁律」一致, 引用时须在方法节写明。
