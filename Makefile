# PARUS project main Makefile
# Build requires:    Python-3 with `setuptools` `wheel` `build`
# Autodoc requires:  Python-3 with `sphinx` `sphinx-autodoc-typehints` `sphinx-design` `pydata-sphinx-theme`


# Semantic version number, allowed value `X.Y.Z` or `X.Y.ZrcN`
VERSION    ?=
# Clear API documentation builds switch for `gendoc`
CLRDOC     ?=

# OS based Python command
ifeq ($(OS),Windows_NT)
    PYTHON := py
else
    PYTHON := python3
endif

.PHONY: help clean semver build gendoc pack release


help:
	@echo PARUS project build automation
	@echo Valid targets ['clean', 'semver', 'build', 'gendoc', 'pack', 'release']

clean:
# Remove released package(s)
ifeq ($(OS),Windows_NT)
	@if exist "dist" rd /s /q "dist"
	@for /d %%i in ("*.egg-info") do (rd /s /q "%%i")
else
	@rm -rf "dist" "*.egg-info"
endif
# Remove API documentation build
	@$(MAKE) -C "doc/API" clean

semver:
	@echo [INFO] Setting package version...
	@$(PYTHON) "automation/environment/set_version.py" $(VERSION)

build:
	@echo [INFO] Building package...
	@$(PYTHON) -m build

gendoc:
	@echo [INFO] Generating API documentation...
	@$(MAKE) -C "doc/API" rebuild archive
ifdef CLRDOC
	@$(MAKE) -C "doc/API" clean
endif

# Archive and compress project files
pack:
# Generate API documentation
	@$(MAKE) gendoc CLRDOC=true
# Archive and compress
	@echo [INFO] Archiving and compressing project files...
ifeq ($(OS),Windows_NT)
	@if exist "parus.tar.gz" del /f "parus.tar.gz"
else
	@rm -f "parus.tar.gz"
endif
	@tar -czf "parus.tar.gz" \
        --option gzip:compression-level=9 \
        --exclude="__pycache__" \
        "parus" "automation" "doc" "README.md" "LICENSE" "Makefile" "pyproject.toml" ".gitattributes" ".gitignore"
	@echo [INFO] Project files packed

# Package release sequence
release: semver build gendoc
	@echo [INFO] Package released
