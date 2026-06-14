# 媒体注意力测度框架 — 顶刊 referee 级系统审计 (全量 T=18 / 17M 语料)

**日期**: 2026-06-14
**范围**: 媒体注意力测度框架(构建正确性 / 覆盖完整性 / 识别有效性 / T=18 重激活),针对**全量 17M 篇、2007–2024、T=18** 银行媒体报道语料(非 T=2 试跑盘)。
**方法**: 10 审计维度 × 深读代码 finder → 逐条发现对抗核验 → 完整性批判 → 主编终裁。80 agent / 5.65M token / 1112 tool-use。引文联网核验。
**验证状态**: 68 条发现中 **41 条经独立对抗核验**(18 confirmed-real / 21 severity-overstated / 2 false-positive);**27 条 finder 标记但核验阶段遭会话 token 上限中断**(下方标 `[finder-flagged]`,多数被终裁/完整性批判的独立 grep 或项目 memory 交叉佐证)。

---

## 0. 总裁决

| 项 | 结论 |
|---|---|
| **总评级** | **major revision**(大修后可接收,非拒稿) |
| **P0 阻断** | **0** |
| **P1 阻断** | **3** |
| **must-fix (P1+P2)** | **11** |
| **T=18 就绪性** | **未就绪** — 多个 T=2 时代的 graceful-skip 守卫现在会**误导**而非诚实降级 |

**核心判断**: 文章级测度机制是**健全**的 —— ATT-1 firm-level verified-universe 门控已正确落地(`attention_media.py:376/395`),双轨 full/ctx 红线已强制执行,错时 `dcep_/sandbox_` DiD 列与 `_lag1` peer-LOO 工具变量**已物化在面板上**,确定性锚点(离线模式 cache miss 即 fail-close)真实有效。因此大量发现被正确**下调**严重度。但有三类问题**阻断**在全量 T=18 语料上发表。

---

## 1. 大白话

你现在拿到了 2007–2024 全量 17M 篇语料(T=18),这激活了一整族之前在 2 年试跑盘上"算不动"而被搁置的测度(异常注意力、爆发度、持续性、事件研究/DiD、Lazy-Prices)。审计要同时查三件事:**已有的算得对不对、该有的全不全、为 2 年盘写的"优雅跳过"守卫现在是不是反而把该跑的测度给藏了**。

结论是:**框架地基是稳的,但还不能直接在全量语料上跑出能投顶刊的结果,有三个硬伤必须先补**:

1. **比值测度跨年不可比**(最隐蔽、最致命)。`attention_pct`、`ft_attn_*` 都是"金融科技报道 / 全部银行报道"的比值。2008 年语料稀薄、2020 年语料饱和,**同一个比值数字在两年含义完全不同**(媒体进入退出、数字化、2013 后金融科技话题爆发)。没有任何维度去审计这个"语料构成 18 年漂移",而你要做的所有跨年 DiD/事件研究全建立在它之上。
2. **事件研究/错时 DiD 是空壳**。spec 声称做了 E1–E5b 事件 DiD 和 csdid 稳健性,但 `post_E1/treat_E*_year/never_treated_E*` 这些列**全代码库没有任何地方生产**(grep 零命中),主回归 M6 遇到它们 `capture confirm` 后**静默跳过**。能用的错时设计只存在于另一套 `dcep_/sandbox_` 列里,但 attention 论文的叙事从没接上去。
3. **11 个方法×双轨情感测度 + 注意力指数本身,零人工金标准验证**。所有评分者表是空的,而且你引的 Da-Engelberg-Gao 2011 这篇文章的全部贡献恰恰就是"把新注意力代理变量对照其他基准做验证"——引了却没做这个验证。

好消息:三个阻断项里有两个是 **golden-safe、$0** 的(语料漂移披露 + 把事件研究接到已存在的 `dcep_/sandbox_` 列),不用重跑付费阶段。新列工作可以攒到一次受控的生产 golden 重生里一起做。

---

## 2. T=18 就绪性 — 哪些 T=2 守卫现在会"误导"

三类 T=2 时代假设在全量语料下失效:

