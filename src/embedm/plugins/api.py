"""Public API for embedm plugin authors.

Import everything you need from this single module:

    from embedm.plugins.api import PluginBase, Status, StatusLevel, PluginContext

For plugins that perform input validation:

    from embedm.plugins.api import PluginBase, ValidationResult, Directive, Status, StatusLevel
"""

from embedm.domain.directive import Directive
from embedm.domain.document import Fragment
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel
from embedm.plugins.normalization_base import NormalizationResult
from embedm.plugins.plugin_base import PluginBase
from embedm.plugins.plugin_configuration import PluginConfiguration
from embedm.plugins.plugin_context import PluginContext

__all__ = [
    "Directive",
    "Fragment",
    "PlanNode",
    "PluginBase",
    "PluginConfiguration",
    "PluginContext",
    "Status",
    "StatusLevel",
    "NormalizationResult",
]
