from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class IngredientFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(FilterSet):

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    is_favorited = filters.BooleanFilter(
        method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags',
                  'is_in_shopping_cart', 'is_favorited']

    def get_is_favorited(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(
                favorite_recipes__user=self.request.user
            )
        return Recipe.objects.none

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(
                shopping_cart__user=self.request.user
            )
        return Recipe.objects.none