1. **硬编码的永久降级**: `15_attention_main_regression` 模板自述 "本模板无 csdid 块 / 待 production run 且 T≥3";`attention_media.py:314` 时间域注释把 "Da异常/AR/burstiness/月度" 的搁置**硬编码**,没有任何 opt-in flag 或代码路径 —— 这些测度在它们恰好重获功效时**仍然休眠**。
2. **缺生产者导致静默 no-op**: `post_E*/treat_E*/never_treated_E*` 零生产者,M6 和所有声明的 E1–E5b 事件 spec 在全量盘上**依旧 capture-confirm 跳过**;可用的 `dcep_/sandbox_` 错时列确实存在(`iv_did.py:625-761`,带 notyet 指引),但 attention spec 没接上。
3. **为 T=2 写的静默跳过守卫现在错误压制**: `compute_balanced_media_robustness` 的 balanced-media 逐年覆盖守卫、N<2→NaN、staleness `WINDOW_DAYS=7` 硬编码(`article_staleness.py:84`,非 config 驱动、语料池而非 Tetlock 同公司)—— 都是为 176 行写的,在 T=18 需重估。

**正面**: ID-1 错时 DiD 修复是 golden-safe 的(`dcep_/sandbox_` 列已在面板上、已存活进单列 `.dta`);财务面板依赖项是 forthcoming-not-blocking;3 个 BLAS-FP 网络中心度列按设计排除在确定性检查外。

---

## 3. 三个 P1 阻断项

### P1-A ⭐ 比值测度跨年构成漂移(完整性批判头号遗漏,10 维度全漏)
- **问题**: `ft_attn_yr/prov/city = fintech/total`、`attention_pct = N_ft/N_all` 是比值,分母(全部银行报道)在 2007–2024 量级暴涨且构成重组。同一比值数字在稀薄 2008 vs 饱和 2020 含义不同。`detect_defacto_cessation` 只碰媒体退出;**无**媒体进入/退出表、**无**篇均长度/通讯社占比漂移报告、**无**分时代稳定性检验、**无**时变基准归一化。
- **直接威胁**: 整个 T=18 重激活前提所依赖的跨年 DiD/事件研究识别。
- **修复(P1, golden-safe, $0, 最先做)**: 出逐年 outlet-entry/exit + 篇均长度 + wire-ratio + geo-footprint 表 + 分时代(2007-12 / 2013-18 / 2019-24)稳定性检验;对 fintech/total 分母做时变基准归一化,或披露不可比。纯分析/披露,不改面板列。

### P1-B ⭐ 错时 DiD / 事件研究在声明的 event spec 上永久失效 (ID-1 + ID-3 + ID-7)
- **问题**(grep 核验): `post_E1/treat_E*_year/never_treated_E*` 全 pipeline 零生产者;`15_attention_main` M6 capture-confirm 静默跳过;locus/collab 事件研究模板消费同样不存在的列;csdid "稳健性"模板自述不存在。能用的错时设计只在 `iv_did.py` 的 `dcep_/sandbox_` 生产者里(2019-2022 真错时 cohort),attention spec 未接。
- **修复(P1, golden-safe Stata+spec, $0)**: 二选一。**Route B(最干净)**: 把 attention spec 的 event_studies/DiD 重指到已存在的 `dcep_/sandbox_` 生产者(`iv_did.py:625-761`),用 `csdid ... notyet`(**非** never-treated,后者仅 ~2/87 银行),改写 M6/csdid 块。**Route A**: 写缺失的 `post_E*/treat_E*` 生产者读 `exogenous_shocks.yaml`(注意:E1-E5b 是**同步**强度 DiD 非错时,cohort-based 事件研究模板对同步政策不适用,须 reconcile;勿破 `test_papers_b_route.py::test_exogenous_shocks_yaml_17_specs`)。可抄现成范例 `bank_fintech_locus/19_locus_event_study.do.tmpl`(Sun-Abraham)。同时落实或删掉 csdid 语言。

