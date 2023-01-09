from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer


from backend.models import Customer, Provider, Shop


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name']


class CustomerCustomRegistrationSerializer(RegisterSerializer):
    customer = serializers.PrimaryKeyRelatedField(read_only=True, )
    city = serializers.CharField(required=True)
    street = serializers.CharField(required=True)
    house = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)

    def get_cleaned_data(self):
        data = super(CustomerCustomRegistrationSerializer, self).get_cleaned_data()
        extra_data = {
            "city": self.validated_data.get("city", ""),
            "street": self.validated_data.get("street", ""),
            "house": self.validated_data.get("house", ""),
            "phone": self.validated_data.get("phone", "")
        }
        data.update(extra_data)
        return data

    def save(self, request):
        user = super(CustomerCustomRegistrationSerializer, self).save(request)
        user.is_buyer = True
        user.save()
        customer = Customer(customer=user, city=self.cleaned_data.get("city"),
                            street=self.cleaned_data.get("street"),
                            house=self.cleaned_data.get("house"),
                            phone=self.cleaned_data.get("phone")
                            )
        customer.save()
        return user


class ProviderCustomRegistrationSerializer(RegisterSerializer):
    provider = serializers.PrimaryKeyRelatedField(read_only=True, )
    company = serializers.CharField(required=True)
    shop = serializers.CharField(required=True)
    position = serializers.CharField(required=True)

    def get_cleaned_data(self):
        data = super(ProviderCustomRegistrationSerializer, self).get_cleaned_data()
        extra_data = {
            "company": self.validated_data.get("company", ""),
            "shop": self.validated_data.get("shop", ""),
            "position": self.validated_data.get("position", ""),
        }
        data.update(extra_data)
        return data

    def save(self, request):
        user = super(ProviderCustomRegistrationSerializer, self).save(request)
        user.is_provider = True
        user.save()
        shop = Shop.objects.get_or_create(name=self.cleaned_data.get("shop"))
        print(shop)
        provider = Provider(provider=user, company=self.cleaned_data.get("company"),
                            shop=shop[0],
                            position=self.cleaned_data.get("position"),
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


