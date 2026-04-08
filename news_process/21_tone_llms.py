"""
21_tone_llms.py — 阶段21：统一 LLM 语义精筛与情感分析（双轨版）
=====================================================

功能：
    将早期的 `13_news_llms.py` (真伪精筛) 和 `23_tone_llms.py` (情感分析) 组合，
    使用同一个大模型 Prompt 构建思维链 (Chain-of-Thought)，单次请求获取"真伪"与"情感"。
    采用多模型（如 gpt5nano, gemini3, claude4h）逐条并发请求，并使用多数投票（Majority Vote）
    合成最终共识，满足顶级学术期刊的交叉验证和三角验证标准。
    每条新闻独立请求各模型，通过信号量控制并发。

    【双轨输入】每条新闻同时以全文 (_full) 和上下文片段 (_ctx) 两种输入分别请求模型，
    生成两套完整的验证与情感判定结果，供下游消融研究和三角验证使用。

输入：
    模块二前置输出的 `12_fintech_news.parquet`
    
输出：
    筛选后的合法新闻 `21_tone_llms.parquet`
"""

import os
import sys
import time
import json
import logging
import asyncio
import aiohttp
import pandas as pd

from collections import Counter
from utils.helpers import load_config, setup_logging, log_memory_usage, log_stage_summary, save_dataset

from utils.canonicalization import canonicalize_topic
from utils.entity_context import extract_entity_context, get_target_aliases

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "21_tone_llms"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 读取 tone_llm_processing 配置
LLM_CONFIG = CONFIG.get('tone_llm_processing', {})
if not LLM_CONFIG:
    logger.error("在 config.yaml 中未找到 tone_llm_processing 配置节！")
    sys.exit(1)

# 模型列表: 多模型并行请求以支持多数投票(Majority Vote)共识机制
# 推荐至少 3 个模型, 以实现 2/3 多数投票的稳健共识
MODELS = LLM_CONFIG.get('models', [])
MAX_CONCURRENCY = max(1, int(LLM_CONFIG.get('max_concurrency', '')))
# Prompt 模板: 包含 {title}, {content}, {target_bank}, {co_mentioned_banks} 占位符
PROMPT_TEMPLATE = LLM_CONFIG.get('prompt_template', '')
# G-06: 温度参数锁定 — temperature=0 确保确定性推理输出, 保证可复现性
# 学术依据: Lopez-Lira, A., & Tang, Y. (2023). Can ChatGPT forecast stock price
#           movements? SSRN Working Paper No. 4412788:
#           "We use temperature = 0 to ensure deterministic outputs for
#           reproducibility of sentiment labels."
# 同见: Carlson & Burbano (2026, SMJ §3.3): "temperature should be fixed and reported"
TEMPERATURE = LLM_CONFIG.get('temperature', '')
RANDOM_SEED = LLM_CONFIG.get('random_seed', '')
FORCE_JSON = LLM_CONFIG.get('force_json', True)

# 显式记录 LLM 推理参数 (G-06: 审稿人可追溯的参数报告)
logger.info(f"LLM 推理参数: temperature={TEMPERATURE}, seed={RANDOM_SEED}, "
            f"force_json={FORCE_JSON}, models={len(MODELS)}, "
            f"concurrency={MAX_CONCURRENCY}")

MAX_RETRIES = LLM_CONFIG.get('max_retries', '')
RETRY_DELAY = LLM_CONFIG.get('retry_delay', '')


# ============================================================================
# 2. 异步请求大模型 API
# ============================================================================