### P1-C ⭐ 注意力指数 + 11 情感测度零人工/外部效度验证 (GOLD-1)
- **问题**: 零 criterion validity —— 无盲编码完成,LLM 投票/词典/BERT/intensity 验证/staleness/W&Z 实质/Gomber locus 的 accuracy/P/R/F1 全未对照金标准建立。**完整性批判加码**: 注意力指数本身零外部基准(无 turnover/分析师跟随/搜索量/头版位置相关性),而引的 DEG 2011 全部贡献正是这个验证。
- **已落地部分**(勿重做): 收敛≠效度的免责声明已加(`tone_validation.py:13-16`);gold_source 门控、Wilson/kappa CI、population-weighted accuracy 已落地(commit 9b0351e9);空标注时 fail-close 写 pending 不造假。
- **修复(P1, 主要是人工, 代码 $0)**: 抽 population-weighted 分层样本,≥2 **盲**编码者,报 Krippendorff α / Cohen κ + bootstrap CI + accuracy/P/R/F1 vs 共识。填 `32_human_samples.xlsx` / `09_sentiment_verify_*.xlsx` 后重跑 stage 33/34($0,eval 层不碰面板,无 golden 重生)。**注意**: 现有工作簿**非盲**(带机器 LLM 列),盲编码需先 strip 机器列(schema 改动,需 user 签字)。另加注意力指数对任意可得非文本基准的外部效度检验,或至少内部头版位置收敛。

---

## 4. P2 must-fix(经核验)

### 识别 / IV
- **ID-2 [finder-flagged] ⭐ 同期 peer-LOO 做 2SLS 主工具,而反射问题的真正解药 `_lag1` 已生产却闲置**。`iv_extensions.py` 已建 `{out_col}_lag1`,但 substance/22、collab/21、benefit/25、attention/19 的 2SLS 列全用**同期**同类×年 peer 均值(只有 locus/20 有 `tsls_lag`)。模板禁 type×year FE → 同类×年共同冲击(P2P 整治、蚂蚁 IPO 暂停、数据出境)未被吸收 → 同期 LOO 机械相关于结构误差 = 反射违背(Manski 1993)。**T=18 放大**(跨多个行业冲击)。**修复**: 把 `_lag1` 提为主工具或与同期并列报告;每个模板补 `tsls_lag` 列镜像 locus/20。(注:新列 → stage 45/46 + golden 重生)
- **ID-1 (verified) Anderson-Rubin 弱工具稳健 CI 在每个模板注释里规定却从不计算**。7 个 2SLS 模板都让读者"KP F<16.38 时看 AR CI",但无模板跑 `weakiv/condivreg/rivtest`。**T=18 放大**(一阶段真跑且 peer-LOO/Bartik 在 ~4 类组上 notoriously 弱)。**修复(golden-safe, Stata only)**: 加 `weakiv`(注意它是独立估计命令非后估)+ `capture which weakiv` 守卫 + doctor 补 ado 依赖检查(现查零 ado);esttab stats 名单须 lockstep。
- **ID-4 (verified) Bartik 声称 GPSS 份额外生,但基期份额是同类共现频率,可能相关于焦点行 T0 媒体显著性**。无 Rotemberg 权重诊断 / 高权重份额 placebo。**修复(golden-safe)**: 加 `bartik_weight` ado(`capture which` 守卫)+ share-vs-pretrend 相关块 + 论文一句话。
- **ID-6 (verified) P1 省级-LOO 主工具纯同期无 lag 变体** —— 旗舰 Table A6 col 1 用同期同省年 peer tone,正是反射未识别对象。**修复**: 加 `prov_leave1out_tone_lag1`(29 字符 OK,勿扩到 dict/bert 家族会超 32 字符);或纯论文文本走 Gurun-Butler 本地媒体排他性论证(line 142 已半present)。
- **ID-5 (verified) 单向 bank 聚类,无双向(bank×year)或 few-treated wild bootstrap**。宏观金融科技冲击年内相关 → bank-only 低估 SE;错时 dcep/sandbox 有效处理 cluster(省/cohort)少 → 需 MacKinnon-Webb subcluster bootstrap。**修复(golden-safe)**: 加 P2 聚合/推断稳健性模板(镜像 substance/23 Panel B 双向 cluster);错时 spec 加 `boottest ... bootcluster(prov_id)` 并披露 G_treated。

