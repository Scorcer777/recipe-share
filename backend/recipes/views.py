from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.validators import ValidationError
from .filters import RecipeFilter, IngredientFilter
from .pagination import CustomPagination
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
    '''Вьюсет для тегов.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Вьюсет для игредиентов.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    '''Вьюсет для рецептов.'''
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadOnlySerializer
        else:
            return RecipeCreateSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        current_recipe = get_object_or_404(Recipe, pk=pk)
        current_user = request.user
        if request.method == 'POST':
            if Favourite.objects.filter(user=current_user,
                                        recipe=current_recipe).exists():
                raise ValidationError('Этот рецепт уже есть в избранном!')
            Favourite.objects.create(user=current_user, recipe=current_recipe)
            serializer = FavouriteAndCartSerializer(
                current_recipe, context={'request': request})
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)
        else:
            if not Favourite.objects.filter(user=current_user,
                                            recipe=current_recipe).exists():
                raise ValidationError('Этого рецепта не было в избранном!')
            favorite_to_delete = get_object_or_404(
                Favourite, user=current_user, recipe=current_recipe
            )
            favorite_to_delete.delete()
            return Response({'message': 'Рецепт удален из избранного'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        current_recipe = get_object_or_404(Recipe, pk=pk)
        current_user = request.user
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=current_user,
                                           recipe=current_recipe).exists():
                raise ValidationError(
                    'Этот рецепт уже есть в списке покупок!'
                )
            ShoppingCart.objects.create(user=current_user,
                                        recipe=current_recipe)
            serializer = FavouriteAndCartSerializer(
                current_recipe, context={'request': request})
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)
        else:
            if not ShoppingCart.objects.filter(user=current_user,
                                               recipe=current_recipe).exists():
                raise ValidationError(
                    'Этого рецепта не было в списке покупок!'
                )
            shopping_cart_to_delete = get_object_or_404(
                ShoppingCart, user=current_user, recipe=current_recipe
            )
            shopping_cart_to_delete.delete()
            return Response({'message': 'Рецепт удален из списка покупок'},
                            status=status.HTTP_204_NO_CONTENT)

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
            print(string_list)
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
