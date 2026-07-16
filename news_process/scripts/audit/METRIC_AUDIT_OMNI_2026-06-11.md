# 指标计算终极复审 — 权威闭合报告 (OMNI, 2026-06-11)

> 对 news_process 全仓**所有指标计算**按国际顶刊 (AER/QJE/JF/RFS/JFE) 复现包标准做的第四轮、覆盖面最大的一次系统复审。
> 在 2026-06-09/10 三层审计+修复闭合 (commits `b0442124`/`5d5561e9`/`cd5afb48`) 之后的 main 上执行, 猎取漏网新缺陷并核验修复落地。

**方法**: 三波多智能体工作流 (Wave-1 59单元: 6修复核验+40模块/模板/论文单元+8同型扫描+3数据实证; Wave-2 19补跑单元+30批量复核官; Wave-3 10收尾单元+5组遗留裁决) + 主控亲验。
合计 **~474 个 agent / ~22.5M tokens**; 每条发现经对抗证伪 (P1 三镜头 / P2 双镜头 / P3 单镜头, 或批量复核官逐条读码裁决); 双 critic (覆盖完备性+裁决质量) 复核裁决层; 主控对全部 P1 与争议击杀亲验终裁。
**口径**: READ-ONLY, $0, 未改任何生产代码; 盘上 T=2 试跑样本 (174 行 bank-year, 2017-2018), 全量为 18,198,978 篇/2007-2025/T=19 — latent 缺陷按全量触发性裁决。

---

## 0. 总裁决


本轮共产出 **348 条唯一发现**, 经对抗证伪与主控终裁:

| 桶 | 数量 |
|---|---|
| **P1 确认 (含 latent 3)** | **22** |
| P2 确认 (活跃) | 117 |
| P2 确认 (latent, T=19 触发) | 13 |
| P3 确认 (活跃) | 119 |
| P3 确认 (latent) | 54 |
| 证伪击杀 (refuted) | 9 |
| 归并已知台账 (dup-known) | 14 |
| 未决残余 | 0 |

**核心结论**:
1. **2026-06-10 的修复活动本身基本守住了**: 39 项修复核验 36 verified / 3 partial (引文残留 2 处 + 回归锁 3 个 vacuous 既有测试), 无一 broken; golden 复现 39 测试绿; panel 值修复全部盘上实证生效 (peer_tone 伪零清零 / JF∈[-1,1] / bartik 行和=1 / JSD∈[0,1] / sum_wd_ 零填)。
2. **但修复活动之外, 本轮在此前从未深审的层面逮出大量真缺陷**: 预处理语料层 (数字被正则破坏)、实体匹配层 (嵌套变体重复计数)、BERT 推理层 (tokenizer 错配)、验证器自身 (IDF 泄入 BERT 族 / 评估口径污染) — 此前四轮审计集中在 panel 公式层, 这些上游/旁路层是系统性盲区。
3. **复现包/Stata 模板层结构性塌方 (本轮最重的新发现面)**: 11 篇论文中约 10 篇的 build-replication 主回归链不可跑通 — P2-P5 与全部衍生论文的 MAIN_DV/CONTROLS 为幻影列 (外部财务面板从未接入), P3/P5 把文章级列名当 panel 变量, P3 outcome 名 36 字符超 Stata 32 上限, benefit Table 6 `se ci` 互斥崩链, 论文 10/11 主 treatment+控制无任何可产出数据源, 五篇主线 esttab 只写 .tex 而 python 表格层只读 .csv。panel 数字本身不受影响, 但"可复现"声称在模板层当前不成立。
4. **历史教训第三次重演**: 证伪层又产生 4 条过度击杀 (事实坐实却被程序性误杀), 全部由 critic + 主控终裁改判恢复。自动层永远需要主控终裁。


---

## 1. 修复核验 (fixChecks, 39 项)

| 组 | 结果 |
|---|---|
| fix-citations (9 引文) | 7 verified / **2 partial** |
| fix-panel-values (8 值修复) | 8 verified (盘上实证: peer_tone_2nd min 0.948 无伪零 / jf∈[-1,1] / bartik 行和=1.000 / JSD∈[0,1] / 30 列 sum_wd_* 已零填 / fintech_share=ft_dedup/(ft_dedup+nf) 全行成立) |
| fix-audit-validation (4) | 4 verified |
| fix-upstream-deferred (6, golden-deferred) | 6 verified (代码语义+单测在位) |
| fix-regression-locks | 25/25 绿; **partial**: 3 个 vacuous 为 2026-06-03 既有测试被计入 25, 其中 JF Int8 项无真生产锁 (revert 仅 runtime 报错) |
| fix-golden-consistency | 4 verified (repro+dag 39 绿 / golden 列集一致 / 零填契约抽验过 / .dta 行列一致) |

**2 处 partial 的残留清单 (须补修)**:
- Berger 2022 误引残留 1 处: `pipeline/panel/export.py:959` 段头注释 (紧贴 peer_fintech_exposure_lag1 标签)。
- difflib≠TNIC 误标残留 3 处: `export.py:966`、`papers/llm_peer/paper_spec.yaml:49`、**`papers/llm_peer/figures.py:41` (出版图 Figure 1 坐标轴标签, 最高风险)**。
- 同族延伸 (Wave-2 确认): z_score "CAR 变体≠Laeven-Levine" 更正仅落 bank_news_clarity spec 一处, **姊妹 13 处仍直引 L&L 2009** (bank_media_disagreement spec:58 / 两 11_table2 模板含 esttab 表注 / 两 tables.py / 两 replication README)。

---

## 2. P1 确认清单 (22 条)


- **5 个 IDF 词典标签泄漏进 'BERT' 组: 三角验证全链 (Cronbach α/跨方法一致率/覆盖率稳健性/人工抽样分层) 被结构性污染**
  - 位置: `validation/tone_validation.py`:155-175 (discover_sentiment_columns BERT 检测块, 排除检查 L161) · 单元: validation-tone-llm
  - 要点: BERT 检测仅排除 result['words'] 与 llm 名, 未排除 result['words_idf'] → jiang_2021_idf 等 5 个 IDF 词典的 *_label_full 列被当作 'BERT 模型', 且因存在 {name}_zscore_full 列 probs 非空而进入 all_scores (label_to_numeric)。模块 3.1b 注释自己声明 'IDF 与等权是同源数据的不同加权…混入同一 Cronbach α 会虚假膨胀, 因此单独报告', 但该泄漏使其直接进入 BERT 组与全部跨方法统计。

- **FIX-REGRESSION: stata_audit 3e MW加权恒等式仍用物理分母, 在 valid-mask 修复后的重生面板上必然误 FAIL (实证 14/117 行, max diff=0.5)**
  - 位置: `pipeline/audit/stata_audit.py`:399-426 (audit_sentiment_consistency 3e) · 单元: pipeline-audit-family
  - 要点: 2026-06-10 已落地的 VW/MW/HW valid-mask 权重修复 (encode.py:1453-1462, LLM 族分母改 sum_wd_{wtag}_llm_{track}) 未同步到 stata_audit 的加权恒等式检验: 3e 仍按 expected = llm_vote_score_mw_sum_full / sum_media_authority_weight (物理分母) 重算并与 llm_vote_tone_mw_full (valid-mask 分母) 比对, 任何含 LLM-invalid 文章的 bank-year 都 diff>1e-8 → record FAIL → main() 返回退出码 1。

- **重复字符压缩正则吞掉数字量级: 1000亿→100亿、2000年→200年、股票代码600000→600, 全语料已被不可逆破坏**
  - 位置: `pipeline/preprocess/normalize.py:53-54,109 + pipeline/preprocess/_constants.py:190-194`:TAIL_CLEANUP_PATTERN / _tail_cleanup_repl · 单元: preprocess
  - 要点: TAIL_CLEANUP_PATTERN 第一支 `(.)\1{2,}` 对任意字符(含数字)的 ≥3 连续重复一律压缩为 2 个 (`return m.group(1) * 2`), 注释自称'尾部清理'实际作用于全文。金融新闻中圆整金额/年份/指数/股票代码大量含 ≥3 连零, 全部被改写为错误数值。

- **finbert2 全程使用 finbert_cn 的 tokenizer 推理 — 共享分词组仅按 max_length 分组, 无词表一致性校验**
  - 位置: `pipeline/sentiment/tone_berts.py`:389-390 (分组), 437-454 (representative tokenizer), 479-497 (共享窗口), 514-524 (逐模型复用) · 单元: tone-berts
  - 裁决: 亲验坐实且比声称更严重: tone_berts.py:389-390 仅按 max_length 分组, L448/L514 整组复用 finbert_cn token id。实测 finbert2 基础词表 21128 条中 20785 条与 bert-base-chinese 不一致(整体错位1位: 银7214→7213), 喂入的每个 id 解析为另一个字=乱码输入; 13809 词级 added_tokens 从未被用。盘上 23_bert_tone.parquet finbert2 双轨列即此路径产出(815/857 判正), live 非 latent。

- **cn2arab 单字/成语级中文数字误转把功能词洪泛进 num_intensity 分子 (实测占分子 42%, 影响 94.5% 文章; 文件内披露的 "≈1%" 低估约两个数量级)**
  - 位置: `pipeline/sentiment/numerical_intensity.py`:66-68 (_CN_NUMBER_BLOCK_RE), 174-187 (_replace_block), 246-251 (错误的影响量化) · 单元: fls-lexical-numint
  - 裁决: 亲测复现: '进一步'→'进1步'/'十九大'→'19大'/'十三五'→'15'; 全语料分子 19148/45215=42.3% 来自转换, 单'一'块 11366 (25.1%), 1106/1170=94.5% 文章命中。numerical_intensity.py:66-68 无边界约束, L179-181 仅守'第'; L250-251 仍声称影响≈1%且 deferred v3.7.5, v3.8.0 未修。不在台账, 分子构念污染+披露失真坐实。

- **semantic staleness 窗口含同日行 → 同 docid 跨行复制行机械得 1.0, 污染面板 semantic_* 列 (与 surface 轨窗口不对称)**
  - 位置: `pipeline/text/article_staleness.py`:234-248 (semantic) vs 156-161 (surface) · 单元: staleness-sbert-embed
  - 裁决: 亲验坐实。article_staleness.py:158-159 surface 窗口严格 `day < d` 排今日; semantic L237-246 仅剔 `< cutoff`, index.add 含同日更早行。盘上实证: 155/155 同日 later-dup 行 sem_full≥0.999, 非dup均值0.790; panel semantic_highstale_full=0.1492 (surface=0.0), 282条high-stale中155条纯dup artifact; 经 runner.py:1717 直达回归。

- **同行嵌套变体重叠双计数: 一次物理提及全称被计为 2 次, 污染分类门槛与 VW 权重**
  - 位置: `core/text/ahocorasick.py`:326-347, 374-396 (analyze_bank_matches) · 单元: ctx-materializer-coretext
  - 裁决: 亲跑复现: 2次物理'中国工商银行'→total=4且is_bank_news=True(门槛3被击穿); bank_names.json实测1771对同行嵌套对。ahocorasick.py:326-347/374-396无任何位置去重, L50注释承诺的最长匹配从未兑现(同库canonicalization.py:252-264有正确范式却未用于此)。计数直入news_bank.py:236-237 mention_count/density→runner.py:259 VW权重, 按银行系统性异质膨胀(max 2x), 同时偏置样本选择与VW加权。

- **同行嵌套名称变体无位置去重→一次物理提及被多重计数, 通胀 mention_density/VW权重并降低有效入样门槛**
  - 位置: `core/text/ahocorasick.py (analyze_bank_matches L326-360, L396-418) + pipeline/filtering/news_bank.py:236-237`:ahocorasick.py:326-360 · 单元: news-bank-fintech-salience
  - 裁决: 亲跑复现: 2次物理提及'中国光大银行'→total_count=4; 1正文+1标题→total_with_title=4≥3即入样(声称阈值3被实质减半)。ahocorasick.py:326-360无位置去重, L49注释承诺'下游识别最长匹配'从未实现; news_bank.py:236-237直接用total_count喂mention_density/VW。1771对嵌套变体, 偏差按银行命名结构系统分化('中国X银行'族全部翻倍)。非台账项。

- **t2v 稳健轨嵌入被本地模型静默截断到 128 token — strat_*_t2v / centroid_diff_emb_t2v / coh_emb_t2v / 契约列 strat_diff_t2v_{full,ctx} 实际度量"文档前缀相似度"**
  - 位置: `pipeline/features/strategic_diff.py`:194-196, 634-652 (+ pipeline/text/embedding_engine.py:113-128, 300-362) · 单元: strategic-diff-panel
  - 裁决: 亲验: HF缓存sentence_bert_config.json实测max_seq_length=128; embedding_engine.py:113-128 encode_local无max_seq适配, :332-333将8191-token块直送。盘上复现: 广东南粤/杭州2017两文档前300字相同全文不同, strat_sim_max_emb_t2v双双=1.000000。docstring L126对t2v轨为假。与台账⑧(L2归一)不同缺陷。

- **7h-token 政策对齐面板族在 pre-LLM-verification 文章全集上聚合, 与全仓其余面板测度的 verified 聚合域结构性不一致**
  - 位置: `pipeline/panel/runner.py (消费 pipeline/filtering/policy_alignment.py 输出)`:1194-1320 (df_align 读 15_article_alignment.parquet; _agg L1228; 分位阈值 L1288-1293; 四象限聚合 L1307-1319) · 单元: policy-alignment-similarity
  - 裁决: runner.py:1194/1228/1307 聚合 df_align(1170 未验证行), 其余族用 24_herd_decay 857 verified 行(runner.py:212-219; tone_llms.py:1893-1895)。盘上实证: 孪生对 118 共同行 60 个不同, max|Δ|=0.437, corr=0.941, 4 个 phantom bank-year 复现。不在台账, 进主回归, P1 成立。

- **Bartik 基期敏感性变体 _t01 是幻影: share 从未池化 (≡_t0), 且 shift 被截断到基期两年, 其余年份 IV 被 fillna(0) 制成精确伪零 (latent at T=19)**
  - 位置: `pipeline/panel/runner.py`:696-706 (协同 pipeline/panel/iv_did.py:128, 201-204, 253-256) · 单元: panel-runner-merge
  - 裁决: 亲验属实。runner.py:696-698 传年份子集但 iv_did.py:128 仍 year==T0 取 share→池化从未发生, golden 实证 _t01 哈希 46dc4562 与 _t0/main 字节级同(_t1 不同)→幻影盘上已激活; T=19 时 shift 域截到{T0,T0+1}, 余年 shift NaN 经 iv_did.py:256 fillna(0)→IV 精确 0.0(伪零部分 latent)。伪稳健性检验+IV 伪零, P1 成立。

- **共现网络边权口径不连贯: 在 verification 过滤后的展开帧上逐行双向计数, 边权为 1x/2x 任意混合且含 verification-拒绝的 phantom 边**
  - 位置: `pipeline/panel/network_spillover.py`:139-157 (build_adjacency_matrix), 文档声称 L36-38/L107-109 · 单元: network-spillover
  - 裁决: 实证复现: tone_llms.py:1893-1895 union 过滤(1170→857)后, network_spillover.py:139-157 逐 twin 行计数→2017 年 87 边中 44 奇数(50.6%)、31 phantom(both-verified 口径下不存在); 42 个被引 twin 键在 d12 在场 d24 缺失; peer_tone_lag1_full 2018 的 32 观测中 5 个仅靠 phantom 边存在, 共同观测最大偏移 0.0344≈1.1×SD(0.0312)。docstring L107-109 '每篇文章+1' 与实现(双 twin 存活计 2)不符; 同矩阵还喂 22 中心度(L455)。非台账项。

- **缺失基期暴露被零填为伪零 Bartik IV (share fillna(0) → IV=0 而非 NaN)**
  - 位置: `pipeline/panel/iv_did.py`:L148-150, L180-181, L312-313, L318 (BIV 求和 L256/L379) · 单元: iv-did
  - 裁决: 亲验属实: iv_did.py:148-150 基期无文章银行被 continue 跳过, L181/L313/L318 fillna(0) 致 share 和=0、IV 恰为 0.0。盘上 7 族各 30/174 行 (media 70/174) IV==0 且 NaN=0; 这 15 家 2017 年 n_articles==0 但 2018 行有效出表。合法 IV 均值 0.944/0.956, 伪零是 12σ/50σ 离群, 直接污染一阶段。非台账重复 (bartik 已修项是 'other' 分母, fillna 已修项是 peer_tone 网络模块)。

- **σ(ROA) 滚动窗与 NPL formation lag-1 均为位置语义, 缺年份连续性守卫 — gap year 下产出错误值而非 NaN (latent)**
  - 位置: `pipeline/panel/risk_taking_outcomes.py`:158-170 (compute_sigma_roa_rolling), 202-219 (compute_npl_formation shift(1)) · 单元: risk-taking · ⚠latent
  - 裁决: risk_taking_outcomes.py:166-169 rolling(5) 行位置窗、:203-204 shift(1) 行位置滞后, 全模块无 reindex 年网格/year-diff 校验; docstring L26/L31 明写日历语义。实测年份[2007,08,12,13,14]: 2012 npl_formation=0.16364(误用2008作lag), σ第4行即出值跨7日历年。dry_run 仅单季 placeholder, full 加载器未实现 — T=19 缺年下静默产错 DV 值, 坐实 latent P1。

- **Placebo DID 伪处理窗口包含真实处理后期间 — placebo 检验机械性显著, 必假阳性 (latent, 当前未接线)**
  - 位置: `pipeline/falsification/controls.py`:1024-1058 (generate_placebo_did_variables) · 单元: falsification-controls · ⚠latent
  - 裁决: controls.py:1033-1037 placebo_post=1{year>=ty-k} 无 year<ty 上界, 是真 post 严格超集; L997/L1055 建议回归不控真 DID 不限前期 → 真效应存在则 placebo 必显著, L1057-1058 解读错误否定平行趋势。grep 证实零生产调用 (死代码), 但列入全量 REINSTATE, 接线前必修。Hassan QJE Table 7 非时点 placebo, 引文错配属实。

- **银行名称长短变体嵌套双重计数: 1 次物理提及被计 2 次, mention_density(VW权重)与判定阈值系统性失真**
  - 位置: `core/text/ahocorasick.py (analyze_bank_matches L326-407) + pipeline/filtering/news_bank.py:236-237 + config/bank_names.json`:326-407 · 单元: sweep-chinese-text
  - 裁决: 实证复现: 3 次'中国工商银行'→total_count=6 (ahocorasick.py:326-360 每 (end_pos,variant) +1 无最长匹配消解, L49-50 docstring 承诺未实现); 2 次物理提及即过 min=3 (实测 total=4, is_bank_news=True); 词典实测 1771 对同行嵌套。下游 news_bank.py:236-237 mention_density + panel/runner.py:255-259 VW 加权直接吃入膨胀计数, 全称写法文章 ~2x 失真且与文体相关 — 分类阈值+VW 权重双失真, P1 成立。

- **num_intensity 分子: 单字中文数字块误转 — '进一步/一起/统一/之一' 全被计为数字 token, 实测占分子 44%**
  - 位置: `pipeline/sentiment/numerical_intensity.py (_CN_NUMBER_BLOCK_RE L66-68, _cn2arab L175-187, _count_numerical_tokens L206-226)`:66-68, 175-187 · 单元: sweep-chinese-text
  - 裁决: 实证复现: _cn2arab('进一步')='进1步'、'万一'→'10001' (numerical_intensity.py:66-68 块正则含孤立'一', L177-180 仅排'第'前缀)。盘上 300 篇 content_full 实测单字块占分子 43.8% (top: 进一步×199/一带一路/一是二是三是), 与声称 44% 吻合; L247-251 known-issue 仅承认 ~1%, 失真 ~40 倍。影响 num_intensity_{full,ctx} + word 版共 4 列, 台账'valid分母'修复是聚合权重与此无关, 非重复。P1 成立。

- **N4-EXTENSION: 4 个原始衍生论文复现包 MAIN_DV='ROA' 全幻影 (+benefit CAR/is_listed), 包内主回归链 0 条可跑**
  - 位置: `papers/_common/derivative_replication.py`:75, 113, 132, 151 (MAIN_DV='ROA'); 94 (ROBUSTNESS_DV='CAR'); 78 (HET_VAR='is_listed') · 单元: papers-derivative
  - 裁决: derivative_replication.py:75/113/132/151 MAIN_DV='ROA'、:94 CAR、:78 is_listed; 实读 parquet+.dta(1658列)零命中。四篇 01_data_prep foreach 含 {{MAIN_DV}} 且 exit 198 (brokerage:36-42 等) → 包内全表死亡。台账 N4 仅覆盖 P2-P5, 非重复。

- **benefit_society Table 6 esttab 'se ci' 互斥选项必崩 r(198), 非 capture 调用使 00_master 中途中止**
  - 位置: `papers/_common/stata_templates/benefit_society/15_table6_effect_size.do.tmpl`:42 · 单元: stata-templates-papers-b
  - 裁决: 15_table6:42 实有 `se ci`; esttab.ado:588-594 实证 aux sizeof>1→exit 198; 01_data_prep xtset 已存盘故前面 L1. 不先崩; 00_master:32 裸 do→在此硬停, 16/17/17b/18/20/21/30/31 全不执行。全模板 grep 仅此一处。

- **P3/P5 data-prep 把 article-level 分类列名当 bank-year panel 必备变量 → 复现包永久 exit 198, R35-M02 修复未传播 (FIX-REGRESSION)**
  - 位置: `papers/_common/stata_templates/bank_fintech_substance/01_data_prep.do.tmpl`:25-31 · 单元: stata-templates-papers-a
  - 裁决: 亲验: substance/01:25+derivative_replication.py:185 要求 innovation_substantiveness_full, collab/01:25 硬编码 innovation_collab_mode_full; 实读 panel 两名 MISS, encode.py:1135 证其仅为 article-level (panel 只产 sub_frac/collab_frac 等, 全 OK); master:25/26 `do 01` 未 capture → exit 198 杀全包。locus/01:24-43 注释自证同 bug 已修仅 P4。结构性死锁超 N4 enrichment 范畴, 非重复。

- **P3 短期 outcome 变量名 36 字符 > Stata 32 字符硬限 → W&Z 1994 双 outcome 核心检验结构性不可达 (latent)**
  - 位置: `papers/_common/stata_templates/bank_fintech_substance/16_substance_mechanism.do.tmpl`:34-59 · 单元: stata-templates-papers-a · ⚠latent
  - 裁决: 亲验 len=36; stata_export.py:38 MAXLEN=32, :388-396 缩写表无匹配→截断为 car_3day_window_fintech_announce; 全名承诺链 paper_spec.yaml:29/pipeline_v34_rerun.yaml:147/tables.py:32 坐实; 引用站点 substance/01:34, 15:60-67, 16:34-57, 19:36-56 全用 36 字符名; 16:59 esttab short_run 无条件→r(111) Table 3 永丢。盘上列本就缺 (enrichment pending) 故 latent, 但 enrichment 后仍永久不可达。

- **papers 10/11 主回归模板绕过 working dataset: 主 treatment+全部控制在管道可产出的任何数据源中均不存在, M1 起 r(111); 唯一可跑的盘上数据是仓库外手工拼装 fixture**
  - 位置: `papers/bank_media_disagreement/stata_templates/11_table2_main_disagreement_risk.do.tmpl`:22-58 (同病: bank_media_disagreement/13_table4:13-27; bank_news_clarity/11_table2:25-58; bank_news_clarity/13_table4:14-45) · 单元: stata-templates-mainline
  - 裁决: 实证: 49.parquet=13列0行; risk_taking_outcomes.py:76-89/470 只写13列.dta; 11_table2:22-40 use 49.dta 回归 TX+7控制全缺→M1 r(111); grep 证 _paper10/11_working 仅 save 无消费; credit_rating/listed 连 fixture(24列) 与 40_panel(1658列) 均无→clarity M4/Panel B(13_table4:42-45) fixture 上也崩。


