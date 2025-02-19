from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from foodgram.constants import (TAG_MAX_LENGTH,
                                INGREDIENT_NAME_MAX_LENGTH,
                                MEASUREMENT_UNIT_MAX_LENGTH,
                                RECIPE_NAME_MAX_LENGTH,
                                SHORT_LINK_MAX_LENGTH)


User = get_user_model()


class Tag(models.Model):
    """Модель тэга."""
    name = models.CharField(
        max_length=TAG_MAX_LENGTH,
        unique=True,
        verbose_name='Тег',
        help_text='Теги для рецептов.'
    )
    slug = models.SlugField(
        max_length=TAG_MAX_LENGTH,
        unique=True,
        verbose_name='Слаг тега',
        help_text='Идентификаторы тегов.')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        verbose_name='Ингредиента',
        help_text='Название ингредиента.'
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_MAX_LENGTH,
        default=None,
        verbose_name='Единица измерения',
        help_text='Единица измерения ингредиента.'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    """Модель рецепта."""
    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LENGTH,
        verbose_name='Блюдо',
        help_text='Название рецепта.'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Опишите рецепт и шаги приготовления.'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги рецепта',
        help_text='Укажите теги рецепта.'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[
            MinValueValidator(
                1, message='Время приготовления не может быть меньше 1 минуты.'
            ),
        ],
        verbose_name='Время приготовления',
        help_text='Время приготовления в минутах.'
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор',
        help_text='Автор рецепта.'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение',
        help_text='Фото блюда в формате jpg/png.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время создания рецепта',
        help_text='Дата и время создания рецепта.'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        related_name='recipes',
        verbose_name='Ингредиенты',
        help_text='Ингредиенты и их количество для приготовления блюда.'
    )
    short_link = models.CharField(
        max_length=SHORT_LINK_MAX_LENGTH,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Короткая ссылка',
        help_text='Короткая ссылка на рецепт.'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)


class RecipeIngredients(models.Model):
    """Модель для связи рецепта с ингредиентами и их количеством."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
        help_text='Связанный с ингредиентом рецепт.'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        help_text='Связанный с рецептом ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1, message='Время приготовления не может быть меньше 1 минуты.'
            ),
        ],
        verbose_name='Количество ингредиента',
        help_text='Количество ингредиента для рецепта.'
    )

    class Meta:
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'


class Favorited(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorite_recipes'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorited_by'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_cart_recipes'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='in_shopping_cart_of'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            )
        ]
