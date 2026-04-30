from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Country,City, Airport
from .serializers import CountrySerializer, CitySerializer, AirportSerializer
from apps.common.permissions import ReadOnlyOrAdmin

# Create your views here.
class CountryViewSet(ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [ReadOnlyOrAdmin]

    search_fields = ["name"]
    ordering_fields = ["id", "name"]
    ordering = ["name"]

class CityViewSet(ModelViewSet):
    queryset = City.objects.select_related('country').all()
    serializer_class = CitySerializer
    permission_classes = [ReadOnlyOrAdmin]

    filterset_fields = ["country"]
    search_fields = ["name", "country__name"]
    ordering_fields = ["id", "name", "country__name"]
    ordering = ["name"]

class AirportViewSet(ModelViewSet):
    queryset = Airport.objects.select_related('city', 'city__country').all()
    serializer_class = AirportSerializer
    permission_classes = [ReadOnlyOrAdmin]

    filterset_fields = ["city", "city__country", "code"]
    search_fields = ["name", "code", "city__name", "city__country__name"]
    ordering_fields = ["id", "name", "code", "city__name", "city__country__name"]
    ordering = ["code"]
