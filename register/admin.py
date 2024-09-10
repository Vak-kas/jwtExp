# register/admin.py

from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    # 관리자 페이지에서 표시할 필드들 (이메일 제외)
    list_display = ('id', 'username', 'name', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser')
    search_fields = ('username', 'name')
    ordering = ('id',)

# 사용자 모델을 관리자 페이지에 등록
admin.site.register(User, UserAdmin)
