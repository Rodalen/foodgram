from rest_framework import viewsets, permissions
from .models import Tag, Ingredient, Recipe, IsFavorited, IsInShoppingCart
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer, IsFavoritedSerializer, IsInShoppingCartSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        favorite, created = IsFavorited.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            favorite.delete()
        return Response({'status': 'added to favorites' if created else 'removed from favorites'})

    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        shopping_cart, created = IsInShoppingCart.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            shopping_cart.delete()
        return Response({'status': 'added to shopping cart' if created else 'removed from shopping cart'})