from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField

from foodgram_project.constants import USERNAME_MAX_LENGTH
from recipes.models import Recipe
from recipes.validators import username_validator
from .models import CustomUser, Subscriptions


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
        if not current_user.is_authenticated:
            return False
        return current_user.subscribed_to.filter(subscription=obj).exists()

    def to_representation(self, instance):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        if limit:
            instance.recipes.set(instance.recipes.all()[:int(limit)])
        return super().to_representation(instance)
