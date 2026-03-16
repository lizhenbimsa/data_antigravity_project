# -*- coding: utf-8 -*-
"""
AutoPaper 生产基础设施 — 评审提示词模板引擎
==========================================
为不同评审模型生成定制化的评审提示词。
"""

# ============================================================
# 评审维度权重
# ============================================================

REVIEW_DIMENSIONS = {
    "research_question": {
        "name": "Research Question Quality",
        "weight": 0.15,
        "description": "Originality, significance, and clarity of the research question",
    },
    "identification": {
        "name": "Causal Identification",
        "weight": 0.25,
        "description": "Credibility of the identification strategy (DiD/RDD assumptions)",
    },
    "data_quality": {
        "name": "Data and Sample",
        "weight": 0.15,
        "description": "Data sources, sample selection, variable construction",
    },
    "statistical_analysis": {
        "name": "Statistical Analysis",
        "weight": 0.20,
        "description": "Correctness and comprehensiveness of the econometric analysis",
    },
    "writing_quality": {
        "name": "Writing Quality",
        "weight": 0.10,
        "description": "Clarity, structure, and academic writing standards",
    },
    "reproducibility": {
        "name": "Reproducibility",
        "weight": 0.15,
        "description": "Code completeness, documentation, and data accessibility",
    },
}


# ============================================================
# 评审报告格式模板
# ============================================================

REVIEW_OUTPUT_FORMAT = """
## 总体评价
- **建议：** [接受 / 小修 / 大修 / 拒稿]
- **总体评分：** X/10
- **信心度：** [高 / 中 / 低]

## 各维度评分
| 维度 | 评分（0-10） | 权重 | 加权得分 |
|------|-----------|------|---------|
| 研究问题 | X | 15% | X.XX |
| 因果识别 | X | 25% | X.XX |
| 数据与样本 | X | 15% | X.XX |
| 统计分析 | X | 20% | X.XX |
| 写作质量 | X | 10% | X.XX |
| 可复现性 | X | 15% | X.XX |
| **加权总分** | | | **X.XX** |

## 主要问题
1. [主要问题的详细描述，说明为什么重要]
2. [...]

## 次要问题
1. [详细描述]
2. [...]

## 对作者的问题
1. [关于方法或结果的具体问题]
2. [...]

## 具体建议
- [具体的改进建议]
- [...]

## JSON 汇总
```json
{
  "recommendation": "Accept|Minor Revision|Major Revision|Reject",
  "overall_score": X.X,
  "confidence": "High|Medium|Low",
  "dimension_scores": {
    "research_question": X,
    "identification": X,
    "data_quality": X,
    "statistical_analysis": X,
    "writing_quality": X,
    "reproducibility": X
  },
  "major_concerns_count": N,
  "minor_concerns_count": N
}
```
"""


# ============================================================
# 角色化评审提示词
# ============================================================

