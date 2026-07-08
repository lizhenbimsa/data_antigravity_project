"""税调企业—银行共现面板流水线 orchestrator (COMPANY_TAX_BANK_COOC_PANEL_EXECUTION_PLAN v6).

按硬依赖顺序串跑三步 (子进程隔离, 任一步非零退出即中断, 镜像 run_pipeline_function.py 风格):
  01 WP0 注册表对账   → config/company_tax_bank_cooc_registry.yaml (加权引擎唯一 SSOT)
  02 WP1 主面板构建   → company_tax_bank/data/company_tax_bank_cooc_panel.{dta,parquet} + codebook + pair 长表
  03 WP5 双权源互验   → company_tax_bank/data/ 双替代权长表 + 双权面板 ×2 + 三权互验报告

三权 = 共现报道权 (02 主面板) + 城市网点权 (branch_city, 03) + 县域网点权 (branch_county, 03),
互为规格稳健性、不分主次 (禁混同一 over-identified Hansen J)。

日志: 本 orchestrator 与三步各写 company_tax_bank/logs/<stem>.log (格式/覆盖语义同主管道
core/logging.py::setup_logging); 数据产物统一落 company_tax_bank/data/ (不入库)。

用法 (从 news_process/ 目录, conda base python):
  python company_tax_bank/run_pipeline.py                 # 全链 01→02→03
  python company_tax_bank/run_pipeline.py --steps 02,03   # 从 02 起 (registry 已就绪时)
  python company_tax_bank/run_pipeline.py --dry-run       # 只打印将执行的命令

⚠ 重跑 01 会重生 registry → 哈希锚变 → 须 bump
  tests/test_company_tax_bank_cooc_registry.py::EXPECTED_TAX_REGISTRY_SHA256 并级联 02 (pair 指纹)
  → 03 (DV2 双向锁); 本 orchestrator 跑完含 01 的链后会打印该提醒。
独立派生数据流水线, 不注册 DAG (镜像 generate_company_tax_names.py 定位)。
与姊妹管线 company_listed_bank/ 完全隔离, 唯一交集 = 02/03 只读 import listed 02 加权引擎 (T-D10/T-D18)。
"""
from __future__ import annotations

import argparse
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

# 03 分支长表 (~千万行级) 的加权引擎内存预算默认值 (T-D13): 媒体权稀疏长表用引擎默认 60M 即可,
# 但 03 城/县网点长表 ~25–34M 行, 默认预算会把 chunk_eff 收缩到 2、触发内存吃紧 WARNING 且 groupby
# 轮次暴涨 (~945 轮)。500M cell (25M 行×20 列×8B≈4GB/帧) → chunk_eff→20、轮次降一个数量级。
_BRANCH_BUDGET_CELLS = 500_000_000

logger = logging.getLogger("run_pipeline")
if not logger.handlers:  # console 兜底; main() 实跑时由 setup_logging 接管
    _h = logging.StreamHandler(sys.stdout)
    _h.setFormatter(logging.Formatter("[pipeline] %(levelname)s %(message)s"))
    logger.addHandler(_h)
    logger.setLevel(logging.INFO)


def _init_stage_logging() -> None:
    """接入主管道日志基建 (core/logging.py::setup_logging): 写 company_tax_bank/logs/run_pipeline.log,
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

    2026-07-07 实弹 (listed 姊妹管线): 两个 orchestrator 相差 46 秒并发全链, 各持句柄按各自偏移交错
    覆写同一套日志 (PID 混写/时间戳倒流/行粘连) 与同一套 ~13GB 产物, 最终 branchw dta 留下 688MB
    半成品 (后启动实例在先启动实例收尾后被杀于写盘中途)。税调 03 双权面板同为 ~13GB dta、风险同构,
    本锁把该事故类别封死在入口。

    语义: 锁已存在 → 读持有者 PID 判存活 — 存活 → SystemExit(1) fail-loud (绝不静默排队);
    已死/不可读 → 视为陈旧锁 (上次异常退出残留), 清除后重试一次。返回持有的 fd, 由
    _release_single_instance_lock 在 main() 收尾 (含失败路径) 释放。
    ⚠ 本锁只护 orchestrator 入口; 绕过 orchestrator 直跑单步脚本仍无互斥, 并发纪律同样适用。"""
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    for attempt in (1, 2):
        try:
            fd = os.open(str(LOCK_FILE), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode("ascii"))
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
    except OSError:
        logger.warning("锁文件 %s 删除失败 (无害: 下次启动按陈旧锁清除)", LOCK_FILE)


STEPS: list[tuple[str, str, str]] = [
    ("01", "01_build_company_tax_bank_cooc_registry.py",
     "WP0 注册表对账 → config/company_tax_bank_cooc_registry.yaml"),
    ("02", "02_build_company_tax_bank_cooc_panel.py",
     "WP1 主面板 + pair 长表 + codebook"),
    ("03", "03_build_company_tax_bank_weight_validation.py",
     "WP5 双权源 (城市/县域网点) + 双替代权面板 (与 02 主面板并称三权) + 互验报告"),
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
        yield (REPO / "config" / "company_tax_bank_cooc_registry.yaml",
               "注册表 yaml (加权引擎唯一 SSOT; 例外入库, 属配置而非数据结果)")
    elif step_id == "02":
        yield (OUT_DATA / "company_tax_bank_cooc_panel.dta",
               "主面板 dta (Stata format 118; 20 固定列 [含 usci] + 加权列; 消费者 = Stata 回归 + 03 骨架)")
        yield (OUT_DATA / "company_tax_bank_cooc_panel.parquet",
               "主面板 parquet 伴生 (未缩写全名, 供 Python 侧审计)")
        yield (OUT_DATA / "company_tax_bank_cooc_panel_codebook.md",
               "codebook (与 news_process 主项目 codebook 互不交叉)")
        yield (OUT_DATA / "_company_tax_bank_cooc_pairs.parquet",
               "pair 长表 10 列 (被删加权列唯一重构载体; 03 互验的锚, 缺则 03 SystemExit)")
    elif step_id == "03":
        for p in sorted(OUT_DATA.glob("_company_tax_bank_altweights_branch_*.parquet")):
            yield p, "替代权长表 (统一 schema company/bank/year/w; branch_city/branch_county 双 scheme 无稳健臂)"
        for p in sorted(OUT_DATA.glob("company_tax_bank_branch_*w_panel.dta")):
            yield p, "替代权面板 dta (与主面板同引擎同列名, scheme 身份由文件名承载)"
        for p in sorted(OUT_DATA.glob("company_tax_bank_branch_*w_panel.parquet")):
            yield p, "替代权面板 parquet 伴生"
        yield (OUT_DATA / "_company_tax_bank_weight_validation.md",
               "三权互验报告 (DV5 五件套 + 顶刊披露包 + 未映射审计附录)")


def _log_banner(selected_ids: list[str]) -> None:
    """运行头 banner: 流水线定位/上下游/复现命令/关键 config/环境版本 — 复现材料级最小充分信息。"""
    logger.info("=" * 70)
    logger.info("税调企业—银行共现面板流水线 orchestrator (COMPANY_TAX_BANK_COOC_PANEL_EXECUTION_PLAN v6)")
    logger.info("定位: 税调企业×年 银企共现媒体报道面板三步生产链 (registry → 主面板 → 双权源互验; 三权稳健)")
    logger.info("  · 规模锚: 850,649 行 = 44,771 家税调企业 × 19 年 (2007–2025) 全骨架, 含零覆盖行")
    logger.info("  · merge 键: usci × year (18 位统一社会信用代码, 全填全唯一; company_tax_name×year 等价备用键)")
    logger.info("  · 上游(只读): data/processed/ 五 parquet (40/51/27/16/21_full, 主管道产物)")
    logger.info("  · 上游(权源): config/银行业金融机构基本信息表.dta (城市/县域两层级网点权; 恒不入库)")
    logger.info("               + config/company_tax_names.yaml (税调名单 SSOT v1.0.0, 44,771 家; 已入库)")
    logger.info("  · 下游消费者: Stata 税调企业回归 (三权面板互为规格稳健性臂) + gate 测试四件 (pytest 收集 15+59+45+6=125 项)")
    logger.info("  · 关键 config 键: config/company_tax_bank_cooc_registry.yaml (加权引擎唯一 SSOT, 01 产出)")
    logger.info("  · own-bank 映射: registry 顶层 bank_company_map (D4, 280 家银行系税调企业 → 自家银行剔除; 值可为空列表)")
    logger.info("复现命令 (从 news_process/ 目录, conda base python):")
    logger.info("  python company_tax_bank/run_pipeline.py                 # 全链 01→02→03")
    logger.info("  python company_tax_bank/run_pipeline.py --steps 02,03   # registry 已就绪时从 02 起")
    logger.info("  python company_tax_bank/run_pipeline.py --dry-run       # 只打印将执行的命令")
    logger.info("本次选定步骤: %s (顺序恒按 01→02→03 硬依赖执行, 传入序不生效)", ", ".join(selected_ids))
    logger.info("环境 (importlib.metadata, 仅日志用途): Python %s", sys.version.split()[0])
    logger.info("  pandas %s | numpy %s | pyarrow %s | pyreadstat %s",
                _pkg_version("pandas"), _pkg_version("numpy"),
                _pkg_version("pyarrow"), _pkg_version("pyreadstat"))
    logger.info("  pyahocorasick %s | PyYAML %s | psutil %s",
                _pkg_version("pyahocorasick"), _pkg_version("PyYAML"), _pkg_version("psutil"))
    rss = _rss_mb()
    if rss is not None:
        logger.info("  启动时 orchestrator RSS %.4g MB (三步各为独立子进程, 峰值内存见各步骤自身日志)", rss)
    logger.info("=" * 70)


def _log_step_context(step_id: str) -> None:
    """步骤开跑前的输入/输出角色与缺失语义说明 (静态口径 + 廉价存在性读数), 仅日志用途。"""
    if step_id == "01":
        logger.info("  输入: 五上游 parquet 全列名 (data/processed/, 只读) + 裁剪负清单")
        logger.info("        COMPANY_BANK_COOC_PANEL_CUT_LIST_v23.txt + 税调名单 SSOT (company_tax_names.yaml) + 银行清单")
        logger.info("  职责: D15/D11 全划分对账 (残差非零 → SystemExit) + D16 短名 (≤32 全局唯一) + sha256 哈希锚")
        logger.info("  输出: config/company_tax_bank_cooc_registry.yaml — 02/03 加权引擎与 gate 测试的唯一 SSOT")
    elif step_id == "02":
        reg = REPO / "config" / "company_tax_bank_cooc_registry.yaml"
        logger.info("  输入: registry yaml (启动校验哈希锚, 当前%s; 缺则 02 拒跑) + 五上游 parquet",
                    "存在" if reg.exists() else "缺失")
        logger.info("  输出: 主面板 dta/parquet (850,649 行, 20 固定列 [含 usci] + 加权列) + codebook + pair 长表 10 列")
        logger.info("  缺失语义: rel_n_banks=0 的企业-年 cw/ce 置 NaN (非 0, 勿把无关系年当零暴露); rel_hhi∈(0,1]")
        logger.info("  满骨架: 44,771 家税调名单快照无逐年存续 → 99%+ 全零行属\"无共现企业-年\", 样本裁剪归分析端 (codebook 给口径)")
        logger.info("  pair 长表 = 被删加权列的唯一重构载体, 亦是 03 互验的锚 (跨年去重键禁含 year)")
    elif step_id == "03":
        pairs = OUT_DATA / "_company_tax_bank_cooc_pairs.parquet"
        logger.info("  输入: registry (DV2 常量双向锁) + 02 pair 长表 (当前%s; 缺则 SystemExit: 无锚即无互验)",
                    "存在" if pairs.exists() else "缺失")
        logger.info("        + config/银行业金融机构基本信息表.dta 权源 (603,907 行; 城市/县域两层级网点)")
        logger.info("  权源 2 scheme: branch_city (城市网点) / branch_county (县域网点; 银行名 canon 化 = DV2 判定序)")
        logger.info("  输出: 双替代权长表 ×2 + 双权面板 dta/parquet ×2 + 三权互验报告 md (均不入库)")
        logger.info("  互验口径: 与主面板同引擎同列名 (cw_/ce_{基名}_{track}), scheme 身份由文件名承载 (D18 单引擎)")
        logger.info("  三权 = 共现报道权 (02) + 城市网点权 + 县域网点权, 互为规格稳健性、不分主次 (禁混同一 Hansen J)")


def _log_step_done(step_id: str, dt: float) -> None:
    """步骤成功后的产物清点 (体量/角色) + 吞吐率 — 只消费已算出的墙钟与廉价 stat 读数。"""
    rss = _rss_mb()
    if rss is not None:
        logger.info("步骤 %s 完成: 墙钟 %.4gs | orchestrator RSS %.4g MB (子进程已退出, 其峰值见该步骤日志)",
                    step_id, dt, rss)
    else:
        logger.info("步骤 %s 完成: 墙钟 %.4gs", step_id, dt)
    total_mb = 0.0
    for p, desc in _iter_artifacts(step_id):
        mb = _size_mb(p)
        if mb is None:
            logger.warning("  产物缺失: %s — %s", p.name, desc)
        else:
            total_mb += mb
            logger.info("  产物 %-48s %.4g MB — %s", p.name, mb, desc)
    if total_mb > 0 and dt > 0:
        logger.info("  本步落盘合计 %.4g MB, 吞吐 %.4g MB/s (墙钟口径, 含计算+IO; 体量为盘上现值)",
                    total_mb, total_mb / dt)
    if step_id == "02" and dt > 0:
        logger.info("  主面板文档口径 850,649 行 → 构建吞吐 %.4g 行/s (墙钟口径)", 850649.0 / dt)


def _log_run_summary(step_stats: list[tuple[str, str, float]], total: float) -> None:
    """收尾统计报告 + 【结果分析】逐条经济学/方法学判读 — 仅消费已算出的墙钟, 无新增计算。"""
    ran = {s for s, _, _ in step_stats}
    logger.info("=" * 70)
    logger.info("【统计报告 · 墙钟分解】总墙钟 %.4gs ≈ %.4g 分钟", total, total / 60.0)
    for step_id, desc, dt in step_stats:
        share = 100.0 * dt / total if total > 0 else 0.0
        logger.info("  步骤 %s: %.4gs (占 %.4g%%) — %s", step_id, dt, share, desc)
    logger.info("【结果分析 · 判读】")
    logger.info("  · 走到本节 = 三步 rc 全 0, 硬依赖链完整闭合: registry 哈希锚 → 主面板/pair 指纹 →")
    logger.info("    DV2 双向锁; 任一环节断裂会 fail-loud 中断, 本节根本不会打印")
    if "01" in ran:
        logger.info("  · 01 判读: 秒级墙钟为健康区间; 失败/骤慢通常 = 上游 parquet 列名漂移或负清单不同步")
        logger.info("    (全划分残差非零即 SystemExit 是防静默漏列的设计 — 翻红应查列名对账而非盲目重试)")
    if "02" in ran:
        logger.info("  · 02 判读: 分钟级墙钟为健康区间; 面板保留全骨架 (零共现企业-年不删行, 缺权重记 NaN")
        logger.info("    而非 0), 避免以媒体覆盖存活为条件的幸存者/选择偏差; dta ≈13GB 系 Stata format 118")
        logger.info("    定长字符串 (含 usci str18 + 中文企业名) 所致, dta ≫ parquet 属格式预期而非数据膨胀异常")
    if "03" in ran:
        logger.info("  · 03 判读: 占总墙钟约大头为预期形态 (2 权源 × 全套加权面板 × dta+parquet 双格式落盘,")
        logger.info("    双 13GB dta IO-bound); 占比骤降多半 = 某 scheme 长表全缺被跳过, 须查 03 日志的")
        logger.info("    逐权逐年覆盖表; 单银行企业-年 rel_hhi 恒 1 属定义使然, 非集中度异常")
        logger.info("  · 互验判读: 富集度须双基准并报 (计划实弹: 均匀基准会夸大收敛效度, 须并报边际保持置换基准) —")
        logger.info("    城/县两网点权 + 共现报道权为规格稳健性并排臂, 按 specification-curve 口径逐权独立报告,")
        logger.info("    不混作同一回归的多工具 (城/县两权是同一权源的粒度梯子, 论文端预声明 primary 层级)")
    logger.info("  · 生产 T=18 预期差异: 当前上游 21_full 为 dev 语料口径, 覆盖/富集度实测以互验报告为准;")
    logger.info("    生产重跑后 §6 级联义务生效 (哈希锚 bump → 02 pair 指纹 → 03 双向锁), 墙钟与 IO 同步放大")


def _log_references() -> None:
    """📖 方法论依据 — APA 引文逐字取自审定引文池 (仅整理换行); 白话注解落到本脚本的具体设计决策。"""
    logger.info("-" * 70)
    logger.info("📖 方法论依据")
    logger.info("[数据工程与复现]")
    logger.info("  1. Menkveld, A. J., Dreber, A., Holzmeister, F., Huber, J., Johannesson, M.,")
    logger.info("     Kirchler, M., Razen, M., Weitzel, U., … [百人合著] (2024). Nonstandard errors.")
    logger.info("     The Journal of Finance, 79(3), 2339–2390. https://doi.org/10.1111/jofi.13337")
    logger.info("     → 白话: 同一数据同一假设, 不同团队跑出的结果会系统性发散 (\"非标准误差\")。本 orchestrator")
    logger.info("       把 01→02→03 固化为唯一执行序 (传入序不生效) 并逐条记录实际命令行, 就是把\"跑法自由度\"")
    logger.info("       这一误差源压到零。")
    logger.info("  2. Brodeur, A., Mikola, D., Cook, N., … [百人合著] (2026). Reproducibility and")
    logger.info("     robustness of economics and political science research. Nature, 652(8108),")
    logger.info("     151–156. https://doi.org/10.1038/s41586-026-10251-x")
    logger.info("     → 白话: 大样本复现研究表明复现成败高度取决于材料完备度。本日志记录环境库版本、逐步产物")
    logger.info("       清单/体量/角色与失败排障入口, 即为审稿人与 data editor 准备的最小充分复现信息。")
    logger.info("  3. Chen, A. Y., & Zimmermann, T. (2022). Open source cross-sectional asset pricing.")
    logger.info("     Critical Finance Review, 11(2), 207–264. https://doi.org/10.1561/104.00000112")
    logger.info("     → 白话: 把面板生产做成可一键重建的代码本身就是研究基础设施。本链以 registry 唯一 SSOT +")
    logger.info("       02/03 单引擎双函数复用 (禁第二份实现) 实现同等的\"代码即口径\"可审计性。")
    logger.info("[面板构建与样本选择]")
    logger.info("  4. Brown, S. J., Goetzmann, W., Ibbotson, R. G., & Ross, S. A. (1992). Survivorship")
    logger.info("     bias in performance studies. The Review of Financial Studies, 5(4), 553–580.")
    logger.info("     https://doi.org/10.1093/rfs/5.4.553")
    logger.info("     → 白话: 只留\"活下来/被报道\"的样本会系统性高估效应。步骤 02 保留 44,771 家税调企业 × 19 年")
    logger.info("       全骨架 (零共现企业-年不删行, 缺权重记 NaN 而非 0), 正是为切断这条选择偏差通道。")
    logger.info("[识别与多口径稳健]")
    logger.info("  5. Simonsohn, U., Simmons, J. P., & Nelson, L. D. (2020). Specification curve analysis.")
    logger.info("     Nature Human Behaviour, 4(11), 1208–1214. https://doi.org/10.1038/s41562-020-0912-z")
    logger.info("     → 白话: 把合理规格全枚举再看结论分布, 而非只报一条。步骤 03 用共现报道 + 城市/县域两层级")
    logger.info("       网点 3 个独立权重对同一共现构念批量生产平行面板, 就是把\"权重矩阵怎么选\"这条研究者")
    logger.info("       自由度摊开成规格曲线供互验 (城/县为同一权源的粒度梯子)。")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="税调企业—银行共现面板流水线: 01 registry → 02 panel → 03 weights (硬依赖顺序)")
    ap.add_argument("--steps", default=",".join(STEP_IDS),
                    help="逗号分隔步骤子集 (默认全链); 顺序恒按 01→02→03, 传入序不生效")
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
        _init_stage_logging()
    try:
        return _run(args, wanted, selected)
    finally:
        if lock_fd is not None:
            _release_single_instance_lock(lock_fd)


