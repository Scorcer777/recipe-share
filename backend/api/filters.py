from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Favourite, Recipe, ShoppingCart, Tag, User

CHOICES = (
    ('0', 'False'),
    ('1', 'True')
)


class RecipeFilter(FilterSet):
    '''Фильтр рецептов.'''
    is_favorited = filters.ChoiceFilter(
        choices=CHOICES,
        method='get_is_flagged',
    )
    is_in_shopping_cart = filters.ChoiceFilter(
        choices=CHOICES,
        method='get_is_flagged',
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    def get_is_flagged(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return Recipe.objects.none()

        if name == 'is_favorited':
            flag_model = Favourite
        elif name == 'is_in_shopping_cart':
            flag_model = ShoppingCart

        flagged_items = flag_model.objects.filter(user=user)
        recipes_id = [item.recipe.id for item in flagged_items]

        if value == '1':
            return queryset.filter(id__in=recipes_id)
        return queryset.exclude(id__in=recipes_id)

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')


class IngredientSearch(SearchFilter):
    search_param = 'name'
