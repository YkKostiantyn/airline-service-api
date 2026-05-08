from django.db import models
from apps.orders.models import Order

# Create your models here.
class TicketStatus(models.TextChoices):
    AVAILABLE = 'available', 'Available'
    BOOKED = "booked", "Booked"
    PAID = "paid", "Paid"
    CANCELLED = "cancelled", "Cancelled"
    USED = "used", "Used"

class Ticket(models.Model):
    flight = models.ForeignKey('flights.Flight', on_delete=models.PROTECT, related_name='tickets')
    order = models.ForeignKey('orders.Order', on_delete=models.PROTECT, related_name='tickets', null = True, blank=True)
    seat = models.ForeignKey(
        "aviation.Seat",
        on_delete=models.PROTECT,
        related_name="tickets",
    )

    status = models.CharField(max_length=20,
                              choices=TicketStatus.choices,
                              default=TicketStatus.AVAILABLE)
    price = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["flight", "seat"],
                name="unique_ticket_per_flight_seat",
            ),
        ]

    def __str__(self):
        if self.order:
            return f"{self.order.user}: {self.seat.label}, {self.status}"

        return f"No order: {self.seat.label}, {self.status}"
