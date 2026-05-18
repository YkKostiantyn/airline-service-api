"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.assistant.routing import websocket_urlpatterns
# Створюємо маршрутизатор
application = ProtocolTypeRouter({
    # Звичайні HTTP запити йдуть стандартним шляхом
    "http": get_asgi_application(),

    # WebSocket запити обгортаємо в перевірку авторизації та віддаємо нашому routing.py
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
