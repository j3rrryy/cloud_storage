from unittest.mock import MagicMock, patch

from config import load_config
from storage.engine import _get_client


@patch("storage.engine.session")
def test_get_client(mock_session):
    config = load_config()
    mock_aiosession = MagicMock()
    mock_client = MagicMock()
    mock_session.get_session.return_value = mock_aiosession
    mock_aiosession.create_client = mock_client
    _get_client()

    mock_client.assert_called_once_with(
        "s3",
        endpoint_url=f"http://{config.minio.host}:{config.minio.port}",
        use_ssl=False,
        aws_access_key_id=config.minio.access_key,
        aws_secret_access_key=config.minio.secret_key,
    )
