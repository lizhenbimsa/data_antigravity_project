# AI Use Disclosure Templates (Plan E P2 / N3 Closure)

> **Context**: 单作者 + 11 paper portfolio (8 fully-coded + 3 provisional). 治理已解锁 (No SSRN preprint, 数据授权,
> 无共同作者). 所有 paper 在投稿前必须在 manuscript 中加入相应期刊系列的 AI
> disclosure 段落. 本文件为统一模板.

## 1. Nature / Science 系列 (e.g., Nature Human Behaviour)

**位置**: Methods section 末尾, "Code & Data Availability" 之前.

```
AI Use Disclosure

The author used Anthropic Claude (code assistant), a three-family
LLM ensemble for sentiment annotation (OpenAI gpt-5.4-nano; Google
gemini-3.1-flash-lite; DeepSeek deepseek-v4-flash; majority vote),
and two co-primary text-embedding APIs (Alibaba Qwen3-Embedding-8B,
4096-d, via SiliconFlow; OpenAI text-embedding-3-large, 3072-d)
during this work in the following capacities:
  (a) Code generation and refactoring for the news_process pipeline
      (https://github.com/[REPO]).
  (b) Sentiment classification at the article × bank level
      (entity-attributed tone using llm_vote_tone_{full,ctx,ss}).
  (c) Semantic-similarity measurement (embedding-based features,
      reported in cross-vendor dual-track parallel as mutual
      robustness).
  (d) Manuscript drafting and language editing.

All analyses, interpretations, and final manuscript text were
reviewed, verified, and approved by the author. The author bears
full responsibility for all content. Prompt versions and LLM
invocation logs are preserved in the replication package
(prompt sources in config/prompts/ + _llm_cache.db).
```

## 2. AER / AEJ / Econometrica 系列

**位置**: Acknowledgments section (在 footnote 之前).

```
The author acknowledges the use of Anthropic Claude (code
generation), a three-family LLM ensemble (OpenAI / Google /
DeepSeek) for sentiment annotation, and Alibaba Qwen3-Embedding-8B
plus OpenAI text-embedding-3-large (co-primary dual-track) for
semantic measurement, as well as AI assistance in manuscript
preparation. All outputs were independently verified. Per AEA
guidelines (2024+),
the replication package preserves all LLM prompts, model versions,
and cache databases enabling exact reproduction.
```

## 3. JF / RFS / JFE / JFQA (Finance)

**位置**: First-page footnote.

```
* I thank [seminar/conference] participants for comments. AI tools
(Anthropic Claude for code drafting; an OpenAI/Google/DeepSeek LLM
ensemble for sentiment measurement; Alibaba Qwen3-Embedding-8B and
OpenAI text-embedding-3-large co-primary embeddings for semantic
measurement) were used at the firm-day level; full prompt versions
and cache logs are in the replication archive. The author is
responsible for any errors.
```

## 4. ASQ / AMJ / SMJ / Organization Science

**位置**: Methods 末尾 (在 Robustness checks 之前).

```
Researcher-AI collaboration: The author employed Anthropic Claude
for code generation, a three-family LLM ensemble (OpenAI gpt-5.4-nano,
Google gemini-3.1-flash-lite, DeepSeek deepseek-v4-flash; majority
vote) for sentiment annotation, and two co-primary embedding models
(Alibaba Qwen3-Embedding-8B via SiliconFlow; OpenAI
text-embedding-3-large) for semantic similarity measurement,
reported side by side as mutual robustness. All theoretical framing, hypothesis
development, and interpretation are the author's own. The use of AI
follows the ASQ / AMJ AI policy (effective [date]). Reproducibility
materials including LLM prompt sources (config/prompts/), cache databases
(_llm_cache.db), and version manifests (the prompt_v8_sha256 key in
data/processed/v3_5_1_constants.json) are deposited at [DOI / repository].
Fingerprint convention: prompt_v8_sha256 refers to the SHA-256 of the
raw on-disk prompt bytes (CRLF, 0430ba3c…); the cache-key layer consumes
the LF-normalized in-memory text (SHA-256 14952b06…) — any replication
of either fingerprint must state which of the two conventions it uses.
Wording-sensitivity and criterion-validity results are disclosed together
with the sample/corpus scope on which they were computed (production
T=18 corpus vs. development pilot), per the evidence-class discipline in
scripts/audit/M0_PRODUCTION_GATE_CHECKLIST.md.
```