async def fetch_llm_async(session: aiohttp.ClientSession, semaphore: asyncio.Semaphore, 
                          prompt: str, model_cfg: dict, row_idx: int, track: str) -> tuple:
    """异步请求单个模型的单篇文章，自带重试保护。
    
    model_cfg 结构示例：
        {model_name: ..., short_name: ..., base_url: ..., api_key: ...}
    每个模型可独立指定 base_url 和 api_key。

    Args:
        track: 'full'、'ctx' 或 'title'，标识本次请求使用的文本轨道。
    
    Returns:
        tuple: (row_idx, model_id, result_text, track)
    """
    model_id = model_cfg['model_name']
    base_url = model_cfg.get('base_url', '')
    api_key  = model_cfg.get('api_key', '')

    # 准备请求
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model_id,
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
                async with session.post(f"{base_url}/chat/completions", json=payload, headers=headers, timeout=req_timeout) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        result_text = data['choices'][0]['message']['content']
                        return row_idx, model_id, result_text, track
                    elif resp.status in (429, 500, 502, 503, 504):
                        logger.warning(f"[{model_id}] API HTTP {resp.status} - 等待 {RETRY_DELAY}s 后重试...")
                        await asyncio.sleep(RETRY_DELAY)
                    else:
                        resp_text = await resp.text()
                        logger.error(f"[{model_id}] API 错误 {resp.status}: {resp_text}")
                        break
            except asyncio.TimeoutError:
                logger.warning(f"[{model_id}] 请求超时 - 等待 {RETRY_DELAY}s 后重试...")
                await asyncio.sleep(RETRY_DELAY)
            except Exception as e:
                logger.warning(f"[{model_id}] 异常 ({type(e).__name__}): {e}")
                await asyncio.sleep(RETRY_DELAY)

    # 所有重试均失败，返回 None 标记（区别于空 JSON，避免影响多数投票）
    logger.warning(f"[{model_id}] 行 {row_idx}: 所有 {MAX_RETRIES} 次重试均失败，该模型结果将从投票中排除")
    return row_idx, model_id, None, track

