PYTHON ?= python3
UV ?= uv
PIP ?= $(PYTHON) -m pip
VENV ?= .venv
VENV_PYTHON = $(VENV)/bin/python
MAIN ?= main.py

MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

.PHONY: install install-pip run debug clean lint lint-strict format check-modern

install:
	@if command -v $(UV) >/dev/null 2>&1; then \
		$(UV) sync --dev; \
	else \
		$(PYTHON) -m venv $(VENV); \
		$(VENV_PYTHON) -m pip install --upgrade pip; \
		$(VENV_PYTHON) -m pip install -e ".[dev]"; \
	fi

install-pip:
	$(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -e ".[dev]"

run:
	@if command -v $(UV) >/dev/null 2>&1; then \
		$(UV) run python $(MAIN); \
	else \
		$(VENV_PYTHON) $(MAIN); \
	fi

debug:
	@if command -v $(UV) >/dev/null 2>&1; then \
		$(UV) run python -m pdb $(MAIN); \
	else \
		$(VENV_PYTHON) -m pdb $(MAIN); \
	fi

clean:
	find . -type d \( -name "__pycache__" -o -name ".mypy_cache" -o -name ".ruff_cache" \
		-o -name ".pytest_cache" -o -name ".ty" \) -prune -exec rm -rf {} +
	find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete

lint:
	@if command -v $(UV) >/dev/null 2>&1; then \
		$(UV) run flake8 . && $(UV) run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs; \
	else \
		$(VENV_PYTHON) -m flake8 . && $(VENV_PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs; \
	fi

lint-strict:
	@if command -v $(UV) >/dev/null 2>&1; then \
		$(UV) run flake8 . && $(UV) run mypy . --strict; \
	else \
		$(VENV_PYTHON) -m flake8 . && $(VENV_PYTHON) -m mypy . --strict; \
	fi

format:
	@if command -v $(UV) >/dev/null 2>&1; then \
		$(UV) run ruff format . && $(UV) run ruff check --fix .; \
	else \
		$(VENV_PYTHON) -m ruff format . && $(VENV_PYTHON) -m ruff check --fix .; \
	fi

check-modern:
	@if command -v $(UV) >/dev/null 2>&1; then \
		$(UV) run ruff check . && $(UV) run ty check .; \
	else \
		$(VENV_PYTHON) -m ruff check . && $(VENV_PYTHON) -m ty check .; \
	fi
