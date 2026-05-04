# Makefile — news_process v2.0.0 documentation site
# ==================================================
#
# Standard targets:
#   make html        — build HTML to ``_build/html/`` (incremental)
#   make clean       — wipe ``_build/`` and ``api/_autosummary/``
#   make rebuild     — clean + html (full from-scratch build)
#   make serve       — start a local HTTP server at http://localhost:8000

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
	@echo "Build finished. Open $(BUILDDIR)/html/index.html"

clean:
	@rm -rf "$(BUILDDIR)" api/_autosummary api/generated
	@echo "Cleaned $(BUILDDIR)/, api/_autosummary/, api/generated/"

rebuild: clean html

serve: html
	@echo "Serving on http://localhost:8000  (Ctrl+C to stop)"
	@cd $(BUILDDIR)/html && python -m http.server 8000

# Strict: warnings become errors (used for DoD verification).
strict:
	@$(SPHINXBUILD) -W --keep-going -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)

# Detect broken external links.
linkcheck:
	@$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)/linkcheck" $(SPHINXOPTS)
