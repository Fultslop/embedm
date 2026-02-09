"""
Plugin Registry and Dispatcher
===============================

This module provides the infrastructure for registering and routing embed
processing to plugin handlers.

## PluginRegistry

The registry stores plugin instances and maps embed types to plugins:

```python
from embedm.registry import PluginRegistry
from embedm.plugin import EmbedPlugin

registry = PluginRegistry()
registry.register(MyPlugin())

# Lookup plugin
plugin = registry.get_plugin('file', ProcessingPhase.EMBED)
```

## Dispatcher

The dispatcher routes embed processing to the appropriate plugin:

```python
from embedm.registry import dispatch_embed

result = dispatch_embed(
    embed_type='file',
    properties={'source': 'file.txt'},
    current_file_dir='/path/to/dir',
    processing_stack=set(),
    phase=ProcessingPhase.EMBED,
    registry=registry
)
```

## Fallback Behavior

If no plugin is registered for an embed type, the dispatcher falls back
to existing hard-coded handlers (process_file_embed, process_layout_embed).
This maintains backward compatibility.

## Default Registry

A default global registry is available:

```python
from embedm.registry import get_default_registry

registry = get_default_registry()
registry.register(MyPlugin())
```
"""

from typing import Dict, List, Optional, Set, TYPE_CHECKING
from .phases import ProcessingPhase

if TYPE_CHECKING:
    from .plugin import EmbedPlugin
    from .resolver import ProcessingContext


def discover_plugins(enabled_plugins: Optional[Set[str]] = None) -> List['EmbedPlugin']:
    """Discover plugins via entry points.

    Args:
        enabled_plugins: Optional set of plugin names to enable. If None, all discovered plugins are enabled.

    Returns:
        List of instantiated plugin objects

    Example:
        # Discover all plugins
        plugins = discover_plugins()

        # Discover only specific plugins
        plugins = discover_plugins(enabled_plugins={'file', 'toc'})
    """
    try:
        from importlib.metadata import entry_points
    except ImportError:
        # Python < 3.8 fallback
        from importlib_metadata import entry_points

    discovered = []

    # Discover plugins registered under "embedm.plugins" entry point group
    try:
        # Python 3.10+ API
        eps = entry_points(group='embedm.plugins')
    except TypeError:
        # Python 3.9 and earlier API
        eps = entry_points().get('embedm.plugins', [])

    for entry_point in eps:
        plugin_name = entry_point.name

        # Skip if filtering and this plugin is not enabled
        if enabled_plugins is not None and plugin_name not in enabled_plugins:
            continue

        try:
            # Load the plugin class
            plugin_class = entry_point.load()

            # Instantiate the plugin
            plugin_instance = plugin_class()

            discovered.append(plugin_instance)

        except Exception as e:
            # Log error but continue discovering other plugins
            import sys
            print(f"Warning: Failed to load plugin '{plugin_name}': {e}", file=sys.stderr)

    return discovered


class PluginRegistry:
    """Registry for managing embed plugins.

    Maps embed types to plugin instances. Supports plugins that handle
    multiple embed types and run in multiple phases.

    Example:
        registry = PluginRegistry()
        registry.register(FilePlugin())  # Handles 'file' and 'embed'
        registry.register(TOCPlugin())   # Handles 'toc' and 'table_of_contents'

        plugin = registry.get_plugin('file', ProcessingPhase.EMBED)
        if plugin:
            result = plugin.process(properties, ...)
    """

    def __init__(self):
        """Initialize empty registry."""
        # Map: (embed_type, phase) → plugin instance
        self._registry: Dict[tuple[str, ProcessingPhase], 'EmbedPlugin'] = {}

        # Track all registered plugins (for introspection)
        self._plugins: List['EmbedPlugin'] = []

    def register(self, plugin: 'EmbedPlugin') -> None:
        """Register a plugin for its declared embed types and phases.

        Args:
            plugin: Plugin instance to register

        Raises:
            ValueError: If a plugin is already registered for (type, phase) combination
        """
        for embed_type in plugin.embed_types:
            for phase in plugin.phases:
                key = (embed_type, phase)

                if key in self._registry:
                    existing = self._registry[key]
                    raise ValueError(
                        f"Plugin '{plugin.name}' conflicts with existing plugin "
                        f"'{existing.name}' for type '{embed_type}' in phase {phase.value}"
                    )

                self._registry[key] = plugin

        # Track plugin for introspection
        if plugin not in self._plugins:
            self._plugins.append(plugin)

    def get_plugin(
        self,
        embed_type: str,
        phase: ProcessingPhase
    ) -> Optional['EmbedPlugin']:
        """Get plugin for embed type and phase.

        Args:
            embed_type: Embed type string (e.g., 'file', 'toc')
            phase: Processing phase

        Returns:
            Plugin instance if registered, None otherwise
        """
        return self._registry.get((embed_type, phase))

    def get_all_plugins(self) -> List['EmbedPlugin']:
        """Get all registered plugins.

        Returns:
            List of unique plugin instances
        """
        return list(self._plugins)

    def get_plugins_for_phase(self, phase: ProcessingPhase) -> List['EmbedPlugin']:
        """Get all plugins registered for a specific phase.

        Args:
            phase: Processing phase

        Returns:
            List of plugins that run in this phase
        """
        plugins = []
        for (_, p), plugin in self._registry.items():
            if p == phase and plugin not in plugins:
                plugins.append(plugin)
        return plugins

    def is_registered(self, embed_type: str, phase: ProcessingPhase) -> bool:
        """Check if a handler is registered for embed type and phase.

        Args:
            embed_type: Embed type string
            phase: Processing phase

        Returns:
            True if handler registered, False otherwise
        """
        return (embed_type, phase) in self._registry


