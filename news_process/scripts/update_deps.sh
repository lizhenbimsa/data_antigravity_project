#!/bin/bash
# 更新依赖锁定文件
# 用法: ./scripts/update_deps.sh

set -e

echo "🔄 更新依赖锁定文件..."
pip-compile pyproject.toml --output-file=requirements.lock --resolver=backtracking --upgrade

echo "✅ 依赖锁定文件已更新"
echo "📝 请检查 git diff requirements.lock 确认变更"
echo "🧪 建议运行全量测试: pytest"
