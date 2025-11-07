from drf_spectacular.utils import (OpenApiExample, OpenApiResponse,
                                   extend_schema)
from rest_framework import mixins, routers, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from admin_panel.models import (Offer, OfferChoices, OfferWall, OfferWallOffer,
                                OfferWallPopupOffer)


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = [
            "uuid",
            "id",
            "url",
            "is_active",
            "name",
            "sum_to",
            "term_to",
            "percent_rate",
        ]


class OfferWallOfferSerializer(serializers.ModelSerializer):
    offer = OfferSerializer()

    class Meta:
        model = OfferWallOffer
        fields = ["offer"]


class OfferWallPopupOfferSerializer(serializers.ModelSerializer):
    offer = OfferSerializer()

    class Meta:
        model = OfferWallPopupOffer
        fields = ["offer"]


class OfferWallSerializer(serializers.ModelSerializer):
    offer_assignments = OfferWallOfferSerializer(many=True, read_only=True)
    popup_assignments = OfferWallPopupOfferSerializer(many=True, read_only=True)

    class Meta:
        model = OfferWall
        fields = [
            "token",
            "name",
            "url",
            "description",
            "offer_assignments",
            "popup_assignments",
        ]


class OfferWallViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    """
    A viewset for viewing and editing OfferWall instances with their assigned offers. Offers in offer_assignments are sorted by order
    """

    queryset = OfferWall.objects.all()
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = OfferWallSerializer
    lookup_field = "token"

    @extend_schema(
        responses=OpenApiResponse(
            response=200,
            examples=[OpenApiExample("response", value={"offer_names": ["Loanplus"]})],
        )
    )
    @action(methods=["get"], detail=False)
    def get_offer_names(self, _request):
        offer_names = [offer_name[0] for offer_name in OfferChoices.choices]
        return Response({"offer_names": offer_names})


router = routers.DefaultRouter()
router.register("offerwalls", OfferWallViewSet, basename="offerwalls")
