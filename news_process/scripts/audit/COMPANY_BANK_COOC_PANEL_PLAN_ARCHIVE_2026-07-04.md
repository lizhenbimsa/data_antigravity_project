# COMPANY_BANK_COOC_PANEL 执行计划 — 评审史与学术锚点归档 (2026-07-04)

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


> 本文件系 `COMPANY_BANK_COOC_PANEL_EXECUTION_PLAN_2026-07-03.md` (v23) 的 provenance 归档: v23 简化轮 (2026-07-04, 用户令"删减对执行无影响内容") 自主计划整体拆出, **内容零删改、仅搬移**。主计划正文的 "§9.x" / "§10.x" 编号引用指向本文件同编号节 (如 GPSS 2020 = 本文件 §10.9)。对执行零影响; 执行所需全部决策/勘误/义务已在主计划 D1–D17 与 WP0–WP4 正文 (原 §9.10 两条 WP2 义务已前置为主计划 WP2 ⑫d, 原 §9.9 借款表待议已前置为主计划 §6 末条)。学术锚点 150 条 (137 DOI) 以本文件为 codebook/manuscript 引文 SSOT。

## 原头部版本演进段 (主计划 v23 简化前 L3/L4 原文)

**日期**: 2026-07-03 (**v16 评审定稿 2026-07-04**: 四并行代理最高标准评审 (方法/事实/工程/一致性+break-it, 详见 §9) — 修 2×P0 (D4b 子串自共现 / PA 宇宙对齐) + ~20×P1 + 全部文档矛盾; 新增 D4b/D11h/D15⑪/D16。v15: 用户定案全谱单文件 + 首轮审核。v14 终验: 上游六文件开箱 +0 (D11g)。v13: 22/23/25/26 号开箱直检 +4 基名 (D11f) — ⚠ 其"36 个 parquet 全部开箱"陈述系笔误, 该里程碑实际在 v14 达成。v12 收官: 文章级角落末轮复核 (21 号剩余 56 列 / 24 号 herd_decay 459 列 / 聚合缺口探针) — **+5 基名 (D11e)**: 分类三维度**概率连续标度** `avg_{subst,locus,collab}_prob_score` 3 个系 D15 ⑦ `_prob_` 正则**误伤救回** (它们是测度非诊断, 在 40 面板实存) + 自聚合 `avg_mention_density`/`avg_target_mention_count` 2 个 (40 面板无此聚合)。其余确认全覆盖, 检索收敛。v11: 面板外 4 来源 23 基名; v10: 残差第三审 16 族; v9: 全项目 20 族 + WP0 机制; v8: 情感/强度穷尽; v7: 分类三维度; v6: 注册表架构; v5: 加权测度; v4: 只出文件①)

**状态**: **v23 正式版** (2026-07-04) — v15 全谱单文件定案 + v16 四代理评审 (§9.1) + v17 学术锚点 (§9.2/§9.3, §10 共 150 条/137 DOI) + v18 做法审核 (§9.5) + v19 收官终审 (§9.6: 上游定案 21_full) + v20 四路终检 (§9.7) + v21 沙箱干跑轮 (§9.8: gate A 8/8 / 双路径 100% 等价 / WP0 缺口全修) + **v22 增量包定案** (§9.9: S5 三处 vw/mw/hw 失实表述代码级更正 + pair 表 year 钉死与 target_bank 封闭断言两缺口修复 + 三路评审后用户批准**最小增量包**: 面板 +3 `cooc_hhi` / pair 长表 7→10 列 (+frac/frac_v/longhit) / §7 两段披露 / §8 四条防再起 — top1_share/w_auth_sum/权函数全谱臂经实证砍除) + **v23 加权列裁剪定案** (§9.10, 用户 2026-07-04 拍板推翻 v15 "全谱"半边: 研究目的锚定"银行金科及其各维度媒体报道→上市公司影响", 五轮十代理审查后**删 410 加权基名 ×6 = 2,460 列、保留 294 基名** — 判据/救回史/四前提见 **D17**, 权威负清单 = 同目录 `COMPANY_BANK_COOC_PANEL_CUT_LIST_v23.txt`), **待实施** (WP0→WP4); 后续变更只应来自 §9.4 实施回填或主仓上游漂移

## 9. 评审与实施记录 (归档部分; §9.4 实施记录留在主计划)

### 9.1 v16 最高标准评审记录 (2026-07-04, 四并行只读代理 + 主线程裁决)

- **评审配置**: 4 个对抗式只读代理 — ① 数据事实核查 (~40 组主张逐条实跑) / ② 计量方法与口径 (14 findings: 1 P0 + 7 P1 + 6 P2) / ③ 工程与 Stata 约束 (6 项探针实测) / ④ 文档一致性 (22 findings) + break-it (12 边界情况, 多数在 dev 实证)。全程仓库零写入。
- **P0 两项** (已修入正文): ① **D4b 子串自共现** — 17 个公司 variant 是银行名真子串 (牡丹江案例), 不拦截则产 100% 假阳性共现, 升为设计级排除; ② **PA 宇宙对齐** — 16 号 ⊋ 21 号 (+45% docid, 偏移 max≈1.5σ), 自聚合前 semi-join 21 宇宙。
- **主要 P1** (已修): 凸包/单银行断言浮点化 (isclose/N=1 短路); `日期` 实为 object 字符串; 40 面板已漂移 3,308→3,395 (D11h 分诊 +87 列); 16 基名 42 列超 Stata 32 字符且存在截断重名 (D16 缩写规则, 已验证零碰撞); 标签双闸 ≤80 字符且 ≤320 字节 (pyreadstat 不守门, 实测); WP1 宽 join 生产内存陷阱 (分块/稀疏矩阵二选一); 年份越界/NaT/空文本/重复行/零命中等 12 项 fail-loud 处置; D15 正则形态修正 (中置双向匹配 + 白名单 avg/max_bank_count + ⑨b event-time + ⑪ bank-invariant 数据驱动排除, net_*_yr 改判); pyreadstat 实写 release 119 (非 118)。
- **改判两项**: `net_*_yr` 24+ 列纳入→排除 (bank-invariant 零信息); `cross_outlet_tone_variance` 漂移新列→纳入 DA 扩。
- **文档修复**: v13"全部开箱"叙事笔误、DA 错误指针 ②→③、§3 标题 D1–D16、WP4 3→6 文件、v5"21 列"残留、"最长 31 字符"失效主张、D11 表格式化损伤等 22 条全部落地。
- **AC 性能实测锚**: 构建 0.033s; 7.5M chars/s 单核 → 生产 ≈2.1h 纯扫描。

### 9.2 学术锚点核验记录 (2026-07-04)

三源采集 + 双层核验, **零自造**: ① 注册表挖掘 ×2 (A 桶 72 + B 桶 48 条, 逐字摘自仓库 6 份已核验注册表, 核验员复核 **125 DOI + 8 非 DOI 全部逐字在册, 0 转录错误**); ② 网检 ×1 (22 条 2024–2026 新锚, 核验员经 Crossref/DataCite/落地页三对照 **22/22 实体真实**, 抓出 1 处实质错误 — Chen/Kelly/Xiu "RFS 38, 3542–3579" 卷页系张冠李戴 (属另一篇 Xiu 论文), 降级为 SSRN WP 引用; 另修正 4 处: Ge/Li/Zheng 补真实 DOI、Babina JFE 版 DOI/年、EJF 文补作者、Elliott 等补 REStat 刊出 DOI); ③ 注册表真空 (关系型信贷) 由主线程 Crossref 书目检索实取 2 条经典。网检代理另主动排除 2 条 (1 篇 arXiv 撤稿、1 篇作者无法核实)。**§10 全部条目均有"注册表在册"或"Crossref/落地页实证"两种出处之一**。

### 9.3 顶刊终审面板记录 (2026-07-04, v17)

- **终审配置**: 1 个对抗式终审代理 (JF/JFE/RFS 级数据与方法审稿人 + 文献编辑双角色), 机器全量核验 §10 的 136 个 DOI 链接 (合法性 136/136, 零重复) + 三向审查 (文献编辑 8 findings / 计划-文献扣合 5 findings / 整体验收 5 意见)。
- **裁决**: **有条件通过** → 条件已全部落实: F1-1 四条 et al. 补全或按 >20 人规则注记; F1-2 两条年卷经 Crossref 复核修正 (Jacobs & Lauber 2026/EFM 32(2); Li Y. 改 early view 引法); F1-3 Brodeur 改 DOI 链接; F1-7 两条映射收窄 (Gligorić/Zhu); F2-1 §7 增"共现关系类型异质"局限; F2-2 §7 增"LLM 前瞻偏差"局限 (词典/BERT 轨为对照臂 — 本条系 v17 时点历史记录保真; v18 已弱化为"梯度对照臂", 以 §7 现行文本为准); F2-3 Leary-Roberts 改对照锚措辞; F2-4 BHJ 括注补 incomplete-shares; F2-5 §10 加范围声明; R3-1 命中明细长表固定落盘 (frozen-share 臂可重构); R3-2 WP3 加分层 precision 抽样; R3-3 使用要点补 exposure-robust SE + generated-regressor 提醒; R3-4 codebook 示例补推荐样本行。
- **遗留 (非阻断, 投稿前办)**: F1-4 WP 链接格式统一为 DOI 形态; F1-5 Hoberg/Phillips 缩写统一; F1-6 中文文献补英译题名 (英文刊投稿时); F1-8 Lopez-Lira & Tang / Hansen & Kazinnik 复查是否已有刊出版; Menkveld/Brodeur 全作者名单终稿排版。

