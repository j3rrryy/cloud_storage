from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin

from settings import Settings


def setup_openapi() -> OpenAPIConfig:
    return OpenAPIConfig(
        path="/docs",
        title=Settings.APP_NAME,
        version=Settings.VERSION,
        render_plugins=(SwaggerRenderPlugin(),),
        security=[{"BearerToken": []}],
    )
