import pandas as pd
from openai import OpenAI
import time
import os
import json
from typing import List, Dict, Optional
import concurrent.futures
from tqdm import tqdm

# 大模型参数说明： https://docs.aimlapi.com/api-references/text-models-llm/openai/gpt-5-nano
# 官方提示词优化： https://platform.openai.com/chat/edit?models=gpt-5&optimize=true
# --- 1. 配置信息 ---
# 重要：请将 'sk-xxxxx' 替换为您自己的 API 密钥
BASE_URL = "https://yunwu.ai/v1"
API_KEY = "***ROTATED-2026-05-09***"
MODEL_NAME = "gpt-5-nano-2025-08-07"

TIMEOUT     = 600                   # 请求超时时间（秒）
MAX_RETRIES = 500                     # 最大重试次数
RETRY_DELAY = 10                    # 重试前的等待时间（秒）
MAX_CONCURRENCY = 10000   # 并行调用API的数量

INPUT_FILE  = 'news_input_small.xlsx'     # 输入文件名
OUTPUT_FILE = 'news_output.xlsx'    # 输出文件名

# 情感词典文件路径 (Du et al., 2022)
TONE_DICTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               '..', 'news_process', 'config', 'tone_dicts.json')

# --- 2. 输出列定义 ---
EXPECTED_COLUMNS = [
    'docid', '题目银行实体', '内容银行实体', '是否提及境内银行', '标题的情感',
    '标题的情感分析理由', '内容的情感', '内容的情感分析理由'
]

# --- 3. 提示词模板 ---
# 这是您提供的，用于指导 AI 模型输出的提示词
PROMPT_TEMPLATE = """<role>
你是一位顶级的金融文本分析专家。
</role>

<objective>
分析给定的新闻“标题”和“内容”，进行银行实体识别和情感分析。
**你的回答必须且只能是一个完整的、包含单行数据的Markdown表格，从 `| docid |` 开始。严禁任何解释性文字。**
</objective>

<instructions>
**1. 银行实体识别 (目标：全面、无遗漏)**
- **识别范围**: 从“标题”和“内容”中，识别**所有**明确提及的银行机构名称（全称、简称、别称、英文名等）。
- **规范化**: 将所有识别出的名称统一为中文官方全称。
  - 示例: `工行`, `ICBC`, `Industrial and Commercial Bank of China` 均转化为 `中国工商银行`。
  - 示例: `BoC` 转化为 `中国银行`。
- **银行定义**: 仅包括央行、政策性银行、商业银行、信用社等，**严格排除**券商、保险、基金公司、普通企业（如`华为`）及政府机构（央行除外）。
- **输出**:
  - `题目银行实体`: 来源于“标题”的银行实体。
  - `内容银行实体`: 来源于“内容”的银行实体。
  - 若未识别到，则对应字段留空。

**2. 情感分析 (目标：精准、客观、基于事实)**
- **分析对象**: 若提及多个银行，你的分析应**聚焦于新闻主旨讨论的、或受事件影响最核心的银行**。
- **是否提及境内银行**: 判断“内容”中是否出现中国境内银行。若是，则为`是`，否则为`否`。

- **情感判断 (`积极`/`中性`/`消极`)**:
  - **核心原则**: **严格基于**事件对银行**基本面（如盈利能力、资产质量、资本充足率、风险水平、市场竞争力、监管评级）**的**直接或间接的、可预见的**影响。**忽略文章作者的主观语气或情绪化用词**。
  - **思维链**:
    1.  识别新闻报道的核心事件。
    2.  判断该事件对核心银行的基本面会产生什么具体影响。
    3.  根据影响的性质和程度，做出情感判断。

  - **判断标准与示例**:
    - `积极`: 事件**明确**对银行基本面产生**正面**影响。
    - `中性`: 事件为常规性信息披露，或对银行基本面**无实质性、可衡量的**影响。
    - `消极`: 事件**明确**对银行基本面产生**负面**影响。

{sentiment_dict_section}

- **情感分析理由**: **简要、精确**地说明做出情感判断的核心原因，**必须聚焦于对银行基本面的具体影响**。

<output_format>
**1. 字段 (必须完全一致)**:
`docid`, `题目银行实体`, `内容银行实体`, `是否提及境内银行`, `标题的情感`, `标题的情感分析理由`, `内容的情感`, `内容的情感分析理由`

**2. 格式**:
- **分隔符**: `题目银行实体`和`内容银行实体`列中若有多个实体，使用**中文分号(；)**分隔。
- **示例**:
```markdown
| docid | 题目银行实体 | 内容银行实体 | 是否提及境内银行 | 标题的情感 | 标题的情感分析理由 | 内容的情感 | 内容的情感分析理由 |
|---|---|---|---|---|---|---|---|
| 2030102800009501613 | 中国工商银行 | 中国工商银行；中国建设银行 | 是 | 积极 | 银行与科技公司合作是积极信号。 | 积极 | 合作有助于银行数字化转型，提升竞争力。 |
```
</output_format>

<task>
现在，请根据以下新闻内容进行分析：
</task>
"""


