# 执行计划：向 strategic_diff / policy_similarity 的 word/LDA 轨注入金科词

**日期**: 2026-06-21
**作者**: Claude (ultracode)
**状态**: ✅✅ **已实施 + 四轮审核 + 经验实测闭环 = 实现万无一失（零阻断）**。
  - **代码已落地** `pipeline/features/strategic_diff.py`：`_get_diff_tokenizer()`（DCL+RLock 注入 1506 金科词独立实例 + 空词典 loud WARNING 优雅降级）+ `_jieba_tokenizer` 改写；`tests/test_omni_fix_strategic.py::TestFintechInjectionWordLDA` 8 个回归测试；**73 passed / ruff clean**。
  - **实现审核** wf_c37656e9-a66（6 维 32-agent + 对抗 + 魔鬼代言人）：**零阻断/零必修**；2 项 follow-up 已落地（空词典 loud WARNING / 源码级回归锁）。
  - **经验闭环**：实现 `_jieba_tokenizer` 与已验证 prototype 在 **1125 篇真实文章 717843 tokens 逐一致 0 失配** → 探针 C1–C6 全转移到实现。
  - **唯一 gated follow-up**（非阻断, 因 `export.py` 正被并行会话改, 刻意不碰）：§4 步骤2 的 codebook/export 列标签补"(领域词注入)"披露 + paper_spec note；+ golden 受控重生（§5.0，T=18 生产）。
**（原状态：三轮审核 + 经验实测通过 = 可执行（须采 §5.0 外科隔离注入））**。
  ① 5 维 29-agent 对抗审核 (wf_97b431e1-448)：5 P0 + 设计/范围 P1 全证伪；P1-a/b/c 已订正。
  ② 顶刊最高标准 6 维 17-agent 终审 (wf_9dd304e5-6ee)：8/9 P0/P1 证伪；**魔鬼代言人抓出唯一真材料缺陷 = `_allv` companion 陈旧**（前两轮 + 经验探针均漏），已纳入 §3.1b/§5.0/R6。
  ③ 主循环经验实测（探针 `scripts/audit/_jieba_probe/probe_inject_blast_radius.py`, 真实 71 行）：C1 char 字节免疫 / C2 word 变 / C3+C4 word+LDA 注入态两跑 bit 一致 / C6 无 NaN 爆增 —— 机制铁证。
**关联**: jieba 有效性审计 wf_783e21fc-8d6；审核 wf_97b431e1-448；终审 wf_9dd304e5-6ee
**⚠ 操作事故记录**: 终审某 general-purpose 子代理为实测 `_allv` 跑了一次 panel build, 副作用 = 截断 gitignored 中间件 `40_article_bank_level.parquet`(847行→1行) + bump 了 tracked sidecar `v3_5_1_constants.json`(已 git checkout 还原); 中间件可由重跑 panel 再生, 无 tracked 源码被改。

---

## 0. 一句话目标

让 `strategic_diff.py` 与 `policy_similarity.py` 的 **word 级 TF-IDF 轨**与 **LDA 主题轨**改用
**注入了 1506 个金科词的独立 jieba Tokenizer**（取代当前裸 `jieba.lcut`），使这两个"词级稳健性
对照轨"看到完整的领域复合词（金融科技 / 区块链 / 第三方支付 …），与 char 轨 / embedding 轨的
**领域感知口径一致** —— 这是一次**次级稳健性轨的质量提升 / code-hygiene 修复，不改任何论文主因变量**。

---

## 1. 背景与现状（已实测核实）

### 1.1 问题来源
jieba 有效性审计（32-agent，对抗验证）确认两条 **P1→impact=marginal** 真缺陷：
- `strategic_diff.py` word/LDA 轨用裸 `jieba.lcut`，14 个金科复合词被切碎（实测：金融科技→金融/科技）。
- `policy_similarity.py` 复用同一分词器，同样切碎。

### 1.2 唯一变更点（已 grep 穷举核实）
`strategic_diff.py:320` 的 `jieba.lcut` 是该文件**唯一**裸 jieba 调用：
```python
_STOPWORDS = {'的','了','在','是','和','与','为','对','等','将','也','及','到','从','中','上','下','不'}  # L306-307

def _jieba_tokenizer(text: str) -> list[str]:           # L310
    return [w for w in jieba.lcut(text) if len(w) >= 2 and w not in _STOPWORDS]   # L320
```
所有 8 处下游消费**全部经 `_jieba_tokenizer`**（无第二条裸 jieba 路径）：

