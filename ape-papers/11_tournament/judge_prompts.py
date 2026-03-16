# -*- coding: utf-8 -*-
"""
APEP 生产基础设施 — 裁判比较提示词
==========================================
为竞赛系统的头对头比较生成裁判提示词。
"""

import re
import json
from typing import Optional


def build_judge_prompt(
    paper_a_content: str,
    paper_b_content: str,
) -> tuple[str, str]:
    """
    构建裁判比较提示词。

    注意: 论文标签为 "Paper A" 和 "Paper B"，
    不暴露论文 ID，实现双盲比较。

    Args:
        paper_a_content: 论文 A 内容
        paper_b_content: 论文 B 内容

    Returns:
        (system_prompt, user_prompt)
    """
    system = (
        "You are a senior economist serving as a judge in an academic paper "
        "comparison tournament. You must evaluate two papers and determine "
        "which one is of higher quality. Be fair, systematic, and rigorous. "
        "Your evaluation should reflect the standards of top-5 economics journals "
        "(AER, QJE, Econometrica, JPE, REStud)."
    )

    prompt = f"""Compare the following two academic papers and determine which 
is of higher quality. This is a blind comparison — do not try to identify the 
authors or source.

=== PAPER A ===
{paper_a_content}
=== END PAPER A ===

=== PAPER B ===
{paper_b_content}
=== END PAPER B ===

EVALUATION CRITERIA (score each 0-10):

1. **Research Question** (15%): 
   - Originality and significance
   - Clear framing of the causal question

2. **Identification Strategy** (25%):
   - Credibility of causal claims
   - Proper use of DiD/RDD methodology
   - Discussion of threats to identification

3. **Data Quality** (15%):
   - Appropriate data sources
   - Sample selection justification
   - Variable construction

4. **Analysis Rigor** (20%):
   - Correct statistical implementation
   - Robustness and sensitivity analysis
   - Event study / pre-trends

5. **Writing & Presentation** (10%):
   - Clarity and structure
   - Professional quality
   - Proper citations

6. **Contribution & Impact** (15%):
   - Policy relevance
   - Advancement of knowledge
   - Practical significance of findings

INSTRUCTIONS:
1. Score each paper on each criterion (0-10)
2. Compute weighted total for each paper
3. Declare a winner or tie
4. Explain your reasoning

OUTPUT FORMAT (strict JSON at the end):
```json
{{
  "paper_a_scores": {{
    "research_question": X,
    "identification": X,
    "data_quality": X,
    "analysis_rigor": X,
    "writing": X,
    "contribution": X,
    "total_weighted": X.XX
  }},
  "paper_b_scores": {{
    "research_question": X,
    "identification": X,
    "data_quality": X,
    "analysis_rigor": X,
    "writing": X,
    "contribution": X,
    "total_weighted": X.XX
  }},
  "winner": "paper_a" | "paper_b" | "draw",
  "confidence": "high" | "medium" | "low",
  "margin": "decisive" | "narrow" | "negligible",
  "key_differentiator": "what made the difference",
  "reasoning": "brief explanation"
}}
```

Be decisive. Only declare a draw if the papers are truly indistinguishable."""

    return system, prompt


def parse_judge_verdict(
    verdict_text: str,
    swapped: bool = False,
) -> dict:
    """
    解析裁判的判定结果。

    Args:
        verdict_text: 裁判输出文本
        swapped: 是否交换了展示顺序（双盲处理）

    Returns:
        解析后的判定 dict
    """
    result = {
        "winner": "draw",
        "confidence": "medium",
        "margin": "negligible",
        "paper_a_total": 0.0,
        "paper_b_total": 0.0,
        "key_differentiator": "",
        "raw_text": verdict_text[:500],
    }

    # 尝试从 JSON 块解析
    json_match = re.search(
        r'```json\s*\n(\{[^`]+\})\s*\n```',
        verdict_text, re.DOTALL
    )
    if json_match:
        try:
            data = json.loads(json_match.group(1))
            result["winner"] = data.get("winner", "draw")
            result["confidence"] = data.get("confidence", "medium")
            result["margin"] = data.get("margin", "negligible")
            result["key_differentiator"] = data.get("key_differentiator", "")

            a_scores = data.get("paper_a_scores", {})
            b_scores = data.get("paper_b_scores", {})
            result["paper_a_total"] = a_scores.get("total_weighted", 0)
            result["paper_b_total"] = b_scores.get("total_weighted", 0)
            result["paper_a_scores"] = a_scores
            result["paper_b_scores"] = b_scores

        except json.JSONDecodeError:
            pass

    # Fallback: 文本解析
    if result["winner"] == "draw" and result["paper_a_total"] == 0:
        text_lower = verdict_text.lower()
        if "paper a" in text_lower and "wins" in text_lower:
            result["winner"] = "paper_a"
        elif "paper b" in text_lower and "wins" in text_lower:
            result["winner"] = "paper_b"
        elif "paper a is superior" in text_lower:
            result["winner"] = "paper_a"
        elif "paper b is superior" in text_lower:
            result["winner"] = "paper_b"

    # 处理双盲交换
    if swapped:
        if result["winner"] == "paper_a":
            result["winner"] = "paper_b"
        elif result["winner"] == "paper_b":
            result["winner"] = "paper_a"

        # 交换分数
        result["paper_a_total"], result["paper_b_total"] = (
            result["paper_b_total"], result["paper_a_total"]
        )
        if "paper_a_scores" in result and "paper_b_scores" in result:
            result["paper_a_scores"], result["paper_b_scores"] = (
                result["paper_b_scores"], result["paper_a_scores"]
            )

    return result


# ============================================================
# 自测
# ============================================================

if __name__ == "__main__":
    # 测试提示词生成
    system, prompt = build_judge_prompt(
        "Paper A: Studies the effect of minimum wage on employment using DiD...",
        "Paper B: Examines the impact of clean slate laws on labor outcomes using RDD...",
    )
    print(f"System prompt length: {len(system)}")
    print(f"User prompt length: {len(prompt)}")

    # 测试判定解析
    mock_verdict = """
Based on my analysis, Paper B shows stronger identification.

```json
{
  "paper_a_scores": {
    "research_question": 7,
    "identification": 6,
    "data_quality": 7,
    "analysis_rigor": 6,
    "writing": 7,
    "contribution": 6,
    "total_weighted": 6.45
  },
  "paper_b_scores": {
    "research_question": 8,
    "identification": 8,
    "data_quality": 7,
    "analysis_rigor": 8,
    "writing": 7,
    "contribution": 7,
    "total_weighted": 7.55
  },
  "winner": "paper_b",
  "confidence": "high",
  "margin": "narrow",
  "key_differentiator": "Superior identification strategy",
  "reasoning": "Paper B has a more convincing RDD design."
}
```
"""

    verdict = parse_judge_verdict(mock_verdict, swapped=False)
    print(f"\n判定结果: {json.dumps(verdict, indent=2, ensure_ascii=False)}")
    assert verdict["winner"] == "paper_b", "解析错误"

    # 测试交换
    verdict_swapped = parse_judge_verdict(mock_verdict, swapped=True)
    assert verdict_swapped["winner"] == "paper_a", "交换逻辑错误"
    print("✅ 所有测试通过")
