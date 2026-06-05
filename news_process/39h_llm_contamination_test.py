"""Thin shim → news_process.pipeline.audit.llm_contamination_test.

Stage 39h: DC4 LLM 训练数据污染留出检验 (Fisher z + permutation + Bayes factor).
两篇 provisional 论文 (bank_news_clarity / bank_media_disagreement) frozen spec 的
DC4 必修项 (F-Adv.2); 2026-06-05 补 shim+注册接线。

opt-in 默认禁用 (config/validation.yaml::validation.llm_contamination=false): 需
opt-in stage 49 的 z_score outcome + 用户在 config 提供官方 LLM cutoff (禁止伪造);
缺数据/未配 cutoff 时 run_stage 优雅跳过。≤30 行 thin shim 不变式。
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from news_process.pipeline.audit.llm_contamination_test import run_stage  # noqa: E402

if __name__ == "__main__":
    run_stage()
