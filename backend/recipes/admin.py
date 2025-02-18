from django.contrib import admin

from recipes.models import Ingredient, Recipe, RecipeIngredients, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'created_at', 'is_favorited_count')
    search_fields = ('name', 'author__username', 'author__first_name')
    list_filter = ('tags',)

    def is_favorited_count(self, obj):
        return obj.is_favorited.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)


@admin.register(RecipeIngredients)
class RecipeIngredientAdmin(admin.ModelAdmin):
    pass
