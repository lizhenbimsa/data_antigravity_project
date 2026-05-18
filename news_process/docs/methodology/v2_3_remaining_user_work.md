# v2.3 Remaining Work · USER_ACTION_REQUIRED 标注

**Generated**: 2026-05-18 (第 17 轮 audit 后, user 明确要求标注 AI 不可完成项)
**Branch**: v2.3-followup-v2
**Status**: v2.3 implementation 主体 (15/16 PR) 已在 main 生效; 剩余工作需用户/外部资源/人工

---

## 标注约定

| 标记 | 含义 |
|---|---|
| 🔴 **AI 不可完成** | 完全不能由 AI 自动化, 必须用户/外部资源 |
| 🟡 **AI 部分可做** | 草稿可由 AI 生成, 但最终质量需用户/专家 |
| 🟢 **AI 可继续** | 仍可由 AI 完成, 但当前 session 时间/资源约束未做 |

---

## Layer 2 · 解锁 v2.3 真跑通（AI 不可完成）

### 🔴 L2.1 启用 5 个 v3.7.0 包

**操作**：
```powershell
cd F:\WiseSearch\data_antigravity_project
# 取消 requirements.txt 5 行 v3.7.0 包注释
notepad news_process\requirements.txt  # 删除 5 行的 # 注释符
pip install -r news_process\requirements.txt
```

**包**：bertopic / umap-learn / hdbscan / faiss-cpu / krippendorff

**阻塞原因**：
- AI 无 pip install 权限（sandbox + 环境管理）
- HF 网络限制（CLAUDE.md memory `hf_network` 直连超时）

**阻塞下游**：D 组所有 PR（#10-#13）真实跑通; stage 39e/39f validation

**时长**：10-15 min（含包下载）

---

### 🔴 L2.2 EPU 中国版 CSV 下载

**操作**：
```powershell
# 访问 https://www.policyuncertainty.com/scmp_monthly.html
# 下载中国月度 EPU 数据 CSV
# 保存为: news_process\data\external\epu_china_monthly_2007_2024.csv
# Schema: year,month,epu
```

**阻塞原因**：
- AI 无外网访问权限
- policyuncertainty.com 是第三方学术网站, 数据 license 用户确认

**阻塞下游**：stage 16 真跑通; 11 paper macro control 加入

**D-0 实测项**：实际覆盖年份（若止于 2022 → 用 Davis-Liu-Sheng 2019 NBER 中国本土版或 Huang-Luk 2020 R 代码自构 2023-2024）

**时长**：30 min（含数据 review）

---

### 🔴 L2.3 Stata `ssc install ritest`

**操作**：
```stata
* 本地 Stata MP 19.5 命令行
ssc install ritest, replace
ssc install boottest, replace  // PR #7.5 collab 也需
which ritest
which boottest
```

**阻塞原因**：
- AI 无 Stata 进程调用权限
- SSC repo 在 IDEAS-RePEc, 需用户机器联网

**阻塞下游**：4 paper Stata `18_*_robustness.do.tmpl` ritest 真跑通

**D-0 实测项**：失败 → 手动从 https://ideas.repec.org/c/boc/bocode/s458352.html 下载 ritest.ado + ritest.sthlp 拷贝到 `~/ado/personal/r/`

**时长**：5 min

---

## Layer 3 · 专家审定 / 人工标注（AI 不可完成）

### 🔴 L3.1 A1 LM 4 子词典 v0.1.5 → v0.2

**现状**：v0.1.5 实测 314 词（uncert 83 / litig 104 / constr 76 / modal_strong 51），LM 2011 原版 14-41% 覆盖
**目标 v0.2**：LM 2011 原版 1219 词完整覆盖（uncertainty 285 / litigious 731 / constraining 184 / modal_strong 19）

**操作**：
1. 邀请 1 位中文金融语言学专家
2. 审定 `config/lm_non_sentiment_dicts.json` v0.1.5 314 词词义对齐 ≥ 90%（G-A1.1 准入门控）
3. 扩词到 ~800-1200 词（注：modal_strong 中文表达比英文丰富, 可超 100%）
4. 与 bian_2021 (LM 中文本土化 sentiment 版) 团队对接 non-sentiment 扩展

**阻塞原因**：AI 不能担任学术词典审定者

