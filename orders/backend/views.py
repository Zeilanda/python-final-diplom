from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Q, Count
from django.http import JsonResponse
from requests import get
from rest_auth.registration.views import RegisterView
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from yaml import load as load_yaml, Loader

from backend.models import Category, Shop, Customer, User, Provider, Parameter, ProductParameter, Product, \
    ConfirmEmailToken, Order, OrderPosition, ConfirmOrderToken
from backend.serializers import (LoginSerializer, CustomerSerializer, CategorySerializer, ShopSerializer,
                                 ProviderSerializer, ProductSerializer, OrderSerializer,
                                 CustomerRegistrationSerializer, ProviderRegistrationSerializer)
from backend.tasks import new_user_registered, new_order_created


# from backend.signals import new_user_registered, new_order


class CustomerRegistrationView(RegisterView):
    """
    Для регистрации покупателей
    """
    throttle_classes = [AnonRateThrottle]
    serializer_class = CustomerRegistrationSerializer
    #
    def get_response_data(self, user):

        new_user_registered.delay(user_id=user.id)
        return {"detail": "Verification e-mail sent."}


class ProviderRegistrationView(RegisterView):
    """
    Для регистрации поставщиков
    """
    throttle_classes = [AnonRateThrottle]
    serializer_class = ProviderRegistrationSerializer

    def get_response_data(self, user):
        new_user_registered.delay(user_id=user.id)
        return {"detail": "Verification e-mail sent."}


class ConfirmAccount(APIView):
    """
    Класс для подтверждения почтового адреса
    """
    # Регистрация методом POST
    throttle_classes = [AnonRateThrottle]

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
    Авторизация пользователя
    """
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
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
    Класс для работы данными покупателя
    """
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    # получить данные
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if not request.user.is_buyer:
            return JsonResponse({'Status': False, 'Error': 'Только для покупателей'}, status=403)

        serializer_self = CustomerSerializer(request.user)
        customer_id = serializer_self.data["id"]
        customer_data = Customer.objects.filter(user_id=customer_id).values('user_id', 'city',
                                                                            'street', 'house', 'phone')
        user_data = User.objects.filter(id=customer_id).values('email', 'first_name', "last_name")

        print(user_data)
        return Response({'customer_data': customer_data, "user_data": user_data}, status=status.HTTP_200_OK)



class AccountProviderDetails(APIView):
    """
    Класс для работы данными поставщика
    """
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

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
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

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
    Класс для просмотра категорий товаров
    """
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(ListAPIView):
    """
    Класс для просмотра списка магазинов
    """
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


class ProductsViewSet(ReadOnlyModelViewSet):
    """
    Класс для просмотра списка товаров выбранного магазина и/или категории
    """
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    serializer_class = ProductSerializer

    def get_queryset(self):
        query = Q(shop__state=True)
        shop_id = self.request.query_params.get('shop_id')
        category_id = self.request.query_params.get('category_id')

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(category_id=category_id)

        queryset = Product.objects.filter(query).prefetch_related('parameters').distinct()

        return queryset


class BasketView(APIView):
    """
    Класс для работы с корзиной пользователя
    """
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    # получить корзину
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        basket = Order.objects.filter(
            user_id=request.user.id, status='basket').prefetch_related(
            'positions__product__category',
            # 'positions__product__price',
            'positions__product__parameters').distinct()

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)


class BasketPosition(APIView):
    """
    Класс для добавления или изменения позиции в корзине
    """
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        product_id = request.data['product_id']
        amount = request.data.get('amount', 1)
        order = Order.objects.get_or_create(status='basket', user_id=request.user.id)

        OrderPosition.objects.create(product_id=product_id, amount=amount, order_id=order[0].id)

        return JsonResponse({'Status': True})

    def patch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        product_id = request.data['product_id']
        amount = request.data['amount']
        order = Order.objects.get(status='basket', user_id=request.user.id)

        order_position = OrderPosition.objects.get(product_id=product_id, order_id=order.id)
        order_position.delete()
        if amount > 0:
            OrderPosition.objects.create(product_id=product_id, amount=amount, order_id=order.id)
        return JsonResponse({'Status': True})


class OrderNew(APIView):
    """
    Класс для формирования нового заказа
    """
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        address = request.data['address']
        order = Order.objects.get(status='basket', user_id=request.user.id)
        order.status = "new"
        order.save()
        new_order_created.delay(order_id=order.id, address=address)
        # new_order.send(sender=self.__class__, order_id=order.id, address=address)

        return JsonResponse({'Status': True})


class ConfirmOrder(APIView):
    """
    Класс для подтверждения заказа
    """
    # Регистрация методом POST
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def get(self, request, *args, **kwargs):

        # проверяем обязательные аргументы
        token = request.GET.get('token', '')

        confirm_order_token = ConfirmOrderToken.objects.filter(key=token).first()
        if confirm_order_token:
            confirm_order_token.order.status = "confirmed"
            confirm_order_token.order.address = confirm_order_token.address
            confirm_order_token.order.save()
            confirm_order_token.delete()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': 'Неправильно указан токен'})


class OrderList(ListAPIView):
    """
    Класс для просмотра списка магазинов
    """
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    queryset = Order.objects.exclude(status="basket").prefetch_related(
        # 'positions__product__category',
        'positions__product')

    serializer_class = OrderSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(user_id=request.user.id)
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OrderProcessing(ListAPIView):
    """
    Класс для просмотра списка заказов для поставщиков
    """
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    queryset = Order.objects.exclude(status="basket").prefetch_related(
        # 'positions__product__category',
        'positions__product')

    serializer_class = OrderSerializer

    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if not request.user.is_provider:
            return JsonResponse({'Status': False, 'Error': 'Только для поставщиков'}, status=403)
        provider = Provider.objects.get(provider_id=request.user.id)
        shop_id = provider.shop_id
        queryset = (Order.objects.distinct()
                    .filter(positions__product__shop_id=shop_id)
                    .annotate(positions__amount=Count('positions'))
                    .filter(positions__amount__gt=0))

        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
