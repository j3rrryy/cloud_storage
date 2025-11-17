from litestar.plugins.prometheus import PrometheusConfig

from config import setup_prometheus
from settings import Settings


def test_setup_prometheus():
    prometheus_config = setup_prometheus()

    assert prometheus_config == PrometheusConfig(
        app_name=Settings.APP_NAME,
        prefix="gateway",
        excluded_http_methods=("PUT"),
        group_path=True,
    )