**时长**：1 人·周（专家） + 0.5 人·周（标注员复核）

**成本**：取决于专家 day rate

---

### 🔴 L3.2 A2 FLS 词表 500 句人工标注

**现状**：v0.1.5 词表 131 词（future 72 + time 59）
**目标**：500 句人工标注上 precision ≥ 0.80（G-A2.1 准入门控）

**操作**：
1. 从 stage 13 (`13_news_with_ctx.parquet`) 随机抽 500 句 (用 jieba 已分句)
2. 标注员判断每句是否 forward-looking statement
3. 计算 `_is_fls_sentence()` 输出与人工标注的 precision/recall
4. 若 precision < 0.80 → 收紧双门控（要求 future 词与 time 词位置距离 ≤ 5 tokens）

**阻塞原因**：AI 不能担任人工标注 ground truth

**时长**：标注员 2-3 d

---

### 🔴 L3.3 D4 LLM CEO NER 200 篇 gold standard

**现状**：模块完整，但 200 篇 gold 不存在
**目标**：precision ≥ 0.85, recall ≥ 0.75（G-D4.1 准入门控）

**操作**：
1. 从 stage 13 随机抽 200 篇新闻
2. 标注员手工抽取每篇文章中的所有银行高管姓名+职位+提及次数
3. 跑 `python news_process/19_executive_ner.py` 输出 LLM NER 结果
4. 计算 precision/recall
5. 若 P < 0.7 → 降级规则版（正则 + 高管 alias 列表，基于 CSMAR 银行高管表）

**阻塞原因**：AI 不能担任人工标注 ground truth + yunwu API 调用预算

**时长**：标注员 2 h（标注） + LLM 12-24 h wall clock（400k articles）

**成本**：~$12 yunwu API（100% miss; LLMCache 命中后 $4-6）

---

### 🔴 L3.4 D1 BERTopic K 个 topic 中文命名

**现状**：模块完整，但 BERTopic 未跑（依赖 L2.1 启用 5 包）
**目标**：c-TF-IDF top-10 词 ≥ 80% 中文金融专家可解读（G-D1.2 准入门控）

**操作**：
1. 跑 `python news_process/17_article_topic.py`
2. 看 `data/processed/17_topic_metadata.json` 中 `topic_keywords_top10`
3. 中文金融专家审定每个 topic 的 top-10 keywords 是否构成可识别的 narrative
4. 给每个 topic 命名（如 "P2P 监管整顿" / "数字人民币试点" / "移动支付场景" 等）

**阻塞原因**：AI 不能担任中文金融专家解读

**时长**：0.5 人·周专家

---

## Layer 4 · 计算密集型操作（AI 不可完成）

### 🔴 L4.1 M0 panel 扩展（前置硬依赖）

**现状**：v3.7.0 panel 168 行（84 banks × 2 years, 2017-2018）
**目标**：~9000 行（500 banks × 18 years, 2007-2024）

**操作**：
1. 扩展 `bank_list.yaml` 至 ~500 银行（v3.7.0 已 frozen 39 行 + ~460 待补 M1）
2. 扩展 `data/raw/` 至 2007-2024 完整年份
3. 重跑 stage 00 → 51 全 pipeline
4. 验证 `40_panel_yearly.parquet` 行数 ≥ 1000

**阻塞原因**：
- AI 无 raw data 访问权限（Wind/CSMAR 商业数据 license）
- 计算 10-30 h CPU/GPU 时间

**阻塞下游**：D 组所有 paper-level power（G-A1.2 / G-C1.1 / G-D3.1 等）

**时长**：10-30 h（含数据获取）

---

### 🔴 L4.2 stage 30a article-level SBERT 持久化

**操作**：`python news_process/30a_article_sbert.py`

**资源**：
- 400k articles × 768 dim × float32 × 2 轨 = ~2.5 GB
- shibing624/text2vec-base-chinese (本机 HF cache 已有)
- GPU 2 h / CPU 4-6 h

**阻塞原因**：AI 不能跑长时计算任务

**阻塞下游**：D1 / D2.b semantic / D3（部分）

---

### 🔴 L4.3 D1 BERTopic 跑

**操作**：`python news_process/17_article_topic.py`（依赖 L2.1 + L4.2）

**资源**：UMAP + HDBSCAN，MP 64-core，4-6 h

