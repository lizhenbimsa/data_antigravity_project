> ⚠️ **本初版已被 `METRIC_AUDIT_FINAL_2026-06-02.md` 取代。** 经元验证：本文 P0 约 50% 被降级/推翻（tone_words-02、risk_outcomes-01 已 overturned；cn2arab "22%"、epu-01 "上偏"、network-01 量级须改述），且本文漏报了 2 个 active-crash P0（exec_ner / staleness 的 groupby year KeyError）。**P0/P1 定级请以 FINAL 版为准，勿直接采信本文。**

# news_process 指标计算体系 — 顶刊标准终审报告（初版，已取代）

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


**审查标准**：AER / QJE / JF / RFS / JFE 方法学硬约束 ——「每个指标必须忠实测度其所声称的构念，且实现须与所引文献口径逐项一致；进入回归/IV 的派生列必须有公式正确性保障」。
**审查日期**：2026-06-02
**审查方法**：27 个指标单元 × (深度评审 → 结构化抽取 → 双棱镜对抗验证) + 完备性批判 + 终审独立逐行核验 7 个最高风险模块。共生成 366 个审查智能体、约 2150 万 token。
**证据分级**：`confirmed`=双棱镜均确认；`contested`=公式棱镜与代码棱镜分歧（需人工裁定）；`terminal-verified`=终审在主对话逐行复核坐实。所有发现均落到 `file:line`。

---

## 0. 总裁决

**当前指标体系尚未达到顶刊「零错漏」标准，需修复后方可作为论文主结果。**

工程骨架是顶刊级的：双轨 full/ctx 契约、LLM 缓存与归档、jieba/prompt v8 字节冻结、加权聚合的 sum/sum 骨架、纯函数确定性、Bartik Rotemberg 诊断与官方包对接意识、广泛白盒测试。多个核心公式经验证**逐项正确并明确背书**（见 §7）。

但存在一批**会系统性改变指标值乃至回归系数符号/显著性**的确认缺陷，且其中多个被「锁定实现现状而非文献应然」的测试夹具掩盖。最危险的是 4 类系统性根因（§2）+ 1 个静默行错位（数据完整性级）。

### 确认问题计数（双棱镜对抗验证后，已去重 herd 跨单元重复）

| 优先级 | 确认 | 争议 | 证伪剔除 | 说明 |
|---|---:|---:|---:|---:|
| **P0**（改变指标值/结论） | **18** | 1 | 2 | 含 run-1 的 cn2arab inflation；herd 幽灵列跨 3 处计 1 类 |
| **P1**（显著口径/公式偏差） | **41** | 4 | 14 | |
| **P2**（边界/标注/防御性） | **26** | 11 | 13 | |
| **P3**（吹毛求疵/展望） | 44(未验) | — | — | 低优先 |

> 注：P0/P1 边界上有若干发现经验证者上调/下调（`corrected_severity`）；本报告按「确认即需修」组织，不纠结单条 P0 vs P1。证伪剔除的 29 条（含 2 条 P0、14 条 P1）见 §8，体现对抗验证确实在过滤误报。

---

## 2. 横切系统性主题（最高价值 —— 根因，一处修复消多处症状）

### 主题 A：jieba 整词匹配系统性漏配多字词典条目（覆盖面最广的系统缺陷）

全仓多个词典法指标用 `set(jieba.cut(text)) & 词典` 或 `tok in frozenset` 做匹配。jieba 按其**默认词典**切分，边界与项目自建词典（LM 4 子词典、FLS 时间标记、fintech 1506 词）不对齐 → 多字条目被切碎 → `in frozenset` 永不命中 → 词频被系统性、且与构词系统相关地低估（非随机测量误差）。

