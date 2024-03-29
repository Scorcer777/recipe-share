from django.db import models
from django.utils.html import format_html
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

from colorfield.fields import ColorField

from foodgram_project.constants import (MIN_AMOUNT, MAX_AMOUNT,
                                        MIN_COOKING_TIME, MAX_COOKING_TIME,
                                        MAX_STRING_LENGTH)


User = get_user_model()


class Ingredient(models.Model):
    """Модель ингридиентов."""
    name = models.CharField('Наименование ингридиента',
                            max_length=MAX_STRING_LENGTH)
    measurement_unit = models.CharField('Ед. измерения',
                                        max_length=MAX_STRING_LENGTH)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit_list',
            ),
        )
        ordering = ('name',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField('Тег', max_length=MAX_STRING_LENGTH,
                            unique=True)
    color = ColorField('Цвет', format='hex',
                       unique=True, null=True)
    slug = models.SlugField('Cлаг', max_length=MAX_STRING_LENGTH,
                            unique=True, null=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes'
    )
    name = models.CharField('Название рецепта', max_length=MAX_STRING_LENGTH)
    text = models.TextField('Описание',)
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления мин.',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                message=f'Минимальное время приготовелния - {MIN_COOKING_TIME}'
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message=f'Минимальное время приготовелния - {MAX_COOKING_TIME}'
            )
        ]
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredientList', verbose_name='Ингридиенты'
    )
    tags = models.ManyToManyField(
        Tag, verbose_name='Теги',
        through='RecipeTagList',
        related_name='recipes'
    )
    image = models.ImageField('Изображение блюда', upload_to='recipes/')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
        db_index=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    def formatted_text(self):
        return format_html('<br>'.join(self.text.splitlines()))


class RecipeTagList(models.Model):
    """Модель связи рецепта c тегами."""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт',
        related_name='recipe_tags'
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, verbose_name='Тег',
        null=True, related_name='tag_recipes'
    )

    class Meta:
        ordering = ('tag',)
        verbose_name = 'Тег в рецепте'
        verbose_name_plural = 'Теги в рецептах'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'tag'),
                name='unique_recipe_tag_list',
            ),
        )

    def __str__(self):
        return f'{self.recipe}: {self.tag}'


class RecipeIngredientList(models.Model):
    """Модель связи рецепта количества ингридиента."""
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
                MIN_AMOUNT,
                message=f'Минимальное количество ингридиента = {MIN_AMOUNT}'
            ),
            MaxValueValidator(
                MAX_AMOUNT,
                message=f'Максимальное количество ингридиента = {MAX_AMOUNT}')
        ]
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Ингридеиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient_list',
            ),
        )

    def __str__(self):
        return f'{self.recipe}: {self.ingredient} - {self.amount}'


class UserRecipeModel(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')

    class Meta:
        abstract = True


class Favourite(UserRecipeModel):
    """Модель избранных рецептов."""

    class Meta:
        default_related_name = 'favorite_recipes'
        verbose_name = 'Объект избранного'
        verbose_name_plural = 'Объекты избранного'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_favorite_list',
            ),
        )
        ordering = ('recipe',)

    def __str__(self):
        return f'{self.user}: {self.recipe}'


class ShoppingCart(UserRecipeModel):
    """Модель модель списка покупок."""
    class Meta:
        default_related_name = 'shopping_cart'
        verbose_name = 'Объект корзины'
        verbose_name_plural = 'Объекты корзины'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart_list',
            ),
        )
        ordering = ('recipe',)

    def __str__(self):
        return f'{self.user}: {self.recipe}'
