from django.urls import path
from .consumers import WebRTCConsumer

websocket_urlpatterns = [
    path("ws/webrtc/", WebRTCConsumer.as_asgi()),
]
