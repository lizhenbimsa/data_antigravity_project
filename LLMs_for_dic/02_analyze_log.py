"""
分析 run 日志，统计每个模型的调用情况。

用法:
    python LLMs_for_dic/02_analyze_log.py                         # 分析最新日志
    python LLMs_for_dic/02_analyze_log.py path/to/run_xxx.log     # 分析指定日志
    python LLMs_for_dic/02_analyze_log.py --list                  # 列出所有日志文件
"""

# === 标准库 ===
import argparse
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import DefaultDict, Dict, List, Optional, Set

# === 本地配置 ===
from config import LOG_DIR


# ════════════════════════════════════════════════════════════════
# 错误类型分类
# ════════════════════════════════════════════════════════════════

def _classify_error(line: str) -> str:
    """根据日志内容分类错误类型。"""
    lower = line.lower()
    if "timed out" in lower or "timeout" in lower:
        return "Timeout"
    elif "429" in line or "rate limit" in lower:
        return "429 限速"
    elif "502" in line:
        return "502 网关"
    elif "503" in line:
        return "503 不可用"
    elif "500" in line:
        return "500 服务器"
    elif "connection" in lower:
        return "连接错误"
    elif "json" in lower or "parse" in lower:
        return "解析错误"
    else:
        return "其他"


