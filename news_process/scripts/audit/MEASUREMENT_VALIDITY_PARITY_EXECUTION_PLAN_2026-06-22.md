# 四维 LLM 文本测度「测量效度**验证管道**对称化」执行计划（代码就绪 / 效度结论 deferred-T18）

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


> ## 实现执行状态（2026-06-22，用户授权自动执行后；R6 实现前终审 GO → 实现 → R7/R8 执行成果终审）
> **已实现（$0/golden-safe/未提交，13 文件 by-name，零 clobber 并行脏树）**：WS-0/WS-A/WS-B/WS-C/WS-D/WS-E 全部承重代码 + 测试（test_63=43 / test_73=29 / gate 新增 / 全绿）。R8 终审：回归 GO + golden-safety GO + EIC「无 P0、工程实施 GO」（真盘 51_panel 端到端复跑验证）；唯一真 bug = C2 加权 bootstrap 双重计权（已修方案 B + 回归锁）。**golden 未触动 / 计数 16-16-16 / 模板 142 / test_panel_reproducibility 绿。**
> **显式 deferred（非遗漏，R8 收口记录）**：
> - **真人工标注 / T=19 付费重跑 / separate-call NMI 探针（M0）/ golden 重生** = 须用户拍板，非代码所能。
> - **M5 codebook.py:1013 旧号 39d→73 + HTMT 术语降级** = `codebook.py` 已被**并行 rule-ablation 会话改脏**，by-name 提交会 clobber → 本计划**不碰**，留并行会话或后续顺修（Stata 模板 `21_substance_clarity_robustness.do.tmpl` 5×39d→73 因 clean 已做）。
> - **WS-F 文档层（coverage 三分入 codebook / 三维 face-content / known-groups / 窗口保真审计二选一）** = locus/collab/substance 均 provisional **无 manuscript（.tex 零命中）→ 无落点**，deferred 至各篇 manuscript onboarding。
> - **WS-G（收敛效度降级/收窄，计划标"可选"）** = 采用缺省路径＝留空 + LLM-only 披露（§2.3 注³）；locus hybrid 收窄已由 WS-A 的 `paper_spec` `hybrid_disclosure` 字段覆盖。
> - **提交前**：还原 `data/processed/v3_5_1_constants.json` sidecar 时间戳漂移（已还原）。
>
> **v3.3 · 2026-06-22 · 五轮对抗审计收敛 = 工程实施 GO（计划层）+ R6→实现→R7→R8 执行层 GO**
> 收敛轨迹：v1.0 → R1（31-agent）→ v2.0 → R2（11）→ v3.0 → R3（5）→ v3.1 → **R4（10-agent 终审：可实现性逐行复证 GO；抓 5 个前三轮盲点）→ v3.2（收 population-weighted κ/Gwet AC1 公式 P1-01/P2-04 + 门vs模板 F-b + pilot 资格门 M1 + 矩阵误标 collab 三轨 κ M2 + 单次调用 NMI 混淆 EIC-F1 + face/content/known-groups/伦理/tone 框）→ R5（2-agent 聚焦闭合：终审怀疑者 GO + 独立直读复证 8 项代码主张全属实；唯 1 个 P2=checklist 残留旧"保守"措辞未随 EIC-F1 降级）→ v3.3（收口该 P2，NMI 措辞全文统一为 confound-limited）**。**五轮（57+2 agent）后零 P0/P1 未决。**
> 范围决策（用户 2026-06-22）：对「待办事项」撰写执行计划，再以国际顶刊最高标准多智能体反复审核验证。
> 任务定位 = 把 **substance（实质/象征）· locus（底层/应用）· collab（自研/协同）** 三维的**验证管道**提升到与 **tone（语调）** 方法一致的水平（criterion / discriminant / reliability 三类效度的代码框架 + 协议）；**coverage（是否报道）** 是关键词构念、不同效度范式、单列；并补齐共性最大短板 = **真实人工金标准回填（含反锚定盲标 + per-dimension 效度声明门）**。
> **粒度铁律（R2-P0-3 厘清）**：**效标效度（criterion，Panel A-G + G0 tone κ）= 文章级**（抽自 约 1125 篇语料，**不受 T=2 约束，现盘可启动**）；**判别效度（stage 73 panel 相关）+ 构念正交（stage 72 NMI）= bank-year 级**（T=2 退化，min-N 守卫 + insufficient_obs，仅验管道）。本计划**当前盘面交付 = 代码就绪 + 单元测试，零效度结论**；任何效度数值结论 deferred 至 T=19 + 真人工回填。
> 前置依据 = 五次多智能体工作流（① 五维 LLM 三轨投票一致性核验；② 7 路代码地面真相采集；③ R1 6 视角；④ R2 4 视角；⑤ R3 3 视角 + R4 5 视角终审）。
> **⚠ 两个「GO」勿混（R4-EIC-F2/F6）**：本计划的「GO」= **工程实施 GO**（计划内部一致、file:line 准确、可据以执行，R4 可实现性逐行复证确认）；**≠ 对应 measurement 论文发表就绪**。后者额外要求：(a) 至少 G0-tone 真 κ **被实际跑出**（非仅可跑）；(b) R4-EIC-F1 单次调用 NMI 混淆经 separate-call 探针处理或诚实降级。**本交付物本质 = 「测量效度验证基础设施 + 预注册协议」贡献**（research-infrastructure / replication-package），非「已验证的四维测度」贡献——投稿前若作 measurement paper，须先执行 G0-tone（计划明确其现盘可启动、非 T=2 阻塞），否则四维 criterion 全 pending 近乎必然 major-revision/reject。

---

## 0.5 R1 审计返工裁决（v1→v2，必读）

> 裁决依据 = R1 每条发现经第二个对抗智能体「读计划+读代码」核验（STANDS=真缺陷 / PARTIAL=部分成立 / REFUTED=审稿人误读）。

| F# | 来源·原severity | 核验裁决 | 缺陷一句话 | v2 处置 |
|----|------|:---:|------|------|
| **F1** | 毒舌P0-2 | PARTIAL(强) | v7ref（LLM 预测）与人工标注同表并排，列名前缀≠盲标 → anchoring → 效标效度虚高 | **MUST**：WS-D 双文件（编码者盲表零 LLM 标签 + 对账表后解锁）；新增 **R-0** 风险；预注册盲标 |
| **F2** | 统计P0-1 | STANDS | §5 功效表 κ CI 半宽 0.045 是误把比例 Wilson 半宽当 κ 半宽；真值 N=400/κ0.7 = 0.07–0.12 | **MUST**：§5 按患病率重算+内嵌复核式；改「保持500」结论 |
| **F3** | 统计P0-2 | PARTIAL | population_weight 只入 accuracy；κ/α 是 sample-conditional 非总体 | **MUST**：双报 sample-conditional + population-weighted κ；加权 bootstrap；删错误因果链 |
| **F4** | 统计P1-1 | STANDS | 数十个 κ/HTMT/permutation 判定无 FWER | **MUST**：Holm/Romano-Wolf + 确证(full)/探索(ctx/ss)分层；§5 family 列 |
| **F5** | 统计P1-2 | PARTIAL | §5 把三分类 tone α 与二分类 innovation κ 同列 | **MUST**：加「估计量/类别数」列；表题去「二分类」绝对化 |
| **F6** | 实现S-1 | PARTIAL | 泛化 73 非「轻量加循环」：κ 子路径硬编码 substance 阈值 0.5/方向锁，frac 需中位数二分 | **MUST**：focal_label 参数化 + 泛化 κ 函数；§3 改标「中等函数体重构」 |
| **F7** | 复现P1-1 | STANDS | 抽样脚本用裸名 `innovation_substantiveness`，盘上仅 `_full/_ctx/_ss` → KeyError 先决崩溃 | **MUST**：WS-D 改 `_full` + loud 守卫 + 回归锁 |
| **F8** | 复现P1-2/实现S-4 | STANDS | Panel E/F/G 同处**第 2 个** tabular；v1 的「tabular==2→改3」是错的，会制造回归 | **MUST**：保持 tabular 计数 2；测试改为 Panel G 子表头存在性断言 |
| **F9** | 复现P1-3 | PARTIAL | 验收门 5 离线烟雾因 40_panel 缺盘空转；R-2 真护栏=单元测试；盘上实为 51_panel | **MUST**：R-2 钉为单元测试硬断言；烟雾走合成 fixture；订正文件名 |
| **F10** | 方法M-2/M-5·完整M-3·毒舌P3-1 | STANDS | WS-G「canonicalize_topic 是 locus 第二机理」循环（吃 LLM 自产 fintech_topic + 词表撞 prompt） | **MUST**：撤「第二机理」；降为 hybrid 内部一致性诊断（非收敛效度）；矩阵 locus 收敛→LLM-only |
| **F11** | 方法M-4·毒舌P0-3 | STANDS | 单 indicator |corr| 非 HTMT（无衰减校正）；单 item AVE≡1 永真空检验；MTMM 误称 heteromethod | **MUST**：术语降级为 |Pearson/Spearman|；删单 item AVE 判定；主判别证据改挂 stage72 NMI；订正 73/74 docstring |
| **F12** | 方法M-3·复现P2-3·毒舌P0-1 | PARTIAL | 计划诚实标命门，但无 manuscript 级硬门；全部真标注推 deferred | **MUST**：新增 **G0** 最低可发表门 + `validity_claim_gate`；tone 先行真 κ 提为非 deferred |
| **F13** | 毒舌P1-3 | PARTIAL | 人工金标准判全文，ctx/ss 测窗口 → 机器-人工 κ 是混合下界 | **MUST**：innovation Panel ctx/ss 附 `GOLD_CONSTRUCT_DISCLOSURE`；窗口金标准 deferred |
| **F14** | 毒舌P1-1 | PARTIAL | 三轨已正确定位为窗口稳健（主指控驳回），但 substance full_ss κ=0.368 失败轨对未披露 | **MUST**（R2-V2-2 升格）：披露 passes_threshold=False；checklist 加项 |
| F15 | 完整M-1 | PARTIAL | 遗漏 stage 74（LM 判别效度）73/74 分工 | SHOULD：§2.3 补 73/74 边界交叉引用 |
| F16 | 完整M-2 | PARTIAL | 缺 test-retest/predictive 效度定位（矩阵已有 prompt 敏感性行） | SHOULD：补 test-retest=N/A 披露 + predictive→§10 |
| F17 | 完整M-4·毒舌P2-2 | PARTIAL | coverage 效度误锚 dict_coverage（dict≠media coverage） | SHOULD：WS-F 三分拆 |
| F18 | 完整M-5 | PARTIAL | Panel G/HTMT 未接 paper 复现包；无 spec 现存 validation 块可对齐 | SHOULD：deferred 镜像 substance clarity 模板；validation schema SSOT=G6 |
| F19 | 实现S-5 | P2 | 键名两命名空间须区分（**R2-V2-1 订正：v1 误写"4 处统一裸 collab"**） | SHOULD：(a) schema/gold 维度键=裸 `'collab'`；(b) task_name/classifier/pred 前缀=`innovation_collab_mode`（`_mode` 是真实落盘列名不可删，误裸名→join 全 skip） |
| F20 | 实现S-6/复现P2-1 | P2 | 跨构念块缺 min-N 守卫；substance prob vs locus/collab frac 测度异质 | SHOULD：复用 `_safe_corrcoef`+min-N≥10；披露口径差异 |
| F21 | 复现P2-2·毒舌P2-1 | P2 | §5 只看总体 κ，未论证少数类 per-class recall 功效；抽样框由 LLM 标签定义→漏判不可估 | SHOULD：§5 加少数类 CI；加纯随机层估漏判 |
| F22 | 完整M-6 | P2 | stage 73 输出文件名 dim-suffix vs 既有 backward-compat + schemas.py:181 注释 | SHOULD：保留 substance 旧名作别名 |
| F23 | 复现P2-4 | P2 | per-dim optional 是结构重构（`innovation_pending_reason` str→per-dim dict） | SHOULD：明列子步骤 |
| F24 | 完整M-8 | P2 | docid join 键缺则全 innovation 维 pending | SHOULD：WS-0 加 docid 硬门 |
| F25 | 完整M-9/M-10·复现P3-1/P3-2 | P3 | tone 抽样框 reconcile；provisional→fully 显式排除；WS-G 词表落点；备份 | SHOULD：逐条文档化 |
| **F-驳1** | 方法M-6 | **REFUTED** | 「Gwet AC1 与 NaN 守卫抵消」——守卫仅 `min==max` 真常量触发，AC1 域=偏态有变异，**互斥域不冲突** | 不改（可选注一句边界） |
| **F-驳2** | 毒舌P0-3/P1-2 部分 | **REFUTED** | 「stage72 说 substance×collab 重叠」——审稿人把 NMI `'strong'` 读反（**strong=强正交=好**，weak 才是重叠）；实测两阶段一致判可区分 | 不改裁决，但订正 v1 的 L93「72 已覆盖三维互正交」overclaim 散文 |

