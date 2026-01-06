from unittest.mock import patch

from argon2 import profiles

from config import setup_password_hasher


@patch("config.password_hasher_config.PasswordHasher")
def test_setup_password_hasher(mock_password_hasher):
    setup_password_hasher()

    mock_password_hasher.from_parameters.assert_called_once_with(
        profiles.RFC_9106_LOW_MEMORY
    )
