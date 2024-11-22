from django.urls import path
from .consumers import LiveFeedConsumer, FireAlertConsumer

websocket_urlpatterns = [
    path("ws/live_feed/", LiveFeedConsumer.as_asgi()),
    path("ws/fire_alert/", FireAlertConsumer.as_asgi()),
]
