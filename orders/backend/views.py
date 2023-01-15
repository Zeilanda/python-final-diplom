from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Q, Sum, F
from django.http import JsonResponse
from requests import get
from rest_auth.registration.views import RegisterView
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from yaml import load as load_yaml, Loader

from backend.models import Category, Shop, Customer, User, Provider, Parameter, ProductParameter, Product, \
    ConfirmEmailToken, Order, OrderPosition
from backend.serializers import (CustomerCustomRegistrationSerializer, ProviderCustomRegistrationSerializer,
                                 LoginSerializer, CustomerSerializer, CategorySerializer, ShopSerializer,
                                 ProviderSerializer, ProductSerializer, OrderSerializer)
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
    Класс для просмотра списка товаров выбранного магазина и/или категории
    """
    def get(self, request, *args, **kwargs):

        query = Q(shop__state=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(category_id=category_id)

        queryset = Product.objects.filter(query).prefetch_related('parameters').distinct()

        serializer = ProductSerializer(queryset, many=True)

        return Response(serializer.data)


class ProductInfoView(APIView):
    """
    Класс для просмотра карточки товара
    """
    def get(self, request, id):

        queryset = Product.objects.filter(id=id)

        serializer = ProductSerializer(queryset, many=True)

        return Response(serializer.data)


class BasketView(APIView):
    """
    Класс для работы с корзиной пользователя
    """

    # получить корзину
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        basket = Order.objects.filter(
            user_id=request.user.id, status='basket').prefetch_related(
            'positions__product__category',
            'positions__product__parameters').annotate(
            total_cost=Sum(F('positions__amount') * F('positions__product__price'))).distinct()

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)


class BasketPosition(APIView):
    """
    Concrete view for creating a model instance.
    """
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
    # добавить товары в корзину
    # def post(self, request, *args, **kwargs):
    #     if not request.user.is_authenticated:
    #         return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        # items_string = request.data.get('items')
        # print(items_string)
        # if items_string:
        #     try:
        #         items_dict = load_json(items_string)
        #     except ValueError:
        #         JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
        #     else:
        #         basket, _ = Order.objects.get_or_create(customer_id=request.user.id, status='basket')
        #         objects_created = 0
        #         for order_item in items_dict:
        #             order_item.update({'order': basket.id})
        #             serializer = OrderPositionSerializer(data=order_item)
        #             if serializer.is_valid():
        #                 try:
        #                     serializer.save()
        #                 except IntegrityError as error:
        #                     return JsonResponse({'Status': False, 'Errors': str(error)})
        #                 else:
        #                     objects_created += 1
        #
        #             else:
        #
        #                 JsonResponse({'Status': False, 'Errors': serializer.errors})
        #
        #         return JsonResponse({'Status': True, 'Создано объектов': objects_created})
        # return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
    #
    # # удалить товары из корзины
    # def delete(self, request, *args, **kwargs):
    #     if not request.user.is_authenticated:
    #         return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
    #
    #     items_sting = request.data.get('items')
    #     if items_sting:
    #         items_list = items_sting.split(',')
    #         basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
    #         query = Q()
    #         objects_deleted = False
    #         for order_item_id in items_list:
    #             if order_item_id.isdigit():
    #                 query = query | Q(order_id=basket.id, id=order_item_id)
    #                 objects_deleted = True
    #
    #         if objects_deleted:
    #             deleted_count = OrderItem.objects.filter(query).delete()[0]
    #             return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})
    #     return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
    #
    # # добавить позиции в корзину
    # def put(self, request, *args, **kwargs):
    #     if not request.user.is_authenticated:
    #         return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
    #
    #     items_sting = request.data.get('items')
    #     if items_sting:
    #         try:
    #             items_dict = load_json(items_sting)
    #         except ValueError:
    #             JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
    #         else:
    #             basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
    #             objects_updated = 0
    #             for order_item in items_dict:
    #                 if type(order_item['id']) == int and type(order_item['quantity']) == int:
    #                     objects_updated += OrderItem.objects.filter(order_id=basket.id, id=order_item['id']).update(
    #                         quantity=order_item['quantity'])
    #
    #             return JsonResponse({'Status': True, 'Обновлено объектов': objects_updated})
    #     return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})