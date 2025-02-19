import django_filters

from django.db.models import Q
from rest_framework import filters

from recipes.models import Recipe, Tag, Favorited, ShoppingCart


class NameFilter(filters.SearchFilter):
    search_param = 'name'


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        distinct=True
    )
    is_favorited = django_filters.NumberFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value == 1:
            favorite_ids = Favorited.objects.filter(
                user=user
            ).values_list('recipe_id', flat=True)
            return queryset.filter(id__in=favorite_ids)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value == 1:
            cart_ids = ShoppingCart.objects.filter(
                user=user
            ).values_list('recipe_id', flat=True)
            return queryset.filter(id__in=cart_ids)
        return queryset
