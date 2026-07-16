"""news_process.core.stage — 子进程隔离的阶段执行器 + (未来) Stage 基类。

由历史 ``utils/helpers.py:666-752`` 拆分而来。

保留的公开 API: ``run_stage``。

Phase 1 范围: 本文件仅承载 ``run_stage`` (子进程执行器)。
Phase 3 将在此处增加 ``Stage`` 运行时抽象基类 + ``@stage`` 装饰器,
与 ``core/dag.py`` 中声明的 *声明式* ``StageSpec`` 数据类分离。
两个名字 ``Stage`` (运行时基类) 与 ``StageSpec`` (声明式记录) 刻意不同,
以避免命名冲突。

Phase 9 (plan c4): ``run_stage`` 由 ``subprocess.run(capture_output=True)``
重写为 ``subprocess.Popen`` + 双 reader 线程, 解决三个长期痛点:
  1. 内存爆涨 — 旧实现把子进程整段 stdout/stderr 累积到父进程内存,
     LLM 阶段 (stage 21, timeout 7200s) 与 panel 阶段 (stage 45)
     长输出会导致父进程 RSS 暴增。
  2. 无实时进度 — 旧实现等子进程 EOF 才一次性返回, 用户跑 7200s 阶段
     在父端完全看不到进度。
  3. 失败信息截断 — 旧实现仅保留末 30 行 stderr, 关键 traceback 上文
     与 stdout 全部丢失。

新实现以行为单位通过两个后台线程实时把子进程 stdout/stderr 转发到父 logger,
同时用环形缓冲 (deque(maxlen=N)) 累积末尾 N 行用于诊断, 既保证可观测性
又封顶内存占用。
"""

from __future__ import annotations

import logging
import os
import re
import subprocess
import sys
import threading
import time
from collections import deque
from typing import IO, Deque

try:
    import psutil
except ImportError:  # pragma: no cover - psutil 是运行时必装依赖, 此分支仅防御
    psutil = None

from .logging import get_run_id, log_memory_usage, sig4

# 子进程 stdout/stderr 尾部累积上限 (行数); 防止任意大日志撑爆父进程。
# 2026-06-12 由 1 万行上调为 10 万行 (用户决策): 失败诊断时保留更长尾部。
# 此环形缓冲只是父进程内存里的诊断快照 — 完整(超长)日志始终经 reader 线程
# 实时透传到父 logger, 落盘于 logs/<stage>.log (每次运行覆盖, 只留最新), 不受此上限截断。
_TAIL_BUFFER_MAXLEN = 100000

# ANSI / VT100 转义序列 (CSI 颜色/样式/光标等 + 双字 Fe 转义)。orchestrator 捕获
# 子进程 stdout/stderr 后会把每行原样转发进父 logger → 落入 run_pipeline_*.log。
# 子进程被 PIPE 捕获 (非 TTY) 时本不应再着色 (见 core/logging.py 的 TTY 判定), 但
# 此处再做一道**防御性剥离**: 任何来源 (第三方库直接写 stdout、tqdm、外部工具) 的
# 转义码都在转发前剥掉, 保证 orchestrator 落盘日志恒为纯文本 (LOG-COLOR 2026-06-25)。
_ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

# ── 经核验参考文献 (VERIFIED_REFERENCES 注册表, 逐字照抄 APA-7 + DOI; 仅日志用) ──
# 白话: 本执行器对每个 stage 子进程强制 ``env["PYTHONHASHSEED"]="0"`` (见下方注入逻辑),
# 让带随机性的链路 (stage 22 jieba+frozenset 边界 token / golden snapshot 复现) 可逐位
# 重放 —— 这正是 Sandve 等 (2013) "可复现计算研究十诫" 之 Rule 6「凡含随机性的分析须记录
# 其底层随机种子」的直接落地。emit 进运行期日志, 让 .log 自证这一方法学锚点 (非仅留注释)。
_STAGE_REFERENCES = {
    "sandve_reproducible_seed": (
        "Sandve, G. K., Nekrutenko, A., Taylor, J., & Hovig, E. (2013). Ten "
        "simple rules for reproducible computational research. PLoS "
        "Computational Biology, 9(10), e1003285. "
        "https://doi.org/10.1371/journal.pcbi.1003285"
    ),
}


def _stage_popen_isolation_kwargs() -> dict[str, object]:
    """返回隔离控制台信号的平台特定 Popen kwargs (Windows 新进程组 / Unix 新会话)。"""
    if os.name == "nt":
        return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}


