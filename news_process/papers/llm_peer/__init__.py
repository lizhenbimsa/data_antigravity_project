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
- ``papers_assets/llm_peer/{do,output,drafts}/``
- TODO(Phase 3d): .do 文件待迁移 (主线 stata/ 暂未确认归属此论文的 .do)
"""

from news_process.papers.llm_peer import dag

PAPER_ID = 'llm_peer'
__all__ = ['dag', 'PAPER_ID']
