from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Ticket
from .serializers import TicketSerializer

# Create your views here.
class TicketViewSet(ModelViewSet):
    queryset = Ticket.objects.select_related(
        'order__user',
        'flight',
        "flight__departure_airport",
        "flight__arrival_airport",
    ).all()
    serializer_class = TicketSerializer