def _registry_sha() -> str | None:
    """读盘上 registry meta.registry_sha256 (yaml.safe_load, 与 02/03/gate 测试同一解析路径,
    禁第二份实现); 缺文件/缺键/解析失败 → None (fail-soft, 本函数仅服务收尾判读日志)。"""
    reg = REPO / "config" / "company_tax_bank_cooc_registry.yaml"
    try:
        import yaml
        with open(reg, encoding="utf-8") as fh:
            sha = yaml.safe_load(fh).get("meta", {}).get("registry_sha256")
        return sha if isinstance(sha, str) and len(sha) == 64 else None
    except Exception:
        return None


def _expected_registry_anchor() -> str | None:
    """读 gate 测试锚 EXPECTED_TAX_REGISTRY_SHA256 (正则取常量字面量); 不可读 → None。
    ⚠ 常量名刻意与 listed 的 EXPECTED_REGISTRY_SHA256 不同名 — 正则以行首+全名匹配, 免误锚姊妹管线。"""
    test_file = REPO / "tests" / "test_company_tax_bank_cooc_registry.py"
    try:
        m = re.search(r'^EXPECTED_TAX_REGISTRY_SHA256\s*=\s*["\']([0-9a-f]{64})["\']',
                      test_file.read_text(encoding="utf-8"), re.M)
        return m.group(1) if m else None
    except Exception:
        return None


