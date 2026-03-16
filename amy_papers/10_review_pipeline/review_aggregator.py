# -*- coding: utf-8 -*-
"""
AutoPaper 生产基础设施 — 评审结果聚合器
==========================================
解析各模型评审报告中的结构化评分，
加权汇总后做出 Accept / Revision / Reject 决策。
"""

import re
import json
from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "09_agent_framework"))

from config import REVIEW_THRESHOLDS, setup_logging
from review_prompts import REVIEW_DIMENSIONS

logger = setup_logging("paper.aggregator")


class ReviewAggregator:
    """
    评审结果聚合器。

    从多个评审报告中提取结构化评分，
    计算加权总分，并根据阈值做出决策。
    """

    def __init__(self, thresholds=None):
        self.thresholds = thresholds or REVIEW_THRESHOLDS

    def aggregate(
        self,
        reviews: dict[str, str],
        paper_dir: Optional[Path] = None,
    ) -> dict:
        """
        聚合多个评审结果。

        Args:
            reviews: {model_key: review_content} 字典
            paper_dir: 论文目录（用于保存聚合报告）

        Returns:
            聚合结果 dict
        """
        parsed_reviews = {}
        for model_key, content in reviews.items():
            parsed = self._parse_review(content, model_key)
            if parsed:
                parsed_reviews[model_key] = parsed

        if not parsed_reviews:
            logger.warning("⚠️ 无法从任何评审报告中提取结构化评分")
            return {
                "status": "error",
                "reason": "无法解析评审报告",
                "recommendation": "Manual Review Required",
            }

        # 计算各维度的平均分
        avg_scores = self._average_scores(parsed_reviews)

        # 计算加权总分
        weighted_score = self._weighted_score(avg_scores)

        # 做出决策
        recommendation = self._decide(weighted_score)

        # 汇总各模型的建议
        model_recommendations = {
            k: v.get("recommendation", "Unknown")
            for k, v in parsed_reviews.items()
        }

        result = {
            "status": "ok",
            "weighted_score": round(weighted_score, 2),
            "recommendation": recommendation,
            "average_dimension_scores": avg_scores,
            "model_recommendations": model_recommendations,
            "individual_scores": {
                k: v.get("dimension_scores", {})
                for k, v in parsed_reviews.items()
            },
            "num_reviewers": len(parsed_reviews),
            "consensus": self._check_consensus(model_recommendations),
        }

        logger.info(f"📊 聚合结果:")
        logger.info(f"   加权总分: {weighted_score:.2f}/10")
        logger.info(f"   决策: {recommendation}")
        logger.info(f"   共识度: {result['consensus']}")

        return result

    def _parse_review(self, content: str, model_key: str) -> Optional[dict]:
        """
        从评审报告中提取结构化数据。

        尝试两种方式:
        1. 从 JSON 块中解析
        2. 从 Markdown 表格中解析
        """
        result = {"model": model_key}

        # 方式 1: 从 JSON Summary 块中提取
        json_match = re.search(
            r'```json\s*\n(\{[^`]+\})\s*\n```',
            content, re.DOTALL
        )
        if json_match:
            try:
                json_data = json.loads(json_match.group(1))
                result["recommendation"] = json_data.get("recommendation", "Unknown")
                result["overall_score"] = json_data.get("overall_score", 0)
                result["confidence"] = json_data.get("confidence", "Medium")
                result["dimension_scores"] = json_data.get("dimension_scores", {})
                result["major_concerns_count"] = json_data.get("major_concerns_count", 0)
                result["minor_concerns_count"] = json_data.get("minor_concerns_count", 0)
                logger.info(f"  ✅ [{model_key}] JSON 解析成功")
                return result
            except json.JSONDecodeError:
                logger.warning(f"  ⚠️ [{model_key}] JSON 解析失败，尝试表格解析")

        # 方式 2: 从 Markdown 表格提取维度评分
        # 匹配形如 "| Research Question | 7 | 15% | 1.05 |" 的行
        dimension_patterns = {
            "research_question": r"Research Question.*?\|\s*(\d+(?:\.\d+)?)\s*\|",
            "identification": r"(?:Causal )?Identification.*?\|\s*(\d+(?:\.\d+)?)\s*\|",
            "data_quality": r"Data.*?Sample.*?\|\s*(\d+(?:\.\d+)?)\s*\|",
            "statistical_analysis": r"Statistical Analysis.*?\|\s*(\d+(?:\.\d+)?)\s*\|",
            "writing_quality": r"Writing Quality.*?\|\s*(\d+(?:\.\d+)?)\s*\|",
            "reproducibility": r"Reproducibility.*?\|\s*(\d+(?:\.\d+)?)\s*\|",
        }

        scores = {}
        for dim_key, pattern in dimension_patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                scores[dim_key] = float(match.group(1))

        if scores:
            result["dimension_scores"] = scores
            result["overall_score"] = sum(scores.values()) / len(scores)
        else:
            # 方式 3: 尝试提取 "Overall Score: X/10"
            overall_match = re.search(
                r"Overall Score.*?(\d+(?:\.\d+)?)\s*/\s*10",
                content, re.IGNORECASE
            )
            if overall_match:
                result["overall_score"] = float(overall_match.group(1))
            else:
                logger.warning(f"  ⚠️ [{model_key}] 无法提取任何评分")
                return None

        # 提取推荐
        rec_match = re.search(
            r"Recommendation.*?:\s*(Accept|Minor Revision|Major Revision|Reject)",
            content, re.IGNORECASE
        )
        result["recommendation"] = rec_match.group(1) if rec_match else "Unknown"

        # 统计问题数量
        major = len(re.findall(r"##\s*Major Concern", content, re.IGNORECASE))
        minor = len(re.findall(r"##\s*Minor Concern", content, re.IGNORECASE))
        result["major_concerns_count"] = major or content.lower().count("major concern")
        result["minor_concerns_count"] = minor or content.lower().count("minor concern")

        logger.info(f"  ✅ [{model_key}] 表格/文本解析成功 (score={result['overall_score']:.1f})")
        return result

    def _average_scores(self, parsed_reviews: dict) -> dict:
        """计算各维度的平均分"""
        all_dims = set()
        for review in parsed_reviews.values():
            all_dims.update(review.get("dimension_scores", {}).keys())

        avg = {}
        for dim in all_dims:
            scores = [
                review["dimension_scores"][dim]
                for review in parsed_reviews.values()
                if dim in review.get("dimension_scores", {})
            ]
            if scores:
                avg[dim] = round(sum(scores) / len(scores), 2)

        return avg

    def _weighted_score(self, avg_scores: dict) -> float:
        """计算加权总分"""
        total = 0.0
        total_weight = 0.0

        for dim_key, dim_info in REVIEW_DIMENSIONS.items():
            if dim_key in avg_scores:
                total += avg_scores[dim_key] * dim_info["weight"]
                total_weight += dim_info["weight"]

        if total_weight == 0:
            # Fallback: 使用所有可用分数的简单平均
            if avg_scores:
                return sum(avg_scores.values()) / len(avg_scores)
            return 0.0

        return total / total_weight

    def _decide(self, weighted_score: float) -> str:
        """根据阈值做出决策"""
        t = self.thresholds
        if weighted_score >= t.accept_threshold:
            return "Accept"
        elif weighted_score >= t.minor_revision_threshold:
            return "Minor Revision"
        elif weighted_score >= t.major_revision_threshold:
            return "Major Revision"
        else:
            return "Reject"

    def _check_consensus(self, recommendations: dict) -> str:
        """
        检查评审共识度。

        Returns:
            "unanimous" / "majority" / "split"
        """
        if not recommendations:
            return "no_data"

        recs = list(recommendations.values())
        unique = set(recs)

        if len(unique) == 1:
            return "unanimous"

        # 检查是否有多数意见
        from collections import Counter
        counts = Counter(recs)
        most_common_count = counts.most_common(1)[0][1]

        if most_common_count > len(recs) / 2:
            return "majority"
        else:
            return "split"