> **R1 净结论**：方法层无致命阻断（毒舌 NO_GO 的三条 P0 经核验全 PARTIAL：事实成立但戏剧化定性被驳；其余 5 视角 GO_WITH_FIXES）。**F1（盲标反锚定）与 F2（功效数值错）是 v1 的真硬伤**，连同 F10/F11 的方法学术语错配，已在 v2 收口；F12 把「效度证据=零」从分散免责升格为发表硬门。

### R2 收口复审裁决（v2→v3）

> R2 4 视角：① must-fix 收口审计（F1-F14 **全 P3 = 14 条正确充分收口**，无 P0/P1 残留）；② 回归一致性；③ 可实现性复核；④ 新鲜毒舌。

| R# | 来源·severity | 裁决 | 缺陷一句话 | v3 处置 |
|----|------|:---:|------|------|
| **R-V2-1** | 回归 P1 | STANDS | v2 新引入矛盾：F19「4 token 统一裸 collab」与正文 `innovation_collab_mode` 打架（`_mode` 是真实落盘列名） | **MUST**：区分两命名空间（已订正 F19 + WS-A） |
| **R-P0-2** | 毒舌 P0 | STANDS | `validity_claim_gate` 全局门 → tone 的 κ 解锁全四维 = criterion 偷换 | **MUST**：改 **per-dimension** 门（每篇 spec 绑自身维度；tone κ 只解锁 tone 论文） |
| **R-P1-3** | 毒舌 P1 | STANDS | 给编码者窗口文本 → 人机同读预切窗口=同源循环；窗口 κ 测「共同反应」非「窗口切对没」 | **MUST**：全文 gold 为主效标；窗口 κ 降为「窗口解读一致性」辅助诊断；窗口保真度独立前置审计（复用 ctx/ss_is_fallback） |
| **R-P0-1** | 毒舌 P0 | PARTIAL | NMI=monomethod 自证/tautology **被驳**（NMI 测构念非冗余 Bagozzi-Yi 1988 合法）；残留=「主证/承重」措辞须降级 | **MUST(措辞)**：NMI 改称「同源 LLM 标注器内部构念非冗余正交检验」+ 显式披露无 heteromethod 判别证据。⚠ **R4-EIC-F1 再降级**：v3.0 的「共享方差抬高→近零是保守证据」方向性论证已被推翻——单次调用条件解码可**双向偏倚、符号不可识别**，现统一标「描述性·confound-limited」，**禁回「保守」**（见 note² L167/§9-7/checklist） |
| **R-P1-2** | 毒舌 P1 | PARTIAL | 「判别不可得」**被驳**（72 NMI 即理论锚定主证）；残留=locus/collab 的**定向 κ** 无理论符号锚 | **MUST**：locus/collab **取消定向 κ**，只报无向 \|corr\|/ρ + permutation null（非冗余旁证，无需符号理论）；substance 保留其有理论定向 κ |
| **R-P1-1** | 毒舌 P1 | **REFUTED** | 「coverage 当第 4 个 LLM 维」=误读（v2 已分离 coverage）；仅矩阵网格视觉可收紧 | 仅 cosmetic：§2.3 矩阵改标题 + coverage 列 ✅→△门控 |
| **R-P0-3** | 毒舌 P0 | **REFUTED** | 「全 T=2 空转」=混淆文章级/panel 级（效标=文章级 约 1125 篇非 T=2；门已纯 code/test；pending 已覆盖全维） | 仅 cosmetic：标题/§7 已显式厘清粒度（见顶部粒度铁律） |
| R-V2-2 | 回归 P2 | STANDS | must/should 计数 13+12（非 14+11） | F14 升格 MUST → **14 must + 11 should** 一致 |
| R-V2-3 | 回归 P2 | STANDS | 0.045 双义（伪 κ 半宽 vs 正确 accuracy CI）；coverage 0.040 无源 | 按**指标类型**设禁（非按数值）；§5 注 0.040→0.068 来历 |
| R-V2-4/5/6 | 回归 P3 | — | κ 半宽区间不统一 / 行号 :683→:685 / Carlson §3.3 不可核验 | 统一 0.089–0.102；订正 :685 + 73 文件名映射；Carlson 改概括引用 |
| R-impl-V1 | 实现 P3 | — | per-dim pending 须区分全局 pending（文件/读/docid）vs 单维 pending | WS-A 明列：全局保留顶层 str，单维走 dict |
| R-impl-V5 | 实现 P2 | — | F7 裸名 bug 修复面含 :65-86 共 4 处分层判据（非仅 :60-62），现盘即崩 | WS-D 列全修复面 |
| R-impl-V6 | 实现 P3 | — | 生产 stage 73 main() 仍读 40_panel（勿改 51） | WS-0/§7 注明 51/合成仅供单元/烟雾 |

> **R2 净结论**：14 must-fix 全部正确收口（收口审计全 P3）。新增 2 个真 P0/P1（per-dim 门 R-P0-2、窗口循环 R-P1-3）+ 1 个 v2 自引回归（命名空间 R-V2-1），**均为文档/spec 层，golden-safe，无新架构**。毒舌的 2 条 P0（NMI 自证、T=2 空转）经核验 REFUTED，确证计划核心稳健（NMI 是合法保守证据；效标效度文章级现盘可跑）。R3 仅需确认 v3 收口无新矛盾。

---

## 0. 关键再定位（直读代码复证）

| # | 常见误读 | 直读代码实况 | 证据 |
|---|----------|--------------|------|
| R0-1 | 「五维都该做方法一致的 LLM 三轨投票」 | **只有 tone/substance/locus/collab 四维**走 LLM 三轨投票（同一次 stage 21 调用 / 同冻结 prompt v8 / 同三模型多数票 / full·ctx·ss 三轨一次共产）。**coverage 是关键词分类计数（Aho-Corasick），不同构念，刻意不走 LLM**——设计而非缺口。 | `unified_cot.txt` L94-114；`tone_llms.py:1377-1432`；`attention_media.py:458` |
| R0-2 | 「locus 与 substance/collab 提取方法一致」 | **不完全**：locus 是 hybrid（LLM 多数票定标签 + `canonicalize_topic` 关键词**仅调置信度** + 空票回退）；substance/collab 纯 LLM。 | `tone_llms.py:926-965` vs `:2041-2058`/`:2075-2092` |
| R0-3 | 「现有 κ 证明了 LLM 判得对」 | **否**：盘上所有 κ 都是机器-机器。**真实机器-人工 criterion validity 在盘上为零**。 | `sentiment_validation_results_*.json` `status=pending`；`classification_eval_results_DEMO.json` |
| **R0-4（命门）** | 「补好验证代码 = 效度就绪」 | **否**：效标效度的全部价值在机器 vs 真人工金标准的吻合数字；四维（含 tone 这把参照金尺）真值全空 → **任何「测度有效」主张在投稿时均 unsubstantiated**。代码就绪 ≠ 效度就绪。 | 同 R0-3 + `61_human_samples.xlsx` 人工列 0/1000 |
| **R0-5（反锚定）** | 「v7ref 列名加前缀 = 盲标」 | **否**：`manual_validation_sampling.py:152-168` 把 LLM 预测加 `v7ref_` 前缀写进**与编码者标注列同一张 xlsx 同一行**；列名前缀挡不住人眼读相邻单元格（Tversky-Kahneman anchoring）→ 人工金标准被 LLM 系统性锚定 → 机器-人工 κ 虚高 = LLM 给自己打分。 | `manual_validation_sampling.py:152-168`；v1 R-1..R-8 无此风险条目 |

**结论**：补的**不是**「提问投票一致性」（四维已极致同源），而是 **(a) 验证层对四维覆盖不对称 + (b) 人工金标准框架缺位/数据全空 + (c) 盲标反锚定 + (d) 效度声明的 manuscript 级硬门**。

---

## 1. 目标 / 非目标

