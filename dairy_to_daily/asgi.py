"""
ASGI config for dairy_to_daily project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack 
from employees import routing 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dairy_to_daily.settings')


# Define the application
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handles HTTP requests
    "websocket": AuthMiddlewareStack(  # Handles WebSocket connections with authentication middleware
        URLRouter(
            routing.websocket_urlpatterns  # Points to the URL routing for WebSockets
        )
    ),
})