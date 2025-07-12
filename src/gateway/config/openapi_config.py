import os

from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin


def setup_openapi() -> OpenAPIConfig:
    return OpenAPIConfig(
        path="/docs",
        title=os.environ["APP_NAME"],
        version=os.environ["VERSION"],
        render_plugins=(SwaggerRenderPlugin(),),
        security=[{"BearerToken": []}],
    )
