"""
48_llm_peer_iv.py — LLM-Peer 动态竞争网络工具变量
============================================================

管线位置:
  40_panel_export_main.py → 步骤 7h-llmpeer
  本模块在 46_network_spillovers.py 之后执行。
  依赖 11_news_bank.py 生成的 co_mentioned_banks 列
  和 llm_vote_tone_* 情感指标。

核心思想:
  从新闻正文中提取同时包含焦点银行与其他银行 (规范名 distinct ≥2 家) 的句子
  → 送 GPT 判断竞争关系 → 构建动态同行网络
  → 等权同行情感均值 (文章级 leave-out) 作为 IV。
  (fix omni-g-llm-peer-08, 2026-06-11: 原文档误称 "加权" — 实现自始为
   等权 .mean(); prompt 的竞争强度排序现经保序去重保留, 供未来秩权重使用。)

学术依据:
  Cao, Y., Chen, L., Tucker, J. W., & Wan, C. (2025). Can generative AI
  help identify peer firms? Review of Accounting Studies, 30(4), 3344-3386.
  https://doi.org/10.1007/s11142-025-09892-6
  → LLM 识别产品市场竞争同行; Peer 数量上限 = 10 (TNIC 标准)

  Hoberg, G., & Phillips, G. (2016). Text-based network industries and
  endogenous product differentiation. Journal of Political Economy, 124(5),
  1423-1465. https://doi.org/10.1086/688176
  → TNIC 方法标准为 "10 closest peers", 本模块遵循此上限

  Manski, C. F. (1993). Identification of endogenous social effects:
  The reflection problem. The Review of Economic Studies, 60(3), 531-542.
  https://doi.org/10.2307/2298123
  → 使用 Lag(Y-1) 规避同期反射问题

  Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate
  financial policy? The Journal of Finance, 69(1), 139-178.
  https://doi.org/10.1111/jofi.12094
  → 同行均值 IV 的局限讨论 (fix omni-g-llm-peer-01, 2026-06-11): L&R 正因
    同行结果均值难以满足排除约束而改用同行特质收益冲击。本模块以
    滞后一期 + 文章级 leave-out (剔除与焦点银行共提的报道) 缓解共享文章
    带来的机械相关; 剩余识别假设 (情感持续性下, 同行 t-1 特质报道冲击
    对焦点银行 t 期结果仅经同行渠道起作用) 须在论文中明确披露。

输出:
  llm_peer_tone_iv_full/ctx/ss: LLM-Peer 等权情感均值 IV (文章级 leave-out; 核心 IV;
                         三轨 full/ctx/ss=银行+金科同句, 各自 just-identified 并排,
                         ⚠ 禁混进同一 over-id Hansen J)
  llm_peer_coverage_iv:  LLM-Peer 等权声量均值 IV (辅助 IV; panel 级均值,
                         未做文章级 leave-out — 共享报道声量的披露项)
  llm_peer_count:        LLM-Peer 网络连通度 (诊断变量; 计全部归一化同行,
                         含不在面板内的在册银行 — 与 tone IV 有效域不同, 见
                         llm_peer_n_effective)
  llm_peer_n_effective:  实际进入 tone IV 均值的面板内同行数 (诊断变量,
                         fix omni-g-llm-peer-08)
  llm_peer_queried:      1 = 该 bank-year LLM 调用+解析成功 (peer 集可为空),
                         区分 '查证后零同行' 与 '未查证' (fix omni-g-llm-peer-07)
"""

import asyncio
import json
import os
import platform
import re
import sys
import time
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

# Phase 5c-1: 注入项目根, 让 ``news_process.core.*`` 在包模式下可解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.caching import LLMCache

# fix(omni-g-llm-peer-06, 2026-06-11): stage 48 接入与 stage 21 相同的离线确定性
# 守卫 — 复用 tone_llms.LLMCacheMissError 保证 except 语义跨 stage 一致;
# tone_llms 不可导入的极端环境 (如 aiohttp 缺失) 用本地同名 fallback 兜底。
try:
    from news_process.pipeline.sentiment.tone_llms import LLMCacheMissError
except Exception:  # pragma: no cover — aiohttp 缺失等极端环境
    class LLMCacheMissError(RuntimeError):
        """fallback: tone_llms 不可导入时的本地同名异常 (语义一致)。"""

# 离线确定性守卫开关 (与 pipeline/sentiment/tone_llms.py L189 完全同语义):
# 设 NEWS_PROCESS_LLM_OFFLINE=1 后, stage 48 缓存 miss 时 raise 而非调付费 API,
# 杜绝 "上游句子/排序微变 → 缓存键漂移 → LLM 重判 → peer 网络静默翻转"。
LLM_OFFLINE = os.environ.get('NEWS_PROCESS_LLM_OFFLINE', '').strip().lower() in (
    '1', 'true', 'yes', 'on',
)

# v3.7.0 (DC3 + C1 + M13 修复): LLM raw response archive 集成 (V4 F-P2.1 critical)
try:
    from news_process.pipeline.llm_archive import archive_record as _llm_archive_record
    _LLM_ARCHIVE_AVAILABLE = True
except ImportError as _archive_import_exc:
    _llm_archive_record = None
    _LLM_ARCHIVE_AVAILABLE = False
    import logging as _logging_for_archive_error
    _logging_for_archive_error.getLogger(__name__).error(
        "CRITICAL v3.7.0: llm_archive 不可用 (%s). Stage 48 (LLM peer IV) "
        "将无归档 — 顶刊复现性 (V4 F-P2.1) 受损.", _archive_import_exc,
    )
from news_process.core.config import load_config
from news_process.core.logging import pct4, setup_logging, sig4

# ============================================================================
# 1. 全局配置
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "48_llm_peer_iv"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 从 config.yaml 的 tone_llm_processing 读取, 与 21_tone_llms.py 完全一致
# 严禁硬编码: 确保项目全局参数一致性
LLM_CONFIG = CONFIG.get('tone_llm_processing', {})
MODELS = LLM_CONFIG.get('models', [])
MAX_CONCURRENCY = max(1, int(LLM_CONFIG.get('max_concurrency', 5)))
TEMPERATURE = LLM_CONFIG.get('temperature', 0.0)
RANDOM_SEED = LLM_CONFIG.get('random_seed', 42)
FORCE_JSON = LLM_CONFIG.get('force_json', True)
# fallback 对齐生产 config (tone_llm_processing.max_retries=80) — 2026-06-23 统一:
# 大模型 API 调用失败一律重试 80 次 (本模块复用 stage 21 同一配置段)。
MAX_RETRIES = LLM_CONFIG.get('max_retries', 80)
RETRY_DELAY = LLM_CONFIG.get('retry_delay', 10)

# fix(log-round4-2026-06-20): 参数回显移入 compute_llm_peer_iv() —— 模块级 emit 会在 stage 45
# 面板构建经 runner import 本模块时触发 setup_logging(delay=True) 首写截断, 覆写
# logs/48_llm_peer_iv.log; 移入函数后仅真正计算 IV 时回显, import 不再截断。


# ============================================================================
# 2. 句子分割正则
# ============================================================================
# 按中文句号、感叹号、问号、分号、换行符分句
SENT_SPLIT = re.compile(r'(?<=[。！？；\n])')


# ============================================================================
# 3. 辅助加载函数
# ============================================================================