| 受害指标 | 文件:行 | 实测漏配 |
|---|---|---|
| LM 4 子词典 `uncert/litig/constr/modal_strong_frac` | `lm_non_sentiment.py:117,124-127` | 19/83、22/104、9/76、8/51 条目不可达（可达率仅 77%/79%/88%/84%）`lm_fls-01` |
| FLS 双门控 time-marker | `forward_looking.py:111-114` | 28/59 复合标记不可命中（`未来三年→未来\|三年`、`到2030`、`次月` 等）`lm_fls-02` |
| fintech 强度 TF | `fintech_intensity.py:278` (TF=jieba) vs `:117-122` (DF=AC 自动机) | **TF 用 jieba 整词、DF 用 AC 子串 → IDF 每一项失配**（`idf=log(N/df)` 的 df 与 tf 计数算子不同）`fintech_intensity-01` |
| 清晰度分句器 | `cn_text_utils.py:96-100` | 「引号配对内不切分」是虚假声称，实为单字符 lookahead，连续标点产垃圾单标点「句子」，膨胀 FLS 分母 `clarity_cn-01` |

**统一修复**：改用项目已有的 `core/text/ahocorasick.py` 多模式子串匹配（与 stage 12/14 fintech 一致），或 `jieba.add_word()` 注入全部词典条目后再切。务必让 TF 与 DF 共享同一匹配引擎。**会破 prompt v8 / $0 约束并需重生 golden snapshot，但这是正确性而非可选优化。**

### 主题 B：标题注入双轨不对称（v3.8.0 remove-title-track 的接线遗漏，散布多模块）

v3.8.0 规定 full/ctx 两轨文本都应「含标题」（`content_full`=标题+正文、`content_ctx`=标题+实体窗口，经 `prepend_title` 注入）。但多个指标的 full 轨仍硬读裸 `内容`（无标题），而 ctx 轨读含标题的 `content_ctx` → full vs ctx 差异混入了「是否含标题」的混杂，破坏 Hassan 2019 QJE proximity 稳健性对照与 Campbell-Fiske MTMM 三角验证。

| 模块 | 文件:行 | 不对称表现 |
|---|---|---|
| LLM 情感 | `tone_llms.py:562-571` + `ctx_materializer.py:138` | **依赖 stage 顺序的双重注入**：ctx_materializer 已把标题写进 content_ctx，stage 21 又把 title 作独立字段喂 prompt → ctx 轨标题进 prompt 两次；full 轨仅一次。`llm_vote_tone_ctx`（主处理候选）取值随 stage 13 是否先跑而变 `tone_llms-01` |
| 社会效益 full 轨 | `benefit_society.py:568-573` | 用 `标题+' '+内容` 裸空格拼接（非句号、无去重），与 `prepend_title` 产物逐字不同 `benefit_society-01` |
| 高管 NER full 轨 | `executive_ner.py:414` | 硬读 `内容`，漏掉「仅出现在标题」的高管（中文银行标题高频「XX 行长/董事长」）；ctx 读含标题 → `n_ceo_mentions_full < _ctx` 反直觉 `exec_ner-01` |
| fintech 强度 full 轨 | `fintech_intensity.py:400` (`内容`) vs `:411` (`content_ctx`) | 前缀不对称 `fintech_intensity-04` |
| 词典 IDF 语料 | `tone_words.py:1238` (DF 用裸 `内容`) vs `:986`(评分用 prepend_title) | DF 语料与评分文本分叉，标题情感词 IDF 偏高 `tone_words-04` |

**统一修复**：全部 full 轨改读 `content_full`（缺列时 fallback `内容`）；LLM ctx 轨改消费「去标题的纯 ctx body」。这会改变所有 full 轨指标值，需重跑相关 stage + 重生 golden snapshot。

### 主题 C：加权均值分子分母样本不匹配（缺失情感行的权重仍入分母 → 系统性向 0 偏）

标准加权均值 `Σ_{j∈S} w_j·tone_j / Σ_{j∈S} w_j` 要求分子分母遍历**同一有效集 S**。但多处分子用 `score(nullable Int8)·w` 经 `groupby.sum` 自动跳过 NA，分母却用全体 `Σw`（与情感是否有效无关）→ 缺失情感文章的权重撑大分母，加权均值被压向 0。

