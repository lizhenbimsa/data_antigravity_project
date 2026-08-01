# news_process 指标计算体系 — 最终终审报告（三层验证收敛版）

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


> 本报告**取代** `METRIC_AUDIT_REPORT_2026-06-02.md`（初版）。初版的 P0/P1 定级**不可直接采信**——经元验证后原 P0 约 50% 被降级/推翻，且初版漏报了 2 个 active-crash P0。本报告为最终权威净清单。

**审查日期**：2026-06-02
**三层验证**：
1. **原审计**（27 单元 × 深度评审 + 双棱镜对抗验证 + 完备性批判）→ 175 条发现。
2. **元验证**（24 模块对抗式逐条**经验复现** + 假阴性猎取）→ 80 upheld / 20 overturned / 22 restate-magnitude / 17 severity-adjust / **93 漏报**。
3. **终审亲自经验复现**（在本机 jieba 0.42.1 / pandas 3.0.3 / 盘上真实语料上运行）→ 逐一坐实关键 P0 + 新发现，并独立逮出 1 处量级错误。

**证据分级**：`yes_empirical`=已跑代码/数据复现；`yes_codepath`=逐行读代码确证；`latent`=机制成立但当前数据/配置下不触发。

---

## 1. 原审计可信度评级：B+（机制可靠，定级偏高，覆盖有盲区）

| 维度 | 评级 | 依据 |
|---|---|---|
| **机制识别** | **高** | 142 条复核中 122 条（86%）机制成立，**零凭空捏造代码行为**；20 条 overturned 多为"代码行为属实但承重机制虚假/不可达" |
| **严重度定级** | **中** | 39 条调级（20 overturned + 17 severity_adjust + 部分 restate）；主因：(a) 把 latent 当 active；(b) 把标准 IR 实践误判为计量泄漏；(c) 把"理论可能但代码已防御"当缺陷 |
| **覆盖完整性** | **低（最大短板）** | 93 条漏报，含 **2-3 条 active-crash P0**；根因：原审第一轮**只静态验证 metric 公式、从未对 `main()` 跑真实数据**，致 3 个 stage 端到端崩溃被整体漏掉 |

**结论**：原审计可作为缺陷线索源，但**最终 P0/P1 净清单须以本报告为准**。

---

## 2. 最终 P0 净清单（4 条，全部 `yes_empirical` 实跑确认）

### P0-① ctx 轨 LLM prompt 标题双重注入（原审 upheld）
`tone_llms.py:562-571` + `ctx_materializer.py:138`。stage 13 已把标题 prepend 进 content_ctx，stage 21 又把 title 作独立字段喂 prompt → ctx 轨标题进 prompt **2 次**，full 轨 1 次。主处理候选 `llm_vote_tone_ctx` 取值依赖 stage 顺序。**1170/1170 active**；且 prompt 文本不同 → LLMCache 键不同 → 破坏 $0/缓存再现性。
**终审复现**：`13_news_with_ctx.parquet` 1170/1170 行 content_ctx 含标题前缀（已验）。

### P0-② Hassan 2019 QJE 锚定的 attention 指标 4 个幽灵列零产出（原审 upheld）
`attention_media.py:197-345`。代码只产 geo/year 的 article-count 占比（单轨、无 full/ctx、无标准化、无 dispersion/percentile），而 paper_spec R36-m01 声称的 `attention_index_full/ctx/disp/pct` 从未物化 → `figures.py:35` 实跑 KeyError。代码实现 ≠ 论文声称的 treatment。

### P0-③【原审漏报】exec_ner main() `groupby('year')` KeyError + 跨银行双归因（active crash）
`executive_ner.py:467`（及 :400 读 13_news_with_ctx.parquet 后无 year 派生）。
**终审实跑复现**：13_news_with_ctx **无 `year` 列**（仅 str 型 `日期`）；`df.groupby(['target_bank','year'])` → **`KeyError: 'year'`**。grep 确认全模块仅 :467 出现 year、**无任何 `dt.year` 派生**（对照 runner.py:1094 / attention_media.py:255 都显式派生并注释"否则 KeyError"）。`config['executive_ner']['enabled']==True`（2026-06-01 全功能打开）→ **active 非 latent**：跑真实管道时 stage 19 在聚合处 abort，NER 面板列永不产出。
**附**：多银行文章跨 target_bank 重复归因——**实测 79/1015=7.8% docid 挂 >1 银行**（docid 2017111300003019497 同挂建设/中信/中国银行），同批高管被双计入多家 bank-year 的 `n_ceo_mentions/exec_hhi` + LLM 成本虚增。

