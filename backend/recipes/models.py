from django.db import models
from django.utils.html import format_html
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model


MIN_VALIDATION = 1
MAX_VALIDATION = 100
MAX_LENGTH = 200


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField('Наименование ингридиента',
                            max_length=MAX_LENGTH)
    measurement_unit = models.CharField('Ед. измерения',
                                        max_length=MAX_LENGTH)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit_list',
            ),
        ]
        ordering = ('name',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField('Тег', max_length=MAX_LENGTH,
                            unique=True)
    color = models.CharField('Цвет', max_length=7,
                             unique=True, null=True)
    slug = models.SlugField('Cлаг', max_length=MAX_LENGTH,
                            unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes'
    )
    name = models.CharField('Название рецепта', max_length=MAX_LENGTH)
    text = models.TextField('Описание',)
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления мин.',
        validators=[
            MinValueValidator(
                MIN_VALIDATION,
                'Минимальное время приготовелния - 1 минута.'
            ),
            MaxValueValidator(MAX_VALIDATION, 'Перебор!')]
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientAmount', verbose_name='Ингридиенты'
    )
    tags = models.ManyToManyField(
        Tag, verbose_name='Теги', related_name='recipes'
    )
    image = models.ImageField('Изображение блюда', upload_to='recipes/')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
        db_index=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = ('Рецепт')
        verbose_name_plural = ('Рецепты')

    def __str__(self):
        return self.name

    def formatted_text(self):
        return format_html('<br>'.join(self.text.splitlines()))


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт',
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингридиент',
        null=True, related_name='ingredient_recipes'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                MIN_VALIDATION,
                message='Минимальное количество ингридиента = 1'
            ),
            MaxValueValidator(MAX_VALIDATION, message='Перебор!')
        ]
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Рецепт - Ингридиент - Количество'
        verbose_name_plural = 'Рецепты - Ингридиенты - Количества'
        # В рецепте каждый ингридиент может фигурировать только один раз.
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient_list',
            ),
        ]

    def __str__(self):
        return f'{self.recipe}: {self.ingredient} - {self.amount}'


class UserRecipeModel(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')

    class Meta:
        abstract = True
        ordering = ('recipe',)


class Favourite(UserRecipeModel):

    class Meta(UserRecipeModel.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_favorite_list',
            ),
        ]


class ShoppingCart(UserRecipeModel):

    class Meta(UserRecipeModel.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart_list',
            ),
        ]
