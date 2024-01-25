from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.validators import ValidationError

from .filters import RecipeFilter, IngredientFilter
from .permissions import IsAuthorOrReadOnly
from .models import (Favourite,
                     Tag,
                     Ingredient,
                     Recipe,
                     RecipeIngredientList,
                     ShoppingCart)
from .serializers import (RecipeCreateSerializer,
                          FavouriteAndCartSerializer,
                          IngredientSerializer,
                          RecipeReadOnlySerializer,
                          TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для игредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadOnlySerializer
        return RecipeCreateSerializer

    def favor_shopcart_post(self, request, pk, model):
        if not Recipe.objects.filter(pk=pk).exists():
            return Response(
                {'message': 'Такого рецепта не существует!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        current_recipe = Recipe.objects.get(pk=pk)
        current_user = request.user
        if model.objects.filter(user=current_user,
                                recipe=current_recipe).exists():
            raise ValidationError('Этот рецепт уже есть!')
        model.objects.create(user=current_user, recipe=current_recipe)
        serializer = FavouriteAndCartSerializer(
            current_recipe, context={'request': request})
        return Response(data=serializer.data,
                        status=status.HTTP_201_CREATED)

    def favor_shopcart_delete(self, request, pk, model):
        current_recipe = get_object_or_404(Recipe, pk=pk)
        current_user = request.user
        if not model.objects.filter(user=current_user,
                                    recipe=current_recipe).exists():
            raise ValidationError('Этого рецепта не было!')
        object_to_delete = get_object_or_404(
            model, user=current_user, recipe=current_recipe
        )
        object_to_delete.delete()
        return Response({'message': 'Рецепт удален'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        return self.favor_shopcart_post(request, pk, Favourite)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.favor_shopcart_delete(request, pk, Favourite)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        return self.favor_shopcart_post(request, pk, ShoppingCart)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.favor_shopcart_delete(request, pk, ShoppingCart)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart_recipes = ShoppingCart.objects.filter(
            user=user).values('recipe')
        ingredients = RecipeIngredientList.objects.filter(
            recipe__in=shopping_cart_recipes).values('ingredient')
        # Фильтрация через default_related_name модели ShoppingCart
        # никаким образом не получилась.
        # К примеру пробовал так shopping_cart__recipe=recipe.
        # Перепробовал множество вариантов. Нужна подсказка:)
        aggregated_ingredients = RecipeIngredientList.objects.filter(
            recipe__in=shopping_cart_recipes,
            ingredient__in=ingredients
        ).values('ingredient__name', 'ingredient__measurement_unit').annotate(
            total_amount=Sum('amount')
        )
        dict = {}
        for ingredient in aggregated_ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['total_amount']
            if name not in dict:
                dict[name] = {'unit': unit, 'amount': amount}
            elif name in dict and dict[name]['unit'] == unit:
                dict[name]['amount'] += amount
        string_list = ['Ваш список покупок:']
        n = 1
        for ingredient_name, value in dict.items():
            line = (f'{n}. {ingredient_name}: '
                    f'{value["amount"]} {value["unit"] }')
            string_list.append(line)
            n += 1
        text = '\n'.join(string_list)
        response = HttpResponse(
            text,
            'Content-Type: application/pdf',
            headers={
                "Content-Disposition": ('attachment; '
                                        'filename="shopping_list.txt"')
            }
        )
        return response