### P0-④【原审漏报】staleness stage 18 main() `groupby('year')` KeyError（dead-on-arrival）
`article_staleness.py:296-338`。同型 bug：main 读无 year 列的 13_news_with_ctx 却按 year groupby → `18_staleness_panel.parquet` 根本产不出。stage 18 已启用（faiss+datasketch **均已装**，终审实测）。
**另**：surface staleness 还有独立的**行错位**（`:300-306` 返回排序序数组按位置赋回未排序帧；终审实测盘上 13_news_with_ctx **未按日期排序、99.8% 行会移位**）——但因 groupby KeyError 先崩，该列实际产不出，故并入本 P0。

> **从 P0 降出（原审 7 条 P0 误定级）**：fintech_intensity-01（P0→P1，"21%"量级不复现）、benefit_society-01（P0→P1，0 符号翻转）、geography-01（P0→P2，方向判反 + 列族零消费）、encode_collab-01（P0→P1，生产仍按 media 加权非退化为 1.0）、llm_peer_iv-01（P0→P1，LLM 语义层缓释）、iv_did-01（P0→P1-latent，生产 corpus 上 0 行触发）、risk_outcomes-01（**overturned**，归因错误：stage 49 读 dry_run 18 年数据非 T=2 面板）。

---

## 3. 最终 P1 净清单（约 50 条）= 原审 upheld-P1 + 上调 7 + 从P0降入 5 + 漏报新增 25

### 3.1 横切根因 A：双轨标题注入不对称（≥6 单元同构，多数第一轮漏标）
v3.8.0 规定 full/ctx 两轨都"含标题"，但多模块 full 轨仍读裸 `内容`：
- `tone_llms-01`（P0-①，双重注入）｜`exec_ner-01` full 读裸内容、99.4% 行 内容≠content_full、漏标题高管（P1，`executive_ner.py:414`）
- `fintech_intensity-04` full 用裸内容/ctx 用含标题 content_ctx（P1，`:400 vs :411`）
- **【漏报】政策对齐**：ctx 轨标题**双重注入**，`auth_sim_*_ctx` 10 列已落 panel、full↔ctx ρ=0.900 逼近坍缩（P1，`strategic_diff.py:333-335` + `policy_similarity.py:116-118`，yes_empirical）
- **【漏报】herd_decay** full 轨读裸内容（P1，`herd_decay.py:221`，23 篇 herd_weight 改变）
- **【漏报】staleness** surface_full 用 body、semantic_full emb 含标题、ctx 含标题——同 _full 轨子指标文本不一（P1，`article_staleness.py:301`）

### 3.2 横切根因 B：T=2 面板下 lag/IV/DiD 结构退化（≥4 单元）
- `llm_peer_iv-02` IV 滞后吃掉首年 → 非空仅 **18 值/全在 2018**，2SLS 退化为单期横截面（P1）
- **【漏报】iv_did**：Bartik share **64%（112/176）退化为 own-type one-hot**、仅 19% 真混合 → IV 近共线 bank-type FE（P1，终审实测）；fintech Bartik 基期 96.7% app vs 3.3% tech → share 近常数、一阶段 F 必弱（P1）
- `iv_did-06`（上调 P2→P1）：`dcep_post/sandbox_post` 恒为 0、rel_year 全负 → DiD 在 corpus 上**根本不可识别**（实测）
- **【漏报】network**：全部 lag 类（含 IV `peer_tone_2nd_lag1`）仅 2018 单截面有值（P1）；`network-04`（上调 P2→P1）二阶溢出 `W²` 对角 44% 银行>0=自反馈、破坏 Bramoullé 排他性

