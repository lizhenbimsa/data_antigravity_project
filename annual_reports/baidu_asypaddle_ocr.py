# PaddleOCR 批量并行处理脚本
# pip install requests fitz(PyMuPDF)

import fitz  # PyMuPDF
import json
import logging
import os
import requests
import sys
import tempfile
import time
from datetime import datetime, time as dt_time, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter


# ======================== 配置 ========================
# 配置重试策略
retry_strategy = Retry(
    total=150,  # 最大重试次数
    backoff_factor=0,  # 重试间隔时间因子 (1s, 2s, 4s, 8s, 16s, ...)
    status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的状态码
    allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"] # 需要重试的方法
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

JOB_URL = "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs"
TOKEN = os.environ.get("PADDLE_OCR_TOKEN", "b74a03cf89c633dc8f17e6e07e6ea724af3cbc11")
MODEL = "PaddleOCR-VL-1.5"  # 可选: "PaddleOCR-VL-1.5", "PaddleOCR-VL", "PP-StructureV3"

# 配置日志
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = os.path.join(LOG_DIR, f"ocr_process_{timestamp}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# 运行时间窗口配置
START_TIME = dt_time(0, 1)  
END_TIME   = dt_time(23, 59) 

# 输入输出目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# 并行处理的最大线程数
MAX_WORKERS = 1

# PDF 拆分配置
MAX_FILE_SIZE_MB = 50   # 文件上传大小限制 (MB)
SPLIT_PAGES = 30        # 拆分时每块的页数

OPTIONAL_PAYLOAD = {
    "markdownIgnoreLabels": [
        "header",
        "header_image",
        "footer",
        "footer_image",
        "number",
        "footnote",
        "aside_text"
    ],
    "useDocOrientationClassify": False,
    "useDocUnwarping": False,
    "useLayoutDetection": True,
    "useChartRecognition": False,
    "useSealRecognition": True,
    "useOcrForImageBlock": False,
    "mergeTables": True,
    "relevelTitles": True,
    "concatenatePages": True,
    "prettifyMarkdown": True,   
    "layoutShapeMode": "auto",
    "promptLabel": "ocr",
    "repetitionPenalty": 1,
    "temperature": 0,
    "topP": 1,
    "minPixels": 147384,
    "maxPixels": 2822400,
    "layoutNms": True,
    "restructurePages": True,
    "visualize": False,
}


def is_run_window():
    """检查当前时间是否在允许运行的窗口内 (START_TIME - END_TIME)"""
    now = datetime.now().time()
    if START_TIME <= END_TIME:
        return START_TIME <= now <= END_TIME
    else:  # 跨午夜的情况 (虽然当前配置是 4-6 点，但也处理一下通用逻辑)
        return now >= START_TIME or now <= END_TIME


def split_pdf(file_path, pages_per_split=SPLIT_PAGES):
    """将大 PDF 拆分为多个小 PDF 文件。
    
    Args:
        file_path: 原始 PDF 文件路径
        pages_per_split: 每个分片的页数
    
    Returns:
        分片文件路径列表（按顺序）
    """
    doc = fitz.open(file_path)
    total_pages = len(doc)
    file_name = os.path.basename(file_path)
    base_name = os.path.splitext(file_name)[0]
    
    # 在 input 目录下创建临时目录存放分片
    temp_dir = os.path.join(os.path.dirname(file_path), f".split_{base_name}")
    os.makedirs(temp_dir, exist_ok=True)
    
    split_files = []
    for start_page in range(0, total_pages, pages_per_split):
        end_page = min(start_page + pages_per_split, total_pages)
        part_num = len(split_files) + 1
        part_path = os.path.join(temp_dir, f"{base_name}_part{part_num:03d}.pdf")
        
        # 如果分片已存在则跳过（支持断点续传）
        if not os.path.exists(part_path):
            part_doc = fitz.open()
            part_doc.insert_pdf(doc, from_page=start_page, to_page=end_page - 1)
            part_doc.save(part_path)
            part_doc.close()
        
        split_files.append(part_path)
    
    doc.close()
    logging.info(f"[拆分] {file_name}: {total_pages} 页 -> {len(split_files)} 个分片 (每片 {pages_per_split} 页)")
    return split_files, temp_dir


def create_ocr_job(file_path):
    """创建 OCR 任务"""
    headers = {"Authorization": f"bearer {TOKEN}"}
    
    try:
        if file_path.startswith("http"):
            headers["Content-Type"] = "application/json"
            payload = {
                "fileUrl": file_path,
                "model": MODEL,
                "optionalPayload": OPTIONAL_PAYLOAD
            }
            response = http.post(JOB_URL, json=payload, headers=headers, timeout=60)
        else:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            data = {
                "model": MODEL,
                "optionalPayload": json.dumps(OPTIONAL_PAYLOAD)
            }
            
            with open(file_path, "rb") as f:
                files = {"file": f}
                response = http.post(JOB_URL, headers=headers, data=data, files=files, timeout=120)
        
        if response.status_code != 200:
            raise Exception(f"创建任务失败: {response.status_code} - {response.text}")
        
        return response.json()["data"]["jobId"]
    except requests.exceptions.RequestException as e:
        raise Exception(f"创建任务网络错误: {e}")


def poll_job_status(job_id, max_wait_minutes=30):
    """轮询任务状态"""
    headers = {"Authorization": f"bearer {TOKEN}"}
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60
    
    while True:
        if time.time() - start_time > max_wait_seconds:
            raise TimeoutError(f"任务 {job_id} 超时")
        
        try:
            response = http.get(f"{JOB_URL}/{job_id}", headers=headers, timeout=30)
            if response.status_code != 200:
                raise Exception(f"查询状态失败: {response.status_code}")
            
            data = response.json()["data"]
            state = data["state"]
            
            if state == 'done':
                return data['resultUrl']['jsonUrl']
            elif state == 'failed':
                raise Exception(f"任务失败: {data.get('errorMsg', '未知错误')}")
        except requests.exceptions.RequestException as e:
            logging.warning(f"查询任务状态网络错误 (重试中): {e}")
            # 网络错误时，不立即抛出异常，而是继续循环等待
            pass
        
        time.sleep(5)


def download_results_text(jsonl_url):
    """下载结果并返回解析后的文本列表"""
    try:
        response = http.get(jsonl_url, timeout=60)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"下载结果失败: {e}")
    
    lines = response.text.strip().split('\n')
    page_texts = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            result = json.loads(line)["result"]
            for res in result["layoutParsingResults"]:
                page_texts.append(res["markdown"]["text"])
        except Exception as e:
            logging.warning(f"解析结果行失败: {e}")
            continue
            
    return page_texts


def save_text(content_list, output_path):
    """保存文本列表到文件"""
    final_text = '\n\n'.join(content_list)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_text)
    return len(content_list)



