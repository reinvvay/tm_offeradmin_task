import typing

from litestar import Router, get, status_codes
from litestar.exceptions import HTTPException
from resources.repositories import OfferWallRepository
from resources.schemas import OfferWallSchema


@get("/offerwalls/{token:str}/")
async def get_offerwall(token: str, repo: OfferWallRepository) -> OfferWallSchema:
    offerwall = await repo.get_by_token(token)
    if not offerwall:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND, detail="OfferWall not found"
        )
    return OfferWallSchema.model_validate(offerwall)


@get("/offerwalls/get_offer_names/")
async def get_offer_names(repo: OfferWallRepository) -> dict:
    names = await repo.get_offer_names()
    return {"offer_names": names}


ROUTER: typing.Final = Router(
    path="/api",
    route_handlers=[get_offerwall, get_offer_names],
)
