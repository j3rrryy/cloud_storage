import os

from litestar.openapi.plugins import SwaggerRenderPlugin

from config import setup_openapi


def test_setup_openapi():
    openapi_config = setup_openapi()

    assert openapi_config.path == "/docs"
    assert openapi_config.title == os.environ["APP_NAME"]
    assert openapi_config.version == os.environ["VERSION"]
    assert openapi_config.security == [{"BearerToken": []}]
    assert len(openapi_config.render_plugins) == 1
    assert isinstance(openapi_config.render_plugins[0], SwaggerRenderPlugin)
