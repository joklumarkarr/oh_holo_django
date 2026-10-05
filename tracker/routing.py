from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/live-status/", consumers.LiveStatusConsumer.as_asgi()),
]