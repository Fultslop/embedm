# Note: requires 'make' to be installed, e.g., 'choco install make' on Windows

# --- OS Detection ---
ifeq ($(OS),Windows_NT)
    PYTHON ?= py
else
    PYTHON ?= python3
endif

# --- Variables ---
# We use the module name for 'python -m' execution
MODULE = embedm
# We keep the source directory for tools like ruff/mypy
SRC_DIR = ./src/embedm/

.PHONY: all update_snapshots regression manual context test clean pre-commit \
        pre-commit-no-install install lint static-analysis ok copy-read-me

# Default target
all: update_snapshots

# --- Snapshot Management ---

update_snapshots: regression manual context

regression:
	@echo "Running regression tests (Expected failures allowed)..."
	-$(PYTHON) -m $(MODULE) './tests/regression/src/**' -d ./tests/regression/snapshot/ -A

manual:
	@echo "Building manual..."
	$(PYTHON) -m $(MODULE) './doc/manual/src/*' -d ./doc/manual/compiled/
	$(MAKE) copy-read-me
	
copy-read-me:   
	@echo "Copying README to root..."
	$(PYTHON) -c "import shutil; shutil.copy2('./doc/manual/compiled/README.md', './README.md')"

context:
	@echo "Updating agent context..."
	$(PYTHON) -m $(MODULE) ./doc/project/agent_context.src.md -o ./doc/project/agent_context.md

# --- Development Quality Checks ---

test:
	uv run pytest ./tests/

install:
	$(PYTHON) -m pip install -e .

lint:
	ruff format ./src && ruff check --fix ./src

static-analysis:
	mypy ./src && radon cc ./src/ -s -a

# --- Precommit ---

pre-commit: install update_snapshots test lint static-analysis ok

pre-commit-no-install: update_snapshots test lint static-analysis ok

# --- Utilities ---

clean:
	@$(PYTHON) -c "import os, glob; [os.remove(f) for f in glob.glob('./doc/manual/compiled/*')]"
	@echo "Cleaned compiled documentation."

ok:
	@$(PYTHON) -c "print('\n' + '='*40 + '\n ALL CHECKS PASSED: Ready to commit!\n' + '='*40)"