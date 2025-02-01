import re

from django.core.exceptions import ValidationError

from foodgram.constants import PATTERN


def UsernameValidator(username):
    if username == 'me':
        raise ValidationError('Имя пользователя не может быть me.')

    if not re.match(PATTERN, username):
        raise ValidationError(
            {'username': ['Неверный формат имени пользователя.']}
        )