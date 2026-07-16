# BERT 概率分布形状指标扩展 — 执行计划 (2026-07-03)

> 状态: **v3 — 两轮评审收敛 (第一轮 4 镜头 31 findings + 第二轮 5 镜头复审, 全裁定, 见 §10); 实施前置 = P0-0**
> 计划作者: Claude (Fable 5) 会话 2026-07-03; 评审: 第一轮 4 路 + 第二轮 5 路对抗 agent
> 权威基线: main=5eba7a52; ⚠ 行号坐标系 **[R5 勘误]**: runner.py (217 行以下)/attention_media.py 的行号为 **HEAD 口径** (脏树含 finbert2 fix 时分别 +4/+3); encode/codebook/export 锚点为脏树口径 (其 hunk 在锚点之上/之下不影响锚点内容)。实施挂载一律以**语义锚**为准 (P1-2「_append_columns 之后、aggregate_panel 之前」/ P1-4「log_diagnostics 之前」/ P2-2「7h-net 与 7h-cent 之间」), P0-0 后以提交后 HEAD 终核。[R4] 脏树面已扩大, 见 P0-0
> 触发: 用户问「根据国际顶级期刊, 还可以计算哪些指标?」→ 差距分析确认现有 BERT 族只消费概率的均值/标准差, 逐篇概率分布的**形状信息**是空白。

---

## §0 目标与范围

在 stage 23 已落盘的 BERT 概率列 (`{b}_正面/中性/负面{trk}`) 之上, 以 **$0 纯后处理** (不重跑任何推理、不碰 stage 21/23) 新增五族面板指标:

| WP | 指标族 | 锚点 (措辞纪律 §2.7) | 新面板列数 |
|----|--------|----------|-----------|
| A | 分类熵 `{b}_tone_entropy{trk}` | 构念动机: Epstein & Schneider (2008, JF); Ilut & Schneider (2014, AER) — **非构造出处** | 9 |
| B | 极端负面尾部 `{b}_xneg_frac[_t80/_t95]{trk}` | 家族动机: Baker, Bloom & Davis (2016, QJE); Engle et al. (2020, RFS) — **非构造出处** | 27 |
| C | 净语调偏度 `{b}_net_tone_skew{trk}` | 方法论移植: Chen, Hong & Stein (2001, JFE) — raw skew (正=右偏), **非 NCSKEW** (无负号) | 9 |
| D | 跨模型逐篇分歧双轨: `bert_xmodel_lblhet{trk}` (canonical) + `bert_xmodel_disp{trk}` (稳健轨) | 直接类比: Diether, Malloy & Scherbina (2002, JF); Cookson & Niessner (2020, JF) — 标准化方案与 DMS 不同, 勿写"按 DMS 方法" | 6 |
| E | 年内波动/趋势 `{b}_nt_iyvol{trk}` / `{b}_nt_iytrend{trk}` | 前提动机: Tetlock (2007, JF); Da, Engelberg & Gao (2015, RFS) — **非构造出处** | 18 |

**合计 +69 面板列**。全部三轨 × per-model (WP-D 除外)。
**不在范围**: LLM/词典侧同类扩展; `_lg` 孪生 (非嵌入 carve-out); 加权 (_vw/_mw/_hw) 孪生。

---

## §1 现状事实基础 (两轮实读核实; 行号准确率 100% @脏树)

1. **概率列 NaN 语义**: pos/neg(/neu) 同置 NaN (encode.py:1426-1432 明文); `{sn}_infer_failed` 存在 (tone_berts.py:1154)。⚠ **finbert2 `中性` 列存在但恒全 NaN** (tone_berts.py:1149-1150) — 熵类集按 `THREE_CLASS_MODELS` 决定, **finbert2 只读 pos/neg**。文章级源列名模板 = `{b}_正面{trk}` / `{b}_负面{trk}` / `{b}_中性{trk}` (tone_berts.py:1543-1548, suffix 拼接; ss 轨可整体缺席)。
2. **finbert2 = 二分类** (encode.py:113-119), 中性质量重归一进 pos/neg (omni-g-geography-06 实测 0.912 vs 0.690/0.817)。
3. **中间列→聚合链路**: washing_cols dict (runner.py:939) → `_append_columns` 一次性 concat (runner.py:1120) → `aggregate_panel(df)` (runner.py:1128) → `build_aggregation_dict(df)` (encode.py:1395) → valid_agg 只查源列在位、**不校验 func** (encode.py:1398-1404) → groupby agg (encode.py:1414)。**挂载硬边界 = 1120 与 1128 之间** (建议 1123 之后)。
4. **`日期`**: required_cols fail-loud (runner.py:682); parse_time 转 datetime + dropna (encode.py:686-700) → 面板构建时恒非空。
5. **codebook 推断**: 69 列 → 'Stage 23' 全对 (**63 走宽前缀** codebook.py:2190-2193, **6 走 'bert' 子串** :2196; ⚠v2 误写 66/3); `_infer_category` 分叉 (fin_sent_zh 含 'sent' 子串) + `_infer_label` Title-case 兜底 → P3-1 显式条目全覆盖。`_BERT_MODEL_RE` (codebook.py:272-274) 全锚定, 实判 `..._net_tone_skew_full → None`。codebook.py:50 模块级 import encode (成环链依据)。
6. **runner 时序全链** (第二轮实证): aggregate_panel 1128 → df_exploded=df 1139 (1140 del df) → 6c `compute_media_heterogeneity` **1180** (attention_media.py:1709-1712 in-place drop 仅 `_is_*`+3 具名列) → 7h-net **1723** → 7h 后续块 1727-1767 → … → `log_diagnostics(panel, df_exploded)` **2699** → `export_panel(panel, df_exploded)` **2702** (export.py:1548 **全列无过滤**写入 40_article_bank_level.parquet; :1536 全 None object 崩溃先例)。`_nt_art_*` 等非 `_is_` 中间列在 6c/7h 全程**无人 drop** → 泄盘风险真实, 且 WP-E 消费窗口 (≈1725) 与 drop 窗口 (1739~2699) 真实存在。
7. **merge 模式**: `panel.merge(frame, on=['target_bank','year'], how='left')` (network_spillover.py:1577 等同文件 **6 处**同构)。zero-fill 在 balance_panel (runner.py:1143 调用, 逻辑 encode.py:2395-2461) 内, 时序先于 WP-E merge; 五族机制对 69 列 **0 命中** (两轮独立复核)。
8. **pandas==2.3.3** (requirements.lock:109); groupby 'skew'/'count' 字符串协议可用; encode.py:1440 只禁 lambda 闭包。
9. **net_tone 前缀风险 = 低**: 8 处消费点全精确/锚定 (两轮复核), P0-3 收敛为负例锁测试。
10. **disag_{b} 构造基 = 概率均值** (runner.py:2358-2360 输入 `{b}_pos/{b}_neg` ← encode.py:800 mean; ⚠v2 误写 "argmax 计数基" — argmax 计数基是 disag_llm 族与 `_is_{b}_positive` 洗稿族 runner.py:190/1044-1046)。`{b}_pos_count` (encode.py:1121-1123) = **argmax 判正篇数**, ≠有效篇数。
11. **`_KNOWN_BLAS_RE`** (diff_golden.py:18-19): 对 69 列及全部中间列 0 意外命中; `_ABL_RE` ADDED 白名单只认词典消融 → 生产机重生 diff 对 +69 列必报 NON-ablation ADDED (预期, §8)。
12. **[R4] finbert2 argmax 值层 fix 已落树未提交** (runner.py:210-217, `fix(dta-coverage-audit, 2026-07-03)`, 加 `notna().any()` 守卫防全 NaN 中性占位列误走 3-class 分支): ① **独立佐证**本计划 §2.1/§2.6 的同类设计 (类集按 THREE_CLASS_MODELS 成员资格/只读 pos/neg, 不凭列存在); ② 该 fix 改变 `_is_finbert2_*`/washing/disag_finbert2 取值, 但本计划**零消费**这些列 (skew 掩码用 `_nt_n_` count, `_nt_art` 用概率差) → 无交互; ③ dev A/B 基线必须取在该 fix 提交之后 (P0-0 已保证)。同批 l1o IV 模板 fix 亦已落树 (2 个 .do.tmpl)。