def _load_fintech_keywords(fintech_path: str) -> Set[str]:
    """从 fintech_dict.json 加载金融科技关键词集合。

    fintech_dict.json 结构: ["关键词1", "关键词2", ...]
    与 12_news_fintech.py 使用同一份词典, 确保筛选标准一致。

    Args:
        fintech_path: fintech_dict.json 的完整路径
                      (来自 config.yaml paths.fintech_dict_file)

    Returns:
        set[str]: 长度 >= 2 的金融科技关键词集合
    """
    with open(fintech_path, 'r', encoding='utf-8') as f:
        keywords = json.load(f)
    result = set(kw for kw in keywords if isinstance(kw, str) and len(kw) >= 2)
    logger.info(f"  加载金融科技关键词: {len(result)} 个 (来自 {os.path.basename(fintech_path)})")
    return result


def _load_all_bank_names(bank_names_path: str
                         ) -> Tuple[Set[str], List[str], Dict[str, str]]:
    """从 bank_names.json 加载全部银行名+别名, 并构建变体→标准名映射。

    bank_names.json 结构:
      [{"bank_name": "中国工商银行", "variants": ["工商银行", "工行"]}, ...]

    返回三个对象:
      all_names: bank_name 与全部 variants 的并集 (用于句子提取)
      canonical_names: 仅 bank_name 字段 (用于 LLM 输出的模糊匹配)
      variant_to_canonical: {变体: 标准名} 映射
        (用于 _normalize_peer_names 解析 LLM 输出的简称,
         如 '工行' → '中国工商银行', '招行' → '招商银行')

    过滤掉长度 < 2 的简称以减少误匹配。

    Args:
        bank_names_path: bank_names.json 的完整路径
                         (来自 config.yaml paths.bank_names_file)

    Returns:
        (all_names, canonical_names, variant_to_canonical)
    """
    with open(bank_names_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    all_names = set()
    canonical_names = []
    variant_to_canonical: Dict[str, str] = {}
    for entry in data:
        if isinstance(entry, dict):
            bn = entry.get('bank_name', '')
            if bn and len(bn) >= 2:
                all_names.add(bn)
                canonical_names.append(bn)
                variant_to_canonical[bn] = bn  # 标准名也映射到自身
            for v in entry.get('variants', []):
                if isinstance(v, str) and len(v) >= 2:
                    all_names.add(v)
                    variant_to_canonical[v] = bn  # 变体映射到标准名
    logger.info(f"  加载银行名: {len(canonical_names)} 家 (标准名), "
                f"{len(all_names)} 个 (含变体), "
                f"{len(variant_to_canonical)} 条变体映射")
    return all_names, canonical_names, variant_to_canonical


# ============================================================================
# 4. 句子双重筛选提取
# ============================================================================

def _extract_multi_bank_sentences(df_bank_year: pd.DataFrame,
                                   all_bank_names: Set[str],
                                   fintech_keywords: Set[str],
                                   variant_to_canonical: Dict[str, str],
                                   focal_bank: str,
                                   max_sents: int = 5000) -> List[str]:
    """从该银行某年文章中提取同时满足两个条件的句子。

    条件 1 (fix omni-g-llm-peer-02/03, 2026-06-11): 句中命中的银行名先经
      variant → canonical 归一, 再要求 distinct 规范银行 ≥2 家, 且规范银行集
      必须包含焦点银行本身:
      (a) 修变体子串双计 — 如 '中国工商银行' 一个实体同时命中变体 '工商银行',
          旧实现把单行句伪装成 '≥2 银行' 比较句 (盘上实测 ~20% 过筛句仅 1 家);
      (b) 修 PEER_PROMPT 虚假前提 — prompt 向 LLM 断言句子 '同时提及
          【焦点银行】和其他银行', 旧实现 ~46% 过筛句根本不含焦点银行,
          诱导 LLM 把无关银行判为焦点行竞争对手。
    条件 2: 包含 ≥1 个金融科技关键词 (来自 fintech_dict.json)

    双重筛选确保送入 LLM 的句子既涉及焦点银行与其他银行的真实比较,
    又聚焦于金融科技领域, 最大化信号纯度。

    流程:
      1. 筛选 co_mentioned_banks 非空的文章 (预筛)
      2. 标题+正文拼接后按 。！？；\\n 分句
      3. 逐句检查: 规范银行集含焦点银行 且 distinct ≥2 且 含 ≥1 金融科技关键词
      4. 去重 + 截断至 max_sents 条

    Token 预算:
      GPT-5.4-nano 上下文窗口: 400,000 tokens
      增加金融科技关键词条件后, 实际句子数会进一步减少,
      token 消耗更加可控。设 5000 实质等于不限制。

    注意: 此处使用简单子串匹配 (非 AC 自动机), 可能有少量
    误匹配 (如 "中国银行业" 匹配到 "中国银行")。
    这是可接受的——此步骤仅为预筛, LLM 会在语义层进一步过滤。

    Args:
        df_bank_year: 该银行某年全部文章
        all_bank_names: set, 全部银行名+别名 (bank_names.json)
        fintech_keywords: set, 金融科技关键词 (fintech_dict.json)
        variant_to_canonical: {变体: 标准名} 映射 (来自 _load_all_bank_names)
        focal_bank: 焦点银行 (panel target_bank, 即 bank_names.json 规范名)
        max_sents: 最大返回句数 (默认 5000, 实质不限制)

    Returns:
        list[str]: 去重后满足双重条件的句子
    """
    # co_mentioned_banks 由 11_news_bank.py 生成, 格式为分号分隔字符串
    # (如 "工商银行;建设银行"), 空字符串表示无共提银行
    # 只要存在共提银行, 文章中就可能有含 2+ 银行名的句子
    mask = df_bank_year['co_mentioned_banks'].apply(
        lambda x: isinstance(x, str) and len(x.strip()) > 0)
    df_co = df_bank_year[mask]

    # 焦点银行规范名 (target_bank 本就是规范名, 经映射兜底变体输入)
    focal_canon = variant_to_canonical.get(focal_bank, focal_bank)

    sentences = []
    for _, row in df_co.iterrows():
        title = str(row.get('标题', '')).strip()
        content = str(row.get('内容', '')).strip()
        full = title + '。' + content

        for sent in SENT_SPLIT.split(full):
            sent = sent.strip()
            if len(sent) < 10:
                continue
            # 检查条件 1: 规范化后 ≥2 家不同银行 且 含焦点银行
            banks_found = set()
            for name in all_bank_names:
                if len(name) >= 2 and name in sent:
                    banks_found.add(name)
            # fix(omni-g-llm-peer-02, 2026-06-11): 变体 → canonical 归一后再数
            # distinct, 防 '中国工商银行'⊃'工商银行' 同实体双计击穿 ≥2 契约
            canon_found = {variant_to_canonical.get(n, n) for n in banks_found}
            if len(canon_found) < 2:
                continue
            # fix(omni-g-llm-peer-03, 2026-06-11): 焦点银行必须在句中 —
            # 与 PEER_PROMPT '同时提及【{bank_name}】和其他银行' 前提对齐
            if focal_canon not in canon_found:
                continue
            # 检查条件 2: ≥1 个金融科技关键词
            has_fintech = any(kw in sent for kw in fintech_keywords)
            if has_fintech:
                sentences.append(sent)

    # 去重
    seen = set()
    unique = []
    for s in sentences:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return unique[:max_sents]


# ============================================================================
# 5. Prompt 模板
# ============================================================================
# Peer 数量 = 10: Hoberg & Phillips (2016, JPE) TNIC 方法标准为 "10 closest
# peers", Cao et al. (2025, RAS) 以此为基准评估 LLM peer 质量。

PEER_PROMPT = """你是一位中国银行业金融科技分析师。以下是 {year} 年媒体报道中
同时提及【{bank_name}】和其他银行的句子。请基于这些报道，
识别在金融科技领域与【{bank_name}】构成产品市场竞争关系的银行。

判断标准：
- 报道中被描述为金融科技领域的直接竞争者、对标对象或业务重叠方
- 在相似金融科技细分领域（如数字支付、智能风控、开放银行等）有可比业务布局
- 排除仅因行业排名、宏观综述或非金融科技业务而并列提及的银行

句子：
{numbered_sentences}

仅输出 JSON: {{"peers": ["银行A全称", "银行B全称", ...]}}
最多 10 家，按竞争强度排列。无法判断则 {{"peers": []}}。"""

# Plan-r3 P3-17 接入: PEER_PROMPT 是模块内联常量 (不经 config/prompts/),
# 任何对此字符串的修改必须同步 bump 此版本号, 让既有 LLMCache 自动失效.
PEER_PROMPT_VERSION = "v1-2026-05-13"


# ============================================================================
# 6. LLM API 调用
# ============================================================================

async def _call_llm_peer(session, semaphore, bank: str, year: int,
                          sentences: List[str], model_cfg: dict,
                          cache: Optional[LLMCache]) -> Tuple[str, int, Optional[str]]:
    """调用 GPT 识别竞争对手, 含重试和缓存 (复用 21_tone_llms.py 模式)。

    全部推理参数 (temperature, seed, force_json, retries, delay)
    从 config.yaml 统一读取, 与 21_tone_llms.py 保持严格一致。

    Args:
        session: aiohttp.ClientSession
        semaphore: asyncio.Semaphore, 并发控制
        bank: 目标银行名
        year: 年份
        sentences: 筛选后的句子列表
        model_cfg: 模型配置字典 (含 model_name, api_key, base_url)
        cache: LLMCache 实例, 用于持久化缓存

    Returns:
        (bank, year, result_json_str or None)
    """
    model_id = model_cfg['model_name']
    prompt = PEER_PROMPT.format(
        bank_name=bank, year=year,
        numbered_sentences='\n'.join(f'{i+1}. {s}' for i, s in enumerate(sentences))
    )

    # 查询 LLMCache (SQLite 持久化缓存)
    # audit S2 修复: 缓存键纳入 temperature/random_seed 维度 (temp=0.0 时不变)。
    if cache is not None:
        cached = cache.get(model_id, prompt, prompt_version=PEER_PROMPT_VERSION,
                           temperature=TEMPERATURE, random_seed=RANDOM_SEED)
        if cached:
            return bank, year, cached

    # fix(omni-g-llm-peer-06, 2026-06-11): 离线确定性守卫 (与 stage 21 同模式) —
    # NEWS_PROCESS_LLM_OFFLINE=1 下缓存 miss 即 raise, 严禁静默调付费 API
    # (peer 网络列入 golden panel, miss → 重判可翻转 peer 集 → golden 漂移)。
    if LLM_OFFLINE:
        raise LLMCacheMissError(
            f"[Peer-IV offline] 缓存 miss: bank={bank}, year={year}, "
            f"model={model_id}, prompt_version={PEER_PROMPT_VERSION} — "
            f"NEWS_PROCESS_LLM_OFFLINE=1 下禁止调用付费 API; "
            f"请在线回填缓存或检查句子筛选/语料是否相对 golden 漂移"
        )

    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {model_cfg['api_key']}"}
    payload = {
        "model": model_cfg['model_name'],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE,
        "seed": RANDOM_SEED,
    }
    if FORCE_JSON:
        payload["response_format"] = {"type": "json_object"}

    req_timeout = aiohttp.ClientTimeout(total=LLM_CONFIG.get('timeout', 600))
    async with semaphore:
        for attempt in range(MAX_RETRIES):
            try:
                async with session.post(
                    f"{model_cfg['base_url']}/chat/completions",
                    json=payload, headers=headers,
                    timeout=req_timeout
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        result = data['choices'][0]['message']['content']
                        # 写入 LLMCache (SQLite 持久化缓存)
                        if cache is not None:
                            cache.put(model_id, prompt, result,
                                      prompt_version=PEER_PROMPT_VERSION,
                                      temperature=TEMPERATURE,
                                      random_seed=RANDOM_SEED)
                        # v3.7.0 (C1): LLM 原始响应永久归档 (V4 F-P2.1 复现性要求)
                        if _LLM_ARCHIVE_AVAILABLE:
                            try:
                                _llm_archive_record(
                                    cache_key=LLMCache.make_key(
                                        model_id, prompt,
                                        prompt_version=PEER_PROMPT_VERSION,
                                        temperature=TEMPERATURE,
                                        random_seed=RANDOM_SEED,
                                    ),
                                    model_id=model_id,
                                    model_version=data.get('model', model_id),
                                    prompt=prompt,
                                    response_raw=json.dumps(data, ensure_ascii=False),
                                    prompt_version=PEER_PROMPT_VERSION,
                                    temperature=TEMPERATURE,
                                    api_endpoint=f"{model_cfg['base_url']}/chat/completions",
                                    http_status=resp.status,
                                )
                            except Exception as _arch_exc:
                                logger.warning(
                                    f"LLM archive 失败 (不阻塞 pipeline): {_arch_exc!r}"
                                )
                        return bank, year, result
                    elif resp.status in (429, 500, 502, 503, 504):
                        logger.warning(f"[Peer-IV] {bank}_{year} HTTP {resp.status}, "
                                       f"重试 {attempt+1}/{MAX_RETRIES}")
                        await asyncio.sleep(RETRY_DELAY)
                    else:
                        body = await resp.text()
                        logger.error(f"[Peer-IV] {bank}_{year} HTTP {resp.status}: "
                                     f"{body[:200]}")
                        break
            except asyncio.TimeoutError:
                logger.warning(f"[Peer-IV] {bank}_{year} 超时, "
                               f"重试 {attempt+1}/{MAX_RETRIES}")
                await asyncio.sleep(RETRY_DELAY)
            except Exception as e:
                logger.warning(f"[Peer-IV] {bank}_{year} 异常 ({e}), "
                               f"重试 {attempt+1}/{MAX_RETRIES}")
                await asyncio.sleep(RETRY_DELAY)
        return bank, year, None  # 全部重试失败


# ============================================================================
# 7. 模糊匹配标准化
# ============================================================================

def _normalize_peer_names(raw_peers: List[str],
                           canonical_names: List[str],
                           variant_to_canonical: Optional[Dict[str, str]] = None,
                           cutoff: float = 0.8
                           ) -> List[str]:
    """将 LLM 输出的银行名匹配至 bank_names.json 标准名。

    匹配策略 (优先级递减):
      1. 精确匹配: raw == canonical
      2. 变体映射: raw ∈ variant_to_canonical (bank_names.json 的 variants)
         → 处理 LLM 输出简称如 '工行' → '中国工商银行',
           '招行' → '招商银行' 等 2 字符缩写
      3. 子串包含 (最小长度 3, fix omni-g-llm-peer-04 歧义守卫):
         仅当唯一命中 1 家规范名时接受 (处理 LLM 返回
         '中国工商银行股份有限公司' 而标准名为 '中国工商银行' 的情况);
         命中 >1 家 (如行业泛称 '农村商业银行' ⊂ 1558 个规范名, 旧实现
         max(key=len) 任取一家) 视为歧义泛称, 直接拒绝。
      4. OOV 拒绝 (fix omni-g-llm-peer-04, 2026-06-11): 原 difflib.get_close_matches
         兜底已移除 — 不在 bank_names.json 的名称 (如政策性银行
         '中国农业发展银行', difflib ratio=0.857 ≥ 0.8 曾被错配为
         '中国农业银行') 一律丢弃并记录, 不再吸附到最相近的在册银行。

    Args:
        raw_peers: LLM 输出的银行名列表
        canonical_names: bank_names.json 中的标准 bank_name 列表
        variant_to_canonical: {变体: 标准名} 映射 (来自 bank_names.json)
            → 用于解析 '工行'/'招行' 等 2 字符简称
        cutoff: (inert since fix omni-g-llm-peer-04) 原 difflib 串匹配严格度;
            策略 4 改为 OOV 拒绝后本参数不再影响归一化结果, 仅为五档
            cutoff 扫描调用兼容保留 — 五档列结构性相同, 见
            omni-g-llm-peer-05 disclosure (compute_llm_peer_iv 步骤 5)。

    Returns:
        list[str]: 保序去重后的标准银行名列表 (fix omni-g-llm-peer-09:
        list(set()) → dict.fromkeys 保留 LLM 的竞争强度排序, 未来 top-N
        截断/秩权重不再受 hash 序漂移影响)
    """
    canonical_set = set(canonical_names)  # O(1) 查找优化 (银行数 ~200+)
    normalized = []
    rejected: List[str] = []
    for name in raw_peers:
        name = name.strip()
        if not name:
            continue
        # 策略 1: 精确匹配 (使用 set 实现 O(1) 复杂度)
        if name in canonical_set:
            normalized.append(name)
            continue
        # 策略 2: 变体映射 (处理 '工行'/'招行' 等简称)
        if variant_to_canonical and name in variant_to_canonical:
            normalized.append(variant_to_canonical[name])
            continue
        # 策略 3: 子串包含 — fix(omni-g-llm-peer-04, 2026-06-11): 唯一命中才接受,
        # 命中 >1 家规范名 = 行业泛称/歧义 (如 '农村商业银行'), 拒绝
        # 最小长度 3: 防止 '中国'/'银行' 等过短非银行名片段误匹配
        if len(name) >= 3:
            substr_matches = {cn for cn in canonical_names
                              if cn in name or name in cn}
            if len(substr_matches) == 1:
                normalized.append(next(iter(substr_matches)))
                continue
            if len(substr_matches) > 1:
                rejected.append(name)
                continue
        # 策略 4: OOV 拒绝 — fix(omni-g-llm-peer-04, 2026-06-11): 词典外名称丢弃,
        # 不再用 difflib.get_close_matches(cutoff) 吸附 (原 cutoff=0.8 错配实证见
        # docstring); '命名勘误' 注释 (compute 步骤 6) 中 difflib cutoff 语义随之失效
        rejected.append(name)
    if rejected:
        logger.debug(f"  [peer 归一化] 拒绝 {len(rejected)} 个 OOV/歧义泛称名称: "
                     f"{rejected[:5]}")
    # fix(omni-g-llm-peer-09, 2026-06-11): dict.fromkeys 保序去重 (替代 list(set()))
    # — 保留 PEER_PROMPT '按竞争强度排列' 的输出序, 当前消费点序无关故盘上值零变化
    return list(dict.fromkeys(normalized))


# ============================================================================
# 8. 缓存管理
# ============================================================================

def _load_peer_cache(cache_path: str) -> dict:
    """加载 LLM-Peer 缓存。"""
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"  缓存加载失败 ({e}), 使用空缓存")
    return {}


def _save_peer_cache(cache: dict, cache_path: str):
    """保存 LLM-Peer 缓存。"""
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    logger.info(f"  缓存已保存: {len(cache)} 条 → {cache_path}")


# ============================================================================
# 8b. 文章级 leave-out 情感索引 (fix omni-g-llm-peer-01)
# ============================================================================

def _build_article_tone_index(df_exploded: pd.DataFrame,
                              tone_cols: List[str]) -> Dict[tuple, tuple]:
    """预聚合文章级情感索引: (target_bank, year) → (co_sets, {col: 值列表})。

    fix(omni-g-llm-peer-01, 2026-06-11): 为 peer 情感的文章级 leave-out 服务。
    news_bank.py 的 explode 使同一篇共提文章同时进入焦点银行 i 与同行 j 双方的
    bank-year 情感聚合 — peer j 的 panel 级均值机械嵌入 i 自身报道的情感。
    本索引保留每篇文章的 co_mentioned_banks 规范名集合, 让 IV 构建时能按
    (i, j) 对剔除共提文章 ($0, 无新 LLM 调用)。

    Returns:
        {(bank, year): (co_sets, tone_lists)} —
        co_sets[k] = 第 k 篇文章的共提银行集合;
        tone_lists[col][k] = 第 k 篇文章的情感值 (缺失 → None)。
    """
    index: Dict[tuple, tuple] = {}
    cols = ['target_bank', 'year', 'co_mentioned_banks'] + list(tone_cols)
    sub = df_exploded[cols]
    for (b, y), g in sub.groupby(['target_bank', 'year'], sort=False):
        co_sets = []
        for x in g['co_mentioned_banks']:
            if isinstance(x, str) and x.strip():
                co_sets.append({s for s in x.split(';') if s})
            else:
                co_sets.append(set())
        tone_lists = {
            c: [float(v) if pd.notna(v) else None for v in g[c].tolist()]
            for c in tone_cols
        }
        index[(b, int(y))] = (co_sets, tone_lists)
    return index


def _peer_leave_out_tone_mean(art_index: Dict[tuple, tuple],
                              peer: str, lag_year: int, tone_col: str,
                              exclude_bank: str) -> Optional[float]:
    """peer 在 lag_year 的文章级情感均值, 排除与 exclude_bank 共提的文章。

    fix(omni-g-llm-peer-01, 2026-06-11): leave-out 均值 — 无共提文章时
    与 panel 级均值等价 (encode.py L506 同为 plain mean), 有共提文章时
    剔除焦点银行自身 t-1 报道的情感, 修复 IV 排除约束的机械违背。
    """
    entry = art_index.get((peer, int(lag_year)))
    if entry is None:
        return None
    co_sets, tone_lists = entry
    vals = [v for cs, v in zip(co_sets, tone_lists.get(tone_col, []))
            if v is not None and exclude_bank not in cs]
    if not vals:
        return None
    return sum(vals) / len(vals)


# ============================================================================
# 9. 日志富集: 环境 / 方法论 (2026-06-24)
# ============================================================================

def _log_environment_and_methodology(panel: pd.DataFrame,
                                      df_exploded: pd.DataFrame,
                                      cache_db: str) -> None:
    """打印项目/环境信息 + 方法论引文 (日志富集, golden-safe)。

    本模块经 runner import 调用 (无独立 main), 但有自己的日志文件
    ``logs/48_llm_peer_iv.log``, 故在计算入口处补打 tone_words.py 金标准的
    ① 项目/环境指纹 ② 输入/输出 ③ 方法论依据(含 DOI) 三块 (CONFIG 块已由
    compute_llm_peer_iv 入口的参数回显覆盖)。纯 logger.* 输出, 不改任何
    产物/schema/控制流。引文逐字取自经核验参考文献注册表。
    """
    try:
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (LLM-Peer 动态竞争网络工具变量; "
                    "panel 步骤 7h-llmpeer, 经 runner 调用)")
        logger.info("     · 项目: news_process 研究数据流水线 "
                    "(中文银行/金科新闻 → 计量面板) | 版本 v3.11.1")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    f"aiohttp={'已装' if HAS_AIOHTTP else '缺失'}")
        logger.info(f"     · 成本/确定性: LLM_OFFLINE={LLM_OFFLINE} "
                    f"({'缓存全命中→$0 离线确定性复现' if LLM_OFFLINE else '缓存 miss 时调付费 API'}); "
                    "确定性锚点=_llm_cache.db (勿删)")

        logger.info("  📂 输入 / 输出")
        logger.info(f"     · 输入面板: {len(panel):,} 行 × {panel.shape[1]:,} 列 "
                    "(in-memory, 来自 runner panel 构建链)")
        logger.info(f"     · 输入文章级: df_exploded {len(df_exploded):,} 行 × "
                    f"{df_exploded.shape[1]:,} 列 (文章级 leave-out 数据源)")
        logger.info(f"     · LLM 缓存 DB: {cache_db}")
        logger.info("     · 输出: 就地为 panel 追加 llm_peer_tone_iv_full/ctx/ss + "
                    "coverage_iv + count + n_effective + queried + 五档 cutoff 列")

        logger.info("  📖 方法论依据 (参考文献逐字取自经核验注册表)")
        logger.info("     · LLM 识别竞争同行 (Peer ≤10, TNIC 标准): Cao, Y., Chen, L., "
                    "Tucker, J. W., & Wan, C. (2025). Can generative AI help identify "
                    "peer firms? Review of Accounting Studies, 30(4), 3344-3386. "
                    "https://doi.org/10.1007/s11142-025-09892-6")
        logger.info("     · TNIC '10 closest peers' 上限: Hoberg, G., & Phillips, G. "
                    "(2016). Text-based network industries and endogenous product "
                    "differentiation. Journal of Political Economy, 124(5), 1423-1465. "
                    "https://doi.org/10.1086/688176")
        logger.info("     · 滞后一期规避反射问题: Manski, C. F. (1993). Identification "
                    "of endogenous social effects: The reflection problem. The Review "
                    "of Economic Studies, 60(3), 531-542. "
                    "https://doi.org/10.2307/2298123")
        logger.info("     · 同行均值 IV 排除约束讨论 (→ 改文章级 leave-out): Leary, M. T., "
                    "& Roberts, M. R. (2014). Do peer firms affect corporate financial "
                    "policy? The Journal of Finance, 69(1), 139-178. "
                    "https://doi.org/10.1111/jofi.12094")
        logger.info("     → 白话: 用大模型从新闻里认出『谁跟谁是竞争对手』搭出动态同行网, "
                    "再取同行去年的情感均值(剔除共提报道)当工具变量; 滞后+leave-out 是为了"
                    "让这个工具变量满足『只经同行渠道影响焦点银行』的识别假设。")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/方法论信息打印失败 (不影响计算): {e}")