### 推断 / p-hacking
- **FWER 跨注意力测度族全缺**(完整性批判,verified)。`18_attention_robustness.do.tmpl:42` 只对单一主 DV 跑 `rwolf`,124-127 把 index_ctx/disp/pct 当**独立未校正**回归。全族 ~10 firm-level + 6 geo × outcomes × EW/VW/MW/HW × full/ctx。brokerage_network 有 22-metric wyoung 战队,注意力论文(测度农场最大的那篇)零。**修复(golden-safe Stata)**: 移植 brokerage wyoung/rwolf 模式覆盖 ~16 处理族 + 加 PAP/单一主假设声明。

### 聚合 / 权重
- **AGG-5 (verified) dict/BERT 加权聚合用物理 Σweight 分母,分子对短/空文本可能 NaN** —— encode-01 只修了 LLM 族。IDF dict 分数 NaN-skip 但 mention_density/authority/herd 分母仍计权 → dict-IDF VW/MW/HW tone 向零衰减。**T=18 放大**(17M 短文本占比稳定非零)。**修复**: valid-mask 分母(类比 `_build_llm_valid_masked_weights`),扩到 core-dict `_score` 不只 IDF。(改列值 → golden 重生,defer 到生产 run)

### 确定性 / 可复现
- **DET-1 确定性证明在生产规模上空洞**(verified)。`verify_stage21_cache_coverage` 迭代 1170 行 T=2 帧(7020 lookup)报**绝对** miss 数,17M 帧未覆盖也会打印 7020/7020 PASS。已缓解(非静默): `NEWS_PROCESS_LLM_OFFLINE=1` miss 即 fail-close。**修复(golden-safe)**: 改 corpus-parametric(`--input`,分数覆盖率 + 全语料分母),golden 重生门控在 coverage==1.0,gated 在 M0 付费 stage-21 事件后。

---

## 5. 最重复且仍未修:ATT-2 地理层 verified-universe 门控

> 4 个独立 finder(FL-1 / ATT-2-GEO-1 / DI-4 / CIT-5)都标 **P1**;终裁 grep 复核后**下调 P2**(原因:当前 `ft_attn_*/ft_vol_*` 只喂 `bank_fintech_tone/tables.py` 的 Table 1 **描述性**行,year 层有 year-FE-吸收脚注,**不喂任何 IV 或回归系数**)。

- **代码证据**(grep 核验): `compute_fintech_attention_index`(`attention_media.py:558-559`)与 `_build_geo_index`(:654-655)从**未门控**的 `12_fintech_news_full` 数 `is_fintech_news==True`,**零** `restrict_to_verified` 调用 —— firm-level 拿到门控(376/395),geo 没有。docstring 320-323 自承 "ft_attn_* 仍未门控(ATT-2,deferred)"。~26.8% LLM 判伪 fintech 漏入 `ft_attn_*/ft_vol_*`。
- **为何 P1-at-T=18**: 全量盘上省/市 LOO 指数重获功效并成为地理 Bartik 曝露 IV 的输入 → 26.8% 污染从描述性比值升级为**污染识别工具**。
- **修复**: 在 `compute_fintech_attention_index` 数 `is_fintech_news` 前对 fintech 行 `restrict_to_verified`(只门控分子,分母保持 `12_full` 全宇宙以保 Fang-Peress agenda-share 语义);加 `test_verified_gate_applied` 类比测试。**地理层 DiD/IV 在 T=18 激活前必须先落此修复。**(→ stage 45/46 + golden 重生)

---

## 6. 完整性批判:10 维度漏掉的盲区

### 漏掉的注意力构念(全 grep 零命中,$0 可建于 T=18)
1. **策略时机注意力** — Friday/周末/节假日/day-of-week(DellaVigna-Pollet 2009;Michaely-Rubin-Vedrashko)。`日期` 列现成,$0,从未建。
2. **异常/期望-vs-实现注意力残差** — firm-FE/size-expected 残差才是顶刊要的**干净识别冲击**,raw level 被机械的银行规模/语料基污染。零脚手架。
3. **年内爆发度/聚集** — daily 文章数的 temporal-HHI/Gini(区别于 `attention_disp` 的**跨媒体** HHI)。冲击 vs 细水长流,under/over-reaction 文献核心。
4. **持续性/半衰期** — firm-level 注意力 AR(1)/衰减半衰期状态变量(区别于 herd_decay 的情感衰减)。T=18 才可估 within-bank 自相关。
5. **好/坏消息覆盖量不对称** — tone-conditioned 注意力量拆分(负面偏向,Soroka)。有 tone 有 attention 但从不相乘成有符号注意力。
6. **银行×金融科技实体共注意** — `co_mentioned_banks` 是银行-银行,非银行-金融科技实体共现显著性。
7. **显著性加权注意力指数(stranded inputs,verified)** — `frac_front_page/avg_page_rank/staff_written_frac/frac_target_in_lead`(`encode.py:718-723`)被聚合却**不加权任何指数**。`Σ intensity·front_page_weight` 是 Boudoukh 2019 prominence-weighted 构念,离现成只差一次 merge。