### 9.5 v18 做法全面审核记录 (2026-07-04, 四并行只读代理)

- **配置**: ① 数据口径与事实基础 (五 parquet schema 实读 + 两份名单全量解析 + encode.py 源码核对) / ② 工程可行性 (依赖/内存/pyreadstat 源码/闸门/性能估算链) / ③ 计量统计 (权重构造/缺失语义/内生性/铁律贯彻/多重检验) / ④ 流程测试纪律 (WP 分解/DAG 边界/git 协议/自一致性 8 处抽查全过)。全程仓库零写入。
- **P0×1 (已修)**: **D4 银行系公司识别缺口** — 42 家 A 股上市银行中 5 家农商行 (常熟/瑞丰/江阴/张家港/青农商行) 两侧名单写法不同 (股票简称 vs 银行全称), variant 零交集且非子串, 同时逃逸 D4/D4b → 自家银行报道记为真共现且 is_bank_company 错置 0, dev 即可复现。修法 = 42 家人工对照表入 registry + WP0 机器覆盖性断言 (D4 v18)。
- **P1×11 (已修)**: BLAS 豁免 3→9 源列 (D11b/§7/WP3 三处同步); PA semi-join 补 WP2 回归锁; fail-loud 路径补负例全覆盖 (WP2 ③); D11h 归因更正 (+87 = BERT 五族 69 + dta-coverage 18, 非 tritrack) + 五族 23 基名全预分诊并继承主仓 caveat (§3b ⑩); D4b "17 个"更正为 "22 个 (13 个不被 D4 覆盖)" 并写明口径; 稀疏/长表公式分子明写 fillna(0)+掩码 (WP1-5); 年份闸拆绝对合法域/用户窗口两层 (D10); "上市前结构零"失实表述更正 (使用要点); per-measure 重归一补 MNAR/common-support 披露 (§3b ⑨); "天然对照臂"弱化为梯度对照臂 (§7); C2 分母 per-model 分写 (§3b ⑦/§7)。
- **P2×16 (已吸收)**: D15 ②→③ 残留指针 / WP4 产物归属 + git 纪律复述 / §5 registry 数据态红灯口径 + WP3 后全量 A/B / §1 cw 展示式分母限定 / "银行层聚类"改 BHJ shock-level / FWER 族界定 (同构念 vs 规格梯子) / frozen-share 复现包附长表 / frac=average-of-ratios 语义 (§3b ⑧) / codebook 逐年语料覆盖表 (真假零判别, D9) / 企业侧自选择披露 (§7) / BHJ 份额和作控制 (D12) / WP1 启动新鲜度断言 (D10) / docid 去重列式化 (WP1-6) / D4b 残余第三方假阳性点名 (§7) / 显式传参缺失升级 SystemExit + 27 号无 paths 键注记 (D10) / encode.py:76 行号复核。
- **刻意不改**: 列数预估各处微差 — 均已标注"以 WP0 落盘为准", §9.4 回填时一次性统一; §9.1 v16 历史记录中的"17 个"原文保真不改, 更正落在 D4b 正文与本节。
- **四路判定**: 数据口径/工程/计量/流程均"**有条件通过**", 无一路 P0 级方案否定; 全部条件已落实于本版 (v18)。工程侧另实证确认: pyahocorasick 双声明在册 (pyproject:44 + lock:119)、pyreadstat 写 release 119 有源码级证据 (`_readstat_writer.pyx:1023`)、`.gitignore:56/92` 双重覆盖产物防误提交、性能估算链自洽且方向保守。

### 9.6 v19 收官终审记录 (2026-07-04, 四并行只读代理二轮 + 高风险事实独立复核)

- **配置**: ① v18 修订落地核验 (§9.5 声称的 28 项逐条 grep 定位 + 旧表述残留全文扫描 + 10 段未修订区误伤抽查) / ② 实施者视角 WP0→WP4 走查 (专攻"写代码会卡住"的规格空白) / ③ 数字断言与 gate 穷尽核算 (全部算术复算 + 盘上可验断言 100% 复现 + dev 假红实证模拟) / ④ 最高风险事实独立二次复核 (**7/7 证实零推翻**, 不沿用前轮结论自行重算)。全程零写入。
- **重大定案 (P1 之首)**: **上游输入 = `21_tone_llms_full.parquet`** — 走查实测 `21_tone_llms.parquet` 写盘前已按 verified 过滤 (全宇宙在 21_full: dev 1,544 = 1,005 True + 539 False, 15 列齐备); 原输入下 D7 双口径永远恒等、`_v` 三列纯冗余、"生产上分化"失实。切 21_full 后: canonical = 真全宇宙、`_v` = verified 子集、dev 即分化 (WP3 恒等 gate 反转为分化断言); **PA semi-join 明确锚 verified 子集** (锚 21_full 全宇宙则与 16 号同宇宙 → no-op, v16 P0 修复静默蒸发); 自聚合族宇宙写实为 verified 集 (与原盘上行为语义等价)。
- **其余 P1 (已修)**: 跨年去重键去 year + 全局 docid→min(年) 映射 (原 v18 配方在同 docid 跨年时生产静默双计, dev 0 例测不出); D4/D4b 扫描时内联执行 + 明细加 variants_hit 列; registry yaml schema/emit_tracks 逐基名/条目顺序=列序 SSOT/排除理由码枚举定死; D16 替换表完整落 WP0 常量 + xneg 补规则 (v18 谱系 2 列 33 字符超限 + 2 列恰 32 实测); 分类三步顺序定死 (白名单>排除>族>残差崩, 多重命中显式报错); 哈希锚 = canonical JSON sha256 双锚 (禁文件字节, CRLF 跨机假红); 值域 gate 禁列名子串圈定 (dev 实证 llm_vote_tone_std=1.414/disp=4.13 假红反例); D4b "13" 口径写死 (variant 级; pair 级=12 注记, 三口径歧义解除); D9 "上市前结构零"残留清偿; §2 "B3" 空指针清偿。
- **P2 (已吸收)**: §6 pair 长表记账兑现 / §8 十条→十一条 / `_ew`→`ce_` 两处残留 / §9.3 历史保真括注 / 头部上界算术统一 (≈4,820) / 缺失率 35–67% 视族而异 (tone 族 dev ~67% 实测) / 两法等价 isclose 容差 / paths 键名点名 (16=output_15_*, 27 勿用 benefit_cache) / §5 WP3 写 4 文件 / 16 号年份复用 docid→year 映射 / 51 重复列 DUP_OF_40 / "同引擎复算一致" gate 重述为 WP2 手算锁 / pair 长表 schema 定死。
- **独立复核确认 (④, 全部自行重算)**: 42/37/5 逐字复现、无第 6 家逃逸 (bank_names.json 零信托/租赁/消金条目 → 此类结构上不可能成为 target_bank, 无需进对照表)、37 家交集无一多银行映射 (零反向误伤); D4b 22/13 双数复现 (口径 = variant 自身不产生交集); C2 分母 = 该模型自身 verified 篇数 (encode.py L325–331 注释 + L749 mean-skipna 机制摘录证实); BERT 五族 69 列逐列实点恰等 (9+27+9+6+18, iyvol/iytrend 带轨后缀, 23×3 算术成立); BLAS 9 源列与 CLAUDE.md 逐字一致且全部在盘; pair 长表三重 .gitignore 覆盖 (根:56/:92 + news_process:46)。
- **判定**: 四路一致"有条件通过/可实施", 条件已全部落实于本版; 数字体系经穷尽核算全自洽 (166 分族小计/996/4,820 上界/23×3=69/42=37+5/22-13-12 全部收敛), 盘上可验断言 100% 复现 (含零命中闸实扫: dev full 轨 876/1,005 行命中、206 家公司)。**本版为收官终稿, 后续变更只应来自实施记录回填 (§9.4) 或主仓上游漂移。**

### 9.7 v20 第八轮四路终检记录 (2026-07-04, 收官冻结轮)

