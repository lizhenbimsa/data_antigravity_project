# 论文分类索引 (Papers Taxonomy)

> 153篇论文按主题分类并评估与 `news_process` 项目的相关度
> 相关度评分：★★★★★(5)=核心直接相关 → ★(1)=间接参考

## 分类统计

| 类别 | 主题 | 论文数 | 高相关(≥4) |
|-----|------|--------|-----------|
| A | 文本情感分析方法论(LLM/BERT/词典) | 28 | 22 |
| B | 实体识别与上下文提取/NER | 8 | 6 |
| C | ESG/绿色金融/企业社会责任 | 14 | 8 |
| D | 金融科技与银行/数字化 | 12 | 8 |
| E | 计量经济学方法(IV/DID/面板) | 10 | 5 |
| F | 媒体效应与信息传递 | 18 | 13 |
| G | 机器学习/NLP/AI基础技术 | 24 | 10 |
| H | 其他(宏观/政策/劳动/专题) | 39 | 5 |

---

## A类：文本情感分析方法论（28篇）

### ★★★★★ 核心必读

| ID | 论文 | 语言 | 关键对标模块 |
|----|------|------|------------|
| 2 | Can ChatGPT Forecast Stock Price Movements? (Lopez-Lira) | EN | `21_tone_llms.py` |
| 3 | ChatGPT for Textual Analysis: How to use GLLMs in Accounting Research (de Kok) | EN | `21_tone_llms.py` |
| 6 | FinBERT: A Large Language Model for Extracting Information from Financial Text (Huang) | EN | `23_tone_berts.py` |
| 10 | Manager Sentiment and Stock Returns (Jiang et al., JFE) | EN | 全局情感框架 |
| 20 | Finance-specific LLMs: Advancing Sentiment with LLaMA 2 (Chiu) | EN | `21_tone_llms.py` |
| 30 | Predicting Returns with Text Data (Ke, Kelly, Xiu, RFS) | EN | 面板输出 |
| 33 | (Almost) 200 Years of News-Based Economic Sentiment (NBER) | EN | 情感测度方法论 |
| 53 | ChatGPT for textual analysis (de Kok, INFORMS版) | EN | `21_tone_llms.py` |
| 54 | ChatGPT outperforms crowd workers for text-annotation (Gilardi, PNAS) | EN | `32_news_llms_human.py` |
| 73 | Enhancing Investment Decisions with Sentiment Analysis (Ke, Kelly, Xiu, JASA) | EN | 概率排序框架 |
| 88 | How much can machines learn finance from Chinese text data (Fan) | EN | 中文金融NLP |
| 99 | Measuring News Sentiment (Shapiro) | EN | 情感测度 |
| 104 | Sentiment Management: AI-based Evidence from Earnings Guidance | EN | LLM情感管理 |
| 107 | The Effects of Sentiment Evolution in Financial Texts: Word Embedding (JMIS) | EN | 情感演化 |
| 124 | 不同来源金融文本信息含量的异质性分析——混合式文本情绪测度方法 (范小云) | CN | `22_tone_words.py`, 混合法 |
| 140 | 大语言模型、文本情绪与金融市场 (姜富伟) | CN | `21_tone_llms.py`, 中文金融LLM |
| 142 | 媒体情绪与企业风险承担——基于机器学习和文本分析 (宫晓莉) | CN | 情感-风险链 |

### ★★★★ 高度相关

| ID | 论文 | 语言 | 关键对标 |
|----|------|------|--------|
| 15 | The News in Earnings Announcement Disclosures: LLM Methods (Siano) | EN | LLM方法论 |
| 48 | Can ChatGPT Decipher Fedspeak? (Hansen) | EN | LLM文本分类 |
| 56 | Computational emotion analysis with multimodal LLMs | EN | 多模态情感 |
| 57 | Context-Based Interpretation of Financial Information (Kim, JAR) | EN | 上下文解释 |
| 67 | Does Finance Benefit Society? A Language Embedding Approach | EN | 语言嵌入 |
| 77 | From Man vs. Machine to Man + Machine (stock analyses) | EN | 人机协作分析 |
| 101 | Monetary Policy Shocks: LLMs and Central Bank Communication | EN | 多智能体LLM |
| 116 | Using GPT to Measure Business Complexity | EN | GPT测度方法 |
| 117 | Using Machine Learning to Measure Conservatism | EN | ML测度 |
| 152 | 非结构化数据增强出口预测：基于机器学习与大语言模型 (孟庆伟) | CN | LLM+ML混合 |

