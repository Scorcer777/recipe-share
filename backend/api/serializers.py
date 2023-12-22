from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, ValidationError

from recipes.models import (Favourite, Ingredient, Recipe, IngredientAmount,
                            ShoppingCart, Tag)
from users.models import CustomUser, Follow


MIN_VALUE = 1
MAX_VALUE = 32000


class UserRegistrationSerializer(UserCreateSerializer):
    '''Сериализатор регистрции пользователя.'''
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())])

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class UserProfileSerializer(UserSerializer):
    '''Сериализатор просмотра профиля пользователя.'''
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """
        Метод проверки подписан ли текущий
        пользователь на просматриваемого.
        """
        current_user = self.context.get("request").user
        return (
            Follow.objects.filter(user=current_user, following=obj).exists()
            if current_user.is_authenticated
            else False
        )


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор ингредиентов.'''
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    '''Сериализатор для тэгов.'''

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientAmountReadOnlySerializer(serializers.ModelSerializer):
    '''Сериализатор для просмотра ингредиентов для рецепта.'''
    id = serializers.ReadOnlyField(source='ingredient.id',)
    name = serializers.ReadOnlyField(source='ingredient.name',)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    '''Сериализатор рецепта(чтение).'''
    tags = TagSerializer(read_only=True, many=True)
    author = UserProfileSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'text',
            'cooking_time',
            'ingredients',
            'tags',
            'image',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_ingredients(self, obj):
        ingredients = obj.recipe_ingredients.all()
        return IngredientAmountReadOnlySerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        current_user = self.context.get('request').user
        return (
            current_user.favorites.filter(recipe=obj).exists()
            if current_user.is_authenticated
            else False
        )

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context.get('request').user
        return (
            current_user.shopping_cart.filter(recipe=obj).exists()
            if current_user.is_authenticated
            else False
        )


class IngredientAmountCreateSerializer(serializers.ModelSerializer):
    '''Сериализатор для создания ингредиентов в рецепте.'''
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        write_only=True, max_value=MAX_VALUE, min_value=MIN_VALUE)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор для добавления нового рецепта.'''
    author = UserProfileSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    cooking_time = serializers.IntegerField(
        max_value=MAX_VALUE, min_value=MIN_VALUE)
    ingredients = IngredientAmountCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'text',
            'cooking_time',
            'ingredients',
            'tags',
            'image',
        )

    def create_ingredients(self, recipe, ingredients):
        recipe_ingredients = []
        for ingredient in ingredients:
            current_ingredient = ingredient['id']
            amount = ingredient['amount']
            recipe_ingredients.append(
                IngredientAmount(
                    ingredient=current_ingredient,
                    recipe=recipe,
                    amount=amount
                )
            )
        IngredientAmount.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.tags.set(tags)
        instance.ingredients.all().delete()
        self.create_ingredients(instance, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadOnlySerializer(instance, context={
            "request": self.context.get("request")
        }).data


class FavorShopCartRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор для добавления рецепта в спискок покупок и избранное.'''
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )

    def validate_favorited(self, data):
        current_user = self.context.get('request').user
        if Favourite.objects.filter(user=current_user, recipe=data['id']
                                    ).exists():
            raise ValidationError('Этот рецепт уже есть в избранном!')
        return data

    def validate_shopping_cart(self, data):
        current_user = self.context.get('request').user
        if ShoppingCart.objects.filter(user=current_user, recipe=data['id']
                                       ).exists():
            raise ValidationError('Этот рецепт уже есть в списке покупок!')
        return data


class FollowSerializer(serializers.ModelSerializer):
    '''Сериализатор подписок.'''
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = FavorShopCartRecipeSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        return (
            current_user.follows.filter(following=obj).exists()
            if current_user.is_authenticated
            else False
        )

    def validate(self, data):
        current_user = self.context.get('request').user
        if Follow.objects.filter(user=current_user, following=data['id']
                                 ).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя!')
        if self.context.get('request').user.id == data['id']:
            raise ValidationError('Невозможно подписаться на самого себя!')
        return data
