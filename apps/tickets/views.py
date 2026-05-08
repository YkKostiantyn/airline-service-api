from rest_framework.viewsets import ModelViewSet
from .models import Ticket
from .serializers import TicketSerializer
from .permissions import IsTicketOwnerOrAdmin
from apps.users.models import UserRole
from django.db.models import Q
from .models import TicketStatus
from django.core.exceptions import ValidationError
from django.db import transaction
from apps.aviation.models import Airplane

class TicketViewSet(ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsTicketOwnerOrAdmin]

    filterset_fields = ["order", "flight", "status", "seat"]
    search_fields = [
        "flight__flight_number",
        "flight__departure_airport__name",
        "flight__departure_airport__code",
        "flight__departure_airport__city__name",
        "flight__arrival_airport__name",
        "flight__arrival_airport__code",
        "flight__arrival_airport__city__name",
        "seat__seat_class",
    ]
    ordering_fields = ["id", "seat", "status"]
    ordering = ["id"]

    def get_queryset(self):
        queryset = Ticket.objects.select_related(
            "order__user",
            "flight",
            "flight__departure_airport",
            "flight__departure_airport__city",
            "flight__arrival_airport",
            "flight__arrival_airport__city",
            "seat",
            "seat__airplane",
        )

        user = self.request.user

        if getattr(user, "role", None) == UserRole.ADMIN:
            return queryset.all()

        return queryset.filter(Q(order__isnull=True) | Q(order__user=user))

@transaction.atomic
def create_tickets_for_flight(flight, price):
    if price <= 0:
        raise ValidationError("Ticket price must be greater than 0.")

    seats = flight.airplane.seats.all()

    if not seats.exists():
        raise ValidationError("Cannot create tickets: airplane has no seats.")

    tickets = [
        Ticket(
            flight=flight,
            seat=seat,
            price=price,
            status=TicketStatus.AVAILABLE,
        )
        for seat in seats
    ]

    created_tickets = Ticket.objects.bulk_create(
        tickets,
        ignore_conflicts=True,
    )

    return len(created_tickets)