| 受害链路 | 文件:行 |
|---|---|
| VW/MW/HW 加权情感（encode 核心） | `encode.py:1362-1366,1396-1401,1438-1450` `encode-01` |
| clarity/num_intensity 加权（encode_collab） | `encode_collab.py:520-537` `encode_collab-03` |
| 地理缓冲情感/正负比例 | `geography.py:916-935`（nullable Int8 `.mean()` skipna，分母≠n_within）`geography-01` |
| 网络溢出 peer_tone | `network_spillover.py:265`（缺失同行 tone 填 0 而不重归一化 W）`network-02` |
| EPU 年均值 | `epu_merge.py:161-168`（文章数加权而非月度等权，引入机械内生性）`epu-01,epu-03` |
| fintech 强度面板均值 | `encode.py:755-760`（`intensity_verified=False→0` 的哨兵值混入 mean，把缺失当 0）`fintech_intensity-02` |

**统一修复**：为每个加权轨同步产出「有效行权重和」作分母（`w.where(score.notna())` 后 sum）；EPU 改月度去重等权；fintech 用 verified 掩码聚合。

### 主题 D：herd 幽灵列 —— 跟风衰减权重生产期静默失效（双向 terminal-verified）

`encode_collab.py:503,583` 的加权循环写 `for w_col in ('media_authority_weight', 'herd_decay_weight')`，但**生产中根本无 `herd_decay_weight` 列**：producer `herd_decay.py:246-247,313` 实际产 `herd_weight`/`herd_weight_full`/`herd_weight_ctx`。`if w_col in df.columns` 永假 → herd 乘子永不参与 → `mean_clarity_score_*`/`mean_num_intensity_*` 只按 media_authority 加权，与 docstring「media_authority × herd_decay」(Tetlock 2011 JF) 公开矛盾。而 `encode.py` 的 `llm_vote_tone_hw` 路径用的是**真** herd 权重 → 同一「herd 加权」构念在两模块两套口径、其一失效。`tone_words-…`：测试夹具 `test_a1_a3_panel_aggregation.py` 等注入伪列 `herd_decay_weight=1.0` 恰好匹配错误列名并恒为 1.0，掩盖了 bug。`herd_decay-01 / encode_collab-01 / encode_collab-02`。

### 主题 E：测试夹具掩盖错误口径（顶刊再现性反模式，贯穿多个 P0）

多个 P0/P1 被「锁定实现现状而非文献应然」的测试掩盖，回归保护失效：
- herd 幽灵列：夹具注入 `herd_decay_weight=1.0`（主题 D）`encode_collab-02`
- cn2arab inflation：测试只断言 token 计数关系，从不断言「成语不应进分子」（run-1 P0-1）
- media tier 死代码：`test_media_tier_and_epu.py:115-126` 用 `inspect.getsource` 断言「源码含某字符串」而非「面板列数值正确」，放过了「算了但没用」的死代码 `attention_media-04`
- LLM 投票：`test_21_tone_llms.py:19-78` 用本地复刻的影子函数副本测试，且平局口径与生产相反 `tone_llms-04`
- exec_ner：docstring 声称 200 篇 gold-standard precision≥0.85 门控，代码中完全不存在 `exec_ner-02`

### 主题 F：样本内标准化/IDF 泄漏（再现性 + 机械关联）

IDF/分位数/中位数阈值在「即将被评分并进回归的同一样本」上估计，注入样本统计量：
- 词典 IDF + P1/P99 Winsorize 全样本分位数 `tone_words.py:591-658` `tone_words-02`
- herd 相似度 IDF 每银行组内 `fit_transform`，T=2 下随面板规模漂移 `herd_decay.py:127` `herd_decay-02`
- fintech IDF 样本内（同主题 A 的 `fintech_intensity-01`）
- 39d Cohen κ 用样本内 median 而非 D0 冻结常量 `lexical_discriminant_validity.py:164-167` `discriminant-02`

### 主题 G：静默行错位（数据完整性级，最严重单点）

`article_staleness.py:300-306`：`compute_surface_staleness` 内部 `sort_values(date).reset_index()` 后在**日期排序序**返回数组，main() 却用 `art_df['surface_staleness_full'] = <排序后数组>` 按**位置**赋回**未排序**的 art_df → 每篇文章被错配到另一篇的 staleness 并错配 bank-year；semantic 轨返回原序、surface 返回排序序 → 两轨在 art_df 中互相错位。`staleness_topic-01`（confirmed P0）。**修复**：在 return 前加逆置换还原原始行序（对齐 semantic 实现 L244-245）。

