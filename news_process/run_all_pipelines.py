"""run_all_pipelines.py — 全项目「九入口」顺序真跑总编排器
=================================================================

功能:
    把本项目的九个顶层入口 (九入口) 按硬约定顺序作为**独立子进程**逐个拉起来跑,
    子进程隔离 (异常不串 / 内存进程退出即释放 / jieba·signal·线程池等全局态不冲突),
    默认 fail-fast (任一入口非零退出即中断), 末尾出耗时统计与判读。本脚本自身不亲自
    算任何数据, 只负责按序编排、注入确定性/离线环境、汇总结果。

九入口执行顺序 (= scripts/audit/NINE_ENTRYPOINT_RUN_AUDIT_*.md §1 运行矩阵 ①→⑨,
用户 2026-07-23 指定顺序与之逐一对应):

    ① LLMs_for_FinTech_dic/00_LLMs_for_dic.py   金融科技词典生成 + 盲审 (独立 LLM 管道)
    ② run_pipeline_function.py                   主流水线 (00→51, 16 阶段)
    ③ run_pipeline_validation.py                 评估验证模块 (60→75, 16 阶段)
    ④ run_paper.py                               多论文调度 (--list + 白名单逐篇 --stage all)
    ⑤ 80_placebo_and_alt_anchor.py               安慰剂 + 替代锚点稳健性 (audit-only)
    ⑥ 81_stata_data_audit.py                     Stata 导出数据审计
    ⑦ 82_export_stats_excel.py                   描述性统计 Excel 导出
    ⑧ company_listed_bank/run_pipeline.py        上市公司×银行 共现面板四步链 (01→04)
    ⑨ company_tax_bank/run_pipeline.py           税调企业×银行 共现面板四步链 (01→04)

工作目录约定:
    全部九入口都设计为**从 news_process/ 目录**运行 (= 本脚本所在目录)。①的本地
    import (config/llm_cache/academic) 靠 Python 运行脚本时自动把脚本所在目录置于
    sys.path[0] 解析; ②③④⑤⑥⑦ 各自注入 news_process 父目录到 sys.path;
    ⑧⑨ 两 orchestrator 内部把子步 cwd 设回 news_process/。故本编排器统一用
    cwd = 本脚本所在目录 (news_process/) 拉起每个入口。

离线 / 成本安全 (默认离线, load-bearing):
    ⚠ 本项目多个阶段会调用**付费** LLM / Embedding API (stage 21 情感三家投票、词表/
    文章嵌入、run_paper --stage all 内含重跑主线、① 词典生成盲审)。CLAUDE.md 铁律:
    「完整付费 LLM 重处理须先过 M0 审批门」「付费不可逆」。故本编排器**默认离线**:
      - ②③④⑤⑥⑦ (news_process 家族) 注入 NEWS_PROCESS_LLM_OFFLINE=1 (缓存命中 $0
        逐字节复现; miss 即 fail-loud raise, 绝不静默直连付费 API);
      - ① (LLMs_for_dic 独立管道) 注入其独立开关 LLMS_DIC_OFFLINE=1 ($0 全链重放)。
    需要真联网/付费首跑或播种时须**显式** --online (并自行确保已过 M0 审批门 + 配好
    OPENLUX_API_KEY / DEEPSEEK_API_KEY / SILICONFLOW_API_KEY)。

确定性:
    对齐 core/stage.py 的子进程环境注入 — 强制 PYTHONHASHSEED=0 (消除 jieba+frozenset
    边界 token 非确定性 / 锁 golden), setdefault 编码/缓冲/OMP 契约; **不**默认钉死 BLAS
    线程 (对齐 core/stage.py F13: HASHSEED 零性能代价, BLAS=1 对嵌入/网络重数值阶段有真实
    性能代价) — golden 逐位复现的 BLAS 钉死是 shell 约定 / M0 SOP, 需要时用 --pin-blas。

并发安全:
    ②③④ 共享同一 PipelineLock (output_dir 级), ⑧⑨ 各有独立单实例锁 —— 本编排器逐进程
    串行执行 (fail-fast, 同一时刻至多一个子进程), 天然不触发任何跨入口锁竞争。⚠ 勿在本
    编排器运行期间另起 run_pipeline_* / company_*/run_pipeline.py 实例 (会被锁 fail-loud 拒)。

G9 传导铁律 (来自九入口审计教训, 供人工判读):
    凡影响 40 面板的整改, 传导必须走**全链 ②** 而非单跑 stage 40 —— 单跑时 75 号比 21 号新
    会把面板推进「激活代」触发 codebook/labels 测试红; 全链 ② 内部重跑 21 刷新代际即回稳。
    本编排器按序跑 ②→③→④ 天然满足该传导 (④ --stage all 末次重跑主线为终代)。

用法 (从 news_process/ 目录, conda base python; 见 CLAUDE.md「本项目 Python=conda base 3.13」):
    python run_all_pipelines.py                 # 默认: 离线, 九入口全链 ①→⑨ 顺序真跑
    python run_all_pipelines.py --dry-run        # 只打印将执行的全部命令 + 环境, 不实跑
    python run_all_pipelines.py --only 2,3,8      # 只跑第 2/3/8 个入口 (序号 1..9)
    python run_all_pipelines.py --start-at 5      # 从第 5 个入口起 (断点续跑)
    python run_all_pipelines.py --stop-after 4    # 跑到第 4 个入口为止
    python run_all_pipelines.py --papers tone,attention   # ④ 只跑指定论文 (逗号分隔简名/全名)
    python run_all_pipelines.py --paper-stage tables      # ④ 转发给 run_paper 的 --stage (默认 all)
    python run_all_pipelines.py --skip-21-if-exists       # 转发给 ② (LLM 阶段已跑完时跳过)
    python run_all_pipelines.py --online         # ⚠ 关闭离线守卫 (付费; 须先过 M0 审批门)
    python run_all_pipelines.py --keep-going      # 不 fail-fast, 跑完所有入口后再汇总红/绿

方法论依据 (逐字取自本仓已核验引文, 0 臆造 DOI):
    Sandve et al. (2013) PLoS CB e1003285 (可复现计算十规则); Wilson et al. (2017) PLOS CB
    e1005510 (科研软件良好实践: DAG/隔离/日志溯源); Stodden et al. (2018) PNAS 115(11)
    2584-2589 (期刊复现政策实证); Wilkinson et al. (2016) Sci Data 3, 160018 (FAIR 原则)。

设计约束:
    - 独立顶层编排器, **不注册** core/dag.py::STAGES_MAIN/VALIDATION, **不是** NN_*.py thin shim
      (不影响计数不变量 STAGES_MAIN=16 / thin shim=35 / OUTPUT_REGISTRY=16), 定位镜像
      run_pipeline_function.py / company_*/run_pipeline.py。
    - 纯子进程编排 + 环境注入 + 汇总日志; 零业务逻辑。
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

# ── 路径锚点 ────────────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent          # news_process/
REPO_PARENT = HERE.parent                        # data_antigravity_project/ (news_process 的父目录)
LOG_DIR = HERE / "logs"                           # 扁平日志目录 (与主管道各阶段同址)
PY = sys.executable                               # 当前解释器 (conda base python)
STAGE_NAME = "run_all_pipelines"

# 圆圈序号 ①..⑨ (仅日志展示用途)
_CIRCLED = "①②③④⑤⑥⑦⑧⑨"


# ── 日志基建 (优先复用 core/logging.setup_logging, 保持与主管道一致的落盘格式) ──
# 先把 news_process 父目录置于 sys.path, 使 ``import news_process`` 可解析 (镜像
# run_pipeline_function.py 的 sys.path 注入)。
if str(REPO_PARENT) not in sys.path:
    sys.path.insert(0, str(REPO_PARENT))

try:
    from news_process.core.logging import (  # type: ignore
        log_memory_usage,
        setup_logging,
        sig4,
    )
    _HAVE_CORE_LOGGING = True
except Exception:  # noqa: BLE001 — 包不可用时降级为 stdlib 日志, 编排器仍可跑
    import logging as _logging

    _HAVE_CORE_LOGGING = False

    def sig4(value, sig: int = 4) -> str:  # type: ignore
        """4 位有效数字格式化的极简回退 (core/logging.sig4 不可用时)。"""
        try:
            return f"{float(value):.{sig}g}"
        except (TypeError, ValueError):
            return str(value)

    def log_memory_usage(logger, tag: str = "") -> None:  # type: ignore
        """RSS 内存读数回退; psutil 缺席则静默跳过 (纯日志, 不影响控制流)。"""
        try:
            import psutil

            rss = psutil.Process().memory_info().rss / 1048576.0
            logger.info("  💾 内存 (%s): RSS %.4g MB", tag, rss)
        except Exception:  # noqa: BLE001
            pass

    def setup_logging(stage_name, log_dir, file_mode="w"):  # type: ignore
        """stdlib 回退: 文件 + console 双通道, 覆盖式写入。"""
        os.makedirs(log_dir, exist_ok=True)
        logger = _logging.getLogger(stage_name)
        if logger.hasHandlers():
            logger.handlers.clear()
        logger.setLevel(_logging.INFO)
        fmt = _logging.Formatter(
            "%(asctime)s - %(name)s - PID:%(process)d - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        fh = _logging.FileHandler(
            os.path.join(log_dir, f"{stage_name}.log"),
            mode=("w" if file_mode == "w" else "a"),
            encoding="utf-8",
        )
        fh.setFormatter(fmt)
        logger.addHandler(fh)
        ch = _logging.StreamHandler(sys.stdout)
        ch.setFormatter(fmt)
        logger.addHandler(ch)
        logger.propagate = False
        return logger


logger = setup_logging(STAGE_NAME, str(LOG_DIR))


# ── 论文白名单 (④ run_paper 逐篇) 的回退清单 (子进程探测失败时用) ──────────────
# 权威 SSOT = papers._common.paper_config._VALID_PAPER_IDS (= paper_registry.PAPER_IDS_ALL);
# 运行期优先经子进程动态探测, 探测失败才回退到本硬编码 11 篇 (与探测同排序: 字母序)。
_PAPER_IDS_FALLBACK = sorted([
    "bank_fintech_tone",
    "bank_fintech_attention",
    "bank_fintech_substance",
    "bank_fintech_locus",
    "bank_fintech_collab",
    "benefit_society",
    "brokerage_network",
    "llm_peer",
    "strategic_diff",
    "bank_media_disagreement",
    "bank_news_clarity",
])

# 论文简名 → 全名别名 (供 --papers 传简名, 对齐 run_paper.py docstring 的简名口径)
_PAPER_ALIASES = {
    "tone": "bank_fintech_tone",
    "attention": "bank_fintech_attention",
    "substance": "bank_fintech_substance",
    "locus": "bank_fintech_locus",
    "collab": "bank_fintech_collab",
    "disagreement": "bank_media_disagreement",
    "clarity": "bank_news_clarity",
}


def _resolve_paper_ids() -> tuple[list[str], str]:
    """动态解析 run_paper 白名单 (防硬编码漂移)。

    经一次隔离子进程 import ``_VALID_PAPER_IDS`` 并按字母序打印; 任何失败 (包不可用/
    import 报错/空输出) 回退到 ``_PAPER_IDS_FALLBACK`` 并在返回值第二项标注来源。
    子进程 cwd 设为 news_process 父目录, 使 ``import news_process`` 解析。
    """
    probe = (
        "from news_process.papers._common.paper_config import _VALID_PAPER_IDS;"
        "print('\\n'.join(sorted(_VALID_PAPER_IDS)))"
    )
    try:
        out = subprocess.run(
            [PY, "-c", probe],
            cwd=str(REPO_PARENT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        ids = [ln.strip() for ln in out.stdout.splitlines() if ln.strip()]
        if out.returncode == 0 and ids:
            return sorted(ids), "SSOT (paper_config._VALID_PAPER_IDS)"
        logger.warning(
            "论文白名单探测子进程非零退出/空输出 (rc=%s); 回退硬编码 11 篇。stderr 首行: %s",
            out.returncode, (out.stderr.splitlines() or ["<空>"])[0],
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("论文白名单探测失败 (%s); 回退硬编码 11 篇。", e)
    return list(_PAPER_IDS_FALLBACK), "回退硬编码清单 (探测失败)"


# ── 子进程环境构造 ────────────────────────────────────────────────────────────
def build_child_env(offline: bool, pin_blas: bool) -> dict:
    """构造九入口子进程的环境变量 (对齐 core/stage.py 注入约定 + 离线/BLAS 策略)。

    - 确定性: 强制 PYTHONHASHSEED=0 (非 setdefault — 防父 shell 非零 seed 击穿);
      setdefault 编码/缓冲/OMP 契约 (尊重外部覆盖)。
    - 离线 (默认): NEWS_PROCESS_LLM_OFFLINE=1 (②–⑦) + LLMS_DIC_OFFLINE=1 (①) + setdefault
      HF/TRANSFORMERS_OFFLINE=1 (stage 23 BERT 重跑离线, 见 memory)。
    - 联网 (--online): **移除**继承来的两个离线守卫 (防 shell 里残留的 OFFLINE=1 静默强制
      离线), 并 best-effort setdefault SSL_CERT_FILE=certifi (裸环境嵌入 SSL 修复, 见 memory)。
    - BLAS: 仅 --pin-blas 时钉死 MKL/OPENBLAS/NUMEXPR/OMP_NUM_THREADS=1 (golden 逐位复现)。
    """
    env = os.environ.copy()

    # 确定性 + 编码 (对齐 core/stage.py:239-255)
    env.setdefault("PYTHONUNBUFFERED", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8:replace")
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
    env["PYTHONHASHSEED"] = "0"  # 强制 (非 setdefault)

    if pin_blas:
        for _k in ("MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                   "NUMEXPR_NUM_THREADS", "OMP_NUM_THREADS"):
            env[_k] = "1"

    if offline:
        env["NEWS_PROCESS_LLM_OFFLINE"] = "1"   # ②–⑦: 缓存命中 $0, miss fail-loud
        env["LLMS_DIC_OFFLINE"] = "1"           # ①: 独立离线开关 ($0 全链重放)
        env.setdefault("HF_HUB_OFFLINE", "1")
        env.setdefault("TRANSFORMERS_OFFLINE", "1")
    else:
        # 显式联网: 清掉可能从 shell 继承的离线守卫, 否则子进程仍会静默离线
        env.pop("NEWS_PROCESS_LLM_OFFLINE", None)
        env.pop("LLMS_DIC_OFFLINE", None)
        try:
            import certifi

            env.setdefault("SSL_CERT_FILE", certifi.where())
        except Exception:  # noqa: BLE001 — 无 certifi 时不阻断, 仅少一层 SSL 兜底
            pass

    return env


# ── 执行计划构造 ──────────────────────────────────────────────────────────────
def build_plan(args, paper_ids: list[str]) -> list[dict]:
    """构造九入口执行计划: 每个入口 = {num, mark, title, cmds:[(sublabel, argv), ...]}。

    多数入口只含 1 条命令; ④ run_paper 展开为「--list + 逐篇 --stage <paper_stage>」多条。
    argv 均用绝对路径 + ``-u`` (无缓冲, 对齐 company orchestrator)。cwd 由调用方统一设为 HERE。
    """
    main_extra: list[str] = []
    if args.skip_21_if_exists:
        main_extra.append("--skip-21-if-exists")
    if args.skip_unchanged:
        main_extra.append("--skip-unchanged")

    def _run_paper_cmds() -> list[tuple[str, list[str]]]:
        rp = str(HERE / "run_paper.py")
        cmds: list[tuple[str, list[str]]] = [("run_paper --list", [PY, "-u", rp, "--list"])]
        for pid in paper_ids:
            cmds.append((f"run_paper {pid} --stage {args.paper_stage}",
                         [PY, "-u", rp, pid, "--stage", args.paper_stage]))
        return cmds

    plan: list[dict] = [
        {"num": 1, "title": "LLMs_for_FinTech_dic 词典生成 + 盲审 (独立 LLM 管道)",
         "cmds": [("00_LLMs_for_dic",
                   [PY, "-u", str(HERE / "LLMs_for_FinTech_dic" / "00_LLMs_for_dic.py")])]},
        {"num": 2, "title": "主流水线 run_pipeline_function (00→51, 16 阶段)",
         "cmds": [("run_pipeline_function",
                   [PY, "-u", str(HERE / "run_pipeline_function.py"), *main_extra])]},
        {"num": 3, "title": "评估验证 run_pipeline_validation (60→75, 16 阶段)",
         "cmds": [("run_pipeline_validation",
                   [PY, "-u", str(HERE / "run_pipeline_validation.py")])]},
        {"num": 4, "title": f"多论文 run_paper (--list + {len(paper_ids)} 篇 --stage {args.paper_stage})",
         "cmds": _run_paper_cmds()},
        {"num": 5, "title": "80_placebo_and_alt_anchor (安慰剂 + 替代锚点, audit-only)",
         "cmds": [("80_placebo_and_alt_anchor",
                   [PY, "-u", str(HERE / "80_placebo_and_alt_anchor.py")])]},
        {"num": 6, "title": "81_stata_data_audit (Stata 导出数据审计)",
         "cmds": [("81_stata_data_audit",
                   [PY, "-u", str(HERE / "81_stata_data_audit.py")])]},
        {"num": 7, "title": "82_export_stats_excel (描述性统计 Excel 导出)",
         "cmds": [("82_export_stats_excel",
                   [PY, "-u", str(HERE / "82_export_stats_excel.py")])]},
        {"num": 8, "title": "company_listed_bank 银企共现面板四步链 (01→04)",
         "cmds": [("company_listed_bank/run_pipeline",
                   [PY, "-u", str(HERE / "company_listed_bank" / "run_pipeline.py")])]},
        {"num": 9, "title": "company_tax_bank 税调银企共现面板四步链 (01→04)",
         "cmds": [("company_tax_bank/run_pipeline",
                   [PY, "-u", str(HERE / "company_tax_bank" / "run_pipeline.py")])]},
    ]
    for step in plan:
        step["mark"] = _CIRCLED[step["num"] - 1]
    return plan


# ── 单条命令执行 (stdout/stderr 继承实时终端; Ctrl+C 传子进程各自优雅停机) ──────────
def run_one(sublabel: str, cmd: list[str], env: dict) -> tuple[int, float]:
    """拉起单条子进程命令, 返回 (退出码, 墙钟秒)。

    stdout/stderr 直接继承 (实时透传到终端); 每个入口自身另写独立 <stem>.log 作为
    完整取证记录 (本编排器日志只记编排事件 + 汇总)。

    Ctrl+C 语义 (对齐同级 company_*/run_pipeline.py 范式, **刻意不拦截**): 控制台 Ctrl+C
    与本编排器、当前子进程同处一个控制台进程组 → 信号同时投递两者; 各入口有各自的优雅
    停机 (① SIGINT handler / ②③④ PipelineLock finally 释放 / ⑧⑨ 单实例锁 finally 释放),
    由**子进程自己**干净收尾。本函数刻意不做裸 proc.terminate() 越俎硬杀 —— 那会抢占/
    截断子编排器自身的进程树清理 (core/stage.py::_terminate_process_tree 有 grace 期) 而
    留下孤儿孙进程。KeyboardInterrupt 经 proc.wait() 在父进程上抛, 透传出 main() 由解释器
    顶层以非零码退出 (下方 ``except Exception`` 只兜启动失败, 不捕获 KeyboardInterrupt)。
    """
    logger.info("  $ %s", " ".join(cmd))
    t0 = time.time()
    try:
        proc = subprocess.Popen(cmd, cwd=str(HERE), env=env)
    except Exception as e:  # noqa: BLE001 — 启动失败即该步失败 (KeyboardInterrupt 属 BaseException, 不被捕获)
        logger.error("  ✗ 子进程启动失败 [%s]: %s", sublabel, e)
        return 1, time.time() - t0
    rc = proc.wait()  # Ctrl+C → KeyboardInterrupt 在此上抛并透传 (子进程同组已收到信号, 自行优雅停机)
    return rc, time.time() - t0


# ── 运行头 banner / 参考文献 (纯日志) ─────────────────────────────────────────
def _log_banner(plan: list[dict], args, paper_ids: list[str], paper_src: str) -> None:
    import platform

    bar = "=" * 78
    logger.info(bar)
    logger.info("全项目九入口顺序真跑总编排器 (news_process ALL-PIPELINES ORCHESTRATOR)")
    logger.info(bar)
    logger.info("【功能】把项目九个顶层入口按 ①→⑨ 硬顺序作为独立子进程逐个拉起来跑, 子进程隔离 +")
    logger.info("        %s + 阶段前后各入口自管产物与日志; 本编排器只编排, 不亲自算数据。",
                "fail-fast" if not args.keep_going else "keep-going (不 fail-fast)")
    logger.info("【顺序】= scripts/audit/NINE_ENTRYPOINT_RUN_AUDIT_*.md §1 运行矩阵 ①→⑨")
    logger.info("【离线】%s", (
        "默认离线 — ②–⑦ 注入 NEWS_PROCESS_LLM_OFFLINE=1 / ① 注入 LLMS_DIC_OFFLINE=1 "
        "(缓存命中 $0 逐字节复现; miss fail-loud, 绝不静默付费)"
        if args.offline else
        "⚠ 联网模式 (--online) — 已移除离线守卫, 将按需调用**付费** API; "
        "请确认已过 M0 审批门并配好 *_API_KEY"))
    logger.info("【确定性】强制 PYTHONHASHSEED=0 + %s BLAS 钉死 (%s)",
                "启用" if args.pin_blas else "不",
                "--pin-blas" if args.pin_blas else "对齐 core/stage.py F13, --pin-blas 可开")
    logger.info("【判读】末尾统计表逐入口列墙钟秒+占比: ✓=成功 / ✗=失败 / ⏭=未选 / ⛔=未跑到(fail-fast 中断); 全绿=九入口全链闭合。")
    logger.info("-" * 78)
    logger.info("  🧭 环境: Python %s @ %s", sys.version.split()[0], PY)
    logger.info("  🧭 平台: %s | CPU 逻辑核=%s | PID=%s",
                platform.platform(), os.cpu_count(), os.getpid())
    logger.info("  📂 工作目录 (各入口 cwd): %s", HERE)
    logger.info("  📂 日志目录: %s (本编排器 → %s.log; 各入口另写各自 <stem>.log)",
                LOG_DIR, STAGE_NAME)
    logger.info("  📄 论文白名单来源: %s (%d 篇): %s",
                paper_src, len(paper_ids), ", ".join(paper_ids))
    logger.info("-" * 78)
    logger.info("  待执行入口 (共 %d 个被选中):", sum(1 for s in plan if s.get("_selected")))
    for step in plan:
        tag = "待执行" if step.get("_selected") else "未选 (--only/--start-at/--stop-after 过滤)"
        n_cmd = len(step["cmds"])
        logger.info("    %s %s  [%s%s]", step["mark"], step["title"], tag,
                    f", {n_cmd} 条子命令" if n_cmd > 1 else "")
    logger.info(bar)


def _log_references() -> None:
    logger.info("-" * 78)
    logger.info("📖 方法论依据 (APA, 逐字取自本仓已核验引文池; 0 臆造 DOI)")
    logger.info("  1. Sandve, G. K., Nekrutenko, A., Taylor, J., & Hovig, E. (2013). Ten simple rules for")
    logger.info("     reproducible computational research. PLoS Computational Biology, 9(10), e1003285.")
    logger.info("     https://doi.org/10.1371/journal.pcbi.1003285")
    logger.info("     → 本编排器落实: 固定执行序、向子进程注入 PYTHONHASHSEED=0、逐条记录实际命令行。")
    logger.info("  2. Wilson, G., Bryan, J., Cranston, K., Kitzes, J., Nederbragt, L., & Teal, T. K. (2017).")
    logger.info("     Good enough practices in scientific computing. PLOS Computational Biology, 13(6),")
    logger.info("     e1005510. https://doi.org/10.1371/journal.pcbi.1005510")
    logger.info("     → DAG/子进程隔离/日志溯源 = 科研软件良好实践在编排层的落地。")
    logger.info("  3. Stodden, V., Seiler, J., & Ma, Z. (2018). An empirical analysis of journal policy")
    logger.info("     effectiveness for computational reproducibility. PNAS, 115(11), 2584-2589.")
    logger.info("     https://doi.org/10.1073/pnas.1708290115")
    logger.info("  4. Wilkinson, M. D., Dumontier, M., Aalbersberg, I. J., et al. (2016). The FAIR Guiding")
    logger.info("     Principles for scientific data management and stewardship. Scientific Data, 3, 160018.")
    logger.info("     https://doi.org/10.1038/sdata.2016.18")


# ── CLI ───────────────────────────────────────────────────────────────────────
def _parse_step_ids(spec: str) -> set[int]:
    """解析 --only 的入口序号集合 (接受 '2,3,8' 或 '2-4' 混合; 序号 1..9)。

    非数字 / 空端点 token (如 'abc' / '1-' / '-3') 一律 raise SystemExit 给干净用法
    报错, 与越界分支及 --start-at/--stop-after/--papers 的报错契约一致 (不抛裸 ValueError
    traceback)。
    """
    def _to_int(tok: str) -> int:
        if not tok.isdigit():
            raise SystemExit(f"[--only] 非法序号片段 {tok!r} (须为 1..9 或 a-b 区间, 如 '2,3,8' / '5-9')")
        return int(tok)

    out: set[int] = set()
    for tok in spec.replace(" ", "").split(","):
        if not tok:
            continue
        if "-" in tok:
            a, b = tok.split("-", 1)
            lo, hi = _to_int(a), _to_int(b)
            if lo > hi:
                raise SystemExit(f"[--only] 逆序区间 {tok!r} (须 a≤b, 如 '5-9')")
            out.update(range(lo, hi + 1))
        else:
            out.add(_to_int(tok))
    bad = {n for n in out if n < 1 or n > 9}
    if bad:
        raise SystemExit(f"[--only] 非法入口序号 {sorted(bad)} (合法 1..9)")
    return out


def _resolve_papers_arg(spec: str, whitelist: list[str]) -> list[str]:
    """解析 --papers: 'all' → 全白名单; 'none' → 空 (跳过逐篇, 只留 --list); 否则逗号分隔简名/全名。"""
    s = spec.strip().lower()
    if s == "all":
        return list(whitelist)
    if s == "none":
        return []
    wl = set(whitelist)
    out: list[str] = []
    for tok in spec.split(","):
        tok = tok.strip()
        if not tok:
            continue
        # 简名走别名表, 全名回退到小写 token: 两条路径都对大小写不敏感 (白名单 ID 恒小写
        # snake_case, 归一化无歧义), 兑现 docstring「简名/全名等价」承诺。
        pid = _PAPER_ALIASES.get(tok.lower(), tok.lower())
        if pid not in wl:
            raise SystemExit(
                f"[--papers] 未知论文 {tok!r} → {pid!r} (不在白名单)。可选: {sorted(wl)}"
            )
        if pid not in out:
            out.append(pid)
    return out


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="run_all_pipelines",
        description="全项目九入口顺序真跑总编排器 (①→⑨, 子进程隔离, 默认离线 fail-fast)。",
    )
    p.add_argument("--dry-run", action="store_true",
                   help="只打印将执行的全部命令 + 环境策略, 不获任何锁、不实跑。")
    p.add_argument("--online", dest="offline", action="store_false", default=True,
                   help="⚠ 关闭离线守卫, 允许调用付费 API (默认离线; 联网前须过 M0 审批门 + 配 *_API_KEY)。")
    p.add_argument("--pin-blas", action="store_true",
                   help="钉死 BLAS 线程=1 (MKL/OPENBLAS/NUMEXPR/OMP) 逐位复现; 默认不钉 (对齐 core/stage.py F13)。")
    p.add_argument("--only", metavar="IDS", default=None,
                   help="只跑指定入口序号 (1..9, 如 '2,3,8' 或 '5-9'); 与 --start-at/--stop-after 取交集。")
    p.add_argument("--start-at", type=int, default=1, metavar="N",
                   help="从第 N 个入口起 (断点续跑, 默认 1)。")
    p.add_argument("--stop-after", type=int, default=9, metavar="N",
                   help="跑到第 N 个入口为止 (默认 9)。")
    p.add_argument("--papers", default="all", metavar="SPEC",
                   help="④ run_paper 逐篇范围: all(默认) / none(仅 --list) / 逗号分隔简名或全名。")
    p.add_argument("--paper-stage", default="all",
                   choices=["pipeline", "tables", "figures", "all"],
                   help="④ 转发给 run_paper 的 --stage (默认 all; all 内含重跑主线, 耗时最长)。")
    p.add_argument("--skip-21-if-exists", action="store_true",
                   help="转发给 ② run_pipeline_function: stage 21 输出已存在则跳过 (省 LLM 阶段重放时间)。")
    p.add_argument("--skip-unchanged", action="store_true",
                   help="转发给 ② run_pipeline_function: 通用阶段级增量跳过 (输入未变的阶段跳过)。")
    p.add_argument("--keep-going", action="store_true",
                   help="不 fail-fast: 某入口失败后继续跑剩余入口, 末尾统一汇总红/绿 (默认 fail-fast)。")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.start_at < 1 or args.stop_after > 9 or args.start_at > args.stop_after:
        raise SystemExit(f"[范围非法] --start-at={args.start_at} --stop-after={args.stop_after} (须 1≤start≤stop≤9)")

    # 选中的入口序号集合
    selected = set(range(args.start_at, args.stop_after + 1))
    if args.only:
        selected &= _parse_step_ids(args.only)
    if not selected:
        raise SystemExit("[无入口被选中] --only 与 --start-at/--stop-after 取交集为空。")

    # 论文白名单 (④) + --papers 过滤
    whitelist, paper_src = _resolve_paper_ids()
    paper_ids = _resolve_papers_arg(args.papers, whitelist)

    plan = build_plan(args, paper_ids)
    for step in plan:
        step["_selected"] = step["num"] in selected

    run_start = time.time()
    _log_banner(plan, args, paper_ids, paper_src)

    # ── dry-run: 只打印计划, 不实跑 ──
    if args.dry_run:
        logger.info("【dry-run】以下为将执行的全部命令 (未获锁、未实跑、未写任何产物):")
        env_preview = build_child_env(args.offline, args.pin_blas)
        _off = env_preview.get("NEWS_PROCESS_LLM_OFFLINE", "(未设)")
        _dic = env_preview.get("LLMS_DIC_OFFLINE", "(未设)")
        logger.info("  子进程环境: PYTHONHASHSEED=%s | NEWS_PROCESS_LLM_OFFLINE=%s | LLMS_DIC_OFFLINE=%s | BLAS 钉死=%s",
                    env_preview.get("PYTHONHASHSEED"), _off, _dic, "是" if args.pin_blas else "否")
        for step in plan:
            if not step["_selected"]:
                continue
            logger.info("  %s %s", step["mark"], step["title"])
            for sublabel, cmd in step["cmds"]:
                logger.info("      $ %s", " ".join(cmd))
        logger.info("【dry-run】完毕 — 去掉 --dry-run 即按上表实跑。")
        return 0

    logger.info("依赖环境: 各入口自身依赖 (LLM 缓存 / data/processed 上游产物 / config 名单) 须已就绪; "
                "离线守卫会在缓存 miss 时 fail-loud (属预期, 非本编排器缺陷)。")
    log_memory_usage(logger, "编排启动")

    # ── 逐入口执行 (fail-fast, 除非 --keep-going) ──
    # 结果记录: num -> (墙钟秒, 状态, 失败子命令 or None)。状态 ∈ {ok, fail, skipped, not_reached}:
    #   ok/fail=实跑成功/失败; skipped=未选 (--only/范围过滤); not_reached=被选中但 fail-fast 中断前未跑到。
    results: dict[int, tuple[float, str, str | None]] = {}
    all_success = True

    for step in plan:
        num = step["num"]
        if not step["_selected"]:
            results[num] = (0.0, "skipped", None)
            continue

        env = build_child_env(args.offline, args.pin_blas)
        logger.info("")
        logger.info("─" * 78)
        logger.info("%s 开始: %s", step["mark"], step["title"])
        step_t0 = time.time()
        step_ok = True
        failed_sub: str | None = None

        for sublabel, cmd in step["cmds"]:
            if len(step["cmds"]) > 1:
                logger.info("  ▶ 子命令: %s", sublabel)
            rc, elapsed = run_one(sublabel, cmd, env)
            if rc != 0:
                step_ok = False
                failed_sub = sublabel
                logger.error("  ✗ %s 失败 (exit=%d, 墙钟 %ss)。排障: 看对应入口自身的 logs/<stem>.log。",
                             sublabel, rc, sig4(elapsed))
                break
            logger.info("  ✓ %s 完成 (墙钟 %ss)", sublabel, sig4(elapsed))

        step_dt = time.time() - step_t0
        results[num] = (step_dt, "ok" if step_ok else "fail", failed_sub)
        if step_ok:
            logger.info("%s 成功: %s (墙钟 %ss)", step["mark"], step["title"], sig4(step_dt))
        else:
            all_success = False
            logger.error("%s 失败: %s (在子命令 [%s] 处中断, 墙钟 %ss)",
                         step["mark"], step["title"], failed_sub, sig4(step_dt))
            if not args.keep_going:
                logger.error("fail-fast: 编排在 %s 处中断, 后续入口跳过 (加 --keep-going 可继续跑完再汇总)。",
                             step["mark"])
                break

    # fail-fast 中断后未跑到的入口回填 (被选中→not_reached ⛔, 未选→skipped ⏭): 保证下方汇总表
    # 恒列全 9 行, 否则断点之后被选中的入口既不显 ✗ 也不显 ⏭, 读表者无法与"被过滤"区分。
    for step in plan:
        if step["num"] not in results:
            results[step["num"]] = (0.0, "not_reached" if step["_selected"] else "skipped", None)

    # ── 汇总 ──
    total = time.time() - run_start
    _SYMBOL = {"ok": "✓", "fail": "✗", "skipped": "⏭", "not_reached": "⛔"}
    logger.info("")
    logger.info("=" * 78)
    logger.info("===    九入口执行耗时统计    ===")
    logger.info("=" * 78)
    logger.info("%-2s %-52s %12s %10s %6s", "", "入口", "墙钟(秒)", "占比", "状态")
    logger.info("-" * 78)
    n_ran = sum(1 for _dt, st, _sub in results.values() if st in ("ok", "fail"))
    for step in plan:
        dt, status, _sub = results[step["num"]]
        symbol = _SYMBOL.get(status, "?")
        pct = (dt / total * 100.0) if (status in ("ok", "fail") and total > 0) else 0.0
        _title = step["title"] if len(step["title"]) <= 50 else step["title"][:49] + "…"
        logger.info("%-2s %-52s %10ss %9.4g%% %6s", step["mark"], _title, sig4(dt), pct, symbol)
    logger.info("-" * 78)
    logger.info("  总计 %ss (%s 分钟 / %s 小时) | 实跑入口 %d 个",
                sig4(total), sig4(total / 60.0), sig4(total / 3600.0), n_ran)
    logger.info("=" * 78)
    _log_references()
    log_memory_usage(logger, "编排完成")

    if all_success:
        logger.info("✓ 已选九入口全部执行成功 — 全链闭合。")
        return 0
    logger.error("✗ 编排存在失败入口 (见上表 ✗)。逐入口排障看各自 logs/<stem>.log。")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
