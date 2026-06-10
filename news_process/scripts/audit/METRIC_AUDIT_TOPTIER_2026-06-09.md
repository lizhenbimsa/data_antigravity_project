# news_process 指标计算体系 — 顶刊标准系统审计 (2026-06-09)

> 本报告是对 v3.8.0 (post stage16/17/19 移除 + dual-track twin 补全 + 15 族文本测度新增 + degradation 修复, HEAD `5bbb00b1`) 的**全量指标实现审计**。覆盖上一轮全面审计 (`METRIC_AUDIT_V3_2026-06-02.md`) 之后**新增/变更的指标面**(此前从未经顶刊标准审过),并回归核验历史修复是否守住。

> **⚠ 校准更新 (2026-06-10, 见 `METRIC_AUDIT_METAVERIFY_CLOSURE_2026-06-10.md`)**: 本报告经最高标准终审核查(37 条独立重证伪 + 覆盖扫描),**96% 站得住(33/37 upheld)**。变更:`tonellms prob-score` **升 P2→P1**(falsification DV 完整性);`lmfls-01`、`stratdiff-centroid` **降 P2→P3**;`stata-export46` **判 env-conditional 假阳性**。新增 ~10 条覆盖发现(最重要:**clarity 加权均值 P1 同型兄弟**)。**两处自纠**:(1) 本报告 §7/§0 沿用的 "Tetlock (2011, JF)" **应为 RFS 24(5)**;(2) §6 "全仓无其他模块对 Int8 计数列裸算术" **不完整 —— `stata_audit.py:357` 有 `pos+neg` Int8 裸加法**(latent)。最终清单 ~6 P1 / ~24 P2 / ~10 P3 / 8 假阳性。以闭合报告为准。

**审计日期**: 2026-06-09
**方法**: 31 个指标族审查单元 × (referee review → 对抗 verify + 公式溯源 verify) 多智能体工作流 (**88 agents / 6.5M tokens / 1787 tool-uses / ~21min**) → **主控亲验最高价值发现 7/7 坐实** + 严重度重校准 + 与历史审计对账。
**环境**: Python 3.14.3 / pandas 3.0.3 / numpy 2.4.6 / jieba 0.42.1 (冻结); 盘上面板 = T=2 试跑样本 (174 行, 2017–2018, = 全量 17M/T=18 语料的 0.055%)。
**口径**: $0 只读审计 — 不动 `_llm_cache.db`、不付费重跑。

---

## 0. 主控亲验结论 (本报告可信度锚)

不照单全收工作流的 38 条 confirmed。对最高价值、最可操作的发现**亲自跑代码 + 盘上数据复现**:

| # | 发现 | 主控复现证据 | 裁决 |
|---|------|------------|------|
| A | lexical `function_word_ratio` 把所有英文 token 当虚词 | 纯英文文本 → ratio=**1.0**;中英混排 → 0.417(被 FinTech/APP/GDP/ESG 抬高) | ✅ 真(新模块) |
| B | Janis-Fadner 分母用 `(P+N)²` 而非 canonical `t²`(含中性) | P=10,N=0,中性=90:代码 JF=**1.0** vs canonical **0.01** | ✅ 真(公式偏离+误引) |
| C | strategic_diff LDA-JSD 用 base-e 而非 docstring 宣称的 base-2/[0,1] | 盘上 `strat_diff_n5_lda` max=**0.8260**≈√ln2;`coh_lda` 底=0.1813 | ✅ 真 |
| D | network `peer_tone` 用 `fillna(0)` 把缺 tone 同行注入为 0 | `peer_tone_2nd_lag1_full` min=**0.0**(4 个伪零)vs 一阶 min=0.8667;ctx 均值 0.921<full 0.962 | ✅ 真(P1) |
| E | risk `loan_loss_provision_discretion` 是裸 LLP/贷款比率却标为 BW2012 残差 | residual 模板**不存在**;`paper_spec.yaml:71` 标 "Bushman-Williams 2012 JAE DIRECT MATCH" | ✅ 真(P1) |
| F | fintech `intensity_verified` 门控算了从不消费 | `pipeline/panel/` 下 `intensity_verified` **0 命中** | ✅ 真 |
| G | herd_decay 同日 unstable quicksort → `llm_vote_tone_hw` 漂移 | 主控独立推导 + 工作流对拍一致(见下) | ✅ 真 |

