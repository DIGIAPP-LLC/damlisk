VERSION ?= 0.0.1
PYTHON ?= python3

DARS_REF ?= main
DARS_ONLY ?=
DPM ?= $(shell command -v dpm || echo $(HOME)/.dpm/bin/dpm)
DAML_SDK ?= 3.4.8
VENV ?= .venv
LICENSE_MARKER := Licensed under the Apache License, Version 2.0

.PHONY: ci dpm dars license-check init dev-init test lint mypy black flake8 isort build dev dev-release release clean clean-pyc clean-build clean-test

init:
	$(PYTHON) setup.py install

dev-init:
	$(PYTHON) -m pip install -e . --group dev

ci:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install -q -U pip
	$(VENV)/bin/pip install -q -e . --group dev
	$(MAKE) dpm dars PYTHON=$(VENV)/bin/python
	$(MAKE) license-check
	PATH="$(CURDIR)/$(VENV)/bin:$$PATH" $(MAKE) lint test
	git diff --exit-code -- damlisk tests setup.py

dpm:
	[ -x "$(DPM)" ] || curl -sSL https://get.digitalasset.com/install/install.sh | sh
	$(DPM) install $(DAML_SDK)

dars:
	$(PYTHON) scripts/fetch_dars.py --out examples/dars --ref $(DARS_REF) --only "$(DARS_ONLY)"
	@for dir in examples/vulnerable/*/; do \
		name=$$(basename $$dir); \
		echo "building $$name"; \
		log=$$(cd $$dir && $(DPM) build -o $$name.dar 2>&1) || { echo "$$log"; exit 1; }; \
		rm -rf $$dir.daml; \
	done

license-check:
	@missing=$$(git ls-files --cached --others --exclude-standard -- setup.py 'damlisk/*.py' 'tests/*.py' 'scripts/*.py' \
		| grep -v '^damlisk/version.py$$' \
		| while read -r file; do head -n 20 "$$file" | grep -q "$(LICENSE_MARKER)" || echo "$$file"; done); \
	if [ -n "$$missing" ]; then \
		echo "Missing Apache-2.0 license header:"; echo "$$missing"; exit 1; \
	fi; \
	echo "All Python files have the Apache-2.0 license header."

test:
	pytest

lint: mypy black flake8 isort

mypy:
	mypy -p damlisk

black:
	black damlisk/ tests/ setup.py

flake8: black
	flake8 damlisk/ tests/

isort: black
	isort damlisk/ tests/ setup.py

build: clean
	$(PYTHON) -m build
	ls -la dist/

dev:
	SETUPTOOLS_SCM_PRETEND_VERSION=$(VERSION) $(MAKE) build

dev-release:
	SETUPTOOLS_SCM_PRETEND_VERSION=$(VERSION) \
	$(PYTHON) -m pip install --no-deps --force-reinstall -e .

release: build
	twine check dist/*

clean: clean-build clean-pyc clean-test

clean-build:
	@echo Cleaning python build files...
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info
	@rm -f damlisk/version.py damlisk/damlisk_git_commithash.txt

clean-pyc:
	@echo Cleaning python files...
	@find . -path ./.venv -prune -o -name '*.pyc' -exec rm -f {} +
	@find . -path ./.venv -prune -o -name '*.pyo' -exec rm -f {} +
	@find . -path ./.venv -prune -o -name '__pycache__' -exec rm -rf {} +

clean-test:
	@echo Cleaning test files...
	@find . -path ./.venv -prune -o -name 'htmlcov' -exec rm -rf {} +
	@rm -fr coverage.xml
	@rm -fr .coverage
	@rm -fr .pytest_cache/
	@rm -fr .mypy_cache/