- **配置**: ① v19 落地全核 + 21_full 波及面全扫 (10 处落点逐条定位 + Markdown 结构零损伤 + 盘上 9 组数字复现) / ② 白纸通读 (不带前轮框架抓"看惯了看不见"的问题) / ③ 14 边界用例对抗轰击 (**矛盾 0**, 高危区 7 场景全由原文一句话封口) / ④ v19 新事实主张独立实测 (**9/9 复现**, 含 tone_llms.py L2872/L2898/L2936 代码级取证、16 号≡21_full 宇宙精确相等、xneg 缩写 0 超限 0 碰撞)。
- **P1×2 (已修)**: ① §3b 共同规则⑦系 v19 输入定案的最后一处漏改 (三路同时抓到; 仍写"自聚合=21 全行宇宙/dev 无区分", 照抄实现即复活 PA no-op 陷阱且会原文落进交付 codebook) → 重写为"权重=21_full 全宇宙 vs 测度侧统一 verified 宇宙"双宇宙框架; ② `_v` 混合 docid 判定歧义 (dev 实测 49 个 unverified 行落在混合 docid 上, 行级/篇级两读法数字不同) → D7 写死**行级**口径 (滤行后重跑同一"docid 任一行命中"判定) + WP2 ⑦ 定向锁。
- **关键实测落定**: 分化 gate 经两路独立 AC 实扫证实安全 — 539 unverified 行 full/ctx/ss 命中 426/406/378 行 (docid 级 350 个纯 unverified docid 有命中), 反转后的 gate 余量数百行级; 21_full full 轨总命中 1,351/1,544 (區别于 §9.6 记录的 876/1,005 旧宇宙数字)。
- **P2 (~18 项已吸收)**: 头部 ×6+19→×6+16 / 两处"v18 前"→"v19 前 (含 v18)" / D1↔WP1-4 互指 (禁含 year 键) / D11d PA 行 v20 括注 (勿按 21_full 全宇宙 join) / D16 施加范围=基名级 + 名单内容哈希入锚 + 双向覆盖断言 / §5.3 与 NW allclose 豁免分层 (同输入重跑无豁免) / D4b 补 12=13−4+3 算式 / WP2 锁编号连续化 (④b) / D8 "唯二"→三族 (含 n_banks ctx/ss 对) / D9 标签截断单位=字符 / D10 映射-窗口顺序封口 (合法域剔除后、窗口裁剪前) + 覆盖表参数化 / WP1-1 空 variant 守卫 / WP1-2 去重 keep='first'+文本 hash 断言 / WP1-4b PA 反向宇宙差日志 (分母=verified∩16) / WP1-5 全 NaN 列诊断 WARNING / WP3 单银行 gate 双 NaN 容错 / §7 上游表述联动 / 缺失率族归属更正 (v19 "tone 族 ~67%" 误归 — canonical tone 实测 35–45%, 67–75% 属 std 伴生/S7 切片; §9.6 原文保真, 更正以 D12 现行文本为准) / D 序号阅读路标。
- **判定**: 四路一致可实施 — 落地核验"通过 (有条件, 条件已落实)"、白纸"修毕放行"、边界轰击"0 矛盾无阻断"、事实实测"9/9 复现无 P0/P1 推翻"。**v20 冻结**: 计划文本层面的评审至此收敛 (八轮、约 28 个专职代理), 后续变更只应来自 §9.4 实施回填或主仓上游漂移; 再启评审的边际收益已低于实施中 WP0/WP2/WP3 三层 fail-loud 机器闸的兜底能力。

### 9.8 v21 第九轮·沙箱干跑轮记录 (2026-07-04, 评审方式升级: 从"读计划"到"照计划写代码跑真数据")

- **配置**: ① 文本终扫 (v20 落地 20 项全核 + ~50 处版本标注 + 全数字/指针/残留/结构五层, **0 P0/0 P1**) / ② **WP0 分区干跑** (scratchpad 实现十一条规则+白名单+族枚举, 对 3,395+68+26+11 列真跑全划分) / ③ **WP1 计数引擎端到端干跑** (真实 dev 数据全链, **WP3 gate A 8/8 一次全过**, 全部关键锚 37/42/5/22/13/30/49 独立复现) / ④ **加权引擎干跑** (**双路径 100% 等价** (13,377 格 isclose) + gate B 全 PASS + **13 个刻意挑刺的不规则后缀基名映射零失败** + 3 格全手算复现 + 性能锚 7.28–7.33M chars/s 复现)。全程仓库零写入, 脚本只落 scratchpad。
- **WP0 干跑核心发现 (本轮价值所在)**: 纯按 v20 文字实现 → **残差 103 列 + 22 条非设计内族∩⑪冲突先行 SystemExit**; 规则体系接住 97%、十几个族小计精确吻合、D16 零残留零碰撞、多族冲突 0 — 缺口全部为**清单级可枚举修补**, 无结构性设计错误。**5×P1 已全部修入**: ① D15 ⑪ 作用域定死 = 候选枚举清单 {net_*_yr + stress_period + 政策 treated/post 族}, 族命中优先 + 全列双评执行语义 (消解"流水线序下冲突报错永不触发"的自相矛盾); ② D11i 预分诊 6 无判定列 (cross_media_alpha→DA 扩 / n_events→CV 扩, 生产者语义已查证 stage 75); ③ S5 扩补漏 25 基名 (34→59); ④ DS llm_vote 孪生拆 `_dm` 第二基名 (31≤32); ⑤ AS 扩补"full 轨无缀"。
- **WP1/加权干跑的口径钉死 (P2, 已修入)**: D4b 集合=真子串 (相等已被 D4 拦, 锚 22)、粒度=逐 (row,track,company); **WP2 牡丹江锁 target_bank 必须写 canonical 龙江银行** (牡丹江市商业银行系其 variant, 照散文写锁错键); 锚数字口径 (426/406/378 = 作废前 unverified-only docid; 1,351 = 作废前, 作废后 918; 探针口径不可相减); N=1 的 N = 非缺失测度银行数; 凸包端点 = join 后非缺失集; pair 表 full/ctx 行 strict=n_docs 恒等; WP1-4 补 track 维; D4 五家配对表机械可复现 (剥"股份有限公司"后缀精确匹配, 1:1); raw hits 21_full 复测 (occurrence 17.6/行, 明细 3.7/行, 1.8 亿为 2.9× 保守上界)。
- **实证增量**: `_v` 行级 vs 篇级口径在 dev 上差 88 格/Σ150 篇 (v20 钉死行级有实质约束力); D4 作废 3,246 条 (top=工行自家 443)、D4b 作废 315 条; D4 在 dev 上零次活体触发 (拦截由映射保证); 30 个跨公司重复 variant dev 零活体双计 (mock 验证通过); NW 判据轨展开口径实测 77 基名 (计划"~"系折叠口径, 小计 gate 以实测锚); DS 实测 76 (原 ~120 高估)。
- **文本终扫 4×P2 (已修)**: 头部 §10 计数 115→150 条/137 DOI; §9.7 "四类"→"三族"; net_*_yr 24+→30 统一; 探针不可相减注记。§9.6 内 "缺失率 35–67%"/"426/406/378 无口径"/"4,820" 等原文按历史保真不改, 现行口径以 D12/WP3/头部为准。
- **判定**: 四路一致 — **计数引擎与加权引擎"可照计划直接实施"** (gate 一次全过、锚全复现、无 P1 缺口); WP0 补入本轮 5 项清单修补后, "残差恰 0" 恢复可合理预期 (剩余不确定性 = 21 域 ~28 列逐列人工判定的工作量与生产机 ⑪ 翻转重锚, 均为计划内机制)。**v21 实证冻结**: 九轮评审 (约 36 个专职代理) 至此不仅读稿收敛, 且核心算法已在真实数据上跑通 — 评审阶段正式终结。

### 9.9 v22 增量包定案记录 (2026-07-04, 用户批准)

- **缘起**: 用户问"共现报道数定权之外还有什么方法、cw/ce 之外还有什么聚合"→ 主线程提四臂建议 → 三路对抗审核 (计量/工程/顶刊) 判"过于慷慨"并抓出 2 处实质错误 (② ln 凹权"对症药"方向反了 — 真对症 = fractional counting; ① "hw=媒体权威"绑错构念 — hw 系羊群衰减, 权威是 mw) → 修正为最小增量包 → 再经三路评审 (计量边角推演 / 工程 dev 迷你干跑 / 纪律守护人) + 主线程仲裁 → 用户批准。
- **C 冲突仲裁记录**: 守护人以"纯变换可复算"砍 `n_docs_frac`, 经核实前提错误 — k 是 docid 级信息、聚合后永久丢失**不可**由 pair 表复算, 恰是"必须扫描时物化"的教科书判据; 加之工程实证 (多银行格 cw~cw_frac corr 仅 0.9417, 极端格权重 5.3%→50%) 为五件最高信息增量 → 采纳。
- **入包**: 面板 +3 (`cooc_hhi` 三轨, D8b, 走 cooc_wt_base 固定列通道) / pair 长表 7→10 列 (+`n_docs_frac`/`n_docs_frac_v`/`n_docs_longhit`) / §7 两段披露 (名录通稿 + 权威臂免做实测) / WP2 ⑧–⑪ 四组锁 / WP3 HHI 三 gate + frac 恒等 gate + k^c 分位数日志 / R3-2 双维分层。
- **砍除 (§8 防再起)**: `top1_share` (与 HHI corr 0.995/夹逼/58% 并列无构念) / `w_auth_sum` (与 n_docs corr 0.998, cwm≈cw corr 0.9996 — 实测事实反写进 §7 作预答) / 全谱权函数臂 (每臂 +2,160 列、4 字符前缀连坐 D16、推翻 D14)。
- **顺带修复的计划缺陷** (独立于增量包): S5 三处 "vw/mw/hw = stage 62 媒体权重制" 失实 (代码级: vw=提及密度/mw=权威/hw=羊群, `runner.py:731/783/816–837`); pair 长表 year 未钉死 (行级原始年会使 n_docs 权重质量跨年双计 — v19 修的 bug 在加权侧的半扇门, 已封); target_bank ⊆ canonical 生产断言 (集外银行使 D4b 静默失效)。
- **dev 干跑实证锚** (生产回填更新): HHI ~75% 非零格 ≡1/n_banks (稀疏重参数化, 定位"补充诊断"的依据); frac 恒等式 425 格 0 违例 (max 偏差 1.8e-15); k^c max=56; 媒体权威分 CV 0.121。
- **未入包待议** (贷款表接入后另立计划): 媒体共现 vs 真实借款关系的**构念效度对照** — `config/` 已到盘三个 dta (上市公司向金融机构借款表/董监高金融机构背景表/银行业金融机构基本信息表), 顶刊组判其价值数量级高于任何权函数臂; 贷款规模定权对照臂同期。

