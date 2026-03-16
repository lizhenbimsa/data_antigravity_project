"""
LLMs_for_dic 配置文件

所有可调参数集中在此文件管理，修改后无需改动主脚本。
包含共享工具函数（如 _get_temperature）供多个脚本使用。
"""

import os
from pathlib import Path
from typing import Dict, List

# ════════════════════════════════════════════════════════════════
# 路径配置
# ════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR / "logs"
DATA_DIR = SCRIPT_DIR / "data_processed"
CHECKPOINT_FILE = DATA_DIR / "checkpoint.json"
JUDGE_CHECKPOINT_FILE = DATA_DIR / "judge_checkpoint.json"

# ════════════════════════════════════════════════════════════════
# API 配置（优先从环境变量读取，安全不泄露）
# ════════════════════════════════════════════════════════════════

BASE_URL: str = os.environ.get(
    "YUNWU_BASE_URL", "https://yunwu.ai/v1"
)
API_KEY: str = os.environ.get(
    "YUNWU_API_KEY", "sk-bxKmTvBf5WrJwZ0r474eBfC2De404a38931216Ed79548f05"
)

# ════════════════════════════════════════════════════════════════
# 任务参数
# ════════════════════════════════════════════════════════════════

JUDGE_BATCH_SIZE: int = 70          # 每次批量判别的关键词数量
NUM_REPEAT_PER_MODEL: int = 1       # 每个模型、每个领域重复生成的次数
MAX_WORKERS_GENERATE: int = 70      # 生成阶段并发线程数
MAX_WORKERS_JUDGE: int = 70         # 判别阶段并发线程数
MAX_PARSE_RETRIES: int = 5          # 解析失败重试次数
MAX_RETRIES: int = 200              # 单次任务最大重试次数
MAX_TOTAL_RETRIES: int = 2000       # 全局重试上限（费用保护，防止无限重试）
REQUEST_TIMEOUT: int = 1800         # 单次 API 请求超时（秒），谷歌超时严重
MODEL_FAIL_THRESHOLD: int = 200     # 模型连续失败此次数后自动跳过
LOG_RETENTION_COUNT: int =  20      # 最多保留的日志文件数量（自动清理旧日志）


# ════════════════════════════════════════════════════════════════
# 共享工具函数
# ════════════════════════════════════════════════════════════════

def is_thinking_model(model_name: str) -> bool:
    """判断模型名称是否为 thinking（推理）模式变体。"""
    name = model_name.lower()
    if "thinking" in name:
        return True
    if any(tag in name for tag in ("nothinking", "non-reasoning", "instruct")):
        return False
    if any(name.startswith(p) for p in ("o1", "o3", "o4")):
        return True
    if "deepseek-r1" in name:
        return True
    return False


def get_model_params(model_name: str) -> Dict:
    """
    根据模型名称返回 API 调用参数。

    当前策略：所有模型均不使用推理模式，统一使用
    temperature + JSON mode 以获得最大确定性。
    """
    # 不支持 response_format 的模型列表
    NO_JSON_MODE_MODELS = {"grok-4-fast", "grok-4.1-fast"}

    params: Dict = {
        "temperature": 0,
    }
    if model_name not in NO_JSON_MODE_MODELS:
        params["response_format"] = {"type": "json_object"}
    if "ERNIE" in model_name:
        params["temperature"] = 0.0000000001
    return params


def get_temperature(model_name: str) -> float:
    """获取模型对应的 temperature（向后兼容）。"""
    return get_model_params(model_name).get("temperature", 0)





"""

# ════════════════════════════════════════════════════════════════
# 生成用模型列表（多样性优先，覆盖各大厂商）
# ════════════════════════════════════════════════════════════════

MODELS: List[str] = [
    "gpt-5-nano-2025-08-07",
    "gemini-2.5-flash-nothinking",
]

# ════════════════════════════════════════════════════════════════
# 判别用顶级模型
# ════════════════════════════════════════════════════════════════

JUDGE_MODELS: List[str] = [
    "gpt-5-nano-2025-08-07",
    "gemini-2.5-flash-nothinking",
]

"""

# ════════════════════════════════════════════════════════════════
# 生成用模型列表（多样性优先，覆盖各大厂商）
# ════════════════════════════════════════════════════════════════

