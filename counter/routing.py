from django.urls import re_path

from counter import consumers

websocket_urlpatterns = [
    re_path(r"ws/counter", consumers.CountConsumer.as_asgi()),
]