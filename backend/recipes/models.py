from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True)
    slug = models.SlugField(max_length=32, unique=True)


class Ingredient(models.Model):
    name = models.CharField(max_length=32)
    unit = models.CharField(max_length=10)


class Recipe(models.Model):
    name = models.CharField(max_length=32)
    text = models.TextField(blank=True, null=True)
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

    class Meta:
        ordering = ('created_at',)


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.FloatField(
        validators=[MinValueValidator(0),]
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')


class IsFavorited(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'recipe')


class IsInShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'recipe')