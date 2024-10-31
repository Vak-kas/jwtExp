from django.urls import re_path
from .consumers import MetricsConsumer  # wsocket.py에서 MetricsConsumer를 임포트

websocket_urlpatterns = [
    re_path(r'ws/metrics/$', MetricsConsumer.as_asgi()),
]