---

## §2 设计决策 (⚠=评审回改点; v3 增量标 [R2])

### §2.1 WP-A 分类熵

- 文章级: `_ent_{b}{trk}` = −Σ_k p_k·ln(p_k) / ln(K_b); K_b 按 THREE_CLASS_MODELS 取 3/2; finbert2 只读 pos/neg。p_k=0 项记 0 (lim=0); 参与类任一 NaN → 整篇 NaN。**[R2] 实现反模式点名**: `np.where(p>0, p*log(p), 0)` 会把 NaN 静默映 0 (NaN>0=False), 须先 isna 短路再算 (P1-1 docstring 明写)。
- 面板列: `{b}_tone_entropy{trk}` = mean。只产 mean。
- **构念边界**: 归一化仅对齐值域不对齐构念——二分类熵混同"中性"与"模糊", 且 finbert2 熵 = H((1+nt)/2) 是 |nt| 的**严格单调递减**确定性变换 (**[R2] 负向**; dH/d|nt| < 0, |nt|=0→熵1, |nt|=1→熵0)。裁定: 构念仅在 THREE_CLASS_MODELS 上为主解释; finbert2 列照产, codebook notes 封「二分类 Bernoulli 熵=极性不确定度, 与三分类模糊度不可比, 禁跨模型比较水平; 与 |finbert2_net_tone| 负向确定性共线 (MATH-1: 报 corr 不并列同式)」。
- gate: **[R2] Spearman ρ == −1** (⚠v2 误写 +1, 照写必红; ties 下 average-rank 镜像仍精确 −1; 合成数据须含 ≥2 个不同 |nt| 值防秩零方差 ρ=NaN); finbert2 (中性列在场全 NaN) 熵非 NaN。
- 与 pos_std 区分 (codebook): 跨文章离散度 vs 篇内类分布不确定性。
- [R2→R5 校准] P5-1 sanity「熵∈[0,1]」写 `≤1+1e-5` (dev Σp 舍入偏差 1e-4 下归一化熵可超 1 约 9e-6; 不做重归一, 保确定性口径)。

### §2.2 WP-B 极端负面尾部

- SSOT: `XNEG_THRESHOLDS = (0.80, 0.90, 0.95)`, canonical=0.90≡无后缀, 变体 `_t80/_t95` (镜像 RARE_WORD_FREQ_CUTOFFS; `_t80/_t95` 全仓零命中、与 `_thrNN`/`_n\d+`/`_CRITERIA_SFX_RE` 零交叉, 两轮复核)。
- 文章级: `_xneg_ind_{b}{tag}{trk}` = (P(负面)>τ), **float 保 NaN 禁 fillna(0)**; 命名避开 `_is_` 命名空间 (既有惯例 int+fillna(0), 借用即埋 blanket 处理陷阱)。**[R2] 实现写法**: `(p>τ).astype(float).mask(p.isna())` 类 (裸比较对 NaN 返回 False, 直接 astype 即静默填 0)。
- 面板 = mean → 分母 = 该模型该轨概率非缺篇数。三阈值指示列同源同 NaN 掩码 → 分母恒同、单调性逐格精确成立 (第二轮推导确认)。**[R2] gate 写法**: 单调性断言在 notna 掩码上比较或用 `~(a>b).any()`; 全 NaN 格断言三列同时 NaN (裸 `(a<=b).all()` 对 NaN 假红)。
- **二分类阈值语义** (R1 BLOCKER 修复, 保留): 固定 τ 仅**模型内**一致; 跨模型水平不可比 (finbert2 重归一使同 τ 捕获集更大更温和)。① codebook 禁跨模型比较占比水平 (只比标准化 β, Table A5 口径); ② manuscript 披露; ③ 不产 pooled 列。分位校准弃案 §6#8。
- 铁律: 三阈值互为稳健不分主次, 禁混同一 over-identified Hansen J; 与既有梯子正交。

### §2.3 WP-C 净语调偏度