### ★★★ 中度相关

| ID | 论文 | 语言 |
|----|------|------|
| 21 | Fintech Sentiment Analysis Using Deep Learning: A Survey | EN |
| 29 | News sentiment and investment risk management: LLMs | EN |
| 35 | A picture is worth a thousand words: Measuring investor sentiment | EN |
| 61 | Cross-Lingual Multi-Label Emotion Detection Using Generative Models | EN |

---

## B类：实体识别与上下文提取（8篇）

### ★★★★★ 核心必读

| ID | 论文 | 语言 | 关键对标模块 |
|----|------|------|------------|
| 8 | Firm-level Political Risk: Measurement and Effects (Hassan, QJE) | EN | `entity_context.py`, sentence_radius |
| 7 | Firm-level Climate Change Exposure (Sautner, ECGI) | EN | 实体暴露度测度 |
| 97 | Measuring Firm Exposure to Government Agencies | EN | 实体暴露度 |
| 12 | Measuring Misinformation in Financial Markets (Fan) | EN | 信息可靠度 |

### ★★★★ 高度相关

| ID | 论文 | 语言 | 关键对标 |
|----|------|------|--------|
| 13 | Text as Data in Economic Analysis (Hassan et al.) | EN | 方法论综述 |
| 14 | Text as Data (Gentzkow, Kelly, Taddy, NBER) | EN | 方法论综述 |

### ★★★ 中度相关

| ID | 论文 | 语言 |
|----|------|------|
| 49 | Can generative AI help identify peer firms | EN |
| 91 | Identify Critical Nodes in Complex Network with LLMs | EN |

---

## C类：ESG/绿色金融/企业社会责任（14篇）

### ★★★★★ 核心必读

| ID | 论文 | 语言 | 关键对标模块 |
|----|------|------|------------|
| 5 | ESG News, Future Cash Flows, and Firm Value (Derrien, JF) | EN | ESG面板变量 |
| 69 | ESG News, Future Cash Flows, and Firm Value (JF正式版) | EN | ESG面板变量 |
| 18 | Adding Fuel to the Fire: Media Coverage of ESG and Earnings News | EN | ESG媒体报道 |
| 31/121 | When ESG news talks: Media sentiment shapes corporate financial behavior in China | EN | ESG情感-中国 |
| 70 | ESG新闻舆情如何影响企业非效率投资行为 (何青) | CN | ESG+情感+投资 |
| 123 | "漂绿"对绿色创新的挤出效应 (蔡真) | CN | ESG测度方法 |
| 145 | 管理层有限视野与企业ESG表现 (姜富伟) | CN | ESG+管理层 |

### ★★★★ 高度相关

| ID | 论文 | 语言 | 关键对标 |
|----|------|------|--------|
| 22 | Local media sentiment towards pollution and corporate green innovation | EN | 地方媒体+绿色创新 |
| 65 | Diversity Washing (Baker, JAR) | EN | 洗涤型披露 |
| 68 | ESG Disclosures in the Private Equity Industry (JAR) | EN | ESG披露 |
| 87 | How cheap talk in climate disclosures relates to emissions (JFE) | EN | 气候披露 |
| 149 | 象征性还是实质性：合法性压力下的企业ESG行动策略 (李雅文) | CN | ESG策略 |

### ★★★ 中度相关

| ID | 论文 | 语言 |
|----|------|------|
| 58 | Contractual arrangements: ESG compensation and AI disclosure | EN |
| 75 | Financial Constraints and Corporate Environmental Policies | EN |

---

## D类：金融科技与银行/数字化（12篇）

### ★★★★★ 核心必读

| ID | 论文 | 语言 | 关键对标模块 |
|----|------|------|------------|
| 1 | Bank Sentiment and Liquidity Hoarding (Berger) | EN | 银行情感+流动性 |
| 43 | Bank Sentiment, Loan Loss Provisioning, and Lending (Bae, Berger) | EN | 银行情感+LLM |
| 27 | Media sentiment, deposit stability and bank systemic risk: China | EN | 媒体情感+银行风险 |
| 106 | Surviving the Fintech Disruption | EN | 金融科技+银行 |
| 138 | 基于文本分析的商业银行金融科技测度及赋能效果检验 (胡俊) | CN | `12_news_fintech.py` |
| 150 | 金融稳定沟通与银行系统性风险 (姜富伟) | CN | 银行+文本分析 |

### ★★★★ 高度相关

| ID | 论文 | 语言 | 关键对标 |
|----|------|------|--------|
| 71 | Economic policy uncertainty and bank liquidity | EN | 银行+政策不确定性 |
| 126 | 中国企业数字技术风险暴露对企业价值的影响 | CN | 数字风险+LLM |

### ★★★ 中度相关

| ID | 论文 | 语言 |
|----|------|------|
| 125 | 中国上市公司数字化水平测度与演化研究 (胡忠义) | CN |
| 131 | 企业数字化与技术采用 (高远东) | CN |
| 132 | 企业数字化转型的测度难题：基于大语言模型 (金星晔) | CN |
| 133 | 企业数字化转型程度的统计测度 (谭莹) | CN |

---

## E类：计量经济学方法（10篇）

### ★★★★★ 核心必读

| ID | 论文 | 语言 | 关键对标模块 |
|----|------|------|------------|
| 63 | Decoding China's Industrial Policies (Fang, NBER) | EN | DID+政策分析 |
| 139 | 增值税留抵退税、预期与企业雇佣 (陈宇) | CN | 多期DID |
| 111 | Anxiety or pain? The impact of tariffs on Chinese firms (trade war) | EN | 贸易政策DID |

### ★★★★ 高度相关

| ID | 论文 | 语言 | 关键对标 |
|----|------|------|--------|
| 75 | Financial Constraints and Corporate Environmental Policies (Xu) | EN | 准自然实验 |
| 94 | Local newspaper closures and bank loan contracts | EN | 媒体+银行+因果 |

### ★★★ 中度相关

| ID | 论文 | 语言 |
|----|------|------|
| 76 | Firm Inattention and Monetary Policy: Text-Based Approach (RES) | EN |
| 80 | Generative AI at Work (Brynjolfsson, QJE) | EN |
| 127 | 产业链融入与企业创新 (陈林) | CN |
| 134 | 信息摩擦、公共数据与企业创新边界 (谢佳松) | CN |
| 135 | 关税壁垒、跨国知识流动与突破性创新 (李元琨) | CN |

---

## F类：媒体效应与信息传递（18篇）

### ★★★★★ 核心必读

| ID | 论文 | 语言 | 关键对标模块 |
|----|------|------|------------|
| 9 | How news and its context drive risk and returns around the world | EN | 新闻上下文+风险 |
| 19/62 | Curbing Enthusiasm: Media Sentiment and Earnings Announcements (Holzman) | EN | 媒体情感+纪律 |
| 23 | Media Narratives and Price Informativeness | EN | 媒体叙事 |
| 24 | Media Sentiment and Currency Reversals | EN | 媒体情感+资产 |
| 25 | Media sentiment and corporate R&D manipulation | EN | 媒体情感+企业行为 |
| 26 | Media sentiment and international asset prices | EN | 国际媒体情感 |
| 28 | Media sentiment, financial services, and corporate investment | EN | 媒体情感+投资 |
| 44 | Beyond the Fundamentals: How Media-Driven Narratives Influence Capital Flows | EN | 媒体叙事 |
| 45 | Business News and Business Cycles (Bybee, JF) | EN | `38_media_diversity.py` |
| 110 | The effect of media-linked directors on financing | EN | 媒体-董事关联 |
| 113 | The power of the pen and executive compensation (Core, JFE) | EN | `38_media_diversity.py` |

