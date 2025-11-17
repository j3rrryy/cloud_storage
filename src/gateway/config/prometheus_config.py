from litestar.plugins.prometheus import PrometheusConfig

from settings import Settings


def setup_prometheus() -> PrometheusConfig:
    return PrometheusConfig(
        app_name=Settings.APP_NAME,
        prefix="gateway",
        excluded_http_methods=("PUT"),
        group_path=True,
    )
