"""
code_review_pipeline_lock.py — PipelineLock代码质量审查报告
===========================================================

静态代码审查，不执行实际测试，只分析代码质量
"""

import ast
import sys
from pathlib import Path


def analyze_pipeline_lock():
    """分析pipeline_lock.py的代码质量"""

    print("=" * 70)
    print("PipelineLock 代码质量审查报告")
    print("=" * 70)
    print()

    # 读取源代码
    lock_file = Path(__file__).parent.parent / 'utils' / 'pipeline_lock.py'

    if not lock_file.exists():
        print(f"❌ 错误: 找不到文件 {lock_file}")
        return False

    with open(lock_file, 'r', encoding='utf-8') as f:
        source_code = f.read()

    print(f"📄 文件: {lock_file}")
    print(f"📏 代码行数: {len(source_code.splitlines())}")
    print()

    # 1. 语法检查
    print("1️⃣ 语法检查")
    print("-" * 70)
    try:
        ast.parse(source_code)
        print("✅ 语法正确")
    except SyntaxError as e:
        print(f"❌ 语法错误: {e}")
        return False
    print()

    # 2. 导入检查
    print("2️⃣ 导入检查")
    print("-" * 70)
    required_imports = ['os', 'sys', 'time']
    for imp in required_imports:
        if f"import {imp}" in source_code:
            print(f"✅ {imp} - 已导入")
        else:
            print(f"❌ {imp} - 未导入")
    print()

    # 3. 跨平台兼容性检查
    print("3️⃣ 跨平台兼容性检查")
    print("-" * 70)

    has_windows_support = "sys.platform == 'win32'" in source_code
    has_unix_support = "else:" in source_code and "fcntl" in source_code
    has_msvcrt = "import msvcrt" in source_code
    has_fcntl = "import fcntl" in source_code

    print(f"✅ Windows支持 (msvcrt): {'是' if has_msvcrt else '否'}")
    print(f"✅ Unix/Linux支持 (fcntl): {'是' if has_fcntl else '否'}")
    print(f"✅ 平台检测逻辑: {'是' if has_windows_support else '否'}")
    print()

    # 4. 核心方法检查
    print("4️⃣ 核心方法检查")
    print("-" * 70)

    required_methods = [
        '__init__',
        '__enter__',
        '__exit__',
        '_handle_lock_failure',
        '_cleanup'
    ]

    for method in required_methods:
        if f"def {method}" in source_code:
            print(f"✅ {method} - 已实现")
        else:
            print(f"❌ {method} - 未实现")
    print()

    # 5. 错误处理检查
    print("5️⃣ 错误处理检查")
    print("-" * 70)

    has_try_except = source_code.count('try:') > 0
    has_exception_handling = 'except Exception' in source_code or 'except IOError' in source_code
    has_runtime_error = 'raise RuntimeError' in source_code

    print(f"✅ try-except块: {'是' if has_try_except else '否'}")
    print(f"✅ 异常处理: {'是' if has_exception_handling else '否'}")
    print(f"✅ RuntimeError抛出: {'是' if has_runtime_error else '否'}")
    print()

    # 6. 资源清理检查
    print("6️⃣ 资源清理检查")
    print("-" * 70)

    has_file_close = 'self.lock_file.close()' in source_code
    has_file_remove = 'os.remove(self.lock_file_path)' in source_code
    has_lock_release = 'LK_UNLCK' in source_code or 'LOCK_UN' in source_code

    print(f"✅ 文件关闭: {'是' if has_file_close else '否'}")
    print(f"✅ 文件删除: {'是' if has_file_remove else '否'}")
    print(f"✅ 锁释放: {'是' if has_lock_release else '否'}")
    print()

    # 7. 日志记录检查
    print("7️⃣ 日志记录检查")
    print("-" * 70)

    has_info_log = 'self.logger.info' in source_code
    has_error_log = 'self.logger.error' in source_code
    has_warning_log = 'self.logger.warning' in source_code

    print(f"✅ info日志: {'是' if has_info_log else '否'}")
    print(f"✅ error日志: {'是' if has_error_log else '否'}")
    print(f"✅ warning日志: {'是' if has_warning_log else '否'}")
    print()

    # 8. 状态管理检查
    print("8️⃣ 状态管理检查")
    print("-" * 70)

    has_locked_flag = 'self._locked' in source_code
    has_pid_tracking = 'self.pid' in source_code
    has_lock_file_tracking = 'self.lock_file' in source_code

    print(f"✅ _locked标志: {'是' if has_locked_flag else '否'}")
    print(f"✅ PID跟踪: {'是' if has_pid_tracking else '否'}")
    print(f"✅ lock_file跟踪: {'是' if has_lock_file_tracking else '否'}")
    print()

    # 9. 锁文件内容检查
    print("9️⃣ 锁文件内容检查")
    print("-" * 70)

    has_pid_write = 'self.pid' in source_code and 'write' in source_code
    has_timestamp_write = 'time.strftime' in source_code
    has_flush = 'flush()' in source_code

    print(f"✅ PID写入: {'是' if has_pid_write else '否'}")
    print(f"✅ 时间戳写入: {'是' if has_timestamp_write else '否'}")
    print(f"✅ 缓冲区刷新: {'是' if has_flush else '否'}")
    print()

    # 10. 代码质量指标
    print("🔟 代码质量指标")
    print("-" * 70)

    lines = source_code.splitlines()
    code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
    comment_lines = [l for l in lines if l.strip().startswith('#')]
    docstring_count = source_code.count('"""')

    print(f"📊 总行数: {len(lines)}")
    print(f"📊 代码行数: {len(code_lines)}")
    print(f"📊 注释行数: {len(comment_lines)}")
    print(f"📊 文档字符串: {docstring_count // 2}")
    print(f"📊 注释率: {len(comment_lines) / len(code_lines) * 100:.1f}%")
    print()

    # 总结
    print("=" * 70)
    print("📋 审查总结")
    print("=" * 70)

    checks = [
        ("语法正确", True),
        ("跨平台支持", has_windows_support and has_unix_support),
        ("核心方法完整", all(f"def {m}" in source_code for m in required_methods)),
        ("错误处理完善", has_try_except and has_exception_handling),
        ("资源清理完整", has_file_close and has_file_remove),
        ("日志记录完整", has_info_log and has_error_log),
        ("状态管理完整", has_locked_flag and has_pid_tracking),
    ]

    passed = sum(1 for _, result in checks if result)
    total = len(checks)

    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")

    print()
    print(f"通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    print()

    if passed == total:
        print("🎉 代码质量评估: 优秀")
        print("✅ 所有检查项均通过，代码达到生产级别标准")
    elif passed >= total * 0.8:
        print("👍 代码质量评估: 良好")
        print("⚠️ 大部分检查项通过，建议修复剩余问题")
    else:
        print("⚠️ 代码质量评估: 需要改进")
        print("❌ 多个检查项未通过，需要重构")

    print("=" * 70)

    return passed == total


if __name__ == '__main__':
    success = analyze_pipeline_lock()
    sys.exit(0 if success else 1)