### 目标（G）
- **G0（最低可行性演示，非 deferred · F12 + R-P0-2）**：tone 一维 ×N≈400 真实双编码者盲标 → 真 Cohen κ/Krippendorff α（61_human_samples + 09_sentiment_verify 框架已就绪、**效标效度=文章级、tone 框=`61_human_samples` 的 1000 篇随机批（创新维语料为约 1125 篇 `21_tone_llms_full`，勿混 · F-c）、不受 T=2 约束**）。**⚠ 二分（R3-03）：本次提交（T=2 现盘）交付 = G0 的 κ 计算代码 + 单元测试 + 反锚定盲表生成脚本（使人工标注**得以开始**）；真 κ **数值**阻塞于「真人编码者填 400 格」的组织/劳动步骤（非代码 deferred）。「非 deferred」= 盲标流程现盘即可启动、不受 T=2 panel 约束，不暗示本次提交即产出 κ 数值。** **G0 仅证明「deferred-解锁链路可跑通」，对 substance/locus/collab 任一创新维零效度支持**（criterion validity per-construct：tone κ 对三创新维零外推）。
- **G1（collab 效标效度 Panel G）**：63 阶段补 Panel G，与 E/F 完全对称（机器三轨预测 vs 3 编码者人工金标准）。
- **G2（locus + collab 判别效度）**：泛化 73，三创新维各自对**词汇对照轴**（clarity/num_intensity）的**裸相关判别旁证**（F11：单 indicator 不称 HTMT）+ 三维彼此 **heterotrait-monomethod 裸相关块**（F11：非 heteromethod）；**主判别证据明确改挂既有 stage 72 NMI 正交性**（对离散构念标签合法、非退化）。
- **G3（collab **编码者间** schema · M2 精确化）**：`R_COLUMNS_BY_RATER` 补 collab 键 + 抽样脚本补 `stage3c_collab`。**范围 = 仅补 collab 的编码者间 reliability schema，不含三轨 κ**（collab 三轨 κ 已由 stage 71 覆盖，见 §2.3 注⁶）。
- **G4（信度稳健升级）**：innovation 三维效标补 **Gwet AC1**（偏态患病率，破 κ 悖论）+ κ 的 **bootstrap 95% CI（sample-conditional + population-weighted 双报）**。
- **G5（反锚定盲标回填协议 · F1/F12）**：交付**双文件盲标协议**（编码者表零 LLM 标签 + 对账表后解锁）+ 抽样设计 + 功效论证（修正后）+ IRR 预注册阈值 + 仲裁。真标注=deferred-生产（G0 的 tone 先行除外）。
- **G6（论文承诺对齐）**：locus/collab `paper_spec.yaml` 加 `validation:` 块，标 `commitment_status: new_2026-06-22` + `evidence_status: pending_T18_human_annotation`。validation schema 单一事实源 = 本计划字段（**无任何现存 spec 有 validation 块可对齐**，F18）。
- **G7（coverage 效度三分归位 · F17）**：如实记述 coverage 三件**不同**的事——(i) coverage 构念 face/content validity（Fang-Peress 关键词法 + verification semi-join 门控披露）；(ii) `dict_coverage` Wilson CI = 金科**词典**召回审计（Sautner 2023，**工具效度非 coverage 构念效度**）；(iii) Panel A verification = 真伪 criterion validity（门控 coverage）。三者不混为「coverage 效度轨」。

### per-dimension 效度声明门（F12 + R-P0-2；R3-01 定性：文档约定 + 可执行 spec 层回归，**非 CI 强制谓词**）
- **per-dimension 约定**：每篇 paper_spec 的 `validity_claim_gate` 绑定**该论文自身主测度维度**（tone spec 绑 tone / substance 绑 substance / …），字段 `requires_real_human_kappa_for: <dimension>`（**YAML 声明，非可执行谓词**）。**某维回填真 κ 仅解锁该维论文声称，对其余维零外推**。
- 未达本维门 → 正文/摘要**不得断言该维 criterion validity**，**不得断言该维 construct validity 已建立（established / 构念效度成立）**；**可如实报告 stage72 同源 NMI 非冗余判别诊断结果**（须标 within-single-LLM-method / machine-machine，**非 established construct validity**，且配 R3-04 正向句），不得据 NMI 外推为该维构念效度已建立。保留占位句 `measurement validity pending human gold standard for <dimension>`。⚠（F-b）此处「construct validity」加「已建立」限定 = 与下方可执行黑名单 `construct validity established`/`构念效度成立` 逐字一致（criterion 仍裸禁）；判别效度 ⊆ 构念效度，NMI 诊断可报但不等于构念效度已建立。
- **可机械执行的护栏（R3-01，把门从纸面变 T=2 可跑）**：新增 `tests/integration/test_validity_claim_gate_consistency.py`，复用既有 `paper_registry.get_spec`/`load_all_specs`：
  - 对每篇 spec，读 `validation.evidence_status`（无块/字段则 `pytest.skip(reason=...)`，**显式可见非永真**）；
  - 若 == `pending_T18_human_annotation`：断言该 spec 全部自由文本声称字段（现盘存在的 `differentiation_claim` 等）规范化后**不含**越权短语集 {`criterion validity`, `construct validity established`, `validated against human`, `效标效度(已建立)`, `构念效度成立`}（允许 `pending`/`machine-machine reliability`/`LLM-assisted`）；
  - per-dim 锚：断言 `validity_claim_gate.requires_real_human_kappa_for` == spec 主测度维度（防 tone κ 越权解锁三创新维）；
  - manuscript 守卫**条件激活**：该 paper 目录出现 `*.tex`/`manuscript*.md` 时才把同一黑名单扫正文 + 断言「manuscript 存在 ⟹ evidence_status != pending」；缺席则 skip-with-reason（杜绝护栏本身静默漂移）。
- 这是 eval 层 per-dim `innovation_pending_reason` dict（F23）与 manuscript 层声称权限之间**唯一真实代码连接点**（落实 §G6 的「同 dim 键空间」承诺）。

**中间态可声称模板（R3-05，给作者直接引用，证明非死锁）**：某维真 κ 回填前，该维论文**仍可投**，按下表诚实表述：

| 维度（真 κ 前） | ✅ 可声称（现盘真值） | ⏳ 须占位（pending） | ✋ 禁止 |
|------|------|------|------|
| tone | 三轨 reliability（stage71 κ）+ dict/BERT/LLM 收敛（stage64） | 机器-人工 criterion（待 G0） | — |
| substance/locus/collab | 三轨 reliability（stage71 κ）+ 同源 NMI 非冗余**诊断**†（stage72，描述性·受单次调用混淆限制）+ 机器-机器分类一致性 | 机器-人工 criterion validity | 跨维背书（「tone 验证故三维亦可信」）/ **声称 construct validity 已建立** / 声称做过 heteromethod 判别 |

> † **此为 within-single-LLM-method 同源非冗余诊断（非 heteromethod 判别效度，非 established construct validity），受 per-dim 门约束（F-b）**；表述须配 R3-04 正向句**且必须同时披露「无 heteromethod 判别证据」缺位（F-g）**——「弱但合法」作复合主张整体陈述，不得简写成「构念效度成立」，亦不得只写禁列项而漏披露缺位+配对句。

### 非目标（铁律）
- ✋ 不触 stage 21 / 不改 prompt v8 / 不删 `_llm_cache.db`。
- ✋ 不把 coverage 改成 LLM。
- ✋ 不向 40/51 panel 新增列（全落 validation 层 → golden 零重生 / $0）。
- ✋ 不新增 DAG 阶段（STAGES_VALIDATION 计数 16 不变）。⚠（F-e）新增 `tests/integration/test_validity_claim_gate_consistency.py` 为纯 pytest 文件，**非 DAG 阶段/非 shim，不计入 STAGES_VALIDATION=16 与 shim=35 计数**。
- ✋ 不混三轨进同一 over-identified Hansen J。
- ✋ **test-retest（同 prompt 温度重抽样）= N/A**（prompt v8 字节冻结 + T=0 + 缓存确定，κ≡1 trivial；Carlson-Burbano 2026 SMJ 主张温度应固定并报告）；非缓存重抽样违 prompt 冻结铁律，不做。**但稳定性威胁不一刀切（R2-P3-1）**：模型版本漂移由 `_llm_cache.db` 哈希 + 模型版本锁作可复现锚（CLAUDE 记录过 panel 176→174 边缘银行漂移），等价 prompt 改写稳定性由 stage 70 prompt_sensitivity 作 test-retest 近似（报其 κ）——不以一句 N/A 抹掉整个稳定性维度（F16）。
- ✋ **不宣称生产结论**（T=2 仅验管道）。

---

## 2. 现状真值盘点

### 2.1 四维 LLM 测度的列（命名例外，WS-B 必硬编码）
| 维度 | 文章级预测列（`21_tone_llms.parquet`，规则） | panel 级聚合列（命名例外） |
|------|---------------------------------------------|---------------------------------------------------|
| tone | `llm_vote_tone_{full,ctx,ss}` | `llm_vote_tone_*` |
| substance | `innovation_substantiveness_{full,ctx,ss}` | `avg_subst_prob_score_{full,ctx,ss}`（规则；**LLM 概率均值**） |
| **locus** | `innovation_locus_{full,ctx,ss}` | ⚠ `tech_frac`(full)/`tech_frac_lc`(ctx)/`tech_frac_ls`(ss) |
| **collab** | `innovation_collab_mode_{full,ctx,ss}` | ⚠ `collab_frac`(full)/`collab_frac_cm`(ctx)/`collab_frac_cm_ss`(ss) |

> **F7 修正**：`manual_validation_sampling.py:60-86` 现用**裸名** `innovation_substantiveness`/`innovation_locus`（无后缀），盘上仅有 `_full/_ctx/_ss` → 现盘即 KeyError。WS-D 须先改读 `_full` 主轨 + loud 守卫（独立于 T=2/T=19 的先决 bug）。
> **F11 修正**：substance 用 prob 均值、locus/collab 用 frac 份额 = 测度口径异质，HTMT/相关绝对值不可横向比较，须披露（或统一用 sub_frac/symb_frac，但破旧测试契约，暂不）。
> **F9 修正**：`40_panel_yearly.parquet` **当前缺盘**；盘上实为 `51_panel_with_controls.parquet`（172 行，已含全部 6 个命名例外列 + 对照轴列）。WS-0/验收门按此订正。

### 2.2 人工金标准基础设施
| schema | 文件 | 编码者 | 维度 | 数据状态 |
|--------|------|--------|------|----------|
| 双编码者 | `llms_human.py` | A/B | verification + sentiment(tone) | 1000 行人工列**全空** |
| 3 编码者 | `manual_validation_schema.py::R_COLUMNS_BY_RATER`（仅 2 键） | R1/R2/R3 | substance + locus | xlsx **不在盘** |
| — | 无 | — | **collab：完全无 schema** | 无 |

### 2.3 验证阶段对**四维 LLM 测度**覆盖矩阵（coverage 列仅门控参照，非 LLM 维 · R-P1-1）
| 效度类型 | 阶段·文件 | coverage⁰ | tone | substance | locus | collab |
|----------|----------|:---:|:---:|:---:|:---:|:---:|
| 效标效度（机器 vs 人工，**文章级**） | 63 `llms_evaluation.py` | △门控¹ | ✅ B-D + 64 | ✅ E | ✅ F | ❌ **(G1)** |
| 判别效度（同源 LLM 非冗余正交，**非 heteromethod**²） | 72(NMI承重) + 73(裸相关辅) | — | (对照轴) | ✅ | ◐ 72✅/73待G2 | ◐ 72✅/73待G2 |
| 三轨 κ（机器-机器，stage 71） | 71 `inter_track_kappa.py` | — | ✅ | ✅ | ✅ | ✅⁶（**自 v3.4.0 已覆盖 collab**） |
| 编码者间 reliability（stage 63 α） | 63(α) | ✅ | ✅ | ◐ schema 在·数据空 | ◐ schema 在·数据空 | ❌ schema 缺 **(G3)** |
| 收敛效度（多机理趋同） | 64 `tone_validation.py` | — | ✅ dict/BERT/LLM | —³ | **—³(非 kw)** | —³ |
| 构念正交 NMI | 72 `construct_orthogonality.py` | — | — | ✅ | ✅ | ✅ |
| 稳健·三轨/prompt（=LLM 的 test-retest 操作化⁴） | 71 + 70 prompt_sensitivity | — | ✅ | ✅ | ✅ | ✅ |
| predictive/nomological⁵ | (§10 outcome 轨) | — | — | →§10 | →§10 | →§10 |