async def run_all_llms(df: pd.DataFrame, models: list) -> dict:
    """逐条并发执行 DataFrame 中所有行对所有配置模型的双轨请求。
    
    为每行 × 每模型 × 每轨道 生成独立 prompt，通过信号量控制并发数。
    要求 df 中已包含 'content_ctx' 列（由 main() 预计算并物化）。
    
    Returns:
        dict: {row_idx: {'full': {model_id: res_text}, 'ctx': {model_id: res_text}}}
    """
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    results_map = {i: {'full': {}, 'ctx': {}} for i in df.index}
    
    total_tasks = len(df) * len(models) * 2  # ×2 因为双轨
    logger.info(f"逐条请求: {len(df)} 条新闻 × {len(models)} 模型 × 2 轨道 = {total_tasks} 个请求")
    
    # 连接池优化：复用 TCP 连接 + keepalive，减少握手和 TLS 协商开销
    connector = aiohttp.TCPConnector(
        limit=MAX_CONCURRENCY,        # 连接池大小与并发数匹配
        keepalive_timeout=30,         # 连接保活 30 秒
        enable_cleanup_closed=True,   # 自动清理已关闭连接
    )
    async with aiohttp.ClientSession(connector=connector) as session:
        # 构建任务列表：每行 x 每轨道 x 每模型
        real_tasks = []
        for idx, row in df.iterrows():
            content_full = str(row.get('内容', ''))
            content_ctx = str(row.get('content_ctx', content_full))
            target_bank = str(row.get('target_bank', ''))
            
            for track, content in [('full', content_full), ('ctx', content_ctx)]:
                prompt = PROMPT_TEMPLATE.format(
                    title=str(row.get('标题', '')),
                    content=content,
                    target_bank=target_bank,
                    co_mentioned_banks=str(row.get('co_mentioned_banks', '无')),
                )
                for m in models:
                    real_tasks.append(fetch_llm_async(session, semaphore, prompt, m, idx, track))
        
        completed = 0
        total = len(real_tasks)
        report_interval = max(1, total // 20)  # 每 5% 汇报一次
        next_report = report_interval
        logger.info(f"📡 LLM 双轨逐条请求开始: 共 {total} 个请求")
        
        for coro in asyncio.as_completed(real_tasks):
            row_idx, model_id, res_text, track = await coro
            results_map[row_idx][track][model_id] = res_text
            completed += 1
            if completed >= next_report or completed == total:
                pct = completed / total * 100
                logger.info(f"📡 LLM 请求进度: {completed}/{total} ({pct:.1f}%)")
                next_report += report_interval
        
        logger.info(f"📡 LLM 双轨逐条请求完成: 共 {total} 个请求全部处理完毕")
    
    return results_map


# ============================================================================
# 3. 结果提取与多数投票聚合
# ============================================================================

def parse_json_response(res_text: str) -> dict:
    """尝试从大模型结果中解析 JSON。

    容错策略: 自动去除 markdown 代码块包围(```json ... ```),
    因为部分模型(如 GPT 系列)倾向于在 JSON 响应外添加代码块标记。
    """
    try:
        # 去除 markdown json 代码块包围
        text = res_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except Exception:
        return {}

def majority_vote_bool(bools: list) -> bool:
    """严格多数决判断真伪（超过半数才通过）"""
    if not bools: return False
    return sum(bools) > (len(bools) / 2.0)

def majority_vote_sentiment(sents: list) -> str:
    """多数决判断情感，平局降级为中性"""
    if not sents: return "中性"
    c = Counter(sents)
    most_common = c.most_common()
    if len(most_common) > 1 and most_common[0][1] == most_common[1][1]:
        return "中性"
    return most_common[0][0]


def _aggregate_track(model_res_dict: dict, models: list) -> tuple:
    """对某一轨道的模型响应进行解析和多数投票聚合。
    
    Args:
        model_res_dict: {model_id: res_text} — 某一轨道的模型响应
        models: 模型配置列表
    
    Returns:
        tuple: (final_v, final_s, agree_rate, per_model_parsed, topics, llm_categories, text_types, n_failures)
            per_model_parsed: {f'{short}_verified': v, ...} 的字典
    """
    v_votes = []
    s_votes = []
    topics = []
    llm_categories = []
    text_types = []
    per_model_parsed = {}
    n_failures = 0
    
    for m in models:
        short = m['short_name']
        m_id = m['model_name']
        raw_text = model_res_dict.get(m_id, None)
        
        # None 表示该模型 API 调用失败，跳过投票
        if raw_text is None:
            n_failures += 1
            per_model_parsed[f"{short}_verified"] = None
            per_model_parsed[f"{short}_sentiment"] = None
            per_model_parsed[f"{short}_verification_confidence"] = 0.0
            per_model_parsed[f"{short}_sentiment_confidence"] = 0.0
            continue
        
        jd = parse_json_response(raw_text)
        
        # 解析对应字段（安全处理 LLM 返回的字符串布尔值）
        v = jd.get('is_bank_fintech_news', False)
        if isinstance(v, str):
            v = v.strip().lower() in ('true', '1', 'yes')
        v = bool(v)
        
        s = jd.get('sentiment', '中性')
        
        # 若判别为伪，其情感严格规定为中性以防噪声
        if not v:
            s = "中性"
            
        v_votes.append(v)
        s_votes.append(s)
        
        per_model_parsed[f"{short}_verified"] = v
        per_model_parsed[f"{short}_sentiment"] = s
        per_model_parsed[f"{short}_verification_confidence"] = jd.get('verification_confidence', 0.0)
        per_model_parsed[f"{short}_sentiment_confidence"] = jd.get('sentiment_confidence', 0.0)
        
        # 同步提取 fintech_topic 和 fintech_category（复用已解析的 jd）
        topic = jd.get('fintech_topic', None)
        if topic and str(topic).strip().lower() not in ('null', 'none', ''):
            topics.append(str(topic))
        llm_cat = jd.get('fintech_category', None)
        if llm_cat:
            cat_str = str(llm_cat).strip().replace('；', ';')
            for part in cat_str.split(';'):
                part = part.strip()
                if part in ('底层技术', '应用场景', '混合型'):
                    llm_categories.append(part)
                    break
        # 提取 text_type（与 fintech_category 对称的三分类模式）
        llm_tt = jd.get('text_type', None)
        if llm_tt:
            tt_str = str(llm_tt).strip()
            if tt_str in ('实质性', '描述性', '混合型'):
                text_types.append(tt_str)
    
    final_v = majority_vote_bool(v_votes)
    final_s = majority_vote_sentiment(s_votes) if final_v else "中性"
    
    # 计算一致性：有效投票中支持 majority 的比例
    n_valid_votes = len(v_votes)
    agree_v_count = sum(1 for x in v_votes if x == final_v)
    agree_rate = agree_v_count / n_valid_votes if n_valid_votes > 0 else 0.0
    
    return final_v, final_s, agree_rate, per_model_parsed, topics, llm_categories, text_types, n_failures


def _materialize_content_ctx(df: pd.DataFrame) -> pd.DataFrame:
    """预计算并物化 content_ctx 列，供双轨分析和下游阶段复用。

    对每个 (文章, 目标银行) 对调用 extract_entity_context() 提取
    实体特异性上下文片段，结果存入 'content_ctx' 列。下游阶段
    22_tone_words 和 23_tone_berts 直接读取此列，避免重复计算
    并确保三种情感分析方法对完全一致的文本进行分析。

    Args:
        df: 含 '内容' 和 'target_bank' 列的 DataFrame。

    Returns:
        pd.DataFrame: 增加了 'content_ctx' 列的 DataFrame。
    """
    logger.info("物化 content_ctx 列（实体特异性上下文提取）...")
    _bnf = CONFIG['paths'].get('bank_names_file', '')
    _alias_cache = {}

    ctx_list = []
    for _, row in df.iterrows():
        content_full = str(row.get('内容', ''))
        target_bank = str(row.get('target_bank', ''))

        if target_bank:
            if target_bank not in _alias_cache:
                _alias_cache[target_bank] = get_target_aliases(target_bank, _bnf)
            content_ctx = extract_entity_context(content_full, _alias_cache[target_bank])
            if not content_ctx:
                content_ctx = content_full  # 回退公理
        else:
            content_ctx = content_full

        ctx_list.append(content_ctx)

    df['content_ctx'] = ctx_list
    n_fallback = sum(1 for ctx, full in zip(ctx_list, df['内容'].astype(str)) if ctx == full)
    n_with_bank = (df['target_bank'].astype(str).str.strip() != '').sum()
    logger.info(f"  content_ctx 列物化完成: {len(df)} 行, "
                f"回退至全文: {n_fallback}/{n_with_bank} 条"
                f"（{n_fallback/max(n_with_bank,1)*100:.1f}%）")
    return df


def main():
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} (双轨模式) ---")
    
    if not LLM_CONFIG.get('enabled', False):
        logger.info("统一 LLM 处理已在 config.yaml 中禁用。将透传输入数据。")

        input_filename = CONFIG['filenames'].get('output_12_fintech_news', '12_fintech_news.parquet')
        input_path = os.path.join(CONFIG["paths"]["output_dir"], input_filename)

        if not os.path.exists(input_path):
            logger.error(f"输入文件未找到: {input_path}")
            return

        df = pd.read_parquet(input_path)

        # 物化 content_ctx 列（即使 LLM 禁用，下游词典/BERT 仍需此列）
        df = _materialize_content_ctx(df)

        # 添加空的 LLM 双轨列，确保下游阶段不因缺列报错
        df['llm_verified_full'] = True
        df['llm_verified_ctx'] = True
        df['llm_sentiment_full'] = '中性'
        df['llm_sentiment_ctx'] = '中性'
        df['llm_agreement_rate_full'] = 0.0
        df['llm_agreement_rate_ctx'] = 0.0
        df['fintech_category'] = '应用场景'
        df['category_confidence'] = 0.0
        # 逐模型虚拟列补全
        for m in MODELS:
            short = m['short_name']
            for track in ['_full', '_ctx']:
                df[f'{short}_verified{track}'] = True
                df[f'{short}_sentiment{track}'] = '中性'
                df[f'{short}_verification_confidence{track}'] = 0.0
                df[f'{short}_sentiment_confidence{track}'] = 0.0

        output_filename = CONFIG.get('filenames', {}).get('output_21_tone_llms', '21_tone_llms.parquet')
        output_path = os.path.join(CONFIG["paths"]["output_dir"], output_filename)
        save_dataset(df, output_path, logger)

        log_stage_summary(logger, STAGE_NAME, stage_start, len(df), len(df))
        logger.info(f"已透传 {len(df)} 行数据至 {output_path}")
        return
        
    input_filename = CONFIG['filenames'].get('output_12_fintech_news', '12_fintech_news.parquet')
    input_path = os.path.join(CONFIG["paths"]["output_dir"], input_filename)
    
    if not os.path.exists(input_path):
        logger.error(f"输入文件未找到: {input_path}")
        return
        
    logger.info(f"加载预筛数据: {input_path}")
    df = pd.read_parquet(input_path)
    logger.info(f"总计候选新闻: {len(df)}")
    log_memory_usage(logger, "数据加载完成")
    
    # 物化 content_ctx 列（供 LLM 双轨请求 + 下游阶段 22/23 直接复用）
    df = _materialize_content_ctx(df)
    
    # 异步并发大模型（双轨）
    logger.info(f"开始分发双轨组合模型处理任务，包含模型: {[m['short_name'] for m in MODELS]}")
    results_map = asyncio.run(run_all_llms(df, MODELS))
    
    # 提取与投票（双轨）
    logger.info("开始聚合各模型 JSON 响应并执行双轨多数投票三角验证...")
    
    llm_verified_full_arr = []
    llm_verified_ctx_arr = []
    llm_sentiment_full_arr = []
    llm_sentiment_ctx_arr = []
    agreement_rate_full_arr = []
    agreement_rate_ctx_arr = []
    fintech_category_arr = []
    category_confidence_arr = []
    text_type_arr = []
    
    # 预分配每个模型 × 每轨道的独立判断列表
    per_model_cols = {}
    for m in MODELS:
        short = m['short_name']
        for track in ['_full', '_ctx']:
            per_model_cols[f"{short}_verified{track}"] = []
            per_model_cols[f"{short}_sentiment{track}"] = []
            per_model_cols[f"{short}_verification_confidence{track}"] = []
            per_model_cols[f"{short}_sentiment_confidence{track}"] = []
    
    n_api_failures = 0
    
    for idx, row in df.iterrows():
        row_results = results_map.get(idx, {'full': {}, 'ctx': {}})
        
        # ── Full 轨道聚合 ──
        final_v_full, final_s_full, agree_rate_full, parsed_full, topics_full, llm_cats_full, text_types_full, n_fail_full = \
            _aggregate_track(row_results.get('full', {}), MODELS)
        n_api_failures += n_fail_full
        
        llm_verified_full_arr.append(final_v_full)
        llm_sentiment_full_arr.append(final_s_full)
        agreement_rate_full_arr.append(agree_rate_full)
        
        for m in MODELS:
            short = m['short_name']
            per_model_cols[f"{short}_verified_full"].append(parsed_full.get(f"{short}_verified"))
            per_model_cols[f"{short}_sentiment_full"].append(parsed_full.get(f"{short}_sentiment"))
            per_model_cols[f"{short}_verification_confidence_full"].append(parsed_full.get(f"{short}_verification_confidence", 0.0))
            per_model_cols[f"{short}_sentiment_confidence_full"].append(parsed_full.get(f"{short}_sentiment_confidence", 0.0))
        
        # ── Ctx 轨道聚合 ──
        final_v_ctx, final_s_ctx, agree_rate_ctx, parsed_ctx, topics_ctx, llm_cats_ctx, text_types_ctx, n_fail_ctx = \
            _aggregate_track(row_results.get('ctx', {}), MODELS)
        n_api_failures += n_fail_ctx
        
        llm_verified_ctx_arr.append(final_v_ctx)
        llm_sentiment_ctx_arr.append(final_s_ctx)
        agreement_rate_ctx_arr.append(agree_rate_ctx)
        
        for m in MODELS:
            short = m['short_name']
            per_model_cols[f"{short}_verified_ctx"].append(parsed_ctx.get(f"{short}_verified"))
            per_model_cols[f"{short}_sentiment_ctx"].append(parsed_ctx.get(f"{short}_sentiment"))
            per_model_cols[f"{short}_verification_confidence_ctx"].append(parsed_ctx.get(f"{short}_verification_confidence", 0.0))
            per_model_cols[f"{short}_sentiment_confidence_ctx"].append(parsed_ctx.get(f"{short}_sentiment_confidence", 0.0))
        
        # ── 金融科技主题标准化分类（仅基于 full 轨道） ──
        combined_topic = ' '.join(topics_full) if topics_full else ''
        kw_category, kw_confidence = canonicalize_topic(combined_topic)
        
        if llm_cats_full:
            cat_votes = Counter(llm_cats_full)
            top = cat_votes.most_common(2)
            if len(top) >= 2 and top[0][1] == top[1][1]:
                # 平局：降为混合型（无法确定主分类）
                llm_majority_cat = '混合型'
            else:
                llm_majority_cat = top[0][0] if top else kw_category
            if llm_majority_cat == kw_category:
                final_confidence = min(kw_confidence + 0.2, 1.0)
            else:
                final_confidence = round(kw_confidence * 0.5, 3)
            fintech_category_arr.append(llm_majority_cat)
            category_confidence_arr.append(final_confidence)
        else:
            fintech_category_arr.append(kw_category)
            category_confidence_arr.append(kw_confidence)
        
        # ── 文本类型分类多数决（仅基于 full 轨道，与 fintech_category 一致） ──
        if text_types_full:
            tt_votes = Counter(text_types_full)
            tt_top = tt_votes.most_common(2)
            if len(tt_top) >= 2 and tt_top[0][1] == tt_top[1][1]:
                text_type_arr.append('混合型')  # 平局降为混合型
            else:
                text_type_arr.append(tt_top[0][0])
        else:
            text_type_arr.append(None)
    
    # 批量赋值各模型独立判断列
    for col_name, col_values in per_model_cols.items():
        df[col_name] = col_values
    
    df['llm_verified_full'] = llm_verified_full_arr
    df['llm_verified_ctx'] = llm_verified_ctx_arr
    df['llm_sentiment_full'] = llm_sentiment_full_arr
    df['llm_sentiment_ctx'] = llm_sentiment_ctx_arr
    df['llm_agreement_rate_full'] = agreement_rate_full_arr
    df['llm_agreement_rate_ctx'] = agreement_rate_ctx_arr
    df['fintech_category'] = fintech_category_arr
    df['category_confidence'] = category_confidence_arr
    df['text_type'] = text_type_arr
    
    if n_api_failures > 0:
        logger.warning(f"共有 {n_api_failures} 次模型 API 调用失败，已从对应投票中排除")
    
    # 统计分类分布（基于 full 轨道）
    if df['llm_verified_full'].sum() > 0:
        verified_df = df[df['llm_verified_full']]
        cat_counts = verified_df['fintech_category'].value_counts()
        for cat, cnt in cat_counts.items():
            logger.info(f"  金融科技分类 [{cat}]: {cnt}")
    
    # 结果统计（双轨对比）
    total_len = len(df)
    for track in ['_full', '_ctx']:
        ver_col = f'llm_verified{track}'
        sent_col = f'llm_sentiment{track}'
        passed_len = df[ver_col].sum()
        logger.info(f"[{track}] 多数决判定为真: {passed_len}/{total_len} ({passed_len/total_len*100:.1f}%)")
        
        if passed_len > 0:
            sent_counts = df[df[ver_col]][sent_col].value_counts()
            for s_type, cnt in sent_counts.items():
                logger.info(f"  [{track}] [{s_type}]: {cnt} ({cnt/passed_len*100:.1f}%)")
            
    # 保存全量结果（含 llm_verified=True 和 False），供验证模块使用
    full_output_filename = CONFIG.get('filenames', {}).get(
        'output_21_tone_llms_full', '21_tone_llms_full.parquet')
    full_output_path = os.path.join(CONFIG["paths"]["output_dir"], full_output_filename)
    save_dataset(df, full_output_path, logger)
    logger.info(f"全量 LLM 结果已保存: {full_output_path} ({len(df)} 行)")

    # 过滤丢弃不相关的假新闻（基于 full 轨道）
    df_filtered = df[df['llm_verified_full'] == True].copy()
    
    # ── B1-2: 标题轨道独立情感提取（仅已验证样本） ──
    # 学术依据: 姜富伟等 (2024, 管理世界) — 标题短文本LLM情感
    TITLE_PROMPT_TEMPLATE = LLM_CONFIG.get('title_sentiment_prompt_template', '')
    
    if TITLE_PROMPT_TEMPLATE and len(df_filtered) > 0:
        logger.info(f"── 标题轨道情感提取开始 ({len(df_filtered)} 条已验证样本) ──")
        
        BATCH_SIZE = 100
        titles = df_filtered['标题'].fillna('').astype(str).tolist()
        indices = df_filtered.index.tolist()
        
        # 按批次分组
        batches = []
        for i in range(0, len(titles), BATCH_SIZE):
            batch_titles = titles[i:i+BATCH_SIZE]
            batch_indices = indices[i:i+BATCH_SIZE]
            numbered = '\n'.join(f"{j+1}. {t}" for j, t in enumerate(batch_titles))
            prompt = TITLE_PROMPT_TEMPLATE.format(numbered_titles=numbered)
            batches.append((batch_indices, batch_titles, prompt))
        
        logger.info(f"  共 {len(batches)} 批 × {len(MODELS)} 模型 = {len(batches)*len(MODELS)} 次 API 调用")
        
        async def _run_title_batches():
            """批量调用LLM获取标题情感"""
            semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
            connector = aiohttp.TCPConnector(limit=MAX_CONCURRENCY * 2)
            timeout = aiohttp.ClientTimeout(total=LLM_CONFIG.get('timeout', 600))
            
            # {batch_idx: {model_id: response_text}}
            batch_results = {}
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                tasks = []
                for b_idx, (b_indices, b_titles, prompt) in enumerate(batches):
                    for m in MODELS:
                        tasks.append(
                            fetch_llm_async(session, semaphore, prompt, m, b_idx, 'title')
                        )
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for res in results:
                    if isinstance(res, Exception):
                        logger.warning(f"  标题批次请求异常: {res}")
                        continue
                    b_idx, model_id, text, track = res
                    if b_idx not in batch_results:
                        batch_results[b_idx] = {}
                    batch_results[b_idx][model_id] = text
            
            return batch_results
        
        batch_results = asyncio.run(_run_title_batches())
        
        # 解析批量结果 → 逐条多数决
        title_sentiment_map = {}  # {df_index: {'sentiment': ..., 'confidence': ..., per_model...}}
        
        for b_idx, (b_indices, b_titles, _) in enumerate(batches):
            # 收集每个模型对这批的解析结果
            per_model_parsed = {}  # {model_short: [{id, sentiment, confidence}, ...]}
            
            for m in MODELS:
                short = m['short_name']
                m_id = m['model_name']
                raw = batch_results.get(b_idx, {}).get(m_id, None)
                
                if raw is None:
                    per_model_parsed[short] = [None] * len(b_indices)
                    continue
                
                jd = parse_json_response(raw)
                items = jd.get('results', [])
                
                # 构建 id → item 映射（防止 id 缺失或乱序）
                id_map = {}
                for item in items:
                    if isinstance(item, dict):
                        id_map[item.get('id', -1)] = item
                
                parsed_list = []
                for j in range(len(b_indices)):
                    item = id_map.get(j + 1, None)
                    if item:
                        try:
                            conf_val = float(item.get('confidence', 0.0))
                        except (ValueError, TypeError):
                            conf_val = 0.0
                        parsed_list.append({
                            'sentiment': item.get('sentiment', '中性'),
                            'confidence': conf_val
                        })
                    else:
                        parsed_list.append(None)
                per_model_parsed[short] = parsed_list
            
            # 逐条多数决
            for j, df_idx in enumerate(b_indices):
                s_votes = []
                per_model_data = {}
                
                for m in MODELS:
                    short = m['short_name']
                    item = per_model_parsed[short][j]
                    if item is not None:
                        s_votes.append(item['sentiment'])
                        per_model_data[f'{short}_sentiment_title'] = item['sentiment']
                        per_model_data[f'{short}_sentiment_confidence_title'] = item['confidence']
                    else:
                        per_model_data[f'{short}_sentiment_title'] = None
                        per_model_data[f'{short}_sentiment_confidence_title'] = 0.0
                
                # 多数决
                if s_votes:
                    final_s = Counter(s_votes).most_common(1)[0][0]
                    agree_count = sum(1 for v in s_votes if v == final_s)
                    agree_rate = agree_count / len(s_votes)
                else:
                    final_s = '中性'
                    agree_rate = 0.0
                
                title_sentiment_map[df_idx] = {
                    'llm_sentiment_title': final_s,
                    'llm_agreement_rate_title': agree_rate,
                    **per_model_data
                }
        
        # 写入 DataFrame
        for col in ['llm_sentiment_title', 'llm_agreement_rate_title']:
            df_filtered[col] = df_filtered.index.map(
                lambda idx, c=col: title_sentiment_map.get(idx, {}).get(c))
        
        for m in MODELS:
            short = m['short_name']
            for suffix in ['_sentiment_title', '_sentiment_confidence_title']:
                col = f'{short}{suffix}'
                df_filtered[col] = df_filtered.index.map(
                    lambda idx, c=col: title_sentiment_map.get(idx, {}).get(c))
        
        # Step 1c: llm_verified_title 固定为 True（已通过 full 轨道验证）
        df_filtered['llm_verified_title'] = True
        
        # 统计
        sent_counts = df_filtered['llm_sentiment_title'].value_counts()
        logger.info(f"── 标题轨道情感提取完成 ──")
        for s_type, cnt in sent_counts.items():
            logger.info(f"  [_title] [{s_type}]: {cnt} ({cnt/len(df_filtered)*100:.1f}%)")
    else:
        if not TITLE_PROMPT_TEMPLATE:
            logger.info("  title_sentiment_prompt_template 未配置，跳过标题轨道")
        else:
            logger.info("  无已验证样本，跳过标题轨道")
    
    # ======================================================================
    # 4. 保存文件与报告
    # ======================================================================
    output_filename = CONFIG.get('filenames', {}).get('output_21_tone_llms', '21_tone_llms.parquet')
    output_path = os.path.join(CONFIG["paths"]["output_dir"], output_filename)
    
    logger.info(f"正在保存处理结果至 {output_path}...")
    save_dataset(df_filtered, output_path, logger)
    
    log_stage_summary(logger, STAGE_NAME, stage_start, len(df), len(df_filtered))

if __name__ == "__main__":
    main()
