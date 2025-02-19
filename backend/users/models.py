from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.constants import EMAIL_MAX_LENGTH, USER_MAX_LENGTH
from foodgram.validators import ValidationMixin


class User(AbstractUser, ValidationMixin):
    username = models.CharField(
        max_length=USER_MAX_LENGTH,
        unique=True,
        validators=[ValidationMixin.username_validator, ]
    )
    email = models.EmailField(  
        max_length=EMAIL_MAX_LENGTH, unique=True
    )
    first_name = models.CharField(max_length=USER_MAX_LENGTH, blank=False)
    last_name = models.CharField(max_length=USER_MAX_LENGTH, blank=False)
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
        return self.is_superuser


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписчик',
        help_text='Подписчик.'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Автор',
        help_text='Автор.'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'following'],
                                    name='Подписаться можно только один раз.')
        ]