MODELS: List[str] = [
    # --- Claude 系列 ---
    "claude-opus-4-5-20251101",
    "claude-sonnet-4-5-20250929",
    "claude-haiku-4-5-20251001",
    "claude-opus-4-1-20250805",
    "claude-opus-4-20250514",
    "claude-sonnet-4-20250514",
    # --- GPT 系列 ---
    "gpt-5.2-all",
    "gpt-5.2-chat",
    "gpt-5.1",
    "gpt-5.1-all",
    "gpt-5.1-chat",
    "gpt-5",
    "gpt-5-all",
    "gpt-5-chat-latest",
    "gpt-5-mini",
    "gpt-5-nano",
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    # --- Gemini 系列 ---
    "gemini-3-flash-preview",
    "gemini-2.5-pro",
    "gemini-2.5-pro-all",
    "gemini-2.5-flash",
    "gemini-2.5-flash-all",
    "gemini-2.5-flash-nothinking",
    # --- Grok 系列 ---
    "grok-4.1",
    "grok-4-1-fast-non-reasoning",
    "grok-4.1-fast",
    "grok-4",
    "grok-4-fast-non-reasoning",
    "grok-4-fast",
    # --- DeepSeek 系列 ---
    "deepseek-v3.2",
    "deepseek-v3.2-fast",
    "deepseek-v3.1",
    "deepseek-v3.1-fast",
    "deepseek-v3",
    "deepseek-v3-fast",
    # --- 豆包/字节 ---
    "doubao-seed-1-8-251228",
    "doubao-seed-1-6-251015",
    # --- 通义千问 ---
    "qwen3-max-2026-01-23",
    "qwen3-max",
    "qwen3-max-preview",
    "qwen3-235b-a22b-instruct-2507",
    "qwen3-next-80b-a3b-instruct",
    # --- Kimi ---
    "kimi-k2.5",
    "kimi-k2",
    "kimi-k2-instruct",
    # --- 文心一言 ---
    "ERNIE-4.0-8K",
    "ERNIE-3.5-8K",
    # --- 其他 ---
    "glm-4.7",
    "minimax-m2.1",
    "mistral-large-latest",
]

# ════════════════════════════════════════════════════════════════
# 判别用顶级模型
# ════════════════════════════════════════════════════════════════

JUDGE_MODELS: List[str] = [
    "claude-opus-4-6",
    "gemini-3-pro-preview",
    "gpt-5.2",
]




# ════════════════════════════════════════════════════════════════
# 银行领域定义（26 个领域，全面覆盖银行经营）
# ════════════════════════════════════════════════════════════════

DOMAINS: List[Dict[str, str]] = [
    # ═══ 0. 银行基础概念 ═══
    {
        "name": "银行基础概念",
        "description": "银行、存款、取款、利率、利息、账户、储户、柜台、柜员、ATM、金库、汇款、转账、开户、销户、存折、银行卡、网点、支行、分行、总行、央行等",
    },
    # ═══ I. 核心业务条线（8个） ═══
    {
        "name": "个人银行与零售业务",
        "description": "储蓄存款、定期存款、大额存单、个人贷款、住房按揭、消费信贷、信用卡、借记卡、个人理财、手机银行、网上银行、社区银行等",
    },
    {
        "name": "公司银行与对公业务",
        "description": "公司贷款、银团贷款、流动资金贷款、固定资产贷款、小微企业贷款、供应链融资、商业汇票、保理业务、企业存款、现金管理、代发工资等",
    },
    {
        "name": "投资银行与资本市场",
        "description": "IPO承销、债券发行、并购重组、结构化融资、资产证券化、财务顾问、杠杆收购、股权融资、夹层融资、项目融资、可转债、定向增发等",
    },
    {
        "name": "资产管理与财富管理",
        "description": "理财产品、基金托管、信托计划、私人银行、家族信托、资产配置、净值型产品、固定收益、权益投资、另类资产、委外投资、FOF基金等",
    },
    {
        "name": "同业业务与金融市场",
        "description": "同业拆借、回购协议、票据贴现、银行间市场、利率互换、债券交易、货币基金、短期融资券、同业存单、资金池、资产负债管理、利率定价等",
    },
    {
        "name": "国际业务与贸易金融",
        "description": "跨境汇款、信用证、国际结算、外汇交易、贸易融资、保函、福费廷、出口信贷、离岸金融、汇率风险对冲、跨境人民币、自贸区金融等",
    },
    {
        "name": "交易银行与支付清算",
        "description": "大额支付系统、小额支付系统、第三方支付、跨境支付、清算结算、电子票据、条码支付、数字人民币、现金管理、交易银行、供应链支付等",
    },
    {
        "name": "信用管理与不良资产",
        "description": "信贷审批、贷后管理、五级分类、不良贷款、核销清收、债转股、资产处置、催收管理、信用评分、授信管理、联合征信、逾期管理等",
    },
    # ═══ II. 风险合规与监管（4个） ═══
    {
        "name": "全面风险管理",
        "description": "信用风险、市场风险、操作风险、流动性风险、利率风险、汇率风险、声誉风险、战略风险、集中度风险、压力测试、风险加权资产、经济资本等",
    },
    {
        "name": "合规与反洗钱",
        "description": "合规管理、反洗钱、反恐怖融资、制裁合规、客户尽职调查、可疑交易报告、大额交易报告、内部合规审查、监管处罚、消费者权益保护等",
    },
    {
        "name": "监管体系与宏观审慎",
        "description": "银行监管、货币政策、基准利率、存款准备金率、公开市场操作、宏观审慎监管、巴塞尔协议、资本充足率、系统重要性银行、金融稳定、存款保险等",
    },
    {
        "name": "宏观经济与政策环境",
        "description": "经济政策、利率政策、财政政策、房地产政策、房地产风险、地方政府债务、地缘政治风险、气候政策、环境政策、人口老龄化、经济周期等",
    },
    # ═══ III. 治理经营与管理（5个） ═══
    {
        "name": "公司治理与股权结构",
        "description": "董事会治理、监事会、独立董事、股权结构、关联交易、信息披露、薪酬管理、风险委员会、审计委员会、股东大会、治理评价等",
    },
    {
        "name": "战略规划与业务转型",
        "description": "战略转型、国际化战略、兼并重组、经营模式创新、轻资产转型、零售转型、综合化经营、差异化竞争、品牌建设、市场定位等",
    },
    {
        "name": "财务管理与绩效分析",
        "description": "净息差、净利差、不良率、拨备覆盖率、资本利润率、成本收入比、贷存比、杠杆率、流动性覆盖率、经济增加值、RAROC、中间业务收入占比等",
    },
    {
        "name": "人力资源与组织文化",
        "description": "人才培养、绩效考核、薪酬体系、组织架构、企业文化、员工培训、高管管理、人才引进、岗位设置、劳动用工、合规文化建设等",
    },
    {
        "name": "运营管理与服务质量",
        "description": "网点管理、柜面服务、客户体验、渠道建设、流程优化、集中运营、业务外包、服务标准、客户投诉、满意度调查、全渠道协同等",
    },
    # ═══ IV. 科技与数据（4个） ═══
    {
        "name": "金融科技与数字化转型",
        "description": "FinTech、金融科技、数字化转型、数字银行、开放银行、监管科技、智能投顾、数字资产、数字货币、数字人民币、加密货币、嵌入式金融、去中心化金融等",
    },
    {
        "name": "前沿技术与智能应用",
        "description": "人工智能、大数据、区块链、云计算、物联网、5G/6G通信、移动互联网、机器学习、自然语言处理、知识图谱、RPA流程自动化、联邦学习等",
    },
    {
        "name": "数据治理与数据要素",
        "description": "数据资产、数据要素、数据共享、数据智能、数据科学、数据安全、隐私计算、数据中台、数据标准化、数据质量、数据湖、主数据管理等",
    },
    {
        "name": "信息安全与业务连续性",
        "description": "网络安全、信息安全、数据泄露防护、灾难恢复、业务连续性计划、等级保护、渗透测试、安全审计、反欺诈、身份认证、零信任架构等",
    },
    # ═══ V. 创新与可持续（4个） ═══
    {
        "name": "金融创新与新兴业态",
        "description": "科技金融、场景金融、消费金融、开放金融、银保合作、银证合作、综合金融、平台经济、跨界融合、沙盒监管等",
    },
    {
        "name": "绿色金融与ESG",
        "description": "绿色信贷、绿色债券、碳金融、ESG、气候风险、环境保护、可持续金融、转型金融、环境信息披露、碳交易、赤道原则、社会责任投资等",
    },
    {
        "name": "普惠金融与乡村振兴",
        "description": "普惠金融、小微金融、三农金融、乡村振兴、农村信用社、扶贫贷款、助学贷款、创业担保贷款、金融服务下沉、数字普惠等",
    },
    {
        "name": "养老金融与民生服务",
        "description": "养老金融、养老理财、个人养老金、企业年金、职业年金、长期护理保险、医疗健康金融、教育金融、住房公积金、民生缴费等",
    },
]


# ════════════════════════════════════════════════════════════════
# Prompt 构建
# ════════════════════════════════════════════════════════════════

def build_generate_prompt(domain: Dict[str, str]) -> str:
    """根据银行领域定义构建关键词生成 Prompt。"""
    return (
        f"你是一名银行领域的资深专家。请针对银行的\"{domain['name']}\"领域，"
        f"生成一个包括 100个关键词的列表。\n"
        f"参考范围：{domain['description']}\n"
        f"要求：关键词以中文为主，非必要严禁多于16个字符，非必要严禁中英文混写。严禁生成的关键词多于100个。\n"
        f"格式：请直接给出结果，不要输出任何思考过程、分析步骤或推理链。返回标准的JSON对象，Key为\"keywords\"，Value为列表。\n"
        f"示例：{{\"keywords\": [\"存款\", \"Fintech\", \"利率\", ...]}}"
    )


def build_judge_prompt(keywords_batch: List[str]) -> str:
    """构建批量判别 Prompt。"""
    kw_list_str = "\n".join(f"{i + 1}. {kw}" for i, kw in enumerate(keywords_batch))
    return (
        f"你是一名银行领域的资深专家。请逐一判断以下{len(keywords_batch)}个关键词是否属于银行领域的专业关键词。\n\n"
        f"关键词列表：\n{kw_list_str}\n\n"
        f"要求：\n"
        f"1. 属于银行领域返回1，不属于返回0。\n"
        f"2. 每个关键词给出不超过20字的理由。\n"
        f"3. 请直接给出结果，不要输出任何思考过程、分析步骤或推理链。返回标准的JSON对象。\n\n"
        f"返回格式示例：\n"
        f"{{\"results\": [\n"
        f"  {{\"keyword\": \"存款\", \"score\": 1, \"reason\": \"银行核心负债业务\"}},\n"
        f"  {{\"keyword\": \"天气预报\", \"score\": 0, \"reason\": \"与银行无关\"}}\n"
        f"]}}"
    )

