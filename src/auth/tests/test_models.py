from database import TokenPair, User

from .mocks import SESSION_ID, USER_ID


def test_user():
    user = User(user_id=USER_ID)
    assert str(user) == f"<User: {USER_ID}>"


def test_token_pair():
    token_pair = TokenPair(session_id=SESSION_ID)
    assert str(token_pair) == f"<TokenPair: {SESSION_ID}>"
