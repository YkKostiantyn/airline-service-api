from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Country,City, Airport
from .serializers import CountrySerializer, CitySerializer, AirportSerializer

# Create your views here.
class CountryViewSet(ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

class CityViewSet(ModelViewSet):
    queryset = City.objects.select_related('country').all()
    serializer_class = CitySerializer

class AirportViewSet(ModelViewSet):
    queryset = Airport.objects.select_related('city', 'city__country').all()
    serializer_class = AirportSerializer
