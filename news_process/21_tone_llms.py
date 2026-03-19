"""
21_tone_llms.py — 第二十一阶段：统一 LLM 语义精筛与情感分析
=====================================================

功能：
    将早期的 `13_news_llms.py` (真伪精筛) 和 `23_tone_llms.py` (情感分析) 组合，
    使用同一个大模型 Prompt 构建思维链 (Chain-of-Thought)，单次请求获取"真伪"与"情感"。
    采用多模型（如 gpt5nano, gemini3, grok4）逐条并发请求，并使用多数投票（Majority Vote）
    合成最终共识，满足顶级学术期刊的交叉验证和三角验证标准。
    每条新闻独立请求各模型，通过信号量控制并发。

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

MODELS = LLM_CONFIG.get('models', [])
MAX_CONCURRENCY = max(1, int(LLM_CONFIG.get('max_concurrency', '')))
PROMPT_TEMPLATE = LLM_CONFIG.get('prompt_template', '')
TEMPERATURE = LLM_CONFIG.get('temperature', '')
RANDOM_SEED = LLM_CONFIG.get('random_seed', '')
FORCE_JSON = LLM_CONFIG.get('force_json', True)

MAX_RETRIES = LLM_CONFIG.get('max_retries', '')
RETRY_DELAY = LLM_CONFIG.get('retry_delay', '')


# ============================================================================
# 2. 异步请求大模型 API
# ============================================================================

async def fetch_llm_async(session: aiohttp.ClientSession, semaphore: asyncio.Semaphore, 
                          prompt: str, model_cfg: dict, row_idx: int) -> tuple:
    """异步请求单个模型的单篇文章，自带重试保护。
    
    model_cfg 结构示例：
        {model_name: ..., short_name: ..., base_url: ..., api_key: ...}
    每个模型可独立指定 base_url 和 api_key。
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
                        return row_idx, model_id, result_text
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
    return row_idx, model_id, None

