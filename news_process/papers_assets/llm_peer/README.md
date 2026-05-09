# Paper: `llm_peer` — LLM-Peer Competition Network IV

**Status (2026-05-09 / Plan-r3 P1-5)**: 骨架占位 — 代码包 `news_process/papers/llm_peer/` 已存在
（Phase 3c 落地的 5 paper 之一），但本资产目录 `papers_assets/llm_peer/` 直到本 commit 才补齐。
此前 `paper_config.py:_VALID_PAPER_IDS` 含 `llm_peer` 但 `papers_assets/` 下无对应目录，导致
`get_paper_config('llm_peer')` 返回的 `do_dir` / `output_dir` / `drafts_dir` 指向不存在的路径，
违反了与其它 4 个 paper 的目录契约一致性。

## 主题

LLM-Peer (Cao et al. 2025, RAS) 同业竞争网络 IV：用 LLM 判定的语义同业关系（vs 传统 SIC 行业代码）
构造 leave-one-out 工具变量，估计同业语调溢出对银行 fintech 战略响应的因果效应。

## 与 pipeline 的对应关系

| 子模块 | 行数 | 责任 |
|---|---|---|
| `news_process.pipeline.panel.llm_peer_iv` | 714 | 计算 `llm_peer_tone_iv_full` / `llm_peer_count` / `peer_compete_idx` 等 panel 列 |
| `news_process.papers.llm_peer.analysis` | 57 | CLI 入口 (与其它 4 paper analysis.py 同模板) |
| `news_process.papers.llm_peer.tables` | 58 | Table 1 描述统计 (骨架) |
| `news_process.papers.llm_peer.figures` | 51 | Figure 1 (骨架) |

## 资产目录约定

```
papers_assets/llm_peer/
├── README.md          ← 本文件 (paper 主题 + 状态说明)
├── do/                ← Stata .do 脚本 (主回归 / 机制 / 异质性 / 稳健性)
│   └── .gitkeep       ← 当前为空; v3.0 会补主回归 do
├── output/            ← .gitignored — 运行时按需 mkdir
└── drafts/            ← .gitignored — manuscript .tex / .docx
```

## v3.0 待办

1. 补 `do/main_regression.do` — 用 `llm_peer_tone_iv_full` 跑主 IV 回归（双向固定效应 + 集群标准误）
2. 扩 `papers/llm_peer/tables.py` — 加 Table 2 (主回归)、Table 3 (机制)、Table 4 (稳健性)
3. 扩 `papers/llm_peer/figures.py` — 加 Figure 2 (network 可视化)
4. 起草 `drafts/manuscript.tex`

## 不要做的事

- ❌ 不要从 `_VALID_PAPER_IDS` 中删除 `llm_peer` —— 代码包已存在，删除会让 5 个测试 collection
  失败。
- ❌ 不要在没有补 main_regression.do 之前跑 `python -m news_process.papers.llm_peer.analysis
  --stage tables` 的输出当作正式结果引用 —— Table 1 仅是 summary stats 占位。
