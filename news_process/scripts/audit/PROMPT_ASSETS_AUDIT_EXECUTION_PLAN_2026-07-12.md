# 全项目提示词资产两轮审计 · 整改执行计划（2026-07-12）

> **审计方法**：两轮多智能体评审（第一轮 6 个分簇深审 + 第二轮 3 个终审：P1 对抗复核 / P2 对抗复核 / 完备性扫描+手稿引用核对），合计 9 agents，全程只读零改动。
> **审计范围**（6 簇全覆盖）：① stage 21 主 prompt v8（`config/prompts/unified_cot.txt` + `tone_llms.py`）；② `validation/` 族（prompt_sensitivity / radius_sensitivity_llm / llms_human / llms_evaluation / tone_validation / entity_masking）；③ benefit_society 锚点/dimension_analysis/ncd_text_extractor/placebo + policy_alignment 锚文本；④ llm_peer_iv PEER_PROMPT + fintech_rating_prompt.jinja2 + llm_archive 归档链 + 嵌入 instruction 面；⑤ `LLMs_for_FinTech_dic/` 独立管道 + L&M 词典提示词；⑥ 横向（版本字面量矩阵 / temperature 纪律 / EOL / CLAUDE.md 铁律逐条核验 / 手稿引用一致性 / 治理基础设施）。
> **总盘**：P1 终判 4 项（M1–M4）+ P2 应修 14 项（S1–S14）+ P3/披露 10 项（D1–D10）；1 项第一轮 P1 被第二轮**实证推翻**（EOL 缓存风险）。
> **本计划为唯一权威执行清单；实施时逐项打勾，完成后在 §9 记录收口证据。**
> **2026-07-12 增补**：§10「稳健性缺口闭环 WP-R1..R5」（v8 三阶段测量的稳健性检验补全；四轮评审收敛：草案→三路评审[工程/方法学/铁律]→v2→对抗终验 7 处小修后 ok_to_merge）。S9/D8（整体）与 D7（仅实修部分）被 §10 吸收（原条目留指针；"实修部分"限定词只修饰 D7——其 docstring 文字部分仍留批次 F）。
> **2026-07-12 增补 2（用户决策）**：§11「v9 prompt 升级」——v8 冻结的效力范围收窄为**本计划（§1–§10）执行期内**；执行完毕后按 §11 流程升级 v9（草案→对抗评审 1 真方法学洞+7 遗漏耦合点修正后 ok_to_merge）。§0-1 铁律与 §4-1 已同步改写。**（本行"执行完毕后升级"的时点已被增补 3 翻转覆盖，以增补 3 为准）**
> **2026-07-13 第二次文档终审**（终审序号口径：第一次=两轮提示词审计自身的第二轮对抗终审，见 §7；本行起为对计划文档本体的历次终审）：三路并行终审（内部一致性 11 处+6 NIT / 事实锚点 52 项抽验全部到码到盘、承重锚点零走样、2 处转写漂移 / 完备性 4 承重+4 补记）全部修正并回灌本文档；关键裁定：变体 prompt_version 补传移入执行期（WP-R1.1 ③）、N2 升为人工窗口硬前置、批次 B 拆 B-1/B-2 两时点、G-v9-4 补 CLAUDE.md 同步条目。本计划自此收口，可执行。
> **2026-07-13 增补 3（用户决策，冻结时间轴翻转）**：**执行期内允许修改提示词**（经 §11 受控流程承载；v9 升级纳入本计划统筹推进，不再强制等 §1–§10 全部收口）；**计划执行完毕（§1–§11 全部收口、v9 落地）后，提示词进入终态冻结，严禁任何修改，无 v10 升级路径**。§0-1 / §11 定位与命名规范 / G-v9-0 已同步改写。
> **2026-07-13 增补 4（用户要求）**：新增 **§11.1-Q「v9 质量标准」十三条**——提示词修改须达到国际顶级期刊最高水平（设计六条硬闸 / 实证五条[非劣硬闸+优效目标+test-retest 补缺] / 评审两条[模拟顶刊审稿+终局标准]）；经对抗评审修正 7 处（含拆除一个可被派生强度博弈的伪硬闸，换为"过线集合包含+扰动强度锚定+先锁后算"）后定稿。G-v9-1 出口条件、G-v9-3 ②、§11.5-7 已同步。
> **2026-07-13 第三次文档终审（增补 3/4 之后全文复核）**：三路并行（时间轴一致性 8 处+4NIT / 11.1-Q 新锚点 12/12 到码零走样+可执行性 5 处 / 上轮 21 修回灌 21/21 在位+完备性 1+3）——全部修正已回灌：增补 3 漏改的 §4-1/D1/WP-R1.5(i)/两条零漂移验收时序界标、§9 补 §11 收口两行并清 N2 残留、v8/v9 **两笔 36k 变体费用口径**（禁合并认领）、test-retest **rep 编码进 prompt_version 后缀**（主缓存无 tag 槽，同键裸调用=假一致率）、G-v9-0 ④ 限定为 G-v9-4 前、CLAUDE.md 终态冻结声明扩为**全部提示词资产**、§5 补 v9 通道行、memory 三处过期表述同步清理。
> **2026-07-14 增补 5（用户要求）**：**所有修改必须详细具体反映到注释和日志中**——新增 §0-5「注释与日志同步纪律」（原子三件套：改代码+清理会变谎话的既有注释+更新运行时日志；两类触点分治；banner 最高危；跨语言字面量不豁免；计算点与文字点原子打包）+ **§12「注释与日志同步台账」**（逐条到码 grep 产出：批次 A / 批次 B-D 合并[表内含跨批次 N2 项] / 批次 F 与 §11 前置补遗 / §10 / G-v9 五张触点表，含多处"改完代码就变谎言"的既有 docstring、2 条与实际行为相反的 banner、radius :584 每次运行必打的 scaffold 假信息等）；§6-8 / §11.5-8 验收同步。
> **2026-07-14 第四次文档终审（增补 5 之后收口检）**：两路并行——§12 逐行到码复核（~60 处全部命中、摘录忠实、零语义反转）+ 全文一致性终检。修正 8 处：头部日志链时序归位（本条即证）、§12 补 N1/D5/V9-PRE-1 三行与 do.tmpl 完整路径（11 份同名文件歧义）、§9 补 §12 打勾证据行、"五组表"计数与 N2 归属措辞、新增脚本 docstring 范式统一。**本计划自此终版收口，可执行。**
> **2026-07-14 第五次文档终审（换新视角复核）**：两路并行——冷启动可执行性模拟+内部交叉引用逐一解析（全部 §X-Y/WP/Gate 引用命中、§9↔§5 一一对应、零死锁零矛盾指令、**0 确证问题**）+ §12 之外正文 25 组代码锚点独立抽验（22 组逐字命中；1 项 agent 误报经主会话回验推翻——manifest.py 双组行号本就正确）。修正 6 处（全部措辞/行号精度级，零实质缺陷）：WP-R4.1 `:60` 行号拆分（CACHED_RADIUS 常量 vs parquet 读取 :352/:508 两处真实位置）、§11.4-#1 "无硬编码回退"改写为准确表述（回退='v0' 哨兵非旧版本号）、Q-B #10 caching.py 行号 292-297→291-295、头部 S9/D8/D7 吸收措辞限定词归位、批次 E 顺序行改"硬顺序仅两条"防 S9 修字被误等生产窗口+补抽样帧先于 radius 播种、WP-R4.3 "三层协议"展开为三要素。**终版收口判定维持：可执行。**
> **2026-07-14 执行记录（用户完全授权后当日实施）**：本机可执行范围全部完成并按批次提交——批次 A=d06ce8b3 / B-1=2fcc56e1 / C=23bf4229 / D+WP-R3=1fea954d / E前置(S9+WP-R1.1+R1.2)=1eca8523 / F=9cda7d84 / V9-PRE-1=18d2619d（收口证据与执行中四项新发现[归档 mock 污染 146 条清洗、M1-P0 gitignore 缺口、N2-P1 编排器死锁、S14-P1 模板未入库]详见 §9）。批次 B-2/E 付费播种、人工窗口、v9 起草按本计划前置条款合法延后（§9 逐行登记）。质量流程：9+2 路实施 agent → 第一轮三路对抗评审（§12 台账逐行/全 diff 对抗/完备性五子路）→ 修正 → 终审 R2 双路 → 修正 → 全量 pytest A/B 差分 0 新增红灯（21↔21 与基线逐条相同）。

---

## §0 全局铁律（实施任何 WP 前必读）

1. **提示词修改政策（用户决策 2026-07-13，时间轴翻转）**：**执行期内允许修改提示词**——但一切进缓存键的 prompt 字节（`unified_cot.txt`[v8]、`llm_peer_iv.PEER_PROMPT`、`LLMs_for_FinTech_dic/config.py` 生成/判别 prompt、benefit 10 对锚点句、jlm 5 对锚点、`ncd_text_extractor.EXTRACTION_PROMPT`）的修改**必须经 §11 受控流程承载**（当前指向 v8→v9 主 prompt；其余带独立版本门的 prompt 如需修改，各自走同级受控流程且须在计划执行完毕前完成）。这是**工程约束而非禁令**：改一个字节 = 对应缓存全 miss（stage 21 三轨 ≈13 万条 / peer / 词典管道各自付费重跑），未经流程的"顺手改一字"仍绝对禁止（防误废缓存与 golden）。§1–§10 各条目对 prompt 缺陷的修复方向不变（改文档/解析器/测试/守卫/披露）——prompt 本体的修复统一汇入 §11.1(a) 一次做掉，不零敲碎打。**计划执行完毕（§1–§11 全部收口、v9 落地）后：提示词进入终态冻结，严禁任何修改，无 v10 升级路径。**
2. **审计核验通过的硬事实（勿再质疑，直接引用）**：
   - v8 自 2026-05-17（450c1aa7）起 git 可证零字节触碰；prompt 构造 SSOT = `tone_llms.iter_article_track_prompts` 全仓唯一（3 个消费点同一函数对象）；16 个 JSON 字段 prompt↔解析器契约闭合；`encode.LLM_CLASS_SPEC` 与 `_LLM_CLASS_SPEC_FALLBACK` 逐字节相同。
   - temperature=0.0 单源恒定（例外均有记录：LLMs_dic 生成阶段刻意默认温度+rep 进键、ERNIE 1e-10 死配置、诊断脚本）。
   - `v8-2026-05-17` token 全仓单一拼写零变体（2026-07-13 复扫：git 跟踪域 296 处/17 文件；其中手写源头 30 处/15 文件，其余为 codebook 生成物——引用该计数时必须标注口径，见 §11.4-#6）；PEER_PROMPT sha 冻结锁健康；`_lg` 缓存键 `('text-embedding-3-large','v1-2026-06-27-emb3large')` 三处硬锁一致。
   - 验证族缓存双保险隔离（独立 `_llm_cache_validation.db` + prompt 文本必异）；离线守卫链（`LLMCacheMissError` / 嵌入 `RuntimeError`）主路径健全。
   - **【已推翻】EOL/autocrlf 不构成缓存风险**：`core/config.py:123` 文本模式 universal newlines，磁盘 CRLF 进内存恒归一 `\n`，缓存键与 checkout 行尾无关（实测内存 prompt `contains CR: False`）。`.gitattributes` 无需加 eol 规则。
3. **指纹双口径声明（M1/M2/S1 落地时必须统一写明）**：公示指纹 `0430ba3c…` = `unified_cot.txt` **raw 磁盘 CRLF 字节**（含版本头）sha256；缓存键使用的是 **LF 归一内存字节**（其 sha = `14952b06…`）。两口径都合法，但所有锚点/gate/复现文档必须显式标注自己用哪个口径，否则复算必撞口径墙。
4. 共享树纪律照旧：**by-name stage、绝不 amend、绝不 --no-verify**；`data/processed/v3_5_1_constants.json` 当前工作树已有未提交改动（正是 M1 的案发现场），处理前先按 §1-M1 迁移，勿盲目 checkout 恢复。
5. **注释与日志同步纪律**（用户要求 2026-07-13：所有修改必须详细具体反映到注释和日志中；触点已逐条 grep 成 §12 台账）：
   - **每个"改行为"的条目 = 原子三件套**：改代码 + 清理"会变谎话的既有注释/docstring"（§12 按条目列全了将失真的现存文字——这不是缺注释，是**改完代码后留下来会变成谎言的旧文字**，必须同批删改）+ 更新运行时日志字面量。修复注释统一用项目既有 fix-tag 范式：`# fix(<台账编号如 S7/M1/WP-R1.1②>, <日期>): <问题一句话> — <解法一句话>`（镜像 `tone_llms.py:749` omni-g-tonellms-04 的写法）。
   - **两类触点分治**：硬编码字面量（版本号/路径/口径写死在字符串里，如 `codebook.py:1487` notes、`.do.tmpl` 的 `display as error`、scaffold 警告 banner）必须逐条手工改，§12 已列全；变量插值（如 manifest 用 `%s` 打印 anchor）只需确认变量本身更新，勿逐条改文案。
   - **运行时必打印的 banner/log 是最高危类**：过期注释只误导开发者，过期 banner 每次运行都输出、会持续污染日志并误导日志审计与下游（本项目 53 处 banner 版本陈旧的教训）。每批收口前跑一次冒烟（输出到 scratchpad）并人工目检新日志零过期口径。
   - **跨语言字面量不豁免**：Stata `.do.tmpl` 的 `display` 输出、yaml 头注、xlsx 表头/统计列名均属用户可见输出，纳入 grep 范围（勿只扫 .py）。
   - **计算点与文字描述点打包**：凡总判定/口径类改动，"计算它的那一行"（唯一）与"描述它的全部注释/日志"（N 处）必须在同一 commit 内原子完成——先例教训：`prompt_sensitivity` 的"三轨 AND"语义散布在 1 个计算点 + ≥6 处文字，只改计算点 = 代码已切换而日志仍自称旧口径（= "文档陈述与实测方向相反" 教训的复现模式）。