**阻塞原因**：AI 不能跑长时计算 + 5 包未启用

---

### 🔴 L4.4 D2 staleness 跑

**操作**：`python news_process/18_article_staleness.py`

**资源**：
- Surface MinHash：5-15 min
- Semantic Faiss：30 min（依赖 L4.2 SBERT）

**阻塞原因**：依赖 L2.1 + L4.2

---

### 🔴 L4.5 D4 LLM CEO NER 跑

**操作**：`python news_process/19_executive_ner.py`

**资源**：
- 400k articles × ~0.3K tokens × $0.5/1M ≈ **$12 USD**（100% miss）
- 12-24 h wall clock

**阻塞原因**：
- yunwu API key 用户配置
- $12 预算批准
- 长时计算

---

### 🔴 L4.6 Stage 16 EPU merge 跑

**操作**：`python news_process/16_epu_merge.py`（依赖 L2.2 EPU CSV）

**资源**：5 min（轻量）

**阻塞原因**：依赖 L2.2

---

### 🔴 L4.7 Stage 39e/39f validation 跑

**操作**：
```powershell
python news_process/39e_lm_discriminant_validity.py  # 依赖 L4.1 + Stage 22 重跑
python news_process/39f_cross_media_alpha.py        # 依赖 L2.1 + L4.1
```

**资源**：每个 < 1 h

**阻塞原因**：依赖上游

---

## Layer 5 · 9 paper portfolio 集成（AI 部分可做）

### 🔴 L5.1 4 paper Stata ritest 启用 + 跑

**操作**：
```powershell
cd F:\WiseSearch\data_antigravity_project\news_process\papers
# 对每个 paper, instantiate template + 跑 Stata
python -m news_process.papers._common.stata_runner build-replication bank_fintech_locus
stata -b do papers/bank_fintech_locus/replication/code/18_locus_robustness.do
# 重复 substance / attention / collab
```

**资源**：MP 64-core, 4 paper × 17 min ≈ 1 h

**阻塞原因**：
- 依赖 L2.3 ritest 安装
- 依赖 L4.1 panel 扩展
- Stata 进程 AI 不能跑

---

### 🟡 L5.2 9 paper specs YAML 更新

**操作**：在 9 个 `paper_spec.yaml` 加 controls / robustness / tables 引用，含新 panel 列:
- A1 LM 4 列 → P3/P4/P5 tA7
- A2 FLS 2 列 → P1/P3 tA8
- C1 媒体 tier → 全 paper Table A8 sensitivity
- B1 EPU → 全 paper macro control
- D1/D2/D3/D4 → P10 + P11 + 各 mechanism

**阻塞原因**：
- 需 9 paper 作者协调 (P10/P11 是新立项)
- AI 可以生成 stub YAML，但 main treatment 选择需用户决策

**时长**：2-3 d (含协调)

**🟡 AI 可继续**：生成 YAML stub（一个 sample），但 9 个全做需用户/作者决策

---

### 🔴 L5.3 SSRN v2 update（已发布 paper）

**操作**：4 个已发布 SSRN paper 草稿加 robustness Tables A7/A8/A9，提交 v2

**阻塞原因**：SSRN 上传需作者账户 + DOI 协调

**时长**：1-2 周

---

### 🔴 L5.4 P10 narrative-novelty paper 立项

**操作**：
1. 创建 `papers/narrative_novelty/` 目录（仿 v3.7.0 bank_media_disagreement 结构）
2. 写 paper_spec.yaml + paper draft + Stata replication
3. 主方法 = D1 BERTopic + D2 staleness

**阻塞原因**：paper-writing 不可 AI 自动化（作者署名 + 学术判断）

**时长**：8-12 周

---

### 🔴 L5.5 P11 executive-media paper 立项

**操作**：类似 P10，主 treatment = D4 LLM CEO NER

**阻塞原因**：同 P10

**时长**：8-12 周

---

## Layer 6 · v3.7.0 协调（AI 不可完成）

### 🔴 L6.1 第 10 篇 `bank_media_disagreement` spec 对齐

**操作**：与第 10 篇作者协调:
- D3 `cross_media_alpha` 与 `cross_outlet_tone_variance_full` 重叠
- 决定: variance 作 main 还是 α 作 main? 或并行 robustness?

