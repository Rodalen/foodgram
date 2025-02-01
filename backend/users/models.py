from django.contrib.auth.models import AbstractUser

from django.db import models

from foodgram.constants import ROLES, ROLE_MAX_LENGTH, EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH
from foodgram.validators import UsernameValidator


class User(AbstractUser):
    role = models.CharField(max_length=ROLE_MAX_LENGTH, choices=ROLES, default='user')
    email = models.EmailField(max_length=EMAIL_MAX_LENGTH, unique=True)
    username = models.CharField(max_length=USERNAME_MAX_LENGTH, unique=True, validators=[UsernameValidator,])

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser