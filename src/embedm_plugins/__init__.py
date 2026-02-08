"""
EmbedM Plugins
==============

This package contains built-in plugins for EmbedM. Plugins are independent
from the core embedm package and implement the EmbedPlugin interface.

Built-in plugins:
- FilePlugin: Handles file and code embeds (embed.file)
- LayoutPlugin: Handles multi-column/row layouts (embed.layout)
- TOCPlugin: Handles table of contents generation (embed.toc)

Built-in plugins are automatically registered in the default registry when
this package is imported.
"""

from .file_plugin import FilePlugin
from .layout_plugin import LayoutPlugin
from .toc_plugin import TOCPlugin

__all__ = ['FilePlugin', 'LayoutPlugin', 'TOCPlugin']


def register_builtin_plugins():
    """Register all built-in plugins in the default registry.

    This function is called automatically when embedm_plugins is imported.
    It registers all built-in plugins so they're available for use.
    """
    from embedm.registry import get_default_registry

    registry = get_default_registry()

    # Register built-in plugins
    registry.register(FilePlugin())
    registry.register(LayoutPlugin())
    registry.register(TOCPlugin())


# Auto-register built-in plugins when package is imported
register_builtin_plugins()
