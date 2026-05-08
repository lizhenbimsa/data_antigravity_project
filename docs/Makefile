# Makefile — news_process v2.1.0 文档站
# ======================================
#
# 标准目标:
#   make html        — 增量构建 HTML 至 ``_build/html/``
#   make clean       — 清空 ``_build/`` 以及 ``api/_autosummary/``
#   make rebuild     — clean + html (自零开始的完整构建)
#   make serve       — 在 http://localhost:8000 启动本地 HTTP 服务

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

.PHONY: help html clean rebuild serve linkcheck strict

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)
	@echo
	@echo "构建完成。请打开 $(BUILDDIR)/html/index.html"

clean:
	@rm -rf "$(BUILDDIR)" api/_autosummary api/generated
	@echo "已清理 $(BUILDDIR)/、api/_autosummary/、api/generated/"

rebuild: clean html

serve: html
	@echo "服务地址 http://localhost:8000  (Ctrl+C 停止)"
	@cd $(BUILDDIR)/html && python -m http.server 8000

# strict: 警告视为错误 (用于 Definition of Done 验收)。
strict:
	@$(SPHINXBUILD) -W --keep-going -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)

# linkcheck: 探测失效外链。
linkcheck:
	@$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)/linkcheck" $(SPHINXOPTS)
