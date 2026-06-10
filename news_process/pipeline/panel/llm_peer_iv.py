"""
48_llm_peer_iv.py — LLM-Peer 动态竞争网络工具变量
============================================================

管线位置:
  45_panel_export_main.py → 步骤 7h-llmpeer
  本模块在 46_network_spillovers.py 之后执行。
  依赖 41_panel_encode_aggregate.py 生成的 co_mentioned_banks 列
  和 llm_vote_tone_* 情感指标。

核心思想:
  从新闻正文中提取同时包含 2+ 银行名的句子 → 送 GPT 判断竞争关系
  → 构建动态同行网络 → 加权同行情感作为 IV。

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
  → 同行情感均值作为 IV 的理论基础

输出:
  llm_peer_tone_iv_full: LLM-Peer 加权情感 IV (核心 IV)
  llm_peer_coverage_iv:  LLM-Peer 加权声量 IV (辅助 IV)
  llm_peer_count:        LLM-Peer 网络连通度 (诊断变量)
"""

import asyncio
import json
import os
import re
import sys
from difflib import get_close_matches
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
from news_process.core.logging import setup_logging

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
MAX_RETRIES = LLM_CONFIG.get('max_retries', 5)
RETRY_DELAY = LLM_CONFIG.get('retry_delay', 10)

