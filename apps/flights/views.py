from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializers import FlightSerializer
from .models import Flight
# Create your views here.

class FlightViewSet(ModelViewSet):
    queryset = Flight.objects.select_related('airplane', 'departure_airport', 'arrival_airport').all()
    serializer_class = FlightSerializer