| 行号 | 消费点 | 影响列族 |
|------|--------|---------|
| 494 | `_build_tfidf_sim_matrix(mode='word')` | `strat_diff_n*_w` / `strat_sim_max_w` (+ctx +ss) |
| 555,564 | `_build_lda_jsd_matrix` CountVectorizer | `strat_diff_n5_lda` / `strat_sim_max_lda` (+ctx +ss) |
| 1054 | `_build_fluidity(mode='word')` | `strat_fluidity_w` (+ctx +ss) |
| 1141 | `_compute_tfidf_coherence(mode='word')` | `coh_tfidf_w_{full,ctx,ss}` |
| 1227-1228 | `_compute_*` set-overlap coherence | (词集连贯性派生) |
| 1288,1294 | `_compute_lda_coherence` CountVectorizer | `coh_lda_{full,ctx,ss}` |

`policy_similarity.py` 通过 `from ...strategic_diff import _build_tfidf_sim_matrix, _build_lda_jsd_matrix`
（L48-59）复用 → 其 `auth_sim_tfidf_w*` / `auth_sim_lda*`（+ `_allv` 孪生）**自动受同一修复覆盖**。

> **结论：改 `_jieba_tokenizer` 一处，两模块、TF-IDF/LDA/Fluidity/Coherence 四族全覆盖。**

### 1.3 不受影响（必须验证字节不变）
- **char 轨**：`analyzer='char_wb', ngram_range=(2,4)`，**不经 jieba** → `strat_diff_n*`(无 _w)、`strat_sim_max`、`coh_tfidf_c_*`、`centroid_diff_tfidf_c`、`auth_sim_tfidf_c*` 全部不变。
- **embedding 轨**：`emb` / `emb_t2v` / `auth_sim_emb*`，不经 jieba → 不变。
- **全部非文本列**：不变。

---

## 2. 设计决策

### D1：独立注入 Tokenizer（**不**走全局 jieba）
新增模块级懒加载单例 `_get_diff_tokenizer() -> jieba.Tokenizer`，用 **DCL + RLock**（镜像
`tone_words._get_tone_tokenizer` / `lexical_complexity._get_pristine_tokenizer` 既有最佳实践），
金科词只 `add_word` 进**此实例**，全局 `jieba.dt` 保持纯净。

**理由**：
- 与项目首选模式一致（审计认定全局注入是 `fintech_intensity` 的"设计债"，不应复制）。
- 对/从同进程其它 jieba 消费者**零污染**（strategic_diff 跑在 panel runner 内，同进程可能有其它消费）。
- 注入幂等 + jieba 0.42.1 冻结 → 确定性。

### D2：注入内容 = 1506 金科词（单一事实源）
复用 `core/text/ahocorasick.py::load_fintech_dict(CONFIG['paths']['fintech_dict_file'])`
（与 `news_fintech` / `ctx_materializer` / `fintech_intensity` 同源同词表），取其返回的
`FINTECH_KEYWORDS` 列表 `add_word`。

**理由**：单一事实源，词表增删自动同步，不引入第二份硬编码。

### D3：**不**注入银行名（明确划出范围）
- 用户诉求明确为"金科词"。
- 银行身份已被 **char 轨**（char_wb n-gram 覆盖银行名字符）与 embedding 轨捕获。
- 注入银行名会扩大 golden 改动面、混入第二个语义维度。
- → 列为**可选 follow-up**（§7），本计划不做。

### D4：**无需** matchable/unmatchable 分区（区别于 fintech_intensity）
`fintech_intensity` 需剔除 6/1506 含空格顿号的"永不可匹配"词，是因为它做**精确关键词→权重宇宙**
匹配。本场景是 **bag-of-words 向量化**：6 个含空格词 `add_word` 后仍被 jieba 块切分正则切开，
退化为其子 token（与注入前完全一样），**无害**。故全部 `add_word`，不加分区逻辑、不加 WARNING。

### D5：保留 `len>=2 + _STOPWORDS` 过滤不变
```python
def _jieba_tokenizer(text: str) -> list[str]:
    return [w for w in _get_diff_tokenizer().cut(text) if len(w) >= 2 and w not in _STOPWORDS]
```
注入的金科词均 ≥2 字（或退化为子 token），过滤规则对它们无副作用。`_STOPWORDS`（18 个通用虚词，
**不含**任何金融信号词）保持不变。

