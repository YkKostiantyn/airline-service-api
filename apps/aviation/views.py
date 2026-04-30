from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import AirplaneSerializer, AirlineSerializer
from .models import Airplane, Airline
from apps.common.permissions import ReadOnlyOrAdmin

# Create your views here.
class AirplaneListCreateAPIView(ListCreateAPIView):
    queryset = Airplane.objects.select_related('airline__base_airport').all()
    serializer_class = AirplaneSerializer
    permission_classes = [ReadOnlyOrAdmin]

class AirplaneRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Airplane.objects.select_related('airline__base_airport').all()
    serializer_class = AirplaneSerializer
    permission_classes = [ReadOnlyOrAdmin]

class AirlineListCreateAPIView(ListCreateAPIView):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
    permission_classes = [ReadOnlyOrAdmin]

class AirlineRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
    permission_classes = [ReadOnlyOrAdmin]