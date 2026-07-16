# 指标计算缺陷真实性 — 终极元验证裁决(V3 收官)

> 回答用户诉求"最后一次系统全面的审核, 确保所有缺陷真实存在"。本文是 V3 三轮(初审→元验证→主控亲验)的收官裁决, 与 `METRIC_AUDIT_V3_2026-06-02.md`(初审)、`_mv_report.md`(元验证终审编辑全文)配套。

**裁决日期**: 2026-06-02(收官 06-03)
**当前 HEAD**: `6d56cb9c`(fintech avg_ft_intensity_full→content_full 全链重跑 + golden 重生; 只改 golden_panel_v0.json 一个 tracked 文件)
**元验证规模**: 135 条主张 × 默认证伪复现(P0 双复现)+ 假阳性总审计 = **107 agents / 7.8M tok / 131-of-135 在真实数据上实测复现**

---

## 0. 一句话结论

**所有被主张的缺陷"机制本体"几乎全部真实存在(135 条中 0 条被证伪为造假, 仅 2 条因后果不成立/不可达被整体推翻), 但约 1/3 的"严重度"被系统性高估。** 经三层校准, 真正"当前可复现 + 承重 + 可修的代码缺陷"约 **20 个**(其中 2–4 个 active-crash/结构性 IV bug 是 P0); 另有 ~14 个是"真实但属 T=2 数据天花板的已披露限制(非可修 bug)"; ~45+ 条经假阳性审计降级(非承重/不可达/标准实践/量级夸大)。

---

## 1. 复现统计(结构化口径)

| 类别 | 计数 | 含义 |
|---|---:|---|
| **real**(机制经真实数据复现, 确认存在) | **93** | 0 条机制造假 |
| **contested_or_partial**(机制真但定级/量级须改, 或已被 HEAD 闭合) | **40** | 多为 magnitude_wrong / disclosed_limitation / non_load_bearing |
| **refuted**(整体推翻) | **2** | st-did-06(机制假)、st-data-prep-04(后果不可达) |
| 在真实数据上实测复现 | **131 / 135** | 仅 4–5 条以读码/git 取证 |

> 终审编辑手工再核后建议把另 ~5 条 real 按假阳性审计降级(→ 实质 real ≈ 88)。无论 88 还是 93, 实质结论一致。

---

## 2. 主控亲验的 5 个锚点 — 在当前 HEAD `6d56cb9c` 上逐一复证仍成立

> 这 5 条是我(主控)亲自跑代码+数据坐实的, 且 `6d56cb9c` 未触及其代码站点。是本次审查可信度的硬锚。

| 锚点 | 当前盘上复证(06-02 20:21 面板 / HEAD 6d56cb9c) | 状态 |
|---|---|---|
| **V1 JF Int8 溢出** | `jf_coefficient_full` max=**2.3870967**(>1 不可能); 平安银行2017 正确值 0.809 | ✅ 仍成立(真缺陷) |
| **V2 network W² 未去对角** | `network_spillover.py:269` 代码未改, `peer_tone_2nd_lag1_*` 作 brokerage IV; 元验证"审计未质疑"维持 P0 | ✅ 仍成立 |
| **V3 39f 陈旧 tone 污染** | `39f_*.parquet` 仍 **05-31**(6d56cb9c 只重跑 21→24 未跑 39f); `cross_media_alpha_full`=**0/176 空壳**, `cross_outlet_tone_variance_full`=36(旧 tone) | ✅ 仍成立 |
| **V4 num_intensity 漏标题** | `tone_words.py:1357` 未改, 默认 `full_col='内容'`; num_intensity_full=裸正文 | ✅ 仍成立 |
| **V5 Stata 幻影列** | 面板**无 `tech_frac_lf`**(只有 `tech_frac`/`tech_frac_lc`); 选 full 轨(lf/sf)→ Table2 M4/M6 r(111) | ✅ 仍成立 |

> **重要区分**: `6d56cb9c` 闭合的是 *fintech 链* 的 stale(genA-03: stage23→24→panel 现 mtime 单调、max_abs_diff=0)。我的 **V3/39f 是另一条独立 validation 阶段**, 未被 6d56cb9c 触及, 仍 stale。

---

## 3. 最终四层净清单(用户"确保真实存在"的回答)

### 第①层 — 确认真实 + 当前可复现 + 承重 + 可修代码缺陷(~20, 应修)