### 9.10 v23 加权列裁剪定案记录 (2026-07-04, 用户批准; 五轮十代理 + 主线程机械复验)

- **触发与授权**: 用户令"识别完全没有必要放入的加权列并删除, 再三核对; 相关主题必须有足够稳健性, 严禁为了删除而删除", 并锚定研究目的 = **银行 (主要是银行金融科技及其各维度) 媒体报道对上市公司的影响** — 该声明构成对 v15 "全谱"半边的明示推翻 (单文件半边不动), 亦是 AD 采纳三型救回裁决的直接依据 (见下)。
- **审查配置** (全代理只读, 干跑分区 704 基名为划分域): R1 三路并行 = 构念效用 (产 435 初始候删) + dev 实证 (梯子臂间 ρ 一手测量) + 一致性/可重构性 (六条红线 + 79 项必要集 + 基名整删粒度论证); R2 对抗复核 = 辩方逐项推翻测试 (推翻 1 修正 4) + 清点代理平表对账 (435/435 零差集); R3 目的重审三路 = 处理构念中心性 (T0/T1/T2 分层, 救回 AD 18 + xneg 2) + 三份模拟审稿 (计量/领域/中文顶刊, 一致 0 失守) + 反"为删而删"审计 (25 删除类逐类归 A/B/C 级, 0 类裸靠口号; A 级数字亲测零幻觉); R4 终验 = 全新代理整体终确认 (救回过度检查/孤儿检查/253 文件消费者全扫零冲突/研究目的全变量对表零落空, **1 修正后签字放行**) + 主线程机械复验 (铁律组 10/10、嵌入 20 对零孤儿、必要集 0 违例)。
- **终值**: 删 **410 基名 ×6 = 2,460 列** / 保留 294 (40 面板域) + ~25 域外基名; 负清单 = `COMPANY_BANK_COOC_PANEL_CUT_LIST_v23.txt` (与本计划同为 WP4 by-name 提交物, 第 7 文件)。判据/粒度/救回史/四前提/生产复核条款全文见 **D17**。
- **关键裁决留痕**: ① AD 采纳三型 18 个救回 — R3 两代理曾以"adopt 非主解释变量, 附录臂可接受"维持删除但各自附条件"若 adoption 成为核心变量须 WP0 前赎回", 用户目的声明使条件当下成立, 主线程终裁采救回 (阈值臂 ρ=0.163–0.601 真变异 + T0 处理本体双重依据); ② `finbert_cn_xneg_t80/t95` 救回 — 终验 I 判其为 412 项中唯一"无证据即删" (dev 全族零方差 ≠ 恒等证据, "禁 T=2 借口"铁律 + D11h dev 退化列纳入先例), 救回后 xneg 删除规则收敛为纯数据驱动 "ρ≥0.995 恒等臂不出列"; ③ `_dcls` 幻影争议终裁 — 字面列不在盘 (R3-H 对) 但源列实存 (R2-D 对; 收官终审定数 **12 列**, 中缀集 {lc,ls,cm,sc,ss}, 仅 ctx/ss 两轨无 full 孪生), 6 基名维持删除、命名统一 `_dm` (WP0-6 ①); ④ DP 结构重排 — 保 du+loughran 两对的 2/6 任意切分被否, 改为救回 ensemble 载体 `avg_{pos,neg}_ratio` (自 CL 删单移出) + per-dict 12 全删, 与 S1c/BERT 侧三方法对称; ⑤ 证据勘误两条已写死 D17 (CT 勿称 cw 层恒等 / HD thr ρ=0.9417–0.9945 勿引 0.9936)。
- **随裁剪抓出的干跑缺陷** (独立于删列, 落 WP0-6): `_dcls`→`_dm` 命名 / lazy 第四基名注册 bug / `llm_vote_tone_std` 白名单疑被吞 (不在 704 域) / MISC jf "可复算"失实表述 (真分母 = `n_articles_llm_valid`, 属排除域 — 删除依据已改写为重构保障 + sp=0.9999)。
- **本记录后计划内状态**: D17/D15 第四步/WP0-5·6/WP2 ⑫/WP3 双 gate/§6 必附/§7 (NW 收缩 + 多重检验·体积两段)/§8 防再起/头部三处列数/§3b (文件功能段+表头+996 注+使用要点+凸包规模数) — 联动已全部落墨 (§5 经收官终审核定**无需改动**, 自旧"十处"清单移除); 实施回填仍走 §9.4。
- **收官终审记录** (2026-07-04, 用户令"最后一次最高标准全面评审"后加做, 三路全新只读代理: 全文一致性与账目 / 实施者走查 (负清单机械验算 + 40 面板实测) / D17·§9.10 事实主张逐条一手复测): 收 **P0×2** (§3b 文件功能段"全谱/~4,000"陈旧且会随 D9 落进交付 codebook; `_dcls→_dm` 改名与 WP0-5/⑫b "逐名对上/集合恰等"断言字面矛盾 → 已写死对账前 6 条别名映射)、**P1×14** (§7 两段 v13 旧数漏改 / KEEP 294·域 704 系干跑快照且 WP0-6 修正后预期 **292/702** 而计划无对账语义 (已在 WP0-5 钉死"负清单仅锚 CUT 410、禁 keep==294/domain==704 断言") / 19 固定列口径混用 / §3 标题漏 D17 / GAP_UNPLANNED 族码未定义 (已定: 族列仅人读, 正式归属按 D11i) / `llm_vote_tone_std` emit 未裁决 (已定 emit=true) / 负清单解析规格缺失 (已规格化: 全等段头+tab+仅基名对账) / 704↔719–733 无桥接 (已补 D8) / **两处事实失实已勘误**: "washing per-model ρ≥0.9988" 实测 full 轨 min=**0.9679** (gemini31; 达标仅六词典臂+hc, per-model 臂删除依据改归判据 (b)) 与 "`_dcls` 源列 18 列" 实为 **12** 列 等)、**P2×19** 择要修入 ((A) 表断裂空行 / finbert2_t95 "=1.0" 系 4 位舍入 (0.99998, maxdiff=0.0089 非逐位) / runner.py:816 系节头注释 (hw 赋值在 831/837, 引用已改 816–837) / S2·HD 区间标注 full 轨口径且 S2 删除归判据 (b) / 引擎迭代域钉死 emit 子集 / 新族族间序钉死 D11b→c→d→e→i / cut_code 改中性 CUT_V23 / D11i 表行 2 基名 / 凸包规模数 ~950 / bert_avg_neu 注记语义消歧 / IN·cogn 族 full 裸名注 / D9 补注册表清单指针 等)。同轮 **PASS 项**: 负清单结构 (410/294/25 族小计/零重复零交集) 全对; 嵌入 20 对零孤儿与点名铁律组独立重跑复现; 代码引用行号 8/9 精确; "253 文件消费者零冲突"口径可复现 (git-tracked 非 md 恰 253); D16 替换表在 emit 子集覆盖全部 4 个超限名 (另 7 个恰 32 零余量, fail-loud 兜底必留); AD/xneg/allv/HD/PC/S2 全部 dev ρ 一手复现零幻觉。⚠ **评审代理计数统一口径**: v23 裁剪全程 = 五轮 **12 个专职代理** (R1 三 + R2 二 + R3 三 + R4 终验一 + 收官三) + 主线程机械复验; 此前"十代理"系 R4 时点计法, 以本句为准。⚠ 两项可追溯性义务追加落 WP2: "79 项必要集"与"铁律组全集"以常量落 registry 测试, 使机器断言可在 repo 内复跑 (session scratchpad 脚本不留档)。

## 10. 学术锚点 (APA 7; 全部经核验, 见 §9.2; 〔〕内为计划构念映射)

**范围声明** (终审 F2-5): 本节锚点覆盖**计划级关键决策与主构念族** (计数/情感三方法/分类维度/加权识别/网络/多重检验/LLM 推断等); 次级构念族 (TD/BD/CL/ST/BP/RW/AD/FE/CO/AS/CT/PE/KW/CTRL) 的锚点归主仓各论文注册表 (`LITERATURE_ANCHORS_*` 全套 507 DOI), 不在此重复。
**来源纪律**: 每条出处二选一 — (R) = 仓库已核验注册表逐字在册 (`scripts/audit/LITERATURE_ANCHORS_*.md`, 507 DOI 全过 Crossref/DataCite); (W) = 本轮网检/Crossref 实取并三对照。**零条目出自记忆**。⚠ 缺口披露: 附件式(3) 中文原文 (李逸飞等 2024) 经检索未能核验定位题录, 按纪律**不写入** — 计划正文对其保持"用户提供附件"引用形态, 待补题录核验后再入; Bian et al. (2021) SSRN 首贴年 2019, 投稿前确认年份口径 (注册表内置警示)。

