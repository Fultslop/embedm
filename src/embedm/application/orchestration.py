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

    if len(errors) == 0:
        file_cache = FileCache(config.max_file_size, config.max_memory, ["./**"])
        plugin_registry = PluginRegistry()
        context = EmbedmContext(config, file_cache, plugin_registry)

        for file_name in enumerate(config.file_list):
            # todo check if output file already exists and is up to date in the target dir
            # if so there should be an entry in the file cache
            plan_root = create_plan(file_name[1], context)
            # todo present plan to user if needed
            if present_plan(plan_root, config.is_force_set):
                document = compile(plan_root, context)
                if not config.is_dry_run:
                    # todo write to target directory if provided else create a filename
                    file_cache.write(document, "todo: create path from config")
    else:
        # todo present errors to user
        present_arg_errors(["todo"])

    # todo present process complete
