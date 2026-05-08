from rest_framework import serializers
from django.db import transaction

from .models import Order, OrderStatus
from apps.tickets.models import Ticket, TicketStatus
from apps.users.models import UserRole

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

    ticket_ids = serializers.PrimaryKeyRelatedField(
        queryset=Ticket.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Order
        fields = ["id", "user", "status", "created_at", "tickets", "ticket_ids"]
        read_only_fields = ["id", "created_at", "user"]

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

        if "user" in attrs and attrs["user"] != self.instance.user:
            raise serializers.ValidationError(
                "You cannot change order user."
            )

        if current_user and getattr(current_user, "role", None) != UserRole.ADMIN:
            allowed_fields = {"status", "ticket_ids"}

            if set(attrs.keys()) - allowed_fields:
                raise serializers.ValidationError(
                    "You can only change order status or tickets."
                )

            if "status" in attrs and new_status != OrderStatus.CANCELLED:
                raise serializers.ValidationError(
                    "You can only cancel your order."
                )

            if "ticket_ids" in attrs and old_status != OrderStatus.PENDING:
                raise serializers.ValidationError(
                    "You can change tickets only for pending order."
                )

            if "ticket_ids" in attrs and not attrs["ticket_ids"]:
                raise serializers.ValidationError(
                    "Order must contain at least one ticket."
                )

        return attrs

    def update(self, instance, validated_data):
        new_status = validated_data.get("status", instance.status)
        new_tickets = validated_data.pop("ticket_ids", None)

        with transaction.atomic():
            if new_status == OrderStatus.CANCELLED:
                instance.status = OrderStatus.CANCELLED
                instance.save(update_fields=["status"])

                instance.tickets.update(order=None, status=TicketStatus.AVAILABLE)

                return instance

            if new_tickets is not None:
                new_ticket_ids = [ticket.id for ticket in new_tickets]

                locked_tickets = Ticket.objects.select_for_update().filter(
                    id__in=new_ticket_ids,
                )

                if locked_tickets.count() != len(new_ticket_ids):
                    raise serializers.ValidationError(
                        "Some tickets do not exist."
                    )

                unavailable_tickets = locked_tickets.exclude(order__isnull=True,).exclude(order=instance)

                if unavailable_tickets.exists():
                    raise serializers.ValidationError(
                        "Some tickets are already ordered."
                    )

                instance.tickets.exclude(
                    id__in=new_ticket_ids,
                ).update(order=None, status=TicketStatus.AVAILABLE)

                locked_tickets.update(order=instance, status=TicketStatus.BOOKED)

            instance.status = new_status
            instance.save(update_fields=["status"])

        return instance


class OrderCreateSerializer(serializers.ModelSerializer):
    tickets = serializers.PrimaryKeyRelatedField(
        queryset=Ticket.objects.filter(order__isnull=True),
        many=True,
        write_only=True,
    )

    class Meta:
        model = Order
        fields = ["id", "tickets"]
        read_only_fields = ["id"]

    def validate_tickets(self, value):
        if not value:
            raise serializers.ValidationError(
                "At least one ticket is required."
            )

        return value

    def create(self, validated_data):
        tickets = validated_data.pop("tickets")
        user = self.context["request"].user
        ticket_ids = [ticket.id for ticket in tickets]

        with transaction.atomic():
            locked_tickets = Ticket.objects.select_for_update().filter(
                id__in=ticket_ids,
                order__isnull=True,
            )

            if locked_tickets.count() != len(ticket_ids):
                raise serializers.ValidationError(
                    "Some tickets are already ordered."
                )

            order = Order.objects.create(user=user, status=OrderStatus.PENDING)

            locked_tickets.update(order=order, status=TicketStatus.BOOKED)

        return order