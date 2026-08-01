# news_process 指标计算体系 — 顶刊标准终极验证 V3（独立复核 + 亲验收敛版）

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


> 本报告**补充并部分取代** `METRIC_AUDIT_FINAL_2026-06-02.md`。该 FINAL 报告针对的是修复**前**的代码;本报告针对 **18-commit 修复后**(PR#5, HEAD `f2f67570`)的当前代码 + 当前盘上数据(`40_panel_yearly.parquet` 176×1552, Jun-2 20:21),并由我(主控)对最高价值的新发现**逐条亲自经验复现**。

**复核日期**: 2026-06-02
**复核对象**: news_process v3.8.0, 经 18-commit metric-audit 修复批次后
**方法**: 46 单元 × (review→三棱镜对抗 verify) 工作流(377 agents / 24.6M tokens) → 终审编辑合成 → **主控亲自复核 5 个最高价值新发现(5/5 全部坐实)** + 严重度重校准
**环境**: Python 3.14.3 / pandas 3.0.3 / numpy 2.4.6 / jieba 0.42.1; 面板 88 banks × {2017,2018} = **T=2**

---

## 0. 主控亲验结论(本报告可信度锚点)

我没有照单全收 workflow 的 129 条"confirmed"(历史证明对抗确认仍有 ~15-20% 在元层被推翻)。我对**最高价值、最可操作的 5 个新发现亲自跑代码+数据复现,5/5 全部坐实**:

| # | 发现 | 我的复现证据 | 裁决 |
|---|---|---|---|
| V1 | **JF 系数 Int8 整数溢出** | `pos_count_full` dtype=**Int8**(max 98); 盘上 `jf_coefficient_full` max=**2.387**(数学不可能>1); 平安银行2017 P=14/N=1 盘值2.387 vs 我 float64 重算**0.809** | ✅ 真缺陷 |
| V2 | **network W² 未去对角** | `network_spillover.py:269` `peer_tone_2nd = W@(W@tone)` 无 `fill_diagonal`; `peer_tone_2nd_lag1_{full,ctx}` 已落盘且被 brokerage spec 用作 IV | ✅ 真缺陷(代码确证) |
| V3 | **39f 跨媒体方差用陈旧 tone** | `39f_cross_media_alpha.parquet` mtime=**05-31**(面板=Jun-2); 面板 `cross_outlet_tone_variance_full`=36非空(旧tone), `cross_media_alpha_full`=**0非空(空壳)** | ✅ 真缺陷 |
| V4 | **numerical_intensity full 轨漏标题** | `tone_words.py:1357` 调 `enrich_with_num_intensity_dual_track(processed_df)` 用默认 `full_col='内容'`(裸正文无标题) | ✅ 真缺陷(病根A漏网) |
| V5 | **Stata 主回归引用幻影列** | 面板有 `tech_frac`/`tech_frac_lc` 但**无 `tech_frac_lf`**; `11_table2:43-44` 生成 `tech_frac_{lf,lc}`/`symb_frac_{sf,sc}`(`stata_runner.py:206`); full轨(lf/sf, 含文档示例 `lc_sf_ctx`)→ M4/M6 无 `capture confirm` → **r(111) 崩** | ✅ 真缺陷 |

**关键校准——JF 溢出的精确影响(我亲测)**: 21 行有溢出风险(P+N≥12), 但当 N=0 时比值 P²/P² 对溢出**免疫**(分子分母同步回绕→恒=1.0)。因 `neg_count` max 仅 1-2, **当前仅 1 行真错**(平安银行2017→2.387)。**当前影响=1 个 cell(一个稳健性替代指标), 潜伏风险=production 负面覆盖上升后无界扩散。** 既不夸大也不淡化。

**对 workflow 可信度的判断**: 5/5 亲验命中 + 终审编辑自己把 17 个原始 P0 收敛到 8 个并主动标注 6 处过度声称 → 本批工作流的**机制识别可靠、定级仍偏高但已自校准**。下文按我的重校准给级。

---

## 1. 执行摘要

**整体结论: 单指标算法实现层达到顶刊水准, 但体系尚未达"零错漏"投稿标准。**

绝大多数核心指标(LLM语调/词典法/herd decay/geography/benefit_mean/EPU/Burt代数/判别效度HTMT/Bartik机制)经**独立重实现逐位复现**(max_abs_diff≈0), 工程忠实度很高。缺陷集中在四个**非算法**层面:

1. **派生指标层(runner.py)的未审盲区** — JF Int8 溢出(V1)是典型, 这层从未被系统审过(40+18 个无锚点 washing/quadrant 变体同源风险)。
2. **识别有效性(T=2 元缺陷)** — 所有 IV/DiD/event-study/滞后在 T=2 下结构性退化或不可识别。**这不是代码 bug, 是数据维度天花板**, 多已在 Python docstring 诚实披露, 但 Stata 模板/README 未承接披露。
3. **双轨 full/ctx 不对称未完全闭合** — 病根A漏 numerical_intensity(V4) + LLM ctx 双注入 + herd/clarity/frac_amb ctx 轨用 full 口径。
4. **修复批次自身的诚实度 + 时序血缘** — 6 处过度声称 + 39f 陈旧 tone 污染(V3) + Stata 幻影列(V5)。

### 确认问题计数(我重校准后)

| 级别 | 数量 | 说明 |
|---|---:|---|
| **P0(立即修, 当前数据可修)** | **3** | V1 JF溢出(P0-by-可见性) · V5 Stata幻影列崩 · attention_index幽灵列figures崩 |
| **P1(实质缺陷)** | **~24** | 真缺陷净集(剔除T=2族与重复) |
| **T=2 识别限制(非bug, 须披露/待T≥3)** | **~12** | IV/DiD/滞后退化族, 单列 |
| **P2/P3(边界/潜伏/文档)** | **~40** | latent + Stata表层 + 词表 |
| **过度声称(诚实更正)** | **6** | 见 §4 |

> 注: 我把 workflow 报的 8 个 P0 中 5 个(llmpeeriv/ivdid-DiD/network-W²/st-iv-2sls/st-bartik/st-table2)重归为"T=2识别限制"或 P1 —— 它们是真实的, 但要么是已披露的数据天花板, 要么消费方IV本就T=2退化。**真正"立即修且当前数据能修"的硬缺陷是 3 个。**

---

## 2. 立即修 P0 净清单(3 条, 当前数据可修, 全部我亲验)

### P0-1 · `jf_coefficient_{full,ctx}` Int8 整数溢出 → 越界 2.387
- **file**: `pipeline/panel/runner.py:1413-1434`
- **违反**: Janis-Fadner (1965) / Deephouse (2000 SMJ), 理论域 [-1,+1]
- **实测**: `pos_count_full`=Int8; `P**2`/`(P+N)**2` 在 Int8 静默回绕。平安银行2017盘值 **2.387**(正确0.809)。当前1行真错, 21行潜伏风险, production 必扩散。
- **修复(1行级, 低风险)**: JF 计算前 `P = panel[pos_col].fillna(0).astype('float64')`(N 同); 产出后 `assert jf∈[-1,1]`; 全仓扫 Int8 计数列做 `**2`/乘积的其他派生(washing 族)。
- **代价**: 改值(1 cell) → 需重生 golden(定向)。
- **验证**: confirmed / yes_empirical(主控亲测)

### P0-2 · Stata Table 2 主回归引用幻影列 `tech_frac_lf`/`symb_frac_sf` → r(111) 崩
- **file**: `11_table2_main_m1m6.do.tmpl:43-44,56,72` + `01_data_prep.do.tmpl:41` + 同类 `13/14/22/24` 模板; 替换器 `stata_runner.py:300`(无 lf→裸名 重映射)
- **违反**: 可复现性(Nosek 2018 PNAS) — replication 主表须可运行
- **实测**: 面板只有裸名 `tech_frac`/`symb_frac`(full)与 `_lc`/`_sc`(ctx), **无 `_lf`/`_sf`**。选 full 轨(lf/sf, 含文档示例 `replication_..._lc_sf_ctx` 的 sf)时模板生成不存在列; M4/M6 无 `capture confirm` → Table2 在 M4 处 r(111) 中止; `01_data_prep` winsor 有守卫故 full 轨**静默跳过缩尾**(缩尾口径随 track 不对称)。
- **修复**: `stata_runner.py` 替换层加 `lf→''`/`sf→''` 重映射(full 轨→裸名), 或统一 Python 也产 `_lf`/`_sf` 别名; M4/M6 加 `capture confirm variable`。
- **验证**: confirmed / yes_empirical(主控亲验列名 + 模板 + track 取值)

### P0-3 · attention_index 幽灵列 + `figures.py` ArrowInvalid 硬崩
- **file**: `papers/bank_fintech_attention/figures.py:32-35` + `paper_spec.yaml`
- **违反**: 可复现性; 代码实现 ≠ 论文声称的 Hassan 2019 treatment
- **实测(workflow, 与先前FINAL P0-②一致)**: `attention_index_{full,ctx,disp,pct}` 6 列全仓零命中, 从未物化; `figures.py --stage figures` 真跑抛 ArrowInvalid, `analysis.py:62` except 接不住 → traceback。
- **修复**: P2 treatment 重定向到真实列 `avg_ft_intensity_{full,ctx}`(最接近 Hassan attention intensity)并同步 figures/tables/spec; 放宽 except + 列存在性守卫。
- **验证**: confirmed / yes_empirical(workflow; 属已知项延续, 未本人重跑 figures)

---

## 3. P1 真缺陷净清单(~24, 按横切根因分组; 已剔除 T=2 退化族)

### R1 — 双轨 full/ctx 标题不对称(病根A未完全闭合)
- **V4 `numintensity-01`** `numerical_intensity.py:256` + `tone_words.py:1357`: full 轨默认 `full_col='内容'`(裸正文), 唯一不含标题的 *_full 情感族指标。(主控亲验)
- `tonellms-01` `tone_llms.py:562,565`: LLM ctx 轨标题双重注入(content_ctx 已含标题 + {title} 再喂 prompt 一次), full 轨干净 → 破坏 full/ctx 对照。ctx 是 P1 主处理 `llm_vote_tone_ctx`。
- `herd-ghost-01` `encode_collab.py:508,588`: _ctx 派生轨用 full herd 权重(偏差 mean 2.0%/max 91.8%, 16.8% cell)。
- `encode_collab-01` `encode_collab.py:534`: `frac_amb_articles_ctx` 用 full 轨 median 阈值, ctx 仅 42.6% flagged, 翻转 ~7.5% 文章。

### R2 — 派生指标层 + 加权/聚合口径
- **V1 JF 溢出**(见 P0-1)。
- **A2 `encode_collab.py:389`**: D4 残差 small_mask 用 `n_articles<5`(物理 size), 但 frac 本身在 LLM-valid count 域 → metric-audit P1 重定义 n_articles 后口径漂移未传播到 encode_collab(边界: 物理≥5 但有效<5 不被剔)。(主控读码确认)
- `encode-01` `encode.py:1380-1492`: VW/MW/HW 加权 tone 分子仅 valid、分母全物理 → 系统性向零衰减(full 18行 max 0.5 / ctx 32行 max 0.73)。
- `encode-02` `encode.py:1135-1252`: `tone_gap_sub_symb`/`indep_collab` 缺 min-n≥5 守门(对照 tech_app 有), 18/48 单篇 cell 被 Table3 机制回归消费。
- `fintech_intensity-01` `encode.py:771`: verified 门控未消费, 178 篇打 0 进 mean(应 mask NaN), ctx 轨稀释 15.2%。

### R3 — 词典/分词覆盖(系统性下偏)
- `lmfls-01` `lm_non_sentiment.py:118`: LM 分母含 ~19% 标点+纯数字 token, frac 全体下偏。
- `lmfls-02` `lm_non_sentiment.py:124`: 18.5% 多字词典短语被 jieba 切碎永不命中(应 add_word/AC)。
- `clarity_cn-01` `tone_words.py:724`: You 2018 清晰度词典未注入 jieba, 12.4% 多字词不可匹配。
- `numintensity-02` `numerical_intensity.py:138`: 序数"第N"误转数字 token(44.7% 文章, +3.33%)。

### R4 — 跨模型/跨标度可比性
- `toneberts-01`: `bert_avg_pos` 混 2 类与 3 类 P(pos) 行均值, 尺度不可比(虚增 ~9.6%), 经 LOO-IV/disag 传播。
- `toneberts-02` `tone_berts.py:311`: label_map 只校验标签数不校验 id2label 顺序(checkpoint 重排→潜伏极性对调, latent)。
- `embedding-01/02` `embedding_engine.py:125`: `encode_local`(text2vec) 未 L2 归一化, ~32% 文档混入质心(centroid_diff_emb_t2v 是 export 硬列)。
- `tone_words-01` `tone_words.py:877`: best-dict 动态漂移(主词典仅赢 6%)。

### R5 — 网络/IV 排他性(机制层, 非纯 T=2)
- **V2 `network-01`** `network_spillover.py:269`: W² 未去对角, `peer_tone_2nd_lag1` 作 IV 含 ~24.5% 本行自身 tone, 违反 Bramoullé(2009)排他性 —— 而 brokerage spec 显式援引该约束。修复: 计算前 `np.fill_diagonal(W2,0)`。(主控代码确证)
- `network-03` `network_spillover.py:180,265`: 孤立银行 peer_tone 填结构性 0.0(应 NaN), 41/73 伪零, attenuation。

### R6 — 时序血缘污染
- **V3 `genA-03`/B1** `runner.py:1606`: 面板 merge 了 05-31 的 39f → `cross_outlet_tone_variance_*`(paper-10 主处理, 36非空)用旧 tone, 面板其余 tone 用 Jun-2 新 tone; 且 `cross_media_alpha_*`=0非空空壳。(主控亲验 mtime+列)
- B3: `content_ctx` 在 stage15(Jun-2 16:59)与 stage21(18:28)间 10/789 篇不一致 → 1.3% ctx 轨聚合建立在与盘面不符的窗口文本上。

### R7 — 单指标其他
- `falsification-01` `controls.py:615`: fintech_share 分子(物理859)/分母(去重851)计数基不一致, 最坏 7.05pp, 进 Stata 交互。
- `exec_ner-01` `executive_ner.py`: NER 不去歧义, 多银行同文归因全部共提行(7.78% docid, 最坏 15 家)。
- `policy_align-01` `policy_alignment.py:559`: MAIN↔_t2v 收敛效度仅 r≈0.36-0.39(弱)。
- `discriminant-01` `cross_media_alpha.py`: 39f Krippendorff α 列 100% NaN(krippendorff 包未装), 学术锚点从未产出。

---

## 4. T=2 识别限制(真实但非代码 bug — 须披露, 待 M0 扩 T≥3)

**元主题**: 面板 T=2(2017-2018)使所有依赖时序变异的设定退化。这是**上游数据维度天花板**(受 stage 41 限制, 非 Stata 容量), 多数已在 Python docstring 诚实披露(commit 76c1301a)。**当前所有"因果识别"声称在 T=2 下不成立。** 单列如下, 不计入"待修 bug":

- `llmpeeriv-01`: LLM peer IV 一阶段 corr(treat,IV)=**0.007**, 有效N=14/全2018单截面(弱工具)。
- `ivdid-01`: DiD `dcep_post`/`sandbox_post` **恒0**(处理年≥2019>面板2018), 26 列恒0仍产出 → 不可识别。**修复(可现在做)**: `merge_policy_shocks` 末尾 `assert (post==1).any()` 否则 drop 派生列 + log。
- `ivdid-04`: Bartik 基期 share 63.6% one-hot + fintech 96.6% app → 近共线 type FE, 一阶段去均值后 corr=0.049。
- `geography-01`: geo LOO IV 一阶段 F≈0.04-0.25。
- `herd_decay-01`: 同日并列 + 非稳定 quicksort → hw 加权语调非决定性(459/859 同日; 正/反序 0.273↔-0.091)。**修复(可现在做)**: tie 加确定性二级键(article_id)。
- `stale-tie-01`(V13修复半成品): semantic staleness `kind=stable` 未消除同日 tie 对输入序的依赖(~11% 行漂移)。**修复**: 排序加确定性二级键。

> **Stata 侧承接缺口**: `st-did-01` 宣称 Callaway-Sant'Anna 实为裸 TWFE(csdid 全模板零调用); `st-iv-2sls`/`st-table2`/`st-bartik` 主表无 wild cluster bootstrap、无弱工具守卫、Table A3 恰好识别仍报 Hansen J + lf/lc 工具相关 0.9999。这些是**Stata 模板未承接 Python 诚实披露**的表层问题, 须在 replication 包统一披露 T=2 限制 + 加 `boottest`/`weakivtest` 守卫。

---

## 5. 过度声称(诚实更正, 6 处)

修复批次方向整体正确、多数真实落盘, 但以下声明与代码/数据实况不符, 须更正记录:

1. `genA-02`: "test_panel_reproducibility 19 绿"实测 **3 红**(21/22 mtime 晚于 golden 快照 43 分钟)。
2. `riskpath-01`: "短面板 T 守卫"在 `risk_taking_outcomes.py` **从不存在**(git diff 仅含路径替换; min_periods=4 是 pre-existing)。
3. `stale-tie-01`: semantic "kind=stable 使其确定"**未消除** tie 漂移(只固定了同输入排序内部)。
4. `ivdid-stata-01`: DiD 披露"处理年份≤2018"实为 **≥2019**(归因方向倒置)。
5. `herd-ghost-02`: "与 llm_vote_tone 同口径"**无乘积加权兄弟列**。
6. (memory 自承)"重跑 $0/0 API"实为前批 **856 次付费 embedding** —— 本报告未独立核实, 但与 memory 记载矛盾, 列入待澄清。

---

## 6. 各单元清白认定(明确背书)

经独立重实现逐位复现(max_abs_diff≈0), **以下指标计算符合学术标准, 予以背书**:

- ✅ **修复 clean(5)**: 39e fill_diagonal CoW + 39d Cohen κ 守卫 · strategic_diff/policy ctx 去重 · ctx 对角 frac 切 ctx 分母 · EPU 月度等权聚合(BBD 2016 逐位) · n_articles 物理重构(三分类 frac 和恒=1, 恒等式 0 fail)。
- ✅ **核心算法 yes(逐位)**: LLM 语调编码/聚合/prob_score · 词典法状态机(IDF 公式正确) · herd decay(859/859 maxdiff=0, 无前视) · 政策对齐 cosine(maxdiff=1.79e-7, 锚点外生无泄漏) · benefit_mean(maxdiff=4.3e-8) · 战略差异化 NN/centroid · 面板等权聚合(llm_vote_tone/n_articles/std/frac maxdiff=0) · LLM peer IV LOO 算法(self-exclusion 0 泄漏) · Bartik 机制代数 · geography haversine/prox/z-score · 网络 Burt constraint/eigen/gini · EPU 聚合 · 判别效度 HTMT/NMI/κ/Cronbach(seed 锁定) · 陈旧度 surface/semantic 核心。
- ✅ **样本内泄漏整体清白**: policy 锚点为冻结外部语料; fintech IDF 在全参考语料; benefit _center 经 FE 吸收(唯一隐患 median_amb_d0 声称 frozen 实 in-sample, latent)。

**结论**: pipeline 的**单指标计算引擎质量很高**, 确定性/可复现性/公式忠实度在已审范围内基本达标。

---

## 7. 优先级修复路线图

### 阶段 0 — 立即修(当前数据可修, 低风险, 需定向重生 golden)
1. **JF Int8 溢出**(P0-1): `runner.py:1413` 前 `astype('float64')` + 越界断言 + 扫 washing 族。
2. **Stata 幻影列**(P0-2): `stata_runner.py` 替换层 `lf/sf→''` 重映射 + M4/M6 `capture confirm`。
3. **attention_index 幽灵列**(P0-3): figures/spec 重定向 `avg_ft_intensity_*` + 放宽 except。
4. **W² 去对角**(V2): `network_spillover.py:269` `np.fill_diagonal(W2,0)`。
5. **DiD post 全0 守卫**(ivdid-01): drop 恒0派生列 + log。
6. **39f 用 Jun-2 tone 重跑**(V3): 修 cross_outlet_tone_variance stale + cross_media_alpha 空壳(装 krippendorff)。

### 阶段 1 — 横切根因(需重跑 stage 21/22/encode + golden)
- **R1 标题不对称一次性闭合**: num_intensity `full_col=content_full` · LLM ctx 去标题 body · herd/clarity ctx 配 ctx 权重 · frac_amb ctx 用自身 median · staleness 确定性二级键。
- **R3 加权/守门**: VW/MW/HW 分母改 valid-sample · tone_gap_sub_symb/indep_collab 加 min-n≥5 · fintech verified 门控 mask NaN · A2 encode_collab small_mask 切 llm_valid。
- **R4 可比性**: bert_avg_pos 分组平均 · encode_local 加 L2 归一化 · best-dict 固定主词典。
- **R3 词表**: LM 分母过滤标点数字 + 短语 add_word; clarity 词典注入 jieba。

### 阶段 2 — T=2(数据先决)
- **M0 production run 扩 T≥3** 为达"因果识别"门槛的**先决条件**。在此之前: 所有 IV/DiD/event-study 加 T<3 守卫 + 诚实披露, 不呈现因果估计; Stata 模板承接 Python caveat + 加 boottest/weakivtest。

### 阶段 3 — 文档/Stata 表层 + 6 处过度声称更正 + codebook 补列 + 缩尾口径统一(Table1/Table2 同源)。

### 阶段 4 — 完备性新单元
- 新增 `[metric] runner 派生指标层`审查单元(washing 40 + quadrant 18 + concern + JF + cater); 全扫 Int8 `**2`/乘积。

---

## 8. 本次审查的诚实边界

1. **未直接跑 Stata**: 所有 Stata 结论基于模板逐行读 + pandas 模拟回归样本/共线性 + 主控亲验列名/track, **未在本机 StataNow 19.5 实跑 .do**。reghdfe singleton/absorb 饱和为逻辑+样本推断, 建议人工 Stata 实跑确认 r(111)/r(301)。
2. **主控亲验范围**: V1-V5(5个最高价值新发现) + JF 溢出机制。其余 ~100 条 P1/P2 依赖 workflow 三棱镜对抗(可信但定级偏高已校准), **未逐条亲跑**。
3. **P1 计数为区间(~24)**: 据三层 verifier 投票重归级, latent vs active 边界依赖 production 数据时序假设。
4. **outcome 数据未审**: stage 49 outcome 是 2024 季度采集数据(非 2017-2018 新闻面板), risk_taking 经合成数据实证, production 行为待验。
5. **未覆盖**: validation pipeline 完整链、Stata 下游 csdid/sdid/synth 具体行为、LLM cache provenance、production 成本($0 vs 856 次付费 embedding 矛盾未独立核实)。

**终审意见**: pipeline 在**单指标算法实现层达顶刊水准**, 但在**派生指标层(Int8)、识别有效性(T=2)、双轨可比性、Stata 表层诚实度**四维存在系统性缺陷。**阶段0(3 P0 + 3 surgical)后消除 active-crash/越界; 阶段1(R1/R3/R4)是消除横切口径污染的实质门槛; T≥3 是任何因果声称的先决。当前状态不可用于投稿。**

---

## 附: 审查产物(全在 `scripts/audit/`)
- **`METRIC_AUDIT_V3_2026-06-02.md`**(本报告, 最新权威)
- `_v3_result.json`(workflow 结构化全量: 135 kept findings + formula_audit + completeness + consistency)
- `_v3_report.md`(终审编辑合成全文) · `_v3_P0.md`/`_v3_P1.md`/`_v3_P2.md`(分级明细) · `_v3_completeness.md`(派生层盲区 + 时序血缘)
- `_verify_jf.txt`/`_verify_jf2.txt`/`_verify_misc.txt`(主控亲验脚本输出)
- 工作流脚本: 会话 `workflows/scripts/metric-audit-v3-toptier-*.js`(可复跑)
- 前序: `METRIC_AUDIT_FINAL_2026-06-02.md`(修复前基线) · `METRIC_AUDIT_REPORT_2026-06-02.md`(初版, 勿采信定级)
