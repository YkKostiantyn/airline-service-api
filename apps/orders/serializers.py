from rest_framework import serializers
from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import Order, OrderStatus
from apps.tickets.models import Ticket, TicketStatus
from apps.users.models import UserRole
from apps.flights.models import Flight
from apps.aviation.models import Seat

class TicketInOrderSerializer(serializers.ModelSerializer):
    seat_label = serializers.CharField(source="seat.label", read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "flight", "seat", "seat_label", "status", "price"]

class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "user", "status", "created_at", "tickets"]
        read_only_fields = ["id", "created_at"]

class OrderDetailSerializer(serializers.ModelSerializer):
    tickets = TicketInOrderSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "status", "created_at", "tickets", "total_amount"]
        read_only_fields = ["id", "created_at", "user", "total_amount"]

    def validate(self, attrs):
        request = self.context.get("request")
        current_user = request.user if request else None

        old_status = self.instance.status
        new_status = attrs.get("status", old_status)

        if old_status == OrderStatus.CANCELLED:
            raise serializers.ValidationError(
                "Cancelled order cannot be changed."
            )

        if old_status == OrderStatus.PAID:
            raise serializers.ValidationError(
                "Paid order cannot be changed."
            )

        if current_user and getattr(current_user, "role", None) != UserRole.ADMIN:
            allowed_fields = {"status"}

            if set(attrs.keys()) - allowed_fields:
                raise serializers.ValidationError(
                    "You can only change order status."
                )

            if "status" in attrs and new_status != OrderStatus.CANCELLED:
                raise serializers.ValidationError(
                    "You can only cancel your order."
                )

        return attrs

    def update(self, instance, validated_data):
        new_status = validated_data.get("status", instance.status)

        with transaction.atomic():
            if new_status == OrderStatus.CANCELLED and instance.status != OrderStatus.CANCELLED:
                instance.status = OrderStatus.CANCELLED
                instance.save(update_fields=["status"])

                instance.tickets.all().delete()

        return instance

class OrderCreateSerializer(serializers.ModelSerializer):
    flight_id = serializers.IntegerField(write_only=True)
    seat_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, min_length=1
    )

    class Meta:
        model = Order
        fields = ['id', 'flight_id', 'seat_ids', 'status', 'total_amount']
        read_only_fields = ['status', 'total_amount']

    def validate(self, attrs):
        flight_id = attrs.get('flight_id')
        seat_ids = attrs.get('seat_ids')

        try:
            flight = Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            raise ValidationError({"flight_id": "Flight not found."})

        valid_seats_count = Seat.objects.filter(
            airplane=flight.airplane,
            id__in=seat_ids
        ).count()

        if valid_seats_count != len(set(seat_ids)):
            raise ValidationError({"seat_ids": "Some seats do not exist in this airplane."})

        attrs['flight'] = flight
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        flight = validated_data.pop('flight')
        seat_ids = validated_data.pop('seat_ids')
        user = self.context['request'].user

        locked_seats = Seat.objects.select_for_update().filter(id__in=seat_ids)

        existing_tickets = Ticket.objects.filter(
            flight=flight,
            seat__in=locked_seats,
            status__in=[TicketStatus.PAID, TicketStatus.BOOKED]
        )

        if existing_tickets.exists():
            raise ValidationError({"seat_ids": "Sorry, some of these seats were just booked by someone else."})

        order = Order.objects.create(user=user, status=OrderStatus.PENDING)

        tickets_to_create = []
        total_amount = 0

        for seat in locked_seats:
            base_price = flight.base_price or 0

            if seat.seat_class == Seat.SeatClass.FIRST:
                ticket_price = base_price * 3
            elif seat.seat_class == Seat.SeatClass.BUSINESS:
                ticket_price = base_price * 2
            else:
                ticket_price = base_price

            tickets_to_create.append(Ticket(
                flight=flight,
                seat=seat,
                order=order,
                price=ticket_price,
                status=TicketStatus.BOOKED
            ))
            total_amount += ticket_price

        Ticket.objects.bulk_create(tickets_to_create)

        order.total_amount = total_amount
        order.save(update_fields=['total_amount'])

        return order