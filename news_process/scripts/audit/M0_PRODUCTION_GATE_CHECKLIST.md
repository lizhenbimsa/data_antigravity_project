# M0 生产总闸检查单 (M0 PRODUCTION GATE CHECKLIST)

**版本**: v1.0 (2026-07-14) | **母计划**: `PROMPT_ASSETS_AUDIT_EXECUTION_PLAN_2026-07-12.md` §10 WP-R5
**创建缘由**: 全仓 33 个 audit 计划文件引用"M0 审批门"作为生产 T=18 付费重跑/播种前置, 但此前从未有一份实体文件承载该门的具体核查内容——`DEFERRED_ITEMS_COMPLETION_2026-06-20.md:62` 指向的 memory 条目 (`paper_portfolio_decision_gates`) 已不存在, 各计划各自复述"过 M0 门"却无统一清单, 存在"门存在但核查标准漂移"的风险。**本文档是 M0 门唯一实体文件**——任何计划写"过 M0 门"时应指向本文档, 而非重新复述门槛内容。
**批准人**: 一切本文档下的付费/不可逆动作, 批准人 = 用户本人, 唯一; 任何 agent 的评审结论仅供决策参考, 不构成批准。
**预注册载体**: 本文档入 git 的首次提交时间戳为预注册时点; 此后任何阈值/规则修改须新 commit 并在 §5 变更日志登记, **不得**在看到生产结果后回溯放宽判定规则。

---

## §1 T=18 生产稳健性判决总表 (robustness verdicts at T=18)

**总纲**: `prompt_sensitivity`（措辞敏感性）/ `radius`（上下文半径敏感性）/ **人工 κ**（情感 + 创新三维效标效度）/ **proxy 三角化**（创新三维构造效度）四件套, 在 T=18 生产语料上**必须**留有明确记录——或是生产重跑结果, 或是"为何 T=2 结果在此维度上仍有效"的可核查论证 (仅限 §2 A/B 类, 见下)。**本条不满足于写一条原则**, 逐项核查动作如下表, 每项动作 = 一条可执行命令 + 一个通过/不通过判据:

| # | 四件套项 | T=2 现状 | T=18 核查动作 (可执行) | 通过判据 |
|---|----------|----------|------------------------|----------|
| 1 | `prompt_sensitivity`（措辞敏感性，⊇S9+D8，母计划 WP-R1） | `validation/eval_reports/prompt_sensitivity_results.json` 现 `passed=False`（dev 语料, 变体自身有缺陷污染）| ① 生产重跑后检查 `eval_reports/prompt_sensitivity_results_<run_id>.json` 是否含 `sample_scope="T18_production"` 或等价字段; ② `grep -rn "prompt.*sensitiv\|措辞敏感" papers_assets/*/drafts/{zh,en}/manuscript.tex papers_assets/*/manuscript_{zh,en}.md` 逐条核对手稿中引用的样本口径句是否标注 T=18（而非沿用 dev 数字或笼统"稳健"表述） | 有 T=18 结果 json + 手稿引用句与之口径一致；如仍未重跑，手稿必须写"pilot, not evidential"（§2 C 类披露语） |
| 2 | `radius`（上下文半径敏感性，⊇D7，母计划 WP-R4） | `validation/radius_sensitivity_llm.py` 从未真跑（scaffold） | 同上模式：① 生产 9,000 请求跑批后检查 eval_reports 产物是否标 T=18 语料 id; ② `grep -rn "radius.*sensitiv\|半径敏感" papers_assets/*/drafts/{zh,en}/manuscript.tex papers_assets/*/manuscript_{zh,en}.md` | 同上 |
| 3 | 人工 κ（情感 M3 + 创新三维 MVP-0622，母计划 WP-R2） | 盲表零人工填写；κ=0 | ① 检查 `manual_validation_samples.xlsx` 是否存在且非零填写行；② `grep -rn "Cohen|Krippendorff|kappa|κ" papers_assets/*/drafts/{zh,en}/manuscript.tex papers_assets/*/manuscript_{zh,en}.md` 核对手稿引用的 κ/α 数值是否来自 T=18 人工标注批次（而非 dev pilot 批次） | 三块报告（门控κ/三维agreement/漏检率）齐备且样本量达 §10 WP-R2.3 预登记地板 |
| 4 | proxy 三角化（创新三维构造效度，母计划 WP-R3） | 三 proxy 构造脚本可 $0 先行，但收口依赖 WP-R2 人工标签 | ① 检查 `scripts/audit/innovation_proxy_triangulation.py` 产物 eval_reports 是否含三边（human-LLM/human-proxy/LLM-proxy）报告；② `grep -rn "proxy\|三角化\|triangulat" papers_assets/*/drafts/{zh,en}/manuscript.tex papers_assets/*/manuscript_{zh,en}.md` | 三角闭环三边齐备且弱边定位规则已按预登记应用 |