> **图例（F-a）**：✅=现盘代码路径已建；◐=部分已建（子证据 ✅ / 另一子证据待对应 Gn）；❌=未建（待对应 Gn）；△=门控参照非主体；—=构念性不适用。
> ⁶ **M2 订正（前三轮漏判）**：stage 71 自 v3.4.0 起**已对 `innovation_collab_mode` 三轨算 Cohen κ**（`inter_track_kappa.py:79` 阈值 0.45 / `:314` 读三轨列 / 9 行 3维×3pair）。v3.1 把"机器-机器三轨 κ"与"编码者间 α"混一格、整行对 collab 标 ❌ 是误判——**collab 三轨 κ 已做，只有编码者间 α 真缺**。故 **G3 范围精确化 = 仅补 collab 的编码者间 schema + `stage3c_collab` 抽样列，不含三轨 κ**。substance/locus 编码者间 α 是 schema 在但 R 列全 NaN→`status=pending`，故 ◐ 非无保留 ✅。

> ⁰ **coverage 非 LLM 维（R-P1-1）**：coverage 是 Aho-Corasick 关键词计数（`attention_media.py:458`），**不同构念、不同效度范式**，刻意不入四维 LLM 矩阵主体，列于此仅为门控参照（△）。
> ¹ **coverage 三分（F17）**：△门控 = Panel A verification 真伪二分类（**样本门控审计，非 coverage 测度本身的 criterion validity**）；coverage 构念本身效度 = Fang-Peress 关键词法 face/content validity + semi-join 门控披露；`dict_coverage`=词典工具效度（Sautner 2023），**不是 coverage 构念效度**，三者锚点不可互换。
> ² **判别效度 = 同源 LLM 标注器内部构念非冗余正交检验，非 heteromethod 判别效度（F11/F-驳2 + R-P0-1）**：stage 72 对离散创新标签算 NMI（Bagozzi-Yi 1988 构念冗余检验，对 monomethod 合法、非退化），检验三维彼此是否携带独立信息。**关键披露**：三创新维结构上 LLM-only、无方法独立第二测度，故 **Campbell-Fiske heteromethod 判别效度本质缺位**，论文如实披露（不得宣称已做 heteromethod 判别）。**⚠ 方向性诚实降级（R4-EIC-F1）**：三创新维由**单次 LLM 调用、单个 JSON、共享思维链**（`innovation_*_reason` 前置）**条件解码**（`unified_cot.txt` v8），这是比经典 monomethod 更强的 within-response 共依赖。单次条件生成可使离链关联**向任一方向**偏移（共享潜在判断可抬高；而条件解码的互斥倾向——如判 symbolic 后偏 application——可机械压低离链 MI），**偏移符号不可识别**。故 NMI 近 permutation null 是与非冗余**一致的证据（evidence consistent with）**，**而非对非冗余的干净检验（not a clean test）**；判别证据等级从「保守支持」降为「**描述性、受单次调用混淆限制（descriptive, single-call-confound-limited）**」。论文 Appendix 须显式写入此局限（审稿人必问"近零 NMI 是真可区分还是单次响应切分伪迹"）。73 的 panel 裸相关因单 indicator 退化为 |corr|，更弱辅助旁证。**实测**（substance×collab：NMI=0.004 / panel|corr|=0.040）；72 的 `'strong'`=强正交=好（非重叠）；locus×collab 单向 'weak' 须带「近零区 NMI 有限样本偏差方向不稳，双向取严判仍非冗余」caveat（R4-P2-02，防裸读为判别失败）。paper_spec 标 `evidence_type: within_single_LLM_method_nonredundancy, confound_sign_unidentified`。**干净检验须 separate-call 探针（§9 deferred-付费，非现盘 $0）**。
> ³ **收敛效度构念性不对称（F10）**：substance/locus/collab 均 LLM-only，**无方法独立的第二测量机理**。locus 的 `canonicalize_topic` 消费的是 **LLM 自产 fintech_topic**（非原文），且词表与 prompt locus 维高度重叠 → **不构成独立第二机理**（撤 v1「locus 例外」）。三维收敛效度构念性不适用，论文如实披露。
>
> **⚠ 修订注（WP-R3, 2026-07-14）**：本条"三维收敛效度构念性不适用"的适用前提已被 `PROMPT_ASSETS_AUDIT_EXECUTION_PLAN_2026-07-12.md` §10 WP-R3「创新维度三角化」改变 —— WP-R3 为 substance/locus/collab 各构造了一条**方法学独立**的 $0 proxy 测度（正则投入信号 / Gomber 词表二分 AC 自动机 / 协作动词×实体共现，零 LLM），与 LLM 标签、（未来 WP-R2）人工标签三边互证（human-LLM / human-proxy / LLM-proxy 三角闭环），而非再造一个"更准的"同方法测量。这不是撤销本条判断（三维**仍然结构上 LLM-only、无第二独立机理承担 criterion 角色**），而是**在收敛效度之外新增一条并行的三角化证据链**：LLM-proxy 边当前 $0 可算（本轮 dry-run 实测 collab Spearman ρ≈0.57、locus/subst 近零，弱相关不构成 LLM 测量失败的证据，只构成"proxy 精度天花板"的披露，见 WP-R3 §3 预登记弱边定位规则）；human 边待 WP-R2 收口后补齐。论文如实披露口径不变，但可补一句"另辅以独立于 LLM 的 proxy 测度三角化，见 WP-R3"。实现: `scripts/audit/innovation_proxy_triangulation.py` + `config/fintech_locus_split.yaml`；gate: `tests/test_wpr3_locus_split.py`。
> ⁴ **test-retest=N/A（F16）**：LLM 标注器的 test-retest 操作化 = prompt 扰动稳健性（stage 70/71，四维已覆盖）+ 编码者间 κ/α；经典「同 prompt 温度重抽样」在 prompt v8 冻结 + T=0 + 缓存下退化为 κ≡1 trivial，故不做且不违铁律。
> ⁵ **predictive/nomological（F16）**：创新维测度预测理论 outcome（collab→m_and_a_fintech / locus→citation_weighted_patent）属 §10 outcome 轨（对齐 memory `bipolar-anchor-bank-topics-plan-2026-06-22` 银行财务面板采集），非本测度效度核心。

### 2.4 闭环现状
- substance/locus：闭环已在（63），仅缺数据 + F7 抽样脚本裸名 bug。
- collab：**criterion-validity 闭环（stage 63）不存在**（须建 schema + Panel G）；但**机器-机器三轨 κ 闭环（stage 71）已在**（M2，含 collab），缺的是编码者间 α + Panel G 人工金标准。
- tone：双闭环已在（63 双编码者 + 64 单编码者，且 **64 的 `09_sentiment_verify{track}.xlsx` 已是窗口级金标准**——编码者读轨特定窗口文本，F13 对 tone 不成立）。
- **gold-construct 错配（F13）**：innovation 三维的人工金标准按**全文**判，而 ctx/ss 测**窗口** → 机器-人工 κ 在 ctx/ss 轨是 [模型误差 + 窗口-全文构念漂移] 的**混合下界**。
- **窗口 gold 同源循环（R-P1-3，新增）**：F13 的「deferred 窗口级金标准」（给编码者下发 content_ctx/ss 窗口文本）**不能简单视为"消除"混合下界**——窗口由上游 entity-cooccurrence 规则**预切**，编码者与 LLM 读**同一预切窗口** → 窗口 κ 只度量「人机对同一预切窗口的共同反应」，**不验证窗口切得对不对**；若窗口误切（漏相关句/纳误导句），人机同向出错 → κ 虚高、窗口保真度被掩盖（与 R-P0-1 同源高估同构）。故：**全文 gold 永为 criterion 主轨**；窗口 κ 降为「窗口解读一致性」**辅助诊断**（标不可作 criterion 主张、不可跨轨比较）；**窗口切分保真度抽成独立前置审计**（复用既有 `ctx_is_fallback`/`ss_is_fallback` 标志 + 抽检「相关句是否落入窗口」），与 κ 分列不互相掩盖。

---

## 3. 关键设计决策（锁定）

| 决策 | **锁定** | 理由 / R1 修正 |
|------|:---:|------|
| collab 效标效度 | **扩 63 加 Panel G** | golden-safe；零计数变更。**F8：Panel G 是第 2 个 tabular 内的子表头，tabular 计数保持 2，非新开第 3 个** |
| locus/collab 判别效度 | **泛化 73** | 文件名「lexical」指对照轴（仍准确）。**F6：非「轻量加循环」——`focal_label` 参数化 + κ 函数泛化 = 中等函数体重构。⚠ 仅 substance 走定向 κ**（focal frac 阈值 0.5 二分 + clarity median 二分，有 W&Z 理论符号锚）；**locus/collab 取消定向 κ（R-P1-2）：`direction=None` → 不对 frac 做任何二分、不产 κ，只报无向 \|corr\|/ρ**（与 WS-B/测试/checklist 一致；判别承重证据=stage 72 NMI） |
| 判别效度术语 | **降级（F11）** | 单 indicator |corr| 不称 HTMT；删单 item AVE 判定（≡1 永真）；跨构念块称「heterotrait-monomethod 裸相关」非「MTMM heteromethod」；主证挂 stage 72 NMI |
| 人工标注 | **双文件盲标（F1）** | 编码者表零 LLM 标签；v7ref 入独立对账表，编码完成后解锁 |
| 不动 72 / 不改 panel 列 | 维持 | 72 已是合法 NMI 正交主证；panel 列动则破 golden |
| 不新建阶段 | 维持 | 全扩现有 validation，STAGES_VALIDATION=16 不变 |

---

## 4. 工作流（WS-0 … WS-H）

### WS-0 前置硬门
1. worktree off origin/main + by-name add（禁 `git add -A`；与并行脏文件零交集）。
2. 备份 `data/processed/eval_reports/` + `manual_validation_*` → `_validity_backup_20260622/`（F25/P3-2：烟雾跑前确认已备份，跑后 diff DEMO 产物仅结构变化非数据污染）。
3. **列就位核对（订正文件名 F9）**：`21_tone_llms.parquet` 含 `innovation_collab_mode_{full,ctx,ss}`；panel 用 `51_panel_with_controls.parquet`（含 6 命名例外列 + 对照轴；`40_panel_yearly.parquet` 当前缺盘）。
4. **docid 硬门（F24）**：核对 `manual_validation_sampling.py` 输出含 `docid`（与 `21_tone_llms.parquet` 同口径），否则全 innovation 维 schema-mismatch pending。

