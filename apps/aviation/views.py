from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import AirplaneSerializer, AirlineSerializer
from .models import Airplane, Airline

# Create your views here.
class AirplaneListCreateAPIView(ListCreateAPIView):
    queryset = Airplane.objects.select_related('airline__base_airport').all()
    serializer_class = AirplaneSerializer

class AirplaneRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Airplane.objects.select_related('airline__base_airport').all()
    serializer_class = AirplaneSerializer

class AirlineListCreateAPIView(ListCreateAPIView):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer

class AirlineRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer