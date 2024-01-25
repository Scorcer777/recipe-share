from rest_framework import serializers
from rest_framework.validators import ValidationError, UniqueValidator

from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField

from .models import (Ingredient,
                     Recipe, RecipeIngredientList,
                     ShoppingCart, Tag)
from foodgram_project.constants import (MIN_AMOUNT, MAX_AMOUNT,
                                        MIN_COOKING_TIME, MAX_COOKING_TIME,
                                        USERNAME_MAX_LENGTH)
from users.models import CustomUser, Subscriptions
from .validators import username_validator


class RegistrationSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователей."""
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    username = serializers.CharField(
        validators=[
            username_validator,
            UniqueValidator(queryset=CustomUser.objects.all()),
        ]
    )
    password = serializers.CharField(write_only=True,
                                     max_length=USERNAME_MAX_LENGTH,)
    first_name = serializers.CharField(max_length=USERNAME_MAX_LENGTH,)
    last_name = serializers.CharField(max_length=USERNAME_MAX_LENGTH,)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'password')


class ProfileSerializer(UserSerializer):
    """Сериализатор для просмотра данных пользователей."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')
        read_only_fields = ('email', 'username', 'first_name',
                            'last_name')

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        if not current_user.is_authenticated:
            return False
        return Subscriptions.objects.filter(user=current_user,
                                            subscription=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэгов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientListReadOnlySerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра ингредиентов рецепта."""
    id = serializers.ReadOnlyField(source='ingredient.id',)
    name = serializers.ReadOnlyField(source='ingredient.name',)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )
    amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = RecipeIngredientList
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientListCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиентов в рецепте."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        write_only=True,
        min_value=MIN_AMOUNT, max_value=MAX_AMOUNT,
        error_messages={
            'min_value': f'Мин. количество ингридиента - {MIN_AMOUNT}',
            'max_value': f'Макс. количество ингридиента - {MAX_AMOUNT}'
        }
    )

    class Meta:
        model = RecipeIngredientList
        fields = ('id', 'amount')


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    """Сериализатор рецепта(чтение)."""
    tags = TagSerializer(read_only=True, many=True)
    author = ProfileSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    ingredients = RecipeIngredientListReadOnlySerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    name = serializers.CharField(read_only=True)
    image = Base64ImageField(read_only=True)
    text = serializers.CharField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        ingredients = obj.recipe_ingredients.all()
        return RecipeIngredientListReadOnlySerializer(
            ingredients, many=True).data

    def get_is_favorited(self, obj):
        current_user = self.context.get('request').user
        if not current_user.is_authenticated:
            return False
        return current_user.favorite_recipes.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context.get('request').user
        if not current_user.is_authenticated:
            return False
        return current_user.shopping_cart.filter(recipe=obj).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления нового рецепта."""
    ingredients = RecipeIngredientListCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = ProfileSerializer(read_only=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        write_only=True,
        min_value=MIN_COOKING_TIME,
        max_value=MAX_COOKING_TIME,
        error_messages={
            'min_value': f'Мин. время приготовления - {MIN_AMOUNT} минута.',
            'max_value': f'Макс. количество ингридиента - {MAX_AMOUNT} минут.'
        }
    )

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'tags',
                  'name', 'image', 'text', 'cooking_time')

    def create_ingredients(self, recipe, ingredients):
        ingredients_involved = []
        for ingredient in ingredients:
            current_ingredient = ingredient['id']
            amount = ingredient['amount']
            ingredients_involved.append(
                RecipeIngredientList(
                    ingredient=current_ingredient,
                    recipe=recipe,
                    amount=amount
                )
            )
        RecipeIngredientList.objects.bulk_create(ingredients_involved)

    def create(self, validated_data):
        current_user = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=current_user, **validated_data)
        self.create_ingredients(recipe, ingredients)
        if not RecipeIngredientList.objects.filter(recipe=recipe).exists():
            raise serializers.ValidationError('Ингридиенты не добавлены!',
                                              code='invalid')
        recipe.tags.set(tags)
        return recipe

    def to_representation(self, instance):
        return RecipeReadOnlySerializer(instance, context={
            'request': self.context.get('request')
        }).data

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        try:
            ingredients = validated_data.pop('ingredients')
        except KeyError:
            raise serializers.ValidationError('Ингридиенты отсутствуют!',
                                              code='invalid')
        instance.ingredients.all().delete()
        self.create_ingredients(instance, ingredients)
        if not RecipeIngredientList.objects.filter(recipe=instance).exists():
            raise serializers.ValidationError('Ингридиенты не добавлены!',
                                              code='invalid')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.save()
        return instance


class FavouriteAndCartSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в спискок покупок и избранное."""
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate_shopping_cart(self, data):
        current_user = self.context.get('request').user
        if ShoppingCart.objects.filter(user=current_user, recipe=data['id']
                                       ).exists():
            raise ValidationError('Этот рецепт уже есть в списке покупок!')
        return data


class SubscriptionsRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта для подписок(чтение)."""
    name = serializers.CharField(read_only=True)
    image = Base64ImageField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""
    is_subscribed = serializers.SerializerMethodField()
    recipes_limit = serializers.IntegerField(write_only=True, required=False)
    recipes = SubscriptionsRecipeSerializer(
        many=True, read_only=True
    )
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes',
                  'recipes_count', 'recipes_limit')
        read_only_fields = ('email', 'username',
                            'first_name', 'last_name')

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        if current_user.is_authenticated:
            if current_user.subscribed_to.filter(subscription=obj).exists():
                return True
            return False
        return False

    def to_representation(self, instance):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        if limit:
            instance.recipes.set(instance.recipes.all()[:int(limit)])
        return super().to_representation(instance)