**核查动作的落地要求**: 上表第②列 grep 命令必须**实际跑一遍**并把命中行贴入 §5 变更日志（而非凭记忆勾选）；手稿中任何"结果对 prompt 措辞稳健"/"半径选择不影响结论"一类表述，若引用的是 T=2 dev 数字，视为**未过闸**，须改写为 §2 C 类披露语或删除该表述。

---

## §2 证据三分类 (替代一刀切"T=2 结果一律无效"禁令)

**动机**: 并非所有 T=2 结果都因样本量小而失效——工程不变量与数学恒等在任何样本量下都成立；只有**统计效度结论**（依赖样本分布、随机性、显著性/信度阈值）才需要 T=18 验证。三分类如下, 所有引用 T=2 结果的手稿/文档句子必须显式标注所属类别：

- **A 类 = 工程不变量 / 构造性结论**：代码路径正确性、位级等价（bitwise equality）、schema parity、fail-loud 逻辑、EOL/编码免疫、缓存键构造正确性等——**T=2 上验证即永久有效**, 不因语料规模扩大而改变（除非代码本身变动）。引用时标注 **"code-invariant, sample-size-independent"**。
- **B 类 = 数学恒等 / 退化论证**：如 dev T=2 上某网络指标零方差属数学必然退化（非 bug）、罕见词分位数在冻结词典上退化等——**豁免 T=18 要求但标注推导依据**, 引用时标注 **"degenerate-by-construction at T=2; expected to differ at T=18"**。
- **C 类 = 统计效度结论**：κ / α / φ（相关系数）/ 标签翻转率 / 聚合相关 / 任何"稳健"/"不稳健"判定——**必须 T=18**, T=2 结果在手稿中只能以 **"pilot, not evidential"** 措辞出现, 不得省略此限定语单独引用数值。§1 四件套全部落 C 类, 无例外。

**标注规范**：任何文档（手稿 `\parencite`/脚注、`eval_reports/*.json` 的 `note` 字段、`AI_DISCLOSURE_TEMPLATES.md` 披露段）引用 T=2 阶段产出的量化结果时, 必须在同句或紧邻脚注内写明所属类别（A/B/C 三选一）及对应措辞；C 类结果缺失该限定语视为披露不合规, 须补写而非删除数值。

---

## §3 选择性报告纪律 (代替 FWER，回应"多重比较"质疑)

**为何不进 rwolf 族错误率家族**：Romano–Wolf (`rwolf`) 保护的是"同一构念的多个 headline 处理效应估计"这一**确证性假设检验族**（如跨模型系数、跨规格系数）。κ / φ / 标签翻转率 / 聚合相关是**信度系数**（reliability coefficients）, 心理测量学惯例中无"拒绝域"对象——它们的报告规范是描述性统计 + 置信区间, 而非假设检验意义上的显著性判定, 因此**不适用**、也**不应**并入 rwolf 家族（这不是遗漏, 是范畴不匹配, 强行并入反而制造虚假的统计严谨性外观）。

**真正的多重性风险 = 网格挑格子报告 (grid cherry-picking)**：四件套中每一项都是"多变体 × 多维度 × 多轨"的网格设计（如 prompt_sensitivity 的 4 变体 × 3 轨 × 7 指标），若只报告"过线"的格子、隐藏未过线格子, 会制造虚假稳健性印象。纪律如下（三条, 均须在付费重跑**之前**以 commit 形式锁定, 呼应母计划 §10 WP-R1.3/WP-R4.3 预登记协议）：

