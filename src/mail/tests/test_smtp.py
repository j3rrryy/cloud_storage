from unittest.mock import patch

from config import load_config
from mail import get_smtp


@patch("mail.engine.SMTP")
def test_connect_smtp_service(mock_smtp):
    config = load_config().smtp
    get_smtp()
    mock_smtp.assert_called_once_with(
        hostname=config.hostname,
        port=config.port,
        username=config.username,
        password=config.password,
        use_tls=True,
    )
