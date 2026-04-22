from django.db import models

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
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} - {self.tail_number}"