"""
utils/canonicalization.py — 金融科技主题标准化分类
=====================================================

将 LLM 自由文本输出的 fintech_topic 标准化为两大类：
    - 底层技术：大数据、云计算、人工智能、区块链、物联网等
    - 应用场景：数字支付、智能风控、智能客服、数字信贷、数字营销等

方法：
    1. 关键词匹配（高效，零成本）
    2. fuzzywuzzy 模糊匹配（兜底）
"""

import logging

logger = logging.getLogger(__name__)

# ============================================================================
# 标准化分类关键词表
# ============================================================================

# 底层技术关键词
TECHNOLOGY_KEYWORDS = [
    # 人工智能
    "人工智能", "AI", "机器学习", "深度学习", "自然语言处理", "NLP",
    "计算机视觉", "神经网络", "大模型", "生成式AI", "语音识别",
    # 大数据
    "大数据", "数据挖掘", "数据分析", "数据治理", "数据中台",
    # 云计算
    "云计算", "云原生", "分布式", "微服务", "容器化", "私有云", "公有云", "混合云",
    # 区块链
    "区块链", "分布式账本", "智能合约", "数字货币", "央行数字货币", "DCEP",
    "数字人民币", "加密", "通证", "比特币", "以太坊",
    # 物联网
    "物联网", "IoT", "传感器", "边缘计算",
    # 其他底层技术
    "5G", "量子计算", "隐私计算", "联邦学习", "知识图谱", "RPA",
    "机器人流程自动化", "生物识别", "OCR", "API", "开放接口",
]

# 应用场景关键词
APPLICATION_KEYWORDS = [
    # 支付
    "数字支付", "移动支付", "电子支付", "扫码支付", "跨境支付",
    "聚合支付", "条码支付", "NFC支付",
    # 风控
    "智能风控", "风险管理", "反欺诈", "反洗钱", "征信",
    "信用评估", "风险评估", "合规", "监管科技",
    # 信贷
    "数字信贷", "智能信贷", "在线贷款", "消费金融", "供应链金融",
    "小微贷款", "普惠金融",
    # 客服与营销
    "智能客服", "智能营销", "数字营销", "精准营销", "智能推荐",
    "客户画像", "用户画像", "千人千面",
    # 银行数字化业务
    "数字银行", "手机银行", "网上银行", "远程银行", "开放银行",
    "直销银行", "智慧网点", "无人银行",
    # 理财与投资
    "智能投顾", "智能理财", "数字财富管理", "量化投资",
    # 保险科技
    "保险科技", "智能核保", "智能理赔",
]


def canonicalize_topic(raw_topic: str) -> str:
    """将 LLM 输出的 fintech_topic 标准化为「底层技术」或「应用场景」。
    
    Args:
        raw_topic: LLM 返回的自由文本主题描述
        
    Returns:
        "底层技术" 或 "应用场景"
    """
    if not raw_topic or raw_topic.strip().lower() in ('null', 'none', ''):
        return "应用场景"  # 默认归为应用场景
    
    text = raw_topic.strip()
    
    # 第一轮：精确关键词匹配
    tech_score = sum(1 for kw in TECHNOLOGY_KEYWORDS if kw in text)
    app_score = sum(1 for kw in APPLICATION_KEYWORDS if kw in text)
    
    if tech_score > 0 or app_score > 0:
        return "底层技术" if tech_score > app_score else "应用场景"
    
    # 第二轮：模糊匹配
    try:
        from fuzzywuzzy import fuzz
        
        best_tech_score = max(
            (fuzz.partial_token_set_ratio(text, kw) for kw in TECHNOLOGY_KEYWORDS),
            default=0
        )
        best_app_score = max(
            (fuzz.partial_token_set_ratio(text, kw) for kw in APPLICATION_KEYWORDS),
            default=0
        )
        
        if best_tech_score > best_app_score and best_tech_score >= 60:
            return "底层技术"
        elif best_app_score >= 60:
            return "应用场景"
    except ImportError:
        logger.warning("fuzzywuzzy 未安装，跳过模糊匹配")
    
    # 兜底：默认归为应用场景
    return "应用场景"
