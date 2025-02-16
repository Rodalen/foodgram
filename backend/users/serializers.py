import re

from django.contrib.auth import get_user_model
from rest_framework import serializers

from foodgram.constants import EMAIL_MAX_LENGTH, USER_MAX_LENGTH, PATTERN
from foodgram.helpers_serializers import Base64ImageField
from .models import Follow
from recipes.models import Recipe


User = get_user_model()


class AbstractUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        abstract = True

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        return Follow.objects.filter(user=request.user, following=obj).exists()


class UserSerializer(AbstractUserSerializer):
    
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'avatar',
        )


class UserRegistrationSerializer(AbstractUserSerializer):
    email = serializers.EmailField(required=True, max_length=EMAIL_MAX_LENGTH)
    username = serializers.CharField(required=True, max_length=USER_MAX_LENGTH)
    first_name = serializers.CharField(required=True, max_length=USER_MAX_LENGTH)
    last_name = serializers.CharField(required=True, max_length=USER_MAX_LENGTH)
    password = serializers.CharField(required=True, max_length=USER_MAX_LENGTH)

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 'password',
        )

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user

    def validate(self, attrs):
        errors = {}
        email = attrs.get('email')
        username = attrs.get('username')
        if not re.match(PATTERN, username) or User.objects.filter(username=username):
            errors['username'] = 'Неверное имя пользователя.'
        if User.objects.filter(email=email):
            errors['email'] = 'Неверная почта.'
        if errors:
            raise serializers.ValidationError(errors)
        return attrs



class UserRegisteredSerializer(AbstractUserSerializer):
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
        )


class FollowRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = Base64ImageField(source='following.avatar')

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=obj.user, following=obj.following).exists()
    
    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.following)

        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]

        return FollowRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.following).count()