### ★★★★ 高度相关

| ID | 论文 | 语言 |
|----|------|------|
| 105 | Shall we talk? Interactive investor platforms (Lee, JFE) | EN |
| 119 | War Discourse and Disaster Premium: 160 Years | EN |

### ★★★ 中度相关

| ID | 论文 | 语言 |
|----|------|------|
| 40 | Are There Externalities of Private Firm News Disclosure? | EN |
| 47 | CEO turnover, sequential disclosure, and stock returns | EN |
| 85 | Hedging Climate Change News (Engle, RFS) | EN |
| 89 | How to Talk When a Machine Is Listening (Cao, RFS) | EN |
| 103 | Responding to Climate Change Crises: Firms' Trade-Offs (JAR) | EN |

---

## G类：机器学习/NLP/AI基础技术（24篇）

### ★★★★★ 核心必读

| ID | 论文 | 语言 | 关键对标 |
|----|------|------|--------|
| 16 | The Use of LLMs to Annotate Data in Management Research (Carlson, SMJ) | EN | `32_news_llms_human.py` |
| 114 | The use of LLMs to annotate data (SMJ版) | EN | LLM标注方法 |
| 4 | Dissecting Corporate Culture Using Generative AI (Li, RFS) | EN | GenAI+文本测度 |
| 11/95 | Measuring Corporate Culture Using Machine Learning (Li, RFS) | EN | ML+文本测度 |
| 81 | Generative AI in Financial Reporting (Blankespoor, JAR) | EN | GenAI方法概览 |
| 79 | Generative AI and Finance (Eisfeldt, Annual Review) | EN | 综述性参考 |
| 36 | A scoping review of ChatGPT research in accounting and finance | EN | 综述 |

### ★★★★ 高度相关

| ID | 论文 | 语言 |
|----|------|------|
| 34 | A Text-Based Analysis of Corporate Innovation (Bellstam) | EN |
| 93 | Learning from Earnings Calls: Graph-Based Conversational Modeling (ISR) | EN |
| 96 | Measuring R&D activity through 10-K narrative disclosures | EN |
| 130 | 企业包容性创新的测度：基于大语言模型 (梁宇奇) | CN |

### ★★★ 中度相关

| ID | 论文 | 语言 |
|----|------|------|
| 37 | AI-Generated Report, Information Risk and Stock Return | EN |
| 39 | An explainable attention network for fraud detection | EN |
| 46 | CEO emotions and firm valuation in ICOs | EN |
| 50 | Can investors learn from patent documents: textual analysis | EN |
| 59 | Corporate Climate Risk: Measurements and Responses | EN |
| 60 | Corporate responses to generative AI: conference calls | EN |
| 82 | Generative AI and evaluating strategic decisions | EN |
| 86 | How Does AI Shape Audit Firms (INFORMS) | EN |
| 98 | Measuring founding strategy (Guzman) | EN |
| 100 | Measuring the commercial potential of science | EN |
| 102 | Research in Commotion: Measuring AI R&D through Conference Calls | EN |
| 108 | The Impact of Generative AI on Information Processing (Italy ban) | EN |
| 118 | Using supervised ML for large-scale classification (AI patents) | EN |

---

## H类：其他（39篇）

### ★★★ 中度相关（有方法论参考价值）