**P0(active crash / 结构性 IV bug, 代码层可修)**
- `attention_media-01` — `bank_fintech_attention/figures.py` 消费 6 个从未物化的 `attention_index_*` 列, 真 CLI 退出码 1 + ArrowInvalid(`analysis.py:62` except 接不住); 是可 build 论文。
- `network-01`(=V2) — `network_spillover.py:269` W² 未 `fill_diagonal(0)`, IV 含 ~24.5% 本行自身 tone, 违 Bramoullé 排他性, 是 brokerage `iv.primary`。
- `jf_coefficient`(=V1, 完备性新逮, 未入 135 但主控亲验) — `runner.py:1413` Int8 `**2` 静默回绕, 盘上越界 2.387; **1 行真错 / 21 行潜伏 / production 负面覆盖升后扩散**。修=`astype('float64')`+越界断言。

**P1(承重逻辑/口径不对称, 进主回归或核心机制表)**
- `network-02` 邻接矩阵单篇双端各计(30.1% 行权重改变); `network-03` 孤立银行 peer_tone `fillna(0)` 混淆中性(56% 结构性零, 是 brokerage treatment.primary)。
- `herd-ghost-01`(`encode_collab.py:508/588`) _ctx 派生轨硬读 `herd_weight_full`, 违 Edwards 轨匹配。
- `genA-01`/`numintensity-01`(=V4) num_intensity_full 读裸正文, 唯一不含标题的 *_full 情感族。
- `tonellms-01` LLM full/ctx 两轨都把标题作独立字段注入 prompt(与 `entity_context.py` 三处明文矛盾), ctx 是 G3 主处理。
- `benefitfrac-01` commit 把 median-split 误标 mean-center, P(>mean)=0.5634≠声称 0.497。
- `clarity_cn-01` clarity 词典从不 `add_word` → 67/541 多字词被 jieba 切碎(12.4% 永久漏匹配)。
- `encode-02` tone_gap_sub_symb/indep_collab 四处裸相减无 `≥5` 守门, 进 `12_table3_mechanism.do` 机制回归。
- `geography-01` LOO IV 一阶段 F=0.25/0.037(docstring 方向写反), 进 falsification 2SLS。
- `llmpeeriv-02`/`st-robust-boot-01` 5 个 cutoff IV 列字节相同(no-op), Table3 退化为 5 列重复回归制造伪稳健。
- `st-did-05` `bank_type`(str7) 数值比较 r(109) + `levelsof` 未引号 r(198), StataNow 实跑双崩。
- `st-did-01` 模板头注/addnote 印 "Callaway-Sant'Anna staggered DiD" 但 M1-M6 全是 reghdfe TWFE(7 模板 0 个 csdid), addnote 逐字落入 .tex。
- `st-descriptives-01` 5 模板描述统计用全面板(非 `if e(sample)`), 57 个零报道 bank-year 进描述, 与回归 N 口径不一。
- `V5`(`st-table2-main-04`/`st-bartik-iv-08`/`st-descriptives-04`) full 轨(lf/sf)幻影列 → 主表/A3 r(111) 或静默跳过。

### 第②层 — 真实但属 T=2 数据天花板的已披露限制(~14, 非可修 bug → 转披露完整性)
`llmpeeriv-01`(IV 仅 2018 单截面 18 值, 一阶段 F=0.0006)、`ivdid-01`(dcep/sandbox treat_year≥2019>2018, post 恒0 不可识别, docstring L29-33 已披露)、`ivdid-02/03/04`(Bartik 共线/反射/one-hot, docstring L17-34 已披露)、`st-iv-2sls-01/02/03/05/06/07`(ROA 缺 exit198 / 单截面 73-for-73 或 14-for-14 FE 饱和 / 少聚类无 wild bootstrap)、`st-table2-main-02`(median-split 子期空)、`st-did-02/03/04`。**根因 = T=2 面板 + 全部处理年≥2019; production run(spec 声明 T=19)下自然消失。代码逻辑本身正确。**

