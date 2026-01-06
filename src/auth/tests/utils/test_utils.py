from datetime import datetime

from utils import convert_user_agent, utc_now_naive


def test_utc_now_naive():
    now = utc_now_naive()

    assert isinstance(now, datetime)
    assert now.tzinfo is None


def test_convert_user_agent():
    user_agent = convert_user_agent(
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
    )

    assert user_agent == "Firefox 47.0, Windows 7"
