from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer

from backend.models import Customer, Provider, Shop, Category, Product, ProductParameter, OrderPosition, \
    Order, User


class ShopSerializer(serializers.ModelSerializer):
    """
    Сериализатор для магазина
    """

    class Meta:
        model = Shop
        fields = ['id', 'name']


class CustomerSerializer(serializers.ModelSerializer):
    """
    Сериализатор для покупателя
    """

    class Meta:
        model = Customer
        fields = ['id', 'city', 'street', 'house', 'phone']


class ProviderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для поставщика
    """

    class Meta:
        model = Provider
        fields = ['id', 'shop', 'position']


class CustomerRegistrationSerializer(RegisterSerializer):
    """
    Сериализатор подтверждения регистрации покупателя
    """
    customer = serializers.PrimaryKeyRelatedField(read_only=True, )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    username = None
    city = serializers.CharField(required=True)
    street = serializers.CharField(required=True)
    house = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)

    def get_cleaned_data(self):
        data = super(CustomerRegistrationSerializer, self).get_cleaned_data()
        extra_data = {
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "city": self.validated_data.get("city", ""),
            "street": self.validated_data.get("street", ""),
            "house": self.validated_data.get("house", ""),
            "phone": self.validated_data.get("phone", "")
        }
        data.update(extra_data)
        return data

    def save(self, request):
        user = User.objects.create_user(email=self.validated_data.get('email'),
                                        username=self.validated_data.get('email'),
                                        password=self.validated_data.get('password1'),
                                        first_name=self.validated_data.get("first_name"),
                                        last_name=self.validated_data.get("last_name"),
                                        is_buyer=True)

        customer = Customer(user=user, city=self.validated_data.get("city"),
                            street=self.validated_data.get("street"),
                            house=self.validated_data.get("house"),
                            phone=self.validated_data.get("phone")
                            )
        customer.save()

        return user


class ProviderRegistrationSerializer(RegisterSerializer):
    """
    Сериализатор для подтверждения регистрации поставщика
    """
    provider = serializers.PrimaryKeyRelatedField(read_only=True, )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    username = None
    shop = serializers.CharField(required=True)
    position = serializers.CharField(required=True)

    def get_cleaned_data(self):
        data = super(ProviderRegistrationSerializer, self).get_cleaned_data()
        extra_data = {
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "shop": self.validated_data.get("shop", ""),
            "position": self.validated_data.get("position", ""),
        }
        data.update(extra_data)
        return data

    def save(self, request):
        # user = super(ProviderRegistrationSerializer, self).save(request)
        user = User.objects.create_user(email=self.validated_data.get('email'),
                                        username=self.validated_data.get('email'),
                                        password=self.validated_data.get('password1'),
                                        first_name=self.validated_data.get("first_name"),
                                        last_name=self.validated_data.get("last_name"),
                                        is_provider=True)

        shop = Shop.objects.get_or_create(name=self.validated_data.get("shop"))
        print(shop)
        provider = Provider(provider=user, shop=shop[0],
                            position=self.validated_data.get("position"),
                            )
        provider.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    Authenticates an existing user.
    Email and password are required.
    Returns a JSON web token.
    """
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)

    # Ignore these fields if they are included in the request.
    username = serializers.CharField(max_length=255, read_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        """
        Validates user data.
        """
        email = data.get('email', None)
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        return {
            'token': user.token,
        }


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для категорий товаров
    """

    class Meta:
        model = Category
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class ProductParameterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для параметров товара
    """
    parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ('parameter', 'value',)


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для товара
    """
    category = serializers.StringRelatedField()
    parameters = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        model = Product
        fields = ('name', 'model', 'price', 'price_rrc', 'quantity', 'category', 'shop', 'parameters')
        read_only_fields = ('id',)


class OrderPositionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для позиций в заказе
    """
    product = serializers.StringRelatedField()

    class Meta:
        model = OrderPosition
        fields = ("id", "order", "product", 'product_id', "amount",)
        read_only_fields = ('id',)
        extra_kwargs = {
            'order': {'write_only': True}
        }


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для заказа
    """
    positions = OrderPositionSerializer(read_only=True, many=True)

    class Meta:
        model = Order
        fields = ('id', 'positions', 'status', 'order_datetime', "address")
        read_only_fields = ('id',)
        extra_kwargs = {
            'order': {'write_only': True}
        }
