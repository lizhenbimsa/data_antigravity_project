"""
fintech_rating_example.py — 金融科技新闻多维度连续评分示例

基于 GABRIEL gabriel.rate 的设计范式:
  - 0-100 连续整数评分（非三分类）
  - 多属性独立评分 + 均值聚合
  - 多轮 (n_runs) 独立重复 → 取均值降噪

本模块展示两种使用方式:
  A) 直接使用 GABRIEL 库 (pip install openai-gabriel)
  B) 不依赖 GABRIEL，复用现有管线基础设施

属性设计学术依据:
  - 情感倾向: Lopez-Lira & Tang (2023, SSRN 4412788)
  - 创新深度: Li et al. (2021, The Review of Financial Studies — Measuring corporate culture using machine learning)
  - 战略前瞻: 姜富伟等 (2024, 管理世界)
  - 实质关联: Carlson & Burbano (2026, SMJ §3.3)
"""

# ============================================================================
# 属性定义（核心配置）
# ============================================================================

FINTECH_RATING_ATTRIBUTES = {
    "情感倾向": (
        "该新闻对目标银行金融科技业务的情感倾向。"
        "0=极度负面（严重风险暴露、重大监管处罚、系统性安全事故），"
        "50=完全中性（客观事实陈述、无褒贬），"
        "100=极度正面（重大技术突破、里程碑式业绩增长、行业标杆认可）。"
        "注意：仅评估新闻文本传递的情感信号，不得基于银行身份做先验推断。"
    ),
    "创新深度": (
        "新闻所涉金融科技创新的技术深度和实质性程度。"
        "0=无任何技术内容（纯行政通知或人事变动），"
        "30=浅层应用提及（如'引入AI'但无技术细节），"
        "60=具体技术方案描述（如算法名称、架构设计、性能指标），"
        "100=底层核心技术突破（如自研大模型、专利技术、行业标准制定）。"
    ),

    "实质关联度": (
        "目标银行与金融科技主题之间的实质关联强度。"
        "0=无关联（银行仅在来源标注或免责声明中出现），"
        "30=边缘关联（银行在宏观行业综述中被泛泛提及），"
        "60=中度关联（银行是具体金融科技事件的参与方之一），"
        "100=核心关联（银行是金融科技行动的主体发起者和直接执行者）。"
    ),
    "信息密度": (
        "文章中金融科技相关有效信息的密度。"
        "0=金融科技信息为零（纯噪音或无关内容），"
        "50=金融科技内容与其他内容各占一半，"
        "100=全文聚焦金融科技，几乎每句都含实质技术或业务信息。"
    ),
}


# ============================================================================
# 方式 A: 使用 GABRIEL 库（最简方式）
# ============================================================================

async def rate_with_gabriel(df, content_column="内容"):
    """使用 GABRIEL 库进行金融科技多维度评分。

    前提: pip install openai-gabriel
          设置 OPENAI_API_KEY 环境变量

    Args:
        df: 含新闻文本的 DataFrame
        content_column: 文本列名

    Returns:
        pd.DataFrame: 原 DataFrame + 5 个评分列 (0-100)
    """
    import gabriel

    results = await gabriel.rate(
        df,
        column_name=content_column,
        attributes=FINTECH_RATING_ATTRIBUTES,
        save_dir="./gabriel_runs/fintech_rating",
        model="gpt-5.4-mini",
        n_runs=3,              # 3 轮独立评分 → 取均值降噪
        modality="text",
        reset_files=False,     # 支持断点续传
        additional_instructions=(
            "聚焦目标银行在金融科技领域的表现。"
            "忽略同文提及的其他银行的相关信号。"
            "每个属性必须严格独立评分，禁止交叉推断。"
        ),
    )
    return results


# ============================================================================
# 方式 B: 不依赖 GABRIEL，复用现有管线基础设施
# ============================================================================