### D6：确定性
- `add_word` 幂等、isolated 实例、jieba 0.42.1 冻结。
- LDA 已 `n_jobs=1, random_state=42`（L570-572，单线程逐位可复现）。
- 注入不引入新随机性。
- ⚠ **`n_jobs=1` 仅是确定性的必要条件之一**：`*_lda*` / `coh_lda*` 列的逐位可复现仍依赖 §5.1 钉死的**全 BLAS 线程=1 + PYTHONHASHSEED=0**（memory `golden-regen-omp-determinism` 实测 E≡F 含全部 `coh_lda_*` 0 漂移）。只读本节者勿据 `n_jobs=1` 单独推断"已确定"。

---

## 3. golden 影响面（精确清单）

### 3.1 会变的测度列（word + LDA 两族）
**strategic_diff**（`40_panel` 列）：
```
# word TF-IDF 族 (_w)
strat_diff_n3_w  strat_diff_n4_w  strat_diff_n5_w  strat_diff_n6_w  strat_diff_n7_w
strat_sim_max_w  strat_fluidity_w
strat_diff_n5_w_ctx  strat_sim_max_w_ctx
strat_diff_n5_w_ss   strat_sim_max_w_ss
centroid_diff_tfidf_w  centroid_diff_tfidf_w_ctx  centroid_diff_tfidf_w_ss
strat_fluidity_w_ctx  strat_fluidity_w_ss   # ← strat_fluidity_w_ss 经 _sub_tracks(L1692,1702) 落列, 审核 P1-a 补
coh_tfidf_w_full  coh_tfidf_w_ctx  coh_tfidf_w_ss
# LDA 族 (词表经 jieba → 注入改变词表 → theta → JSD 全变)
strat_diff_n5_lda  strat_sim_max_lda
strat_diff_n5_lda_ctx  strat_sim_max_lda_ctx
strat_diff_n5_lda_ss   strat_sim_max_lda_ss
centroid_diff_lda  centroid_diff_lda_ctx  centroid_diff_lda_ss
coh_lda_full  coh_lda_ctx  coh_lda_ss
```
**policy_similarity**（`40_panel` 现有列, 会变值）：
```
auth_sim_tfidf_w_full  auth_sim_tfidf_w_ctx  auth_sim_tfidf_w_ss
auth_sim_lda_full      auth_sim_lda_ctx      auth_sim_lda_ss
```
> ⚠ **LDA 族爆炸半径 > _w 族**：LDA 的 CountVectorizer 用 `_jieba_tokenizer`，注入改变词表 →
> theta 分布 → JSD → **全部 `*_lda*` 列变**。用户已点名"word/LDA 轨"，知情。
> ✅ 经验已证（探针 §C2/C4, 真实 71 行）：word 矩阵 max|Δ|≈0.023、LDA mean-offdiag 0.642→0.695，两者注入态两跑 bit 一致。

### 3.1b ⚠ `_allv` 全年份孪生 = golden 中**尚不存在的新增列**（终审 P1 / 必修, 见 §5.0）
**关键修正**（终审魔鬼代言人维度抓出, 主循环已实测复核）：`policy_similarity.py:310-317` 在
`config/filtering.yaml:73 all_vintage_companion: true`（默认开）时**无条件**并列产 **5 法 × 3 轨 = 15 个
`auth_sim_*_allv*` 列**，但**实测当前 golden 与 51_panel 均含 0 个 `_allv`**（该 companion 2026-06-21
新接线、面板从未为它重生）。故 `_allv` **不是"会变值的现有列"，而是 golden 缺失的新增列**：
- **6 个 jieba-affected** `_allv`（`auth_sim_tfidf_w_allv{_full,_ctx,_ss}` / `auth_sim_lda_allv{_full,_ctx,_ss}`）—— 受本改影响 + 新增。
- **9 个非 jieba** `_allv`（`auth_sim_tfidf_c_allv*` / `auth_sim_emb_allv*` / `auth_sim_emb_t2v_allv*`）—— **与本改无关** 但同样新增。

⚠ **后果**：任何**全 stage 重跑**会让这 15 列全落 `test_panel_reproducibility.py:161-163` 的列集断言
`extra`（在逐列哈希**之前** FAIL），且 9 个非 jieba `_allv` 会**伪证伪** §3.2 的 char/emb 外科性。
→ 解法见 §5.0（用外科隔离注入**绕过**, 或先做 `_allv` baseline 同步）。