**额外回归核验(历史修复守住)**: JF 边界严格 `[-1,1]`✓;180 个比率列**零越界**(ctx 对角修复守住)✓;W² `fill_diagonal`✓;peer_cov 孤立掩码✓;tone_gap min-n 守卫(12 处)✓;jieba 词典注入✓;F1 LLM 禁用 `verified=False`✓;F11 fintech 降级→ERROR✓。

**对工作流可信度的判断**: 主控亲验 7/7 命中 + 对抗 verifier 已自校准(38 confirmed / 6 refuted,refuted 含 2 个"机制对但非 bug")→ **机制识别可靠,定级合理**。下文按主控重校准给级。

---

## 1. 执行摘要

**整体结论:单指标算法引擎(LLM 投票/词典状态机/herd decay/policy cosine/Burt/HTMT)仍达顶刊水准且历史核心修复守住;但缺陷集中在三个层面 —— (1) 聚合域不匹配(valid vs physical)、(2) 公式/引文保真度(多处误引顶刊 + 派生指标偏离 canonical 公式)、(3) 文本测度新族与登记/复现包工程质量。**

关键元结论:**`METRIC_AUDIT_V3` §7「阶段1 横切根因」路线图(加权均值分母、verified 门控掩码、staleness 确定性、embedding L2 归一、herd tie、词典分母)在很大程度上从未执行** —— 这些修复当时被 cost-gate/defer,至今在 HEAD 仍开放。closure 批次实际落地的是另一组较小集合(peer_cov / tone_gap min-n / jieba 注入 / content_full 对称 / JF float 转换)。

### 确认问题计数(主控重校准后)

| 级别 | 数量 | 说明 |
|---|---:|---|
| **P1(实质缺陷,进发表回归)** | **5** | 聚合域 ×2 + 网络伪零 + 两个构念/引文严重错配 |
| **P2(真缺陷,须修)** | **~20** | 公式/引文保真 + 聚合域 + 双轨 + 降级透明 |
| **P3(latent/边界/卫生)** | **~6** | 仅 T=18 或边界触发 |
| **T=2 识别限制(非 bug,须披露)** | **1** | DiD 恒零列(ivdid-01 守护不完整) |
| **推翻的假阳性(诚实记录)** | **6** | 见 §5 |
| **主控独立新增** | **2** | codebook 内容失真 + Int8 算术 landmine |

---

## 2. P1 净清单(5 条,进发表产物,须优先修)

### P1-1 · `fintech_share` 分子分母计数基不一致 → 污染 Stata 赛马交互
- **file**: `pipeline/falsification/controls.py:339-343,607,615-619`;分子源 `encode.py:594`
- **问题**: 分子 `n_articles` = 面板**物理** firm-document 行计数(无 `(bank,标题,日期)` 去重);分母 NF 部分 `nf_n_articles` 来自**去重后** anti-join。`share=A/(A+B)` 要求 A、B 同计数基。盘上实测:物理 857 行 vs 去重 849;最坏单 bank-year 偏 **7.05pp**。被 `falsification_template.do.tmpl:47` 的 `c.llm_vote_tone##c.fintech_share` 交互直接消费。
- **违反**: Hassan (2019 QJE) Table 7 的 PRisk/(PRisk+NPRisk) 要求同一语料互补划分、单一计数基。
- **状态**: **历史已知(falsification-01 / finding_91, V3 定 P1),修复从未落地**。
- **修**: 分子改用 anti-join 同源的去重计数;$0 本地重算 + 重生 golden。

### P1-2 · VW/MW/HW 加权语调:valid-only 分子 ÷ physical-domain 权重和分母 → 系统性向零衰减
- **file**: `pipeline/panel/encode.py:1447-1451,1481-1482,1523-1526`(分子);`634,668,708-709`(分母权重和)
- **问题**: 三族加权语调(价值加权 VW / 媒体权威 MW / 跟风衰减 HW)分子 `Σ(w·score)` 因 `score` 对 LLM-invalid 行为 `<NA>` 而**只覆盖 valid 文章**,但分母 `Σw`(`sum_mention_density`/`sum_media_authority_weight`/`sum_herd_weight`)对**全部物理文章**求和。结果 = `Σ_valid(w·score)/Σ_all(w)`,被因子 (valid 权重质量/总权重质量)<1 系统性拉向 0(attenuation),随 LLM-invalid 占比增大而恶化 → 直接衰减头条语调回归系数。
- **违反**: 加权均值要求分子分母同观测域(Hassan 2019 / Holzman et al. 2023 TAR / Tetlock 2011)。
- **状态**: **历史已知(encode-01, V3 §7 阶段1 R2 P1),从未执行**。
- **修**: 分母按 track 的 valid mask 重算(`sum_*_valid{track}`);$0 + golden 重生。

