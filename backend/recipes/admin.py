from django.contrib import admin

from .models import (Recipe, Ingredient, Tag,
                     RecipeIngredientList, RecipeTagList,
                     Favourite, ShoppingCart)
from users.models import Subscriptions


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'text',
        'cooking_time',
        'image',
        'favorites_count',
        'ingredient_list',
        'tag_list'
    )
    list_editable = (
        'name',
        'text',
        'cooking_time',
        'image',
    )
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')

    @admin.display(description='Количество рецептов в избранном')
    def favorites_count(self, obj):
        count = Favourite.objects.filter(recipe=obj).count()
        return count

    @admin.display(description='Инридиенты')
    def ingredient_list(self, obj):
        ingredients = RecipeIngredientList.objects.filter(
            recipe=obj.id
        ).values_list('ingredient__name', flat=True)
        return ingredients

    @admin.display(description='Теги')
    def tag_list(self, obj):
        tags = RecipeTagList.objects.filter(
            recipe=obj.id
        ).values_list('tag__name', flat=True)
        return tags


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, admin.ModelAdmin)
admin.site.register(RecipeIngredientList, admin.ModelAdmin)
admin.site.register(RecipeTagList, admin.ModelAdmin)
admin.site.register(Favourite, admin.ModelAdmin)
admin.site.register(Subscriptions, admin.ModelAdmin)
admin.site.register(ShoppingCart, admin.ModelAdmin)
