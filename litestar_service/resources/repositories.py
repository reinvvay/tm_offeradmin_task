from resources.models import (Offer, OfferWall, OfferWallOffer,
                              OfferWallPopupOffer)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class OfferWallRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_token(self, token: str) -> OfferWall | None:
        stmt = (
            select(OfferWall)
            .where(OfferWall.token == token)
            .options(
                selectinload(OfferWall.offer_assignments).joinedload(
                    OfferWallOffer.offer
                ),
                selectinload(OfferWall.popup_assignments).joinedload(
                    OfferWallPopupOffer.offer
                ),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().unique().first()

    async def get_offer_names(self) -> list[str]:
        result = await self.session.execute(select(Offer.name).distinct())
        return [r[0] for r in result.all()]
