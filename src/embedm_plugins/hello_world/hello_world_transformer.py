from embedm.plugins.transformer_base import NoParams, TransformerBase


class HelloWorldTransformer(TransformerBase[NoParams]):
    params_type = NoParams

    def execute(self, _params: NoParams) -> str:
        return "hello embedded world!"
