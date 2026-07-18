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
from pathlib import Path
from typing import DefaultDict, Dict, List, Optional, Set

# === 本地配置 ===
# fix(S12, 2026-07-14): 补 DOMAINS 导入，替换本文件内硬编码的 "26"（历史领域
# 数量），改为动态 len(DOMAINS)，避免领域列表精简/扩容后报告口径与实际漂移。
from config import LOG_DIR, DOMAINS
# 学术化日志支撑（四位有效数字 + 经核验 APA 参考文献；详见 academic.py）
from academic import sig4, pct4, cite, references_block

# 00_LLMs_for_dic.py 的运行日志固定名 = 其脚本名（同 py 文件名，覆盖写只留最近一次）。
# 本文件无法以数字前缀名 import 该脚本，故此处以字面量硬编码，须与其文件名保持一致。
MAIN_RUN_LOG_NAME = "00_LLMs_for_dic.log"

# 本分析报告引用文献 handle（生成采样 / 集合规约 / LLM-as-Judge / 金融文本量化根基）
# 注：κ 一致性文献 (Fleiss/Landis/McHugh) 归 calculate_kappa.py 各自引用；本报告不做
# κ 分析，故不列入，以使尾部「参考文献」表严格等于正文 in-text 实引集。
_CITED_02 = [
    "gentzkow_2019", "loughran_2011", "kearney_2014", "gomber_2018",
    "brown_2020", "dekok_2025",
    "hanley_2019", "li_2021",
    "zheng_2023", "liu_2023", "ouyang_2022", "gopal_2025", "wei_2022",
]


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
        # fix(S12, 2026-07-14): 原正则要求 "]" 后紧跟 " 失败"，漏计
        # 00_LLMs_for_dic.py:449 的 "达到最大重试次数，任务失败"（"]" 与
        # "失败" 之间夹了 "达到最大重试次数，任务" 字样）一类失败信息，
        # 导致该类失败未计入 total_gen_fail → 放宽为 "].*失败"，两种措辞
        # （紧邻式 "] 失败" 与夹字式 "] 达到最大重试次数，任务失败"）均可捕获。
        m_fail = re.search(
            r"\[ERROR\].*\[任务 (.+?)/(.+?) \((\d+)\)\].*失败", line
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
    p("大模型调用全面分析报告 (LLM Swarm Call Analytics)")
    p("=" * 100)
    p("【项目】基于大语言模型群体智能的金融科技领域词典构建管道运行分析：三阶段——种子引导")
    p(f"  并发生成 {cite('brown_2020', 'dekok_2025')} → 集合规约 {cite('hanley_2019', 'li_2021')}")
    p(f"  → 机器交叉盲审（LLM-as-a-Judge Swarm，2/3 严格多数，凝缩型 CoT 约束）{cite('zheng_2023', 'liu_2023', 'ouyang_2022', 'gopal_2025', 'wei_2022')}；")
    p(f"  测度构念承接金融文本量化与专属词典传统 {cite('gentzkow_2019', 'loughran_2011', 'kearney_2014', 'gomber_2018')}。")
    p("  说明：本报告全部非整数统计量均保留四位有效数字（4 significant figures）。")
    p("-" * 100)
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
        p(f"  成功率:     {pct4(total_gen_success, total_gen_tasks)}")
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
            # fix(S12, 2026-07-14): 硬编码 /26 → len(DOMAINS) 动态（领域列表现已精简为 1 个）
            # 四位有效数字（sig4）: 平均词数右对齐 7 位
            f"{sig4(avg_kw):>7s} {len(stats['domains']):>5}/{len(DOMAINS)}"
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
            p(f"  {model}: 失败 {stats['fail']} 次, 成功 {stats['success']} 次, 成功率 {pct4(stats['success'], total)}")
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

    # 5. 大模型关键词产出排名
    p()
    p("=" * 80)
    p("五、大模型关键词产出排名 (平均每领域)")
    p("=" * 80)
    kw_ranked = sorted(
        [(m, s) for m, s in gen_models.items() if s["success"] > 0],
        key=lambda x: x[1]["keywords_total"] / x[1]["success"],
        reverse=True,
    )
    for i, (model, stats) in enumerate(kw_ranked):
        avg = stats["keywords_total"] / stats["success"]
        p(f"  {i + 1:>2}. {model:<50} 平均 {sig4(avg):>6s} 词/领域, 总计 {stats['keywords_total']:>5} 词")

    # fix(S12, 2026-07-14): 本节 4 处硬编码 "26"（与 :201/:208 同族缺陷）
    # 一并改 len(DOMAINS) 动态，避免领域列表精简/扩容后报告口径漂移。
    n_domains = len(DOMAINS)
    # 6. 未完全覆盖全部领域的模型
    incomplete = [(m, s) for m, s in gen_models.items() if len(s["domains"]) < n_domains]
    if incomplete:
        p()
        p("=" * 80)
        p(f"六、未完全覆盖全部{n_domains}个领域的模型 (共 {len(incomplete)} 个)")
        p("=" * 80)
        for model, stats in sorted(incomplete, key=lambda x: len(x[1]["domains"])):
            p(
                f"  {model}: 覆盖 {len(stats['domains'])}/{n_domains} 领域, "
                f"成功 {stats['success']}, 失败 {stats['fail']}"
            )
    else:
        p()
        p(f"六、所有模型均完全覆盖全部{n_domains}个领域 ✅")

    # 7. 判别阶段统计
    if judge_models:
        p()
        p("=" * 80)
        p("七、判别阶段统计（机器交叉盲审 LLM-as-a-Judge，零温 T=0，2/3 严格多数截断）")
        p(f"   {cite('zheng_2023', 'liu_2023', 'ouyang_2022')}")
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

    # 8. 错误类型分析
    if error_types:
        p()
        p("=" * 80)
        p("八、错误类型分布")
        p("=" * 80)
        for err_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * min(count, 50)
            p(f"  {err_type:<12} {count:>5} 次  {bar}")

    # 9. 日志结尾状态
    p()
    p("=" * 80)
    p("九、运行结束状态 (日志最后20行)")
    p("=" * 80)
    last_lines = [l.strip() for l in lines[-20:] if l.strip()]
    for l in last_lines:
        p(f"  {l}")

    # 十、参考文献（APA；经 crossref/doi.org 核验，逐字誊抄自手稿书目，严禁自造）
    p()
    p("=" * 80)
    for ref_line in references_block(_CITED_02, title="十、参考文献 (References, APA)"):
        p(ref_line)

    # 写入文件
    report = "\n".join(out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"报告已保存至: {output_path}")
    print(f"总行数: {len(out)}")


def _find_latest_log() -> Optional[Path]:
    """返回主运行日志（固定名，只留最近一次），不存在则返回 None。"""
    log_path = LOG_DIR / MAIN_RUN_LOG_NAME
    return log_path if log_path.exists() else None


def _list_logs() -> None:
    """列出当前日志文件（每脚本仅保留最近一次，文件名同 py 文件名）。"""
    if not LOG_DIR.exists():
        print("日志目录不存在")
        return
    logs = sorted(f for f in LOG_DIR.iterdir() if f.suffix == ".log")
    if not logs:
        print("没有找到日志文件")
        return
    print(f"\n{'=' * 60}")
    print(f"  当前日志文件 (共 {len(logs)} 个)")
    print(f"{'=' * 60}")
    for i, log in enumerate(logs):
        size_kb = log.stat().st_size / 1024
        print(f"  {i + 1:>3}. {log.name:<35} ({sig4(size_kb)} KB)")
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

        # 分析报告文件名固定为「同 py 文件名」，覆盖写入，只保留最近一次
        output_path = LOG_DIR / f"{Path(__file__).stem}.md"
        analyze_log(log_path, output_path)
