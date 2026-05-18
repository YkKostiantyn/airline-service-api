from apps.flights.models import Flight
from apps.aviation.models import Seat
from apps.tickets.models import Ticket
from apps.orders.models import Order
import os

def get_available_flights(destination_city: str = None, origin_city: str = None):
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

    print(f"[AI CALL] Flight search: {origin_city} -> {destination_city}")
    try:
        print(f"[AI CALL] Flight search: {origin_city} -> {destination_city}")

        queryset = Flight.objects.select_related('departure_airport', 'arrival_airport').all()

        if destination_city:
            queryset = queryset.filter(arrival_airport__city__icontains=destination_city)
        if origin_city:
            queryset = queryset.filter(departure_airport__city__icontains=origin_city)

        flights = list(queryset[:10])

        if not flights:
            return {"status": "not_found", "message": "Unfortunately, no flights were found."}

        result = []
        for f in flights:
            result.append({
                "flight_number": f.flight_number,
                "from_airport": f.departure_airport.name if f.departure_airport else "Unknown",
                "from_city": f.departure_airport.city.name if f.departure_airport and f.departure_airport.city else "Unknown",
                "to_airport": f.arrival_airport.name if f.arrival_airport else "Unknown",
                "to_city": f.arrival_airport.city.name if f.arrival_airport and f.arrival_airport.city else "Unknown",
                "departure_time": f.departure_time.strftime("%Y-%m-%d %H:%M"),
                "base_price": float(f.base_price),
                "status": f.status
            })

        return result

    except Exception as e:
        print(f"TOOLS ERROR: {str(e)}", flush=True)
        return {"error": str(e)}


def get_flight_pricing_and_seats(flight_id: int):
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    print(f"✈️ [AI CALL] Checking pricing for flight ID: {flight_id}", flush=True)

    try:
        flight = Flight.objects.select_related('airplane').get(id=flight_id)
        base_price = flight.base_price or 0

        all_seats = Seat.objects.filter(airplane=flight.airplane)

        booked_seats_ids = Ticket.objects.filter(
            flight=flight,
            status__in=['booked', 'paid']
        ).values_list('seat_id', flat=True)

        available_seats = all_seats.exclude(id__in=booked_seats_ids)

        if not available_seats.exists():
            return {"status": "full", "message": "There are no available seats left for this flight."}

        result = {
            "flight_id": flight.id,
            "airplane": flight.airplane.name,
            "classes": {}
        }

        for seat_class in ['first', 'business', 'economy']:
            seats_in_class = available_seats.filter(seat_class=seat_class)

            if seats_in_class.exists():
                multiplier = 3 if seat_class == 'first' else (2 if seat_class == 'business' else 1)
                price = base_price * multiplier

                result["classes"][seat_class] = {
                    "price_usd": float(price),
                    "available_count": seats_in_class.count()
                }

        return result

    except Flight.DoesNotExist:
        return {"error": f"Flight with ID {flight_id} was not found."}
    except Exception as e:
        print(f"TOOLS ERROR: {str(e)}", flush=True)
        return {"error": str(e)}

def get_order_info(order_id: int):
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    print(f"✈️ [AI CALL] Checking order #{order_id}", flush=True)

    try:
        order = Order.objects.select_related('payment').prefetch_related('tickets__seat').get(id=order_id)

        tickets_list = []
        for ticket in order.tickets.all():
            tickets_list.append({
                "seat_label": ticket.seat.label,
                "class": ticket.seat.seat_class,
                "price": float(ticket.price)
            })

        payment_status = "unpaid"
        if hasattr(order, 'payment'):
            payment_status = order.payment.status

        return {
            "order_id": order.id,
            "order_status": order.status,
            "total_amount": float(order.total_amount),
            "currency": order.currency.upper(),
            "payment_status": payment_status,
            "tickets_count": len(tickets_list),
            "tickets_details": tickets_list
        }

    except Order.DoesNotExist:
        return {"error": f"Order #{order_id} was not found."}
    except Exception as e:
        print(f"TOOLS ERROR: {str(e)}", flush=True)
        return {"error": str(e)}
tools_list = [get_available_flights, get_flight_pricing_and_seats, get_order_info]