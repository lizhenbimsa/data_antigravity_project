# 网络指标三轨化 (①类) + 网络构造判据敏感性 (②类) 执行计划

**日期**: 2026-07-02 (v2 修订 2026-07-03)
**状态**: v3 定稿 — 8-lens 对抗评审 (24→19 确认) + 双 agent 终审 + **6 专项终验门禁 (wf_1b6c39b7-a82: 29 条事实全量重核 0 broken / 1 major + 11 minor 全部落入本文)** → **已批准实施**
**基线**: ⭑⭑ main=**e39955d0** (终验时 HEAD; 原基线 6805475a 后 5 个并发 commit, 含 41886246 改动 encode/codebook/stata_export/tone_llms 四文件 + 新增根级模板 28_tableA13 → 计数 146→**147**)。⚠ **本文全部行号引用按函数名定位, 禁按行号盲改** (四文件行号已系统性漂移, 终验 facts 重核给出新锚: encode neg_count 聚合 ~:734-757 / 分母 ~:902-914; stata_export anchor ~:531-569; tone_llms 门控 ~:2898; codebook 推断 ~:2034-2097)。§4 baseline-stash A/B 以**当前 HEAD** 为 baseline。
**侦察**: 4-agent (wf_4f22970c-160); 评审: 8-lens×2票 (wf_22920e55-e32); 终验: 6 专项 (wf_1b6c39b7-a82); 台账见 §7

---

## §0 关键已核验事实 (侦察+评审实测, 改动前提)

### ①-A industry_neg_shock
- **F0.1** 分子已存在: encode.py:700-716 逐轨产 `neg_count_{full,ctx,ss}`; 盘上 40_panel_yearly.parquet 三列俱在 (nonnull=220), golden fixture 已含 neg_count_ctx/ss。
- **F0.2** 分母已存在: `n_articles_llm_valid` (full, encode.py:857) / `n_articles_llm_valid_ctx` (:866) / `n_articles_llm_valid_ss` (:869)。T=2 实测 full=1005 / ctx=932 / ss=891 严格递减子集 (conditional-on-full 语义自洽)。
- **F0.3** network_brokerage.py:678-682 的 no-ss-track 护栏注释**事实前提已失效** (「encode 仅产 neg_count_full」为陈旧陈述), 与 codebook.py:676-699 (已为 neg_count 三轨精写元数据) 直接矛盾。
- **F0.4** 现实现分母回退链 `_nac = n_articles_llm_valid else n_articles` (network_brokerage.py:696) 是 full 轨口径; encode 曾修复过「ctx/ss 分子配 full 分母 → frac 越界 3.0」的轨道不对称 bug (encode.py:858-865, c8a70ac5)。
- **F0.5** 运行时消费点 8 处: runner.py:152,2042-2045 / stata_export.py:412 (仅 lag1 有 HEURISTIC 标签) / export.py:1197-1199 / brokerage paper_spec.yaml:114 (仅 lag1) / tables.py:18 / 15_table6 模板:50,52 / stata/08_label_network.do:53 / fire_sale 交乘 (network_brokerage.py:841-855, 消费**同期** shock)。
- **F0.6** T=2 dev 实测 (评审 identity-trap-2 复核): **ss 与 ctx 两轨的新 shock 列全部零方差退化** — neg_count_ss 全盘 sum=0; neg_count_ctx sum=1 但唯一负例银行的 n_articles_llm_valid_ctx=2 < min_count=5 被守门置 NaN → `industry_neg_shock_{ctx,ss}` 及其 lag1 在 dev 上均 ≡0 (触零方差 WARN 路径 L758-760); 仅 full 轨有方差 (std≈0.0013)。数值验证 DEFERRED 生产机 (17M/T=18 铁律); §9 基线记录三轨。

### ①-B 认知邻近 / 嵌入相似网
- **F0.7** `bank_cogn_mean` = 纯本地 TF-IDF (char_wb 2-4gram, network_spillover.py:1373-1395), **零嵌入 API**, 三轨化 $0。文本源硬编码 `'内容'+'标题'` (:1325-1353), 输出仅 1 列, [0,1] 值域守卫 + **100 字符最短守卫 (:1361-1362, 该守卫为 cogn 独有)**。
- **F0.8** W_emb 超级文档同样硬编码原始 `'内容'+'标题'` (:1548-1591), **不读** stage 14 物化的 content_{full,ctx,ss}; **嵌入 pass 无任何最短长度/空文本守卫** (:1582-1604, groupby 拼接直送 _embed_peer_texts) — 其天然兜底是「银行被剔行后从 groupby 缺席 → merge 后 NaN」, 与 cogn 的 100 字符守卫是**两套不同机制** (评审 sparsity-numeric-2/feasibility-5)。
- **F0.9** runner 传入的 df_exploded = 24_herd_decay.parquet (634 列), **已含** content_full/content_ctx/content_ss + ctx_is_fallback/ss_is_fallback → 三轨文本零新接线。
- **F0.10** 现有 `emb_peer_tone_lag1_{full,ctx,ss}` 语义 = **同一个 full 文本 W_emb × 三轨 tone** (:1551-1673 注释明言"同一 W_emb 传播三轨 tone, 零额外嵌入")。该 6 列 (含 _lg) 列名已被占用, 语义不可静默反转。
- **F0.11** 嵌入缓存键 = sha256(model|chunk文本|prompt_version|temperature) — ctx/ss 新超级文档必 cache miss; NEWS_PROCESS_LLM_OFFLINE=1 下 miss → RuntimeError **被 _embed_peer_texts try/except 吞掉 → return None → 该年跳过**; 全部年 miss 且 MAIN 空结果时 both-or-neither 把**全族列 (含本可命中的 full 轨) 一起 NaN**, run 不失败 (:1510-1516, :1784-1792)。
- **F0.12** parity 判定面: `_EMB_FAMILY_PREFIXES` 已含 'emb_peer_tone_lag1' 与 'bank_emb_sim_mean_lag1' (test_embedding_coprimary_parity.py:44); 新前缀不加会静默逃逸 (n10 教训, :74-78)。bank_cogn_mean 非嵌入, 不入 parity 面。
- **F0.13** stata_export._MAIN_ANCHOR_KEYS 有 P2-D fail-loud 硬 assert (build_variable_labels 内, :514-553): anchor 键必须在 HEURISTIC_LABELS 且含 `_QWEN_ANNOT`; _lg 标签 replacive 派生 (:554-563)。既存缺口: emb_peer_tone_lag1_ctx/_ss 及其 _lg 无手写标签、非 anchor。
- **F0.14** 播种量 (⭑终验更新: 盘上面板实为 110 银行/220 行; 有滞后年数据的超级文档 bank-year=143): T=2 dev 新增 ctx+ss 超级文档 ≈ 143×2轨×2模型 ≈ **572 条文本** (×切块因子); 生产 T=18 ≈ 5,848 条超级文档 (切块因子随年度拼接长度放大, 单条可切数十~上百块)。生产总费用**须在生产语料上按实测 token 计数重估后再过播种审批** (D16), 本估计仅定条数量级、不定金额。本机在线播种可行 (需 SILICONFLOW_API_KEY + YUNWU_API_KEY)。

### ② 结构判据敏感性
- **F0.15** 现判据 = 同篇 both-verified 共现 (build_adjacency_matrix, network_spillover.py:226-331): docid 分组、幸存 target_bank 集合、每篇每无序对 +1; 行宇宙 = full-only 留篇集 (tone_llms.py:2865)。
- **F0.16** 33 指标全集: 18 节点级 (bank_degree_cent…bank_is_hub, :905-1123) + 10 网络级 (net_*_yr, :742-779,1140-1180) + 5 GF (gf_*, :721-725)。BLAS 非确定 3 列 = bank_clustering / bank_cfbetween_cent / bank_harmonic_cent; ⚠ diff_golden.py:18-19 的 _KNOWN_BLAS_RE 更宽 (含 bank_eigen_cent), 两清单不一致。
- **F0.17** 银行∧银行同句/窗口共现**无现成原语**: entity_context.py 两原语均为银行∧金科口径 (禁互代); stage 11 只存计数不存位置, 但底层 `_scan_dedup_bank_matches` (ahocorasick.py:417-459) 返回**原文字符级位置** (start,end)。⚠ **`_split_sentences` (entity_context.py:103-117) 对每段 strip 且丢空段, 返回的句子列表无法还原原文偏移** — naive 累计长度二分会把字符命中系统性映射到错误句索引 (评审 sparsity-numeric-1/feasibility-3 实测证实), 必须用**位置保真**切分原语 (层 A)。
- **F0.18** panel 期重扫 vs stage 11 预产: panel 期天然在 verified 行宇宙上 (both-verified 免费、无 phantom 边风险 omni-g-net-spill-01)、不触 stage 11 schema/golden; stage 11 预产须存 per-doc 明细供 panel 过滤, 否则重现 phantom 边。同 docid 组内多 target_bank 行的 `内容`/`标题` 实测组内 nunique>1 为 0 组 (24_herd_decay, 917 个 docid 组) — 取组首行文本安全, 实现时加组内一致性 assert。
- **F0.19** 稀疏度: T=2 共现网 2017=88节点/63边, 2018=55节点/31边 (终验逐位复现); peer_tone_lag1 非空 ≈**28** bank-year (⭑终验更正, 原"32"不可复现); 银行句仅 34% 含金科 (旁证句级更稀); **银行∧银行同句共现率无任何现成测量** (Phase 0 实测)。
- **F0.20** 后缀落点 (评审 6 条 finding 交叉证实, **原「走既有命中」断言已证伪**): ⚠ codebook._infer_category 首个内容分支 `'tone' in var_name or 'sent' in var_name → '情感指标'` (:2047) 排在网络分支 (:2051-2053) **之前** → 全部 33 个 `_sent` 列会被误归「情感指标」; ⚠ 三个推断函数的 net 级分支均要求 `startswith('net_') and endswith('_yr')` (:1963/:2031-2033/:2051-2053) → 20 个 `net_*_yr_{win1,sent}` 列 endswith 失配落「未知/其他/Title-case 兜底」; ⚠ 18 节点指标中 8 个无 'cent' 子串基名 (clustering/constraint/ego_density/effective_size/avg_nbr_deg/coreness/ci/is_hub) 现状已落「未知」, 其变体再 +16 列「未知」。→ 层 E 必须做**判据后缀归一** (剥 `_win1`/`_sent` 再推断) + G1 加 codebook 断言。_infer_track (:2063-2072) 与 parity/_is_emb_family/test_dual_track 不受影响 (此半句仍成立); 34 处 paper_spec/模板全部引用无后缀名 → 加后缀新列纯加法。
- **F0.21** diff_golden.py 的 ADDED 白名单 `_ABL_RE` 只认词典消融列 → 任何新增网络列会被判 NON-ablation ADDED 退出码 1 (:22-24, 该脚本专用于消融重生验证)。

### 横切
- **F0.22** golden: test_column_hashes_match_golden 是**双向断言** (extra 也红, test_panel_reproducibility.py:161-166) → 新列落盘即红; 重生 DEFERRED 生产机; 本机验证 = baseline-stash A/B 差分证 0 新增失败。盘上 golden 本就分叉红 (strategic_diff 3144 vs 2787)。
- **F0.23** 标签**三源** (评审 wiring-3): ① stata_export.HEURISTIC_LABELS (走 stage-46 .dta); ② export.py STATA_LABELS (另一路径, 自带 _ctx→_ss 机械镜像循环 :1427-1433); ③ **stata/08_label_network.do (live 手写源, 经 stata/99_master.do:102-103 实际执行)** — 该文件手写了本次全部三个改动族的基名标签 (:20-46 结构指标 / :53 industry_neg_shock / :60-61 emb 族), strategic_diff 先例 (09_label_strategic.do) 是同步追加的。缺标签不自红 (fallback=列名), 红灯靠族专属 gate 测试 (test_network_metrics_expansion.py:325-332 先例)。⚠ 01_label_variables.do:8-23 约定: `_ss` 类标签权威=stage-46 自动生成文件, 手写源只补非 _ss 键。
- **F0.24** codebook._infer_source_stage (:1997-2040): `industry_neg_shock*` 与 `bank_cogn_mean*` 均无 token 命中 → 落 '未知' (现状已如此); 'cent'/'gf_' 命中节点/GF 族, 但 **net 级分支的 endswith('_yr') 会被判据后缀破坏** (见 F0.20 更正)。SSOT import 复用先例 = codebook 模块级 import encode.LLM_MODELS (:44-50)。
- **F0.25** config 惯例: panel.yaml:13-23 明言三轨 _ss 类结构性列扩展**无独立开关**, 常开; 参数放 config 记录性段。
- **F0.26** 无新 stage → DAG/OUTPUT_REGISTRY/test_dag_consistency 零触碰; 无新 .do 模板 → 计数不动 (⭑终验更正: 现值已是 **147**, 41886246 加了 28_tableA13; 本计划零模板增量的结论不变)。
- **F0.27** Stata 硬约束: 列名 ≤32 字符 + _assert_track_triplet_unique (缩名防串轨, stata_export.py:690-708,914-929)。
- **F0.28** check_static_enums.py 是 standalone 护栏 (未接 pytest); 改静态枚举后须手动跑。
- **F0.29** ② 扫描文本口径是 load-bearing 未决维度 (评审 4 条 finding 交叉证实): stage 13 在 2026-06-29 刚为「只读正文 → 标题点明实体的真报道单向假阴性」修过同型 bug (config/filtering.yaml:131-141, match_in_title=true); stage 11 幸存判定含标题通道 (in_title ∧ 正文≥1); prepend_title (entity_context.py:63-71) 使标题自成一句。→ 本计划以 D19 显式决策。

---

## §1 设计决策 (逐项【已定】; v2 按评审修订处标 ⭑)

- **D1【已定】①-A 命名 = 无后缀保留 canonical**: `industry_neg_shock`/`industry_neg_shock_lag1` 不 rename (镜像 du_2022 polw05≡canonical 先例), 新增 `industry_neg_shock_{ctx,ss}` + `industry_neg_shock_lag1_{ctx,ss}` (26 字符, ≤32 ✓)。8 处消费点零破坏。无后缀=历史命名产物非"主", 三轨互为稳健性、不分主次。
- **D2【已定】①-A 分母严格逐轨、无跨轨回退**: ctx→`n_articles_llm_valid_ctx`, ss→`n_articles_llm_valid_ss`; 该轨分母列缺失 → **跳过该轨** (WARN), 绝不借 full/物理分母 (防 c8a70ac5 轨道不对称复刻, F0.4)。min_count=5 逐轨沿用 (轨间 N 不齐是 conditional-on-full 的自然结果, 接受)。
- **D3【已定】①-A fire_sale 不三轨化 (out-of-scope)**: `brokerage_fire_sale` 维持 canonical shock 交乘; 注释显式声明「shock 已三轨但交乘仅 canonical, 判据=控制范围非遗漏」。
- **D4【已定】①-A 翻护栏注释**: network_brokerage.py:678-682 改写为「三轨已实现」的新护栏 (分子/分母逐轨对齐表), 保留 brokerage_eigen_cent/二分图 track-agnostic 部分。
- **D5【已定】①-B full 轨文本源不动**: cogn 与 W_emb 的 full/canonical 口径维持原始 `'内容'+'标题'` 拼接 — 缓存键不变、$0、golden canonical 列零漂移。**仅新增** ctx/ss 轨读 content_ctx/content_ss。full(原始拼接) 与 ctx/ss(stage14 物化, prepend_title) 口径不同源 → 在函数 docstring + codebook 备注显式披露 (不视为 bug)。
- **D6【已定⭑】①-B ss/ctx 超级文档剔除 fallback 行, 兜底机制分家陈述**: `ss_is_fallback==True` / `ctx_is_fallback==True` 的行**不进**对应轨超级文档 (否则 ss-W 与 full-W 趋同, 稳健性轨自证失效)。剔除后的兜底**按路径分述** (评审 sparsity-numeric-2/feasibility-5): **cogn 路径** = 既有 100 字符最短守卫 → NaN; **emb 路径** = 剔行后该 bank 从 groupby 缺席 → merge 后 NaN, 且 B4 **新增对称守卫**「超级文档 strip 后为空 → 该 bank 从该轨节点集剔除」防空串/近空串进付费 API (不设 100 字符门, 短文本照嵌 — 与 cogn 刻意不同, docstring 披露)。与份额类测度"共享 n_articles 分母"口径不同属刻意: 网络构造要纯轨文本, codebook 披露。⭑⭑ **ctx/ss 轨超级文档 = 逐篇 content_{ctx,ss} 原样拼接, 禁再走 title_col 通道** — 标题已由 stage 14 prepend_title 内嵌, 沿用现行 `' '.join(titles + ' ' + bodies)` 闭包会**双倍注入标题** (cogn TF-IDF 权重扭曲 + emb 以错文本付费播种、错缓存键不可逆) (终验 break-it-2-1); G1(i) 断言拦截。
- **D7【已定】①-B 新列命名 (避开被占用语义)**:
  - cogn: `bank_cogn_mean_ctx` / `bank_cogn_mean_ss` (17/16 字符 ✓, 非嵌入不入 parity)。
  - sim: `bank_emb_sim_mean_lag1_ctx` / `_ss` (+ `_lg` 孪生 `bank_emb_sim_mean_lag1_lg_ctx`, 29 ✓) — 后缀语义 = **W 来源轨**; 自动落入 parity 前缀 'bank_emb_sim_mean_lag1' ✓。
  - peer tone 对角轨: `emb_peer_tone_diag_lag1_ctx` / `_ss` (+ `_lg`: `emb_peer_tone_diag_lag1_lg_ctx`, 30 ✓) — `diag` = W 与 tone 同轨对角。**不复用** emb_peer_tone_lag1_{ctx,ss} (已被 W_full×tone_ctx 占用, F0.10)。新前缀 `'emb_peer_tone_diag_lag1'` **必须**加入 _EMB_FAMILY_PREFIXES (F0.12 n10 教训)。
  - 不做 3×3 交叉: 仅对角 2 新列/模型 (正交不交叉先例)。
- **D8【已定】①-B 降级单元 = per-W-轨独立 both-or-neither**: ctx-W 族 (emb_peer_tone_diag_lag1_ctx + bank_emb_sim_mean_lag1_ctx + 各自 _lg) 与 ss-W 族、既有 full-W 族**互为独立降级单元** — 任一单元内 canonical/_lg 同置 NaN (无单边孤儿), 但 ctx/ss 未播种**绝不连带抹掉 full 族** (修复 F0.11 全族连坐风险)。per-单元独立降级镜像 BERT per-model 先例; 单元内 parity 镜像 co-primary 铁律。
- **D9【已定⭑】② 后缀 = `_win1` / `_sent`, 不复用 _ctx/_ss**: 同篇判据 = 无后缀 canonical; `_win1` = 银行∧银行 ±1 句窗共现; `_sent` = 严格同句。判据轨≠文本轨 (正交概念空间), 复用 _ctx/_ss 会被 _infer_track 误标 + 污染"三轨禁混 Hansen J"散文口径。最长列名 `net_assortativity_yr_sent`=25 ✓。33×2=+66 列。⭑ **后缀本身不足以保 codebook 安全** (F0.20 更正: 'sent' 子串误归情感 + net_yr endswith 失配) — 由层 E 的判据后缀归一兜住, 后缀命名维持不变 (改推断链代价 < 换后缀)。
- **D10【已定⭑】② panel 期重扫, 不动 stage 11/13; 原语必须位置保真**: 在 network_spillover 新增 build_adjacency_matrix 的判据参数化版本; 每 docid 组 (仅 ≥2 家幸存银行的组) 一次全银行 AC 扫描 (复用 `_scan_dedup_bank_matches` 位置输出), 银行侧**必须**过否定/短名排除 (与 stage 11 单一匹配语义事实源对齐, 禁裸 AC — '涉农行业'→'农行' 假阳性)。⭑ 句边界**禁用** `_split_sentences` + naive 累计长度二分 (strip/丢空段致偏移漂移, F0.17) — 层 A 新增位置保真切分 `_split_sentences_with_spans` (同一 `_SENT_SPLIT_RE` 以 finditer 在原文上产 `[(char_start, char_end, sent_idx)]`, 分句结果与 `_split_sentences(text)` 严格一致 — 保 win1 半径语义与 `_ss` 轨同源), 命中按 span 区间归句。新原语放 core/text/entity_context.py (银行∧银行, 与银行∧金科原语并列、互不复用)。取 docid 组首行文本 + 组内一致性 assert (F0.18)。
- **D11【已定】② 窗口判据对称化 = OR**: 银行 A 锚句 ±1 句内含 B **或** B 锚句 ±1 句内含 A → 成边 (无向图自然对称化)。
- **D12【已定】② 不交叉加权**: 只做 3 判据 × 未加权计数; hyperedge_normalize (Newman) 维持未接线。
- **D13【已定⭑】② Phase 0 决策门 (置于层 A 之后, 共用生产原语)**: 层 A 落地后, 用**同一原语同一参数**写只读审计脚本实测盘上 1005 行的银行∧银行三判据边数/LCC (G5; 禁 ad-hoc 重复实现判据, 保「审计==生产」单一事实源)。**无论结果如何 33×2 全量照做** (T=2 稀疏≠生产稀疏)。⭑ 降级条款范围扩为: **任一新轨/新判据在 T=2 上零方差或 0 边** (含已实测的 ①-A ctx/ss 零方差, F0.6) → 该族 gate 的数值断言降级为 schema/标签断言, 数值覆盖由合成帧补。Phase 0 产出记入 §9 (含 ①-A 三轨 dev 基线: full 有方差 / ctx≡0 / ss≡0)。
- **D14【已定⭑】② 判据参数入 config**: `config/panel.yaml` 新增记录性段 `network_criteria: {win_radius: 1, match_in_title: true}` (⭑ 补 match_in_title 键, 对齐 D19; 镜像记录性 flag 惯例, 常开无开关); ⚠ 与 filtering.yaml::cooccurrence_filter.sentence_radius (stage 13 银行∧金科) 是**不同键**, 注释互指。
- **D15【已定】golden 策略**: 全部改动后 golden 双向断言必红 — 本机验证 = baseline-stash A/B 差分证 0 新增失败; golden 重生 + 生产数值 DEFERRED 生产机。diff_golden._ABL_RE **不扩** (该脚本专用于词典消融重生验证)。
- **D16【已定⭑】播种策略**: ①-B 的 ctx/ss 嵌入在本机**在线播种** (~344 条文本, 两 key 齐备时执行; 无 key 则 DEFERRED 并记录) → 播种后离线可 $0 复现。生产 T=18 全量播种 DEFERRED; ⭑ **金额须在生产语料上按实测 token 计数重估** (F0.14 只锚定条数量级) 再过播种审批门, 计划不预设费用结论。
- **D17【已定⭑】codebook/标签联动全补**: _infer_source_stage 新增 token 分支 (`neg_shock`→network_brokerage 族; `cogn`/`emb_peer`/`emb_sim`→network_spillover 族); ⭑ **判据后缀归一** (层 E): 三个推断函数 (`_infer_source_stage`/`_infer_category`/`_infer_label`) 在匹配前剥离 `_win1`/`_sent` 尾缀 (镜像 _strip_lg token 剥离先例) — 一处归一同时修复 'sent' 误归情感与 net_yr endswith 失配; ⭑ 顺手消化 8 个无 'cent' 节点指标基名的现存「未知」(加族 token 或白名单)。标签**三源都补** (F0.23): HEURISTIC_LABELS + export.py STATA_LABELS + stata/08_label_network.do (仅非 _ss 键, capture 写法, 镜像 09_label_strategic 先例); 含既存缺口 (emb_peer_tone_lag1_ctx/_ss 及 _lg; ⭑ **canonical 同期 `industry_neg_shock` 的年FE共线警示标签**, 评审 econometrics-3) 一并补齐; 新增族专属 gate 测试断言 labels[c] != c **且 codebook category/source_stage 正确** (G1)。
- **D18【已定⭑】铁律**: 新增的每个稳健性维度 (①-A 三轨 / ①-B W-轨 / ② 判据) 各自 just-identified 并排, **禁混同一 over-identified Hansen J**; 不新增 .do 模板、不动 paper_spec primary; manuscript prose DEFERRED。⭑ **不做 FWER 的依据** (终验 econometrics-final-2, 防与 LLM/BERT 段的 27_tableA12 先例形成无解释不对称): 判据/W轨/①-A三轨敏感性属**规格稳健性并排** (镜像政治词权重 {0,0.5,1} 与词典消融梯度先例, 均无 FWER 模板); 跨模型 rwolf FWER 先例仅覆盖**同构念替代 headline 测量**, 本计划不适用 — 若 manuscript 需要, 随 DEFERRED prose 阶段披露。此句写入层 H 新铁律段。
- **D19【已定⭑, 评审新增】② 扫描文本口径 = 标题+正文, 与 stage 13 对齐**: 层 A 扫描文本 = `prepend_title(标题, 内容)` (复用 entity_context.py:63-71 原语, 标题自成第 0 句) — 依据: ① stage 13 已实证修复「只读正文 → 标题点明实体的单向假阴性」(F0.29), ② stage 11 幸存判定本含标题通道, 银行列举最常见于标题。标题句语义: **参与 `_sent` 同句判定 (标题双银行 → 成边) 与 `_win1` 距离 (第 0 句, 与正文首句相邻)**。G5 Phase 0 与层 B1 共用同一原语同一参数 (含该口径); G1 合成帧加「标题双银行、正文锚句分散」正例断言 (镜像 R4 反例写法)。config 记录 `match_in_title: true` (D14)。

