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
- ``papers_assets/llm_peer/{do,output,drafts}/`` (Plan-r3 P1-5 刚补齐目录契约)
- Phase 4a 审计: ``stata/`` 5 个原始 .do 文件均归属其它 4 篇论文; 本论文目前
  无独立 .do, 论文级回归预计在后续手稿写作阶段补齐。

骨架性提示 (Plan-r3 P1-6)
--------------------------
本 paper 是 5 paper 中最不成熟的一个. tables.py 仅含 Table 1 描述统计;
figures.py 仅含 Figure 1 分布图; do/ 为空 (.gitkeep). v3.0 计划补齐:
1. main_regression.do  -- 用 llm_peer_tone_iv_full 跑 IV 双向 FE 回归
2. tables.py 扩 Table 2 (主回归) / Table 3 (机制) / Table 4 (稳健性)
3. figures.py 扩 Figure 2 (network 可视化)
4. drafts/manuscript.tex
"""

PAPER_ID = 'llm_peer'
__all__ = ['PAPER_ID']
