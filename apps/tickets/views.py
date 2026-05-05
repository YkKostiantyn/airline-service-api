from rest_framework.viewsets import ModelViewSet
from .models import Ticket
from .serializers import TicketSerializer
from .permissions import IsTicketOwnerOrAdmin


class TicketViewSet(ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsTicketOwnerOrAdmin]

    def get_queryset(self):
        queryset = Ticket.objects.select_related(
            "order__user",
            "flight",
            "flight__departure_airport",
            "flight__arrival_airport",
        )

        user = self.request.user

        if getattr(user, "role", None) == "admin":
            return queryset.all()

        return queryset.filter(order__user=user)