---

## §2 范围

**In scope**
- ①-A: industry_neg_shock 三轨 (+4 列) + 护栏注释翻转 + 分母逐轨。
- ①-B: bank_cogn_mean 三轨 (+2 列, $0); bank_emb_sim_mean_lag1 W-轨 (+2 canonical +2 _lg); emb_peer_tone 对角轨 (+2 canonical +2 _lg); per-W-轨独立降级重构; 本机播种。
- ②: 33 结构指标 × {_win1,_sent} (+66 列); 银行∧银行共现新原语 (位置保真); Phase 0 稀疏度审计脚本。
- 横切: 标签三源 / codebook 判据后缀归一 + matcher / parity 前缀 / gate 测试 / CLAUDE.md / check_static_enums 手动跑。

**Out of scope (显式)**
- fire_sale 三轨 (D3); peer_tone_lag1 (共现网) 的判据分轨; W轨×tone轨 3×3 交叉; Newman 加权交叉 (D12); 新 .do 模板与 manuscript prose; golden 重生与生产播种 (DEFERRED); 二分图/brokerage_eigen_cent 任何变体 (数学恒等)。

**列增量**: ①-A +4, ①-B +10, ② +66 → **净增 +80 列** (⭑终验勘误: 原"≈2782→≈2862"是对陈旧基数的心算 — 07-02/07-03 多轮扩展叠加后实际基数 3228, 落盘后实读 **3308** 列, CLAUDE.md 已按实读口径更正)。

---

## §3 确切改动清单 (按层)

### 层 A — core/text (② 新原语, ⭑v2 重写)
- `core/text/entity_context.py` 新增:
  - `_split_sentences_with_spans(text) -> list[(char_start, char_end, sent_idx)]` — 用**同一** `_SENT_SPLIT_RE` 以 `finditer` 在原文上切句并保留原文偏移; **分句结果 (剔空段后的句序) 与 `_split_sentences(text)` 严格一致** (单测断言逐句相等), 保 win1 半径语义与 `_ss` 轨同源。禁 naive 累计长度重建 (F0.17)。
  - `map_bank_sentence_positions(title, body, bank_ac, negation_ac, short_name_exclusions, ...) -> dict[bank_name, set[sent_idx]]` — 文本 = `prepend_title(title, body)` (D19, 标题=第 0 句); 一次 AC 全银行扫描 (`_scan_dedup_bank_matches` 位置输出) + span 区间归句 + 逐命中否定/短名排除。docstring 写明「银行∧银行判据专用, 与银行∧金科原语互不复用」。
- 短文本: `_sent` 判据按实际句列表算 (单句文章两银行必同句), 不另设字符回退。
- 单测 (与层 A 同 commit): ① '涉农行业'→'农行' 假阳性反例 (R4); ② 位置对齐单测 — 含全角标点/连续空白/空段的文本上, char-hit 归句结果 == 逐句独立扫描的真值 (F0.17); ③ 标题双银行、正文锚句分散 → _sent 成边正例 (D19); ④ spans 与 `_split_sentences` 逐句一致断言。