### 10.1 银企共现计数与媒体覆盖 〔D1–D3 计数列 / Q・CV 族〕

- Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. *The Journal of Finance, 64*(5), 2023–2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x (R)〔n_cooc 计数主锚〕
- Peress, J. (2014). The media and the diffusion of information in financial markets: Evidence from newspaper strikes. *The Journal of Finance, 69*(5), 2007–2043. https://doi.org/10.1111/jofi.12179 (R)
- Engelberg, J. E., & Parsons, C. A. (2011). The causal impact of media in financial markets. *The Journal of Finance, 66*(1), 67–97. https://doi.org/10.1111/j.1540-6261.2010.01626.x (R)〔计数内生性〕
- Bybee, L., Kelly, B. T., Manela, A., & Xiu, D. (2024). Business news and business cycles. *The Journal of Finance, 79*(5), 3105–3147. https://doi.org/10.1111/jofi.13377 (R)〔大语料→面板〕
- Gutknecht, D. (2025). Media coverage of corporate social irresponsibility and firm equity risk. *Review of Quantitative Finance and Accounting, 65*(4), 1373–1403. https://doi.org/10.1007/s11156-024-01383-0 (R)
- Cagé, J., Hervé, N., & Viaud, M.-L. (2020). The production of information in an online world. *The Review of Economic Studies, 87*(5), 2126–2164. https://doi.org/10.1093/restud/rdz061 (R)〔D1 docid 去重〕
- Silcock, E., D'Amico-Wong, L., Yang, J., & Dell, M. (2022). *Noise-robust de-duplication at scale* (NBER Working Paper No. 30726). https://doi.org/10.3386/w30726 (R)〔去重方法学〕
- Guo, L., Peng, L., Tao, Y., & Tu, J. (2026). *Joint news, attention spillover, and stock returns* (SSRN No. 2927561). https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2927561 (R)〔同篇共现 joint news 直接锚 / multi_bank_frac〕
- Ge, S., Li, S., & Zheng, H. (2025). Diamond cuts diamond: News co-mention momentum spillover prevails in China. *Journal of Banking & Finance, 171*, Article 107356. https://doi.org/10.1016/j.jbankfin.2024.107356 (W)〔中国新闻共现→企业关联效度; 核验修正 DOI〕
- Hilt, V., & Schwenkler, G. (2024). *The different networks of firms implied by the news* (SSRN No. 4946066). https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4946066 (W)〔共现≠单一关系类型, §7 局限〕
- Zhu, S., He, C., Liu, H., Dong, P., Zhao, H., Yan, Y., Jia, Y., Zan, H., & Peng, M. (2024). SILC-EFSA: Self-aware in-context learning correction for entity-level financial sentiment analysis. arXiv. https://doi.org/10.48550/arXiv.2412.19140 (R)〔实体级窗口打分 ≈ _ctx/_ss 佐证 (终审收窄: 该文为实体级情感基准, 不涉共现判定)〕

### 10.2 情感测度-LLM 法 〔S1/S1b/S1c 族・D7 门控〕

- de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. *Management Science, 71*(9), 7888–7906. https://doi.org/10.1287/mnsc.2023.03253 (R)〔temperature=0/prompt 冻结/缓存范式〕
- Kirtac, K., & Germano, G. (2024). Sentiment trading with large language models. *Finance Research Letters, 62*, 105227. https://doi.org/10.1016/j.frl.2024.105227 (R)
- Lopez-Lira, A., & Tang, Y. (2025). *Can ChatGPT forecast stock price movements?* (SSRN No. 4412788). https://ssrn.com/abstract=4412788 (R)
- Jha, M., Qian, J., Weber, M., & Yang, B. (2024). *ChatGPT and corporate policies* (NBER Working Paper No. 32161). https://doi.org/10.3386/w32161 (R)〔LLM 分数→企业面板整链〕
- Hansen, A. L., & Kazinnik, S. (2023). *Can ChatGPT decipher Fedspeak?* (SSRN No. 4399406). https://doi.org/10.2139/ssrn.4399406 (R)〔三方法横比设计〕
- Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. *Neural Computing and Applications, 37*(30), 24883–24892. https://doi.org/10.1007/s00521-024-10603-6 (R)〔中文金融 LLM 实体级情感〕
- Chen, K., Granville, B., & Matousek, R. (2026). Decoding central bank communications with large language models. *Journal of International Financial Markets, Institutions and Money, 109*, Article 102325. https://doi.org/10.1016/j.intfin.2026.102325 (R)
- Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv. https://doi.org/10.48550/arXiv.2511.15714 (R)〔llm_vote 多数投票〕
- Li, J., Zhang, Q., Yu, Y., Fu, Q., & Ye, D. (2024). More agents is all you need. *Transactions on Machine Learning Research*. https://openreview.net/forum?id=bgzUSZ8aeg (R)〔投票集成降噪〕
- Chen, Y., Kelly, B. T., & Xiu, D. (2025). *Expected returns and large language models* (SSRN No. 4416687; R&R at RFS). https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4416687 (W)〔⚠核验降级: 勿引"RFS 38 卷"假卷页〕
- Kim, A., Muhn, M., & Nikolaev, V. (2024). *Financial statement analysis with large language models*. arXiv:2407.17866. https://arxiv.org/abs/2407.17866 (W)

### 10.3 情感测度-词典法与规则消融 〔S2/S2b/S3/S6 族・九变体・polw 梯子〕

- Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. *The Journal of Finance, 66*(1), 35–65. https://doi.org/10.1111/j.1540-6261.2010.01625.x (R)〔loughran 词典 + S6 扩展类别〕
- Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. *Review of Finance, 26*(3), 673–719. https://doi.org/10.1093/rof/rfab036 (R)〔du_2022 + 政治词权重 polw〕
- 姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. *经济学(季刊), 21*(4), 1323–1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10 (R)〔jiang_2021〕
- Bian, S., Jia, D., Li, F., & Yan, Z. (2021). *A new Chinese financial sentiment dictionary for textual analysis in accounting and finance* (SSRN No. 3446388). https://doi.org/10.2139/ssrn.3446388 (R)〔bian_2021; ⚠年份口径警示〕
- You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? *The Review of Financial Studies, 31*(1), 43–96. https://doi.org/10.1093/rfs/hhx055 (R)〔you_2018 + 官媒/市场化双锚〕
- Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. *Expert Systems with Applications, 264*, 125739. https://doi.org/10.1016/j.eswa.2024.125739 (R)
- García, D., Hu, X., & Rohrer, M. (2023). The colour of finance words. *Journal of Financial Economics, 147*(3), 525–549. https://doi.org/10.1016/j.jfineco.2022.11.006 (R)〔多词典并行 + dict_avg〕
- Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. *Economic Inquiry, 63*(1), 125–143. https://doi.org/10.1111/ecin.13264 (R)〔LLM 时代保留词典轨〕
- Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. *Intelligent Systems in Accounting, Finance and Management, 31*(1), e1549. https://doi.org/10.1002/isaf.1549 (R)
- Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. *The Journal of Finance, 62*(3), 1139–1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x (R)〔S2b msent 零规则档原点〕
- Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. *Journal of Financial Economics, 110*(3), 712–729. https://doi.org/10.1016/j.jfineco.2013.08.018 (R)〔idf 臂〕
- Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. *Journal of Accounting Research, 54*(4), 1187–1230. https://doi.org/10.1111/1475-679X.12123 (R)〔消融敏感性依据〕
- Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. *Journal of Documentation, 28*(1), 11–21. https://doi.org/10.1108/eb026526 (R)〔IDF 原始出处〕
- Salton, G., & Buckley, C. (1988). Term-weighting approaches in automatic text retrieval. *Information Processing & Management, 24*(5), 513–523. https://doi.org/10.1016/0306-4573(88)90021-0 (R)
- Kennedy, A., & Inkpen, D. (2006). Sentiment classification of movie reviews using contextual valence shifters. *Computational Intelligence, 22*(2), 110–125. https://doi.org/10.1111/j.1467-8640.2006.00277.x (R)〔否定/程度规则出处〕
- Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. *Computational Linguistics, 37*(2), 267–307. https://doi.org/10.1162/COLI_a_00049 (R)〔advonly/转折规则〕
- Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. *Decision Support Systems, 88*, 67–75. https://doi.org/10.1016/j.dss.2016.05.009 (R)〔negonly 臂〕
- Punetha, N., & Jain, G. (2025). Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach. *Social Network Analysis and Mining, 15*(1), Article 20. https://doi.org/10.1007/s13278-025-01416-z (R)
- Barbaglia, L., Consoli, S., & Manzan, S. (2023). Forecasting with economic news. *Journal of Business & Economic Statistics, 41*(3), 708–719. https://doi.org/10.1080/07350015.2022.2060988 (R)〔实体窗内打分 ≈ _ctx/_ss〕
- Algaba, A., Ardia, D., Bluteau, K., Borms, S., & Boudt, K. (2020). Econometrics meets sentiment: An overview of methodology and applications. *Journal of Economic Surveys, 34*(3), 512–547. https://doi.org/10.1111/joes.12370 (R)〔词级→聚合→回归全链〕
- Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. *Journal of Economic Literature, 57*(3), 535–574. https://doi.org/10.1257/jel.20181020 (R)〔全表方法学总纲〕

