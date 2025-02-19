import django_filters

from django.db.models import Q
from rest_framework import filters

from recipes.models import Recipe, Tag, IsFavorited, IsInShoppingCart


class NameFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        name = request.query_params.get('name')
        if name:
            return queryset.filter(Q(name__istartswith=name)
                                   | Q(name__icontains=name))
        return queryset


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
            favorite_ids = IsFavorited.objects.filter(
                user=user
            ).values_list('recipe_id', flat=True)
            return queryset.filter(id__in=favorite_ids)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value == 1:
            cart_ids = IsInShoppingCart.objects.filter(
                user=user
            ).values_list('recipe_id', flat=True)
            return queryset.filter(id__in=cart_ids)
        return queryset