### 3.3 加权/聚合口径（encode 族）
- `encode-01`（**上调 P2→P1**）：VW/MW/HW 加权 tone 分子分母样本不匹配，19 个混合 BY 衰减因子最差 **0.106**（单 BY VW tone 被衰减 89%）（yes_empirical）
- `encode-02`（**上调 P2→P1**）：`n_articles=count(llm_vote_score_full)` 跳过 NA = LLM 有效投票篇数非物理篇数，17.6% BY 低估、污染 `ln_news_coverage`/所有 frac 分母/digital_frontier 分组（yes_empirical）
- `encode_collab-01`（P0→**P1**）：herd 幽灵列 `herd_decay_weight` → 33% BY 权重退化为"仅 media"（非退化为 1.0）；grep 坐实该列仅在 2 消费点 + 3 测试夹具、无 stage 产出（yes_empirical）
- **【漏报】encode** tone_gap_sub_symb/indep_collab 4 个 gap 缺 min-n≥5 防混淆门（`:1119-1122` 等，对照 `:800` 有守卫），18 个现存 gap 100% 低于阈、67% 单篇驱动（P1）
- **【漏报】encode-01/02 在 _ctx 轨严重度是 _full 的 3.1×**，而 _ctx 是 G3 主处理（P1）
- **【漏报】encode_collab** `frac_amb_articles_ctx` 用 full 轨 median 作 ctx 阈值、~7.5% 文章误分类（P1，active）

### 3.4 词典/LM/清晰度
- **【漏报】tone_words** 文章级 pos_ratio/neg_ratio/msent 取自"逐文章匹配最多的词典"，**91.2% 文章 best≠主词典** → 面板 avg_* 是漂移混合度量（P1，`:877-931`）
- `tone_words-03` pos/neg 计数用否定后符号、与同模块 MSENT 内部不一致（P1）
- **【漏报】lm_fls** `n_tokens` 分母含标点/纯数字 token（前 500 篇 18.5%）→ frac 在 jieba 漏配（13-27%）之上再叠 ~18% 同向下偏（P1，`lm_non_sentiment.py:118`）
- `lm_fls-01`（jieba 漏配，**终审实测精确**：uncert 19/83·litig 22/104·constr 9/76·modal 8/51）｜`lm_fls-02`（FLS time-marker **28/59** 实测）｜`lm_fls-04`（mean-of-fractions 偏离 LM 池化）｜`lm_fls-05`（non-sentiment 缺判别效度、词典含强情感词）
- **【漏报】clarity_cn** `_is_valid_token` 丢弃 460 个英文领域词（AI/ATM/IPO 共 3813 occ）却留百分数噪声、对 fintech 主题模型危害大（P1）
- `clarity_cn-01`（引号分句破损）**量级反转**：净效应 **+18.99% 上偏**非下偏（P1→**P2**）

### 3.5 BERT / Embedding
- `tone_berts-01` label_map 仅校验标签数不校验 id2label 顺序、上游 checkpoint 重排即静默正负对调（P1）
- `tone_berts-03` `bert_avg_pos` 跨 2 类/3 类概率直接行均值、尺度不可比（P1）
- `embedding-01`（**上调 P2→P1**）API/本地路径 L2 归一化口径分裂、centroid 路径 32% 走归一化混排、Spearman 仅 0.16（yes_empirical）

### 3.6 金融科技强度（核-01 真危害）
- `fintech_intensity-01`（P0→**P1**）：TF(jieba)/DF(AC) 引擎不一致——**终审实测** 11 个关键词 AC-DF>0 但 jieba-DF=0；但完整管道后 IDF 平均绝对偏差仅 0.0065、相关 0.992、数值冲击<1%（故非 P0）
- **【漏报】fintech verified 门控真危害**：matching 不一致传播进 verified 门控、**清零 AC-已分类 fintech 文章**（5 个 full-verified=False 行 AC-DF 全=3）——这是离散样本剔除而非估计漂移（P1，`:311,313`）

