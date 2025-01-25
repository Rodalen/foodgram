from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

User = get_user_model()


class Tag(models.Model):
    id = models.IntegerField()
    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length=32, unique=True)


class Ingredient(models.Model):
    name = models.CharField(max_length=32)
    weight = models.CharField(max_length=2)


class Recipe(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField()
    ingredients = models.Choices()
    tag = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1),]
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        # upload_to=
        null=True,
        default=None
    )

    is_favorited = models.ForeignKey(User)
    is_in_shopping_cart = models.ForeignKey(User)

    class Meta:
        ordering = ('created_at',)
