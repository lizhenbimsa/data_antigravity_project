"""
test_pipeline_lock_standalone.py — PipelineLock独立单元测试
===========================================================

独立测试脚本，不依赖项目其他模块，直接测试pipeline_lock.py
"""

import os
import sys
import tempfile
import threading
import time
import unittest


class MockLogger:
    """模拟日志对象"""
    def __init__(self):
        self.info_calls = []
        self.error_calls = []
        self.warning_calls = []
        self.debug_calls = []

    def info(self, msg):
        self.info_calls.append(msg)

    def error(self, msg):
        self.error_calls.append(msg)

    def warning(self, msg):
        self.warning_calls.append(msg)

    def debug(self, msg):
        self.debug_calls.append(msg)


# 直接导入PipelineLock类（内联代码以避免依赖问题）
# Plan P1-5: 与生产 news_process/core/locking.py 的 sidecar 设计同步.
class PipelineLock:
    """管道运行锁 (内联副本, 与 news_process.core.locking.PipelineLock 同步; Plan P1-5 sidecar 设计)."""

    def __init__(self, logger, lock_dir: str = None):
        self.logger = logger
        if lock_dir is None:
            lock_dir = os.path.dirname(os.path.abspath(__file__))
        self.lock_file_path = os.path.join(lock_dir, '.pipeline.lock')
        self.sidecar_path = self.lock_file_path + '.info'
        self.lock_file = None
        self.pid = os.getpid()
        self._locked = False

    def __enter__(self):
        try:
            self.lock_file = open(self.lock_file_path, 'w')

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
                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self._locked = True
                except OSError:
                    self._handle_lock_failure()

            try:
                with open(self.sidecar_path, 'w', encoding='utf-8') as sf:
                    sf.write(f"{self.pid}\n")
                    sf.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            except OSError as e:
                self.logger.warning(
                    f"sidecar 写入失败 (主锁仍有效, 诊断信息将不可用): {e}"
                )

            self.logger.info(f"已获取管道锁: {self.lock_file_path} (PID: {self.pid})")
            return self

        except Exception as e:
            if self.lock_file:
                try:
                    self.lock_file.close()
                except Exception:
                    pass
                self.lock_file = None
            raise RuntimeError(f"获取管道锁失败: {e}")

    def _handle_lock_failure(self):
        if self.lock_file:
            try:
                self.lock_file.close()
            except Exception:
                pass
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
            pass
        except Exception:
            pass

        error_msg = (
            f"管道已在运行中，无法启动新实例。\n"
            f"锁文件: {self.lock_file_path}\n"
            f"占用者: {lock_info}\n"
            f"如果确认没有其他实例运行，请手动删除锁文件 (含 sidecar "
            f"{os.path.basename(self.sidecar_path)})。"
        )
        self.logger.error(error_msg)
        raise RuntimeError(error_msg)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup()
        return False

    def _cleanup(self):
        if self.lock_file and self._locked:
            try:
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

                if os.path.exists(self.lock_file_path):
                    try:
                        os.remove(self.lock_file_path)
                        self.logger.info(f"已释放管道锁: {self.lock_file_path}")
                    except Exception as e:
                        self.logger.warning(f"删除锁文件失败: {e}")
                if os.path.exists(self.sidecar_path):
                    try:
                        os.remove(self.sidecar_path)
                    except Exception as e:
                        self.logger.warning(f"删除 sidecar 文件失败: {e}")
            except Exception as e:
                self.logger.warning(f"清理锁文件失败: {e}")


