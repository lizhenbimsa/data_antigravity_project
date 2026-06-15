"""
tests/test_helpers.py — core 辅助函数单元测试 (历史名 utils/helpers.py, 现拆分至
core/{config,logging,reporting,stage}.py)
==================================================
"""

import logging
import os
import sys
import time

import pandas as pd
import pytest

# Phase 5c-2: 注入项目父目录, 让 ``news_process.core.*`` 在包模式下可解析
_PROJECT_PARENT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import (
    log_and_time,
    log_memory_usage,
    log_stage_summary,
    setup_logging,
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
        """应自动创建日志文件 (扁平布局 ``<log_dir>/<stage>.log``)。

        2026-06-15: setup_logging 改为只写扁平的 ``<log_dir>/<stage>.log``,
        不再按 NEWS_PROCESS_RUN_ID 分 per-run 子目录 (只保留最新一次运行,
        新覆盖旧)。因此无论 NEWS_PROCESS_RUN_ID 是否已被先行 import 的
        test_dag_consistency 等设置, 路径都固定为扁平布局。
        """
        log_dir = str(tmp_dir / 'logs')
        logger = setup_logging('test_stage', log_dir)
        logger.info("测试消息")
        expected = os.path.join(log_dir, 'test_stage.log')
        assert os.path.exists(expected), (
            f"Log file not at expected flat path {expected!r}"
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

    # ------------------------------------------------------------------
    # 2026-05-30 audit (delay=True 根因修复 + LOG-1 截断回归):
    #   C3-1 守护 "未写日志则不建文件" (delay 的核心目的);
    #   LOG-1 守护 file_mode='w' 跨运行截断 (stdlib 把 mode='w' 强制改 'a',
    #   故由 _DelayedTruncatingRotatingHandler 在 _open() 层截断)。
    # ------------------------------------------------------------------

    def test_delay_no_file_until_first_log(self, tmp_dir, monkeypatch):
        """delay=True: setup 后、首条日志写入前不应创建文件 (C3-1; 空 log 根因守护)。

        与 test_creates_log_file 互补: 后者验证"写后有文件", 本测试验证
        "未写则无文件", 正面锁死 delay=True 的目的 (仅 import / 早退不留空 log)。
        """
        monkeypatch.delenv("NEWS_PROCESS_RUN_ID", raising=False)
        log_dir = str(tmp_dir / 'logs_delay')
        logger = setup_logging('delay_probe', log_dir)
        log_file = os.path.join(log_dir, 'delay_probe.log')
        assert not os.path.exists(log_file), (
            "setup 后未写日志即创建了文件, delay=True 失效 (空 log 会回归)"
        )
        logger.info("现在才有内容")
        for h in logger.handlers:
            h.flush()
        assert os.path.exists(log_file)
        assert os.path.getsize(log_file) > 0

    def test_file_mode_w_truncates_stale_file(self, tmp_dir, monkeypatch):
        """file_mode='w': 首次写入应截断上一次运行遗留的内容 (LOG-1 回归守护)。

        模拟"上一次运行遗留非空日志", 断言本次 'w' 运行将其截断 —— 防止
        stdlib 把 mode='w' 强制改 'a' 导致同名日志跨运行累积。
        """
        monkeypatch.delenv("NEWS_PROCESS_RUN_ID", raising=False)
        log_dir = str(tmp_dir / 'logs_trunc')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'trunc_probe.log')
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("STALE_FROM_PREVIOUS_RUN\n")

        logger = setup_logging('trunc_probe', log_dir, file_mode='w')
        logger.info("FRESH_RUN_LINE")
        for h in logger.handlers:
            h.flush()

        content = open(log_file, encoding='utf-8').read()
        assert "FRESH_RUN_LINE" in content
        assert "STALE_FROM_PREVIOUS_RUN" not in content, (
            "file_mode='w' 首次写入应截断遗留内容 (LOG-1: stdlib 把 mode 改 'a' 致截断失效)"
        )

    def test_file_mode_a_appends_to_stale_file(self, tmp_dir, monkeypatch):
        """file_mode='a': 应保留遗留内容并追加, 不截断 (LOG-1 反向守护)。"""
        monkeypatch.delenv("NEWS_PROCESS_RUN_ID", raising=False)
        log_dir = str(tmp_dir / 'logs_append')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'append_probe.log')
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("PRESERVED_PRIOR\n")

        logger = setup_logging('append_probe', log_dir, file_mode='a')
        logger.info("APPENDED_LINE")
        for h in logger.handlers:
            h.flush()

        content = open(log_file, encoding='utf-8').read()
        assert "PRESERVED_PRIOR" in content, "file_mode='a' 不应截断遗留内容"
        assert "APPENDED_LINE" in content


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

    # quality-hardening Round 20 (2026-05-27): logging.py 94.97% → ~100%
    # missing 237-243 (__len__ + arbitrary object 分支) + 260 (_format_bytes MB)

    def test_log_and_time_result_with_len_branch(self, tmp_dir):
        """result 是 list/dict (有 __len__ 但非 DataFrame/int) → 走 line 237-241."""
        log_dir = str(tmp_dir / 'logs_len')
        logger = setup_logging('test_len', log_dir)

        @log_and_time(logger)
        def returns_list():
            return [1, 2, 3, 4, 5]

        result = returns_list()
        assert result == [1, 2, 3, 4, 5]

    def test_log_and_time_result_arbitrary_object_branch(self, tmp_dir):
        """result 无 __len__ → 走 else line 242-243."""
        log_dir = str(tmp_dir / 'logs_obj')
        logger = setup_logging('test_obj', log_dir)

        class Foo:
            pass

        @log_and_time(logger)
        def returns_obj():
            return Foo()

        result = returns_obj()
        assert isinstance(result, Foo)


