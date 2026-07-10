"""
news_process.core.locking — 管道并发运行保护（跨平台 + sidecar 信息文件）
====================================================================

提供文件锁机制，防止多个管道实例同时运行导致数据损坏。

跨平台支持：
    - Windows: msvcrt.locking
    - Unix/Linux: fcntl.flock

Plan P1-5 sidecar 方案 (2026-05-09):
    历史实现把 PID + 启动时间写入主锁文件 ``.pipeline.lock`` 内容. 当其它
    进程冲突时, ``_handle_lock_failure`` 用 ``open('r')`` 读它来诊断占用者.
    在 Windows 下, msvcrt.locking + 'w' 模式持有写句柄时, **同进程**再
    open('r') 读同一文件触发 ``PermissionError``, 让 ``lock_info`` 静默
    退化为 ``"未知"``. 6 个相关测试因此 ``@skipIf(sys.platform == 'win32')``,
    Windows 用户得到的诊断信息是 GBK 解码 garbled (``"δ֪"`` 等). 真正的
    生产场景 (跨进程冲突) 也部分受影响 — 父进程的 ``open('r')`` 在
    某些 Windows + Python 组合下也会被锁文件本身的 ACL 阻碍.

    Sidecar 方案: 把诊断信息写入**独立的** ``.pipeline.lock.info`` 文件,
    写完立即 ``close()`` 不持有句柄. 主锁文件 ``.pipeline.lock`` 仅承载
    OS 级文件锁, 其内容不再被读取. 任一进程任意时刻都能 ``open('r')``
    读 sidecar (它没有任何句柄持有), 跨平台一致. Sidecar 在 ``__exit__``
    时与主锁文件一起删除.

使用方法：
    from news_process.core.locking import PipelineLock

    with PipelineLock(logger):
        run_pipeline()
"""

import os
import sys
import time

from news_process.core.logging import sig4

# Sidecar 文件名后缀常量, 与主锁文件后缀对齐 (.pipeline.lock + .info)
_SIDECAR_SUFFIX = '.info'


