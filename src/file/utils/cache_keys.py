def file_upload_key(user_id: str, upload_id: str) -> str:
    return f"file:{user_id}:{upload_id}:upload"


def file_list_key(user_id: str) -> str:
    return f"file:{user_id}:list"


def file_name_key(user_id: str, file_id: str) -> str:
    return f"file:{user_id}:{file_id}:name"