def analyze_log(log_path: Path, output_path: Path) -> None:
    """
    分析运行日志，统计各模型的调用成功/失败/重试情况，生成分析报告。

    Args:
        log_path: 输入日志文件路径
        output_path: 输出报告文件路径
    """
    lines = log_path.read_text(encoding="utf-8").splitlines()

    # 统计结构
    gen_models: DefaultDict[str, Dict] = defaultdict(
        lambda: {"success": 0, "fail": 0, "retry": 0, "keywords_total": 0, "domains": set()}
    )
    judge_models: DefaultDict[str, Dict] = defaultdict(
        lambda: {"success": 0, "fail": 0, "retry": 0}
    )
    # 错误类型统计
    error_types: DefaultDict[str, int] = defaultdict(int)

    judge_phase_started = False
    gen_start_time: Optional[str] = None
    gen_end_time: Optional[str] = None
    judge_start_time: Optional[str] = None
    judge_end_time: Optional[str] = None

    for line in lines:
        line = line.strip()

        # 提取时间戳
        ts_match = re.match(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]", line)
        timestamp = ts_match.group(1) if ts_match else None

        # 检测阶段切换
        if "开始判别阶段" in line or "开始批量判别" in line:
            judge_phase_started = True
            judge_start_time = timestamp
            continue

        if "开始并行执行" in line:
            gen_start_time = timestamp
            continue

        # 错误类型分类
        if "[ERROR]" in line or "[WARNING]" in line:
            error_type = _classify_error(line)
            error_types[error_type] += 1

        # 生成阶段 - 成功
        m_success = re.search(
            r"\[任务 (.+?)/(.+?) \((\d+)\)\] 成功获取 (\d+) 个词", line
        )
        if m_success and not judge_phase_started:
            model, domain, idx, count = m_success.groups()
            gen_models[model]["success"] += 1
            gen_models[model]["keywords_total"] += int(count)
            gen_models[model]["domains"].add(domain)
            gen_end_time = timestamp
            continue

        # 生成阶段 - 失败
        m_fail = re.search(
            r"\[ERROR\].*\[任务 (.+?)/(.+?) \((\d+)\)\] 失败", line
        )
        if m_fail and not judge_phase_started:
            model, domain, idx = m_fail.groups()
            gen_models[model]["fail"] += 1
            gen_models[model]["domains"].add(domain)
            continue

        # 生成阶段 - 重试
        m_retry = re.search(
            r"\[WARNING\].*\[任务 (.+?)/(.+?) \((\d+)\)\] 重试 (\d+)", line
        )
        if m_retry and not judge_phase_started:
            model, domain, idx, retry_num = m_retry.groups()
            gen_models[model]["retry"] += 1
            continue

        # 判别阶段 - 成功
        m_judge_success = re.search(
            r"\[判别-(.+?)/批次\d+\] 成功判别", line
        )
        if judge_phase_started and m_judge_success:
            model = m_judge_success.group(1)
            judge_models[model]["success"] += 1
            judge_end_time = timestamp
            continue

        # 判别阶段 - 失败
        m_judge_fail = re.search(
            r"\[ERROR\].*\[判别-(.+?)/批次\d+\] 失败", line
        )
        if judge_phase_started and m_judge_fail:
            model = m_judge_fail.group(1)
            judge_models[model]["fail"] += 1
            continue

        # 判别阶段 - 重试
        m_judge_retry = re.search(
            r"\[WARNING\].*\[判别-(.+?)/批次\d+\] 重试 (\d+)", line
        )
        if judge_phase_started and m_judge_retry:
            model = m_judge_retry.group(1)
            judge_models[model]["retry"] += 1
            continue

    # --- 生成报告 ---
    out: List[str] = []

    def p(text: str = "") -> None:
        out.append(text)

    p("=" * 100)
    p("大模型调用全面分析报告")
    p(f"日志文件: {log_path}")
    p(f"日志总行数: {len(lines)}")
    p("=" * 100)

    # 1. 总体统计
    total_gen_success = sum(m["success"] for m in gen_models.values())
    total_gen_fail = sum(m["fail"] for m in gen_models.values())
    total_gen_retry = sum(m["retry"] for m in gen_models.values())
    total_gen_tasks = total_gen_success + total_gen_fail

    p()
    p("=" * 80)
    p("一、生成阶段总体统计")
    p("=" * 80)
    p(f"  参与模型数: {len(gen_models)}")
    p(f"  总任务数:   {total_gen_tasks}  (成功 {total_gen_success} + 失败 {total_gen_fail})")
    p(f"  重试次数:   {total_gen_retry}")
    if total_gen_tasks > 0:
        p(f"  成功率:     {total_gen_success / total_gen_tasks * 100:.2f}%")
    total_kw = sum(m["keywords_total"] for m in gen_models.values())
    p(f"  关键词总产出: {total_kw} 个")
    if gen_start_time and gen_end_time:
        p(f"  时间范围:   {gen_start_time} ~ {gen_end_time}")

    # 2. 各模型详细统计
    p()
    p("=" * 80)
    p("二、生成阶段各模型详情 (按成功数降序)")
    p("=" * 80)
    header = f"{'模型名称':<50} {'成功':>5} {'失败':>5} {'重试':>5} {'总词数':>7} {'平均词':>7} {'领域':>6}"
    p(header)
    p("-" * 90)

    sorted_models = sorted(gen_models.items(), key=lambda x: x[1]["success"], reverse=True)
    for model, stats in sorted_models:
        avg_kw = stats["keywords_total"] / stats["success"] if stats["success"] > 0 else 0
        p(
            f"{model:<50} {stats['success']:>5} {stats['fail']:>5} "
            f"{stats['retry']:>5} {stats['keywords_total']:>7} "
            f"{avg_kw:>7.1f} {len(stats['domains']):>5}/26"
        )

    # 3. 失败模型汇总
    failed_models = [(m, s) for m, s in gen_models.items() if s["fail"] > 0]
    if failed_models:
        p()
        p("=" * 80)
        p(f"三、生成阶段失败模型详情 (共 {len(failed_models)} 个模型有失败)")
        p("=" * 80)
        for model, stats in sorted(failed_models, key=lambda x: x[1]["fail"], reverse=True):
            total = stats["success"] + stats["fail"]
            rate = stats["success"] / total * 100 if total > 0 else 0
            p(f"  {model}: 失败 {stats['fail']} 次, 成功 {stats['success']} 次, 成功率 {rate:.1f}%")
    else:
        p()
        p("三、生成阶段无失败模型 ✅")

    # 4. 重试模型汇总
    retry_models = [(m, s) for m, s in gen_models.items() if s["retry"] > 0]
    if retry_models:
        p()
        p("=" * 80)
        p(f"四、生成阶段存在重试的模型 (共 {len(retry_models)} 个)")
        p("=" * 80)
        for model, stats in sorted(retry_models, key=lambda x: x[1]["retry"], reverse=True):
            p(
                f"  {model}: 重试 {stats['retry']} 次 "
                f"(最终成功 {stats['success']}, 失败 {stats['fail']})"
            )

    # 5. 关键词产出 TOP 10
    p()
    p("=" * 80)
    p("五、模型关键词产出 TOP 10 (平均每领域)")
    p("=" * 80)
    kw_ranked = sorted(
        [(m, s) for m, s in gen_models.items() if s["success"] > 0],
        key=lambda x: x[1]["keywords_total"] / x[1]["success"],
        reverse=True,
    )
    for i, (model, stats) in enumerate(kw_ranked[:10]):
        avg = stats["keywords_total"] / stats["success"]
        p(f"  {i + 1:>2}. {model:<50} 平均 {avg:>6.1f} 词/领域, 总计 {stats['keywords_total']:>5} 词")

    # 6. 关键词产出最少 10
    p()
    p("=" * 80)
    p("六、关键词产出最少 10 个模型 (平均每领域)")
    p("=" * 80)
    for i, (model, stats) in enumerate(kw_ranked[-10:]):
        avg = stats["keywords_total"] / stats["success"]
        p(f"  {i + 1:>2}. {model:<50} 平均 {avg:>6.1f} 词/领域, 总计 {stats['keywords_total']:>5} 词")

    # 7. 未完全覆盖 26 领域的模型
    incomplete = [(m, s) for m, s in gen_models.items() if len(s["domains"]) < 26]
    if incomplete:
        p()
        p("=" * 80)
        p(f"七、未完全覆盖26个领域的模型 (共 {len(incomplete)} 个)")
        p("=" * 80)
        for model, stats in sorted(incomplete, key=lambda x: len(x[1]["domains"])):
            p(
                f"  {model}: 覆盖 {len(stats['domains'])}/26 领域, "
                f"成功 {stats['success']}, 失败 {stats['fail']}"
            )
    else:
        p()
        p("七、所有模型均完全覆盖26个领域 ✅")

    # 8. 判别阶段统计
    if judge_models:
        p()
        p("=" * 80)
        p("八、判别阶段统计")
        p("=" * 80)
        total_j_success = sum(s["success"] for s in judge_models.values())
        total_j_fail = sum(s["fail"] for s in judge_models.values())
        total_j_retry = sum(s["retry"] for s in judge_models.values())
        p(f"  模型数: {len(judge_models)}")
        p(f"  总成功: {total_j_success}, 总失败: {total_j_fail}, 总重试: {total_j_retry}")
        p()
        for model, stats in sorted(
            judge_models.items(), key=lambda x: x[1]["success"], reverse=True
        ):
            p(
                f"  {model:<50} 成功 {stats['success']:>4}, "
                f"失败 {stats['fail']:>4}, 重试 {stats['retry']:>4}"
            )

    # 9. 错误类型分析（新增）
    if error_types:
        p()
        p("=" * 80)
        p("九、错误类型分布")
        p("=" * 80)
        for err_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * min(count, 50)
            p(f"  {err_type:<12} {count:>5} 次  {bar}")

    # 10. 日志结尾状态
    p()
    p("=" * 80)
    p("十、运行结束状态 (日志最后20行)")
    p("=" * 80)
    last_lines = [l.strip() for l in lines[-20:] if l.strip()]
    for l in last_lines:
        p(f"  {l}")

    # 写入文件
    report = "\n".join(out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"报告已保存至: {output_path}")
    print(f"总行数: {len(out)}")


