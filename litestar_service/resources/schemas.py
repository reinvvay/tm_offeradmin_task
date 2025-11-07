from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class OfferSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uuid: str
    id: int
    url: str
    is_active: bool
    name: str
    sum_to: float
    term_to: int
    percent_rate: float


class OfferWallOfferSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    offer: OfferSchema


class OfferWallPopupOfferSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    offer: OfferSchema


class OfferWallSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    token: str
    name: str
    url: str
    description: Optional[str]
    offer_assignments: List[OfferWallOfferSchema]
    popup_assignments: List[OfferWallPopupOfferSchema]
