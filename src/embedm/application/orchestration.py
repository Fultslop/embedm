from embedm.domain.directive import Directive
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.plugin_registry import PluginRegistry

from .cli import parse_command_line_arguments
from .compiler import compile
from .console import present_arg_errors, present_plan, present_title
from .embedm_context import EmbedmContext
from .planner import create_plan


def main() -> None:
    present_title()

    config, errors = parse_command_line_arguments()

    # todo if an output directory is defined and the config doesn't exist
    # in the output directory and we're not doing a dry-run safe the config

    if errors:
        # todo present errors to user
        present_arg_errors(["todo"])
        return

    file_cache = FileCache(config.max_file_size, config.max_memory, ["./**"])
    plugin_registry = PluginRegistry()
    context = EmbedmContext(config, file_cache, plugin_registry)

    for file_name in config.file_list:
        _process_file(file_name, context)

    # todo present process complete


def _process_file(file_name: str, context: EmbedmContext) -> None:
    """Plan and compile a single input file."""
    # todo check if output file already exists and is up to date in the target dir
    root_directive = Directive(type="root", source=file_name)
    content, file_errors = context.file_cache.get_file(file_name)
    if file_errors or content is None:
        # TODO: present file load errors
        return

    plan_root = create_plan(root_directive, content, 0, context)
    # todo present plan to user if needed
    if not present_plan(plan_root, context.config.is_force_set):
        return

    document = compile(plan_root, context)
    if not context.config.is_dry_run:
        # todo write to target directory if provided else create a filename
        context.file_cache.write(document, "todo: create path from config")