### WS-A（collab 效标效度 Panel G） [$0/golden-safe]
- ★`manual_validation_schema.py:18-29`：`R_COLUMNS_BY_RATER` 加键。**⚠ 两命名空间（R-V2-1 订正，禁混）**：
  - (a) **维度键 = 裸名**：`R_COLUMNS_BY_RATER` 键 + `_INNOV_LABEL_CODE` 键 = `'collab'`（对齐 `substantiveness`/`locus`）。
  - (b) **task/pred/metrics = 带 `innovation_` 前缀**：task_name + classifier_metrics 键 + pred 列前缀 = `innovation_collab_mode`（`_mode` 是 `tone_llms.py:2179-2181` 真实落盘列名，**不可删**；误裸名 `collab_full` → `:960` `pred_col not in columns` → 静默全 skip，Panel G 永空）。
  - 回归锁：pred col 与 tone_llms 落盘列名逐字一致（含 `_mode`），防 `.replace` swap。
- ★`:34-44`：`_RATER_VALUE_TO_CANONICAL_LABEL_RAW` 加 `{self_developed→自主研发, collaborative→外部协同, 中文透传}`。
- `llms_evaluation.py`：
  - **pending 两层（F23 + impl-V1 订正；R6-P1-2 精确 schema）**：**全局 pending**（文件缺 `:832`/读失败 `:846`/无 docid join `:924/:940`）= 保留顶层 `results['innovation_pending_reason']` str（全维同时失效，**向后兼容不变**，护 `test_join_falls_back_to_orig_index` 等 ≥10 处 flat 键断言）；**单维 pending** = 新增 `results['innovation_pending_by_dim'] = {dim: reason_str_or_None}`（dim ∈ {`substantiveness`,`locus`,`collab`}，值=`'file not present'`/`'schema mismatch'`/`'n=0'`/`None`）。**规则**：全局失效时顶层 str 置该 reason、`by_dim` 三键同置该 reason；某维独立缺（如 collab R 列缺/该维 n_gold==0）时顶层 str 保持 `None`、仅 `by_dim['collab']` 置 reason、其余维续跑。Panel E/F/G 各读 `by_dim[dim]`。`test_collab_dimension_optional_pending` 断言 collab 缺列时 `innovation_pending_reason is None and innovation_pending_by_dim['collab']=='schema mismatch'`。`validity_claim_gate` 测试与此同 dim 键空间。⚠ **`:853` 全局 schema 门（V-01）**：`all_r_cols` 保持只含 subst+locus 作核心两维全局 mismatch 门，**禁把 collab 拼进 `:853` 的全局 missing 检查**（否则现有只供 subst+locus 的 fixture 触发全局早退 → E/F/G 全 pending 破 per-dim 语义）；collab 缺走单维 `n_gold==0` 软 pending。回归锁 = `test_collab_dimension_optional_pending`（collab 缺列时断言 `innovation_pending_reason is None` 且仅 collab dim 标 pending）。
  - `:865-872` 加 `gold_collab = apply(merge_three_rater_majority, R_COLUMNS_BY_RATER['collab'])`。
  - `:883-910` `_INNOV_LABEL_CODE` 加 `'collab':{'自主研发':0,'外部协同':1}` + 循环加该 dim（α 入**独立键** `innovation_inter_coder_reliability`，**勿破 2 键不变量** R27B-02）。
  - `:951-955` 元组列表加 `('innovation_collab_mode','gold_collab','innovation_collab_mode{track}',['自主研发','外部协同'])`（前缀名）。
  - **criterion κ（F3，当前 `compute_classification_metrics` 不算 κ）**：在 `:972` 后并行算 **sample-conditional κ**（复用 `compute_cohens_kappa`，零成本）**+ population-weighted 混淆矩阵 κ_w**（WS-C `compute_cohens_kappa_weighted`，复用 `:978-988` 已校验 `_w_valid` 守卫防负权/全零/NaN）两键 + **Gwet AC1（WS-C）** + bootstrap CI；复用 accuracy_note 同款 stratum-conditional 标注。⚠ **R6-P2-2**：直接喂 `y_true/y_pred` 的中文 str array（`compute_cohens_kappa`/`compute_gwet_ac1`/`compute_cohens_kappa_weighted` 内部 `sorted(set(...))` 统一编码），**勿额外 `_INNOV_LABEL_CODE` 转换**（那是给 ICR α 用的）；三者类别索引顺序一致。⚠ **R6-P2-1**：collab gold 用 `df_mv.apply(merge_three_rater_majority, ...['collab'])`（依赖其 `row.get` 容错，collab 缺列时返全 None→软 pending），**勿改 `df_mv[...]` 直索引**（会 KeyError）。
  - **F13 + R-P1-3 披露**：innovation Panel E/F/G 的 ctx/ss 指标强制附挂 `GOLD_CONSTRUCT_DISCLOSURE`（现仅 tone 路径附），标「**全文 gold 下的混合下界**，不可跨轨比较测度优劣；窗口 κ（若回填）仅『窗口解读一致性』辅助诊断、非 criterion」。
  - **locus hybrid 不可比 caveat（R4-EIC-F3）**：Panel F（locus）的机器端标签含 `canonicalize_topic` 关键词置信度调整 + 空票回退（吃 LLM 自产 fintech_topic），**criterion/判别 κ 继承 substance/collab 没有的关键词循环 → locus 效度数值不与纯 LLM 维直接可比**，须在 Panel F 脚注 + `paper_spec` 披露。可选：locus criterion **同时算纯 LLM 多数票版 vs hybrid 版**以 bound 关键词贡献（$0/golden-safe，直答"locus 效度是 LLM 的还是关键词表的"）。
  - `:1565-1571` `classifier_metrics` 加 `'innovation_collab_mode':{}`。
  - **Panel G 渲染（F8）+ Gomber 引文勘误（V-02）**：在**现第 2 个 tabular 内**（`:685` `\end{tabular}` 之前；`:683` 是数据行收尾）镜像 Panel F 加 Panel G 子表头「Innovation Collaboration Mode (binary, Chesbrough 2003 / Laursen-Salter 2006)」，pending 复用 per-dim 语义，demo 走 `_demo_marked_path`。⚠ 顺手订正 Panel F 表头 `:668` 的 `Gomber 2018 JMIS` → `Gomber-Koch-Siering 2017 JBE`（memory `comments-docs-audit-2026-06-19` 已记此引文勘误；golden-safe，仅 .tex 字符串）。
- **测试**：`test_63_evaluation.py` — schema coupling 加 `stage3c_collab` token + 往返断言；**`_rater_row` 签名扩为 `_rater_row(sub_vals, locus_vals, collab_vals=None)`（R6-P1-1：`collab_vals=None` 时跳过 `R{i}_stage3c_collab` 列注入，护现有 ~10 处 2-arg 调用向后兼容）**；`test_panels_E_F_in_separate_tabular` **保持 `tabular==2`**（F8），加 `assert 'Panel G' in tex` + Panel-G-rendered 断言 + `test_collab_dimension_optional_pending`（collab 缺列仅 G pending，E/F 仍跑）+ `test_panel_G_collab_present_with_gold`（fixture `_rater_row(...,collab_vals=[...])` 用 collab 取值字符串，断言 gold_collab 非全 None）+ 断言 `innovation_inter_coder_reliability` 恰 3 子键。

### WS-B（locus + collab 判别效度，泛化 73） [$0/golden-safe，中等重构]
- ★`lexical_discriminant_validity.py:103-109`：平行字典（**硬编码命名例外** F-R2）：`LOCUS_INDICATORS={full:'tech_frac',ctx:'tech_frac_lc',ss:'tech_frac_ls'}`；`COLLAB_INDICATORS={full:'collab_frac',ctx:'collab_frac_cm',ss:'collab_frac_cm_ss'}`；对照轴共用。
- **κ 子路径泛化（F6 + R-P1-2 订正；R6-P2-3/P2-4 精确化）**：`run_discriminant_validity` 加 `focal_label` 参数（默认 `'T1_substance'` 向后兼容）；`compute_cohen_kappa_substance_vs_clarity` 泛化为 `compute_cohen_kappa_focal_vs_clarity(focal,clarity,focal_threshold,direction)`，**`direction: Optional[str]`**——substance 传非 None（如 `'positive'`，走现有硬编码方向锁 `c_bin=(c<median)`），**`direction=None` ⟹ 跳过 κ 计算、返回 dict 干脆省略 κ 键**（非含 NaN κ）。保留旧名 `compute_cohen_kappa_substance_vs_clarity` 作 substance 薄封装（默认 `direction='positive'`/`focal_threshold=0.5`），不破 `test_73` ~6 个默认调用契约。⚠ **R6-P2-4 返回键冻结**：substance 轨返回 dict **保留 `cohen_kappa_substance_clarity`/`spearman_substance_clarity` 旧键名字面**（M7 schema 锁断言"逐字一致"的基线）；locus/collab 轨返回 dict **不含** `cohen_kappa_*` 键、含 `abs_corr_*`/`spearman_*` 键。
- **术语降级（F11）**：dim-suffixed 产物不称 HTMT，称「构念间 |Pearson r|/Spearman ρ（单 indicator，无衰减校正）」；HRS 2015 从「采用 HTMT 准则」弱化为「沿用其 0.85/0.90 经验阈值作旁证」；删/弱化单 item Fornell-Larcker（√AVE≡1 永真，仅作完整性记录）。
- **判别证据架构澄清（R-P1-2 + F11/F-R2）**：**locus/collab 判别效度的承重证据 = stage 72 三创新维 NMI 互正交**（理论锚：W&Z/Gomber/Chesbrough 三构念预期互不冗余，§2.3 注²，对离散标签合法非退化）；**73 的 vs 词汇对照轴对 locus/collab 仅证「不与无关词汇测度共线」，非构念间判别主张**（弱「非冗余」旁证）。substance 的 vs-clarity 有理论（实质 vs 可读性），保留其定向 κ。
- **跨构念块（F11）**：三创新维 panel 列两两 |corr| 称「**heterotrait-monomethod** 裸相关块」（非 heteromethod；Campbell-Fiske 1959 降为概念锚），披露「三 frac 列共享 stage21 LLM 方法方差，低相关仅弱『非冗余』旁证」；**复用 `_safe_corrcoef` + min-N≥10 守卫**（F20），退化标 `insufficient_obs` + T=2 披露。
- **stage 72/74 分工交叉引用（F15）**：72=三创新维 article 级 NMI 互正交（判别承重）；73=LLM 创新构念 vs 词汇对照轴（弱旁证）；74=LM 6 子词典 vs 同对照轴。焦点构念族不相交，clarity/num_intensity 共用同列名 + 同 `_apply_llm_valid_mask` → 数值一致无冲突。
- **常量轴守卫**：substance 定向 κ 的 `min==max` 真常量返 NaN（F-驳1：守卫仅真常量触发，偏态有变异并报 Gwet AC1，互斥域不冲突）。
- **输出文件名三映射（F22 + R-V2-5）**：substance 兼容名 = `73_htmt_matrix.json` + `73_lexical_discriminant_{track}`；locus/collab 新名 = `73_discriminant_{dim}_{track}`；同步更新 `schemas.py:181` 注释；验收门加「注释与实际产物名一致」检查。
- **下游旧号顺修（M5，zero-marginal-cost）**：本计划既改这套 73 机理，顺手把 `codebook.py:1013` notes 的 `(stage 39d)` → `(stage 73)` 且 `HTMT` → `判别效度旁证`（与 F11 术语降级一致，否则自相矛盾）；`bank_fintech_substance/21_substance_clarity_robustness.do.tmpl` 5 处 `39d`→`73` 从「pre-existing 待顺修」升为本计划顺修（同一改动面）。golden-safe（codebook xlsx 不进 golden）。
- **测试**：`test_73_*` 加 locus/collab dim 产物 + **命名例外六列字面硬断言**（防 `.replace` swap，**R-2 唯一真护栏**，F9）+ 跨构念块存在 + min-N 守卫 + locus/collab `direction=None` 不产 κ 断言 + **substance 路径返回 dict 键集与泛化前逐字一致（含 κ 键）/ locus/collab 路径不含 κ 键含 |corr|/ρ 键（M7 返回 schema 锁）**。

