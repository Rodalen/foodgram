import uuid

from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from api.permissions import FoodgramPermission
from foodgram.filters import NameFilter, RecipeFilter
from .models import (Ingredient, Recipe, RecipeIngredients,
                     Tag, Favorited, ShoppingCart)
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeFavoriteShoppingCartSerializer,
                          RecipeSerializer, TagSerializer,
                          FavoritedSerializer, ShoppingCartSerializer)


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,
                 mixins.RetrieveModelMixin):
    """Вьюсет для тэгов."""
    permission_classes = [permissions.AllowAny, ]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):
    """Вьюсет для ингредиентов."""
    permission_classes = [permissions.AllowAny, ]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [NameFilter, ]
    search_fields = ['name', ]


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    permission_classes = [FoodgramPermission]
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ['create', 'patch', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeSerializer

    def create_or_update(self, request, instance=None):
        """Создание или обновление рецепта."""
        serializer = RecipeCreateSerializer(
            data=request.data,
            context=self.get_serializer_context(),
            instance=instance,
            partial=(instance is not None)
        )
        serializer.is_valid(raise_exception=True)
        if not request.data.get('image') and not instance:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if instance:
            recipe = serializer.save()
        else:
            recipe = serializer.save(author=self.request.user)
        output_serializer = RecipeSerializer(
            recipe, context=self.get_serializer_context()
        )
        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK if instance else status.HTTP_201_CREATED
        )

    def create(self, request, *args, **kwargs):
        return self.create_or_update(request)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.create_or_update(request, instance)

    @action(detail=False, methods=['GET'],
            url_path=r'(?P<recipe_id>\d+)/get-link')
    def get_short_link(self, request, recipe_id):
        """Получение (создание) короткой ссылки на рецепт."""
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if not recipe.short_link:
            link = uuid.uuid4().hex[:3]
            recipe.short_link = link
            recipe.save()
        url = f"{request.get_host()}/s/{recipe.short_link}"
        return Response({'short-link': url}, status=status.HTTP_200_OK)

    @staticmethod
    def create_object(request, pk, serializer_class):
        """Метод для создания объектов."""
        user = request.user.id
        recipe = get_object_or_404(Recipe, pk=pk)
        if not recipe:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = serializer_class(
            data={'user': user, 'recipe': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = RecipeFavoriteShoppingCartSerializer(
            recipe, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_object(request, pk, model):
        """Метод для удаления объектов."""
        user = request.user.id
        recipe = get_object_or_404(Recipe, pk=pk)
        if not recipe:
            return Response(status=status.HTTP_404_NOT_FOUND)
        obj = model.objects.filter(user=user, recipe=recipe)
        if not obj.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['POST'],
            permission_classes=[permissions.IsAuthenticated],
            url_path=r'(?P<recipe_id>\d+)/favorite')
    def favorite(self, request, recipe_id):
        """Добавление рецепта в избранное."""
        return self.create_object(
            request=request,
            pk=recipe_id,
            serializer_class=FavoritedSerializer
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, recipe_id):
        """Удаление рецепта из избранного."""
        return self.delete_object(
            request=request,
            pk=recipe_id,
            model=Favorited
        )

    @action(detail=False, methods=['POST'],
            permission_classes=[permissions.IsAuthenticated],
            url_path=r'(?P<recipe_id>\d+)/shopping_cart')
    def shopping_cart(self, request, recipe_id):
        """Добавление рецепта в корзину."""
        return self.create_object(
            request=request,
            pk=recipe_id,
            serializer_class=ShoppingCartSerializer
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, recipe_id):
        """Удаление рецепта из корзины."""
        return self.delete_object(
            request=request,
            pk=recipe_id,
            model=ShoppingCart
        )

    @action(detail=False, methods=['GET'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        """Скачивание корзины."""
        user = request.user
        recipes = [
            item.recipe for item in ShoppingCart.objects.filter(
                user=user
            ).select_related('recipe')
        ]
        cart = ['Список покупок:\n\n']
        ingredients = (
            RecipeIngredients.objects
            .filter(recipe__in=recipes)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=models.Sum('amount'))
            .order_by('ingredient__name')
        )
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['total_amount']
            cart.append(f'- {name} - {amount} {unit}\n')
        file_content = ''.join(cart)
        response = HttpResponse(file_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="cart.txt"'
        return response


def redirect_from_short_link(request, short_link):
    """Переадресация с короткой ссылки на страницу рецепта."""
    recipe = get_object_or_404(Recipe, short_link=short_link)
    return redirect(f'/recipes/{recipe.id}/')
