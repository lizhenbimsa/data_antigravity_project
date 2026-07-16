# Stata 变量属性完备化 × 变量代码手册长注释 (≥1000 汉字 / core ≥5000 汉字) — 合并执行计划

**日期**: 2026-07-10 (v2.9 — 八轮多智能体评审收口: 5+2+3+2+3+2+2+2 共 **21 路**, 台账见 §10; 终判 **ok_to_ship (计划层 + 需求符合层 + 汉字口径)**)
**状态**: 已写未实施 (planning-only; 本计划是权威执行口径)
**范围**: Phase 1 = 主线面板 dta 族 (40/46/51 三份) + codebook 四格式产物; **Phase 2 (计划内, 非 DEFER)** = company_listed_bank / company_tax_bank 共现面板族 (§5 WP6)
**字数口径 (用户修订, 2026-07-10 终版)**: 全量变量注释 **≥1000 汉字**; **关键核心指标 ≥5000 汉字** (⚠ 计量单位 = **CJK 汉字数**, 非字符数 — 引文段英文/数字/标点不计入, tier 三态机制见 §1a)
**费用**: 全程 $0 LLM pipeline API (纯文本资产生产, 走会话 agent; 不触 stage 21/嵌入缓存, 不过 M0 审批门)
**Golden 风险**: 零 (不动任何 panel 数值列 / parquet; 只富集文档产物与 dta 元数据层)

---

## §0 两任务合并逻辑 (承重决策, 先读)

用户两项任务表面是两件事, 实为**同一 SSOT 的两个消费端**:

1. **任务 1 (Stata 变量属性)**: 每变量 = 中文标签 + 长注释 (数据来源/计算公式/顶刊文献, APA + doi 全核验)。
2. **任务 2 (代码手册 12 字段)**: 变量名、标签、描述/注释、数据类型、单位、取值范围、计算公式、来源阶段、学术引用、备注、变量类别、文本轨道。

字数要求分两级: **全量 ≥1000 汉字 / 关键核心指标 ≥5000 汉字** (历史口径 ≥2500 单一、≥500 两级、以及"字符"计量单位均已作废 — 现行计量 = 汉字数)。

**合并方案**: 长注释正文只生产一次, 落在 codebook 的 `描述` 字段 (SSOT = `codebook.py::_compose_long_description` 组装器, **唯一挂载点 = `generate_codebook` 逐列发射循环** [codebook.py:2082-2159, `col`/`panel` 全在作用域; ⚠ 宇宙=51 **须 fail-loud 保证**: generate_codebook.py:131-148 在 51 缺失时会回退 40 并告警 — **长文生产/验收模式下 51 缺失 = 拒跑**, 禁在回退 40 宇宙 (3442, 缺 11 个 51-only 列) 下产出四格式成品; ⚠ `meta` 仅在显式命中分支 (:2085) 定义 — 组装器实现须 `meta = metadata_dict.get(col)` 显式取值 (None 时组装器内部走推断), 禁复用循环残留绑定]; ⚠ v2.3 铁律: **刻意不进 `get_variable_metadata_dict`** — 该函数无参签名 (codebook.py:329) 且被 stage 40/46/51 标签路径 + ~30 测试点调用, 挂入则三条导出链背上组装成本、51-only 列在 46 的 3442 列宇宙触发 SystemExit、而 `stata_export.py:252` 的 `except Exception` 捕不到 SystemExit → stage 全崩; gate 断言导出路径不 import 组装器), 然后:
- 消费端 A = codebook 四格式 (excel/csv/markdown/json, `scripts/generate_codebook.py`) → 任务 2 交付;
- 消费端 B = 新增 `write_notes_do_file` 生成 `{40,46,51}_apply_notes` do 族 (命名规则见 §3b), 把同一段文本以 Stata `notes` 注入三份 dta → 任务 1 交付。

**绝不**双头维护两套文本。⚠ **更正 (v2)**: stage 46 `_write_codebook_xlsx` (stata_export.py:1398-1428) **不**消费 `get_variable_metadata_dict` — 它是独立的轻量 7 字段产物 (var_name/original_name/label/data_type/value_labels/n_non_null/n_unique, 无描述字段), 仅经 `build_variable_labels` 同步 label 单字段。**决策: 保持其轻量定位不改造** (长文全量只进四格式 codebook, 避免 46 export 路径背上组装依赖); §4 只声明该分工, 不再宣称"两端自动同步"。

### 现状盘点 (2026-07-10 v2 实测修订, 事实基座)

| 事实 | 出处 |
|---|---|
| `VariableMetadata` 已有**恰好 12 字段**, 与用户清单一一对应 (描述=描述/注释, reference=学术引用, notes=备注) | `codebook.py:83-141` |
| 显式元数据 = **58 个构造调用点 → 实跑 283 个显式条目** (调用点多在 per-model/per-track 循环内); 其余 **~3170 列**靠家族推断函数 + `_AUTO_INFER_NOTE` 兜底 | 实跑 `get_variable_metadata_dict()` 计数 |
| 面板列数 (2026-07-10 本机实读): `51_panel_with_controls` = **3453** (最宽, codebook 覆盖宇宙, generate_codebook 优先读 51); `40/46` = **3442**; 差 11 列 = stage 51 controls 族 (`nf_*`/`fintech_share` 等只在 51)。**全文一切列数以生成期实读为准, 禁写死** | 本机 parquet/dta 实读 |
| 标签机制已有: `build_variable_labels` **四级**优先级 (meta[原名] → HEURISTIC[原名] → meta/HEURISTIC[**短名**] → 列名兜底), ≤80 字节 UTF-8 边界截断 | `stata_export.py:226,237-245` |
| dta 内列名 ≠ panel 原列名的列真实存在: >32 字符列经 `shorten_long_column_names` (截断+md5)、非 ASCII 列经 `asciify_non_ascii_columns` 改名, `rename_map` (short→original) 链式压平; 三 dta 短名一致性有既有 gate `test_dta_name_sanitizer_consistency.py` | `stata_export.py:826-950 (shorten) / :960 起 (asciify) / :1299-1336 (写路径应用+链式压平)` |
| pyreadstat / pandas to_stata **均不支持写 notes** → 注入必须走 .do 后处理; dta writer 共 **4 个**: 40 ← `pipeline/panel/export.py:1521` **及** `scripts/convert_parquet_to_stata.py` (第二 writer, :24 默认同路径声明, to_stata 实调 :143) / 46 ← `stata_export.py` / 51 ← `pipeline/falsification/controls.py:1299`; **任一重跑 = 该 dta notes 全灭** | 源码实读 |
| 引文白名单 = **874 唯一 DOI** (本机 `extract_refs` 全量实测精确), 来源 = `audit_dois.py::FILES` **13 个静态路径** (10 锚点 + 1 COMPANY_BANK 归档 + 2 LLMs_for_FinTech_dic 修复文档); `extract_refs` 只捕 `doi.org/10.x` 链接格式 | `audit_dois.py:33-51 (FILES) / :53 (DOIORG_RE)` |
| codebook 生成器已有覆盖度自检 (自动推断占比 / 引用填充率 / 来源阶段未知率 / 轨道分布) | `codebook.py:1987-2040` |
| 四格式 xlsx 用 `engine='openpyxl'` (codebook.py:2181); stage 46 xlsx 用 `xlsxwriter` (stata_export.py:1428) — **两端 engine 不同**, 守卫必须写在组装层 (engine 无关) | 源码实读 |
| csv writer 现状 = `to_csv(..., encoding='utf-8-sig')` 无 quoting 参数 (QUOTE_MINIMAL) → WP1 改 `codebook.py:2206` 加 `quoting=csv.QUOTE_ALL` | `codebook.py:2206` |
| `config/` 已 git 版本化 (77 tracked), `config/codebook_longdesc/` 不被 gitignore → 长文库可版本化; `data/processed` 整目录忽略 | git check-ignore 实测 |

---

## §1 核心架构: 家族长文库 + 组装引擎 (最承重)

**问题规模**: ~3453 列按 ≥1000 汉字口径 ≈ **345 万+ 汉字** (core 列 ≥5000 另计; 引文段英文另加不计入)。逐列独立写作不可维护、必然内部矛盾、且同族变体 (如 33 网络指标 × 3 判据、6 词典 × 8 消融 × 3 轨) 的"来源/公式/文献"本就同源。

**方案**: 描述/注释 = 五段确定性组装, 逐列产出唯一文本, **段落深度按 tier 分级** (§1a):

```
描述(col) = 家族核心长文(family)      # standard 家族 ≥700 汉字 / core 家族 ≥4200 汉字:
                                     #   构念/来源/方法学/文献综述 (core 另须: 识别策略定位、
                                     #   与相邻测度的构念区分、已知局限与稳健性梯子叙事)
          + 变体差分段(col)          # standard ≥350 汉字 / core ≥900 汉字: 该列区别于家族
                                     #   canonical 的精确语义 (轨道/模型/阈值/判据/权重/滞后)
          + 计算链路段(col)          # 机械生成: 来源阶段→函数→公式→上下游列
          + 动态统计段(col)          # 生成期从 panel 实测注入 (四态定义见下)
          + 引文段(family ∪ col)     # 由 frontmatter 结构化 citations 机器渲染 (§2);
                                     #   standard ≥3 条且 ≥300 字符 / core ≥10 条且 ≥1000 字符
                                     #   (⚠ 引文段以英文/DOI 为主, 汉字贡献≈0, **不计入汉字闸**,
                                     #   字符下限仅作引文段自身质量约束);
                                     #   条数上不封顶 (用户口径"越多越好"), 唯每条必过
                                     #   claim-fit 与白名单闸 (质量约束替代数量上限)
```

