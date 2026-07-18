"""
LLMs_for_dic 配置文件

所有可调参数集中在此文件管理，修改后无需改动主脚本。
包含共享工具函数（如 get_temperature）供多个脚本使用。
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
GEN_CHECKPOINT_FILE = DATA_DIR / "gen_checkpoint.json"

# ════════════════════════════════════════════════════════════════
# API 配置（优先从环境变量读取，安全不泄露）
# ════════════════════════════════════════════════════════════════

BASE_URL: str = os.environ.get(
    "YUNWU_BASE_URL", "https://yunwu.ai/v1"
)
API_KEY: str = os.environ.get("YUNWU_API_KEY", "")

# ════════════════════════════════════════════════════════════════
# LLM 缓存配置（本目录独立缓存，见 llm_cache.py）
# ════════════════════════════════════════════════════════════════

# 缓存库文件（SQLite，与主项目 news_process 的 _llm_cache.db 完全独立）
CACHE_DB_FILE = DATA_DIR / "_llm_cache.db"
# 整体开关：设 LLMS_DIC_CACHE=0 停用缓存（读写全跳过）
CACHE_ENABLED: bool = os.environ.get("LLMS_DIC_CACHE", "1").strip().lower() not in {
    "0", "false", "no", "off",
}
# 离线模式：设 LLMS_DIC_OFFLINE=1 后缓存 miss 直接报错，绝不调 API（$0 重放守卫）
OFFLINE_MODE: bool = os.environ.get("LLMS_DIC_OFFLINE", "").strip().lower() in {
    "1", "true", "yes", "on",
}

# ════════════════════════════════════════════════════════════════
# 任务参数
# ════════════════════════════════════════════════════════════════

JUDGE_BATCH_SIZE: int = 100         # 每次批量判别的关键词数量
NUM_REPEAT_PER_MODEL: int = 10      # 每个模型、每个领域重复生成的次数
MAX_WORKERS_GENERATE: int = 200     # 生成阶段并发线程数
MAX_WORKERS_JUDGE: int = 200        # 判别阶段并发线程数
MAX_PARSE_RETRIES: int = 100        # 解析失败重试次数
MAX_JUDGE_RETRIES: int = 200        # 判别解析失败重试次数
MAX_RETRIES: int = 500              # 单次任务最大重试次数
MAX_TOTAL_RETRIES: int = 5000       # 全局重试上限（费用保护，防止无限重试）
REQUEST_TIMEOUT: int = 1800         # 单次 API 请求超时（秒），谷歌超时严重
MODEL_FAIL_THRESHOLD: int = 500     # 模型连续失败此次数后自动跳过
MAX_CONCURRENT_PER_MODEL: int = 10  # 每个模型的最大并发请求数（防止触发 429 限流）
LOG_RETENTION_COUNT: int =  10      # 最多保留的日志文件数量（自动清理旧日志）


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
    根据模型名称返回 API 调用基础参数。

    注意：返回的 temperature 为默认值（0），调用方可根据场景覆盖或移除：
    - 生成阶段（fetch_batch）：移除 temperature，使用模型自身默认值以获得多样性
    - 判别阶段（judge_batch）：强制 temperature=0 以获得最大确定性
    """
    # 不支持 response_format 的模型列表
    NO_JSON_MODE_MODELS = {"grok-4-fast", "grok-4.1-fast"}

    params: Dict = {
        "temperature": 0,
    }
    # 豆包模型不支持 response_format（历史上在火山引擎 ARK 实测确认）
    no_json = model_name in NO_JSON_MODE_MODELS or "doubao" in model_name.lower()
    if not no_json:
        params["response_format"] = {"type": "json_object"}
    if "ERNIE" in model_name:
        params["temperature"] = 0.0000000001
    return params


def get_temperature(model_name: str) -> float:
    """获取模型对应的 temperature（向后兼容）。"""
    return get_model_params(model_name).get("temperature", 0)


def get_client_config(model_name: str) -> Dict[str, str]:
    """根据模型名称返回对应的 API 客户端配置（base_url + api_key）。

    所有模型（含豆包）统一走 BASE_URL + API_KEY，不再有厂商专用端点。
    """
    return {"base_url": BASE_URL, "api_key": API_KEY}


# ════════════════════════════════════════════════════════════════
# 生成用模型列表（多样性优先，覆盖各大厂商）
# ════════════════════════════════════════════════════════════════
# 2026年7月18日，根据14个中国和国外主流大模型，其中7个是美国大模型，7个是中国大模型
MODELS: List[str] = [
    "claude-fable-5",
    "claude-opus-4-8",
    "gpt-5.6-sol",
    "gpt-5.6-terra",
    "gemini-3.1-pro-preview",
    "gemini-3.5-flash",
    "grok-4.5",
    "kimi-k3",
    "glm-5.2",
    "qwen3.7-max",
    "deepseek-v4-pro",
    "doubao-seed-2-1-pro-260628",
    "MiniMax-M3",
    "mimo-v2.5-pro",
]

# ════════════════════════════════════════════════════════════════
# 判别用顶级模型
# ════════════════════════════════════════════════════════════════

JUDGE_MODELS: List[str] = [
    "claude-fable-5",
    "claude-opus-4-8",
    "gpt-5.6-sol",
    "gpt-5.6-terra",
    "gemini-3.1-pro-preview",
    "gemini-3.5-flash",
    "grok-4.5",
    "kimi-k3",
    "glm-5.2",
    "qwen3.7-max",
    "deepseek-v4-pro",
    "doubao-seed-2-1-pro-260628",
    "MiniMax-M3",
    "mimo-v2.5-pro",
]