---

## §1 必须修（M 组，有严格顺序依赖：M1 → M2；M3/M4 独立可并行）

### M1【P1】prompt_v8_sha256 sidecar 写/读路径双脑分裂 + 权威值迁移

- **事实**：写方 `pipeline/panel/encode_collab.py:1260` 用 **cwd 相对路径** `'data/processed/v3_5_1_constants.json'`；读方 `pipeline/llm_archive/manifest.py:190-211` 经 `load_config()['paths']['output_dir']` 解析到 **news_process 包内绝对路径**。某次以 news_process 为 cwd 的运行新生了第二副本 → 现状双副本分裂：repo 根副本（git 跟踪，2026-07-12）`prompt_v8_sha256='0430ba3c…'`、`median_amb_d0=0.005325`；news_process 副本（git 未跟踪，2026-07-10）sha=**null**、median=**0.006484**。`0430ba3c` 的唯一来源 = repo 根 commit `aba2196c` 人工一次性锚定，runtime producer 缺席（`encode.py:2129` 恒传 None）。
- **改法**（单点收敛）：
  1. writer 的 `sidecar_path` 改为与 `manifest._resolve_sidecar_path` **同源**（config `output_dir` 解析），消灭 cwd 依赖；
  2. 一次性把 repo 根副本的权威值（sha `0430ba3c…` + median 0.005325 + 全部字段）迁移到 config 路径副本；repo 根副本退役（git rm 或留 tombstone 注释）；
  3. （可选加固）给 `apply_v3_5_1` 的 callsite 补 runtime producer：读 `unified_cot.txt` 计算 raw 字节 sha 传入，消灭"锚点靠人工一次性播种"。
- **⚠ golden-safe 前提**：迁移必须保留根副本的 **median 值**（clarity 二值化列消费该阈值）；只切路径不迁值 → 面板漂移 = **非** golden-safe。
- **实施首步指引**（终审补）：① 先 `git diff -- data/processed/v3_5_1_constants.json`（repo 根）确认当前**未提交改动**的字段级差异——权威值以**盘上工作树**为准（sha `0430ba3c…` + median 0.005325 均已实读验证在工作树中）；该未提交改动即本条案发现场，勿盲目 checkout 恢复也勿先行提交；② repo 根副本退役前，先 `grep -rn "v3_5_1_constants.json"` 全仓列消费点清单（含 migrate 脚本/测试/codebook.py:1487 读取路径）逐一确认无 cwd 相对读取残留后方可 `git rm`。
- **验证**：`manifest._resolve_sidecar_path()` 实读返回 `0430ba3c…`；`pytest -k "llm_archive or v3_5_1"` 绿。

### M2【P1】llm_archive manifest 陈旧（28 个 jsonl 未登记，`fetch_llm_archive.py` 现红退出码 3）

- **事实**：`data/llm_archive/manifest.json` 生成于 2026-05-30，仅登记 5 个 jsonl；`responses/` 实有 33 个；实跑 `verify_manifest()` = `(False, 28 项未登记)`。Zenodo 冻结包（10.5281/zenodo.20453766）只覆盖前 5 文件。
- **改法**：**必须在 M1 之后**跑 `write_manifest()` 重登记（否则从 null 副本读到 `prompt_sha256=None`，把现存密码学锚降级掉）。同时处置：① `archive_frozen_date='2026-05-18'` 语义已漂（归档持续追加）→ 改滚动语义或披露；② 后续 28 文件的外部托管（Zenodo 增补）列入生产收口清单（**M0 门内兑现这 28 文件；§11 G-v9-4 的 Zenodo 版本化 deposit 仅覆盖 v9 新增归档，非同一笔，勿双重认领**）；③ NIT 顺带：`prompt_version_anchor='v8'` 人读 token 与完整 token `v8-2026-05-17` 对齐。
- **验证**：`verify_manifest()` = OK；`fetch_llm_archive.py` 退出码 0；重生 manifest 内 `prompt_sha256='0430ba3c…'` 非 None。manifest.json 不入 golden，安全。

### M3【P1】tone_validation 人工验证盲表构念错位（人工标注启动前的免费窗口，标完不可逆）

- **事实**：`validation/tone_validation.py:729-787` 盲表 `blind_cols` **缺 `target_bank`**（盘上 `09_sentiment_verify_full_blind_A.xlsx` 实读确认），编码指南三轨全写"整体语调判断"；而 LLM 构念 = "仅对【target_bank】的情感 + 同行抗污染"（`unified_cot.txt:20-21`）。docid 为文章×银行粒度非唯一 → 同文两行人工不可区分 → κ/效标效度被结构性压低且不可归因。对照 `llms_human.py:147` 盲表白名单**含** target_bank（注释明言编码员须知道目标银行）。
- **改法**：① `blind_cols` 加 `target_bank`（实体匹配产物非模型预测，不破盲）；② 三轨 coding_note "整体语调"→"仅对目标银行的情感倾向"；③ **同步** `llms_human.py:171` 情感指南同款措辞（两处必须一致）；④ 重生盲表 xlsx（$0 纯 Excel）。不动 parquet/缓存/golden。
- **验证**：重生盲表列含 target_bank；`pytest -k "tone_validation or llms_human"` 绿；与 `HUMAN_ANNOTATION_PROTOCOL_2026-07-03.md` T2 口径对读一致。若与 §10 WP-R2 同窗口落地，61 工作台与 09 盲表只重生一次（防两次重生浪费与版本混淆）。

### M4【P1】10 个手稿文件「平局→undefined」语义与生产代码相反（投稿前必修）

- **事实**：5 篇 × 2 语种（bank_fintech_tone / benefit_society / brokerage_network / llm_peer / strategic_diff 的 `papers_assets/*/drafts/{zh,en}/manuscript.tex`，行号见审计台账 §8-F1）写"三方平局记 undefined/missing"；生产 `tone_llms.py:1774` 已按 2026-06-23 用户决策 promote `tie_strategy='neutral'`：80 轮 tie-retry 后仍平 → 保守降级"中性"，verified 轨不再产 `llm_undefined`。手稿成稿（2026-07-03）晚于决策却写入被逆转前的规则。
- **改法**：10 处手稿改为真实语义："relevance 未过 → 情感缺失（此半句原本就对）；三家平局/空票 → 最多 80 轮确定性重试，仍未破局则保守编码为中性"。zh/en 措辞对齐。纯 .tex/.md 文档改动，golden 零涉。
- **验证**：全 papers_assets grep `undefined` 复扫零残留错误语义；与 `config/sentiment.yaml:18`（retries=80）数字一致。

---

## §2 应修（S 组，全部 golden-safe，可一批或分批落地；无相互依赖，S1 建议随 M1/M2 同批）

| #   | 严重度 | 位置                                                                            | 缺陷 → 改法                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| --- | ------ | ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| S1  | P2     | `tests/`（新增）                                                                | v8 冻结无字节 gate：新增 frozen-hash 测试，锁`unified_cot.txt` **LF 归一** sha（`14952b06…`，镜像 `test_peer_prompt_frozen` 的 `.replace('\r\n','\n')` 模式防跨 EOL 误红），并断言 sidecar 锚 `0430ba3c…` 与实文件 raw 字节复算恒等（双口径各一条断言，见 §0-3）。可选加一条"CRLF/LF 两份 tmp 模板 → `prompt_template` 相同"的 EOL 免疫回归测试                                                                                                                        |
| S2  | P2     | `LLMs_for_FinTech_dic/00_LLMs_for_dic.py:1286`                                  | 词表阈值双口径：`total_score >= len(JUDGE_MODELS)*0.5`（=≥4，含平票）→ `>`（严格多数=≥5，对齐发表词表 1506 实证口径）+ 注释锚定论文口径。发表词表本身未被污染（xlsx 实测 ≥5=1506=fintech_dict.json 词条数），阈值不进缓存键                                                                                                                                                                                                                                            |
| S3  | P2     | `pipeline/features/benefit_society.py:548-579`                                  | 冻结 center sidecar 守卫只锁 model_id：写入侧补`anchor_sha256`（锚词 canonical 拼接 sha）+ `text_pipeline_version` 两字段；读取侧双方都存在且不匹配 → fail-loud；**旧条目缺字段 → warning + 回填字段但不改 center 值**（直接 fail-loud 会当场崩 stage 40 = 非 golden-safe）                                                                                                                                                                                            |
| S4  | P2     | `FinTech_Dictionary_LLMs_Paper_Final.md:69-114`                                 | 论文"逐字引用"的生成/判别 prompt 与`config.py:196-220` 四处实质不一致（约100个/银行限定/参考词汇行/末批"以下14个"）→ **改 md 引文为代码逐字**，禁反向改代码 prompt（词典管道缓存以 prompt 为键）                                                                                                                                                                                                                                                                       |
| S5  | P2     | `papers_assets/bank_fintech_collab/manuscript_{zh,en}.md:35,57`                 | 杜撰引用组合 "Wickert & Zajac" ×4 → 改为**Westphal & Zajac (1994/1998 ASQ)**（prompt 实物、P3 手稿、refs.bib 均为后者；前者无 refs 条目支撑）                                                                                                                                                                                                                                                                                                                          |
| S6  | P2     | `papers_assets/benefit_society/drafts/{zh,en}/manuscript.tex`（4 处）           | 锚点翻号披露编号错误："第 9 对"→按代码配对序号实为**第 3 对**（信贷质量维度；`logs/40_build_panel.log:1063` "负极句 #3" 实证；混淆源=代码注释维度圈号"⑨"）。披露内容为真，仅编号不可复现                                                                                                                                                                                                                                                                               |
| S7  | P2     | `pipeline/panel/llm_peer_iv.py:420-448`                                         | 归档顺序"先 cache.put 后 archive"未镜像 omni-g-tonellms-04 → 机械镜像`tone_llms.py:749-795` 的 `_archive_ok` 模式（archive 失败则跳过 put）；同批补 `_is_cacheable` 写入闸（该通道亦缺）。纯副作用顺序，产物字节零漂移                                                                                                                                                                                                                                                 |
| S8  | P2     | `scripts/migrate/v7_wz_audit.py:100-101`                                        | 在线路径`cache.put` 无写入闸直写生产库（WP-A3 只堵了离线）→ put 前加 `_is_cacheable_llm_response` 校验 3 行；顺带修 docstring "v7"名实漂移与死 fallback `'v7-2026-05-14'` 注释化；**顺带加弃用声明**"本工具仅对 v8 语料/缓存有效，v9 后运行须 checkout 历史 commit"（预先兑现 §11.4-#15，v9 时仅复核声明在位）                                                                                                                                                         |
| S9  | P2     | `validation/prompt_sensitivity.py:215/283/360/404 + reason 字段`                | 4 变体头部"两项/两阶段"vs 正文三任务（v8 升级漏改）+ 2 个`*_reason` 缺"须引用文章具体内容"→ 改变体文本。**成本**：变体库增量重跑（≤36,000 请求），但盘上结果 `passed=False` 本来就必须在生产语料重跑——随生产重跑窗口一并生效，边际成本≈0。同批：热力图补 `call_failure` 掩码（4 行）+ undefined 平局行掩码或报 `n_undefined_excluded`；docstring 阈值/retries 与 config 现值对齐（0.70/0.70、retries=80）。**→ 修复与重跑设计整体由 §10 WP-R1 吸收，本条不再单独收口** |
| S10 | P2     | `pipeline/features/benefit_society.py:268-280`                                  | `_lg` 的 `except Exception` 吞离线 `RuntimeError` → 静默全 NaN 家族。except 内检测 `NEWS_PROCESS_LLM_OFFLINE` 真值时 re-raise（3 行）；在线降级行为不变                                                                                                                                                                                                                                                                                                                |
| S11 | P2     | `tests/test_benefit_dimension_tracks.py` 等                                     | ①`DIMENSION_INDICES` 纯位置耦合 → gate 补 10 条锚点内容关键词断言（重排即红）；② 主 10 对锚点无冻结锁（对照 PEER_PROMPT/jlm 均有）→ 补 `ANCHORS_SHA256` 冻结测试。均纯测试侧                                                                                                                                                                                                                                                                                           |
| S12 | P2     | `LLMs_for_FinTech_dic/00_LLMs_for_dic.py:599` + `02_analyze_log.py:108-110,201` | ①`int(item.get("score",0))` 裸转换会炸穿判别主循环 → try 包裹跳过坏项；② 日志分析器漏计"达到最大重试次数"型失败（正则失配）+ 硬编码 `/26` vs `DOMAINS=1` → 放宽正则 + `len(DOMAINS)`。同族披露：判别失败与真负类同码 0 的 latent 缺口（本轮 xlsx 实测 0 NaN 未污染）在方法学文档记一句                                                                                                                                                                                 |
| S13 | P2     | `config/benefit_society_placebo_keywords.yaml:73`                               | placebo「智能柜员机」∈ fintech_dict 精确交集（构念泄漏，方向保守）→ 二选一：删词+重生 stage 80 sidecar（主面板零触），或保留+Table A10 注记披露；**无论哪个**都补 gate 测试 `placebo ∩ fintech_dict ⊆ 已披露白名单` 防词典更新再漂                                                                                                                                                                                                                                     |
| S14 | P2     | `papers/_common/AI_DISCLOSURE_TEMPLATES.md:81`                                  | 披露模板承诺的`prompt_v8_sha256` 锚现为 null → 随 M1/M2 收口后自动兑现；模板中补一句指纹口径声明（§0-3）                                                                                                                                                                                                                                                                                                                                                               |

