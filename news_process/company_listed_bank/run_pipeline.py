"""银企共现面板流水线 orchestrator (COMPANY_BANK_COOC_PANEL_EXECUTION_PLAN v34).

按硬依赖顺序串跑四步 (子进程隔离, 任一步非零退出即中断, 镜像 run_pipeline_function.py 风格):
  01 WP0 注册表对账   → config/company_bank_cooc_registry.yaml (加权引擎唯一 SSOT)
  02 WP1 主面板构建   → company_listed_bank/data/company_bank_cooc_panel.{dta,parquet} + codebook + pair 长表
  03 WP5 七权源互验   → company_listed_bank/data/ 七替代权长表 + 七权面板 ×7 + 互验报告
  04 替代聚合权面板   → company_listed_bank/data/ frozenw/mainbankw 面板 ×2 + 权重长表 ×2 + codebook 章

日志: 本 orchestrator 与四步各写 company_listed_bank/logs/<stem>.log (格式/覆盖语义同主管道
core/logging.py::setup_logging); 数据产物统一落 company_listed_bank/data/ (不入库)。
⚠ 级联义务: 重跑 02 会重生 pair 长表且 codebook 整文件重写只保留 03 标记块 → 04 产物与
codebook「替代聚合面板章」stale, 重跑 02 后须补跑 04。

用法 (从 news_process/ 目录, conda base python):
  python company_listed_bank/run_pipeline.py                 # 全链 01→02→03→04
  python company_listed_bank/run_pipeline.py --steps 02,03,04  # 从 02 起 (registry 已就绪时; 含 02 必含 04, 级联义务)
  python company_listed_bank/run_pipeline.py --dry-run       # 只打印将执行的命令

⚠ 重跑 01 会重生 registry → 哈希锚变时须级联 02 (pair 指纹) → 03 (DV2 双向锁) → 04
  (pair 锚同代); 本 orchestrator 跑完含 01 的链后会打印锚状态判读。双值冻结期 (G9 挂账,
  2026-07-17 起): 新锚 ∈ FROZEN_REGISTRY_SHAS (激活/非激活两合法世代) 时**勿 bump 主锚**,
  仅真第三值才须 bump tests/test_company_bank_cooc_registry.py::EXPECTED_REGISTRY_SHA256。
独立派生数据流水线, 不注册 DAG (镜像 generate_company_listed_names.py 定位)。
"""
from __future__ import annotations

import argparse
import io
import logging
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
OUT_DATA = HERE / "data"
LOCK_FILE = HERE / "logs" / "_run_pipeline.lock"

logger = logging.getLogger("run_pipeline")
if not logger.handlers:  # console 兜底; main() 实跑时由 setup_logging 接管
    # A1 修复 (2026-07-09 五入口诊断): 兜底 handler 在 dry-run/锁前路径直写 stdout, 未经 setup_logging
    # 的 _configure_standard_streams reconfigure; Windows GBK(cp936) 终端遇 emoji 会 UnicodeEncodeError。
    # 用 errors='backslashreplace' 包裹流规避。⚠ pytest 经 spec_from_file_location import 本模块时
    # capture 下 sys.stdout 可能无 .buffer/fileno → try/except 回退裸 stdout, 保 import 不崩。
    try:
        _stream = io.TextIOWrapper(
            sys.stdout.buffer,
            encoding=getattr(sys.stdout, "encoding", None) or "utf-8",
            errors="backslashreplace", line_buffering=True,
        )
    except (AttributeError, ValueError, io.UnsupportedOperation):
        _stream = sys.stdout
    _h = logging.StreamHandler(_stream)
    _h.setFormatter(logging.Formatter("[pipeline] %(levelname)s %(message)s"))
    logger.addHandler(_h)
    logger.setLevel(logging.INFO)