def build_review_prompt(
    paper_content: str,
    reviewer_persona: str = "general",
    review_round: int = 1,
) -> tuple[str, str]:
    """
    构建评审提示词。

    Args:
        paper_content: 论文 Markdown 内容
        reviewer_persona: 评审人角色 (general/methodologist/empiricist/code_reviewer)
        review_round: 评审轮次

    Returns:
        (system_prompt, user_prompt)
    """

    personas = {
        "general": {
            "role": "顶尖研究型大学的资深经济学家",
            "focus": "整体质量、学术贡献与政策相关性",
            "style": "平衡、建设性，但严格",
        },
        "methodologist": {
            "role": "专精因果推断的著名计量经济学家",
            "focus": (
                "识别策略、估计方法、"
                "假设可能违反（SUTVA、平行趋势、"
                "断点处的排序）"
            ),
            "style": "技术上精确严谨，对稳健性要求高",
        },
        "empiricist": {
            "role": "具有丰富政策评估经验的应用微观经济学家",
            "focus": (
                "数据质量、制度背景准确性、"
                "结果的实际意义、政策启示"
            ),
            "style": "实用、重视背景，关注经济幅度",
        },
        "code_reviewer": {
            "role": "计算社会科学家和可复现性专家",
            "focus": (
                "代码质量、可复现性、数据流水线正确性、"
                "统计实现错误"
            ),
            "style": "注重细节，专注于技术正确性",
        },
    }

    persona = personas.get(reviewer_persona, personas["general"])

    round_context = ""
    if review_round > 1:
        round_context = (
            f"\n\n这是第 {review_round} 轮评审。"
            f"请特别注意作者是否充分回应了上一轮的意见。"
        )

    system = (
        f"你是{persona['role']}，"
        f"受邀为一篇提交到顶级经济学期刊的论文撰写评审报告。"
        f"你的主要关注点是{persona['focus']}。"
        f"你的评审风格是{persona['style']}。"
        f"你必须全面、具体地提供可操作的反馈。请用中文回复所有内容。"
        f"{round_context}"
    )

    dimensions_desc = "\n".join(
        f"- **{d['name']}**（权重：{d['weight']*100:.0f}%）：{d['description']}"
        for d in REVIEW_DIMENSIONS.values()
    )

    prompt = f"""请对以下学术论文提供详细的同行评审意见。请用中文撰写所有评审内容。

=== 论文内容 ===
{paper_content}
=== 论文结束 ===

评审说明：
1. 仔细、批判性地阅读论文
2. 对下列每个维度进行评估
3. 针对每个问题提供具体、可操作的反馈
4. 对每个维度评分（0-10）
5. 给出整体建议

评估维度：
{dimensions_desc}

关键检查（请明确回答每项）：
- 预趋势是否真正平行（如果是 DiD）？
- 运行变量是否可操纵（如果是 RDD）？
- 结果对不同规格是否稳健？
- SUTVA 在该背景下是否合理？
- 幅度是否具有经济学意义？
- 是否存在可能导致偏误的遗漏变量？
- 代码是否足以支持复现？

输出格式：
{REVIEW_OUTPUT_FORMAT}

证审必须全面。走过场的评审比没有评审更差。"""

    return system, prompt


def build_code_review_prompt(
    code_content: str,
    research_plan: str,
) -> tuple[str, str]:
    """
    构建代码审查提示词。

    Args:
        code_content: Stata 代码内容
        research_plan: 研究计划内容

    Returns:
        tuple[str, str]: system, prompt
    """
    system = (
        "你是一位著名的 Stata 程序员和可复现性专家。"
        "你有十年的顶刊论文代码审查经验，对代码错误极其敏锐。"
    )

    prompt = f"""请对以下政策评估论文的 Stata 分析代码进行审查。请用中文撰写评审报告。

你的任务是：
1. 识别代码中的任何统计方法或逻辑错误
2. 检查变量变换、固定效应、标准误聚类是否规范
3. 检查代码的结构、注释和可读性
4. 验证是否符合前沿计量经济学实践（如多期 DiD 的异质性处理）

研究计划：
{research_plan}

Stata 代码：
```stata
{code_content}
```

审查清单：
1. **数据完整性**：是否对 NA、异常值、样本限制进行了适当处理？
2. **估计正确性**：
   - 固定效应是否正确设定？
   - 标准误是否在正确层级上堆算？
   - 处理变量是否正确构造？
   - 交错 DiD 估计量是否正确使用？
3. **稳健性**：是否实现了安慰剂检验、替代结果变量和子组分析？
4. **可复现性**：
   - 所有路径是否为相对路径？
   - 是否设置了随机种子？
   - 是否记录了包版本？
5. **输出**：结果是否以可复现的格式保存？

对于发现的每个问题，请指定：
- 文件和行号（近似）
- 严重程度（严重 / 警告 / 建议）
- 修复代码建议

请输出结构化的评审报告（用中文）。"""

    return system, prompt
