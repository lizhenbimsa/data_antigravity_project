# 顶刊文本测度缺口报告 — 复核修订版 (含白话)

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


**日期**: 2026-06-05  **方法**: 47-agent 对抗复核工作流 (16 判断回验 + 22 完整性扫荡 + 26 引文 web 核对)
**复核对象**: 上一轮"顶刊文本测度缺口"报告 (memory: textual-measure-gap-topjournal-2026-06-05)

---

## 0. 一句话总评

原报告方向正确(顶刊文本测度已基本覆盖、确有几个 $0 缺口),但**(a) 2 处判断需降级/纠正,(b) 漏掉了一整族"新闻体裁显著性"测度——而原始数据现成却没用,(c) 多条引文错误**。本版逐条修订并加白话。

---

## 1. 对原报告的更正 (over-claim / 不准确)

| 项 | 原报告说法 | 复核结论 | 白话 |
|---|---|---|---|
| **Lazy Prices 四距离 (G6)** | P2 真缺口 | **降级 P3**:核心构念(相邻年文本变化)已被 `coh_*` 10 列覆盖,只缺 Jaccard/编辑距离/词重叠 3 个非余弦算子 | "今年 vs 去年新闻像不像"项目早做了(`coh_*`),只是没多放 3 把尺子。不是大窟窿,是稳健性小补丁 |
| **词级长度列 (G7)** | 真缺失 | **夸大**:可读性簇 avg_sent_len/avg_ttr/avg_cpw 双轨已进面板,WordsPerSentence 以"字符/句"形式已覆盖。真正只缺 1 个独立 `ln(1+jieba词数)` 列 | "缺词级长度"说大了,其实只缺一个"按词数取对数"的单列 |
| **num_intensity_word "仅缺除法" (G1)** | trivial,分子分母都现成 | **校正**:分母(jieba 词数)现成,但分子 `n_numeric` 算完即丢、未存列,需先暴露(~5-15 行),非"一个除法" | 不是改一行那么轻,要先把"数字个数"留住再除,但仍是小活、$0 |
| **`coh_*` = Brown-Tucker 修改分数 (C1)** | 等价 Brown-Tucker 2011 | **构念归属夸大**:代码自引欧阳志刚&胡雯华 2024,度量的是"第三方新闻"连贯性,非 10-K 自我披露;且是 8 主列+2 t2v=10,非 8 列直接=10 | 方向对(相似度≈1−变化),但别说成"复刻了那篇会计名作" |
| **jieba.posseg 可替代付费 NER (C4/G4)** | 暗示可 $0 替代 stage19 | **校正**:posseg 能 $0 标人名/机构,但精度糙("陈四清"只认"陈"、"工商银行"认不出机构)。能力在、质量≠付费 LLM | 免费能用,但识别质量比花钱的大模型差,论文里要写"近似" |
| **n_tokens 从未入面板 (C7)** | 词数从未触及面板 | **过强**:原始 n_tokens 计数列确无,但其派生的 CPW(平均词长)以词数作分母、已聚合为 avg_cpw 入面板 | 词数没单独进表,但"平均词长"用到词数、进了表 |
| **avg_article_length "审稿人一眼可见" (G8)** | 一眼可见的硬伤 | **轻微收紧**:标签写"words"可见,但要确认它"错"(实为字符)需回查源码 `len()`。定性"一致性/诚实性问题非计算错误"正确 | 名牌贴错了,但要发现贴错得翻代码,不是扫一眼就能断定 |

---

## 2. 原报告【漏掉】的缺口 (完整性扫荡新增) — 本次最大增量

原报告聚焦"可读性/披露质量"经典,**漏掉了新闻体裁特有的"显著性/注意力"族——而这正是本项目(中文新闻)最该有、且原始数据现成的维度**。

### 2.1 新增 P1 (高价值, $0, 原始数据现成)

