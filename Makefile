# PARUS project main Makefile

SEMVER    ?=    # Semantic version number, allowed value `X.Y.Z` or `X.Y.ZrcN`

.PHONY: help clean version build rebuild gendoc release

help:
	@echo PARUS project build automation, valid rules ['clean', 'version', 'build', 'rebuild', 'gendoc', 'release']

clean:
ifeq ($(OS),Windows_NT)
	@if exist "dist" rd /s /q "dist"
	@if exist "parus.egg-info" rd /s /q "parus.egg-info"
else
	@rm -rf "dist" "parus.egg-info"
endif

version:
ifeq ($(OS),Windows_NT)
	@py "automation/environment/set_version.py" $(SEMVER)
else
	@python3 "automation/environment/set_version.py" $(SEMVER)
endif

build:
ifeq ($(OS),Windows_NT)
	@py -m build
else
	@python3 -m build
endif

rebuild: clean build

gendoc:
	@$(MAKE) -C "doc/API" rebuild publish
	@$(MAKE) -C "doc/API" clean

release: version clean build gendoc