def _reader_thread(stream: IO[str],
                   logger: logging.Logger,
                   prefix: str,
                   accumulator: Deque[str],
                   log_level: int = logging.INFO) -> None:
    """逐行读取 ``stream`` → 转发到 ``logger`` + 累积到 ``accumulator``.

    在子进程关闭流 (EOF) 时自然退出。线程被外层标记为 daemon, 父进程退出时
    不会因此挂起。``logging.Logger`` 自身线程安全 (内置 RLock), 因此双 reader
    线程可同时调用同一 logger 而无需额外锁。
    """
    try:
        for line in iter(stream.readline, ''):
            # 去掉行末换行 / 回车; 保留行内空白以维持原始可读性
            line = line.rstrip('\r\n')
            # 防御性剥离 ANSI 转义码: 子进程非 TTY 时本不该着色, 但任何残留的转义
            # 序列 (第三方库直写 stdout 等) 都不得随转发落入 run_pipeline_*.log。
            line = _ANSI_ESCAPE_RE.sub('', line)
            logger.log(log_level, f"  {prefix} {line}")
            accumulator.append(line)
    except Exception as e:  # pragma: no cover — 防御性兜底
        logger.warning(f"  reader thread ({prefix}) 异常: {e}")
    finally:
        try:
            stream.close()
        except Exception:
            pass


def _terminate_process_tree(proc: subprocess.Popen,
                            logger: logging.Logger,
                            reason: str,
                            grace_seconds: float = 5.0) -> None:
    """尽力而为地终止阶段子进程及其全部后代进程。

    刻意不发送控制台控制事件 (Ctrl 信号): Windows 上 Intel Fortran 运行时
    直接收到 Ctrl+C 时会打印 ``forrtl: error (200)``, 因此由 orchestrator
    在捕获用户中断后通过进程终止 (terminate/kill) 独占接管关停流程。
    """
    if proc.poll() is not None:
        return

    logger.warning(f"  正在终止子进程 PID={proc.pid}（{reason}）...")

    if psutil is not None:
        try:
            parent = psutil.Process(proc.pid)
            processes = parent.children(recursive=True) + [parent]
            for process in processes:
                try:
                    process.terminate()
                except psutil.NoSuchProcess:
                    pass
                except psutil.Error as exc:
                    logger.debug(f"  终止 PID={process.pid} 失败: {exc}")

            _, alive = psutil.wait_procs(processes, timeout=grace_seconds)
            if alive:
                logger.warning(
                    f"  {len(alive):,d} 个子进程未在 {sig4(grace_seconds)}s 内退出，强制结束..."
                )
                for process in alive:
                    try:
                        process.kill()
                    except psutil.NoSuchProcess:
                        pass
                    except psutil.Error as exc:
                        logger.debug(f"  强制结束 PID={process.pid} 失败: {exc}")
                psutil.wait_procs(alive, timeout=2)
        except psutil.NoSuchProcess:
            return
        except psutil.Error as exc:
            logger.debug(f"  枚举子进程树失败，将回退到 Popen 终止: {exc}")

    if proc.poll() is None:
        try:
            proc.terminate()
            proc.wait(timeout=grace_seconds)
        except subprocess.TimeoutExpired:
            try:
                proc.kill()
                proc.wait(timeout=2)
            except Exception as exc:
                logger.warning(f"  子进程 PID={proc.pid} 强制结束失败: {exc}")
        except Exception as exc:
            logger.debug(f"  Popen 终止子进程失败: {exc}")


