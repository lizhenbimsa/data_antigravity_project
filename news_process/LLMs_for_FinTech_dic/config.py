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
NUM_REPEAT_PER_MODEL: int = 1       # 每个模型、每个领域重复生成的次数
MAX_WORKERS_GENERATE: int = 200     # 生成阶段并发线程数
MAX_WORKERS_JUDGE: int = 200        # 判别阶段并发线程数
MAX_PARSE_RETRIES: int = 100        # 解析失败重试次数
MAX_JUDGE_RETRIES: int = 200        # 判别解析失败重试次数
MAX_RETRIES: int = 500              # 单次任务最大重试次数
MAX_TOTAL_RETRIES: int = 50         # 全局重试上限（费用保护，防止无限重试）
REQUEST_TIMEOUT: int = 1800         # 单次 API 请求超时（秒），谷歌超时严重
MODEL_FAIL_THRESHOLD: int = 50      # 模型连续失败此次数后自动跳过
MAX_CONCURRENT_PER_MODEL: int = 10  # 每个模型的最大并发请求数（防止触发 429 限流）
# 单次 API 响应的最大输出 token（显式上限，防止响应被截断）。
# 背景：生成端每次要求 200 个「对象数组」词条 {keyword, reason}（判别端 200 条
# {keyword, score, reason}），单条响应体量约 6,000–7,000 输出 token。多数模型默认输出
# 上限足够，但个别模型（实测 kimi-k2.6）在 yunwu 代理下默认上限偏低（约 4,096），
# 会在生成到约 150 词处**截断**成非法 JSON → 解析失败 → 触发大量重试。显式抬高上限
# 让所有模型都能完整输出整个数组。⚠ 这是**运行期 API 参数**，非 Prompt 字段/模型清单/
# 阈值/数量链的任何一项，与手稿 FinTech_Dictionary_LLMs_Paper_Final.md 的锁步无关，
# 不改变任何被誊抄的字面。设 None/<=0 则不传 max_tokens（回退各模型默认上限）。
MAX_OUTPUT_TOKENS: int = 16384      # 16k >> 单条约 7k 需求，对全部 14 个前沿模型均在其输出上限内
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

# ══ 生成端 ∩ 判别端 共享的六条「银行金融科技」判据理由 (单一 SSOT 字面源) ══
#   合并前本为 POSITIVE_REASONS(正向3) + NEGATIVE_REASONS(否定3) 两独立字面块，现统一为
#   单一列表 REASONS，每条 = (代表词, reason, score)，score 由 reason 唯一决定：
#   前三条 score=1（正向，生成端亦用于自我锚定）、后三条 score=0（否定/边界，仅判别端用）。
#   顺序即 build_judge_prompt 的 1..6 象限，score 降序 1,1,1,0,0,0（末段 4-6 全 0 占最强近因位，
#   压满「拒收」示范；③手机银行(1)→④柜台业务(0) 于 1→0 交界构成「银行有无科技」最小对比对；
#   最硬似是而非「第三方支付(有科技·无银行)」殿后；0:1 配比 3:3 平衡，抑多数标签偏置）：
#     ① 金融科技   银行金融科技领域的核心词汇       1  银行锚定的领域母词
#     ② 人工智能   银行主体共现的通用科技词汇       1  有银行·通用科技词（宽口径/召回向）
#     ③ 手机银行   提及即为银行金融科技词汇         1  有银行·有科技（精确标记词）
#     ④ 柜台业务   无金融科技属性的银行传统业务词汇 0  有银行·无科技（与⑥对称；与③构成科技边界最小对比对）
#     ⑤ 天气预报   不属于银行金融科技的词汇         0  判0兜底（他类金融/完全无关）
#     ⑥ 第三方支付 默认主体非银行的金融科技词汇     0  有科技·无银行（最硬似是而非·殿后）
#   两处 Prompt 均从本列表派生，勿在别处重写字面（防两端漂移）；改字面 = 两个 Prompt 同步变：
#     · 生成端 build_generate_prompt：取 score==1 的三条 reason 自我锚定（下方 POSITIVE_REASONS）。
#     · 判别端 build_judge_prompt：直接消费全部六条 (kw, reason, score)（其内 JUDGE_REASONS = REASONS）。
REASONS: List[tuple] = [
    ("金融科技",   "银行金融科技领域的核心词汇",       1),
    ("人工智能",   "银行主体共现的通用科技词汇",       1),
    ("手机银行",   "提及即为银行金融科技词汇",         1),
    ("柜台业务",   "无金融科技属性的银行传统业务词汇", 0),
    ("天气预报",   "不属于银行金融科技的词汇",         0),
    ("第三方支付", "默认主体非银行的金融科技词汇",     0),
]

# 生成端只用正向判据：从 SSOT 按序抽取 score==1 的 reason 文本（逐字等价旧 POSITIVE_REASONS）。
POSITIVE_REASONS: List[str] = [reason for _kw, reason, score in REASONS if score == 1]