# --- 3.5 加载情感词典参考 ---

def _load_sentiment_dict_section() -> str:
    """
    从 tone_dicts.json 加载以下词典，生成嵌入 prompt 的参考文本段落：
    - Du et al. (2022, Review of Finance)：正面词、政治正面词、负面词
    - You et al. (2018, Review of Financial Studies)：正面词、负面词、确定性词、模糊性词
    """
    if not os.path.exists(TONE_DICTS_FILE):
        print(f"[警告] 情感词典文件未找到: {TONE_DICTS_FILE}，将不使用词典参考")
        return ""
    try:
        with open(TONE_DICTS_FILE, 'r', encoding='utf-8') as f:
            all_dicts = json.load(f)

        sections = []

        # --- Du et al. (2022) ---
        du = all_dicts.get('du_2022', {})
        if du:
            du_pos = du.get('positive', [])
            du_pol = du.get('political_positive', [])
            du_neg = du.get('negative', [])
            sections.append(
                "  - **情感词汇参考① Du et al. (2022, Review of Finance)**:\n"
                "    基于310万篇财经新闻，Word2Vec方法构建，供辅助参考。\n"
                "    - **正面词** (共{pc}个，示例): {ps}\n"
                "    - **政治正面词** (共{lc}个，与股票收益相关性较弱，示例): {ls}\n"
                "    - **负面词** (共{nc}个，示例): {ns}".format(
                    pc=len(du_pos), ps='、'.join(du_pos[:25]) + '……',
                    lc=len(du_pol), ls='、'.join(du_pol[:15]) + '……',
                    nc=len(du_neg), ns='、'.join(du_neg[:25]) + '……'
                )
            )
            print(f"[信息] 已加载 Du et al. (2022): 正面{len(du_pos)}, 政治正面{len(du_pol)}, 负面{len(du_neg)}")

        # --- You et al. (2018) ---
        you = all_dicts.get('you_2018', {})
        if you:
            you_pos = you.get('positive', [])
            you_neg = you.get('negative', [])
            you_cert = you.get('certain', [])
            you_unc = you.get('uncertain', [])
            sections.append(
                "  - **情感词汇参考② You et al. (2018, Review of Financial Studies)**:\n"
                "    人工审阅2000篇金融新闻 + LM词典中文翻译，包含情感维度和确定性维度，供辅助参考。\n"
                "    - **正面词** (共{pc}个，示例): {ps}\n"
                "    - **负面词** (共{nc}个，示例): {ns}\n"
                "    - **确定性词** (共{cc}个，示例): {cs}\n"
                "    - **模糊性词** (共{uc}个，示例): {us}".format(
                    pc=len(you_pos), ps='、'.join(you_pos[:20]) + '……',
                    nc=len(you_neg), ns='、'.join(you_neg[:20]) + '……',
                    cc=len(you_cert), cs='、'.join(you_cert[:15]) + '……',
                    uc=len(you_unc), us='、'.join(you_unc[:15]) + '……'
                )
            )
            print(f"[信息] 已加载 You et al. (2018): 正面{len(you_pos)}, 负面{len(you_neg)}, 确定性{len(you_cert)}, 模糊性{len(you_unc)}")

        if not sections:
            print("[警告] tone_dicts.json 中未找到 du_2022 或 you_2018 词典")
            return ""

        return '\n'.join(sections)

    except Exception as e:
        print(f"[警告] 加载情感词典失败: {e}")
        return ""

# 加载词典参考段落并嵌入 prompt
_SENTIMENT_DICT_SECTION = _load_sentiment_dict_section()
PROMPT_TEMPLATE = PROMPT_TEMPLATE.format(sentiment_dict_section=_SENTIMENT_DICT_SECTION)


# --- 4. 定义核心功能函数 ---

def get_analysis_from_openai(content: str, client: OpenAI) -> Optional[str]:
    """
    将单条新闻内容发送到 OpenAI API 进行分析，并处理重试逻辑。
    """
    last_exception = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": content}],
            )
            return response.choices[0].message.content
        except (OpenAI.APIError, OpenAI.APITimeoutError, OpenAI.RateLimitError, OpenAI.APIConnectionError) as e:
            last_exception = e
            print(f"\n[API 警告] 调用API时遇到临时错误 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}。将在 {RETRY_DELAY} 秒后重试...")
            time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"\n[严重错误] 调用API时发生未知错误: {e}。这将导致当前条目处理失败并重试。")
            return None # 发生未知错误，直接返回None以触发上层重试
    print(f"\n[API 错误] 达到最大重试次数 ({MAX_RETRIES}) 后，API调用仍然失败。最后一次错误: {last_exception}")
    return None

