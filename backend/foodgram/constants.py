EMAIL_MAX_LENGTH = 254
USER_MAX_LENGTH = 150
TAG_MAX_LENGTH = 32
PATTERN = r'^[\w.@+-]+\Z'
ROLES = (
    ('user', 'авторизованный пользователь'),
    ('admin', 'администратор'),
    ('superuser', 'суперюзер'),
)
