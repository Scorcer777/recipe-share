from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from recipes.models import Recipe
from .models import CustomUser, Subscriptions


class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'password',
        'subscribers_count',
        'recipes_count'
    )
    search_fields = ('email',)
    list_filter = ('username', 'email')

    @admin.display(description='Количество подписчиков')
    def subscribers_count(self, obj):
        count = Subscriptions.objects.filter(user=obj).count()
        return count

    @admin.display(description='Количество рецептов')
    def recipes_count(self, obj):
        count = Recipe.objects.filter(author=obj).count()
        return count


admin.site.register(CustomUser, CustomUserAdmin)