### 3.7 社会效益 / EPU / 判别效度 / 风险 / 伪造 / Stata
- **【漏报】benefit_society** 余弦投影未零中心化 → `benefit_pos_frac` 均值 **0.969**（96.9% 投影>0）近饱和退化、作自变量信息量趋零（P1，`:497,621-622`，磁盘 n=119 复现）
- `benefit_society-01`（P0→**P1**）full 轨裸空格拼接非 prepend_title（0 符号翻转）
- **【漏报】EPU**：`epu_data_complete` 生产语料下**结构性恒为 0**（bank-year 最多覆盖 2 月、永<12）flag 完全失效（P1）；主路径 vs fallback **同数据产出系统性不同 EPU**（mean 差 ~50%、complete 相反）、**生产走错口径**、文献正确实现被降级为 fallback（P1）
- `epu-01`（article-count 加权）**方向反转**：157/157 cell 全部**下偏**（非原审"上偏 +3"）（维持 P1）｜`epu-03` `epu_std_year` **77% 退化**（NaN+0）、label 名实严重不符（P1）
- **【漏报】判别效度**：39e `np.fill_diagonal(df.values)` 在 **pandas 3.0 CoW 下运行期崩溃**（**终审实测** `writeable=False` → ValueError）、默认启用 validation stage 零测试（P1，`lm_discriminant_validity.py:143,152,204`）；39d Cohen κ 真实数据上 substance 侧恒<0.5 → s_bin 全 0 → **κ 结构性退化为 0.0**（P1，无 constant-axis 守卫）
- `discriminant-01`（HTMT==裸\|r\|）：机制属实但 HTMT≥\|r\| 恒成立 → 用 \|r\| 套 0.85 是**保守**检验（P1→**P3**）
- **【漏报】风险结果**：`bank_list.yaml` 默认路径在 cwd=news_process/ 下解析失败 → is_soe/tier 静默全 NaN（P1，实跑确认 + warning）；`build_risk_taking_outcomes` 缺 T 守卫、短面板静默全 NaN z_score 无告警（P1）
- **【漏报】伪造检验** `fintech_share` 分子分母计数基不一致、最坏单 BY 偏 25pp、Stata 赛马回归直接消费（P1，`controls.py:615-619`）
- **【漏报】Stata** Table 1 描述统计在缩尾数据（继承 01_data_prep 内存态）、Table 2 主回归在原始数据（`use core.dta, clear`）→ **同论文内样本口径互反、审稿人可见**（P1）；`stata_vars-01`（root winsor 孤儿，**终审读 :17 确认**）

> **P1 中 3 条 latent 需标注**：`encode_collab-03`（NaN 加权分母，当前 clarity NaN 率 0/859）｜`iv_did-01`（NaN-shift 衰减，生产 0 行触发）｜`stata_vars-03`（一阶差分 T=2，ROA 列当前不在 panel）。

---

## 4. 被推翻的原发现（20 条 overturned）+ 量级更正（22 条）— 不得再作为缺陷主张

**关键推翻（须从初版报告删除/降级）**：
- `tone_words-02`（IDF 样本内泄漏）— **overturned**：IDF 是无监督词权（Manning 2008 Ch.6.2.1 教科书定义"相对 collection 计算"），GKT §2.2 警示的是监督式特征；不存在泄漏路径。
- `risk_outcomes-01`（T=2 z_score 全 NaN）— **overturned**：stage 49 读 `--input` dry_run 季度数据（full 模式覆盖 2007-2025），不消费 T=2 文本面板（残余真问题"无 T 守卫"已升为 §3.7 漏报）。
- `fintech_intensity-03/06/07`（Winsorize 漂移 / jieba 跨 stage 污染 / Parallel 顺序）— overturned：scale-equivariant（2.2e-16）/ subprocess 隔离 / 只读 trie。
- `encode-04`（std NaN 两来源不可分）— overturned：n_articles(0 vs 1) 精确分离。
- `geography-02/03/04/05/06` — 多条 overturned（dict_avg_tone 不含 IDF 子项=前提假；标题与正文自相矛盾；门槛不可达；省会退化 0.9% 几乎不触发）。
- `attention_media-03/05/06`、`epu-04`、`discriminant-07`、`embedding-05`、`stata_vars-04` — overturned（常数 rescale 对消 / 跨年值碰撞 / pandas 3.0 无 warning / 不可达 / pooled-SD 可辩护）。

**关键量级更正（机制对、数字须改述）**：
- **cn2arab inflation（初版 P0-②）**：初版"22% / 90.3% / 10184 / 1057"**不可复现**——总数字 token 46338 精确吻合，但**终审在真实语料复现**：cn2arab 净增 token 20498=**44.2%**、"第N"序数 1697 波及 **50.8%** 文章、已知成语≥999 波及 26.4%。**机制坐实（三农→3农、十八大→18大、第三季度→第3季度均产假数字 token）、结论（mean_num_intensity 受污、Table A9 需重估）不变，但具体百分比须改为上述复现值。**
- `network-01`（共现翻倍）：初版"W 整体约掉 peer_tone 不受影响"的**免责声明 overturned**——真实 explode 数据上 buggy/true 比值非均匀（0–2.0）、行归一化后 30% 银行行改变、污染 brokerage 2SLS 内生量与 IV，后果**比初版更重（近 P0）**。
- `benefit_society-01` P0→P1（投影 corr 0.996、0/200 符号翻转）｜`iv_did-01` P0→P1-latent（0 行触发）｜`llm_peer_iv-02` "84 行"→实测 18 值。