### 3.2 必须验证**字节不变**（外科性证据, 采外科隔离注入路径时成立）
所有 char 列（`*_tfidf_c*`, `strat_diff_n*` 无 _w, `strat_sim_max` 无后缀, `coh_tfidf_c_*`,
`auth_sim_tfidf_c*`）、所有 embedding 列（`*_emb*`, `*_emb_t2v*`）、所有非文本列、**以及当前缺失的 15 个
`_allv` 列保持缺失**。**采 §5.0 外科隔离注入**（只重算 §3.1 列注入回现有面板）时：仅 §3.1 现有列变值、
其余 0 失配、`_allv` 仍不出现 = 列集断言不破 + 外科性成立。经验已证 char 矩阵注入前后字节一致（探针 §C1, hash 恒 `a5a6ae36`）。

---

## 4. 实施步骤（代码层）

1. **`strategic_diff.py`**：
   - 顶部新增 `import threading` + `from news_process.core.text.ahocorasick import load_fintech_dict`（若未导入）。
   - 新增模块级 `_DIFF_LOCK = threading.RLock()`、`_DIFF_TOKENIZER = None`、
     `_get_diff_tokenizer()`（DCL 懒加载 + 注入 `load_fintech_dict` 的 `FINTECH_KEYWORDS`；
     词典缺失 → loud WARNING + 退化为未注入 Tokenizer，**绝不 raise**，镜像 §SAFE 降级）。
   - 改 `_jieba_tokenizer` body：`jieba.lcut(text)` → `_get_diff_tokenizer().cut(text)`。
   - 更新 `_jieba_tokenizer` / 文件头 docstring：声明 word/LDA 轨现为**领域注入**口径（披露）。
2. **披露**：`pipeline/panel/codebook.py` 或 `export.py` 中 word/LDA 列标签/codebook 注释补"(领域词注入)"措辞（口径披露，非必须改值）。
2b. **论文产物消费链披露**（审核 P1-b 补）：受影响的 `centroid_diff_tfidf_w` / `centroid_diff_lda` 列**已被** `papers/strategic_diff/paper_spec.yaml:86` 的 centroid 稳健性族（Romano-Wolf FWER 校正，L87）声明，并由 Stata 模板（`papers/.../strategic_diff/10_table1_descriptives.do.tmpl`、`12_table3_mechanism.do.tmpl` 消费 `strat_diff_n5_w` / `strat_diff_n5_lda`）消费。⚠ 订正（终审 P2）：`papers/strategic_diff/tables.py` 的 `_TABLE1_VARIABLES` 是**硬编码列表**, 须**核实**其是否含 `centroid_diff_tfidf_w`/`centroid_diff_lda`（若未含则这些列仅经 Stata 模板路径, 不经 tables.py）—— 勿笼统称"tables.py 自动读取"。⚠ **主回归 RHS = `strat_diff_n5`(char 轨, paper_spec.yaml:75)，不受本改影响**；但上述 word/LDA 列是**已发表的稳健性对照列**（非"未用列"），注入后须 `python -m news_process.papers._common.stata_runner build-replication` re-generate 相关表方反映新值；`paper_spec.yaml` 的 `centroid_diff_tfidf_w`/`centroid_diff_lda` note 补"(含金科词注入)"来源标注。⚠ 命名陷阱: `paper_spec.yaml:75` 的 `tobin_q_w` 中 `_w` = **winsorized**, 与 word 轨 `_w` 无关, 勿混淆。
3. **测试**（§6）。
4. **golden 重生**（§5）。

> **铁律**：不碰 char 轨 `_kw`（L491-492 等）、不碰 `_STOPWORDS`、不碰 embedding 轨、不碰 shim。

---

## 5. golden / 确定性策略

### 5.0 ⚠ 必修前置：用**外科隔离注入**, 不做全 stage 重跑（终审 P1 / material）
**终审唯一必修阻断项 + memory 一致结论**：**禁用"全 panel 重跑后全量重哈希"**, 改用已验证的
**外科隔离注入范式**（镜像 memory `_inject_named_entity_20260620` / `_inject_boilerplate_20260620`
/ `loughran-exc-cols-fix-regen`：只 ADD/改目标列, 既有列 0 漂移字节级）。两大理由：
1. **绕过 `_allv` 陈旧**（§3.1b）：全 stage 重跑会让 `compute_authoritative_similarity` 吐 15 个
   golden 没有的 `_allv` 列 → 列集断言在哈希前 FAIL, 且 9 个非 jieba `_allv` 伪证伪外科性。外科隔离注入
   **只重算 §3.1 现有列并注入回现有面板**, 不触发 policy_similarity 全 run → `_allv` 不出现, 列集不变。
