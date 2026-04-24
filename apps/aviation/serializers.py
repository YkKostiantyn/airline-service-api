from rest_framework import serializers
from .models import Airplane, Airline
from apps.locations.models import Airport

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