# ════════════════════════════════════════════════════════════════
# 领域定义（覆盖银行经营；领域数以下方 DOMAINS 列表实际项数为准，
# fix(S12, 2026-07-14): 历史注释曾写死"26 个"，现已随领域列表精简至
# len(DOMAINS)=1，禁再写死数字——消费方一律读 len(DOMAINS) 动态获取）
# ════════════════════════════════════════════════════════════════

DOMAINS: List[Dict[str, str]] = [
    {
        "name": "银行金融科技",
        "description": "金融科技、数字金融、智慧金融、数字普惠金融、网络金融、电子银行、网上银行、网络银行、网银、手机银行、掌上银行、电话银行、微信银行、智慧银行、智能银行、直销银行、开放银行、互联网银行、数字银行、虚拟银行、无人银行、远程银行、智慧网点、智能网点、移动银行、数字人民币、云闪付、数字货币、互联网贷款、数字信贷、线上贷款、互联网存款、智能存款、数字信用卡、智能柜台、超级柜台、智能客服、智能营销、客户画像、数字员工、银企直连、智能投顾、数字化、数智化、线上化、数字技术、信息科技、科技赋能、科技投入、人工智能、云计算、大数据、区块链、大模型、生物识别、隐私计算、联邦学习、知识图谱、机器人、物联网、数据要素、数据治理、数据资产、数据智能、数据中台、数据入表、场景金融、嵌入式金融、开放平台、监管科技、智能风控、大数据风控、数字化风控、反欺诈、监管沙盒、智能反洗钱、合规科技等",
    },
]


# ════════════════════════════════════════════════════════════════
# Prompt 构建
# ════════════════════════════════════════════════════════════════

def build_generate_prompt(domain: Dict[str, str]) -> str:
    """根据银行金融科技领域定义构建关键词生成 Prompt。"""
    return (
        f"请生成一个包含**200个**中文专业词汇的\"{domain['name']}\"词典。\n"
        f"参考词汇：{domain['description']}\n"
        f"要求：每个词汇应确保简洁、准确且意义明确，涵盖\"{domain['name']}\"的所有领域。\n"
        f"格式：必须严格返回一个JSON对象，Key为\"keywords\"，Value为列表。\n"
        f"示例：{{\"keywords\": [\"金融科技\", \"数字金融\", \"手机银行\"]}}"
    )

def build_judge_prompt(keywords_batch: List[str]) -> str:
    """根据银行金融科技领域定义构建批量判别 Prompt。"""
    kw_list_str = "\n".join(f"{i + 1}. {kw}" for i, kw in enumerate(keywords_batch))
    domain_names = "、".join(d['name'] for d in DOMAINS)
    # ══ 五类固定判据（SSOT）：(代表词, reason, score)。reason 五选一、原文照抄，
    #    score 由 reason 唯一决定；判据句已从 prompt 移除，改由这五个理由承载，勿删/勿改写。
    #    判据本质 = 银行 ∩ 金融科技 两侧俱全 → 1；否则 → 0（④=非银金科词的具体理由，⑤=判0兜底覆盖其余）。
    #      ① 手机银行   提及即为银行金融科技词汇     1  有银行·有科技（精确标记词）
    #      ② 金融科技   银行金融科技领域的核心词汇   1  银行锚定的领域母词（方案A加"银行"消②④重叠）
    #      ③ 人工智能   银行主体共现的通用词汇       1  有银行·通用词（宽口径/召回向）
    #      ④ 第三方支付 默认主体非银行的金融科技词汇 0  有科技·无银行
    #      ⑤ 存贷款     不属于银行金融科技的词汇     0  判0兜底（非科技/非银/无关主体全归此）
    # ⚠ menu 与示例均由 SSOT 用「,\n」.join 生成，末条自动无尾逗号（不再手工维护）；
    #    doubao 非 JSON-mode 靠 prompt 产合法 JSON，_safe_parse_json 是裸 json.loads。
    JUDGE_REASONS = [
        ("手机银行", "提及即为银行金融科技词汇", 1),
        ("金融科技", "银行金融科技领域的核心词汇", 1),
        ("人工智能", "银行主体共现的通用词汇", 1),
        ("第三方支付", "默认主体非银行的金融科技词汇", 0),
        ("存贷款", "不属于银行金融科技的词汇", 0),
    ]
    reason_menu = "\n".join(
        f"  {idx}. \"{reason}\" → score={score}"
        for idx, (_kw, reason, score) in enumerate(JUDGE_REASONS, 1)
    )
    example_items = ",\n".join(
        f"  {{\"keyword\": \"{kw}\", \"score\": {score}, \"reason\": \"{reason}\"}}"
        for (kw, reason, score) in JUDGE_REASONS
    )
    return (
        f"请逐一判断以下{len(keywords_batch)}个词汇是否属于\"{domain_names}\"领域的专业词汇。\n\n"
        f"词汇列表：\n{kw_list_str}\n\n"
        f"要求：判定属于\"{domain_names}\"（银行与金融科技两侧俱全）返回1，否则返回0。"
        f"每个词汇的 reason 必须从以下 5 个固定理由中原文照抄选取一个（不得改写、合并或新增），"
        f"score 由所选 reason 唯一决定：\n"
        f"{reason_menu}\n"
        f"格式：必须严格返回一个JSON对象。包含一个名为'results'的数组，数组中的每个对象拥有且仅有三个键："
        f"'keyword'（要判定的词汇）、'score'（1或0）和'reason'（判定理由，须为上述 5 个之一）。\n\n"
        f"示例：\n"
        f"{{\"results\": [\n"
        f"{example_items}\n"
        f"]}}"
    )