| 缺口 | 锚点 | 证据 | 白话 |
|---|---|---|---|
| **版位显著性** `is_front_page`/`front_section_frac`/`page_rank` | Tetlock 2007 JF;Boudoukh 2019 RFS | `版面`(头版/要闻/财经)、`页号`(A01/B05)两列原始数据存活到 article 级文件(11/12/14),**但只用于广告过滤,从未聚合到 bank-year**;曾挂的 bartik_page/pgnum IV 已作 post-treatment 删除 | 报纸登在头版还是 B 叠后页=读者注意力强弱。数据里明明有版面/页号,却从没拿来算特征——白白浪费 |
| **导语/首段显著性** `target_in_lead`/`lead_mention_share` | Tetlock 2008;Boudoukh 2019 RFS | 全仓无"首段/前K句命中"标量;`fintech_upper/lower_count` 只是 50% 字符中点切分的过滤阈值;`article_sbert` 的 FIRST_PARA_CHARS=300 只喂 embedding 不产标量 | 银行是开头导语就被点名(主角),还是读到一半才顺带提一句(路人)——倒金字塔写法下区分力强,现在没做 |
| **署名/通稿原创性** `has_byline`/`staff_written_frac` | 来源权威/原创性文献 | `作者`字段存活到 stage13(实测 42.8% 具名/57.2% 空=通稿);**不仅没用,反被 noise_patterns 当噪声剥离**;与 media_authority(媒体级)、herd_decay(产出端重复)正交 | 署名记者深度稿 vs 无名通稿,区分原创性。数据有"作者"列却没用,还被当垃圾删了(实现要在去噪前抽取) |
| **boilerplate 套话比例** `boilerplate_share` | Lang & Stice-Lawrence 2015 JAE 60(2):110-135 | 真缺(全仓 0);需 jieba 词级 4-gram 跨文档 DF + 覆盖比(新建 stage,**非**直接复用 strategic_diff 的 char-level TF-IDF) | 一篇报道里有多少是通稿式固定套话。中国财经新闻通稿化重,这信号可能比美国 10-K 还强 |
| **specificity 硬信息密度** `specificity_index` | Hope, Hu & Lu 2016 *Rev. Account. Stud.* 21(4):1005-1045 | 真缺;num_intensity 只数字半边,executive_ner 是付费窄域 PER;实体半边用 jieba.posseg(nr/ns/nt)$0 补 | "说得具不具体"=人名+机构+数字+日期占比。高=硬信息多。注意别和 num_intensity 重复计数、别复用付费 ner |
| **num_intensity_word** 按词数版 | (见引文勘误,**非** Hales) | docstring 自我承诺 §4.3 word-level 未兑现 | 数字/词数(对照按句数版),回应"中文句号稀疏致分母失真"。兑现自己写过的承诺 |
| **词汇难度维** `rare_word_ratio`(主)/`hard_char_ratio` | You-Zhang 2009;Gentzkow 2019 JEL | 真缺;CPW/TTR 测长度/多样性≠难度。`rare_word` 可用 jieba 自带词频表(jieba.dt.FREQ 49.8 万词)$0;`hard_char` 仍需外部常用字表(项目没有) | "用词难不难/多少生僻冷门词"——可读性三件套缺的唯一维,即 Fog "%复杂词"的中文等价 |

### 2.2 新增 P2 (稳健性/补全)

| 缺口 | 锚点 | $0? | 白话 |
|---|---|---|---|
| **语调时序波动率** rolling SD | — | $0,需 T≥3(全量) | "同一行语调在年份间起伏多大"。现有只有年内跨文章离散、相邻年差分,没有跨年滚动波动 |
| **文档内冗余/重复率** | Dyer 2017 JAE;Cazier-Pfeiffer 2016 | $0(字符 n-gram 自相似 / gzip 压缩率) | "一篇新闻自己内部多啰嗦/复读"。现有相似度全是篇间/年间/行间,没有篇内 |
| **主题熵** Shannon entropy | Dyer 2017;Blei 2003 | $0(numpy),**但依赖 stage17 BERTopic 先跑通**(8-12h opt-in) | stage17 只有 HHI(看头部主题),缺对偶的香农熵(看长尾)。等 BERTopic 跑起来才有数据 |
| **名词化率** | Bonsall 2017 Bog 成分 | $0(posseg + 性/化/度后缀) | "把动词憋成抽象名词"(进行优化/安全性)越多越官腔 |
| **虚词/功能词比率** (LIWC Analytic 近似) | LIWC | 功能词比率 $0(posseg);完整 LIWC 需 CLIWC 词典(版权) | "的/了/和/在"等虚词占比=分析性思维。停用词表现在只用来"删",没拿来算比例 |
| **报道连续性/节奏** | Hillert 2014 RFS | $0,需 T≥3 | "全年有多少天有报道/是否连续上版/还是一两天爆发"。现有 coverage 全是总量,无时间节奏 |
| **异常/残差语调** abnormal tone | Huang-Teoh-Zhang 2014 TAR 89(3) | **非 $0**:面板无银行财务基本面(资产/杠杆/ROA/NPL),需先外部 merge | 残差语调法在 P1 证伪模板里已有雏形(Stata、单轨、引 Fang 2024 而非 Huang),但物化成双轨面板变量缺;且第一步缺被减项(财务数) |
| **连接词/逆接密度** | ⚠见勘误(**非**王克敏 2018) | $0(须独立词表) | "转折/连接词密度"=篇章衔接复杂度。⚠须用独立逆接词表,勿复用情感轨 adversative_boost 同表(否则与情感分纠缠) |
| **词级 `ln(1+jieba词数)`** | Li 2008 JAE | $0 | G7 里唯一真缺的一列(顺带可修 avg_article_length 单位) |

### 2.3 确认"已覆盖/不补"(纠正原报告或扫荡误判)

