from django.urls import path

from backend.views import CustomerRegistrationView, ProviderRegistrationView, LoginAPIView

app_name = "backend"
urlpatterns = [
    #Registration Urls
    path('registration/customer/', CustomerRegistrationView.as_view(), name='register-customer'),
    path('registration/provider/', ProviderRegistrationView.as_view(), name='register-provider'),
    path('login/', LoginAPIView.as_view(), name='user_login')
]