### P1-3 · network `peer_tone` 把缺 tone 同行伪零注入 + 双轨不对称衰减
- **file**: `pipeline/panel/network_spillover.py:272-273,281,314,1240`
- **问题**: W 在知道哪些同行有有效滞后 tone **之前**就按全部共提同行行归一到 1;`tone_vec.fillna(0)` 后 `W@tone` → 缺 tone 同行(NaN,因无文章/掉出面板)以 tone=0 进分子但权重仍在分母。盘上 57/174(full)、70/174(ctx)的 `llm_vote_tone` 为 NaN;`peer_tone_2nd_lag1_full` min=**0.0**(主控实测 4 个伪零),mean 0.725 vs 一阶 0.962。**且**两轨 NaN 数不同(2017 lag:full 15 vs ctx 24)→ ctx 被更多伪零稀释(mean 0.921<full 0.962),双轨分歧来自缺失伪差而非归因窗口(破坏互为稳健语义)。
- **违反**: 行随机空间滞后/同行均值须对**有 tone 观测**的同行求均值并重归一(LeSage-Pace 2009;Leary-Roberts 2014 JF)。
- **状态**: **peer_cov(peer_fintech_exposure)的同型修复已落地(completeness-01),但 peer_tone 兄弟站点漏修**。
- **修**: 按观测掩码重归一 `(W[:,mask]@tone[mask])/W[:,mask].sum`,denom=0→NaN;同步修 W² 二阶。$0 + golden 重生(注:3 个 centrality 列 BLAS-FP 非确定,验证时排除)。

### P1-4 · `loan_loss_provision_discretion` 是裸 LLP/贷款比率却被当 BW2012 "DIRECT MATCH" 残差消费
- **file**: `pipeline/panel/risk_taking_outcomes.py:223-247`(诚实 docstring);消费端 `papers/bank_news_clarity/stata_templates/11_table2_main_clarity_risk.do.tmpl:55-68`、`paper_spec.yaml:71,76,234`
- **问题**: 函数返回裸 LLP/总贷款比率;其 docstring 已诚实声明"非 BW2012 残差,residual regression 未实现,模板 `12_table3_bw2012_llp_residual.do.tmpl` 待 M5 创建"。主控核实:该残差模板**确不存在**。但列名 `*_discretion`、Stata 表标 "BW2012 LLP / Bushman-Williams 2012 JAE direct match"、`paper_spec.yaml` 标 "DIRECT MATCH"、主刊 JAE "direct anchor"。BW2012 的 discretion = `LLP/Loans = a+b1·ΔNPL+b2·ΔLoans+b3·GDP+e` 的**残差 e**,而非 LHS 本身。把基本面驱动(非自由裁量)的拨备水平当自由裁量拨备呈现 = **顶刊致命错配**。
- **状态**: **NEW**。
- **修**: (a) 列改名 `loan_loss_provision_ratio` 并去除所有 BW2012/discretion 标注;或 (b) 实现基本面回归真正产出残差后再称 discretion。

### P1-5 · (拆自 P1-3 同根,合并计) — 见 P1-3 双轨不对称facet。

> 注:JF 分母偏离(主控亲验 B,代码 JF=1.0 vs canonical 0.01)严重度处于 **P1-watch / 高 P2** —— as-implemented 是内部自洽的"仅有效方向极性指数",但**误引** Janis-Fadner(1965)/Deephouse(2000)且丢弃中性覆盖。见 P2-公式族。

---

## 3. P2 清单(~20,按根因分组)

