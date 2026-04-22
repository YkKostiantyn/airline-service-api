from django.db import models

# Create your models here.
class TicketStatus(models.TextChoices):
    BOOKED = "booked", "Booked"
    PAID = "paid", "Paid"
    CANCELLED = "cancelled", "Cancelled"
    USED = "used", "Used"

class Ticket(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='tickets')
    flight = models.ForeignKey('flights.Flight', on_delete=models.PROTECT, related_name='tickets')
    seat_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20,
                              choices=TicketStatus.choices,
                              default=TicketStatus.BOOKED)

    def __str__(self):
        return f"{self.user}: {self.seat_number}, {self.status}"