def _ocr_single_pdf(file_path):
    """对单个 PDF 文件执行 OCR 处理（创建任务、轮询、下载结果）。
    
    Returns:
        OCR 提取的文本列表（每页一个元素）
    """
    file_name = os.path.basename(file_path)
    job_id = create_ocr_job(file_path)
    logging.info(f"[任务创建] {file_name} -> job_id: {job_id}")
    
    jsonl_url = poll_job_status(job_id)
    logging.info(f"[任务完成] {file_name}")
    
    texts = download_results_text(jsonl_url)
    return texts


def process_single_file(file_path, output_dir):
    """处理单个 PDF 文件，超大文件自动拆分处理后合并结果"""
    file_name = os.path.basename(file_path)
    base_name = os.path.splitext(file_name)[0]
    output_path = os.path.join(output_dir, f"{base_name}.md")
    
    # 检查是否已处理过
    if os.path.exists(output_path):
        logging.info(f"[跳过] {file_name} - 已存在输出文件")
        return {"file": file_name, "status": "skipped", "message": "已存在输出文件"}
    
    try:
        logging.info(f"[开始] {file_name}")
        
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        if file_size_mb <= MAX_FILE_SIZE_MB:
            # 普通文件：直接处理
            texts = _ocr_single_pdf(file_path)
        else:
            # 超大文件：拆分 -> 分别 OCR -> 合并结果
            logging.info(f"[大文件] {file_name}: {file_size_mb:.1f}MB 超过 {MAX_FILE_SIZE_MB}MB 限制，开始拆分处理...")
            split_files, temp_dir = split_pdf(file_path)
            
            texts = []
            try:
                for idx, part_path in enumerate(split_files, 1):
                    logging.info(f"[分片 {idx}/{len(split_files)}] 处理 {os.path.basename(part_path)}")
                    part_texts = _ocr_single_pdf(part_path)
                    texts.extend(part_texts)
            finally:
                # 清理临时分片文件
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                    logging.info(f"[清理] 已删除临时目录 {temp_dir}")
                except Exception as cleanup_err:
                    logging.warning(f"[清理] 删除临时目录失败: {cleanup_err}")
        
        # 保存合并后的结果
        page_count = save_text(texts, output_path)
        logging.info(f"[保存成功] {file_name} -> {page_count} 页已保存到 {output_path}")
        
        return {"file": file_name, "status": "success", "pages": page_count}
        
    except Exception as e:
        error_msg = str(e)
        if "12001" in error_msg or "每日页数上限" in error_msg or "403" in error_msg:
            logging.error(f"[错误] {file_name}: 每日限额已达 ({error_msg})")
            return {"file": file_name, "status": "limit_reached", "message": error_msg}
        else:
            logging.error(f"[错误] {file_name}: {error_msg}")
            return {"file": file_name, "status": "error", "message": error_msg}