### 层 B — pipeline/panel/network_spillover.py
- **B1 (②)** `build_adjacency_matrix(df_exploded, year, criterion='article'|'win1'|'sent')`: criterion='article' 走现路径 (零改动); 'win1'/'sent' 对 ≥2 幸存银行的 docid 组取组首行 (标题, 内容) 调层 A 原语 (组内一致性 assert, F0.18); ⭑⭑ **层 A 返回 dict 先与该 docid 组的幸存 target_bank 集合求交, 仅在交集内枚举无序对成边** — AC 命中的非幸存银行只定位不成边 (否则复刻 omni-g-net-spill-01 phantom 边, 终验 traceability-4); 按句索引集判边 (sent: 交集非空; win1: min 距离 ≤1, OR 对称 D11), 每篇每对 +1。
- **B2 (②)** `compute_bank_network_centrality` 参数化 suffix: 循环 criterion×suffix ∈ {('article',''), ('win1','_win1'), ('sent','_sent')}, 33 指标 ×3 落列。无后缀路径数值不变 (验收口径见 §4.2, 含 BLAS 列豁免)。
- **B3 (①-B cogn)** `compute_cognitive_proximity` 增加轨循环: full=现路径原样; ctx/ss 用 content_ctx/content_ss 且剔 *_is_fallback 行 (D6), ⭑⭑ **禁走 title_col 通道** (标题已内嵌, D6), 产 bank_cogn_mean_{ctx,ss}, [0,1] + 100 字符守卫逐轨。
- **B4 (①-B emb, ⭑v3)** `_compute_embedding_peer_network_pass` 重构为 per-W-轨: full-W pass 原样 (缓存键零变化); 新增 ctx-W / ss-W pass (content_{ctx,ss} **原样拼接、禁 title_col 通道** D6, 剔 fallback 行), 各产 `bank_emb_sim_mean_lag1_{track}` + `emb_peer_tone_diag_lag1_{track}` (+_lg); **每 W-轨独立 both-or-neither 单元** (D8); 守卫: 超级文档 strip 后为空 → 该 bank 从该轨节点集剔除 (D6, 防空串进付费 API), 不设 100 字符门 (与 cogn 刻意不同, docstring 披露); ⭑⭑ **轨级 miss 计数 WARN**: `_embed_peer_texts` 吞 miss 时按 W-轨累计, 年度循环结束 count>0 → logger.warning(轨名+条数) (承载 R12 后半, 终验 traceability-2)。
- **B5** 模块头/docstring: L1551-1560 「同一 W_emb, $0」注释改写为「full-W 传三轨 tone (历史列) + diag 新轨」双口径说明。

### 层 C — pipeline/panel/network_brokerage.py (①-A)
- `compute_industry_neg_shock` 轨循环: {'': ('neg_count_full','n_articles_llm_valid'), '_ctx': ('neg_count_ctx','n_articles_llm_valid_ctx'), '_ss': ('neg_count_ss','n_articles_llm_valid_ss')}; 无后缀轨保留 `else n_articles` 旧回退 (兼容), ctx/ss 轨**缺任一列即跳过该轨** (D2); LOO 双分支 + lag1 逐轨复用同一内核函数。
- L678-682 护栏注释翻转 (D4); fire_sale 处加 canonical-only 注释 (D3)。

### 层 D — config
- `config/panel.yaml`: `network_criteria: {win_radius: 1, match_in_title: true}` 记录性段 + 互指注释 (D14/D19)。

### 层 E — codebook.py (⭑v2 重写)
- ⭑ **判据后缀归一** (根修复, 评审 6 条 finding): 三个推断函数 `_infer_source_stage` / `_infer_category` / `_infer_label` 入口先 `re.sub(r'_(win1|sent)$', '', var_name)` 再走既有匹配 (镜像 _strip_lg 剥离先例) — 一处归一同时修复: ① 'sent' 子串误归「情感指标」(33 列); ② net_*_yr endswith('_yr') 失配 (20 列); ③ _infer_label 的 net 级语义标签丢失。
- _infer_source_stage 新 token 分支: `neg_shock` / `cogn` / `emb_peer` / `emb_sim` (置于网络族分支邻近, 顺序在 LLM/BERT 宽前缀之后)。
- ⭑ 顺手消化 8 个无 'cent' 节点指标基名的现存「未知」: 加结构族 token 白名单 (clustering/constraint/ego_density/effective_size/avg_nbr_deg/coreness/`bank_ci`/is_hub); ⭑⭑ **白名单同时接入 `_infer_source_stage` (→network_spillover 族) 与 `_infer_category` (→'网络指标')** (或抽公共 helper) — 否则剥后缀后这 8 基名的 16 个判据变体在 _infer_category 仍落'其他', G1(g) 必红 (终审 break-it, fail-loud 非静默)。
- ⚠ 本计划引用的 codebook.py 行号存在 ~30-40 行漂移 (如 _infer_category 'sent' 分支实际在 :2084 邻近而非 :2047) — 实施时**按函数名定位**, 禁按行号盲改 (终审 closure 注记)。
- ⭑⭑ _SENT_DIAG_SPECS 式精写 (**必做**, 终验 traceability-3/econometrics-final-3): 范围 = industry_neg_shock 三轨 + diag 族 + legacy `emb_peer_tone_lag1_{ctx,ss}` + `bank_cogn_mean_{ctx,ss}` 的 VariableMetadata (~10 条); 备注字段须含 D5 的 full-vs-ctx/ss 文本源不同源披露 + D6 的兜底机制分家/纯轨文本口径披露; diag 族与 legacy 族的 label/备注**必须写明 W 来源** (legacy = W_full×tone_track, diag = W same-track)。

### 层 F — 标签三源 (F0.23, ⭑v2)
- **源① stata_export.py HEURISTIC_LABELS**: ⭑ ①-A **5 条** (4 新列 + 补 canonical 同期 `industry_neg_shock` 的 '(LOO, same-period; year-FE collinear)' 警示, 镜像 export.py:1197 文案, 评审 econometrics-3) + ①-B 8 条 (diag/sim canonical 键带 _QWEN_ANNOT 并入 _MAIN_ANCHOR_KEYS — P2-D assert 原子同增; _lg 由 replacive 派生) + 既存缺口 emb_peer_tone_lag1_ctx/_ss 2 条 (同带 annot 入 anchor) + ② 66 条机械派生块 (基名标签源 = 既有精写/HEURISTIC/08 块的基名条目; ⭑⭑ 追加后缀**必须带 bank-bank 限定**: ' (bank-bank ±1-sent edge)' / ' (bank-bank same-sent edge)' — 裸 'same-sent' 已是 `_ss` 银行∧金科文本轨的官方压缩词, 逐字冲突 (终验 econometrics-final-1); net_*_yr 变体继承 'year-FE absorbed' 披露)。⭑⭑ 既存缺口 2 条 legacy 标签与 diag 族标签**写明 W 来源** (如 'Emb Peer Tone L1 (W=full-doc, tone=ctx)' / diag 带 'W same-track'), export.py :1206-1207 两条既有标签顺手同改 (标签非数据, golden-safe) (终验 econometrics-final-3)。
- **源② export.py STATA_LABELS**: 同族补齐; 实施时现场确认 :1427-1433 _ctx→_ss 镜像循环键域与 `_sent` 列无碰撞。
- **源③ stata/08_label_network.do** (⭑ 评审 wiring-3): 追加新列中文标签, **仅非 _ss 键** (capture 写法, 镜像 09_label_strategic.do 先例); _ss/_lg 键按 01_label_variables.do 约定留给 stage-46 自动生成文件。

