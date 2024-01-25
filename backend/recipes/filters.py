from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class IngredientFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )

    is_favorited = filters.BooleanFilter(
        method='get_objects_or_none')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_objects_or_none'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags',
                  'is_in_shopping_cart', 'is_favorited')

    def get_objects_or_none(self, queryset, name, value):
        FILTERS_DICT = {
            'is_favorited': Recipe.objects.filter(
                favorite_recipes__user=self.request.user
            ),
            'is_in_shopping_cart': Recipe.objects.filter(
                shopping_cart__user=self.request.user
            )
        }
        if value:
            return FILTERS_DICT[name]
        return Recipe.objects.none