### 漏掉的审计角度
- **注意力指数的外部/criterion 效度**(Dim 8 只覆盖了情感测度,漏了注意力指数族)。
- **18 年语料构成漂移**(= P1-A,无维度 own)。
- **注意力论文的 FWER/p-hacking 纪律**(= 上文)。
- **新闻媒介外的可推广性** — 全为报纸,中国国媒主导系统性偏覆盖某些银行类型;无社媒/监管讲话/财报电话外部效度问。
- **测量误差衰减偏误** — intensity 是 IDF×cosine、per-run 缩尾、门控前被假 fintech 污染的噪声估计构念;无 reliability-ratio/split-half(T=18 可做)。

---

## 7. 数据完整性(17M 规模)[多为 finder-flagged,生产 run 前必查]

- **DI-1 [finder-flagged] ⭐ 本分支 dedup.py 缺 N4 传递性过删修复**(pairwise 真-Jaccard 复核)。HEAD(`fix/network-metrics-audit`)缺 commit `28b4ab93`(在 main 上)。**memory `push-all-changes-session-2026-06-13` 交叉佐证**: 该 dedup.py N4 修复"刻意排除、本分支落后 origin/main"。生产 dedup 走未修的传递删除版;J_eff≈0.82 banding 下真 J=0.80 仅 ~40% 检出 → 簇噪声 + 传递过删非随机下偏 `n_fintech_articles`(高覆盖大行更糟)。**修复**: cherry-pick `28b4ab93` 到本分支,config fallback 阈值设 0.80。
- **DI-2 [finder-flagged] ⭐ balance_panel spine = 仅被覆盖银行;1771 行 NFRA 主名册 ~95%(从未被覆盖银行)静默丢弃** —— 外延边际/Merton 投资者识别选择性。`encode.py:1834` `all_banks=panel['target_bank'].unique()`,无与 `bank_list.yaml`(1771 行)merge。媒体注意力的"从无覆盖到有覆盖"外延边际**结构不可观测**,系数 conditional on coverage>0 内生选择。**修复**: spine 从 1771 商业银行主名册 × [2007..2024] 起,LEFT-join 覆盖,加 `has_coverage` 指示 + 按 tier 报从未覆盖集规模;或显式声明样本限制 + Heckman 外延边际稳健性。
- **DI-3 [finder-flagged] 无年份范围校验** —— 单条畸形/越界日期(17M 异构行近必然)使 `range(year.min(), year.max()+1)` 给**每个银行**造幻影年。**修复**: `parse_time` 后硬过滤 year∈[2007,2024] + 逐年保留直方图 + from_product 前断言 min/max。
- **DI-6 / DEDUP-SENS-SCALE-1 [finder-flagged] dedup 无规模守卫** —— 对全 17M 建单个 in-RAM MinHash/LSH + 全 `标题+内容` 串拷贝(~17GB MinHash + dict 复制 + 全文列)。128GB 机临界,无优雅降级;若 OOM 要么失败要么静默采样(破确定性)。`dedup_sensitivity` 每变体重算全语料 LSH,更糟。**修复**: 按日期窗(5 busday,镜像 `article_staleness.py` 的 per-day rolling LSH)分块,流式 hash,加 peak-RAM/行数断言防静默采样;≥1M 基准测试后再声称可生产 run。
- **DI-5 [finder-flagged] 内容 10000 字上限矛盾于所引 TSM 2008(无上限)** —— 非随机丢最长最富信息文章。**修复**: 去上限靠年度标准化控杠杆,或跑并报截断敏感性矩阵(`_DIAG_MAX_CUTOFFS` 已 log 保留数)。
- **DI-8 [finder-flagged] 日期解析全靠 format-free `errors='coerce'` 跨 18 异构源年** —— 静默 NaT-drop 无逐年分解 = 构成漂移盲点。**修复**: profile 逐源/年格式,显式 format list 或 `format='mixed'` + 失败样本 log + 逐年保留/丢弃表。
- **FRESH-1 [finder-flagged] 注意力分子输入(14/12)对更新的门控(24_herd_decay)无 mtime 新鲜度守卫** —— 对比 `runner.py:305-343` opt-in merge **有** mtime 守卫。盘上 14=Jun5 / 24=Jun13(分子旧于门控)。**修复**: 加 mtime 守卫,门控新于分子时 loud-warn/raise。