### 10.4 情感测度-BERT 法 〔S4/S4b 族〕

- Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. *Contemporary Accounting Research, 40*(2), 806–841. https://doi.org/10.1111/1911-3846.12832 (R)
- Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. In *Proceedings of the 31st ACM SIGKDD Conference* (pp. 5117–5128). https://doi.org/10.1145/3711896.3737219 (R)〔finbert2 同源〕
- Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J. (2020). FinBERT: A pre-trained financial language representation model for financial text mining. In *Proceedings of IJCAI-20* (pp. 4513–4519). https://doi.org/10.24963/ijcai.2020/622 (R)
- Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. *Management Science, 68*(7), 5514–5532. https://doi.org/10.1287/mnsc.2021.4156 (R)〔三方法互为稳健先例〕
- Nasiopoulos, D. K., Roumeliotis, K. I., Sakas, D. P., Toudas, K., & Reklitis, P. (2025). Financial sentiment analysis and classification: A comparative study of fine-tuned deep learning models. *International Journal of Financial Studies, 13*(2), Article 75. https://doi.org/10.3390/ijfs13020075 (R)
- Hicham, N., & Habbat, N. (2026). LLMs and generative AI for financial sentiment classification: An explainable domain-adaptive framework. *Digital, 6*(2), Article 48. https://doi.org/10.3390/digital6020048 (R)
- Nițoi, M., Pochea, M.-M., & Radu, Ş.-C. (2023). Unveiling the sentiment behind central bank narratives: A novel deep learning index. *Journal of Behavioral and Experimental Finance, 38*, 100809. https://doi.org/10.1016/j.jbef.2023.100809 (R)

### 10.5 银行级媒体情感的经济落点 〔cw_*tone* 列〕

- Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. *International Review of Economics & Finance, 91*, 1150–1172. https://doi.org/10.1016/j.iref.2024.01.067 (R)〔中国银行级媒体情感同域〕
- Marchetti, S., Tarducci, E., & Branzoli, N. (2025). *Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy* (SSRN). https://doi.org/10.2139/ssrn.5220056 (R)〔银行×年语气聚合口径〕
- Jacobs, H., & Lauber, A. (2026). Media sentiment and price run-ups. *European Financial Management, 32*(2), 677–700. https://doi.org/10.1111/eufm.70025 (R; 终审 Crossref 复核: 印刷版 2026 年 3 月, 32(2); 2025 为 online-first 年)
- Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C. (2026). Social media as a bank run catalyst. *Journal of Financial Economics, 176*, 104218. https://doi.org/10.1016/j.jfineco.2025.104218 (R)

### 10.6 注意力/显著性/报道形态 〔AT・CS 族〕

- Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. *The Quarterly Journal of Economics, 134*(4), 2135–2202. https://doi.org/10.1093/qje/qjz021 (R)〔公司级文本暴露面板总范式〕
- Da, Z., Engelberg, J., & Gao, P. (2011). In search of attention. *The Journal of Finance, 66*(5), 1461–1499. https://doi.org/10.1111/j.1540-6261.2011.01679.x (R)〔对照锚, 主锚归 Fang & Peress〕
- Cookson, J. A., Lu, R., Mullins, W., & Niessner, M. (2024). The social signal. *Journal of Financial Economics, 158*, 103870. https://doi.org/10.1016/j.jfineco.2024.103870 (R)〔注意力与情感可分离 → Q/S 并出〕
- Chen, Z., Li, Z., Liu, J., & Liu, X. (2026). Information salience, investor attention, and stock price crash risk. *Journal of Empirical Finance, 85*, Article 101670. https://doi.org/10.1016/j.jempfin.2025.101670 (R)
- Fedyk, A. (2024). Front-page news: The effect of news positioning on financial markets. *The Journal of Finance, 79*(1), 5–33. https://doi.org/10.1111/jofi.13287 (R)〔frac_front_page 因果证据〕
- Boudoukh, J., Feldman, R., Kogan, S., & Richardson, M. (2019). Information, trading, and volatility: Evidence from firm-specific news. *The Review of Financial Studies, 32*(3), 992–1033. https://doi.org/10.1093/rfs/hhy083 (R)〔frac_target_in_lead〕
- Hirshleifer, D., Lim, S. S., & Teoh, S. H. (2009). Driven to distraction: Extraneous events and underreaction to earnings news. *The Journal of Finance, 64*(5), 2289–2325. https://doi.org/10.1111/j.1540-6261.2009.01501.x (R)〔有限注意力 → HD〕
- Li, Y. (2026). The textual tone of annual reports and market attention: Evidence from Chinese listed companies. *Managerial and Decision Economics*. Advance online publication. https://doi.org/10.1002/mde.70100 (R; 终审 Crossref 复核: 尚无卷期, 原"46 卷"删除, 按 early view 引)〔A 股同对象同语种〕

### 10.7 媒体类型/权重/地理 〔S5 vw·mw·hw・S7 切片・MC 族〕

- Qin, B., Strömberg, D., & Wu, Y. (2018). Media bias in China. *American Economic Review, 108*(9), 2442–2476. https://doi.org/10.1257/aer.20170947 (R)〔央媒/地方切片体制基础〕
- Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. *Journal of Accounting Research, 53*(2), 405–459. https://doi.org/10.1111/1475-679X.12071 (R)〔official/market_media_frac〕
- Gentzkow, M., & Shapiro, J. M. (2010). What drives media slant? Evidence from U.S. daily newspapers. *Econometrica, 78*(1), 35–71. https://doi.org/10.3982/ECTA7195 (R)〔媒体风格固定性 → outlet 权重〕
- Dougal, C., Engelberg, J., García, D., & Parsons, C. A. (2012). Journalists and the stock market. *The Review of Financial Studies, 25*(3), 639–679. https://doi.org/10.1093/rfs/hhr133 (R)
- Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local media slant, local advertising, and firm value. *The Journal of Finance, 67*(2), 561–598. https://doi.org/10.1111/j.1540-6261.2012.01725.x (R)〔neg_frac_homeprov/homecity〕
- Guest, N. M. (2021). The information role of the media in earnings news. *Journal of Accounting Research, 59*(3), 1021–1076. https://doi.org/10.1111/1475-679X.12349 (R)〔deepdive/staff_written/wire〕
- Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. *The Accounting Review, 98*(7), 315–345. https://doi.org/10.2308/TAR-2020-0104 (R)〔媒体权威加权 tone 直接锚〕
- Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct. *Journal of Financial Economics, 145*(2), 445–463. https://doi.org/10.1016/j.jfineco.2021.08.015 (R)〔ceased_media_frac〕
- Gao, P., Lee, C., & Murphy, D. (2020). Financing dies in darkness? The impact of newspaper closures on public finance. *Journal of Financial Economics, 135*(2), 445–467. https://doi.org/10.1016/j.jfineco.2019.06.003 (R)
- Kang, B. U., & Nam, J. S. (2025). Do local newspapers matter to institutional investors? *Contemporary Accounting Research, 42*(3), 1713–1743. https://doi.org/10.1111/1911-3846.13049 (R)

### 10.8 网络/中介 〔NW 族・brok_bip・gf_*〕

- Gould, R. V., & Fernandez, R. M. (1989). Structures of mediation: A formal approach to brokerage in transaction networks. *Sociological Methodology, 19*, 89–126. https://doi.org/10.2307/270949 (R)〔gf_* 算法出处; ⚠勿用曾流传的错 DOI 10.1086/229068〕
- Han, M., Kim, S. (H.), & Nanda, V. K. (2024). Institutional brokerage networks: Facilitating liquidity provision. *The Review of Financial Studies, 37*(9), 2903–2935. https://doi.org/10.1093/rfs/hhae026 (R)〔构念锚非算法〕
- Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. *Annual Review of Economics, 13*, 171–202. https://doi.org/10.1146/annurev-economics-083120-111540 (R)
- Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. *Journal of Financial Economics, 144*(1), 247–272. https://doi.org/10.1016/j.jfineco.2021.05.060 (R)〔W 矩阵设定即识别 — 对共现权重构造的方法论提醒〕
- Zádor, Z., Zhu, Z., Smith, M., & Gorgoni, S. (2022). A weighted and normalized Gould–Fernandez brokerage measure. *PLOS ONE, 17*(9), e0274475. https://doi.org/10.1371/journal.pone.0274475 (R)
- Neal, Z. P., & Neal, J. W. (2024). Illustrating the importance of edge constraints in backbones of bipartite projections. *PLOS ONE, 19*(5), e0302973. https://doi.org/10.1371/journal.pone.0302973 (R)〔二模投影 + 结构性零〕
- Neal, Z. P. (2026). Backbone 3.0: An R package for extracting network backbones. *PLOS ONE, 21*(5), e0349258. https://doi.org/10.1371/journal.pone.0349258 (R)
- Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. *International Review of Financial Analysis, 93*, 103223. https://doi.org/10.1016/j.irfa.2024.103223 (R)
- Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. *Journal of the Academy of Marketing Science, 53*(1), 79–104. https://doi.org/10.1007/s11747-024-01043-8 (R)〔⚠注册表注: 不背书 bank_clustering〕

### 10.9 加权暴露构造与识别 〔式(3)・D12–D14・使用要点 Hansen J/FWER〕

