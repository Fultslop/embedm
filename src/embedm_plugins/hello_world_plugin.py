from embedm.application.configuration import Configuration
from embedm.domain.directive import Directive
from embedm.domain.document import Document
from embedm.domain.status_level import Status, StatusLevel
from embedm.io.file_cache import FileCache
from embedm.plugins.plugin_base import PluginBase
from embedm.plugins.transformer_base import NoParams
from embedm_plugins.hello_world_transformer import HelloWorldTransformer


class HelloWorldPlugin(PluginBase):
    name = "hello world plugin"
    api_version = 1
    directive_type = "hello_world"

    def validate_directive(self, directive: Directive) -> list[Status]:
        if directive.type != self.directive_type:
            return [
                Status(
                    # is fatal because this indicates a programming error, not
                    # an input error
                    StatusLevel.FATAL,
                    f"directive type does not match. "
                    f"Expected '{self.directive_type}', provided: '{directive.type}'."
                )
            ]
        return []

    def transform(
        self,
        _directive: Directive,
        _document: Document | None = None,
        _file_cache: FileCache | None = None,
        _configuration: Configuration | None = None,
    ) -> str:

        transform = HelloWorldTransformer()
        return transform.execute(NoParams())
