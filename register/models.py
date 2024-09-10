# register/models.py

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, username, name, password=None):
        if not username:
            raise ValueError('Users must have a username')
        if not name:
            raise ValueError('Users must have a name')

        user = self.model(
            username=username,
            name=name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, name, password=None):
        user = self.create_user(
            username=username,
            name=name,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True  # 슈퍼유저 속성도 설정
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=128)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)  # 슈퍼유저 속성 추가

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.username

    @property
    def is_active(self):
        return True

    def has_perm(self, perm, obj=None):
        """
        특정 권한이 있는지를 확인하는 메서드.
        슈퍼유저라면 항상 True를 반환.
        """
        return self.is_superuser

    def has_module_perms(self, app_label):
        """
        사용자가 주어진 앱(app_label)에 접근할 수 있는지를 확인하는 메서드.
        슈퍼유저라면 항상 True를 반환.
        """
        return self.is_superuser
