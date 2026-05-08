import stripe

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import OrderStatus
from apps.payments.models import Payment, PaymentStatus
from apps.payments.serializers import CreateCheckoutSessionSerializer
from apps.tickets.models import TicketStatus
import time
from django.db import transaction


stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CreateCheckoutSessionSerializer,
        responses={
            201: {
                "type": "object",
                "properties": {
                    "checkout_url": {"type": "string"},
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string"},
                },
            },
        },
    )
    def post(self, request):
        serializer = CreateCheckoutSessionSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        order = serializer.context["order"]

        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={
                "user": request.user,
                "amount": order.total_amount,
                "currency": order.currency,
            },
        )

        if payment.status == PaymentStatus.PAID:
            return Response(
                {"detail": "This order is already paid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if payment.status == PaymentStatus.PENDING:
            payment.amount = order.total_amount
            payment.currency = order.currency
            payment.user = request.user
            payment.save(update_fields=["amount", "currency", "user", "updated_at"])

        checkout_session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": payment.currency,
                        "product_data": {
                            "name": f"Airline order #{order.id}",
                        },
                        "unit_amount": payment.amount * 100,
                    },
                    "quantity": 1,
                }
            ],
            success_url=f"{settings.FRONTEND_URL}/payments/success/",
            cancel_url=f"{settings.FRONTEND_URL}/payments/cancel/",
            expires_at=int(time.time()) + 30 * 60,
            metadata={
                "payment_id": str(payment.id),
                "order_id": str(order.id),
                "user_id": str(request.user.id),
            },
        )

        payment.stripe_checkout_session_id = checkout_session.id
        payment.save(update_fields=["stripe_checkout_session_id", "updated_at"])

        return Response(
            {"checkout_url": checkout_session.url},
            status=status.HTTP_201_CREATED,
        )


def payment_success(request):
    return HttpResponse(
        "Payment success page. Final status will be updated by Stripe webhook."
    )


def payment_cancel(request):
    return HttpResponse("Payment cancelled.")


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        return HttpResponse("Invalid payload", status=400)
    except stripe.SignatureVerificationError:
        return HttpResponse("Invalid signature", status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        metadata = getattr(session, "metadata", None)
        payment_id = getattr(metadata, "payment_id", None) if metadata else None
        payment_intent_id = getattr(session, "payment_intent", None)

        if not payment_id:
            return HttpResponse("Payment id not found in metadata", status=400)

        payment = (Payment.objects.select_related("order").filter(id=payment_id).first())

        if not payment:
            return HttpResponse("Payment not found", status=404)

        with transaction.atomic():
            if payment.status != PaymentStatus.PAID:
                payment.status = PaymentStatus.PAID
                payment.stripe_payment_intent_id = payment_intent_id
                payment.save(update_fields=[
                    "status",
                    "stripe_payment_intent_id",
                    "updated_at",
                ])

                order = payment.order
                order.status = OrderStatus.PAID
                order.save(update_fields=["status"])

                order.tickets.update(status=TicketStatus.PAID)

    elif event["type"] == "checkout.session.expired":
        session = event["data"]["object"]

        metadata = getattr(session, "metadata", None)
        payment_id = getattr(metadata, "payment_id", None) if metadata else None

        if not payment_id:
            return HttpResponse("Payment id not found in metadata", status=400)

        payment = (Payment.objects.select_related("order").filter(id=payment_id).first())

        with transaction.atomic():
            if payment and payment.status == PaymentStatus.PENDING:
                payment.status = PaymentStatus.CANCELLED
                payment.save(update_fields=["status", "updated_at"])

                order = payment.order
                order.status = OrderStatus.CANCELLED
                order.save(update_fields=["status"])

                order.tickets.update(status=TicketStatus.AVAILABLE)

    return HttpResponse(status=200)