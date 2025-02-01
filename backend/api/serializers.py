from rest_framework import serializers

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient, IsFavorited, IsInShoppingCart


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'amount']

class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(source='ingredients', many=True)
    class Meta:
        model = Recipe


class IsFavoritedSerializer(serializers.ModelSerializer):
    class Meta:
        model = IsFavorited
        fields = ['user', 'recipe']


class IsInShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = IsInShoppingCart
        fields = ['user', 'recipe']