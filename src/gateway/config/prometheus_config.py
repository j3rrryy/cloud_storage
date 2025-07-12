import os

from litestar.plugins.prometheus import PrometheusConfig


def setup_prometheus() -> PrometheusConfig:
    return PrometheusConfig(
        app_name=os.environ["APP_NAME"],
        prefix="gateway",
        excluded_http_methods=("PUT"),
        group_path=True,
    )
