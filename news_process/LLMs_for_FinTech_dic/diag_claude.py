"""
诊断脚本：测试Claude模型判别接口返回内容
只发送3个关键词，观察实际返回的原始文本

【D6 裁定, 2026-07-14】本脚本刻意绕过 LLMCache 与目录级 `LLMS_DIC_OFFLINE` 守卫，
直连 Claude API 做手动诊断（非确定性、非 $0、不落入生产缓存）——仅供开发者手动
在线排查判别接口返回格式时执行，不进入任何自动化/CI 路径。原文件名 `test_claude_diag.py`
以 `test_` 为前缀，若在本目录内裸跑 `pytest`（绕开 repo 根 `pyproject.toml::testpaths`
限制到 `news_process/tests`）会被当作测试文件收集，导入时即触发顶层付费 API 调用；
已於 D6 批次 `git mv` 改名为 `diag_claude.py`（脱离 `test_*.py` 收集模式）并把全部顶层
副作用代码收进 `if __name__ == '__main__':`，双重防线杜绝意外触发。
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import (
    JUDGE_MODELS,
    build_judge_prompt,
    get_client_config,
    get_model_params,
)
from openai import OpenAI


def main() -> None:
    # 测试用的小批量关键词
    test_keywords = ["金融科技", "区块链", "天气预报"]

    prompt = build_judge_prompt(test_keywords)
    print("=" * 60)
    print("PROMPT:")
    print(prompt)
    print("=" * 60)

    models_to_test = JUDGE_MODELS

    for model_name in models_to_test:
        print(f"\n{'=' * 60}")
        print(f"测试模型: {model_name}")
        print("=" * 60)

        config = get_client_config(model_name)
        client = OpenAI(base_url=config["base_url"], api_key=config["api_key"])
        model_params = get_model_params(model_name)

        print(f"API参数: {model_params}")
        print(f"Base URL: {config['base_url']}")

        try:
            call_kwargs = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "timeout": 120,
                **model_params,
            }
            resp = client.chat.completions.create(**call_kwargs)
            text = resp.choices[0].message.content

            print(f"\n--- 原始返回 (长度={len(text) if text else 0}) ---")
            print(text[:2000] if text else "(None)")
            print("--- 原始返回结束 ---")

            # 用同样的解析逻辑测试
            if text:
                # 去除 think 标签
                cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
                cleaned = re.sub(r"<think>.*", "", cleaned, flags=re.DOTALL)
                cleaned = re.sub(r"</think.*", "", cleaned, flags=re.DOTALL)
                cleaned = re.sub(r"```(?:json)?\s*\n?", "", cleaned)
                cleaned = cleaned.strip()

                print(f"\n--- 清洗后文本 (长度={len(cleaned)}) ---")
                print(cleaned[:2000])
                print("--- 清洗后文本结束 ---")

                try:
                    data = json.loads(cleaned)
                    print(f"\n直接JSON解析成功: keys={list(data.keys())}")
                except:
                    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
                    if match:
                        try:
                            data = json.loads(match.group())
                            print(f"\n正则提取JSON成功: keys={list(data.keys())}")
                        except:
                            print("\n正则提取后JSON解析也失败")
                            data = {}
                    else:
                        print("\n未找到花括号模式")
                        data = {}

                if data:
                    results_list = data.get("results", [])
                    if not results_list:
                        print("'results'键不存在或为空，遍历所有值...")
                        for k, v in data.items():
                            print(f"  键: '{k}', 类型: {type(v).__name__}, 值预览: {str(v)[:200]}")
                            if isinstance(v, list) and len(v) > 0:
                                results_list = v
                                break

                    if results_list:
                        print(f"\nresults_list 长度: {len(results_list)}")
                        for item in results_list[:3]:
                            print(f"  项目: {item}")
                            if isinstance(item, dict):
                                print(f"    含有 'keyword' 键: {'keyword' in item}")
                                print(f"    所有键: {list(item.keys())}")
                    else:
                        print("\n最终 results_list 为空 - 这就是失败原因!")

        except Exception as e:
            print(f"\nAPI调用失败: {e}")

    print("\n\n测试完成")


if __name__ == "__main__":
    main()
