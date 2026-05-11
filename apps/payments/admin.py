from django.contrib import admin

from apps.payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "order",
        "amount",
        "currency",
        "status",
        "created_at",
    )
    list_filter = ("status", "currency", "created_at")
    search_fields = (
        "id",
        "stripe_checkout_session_id",
        "stripe_payment_intent_id",
    )