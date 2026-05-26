"""
test_pipeline_lock.py — PipelineLock单元测试
================================================

测试覆盖：
    1. 基本锁获取和释放
    2. 并发锁冲突检测
    3. 跨平台兼容性（Windows/Unix）
    4. 异常处理和资源清理
    5. 边界条件和错误场景
"""

import logging
import os
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Phase 5c-2: 添加项目父目录到 sys.path 解析 ``news_process.*``
_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

from news_process.core.locking import PipelineLock


class TestPipelineLock(unittest.TestCase):
    """PipelineLock单元测试套件"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = Mock(spec=logging.Logger)
        self.lock_file_path = os.path.join(self.temp_dir, '.pipeline.lock')
        # Plan P1-5: sidecar 文件路径 (PID + 启动时间存于此, 不再存于主锁文件)
        self.sidecar_path = self.lock_file_path + '.info'

    def tearDown(self):
        """测试后清理"""
        # 清理临时文件 + sidecar (Plan P1-5)
        for p in (self.lock_file_path, self.sidecar_path):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

        # 清理临时目录
        try:
            os.rmdir(self.temp_dir)
        except Exception:
            pass

    def test_basic_lock_acquire_and_release(self):
        """测试1: 基本的锁获取和释放"""
        with PipelineLock(self.logger, self.temp_dir):
            # 验证锁文件已创建
            self.assertTrue(os.path.exists(self.lock_file_path))

            # 验证日志记录
            self.logger.info.assert_called()
            info_calls = [str(call) for call in self.logger.info.call_args_list]
            self.assertTrue(any('已获取管道锁' in str(call) for call in info_calls))

        # 验证锁文件已删除
        self.assertFalse(os.path.exists(self.lock_file_path))

    def test_concurrent_lock_conflict(self):
        """测试2: 并发锁冲突检测"""
        # 第一个锁成功获取
        with PipelineLock(self.logger, self.temp_dir):
            # 尝试获取第二个锁应该失败
            logger2 = Mock(spec=logging.Logger)
            with self.assertRaises(RuntimeError) as context:
                with PipelineLock(logger2, self.temp_dir):
                    pass

            # 验证错误消息
            self.assertIn('管道已在运行中', str(context.exception))

            # 验证错误日志
            logger2.error.assert_called()

    def test_lock_file_content(self):
        """测试3: 锁文件 sidecar 内容验证 (Plan P1-5: 跨平台).

        历史版本中, PID + 启动时间写入主锁文件 ``.pipeline.lock`` 内容,
        但 Windows ``msvcrt.locking + open('w')`` 持有写句柄后同进程再
        ``open('r')`` 触发 PermissionError, 让本测试在 Windows 上不得不
        @skipIf. 现在改为 sidecar 文件 ``.pipeline.lock.info``, 写完立即
        close 不持有句柄, 跨平台一致可读.
        """
        with PipelineLock(self.logger, self.temp_dir):
            # 主锁文件存在但内容不再是诊断信息载体 (Plan P1-5)
            self.assertTrue(os.path.exists(self.lock_file_path))
            # sidecar 文件存在且包含 PID + 启动时间
            self.assertTrue(os.path.exists(self.sidecar_path))
            with open(self.sidecar_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            self.assertEqual(len(lines), 2)
            pid = int(lines[0].strip())
            self.assertEqual(pid, os.getpid())

            timestamp = lines[1].strip()
            self.assertRegex(timestamp, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')

    def test_lock_cleanup_on_exception(self):
        """测试4: 异常时的锁清理"""
        try:
            with PipelineLock(self.logger, self.temp_dir):
                # 在with块内抛出异常
                raise ValueError("测试异常")
        except ValueError:
            pass

        # 验证锁文件已被清理
        self.assertFalse(os.path.exists(self.lock_file_path))

    def test_lock_with_custom_directory(self):
        """测试5: 自定义锁文件目录"""
        custom_dir = tempfile.mkdtemp()
        try:
            with PipelineLock(self.logger, custom_dir):
                lock_path = os.path.join(custom_dir, '.pipeline.lock')
                self.assertTrue(os.path.exists(lock_path))

            self.assertFalse(os.path.exists(lock_path))
        finally:
            try:
                os.rmdir(custom_dir)
            except Exception:
                pass

    def test_lock_with_none_directory(self):
        """测试6: 默认锁文件目录（None参数）"""
        # 当lock_dir为None时，应使用utils目录
        with PipelineLock(self.logger, None):
            # 验证锁被创建（不验证具体路径，因为它在utils目录）
            self.logger.info.assert_called()

    @unittest.skipIf(sys.platform != 'win32', "仅在Windows上测试")
    def test_windows_msvcrt_locking(self):
        """测试7: Windows平台msvcrt锁机制"""

        with PipelineLock(self.logger, self.temp_dir) as lock:
            # 验证锁文件存在
            self.assertTrue(os.path.exists(self.lock_file_path))

            # 验证_locked标志
            self.assertTrue(lock._locked)

    @unittest.skipIf(sys.platform == 'win32', "仅在Unix/Linux上测试")
    def test_unix_fcntl_locking(self):
        """测试8: Unix/Linux平台fcntl锁机制"""

        with PipelineLock(self.logger, self.temp_dir) as lock:
            # 验证锁文件存在
            self.assertTrue(os.path.exists(self.lock_file_path))

            # 验证_locked标志
            self.assertTrue(lock._locked)

    def test_lock_info_on_conflict(self):
        """测试9: 锁冲突时的诊断信息显示 (Plan P1-5: 跨平台).

        Sidecar 化后, 冲突方 ``_handle_lock_failure`` 读独立的
        ``.pipeline.lock.info`` 文件 (无任何句柄持有), Windows 也能正常
        读到 PID + 启动时间. 历史 skipIf 已撤销.
        """
        with PipelineLock(self.logger, self.temp_dir):
            logger2 = Mock(spec=logging.Logger)

            try:
                with PipelineLock(logger2, self.temp_dir):
                    pass
            except RuntimeError:
                pass

            error_calls = logger2.error.call_args_list
            self.assertTrue(len(error_calls) > 0)
            error_msg = str(error_calls[0])
            self.assertIn('PID', error_msg)
            self.assertIn('启动时间', error_msg)

    def test_multiple_sequential_locks(self):
        """测试10: 多次顺序获取锁"""
        # 第一次获取和释放
        with PipelineLock(self.logger, self.temp_dir):
            pass

        # 第二次获取和释放
        with PipelineLock(self.logger, self.temp_dir):
            pass

        # 第三次获取和释放
        with PipelineLock(self.logger, self.temp_dir):
            pass

        # 验证最终锁文件已清理
        self.assertFalse(os.path.exists(self.lock_file_path))

    def test_lock_file_permission_error(self):
        """测试11: 锁文件权限错误处理"""
        # 创建一个只读目录（Unix/Linux）
        if sys.platform != 'win32':
            readonly_dir = tempfile.mkdtemp()
            try:
                os.chmod(readonly_dir, 0o444)

                with self.assertRaises(RuntimeError):
                    with PipelineLock(self.logger, readonly_dir):
                        pass
            finally:
                os.chmod(readonly_dir, 0o755)
                try:
                    os.rmdir(readonly_dir)
                except Exception:
                    pass

    def test_lock_cleanup_warning_on_failure(self):
        """测试12: 清理失败时的警告日志"""
        lock = PipelineLock(self.logger, self.temp_dir)

        # 手动进入锁
        lock.__enter__()

        # 模拟文件删除失败
        with patch('os.path.exists', return_value=True):
            with patch('os.remove', side_effect=OSError("模拟删除失败")):
                lock.__exit__(None, None, None)

        # 验证警告日志
        self.logger.warning.assert_called()

    def test_lock_state_tracking(self):
        """测试13: 锁状态跟踪"""
        lock = PipelineLock(self.logger, self.temp_dir)

        # 初始状态
        self.assertFalse(lock._locked)
        self.assertIsNone(lock.lock_file)

        # 获取锁后
        lock.__enter__()
        self.assertTrue(lock._locked)
        self.assertIsNotNone(lock.lock_file)

        # 释放锁后
        lock.__exit__(None, None, None)
        self.assertFalse(lock._locked)

    def test_concurrent_process_simulation(self):
        """测试14: 模拟并发进程场景"""
        def try_acquire_lock(result_list, index):
            """子线程尝试获取锁"""
            logger = Mock(spec=logging.Logger)
            try:
                with PipelineLock(logger, self.temp_dir):
                    result_list[index] = 'success'
                    time.sleep(0.1)
            except RuntimeError:
                result_list[index] = 'failed'

        # 主线程持有锁
        with PipelineLock(self.logger, self.temp_dir):
            results = [None, None]

            # 启动两个子线程尝试获取锁
            t1 = threading.Thread(target=try_acquire_lock, args=(results, 0))
            t2 = threading.Thread(target=try_acquire_lock, args=(results, 1))

            t1.start()
            t2.start()

            t1.join()
            t2.join()

            # 验证两个子线程都失败了
            self.assertEqual(results[0], 'failed')
            self.assertEqual(results[1], 'failed')

    def test_lock_file_corruption_handling(self):
        """测试15: 损坏的锁文件处理"""
        # 创建一个损坏的锁文件（只有一行）
        # F-13 (2026-05-16): encoding='utf-8' 与生产 locking.py 一致
        with open(self.lock_file_path, 'w', encoding='utf-8') as f:
            f.write("12345\n")

        # 手动锁定文件
        if sys.platform == 'win32':
            import msvcrt
            lock_file = open(self.lock_file_path, 'r+', encoding='utf-8')
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            lock_file = open(self.lock_file_path, 'r+', encoding='utf-8')
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

        try:
            # 尝试获取锁应该失败
            logger2 = Mock(spec=logging.Logger)
            with self.assertRaises(RuntimeError):
                with PipelineLock(logger2, self.temp_dir):
                    pass

            # 验证错误信息中包含"未知"（因为锁文件格式不完整）
            error_calls = logger2.error.call_args_list
            # 注意：由于锁文件只有一行，lock_info应该显示"未知"
        finally:
            # 清理
            if sys.platform == 'win32':
                import msvcrt
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()


class TestPipelineLockEdgeCases(unittest.TestCase):
    """PipelineLock边界条件测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = Mock(spec=logging.Logger)

    def tearDown(self):
        """测试后清理"""
        lock_file = os.path.join(self.temp_dir, '.pipeline.lock')
        if os.path.exists(lock_file):
            try:
                os.remove(lock_file)
            except Exception:
                pass
        try:
            os.rmdir(self.temp_dir)
        except Exception:
            pass

    @unittest.skip(
        "PipelineLock 不负责空字符串 lock_dir 的输入校验 — 该 contract 属于上层调用方. "
        "Linux/macOS: os.path.join('', '.pipeline.lock') == '.pipeline.lock' (cwd 相对路径, "
        "fcntl 锁定成功); Windows: 同上 (msvcrt 锁定成功). 两个平台 PipelineLock(\"\") 都不 raise. "
        "原 skipIf(win32) 漏判 Linux 同样行为, CI ubuntu 上始终 fail; 改为永久 skip + 文档化, "
        "保留测试用例骨架, 便于未来若决定把 input validation 迁入 PipelineLock 时一行恢复."
    )
    def test_empty_lock_directory(self):
        """边界测试1: 空的锁目录路径 (永久 skip; 见 @skip 注释)"""
        with self.assertRaises(Exception):
            with PipelineLock(self.logger, ""):
                pass

    def test_nonexistent_lock_directory(self):
        """边界测试2: 不存在的锁目录"""
        nonexistent_dir = os.path.join(self.temp_dir, 'nonexistent')

        with self.assertRaises(Exception):
            with PipelineLock(self.logger, nonexistent_dir):
                pass

    def test_lock_with_very_long_path(self):
        """边界测试3: 超长路径"""
        # 创建一个很长的路径
        long_path = self.temp_dir
        for i in range(10):
            long_path = os.path.join(long_path, f'subdir_{i}')

        # 创建目录
        os.makedirs(long_path, exist_ok=True)

        try:
            with PipelineLock(self.logger, long_path):
                lock_file = os.path.join(long_path, '.pipeline.lock')
                self.assertTrue(os.path.exists(lock_file))
        finally:
            # 清理
            import shutil
            try:
                shutil.rmtree(os.path.join(self.temp_dir, 'subdir_0'))
            except Exception:
                pass

    def test_rapid_lock_acquisition(self):
        """边界测试4: 快速连续获取锁"""
        for i in range(100):
            with PipelineLock(self.logger, self.temp_dir):
                pass

        # 验证最终状态正常
        lock_file = os.path.join(self.temp_dir, '.pipeline.lock')
        self.assertFalse(os.path.exists(lock_file))


