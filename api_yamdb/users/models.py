from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from users.validators import SelfValidate


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLE_POOL = [
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь'),
    ]

    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        validators=[SelfValidate, username_validator]
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        unique=True
    )
    bio = models.TextField(
        'Биография',
        null=True,
        blank=True
    )
    role = models.CharField(
        'Роль пользователя',
        max_length=40,
        choices=ROLE_POOL,
        default=USER
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR or self.is_staff

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'

        constraints = [
            models.CheckConstraint(
                check=~models.Q(username__iexact='me'),
                name='username_is_not_me'
            )
        ]
