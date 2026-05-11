from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Airline(models.Model):
    name = models.CharField(max_length=255)
    base_airport = models.ForeignKey(
        'locations.Airport',
        on_delete=models.PROTECT,
        related_name='airlines'
    )

    def __str__(self):
        return self.name


class Airplane(models.Model):
    airline = models.ForeignKey(
        Airline,
        on_delete=models.PROTECT,
        related_name='airplanes'
    )
    name = models.CharField(max_length=100)
    tail_number = models.CharField(max_length=10, unique=True)
    capacity = models.PositiveIntegerField(validators = [MinValueValidator(1), MaxValueValidator(400)])

    def __str__(self):
        return f"{self.name} - {self.tail_number}"


class Seat(models.Model):
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="seats",
    )
    row = models.PositiveIntegerField()
    number = models.PositiveIntegerField()

    class SeatClass(models.TextChoices):
        FIRST = "first", "First"
        BUSINESS = "business", "Business"
        ECONOMY = "economy", "Economy"

    seat_class = models.CharField(
        max_length=20,
        choices=SeatClass.choices,
        default=SeatClass.ECONOMY,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["airplane", "row", "number"],
                name="unique_seat_per_airplane",
            )
        ]

    @property
    def label(self):
        letter = chr(64 + self.number)
        return f"{self.row}{letter}"

    def __str__(self):
        return f"{self.airplane.name} - {self.label} ({self.seat_class})"