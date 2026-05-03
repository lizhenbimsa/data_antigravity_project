"""news_process.papers.brokerage_network — 衍生论文 2.

研究主题
--------
Brokerage-Network — 信息经纪网络与企业表现 (Information Brokerage Network).
衍生自 ``pipeline/panel/network_brokerage.py`` (原 47_panel_network_brokerage.py),
学术依据 Han, Jiang, Zhang & Zhu 2024 — 银行作为信息经纪人在共现网络中的中介性。

核心被解释变量
--------------
- ``brokerage_eigen_cent``       : 银行在共现网络中的特征向量中心性
- ``industry_neg_shock``         : 行业留一负面冲击
- ``brokerage_fire_sale``        : 中心性 × 负面冲击交互项
- ``peer_fintech_exposure_lag1`` : 同业金融科技暴露 (滞后 1 期)

非代码资产
----------
- ``papers_assets/brokerage_network/{do,output,drafts}/``
- TODO(Phase 3d): 关联 ``stata/network_causal.do`` 待归属确认后迁移
"""

from news_process.papers.brokerage_network import dag

PAPER_ID = 'brokerage_network'
__all__ = ['dag', 'PAPER_ID']
