"""
tests/test_helpers.py — utils/helpers.py 单元测试
==================================================
"""

import os
import sys
import time
import logging
import pytest
import pandas as pd
import numpy as np

# Phase 5c-2: 注入项目父目录, 让 ``news_process.core.*`` 在包模式下可解析
_PROJECT_PARENT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import (
    setup_logging, log_and_time, log_memory_usage, log_stage_summary,
)
from news_process.core.reporting import safe_save_preview_csv, save_dataset
from news_process.core.stage import run_stage


# ============================================================================
# load_config 测试
# ============================================================================

class TestLoadConfig:
    """测试 load_config() 配置加载功能。"""

    def test_load_config_default(self):
        """默认路径加载，配置应含关键 key。"""
        config = load_config()
        assert 'paths' in config
        assert 'filenames' in config
        assert 'parallel' in config

    def test_load_config_missing_file(self):
        """不存在的路径应抛出 FileNotFoundError。"""
        with pytest.raises(FileNotFoundError):
            load_config('/nonexistent/path/config.yaml')

    def test_load_config_resolves_relative_paths(self):
        """以 ./ 开头的路径应被解析为绝对路径。"""
        config = load_config()
        output_dir = config['paths']['output_dir']
        assert os.path.isabs(output_dir), f"预期绝对路径，实际: {output_dir}"

    def test_load_config_returns_dict(self):
        """返回值应为字典类型。"""
        config = load_config()
        assert isinstance(config, dict)


# ============================================================================
# setup_logging 测试
# ============================================================================

class TestSetupLogging:
    """测试 setup_logging() 日志配置功能。"""

    def test_creates_log_file(self, tmp_dir):
        """应自动创建日志文件。

        Phase 4e 修复: setup_logging 在 NEWS_PROCESS_RUN_ID 环境变量存在时
        会把日志路由到 ``<log_dir>/runs/<run_id>/<stage>.log`` (per-run 隔离)。
        测试需要适配两种路径模式; 早期版本只检查 legacy 路径, 在
        test_dag_consistency 等先 import 的测试设置 RUN_ID 后失败。
        """
        log_dir = str(tmp_dir / 'logs')
        logger = setup_logging('test_stage', log_dir)
        logger.info("测试消息")
        run_id = os.environ.get("NEWS_PROCESS_RUN_ID")
        if run_id:
            expected = os.path.join(log_dir, 'runs', run_id, 'test_stage.log')
        else:
            expected = os.path.join(log_dir, 'test_stage.log')
        assert os.path.exists(expected), (
            f"Log file not at expected path {expected!r}; "
            f"NEWS_PROCESS_RUN_ID={run_id!r}"
        )

    def test_console_only_no_file(self, tmp_dir):
        """console_only=True 时不应创建文件。"""
        log_dir = str(tmp_dir / 'logs_console')
        logger = setup_logging('test_console', log_dir, console_only=True)
        logger.info("仅控制台消息")
        # 不应有文件 handler
        file_handlers = [h for h in logger.handlers
                         if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) == 0

    def test_no_duplicate_handlers(self, tmp_dir):
        """重复调用不应产生重复 handler。"""
        log_dir = str(tmp_dir / 'logs_dup')
        logger1 = setup_logging('test_dup', log_dir)
        handler_count_1 = len(logger1.handlers)
        logger2 = setup_logging('test_dup', log_dir)
        handler_count_2 = len(logger2.handlers)
        assert handler_count_1 == handler_count_2

    def test_returns_logger_instance(self, tmp_dir):
        """返回值应为 logging.Logger 实例。"""
        log_dir = str(tmp_dir / 'logs_type')
        logger = setup_logging('test_type', log_dir)
        assert isinstance(logger, logging.Logger)

    def test_logger_name_matches(self, tmp_dir):
        """logger name 应等于 stage_name。"""
        log_dir = str(tmp_dir / 'logs_name')
        logger = setup_logging('my_stage_name', log_dir)
        assert logger.name == 'my_stage_name'


# ============================================================================
# log_and_time 装饰器测试
# ============================================================================

class TestLogAndTime:
    """测试 log_and_time() 装饰器。"""

    def test_returns_result(self, tmp_dir):
        """装饰后的函数应正确返回结果。"""
        log_dir = str(tmp_dir / 'logs_dec')
        logger = setup_logging('test_deco', log_dir)

        @log_and_time(logger)
        def add(a, b):
            return a + b

        result = add(3, 4)
        assert result == 7

    def test_preserves_function_name(self, tmp_dir):
        """装饰后的函数应保留原函数名。"""
        log_dir = str(tmp_dir / 'logs_name2')
        logger = setup_logging('test_name2', log_dir)

        @log_and_time(logger)
        def my_function():
            pass

        assert my_function.__name__ == 'my_function'

    def test_exception_propagated(self, tmp_dir):
        """异常应被重新抛出。"""
        log_dir = str(tmp_dir / 'logs_exc')
        logger = setup_logging('test_exc', log_dir)

        @log_and_time(logger)
        def failing_func():
            raise ValueError("测试错误")

        with pytest.raises(ValueError, match="测试错误"):
            failing_func()

    def test_dataframe_input_logging(self, tmp_dir, sample_df):
        """DataFrame 参数应被检测并记录行数。"""
        log_dir = str(tmp_dir / 'logs_df')
        logger = setup_logging('test_df', log_dir)

        @log_and_time(logger)
        def process(df):
            return df.head(5)

        result = process(sample_df)
        assert len(result) == 5


