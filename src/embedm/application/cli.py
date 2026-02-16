from __future__ import annotations

import argparse
import sys

from embedm.domain.status_level import Status, StatusLevel

from .configuration import Configuration, InputMode


def parse_command_line_arguments(
    args: list[str] | None = None,
) -> tuple[Configuration, list[Status]]:
    """Parse command line arguments into a Configuration."""
    parser = _build_parser()
    parsed = parser.parse_args(args)

    if parsed.init is not None:
        init_path = parsed.init if parsed.init else "."
        return Configuration(init_path=init_path), []

    errors = _validate(parsed)
    if errors:
        return Configuration(), errors

    input_mode, input_value = _resolve_input(parsed)

    return Configuration(
        input_mode=input_mode,
        input=input_value,
        output_file=parsed.output_file,
        output_directory=parsed.output_dir,
        config_file=parsed.config,
    ), []


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for embedm CLI."""
    parser = argparse.ArgumentParser(prog="embedm", add_help=True)
    parser.add_argument("input", nargs="?", default=None, help="input file or directory")
    parser.add_argument("-o", "--output-file", default=None, help="output file path")
    parser.add_argument("-d", "--output-dir", default=None, help="output directory path")
    parser.add_argument("-c", "--config", default=None, help="configuration file path")
    parser.add_argument("--init", nargs="?", const="", default=None, help="generate embedm-config.yaml in directory")
    return parser


def _validate(parsed: argparse.Namespace) -> list[Status]:
    """Validate parsed arguments and return errors."""
    errors: list[Status] = []

    if parsed.output_file and parsed.output_dir:
        errors.append(Status(StatusLevel.ERROR, "cannot specify both --output-file and --output-dir"))

    if not parsed.input and sys.stdin.isatty():
        errors.append(Status(StatusLevel.ERROR, "no input provided; pass a file/directory or pipe via stdin"))

    return errors


def _resolve_input(parsed: argparse.Namespace) -> tuple[InputMode, str]:
    """Determine input mode and value from parsed arguments."""
    if not parsed.input:
        return InputMode.STDIN, sys.stdin.read()
    if parsed.output_dir:
        return InputMode.DIRECTORY, parsed.input
    return InputMode.FILE, parsed.input
