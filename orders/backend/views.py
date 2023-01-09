from rest_auth.registration.views import RegisterView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.serializers import (CustomerCustomRegistrationSerializer, ProviderCustomRegistrationSerializer,
                                 LoginSerializer)


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
