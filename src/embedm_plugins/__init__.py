"""
EmbedM Plugins
==============

This package contains built-in plugins for EmbedM. Plugins are independent
from the core embedm package and implement the EmbedPlugin interface.

Built-in plugins:
- FilePlugin: Handles file and code embeds (embed.file)
- LayoutPlugin: Handles multi-column/row layouts (embed.layout)
- TOCPlugin: Handles table of contents generation (embed.toc)
- TablePlugin: Handles tabular data embeds (embed.table)
- CommentPlugin: Handles comment blocks that are removed from output (embed.comment)

Plugins are automatically discovered and registered via entry points defined
in pyproject.toml. No manual registration is required.
"""

from .file_plugin import FilePlugin
from .layout_plugin import LayoutPlugin
from .toc_plugin import TOCPlugin
from .table_plugin import TablePlugin
from .comment_plugin import CommentPlugin

__all__ = ['FilePlugin', 'LayoutPlugin', 'TOCPlugin', 'TablePlugin', 'CommentPlugin']
