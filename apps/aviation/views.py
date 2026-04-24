from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializers import AirplaneSerializer, AirlineSerializer
from .models import Airplane, Airline

# Create your views here.
class AirplaneViewSet(ModelViewSet):
    queryset = Airplane.objects.select_related('airline__base_airport').all()
    serializer_class = AirplaneSerializer

class AirlineViewSet(ModelViewSet):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer