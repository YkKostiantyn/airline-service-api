from django.db import models
from apps.users.models import User
# Create your models here.

class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    CANCELLED = "cancelled", "Cancelled"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    currency = models.CharField(max_length=10, default="usd")
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.PositiveIntegerField(default=0)

    def recalculate_total_amount(self):
        total = self.tickets.aggregate(total=models.Sum("price"))["total"] or 0
        self.total_amount = total
        self.save(update_fields=["total_amount"])
        return self.total_amount

    def __str__(self):
        return f"{self.user}: {self.status} - {self.created_at}"