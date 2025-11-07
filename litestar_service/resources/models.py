from resources.db import Base
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Offer(Base):
    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(String(64), unique=True)
    url: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool]
    name: Mapped[str]
    sum_to: Mapped[float]
    term_to: Mapped[int]
    percent_rate: Mapped[float]


class OfferWallOffer(Base):
    __tablename__ = "offer_wall_offers"

    id: Mapped[int] = mapped_column(primary_key=True)
    offer_id: Mapped[int] = mapped_column(ForeignKey("offers.id"))
    offer: Mapped["Offer"] = relationship("Offer", lazy="joined")
    order: Mapped[int]


class OfferWallPopupOffer(Base):
    __tablename__ = "offer_wall_popup_offers"

    id: Mapped[int] = mapped_column(primary_key=True)
    offer_id: Mapped[int] = mapped_column(ForeignKey("offers.id"))
    offer: Mapped["Offer"] = relationship("Offer", lazy="joined")


class OfferWall(Base):
    __tablename__ = "offer_walls"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str]
    url: Mapped[str]
    description: Mapped[str | None]

    offer_assignments: Mapped[list["OfferWallOffer"]] = relationship(
        "OfferWallOffer", lazy="selectin", order_by="OfferWallOffer.order"
    )
    popup_assignments: Mapped[list["OfferWallPopupOffer"]] = relationship(
        "OfferWallPopupOffer", lazy="selectin"
    )