def build_rating_prompt(
    title: str,
    content: str,
    target_bank: str,
    co_mentioned_banks: str = "无",
    attributes: dict = None,
) -> str:
    """构建评分 Prompt（纯 Python 字符串格式化，无需 Jinja2）。

    遵循 GABRIEL 的核心设计原则:
      1. 属性独立性约束
      2. 0-100 连续评分标准
      3. 抗交叉推断规则
      4. 证据驱动要求

    Args:
        title: 新闻标题
        content: 新闻正文
        target_bank: 目标分析银行
        co_mentioned_banks: 同文提及的其他银行
        attributes: 评分属性字典，默认使用 FINTECH_RATING_ATTRIBUTES

    Returns:
        str: 完整的评分 Prompt
    """
    if attributes is None:
        attributes = FINTECH_RATING_ATTRIBUTES

    # 构建属性列表
    attr_block = "\n".join(
        f"• {name}: {desc}" for name, desc in attributes.items()
    )

    # 构建输出 JSON schema
    json_fields = ",\n".join(
        f'  "{name}": <0-100 整数>' for name in attributes.keys()
    )

    prompt = f"""你是一名资深金融科技研究分析师，精通银行数字化转型与中文财经文本计量分析。
请对以下新闻内容的每个属性进行独立评分。

═══════════════════ 输入数据 ═══════════════════
目标分析银行: {target_bank}
同文提及的其他银行（仅供参考，不作为评分对象）: {co_mentioned_banks}
标题: {title}
正文: {content}
═══════════════════════════════════════════════

═══════════════════ 评分属性 ═══════════════════
{attr_block}
═══════════════════════════════════════════════

═══════════════════ 评分标准 ═══════════════════
使用 0-100 整数（含端点）进行评分:
  0-10   = 完全不存在 / 完全不符合
  11-30  = 微弱 / 边缘提及
  31-50  = 适中 / 客观陈述
  51-70  = 较明显 / 有一定倾向
  71-90  = 强烈 / 证据充分
  91-100 = 极端 / 压倒性证据

要求:
- 使用全范围的每一个增量，不要取整到 5 或 10 的倍数
- 极端值（<5 或 >95）应极其罕见，仅在证据压倒性时使用
- 优先使用中间值（如 23, 47, 64, 78）以精确反映细微差异
═══════════════════════════════════════════════

═══════════════════ 核心规则 ═══════════════════
1.【属性独立性】每个属性必须完全独立评分，严禁属性间交叉推断
   ✗ 错误: 因为"创新深度"高就推断"情感倾向"为正面
   ✓ 正确: 仅基于该属性本身的直接文本证据评分

2.【实体聚焦】仅评估新闻对【{target_bank}】的相关信号
   同文提及的 {co_mentioned_banks} 的利好或负面一律视为噪音，
   不得影响对目标银行的任何属性评分

3.【证据驱动】每项评分必须基于文本中的直接、具体证据
   不得基于对银行的先验知识或刻板印象进行推断

4.【高精度要求】需要对内容进行深入、全面的分析
   每个属性都需要仔细考量，不允许草率给出默认中间值
═══════════════════════════════════════════════

严格输出以下 JSON，禁止添加前缀、后缀或 Markdown 包裹:
{{
{json_fields}
}}

请评估以上全部 {len(attributes)} 个属性，不允许遗漏。"""

    return prompt


def parse_rating_response(response_text: str, attributes: dict = None) -> dict:
    """解析评分 JSON 响应。

    Args:
        response_text: LLM 返回的原始文本
        attributes: 属性字典，用于校验字段完整性

    Returns:
        dict: {属性名: 分数(float)} — 解析失败的属性值为 None
    """
    import json

    if attributes is None:
        attributes = FINTECH_RATING_ATTRIBUTES

    # 去除 markdown 代码块包围
    text = response_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]

    try:
        parsed = json.loads(text.strip())
    except json.JSONDecodeError:
        return {attr: None for attr in attributes}

    result = {}
    for attr in attributes:
        raw_val = parsed.get(attr)
        if raw_val is not None:
            try:
                val = float(raw_val)
                # 强制截断到 [0, 100] 范围
                result[attr] = max(0.0, min(100.0, val))
            except (ValueError, TypeError):
                result[attr] = None
        else:
            result[attr] = None

    return result


def aggregate_multi_run_ratings(all_runs: list) -> dict:
    """多轮评分均值聚合（GABRIEL 核心聚合策略）。

    Args:
        all_runs: [{"情感倾向": 62, "创新深度": 45, ...}, ...] 每轮的评分结果

    Returns:
        dict: {属性名: 均值分数} — 忽略 None 值
    """
    from collections import defaultdict

    scores = defaultdict(list)
    for run in all_runs:
        for attr, val in run.items():
            if val is not None:
                scores[attr].append(val)

    return {
        attr: round(sum(vals) / len(vals), 2) if vals else None
        for attr, vals in scores.items()
    }


# ============================================================================
# 使用示例
# ============================================================================

if __name__ == "__main__":
    # 示例: 构建 prompt 并展示
    prompt = build_rating_prompt(
        title="工商银行发布自研金融大模型 实现核心风控算法突破",
        content="近日，中国工商银行正式发布自主研发的金融大模型...",
        target_bank="中国工商银行",
        co_mentioned_banks="建设银行;农业银行",
    )
    print(prompt)
    print("\n" + "=" * 60)

    # 示例: 解析响应
    fake_response = '{"情感倾向": 78, "创新深度": 85, "实质关联度": 93, "信息密度": 71}'
    parsed = parse_rating_response(fake_response)
    print(f"\n解析结果: {parsed}")

    # 示例: 多轮聚合
    runs = [
        {"情感倾向": 78, "创新深度": 85, "实质关联度": 93, "信息密度": 71},
        {"情感倾向": 74, "创新深度": 82, "实质关联度": 91, "信息密度": 68},
        {"情感倾向": 76, "创新深度": 87, "实质关联度": 90, "信息密度": 73},
    ]
    aggregated = aggregate_multi_run_ratings(runs)
    print(f"\n3轮均值聚合: {aggregated}")
