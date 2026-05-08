from rest_framework import serializers
from .models import Airplane, Airline
from apps.locations.models import Airport
from .models import Seat

class AirlineSerializer(serializers.ModelSerializer):
    base_airport_name = serializers.CharField(source='base_airport.name', read_only=True)

    class Meta:
        model = Airline
        fields = '__all__'
        read_only_fields = ['id']

class AirplaneSerializer(serializers.ModelSerializer):
    airline_name = serializers.CharField(source='airline.name', read_only=True)

    class Meta:
        model = Airplane
        fields = '__all__'
        read_only_fields = ['id']

class SeatSerializer(serializers.ModelSerializer):
    seat_label = serializers.CharField(source="label", read_only=True)
    airplane_name = serializers.CharField(source="airplane.name", read_only=True)
    tail_number = serializers.CharField(source="airplane.tail_number", read_only=True)

    class Meta:
        model = Seat
        fields = [
            "id",
            "airplane",
            "airplane_name",
            "tail_number",
            "row",
            "number",
            "seat_label",
            "seat_class",
        ]
        read_only_fields = ["id", "seat_label", "airplane_name", "tail_number"]