### 层 G — tests (⭑v2)
- **G1** `tests/test_network_tritrack_expansion.py` (新建 gate):
  - (a) 新列落盘存在性 (对 real output 有条件 skip);
  - (b) labels[c] != c 非 fallback (源①②双源断言);
  - (c) parity: diag/sim 新列 _lg 双射 + 新前缀登记断言;
  - (d) ①-A 分母逐轨断言 (合成帧: ctx 分子借 full 分母即红);
  - (e) ② 无后缀列与改动前等价 — ⭑⭑ **实现口径** (终验 test-adequacy-2, 禁真空自对拍): 在 **Phase 0 (代码未改动时)** 用现 build_adjacency_matrix + compute_bank_network_centrality 跑固定合成小图, 33 指标输出**冻结为测试 fixture 常量** (BLAS 3 列 np.allclose 容差), 改动后 criterion='article' 对冻结值断言 (真实盘上 A/B 见 §4.2);
  - (f) ② `_sent ⊆ _win1 ⊆ 同篇` 边数单调断言 (合成帧); ⭑⭑ 加 **phantom 反例**: 正文提及第三家非幸存银行且与幸存银行同句 → 不成边 (终验 traceability-4);
  - ⭑ (g) codebook 断言: 全部 66 个 ② 新列 `_infer_category == '网络指标'` 且 `_infer_source_stage != '未知'`; ①-A/①-B 新列 source_stage 落对应族;
  - ⭑ (h) 层 A 位置对齐/标题正例/假阳性反例 (若不在层 A 单测文件中);
  - ⭑⭑ (i) **D6 语义断言** (终验门禁 major traceability-1): 合成帧上 mock 嵌入 (cogn 用可判别 token) — 断言 ss_is_fallback==True 行的文本**不出现**在 ss 轨超级文档; 空超级文档 bank 不入该轨节点集; ctx 轨超级文档 == `' '.join(content_ctx 序列)` 且**标题子串出现次数 == 篇数** (拦双标题, break-it-2-1; 播种前即拦, 防付费缓存被错文本污染);
  - ⭑⭑ (j) **D8 隔离断言** (同 major): 模拟 ctx 轨嵌入 return None → full-W 族列非 NaN 而 ctx-W 族 (canonical+_lg) 全 NaN (per-单元 both-or-neither 隔离, 不连坐);
  - ⭑⭑ (k) 标签措辞断言: ② 新列标签含 'bank-bank' 限定 (不得裸 'same-sent'); diag/legacy 标签含 W 来源子串。
- **G2** `test_embedding_coprimary_parity.py`: _EMB_FAMILY_PREFIXES += 'emb_peer_tone_diag_lag1' (D7)。
- **G3** `test_omni_fix_net_brok.py`: LOO 断言参数化三轨 (L295-305 口径断言逐轨)。
- **G4** 跑 `scripts/audit/check_static_enums.py` (手动, F0.28)。
- **G5** Phase 0 脚本: `scripts/audit/measure_bank_bank_cooccurrence.py` (只读; ⭑ **调用层 A 生产原语与 D19 口径**, 禁 ad-hoc 判据复制, D13)。⭑⭑ **输入写死 = `data/processed/24_herd_decay.parquet`** (runner df_exploded 同源, F0.9; 实测 1005 行唯一吻合) + 施加与 B1 相同的「docid 组内 ≥2 幸存 target_bank」预过滤 — **禁沿用 measure_bank_fintech_cooccurrence.py 的 14_/12_ 输入样板** (那是过滤前/非幸存宇宙, 终验 impl-dryrun-2)。顺带产出 G1(e) 的合成小图冻结 fixture。

### 层 H — CLAUDE.md + memory
- 「当前状态铁律」新增段: 三个新稳健性维度 + 禁混 Hansen J + 命名口径 (`_win1`/`_sent`≠文本轨; diag=W同轨; codebook 推断做判据后缀归一) + 播种状态。
- :53 BLAS 句更新: 非确定列 3 → 9 (3 列 × 3 判据); 顺手记录 diff_golden(~4 含 eigen) 与 CLAUDE.md(3) 清单不一致待生产机重生时实证统一。
- :55/:201 「最宽 ≈2782」→ 「≈2862 (随重生漂移, 以实读为准)」。
- memory: panel-3-network-cols-nondeterministic 同步更新。

### 层 I — 播种 (①-B, D16)
- 两 key 齐备 → 在线跑一次 (T=2 量小); 播种后 `NEWS_PROCESS_LLM_OFFLINE=1` 重跑验证 0 miss。无 key → 层 I 整体 DEFERRED, 新列 NaN 落盘 (per-单元降级 D8 保证不伤 full 族)。

---

## §4 测试与 golden 策略 (⭑v2)

1. **baseline-stash A/B** (F0.22): stash 前跑全量 pytest 记录失败集 A; 应用改动重跑记录 B; 断言 B ⊆ A ∪ {golden 新列 extra 红 (预期)}。churn 隔离 (memory: log-enrich-round8 教训)。
2. **无后缀 canonical 列不变** 硬验收 (⭑ 评审 wiring-4/feasibility-1 修订): ② criterion='article' 路径、①-B full-W pass、①-A 无后缀 shock 三处 A/B 对比 — **两次 run 均须 `PYTHONHASHSEED=0` + 全 BLAS 线程钉 1** (MKL/OPENBLAS/NUMEXPR/OMP=1), 且 **3 个 BLAS 非确定列 (bank_clustering/bank_cfbetween_cent/bank_harmonic_cent 的无后缀本体) 从逐位哈希中排除、改用 `np.allclose` 容差对比** (与 R11 九列清单同源互指); 其余列逐位哈希相等。
3. golden 重生 + 9 列 BLAS 排除清单 + 生产播种 → **DEFERRED 生产机** (§6 尾)。
4. e2e smoke: 本机重跑 panel runner 一次, 验列数 +80、值域守卫、log 无新 ERROR; ⭑ 预期基线: ①-A ctx/ss 零方差 WARN (F0.6) 与 ② `_sent` 稀疏 WARN 是**已知预期**, 不判失败。

## §5 风险与缓解 (计划级, ⭑v2)

| # | 风险 | 缓解 |
|---|---|---|
| R1 | ①-A ctx/ss 借错分母 (c8a70ac5 复刻) | D2 严格逐轨 + G1(d) 合成帧 gate |
| R2 | ①-B 全族连坐 NaN (F0.11) | D8 per-W-轨独立降级 + full 路径等价保留 + ⭑ G1(j) 隔离断言 |
| R15 | ⭑ D6 剔除/双标题静默失效 (终验 major) | G1(i) 语义断言 (fallback 不入超级文档/空文档剔节点/标题次数==篇数) |
| R3 | diag 新列逃逸 parity (n10 教训) | G2 前缀登记 + G1(c) |
| R4 | ② 裸 AC 假阳性 ('涉农行业'→'农行') | D10 强制复用排除原语, 层 A 单测反例 |
| R5 | ② phantom 边 | D10 panel 期重扫, 天然幸存集 |
| R6 | 后缀语义污染 | D7/D9 命名隔离 + ⭑ 层 E 判据后缀归一 + G1(g) codebook 断言 |
| R7 | anchor/HEURISTIC 不原子 → fail-loud 崩 | F0.13 P2-D assert 是护栏, 层 F 原子提交 |
| R8 | 标签**三源**漂移 (⭑) | 层 F 三源同 PR + G1(b) 断言 + 08.do 仅非 _ss 键 |
| R9 | ② 生产 17M 重扫耗时 | 仅 ≥2 幸存银行 docid 组进扫描; Phase 0 记录单篇耗时外推; 超预算 → 生产机 sidecar 物化 |
| R10 | ⭑ 任一新轨/判据 T=2 零方差或 0 边 (已实测: ①-A ctx/ss ≡0; ② _sent 待 Phase 0) | D13 数值断言降级 schema/标签断言, 合成帧补数值覆盖; §9 记录基线 |
| R11 | BLAS 非确定 ×3 漂移假阳性 | 层 H 清单先行更新; 9 列全名 drop 写死计划与 memory; ⭑ §4.2 A/B 验收钉线程 + 3 列 allclose 豁免 |
| R12 | 离线跑把新列静默 NaN 误当 bug | 层 I 播种后 0-miss 验证; log 加轨级 miss 计数 WARN |
| R13 | ⭑ 句边界偏移漂移 → 边集静默算错 (F0.17) | 层 A 位置保真 spans 原语 + 对齐单测 (全角标点/连续空白/空段) + spans≡_split_sentences 一致性断言 |
| R14 | ⭑ ② 扫描口径分叉 (标题盲区复刻, F0.29) | D19 显式决策 + config 记录 + G5/B1 共用原语 + G1 标题正例断言 |

