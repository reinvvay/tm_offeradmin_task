from litestar.exceptions import HTTPException, NotFoundException
from litestar.response import Response
from litestar.status_codes import HTTP_404_NOT_FOUND


def not_found_handler(_: NotFoundException) -> Response:
    return Response({"detail": "Not found."}, status_code=HTTP_404_NOT_FOUND)


exception_handlers = {
    NotFoundException: not_found_handler,
    HTTPException: lambda exc: Response(
        {"detail": exc.detail}, status_code=exc.status_code
    ),
}
