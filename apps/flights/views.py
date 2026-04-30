from rest_framework.viewsets import ModelViewSet
from .serializers import FlightSerializer
from .models import Flight
from apps.common.permissions import ReadOnlyOrAdmin
# Create your views here.

class FlightViewSet(ModelViewSet):
    queryset = Flight.objects.select_related('airplane', 'departure_airport', 'arrival_airport').all()
    serializer_class = FlightSerializer
    permission_classes = [ReadOnlyOrAdmin]

    filterset_fields = [
        "airplane",
        "departure_airport",
        "arrival_airport",
        "status",
    ]

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
