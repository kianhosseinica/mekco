from django.urls import path
from .views import *
app_name = 'customers'
urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('admin/assign-customer-type/', admin_assign_customer_type_view, name='admin_assign_customer_type'),
    path('activate/<uidb64>/<token>/', activate_view, name='activate'),
    path('password-reset/', password_reset_request_view, name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', password_reset_confirm_view, name='password_reset_confirm'),
    path('order_history/', order_history_view, name='order_history'),
    path('order/<int:order_id>/', order_detail_view, name='order_detail'),
    path('order-item/<int:order_item_id>/request-return/', request_return_view, name='request_return'),

]
