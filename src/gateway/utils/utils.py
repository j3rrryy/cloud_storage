from litestar import MediaType, Request, Response
from litestar.exceptions import HTTPException, NotAuthorizedException


def exception_handler(_: Request, exc: HTTPException) -> Response:
    return Response(
        content={"status_code": exc.status_code, "detail": exc.detail},
        headers=exc.headers,
        media_type=MediaType.MESSAGEPACK,
        status_code=exc.status_code,
    )


def validate_access_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise NotAuthorizedException(detail="Token is missing")

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise NotAuthorizedException(detail="Invalid token format")

    return parts[1]
