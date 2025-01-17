from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from backend.views import CustomerRegistrationView, \
    CategoryView, ShopView, AccountCustomerDetails, AccountProviderDetails, ProviderPriceUpdate, ConfirmAccount, \
    ProductsViewSet, BasketView, BasketPosition, OrderNew, ConfirmOrder, OrderList, OrderProcessing, \
    ProviderRegistrationView

router = DefaultRouter()
router.register('products', ProductsViewSet, basename='product')

app_name = "backend"
urlpatterns = [
    path('registration/customer', CustomerRegistrationView.as_view(), name='register-customer'),
    path('registration/provider', ProviderRegistrationView.as_view(), name='register-provider'),
    path('user/register/confirm', ConfirmAccount.as_view(), name='user-register-confirm'),
    path('login/', TokenObtainPairView.as_view(), name='user_login'),
    path('login/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('customer/details', AccountCustomerDetails.as_view(), name='user-details'),
    path('provider/details', AccountProviderDetails.as_view(), name='provider-details'),
    path('price/update', ProviderPriceUpdate.as_view(), name='price-update'),
    path('categories', CategoryView.as_view(), name='categories'),
    path('shops', ShopView.as_view(), name='shops'),
    path('basket', BasketView.as_view(), name='basket'),
    path('basket/position', BasketPosition.as_view(), name='basket-position'),
    path('order/new', OrderNew.as_view(), name='order-new'),
    path('order/confirm', ConfirmOrder.as_view(), name='order-confirm'),
    path('orders', OrderList.as_view(), name='order-list'),
    path('orders/processing', OrderProcessing.as_view(), name='order-processing'),
    path('', include(router.urls)),


]
