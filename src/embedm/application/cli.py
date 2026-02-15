from __future__ import annotations

import argparse
import sys

from embedm.domain.status_level import Status, StatusLevel

from .configuration import Configuration


def parse_command_line_arguments(
    args: list[str] | None = None,
) -> tuple[Configuration, list[Status]]:
    """Parse command line arguments into a Configuration."""
    parser = _build_parser()
    parsed = parser.parse_args(args)

    errors = _validate(parsed)
    if errors:
        return Configuration(), errors

    input_value = parsed.input if parsed.input else _read_stdin()

    return Configuration(
        input=input_value,
        output_file=parsed.output_file,
        output_directory=parsed.output_dir,
    ), []


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for embedm CLI."""
    parser = argparse.ArgumentParser(prog="embedm", add_help=True)
    parser.add_argument("input", nargs="?", default=None, help="input file or directory")
    parser.add_argument("-o", "--output-file", default=None, help="output file path")
    parser.add_argument("-d", "--output-dir", default=None, help="output directory path")
    parser.add_argument("-c", "--config", default=None, help="configuration file path")
    return parser


def _validate(parsed: argparse.Namespace) -> list[Status]:
    """Validate parsed arguments and return errors."""
    errors: list[Status] = []

    if parsed.output_file and parsed.output_dir:
        errors.append(
            Status(StatusLevel.ERROR, "cannot specify both --output-file and --output-dir")
        )

    if not parsed.input and sys.stdin.isatty():
        errors.append(
            Status(StatusLevel.ERROR, "no input provided; pass a file/directory or pipe via stdin")
        )

    return errors


def _read_stdin() -> str:
    """Read all content from stdin."""
    return sys.stdin.read()
