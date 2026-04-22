from django.db import models

# Create your models here.
class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return f"{self.name} {self.country.name}"

class Airport(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=5, unique=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='airports')

    def __str__(self):
        return f"{self.name} {self.city.code}"