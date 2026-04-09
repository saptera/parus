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
	@rm -rf $(BUILDDIR)/* $(SOURCEDIR)/_api

generate:
	@$(SPHINXAPIDOC) -o "$(SOURCEDIR)/_api" "../../../parus" -f -e -M

html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

rebuild: clean generate html

publish:
	@$cp -r "$(BUILDDIR)/html" "$(PUBLISHDIR)"