### WS-C（信度稳健升级：Gwet AC1 + 加权 bootstrap κ CI） [$0/golden-safe]
- **Gwet AC1 公式锁定（R4-P2-04，防误抄 κ 的 p_e）**：`llms_evaluation.py` 新增 `compute_gwet_ac1(r1,r2)`（Gwet 2008 BJMSP 61:29）。**AC1 = (p_o − p_e^AC1)/(1 − p_e^AC1)**，其 chance-agreement **p_e^AC1 = (1/(q−1))·Σ_k π_k(1−π_k)**（q=类别数，π_k=两评者平均边际比例）；二分类闭式 **p_e^AC1 = 2π(1−π)**，π=(p1_marginal+p2_marginal)/2。⚠ 与 Cohen κ 的 p_e=Σπ_k² **不同**（误抄会静默出错数，且"完全一致=1"测不出区别）。
- **population-weighted κ 算子锁定（R4-P1-01，三轮盲点，须给公式否则无法落地）**：现 `compute_cohens_kappa` 只对**未加权**计数矩阵算 p_o/p_e，`population_weight` 现仅入 accuracy（`:978-998` 标量加权，**非混淆矩阵加权**）。定义加权混淆矩阵 **C_w[i,j]=Σ_{n: y_true=i,y_pred=j} w_n**，**p_o=Σ_k C_w[k,k]/Σw**，p_e 用**加权边际** (Σ_j C_w[k,j])(Σ_i C_w[i,k])/(Σw)²；κ_w=(p_o−p_e)/(1−p_e)。这是 Manski-Lerman 后分层**外推**口径。
- **双报 + 双轨 CI（F3）**：innovation E/F/G 同报 **sample-conditional κ（未加权，诊断分类器判别力）+ population-weighted κ_w（外推总体）+ Gwet AC1（偏态稳健）+ Krippendorff α**。CI：诊断走 `_compute_kappa_with_bootstrap` 均匀重抽；**外推走加权 bootstrap**（按 w 归一化概率重抽行，每个 bootstrap 样本重算 C_w 的 κ_w）。
- **三者正交分列勿混（F3）**：Gwet AC1 解 κ 悖论（偏态边际高一致低 κ，sample-conditional）；population-weighted κ_w 解抽样过采样外推（Manski-Lerman）；二者**正交**，不互相替代。
- **测试**：`compute_gwet_ac1`——除「完全一致=1」外，**加一个偏态固定混淆矩阵（如 90/5/5/0）手算 AC1 vs κ 断言**（验 AC1>κ 且=手算值，否则区分不出误抄 κ 公式）。`compute_cohens_kappa_weighted`——**全 w=1 时必须逐位等于现有 `compute_cohens_kappa`**（向后兼容锚）。

### WS-D（反锚定盲标回填协议 + 抽样脚本） [$0 代码 / deferred 真标注]
- **F7 先决修复（impl-V5：现盘即崩，修复面比 v2 写的更宽）**：`manual_validation_sampling.py` 裸名 `innovation_substantiveness`/`innovation_locus` → `_full` 主轨，**修复面含 `:60-62` value_counts + `:65-86` 共 4 处 2×2 分层布尔判据**（非仅 :60）；缺列 `SystemExit` 列出现有 `innovation_*` 列 + 回归锁。标注「此 bug 现盘即 KeyError、是先决阻断、与 docid 门/双文件协议解耦」。
- **F1 双文件盲标（核心）**：抽样脚本输出**两个文件**——(a) **coder-facing 盲表**（仅 `orig_index/docid/标题/内容/stratum/population_weight` + 空白 R1/R2/R3 标注列，**零 LLM 输出**）；(b) **reconciliation 对账表**（同 `orig_index` 主键，含全部 `v7ref_*` LLM 预测），**仅在三编码者标注完成 + 共识冻结后解锁对账**。新加 collab 的 v7ref 同样只进对账表。
- ★`:136-150`：rater 循环加 `{rater}_stage3c_collab`(self_developed/collaborative) + `_conf` + `_rationale`。
- **窗口金标准 = 替换非消除（F13 + R-P1-3 订正）**：**全文 gold 永为 criterion 主轨**（manual_validation_samples.xlsx 携标题+正文全文）。deferred 窗口 gold（盲表 `metadata_cols` 追加 `content_ctx`/`content_ss`，各轨下发「仅基于该轨窗口判标签」，镜像 `tone_validation.py:653-669`）**仅产「窗口解读一致性」辅助诊断 κ**——标「人机对同一**预切**窗口的共同反应，不验证窗口切得对不对（与 R-P0-1 同源高估同构）；不可作 criterion 主张、不可跨轨比较」。删一切「消除混合下界」绝对化措辞。
- **窗口切分保真度 = 独立前置审计（R-P1-3）**：复用既有 `ctx_is_fallback`/`ss_is_fallback` 标志落零成本诊断（各轨 fallback 率 + 抽检「相关句是否落入窗口」），与窗口 κ **分列不互掩**；全文 gold κ 在 fallback 行上的额外漂移即窗口保真信号。
- **抽样分层**：保持 5 层（A_not_relevant + substance×locus 2×2）；**collab 不进分层**（8 格 T=2 枯竭）。**F21 加纯随机层**（10–20%，不按任何 LLM 标签）以无偏估计 LLM 漏判率（分层抽样按 LLM 标签定义 frame 无法估漏判）。
- **★编码者上岗流程：pilot + 资格门（M1，顶刊 IRR 硬要求，前置于正式批）**：(1) **编码手册冻结**（四维定义+边界判例+中文锚词，版本戳；冻结后只走仲裁不改手册，防 manual 漂移污染 IRR）；(2) **pilot 子集**：从盲表随机抽 30–50 篇（双重少数类格 C/D/E 各保证 ≥3–5 篇），标 `is_pilot=True`，**不计入正式 400/500、不进 criterion κ 分母**（防数据复用），零 LLM 标签；(3) **资格门**：pilot 双/三标 → pilot κ/AC1（偏态维 AC1 主裁），< 预注册门（建议 κ≥0.55/AC1≥0.60，略宽于正式）→ **编码者间 reconcile + 二次培训 + 重抽新 pilot**，循环至达标才解锁正式批。⚠ pilot 门（处理**系统性误校准**=重训）与 IRR-after 第三轮仲裁（处理**孤立单格分歧**=逐格）**正交互补**。pilot κ 不进 manuscript criterion 主张。tone 的 G0 先行同样须先过 tone 单维 pilot 门。
- **IRR 预注册阈值**：Krippendorff α ≥ 0.80 / Cohen κ ≥ 0.61（Landis-Koch；**偏态维以 Gwet AC1 为主裁、κ 阈值参考**）；低于阈值触发第三轮仲裁。预注册写入协议。
- **纯随机层最小 N（R4-P2-05）**：纯随机层（10–20%）估 LLM 漏判率，但 N≈400 下抽 40–80 篇纯随机、命中真少数类漏判可能个位数 → 漏判 CI 宽到无信息。**协议显式标**：纯随机层在 T=2/N≈400 仅作 face-validity 哨兵，漏判率点估计**不附推断 CI**，真值 deferred-T18 全样本（与 §5 少数类 N<60 口径一致）。
- **伦理/数据治理（M6）**：语料=公开新闻二手数据 + 编码者=受训研究助理 → 多数辖区属免 IRB/最小风险，给一句立场声明（或标"投稿前按目标刊补伦理审查"）；编码者身份去标识（R1/R2/R3 代号）；`manual_validation_samples.xlsx` 纳入 `_validity_backup_/` 版本备份语义。
- **F25 tone 抽样框 reconcile**：tone 沿用独立 1000 篇随机批（61_human_samples，**注意 tone 框=1000 行非语料 1125**）；**协议如实声明「四维统一」指编码指南统一，抽样框不强求统一**。
- **deferred 生产（须用户拍板）**：① **先过 pilot 资格门** → T=19 重生 `21_tone_llms_full.parquet` 后生成两文件；② 3 编码者盲标 + tone 双编码者填 61/09；③ merge 共识 gold → 重跑 63/64；④ 重跑 73。**例外：G0 的 tone 一维 ×N≈400 真 κ 提为非 deferred（现盘可启动，但仍须先过 tone pilot 门）**。

### WS-E（论文承诺对齐） [$0/doc]
- locus/collab `paper_spec.yaml` 加 `validation:` 块（字段 SSOT = 本计划 G6：`criterion_validity`/`discriminant_validity`/`inter_track_reliability` + `commitment_status: new_2026-06-22` + `evidence_status: pending_T18_human_annotation`）；tone/substance spec 交叉引用同一矩阵（**无现存 validation 块可对齐**，F18）。
- **per-dimension `validity_claim_gate`（R-P0-2）**：每篇 spec 绑 `requires_real_human_kappa_for[this_dimension]`（非全局 ≥1）；某维真 κ 仅解锁该维论文。
- **discriminant evidence_type 字段（R-P0-1）**：locus/collab `discriminant_validity` 标 `evidence_type: within_single_LLM_method_nonredundancy(non_heteromethod)`，与 tone 的 stage64 `cross_method_convergent` 区分，防读者当同级。
- **F18 deferred 复现包**：真数据回填后镜像 `bank_fintech_substance/21_substance_clarity_robustness.do.tmpl:63-68` 的 display，在 `19_locus_clarity_robustness.do.tmpl`/`20_collab_clarity_robustness.do.tmpl` 末尾加读 73 产物的 display 行（就地加 display 不新建 .do → **Stata 模板数保持 142**）。
- **防误填（F2 + R-V2-3 按指标类型设禁）**：paper_spec criterion_validity 块**不得把 accuracy 的 Wilson 半宽（≈0.045，本身正确）冒充为 κ/α 的 CI 半宽**；κ/α 半宽须用 §5 重算值（焦点维 0.089–0.102）。即按「指标类型」设禁，非按数值 0.045 一刀切。