---

## §3 可披露代替修 / P3 批（低优先，可攒批处理）

| #   | 位置                                                                                                                                                                  | 处置                                                                                                                                                                                                                                                                                                                                                                                                 |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| D1  | `unified_cot.txt:84`                                                                                                                                                  | prompt 内悬空指针`docs/methodology/innovation_collab_mode_framework.md`（docs/ 已随 1698bda5 删除）。**v8 字节不动（prompt 侧悬空引注的删改统一走 §11 v9，见 §0-1 与 §11.1(a)）**；补建该文档（从 git history 恢复或重写**该文档自身的** §2 cross-tab 框架节，非本计划 §2）——该文档服务 **v8 历史复现包**，与 §11 v9 删除该悬空引注**双轨不冲突**（v8 缓存/归档永久引用 v8 字节，文档仍需存在）                                                             |
| D2  | CLAUDE.md 嵌入架构段 / SWAP 计划 / manuscript 数据附录                                                                                                                | Qwen3-Embedding 刻意零 instruct 前缀的两句话依据（对称相似度任务；官方前缀面向非对称检索；前缀已冻结为缓存键语料）。**绝不加前缀**（=嵌入缓存全废+golden 全漂移）                                                                                                                                                                                                                                    |
| D3  | `papers/benefit_society/ncd_text_extractor.py`                                                                                                                        | 四处捆绑进**D4 解禁 checklist**（接真 API 前）：① JSON 解析失败不 put/put 前校验；② parsed=None 时 status≠"ok"；③ 模型 ID 修正（`claude-opus-4-5-20251001`→`…1101`，`gemini-2.0-pro` 以接线时 API 实况为准）；④ 统一缓存键口径叙述（:17/:397 称键含 temperature vs :489 实际键 `(model_id, pdf_sha256, prompt_version)` 不含——三处矛盾择一改齐）。现全 provider stub，零运行时影响                   |
| D4  | `config/prompts/fintech_rating_prompt.jinja2` + `scripts/fintech_rating_example.py`                                                                                   | 双死代码互漂（三处文本差 + docstring "5 列"vs 4 属性）：example 改为渲染 jinja2 模板消灭副本，或两文件头注 SSOT 指向；若未来接线必须补`# version:` 头（现 `.jinja2` 被 check_prompt_headers 豁免 → 会落 v0 命名空间）                                                                                                                                                                                |
| D5  | `core/dag.py:199`、`pipeline/filtering/policy_alignment.py`（15/16 混用 6 处）、`validation/` 注释（stage 13/14 物化归属）、`radius_sensitivity_llm.py`（35/65 混用） | 重编号注释残留一次机械批改；**优先修 SSOT 文件 `core/dag.py:199` 一处**。纯注释                                                                                                                                                                                                                                                                                                                      |
| D6  | `LLMs_for_FinTech_dic/test_claude_diag.py` + `01_test_models.py`                                                                                                      | `test_` 前缀 + 顶层付费副作用：改名 `diag_claude.py` 或包 `if __name__`（主 sweep 因 testpaths 免疫，目录内裸 pytest 才触发）；`01_test_models.py` 同款处置——两脚本均直连 API 绕过缓存与 `LLMS_DIC_OFFLINE` 守卫，加 `__main__` 守卫时顺带接入离线开关检查（或显式注释"诊断脚本刻意绕守卫，仅手动在线使用"二选一）                                                                                   |
| D7  | `validation/radius_sensitivity_llm.py`                                                                                                                                | scaffold 三不闭合（`--radii` 死参数 / precheck 缺 DEEPSEEK key / 未来写生产库与 W4 隔离决策冲突）→ 分工：**本批（批次 F）仅改 docstring 中 cache 目标的文字表述**为 `_llm_cache_validation.db`（纯注释）；三不闭合的**代码级实修**（--radii 接线 / precheck 补 key / 写入目标代码切 validation 库）与真实 launch 实现全部由 §10 WP-R4 吸收，两处不构成重复打勾                                       |
| D8  | `validation/eval_reports/prompt_sensitivity_results.json`                                                                                                             | 现状`passed=False`（subst κ 最低 0.29）——论文任何"对 prompt 措辞稳健"声明前必须生产重跑或如实披露。**→ 由 §10 WP-R1 吸收（生产重跑 + 预登记判定协议 + 决策树）**                                                                                                                                                                                                                                     |
| D9  | `config/dicts_excel/Loughran-McDonald/`                                                                                                                               | LM 词典 prompt 级复现闭环缺失（`_work/` 目录不在仓、逐批实际 prompt 未存档、提示词.txt 仅为任务书）→ 在审计报告 md 补一节如实披露证据链现状；无法事后补造                                                                                                                                                                                                                                            |
| D10 | NIT 批                                                                                                                                                                | `caching.py` docstring v6 示例、`27_benefit_*_t2v*.sidecar.json` 残影清理、`jlm2026_chinese_anchors.yaml:91` t2v 尾注、codebook `F110:207` 锚点示例句"了"字与设计规则相悖、`llm_peer_iv` "最多10家"软约束已披露维持、`LLMs_for_FinTech_dic/calculate_kappa.py:33-34` `P_e==1` 分支返回标量而正常路径返回三元组（调用方解包必 TypeError，latent 边界）、preflight 探针/(_replan_v5 证据脚本) 维持现状 |

---

## §4 明确不修清单（决策记录，防后人重提）

1. **v8 prompt 全部文本级 NIT 不在 §1–§10 各条目内零敲碎打修**（悬空指针 D1 走补文档、confirmed_bank 零消费、"大数据风控"跨类示例、空 co_mentioned 括号、false 分支不对称[sentiment_reason/confidence 无 false 时指示]、Gomber 2017/2018 引注口径）——v8 字节保持不动（修改仅由 §11 受控流程承载，见 §0-1 增补 3 口径），解析层均已兜底，v9 落地前一律走方法学披露；**全部统一汇入 §11 v9 受控窗口一次做掉**（= §11.1(a) 内容来源清单）。
2. **`.gitattributes` 不加 eol 规则**——EOL 风险已被实证推翻（§0-2），且"不写 eol"是有注释的 V7 刻意决策。
3. **变体 prompt 的"漂移"中属敏感性设计者不动**（V1–V4 措辞差异本身是被测对象）；只修 S9 那种"意外残留"。
4. **placebo 删词与否二选一后不再反复**（S13）；「智能柜员机」构念上双属，两个处置都可辩护。
5. **LLMs_dic 生成阶段非零温度不改**——多样性采样刻意设计，rep 序号已进缓存键。

---

## §5 实施顺序与批次建议

```
批次 A（复现账本链，先后依赖）：M1 → M2 → S1 → S14        [同一 commit 序列]
批次 B（人工标注窗口，两个时点）：B-1 M3 装置修复+09/61 盲表重生 [立即，本机 $0]
                              B-2 §10 WP-R2 生产盲表生成 [⚠ 前置=生产 stage 21 数据到位，
                              T=2 上生成则四格×100/每维≥300 无从谈起；与 B-1 协调只重生一次]
批次 C（手稿层/文档，投稿前）：M4 + S5 + S6 + S4 + §10 WP-R5 [纯文档]
批次 D（代码 golden-safe 批）：S2 S3 S7 S8 S10 S11 S12 S13
                              + §10 WP-R3 proxy 构造($0)     [每项独立可回退]
批次 E（生产 T=18 付费窗口，M0 门）：§10 WP-R1(⊇S9+D8) + WP-R4(⊇D7)
                              前置=生产 stage 21 播种完成；硬顺序仅两条：
                              ① S9 修字+WP-R1.1 ②③ 先于变体 36k 播种（修字 $0 且与
                              主播种无耦合，可提前任何时点做，勿因本行误等生产窗口）；
                              ② WP-R1.2 抽样帧固化先于 radius 9k 播种（WP-R4 共帧）
批次 F（低优攒批）：D1–D6、D7(docstring 部分)、D9、D10、N1
人工窗口（跨批次）：N2 防覆写机制[⚠ 硬前置，人工填写启动前必须先落，勿按低优攒批理解]
                  → WP-R2 人工填写 → κ 收口 → WP-R3 三角闭环收口
v9 通道（跨批次，增补 3 统筹推进）：(a)/(c) 起草+G-v9-1 评审+V9-PRE-1 可立即开始；
                  G-v9-2 pilot 付费须待 G-v9-1 出口+预登记 commit+用户批准（帧② 另需人工窗口收口）；
                  G-v9-4 重锚须待批次 A 收口（G-v9-0 ④）；付费均过 M0
```

- 批次 A/B-1/C/D 全部本机可完成、$0、golden-safe（S3 按"回填不 fail"设计、M1 按"迁 median 值"设计）；批次 B-2 依赖生产数据到位（机器侧仍 $0，人工时间另计）。
- 批次 E 属付费重跑，挂 **M0 审批门**之后与生产语料窗口合并。
- 每批完成后跑 `pytest -m fast` + 相关 gate；批次 A 后额外跑 `python -m news_process.scripts.audit.verify_stage21_cache_coverage` 与 `verify_manifest()` 双绿。
- 提交纪律：by-name stage、每批新 commit、message 引用本计划文件名与条目号（如 `fix(prompt-audit): M1+M2 sidecar 同源化+manifest 重登记`）。

## §6 验收标准（全部满足即收口）

1. `verify_manifest()` OK 且 `prompt_sha256≠None`；`fetch_llm_archive.py` 退出码 0。
2. 新增 frozen-hash gate（S1）与 anchors gate（S11）、placebo 交集 gate（S13）常绿。
3. 盲表含 target_bank；两处代码指南（tone_validation 三轨 coding_note 与 llms_human.py:171）口径一致，且与 HUMAN_ANNOTATION_PROTOCOL T2 对读一致（M3）。
4. papers_assets 全量 grep：无 "undefined 平局" 错误语义、无 "Wickert & Zajac"、锚点编号=第 3 对。
5. `pytest`（repo 根全量）0 新增红灯（baseline-stash A/B 差分口径）。
6. 面板/dta 字节零漂移（除 S13 若选"删词重生 80 sidecar"仅该 audit sidecar 变；**本条为 G-v9-4 受控全量重生前口径，重生后以新 golden 为基线复核**）。
7. 批次 D 各代码项（S2/S3/S7/S8/S10/S12）**各配 ≥1 条专属断言**方可打勾（终审补：这些条目原缺专属验收，仅靠 `pytest -m fast` 泛化兜底不足——如 S3 三分支单测、S10 离线 RuntimeError 穿透单测、S7 镜像 tone_llms 侧 omni-g gate）；D1/D5 收口配 grep 复扫式验证；N1 二选一后指定复跑的模板测试。
8. **注释/日志同步（§0-5 纪律 + §12 台账）**：每批 commit 前按 §12 对应分组逐行打勾；每批收口跑一次冒烟（输出到 scratchpad）并人工目检新日志零过期口径（重点：运行时必打印的 banner/警告类字面量）。

## §7 审计台账指针

- 第一轮 6 报告 + 第二轮 3 报告全文见本会话 agent 输出（要点已全部并入上文条目）；关键实证数字：v8 sha 双口径 `0430ba3c`(raw)/`14952b06`(LF)、变体库 53,655 条/125MB、manifest 28 项未登记、LLMs_dic ≥4=1738 / ≥5=1506 / 全票=870、placebo 交集恰 1 词、`v8-2026-05-17` 全仓零变体（计数口径见 §0-2 与 §11.4-#6）。
- 被推翻项存档：P1-B（EOL/autocrlf 缓存风险）——`core/config.py:123` universal newlines 实证免疫；勿再基于"缓存锚定 CRLF"做任何决策。

## §8 附：发现↔手稿行号台账（M4/S5/S6 精确定位）

- **F1 平局语义（M4）**：`bank_fintech_tone/drafts/en/manuscript.tex:334,356-357`；`zh:245-246,262`；`benefit_society zh:195 / en:288`；`brokerage_network zh:248 / en:349`；`llm_peer zh:203 / en:261`；`strategic_diff zh:237 / en:320`。
- **F2 杜撰引用（S5）**：`bank_fintech_collab/manuscript_zh.md:35,57`；`manuscript_en.md:35,57`。
- **F3 锚点编号（S6）**：`benefit_society/drafts/zh/manuscript.tex:235,502`；`en:340-341,722`。

## §9 收口记录（实施时填写；2026-07-14 执行完毕批次已回填，全程两轮结果评审+终审 R2 双路）