logger.info(f"LLM-Peer IV 参数: temperature={TEMPERATURE}, seed={RANDOM_SEED}, "
            f"force_json={FORCE_JSON}, models={len(MODELS)}, "
            f"concurrency={MAX_CONCURRENCY}, "
            f"retries={MAX_RETRIES}, delay={RETRY_DELAY}")


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
                                   max_sents: int = 5000) -> List[str]:
    """从该银行某年文章中提取同时满足两个条件的句子。

    条件 1: 包含 ≥2 个不同银行名称
    条件 2: 包含 ≥1 个金融科技关键词 (来自 fintech_dict.json)

    双重筛选确保送入 LLM 的句子既涉及银行间比较, 又聚焦于金融科技
    领域, 最大化信号纯度, 避免宏观经济/公司治理等无关并列干扰。

    流程:
      1. 筛选 co_mentioned_banks 非空的文章 (预筛)
      2. 标题+正文拼接后按 。！？；\\n 分句
      3. 逐句检查: 是否含 ≥2 银行名 且 含 ≥1 金融科技关键词
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

    sentences = []
    for _, row in df_co.iterrows():
        title = str(row.get('标题', '')).strip()
        content = str(row.get('内容', '')).strip()
        full = title + '。' + content

        for sent in SENT_SPLIT.split(full):
            sent = sent.strip()
            if len(sent) < 10:
                continue
            # 检查条件 1: ≥2 个不同银行名称
            banks_found = set()
            for name in all_bank_names:
                if len(name) >= 2 and name in sent:
                    banks_found.add(name)
            if len(banks_found) < 2:
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
                        # v3.7.0 (C1): LLM raw response archive (V4 F-P2.1)
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
    """将 LLM 输出的银行名模糊匹配至 bank_names.json 标准名。

    匹配策略 (优先级递减):
      1. 精确匹配: raw == canonical
      2. 变体映射: raw ∈ variant_to_canonical (bank_names.json 的 variants)
         → 处理 LLM 输出简称如 '工行' → '中国工商银行',
           '招行' → '招商银行' 等 2 字符缩写
      3. 子串包含: canonical ⊂ raw 或 raw ⊂ canonical (最小长度 3)
         → 处理 LLM 返回 '中国工商银行股份有限公司' 而标准名为
           '中国工商银行' 的情况
      4. difflib 模糊匹配: cutoff=0.8
         → 防止 '招商银行' vs '浙商银行' 误匹配 (相似度 0.75)

    Args:
        raw_peers: LLM 输出的银行名列表
        canonical_names: bank_names.json 中的标准 bank_name 列表
        variant_to_canonical: {变体: 标准名} 映射 (来自 bank_names.json)
            → 用于解析 '工行'/'招行' 等 2 字符简称

    Returns:
        list[str]: 去重后的标准银行名列表
    """
    canonical_set = set(canonical_names)  # O(1) 查找优化 (银行数 ~200+)
    normalized = []
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
        # 策略 3: 子串包含 (取最长匹配避免歧义)
        # 最小长度 3: 防止 '中国'/'银行' 等过短非银行名片段误匹配
        if len(name) >= 3:
            substr_matches = [cn for cn in canonical_names
                              if cn in name or name in cn]
            if substr_matches:
                best = max(substr_matches, key=len)
                normalized.append(best)
                continue
        # 策略 4: difflib 模糊匹配 (最后手段)
        match = get_close_matches(name, canonical_names, n=1, cutoff=cutoff)
        if match:
            normalized.append(match[0])
    return list(set(normalized))  # 去重


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
# 9. 主函数
# ============================================================================

def compute_llm_peer_iv(panel: pd.DataFrame,
                         df_exploded: pd.DataFrame) -> pd.DataFrame:
    """基于 LLM 语义判断的动态竞争网络工具变量。

    完整流程:
      1. 加载银行名 + 金融科技关键词
      2. 按银行×年份提取双重筛选句子
      3. 调用 LLM 识别竞争同行 (异步并发)
      4. 模糊匹配标准化 → 构建 peer_map
      5. 滞后一期: IV = mean(tone_{peers, t-1})

    方法论:
      - 句子双重筛选: 2+ 银行名 + fintech 关键词
      - LLM 判断: temperature=0, seed=42, JSON 输出
      - 滞后一期规避 Manski (1993) 反射问题
      - Peer 数量上限 = 10 (Hoberg & Phillips 2016 TNIC 标准)

    Args:
        panel: 银行-年份面板 DataFrame
        df_exploded: 文章级 DataFrame

    Returns:
        panel: 追加 llm_peer_tone_iv_full, llm_peer_coverage_iv,
               llm_peer_count 列的面板

    References:
        Cao, Y. et al. (2025). RAS, 30(4), 3344-3386.
        Hoberg, G., & Phillips, G. (2016). JPE, 124(5), 1423-1465.
        Manski, C. F. (1993). RES, 60(3), 531-542.
        Leary, M. T., & Roberts, M. R. (2014). JF, 69(1), 139-178.
    """
    logger.info("=" * 60)
    logger.info("LLM-Peer 动态竞争网络 IV (Cao et al. 2025)")
    logger.info("=" * 60)

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
    logger.info(f"  LLM 缓存: {cache.size()} 条已缓存, 路径: {cache_db}")

    # ── 3. 按银行×年份提取句子 + LLM 调用 ──
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

            sents = _extract_multi_bank_sentences(
                df_by, all_bank_names, fintech_keywords)
            if not sents:
                logger.info(f"  {bank} {year}: 无符合条件的句子, 跳过")
                continue

            tasks_to_call.append((bank, year, sents))

    logger.info(f"  需调用 LLM: {len(tasks_to_call)} 对 (银行×年份)")

    # ── 4. 异步并发调用 ──
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
            if isinstance(r, Exception):
                n_fail += 1
                logger.error(f"  LLM 调用异常: {r}")
            elif r[2] is not None:
                n_success += 1
            else:
                n_fail += 1

        logger.info(f"  LLM 调用完成: 成功={n_success}, 失败={n_fail}")

    # ── 5. 解析结果 → peer_map ──
    cutoffs = [0.70, 0.75, 0.80, 0.85, 0.90]
    peer_maps = {c: {} for c in cutoffs}

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
        logger.info(f"  Peer 网络 (cutoff={c}): {len(peer_maps[c])} 对有效 (银行×年份)")

    # ── 6. IV 构建 (滞后一期) ──
    results = {}  # key: (bank, year), value: dict
    for year in years:
        lag_year = year - 1
        for bank_i in banks:
            key = f'{bank_i}_{lag_year}'
            iv_entry = {}
            for c in cutoffs:
                peers = peer_maps[c].get(key, [])
                if not peers:
                    continue
                c_str = f"{int(c*100)}"
                # [计量逻辑加固] 同侪数量 (网络中心度) 属于网络拓扑结构变量
                # 绝对不能因为同侪恰好当年未发布新闻 (情感为 NaN) 而将其连带设置为缺失
                iv_entry[f'llm_peer_count_{c_str}'] = len(peers)

                # 取 t-1 年 LLM-peers 的情感均值 (规避同期反射问题 Manski, 1993)
                peer_mask = (panel['year'] == lag_year) & (panel['target_bank'].isin(peers))
                tone_vals = panel.loc[peer_mask, tone_col]
                
                # [白盒安全加固] 必须使用 notna().any() 而非 len() > 0 
                # 防止当所有匹配到的 peer 情感值全为 NaN 时，触发均值计算污染面板数据
                if tone_vals.notna().any():
                    iv_entry[f'llm_peer_tone_iv_full_{c_str}'] = tone_vals.mean()

                # dual-track parity (2026-06-08): ctx 轨 IV — peer_map (LLM 识别同侪)
                # track-agnostic, 同一 peer_mask 复聚合 llm_vote_tone_ctx (规避反射 Manski 1993),
                # 产 llm_peer_tone_iv_ctx_{c}, 与 _full 对称 ($0, 无新 LLM 调用)。
                if 'llm_vote_tone_ctx' in panel.columns:
                    _tone_vals_ctx = panel.loc[peer_mask, 'llm_vote_tone_ctx']
                    if _tone_vals_ctx.notna().any():
                        iv_entry[f'llm_peer_tone_iv_ctx_{c_str}'] = _tone_vals_ctx.mean()

                if coverage_col in panel.columns:
                    cov_vals = panel.loc[peer_mask, coverage_col]
                    if cov_vals.notna().any():
                        iv_entry[f'llm_peer_coverage_iv_{c_str}'] = cov_vals.mean()
            # 主回归用无后缀变量: cutoff=0.80
            # ⚠ 命名勘误 (metric-audit 2026-06-10): 此 cutoff 是 difflib.get_close_matches
            # 的字符串匹配严格度 (用于把 LLM 输出的银行名归一到规范名), 不是 TNIC 的
            # 同行语义相似度阈值。Hoberg & Phillips (2016) 的 TNIC "10 closest peers" 上限
            # (见 L264) 与本 difflib cutoff 是两回事, 勿将 cutoff 扫描标注为 TNIC/Cao 相似度阈值。
            # 与 45_panel_export_main.py Stata 标签 'llm_peer_tone_iv_full' 等对齐
            _primary_maps = [
                ('llm_peer_count', 'llm_peer_count_80'),
                ('llm_peer_tone_iv_full', 'llm_peer_tone_iv_full_80'),
                ('llm_peer_coverage_iv', 'llm_peer_coverage_iv_80'),
            ]
            # dual-track parity (2026-06-08): ctx 轨主回归无后缀变量 = cutoff=0.80
            if 'llm_vote_tone_ctx' in panel.columns:
                _primary_maps.append(
                    ('llm_peer_tone_iv_ctx', 'llm_peer_tone_iv_ctx_80'))
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
        logger.info(f"  peer_compete_idx 生成完毕 (多阈值)")
    else:
        logger.info("  peer_compete_idx: 无 peer_map 记录, 跳过")

    # 诊断统计
    if results:
        for c in cutoffs:
            c_str = f"{int(c*100)}"
            for col in [f'llm_peer_tone_iv_full_{c_str}', f'llm_peer_coverage_iv_{c_str}', f'llm_peer_count_{c_str}']:
                if col in panel.columns:
                    valid = panel[col].dropna()
                    logger.info(f"  {col}: {len(valid):,} 有效值, "
                                f"mean={valid.mean():.4f}")
    else:
        logger.warning("  未生成任何 LLM-Peer IV 变量")

    return panel
