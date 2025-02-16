from django.urls import include, path
from rest_framework.routers import SimpleRouter

from users.views import UserViewSet, GetToken, DeleteToken
from recipes.views import TagViewSet, IngredientViewSet, RecipeViewSet

v1_router = SimpleRouter()
v1_router.register('users', UserViewSet, basename='users')
v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')
v1_router.register('recipes', RecipeViewSet, basename='recipes')

url_v1 = [
    path('auth/token/login/', GetToken.as_view(), name='get_token'),
    path('auth/token/logout/', DeleteToken.as_view(), name='delete_token'),
    path('', include(v1_router.urls))
]

urlpatterns = [
    path('', include(url_v1)),
]
