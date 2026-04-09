# Makefile for Sphinx documentation

SPHINXOPTS    ?=
SPHINXAPIDOC  = sphinx-apidoc
SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
BUILDDIR      = build
PUBLISHDIR    = reference

.PHONY: help clean generate html rebuild publish

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

clean:
ifeq ($(OS),Windows_NT)
	@if exist "$(SOURCEDIR)\\_api" rd /s /q "$(SOURCEDIR)\\_api"
	@if exist "$(BUILDDIR)" rd /s /q "$(BUILDDIR)"
	@mkdir "$(BUILDDIR)"
else
	@rm -rf "$(SOURCEDIR)/_api" "$(BUILDDIR)"/*
endif

generate:
	@$(SPHINXAPIDOC) -o "$(SOURCEDIR)/_api" "../../../parus" -f -e -M

html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

rebuild: clean generate html

publish:
ifeq ($(OS),Windows_NT)
	@if exist "$(PUBLISHDIR)" rd /s /q "$(PUBLISHDIR)"
	@xcopy /s "$(BUILDDIR)\\html\\" "$(PUBLISHDIR)\\"
else
	@rm -rf "$(PUBLISHDIR)"
	@cp -r "$(BUILDDIR)/html" "$(PUBLISHDIR)/"
endif