def run_stage(stage_script: str, stage_name: str, logger,
              base_dir: str | None = None,
              timeout: int = 3600) -> tuple[bool, float]:
    """以隔离的子进程方式运行单个流水线阶段脚本.

    Args:
        stage_script: 文件名 (例如 ``"00_preprocessing.py"``)。
        stage_name:   日志中显示的人类可读阶段名。
        logger:       父进程 logger。
        base_dir:     阶段脚本所在目录; 默认为本文件所属包的父目录
                      (即项目根)。
        timeout:      子进程硬超时, 单位为秒。

    Returns:
        (success: bool, elapsed_seconds: float)

    子进程从父进程继承 ``NEWS_PROCESS_RUN_ID`` (以及其他全部 env 变量),
    使得每次运行的日志目录自动传播。

    实现说明 (plan c4):
    子进程 stdout/stderr 由两个 daemon reader 线程逐行抽取 → 实时转发到父 logger,
    同时累积末尾 ``_TAIL_BUFFER_MAXLEN`` 行供失败诊断。timeout 路径下用
    ``_terminate_process_tree()`` (best-effort 进程树终止: terminate() 后 kill()
    兜底) 杀掉子进程及其衍生的 joblib/ProcessPool 工作进程, reader 线程在管道
    关闭后自然退出 (audit S7 修复 2026-05-30, 替代历史的裸 ``proc.kill()``)。
    """
    if base_dir is None:
        # core/stage.py -> core/ -> news_process/  (上溯一层到项目根)
        base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

    script_path = os.path.join(base_dir, stage_script)

    if not os.path.exists(script_path):
        logger.error(f"阶段脚本未找到: {script_path}")
        return False, 0.0

    logger.info(f"{'─'*60}")
    logger.info(
        f"▶ 开始执行: {stage_name} ({stage_script}) "
        f"| 子进程隔离 (PID 待分配, timeout={timeout:,d}s, 父PID={os.getpid()})"
    )
    logger.info(f"{'─'*60}")
    # LOG-ENRICH round 8 (io_provenance): 代码出处 — 把第 ~188 行解析出的**绝对**脚本路径
    # 与其磁盘字节数 surface 到成功路径起始横幅 (此前该绝对路径仅在 not-found 错误分支才打印)。
    # 审稿人复现一次 run 时想精确知道每个 stage 实际执行的是磁盘上哪个文件 / 多大, 而非仅看
    # 横幅里裸的 shim 文件名。getsize 整段包在 try/except 内, 结果只喂 logger 旋即丢弃 (绝不
    # 下游复用), 严格 log-only / golden-safe; 字节整数 → :,d, KiB → sig4 (四位有效数字)。
    try:
        _script_bytes = os.path.getsize(script_path)
        logger.info(
            f"  ├─ 代码出处: {script_path} "
            f"({_script_bytes:,d} B / {sig4(_script_bytes / 1024)} KiB)"
        )
    except OSError as _exc:  # pragma: no cover — 防御性; script_path 上方已做 exists 校验
        logger.debug(f"  代码出处 getsize 失败 (不影响执行): {_exc}")
    log_memory_usage(logger, f"阶段 {stage_name} 开始前")

    # 显式传播 run_id (防御性写法 — Popen 默认已继承 env,
    # 但此处显式物化, 便于日志可读性)。
    env = os.environ.copy()
    run_id = get_run_id()
    if run_id:
        env["NEWS_PROCESS_RUN_ID"] = run_id

    # plan c4 后续改进: 子进程 stdout/stderr 完全不缓冲, 让父端 reader 线程
    # 不必等 Windows pipe chunk 满才看到行 (即使子进程 print 不主动 flush 也立即透传)。
    # 副作用: 子进程 stdio 性能轻微下降, 在 IO 远大于 stdio 的 ETL 中可忽略。
    env.setdefault("PYTHONUNBUFFERED", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8:replace")
    env.setdefault("PYTHONUTF8", "1")
    # OpenMP 双运行时防御 (OMP Error #15): conda base MKL 的 libiomp5md.dll 与
    # pip torch 自带的 libiomp5md.dll 在同一 stage 子进程同时初始化会中止.
    # 在子进程 spawn 前注入 env (比 news_process/__init__ 的 in-process setdefault
    # 更早, 早于子进程任何 import), 与既有 canonical SOP 一致; setdefault 不覆盖外部值.
    env.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
    # 确定性保障: 锁定 PYTHONHASHSEED 消除 stage 22 等 jieba+frozenset 链路上
    # 边界 token 数偶发非确定性 (实测最大漂移 < 0.001 in uncert_frac, 但触发
    # column hash 不一致, 影响回归测试 / golden snapshot 复现性)。
    # 确定性契约 (audit-fixes 2026-05-29): 强制 "0" 而非 setdefault — 后者会
    # 沿用父 shell 继承的非零值, 静默击穿 commit a4526731 "lock PYTHONHASHSEED"
    # 的本意 (CI/dev 若 export 了随机/非零 seed 会传播到每个 stage 子进程,
    # 重新引入 jieba+frozenset 边界 token 的非确定性). 此处子进程的 seed 不应
    # 由调用方意外覆盖, 故强制赋值.
    env["PYTHONHASHSEED"] = "0"
    # F13 (2026-07-10 五入口再验证): 本执行器**只**强制 HASHSEED=0, **不** setdefault BLAS 线程
    # (MKL/OPENBLAS/NUMEXPR/OMP_NUM_THREADS=1) —— 刻意不对称: HASHSEED 零性能代价; BLAS=1 对生产 T=19
    # 嵌入/网络重数值 stage 有真实性能代价 (逼成单线程 BLAS)。故 golden 逐位复现的 BLAS 钉死是 **shell 约定**
    # (经上方 os.environ.copy() 继承), 由 golden-regen SOP + M0 审批门覆盖 (见 CLAUDE.md 确定性铁律);
    # 勿在此盲加 setdefault BLAS=1 (会拖慢正常跑)。

    start_time = time.time()

    proc: subprocess.Popen | None = None
    try:
        proc = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env,
            bufsize=1,  # 行缓冲: 让 reader 线程能尽早拿到完整行
            # audit S7 修复 (2026-05-30): 接线进程组隔离 — 此前 _stage_popen_isolation_kwargs
            # 定义却从未被调用 (dead function), 导致 orchestrator 捕获 Ctrl+C 时控制台信号
            # 会直接传给子进程 (Windows Intel Fortran runtime 打 forrtl: error 200)。隔离后
            # orchestrator 经 _terminate_process_tree 主动关停, 独占 shutdown 控制。
            **_stage_popen_isolation_kwargs(),
        )
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"✗ {stage_name} 启动子进程失败: {e}")
        return False, elapsed

    # LOG-ENRICH round 7: 兑现上方启动横幅的 "PID 待分配" — 子进程真正 spawn 后回填
    # 实际 PID + 进程组隔离方式 + 确定性锚点, 让父端日志可直接定位/追踪/复现这一 stage
    # 子进程 (纯打印已算就的值, golden-safe; 计数皆整数, 无需 sig4)。
    _isolation_mode = (
        "CREATE_NEW_PROCESS_GROUP" if os.name == "nt" else "start_new_session"
    )
    logger.info(
        f"  ├─ 子进程已启动: PID={proc.pid} | 进程组隔离={_isolation_mode} "
        f"| PYTHONHASHSEED=0 (确定性已锁定) | KMP_DUPLICATE_LIB_OK=TRUE (OMP 双运行时防御)"
    )
    # LOG-ENRICH round 8 (runtime_params): 补全确定性 + 编码契约 echo — 上方横幅已 surface
    # PYTHONHASHSEED=0 与 KMP_DUPLICATE_LIB_OK, 但执行器还向每个 stage 子进程注入了
    # PYTHONUNBUFFERED / PYTHONIOENCODING / PYTHONUTF8 (见上方 env.setdefault)。一并 echo,
    # 让 .log 完整自证「本 stage 子进程在何种可复现 + 编码契约下运行」(纯读 env dict, 值未改,
    # golden-safe; 皆字符串, 无需 sig4)。
    logger.info(
        f"  ├─ 子进程编码/缓冲契约: PYTHONUNBUFFERED={env.get('PYTHONUNBUFFERED')} "
        f"| PYTHONIOENCODING={env.get('PYTHONIOENCODING')} "
        f"| PYTHONUTF8={env.get('PYTHONUTF8')}"
    )
    # LOG-ENRICH round 8 (📖 new_citation): 可复现计算研究锚点 — 上方对每个 stage 子进程强制
    # PYTHONHASHSEED=0 (消除 jieba+frozenset 边界 token 非确定性 / 锁定 golden snapshot 复现)
    # 正是 Sandve 等 (2013) Rule 6「凡含随机性的分析须记录随机种子」的直接落地; runtime emit
    # 让 .log 自证该方法学锚点 (纯 logger 字符串, golden-safe)。
    logger.info(f"  📖 {_STAGE_REFERENCES['sandve_reproducible_seed']}")

    stdout_tail: Deque[str] = deque(maxlen=_TAIL_BUFFER_MAXLEN)
    stderr_tail: Deque[str] = deque(maxlen=_TAIL_BUFFER_MAXLEN)

    assert proc.stdout is not None and proc.stderr is not None
    t_out = threading.Thread(
        target=_reader_thread,
        args=(proc.stdout, logger, '│', stdout_tail, logging.INFO),
        name=f"stage-{stage_script}-stdout",
        daemon=True,
    )
    t_err = threading.Thread(
        target=_reader_thread,
        args=(proc.stderr, logger, '│⚠', stderr_tail, logging.WARNING),
        name=f"stage-{stage_script}-stderr",
        daemon=True,
    )
    t_out.start()
    t_err.start()

    try:
        returncode = proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        logger.error(
            f"✗ {stage_name} 执行超时（超过 {timeout}s），强制终止子进程..."
        )
        # audit S7 修复: 用进程树终止替代裸 proc.kill() — 杀掉子进程及其衍生的
        # joblib/ProcessPool 工作进程 (stage 00/11/12), 避免孤儿进程残留。
        _terminate_process_tree(proc, logger, f"执行超时 > {timeout}s")
        # 等 reader 线程把已缓冲的剩余行排空 (管道关闭后自然 EOF)
        t_out.join(timeout=5)
        t_err.join(timeout=5)
        return False, elapsed
    except KeyboardInterrupt:
        # audit S7 复核闭环 (2026-05-30): 进程组隔离 (CREATE_NEW_PROCESS_GROUP /
        # start_new_session) 后, 子进程不再随控制台 Ctrl+C 终止 — orchestrator 必须
        # 显式终止进程树, 否则用户中断时子进程 (含 joblib/ProcessPool 工作进程) 成
        # 孤儿存活 (尤其 stage 21 7200s LLM 长跑被手动中断时)。KeyboardInterrupt 是
        # BaseException 子类, 不被下方 `except Exception` 捕获, 故必须独立分支。
        # 终止后 re-raise, 让上层 orchestrator 照常停止整个 pipeline (兑现隔离注释
        # 声称的 "orchestrator 经 _terminate_process_tree 主动关停" 闭环)。
        elapsed = time.time() - start_time
        logger.error(f"✗ {stage_name} 被用户中断 (Ctrl+C)，终止子进程树...")
        _terminate_process_tree(proc, logger, "用户中断 (Ctrl+C)")
        t_out.join(timeout=5)
        t_err.join(timeout=5)
        raise
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"✗ {stage_name} 等待子进程异常: {e}")
        # audit S7 修复: 同上, 进程树终止替代裸 proc.kill()。
        _terminate_process_tree(proc, logger, f"等待子进程异常: {e}")
        t_out.join(timeout=5)
        t_err.join(timeout=5)
        return False, elapsed

    # 子进程已正常退出: 等 reader 线程把剩余行排空再返回
    t_out.join(timeout=30)
    t_err.join(timeout=30)
    elapsed = time.time() - start_time

    if returncode == 0:
        logger.info(
            f"✓ {stage_name} 执行成功（耗时 {sig4(elapsed)}s, "
            f"stdout {len(stdout_tail):,d} 行 / stderr {len(stderr_tail):,d} 行已透传）"
        )
        # LOG-ENRICH round 7: 尾部环形缓冲是否饱和的诚实诊断 — deque(maxlen) 仅保留末
        # _TAIL_BUFFER_MAXLEN 行快照, 饱和时上文早期行已被挤出快照 (完整日志仍经 reader
        # 线程实时落盘 logs/<stage>.log, 不受此上限截断)。仅饱和时打印, 平时零噪声。
        if (len(stdout_tail) >= _TAIL_BUFFER_MAXLEN
                or len(stderr_tail) >= _TAIL_BUFFER_MAXLEN):
            logger.info(
                f"  └─ 尾部快照已饱和 (≥{_TAIL_BUFFER_MAXLEN:,d} 行/流): "
                f"父端诊断快照仅保留末 {_TAIL_BUFFER_MAXLEN:,d} 行; "
                f"完整日志见 logs/<stage>.log (实时透传, 不截断)"
            )
        # LOG-ENRICH round 7: 与开始前的 log_memory_usage 对称收口 — 给出本 stage 子进程
        # 退出后父进程 RSS, 便于读者从一对 "开始前/结束后" 估算该 stage 的内存足迹。
        log_memory_usage(logger, f"阶段 {stage_name} 结束后")
        return True, elapsed
    else:
        logger.error(
            f"✗ {stage_name} 执行失败（返回码 {returncode}, 耗时 {sig4(elapsed)}s）"
        )
        # 完整 stderr 已实时透传到父 logger (前缀 '│⚠'); 此处不再重复打印,
        # 仅给出 tail 提示便于在长日志中快速定位
        if stderr_tail:
            tail_n = min(30, len(stderr_tail))
            logger.error(f"诊断提示 — 末 {tail_n} 行 stderr:")
            for line in list(stderr_tail)[-tail_n:]:
                logger.error(f"  | {line}")
        return False, elapsed
