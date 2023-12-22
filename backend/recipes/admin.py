from django.contrib import admin
from .models import Ingredient, Tag, Recipe, IngredientAmount, Favourite


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'text',
        'cooking_time',
        'image',
        'favorites_count'
    )
    list_editable = (
        'name',
        'text',
        'cooking_time',
        'image',
    )
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')

    def favorites_count(self, obj):
        count = Favourite.objects.filter(recipe=obj).count()
        return count


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(IngredientAmount)
