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
GEN_CHECKPOINT_FILE = DATA_DIR / "gen_checkpoint.json"

# ════════════════════════════════════════════════════════════════
# API 配置（优先从环境变量读取，安全不泄露）
# ════════════════════════════════════════════════════════════════

BASE_URL: str = os.environ.get(
    "YUNWU_BASE_URL", "https://yunwu.ai/v1"
)
API_KEY: str = os.environ.get(
    "YUNWU_API_KEY", "sk-bxKmTvBf5WrJwZ0r474eBfC2De404a38931216Ed79548f05"
)

# 豆包模型专用 API 配置（火山引擎）
DOUBAO_BASE_URL: str = os.environ.get(
    "DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"
)
DOUBAO_API_KEY: str = os.environ.get(
    "DOUBAO_API_KEY", "0bfef660-19b7-4fb8-9623-83df55730ad6"
)

# ════════════════════════════════════════════════════════════════
# 任务参数
# ════════════════════════════════════════════════════════════════

JUDGE_BATCH_SIZE: int = 100         # 每次批量判别的关键词数量
NUM_REPEAT_PER_MODEL: int = 100     # 每个模型、每个领域重复生成的次数
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
    # 豆包模型（火山引擎 ARK）不支持 response_format
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
    """根据模型名称返回对应的 API 客户端配置（base_url + api_key）。"""
    if "doubao" in model_name.lower():
        return {"base_url": DOUBAO_BASE_URL, "api_key": DOUBAO_API_KEY}
    return {"base_url": BASE_URL, "api_key": API_KEY}




"""

# ════════════════════════════════════════════════════════════════
# 生成用模型列表（多样性优先，覆盖各大厂商）
# ════════════════════════════════════════════════════════════════

MODELS: List[str] = [
    "gpt-5-nano-2025-08-07",
]

# ════════════════════════════════════════════════════════════════
# 判别用顶级模型
# ════════════════════════════════════════════════════════════════

JUDGE_MODELS: List[str] = [
    "gpt-5-nano-2025-08-07",
]

"""

# ════════════════════════════════════════════════════════════════
# 生成用模型列表（多样性优先，覆盖各大厂商）
# ════════════════════════════════════════════════════════════════
# 根据2026年2月27日更新的SuperCLUE通用榜总排行榜，总分超过60分的大模型    
MODELS: List[str] = [
    "claude-opus-4-6",          #01
    "gemini-3.1-pro-preview",   #02
    "doubao-seed-2-0-pro-260215",   #03  
    "claude-opus-4-5-20251101", #04
    "gemini-3-pro-preview",     #05
    "gpt-5.2",                  #06
    "kimi-k2.5",                #07
    "gemini-3-flash-preview",   #08
]

# ════════════════════════════════════════════════════════════════
# 判别用顶级模型
# ════════════════════════════════════════════════════════════════

JUDGE_MODELS: List[str] = [
    "claude-opus-4-6",          #01
    "gemini-3.1-pro-preview",   #02
    "doubao-seed-2-0-pro-260215",   #03  
    "claude-opus-4-5-20251101", #04
    "gemini-3-pro-preview",     #05
    "gpt-5.2",                  #06
    "kimi-k2.5",                #07
    "gemini-3-flash-preview",   #08
]




# ════════════════════════════════════════════════════════════════
# 领域定义（26 个领域，全面覆盖银行经营）
# ════════════════════════════════════════════════════════════════

DOMAINS: List[Dict[str, str]] = [
    # ═══ 0. 银行基础概念 ═══
    {
        "name": "金融科技",
        "description": "金融科技、数字金融、开放银行、监管科技、人工智能、大数据、区块链、云计算、物联网等",
    },
]


# ════════════════════════════════════════════════════════════════
# Prompt 构建
# ════════════════════════════════════════════════════════════════

def build_generate_prompt(domain: Dict[str, str]) -> str:
    """根据金融科技领域定义构建关键词生成 Prompt。"""
    return (
        f"请生成一个包含**100个**中文专业词汇的\"{domain['name']}\"词典。\n"
        f"参考词汇：{domain['description']}\n"
        f"要求：每个词汇应确保简洁、准确且意义明确，涵盖\"{domain['name']}\"的所有领域。\n"
        f"格式：必须严格返回一个JSON对象，Key为\"keywords\"，Value为列表。\n"
        f"示例：{{\"keywords\": [\"金融科技\", \"数字金融\", \"开放银行\"]}}"
    )

def build_judge_prompt(keywords_batch: List[str]) -> str:
    """根据金融科技领域定义构建批量判别 Prompt。"""
    kw_list_str = "\n".join(f"{i + 1}. {kw}" for i, kw in enumerate(keywords_batch))
    domain_names = "、".join(d['name'] for d in DOMAINS)
    return (
        f"请逐一判断以下{len(keywords_batch)}个词汇是否属于\"{domain_names}\"领域的专业词汇。\n\n"
        f"词汇列表：\n{kw_list_str}\n\n"
        f"要求：判定属于\"{domain_names}\"领域的词汇返回1，不属于返回0。对每个词汇的判定要给出理由，理由字数不多于20字。\n"
        f"格式：必须严格返回一个JSON对象。包含一个名为'results'的数组，数组中的每个对象拥有且仅有三个键：'keyword'（要判定的词汇）、'score'（1或0）和'reason'（判定理由）。\n\n"
        f"示例：\n"
        f"{{\"results\": [\n"
        f"  {{\"keyword\": \"金融科技\", \"score\": 1, \"reason\": \"典型的前沿金融技术领域\"}},\n"
        f"  {{\"keyword\": \"天气预报\", \"score\": 0, \"reason\": \"属于气象学，与金融无关\"}}\n"
        f"]}}"
    )

