import base64
import os
import time
import asyncio
import aiohttp

# Please make sure the requests/aiohttp library is installed
# https://aistudio.baidu.com/paddleocr/task
# 在这个网址里面可以生成所有的代码（设置）

API_URL = "https://zf13j9j6rch5w6oe.aistudio-app.com/layout-parsing"
TOKEN = "b74a03cf89c633dc8f17e6e07e6ea724af3cbc11"

input_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "input")
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

# Concurrency setting - adjust based on your machine and API limits
# Lowered to 2 to avoid hitting API rate limits (429) too quickly
MAX_CONCURRENT_REQUESTS = 1

async def read_file_async(file_path):
    """Asynchronously read a file using run_in_executor."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _read_file_sync, file_path)

def _read_file_sync(file_path):
    with open(file_path, "rb") as file:
        return file.read()

async def write_file_async(file_path, content):
    """Asynchronously write a file using run_in_executor."""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _write_file_sync, file_path, content)

def _write_file_sync(file_path, content):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

async def process_pdf(sem, session, pdf_file, input_dir, output_dir):
    file_path = os.path.join(input_dir, pdf_file)
    print(f"Starting processing: {file_path}")

    try:
        # Read file asynchronously
        file_bytes = await read_file_async(file_path)
        file_data = base64.b64encode(file_bytes).decode("ascii")
    except Exception as e:
        print(f"Error reading {pdf_file}: {e}")
        return

    headers = {
        "Authorization": f"token {TOKEN}",
        "Content-Type": "application/json"
    }

    required_payload = {
        "file": file_data,
        "fileType": 0,  # For PDF documents, set `fileType` to 0; for images, set `fileType` to 1
    }

    optional_payload = {
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
        "layoutShapeMode": "auto",
        "promptLabel": "ocr",
        "repetitionPenalty": 1,
        "temperature": 0,
        "topP": 1,
        "minPixels": 147384,
        "maxPixels": 2822400,
        "layoutNms": True,
        "restructurePages": True,

    }

    payload = {**required_payload, **optional_payload}
    
    max_retries = 1000
    
    # Process within the semaphore limit
    async with sem:
        for attempt in range(max_retries):
            try:
                # Use the session with increased timeout
                async with session.post(API_URL, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data.get("result", {})
                        
                        combined_md_content = []
                        if "layoutParsingResults" in result:
                            for res in result["layoutParsingResults"]:
                                md_text = res.get("markdown", {}).get("text", "")
                                combined_md_content.append(f"\n{md_text}")
                        
                        # Save combined file
                        combined_filename = os.path.join(output_dir, os.path.basename(file_path).replace(".pdf", ".md"))
                        await write_file_async(combined_filename, "".join(combined_md_content))
                        
                        print(f"Success: Combined Markdown document saved at {combined_filename}")
                        break
                    else:
                        print(f"Attempt {attempt+1}/{max_retries} failed for {pdf_file}, status code: {response.status}")
                        if response.status == 504:
                            print(f"Gateway Timeout (504) detected for {pdf_file}. Server might be overloaded.")
                        
                        if attempt < max_retries - 1:
                            # Cap delay at 60 seconds
                            delay = min(60, 2 * (1.5 ** attempt))
                            print(f"Retrying {pdf_file} in {delay:.1f}s...")
                            await asyncio.sleep(delay)
            except asyncio.TimeoutError:
                print(f"Attempt {attempt+1}/{max_retries} Client Timeout (sock_read) for {pdf_file}")
                if attempt < max_retries - 1:
                    delay = min(60, 2 * (1.5 ** attempt))
                    print(f"Retrying {pdf_file} in {delay:.1f}s...")
                    await asyncio.sleep(delay)
            except Exception as e:
                print(f"Attempt {attempt+1}/{max_retries} error for {pdf_file}: {e}")
                if attempt < max_retries - 1:
                    delay = min(60, 2 * (1.5 ** attempt))
                    print(f"Retrying {pdf_file} in {delay:.1f}s...")
                    await asyncio.sleep(delay)
        else:
            print(f"Given up on {pdf_file} after {max_retries} attempts.")

async def main():
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Input directory not found: {input_dir}")
        return

    # Get all PDF files
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDF files to process.")
    
    if not pdf_files:
        return

    # Create a semaphore to limit concurrent requests
    sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    # Use a single session for all requests
    # Set a custom timeout if needed, e.g., for large uploads
    # Increased sock_read to 3600s (1 hour) to handle large files/slow processing
    timeout = aiohttp.ClientTimeout(total=None, connect=60, sock_read=3600) 
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = []
        for pdf_file in pdf_files:
            task = process_pdf(sem, session, pdf_file, input_dir, output_dir)
            tasks.append(task)
        
        # Run all tasks
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    print(f"Total processing time: {time.time() - start_time:.2f} seconds")
