from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'email')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    pass
