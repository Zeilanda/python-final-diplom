import json

from django.contrib.auth.password_validation import validate_password
from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Q
from django.http import JsonResponse
from requests import get
from rest_auth.registration.views import RegisterView
from rest_framework import status, viewsets
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from yaml import load as load_yaml, Loader

from backend.models import Category, Shop, Customer, User, Provider, Parameter, ProductParameter, Product, \
    ConfirmEmailToken
from backend.serializers import (CustomerCustomRegistrationSerializer, ProviderCustomRegistrationSerializer,
                                 LoginSerializer, CustomerSerializer, CategorySerializer, ShopSerializer,
                                 ProviderSerializer, ProductSerializer)
from backend.signals import new_user_registered


class CustomerRegistrationView(RegisterView):
    """
    Для регистрации покупателей
    """
    serializer_class = CustomerCustomRegistrationSerializer

    def get_response_data(self, user):
        new_user_registered.send(sender=self.__class__, user_id=user.id)

        return {"detail": "Verification e-mail sent."}


class ProviderRegistrationView(RegisterView):
    """
    Для регистрации поставщиков
    """
    serializer_class = ProviderCustomRegistrationSerializer

    def get_response_data(self, user):
        new_user_registered.send(sender=self.__class__, user_id=user.id)

        return {"detail": "Verification e-mail sent."}


class ConfirmAccount(APIView):
    """
    Класс для подтверждения почтового адреса
    """
    # Регистрация методом POST
    def post(self, request, *args, **kwargs):

        # проверяем обязательные аргументы
        token = request.GET.get('token', '')

        token = ConfirmEmailToken.objects.filter(key=token).first()
        if token:
            token.user.is_active = True
            token.user.save()
            token.delete()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': 'Неправильно указан токен или email'})


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

        if not request.user.is_buyer:
            return JsonResponse({'Status': False, 'Error': 'Только для покупателей'}, status=403)

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


class AccountProviderDetails(APIView):
    """
    Класс для работы данными пользователя
    """

    # получить данные
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if not request.user.is_provider:
            return JsonResponse({'Status': False, 'Error': 'Только для поставщиков'}, status=403)

        serializer_self = ProviderSerializer(request.user)
        provider_id = serializer_self.data["id"]
        shop_id = Provider.objects.filter(provider_id=provider_id)[0].shop_id
        shop_name = Shop.objects.filter(id=shop_id).values("name")
        provider_data = Provider.objects.filter(provider_id=provider_id).values('provider_id',
                                                                                'position')
        # print(provider_data)
        user_data = User.objects.filter(id=provider_id).values('email', 'first_name', "last_name")

        return Response({'provider_data': provider_data, "shop": shop_name, "user_data": user_data},
                        status=status.HTTP_200_OK)


class ProviderPriceUpdate(APIView):
    """
    Класс для обновления прайса от поставщика
    """

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if not request.user.is_provider:
            return JsonResponse({'Status': False, 'Error': 'Только для поставщиков'}, status=403)

        url = request.data.get('url')
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return JsonResponse({'Status': False, 'Error': str(e)})
            else:
                stream = get(url).content

                data = load_yaml(stream, Loader=Loader)

                shop = Shop.objects.get_or_create(name=data['shop'])

                for category in data['categories']:
                    category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
                for item in data['goods']:
                    product, _ = Product.objects.get_or_create(external_id=item['id'],
                                                               name=item['name'],
                                                               category_id=item['category'],
                                                               model=item['model'],
                                                               price=item['price'],
                                                               price_rrc=item['price_rrc'],
                                                               quantity=item['quantity'],
                                                               shop_id=shop[0].id
                                                               )
                    #
                    for name, value in item['parameters'].items():
                        parameter_object, _ = Parameter.objects.get_or_create(name=name)
                        ProductParameter.objects.create(product_id=product.id,
                                                        parameter_id=parameter_object.id,
                                                        value=value)

                return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class CategoryView(ListAPIView):
    """
    Класс для просмотра категорий
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(ListAPIView):
    """
    Класс для просмотра списка магазинов
    """
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


class ProductsView(APIView):
    """
    Класс для поиска товаров
    """
    def get(self, request, *args, **kwargs):

        query = Q(shop__state=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(category_id=category_id)

        # фильтруем и отбрасываем дубликаты
        # queryset = Product.objects.filter(
        #     query).select_related(
        #     'shop', 'category').prefetch_related(
        #     'product_parameters__parameter').distinct()
        queryset = Product.objects.filter(query).prefetch_related('parameters')

        serializer = ProductSerializer(queryset, many=True)

        return Response(serializer.data)
