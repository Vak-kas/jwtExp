from django.urls import path
from . import views

urlpatterns = [
    # URL 패턴 추가 예시
    path('', views.index, name='index'),  # 기본 경로 설정 (필요에 따라 수정)
]