- Petersen, M. A., & Rajan, R. G. (1994). The benefits of lending relationships: Evidence from small business data. *The Journal of Finance, 49*(1), 3–37. https://doi.org/10.1111/j.1540-6261.1994.tb04418.x (W-Crossref 实取)〔银企关系谱系奠基 — 式(3) "银行对企业影响经由关系"前提〕
- Khwaja, A. I., & Mian, A. (2008). Tracing the impact of bank liquidity shocks: Evidence from an emerging market. *American Economic Review, 98*(4), 1413–1442. https://doi.org/10.1257/aer.98.4.1413 (W-Crossref 实取)〔银行冲击经贷款关系传导至企业的识别范式 — cw_X 设计的经济学原型〕
- Bartik, T. J. (1991). *Who benefits from state and local economic development policies?* W.E. Upjohn Institute. https://doi.org/10.17848/9780585223940 (R)〔share×shift 加权范式源头〕
- Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. *American Economic Review, 110*(8), 2586–2624. https://doi.org/10.1257/aer.20181047 (R)〔份额外生路径 + Rotemberg 权重诊断〕
- Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share research designs. *The Review of Economic Studies, 89*(1), 181–213. https://doi.org/10.1093/restud/rdab030 (R)〔shift 外生路径〕
- Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. *Journal of Economic Perspectives, 39*(1), 181–204. https://doi.org/10.1257/jep.20231370 (R/W 双源)〔cw_X = share(共现权重)×shift(银行测度) 的检查表; 含 incomplete-shares/重归一选择的正面处理 (D12)〕
- Adão, R., Kolesár, M., & Morales, E. (2019). Shift-share designs: Theory and inference. *The Quarterly Journal of Economics, 134*(4), 1949–2010. https://doi.org/10.1093/qje/qjz025 (R)〔exposure-robust 标准误〕
- Borusyak, K., & Hull, P. (2025). *Optimal formula instruments* (NBER Working Paper No. 33594). https://doi.org/10.3386/w33594 (R/W)〔公式型暴露变量 recentering〕
- Apfel, N. (2024). Relaxing the exclusion restriction in shift-share instrumental variable estimation. *Journal of the Royal Statistical Society Series A, 187*(3), 748–771. https://doi.org/10.1093/jrsssa/qnad148 (R)
- Hahn, J., Kuersteiner, G., Santos, A., & Willigrod, W. (2024). Overidentification in shift-share designs. arXiv. https://doi.org/10.48550/arXiv.2404.17049 (R)〔禁混 Hansen J 铁律的计量支撑〕
- Breuer, M. (2022). Bartik instruments: An applied introduction. *Journal of Financial Reporting, 7*(1), 49–67. https://doi.org/10.2308/JFR-2021-003 (R)
- Gabaix, X., & Koijen, R. S. J. (2024). Granular instrumental variables. *Journal of Political Economy, 132*(7), 2274–2303. https://doi.org/10.1086/728743 (R)〔cw 规模加权 vs ce 等权的识别对比〕
- Wu, D. (A.). (2024). Text-based measure of supply chain risk exposure. *Management Science, 70*(7), 4781–4801. https://doi.org/10.1287/mnsc.2023.4927 (R)〔公司级文本暴露 2024 同法先例〕
- Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy? *The Journal of Finance, 69*(1), 139–178. https://doi.org/10.1111/jofi.12094 (R)〔D15 ① 排除 LOO 族的**对照锚** — 该构造属分析端同伴效应设计, 非银行自身测度 (终审改写, 防误读为纳入锚)〕
- Ahnert, T., Doerr, S., Pierri, N., & Timmer, Y. (2026). Information technology in banking and entrepreneurship. *Management Science, 72*(3), 1796–1813. https://doi.org/10.1287/mnsc.2023.02555 (W)〔"对高技术银行的暴露"同族 exposure 设计〕

### 10.10 银行金融科技测度与企业溢出 〔Q/F/F2 族・效度〕

- 胡俊, 李强, 戴嘉诚, 曾勇. (2024). 基于文本分析的商业银行金融科技测度及赋能效果检验. *中国管理科学, 32*(1), 31–41. (R; 注册表即无 DOI)〔上游 1506 金科词典出处〕
- Cheng, M., & Qu, Y. (2020). Does bank FinTech reduce credit risk? Evidence from China. *Pacific-Basin Finance Journal, 63*, 101398. https://doi.org/10.1016/j.pacfin.2020.101398 (R)〔中国 bank FinTech 指数面板对标〕
- Hau, H., Huang, Y., Lin, C., Shan, H., Sheng, Z., & Wei, L. (2024). FinTech credit and entrepreneurial growth. *The Journal of Finance, 79*(5), 3309–3359. https://doi.org/10.1111/jofi.13384 (R/W 双源)〔金科→企业实质效应 JF 主锚〕
- Kwan, A., Lin, C., Pursiainen, V., & Tai, M. (2024). Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic. *Journal of Financial and Quantitative Analysis, 59*(6), 2618–2646. https://doi.org/10.1017/S0022109023000662 (R)
- He, Z., Jiang, S., Xu, D., & Yin, X. (2026). Investing in lending technology: IT spending in banking. *Management Science*. Advance online publication. https://doi.org/10.1287/mnsc.2024.04608 (R)
- Berg, T., Fuster, A., & Puri, M. (2022). FinTech lending. *Annual Review of Financial Economics, 14*, 187–207. https://doi.org/10.1146/annurev-financial-101521-112042 (R)
- Babina, T., Bahaj, S., Buchak, G., De Marco, F., Foulis, A., Gornall, W., Mazzola, F., & Yu, T. (2025). Customer data access and fintech entry: Early evidence from open banking. *Journal of Financial Economics, 169*, Article 103950. https://doi.org/10.1016/j.jfineco.2024.103950 (W; 核验补 JFE 版, NBER w32089 为 WP 版)
- Ghosh, P., Vallée, B., & Zeng, Y. (2026). FinTech lending and cashless payments. *The Journal of Finance, 81*(2), 1053–1101. https://doi.org/10.1111/jofi.70003 (W)〔金科改变银企信贷匹配机制〕
- Wu, M., Shen, L., Wu, T., & Shao, Y. (2025). Does strategic cooperation between banks and fintech companies increase bank risk-taking? Evidence from China. *Applied Economics*. Advance online publication. https://doi.org/10.1080/00036846.2025.2536881 (R)
- Li, T., Stasinakis, C., Yeo, W. M., & Da Silva Fernandes, F. (2025). Fintech, financial development and banking efficiency: Evidence from Chinese commercial banks. *The European Journal of Finance, 31*(10), 1245–1295. https://doi.org/10.1080/1351847X.2025.2468481 (W; 核验补作者)〔⚠非清单顶刊, 仅作文本挖掘构造惯例佐证〕
- Shen, Y., Han, F., & Li, Y. (2025). *Digital financial inclusion and income inequality in China* (IMF Working Paper No. 2025/071). https://www.elibrary.imf.org/view/journals/001/2025/071/article-A001-en.xml (W)〔媒体测度 vs 指数测度对照〕

### 10.11 分类三维度 〔C1/C2/QD/DS 族〕

- Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital finance and FinTech: Current research and future research directions. *Journal of Business Economics, 87*(5), 537–580. https://doi.org/10.1007/s11573-017-0852-x (R)〔locus 维直接出处〕
- Chesbrough, H. W. (2003). *Open innovation: The new imperative for creating and profiting from technology*. Harvard Business School Press. (R; 注册表即无 DOI)〔collab 维理论原点〕
- Yoo, Y., Henfridsson, O., & Lyytinen, K. (2010). The new organizing logic of digital innovation: An agenda for information systems research. *Information Systems Research, 21*(4), 724–735. https://doi.org/10.1287/isre.1100.0322 (R)〔locus 分层逻辑〕
- Zhang, H., Ma, Z., Liang, X., & Garrett, T. C. (2024). Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis. *Journal of Product Innovation Management, 41*(4), 793–815. https://doi.org/10.1111/jpim.12710 (R)〔collab 二分最新 meta〕
- Lerner, J., Seru, A., Short, N., & Sun, Y. (2024). Financial innovation in the twenty-first century: Evidence from US patents. *Journal of Political Economy, 132*(5), 1391–1449. https://doi.org/10.1086/727712 (R)〔创新来源归属 JPE 编码参照〕
- Kim, E.-H., & Lyon, T. P. (2015). Greenwash vs. brownwash: Exaggeration and undue modesty in corporate sustainability disclosure. *Organization Science, 26*(3), 705–723. https://doi.org/10.1287/orsc.2014.0949 (R)〔substance 维 decoupling 经典〕
- Giannetti, M., Jasova, M., Loumioti, M., & Mendicino, C. (2026). "Glossy green" banks: The disconnect between environmental disclosures and lending activities. *Management Science*. Advance online publication. https://doi.org/10.1287/mnsc.2024.07420 (R)〔银行为单位的实质-象征脱钩〕
- Sastry, P. R., Verner, E., & Marques-Ibanez, D. (2024). *Business as usual: Bank net zero commitments, lending, and engagement* (NBER Working Paper No. 32402). https://www.nber.org/papers/w32402 (R)
- Lai, H., Quan, L., Wu, F., Tang, S., Guo, C., & Lai, X. (2025). Corporate environmental publicity and green innovation: Are words consistent with actions? *Humanities and Social Sciences Communications, 12*(1), 514. https://doi.org/10.1057/s41599-025-04826-8 (R)〔中国上市公司实质-象征二分〕
- Chen, X., Wan, P., Ma, Z., & Yang, Y. (2024). Does corporate digital transformation restrain ESG decoupling? Evidence from China. *Humanities and Social Sciences Communications, 11*(1), Article 407. https://doi.org/10.1057/s41599-024-02921-w (R)
- Kueschnig, M., & Schertler, A. (2024). Fusing futures: Financial institutions' stock price response to fintech acquisitions. *Finance Research Letters, 59*, 104779. https://doi.org/10.1016/j.frl.2023.104779 (R)〔collab 并购臂〕
- Zheng, H., & Mao, M. Q. (2024). Fintech mergers and acquisitions. *Journal of International Money and Finance, 143*, Article 103076. https://doi.org/10.1016/j.jimonfin.2024.103076 (R)

