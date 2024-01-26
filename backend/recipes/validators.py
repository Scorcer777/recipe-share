from django.core.exceptions import ValidationError

import re

from .models import Favourite


def username_validator(value):
    if value == 'me':
        raise ValidationError(
            'Имя пользователя "me" недопустимо!'
        )
    if len(value) > 150:
        raise ValidationError(
            'Имя пользователя не может превышать 150 символов'
        )

    if re.search(r'^[\w.@+-]+$', value) is None:
        raise ValidationError(
            'Недопустимые символы в имени пользователя'
        )


def favorite_validator(request, data):
    current_user = request.user
    return Favourite.objects.filter(
        user=current_user, recipe=data['id']
    ).exists()
