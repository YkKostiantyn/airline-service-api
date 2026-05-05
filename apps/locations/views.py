from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Country,City, Airport
from .serializers import CountrySerializer, CitySerializer, AirportSerializer
from apps.permission.permissions import ReadOnlyOrAdmin

# Create your views here.
class CountryViewSet(ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [ReadOnlyOrAdmin]

class CityViewSet(ModelViewSet):
    queryset = City.objects.select_related('country').all()
    serializer_class = CitySerializer
    permission_classes = [ReadOnlyOrAdmin]

class AirportViewSet(ModelViewSet):
    queryset = Airport.objects.select_related('city', 'city__country').all()
    serializer_class = AirportSerializer
    permission_classes = [ReadOnlyOrAdmin]