def parse_markdown_table(markdown_text: str) -> Optional[pd.DataFrame]:
    """
    将API返回的Markdown表格字符串解析为DataFrame。
    此函数经过强化，可以忽略表格前后的额外文本，并标准化列名。
    """
    try:
        if not markdown_text:
            print("  [警告] API响应为空，无法解析。")
            return None
        # 1. 找到Markdown表格的所有行
        lines = markdown_text.strip().split('\n')
        table_lines_raw = [line for line in lines if '|' in line]

        if len(table_lines_raw) < 3: # 至少需要表头、分隔线和数据行
            print(f"  [警告] API响应中未找到有效的Markdown表格结构。响应预览: {markdown_text[:200]}...")
            return None

        # 2. 提取表头并验证
        header_parts = [h.strip() for h in table_lines_raw[0].split('|') if h.strip()]
        if len(header_parts) != len(EXPECTED_COLUMNS):
            print(f"  [警告] 表头列数 ({len(header_parts)}) 与预期 ({len(EXPECTED_COLUMNS)}) 不符。")
            return None

        # 3. 智能解析数据行，处理单元格内换行
        data_lines = table_lines_raw[2:]
        full_data_row_str = "\n".join(data_lines)

        # 4. 移除行首和行尾的'|'
        if full_data_row_str.startswith('|'):
            full_data_row_str = full_data_row_str[1:]
        if full_data_row_str.endswith('|'):
            full_data_row_str = full_data_row_str[:-1]

        # 5. 按'|'分割，现在每个部分就是一列的完整内容（包含换行符）
        parts = [p.strip() for p in full_data_row_str.split('|')]

        if len(parts) != len(EXPECTED_COLUMNS):
            print(f"  [警告] 解析出的数据列数 ({len(parts)}) 与预期 ({len(EXPECTED_COLUMNS)}) 不符。")
            return None

        # 4. 构建DataFrame
        df = pd.DataFrame([parts], columns=EXPECTED_COLUMNS)
        # 5. 清理数据：移除多余的空白字符，并将NaN值替换为空字符串
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x).fillna('')
        return df
    except Exception as e:
        print(f"  [错误] 解析API响应时出错: {e}")
        return None

def load_news_data(filepath: str) -> List[Dict]:
    """从Excel文件加载新闻数据并进行验证。"""
    start_time = time.monotonic()
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"输入文件 '{filepath}' 未找到。请确保文件存在于正确路径。")

    df = pd.read_excel(filepath)
    required_columns = ['docid', '标题', '内容']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"输入文件 '{filepath}' 必须包含以下列: {', '.join(required_columns)}")

    news_items = df[required_columns].to_dict('records')
    if not news_items:
        raise ValueError(f"输入文件 '{filepath}' 为空或没有数据。")

    duration = time.monotonic() - start_time
    print(f"\n[步骤 1/3] 成功从 '{filepath}' 读取 {len(news_items)} 条新闻。(耗时: {duration:.2f} 秒)")
    return news_items

def _process_single_item(item_with_index: dict, client: OpenAI) -> Optional[pd.DataFrame]:
    """
    处理单条新闻的完整流程：构建提示、调用API、解析结果。
    此函数为内部辅助函数，用于并行处理。
    """
    index, item = item_with_index['index'], item_with_index['data']
    item_num = index + 1

    # 准备提交给API的内容
    item_content = f"docid: {item['docid']}\n标题: {item['标题']}\n内容: {item['内容']}"
    full_prompt = PROMPT_TEMPLATE + "\n\n" + item_content

    # 获取并解析分析结果
    raw_analysis = get_analysis_from_openai(full_prompt, client)

    item_df = parse_markdown_table(raw_analysis)
    if item_df is not None:
        # 解析成功，返回DataFrame
        return item_df
    else:
        # 解析失败，打印警告并返回None，这将触发重试机制
        print(f"\n[警告] 第 {item_num} 条新闻 (docid: {item['docid']}) 解析失败，将自动重试。")
        return None