class TestPipelineLock(unittest.TestCase):
    """PipelineLock单元测试套件"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.logger = MockLogger()
        self.lock_file_path = os.path.join(self.temp_dir, '.pipeline.lock')
        # Plan P1-5: sidecar 路径 (PID + 启动时间存于此, 不再存于主锁文件)
        self.sidecar_path = self.lock_file_path + '.info'

    def tearDown(self):
        for p in (self.lock_file_path, self.sidecar_path):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
        try:
            os.rmdir(self.temp_dir)
        except Exception:
            pass

    def test_01_basic_lock_acquire_and_release(self):
        """测试1: 基本的锁获取和释放"""
        print("\n[测试1] 基本的锁获取和释放...")

        with PipelineLock(self.logger, self.temp_dir):
            self.assertTrue(os.path.exists(self.lock_file_path), "锁文件应该被创建")
            self.assertTrue(len(self.logger.info_calls) > 0, "应该记录info日志")

        self.assertFalse(os.path.exists(self.lock_file_path), "锁文件应该被删除")
        print("✓ 测试通过")

    def test_02_concurrent_lock_conflict(self):
        """测试2: 并发锁冲突检测"""
        print("\n[测试2] 并发锁冲突检测...")

        with PipelineLock(self.logger, self.temp_dir):
            logger2 = MockLogger()

            with self.assertRaises(RuntimeError) as context:
                with PipelineLock(logger2, self.temp_dir):
                    pass

            self.assertIn('管道已在运行中', str(context.exception))
            self.assertTrue(len(logger2.error_calls) > 0, "应该记录错误日志")

        print("✓ 测试通过")

    def test_03_lock_file_content(self):
        """测试3: sidecar 文件内容验证 (Plan P1-5: 跨平台)."""
        print("\n[测试3] sidecar 文件内容验证 (Plan P1-5)...")

        with PipelineLock(self.logger, self.temp_dir):
            self.assertTrue(os.path.exists(self.lock_file_path),
                            "主锁文件应该存在")
            self.assertTrue(os.path.exists(self.sidecar_path),
                            "sidecar 文件应该存在")
            with open(self.sidecar_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            self.assertEqual(len(lines), 2, "sidecar 文件应该包含2行")

            pid = int(lines[0].strip())
            self.assertEqual(pid, os.getpid(), "PID应该匹配")

            timestamp = lines[1].strip()
            self.assertRegex(timestamp, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
                           "时间戳格式应该正确")

        print("✓ 测试通过")

    def test_04_lock_cleanup_on_exception(self):
        """测试4: 异常时的锁清理"""
        print("\n[测试4] 异常时的锁清理...")

        try:
            with PipelineLock(self.logger, self.temp_dir):
                raise ValueError("测试异常")
        except ValueError:
            pass

        self.assertFalse(os.path.exists(self.lock_file_path),
                        "异常后锁文件应该被清理")
        print("✓ 测试通过")

    def test_05_multiple_sequential_locks(self):
        """测试5: 多次顺序获取锁"""
        print("\n[测试5] 多次顺序获取锁...")

        for i in range(3):
            with PipelineLock(self.logger, self.temp_dir):
                self.assertTrue(os.path.exists(self.lock_file_path))

        self.assertFalse(os.path.exists(self.lock_file_path),
                        "最终锁文件应该被清理")
        print("✓ 测试通过")

    def test_06_lock_state_tracking(self):
        """测试6: 锁状态跟踪"""
        print("\n[测试6] 锁状态跟踪...")

        lock = PipelineLock(self.logger, self.temp_dir)

        self.assertFalse(lock._locked, "初始状态应该是未锁定")
        self.assertIsNone(lock.lock_file, "初始状态lock_file应该是None")

        lock.__enter__()
        self.assertTrue(lock._locked, "获取锁后应该是锁定状态")
        self.assertIsNotNone(lock.lock_file, "获取锁后lock_file不应该是None")

        lock.__exit__(None, None, None)
        self.assertFalse(lock._locked, "释放锁后应该是未锁定状态")

        print("✓ 测试通过")

    def test_07_platform_specific_locking(self):
        """测试7: 平台特定的锁机制"""
        print(f"\n[测试7] 平台特定的锁机制 (当前平台: {sys.platform})...")

        if sys.platform == 'win32':
            try:
                import msvcrt  # noqa: F401 — 测试目的: 验证模块可导入
                print("  - Windows平台: msvcrt模块可用")
            except ImportError:
                self.fail("Windows平台应该有msvcrt模块")
        else:
            try:
                import fcntl  # noqa: F401 — 测试目的: 验证模块可导入
                print("  - Unix/Linux平台: fcntl模块可用")
            except ImportError:
                self.fail("Unix/Linux平台应该有fcntl模块")

        with PipelineLock(self.logger, self.temp_dir) as lock:
            self.assertTrue(lock._locked, "锁应该被成功获取")

        print("✓ 测试通过")

    def test_08_concurrent_thread_simulation(self):
        """测试8: 模拟并发线程场景"""
        print("\n[测试8] 模拟并发线程场景...")

        def try_acquire_lock(result_list, index):
            logger = MockLogger()
            try:
                with PipelineLock(logger, self.temp_dir):
                    result_list[index] = 'success'
                    time.sleep(0.05)
            except RuntimeError:
                result_list[index] = 'failed'

        with PipelineLock(self.logger, self.temp_dir):
            results = [None, None]

            t1 = threading.Thread(target=try_acquire_lock, args=(results, 0))
            t2 = threading.Thread(target=try_acquire_lock, args=(results, 1))

            t1.start()
            t2.start()

            t1.join()
            t2.join()

            self.assertEqual(results[0], 'failed', "第一个线程应该失败")
            self.assertEqual(results[1], 'failed', "第二个线程应该失败")

        print("✓ 测试通过")

    def test_09_rapid_lock_acquisition(self):
        """测试9: 快速连续获取锁"""
        print("\n[测试9] 快速连续获取锁 (50次)...")

        for i in range(50):
            with PipelineLock(self.logger, self.temp_dir):
                pass

        self.assertFalse(os.path.exists(self.lock_file_path),
                        "最终锁文件应该被清理")
        print("✓ 测试通过")

    def test_10_lock_info_on_conflict(self):
        """测试10: 锁冲突时的诊断信息显示 (Plan P1-5: 跨平台)."""
        print("\n[测试10] 锁冲突时的诊断信息显示 (Plan P1-5)...")

        with PipelineLock(self.logger, self.temp_dir):
            logger2 = MockLogger()

            try:
                with PipelineLock(logger2, self.temp_dir):
                    pass
            except RuntimeError:
                pass

            self.assertTrue(len(logger2.error_calls) > 0, "应该有错误日志")
            error_msg = logger2.error_calls[0]
            self.assertIn('PID', error_msg, "错误消息应该包含PID")
            self.assertIn('启动时间', error_msg, "错误消息应该包含启动时间")

        print("✓ 测试通过")


def run_tests():
    """运行所有测试"""
    print("=" * 70)
    print("PipelineLock 单元测试")
    print("=" * 70)
    print(f"Python版本: {sys.version}")
    print(f"平台: {sys.platform}")
    print("=" * 70)

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPipelineLock)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
