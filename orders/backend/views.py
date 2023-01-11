import json

from django.contrib.auth.password_validation import validate_password
from django.core import serializers
from django.http import JsonResponse
from rest_auth.registration.views import RegisterView
from rest_framework import status, viewsets
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.models import Category, Shop, Customer, User
from backend.serializers import (CustomerCustomRegistrationSerializer, ProviderCustomRegistrationSerializer,
                                 LoginSerializer, CustomerSerializer, CategorySerializer, ShopSerializer)


class CustomerRegistrationView(RegisterView):
    """
    Для регистрации покупателей
    """
    serializer_class = CustomerCustomRegistrationSerializer


class ProviderRegistrationView(RegisterView):
    """
    Для регистрации поставщиков
    """
    serializer_class = ProviderCustomRegistrationSerializer


class LoginAPIView(APIView):
    """
    Logs in an existing user.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        """
        Checks is user exists.
        Email and password are required.
        Returns a JSON web token.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class AccountCustomerDetails(APIView):
    """
    Класс для работы данными пользователя
    """

    # получить данные
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        serializer_self = CustomerSerializer(request.user)
        customer_id = serializer_self.data["id"]
        customer_data = Customer.objects.filter(customer_id=customer_id).values('customer_id', 'city',
                                                                                'street', 'house', 'phone')
        user_data = User.objects.filter(id=customer_id).values('email', 'first_name', "last_name")

        print(user_data)
        return Response({'customer_data': customer_data, "user_data": user_data}, status=status.HTTP_200_OK)

    # Редактирование методом POST
    # def post(self, request, *args, **kwargs):
    #     if not request.user.is_authenticated:
    #         return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
    #     # проверяем обязательные аргументы
    #
    #     if 'password' in request.data:
    #         errors = {}
    #         # проверяем пароль на сложность
    #         try:
    #             validate_password(request.data['password'])
    #         except Exception as password_error:
    #             error_array = []
    #             # noinspection PyTypeChecker
    #             for item in password_error:
    #                 error_array.append(item)
    #             return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
    #         else:
    #             request.user.set_password(request.data['password'])

        # проверяем остальные данные
        # user_serializer = CustomerSerializer(request.user, data=request.data, partial=True)
        # if user_serializer.is_valid():
        #     user_serializer.save()
        #     return JsonResponse({'Status': True})
        # else:
        #     return JsonResponse({'Status': False, 'Errors': user_serializer.errors})


class CategoryView(ListAPIView):
    """
    Класс для просмотра категорий
    """
    permission_classes = [AllowAny]

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(ListAPIView):
    """
    Класс для просмотра списка магазинов
    """
    permission_classes = [AllowAny]

    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer
