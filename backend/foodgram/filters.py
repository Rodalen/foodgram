import django_filters

from django.db.models import Q
from rest_framework import filters

from recipes.models import Recipe, Tag


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
            return queryset.filter(is_favorited=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value == 1:
            return queryset.filter(is_in_shopping_cart=user)
        return queryset
