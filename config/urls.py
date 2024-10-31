"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# myproject/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', include('register.urls')),  # Include the register app's URLs
    path('api/login/', include('login.urls')),        # Include the login app's URLs
    path('main/', include('main.urls')),


    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('', include('django_prometheus.urls')),  # Prometheus 메트릭 엔드포인트 추가
    path('status/', include('status.urls')),

]
