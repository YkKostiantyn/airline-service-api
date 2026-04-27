from rest_framework import serializers
from .models import Order, OrderStatus
from apps.tickets.models import Ticket

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
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        user = attrs.get("user")
        status = attrs.get("status")

        #validation create
        if self.instance is None:
            if not user:
                raise serializers.ValidationError("User is required")
            if status and status != OrderStatus.PENDING:
                raise serializers.ValidationError("Order status is invalid")

        #check put/patch
        else:
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

        return attrs

class OrderCreateSerializer(serializers.ModelSerializer):
    tickets = serializers.PrimaryKeyRelatedField(
        queryset=Ticket.objects.filter(order__isnull=True),
        many=True,
        write_only=True
    )

    class Meta:
        model = Order
        fields = ["id", "user", "tickets"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        tickets = validated_data.pop("tickets")

        order = Order.objects.create(
            user=validated_data["user"],
            status=OrderStatus.PENDING,
        )

        for ticket in tickets:
            ticket.order = order
            ticket.save()

        return order