> **P1 去重说明**: 嵌套变体重复计数在 3 个单元独立发现 (ctx-materializer / news-bank / sweep-chinese-text), num_intensity cn2arab 在 2 个单元独立发现, Bartik fillna 伪零在 3 个单元独立发现 — 上表保留各自证据但**实质独立缺陷约 15 个 panel/测度层 + 5 个复现包/模板层**。

### 主控亲验记录 (终裁层)
以下 P1 经主控逐行读码/盘上实测二次确认: ① normalize `(.)\1{2,}` 数字破坏+phone 正则无锚 (亲读 normalize.py:53-58,109 + _constants.py:153,190-194); ② stata_audit 3e 物理分母 (亲读 :398-426); ③ words_idf 泄入 BERT 族 (亲读 tone_validation.py:115-175); ④ derivative_replication 幻影列 (盘上 1658 列实测 10/10 MISSING); ⑤ finbert2 共享 tokenizer (亲读 tone_berts.py:438-454 分组逻辑)。

---

## 3. P2 确认清单 — 活跃 (117 条)


- **KNOWN-OPEN-STATUS: ⑤ codebook 质量缺陷全部仍在, 且 2026-06-10 修复后陈旧度恶化 (未登记列 24→54, 58 个统计量已失真)**
  - 位置: `data/processed/variable_codebook.{json,csv,md,xlsx} + pipeline/panel/codebook.py`:产物时间戳 2026-06-06 12:28 vs panel 重生 2026-06-10 10:15 · 单元: codebook
  - 要点: 实测现状: (a) 占位描述 1517/1613=94.0%, 空学术引用 1519/1613=94.2% — 未动; (b) year 取值范围仍标 [2013,2023], 实际盘上 2017–2018 (全量 2007–2025 也不符); (c) 幻影行仍 9 个 (nf_n_articles/nf_media_breadth/nf_headline_frac/nf_ln_coverage/all_n_articles/all_ln_coverage/fintech_share/ln_ft_articles/ln_nf_articles, 相对 40_panel_yearly); (d) 未登记列由已知 24 恶化到 54 — 06-10 修复自己新增的 30 个 sum_wd_{vw,mw,hw}_* valid-mask 权重列 + 12

- **主线核心变量 llm_vote_tone 的 codebook 备注虚构 LLM 集成: 声称 'GPT-5-nano、Gemini-3、Grok-4.1', 实际第三模型是 DeepSeek-V4-Flash (全仓无任何 Grok)**
  - 位置: `pipeline/panel/codebook.py`:305, 322 (metadata['llm_vote_tone_full'/'llm_vote_tone_ctx'].notes) · 单元: codebook
  - 要点: curated 条目 notes='使用GPT-5-nano、Gemini-3、Grok-4.1三个模型的多数投票结果' 与真实投票集成不符: config/sentiment.yaml:29-43 锁定 gpt-5.4-nano (OpenAI) / gemini-3.1-flash-lite (Google) / deepseek-v4-flash (DeepSeek 直连); encode.py:54-56 注释同。'Grok-4.1' 在全仓代码/配置/审计报告中零出现 (历史第三模型曾名 claude4h, 后正名 deepseekv4, 从未是 Grok)。该错误已写入盘上 4 种格式产物。

