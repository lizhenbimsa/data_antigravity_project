# 银企共现面板双管道「基期冻结权重 + top-1 主办银行」替代聚合臂 — 执行计划 v3

日期: 2026-07-10 · 状态: **IMPLEMENTED (v3 已实施 2026-07-10; 双侧真跑×2 EXIT=0 + 手算对照 4 格 + 294 gate 全绿 + fast A/B 0 新增 + 三轮结果评审收口 SHIP)** · 作者: Claude
适用管道: `company_listed_bank` (上市公司×银行) + `company_tax_bank` (税调企业×银行), 双侧镜像同引擎。
v1→v2 修订史见 §11 (四路对抗评审: 引擎复用/设计计量/爆炸半径/运行实据; P0×6 + P1×8 + 事实错误×2 全落实)。

---

## §0 一句话目标与动机

为两条银企共现管道各新增 **2 个替代聚合权面板** (scheme 身份由文件名承载, 与既有八权/三权并排):

| scheme | 回应的识别威胁 | 顶刊锚 (§10) |
|---|---|---|
| `frozenw` 基期冻结权重 | cw 权重=当期共现份额, 与结果同源共动 (shift-share 时点内生) | Chodorow-Reich (2014, QJE); GPSS (2020, AER); BHJ (2022, ReStud); AKM (2019, QJE) |
| `mainbankw` top-1 主办银行 | 加权**均值**聚合函数被长尾共现稀释 (中小企业实际只有 1–2 家主办行) | Petersen & Rajan (1994, JF); Hoshi–Kashyap–Scharfstein (1991, QJE); Bharath et al. (2011, RFS) |

两臂正交且各与主 cw **差恰一个自由度**: frozenw 只动"权重的时点", mainbankw 只动"聚合的函数" (own-bank 处置四臂同源: pair 长表上游 02 D4 已剔自身银行, 双侧同, 04 零 own-bank 特判 — 见 D3)。全部走 **pair 长表 + 02 引擎复用**路线, $0 LLM (纯 CPU 后处理, 但含一次完整测度库构建, 非"轻量"), 不动 01/02/03 生产脚本、registry yaml、registry_sha256 锚、主仓 golden。

## §1 范围 / 非范围

### 1a 范围 (本计划做)
- 双管道各新增步骤 04 脚本 (`04_build_company_bank_altagg_panels.py` / `04_build_company_tax_bank_altagg_panels.py`)。
- 每管道产出 2×2 产物: `company_bank_{frozenw,mainbankw}_panel.{dta,parquet}` (tax 侧 `company_tax_bank_` 前缀) + 权重长表 `_company_bank_altagg_{frozen,mainbank}.parquet` (tax 同款前缀; 与 `_altweights_` 前缀无 glob 碰撞, 已核)。
- run_pipeline 双侧接线 (STEPS+04 及 §3-WP3 穷尽字面量清单)、README、codebook 04 章 upsert、gate 测试×2、三个既有测试文件同步。

### 1b 非范围 (刻意不做, 写进两侧 codebook 04 章归档, 一句话理由预答审稿人)
1. **GIV (cw−ce)**: 估计框架非测度稳健臂, 有效性依赖 Gabaix–Koijen 因子结构假设, 归宿=将来 paper 的 identification 章。两列相减随时可做, 不物化。
2. **Leave-one-out**: 真 LOO 须回文章级重算银行测度 (非 pair 表后处理); 窄版 (剔自身银行) 已被上游 D4 剔除天然覆盖, 无独立内容。
3. **关系存量/时间衰减权重**: 与 frozenw 答同一威胁, 冗余梯子 (先验判断, 审稿人质疑时经 pair 表实测)。
4. **frozen×mainbank 交叉臂**: 梯子禁交叉先例。
5. **tax 侧窗前 (2007–2010) 语料基期臂**: pair 长表被 02 裁到面板窗 2011–2020 (tax 02 `build_pair_table` L443–444), 窗前份额不在盘上; DEFER 生产机 (§9)。
6. **Stata 2SLS/AKM SE 模板**: papers 侧接入财务面板时再做; 本计划只落披露义务 (D10)。
7. **mainbank top-k (k≥2) 梯子**: top-k 加权是 top-1 与 cw 之间的插值臂, 冗余梯子; pair 长表在, $0 可重构, 不物化。
8. **strict/longhit 计数口径变体臂** (基期/argmax 按 `n_docs_strict` 或 `n_docs_longhit` 重算): 经 pair 表 $0 可重构, 刻意不物化 (防口径×scheme 列爆炸); ss 轨按 `n_docs` 含 fallback 口径判定基期与主办行, codebook 披露。

## §2 设计决案 (D1–D12, 承重; 改动前必读)