def _find_latest_log() -> Optional[Path]:
    """查找最新的运行日志文件。"""
    if not LOG_DIR.exists():
        return None
    logs = sorted(
        (f for f in LOG_DIR.iterdir() if f.name.startswith("run_") and f.suffix == ".log"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
    return logs[0] if logs else None


def _list_logs() -> None:
    """列出所有日志文件。"""
    if not LOG_DIR.exists():
        print("日志目录不存在")
        return
    logs = sorted(
        (f for f in LOG_DIR.iterdir() if f.name.startswith("run_") and f.suffix == ".log"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
    if not logs:
        print("没有找到日志文件")
        return
    print(f"\n{'=' * 60}")
    print(f"  日志文件列表 (共 {len(logs)} 个)")
    print(f"{'=' * 60}")
    for i, log in enumerate(logs):
        size_kb = log.stat().st_size / 1024
        print(f"  {i + 1:>3}. {log.name:<35} ({size_kb:.0f} KB)")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="分析 LLMs_for_dic 运行日志")
    parser.add_argument("log_file", nargs="?", default=None, help="日志文件路径 (默认: 最新)")
    parser.add_argument("--list", action="store_true", help="列出所有日志文件")
    args = parser.parse_args()

    if args.list:
        _list_logs()
    else:
        if args.log_file:
            log_path = Path(args.log_file)
        else:
            log_path = _find_latest_log()
            if log_path is None:
                print("❌ 未找到日志文件。请指定路径或先运行主脚本。")
                raise SystemExit(1)

        if not log_path.exists():
            print(f"❌ 文件不存在: {log_path}")
            raise SystemExit(1)

        # 从日志文件名提取时间戳
        ts_match = re.search(r"(\d{8}_\d{6})", log_path.name)
        ts = ts_match.group(1) if ts_match else datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = LOG_DIR / f"analysis_{ts}.md"
        analyze_log(log_path, output_path)
