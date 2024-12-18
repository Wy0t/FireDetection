from django.urls import path
from .consumers import WebRTCConsumer, AlertConsumer

websocket_urlpatterns = [
    path("ws/webrtc/", WebRTCConsumer.as_asgi()),
    path("ws/alerts/", AlertConsumer.as_asgi()),
]