完整 20 overturned + 22 restate 见 `_meta_verify_report.md` §2-3 与 `_meta_verify_digest.txt`。

---

## 5. 优先级修复路线图（按横切根因，非逐 finding 点修）

### 阶段 0 — P0（阻断 / 崩溃，立即修）
1. **修 2 个 active-crash P0**（最快、确认即崩）：exec_ner（`:467` 前）+ staleness（`:335` 前）补 `df['year']=pd.to_datetime(df['日期']).dt.year`；staleness surface 加逆置换还原原序（对齐 semantic `:244`）。
2. **attention_media-02**：物化 paper_spec 的 text-intensity 双轨 attention，或诚实降锚为 Fang-Peress coverage 并删幽灵列宣称。
3. **tone_llms-01**：ctx 轨消费"去标题的纯 ctx body"（stage 13 额外保留 content_ctx_body，或 tone_llms 剥离已 prepend 的标题前缀）。

### 阶段 1 — 横切根因统一修（消多单元症状）
4. **根因 A（标题不对称）**：全仓 full 轨统一读 `content_full`（exec_ner/fintech_intensity/herd/policy/staleness/benefit_society 六单元），重生 golden snapshot。
5. **根因 B（T=2 退化）**：iv_did/llm_peer/network/geography 统一标注 first-stage 有效 N/F、披露单截面退化、降权相关 spec；Bartik 改用真正预定的结构暴露 share 或承认 GPSS-only 识别 + Rotemberg 走官方包。
6. **加权分母（encode 族）**：统一"有效行权重和"分母；`n_articles` 改 `groupby.size()` + 新增 `n_articles_llm_valid`；herd 幽灵列改真列名 + 删测试伪列。
7. **判别效度崩溃**：39e `np.fill_diagonal` 改 `.to_numpy(copy=True)`；39d 加 constant-axis 守卫。

### 阶段 2 — P1 余项 + P2
8. 词典 best-dict 漂移、lm n_tokens 分母、fintech verified 门控、benefit 零中心化、EPU 月度等权 + complete flag、risk bank_list 路径 + T 守卫、falsification fintech_share、Stata 缩尾口径统一（Table1/Table2 同源）+ 全 portfolio `_w` 后缀。

### 阶段 3 — 修正初版报告
9. 从初版报告删除/降级 20 条 overturned（尤其 tone_words-02、risk_outcomes-01）；改述 cn2arab/network-01/epu-01 量级。

---

## 6. 诚实校准声明

- **P0 净清单 4 条全部 `yes_empirical`**（终审实跑复现 KeyError / 幽灵列 / 排序错位）。
- **P1 净清单约 80% `yes_empirical`、20% `yes_codepath`**（主要是 Stata 模板缩尾、encode_collab 口径等代码直证类）。
- **方法论教训（供未来审查）**：原审第一轮"只验 metric 公式正确性、从未跑 `main()` 真实数据"是覆盖盲区根源——3 个 stage 公式对但 stage 端到端崩溃却全漏。**任何顶刊级指标审计必须包含"在真实数据上跑通每个 stage main() 到面板落列"的端到端门控。**
- **未触及范围（诚实边界）**：本审查覆盖 Python 指标构造层；Stata **回归估计本身**（reghdfe/ivreghdfe 的 vce/absorb/弱工具检验输出）仅抽查变量构造，未逐表复核回归设定的计量正确性；下游论文表格数值未重跑。

---

## 附：审查产物（全在 `scripts/audit/`）
- **`METRIC_AUDIT_FINAL_2026-06-02.md`**（本报告，最终权威）
- `_meta_verify_report.md`（元审计裁决全文）｜`_meta_verify_digest.txt`（20 overturned + 22 restate + 17 调级 + 93 漏报明细）｜`_meta_verify_raw.json`
- `METRIC_AUDIT_REPORT_2026-06-02.md`（**初版，已被本报告取代，P0/P1 定级勿直接采信**）
- `_metric_audit_merged.json`（原审 175 发现 + 258 裁决）｜`_v2_findings_digest.txt`
- `metric_audit_workflow.js` / `_v2.js` / `metric_audit_meta_verify.js`（三层可复跑工作流）