### WS-F（coverage 三分 + face/content + known-groups + 三轨稳定性 + codebook） [$0/doc]
- coverage 效度三分（G7/F17）写入 codebook + 计划，锚点不互换；coverage 构念 face validity 锚明确限定为 **Fang-Peress 2009 extensive-margin 报道判定**，与 intensity 加权（若含）的 **Hassan 2019** 锚分列一句（R4-P3-06），避免单锚外推到加权口径。
- **face/content validity（M3，现盘可做、不依赖人工 κ）**：为 substance/locus/collab 各补一段——(1) 引 `unified_cot.txt` v8 三维标签定义文本；(2) 显式映射到 **W&Z 实质/象征 · Gomber-KS 底层/应用 · Chesbrough 自研/协同** 的理论二分；(3) 标注 content coverage（prompt 是否枚举了构念关键面向）；(4) 可选 1–2 名领域专家对 prompt-构念映射打 face-validity 评分。**为 deferred 的 criterion 提供"即便人工 κ 未回填、构念定义本身可辩护"的前置支撑**，直答审稿人"你怎么知道 prompt 测的就是 Chesbrough 的协同"。
- **known-groups validity（M4，不依赖人工 κ）**：用一小组"已知高金科参与"银行（年报/公开新闻硬编码）vs 对照，对三创新维 panel 列做组间均值差异 + 效应量（Cohen d / Cliff δ），T=2 退化时 min-N 守卫 + insufficient_obs 披露（同 73 口径），**标探索性**。若外部分组获取超范围，则在矩阵注脚**显式声明 known-groups deferred 并给理由**（勿让审稿人发现该标准缺席却无交代）。
- **窗口保真审计严格化（R4-EIC-F4，二选一勿留占位）**：R-P1-3 的"窗口保真前置审计"**要么** (a) 给与正式标注同等严格度——抽样框 + ≥2 独立编码者在**原文全文上**判"相关句是否落入窗口"（不看 LLM/窗口决策）+ IRR 阈值 + fallback 率×误切率表；**要么** (b) 明确降级为纯 `ctx/ss_is_fallback` 率描述性披露，**删一切"验证窗口正确性"措辞**。禁止把未规约的抽检当成能破同源循环的方法学控制。
- **F14 披露 substance full_ss κ=0.368**（<0.45，passes_threshold=False）为窗口敏感性偏高信号，在 substance 论文(P3)作 measurement-stability caveat，**禁以三轨高均值掩盖单轨对失败**。

### WS-G（收敛效度——降级/收窄） [$0/golden-safe，可选]
- **locus（F10）**：撤「canonicalize_topic 是第二机理」；**重命名为 hybrid 内部一致性诊断（非收敛效度）**，仅 exploratory 附录 + 显式循环风险，计算**排除空票回退行**，不进效度矩阵主体。
- **substance/collab（F25/P3-1）**：若做轻量关键词锚分类器作第二机理，**词表须落 validation 局部常量**（不进 config/、不被任何 panel 列消费、产物只进 eval_reports/，标 `[$0/golden-safe/validation-only]`，且锚词表**读原文非读 LLM 输出**）；或直接留空并披露 LLM-only 构念无第二独立机理（更干净，与 §2.3 注³ 一致）。
>
> **⚠ 修订注（WP-R3, 2026-07-14，词表落位条款）**：本条"词表须落 validation 局部常量（不进 config/）"的隔离意图，在 `PROMPT_ASSETS_AUDIT_EXECUTION_PLAN_2026-07-12.md` §10 WP-R3 的 locus 二分表实现中做了**受控例外**：`config/fintech_locus_split.yaml` 二分表是**双人独立编码 + 第三方仲裁**的持久化产物（含 Cohen's κ=0.8375 与双编码原始表存档），需要版本化与跨会话持久存档，落 `validation/` 局部常量（模块级 Python 变量）不适合承载这类可审计、可复现的编码产物。故改为**落 `config/` YAML + 以 gate 测试断言替代"不进 config/"的隔离意图**：`tests/test_wpr3_locus_split.py::TestConsumerScopeIsolation` 全仓 grep 断言零 `pipeline/`/`papers/` import（仅 `scripts/audit/innovation_proxy_triangulation.py` 消费），效果等价于原隔离意图（生产代码零消费、面板列零污染），但载体从"physically 不进 config/ 目录"改为"逻辑上零生产 import + gate 强制"。substance/collab 两维仍按本条原方案处理（proxy regex/动词表落 `scripts/audit/innovation_proxy_triangulation.py` 模块级常量, 非 `config/`, 不适用本例外）。

### WS-H（终审门） [gate]

---

## 5. 样本量功效表（修正版 · F2/F3/F5/F21）

> **F2 修正**：v1 的 0.045 是误把比例 p̂ 的 Wilson 半宽 `1.96·√(0.7·0.3/N)` 当成 κ 半宽。κ 方差含 p_e 项，偏态下放大。下表用 Fleiss-Cohen-Everitt(1969) 渐近 SE + bootstrap MC 双路复核（逐点吻合），构造对称边际使 κ=0.70。

| 维度 | 估计量 | 类别数 | 有效 N | 预期患病率 | **κ/α CI 半宽（真值）** | 少数类 recall CI（F21） | 偏态主裁 |
|------|------|:---:|:---:|:---:|:---:|:---:|:---:|
| coverage/verification | Cohen κ | 2 | 500 | ~0.70 | **0.068**（非 0.040） | — | — |
| tone/sentiment | Krippendorff α（并报多分类 κ） | 3 | ~400 | 三分类 | **≈0.05–0.07** | per-class | — |
| substance | Cohen κ | 2 | ~400 | 偏态 0.15–0.20 | **0.089–0.102**（非 0.045） | 少数类 N<60→宽 | **Gwet AC1** |
| locus | Cohen κ | 2 | ~400 | 偏态 0.15–0.20 | **0.089–0.102** | 同上 | **Gwet AC1** |
| collab | Cohen κ | 2 | 同批+stage3c | 偏态（待 T=19 实测，无分层保证 F-M7） | **>0.10 可能**（无过采样保障） | 须 T=19 定 | **Gwet AC1** |

- **family 列（F4 FWER）**：判别效度全维一族 / 效标效度全维一族；**确证=full 轨**（纳入主 FWER，Holm/Romano-Wolf step-down），**探索=ctx/ss 轨**（不计入主张）。HTMT 描述性 cutoff 豁免，permutation 显著性 + κ 显著性须纳入。
- **结论（修正 F2 + R-V2-4 统一区间）**：删除「半宽<0.05 / 远优于 0.10 / 无需上调」。**主精度指标 = accuracy 的 Wilson CI（≈0.045，本就正确）+ Gwet AC1（偏态稳健）**；**κ 半宽权威区间以本表为准：平衡维(coverage,p≈0.70)≈0.068、偏态焦点维(substance/locus,p≈0.15–0.20)≈0.089–0.102**（更宽的 0.07–0.12 是全患病率 0.10–0.50 扫描的外包络，仅作上下界参考），偏态焦点维已触及而非远优于 0.10。若坚持 κ 半宽<0.05，须上调 `PER_STRATUM`（现 100，SSOT `manual_validation_sampling.py:35-37`）使焦点维有效 N≈1000–1500（受 T=2/T=19 少数类可得性约束）。
- **0.040 来历（R-V2-3）**：v1 coverage 行旧值 0.040 = 误把比例 p̂=0.7 在 N=500 的 Wilson 半宽当 κ 半宽；真值 0.068（N=500/p=0.70，κ 方差含 p_e 项故大于比例半宽）。表中「0.068（非 0.040）」即此订正，0.040 不再作任何主张。
- **F3**：所报 κ 须标 sample-conditional / population-weighted；population_weight 只纠偏点估计、不缩小 CI。
- **F21**：少数类 N<阈值（如 60）则该维只报描述性一致率 + Gwet AC1，不报推断性 κ-CI。
- **偏态维样本量绑定决策（R4-EIC-F5，不留"也许上调"悬念）**：substance/locus/collab **预注册二选一**（投稿前锁定，避免被读成"验证设计成注定不确定"）：**(a)** 目标 N（用计划已设想的少数类过采样）达 κ CI 半宽 **<0.075**；或 **(b)** a-priori 声明三维 criterion 一律**只报 Gwet AC1 + 描述性一致率（不报推断 κ-CI）**，且此为已注册、被接受的精度上限。**纯随机层最小 N**（R4-P2-05）：N≈400 下抽 40–80 篇纯随机命中真少数类漏判可能个位数 → 漏判 CI 无信息 → 协议标"T=2/N≈400 仅作 face-validity 哨兵，漏判率不附推断 CI，真值 deferred-T18"。
- 内嵌复核脚本（Fleiss-Cohen-Everitt 渐近 + bootstrap MC 双路）+ 锚 Donner-Eliasziw(1992) Stat Med 11:1511 的 κ 样本量表（**F-P2-1：该表恰证偏态下需远大于 400 的 N，引用方向已修正**）。锚点：Bujang-Baharum(2017)；Sim-Wright(2005) Phys Ther 85:257；Gwet(2008) BJMSP 61:29。

---

## 6. 风险与回滚
| # | 风险 | 缓解 |
|---|------|------|
| **R-0（最高，F1）** | circular/anchored gold standard：编码者见 LLM 标签 → κ 虚高 | **双文件**：coder-facing 盲表零 LLM 标签 + 对账表后解锁；预注册「标注阶段无任何 LLM 标签可见」；隔离机制写入协议 + checklist |
| **R-0b（R-P1-3）** | 窗口 gold 同源循环：人机同读预切窗口 → 窗口 κ 虚高、保真度被掩盖 | 全文 gold 为 criterion 主轨；窗口 κ 降辅助诊断；窗口保真度独立前置审计（ctx/ss_is_fallback） |
| R-1 | collab R 列缺 → E/F/G 全 pending | per-dim optional（pending str→dict） |
| R-2 | locus/collab ctx/ss 列名朴素 swap → 静默全 NaN | **硬编码** indicators + **单元测试六列字面断言（唯一真护栏，非烟雾，F9）** |
| R-3 | 破 `inter_coder_reliability` 2 键不变量 | collab 信度入 `innovation_inter_coder_reliability` |
| R-4（F8 订正） | ~~tabular==2→3~~ | **保持 tabular 计数 2**；Panel G 是第 2 tabular 内子表头；测试改子表头存在性断言 |
| R-5 | 偏态恒常轴 vacuous κ=0 | `min==max` 真常量返 NaN + 并报 Gwet AC1（互斥域，F-驳1） |
| R-6 | panel 列新增 → golden 重生 | 铁律：全 validation 层零 panel 列 |
| R-7 | 误带并行脏文件 | worktree off origin/main + by-name add |
| R-8（F7） | 抽样脚本裸列名 KeyError | 改 `_full` + loud 守卫 + 回归锁 |
| R-9（F2） | 伪功效数写进协议/paper_spec | §5 重算 + WS-E 防误填 |

回滚：每 WS 独立提交 + 备份；validation 层零 golden 足迹。

---

