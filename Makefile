# Note: requires 'make' to be installed, `eg choco install make`

# Variables for cross-platform flexibility
PYTHON = py
SRC_DIR = ./src/embedm/

.PHONY: all update_snapshots regression manual context test clean pre-commit install lint static-analysis ok

# Default target
all: update_snapshots

# --- Snapshot Management ---

update_snapshots: regression manual context

regression:
	@echo Running regression tests (Expected failures allowed)...
	-$(PYTHON) $(SRC_DIR) './tests/regression/src/**' -d ./tests/regression/snapshot/ -A

manual:
	$(PYTHON) $(SRC_DIR) './doc/manual/src/**' -d ./doc/manual/compiled/

context:
	$(PYTHON) $(SRC_DIR) ./doc/project/agent_context.src.md -o ./doc/project/agent_context.md

# --- Development Quality Checks ---

test:
	pytest ./tests/

install:
	$(PYTHON) -m pip install -e .

lint:
	ruff format ./src && ruff check --fix ./src

static-analysis:
	mypy ./src && radon cc ./src/ -s -a

# --- Precommit

pre-commit: install update_snapshots test lint static-analysis ok

pre-commit-no-install: update_snapshots test lint static-analysis ok

# --- Utilities ---

clean:
	@$(PYTHON) -c "import os, glob; [os.remove(f) for f in glob.glob('./doc/manual/compiled/*')]"
	@echo Cleaned compiled documentation.

ok:
	@$(PYTHON) -c "print('\n' + '='*40 + '\n ALL CHECKS PASSED: Ready to commit!\n' + '='*40)"