### 主题 H：T=2 面板对滚动统计 / IV / 差分的结构性限制

面板仅 168 行（84 banks × 2017–2018）。多派生列在 T=2 下退化：
- llm_peer IV 滞后一期吃掉首年 → 仅 1 个有效截面，2SLS 退化为横截面 `llm_peer_iv-02`
- risk Z-score 的 σ(ROA) 需 5y/min_periods=4 → outcome 面板若 T<4 则 z_score 全 NaN（终审独立核验）
- benefit_society 一阶差分在 T=2 塌缩为单期 n≈58 横截面 + levels-controls 混搭 `stata_vars-03`
- Bartik IV 在 T=2 + LOO shift 下退化（CLAUDE.md 已记 ivreghdfe r301）

这些**不全是 bug**，但论文必须显式披露退化、报告 first-stage 有效 N/F，并据此降权相关 spec。

---

## 3. P0 清单（确认/争议，按主题去重）

> herd 幽灵列（主题 D）、jieba 漏配（主题 A）、标题不对称（主题 B）、加权分母（主题 C）已在 §2 详述，此处列其余独立 P0 + 关键索引。

### P0-① 静默行错位（surface staleness）— `staleness_topic-01` confirmed
最严重。详见主题 G。`article_staleness.py:103,300-306`。整列行错配 + 错配 bank-year，污染 staleness 双指标及其 `staleness_corr` 门控。

### P0-② cn2arab 把成语/序数/专名当数值 token（实测占分子 22%、波及 90.3% 文章）— run-1 P0-1 confirmed terminal-verified
`numerical_intensity.py:138-192,208,250`。`三农→3`、`十八大→18`、`第一→1` 无差别计入。docstring:235-239 仍自称「≈1%」，与实测 22% 相差约 20×。`mean_num_intensity_*` 直接作 Table A9 treatment，足以翻转系数。

### P0-③ 根模板 winsorization 是孤儿，主表 Table 2 在未缩尾数据上估计 — `stata_vars-01` confirmed
`01_data_prep.do.tmpl:66`（winsor2 replace 存 `_prepared_panel.dta`）vs `11_table2_main_m1m6.do.tmpl:17,27`（重新 `use 46_panel_yearly_core.dta` 未缩尾 + 裸列名）。缩尾结果在根链路无消费者，主线 Table 2 的缩尾对主结论失效。

### P0-④ fintech 强度 TF/DF 计数引擎不一致致 IDF 系统性偏差 — `fintech_intensity-01` confirmed（主题 A）

### P0-⑤ herd 幽灵列 — `herd_decay-01`/`encode_collab-01/02` confirmed terminal-verified（主题 D）

### P0-⑥ LLM ctx 轨标题双重注入 + 依赖 stage 顺序的非对称污染 — `tone_llms-01` confirmed（主题 B）

### P0-⑦ 社会效益 full 轨未走 prepend_title — `benefit_society-01` confirmed（主题 B）

### P0-⑧ 媒体注意力锚定 Hassan 2019 QJE 名不副实 — `attention_media-02` confirmed
`attention_media.py:197-345`。代码只产 geo/year 的 article-count 占比（单轨、无 full/ctx 文本分轨、无标准化、无 dispersion/percentile），而 paper_spec R36-m01 声称的 `attention_index_full/ctx/disp/pct`（text-intensity 双轨）从未物化。代码实现与论文声称的 treatment 不是同一个量。**配套**：`attention_media-01` —— `media_authority_weight_tier` 是死代码（算了但既不加权也不聚合，永不进面板），且被 `test_media_tier_and_epu.py` 字符串断言掩盖（主题 E）。

### P0-⑨ llm_peer「≥2 银行」预筛用未归一变体集合计数 — `llm_peer_iv-01` confirmed
`llm_peer_iv.py:240-244`。同一银行「全称+短变体」(中国工商银行+工商银行) 被计为 2 家不同银行，1475/1767(83%) canonical 名含自身短变体 → 单银行单次提及即误过 ≥2 门，大量单银行句被当竞争比较句送入 PEER_PROMPT，污染 peer 网与 IV。（终审独立核验已先行发现，工作流坐实）

