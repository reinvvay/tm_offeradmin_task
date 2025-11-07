from litestar import Litestar
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin
from resources.db import on_shutdown, on_startup


def create_app() -> Litestar:
    from api.offerwalls import ROUTER

    openapi = OpenAPIConfig(
        title="OfferWall API",
        version="1.0.0",
        render_plugins=[SwaggerRenderPlugin()],
        path="/api/schema",
    )

    return Litestar(
        route_handlers=[ROUTER],
        on_startup=[on_startup],
        on_shutdown=[on_shutdown],
        openapi_config=openapi,
    )