- [x] 批次 A（M1/M2/S1/S14）：commit **d06ce8b3**，verify 双绿证据 = verify_manifest()=(True,[]) + fetch_llm_archive EXIT=0 + verify_stage21_cache_coverage 0 miss + 批次相关测试 178 绿。**执行中发现并同批收口**：① M1-P0（终审 R2 确证）——config 路径被 news_process/data/ 整目录 gitignore 吞，迁移后冻结 sidecar 零跟踪副本 → .gitignore ** 化 + negation 例外恢复跟踪（git 识别为 rename 92% 保血缘）；② 归档 mock 污染——test_sentiment_tie_retry 缺归档隔离，自 2026-06-24 起 146 条 m1/http://x 测试记录泄入生产 append-only 归档（16 文件混入，8 纯 mock 文件）→ 记录级清洗（备份于会话 scratchpad）+ 根因测试补 _LLM_ARCHIVE_AVAILABLE 隔离 + manifest 重登记 26 文件/197,247 条；Zenodo 冻结 5 文件（05-25~29）不涉；③ S14-P1——AI_DISCLOSURE_TEMPLATES.md 被 papers/**/*.md 规则吞、从未入库 → negation 例外首次入库。
- [x] 批次 B-1（M3 装置修复+盲表重生）：commit **2fcc56e1**，盲表重生指纹 = 09 全系 6 份（2026-07-14 10:34, 含 target_bank 列实读确认）+ 61 blind_A/B（10:40, N2 守卫放行路径实证）。**执行中发现并同批收口**：N2-P1（终审 R2-A 实跑确证）——旗标单独硬拦 = 编排器死锁（shim 零参无越权通道, stage 61 首跑后每次验证管道硬中止连坐后续阶段）→ 旗标降格发放记录（零标注放行+LOUD 警告, 非空标注仍硬拦），shim 补 argv 透传，编排器两连跑 EXIT=0 实证，gate 13 用例。
- [ ] 批次 B-2（WP-R2 生产盲表生成，前置=生产数据到位）：**合法延后**（本机 T=2 无生产语料；N2 防覆写已先落, 证据=2fcc56e1 + test_n2_blind_overwrite_guard 13 绿）。
- [x] 批次 C（M4/S4/S5/S6 + WP-R5 文档）：commit **23bf4229**，grep 复扫零残留 = Wickert 零命中 / 平局 undefined 错误语义零残留（V6 changelog 加历史逆转指针, 终审 R2-B 裁定项）/ 第 3 对×4 全对；test_manuscripts_structure 126 绿。
- [x] 批次 D（S2/S3/S7/S8/S10-S13 + WP-R3 proxy 构造）：commit **1fea954d**，fast+gate 全绿 = 专属断言 35 用例 + WP-R3 gate 21 + S11 锚点 sha 与 S3 生产侧双向独立一致互证；locus 双编码 κ=0.8375（tech 492/func 758/unassigned 256），WP-R3-P1（终审 R2-B）：双编码 CSV 由 eval_reports（不入库惯例）迁 config/ 并 negation 入库（κ 证据不可再生须版本化, 文档化偏离）。
- [ ] 批次 E（WP-R1(⊇S9+D8) + WP-R4(⊇D7)，M0 门后）：**合法延后**（付费 36k+9k 播种须生产 stage 21 播种完成+M0 审批）。其 $0 前置已提前完成：commit **1eca8523** = S9 修字 + WP-R1.1①②③（passed 切 full 轨/变体补传 prompt_version/过时注释）+ WP-R1.2 分层抽样器与确定性 gate（帧固化留生产窗口）。判定协议锁定 commit = 1eca8523（WP-R1.3 阈值即 config/validation.yaml:62-69 现值 7 项，先验锁定于计划文本+本 commit）。
- [x] 批次 F（D 组 + N1）：commit **9cda7d84**（D1 恢复历史文档/D2 零前缀依据三落点/D3 checklist/D4 SSOT 互指/D5 重编号批改/D6 改名+守卫/D7 docstring+读写分流注释/D9 证据链披露/D10 五项含 jlm 冻结 hash 按测试自带先例同步/N1 如实声明分支）。
- [ ] 人工窗口（N2 先落 → WP-R2 κ 收口 + WP-R3 三角闭环）：**合法延后**（需真人编码员 + 生产盲表）；N2 已先落（见批次 B-1 行），协议 §8 已登记 M3/N2/N2-P1/WP-R2 通道与 0.6 收口线四行。
- [ ] §11 v9 前置与定稿：V9-PRE-1 已完成 = commit **18d2619d**（skip 守卫四分支版本校验 + parquet 版本戳, grandfather 今日零行为变化, gate 6 用例）；(a)/(c) 起草与 G-v9-1 按推荐路径**待 §10 生产实证输入**（WP-R1/R2 收口）后启动；G-v9-1/G-v9-3 批准人=用户唯一。
- [ ] §11 v9 落地（G-v9-2..5）：待前项。
- [x] §12 注释/日志台账打勾证据：批次 A 表 ✅ / 批次 B-D 表 ✅ / 批次 F 补遗表 ✅ / §10 表（WP-R3 行）✅（第一轮评审一号路逐行核对全中, 冒烟三项 = write_manifest banner anchor 口径 ✅ + radius --help 无旧编号残留 ✅ + prompt_sensitivity 全 full-only 无三轨 AND 残留 ✅）/ G-v9 表 = v9 时点不适用。
- **全量 A/B 差分终判**：改动前基线 21 失败（17 golden 慢性陈旧+4 既有杂项）↔ 终局 21 失败**逐条相同**，0 新增 0 消失（§6-5 达成）；盘上 parquet/dta/golden_panel_v0.json 零触碰（§6-6 达成）；unified_cot.txt/PEER_PROMPT/锚点句等一切缓存键 prompt 字节零触碰（三冻结 gate + git diff 双重实证）。

---

## §10 稳健性缺口闭环（WP-R1..R5；2026-07-12 增补，四轮评审收敛）

> **由来**：v8 三阶段（主体-议题关联识别 / 情感属性分类 / 创新属性分类）的稳健性检验框架齐备但未闭合。本节方案经四轮评审：草案 v1 → 三路并行评审（工程/缓存-golden、计量方法学、铁律/计划冲突，合计 29 条修改意见全部吸收）→ v2 → 对抗终验（7 处精确修正后 ok_to_merge）。
> **衔接声明**：① 本节吸收原条目 S9/D8（→WP-R1）、D7 实修部分（→WP-R4）；M3 保持独立前置。② 与 `MEASUREMENT_VALIDITY_PARITY_EXECUTION_PLAN_2026-06-22.md` 的关系：吸收其 G0–G4 设计，**修订**其注³/F10（"三维收敛效度构念性不适用"）与 WS-G 词表落位条款（见 WP-R3.4，须在该计划留修订注防两份权威文档矛盾）。③ 与 `HUMAN_ANNOTATION_PROTOCOL_2026-07-03.md` 的关系：一切任务/参数变更须在其 §8 变更日志登记（预注册条款强制）。

### 缺口清单（G1–G5，两轮审计+终验核实）

- **G1**：prompt_sensitivity 变体自身有缺陷（S9）且盘上 `passed=False`（V0 true_rate 0.668 vs 变体 0.548–0.581；subst κ 最低 0.29、locus 0.526）——结论被污染，既不能宣称稳健也不能定罪。
- **G2**：情感人工效标装置构念错位（=M3，盲表缺 target_bank+"整体语调"指南）。
- **G3**：创新三维人类金标准**"装置已备、真值为零"**——MVP-0622 通道（`scripts/migrate/manual_validation_sampling.py` + `validation/manual_validation_schema.py`：三编码员 R1/R2/R3、stage3a/b/c 九组列、B/C/D/E 四格分层各 100 + 拒判层 A + 纯随机层 F、v7ref 反锚定双文件）已建成，但盘上无 `manual_validation_samples.xlsx`、人工填写为零；且三维为单方法构念（只有 LLM 一种测法）。
- **G4**：radius_sensitivity_llm 是 scaffold 从未真跑（D7 三不闭合）。
- **G5**：全部统计效度检验都在 T=2 dev 样本，不可外推 T=18。

### WP-R1 措辞敏感性闭环（⊇S9+D8；覆盖阶段一+三，兼及阶段二）

1. **先修字后播种（顺序铁律）**：S9 全部文本修复必须在**变体库付费重跑（36k 播种）之前**一次完成——改变体文本=改缓存键，先跑后修=36k 请求作废（stage 21 主语料播种与 S9 修字无耦合，先后均可）。同批三项代码工作（均不动变体文本之外的缓存键、$0，必须与 S9 同批在 36k 播种前完成）：① 修 `evaluate_track_criteria` 过时注释（"P1 main spec = llm_vote_tone_ctx"，:1086/:1720——full-only 已切主轨）；② **改聚合层**：`passed` 主判定由三轨 AND 切为 full 轨 7 项——**实际切换点 = :1741 `passed = all(...)`（连带 :1185-1190 passed/passed_full 字段；:1187 仅为注释行，勿只改注释不改计算）**，results.json 增 per-track 分判定字段；③ **变体调用补传 prompt_version**（现 `fetch_llm_async` 不传→落 'v0' 命名空间；播种后再补传=键变=36k 变体库作废，必须播种前定稿——终审判定：并入本条（36k 播种前）完成，不推迟到 §11 v9 窗口顺带）。
2. **抽样设计（新写分层器 + 确定性 gate 测试）**：两阶段整群——按 **年 × bank_type_id**（`config/bank_list.yaml:18` 现成键 1–8；媒体类型分层空转 [stage 00 后报纸占 92.93%]、银行规模列不存在，均禁用）分层抽 ~70 个 bank-year 格 × 每格 ~14 篇 ≈ 1000 篇；抽样帧固化为 eval_reports 下 sidecar CSV，**WP-R4 共用同帧**。现行实现是简单随机（`random_sample`, seed=42），分层器为新增工作项。
3. **判定规则预登记**（付费重跑前锁定；明示：dev 结果已被变体缺陷污染，此时改聚合规则不构成事后调整）：
   - 主判定 = **full 轨 7 项 criteria 全过**（0.85 verification / 0.80 sentiment / 0.70 κ / 0.667 α / 0.70×3 三创新维，恰为 `config/validation.yaml:62-69` 现值 7 项，先验锁定）；
   - ctx/ss 轨 fail 不推翻主结论，但强制触发该轨下游稳健性声明的限界披露；
   - **全网格逐格披露**：4 变体 × 3 轨 × 7 指标（含 NaN/失败格及原因），禁只报过线格；
   - 精度声明：verification κ 95% CI 半宽 ≈ ±0.05（n=1000, 边际≈0.67）；创新三维在 verified 子集（n≈670）且类别偏斜下 ±0.12–0.14；**每维少数类地板 ≥60 篇**，不足则按 LLM 预测标签定向过采样 + poststratify 还原；min-κ 是 4 变体序统计量、系统性低估 ~0.5–1 SE——pass 判定用点估计 vs 阈值并强制披露 CI（indifference-zone 备选，二选一预登记）。
4. **聚合层证据（辅助、非 gate；独立 audit 脚本，禁耦合进 `passed`）**：主报**文章级配对指标**（变体 vs V0 tone 相关、标签翻转率 π̂）+ **Spearman–Brown 解析外推** λ = σ²_true/(σ²_true+σ²_flip/n̄) 到生产格深 n̄ 的面板信度——直接回答"标签级 κ 低是否传导到面板级"；整群设计下 n≥5 的格做加权 ρ 作次要展示（格数少则如实降格 illustrative）。实现：`generate_reports` detail CSV 增列 target_bank/年份/三创新维标签（现只有 verified/sentiment），聚合分析放 `scripts/audit/` 独立脚本只消费 CSV。
5. **预登记决策树（生产重跑仍 fail 时）**：(i) **排除"未经 §11 gates 的即时 prompt 修改"作为本分支补救**（WP-R1 fail 不构成绕过 G-v9-0..3 的理由；未经受控重生的 prompt_version 翻转 = 2.1GB 缓存+golden 锚全废）；弱维发现转入 §11.1(b) 作为 v9 定向强化的设计输入（v9 本身按 §11 自有 gates 推进，非本分支的即时补救）；(ii) 限界节逐维披露 κ 与 CI；(iii) **效度锚 = 人工效标（WP-R2）**——V0 与人工金标准 agreement 达标则 V0 作为既定操作化成立，措辞敏感性降格为"替代操作化间信度问题"如实披露；三家共识仅作**模型轴**稳健性证据，**不得表述为对措辞轴的补救**（两轴正交，范畴错误）；**阻塞语义**：若 WP-R1 fail 而人工效标尚未收口，本分支判定挂起至人工窗口收口，不得以未收口数据预判；(iii-b 可选) 抽样子集上各变体标签重构 treatment 的 specification-curve 式系数展示（illustrative）；(iv) 涉事维度论文声明降格。
6. **成本/隔离/前置**：36,000 付费请求（V0 $0 从 `21_tone_llms_full.parquet` 读）≈ 数十至低两百美元、concurrency=20 约 4–6h；全部写 `_llm_cache_validation.db`（W4 隔离，与 WP-B1 golden 重生窗口零互斥）；**前置 = 生产 T=18 stage 21 播种完成**；随 §5 批次 E 过 M0（先例：批次 E 本含 S9/D8 同笔预算）。

### WP-R2 人工效标补全（前置=M3；创新三维走 MVP-0622 既有通道）

