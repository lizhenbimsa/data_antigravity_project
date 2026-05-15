"""news_process.papers.llm_peer — 衍生论文 3.

研究主题
--------
LLM-Peer — 基于大语言模型构造的同业竞争 IV (LLM-Generated Peer Competition IV).
衍生自 ``pipeline/panel/llm_peer_iv.py`` (原 48_panel_llm_peer_iv.py),
学术依据 Cao, Li, Wang & Zhao 2025 — *Can Generative AI Help Identify Peer Firms?*

核心变量
--------
- ``llm_peer_tone_iv_full`` : LLM 生成的同业语调 IV (主回归)
- ``llm_peer_count``         : LLM 同业数量
- ``peer_compete_idx``       : 同业竞争强度指数
- 多阈值敏感性: cutoff = {0.70, 0.75, 0.80, 0.85, 0.90} 各 4 套变量

非代码资产
----------
- ``papers_assets/llm_peer/{do,output,drafts/{en,zh}}/`` (P0 目录契约 + P4 双语手稿)
- ``papers_assets/llm_peer/README.md`` (paper 主题 + 状态说明)

P0-P4 落地状态 (commit 8d33c46, 2026-05-15)
--------------------------------------------
- **Stata 模板** (8 .do.tmpl):
  ``_common/stata_templates/llm_peer/{00_master, 01_data_prep,
  10_table1_descriptives, 11_table2_main_iv_2sls,
  12_table3_cutoff_sensitivity, 13_table4_heterogeneity,
  14_table5_robustness, 30_figure1_first_stage_F}.do.tmpl``
  + README.md.
- **Python tables**: build_table1 (描述统计) + build_table2_main / build_table3_cutoff /
  build_table4_heterogeneity / build_table5_robustness (读 Stata esttab CSV).
- **Python figures**: plot_cutoff_sensitivity (Figure 1) +
  plot_main_iv_coefplot (Figure 2) + plot_heterogeneity_forest (Figure 3).
- **Manuscripts**: ``papers_assets/llm_peer/drafts/{en,zh}/manuscript.tex``
  (8 节标准结构 + V6 F1-F4 方法学声明) + refs.bib.
- **复现包**: ``python -c "from news_process.papers._common.derivative_replication
  import build_derivative_replication_package as b; b('llm_peer')"`` 一键生成.

仍待用户补充 (manuscript 内容)
------------------------------
- 各 manuscript 内 ``\\NoteThis{...}`` 占位 (Intro / Lit / Results 等)
- BibLaTeX 文献库扩展 (当前 ~6 条共享 + 2 条 LLM-Peer 专属)
"""

PAPER_ID = 'llm_peer'
__all__ = ['PAPER_ID']