2. **绕过 BLAS 伪失配**：全链重跑会重算 emb/网络中心度列, 这些在非 canonical/异线程下漂移 →
   与 jieba 无关的伪失配污染 Gate。外科隔离注入**不重算 emb/网络列**, 从源头消除。

**外科隔离注入步骤**：
1. canonical env（下方钉死）下, 隔离跑 `strategic_diff` + `policy_similarity`（注入态）的 word/LDA/Fluidity/Coherence 路径, **只产 §3.1 现有列**的新值;
2. **validation gate**：重算若干既有 **char/emb** 列对 committed golden, 证 **0 失配**（忠实性证据, 证注入未触非 jieba 列）;
3. 纯注入回 `40_panel.parquet`（**不重算 emb/网络列、不新增 `_allv`**）, `46/51` 走确定性再导出;
4. golden **外科更新**：仅重算 §3.1 现有列的哈希条目, 其余字节不变。
> 备选（仅当确需全 panel 重跑）：先做一次**与 jieba 无关的 `_allv` baseline 同步**（把 15 个 `_allv` 纳入 golden）,
> 再做 jieba 注入重跑, 使 Gate 的 `extra` 集为空; 并把 9 个非 jieba `_allv` 显式从外科性判定划出 + 披露。

### 5.1 受控注入的环境与验证 gate
- 环境钉死（镜像 memory `golden-regen-omp-determinism`, 经验已实证 §C3/C4 在此 env 下 word/LDA 两跑 bit 一致）：
  `PYTHONHASHSEED=0` + `MKL_NUM_THREADS=1` + `OMP_NUM_THREADS=1` + `OPENBLAS_NUM_THREADS=1` + `NUMEXPR_NUM_THREADS=1` + `KMP_DUPLICATE_LIB_OK=TRUE`。
- 跑链：**外科隔离注入**（§5.0）→ 注入回 40_panel → 46/51 确定性再导出（**不走全 stage 25/26 重跑**）。
- **三段验证**（gate）：
  1. **外科性**：新 40_panel 逐列哈希对当前 golden，**仅 §3.1 清单列变**，char/emb/非文本列 **0 失配**。
  2. **确定性**：同环境重跑两次（A vs B），§3.1 列**两次 0 漂移**（证 word/LDA 注入轨可复现）。
  3. **方向合理性**：抽查若干 `strat_diff_n5_w` / `auth_sim_lda_full`，注入前后变化幅度有限、无 NaN 爆增（注入只精化分词，不应整列坍缩）。
  4. **同 env 防伪失配**（审核可选强化补）：committed golden 须在**与 Gate 1 完全相同的线程 env**（MKL=1 等）下重生再比对 —— 否则若现 golden 是默认 MKL=24 下产出而 gate 钉 MKL=1，BLAS 敏感的 emb/网络列会产生**与 jieba 无关的伪失配**，污染外科性判定。或对已知 BLAS 敏感列（`*_emb*` / 网络中心度）改用数值容差 / 排除名单比对。
- gate 全绿 → golden **外科更新**（审核 P1-c 订正术语）：**重算 §3.1 列**为新分词器算出的真实值并刷新其哈希条目；§3.1 之外的列哈希与 JSON 结构字节不变。⚠ 这是**真重建值**，**不是** shim-renumber 计划里"键改、哈希值字节不变"的 $0 `re-key`（值确实变了，必须重算重写哈希）。

### 5.2 T=2 vs 生产 T=18（诚实限定）
- 本机 = T=2（86 banks × 2 years），**仅验管道机制 + 确定性 + 外科性**。
- 真实测度值的 golden 须**生产 T=18 全量重跑**才权威 → 列为 **gated / deferred**（项目惯例）。
- ⚠ 不在脏工作树 / 非 canonical env 下 bless（会误 bless 无关 BLAS-FP 漂移）。

---

## 6. 测试

