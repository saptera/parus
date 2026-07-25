# Makefile for Sphinx documentation
# Requires: `sphinx` `sphinx-autodoc-typehints` `sphinx-design` `pydata-sphinx-theme`

SPHINXOPTS    ?=
SPHINXAPIDOC  = sphinx-apidoc
SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
GENDOCDIR     = $(SOURCEDIR)/_api
BUILDDIR      = build
PACKAGEDIR    = ../../parus
PUBLISHFILE   = api.tar.gz

# Sub-packages / modules to skip when generating the API stubs
APIDOC_EXCLUDE = \
    $(PACKAGEDIR)/scripts \
    $(PACKAGEDIR)/gui \
    $(PACKAGEDIR)/app/pac_ma.py \
    $(PACKAGEDIR)/app/pac_rt.py \
    $(PACKAGEDIR)/rt/app_rt.py \
    $(PACKAGEDIR)/rt/desg_apprtp.py

.PHONY: help clean generate html strict rebuild publish


help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

clean:
ifeq ($(OS),Windows_NT)
	@if exist "$(GENDOCDIR)" rd /s /q "$(GENDOCDIR)"
	@if exist "$(BUILDDIR)" rd /s /q "$(BUILDDIR)"
else
	@rm -rf "$(GENDOCDIR)" "$(BUILDDIR)"
endif

generate:
	@$(SPHINXAPIDOC) -f -e -M -T -q -o "$(GENDOCDIR)" "$(PACKAGEDIR)" $(APIDOC_EXCLUDE)

html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

strict:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" -n -W --keep-going $(SPHINXOPTS)

rebuild: clean generate html

publish:
ifeq ($(OS),Windows_NT)
	@if exist "$(PUBLISHFILE)" del /f "$(PUBLISHFILE)"
else
	@rm -f "$(PUBLISHFILE)"
endif
	@cd "$(BUILDDIR)/html" && tar -c -z --option gzip:compression-level=9 -f "$(CURDIR)/$(PUBLISHFILE)" *
