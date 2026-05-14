from django.db import models

# Create your models here.
class FlightStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    BOARDING = "boarding", "Boarding"
    DEPARTED = "departed", "Departed"
    DELAYED = "delayed", "Delayed"
    CANCELLED = "cancelled", "Cancelled"

class Flight(models.Model):
    flight_number = models.CharField(max_length=20, unique=True)
    airplane = models.ForeignKey('aviation.Airplane', on_delete=models.PROTECT, related_name='flights')
    departure_airport = models.ForeignKey(
        'locations.Airport',
        on_delete=models.PROTECT,
        related_name='departing_flights'
    )
    arrival_airport = models.ForeignKey(
        'locations.Airport',
        on_delete=models.PROTECT,
        related_name='arriving_flights'
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    status = models.CharField(max_length=15, choices=FlightStatus.choices, default=FlightStatus.SCHEDULED)
    base_price = models.PositiveIntegerField(default=0, help_text="Base price ticket for this flight")

    def __str__(self):
        return f"{self.flight_number}: {self.departure_airport} → {self.arrival_airport}"