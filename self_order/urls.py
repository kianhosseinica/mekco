from django.urls import path
from .views import *

app_name = 'self_order'

urlpatterns = [
    path('', self_order_home, name='self_order_home'),
    path('search-customer/', search_customer, name='search_customer'),
    path('menu/<int:customer_id>/', self_order_menu, name='self_order_menu'),
    path('add-to-cart/', add_to_self_order_cart, name='add_to_self_order_cart'),
    path('cart/', self_order_cart_view, name='self_order_cart'),
    path('checkout/', self_order_checkout, name='self_order_checkout'),
]
