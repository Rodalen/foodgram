import base64

from django.contrib.auth.models import AbstractUser

from django.db import models

from foodgram.constants import ROLES, EMAIL_MAX_LENGTH, USER_MAX_LENGTH
from foodgram.validators import UsernameValidator


class User(AbstractUser):
    username = models.CharField(max_length=USER_MAX_LENGTH, unique=True, validators=[UsernameValidator,])
    email = models.EmailField(max_length=EMAIL_MAX_LENGTH, blank=False, unique=True)
    first_name = models.CharField(max_length=USER_MAX_LENGTH, blank=False)
    last_name = models.CharField(max_length=USER_MAX_LENGTH, blank=False)
    role = models.CharField(max_length=USER_MAX_LENGTH, choices=ROLES, default='user')
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
    

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')

    class Meta:
        unique_together = ('user', 'following')