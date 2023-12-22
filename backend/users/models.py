from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser


EMAIL_MAX_LENGTH = 254
USERNAME_MAX_LENGTH = 150


class CustomUser(AbstractUser):
    '''Кастомная модель пользователя.'''
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    username = models.CharField(
        'Никнейм',
        max_length=USERNAME_MAX_LENGTH,
        unique=True
    )
    email = models.EmailField(
        'E-mail',
        blank=False,
        max_length=EMAIL_MAX_LENGTH,
        unique=True
    )
    first_name = models.CharField('Имя', max_length=USERNAME_MAX_LENGTH)
    last_name = models.CharField('Фамилия', max_length=USERNAME_MAX_LENGTH)

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    '''Модель подписок.'''
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='follows',
    )
    following = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Подписан на пользователя',
        related_name='is_followed_by',
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def restrictions(self):
        if self.user == self.following:
            raise ValidationError(
                'Нельзя подписаться на себя!'
            )
        if Follow.objects.filter(
                user=self.user, following=self.following).exists():
            raise ValidationError(
                'Вы уже подписаны на данного пользователя!'
            )
        return super().save(self)

    def __str__(self):
        return f'{self.user} подписан на {self.following}'