# Global default registry
_default_registry: Optional[PluginRegistry] = None


def get_default_registry(enabled_plugins: Optional[Set[str]] = None, auto_discover: bool = True) -> PluginRegistry:
    """Get or create the default plugin registry.

    Args:
        enabled_plugins: Optional set of plugin names to enable. If None, all discovered plugins are enabled.
        auto_discover: Whether to automatically discover and register plugins via entry points (default: True)

    Returns:
        Default PluginRegistry instance

    Note:
        On first call, plugins are automatically discovered via entry points and registered.
        Subsequent calls return the same registry instance unless set_default_registry() is called.

        If no plugins are discovered via entry points (e.g., during development), built-in
        plugins are registered manually as a fallback.
    """
    global _default_registry
    if _default_registry is None:
        _default_registry = PluginRegistry()

        # Auto-discover and register plugins on first initialization
        if auto_discover:
            plugins = discover_plugins(enabled_plugins)

            # Fallback: If no plugins discovered (e.g., development mode), manually register built-ins
            if not plugins:
                try:
                    from embedm_plugins import FilePlugin, LayoutPlugin, TOCPlugin, TablePlugin
                    plugins = [FilePlugin(), LayoutPlugin(), TOCPlugin(), TablePlugin()]
                except ImportError:
                    pass  # embedm_plugins not available

            for plugin in plugins:
                try:
                    _default_registry.register(plugin)
                except Exception as e:
                    # Log error but continue with other plugins
                    import sys
                    print(f"Warning: Failed to register plugin '{plugin.name}': {e}", file=sys.stderr)

    return _default_registry


def set_default_registry(registry: PluginRegistry) -> None:
    """Set the default plugin registry.

    Args:
        registry: PluginRegistry to use as default
    """
    global _default_registry
    _default_registry = registry


def dispatch_embed(
    embed_type: str,
    properties: Dict,
    current_file_dir: str,
    processing_stack: Set[str],
    context: Optional['ProcessingContext'] = None,
    phase: ProcessingPhase = ProcessingPhase.EMBED,
    registry: Optional[PluginRegistry] = None
) -> str:
    """Dispatch embed processing to plugin or fallback handler.

    Args:
        embed_type: Type of embed (e.g., 'file', 'toc')
        properties: YAML properties dict
        current_file_dir: Directory containing the markdown file
        processing_stack: Set of files being processed (cycle detection)
        context: Processing context with limits
        phase: Current processing phase
        registry: Plugin registry (optional, uses default if None)

    Returns:
        Processed content string or error message
    """
    # Use default registry if none provided
    if registry is None:
        registry = get_default_registry()

    # Filter out 'comment' property before passing to plugin
    # The 'comment' property is for documentation only
    properties_for_plugin = {k: v for k, v in properties.items() if k != 'comment'}

    # Try plugin registry
    plugin = registry.get_plugin(embed_type, phase)
    if plugin:
        return plugin.process(properties_for_plugin, current_file_dir, processing_stack, context)

    # Handle special cases
    if embed_type in ('toc', 'table_of_contents') and phase == ProcessingPhase.EMBED:
        return None  # Deferred to POST_PROCESS phase

    # Unknown embed type (no plugin registered)
    return f"> [!CAUTION]\n> **Embed Error:** Unknown embed type: `{embed_type}`"
