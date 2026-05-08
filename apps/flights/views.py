from rest_framework.viewsets import ModelViewSet
from .serializers import FlightSerializer
from .models import Flight
from apps.common.permissions import ReadOnlyOrAdmin
from .filters import FlightFilter
from apps.tickets.views import create_tickets_for_flight

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

# Create your views here.

class GenerateTicketsSerializer(serializers.Serializer):
    price = serializers.IntegerField(min_value=1)

class FlightViewSet(ModelViewSet):
    queryset = Flight.objects.select_related('airplane', 'departure_airport', 'arrival_airport').all()
    serializer_class = FlightSerializer
    permission_classes = [ReadOnlyOrAdmin]

    filterset_class = FlightFilter

    search_fields = [
        "departure_airport__name",
        "departure_airport__code",
        "departure_airport__city__name",
        "departure_airport__city__country__name",
        "arrival_airport__name",
        "arrival_airport__code",
        "arrival_airport__city__name",
        "arrival_airport__city__country__name",
    ]

    ordering_fields = [
        "id",
        "departure_time",
        "arrival_time",
        "status",
    ]

    ordering = ["departure_time"]

    @extend_schema(
        request=GenerateTicketsSerializer,
        responses={
            201: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string"},
                    "created_count": {"type": "integer"},
                },
            }
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="generate-tickets",
    )
    def generate_tickets(self, request, pk=None):
        flight = self.get_object()

        serializer = GenerateTicketsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            created_count = create_tickets_for_flight(
                flight=flight,
                price=serializer.validated_data["price"],
            )
        except DjangoValidationError as error:
            return Response(
                {"detail": error.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": "Tickets generated successfully.",
                "created_count": created_count,
            },
            status=status.HTTP_201_CREATED,
        )