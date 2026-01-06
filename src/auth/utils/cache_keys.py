def user_profile_key(user_id: str) -> str:
    return f"user:{user_id}:profile"


def user_session_list_key(user_id: str) -> str:
    return f"user:{user_id}:session_list"


def user_reset_key(user_id: str) -> str:
    return f"user:{user_id}:reset"


def access_token_key(access_token: str) -> str:
    return f"token:access:{access_token}"


def user_all_keys(user_id: str) -> list[str]:
    return [
        user_profile_key(user_id),
        user_session_list_key(user_id),
        user_reset_key(user_id),
    ]
