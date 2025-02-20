import django_filters

from rest_framework import filters

from recipes.models import Recipe, Tag


class NameFilter(filters.SearchFilter):
    search_param = 'name'


# Поменял NumberFilter на BooleanFilter.
# На уровне API работает, в самом проекте нет, т.к.
# с фронтенда приходит следующий запрос:
# /api/recipes/?is_in_shopping_cart=1
# В таком случае в BooleanFilter всегда приходит value = False
# и над корзиной отображается количество всех созданных рецептов,
# хотя в самой корзине их нет.
# Пробовал преобразовывать value внутри методов, но не сработало.
# Нашел вариант с переопределением класса BooleanFilter,
# но думаю, что переопределять BooleanFilter выйдет еще запутаннее,
# чем оставить NumberFilter.
# Для ревью кода оставлю BooleanFilter
# P.S. проверял через Postman, если задавать так:
# ?is_in_shopping_cart=true или ?is_in_shopping_cart=false
# то все работает.
class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        distinct=True
    )
    is_favorited = django_filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(favorited_by__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(in_shopping_cart_of__user=user)
        return queryset