1. **路线判定**：创新三维**不**扩 `61_human_samples` 工作台（协议 §4-③ 禁一切机器判定入盲表、`merge_annotations`/`_ANNOTATION_COLS` 4 列硬编码、strict/仲裁台/三个既有测试全量改动、且协议头部明文"创新维度以 MVP-0622 及其盲表协议为准"）。**启用 MVP-0622 既有通道**：生产语料上运行 `manual_validation_sampling.py` 生成三编码员盲表 → 人工填写 → κ 分析收口（G0–G4/Gwet AC1/bootstrap CI 按 MVP-0622 既定设计）。
2. **口径写死**：三维 agreement 的**评估框 = verified 子集分层格 B–E**（`llm_verified_full==True`，框级门控、表内零机器列——MVP-0622 既有设计，天然解决"机器判定不得入盲表"矛盾）；盲表另含拒判层 A（verified=False ×100）与纯随机层 F（~15%，脚本内置的 LLM 漏检率无偏估计层）。与模型 m 的 per-model 比较再按 `{m}_verified_full` 二次取子集并报各自 n。**三块报告结构**：① 门控审计 κ（61 工作台 T1，全样本含 verified=False 负类，M3 修复后装置）；② 三维人-机 agreement（MVP-0622 B–E 格）；③ 门控漏检率——以 61 工作台 T1 为主口径，MVP-0622 的 A/F 层作交叉验证第二来源。relevance→三维效标链条闭合，零额外人工成本。
3. **样本量**：每维有效标注 ≥300（均衡边际下 κ CI 半宽 ≈0.09，偏斜 80/20 时 ≈0.12，写明假设）；与 MVP-0622 分层设计（B/C/D/E 格 ×100，E 不足回补 C/D + 拒判格 A + 纯随机层 F）取并集校核；少数类 ≥60 地板 + 定向过采样。
4. **编码指南（防转述漂移）**：逐字引用 v8 step3 类目定义——**模块内常量 + verbatim gate 测试**（断言常量 ∈ `unified_cot.txt` step3 段子串，测试只读）；**禁 `import tone_llms`**（其模块级 setup_logging 会截断覆盖 `logs/21_tone_llms.log`）；引用标注 `v8-2026-05-17` token；**prompt 本体零字节触碰**（铁律显式钉死）。
5. **κ 纪律**：人-人 κ 用仲裁**前**独立编码计算（仲裁后算 κ = 循环）；人-机效标 = 仲裁后金标准（另报 vs 各编码员上下界）；名义类目禁任何"平均"。**双线并存声明**：pilot 试标资格门沿用协议 §5 的 **0.667** 不变；本条新增 **0.6** 为正式批"构念可编码性"收口线，属新增参数随 §8 登记。**人-人 κ<0.6 处置协议**：一次性指南澄清（禁改类目定义）→ **换新抽样批**重标（禁原批重标防记忆污染）→ 最多 2 轮 → 仍<0.6 判"该构念文章级不可被人类可靠编码"，该维 LLM 声明降格为机器间一致性证据入限界节，禁在 κ<0.6 人工标签上算人-机 agreement 充数。
6. **协议与防覆写**：协议 §8 登记本 WP（通道启用 + 0.6 收口线 + 任何参数变更）；**N2 前置**：stage 61 每次管道运行重生盲表（07-10 八入口审计已覆盖过一轮）——人工标注启动前必须先落防覆写机制。

### WP-R3 创新维度三角化（proxy 构造可先行 $0；**收口依赖 WP-R2 人工标签**）

1. **载体**：`scripts/audit/innovation_proxy_triangulation.py`（audit-only：不注册 DAG/OUTPUT_REGISTRY/shim，产物仅 eval_reports）——零 golden 已三路核实。
2. **三 proxy 构造**：
   - subst：具体投入信号 regex（金额+单位/人数/系统上线/专利号/资质获批）；
   - locus：fintech_dict 1506 词按 Gomber enabling-tech vs business-function 二分 → **新建 `config/fintech_locus_split.yaml`**（**禁改 `fintech_dict.json` 本体**——已入两个 parquet 的 input_hashes 血缘）；二分 = **双人独立编码**（指南逐字引 Gomber 类目）+ 词级 κ（预期 >0.7）+ 仲裁 + **unassigned 第三桶**（两可词剔出分子分母）+ 覆盖率披露 + 版本号 + 双编码原始表存档 eval_reports；
   - collab：协作动词表 × 非银实体共现——实体锚点 = `company_listed_names.yaml`(5,528) + `company_tax_names.yaml`(44,771) + `bank_list.yaml` 剔除 + ~20 词头部非上市金科手工名单（蚂蚁/微众等）+ 泛机构后缀正则；AC 自动机范式抄 `company_listed_bank/01_build_company_bank_cooc_registry.py`；覆盖口径披露。
3. **分析设计（三角闭环替代单边 φ）**：在 WP-R2 人工标注同一批文章上同报三边 human-LLM / human-proxy / LLM-proxy（proxy $0 边际）；**预登记弱边定位规则**：human-LLM 高 + human-proxy 低 → proxy 弱、LLM 效度由人工边独立支撑、LLM-proxy 低不构成负面证据；human-LLM 低 → 问题在 LLM 或构念（回 WP-R2.5）；三边俱低 → 操作化整体存疑入限界。各边附 Spearman 衰减校正参考值（标注 illustrative）。**主报连续占比的 point-biserial/Spearman**（不依赖阈值），二值 φ/κ 在阈值梯子 {0.3, 0.5, 0.7} 上次要展示（梯子各点并排、不进任何联合检验）。
4. **防误用与决策记录修订**：proxy 报告 md/JSON 固定印铁律 note（"co-equal validity evidence; never pooled into one over-identified Hansen J; not a panel measure, not an instrument"）；gate 断言：产物路径 ⊆ eval_reports、`fintech_locus_split.yaml` 零 `pipeline/`/`papers/` import（仅 `scripts/audit/` 消费）、与面板 dta 列名零交集。**修订 MEASUREMENT_VALIDITY_PARITY 计划两处**：① 注³/F10"三维收敛效度构念性不适用"（本 WP 三角闭环设计改变其适用前提）；② **WS-G 词表落位条款**（"词表须落 validation 局部常量不进 config/"）——locus 二分表为双编码产物需持久存档与版本化，validation 局部常量不适合承载，故落 config YAML 并以上述 gate 断言替代"不进 config/"的隔离意图；两处均须在该计划留修订注。
5. 外部效度挂账（不阻塞）：财务面板到位后 subst→IT 投入/专利、collab→M&A 预测效度。

### WP-R4 上下文半径敏感性闭环（⊇D7 实修部分）

1. **事实基线**：`radius_sensitivity_llm` 测的是 **ctx 轨实体窗口半径**（`RADII_TO_TEST=[0,1,2,3]` :59、baseline=1 即 `CACHED_RADIUS` :60、baseline 结果从 parquet $0 读的逻辑在 :352/:508 非 :60 邻近、模块明写"仅 ctx 轨" :20）；full 按构造豁免；**ss 轨的 `ss_sentence_radius` 是另一个 config 键另一个敏感性问题**——裁定：本 WP 不做，挂账为"如 referee 要求另立平行臂，共用抽样帧"。
2. **工作项如实列**：D7 三小改**代码级实修**（`--radii` 接线到 RADII_TO_TEST / precheck 补 `DEEPSEEK_API_KEY` / cache 写入目标代码切 `_llm_cache_validation.db`；D7 批次 F 仅先行改 docstring 文字表述，非重复项）+ **launch 路径 ~150–200 行异步实现**（复用 `tone_llms.run_all_llms` + LLMCache，**显式传 prompt_version，勿默认 'v0'**——镜像 WP-R1.1 ③）+ 逐 radius 重物化 content_ctx（entity_context 重抽，$0 CPU）；**读写分离纪律**：新 radii 响应写 validation 库、baseline 从 parquet 读（勿点查生产库）；`tests/test_radius_sensitivity_llm.py:74` 锚 RADII={0,1,2,3} 沿用不红。
3. **统计设计（预登记）**：每维 κ(r vs 1) + **标签翻转率**双报；**McNemar 精确检验**测翻转方向性（系统性单向翻转 vs 对称噪声，κ 区分不了）；跨 4 radius 的 Krippendorff α 总量指标；verified 率对 r 的弱单调性检查（非单调提示提取 bug 而非真敏感性）；判定线沿用模块 `KAPPA_THRESHOLD_RADIUS=0.70` 先验锁定；聚合与披露规则同 WP-R1.3 预登记协议（主判定锁定 / 全网格逐格披露 / 精度声明三要素）。
4. **费用与 $0 前哨**：1000 篇（与 WP-R1 共帧）× 3 模型 × 3 新 radii {0,2,3} × ctx 单轨 = **9,000 请求** ≈ WP-R1 的 1/4；**先跑 $0 词典法前哨**——姊妹模块 `validation/radius_sensitivity.py`（6 词典本地）在生产语料跑半径梯子，LLM 法只对词典法显示不稳的维度全量跑（最坏省 2/3）；**降级方案预登记**：deepseek 单模型全 radii + 两家端点 {0,3}（within-model 识别 + 端点可迁移性），端点三家 κ 分歧 >0.1 则降级作废、补跑或列限界。
5. 前置与预算同 WP-R1（生产 stage 21 播种完成；批次 E 同一预算单过 M0）。

### WP-R5 生产 T=18 稳健性总闸（纯文档，可先行）

1. **新建 `scripts/audit/M0_PRODUCTION_GATE_CHECKLIST.md`** 作为 M0 门唯一实体文件（现状：33 个 audit 计划引用 M0、无实体、`DEFERRED_ITEMS_COMPLETION_2026-06-20.md:62` 指向的 memory 已不存在），内设"robustness verdicts at T=18"一节：prompt_sensitivity / radius / 人工 κ / proxy 三角化四件套必须有 T=18 记录（重跑或有效性论证），并写明核查动作（grep manuscripts 样本口径句），非只写原则。
2. **证据三分类（替代一刀切禁令）**：**A 类**=工程不变量/构造性结论（代码路径、位级等价、schema parity、fail-loud 逻辑、EOL）——T=2 永久有效，引用标注 "code-invariant, sample-size-independent"；**B 类**=数学恒等/退化论证——豁免但标注；**C 类**=统计效度结论（κ/α/φ/翻转率/聚合相关及一切"稳健/不稳健"判定）——必须 T=18，T=2 结果只能以 "pilot, not evidential" 出现。四件套全落 C 类。
3. **选择性报告纪律（代替 FWER）**：效度诊断不进 rwolf FWER 家族——rwolf 保护的是"同构念多个 headline 处理效应估计"的确证性家族，κ/φ/翻转率是信度系数无拒绝域对象（心理测量惯例 = 描述性报告+CI）；真正的多重性风险是**网格挑格子报告**——纪律：预登记网格逐格披露（含 NaN 格及原因）、pass/fail 聚合规则在付费重跑前锁定、事后剔格须给独立于结果的理由。
4. `papers/_common/AI_DISCLOSURE_TEMPLATES.md` 补句：措辞敏感性与效标效度结果须随样本/语料口径一起披露。

### 新挂账（评审衍生，非 WP-R 范围）

- **N1**：`27_tableA12` Panel C（:122-123）只 confirm `{m}_sub_frac`——P4（`bank_fintech_locus/paper_spec.yaml:92-93`）/P5（`bank_fintech_collab/paper_spec.yaml:122-123`）的"真 FWER=Panel C"**空指**（P3 为真）。处置二选一：扩 CLS 族至 tech_frac/collab_frac（RES J(9,1)→J(15,1)，独立小改）或 P4/P5 spec 注释改如实声明。
- **N2**：盲表防覆写机制——**三要素**（终审补全）：**做什么** = 盲表写出前检测既有文件的人工标注列是否已有任何非空值，有则拒绝覆写并 loud 报错（要求显式 `--force-regenerate` 才可覆盖），另落一个"标注进行中"旗标文件作双保险；**在哪做** = `llms_human.py` 盲表写出口 + `manual_validation_sampling.py` 工作台写出口（两处同模式）；**验收** = 单测两条（已填盲表被拒绝覆写 / 空盲表正常重生）+ 人工填写启动前实测一次拒绝路径。**时序 = 人工窗口硬前置**（人工填写启动前必须先落，见 WP-R2.6 与 §5 人工窗口行；勿按批次 F 低优理解）。

### §10 验收标准

1. WP-R1/R4 的判定协议（阈值+聚合规则+决策树）在付费播种**之前**以 commit 形式锁定（§9 批次 E 行记录 commit hash）。
2. 变体/radius 全部响应仅存在于 `_llm_cache_validation.db`（生产库条目数播种前后不变）。
3. 新增 gate 常绿：分层抽样确定性、编码指南 verbatim 锁、locus 词表三桶完整性+零 pipeline import、proxy 产物路径断言。
4. 人工窗口收口时：三块报告（门控 κ / 三维 agreement / 漏检率）+ 三角闭环三边齐备于 eval_reports，协议 §8 有登记记录。
5. `M0_PRODUCTION_GATE_CHECKLIST.md` 存在且被批次 E 实际走过（checklist 打勾）。
6. 全程 v8 prompt / PEER_PROMPT / 变体外的一切缓存键 prompt **主树零字节触碰**（§11 worktree 候选文本与 G-v9-3 批准后的受控翻转不在此列，见 11.2-3）；面板 dta 零新列零漂移（**G-v9-4 受控全量重生前口径**；重生后以新 golden 为基线）。

---

## §11 v9 prompt 升级（本计划的组成部分；提示词修改的唯一受控通道；落地后终态冻结）

> **授权与定位**（用户决策 2026-07-12，**时点于 2026-07-13 更新**）：v8 prompt 可按国际顶刊要求修改形成 v9；v9 升级**纳入本计划统筹推进**，不再强制等 §1–§10 全部收口——但 (b) 类内容依赖 §10 WP-R1/R2 实证结果，**推荐保持"先 §10 收口、后 v9 定稿"的顺序**（(a)/(c) 类内容可先行起草评审；若放弃 (b) 类输入提前定稿，须在 G-v9-1 记录该放弃决策及理由）。**v9 ≠ 修字，= 一次完整的测量版本再造**：全量 stage 21 付费重跑 + golden 受控重生 + 全链耦合点同步。**v9 落地即终局**（用户决策 2026-07-13）：计划执行完毕后提示词终态冻结、严禁修改、无 v10 路径——v9 是最后一次提示词变更窗口，定稿评审须按"此后永不再改"的标准执行。
> **审批人条款**：v9 定稿（G-v9-1 出口）与全量付费（G-v9-3/M0）的批准人 = **用户本人，唯一**；评审 agent 结论仅供决策参考，任何 agent 判定不构成批准。
> **版本头命名规范**：token = `v9-<定稿日期 YYYY-MM-DD>`，须匹配 `scripts/lint/check_prompt_headers.py:32` 的 `^#\s*version:\s*(\S+)` 正则；G-v9-2 回炉改任何字节必须换新日期 token（禁复用——缓存键含全文不会错命中，但 manifest/叙述/归档锚会二义）；付费播种开始后 token 与字节冻结；**计划执行完毕后 v9 进入终态冻结（用户决策 2026-07-13）：严禁任何修改，无 v10 升级路径**。
> **本节评审史**：草案 → 对抗评审（12 点耦合清单核验 10 点准确 + 1 真方法学洞[桥接金标准帧错位] + 7 遗漏耦合点[13–19] + 6 组精确修正）→ 全部并入后 ok_to_merge。

### 11.1 v9 内容来源（三类，逐行 diff 须带 a/b/c 标签随版本头入库）

- **(a) v8 已知文本级缺陷修复**（= §4-1 deferred 清单，两处集合已对齐）：删/改悬空文档引注与版本管理元叙述（:84）；补 false 分支不对称（sentiment_reason/各 confidence 无"false 时"指示）；空 co_mentioned_banks"同行（）"空括号（prompt 或构造侧改"无"）；"大数据风控"跨类示例补 tie-break 指引；confirmed_bank 零消费字段删或启用（二选一）；Gomber 2017/2018 引注口径对齐代码注释（二元直接出处 = Gomber, Koch & Siering 2017）。
- **(b) §10 实证驱动改进**（v9 设计核心输入，也是"必须在本计划之后"的理由）：WP-R1 生产措辞敏感性逐维结果、WP-R2 人-机分歧模式、WP-R4 半径敏感性结论——对弱维定向强化类目定义/边界示例。
- **(c) 顶刊 referee 驱动通用增强**：最小化原则（镜像 v8 的 additive supplementation per Nosek et al. 2018 先例），优先加边界示例/判定原则，不动构念本体；v8 prompt 内"维度 1/2 判定规则与 v7 严格一致"的元叙述（:84）若 step3 有改动须同步重写。

### 11.1-Q v9 质量标准（国际顶刊最高水平门槛；用户要求 2026-07-13，经对抗评审 7 处必改+1 缺口补全后定稿）

> **定位**：v9 不仅是缺陷修复，必须以"顶刊测量工具"标准定稿。三层门槛全部预登记；**设计层 = 硬闸**（完全可控，必须全过）；**实证层 = 非劣硬闸 + 优效目标 + 诚实披露框架**（构念的真实措辞敏感性不可由文本消灭——顶刊标准 = 设计卓越 + 证据诚实，非"保证全绿"）；**评审层 = 模拟顶刊审稿闭环**。Q-A 检查单落 `scripts/audit/V9_QA_CHECKLIST_<v9定稿日期>.md`（结构 = 十三条各一节：条目原文引用 / 证据指针 / 勾选 / 裁定人），路径登记进 §9 的 §11 收口行。

**Q-A 设计门槛（硬闸，G-v9-1 出口条件，逐条可检查）**

1. **构念-操作化三层对齐**：每个测量维度给出「文献构念定义 → 判定规则 → 边界案例处置」三层结构，每条判定规则可追溯到已锚定文献（W&Z 1994/1998 + Fiss & Zajac 2006 [subst]；Gomber et al. 2018 / Gomber, Koch & Siering 2017 [locus，引注口径对齐代码注释]；Chesbrough 2003 + Laursen & Salter 2006 [collab]）；**既有引注（含 Adner & Kapoor 2010 SMJ，:57）的保留/删除须逐条决策记录**；新增文献必须过 audit_dois 机械闸（登记载体 = 新建补编 md + append `FILES_WHITELIST_ANCHOR` 冻结 tuple，按第六~九补编先例；prompt 内引注为 author-year 无 DOI，机械闸作用于锚点登记册而非 prompt 文件本身）。
2. **类目体系满足内容分析方法学标准**（Krippendorff）：互斥、单维度；每对类目给显式 tie-break 规则（修复"大数据风控"跨类悬空）；**穷尽性经由"强制二选一设计 + 边界案例处置规则"实现（v8 既有范式，如 :82 无"混合"类的显式声明），不通过新增类目**——若模拟审稿判定必须新增类目 → 触发 11.2-1 schema-breaking 单独审批，不在本条内静默放行。
3. **输出契约完备性**：v9 定稿 output_format 的**全部字段**（字段数由 gate 测试对 prompt 与解析器动态断言，**禁在文档硬编码计数**——v8 盘上实为 17 键、契约口径 16，正是硬编码数字打架的教训）在 true/false 两分支均有显式取值指示（修复 false 分支不对称）；零消费字段清零（confirmed_bank 删或启用）；JSON 契约与解析器逐字段互锁并有 gate 测试。
4. **CoT 结构符合 LLM 测量最佳实践**：reason 前置于标签（De Kok 2025 先例，保持）；属性独立/抗交叉推断指令（GABRIEL 范式）；实体聚焦/同行抗污染指令保留并按 WP-R2 人工分歧模式定向强化。
5. **Token 纯净性与成本纪律**：不向模型发送内部元叙述、版本管理叙述、悬空文档引用（修复 :84）；每个 token 服务测量；**v9 相对 v8 的 token 增幅在 G-v9-3 ① 费用外推中显式列示**（防边界示例无度膨胀）。
6. **语言与结构零缺陷**：无错别字/歧义/自相矛盾；指令计数词与任务数严格一致（吸取变体"两项/三任务"教训）；类目标签中英对照表与 codebook 同步定稿；prompt 全文由 ≥2 个独立评审 agent 逐句审后**零 P1 级（本计划分级口径：必须修）残留，P2 级逐条显式裁定（修或记录不修理由），禁静默遗留**。

**Q-B 实证门槛（预登记于任何 v9 付费请求之前）**

7. **措辞稳健性重测（强制，覆盖 G-v9-3 ② 对变体族的裁定权）**：① v9 变体套件按**预登记扰动分类学**重派生——V1–V4 各自扰动维度不变（角色改写/结构调序[并入"标签枚举列序对调"扰动]/精简/整句改写），扰动强度以可核对代理锚定（各变体相对基准的长度比/编辑距离落在 **S9 修字后的** v8 同名变体区间 ±20% 内），派生文本在任何 κ 计算前以 commit 锁定（防"派生下手轻→κ 自动变好"的博弈）；② 判定用 WP-R1.3 同一预登记绝对阈值集（7 项 criteria 现值），**硬闸 = v9 的过线 criteria 集合 ⊇ v8 生产重跑的过线集合**（v8 已 fail 的维度 v9 同 fail 不触闸，走 WP-R1.5 决策树+披露）；③ v8↔v9 的 κ 数值对比仅作描述性披露，显式标注"两套扰动集非同一，不构成劣化检验"。
8. **效标效度非劣 + 优效目标**：非劣硬闸（G-v9-2 帧②，下界差 ≥ −0.05）不变；**优效目标（aspirational，非硬闸）** = v8 弱维在 v9 下提升 ≥0.05——弱维 = 帧② v8 vs 人工金标准 agreement 点估计最低的**单一维度**（平局取 κ 低者），付费前随判定协议 commit 锁定；报点估计 + bootstrap CI；未达成不回炉、如实报告（防无限迭代）。
9. **跨厂商稳定**：帧① 同帧配对（v9 侧 = pilot 响应，v8 侧 = `21_tone_llms_full.parquet` $0 直读），full 轨主判定；三家 per-model 与各自版本共识的 κ **逐家逐维下界差 ≥ −0.05**（镜像帧② 非劣界，点值直比会被 ±0.05 的 CI 噪声击穿）；破界 → 回炉 G-v9-1 并定位该厂商劣化维度。
10. **重复稳定性（test-retest，本次评审补全的唯一真缺口）**：帧① 内嵌 test-retest 臂——~200 篇 × 3 家 × 3 次重复 ≈ 1,800 请求（写 validation 库，计入 G-v9-2 帧① pilot 预算），报逐维重复一致率/κ；**描述性披露不设硬闸**（temperature=0 下的重复不稳定是 provider 属性非 prompt 设计可控，设硬闸=无法兑现）——这是 LLM-as-measurement 顶刊 referee 高频问题，v8 从未量化。**落地机制裁定**（终审补，防结构性假报告）：主 LLMCache 键在 temperature=0.0 下 seed 刻意不进键（caching.py:291-295）且无 LLMs_dic 式 tag 槽——rep 序号须编码进 **prompt_version 后缀**（如 `v9-<date>#rep{1,2}`，rep0 用裸 token；pv 仅入键不发 API）；rep>0 条目**不参与** copy-on-pass 复制（生产键空间无 rep）；**禁三次同键裸调用**（= 全部缓存命中 = 一致率恒 100% 的假报告，$0 无异常信号最难发现）。
11. **可复现性包合规**（Carlson & Burbano 2026 SMJ §3.3 口径，已过 audit_dois）：汇总核验既有条款（G-v9-5 桥表与披露 + S14 + §11.4-#6/#7），**本条唯一净增项** = 复现包内容核对单（v9 全文 + token + temperature=0.0 + seed=42 + 三家模型 ID + 解析器契约文件清单）落 replication README 逐项打勾；可选（用户裁定）：判定协议 commit hash 镜像至 OSF。

**Q-C 评审门槛（G-v9-1 升格）**

12. **模拟顶刊审稿轮**：作为 G-v9-1 多路评审的**固定一路**（扩充而非对抗终验之后再加轮，防流程无限加长）——≥3 个独立评审视角（测量方法学审稿人 / 内容分析方法学家 / 领域理论审稿人[银行×金融科技]）对 v9 草案+效度证据包出具审稿意见；**首轮证据包 = §10 已收口的 v8 效标/敏感性证据**（即 11.1(b) 设计输入；v9 自身桥接证据归 G-v9-2 预登记协议机械判定，不进首轮审稿；若 G-v9-2 破界回炉，复审轮证据包须并入桥接结果；若走 G-v9-0 ① 放弃分支提前定稿，证据包降格为 dev 结果 + 放弃理由书，审稿轮如实按无生产证据评审）；全部 major 意见闭环（修复或书面 rebuttal）后方可提交用户定稿批准。
13. **终局标准**：v9 落地即终态冻结（无 v10），定稿评审按"此后永不再改"把关——任何"以后再优化"类意见一律视为 major、当轮闭环。

### 11.2 变更纪律

1. **禁改输出 JSON schema 键名与标签枚举**（正面/中性/负面、实质性/象征性、底层技术/应用场景、自主研发/外部协同）——除非走 schema-breaking 单独审批，同步改：tone_llms 解析器 + `_aggregate_track` tie_default 字面量 + `encode.LLM_CLASS_SPEC` + `_LLM_CLASS_SPEC_FALLBACK` + `prompt_sensitivity` 变体 schema + 人工标注枚举（`manual_validation_schema.py`/`llms_human.py`）+ 测试响应构造器（`test_omni_fix_tonellms.py:62`、`test_llm_classification_robustness.py:49`）+ codebook；落地前以 `grep -rn '实质性|象征性|底层技术|应用场景|自主研发|外部协同' --include='*.py'` 生成消费方 inventory 逐处核对，**不得凭清单记忆**。
2. v9 窗口内禁"顺手改"其他任何带独立版本门的 prompt（PEER_PROMPT `v1-2026-05-13` / LLMs_dic / ncd EXTRACTION_PROMPT 各有独立缓存键空间与升级路径——**该等升级路径仅在计划执行期内有效，终态冻结后一并关闭，见 §0-1 末句**）。
3. **主树隔离铁律**：v9 候选文本放 worktree/独立分支，pilot driver 显式加载候选文件路径；主树 `config/prompts/unified_cot.txt` 在 G-v9-3 批准前零字节不动——否则全局 `PROMPT_VERSION` 翻转，skip 守卫、verify 脚本、任何并发 stage 21 全部跟着变。

### 11.3 流程 Gates

