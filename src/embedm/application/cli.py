from __future__ import annotations

import argparse
import sys
from pathlib import Path

from embedm.domain.status_level import Status, StatusLevel

from .application_resources import str_resources
from .configuration import Configuration, InputMode


def parse_command_line_arguments(
    args: list[str] | None = None,
) -> tuple[Configuration, list[Status]]:

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
        is_accept_all=parsed.accept_all,
        is_verbose=parsed.verbose,
    ), []


def _build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(prog="embedm", add_help=True)
    parser.add_argument("input", nargs="?", default=None, help="input file or directory")
    parser.add_argument("-o", "--output-file", default=None, help="output file path")
    parser.add_argument("-d", "--output-dir", default=None, help="output directory path")
    parser.add_argument("-c", "--config", default=None, help="configuration file path")
    parser.add_argument(
        "-A", "--accept-all", action="store_true", default=False, help="continue on errors without prompting"
    )
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="write diagnostic output to stderr")
    parser.add_argument("--init", nargs="?", const="", default=None, help="generate embedm-config.yaml in directory")
    return parser


def _validate(parsed: argparse.Namespace) -> list[Status]:

    errors: list[Status] = []

    if parsed.output_file and parsed.output_dir:
        errors.append(Status(StatusLevel.ERROR, str_resources.err_cli_file_and_dir_output))

    if parsed.output_file and _is_directory_input(parsed.input):
        errors.append(Status(StatusLevel.ERROR, str_resources.err_cli_out_file_and_dir_input))

    if not parsed.input and sys.stdin.isatty():
        errors.append(Status(StatusLevel.ERROR, str_resources.err_cli_no_input))

    return errors


def _resolve_input(parsed: argparse.Namespace) -> tuple[InputMode, str]:

    if not parsed.input:
        return InputMode.STDIN, sys.stdin.read()
    if parsed.output_dir or _is_directory_input(parsed.input):
        return InputMode.DIRECTORY, parsed.input
    return InputMode.FILE, parsed.input


def _is_directory_input(input_path: str | None) -> bool:

    if not input_path:
        return False
    if "*" in input_path:
        return True
    return Path(input_path).is_dir()
