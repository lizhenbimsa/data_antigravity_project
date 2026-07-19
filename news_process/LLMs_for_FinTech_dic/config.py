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
# 环境变量加载
# ════════════════════════════════════════════════════════════════
# 本子管道独立运行（python 00_LLMs_for_dic.py）时不经主项目 core.config 的
# _load_dotenv，故在此显式从主项目 news_process/.env（= SCRIPT_DIR.parent/.env）
# 载入，使 YUNWU_FULL_KEY 等键可被下方 os.environ.get 读到；override=False 不覆盖
# shell 已显式设定的同名变量（优先级：进程环境 > .env）。
try:
    from dotenv import load_dotenv
    load_dotenv(SCRIPT_DIR.parent / ".env", override=False)
except ImportError:
    pass

# ════════════════════════════════════════════════════════════════
# API 配置（优先从环境变量读取，安全不泄露）
# ════════════════════════════════════════════════════════════════

BASE_URL: str = os.environ.get(
    "YUNWU_BASE_URL", "https://yunwu.ai/v1"
)
API_KEY: str = os.environ.get("YUNWU_FULL_KEY", "")

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

JUDGE_BATCH_SIZE: int = 200         # 每次批量判别的关键词数量
NUM_REPEAT_PER_MODEL: int = 10      # 每个模型、每个领域重复生成的次数
MAX_WORKERS_GENERATE: int = 200     # 生成阶段并发线程数
MAX_WORKERS_JUDGE: int = 200        # 判别阶段并发线程数
MAX_PARSE_RETRIES: int = 100        # 解析失败重试次数
MAX_JUDGE_RETRIES: int = 200        # 判别解析失败重试次数
MAX_RETRIES: int = 500              # 单次任务最大重试次数
MAX_TOTAL_RETRIES: int = 50         # 全局重试上限（费用保护，防止无限重试）
REQUEST_TIMEOUT: int = 1800         # 单次 API 请求超时（秒），谷歌超时严重
MODEL_FAIL_THRESHOLD: int = 50      # 模型连续失败此次数后自动跳过
MAX_CONCURRENT_PER_MODEL: int = 10  # 每个模型的最大并发请求数（防止触发 429 限流）
# 日志文件固定命名为「同 py 文件名」并 mode="w" 覆盖写入，只保留最近一次运行，
# 故不再需要"保留最近 N 个"的滚动清理配置（原 LOG_RETENTION_COUNT 已移除）。


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


"""


# ════════════════════════════════════════════════════════════════
# 生成用模型列表（多样性优先，覆盖各大厂商）
# ════════════════════════════════════════════════════════════════
# 2026年7月18日，根据14个中国和国外主流大模型，其中7个是美国大模型，7个是中国大模型
MODELS: List[str] = [
    "gpt-5.4-nano",
    "gemini-3.1-flash-lite"
]

# ════════════════════════════════════════════════════════════════
# 判别用顶级模型
# ════════════════════════════════════════════════════════════════

JUDGE_MODELS: List[str] = [
    "gpt-5.4-nano",
    "gemini-3.1-flash-lite"
]


"""

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
    "kimi-k2.6",
    "glm-5.2",
    "qwen3.7-max",
    "deepseek-v4-pro",
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
    "kimi-k2.6",
    "glm-5.2",
    "qwen3.7-max",
    "deepseek-v4-pro",
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
        "description": "金融科技、数字金融、智慧金融、数字普惠金融、网络金融、电子银行、网上银行、网络银行、网银、手机银行、掌上银行、电话银行、微信银行、智慧银行、智能银行、直销银行、开放银行、互联网银行、数字银行、虚拟银行、无人银行、远程银行、智慧网点、智能网点、移动银行、数字人民币、云闪付、数字货币、互联网贷款、数字信贷、线上贷款、互联网存款、智能存款、数字信用卡、智能柜台、超级柜台、智能客服、智能营销、客户画像、数字员工、银企直连、智能投顾、数字化、数智化、线上化、数字技术、信息科技、科技赋能、科技投入、人工智能、云计算、大数据、区块链、大模型、生物识别、隐私计算、联邦学习、知识图谱、物联网、数据要素、数据治理、数据资产、数据智能、数据中台、数据入表、场景金融、嵌入式金融、开放平台、监管科技、智能风控、大数据风控、数字化风控、反欺诈、监管沙盒、智能反洗钱、合规科技等",
    },
]


