from rest_framework import serializers
from .models import Ticket
from apps.flights.models import FlightStatus, Flight


class TicketSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='order.user.username', read_only=True)
    flight_info = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ['id',"order",'user_username' ,'flight','flight_info' ,'seat_number', 'status']
        read_only_fields = ['id', 'order']

    def get_flight_info(self, obj):
        return f"{obj.flight.departure_airport} -- {obj.flight.arrival_airport}"

    def validate_seat_number(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Please enter a valid seat number")
        return value.strip().upper()

    def validate(self, attrs):
        flight = attrs.get('flight')
        seat_number = attrs.get('seat_number')

        if self.instance:
            flight = flight or self.instance.flight
            seat_number = seat_number or self.instance.seat_number

        if flight and flight.status == FlightStatus.CANCELLED:
            raise serializers.ValidationError("Can't create a ticket for cancelled flight")

        #check whether the ticket is on this flight and seat
        queryset = Ticket.objects.filter(flight = flight ,seat_number=seat_number)

        #check without current seat(for put\patch)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError("Ticket already exists")
        return attrs