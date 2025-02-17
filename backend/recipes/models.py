from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from foodgram.constants import TAG_MAX_LENGTH


User = get_user_model()


class Tag(models.Model):
    """Модель тэга."""
    name = models.CharField(max_length=TAG_MAX_LENGTH, unique=True)
    slug = models.SlugField(max_length=TAG_MAX_LENGTH, unique=True)


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(max_length=128)
    measurement_unit = models.CharField(max_length=64, default=None)


class Recipe(models.Model):
    """Модель рецепта."""
    name = models.CharField(max_length=256)
    text = models.TextField(blank=False)
    tags = models.ManyToManyField(Tag, blank=False, related_name='recipes')
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1),]
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to='recipes/',
        null=True,
        default=None
    )
    created_at = models.DateTimeField(auto_now_add=True)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        related_name='recipes',
        blank=False,
    )
    is_favorited = models.ManyToManyField(
        User,
        related_name='favorite_recipes',
        blank=True
    )
    is_in_shopping_cart = models.ManyToManyField(
        User,
        related_name='shopping_cart_recipes',
        blank=True
    )
    short_link = models.CharField(
        max_length=32,
        unique=True,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('-created_at',)


class RecipeIngredients(models.Model):
    """Модель для связи рецепта с ингредиентами и их количеством."""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1),]
    )