- **字数 gate 口径 (统一定义, v2.7 用户修订: 计量单位 = 汉字)**: **CJK 汉字数** = `len(re.findall(r'[一-鿿㐀-䶿]', text))` (Unicode 基本区 + 扩展 A; 英文/数字/标点/全角符号/空白**均不计**; ⚠ 实现层必须用 `\u` 转义形式 — 字面 CJK 端点字符在 Windows GBK 控制台回显即 UnicodeEncodeError 崩溃, 本轮实测踩中), 组装后逐列强制: **standard ≥1000 / core ≥5000 汉字** (结构列白名单豁免, §1a.7)。段落级下限 (上表) 是生产端工艺约束, **中文正文段独立过线** (core 4200+900=5100 > 5000; standard 700+350=1050 > 1000 — 引文段汉字贡献≈0 已刻意排除在推导外, 计算链路/统计段的中文内容作裕量), 逐列总量闸才是验收契约 — 两级都测 (⚠ 互锁: 总量闸的确定性盈余依赖段落闸同为硬闸, 禁把段落闸降级为 warning-only)。
- **fail-loud 分级 (防滚动落地期崩 pipeline)**: 字数不足时, 该家族 `_index.json.status == 'final'` → `SystemExit(1)`; `== 'draft'` → 告警计数 (渐进批次不断链)。终验 gate 要求全库 `final` 且 0 告警。库整体缺失该列家族 → 回退现状短描述 + 告警计数 (同理终验归零)。
- **动态统计段四态定义**: ① 占位符引用的列不在 panel 且非 pending → 生成期 `SystemExit(1)`; ② 列全 NaN → 渲染 "全缺失 (非缺失 n=0)" + T=2 尾注; ③ 正常 → 格式化注入 (dtype/min/max/mean/缺失率/非缺失 n, T=2 dev 值一律带"生产 T=19 重生后以实读为准"尾注); **④ `tier=pending` → 跳过动态统计段, 渲染"待外部财务面板接入"哨兵文本** (pending 列长文经同一组装器渲染进附录章, 不触 ①)。**未解析占位符残留 gate (宽口径)**: 组装器对一切未知 `\{[A-Za-z_]+:...\}` 语法 fail-loud (拼错 `{stats:...}`/`{STAT:...}` 不许静默穿过); 最终 md/json/xlsx 产物宽 regex `\{[A-Za-z_]+:[^}]*\}` 零命中; 写手规范禁用全角括号占位符。写手 agent 禁手填任何实测数字。
- **诚实披露**: 同家族变体共享核心长文属**刻意设计** (镜像 codebook 既有家族推断结构); 变体差分段保证逐列非逐字重复。此口径写进 codebook markdown 头部方法学声明 — **归 WP1 产物, `test_codebook_longdesc` 断言该声明存在**。
- **家族粒度与归族三级次序 (v2.5 补全 — SSOT 常量覆盖不满 3453 列, 无兜底规则则守恒 gate 永久红)**: ① SSOT 常量精确匹配 (`NETWORK_METRIC_BASES`(33) / `LLM_CLASS_SPEC` / `_RULE_ABLATION_VARIANTS` / `POLITICAL_WEIGHT_VARIANTS` / `LLM_MODELS`/`BERT_MODELS` / `bert_distribution` 五族 / benefit 维度 / IV 三引擎等); ② 未命中者复用 codebook 既有推断函数 (`_infer_category`/`_infer_source_stage`) 按 (变量类别 × 来源阶段 × 剥后缀基名) 机械聚类; ③ 仍剩者逐列单例家族 + `needs_family_review` 标记, **单例占比 >15% 触发人工复审归并**。家族总数**以 WP0 实测为准** (预估 250–400, 全文测算统一取 ~300 作工作值)。**family_id 编号规则**: `F` + 按家族首列字典序一次性分配三位号, 增量 merge 只追加不重排 (保证批次 by-name 清单可预先枚举)。

**长文库落盘** (版本化资产, 非代码) — **`_index.json` 唯一完整 schema (v2.5 集中定义, 各处引用以此为准)**:
```
news_process/config/codebook_longdesc/
├── _index.json    # 顶层: {tier_signoff: {date, method, user_ack, signed_manifest_sha},
│                  #        structural_whitelist: [target_bank, year],   ← 结构列豁免白名单
│                  #        families: {F001: {file, columns: [...], tier_by_col: {col: core|standard|pending},
│                  #                           core_rationale_by_col, status: draft|final, batch,
│                  #                           unit_draft, formula_draft, producer_draft}}}
│                  # ⚠ unit/formula/producer 的 *_draft 仅为 WP0 初判 (供 md 骨架生成);
│                  #   落地后 SSOT = 家族 md frontmatter, 组装器只读 frontmatter,
│                  #   gate 断言 frontmatter 存在时 index draft 字段不再被消费 (防双头)。
├── F001_xxx.md    # 每家族一文件, 唯一模板 (WP0 产骨架):
│                  #   frontmatter: {family_id, columns, unit, formula, producer, upstream,
│                  #                 citations: [...], new_dois: [...]}
│                  #   正文: "## CORE" 一节 (家族核心长文) + 逐列 "## VAR: <panel 实名>" 节
│                  #        (变体差分段; 组装器按 heading 精确匹配切分, 缺节 = draft 告警 / final 崩)
│                  #   尾部: <!-- rendered-citations:begin/end --> 机器渲染尾节 (人工禁改)
└── ...
```
- **组装产物格式铁律 (v2.5)**: 组装器输出 = **纯文本** (段间单空行, 段首中文小标题如【构念与来源】【计算链路】); 家族 md 人工区**禁用 markdown 结构语法** (#/**/表格/fence, lint gate 兜底); 渲染尾节 fence 标记仅存于 md 文件、组装时剥除; **notes 文本 = codebook 描述文本经 `_stata_notes_text` 归一, 此外零差异** (禁把 `##`/`<!-- -->` 注进 Stata notes)。
- 计算链路段的 producer 函数与上下游列来源 = frontmatter `producer:`/`upstream:` 字段 (WP0 初判 + 写手校对, 对抗 agent 对源码核验)。
组装层新函数 `codebook.py::_compose_long_description(col, meta, panel)` 读库 + 拼装。

### §1a Tier 机制: 关键核心指标清单 (core, ≥5000 汉字)

- **SSOT** = `_index.json` 逐列 `tier: core|standard|pending` **三态**字段; WP0 机械生成初版, 生效前**用户签核** (AskUserQuestion 完成签核, 结果落 `_index.json` 顶层 `tier_signoff: {date, method, user_ack, signed_manifest_sha}` — **signed_manifest_sha = 签核时 core 清单 + 结构列豁免白名单的联合内容哈希**, gate 断言"当前哈希 == signed_manifest_sha", 不等即强制重新签核 — 防"签核对象已非签核时清单"与豁免蠕变双假绿)。**签核问卷除 core 清单外, 须同时列出四项对用户字面要求的收窄决策请用户确认** (v2.5 忠实性披露): ① 结构列 (`target_bank`/`year`) 豁免 ≥1000 字数闸; ② pending 哨兵列暂不注 notes (不在 dta 中, 事实约束); ③ 顶刊闸允许 field 领域刊 ≤30%; ④ wp/preprint 不计入"非顶刊"分母 — 四项亦入 codebook markdown 方法学声明。**WP0 脚本定义为增量 merge** (面板列变/重跑时: 新列 → 新条目 `draft`, 存量条目的 tier/状态/rationale/签核**只增不改**), 绝不全量重写 — 否则 300 家族的 draft→final 进度与人工改判一次归零。
- **总判据 (扩量但不灌水)**: core = **"正文级"列** — 出现在论文正文主表 (主回归 / 2SLS 识别 / 机制表) 或识别叙事中被点名的列; 只出现在附录稳健性 battery 的列 = standard。
- **机械化双轨 (v2 重写 — 原"扫 .tmpl 提取 regress 变量"在原始模板上不可行: 模板变量 100% 走 `{{占位符}}`/`` `local' ``/`$controls` 宏, 零字面列名)**:
  - **主轨 = spec 驱动**: 直接读 **11 篇** paper_spec 的 `treatment` / outcome / `identification.iv` 字段 (真实存在的 SSOT); ⚠ P4 locus 无 `treatment.primary` 键而是 `primary_pair` → special-case, 其面板真实源列 = **`tech_frac` + `app_frac`** 双列入 core (pair 派生列 Stata 侧生成不落盘, 在差分段说明)。
  - **验证轨 = 先 instantiate 再扫** (v2.5 命令固化): 主线 = `stata_runner build-replication` 且三轨占位符取**生产默认** (`--sent full` 等 — 实测 bank_fintech_tone 强制要求 MAIN_{SENT,LOCUS,SUBST}_TRACK, 传 ctx 与 full 实例化出的列名不同, **扫描一律以 full 主轨实例为准**); 其余 paper 走 `_PAPER_DEFAULTS`; provisional 两篇跑 `scripts/instantiate_paper_stata.py`。产实例化 .do 后扫 regress 行 + 一跳 local/global 解析 (spec controls 回填 `$controls`)。**裁决规则 (v2.8)**: 验证轨**仅核验主轨候选在实例化 .do 中确实出现** (存在性核验), 扫描新增的 spec 外列一律打 `needs_review` **不自动入 core**; **bank controls 全体显式入负面清单** (M1-M6 字面含全部 controls, 无此排除则总判据被 controls 灌满)。
  - **模板白名单点名 (弃 "01_main_results" 幻影名与 "排除 tableA*" 黑名单 — 前者 0 命中, 后者与"含 2SLS"自相矛盾且会把 brokerage `20_table11_fwer_battery` 等非 tableA 附录性 battery 误收)**。每 paper 固化 {主结果, 机制, 2SLS} 真实文件名:
    | paper | 主结果模板 (真名) |
    |---|---|
    | P1 tone | 根级 `11_table2_main_m1m6` (+ IV: `22_tableA3_bartik_iv`/`25_tableA6_tone_iv_2sls` — 虽名带 tableA 但为识别承重, 白名单显式收) |
    | attention/substance/locus/collab | 各自 `15_*_main_regression` |
    | benefit_society / strategic_diff | `11_table2_main` (+ benefit IV `25_tableA12_iv_2sls` 显式收; strategic_diff 无独立 2SLS 模板 — 其 `12_table3_mechanism` 内嵌 ivreghdfe 2SLS 行, instantiate 验证轨可扫到, IV 主列另走 spec 主轨兜底) |
    | brokerage / llm_peer | `11_table2_main_iv_2sls` |
    | clarity (prov) | `papers/bank_news_clarity/stata_templates/11_table2_main_clarity_risk` + `12_table3_iv_2sls` |
    | disagreement (prov) | `papers/bank_media_disagreement/stata_templates/11_table2_main_disagreement_risk` (统一扫模板域; replication/code 下另有实例化产物) |
    机制表 = `12_table3_mechanism*` / `16_*_mechanism*`。⚠ provisional 模板里 `z_score`/NPL/RWA 是占位变量名 (CLAUDE.md 铁律), 扫描结果须过滤。
- **core 类别规则** (机械初判, 预估 **180–280 列**, 以实测为准; ⚠ **全部使用面板实存全名**, WP0 出稿后跑 `core 候选名 ⊆ set(panel.columns)` 断言, 幻影名 fail-loud — 唯 pending 态豁免):
  1. 11 篇 paper_spec 的 treatment 主列 (实名: P1 `llm_vote_tone_full` / P2 `attention_index_full` / P3 `sub_frac` / P4 `tech_frac`+`app_frac` / P5 `collab_frac` / benefit `benefit_mean_full` / brokerage `peer_tone_lag1_full` / strategic_diff `strat_diff_n5` / clarity `mean_clarity_score_full` / llm_peer 复用 `llm_vote_tone_full` / disagreement `cross_outlet_tone_variance_full`→**pending**);
  2. **各 paper 主 outcome/DV** — ⚠ v2.5/v2.6 口径更正 (以 spec 主轨为准, 宇宙=**11 篇**与类别 1 一致): **11/11 主 DV 全为外部财务哨兵** (funding_cost / ln_fintech_investment / cost_income_ratio_change_3yr / citation_weighted_patent / m_and_a_fintech / roa×3 [benefit/brokerage/llm_peer] / tobin_q / z_score×2 [两篇 prov 占位], **唯一名 8 个**; llm_peer 的 DV 按 `paper_spec.yaml:27-44` SAL-3 修正已是 `roa` 而非 CLAUDE.md 旧记的 avg_ft_intensity_full — `avg_ft_intensity_full` 面板实存但其 core 资格**仅经类别 4** headline 测度) → 哨兵列全部记 **`tier: pending`**: 家族长文照写入库 (12 字段照填, 来源阶段标"外部财务面板接入时构造"), 但**显式排除**在 WP0 守恒 gate / 逐列 ≥5000 gate / notes 注入对账之外; 其长文落 codebook markdown 附录"待接入变量"章; 财务面板接入后自动升 core 并回补 codebook 行 + notes (列入接入 checklist);
  3. **识别策略主 IV 列 = 全 11 篇 `identification.iv` 的 primary + fallback 主列全收** (v2 修订 — 原"三引擎 7 篇"漏掉 4 篇: P1 `prov_leave1out_tone_full`+`bartik_type_iv_full` / brokerage `peer_tone_2nd_lag1_full` / llm_peer `llm_peer_tone_iv_full` / strategic_diff `bartik_type_iv_full`; 三引擎 (l1o/bartik/outlet) 仅是其中 7 篇的来源注脚);
  4. 全局 headline 测度 (实名): `n_articles` / `n_articles_llm_valid` (分母/门控列, 裸名即 full canonical) / `fintech_share` (⚠ 仅 51 宇宙实存) / `attention_pct_full` / `avg_ft_intensity_full` 族 canonical + **`_lg` co-primary 对偶全收** — ⚠ v2.3 实测限定: 本类别仅 `avg_ft_intensity` 族有 `_lg` 且为**中缀形态** (`avg_ft_intensity_lg`/`avg_ft_intensity_lg_full` 等); attention_pct/n_articles/fintech_share 非嵌入族**无 `_lg`** (勿造幻影名, WP0 实存断言兜底);
  5. **跨厂商/跨模型 co-equal 主轨的 full 列**: 三 LLM `{gpt54nano,gemini31,deepseekv4}_tone_full` + 三 BERT `{finbert_cn,fin_sent_zh,finbert2}_net_tone_full` (27_tableA12 FWER 主角) — 其 ctx/ss 轨不入;
  6. 各大家族 canonical 代表列 (实名, 2026-07-10 面板实测): 六词典 `{loughran,jiang_2021,yao_2021,bian_2021,du_2022,you_2018}_tone_full` + `dict_avg_tone_full`、staleness canonical **`semantic_staleness_full`** (+对偶 `semantic_staleness_full_lg`) 与 **`surface_staleness_full`** (carve-out 无 `_lg`; ⚠ 无裸名, 实名均带 `_full`)、`avg_boilerplate_full`、herd canonical `avg_herd_weight_full` (+sum/min 姊妹)、网络溢出 headline (`industry_neg_shock` / `emb_peer_tone_lag1_full` / `bank_cogn_mean` / `bank_degree_cent` 等高频用列)、benefit 4 维度 full 轨 canonical、BERT 分布形状五族 canonical (`{b}_tone_entropy_full` / `{b}_xneg_frac_full` [τ=.90 无阈值后缀] / `{b}_net_tone_skew_full` / `bert_xmodel_lblhet_full` / `{b}_nt_iyvol_full`)。**嵌入族 canonical 的 `_lg` 对偶随收** (非嵌入 carve-out — surface_staleness/boilerplate/lblhet 等 — 无 `_lg` 不适用);
  7. 主键与结构列 (**`target_bank`**/`year`) — **结构列白名单** (逐列点名, 落 `_index.json` 供 gate 机械消费): **豁免 ≥1000 汉字闸**, 仅须 12 字段完整 + 短描述; 不进 core (§9.2 的全列字数闸按此白名单豁免, 否则"豁免长文"与"全列 ≥1000 汉字"字面矛盾)。
- **明确不入 core (负面清单)**: 梯子/消融/阈值/判据变体 (polw00/10、`_c2/_c5`、`_win1/_sent`、`_t80/_t95`、消融 7 变体)、ctx/ss 条件稳健轨、per-model 分类维度门控孪生、lag/交互派生、altagg 替代聚合臂、**bank controls 全体** (v2.8 补 — 主回归表字面含全部控制变量, 不排除则"正文级"总判据被灌满)。**判定次序 (v2.9 定序): 显式名单类别 1–7 均优先于负面清单** (brokerage treatment 是 lag 列按类别 1 入 core; `n_articles`/`fintech_share` 虽常作回归控制但按类别 4 headline 入 core); 负面清单仅约束验证轨 needs_review 候选与"正文级"总判据的兜底裁决。
- **反灌水守卫 (硬闸)**: core (含 pending) 占面板列数比例 **≤10%**; **每 core/pending 列一律必附** `core_rationale` 一句书面理由 (v2 修订: 无条件全量, 非"超限时才附"), gate 断言逐列非空; 超 ~10% 额外触发人工复审。
- **传染规则**: core 列所在家族核心长文按 core 深度写 (≥4200 汉字), 该家族其余 standard 变体免费复用深文 — 差分段达 standard 下限即可。
- gate: `tests/test_codebook_longdesc.py` 断言 — core 清单非空、实存 core 逐列 ≥5000 汉字、pending 列不进守恒/notes 对账、逐列 rationale 非空、占比 ≤10%、`tier_signoff` 非空、清单与 `_index.json` 一致。

---

## §2 引文铁律 (零臆造, 全计划最高优先级验收项)

**架构 (v2 重写): 结构化引文 SSOT + 机器渲染 APA + 双闸即时断言** (根治初版三断点: frontmatter 裸 DOI 漏扫 / 白名单差集断言无实现 / 散文 APA regex 结构性假阳):

1. **引文 SSOT = 家族 md frontmatter `citations:` 结构化列表**, 逐条 `{doi, type: journal|wp|arxiv|book, authors, year, title, venue, vol?, issue?, pages_or_artno?}`。**APA 7 文本由组装器按 type 分模板机器渲染** (渲染即合规 — journal 型带卷期页/文章号, wp 型 "NBER Working Paper No. x" 式, arxiv 型标注 preprint); 每条渲染产物末尾恒带 `https://doi.org/<DOI>` 链接。原"APA regex 闸"降级为渲染产物冒烟检查。
   - **渲染物化协议 (v2.3 P0 修复 — 否则 audit_dois 全量闸对整个长文库提取 0 条、"0 红旗"恒真)**: frontmatter 是裸 DOI 而 `extract_refs` 只捕 doi.org 链接 → 组装器必须把引文渲染段**物化回写**为家族 md 的机器生成尾节 (fence 标记 `<!-- rendered-citations:begin/end -->`, 人工区禁改), 该尾节即 audit_dois 核验域的扫描对象。配套双断言 (WP1 gate): ① `longdesc 域 extract_refs 提取 DOI 数 ≥ 全库 frontmatter citations 去重后唯一 DOI 总数` (防空转; ⚠ 勿实现成"逐家族唯一数求和" — 跨家族共享 DOI 会使该式恒红诱发弱化; ⚠ 右侧须与 extract_refs 同用 `clean_doi().lower()` 归一口径, 否则大小写/尾标点变体假红); ② 逐家族 `渲染段 DOI 集 == citations DOI 集` (防 frontmatter 改后忘重渲染的陈旧集假绿)。
   - **DOI 必填铁律 (防 book 型旁路)**: 每条 citation **必有 doi** — 无 DOI 经典 (Chesbrough 2003 / W&Z 1998 类专著) 改锚其权威书评/handbook 章节/期刊综述的 DOI; 确需保留 no-DOI 条目须带 `no_doi_ack` 台账编号 + 人工核验记录 + **替代可访问链接必填** (出版社页/ISBN/WorldCat/权威 handbook 页 — 用户口径是"doi **等**可访问链接", ack 条目渲染时带替代链接与 ack 编号); **差集闸对 doi 缺失且无 ack 的条目 fail-loud** (否则无 DOI 条目同时逃逸差集断言与 extract_refs, 是写手捏造书籍引文的自由通道)。
2. **白名单唯一来源** = 874-DOI (SSOT = `FILES_WHITELIST_ANCHOR` 13 静态路径冻结列表全量 `extract_refs` 去重 — 见第 5 条两列表分离, 长文库 glob **永不**进白名单派生源)。写手 agent 的 prompt 中**只发白名单子集**, 不许自带记忆引文。
3. **白名单差集断言 (新增实现, WP1 交付)**: `scripts/audit/check_longdesc_whitelist.py` — 对每家族 md 断言 `citations[].doi ⊆ (白名单 874 ∪ 已过闸 new_dois 台账)`, 差集非空即 `SystemExit(1)` 并打印越权 DOI; **组装期 + 每批收尾即时跑** (不等收口 — audit_dois 只做 DOI→标题回比, 抓得住幻觉文献但抓不住"真实存在却白名单外"的记忆引文, 集合差断言是唯一防线)。new_dois 台账单独落盘 (`_new_dois_ledger.json`: DOI/准入日期/核验轮次), 防"写进 frontmatter 即自动合法"的自我授权循环。**frontmatter 解析失败 = `SystemExit(1)`** (300 个 agent 写的 YAML 畸形概率不低, try/except 跳过 = 与 fail-open 同构的静默漏检), 并对账 "解析成功家族数 == `_index.json` 家族数"。**draft 出口 (v2.9)**: 差集闸对 `status==draft` **且**越权 DOI ∈ 该家族自身 `new_dois:` 声明的条目降级为告警计数 (批收尾 ① 准入后归零; final 态一律 SystemExit) — 否则批中途任何组装动作 (如 WP3 interim 重生) 会把含合法候选 DOI 的 draft 家族在准入前打死。
4. **新增 DOI 流程**: 候选 → frontmatter `new_dois:` 裸 DOI (仅作增量 diff 元数据) + **同一 DOI 必须同时以 citations 条目落地** (随渲染物化进尾节被机械闸回比) → **增量核验 = 白名单差集 + 逐条调 `audit_dois.fetch_crossref` DOI→标题回比 + 顺带查 Crossref `update-to`/retraction 字段筛撤稿** (函数现成 audit_dois.py:93, 撤稿筛查边际成本≈0; 只差集不回比会让幻觉 DOI 撑到批末才爆) → 对抗 verify agent 五元组复核 (题名-作者-年份-期刊-构念相关性, 镜像第九补编抓 18 错 DOI + 5 幻觉工艺) → 记入台账。一致性断言: `set(new_dois) ⊆ set(citations[].doi)`。
5. **全量机械闸节奏与两列表分离 (v2.3 防自授权环)**: `audit_dois.py` 改造为**两个列表**: `FILES_WHITELIST_ANCHOR` = 13 静态路径冻结列表 (**白名单唯一派生源**) 与 `FILES_AUDIT_ALL` = 锚 ∪ glob `config/codebook_longdesc/*.md` (机械核验域) — ⚠ 若把 glob 扩进同一个 FILES 再从 FILES 派生白名单, 家族 md 渲染出的 DOI 会自动并入白名单 → 差集闸恒真、new_dois 台账整体架空。配套三断言 (WP1 gate): `assert len(glob_files) > 0` + 与 `_index.json` 家族数对账 (防 fail-open) + `白名单派生输入 ∩ glob(codebook_longdesc) == ∅` (防膨胀)。全量重跑 (~15-30 分钟, 串行 Crossref 无缓存) **只在每批收尾 + WP5/WP6 收口**; audit_dois.py 加本地 `{doi: meta}` json 缓存 (OK 条目免重查) + UNRESOLVED 单次重试 (防网络抖动噪声红旗)。
6. **正文散文禁 doi.org 链接**: 家族 md 中 doi.org 链接**只准出现在渲染尾节内**, 正文提及文献一律 "作者 (年份)" 不带链接 (extract_refs 按最长行选 APA 行, 散文链接会顶替真 APA 行制造 TITLE_MISMATCH 假旗) — lint gate: 尾节外出现 `doi.org/` 即红。**配套弱断言 (防正文引用与 citations 制度化脱钩)**: 正文提取 `作者 (\d{4})` 型引注 → (作者, 年份) ⊆ citations 渲染集, 未命中即 WARN 供对抗审核聚焦 (中文行文/常见误报走白名单, 弱断言不设红灯 — claim-fit 终审仍在对抗 agent)。
7. **顶刊清单 SSOT** = `config/top_journal_list.yaml` (WP1 交付; 显式枚举 top 刊 + field 领域刊 JBF/JFI/JCF/IRFA/JEL/ARFE/CAR 等; **清单定稿随 WP1 提交时全文列出供用户确认**, 之后增删须记 rationale)。计分三分类 `top / field / wp-preprint`, **wp-preprint 不计入"非顶刊"分母** (与 arXiv 方法学补充锚地位一致 — 否则 LLM 方法学 core 家族先天过不了闸); **家族级**闸: (top+field 内) 非 top 占比 >30% 打回。**v2.11 实施期修正 (2026-07-11, 按 §3b probe 矛盾同款流程)**: 家族级顶刊闸经 C1 实证校准改**双层** — ① 每 final 家族 citations 中 top 分类 ≥1 条硬闸 (零 top 锚 = FATAL, 保住"国际顶级期刊学术支持"底线); ② 原"非 top 占比 >30% FATAL"降级为 WARN (记录占比数字供对抗审核聚焦与 WP5 终局报告); 清单扩跨学科旗舰 (PNAS/Nature Communications/PRX/AJS/ASR/ARS/TACL 等, 学科对等原则, 逐刊 rationale 在 yaml; PLOS ONE 与会议 proceedings 刻意不收); 全卷级 final 家族 top/field/unlisted 构成入 run_checks report 供 WP5 终局报告。**修正依据**: C1 实证 20+/36 方法学家族 (网络中心度/词典构造) 被 finance-centric 清单结构性打回, 而引文防伪与 claim-fit 五道防线全过 — 构念规范出处 (Social Networks/PNAS/AJS/PRX/TACL 等) 未列名被"未列名计非 top"口径全压进分母。
8. **2023+ 新颖度闸 (硬)**: **全卷级** 2023+ 占比 <50% 即终验红灯 (白名单 2023+ 实测 466/874 = 53.3%, 供给边际成立); 单家族允许例外但须 rationale — **构念定义型家族 (词典/经典理论锚, 最适年份分布天然偏老) 的 rationale 例外属预期常态, 不视为异常**。写手按年份倒序排引文。
9. **"0 红旗"验收判据精确化**: = 0 × (UNRESOLVED | TITLE_MISMATCH | YEAR_DIFF); `CNKI_EXPECTED` 为白名单化已知状态**不计红** (audit_dois 对 CNKI 特判恒非 OK, 白名单本含 1 条 CNKI)。
10. **禁**: CNKI/预印本充当主锚 (arXiv 仅方法学补充锚须标注); 单列引文段重复 DOI; 引文与正文陈述脱钩 (对抗审核逐条 claim-fit, 镜像第九补编先例)。

## §3 Stata 侧落地 (任务 1)

属性分工总览 (覆盖用户"变量名、标签、注释**等**属性"的"等"字): 变量名 = 既有 shorten/asciify 机制不动; 标签 = §3a; 注释 (notes) = §3b; **value labels = 既有 `labels.do` 覆盖 (46 嵌入 / 40+51 必跑), format = pyreadstat 写出自带 — 两者现状无缺口, 不在本计划改动范围**。

### 3a. 标签 (label)
- 缺口有二 (v2.5 需求追溯更正): ① 第 4 级兜底 (裸列名); ② **第 2 级 `HEURISTIC_LABELS` 实存成批纯英文标签** (如 stata_export.py:717 `'LLM ensemble vote tone (...)'`) — 仅"兜底归零"会让这些列假绿过闸, 与用户"标签均使用中文"要求不等价。
- **WP3**: 机械扫描三份 dta 全列标签 (⚠ 原名/短名两域判定 — 四级优先级含 rename_map 短名层) → **逐列 CJK 断言** (每列 label 须含 ≥1 个汉字; 主键结构列白名单豁免) → 兜底命中 + 英文 HEURISTIC 条目**逐族汉化** (技术术语可留英文括注, 符合仓库注释惯例) → gate: ① CJK 断言全绿; ② 非白名单兜底归零; ③ **零截断告警** (`build_variable_labels` 的 ≤80 字节截断一旦发生即计数, 新补中文标签须 ≤26 汉字不触截断, 超长者改写短名)。
- 硬约束: Stata label ≤80 字节 = ≤26 汉字; 标签定位"短中文指标名", 长说明进 notes。
- ⚠ 时序声明: WP3 若晚于 WP4 首批, 已提交的 `build/codebook/` 成品标签字段为 **interim 版**, WP5 四格式重生为权威版 (标签不进家族 md, 纯再生成零返工)。

### 3b. 注释 (notes) — 新增 `write_notes_do_file` (v2 按 4 项 P1 修法重写)

**文本层 — 专用 `_stata_notes_text()` (勿复用 `_stata_string_literal` 的 compound-quote 包裹)**: `notes varname: text` 的 text 是**宏展开后按行剩余原样入库** (verbatim 语境), 非字符串表达式 — 包 `` `"..."' `` 定界符高概率把定界符本身存进全部列的 note。专用函数: ① **(v2.10 probe 实证重写 — 原"保留 `\$`/`` \` `` 反斜杠转义"被 2026-07-10 三轮 probe 存储层字节证伪: notes verbatim 语境自有宏展开 pass 不承认反斜杠保护, `` \`macro' `` 静默展开为空、未闭合 `` ` `` 直接 r(132) 整条丢失、compound 包裹内同样失效; 而 label/display 双引号串语境转义有效 — 两语境行为分叉)** 危险宏序列**全角中和** (镜像 ④ `／／` 既有先例, 全角字符实测安全入库): 一切 `\` → `＼` (U+FF3C, 全量 — 消除 `\\`→`\` 折叠与 `\$` 反斜杠被消费两个观测畸变; notes 正文=中文散文+DOI URL, 反斜杠无正当出现场景); 一切 `` ` `` → `｀` (U+FF40, 全量 — `` ` `` 任意出现均危险: 未定义 local 静默变空/不闭合 r(132)); `$` 后接 `[A-Za-z_{]` → `＄` (U+FF04, 窄面替换 — probe 实证 `$100`/`$ `/行尾 `$` 原样保留安全, 数额美元号保真); ② **不包 compound quotes**, 引号字符原样 (probe 证实定界符会原样入库); ③ 换行归一为空格 (verbatim 语境换行会截断 do 行); ④ ` // ` / ` ///` 注释序列归一 (替换为全角 `／／` — 行内 `//` 前有空白即截断该行; DOI URL 的 `://` 前无空白, 安全; ` /// ` 续行吞后行已实弹证实); ⑤ 段首 "TS" 守卫 (probe 证实**存储层**即被替换为时间戳; 前置全角空格 U+3000 实测有效保护)。**WP2 动工首日先跑 1 分钟 probe do 实证** (`notes x: ...` → `notes list` 核对入库字节, **顺带验 use→save→pyreadstat 读回全链** — 把 WP5 读回断言的失败时点提前到 WP2) 后冻结该函数行为。**probe 判定纪律 (v2.5)**: 默认臂 = 本节五条规则; probe 仅作**证伪触发器** — 若观测与任一条规则矛盾, **停工回报重议, 禁现场发明替代方案**。**probe 结果台账 (2026-07-10 实施期, 三轮消歧)**: 规则① PROBE_CONTRADICTION → 编排会话按上述全角中和方案重议裁决 (fuzz gate 同步: 输出断言零 ASCII `` ` ``/`\`、零 `$`+宏名起始字符, `$100` 保真); 规则②③④⑤ 观测一致冻结; 附带定音: `confirm variable` 缩写命中实锤 (无 exact 时 rc=0!) / use→save 读回全链无损 / 中文 UTF-8 note 往返无损 / **pyreadstat 1.3.4 无 variable notes 读回通道** (`meta.notes` 仅 `_dta` 文件级; WP5 notes 层核验依赖 `notes list` log 扫描为主 + dta118 `<characteristics>` 区二进制解析为第三重独立通道, probe readback.py 已演示可行) / apply 脚本 Start-Process -Wait 须配超时+进程清理护栏 (probe 见 `exit, clear` 后进程滞留个案)。

**列名层 — rename_map 必传**: `write_notes_do_file(notes_by_col, rename_map)` — do 内一律用 **dta 短名** (>32 字符/非 ASCII 列在 dta 内已改名, 用 panel 原名 confirm 必失败且对账两侧同落选 → **假绿 + 改名列永久无 notes**, 这是初版对账闸抓不住的静默缺口); note 文本首段写明原始 panel 列名。生成钩在源码注释 "# 5." 的 `write_labels_do_file` (:1368) 之后 (rename_map 为主流程局部变量, 作用域活至 :1390 return)。

**守卫层**: 一律 `capture confirm variable <短名>, exact` (**必须 exact** — 默认允许唯一缩写匹配, ~3450 列 (以实读为准) 大量互为前缀, 错拼名可能缩写命中别列 → notes 静默挂错对象且对账全等)。

**幂等层**: 每列块内首行 `capture notes drop <短名>` 先清后注 (⚠ 披露: 会连坐删除该变量既有手工 notes — 本项目 dta 全程机器生成无手工 notes, 可接受但写明)。WP2 测试断言"重放两次 == 注入一次"。

**编排层 — master 模式** (命名规则: `{40,46,51}_apply_notes_master.do` 各一): `46_apply_notes_master.do` = `version 19` + `set maxvar 32767` + `use <dta>` 一次 → 顺序 `do` 各子卷 `_part01..NN` (每卷 ≤500 变量; **子卷纯 notes 命令, 无 use/save/exit** — CLAUDE.md 铁律: exit 绝不进被 master 调用的子 do) → `save, replace` → `exit, clear`。单次 use/save、失败原子 (未 save 即无半状态)。每 dta 一套 master (40/46/51 各一, 共用子卷生成器; 51 宇宙多 11 列, 40/46 对应子卷条目由 exact-confirm 跳过并**从该 dta 期望数中排除** — 期望数按各 dta 实际列名集合分别计算)。段切 ≤4000 字节/段 (UTF-8 字节边界; 单条 note 上限 67,784 字节, 双保险防行长; standard ≥1000 汉字 ≈3KB+引文段 → 1-2 段 [core 家族受传染变体 ~4550 汉字 ≈14KB → 4 段], core 5000 汉字+引文 ≈17KB → 5 段)。

**对账层 — log 标记法 (弃 `notes _dta:` 计数)**: `notes _dta:` 追加语义跨卷/跨次累积, 旧计数残留误导, 且 pandas/pyreadstat 读回 characteristics 通道未验证。改为: do 内 local 计数器逐列自增, 各卷末 `display "NOTES_APPLIED_PART01=<n>"`, Python 扫 log (encoding='utf-8', errors='replace') 提取并对账: **Σ各卷计数 == 该 dta 实际列名 ∩ (codebook 名经 orig→short 映射)** (pending 列排除), 差异非零即红; 收尾另跑一次 `notes list` 全量导出重扫作第二重独立核验 (机械全扫, 非抽查; ⚠ 解析口径 = 按 note 头 `varname:note#` 计数, 勿逐行匹配 — `set linesize 120` 会把长 note 折行)。

**执行**: canonical 注入对象 = `46_panel_yearly_full.dta`; 40/51 复用同一子卷 + 各自 master。**注入顺序 46→40→51**; 每 dta 内先 labels.do 后 notes (40/51 走 pandas 路径无嵌入 value labels, labels.do 本就必跑)。**失败处置 (v2.5)**: sidecar `_notes_applied_fingerprint.json` **逐 dta 键局部更新** (任一 dta 失败 = 该键缺失, doctor 按键逐 dta 告警), 失败 dta 直接重放其 master (幂等) 即恢复, 无需回滚; **注入前快照由 `scripts/apply_stata_notes.ps1` 开头自动落盘** (列数/dtype/var labels json, 供 WP5 读回全等断言)。启动 `/b` + `stata_runner.run_do` 封装 + 跑完扫 `r(###)`。

**注入后硬验收 (WP5)**: ① pyreadstat 读回三 dta, 断言列数/dtype/var labels 与注入前快照全等 (机械证明"只动 characteristics 层"); ② 跑 1 个既有根级模板 smoke (如 11_table2_main_m1m6 实例化产物), log 无新增 `r(###)`。⚠ 披露: `stata_runner` 的 `_rundo_skip_key` 以 dta 内容哈希入键 → 注入后所有以三 dta 为 data_deps 的模板 skip stamp 全体失效重跑 (方向安全, 生产上是一次全量模板重算)。dta 体积按**传染后 + 汉字口径**估 +~40-55MB/**每 dta** (三份合计 ~120-165MB, 128GB 下仍可忽略; notes 入 characteristics; core 家族的 standard 变体复用 ≥4200 汉字深核心 → 受传染列可达千级、每列 ~15KB [汉字 3 字节/字 + 引文段], 非逐列独立 tier 估); WP1 生成期落体积日志实测校准 (全卷汉字总量按传染后 ~700-1100 万汉字预估)。

**陈旧性自动检测**: apply 成功后写 sidecar (`_notes_applied_fingerprint.json`: 三 dta 内容哈希); doctor 新检测段比对当前哈希, 不等即 loud WARN "dta 已重生, notes 缺失/陈旧, 请重放" (⚠ doctor 是硬编码 `[n/6]` 顺序 print, 六段跨 stata_runner.py:853-948 (def :834) — 加第 7 段须同步 renumber 全部 `[n/7]` 字面量 + CLAUDE.md "6 段诊断"口径, 归 WP2); stage 46 收尾日志加固定提示行。**Stata 注入执行不进 pipeline 主线** (依赖本机 Stata, CI 无), 独立脚本 `scripts/apply_stata_notes.ps1`。

## §4 代码手册侧落地 (任务 2) — 12 字段逐字段策略 (v2 补全)

| 字段 | 填充策略 | 验收 |
|---|---|---|
| 变量名 / 数据类型 / 来源阶段 / 变量类别 / 文本轨道 | 既有机制不动 (panel 驱动 + 推断函数) | 覆盖度自检既有报告 |
| 标签 | §3a WP3 (codebook meta 命中列两端同源; **HEURISTIC-only 列两端须同步补** — HEURISTIC_LABELS 是 stata_export 私有字典, codebook 侧走 `_infer_label` 可分叉) | CJK 断言 + 兜底归零 + 零截断 gate |
| 描述/注释 | §1 五段组装 (≥1000 / core ≥5000 **汉字**双闸) | §9.2 |
| **单位** | **家族 md frontmatter `unit:` 字段** (比率/篇数/字符数/z 分数等家族级同源), WP0 家族映射时一并初判, 组装层回填 | **非空率 100%** (结构列白名单 + **pending 列 [填"待接入"]** 豁免) |
| **取值范围** | **动态统计段同源机械回填** (数值列 min–max / 枚举列 nunique 值域, T=2 尾注同 §1); **pending 列填"待接入"** | **非空率 100%** (同上豁免口径) |
| 计算公式 | 家族 md frontmatter `formula:` 机械回填; 无公式列 (原始计数等) 须在备注声明"原始计数无导出公式" | **空串归零** (声明式豁免计数) |
| 学术引用 | 引文段短版 (家族 3-5 条代表作 — 短版展示口径, 非引文条数上限; 全文在描述内) | **填充率 100%** |
| 备注 | 保留既有披露注入 (_DICT6/_AUTO_INFER 等) | `_AUTO_INFER_NOTE` 终验归零 |

- **生产者分工 (v2 更正 + v2.3 挂载点收口)**: 长文全量只进 `scripts/generate_codebook.py` 四格式 (组装器由 `generate_codebook` 发射循环唯一调用, 见 §0); stage 46 `_write_codebook_xlsx` 保持轻量 7 字段定位**刻意不改造** (仅 label 字段经 build_variable_labels 同步)。
- **md writer 重写 (v2.3 P1 修复, WP1 交付)**: 现行 `to_markdown` 单表 (codebook.py:2219) 在长文下实测损坏 — 单元格换行破表成变量名为空的续行 (破坏"产物行数=面板列数"判读)、`|` 不转义、tabulate 逐格 pad 到全列最宽 → 30MB+ 纯 padding。改为**逐变量分节式** (`## 变量名` + 12 字段块), 顶部摘要表只放短字段; §9.5 "md 全文完整" 按该格式机器可验。
- **四格式落点迁移 (v2.3 P1 修复; v2.4 更正)**: 现落点 data/processed 被 gitignore → 成品不可版本化, 与 WP5 "by-name 提交推送"冲突 (盘上四格式现已不存在即实证后果)。**md + json (权威载体) 迁 `build/codebook/`** — ⚠ v2.4/v2.5 实测更正: `news_process/.gitignore:7` 是 `build/` 整目录忽略且**真 git 根 = 上级 `data_antigravity_project` (其 `.gitignore:11` 也有非锚定 `build/`)**, `build/manual_facts` **并非 tracked 先例**; ⚠ **单条 `!build/codebook/` 否定实测无效** (父目录被目录模式忽略后 git 不下探)。实测可用修法 = 在 `news_process/.gitignore` **替换**原第 7 行为三行组合 (缺一不可, 顺序敏感, 深层文件优先级覆盖根层规则):
  ```
  !/build/
  /build/*
  !/build/codebook/
  ```
  归 WP1 交付并配 gate (`git check-ignore build/codebook/x.md` 须不命中 + `build/manual_facts` 仍被忽略)。xlsx + csv 留 data/processed 作可再生品不入 git。
- **xlsx 32,767 字符守卫写在组装层** (engine 无关 — 四格式端 openpyxl / 46 端 xlsxwriter 两个 writer): >30000 字符截断 + 尾注"全文见 codebook.md/json"。
- csv: WP1 改 `codebook.py:2206` 加 `quoting=csv.QUOTE_ALL` (现状 QUOTE_MINIMAL, 文件合法但按计划口径统一全引号)。
- codebook 覆盖宇宙 = 51 面板 (generate_codebook 优先读 51); 46/40 dta 少 11 列 (nf_*/fintech_share 族) — notes 注入按各 dta 宇宙对账, codebook 全量按 51。

## §5 分阶段工作包 (WP)

| WP | 内容 | 性质 | 产物 / gate |
|---|---|---|---|
| **WP0** | 家族映射机械化: `scripts/audit/build_codebook_family_map.py` — spec 主轨 + instantiate 验证轨 (§1a) 扫 51 面板全列, **按 §1 三级归族次序** (SSOT 精确匹配→推断函数聚类→单例+review 标记, >15% 复审; family_id 编号规则同 §1) → `_index.json` 初版 (family→列清单 + tier 三态 + unit/formula/**producer** 初判) + **per-家族写手输入包三件套 (§6)**; core 清单 + 四项收窄决策出稿 → 用户签核 → `tier_signoff` 落库 | 机械, 1 会话 | **守恒 gate**: Σ家族列数 (剔除 tier=pending 条目) == 面板实存列数, 0 孤儿列; core 候选 ⊆ panel.columns (pending 豁免) 0 幻影名; rationale 逐列非空; `tests/test_codebook_family_map.py` |
| **WP1** | 组装引擎 + 引文闸: `_compose_long_description` (唯一挂载点=generate_codebook 循环) + 长文库 loader + 字数双闸 (draft/final 分级 fail-loud) + 占位符四态/宽残留 gate + citations 机器渲染 APA + **渲染物化回写尾节 (双断言: 提取数下界 + 渲染段==citations 集)** + **`check_longdesc_whitelist.py` (含 frontmatter 解析 fail-loud + 解析数对账 + no-DOI ack 闸)** + **`audit_dois.py` 两列表分离 (FILES_WHITELIST_ANCHOR 冻结 / FILES_AUDIT_ALL=锚∪glob, 三断言) + 本地缓存 + UNRESOLVED 重试** + **`config/top_journal_list.yaml`** + **md writer 重写 (逐变量分节式)** + **四格式落点迁 `build/codebook/` (md/json 入 git)** + xlsx 组装层截断守卫 + **csv QUOTE_ALL (codebook.py:2206)** + markdown 头部方法学声明 + 生成期体积日志 | 代码, 1-2 会话 | `tests/test_codebook_longdesc.py` (组装确定性/双字数闸/四态渲染/宽占位符零命中/白名单差集/两列表分离断言/渲染物化一致性/**gitignore 双断言 [codebook 不命中 + manual_facts 仍忽略]**/**index draft 字段防双头 [frontmatter 存在即不消费]**/**列集合三处全等 [_index.columns == frontmatter.columns == md "## VAR:" 节集]**/方法学声明存在/缺库回退告警/幂等/导出路径不 import 组装器) |
| **WP2** | `write_notes_do_file` 全套 (§3b: `_stata_notes_text` probe 实证 + rename_map + exact confirm + notes drop 幂等 + master 编排 + log 对账) + `scripts/apply_stata_notes.ps1` + doctor 第 7 段 (含 [n/7] renumber + CLAUDE.md 口径同步) + 陈旧性 sidecar | 代码, 1 会话 | `tests/test_stata_notes_do.py` (转义 fuzz: `` `" ``/`$`/换行/` // `/` ///`/段首TS/`\$`/`\\`/尾`\`; 前缀歧义名 exact fuzz; 分段字节边界; 重放两次==一次; 对账数含改名列) |
| **WP3** | 标签中文化审计: 原名/短名双域全列扫描 → 兜底命中 + 英文 HEURISTIC 条目 (实测 179+ 静态条目 + 9 个生成族) 逐族汉化 | 机械+批量写作 | **逐列 CJK 断言全绿** + 非白名单兜底=0 + **零截断告警** + `validate_stata_compat` 全绿 |
| **WP4** | **内容生产主战役**: 家族长文 + 变体差分 + 结构化引文, 多批次多智能体 | 多会话, 见 §6 | 每批过 §6 机械闸五件套 + 对抗审核 0 CONFIRMED P0/P1 |
| **WP5** | Phase 1 终验收口: 全量 pytest + audit_dois 全量闸 + 覆盖率四合一 (§9.2) + Stata 实机注入三 dta (master 模式) + 读回全等断言 + 模板 smoke + `notes list` 机械全扫 + 抽查 30 列 (**含 ≥10 列 core**) + 四格式重生 + by-name 提交推送 | 1 会话 | 终局闸报告落 `scripts/audit/` |
| **WP6** | **Phase 2: company_listed_bank / company_tax_bank 面板族** — 复用 WP0–WP2 引擎, 覆盖两管道全部 dta (listed: 主 cooc + 7 权重 + altagg 2; tax 镜像: cooc + branch_{city,county}w + altagg 2; 固定列 20): 家族映射扩展 (预估 15–25 家族; **落盘分置**: 两管道各自 `_index_company_{listed,tax}.json`, 家族 md 同目录 F9xx 段号; listed/tax 镜像家族以 frontmatter `shares_core_with: F9xx` 键**共享核心长文**、差分段写清两管道口径差: 主键 stock_code vs usci×year / 样本框 5,528 vs 44,771; ⚠ WP1 组装器须实现为 **panel-无关纯函数** [禁 import 主线 51 路径常量], WP6 从两管道各自 codebook 生成脚本传入其 panel 调用); 自有 codebook md 富集为同一 12 字段 schema; notes.do 注入 (两管道 dta 均 pyreadstat 写出, 方案完全适用 — listed 02:936 / tax 02:607 实证); 每批过同一机械闸五件套; **tier 判据降级为人工点名** (两管道无 paper_spec 无 stata_templates, §1a 机械双轨零输入): headline 白名单从管道 README/canonical 权重族声明人工点名 + 逐列 rationale + **独立一次签核** (signed_manifest_sha 同机制); ≤10% 闸在 20 列宇宙换算 = **每面板 core ≤2 列**。1.6GB 级 dta 的 use→save 注入墙钟与磁盘峰值**首个面板实测校准后再排批**。**前提**: 两管道 04 altagg 脚本已入库 (并发会话 main=3400c1cc, 前提已满足), 产物清单以入库后为准; ⚠ 覆盖宇宙**排除** `.tmp` 残留与 `data/processed/` 下目录迁移前的陈旧副本 (实测: **5 个** `company_bank_{boardw,dsgw,execw,shareholderw,supervisorw}_panel.dta`, 各 1,602,853,327 字节, 另有 6 个陈旧 parquet 含 branchw — 均勿误入 notes 对账; 活跃落点 = company_listed_bank/data/) | 多会话, 1-2 批 | 同一机械闸五件套 + 两管道既有 gate 测试全绿 (**计数以 `pytest --collect-only` 实测为准** — 2026-07-10 两次实测已从 147+147 漂移至 150+150, 恰证"以实测为准"必要) + registry 哈希锚零变动 (纯元数据层证明) |

WP0→WP1→WP2/WP3 (可并行) → WP4 (批次滚动, 每批过闸即提交) → WP5 (Phase 1 收口) → **WP6 (Phase 2, 计划内必做)**。⚠ 勿动两管道 01–04 计算逻辑与 registry 哈希锚。

## §6 WP4 批次工艺 (镜像 litanchor 补编 + manuscripts-enrichment 先例)

- **机械闸五件套 (显式定义, v2.3 +①)**: ① **守恒快检** — `set(_index 非 pending 列) == set(51 panel.columns)` **且** `Σ|各家族列清单| == |并集|` (后式封死"同列被两家族重复收录"的 set 盲区) 秒级 (pending 条目剔除后对齐面板, 与 WP0/§9.2 同口径) (并发会话加列是本仓常态, 漂移最晚每批收尾即爆, 勿拖到 WP5); ② 字数双闸 (≥1000 / core ≥5000 **汉字**, CJK 计数 §1); ③ DOI 白名单差集闸 (`check_longdesc_whitelist.py`, 含 frontmatter 解析成功数对账); ④ 引文渲染闸 (渲染尾节存在 + 渲染段集合==citations 集合 + 尾节外 doi.org 零命中 lint); ⑤ 占位符残留闸 (宽 regex `\{[A-Za-z_]+:[^}]*\}` 零命中)。对抗审核是第六道 agent 评审, 不属机械闸。
- **写手铁律 (v2.5, 用户口径"尽可能详细/越多越好")**: 字数与引文条数下限是**验收地板, 非写作目标** — 在 claim-fit 可审、零注水的前提下按信息量写满; §9.2 配汉字数分布报告 (中位数/P10 距地板距离), 聚集在地板 +10% 以内即触发抽查复审。
- **写手输入包 (v2.5 生产规格)**: WP0 脚本顺带产 per-家族输入包三件套 — ① 家族列清单 (自 `_index.json`); ② 源码摘录 = `_index.json` 记录的 producer 模块按基名 grep 自动截取相关函数 ±N 行; ③ 白名单引文子集 = 874 条渲染行按家族关键词 (基名+构念词) 检索 top-K + 该家族所属论文 manuscript refs 全量。首批由编排会话人工抽查输入包质量后再放量。
- **批次粒度**: 每批 30-40 家族 → ~300 家族 = **8-10 批** (WP6 另加 1-2 批); 每家族 1 写手 agent (输入=上述三件套) + 1 对抗审核 agent; core 家族的额外深写 agent **拿写手初稿做深化** (非从零写), 复审并入对抗轮 (查: 引文-陈述 claim-fit / 公式与 `pipeline/*` 源码一致 / 无幻觉数字 / 无跨家族矛盾 / T=2 退化陈述准确 / **与 CLAUDE.md 铁律一致** — 凡涉三轨/co-primary/梯子必须复述"各自 just-identified 并排、禁混同一 over-identified Hansen J"口径, 凡涉 n_articles/full-only 门控与 2026-06-29 口径一致)。
- **预算公式**: ~300 家族 × 2 (写手+审核) + core 家族 (~60-100) 额外深写/复审 1 agent ≈ **660-700 agents** (WP6 另加 30-50; 返工冗余另计), 纯 agent token, $0 pipeline API。**core 深文批次优先排** (正文级列先交付, 论文写作即取即用)。
- 每批收尾 (v2.8 顺序修正 — 原"五件套→DOI 核验"会让含合法新 DOI 的批被差集硬闸在准入前打死): **① 增量 DOI 核验先行** (fetch_crossref 逐条回比 + 撤稿筛查 + 对抗 verify 五元组 → 准入 `_new_dois_ledger.json`) → **② 机械闸五件套** (此时差集闸的白名单已含新准入 DOI) → **③ 对抗审核 0 CONFIRMED 且该批五件套 0 告警后, 编排会话把该批家族 `status` 置 `final`** (draft→final 唯一迁移点, 随批提交 — 否则 WP5 "全库 final" 闸永不可达; 带告警置 final 会把定位成本推迟到下次组装硬崩) → ④ by-name 提交 (`config/codebook_longdesc/F*.md` + `_index.json` + 台账 + `build/codebook/` md/json 成品; **排除** `*constants.json`/并发产物)。

## §7 铁律 / 雷区清单 (改动前必读)

1. **引文零臆造** (§2): 白名单外 DOI 未过"增量核验 + 对抗复核 + 台账"三关 = 不准入库; 集合差断言组装期即时跑。
2. **golden/数值零接触**: 一切改动不产生/不修改任何 panel 数值列; 改前改后 `pytest -m fast` + baseline-stash A/B 证 0 新增失败。
3. **硬限四条**: label ≤80 字节 / note 段 ≤4000 字节 (单条上限 67,784) / xlsx 单元格 ≤32,767 字符 (守卫在组装层) / do 子卷禁 use/save/exit。
4. **capture confirm 必须 `, exact` 且配 log 计数对账** (缩写匹配会静默挂错对象; 28_tableA13 教训升级版)。
5. **rename_map 必传**: notes/labels/对账一律以 dta 短名为键, 原名只进 note 正文 (改名列静默零覆盖是对账假绿的唯一已知形态)。
6. **Stata 启动**: `/b` + master 末尾 `exit, clear` + 扫 log `r(###)`; 禁 `/e`/裸 GUI。
7. **字数口径唯一** (§1/§1a): **CJK 汉字数** (基本区+扩展A regex, §1 定义), standard ≥1000 / core ≥5000 **汉字** (tier 三态 SSOT=`_index.json`, 签核落 `tier_signoff`); 历史口径 (≥2500 单一、≥500 两级、"去空白字符数"计量) 均已作废, 勿在任何 gate/文档残留。
8. **T=2 退化诚实披露**: 动态统计段 dev 值一律带"生产 T=19 重生后以实读为准"尾注; 列数等基数**禁写死** (本机实读 3442/3453, 随重生漂移)。
9. **dta 重生 = notes 全灭**: 4 个 writer (40×2/46/51) 任一重跑后必须重放 notes master; 防忘三重保险 = doctor 指纹段 loud WARN + stage 46 收尾提示行 + 生产重生 checklist 条目。do 幂等可重放 (notes drop 先清)。
10. **pandas 旁路丢 notes**: `pandas.read_stata` 不读 characteristics — 任何"读 dta→改→to_stata 重写"的旁路脚本都会静默丢全部 notes; 新增此类脚本一律先过本条评审。
11. **审批门**: 无付费 API、无 golden 重生 → 不触 M0; 生产重生时 notes 重放排在重生后执行。
12. **`config/codebook_longdesc/` 单会话串行** (v2.8): WP0/WP4/WP6 编排会话对该目录加会话锁文件 (镜像 cooc 单实例锁先例) — 8-10 批滚动期两会话交错写 `_index.json` 是本仓已实弹的损坏形态 (SUPPLEMENT_VIII 覆盖/hunk 被扫走), 增量 merge 只防 WP0 重跑不防并发。

## §8 刻意不做 / DEFER

- **不逐列独立写 ~3450 篇**: 家族+差分组装 (§1); 若审稿人要求逐列全独立文本再评估。
- **不把长文塞 label / char 单条**: 80 字节与行长硬限。
- **不改造 stage 46 `_write_codebook_xlsx`**: 保持轻量 7 字段 (§4 分工决策), 长文只进四格式。
- **不做英文双语长注释**: 用户口径=中文说明 (技术术语英文); 投稿包需要时按需生成。
- **不动 OUTPUT_REGISTRY** (codebook/do 均非注册 parquet 产物)。
- **哨兵 pending 列的 notes 注入**: DEFER 到外部财务面板接入后 (checklist 已挂 §1a 类别 2)。
- **生产 T=19 重生后的 notes 重放与四格式重生**: 列入生产重生 checklist (§7.9 三重保险), 本计划不预演。

## §9 验收总闸 (WP5 = Phase 1 / WP6 = Phase 2, 全绿才算完)

**Phase 1 (主线):**
1. `pytest` 全量 0 新增红灯 (baseline-stash A/B)。
2. **覆盖率四合一**: 全列 (=生成期实读 N, 覆盖宇宙=51 面板; 禁写死基数; **结构列白名单豁免字数闸**) 描述 ≥1000 汉字 + 实存 core 逐列 ≥5000 汉字 + **WP0 守恒复验** (Σ家族列数 [剔除 tier=pending 条目]==N, 0 孤儿) + **core 占比 ≤10% 复验** + `tier_signoff` 存在; `_AUTO_INFER_NOTE` 归零; 标签三闸全绿 (**逐列 CJK 断言 + 非白名单兜底归零 + 零截断告警**); **12 字段逐字段非空率报告** (单位/取值范围 100% [白名单+pending 豁免] / 计算公式空串归零 [声明式豁免计数] / 学术引用 100%; **报告由 generate_codebook 落 `build/codebook/field_coverage_report.json`, gate 读文件断言而非人读日志**); **汉字数分布报告** (逐列三单位: 汉字数 [闸] / 字符数 / UTF-8 字节数 — 一次诊断引文超重、xlsx 32767 逼近、note 分段预测; 中位数/P10 距地板距离, 地板 +10% 内聚集触发抽查复审); 全库 `status==final` 且回退告警归零。
3. 引文: audit_dois 全量闸 (核验域 = `FILES_AUDIT_ALL` = 锚∪glob, **三断言**: glob>0 / `_index` 家族数对账 / 白名单派生输入∩glob==∅; 白名单只从 `FILES_WHITELIST_ANCHOR` 派生) **0 红旗 = 0×(UNRESOLVED|TITLE_MISMATCH|YEAR_DIFF), CNKI_EXPECTED 不计红**; 白名单差集闸全绿; 渲染物化双断言全绿; 2023+ 占比 ≥50% (硬); 尾节外 doi.org 零命中。
4. 三 dta 实机注入 (master 模式): log 计数对账全等 (按各 dta 宇宙, pending 排除) + `notes list` 机械全扫核验 + 随机 30 列人工抽查 (**固定 seed + core/standard 分层, 含 ≥10 列 core**; 引文可点开、公式与源码一致) + **读回全等断言** (列数/dtype/var labels 快照对比) + **1 个根级模板 smoke 无新增 r(###)**。
5. 四格式 codebook 重生成功; xlsx 0 截断告警 (或截断清单已披露); md/json 全文完整 (含"待接入变量"附录章覆盖全部 pending 列)。
6. 终局报告 + by-name 提交推送 main。

**Phase 2 (WP6, company 两面板族):**
7. 两管道全部 dta 列 100% 覆盖 (≥1000 汉字; 人工点名 headline 列 [≤2/面板] ≥5000 汉字); 同一机械闸五件套全绿 (守恒快检按两管道各自 dta 宇宙)。
8. 两管道既有 gate 测试全绿 (计数以 `--collect-only` 实测为准), registry 哈希锚零变动。
9. `company_*_cooc_panel_codebook.md` 富集后与主线 12 字段 schema 同构; notes 注入对账全等。

## §10 评审台账 (v1→v2→v2.1→v2.2→v2.3→v2.4→v2.5→v2.6→v2.7→v2.8→v2.9)

**第一轮 (2026-07-10, 5 路独立评审: 代码事实 / Stata 机制 / 模板 tier / 文档一致性 / 引文闸)**: 合计 1 P0 + 16 P1 + 29 P2 + 20 NIT, v2 已全部落实。要点: P0 = 单位/取值范围两字段零策略 (→ §4 逐字段表); P1 簇 = tier 机械判据在原始模板不成立 (→ spec 主轨 + instantiate 验证轨 + 真名白名单)、8/9 DV 哨兵列不实存 (→ pending 三态)、notes verbatim 语境/rename_map/exact/对账信道 (→ §3b 重写)、引文闸三断点 (→ 结构化 citations + 差集断言 + glob 防 fail-open)、双生产者"自动同步"不实 (→ §0/§4 分工更正)、列数 3395 陈旧 (→ 实读 3442/3453, 禁写死)、批次算术 (→ 8-10 批)、幂等 notes drop 落地。已验证属实的事实基座 (874 DOI 精确 / 21 根级模板 / 12 字段 / 各列名类别 5 / WP6 机制名与样本框 / pyreadstat 双管道写出) 保留于 §0。

**第二轮终验 (2026-07-10, 2 路全新智能体: 全新通读+17 项 P0/P1 回归核验 / v2 新事实机械复核)**: 回归 17 项 → 16 全落实 + 1 部分落实 (3395 残留 1 处); 事实复核 13 项 → 11 属实 + 2 部分属实 (04 altagg 已被并发会话 3400c1cc 提交入库、doctor 行号上界 903→948) + **0 不实**。新增 findings = 1 P1 (pending 列与动态统计段/取值范围 100% 闸字面矛盾 → 四态④"待接入"哨兵 + §4 豁免口径) + 3 P2 (3395 残留 / standard 引文段补 ≥150 字符下限使加总成真下限 [v2.2 已再上调至 ≥300] / §9.2 守恒补 pending 剔除) + 3 NIT (预算上界 660-700 / disagreement 统一扫模板域 / convert 脚本行号写法), **v2.1 已全部落实**。两轮独立实证均确认: 无幻觉事实、无孤儿承诺、WP↔验收互指闭合、承重数字 (283 条目/3453·3442/874/53.3%/147+147) 逐一复现。终判: **ok_to_ship (计划层)**。

**v2.2 (2026-07-10, 用户口径再修订)**: 全量 ≥500 → **≥1000 字符** (core ≥5000 不变)。传播点: 标题/§0×2/§1 问题规模 (170 万→345 万)/§1 段落下限 (standard 家族核心 300→600、差分 150→250、引文 150→300, 真下限加总 1150>1000)/§1 gate/§4 表/§6 四件套/§7.7/§9.2/§9.7/§3b 段数与 dta 体积估算。

**第三轮 (2026-07-10, 3 路: 口径传播完备性 / red-team 对抗 / 事实扫尾)**: 合计 **1 P0 + 8 P1 (跨报告去重后) + 8 P2 + 5 NIT**, v2.3 已全部落实。P0 = audit_dois 全量闸对新长文库结构性空转 (frontmatter 裸 DOI 不被 extract_refs 捕获 + 正文禁链接 → 提取 0 条、"0 红旗"恒真; 修 = 渲染物化回写尾节 + 提取数下界/渲染段==citations 双断言)。P1 簇: FILES 扩 glob 白名单自授权环 (→ 两列表分离三断言) / 组装挂载点字面矛盾 (→ 唯一挂载点=generate_codebook 循环, 禁进无参 get_variable_metadata_dict) / md writer to_markdown 单表长文实测损坏 (→ 逐变量分节式重写) / 四格式落 gitignored 目录不可版本化 (→ md/json 迁 build/codebook/) / book 无 DOI 旁路 (→ DOI 必填 + no_doi_ack 闸) / _index 签核被机械重生覆盖 (→ 增量 merge + signed_manifest_sha) / §10 台账悬空 / attention_pct 无 `_lg` 幻影 (类别 4 限定 + staleness/词典/herd/BERT 五族 canonical 实名化)。P2/NIT: 五件套 (+守恒快检) / WP6 tier 人工点名 ≤2 列/面板 + 陈旧 dta 副本排除 / frontmatter 解析 fail-loud / 宽占位符 regex / 正文引注弱断言 / 传染乘数体积重估 (+30-40MB) / notes list 按 note 头计数 / probe 验读回全链 / 2023+ 闸构念家族例外常态化 / 结构列字数豁免落字 / core 段数 3-6。事实扫尾另证: 六词典/staleness/herd/BERT 五族 canonical 实名、`n_articles_llm_valid` 裸名即 canonical、rename_map 作用域至 :1390 (labels 调用为源码注释 # 5)、两管道 dta 基线 10+5、`pytest -m fast` 收集 4499、书面事实 0 不实。red-team 攻不破清单: WP0 无时序死锁 (build-replication 纯模板替换) / convert 脚本无自动触发通道 / notes 与 value labels 无冲突域 / paper_spec 基座 / 字数加总数学。

**第四轮终验 (2026-07-10, 2 路全新智能体: 全新通读 + 第三轮 22 项回归 / 全口径机械残留扫描 + v2.3 新事实复核)**: 回归 22 项 → 20 完全落实 + 2 携带传播残留/计数误差; 机械扫描 17 项旧口径 → 16 项零生效残留 + 1 项违规 (WP6 四件套); 新事实复核 7 项 → 1 不实 (**`build/manual_facts` 实为 gitignored 非 tracked 先例** → 修法改为 `.gitignore` 加 `!build/codebook/` 否定规则归 WP1 + gate) + 1 计数误差 (陈旧 dta 6→**5**, 另 6 个陈旧 parquet 一并排除)。通读新增 4 P2 + 3 NIT: WP6 四件套残留 / **§6 守恒快检公式集合代数写反** (→ `set(_index 非 pending 列)==set(panel.columns)`) / §9.3 残留 v2 单列表旧措辞 (→ 三断言两列表) / 陈旧副本计数 / meta 循环残留绑定陷阱 (→ 显式 `metadata_dict.get(col)`) / 断言① Σ 语义 (→ 全库去重后总数) / §1 字数闸补结构列豁免括注。**v2.4 已全部落实**。两路独立实证再次确认: 承重架构 (SSOT 组装 + 两列表引文闸 + 渲染物化闭环 + tier 三态 + notes master 编排) 全部成立、事实基座零幻觉。终判 (第四轮时点): ok_to_ship (计划层)。

**第五轮 (2026-07-10, 3 路全新视角: 需求符合性追溯 / 实施者可执行性走查 / v2.4 增量复核+全新通读)**: 合计 **5 P1 + 15 P2 + 14 NIT** (去重后), v2.5 已全部落实。P1 簇: ① "标签均使用中文"与 WP3 兜底归零 gate 不等价 (HEURISTIC_LABELS 第 2 级实存成批纯英文标签, stata_export.py:717 实证 → 逐列 CJK 断言 + 英文条目逐族汉化 + 零截断 gate); ② WP0 无兜底归族规则 (SSOT 常量覆盖不满 3453 列 → 三级归族次序 + 单例 >15% 复审 + family_id 编号规则); ③ 组装产物文本格式悬空 (→ 纯文本铁律 + 家族 md 唯一模板 [## CORE / ## VAR: 实名 heading 定界] + fence 剥除 + notes 与描述零差异); ④ 写手输入包无生产规格 (→ WP0 产三件套: 列清单/源码摘录 grep±N 行/引文子集 top-K+manuscript refs); ⑤ **单条 `!build/codebook/` gitignore 否定实测无效** (父目录目录模式忽略 git 不下探; 真 git 根在上级 data_antigravity_project 且其 .gitignore:11 也有 build/ → 实测可用 = news_process/.gitignore 第 7 行替换为 `!/build/` + `/build/*` + `!/build/codebook/` 三行组合)。P2 簇: 需求忠实性四项 (下限是地板非目标铁律 + 字数分布报告 / 引文条数上不封顶 / no-DOI ack 补替代可访问链接 / 四项收窄决策进签核问卷与方法学声明) + 可执行性八项 (instantiate 命令固化 full 主轨 / _index.json 唯一 schema + unit/formula SSOT=frontmatter 防双头 / producer·upstream 入 frontmatter / probe 证伪触发器纪律 / 注入顺序 46→40→51 + sidecar 逐 dta 键 / field_coverage_report.json 机械可验 / WP6 index 分置 + shares_core_with + 组装器 panel-无关纯函数 / llm_peer DV 按 spec=roa → 9/9 全哨兵口径更正)。NIT: 撤稿筛查 / 断言① clean_doi 归一口径 / 快检加 Σ 防重复收录 / value labels·format 分工声明 / gate 计数 147→150 漂移记录 / 抽查 seed 分层 / top_journal 定稿披露 / 深写 agent 拿初稿 / WP3 interim 声明 / F 编号 / audit_dois :33-51 行号等。需求追溯矩阵: 16 项 = 10 完整 + 5 部分 (已修) + 1 轻偏离 (已修), 12 字段 12/12, 三修订 3/3。

**第六轮终验 (2026-07-10, 2 路全新智能体: 全新通读 + 第五轮 20 项回归 / 全量作废口径终扫 18 项 + v2.5 新事实抽核 5 项 + 台账算术复算)**: 回归 **20/20 全落实**; 作废口径 16/18 项零生效残留 + 2 处低危标签 gate 摘要未同步 (已修); 新事实 **5/5 属实** (含 HEURISTIC 英文条目 AST 实测 179 静态 + 9 生成族 [数百条汉化工作量] / llm_peer spec `primary: roa` / gitignore 三行组合 mini-repo 实测有效 [`build/codebook/` 不忽略且 `manual_facts` 仍忽略] / `_infer_label` 等三推断函数实存 / `_PAPER_DEFAULTS`+instantiate 脚本实存); 五轮计数复算恰好相等。通读新增 0 P0 / 0 P1 / 3 P2 / 5 NIT (类别 2 计数口径 9/9→**11/11 唯一名 8** 闭合 / §9.2·WP3 行标签三闸同步 / WP0 行互指三级归族+输入包+producer 初判 / WP1 gate 列补 gitignore 双断言+防双头+列集合三处全等 / `status` 字段名统一 / §4 短版括注 / meta 取值纪律对齐), **v2.6 已全部落实**。终判 (第六轮时点): ok_to_ship (计划层 + 需求符合层) — 需求追溯矩阵 16 项全闭合 (12 字段 12/12, 三修订 3/3, 四项收窄决策进签核), 承重架构六轮 17 路独立实证零幻觉。

**v2.7 (2026-07-10, 用户第七次修订)**: 字数计量单位 **字符 → 汉字** (全量 ≥1000 汉字 / core ≥5000 汉字)。实质变更非措辞: ① gate 计数改 **CJK 专用 regex** (基本区+扩展A, 英文/数字/标点/空白均不计); ② **引文段汉字贡献≈0** → 段落下限重推导为中文正文段独立过线 (standard 家族核心 600→**700** + 差分 250→**350** = 1050 > 1000; core 4000→**4200** + 800→**900** = 5100 > 5000; 引文段字符下限降级为自身质量约束不计入闸); ③ 派生数字连带 (345 万汉字 / 段数 / dta 体积 +40-55MB / 汉字数分布报告 / 全卷 ~700-1100 万汉字)。传播点: 标题/§0×2/§1 公式+gate/§1a×3/§4 表/§6 五件套②+分布报告/§7.7/§9.2/§9.7/§3b 段数与体积。随后第七/八轮评审见下。

**第七轮 (2026-07-10, 2 路: 汉字口径专项 [传播+CJK regex 实测+算术] / 全新通读+实证抽查)**: 专项 = 1 P2 (传染规则 ≥4000 残留 → 4200 汉字) + 5 NIT (报告命名/体积口径=每 dta 三份合计 120-165MB/**`\u` 转义防 GBK 控制台崩** [实测踩中]/三单位诊断报告/CJK 覆盖边界判断无需扩区), 14 处"字符"残留逐一判定 13 处合规保留、CJK regex 码点逐一实测等价、段落重推导算术全对且总量闸确定性成立 (加互锁注记)。通读 = **1 P1 + 5 P2 + 4 NIT**: P1 = **新 DOI 准入时序死锁** (批收尾"五件套→DOI 核验"顺序会让含合法新 DOI 的批被差集硬闸在准入前打死 → §6 对调为"①增量核验准入→②五件套"); P2 = 宇宙恒 51 不实 (generate_codebook 会回退 40 → 长文模式 51 缺失拒跑) / **draft→final 迁移无执行者** (→ §6 批收尾第③步=对抗审核后编排会话置 final, 唯一迁移点) / `_index.json` 并发写零防护 (→ §7.12 目录单会话串行锁) / 验证轨裁决规则缺失 (→ 仅存在性核验 + 新增列 needs_review + **controls 全体入负面清单**防灌满) / 传染 ≥4000 (与专项重叠); NIT = master 命名规则/core 5 段/doctor 853-948/~300 工作值措辞。8 组实证抽查 7 组精确复现。**v2.8 已全部落实**。

**第八轮终验 (2026-07-10, 2 路全新智能体: 全新通读 + 第七轮 16 项回归 / 作废口径终扫 15 项 + v2.8 新事实抽核 + 台账八轮完整性)**: 回归 **16/16 全落实**; 作废口径 **15/15 零生效残留**; v2.8 新事实 3 属实 + 1 缺口 (两路同源发现: **组装期差集闸对 draft 家族无分级出口** — 批中期含合法候选 DOI 的家族会被硬闸在准入前打死, 修 = §2.3 draft 出口: `status==draft` 且越权 DOI⊆自身 `new_dois:` 声明 → 降级告警计数, 批收尾 ① 准入后归零, final 态硬崩); 八轮台账完整、计数全对、v2.7/v2.8 概括准确; doctor/generate_codebook 行号实测精确。通读另收 1 P2 (类别 1-7 均优先于负面清单定序, 防 `n_articles`/`fintech_share` 双可) + 4 NIT (置 final 前提=五件套 0 告警 / §7.12 锁补 WP6 / 128GB 重复短语 / §0 do 族命名 / :253 引用位)。**v2.9 已全部落实**。终判: **ok_to_ship (计划层 + 需求符合层 + 汉字口径)** — 八轮 21 路独立评审, 承重架构与事实基座零幻觉。
