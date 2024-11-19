from django.urls import path
from .views import *

urlpatterns = [
    # URL 패턴 추가 예시
    path('', index, name='index'),  # 기본 경로 설정 (필요에 따라 수정)
    path('recorded-sessions/', get_recorded_sessions, name='recorded-sessions'),
    path('recorded-session/<int:session_id>/', get_recorded_session_detail, name='recorded_session_detail'),
]