# ============================================================
# 自测
# ============================================================

if __name__ == "__main__":
    # 模拟评审报告
    mock_review = """
## Overall Assessment
- **Recommendation**: Minor Revision
- **Overall Score**: 7/10
- **Confidence**: High

## Dimension Scores
| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Research Question | 8 | 15% | 1.20 |
| Causal Identification | 6 | 25% | 1.50 |
| Data & Sample | 7 | 15% | 1.05 |
| Statistical Analysis | 7 | 20% | 1.40 |
| Writing Quality | 8 | 10% | 0.80 |
| Reproducibility | 7 | 15% | 1.05 |

## Major Concerns
1. Pre-trends are not convincingly parallel.

## Minor Concerns
1. Some typos in Section 4.

```json
{
  "recommendation": "Minor Revision",
  "overall_score": 7.0,
  "confidence": "High",
  "dimension_scores": {
    "research_question": 8,
    "identification": 6,
    "data_quality": 7,
    "statistical_analysis": 7,
    "writing_quality": 8,
    "reproducibility": 7
  },
  "major_concerns_count": 1,
  "minor_concerns_count": 1
}
```
"""

    agg = ReviewAggregator()
    result = agg.aggregate({
        "gpt-5-mini": mock_review,
        "grok-4.1-fast": mock_review.replace("7/10", "8/10").replace('"overall_score": 7.0', '"overall_score": 8.0'),
    })

    print("\n聚合结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
