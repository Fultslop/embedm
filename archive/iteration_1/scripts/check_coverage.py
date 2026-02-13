"""
Per-module coverage enforcement script.

Run AFTER tests to check per-module coverage thresholds.

Usage:
    py -m pytest tests/                    # Run tests (generates coverage.json)
    py scripts/check_coverage.py           # Check per-module thresholds

Or as a single command:
    py -m pytest tests/ && py scripts/check_coverage.py
"""

import json
import sys
import os


# Minimum coverage requirements per module
# Adjust these thresholds as coverage improves
MODULE_REQUIREMENTS = {
    # Core modules
    'src/embedm/resolver.py': 90,
    'src/embedm/parsing.py': 90,
    'src/embedm/extraction.py': 85,
    'src/embedm/plugin.py': 85,
    'src/embedm/registry.py': 75,
    'src/embedm/discovery.py': 90,
    'src/embedm/converters.py': 85,
    'src/embedm/config.py': 100,
    'src/embedm/validation.py': 90,
    'src/embedm/formatting.py': 70,
    'src/embedm/models.py': 75,
    'src/embedm/symbols.py': 70,
    'src/embedm/sandbox.py': 85,

    # Plugins
    'src/embedm_plugins/file_plugin.py': 90,
    'src/embedm_plugins/toc_plugin.py': 90,
    'src/embedm_plugins/layout_plugin.py': 60,
    'src/embedm_plugins/table_plugin.py': 60,

    # CLI - low threshold for now
    'src/embedm/cli.py': 13,
}

# Overall minimum coverage
OVERALL_MINIMUM = 70.0


def check_coverage():
    """Check per-module coverage against requirements."""

    coverage_file = os.path.join(os.path.dirname(__file__), '..', 'coverage.json')
    coverage_file = os.path.abspath(coverage_file)

    if not os.path.exists(coverage_file):
        print("Error: coverage.json not found.")
        print("Run tests first: py -m pytest tests/")
        return 1

    with open(coverage_file, 'r') as f:
        data = json.load(f)

    # Check overall coverage
    total_coverage = data['totals']['percent_covered']
    print(f"Overall coverage: {total_coverage:.1f}% (minimum: {OVERALL_MINIMUM}%)")
    print()

    # Check per-module coverage
    failures = []
    passes = []

    for module_path, min_coverage in sorted(MODULE_REQUIREMENTS.items()):
        # Normalize path separators for matching
        normalized = module_path.replace('/', os.sep)

        # Find the module in coverage data
        module_data = None
        for path, file_data in data['files'].items():
            if normalized in path or module_path in path:
                module_data = file_data
                break

        if not module_data:
            continue

        summary = module_data['summary']
        actual_coverage = summary['percent_covered']

        if actual_coverage < min_coverage:
            failures.append((module_path, actual_coverage, min_coverage))
        else:
            passes.append((module_path, actual_coverage, min_coverage))

    # Print results
    if passes:
        print(f"  Passed ({len(passes)} modules):")
        for module, actual, minimum in passes:
            name = os.path.basename(module)
            print(f"    {name:<30} {actual:5.1f}% >= {minimum}%")

    if failures:
        print()
        print(f"  FAILED ({len(failures)} modules):")
        for module, actual, minimum in failures:
            name = os.path.basename(module)
            print(f"    {name:<30} {actual:5.1f}% <  {minimum}%  !!!")

    print()

    # Final verdict
    exit_code = 0

    if total_coverage < OVERALL_MINIMUM:
        print(f"FAIL: Overall coverage {total_coverage:.1f}% < {OVERALL_MINIMUM}%")
        exit_code = 1

    if failures:
        print(f"FAIL: {len(failures)} module(s) below minimum coverage")
        exit_code = 1

    if exit_code == 0:
        print(f"OK: All {len(passes)} modules meet coverage requirements")

    return exit_code


if __name__ == '__main__':
    sys.exit(check_coverage())