async def run_all_llms(df: pd.DataFrame, models: list) -> dict:
    """逐条并发执行 DataFrame 中所有行对所有配置模型的请求。
    
    为每行 × 每模型生成独立 prompt，通过信号量控制并发数。
    """
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    results_map = {i: {} for i in df.index}
    
    total_tasks = len(df) * len(models)
    logger.info(f"逐条请求: {len(df)} 条新闻 × {len(models)} 模型 = {total_tasks} 个请求")
    
    # 连接池优化：复用 TCP 连接 + keepalive，减少握手和 TLS 协商开销
    connector = aiohttp.TCPConnector(
        limit=MAX_CONCURRENCY,        # 连接池大小与并发数匹配
        keepalive_timeout=30,         # 连接保活 30 秒
        enable_cleanup_closed=True,   # 自动清理已关闭连接
    )
    async with aiohttp.ClientSession(connector=connector) as session:
        # 构建任务列表：每行 x 每模型
        real_tasks = []
        for idx, row in df.iterrows():
            prompt = PROMPT_TEMPLATE.format(
                title=str(row.get('标题', '')),
                content=str(row.get('内容', '')),
                matched_bank_names=str(row.get('matched_bank_names', '')),
            )
            for m in models:
                real_tasks.append(fetch_llm_async(session, semaphore, prompt, m, idx))
        
        completed = 0
        total = len(real_tasks)
        report_interval = max(1, total // 20)  # 每 5% 汇报一次
        next_report = report_interval
        logger.info(f"📡 LLM 逐条请求开始: 共 {total} 个请求")
        
        for coro in asyncio.as_completed(real_tasks):
            row_idx, model_id, res_text = await coro
            results_map[row_idx][model_id] = res_text
            completed += 1
            if completed >= next_report or completed == total:
                pct = completed / total * 100
                logger.info(f"📡 LLM 请求进度: {completed}/{total} ({pct:.1f}%)")
                next_report += report_interval
        
        logger.info(f"📡 LLM 逐条请求完成: 共 {total} 个请求全部处理完毕")
    
    return results_map


# ============================================================================
# 3. 结果提取与多数投票聚合
# ============================================================================

def parse_json_response(res_text: str) -> dict:
    """尝试从大模型结果中解析 JSON"""
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

def main():
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")
    
    if not LLM_CONFIG.get('enabled', False):
        logger.info("统一 LLM 处理已在 config.yaml 中禁用。将透传输入数据。")

        input_filename = CONFIG['filenames'].get('output_12_fintech_news', '12_fintech_news.parquet')
        input_path = os.path.join(CONFIG["paths"]["output_dir"], input_filename)

        if not os.path.exists(input_path):
            logger.error(f"输入文件未找到: {input_path}")
            return

        df = pd.read_parquet(input_path)

        # 添加空的 LLM 列，确保下游阶段不因缺列报错
        df['llm_verified'] = True  # 禁用 LLM 时，视为全部保留
        df['llm_sentiment'] = '中性'
        df['llm_agreement_rate'] = 0.0
        df['fintech_category'] = '应用场景'
        df['category_confidence'] = 0.0

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
    
    # 异步并发大模型
    logger.info(f"开始分发组合模型处理任务，包含模型: {[m['short_name'] for m in MODELS]}")
    results_map = asyncio.run(run_all_llms(df, MODELS))
    
    # 提取与投票
    logger.info("开始聚合各模型 JSON 响应并执行多数投票三角验证...")
    
    llm_verified_arr = []
    llm_sentiment_arr = []
    agreement_rate_arr = []
    fintech_category_arr = []
    category_confidence_arr = []
    
    # 预分配每个模型的独立判断列表（批量赋值，避免逐行 df.at）
    per_model_cols = {}
    for m in MODELS:
        short = m['short_name']
        per_model_cols[f"{short}_verified"] = []
        per_model_cols[f"{short}_sentiment"] = []
        per_model_cols[f"{short}_verification_confidence"] = []
        per_model_cols[f"{short}_sentiment_confidence"] = []
    
    n_api_failures = 0
    
    for idx, row in df.iterrows():
        model_res = results_map.get(idx, {})
        v_votes = []
        s_votes = []
        topics = []
        llm_categories = []  # LLM 直接返回的分类
        
        for m in MODELS:
            short = m['short_name']
            m_id = m['model_name']
            raw_text = model_res.get(m_id, None)
            
            # None 表示该模型 API 调用失败，跳过投票
            if raw_text is None:
                n_api_failures += 1
                per_model_cols[f"{short}_verified"].append(None)
                per_model_cols[f"{short}_sentiment"].append(None)
                per_model_cols[f"{short}_verification_confidence"].append(0.0)
                per_model_cols[f"{short}_sentiment_confidence"].append(0.0)
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
            
            per_model_cols[f"{short}_verified"].append(v)
            per_model_cols[f"{short}_sentiment"].append(s)
            per_model_cols[f"{short}_verification_confidence"].append(jd.get('verification_confidence', 0.0))
            per_model_cols[f"{short}_sentiment_confidence"].append(jd.get('sentiment_confidence', 0.0))
            
            # 同步提取 fintech_topic 和 fintech_category（复用已解析的 jd）
            topic = jd.get('fintech_topic', None)
            if topic and str(topic).strip().lower() not in ('null', 'none', ''):
                topics.append(str(topic))
            llm_cat = jd.get('fintech_category', None)
            if llm_cat:
                cat_str = str(llm_cat).strip().replace('；', ';')
                for part in cat_str.split(';'):
                    part = part.strip()
                    if part in ('底层技术', '应用场景'):
                        llm_categories.append(part)
                        break
            
        final_v = majority_vote_bool(v_votes)
        final_s = majority_vote_sentiment(s_votes) if final_v else "中性"
        
        # 计算一致性：有效投票中支持 majority 的比例
        n_valid_votes = len(v_votes)
        agree_v_count = sum(1 for x in v_votes if x == final_v)
        agree_rate = agree_v_count / n_valid_votes if n_valid_votes > 0 else 0.0
        
        llm_verified_arr.append(final_v)
        llm_sentiment_arr.append(final_s)
        agreement_rate_arr.append(agree_rate)
        
        # 金融科技主题标准化分类
        combined_topic = ' '.join(topics) if topics else ''
        kw_category, kw_confidence = canonicalize_topic(combined_topic)
        
        if llm_categories:
            cat_votes = Counter(llm_categories)
            llm_majority_cat = cat_votes.most_common(1)[0][0] if cat_votes else kw_category
            if llm_majority_cat == kw_category:
                final_confidence = min(kw_confidence + 0.2, 1.0)
            else:
                final_confidence = round(kw_confidence * 0.5, 3)
            fintech_category_arr.append(llm_majority_cat)
            category_confidence_arr.append(final_confidence)
        else:
            fintech_category_arr.append(kw_category)
            category_confidence_arr.append(kw_confidence)
    
    # 批量赋值各模型独立判断列
    for col_name, col_values in per_model_cols.items():
        df[col_name] = col_values
    
    df['llm_verified'] = llm_verified_arr
    df['llm_sentiment'] = llm_sentiment_arr
    df['llm_agreement_rate'] = agreement_rate_arr
    df['fintech_category'] = fintech_category_arr
    df['category_confidence'] = category_confidence_arr
    
    if n_api_failures > 0:
        logger.warning(f"共有 {n_api_failures} 次模型 API 调用失败，已从对应投票中排除")
    
    # 统计分类分布
    if df['llm_verified'].sum() > 0:
        verified_df = df[df['llm_verified']]
        cat_counts = verified_df['fintech_category'].value_counts()
        for cat, cnt in cat_counts.items():
            logger.info(f"  金融科技分类 [{cat}]: {cnt}")
    
    # 结果统计
    total_len = len(df)
    passed_len = df['llm_verified'].sum()
    logger.info(f"多数决判定为真: {passed_len}/{total_len} ({passed_len/total_len*100:.1f}%)")
    
    if passed_len > 0:
        sent_counts = df[df['llm_verified']]['llm_sentiment'].value_counts()
        for s_type, cnt in sent_counts.items():
            logger.info(f"  [{s_type}]: {cnt} ({cnt/passed_len*100:.1f}%)")
            
    # 保存全量结果（含 llm_verified=True 和 False），供验证模块使用
    full_output_filename = CONFIG.get('filenames', {}).get(
        'output_21_tone_llms_full', '21_tone_llms_full.parquet')
    full_output_path = os.path.join(CONFIG["paths"]["output_dir"], full_output_filename)
    save_dataset(df, full_output_path, logger)
    logger.info(f"全量 LLM 结果已保存: {full_output_path} ({len(df)} 行)")

    # 过滤丢弃不相关的假新闻
    df_filtered = df[df['llm_verified'] == True].copy()
    
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
