from rest_framework import serializers

from .models import Ticket
from apps.flights.models import FlightStatus


class TicketSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="order.user.email", read_only=True)
    flight_info = serializers.SerializerMethodField()
    seat_label = serializers.CharField(source="seat.label", read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "order",
            "user_email",
            "flight",
            "flight_info",
            "seat",
            "seat_label",
            "status",
            "price",
        ]
        read_only_fields = [
            "id",
            "order",
            "seat_label",
            "user_email",
            "flight_info",
        ]

    def get_flight_info(self, obj):
        return (
            f"{obj.flight.departure_airport} -- "
            f"{obj.flight.arrival_airport}"
        )

    def validate(self, attrs):
        flight = attrs.get("flight")
        seat = attrs.get("seat")

        if self.instance:
            flight = flight or self.instance.flight
            seat = seat or self.instance.seat

        if flight and flight.status == FlightStatus.CANCELLED:
            raise serializers.ValidationError(
                "Can't create a ticket for cancelled flight."
            )

        if flight and seat and seat.airplane != flight.airplane:
            raise serializers.ValidationError(
                "Seat does not belong to the airplane assigned to this flight."
            )

        queryset = Ticket.objects.filter(
            flight=flight,
            seat=seat,
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "Ticket for this flight and seat already exists."
            )

        return attrs