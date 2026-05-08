from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import AirplaneSerializer, AirlineSerializer
from .models import Airplane, Airline
from apps.common.permissions import ReadOnlyOrAdmin
from .models import Seat
from .serializers import SeatSerializer

# Create your views here.
class AirplaneListCreateAPIView(ListCreateAPIView):
    queryset = Airplane.objects.select_related('airline__base_airport').all()
    serializer_class = AirplaneSerializer
    permission_classes = [ReadOnlyOrAdmin]

    filterset_fields = ["airline","capacity"]

    search_fields = [
        "name",
        "tail_number",
        "airline__name",
        "airline__base_airport__name",
        "airline__base_airport__code",
        "airline__base_airport__city__name",
        "airline__base_airport__city__country__name",
    ]

    ordering_fields = [
        "id",
        "name",
        "tail_number",
        "capacity",
    ]

    ordering = ["id"]

class AirplaneRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Airplane.objects.select_related('airline__base_airport').all()
    serializer_class = AirplaneSerializer
    permission_classes = [ReadOnlyOrAdmin]

class AirlineListCreateAPIView(ListCreateAPIView):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
    permission_classes = [ReadOnlyOrAdmin]

    filterset_fields = [
        "base_airport",
        "base_airport__city",
        "base_airport__city__country",
    ]

    search_fields = [
        "name",
        "base_airport__name",
        "base_airport__code",
        "base_airport__city__name",
        "base_airport__city__country__name",
    ]

    ordering_fields = [
        "id",
        "name",
        "base_airport__name",
        "base_airport__code",
    ]

    ordering = ["name"]

class AirlineRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
    permission_classes = [ReadOnlyOrAdmin]

class SeatListCreateAPIView(ListCreateAPIView):
    queryset = Seat.objects.select_related(
        "airplane",
        "airplane__airline",
        "airplane__airline__base_airport",
    ).all()
    serializer_class = SeatSerializer
    permission_classes = [ReadOnlyOrAdmin]

    filterset_fields = ["airplane", "seat_class", "row", "number"]

    search_fields = ["airplane__name", "airplane__tail_number", "airplane__airline__name"]

    ordering_fields = ["id", "airplane", "row", "number", "seat_class"]

    ordering = ["airplane", "row", "number"]
class SeatRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Seat.objects.select_related(
        "airplane",
        "airplane__airline",
        "airplane__airline__base_airport",
    ).all()
    serializer_class = SeatSerializer
    permission_classes = [ReadOnlyOrAdmin]