### R-A 公式/引文保真度(误引顶刊 / 偏离 canonical)
- **JF 分母 `(P+N)²` vs canonical `t²`(含中性)** `runner.py:1473-1520` — 主控亲验 B,偏离 Deephouse(2000)。修:用 `n_articles_llm_valid` 作 t,或停止援引 JF/Deephouse 改记为自定义极性指数。
- **`peer_fintech_exposure` 误引 Berger et al.(2022 JFI)** `network_spillover.py:299-305` — 该文是 EPU→流动性囤积,不定义同行共提空间滞后;实为 LeSage-Pace(2009)。修:改引文(纯文档 $0)。
- **`auth_sim` 误引 Hassan(2019 QJE)余弦法** `policy_similarity.py:10-11,64-70` — Hassan 是窗口 bigram 频率,非"微观向量↔宏观锚向量余弦";实为 Hoberg-Phillips(2016)/Guzman-Li(2023)。修:改引文。
- **`z_score` 是 CAR-based 变体却标 Laeven-Levine(2009)标准 Z** `risk_taking_outcomes.py:173-189` 诚实但 `dag.py:313`/`paper_spec.yaml:65`/Stata 表头标 L&L 标准 — 资本项用监管 CAR(RWA 加权)而非 L&L 的账面 equity/assets。修:把函数自身的 variant caveat 传播到下游标签。
- **llm_peer cutoff 扫描是 difflib 串匹配严格度,却标为 TNIC/Cao 同行相似度阈值** `llm_peer_iv.py:615,691`;`paper_spec.yaml:49`;Table3/Figure1 模板 — cutoff [0.70–0.90] 只进 `difflib.get_close_matches`(银行名归一),与 TNIC 余弦阈值无关(TNIC=10 邻居上限的引用合法,勿混淆)。修:如实标注 difflib 归一阈值,或实现真正的 peer-set-size 敏感性。
- **`attention_index` 是 extensive 累积 log-sum,但 Hassan(2019)曝光是 intensive 归一化份额** `attention_media.py:224-226,320-321` — 主处理 = `ln(1+Σ intensity)` 未按文章数/token 归一,把曝光强度与覆盖量混淆。同函数已有 intensive 的 `attention_pct`/`attention_intensity_density`。修:重标 extensive 或把 intensive 列设为 spec primary。
- **strategic_diff LDA-JSD base-e vs docstring 宣称 base-2/[0,1]** `strategic_diff.py:468,1072-1073,1124-1126` — 主控亲验 C,实测 max 0.826。修:`jensenshannon(..., base=2)` 两处,或更正 docstring/range 断言。
- **lexical `function_word_ratio` 把所有英文 token(`eng`)误计虚词** `lexical_complexity.py:64,212` — 主控亲验 A,`f[0] in (...,'e')` 撞 `eng`。修:精确 flag 成员判定或 `f!='eng'` 守卫。
- **LM 非情感 frac 分母仍含标点+纯数字 token** `lm_non_sentiment.py:117-138` — 字节级等同 V3 标记的 `lmfls-01`(注:closure 只修了 jieba 注入 lmfls-02,**分母 lmfls-01 从未修**);repo 内 `cn_text_utils._is_valid_token` 已有正确过滤但未复用。修:复用该过滤器。
- **fintech IDF 的 DF(AC 子串)与 TF(jieba 整词)算子不一致** `fintech_intensity.py:117-122 vs 298-299` — 已知 fintech_intensity-01b,实测影响<1%(低)。修:TF/DF 统一到同一 occurrence 算子。
- **39d 判别效度只算 `_full` 轨,但 bank_news_clarity 主处理用 `_ctx`** `lexical_discriminant_validity.py:240-242` — 效度证据未认证论文实际使用的构念(39e 正确做了双轨)。修:双轨各跑一遍,$0。

### R-B 聚合域不匹配(valid vs physical)
- **fintech `intensity_verified` 门控算了从不消费** `encode.py:796-801` — 主控亲验 F(`pipeline/panel/` 0 命中);未验证文章以 score=0 稀释 bank-year 均值(应 NaN-mask,镜像 LLM 轨)。**历史已知 fintech_intensity-01,从未落地**。修:聚合前按 `intensity_verified` mask;$0 + golden。
- **tone_llms `avg_prob_score` 纳入 verified=False 模型** `tone_llms.py:1190-1198,1224` — 离散投票仅纳 verified 模型(F2 契约),连续 prob_score 无此门控 → 主 DV 与稳健 DV 算在不同模型子集。修:连续路径加同款 verified 门控(缓存命中 $0,但变值需 golden)。
- **numerical_intensity 面板加权均值分母含 NaN-num_intensity 文章权重** `encode_collab.py:624-655` — 抵消了 A7 NaN 保护,系统性下偏(latent)。修:分母按 num_intensity 有效性 mask。
- **iv_did `compute_bartik_iv_fintech` 份额分母含 'other'(分子排除)** `iv_did.py:296-307` — media 份额行和均值 0.43 vs type/scale 0.83,两 Bartik 族归一不可比(注释称一致实则不一致)。修:分母限于 kept groups。

### R-C 双轨对称(见 P1-3)
- 已并入 P1-3(network peer_tone 差异化 NaN 注入)。

### R-D 确定性 / 泄漏
- **staleness semantic 轨同日非确定(kind=stable 不足)** `article_staleness.py:214-249` — 同日文章彼此日期相等,stable 仅按输入序保序 → 值随输入排位翻转;盘上 69/72 天为同日多文。**历史已知 stale-tie-01,半成品**。修:窗口下界改严格前序日(对齐 surface 轨)。
- **staleness 双轨窗口不对称 + semantic 同日 look-ahead** `article_staleness.py:149-161,234-246` — surface 严格排除同日,semantic 含"同日早发文"。**历史已知 staleness-02,未修**。修:两轨统一严格排除同日。
- **benefit `pos_frac/neg_frac` 用 in-sample pooled median 二值化后进回归 RHS** `benefit_society.py:631-639` — 阈值取自全样本中位数(T=18 含未来年),非冻结外部锚(latent 泄漏);连续 `benefit_mean` 不受影响(FE 吸收)。修:首跑冻结 `_center` 到 sidecar(镜像 `median_amb_d0`)或论文披露。
- **sbert `encode_local`(text2vec)返回未归一向量,污染 `centroid_diff_emb_t2v`** `embedding_engine.py:113-128` — 缺 `normalize_embeddings=True`,norm~17 与单位范数 pooled 向量混入算术质心,长度加权偏置;主控/工作流实测 std 被压缩(0.0669 vs ~0.0672)。**历史已知 embedding-01/02,未修**。修:`encode_local` 加 `normalize_embeddings=True` 或末端统一 L2 归一(本地 $0)。

### R-E 降级透明 / 工程质量
- **network_brokerage degree_centrality 兜底混入 `brokerage_eigen_cent` 列,记 INFO 而非 docstring 承诺的 CRITICAL,且不写 method 列** `network_brokerage.py:178-179,246-254` — 两种不同 centrality 构念静默同列,下游无法识别污染。修:升 ERROR + 写 `_method` 列,或兜底设 NaN。
- **network_brokerage `industry_neg_shock` 同期 LOO 声称"打破反射效应/满足排他性"** `network_brokerage.py:33-35,297-303` — 同期 LOO 只去机械自相关,不解 Manski(1993)反射;需滞后/工具化。**历史已知 network-04,docstring 未改**。修:改 docstring 或滞后到 t-1。
- **codebook stage46 pandas-fallback 缺 nullable→float 强转(pd.NA → to_stata 崩溃类)** `stata_export.py:560-575` — 与 stage45 `export.py:299` 的强转不对称;仅在 minimal-install + pandas 2.x 触发(latent)。修:fallback 路径补同款强转。
- **validation `radius_sensitivity` 无零方差守卫 → NaN 相关静默进稳健性裁决** `radius_sensitivity.py:497-498,974-975` — 兄弟模块 `decay_sensitivity` 已有该守卫。修:加 `np.std==0` 守卫 + NaN-aware min/mean。
- **validation `threshold.py` path-B 用 `total_with_title` 而生产用 body-only `(upper+lower)`** `threshold.py:120,137-139` — 阈值敏感性扫描的分类器与生产不一致 → 曲线/裁决失真。修:path-B 改 body-only,与 `ahocorasick.py:414-416` 逐位一致。
- **news_salience `page_rank` 多字母版号误解析(SZ02→2502,AII08→808)** `news_salience.py:35,59-69` — 单字母 regex 回溯取最后字母 → 错乱 rank 抬高 `avg_page_rank`。修:锚定串首 + 多字母版段映射表。

---