---

## 8. 引文完整性

- **CIT-1 [finder-flagged] ⭐ `encode.py:369` Hillert-Jacobs-Müller (2014) 硬误引**: 标 "Journal of Finance, 69(5), 2095-2143",实为 **RFS 27(12):3467-3501**(DOI 10.1093/rfs/hhu061)。同文件 1131 行自相矛盾写 "RFS"。codebook/LITERATURE_ANCHORS 已正确,encode.py 是唯一残留 outlier。**memory `citation-corrections` + 上轮 workflow 交叉佐证**。**修复**: 订正 + 加 source-text lock 测试(断言 "Journal of Finance, 69(5)" 不与 "Hillert" 共现)+ 全树 grep。
- **DI-7 [finder-flagged] `article_staleness.py:45-46` "Text as Data" 误作 Gentzkow, Shapiro & Taddy** —— 正确为 **Gentzkow, Kelly & Taddy** (2019 JEL 57(3):535-574, DOI 10.1257/jel.20181020)。**上轮 workflow 已独立逮到同一误引**。**修复**: 订正 + 全树/refs.bib grep Shapiro-Taddy 变体。
- **CIT-2/3/5 [finder-flagged] DEG 2011 claim-fit 拉伸**: `attention_media.py:469` 把 DEG 2011(Google-SVI **直接**注意力,论文主旨是报纸覆盖是它取代的**劣质**代理)当报纸覆盖比值的"经典范式"。且 DEG 2011 未进 `LITERATURE_ANCHORS` 审计文档(un-vetted live cite)。**修复**: 改框架 —— Fang-Peress 2009 为主锚,DEG 2011 降为 disclosed contrast("无搜索量数据,报纸覆盖作间接代理,cf. Da et al. 2011");补进 LITERATURE_ANCHORS §5 过 Crossref/claim-fit。
- **CIT-4 [finder-flagged] `paper_spec.yaml` 把 `attention_index=ln(1+Σintensity)` 标 "Fang-Peress 式"略过度** —— Fang-Peress 是无权**计数**,本指数是 intensity 加权和。**修复**: 软化措辞为 "Fang-Peress 外延覆盖构念的 intensity 加权扩展"。
- **CIT-6 (verified) 清白核验**: Hassan QJE qjz021 / GPSS AER aer.20181047 / BHJ REStud rdab030 / Gentzkow-Shapiro ECMA ECTA7195 / Dougal RFS hhr133 / Gurun-Butler JF 2012.01725.x / Bushee JAR 2009.00357.x / Tetlock RFS hhq141 / Bybee JF jofi.13377 / Engelberg-Parsons JF 2010.01626.x —— **全 Crossref 核验 MATCH**,先前 fabricated DOI(Hassan qjz009 / Tetlock JF)在 live code 已全订正。

---

## 9. 已确认正确(clean bills,核验得出 —— 勿误改)

- **ATT-1 firm-level verified-universe 门控已正确落地**(`attention_media.py:376/395`,1170→857)。
- **双轨 full/ctx 红线已强制执行**(无 Hansen-J 叠加;benefit `tsls_overid_ctx` 是合法跨族 type-LOO×zone-LOO,非同轨叠加)。
- **错时 `dcep_/sandbox_` DiD 列 + `_lag1` peer-LOO 工具已物化在面板上**(`iv_did.py:709-764`,`runner.py:1252`),已存活进单列 `.dta`。
- **确定性锚点真实**(离线模式 cache miss fail-close)。
- **GEO-3 (verified) `ft_vol` prov/city = ln1p-of-mean 构建正确**(test 核验 A=ln1p(3)),codebook 已正确披露"二阶邻域曝露量非银行自身覆盖计数",非误标。
- **AGG-6 (verified) 覆盖筛选 k=3,5 + frac 分母对齐正确**(按设计 EW 列筛、加权列报全样本,memory `agg-robustness-impl` 佐证)。

