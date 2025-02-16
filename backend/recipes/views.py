import uuid

from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, generics, permissions, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Tag, Ingredient, Recipe, RecipeIngredients
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer, RecipeCreateSerializer, RecipeFavoriteShoppingCartSerializer
from api.permissions import FoodgramPermission


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    """Вьюсет для тэгов."""
    permission_classes = [permissions.AllowAny]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    """Вьюсет для ингредиентов."""
    permission_classes = [permissions.AllowAny]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            name.lower()
            queryset = queryset.filter(models.Q(name__istartswith=name) | models.Q(name__icontains=name))
        return queryset
    

class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    permission_classes = [FoodgramPermission]
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author',)

    def get_queryset(self):
        """Фильтрация по тэгам, избранному, корзине."""
        queryset = super().get_queryset()
        
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited and self.request.user.is_authenticated:
            if is_favorited.lower() in ['true', '1']:
                queryset = queryset.filter(is_favorited=self.request.user)

        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        if is_in_shopping_cart and self.request.user.is_authenticated:
            if is_in_shopping_cart.lower() in ['true', '1']:
                queryset = queryset.filter(is_in_shopping_cart=self.request.user)

        return queryset

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
        if instance:
            recipe = serializer.save()
        else:
            recipe = serializer.save(author=self.request.user)
        output_serializer = RecipeSerializer(recipe, context=self.get_serializer_context())
        return Response(output_serializer.data, status=status.HTTP_200_OK if instance else status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        return self.create_or_update(request)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.create_or_update(request, instance=instance)
    
    @action(detail=False, methods=['GET'], url_path='(?P<recipe_id>\d+)/get-link')
    def get_short_link(self, request, recipe_id):
        """Получение (создание) короткой ссылки на рецепт."""
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if not recipe.short_link:
            link = uuid.uuid4().hex[:3]
            recipe.short_link = link
            recipe.save()
        url = f"{request.get_host()}/s/{recipe.short_link}"
        return Response({'short-link': url}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST', 'DELETE'], url_path='(?P<recipe_id>\d+)/favorite')
    def add_favorite(self, request, recipe_id):
        """Добавление в избранное."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if recipe.is_favorited.filter(pk=user.id).exists():
            if request.method == 'DELETE':
                recipe.is_favorited.remove(user)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            if request.method == 'POST':
                recipe.is_favorited.add(user)
                serializer = RecipeFavoriteShoppingCartSerializer(recipe)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST', 'DELETE'], url_path='(?P<recipe_id>\d+)/shopping_cart')
    def add_to_shopping_cart(self, request, recipe_id):
        """Добавление в корзину."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if recipe.is_in_shopping_cart.filter(pk=user.id).exists():
            if request.method == 'DELETE':
                recipe.is_in_shopping_cart.remove(user)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            if request.method == 'POST':
                recipe.is_in_shopping_cart.add(user)
                serializer = RecipeFavoriteShoppingCartSerializer(recipe)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        
    @action(detail=False, methods=['GET'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        """Скачивание корзины."""
        user = request.user
        recipes = user.shopping_cart_recipes.all()
        ingredients = (
            RecipeIngredients.objects
            .filter(recipe__in=recipes)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=models.Sum('amount'))
            .order_by('ingredient__name')
        )
        file_content = 'Список покупок:\n\n'
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['total_amount']
            file_content += f'- {name} - {amount} {unit}\n'
        response = HttpResponse(file_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response
    

def redirect_from_short_link(request, short_link):
    """Переадресация с короткой ссылки на страницу рецепта."""
    recipe = get_object_or_404(Recipe, short_link=short_link)
    return redirect(f'/recipes/{recipe.id}/')