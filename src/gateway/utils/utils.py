from litestar import MediaType, Request, Response
from litestar.exceptions import HTTPException


def exception_handler(_: Request, exc: HTTPException) -> Response:
    return Response(
        content={"status_code": exc.status_code, "detail": exc.detail},
        headers=exc.headers,
        media_type=MediaType.MESSAGEPACK,
        status_code=exc.status_code,
    )
