from django.urls import path

from apps.payments.views import (
    CreateCheckoutSessionView,
    payment_cancel,
    payment_success,
    stripe_webhook,
)

urlpatterns = [
    path(
        "create-checkout-session/",
        CreateCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
    path("success/", payment_success, name="payment-success"),
    path("cancel/", payment_cancel, name="payment-cancel"),
    path("webhook/", stripe_webhook, name="stripe-webhook"),
]