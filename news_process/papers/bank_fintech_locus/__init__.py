"""news_process.papers.bank_fintech_locus — P4 B-route paper.

研究主题
--------
Bank Fintech Locus — 银行 fintech 公告的"底层技术 (区块链 / AI / 云)"vs
"应用场景 (支付 / 信贷 / 理财)"locus 区分, 检验差异化市场反应与创新产出.

锚定文献:
    - Gomber, Kauffman, Parker, Weber (2018) JMIS — fintech taxonomy (technology vs business function)
    - Kogan, Papanikolaou, Seru, Stoffman (2017) QJE — innovation market-value 度量
    - Goldstein, Jiang, Karolyi (2019) RFS — fintech special issue editorial

核心被解释变量:
- ``car_5day_window``        : event-window 5-day CAR (primary)
- ``patent_fintech_count``   : IncoPat fintech 专利计数
- ``citation_weighted_patent``: Kogan 2017 market-value 加权专利

核心处理变量 (primary_pair; fix(omni-g-papers-misc-05/-11, 2026-06-11)
实际推导 = Stata 01_data_prep.do 从 panel 列 tech_frac/app_frac 主导类别二元化,
非文章级 innovation_locus_full 字符串):
- ``locus_layer_full``       : 1 if tech_frac > app_frac (R35-M02 derived, Stata 层)
- ``locus_scenario_full``    : 1 if app_frac > tech_frac (R35-M02 derived, Stata 层)
- ``locus_gap``              : locus_layer - locus_scenario ∈ {-1, 0, +1}
                               (0 = 平票 tech_frac == app_frac, 含两者皆 0; 作参照组)

Mediator (R7-M04):
- ``capex_it``                : CSMAR 资本支出 IT 板块
- ``r_and_d_intensity``       : 国家专利局衍生 R&D investment intensity

Heterogeneity wave (R4-M03 三波严格对称):
    pre_period (2007-2012) / wave_1 (2013-2015) /
    wave_2 (2016-2018) / consolidation (2019-2021) / wave_3 (2022-2024).

Spec: ``papers/bank_fintech_locus/paper_spec.yaml`` (M0 G0 frozen).
"""

PAPER_ID = 'bank_fintech_locus'
__all__ = ['PAPER_ID']