<!-- fix(S14 + WP-R5.4, 2026-07-14): 指纹双口径声明 (计划 §0-3) + 敏感性/效标
     结果须随样本口径披露 (计划 WP-R5.4)。sidecar 自 M1 起位于 config output_dir,
     经 .gitignore negation 例外保持 git 跟踪 (M1-P0); sha 锚另有 runtime producer
     每次 panel build 实算兜底。 -->

## 5. Research Policy

**位置**: Methods §3 末尾.

```
AI Use: Anthropic Claude assisted with code refactoring of the
panel-construction pipeline. Article-level policy alignment is
computed via cosine similarity per Distel, Grimpe & Poetz (2026, RP
§3.2.1) using two co-primary embedding models reported in parallel
as mutual robustness (Alibaba Qwen3-Embedding-8B, 4096-d, via
SiliconFlow; OpenAI text-embedding-3-large, 3072-d); following
Hassan et al. (2019) entity-proximity, alignment is computed on both
full-article and entity-localized (target-bank) windows. Embedding
inputs deliberately carry no instruction prefix: all similarity tasks
in this project are symmetric (document-to-document / document-to-
anchor), whereas the Qwen3-Embedding instruction prefix targets
asymmetric retrieval (query-to-document); the prefix-free text is
also the frozen cache-key corpus, so retrofitting a prefix would
invalidate the embedding cache and the golden reproducibility anchor.
All embeddings, prompts, and caches are preserved in the replication
archive.
```

<!-- fix(D2, 2026-07-14): 零 instruct 前缀两句话依据 (对称任务 + 前缀已冻结为
     缓存键语料) — manuscript 数据附录经本模板单点落地; 同款声明见 CLAUDE.md
     嵌入架构段与 SWAP_GEMINI_TO_QWEN3 计划 §0。 -->

## 6. CSSCI / 中文期刊 (经济研究 / 管理世界 / 金融研究 / 经济学(季刊))

**位置**: 致谢 (Acknowledgments) 段.

```
作者在本研究中使用了三类 AI 工具: Anthropic Claude (代码生成与重构);
三家大语言模型多数投票集成 (OpenAI gpt-5.4-nano、Google
gemini-3.1-flash-lite、DeepSeek deepseek-v4-flash) 用于新闻情感标注;
以及两个互为稳健性、不分主次的文本嵌入模型 (阿里 Qwen3-Embedding-8B,
4096 维, 经硅基流动 API; OpenAI text-embedding-3-large, 3072 维)
用于文本语义相似度计算. 所有分析、解读与最终文本均由作者审核确认,
文责自负. 复制包 (replication package) 包含完整的 LLM 调用日志、
prompt 版本与缓存数据库, 支持方法学审计与结果重现.
```

## 替换 Token 列表

每篇 paper 投稿前替换:
- `[REPO]`        — GitHub 仓库地址或私有 SHA
- `[DOI / repository]` — Replication archive DOI
- `[seminar/conference]` — 实际致谢的会议/同行
- `[date]`        — 期刊 AI policy 生效日期 (查官网)

## 期刊政策核对清单 (投稿前 1 周完成)

| 期刊 | AI policy 链接 | 最后更新 | 模板版本 |
|---|---|---|---|
| Nature 系列 | https://www.nature.com/nature-portfolio/editorial-policies/ai | 查 |  §1 |
| AER | https://www.aeaweb.org/journals/policies/policies-on-data-and-code | 2024 | §2 |
| JF | https://onlinelibrary.wiley.com/page/journal/15406261/homepage/ForAuthors.html | 查 | §3 |
| ASQ | https://journals.sagepub.com/author-instructions/ASQ | 查 | §4 |
| RP | https://www.elsevier.com/journals/research-policy/0048-7333/guide-for-authors | 查 | §5 |
| 经济研究 | http://www.erj.cn/cn/instructions.aspx | 查 | §6 |

## 与 Plan E 的关系

- 单作者 (Plan E §0 表 0-1 N2 解锁) → 无需 co-author 多签字
- No SSRN preprint (N8 解锁) → AI 披露版本与正式投稿一致, 无 pre-reg 冲突
- 数据授权 (N1 解锁) → "Data Availability" 段可声明 "available upon request"
- LLM 调用日志保留 (P-1 F1 cache 隔离已确认) → reproducibility 段可指向 _llm_cache.db