---

## 4. P1 清单（确认/争议，按模块）

**LLM 情感**：`tone_llms-02` 连续语调 `avg_prob_score` 未做 verification 门控、与离散 `final_s` 口径不一致 (`:1108-1142`)；`tone_llms-04` 影子副本测试（主题 E）。

**词典情感**：`tone_words-03` 正/负计数基于否定后 `final_score` 符号，使 `pos_ratio/neg_ratio` 偏离「词典命中频率」语义且与同模块 MSENT(base 计数)内部不一致 (`:442-445`)；`tone_words-02` IDF 样本内泄漏（主题 F）；`tone_words-04` IDF 语料口径分叉（主题 B）。

**BERT 情感**：`tone_berts-01` `label_map` 只校验标签数不校验模型 `id2label` 顺序，上游 checkpoint 重排即静默正负对调，且 count 不等时 fallback 顺序与配置相反 (`:309-318`)；`tone_berts-03` `bert_avg_pos` 跨 2 类/3 类模型直接行均值，概率尺度不可比、随 finbert2 可得性漂移 (`encode.py:935-945`)。

**LM4子词典+FLS**（serious_issues）：`lm_fls-01/02` jieba 漏配（主题 A）；`lm_fls-03` 双门控 AND 偏离 Li 2010 召回导向、系统低估 FLS；`lm_fls-04` 面板聚合 mean-of-fractions + skipna 偏离 LM 文档池化口径（小文偏倚）(`encode_collab.py:759-785`)；`lm_fls-05` 「non-sentiment」标签缺判别效度证据，39e 从不对情感轨检验且词典含强情感词（欺诈/危机/违法）(`lm_discriminant_validity.py:70-86`)。

**金融科技强度**：`fintech_intensity-02` verified 门控在聚合层失效、0 值稀释（主题 C）；`fintech_intensity-05` 单元零单元测试。

**社会效益**：`benefit_society-02` placebo 排他性论证缺口（业务线文本含 fintech 渗透污染）+ β/阈值 0.3 缺统计检验 (`benefit_society_placebo.py:140-223`)。

**跟风衰减**：`herd_decay-02` 样本内 IDF、规模依赖漂移（主题 F）。

**面板聚合 encode**：`encode-01` 加权分母（主题 C）；`encode-02` `n_articles` 用 LLM-valid 计数冒充新闻覆盖篇数（`count(llm_vote_score_full)` 跳过 NA ≤ 物理篇数），污染 `tech_frac`/`ln_news_coverage`/恒等式校验 (`encode.py:574`)。

**协同聚合 encode_collab**（serious_issues）：`-01/-02` herd 幽灵列（主题 D）；`-03` 加权分母（主题 C）；`-04` docstring「与 llm_vote_tone 同权重」与实现及主轨均不符。

**LLM 同伴 IV**：`llm_peer_iv-01`（主题，见 P0-⑨）；`llm_peer_iv-02` T=2 退化（主题 H）。

**Bartik/DID**：`iv_did-01` NaN shift 置零但 share 不重归一化 → Σshare<1、IV 向 0 偏 (`:236,353`)；`iv_did-02` share 由 co_mentioned_banks 计数构造、外生性论证不足且同文同组双计数 (`:122-149`)；`iv_did-03` shift 是 LOO 组情感均值(内生反射)，识别仅靠 share，但文件头把 BHJ 2022 列为 shift 视角锚点 → 误导审稿人以为有双重识别 (`:210-218`)；`iv_did-04` `diagnose_rotemberg_weights` 用 `Cov/Var` 近似冒充 α_k，却输出带 GPSS §5.2 署名的负权重/排他性结论 (`:730-794`)。（后三项均与终审独立核验一致）

**地理/留一IV**：`geography-01` 加权分母（主题 C，contested）。

**网络/经纪**：`network-01` 邻接矩阵共现计数翻倍（firm-document 展开 + 对称双写，一篇 {A,B} → adj=2）(`network_spillover.py:132-150`)；`network-02` 溢出权重缺失填 0 不重归一化（主题 C）；`network-03` `bank_emb_sim_mean` 仅对正相似度取均值 → 上偏且与 `cogn_mean` 口径不一致 (`:1209-1210`)。

