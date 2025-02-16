from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404

from foodgram.helpers_serializers import Base64ImageField
from .models import Tag, Ingredient, Recipe, RecipeIngredients
from users.serializers import UserSerializer


User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэгов."""

    class Meta:
        model = Tag
        fields = ('__all__')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('__all__')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для связи рецепта с ингредиентами."""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        abstract = True
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        """Получение списка ингредиентов для рецепта."""
        recipe_ingredients = obj.recipe_ingredients.all()
        return RecipeIngredientSerializer(recipe_ingredients, many=True).data

    def get_is_favorited(self, obj):
        """Проверка на наличие рецепта в избранном."""
        user = self.context.get('request').user
        return obj.is_favorited.filter(pk=user.pk).exists()
    
    def get_is_in_shopping_cart(self, obj):
        """Проверка на наличие рецепта в корзине."""
        user = self.context.get('request').user
        return obj.is_in_shopping_cart.filter(pk=user.pk).exists()


class RecipeCreateSerializer(RecipeSerializer):
    """Сериализатор для создания рецепта."""
    ingredients = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()),
        required=True,
    )
    tags = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    image = Base64ImageField(
        required=True,
        allow_null=False
    )

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text', 'cooking_time')

    def validate_ingredients(self, value):
        """Проверка на корректность добавленных ингредиентов при создании рецепта."""
        errors = []
        if not value:
            errors.append('Ингредиенты обязательны.')
        unique_ingredients = set()
        for ingredient in value:
            if ingredient['id'] in unique_ingredients:
                errors.append('Ингредиенты должы быть уникальными.')
            unique_ingredients.add(ingredient['id'])
            if ingredient['amount'] <= 0:
                errors.append('Количество должно быть больше 0.')
            if not Ingredient.objects.filter(id=ingredient['id']).exists():
                errors.append('Ингредиента не существует.')
        if errors:
            raise serializers.ValidationError(errors)
        return value
    
    def validate_tags(self, value):
        """Проверка на корректность выбранных тэгов."""
        errors = []
        if not value:
            errors.append('Тэги обязательны.')
        unique_tags = set()
        for tag in value:
            if tag in unique_tags:
                errors.append('Тэги должы быть уникальными.')
            unique_tags.add(tag)
            if not Tag.objects.filter(id=tag).exists():
                errors.append('Тэга не существует.')
        if errors:
            raise serializers.ValidationError(errors)
        return value
 
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe_ingredients = [
            RecipeIngredients(recipe=recipe, ingredient_id=ingr['id'], amount=ingr['amount']) for ingr in ingredients
        ]
        RecipeIngredients.objects.bulk_create(recipe_ingredients)
        return recipe
    
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        if not tags:
            raise serializers.ValidationError('Тэги обязательны.')
        if not ingredients:
            raise serializers.ValidationError('Ингредиенты обязательны.')
        RecipeIngredients.objects.filter(recipe=instance).delete()
        recipe_ingredients = [
        RecipeIngredients(recipe=instance, ingredient_id=ingr['id'], amount=ingr['amount']) for ingr in ingredients
        ]
        RecipeIngredients.objects.bulk_create(recipe_ingredients)
        instance.tags.set(tags)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    

class RecipeFavoriteShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для ответа при добавлении рецепта в избранное или корзину."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
  