1. **预登记网格逐格披露**：全部格子（含 NaN/失败格及失败原因）必须出现在报告中, 不得只报过线格; 论文正文可摘要, 但完整网格必须在附录/data appendix 或 replication 包中可查。
2. **Pass/Fail 聚合规则先锁定**：判定"是否稳健"的聚合规则（如"7 项 criteria 全过"）必须在付费重跑**之前**以 commit 锁定, 事后不得因结果不理想而放宽或收紧规则。
3. **事后剔格须独立理由**：若某网格单元事后被排除在主报告之外, 排除理由必须独立于该单元的结果本身（如"该维度 verified 样本量结构性不足"是可接受理由, "该格 κ 太低不好看"不是）, 理由须记入 §5 变更日志或对应 eval_reports 的 `exclusion_reason` 字段。

---

## §4 既有挂账收口清单 (跨计划挂账，本 M0 门内兑现)

以下四项挂账已散落在各处文档/CLAUDE.md, 在此汇总为 M0 门下的统一收口清单——**批次 E（生产 T=18 付费窗口）实际执行时必须逐项走过并打勾**, 不得遗漏：

1. **M2 遗留：28 个 jsonl 的 Zenodo 增补 deposit**（母计划 §1-M2）——`data/llm_archive/manifest.json` 重登记后, `responses/` 目录内除已冻结的 5 个文件外, 另有 28 个 jsonl 未被 Zenodo 冻结包（10.5281/zenodo.20453766）覆盖; 需以增补版本化 deposit 方式补登。**⚠ 与 §11 G-v9-4 的 Zenodo 版本化 deposit 不是同一笔**——后者仅覆盖 v9 新增归档, 此处 28 文件是 v8 阶段既有挂账, 禁双重认领。
2. **批次 E 两笔独立付费**（母计划 §5 批次 E / §10 WP-R1.6 / §11 G-v9-3）：① WP-R1 措辞敏感性 v8 生产重跑变体库 ≈36,000 请求（S9 修字必须先于此播种完成，见母计划 §10 WP-R1.1）；② WP-R4 上下文半径敏感性 ≈9,000 请求。**两笔预算独立、各自过 M0、禁合并认领**——尤其禁止以"v9 反正要重跑"为由跳过 v8 这一笔（母计划 §11 G-v9-3 已明确 v8/v9 两笔口径不可混淆，Q-B #7 ② 硬闸的参照集即 v8 生产重跑过线集合，缺此笔则硬闸空转）。
3. **boilerplate `§3-P0` 校准**（CLAUDE.md「boilerplate OOM 硬化」段已挂账）：`df_dict_budget_hard=40M` 是未校准占位值, 生产语料 `global_df` 词表极可能超出该值——T=18 首播前必须先跑 `BOILERPLATE_CHUNKED_TWOPASS_OOM_HARDENING_EXECUTION_PLAN_2026-07-06.md §3-P0` 的 per-entry 字节实测, 按 128GB 内存反推校准硬闸阈值, 否则 Pass1 循环内 `SystemExit` 会连坐 nuke 整批 stage-22（词典 tone 先算完才轮到 boilerplate save, 一旦触发等于整批 stage 21/22 重投）。
4. **stage 21 播种前 >256 批硅基流动限流探针**（CLAUDE.md「嵌入架构」段已挂账）：本机探针仅验证到 n≤256 的批次大小；生产首次播种（Qwen3-Embedding-8B, 硅基流动 API）前必须先验证 >256 的批是否触发限流, 否则生产播种中途限流会造成不可预期的部分失败与缓存不一致。

---

## §5 变更日志

| 日期 | 变更 | 依据 |
|------|------|------|
| 2026-07-14 | v1.0 初版预注册（新建本文件） | `PROMPT_ASSETS_AUDIT_EXECUTION_PLAN_2026-07-12.md` §10 WP-R5 |
