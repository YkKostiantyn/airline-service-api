from rest_framework import serializers
from .models import Order, OrderStatus
from apps.tickets.models import Ticket
from django.db import transaction

class TicketInOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "flight", "seat_number", "status"]


class OrderListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ["id", "user", "status", "created_at", "tickets"]
        read_only_fields = ["id", "created_at"]

class OrderDetailSerializer(serializers.ModelSerializer):
    tickets = TicketInOrderSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "status", "created_at", "tickets"]
        read_only_fields = ["id", "created_at", "user"]

    def validate(self, attrs):
        request = self.context.get("request")
        current_user = request.user if request else None

        status = attrs.get("status")

        #check put/patch

        old_status = self.instance.status
        new_status = status or old_status

        #user identity check
        if "user" in attrs and attrs["user"]!= self.instance.user:
            raise serializers.ValidationError("You cannot change order user.")

        #check cencelled status
        if old_status == OrderStatus.CANCELLED:
            raise serializers.ValidationError("Cannot be change")

        #check paid status
        if old_status == OrderStatus.PAID and new_status != OrderStatus.PAID:
            raise serializers.ValidationError("Cannot change back")

        # regular user can only cancel own order
        if current_user and getattr(current_user, "role", None) != "admin":
            if set(attrs.keys()) - {"status"}:
                raise serializers.ValidationError(
                    "You can only change order status."
                )

            if new_status != OrderStatus.CANCELLED:
                raise serializers.ValidationError(
                    "You can only cancel your order."
                )

            if old_status == OrderStatus.PAID:
                raise serializers.ValidationError(
                    "You cannot cancel paid order."
                )
        return attrs

    def update(self, instance, validated_data):
        new_status = validated_data.get("status", instance.status)

        with transaction.atomic():
            instance.status = new_status
            instance.save()

            if new_status == OrderStatus.CANCELLED:
                instance.tickets.update(order=None)
        return instance

class OrderCreateSerializer(serializers.ModelSerializer):
    tickets = serializers.PrimaryKeyRelatedField(
        queryset=Ticket.objects.filter(order__isnull=True),
        many=True,
        write_only=True
    )

    class Meta:
        model = Order
        fields = ["id", "tickets"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        tickets = validated_data.pop("tickets")
        user = self.context["request"].user
        ticket_ids = [ticket.id for ticket in tickets]

        with transaction.atomic():
            locked_tickets = Ticket.objects.select_for_update().filter(
                id__in=ticket_ids,
                order__isnull=True
            )
            if locked_tickets.count() != len(ticket_ids):
                raise serializers.ValidationError(
                    "Some tickets are already ordered."
                )

            order = Order.objects.create(
                user=user,
                status=OrderStatus.PENDING,
            )
            locked_tickets.update(order=order)

        return order

    def validate_tickets(self, value):
        if not value:
            raise serializers.ValidationError("At least one ticket is required")
        return value