# ============================================================================
# 10. 主函数
# ============================================================================

def compute_llm_peer_iv(panel: pd.DataFrame,
                         df_exploded: pd.DataFrame) -> pd.DataFrame:
    """基于 LLM 语义判断的动态竞争网络工具变量。

    fix(omni 2026-06-11) 语义变更披露: tone IV 改文章级 leave-out 等权均值
    (剔除与焦点银行共提的 t-1 报道, g-llm-peer-01); 句子筛选要求规范化后
    ≥2 家不同银行且含焦点银行 (g-llm-peer-02/03, 改变 LLM 输入 → 缓存键);
    LLM 判 '零同行' 显式写 count=0 并加 llm_peer_queried 旗标 (g-llm-peer-07);
    新增 llm_peer_n_effective 诊断列 (g-llm-peer-08)。

    完整流程:
      1. 加载银行名 + 金融科技关键词
      2. 按银行×年份提取双重筛选句子 (规范银行 ≥2 家 + 含焦点银行 + fintech 词)
      3. 调用 LLM 识别竞争同行 (异步并发; NEWS_PROCESS_LLM_OFFLINE=1 时
         缓存 miss → raise LLMCacheMissError, 不调付费 API)
      4. 名称标准化 (精确/变体/唯一子串; 泛称歧义与 OOV 拒绝) → 构建 peer_map
      5. 滞后一期 + 文章级 leave-out:
         tone IV = mean_j [ mean(tone_{j 文章, t-1, 排除共提 i 的文章}) ]
         (coverage IV 仍为 panel 级均值, 未做 leave-out — 披露项)

    方法论:
      - 句子双重筛选: 规范银行 ≥2 家 (含焦点银行) + fintech 关键词
      - LLM 判断: temperature=0, seed=42, JSON 输出
      - 滞后一期规避 Manski (1993) 反射问题; 文章级 leave-out 缓解
        共享文章机械相关 (Leary & Roberts 2014 排除约束讨论, 见模块头)
      - Peer 数量上限 = 10 (Hoberg & Phillips 2016 TNIC 标准, prompt 软约束)

    Args:
        panel: 银行-年份面板 DataFrame
        df_exploded: 文章级 DataFrame (含 llm_vote_score_full/_ctx/_ss 时启用
            文章级 leave-out; 缺失时回退 panel 级均值并 loud 披露)

    Returns:
        panel: 追加 llm_peer_tone_iv_full/_ctx/_ss, llm_peer_coverage_iv,
               llm_peer_count, llm_peer_n_effective, llm_peer_queried
               (及五档 cutoff 后缀列) 的面板。三轨 (full/ctx/ss) 并排各自
               just-identified, ⚠ 禁混进同一 over-id Hansen J。

    References:
        Cao, Y. et al. (2025). RAS, 30(4), 3344-3386.
        Hoberg, G., & Phillips, G. (2016). JPE, 124(5), 1423-1465.
        Manski, C. F. (1993). RES, 60(3), 531-542.
        Leary, M. T., & Roberts, M. R. (2014). JF, 69(1), 139-178.
    """
    _stage_start = time.time()
    # 运行期阶段计时累计 (各主要子阶段墙钟耗时, 末尾汇总; 纯日志, golden-safe)
    _phase_durations: dict[str, float] = {}

    logger.info("=" * 60)
    logger.info("LLM-Peer 动态竞争网络 IV (Cao et al. 2025)")
    logger.info("=" * 60)
    logger.info(f"  ⚙ 运行配置: temperature={sig4(TEMPERATURE)}, seed={RANDOM_SEED}, "
                f"force_json={FORCE_JSON}, models_used=1 (仅 MODELS[0], 配置共 {len(MODELS)}), "
                f"concurrency={MAX_CONCURRENCY}, "
                f"retries={MAX_RETRIES}, delay={sig4(RETRY_DELAY)}s (flat sleep, 非 stage21 指数退避)")

    if not HAS_AIOHTTP:
        logger.error("  aiohttp 未安装, 无法进行 LLM-Peer IV 计算")
        return panel

    if not MODELS:
        logger.error("  config.yaml 中无可用 LLM 模型配置")
        return panel

    tone_col = 'llm_vote_tone_full'
    coverage_col = 'ln_news_coverage'

    if tone_col not in panel.columns:
        logger.warning(f"  {tone_col} 不存在, 跳过 LLM-Peer IV")
        return panel

    # 列存在性守卫: co_mentioned_banks 由 11_news_bank.py 生成,
    # 是句子双重筛选的前提条件 (与 46_network_spillovers.py L199-200 一致)
    if 'co_mentioned_banks' not in df_exploded.columns:
        logger.warning("  co_mentioned_banks 列不存在, 跳过 LLM-Peer IV")
        return panel

    # ── 1. 加载配置 (使用 config.yaml 中的精确文件路径) ──
    bank_names_path = CONFIG['paths'].get(
        'bank_names_file',
        os.path.join(os.path.dirname(__file__), 'config', 'bank_names.json'))
    fintech_dict_path = CONFIG['paths'].get(
        'fintech_dict_file',
        os.path.join(os.path.dirname(__file__), 'config', 'fintech_dict.json'))
    all_bank_names, canonical_names, variant_to_canonical = _load_all_bank_names(
        bank_names_path)
    fintech_keywords = _load_fintech_keywords(fintech_dict_path)

    # ── 2. 初始化 LLMCache (SQLite 持久化缓存) ──
    cache_db = os.path.join(CONFIG["paths"]["output_dir"], '_llm_cache.db')
    cache = LLMCache(cache_db)
    logger.info(f"  LLM 缓存: {cache.size():,} 条已缓存, 路径: {cache_db}")

    # 项目/环境信息 + 方法论引文 (日志富集 2026-06-24; 纯日志, golden-safe)
    _log_environment_and_methodology(panel, df_exploded, cache_db)
    _phase_durations['①加载词典+银行名+缓存'] = time.time() - _stage_start

    # ── 3. 按银行×年份提取句子 + LLM 调用 ──
    _t_extract = time.time()
    banks = sorted(panel['target_bank'].unique())
    years = sorted(panel['year'].unique())
    model_cfg = MODELS[0]  # 使用第一个模型

    # 收集需要调用的任务（所有任务，缓存查询在 _call_llm_peer 内部进行）
    tasks_to_call = []
    for bank in banks:
        for year in years:
            df_by = df_exploded[
                (df_exploded['target_bank'] == bank) &
                (df_exploded['year'] == year)
            ]
            if df_by.empty:
                continue

            # fix(omni-g-llm-peer-02/03, 2026-06-11): 传 variant_to_canonical
            # (规范化去双计) + focal_bank=bank (焦点银行必须在句中)
            sents = _extract_multi_bank_sentences(
                df_by, all_bank_names, fintech_keywords,
                variant_to_canonical, bank)
            if not sents:
                logger.info(f"  {bank} {year}: 无符合条件的句子, 跳过")
                continue

            tasks_to_call.append((bank, year, sents))

    logger.info(f"  需调用 LLM: {len(tasks_to_call):,} 对 (银行×年份), "
                f"全集 {len(banks):,} 银行 × {len(years):,} 年")
    _phase_durations['②句子双重筛选'] = time.time() - _t_extract

    # ── 4. 异步并发调用 ──
    _t_llm = time.time()
    raw_results = []
    if tasks_to_call:
        async def _run_all():
            semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
            connector = aiohttp.TCPConnector(limit=MAX_CONCURRENCY)
            async with aiohttp.ClientSession(connector=connector) as session:
                coros = [
                    _call_llm_peer(session, semaphore, bank, year, sents,
                                    model_cfg, cache)
                    for bank, year, sents in tasks_to_call
                ]
                results = await asyncio.gather(*coros, return_exceptions=True)
            return results

        raw_results = asyncio.run(_run_all())

        n_success = 0
        n_fail = 0
        for r in raw_results:
            if isinstance(r, LLMCacheMissError):
                # fix(omni-g-llm-peer-06, 2026-06-11): gather(return_exceptions=True)
                # 会把离线守卫的 raise 包成结果项 — 此处显式重抛, 镜像 tone_llms
                # as_completed 路径的立即 loud-fail 语义。若吞成普通失败日志,
                # 离线确定性守卫将静默失效 (peer 网络以残缺结果继续构建)。
                # raise 发生在 session.post 之前, $0 零网络已由 _call_llm_peer 保证。
                raise r
            if isinstance(r, Exception):
                n_fail += 1
                logger.error(f"  LLM 调用异常: {r}")
            elif r[2] is not None:
                n_success += 1
            else:
                n_fail += 1

        logger.info(f"  LLM 调用完成: 成功={n_success:,}, 失败={n_fail:,} "
                    f"(成功率 {pct4(n_success / (n_success + n_fail)) if (n_success + n_fail) else 'n/a'})")
    _phase_durations['③LLM 调用/缓存'] = time.time() - _t_llm

    # ── 5. 解析结果 → peer_map ──
    _t_parse = time.time()
    # disclosure(omni-g-llm-peer-05, 2026-06-11): cutoff 五档 (0.70..0.90) 原仅
    # 作用于已移除的策略 4 difflib 兜底; 策略 1-3 (精确/变体/唯一子串) 与 cutoff
    # 无关 → 五档后缀列结构性逐位相同 (盘上实证: nonnull 数与 mean 五档全同)。
    # 五档列保留仅为 Stata schema 兼容 (derivative_replication.py CUTOFF_VARS
    # 消费); 论文表注必须披露该灵敏度维度无识别变差, 真正有识别力的稳健性维度
    # (max peers 上限 / 单模型 vs 多模型 / 句子口径) 须另行扫描。
    cutoffs = [0.70, 0.75, 0.80, 0.85, 0.90]
    peer_maps = {c: {} for c in cutoffs}
    # fix(omni-g-llm-peer-07, 2026-06-11): 记录 '已查证' bank-year (LLM 调用 +
    # JSON 解析成功, peers 可为空) — 让 affirmative 零同行与未查证可区分
    queried_keys: Set[str] = set()

    # 从 raw_results 解析 peer_map
    for r in raw_results:
        if isinstance(r, Exception) or r[2] is None:
            continue
        bank, year, raw_json = r
        try:
            # 与 21_tone_llms.py parse_json_response 保持一致:
            # 自动去除 markdown 代码块包围 (```json ... ```)
            _raw = raw_json if isinstance(raw_json, str) else json.dumps(raw_json)
            _raw = _raw.strip()
            if _raw.startswith("```json"):
                _raw = _raw[7:]
            if _raw.startswith("```"):
                _raw = _raw[3:]
            if _raw.endswith("```"):
                _raw = _raw[:-3]
            parsed = json.loads(_raw.strip())
            raw_peers = parsed.get('peers', [])
            # fix(omni-g-llm-peer-07): 解析成功即标记已查证 (含 {"peers": []})
            queried_keys.add(f"{bank}_{year}")
            if raw_peers:
                # 使用从 raw_results 解析出的 bank 和 year 构建 key
                for c in cutoffs:
                    normalized = _normalize_peer_names(
                        raw_peers, canonical_names, variant_to_canonical, cutoff=c)
                    # 排除自身
                    normalized = [p for p in normalized if p != bank]
                    if normalized:
                        peer_maps[c][f"{bank}_{year}"] = normalized
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"  解析失败 ({bank}_{year}): {e}")

    # 关闭 LLMCache
    cache.close()

    for c in cutoffs:
        logger.info(f"  Peer 网络 (cutoff={sig4(c)}): {len(peer_maps[c]):,} 对有效 (银行×年份)")
    _phase_durations['④解析 peer_map'] = time.time() - _t_parse

    # ── 6. IV 构建 (滞后一期 + 文章级 leave-out) ──
    _t_build = time.time()
    # fix(omni-g-llm-peer-01, 2026-06-11): tone IV 改两层等权均值 —
    #   外层: 对 peers 等权; 内层: 每个 peer j 取其 t-1 文章级情感均值,
    #   剔除 co_mentioned_banks 含焦点银行 i 的共提文章 (leave-out)。
    # news_bank explode 使共提文章同入 i/j 双方 bank-year 聚合, 旧 panel 级
    # 均值机械嵌入 i 自身 t-1 报道情感, 违背 IV 排除约束 (见模块头 L&R 段)。
    # coverage IV 保持 panel 级均值 (无文章级 leave-out, 模块头已披露)。
    _ART_TONE_BY_TRACK = {
        'full': 'llm_vote_score_full',  # 文章级列, 聚合后即 panel llm_vote_tone_full
        'ctx': 'llm_vote_score_ctx',
        # 第三轨 ss (银行+金科同句): content_ss 的文章级 LLM 投票分, 聚合后即
        # panel llm_vote_tone_ss; 镜像 ctx 键 (stage 21 ss 轨产 llm_vote_score_ss)。
        'ss': 'llm_vote_score_ss',
    }
    art_tone_cols = [c for c in _ART_TONE_BY_TRACK.values()
                     if c in df_exploded.columns]
    art_index = (_build_article_tone_index(df_exploded, art_tone_cols)
                 if art_tone_cols else {})
    if 'llm_vote_score_full' not in df_exploded.columns:
        # loud 披露: 回退旧 panel 级口径 (无 leave-out, 含共提文章机械相关)
        logger.warning(
            "  [leave-out 回退] df_exploded 缺 llm_vote_score_full — "
            "llm_peer_tone_iv_full 回退 panel 级均值 (无文章级 leave-out, "
            "IV 排除约束缺口见模块头 g-llm-peer-01 披露)")

    results = {}  # key: (bank, year), value: dict
    for year in years:
        lag_year = year - 1
        for bank_i in banks:
            key = f'{bank_i}_{lag_year}'
            iv_entry = {}
            for c in cutoffs:
                c_str = f"{int(c*100)}"
                peers = peer_maps[c].get(key, [])
                if not peers:
                    # fix(omni-g-llm-peer-07, 2026-06-11): t-1 查证成功且判
                    # '零同行' → count 显式 0 (拓扑变量, 区别于未查证的 NaN);
                    # tone/coverage IV 保持缺失 — 空集合均值未定义。
                    if key in queried_keys:
                        iv_entry[f'llm_peer_count_{c_str}'] = 0
                        if c == 0.80:
                            iv_entry['llm_peer_n_effective'] = 0
                    continue
                # [计量逻辑加固] 同侪数量 (网络中心度) 属于网络拓扑结构变量
                # 绝对不能因为同侪恰好当年未发布新闻 (情感为 NaN) 而将其连带设置为缺失
                iv_entry[f'llm_peer_count_{c_str}'] = len(peers)

                # 取 t-1 年 LLM-peers 的情感均值 (规避同期反射问题 Manski, 1993)
                peer_mask = (panel['year'] == lag_year) & (panel['target_bank'].isin(peers))
                # 三轨 (full/ctx/ss) 并排各自 just-identified — ⚠ 铁律: full×ctx×ss
                # 禁混进同一 over-id Hansen J (三轨高度共线, 见 iv_extensions Hansen J 段);
                # ss 轨 (银行+金科同句) llm_vote_score_ss 缺列时 _art_col/_panel_tone_col
                # 两守卫自动优雅跳过 (镜像 ctx 缺列行为)。
                for _track in ('full', 'ctx', 'ss'):
                    _panel_tone_col = f'llm_vote_tone_{_track}'
                    _art_col = _ART_TONE_BY_TRACK[_track]
                    _out_col = f'llm_peer_tone_iv_{_track}_{c_str}'
                    if _art_col in df_exploded.columns:
                        # 文章级 leave-out: peer j 的 t-1 均值剔除共提 i 的文章
                        _lo = [_peer_leave_out_tone_mean(
                                   art_index, p, lag_year, _art_col, bank_i)
                               for p in peers]
                        _vals = [v for v in _lo if v is not None]
                        if _vals:
                            iv_entry[_out_col] = sum(_vals) / len(_vals)
                        if _track == 'full' and c == 0.80:
                            # fix(omni-g-llm-peer-08): 实际进入 tone IV 的
                            # 面板内有效 peer 数 (count 计全部归一同行, 域不同)
                            iv_entry['llm_peer_n_effective'] = len(_vals)
                    elif _panel_tone_col in panel.columns:
                        # 回退: panel 级均值 (旧口径, 无 leave-out — loud 披露见上)
                        _tone_vals = panel.loc[peer_mask, _panel_tone_col]
                        # [白盒安全加固] notna().any() 而非 len()>0, 防全 NaN
                        # 的 peer 集触发均值计算污染面板数据
                        if _tone_vals.notna().any():
                            iv_entry[_out_col] = _tone_vals.mean()
                        if _track == 'full' and c == 0.80:
                            iv_entry['llm_peer_n_effective'] = int(
                                _tone_vals.notna().sum())

                if coverage_col in panel.columns:
                    cov_vals = panel.loc[peer_mask, coverage_col]
                    if cov_vals.notna().any():
                        iv_entry[f'llm_peer_coverage_iv_{c_str}'] = cov_vals.mean()
            # 主回归用无后缀变量: cutoff=0.80
            # ⚠ 命名勘误 (metric-audit 2026-06-10): 此 cutoff 原是 difflib.get_close_matches
            # 的字符串匹配严格度 (银行名归一), 不是 TNIC 的同行语义相似度阈值, 勿将
            # cutoff 扫描标注为 TNIC/Cao 相似度阈值。fix(omni-g-llm-peer-04/05,
            # 2026-06-11) 后 difflib 兜底已移除, cutoff 完全惰性 — 五档列结构性
            # 逐位相同 (披露见步骤 5 注释)。
            # 与 40_panel_export_main.py Stata 标签 'llm_peer_tone_iv_full' 等对齐
            _primary_maps = [
                ('llm_peer_count', 'llm_peer_count_80'),
                ('llm_peer_tone_iv_full', 'llm_peer_tone_iv_full_80'),
                ('llm_peer_coverage_iv', 'llm_peer_coverage_iv_80'),
            ]
            # 三轨 (full/ctx/ss) parity: ctx/ss 轨主回归无后缀变量 = cutoff=0.80
            # (2026-06-08 ctx; 2026-06-14 +ss 银行+金科同句轨)
            if 'llm_vote_tone_ctx' in panel.columns:
                _primary_maps.append(
                    ('llm_peer_tone_iv_ctx', 'llm_peer_tone_iv_ctx_80'))
            # ss 轨主回归无后缀变量 = cutoff=0.80; 缺列 (stage 21 未产 ss) 时优雅跳过
            if 'llm_vote_tone_ss' in panel.columns:
                _primary_maps.append(
                    ('llm_peer_tone_iv_ss', 'llm_peer_tone_iv_ss_80'))
            for primary_col, suffixed_col in _primary_maps:
                if suffixed_col in iv_entry:
                    iv_entry[primary_col] = iv_entry[suffixed_col]
            if iv_entry:
                results[(bank_i, year)] = iv_entry

    # ── 7. 合并至面板 ──
    if results:
        iv_df = pd.DataFrame([
            {'target_bank': k[0], 'year': k[1], **v}
            for k, v in results.items()
        ])
        panel = panel.merge(iv_df, on=['target_bank', 'year'], how='left')

    # ── 7b. 同业竞争压力指标 (Peer Competition Index) ──
    # 学术依据: Cao, Y., Chen, L., Tucker, J. W., & Wan, C. (2025). 
    #   Can generative AI help identify peer firms? Review of Accounting Studies, 30(4), 3344-3386. 
    #   https://doi.org/10.1007/s11142-025-09892-6
    # 辅助依据 (对比 TNIC): Hoberg, G., & Phillips, G. (2016). 
    #   Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. 
    #   https://doi.org/10.1086/688176
    # 公式: peer_compete_idx = 与 LLM 识别同行共现的文章比例 ∈ [0, 1]
    compete_records = []
    banks = panel['target_bank'].unique()
    years = panel['year'].unique()
    for bank in banks:
        for year in years:
            key = f'{bank}_{year}'
            compete_entry = {'target_bank': bank, 'year': year}
            has_data = False
            for c in cutoffs:
                peers = peer_maps[c].get(key, [])
                if not peers:
                    # fix(omni-g-llm-peer-07, 2026-06-11): 同年查证成功且判
                    # '零同行' → 共现比例 trivially 0 (区别于未查证的 NaN)
                    if key in queried_keys:
                        compete_entry[f'peer_compete_idx_{int(c*100)}'] = 0.0
                        if c == 0.80:
                            compete_entry['peer_compete_idx'] = 0.0
                        has_data = True
                    continue
                peer_set = set(peers)
                mask = ((df_exploded['target_bank'] == bank) &
                        (df_exploded['year'] == year))
                articles = df_exploded.loc[mask]
                if len(articles) == 0:
                    continue
                # ruff B023: 默认参数绑定 peer_set, 与上方 tone_words.py
                # 修复后风格一致 (Plan-r3 P2-13).
                co_with_peer = articles['co_mentioned_banks'].apply(
                    lambda x, ps=peer_set: bool(set(str(x).split(';')) & ps)
                    if pd.notna(x) and str(x).strip() else False
                ).sum()
                c_str = f"{int(c*100)}"
                idx_val = co_with_peer / len(articles)
                compete_entry[f'peer_compete_idx_{c_str}'] = idx_val
                # 主回归用无后缀变量: difflib 名归一 cutoff=0.80 (⚠ 非 TNIC 相似度阈值,
                # 与 L691 同口径勘误 — cutoff 是 difflib.get_close_matches 串匹配严格度)
                if c == 0.80:
                    compete_entry['peer_compete_idx'] = idx_val
                has_data = True
            if has_data:
                compete_records.append(compete_entry)
    if compete_records:
        compete_df = pd.DataFrame(compete_records)
        panel = panel.merge(compete_df, on=['target_bank', 'year'], how='left')
        logger.info(f"  peer_compete_idx 生成完毕 (多阈值, {len(compete_records):,} bank-year 有记录)")
    else:
        logger.info("  peer_compete_idx: 无 peer_map 记录, 跳过")

    # ── 7c. llm_peer_queried 旗标 (fix omni-g-llm-peer-07, 2026-06-11) ──
    # 1 = 该 bank-year 自身的 LLM 调用 + JSON 解析成功 (peers 可为空; 同年口径,
    # 与 peer_compete_idx 一致 — 滞后 IV/count 的查证年份是 t-1)。
    # 0 = 未查证 (无合格句子 / 调用失败 / 解析失败), 供回归区分样本选择。
    panel['llm_peer_queried'] = [
        int(f"{b}_{y}" in queried_keys)
        for b, y in zip(panel['target_bank'], panel['year'])
    ]
    _n_queried = int(panel['llm_peer_queried'].sum())
    logger.info(f"  llm_peer_queried: {_n_queried:,}/{len(panel):,} bank-year 已查证 "
                f"({pct4(_n_queried / len(panel)) if len(panel) else 'n/a'})")
    _phase_durations['⑤IV 构建+合并'] = time.time() - _t_build

    # 诊断统计
    if results:
        for c in cutoffs:
            c_str = f"{int(c*100)}"
            for col in [f'llm_peer_tone_iv_full_{c_str}', f'llm_peer_coverage_iv_{c_str}', f'llm_peer_count_{c_str}']:
                if col in panel.columns:
                    valid = panel[col].dropna()
                    logger.info(f"  {col}: {len(valid):,} 有效值, "
                                f"mean={sig4(valid.mean())}")
    else:
        logger.warning("  未生成任何 LLM-Peer IV 变量")

    # ── 8. 关键指标解读 (运行结果信息, 对照阈值给好/临界/坏判读) ──
    # 纯日志块; 任何异常以 warning 吞掉, 绝不让结果分析崩 stage (golden-safe)。
    try:
        logger.info("  📊 关键指标解读 (LLM-Peer IV 质量诊断)")
        n_panel = len(panel)
        # ① 查证覆盖率: LLM 成功识别同行的 bank-year 占比 (识别样本是否足够)
        cov = _n_queried / n_panel if n_panel else 0.0
        cov_verdict = ("✅ 充分" if cov >= 0.50 else
                       "⚠ 临界 (识别样本偏小, IV 第一阶段 N 受限)" if cov >= 0.20 else
                       "❌ 偏弱 (查证覆盖不足, 多数 bank-year 无 peer 网络)")
        logger.info(f"     · 查证覆盖率 llm_peer_queried = {pct4(cov)} → {cov_verdict}")
        # ② 核心 tone IV (cutoff=0.80 主回归口径) 有效率 + 均值
        main_col = 'llm_peer_tone_iv_full_80'
        if main_col in panel.columns:
            mv = panel[main_col].dropna()
            iv_cov = len(mv) / n_panel if n_panel else 0.0
            iv_verdict = ("✅ 充分" if iv_cov >= 0.50 else
                          "⚠ 临界" if iv_cov >= 0.20 else "❌ 偏弱 (IV 缺失过多)")
            logger.info(f"     · 核心 IV {main_col}: 有效 {len(mv):,}/{n_panel:,} "
                        f"({pct4(iv_cov)}) → {iv_verdict}")
            if len(mv) >= 2:
                _std = float(mv.std())
                std_verdict = ("✅ 有横截面变异" if _std > 1e-6 else
                               "❌ 零方差 (IV 无识别力, 全样本同值)")
                logger.info(f"       均值={sig4(mv.mean())} σ={sig4(_std)} "
                            f"[{sig4(mv.min())}, {sig4(mv.max())}] → {std_verdict}")
        # ③ 三轨并排在场性 (full/ctx/ss 各自 just-identified, 禁混 Hansen J)
        present_tracks = [t for t in ('full', 'ctx', 'ss')
                          if f'llm_peer_tone_iv_{t}_80' in panel.columns]
        tr_verdict = ("✅ 三轨齐备" if len(present_tracks) == 3 else
                      f"⚠ 仅 {len(present_tracks)}/3 轨 (ss 轨依赖 llm_vote_score_ss)")
        logger.info(f"     · 三轨在场: {present_tracks} → {tr_verdict} "
                    "(⚠ 三轨禁混进同一 over-id Hansen J)")
        # ④ 同行网络规模 (诊断: 平均连通度)
        if 'llm_peer_count_80' in panel.columns:
            pc = panel['llm_peer_count_80'].dropna()
            if len(pc):
                logger.info(f"     · 同行连通度 llm_peer_count: 均值={sig4(pc.mean())} "
                            f"(TNIC 上限=10; >10 提示归一化异常)")
        # ⑤ 小样本/确定性警告
        if n_panel < 100:
            logger.warning(f"     · ⚠ 小样本: panel 仅 {n_panel:,} 行 — "
                           "IV 第一阶段功效受限, 生产规模 (T=18) 才有充分识别力")
        if not LLM_OFFLINE:
            logger.info("     · ⚠ 非离线模式: 缓存 miss 将调付费 API → peer 网络可能随重判漂移; "
                        "复现性优先时设 NEWS_PROCESS_LLM_OFFLINE=1")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  关键指标解读失败 (不影响产物): {e}")

    # ── 9. 阶段计时汇总 (各子阶段墙钟; 纯日志, golden-safe) ──
    try:
        _total = time.time() - _stage_start
        logger.info("  ⏱ 阶段计时 (墙钟)")
        for _name, _dur in _phase_durations.items():
            _frac = _dur / _total if _total > 0 else 0.0
            logger.info(f"     · {_name}: {sig4(_dur)}s ({pct4(_frac)})")
        logger.info(f"     · 合计: {sig4(_total)}s")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  计时汇总失败 (不影响产物): {e}")

    return panel