**媒体注意力**：见 P0-⑧ + `attention_media-04`（主题 E）。

**风险结果**：`risk_outcomes-02` Z-score 用 CAR 替代 equity/assets，**代码 docstring 已诚实标注**为 CAR 变体，但 `bank_news_clarity`/`bank_media_disagreement` 两篇 paper_spec.yaml 仍写「Laeven-Levine 2009 标准」→ 论文层归因与代码层 caveat 矛盾 (`risk_taking_outcomes.py:179`)。（终审独立核验一致）

**EPU**：`epu-01` 文章数加权（主题 C）；`epu-03` `epu_std_year` 主分支被文章频率加权、与 fallback 分支口径不一致 (`:165 vs 138-139`)。

**判别效度**：`discriminant-01` HTMT 在 single-item 退化为裸 |corr|、reliability 分母硬置 1，仍叫 HTMT 并套 0.85/0.90 cutoff (`:90-91,108`)；`discriminant-02` κ 阈值样本内 median（主题 F）。

**陈旧度/主题**（serious_issues）：`staleness_topic-01`（P0-①）；`-02` 两轨窗口定义不对称（surface 严格排除同日、semantic 含同日早发文）→ 污染 `staleness_corr` 门控 (`:150-155 vs 227-236`)；`-04` BERTopic outlier topic(-1) 被当正常 topic 计入 frac 与 HHI（BERTopic 常见 30%+ outlier 率）(`article_topic.py:190-208`)。

**高管 NER**：`exec_ner-01` full 轨读裸 `内容`（主题 B）；`exec_ner-02` mention_count 全盘采信 LLM 自报数、无样本内校验（主题 E）；`exec_ner-03` 2000 字截断使长文 count 系统性下偏、与 doc_length 协变（非随机测量误差）(`:252`)；`exec_ner-04` bank-year 用 `mean(hhi)`/`mean(count)` 而非提及加权/sum，丢失曝光强度 (`:461,467`)；`exec_ner-05` HHI 与所引三篇文献无理论对应（事后归因）。

**Embedding**：`embedding-03` `CONFIG.get('embedding',{})` 为永久落空死配置键，「单源对齐」失效（值恰巧等于硬编码默认故不改结果）(`article_sbert.py:58-60`)；`embedding-01/02` L2 归一化口径不一致（contested）。

**Stata 派生**：`stata_vars-01`（P0-③）；`stata_vars-02` 缩尾命名跨模板不一致（root 用 replace、衍生链用 suffix `_w`）→ 根链路裸名语义不可判定；`stata_vars-03` T=2 差分退化（主题 H）。

---

## 5. P2 / P3 摘要（26 确认 P2，44 未验 P3）

代表性 P2：`epu-02` `epu_year_end` 取「最后有数据月」而非 12 月、label 失实 off-by-one；`epu-04` completeness 用 `nunique()` 数值去重误判（contested）；`tone_berts-01` label_map 顺序；`network` 系列口径；`discriminant` HTMT/κ 命名；`embedding` 归一化与死配置键。完整列表见 `_v2_findings_digest.txt`。P3 多为文档/命名/展望项，低优先。

---

## 6. 公式合规矩阵（单元级 verdict）

| 单元 | verdict | 单元 | verdict |
|---|---|---|---|
| LM4子词典+FLS | **serious** | encode_collab | **serious** |
| 陈旧度/主题 | **serious** | LLM情感 | material |
| 词典情感 | material | BERT情感 | material |
| 金融科技强度 | material | 社会效益 | material |
| 跟风衰减 | material | 面板聚合encode | material |
| LLM同伴IV | material | Bartik/DID | material |
| 地理/留一IV | material | 网络/经纪 | material |
| 媒体注意力 | material | 风险结果 | material |
| EPU | material | 判别效度 | material |
| 高管NER | material | Embedding | material |
| 伪造检验 | material | Stata派生 | material |
| 数值密度(run1) | material | 上下文/实体(run1) | material |
| 清晰度/中文工具 | minor | 政策对齐 | minor |
| 战略差异化(run1) | minor | | |