def process_batch(input_dir, output_dir, max_workers=3, max_retries=1000):
    """批量并行处理目录中的所有 PDF 文件，支持失败重试"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有 PDF 文件
    pdf_files = [
        os.path.join(input_dir, f) 
        for f in os.listdir(input_dir) 
        if f.lower().endswith('.pdf')
    ]
    
    if not pdf_files:
        logging.warning(f"在 {input_dir} 中未找到 PDF 文件")
        return
    
    logging.info(f"发现 {len(pdf_files)} 个 PDF 文件，开始并行处理（最大 {max_workers} 个线程）...")
    logging.info("=" * 60)
    
    # 初始化待处理文件列表
    pending_files = pdf_files.copy()
    all_results = []
    retry_count = 0
    # 注意：limit_reached_monitor_count 是跨轮次累计的，这是有意设计。
    # 即使分散在多轮中，总计达到 15 次限额错误就会停止今日处理，避免无效请求浪费。
    limit_reached_monitor_count = 0
    
    while pending_files and retry_count < max_retries:
        if retry_count > 0:
            # 指数退避：初始30秒，每次翻倍，最高60分钟（3600秒）
            wait_seconds = min(30 * (2 ** (retry_count - 1)), 3600)
            wait_display = f"{wait_seconds}秒" if wait_seconds < 60 else f"{wait_seconds // 60}分钟{wait_seconds % 60}秒" if wait_seconds % 60 else f"{wait_seconds // 60}分钟"
            logging.info(f"\n{'=' * 60}")
            logging.info(f"[重试 {retry_count}/{max_retries}] 还有 {len(pending_files)} 个文件需要重试，等待 {wait_display} 后开始...")
            logging.info("=" * 60)
            time.sleep(wait_seconds)
        
        # 检查是否在运行时间窗口内 (轮次开始前检查)
        if not is_run_window():
            logging.info(f"\n[暂停] 当前时间 {datetime.now().strftime('%H:%M:%S')} 不在运行窗口 ({START_TIME} - {END_TIME})，暂停处理。")
            return

        current_results = []
        chunk_size = 20  # 每 20 个文件检查一次时间
        
        # 分块处理
        for i in range(0, len(pending_files), chunk_size):
            # 每次处理一个 chunk 前都检查时间
            if not is_run_window():
                logging.info(f"\n[暂停] 批处理中途检查：当前时间 {datetime.now().strftime('%H:%M:%S')} 不在运行窗口，暂停处理。")
                return

            chunk_files = pending_files[i : i + chunk_size]
            
            chunk_results = []
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_file = {
                    executor.submit(process_single_file, pdf_file, output_dir): pdf_file 
                    for pdf_file in chunk_files
                }
                
                for future in as_completed(future_to_file):
                    pdf_file = future_to_file[future]
                    try:
                        result = future.result()
                    except Exception as e:
                        logging.error(f"[未预期异常] {os.path.basename(pdf_file)}: {e}")
                        result = {"file": os.path.basename(pdf_file), "status": "error", "message": str(e)}
                    
                    # 防御性检查：如果 process_single_file 意外返回 None
                    if result is None:
                        logging.error(f"[异常] {os.path.basename(pdf_file)}: 处理函数返回了 None")
                        result = {"file": os.path.basename(pdf_file), "status": "error", "message": "处理函数返回了 None"}
                    
                    current_results.append(result)
                    chunk_results.append(result)
            
            # 统计本次 chunk 的限额错误并累加
            limit_this_chunk = sum(1 for r in chunk_results if r["status"] == "limit_reached")
            limit_reached_monitor_count += limit_this_chunk
            
            # 检查是否达到累计阈值
            if limit_reached_monitor_count >= 15:
                logging.warning(f"\n[停止] 已累计检测到 {limit_reached_monitor_count} 次每日限额，停止今日处理...")
                return "limit_stopped"

        # 分离成功和失败的文件
        failed_files = []
        for result in current_results:
            if result["status"] in ["error", "limit_reached"]: # limit_reached 也视为失败需要重试（在此逻辑中，但上面已经 return 了，所以这里主要是 error）
                 # 获取完整路径
                file_path = next(
                    (f for f in pending_files if os.path.basename(f) == result["file"]), 
                    None
                )
                if file_path:
                    failed_files.append(file_path)
            all_results.append(result)
        

        
        # 更新待处理文件列表为失败的文件
        pending_files = failed_files
        retry_count += 1
        
        # 打印当前轮次状态
        success_this_round = sum(1 for r in current_results if r["status"] == "success")
        skip_this_round = sum(1 for r in current_results if r["status"] == "skipped")
        error_this_round = sum(1 for r in current_results if r["status"] == "error")
        limit_this_round = sum(1 for r in current_results if r["status"] == "limit_reached")
        
        logging.info(f"\n[轮次 {retry_count}] 成功: {success_this_round}, 跳过: {skip_this_round}, 失败: {error_this_round}, 限额: {limit_this_round}")
        
        # 如果没有失败的文件，提前退出
        if not pending_files:
            logging.info("\n所有文件处理完成！")
            break
    
    # 打印最终汇总
    logging.info("\n" + "=" * 60)
    logging.info("最终处理结果汇总：")
    
    # 统计每个文件的最终状态（取最后一次处理结果，后续结果覆盖前次）
    final_status = {}
    for result in all_results:
        file_name = result["file"]
        final_status[file_name] = result
    
    success_count = sum(1 for r in final_status.values() if r["status"] == "success")
    skip_count = sum(1 for r in final_status.values() if r["status"] == "skipped")
    error_count = sum(1 for r in final_status.values() if r["status"] == "error")
    
    logging.info(f"  总文件数: {len(pdf_files)}")
    logging.info(f"  成功: {success_count}")
    logging.info(f"  跳过: {skip_count}")
    logging.info(f"  失败: {error_count}")
    logging.info(f"  总重试次数: {retry_count}")
    
    if error_count > 0:
        logging.info("\n最终失败的文件：")
        for file_name, result in final_status.items():
            if result["status"] == "error":
                logging.error(f"  - {file_name}: {result['message']}")


if __name__ == "__main__":
    logging.info(f"启动自动运行脚本，计划运行时间: 每天 {START_TIME} - {END_TIME}")
    
    while True:
        now = datetime.now()
        
        if is_run_window():
            logging.info(f"\n[激活] 当前时间 {now.strftime('%Y-%m-%d %H:%M:%S')} 在运行窗口内，开始处理...")
            try:
                status = process_batch(INPUT_DIR, OUTPUT_DIR, MAX_WORKERS)
                if status == "limit_stopped":
                    # 统计当前输出目录下的 markdown 文件数量
                    md_files = [f for f in os.listdir(OUTPUT_DIR) if f.lower().endswith('.md')]
                    total_count = len(md_files)
                    
                    # 统计每家银行的文件数量
                    bank_counts = Counter()
                    for f in md_files:
                        parts = f.split('_')
                        if len(parts) >= 2:
                            bank_name = parts[1]
                            bank_counts[bank_name] += 1
                        else:
                            bank_counts["Unknown"] += 1
                    
                    if bank_counts:
                        logging.info("[统计] 各银行生成情况:")
                        for bank, count in bank_counts.most_common():
                            logging.info(f"  - {bank}: {count} 个")

                    logging.info(f"\n[统计] 当前已生成总文件数: {total_count}")

                    # 强制休眠直到明天开始时间
                    next_run = datetime.combine(now.date(), START_TIME) + timedelta(days=1)
                    wait_seconds = (next_run - now).total_seconds()
                    
                    wait_hours = int(wait_seconds // 3600)
                    wait_minutes = int((wait_seconds % 3600) // 60)
                    
                    logging.info(f"[休眠] 触发限额保护。将在 {next_run.strftime('%Y-%m-%d %H:%M:%S')} 唤醒 (等待约 {wait_hours} 小时 {wait_minutes} 分钟)...")
                    time.sleep(wait_seconds)
                    continue

                logging.info("[完成] 本次批处理结束，休眠 60 秒后检查...")
            except Exception as e:
                logging.error(f"[错误] 批处理过程中发生异常: {e}")
            
            # 批处理完成后（或异常退出后），短暂休眠避免死循环空转，然后再次检查时间
            time.sleep(60)
            
        else:
            # 计算距离下一个开始时间的秒数
            # 如果当前时间早于开始时间，则是今天开始
            # If current time is earlier than start time, it's today's start time
            next_run = datetime.combine(now.date(), START_TIME)
            if now.time() > END_TIME:
                # 如果当前时间晚于结束时间，则是明天的开始时间
                # If current time is later than end time, it's tomorrow's start time
                next_run += timedelta(days=1)
            elif now.time() < START_TIME:
                 # 如果当前时间早于开始时间，目标就是今天的开始时间，不需要加一天
                 pass
            
            wait_seconds = (next_run - now).total_seconds()
            
            # 防止微小的计算误差导致的负数
            if wait_seconds < 0:
                wait_seconds = 0
            
            wait_hours = int(wait_seconds // 3600)
            wait_minutes = int((wait_seconds % 3600) // 60)
            
            logging.info(f"[休眠] 当前时间 {now.strftime('%Y-%m-%d %H:%M:%S')} 不在运行窗口。")
            logging.info(f"       将在 {next_run.strftime('%Y-%m-%d %H:%M:%S')} 唤醒 (等待约 {wait_hours} 小时 {wait_minutes} 分钟)...")
            
            time.sleep(wait_seconds)