**D1 落地形态 = 新步骤 04, 上游 01/02/03 零代码改动。** 输入 = ① pair 长表 ② 五上游测度 DataFrame (与 02 同源同读法) ③ registry yaml (只读)。复用姿势 (全部 importlib, 序号前缀模块名非法标识符; 镜像 03 惯例; **tax 04 一律经 tax 02 的 `engine()` 惰性单例取 listed 引擎函数, 自身代码零 `company_bank`/listed token — 防 `_TAX_SCRIPTS` 跨管道污染扫描翻红**):
- `compute_weighted_panel(weights, measures, registry)` — listed 02 L659 (签名 v33 钉死, 第 4 参 chunk 有默认); **weights 消费面 schema**: 必需列 `company`(不得 NaN)/`bank`/`year`(int32 安全, 引擎 astype 对齐)/**`w`**(计数列必须叫 w), 可选 `track`(有→逐轨; 04 两 scheme 权重逐轨, 必须保留); 其余列静默丢弃; **隐含契约: (company,bank,year,track) 不得重复行** (重复=NUM/DEN 双计, 无内建防线; 04 的两种构造天然唯一, gate 锚死)。输出 index 名硬编码 `["company_listed_name","year"]` — **tax 04 照 tax 03 姿势按值 merge** (`left_on=["company_tax_name","year"], right_index=True`), 禁 `join(on=…)`。
- `write_outputs` — **双侧签名不同, 各用各的 02**: listed 02 L898 `(panel, registry, out_dta, scheme_word, fixed_labels)` **无 emit_dta 参数**; tax 02 L557 多 `emit_dta=True` + label≤80 断言。**listed 04 不提供 `--no-emit-dta`** (保 02 零改动, 三选一定案 (a)); tax 04 提供并接 run_pipeline 转发 (WP3)。面板公司列名必须精确 = `company_listed_name`/`company_tax_name` (write_outputs 按 get_loc 注入 stock_code/usci)。新诊断列不匹配 cw_/ce_ 前缀 → 原名直落 dta, 标签经 `fixed_labels` 参数注入 (03 调用姿势照抄)。
- 测度库同源调用序: `default_paths()` (config 键 = `output_21_tone_llms_full`/`output_40_panel_yearly`/`output_15_article_alignment`(值指向 16 文件)/`output_51_panel_controls`; benefit 无键, 脚本内常量 27 parquet) → `load_name_assets(registry)` (取 bank_canonical/company_names/bank_company_set) → `load_input21(p_input, bank_canonical)` → 四上游 read_parquet (缺→None) → `build_measure_library(五 DataFrame, registry)`。registry 载入镜像 02 L1290–1296: importlib 载 01 复算 `registry_content_sha256` 锚, 不自洽 → SystemExit。
- pair 长表载入校验镜像 03: 读 parquet metadata `registry_sha256`/`input_fingerprint`, 与盘上 registry 锚比对, stale → SystemExit (无锚即无面板)。
- codebook upsert: **04 各自自带 ≤12 行参数化 `_upsert_section(path, md, begin, end)`** (语义=tax 03 四参版 pre+block+post; listed 03 版标记对硬编码不可复用, 跨管道 import 又踩 token 扫描 — 双辙皆废, 自带最小实现并注明镜像来源)。标记对 = `<!-- BEGIN 替代聚合面板章 (04 生成, 勿手改) -->` / `<!-- END 替代聚合面板章 -->` (双侧同 token, 各写各的 codebook)。
- ⚠ **已知磨损 (接受+披露, 保 02 零改动)**: 两侧 02 `write_codebook` 整文件重写只保留 03 标记块 (listed 02 L1103–1109 / tax 02 CODEBOOK_ALT 对) → **单跑 `--steps 02`(,03) 后 04 章被抹掉, 直到补跑 04**。处置: README 级联义务写明 "重跑 02 ⇒ 04 产物与 codebook 章 stale, 须补跑 04"; 全链 01→02→03→04 无碍。

**D2 frozenw 权重定义 (canonical, 双侧统一)。** 逐 (company, track):
- `base_year` = 面板窗内首个 `n_docs > 0` 的年 (canonical 不门控 `n_docs`, 镜像主面板权宇宙; GPSS initial-share 构造)。三轨 base_year 逐轨独立、可不同 (轨内自包含, "权重与测度同轨"的严格延伸) — 跨轨并排判读时基期时点差是额外差异源 (非 bug), 覆盖表报"三轨 base_year 不一致公司占比"。
- weights frame = base_year 年该轨 pair 行 (w=当年 n_docs) **复制到 t ∈ [base_year, year_max] 每一年**; 归一化交给引擎 (cw 分母 = Σ(w·notna(X)) 逐 (company,year,track) 天然限非缺失重归一, 权重绝对量纲不影响 cw)。
- `t < base_year` → 不入 frame → 全列 NaN (**左截断, 不回退当期权重** — 回退即重新引入时点内生, fail-closed)。
- `t ≥ base_year` **权重恒有定义; 加权值有值的前提 = 冻结集合内至少一家银行该年测度非缺** — 基期银行整体退出银行面板/测度全缺 → 该格 NaN (**第三缺失通道**, 与 D10⑤ 对齐义务联动披露)。当年零共现不影响有值 (冻结暴露与当年新闻流量刻意解耦, 构念特征)。
- ce 臂 = 引擎对 frame 内银行集合的等权均值 (mean skipna, 不看 w) = **基期银行集合等权** — 有独立信息的稳健臂 (与主 ce 的"当年集合等权"不同)。
- 银行当年测度缺失 → 引擎限非缺失重归一 (披露: 重归一后非严格 shift-share; 生产机验证轮量化重归一触发占比)。
- own-bank: pair 长表上游 02 D4 已剔自身银行 (双侧同; listed 02 L356 / tax codebook "own-bank 剔除后其行保留"), 04 零特判, 四臂 (主 cw/ce + frozenw + mainbankw) 同源承接。

**D3 mainbankw 定义 (canonical, 双侧统一)。** 逐 (company, year, track):
- main bank = 当年该轨 `n_docs` argmax (时点=当期, 与主 cw 同时点 — 保持与 frozenw 正交)。
- **确定性平票规则** (三级): `n_docs` → `n_docs_longhit` → 银行 canonical 名 Unicode 码点升序; 平票发生 (第一级并列) → `main_bank_tie=1`。
- own-bank: 同 D2, 上游已剔, argmax 天然选不到自己, **无 drop_own_bank 步骤** (v1 该设计经代码实证撤销: listed 02 L356 D4 内联跳过 own-bank, tax 同款; 03 的 drop_own_bank 是给贷款/董监高等外部权源用的, 与 pair 表无涉)。
- weights frame = 每格单行 (main bank, w=1.0) → 引擎 N=1 短路给出 cw = X_main **逐位** (取原值无浮点运算), ce = mean(单值) ≡ cw **逐位恒等**; X_main 缺失 → 两臂同步 NaN。**mainbankw 的 ce 列无独立信息** (恒等结构冗余, 分析端任取一臂, 镜像替代权面板 track-agnostic 列恒等先例; 与 frozenw 的 ce=独立臂不同), codebook 逐 scheme 写明 ce 信息地位。
- **main bank 当年某测度在银行面板缺失 → 该格该列 NaN (严格 top-1, 不顺延次位)** — 顺延即按测度可得性重选银行 (重新引入选择内生性, 且 main_bank 身份逐列漂移); 引擎空分母自然给出该行为, 04 零特判。gate 负例锚死; 覆盖表报 main-bank 测度缺失格点占比。

**D4 行宇宙与缺失语义。** 两面板 = 满骨架 company×year (listed 5,528×19 / tax 44,771×10, 与主面板同); **公司序钉死 `sorted(company_names)`** (随 03 替代面板族先例; 02 用 yaml 原序, 两先例冲突处 04 归 03 系, R2-P2-7)。mainbankw 无当年共现格点 → 全列 NaN; frozenw 按 D2 三通道 (左截断 / 冻结集合测度全缺 / 全轨零共现公司整行 NaN)。诊断列缺失语义与 dtype **逐列钉死** (v1 "int16+NaN" 自相矛盾已修):

| 列 | dtype | 缺失语义 |
|---|---|---|
| `base_year_{track}` (frozenw) | float64 | NaN = 该轨窗内无共现 |
| `frozen_n_banks_{track}` (frozenw) | float64 | 基期银行家数; NaN 同上 (**不填 0**, 面板计数填 0 语义仅适用主面板 n_cooc 族) |
| `main_bank_{track}` (mainbankw) | str | 缺失 = **空串 ""** (pyreadstat 实测 NaN 落 Stata 空串非 `.`; codebook 显式披露字符串缺失口径与数值列不同套) |
| `main_bank_share_{track}` | float64 | ∈(0,1]; NaN = 无共现 |
| `main_bank_tie_{track}` | float64 | 0/1; NaN = 无共现 |

**D5 门控双宇宙镜像。** 权重 = canonical 不门控 `n_docs`; 测度 = verified 宇宙 (registry emit 子集, 与 02/03 完全同源)。04 不另起口径。

**D6 列 schema。** 加权列 = registry 同一 emit 子集 × `cw_/ce_{D16 短名}_{track}`, **registry yaml 零改动, sha 锚不 bump**。诊断列名全部 ≤32 字符 (最长 `main_bank_share_full`=20, 已核)。固定标识列 = listed: company_listed_name/stock_code(write_outputs 注入)/year/is_bank_company; tax: company_tax_name/usci(注入)/year/is_bank_company。is_bank_company 由 registry `bank_company_map` 键集派生 (与 02 同源)。

**D7 track 语义。** 两 scheme 权重**逐轨** (与媒体主面板同语义, 与替代权面板 track-less 权重不同 — codebook 章写明防套错)。某公司仅单轨有共现 → 无共现轨全列 NaN 不连坐有共现轨 (gate 用例)。

**D8 确定性。** 纯 pandas groupby/argmax (n_docs=int32 无浮点歧义), 无 BLAS 重矩阵; 确定性验证用**列内容哈希** (dta 头嵌时间戳禁 file-SHA); PYTHONHASHSEED 由 run_pipeline `setdefault("0")` 承接。**mainbank 取行姿势钉死 (R2-P2-4)**: `sort_values(多键)` (np.lexsort 稳定) + `drop_duplicates(subset=[company,year,track], keep="first")` — **行原子**; 禁 `groupby.first()` (pandas 2.2.x 逐列取首个非 NaN 值, 格内跨行拼装暗雷) 禁裸 `idxmax`。覆盖表加报"仅靠第三级名序裁决的格点占比" (二级 longhit 常与一级同平, 第三级实际频繁承重)。同输入双跑列哈希恒等 = gate 用例。

**D9 日志与运行卫生。** `logs/04_*.log` 扁平覆盖式 (盘上无同名, 已核); `PYTEST_CURRENT_TEST` 守卫 (镜像四脚本先例, 并入既有 `test_pytest_never_touches_stage_logs` parametrize); 单实例锁由 run_pipeline 持有; 全量数字 `%.4g`; RSS psutil 惯例。**引擎日志归宿 (R2-P2-6)**: 引擎 budget/chunk WARNING 走 listed-02 logger — **双侧 04 各自带 `_attach_engine_logging`** (own stem 改名 Filter + 自身文件 handler + PYTEST 守卫, 镜像 tax 03 L122–137; **勿照抄 listed 03 — 它没做**), 否则 04 日志缺引擎行且错归 02 阶段名。**日志引文只引已在 audit_dois 池的 5 条** (GPSS/BHJ/AKM/Petersen-Rajan/Khwaja-Mian, 逐条已核在池); Chodorow-Reich/HKS/Bharath **不入日志**, 进 codebook 散文引用不带 DOI (镜像 codebook 既有 "AKM 2019" 散文先例; 不碰 audit_dois.py — 当前是并发会话脏文件)。引擎 budget env: 04 weights frame 量级 (dev ~6k/2.2k 行; 生产 ≈ pair×年窗深线性) 远小于 03, 默认预算充裕, **不注入** budget env (§6 记录)。

**D10 frozenw 发表义务五句 (codebook 章必含, 非可选)。**
① shift-share 推断须 exposure-robust SE (AKM 2019), 常规聚类 SE 过窄。
② 基期=首个入样共现年属研究者选择 (GPSS 2020 initial-share), pair 长表在, 可 $0 重定基期 (D17 通道)。
③ 识别假设 = 基期份额对企业结果的影响仅经银行冲击通道 (exogenous shares 叙事)。
④ **staggered 基期三重偏离**: 基期年逐公司异质且与媒体首次可见时点相关 (非统一 pre-period 快照) — 识别叙事须条件于公司首现年成立; 基期时点本身内生于媒体可见度; 基期越晚 frozen 与当期权重越收敛 (去内生化力度异质衰减)。生产机验证轮加报 frozen-vs-当期权重向量逐年 Spearman 作稀释诊断。
⑤ **共同样本对齐义务**: frozenw 与主 cw/ce 的非缺失格点集合**互不包含** (左截断缺 t<base_year / 解耦语义在零共现年有值而主面板 NaN / 冻结集合测度全缺第三通道) — 两臂并排对比一律先取共同非缺失样本 (common support) 再估计, 禁在各自全样本上直接比系数; 覆盖表报两臂非缺失格点交/并集数与错位方向分解。

**D11 codebook/文档接线。** 04 收尾用自带 `_upsert_section` 写「替代聚合面板章」(标记对见 D1), 内容: 两 scheme 定义/D2–D8 全部口径/D10 五句/ce 信息地位/字符串缺失=空串/ss fallback 口径/覆盖表 (逐年 base_year 分布 + 三轨 base_year 不一致率 + mainbank 非缺格点与 tie 率 + 重归一触发与测度缺失占比 + frozen-cw 交并集) /§1b 八条刻意不做/**铁律衔接句**: "本章 2 面板与主面板/七权(listed)或双替代权(tax)面板并排 — 合计聚合臂 listed 10 / tax 5, 03 生成的『禁八(三)面板横向 merge』铁律与 02 总览表『×7(×2)』计数不含本章产物, 铁律对全体面板成立"。README 双侧: 产物表+04 (listed "26 文件"→32 / tax 磁盘 "约 40GB 级"→约 55GB 级, tax 04 双 dta 各 ~6.9GB)、执行顺序+04、**级联义务 01→02→03→04** (pair 重生 ⇒ 04 stale; 重跑 02 抹 04 codebook 章 ⇒ 补跑 04)。

**D12 dev 预期退化 (判读预答)。** 双侧 dev 语料仅 2017–2018 非零 (tax 窗 2011–2020 内 **8/10 年零共现**, 比 v1 表述更极端, 日志判读段按实况写); listed base_year 分布 2017=589/2018=198 单元, frozen 仅 2018 有非平凡冻结差; **base_year=窗末年公司 frozen≡cw 逐点恒等属构造退化非 bug**; skew 类比先例同款。gate 全用合成 fixture 不依赖盘上数据。

## §3 工作包 (WP1–WP6, 依赖序)

**WP1 — listed 04 脚本** (`company_listed_bank/04_build_company_bank_altagg_panels.py`)
1. importlib 载 02 (engine 函数族+载入函数+FIXED 常量) 与 01 (registry sha 复算)。
2. 读 pair 长表 + metadata stale 校验 (缺/stale → SystemExit, 提示先跑 02)。
3. `build_frozen_weights(pair, year_max)` → 逐 (company,track) base_year → 基期行展年 → weights frame (含 track, w=float(n_docs))。
4. `build_mainbank_weights(pair)` → 逐格三级平票 argmax → 单行 frame (w=1.0) + 诊断三列源数据。
5. 两次 `compute_weighted_panel` → 满骨架合并 (**姿势钉死, R2-P1-1**: 骨架 `MultiIndex.from_product(company_names × years)` 只承载固定/诊断列; 加权列一律**按值 merge** `panel.merge(weighted, how="left", left_on=[公司列,"year"], right_index=True)` 镜像 02 L1415/03 L1184; **明文禁 `weighted.reindex(骨架)`** — 混 dtype level 的 get_indexer 有全 -1 静默全 NaN 雷, 引擎 L643 自己写明; 面板 year 落盘前 `astype("int16")` 与主面板一致) → 拼诊断列 (D4 dtype 表) → 两次 `write_outputs` (scheme_word="基期冻结"/"主办银行")。**禁复用 02 `run_gates`** (其 gate⑧ "n_cooc==0⇒cw/ce 全 NaN" 对 frozenw 结构性不成立); 04 自带内联 gate (frame 键唯一性/mainbank cw≡ce/base_year 值域/share∈(0,1]/**frozen 面板存在非 NaN 加权值** — 防 merge 键错配静默全 NaN)。
5a. **年窗来源钉死 (R2-P1-2): 禁从 pair 数据推年窗** (dev pair max=2018, 推导必产窄面板)。listed 04 argparse `--year-min/--year-max` 默认 **2007/2025** 字面量 (注明系 02/03 argparse 默认的第三副本, 无模块常量可 import); tax 04 直接 import `tax02.PANEL_YEAR_MIN/MAX` (2011/2020)。gate 锚死行数不变量 (listed 5528×19 / tax 44771×10)。
6. 权重长表 ×2 落 `_company_bank_altagg_{frozen,mainbank}.parquet` (metadata 内嵌 registry sha, 镜像 pair 表)。
7. 日志: 阶段头+口径+铁律段+覆盖诊断 (D11 清单) + D9 在池 5 条引文 + dev 退化判读段。
8. codebook `_upsert_section` + argparse (`--pairs/--output-dir`, 默认自足 — run_pipeline 子进程不带参调用)。**无 `--no-emit-dta`** (D1 定案 (a))。

**WP2 — tax 04 镜像** (`company_tax_bank/04_build_company_tax_bank_altagg_panels.py`)
与 WP1 同构; 差异: 经 tax 02 `engine()` 取引擎 (自身零 listed token)、merge 键 usci/company_tax_name、年窗 2011–2020、tax 02 的 write_outputs (**支持 `--no-emit-dta`**)、按值 merge 姿势 (D1)。镜像纪律: 结构逐节对齐, 差异集中头部常量块。

**WP3 — run_pipeline 双侧接线 (爆炸半径审计穷尽清单, grep 驱动逐处)**
- 双侧: STEPS += ("04", 脚本名, 描述); `_iter_artifacts` +04 分支 (2 面板×2 格式+2 长表; tax 版接 no_emit_dta 语义); **listed `_iter_artifacts` step-03 分支 glob `company_bank_*w_panel.*` 排除 frozenw/mainbankw 前缀** (否则 04 产物误归 03 名下; tax 侧 `branch_` 前缀天然隔离零改动); `_log_step_context` +04 段; `_log_run_summary` "三步 rc 全 0"→四步 +04 判读; 跳步预检集合 `{"02","03"}`→`{"02","03","04"}` (listed L474/tax L500); 04-未选-02-且-pair-缺 预检 (可并入 03 同分支); docstring/banner/argparse 全部 "三步"/"01→02→03" 字面量 (listed L3,12,245,249,253–256,265,325,354,381,383; tax 对应行) 逐处翻; gate 计数 banner listed "12+58+54+5=129" / tax **"15+61+47+6=129"** (两侧字面量构成不同, 按各自式样改为五件新总数, 勿用 listed 式 grep tax)。
- tax 独有: `--no-emit-dta` 转发白名单 `("02","03")`→`("02","03","04")` (L518)。
- README ×2: D11 清单。

**WP4 — gate 测试** (新增 2 文件 + 3 个既有文件同步)
新增 `tests/test_company_bank_altagg.py` + `tests/test_company_tax_bank_altagg.py`, 合成 fixture + mock 读盘, 每侧覆盖:
1. frozen: base_year=首个 n_docs>0 年 (含跨轨不同 base_year; 单轨覆盖公司无共现轨全 NaN 不连坐)。
2. frozen: t<base_year 全 NaN (负例: 若回退则有值的格点断言 NaN)。
3. frozen: t≥base_year 权重恒等基期份额; 当年零共现格仍有值; **基期银行测度全缺 → NaN (第三通道负例)**。
4. frozen: 重归一=冻结集合内限非缺失 (手算对照)。
5. frozen: ce=基期集合等权 (手算, 与主 ce 不同值用例)。
6. mainbank: argmax+三级平票各一正例+tie 旗标。6a. frozen: **base_year=窗末年 frozen≡cw 恒等退化用例** (对应 D12)。
7. mainbank: cw≡ce 逐位恒等 (非 isclose)。
8. mainbank: **main bank 测度缺、次位有值 → NaN 非次位值 (严格 top-1 负例)**。
9. 缺失语义: 无共现格 NaN 非 0; 满骨架行数=公司×年; 全零公司整行 NaN。
10. 确定性: 同输入双跑列内容哈希恒等; **weights frame (company,bank,year,track) 唯一性锚**。
11. 列名=registry emit×D16 短名双射; 诊断列 dtype/标签≤80 字符 (tax 断言)。
12. 原子写 (.tmp 无残留) + PYTEST_CURRENT_TEST 守卫; tax `--no-emit-dta` 行为。
13. registry sha 不变锚 (读既有 EXPECTED 常量对比盘上)。
14. `_upsert_section` 三用例 (R2-P1-3): 幂等双跑仅一块 / 保全他人 (03) 标记块内容逐字节不动 / 无标记时 append 到尾。
**fixture 纪律 (R2-P2-5)**: 合成 registry 复用 `test_company_bank_cooc_panel.py::mini_registry/entry` SSOT (12 字段); gate 直接调 build_* 纯函数**绕过** main() 的 sha 复算/pair metadata 闸; write_outputs 类用例 (原子写/dtype/--no-emit-dta) 豁免 mock, 用真实名单公司名 (stock_code/usci notna 断言对合成名必崩) 或 monkeypatch `stock_code_map`/`usci_map`。
既有文件同步 (v1 "lock 测试 STEPS 锚"系事实错误, 两 lock 测试无此锚、预期零改动仅确认零红灯; 真改动是这三个): ① `test_company_tax_bank_cooc_registry.py` `_TAX_SCRIPTS` 元组 (L81–86) += tax 04 脚本名 (tax 04 零 listed token → 无需动 `_XPIPE_TOKEN_WHITELIST`); ② `test_company_bank_cooc_panel.py` L441–446 `test_pytest_never_touches_stage_logs` parametrize += listed 04 stem; ③ `test_company_tax_bank_cooc_panel.py` L518–523 同款 += tax 04 stem。

**WP5 — codebook + 归档** (D10 五句 + D11 全部内容 + §1b 八条落地)。

**WP6 — 验证与收尾**
1. **前置: 等并发会话 listed run (锁 PID 10300) 结束、锁释放**; 磁盘余量核查 (tax +~14GB / listed +~3.2GB)。
2. 双侧 `run_pipeline.py --steps 04` 真跑 EXIT=0; 再全链 `--steps 01,02,03,04` EXIT=0 (registry 锚恒等)。**磨损处置三段可操作断言 (R2-P1-3)**: ① 跑 `--steps 02,03` 后 grep codebook — 04 标记**应缺席** (磨损按预期发生); ② 补跑 `--steps 04` 后四个标记 (03 BEGIN/END + 04 BEGIN/END) 全在且 03 块内容非空 (04 upsert 不反噬 03 章); ③ 双跑 04 后 codebook 仅一份 04 块 (幂等)。
3. pytest: 新 gate 全绿; 既有 gate baseline-stash A/B 差分 0 新增失败 (churn 隔离; FAILED 全量 Select-String 抓取禁截尾)。
4. 产物核对: 列数=主面板加权列数+各自诊断列; frozen 1 格 + mainbank 1 格逐数字手算对照。
5. 提交: **by-name** — 新增 04×2/gate 测试×2/本计划; 改动 run_pipeline×2/README×2/三个既有测试文件; **run_pipeline/README 含并发会话未提交 F12 hunk → 提交时按 hunk 拆 patch `git apply --cached` 只锚自己的 hunk** (共享树先例); 排除 data/logs/constants.json/audit_dois.py/一切并发产物。

## §4 验收清单

- [ ] 双管道 04 真跑 EXIT=0, 四面板落盘, 列数恰等预期
- [ ] 新 gate ≥13×2 全绿; 既有 gate (双侧各 129 族; v1 "listed 95" 系陈旧数已更正) A/B 0 新增失败
- [ ] registry sha 双侧恒等; git diff 零 config 改动
- [ ] frozen/mainbank 各 1 格逐数字手算对照通过
- [ ] codebook 04 章 (D10 五句/铁律衔接/覆盖表) + README 级联义务在位; "三步" 字面量 grep 零残留
- [ ] 日志引文 5/5 命中池; Chodorow-Reich 等 3 条仅 codebook 散文
- [ ] by-name 提交 (hunk 隔离并发改动), HEREDOC+Co-Authored-By, 不 amend 不 --no-verify

## §5 确定性 / golden / registry 安全声明

零接触: 主仓 32 阶段、OUTPUT_REGISTRY、golden、`_llm_cache.db`、两管道 01/02/03 脚本、registry yaml 与 sha 锚、constants.json、audit_dois.py。新增均为 additive 下游后处理; 回滚 = 删 04×2+gate×2, 还原 run_pipeline/README/三测试 hunk。

## §6 风险与预答

| 风险 | 预答 |
|---|---|
| frozen 基期份额被基期年单年噪声主导 | GPSS 框架披露项; pair 表在可 $0 多年均值重定基 (D17), 不预物化 |
| mainbank 聚合击穿点=0 (单篇误配即翻转主办行, 均值臂仅被稀释) | 构念代价非 bug; 稳健读法=与 cw 并排+`main_bank_share` 低值格降权判读; longhit 仅平票裁决级非噪声防线; 生产机抽样第二轮量化 main bank 翻转率 (v1 "短名精度预答"答非所威胁, 已重写) |
| 04 墙钟含完整测度库构建 (load_input21+build_measure_library) | 非"轻量"但纯 CPU $0; dev 分钟级; 生产与 02 同量级可接受 |
| weights frame 内存/budget | dev ~6k/2.2k 行, 生产 pair×年窗线性; 默认引擎预算充裕, 不注入 budget env |
| tax 04 双 dta 磁盘 +~14GB | WP6.1 前置余量核查; `--no-emit-dta` dev 可跳 |
| 重跑 02 抹 04 codebook 章 | D1 已知磨损, README 级联义务承接, 保 02 零改动 |
| dev frozen≈cw 被误判无效 | D12 预答 (base_year 几乎全 2017, 仅 2018 有冻结差) |

## §7 铁律 (一段话)

新增 2 权与既有 listed 八权 / tax 三权、三轨、cw/ce 两臂: 互为稳健性、不分主次, 各自 just-identified 并排, **禁混同一 over-identified Hansen J, 禁面板横向 merge, 禁同一 RHS 并置多权重版本同名测度** (horse-race 显式标注豁免); frozen×mainbank 禁交叉; 报告层 canonical 仍为主面板 cw (headline), 计量地位对等 ≠ 报告位置随意。

## §8 工时与顺序

新文件 (04×2, gate×2) 先行 (与并发 run 零冲突) → 等锁释放后改 run_pipeline/README/三测试 → WP6。R2 复核评审 (两路: 修订闭环验证 + 新鲜对抗) 通过后开工。

## §9 DEFERRED (生产机义务)

1. 生产语料重跑双管道全链后: 覆盖表/精度抽样第二轮/重归一与测度缺失占比/frozen-cw Spearman 稀释诊断/main bank 翻转率 回填 codebook 字段终值。
2. tax 窗前 2007–2010 基期臂 (§1b-5): 02 隔离输出参数跑宽窗 pair (勿覆盖主产物) + 04 `--base-window`; 生产机评估覆盖率再议。
3. papers 侧 2SLS + AKM SE `.do` 模板。
4. manuscript 披露段 (D10 五句进相关 paper measurement 章)。
5. Chodorow-Reich/HKS/Bharath 三条 DOI 补入文献锚点池 (下次 litanchor 轮; 届时 04 日志引文可扩)。

## §10 顶刊锚点清单

**日志可引 (已核在池)**: Goldsmith-Pinkham, Sorkin & Swift (2020). Bartik instruments: What, when, why, and how. *AER*, 110(8), 2586–2624. doi:10.1257/aer.20181047 · Borusyak, Hull & Jaravel (2022). Quasi-experimental shift-share research designs. *ReStud*, 89(1), 181–213. doi:10.1093/restud/rdab030 · Adão, Kolesár & Morales (2019). Shift-share designs: Theory and inference. *QJE*, 134(4), 1949–2010. doi:10.1093/qje/qjz025 · Petersen & Rajan (1994). The benefits of lending relationships: Evidence from small business data. *JF*, 49(1), 3–37. doi:10.1111/j.1540-6261.1994.tb04418.x · Khwaja & Mian (2008). Tracing the impact of bank liquidity shocks: Evidence from an emerging market. *AER*, 98(4), 1413–1442. doi:10.1257/aer.98.4.1413。

**codebook 散文引 (不带 DOI, 池缺待 §9-5 补)**: Chodorow-Reich (2014). **The employment effects of credit market disruptions: Firm-level evidence from the 2008–9 financial crisis.** *QJE*, 129(1), 1–59. ⚠ 同作者同年另有 BPEA "Effects of unconventional monetary policy on financial institutions" 易混篇, **禁引错** (v1 双题并列已删, 锁 QJE 篇) · Hoshi, Kashyap & Scharfstein (1991). Corporate structure, liquidity, and investment: Evidence from Japanese industrial groups. *QJE*, 106(1), 33–60 · Bharath, Dahiya, Saunders & Srinivasan (2011). Lending relationships and loan contract terms. *RFS*, 24(4), 1141–1203。

## §11 v1→v2 修订史 (四路评审 2026-07-10)

- **[引擎-P0]** listed `--no-emit-dta` 断链 → 定案 (a) listed 04 不提供 (D1); tax 04 提供+转发白名单 (WP3)。
- **[引擎-P0]** upsert 复用来源错 (listed 03 标记硬编码) → 04 自带参数化 `_upsert_section` (D1)。
- **[引擎-P0]** `base_year int16+NaN` 自相矛盾 → 诊断列 dtype×缺失语义逐列钉死表 (D4); str 缺失=空串披露。
- **[引擎-P1]** 02 重跑抹 04 章磨损披露+级联义务 (D1/D11); 禁复用 02 run_gates (WP1.5); weights 唯一性契约 gate (WP4.10); 测度库调用序+bank_canonical 入参 (D1); tax 按值 merge 姿势 (D1)。
- **[设计-P0]** 共同样本对齐义务 (D10⑤); 第三缺失通道修 D2 表述; mainbank 严格 NaN 不顺延 (D3+WP4.8)。
- **[设计-P1]** staggered 基期三重偏离 (D10④); §6 mainbank 击穿点=0 重写; §1b+top-k/strict 两条归档; 铁律衔接句 (D11); Chodorow-Reich 锁 QJE 删 BPEA (§10); ce 零信息警示 (D3); 三轨 base_year 不一致率披露 (D2)。
- **[设计-撤销]** "listed/tax own-bank 处置不对称"说经代码证伪 — 双侧 02 均在 hits 层 D4 剔 own-bank (listed 02 L356), **drop_own_bank 整条移除** (D3), §0 单自由度声明恢复成立。
- **[爆炸-P0]** listed `_iter_artifacts` 03-glob 误捕 04 产物 → WP3 排除前缀; "lock 测试 STEPS 锚"系事实错误 → 真改动=三个测试文件 (WP4); "listed 95"→129 (§4)。
- **[爆炸-P1]** 预检集合/tax 转发/12 处"三步"字面量/README 文件数与磁盘量/级联义务/`_TAX_SCRIPTS`/parametrize stems — 全数并入 WP3/WP4/D11。
- **[实据]** 3 条 DOI 不在池 → D9 日志 5 条+codebook 散文 3 条分流, audit_dois.py 零接触; 并发 run 进行中 → WP6.1 前置等锁+§3-WP6.5 hunk 隔离; tax dev 8/10 空年判读 (D12)。

### v2→v3 (R2 两轮复核 2026-07-10)
- **[闭环]** v2 全部 §11 修订项逐条核实落点, 判定可开工; 3 处一行级修正 (D6 最长列名示例=main_bank_share_full 20 / WP3 tax banner 字面量 "15+61+47+6=129" 双式样 / WP4.6a 用例分组归 frozen)。
- **[对抗-P1]** WP1.5 合并姿势钉死 (骨架只承载固定列, 加权列按值 merge, **禁 reindex** — 混 dtype 全 -1 雷; year 落盘 astype int16; 非 NaN 存在锚); WP1.5a 年窗来源钉死 (**禁从 pair 推**; listed 04 字面量 2007/2025 第三副本+CLI 参, tax import PANEL_YEAR_MIN/MAX; 行数不变量锚); WP6.2 磨损三段可操作断言 + WP4.14 `_upsert_section` 三用例。
- **[对抗-P2]** D8 mainbank 取行=sort+drop_duplicates 行原子 (**禁 groupby.first** 逐列非 NaN 拼装雷/禁裸 idxmax) + 第三级裁决占比披露; WP4 fixture 纪律 (mini_registry SSOT 复用/绕 main 闸/write_outputs 用真名或 monkeypatch); D9 双侧 04 自带 `_attach_engine_logging` (勿照抄 listed 03); D4 公司序钉死 sorted (归 03 系)。
- **[实据更新]** F12/F2F3 脏 hunk 与 04 改动区不重叠 (hunk 隔离可行, README 脏 hunk 按内容识别勿按标签); 双侧锁文件已消失 (并发 run 已结束, WP6.1 前置此刻满足)。
