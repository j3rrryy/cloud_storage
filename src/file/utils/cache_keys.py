def user_file_upload_key(user_id: str, upload_id: str) -> str:
    return f"user:{user_id}:file_upload:{upload_id}"


def user_file_list_key(user_id: str) -> str:
    return f"user:{user_id}:file_list"


def user_file_name_key(user_id: str, file_id: str) -> str:
    return f"user:{user_id}:file_name:{file_id}"