每单元逐指标 `matches=yes/partial/no` 见 `_metric_audit_merged.json::units[*].formulas_checked`。

---

## 7. 各单元清白认定（明确背书，符合顶刊标准的指标）

对抗验证证伪了 29 条误报，并确认以下指标**逐项正确**：

- **战略差异化主指标**：`strat_diff_n{3..7}`（TF-IDF char/word N-NN，Guzman-Li 2023 逐项一致，sublinear_tf 合 Manning 2008）、`strat_diff_n5_emb`、`strat_fluidity`（Hoberg-Phillips-Prabhala 2014 Eq.2 完全一致）、`strat_sim_max`、`coh_*`。**该论文主处理计算无误。**
- **跟风衰减算法本身**（producer 端）：`weight=1/(1+n_predecessors)`、只用前驱无前视、NaT 处理稳健、TF-IDF 决定性（bug 纯在 encode_collab 消费端列名）。
- **数值密度**：`万亿` 复合单位转换（v3.7.1 P-042 修复正确）、Eq.1 分子/分母结构、加权 sum/sum 骨架。
- **上下文/实体**：`extract_entity_context` 确定性/再现性、`prepend_title` 空透传/去重/幂等。
- **llm_peer IV**：留一均值排除自身正确、Manski 滞后规避反射；缓存 peer 网重建忠实（`_iv_full` 19 值 max_abs_diff=0）。
- **DID 变量**：`_post`/`_rel_year`/lead-lag/endpoint binning 合 Callaway-Sant'Anna / Sun-Abraham 标准。
- **政策对齐 / 清晰度**：核心余弦相似度与清晰度比率骨架正确（仅边界/分句瑕疵）。

---

## 8. 对抗验证剔除的误报（体现验证有效性）

29 条被双棱镜证伪（含 2 条 P0、14 条 P1、13 条 P2），例如：词典 tone 归一化与 Antweiler-Frank/LM 不一致（`tone_words-01`，公式棱镜证伪——实现等价）；多处「理论上可能但代码已防御/不可达」的伪问题。完整证伪清单见 `_metric_audit_merged.json`（status=refuted）。**这说明评审并非无差别堆砌，对抗层确实在过滤。**

---

## 9. 完备性缺口（仍需立项审查）

- `runner.py:1448-1560` 的 `disag`(32 变量)/`concern_score`/`log_sent`/`algo_cater`/交互项：进回归的 treatment/moderator，**零 closed-form 公式测试**；`disag` 跨方法量纲混用（词典词级比率/LLM 篇级计数/BERT 概率均值共用 `sqrt(1-((pos-neg)/(pos+neg))²)`），`concern_score` 用 `neg-pos` 与 `disag` 用 `pos-neg` 方向相反待确认（run-1 完备性批判 + uncertain）。
- 审计模块 39c/39d/39e/39f 只验**分类/情感构念判别效度**（NMI/HTMT/κ/α），**不验派生 panel 列算术** —— 这是真实空白，非被覆盖。建议设立与 39x 并列的「派生列算术正确性审计层」。
- Stata 端基本是占位符替换（仅 llm_peer/benefit_society 有 `gen` 交互项），不在 Stata 重算上述构念 → 口径漂移主要落在 **encode vs encode_collab vs runner/geography 的 Python 内部**，而非 Stata。

---

## 10. 优先级修复路线图

