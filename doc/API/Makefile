# Makefile for Sphinx documentation

SPHINXOPTS    ?=
SPHINXAPIDOC  = sphinx-apidoc
SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

.PHONY: help clean generate html rebuild

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

clean:
	@rm -rf $(BUILDDIR)/* $(SOURCEDIR)/_api

generate:
	@$(SPHINXAPIDOC) -o "$(SOURCEDIR)/_api" "../../../parus" -f -e -M

html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

rebuild: clean generate html
