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
import random
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
# 学术化日志支撑（四位有效数字 + 经核验 APA 参考文献；详见 academic.py）
from academic import sig4, pct4, cite, references_block

# 本报告引用文献 handle（严格等于正文 in-text 实引集：异构模型矩阵抑制架构偏差
# + 基座模型综述）；此诊断报告仅引这两条，勿列入未 in-text 引用的文献。
_CITED_01 = ["zheng_2023", "zhao_2023"]

TEST_PROMPT = '请用JSON格式返回3个银行相关关键词。格式：{"keywords": ["词1", "词2", "词3"]}'

# 诊断重试上限：429 限流 / 502·503 网关 / 超时属**可恢复的瞬时错误**，单发诊断遇之即
# 报"失败"会把「其实可用、只是被并发探测瞬时限流」的模型误判为不可用（假阴性）。故对
# 瞬时错误做有界指数退避重试，退避策略镜像主管道 00_LLMs_for_dic._calculate_backoff 的
# 429 分支（上限 6 档、封顶 60s + 抖动），保持全目录一致口径。
MAX_TEST_RETRIES: int = 5


def _is_transient_error(error_str: str) -> bool:
    """判断错误是否为可重试的瞬时错误（限流 / 网关 / 超时）。"""
    s = error_str.lower()
    return (
        "429" in error_str
        or "rate limit" in s
        or "负载已饱和" in error_str
        or "502" in error_str
        or "503" in error_str
        or "timed out" in s
        or "timeout" in s
    )


def _test_backoff(retry_index: int) -> float:
    """瞬时错误退避秒数（指数 + 随机抖动；镜像主管道 429 分支）。"""
    return min(60, (2 ** min(retry_index, 6)) * 2) + random.uniform(0, 15)


def test_single_model(args: Tuple[str, Dict[str, str]]) -> Tuple[str, str, str, float]:
    """
    测试单个模型是否可正常调用（对瞬时错误做有界退避重试，避免限流假阴性）。

    Args:
        args: (model_name, client_config) 元组

    Returns:
        (模型名, 状态, 详情, 耗时秒数)
    """
    model_name, client_config = args
    client = OpenAI(**client_config)
    model_params = get_model_params(model_name)
    last_err = ""

    for attempt in range(MAX_TEST_RETRIES + 1):
        start = time.time()  # 每次尝试独立计时，"耗时"反映成功调用自身延迟（不含退避等待）
        try:
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

            retry_note = f"（重试 {attempt} 次后成功）" if attempt else ""
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
                detail = f"耗时 {sig4(elapsed)}s, 返回 {len(kw_list)} 个词: {kw_list[:3]}{retry_note}"
            else:
                status = "⚠️ 响应异常"
                detail = f"耗时 {sig4(elapsed)}s, 原始响应: {text[:100]}{retry_note}"

            return (model_name, status, detail, elapsed)

        except Exception as e:
            elapsed = time.time() - start
            last_err = str(e)
            # 瞬时错误（429 限流 / 502·503 网关 / 超时）→ 有界指数退避后重试；
            # 非瞬时错误或已用尽重试次数 → 判定失败。
            if _is_transient_error(last_err) and attempt < MAX_TEST_RETRIES:
                time.sleep(_test_backoff(attempt))
                continue
            note = f"（重试 {attempt} 次仍失败）" if attempt else ""
            return (
                model_name,
                "❌ 失败",
                f"耗时 {sig4(elapsed)}s, 错误: {last_err[:120]}{note}",
                elapsed,
            )

    # 循环内每条路径均已 return，此处仅为静态分析兜底（理论不可达）。
    return (model_name, "❌ 失败", f"错误: {last_err[:120]}", 0.0)


def run_tests(
    models: List[str], label: str, max_workers: int = 30
) -> List[Tuple[str, str, str, float]]:
    """并发测试一组模型。"""
    print(f"\n{'=' * 70}")
    print(f"  {label} — 共 {len(models)} 个模型 (并发数: {max_workers})")
    print(f"  用途：核验异构大模型 API 可用性；多厂商异构面板旨在抑制单一架构/语料的")
    print(f"        推断偏差，为词典生成与盲审提供研究基线 {cite('zheng_2023', 'zhao_2023')}")
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
    print(f"  ✅ 成功: {success}/{len(results)} (可用率 {pct4(success, len(results))})")
    if warning:
        print(f"  ⚠️ 响应异常: {warning}/{len(results)} ({pct4(warning, len(results))})")
    if failed:
        print(f"  ❌ 失败: {failed}/{len(results)} ({pct4(failed, len(results))})")
    print(f"  ⏱️ 平均耗时: {sig4(avg_time)}s")

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
    """保存测试报告到文件（学术化：用途/方法学锚定 + 四位有效数字 + APA 参考文献）。"""
    success = sum(1 for _, s, _, _ in all_results if "成功" in s)
    warning = sum(1 for _, s, _, _ in all_results if "异常" in s)
    failed = len(all_results) - success - warning
    avg_time = sum(e for _, _, _, e in all_results) / len(all_results) if all_results else 0.0
    lines = [
        "模型可用性测试报告 (Heterogeneous LLM API Availability Diagnostic)",
        f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70,
        "",
        "【用途 Purpose】核验参与词典生成 / 交叉盲审的异构大模型 API 可用性；多厂商异构",
        f"  面板旨在抑制单一架构与预训练语料带来的推断偏差 {cite('zheng_2023', 'zhao_2023')}。",
        "",
        f"总计 {len(all_results)} 个模型 | 成功 {success}（可用率 {pct4(success, len(all_results))}）"
        f" | 响应异常 {warning} | 失败 {failed} | 平均耗时 {sig4(avg_time)}s",
        "",
        f"{'模型名称':<45s} {'状态':<10s} {'详情'}",
        f"{'-' * 45} {'-' * 10} {'-' * 50}",
    ]
    for name, status, detail, _ in sorted(all_results, key=lambda x: x[1], reverse=True):
        lines.append(f"{name:<45s} {status:<10s} {detail}")
    lines.append("")
    lines.extend(references_block(_CITED_01))

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
        print("❌ API_KEY 未配置。请设置环境变量 YUNWU_FULL_KEY")
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

    # 保存报告：文件名固定为「同 py 文件名」，覆盖写入，只保留最近一次
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    report_file = LOG_DIR / f"{Path(__file__).stem}.log"
    save_report(all_results, report_file)


if __name__ == "__main__":
    main()