---

## 10. 推荐修复顺序

1. **(P1, golden-safe, $0, 最先)** 审计并披露语料构成漂移(逐年 outlet/length/wire/geo 表 + 分时代稳定性 + 时变基准归一化)。去风险整个 T=18 识别前提,不改面板列。
2. **(P1, golden-safe Stata+spec, $0)** reconcile 面板识别 —— Route B 重指到 `dcep_/sandbox_` 生产者 + `csdid notyet`;或 Route A 写缺失 producer。闭合 ID-1/ID-3/ID-7。
3. **(P1, 人工为主, 代码 $0)** 立人工 criterion validity(盲编码 + Krippendorff/κ + bootstrap CI)+ 注意力指数外部效度。重跑 stage 33/34 不碰面板。
4. **(P2, golden-safe Stata)** 加 FWER 战队(wyoung/rwolf)覆盖 ~16 处理族 + PAP 声明。
5. **(P2, golden-safe)** determinism verifier 改 corpus-parametric;把已物化的 dedup-sensitivity `_jXXwY` 列 + `_lag1` peer-LOO IV 接进 esttab。全 $0 不重跑。
6. **(P2-P3, DEFER 到受控生产 golden 重生)** 建新面板列(opt-in/always-on-with-N-guard): ATT-2 geo 门控 / 异常+持续性残差 / 爆发度 / 策略时机 / 显著性加权指数(NaN→weight-1) / 有符号本地-非本地 geo 差(GEO-4) / `_lag1` 激活 / dict-BERT valid-mask 分母 / config 驱动同公司 staleness 窗。**全须遵双轨红线 + 新分子套 ATT-1 verified-universe semi-join。**
7. **(P3, hygiene)** rebase 分支到 main 使 dedup.py = 已合并的 N4 真-Jaccard 复核(`28b4ab93` 已是 main 祖先,**勿重实现**);加 A-B-C 传递幂等回归测试;订正 `26_tableA7:102` "salience-weighted" 误标;加 `weakiv/bartik_weight` ado 守卫 + doctor ado 依赖检查;**17M run 前加 blocked/streaming dedup fallback(当前全局 in-RAM MinHash 会 OOM)**。

---

## 附:false-positive / 已下调(勿追)

- 多条原标 P1 的发现经 TWFE bank FE 已吸收 level/size 污染而下调 P2/P3(COV-1 abnormal attention 在 `reghdfe absorb(bank_id year)` 下非偏系数,是稳健性变体非偏差修正)。
- ID-5 dual-track 红线 = 清白确认(无 Hansen-J 叠加)。
- GEO-3 = 已在代码(label 已正确)。
- 2 条 false-positive(severity drop)已从清单剔除。

**验证状态**: 41/68 经独立对抗核验;27/68 finder-flagged(会话 token 上限中断核验阶段),其中 ATT-2 门控 / 引文 / dedup N4 / balance spine 等关键项被终裁 grep 或项目 memory 交叉佐证。建议会话额度恢复后 resume workflow(`resumeFromRunId`)补齐 27 条对抗核验。

---

## 11. 核验后修订(2026-06-14,9-agent 顶刊对抗核验 wf_30f775dc 终裁后)

对已落地修复(worktree commits 9460f3d9 + bf1fb393 + 43476f3a)做的多智能体核验**终裁 = minor-issues,三 commit 安全保留**:引文 6 条全 web 核验 clean(Hillert RFS 27(12):3467-3501 / Gentzkow-**Kelly**-Taddy / Bushee .00357 / DEG reframe 与原文"news 是 SVI 取代的间接代理"一致 / Fang-Peress / Andrews-Stock-Sun 全对),golden 安全 clean,DET-1/测试 clean,`weakiv`-after-`eststo` e() 完整性正确,hollow-fix 风险已清(`dcep_post`/`dcep_treat_year` 确在 `.dta`)。已就地整改的 P2/P3(commit 43476f3a):M7 csdid 把注意力移出协变量+改标"DCEP 正交政策辅助"、never-treated 论据订正、ID-4 deferral 原因订正、引文计数一致、00_master 补 ado。

