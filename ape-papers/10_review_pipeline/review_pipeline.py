# -*- coding: utf-8 -*-
"""
APEP 生产基础设施 — 评审流水线
==========================================
并行调度多个 LLM 评审模型，收集评审报告，
触发聚合决策。
"""

import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "09_agent_framework"))

from config import REVIEW_MODELS, REVIEW_THRESHOLDS, setup_logging
from llm_client import create_client, LLMResponse
from review_prompts import build_review_prompt, build_code_review_prompt
from review_aggregator import ReviewAggregator

logger = setup_logging("apep.review")


# ============================================================
# 评审模型 ↔ 角色映射
# ============================================================

MODEL_PERSONA_MAP = {
    "gpt-review":      "methodologist",      # 方法论专家
    "grok-review":     "empiricist",          # 实证经济学家
    "deepseek-review": "general",             # 综合评审
    "gemini-review":   "code_reviewer",       # 代码审查
}

MODEL_FILE_PREFIX = {
    "gpt-review":      "review_gpt",
    "grok-review":     "review_grok",
    "deepseek-review": "review_deepseek",
    "gemini-review":   "review_gemini",
}


class ReviewPipeline:
    """
    多模型同行评审流水线。

    并行调用所有配置的评审模型，收集评审报告，
    运行聚合器做出 Accept/Revision/Reject 决策。
    """

    def __init__(
        self,
        paper_dir: Path | str,
        review_round: int = 1,
        max_workers: int = 4,
    ):
        self.paper_dir = Path(paper_dir)
        self.review_round = review_round
        self.max_workers = max_workers
        self.aggregator = ReviewAggregator()

    def run_review(
        self,
        model_keys: Optional[list[str]] = None,
    ) -> dict:
        """
        执行完整的评审流程。

        Args:
            model_keys: 要使用的评审模型 key 列表（默认使用全部）

        Returns:
            聚合决策结果 dict
        """
        if model_keys is None:
            model_keys = list(REVIEW_MODELS.keys())

        # 1. 读取论文内容
        paper_content = self._read_paper()
        if not paper_content:
            return {"status": "error", "reason": "无法读取论文内容"}

        # 2. 读取代码内容（用于代码审查）
        code_content = self._read_code()
        plan_content = self._read_plan()

        logger.info(f"🔬 启动评审流水线 (Round {self.review_round})")
        logger.info(f"   评审模型: {model_keys}")
        logger.info(f"   论文长度: {len(paper_content)} 字符")

        # 3. 并行调度评审
        reviews = {}
        t0 = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for model_key in model_keys:
                if model_key not in REVIEW_MODELS:
                    logger.warning(f"⚠️ 跳过未知模型: {model_key}")
                    continue

                persona = MODEL_PERSONA_MAP.get(model_key, "general")

                # 代码审查用专门的提示词
                if persona == "code_reviewer" and code_content:
                    system, prompt = build_code_review_prompt(
                        code_content, plan_content
                    )
                else:
                    system, prompt = build_review_prompt(
                        paper_content, persona, self.review_round
                    )

                future = executor.submit(
                    self._single_review,
                    model_key, system, prompt,
                )
                futures[future] = model_key

            for future in as_completed(futures):
                model_key = futures[future]
                try:
                    review_result = future.result()
                    reviews[model_key] = review_result

                    # 保存评审报告到文件
                    self._save_review(model_key, review_result)

                    logger.info(
                        f"✅ [{model_key}] 评审完成 "
                        f"({review_result.output_tokens} tokens)"
                    )
                except Exception as e:
                    logger.error(f"❌ [{model_key}] 评审失败: {e}")
                    reviews[model_key] = None

        duration = time.time() - t0
        logger.info(f"⏱️  所有评审完成 ({duration:.1f}s)")

        # 4. 聚合决策
        successful_reviews = {
            k: v for k, v in reviews.items() if v is not None
        }

        if len(successful_reviews) < REVIEW_THRESHOLDS.min_reviewers:
            logger.warning(
                f"⚠️ 成功评审数不足 "
                f"({len(successful_reviews)}/{REVIEW_THRESHOLDS.min_reviewers})"
            )

        decision = self.aggregator.aggregate(
            {k: v.content for k, v in successful_reviews.items()},
            self.paper_dir,
        )

        # 5. 保存聚合结果
        decision_file = self.paper_dir / f"review_decision_round_{self.review_round}.json"
        decision_file.write_text(
            json.dumps(decision, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        logger.info(f"📋 评审决策: {decision.get('recommendation', 'N/A')}")
        logger.info(f"   加权总分: {decision.get('weighted_score', 'N/A')}")

        return decision

    def _single_review(
        self, model_key: str, system: str, prompt: str
    ) -> LLMResponse:
        """执行单个模型的评审"""
        config = REVIEW_MODELS[model_key]
        with create_client(config) as client:
            return client.generate(
                prompt=prompt,
                system=system,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
            )

    def _save_review(self, model_key: str, response: LLMResponse):
        """保存评审报告到文件"""
        prefix = MODEL_FILE_PREFIX.get(model_key, f"review_{model_key}")
        filename = f"{prefix}_{self.review_round}.md"
        filepath = self.paper_dir / filename
        filepath.write_text(response.content, encoding="utf-8")
        logger.info(f"📄 评审报告已保存: {filename}")

    def _read_paper(self) -> str:
        """读取论文内容"""
        tex_file = self.paper_dir / "paper.tex"
        if tex_file.exists():
            return tex_file.read_text(encoding="utf-8")
        logger.warning("⚠️ paper.tex 不存在")
        return ""

    def _read_code(self) -> str:
        """读取所有 R 代码"""
        code_dir = self.paper_dir / "code"
        if not code_dir.exists():
            return ""
        parts = []
        for r_file in sorted(code_dir.glob("*.R")):
            parts.append(f"# === {r_file.name} ===\n")
            parts.append(r_file.read_text(encoding="utf-8", errors="ignore"))
            parts.append("\n\n")
        return "".join(parts)

    def _read_plan(self) -> str:
        """读取研究计划"""
        plan_file = self.paper_dir / "research_plan.md"
        if plan_file.exists():
            return plan_file.read_text(encoding="utf-8")
        return ""


# ============================================================
# CLI 入口
# ============================================================

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="APEP 评审流水线")
    parser.add_argument("paper_dir", help="论文目录路径")
    parser.add_argument("--round", type=int, default=1, help="评审轮次")
    parser.add_argument("--models", nargs="*", default=None,
                        help="评审模型 keys（默认全部）")

    args = parser.parse_args()

    pipeline = ReviewPipeline(
        paper_dir=args.paper_dir,
        review_round=args.round,
    )

    result = pipeline.run_review(model_keys=args.models)

    print("\n" + "=" * 50)
    print(f"评审决策: {result.get('recommendation', 'N/A')}")
    print(f"加权总分: {result.get('weighted_score', 'N/A')}")
    print("=" * 50)
