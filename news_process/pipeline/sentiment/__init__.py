"""news_process.pipeline.sentiment — Stage 21/22/23/24: 情感/语调分析.

- llm_tone (21): 三模型 LLM 集成投票 + 验证
- lexicon_tone (22): 六部中文金融情感词典 (含 Loughran-McDonald 2011 JF 中文主译本)
- bert_tone (23): 三个微调 BERT 模型 (finbert_cn / fin_sent_zh / finbert2)
- herd_decay (24): 对 stage 23 输出施加 Tetlock 2011 跟风衰减加权
"""