## §6 落地顺序 (⭑v3)

0. ⭑⭑ **基线重校** (终验 facts-1): 确认 HEAD (e39955d0 或更新), §4 A/B 以当前 HEAD 为 baseline; 四文件 (encode/codebook/stata_export/tone_llms) 一律按函数名定位。
1. 层 A (位置保真原语 + 4 组单测) → **Phase 0**: G5 脚本用层 A 原语实测三判据边数/LCC + ①-A 三轨基线 + G1(e) 冻结 fixture (改动前采集), 记入 §9。
2. 层 B1/B2 (②) → G1(e)(f) 合成验证。
3. 层 C (①-A) + G3 → 层 B3 (cogn) → 层 B4/B5 (emb 重构, 最高风险, 单独 commit)。
4. 层 D/E/F (config/codebook 归一/标签三源, 原子) + G2。
5. G1 全绿 (含 (g) codebook 断言) + G4 手动跑 + §4 baseline-stash A/B (钉线程 + BLAS 豁免) + e2e smoke。
6. 层 I 播种 (key 齐备时) + 0-miss 复验。
7. 层 H (CLAUDE.md/memory) → by-name 提交 (排除 *constants.json/eval_reports 并发产物) → 推送。
8. DEFERRED (生产机): golden 重生 (9 列 BLAS 排除) / 生产播种 (费用按生产语料实测重估, D16) / manuscript prose。

## §7 评审台账 (2026-07-03, wf_22920e55-e32: 8-lens → 24 findings → 逐条 2 票对抗 verify → 19 确认 / 5 驳回)

**确认并已修订入本文 (按根因归并)**:
| 根因 | findings | 落点 |
|---|---|---|
| codebook 推断链失配 ('sent' 误归情感 33 列 + net_yr endswith 失配 20 列 + 8 节点基名未知) | identity-trap-1, semantic-drift-1, econometrics-1, wiring-1, wiring-2, feasibility-2 (4×major) | F0.20/F0.24 更正; D9/D17⭑; 层 E 判据后缀归一; G1(g) |
| ② 扫描文本口径未决策 (标题盲区同型) | identity-trap-3, semantic-drift-2, econometrics-4, sparsity-numeric-3 (1×major) | 新 D19; D14 补 match_in_title; F0.29; R14; G1 标题正例 |
| 句边界原语不成立 (_split_sentences 丢偏移) | sparsity-numeric-1, feasibility-3 (2×major) | F0.17 更正; D10⭑; 层 A spans 原语 + 对齐单测; R13 |
| 逐位验收未豁免 BLAS 非确定列 | wiring-4, feasibility-1 (1×major) | §4.2⭑ 钉线程 + 3 列 allclose; R11⭑ |
| D6 兜底机制归属错误 (100 字符守卫仅 cogn) | sparsity-numeric-2, feasibility-5 | F0.7/F0.8 更正; D6⭑ 分家; B4 空文本守卫 |
| ①-A ctx 轨 dev 同零方差 (漏记) | identity-trap-2 | F0.6⭑; D13/R10 降级条款扩域; §9 模板 |
| canonical 同期 shock 无共线警示标签 | econometrics-3 | 层 F 源① 4→5 条 |
| 标签第三 live 源漏列 (08_label_network.do) | wiring-3 | F0.23⭑ 三源; 层 F 源③; R8⭑ |

**驳回 (2 票 verify 未存活)**: semantic-drift-3 / econometrics-2 (② 标签机械派生无源 — 基名标签在精写/既有块中可派生, 层 F 已写明派生源); parity-lg-1 (P2-D assert 定性之争 — F0.13 措辞已中性化为 fail-loud); cache-cost-1 (生产播种费用量级外推 — 采纳其精神于 D16⭑: 金额以生产实测重估, 不预设); feasibility-4 (Phase 0 依赖倒置 — §6⭑ 已把 Phase 0 移到层 A 后, 争议消灭)。

**终验门禁 (2026-07-03, wf_1b6c39b7-a82: 6 专项 + major 2 票复核; 29 条 F0 事实全量重核 = 16 holds + 13 行号漂移 + 0 broken)**:
| finding | 落点 |
|---|---|
| traceability-1 (major, 唯一确认): D6/D8 零测试覆盖 | G1(i)(j) 新增; R2 补指; 新 R15 |
| facts-1: 基线漂移 e39955d0 / 计数 147 / 四文件行号 | 头部基线段⭑⭑; F0.26; §6 步骤 0 |
| facts-2: F0.19 "32"不可复现 (实为 28) | F0.19 更正 |
| traceability-2: R12 后半无承载 | B4 轨级 miss WARN |
| traceability-3: D5/D6 披露落在"(可选)"精写 | 层 E 精写升必做+扩范围 |
| traceability-4: B1 缺幸存集求交句 | B1⭑⭑; G1(f) phantom 反例 |
| impl-dryrun-2: G5 输入路径未写死 (先例样板是错宇宙) | G5⭑⭑ 24_herd_decay + 预过滤 |
| break-it-2-1: ctx/ss 超级文档双标题注入 | D6⭑⭑; B3/B4 禁 title 通道; G1(i) 标题次数断言 |
| econometrics-final-1: ' (same-sent)' 与 _ss 轨词汇冲突 | 层 F bank-bank 限定; G1(k) |
| econometrics-final-2: 不做 FWER 无依据 | D18⭑ 依据句 (入层 H) |
| econometrics-final-3: diag/legacy 标签不含 W 来源 | 层 F/层 E W 来源措辞; G1(k) |
| test-adequacy-2: G1(e) 可被真空自对拍 | G1(e) 冻结 fixture 口径; G5 顺带采集 |

## §8 实施记录 (2026-07-03 实施)

**逐层完成态** (⭑最终终验 wf_ed44ac47-a0e 补记: 层 H ✅ CLAUDE.md 铁律段+BLAS 9 列+列数实读口径+播种状态句 / 层 I ✅ ctx/ss+diag canonical+_lg 已本机在线播种、离线 0-miss 复现、首跑 yunwu SSL 事故实证 D8 单元隔离): 层 A ✅ (entity_context 两原语 + 9 单测) → Phase 0 ✅ (§9) → 层 B1/B2 ✅ (criterion 参数化 + 33×3 落列 + runner 三调) → 层 C ✅ (shock 三轨 + 护栏翻转 + fire_sale canonical-only 注释) → 层 B3/B4/B5 ✅ (cogn 三轨 / emb per-W-轨 diag 单元 + 空文档守卫 + 轨级 miss WARN / docstring 双口径) → 层 D ✅ (panel.yaml::network_criteria, 顶层键直落 CONFIG 根) → 层 E ✅ (三推断函数判据后缀归一 `_CRITERIA_SFX_RE` + 8 基名白名单双接 + neg_shock/cogn/emb 族 token + 14 条精写 VariableMetadata 含 D5/D6 披露) → 层 F ✅ (源① HEURISTIC ①-A 6 条+①-B 8 条+② 66 机械块+anchor 原子 6 键 / 源② export.py 同族+机械块 / 源③ 08_label_network.do capture 非-ss 键+② 声明) → 层 G gate: test_network_tritrack_expansion.py 断言全绿 — 首批 26 项覆盖 (c,d,e,f,g,h,i,j) + ⭑结果审计后补齐 (a,b,k) 三项 (29 项, 见偏差 5), G2 ✅ (_EMB_FAMILY_PREFIXES += 'emb_peer_tone_diag_lag1' — diag 与既有 'emb_peer_tone_lag1' 前缀于第 14 字符分叉, 不加即 n10 式静默逃逸; sim W-轨由既有前缀自动覆盖; parity 10 项全绿), G4 check_static_enums 0 新增违规 (60 条 prose 均 HEAD 既存)。