def test_format_bytes_mb_branch():
    """_format_bytes b < 1 GB → MB 格式 (logging.py:260)."""
    from news_process.core.logging import _format_bytes
    assert _format_bytes(500 * 1024 * 1024) == "500.0 MB"
    assert _format_bytes(1024 * 1024) == "1.0 MB"


def test_format_bytes_gb_branch():
    """_format_bytes b >= 1 GB → GB 格式 (logging.py:258-259)."""
    from news_process.core.logging import _format_bytes
    assert "GB" in _format_bytes(2 * 1024 ** 3)


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

    def test_pythonhashseed_forced_to_zero(self, tmp_dir):
        """audit-fixes 2026-05-29 (L2/L3): run_stage 必须把子进程的
        PYTHONHASHSEED 强制为 '0' (确定性契约), 即使父环境已 export 了非零值。

        守卫 L2 (env.setdefault → env[...] = '0' force) 与 L3 (该契约此前无测试
        保护, 重构可静默回退)。jieba+frozenset 边界 token 的确定性依赖此 seed。
        """
        import os as _os
        out_file = tmp_dir / 'seed.txt'
        script_path = tmp_dir / 'seed_script.py'
        script_path.write_text(
            'import os\n'
            'open(' + repr(str(out_file)) + ', "w", encoding="utf-8")'
            '.write(os.environ.get("PYTHONHASHSEED", "MISSING"))\n',
            encoding='utf-8',
        )
        logger = setup_logging('stage_seed', str(tmp_dir / 'logs'))
        # 故意在父环境设非零值, 验证子进程仍被强制为 '0' (force, 非 setdefault)
        old = _os.environ.get('PYTHONHASHSEED')
        _os.environ['PYTHONHASHSEED'] = '12345'
        try:
            success, _ = run_stage('seed_script.py', '种子脚本', logger,
                                   base_dir=str(tmp_dir))
        finally:
            if old is None:
                _os.environ.pop('PYTHONHASHSEED', None)
            else:
                _os.environ['PYTHONHASHSEED'] = old
        assert success is True
        assert out_file.read_text(encoding='utf-8').strip() == '0'