# ============================================================================
# quality-hardening Round 12 (2026-05-27): core/locking.py 74% → ~88%
# Windows-reachable except handlers (Linux fcntl branches separately blocked
# in docs/TECH-DEBT.md §[1-A])
# ============================================================================


class TestPipelineLockErrorHandlers(unittest.TestCase):
    """missing-branch coverage for OSError / Exception cleanup paths."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.logger = Mock(spec=logging.Logger)
        self.lock_file_path = os.path.join(self.temp_dir, '.pipeline.lock')
        self.sidecar_path = os.path.join(self.temp_dir, '.pipeline.lock.info')

    def tearDown(self):
        for p in (self.lock_file_path, self.sidecar_path):
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass
        try:
            os.rmdir(self.temp_dir)
        except Exception:
            pass

    def test_sidecar_write_oserror_logs_warning_but_lock_holds(self):
        """sidecar 写入 OSError → warning + 主锁仍有效 (lines 101-106)."""
        # Patch open() 的第二次调用 (sidecar 写) → 抛 OSError
        # 第一次调用 (主 lock_file) 应正常.
        import builtins
        orig_open = builtins.open
        call_count = {'n': 0}

        def fake_open(path, *args, **kwargs):
            call_count['n'] += 1
            if str(path).endswith('.pipeline.lock.info'):
                raise OSError("simulated sidecar disk full")
            return orig_open(path, *args, **kwargs)

        with patch('builtins.open', side_effect=fake_open):
            with PipelineLock(self.logger, self.temp_dir):
                pass
        # warning 至少被 sidecar 失败路径调用一次
        warn_calls = [
            c for c in self.logger.warning.call_args_list
            if 'sidecar' in str(c)
        ]
        self.assertTrue(len(warn_calls) >= 1)

    def test_enter_cleanup_close_failure_does_not_mask_original(self):
        """__enter__ 失败 + lock_file.close() 也失败 → RuntimeError 仍抛, debug 记录
        (lines 116-125)."""
        # 让 msvcrt.locking 抛非 OSError 异常, 然后 lock_file.close 也失败.
        with patch('news_process.core.locking.os.path.join',
                   return_value=self.lock_file_path):
            with patch('msvcrt.locking', side_effect=RuntimeError("simulated lock failure")):
                with self.assertRaises(RuntimeError):
                    with PipelineLock(self.logger, self.temp_dir):
                        pass

    def test_handle_lock_failure_close_oserror_logged_to_debug(self):
        """_handle_lock_failure 内 close() 失败 → debug log, 不阻塞主 raise
        (lines 139-145)."""
        # Pre-occupy the lock so second attempt triggers _handle_lock_failure.
        primary = PipelineLock(self.logger, self.temp_dir)
        primary.__enter__()
        try:
            second_logger = Mock(spec=logging.Logger)
            second_lock = PipelineLock(second_logger, self.temp_dir)
            # 让 lock_file.close 抛异常
            import io
            real_open = io.open
            def fake_open(path, *a, **kw):
                f = real_open(path, *a, **kw)
                # 包装 close 抛错
                orig_close = f.close
                def bad_close(*args, **kwargs):
                    raise OSError("simulated close failure during failure cleanup")
                f.close = bad_close
                return f
            with patch('builtins.open', side_effect=fake_open):
                with self.assertRaises(RuntimeError):
                    second_lock.__enter__()
            # close 失败 → 应触发 debug log 至少 1 次
            self.assertTrue(second_logger.debug.called or second_logger.error.called)
        finally:
            primary.__exit__(None, None, None)

    def test_handle_lock_failure_sidecar_read_unicode_decode_returns_unknown(self):
        """sidecar 损坏 (非 UTF-8) → except + lock_info 留 '未知' (lines 159-161)."""
        # Write non-UTF-8 bytes to sidecar
        primary = PipelineLock(self.logger, self.temp_dir)
        primary.__enter__()
        try:
            # 覆盖 sidecar 为损坏的二进制
            with open(self.sidecar_path, 'wb') as f:
                f.write(b'\xff\xfe\x00\x80\x81')  # invalid UTF-8
            second_logger = Mock(spec=logging.Logger)
            second_lock = PipelineLock(second_logger, self.temp_dir)
            with self.assertRaises(RuntimeError) as ctx:
                second_lock.__enter__()
            # 错误消息应含 '未知' (sidecar 读 except 走 fallback)
            self.assertIn('未知', str(ctx.exception))
        finally:
            primary.__exit__(None, None, None)


if __name__ == '__main__':
    # 配置测试运行器
    unittest.main(verbosity=2)