- **实施偏差 1 (层 A, 2026-07-03)**: 未采用计划原定的 `_split_sentences_with_spans` (AC 字符位置 + span 归句), 改为**逐句 `has_unexcluded_occurrence` 判定** (`map_bank_sentence_positions`) — 与 ctx/ss 轨锚句判定字节级同款原语, **从根上无偏移映射问题** (R13 根因消灭而非缓解); B1 只需幸存银行的句集, 逐句判定成本可忽略 (Phase 0 实测 0.77ms/组)。配对判定原语 `bank_pairs_within_sentence_window` (min |i−j| ≤ radius, 天然对称 ≡ D11 OR 口径)。
- **实施偏差 2 (顺序)**: G1(e) 冻结 fixture 未等 Phase 0 — 在改动落地后用 **git HEAD(e39955d0) 版模块与改动后模块在同一合成小图上做一次性 in-process A/B** (33 列全等, 零容差外 0 列), 以 HEAD 输出冻结 `tests/fixtures/network_criteria_baseline_v0.json` — 强于计划口径 (真·改动前代码, 非"改动前时间点")。
- **实施偏差 3 (B1 组内一致性)**: 计划的 assert 落地为 fail-soft loud WARN + 取组首行 (镜像 FINTECH_AC=None 先例, 防单条脏数据崩 stage); F0.18 实测 0 组不一致。
- **实施偏差 4 (G3)**: test_omni_fix_net_brok.py 的 LOO 断言未做三轨参数化 — 数值覆盖由 gate 的 `TestIndustryNegShockTriTrack` 等效承载 (逐轨精确值 + 借 full 分母即红的可判别帧), omni 文件保持 canonical-only 不动。
- **实施偏差 5 (结果审计补落地, 2026-07-03 第二轮)**: 结果终审 (wf_fbe5d1cf-016, 6 专项 + 2 票复核, **80 项 checked_ok / 数据本体零缺陷**) 确认 1 major (closure-1: G1(a)(b)(k) gate 断言首批未落地而 docstring 宣称已覆盖) + 6 minor → 全部修复: ① 补 `TestNewColumnsLandingAndLabels` 三测试 (G1(a) 盘上 80 列存在性含缺盘 skip / G1(b) build_variable_labels 全新列非 fallback+≤80 字节 / G1(k) bank-bank 限定+W= 来源子串); ② 恒真式断言改锁 `_strip_criteria_suffix` no-op + 冻结基名标签; ③ HEURISTIC 补 canonical `bank_cogn_mean` 基名标签 (对称性); ④ criterion 分轨路径加 `hyperedge_normalize=True` 守卫 raise (防未来 *_hn 接线时三判据无警告分叉)。源② export.py 的 labels[c]!=c 不单测 — 该路径经 `_apply_label_fallback` 复用源①同一启发式且自带 100% 覆盖运行时硬断言。

## §10 结果审计台账 (2026-07-03, wf_fbe5d1cf-016 — 实施后最终审)

6 专项 (code-net / code-meta / closure / real-output / downstream / break-it-3) 审已提交 diff (17c8f0d4+593dae3c) 与盘上真实产物; major 2 票对抗复核。**checked_ok 80 项** (含: 判据梯子盘上单调 0.0182>0.0152>0.0128 / parity 双射 0 孤儿 0 错配 / diag≠legacy 实值可分 / canonical 路径零回归逐键等价 / suffix rename 零 _x/_y 碰撞 / 闭包安全 / stage 46 全列过 32 字符+80 字节硬限)。findings = 1 major + 6 minor, 全部为 gate 覆盖记账与两处小缺口 (非数据缺陷), 处置见偏差 5; closure-3 (G3) 记偏差 4。

## §11 最终终验台账 (2026-07-03, wf_ed44ac47-a0e — 最终态 HEAD=24b4eb1d, 5 个全新角度)

5 专项 (commit3 diff 审 / prose-truth 文档全对账 / cross-artifact 跨产物一致性 / value-sanity 数值计量健全 / git-hygiene): **0 major (无一确认亦无一被驳) / 66 项 checked_ok / 代码与数据零缺陷**; 并行全量 sweep 失败集与基线**逐条恰同 (23↔23, 新增 0 消失 0)**。6 条 minor 全为文档一致性, 已全部修正: ① CLAUDE.md/本计划的"≈2862 列"心算口径 → 实读 3308 (593dae3c message 内部自相矛盾一并勘误); ② gate docstring 与 §8 字母表漏列已实现的 (a)(c) (undersell 方向); ③ 17c8f0d4 message 首句"计划全量落地"按整个 effort 口径书写 — 单提交粒度实为层 A/B/C, 联动面见 593dae3c (历史不可改, 此句即对账注记); ④ CLAUDE.md 铁律段补播种状态句 (层 H 原要求); ⑤ §8 补层 H/层 I 完成行; ⑥ MEMORY.md 索引 BLAS 条目 "3列"→"9列" 与 topic 文件对齐。

## §9 Phase 0 实测记录 (2026-07-03, scripts/audit/measure_bank_bank_cooccurrence.py, 生产函数直调)

| year | criterion | nodes | edges | LCC | density |
|---|---|---|---|---|---|
| 2017 | article | 88 | 63 | 24 | 0.0165 |
| 2018 | article | 55 | 31 | 14 | 0.0209 |
| 2017 | win1 | 88 | 51 | 22 | 0.0133 |
| 2018 | win1 | 55 | 27 | 9 | 0.0182 |
| 2017 | sent | 88 | 41 | 18 | 0.0107 |
| 2018 | sent | 55 | 24 | 8 | 0.0162 |

- article 边数与 F0.19 逐位吻合 (63/31) — 生产函数复现历史口径 ✓; 边集单调 sent ⊆ win1 ⊆ article ✓。
- **_sent 网保留 65~77% 边** (41/63, 24/31) — 远优于预期稀疏度 (标题双银行命中充足, D19 口径的直接收益); D13 的"_sent 全 0 边"降级预案未触发, gate 数值断言按正常口径落地。
- R9 耗时: 0.77 ms/多银行组 (dev 55 组 0.04s); 生产外推 50 万组 ≈ 6.4 分钟 — panel 期重扫可行, sidecar 物化预案不需启用。
- ①-A 三轨 dev 基线: full neg_count=1 (分母 17≥5, 有方差 std≈0.0013) / ctx neg_count=1 但分母 2<min_count=5 被守门 → ≡0 / ss neg_count=0 → ≡0 (F0.6 确认)。
