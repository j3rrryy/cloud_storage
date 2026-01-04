from datetime import datetime

from utils import utc_now_naive


def test_utc_now_naive():
    now = utc_now_naive()

    assert isinstance(now, datetime)
    assert now.tzinfo is None
