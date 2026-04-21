# PARUS project main Makefile
# Build requires:    Python-3 with `setuptools` `wheel` `build`
# Autodoc requires:  Python-3 with `sphinx` `sphinx-autodoc-typehints` `sphinx-design` `pydata-sphinx-theme`


# Semantic version number, allowed value `X.Y.Z` or `X.Y.ZrcN`
VERSION    ?=

# OS based Python command
ifeq ($(OS),Windows_NT)
    PYTHON := py
else
    PYTHON := python3
endif

.PHONY: help clean semver build gendoc clrdoc release solopack


help:
	@echo PARUS project build automation
	@echo Valid targets ['clean', 'semver', 'build', 'gendoc', 'clrdoc', 'release', 'solopack']

clean:
ifeq ($(OS),Windows_NT)
	@if exist "dist" rd /s /q "dist"
	@if exist "parus.egg-info" rd /s /q "parus.egg-info"
else
	@rm -rf "dist" "parus.egg-info"
endif

semver:
	@$(PYTHON) "automation/environment/set_version.py" $(VERSION)

build:
	@$(PYTHON) -m build

gendoc:
	@$(MAKE) -C "doc/API" rebuild publish

clrdoc:
	@$(MAKE) -C "doc/API" clean

# Package release sequence
release: semver build gendoc

# Clean and single version project packing
solopack: clean semver build gendoc clrdoc