### 10.12 洗白/政策对齐/战略差异化 〔W・PA・SD 族〕

- Song, X., Hou, W., Ouyang, Z., & Hao, F. (2026). AI washing: Strategic disclosure and backlash. *Finance Research Letters, 95*, 109684. https://doi.org/10.1016/j.frl.2026.109684 (R)〔W 族最新锚〕
- Donelson, D. C., Kim, M. J., Kim, S. S., & Yip, M. A. (2025). *Strategic AI disclosures* (SSRN No. 5265257). https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5265257 (R)
- Gorovaia, N., & Makrominas, M. (2024). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. *European Financial Management, 31*(1), 427–462. https://doi.org/10.1111/eufm.12509 (R)〔washing_ratio 方法学〕
- Calamai, T., Balalau, O., Le Guenedal, T., & Suchanek, F. M. (2025). Detecting greenwashing: A natural language processing literature survey. arXiv. https://doi.org/10.48550/arXiv.2502.07541 (R)
- Liu, Y., Cao, Z., & Wen, F. (2024). Textual similarity between firm and government: Measurement and pricing. *Economics Letters, 241*, 111823. https://doi.org/10.1016/j.econlet.2024.111823 (R)〔PA 族最贴近先例: 中国政企文本余弦对齐〕
- Kalmenovitz, J., Lowry, M., & Volkova, E. (2025). Regulatory fragmentation. *The Journal of Finance, 80*(2), 1081–1126. https://doi.org/10.1111/jofi.13423 (R)〔监管文本测度→企业面板〕
- Fang, H., Li, M., & Lu, G. (2025). *Decoding China's industrial policies* (NBER Working Paper No. 33814). https://www.nber.org/papers/w33814 (R)〔中文政策文本 LLM 可量化〕
- Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. *Journal of Political Economy, 124*(5), 1423–1465. https://doi.org/10.1086/688176 (R)〔SD 族文本余弦经典〕
- Hoberg, G., & Phillips, G. M. (2025). Scope, scale, and concentration: The 21st-century firm. *The Journal of Finance, 80*(1), 415–466. https://doi.org/10.1111/jofi.13400 (R)〔⚠注册表注: 平行参照非直接背书〕
- Guzman, J., & Li, A. (2023). Measuring founding strategy. *Management Science, 69*(1), 101–118. https://doi.org/10.1287/mnsc.2022.4369 (R)〔strat_diff_n{N} 最近邻距离出处〕
- Hoberg, G., Phillips, G., & Prabhala, N. (2014). Product market threats, payouts, and financial flexibility. *The Journal of Finance, 69*(1), 293–324. https://doi.org/10.1111/jofi.12050 (R)〔strat_fluidity 出处〕

### 10.13 羊群/分歧/情感动态 〔HD・DA・TD 族〕

- Cookson, J. A., & Niessner, M. (2020). Why don't we agree? Evidence from a social network of investors. *The Journal of Finance, 75*(1), 173–228. https://doi.org/10.1111/jofi.12852 (R)〔disag_* 分歧分解框架〕
- Hirshleifer, D., Peng, L., & Wang, Q. (2025). News diffusion in social networks and stock market reactions. *The Review of Financial Studies, 38*(3), 883–937. https://doi.org/10.1093/rfs/hhae025 (R)〔HD 衰减建模〕
- Zhang, S., Miao, W., & Zhang, Y. (2025). Institutional investor diversity, herding behavior, and systemic financial risk: Evidence from China. *Risks, 13*(12), 243. https://doi.org/10.3390/risks13120243 (R)

### 10.14 多重检验/稳健性/可复现性 〔使用要点 FWER・§7 检验负担・确定性 gate〕

- Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. *Econometrica, 73*(4), 1237–1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x (R)〔FWER 直接方法锚〕
- Romano, J. P., & Wolf, M. (2016). Efficient computation of adjusted p-values for resampling-based stepdown multiple testing. *Statistics & Probability Letters, 113*, 38–40. https://doi.org/10.1016/j.spl.2016.02.012 (R)
- List, J. A., Shaikh, A. M., & Xu, Y. (2019). Multiple hypothesis testing in experimental economics. *Experimental Economics, 22*(4), 773–793. https://doi.org/10.1007/s10683-018-09597-5 (R)
- List, J. A., Shaikh, A. M., & Vayalinkal, A. (2023). Multiple testing with covariate adjustment in experimental economics. *Journal of Applied Econometrics, 38*(6), 920–939. https://doi.org/10.1002/jae.2985 (R)〔平行脉络补充参照〕
- Menkveld, A. J., Dreber, A., Holzmeister, F., Huber, J., Johannesson, M., Kirchler, M., Razen, M., Weitzel, U., … [百人合著] (2024). Nonstandard errors. *The Journal of Finance, 79*(3), 2339–2390. https://doi.org/10.1111/jofi.13337 (W; 作者 >20 人, 终稿按 APA 规则以 Crossref 全名单排)〔研究者自由度须显式披露 — 多臂稳健交付的顶刊依据 (v23 后部分梯子臂经 pair 表承接)〕
- Elliott, G., Kudrin, N., & Wüthrich, K. (2025). The power of tests for detecting p-hacking. *The Review of Economics and Statistics*. https://doi.org/10.1162/REST.a.1688 (W; 核验补刊出 DOI, arXiv:2205.07950)
- Brodeur, A., Mikola, D., Cook, N., … [百人合著] (2026). Reproducibility and robustness of economics and political science research. *Nature, 652*(8108), 151–156. https://doi.org/10.1038/s41586-026-10251-x (W; 终审改 DOI 链接; 作者 >20 人, 终稿按 APA "前 19 + … + 末位" 规则以 Crossref 全名单排)〔注册表落盘+确定性 gate 的可复现性背书〕

### 10.15 LLM/机器生成变量的下游推断 〔cw_ 列进回归的计量义务〕

- Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). *Large language models: An applied econometric framework* (NBER Working Paper No. 33344). https://doi.org/10.3386/w33344 (R/W 双源)〔无验证样本则估计可被模型选择驱动 — per-model 梯子的计量正当性〕
- Dell, M. (2025). Deep learning for economists. *Journal of Economic Literature, 63*(1), 5–58. https://doi.org/10.1257/jel.20241733 (R/W 双源)
- Battaglia, L., Christensen, T., Hansen, S., & Sacher, S. (2024). Inference for regression with variables generated by AI or machine learning. arXiv. https://doi.org/10.48550/arXiv.2402.15585 (R/W 双源)〔generated-regressor 推断修正 — 本面板消费者必引; ⚠SSRN 版标题变体不同〕
- Egami, N., Hinck, M., Stewart, B. M., & Wei, H. (2023). Using imperfect surrogates for downstream inference: Design-based supervised learning for social science applications of large language models. arXiv. https://doi.org/10.48550/arXiv.2306.04746 (R)
- Törnberg, P. (2024). Large language models outperform expert coders and supervised classifiers at annotating political social media messages. *Social Science Computer Review, 43*(6), 1181–1195. https://doi.org/10.1177/08944393241286471 (R)〔⚠跨域佐证非中文金融直接实证〕
- Gligorić, K., Zrnic, T., Lee, C., Candès, E. J., & Jurafsky, D. (2024). Can unconfident LLM annotations be used for confident conclusions? arXiv. https://doi.org/10.48550/arXiv.2408.15204 (R)〔低置信 LLM 标注可用性的间接支撑 (终审收窄, 非 D7 双口径直接背书)〕
- Hartley, E. (2025). Narratives to numbers: Large language models and economic policy uncertainty. arXiv. https://doi.org/10.48550/arXiv.2511.17866 (R/W 双源)
- Hansen, A. L. (2026). *Validating large language model annotations* (FEDS Working Paper No. 2026-020). Federal Reserve Board. https://doi.org/10.17016/FEDS.2026.020 (W)〔无金标准时的 LLM 标注验证 — κ/α 一致性设计〕
- Sarkar, S. K., & Vafa, K. (2025). *Lookahead bias in pretrained language models* (ICML 2025). https://openreview.net/pdf?id=fn9cJkB86T (W)〔LLM 前瞻偏差 — 历史语料时序效度披露义务〕
- He, S., Lv, L., Manela, A., & Wu, J. (2025). Chronologically consistent large language models. arXiv. https://doi.org/10.48550/arXiv.2502.21206 (W)〔前瞻偏差解法参照〕