### 第③层 — 真实但非承重 / 不可达 / 标准实践(~45 经降级, 当前无计量后果)
- **非承重(导出 .dta 但零回归消费)**: staleness 全族(`grep -rln staleness` 全 papers 树**零命中**, 11% 漂移无后果)→ stale-tie-01/03/staleyear-01 降 P3; `toneberts-01`(bert_avg_pos 9.56% 虚增, 但 LOO-IV/disag 在 95 个 Stata 模板**命中 0 次**)。
- **不可达(provisional 论文 / 缺 DV / 未产出 stage)**: `discriminant-01/02`(validation-only + krippendorff 未装 + 唯一消费方 bank_media_disagreement 是不可 build 的 provisional)、`risk_outcomes-02/exec_ner-04`(stage19/49 无产出 + provisional)、`ivdid-stata-02`(根 11_table2 静默回退路径生产不可达)。
- **标准实践(文献可辩护, 须披露非硬错)**: 加权 valence 均分 / logit 域聚合 / mean-of-fractions / tier 权重 / 88 簇渐近 CRVE。
- **已被 HEAD 闭合(当前不复现, severity→none)**: `genA-03`/`nart-03`(fintech 链 stale + repro 红 → 6d56cb9c 后 mtime 单调、19/19 绿)。
- **量级夸大(机制真数字错)**: ~22 条, 如 `encode-01`(VW/MW/HW 失配真但 0 个 Stata 模板把这些列作处理变量)、`falsification-01`(仅交互列非主回归)、`st-bartik-iv` 系列(0.70 是 Cragg-Donald 非模板展示的 KP F=5.18)。

### 第④层 — 整体推翻(2)
- `st-did-06`(机制假): root 链不存在"Table1 原始 vs Table2 缩尾互反"——root 10_table1 零 use, 经 master 继承 01_data_prep 就地 winsor 后内存, 与 Table2 同口径; 误把陈旧注释当真实 use。
- `st-data-prep-04`(不可达): "$controls r(111) 硬崩"被 DV/treat 的 exit198 fail-fast 先发, StataMP 实跑 LOG 停在 r(198), 8 篇均不可达。

---

## 4. 假阳性审计揭示的两条系统性高估根因
1. **"导出到 .dta = 承重"被滥用**: 多个指标进 `stata_export` core_patterns 却全树 grep 零回归消费(staleness/部分 BERT 衍生), 其"缺陷"无计量后果。
2. **"provisional 论文 + 未产出 stage + 缺 DV"三重不可达被低估**: `bank_media_disagreement`/`bank_news_clarity`/`bank_fintech_collab` 刻意不入 `_DERIVATIVE_PAPER_IDS` 不可 build; ROA/CAR/NPL/z_score 全缺(M0 Wind merge 待办, 已披露); stage 17/19/49 输出盘上不存在。

---

## 5. 对用户问题的最终诚实回答

**"确保所有缺陷真实存在"** —
- **机制真实性**: 通过。135 条主张 0 条造假, 131 条在真实数据上实测复现, 只有 2 条因"后果不成立/不可达"被整体推翻。前两轮审计的发现**不是无中生有**。
- **严重度可信性**: 须打折。约 1/3 主张被系统性高估(非承重/不可达/T=2 已披露/量级夸大)。
- **真正该修的**: 第①层 ~20 个可修代码缺陷(含 2–4 个 P0); 第②层 ~14 个 T=2 已披露限制应转"披露完整性"处理(待 M0 扩 T≥3 自然消失); 其余降级。
- **最高优先级 5 个 surgical 修复**: `network_spillover.py:269`(W² 去对角) · `runner.py:1413`(JF float64) · `figures.py`(缺列防护 ArrowInvalid) · `encode_collab.py:508/588`(_ctx 误用 _full 权重) · `tone_words.py:1357`+`clarity` jieba 注入(标题不对称 + 词典漏匹配)。这 5 个不依赖 T≥3, 当前数据可修, 改值后需定向重生 golden。

---

## 附: 产物(全在 `scripts/audit/`)
- **本文**(收官裁决) · `_mv_report.md`(元验证终审编辑全文) · `_mv_result.json`(93 real/40 contested/2 refuted 结构化)
- `METRIC_AUDIT_V3_2026-06-02.md`(初审 + 主控亲验 V1-V5) · `_v3_result.json` · `_v3_P0/P1/P2.md` · `_v3_completeness.md`
- `_verify_jf.txt`/`_verify_jf2.txt`/`_verify_misc.txt`(主控亲验脚本输出) · `_mv/finding_*.json`(135 条逐条复现输入)
- 工作流脚本: `workflows/scripts/metric-audit-v3-toptier-*.js`(初审) + `metric-audit-v3-metaverify-*.js`(元验证), 均可复跑