- 文章级: `_nt_art_{b}{trk}` = P(正)−P(负) ∈ [−1,1]。恒等式 mean(_nt_art) ≡ net_tone (前提 encode.py:1426-1432 明文); gate 用 **np.allclose(a, b, rtol=0, atol=1e-12)** (**[R2]** 默认 rtol=1e-5 实际容差松 6 个量级; 生产 n~10⁶/格 复用时 atol 放 1e-9)。
- 面板列: `{b}_net_tone_skew{trk}` = groupby 'skew', 门槛 `SKEW_MIN_N = 10` (rationale: n=3/4 时 |G1| 上界分别为 √3 与 2 (**[R2] 勘误**: v2 写 "n=3~4 ≤√3" 在 n=4 不成立), 抽样 SD n=3≈1.22/n=10≈0.69, 纯噪声进回归致衰减偏误; NCSKEW 文献 ≥26 周观测, 文章数场景折中 10)。
- **[R2] 掩码唯一实现** (⚠v2 两个备选全废——`{b}_pos_count{trk}` 面板列虽存在 (encode.py:1121-1123) 但语义=argmax 判正篇数≠有效篇数, 拿极性计数当 n 是**以语调为条件的内生样本选择** [50 篇全负格 pos_count=0 被掩], 三路评审独立确认; pre-agg 置 NaN 击穿恒等式 gate 并连坐 WP-D/WP-E 输入): ① build_aggregation_dict 无条件注册 9 条辅助计数 `agg[f'_nt_n_{b}{trk}'] = (f'_nt_art_{b}{trk}', 'count')` (count=非 NaN 篇数, 与 groupby 'skew' 的 n 恰同口径; 先例 encode.py:908 n_articles_llm_valid); ② aggregate_panel 内、net_tone post-agg 块 (encode.py:1426-1438) 之后: `panel.loc[panel[_nt_n] < SKEW_MIN_N, skew_col] = NaN`; ③ 随即 **drop 全部 `_nt_n_*` 面板临时列** (镜像 `_ctx_fallback_count` 先例 encode.py:1442-1450, 含防 iv_did underscore 过滤干扰同款理由; gate #14 断言无残留)。掩码只改写 skew 列 → 恒等式在**全部**格可断言, 无交互冲突。
- 方向声明: raw skew, 非 NCSKEW; 对象移植 caveat。T=2 稀疏格 NaN=预期退化。

### §2.4 WP-D 跨模型分歧双轨

- **canonical** `bert_xmodel_lblhet{trk}` = 逐篇可用模型 sign(_nt_art_b) **两两不一致的模型对占比** (**[R2] 措辞**: "对"=pair 非 logarithm; ≥2 模型, 否则 NaN)。**[R2] sign(0) 定音**: 不一致 := sign_a ≠ sign_b, 其中 **0 与 ±1 记不一致、0 与 0 记一致** (finbert2 重归一后 0.5/0.5 是真实可达点, 必须定义); near-zero 符号翻转噪声属标签基测度固有, 不设 deadband (§6 归档); gate 加 nt==0 用例。算术: 3 模型 3 对, 一模型异号→2/3 ✓; 2 模型支撑 {0,1}。
- **稳健轨** `bert_xmodel_disp{trk}` = z 标准化 nt 的跨模型样本 SD; **[R2] z 与 SD 全 ddof=1** (docstring+手算同口径); σ=0/全 NaN 模型退出。样本依赖三重披露保留 (前视/不可复现/形状差)。
- **[R2] 逐篇混合口径** (v2 只记了一半): 2-模型 vs 3-模型混合来源 = 模型**全局缺席** (Known Issue #2) **或逐篇 infer_failed** (原子失败) — 三模型全在场时同一 bank-year 内也逐篇混合支撑 {0,1} 与 {0,1/3,2/3,1} (disp 同理: |z₁−z₂|/√2 与 3 值 SD 混合); codebook notes 明写; **dev per-格逐篇可用模型数分布 → §9 具名回填项** (v2 悬空指向已落位)。
- 与 `disag_{b}` 区分 (**[R2] 事实勘误**): disag_{b} = 同模型跨文章分歧, 构造基 = **概率均值** (`{b}_pos/neg` mean, encode.py:800; ⚠v2 误写 argmax 计数基——那是 disag_llm 族); xmodel_* = 同篇跨模型。区分本身成立, codebook 按勘误后措辞写。
- 定位: 测量诊断, 非 per-model co-equal 梯子成员。

### §2.5 WP-E 年内时序

- month = `df['日期'].dt.month`; 对每 (bank,year,model,trk): 月均值 m_t、月篇数 n_t、月内样本方差 s²_t (ddof=1)。
- **[R2] `{b}_nt_iyvol{trk}` 完整定义** (⚠v2 公式在 n_t=1 无定义、ddof 未钉——BLOCKER 修复):
  **iyvol = √max(0, Var₁(m_t) − (1/T)·Σ_t σ̂²/n_t)**, 其中
  ① Var₁ = 有效月均值的样本方差 (**ddof=1**);
  ② 有效月 = 该格下有 ≥1 篇非 NaN _nt_art 的月 (**含单篇月**), T = 有效月数;
  ③ σ̂² = **池化文章级方差** = Σ_{t:n_t≥2}(n_t−1)·s²_t / Σ_{t:n_t≥2}(n_t−1) (池化假设月间文章方差同质, codebook 如实披露); 校正项对**全部**有效月 (含 n_t=1) 按 σ̂²/n_t 求和 (单篇月噪声最大, 恰是最须校正的项, 不可 skipna 漏掉);
  ④ 门槛: T ≥ `IYVOL_MIN_MONTHS=3` **且至少 1 个月 n_t≥2** (否则 σ̂² 不可估 → NaN, 宁缺勿噪);
  ⑤ 无偏性声明**仅指开方/max(0,·) 截断前**的方差差 (双 ddof=1 下 E[Var₁(m_t)] = Var₁(μ_t) + (1/T)Σσ²/n_t 对 n_t/σ²_t 逐月异质均成立); 截断率生产实测记账 §9/§8。
  gate 手算对拍用例**必须含一个 n_t=1 月**。rationale: 剔除稀疏月均值抽样噪声 (否则低覆盖格机械高波动、与 n_articles 构造性负相关)。codebook 披露: 等权月 + 校正公式 + 回归须控 coverage。
- `{b}_nt_iytrend{trk}`: 月均值对实际月号 x∈{1..12} 的 OLS 斜率, 有效月 ≥ `IYTREND_MIN_MONTHS=6`; **闭式** Σ(x−x̄)(m−m̄)/Σ(x−x̄)² 逐元素实现, **禁 lstsq/polyfit** (LAPACK 破"无 BLAS"; runner.py:1707 前车); [R2] 分母>0 由月号互异+门槛 6 结构保证 (实现处一行注释, 免误加守卫); 按 (bank,year) 分组无跨年混月; value_range 宽记 [−2,2]∪NaN。
- 实现: (bank,year) frame → **runner.py:1725 与 1727 之间** merge ([R2] 精确化); **[R2] merge 前先 drop panel 中已存在的 18 列** (防重跑 `_x/_y` 后缀静默污染, 先例 attention_media.py:1697-1699)。**空 frame schema 合同**: 0 行也返回 **18+2 列** ([R2] 含 target_bank/year 键列, 否则 merge on= KeyError), 指标列钉 float64。
- 结构声明: 不经 zero-fill (在 balance_panel 内, 时序先于本 merge); gate: merge 前后行数不变 + 键无重复 (P4-1 **#15**, v2 悬空已落位)。
- 三向正交修正版: vs tone_volatility (跨年) 真正交; vs pos_std 仅校正后近似正交 (此即采校正版第二理由)。

### §2.6 通用架构决策

- **叶模块 `pipeline/panel/bert_distribution.py`**: 零仓内依赖; BERT_MODELS/THREE_CLASS_MODELS 参数注入; SSOT 常量 (`XNEG_THRESHOLDS`/`SKEW_MIN_N`/`IYVOL_MIN_MONTHS`/`IYTREND_MIN_MONTHS`) + 列名生成器 + 纯函数。禁双向模块级 import (codebook.py:50 已 import encode)。
- **[R2] 输入/API 合同** (v2 缺失, 实施者会停手三次): ① df 须含 (或部分含) `{b}_正面{trk}`/`{b}_负面{trk}` (三分类另加 `{b}_中性{trk}`); ② `TRACKS=('_full','_ctx','_ss')` 为模块级常量 (与全仓硬编码字面一致, 叶模块不 import); **三轨循环在模块内**, 调用方调一次; ③ per-(model,track) 守卫: 正/负任一缺席 → 该 (model,track) 全部中间列**不出现在返回 dict** (键也不产, per-model 独立降级); ④ `iter_intermediate_cols`/`iter_panel_cols` 与 df 无关**恒返回声明全集** (声明集−实际产出集 = 合法缺席); ⑤ `three_class` 参数只影响计算路径 (finbert2 双列熵), **不影响键集** (docstring 明写); ⑥ [R2] `compute_xmodel_dispersion(df, models) -> dict[str, Series]` (6 键, 与主函数同构), 与 P1-2 同一批 `_append_columns` 并入。
- **agg 落点**: 无条件注册 + valid_agg 过滤 (D 块惯例) → 无参 `build_aggregation_dict()` gate 可断言条目无条件在场。
- **[R2] 中间列生命周期定音** (v2 "聚合后 drop 但为 WP-E 保留" 会造成 Phase 2 返工/双 call site): **drop 单点挂载 = runner.py:2699 `log_diagnostics` 之前** (步骤 9 导出块入口); 清单 = 声明全集 ∩ `df_exploded.columns` (交集天然容忍 Phase 1 时 WP-D/E 列未存在与 ctx/ss 合法缺席); Phase 1 首落即挂此点, **Phase 2 零改动** (WP-E 在 ≈1725 消费 `_nt_art_*` 时其仍在位); 显式否决双 call site (省的内存 < 维护漂移风险); 代价 = 中间列存活至导出前 (R8 措辞同步)。面板级临时列 `_nt_n_*` 生命周期另见 §2.3 (agg 后即 drop)。
- per-model 独立降级; 确定性 (全逐元素运算, `_KNOWN_BLAS_RE` 实测 0 命中)。

### §2.7 引文措辞纪律

reference 两段式: 「构造 = 本项目定义 (公式); 构念家族锚点 = <引文> (动机, 非方法出处)」。仅 WP-C 可写"方法论移植" (附 raw-skew≠NCSKEW + 对象移植 caveat)、WP-D 可写"直接类比" (注标准化非 DMS)。WP-A/B/E 一律构念动机降格。

---

## §3 列清单与命名预算 (≤32 硬约束; 程序化复算 7/7 零差错, 全 69 列 max=30)

| 列模式 | 最长实例 | 长度 |
|---|---|---|
| `{b}_tone_entropy{trk}` | `fin_sent_zh_tone_entropy_full` | 29 |
| `{b}_xneg_frac{trk}` | `fin_sent_zh_xneg_frac_full` | 26 |
| `{b}_xneg_frac_t80{trk}` | `fin_sent_zh_xneg_frac_t80_full` | 30 |
| `{b}_net_tone_skew{trk}` | `fin_sent_zh_net_tone_skew_full` | 30 |
| `bert_xmodel_lblhet{trk}` | `bert_xmodel_lblhet_full` | 23 |
| `bert_xmodel_disp{trk}` | `bert_xmodel_disp_full` | 21 |
| `{b}_nt_iyvol{trk}` | `fin_sent_zh_nt_iyvol_full` | 25 |
| `{b}_nt_iytrend{trk}` | `fin_sent_zh_nt_iytrend_full` | 27 |

计数: A=9, B=27, C=9, D=6, E=18, **Σ=69**。文章级中间列 51 (`_ent_`9 / `_xneg_ind_`27 / `_nt_art_`9 / `_xmd_art`+`_lblhet_art`6) + [R2] 面板级临时列 `_nt_n_*` 9 (agg 后即 drop)。8 个新名 pattern 全仓零冲突。
dta 宽度: **以 P0-0 后实读为准** ([R2] v2 "→3326" 预测数字已删——与自立的禁心算纪律矛盾且无出处; 并发会话提交可能改变基数)。

---

## §4 分阶段工作包

### Phase 0 — 前置与侦察复核
- [ ] **P0-0 (硬前置)**: 并发冲突解除。**[R4] 脏树面已扩大** (2026-07-03 第四轮实测 git status): 本计划目标文件中 **5 个** pipeline/panel 文件未提交 (codebook +9 / encode +10 / export +5 / **runner +6** [finbert2 fix] / attention_media +5), 另有 2 个 .do.tmpl (l1o fix) + 9 篇 manuscript/refs 大改 (~1.2 万行, 属另一并发论文/标注会话, 见同目录 HUMAN_ANNOTATION_* 计划) + **3 个**他会话 untracked 计划文件 ([R5] COMPANY_BANK_COOC / HUMAN_ANNOTATION_PROTOCOL / HUMAN_ANNOTATION_TOPTIER_CLOSEOUT, 勿碰)。与本计划同文件同函数, by-name 管不住同文件 hunk。**默认等相关会话提交后动工**; [R2] 仅当 >1 个工作日未提交才走 worktree 隔离 (仍须以合并后 HEAD 复核行号)。A/B 基线 = 并发提交后 HEAD。⚠ [R5 勘误] runner/attention_media 行号 = HEAD 口径 (脏树 +4/+3), 挂载以语义锚为准, 终核以提交后 HEAD 重核; [R5 预检] 首选解除案 = 并发 dta-coverage 7 文件 (5 pipeline + 2 .do.tmpl, 已确认自洽完整成品、hunk 注释齐全无 TODO) 先单独成 commit 再动工 (worktree 案与 §1.12③ "基线须含 finbert2 fix" 矛盾, 已降为末选之上的次选; 脏树混提案违反 by-name 纪律, 否决)。
- [ ] P0-1: dev `23_bert_tone.parquet` 实读: ① 9 概率列在位 + pos/neg 同 NaN 掩码; ② 逐模型 Σp_k 归一实测 (**[R5 校准] 容差 |Σp−1| < 2e-4** — dev 概率为四位小数舍入, 三分类实测 max|Σp−1|=1e-4, [R2] 的 1e-6 照写必红); ③ finbert2 中性列全 NaN。[R5 预检已实测三项全过: 27 概率列在位 (ss 轨无缺席)/掩码 9/9 同/中性全 NaN, 1005 行。]
- [ ] P0-2: 冲突 grep 复跑 (防基线漂移)。
- [ ] P0-3: 负例锁测试 (8 处消费点已两轮预核全安全; 复核翻出误捕再升级两段式提交)。
- [ ] P0-4: zero-fill 0 命中复核。
- [ ] P0-5: parse_time 无效日期过滤计数实读记录。
- [ ] P0-6: P3-1 显式条目范围确认 (全 69 列 + category 同值; 字段值表见 P3-1)。

### Phase 1 — 叶模块 + WP-A/B/C
- [ ] P1-1: 新建 `bert_distribution.py` 按 §2.6 全部 API 合同; docstring: 白话 + §2.7 引文 + 构念边界 + NaN 反模式点名 (§2.1) + 中间列生命周期。
- [ ] P1-2: runner.py:1123 之后、1128 之前一次性 `_append_columns` 并入。
- [ ] P1-3: encode 无条件注册: entropy/xneg=('...','mean'); skew=('_nt_art_...','skew'); **[R2] + 9 条 `_nt_n_{b}{trk}`=('_nt_art_...','count') 辅助计数** → post-agg 掩码 (net_tone 块后) → drop `_nt_n_*` (§2.3 唯一实现, 禁 pos_count/pre-agg 两废案)。
- [ ] P1-4: **[R2] 中间列 drop 单点挂载 runner.py:2699 之前** (交集清单, §2.6; Phase 2 零改动)。

### Phase 2 — WP-D 双轨 + WP-E
- [ ] P2-1: `compute_xmodel_dispersion(df, models) -> dict[str, Series]` (sign 定音 §2.4 / z与SD ddof=1 / ≥2 模型), P1-2 同批并入, encode agg mean → 6 列。
- [ ] P2-2: `compute_intrayear_dynamics(df, models) -> DataFrame[(bank,year)+18 列 float64]` (§2.5 完整定义: 池化 σ̂²/双 ddof=1/单篇月并入校正项/双门槛/闭式斜率), **runner.py:1725-1727 之间** merge (先 drop 既存 18 列防 `_x/_y`); 块注释: 三向正交修正版 + 不经 zero-fill。

### Phase 3 — codebook + 标签
- [ ] P3-1: 显式 VariableMetadata 全 69 列 (参数化循环, 模板 codebook.py:912 起三轨循环)。**[R2] 字段值定音表**: data_type 全 'float'; category 统一 `'情感指标-BERT分布形状'`; unit: entropy='归一化熵(无量纲)' / xneg=lblhet='占比' / skew='无量纲' / disp='z分数SD' / iyvol='净语调SD' / iytrend='净语调/月'; value_range: entropy [0,1] / xneg [0,1] / skew (−∞,+∞)∪NaN(n≥10) / lblhet [0,1] (文章级支撑 notes 记) / disp [0,+∞) / **iyvol [0,1.2]∪NaN** ([R5] 上确界>1 反例: 单篇月致 Var₁ 不封顶, √(4/3)≈1.155 真实可达) / iytrend [−2,2]∪NaN; label 英文模板 7 族 (`{Model} Tone Entropy ({Track})` 等, ≤80 截断)。**description 先白话一句 (是什么/量什么) 再公式口径** ([R2] 补白话承诺, memory 稳定参考)。notes: Hansen J 短语 / NaN 语义 / 三处构念边界 / 逐篇 2v3 混合 / 校正公式+coverage 控制 / disag 区分 (按 §2.4 勘误措辞: 概率均值基)。reference 两段式。
- [ ] P3-2: stata_export 机械块: per-model 新 metric **7 个** (entropy 1 + xneg 3 + skew 1 + iyvol/iytrend 2) 精确键入 `_PM_BERT_METRIC_EN` (stata_export.py:682-685); `bert_xmodel_*` 6 列单独精确键 (不走 per-model 块); 全 [:80]。兜底 = P4-1 #10 (无既有 gate 会自红)。
- [ ] P3-3 (纯记账): `_MAIN_ANCHOR_KEYS` (stata_export.py:551) 仅嵌入族, 不触发; export.py `_ALLV_PREFIXES`/fallback 同不触发。零动作。

### Phase 4 — gate 测试 (14+1 项)
- [ ] P4-1: `tests/test_bert_distribution_metrics.py`。**[R2] fixture 最小 schema**: 3 模型×3 轨×(正/负)=18 + 2 三分类×3 轨×中性=6 + target_bank/year/日期=3, **合计 27 列**全源合成 df (闭环/标签/codebook 项必须全源, 否则合法缺席假红; 如需 `{sn}_infer_failed` 类列另行显式加):
  1. 熵: one-hot→0, 均匀→1; finbert2 双列路径非 NaN; NaN 传播 (含 np.where 反模式回归用例)。
  2. 熵-构念锁: **Spearman ρ == −1** ([R2] 方向勘误); 合成含 ≥2 个不同 |nt|。
  3. SSOT 锚: `XNEG_THRESHOLDS==(0.80,0.90,0.95)` + canonical 0.90≡无后缀映射 + `SKEW_MIN_N==10` + **`IYVOL_MIN_MONTHS==3`** ([R2] 补) + `IYTREND_MIN_MONTHS==6`。
  4. 梯子单调性: notna 掩码上比较 ([R2] NaN-aware); 全 NaN 格三列同 NaN。
  5. 恒等式: `np.allclose(rtol=0, atol=1e-12)` ([R2]); 掩码后全格仍可断言 (掩码只触 skew 列)。
  6. lblhet: 三同判→0/一异→2/3/2 模型 {0,1}/**nt==0 用例** ([R2]); disp ≥0, ddof=1 手算; <2 模型→双 NaN。
  7. iyvol/iytrend: 校正公式手算对拍 (**含 n_t=1 月用例** [R2]); 双门槛边界 (2→NaN/3→出值; 5→NaN/6→出值; 全单篇月→NaN); 斜率符号; 空输入→18+2 列在位全 NaN float64。
  8. per-model 独立降级: 删 finbert2 → 仅其族缺席, lblhet/disp 退化 2 模型。
  9. **三方闭环** ([R2] 重定义, v2 按字面 45≠51 恒红): 左端 = `keys(compute_article_distribution_cols(synth)) ∪ keys(compute_xmodel_dispersion(synth))`; 中端 = `iter_intermediate_cols` 全集; 右端 = `{src for (src,func) in build_aggregation_dict().values() if src.startswith(('_ent_','_xneg_ind_','_nt_art_','_xmd_art','_lblhet_art'))}` (只比源列集; `_nt_n_*` 键侧不入比)。+ agg 精确元组逐条 `agg[panel_col]==(src,func)`。
  10. stata 标签: 69 列 `labels.get(c,c)!=c` 且 ≤80 bytes。
  11. codebook: 69 条目在场 + source_stage=='Stage 23' + category 同值 + "over-identified Hansen J" 短语 + SSOT 覆盖差集为空。
  12. geography 反卷入注入 (compute_composite_indicators, 模板 test_bert_model_robustness.py:119-135)。
  13. 负例匹配锁: `_bert_model_match` 对 skew/xneg_t80 等 → None。
  14. 零新闻格 NaN + 文章级 parquet 无 51 中间列残留 + **panel/dta 无 `_nt_n_*` 残留** ([R2]) + 全列名 ≤32。
  15. **[R2] WP-E merge 合同**: 行数不变 + (target_bank,year) 键无重复 (v2 悬空承诺落位)。
- [ ] P4-2: 既有 gate 无回归。

### Phase 5 — 验收
- [ ] P5-1: **[R2] 入口定音** = 单 shim 顺跑 (不走 run_pipeline_function.py, 防 stage 21 skip-reject 付费风险): `F:\Anaconda3\python.exe news_process\40_panel_export_main.py` → 扫日志零 ERROR → 同解释器跑 `46_stata_export.py` (conda base 3.13, memory 铁律; 前提 = dev 上游 parquet 在位)。在位性 = 条件式断言 (输入概率列在位者其派生列必在位); sanity: 熵 ≤1+1e-5 ([R5]), frac 单调, iyvol≥0。
- [ ] P5-1b: 69 列 vs 最近邻既有列 corr, |corr|>0.95 按 MATH-1 记账 ([R2] finbert2 熵×|net_tone| 改「面板级大概率命中; 未中不视为 bug, 按实测记账」——逐篇 ρ=−1 但两次非线性+聚合后无解析保证)。
- [ ] P5-2: A/B 操作序 ([R2] 补: **两侧均从 repo 根跑 + conda base 解释器**): ① 前置 P0-0; ② A=基线 HEAD 全量 sweep, --collect-only 存选择集, Select-String FAILED 全量抓; ③ B=同选择集; ④ set-diff + 三连跑仲裁; ⑤ 既存红两侧对称 (dual_track NaN/benefit CSV/jieba flaky/test_panel_reproducibility 分叉红——新 69 列不在 golden 哈希清单不产新红)。
- [ ] P5-3: ruff 0 新增。
- [ ] P5-4: `git status` 全量逐项归属判定 → by-name; HEREDOC; **[R2] trailer 按 CLAUDE.md 字面值 `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`** (CLAUDE.md OVERRIDE 默认; 若认为已过时, P6-1 提请用户裁定更新该条, 不静默改); 绝不 amend/--no-verify。
- [ ] P5-5: 实读 dta 手算对拍: 熵/frac 各抽一个 3~5 篇格; [R2] 斜率若 dev 无有效月≥6 的格 (T=2 大概率), 对拍改在 gate #7 合成数据上执行并 §9 记账, 勿现场发明替代格。

### Phase 6 — 文档联动
- [ ] P6-1: CLAUDE.md 铁律段新增 (五族 + SSOT + 构念边界 + Hansen J + gate 名) + 最宽 dta 实读更新 (+ trailer 过时与否提请用户)。
- [ ] P6-2: memory 条目 + 索引。
- [ ] P6-3: §9/§10 回填 (注明 golden 双口径按 DEFERRED 支线, stratdiff/网络先例)。

---

## §5 铁律 checklist

- [ ] Hansen J: 三阈值梯子/per-model/三轨/WP-D 双轨各自 just-identified 并排, 禁混同一 over-identified J。
- [ ] **[R2] FWER 豁免逐族拆写**: ① xneg 梯子/skew 门槛/WP-D 双轨 = **规格稳健性并排** (镜像政治词权重/词典消融, 不设 FWER 模板); ② per-model 族 = 同构念跨模型但**非任何 paper 的 headline treatment**, 不触发 27_tableA12 先例; ③ conditional trigger 记账: 若未来某 paper 把 entropy/xneg 升为 treatment.primary, per-model 变体落入 A12 适用面 (届时 18_table9 白名单 30/30 + RES 矩阵 J 扩展原子联动)。
- [ ] 与既有梯子正交; per-model 独立降级; 无 `_lg`。
- [ ] 计数不变量零变动; 无 DAG 变更; `.do` 模板计数零变动 ([R2] 出处括注: 147=test_papers_b_route.py:176 / 21=stata_runner.py:682 `_EXPECTED_ROOT_DO` / 20=00_master 子 do 数 test_stata_templates.py:298)。
- [ ] 跨模型水平比较禁令三处落 codebook (§2.1/§2.2/§2.4)。
- [ ] golden DEFERRED + A/B 验收。

## §6 刻意不做

1. 加权孪生; 2. entropy/skew 的 std/sum; 3. LLM 侧同构; 4. `_lg`; 5. bank-month 面板; 6. xmodel per-pair 分解; 7. 梯子交叉; 8. xneg 分位校准 (样本依赖); 9. raw 未校正 iyvol (噪声-覆盖度构造性负相关); 10. iytrend WLS 稳健轨; 11. finbert2 熵剔除 (列照产, codebook 封); **12. [R2] lblhet deadband** (near-zero 符号噪声属标签基固有, 不引新参数)。

## §7 风险登记 (v3)

| # | 风险 | 概率 | 缓解 |
|---|------|------|------|
| R1 | net_tone 前缀误捕 | 低 (两轮实测全安全) | gate #13 负例锁 |
| R2 | zero-fill 误命中 | 低 (两轮 0 命中) | P0-4 + gate #14 |
| R3 | pandas skew API 漂移 | 低 (2.3.3 钉死) | gate 合成断言 |
| R5 | dev 稀疏格 C/E 大面积 NaN 误判 bug | 中 | 预记账"预期退化" |
| R6 | stata 标签缺失 | 中 | gate #10 (无既有 gate 兜底) |
| R7 | 并发同文件冲突 | 高 (现实发生) | P0-0 硬前置 |
| R8 | 文章级 df 内存 (+51 float64 中间列**存活至导出前** [R2], 生产 10⁶ 行 ≈+0.4GB) | 中 (生产) | 单点 drop + 生产首跑观测 |
| R9 | 概率非 softmax 归一 | 低 | P0-1② 硬前置 |
| R10 | 中间列泄盘 | 中 | §2.6 单点 drop + gate #14 |
| R11 [R2] | `_nt_n_*` 面板临时列泄入 dta | 低 | §2.3③ 即刻 drop + gate #14 |

## §8 DEFERRED

- golden 重生 (生产机); [R2] 届时 diff_golden `_ABL_RE` 对 +69 列报 **NON-ablation ADDED 属预期**, 与网络 +80 列一并处置。
- manuscript 披露: 五族 + Hansen J + 三处构念边界 + §2.7 措辞。
- 生产 T=19: C/E 覆盖率、iyvol max(0,·) 截断率、per-格可用模型数、corr 矩阵复测。

## §9 Phase 0 侦察实测记录

两轮评审预核完成项 (2026-07-03, 累计 9 agent 实测):
- 列名长度/冲突/zero-fill/net_tone 消费点/'skew' 协议/日期非空/washing 链路/merge 模式/`_is_` 生命周期 ✓ (第一轮)
- [R2] 行号全量复核 100% 准确 @脏树; runner 全时序链 (1128→1139→1180→1723→2699→2702) 实证; WP-E drop 窗口真实存在; `_KNOWN_BLAS_RE` 0 意外命中; codebook 拆分 63 宽前缀+6 'bert' 子串; disag_{b}=概率均值基勘误; network merge 同构实为 6 处; P0-0 前提 (+24 行) git diff 逐字复核成立 ✓ (第二轮)

待 P0-0 后实施者复核: P0-1 (Σp/掩码/中性列)、P0-2/P0-4 复跑、P0-5、行号终核。
待 dev 真跑后回填: per-格逐篇可用模型数分布 (§2.4); P5-5 斜率对拍落点 (盘上格或合成)。

## §10 评审与实施记录

**第一轮 (v1→v2)**: 4 镜头 (架构/统计/命名/流程), **31 条独立 findings = 2 BLOCKER + 13 MAJOR + 12 MINOR + 4 INFO** ([R2] 勘误: v2 误记 "22 条=2+10+7", 且漏记 P-F5 [MAJOR, 外科分离→收敛负例锁] 与 A-F6 [INFO, parse_time 已滤日期])。BLOCKER: S-F3 xneg 二分类阈值语义 / P-F1 并发同文件。主要方案变更: WP-D 双轨 (Σ66→69)、iyvol 采校正版、叶模块定音、P4-1 9→14 项、P5-2 操作序、P0-0 硬前置。31/31 落地 (保真度审计确认 31 完整 + P-F6③ 执行位由本轮补齐)。

**第二轮 (v2→v3)**: 5 镜头复审 (保真度/数学 break-it/行号事实/铁律合规/实施 dry-run), 核心发现 (跨镜头独立撞出即三重确认):
- **BLOCKER ×2**: iyvol 公式 n_t=1 无定义+ddof 未钉 (→§2.5 完整定义: 池化 σ̂²+双 ddof=1+双门槛+含单篇月校正); SKEW 掩码两备选全废——pos_count 列不存在且同族语义=argmax 判正数 (内生选择), pre-agg 连坐击穿 (→§2.3 唯一实现 `_nt_n_*` 辅助计数, 数学/行号/dry-run 三路独立确认)。
- **必红 gate ×1**: 熵-|nt| Spearman 方向写反 (+1→**−1**, 严格递减变换)。
- **MAJOR**: lblhet sign(0) 未定义+逐篇 infer_failed 混合漏记一半; 叶模块输入/API 合同缺失; gate #9 闭环按字面 45≠51 恒红 (→三端重定义); drop 时点致 Phase 2 返工 (→单点 2699); disag_{b} "argmax 计数基"事实错 (→概率均值基); §1.5 66/3→63/6; §10 台账计数错。
- **MINOR/INFO ≈20**: allclose rtol=0 / 单调性 NaN-aware / np.where 反模式 / |G1| n=4 上界=2 / P5-1b "必中"降格 / "对数占比"措辞 / FWER 逐族拆写 / `_ABL_RE` ADDED 预期 / trailer 字面值定音 / P5-1 入口定音 (单 shim 防付费) / repo 根+conda base / "→3326" 删 / 147/21/20 出处 / codebook 字段值表 / fixture 最小 schema / IYVOL 锚 / 空 frame 18+2 列 / merge 前 pre-drop / P0-0 worktree 触发条件 / description 白话承诺。
- 合规镜头: 0 BLOCKER/MAJOR, CLAUDE.md 全铁律对拍通过; 行号镜头: 准确率 100% (行号), 事实错 2 处 (均措辞级, 已勘误)。

**第三轮终验 (v3 收敛确认)**: 1 路终审 agent 独立核对: ① 第二轮 12 大项裁定 **12/12 完整落地、零扭曲**; ② v3 自身新缺陷扫描仅 3 条措辞级 nit (§2.3 pos_count "不存在"与 §1.10 冲突 / fixture ≈29 实为 27 / "√3/2" 记法歧义), **已全部当场勘正** (本版); ③ 代码事实抽查 (encode.py:908 count 先例 / :1442-1450 drop 先例 / attention_media.py:1697-1699 pre-drop 先例 / stata_export.py:682-685 现 8 键 / runner.py:2699/2702 / 147-21-20 三出处) **100% 准确**; ④ iyvol 无偏性等式与 |G1| 上界经独立验算成立; ⑤ 69 列/51 中间列/gate #1-#15 编号/交叉引用全部自洽。

**第四轮增量审核 (2026-07-03, 触发=并发会话推进)**: dta-coverage 会话把其终审揪出的 2 个确认缺陷**修进了工作树** (finbert2 argmax fix @runner.py:210-217 + l1o IV 模板 fix ×2, 均未提交), 且另一论文/标注会话产生 ~1.2 万行 manuscript 改动。逐点核实交互: ① finbert2 fix 与本计划**零列消费交集** (本计划不用 `_is_finbert2_*`/washing/disag_finbert2); ② fix 的 `notna().any()` 守卫独立佐证本计划 §2.1/§2.6 "类集不凭列存在" 设计; ③ [R5 勘误] runner/attention_media 行号实为 HEAD 口径 (脏树 +4/+3), 三处"与当前树一致"断言不实已改写, 语义锚不受影响; ④ P0-0 脏树面记账已更新 (3→5 pipeline 文件 + 2 模板 + manuscripts)。计划本体零改动需求。

**第五轮终审 (2026-07-03, 发布前双路: 全文完整性闸 + 实施预检)**: 完整性闸判定设计/公式/gate/铁律**零缺陷、四轮裁定无一翻案**, 收 F1 行号坐标系混用 (HEAD vs 脏树, 三处"已一致"断言不实——本版已改写) + F2 untracked 2→3 + F3 iyvol value_range 不封顶 (√(4/3) 反例——已宽记 [0,1.2]); 实施预检判定**条件性 GO**: 树状态/挂载点/dev 数据/测试基建全实测, P0-1 三项预过, 新收两处 ε 校准 (Σp 容差 1e-6→2e-4, 熵上界 1e-9→1e-5, dev 四位小数舍入实证) + P0-0 三案排序 (首选=并发 7 文件先单独成 commit)。全部六处修正为文档级, 已在本版落地。

**终判: v3-final (五轮收敛) = **approved_for_execution** (用户 2026-07-03 批准执行全部计划任务)。P0-0 按首选案解除 (并发 dta-coverage 7 文件单独成 commit), 随后 Phase 0→6 顺序实施。**

---

## §11 实施记录 (2026-07-03/04, 全 Phase 落地)

- **P0-0**: 并发 dta-coverage 7 文件 by-name 单独成 commit **main=02c84d10** (pre-commit ruff 过; 排除 constants.json 与进行中的 validation/* 标注会话产物; manuscripts 已被论文会话自行提交 ed596d62 → HEAD 前移)。提交后挂载点终核: concat=1124 / aggregate=1132 / 7h-net=1727 / log_diagnostics=2703 (与 [R5] 预判的 +4 偏移一致)。
- **Phase 1/2**: `bert_distribution.py` 叶模块 (SSOT 4 常量 + 3 声明器 + `iter_agg_entries` + 3 compute 函数) + runner 三挂载 (4z 逐篇/7h-bd 年内 merge/8z-bd 单点 drop) + encode (agg 无条件注册 + `_nt_n_` 掩码即 drop)。合成冒烟: 51/69/60 计数 ✓, sign(0)→2/3 ✓, 空 frame 20 列 float64 ✓。⚠ 实施发现 (进 fixture 纪律): 合成 `neg=1−pos` 浮点构造会产生 "|nt| 恰并列而熵差 1e-17" 破坏 ρ==−1 的秩镜像 — fixture 必须用互异 |nt| 精确小数对; 真实数据 4 位小数存储不受影响。
- **Phase 3**: codebook 69 显式条目 (69/69 在位, category 单值) + stata_export (+7 metric 键 + 6 xmodel 精确键; 69 列 0 fallback 0 超 80 字节)。
- **Phase 4**: `tests/test_bert_distribution_metrics.py` 33 用例全绿; 既有 4 gate (bert_robustness/political_ladder/dag_consistency/parity) 72 用例全绿; ruff 全过 (2 处 import 排序 --fix)。
- **Phase 5**: P5-1 单 shim 40→46 真跑 (NEWS_PROCESS_LLM_OFFLINE=1, $0) exit 0, 三条新日志行在位 (51/51 中间列、年内 merge 18 列 143 格 220 行不变、导出前 51 列清理); 面板实读 **3395 列** (3326+69 恰合), 69/69 在位, `_nt_n_`/文章级中间列**零残留**, sanity 全过, skew 26/220 格 (n≥10 门槛真实生效), iyvol/iytrend dev 全 NaN (R5 预期退化)。46 dta = **3395 = 面板恰等**。P5-1b: 无一对 |corr|>0.95 (finbert2 熵×|net_tone| 面板级 −0.88 — v3 降格"必中"的裁定被实证)。P5-5: 熵/xneg 手算对拍精确到 1e-10 (上海银行 2017, n=4); 斜率 dev 无 ≥6 月格 → gate #7 合成覆盖。P5-2 A/B: 只 stash 本计划 4 tracked 文件 (finally pop 保还原), 双侧同选择集 (--ignore 新 gate), **FAILED 集 23↔23 恰同、差集双向为空、0 新增失败、无需仲裁**。
- **Phase 6**: CLAUDE.md 新增"BERT 分布形状五族"铁律段 + 最宽 dta 行 3308→**3395** (实读); memory 更新; 本节回填。
- **DEFERRED (不变)**: golden 生产机重生 (diff_golden `_ABL_RE` 将报 +69 NON-ablation ADDED 属预期) + manuscript 三处构念边界披露 + 生产 T=19 覆盖率/截断率/per-格模型数/corr 复测。

## §12 实现级终审 (2026-07-04, 发布前三路 + 小修收口)

三路只读终审 (计划保真度逐合同 / 代码 break-it 含合成实测 / 集成面+推送安全):
- **保真度**: 通过 (高保真), **0 MAJOR** — 六条叶模块合同/五族公式逐项验算与计划精确一致 (含 iyvol 门槛 `w_sum==0 ⟺ ≥1月n_t≥2` 精确等价、sign(0) 双向锁、`fillna(0)` 判定为不可达防御分支无害); gate 15 项 14.5/15 对号。
- **break-it**: **0 BLOCKER/0 MAJOR** — 13 项合成实测探针全过 (乱序/重复 index 对齐、-0.0 语义、跨 piece concat 外连接、groupby var/skew/count NaN 行为、真跑 aggregate_panel 掩码链路含"12 篇仅 3 非 NaN 按 3 掩"、zero-fill 四正则对 69 列零误伤、merge dtype 容错)。
- **集成面**: GO — 六类下游消费者 (standardize 白名单/iv_did/iv_extensions/6c/7h 族/stage 51/export/`.do` 模板通配) 全为显式清单或限定前缀, 零误卷入; 推送清单仅本计划提交, 无外来 hunk/大文件/秘密/amend 痕迹。
- **小修收口** (合并 1 commit, 全部落地): F1 [MINOR] 真三分类缺中性列的静默 K=2 降级通道封死 (`continue` 键不产 + 新 gate `test_three_class_missing_neutral_no_silent_k2`; 生产不可达但值域可越 1 至 1.0575); D2 补 disp ddof=1 精确手算 gate (nt=±1 镜像 → 行 SD≡1.0) + lblhet 2-模型支撑 1 端; F2 runner 4z 注释事实勘误 (WP-E 从概率列重算 nt, 不消费 `_nt_art_*`); F3 裸 assert → RuntimeError (-O 剥除风险); D4 fixture 计数 docstring 27→30。gate 33→35 用例全绿, ruff 全过。
- 记账不修项: F4 恒等式依赖上游 pos/neg 原子 NaN 契约 (encode 注释已记账, 上游违约时静默破裂无实数据 gate — 剩余风险); D5 encode 掩码循环硬编码轨字面 (与全仓惯例一致)。
