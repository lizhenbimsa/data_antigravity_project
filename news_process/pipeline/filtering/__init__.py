"""news_process.pipeline.filtering — 阶段 11/12/14/15: 领域过滤.

- news_bank (11): 银行名称关键词过滤
- news_fintech (12): fintech 关键词过滤 (full 全量 + filtered 子集双输出)
- fintech_intensity (14): TF-IDF + IDF 加权关键词向量质心的连续强度评分
  (fix omni-g-fintech-02: 非 SIF 实现, 详见该模块 docstring)
- policy_alignment (15): 文章级政策语义对齐
  (复用 pipeline.panel.encode 的 CONFIG/logger; Phase 2a 已移除旧 importlib 反射)
- news_salience (非独立 stage): 新闻体裁显著性测度族, 由 stage 11 (news_bank)
  物化为 article 级列, 经 encode 聚合到 bank-year
"""
