"""
utils/canonicalization.py - 金融科技主题标准化分类(增强版)
=====================================================

将 LLM 自由文本输出的 fintech_topic 标准化分类为二选一:
    - 底层技术: 大数据、云计算、人工智能、区块链、物联网等
    - 应用场景: 数字支付、智能风控、智能客服、数字信贷、数字营销等

分类策略(三轮决策):
  第 1 轮: 加权关键词匹配(最长匹配优先, 取得分较高者为最终分类)
  第 2 轮: fuzzywuzzy 模糊匹配(匹配度 >= 60, 置信度打 0.7 折扣)
  第 3 轮: 兜底默认归为"应用场景"(基率更高), 置信度 0.0

增强特性:
    - 加权关键词评分(核心词 2.0, 长词 1.0, 短词 0.5)
    - 分类置信度(0.0~1.0)
    - 全角/大小写归一化
    - fuzzywuzzy 模糊匹配兜底
"""

import logging

logger = logging.getLogger(__name__)

# ============================================================================
# 文本归一化
# ============================================================================

def _normalize_text(text: str) -> str:
    """统一全角→半角、大小写，去除多余空白。"""
    # 全角→半角
    result = []
    for ch in text:
        code = ord(ch)
        # 全角空格
        if code == 0x3000:
            result.append(' ')
        # 全角 ASCII 字符 (！→~)
        elif 0xFF01 <= code <= 0xFF5E:
            result.append(chr(code - 0xFEE0))
        else:
            result.append(ch)
    normalized = ''.join(result)
    # 大写统一
    normalized = normalized.upper()
    # 去除多余空白
    normalized = ' '.join(normalized.split())
    return normalized


# ============================================================================
# 标准化分类关键词表(加权)
# 格式: (关键词, 权重)
# 权重设计依据:
#   2.0 - 核心标志词: 明确指向某一类别的标志性术语, 如"人工智能"、"数字支付"
#   1.5 - 第二梯队: 较强指示, 但可能跨类, 如"神经网络"、"反欺诈"
#   1.0 - 普通长词: 有指示性但较广泛, 如"AI"、"数据分析"
#   0.5 - 短词/易误匹配: 可能在多种语境中出现, 如"加密"、"合规"、"API"
# ============================================================================

# 底层技术关键词
TECHNOLOGY_KEYWORDS = [
    # 人工智能
    ("人工智能", 2.0),
    ("AI",       1.0),
    ("机器学习", 2.0),
    ("深度学习", 2.0),
    ("自然语言处理", 2.0),
    ("NLP",      1.0),
    ("计算机视觉", 2.0),
    ("神经网络", 1.5),
    ("大模型",   1.5),
    ("生成式AI", 2.0),
    ("语音识别", 1.5),
    ("多模态",   1.0),
    # 大数据
    ("大数据",   2.0),
    ("数据挖掘", 1.5),
    ("数据分析", 1.0),
    ("数据治理", 1.5),
    ("数据中台", 1.5),
    ("数据湖",   1.5),
    ("数据仓库", 1.5),
    ("大数据平台", 2.0),
    # 云计算
    ("云计算",   2.0),
    ("云原生",   1.5),
    ("分布式",   1.0),
    ("微服务",   1.0),
    ("容器化",   1.0),
    ("私有云",   1.5),
    ("公有云",   1.5),
    ("混合云",   1.5),
    ("容灾",     1.0),
    ("双活",     1.0),
    ("异地多活", 1.5),
    # 区块链
    ("区块链",   2.0),
    ("分布式账本", 2.0),
    ("智能合约", 1.5),
    ("加密",     0.5),
    ("通证",     1.0),
    ("比特币",   1.0),
    ("以太坊",   1.0),
    # 物联网
    ("物联网",   2.0),
    ("IOT",      1.0),
    ("传感器",   1.0),
    ("边缘计算", 1.5),
    # 其他底层技术
    ("5G",       1.0),
    ("量子计算", 2.0),
    ("隐私计算", 1.5),
    ("联邦学习", 1.5),
    ("知识图谱", 1.5),
    ("RPA",      1.0),
    ("机器人流程自动化", 2.0),
    ("生物识别", 1.5),
    ("OCR",      1.0),
    ("光学字符识别", 1.5),
    ("API",      0.5),
    ("开放接口", 1.0),
    ("DEVOPS",   1.0),
    ("自动化测试", 1.0),
    ("低代码",   1.0),
    ("无代码",   1.0),
    ("中间件",   1.0),
    ("分布式数据库", 1.5),
    ("图数据库", 1.0),
    ("数据安全", 1.0),
    ("网络安全", 1.5),
    ("零信任",   1.5),
    ("数字身份", 1.0),
]

# 应用场景关键词
APPLICATION_KEYWORDS = [
    # 支付
    ("数字支付", 2.0),
    ("移动支付", 2.0),
    ("电子支付", 1.5),
    ("扫码支付", 1.5),
    ("跨境支付", 1.5),
    ("聚合支付", 1.5),
    ("条码支付", 1.5),
    ("NFC支付",  1.5),
    # 数字货币 — 从底层技术移至应用场景
    ("数字货币", 1.5),
    ("央行数字货币", 2.0),
    ("DCEP",     1.5),
    ("数字人民币", 2.0),
    # 风控
    ("智能风控", 2.0),
    ("风险管理", 1.0),
    ("反欺诈",   1.5),
    ("反洗钱",   1.5),
    ("征信",     1.0),
    ("信用评估", 1.5),
    ("风险评估", 1.0),
    ("合规",     0.5),
    ("监管科技", 2.0),
    # 信贷
    ("数字信贷", 2.0),
    ("智能信贷", 2.0),
    ("在线贷款", 1.5),
    ("消费金融", 1.5),
    ("供应链金融", 2.0),
    ("小微贷款", 1.0),
    ("普惠金融", 1.5),
    # 客服与营销
    ("智能客服", 2.0),
    ("智能营销", 2.0),
    ("数字营销", 1.5),
    ("精准营销", 1.5),
    ("智能推荐", 1.5),
    ("客户画像", 1.5),
    ("用户画像", 1.5),
    ("千人千面", 1.5),
    # 银行数字化业务
    ("数字银行", 2.0),
    ("手机银行", 1.5),
    ("网上银行", 1.5),
    ("远程银行", 1.5),
    ("开放银行", 2.0),
    ("直销银行", 1.5),
    ("智慧网点", 1.5),
    ("无人银行", 1.5),
    # 理财与投资
    ("智能投顾", 2.0),
    ("智能理财", 2.0),
    ("数字财富管理", 2.0),
    ("量化投资", 1.5),
    ("财富管理", 1.0),
    ("私人银行", 1.0),
    # 保险科技
    ("保险科技", 2.0),
    ("智能核保", 1.5),
    ("智能理赔", 1.5),
    # 数字化转型
    ("数字化转型", 2.0),
    ("数字化",   0.5),
    ("数据资产", 1.5),
    ("场景金融", 2.0),
    ("嵌入式金融", 2.0),
    # 绿色/ESG 金融
    ("绿色金融", 2.0),
    ("碳金融",   1.5),
    ("ESG",      1.0),
    # 其他应用场景
    ("养老金融", 1.5),
    ("乡村振兴", 1.0),
    ("资产证券化", 1.5),
    ("ABS",      0.5),
    ("数字孪生", 1.5),
    ("智慧城市", 1.5),
    ("智慧政务", 1.5),
]

# 预构建归一化后的关键词查找表
# 在模块加载时一次性将所有关键词转为大写, 避免每次调用时重复转换
_TECH_NORMALIZED = [(kw.upper(), weight) for kw, weight in TECHNOLOGY_KEYWORDS]
_APP_NORMALIZED  = [(kw.upper(), weight) for kw, weight in APPLICATION_KEYWORDS]


def canonicalize_topic(raw_topic: str) -> tuple:
    """将 LLM 输出的 fintech_topic 标准化分类。

    增强版：支持加权评分和分类置信度。同时涉及两类时，选择得分更高的一方。

    Args:
        raw_topic: LLM 返回的自由文本主题描述

    Returns:
        tuple: (category, confidence)
            - category: "底层技术" 或 "应用场景"
            - confidence: 0.0~1.0 之间的分类置信度
    """
    if not raw_topic or raw_topic.strip().lower() in ('null', 'none', ''):
        return ("应用场景", 0.0)

    text = _normalize_text(raw_topic)

    # 第一轮：加权关键词匹配（最长匹配优先，避免子串重复计分）
    def _match_keywords(keywords, text):
        """最长匹配优先的关键词匹配, 返回加权总分。

        策略: 关键词按长度降序排序, 长词优先匹配。
        已被长词占据的字符位置不会被短词重复计分。
        例如: 如果匹配了"人工智能"(权重 2.0), 则子串"人工"不再计分。
        """
        score = 0.0
        matched_positions: set[int] = set()  # 记录已被匹配占据的字符位置
        # 关键词按长度降序排列(长词优先)
        sorted_kws = sorted(keywords, key=lambda x: len(x[0]), reverse=True)
        for kw, weight in sorted_kws:
            start = 0
            while True:
                pos = text.find(kw, start)
                if pos == -1:
                    break
                positions = set(range(pos, pos + len(kw)))
                if not positions & matched_positions:  # 无重叠才计分
                    score += weight
                    matched_positions |= positions  # 标记这些位置已被占据
                start = pos + 1
        return score

    tech_score = _match_keywords(_TECH_NORMALIZED, text)
    app_score = _match_keywords(_APP_NORMALIZED, text)

    # 第 1 轮结果评估: 取得分较高的一方为最终分类
    total_score = tech_score + app_score

    if total_score > 0:
        if tech_score >= app_score:
            # 置信度 = 胜出方得分 / 总分, 上限 1.0
            # 当 tech_score 远大于 app_score 时, 置信度接近 1.0
            # 当两者接近时, 置信度接近 0.5(表示不确定)
            confidence = min(tech_score / max(total_score, 1.0), 1.0)
            return ("底层技术", round(confidence, 3))
        else:
            confidence = min(app_score / max(total_score, 1.0), 1.0)
            return ("应用场景", round(confidence, 3))

    # 第二轮：模糊匹配(仅当第 1 轮得分为 0 时触发)
    # 使用 fuzzywuzzy 的 partial_token_set_ratio:
    #   - partial: 支持子串匹配(输入可能包含额外文字)
    #   - token_set: 对词语集合比较, 容忍词序差异
    try:
        from fuzzywuzzy import fuzz

        best_tech_score = 0
        for kw, weight in _TECH_NORMALIZED:
            score = fuzz.partial_token_set_ratio(text, kw)
            if score > best_tech_score:
                best_tech_score = score

        best_app_score = 0
        for kw, weight in _APP_NORMALIZED:
            score = fuzz.partial_token_set_ratio(text, kw)
            if score > best_app_score:
                best_app_score = score

        # 匹配度阈值 60: 低于此值认为匹配不可靠, 进入兜底
        if best_tech_score >= 60 and best_tech_score >= best_app_score:
            # 模糊匹配的置信度打 0.7 折扣, 反映其不确定性高于精确匹配
            confidence = best_tech_score / 100.0 * 0.7
            return ("底层技术", round(confidence, 3))
        elif best_app_score >= 60:
            confidence = best_app_score / 100.0 * 0.7
            return ("应用场景", round(confidence, 3))
    except ImportError:
        logger.warning("fuzzywuzzy 未安装，跳过模糊匹配")

    # 第 3 轮: 兜底默认 -- 归为应用场景, 置信度 0.0(表示完全不确定)
    # 设计决策: 默认应用场景而非底层技术, 因为在金融新闻语境中,
    # "应用场景"是更常见的类别(基率更高)
    return ("应用场景", 0.0)