- **G-v9-0 前置硬条件**：① **(b) 类设计输入就位** = §10 WP-R1/R2（及相关 WP-R4）收口（推荐路径）；用户已授权提前推进（2026-07-13），若裁定放弃 (b) 类输入提前定稿，须在 G-v9-1 记录该放弃决策及理由——其余前置不因提前而豁免；② **V9-PRE-1（本节自有前置工作项）**：修 skip 守卫版本盲区——`run_pipeline_function.py:376-391` 指纹只比行数+内容列、对 prompt 版本盲，且 stage 21 输出 parquet 无 prompt_version 记录 → 补 parquet metadata 版本记录 + skip 兼容检查校验版本；不修则 v9 后旧 v8 parquet 被 skip 放行、下游静默消费旧标签；③ 主树隔离就位（11.2-3）；④ 批次 A（M1/M2/S1 指纹锚链）先行收口——v9 重锚（G-v9-4）建立在修好的 sidecar/manifest 单点之上，带病升级会把双脑分裂复制进 v9 锚。**本项约束的时点 = G-v9-4 重锚启动前**（含 S1-v9 gate 更新，见 11.4-#2"先重锚 sidecar 再改 gate"）；(a)/(c) 起草、G-v9-1 评审、G-v9-2 pilot（仅写 validation 库）不被本项阻塞。
- **G-v9-1 v9 草案多轮评审**：镜像本计划四轮模式（草案→多路评审[测量效度/工程耦合/铁律 + **11.1-Q 模拟顶刊审稿轮**（Q-C #12）]→按意见修订→对抗终验）；**出口条件 = Q-A 六条设计门槛全过 + Q-C 全部 major 意见闭环**；定稿批准人=用户。
- **G-v9-2 桥接试点（双帧设计）**：
  - **帧①（v9↔v8 机器桥）**：WP-R1 抽样帧 n≈1000 上 v9 × 3 家 × 3 轨 ≈ 9,000 请求（+ Q-B #10 test-retest 臂 ≈1,800，计入本帧 pilot 预算，合计 ≈10,800；不入 G-v9-3 ① 外推与 ② 族清单）；v8 对照**从 `21_tone_llms_full.parquet` 直读**（官方聚合标签，真 $0；勿走缓存重放——重放须重现聚合与 tie-retry 序列）；报逐维 κ/翻转率。
  - **帧②（人工非劣检验）**：WP-R2 人工已标帧（MVP-0622 B–E 格 + 61 工作台）上 v9 重判 ≈3–6k 请求；**配对设计**（同文章同金标）计算 v8/v9 各自 vs 人工金标准 agreement，bootstrap CI；**预登记非劣界与聚合规则**（付费前锁定）：verification+sentiment 任一维下界差 < −0.05 → 回炉 G-v9-1；三创新维破界 → 披露+定向强化再评审。
  - **pilot 缓存落库（裁定）**：全部写 `_llm_cache_validation.db`；G-v9-2 通过且 v9 字节+token 定稿后，一次性脚本按 cache_key **行级复制进生产库**（`llm_cache` 表自包含、键=sha256(schema|model|prompt|pv|temp)，同键复制即命中 → 省 9–15k 重付）；回炉分支条目留 validation 库自然废弃，生产库（golden 锚）零污染。**两个硬前提**：pilot driver 的 prompt 构造必须走 `iter_article_track_prompts`（对候选模板路径），且**显式传 v9 token 作 prompt_version**（勿镜像 entity_masking/prompt_sensitivity 现行不传→'v0' 的写法，否则键与未来生产不同、复用价值归零）。
  - 白话：试点先记在草稿账本上，考试通过再把答案原样誊进正式账本，正式跑不用重新花钱问；考试不过，草稿撕掉，正式账本干干净净。
- **G-v9-3 M0 审批**（批准人=用户）：① 全量 stage 21 重跑费用按 pilot 单价 × 生产过滤后篇数实测外推；② **validation 族同版本化决策**（对抗评审补项）：**变体族（36k）已被 Q-B #7 强制重跑，不再是可裁定项，其费用计入 ① 外推**；剩余两族（9k 半径 + 9k 实体掩码）逐族裁定"随 v9 重跑"还是"以 v8-scope 披露"（不裁定则论文引用的敏感性/掩码 κ 与生产 prompt 版本错位）。⚠ **两笔口径**（终审补）：本处 36k = **v9 变体族**播种；§10 WP-R1.6 的 36k = **v8 变体族**（S9 修字后）生产重跑，批次 E 预算、另一笔。两笔独立、先后各自过 M0，**禁合并认领、禁以"v9 反正要重跑"为由跳过 v8 笔**——Q-B #7 ② 硬闸的参照集 = v8 生产重跑过线集合，缺 v8 笔则该硬闸空转（镜像 M2 Zenodo"非同一笔勿双重认领"条款）；③ golden 全量重生窗口 + `_llm_cache.db` 体积近翻倍的磁盘预算 + 不可逆确认。
- **G-v9-4 全量重跑与重锚**：受控 golden 重生（`PYTHONHASHSEED=0` + 全 BLAS 钉 1；BLAS 9 列 drop 口径沿用）；**冻结阈值 sidecar 逐一裁定**：`v3_5_1_constants.json` 的 median_amb_d0×3（codebook.py:1487 注明 "anchored to prompt v8"——v9 文章宇宙变，preserve-if-set 会静默沿用 → 显式二选一：删字段重算重冻结 or 保留+披露）、`_benefit_center_sidecar.json`（嵌入空间未变但 verified 宇宙变、守卫只锁 model_id 不会 fire → 同样显式裁定）；**顺序**：先重锚 sidecar（prompt_v9_sha256 新键，保留 v8 键作历史；`manifest.py:64/144/257` 三处 `prompt_version_anchor='v8'` 默认参数化，测试锚 `test_llm_archive.py:243`/`test_v3_5_to_v3_5_1_migration.py:106`/`test_omni_fix_tonellms.py:861` 同步）→ 再更新 S1 frozen-hash gate 为 v9 双口径哈希（顺序反了 S1 先红）；manifest/archive 重生 + **Zenodo 版本化增补 deposit**（仅覆盖 v9 新增归档；M2 的 28 文件挂账在 M0 生产收口窗口兑现，非同一笔）；`verify_stage21_cache_coverage` 按 v9 复跑（脚本用活 PROMPT_VERSION 自动跟随）；**CLAUDE.md 同步改写**（终审补，缺此条则 v9 落地当天 CLAUDE.md 仍陈述无条件 v8 冻结）：①"冻结锚点：Prompt v8 字节级冻结 + jieba==0.42.1"段改写为 v9 口径 + **"全部提示词资产终态冻结（unified_cot v9 / PEER_PROMPT / LLMs_dic 生成·判别 prompt / benefit 10 对锚点 / jlm 5 对锚点 / ncd EXTRACTION_PROMPT），严禁任何修改，无 v10 及任何后续升级路径"声明（用户决策 2026-07-13；勿只写"v9 终态冻结"——会诱导未来会话推断其余 prompt 仍各有升级路径）** + v8 历史复现 checkout 一句；②"缓存命中键 = prompt_version='v8-2026-05-17'"行更新；③各处 M0 引用补指向 `M0_PRODUCTION_GATE_CHECKLIST.md` 实体的指针。
- **G-v9-5 论文披露与可比性桥**：**可比性判读预登记**（付费试点前锁定）——桥表逐维报 v8↔v9 标签 κ：κ ≥ 0.80 的维度声明为 *clarification*（同一构念、同一测量序列）；κ < 0.80 的维度必须声明为 *re-operationalization*（新操作化），该维主结果 v8/v9 双报，**禁写"稳健于 prompt 升级"**——用数据而非措辞裁定"定义澄清 vs 换尺子"。另披露：v8 历史复现口径（缓存条目永久可命中，但盘上模板已 v9 → v8 字节级复现须 checkout 历史 commit，写入 replication README）；数值副作用（verified 率/n_articles/全 LLM 族列漂移，镜像换嵌入先例）。

### 11.4 技术耦合总清单（19 点；bump 时逐点走查，禁凭记忆）

| #   | 耦合点                                                                                                                                                                                                                                                                                                                                                                                                            | v9 时须做                                                                                                                                   |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | 版本头解析链（core/config.py:96-138 → tone_llms.py:246；两处 `.get(...,'v0')` 回退为哨兵值 'v0' **非旧版本号字面量**——bump 头即全链自动跟随、无 v8 字面量残留可陈旧）                                                                                                                                                                                                                                                                                                                                            | 仅改首行 token；须过 check_prompt_headers 正则                                                                                              |
| 2   | S1 frozen-hash gate（§2-S1 新增项）                                                                                                                                                                                                                                                                                                                                                                               | 更新 v9 双口径哈希；**先重锚 sidecar 再改 gate**                                                                                            |
| 3   | sidecar/manifest 指纹锚（manifest.py:240 读`prompt_v8_sha256`；:64/144/257 anchor='v8'；3 个测试锚）                                                                                                                                                                                                                                                                                                              | add`prompt_v9_sha256`（保留 v8 键）+ anchor 参数化 + 测试同步                                                                               |
| 4   | prompt_sensitivity V1–V4（v8 文本硬编码）                                                                                                                                                                                                                                                                                                                                                                         | 从 v9 重派生（保留 S9 修复与 WP-R1.1 ③ 已在执行期补传的 prompt_version）                                                                    |
| 5   | WP-R2/MVP-0622 编码指南 verbatim 常量 + gate 锚                                                                                                                                                                                                                                                                                                                                                                   | 改锚 v9；已完成的人工效标结果标注 v8-scope                                                                                                  |
| 6   | 全仓版本叙述（2026-07-13 复扫现值：全域 307 处/23 文件[不含本计划自身]；手写源头恰 30 处/15 文件逐改，含**CLAUDE.md 两段**[冻结锚点段+缓存命中键行，见 G-v9-4]；生成物 ~277 处随 codebook 重生自动翻新。**口径声明**：本计数=广义"v8 版本叙述"；§0-2 的 296/17 = git 跟踪域精确 token 计数，两口径均有效、引用须标注） + `codebook.py:1487` notes 字面量 + `bank_fintech_collab/01_data_prep.do.tmpl:45` 错误文案 | 手写逐处（含 CLAUDE.md）+ 两处代码内字面量                                                                                                  |
| 7   | v8 历史复现（缓存键含全文+version，条目永久命中；盘上模板变 v9）                                                                                                                                                                                                                                                                                                                                                  | replication README 写明 checkout 历史 commit 口径                                                                                           |
| 8   | verify_stage21_cache_coverage（活 PROMPT_VERSION）                                                                                                                                                                                                                                                                                                                                                                | v9 后自动跟随，重验覆盖即可                                                                                                                 |
| 9   | tie-retry/force_refresh/三轨/ss 回退别名（见 §7 台账·第二轮审计 stage21 簇 P2 第 2 条：ss 回退与 full 缓存键共享条目 × tie-retry force_refresh 跨轨覆盖）                                                                                                                                                                                                                                                         | v9 重跑窗口一并受控处理                                                                                                                     |
| 10  | prompt 内 v7 连续性元叙述（:84）                                                                                                                                                                                                                                                                                                                                                                                  | step3 有动则重写该句                                                                                                                        |
| 11  | golden/dta 全量漂移 + 缓存库体积近翻倍                                                                                                                                                                                                                                                                                                                                                                            | 受控重生 + 磁盘预算 + manuscript 数值副作用披露                                                                                             |
| 12  | Stata 模板/paper_spec（列名不变，功能零影响）                                                                                                                                                                                                                                                                                                                                                                     | 仅#6 的 2 处文案                                                                                                                            |
| 13  | **entity_masking 活引用**（:146 import 活 PROMPT_TEMPLATE；fetch 不传 version）                                                                                                                                                                                                                                                                                                                                   | 掩码结论标 v8-scope 或随 G-v9-3 ②重跑（≈9k）；**若裁定重跑，须先补传 prompt_version**（镜像 WP-R1.1 ③，否则条目落 'v0' 命名空间无版本溯源） |
| 14  | **radius_sensitivity_llm**（launch 复用 run_all_llms，活 v9）                                                                                                                                                                                                                                                                                                                                                     | 半径结论同上，进 G-v9-3 ②决策                                                                                                               |
| 15  | **v7_wz_audit 读活 config**（:39-40，v9 后自动变 v9→缓存全 miss）                                                                                                                                                                                                                                                                                                                                                 | 弃用声明**已由 S8（批次 D）预先落地**；v9 时仅复核声明在位                                                                                  |
| 16  | **冻结阈值 sidecar**（v3_5_1 median×3 / benefit center）                                                                                                                                                                                                                                                                                                                                                          | G-v9-4 逐一显式裁定重锚 or 保留+披露                                                                                                        |
| 17  | **主树隔离**（候选字节入主树=全局 PROMPT_VERSION 翻转）                                                                                                                                                                                                                                                                                                                                                           | worktree/分支 + driver 显式路径（11.2-3）                                                                                                   |
| 18  | **归档多版本共存**（pilot v9 条目进 append-only jsonl；命中路径不归档）                                                                                                                                                                                                                                                                                                                                           | 账本多版本披露 + Zenodo 版本化增补；回炉留废弃记录属合法须披露                                                                              |
| 19  | data_versioning config_hash 含 prompt_version                                                                                                                                                                                                                                                                                                                                                                     | v9 后`--skip-unchanged` 全链拒跳全量重算=**预期**，防误判回归                                                                               |

### 11.5 §11 验收标准

1. V9-PRE-1（skip 守卫版本校验 + parquet 版本记录）先于任何 v9 播种落地并有 gate。
2. 非劣界/可比性桥阈值/pass 聚合规则在**任何 v9 付费请求发出之前**以 commit 锁定。
3. pilot 全部条目仅存在于 `_llm_cache_validation.db`，copy-on-pass 复制脚本有行数对账记录。
4. 桥表（帧① v8↔v9 逐维 κ + 帧② 双版本 vs 人工非劣）齐备于 eval_reports。
5. 11.4 十九点耦合走查逐点有勾（含 3 处测试锚、2 处代码内字面量、sidecar 裁定记录）。
6. G-v9-1 定稿与 G-v9-3 付费均有用户本人批准记录；v9 token 与字节自播种起冻结，新的"字节级冻结"gate（S1-v9）常绿；**终态冻结声明**已写入 CLAUDE.md（G-v9-4 ①）——计划执行完毕后任何提示词修改请求一律拒绝并指向本条。
7. **11.1-Q 十三条逐条有证据**：Q-A 检查单（scripts/audit/ 或 eval_reports，入 §9 收口记录）逐条打勾；Q-B 预登记 commit + 结果（含 test-retest 臂报告）；Q-C 审稿意见与 major 闭环记录归档。缺任一条，v9 不得进入 G-v9-4 全量重跑。
8. **注释/日志同步（§0-5 纪律）**：G-v9-4 收口时 §12 的 G-v9 运行时输出表逐行打勾（tone_llms 双 banner、codebook notes、`.do.tmpl` display、manifest anchor 联动），并对 `papers/_common/stata_templates/**/*.tmpl` 全量 grep 版本字面量单列一步（跨语言字面量不豁免）。

---

## §12 注释与日志同步台账（§0-5 纪律的逐条触点；实施各条目时按行打勾）

> 由只读调查逐条到码 grep 产出（2026-07-14）。列出的是**改动后会失真的现存文字**与**必须新增的日志**；「参照范式」= `tone_llms.py:749-757` 的 fix-tag 注释写法。表中"（勿动）"行为已正确的既有文本，作对照锚。

### 批次 A（M1/M2）

| 条目 | 文件:行 | 类型 | 现文（短摘） | 改后应写明 |
|---|---|---|---|---|
| M1 | `encode_collab.py:1207-1208` | docstring | "Sidecar JSON path: `data/processed/v3_5_1_constants.json`" | 路径经 config `output_dir` 解析（与 `manifest._resolve_sidecar_path` 同源），非 cwd 相对字面串 |
| M1 | `encode_collab.py:1260-1267` | 注释 | 只讲 preserve-if-set，不讲路径来源 | 补 fix-tag：路径与 manifest 同源，消灭双脑分裂（M1） |
| M1 | `encode_collab.py:1342` | log | `"v3.5.1: sidecar JSON 写入 {sidecar_path}"` | 变量自动跟随；迁移当次可加一条一次性 info 披露路径切换 |
| M1 | `manifest.py:190-199` | docstring | 只讲读侧已修 | 补一句"写侧 encode_collab 已于 M1 同步同源，双脑分裂闭环" |
| M1/M2 | `manifest.py:232-235,300-305` | log(warning) | "sidecar 不存在"/"prompt_sha256=None ⚠" | 文字不改；**验收动作**：M1/M2 后跑 write_manifest 确认这两条 WARNING 不再出现 |
| M2 | `manifest.py:9,65,146,258` | docstring+默认参数 | `archive_frozen_date='2026-05-18'`（"冻结"语义已漂） | 按 M2 裁定（滚动语义或披露）同步改注释："该日期=首个 5 文件批次，归档实为持续追加" |
| M2 | `manifest.py:415-418` | log(error) | verify 失败分支文案 | 不改；**验收动作**：重跑 `verify_manifest()` 确认此 ERROR 不出现、退出码 0 |

### 批次 B-1/D（M3 / S 组）+ 跨批次 N2（末三行；N2 归属人工窗口硬前置，证据登记见 §9 人工窗口行，非批次 B/D 收口范围）

| 条目 | 文件:行 | 类型 | 现文（短摘） | 改后应写明 |
|---|---|---|---|---|
| M3 | `tone_validation.py:729-731` | 代码+注释 | blind_cols 缺 target_bank | 加列 + 照抄 `llms_human.py:145-147` 注释风格（"实体匹配产物非模型预测，不破盲"） |
| M3 | `tone_validation.py:749-765` | 指导语文本 | 三轨全写"整体语调判断" | 三轨改"仅对 target_bank 目标银行的情感倾向，同行提及不传染"（对齐 `unified_cot.txt:20-21`） |
| M3 | `llms_human.py:171-172` | 指导语文本 | "基于标题+内容整体语调" | 与 tone_validation 新措辞**逐字对齐** |
| M3 | `llms_human.py:145-147` | 注释（勿动） | target_bank 白名单注释已正确 | 作 tone_validation 的照抄模板 |
| S2 | `00_LLMs_for_dic.py:1286` | 代码（无注释） | 阈值行裸写 | 补注释"严格多数(>50%=≥5/8)对齐发表词表 1506 实证口径；平票(=4)不再计入" |
| S2 | `00_LLMs_for_dic.py:1301,1309,1406-1414` | log/表头 | "AI认可"统计打印 | 紧邻加一行 info 声明口径=严格多数（S2）；表头不改 |
| S3 | `benefit_society.py:530-532` | docstring | "sidecar 记录 model_id…不匹配→fail-loud"（只提 model_id） | 改为三字段（+anchor_sha256/text_pipeline_version）；旧条目缺字段→warning+回填不改 center |
| S3 | `benefit_society.py:554-558` | raise 消息+新 log | 现仅 model 分支 raise | 新增两分支同款 raise 消息；回填分支配 `logger.warning`（明示"回填字段、不改 center 值、防当场崩 stage 40"） |
| S7 | `llm_peer_iv.py:420-426` | 注释 | "写入 LLMCache"先于"永久归档" | 照 omni-g-tonellms-04 范式写 fix-tag（archive 先行、失败跳过 put） |
| S7 | `llm_peer_iv.py:445-448` | log(warning) | "archive 失败(不阻塞 pipeline)" | 改为"归档失败，本次跳过 put，下次 run 重调并重试归档"（对齐 tone_llms:787-790） |
| S8 | `v7_wz_audit.py:1-4,40` | docstring+死 fallback | "用 v7 prompt"名实漂移 | docstring 改"读活 config 模板（现 v8）"+弃用声明（v9 后须 checkout 历史）；:40 fallback 注释化标注死分支 |
| S9/R1.1 | `prompt_sensitivity.py:215,283,360,404` | 变体文本 | "两项/两阶段" | 改"三项/三阶段" |
| S9/R1.1 | `prompt_sensitivity.py:270,276 等` | 变体文本 | 2 个 reason 字段×4 变体缺"须引用文章具体内容" | 8 处补齐（对齐 unified_cot:105,111） |
| S9/R1.1 | `prompt_sensitivity.py:1085-1086,1719-1721,1186-1188` | docstring+注释 ×3 | "P1 main spec = ctx / 总判定=三轨 AND" | 全部改 full-only 语义 + 新 fix-tag（WP-R1.1②） |
| S9/R1.1 | `prompt_sensitivity.py:1741` | **计算点（唯一）** | `passed = all(...)` | 切 full 轨驱动——与上行 6 处文字同一 commit 原子完成 |
| S9/R1.1 | `prompt_sensitivity.py:1450-1451,1543` | log(banner)×2 | "离线时缓存 miss 抛错而非偷跑"（与实际"整体优雅跳过"矛盾） | 改"离线时本阶段整体优雅跳过，勿与 stage21 miss→raise 混淆" |
| S9/R1.1 | `prompt_sensitivity.py:1745,1864-1868` | log(判定文案) | "通过（三轨）/全部有效轨道过线" | 改"full 轨 7 项过线→总判定通过；ctx/ss 供 conditional-on-full 披露" |
| S9/R1.1 | `prompt_sensitivity.py:649` | 代码(缺 kwarg) | fetch 未传 prompt_version（落 'v0'） | 补显式版本串（WP-R1.1③，播种前定稿） |
| S10 | `benefit_society.py:245-249` | docstring（会变谎话） | "致命错(鉴权/网络/配额/**离线闸**)兜底降级"——把离线闸也算进被吞范围 | 改为"离线闸 RuntimeError 必须穿透 re-raise，不属兜底范围（S10）" |
| S10 | `benefit_society.py:275-280` | 代码+log | except 打降级 warning | 先判 OFFLINE 真值 re-raise（不打降级 warning）；仅在线致命错走现有 warning |
| S12 | `LLMs_dic/config.py:180` | 注释 | "26 个领域"（实际 len=1） | 改实测数或 `len(DOMAINS)` 动态措辞，禁写死 |
| S12 | `02_analyze_log.py:108-110,201` | 正则+输出文本 | 失败正则失配"达到最大重试次数"；`/26` 硬编码 | 放宽正则 + `/{len(DOMAINS)}` |
| S13 | `benefit_society_placebo_keywords.yaml:25,66-78` | yaml 头注 | "应当不强烈响应 fintech 锚点"（与实现口径漂移） | 若保留词：紧邻补披露"智能柜员机与 fintech_dict 精确交集，方向保守，见 Table A10"；若删词头注不动 |
| N2 | `llms_human.py:183-196` | 代码（缺防覆写） | 直接 to_excel 无检测 | 写出前检测人工列非空→loud error+要求 --force-regenerate+旗标文件；log 含"检测到 {path} 已有 N 个非空标注→拒绝重生" |
| N2 | `llms_human.py:331-334` | log（范围不够） | 只警告旧单文件路径 | 新增独立 blind_A/B 覆写检测警告，勿与旧警告混用 |
| N2 | `manual_validation_sampling.py:228,230` | 代码（缺防覆写） | 两处 to_excel 无检测 | 同款拒绝机制+同款 log |

### 批次 F 与 §11 前置补遗（N1 / D5 / V9-PRE-1；第四次终审补齐的三处缺行）

| 条目 | 文件:行 | 类型 | 现文（短摘） | 改后应写明 |
|---|---|---|---|---|
| N1 | `papers/bank_fintech_locus/paper_spec.yaml:93` + `papers/bank_fintech_collab/paper_spec.yaml:123` | 注释（**现文已为假**——Panel C 只 confirm sub_frac，tech/collab 空指） | "真 FWER=根级 27_tableA12 Panel C" | 按 N1 处置分支同批改：扩 CLS 族 → 此句变真可保留；维持现状 → 改"tech_frac/collab_frac 真 FWER 待补（Panel C 现仅覆盖 sub_frac），如实声明" |
| D5 | `core/dag.py:199`（优先，SSOT）+ `policy_alignment.py`（15/16 混用 6 处）+ `radius_sensitivity_llm.py:1`（35/65） | 注释（编号残留） | "stage 13 物化 content_ctx"等旧编号 | 机械批改为现行编号；收口配 grep 复扫（§6-7） |
| V9-PRE-1 | `run_pipeline_function.py:377-385` | docstring（改完会变谎话） | "对比上游输入和已有输出的行数与内容指纹"（只字未提 prompt 版本） | 补一句"+ parquet 元数据 prompt_version 与当前 PROMPT_VERSION 一致性校验（V9-PRE-1）"；:739-749 两处 log 用变量插值 skip_reason 自动带出，无需逐条改文案 |

> 新增代码的 docstring 范式统一（软性，与 WP-R3 同规）：WP-R1.2 分层器、G-v9-2 pilot driver、copy-on-pass 复制脚本均比照 `verify_stage21_cache_coverage.py:1-41` 五段式（背景→构造→设计→防误用→白话）+ 显式退出码语义。

### §10 专项

| 条目 | 文件:行 | 类型 | 现文（短摘） | 改后应写明 |
|---|---|---|---|---|
| WP-R2 | `manual_validation_sampling.py:183-186,70` | 注释（会过期） | "T=2 仅 face-validity 哨兵…真值 deferred-T18"/"8 格 T=2 枯竭" | 生产真跑后更新为"已于 <date> 生产 T=18 运行，CI 见 eval_reports/<路径>"；枯竭表述按实况删改 |
| WP-R3 | 新脚本 | docstring 范式 | — | 照 `verify_stage21_cache_coverage.py:1-41` 五段式（背景→构造→设计→防误用铁律→白话）+ 显式退出码语义 |
| WP-R4 | `radius_sensitivity_llm.py:1,28-33,66,371-372` | docstring×4 | "Stage 35"/"脚手架状态"/"仍是 scaffold"/"留 future commit" | launch 落地后全部重写为真实工作流描述；stage 号随 D5 修正 |
| WP-R4 | `radius_sensitivity_llm.py:146-153,189-192` | 代码（NotImplementedError） | "尚未实现—拒绝静默占位" | 替换为真实 cache lookup+ensemble 实现，docstring 同步 |
| WP-R4 | `radius_sensitivity_llm.py:161,341` | 代码（cache 路径） | 两处指生产 `_llm_cache.db` | 分流两条路径（validation 库=新写 / parquet=baseline 读）各自加用途注释 |
| WP-R4 | `radius_sensitivity_llm.py:388,584` | **log(banner/运行时警告)** | banner 含 "scaffold/dry-run"；:584 每次 --launch 打印"当前 CLI 是 scaffold; 真实 launch 需再扩展 ~150 行" | **必删/替换**——落地后仍打印即假信息持续污染日志（最高危类） |

### G-v9（v9 落地时的运行时 v8 输出；补充 §11.4-#6，跨语言字面量单列）

| 文件:行 | 类型 | 现文（短摘） | v9 后处置 |
|---|---|---|---|
| `tone_llms.py:2152-2154,2226-2227` | log(banner)×2 | "Prompt v8 字节冻结" | 改动态读 `PROMPT_VERSION` 或显式 v9 |
| `codebook.py:1487` | notes 字面量（进 dta 生成物） | "median anchored to prompt v8" | 随 G-v9-4 sidecar 裁定二选一：改 v9 或保留+加"冻结于 v8 语料"披露句 |
| `papers/_common/stata_templates/bank_fintech_collab/01_data_prep.do.tmpl:45`（⚠ 仓库有 11 份同名 `01_data_prep.do.tmpl`，含版本文案的只有 collab 这份；根级模板 :45 是无关的 `$bank_controls` 自校验注释，勿开错） | Stata display（运行时用户可见） | "run v3.4.0 prompt v8 stage 21…" | 改通用措辞或同步 v9；**`papers/_common/stata_templates/**/*.tmpl` 全量 grep 版本字面量单列一步** |
| `manifest.py:64,144,257 + :100-101` | 默认参数+log | anchor='v8' 默认 + 动态打印 | 已在 §11.4-#3 参数化范围，确认其打印为运行时输出 |
| `fetch_llm_archive.py` / `verify_stage21_cache_coverage.py` | （已核实无硬编码） | — | 随 manifest 参数化/活 PROMPT_VERSION 自动跟随，无需单独改 |
