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
        return obj.favorite_recipes.all().count()

    @admin.display(description='Инридиенты')
    def ingredient_list(self, obj):
        return obj.recipe_ingredients.all().values_list(
            'ingredient__name', flat=True
        )

    @admin.display(description='Теги')
    def tag_list(self, obj):
        return obj.recipe_tags.all().values_list('tag__name', flat=True)


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
