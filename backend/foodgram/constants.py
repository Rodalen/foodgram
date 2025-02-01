
USERNAME_MAX_LENGTH = 64
ROLE_MAX_LENGTH = 64
EMAIL_MAX_LENGTH = 64
PATTERN = r'^[\w.@+-]+\Z'
ROLES = (
    ('user', 'авторизованный пользователь'),
    ('admin', 'администратор'),
    ('superuser', 'суперюзер'),
)
