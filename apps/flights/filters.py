import django_filters
from django.db.models import Q, Count
from apps.tickets.models import TicketStatus

from .models import Flight


class FlightFilter(django_filters.FilterSet):
    from_country = django_filters.CharFilter(
        field_name="departure_airport__city__country__name",
        lookup_expr='icontains'
    )
    to_country = django_filters.CharFilter(
        field_name="arrival_airport__city__country__name",
        lookup_expr='icontains'
    )

    from_city = django_filters.CharFilter(
        field_name="departure_airport__city__name",
        lookup_expr="icontains",
    )
    to_city = django_filters.CharFilter(
        field_name="arrival_airport__city__name",
        lookup_expr="icontains" #this parameter for collect a value, without register
    )

    from_airport = django_filters.CharFilter(
        field_name="departure_airport__code",
        lookup_expr="iexact", #this parameter for an exact match
    )
    to_airport = django_filters.CharFilter(
        field_name="arrival_airport__code",
        lookup_expr="iexact",
    )

    date_from = django_filters.DateTimeFilter(
        field_name="departure_time",
        lookup_expr="gte", # >= data
    )
    date_to = django_filters.DateTimeFilter(
        field_name="departure_time",
        lookup_expr="lte", #<= data
    )

    route = django_filters.CharFilter(method="filter_route")
    available_only = django_filters.BooleanFilter(method="filter_available_only")

    class Meta:
        model = Flight
        fields = [
            "airplane",
            "departure_airport",
            "arrival_airport",
            "status",
            "from_country",
            "to_country",
            "from_city",
            "to_city",
            "from_airport",
            "to_airport",
            "date_from",
            "date_to",
            "route",
            "available_only",
        ]

    def filter_route(self, queryset, name, value):
        return queryset.filter(
            Q(departure_airport__city__name__icontains=value)
            | Q(arrival_airport__city__name__icontains=value)
            | Q(departure_airport__code__iexact=value)
            | Q(arrival_airport__code__iexact=value)
            | Q(departure_airport__name__icontains=value)
            | Q(arrival_airport__name__icontains=value)
        )

    def filter_available_only(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.annotate(
            available_tickets_count=Count(
                "tickets",
                filter=Q(
                    tickets__order__isnull=True,
                    tickets__status=TicketStatus.AVAILABLE,
                ),
            ))