- **entity_masking ctx 轨掩码 prompt 标题双重注入, 与生产 baseline prompt 构造不一致 → 掩码一致性指标被格式变更混杂**
  - 位置: `validation/entity_masking.py`:619-633 (ctx 掩码) + 256-263 (prompt 构造); 对照 pipeline/sentiment/tone_llms.py:608-613 · 单元: validation-robustness
  - 要点: 生产 stage 21 的 ctx 轨 prompt 经 fix(tonellms-01) 用 _strip_prepended_title 剥离 content_ctx 的标题前缀, 保证标题仅经 {title} 字段注入 1 次; entity_masking 的 ctx 轨直接对盘上 content_ctx (=标题+实体窗口) 整体掩码后填入 {content}, 同时 {title} 又填 masked_title → 掩码后 ctx prompt 标题出现 2 次, 而 baseline (生产缓存) 判定时只出现 1 次。掩码前后判定差异因此混杂了 '实体匿名化' 与 'prompt 结构变化' 两个处理, ctx 轨的 verification/sentiment 一致率与 Cohen κ 不再是纯掩码效应; full 轨 (mask

- **dedup_threshold 在已按 0.80 去重的下游数据上扫描 0.85/0.90 → 高阈值方向机械性 ~100% 保留, 稳健性单侧截尾且 docstring 论证自相矛盾**
  - 位置: `validation/dedup_threshold.py`:89-98 (输入选择论证) + 121 (thresholds) + 138-154 · 单元: validation-robustness
  - 要点: 敏感性输入 21_tone_llms.parquet 是 00→11→12→21 链路产物, 而 stage 00 内部已按生产阈值 jaccard_similarity_threshold=0.80 完成 MinHash 近似去重 (config/preprocessing.yaml:161) — 所有相似度>=0.80 的对已被移除。因此对该数据再跑 0.85/0.90 (更宽松, 要求更高相似度才算重复) 找到的新重复对 ⊂ 已删集合, Dropped≈0、Retained_Ratio≈100% 是机械结果而非稳健性证据; 只有 0.75 (更严) 一侧有信息量。代码注释 L91-93 恰以 '00_preprocessing.parquet 已在生产阈值下完成去重, 在其上重复运行会低估阈值变化的真实影响 (方法论偏误)' 为由改用 21 的

- **dict_coverage 分析 3 '死词/有效覆盖率' 在 fintech 判定通过的子样本上计算, 却声称 '在全部语料中从未出现过' → 选择性样本上的覆盖审计**
  - 位置: `validation/dict_coverage.py`:401-491 (analysis_3_keyword_concentration, 输入 df_llm) + 482 (声称) + 833-835 (清理建议) · 单元: validation-robustness
  - 要点: 关键词频率/零命中统计仅遍历 21_tone_llms_full.parquet 的 fintech_keyword_details — 即已通过 distinct>=T=3 阈值的文章 (盘上实证 1170 行全部 distinct∈[3,44], 无 <3 行)。一个关键词若只在灰色地带 (1<=distinct<T) 或被拒绝的银行新闻中出现, 会被计为 '零命中死词', 而日志明确声称这些词 '在全部语料中从未出现过' (L482), 综合结论据此给出 '清理词典: 移除零命中死词' 建议 (L835)。这是在阈值选择后的样本上审计词典覆盖 — 恰是该审计要诊断的选择机制本身, 系统性高估死词数、高估 HHI 集中度 (高频词在通过样本中过代表)。

- **LLM 多数投票聚合列 'llm' 被当作第 4 个独立模型计入 Cronbach α/一致率/共识合成 (LLM α 0.70 阈值结论翻转)**
  - 位置: `validation/tone_validation.py`:1640-1650 (LLM score/label 收集) + 1743-1752 (Step 3.3) · 单元: validation-tone-llm
  - 要点: discover 的 llm 组含聚合投票列 short_name='llm' (llm_sentiment_full = 3 模型多数票)。诊断函数 diagnose_llm_category_bias/calibration 显式过滤 name!='llm', 但 _run_validation_for_track 构建 all_scores/all_labels (L1640-1650)、Step 3.3 LLM 内部一致性 α、Step 4.2 method_agg['LLM'] 均值、Step 4.3 标签一致率、Step 5.1 majority_vote 合成均未过滤 — 把成员模型的合成结果当独立测量, 经典 α 理论下机械抬高一致性。

- **latent: 情感评估 fillna('中性') 把无预测行 (含 100% 未通过验证文章) 伪造成中性预测, 人工标注完成后将结构性扭曲论文 Panel B 准确率**
  - 位置: `validation/llms_evaluation.py`:1390-1391 (LLM 双轨), 1429-1430 (逐模型) · 单元: validation-tone-llm
  - 要点: y_pred = df[sen_col].fillna('中性') 且 np.where(isin(labels), y_pred, '中性'): 模型未输出情感的行 (NaN) 与解析失败行被静默替换为'中性'预测参与 accuracy/macro-F1/混淆矩阵, 而非从评估域剔除。情感评估域 df_eval_sen 仅按人工金标准 notna 过滤, 不条件于 llm_verified — 把'相关性筛选拒绝'与'情感判断错误'混为一谈。

- **ECE 校准用含被评模型自身的 3 模型多数票作 ground truth (leave-one-in 循环), 且人工金标准路径为死代码**
  - 位置: `validation/tone_validation.py`:1271-1286 (gt 选择), 1309-1346 (ECE 主循环) · 单元: validation-tone-llm
  - 要点: gt_col 回退到 llm_sentiment{track} (3 模型共识) 评估每个成员模型的 per-bin accuracy: 被评模型自己是 3 票之一, 仅当另两模型互相一致且都反对它时才判'错' — accuracy 机械抬高, ECE 对过自信模型系统性低估。优先路径 human_sentiment{track} 在全部 parquet 中不存在 (无任何 stage 回写), 即人工金标准分支永不触发。

- **FIX-REGRESSION: 降级审计 F3 修复不完整 — demo_mode 仍把合成指标写入无任何标记的 publication-ready LaTeX/CSV (盘上现行即此状态)**
  - 位置: `validation/llms_evaluation.py`:1633-1637 (F3 gate 仅盖日志) vs 404-558 (generate_latex_table 无 demo 标记) + 1512-1560 (JSON/CSV 输出) · 单元: validation-tone-llm
  - 要点: F3 修复 (degradation 2026-06-09) 只在 demo_mode 下抑制了'论文建议表述'日志, 但 classification_eval_table.tex、classification_eval_summary.csv、per_model_*_comparison.csv、cm_*.png 仍以与真实运行完全相同的文件名/格式写出合成数据, caption/表体/文件名零 demo 标记 — 唯一标记埋在 JSON 的 demo_mode 字段。

- **latent: merge_annotations 的待仲裁哨兵值 (-1/'待仲裁') 会作为伪金标准类别泄入 stage 33 全部分类指标**
  - 位置: `validation/llms_evaluation.py`:1192 (has_gold_ver=notna), 1287 (astype(int)), 1380 (has_gold_sen) + llms_human.py:227-229,257-259 (哨兵写入) · 单元: validation-tone-llm
  - 要点: llms_human.merge_annotations 把编码者分歧行写成 最终_验证=-1、最终_情感='待仲裁' (明示'待仲裁标记')。llms_evaluation 金标准提取仅 notna() (验证) / notna & !='' (情感), 不排除哨兵 → gold=-1 行进入 accuracy 分母且任何 0/1 预测必判错、对 labels=[0,1] 的 precision 构成虚假 FP; gold='待仲裁' 行同理拖低中性类 precision 与 accuracy。诊断函数 _gold 比较 ==0/==1 恰好排除 -1, 与主指标口径不一致。

- **Tables 2-5 esttab CSV 桥全链死接线: python 层读 *.csv, 全部 Stata 模板只写 *.tex**
  - 位置: `papers/bank_fintech_attention/tables.py (同 substance/locus/collab/tone 系)`:attention:70/78/84/91; substance:63/71/77/83; locus:63/71/77/83; collab:57 · 单元: papers-mainline
  - 要点: 五篇主线论文的 build_table2..5 全部经 read_paper_esttab 读取 papers_assets/<id>/output/tables/table2_main.csv 等 CSV 文件, 但 grep 全部 95 个 .do.tmpl 证实没有任何模板产出 .csv — 所有 esttab 一律 `using "$tables_dir/table2_main.tex"` (如 15_attention_main_regression.do.tmpl:87, 16_substance_mechanism.do.tmpl:59)。即使完整跑通 Stata 复现包, 这些函数也永远 FileNotFoundError; docstring 声称 '(filled at M5/M6)' 永不兑现。依赖同一解析器的 paper_fi

- **P3/P4/P5 figures 读取幻影列 → ArrowInvalid 击穿 analysis CLI (attention-01 修复未扩散)**
  - 位置: `papers/bank_fintech_substance/analysis.py (+locus/collab 同型)`:substance analysis.py:51 & figures.py:26-28; locus analysis.py:51 & figures.py:26-28; collab analysis.py:59 & figures.py:33-35 · 单元: papers-mainline
  - 要点: substance/locus/collab 三篇的 Figure 1 经 load_panel(columns=[...]) 读取 40_panel_yearly.parquet 中不存在的列 (innovation_substantiveness_full / locus_layer_full+locus_scenario_full / innovation_collab_mode_full), pyarrow 抛 ArrowInvalid; 但三篇 analysis.py 的 figures 段只 catch FileNotFoundError → CLI 整体 traceback 崩溃 (run_paper.py:167 不再包 try/except, 直接传播)。metric-audit 2026-06-02 的 attention_med

- **P3/P4/P5 Table 1 变量清单 100% 幻影 → 产出全 NaN 描述统计表; 多列在面板层永不可能物化**
  - 位置: `papers/bank_fintech_substance/tables.py (+locus/collab)`:substance:25-43; locus:25-43; collab:22-33 · 单元: papers-mainline
  - 要点: 实测 build_table1: substance 13/13 行、locus 13/13 行、collab 10/10 行 Mean/SD/N 全 NaN (attention 也有 10/14 行 NaN)。根因分两类: (a) 金融 enrichment 列 (ln_assets/car_*/r_and_d_intensity 等) 待 M0.5.11 落盘, 属已知待办; (b) 但 treatment 列是结构性错名 — innovation_substantiveness_full / innovation_collab_mode_full 只存在于文章级 parquet 且是中文字符串标签 ('实质性'823/'象征性'31; '自主研发'/'外部协同'), 永远不会以该名出现在 bank-year 面板; locus_layer_f

- **stata_audit 3e VW/HW 恒等式检查因列名陈旧静默死亡 — 审计声称覆盖 VW/MW/HW 三项, 实际只有 MW 在运行且无任何缺席记录**
  - 位置: `pipeline/audit/stata_audit.py`:401-426 · 单元: pipeline-audit-family
  - 要点: VW 检验期望的分子列 `llm_vote_score_vw_sum_full` 在当前 schema 不存在 (真名是 llm_vote_score_w_sum_full, encode.py:1466); HW 检验期望的分母列 `sum_herd_weight` 自 v3.6.0 双轨化后已不存在 (真名 sum_herd_weight_full/_ctx)。两检查走 if 条件失败分支, 而 else 兜底仅在 `tone_col not in p.columns` 时报 WARN — tone 列存在 → 零记录输出, 审计报告里 VW/HW 恒等式凭空消失且无人察觉。

- **39f 事件窗 ±3d 不合并重叠事件 → 同一文章跨事件重复计入 bank-year 加权 (盘上 32/81 相邻事件对窗口重叠)**
  - 位置: `pipeline/audit/cross_media_alpha.py`:78-107 (detect_bank_events) + 213-239 (aggregate_to_bank_year) · 单元: pipeline-audit-family
  - 要点: detect_bank_events 把每个 ≥p90 的 bank-day 各自当独立事件, 不合并相邻事件; 持续多日的同一新闻冲击会产生多个 ±3d 互相重叠的窗口, 同一批文章被重复纳入多个事件的 variance/α 计算, 再经 aggregate_to_bank_year 按事件加权平均 → 持续性 spike 被系统性超权, n_events 高估独立事件数。附带: 模块 docstring 第 26 行承诺 bank-year 聚合 '按 event 内文章数加权', 实现 (line 220 `df['_w'] = df['n_outlets']`) 按 outlet 数加权, 口径与设计契约不符。

- **llm_contamination_test verdict 用带符号 r 比较而非 |r| — 负向 LLM-outcome 关系下真污染被误判为 reverse_pattern_anomaly (latent)**
  - 位置: `pipeline/audit/llm_contamination_test.py`:286-293 (contamination_test verdict) · 单元: pipeline-audit-family
  - 要点: 设计构念 (docstring L17) 是污染使 pre-cutoff 相关性'异常高'即 |r_pre|>|r_post| (记忆强化关系强度, 与符号无关), 但实现判定 `p_value < 0.05 and r_pre > r_post → contamination_detected`。当 LLM 输出与 outcome 真实关系为负 (如负面语调 vs 风险类 outcome) 时, 污染使 r_pre 更负 → r_pre < r_post → 被贴 'reverse_pattern_anomaly' 标签而非 'contamination_detected', DC4 检验对负向关系族系统性误分类。

- **llm_contamination_test 年中点规约把跨 cutoff 之年整体划入 post-cutoff 留出集 — 留出样本被 pre-cutoff 文章污染, 全量语料下检验结构性失效 (latent)**
  - 位置: `pipeline/audit/llm_contamination_test.py`:371-375 (run_stage) / 421-425 (main): df['_test_date'] = year + '-07-01' · 单元: pipeline-audit-family
  - 要点: bank-year 面板用 '年-07-01' 作年代表日期再与 cutoff 比较: cutoff=2024-04-01 时, 2024 年 (含 1-3 月 LLM 可能见过的文章) 因年中点 ≥ cutoff 被整年划入 '绝对没见过' 的 post 留出集。设计原理 (docstring L13-14) 要求 post 样本严格 post-cutoff; 跨界年的混入使 r_post 同样含记忆成分 → pre/post 相关性差被衰减 → 检验偏向 'no_contamination_evidence' (恰是最危险方向)。全量语料 2007-2025 + 典型 2024 年中 cutoff 下, post 集唯一构成就是跨界年本身, 留出检验完全失去甄别力。

- **电话号码正则无边界锚定: 任意 10-12 位数字串被当电话删除, 长数字被部分截删留下错误残值 (138000000000元→0元)**
  - 位置: `pipeline/preprocess/_constants.py:153`:phone_pattern · 单元: preprocess
  - 要点: `(?:\+?86)?1[3-9]\d{9}|\d{3,4}[-\s]?\d{7,8}` 两支均无 `(?<!\d)`/`(?!\d)` 或 \b 守卫: 第二支因分隔符可选等价于匹配任意 10-12 位连续数字; 第一支匹配更长数字串中以 13-19 开头的 11 位子串, 删除后残留尾部数字拼出全新错误数值。

- **噪声词典互动计数模式族中句过删实质内容: '推荐30只银行股'→'只银行股'、'回复12条意见'→'意见'、'3/4季度'→'季度'**
  - 位置: `config/noise_patterns.json:49,52-57 (经 _constants.py:163-187 合并, normalize.py:102-103 应用)`:pagination / like_count / comment_count / share_count / count_suffix · 单元: preprocess
  - 要点: view_count/like_count/comment_count/share_count/pagination 等模式设计目标是删网页互动计数, 但无锚定地匹配 '(推荐|赞|回复|评论|分享|转发)\s*[：:]?\s*\d+' 与 '\d+\s*/\s*\d+' 等, 在报纸正文 (本语料媒体类型=报纸, 根本没有网页互动计数) 中命中的是实质性陈述。

- **增量缓存键不含 normalization 配置段、noise_patterns/bank_keywords 资源内容与代码版本 — 注释自称已覆盖, 实未覆盖; 盘上已现混规则语料实证**
  - 位置: `pipeline/preprocess/runner.py:127-166`:_compute_config_hash / 缓存有效性判断 · 单元: preprocess
  - 要点: 缓存键 = compute_config_hash(PARAMS), 而 PARAMS=CONFIG['preprocessing'] 仅含 preprocessing 段。per-file 缓存结果实际还依赖: ① `normalization` 段 (opencc_config/html_removal_length_threshold, 是独立顶层段, 见 preprocessing.yaml:153-155); ② noise_patterns.json 与 bank_keywords.json 的文件内容 (路径在 paths 段, 内容更不在哈希); ③ 清洗代码本身的版本。runner.py:129-131 注释声称 plan m4 修复已把 'noise_patterns_file / media_weights_file / nor

- **主键 target_bank 的 codebook 声称 '42家商业银行', 实际 panel 87 家 — 产物同一行内 唯一值数=87 自相矛盾**
  - 位置: `pipeline/panel/codebook.py` · 单元: codebook
  - 主控终裁: 事实亲验为真(盘上87家 vs codebook.py:136 硬编码42家), 证伪层duplicate-of-known映射经查台账零命中, 属过度证伪, 改判 confirmed P3

- **KNOWN-OPEN-STATUS: ⑤ codebook 质量缺陷现状 — 已恶化: 未登记列 24→54 (盘上四格式产物 2026-06-06 生成, 完全滞后 2026-06-10 全部指标审计修复), 9 幻影行仍在, 94.2% 空引用, year 范围错误未修**
  - 位置: `data/processed/variable_codebook.json`:全产物 (json/csv/md/xlsx, mtime 2026-06-06 12:28); 生成器 pipeline/panel/codebook.py + scripts/generate_codebook.py · 单元: codebook
  - 要点: 盘上 codebook 产物记录的是 174×1613 的旧 panel (md 头部自证), 当前 40_panel_yearly.parquet 为 174×1658 (2026-06-10 10:15 重生)。逐列对拍: (a) 54 列在 panel 中但 codebook 无任何条目 — 含 2026-06-10 VW/MW/HW valid-mask 修复新增的全部 30 个 sum_wd_* 零填契约列、12 个 prox_*km_*_ctx 地理双轨列、6 个 llm_peer_tone_iv_ctx* 、strat_fluidity_ctx/strat_fluidity_w_ctx/article_sim_mean_ctx/article_sim_std_ctx/emb_peer_tone_lag1_ctx/emb_peer_ton

- **codebook 对核心情感测度声称错误的 LLM 模型阵容: 'GPT-5-nano、Gemini-3、Grok-4.1' — 实际为 gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash, 三个名字全错且 Grok 从未在阵容中**
  - 位置: `pipeline/panel/codebook.py`:305 (llm_vote_tone_full 的 notes; 同条目写入 llm_vote_tone_ctx 族文档) · 单元: codebook
  - 要点: codebook.py:305 硬编码 notes='使用GPT-5-nano、Gemini-3、Grok-4.1三个模型的多数投票结果', 并已写入盘上产物 (JSON 实读确认)。config/sentiment.yaml:29-40 的真实阵容是 gpt-5.4-nano(gpt54nano) / gemini-3.1-flash-lite(gemini31111) / deepseek-v4-flash(deepseekv4, yaml 注释明示'从 claude4h 重命名')。'Grok-4.1' 从未出现在任何配置中; 'Gemini-3' 与 'GPT-5-nano' 版本号也不符。同文件 L344 对子集 tone 列已正确改用 encode.LLM_MODELS 动态读取, 唯独主 tone 变量的 notes 仍是陈旧硬编码。

- **core_patterns 声明的主 Bartik IV 是幻影列名 — core.dta 实际含 0 个 Bartik IV 列**
  - 位置: `pipeline/panel/stata_export.py`:293-294 (assign_core_columns) · 单元: stata-export
  - 要点: core_patterns 注释声明 '主 Bartik IV (full/ctx 2 列)' 并列入 'bartik_fintech_iv_full/ctx', 但生产代码从不产出该名: 主 Bartik 实名为 bartik_type_iv_full/ctx (runner.py:677 '主 Bartik: 银行类型'; iv_did.py:110 f'bartik_{prefix}_iv{track}'), fintech 稳健套实名为 bartik_fintech_lf_iv_*/bartik_fintech_lc_iv_* (runner.py:740-746 group_prefix='fintech_lf'/'fintech_lc')。结果: 全部 14 个 Bartik 列 (type 主 IV + t0/t1/t01 敏感性 + 

- **FIX-PARTIAL: 2. network_spillover.py ~L299 peer_fintech_exposure 锚点改为 LeSage-Pace 2009 + Lear**
  - 位置: `fix-verification` · 单元: fix-citations
  - 裁决: 亲验: network_spillover.py:309-316 勘误完整(LeSage-Pace+Leary-Roberts), 但 export.py:959 段头注释仍写 '(Berger et al. 2022)' 紧贴 peer_fintech_exposure_lag1 标签(L960), 同构念误引残留。encode.py:560 Berger Kim & Ma 2024 是另一篇合法引文非残留。'清除误引'声称仓级不成立, 与原 P2 同类。

- **FIX-PARTIAL: 4. llm_peer_iv.py ~L691 与 ~L755 两处 difflib cutoff 澄清为串匹配严格度, 无 TNIC 标准误标残留**
  - 位置: `fix-verification` · 单元: fix-citations
  - 裁决: 亲验: llm_peer_iv.py:692-695/755-756 勘误在位, L19/264/501 等 TNIC 提及均正确指 10-peer 上限。但残留 3 处把 difflib 串匹配 cutoff 误标 TNIC: export.py:966 注释 'cutoff=0.80 TNIC 标准'; paper_spec.yaml:49 'TNIC cutoff=0.75'; figures.py:41 set_xlabel('TNIC similarity cutoff $c$') 直接印入出版图 fig1, 非注释级, P2 坐实。

- **FIX-PARTIAL: (3) 抽查 ≥8 个关键测试断言体, 确认真锁定修复行为 (非 vacuous); 报告失败/vacuous 测试**
  - 位置: `fix-verification` · 单元: fix-regression-locks
  - 裁决: 补全验证: 定向跑6文件25/25绿; 抽查14断言体≥12真锁(调生产+可区分值: VW 1/3≠1/8 encode.py:1467链在位; fintech 8/13 controls.py:1223; prob 0.85≠0.283; herd [0,0,1,2]; peer_tone 0.8≠0.4)。残留小缺口: IDF仅锁机制不锁调用点tone_words.py:1302(golden-deferred期revert无锁); v3的W²/JF 3个demo体不调生产(有e2e测试+runner.py:1568运行时守卫兜底)。无失败/无实质vacuous→降P3。

- **解析失败响应被静默编码为 verified=False 拒绝票, 污染投票/一致率/连续 DV**
  - 位置: `pipeline/sentiment/tone_llms.py`:688-714 (parse_json_response) + 1064-1082 (_aggregate_track) · 单元: tone-llms-parsing
  - 裁决: 亲验: tone_llms.py:713-714 裸 except→{}, :1069/:1082 把不可解析当 False 票+verified=False, 与 call-failure :1056-1062(None不投票)不一致; docstring:696 称'模型缺席'与实现矛盾。缓存重放 8 条坐实(row153 截断内含 true 却记 False); 盘上 n_valid=3/agr=0.667 应为 2/1.0; encode.py:154 衰减+runner.py:519 HC 剔除, 活跃影响。

- **解析失败/空响应被计为 False 验证票, 违反自身'模型缺席'契约 (盘上 8 例坐实)**
  - 位置: `pipeline/sentiment/tone_llms.py`:1064-1082 (契约声明 694-696; n_failures 仅 1056-1062) · 单元: tone-llms-voting
  - 裁决: tone_llms.py:696 契约声明 {} 视为模型缺席, 但 L1069-1082 对 jd={} 仍 v_votes.append(False) 计入 n_valid_votes(L1168), n_failures 仅 raw_text None(L1056)。缓存回放精确复现 8 例 deepseekv4 解析失败, 盘上行 n_valid_votes=3 而非 2; 与 sentiment 通道(s=None 不入票)编码不一致, 叠加 call-failure 可翻转 final_v。

- **创新三维度 (substantiveness/locus/collab) 无 verified 门控 — 与 sentiment 门控结构性不对称, 未验证轨判定进 panel**
  - 位置: `pipeline/sentiment/tone_llms.py`:1100-1136 (模型级票), 1207-1244 (binary prob 无门控), 1737-1776 (文章级无 final_v gate; 对照 sentiment gate 1163-1167/1237) · 单元: tone-llms-voting
  - 裁决: 模型级 L1106-1136 入票无 `if v:` 门控, binary prob L1207-1230 不查 verified, 文章级 L1737-1776 无 final_v gate (对照 sentiment 三层门控 L1086/1205/1237)。盘上实证: 857 行输出 full 轨 15 未验证行 12 带标签+非 NaN avg_subst_prob, ctx 62/62 带 locus; encode.py:829-832/968/1097 聚合无掩码。非台账 prob_score 修复的重复(那是 sentiment 族)。

- **innovation_locus 空票回退到关键词分类器硬默认 '应用场景' — 零证据文章也获标签 (never-None), 与 subst/collab 的 None 回退不对称**
  - 位置: `pipeline/sentiment/tone_llms.py`:1703-1722 (_resolve_locus_track, empty_fallback=_kw_cat) + core/text/canonicalization.py (canonicalize_topic('')→('应用场景',0.0)) · 单元: tone-llms-voting
  - 裁决: canonicalization.py:238-239 对空 topic 硬返回 ('应用场景',0.0); L1713 empty_fallback=_kw_cat → locus 永不 None。盘上验证: null=0/857 两轨, 分布 828:29/830:27, ctx 未验证 62 行全获标签(30 个零置信)。下游 encode.py:968/1097 groupby 无 confidence 过滤而 NaN 本可被 dropna 干净处理(L960-963), 零证据默认实质污染 app_frac/tone 分组; 与 subst/collab(empty_fallback=None, 盘上 3/29 null)不对称坐实。

- **pos_ratio/neg_ratio/msent_score 基于逐篇漂移的 best-dict 选择, 非固定词典测度 (Tetlock/Garcia 构念失真)**
  - 位置: `pipeline/sentiment/tone_words.py`:924-928, 960-983 · 单元: tone-words-tfidf-lm
  - 裁决: 亲验 tone_words.py:924-928 按 argmax(matched) 逐篇选词典, L960-983 pos_ratio/msent 消费 best_*; 盘上857行复证胜出词典逐篇切换(yao 51.2%/du 41.1%/jiang 9.6%); encode.py:562-571 聚合进 panel。所引 Tetlock 2007/Garcia 2013/Henry 2008 均为固定词典构念, 嵌合体测度跨文不可比且词典选择内生于文体。2026-06-02 FINAL 曾评 P1 至今未修且不在台账, P2 成立。

- **FIX-REGRESSION: lmfls-01 word-token 分母修复未延伸至同文件同族 frac 指标 (clarity/pos_ratio/neg_ratio 仍含 ~19% 标点数字分母)**
  - 位置: `pipeline/sentiment/tone_words.py`:282-293, 919-921, 960-962 (对照 lm_non_sentiment.py:124-129 已修) · 单元: tone-words-tfidf-lm
  - 裁决: lm_non_sentiment.py:124-128 已修 word-token 分母(fix 注释自证~19%标点/数字 token), 但同 stage 同引 LM 2011/Garcia 2013 的 tone_words.py:284-285(clarity frac), 920-921({dict}_ratio), 961-962(pos/neg_ratio) 仍用全 token 分母 — 两套口径并存, 逐篇 14.5-25% 非常数缩放; clarity docstring(L243-244) 仅披露未去停用词未披露标点膨胀, frac_definite/clarity_score 是 clarity 论文核心测度。修复不完整成立。

- **pos_ratio/neg_ratio/msent_score 基于逐篇漂移的"最多匹配词典"——测量工具跨观测不固定**
  - 位置: `pipeline/sentiment/tone_words.py`:923-928, 960-962, 978-983 · 单元: tone-words-core
  - 裁决: tone_words.py:924-928 逐篇取 len(matched) 最大词典, L960-962/978-983 由其派生; encode.py:560-571 聚合为 avg_pos/neg_ratio/avg_msent 并引 LM2011/Tetlock2007(均要求固定词表)。盘上实证: full 轨胜出词典 yao 426/du 343/jiang 75/you 10/bian 3 + 43 平局, 同列跨观测换词表, 非经典测量误差成立。

- **pos_ratio/neg_ratio/{dict}_*_ratio 分母含标点+纯数字 token (均值 19.2%), 与同文件 2026-06-10 LM/FLS word-token 分母修复不一致**
  - 位置: `pipeline/sentiment/tone_words.py`:872-875, 919-921, 960-962 · 单元: tone-words-core
  - 裁决: tone_words.py:875 仅滤空白, L919-921/960-962 分母=len(tokens) 含标点数字; lm_non_sentiment.py:46-49,128 已修 word-token 分母但未延伸至本族 24 列。盘上 60 篇实测非词 token 占分母均值 18.8% (11.3-25.7%, std 2.9pp), 跨文稀释不均。非台账重复(LM 修复仅覆盖 lm frac 列)。

- **词典加载对正∩负重叠词静默 last-write-wins 判负 (jiang 21 词 + you_2018 5 词, 含出现于 9.7% 文档的'打破')**
  - 位置: `pipeline/sentiment/tone_words.py`:329-337 (load_all_dictionaries) · 单元: tone-words-core
  - 裁决: tone_words.py:334-337 negative 循环无 `word not in d` 守卫(L342 political_positive 有), 重叠词静默判 -1.0。实测 tone_dicts.json: jiang 重叠 21/you_2018 5; 加载 8794/3003 < docstring L17-18 声称 8815/8815-21 吻合且自述'两类不跨类去重'。'打破'出现于 83/857=9.7% 文档, 大胆1.8%/抢占1.6%/规避1.4%, 无日志披露。

- **句子分母正则把全角句末标点的 digit-guard 一并应用, 漏计 6.4% 真句界 (63.6% 文章受影响), 误差与分子正相关 → num_intensity 系统性上偏**
  - 位置: `pipeline/sentiment/numerical_intensity.py`:50 (_SENTENCE_END_RE), 221-224 · 单元: fls-lexical-numint
  - 裁决: L50 `(?<!\d)[。！？.!?](?!\d)` 对永不为小数点的全角。！？同样守卫。实测 '…显著。2017年…' 仅计 1 句; 全语料转换后文本丢 2383 个全角句末符 (7.1%), 744/1170=63.6% 文章受影响, 与发现者数字一致。分母偏小且与分子(digit相邻)正相关 → 上偏。

- **FLS 时间门控收录方向模糊/当期时间词 (三年/五年/十年/长期/中期/本年度/本季度/年底/年内), 未来门控收录进行体动词 (推进/推动/促进/努力) 与名词 (战略/目标/前景) → 回溯性成就报道被判为前瞻陈述**
  - 位置: `pipeline/sentiment/forward_looking.py`:80-100 (_TIME_FUTURE_MARKERS), 66-70 (_FUTURE_WORDS 战略/目标/前景/推进族) · 单元: fls-lexical-numint
  - 裁决: forward_looking.py:88-94 D_time 含 三年/五年/十年/长期/中期/本年度/本季度/年底/年内; L66-69 D_future 含 推进/推动/努力/战略/目标/前景。亲测 '过去三年,该行持续推进零售转型。'→True, '十年来…十八大以来…战略推进…'(语料实句)→True。违背 Li 2010 未来指向双门控构念; 词表未审定的披露不豁免口径反向。

- **rare_word_ratio 分子 26.4% 是纯数字 token、3.7% 是英文 token (OOV freq=0 ≤ cutoff) — "词汇难度"被数值密度与外来词污染**
  - 位置: `pipeline/sentiment/lexical_complexity.py`:204-207 (freq.get(w,0) <= cutoff 对全部 real_pairs 含 m/eng), 111-124 (_rare_word_cutoff) · 单元: fls-lexical-numint
  - 裁决: lexical_complexity.py:204-206 对全部 real_pairs 用 freq.get(w,0)<=cutoff(3.0), '100'/'2017'/'ABC' 均 freq=0 命中。200 篇实测精确复现: 15973 rare 中数字 4216 (26.4%)+拉丁 598 (3.7%)≈30% 分子与难度构念无关, 且与 num_intensity 机械同源。docstring 仅披露 tie (L47-50), 未披露此污染。

- **within_doc_redundancy (1−唯一3gram占比) 强机械长度依赖: corr(长度)=0.50, 长度五分位均值 0.119→0.228 单调翻倍; full 轨 (中位 1559 字) vs ctx 轨 (732 字) 的轨间差异主要由长度驱动**
  - 位置: `pipeline/sentiment/lexical_complexity.py`:158-170 (_char_trigram_redundancy) · 单元: fls-lexical-numint
  - 裁决: 盘上 1170 篇精确复现: corr(长度)=0.500, corr(log长度)=0.472, 五分位均值 0.119/0.139/0.156/0.197/0.228 严格单调; full/ctx 中位长 1553 vs 725。TTR 族经典长度敏感 (Covington-McFall 2010), 截面变异大半由长度机械驱动, 而 L29-30 诚实限定段仅披露短文本弱信号。轨间可比性子项按双轨纪律弱化, 但篇级/bank-year 长度混杂本身成立。

- **TF-IDF df-band 随组规模退化: min_df=5(绝对计数)+max_df=0.9 在小/中型银行组把词表压缩到近全员共现的 boilerplate 子空间, 相似度系统性膨胀, 0.35 阈值跨银行不可比**
  - 位置: `pipeline/sentiment/herd_decay.py`:83-103 (_build_tfidf_vectorizer), 与 config/sentiment.yaml:298-299 · 单元: herd-decay
  - 裁决: herd_decay.py:89 min_df 绝对计数+L92 floor 收带: n=6 存活带 df∈[5,5.4] 即恰好 5/6 篇, n≤5 relaxed 与 n=6 断崖。盘上独立复现: full 轨 flags 313 vs 253(+24%), n=8 组 5 vs 0(vocab 293 vs 10000), vocab 105/1358 与证据吻合。跨组测度非不变性坐实, P2 成立。

- **Tetlock 2011 RFS 保真缺口: 未按同银行先前报道匹配 (全语料池化) + '原文 cosine 范式' 系误称**
  - 位置: `pipeline/text/article_staleness.py`:19, 24-26; compute_surface_staleness/compute_semantic_staleness 全函数无 target_bank 条件 · 单元: staleness-sbert-embed
  - 裁决: 属实且非台账重复(台账仅修期刊名JF→RFS)。compute_surface/semantic_staleness 签名 (L80-85/L190-194) 与实现均无 target_bank 条件, 全银行混池7d窗; docstring L19 称'原文 cosine 范式', 但 Tetlock 2011 是同公司72h词重叠率, 非嵌入cosine。构念域+声称双重失真, 同 attention_index≠Hassan 类比, P2 成立。

- **跨行子串误归因: '法国兴业银行' 文章同时合格为 '兴业银行' 新闻, 生成错误银行-文章面板行**
  - 位置: `core/text/ahocorasick.py`:326-347 + config/bank_names.json (71 对跨行嵌套变体) · 单元: ctx-materializer-coretext
  - 裁决: 亲跑复现: SocGen测试文同时令法国兴业银行(中国)与兴业银行均qualified(total_with_title=4); 实测71对跨行嵌套对; 252条negation_patterns无任何'法国兴业'/'中信银行国际'消歧条目。news_bank.py:217-220把每个qualified bank展开独立面板行→错误target_bank行确凿。T=19全量按比例放大。

- **ctx 实体窗口锚定用裸子串匹配, 与 stage 11 分类的否定/短名排除规则不一致**
  - 位置: `core/text/entity_context.py`:169-174 (extract_entity_context), 274-279 (with_distances 同型) · 单元: ctx-materializer-coretext
  - 裁决: entity_context.py:171-174与276-279确认裸`alias in sent`, 不调is_match_excluded; stage 11(ahocorasick.py:327-328)带negation/short_name排除。同一alias两套匹配语义确凿, 被分类器判非本行的假锚('农行'⊂'涉农行业')拖无关句进content_ctx — 而ctx是P1主spec(llm_vote_tone_ctx)的文本基底, 2.7%文章受染。修复trivial但口径不一致结构性成立。

- **跨行变体子串包含无消解→外资行/子行新闻误归属为样本内大行, 产生幻影 firm-document 行**
  - 位置: `core/text/ahocorasick.py (analyze_bank_matches, 同一计数循环) + config/bank_names.json`:ahocorasick.py:326-360 · 单元: news-bank-fintech-salience
  - 裁决: 亲跑复现: 纯法国兴业银行文章同时合格为'法国兴业银行(中国)'(total=3)与'兴业银行'(total=3, in_title=True)两条firm-doc行, SocGen语调注入兴业银行面板。实测bank_names.json 71对跨行包含; 盘上138条兴业银行行中1条含'法国兴业银行'。18.2M全量下外资在华子行/县域农信族报道更频, 影响放大。

- **中国银行否定模式词典缺口: '中国银行间'(银行间市场)与'中国银行保险监督管理委员会'(银保监会全称)未覆盖→ BOC 幻影行 (盘上已实证 1 条纯幻影行)**
  - 位置: `config/bank_name_exclusions.json (negation_patterns) + core/text/ahocorasick.py:175-191`:negation_patterns (252 条) · 单元: news-bank-fintech-salience
  - 裁决: 实证: negation_patterns(252条)含'中国银行业'/'中国银行家'但无'中国银行间'与CBIRC全称(逐条grep证实)。亲跑: 纯NAFMII文章→中国银行total=3入样; 对照'中国银行业'被正确拦截, 证明同族短语本应入表。盘上坐实1条纯幻影行(recorded_count=3全部来自'中国银行间', n(中国银行)=3全在其内), 另4条部分通胀。

- **上下半 50/50 字符分割逐半扫描→横跨边界的银行名/fintech关键词匹配被双侧同时丢失 (实证: 正文提及完全消失致分类翻转)**
  - 位置: `core/text/ahocorasick.py (analyze_bank_matches L311-347; analyze_fintech_matches L473-485)`:ahocorasick.py:311-313, 326-347, 473-485 · 单元: news-bank-fintech-salience
  - 裁决: 亲跑复现: '中国工商银行公布业绩。'(split=5)正文提及upper=0/lower=0彻底消失, 仅标题2次<3→is_bank_news翻转为False。ahocorasick.py:311-313先切再扫, 跨界匹配两段都不含; fintech侧L473-485同病。否定/短名上下文窗同被截断。无声欠计与idx0通胀方向相反但同样系统性, 1.4%文章受累量级可信。

- **target_in_lead 仅匹配规范行名而非变体→跨行差异性低估 5 倍 (农行 0.161 vs 0.828), '保守下界'披露失真**
  - 位置: `pipeline/filtering/news_salience.py:107-120 (target_in_lead)`:news_salience.py:117-120 · 单元: news-bank-fintech-salience
  - 裁决: 盘上全量复算逐位证实: 农业银行canon=0.161 vs variant=0.828(5.1x), 工行0.362/0.825, 中信0.890/0.890无偏; 与parquet落盘target_in_lead均值完全一致。news_salience.py:117-120只查bank_name。偏差由命名惯例决定而非均匀保守, 跨行比较被命名结构主导; '保守下界'披露(L21/L111)掩盖差异化本质, 且变体表现成可用、修复零成本。

- **Full 轨共提及文章全文重复注入多家银行年度文档, 机械抬升跨行相似度 (Hoberg-Phillips 构念失真, 未披露)**
  - 位置: `pipeline/features/strategic_diff.py`:309-351 (_aggregate_bank_year_texts) + 1283-1284 · 单元: strategic-diff-measures
  - 裁决: strategic_diff.py:345 按展开行全文拼接无文章级去重; 实测 47/786 篇 explode>1 行(max 8), 118/857 行重复文本, 盘上 strat_sim_max_emb_t2v max=1.000000 恰为逐字重复文档; HP2016 用互斥自有文本, docstring L121-126 未披露此偏差。全量共提及更密, 偏差与媒体共覆盖相关, P2 成立。

- **跨银行共享文章机械相似 — 同一篇多银行报道逐字进入多家银行的"年度战略文档", N-NN 最近邻被共同报道而非战略相似驱动**
  - 位置: `pipeline/features/strategic_diff.py`:309-351 (_aggregate_bank_year_texts), 683-744 (_compute_nn_scores) · 单元: strategic-diff-panel
  - 裁决: 盘上实证逐位吻合: 24_herd_decay 13.8%展开行跨银行逐字重复, 47/786文本挂>1银行, 5/118 bank-year 100%共享(9个≥50%)。strategic_diff.py:309-351无去重/降权, L121-126局限性段未披露。HP2016/GL2023文档自撰唯一, 逐字复制产生与战略无关的机械相似, 真实构念污染。

- **行业质心包含自身 (无 leave-one-out) — centroid_diff_* 全族存在机械性自相关, 对最差异化银行的衰减最大**
  - 位置: `pipeline/features/strategic_diff.py`:836-844 (_compute_centroid_scores) · 单元: strategic-diff-panel
  - 裁决: L836-841 centroid=mean(全部含自身)后cosine, 无排除。模块内对照: NN路径L409 fill_diagonal NaN、fluidity L906 other!=bank均显式排除自身, 质心是唯一例外。偏置~1/n_t且对差异化越高的银行压缩越大(系统性衰减), 与已修bartik 'other'排除同类口径错误, 非台账已修项。

- **27c alt-anchor/placebo 审计链路结构性失效: .npy 输入产物已无人生成 + 嵌入空间错配 (2026-05-29 主轨换模后未重接线)**
  - 位置: `pipeline/features/benefit_society_alt_anchor.py (+ audit_combined.py, benefit_society.py)`:alt_anchor.py:266-270,315-318; audit_combined.py:92-94,156-171; benefit_society.py:478-498,594-599; config/features.yaml:38 · 单元: benefit-society
  - 裁决: 四证齐全: _project_texts(benefit_society.py:481-498)不引用cache_path, _CACHE_EMBEDDINGS(L113)死读, features.yaml:38虚假声称缓存; 全仓无生产np.save; 盘上npy实测(584,1536)/2026-05-09 vs 当前857行→长度守卫必raise; alt_anchor.py:317用768维方向 vs 1536维npy→project_texts L170-173维度守卫必crash; --main-direction-npy无产出方; 27c parquet盘上不存在而2个Stata模板(23_tableA10/24_tableA11)依赖之。AC-A2/AC-S1承诺检验当前不可执行。

- **静态政策锚点含未来年份政策文本 — policy_cosine_sim 与 auth_sim_* 全族存在前视构造 (latent, 全量 T=19 更重)**
  - 位置: `config/authoritative_corpus.txt (消费方 pipeline/filtering/policy_alignment.py + pipeline/features/policy_similarity.py)`:corpus L44-45/L121/L244/L299; policy_alignment.py:430-459 (4.1 加载) + 533 (4.4 分段); policy_similarity.py:101-117 · 单元: policy-alignment-similarity
  - 裁决: corpus L44-45(2021-12)/L121-122(2019-08)/L244(国办发〔2025〕8号)实读确认; 两消费方整体读入无 vintage 切分(policy_alignment.py:449-451; policy_similarity.py:110-112)。盘上 2017-18 文章对 ≥4 份未来政策算余弦, 测度自称'响应国家政策'却嵌入 t 期不可知文本, T=19 更重。真构念缺陷非允许变体。

- **方法 F '高置信度子样本' 阈值 >= 0.67 把唯一的多数票档 2/3 (=0.6667) 整类排除, 实际退化为全票一致子样本, 与声称的 '≥2/3' 构念不符**
  - 位置: `pipeline/panel/runner.py`:519, 566 (vs 构念声明 L424) · 单元: panel-runner-merge
  - 裁决: 亲验属实。runner.py:424 声明 ≥2/3(Shapiro 2022), L519/566 实现 >=0.67; 盘上 24_herd_decay agreement_rate 仅取{2/3,1.0}: full 135/857、ctx 129/857 篇恰为 2/3<0.67 被静默排除, _hc 退化为 ==1.0; 下游 encode.py:760 pos_hc_count→runner.py:1484 washing_ratio_hc 实际受影响。注释 vs 实现的浮点边界翻转, P2 恰当。

- **log_sent 对零覆盖 bank-year 产出伪零 (=0), 与同族语调测度 (JF/concern/disag 皆 NaN) 的缺失语义不一致 — 32% 样本被注入 '完全均衡情感' 假观测**
  - 位置: `pipeline/panel/runner.py`:1628-1634 · 单元: panel-runner-merge
  - 裁决: 盘上实证属实: 56/174 行(32.2%) n_articles==0 的 log_sent_full 全部 notna 且 ==0(pos/neg_count 零填 Int8), 同行 jf_coefficient/concern_score/disag_llm 全 NaN。runner.py:1628-1633 log1p(fillna(0)) 漏守; 违反本文件自申明 F3 红线(L1137-1141/L1324-1332: 无文章语调→NaN)。同族不一致缺失语义, P2 成立。

- **方法F高置信子样本阈值 >=0.67 把整个 2/3-agreement 类静默排除, 与声称的 "≥ 2/3" 互斥**
  - 位置: `pipeline/panel/runner.py`:519, 566 (声称处 424, 516) · 单元: panel-runner-weights
  - 裁决: 亲验坐实: runner.py:519/566 `>= 0.67`, L424 注释 "≥ 2/3"。盘上 agreement_rate 支撑集仅 {0.6667,1.0} (full 135/722, ctx 129/728), 0.67 把全部 2/3 票逐出 → 实现=全票一致; 而有效多数票数学保证 ≥2/3, 文档版过滤真空。声称 vs 实现必有一错, export.py:815 'WR: Hi-Conf' 标签未披露阈值。非台账项。

- **D4 residual frac (subst/locus/collab × disagree/freerider/quietworker) 分子域=both_valid 但分母=物理文章数 → 覆盖率混淆的系统性下偏 + 全量下假零**
  - 位置: `pipeline/panel/encode_collab.py`:376-381 (root: 121/140-142 invariant iii; gate 389) · 单元: encode-collab
  - 裁决: 亲验+实证坐实: L140 缺轨编 False(invariant iii), L376-377 mean 分母=物理文章数; 盘上 panel subst_disagree_frac 与物理分母重算 32/32 一致, 7 行较 both_valid 分母低估(0.0909 vs 0.1000), collab 维 9 组 both_valid=0(n≥5 时输出假零), L389 small_mask 亦用物理 n。与已修 clarity/peer_tone valid-mask 家族同型, 但 18 列均为新位置且盘上已现值损害, 非台账重复。

- **balance_panel 计数/和类列零填充契约残缺: n_articles_llm_valid(_ctx)/ctx对角计数/sum_herd_weight_*/coverage_active_days 在零新闻行残留 NA 而非 0**
  - 位置: `pipeline/panel/encode.py`:1623-1657 (zero-fill 名单/regex), 对照 595/603/908-918/1114/1236/1368/708-709/941-948 · 单元: encode-features-agg
  - 裁决: encode.py:1623-1657 名单/regex 均不匹配 n_articles_llm_valid(_ctx)(595/603)、_lc/_sc/_cm_ctx 计数、sum_herd_weight_*(708-709)、coverage_active_days(941-950)、n_articles_for_ctx_independence(912)。盘上实证 56/56 零新闻行 NA, 对照 sum_media_authority_weight=0 正确; codebook.py:266/282 声称 int [0,n_articles] 与 Int64<NA> 不符。L1/F4/F5 同族修复残留缺口, 非台账重复。

- **coverage_continuity 构念退化: 自身跨度做分母致单日爆发=1.0 (最大值), 与 codebook/注释声称的「低=爆发式」相反**
  - 位置: `pipeline/panel/encode.py`:936-954 (esp. 947-948), 对照 codebook.py:845-848 / export.py:443 · 单元: encode-features-agg
  - 裁决: encode.py:947-948 分母=自身首末跨度+1, 单日报道→1/1=1.0 最大值, 与 encode.py:933-934 及 codebook.py:848「1=天天有, 低=爆发式」相反。盘上实证: 55/118(47%)=1.0 其中 52 为单篇; corr(continuity,active_days)=-0.30; 真高频银行仅 0.53-0.74。端点内生性使稀疏覆盖系统性虚高, 公式vs构念真错配, 非设计变体。

- **Embedding 同业网超级文档前缀截断 8000 字符: 全量语料下 W_emb 退化为'最先若干篇文章前缀'的相似度 (latent, 试跑已 30% 现身)**
  - 位置: `pipeline/panel/network_spillover.py`:1181 (MAX_CHARS=8000), 1220-1221 (texts = [t[:MAX_CHARS]]) · 单元: network-spillover
  - 裁决: L1181 MAX_CHARS=8000 + L1221 t[:MAX_CHARS] 核实; 盘上复现: 118 bank-year 中 30.5%>8000, mean=12168/max=151248 字符, 被截组中位仅留 37.5%, 最多 101 篇/bank-year — 截断保留 df_lag 行序最先文章前缀, 非代表性。对照 compute_cognitive_proximity(L770+) TF-IDF 轨用全年全文, 两邻近度信息集不一致; docstring L1295 '每年的新闻文本' 与实现不符。盘上已现身故 confirm 而非 latent; T=19 下退化更剧。

- **attention_attr_share 把两种不同长度归一化的密度比值当 share, clip[0,1] 实际censor了11.5%面板值在1.0**
  - 位置: `pipeline/panel/attention_media.py`:332-334 (定义), 241 (docstring '归因纯度 clip[0,1] B4'); codebook.py:216-218 · 单元: attention-media
  - 裁决: 实证复现: panel==1.0 恰14/122(11.5%), 文章级ctx>full 291/1170(max 1.59)。fintech_intensity.py:341-345 score=Σ(1+log tf)/(1+log L_d)×w 长度归一密度, ctx短→密度合法更高, 比值非子集share; codebook.py:216-218仍登记[0,1]归因纯度。clip(attention_media.py:334)系统性censor非异常处理, P2成立。

- **维度⑤官方 vs ⑥市场化: OFFICIAL∩MARKET 重叠 386 家 (82% 的市场化媒体同时是官方), You-Zhang-Zhang 2018 RFS 对立二分未被实现**
  - 位置: `pipeline/panel/attention_media.py`:789-845 (维度⑤⑥), 1161 ('正交分类'日志); config/media_classification.json · 单元: attention-media
  - 裁决: json实测|OFF|=2208/|MKT|=471/重叠386(82%); 面板official_frac均值0.873近退化, 两占比和1.53。attention_media.py:789-794/818-824引YZZ对立构念, 实现为重叠dummy, tone_gap_official_nonoff的nonoff组剔除了大部分市场化媒体; L711-713仅查FIN∩COMP从未查OFF∩MKT。构念失配坐实。

- **industry_neg_shock 同期 LOO 均值在年 FE 下与自身 neg_ratio 精确共线 (within-year corr = -1.0), 行业冲击解释在标准规格下结构性失效**
  - 位置: `pipeline/panel/network_brokerage.py`:345-359 (公式), 302-307 (docstring 声称), 41-42/394-396 (Stata 示例) · 单元: network-brokerage
  - 裁决: 盘上验证仿射恒等式 max err=0.0, 两年 within-year corr 均精确 -1.0。paper_spec.yaml:36 与全部 brokerage 模板均 absorb(bank_id year), 年FE下识别变异=−own_ratio/(N−1), docstring L302-304 '消除机械自相关'恰反。与台账 Manski 反射 docstring 修正(L305-307)是不同缺陷, 非重复。

- **brokerage_eigen_cent 非连通图走迭代路径, 非主分量银行获得 1e-180~1e-30 的幂迭代衰减伪值 (networkx 的 AmbiguousSolution 守卫被刻意绕过)**
  - 位置: `pipeline/panel/network_brokerage.py`:222-245 (is_connected 分流 + 迭代 fallback) · 单元: network-brokerage
  - 裁决: 逐位复现: 2017 图 2 分量/2018 图 6 分量均走 L232-239 迭代路径; 重算值 3.244e-180/1.917e-33/5.199e-30 与盘上 panel 6 个 tiny 值完全一致。非主分量值是 (I+A) 幂迭代指数衰减残渣, 同结构位置跨年差 147 个数量级, 无网络含义却进同一回归列。

- **IV 外生性: 滞后同行情感均值机械含焦点银行自身 t-1 新闻 (共享文章无 leave-out), 排除约束声称与实现不符**
  - 位置: `pipeline/panel/llm_peer_iv.py`:671-690 (compute_llm_peer_iv 步骤6); 病根接线 pipeline/filtering/news_bank.py:217-223 · 单元: llm-peer-iv
  - 裁决: 亲验 news_bank.py:217-223 explode 使共提文章同入 i/j 双方 bank-year 情感; 实测 24_herd_decay 138/857=16.1% 共提行; llm_peer_iv.py:642 仅银行级排自身, L671-677 直取 peer 均值无文章级 leave-out。L31-34 引 Leary-Roberts 为'同行情感均值 IV 理论基础'恰反 — L&R 正因排除约束改用特质冲击; lag 不解共享文章+情感持续(stage24)。台账仅修 network_brokerage 引文, 本模块未涉, 非重复。

- **句子双重筛选 '≥2 家银行' 被同行变体子串双计破坏: ~20% 送入 LLM 的句子实际只含 1 家银行**
  - 位置: `pipeline/panel/llm_peer_iv.py`:239-244 (_extract_multi_bank_sentences) · 单元: llm-peer-iv
  - 裁决: L241-244 banks_found 收集原始变体非规范名; 实测 bank_names.json 1476/1767 条目变体⊂标准名(如工商银行⊂中国工商银行)。盘上逐句复算: 292 过筛句中 56 句(19.2%)规范化后仅 1 家银行, 量级坐实。docstring L209-211 免责仅指跨行误匹配('中国银行业'), 不涵盖同行变体双计击穿'≥2 不同银行'契约; 单行句被当比较句送 LLM 污染同行识别核心构念。

- **46% 送 LLM 的句子根本不含焦点银行, 但 prompt 断言这些是 '同时提及【焦点银行】和其他银行的句子'**
  - 位置: `pipeline/panel/llm_peer_iv.py`:239-249 (筛选不要求焦点银行在句中) + 267-269 (PEER_PROMPT 前提) · 单元: llm-peer-iv
  - 裁决: L225-249 亲读: 筛选仅要求文章 co_mentioned 非空+句含任意≥2银行+fintech词, 全程不查焦点银行是否在句中; PEER_PROMPT L267-269 却断言句子'同时提及【{bank_name}】和其他银行'。盘上复算 135/292=46.2% 过筛句规范银行集不含焦点, 与声称 46.4% 一致。虚假前提直接诱导 LLM 把无关银行判为焦点行竞争对手, 同行边可被幻觉构造。

- **FIX-REGRESSION: z_score 'CAR 变体≠Laeven-Levine' 引文修复只改了 bank_news_clarity paper_spec 一处, 姊妹 paper_spec/tables.py/两套 Stata 表注/replication README 共 10+ 处仍直引 L&L 2009**
  - 位置: `papers/bank_media_disagreement/paper_spec.yaml (及 11_table2 两模板/tables.py/replication)`:paper_spec.yaml:58; 11_table2_main_disagreement_risk.do.tmpl:4,71; bank_news_clarity/11_table2_main_clarity_risk.do.tmpl:4; 两 tables.py:24; 两 replication/README.md:54 · 单元: risk-taking
  - 裁决: grep 实证: 更正文案仅 bank_news_clarity/paper_spec.yaml:65 一处; bank_media_disagreement/paper_spec.yaml:58、两 11_table2 模板:4、disagreement 模板:71 esttab note "Z-score per Laeven-Levine 2009 JFE."(直渲染进成品表格脚注)、两 tables.py:24、两 replication README:54 及 replication/code 共 13 处无披露直引。FIX_CLOSURE 报告 L21 也只登记 paper_spec.yaml:65 — 修复不完整坐实。

- **DC4 39h 污染检验默认接线结构性死路: validation.yaml 声称 'stage 49 已把 z_score 并入面板', 与 runner.py 刻意不并入的设计直接矛盾 — 检验在任何配置下永远优雅跳过**
  - 位置: `config/validation.yaml + pipeline/panel/runner.py + pipeline/audit/llm_contamination_test.py`:validation.yaml:76,83; runner.py:1711-1712; llm_contamination_test.py:344-346 · 单元: risk-taking
  - 裁决: validation.yaml:76 写'stage 49 已把 outcome_col (z_score) 并入面板'; runner.py:1711-1712 明示'stage 49 刻意不在此(范畴错误)'; llm_contamination_test.py:362-366 缺 z_score 即 skip。pipeline 无任何产物同时含 llm_vote_tone_full 与 z_score (49 独立 parquet 无 LLM 列), cfg.input 重定向也无解 — 默认接线下 DC4 必修检验结构上永不激活, 文档把不可能写成前置。坐实 P2。

- **复合键去重在 NF 聚合前折叠跨媒体转载副本 — nf_media_breadth (Bushee 2010 媒体广度构念) 系统性低估 (latent 放大)**
  - 位置: `pipeline/falsification/controls.py`:339-343 (dedup) + 530-536 (nunique) · 单元: falsification-controls
  - 裁决: controls.py:335 去重键无媒体列, L339/343 keep='first' 在 L530-536 nunique 之前执行。盘上实证: 20 重复键 19 个跨>1媒体, 复算 1/321 bank-year 广度被低估。Bushee 2010 构念=不同中介覆盖数, 转载即广度, 集合语义不能开脱口径错; 全量转载占比高且与显著性相关 → 非经典测量误差。

- **all_n_articles / ln_ft_articles vs ln_nf_articles 混合计数基: fintech 侧物理、NF 侧去重 — 2026-06-10 修复只修了 fintech_share, 注释把混合基误称'物理覆盖'**
  - 位置: `pipeline/falsification/controls.py`:623-661 (构造) + 630-635 (注释) + 787-803 (弹性诊断) · 单元: falsification-controls
  - 裁决: 实证: panel n_articles=物理 (174/174 匹配), nf_n_articles 经 L343 去重 (4054→4031, NF 3193→3182), L623 all_n_articles 混基; L657-658 弹性对两端口径不同 (5/174 行已不等)。L633-634 注释称 'n_articles+nf (物理覆盖)' 与实现不符。非 fintech_share 已修项重复 — fix 注自认仅改 share。

- **DDD 调节变量 digital_frontier = 逐年同期 median split (时变内生组员资格), 违反本文件自身对 Bartik 强制的 pre-treatment 固定公理**
  - 位置: `pipeline/panel/runner.py`:719-729 (构造), 966-972 (DDD 交互) · 单元: sweep-insample-leakage
  - 裁决: runner.py:721-726同年groupby(['bank_type','year'])中位数切分实证; 盘上43/87银行2017→2018翻转(逐位复核一致); L966-976 DDD交互在产。消费比声称更广: 11_table2_main_m1m6.do.tmpl:82-115以digital_frontier为主解释变量M1-M6+30_figure1事件研究处理变量, 内生时变分组与L664-673 Bartik公理自相矛盾。坐实。

- **FIX-REGRESSION: prompt_sensitivity ctx 轨变体未剥离 prepend 标题 — 标题双重注入污染 baseline↔variant 对照 (tonellms-01 修复未传播)**
  - 位置: `validation/prompt_sensitivity.py`:509, 514-520 (run_variant_llms) · 单元: validation-sensitivity
  - 裁决: 实证坐实: tone_llms.py:608-613 生产剥离 ctx 标题前缀, prompt_sensitivity.py:509+514-520 直接用 content_ctx 并另注 {title} → 变体 ctx 标题两次/V0 一次。盘上验证 1170/1170 行 content_ctx 以标题开头(内容仅7/1170)。任何重跑必污染 ctx 轨措辞敏感性指标, tonellms-01 修复未传播。

- **变体 prompt 滞留 v7 三阶段 schema, 缺 v8 第三维度 innovation_collab_mode — 覆盖缺口 + baseline↔variant schema 不一致 + 死阈值配置**
  - 位置: `validation/prompt_sensitivity.py`:143-384 (VARIANT_PROMPTS), 117-118 (PASS_THRESHOLD_INNOVATION_COLLAB_MODE) · 单元: validation-sensitivity
  - 裁决: 亲验: V1-V4 输出 JSON 均止于 innovation_locus_confidence (如 prompt_sensitivity.py:185-201), unified_cot.txt:62/111-113 v8 含 collab_mode; PASS_THRESHOLD_INNOVATION_COLLAB_MODE 仅 L118 定义从未消费(grep 证实); criteria L1195-1204 无 collab。盘上 JSON 4 变体 true_rate 双轨同向下移(0.583-0.653 vs 0.678/0.724), 与版本混淆一致。P5 collab 论文第三维度零敏感性覆盖。

- **Prompt 敏感性通过/未通过裁决仅基于 full 轨, ctx 轨 (论文主 spec 所在轨) 不进 gate**
  - 位置: `validation/prompt_sensitivity.py`:1170-1206 (Step 7), 843-872 (json_report 单一 passed 字段) · 单元: validation-sensitivity
  - 裁决: prompt_sensitivity.py:1173-1206 全部 criteria 取 pairwise_results['_full']/multi_results['_full'], passed=all(criteria) 单字段写 JSON (L861, 盘上 passed=false)。CLAUDE.md 明示 P1 main=llm_vote_tone_ctx。盘上 iss_κ ctx 最低 0.342 vs full 0.284, 两轨阈值边缘, full 过 ctx 不过时会误报通过。

- **词典 tone 族突破 [-1,1] 值域: 程度副词×3.0/转折×1.5 加权分子除以未加权匹配计数分母**
  - 位置: `pipeline/sentiment/tone_words.py`:439-469 (_compute_sentiment_with_rules; config/sentiment.yaml:71,142-150) · 单元: data-panel-invariants
  - 裁决: tone_words.py:439-445 分子乘 degree(config 极其=3.0)×adversative(1.5), L467-469 分母=裸 pos+neg 计数; tone_dicts.json 为纯词表(base=±1)→理论值域±4.5。盘上实证: 4/5 词典文章级 81-140 篇>1 (you max 1.286), 面板 you_2018_tone_ctx 9行>1、dict_avg_tone_ctx/prov_leave1out max 1.034。文献构念(P−N)/(P+N)有界, ±0.1 阈值按单位区间校准, 跨方法可比性破坏。不在已修台账(LM分母/JF t²/IDF均为他项)。

- **Bartik 基期份额未定义时 fillna(0): 行和=0≠1, IV 制造伪零 — media 族波及 35/87 银行**
  - 位置: `pipeline/panel/iv_did.py`:149-150, 181, 256, 312-318 · 单元: data-panel-invariants
  - 裁决: iv_did.py:149-150 基期无文章银行 continue→L181 merge fillna(0); 第二构造器 L312-313/318 同型; L256 BIV=Σ0×shift≡0非NaN。盘上实证: media 族 70/174 行份额行和=0 (35/87银行, 40个当年有文章的 bank-year IV 仍恒0), 其余6族各30行; 非零行行和=1精确。已修 ivdid-05 仅改 'other' 分母(L306-313注释自证), 未触及此缺陷。GPSS 2020 incomplete-shares 成立; T=19 下 T0=2007 伪零更多, 缺陷放大。

- **bert_avg_pos/neg 把二分类 finbert2 与三分类模型直接平均: pos+neu+neg 全行≠1 (最大 1.33), pos 概率系统性上偏**
  - 位置: `pipeline/panel/geography.py`:79-81 (bert_avg 系列构造) · 单元: data-panel-invariants
  - 裁决: geography.py:79-81 pos/neg 平均全部 BERT_MODELS(含二分类 finbert2), neu 仅 THREE_CLASS_MODELS(encode.py:66-72) — 自身已承认类空间不同却仍混 pos/neg。盘上实证: finbert2 pos+neg≡1(dev 2e-16), pos 均值 0.912 vs 三分类 0.690/0.817; bert_avg_pos==三模型均值(maxdev=0); 三类和 max 1.325/1.333。声称的118行系非零新闻行口径, 实质完全成立。聚合域缺陷, 非台账已修项。

- **跨银行嵌套变体误归属: 法国兴业银行新闻被完整判定为兴业银行新闻并生成 firm-document 行**
  - 位置: `core/text/ahocorasick.py (analyze_bank_matches, 无跨行消歧) + config/bank_names.json (71 对跨行嵌套变体)`:326-424 · 单元: sweep-chinese-text
  - 裁决: 实证复现: 词典 71 对跨行嵌套; 纯法国兴业文章 (3 正文+1 标题) 使'兴业银行' total_with_title=3+in_title=True 合格 → news_bank.py:205-220 生成独立 firm-document 行, tone 误入兴业银行聚合。短名消歧仅 variant_len<=2 触发 (ahocorasick.py:198), 4 字变体无覆盖; 否定模式实测含兴业证券/兴业路但无'法国兴业'。频率受限于外资行/县农信社新闻量, P2 恰当。

- **jieba 注入副作用: OOV 领域词被 posseg 标为 'x' 后当标点剔除, lexical_complexity 全族 8 列失真且依赖注入态**
  - 位置: `pipeline/sentiment/lexical_complexity.py:78,189-190 (_PUNCT_FLAG='x' 过滤) × pipeline/sentiment/tone_words.py:702-834 (_inject_custom_dicts_to_jieba)`:lexical_complexity.py:189-190 · 单元: sweep-chinese-text
  - 裁决: 实证复现: 注入 36847 词后 pseg.lcut('金融科技')=[pair('金融科技','x')], 被 lexical_complexity.py:189-190 f!='x' 过滤剔出分母分子; 同文本 n_words_real 15→9, rare_word_ratio 0.067→0.0, function_word_ratio +67%。生产路径 tone_words main L1266 注入早于 batch, L949 调用 → 全 8 列在注入态计算, 单测/validation 无注入 → 同函数两套值; 失真与领域词密度 (核心 RHS 构念) 逐篇相关, 内生测量误差。P2 成立。

- **FIX-REGRESSION: completeness-02 的 FLS/复合词 jieba 注入反向破坏 forward-looking-jieba 修复 — frac_fls 生产环境漏判且注入态依赖**
  - 位置: `pipeline/sentiment/tone_words.py:820-831 (注入 _FUTURE_WORDS|_TIME_FUTURE_MARKERS 及 5 词典复合词) vs pipeline/sentiment/forward_looking.py:103-124 (_is_fls_sentence)`:forward_looking.py:111-124 · 单元: sweep-chinese-text
  - 裁决: 实证复现: _is_fls_sentence('公司提出了中长期目标') 注入前 True→注入后 False (token'中长期目标'吞掉 future 门控'目标'; forward_looking.py:121-123 兜底仅查 ≥3 字词, 2 字门控词无法补救)。tone_words.py:820-831 把 FLS 标记+词典复合词 add_word, 与 forward_looking.py:114-118 '不用 add_word 以免拆 token' 的修复设计正面冲突; 仅 tone_dicts+FLS 即实测 102 个吞噬型复合词。生产 frac_fls (L1071-1072) 在注入态计算且与单测态分裂, 真 FIX-REGRESSION。

- **FIX-REGRESSION (lmfls-01 不完整闭合): clarity_score、pos/neg_ratio、num_intensity_word 分母仍含标点+纯数字 token, 与已修 LM/FLS 口径分裂**
  - 位置: `pipeline/sentiment/tone_words.py:271-292 (_compute_clarity_for_text), 919-921 + 960-962 (pos/neg_ratio); pipeline/sentiment/numerical_intensity.py:267-276 (_count_word_tokens)`:tone_words.py:271-292 · 单元: sweep-chinese-text
  - 裁决: 代码坐实: lm_non_sentiment.py:128 已 _LMFLS_NONWORD_RE 过滤, 但同 _dual_analyze 内孪生分母未同步 — clarity (tone_words.py:271-285)、5 词典+全局 pos/neg_ratio (L919-921/960-962) 用含标点 len(tokens), _count_word_tokens (numerical_intensity.py:276) 无过滤且其 docstring (L268-272) 仍声称'与 lm_non_sentiment 口径一致、可横向比较'— 修复后已失真。同一论文 frac_uncert 与 clarity_score 分母口径不可比 (~19% 系统差), 与 lmfls-01 同型缺陷应同等定级, P2 成立。

- **stage 14 IDF 语料 (stage 12 AC 子串 DF) 与 TF (jieba 整词) 口径混用, 违反项目自身在 tone_words 已确立的同分词器原则**
  - 位置: `pipeline/filtering/fintech_intensity.py (_parse_global_df L99-128 用 AC 产物 DF; _compute_intensity_scores L285-301 用 jieba TF)`:99-128, 285-301 · 单元: sweep-chinese-text
  - 裁决: 实证复现: 同句 AC 命中 ['网贷'(子串于互联网贷款),'大数据','数据风控'(重叠双计)] vs 注入后 jieba TF 仅 ['数据风控'] — DF端3 vs TF端1。fintech_intensity.py:117-122 DF 来自 stage 12 fintech_keyword_details (news_fintech.py:144, 源于 analyze_fintech_matches AC 扫描无去重), L285-301 TF 走 jieba 整词 → 子串高发关键词 IDF 系统性偏低; 项目自身 tone_words.py:582-584 已为同问题废除 AC 子匹配, stage 14 未同步, 违反 GKT 同语料原则。台账'tone_words IDF改content_full'是语料列问题, 非重复。

- **ctx 轨窗口提取用裸 'alias in sent' 子串匹配, 不带 stage 11 的否定模式/短名消歧 — 分类与 ctx 物化口径分裂**
  - 位置: `core/text/entity_context.py (extract_entity_context L169-174, _char_level_fallback L206-221) + pipeline/text/ctx_materializer.py:126-127`:entity_context.py:169-174 · 单元: sweep-chinese-text
  - 裁决: 代码坐实: entity_context.py:169-174 裸 'alias in sent', _char_level_fallback L206-221 同; ctx_materializer.py:126-131 传 get_target_aliases 全变体含 2 字短名 (实测工商银行 variants 含'工行')。分类层同批别名有 252 否定模式+17 组短名排除 (工行 25 条如'施工行'), 证明假匹配语料真实高发, ctx 提取层全部失效 → 被排除的假命中句及其 radius 邻句污染 content_ctx; 跨行嵌套别名 (兴业⊂法国兴业) 同拉他行句; extract_entity_context_with_distances L264-279 同型。分类与物化口径分裂, P2 成立。

- **Bartik IV: 缺失 shift/缺失基期份额一律填 0 且权重不重归一 — 伪零 IV 注入 (与已修 peer_tone fillna(0) 同病根, 横切修复未覆盖)**
  - 位置: `pipeline/panel/iv_did.py`:248-256, 313-320, 379 (compute_bartik_iv / compute_bartik_iv_fintech) · 单元: sweep-valid-physical-denom
  - 裁决: 亲验 iv_did.py:248-256/313-320/379 属实; 盘上 174 行中 30-70 行基期 share 行和=0 → 7 族 bartik_*_iv 机械 0 且 n_nan=0。内部还自相矛盾: 有基期但零共现的银行得 own-group share=1 (L157-163), 无基期银行却全 0。与已修 netspill-peertone-fillna (network_spillover.py:271-283) 同病根, 修复台账仅含 'other' 分母, 未覆盖此处。

- **attention_attr_share clip(0,1) 把结构性 ctx>full 质量 (15% 单元) 右删失到 1.0, '归因纯度 share' 构念失真**
  - 位置: `pipeline/panel/attention_media.py`:332-334 · 单元: sweep-log-entropy-clip
  - 裁决: 实证坐实: 14_fintech_intensity 29% 篇 ctx>full(max比1.59), 24/157 bank-yr Σctx/Σfull>1(max 1.2227); 盘上 panel attr_share 14/122=11.5% 被 clip 到 1.0。fintech_intensity.py:341 长度归一 1+lnL 致 ctx 短文本 score 系统性超 full(非FP)。attention_media.py:333-334 clip 压平真实变异+乱排序, :202 _validate 声明值域(0,1) 故越界永不报警。机制变量删失失真。

- **log_sent_full/_ctx 对零覆盖 bank-year 产伪中性 0.0 (盘上 32% 行), 与同块 disag/均值类 NaN-mask 政策不一致**
  - 位置: `pipeline/panel/runner.py`:1623-1634 · 单元: sweep-log-entropy-clip
  - 裁决: 实证坐实(40_panel_yearly): n_articles==0 = 56/174=32.2%, 这些行 llm_vote_tone/dict_avg_tone/disag_llm 全 NaN, 唯 log_sent_full 全=0.0。runner.py:1631-1633 用 fillna(0) 无任何覆盖门控, 而同节 disag(:1596) denom→NaN 正确遮蔽。32% 伪中性零混入面板, 回归被错当真零保留而非 listwise 删。

- **deepseekv4 列在 .dta 标签中误标为 'Grok-4.1' — LLM 供应商归属错误**
  - 位置: `pipeline/panel/export.py`:702-703 · 单元: panel-export
  - 裁决: export.py:702-703 实读 'Grok-4.1 Confidence'; 单一事实源 sentiment.yaml:39-43 明确 deepseek-v4-flash 直连 api.deepseek.com; codebook.py:305 与 attention_media.py:31 同错; .dta 实读标签已固化。模型归属写进方法学文档, 属研究披露级错误, P2 成立。

- **LDA n_jobs=-1: 10 个 LDA 面板列的值是机器核数的函数 (random_state=42 不足以保证跨机复现, 实测 |Δθ|≈0.99)**
  - 位置: `pipeline/features/strategic_diff.py`:458-460, 1114-1116 (docstring 错误声称见 1079-1080); 同函数被 pipeline/features/policy_similarity.py:44 import 复用 · 单元: sweep-determinism
  - 裁决: 亲证 strategic_diff.py:458-460/1114-1116 n_jobs=-1; 本机 sklearn 1.8.0 复现 max|Δθ|=0.991 (nj1 vs nj2), 同nj重复=0.0; 实读 panel 10 LDA 列全在产; policy_similarity.py:44 复用坐实; 1079-1080 docstring '保证可复现性'与事实相反, 跨机 replication 不可复现, P2 成立。

- **六篇论文 Tables 2-5 esttab CSV 侧通道无生产者: 所有模板只写 .tex 且写入目录与 reader 不一致 → Python 表格层永久 FileNotFoundError**
  - 位置: `papers/benefit_society/tables.py (52-122) + brokerage_network/tables.py (56-74) + llm_peer/tables.py (54-72) + strategic_diff/tables.py (63-81) + bank_media_disagreement/tables.py:55 + bank_news_clarity/tables.py:55`:消费端如 benefit_society/tables.py:52; 生产端 papers/_common/stata_templates/**/*.do.tmpl · 单元: papers-derivative
  - 裁决: 全 95 模板 grep 'csv' 仅 README 命中, esttab 全写 .tex (llm_peer/11_table2:79); read_paper_esttab (stata_postprocess.py:312-322) 读 papers_assets/<id>/output/tables/*.csv 不存在即 raise。无 tex→csv 桥。已知'Stata Table 2 gap'=tech_frac_lf 幻影, 非同一缺陷。

- **EB shrinkage 两个方差分量均估错 → 收缩权重系统性偏低 ~5×, 与宣称的 Efron-Morris/James-Stein 最优不符**
  - 位置: `papers/benefit_society/shrinkage.py`:90-101 · 单元: papers-derivative
  - 裁决: shrinkage.py:91-100: grand_var(截面总方差)冒充文章级σ², between_var 含抽样噪声未减 σ̂²/n (缺 Morris MoM)。独立模拟复现: 实现权重 0.136 vs 正确 0.626; grand_var=0.229(真1.0), between_var=0.13(真0.04)。模块头:17 宣称 Efron-Morris 最优不符。

- **Table 9 维度分解 (PAP 冻结 H4 机制) 桥接缺失: merge_dimensions_to_panel 不存在 + 面板无 benefit_<dim>_* 列 + esttab 硬编码幻影 eststo 名必 r(111)**
  - 位置: `papers/_common/stata_templates/benefit_society/18_table9_dimension_decomposition.do.tmpl`:12-14 (虚构前置), 35-45 (capture 跳过), 65-66 (esttab 硬编码) · 单元: papers-derivative
  - 裁决: 全仓 grep merge_dimensions_to_panel 仅 18 号模板注释:13/43 自引; 面板零 benefit_{dim} 列; dimension_analysis.py:369 只写孤儿 parquet。模板:65-66 esttab D_core_op_full 等无 capture → 估计名不存在 r(111) 中止。*_shrunk 同样无桥(面板零 shrunk 列)已核。

- **bank_media_disagreement 主 treatment 同名异构: spec 规定全年 outlet 均值的 std, 盘上同名列实为 p90 事件窗内 outlet 方差的 n_outlets 加权年均**
  - 位置: `papers/bank_media_disagreement/paper_spec.yaml`:80-88 (primary_construction) vs pipeline/audit/cross_media_alpha.py:105-107, 187, 233 · 单元: papers-derivative
  - 裁决: paper_spec.yaml:86 = 无条件全年 outlet 均值 std; cross_media_alpha.py:105-107 p90 事件日+:140-144 ±窗口门控+:187 np.var(ddof=1)+:233 n_outlets 加权年均灌同名列(盘上36非空), tables.py:23 作 primary 进 Table 1。估计对象/矩/聚合三重不一致坐实; 已修 p90 项是另一缺陷。

- **block_subsampling_ci 实为 with-replacement 块自助 (block bootstrap), 非宣称的 Politis-Romano (1994) subsampling; 且块为位置切片, T>2/dropna 下与银行依赖结构错位**
  - 位置: `papers/_common/stats_helpers.py`:102-124 (实现); papers/benefit_society/figures.py:93-138 (消费) · 单元: papers-derivative
  - 裁决: stats_helpers.py:117 rng.choice(replace=True, size=n_blocks) 抽满 n = Carlstein/Künsch 块自助, 非 P-R 抽 b≪n 无放回+√(b/n)重标; docstring:71-73 与 figures.py:101-104/:132 均宣称 subsampling。:104 dropna 位置移位 + 全量不平衡面板下块跨银行 (latent), 方法标签错误当下即成立。

- **benefit_society Table 9 依赖不存在的函数 merge_dimensions_to_panel + 8 个幻影维度列, esttab 硬编码名 r(111) 被 master 的 capture 静默吞掉**
  - 位置: `papers/_common/stata_templates/benefit_society/18_table9_dimension_decomposition.do.tmpl`:12-14, 35-45, 65-66 · 单元: stata-templates-papers-b
  - 裁决: merge_dimensions_to_panel 全仓仅 18_table9:13/43 自引, pipeline/features/benefit_society.py 无此函数; 40_panel 实读 0/8 维度列(仅 mean/std/frac); 18:65-66 硬编码 D_core_op_full 等未 eststo 名→r(111); 00_master:36 capture do 吞错, H4 表静默缺失。

- **benefit_society 00_master 漏调 5/22 模板: spec 承诺的 A8–A11 + 主推断 wild bootstrap 11b 从不执行**
  - 位置: `papers/_common/stata_templates/benefit_society/00_master.do.tmpl`:26-40 · 单元: stata-templates-papers-b
  - 裁决: 目录实有 22 模板; master:26-40 仅串 15 项(声称 17 为小计数误, 不影响实质), 确无 11b/19/22/23/24; paper_spec.yaml:60-61/74-88 承诺 tA8+A9/A10/A11/WCB; 11_table2:81 表注引 boottest; analysis.py:91 还期待 22/23/24 产物; derivative_replication.py:312 glob 全实例化进包。

- **Wild cluster bootstrap 推断只活在 log 里: 三处 .tex/图注声称 WCB 推断, 实际星标/SE/CI 全是渐近 cluster, ctx 轨从未 bootstrap**
  - 位置: `papers/_common/stata_templates/benefit_society/21_tableA2_attitude_track_switch.do.tmpl`:104-106, 121-122 (另见 11b:50,62-63; 31_figure2:68) · 单元: stata-templates-papers-b
  - 裁决: 21:104-106 boottest 仅 display r(p) 且只 full 轨一条; 21:114-122 esttab 渐近 SE 却注 WCB; 31_figure2:57-69 coefplot 画渐近 CI、note:68 称 WCB; 11_table2:81 同注; 11b:50 normal() z 近似 vs reghdfe t(G-1) 口径不一; 11b:62-63 esttab deferred 且不在 master。

- **19_bs_num_intensity: 双轨同进一条 RHS (违反项目双轨纪律) + vce(cluster bank_id year) 与本篇自身 G_year 红线矛盾 + DV 未 winsorize**
  - 位置: `papers/_common/stata_templates/benefit_society/19_bs_num_intensity_robustness.do.tmpl`:22-23, 33-34 · 单元: stata-templates-papers-b
  - 裁决: 19:22-23 full+ctx 同进一 RHS, 违用户钦定'两轨分别进各自回归'纪律; vce(cluster bank_id year) 与 11b:8-9 'G_year=2 cannot cluster on year' 红线及 11-14 全单维 cluster(bank_id) 矛盾; 19:22/33 用裸 MAIN_DV 非 _w; 仅 19:20 守 full 列, ctx 无守卫(盘上两列在, 该点 latent)。

- **brokerage_network Table 5 R3 '剔除 singleton' 列与基线规格逐字节相同 (假稳健性列); Table 2 M3 注释虚称 over-identification**
  - 位置: `papers/_common/stata_templates/brokerage_network/14_table5_robustness.do.tmpl`:40-43 (另见 11_table2:35-37) · 单元: stata-templates-papers-b
  - 裁决: 14:41-42 R3 命令与 11:31-32 M2 逐 token 一致, 无任何 keep/drop/singleton/noabsorb 处理, mtitle 'Kept'(14:55)=假稳健列; 11:35-37 M3 的 L_btw/L_cons/L_broker 在 IV 括号外为外生控制, 仍 1 IV/1 endog 恰好识别, Hansen J 不存在。

- **Stage-18 staleness 特征面板聚合域 ≠ 面板样本域: 用 stage-13 预筛语料 (1170 篇/117 行) 聚合, 271 篇被 LLM 语义验证剔除的文章混入 64 个面板 bank-year 的 staleness 均值, 另 35/157 行被 left merge 静默丢弃**
  - 位置: `pipeline/text/article_staleness.py`:301 (src_path='13_news_with_ctx.parquet'), 290 (groupby 聚合); 配合 pipeline/panel/runner.py:1732 (left merge) · 单元: sweep-merge-integrity
  - 裁决: article_staleness.py:301 读 13_news_with_ctx, :290 groupby 聚合; 实测逐数复现: 313 篇不在 24_herd_decay, 271 篇属面板银行, 污染 64 bank-year (24 域恰 118 组, =54%); 18 面板 35/157 键被 runner.py:1732 left merge 静默丢; docstring 无设计声明。盘上活跃 (120/174 非空), 与兄弟列聚合域不一致且未披露。

- **runner 8c opt-in 特征 merge 无新鲜度/血缘守卫: 面板内容依赖 run 历史 — 现盘 40_panel_yearly (06-10 重生) 并入的 39f 文件 (06-03) 早于其自身上游 21_tone_llms 的重生 (06-06); 纯主链复现跑不出 paper-10 主处理列**
  - 位置: `pipeline/panel/runner.py`:1717-1736 (8c merge 仅 os.path.exists 守卫 + drop_duplicates keep='first'); 配合 pipeline/panel/export.py:256-259 (lineage 只记 24+15), run_pipeline_function.py:402-423 (陈旧清理只覆盖 METHOD_TO_PREDICATE 情感阶段) · 单元: sweep-merge-integrity
  - 裁决: runner.py:1720 仅 exists 守卫; :1726 先 dedup 使 :1733 行数守卫永不触发。mtime 实证 39f=06-03<21=06-06<panel=06-10, cross_media_alpha.py:250-252 确认读 21; 且 06-10 落地的 cross_media p90 修复未反映进盘上 39f → 面板 36/174 值确为陈旧代际。export.py:256-259 lineage 只记 24+15, run_pipeline_function.py:402-423 清理只覆盖情感族, 测试无新鲜度锁。盘上活跃。

- **guard-跳过 + 未守卫的具名 esttab → 单个可选块缺失即丢整表; 15_* 主回归表位于 master 未-capture 步 → enrichment 后 P2/P3 包仍整体中止 (N4 影响面外延)**
  - 位置: `papers/_common/stata_templates/bank_fintech_attention/15_attention_main_regression.do.tmpl`:76-93 · 单元: stata-templates-papers-a
  - 裁决: 亲验 attention/15:76-85 M6 守卫无 else-eststo, :87 esttab 无条件点名 M6; 00_master:30 未 capture; grep 全 repo post_E1 零生产者 (exogenous_shocks.yaml 实在 config/ 但无代码派生 panel 列, 实质不变)。次级站点 substance/15:70, collab/16:43, attention/19:65, locus/17:89, locus/18:94, substance/19:58, 20:77 逐一核实同构。系统性模式成立。

- **FIX-REGRESSION: st-did-05 修复 (2026-06-03) 传播不完整 — collab/17 字符串 bank_type 未加引号必崩 r(111); attention/17 + locus/17 SOE 切分引用幻影列 soe (实名 is_soe) 永久静默跳过**
  - 位置: `papers/_common/stata_templates/bank_fintech_collab/17_collab_heterogeneity.do.tmpl`:22-26 · 单元: stata-templates-papers-a
  - 裁决: 亲验: collab/17:24 `if {{HET_VAR}} == `lvl'` 无引号, HET_VAR=bank_type (derivative_replication.py:214), 实读 panel bank_type 为 str ['soe','joint'...]; attention/17:31-34, substance/17:29-34, locus/17:74-77 的 st-did-05 修复注释自证同 bug 已逐站修、漏 collab/17。attention/17:69 与 locus/17:59 `confirm variable soe` 引幻影 (实名 is_soe int64, substance/17:32-34 修复注释明诊)。两点全坐实。

- **四篇 15_* 主回归表 M5 "+macro" 列与 M4 完全相同 — CONTROLS 占位符默认值已含 gdp_growth/m2_growth, 重复加入被 reghdfe 静默 omit**
  - 位置: `papers/_common/derivative_replication.py`:176-177 (同 186-187/199-200/210-211) · 单元: stata-templates-papers-a
  - 裁决: 亲验 derivative_replication.py:176-177/186-187/199-200/210-211 四篇 CONTROLS 均含 gdp_growth m2_growth; attention/15:62-66, substance/15:48-52, locus/15:49-53, collab/15:49-53 M5 再加同名 → reghdfe 重复 regressor 静默 omit (标准行为) → M5≡M4; else 分支 (宏观缺) 也明写复用 M4。两路径下 M1→M6 渐进设计与列标均名存实亡, 四篇 Table 2 受累。

- **双轨稳健性死代码: locus/18 alt_ctx 引用从未派生的 locus_layer_ctx/locus_scenario_ctx, substance/18 引用幻影 innovation_substantiveness_ctx — panel 上 ctx 孪生 (_lc/_sc) 实际存在却未被消费**
  - 位置: `papers/_common/stata_templates/bank_fintech_locus/18_locus_robustness.do.tmpl`:76-81, 94 · 单元: stata-templates-papers-a
  - 裁决: 亲验: locus/01:40-43 仅派生 _full 对, locus_layer_ctx 全 repo 无派生点; 实读 panel: 四个幻影名全 MISS, ctx 真孪生 tech_frac_lc/app_frac_lc/sub_frac_sc/symb_frac_sc 全 OK 且无模板消费; locus/18:76 守卫永假→:94 esttab 无条件点名 alt_ctx→Table 5 整丢; substance/18:76-83 同构永跳; collab/18:20-33 用对真名 (indep_frac_cm 等 OK) 反证可得性。无条件死代码, 非 enrichment 可治。

- **P3/P4/P5 spec 主 treatment 声称 "pipeline 实际列名" 实为文章级中文分类字符串, panel 0 命中, 派生列零实现, gap 公式对字符串做算术 (N4 的 spec 层清点)**
  - 位置: `papers/bank_fintech_substance/paper_spec.yaml; papers/bank_fintech_locus/paper_spec.yaml; papers/bank_fintech_collab/paper_spec.yaml`:substance:35-38; locus:39-45; collab:47-54 · 单元: paper-spec-crosscheck
  - 裁决: 亲验: 两panel 0/8命中; 21_tone_llms三列=str中文标签; P3:38/P5:53对字符串做算术; P3/P5 01_data_prep exit 198; locus figures.py:26-28读幻影列。唯locus_layer在locus/01_data_prep.do.tmpl:41-43有Stata派生(tech_frac/app_frac), '零实现'稍过宽, 主旨成立。

- **P1 主 spec 与主模板方向反转: spec 称 tone 为 treatment→CAR outcome, 实际 Table 2 模板把 llm_vote_tone 当 DV 回归到 digital_frontier 上**
  - 位置: `papers/bank_fintech_tone/paper_spec.yaml; papers/_common/stata_templates/11_table2_main_m1m6.do.tmpl`:spec:21,30 vs tmpl:4,55,82-110 · 单元: paper-spec-crosscheck
  - 裁决: 亲验tmpl:55/82 reghdfe llm_vote_tone_* digital_frontier=tone作DV; spec:21/30反向; stata_runner.py:238-243证根模板不消费MAIN_TREAT; 全审计产物无此前记录, 台账'Table 2 gap'实指BW2012/attention实例, 非本反转; spec/模板均无披露注。

- **bank_media_disagreement 主 treatment 同名异构: spec 标 "待新建" 但 panel 已有同名列, 且 39f 实现公式与 spec 冻结构造实质不同 (事件窗方差加权均值 vs 全年 outlet 均值的 std)**
  - 位置: `papers/bank_media_disagreement/paper_spec.yaml; pipeline/audit/cross_media_alpha.py`:spec:80-99 vs cross_media_alpha.py:6,37,187,213-239 · 单元: paper-spec-crosscheck
  - 裁决: 亲验: spec:80'待新建'+84-86构造=全年outlet均值std; cross_media_alpha.py:187 np.var(ddof=1)事件窗+:220按n_outlets加权+:233落同名列; 两panel两轨命中+stata_export.py:344导出; docstring:6-8/37自称第10篇main treatment, 同名异构(var vs std/事件条件vs全覆盖)坐实。

- **bank_news_clarity 主 treatment 聚合权重声称错误: spec 写 w_i=mention_density, 实现是 media_authority_weight × herd_weight_{track}**
  - 位置: `papers/bank_news_clarity/paper_spec.yaml; pipeline/panel/encode_collab.py`:spec:98-100 vs encode_collab.py:509-521 · 单元: paper-spec-crosscheck
  - 裁决: 亲验encode_collab.py:509-521 _track_weight=media_authority_weight×herd_weight_{track}(缺失回退1); mention_density在encode_collab.py全文件0命中; spec:98-100以'现成 L467'断言错误权重 — 主treatment冻结构造描述错误坐实。

- **P1/P2 spec 声明的 IV 标识符全管线零实现: leave_one_out_industry_tone / leave_one_out_peer_attention_iv / bartik_attention_iv 无 builder 无 panel 列; P1 现行 IV 表实际工具化的是 LOCUS 而非 tone**
  - 位置: `papers/bank_fintech_tone/paper_spec.yaml; papers/bank_fintech_attention/paper_spec.yaml`:tone:50; attention:49-51 · 单元: paper-spec-crosscheck
  - 裁决: 亲验: leave_one_out_industry_tone仅spec:50+派生文档, 0 builder/0 panel列; 根14模板唯一IV表22_tableA3:60/73 ivreg2工具化LOCUS(tech_frac)非tone; attention spec:49-51无pending注而19_attention_iv:30-60 capture confirm跳过; panel bartik族无bartik_attention_iv。

- **主线 13_table4: bank_size 缺失时 HET1 eststo 被守卫跳过但 esttab 无守卫 → r(111) 'HET1_large not found' 硬崩, master 链死于 Table 4, 后续 8 个模板永不执行**
  - 位置: `papers/_common/stata_templates/13_table4_heterogeneity.do.tmpl`:28-38 (HET1 守卫) vs 60-66 (esttab 无守卫) · 单元: stata-templates-mainline
  - 裁决: 13_table4:28-38 守卫 HET1, :60 esttab 硬引 HET1_large 无 capture; bank_size 实测在 46core/46full/51 全缺; 00_master:29 do 无 capture; 本机 Stata 实证 esttab 缺名 _rc=111 → 链死, 14/20-24/30/31 共 8 模板不执行; 与 11_table2:95-104 else 降级写法不一致。

- **21_tableA2 + 31_figure_coefplot: 8-spec 循环用幻影列名 tech_frac_lf/symb_frac_sf → 6/8 spec 永不可估, 且 esttab/coefplot 硬编码 8 个名字无守卫 → r(111) 崩; correctness-04 裸名重映射修复漏掉这两个模板**
  - 位置: `papers/_common/stata_templates/21_tableA2_main_spec_switch.do.tmpl`:39-59 (循环), 62-65 (esttab); 31_figure_coefplot_dual.do.tmpl:12-39 (同病) · 单元: stata-templates-mainline
  - 裁决: 21_tableA2:43-44 直拼 tech_frac_`loc'; 实测 tech_frac_lf/symb_frac_sf 全缺, 裸名+_lc/_sc 在→含 lf/sf 的 6 spec 被 :48 confirm 跳过; :62-65 esttab、31:32-39 coefplot 硬引 8 名, 本机实证均 r(111); 裸名重映射(correctness-04)仅修 11_table2:58-71, 漏此二模板。

- **12_table3: M4 守卫跳过 + esttab 无守卫 + 无 eststo clear → Table 2 的陈旧 M4 估计静默泄入 Table 3 第 4 列 '+ Controls' (错误模型冒充机制回归)**
  - 位置: `papers/_common/stata_templates/12_table3_mechanism.do.tmpl`:51-55 (M4 守卫) + 58 (esttab); 根因: 全部主线模板无 eststo clear · 单元: stata-templates-mainline
  - 裁决: 12_table3:51-55 M4 守卫(bank_size/bank_age 实测全缺)跳过, :58 esttab 无守卫; grep 证 papers/_common/stata_templates 全树零 eststo clear; 本机实证: esttab 同名陈旧估计 rc=0 静默复用、缺名 r(111)→L57 注释为假; master 链中 11_table2 必存 M4→泄入 Table 3 第4列。

- **14_table5 四连缺陷: (a) `eststo MAIN_BOOT: estimates store` 语法错 r(100) — boottest 已安装时 5d 整块中断; (b) leave-one-out 'n_stable' 无条件自增, 表注 'X/Y consistent β' 是恒真假统计量; (c) placebo 声称'随机置换保数量'实为 iid 重抽; (d) T=2 下 5b 子样本 0 obs r(2000) 崩**
  - 位置: `papers/_common/stata_templates/14_table5_advanced_robustness.do.tmpl`:69 (a); 53-62+85 (b); 29-39 (c); 43-49 (d) · 单元: stata-templates-mainline
  - 裁决: (a):69 本机实证 r(100) name required, 在 :66 which boottest 通过分支内无 capture→装包反致中断; (b):55-62 n_stable 无条件自增、b_coef 弃用、:85 恒 100%; (c):35 逐 obs iid runiformint 非置换, bysort 无 stable; (d)实测 years=2017/2018→:46 year<2017 零 obs r(2000), T=19 不触发。

- **20_tableA1: bank-year 级 inter-track 相关性 confirm 引用幻影列 tech_frac_lf/sub_frac_sf → 永远失败, Locus/Subst 两行 ρ 恒为缺失 — 双轨设计核心效度证据表实际永远空表**
  - 位置: `papers/_common/stata_templates/20_tableA1_inter_track_kappa.do.tmpl`:56-66 (幻影 confirm), 83-92 (空 .tex 输出) · 单元: stata-templates-mainline
  - 裁决: 20_tableA1:56 confirm 含幻影 tech_frac_lf/sub_frac_sf(实测缺)→多变量 confirm 任一缺即 _rc≠0→:64-65 corr_locus/subst 恒'.'; 正确列 tech_frac/sub_frac/_lc/_sc 均在产(174行)却从未计算; :88-90 空 macro 内插入 .tex; 篇章级 κ 依赖缺失 21_tone_llms.dta(:20 已披露), 仅 collab ρ 可算。

- **papers 10/11 两篇 01_data_prep 共有恒真条件 `"total_assets" != ""` → 在管道正典 49 输出上必执行 `gen ln_assets = ln(total_assets)` 而 total_assets 变量不存在 → 数据准备阶段即 r(111)**
  - 位置: `papers/bank_media_disagreement/stata_templates/01_data_prep.do.tmpl`:44-47 (同病: papers/bank_news_clarity/stata_templates/01_data_prep.do.tmpl:27-30) · 单元: stata-templates-mainline
  - 裁决: 01_data_prep:44-46(clarity :27-30 同病); 本机 Stata 实证: 字面量比较走 true 分支 + gen ln(total_assets) 缺变量 _rc=111; 正典 49 输出 13 列无 ln_assets/total_assets, 且 :36 merge keepusing 不带 ln_assets→必崩于数据准备; fixture 已含 ln_assets 故首 confirm 通过才侥幸不触发。

- **22_tableA3: IV 列 (ivreg2) 完全无固定效应, 与同表 OLS 对照列 absorb(bank_id year) 规格不对称 — OLS-vs-IV 对比失效且 Bartik IV 未控年份共同冲击**
  - 位置: `papers/_common/stata_templates/22_tableA3_bartik_iv.do.tmpl`:60-61, 73-74 (ivreg2 无 FE) vs 78 (OLS reghdfe absorb(bank_id year)) · 单元: stata-templates-mainline
  - 裁决: 22_tableA3:60-61/:73-74 ivreg2 调用串无 absorb/partial/i.bank_id/i.year(ivreg2 本不支持 absorb, 需 ivreghdfe 或哑变量); :78 OLS reghdfe absorb(bank_id year); :81 esttab 同表三列对比; :89-93 脚注仅披露 KP F 未披露 FE 不对称; Bartik shift 逐年变动, 无 year FE 时共同冲击入残差, GPSS2020 框架下对比不可归因。


## 3b. P2 确认 — latent (T=19 触发, 13 条)


- **银行关键词保留过滤在文本规范化之前执行, 且 8223 关键词 0 个繁体变体 — 混合文字/OCR 噪声源文章被静默丢弃 (latent, 全量语料)**
  - 位置: `pipeline/preprocess/load.py:120-129 + pipeline/preprocess/filter.py:98-110`:_process_single_file 处理顺序: _clean_and_filter_dataframe → clean_text_batch · 单元: preprocess · ⚠latent
  - 裁决: 缺陷真实: load.py:120过滤先于:129规范化,filter.py:102对原始内容AC匹配,8223词0繁体(亲测),AC仅lower(load.py:55,70),'联合银行(中国)'全角形态0词命中(亲测);但实测Wisers地区值='香港'非'中国香港'→繁体源步1按设计排除,主放大通道不存在;盘上切片仅2017-18清洁期,OCR/全角/mojibake通道仅全量2007-2025 latent,量级窄→P2降P3

- **批级推理异常把整批 200 篇 × 全部模型静默置为 '中性'+全 0 概率哨兵, 与空文本不可区分且下游无过滤**
  - 位置: `pipeline/sentiment/tone_berts.py`:605-612 (_empty_result), 648-654 (except 兜底), 883-892 (num_windows 写盘) · 单元: tone-berts · ⚠latent
  - 裁决: 代码坐实: tone_berts.py:648-654 except Exception 整批×全模型覆盖 _empty_result(L612: 中性+全0概率+num_windows=0)仅 warning; encode.py:528-537 prob 全物理域 mean/sum, L1458 明示 BERT prob=0 不改→哨兵直进聚合, 无失败 flag, 与空文本共用 num_windows=0。盘上实测无哨兵(prob-sum min=1.0, num_windows min=1), 18.2M 全量 GPU 瞬态故障即触发→latent。

- **stage 18 盲目按位置对齐 stage 30a 嵌入: 无 article_id join/长度断言/模型版本 provenance**
  - 位置: `pipeline/text/article_staleness.py`:331-341 (消费); article_sbert.py:170-179 (产出) · 单元: staleness-sbert-embed · ⚠latent
  - 裁决: 代码属实: article_staleness.py:333-341 直接 np.stack 按行位传入, 零键校验; 30a 已写 article_id/日期 (article_sbert.py:171-175) 却未消费, 无 model_id 元数据。盘上恰 1170==1170 对齐不触发; 全量下 30a 为 4-6h 手动 stage 而 stage 13 频繁重生, 陈旧+等长时静默整列错位不可见 → latent P2。

- **policy_cosine_sim 全 NaN 时 7h-token 四象限静默把全部高词频文章归入 Token — 由零测量制造出非 NaN 面板值 (latent)**
  - 位置: `pipeline/panel/runner.py`:1288-1316 · 单元: policy-alignment-similarity · ⚠latent
  - 裁决: 代码坐实: 三条早退路径合法写全 NaN parquet(policy_alignment.py:445-457,570-572); runner 仅对文件缺失 fail-loud(1184); 全 NaN 年 quantile→NaN, `>=NaN`→False(1297), _is_token=_high_freq(1299-1300), 与 L1324-1332 NaN 契约矛盾。盘上 policy_cosine_sim 0 NaN 未触发 → latent。

- **面板年份早于基期 T0 时 share 前视 (latent, T=19 触发)**
  - 位置: `pipeline/panel/iv_did.py`:L116, L180 (merge 仅 on target_bank, 无 year≥T0 掩码); 配合 runner.py L663-665 · 单元: iv-did · ⚠latent
  - 裁决: 代码属实: iv_did.py:180 与 L318 仅按 target_bank merge/map, 无 year≥T0 掩码; runner.py:665 T0=max(panel_min,2010)。盘上 panel_min=2017→T0=2017 不触发; 全量 2007-2025 下 T0=2010, 2007-2009 行将携带 2010 年测得 share 与同期 shift 相乘出非 NaN BIV — share 由未来数据测得, GPSS 预定外生性论证对这些行失效。函数内无守卫/警告, 真实 latent 缺陷。

- **名称归一化级联可把泛称/表外银行错配到任意银行: 泛串 '农村商业银行' 命中 1558 家取最长名, difflib 0.8 把农发行错配为农业银行**
  - 位置: `pipeline/panel/llm_peer_iv.py`:443-456 (_normalize_peer_names 策略3/4) · 单元: llm-peer-iv · ⚠latent
  - 裁决: L443-456 亲验: 泛称'农村商业银行'子串命中 1558 规范名, max(key=len) 任取'内蒙古察哈尔右翼前旗农村商业银行'; 农发行不在 bank_names.json, difflib ratio=0.857≥0.8 错归中国农业银行 — 缺陷真实(无歧义守卫/无 OOV 拒绝)。但实读 _llm_cache 全部 73 条 peer 响应 70 唯一名: 策略3歧义/策略4 difflib 零触发, 盘上 T=2 未实际污染; T=19 海量 bank-year 调用下泛称/政策行输出大概率出现 → latent。

- **stock 类季度聚合每列独立取'最后可得季度' — 比率分子分母可来自不同季度 (rwa/TA、NPL/loans、LLP/loans 测量日错配) (latent)**
  - 位置: `pipeline/panel/risk_taking_outcomes.py`:117-124 (aggregate_quarterly_to_yearly stock 路径) → 329-336 (rwa_to_ta/llp), 214-218 (npl formation) · 单元: risk-taking · ⚠latent
  - 裁决: risk_taking_outcomes.py:121-123 `g.ffill().iloc[-1]` 逐列独立取末个非NaN季度。实测 rwa=[50,52,NaN,NaN]/TA=[100,104,108,112] → rwa=52(Q2)/TA=112(Q4)=0.4643, 同期一致值0.5, 增长银行系统性向下偏。同机制污染 npl/loans、LLP/loans 口径。盘上 49 输出 0 行不触发, 全量季度参差缺失下高频触发 — latent P2 坐实。

- **季度→年度聚合假设单季流量/时点比率, 与数据源 YTD 累计口径及 PDF '全年值记 Q4' 路径冲突 — writeoffs 年和可高估约 2 倍, ROA 年均值混口径 (latent)**
  - 位置: `pipeline/panel/risk_taking_outcomes.py (+ scripts/data_acquisition/banking_outcome_dry_run.py)`:129-146 (intensive mean / flow sum); dry_run 脚本 442-449 (PDF 年报值 quarter=4), 210-241 (Wind 季末取数) · 单元: risk-taking · ⚠latent
  - 裁决: 代码坐实: aggregate L139-144 flow 无条件 sum(min_count=1); dry_run L445 PDF 年报值打 quarter=4, L466-484 级联允许同年 Wind Q1-Q3 + PDF Q4 混源 → 全年累计值与季度值直接相加; 模块不读 data_source、无 de-cumulation 守卫。中国银行季报核销/利润惯例 YTD (Wind 季末报表值) 下 sum 高估 ~2x 灌入 npl_formation 分子。盘上 0 行不触发 — latent P2。

- **llms_evaluation 金标准情感评估把 LLM 调用失败/平局行 fillna('中性') 伪造成中性预测, 污染报告的 F1/Accuracy 且双轨不对称**
  - 位置: `validation/llms_evaluation.py`:1390, 1429 (fillna('中性')); 1391, 1430 (np.where 非法标签→'中性') · 单元: sweep-fillna-weights · ⚠latent
  - 裁决: llms_evaluation.py:1390-1391/1429-1430 现场属实; 实测 21_tone_llms NaN=24(full)/79(ctx)/857, 32_human_samples.xlsx 1000 行含 285/335 NaN 行→一旦评估必污染且双轨不对称。但盘上人工金标 (编码者A_情感) 1000/1000 全空→gold_sen_col 缺→当前走 demo 模式未产真报告, 故 latent。与 tone_validation.py:188-198 已修同类 NA 语义相悖。

- **EB shrinkage 收缩目标在全年份 pooled 组均值上计算 (无 year 维度/无 LOO), 含未来年份信息的 shrunk 列直接进 Table 8/8b 回归 RHS**
  - 位置: `papers/benefit_society/shrinkage.py`:78-101 (empirical_bayes_shrinkage), 157 (group_cols) · 单元: sweep-insample-leakage · ⚠latent
  - 裁决: shrinkage.py:157 group_cols=(bank_type,bank_province)无year; L78-91 组均值/grand_var pooled全年份; L100权重随n_obs时变不可被FE吸收; 17_table8:36/17b:42确为RHS。但盘上无benefit_mean_full_shrunk列且40_panel_yearly_shrunk.parquet不存在, 模板capture confirm优雅跳过→缺陷真实但盘上未落, 全量跑shrinkage CLI即触发。

- **iv_did 三处 LOO/Bartik 在 float64 转换【之前】做 Int8−Int8 减法 → 静默回绕可致 IV 符号翻转 (latent)**
  - 位置: `pipeline/panel/iv_did.py`:232, 364, 479 (根源 202-211 / 340-348 / 460-466) · 单元: sweep-int-overflow · ⚠latent
  - 裁决: 亲验 iv_did.py:232/364/479 减法均先于 astype。pandas 3.0.3 实测: masked Int8 groupby sum 按值降型 (sum=100 保持 Int8, 行231注释前提为假); Int8−Int8 静默回绕 (100−(−100)=−56); 端到端逐行同代码复现 LOO 期望 +1.0 实得 −0.969 完整符号翻转零警告。盘上实测 (encode.py:139 Int8 源, bank 和 max 113/总和 796) zone年总和升 Int64 混型减法安全 → 当前不触发, latent 成立。触发窗=稀疏组年全列和落 ±127 且余数越界 (子样本/早年稀有类别)。非台账重复 (台账仅 stata_audit Int8 与 **2 回绕)。

- **semantic_staleness 跨文件纯位置对齐: stage 18 把 30a SBERT embeddings 与 13 号文章表按行位置缝合, 无 article_id 键 join、无长度断言 (键列存在但被忽略)**
  - 位置: `pipeline/text/article_staleness.py`:332-341 (np.stack emb 列 + 直接传入), 217-219 (embeddings[sort_idx] 按 art_df 的 argsort 索引) · 单元: sweep-merge-integrity · ⚠latent
  - 裁决: article_staleness.py:333-341 np.stack 直传, :217-219 embeddings[sort_idx] 按 art_df argsort 位置索引; 实读 30a schema 键齐备 (article_id/target_bank/日期) 但未用, 无 len 断言。mtime 13=06-05 vs 30a=06-08 已跨 run 配对, 当前 1170==1170 同源一致 → 缺陷真实但盘上未触发; 同行数错配时静默错向量。对照 encode_collab.py:224 有键对齐惯例。

- **collab 开/闭二元 dummy 对设计缺陷 (latent): 缺失值落入 both-0 幻影参照组、非缺失时 open+closed≡1 完全共线 → test open=closed 退化**
  - 位置: `papers/_common/stata_templates/bank_fintech_collab/01_data_prep.do.tmpl`:36-38 · 单元: stata-templates-papers-a · ⚠latent
  - 裁决: 亲验 collab/01:36-38 `gen =(mode==1)/(mode==0)` 无 !missing() 守卫 (Stata missing→两 dummy 均 0, 标准语义); master:7 自述 byte 0/1 → 非缺失时 open+closed≡1 与 FE 完全共线, reghdfe 静默 omit → collab/15:69 `test open=closed` 退化为 β=0。locus/01:41-43 正确版 (含 !missing + 平局参照组注释) 同 repo 未复用。盘上因 idx0 死锁 exit 198 该代码不可达 → latent。


---

## 4. P3 确认 (119 活跃 + 54 latent) — 按单元归组


**stata-export** (11):
- KNOWN-OPEN-STATUS: ⑥ pyreadstat Int8∈[101,126]→扩展缺失 — 仍未修, 但当前因 pyreadstat 未安装而休眠; 实测 Int8 已压满 byte 合法上限 (max=100, 零余量) `pipeline/panel/stata_export.py`
- build_variable_labels 标签截断: 字节判定+字符切片不一致, CJK 标签『越截越长』, 触发自家 validate 门 → stage 46 硬崩 (latent) `pipeline/panel/stata_export.py`
- 双 backend 产物不等价且选择随环境静默漂移: 正式依赖含 pyreadstat 但本机未装 → 盘上交付 .dta 实为 fallback 产物; fallback 自我设限不传 value_labels (pandas≥1.4 已支持) `pipeline/panel/stata_export.py`
- 模块 docstring 承诺 'NaN → . / .a / .b extended missing for distinguishable causes' 但全文件零实现; encode 的 .map() 把未知类别静默合流进同一 NaN `pipeline/panel/stata_export.py`
- 改名后元数据同步不对称: value_labels 键只跟 asciify 改名同步、不跟 shorten_long_column_names 同步; build_variable_labels 不接收 rename_map → 改名列标签查找必 miss (latent) `pipeline/panel/stata_export.py`
- labels.do 引号转义用 "" 加倍非 Stata 合法转义 (需 compound quotes); 双引号串内 $ 触发 global macro 展开 — 含特殊字符标签被 capture 静默丢弃 (latent) `pipeline/panel/stata_export.py`
- 变量标签截断按字符切片但限额按字节校验 — 多字节标签'截断后'仍超限 (甚至变长), validate_stata_compat 必然 raise → stage 46 崩溃 `pipeline/panel/stata_export.py`
- 列名缩短发生在 core 分配与标签查找之前 — >32 字符的 core_patterns/HEURISTIC_LABELS 键按构造不可达; collab confidence 双轨截断后 32 字符前缀相同, 首列彻底丢失 _full 轨后缀 `pipeline/panel/stata_export.py`
- 模块头声称 'NaN → . / .a / .b (extended missing for distinguishable causes)' — 两条后端均未实现, 全部缺失原因不可区分地写成 '.' `pipeline/panel/stata_export.py`
- encode_categorical_columns 用 .map() 静默 NaN 化一切未登记类别值, 无未匹配计数校验; 且整套类别编码+value-label 机制在当前 bank-year panel 上是死路径 `pipeline/panel/stata_export.py`
- shorten_long_column_names 的去重集合 used 未预载全部列名 (姊妹函数 asciify 有预载) — 截短名可抢占后续真实同名列, 造成列身份错配 `pipeline/panel/stata_export.py`

**codebook** (9):
- FIX-REGRESSION: attention_index '≠Hassan intensive' 引文修复未传播到 codebook — _ATTN_TREAT 块仍以 Hassan 2019 QJE 为族级锚点引用 `pipeline/panel/codebook.py`
- curated source_stage 错置: bank_degree_cent 标 'Stage 46' (现 DAG stage 46=stata_export), 自动推断规则把 attn→Stage 24、network/cent→Stage 46 系统性错标 `pipeline/panel/codebook.py`
- track 字段编码不一致: v3.2.0 块把 track 赋为中文 '全文'/'上下文', 与全卷标准 'full'/'ctx' 混用 (产物中 4+4 行), 另 '—' 与 '' 两种空值并存 `pipeline/panel/codebook.py`
- 盘上 codebook 产物无法由文档化入口复现: scripts/generate_codebook.py 读 40_panel_yearly, 但产物实际生成自 51_panel_with_controls `scripts/generate_codebook.py`
- 13 个 curated 元数据条目永远无法进入 codebook 产物 (article 级列名, 不存在于 bank-year panel), 且其 '0|1 编码' 取值范围声称与 parquet 实际字符串值矛盾 `pipeline/panel/codebook.py`
- _infer_source_stage 把 'attn' 映射到 'Stage 24', 与本文件自己 2026-06-02 审计更正注释直接矛盾 — ft_attn_prov/ft_attn_city 在产物中带着已被推翻的来源声称 `pipeline/panel/codebook.py`
- Excel 列宽设置用 chr(64+idx) 生成列字母 — 仅支持 A–Z (26 列), 当前 codebook_df 恰为 25 列, 任何新增统计列将产生非法列名 '[' 致 xlsx 生成崩溃 (latent) `pipeline/panel/codebook.py`
- 声称的 prob_score 标准差取值范围 [0, 0.5] 与 ddof=1 样本标准差实现矛盾 — 盘上实测 0.5292 已越界 `pipeline/panel/codebook.py`
- target_bank 取值范围声称 '42家商业银行' — 盘上实际 87 家, 产物同一行内自相矛盾 (唯一值数=87) `pipeline/panel/codebook.py`

**panel-export** (7):
- 双轨重命名后 STATA_LABELS 残留陈旧键 — herd 权重与 fintech Bartik IV 活跃列在 .dta 中无标签 `pipeline/panel/export.py`
- 约 50 个 Bartik 稳健性 IV 标签为纯幻影 — 全仓无任何生产代码 `pipeline/panel/export.py`
- leave1out_dict 列 33 字符截断致 .dta 内双轨命名不对称, 且 geography 推荐的 Stata IV 命令引用不存在的列名 `pipeline/panel/export.py`
- 40_panel_yearly.dta 59.8% 列无变量标签, 含主回归 DV llm_vote_tone_full/_ctx `pipeline/panel/export.py`
- t2v 标签 '与 stata_export.HEURISTIC_LABELS 同源/口径一致' 的注释声称不实 — 2 对标签文本不同 + 1 个 ctx 键单侧缺失 `pipeline/panel/export.py`
- ai_reg_* 标签 'AI Imitation Rate' 构念误称 — 实测度为区域同行 fintech 新闻覆盖渗透率, 与 AI 无关 `pipeline/panel/export.py`
- low_conf_flag 由诊断函数副作用式条件创建 — 数据依赖的 schema 漂移 (latent) ⚠latent `pipeline/panel/export.py`

**tone-llms-parsing** (6):
- 200 成功路径无响应内容校验: 空串/截断响应被 cache.put 永久冻结为合法命中 `pipeline/sentiment/tone_llms.py`
- fix(tonellms-01) 双轨对称声称失真: full 轨 0.6% 双标题注入 + _strip_prepended_title 非 prepend_title 精确逆 + 双路径 ctx 构造分歧 `pipeline/sentiment/tone_llms.py`
- LLM raw response 归档账本对生产语料覆盖为空: archive ⊉ cache 结构性成立且无 backfill 工具, manifest 从未写出 `pipeline/llm_archive/__init__.py`
- manifest prompt_sha256 sidecar 读取仍是 cwd-相对路径 (audit S3 同类路径漂移残留) `pipeline/llm_archive/manifest.py`
- LLM 禁用分支输出 schema 缺 avg_collab_prob_score 双列, 且 llm_prob_score 占位 0.0 与启用分支 NaN 语义冲突 ⚠latent `pipeline/sentiment/tone_llms.py`
- 无效 confidence 政策三类 vs 二类不一致: 3-class 静默 clip 且 NaN→满置信 1.0, binary 则 NaN-reject ⚠latent `pipeline/sentiment/tone_llms.py`

**strategic-diff-measures** (6):
- LDA n_jobs=-1 → E-step 切片数随机器核数变化, theta 跨机浮点漂移, 与代码自称'保证可复现性'矛盾 `pipeline/features/strategic_diff.py`
- LDA 主题数 K=max(10,n//30) 实为硬编码 10 (n//30 在 ~54 银行下恒 <10), 无任何数据驱动选择或 K 敏感性; 两处 K 公式基数不一致却注释声称'一致' `pipeline/features/strategic_diff.py`
- 契约别名 strat_diff_t2v_{full,ctx} 实为 centroid 测度的逐值复制列, 但命名/Stata 标签暗示 N-NN 战略差异度; 且与退役 stage 30 同名列构造域已变 (文章级质心均值 → 银行年文档质心) `pipeline/features/strategic_diff.py`
- _compute_nn_scores 相似度路径 clip 同类删失扩展到 N-NN emb 族 (⑦ 同病根、不同函数), 注释误称仅为 1e-7 FP 容忍 ⚠latent `pipeline/features/strategic_diff.py`
- coh_emb*/coh_emb_t2v* 是未 clip 的原始余弦 (可负), 但 _log_coherence_diagnostics 断言 ∈[0,1] — latent 生产期 AssertionError 崩 stage 45 ⚠latent `pipeline/features/strategic_diff.py`
- N-NN 在 |peers|<N 时静默降级 k=min(N,|peers|): 低覆盖年份 n3..n7 五列塌缩同值, 制造虚假的 N 敏感性稳健 (latent) ⚠latent `pipeline/features/strategic_diff.py`

**papers-mainline** (5):
- P1 tone Figure 1 静默剔除 32% 零覆盖 bank-year 后再画 log1p 覆盖分布 `papers/bank_fintech_tone/figures.py`
- locus_gap / collab gap 文档声称 ∈ {-1,+1}, 实际推导含 0 (平票/缺失) `papers/bank_fintech_locus/__init__.py`
- P1 Table 1 与 frozen spec 主轨不对齐: 连续分与 IV 仅列 full 轨, 而 spec 主回归 = ctx 轨 (ctx 列盘上已存在) `papers/bank_fintech_tone/tables.py`
- parse_esttab_csv 两处 latent 解析缺陷: 科学计数法截断取值 + 重复变量名行静默覆盖 `papers/_common/stata_postprocess.py`
- KNOWN-OPEN-STATUS: Table 2 declared-vs-implemented gap (台账④) — 现状核实: gap 仍开放且延伸到 papers 层 docstring `papers/bank_fintech_attention/tables.py`

**tone-llms-voting** (5):
- 逐模型 {short}_prob_score_{full,ctx} 列对失败模型默认写 0.0/'P3', 与真实零置信中性同值 (title 轨 H1 同类缺陷未延伸到 full/ctx) `pipeline/sentiment/tone_llms.py`
- 行级创新置信度 _avg_conf 聚合域与标签聚合域不匹配 — 标签为 null/被拒模型的置信度仍计入均值 `pipeline/sentiment/tone_llms.py`
- HTTP 200 空字符串响应被无验证缓存并永久冻结为伪 False 票, 缓存命中后永不重试 (盘上 1 例) `pipeline/sentiment/tone_llms.py`
- compute_prob_score 对 NaN confidence 静默映射为满置信 c=1.0 (latent) ⚠latent `pipeline/sentiment/tone_llms.py`
- 双路径 content_ctx 语义分歧: stage 21 备援物化不 prepend 标题、不产 content_full, 违反其自称的'双路径同语义'不变量 (latent) ⚠latent `pipeline/sentiment/tone_llms.py`

**strategic-diff-panel** (5):
- _compute_fluidity 的 TF-IDF 漏 sublinear_tf=True — 与同文件 sim 矩阵/coherence 家族不一致, 注释却声称"保持一致" `pipeline/features/strategic_diff.py`
- lazy_minedit 按聚合文档前 2000 字前缀计算且前缀依赖文章拼接顺序 — 盘上已近退化 (mean 0.95) `pipeline/features/strategic_diff.py`
- LDA n_jobs=-1 → 跨机器核数依赖的浮点求和序, 与 docstring "保证可复现性"声称冲突 (复现包标准) `pipeline/features/strategic_diff.py`
- coh_emb/coh_emb_t2v 存原始嵌入余弦未 clip, 而断言容差 1e-10 小于本文件自述的 float32 误差 1e-7 — 潜在 stage 崩溃 ⚠latent `pipeline/features/strategic_diff.py`
- strat_fluidity 仅附着于通过 ≥3 银行 NN 闸门的年份 — 闸门口径错配致已算出的 fluidity 被静默丢弃 (latent, 早年稀疏语料) ⚠latent `pipeline/features/strategic_diff.py`

**geography** (5):
- 媒体坐标三级退化的省会回退注入与'银行是否在省会'相关的系统性距离误差, 且无 imputation 标记列 (当前 0.9% 触发, 全量放大) `pipeline/panel/geography.py`
- LOO IV 日志把 Manski (1993)/Bramoullé (2009) 标为'文献支撑' (反射问题文献恰是该同期组均值 IV 的识别威胁) + 模块头/Returns 仍写 '28 个' 距离缓冲变量 (实际 40) `pipeline/panel/geography.py`
- prox 双轨情感格 (tone/pos_frac/neg_frac) 全-NA 圈内均值返回 pd.NA → panel 列退化为 object dtype (latent) ⚠latent `pipeline/panel/geography.py`
- n_geocoded==0 时 is_local=0 / n_media=0 与 frac=NaN 自相矛盾 — 同一修复逻辑未覆盖兄弟列 (latent) ⚠latent `pipeline/panel/geography.py`
- merge_bank_geography 回退路径解析到不存在的 pipeline/panel/config/ + 姊妹函数 None 路径 TypeError 守卫不对称 + '' 聚类 'Stata 安全忽略' 误述 (latent) ⚠latent `pipeline/panel/geography.py`

**attention-media** (5):
- FIX-REGRESSION: Hassan extensive≠intensive 锚点更正只落在 attention_media.py docstring, 未传播到 P2 paper_spec / 模块与 runner 日志头 / config 注释 `papers/bank_fintech_attention/paper_spec.yaml`
- ft_attn_prov/city 地理注意力指数无 leave-one-out: 焦点银行自身文章计入其所在地指数, 市级小单元可被单一银行支配 `pipeline/panel/attention_media.py`
- attention_disp_full 标签语义反转: 'Dispersion' 命名/标签下装的是 HHI 集中度 (高值=集中=低分散) `pipeline/panel/attention_media.py`
- 停刊检测在 fintech-only 语料上度量的是'话题退出'而非'停刊', 且未经 NPPA 证实的 suspected 全量进入排除集 (latent, T=19 触发) ⚠latent `pipeline/panel/attention_media.py`
- 平衡媒体面板'全程在刊'仅用端点 (first_year≤start ∧ last_year≥end) 判定, 中间缺刊年不被剔除 (latent, T=19 触发) ⚠latent `pipeline/panel/attention_media.py`

**validation-sensitivity** (5):
- innovation_locus 聚合规则 baseline 与变体不一致: 生产是 LLM 多数票+keyword 分类器回退/交叉验证混合, 变体侧是纯 LLM 票 (空票→None) `validation/prompt_sensitivity.py`
- 变体调用失败行未剔除/未标记 — API 失败噪声计入措辞不一致, 且变体重试次数 (1) 远低于生产 `validation/prompt_sensitivity.py`
- FIX-REGRESSION: radius 零方差守卫未覆盖同模块可视化路径 — generate_visualizations 仍裸调 pearsonr, 常量输入产 NaN 进论文附录热力图 `validation/radius_sensitivity.py`
- decay_sensitivity 'uniform = 当前管道默认' 锚定声称不实: 窗口半径 (2 vs 生产 1)、归一化口径 (句级均值-of-ratios vs 生产池化 ratio-of-sums)、输入文本 (无标题 prepend) 三重偏离 `validation/decay_sensitivity.py`
- radius_sensitivity_llm 空泛真 pass: 全 NaN κ 时 passed=true; parse_track_results_from_cache 文档声称读缓存解析标签实则无条件返回全 None scaffold ⚠latent `validation/radius_sensitivity_llm.py`

**data-dta-parity** (5):
- stage 46 头部声称 NaN→./.a/.b extended missing, 两个写出后端均未实现, 盘上 0 扩展缺失 — 缺失原因不可区分 `pipeline/panel/stata_export.py`
- stage 46 类别编码+value label 机制对当前 panel 是死代码: innovation_locus/substantiveness/collab_mode 列不存在, 全部 .dta value label = 0 `pipeline/panel/stata_export.py`
- 变量标签在三套 .dta 交付物间断崖式丢失: 40.dta=666 条 → 46_*.dta=124 条 → 51.dta=9/1668 条; 1614 列标签跨文件不一致 `pipeline/falsification/controls.py`
- 盘上 46_*.dta 实由 pandas fallback (Backend 2) 写出而非推荐的 pyreadstat 路径; 两后端产出不同的 .dta 存储 schema (byte vs long), 复现二进制随环境漂移 `pipeline/panel/stata_export.py`
- latent(T=19): 12 个 LLM 计数列 dtype 随数据值漂移 (Int8↔Int64), .dta 存储型随之 byte↔long/double 翻转 — 值无损但 schema 跨规模/跨环境不稳定 ⚠latent `pipeline/panel/encode.py`

**sweep-valid-physical-denom** (5):
- 洗稿率 D/D2/E/E2/A2/F 变体: 分子要求 LLM 实质性标签有效, 分母为全体词典/BERT 阳性文章 — valid 分子/physical 分母系统性低估 `pipeline/panel/runner.py`
- all_n_articles / all_ln_coverage 混合计数基: 物理口径 fintech 篇数 + 去重口径 non-fintech 篇数相加 (fintech_share 修复后的残留不一致) `pipeline/falsification/controls.py`
- FIX-REGRESSION: clarity valid-mask 修复不完整 — 同函数内 frac_amb_articles_{full,ctx} 仍用物理 n_articles 分母 (加权均值修了, 计数份额漏修) ⚠latent `pipeline/panel/encode_collab.py`
- entity_masking 验证一致率: 掩码轨 LLM 调用全失败 → final_v=False 被计为'掩码翻转', 失败行留在分母 ⚠latent `validation/entity_masking.py`
- homeprov/homecity_media_frac 与 non-local 组: 地理元数据缺失文章被编码为'非本地'(0) 留在分母/对照组 — latent 域污染 ⚠latent `pipeline/panel/attention_media.py`

**pipeline-audit-family** (4):
- 39c classify_orthogonality 的观测 NMI 与置换 null 来自不同 listwise 样本 (854 vs 825), 且预注册 Z 阈值 (1.96/2.58 双侧) 与实现的单侧 p95/p99 不一致 `pipeline/audit/construct_orthogonality.py`
- 39d 与 39e 判别效度审计对同一对构念 (clarity/num_intensity) 样本过滤不一致 (n_articles_llm_valid≥2 mask: 64 obs vs 无 mask: 174 行), 且 39e 置换 null 连 NaN 一起洗牌致 null 失准 `pipeline/audit/lm_discriminant_validity.py`
- llm_contamination_test BF 标签自称 Jeffreys 1961 量表但证据等级整体抬高 1-2 档 (BF_10≥10 标 'decisive', Jeffreys 须 >100) `pipeline/audit/llm_contamination_test.py`
- KNOWN-OPEN-STATUS: ⑥ pyreadstat Int8∈[101,126]→Stata 扩展缺失仍未修, 且本单元 stata_audit 6d 精度检查存在 NaN 非对称逃逸盲点, 恰好无法捕获该类 值→缺失 腐蚀 `pipeline/audit/stata_audit.py`

**ctx-materializer-coretext** (4):
- 上下半切分边界: 跨界银行名/关键词双半均漏计, 排除上下文在边界截断 `core/text/ahocorasick.py`
- canonicalize_topic 把'无法分类'硬编码为 ('应用场景', 0.0), 缺失被强制归类且下游不过滤置信度 `core/text/canonicalization.py`
- entity_context.py 头注释与实际数据流矛盾: 声称实体窗口特征不含标题, 但 stage 14/15 消费的 content_ctx 已被 stage 13 注入标题 `core/text/entity_context.py`
- latent: ctx_materializer 标题缺失处理 — np.nan 标题会注入字面 'nan。' 前缀, pd.NA 会 TypeError 崩溃 (当前被上游过滤守住) ⚠latent `pipeline/text/ctx_materializer.py`

**network-spillover** (4):
- bank_emb_sim_mean 用 t-1 文本计算却无 lag1 命名/标注, 与 bank_cogn_mean(当年文本)口径不一致 `pipeline/panel/network_spillover.py`
- NSP-B 注释把 W² 行特定重归一误称'2SLS 对工具的标度变换不变': 论证错误 (结论尚立) `pipeline/panel/network_spillover.py`
- bank_emb_sim_mean 的 sim_row>0 过滤把'排除对角线'与'按符号筛选'混同, 非正相似度被静默剔除且使 [0,1] 断言永不可触发 ⚠latent `pipeline/panel/network_spillover.py`
- eigenvector 中心度三级 fallback 跨年语义漂移: 收敛年非主分量银行得 ~0, fallback 年得 NaN ⚠latent `pipeline/panel/network_spillover.py`

**iv-did** (4):
- 缺失 shift 零填并误称'等价于 exclusion restriction' `pipeline/panel/iv_did.py`
- DiD 处理分配按总部城市/省份匹配, 全国性银行 (SOE/股份制) 暴露错配且无代码内披露 `pipeline/panel/iv_did.py`
- zone LOO 不排除 'other' 伪经济圈, 与 Bartik 族 'other' 口径不一致; min_group_size 按文章数而非银行数 ⚠latent `pipeline/panel/iv_did.py`
- sandbox never-treated 控制组近乎为空, 注释/日志推荐的 csdid never-treated baseline 不可行 (latent, T=19) ⚠latent `pipeline/panel/iv_did.py`

**llm-peer-iv** (4):
- cutoff 0.70-0.90 五档 '稳健性' 列在盘上逐位相同 — 灵敏度扫描无识别变化却作为论文稳健性电池导出 `pipeline/panel/llm_peer_iv.py`
- Stage 48 无 NEWS_PROCESS_LLM_OFFLINE 离线守卫: 缓存 miss 静默重调付费 API, peer 网络可跨 run 漂移 (确定性锚点只护住 stage 21) `pipeline/panel/llm_peer_iv.py`
- LLM 明确判 '无同行' 与 '无数据可问' 同样落 NaN: llm_peer_count/peer_compete_idx 缺 0 值语义, 回归样本被选择 `pipeline/panel/llm_peer_iv.py`
- 文档声称 '加权同行情感 IV' 实为等权均值, 且 prompt 索取的竞争强度排序被 set() 销毁; count 计全部同行但均值只覆盖在panel同行 `pipeline/panel/llm_peer_iv.py`

**preprocess** (3):
- 广告关键词过滤对标题/版面/栏名做无锚定子串匹配, 系统性删除真监管新闻 ('央行公告/风险提示/年度报告解读' 类标题盘上为 0) `pipeline/preprocess/filter.py:87-96`
- 精确去重保留最高媒体权重副本而非首发副本: 跨年转载致日期/年度错配, 与近似去重'保留首发'原则相互矛盾; 24% 行权重静默回退默认值 `pipeline/preprocess/dedup.py:64-65,167-177`
- 领导人姓名删除与政策语料不对称且删除不完全: 新闻侧删 '习近平'、authoritative_corpus.txt 保留 6 处, 政策对齐度系统性偏差 `pipeline/preprocess/normalize.py:95-96`

**tone-berts** (3):
- 下游 Method E 把 2-class finbert2 与 3-class 模型的 P(正面) 等权平均后再 0.5 二值化 — 跨类数概率尺度不可比 (根因是 tone_berts 异构输出契约未归一) `pipeline/panel/runner.py`
- num_labels 不匹配时回退 DEFAULT_LABEL_MAP 的顺序对两个 hub checkpoint 都是极性翻转, 守卫仅 warning 不阻断 ⚠latent `pipeline/sentiment/tone_berts.py`
- 模型加载失败被 except 静默吞掉, 任一 hub 模型缺席仍 exit 0 → 输出 schema 静默漂移 ⚠latent `pipeline/sentiment/tone_berts.py`

**fls-lexical-numint** (3):
- specificity_index 把模糊量词 (一些/许多/若干/几十家, jieba 词性 'm') 计入"硬信息"分子 — 与 Hope-Hu-Lu (2016) specificity 构念 (specific vs vague 对立) 方向相反 `pipeline/sentiment/lexical_complexity.py`
- FIX-REGRESSION: lmfls-01 (LM 分母仅 word-token) 修复未传播到 num_intensity_word — _count_word_tokens 分母仍含标点/纯数字 token (~19% 膨胀), 其 docstring 的 "与 lm_non_sentim `pipeline/sentiment/numerical_intensity.py`
- 不定数后缀形式 (三十多万/二十余家/百分之三十几) 绕过 R7-M2 "不定数不计 token" 既定策略 — 不定字符位于匹配块之外, 守卫失效 `pipeline/sentiment/numerical_intensity.py`

**herd-decay** (3):
- 模块文档三处与实现/现行架构不符: ctx 物化阶段错标 stage 21、docstring 仍称轨1用'内容'、阈值边界'高于/>'与代码 >= 不一致 (含 chunk_size 死参数 YAML 注释误导) `pipeline/sentiment/herd_decay.py`
- latent: max_features=10000 按词频截断在全量语料下把头部银行的相似度计算压入最高频 ngram 子空间 ⚠latent `pipeline/sentiment/herd_decay.py`
- relaxed 向量化降级路径静默触发: ValueError 重试改用 min_df=1/max_df=1.0 但零日志, 违反项目降级透明红线 ⚠latent `pipeline/sentiment/herd_decay.py`

**fintech-intensity** (3):
- IDF 参考语料按 bank-article 物理行计数: 同一文章 × k 家银行被当 k 篇文档, 与 fintech_share 新去重口径不一致 `pipeline/filtering/fintech_intensity.py:114-128`
- 'SIF 加权质心' 与 Arora et al. (2017) 引用名实不符: 实现为 IDF 加权平均质心, 无 SIF 频率权重亦无首主成分去除 `pipeline/filtering/fintech_intensity.py:6-7,34-35,188,197-198`
- 上游 DF 输入缺陷: AC 上下半分扫使跨切分点关键词两边都不计数, 低估 DF 与 stage-12 计数 `core/text/ahocorasick.py:473-483`

**benefit-society** (3):
- FIX-REGRESSION: benefitfrac-01 median-center 修复未传播到 alt-anchor twin — benefit_jlm_zh_pos/neg_frac 仍用已证退化的 sign-at-0 阈值 `pipeline/features/benefit_society_alt_anchor.py`
- shrinkage 方差分量估计有偏: 单元素组零离差 + 无 N−k 自由度校正系统性压低 between_var → 过度收缩; within_var 用面板均值的 grand variance 充当抽样方差 `papers/benefit_society/shrinkage.py`
- latent: full 轨 8191-token 预截断丢弃长文尾部, 绕过引擎已支持的 Early-Chunking 均值池化, 与 header '完整语义信号' 声称不符 `pipeline/features/benefit_society.py`

**policy-alignment-similarity** (3):
- stage 15 对文章硬截断 8191 token 丢尾, 而同族 stage 25/26/27 对同一文本 chunk-pool 无损 — 截断理由已陈旧 (引擎本可自动分段池化) `pipeline/filtering/policy_alignment.py`
- stage 26/15 注释与实现漂移: '相同的 8000 字截断'已不存在、'4 种算法'实为 5 列、死代码 _get_embeddings_api_dynamic 描述已废弃的 '-ctx' 缓存命名空间 `pipeline/features/policy_similarity.py`
- 降级透明性缺口: stage 26 对 <3 银行年份裸 continue 无日志 (stage 25 同守卫有 warning), 且两 stage 的 t2v '失败→NaN' 契约只覆盖 returns-None、不覆盖 raise 路径 `pipeline/features/policy_similarity.py`

**network-brokerage** (3):
- neg_ratio 无最小篇数守门: 等权 mean-of-ratios 让 1 篇文章的银行 (ratio 恰为 0/1) 独家设定全行业冲击指数水平 `pipeline/panel/network_brokerage.py`
- own ratio 为 NaN 时 industry_neg_shock 被整体置 NaN, 尽管同行 LOO 均值完全可计算 — 行业级回归元无谓缺失 `pipeline/panel/network_brokerage.py`
- latent: 连通年份 numpy 路径 (scipy ARPACK 随机 v0) 跨 run 非逐位可复现, 该列不在已知 3 列非确定性台账内 ⚠latent `pipeline/panel/network_brokerage.py`

**risk-taking** (3):
- 宣称的 σ(ROA) 3y robustness 路径必然崩溃: --rolling-window 3 时 min_periods 仍默认 4, pandas 直接 ValueError `pipeline/panel/risk_taking_outcomes.py`
- compute_llp_discretion 分母用当期 total_loans, 与其 docstring 声称喂给 BW2012 Eq.(2) 的 LHS 规格 LLP_t/Loans_{t-1} 相矛盾 `pipeline/panel/risk_taking_outcomes.py`
- σ(ROA)<1e-6 → z_score 置 NaN: 把'最稳定银行'从 Z-score 样本中静默剔除 (对 DV 的选择性缺失) ⚠latent `pipeline/panel/risk_taking_outcomes.py`

**falsification-controls** (3):
- L663-669 '恒等式校验' 是同义反复 — 把刚算出的和与自身比较, 永不可能检出数据不一致 `pipeline/falsification/controls.py`
- fintech_share 对零新闻 bank-year 填 0 — 未定义比率 (23/174 行) 与真实零份额 (33/174 行) 同值混淆 `pipeline/falsification/controls.py`
- Hassan 伪造检验主战场 (模板检验 1-10) 全程仅 full 轨 — 论文主指标 llm_vote_tone_ctx 从未受伪造检验保护 `papers_assets/bank_fintech_tone/do/falsification_template.do.tmpl`

**sweep-insample-leakage** (3):
- high_coverage 调节变量 = 同年中位数切分的内生覆盖度, tone×high_coverage 交互进回归 (与 digital_frontier 同型) `pipeline/panel/runner.py`
- substance 论文 3 处 xtile 在全年份 pooled 分布上切分位 (cap_q/car_q/disclose_q), T=19 下趋势变量的分位组沦为年代代理 [latent] ⚠latent `papers/_common/stata_templates/bank_fintech_substance/17_substance_heterogeneity`
- herd_decay 前驱跟风计数的 TF-IDF 在单银行全历史 (含未来文档) 上 fit — 纯后视构念使用了含前视 DF 的向量空间 [latent] ⚠latent `pipeline/sentiment/herd_decay.py`

**sweep-log-entropy-clip** (3):
- benefit_society 经验贝叶斯 shrinkage 的 between_var 实为组内残差方差 (含抽样噪声), 与 James-Stein τ² 及自身 docstring 公式不符 → 系统性欠收缩 `papers/benefit_society/shrinkage.py`
- tone_words Z-score 在 std 退化/全 NaN 分支整列回填 0.0, 把缺失值抹成伪零分 (latent) ⚠latent `pipeline/sentiment/tone_words.py`
- Pielou 均匀度 J' 对单一媒体 (n_unique≤1) 返回 1.0 ('完全均匀'), 与同报告 HHI=1 ('完全集中') 自相矛盾 ⚠latent `validation/media_diversity.py`

**encode-collab** (3):
- _normalize_label 在 pandas 3.0 str dtype 下整体失效 (dtype == object 恒 False) — 文件内全部脏标签防御静默变 no-op, 前轮 clean-bill 对此的声称不成立 ⚠latent `pipeline/panel/encode_collab.py`
- frac_amb_articles_{full,ctx} 分母=物理文章数而分子仅 clarity-valid 文章可进入 — 刚修复的 valid 分母标准未覆盖到三行之下的计数型 frac; 另有全 NaN→median=NaN→全员假零边界 ⚠latent `pipeline/panel/encode_collab.py`
- apply_v3_5_2 缺失幂等 pre-drop — panel 已含同名列时 merge 产生 *_x/*_y 幻影列且陈旧原列残留, 与同文件 clarity/numint 聚合的防护不一致 ⚠latent `pipeline/panel/encode_collab.py`

**encode-features-agg** (3):
- ctx 对角线分类聚合块硬编码源列无存在性守卫 → stage 21 部分产出时 latent KeyError (违背 valid_agg 优雅跳过契约) ⚠latent `pipeline/panel/encode.py`
- ctx_is_fallback 防御性 astype('bool') 对缺失值语义错乱: np.nan→True / None→False (latent 静默计数失真) ⚠latent `pipeline/panel/encode.py`
- 恒等式校验严格度三维度不一致: locus/substantiveness 仍用严格 ==, collab 已按 R6 放宽为 >= — 全量下将产生伪告警 ⚠latent `pipeline/panel/encode.py`

**sweep-merge-integrity** (3):
- encode_collab.apply_v3_5_2 merge 不幂等: panel 已含同名 LM/FLS 列时产出 *_x/*_y 幻影列且陈旧原列保留, 同时仍报告『成功新增』(同文件兄弟聚合器均有 pre-drop 防护, 本函数缺失) ⚠latent `pipeline/panel/encode_collab.py`
- 主线 01_data_prep IC 回退路径 `capture merge 1:1 core+aux` 无 keep(match master)/assert(match): 陈旧 aux.dta 的 using-only bank-year 会被静默追加为幻影观测, capture 同时吞掉键非 ⚠latent `papers/_common/stata_templates/01_data_prep.do.tmpl`
- paper-10/11 处理变量 merge 的 keepusing 全有或全无 + 误导性诊断: 任一 keepusing 列缺失 (主 DAG 复现 run 下 cross_outlet_tone_variance_* 必缺) → 整个 merge r(111) 被 capture 吞掉, 连同 ⚠latent `papers/bank_media_disagreement/stata_templates/01_data_prep.do.tmpl`

**validation-robustness** (2):
- entity_masking 聚合一致性分母含 LLM 调用全失败行 (masked_verified 被空票判 False), 与逐模型分解的 valid 分母口径不一致 `validation/entity_masking.py`
- entity_masking 残留检测 (漏遮审计) 只扫描正文不扫描标题, 且 peer 替换计数漏计标题命中 `validation/entity_masking.py`

**validation-tone-llm** (2):
- latent crash: 'import math' 仅在验证任务 CI 分支内, 验证 ICR 缺失而情感 ICR 存在时 G-10 报告段 UnboundLocalError `validation/llms_evaluation.py`
- 人工验证样本/编码协议与被验证构念错位: 双轨共写同一 09_sentiment_verify.xlsx 互相覆盖 + 编码指南'不受标题影响'与 v3.8.0 标题 prepend 矛盾 + 单一全文金标准同时评 ctx 轨 `validation/tone_validation.py`

**tone-words-tfidf-lm** (2):
- 词典加载对 positive∩negative 重叠词静默 last-writer-wins 赋 -1.0 (jiang 21 词 + you_2018 5 词, 含高频词 '打破') `pipeline/sentiment/tone_words.py`
- IDF document frequency 在 (article×bank) 重复行上统计, 同文被计至 8 次 (偏离 GKT/Manning 文档级 DF 定义) `pipeline/sentiment/tone_words.py`

**staleness-sbert-embed** (2):
- article_sbert 读取不存在的 config 键 embedding.model — '单源对齐'声称失实, 模型实际硬编码且无 revision 钉死 `pipeline/text/article_sbert.py`
- 超长文本 chunk 等权 mean pooling: 尾段碎片 chunk 获得整段同权 (latent, >8191 token 文本) ⚠latent `pipeline/text/embedding_engine.py`

**panel-runner-merge** (2):
- Token/Hidden 四象限分类仅 full 轨: 阈值与分类全用 policy_cosine_sim (full alias), ctx 孪生缺席 — 2026-06-08 双轨补齐止步于 sim mean/std `pipeline/panel/runner.py`
- 运行日志/注释计数声明与实现漂移: 'disag (32 变量)' 实为 28, '40 种洗稿率' 实为 34 列, 'BERT (5模型)' 实为 3 `pipeline/panel/runner.py`

**encode-tone-agg** (2):
- balance_panel 计数/和类零填契约漏 11 列: n_articles_llm_valid(_ctx)、6 个 ctx 对角计数、n_articles_for_ctx_independence、sum_herd_weight_full/ctx 在零新闻行残留 NaN `pipeline/panel/encode.py`
- avg_llm_conf / avg_agreement_rate / avg_{model}_conf 聚合域=物理全集 (含无效票文章), 与 tone 的 valid-only 域错位 — 衰减偏误调节变量被验证失败文章的低置信度系统性拉低 `pipeline/panel/encode.py`

**sweep-fillna-weights** (2):
- 单观测 std 填 0: benefit_std / article_sim_std 把'无法测量的分歧'编码为'零分歧', 与核心 tone 离散度族 (保持 NaN) 口径不一致 `pipeline/features/benefit_society.py`
- frac_amb_articles: NaN-clarity 文章被当 False 排除出分子但计入物理分母 (刚修复的加权均值兄弟列漏修, latent) ⚠latent `pipeline/panel/encode_collab.py`

**data-panel-invariants** (2):
- balance_panel 计数/和列零填契约漏掉 ~20 个兄弟列: 零新闻行残留 NaN 而非 0 (与 F4/F5/L1/vwmwhw-F1 同类缺口) `pipeline/panel/encode.py`
- avg_category_confidence 永久全 NaN 死列: 上游列名 v3.2.0 改版后 else 分支硬编码 NaN, 下游诊断成死代码 `pipeline/panel/encode.py`

**stata-templates-papers-b** (2):
- strategic_diff Bartik 表头声称'识别差异化因果效应'但工具的是 tone, 差异化系数仍是 OLS; llm_peer 引文期刊名错 'Review of Asset Studies' `papers/_common/stata_templates/strategic_diff/12_table3_mechanism.do.tmpl`
- 守卫模式缺陷族: 连续双 capture confirm 只检最后一个 _rc + foreach-continue 空守卫, 缺列时穿透为 r(111) ⚠latent `papers/_common/stata_templates/brokerage_network/14_table5_robustness.do.tmpl`

**paper-spec-crosscheck** (2):
- 全部 11 份 spec 的 financial controls 7 列盘上零命中且无 pending 标注; 4 篇衍生 paper 模板实际用 coverage 代理控制, 与 spec 声称不一致且未披露 `papers/*/paper_spec.yaml`
- spec 引用的表模板悬空: P3/P4/P5 t6 与 P1 tA9 仅存于归档目录且无任何 builder 可达; bank_news_clarity tA8 模板全仓不存在且无 "待设计" 标注 `papers/bank_fintech_substance/paper_spec.yaml:76-77;`

**panel-runner-weights** (2):
- 洗稿率族分母为物理域有效票正面数, 未排除 substantiveness 测量失败文章 (分子隐式要求已测量) — latent ⚠latent `pipeline/panel/runner.py`
- Token/Hidden/Subst 四象限占比: policy_cosine_sim 测量失败文章落入隐式 Irrelevant 并滞留分母 — latent ⚠latent `pipeline/panel/runner.py`

**sweep-determinism** (2):
- 本地 sentence-transformers 编码 (stage 30a + embedding_engine.encode_local) 缺 stage 23 同款确定性硬化, 且 local 路径无缓存逐次重编码 ⚠latent `pipeline/text/article_sbert.py`
- llm_peer_iv._normalize_peer_names 返回 list(set(...)): peer 列表顺序随 PYTHONHASHSEED 漂移且丢弃 LLM 的竞争强度排序 (当前数值惰性, latent 截断隐患) ⚠latent `pipeline/panel/llm_peer_iv.py`

**papers-derivative** (2):
- plot_placebo_comparison 对 Coefficient namedtuple 直接 float() — 输入一旦存在立即 TypeError (实证复现) ⚠latent `papers/benefit_society/figures.py`
- NCD 抽取 prompt 单位指令 (亿元) 与字段命名/校验区间 (billion) 冲突 10 倍 — 解禁后大行被静默置空、中小行带 10× 污染入面板 (latent) ⚠latent `papers/benefit_society/ncd_text_extractor.py`

**data-recompute-spotcheck** (1):
- staleness 面板列聚合域 = 未过 LLM 验证的 1170 篇全集, 与面板其余全部文本测度的 857 篇 verified-union 域系统性不一致 (含 4 个零覆盖幻影 bank-year) `pipeline/text/article_staleness.py`

**stata-templates-papers-a** (1):
- Table 5 "Wild boot" 列展示的是解析 cluster SE 而非 wild bootstrap 推断 — boottest 结果未注入 eststo; 且 attention/substance/locus 18 未守卫 boottest 安装 `papers/_common/stata_templates/bank_fintech_attention/18_attention_robustness.do`

**news-bank-fintech-salience** (1):
- salience 0/1 测度对缺失源字段无 NaN 路径: 版面/页号/作者缺失时硬编码为 0, 全量多源语料下'线上媒体无版面概念'与'未上头版'混同 (latent) ⚠latent `pipeline/filtering/news_salience.py:45-104`


---

## 5. 证伪击杀与主控改判

### 5a. 主控终裁改判 (过度证伪恢复, 历史教训第三次应验)
证伪层把 4 条**事实完全坐实**的发现以错误的 duplicate-of-known 映射或自相矛盾论证击杀, critic 抓出、主控亲验后改判恢复 (已计入上方 P3 清单):
1. codebook `target_bank='42家商业银行'` vs 盘上 87 家 — 自相矛盾铁证 (主控实测 nunique=87)。
2. `scripts/generate_codebook.py` 读 40_panel 而台账修复指令要求 51 — 源不一致真实。
3. codebook `avg_locus_prob_score_std` 声明 [0,0.5] 与同行实测 0.5292 并存 — 自相矛盾铁证。
4. entity_masking 残留检测只扫正文不扫标题 — masked_title 实际注入 prompt, 泄漏通道真实。

### 5b. 维持击杀 (refuted, 9 条)

- media_diversity Pielou 均匀度对单一类别组返回 1.0 ('完全均匀'), 与 0=完全集中语义矛盾且令健康判定在退化组上虚假通过 — Line-level facts are correct (media_diversity.py:207-208 `if n_unique<=1: return 1.0`; L350 shannon_max=1.0 for n_unique==1; L928 gate `evenness<0.70`), but the load-bearing harm claim ("健康判定在退化组上虚假通过
- KNOWN-OPEN-STATUS: ⑥ pyreadstat Int8∈[101,126]→扩展缺失 — 仍未修; 盘上已触 max=100 精确边界; 实际写盘后端是 pandas fallback (安全), 装上'推荐'的 pyreadstat 反而引 — 声称的状态性事实全部属实, 但其载荷性危险断言被实测+源码双重证伪, 且连带证伪了台账 ⑥ 本身的前提。

【证实的部分】(1) F:\WiseSearch\data_antigravity_project\news_process\pipeline\panel\stata_export.py:550-557 的 _write_dta_pyreadstat 确为 4 行直写, 无 int8 值域守
- latent: 标题为 NaN 时 `row.get('标题','') or ''` 产出字符串 'nan' 前缀注入两轨文本 (float NaN 为 truthy) — 上游已结构性过滤: stage 00 filter.py:77 dropna(subset=KEY_COLUMNS)+L82-84 空串 strip 过滤, preprocessing.yaml:28-29 标题/内容均在 key_columns; load.py:147-152 再加标题汉字数下限。该过滤对全量 18.2M/T=19 同样无条件执行(load.py:120 逐文件调用) → NaN/
- 空文本缺失值契约不对称: 词典 score/ratio/msent 零填 ('伪中性') 而 clarity/LM/FLS 用 NaN, 同条件两套口径稀释 panel 均值 — 代码两套默认值确实并存(L853-893 零填 vs L261-280/lm:113-121 NaN), 但触发条件(空/无效文本)生产 DAG 结构性不可达: stage 00 内容非空+汉字数下限(filter.py:75-85), ctx_materializer.py:132-133 空 ctx 回退全文 body, 且 prepend_title 后两轨文本至少含非空标题 → T=19 
- latent: NaN 标题经 `str(row.get('标题','') or '')` 变为字面量 'nan。' 前缀注入双轨文本 (兄弟 stage 均用 fillna('')) — 上游 stage 00 已结构性过滤: filter.py:77 dropna(subset=KEY_COLUMNS 含标题/内容, preprocessing.yaml:27-31) + L82-84 空串过滤 + load.py:148-154 标题汉字≥2 过滤 + load.py:168-170/filter.py:113-115 fillna('')。NaN/空标题行在 T=19 全量下
- latent: 全样本 pooled IDF 前视 — T=19 生产语料下 2007 年文章的强度分嵌入 2024 年文档频率信息 — 全语料IDF是教科书定义(Manning Ch6.2.1 相对collection计算)且正是模块所引方法指令(GKT 2019 §2.2 'IDF must be computed on the full reference corpus', fintech_intensity.py:105-106); 权重无监督、与因变量独立, 无泄漏路径; 时不变权重利面板可比, 滚动IDF仅是稳健性变体。
- _concat 标题去重用未 strip 的原始 标题 比对, 而 stage 13 prepend_title 先 strip 再注入 — 含首尾空白的标题将双重注入聚合文档 (latent) — 上游已过滤: stage 00 `_clean_single_text` 对 TEXT_COLUMNS=['标题','内容'] 全量执行 (normalize.py:109 末尾 .strip() + TAIL_CLEANUP 空白归一; _constants.py:117), df_exploded 必经 stage 00 → 抵达 _concat 的标题恒已 strip, 18.2M 全量同走此管
- HW/MW 加权链条 dict/BERT 族的权重 NaN 策略分子分母不对称 (latent): 分子权重 fillna(1.0), 物理分母聚合原始列 NaN-skip(=0) — 不对称字面存在 (runner.py:358-359 fillna(1.0) vs encode.py:708-709 原始列 sum), 但上游 herd_decay.py:271-272 整列初始化 1.0, 仅以 1.0/(1.0+int(count)) 覆写 (312-320, int 不可能 NaN), 各 fallback (253-255/277-281) 也全设 1.0; runn
- llms_evaluation 金标准诊断: gold 列不可解析/缺失值 fillna(0) 被当作 gold=0 进入混淆矩阵 — 上游已过滤: L1192 has_gold_ver=notna(), L1286 df_eval_ver 仅取有标注行后才传入 L1494 → gold 缺失行根本到不了 L866 fillna(0)。notna 但不可解析的字符串会先在 L1287 astype(int) 崩溃 (Step 4 先于 Step 4b), 不可能静默变 0。_pred fillna(False) 与主指标 L130

### 5c. 归并已知台账 (dup-known, 14 条)

- dict_coverage 分析 5b (灰色地带 LLM 交叉验证 / FNR 估计) 因导入不存在的 utils.llm_clients 永久不可达, --run-llm-check 必然失败
- threshold.py 银行分类模拟 cond_b 用 total_with_title 代替正文 total, 偏离生产 analyze_bank_matches 路径 B → 敏感性网格低阈值端正例数虚高
- pyreadstat / pandas 双后端写出的 .dta 语义不等价, 且后端由 import 探测的环境决定 — 同代码同数据跨机器产出不同复现包
- KNOWN-OPEN-STATUS: ⑧ encode_local 未 L2 归一 — main 上仍未修, 混合范数仍流入 _t2v centroid
- avg_ft_intensity_* 把二次熔断零填(0.0)计入均值分母, ctx 轨 15% 强制零、17/157 bank-year 整组塌 0, verified 掩码从未出口面板
- 词典 6/1506 关键词 jieba 结构性永不可匹配 (TF≡0): 含空格/顿号词参与分类与 IDF 但永远不进强度分
- KNOWN-OPEN-STATUS: ⑦ centroid embedding 轨 clip[0,1] 压尾部 — 核实仍未修, 现状不变
- KNOWN-OPEN-STATUS: ⑦ centroid/NN 嵌入轨 clip[0,1] 压尾部 — 现状核实: 仍未修, L843 与 L737 均维持 clip(…,0.0,1.0)
- KNOWN-OPEN-STATUS: pos/neg_frac in-sample pooled median 泄漏仍未修 (现状核实)
- KNOWN-OPEN-STATUS: encode_local 未 L2 归一 (台账⑧) — 现状未修, 本单元受影响面 = _t2v 轨多 chunk 池化与 t2v 锚点的范数加权偏置
- KNOWN-OPEN-STATUS: panel 12 个 Int8 sum/count 列 × pyreadstat 扩展缺失窗口 [101,126] (台账⑥) — 现状: pos_count_full max=98, 距危险窗仅 3; pandas 仅在组和>127 时升 
- KNOWN-OPEN-STATUS: clarity 二值化 in-sample median 仍未闭合 — sidecar 只写不读, '冻结'锚每次成功重算即被覆盖, 且 ctx 轨根本无锚点通路
- KNOWN-OPEN-STATUS: ③ BW2012 residual discretion 现状核实 — 仍未实现, 披露链完整且一致
- Bartik IV: 无基期暴露银行的份额 fillna(0) 使工具变量坍塌为伪零 0 而非 NaN (盘上 17-40% 行 IV≡0)

---

## 6. 数据层实证结果 (data 单元)

- **panel 不变量**: 发现词典 tone 族突破 [-1,1] (程度副词×3.0 加权分子/未加权分母, 理论值域 ±4.5, 盘上 4/5 词典有 >1 文章); bert_avg_pos/neg 二分类+三分类混平均 (行和最大 1.33); Bartik 份额行和=0 伪零族 (media 70/174 行); 其余族 (frac 三和=1 / (bank,year) 唯一 / sum_wd_ 零填) 通过。
- **.dta 对拍**: parquet↔46↔51 共同列抽样一致; 盘上 .dta 系 pandas fallback 产物 (本机 pyreadstat 未装), 双后端漂移归并 KNOWN-OPEN ⑥。
- **独立重算对拍**: llm_vote_tone / fintech_intensity / 词典 tone / vw 加权可重算项与盘上一致 (valid 域口径下); herd/staleness 等 golden-deferred 列按旧语义一致。

---

## 7. 覆盖图与残余盲区

**已覆盖**: pipeline 全部指标模块 (sentiment/filtering/features/panel/falsification/preprocess/audit) · validation 13 模块 · papers 11 篇 tables/analysis/spec · Stata 模板 (主线 14 + 4 paper 族 + disagreement/clarity 各 5) · codebook 产物对拍 · 8 类同型扫描 · 3 类数据实证 · core/text 实体匹配层。

**双 critic 标记的残余盲区 (本轮未深审, 下轮候选)**:
- `core/` 内核: caching.py v0 键 fallback (威胁 stage 21 确定性锚点)、config loader、schemas。
- `pipeline/llm_archive/` provenance 层 (manifest 哈希↔盘上 jsonl 一致性)。
- `papers/_common/stata_postprocess.py` (Stata 日志→论文表的正则提取层) 与共享绘图层 figures (置信区间公式)。
- 词典/语料资源文件内容质量 (LM 中文词表翻译、8223 关键词 0 繁体、authoritative_corpus 来源)。
- geography 坐标表 provenance (build_city_coordinates 数据源)。
- `config/银行面板2007-2025年.xlsx`: 零代码消费者, T=19 财务列接入(也即 N4 幻影列的解药)完全在审计射程外。
- 全量 18.2M/T=19 工程维度 (load.py read_excel 单文件、dedup MinHash 内存、O(N²) 复杂度)。

---

## 8. 诚实边界

1. 全程在 T=2 试跑盘上验证; latent 判定基于代码语义+全量触发性推断, 未在 T=19 数据上实证。
2. 三波工作流跨 3 个会话限额窗口执行, Wave-1 部分发现的证伪由原设计的逐条 1-3 镜头降级为 Wave-2/3 的批量复核官逐条读码裁决 (每条仍有代码级证据, 但 P3 允许快速抽查)。
3. refuted 桶含程序性击杀与实质证伪两类, 已在 5a/5c 分流; 仍有 0 条未决残余 (全部 P2 以下, 列于台账 JSON)。
4. 未改任何生产代码; 全部修复待 user 拍板。
5. 台账机器可读版: `scripts/audit/_omni_merged_2026-06-10.json` (286+ 条全量, 含逐条裁决理由)。

---

## 9. 修复路线图 (按成本/侵入性分层)

**T0 — 审计器/验证器自身 ($0, 不动 panel, 立即可修)**
stata_audit 3e 三权重分母改 sum_wd_*+修 VW/HW 陈旧列名; tone_validation BERT 发现排除 words_idf+'llm' 聚合列剔出 α; ECE ground-truth 改 leave-one-out; llms_evaluation fillna('中性')→剔除+哨兵(-1/待仲裁)排除+demo 产物加标记; entity_masking ctx 标题双注入; prompt_sensitivity 变体升 v8 schema+ctx 进 gate+ctx 剥离标题; 39f 事件窗合并重叠; llm_contamination |r| 比较+年中点规约; dedup_threshold 改上游语料扫描。

**T1 — panel 值修复 ($0 本地重算 + golden 重生)**
Bartik: share fillna(0)→NaN (7 族伪零)+_t01 真池化或删除+早于 T0 年掩码; log_sent 零覆盖→NaN; 0.67→(2/3−ε); coverage_continuity 分母改全年; bert_avg 族分类口径分离; encode zero-fill 契约补 n_articles_llm_valid/sum_herd_weight_* 等 11 列; D4 residual frac 改 both_valid 分母; frac_amb 分母同步; strategic centroid 改 LOO+共享文章去重/降权; 共现网络边权统一 both-verified 口径; policy 7h 族聚合域改 verified; semantic staleness 窗口排同日; benefit_std/article_sim_std 单观测→NaN; brokerage eigen 非连通→逐分量或 NaN; industry_neg_shock 披露年 FE 共线; iv_did Int8 先 astype 再减。

**T2 — 上游文本/计数层 ($0 但大面积重算 22/23/11/12/14 等非 LLM stage)**
ahocorasick 最长匹配位置去重+跨行嵌套消歧+负面模式补 ('中国银行间'/CBIRC 全称/法国兴业)+上下半切分跨界修复; target_in_lead 用变体; num_intensity cn2arab 单字白名单+句分母全角守卫; tone_words 重叠词去重+best-dict 改固定词典+分母 word-token 化 (与 LM 修复对齐)+度量值域归一; finbert2 独立 tokenizer (分组键加词表哈希); t2v 轨按模型 max_seq 分块; herd TF-IDF min_df 比例化; FLS 门控词表审定; lexical jieba 注入隔离 (独立 Tokenizer 实例)。

**T3 — ⚠ 语料级 (normalize 数字破坏+phone 正则+互动计数模式)**
修复将改变全部下游文本 → **LLM 缓存键全变 → stage 21 全量付费重跑**。与 T=19 production run 合并执行 (受 M0 gate 管辖), 切勿单独小修反复触发付费重跑。修法: `(.)\1{2,}` 排除数字字符 (`([^\d])\1{2,}`); phone 正则加 `(?<!\d)...(?!\d)` 锚; 互动计数模式按媒体类型条件启用。

**T4 — replication/文档层**
derivative_replication 幻影 CONTROLS/MAIN_DV: 接入外部财务面板 (config/银行面板2007-2025年.xlsx) 或先降级为可运行占位; esttab .tex↔.csv 死接线 (模板加 csv 导出或 python 改读 .tex); codebook 重生 (42家→87/LLM 阵容 deepseek/范围/54 缺列/9 幻影行); 引文残留 (Berger 1 + TNIC 3 + z_score 13 + BW2012 模板措辞); core_patterns bartik_fintech_iv 幻影列名。

**T5 — 设计层披露 (spec/manuscript)**
LDA/IDF/EB-shrinkage pooled 全样本 fit 的 look-ahead 披露; digital_frontier/high_coverage 同期内生切分改 pre-period 固定; placebo DID 窗口上界+控真实处理; 双轨 gate (prompt_sensitivity/falsification 仅 full 轨) 补 ctx; Tetlock/Hassan/HP 构念保真差异如实标注 (staleness 全银行池化≠同公司、attention extensive、best-dict 嵌合体)。

---

*生成: metric-omni-audit 三波工作流 + 主控终裁, 2026-06-11。上游报告: METRIC_AUDIT_TOPTIER_2026-06-09.md / METRIC_AUDIT_METAVERIFY_CLOSURE_2026-06-10.md / METRIC_AUDIT_FIX_CLOSURE_2026-06-10.md。*
