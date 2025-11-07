from litestar import MediaType, Response, status_codes  # type: ignore


class JsonErrorResponse:
    default_detail = "Something went wrong"
    default_status_code = status_codes.HTTP_500_INTERNAL_SERVER_ERROR

    @classmethod
    def to_response(cls, detail: str = None, status_code: int = None):
        return Response(
            media_type=MediaType.JSON,
            content={"message": detail or cls.default_detail},
            status_code=status_code or cls.default_status_code,
        )


class NotFound(JsonErrorResponse):
    default_detail = "Not found"
    default_status_code = status_codes.HTTP_404_NOT_FOUND


# Usage:
from litestar import Litestar, get  # type: ignore
from my_project.responses import (  # type: ignore; Adjust import path accordingly
    JsonErrorResponse, NotFound)


@get("/items/{item_id:int}")
def get_item(item_id: int):
    fake_db = {1: "Item 1", 2: "Item 2"}

    item = fake_db.get(item_id)
    if not item:
        # Return a 404 Not Found JSON error response
        return NotFound.to_response()

    return {"id": item_id, "name": item}