## 7. 验收门（全绿才算完成）
1. `ruff check .` clean。
2. `test_panel_reproducibility` — **零变化**（全 validation 层）。
3. `test_dag_consistency` — STAGES_VALIDATION **仍 16**；shim 仍 35。
4. `test_63_evaluation` + `test_71` + 新增（Panel G / Gwet / 73-泛化 / collab-optional / 命名例外硬断言）全绿；**`tabular==2` 不变**（F8）。
5. **R-2 护栏 = 单元测试（强制，不依赖盘面 panel，F9）**：`test_73_*` 含 `LOCUS_INDICATORS`/`COLLAB_INDICATORS` 六个字面列名硬断言。离线烟雾走**合成 panel fixture**（含 tech_frac*/collab_frac*/对照轴列）正向断言三维非全 NaN；**不依赖 40_panel（缺盘）**。⚠ **生产 stage 73 `main():465` 仍读 `40_panel_yearly.parquet`（其设计上游，T=19 重生后补盘，勿改成 51）；51_panel/合成 fixture 仅供 WS-B 单元/烟雾**（impl-V6）。
6. `test_papers_b_route.py::test_total_template_count` — Stata 模板**仍 142**。
7. `schemas.py:181` EXPECTED_NO_OUTPUT_STAGES 注释与实际 73 产物名一致（F22）。
8. grep 确认降级后文档不再无保留称单 indicator |corr| 为 HTMT/MTMM（F11）。
9. 多智能体 R2 复审 GO / 0 must-fix。

---

## 8. 铁律 checklist（提交前逐项）
- [ ] thin shim 冻结；DAG 计数不变（MAIN=16/VALIDATION=16/shim=35/REGISTRY=16）。
- [ ] 全改动落 validation 层 → golden **零重生**。
- [ ] 不触 stage 21 / prompt v8 / `_llm_cache.db`。
- [ ] **R-0 反锚定**：coder-facing 盲表零 LLM 标签；v7ref 仅入对账表后解锁（F1）。
- [ ] locus/collab panel 列名**硬编码** + 单元测试字面断言（F9/R-2）。
- [ ] `inter_coder_reliability` 2 键不变量；innovation 信度走独立键 3 子键。
- [ ] `R_COLUMNS_BY_RATER` ↔ 抽样脚本列名往返一致；键名 4 处 token 自洽（F19）。
- [ ] Panel G 在第 2 tabular 内子表头，tabular 计数保持 2（F8）。
- [ ] §5 功效数为重算真值（非比例 Wilson 半宽）；κ 标 sample-conditional/population-weighted（F2/F3）。
- [ ] **FWER**：family 定义 + Holm/rwolf；确证=full、探索=ctx/ss；HTMT cutoff 豁免、permutation+κ 显著性纳入（F4）。
- [ ] 单 indicator |corr| 不称 HTMT；删单 item AVE 判定；主判别证据挂 stage 72 NMI（F11）。
- [ ] locus 收敛效度=hybrid 一致性诊断（非收敛），排空票回退行（F10）。
- [ ] innovation ctx/ss 效标附 `GOLD_CONSTRUCT_DISCLOSURE`（混合下界，不跨轨比较）（F13）。
- [ ] inter-track κ 表 `passes_threshold=False` 行逐条披露（禁均值掩盖，substance full_ss=0.368）（F14）。
- [ ] **per-dimension `validity_claim_gate`**：每维 criterion/construct validity 声称须有**该维**真 κ；**禁任何「已对 tone 验证故三维亦可信」的跨维背书**（F12 + R-P0-2）。
- [ ] 窗口 gold κ 仅作「窗口解读一致性」辅助诊断、非 criterion；窗口保真度独立前置审计，与 κ 分列（R-P1-3）。
- [ ] locus/collab 判别承重证据 = stage 72 NMI；vs 词汇对照轴仅弱旁证；locus/collab 无理论符号锚故不报定向 κ（R-P0-1/R-P1-2）。
- [ ] **每处「无 heteromethod 判别证据」必配对正向句（R3-04，措辞经 R4-EIC-F1 降级）**：「但三创新构念 NMI 互正交（近 permutation null）在 W&Z/Gomber/Chesbrough 理论预期下提供与非冗余**一致的描述性证据**」——⚠ **偏移符号不可识别（单次调用条件解码可双向偏倚），一律标「描述性·confound-limited」，禁回「保守支持/保守方向」**（与 note² L167/§9-7 统一）；「弱但合法」作复合主张整体陈述，缺位句不单独出现（防读成自我否定）。
- [ ] collab 命名两空间：维度键裸 `'collab'`、task/pred/metrics 带 `innovation_collab_mode` 前缀（`_mode` 不可删）（R-V2-1）。
- [ ] 引用四要素核验：HRS 2015 / Campbell-Fiske 1959 / Gwet 2008 / Cohen 1960 / Krippendorff 2018 / Landis-Koch 1977 / Donner-Eliasziw 1992 / Carlson-Burbano 2026 / Fang-Peress 2009 / Sautner 2023 / W&Z / Gomber / Chesbrough。
- [ ] worktree off origin/main + by-name add。
- [ ] 建 memory + CLAUDE.md 追加一行。

---

## 9. 生产 T=19 待办（deferred）
1. **[非 deferred 例外 · G0]** tone 一维 ×N≈400 真实双编码者**盲标**（先过 tone pilot 资格门 → 效标=文章级、tone 框=61_human_samples 1000 篇、现盘可启动、不受 T=2 约束）+ 重跑 64 → 真 κ/α；**仅解除 tone 论文的 `validity_claim_gate`，不解除 substance/locus/collab 任一维**（R-P0-2）。
2. **[deferred-必做]** T=19 重生 `21_tone_llms_full.parquet`（先修 F7 抽样脚本裸名）→ 生成 coder-facing 盲表 + 对账表（带 docid + content_ctx/ss）→ 3 编码者盲标 substance/locus/collab → 重跑 63 → 真 criterion + IRR。
3. **[deferred-必做]** 重跑 73（真 panel）→ 三维判别效度真值 + 与 72 NMI 对账。
4. **[deferred-可选]** collab 少数类 T=19 定向过采样（无分层保障，F-M7）。
5. **[deferred-可选]** WS-E 镜像 clarity 模板的判别 display 落复现包（模板数保持 142）。
6. **[独立轨，显式排除 F25-M10]** locus/collab 论文 provisional→fully-coded 升级（需 outcome 财务面板：locus `citation_weighted_patent` / collab `m_and_a_fintech`）= 独立 onboarding，**非本测度效度计划范围**，对齐 memory `bipolar-anchor-bank-topics-plan-2026-06-22`（银行面板现全 sentinel）。
7. **[deferred-付费·M0·R4-EIC-F1]** **separate-call NMI 干净检验**：另起独立单维 label-only prompt（新 `prompt_version`，**不复用 v8 缓存键** → 必 cache MISS ≈ 1125文×3模型×1维 付费 API，受 M0 gate），无共享 CoT，实证近零离链 NMI 在**去单次调用混淆后是否复现**。复现 → 非冗余主张获干净支持；不复现 → 暴露单次调用 NMI 受混淆。**现盘不执行**（破 $0/golden 铁律 + 触付费）；落地前现盘披露一律用「描述性·confound-limited」不回「保守支持」。

---

## 附：MVP 垂直切片
1. **WS-0**（备份 + 列就位 51_panel + docid 门 + F7 抽样脚本裸名修复）。
2. **WS-C**（Gwet AC1 + 加权 bootstrap κ CI，独立单元可测）。
3. **WS-A**（collab schema 键名统一 + Panel G 第 2 tabular 子表头 + per-dim pending dict + criterion κ 双报 + GOLD_CONSTRUCT 披露 + 测试）。
4. **WS-B**（focal_label 泛化 73 + 命名例外硬编码单元断言 + 术语降级 + 跨构念 monomethod 块 + min-N 守卫 + 72/74 交叉引用）。
5. 过验收门 1-8 → 补 WS-D 双文件盲标/WS-E/WS-F/WS-G 文档层 → WS-H。
6. **G0 tone 先行真 κ**（现盘可启动，非 deferred）；其余真标注 deferred 拍板。

---

> **审计轨迹（三轮对抗审计收敛）**：v1.0 → **R1**（6 视角 31-agent + 每条 P0/P1 二次核验）→ v2.0（14 must-fix + 11 should-fix）→ **R2**（4 视角 11-agent：must-fix 全 P3 确认 + 新抓 per-dim 门/窗口循环/命名空间回归）→ v3.0 → **R3**（3 视角 5-agent：R2 收口确认 **GO** + 新鲜怀疑者 GO_WITH_FIXES + R3-07 逐条直读复证 8 项 load-bearing 代码主张全属实）→ v3.1（收 V3-1/R3-01/1170→1125/framing）。
> **驳回的 6 条误读**（核验后不改）：F-驳1 Gwet/NaN 互斥域；F-驳2 NMI 'strong'=正交被读反；R-P1-1 coverage 非第4个 LLM 维（已分离）；R-P0-3 效标文章级非 T=2 空转；R3 毒舌 P0-1 NMI 自证（实为合法保守证据）；R3 毒舌 P0-3 全 T=2（混淆文章/panel 级）。
> **R4 终审（5 视角 10-agent，对当前 v3.1 全文 + R3 后 8 处未审编辑）**：可实现性逐行复证 = **GO**（每条 file:line / 磁盘主张独立证实，"高质量、真正可实施"）。抓 5 个前三轮盲点（已收口 v3.2）：① population-weighted κ / Gwet AC1 **无公式**（P1-01/P2-04，三轮共同盲点，已补加权混淆矩阵 + AC1 闭式 + 区分性单测）；② per-dim 门"construct validity" vs 中间态模板"NMI 判别"措辞冲突（F-b，已对齐"established"形）；③ 缺 **pilot 试标/编码者资格门**（M1，顶刊 IRR 硬要求，已补）；④ §2.3 矩阵把 collab 三轨 κ 误标缺失（M2，stage71 实已覆盖，已拆行）；⑤ 单次调用同 JSON 出三标签 → NMI"保守"是断言非证明（EIC-F1，已诚实降级为"描述性·confound-limited" + separate-call 干净检验入 §9 deferred-付费）。另补 face/content + known-groups 效度（现盘可做）、伦理治理、tone 框 1000 订正。
> **当前状态：四轮（R1/R2/R3/R4）后零 P0/P1 未决；工程实施 GO。** 剩余 P3 cosmetic（Carlson future-date / 行号 ±1~2，已加"实读为准"免责）。**⚠ 重申：工程 GO ≠ 论文发表就绪**（须先跑 G0-tone 真 κ + 处理 EIC-F1 单次调用混淆，见顶部两个「GO」勿混）。

> **审计轨迹**：v1.0 → R1（31-agent）→ R2（11）→ R3（5）→ R4（10）= 四轮 57-agent 对抗审计，每条 P0/P1 派第二智能体反驳核验，累计驳回误读 ≥8 条（防假阳当真）。R4 可实现性视角逐行复证全部代码主张属实 = 计划真正可据以实施。
