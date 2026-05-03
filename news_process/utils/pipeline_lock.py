"""
pipeline_lock.py — 管道并发运行保护（跨平台）
====================================

功能：
    提供文件锁机制，防止多个管道实例同时运行导致数据损坏。
    支持Windows和Unix/Linux平台。

使用方法：
    from utils.pipeline_lock import PipelineLock

    with PipelineLock(logger):
        # 执行管道逻辑
        run_pipeline()
"""

import os
import sys
import time


class PipelineLock:
    """管道运行锁，防止并发执行。

    使用文件锁机制确保同一时间只有一个管道实例运行。
    跨平台支持：Windows使用msvcrt，Unix/Linux使用fcntl。
    """

    def __init__(self, logger, lock_dir: str = None):
        """初始化管道锁。

        Args:
            logger: 日志对象
            lock_dir: 锁文件目录，默认为当前目录
        """
        self.logger = logger
        if lock_dir is None:
            lock_dir = os.path.dirname(os.path.abspath(__file__))
        self.lock_file_path = os.path.join(lock_dir, '.pipeline.lock')
        self.lock_file = None
        self.pid = os.getpid()
        self._locked = False

    def __enter__(self):
        """获取锁。"""
        try:
            # 创建或打开锁文件
            self.lock_file = open(self.lock_file_path, 'w')

            # 根据平台选择锁机制
            if sys.platform == 'win32':
                # Windows平台使用msvcrt
                import msvcrt
                try:
                    msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                    self._locked = True
                except IOError:
                    self._handle_lock_failure()
            else:
                # Unix/Linux平台使用fcntl
                import fcntl
                try:
                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self._locked = True
                except IOError:
                    self._handle_lock_failure()

            # 写入当前进程PID和时间戳
            self.lock_file.write(f"{self.pid}\n")
            self.lock_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.lock_file.flush()

            self.logger.info(f"已获取管道锁: {self.lock_file_path} (PID: {self.pid})")
            return self

        except Exception as e:
            # 清理资源
            if self.lock_file:
                try:
                    self.lock_file.close()
                except Exception:
                    pass
                self.lock_file = None
            raise RuntimeError(f"获取管道锁失败: {e}")

    def _handle_lock_failure(self):
        """处理锁获取失败的情况。"""
        # 锁已被占用，尝试读取锁文件内容
        if self.lock_file:
            try:
                self.lock_file.close()
            except Exception:
                pass
            self.lock_file = None

        lock_info = "未知"
        try:
            with open(self.lock_file_path, 'r') as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    lock_pid = lines[0].strip()
                    lock_time = lines[1].strip()
                    lock_info = f"PID {lock_pid}, 启动时间 {lock_time}"
        except Exception:
            pass

        error_msg = (
            f"管道已在运行中，无法启动新实例。\n"
            f"锁文件: {self.lock_file_path}\n"
            f"占用者: {lock_info}\n"
            f"如果确认没有其他实例运行，请手动删除锁文件。"
        )
        self.logger.error(error_msg)
        raise RuntimeError(error_msg)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """释放锁。"""
        self._cleanup()
        return False

    def _cleanup(self):
        """清理锁文件。"""
        if self.lock_file and self._locked:
            try:
                # 根据平台释放文件锁
                if sys.platform == 'win32':
                    import msvcrt
                    try:
                        msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                    except Exception:
                        pass
                else:
                    import fcntl
                    try:
                        fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
                    except Exception:
                        pass

                self.lock_file.close()
                self.lock_file = None
                self._locked = False

                # 删除锁文件
                if os.path.exists(self.lock_file_path):
                    try:
                        os.remove(self.lock_file_path)
                        self.logger.info(f"已释放管道锁: {self.lock_file_path}")
                    except Exception as e:
                        self.logger.warning(f"删除锁文件失败: {e}")
            except Exception as e:
                self.logger.warning(f"清理锁文件失败: {e}")