**阻塞原因**：跨 paper 作者协调

**时长**：1-2 d

---

### 🔴 L6.2 第 11 篇 `bank_news_clarity` 集成

**操作**：D2 staleness 可入 mechanism

**阻塞原因**：paper 作者协调

---

### 🟢 L6.3 DC3 LLM archive 集成 verify

**操作**：实跑 stage 19 (D4 LLM NER) 后 verify `archive_record` 真写入

**资源**：依赖 L4.5

**🟢 AI 可继续**：跑通后可写 functional test 验证 archive

---

## Layer 7 · 文档（AI 可做 / 已做）

### ✅ L7.1 CLAUDE.md +v2.3 段 — 本次 commit
### ✅ L7.2 sidecar JSON — 本次 commit
### ✅ L7.4 方法学文档 — 本次 commit

### 🟢 L7.3 5 paper paper_spec.yaml 加 tA7/tA8/tA10/tA11

**操作**：在 `papers/{bank_fintech_substance,locus,collab,benefit_society,P1}/paper_spec.yaml` 加 `tables.tA8` + `tA10` + `tA11` 引用

**🟢 AI 可继续**：YAML 改 ~30 行 / paper, 总 ~150 行

**时长**：1-2 h AI 工作

---

## Layer 8 · 精度提升（AI 可做 / 本次重新完成）

### ✅ L8.1 stage 39e permutation 100 → 1000 reps — 本次重做
### ✅ L8.3 LM 4 子词典 v0.1 → v0.1.5（314 词）— 本次重做
### ✅ L8.4 FLS 词表 v0.1 → v0.1.5（131 词）— 本次重做

---

## Layer 9 · 低优先级（AI 部分可做）

### 🔴 L9.1 data/external/README.md
状态：本地已写但 .gitignore 屏蔽（data/ 不进 git）
**阻塞原因**：.gitignore 设计

### 🟢 L9.2 paper README AI Disclosure D4 段
**🟢 AI 可继续**：等 L4.5 LLM NER 跑通后加 disclosure

### 🟢 L9.3 core_patterns 中 BERTopic K 个 frac_topic_k 列
**🟢 AI 可继续**：等 L4.3 BERTopic K 实测后补

---

## 总览表

| Layer | 项数 | AI 不可完成 (🔴) | AI 部分可做 (🟡) | AI 可继续 (🟢) | 已做 (✅) |
|---|---|---|---|---|---|
| 2 解锁 | 3 | 3 | 0 | 0 | 0 |
| 3 专家/标注 | 4 | 4 | 0 | 0 | 0 |
| 4 计算 | 7 | 7 | 0 | 0 | 0 |
| 5 paper portfolio | 5 | 4 | 1 | 0 | 0 |
| 6 v3.7.0 协调 | 3 | 2 | 0 | 1 | 0 |
| 7 文档 | 4 | 0 | 0 | 1 | 3 |
| 8 精度 | 3 | 0 | 0 | 0 | 3 |
| 9 低优先级 | 3 | 1 | 0 | 2 | 0 |
| **总计** | **32** | **21** | **1** | **4** | **6** |

## 关键里程碑

| 时间 | 里程碑 | 依赖 |
|---|---|---|
| **今天** | L7.1-7.4 + L8.1-8.4 完成 | ✅ 本次 |
| **本周** | L2.1-2.3 完成（pip + EPU + Stata）| 用户命令行 |
| **本月** | L4.6 (EPU 跑) + L3.1-3.4 准入门控 | 数据 + 专家 |
| **3 个月** | L4.1 M0 panel 扩展 + L4.2-4.5 各 stage 跑 | 计算 + Wind/CSMAR 数据 |
| **6 个月** | L5.1-5.3 9 paper 集成 + SSRN v2 | paper portfolio |
| **12 个月** | L5.4 + L5.5 (P10 + P11 立项) | 11 paper KPI 完成 |

---

**最后更新**: 2026-05-18 (第 17 轮 user-request 重建)
**关联文档**:
- `docs/methodology/v3_5_2_v2_3_supplementation_plan.md` (方法学补给)
- `config/v2_3_implementation_constants.json` (sidecar frozen 常量)
- `CLAUDE.md` "Current version" 段 (v3.7.0 + v2.3 描述)
