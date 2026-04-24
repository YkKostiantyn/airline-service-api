from rest_framework import serializers
from .models import Flight

class FlightSerializer(serializers.ModelSerializer):
    airplane_name = serializers.CharField(source='airplane.name', read_only=True)
    departure_airport_name = serializers.CharField(source='departure_airport.name', read_only=True)
    arrival_airport_name = serializers.CharField(source='arrival_airport.name', read_only=True)

    class Meta:
        model = Flight
        fields = [
            "id",
            "airplane",
            "airplane_name",
            "departure_airport",
            "departure_airport_name",
            "arrival_airport",
            "arrival_airport_name",
            "departure_time",
            "arrival_time",
            "status",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        departure_airport = attrs.get('departure_airport')
        arrival_airport = attrs.get('arrival_airport')
        departure_time =attrs.get('departure_time')
        arrival_time =attrs.get('arrival_time')

        if self.instance:
            departure_airport = departure_airport or self.instance.departure_airport
            arrival_airport = arrival_airport or self.instance.arrival_airport
            departure_time = departure_time or self.instance.departure_time
            arrival_time = arrival_time or self.instance.arrival_time

        if departure_airport == arrival_airport:
            raise serializers.ValidationError("Must be different")

        if arrival_time <= departure_time:
            raise serializers.ValidationError("Must be later")

        return attrs