def _init_stage_logging() -> None:
    """接入主管道日志基建 (core/logging.py::setup_logging): 写 company_listed_bank/logs/run_pipeline.log,
    格式/每次运行覆盖/50MB rotate 与主管道各阶段日志完全一致。单文件 importlib 加载, 不引入包依赖。"""
    import os
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return  # WP-A: 测试进程绝不接管文件日志 (2026-07-07 审计: 负例测试曾首写截断覆盖生产 02 日志)
    import importlib.util
    spec = importlib.util.spec_from_file_location("_np_core_logging", REPO / "core" / "logging.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.setup_logging(Path(__file__).stem, str(HERE / "logs"))
    # setup_logging 置 propagate=False (主管道防双打惯例); 本脚本进程 root 无 handler,
    # 恢复 True 无双打副作用, 且保 pytest caplog (root handler) 可捕 — 否则负例测试调过
    # main() 后, 同会话后续 caplog 断言静默失捕 (2026-07-07 实弹)
    logging.getLogger(Path(__file__).stem).propagate = True


def _pid_alive(pid: int) -> bool:
    """PID 存活判定 (psutil); 判不了一律按存活返回 — 宁可 fail-loud 拒跑, 绝不误清他人持有的锁。"""
    try:
        import psutil
        return psutil.pid_exists(pid)
    except Exception:
        return True


def _acquire_single_instance_lock() -> int:
    """orchestrator 单实例互斥锁: O_CREAT|O_EXCL 原子创建 logs/_run_pipeline.lock (内容=本 PID)。

    2026-07-07 实弹: 两个 orchestrator 相差 46 秒并发全链, 各持句柄按各自偏移交错覆写同一套
    日志 (PID 混写/时间戳倒流/行粘连) 与同一套 ~13GB 产物, 最终 company_bank_branchw_panel.dta
    留下 688MB 半成品 (后启动实例在先启动实例收尾后被杀于写盘中途)。本锁把该事故类别封死在入口。

    语义: 锁已存在 → 读持有者 PID 判存活 — 存活 → SystemExit(1) fail-loud (绝不静默排队);
    已死/不可读 → 视为陈旧锁 (上次异常退出残留), 清除后重试一次。返回持有的 fd, 由
    _release_single_instance_lock 在 main() 收尾 (含失败路径) 释放。
    ⚠ 本锁只护 orchestrator 入口; 绕过 orchestrator 直跑单步脚本仍无互斥, 并发纪律同样适用。"""
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    for attempt in (1, 2):
        try:
            fd = os.open(str(LOCK_FILE), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            try:
                os.write(fd, str(os.getpid()).encode("ascii"))
            except OSError:
                # A9 修复 (2026-07-09 五入口诊断): os.write 失败(如 ENOSPC 磁盘满)时原实现绕过下方
                # except FileExistsError 上抛且 fd 未 close → fd 泄漏 + 留 0 字节锁文件。此处清理后再抛。
                try:
                    os.close(fd)
                except OSError:
                    pass
                LOCK_FILE.unlink(missing_ok=True)
                raise
            logger.info("单实例锁已获取 (F11): PID=%d → %s (此 INFO 走兜底 console, 早于 _init_stage_logging 接管文件日志)",
                        os.getpid(), LOCK_FILE)
            return fd
        except FileExistsError:
            try:
                holder = int(LOCK_FILE.read_text(encoding="ascii").strip() or "0")
            except (OSError, ValueError):
                holder = 0
            if holder and _pid_alive(holder):
                logger.error("另一 run_pipeline 实例正在运行 (PID=%d, 锁=%s) — 拒绝启动。", holder, LOCK_FILE)
                logger.error("  并发双跑会交错覆写同一套日志与 ~13GB 产物 (2026-07-07 实弹: "
                             "branchw dta 688MB 半成品), 请等待该实例结束后再跑。")
                logger.error("  若确认 PID=%d 已不存在 (psutil 误判), 手工删除锁文件后重试。", holder)
                raise SystemExit(1)
            if attempt == 1:
                logger.warning("发现陈旧锁 (持有者 PID=%s 已不存活, 上次异常退出残留), 清除后重试",
                               holder or "不可读")
                try:
                    LOCK_FILE.unlink()
                except OSError:
                    pass
            else:
                logger.error("陈旧锁清除后仍无法获取 %s — 疑似另一实例恰在同刻启动, 拒绝启动", LOCK_FILE)
                raise SystemExit(1)
    raise AssertionError("unreachable")


def _release_single_instance_lock(fd: int) -> None:
    """释放单实例锁: 关句柄 + 删锁文件 (幂等; 删失败仅告警 — 下次启动按陈旧锁自愈)。"""
    try:
        os.close(fd)
    except OSError:
        pass
    try:
        LOCK_FILE.unlink(missing_ok=True)
        logger.info("单实例锁已释放 (F11): %s", LOCK_FILE)
    except OSError:
        logger.warning("锁文件 %s 删除失败 (无害: 下次启动按陈旧锁清除)", LOCK_FILE)


# F12: ANSI/VT100 转义序列剥离 (对齐 core/stage.py:_ANSI_ESCAPE_RE) — 第三方库对子步 stderr 直写的
# 颜色/光标码不得随转发落入 run_pipeline.log (子步经 PIPE 非 TTY 本不应着色, 此为防御性剥离; LOG-COLOR)。
_ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def _spawn_stderr_forwarder(proc: subprocess.Popen, tag: str):
    """F12 (2026-07-10): 守护线程逐行把子步 stderr forward 进 orchestrator logger (→ run_pipeline.log,
    对齐主线 core/stage.py)。原 subprocess.run 无捕获 → 子步未经 logger 的原始 stderr (未捕获 traceback /
    第三方库直写) 只入继承管道不入本 .log; 本转发使 run_pipeline.log 自足佐证 '0 traceback', 消除对会话
    capture 的单点依赖。stdout 仍继承 (保实时终端); 仅 stderr 单管道 + 持续 drain → 无 pipe 满死锁。"""
    import threading

    def _pump():
        try:
            for _line in iter(proc.stderr.readline, ''):
                logger.warning("  │⚠ %s", _ANSI_ESCAPE_RE.sub("", _line.rstrip("\r\n")))
        finally:
            try:
                proc.stderr.close()
            except Exception:
                pass

    t = threading.Thread(target=_pump, name=tag, daemon=True)
    t.start()
    return t


STEPS: list[tuple[str, str, str]] = [
    ("01", "01_build_company_bank_cooc_registry.py",
     "WP0 注册表对账 → config/company_bank_cooc_registry.yaml"),
    ("02", "02_build_company_bank_cooc_panel.py",
     "WP1 主面板 + pair 长表 + codebook"),
    ("03", "03_build_company_bank_weight_validation.py",
     "WP5 七权源 + 七替代权面板 (与 02 主面板并称八权) + 互验报告"),
    ("04", "04_build_company_bank_altagg_panels.py",
     "替代聚合权面板 (frozenw 基期冻结 + mainbankw top-1 主办银行) ×2 + 权重长表 ×2"),
]
STEP_IDS = [s[0] for s in STEPS]


# ────────────────────────── 日志辅助纯函数 (仅日志用途, 不参与任何计算/控制流) ──────────────────────────

def _pkg_version(name: str) -> str:
    """importlib.metadata 读安装版本, 仅日志用途; 未安装/任何异常一律回 'n/a' (绝不影响控制流)。"""
    try:
        from importlib.metadata import version
        return version(name)
    except Exception:
        return "n/a"


def _rss_mb() -> float | None:
    """本 orchestrator 进程自身 RSS (MB); psutil 缺席/异常回 None。仅日志用途的廉价读数。"""
    try:
        import psutil
        return psutil.Process().memory_info().rss / 1048576.0
    except Exception:
        return None


def _size_mb(p: Path) -> float | None:
    """文件体量 (MB) 的廉价 stat 读数; 缺失回 None。仅日志用途, 不打开文件内容。"""
    try:
        return p.stat().st_size / 1048576.0
    except OSError:
        return None


def _iter_artifacts(step_id: str):
    """逐步产物清单 (路径, 角色说明) — 静态口径 + 廉价 glob, 仅供落盘后体量/存在性日志。"""
    if step_id == "01":
        yield (REPO / "config" / "company_bank_cooc_registry.yaml",
               "注册表 yaml (加权引擎唯一 SSOT; 例外入库, 属配置而非数据结果)")
    elif step_id == "02":
        yield (OUT_DATA / "company_bank_cooc_panel.dta",
               "主面板 dta (Stata format 118; 20 固定列 + 加权列; 消费者 = Stata 回归 + 03 骨架)")
        yield (OUT_DATA / "company_bank_cooc_panel.parquet",
               "主面板 parquet 伴生 (未缩写全名, 供 Python 侧审计)")
        yield (OUT_DATA / "company_bank_cooc_panel_codebook.md",
               "codebook (与 news_process 主项目 codebook 互不交叉)")
        yield (OUT_DATA / "_company_bank_cooc_pairs.parquet",
               "pair 长表 10 列 (被删加权列唯一重构载体; 03 互验的锚, 缺则 03 SystemExit)")
    elif step_id == "03":
        # ⚠ glob `company_bank_*w_panel.*` 会误捕步骤 04 的 frozenw/mainbankw 产物 → 显式排除
        # (否则 04 产物被清点/落盘合计误归 03 名下; R2 爆炸半径审计 P0)
        _not_03 = ("company_bank_frozenw_panel", "company_bank_mainbankw_panel")
        for p in sorted(OUT_DATA.glob("_company_bank_altweights_*.parquet")):
            yield p, "替代权长表 (统一 schema company/bank/year/w [+稳健臂])"
        for p in sorted(OUT_DATA.glob("company_bank_*w_panel.dta")):
            if p.stem not in _not_03:
                yield p, "替代权面板 dta (与主面板同引擎同列名, scheme 身份由文件名承载)"
        for p in sorted(OUT_DATA.glob("company_bank_*w_panel.parquet")):
            if p.stem not in _not_03:
                yield p, "替代权面板 parquet 伴生"
        yield (OUT_DATA / "_company_bank_weight_validation.md",
               "互验报告 (DV5 五件套 + 顶刊披露包 + 未映射审计附录)")
    elif step_id == "04":
        for scheme, word in (("frozenw", "基期冻结"), ("mainbankw", "主办银行")):
            yield (OUT_DATA / f"company_bank_{scheme}_panel.dta",
                   f"{word}替代聚合面板 dta (与主面板同引擎同列名, scheme 身份由文件名承载)")
            yield (OUT_DATA / f"company_bank_{scheme}_panel.parquet",
                   f"{word}替代聚合面板 parquet 伴生")
        yield (OUT_DATA / "_company_bank_altagg_frozen.parquet",
               "frozenw 权重长表 (基期行展年, 含 base_year; metadata 内嵌 registry 锚)")
        yield (OUT_DATA / "_company_bank_altagg_mainbank.parquet",
               "mainbankw 权重长表 (每格单行 + 平票诊断列; metadata 内嵌 registry 锚)")
        yield (OUT_DATA / "company_bank_cooc_panel_codebook.md",
               "codebook (本步幂等 upsert「替代聚合面板」章 → 体量为追加后终值; 02 台账所记为该步时点值)")


def _log_banner(selected_ids: list[str]) -> None:
    """运行头 banner: 流水线定位/上下游/复现命令/关键 config/环境版本 — 复现材料级最小充分信息。"""
    logger.info("=" * 70)
    logger.info("银企共现面板流水线 orchestrator (COMPANY_BANK_COOC_PANEL_EXECUTION_PLAN v34)")
    logger.info("定位: 上市公司×年 银企共现媒体报道面板四步生产链 (registry → 主面板 → 七权源互验 → 替代聚合)")
    logger.info("  · 规模锚: 105,032 行 = 5,528 家上市公司 × 19 年 (2007–2025) 全骨架, 含零覆盖行")
    logger.info("  · 上游(只读): data/processed/ 五 parquet (40/51/27/16/21_full, 主管道产物)")
    logger.info("  · 上游(权源): config/ 四份商业 dta (借款/分支/董监高/股东; 恒不入库)")
    logger.info("  · 下游消费者: Stata 银企回归 (七权+替代聚合面板互为规格稳健性臂) + gate 测试五件 (pytest 收集 12+59+54+7+15=147 项)")
    logger.info("  · 关键 config 键: config/company_bank_cooc_registry.yaml (加权引擎唯一 SSOT, 01 产出)")
    logger.info("  · 目标银行映射: registry 顶层 bank_company_map (D4, 42 家; 牡丹江锁 target_bank=龙江银行)")
    logger.info("  · DAG 关系: 独立派生数据流水线, 不注册主 DAG (镜像 generate_company_listed_names.py 定位);")
    logger.info("    只读消费主管道 data/processed/ 产物, 绝不反向写回 — 主线 golden/OUTPUT_REGISTRY 零波及")
    logger.info("  · 并发安全: 单实例锁 logs/_run_pipeline.lock (O_CREAT|O_EXCL 原子创建, fail-loud 拒排队;")
    logger.info("    2026-07-07 双实例交错覆写 ~13GB 产物实弹后封死; 锁只护本入口, 直跑单步脚本仍须人工纪律)")
    logger.info("  · 审计追踪: 本 .log 逐条记录实际命令行/环境库版本/子进程 env 注入 (PYTHONHASHSEED=0)/")
    logger.info("    逐步产物精确字节数/registry 哈希锚三方对比 — 设计目标 = 日志本身可作复现材料级审计底稿")
    logger.info("  · 执行计划出处: COMPANY_BANK_COOC_PANEL_EXECUTION_PLAN v34 (v16–v33 评审史与文献锚点在同名 ARCHIVE)")
    logger.info("复现命令 (从 news_process/ 目录, conda base python):")
    logger.info("  python company_listed_bank/run_pipeline.py                 # 全链 01→02→03→04")
    logger.info("  python company_listed_bank/run_pipeline.py --steps 02,03,04 # registry 已就绪时从 02 起")
    logger.info("  python company_listed_bank/run_pipeline.py --dry-run       # 只打印将执行的命令")
    logger.info("本次选定步骤: %s (顺序恒按 01→02→03→04 硬依赖执行, 传入序不生效)", ", ".join(selected_ids))
    logger.info("环境 (importlib.metadata, 仅日志用途): Python %s", sys.version.split()[0])
    logger.info("  pandas %s | numpy %s | pyarrow %s | pyreadstat %s",
                _pkg_version("pandas"), _pkg_version("numpy"),
                _pkg_version("pyarrow"), _pkg_version("pyreadstat"))
    logger.info("  pyahocorasick %s | PyYAML %s | psutil %s",
                _pkg_version("pyahocorasick"), _pkg_version("PyYAML"), _pkg_version("psutil"))
    rss = _rss_mb()
    if rss is not None:
        logger.info("  启动时 orchestrator RSS %.4g MB (四步各为独立子进程, 峰值内存见各步骤自身日志)", rss)
    logger.info("=" * 70)


def _log_step_context(step_id: str) -> None:
    """步骤开跑前的输入/输出角色与缺失语义说明 (静态口径 + 廉价存在性读数), 仅日志用途。"""
    if step_id == "01":
        logger.info("  输入: 五上游 parquet 全列名 (data/processed/, 只读) + 裁剪负清单")
        logger.info("        COMPANY_BANK_COOC_PANEL_CUT_LIST_v23.txt + 两名单 SSOT yaml (公司/银行清单)")
        logger.info("  职责: D15/D11 全划分对账 (残差非零 → SystemExit) + D16 短名 (≤32 全局唯一) + sha256 哈希锚")
        logger.info("  输出: config/company_bank_cooc_registry.yaml — 02/03 加权引擎与 gate 测试的唯一 SSOT")
        logger.info("  fail-loud 语义: registry 是下游三步的单点契约, 对账失败宁崩不产 — 静默漏列会无声传染")
        logger.info("        全部八权+替代聚合面板; 哈希锚由 tests/test_company_bank_cooc_registry.py 长期看守")
    elif step_id == "02":
        reg = REPO / "config" / "company_bank_cooc_registry.yaml"
        logger.info("  输入: registry yaml (启动校验哈希锚, 当前%s; 缺则 02 拒跑) + 五上游 parquet",
                    "存在" if reg.exists() else "缺失")
        logger.info("  输出: 主面板 dta/parquet (105,032 行, 20 固定列 + 加权列) + codebook + pair 长表 10 列")
        logger.info("  缺失语义: rel_n_banks=0 的公司-年 cw/ce 置 NaN (非 0, 勿把无关系年当零暴露); rel_hhi∈(0,1]")
        logger.info("  pair 长表 = 被删加权列的唯一重构载体, 亦是 03 互验的锚 (跨年去重键禁含 year)")
        logger.info("  失败模式: registry 哈希锚不匹配 / 上游 parquet 缺列 → SystemExit 拒产 stale 面板 (fail-loud);")
        logger.info("        dta 走 Stata format 118 (文件格式 spec 编号) 定长字符串, 体量 ≫ parquet 属格式预期")
    elif step_id == "03":
        pairs = OUT_DATA / "_company_bank_cooc_pairs.parquet"
        logger.info("  输入: registry (DV2 常量双向锁) + 02 pair 长表 (当前%s; 缺则 SystemExit: 无锚即无互验)",
                    "存在" if pairs.exists() else "缺失")
        logger.info("        + config/ 四份商业 dta 权源 (借款/分支/董监高/股东)")
        logger.info("  权源 7 scheme: loan/branch/board/supervisor/exec/dsg/shareholder (银行名 canon 化 = DV2 判定序)")
        logger.info("  输出: 七替代权长表 ×7 + 七权面板 dta/parquet ×7 + 互验报告 md (共 22 文件, 均不入库)")
        logger.info("  互验口径: 与主面板同引擎同列名 (cw_/ce_{基名}_{track}), scheme 身份由文件名承载 (D18 单引擎)")
        logger.info("  缺失语义: 公司-年在某权源无关系 → 该权面板加权列 NaN (非 0, 与主面板同口径); 未映射银行")
        logger.info("        名单入互验报告附录供人工复核, 绝不静默丢弃 — 七权覆盖差异本身即研究信息")
    elif step_id == "04":
        pairs = OUT_DATA / "_company_bank_cooc_pairs.parquet"
        logger.info("  输入: registry (只读, 零改动零 bump) + 02 pair 长表 (当前%s; 缺/stale 锚则 SystemExit)"
                    " + 五上游 parquet (测度库与 02 同源)", "存在" if pairs.exists() else "缺失")
        logger.info("  输出: frozenw/mainbankw 面板 dta+parquet ×2 + 权重长表 ×2 + codebook「替代聚合面板章」")
        logger.info("  口径: frozenw=首个共现年份额冻结 (左截断不回退, GPSS initial-share) / mainbankw=当年")
        logger.info("        argmax 三级平票 (严格 top-1 不顺延); 与八权互为规格稳健性臂, 禁混同一 Hansen J")


def _log_step_done(step_id: str, dt: float) -> None:
    """步骤成功后的产物清点 (体量/角色) + 吞吐率 — 只消费已算出的墙钟与廉价 stat 读数。"""
    rss = _rss_mb()
    if rss is not None:
        logger.info("步骤 %s 完成: 墙钟 %.4gs | orchestrator RSS %.4g MB (子进程已退出, 其峰值见该步骤日志)",
                    step_id, dt, rss)
    else:
        logger.info("步骤 %s 完成: 墙钟 %.4gs", step_id, dt)
    total_mb = 0.0
    n_ok = 0       # 仅日志用途的产物计数 (只读 stat 清点, 不参与任何计算/控制流)
    n_missing = 0
    for p, desc in _iter_artifacts(step_id):
        mb = _size_mb(p)
        if mb is None:
            n_missing += 1
            logger.warning("  产物缺失: %s — %s", p.name, desc)
        else:
            n_ok += 1
            total_mb += mb
            # 精确字节数供跨轮机器对账 (%.4g MB 4 位有效数字不足以证字节等价)
            logger.info("  产物 %-42s %.4g MB (%s B) — %s",
                        p.name, mb, f"{int(round(mb * 1048576.0)):,d}", desc)
    logger.info("  产物清点: %d 个在盘 / %d 个缺失 (缺失非零时上方已逐个 WARNING; 清点=审计底稿必录项,"
                " rc=0 但产物缺席即形态漂移信号)", n_ok, n_missing)
    if total_mb > 0 and dt > 0:
        logger.info("  本步落盘合计 %.4g MB, 吞吐 %.4g MB/s (墙钟口径, 含计算+IO; 体量为盘上现值)",
                    total_mb, total_mb / dt)
    if step_id == "02" and dt > 0:
        logger.info("  主面板文档口径 105,032 行 → 构建吞吐 %.4g 行/s (墙钟口径)", 105032.0 / dt)


def _log_run_summary(step_stats: list[tuple[str, str, float]], total: float) -> None:
    """收尾统计报告 + 【结果分析】逐条经济学/方法学判读 — 仅消费已算出的墙钟, 无新增计算。"""
    ran = {s for s, _, _ in step_stats}
    logger.info("=" * 70)
    logger.info("【统计报告 · 墙钟分解】总墙钟 %.4gs ≈ %.4g 分钟", total, total / 60.0)
    for step_id, desc, dt in step_stats:
        share = 100.0 * dt / total if total > 0 else 0.0
        logger.info("  步骤 %s: %.4gs (占 %.4g%%) — %s", step_id, dt, share, desc)
    logger.info("  (占比判读: 墙钟分解是 IO/计算配比的粗诊断量 — 是什么: 各步墙钟对总墙钟的份额; 为什么看:")
    logger.info("   03 重 IO 落盘 ~13GB 使其占比对磁盘顺序写速度最敏感; 怎么判: 参照带 = 2026-07-08 提速")
    logger.info("   验收实测 19.06–24.97 MB/s (历史样本非本轮判据 — 宿主功耗策略 [07-15 N7 定谳: AC 95% 限频")
    logger.info("   禁睿频 → 全链 ~3× 慢化] 或并发争用可使实测带整体下移, 以本轮台账实录+当日宿主状态为准),")
    logger.info("   骤降先查盘顺序写与宿主争用再疑代码回归 — 07-15 审计教训:")
    logger.info("   慢化归因先做 CPU 满载百分比 + 盘顺序写两个 5 分钟实测定谳, 勿靠时间窗相关)")
    logger.info("【结果分析 · 判读】")
    logger.info("  · 走到本节 = 所选步骤 rc 全 0, 硬依赖链完整闭合: registry 哈希锚 → 主面板/pair 指纹 →")
    logger.info("    DV2 双向锁 → 04 pair 锚同代校验; 任一环节断裂会 fail-loud 中断, 本节根本不会打印")
    if "01" in ran:
        logger.info("  · 01 判读: 秒级墙钟为健康区间; 失败/骤慢通常 = 上游 parquet 列名漂移或负清单不同步")
        logger.info("    (全划分残差非零即 SystemExit 是防静默漏列的设计 — 翻红应查列名对账而非盲目重试)")
    if "02" in ran:
        logger.info("  · 02 判读: 分钟级墙钟为健康区间; 面板保留全骨架 (零共现公司-年不删行, 缺权重记 NaN")
        logger.info("    而非 0), 避免以媒体覆盖存活为条件的幸存者/选择偏差; dta ≈1.6GB 系 Stata format 118")
        logger.info("    定长字符串所致, dta ≫ parquet 属格式预期而非数据膨胀异常")
    if "03" in ran:
        logger.info("  · 03 判读: 占总墙钟约九成为预期形态 (7 权源 × 全套加权面板 × dta+parquet 双格式落盘,")
        logger.info("    合计约 13GB, IO-bound); 占比骤降多半 = 某 scheme 长表全缺被跳过, 须查 03 日志的")
        logger.info("    逐权逐年覆盖表; 单银行公司-年 rel_hhi 恒 1 属定义使然, 非集中度异常")
        logger.info("  · 03 形态锚: 七权 dta 字节数完全一致是定长 format 118 + 同骨架同列宽的机械结果, 非复制")
        logger.info("    错误 (参照: 2026-07-08 实测均 1,603,484,161 B; ⚠ 该锚随 registry 列集漂移 [如 G9 +9 列")
        logger.info("    激活] 整体平移, 以当代 registry sha 下同轮七权互等为判据而非历史绝对值); 信息量在")
        logger.info("    parquet 侧 — 替代权长表与面板 parquet 体量随各权源关系覆盖稀疏度分化 (参照带 0.01053–")
        logger.info("    23.67 / 1.864–22.94 MB, 同轮实测见上方台账), 该分化才是覆盖审计的观察对象")
        logger.info("  · 互验判读: 富集度须双基准并报 (计划 v31 实弹: 均匀基准 4.85× vs 边际保持置换基准")
        logger.info("    1.16×) — 只报均匀基准会夸大收敛效度; 七权面板为规格稳健性并排臂, 按 specification-")
        logger.info("    curve 口径逐权独立报告, 不混作同一回归的多工具")
    if "04" in ran:
        logger.info("  · 04 判读: frozenw dev 上基期几乎全 2017、仅 2018 有非平凡冻结差属预期构造退化")
        logger.info("    (生产 T=19 恢复); 两面板与八权各自 just-identified 并排, 禁混同一 Hansen J;")
        logger.info("    重跑 02 后本步产物与 codebook 章 stale, 须补跑 04 (级联义务)")
    if "02" in ran and "04" not in ran:
        # D9 (2026-07-18): 级联义务运行时提醒 — 旧实现唯一提醒挂在 `if "04" in ran` 内
        # (义务已履行时才打印), 「含 02 不含 04」的违约组合反而零提醒。
        logger.warning("  · ⚠ 本轮重跑了 02 但未跑 04 — 04 产物 (frozenw/mainbankw 面板+权重长表) "
                       "与 codebook「替代聚合面板章」已 stale, 须补跑 --steps 04 (级联义务)")
    logger.info("  · 生产 T=19 预期差异: 当前上游 21_full 为 dev 语料口径, 覆盖/富集度实测以互验报告为准;")
    logger.info("    生产重跑后 §9.4 级联义务生效 (哈希锚 bump → 02 pair 指纹 → 03 双向锁), 墙钟与 IO 同步放大")
    logger.info("  · 判读框架 (本节每个统计量的四层口径): ①是什么 (统计量定义与口径) → ②为什么看 (它防哪类")
    logger.info("    威胁: 静默漏列/幸存者偏差/stale 产物/形态漂移) → ③怎么判 (dev 实测健康区间) → ④学术依据")
    logger.info("    (见下方 📖 节逐条锚定); 所有健康区间均为 dev T=2 实测锚, 生产 T=19 首跑须按实测重标定,")
    logger.info("    耗时基线不可跨状态外推 (07-16 审计裁定: 预算=最近同状态实测)")


def _log_references() -> None:
    """📖 方法论依据 — APA 引文逐字取自审定引文池 (仅整理换行); 白话注解落到本脚本的具体设计决策。"""
    logger.info("-" * 70)
    logger.info("📖 方法论依据 (APA 第 7 版, 逐字取自审定引文池; 每条附本脚本具体设计决策的锚定说明)")
    logger.info("[数据工程与可复现计算]")
    logger.info("  1. Sandve, G. K., Nekrutenko, A., Taylor, J., & Hovig, E. (2013). Ten simple rules for")
    logger.info("     reproducible computational research. PLoS Computational Biology, 9(10), e1003285.")
    logger.info("     https://doi.org/10.1371/journal.pcbi.1003285")
    logger.info("     → 白话: 可复现计算十规则 (method-origin 经典)。本 orchestrator 落实其中多条: 逐条记录实际")
    logger.info("       执行命令行、固定随机种子 (向子进程注入 PYTHONHASHSEED=0)、全部中间产物落盘且精确字节数")
    logger.info("       入日志。迁移边界: 原文面向生物信息管道, 规则本身对任何计算实证管道通用。")
    logger.info("  2. Chen, A. Y., & Zimmermann, T. (2022). Open source cross-sectional asset pricing.")
    logger.info("     Critical Finance Review, 11(2), 207–264. https://doi.org/10.1561/104.00000112")
    logger.info("     → 白话: 把面板生产做成可一键重建的代码本身就是研究基础设施。本链以 registry 唯一 SSOT +")
    logger.info("       02/03 单引擎双函数复用 (禁第二份实现) 实现同等的\"代码即口径\"可审计性。")
    logger.info("  3. Fink, L., & Marcus, J. (2024). Replication code availability over time and across")
    logger.info("     fields: Evidence from the German Socio-Economic Panel. Economic Inquiry, 63(2),")
    logger.info("     357–386. https://doi.org/10.1111/ecin.13267")
    logger.info("     → 白话: 复现代码会随时间流失 (\"论文在、代码丢\")。本链把复现命令直接写进每次运行日志头,")
    logger.info("       代码/口径/产物清单同仓共存, 使任一未来读者仅凭本 .log 即能定位并重跑全链。")
    logger.info("[复现危机与大样本证据]")
    logger.info("  4. Brodeur, A., Mikola, D., Cook, N., Fiala, L., Brailey, T., Briggs, R., de Gendre, A.,")
    logger.info("     Dupraz, Y., Gabani, J., Gauriot, R., Haddad, J., Lima, G., Ankel-Peters, J., Dreber, A.,")
    logger.info("     Campbell, D., Kattan, L., Marino Fages, D., Mierisch, F., Sun, P., … Zhong, Y. (2026).")
    logger.info("     Reproducibility and robustness of economics and political science research. Nature,")
    logger.info("     652(8108), 151–156. https://doi.org/10.1038/s41586-026-10251-x")
    logger.info("     → 白话: 大样本复现研究表明复现成败高度取决于材料完备度。本日志记录环境库版本、逐步产物")
    logger.info("       清单/体量/角色与失败排障入口, 即为审稿人与 data editor 准备的最小充分复现信息。")
    logger.info("  5. Brodeur, A., Sung, S. Y., Miguel, E., Vilhuber, L., & Hoces de la Guardia, F. (2025).")
    logger.info("     Assessing reproducibility in economics using standardized crowd-sourced analysis")
    logger.info("     (NBER Working Paper No. 33753). National Bureau of Economic Research.")
    logger.info("     https://doi.org/10.3386/w33753")
    logger.info("     → 白话: 标准化复现协议能显著压低复现结果的方差。本链把\"复现\"标准化为单条命令 (全链")
    logger.info("       01→02→03→04 顺序固化, 传入序不生效), 消除复现者的操作自由度。")
    logger.info("  6. Fišar, M., Greiner, B., Huber, C., Katok, E., Ozkes, A. I., & the Management Science")
    logger.info("     Reproducibility Collaboration. (2024). Reproducibility in Management Science.")
    logger.info("     Management Science, 70(3), 1343–1356. https://doi.org/10.1287/mnsc.2023.03556")
    logger.info("     → 白话: 期刊级复现协作发现, 数据+代码到位时大部分结果可复现 — 材料完备度是第一决定因素。")
    logger.info("       本步骤日志的产物字节数/哈希锚三方对比即\"到位\"的机器可验证证据。")
    logger.info("  7. Dreber, A., & Johannesson, M. (2024). A framework for evaluating reproducibility and")
    logger.info("     replicability in economics. Economic Inquiry, 63(2), 338–356.")
    logger.info("     https://doi.org/10.1111/ecin.13244")
    logger.info("     → 白话: 区分\"同数据同代码复现\"与\"新数据再现\"的概念框架。本链承诺的是其最窄义 computational")
    logger.info("       reproducibility: 同输入同代码 → registry 哈希锚与产物字节数逐位可对账。")
    logger.info("[研究者自由度与规格稳健]")
    logger.info("  8. Silberzahn, R., Uhlmann, E. L., Martin, D. P., Anselmi, P., Aust, F., Awtrey, E., …")
    logger.info("     Nosek, B. A. (2018). Many analysts, one data set: Making transparent how variations")
    logger.info("     in analytic choices affect results. Advances in Methods and Practices in Psychological")
    logger.info("     Science, 1(3), 337–356. https://doi.org/10.1177/2515245917747646")
    logger.info("     → 白话: 同一数据同一假设, 29 个团队结论系统性发散。本 orchestrator 把执行序/口径/随机种子")
    logger.info("       全部固化并入日志, 就是把\"跑法自由度\"这一发散源在团队内压到零。")
    logger.info("  9. Breznau, N., Rinke, E. M., Wuttke, A., Nguyen, H. H. V., Adem, M., Adriaans, J., …")
    logger.info("     Żółtak, T. (2022). Observing many researchers using the same data and hypothesis")
    logger.info("     reveals a hidden universe of uncertainty. Proceedings of the National Academy of")
    logger.info("     Sciences, 119(44), Article e2203150119. https://doi.org/10.1073/pnas.2203150119")
    logger.info("     → 白话: 即使全流程透明, 隐性建模决策仍造成结论发散。本链把数据构建决策显式编号入册")
    logger.info("       (registry 负清单/D 系决策), 并全量转发子步 stderr (F12) — 隐性决策无处藏身。")
    logger.info("  10. Huntington-Klein, N., Arenas, A., Beam, E., Bertoni, M., Bloem, J. R., Burli, P.,")
    logger.info("     Chen, N., Grieco, P., Ekpe, G., Pugatch, T., Saavedra, M., & Stopnitzky, Y. (2021).")
    logger.info("     The influence of hidden researcher decisions in applied microeconomics. Economic")
    logger.info("     Inquiry, 59(3), 944–960. https://doi.org/10.1111/ecin.12992")
    logger.info("     → 白话: 数据清洗/样本构建阶段的隐藏决策与建模决策同样改变结论。本链的裁剪负清单与全划分")
    logger.info("       对账 (残差非零即崩) 把\"哪些列进面板\"从隐藏决策变成有案可查的显式契约。")
    logger.info("  11. Simonsohn, U., Simmons, J. P., & Nelson, L. D. (2020). Specification curve analysis.")
    logger.info("     Nature Human Behaviour, 4(11), 1208–1214. https://doi.org/10.1038/s41562-020-0912-z")
    logger.info("     → 白话: 把合理规格全枚举再看结论分布, 而非只报一条。步骤 03 用借款/分支/董监高/股东等")
    logger.info("       7 个独立权源对同一共现构念批量生产平行面板, 就是把\"权重矩阵怎么选\"这条研究者自由度")
    logger.info("       摊开成规格曲线供互验。")
    logger.info("  12. Steegen, S., Tuerlinckx, F., Gelman, A., & Vanpaemel, W. (2016). Increasing")
    logger.info("     transparency through a multiverse analysis. Perspectives on Psychological Science,")
    logger.info("     11(5), 702–712. https://doi.org/10.1177/1745691616658637")
    logger.info("     → 白话: 数据构建本身就有多宇宙 (同一原始数据可加工出多个合理数据集)。八权 + frozenw/")
    logger.info("       mainbankw 即数据多宇宙的受控物化: 各臂互为规格稳健性、不分主次, 各自 just-identified")
    logger.info("       并排独立报告, 禁混同一 over-identified Hansen J。")
    logger.info("  13. Brodeur, A., Cook, N., & Heyes, A. (2020). Methods matter: p-hacking and publication")
    logger.info("     bias in causal analysis in economics. American Economic Review, 110(11), 3634–3660.")
    logger.info("     https://doi.org/10.1257/aer.20190687")
    logger.info("     → 白话: p 值在显著性阈值附近异常堆积 = 选择性报告的痕迹。本链把全部平行面板一次性批量")
    logger.info("       产齐并逐权独立落盘, 使\"只挑显著的那个权重报\"在数据生产层即无操作空间。")
    logger.info("[面板构建与样本选择]")
    logger.info("  14. Brown, S. J., Goetzmann, W., Ibbotson, R. G., & Ross, S. A. (1992). Survivorship")
    logger.info("     bias in performance studies. The Review of Financial Studies, 5(4), 553–580.")
    logger.info("     https://doi.org/10.1093/rfs/5.4.553")
    logger.info("     → 白话: 只留\"活下来/被报道\"的样本会系统性高估效应。步骤 02 保留 5,528 公司 × 19 年全")
    logger.info("       骨架 (零共现公司-年不删行, 缺权重记 NaN 而非 0), 正是为切断这条选择偏差通道。")
    logger.info("  15. Muhammad, T. (2026). Temporal coverage bias in financial panel data: A coverage-aware")
    logger.info("     structuring framework with evidence from the Dhaka Stock Exchange [Preprint]. arXiv.")
    logger.info("     https://doi.org/10.48550/arXiv.2603.20237")
    logger.info("     → 白话: 面板的时间覆盖不均本身就是偏差源, 须显式建档而非默认删行。本链保留零覆盖行并把")
    logger.info("       逐权逐年覆盖表写进互验报告, 即 coverage-aware 构面板。迁移边界: 其证据来自达卡交易所")
    logger.info("       行情面板, 框架对媒体覆盖面板同样适用。")
    logger.info("[银企关系权源与聚合口径]")
    logger.info("  16. Amiti, M., & Weinstein, D. E. (2018). How much do idiosyncratic bank shocks affect")
    logger.info("     investment? Evidence from matched bank-firm loan data. Journal of Political Economy,")
    logger.info("     126(2), 525–587. https://doi.org/10.1086/696272")
    logger.info("     → 白话: 银行-企业配对面板是分解银行侧冲击的标准载体。本链的公司×银行×年 pair 长表与")
    logger.info("       loan 权源即此类配对锚在中国上市公司语境的实现。")
    logger.info("  17. Berger, A. N., & Udell, G. F. (1995). Relationship lending and lines of credit in")
    logger.info("     small firm finance. The Journal of Business, 68(3), 351–381. https://doi.org/10.1086/296668")
    logger.info("     → 白话: 借贷关系是银企信息传导的第一通道 (method-origin 经典)。步骤 03 以 loan 为七权源")
    logger.info("       之首的构念依据即在此; 其余六权源提供非信贷通道的平行测度。")
    logger.info("  18. Boot, A. W. A. (2000). Relationship banking: What do we know? Journal of Financial")
    logger.info("     Intermediation, 9(1), 7–25. https://doi.org/10.1006/jfin.2000.0282")
    logger.info("     → 白话: \"主办银行关系\"有排他性与信息租金两个理论特征。步骤 04 mainbankw 取当年 argmax")
    logger.info("       严格 top-1 不顺延, 正是把\"主关系银行\"的排他定义落成聚合口径。")
    logger.info("  19. Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What,")
    logger.info("     when, why, and how. American Economic Review, 110(8), 2586–2624.")
    logger.info("     https://doi.org/10.1257/aer.20181047")
    logger.info("     → 白话: Bartik/shift-share 识别把外生性锚定在基期份额上。步骤 04 frozenw 首个共现年份额")
    logger.info("       冻结 (左截断不回退) 直接镜像该 initial-share 逻辑; 铁律: frozenw/mainbankw 与八权互为")
    logger.info("       规格稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="银企共现面板流水线: 01 registry → 02 panel → 03 weights → 04 altagg (硬依赖顺序)")
    ap.add_argument("--steps", default=",".join(STEP_IDS),
                    help="逗号分隔步骤子集 (默认全链); 顺序恒按 01→02→03→04, 传入序不生效")
    ap.add_argument("--dry-run", action="store_true", help="只打印将执行的命令, 不实跑")
    args = ap.parse_args(argv)

    wanted = {s.strip() for s in args.steps.split(",") if s.strip()}
    unknown = wanted - set(STEP_IDS)
    if unknown:
        ap.error(f"未知步骤 {sorted(unknown)} (合法: {STEP_IDS})")
    selected = [s for s in STEPS if s[0] in wanted]  # 恒按声明序执行
    if not selected:
        ap.error("--steps 为空")

    lock_fd: int | None = None
    if not args.dry_run:
        # ⚠ 锁必须先于 _init_stage_logging: setup_logging 以 'w' 打开日志文件, 若第二实例
        # 先接管文件日志再被锁拒, 会把在跑实例的 run_pipeline.log 首写截断清零。
        # 被拒实例的报错走模块顶部的 console 兜底 handler, 不触盘。
        lock_fd = _acquire_single_instance_lock()
    # A5 修复 (2026-07-09 五入口诊断): _init_stage_logging() 原在 try 外, 若它抛异常(importlib
    # exec_module / setup_logging 'w' 开文件 OSError)则 finally 不执行 → fd 泄漏 + 锁残留。移入 try
    # 使锁在任何失败路径都释放。⚠ 承重铁律: ①acquire 仍先于 _init(锁序不变, 见上方注释);
    # ②_init 保留 `if not args.dry_run` 守卫(否则 dry-run 会 setup_logging 截断 run_pipeline.log)。
    try:
        if not args.dry_run:
            _init_stage_logging()
        return _run(args, wanted, selected)
    finally:
        if lock_fd is not None:
            _release_single_instance_lock(lock_fd)


def _registry_sha() -> str | None:
    """读盘上 registry meta.registry_sha256 (yaml.safe_load, 与 02/03/gate 测试同一解析路径,
    禁第二份实现); 缺文件/缺键/解析失败 → None (fail-soft, 本函数仅服务收尾判读日志)。"""
    reg = REPO / "config" / "company_bank_cooc_registry.yaml"
    try:
        import yaml
        with open(reg, encoding="utf-8") as fh:
            sha = yaml.safe_load(fh).get("meta", {}).get("registry_sha256")
        return sha if isinstance(sha, str) and len(sha) == 64 else None
    except Exception:
        return None


def _expected_registry_anchor() -> str | None:
    """读 gate 测试锚 EXPECTED_REGISTRY_SHA256 (正则取常量字面量); 不可读 → None。"""
    test_file = REPO / "tests" / "test_company_bank_cooc_registry.py"
    try:
        m = re.search(r'^EXPECTED_REGISTRY_SHA256\s*=\s*["\']([0-9a-f]{64})["\']',
                      test_file.read_text(encoding="utf-8"), re.M)
        return m.group(1) if m else None
    except Exception:
        return None


def _expected_registry_anchor_activated() -> str | None:
    """读双值冻结集副锚 EXPECTED_REGISTRY_SHA256_ACTIVATED (N17/D-4fix, 2026-07-18)。

    激活代 (G9 双值冻结的第二合法世代) 盘面下, 收尾判读若只认主锚会误导「须 bump」
    — 照做即重演 3ccd5df4→3938a2df 的 D-1 拉锯。不可读 → None (fail-soft, 仅日志)。
    """
    test_file = REPO / "tests" / "test_company_bank_cooc_registry.py"
    try:
        m = re.search(r'^EXPECTED_REGISTRY_SHA256_ACTIVATED\s*=\s*["\']([0-9a-f]{64})["\']',
                      test_file.read_text(encoding="utf-8"), re.M)
        return m.group(1) if m else None
    except Exception:
        return None


def _cascade_note(completed: set | None) -> str:
    """级联义务判读文案 (D10/D-3fix, 2026-07-18): 按实际完成集合生成, 证据驱动 —
    旧文案「本链若含 02/03 则已级联」按成员资格判定, 在步骤失败路径上为假陈述且漏 04。"""
    done = completed or set()
    chain = {"02", "03", "04"}
    if chain <= done:
        return "级联链 02→03→04 本链已全部成功, 已级联"
    missing = "/".join(sorted(chain - done))
    return f"级联链 02→03→04 未完整 (本链已成功: {'/'.join(sorted(done & chain)) or '无'}; 须补跑 {missing} 及其下游)"


def _log_registry_anchor_status(pre_sha: str | None, completed: set | None = None) -> None:
    """01 重生 registry 后的哈希锚判读: 盘上锚 vs 跑前快照 vs gate 双值冻结锚 (证据驱动;
    含步骤失败提前退出路径 — 只要 01 已成功落盘, 锚状态就必须被披露)。

    D-4fix (2026-07-18): 增加激活代副锚判读 — 盘上锚 ∈ 双值冻结集时勿再误导「须 bump」;
    D-3fix: 级联文案改按实际完成集合 (completed) 生成并补 04 (见 _cascade_note)。
    """
    post_sha = _registry_sha()
    if post_sha is None:
        logger.warning("本次重生了 registry, 但 meta.registry_sha256 读取失败 — 请人工核对 "
                       "config/company_bank_cooc_registry.yaml 与测试锚 (勿在未核对前 bump)")
        return
    expected = _expected_registry_anchor()
    activated = _expected_registry_anchor_activated()
    changed = pre_sha is None or post_sha != pre_sha
    if expected is not None and post_sha != expected:
        if activated is not None and post_sha == activated:
            logger.warning("本次重生了 registry: 盘上锚 %s… = 激活代副锚 (双值冻结集内合法世代) "
                           "— **勿 bump 主锚** (照做即重演 D-1 拉锯), G9 级联收口后回归单值; %s",
                           post_sha[:16], _cascade_note(completed))
        else:
            logger.warning("本次重生了 registry: 盘上锚 %s… ∉ 双值冻结集 {主锚 %s…, 副锚 %s} — "
                           "真第三值, 须核对后 bump tests/test_company_bank_cooc_registry.py::"
                           "EXPECTED_REGISTRY_SHA256; %s",
                           post_sha[:16], expected[:16],
                           (activated or "不可读")[:16], _cascade_note(completed))
        return
    anchor_note = ", 与测试主锚一致" if expected is not None else " (测试锚不可读, 未对比)"
    if not changed:
        logger.info("本次重生了 registry: 哈希锚未变 (%s…%s) — 无需 bump 测试锚, 02/03/04 免级联义务"
                    " (锚未含 meta 输入指纹, registry 文件字节可有 meta 级漂移, 以 git diff 为准)",
                    post_sha[:16], anchor_note)
    else:
        logger.warning("本次重生了 registry 且哈希锚变更 (%s… → %s…%s): %s",
                       (pre_sha or "无旧值")[:16], post_sha[:16], anchor_note,
                       _cascade_note(completed))


def _run(args: argparse.Namespace, wanted: set[str], selected: list[tuple[str, str, str]]) -> int:
    """main() 的执行主体 (锁获取之后); 拆出以保证任何 return/异常路径都经 finally 释放锁。"""
    if not args.dry_run:
        _log_banner([s[0] for s in selected])

    # 跳步前置自检 (fail-loud 提前于子进程闸, 报错更可读; 02/03 自身仍有权威闸)
    if "01" not in wanted and {"02", "03", "04"} & wanted:
        reg = REPO / "config" / "company_bank_cooc_registry.yaml"
        if not reg.exists():
            logger.error("缺 %s 且未选 01 — registry 是 02/03/04 的唯一 SSOT", reg)
            logger.error("  修复: 先跑 `python company_listed_bank/run_pipeline.py --steps 01` 或改跑全链")
            return 1
    if "02" not in wanted and {"03", "04"} & wanted:
        pairs = OUT_DATA / "_company_bank_cooc_pairs.parquet"
        if not pairs.exists():
            logger.error("缺 %s 且未选 02 — 无锚即无互验/替代聚合", pairs)
            logger.error("  修复: 先跑 `python company_listed_bank/run_pipeline.py --steps 02` 重建 pair 长表")
            return 1

    t_all = time.monotonic()
    pre_sha = _registry_sha() if ("01" in wanted and not args.dry_run) else None  # 01 重生前的锚, 收尾对比用
    step_stats: list[tuple[str, str, float]] = []  # (step_id, desc, 墙钟秒) — 仅收尾日志用途
    for step_id, script, desc in selected:
        cmd = [sys.executable, "-u", str(HERE / script)]
        logger.info("─" * 70)
        logger.info("%s %s", step_id, desc)
        if not args.dry_run:
            _log_step_context(step_id)
        logger.info("  $ %s", " ".join(cmd))
        if args.dry_run:
            continue
        # A6 修复 (2026-07-09 五入口诊断): 镜像 core/stage.py:239-255, 给子步子进程注入确定性+编码 env。
        # 裸跑无此保护 → 违反金标 HASHSEED=0(靠子脚本 sorted() 免疫故纵深防御) + GBK emoji 风险。
        # PYTHONHASHSEED 强制="0" 是复现锚非改锚(本轮 sha 已匹配 EXPECTED_REGISTRY_SHA256); setdefault 尊重用户覆盖。
        child_env = dict(os.environ)
        child_env.setdefault("PYTHONUNBUFFERED", "1")
        child_env.setdefault("PYTHONIOENCODING", "utf-8:replace")
        child_env.setdefault("PYTHONUTF8", "1")
        child_env.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
        child_env["PYTHONHASHSEED"] = "0"
        t0 = time.monotonic()
        # F12: stdout 继承 (实时终端), stderr 单管道经守护线程 forward 进 run_pipeline.log
        _proc = subprocess.Popen(cmd, cwd=str(REPO), env=child_env,
                                 stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
        _t = _spawn_stderr_forwarder(_proc, f"listed-step{step_id}-stderr")
        rc = _proc.wait()
        _t.join(timeout=10)
        dt = time.monotonic() - t0
        if rc != 0:
            logger.error("步骤 %s 失败 (exit=%d, 墙钟 %.4gs) — fail-loud 中断, 后续步骤未跑", step_id, rc, dt)
            logger.error("  排障: 看 company_listed_bank/logs/%s.log; 单步重跑 `python company_listed_bank/%s`",
                         Path(script).stem, script)
            if any(s == "01" for s, _, _ in step_stats):  # 01 已成功落盘 → 锚状态不得因中断而失声
                _log_registry_anchor_status(pre_sha, {s for s, _, _ in step_stats})
            return rc
        step_stats.append((step_id, desc, dt))
        _log_step_done(step_id, dt)

    if not args.dry_run:
        total = time.monotonic() - t_all
        logger.info("全部 %d 步完成 (总墙钟 %.4gs)", len(selected), total)
        _log_run_summary(step_stats, total)
        if "01" in wanted:
            _log_registry_anchor_status(pre_sha, {s for s, _, _ in step_stats})
        _log_references()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