def reason_text_from_index(raw) -> str:
    """把判别端模型返回的 reason 序号 (0-based) 映回 REASONS 理由全文（落盘可读化用）。

    ⚠ 纯本地查表，**不调任何 LLM**：模型按新契约只输出序号（省 token/抗截断），可读文本在
    我们这侧确定性补回，$0 成本、离线可跑。发生在大模型调用返回**之后**（judge_batch 解析处）。
    - raw 为 int / 整数浮点(如 0.0) / 纯数字字符串(含首尾空白) 且落在 [0, len(REASONS)) →
      返回对应 reason 文本。用 int(raw) 直转（int() 对字符串自动 strip、对 float 取整），
      比 int(str(raw)) 更稳健：后者会把 0.0 变成非法的 "0.0" 而漏映射。
    - 其它情形（模型仍回了理由全文 / 越界 / 空 / 无法解析）→ 原样 str 返回
      （向后兼容旧缓存的全文格式 + fail-soft，绝不因单条畸形值崩批）。
    生成端 reason 不落盘（fetch_batch 只取 keyword），无需反查，故仅判别端消费本函数。
    """
    try:
        idx = int(raw)
    except (TypeError, ValueError):
        return str(raw).strip()
    if 0 <= idx < len(REASONS):
        return REASONS[idx][1]
    return str(raw).strip()


def build_generate_prompt(domain: Dict[str, str]) -> str:
    """根据银行金融科技领域定义构建关键词生成 Prompt。

    每个词汇须附一条「入选理由」，从与判别端共享的 3 条正向判据 POSITIVE_REASONS
    (score=1) 中三选一 —— 在生成端即以同一套「银行 ∩ 金融科技」正向判据自我锚定，压制裸
    技术词（AI/云计算/大数据…）误报，与 build_judge_prompt 准入判据同源锁步。理由输出为
    **序号**（0-2 的整数，即 POSITIVE_REASONS 的 0-index 下标，非理由全文，省 token 抗截断）；
    理由仅作生成端约束（CoT 自我判据），不落盘；下游 fetch_batch 从对象数组只提取
    "keyword" 字段（并向后兼容旧的纯字符串列表），故 reason 是序号还是全文对下游无影响。
    """
    reason_menu = "\n".join(f"  {i}. \"{r}\"" for i, r in enumerate(POSITIVE_REASONS))
    return (
        f"请生成一个包含**200个**中文专业词汇的\"{domain['name']}\"词典。\n"
        f"参考词汇：{domain['description']}\n"
        f"要求：每个词汇应确保简洁、准确且意义明确，涵盖\"{domain['name']}\"的所有领域；"
        f"并为每个词汇提供一条入选理由，理由须从以下 3 项中选取一个，reason 只写其**序号**"
        f"（0-2 的整数，不得写理由全文、改写、合并或新增）：\n"
        f"{reason_menu}\n"
        f"格式：必须严格返回一个JSON对象，Key为\"keywords\"，Value为对象数组，"
        f"数组中每个对象拥有且仅有两个键：\"keyword\"（词汇）与\"reason\"（须为上述序号 0-2 之一的整数）。\n"
        f"示例：{{\"keywords\": ["
        f"{{\"keyword\": \"金融科技\", \"reason\": 0}}, "
        f"{{\"keyword\": \"人工智能\", \"reason\": 1}}, "
        f"{{\"keyword\": \"手机银行\", \"reason\": 2}}]}}"
    )

def build_judge_prompt(keywords_batch: List[str]) -> str:
    """根据银行金融科技领域定义构建批量判别 Prompt。"""
    kw_list_str = "\n".join(f"{i + 1}. {kw}" for i, kw in enumerate(keywords_batch))
    domain_names = "、".join(d['name'] for d in DOMAINS)
    # ══ 六类固定判据直接复用模块级 SSOT REASONS：(代表词, reason, score)。reason 输出为
    #    **序号** 0-5（即 REASONS 的 0-index 下标），score 由所选序号唯一决定（判据句已从
    #    prompt 移除，改由这六个理由承载）。判据本质 = 银行 ∩ 金融科技 两侧俱全 → 1；否则 → 0
    #    （0 侧三类：兜底其余/有科技·无银行/有银行·无科技）。顺序、六象限含义、近因排布与
    #    0:1 平衡的完整说明见 REASONS 定义处注释（勿在此重写字面，防两端漂移）。
    #    ⚠ 序号是输出契约 → REASONS 一旦重排，序号语义随之改变（menu/示例自动同步，无字面漂移）。
    # ⚠ menu 与示例均由 REASONS 用「,\n」.join 生成，末条自动无尾逗号（不再手工维护）；
    #    doubao 非 JSON-mode 靠 prompt 产合法 JSON，_safe_parse_json 是裸 json.loads。
    JUDGE_REASONS = REASONS
    reason_menu = "\n".join(
        f"  {idx}. \"{reason}\" → score={score}"
        for idx, (_kw, reason, score) in enumerate(JUDGE_REASONS)
    )
    example_items = ",\n".join(
        f"  {{\"keyword\": \"{kw}\", \"score\": {score}, \"reason\": {idx}}}"
        for idx, (kw, reason, score) in enumerate(JUDGE_REASONS)
    )
    return (
        f"请逐一判断以下{len(keywords_batch)}个词汇是否属于\"{domain_names}\"领域的专业词汇。\n\n"
        f"词汇列表：\n{kw_list_str}\n\n"
        f"要求：判定属于\"{domain_names}\"（银行与金融科技两侧俱全）返回1，否则返回0。"
        f"每个词汇的 reason 须从以下 6 个固定理由中选取一个，reason 只写其**序号**"
        f"（0-5 的整数，不得写理由全文、改写、合并或新增），score 由所选序号唯一决定：\n"
        f"{reason_menu}\n"
        f"格式：必须严格返回一个JSON对象。包含一个名为'results'的数组，数组中的每个对象拥有且仅有三个键："
        f"'keyword'（要判定的词汇）、'score'（1或0）和'reason'（判定理由的序号，须为上述 0-5 之一的整数）。\n\n"
        f"示例：\n"
        f"{{\"results\": [\n"
        f"{example_items}\n"
        f"]}}"
    )