# ════════════════════════════════════════════════════════════════
# Prompt 构建
# ════════════════════════════════════════════════════════════════

# ══ 生成端 ∩ 判别端 共享的三条「银行金融科技」正向判据理由 (score=1) — SSOT 锁步 ══
#   顺序与 build_judge_prompt 内 JUDGE_REASONS 前三条严格一一对应（同一 index）：
#     [0] 银行锚定的领域母词  [1] 有银行·通用科技词(召回向)  [2] 有银行·有科技(精确标记词)
#   两处唯一互锁点：生成 Prompt 要求模型每词三选一原文照抄，判别 Prompt 的 JUDGE_REASONS
#   前三条直接引用本列表（勿在 judge 处再写字面，防两端漂移）。改字面 = 两个 Prompt 同步变。
POSITIVE_REASONS: List[str] = [
    "银行金融科技领域的核心词汇",   # 银行锚定的领域母词（≈ judge ①金融科技）
    "银行主体共现的通用科技词汇",   # 有银行·通用科技词，宽口径/召回向（≈ judge ②人工智能）
    "提及即为银行金融科技词汇",     # 有银行·有科技，精确标记词（≈ judge ③手机银行）
]

# ══ 判别端专用的三条 score=0 判据理由（否定/边界），与 POSITIVE_REASONS 对称 ══
#   顺序与 build_judge_prompt 内 JUDGE_REASONS 后三条严格一一对应（同一 index）：
#     [0] 有银行·无科技(传统业务)  [1] 判0兜底(他类/无关)  [2] 有科技·无银行(似是而非)
#   目前仅判别端消费（生成端只用 POSITIVE_REASONS 的正向判据自我锚定），集中于此防字面漂移。
NEGATIVE_REASONS: List[str] = [
    "无金融科技属性的银行传统业务词汇",   # 有银行·无科技（≈ judge ④柜台业务；与①对称）
    "不属于银行金融科技的词汇",           # 判0兜底：他类金融/完全无关（≈ judge ⑤天气预报）
    "默认主体非银行的金融科技词汇",       # 有科技·无银行，最硬似是而非（≈ judge ⑥第三方支付）
]


def build_generate_prompt(domain: Dict[str, str]) -> str:
    """根据银行金融科技领域定义构建关键词生成 Prompt。

    每个词汇须附一条「入选理由」，从与判别端共享的 3 条正向判据 POSITIVE_REASONS
    (score=1) 中三选一原文照抄 —— 在生成端即以同一套「银行 ∩ 金融科技」正向判据自我
    锚定，压制裸技术词（AI/云计算/大数据…）误报，与 build_judge_prompt 准入判据同源锁步。
    理由仅作生成端约束（CoT 自我判据），不落盘；下游 fetch_batch 从对象数组只提取
    "keyword" 字段（并向后兼容旧的纯字符串列表）。
    """
    reason_menu = "\n".join(f"  {i}. \"{r}\"" for i, r in enumerate(POSITIVE_REASONS, 1))
    return (
        f"请生成一个包含**200个**中文专业词汇的\"{domain['name']}\"词典。\n"
        f"参考词汇：{domain['description']}\n"
        f"要求：每个词汇应确保简洁、准确且意义明确，涵盖\"{domain['name']}\"的所有领域；"
        f"并为每个词汇提供一条入选理由，理由必须从以下 3 项中原文照抄选取一个"
        f"（不得改写、合并或新增）：\n"
        f"{reason_menu}\n"
        f"格式：必须严格返回一个JSON对象，Key为\"keywords\"，Value为对象数组，"
        f"数组中每个对象拥有且仅有两个键：\"keyword\"（词汇）与\"reason\"（须为上述 3 项之一）。\n"
        f"示例：{{\"keywords\": ["
        f"{{\"keyword\": \"金融科技\", \"reason\": \"{POSITIVE_REASONS[0]}\"}}, "
        f"{{\"keyword\": \"人工智能\", \"reason\": \"{POSITIVE_REASONS[1]}\"}}, "
        f"{{\"keyword\": \"手机银行\", \"reason\": \"{POSITIVE_REASONS[2]}\"}}]}}"
    )

