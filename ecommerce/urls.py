from django.urls import path
from . import views

app_name = 'ecommerce'

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart_items, name='update_cart_items'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('get_shipping_rate/', views.get_shipping_rate, name='get_shipping_rate'),
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('pricing_rules/', views.pricing_rule_list, name='pricing_rule_list'),
    path('pricing_rules/add/', views.add_pricing_rule, name='add_pricing_rule'),
    path('admin/load-parent-category/', views.load_parent_category, name='load_parent_category'),
    path('admin/load-subcategories/', views.load_subcategories, name='load_subcategories'),
    path('view-pricing-rule-items/<int:pk>/', views.view_pricing_rule_items, name='view_pricing_rule_items'),
    path('index/', views.index, name='index'),
    path('admin/orders/', views.custom_order_list_view, name='admin_order_list'),
    path('admin/orders/<int:order_id>/', views.custom_order_detail_view, name='admin_order_detail'),
    path('admin/orders/with-returns/', views.orders_with_returns_view, name='orders_with_returns'),
    path('admin/orders/<int:order_id>/returns/', views.return_requests_by_order_view, name='return_requests_by_order'),
    path('admin/orders/<int:order_id>/update-return-status/', views.update_return_request_status,
         name='update_return_request_status'),












    path('checkout/paypal/', views.paypal_payment, name='paypal_payment'),
    path('payment/execute/', views.execute_payment, name='execute_payment'),
    path('payment/cancel/', views.cancel_payment, name='cancel_payment'),
    path('payment/success/', views.success_view, name='success'),

    path('search/', views.item_search, name='item_search'),

]