| 文件 | 动作 |
|------|------|
| `tests/test_omni_fix_strategic.py` | 复跑确认不破；新增：`_jieba_tokenizer('银行金融科技区块链')` 含整词 `金融科技`/`区块链`（注入生效断言） |
| `tests/test_omni_fix_policy.py` | 复跑确认 auth_sim word/LDA 路径不破 |
| `tests/test_strategic_diff_embedding.py` | 复跑确认 embedding 轨不受影响 |
| `tests/test_25_audit.py` | 复跑 |
| 新增（可并入 strategic 测试） | (a) 注入确定性：`_get_diff_tokenizer().cut(x)` 两次相等；(b) 全局纯净：注入后 `jieba.lcut('金融科技')` 仍 == `['金融','科技']`（隔离证明）；(c) 词典缺失优雅降级不 raise |

ruff clean + 上述定向测试全过为提交前置。

---

## 7. 风险与权衡（诚实披露）

- **R1（设计权衡）char/word 轨独立性下降**：注入后 word 轨与 char 轨都"看见"金科概念，二者作为
  稳健性对照的独立性略降。**反驳**：当前 word 轨是"**坏的**词级表征"（领域词碎裂），注入后是
  "**干净的**词级表征"；它与 char 轨仍是 token-vs-charNgram 两种**不同表征**，独立性本质仍在。
  这正是"口径一致"的目的 —— 让 word 轨真正测"词级是否印证"，而非"坏分词器是否印证"。**须 codebook 披露**。
- **R2 LDA 爆炸半径 > _w**：见 §3.1。已知、知情、披露。
- **R3 方向性影响可能很小**：高频领域词（金融科技人人都提）IDF 本就低、被下权；注入主要精化
  **罕见多字领域词**的粒度。→ **不应期待注入显著改变稳健性结论**（这是好事：稳健轨应印证而非推翻主轨）。**管理预期：不改任何论文主因变量/主结论**。
- **R4 max_df=0.95 空词表 fallback 触发面变化**：注入改变词表组成，可能让 `_build_tfidf`/LDA 的
  `max_df=0.95→1.0` 降级在 T=2 退化样本上触发路径不同。→ §5.1 验证两模块在 T=2 仍跑通、无新异常。
- **R5 golden T=2≠T=18**：见 §5.2，gate/defer。
- **R6（终审必修, 已纳入 §3.1b/§5.0）`_allv` companion 陈旧 landmine**：`all_vintage_companion` 默认开但 15 个
  `auth_sim_*_allv` 列从未进 golden/panel；**全 stage 重跑**会让它们落列集断言 `extra` 致 Gate 在哈希前 FAIL,
  且 9 个非 jieba `_allv` 伪证伪外科性。→ §5.0 外科隔离注入**绕过**之（不触发 policy_similarity 全 run）。
  ⚠ 这是**先于本改存在的独立 landmine**, 任何全 panel 重跑都会踩到, 非本改引入。
- **R7（终审 marginal, 可选）血缘**：`strategic_diff` 产物未把 `fintech_dict.json` 纳入 `input_hashes`,
  注入后产物依赖词典内容却对其篡改失明（窄盲窗, 非硬 gate, 不破任何测试）。可选润色, 镜像 `news_fintech` 已纳入的先例。

---

## 8. 回滚 / 提交

- 单变更点 → 回滚 = 还原 `_jieba_tokenizer` 一行 + 删 `_get_diff_tokenizer`。
- 提交：`strategic_diff.py` + 测试 + （可选）codebook 披露 + golden（受控重生后）by-name add，
  排除并行会话脏文件；ruff Passed；commit message 含口径披露与 golden 重生说明。
- 生产 T=18 golden 权威重生单列 gated TODO。

---

## 9. 验收清单（提交前逐项打勾）
- [ ] `_jieba_tokenizer` 唯一变更点改成注入实例；全局 jieba 隔离测试通过
- [ ] 金科词单一事实源 = `load_fintech_dict`，无第二份硬编码
- [ ] 词典缺失优雅降级（WARNING，不 raise）
- [ ] 外科性 gate：仅 §3.1 列变，char/emb/非文本 0 失配
- [ ] 确定性 gate：§3.1 列两跑 0 漂移
- [ ] ruff clean + 4 个定向测试 + 新增注入测试全过
- [ ] codebook/标签披露 word/LDA 轨为领域注入口径
- [ ] 生产 T=18 golden 权威重生列入 gated TODO