def _log_registry_anchor_status(pre_sha: str | None) -> None:
    """01 重生 registry 后的哈希锚判读: 盘上锚 vs 跑前快照 vs gate 测试锚 三方对比 (证据驱动;
    含步骤失败提前退出路径 — 只要 01 已成功落盘, 锚状态就必须被披露)。"""
    post_sha = _registry_sha()
    if post_sha is None:
        logger.warning("本次重生了 registry, 但 meta.registry_sha256 读取失败 — 请人工核对 "
                       "config/company_tax_bank_cooc_registry.yaml 与测试锚 (勿在未核对前 bump)")
        return
    expected = _expected_registry_anchor()
    changed = pre_sha is None or post_sha != pre_sha
    if expected is not None and post_sha != expected:
        logger.warning("本次重生了 registry: 盘上锚 %s… ≠ 测试锚 %s… — 须 bump "
                       "tests/test_company_tax_bank_cooc_registry.py::EXPECTED_TAX_REGISTRY_SHA256 %s",
                       post_sha[:16], expected[:16],
                       "并确认 02→03 已级联 (本链若含 02/03 则已级联)" if changed
                       else "并核查盘上 02/03 产物是否与该锚同代 (本次运行未改锚, 属既有欠账)")
        return
    anchor_note = ", 与测试锚一致" if expected is not None else " (测试锚不可读, 未对比)"
    if not changed:
        logger.info("本次重生了 registry: 哈希锚未变 (%s…%s) — 无需 bump 测试锚, 02/03 免级联义务"
                    " (锚未含 meta 输入指纹, registry 文件字节可有 meta 级漂移, 以 git diff 为准)",
                    post_sha[:16], anchor_note)
    else:
        logger.warning("本次重生了 registry 且哈希锚变更 (%s… → %s…%s): 须确认 02→03 已级联 "
                       "(本链若含 02/03 则已级联)%s",
                       (pre_sha or "无旧值")[:16], post_sha[:16], anchor_note,
                       "" if expected is not None else "; 并核对是否须 bump "
                       "tests/test_company_tax_bank_cooc_registry.py::EXPECTED_TAX_REGISTRY_SHA256")