**核验另逮出两条 PLAN 级 P1(属计划而非已落地代码,须并入待办)**:

- **P1-PLAN-1 locus 事件研究传染未修**: P1-B/ID-3 在原审计是**一个**发现(attention M6 + locus/collab 事件研究 + spec E1-E5b),但 batch-2 只修了 attention `15_` M6。`bank_fintech_locus/19_locus_event_study.do.tmpl:36` 仍消费**零生产者**的 `post_E*/treat_E*_year/never_treated_E*`(`locus/00_master:44` LIVE 调用),`eventstudyinteract` 静默 capture-skip → P4 事件研究是空头承诺。(核验确认 `collab/19` **不**受影响,用真实列 `collab_open_full`,故范围仅 locus。)**待办**:把 `locus/19` 重指到已物化 `dcep_/sandbox_` 生产者(+ Sun-Abraham/csdid notyet,镜像 `15_` 修复),或在文件内显式披露 P4 事件研究非operational + reconcile attention `paper_spec.yaml` 的 `event_studies:[E1-E5b]` 到同步 post-dummy 生产者。

- **P1-PLAN-2 ATT-2 §5 下调前提经实证为假 → 应回 P1**: §5 把 ATT-2 下调 P2 的理由是"geo attention 仅喂 Table 1 描述行,不喂任何 IV/系数"。**该前提错**:`falsification_template.do.tmpl:336/345` 已用**未门控**的 `ft_attn_prov`/`ft_attn_city` 在 2SLS 工具化 `llm_vote_tone_full`,:427 还把两者做 Hansen-J overid;且三列在**盘面 T=2 实存**(`ft_attn_prov`/`city` nonnull=150,`llm_vote_tone_full`=117)→ `ivreghdfe Y (llm_vote_tone_full = ft_attn_prov)` **今天即可跑**,26.8% 未门控假 fintech 污染**当前就流入识别**,非 T=18 未来风险。**待办**:ATT-2 回 P1;geo 数值门控(`compute_fintech_attention_index` 分子 `restrict_to_verified`)须在任何 geo-IV 表(含 falsification 表)发表前落地,**不**作 Tier-2 延后列。

**核验逮出的 plan 遗漏(并入待办)**:① ID-1 AR-CI 推广清单漏 `llm_peer/11_table2_main_iv_2sls`(且"6 个"实列 7 个,应为含 llm_peer 共 8 个 live 2SLS 模板)+ doctor 须补 ado 依赖检查(否则 capture-which-weakiv 在复现包静默吞掉 AR-CI);② §6 漏的 $0 构念 #5 有符号/不对称语调加权注意力(Σ intensity·sign(tone),Soroka,**区别于** GEO-4 的地理本地-非本地)+ #6 银行×fintech 实体共注意,应进 Tier-2;③ 注意力指数**外部/criterion 效度**(区别于 P1-C 的 11 情感测度人工金标准)+ 测量误差衰减 reliability-ratio/split-half(T=18 $0);④ §7 数据完整性 DI-5(10000 字上限矛盾 TSM 2008)/ DI-8(format-free 日期解析逐年 NaT 漂移)/ FRESH-1(分子 14/12 比门控 24 旧无 mtime 守卫,**盘面实证**:`40_panel_yearly` Jun10 旧于 `24_herd_decay` Jun13,且 4f4e725b 的 IV 列**未落盘**)须进生产 run 检查单;⑤ ID-2 `_lag1` 的 $0 分类须注明基线:**已重生面板**上 `_lag1` 已物化=$0,**当前陈旧盘面**上 IV 列缺失,接 esttab 须先重生(`leave_one_out_peer_*_iv*` 当前不在盘)。

**核验诚实披露**:batch-2 两修复在**盘面 T=2 全部 inert**(M6 `dcep_post` 全 0 → 跳过;19_ 三 IV 列均缺 → weakiv 不触发),仅在合成 smoke 盘验证过;真实数据验证须 gate 到 T=18 生产 run(勿把 gitignored `build/` 绿 smoke 当真实数据正确性证明)。
