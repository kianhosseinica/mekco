from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('start/', start_refresh_and_redirect, name='start_refresh_and_redirect'),
    path('exchange-token/', exchange_token, name='exchange_token'),
    path('refresh-token/', refresh_token, name='refresh_token'),
    path('account-infox/', get_account_info, name='account_info'),
    path('get-item-details/', get_item_details, name='get_item_details'),
    path('update-item-quantity/', update_item_quantity, name='update_item_quantity'),
    path('add-quantity-to-item/', add_quantity_to_item, name='add_quantity_to_item'),
    path('update-multiple-items/', update_multiple_items_preview, name='update_multiple_items'),
    path('update-multiple-items-preview/', update_multiple_items_preview, name='update_multiple_items_preview'),
    path('confirm-update-items/', confirm_update_items, name='confirm_update_items'),
    path('credit-account-details/', get_credit_account_details, name='credit_account_details'),
    path('customer-details/<int:customer_id>/', get_customer_details, name='customer_details'),
    path('fetch-items/', fetch_all_items, name='fetch_items'),
    path('fetch-all-vendors/', fetch_all_vendors_view, name='fetch_all_vendors'),
    path('items/', list_items, name='list_items'),
    path('items/<int:item_id>/', item_detail, name='item_detail'),
    path('categories/', fetch_all_categories, name='fetch-categories'),
    path('items/reorder/', list_reorder_items, name='list-reorder-items'),
    path('quotes/', list_quotes, name='list_quotes'),
    path('quotes/add/', add_quote, name='add_quote'),
    path('quotes/<int:quote_id>/edit/', edit_quote, name='edit_quote'),
    path('quotes/<int:quote_id>/add-item/', add_quote_item, name='add_quote_item'),
    path('test-specific-item-image/', fetch_specific_item_image, name='test-specific-item-image'),
    # path('categories/', show_categories, name='show_categories'),  # The name here is important
    path('customers/details/', display_customer_details, name='customer_details'),
    path('update-customers/', update_customers, name='update_customers'),
    path('archive-customers/', archive_customers, name='archive_customers'),
    path('load-subcategories/<int:category_id>/', load_subcategories, name='load_subcategories'),
    path('send-email/', send_email, name='send_email'),

        path('send-message/', send_message_page, name='send_message_page'),
    path('search/', search_items, name='search_items'),
    path('update-quantity/', update_quantity, name='update_quantity'),

]
