from apps.flights.models import Flight
from apps.aviation.models import Seat
from apps.tickets.models import Ticket
from apps.orders.models import Order
import os

def get_available_flights(destination_city: str = None, origin_city: str = None):
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

    print(f"✈️ [ШІ ВИКЛИК] Пошук рейсів: {origin_city} -> {destination_city}")
    try:
        print(f"✈️ [ШІ ВИКЛИК] Пошук рейсів: {origin_city} -> {destination_city}")

        queryset = Flight.objects.select_related('departure_airport', 'arrival_airport').all()

        if destination_city:
            queryset = queryset.filter(arrival_airport__city__icontains=destination_city)
        if origin_city:
            queryset = queryset.filter(departure_airport__city__icontains=origin_city)

        flights = list(queryset[:10])

        if not flights:
            return {"status": "not_found", "message": "На жаль, рейсів не знайдено."}

        result = []
        for f in flights:
            result.append({
                "flight_number": f.flight_number,
                "from_airport": f.departure_airport.name if f.departure_airport else "Невідомо",
                "from_city": f.departure_airport.city.name if f.departure_airport and f.departure_airport.city else "Невідомо",
                "to_airport": f.arrival_airport.name if f.arrival_airport else "Невідомо",
                "to_city": f.arrival_airport.city.name if f.arrival_airport and f.arrival_airport.city else "Невідомо",
                "departure_time": f.departure_time.strftime("%Y-%m-%d %H:%M"),
                "base_price": float(f.base_price),
                "status": f.status
            })

        return result

    except Exception as e:
        print(f"🚨 ПОМИЛКА В TOOLS: {str(e)}", flush=True)
        return {"error": str(e)}


def get_flight_pricing_and_seats(flight_id: int):
    """
    Показує кількість вільних місць на конкретний рейс та розраховує вартість квитків за класами.
    """
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    print(f"✈️ [ШІ ВИКЛИК] Перевірка цін для рейсу ID: {flight_id}", flush=True)

    try:
        flight = Flight.objects.select_related('airplane').get(id=flight_id)
        base_price = flight.base_price or 0

        # Отримуємо всі місця цього літака
        all_seats = Seat.objects.filter(airplane=flight.airplane)

        # Шукаємо вже заброньовані або оплачені квитки
        booked_seats_ids = Ticket.objects.filter(
            flight=flight,
            status__in=['booked', 'paid']  # Використай свої статуси з TicketStatus
        ).values_list('seat_id', flat=True)

        # Вільні місця
        available_seats = all_seats.exclude(id__in=booked_seats_ids)

        if not available_seats.exists():
            return {"status": "full", "message": "На цей рейс не залишилося вільних місць."}

        # Групуємо результати для Gemini
        result = {
            "flight_id": flight.id,
            "airplane": flight.airplane.name,
            "classes": {}
        }

        # Проходимося по класах з твоєї моделі Seat
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
        return {"error": f"Рейс з ID {flight_id} не знайдено."}
    except Exception as e:
        print(f"🚨 ПОМИЛКА В TOOLS: {str(e)}", flush=True)
        return {"error": str(e)}

def get_order_info(order_id: int):
    """
    Перевіряє статус замовлення, загальну суму та статус оплати (Stripe).
    """
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    print(f"✈️ [ШІ ВИКЛИК] Перевірка замовлення #{order_id}", flush=True)

    try:
        # Використовуємо select_related для швидкого доступу до оплати
        order = Order.objects.select_related('payment').prefetch_related('tickets__seat').get(id=order_id)

        # Збираємо інформацію про квитки у цьому замовленні
        tickets_list = []
        for ticket in order.tickets.all():
            tickets_list.append({
                "seat_label": ticket.seat.label,
                "class": ticket.seat.seat_class,
                "price": float(ticket.price)
            })

        # Перевіряємо, чи існує об'єкт Payment
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
        return {"error": f"Замовлення #{order_id} не знайдено."}
    except Exception as e:
        print(f"🚨 ПОМИЛКА В TOOLS: {str(e)}", flush=True)
        return {"error": str(e)}
tools_list = [get_available_flights, get_flight_pricing_and_seats, get_order_info]