class PipelineLock:
    """管道运行锁，防止并发执行。

    使用文件锁机制确保同一时间只有一个管道实例运行。
    跨平台支持：Windows使用msvcrt，Unix/Linux使用fcntl。

    Sidecar 信息文件 (Plan P1-5):
        在 ``self.lock_file_path + ".info"`` 处写入 PID + 启动时间;
        冲突时其它 PipelineLock 实例读取该 sidecar 而非主锁文件,
        避免 Windows 下 'w' 模式句柄阻塞同文件的 'r' 读取.
    """

    def __init__(self, logger, lock_dir: str = None,
                 console_only_on_reject: bool = False):
        """初始化管道锁。

        Args:
            logger: 日志对象
            lock_dir: 锁文件目录，默认为当前目录
            console_only_on_reject: 获锁失败 (被拒) 时把诊断走 ``sys.stderr`` 而非
                ``self.logger.error`` (审计 F4, 2026-07-10)。默认 False 保既有行为。
                主/验证编排器传 True: 防被拒并发实例经模块级 delayed-truncating file
                handler **首写截断**在跑实例的共享 .log。⚠ **禁**在 test_pipeline_lock.py
                的 PipelineLock 构造透传此 flag (会破其 reject→logger.error 断言)。
        """
        self.logger = logger
        self.console_only_on_reject = console_only_on_reject
        if lock_dir is None:
            lock_dir = os.path.dirname(os.path.abspath(__file__))
        self.lock_file_path = os.path.join(lock_dir, '.pipeline.lock')
        self.sidecar_path = self.lock_file_path + _SIDECAR_SUFFIX
        self.lock_file = None
        self.pid = os.getpid()
        self._locked = False
        # 持锁起始墙钟时间戳 (仅供 __exit__ 日志报告持锁时长; 不参与任何产物, golden-safe)
        self._t_acquired = None

    def __enter__(self):
        """获取锁。"""
        try:
            # 创建或打开锁文件 (仅承载 OS 级锁; 不再写入诊断信息)
            # F-13 (2026-05-16): encoding='utf-8' 显式锁定, 防 Windows cp936 默认
            self.lock_file = open(self.lock_file_path, 'w', encoding='utf-8')

            # 根据平台选择锁机制
            if sys.platform == 'win32':
                import msvcrt
                try:
                    msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                    self._locked = True
                except OSError:
                    self._handle_lock_failure()
            else:
                import fcntl
                try:
                    fcntl.flock(self.lock_file.fileno(),
                                fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self._locked = True
                except OSError:
                    self._handle_lock_failure()

            # 写入 sidecar 文件: PID + 启动时间.
            # 在 close() 之后, sidecar 没有任何句柄持有, 任意进程任意时刻
            # 都能 open('r') 读取它, 跨平台一致 (Plan P1-5).
            try:
                with open(self.sidecar_path, 'w', encoding='utf-8') as sf:
                    sf.write(f"{self.pid}\n")
                    sf.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            except OSError as e:
                # sidecar 写入失败不致命 — 主锁仍有效, 仅诊断信息缺失.
                # 后续冲突进程读 sidecar 时会 FileNotFoundError → 回退 "未知".
                self.logger.warning(
                    f"sidecar 写入失败 (主锁仍有效, 诊断信息将不可用): {e}"
                )

            self._t_acquired = time.time()
            _lock_mech = (
                'msvcrt.locking (Windows 独占字节锁)' if sys.platform == 'win32'
                else 'fcntl.flock (Unix 建议性独占锁)'
            )
            self.logger.info(
                f"已获取管道锁: {self.lock_file_path} (PID: {self.pid})"
            )
            # 运行期操作上下文 (纯日志富集, golden-safe): 把"用哪套 OS 锁机制、锁/诊断
            # 文件落在哪、为何需要串行"一次性写进日志, 便于排查并发实例被拒/占锁阻塞。
            self.logger.info(
                f"  锁运行期上下文: 机制={_lock_mech} | 锁目录="
                f"{os.path.dirname(self.lock_file_path)} | sidecar 诊断文件="
                f"{os.path.basename(self.sidecar_path)} | 持锁期间拒绝并发实例 "
                "(防多进程同写 data/processed/*.parquet 造成产物损坏)"
            )
            return self

        except Exception as e:
            # 清理资源
            if self.lock_file:
                try:
                    self.lock_file.close()
                except Exception as close_err:
                    # __enter__ 失败路径上的关闭失败 — debug 记录,
                    # 不能让 close 异常掩盖原始的获取锁失败 e.
                    self.logger.debug(
                        "lock file close failed during __enter__ cleanup: %s",
                        close_err,
                    )
                self.lock_file = None
            raise RuntimeError(f"获取管道锁失败: {e}")

    def _handle_lock_failure(self):
        """处理锁获取失败的情况。

        Plan P1-5: 改读 sidecar 文件 ``.pipeline.lock.info`` 获取占用者
        PID 与启动时间. sidecar 由占用者进程在 ``__enter__`` 中独立写入并
        立即 close, 没有任何句柄持有, 因此任意进程任意时刻读它都不会
        因 OS 锁/共享模式触发 PermissionError (Windows / Unix 行为一致).
        """
        if self.lock_file:
            try:
                self.lock_file.close()
            except Exception as close_err:
                # 锁获取失败诊断路径上的关闭失败 — debug 记录;
                # 即便 close 失败也要继续读 sidecar 给用户诊断信息.
                self.logger.debug(
                    "lock file close failed during _handle_lock_failure: %s",
                    close_err,
                )
            self.lock_file = None

        lock_info = "未知"
        try:
            with open(self.sidecar_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    lock_pid = lines[0].strip()
                    lock_time = lines[1].strip()
                    lock_info = f"PID {lock_pid}, 启动时间 {lock_time}"
        except FileNotFoundError:
            # 占用者尚未来得及写 sidecar (race 极窄), 或写入失败 (磁盘满等).
            pass
        except Exception:
            # 读 sidecar 异常 (UTF-8 解码失败等), 不让诊断阻塞主流程.
            pass

        error_msg = (
            f"管道已在运行中，无法启动新实例。\n"
            f"锁文件: {self.lock_file_path}\n"
            f"占用者: {lock_info}\n"
            f"如果确认没有其他实例运行，请手动删除锁文件 (含 sidecar "
            f"{os.path.basename(self.sidecar_path)})。"
        )
        if self.console_only_on_reject:
            # F4: 被拒实例不触 file handler (防经 delayed-truncating handler 首写截断在跑实例
            # 的共享 .log); 诊断改走 stderr。顶层未捕获的 RuntimeError traceback 亦落 stderr。
            print(error_msg, file=sys.stderr)
        else:
            self.logger.error(error_msg)
        raise RuntimeError(error_msg)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """释放锁。"""
        self._cleanup()
        return False

    def _cleanup(self):
        """清理锁文件 + sidecar 文件。"""
        if self.lock_file and self._locked:
            try:
                # 根据平台释放文件锁
                if sys.platform == 'win32':
                    import msvcrt
                    try:
                        msvcrt.locking(self.lock_file.fileno(),
                                       msvcrt.LK_UNLCK, 1)
                    except Exception:
                        pass  # _cleanup 尾路径; 紧接的 close() 会兜底释放 fd
                else:
                    import fcntl
                    try:
                        fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
                    except Exception:
                        pass  # _cleanup 尾路径; 紧接的 close() 会兜底释放 fd

                self.lock_file.close()
                self.lock_file = None
                self._locked = False

                # 纯日志富集 (golden-safe): 报告本次持锁墙钟时长, 便于审计"流水线串行
                # 段实际占锁多久" / 排查长时间占锁阻塞并发实例的情形。时长经 sig4 渲染为
                # 四位有效数字 (项目规范 2026-06-24)。
                if self._t_acquired is not None:
                    _hold_s = time.time() - self._t_acquired
                    self.logger.info(
                        f"管道锁持锁时长: {sig4(_hold_s)} 秒 (PID: {self.pid}; "
                        "自获取至释放的墙钟耗时)"
                    )

                # 删除主锁文件
                if os.path.exists(self.lock_file_path):
                    try:
                        os.remove(self.lock_file_path)
                        self.logger.info(
                            f"已释放管道锁: {self.lock_file_path}"
                        )
                    except Exception as e:
                        self.logger.warning(f"删除锁文件失败: {e}")

                # 删除 sidecar 文件 (Plan P1-5).
                # 即使 sidecar 写入曾失败 (不存在), 这里 silent skip 也安全.
                if os.path.exists(self.sidecar_path):
                    try:
                        os.remove(self.sidecar_path)
                    except Exception as e:
                        self.logger.warning(
                            f"删除 sidecar 文件失败: {e}"
                        )
            except Exception as e:
                self.logger.warning(f"清理锁文件失败: {e}")
