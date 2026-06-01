"""news_process.pipeline.sentiment — Stages 21/22/23/24: tone analysis.

- llm_tone (21): three-model LLM ensemble + verification
- lexicon_tone (22): five Chinese finance dictionaries
- bert_tone (23): three fine-tuned BERT models (finbert_cn / fin_sent_zh / finbert2)
- herd_decay (24): Tetlock 2011 herd-weighting on 23's output
"""
