from django.db import models
from django.conf import settings
from django.db import models

# Create your models here.

class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"

class Payment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments')

    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name='payment')

    amount = models.PositiveIntegerField()

    currency = models.CharField(
        max_length=10,
        default='usd')

    status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING)

    stripe_checkout_session_id = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True)

    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for order {self.order_id}: {self.status}"