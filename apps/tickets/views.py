from rest_framework.viewsets import ModelViewSet
from .models import Ticket
from .serializers import TicketSerializer
from .permissions import IsTicketOwnerOrAdmin
from apps.users.models import UserRole
from django.db.models import Q

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