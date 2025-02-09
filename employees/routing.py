# routing.py
from django.urls import re_path
from .consumers import OrderStatusConsumer
from .consumers import SubscriptionStatusConsumer

websocket_urlpatterns = [
    re_path(r'ws/orders/(?P<order_id>\d+)/$',OrderStatusConsumer.as_asgi()),
    re_path(r'ws/subscriptions/$', SubscriptionStatusConsumer.as_asgi()),  # Shared endpoint
]


