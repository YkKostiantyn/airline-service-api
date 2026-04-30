from rest_framework.viewsets import ModelViewSet
from .serializers import FlightSerializer
from .models import Flight
from apps.common.permissions import ReadOnlyOrAdmin
# Create your views here.

class FlightViewSet(ModelViewSet):
    queryset = Flight.objects.select_related('airplane', 'departure_airport', 'arrival_airport').all()
    serializer_class = FlightSerializer
    permission_classes = [ReadOnlyOrAdmin]
