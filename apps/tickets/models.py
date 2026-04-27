from django.db import models
from apps.orders.models import Order

# Create your models here.
class TicketStatus(models.TextChoices):
    BOOKED = "booked", "Booked"
    PAID = "paid", "Paid"
    CANCELLED = "cancelled", "Cancelled"
    USED = "used", "Used"

class Ticket(models.Model):
    flight = models.ForeignKey('flights.Flight', on_delete=models.PROTECT, related_name='tickets')
    order = models.ForeignKey('orders.Order', on_delete=models.PROTECT, related_name='tickets', null = True, blank=True)
    seat_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20,
                              choices=TicketStatus.choices,
                              default=TicketStatus.BOOKED)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['flight', 'seat_number'],
                                    name='unique_ticket'),
        ]

    def __str__(self):
        if self.order:
            return f"{self.order.user}: {self.seat_number}, {self.status}"

        return f"No order: {self.seat_number}, {self.status}"
