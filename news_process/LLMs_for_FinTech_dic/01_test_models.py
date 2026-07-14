"""
模型可用性测试脚本

测试所有大模型是否可以正常调用。
每个模型发送一个简单请求，记录成功/失败状态和耗时。

用法:
    python LLMs_for_dic/01_test_models.py                  # 测试所有模型
    python LLMs_for_dic/01_test_models.py --judge-only     # 仅测试判别模型
    python LLMs_for_dic/01_test_models.py --generate-only  # 仅测试生成模型
    python LLMs_for_dic/01_test_models.py --workers 20     # 指定并发数

【D6 裁定, 2026-07-14】本脚本刻意绕过 LLMCache 与目录级 `LLMS_DIC_OFFLINE` 守卫，
直连各模型 API 做手动可用性诊断（非确定性、非 $0、不落入生产缓存）——仅供开发者
手动在线排查模型接口时执行，不进入任何自动化/CI 路径。文件名以数字前缀 `01_`
而非 `test_` 开头, 不匹配 `pyproject.toml::[tool.pytest.ini_options] python_files
= ["test_*.py"]`, 不会被 pytest 收集; 顶层逻辑已封装于 `main()` 并由文末
`if __name__ == "__main__":` 守卫 (未改动, 本次仅补充本段声明注释), 双重防线与
同目录 `diag_claude.py` (D6 同批改名+加固) 保持一致处置口径。
"""

# === 标准库 ===
import argparse
import concurrent.futures
import re
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# === 第三方库 ===
from openai import OpenAI

# === 本地配置 ===
from config import (
    API_KEY,
    JUDGE_MODELS,
    LOG_DIR,
    MODELS,
    REQUEST_TIMEOUT,
    get_client_config,
    get_model_params,
)

TEST_PROMPT = '请用JSON格式返回3个银行相关关键词。格式：{"keywords": ["词1", "词2", "词3"]}'


def test_single_model(args: Tuple[str, Dict[str, str]]) -> Tuple[str, str, str, float]:
    """
    测试单个模型是否可正常调用。

    Args:
        args: (model_name, client_config) 元组

    Returns:
        (模型名, 状态, 详情, 耗时秒数)
    """
    model_name, client_config = args
    client = OpenAI(**client_config)
    start = time.time()

    try:
        model_params = get_model_params(model_name)
        resp = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": TEST_PROMPT}],
            timeout=min(REQUEST_TIMEOUT, 120),
            **model_params,
        )
        text = resp.choices[0].message.content
        elapsed = time.time() - start

        # 清理 <think> 标签和 markdown 代码块
        cleaned = text or ""
        cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL)
        cleaned = re.sub(r"<think>.*", "", cleaned, flags=re.DOTALL)
        # 清理孤立的 </think> 或 </think（未闭合）及其后续内容
        cleaned = re.sub(r"</think.*", "", cleaned, flags=re.DOTALL)
        cleaned = re.sub(r"```(?:json)?\s*\n?", "", cleaned)
        cleaned = cleaned.strip()

        # 验证返回是否为有效 JSON（含正则回退）
        data = None
        try:
            data = json.loads(cleaned)
        except (json.JSONDecodeError, TypeError, ValueError):
            # 回退：用正则提取 {...} 部分
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                except (json.JSONDecodeError, ValueError):
                    pass

        has_keywords = (
            isinstance(data, dict)
            and any(isinstance(v, list) for v in data.values())
        )

        if has_keywords:
            # 展平嵌套列表并只保留字符串元素
            result_list = next((v for v in data.values() if isinstance(v, list)), [])
            kw_list = []
            for item in result_list:
                if isinstance(item, str):
                    kw_list.append(item)
                elif isinstance(item, list):
                    kw_list.extend(i for i in item if isinstance(i, str))
            status = "✅ 成功"
            detail = f"耗时 {elapsed:.1f}s, 返回 {len(kw_list)} 个词: {kw_list[:3]}"
        else:
            status = "⚠️ 响应异常"
            detail = f"耗时 {elapsed:.1f}s, 原始响应: {text[:100]}"

        return (model_name, status, detail, elapsed)

    except Exception as e:
        elapsed = time.time() - start
        err_msg = str(e)[:120]
        return (model_name, "❌ 失败", f"耗时 {elapsed:.1f}s, 错误: {err_msg}", elapsed)


def run_tests(
    models: List[str], label: str, max_workers: int = 30
) -> List[Tuple[str, str, str, float]]:
    """并发测试一组模型。"""
    print(f"\n{'=' * 70}")
    print(f"  {label} — 共 {len(models)} 个模型 (并发数: {max_workers})")
    print(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 70}\n")

    tasks = [(m, get_client_config(m)) for m in models]
    results: List[Tuple[str, str, str, float]] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(test_single_model, t): t[0] for t in tasks}
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            model_name, status, detail, elapsed = future.result()
            results.append((model_name, status, detail, elapsed))
            print(f"  [{i:>3}/{len(models)}] {status}  {model_name:<45s}  {detail}")

    return results


def print_summary(
    results: List[Tuple[str, str, str, float]], label: str
) -> List[Tuple[str, str, str, float]]:
    """打印测试汇总。"""
    success = sum(1 for _, s, _, _ in results if "成功" in s)
    warning = sum(1 for _, s, _, _ in results if "异常" in s)
    failed = sum(1 for _, s, _, _ in results if "失败" in s)
    avg_time = sum(e for _, _, _, e in results) / len(results) if results else 0

    print(f"\n{'=' * 70}")
    print(f"  {label} 测试汇总")
    print(f"{'=' * 70}")
    print(f"  ✅ 成功: {success}/{len(results)}")
    if warning:
        print(f"  ⚠️ 响应异常: {warning}/{len(results)}")
    if failed:
        print(f"  ❌ 失败: {failed}/{len(results)}")
    print(f"  ⏱️ 平均耗时: {avg_time:.1f}s")

    if failed or warning:
        print(f"\n  --- 异常/失败模型详情 ---")
        for name, status, detail, _ in results:
            if "失败" in status or "异常" in status:
                print(f"  {status}  {name}")
                print(f"         {detail}")
    print(f"{'=' * 70}\n")

    return results


def save_report(
    all_results: List[Tuple[str, str, str, float]], filepath: Path
) -> None:
    """保存测试报告到文件。"""
    lines = [
        "模型可用性测试报告",
        f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70,
        "",
    ]
    success = sum(1 for _, s, _, _ in all_results if "成功" in s)
    lines.append(
        f"总计: {len(all_results)} 个模型, 成功: {success}, 失败: {len(all_results) - success}"
    )
    lines.append("")
    lines.append(f"{'模型名称':<45s} {'状态':<10s} {'详情'}")
    lines.append(f"{'-' * 45} {'-' * 10} {'-' * 50}")
    for name, status, detail, _ in sorted(all_results, key=lambda x: x[1], reverse=True):
        lines.append(f"{name:<45s} {status:<10s} {detail}")

    filepath.write_text("\n".join(lines), encoding="utf-8")
    print(f"📄 测试报告已保存至: {filepath}")


def main() -> None:
    """主入口。"""
    parser = argparse.ArgumentParser(description="测试所有大模型API可用性")
    parser.add_argument("--judge-only", action="store_true", help="仅测试判别模型")
    parser.add_argument("--generate-only", action="store_true", help="仅测试生成模型")
    parser.add_argument("--workers", type=int, default=30, help="并发数 (默认30)")
    args = parser.parse_args()

    if not API_KEY:
        print("❌ API_KEY 未配置。请设置环境变量 YUNWU_API_KEY")
        return

    all_results: List[Tuple[str, str, str, float]] = []

    if args.judge_only:
        results = run_tests(JUDGE_MODELS, "判别模型 (JUDGE_MODELS)", args.workers)
        all_results.extend(results)
        print_summary(results, "判别模型")
    elif args.generate_only:
        results = run_tests(MODELS, "生成模型 (MODELS)", args.workers)
        all_results.extend(results)
        print_summary(results, "生成模型")
    else:
        results1 = run_tests(MODELS, "生成模型 (MODELS)", args.workers)
        all_results.extend(results1)
        print_summary(results1, "生成模型")

        results2 = run_tests(JUDGE_MODELS, "判别模型 (JUDGE_MODELS)", args.workers)
        all_results.extend(results2)
        print_summary(results2, "判别模型")

    # 保存报告
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    report_file = LOG_DIR / f"test_models_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    save_report(all_results, report_file)


if __name__ == "__main__":
    main()