# ============================================================================
# log_memory_usage 测试
# ============================================================================

class TestLogMemoryUsage:
    """测试 log_memory_usage() 功能。"""

    def test_no_exception(self, tmp_dir):
        """调用不应抛出异常。"""
        log_dir = str(tmp_dir / 'logs_mem')
        logger = setup_logging('test_mem', log_dir)
        log_memory_usage(logger, "测试标签")

    def test_with_empty_tag(self, tmp_dir):
        """空 tag 也不应抛异常。"""
        log_dir = str(tmp_dir / 'logs_mem2')
        logger = setup_logging('test_mem2', log_dir)
        log_memory_usage(logger)


# ============================================================================
# log_stage_summary 测试
# ============================================================================

class TestLogStageSummary:
    """测试 log_stage_summary() 功能。"""

    def test_basic_summary(self, tmp_dir):
        """基本摘要输出不应抛异常。"""
        log_dir = str(tmp_dir / 'logs_sum')
        logger = setup_logging('test_sum', log_dir)
        start_time = time.time() - 10  # 模拟 10 秒前开始
        log_stage_summary(logger, 'test_stage', start_time,
                          input_rows=1000, output_rows=500)

    def test_with_extra_info(self, tmp_dir):
        """含 extra_info 字典的摘要。"""
        log_dir = str(tmp_dir / 'logs_sum2')
        logger = setup_logging('test_sum2', log_dir)
        start_time = time.time()
        log_stage_summary(logger, 'test_stage', start_time,
                          extra_info={'去重数': 100, '保留率': '50%'})


# ============================================================================
# safe_save_preview_csv 测试
# ============================================================================

class TestSafeSavePreviewCsv:
    """测试 safe_save_preview_csv() 安全保存功能。"""

    def test_success(self, tmp_dir, sample_df):
        """正常保存 CSV 文件。"""
        path = str(tmp_dir / 'test_preview.csv')
        logger = setup_logging('csv_test', str(tmp_dir / 'logs'))
        safe_save_preview_csv(sample_df, path, logger)
        assert os.path.exists(path)
        loaded = pd.read_csv(path)
        assert len(loaded) == min(5000, len(sample_df))

    def test_no_crash_on_failure(self, tmp_dir, sample_df):
        """即使路径无效也不应崩溃。"""
        # 尝试写到一个不可写的路径
        logger = setup_logging('csv_fail', str(tmp_dir / 'logs'))
        # 这里用一个非常长的路径来模拟失败
        safe_save_preview_csv(sample_df, '', logger)  # 空路径


# ============================================================================
# save_dataset 测试
# ============================================================================

class TestSaveDataset:
    """测试 save_dataset() 双格式保存功能。"""

    def test_creates_parquet_and_csv(self, tmp_dir, sample_df):
        """应同时生成 parquet 和 csv 文件。"""
        output_dir = tmp_dir / 'output'
        output_dir.mkdir()
        parquet_path = str(output_dir / 'test_data.parquet')
        logger = setup_logging('save_test', str(tmp_dir / 'logs'))

        save_dataset(sample_df, parquet_path, logger)

        assert os.path.exists(parquet_path)
        csv_path = parquet_path.replace('.parquet', '.csv')
        assert os.path.exists(csv_path)

        # 验证 parquet 数据完整
        loaded = pd.read_parquet(parquet_path)
        assert len(loaded) == len(sample_df)


# ============================================================================
# run_stage 测试
# ============================================================================

class TestRunStage:
    """测试 run_stage() 子进程执行器。"""

    def test_script_not_found(self, tmp_dir):
        """脚本不存在时应返回 (False, 0.0)。"""
        logger = setup_logging('stage_test', str(tmp_dir / 'logs'))
        success, elapsed = run_stage(
            'nonexistent_script.py', '不存在的脚本', logger,
            base_dir=str(tmp_dir)
        )
        assert success is False
        assert elapsed == 0.0

    def test_successful_script(self, tmp_dir):
        """成功执行的脚本应返回 (True, elapsed)。"""
        # 创建一个简单的成功脚本
        script_path = tmp_dir / 'success_script.py'
        script_path.write_text('print("Success!")', encoding='utf-8')

        logger = setup_logging('stage_ok', str(tmp_dir / 'logs'))
        success, elapsed = run_stage(
            'success_script.py', '成功脚本', logger,
            base_dir=str(tmp_dir)
        )
        assert success is True
        assert elapsed > 0

    def test_failing_script(self, tmp_dir):
        """失败的脚本应返回 (False, elapsed)。"""
        script_path = tmp_dir / 'fail_script.py'
        script_path.write_text('raise RuntimeError("Fail")', encoding='utf-8')

        logger = setup_logging('stage_fail', str(tmp_dir / 'logs'))
        success, elapsed = run_stage(
            'fail_script.py', '失败脚本', logger,
            base_dir=str(tmp_dir)
        )
        assert success is False
        assert elapsed > 0