| ID | 论文 | 语言 | 参考价值 |
|----|------|------|---------|
| 17/122 | Work Design and Compensation Strategies: Online Job Postings | EN | 文本分析场景 |
| 32 | Why Do Investors Like Short-leg Securities (Chen, RFS) | EN | 文本分析+投资者 |
| 38 | Accounting information usage by retail investors (JAR) | EN | 信息使用 |
| 51 | Can we measure inflation expectations using Twitter? | EN | 社交媒体情感 |
| 52 | Central bank mandates and monetary policy stances | EN | 央行沟通+NLP |
| 55 | Common volatility shocks driven by global carbon transition | EN | 气候+波动 |
| 64 | Dissecting climate change risk and financial market instability | EN | 气候风险 |
| 115 | The voice of monetary policy (AER) | EN | 语音+NLP |
| 128 | 人工智能如何提升企业生产效率 (姚加权) | CN | AI+文本 |
| 136 | 劳动力成本与劳动节约型技术创新 (刘青) | CN | BERT+专利 |
| 141 | 央行沟通公告有助于提升政策利率传导效率 (欧阳志刚) | CN | 央行沟通 |
| 144 | 数字人力投入与企业价格加成 (余典范) | CN | LLM+招聘 |
| 146 | 网络安全风险治理与企业创新 (杨鹏) | CN | LLM+年报 |
| 147 | 诚信文化与金融企业社会责任承担 (田子方) | CN | ML+年报 |
| 148 | 调预期、防风险：央行金融稳定沟通效果 (姜富伟) | CN | Word2Vec |
| 151 | 非正式融资中的文化力量——企业文化 (华秀萍) | CN | 词向量+文化 |
| 153 | 预期的博弈：央行沟通与国债收益率曲线 (尚玉皇) | CN | 央行沟通 |

### ★★ 低相关（背景参考）

| ID | 论文 | 语言 |
|----|------|------|
| 41 | Are the futures computable? Knightian uncertainty & AI | EN |
| 42 | Artificial intelligence, firm growth, and product innovation | EN |
| 66 | Do makerspaces affect entrepreneurship? | EN |
| 72 | Employee Overtime and Innovation Dilemma | EN |
| 74 | Epidemic effects in diffusion of digital technologies | EN |
| 78 | From evidence to impact: scientific research in policy | EN |
| 83 | Global Business Networks | EN |
| 84 | Going digital: implications for firm value | EN |
| 90 | Human Capital Disclosure and Labor Market Outcomes (JAR) | EN |
| 92 | Institutional Brokerage Networks | EN |
| 109 | The bullwhip effect in servitized manufacturers | EN |
| 112 | The informational content of key audit matters | EN |
| 120 | What Is Rationality? Evidence From Internet Text | EN |
| 129 | 企业供应链风险与纵向并购 (蓝发钦) | CN |
| 137 | 劳动节约型创新、买方垄断与超额利润 (喻理) | CN |
| 143 | 市场一体化对企业数字创新的影响 (胡增玺) | CN |

---

## 审计批次分配

### Batch 3.1: 情感分析方法论（对标 `21/22/23_tone_*.py`）
精读：#2, #3, #6, #10, #20, #30, #33, #53, #54, #73, #88, #99, #104, #107, #124, #140, #142
+ #15, #48, #56, #57, #67, #77, #101, #116, #117, #152
**共28篇**

### Batch 3.2: 实体识别与上下文（对标 `11/12_news_*.py`, `entity_context.py`）
精读：#8, #7, #97, #12, #13, #14
**共6篇**

### Batch 3.3: 面板构建与计量（对标 `40~45`, `51`）
精读：#63, #139, #111, #75, #94, #76, #80
**共7篇**

### Batch 3.4: ESG/绿色金融（对标面板变量设计）
精读：#5/#69, #18, #31/#121, #70, #123, #145, #22, #65, #68, #87, #149
**共11篇**

### Batch 3.5: 金融科技测度（对标 `12_news_fintech.py`）
精读：#1, #43, #27, #106, #138, #150, #71, #126
**共8篇**

### Batch 3.6: 媒体效应与权重（对标 `38_media_diversity.py`）
精读：#9, #19/#62, #23, #24, #25, #26, #28, #44, #45, #110, #113, #105, #119
**共13篇**

### Batch 3.7: 验证与稳健性（对标 `31~39`）
精读：#16/#114, #4, #11/#95, #81, #79, #36, #34, #93, #96, #130
**共10篇**

---

**总计精读论文：~83篇（去重后）**
**摘要阅读论文：~40篇**
**仅记录备用：~30篇**
