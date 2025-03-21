from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('secure_admin/', admin.site.urls),
    path('oauth/', include('oauth_handler.urls')),
    path('customers/', include('customers.urls')),  # Include the customers app URLs
    path('', include(('ecommerce.urls', 'ecommerce'), namespace='ecommerce')),
    path('self-order/', include(('self_order.urls', 'self_order'), namespace='self_order')),  # Add Self-Order App

]
