import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import websocket_chat.routing  # Импортируем routing.py из приложения chat

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(  # Добавляем AuthMiddlewareStack для аутентификации пользователей
        URLRouter(
            websocket_chat.routing.websocket_urlpatterns  # Используем URL-паттерны из chat/routing.py
        )
    ),
})