### 阶段 0 — P0（阻断论文主结果，立即修）
1. **主题 G 行错位**（`staleness_topic-01`）：return 前加逆置换 + round-trip 测试。数据完整性级，最先修。
2. **主题 D herd 幽灵列**（最快、确认即坏、测试帮倒忙）：`encode_collab.py:503/583` 改 `herd_weight_full`；删测试伪列，加 `herd_weight≠1.0` 非平凡断言；重生 golden snapshot。
3. **P0-② cn2arab inflation**：接 jieba POS（仅留 CD/m、剔「第」序数）或成语/专名 blacklist；更正 docstring「≈1%」为实测 22%；加 negative 测试；**重跑 Table A9 重估结论**。
4. **P0-③ winsorization 孤儿**：`11_table2_main_m1m6.do` 改 `use _prepared_panel.dta`（对齐 benefit_society/llm_peer）。
5. **主题 A jieba 漏配**（`fintech_intensity-01` TF/DF + `lm_fls-01/02` + `clarity_cn-01`）：统一改 AC 自动机匹配引擎；重跑 stage 14/22 + 重生 golden snapshot。
6. **主题 B 标题不对称**（`tone_llms-01`/`benefit_society-01`/`exec_ner-01`/`fintech_intensity-04`/`tone_words-04`）：full 轨统一读 `content_full`；LLM ctx 轨消费去标题 body。
7. **P0-⑧ attention 锚点 + tier 死代码**：物化 paper_spec 的 text-intensity 双轨 attention，或诚实降锚为 Fang-Peress coverage 并删 tier 死代码。
8. **P0-⑨ llm_peer 预筛归一**：句内计数前归一到 canonical 去重（或复用 AC `analyze_bank_matches`）；重跑 stage 7h-llmpeer 校验 IV 变动。

### 阶段 1 — P1（系统性偏差 + 因果识别核心）
9. **主题 C 加权分母**（encode/encode_collab/geography/network/epu）：统一「有效行权重和」分母。
10. **Bartik 识别诚实化**（`iv_did-01/02/03/04`）：NaN shift 重归一化 share；删/降级 BHJ shift-view 主张、只主张 GPSS share 视角；`diagnose_rotemberg_weights` 重命名为近似投影、正式诊断走官方 `bartik_weight`。
11. **encode `n_articles`**：改 `groupby.size()`，新增 `n_articles_llm_valid` 保留旧语义。
12. **BERT 标签映射**（`tone_berts-01`）：以模型 `id2label` 为唯一真值 + 顺序断言；2 类/3 类概率统一净极性尺度后再平均。
13. **network 邻接翻倍**（`network-01`）：文章级去重 + 单向累加后一次对称化。
14. **risk Z-score 归因**（`risk_outcomes-02`）：采集 equity/assets 另算主指标、CAR 降为 robustness；或改 paper_spec 归因措辞。
15. **立项「派生列算术审计层」**：覆盖 `runner.py` 8b-8e disag/concern_score、geography LOO IV、llm_peer IV，逐公式补 closed-form 测试，确认 disag 量纲与符号约定。
16. **主题 F 样本内泄漏**：IDF/分位数/κ 阈值改外生冻结（sidecar），或论文显式披露 in-sample 性质 + 稳健性对照。

### 阶段 2 — P2（口径/标注/防御性）
17. EPU year-end/std/completeness 口径；HTMT/κ 命名与 single-item 披露；embedding L2 归一化 + 死配置键；exec_ner 截断/聚合/锚点；staleness 双轨窗口对齐 + outlier 剔除；Stata 缩尾命名统一；fintech 补单元测试。

---

## 附：审查产物
- `METRIC_AUDIT_REPORT_2026-06-02.md`（本报告）
- `_metric_audit_merged.json` — 全部 175 条发现 + 258 裁决 + 理由（机器可读，可追溯）
- `_v2_findings_digest.txt` — v2 全量发现明细（190KB）
- `_v2_p0p1.md` — 确认/争议 P0+P1 精简版
- `_metric_audit_run1_3units.txt` / `_metric_audit_run2_24units.json` — 两轮工作流原始输出
- `metric_audit_workflow.js` / `metric_audit_workflow_v2.js` — 可复跑的审查工作流脚本

**终审裁决**：指标体系工程质量高、多个核心公式经验证达顶刊标准并已背书；但因 8 类确认 P0（含 1 个数据完整性级行错位、1 个直接污染 Table A9 的 22% inflation、跨模块的 jieba 漏配与标题不对称系统缺陷）+ 因果识别核心派生列整层零公式覆盖，**当前尚不满足顶刊「零错漏」标准**。按路线图修复阶段 0/1 后重跑相关回归、并补建派生列算术审计层，方可投稿。所有 `terminal-verified`/`confirmed` 发现可直接进入修复工单；`contested`/`uncertain` 需人工复核后定夺。
