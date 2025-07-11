from litestar import Request
from litestar.exceptions import NotAuthorizedException


def validate_access_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise NotAuthorizedException(detail="Token is missing")

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise NotAuthorizedException(detail="Invalid token format")

    return parts[1]
