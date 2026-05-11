from django.contrib import admin
from .models import Airplane, Airline, Seat
# Register your models here.

admin.site.register(Airplane)
admin.site.register(Airline)
admin.site.register(Seat)