def process_all_news(news_items: List[Dict], client: OpenAI) -> pd.DataFrame:
    """
    使用线程池并行处理所有新闻条目。
    对处理失败的条目进行自动重试，直到达到每个条目的最大重试次数。
    """
    start_time = time.monotonic()
    print(f"\n[步骤 2/3] 开始并行处理 {len(news_items)} 条新闻 (最大并行数: {MAX_CONCURRENCY})...")

    # 为每个条目添加重试计数器
    items_with_retry = [{'index': i, 'data': item, 'retries': 0} for i, item in enumerate(news_items)]

    results = [None] * len(news_items)
    items_to_process = list(items_with_retry)

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENCY) as executor:
        with tqdm(total=len(news_items), desc="处理新闻中") as pbar:
            futures = {executor.submit(_process_single_item, item, client): item for item in items_to_process}

            while futures:
                done, _ = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)

                for future in done:
                    item = futures.pop(future)
                    result = future.result()

                    if isinstance(result, pd.DataFrame):
                        results[item['index']] = result
                        pbar.update(1)
                    else:
                        item['retries'] += 1
                        if item['retries'] < MAX_RETRIES:
                            print(f"\n> 条目 {item['index']+1} (docid: {item['data']['docid']}) 处理失败，将进行第 {item['retries']}/{MAX_RETRIES} 次重试...")
                            # 将失败的任务重新提交给线程池
                            new_future = executor.submit(_process_single_item, item, client)
                            futures[new_future] = item
                        else:
                            print(f"\n[严重错误] 条目 {item['index']+1} (docid: {item['data']['docid']}) 达到最大重试次数，已放弃。")
                            # 标记为失败并更新进度条，以防进度条卡住
                            results[item['index']] = f"Failed after {MAX_RETRIES} retries"
                            pbar.update(1)

    duration = time.monotonic() - start_time
    print(f"\n> 所有新闻处理完成，正在合并结果... (处理耗时: {duration:.2f} 秒)")
    successful_results = [df for df in results if isinstance(df, pd.DataFrame)]
    return pd.concat(successful_results, ignore_index=True) if successful_results else pd.DataFrame()

def save_results_to_excel(df: pd.DataFrame, filepath: str):
    """将最终的DataFrame保存到Excel文件，并在文件被占用时尝试使用带时间戳的新文件名。"""
    start_time = time.monotonic()
    try:
        print(f"\n[步骤 3/3] 正在将 {len(df)} 条记录保存到 '{filepath}'...")
        df.to_excel(filepath, index=False, engine='openpyxl')
        duration = time.monotonic() - start_time
        print(f"\n--- 任务成功完成！ ---")
        print(f"结果已保存到 '{filepath}'。(保存耗时: {duration:.2f} 秒)")
    except PermissionError:
        print(f"\n[警告] 保存文件失败：权限不足或文件 '{filepath}' 被占用。")
        print("将尝试使用带时间戳的新文件名进行保存...")
        try:
            base, ext = os.path.splitext(filepath)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            new_filepath = f"{base}_{timestamp}{ext}"
            
            print(f"正在尝试保存到新文件 '{new_filepath}'...")
            df.to_excel(new_filepath, index=False, engine='openpyxl')
            
            duration = time.monotonic() - start_time
            print(f"\n--- 任务成功完成！ ---")
            print(f"结果已保存到 '{new_filepath}'。(保存耗时: {duration:.2f} 秒)")
        except Exception as e:
            print(f"\n[严重错误] 尝试使用新文件名 '{new_filepath}' 保存仍然失败: {e}")
            print("请检查文件权限或磁盘空间。")
    except Exception as e:
        print(f"\n[错误] 保存结果到 Excel 文件时发生未知错误: {e}")

def main():
    """主执行函数，协调整个分析流程。"""
    total_start_time = time.monotonic()
    print("--- 开始执行媒体情绪分析任务 ---")
    try:
        # 初始化 OpenAI 客户端
        client = OpenAI(base_url=BASE_URL, api_key=API_KEY, timeout=TIMEOUT)

        # 1. 加载数据
        news_items = load_news_data(INPUT_FILE)

        # 2. 处理数据
        final_df = process_all_news(news_items, client)

        # 3. 保存结果
        if final_df is not None and not final_df.empty:
            save_results_to_excel(final_df, OUTPUT_FILE)
        else:
            print("\n--- 任务完成，但没有生成任何结果可供保存。---")
            print("请检查输入文件和 API 连接，并查看之前的步骤是否有错误信息。")

    except (FileNotFoundError, ValueError) as e:
        print(f"\n[严重错误] 数据加载失败: {e}")
    except Exception as e:
        print(f"\n[严重错误] 程序执行过程中发生意外错误: {e}")
    finally:
        total_duration = time.monotonic() - total_start_time
        print(f"\n--- 任务全部结束。总耗时: {total_duration:.2f} 秒 ---")

# --- 4. 脚本入口 ---
if __name__ == "__main__":
    main()