## 4. P3 清单(latent / 边界 / 卫生)
- **herd_decay 同日 unstable quicksort 无次键 → `llm_vote_tone_hw` run-to-run 漂移** `herd_decay.py:289`(主控亲验 G:聚合 herd_weight 不变,但加权语调因同日不同 tone 的权重分配翻转而漂移)。**历史已知 herd_decay-01,未修**。修:`sort_values(['日期', <stable_id>], kind='stable')`。
- **fintech IDF `log10(N/(1+df))` 可转负**(词近全文档时)`fintech_intensity.py:162` — 偏离所引 Manning smooth IDF(恒非负);盘上未触发(latent),attention 端已 clip 兜底。修:`log10(1+N/(1+df))` 或 `max(0,·)`。
- **tone_berts 空文章 P(pos)=P(neg)=0.0(伪零非 NaN)稀释 bank-year 均值** `tone_berts.py:605-612`;`bert_num_windows` 写了但 `pipeline/panel/` 从不消费。修:空文章置 NaN 或按 `num_windows==0` mask。
- **`ctx_is_fallback` 对 NaN 正文行误算**(pandas 3.0 `astype(str)` 对 NaN 返 float nan,逐行 `str()` 返 'nan' → 比较恒 False)`ctx_materializer.py:121,147-152` — latent,断言因同逻辑自洽而漏检。修:两侧同款 str 强转。
- **ivdid-01 守护不完整:14 个恒零 DiD 列仍进面板/.dta/codebook,仅 warning 未 drop** `iv_did.py:586-592` — **T=2 数据维度退化(处理年≥2019>面板 2018),非代码 bug**,但前修承诺的 drop+ERROR 未落地。全量 T=18 自愈;当前须 ERROR+drop 恒零列以净化复现包。

---

## 5. 推翻的假阳性(诚实记录,6 条)
工作流报出但经对抗 verifier(及主控)推翻:
1. `tone_words` best-dict 双轨不对称(→P3):机制对但 msent/pos_ratio 影响被高估,降级。
2. `tone_berts` 文章级 0.5 阈值跨 2/3 类不一致(→non-bug):前提对但下游用的是 argmax 派生,非该均值阈值。
3. `tone_berts` `bert_avg_pos` skipna 组成漂移(→non-bug):盘上 finbert2 无逐行缺失,声称的活跃漂移不发生。
4. `news_salience` page_rank 把日期串误解析(→non-bug):`页号` 列不含日期(日期是独立列);多字母版号问题(§3 R-A)成立,但"日期串"变体错误。
5. `policy_alignment` MAIN↔t2v 收敛 r~0.36 过低(→non-bug):双轨各用自己模型正确计算,非代码 bug,属须披露的方法学局限。
6. `network_brokerage` 特征向量中心度跨年不可比(→non-bug):公式正确,需 Stata 侧年 FE,非实现缺陷。

---

## 6. 主控独立新增发现(工作流代码视角未覆盖)
- **Codebook 内容严重失真(复现包硬伤,P1-doc)**:`variable_codebook.csv` 1613 变量中 **94.2% 学术引用字段为空、94.0% 描述为「需要人工补充」占位符**;`year` 的「取值范围」标 `[2013,2023]` 但实际 2017–2018。按 Nosek(2018 PNAS)可复现标准,投稿级 codebook 不可有 94% 空引用。修:从模块 docstring/`stata_export` 标签批量回填引用 + 修元数据派生($0)。
- **Int8 计数列下游算术 landmine(P2 卫生)**:12 个面板列(`pos_count`/`neg_count`/各 LLM `*_tone_sum`×full/ctx)存为 Int8。**澄清(主控实测纠正初判)**:pandas `groupby.sum` 按值降型且**溢出自动升 Int64**(T=18 求和不会静默溢);风险仅在**下游算术** —— pandas Int8 `**2`/乘积静默回绕(实测 `14²→-60`,即历史 jf=2.387 根因)。当前 runner.py 三个危险消费者(jf/disag/concern)**均已 float 转换修复**,`log_sent` 经 `np.log1p` 安全,全仓**无其他模块**对这些面板列做裸算术 → **当前无活跃溢出**。修(稳健):面板构建处把这 12 列升 Int32,根除整类隐患,替代逐消费者打补丁。

---