def _run(args: argparse.Namespace, wanted: set[str], selected: list[tuple[str, str, str]]) -> int:
    """main() 的执行主体 (锁获取之后); 拆出以保证任何 return/异常路径都经 finally 释放锁。"""
    if not args.dry_run:
        _log_banner([s[0] for s in selected])

    # 跳步前置自检 (fail-loud 提前于子进程闸, 报错更可读; 02/03 自身仍有权威闸)
    if "01" not in wanted and {"02", "03"} & wanted:
        reg = REPO / "config" / "company_tax_bank_cooc_registry.yaml"
        if not reg.exists():
            logger.error("缺 %s 且未选 01 — registry 是 02/03 的唯一 SSOT", reg)
            logger.error("  修复: 先跑 `python company_tax_bank/run_pipeline.py --steps 01` 或改跑全链")
            return 1
    if "02" not in wanted and "03" in wanted:
        pairs = OUT_DATA / "_company_tax_bank_cooc_pairs.parquet"
        if not pairs.exists():
            logger.error("缺 %s 且未选 02 — 无锚即无互验", pairs)
            logger.error("  修复: 先跑 `python company_tax_bank/run_pipeline.py --steps 02` 重建 pair 长表")
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
        # T-D13: 03 分支长表 ~千万行级 → 子进程注入加权引擎内存预算默认值 (用户已 export 则不覆盖)
        child_env: dict[str, str] | None = None
        if step_id == "03":
            child_env = dict(os.environ)
            if "NEWS_PROCESS_COOC_BUDGET_CELLS" not in child_env:
                child_env["NEWS_PROCESS_COOC_BUDGET_CELLS"] = str(_BRANCH_BUDGET_CELLS)
                logger.info("  env 注入: NEWS_PROCESS_COOC_BUDGET_CELLS=%s (T-D13: 城/县网点长表 ~25–34M 行, "
                            "防 chunk 收缩至 chunk_eff=2)", _BRANCH_BUDGET_CELLS)
            else:
                logger.info("  env: NEWS_PROCESS_COOC_BUDGET_CELLS 已由环境提供 (%s), 不覆盖默认 %s",
                            child_env["NEWS_PROCESS_COOC_BUDGET_CELLS"], _BRANCH_BUDGET_CELLS)
        logger.info("  $ %s", " ".join(cmd))
        if args.dry_run:
            continue
        t0 = time.monotonic()
        rc = subprocess.run(cmd, cwd=str(REPO), env=child_env).returncode
        dt = time.monotonic() - t0
        if rc != 0:
            logger.error("步骤 %s 失败 (exit=%d, 墙钟 %.4gs) — fail-loud 中断, 后续步骤未跑", step_id, rc, dt)
            logger.error("  排障: 看 company_tax_bank/logs/%s.log; 单步重跑 `python company_tax_bank/%s`",
                         Path(script).stem, script)
            if any(s == "01" for s, _, _ in step_stats):  # 01 已成功落盘 → 锚状态不得因中断而失声
                _log_registry_anchor_status(pre_sha)
            return rc
        step_stats.append((step_id, desc, dt))
        _log_step_done(step_id, dt)

    if not args.dry_run:
        total = time.monotonic() - t_all
        logger.info("全部 %d 步完成 (总墙钟 %.4gs)", len(selected), total)
        _log_run_summary(step_stats, total)
        if "01" in wanted:
            _log_registry_anchor_status(pre_sha)
        _log_references()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
