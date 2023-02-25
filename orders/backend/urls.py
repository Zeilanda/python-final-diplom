from django.urls import path

from backend.views import CustomerRegistrationView, ProviderRegistrationView, LoginAPIView, \
    CategoryView, ShopView, AccountCustomerDetails, AccountProviderDetails, ProviderPriceUpdate, ConfirmAccount, \
    ProductsViewSet, ProductInfoView, BasketView, BasketPosition, OrderNew, ConfirmOrder, OrderList, OrderProcessing

product_list = ProductsViewSet.as_view({
    'get': 'list'
})

product_detail = ProductsViewSet.as_view({
    'get': 'retrieve'
})

app_name = "backend"
urlpatterns = [
    path('registration/customer', CustomerRegistrationView.as_view(), name='register-customer'),
    path('registration/provider', ProviderRegistrationView.as_view(), name='register-provider'),
    path('user/register/confirm', ConfirmAccount.as_view(), name='user-register-confirm'),
    path('login/', LoginAPIView.as_view(), name='user_login'),
    path('customer/details', AccountCustomerDetails.as_view(), name='user-details'),
    path('provider/details', AccountProviderDetails.as_view(), name='provider-details'),
    path('price/update', ProviderPriceUpdate.as_view(), name='price-update'),
    path('categories', CategoryView.as_view(), name='categories'),
    path('shops', ShopView.as_view(), name='shops'),
    path('products', product_list, name='products'),
    path('products/<int:pk>', product_detail, name='product-info'),
    path('basket', BasketView.as_view(), name='basket'),
    path('basket/position', BasketPosition.as_view(), name='basket-position'),
    path('order/new', OrderNew.as_view(), name='order-new'),
    path('order/confirm', ConfirmOrder.as_view(), name='order-confirm'),
    path('orders', OrderList.as_view(), name='order-list'),
    path('orders/processing', OrderProcessing.as_view(), name='order-processing'),


]
