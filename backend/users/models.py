from django.db import models

from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError


EMAIL_MAX_LENGTH = 254
USERNAME_MAX_LENGTH = 150


class CustomUser(AbstractUser):
    '''Кастомная модель пользователя.'''
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    username = models.CharField(
        'Никнейм',
        blank=False,
        max_length=USERNAME_MAX_LENGTH,
        unique=True
    )
    email = models.EmailField(
        'E-mail',
        blank=False,
        max_length=EMAIL_MAX_LENGTH,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        blank=False,
        max_length=USERNAME_MAX_LENGTH)
    last_name = models.CharField(
        'Фамилия',
        blank=False,
        max_length=USERNAME_MAX_LENGTH,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    '''Модель подписок.'''
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='subscribed_to',
    )
    subscription = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Подписан на пользователя',
        related_name='subscribers',
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Объект подписки'
        verbose_name_plural = 'Объекты подпискок'

    def clean(self):
        if self.user == self.subscription:
            raise ValidationError('Вы не можете подписаться на себя!')
        if Subscriptions.objects.filter(
            user=self.user, subscription=self.subscription
        ).exists():
            raise ValidationError('Вы уже подписаны на данного пользователя!')

    def __str__(self):
        return f'{self.user} подписан на {self.subscription}'
