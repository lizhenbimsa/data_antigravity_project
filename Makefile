# news_process top-level Makefile (Plan-r3 P3-15)
# ====================================================================
# 提供数据生命周期 cleanup target (配合 docs/guides/data_lifecycle.md).
# Windows 用户用 ``mingw32-make`` 或 ``wsl make`` 执行;
# 纯 Python 替代见 ``news_process/scripts/cleanup.py`` (功能等价).
#
# 用法:
#   make help            -- 列出全部 target
#   make clean-cache     -- 删除 data/processed/_cache + _llm_cache.db (可恢复, 仅缓存)
#   make clean-backup    -- 删除 data/processed/_backup_*/  (修复锚点, 仅在 release 后用)
#   make clean-derived   -- 删除 stage 14+ 的 parquet/csv/dta (保留 stage 11/12 上游)
#   make purge-all       -- 上述三者并集 + logs/  (DANGER: 仅限完全重置)

.PHONY: help clean-cache clean-backup clean-derived clean-logs purge-all sizes

# 项目根 = Makefile 所在目录
ROOT       := $(dir $(realpath $(firstword $(MAKEFILE_LIST))))
PROCESSED  := $(ROOT)news_process/data/processed
LOGS       := $(ROOT)news_process/logs
PYTHON     ?= python

help:
	@echo "news_process Makefile targets (Plan-r3 P3-15 + round-3 review R7)"
	@echo "------------------------------------------------------------------"
	@echo "  clean-cache    : 删除 _cache/ + _llm_cache.db    (≈8700 MiB; 重跑 LLM/embedding stage 会全部 cache miss)"
	@echo "  clean-backup   : 删除 _backup_* 目录              (≈100 MiB; 仅在 issue #5 已 release 后执行)"
	@echo "  clean-derived  : 删除 stage 14+ parquet/csv/dta   (保留 stage 11/12 上游, 重跑 stage 14-51)"
	@echo "  clean-logs     : 清空 news_process/logs/          (≈?? MB)"
	@echo "  purge-all      : 上述全部 + logs                  (DANGER, 需 CONFIRM=yes 守门)"
	@echo ""
	@echo "  sizes          : 显示各 cleanup target 当前可释放体积"
	@echo ""
	@echo "DANGER 用法:"
	@echo "  CONFIRM=yes make purge-all     # 显式确认才能删 9.4 GiB"
	@echo ""
	@echo "对应文档: docs/guides/data_lifecycle.md"

sizes:
	@$(PYTHON) -m news_process.scripts.cleanup sizes

clean-cache:
	@echo "Plan-r3 P3-15: clean-cache -- 删除 LLM/Embedding API 缓冲 + SQLite cache"
	@$(PYTHON) -c "import shutil, pathlib; \
		c = pathlib.Path('$(PROCESSED)/_cache'); \
		(shutil.rmtree(c) if c.exists() else None); \
		print(f'  ✓ {c} 已删除' if not c.exists() else '  - skipped (不存在)'); \
		db = pathlib.Path('$(PROCESSED)/_llm_cache.db'); \
		(db.unlink() if db.exists() else None); \
		print(f'  ✓ {db} 已删除' if not db.exists() else '  - skipped (不存在)')"

clean-backup:
	@echo "Plan-r3 P3-15: clean-backup -- 删除 _backup_* 修复锚点"
	@$(PYTHON) -c "import shutil, glob, pathlib; \
		paths = glob.glob('$(PROCESSED)/_backup_*'); \
		[shutil.rmtree(p) for p in paths]; \
		print(f'  ✓ {len(paths)} 个 _backup_* 目录已删除') if paths else print('  - skipped (无 _backup_*)')"

clean-derived:
	@echo "Plan-r3 P3-15: clean-derived -- 删除 stage 14+ parquet/csv/dta (保留 stage 11/12 上游)"
	@$(PYTHON) -c "import re, os, glob; \
		patterns = [f'$(PROCESSED)/{stage}_*.{ext}' \
		            for stage in ['14', '15', '21', '22', '23', '24', '30', '31', '32', '32a', '33', '34', '35', '36', '37', '38', '38a', '38b', '39', '40', '41', '42', '43', '44', '45', '46', '47', '50', '51', '52', '53'] \
		            for ext in ['parquet', 'csv', 'dta']]; \
		files = [f for p in patterns for f in glob.glob(p)]; \
		[os.remove(f) for f in files]; \
		print(f'  ✓ {len(files)} 个 stage 14+ 派生文件已删除')"

clean-logs:
	@echo "Plan-r3 P3-15: clean-logs -- 清空 news_process/logs/"
	@$(PYTHON) -c "import shutil, pathlib; \
		p = pathlib.Path('$(LOGS)'); \
		(shutil.rmtree(p) if p.exists() else None); \
		p.mkdir(exist_ok=True); \
		print(f'  ✓ {p} 已清空')"

# Plan-r3 round-3 review R7: 与 cleanup.py purge-all --yes 守门保持一致 —
# Makefile 走 cleanup.py 而非依赖链, 避免 ``make purge-all`` 一键无确认地
# 删除 9.4 GiB 数据 (cache 8.5 GiB + backup 100 MiB + derived 480 MiB + logs).
# 用户必须显式 ``CONFIRM=yes make purge-all`` 才执行.
purge-all:
	@if [ "$(CONFIRM)" != "yes" ]; then \
	    echo "✗ purge-all 会删除 ~9.4 GiB 数据 (cache + backup + derived + logs), 且不可逆."; \
	    echo "  请用以下命令显式确认后再执行:"; \
	    echo "    CONFIRM=yes make purge-all"; \
	    exit 2; \
	fi
	@echo "→ purge-all 已确认, 开始执行..."
	@$(PYTHON) -m news_process.scripts.cleanup purge-all --yes
	@echo ""
	@echo "Plan-r3 P3-15: purge-all 完成"
	@echo "  下一次 ``run_pipeline_function.py`` 会从 stage 11/12 (上游) 重建全部派生数据."
