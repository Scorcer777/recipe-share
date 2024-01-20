from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import CustomUser, Subscriptions
from recipes.serializers import (RegistrationSerializer,
                                 ProfileSerializer,
                                 SubscriptionsSerializer)
from recipes.pagination import CustomPagination


class ProfileViewSet(viewsets.ModelViewSet):
    '''Вьюсет для работы с данными пользователей.'''
    queryset = CustomUser.objects.all()
    http_method_names = ['get', 'post', 'delete']
    serializer_class = ProfileSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    def create(self, request):
        data = {
            'email': request.data['email'],
            'username': request.data['username'],
            'password': request.data['password'],
            'first_name': request.data['first_name'],
            'last_name': request.data['last_name'],
            }
        serializer = RegistrationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        '''Вернуть подписки текущего пользователя.'''
        queryset = CustomUser.objects.filter(subscribers__user=request.user)
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = SubscriptionsSerializer(
            paginated_queryset, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, pk):
        '''Подписаться / отписаться от пользователя.'''
        if request.method == 'POST':
            new_subscription = get_object_or_404(CustomUser, pk=pk)
            serializer = SubscriptionsSerializer(
                new_subscription, context={'request': request})
            serializer.validate(serializer.data)
            if not request.user.is_authenticated:
                return Response({'message': 'Вы не авторизованы!'},
                                status=status.HTTP_401_UNAUTHORIZED)
            if request.user == new_subscription:
                return Response({'message': 'Нельзя подписаться на себя!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if Subscriptions.objects.filter(
                    user=request.user, subscription=new_subscription).exists():
                return Response({
                    'message': 'Вы уже подписаны на данного пользователя!'},
                    status=status.HTTP_400_BAD_REQUEST)
            else:
                Subscriptions.objects.create(user=request.user,
                                             subscription=new_subscription)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            old_subscription = get_object_or_404(CustomUser, pk=pk)
            if not request.user.is_authenticated:
                return Response({'message': 'Вы не авторизованы!'},
                                status=status.HTTP_401_UNAUTHORIZED)
            if not Subscriptions.objects.filter(
                        user=request.user,
                        subscription=old_subscription).exists():
                return Response({
                    'message': 'Вы не были подписаны на данного автора.'},
                    status=status.HTTP_400_BAD_REQUEST)
            request.user.subscribed_to.filter(
                subscription=old_subscription
            ).delete()
            return Response({'message': 'Вы отписались от данного автора!'},
                            status=status.HTTP_204_NO_CONTENT)
