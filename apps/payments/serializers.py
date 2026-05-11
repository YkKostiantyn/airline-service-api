from rest_framework import serializers

from apps.orders.models import Order, OrderStatus


class CreateCheckoutSessionSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()

    def validate_order_id(self, value):
        request = self.context["request"]

        try:
            order = Order.objects.get(id=value, user=request.user)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")

        if order.status != OrderStatus.PENDING:
            raise serializers.ValidationError("Only pending orders can be paid.")

        order.recalculate_total_amount()

        if order.total_amount <= 0:
            raise serializers.ValidationError("Order amount must be greater than 0.")

        self.context["order"] = order
        return value