## 7. 清白背书(经独立复现 / 对抗 verify,予以背书)
- **零 material 发现单元**: `encode_collab`、`geography`(聚合/距离/z-score/LOO 算法逐条核验通过)。
- **核心算法逐位/机制清白**: LLM 投票聚合 + prob_score 3类/2类公式(主控复算)、majority_vote tie 确定性、词典状态机、**herd_decay O(N·window) 双指针重写逐位等价于稠密参照**(主控独立推导:NaT 末位排序保证窗口边界一致)、policy cosine(冻结外部锚无泄漏)、benefit_mean、Bartik 代数、geography haversine/prox、Burt constraint、HTMT/κ/Cronbach。
- **历史修复守住(回归核验)**: JF 边界 `[-1,1]`、比率列零越界、W² fill_diagonal、peer_cov 掩码、tone_gap min-n、jieba 词典注入、F1 LLM 禁用 verified=False、F11 fintech 降级 ERROR、num_intensity 默认 content_full、article_sbert 标题×1、`_cn2arab` 全部冻结样例正确。

---

## 8. 分级修复路线图

### 阶段 0 — 纯文档 / 标签($0,golden 不变,可立即做)
误引/误标修正:JF 引文、Berger→LeSage-Pace、auth_sim Hassan→Hoberg-Phillips、z_score CAR variant 标签、llm_peer difflib-cutoff 如实标注、attention_index extensive 标注、network-04 docstring、BW2012 列标签(配合 P1-4)、strategic_diff JSD docstring(若选改 docstring 而非改 base)。+ codebook 引用批量回填。

### 阶段 1 — $0 本地重算 + 定向重生 golden(无付费 API)
P1-1 fintech_share 同基重算 · P1-2 VW/MW/HW valid 分母 · P1-3 peer_tone 重归一(+W²)· R-B fintech verified 门控 mask · numerical_intensity 分母 mask · iv_did bartik 'other' 排除 · staleness 两轨严格排除同日 + 稳定次键 · herd_decay stable sort + 次键 · sbert encode_local L2 归一 · benefit `_center` 冻结 sidecar · 39d 双轨 · lexical function_word `eng` 守卫 · LM 分母过滤标点数字 · strategic_diff JSD base=2 + centroid clip[0,2] · tone_berts 空文章 NaN · radius_sensitivity 零方差守卫 · threshold path-B body-only · news_salience page_rank 多字母 · Int8→Int32 升型 · codebook nullable 强转。

### 阶段 2 — 需付费缓存命中重跑(变值,$0-if-cached + golden)
tone_llms `avg_prob_score` verified 门控(用缓存逐模型标签,$0,但变 panel 值)。

### 阶段 3 — T=2 数据先决 / 披露
ivdid-01 恒零列 ERROR+drop(全量 T=18 自愈);所有 IV/DiD/event-study 因果声称加 T<3 守卫 + 披露。

---

## 9. 诚实边界
1. 主控亲验范围 = 7 个最高价值发现 + 回归核验;其余 ~31 条 P2/P3 依赖工作流 (review→对抗 verify→公式溯源 verify) 三方投票,可信但未逐条亲跑。
2. 未直接跑 Stata;Stata 侧结论基于模板逐行读 + 列名/spec 核对。
3. Int8 "无活跃溢出"结论基于当前盘上 T=2 + 全仓 grep;生产 T=18 首跑后宜加 assert 复核。
4. 计数为区间;latent vs active 边界依赖生产数据时序假设。

**终审意见**: pipeline **单指标算法层仍达顶刊水准,历史核心修复守住**;但 (a) 聚合域不匹配 5 处(含 2 个 P1 进赛马/头条回归)、(b) 公式/引文保真 ~10 处误引或偏离 canonical、(c) `METRIC_AUDIT_V3 §7 阶段1` 横切路线图大面积未执行、(d) 复现包工程质量(codebook 94% 空引用)四维存在系统性缺陷。**阶段 0+1(几乎全 $0 本地)可消除绝大多数缺陷;当前状态在修复这些前不宜投稿。**

---

## 附:审查产物(`scripts/audit/`)
- `METRIC_AUDIT_TOPTIER_2026-06-09.md`(本报告,最新权威)
- `_wf_findings_parsed.md`(工作流 44 findings 全文 + 双 verifier verdict)· `_wf_cleanbills.md`(31 单元 clean_bill + coverage)
- 工作流脚本: `workflows/scripts/metric-audit-toptier-2026-06-09-wf_06f4043b-8b6.js`(可复跑)
- 前序: `METRIC_AUDIT_V3_2026-06-02.md`(上一轮全面审计)· `METRIC_AUDIT_V3_REVIEW_CLOSURE_2026-06-03.md`