- **LM file-size 长度** / **WordsPerSentence(字符/句)** / **certainty-tentativeness(LIWC)=LM modal_strong+uncertainty** / **yoy stickiness=coh_*** / **Lazy Prices 核心=coh_***:均**已覆盖**,skip。
- **manager sentiment index (Jiang 2019)**:市场层聚合+自我披露,结构不匹配,**skip**(但 `jf_coefficient` 被误标"Jiang 2019",实为 Janis-Fadner,建议改注释)。
- **句法依存深度 (Bushee-Gow-Taylor 2018)**:真缺但**非 $0**(需 HanLP/LTP 依存解析器,破坏 jieba 冻结),P2/倾向 skip。

---

## 3. 引文勘误表 (web 核对, ⚠ 涉及现有代码的需你确认)

| 引文 | 原报告/代码 | 正确 | 严重度 |
|---|---|---|---|
| **Hales-Kuang-Venkataraman 2011** | "CAR 28(1):305-339",归为 num_intensity | ⚠ **JAR 49(1):223-255**,且该文讲 vivid/pallid 语言**非数字密度**;num_intensity 应改引 **Davis & Tama-Sweet 2012 CAR 29(3):804-837**。代码注释 CAR、spec 文档 JAR 均存疑 | **高**(涉冻结代码注释,需你确认再改) |
| **Tetlock 2011** | (前文混 JF/RFS) | **RFS 24(5):1481-1512**;标题"All the News *That's* Fit to Reprint" | 中 |
| **Lang-Stice-Lawrence 2015** | JAE 60(2-3):110-135 | JAE **60(2)**:110-135 | 低 |
| **Hope-Hu-Lu 2016** | "RAST" | *Review of Accounting Studies* (**RAS**) 21(4):1005-1045 | 低(缩写) |
| **Bonsall 2017** | (初版工作流误作 JAR) | **JAE** 63(2-3):329-357 | 已纠 |
| **You-Zhang-Zhang 2018** | RFS? | ✓ **RFS 31(1):43-96**(definite 388/ambiguous 178) | 确认无误 |
| **丘心颖 2016** | 《度量企业年报的可读性》《经济研究》 | ❌ 实为**丘心颖、郑小翠、邓可斌《分析师能有效发挥专业解读信息的作用吗?》《经济学(季刊)》15(4):1483-1506** | 高(篇名+刊均错) |
| **王克敏 2018** | 《会计研究》(逆接/次常用词) | ❌ 实为**王克敏、王华杰、李栋栋《年报文本信息复杂性与管理者自利》《管理世界》34(12):120-132** | 高 |
| **徐巍 2021** | 《金融研究》(副词连词占比) | ❌ 实为**徐巍、姚振晔、陈冬华《中文年报可读性:衡量与检验》《会计研究》2021(3):28-44**(这才是中文可读性 canonical) | 高 |
| **He et al. 2024 IRFA (MLENGTH)** | geography.py:110 注释锚点 | ⚠ **web 无法核实**,疑 phantom/误记。需你提供 DOI 或核实 | 高(涉代码注释) |
| **Guzman-Li 2023** | Management Science | ✓ 69(1):101-118 | 确认 |

---

## 4. 内部一致性问题 (顺手可修, 非缺测度)

1. **avg_article_length 单位错位**:底层 `doc_length`=字符数(news_bank.py:230),但 geography.py:111 注释 + export.py:411 Stata 标签 + falsification_template:142 均写"词数/words/MLENGTH"。中文字符≈词数×1.5-1.7。修法二选一:改标签为"ln(1+字符数)"(零代码,不动 golden)/改用 n_tokens 词数(需重生 golden)。
2. **num_intensity 出处**:源码注释 CAR vs spec 文档 JAR 不一致(且二者对该构念都存疑,见 §3)。
3. **jf_coefficient 误标**:export.py:744 注"Jiang et al. 2019",实为 Janis-Fadner(Deephouse 2000 SMJ);改注释防再被误认。
4. **avg_article_length docstring 路径**:原报告写 core/text/tone_words.py,真实为 pipeline/sentiment/tone_words.py。

---

## 5. 修订后总优先级清单

**P1(建议补,多 $0)**:① 版位显著性 ② 导语显著性 ③ 署名原创性 ④ boilerplate ⑤ specificity ⑥ num_intensity_word ⑦ 词汇难度(rare_word 主)
**P2(稳健性)**:语调波动率 / 文档内冗余 / 主题熵 / 名词化 / 功能词比率 / 报道连续性 / 异常语调(非$0) / 连接词密度 / ln(词数) 单列
**P3(降级)**:Lazy Prices 3 个补充距离
**先修(一致性)**:avg_article_length 单位标签 + num_intensity/jf_coefficient/He2024 引文

> ⚠ 全量提醒:磁盘 176 行 T=2 仅 0.052% 试跑样本;时序类(波动率/连续性/异常量/Lazy)与跨文档类(boilerplate vocab)须全量 18,198,978/T=19 才可识别且需工程化(hash 计数控内存)。
