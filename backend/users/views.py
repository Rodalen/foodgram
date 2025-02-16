from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Follow
from .serializers import (FollowSerializer, UserRegisteredSerializer,
                          UserRegistrationSerializer, UserSerializer)


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data.get('password'))
            response_serializer = UserRegisteredSerializer(user)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['POST'], url_path='set_password', permission_classes=[permissions.IsAuthenticated])
    def password(self, request, *args, **kwargs):
        user = request.user
        new_password = request.data.get('new_password')
        current_password = request.data.get('current_password')
        if not user.check_password(current_password):
            return Response({'error': 'Неверный пароль.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Пароль изменен.'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET',], url_path='me', permission_classes=[permissions.IsAuthenticated])
    def me(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['PUT', 'DELETE',], url_path='me/avatar', permission_classes=[permissions.IsAuthenticated])
    def avatar(self, request, *args, **kwargs):
        user = request.user
        avatar = request.data.get('avatar')
        if request.method == 'PUT':
            if not avatar:
                return Response({'error': 'Поле avatar обязательно.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = UserSerializer(
                user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response({'avatar': str(user.avatar)}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.avatar = None
            user.save()
            serializer = UserSerializer(user, context={'request': request})
            return Response(status=status.HTTP_204_NO_CONTENT)
        
    @action(detail=False, methods=['GET'], url_path='subscriptions', permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request, *args, **kwargs):
        user = request.user
        following = user.following.all()
        paginated_queryset = self.paginate_queryset(following)
        serializer = FollowSerializer(paginated_queryset, many=True, context={'request': request})
        paginated_serializer = self.get_paginated_response(serializer.data)
        return Response(paginated_serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST', 'DELETE'], url_path='(?P<user_id>\d+)/subscribe', permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, user_id):
        user = request.user
        following = get_object_or_404(User, id=user_id)

        if request.method == 'POST':
            if user == following:
                return Response(
                    {'error': 'Нельзя подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Follow.objects.filter(user=user, following=following).exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            follow = Follow.objects.create(user=user, following=following)
            serializer = FollowSerializer(
                follow,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if Follow.objects.filter(user=user, following=following).exists():
                follow = get_object_or_404(Follow, user=user, following=following)
                follow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'error': 'Вы не подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

class GetToken(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny,]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email и пароль обязательны.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(email=email, password=password)
        if user is None:
            return Response({'error': 'Неверные учетные данные.'}, status=status.HTTP_400_BAD_REQUEST)

        token, created = Token.objects.get_or_create(user=user)
        return Response({'auth_token': token.key}, status=status.HTTP_200_OK)
    

class DeleteToken(generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request, *args, **kwargs):
        token = get_object_or_404(Token.objects.filter(user=request.user))
        try:
            token.delete()
            return Response({'detail': 'Токен удален.'}, status=status.HTTP_204_NO_CONTENT)
        except Token.DoesNotExist:
            return Response({'detail': 'Токен не найден.'},status=status.HTTP_400_BAD_REQUEST)
