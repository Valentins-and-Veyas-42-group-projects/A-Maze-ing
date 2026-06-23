PYTHON ?= python3
UV ?= uv
PIP ?= $(PYTHON) -m pip
VENV ?= .venv
VENV_PYTHON = $(VENV)/bin/python
MAIN ?= a_maze_ing.py
ARGS ?= config.txt

MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
FLAKE8_FLAGS = --max-line-length=100 --exclude=.venv,.git,__pycache__,.mypy_cache,.ruff_cache,.pytest_cache,.ty,dist,build,test_env,test_venv,test_install
FLAKE8 = sh -c 'if command -v flake8 >/dev/null 2>&1; then flake8 "$$@"; elif command -v uvx >/dev/null 2>&1; then uvx flake8 "$$@"; elif command -v $(UV) >/dev/null 2>&1; then $(UV) run flake8 "$$@"; else $(VENV_PYTHON) -m flake8 "$$@"; fi' --
MYPY = sh -c 'if command -v mypy >/dev/null 2>&1; then mypy "$$@"; elif command -v uvx >/dev/null 2>&1; then uvx mypy "$$@"; elif command -v $(UV) >/dev/null 2>&1; then $(UV) run mypy "$$@"; else $(VENV_PYTHON) -m mypy "$$@"; fi' --
RUFF = sh -c 'if command -v ruff >/dev/null 2>&1; then ruff "$$@"; elif command -v uvx >/dev/null 2>&1; then uvx ruff "$$@"; elif command -v $(UV) >/dev/null 2>&1; then $(UV) run ruff "$$@"; else $(VENV_PYTHON) -m ruff "$$@"; fi' --
TY = sh -c 'if command -v ty >/dev/null 2>&1; then ty "$$@"; elif command -v uvx >/dev/null 2>&1; then uvx ty "$$@"; elif command -v $(UV) >/dev/null 2>&1; then $(UV) run ty "$$@"; else $(VENV_PYTHON) -m ty "$$@"; fi' --
PYTEST = sh -c 'if command -v pytest >/dev/null 2>&1; then pytest "$$@"; elif command -v uvx >/dev/null 2>&1; then uvx pytest "$$@"; elif command -v $(UV) >/dev/null 2>&1; then $(UV) run pytest "$$@"; else $(VENV_PYTHON) -m pytest "$$@"; fi' --

.PHONY: install install-pip build-package build run debug clean lint lint-strict format check-modern typecheck test

build: build-package

build-package:
	@if command -v $(UV) >/dev/null 2>&1; then \
		$(UV) build; \
	else \
		$(PYTHON) -m pip install --upgrade build; \
		$(PYTHON) -m build; \
	fi
	cp dist/mazegen-*.whl .
	cp dist/mazegen-*.tar.gz .

install: build-package
	@if command -v $(UV) >/dev/null 2>&1; then \
		$(UV) sync --dev; \
	else \
		$(PYTHON) -m venv $(VENV); \
		$(VENV_PYTHON) -m pip install --upgrade pip; \
		$(VENV_PYTHON) -m pip install -e ".[dev]"; \
	fi

install-pip: build-package
	$(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -e ".[dev]"

run:
	@if command -v $(UV) >/dev/null 2>&1; then \
		$(UV) run python $(MAIN) $(ARGS); \
	else \
		$(VENV_PYTHON) $(MAIN) $(ARGS); \
	fi

clean:
	find . -type d \( -name "__pycache__" -o -name ".mypy_cache" -o -name ".ruff_cache" \
		-o -name ".pytest_cache" -o -name ".ty" \) -prune -exec rm -rf {} +
	find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete
	rm -rf dist build mazegen.egg-info mazegen-*.whl mazegen-*.tar.gz


lint:
	$(FLAKE8) . $(FLAKE8_FLAGS)
	$(MYPY) mazegen $(MYPY_FLAGS)

lint-strict:
	$(FLAKE8) . $(FLAKE8_FLAGS)
	$(MYPY) mazegen

format:
	$(RUFF) format .
	$(RUFF) check --fix .

check-modern:
	$(RUFF) check .
	$(TY) check .

typecheck:
	$(MYPY) mazegen $(MYPY_FLAGS)
	$(TY) check .
	

test:
	$(PYTEST)