def build_judge_prompt(keywords_batch: List[str]) -> str:
    """根据银行金融科技领域定义构建批量判别 Prompt。"""
    kw_list_str = "\n".join(f"{i + 1}. {kw}" for i, kw in enumerate(keywords_batch))
    domain_names = "、".join(d['name'] for d in DOMAINS)
    # ══ 六类固定判据（SSOT）：(代表词, reason, score)。reason 六选一、原文照抄，
    #    score 由 reason 唯一决定；判据句已从 prompt 移除，改由这六个理由承载，勿删/勿改写。
    #    判据本质 = 银行 ∩ 金融科技 两侧俱全 → 1；否则 → 0（0 侧三类：兜底其余=天气预报 / 有科技·无银行=第三方支付 / 有银行·无科技=柜台业务）。
    #    顺序 (2026-07-19 优化为「排除似是而非」向): score 降序 1,1,1,0,0,0 — 末段 4-6 位全 0（近因最强位压满「拒收」示范），
    #    最硬似是而非「第三方支付(非银金科)」殿后（占最强近因位）；③手机银行(1)→④柜台业务(0) 于 1→0 交界构成「银行有无科技」最小对比对；
    #    0:1 配比 3:3 平衡（抑多数标签偏置）；reason_menu 与示例均随此列表序生成。
    #      ① 金融科技   银行金融科技领域的核心词汇     1  银行锚定的领域母词（方案A加"银行"消 金融科技∩第三方支付 重叠）
    #      ② 人工智能   银行主体共现的通用科技词汇     1  有银行·通用科技词（宽口径/召回向；「科技」显式限定金科侧，斥非科技泛词）
    #      ③ 手机银行   提及即为银行金融科技词汇       1  有银行·有科技（精确标记词）
    #      ④ 柜台业务   无金融科技属性的银行传统业务词汇 0  有银行·无科技（与⑥对称: [所缺]的[所属]词汇; 与③手机银行构成科技边界最小对比对）
    #      ⑤ 天气预报   不属于银行金融科技的词汇       0  判0兜底（其余全部 0：他类金融/完全无关等，非④非⑥；示例取纯无关词）
    #      ⑥ 第三方支付 默认主体非银行的金融科技词汇   0  有科技·无银行（最硬似是而非·殿后压最强近因）
    # ⚠ menu 与示例均由 SSOT 用「,\n」.join 生成，末条自动无尾逗号（不再手工维护）；
    #    doubao 非 JSON-mode 靠 prompt 产合法 JSON，_safe_parse_json 是裸 json.loads。
    #    六条 reason 全部逐字复用模块级常量（勿在此重写字面，防两端漂移）：
    #    前三条正向 = POSITIVE_REASONS（生成端与判别端同源共享）；后三条否定 = NEGATIVE_REASONS（仅判别端）。
    JUDGE_REASONS = [
        ("金融科技", POSITIVE_REASONS[0], 1),
        ("人工智能", POSITIVE_REASONS[1], 1),
        ("手机银行", POSITIVE_REASONS[2], 1),
        ("柜台业务", NEGATIVE_REASONS[0], 0),
        ("天气预报", NEGATIVE_REASONS[1], 0),
        ("第三方支付", NEGATIVE_REASONS[2], 0),
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
        f"每个词汇的 reason 必须从以下 6 个固定理由中原文照抄选取一个（不得改写、合并或新增），"
        f"score 由所选 reason 唯一决定：\n"
        f"{reason_menu}\n"
        f"格式：必须严格返回一个JSON对象。包含一个名为'results'的数组，数组中的每个对象拥有且仅有三个键："
        f"'keyword'（要判定的词汇）、'score'（1或0）和'reason'（判定理由，须为上述 6 个之一）。\n\n"
        f"示例：\n"
        f"{{\"results\": [\n"
        f"{example_items}\n"
        f"]}}"
    )
