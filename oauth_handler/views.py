import json
import logging
from datetime import datetime
from decimal import Decimal
from django.contrib.auth.decorators import user_passes_test, login_required

import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from django.db import IntegrityError
from .forms import PasswordForm
from .models import *
def is_admin(user):
    return user.is_active and user.is_staff



@user_passes_test(is_admin)
@login_required
def home(request):
    return render(request, 'oauth_handler/home.html')



@csrf_exempt
@user_passes_test(is_admin)
@login_required
def start_refresh_and_redirect(request):
    if request.method == 'POST':
        call_command('refresh_token')
        redirect_url = request.POST.get('redirect_url')
        return redirect(redirect_url)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
@user_passes_test(is_admin)
@login_required
def exchange_token(request):
    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        client_secret = request.POST.get('client_secret')
        code = request.POST.get('code')
        grant_type = request.POST.get('grant_type')

        url = "https://cloud.lightspeedapp.com/oauth/access_token.php"
        payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': grant_type
        }

        response = requests.post(url, data=payload)
        data = response.json()
        settings.ACCESS_TOKEN = data.get('access_token')
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def refresh_token():
    url = 'https://cloud.lightspeedapp.com/oauth/access_token.php'
    payload = {
        'client_id': settings.CLIENT_ID,
        'client_secret': settings.CLIENT_SECRET,
        'refresh_token': settings.REFRESH_TOKEN,
        'grant_type': 'refresh_token'
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        data = response.json()
        settings.ACCESS_TOKEN = data['access_token']
    else:
        raise Exception('Failed to refresh token')

def get_account_info(request):
    def fetch_account_info():
        url = "https://api.lightspeedapp.com/API/V3/Account.json"
        headers = {
            'Authorization': f'Bearer {settings.ACCESS_TOKEN}'
        }
        return requests.get(url, headers=headers)

    response = fetch_account_info()
    if response.status_code == 401:  # Unauthorized error
        call_command('refresh_token')
        response = fetch_account_info()

    if response.status_code == 200:
        return render(request, 'oauth_handler/account_info.html', {'account_info': response.json()})
    else:
        return JsonResponse({'error': 'Failed to fetch account information'}, status=response.status_code)

@csrf_exempt
@user_passes_test(is_admin)
@login_required
def get_item_details(request):
    if request.method == 'POST':
        manufacturer_sku = request.POST.get('manufacturer_sku')
        if settings.ACCESS_TOKEN is None:
            return JsonResponse({'error': 'Access token not available'}, status=400)

        url = f"https://api.lightspeedapp.com/API/V3/Account/{settings.LIGHTSPEED_ACCOUNT_ID}/Item.json"
        params = {
            'load_relations': '["ItemShops"]',
            'manufacturerSku': manufacturer_sku
        }
        headers = {
            'Authorization': f'Bearer {settings.ACCESS_TOKEN}'
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 401:  # Unauthorized error
            call_command('refresh_token')
            headers['Authorization'] = f'Bearer {settings.ACCESS_TOKEN}'
            response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse({'error': 'Failed to fetch item details'}, status=response.status_code)
    else:
        return render(request, 'oauth_handler/get_item_details.html')

@csrf_exempt
@user_passes_test(is_admin)
@login_required
def update_item_quantity(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item_shop_id = request.POST.get('item_shop_id')
        quantity = request.POST.get('quantity')

        if settings.ACCESS_TOKEN is None:
            return JsonResponse({'error': 'Access token not available'}, status=400)

        url = f"https://api.lightspeedapp.com/API/V3/Account/{settings.LIGHTSPEED_ACCOUNT_ID}/Item/{item_id}.json"
        payload = {
            "ItemShops": {
                "ItemShop": [
                    {
                        "itemShopID": item_shop_id,
                        "qoh": quantity
                    }
                ]
            }
        }
        headers = {
            'Authorization': f'Bearer {settings.ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }

        response = requests.put(url, headers=headers, json=payload)
        if response.status_code == 401:  # Unauthorized error
            call_command('refresh_token')
            headers['Authorization'] = f'Bearer {settings.ACCESS_TOKEN}'
            response = requests.put(url, headers=headers, json=payload)

        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse({'error': 'Failed to update item quantity', 'details': response.text}, status=response.status_code)
    else:
        return render(request, 'oauth_handler/update_item_quantity.html')

@csrf_exempt
@user_passes_test(is_admin)
@login_required
def add_quantity_to_item(request):
    if request.method == 'POST':
        manufacturer_sku = request.POST.get('manufacturer_sku')
        quantity_to_add = int(request.POST.get('quantity'))

        if settings.ACCESS_TOKEN is None:
            return JsonResponse({'error': 'Access token not available'}, status=400)

        # Get item details
        url = f"https://api.lightspeedapp.com/API/V3/Account/{settings.LIGHTSPEED_ACCOUNT_ID}/Item.json"
        params = {
            'load_relations': '["ItemShops"]',
            'manufacturerSku': manufacturer_sku
        }
        headers = {
            'Authorization': f'Bearer {settings.ACCESS_TOKEN}'
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 401:  # Unauthorized error
            call_command('refresh_token')
            headers['Authorization'] = f'Bearer {settings.ACCESS_TOKEN}'
            response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to fetch item details', 'details': response.text}, status=response.status_code)

        item_data = response.json()
        if '@attributes' in item_data and 'count' in item_data['@attributes'] and int(item_data['@attributes']['count']) == 0:
            return JsonResponse({'error': 'Item not found'}, status=404)

        item = item_data['Item']
        if not isinstance(item, list):
            item = [item]
        item = item[0]
        item_id = item['itemID']
        # Find the correct ItemShop
        item_shop = next((shop for shop in item['ItemShops']['ItemShop'] if shop['shopID'] != '0'), None)
        if not item_shop:
            return JsonResponse({'error': 'Valid ItemShop not found'}, status=400)

        item_shop_id = item_shop['itemShopID']
        current_qoh = int(item_shop['qoh'])

        # Calculate new quantity
        new_quantity = current_qoh + quantity_to_add

        # Update item quantity
        url = f"https://api.lightspeedapp.com/API/V3/Account/{settings.LIGHTSPEED_ACCOUNT_ID}/Item/{item_id}.json"
        payload = {
            "ItemShops": {
                "ItemShop": [
                    {
                        "itemShopID": item_shop_id,
                        "qoh": new_quantity
                    }
                ]
            }
        }

        response = requests.put(url, headers=headers, json=payload)
        if response.status_code == 401:  # Unauthorized error
            call_command('refresh_token')
            headers['Authorization'] = f'Bearer {settings.ACCESS_TOKEN}'
            response = requests.put(url, headers=headers, json=payload)

        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse({'error': 'Failed to update item quantity', 'details': response.text}, status=response.status_code)
    else:
        return render(request, 'oauth_handler/add_quantity_to_item.html')

@csrf_exempt
@user_passes_test(is_admin)
@login_required
def update_multiple_items_preview(request):
    if request.method == 'POST':
        updates = []
        for key, value in request.POST.items():
            if key.startswith('manufacturer_sku_') or key.startswith('upc_'):
                index = key.split('_')[-1]
                manufacturer_sku = request.POST.get(f'manufacturer_sku_{index}')
                upc = request.POST.get(f'upc_{index}')
                quantity = request.POST.get(f'quantity_{index}')
                if (manufacturer_sku or upc) and quantity:
                    updates.append({
                        'manufacturer_sku': manufacturer_sku,
                        'upc': upc,
                        'quantity': int(quantity)
                    })

        request.session['updates'] = updates
        request.session['toggle_choice'] = request.POST.get('global_toggle', 'sku')

        if settings.ACCESS_TOKEN is None:
            return JsonResponse({'error': 'Access token not available'}, status=400)

        item_details = []
        for update in updates:
            identifier = update.get('manufacturer_sku') or update.get('upc')
            quantity_to_add = int(update.get('quantity'))
            search_field = 'manufacturerSku' if update.get('manufacturer_sku') else 'upc'

            # Get item details
            url = f"https://api.lightspeedapp.com/API/V3/Account/{settings.LIGHTSPEED_ACCOUNT_ID}/Item.json"
            params = {
                'load_relations': '["ItemShops"]',
                search_field: identifier
            }
            headers = {
                'Authorization': f'Bearer {settings.ACCESS_TOKEN}'
            }

            response = requests.get(url, headers=headers, params=params)
            response_data = response.json()
            logging.info(f"Response data for {search_field} {identifier}: {response_data}")

            if response.status_code == 401:  # Unauthorized error
                call_command('refresh_token')
                headers['Authorization'] = f'Bearer {settings.ACCESS_TOKEN}'
                response = requests.get(url, headers=headers, params=params)
                response_data = response.json()

            if response.status_code != 200 or 'Item' not in response_data:
                item_details.append({'identifier': identifier, 'status': 'failed', 'reason': 'Failed to fetch item details'})
                continue

            item_data = response_data['Item']
            if not isinstance(item_data, list):
                item_data = [item_data]
            item_data = item_data[0]
            item_id = item_data['itemID']
            description = item_data.get('description', 'No description available')

            # Find the correct ItemShop
            item_shop = next((shop for shop in item_data['ItemShops']['ItemShop'] if shop['shopID'] != '0'), None)
            if not item_shop:
                item_details.append({'identifier': identifier, 'status': 'failed', 'reason': 'Valid ItemShop not found'})
                continue

            item_shop_id = item_shop['itemShopID']
            current_qoh = int(item_shop['qoh'])

            item_details.append({
                'identifier': identifier,
                'quantity_to_add': quantity_to_add,
                'current_qoh': current_qoh,
                'new_qoh': current_qoh + quantity_to_add,
                'description': description,
                'item_id': item_id,
                'item_shop_id': item_shop_id,
                'search_field': search_field
            })

        request.session['item_details'] = item_details
        return redirect('confirm_update_items')
    else:
        updates = request.session.get('updates', [])
        toggle_choice = request.session.get('toggle_choice', 'sku')
        return render(request, 'oauth_handler/update_multiple_items.html', {'updates': updates, 'toggle_choice': toggle_choice})

@csrf_exempt
@user_passes_test(is_admin)
@login_required
def confirm_update_items(request):
    if request.method == 'POST':
        item_details = request.session.get('item_details', [])

        if settings.ACCESS_TOKEN is None:
            return JsonResponse({'error': 'Access token not available'}, status=400)

        results = []
        for item in item_details:
            identifier = item['identifier']
            new_quantity = item['new_qoh']
            item_id = item['item_id']
            item_shop_id = item['item_shop_id']

            # Update item quantity
            url = f"https://api.lightspeedapp.com/API/V3/Account/{settings.LIGHTSPEED_ACCOUNT_ID}/Item/{item_id}.json"
            payload = {
                "ItemShops": {
                    "ItemShop": [
                        {
                            "itemShopID": item_shop_id,
                            "qoh": new_quantity
                        }
                    ]
                }
            }
            headers = {
                'Authorization': f'Bearer {settings.ACCESS_TOKEN}',
                'Content-Type': 'application/json'
            }

            response = requests.put(url, headers=headers, json=payload)
            if response.status_code == 401:  # Unauthorized error
                call_command('refresh_token')
                headers['Authorization'] = f'Bearer {settings.ACCESS_TOKEN}'
                response = requests.put(url, headers=headers, json=payload)

            if response.status_code == 200:
                results.append({'identifier': identifier, 'status': 'success'})
            else:
                results.append({'identifier': identifier, 'status': 'failed', 'reason': response.text})

        all_success = all(result['status'] == 'success' for result in results)

        if all_success:
            request.session.pop('item_details', None)  # Clear session data after successful update
            request.session.pop('updates', None)
            request.session.pop('toggle_choice', None)
            return render(request, 'oauth_handler/confirm_success.html')
        else:
            return JsonResponse({'results': results})
    else:
        item_details = request.session.get('item_details', [])
        toggle_choice = request.session.get('toggle_choice', 'sku')
        return render(request, 'oauth_handler/confirm_update_items.html', {'item_details': item_details, 'toggle_choice': toggle_choice})

@csrf_exempt
@user_passes_test(is_admin)
@login_required
def get_customer_details(request, customer_id):
    if request.method == 'GET':
        if settings.ACCESS_TOKEN is None:
            return JsonResponse({'error': 'Access token not available'}, status=400)

        url = f"https://api.lightspeedapp.com/API/V3/Account/{settings.LIGHTSPEED_ACCOUNT_ID}/Customer/{customer_id}.json"
        headers = {
            'Authorization': f'Bearer {settings.ACCESS_TOKEN}'
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 401:  # Unauthorized error
            call_command('refresh_token')
            headers['Authorization'] = f'Bearer {settings.ACCESS_TOKEN}'
            response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse({'error': 'Failed to fetch customer details'}, status=response.status_code)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
@user_passes_test(is_admin)
@login_required
def get_credit_account_details(request):
    if request.method == 'GET':
        if settings.ACCESS_TOKEN is None:
            return JsonResponse({'error': 'Access token not available'}, status=400)

        url = f"https://api.lightspeedapp.com/API/V3/Account/{settings.LIGHTSPEED_ACCOUNT_ID}/CreditAccount.json"
        headers = {
            'Authorization': f'Bearer {settings.ACCESS_TOKEN}'
        }

        all_credit_accounts = []
        response = requests.get(url, headers=headers)
        while response.status_code == 200:
            data = response.json()
            credit_accounts = data.get('CreditAccount', [])
            if not isinstance(credit_accounts, list):
                credit_accounts = [credit_accounts]

            all_credit_accounts.extend(credit_accounts)
            next_url = data['@attributes'].get('next', '')
            if not next_url:
                break
            response = requests.get(next_url, headers=headers)

            if response.status_code == 401:  # Unauthorized error
                call_command('refresh_token')
                headers['Authorization'] = f'Bearer {settings.ACCESS_TOKEN}'
                response = requests.get(next_url, headers=headers)

        customer_details = []
        total_balance = 0
        for account in all_credit_accounts:
            if float(account.get('balance', 0)) > 0 and float(account.get('creditLimit', 0)) > 0:
                customer_id = account.get('customerID')
                customer_info = get_customer_info(customer_id)
                if customer_info:
                    customer_info['creditLimit'] = account.get('creditLimit')
                    customer_info['balance'] = account.get('balance')
                    customer_info['percentageUsed'] = round((float(account.get('balance')) / float(account.get('creditLimit'))) * 100, 2)
                    customer_details.append(customer_info)
                    total_balance += float(account.get('balance'))

        # Sort customers by balance in descending order
        customer_details = sorted(customer_details, key=lambda x: float(x['balance']), reverse=True)

        return render(request, 'oauth_handler/credit_account_details.html', {
            'customer_details': customer_details,
            'total_balance': total_balance
        })
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_customer_info(customer_id):
    url = f"https://api.lightspeedapp.com/API/V3/Account/{settings.LIGHTSPEED_ACCOUNT_ID}/Customer/{customer_id}.json"
    params = {
        'load_relations': '["Contact"]'
    }
    headers = {
        'Authorization': f'Bearer {settings.ACCESS_TOKEN}'
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 401:  # Unauthorized error
        call_command('refresh_token')
        headers['Authorization'] = f'Bearer {settings.ACCESS_TOKEN}'
        response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        customer_data = response.json().get('Customer', {})
        contact_data = customer_data.get('Contact', {})

        # Check if 'Emails' and 'Phones' are dictionaries before proceeding
        emails_dict = contact_data.get('Emails', {})
        phones_dict = contact_data.get('Phones', {})

        # Ensure we are dealing with dictionaries
        emails = emails_dict['ContactEmail'] if isinstance(emails_dict, dict) and 'ContactEmail' in emails_dict else []
        phones = phones_dict['ContactPhone'] if isinstance(phones_dict, dict) and 'ContactPhone' in phones_dict else []

        # Process emails and phones safely
        email = next((email['address'] for email in (emails if isinstance(emails, list) else [emails]) if 'address' in email), None)
        phone = next((phone['number'] for phone in (phones if isinstance(phones, list) else [phones]) if 'number' in phone), None)

        return {
            'email': email,
            'firstName': customer_data.get('firstName'),
            'lastName': customer_data.get('lastName'),
            'phone': phone,
            'customerID': customer_id
        }
    else:
        return None



from django.http import JsonResponse

def fetch_all_vendors_view(request):
    # Start with the initial API endpoint
    next_page_url = f"https://api.lightspeedapp.com/API/V3/Account/{settings.LIGHTSPEED_ACCOUNT_ID}/Vendor.json"
    headers = {'Authorization': f'Bearer {settings.ACCESS_TOKEN}'}
    vendor_map = {}

    # Loop through pagination
    while next_page_url:
        response = requests.get(next_page_url, headers=headers)

        # Handle unauthorized error by refreshing the token
        if response.status_code == 401:
            call_command('refresh_token')
            headers['Authorization'] = f'Bearer {settings.ACCESS_TOKEN}'
            response = requests.get(next_page_url, headers=headers)  # Reattempt the request with the new token

        # Process the response if successful
        if response.status_code == 200:
            data = response.json()
            for vendor in data.get('Vendor', []):
                vendor_obj, created = Vendor.objects.get_or_create(name=vendor['name'])
                vendor_map[vendor['vendorID']] = vendor_obj.name  # Store the name instead of the object

            # Update the URL for the next page, or break if there is no next page
            next_page_url = data.get('@attributes', {}).get('next', None)
        else:
            # If an error occurs that isn't handled by the token refresh, log the issue and break the loop
            print(f"Failed to fetch vendors with status code: {response.status_code}")
            break  # Exit loop on failure other than 401

    # Always return an HttpResponse object such as JsonResponse
    return JsonResponse(vendor_map, safe=False)


import os
import requests
from django.http import JsonResponse
from django.conf import settings
from django.core.management import call_command
from django.db import IntegrityError
from .models import Vendor, Category, Item, ItemImage, Brand, TaxClass
from django.utils.timezone import now

def fetch_all_items(request):
    def download_images_for_item(item, image_data_list, image_dir):
        for image_data in image_data_list:
            base_url = image_data['baseImageURL']
            public_id = image_data['publicID']
            image_url = f"{base_url}/{public_id}.jpg"
            image_path = os.path.join(image_dir, f"{public_id}.jpg")
            if not os.path.exists(image_path):
                if save_image(image_url, image_path):
                    ItemImage.objects.create(
                        item=item,
                        image_url=image_url,
                        image_path=image_path,
                        description=image_data.get('description', '')
                    )

    def save_image(image_url, save_path):
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(image_response.content)
            print(f"Image saved successfully at {save_path}")
            return True
        else:
            print(f"Failed to download image from {image_url}")
            return False

    def extract_prices(prices_data):
        price_info = {'default': 0, 'msrp': 0, 'online': 0}
        for price in prices_data.get('ItemPrice', []):
            if price['useType'].lower() == 'default':
                price_info['default'] = float(price['amount'])
            elif price['useType'].lower() == 'msrp':
                price_info['msrp'] = float(price['amount'])
            elif price['useType'].lower() == 'online':
                price_info['online'] = float(price['amount'])
        return price_info

    def handle_rate_limiting(response):
        if 'X-LS-API-Bucket-Level' in response.headers:
            bucket_level, bucket_size = map(float, response.headers['X-LS-API-Bucket-Level'].split('/'))
            drip_rate = float(response.headers.get('X-LS-API-Drip-Rate', 1))

            if bucket_level >= bucket_size:
                wait_time = (bucket_level - bucket_size) / drip_rate
                print(f"Rate limit hit, sleeping for {wait_time:.2f} seconds...")
                time.sleep(wait_time)

    def fetch_data_with_rate_limiting(url, headers):
        while True:
            response = requests.get(url, headers=headers)
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 1))
                print(f"Rate limit exceeded, retrying after {retry_after} seconds...")
                time.sleep(retry_after)
            elif response.status_code == 401:
                call_command('refresh_token')
                headers['Authorization'] = f'Bearer {settings.ACCESS_TOKEN}'
            else:
                handle_rate_limiting(response)
                return response

    def fetch_all_vendors():
        next_page_url = f"https://api.lightspeedapp.com/API/V3/Account/{settings.LIGHTSPEED_ACCOUNT_ID}/Vendor.json"
        headers = {'Authorization': f'Bearer {settings.ACCESS_TOKEN}'}
        vendor_map = {}

        while next_page_url:
            response = fetch_data_with_rate_limiting(next_page_url, headers)
            if response.status_code == 200:
                data = response.json()
                for vendor in data.get('Vendor', []):
                    vendor_obj, created = Vendor.objects.get_or_create(name=vendor['name'])
                    vendor_map[vendor['vendorID']] = vendor_obj
                next_page_url = data.get('@attributes', {}).get('next', None)
            else:
                print(f"Failed to fetch vendors with status code: {response.status_code}")
                break
        return vendor_map

    def fetch_all_categories():
        next_page_url = f"https://api.lightspeedapp.com/API/V3/Account/{settings.LIGHTSPEED_ACCOUNT_ID}/Category.json"
        headers = {'Authorization': f'Bearer {settings.ACCESS_TOKEN}'}
        category_map = {}

        while next_page_url:
            response = fetch_data_with_rate_limiting(next_page_url, headers)
            if response.status_code == 200:
                data = response.json()
                for category in data.get('Category', []):
                    category_obj, created = Category.objects.get_or_create(
                        category_id=category['categoryID'],
                        defaults={'name': category['name'], 'create_time': now()}
                    )
                    category_map[category['categoryID']] = category_obj
                next_page_url = data.get('@attributes', {}).get('next', None)
            else:
                print(f"Failed to fetch categories with status code: {response.status_code}")
                break
        return category_map

    vendor_map = fetch_all_vendors()
    category_map = fetch_all_categories()

    default_category, _ = Category.objects.get_or_create(
        category_id=0,
        defaults={'name': 'Unknown', 'left_node': 0, 'right_node': 0, 'node_depth': 0, 'full_path_name': 'Unknown', 'create_time': now(), 'last_modified': now()}
    )

    image_dir = os.path.join(settings.BASE_DIR, 'image', 'items_image')
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    next_page_url = f"https://api.lightspeedapp.com/API/V3/Account/{settings.LIGHTSPEED_ACCOUNT_ID}/Item.json?load_relations=[\"Manufacturer\",\"Category\",\"TaxClass\",\"ItemShops\",\"ItemVendorNums\",\"ItemComponents\",\"ItemAttributes\"]"
    headers = {'Authorization': f'Bearer {settings.ACCESS_TOKEN}'}

    missing_items = []
    while next_page_url:
        response = fetch_data_with_rate_limiting(next_page_url, headers)
        if response.status_code == 200:
            data = response.json()
            items = data.get('Item', [])
            if isinstance(items, dict):
                items = [items]

            for item_data in items:
                if not isinstance(item_data, dict):
                    print(f"Invalid item_data format: {item_data}")
                    missing_items.append(item_data)
                    continue

                try:
                    item_shops = item_data.get('ItemShops', {}).get('ItemShop', [])
                    qoh = sum(
                        int(shop['qoh']) for shop in item_shops if shop.get('qoh'))

                    reorder_point = max(
                        int(shop['reorderPoint']) for shop in item_shops if shop.get('reorderPoint')) if item_shops else 0
                    reorder_level = max(
                        int(shop['reorderLevel']) for shop in item_shops if shop.get('reorderLevel')) if item_shops else 0

                    price_info = extract_prices(item_data.get('Prices', {}))

                    default_vendor_id = item_data.get('defaultVendorID', None)
                    vendor = vendor_map.get(default_vendor_id, Vendor.objects.get_or_create(name='Unknown')[0])
                    category_id = item_data.get('categoryID', None)
                    category = category_map.get(category_id, default_category)

                    item, created = Item.objects.update_or_create(
                        manufacturer_sku=item_data['manufacturerSku'],
                        defaults={
                            'itemID': item_data['itemID'],
                            'description': item_data.get('description', ''),
                            'system_sku': item_data.get('systemSku', ''),
                            'default_cost': item_data.get('defaultCost', 0),
                            'average_cost': item_data.get('avgCost', 0),
                            'quantity_on_hand': qoh,
                            'reorder_point': reorder_point,
                            'reorder_level': reorder_level,
                            'vendor': vendor,
                            'category': category,
                            'brand': Brand.objects.get_or_create(
                                name=item_data.get('Manufacturer', {}).get('name', 'Unknown'))[0],
                            'tax_class': TaxClass.objects.get_or_create(
                                name=item_data.get('TaxClass', {}).get('name', 'Unknown'))[0],
                            'price_default': price_info.get('default', 0),
                            'price_msrp': price_info.get('msrp', 0),
                            'price_online': price_info.get('online', 0),
                        }
                    )
                    if created:
                        print(f"Created new item: {item}")
                    else:
                        print(f"Updated existing item: {item}")

                    url = f"https://api.lightspeedapp.com/API/V3/Account/{settings.LIGHTSPEED_ACCOUNT_ID}/Item/{item_data['itemID']}/Image"
                    headers = {'Authorization': f'Bearer {settings.ACCESS_TOKEN}', 'Accept': 'application/json'}
                    image_response = fetch_data_with_rate_limiting(url, headers)
                    if image_response.status_code == 200:
                        image_data = image_response.json()
                        if 'Image' in image_data and image_data['Image']:
                            if isinstance(image_data['Image'], list):
                                download_images_for_item(item, image_data['Image'], image_dir)
                            else:
                                download_images_for_item(item, [image_data['Image']], image_dir)

                except IntegrityError as e:
                    print(f"Failed to process item {item_data.get('manufacturerSku', 'Unknown')} due to database error: {str(e)}")
                    missing_items.append(item_data.get('manufacturerSku', 'Unknown'))
                except Exception as e:
                    print(f"Failed to process item {item_data.get('manufacturerSku', 'Unknown')} due to error: {str(e)}")
                    missing_items.append(item_data.get('manufacturerSku', 'Unknown'))

            next_page_url = data.get('@attributes', {}).get('next', None)
        else:
            print(f"Failed to fetch items with status code: {response.status_code}")
            break

    if missing_items:
        print(f"Missing items SKUs: {missing_items}")
    return JsonResponse({'message': 'Items fetched and updated successfully', 'missing_items': missing_items})





from django.shortcuts import render
from django.db.models import Q
from .models import Item, Brand, Vendor, Category

from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Q

def list_items(request):
    brands = Brand.objects.all().order_by('name')
    vendors = Vendor.objects.all().order_by('name')
    categories = Category.objects.filter(parent=None).order_by('name')

    selected_category = None
    subcategories = None

    brand_query = request.GET.get('brand', '')
    vendor_query = request.GET.get('vendor', '')
    category_query = request.GET.get('category', '')
    search_query = request.GET.get('search', '')

    # Normalize the search query to avoid "None" string issue
    search_query = search_query if search_query.lower() != 'none' else ''

    items = Item.objects.all()

    if brand_query:
        items = items.filter(brand__name=brand_query)
    if vendor_query:
        items = items.filter(vendor__name=vendor_query)
    if category_query:
        try:
            selected_category = Category.objects.get(id=category_query)
            descendants_ids = [descendant.id for descendant in selected_category.get_descendants()]
            items = items.filter(Q(category__id=selected_category.id) | Q(category__id__in=descendants_ids))
            subcategories = selected_category.children.all().order_by('name')
        except Category.DoesNotExist:
            items = Item.objects.none()
    if search_query:
        items = items.filter(
            Q(manufacturer_sku__icontains=search_query) |
            Q(system_sku__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Implement pagination
    paginator = Paginator(items, 100)  # Show 100 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,  # Pass the page object instead of full item list
        'brands': brands,
        'vendors': vendors,
        'categories': categories,
        'subcategories': subcategories,
        'selected_category': selected_category,
        'brand_query': brand_query,
        'vendor_query': vendor_query,
        'category_query': category_query,
        'search_query': search_query,
    }

    return render(request, 'oauth_handler/items_list.html', context)

















from django.http import JsonResponse
from .models import Category

from django.http import JsonResponse
from .models import Category

def load_subcategories(request, category_id):
    subcategories = Category.objects.filter(parent_id=category_id).order_by('name')
    subcategories_data = [{'id': sub.id, 'name': sub.name} for sub in subcategories]
    return JsonResponse({'subcategories': subcategories_data})


from django.shortcuts import render, get_object_or_404
from datetime import date
from .models import Item

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Item

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Item

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Item

def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    today = timezone.localdate()  # Get the current date adjusted for timezone

    # Filter the price records to include only those from today or before and order them by date descending
    price_records = item.price_records.filter(record_date__lte=today).order_by('-record_date')

    # Prepare price data
    price_data = {
        'default_price': item.price_default,
        'msrp_price': item.price_msrp,
        'online_price': item.price_online
    }

    return render(request, 'oauth_handler/item_detail.html', {
        'item': item,
        'price_records': price_records,  # Pass filtered and sorted records to the template
        'price_data': price_data  # Pass price data to the template
    })

import requests
from django.conf import settings
from django.core.management import call_command
from .models import Category
from django.utils.dateparse import parse_datetime

def fetch_categories_data():
    next_page_url = f"https://api.lightspeedapp.com/API/V3/Account/{settings.LIGHTSPEED_ACCOUNT_ID}/Category.json"
    headers = {'Authorization': f'Bearer {settings.ACCESS_TOKEN}'}

    all_categories = []
    category_map = {}

    # Fetch all categories first
    while next_page_url:
        response = requests.get(next_page_url, headers=headers)
        if response.status_code == 401:  # Handle unauthorized error
            call_command('refresh_token')
            headers['Authorization'] = f'Bearer {settings.ACCESS_TOKEN}'
            response = requests.get(next_page_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            categories = data.get('Category', [])
            all_categories.extend(categories)
            next_page_url = data.get('@attributes', {}).get('next', None)
        else:
            return False  # Return False if there was a failure to fetch the data

    # Update/Create categories without setting parent
    for category_data in all_categories:
        category_id = category_data['categoryID']
        category, created = Category.objects.update_or_create(
            category_id=category_id,
            defaults={
                'name': category_data['name'],
                'node_depth': int(category_data['nodeDepth']),
                'full_path_name': category_data['fullPathName'],
                'left_node': int(category_data['leftNode']),
                'right_node': int(category_data['rightNode']),
                'create_time': parse_datetime(category_data['createTime']),
                'last_modified': parse_datetime(category_data['timeStamp'])
            }
        )
        category_map[category_id] = category

    # Set parent relationships in a second pass
    for category_data in all_categories:
        category = category_map[category_data['categoryID']]
        parent_id = category_data.get('parentID')
        if parent_id and parent_id in category_map:
            category.parent = category_map[parent_id]
            category.save()

    return True  # Return True if everything went well


def fetch_all_categories(request):
    if not fetch_categories_data():  # Use the adjusted function with pagination
        return JsonResponse({'error': 'Failed to fetch categories'}, status=500)
    return JsonResponse({'success': 'Categories updated successfully'})

from django.shortcuts import render
from django.db.models import Q
from .models import Item, Brand, Vendor, Category

from django.core.paginator import Paginator

def list_reorder_items(request):
    items = Item.objects.filter(quantity_on_hand__lte=models.F('reorder_point'))

    # Filtering by Brand, Vendor, Category
    brand_query = request.GET.get('brand', '')
    vendor_query = request.GET.get('vendor', '')
    category_query = request.GET.get('category', '')
    search_query = request.GET.get('search', '')

    # Normalize the search query to avoid "None" string issue
    search_query = search_query if search_query.lower() != 'none' else ''

    if brand_query:
        items = items.filter(brand__name=brand_query)
    if vendor_query:
        items = items.filter(vendor__name=vendor_query)
    if category_query:
        try:
            selected_category = Category.objects.get(id=category_query)
            descendants_ids = [descendant.id for descendant in selected_category.get_descendants()]
            items = items.filter(Q(category__id=selected_category.id) | Q(category__id__in=descendants_ids))
        except Category.DoesNotExist:
            items = Item.objects.none()
    if search_query:
        items = items.filter(
            Q(description__icontains=search_query) |
            Q(manufacturer_sku__icontains=search_query)
        )

    # Paginate items (100 per page)
    paginator = Paginator(items, 100)  # Show 100 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    brands = Brand.objects.all()
    vendors = Vendor.objects.all()
    categories = Category.objects.filter(parent=None)

    return render(request, 'oauth_handler/reorder_list.html', {
        'page_obj': page_obj,  # Pass the paginated items
        'brands': brands,
        'vendors': vendors,
        'categories': categories,
        'brand_query': brand_query,
        'vendor_query': vendor_query,
        'category_query': category_query,
        'search_query': search_query,
    })


#last updated




from django.shortcuts import render, redirect
from .models import Quote, QuoteItem, Item
from .forms import QuoteItemForm, ItemSearchForm  # Assuming you have or will create these forms

def list_quotes(request):
    quotes = Quote.objects.all()
    return render(request, 'oauth_handler/list_quotes.html', {'quotes': quotes})

from django.shortcuts import redirect, render
from django.urls import reverse
from .models import Quote

from django.shortcuts import redirect, render
from .models import Quote
from django.urls import reverse

def add_quote(request):
    if request.method == 'POST':
        new_quote = Quote()
        new_quote.save()  # This triggers the save method in the model which generates the quote_number.
        # Redirect to the add_quote_item view, passing the ID of the newly created quote
        return redirect(reverse('add_quote_item', kwargs={'quote_id': new_quote.id}))
    return render(request, 'oauth_handler/add_quote.html')

from django.shortcuts import redirect, render
from .models import Quote
from django.urls import reverse


def add_quote_item(request, quote_id):
    quote = Quote.objects.get(id=quote_id)
    items = Item.objects.none()
    item_search_form = ItemSearchForm(request.GET or None)

    if 'item_list' not in request.session or not request.session['item_list']:
        request.session['item_list'] = [
            {
                'item_id': str(item.item.id),  # Ensure ID is a string if needed
                'quantity': item.quantity,
                'price': str(item.price),  # Store price as string
                'description': item.item.description,
                'manufacturer_sku': item.item.manufacturer_sku
            } for item in quote.items.all()
        ]

    if request.method == 'GET' and item_search_form.is_valid():
        query = item_search_form.cleaned_data['query']
        items = Item.objects.filter(
            models.Q(description__icontains=query) |
            models.Q(manufacturer_sku__icontains=query)
        )

    if request.method == 'POST':
        print("POST data:", request.POST)  # Debug output

        if 'add_to_list' in request.POST:
            selected_items = request.POST.getlist('item_ids')
            for item_id in selected_items:
                item = Item.objects.get(id=item_id)
                quantity = request.POST.get(f'quantity_{item_id}', 1)
                price = request.POST.get(f'price_{item_id}', item.price_default)
                request.session['item_list'].append({
                    'item_id': str(item_id),  # Consistent data type
                    'quantity': quantity,
                    'price': str(price),  # Store price as string
                    'description': item.description,
                    'manufacturer_sku': item.manufacturer_sku
                })
            request.session.modified = True

        elif 'remove_from_list' in request.POST:
            item_id_to_remove = request.POST.get('remove_from_list')
            print("Removing item:", item_id_to_remove)  # Debug output
            new_list = [item for item in request.session['item_list'] if item['item_id'] != item_id_to_remove]
            request.session['item_list'] = new_list
            request.session.modified = True

        elif 'update_item' in request.POST:
            item_id_to_update = request.POST.get('update_item')
            print("Updating item:", item_id_to_update)  # Debug output
            for item in request.session['item_list']:
                if item['item_id'] == item_id_to_update:
                    item['quantity'] = request.POST.get(f'quantity_{item_id_to_update}', item['quantity'])
                    item['price'] = str(request.POST.get(f'price_{item_id_to_update}', item['price']))
            request.session.modified = True

        if 'submit_all' in request.POST:
            quote.items.all().delete()
            for item_data in request.session['item_list']:
                item = Item.objects.get(id=item_data['item_id'])
                QuoteItem.objects.create(
                    quote=quote,
                    item=item,
                    quantity=int(item_data['quantity']),
                    price=Decimal(item_data['price'])
                )
            request.session['item_list'] = []
            return redirect('edit_quote', quote_id=quote_id)

    session_items = request.session.get('item_list', [])
    return render(request, 'oauth_handler/add_quote_item.html', {
        'quote': quote,
        'item_search_form': item_search_form,
        'items': items,
        'session_items': session_items
    })









def edit_quote(request, quote_id):
    quote = Quote.objects.get(id=quote_id)
    return render(request, 'oauth_handler/edit_quote.html', {'quote': quote})



#


import os
import requests
from django.http import JsonResponse
from django.conf import settings


def fetch_specific_item_image(request):
    # Directory where images will be saved
    image_dir = os.path.join(settings.BASE_DIR, 'image', 'items_image')
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    # Specific API endpoint for item 16339
    url = "https://api.lightspeedapp.com/API/V3/Account/292471/Item/16339/Image"
    headers = {
        'Authorization': f'Bearer {settings.ACCESS_TOKEN}',
        'Accept': 'application/json'
    }

    # Fetching image metadata from Lightspeed API
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'Image' in data and data['Image']:
            image_data = data['Image']
            base_url = image_data['baseImageURL']
            public_id = image_data['publicID']
            image_url = f"{base_url}/{public_id}.jpg"

            # Downloading the image
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                image_path = os.path.join(image_dir, f"{public_id}.jpg")
                with open(image_path, 'wb') as f:
                    f.write(image_response.content)
                return JsonResponse({'success': f'Image saved successfully at {image_path}'})
            else:
                return JsonResponse({'error': 'Failed to download image', 'status_code': image_response.status_code})
        else:
            return JsonResponse({'error': 'No images found for this item', 'api_response': data})
    else:
        return JsonResponse(
            {'error': 'Failed to fetch image data from Lightspeed API', 'status_code': response.status_code,
             'response': response.text})



from django.shortcuts import render
from .models import Category

from django.shortcuts import render
from .models import Category

from django.shortcuts import render
from .models import Category


def show_categories(request):
    category_id = request.GET.get('category_id')
    parent_category = None
    if category_id:
        categories = Category.objects.filter(parent_id=category_id)  # Subcategories
        parent_category = Category.objects.get(id=category_id)  # For navigation
    else:
        categories = Category.objects.filter(parent=None)  # Root categories

    return render(request, 'oauth_handler/categories.html', {
        'categories': categories,
        'parent_category': parent_category
    })


def build_category_tree(categories):
    # This function might not be necessary with the updated approach but let's keep it for now
    category_dict = {category.id: category for category in categories}
    root_categories = []
    for category in categories:
        if category.parent:
            parent = category_dict.get(category.parent_id)
            if hasattr(parent, 'children'):
                parent.children.append(category)
            else:
                parent.children = [category]
        else:
            root_categories.append(category)
    return root_categories




from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from django.conf import settings
from django.core.management import call_command

@csrf_exempt
@user_passes_test(is_admin)
@login_required
def display_customer_details(request):
    if settings.ACCESS_TOKEN is None:
        return JsonResponse({'error': 'Access token not available'}, status=400)

    url = f"https://api.lightspeedapp.com/API/V3/Account/{settings.LIGHTSPEED_ACCOUNT_ID}/Customer.json"
    headers = {
        'Authorization': f'Bearer {settings.ACCESS_TOKEN}'
    }
    params = {
        'load_relations': '["Contact"]'
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 401:
        call_command('refresh_token')
        headers['Authorization'] = f'Bearer {settings.ACCESS_TOKEN}'
        response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return JsonResponse({'error': 'Failed to fetch customer details'}, status=response.status_code)

    customers = response.json().get('Customer', [])

    return render(request, 'oauth_handler/all_customers_details.html', {'customers': customers})





import requests
from django.http import JsonResponse
from django.core.management import call_command
from .models import CustomerLightspeed
from django.conf import settings
from urllib.parse import unquote
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def fetch_all_customer_ids():
    url = f"https://api.lightspeedapp.com/API/V3/Account/{settings.LIGHTSPEED_ACCOUNT_ID}/Customer.json?limit=100"
    headers = {'Authorization': f'Bearer {settings.ACCESS_TOKEN}'}
    customer_ids = []

    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            customers = data.get('Customer', [])
            customer_ids.extend([customer['customerID'] for customer in customers])

            next_url = data.get('@attributes', {}).get('next', None)
            if next_url:
                url = unquote(next_url)
            else:
                url = None
        elif response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 0))  # Default to 60 seconds if header is missing
            logging.info(f"Rate limited. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            continue
        else:
            logging.error(f"Failed to fetch data: {response.status_code}")
            break  # Optionally, handle different error statuses differently

    return customer_ids

import time
import logging
from django.db import OperationalError, transaction

def fetch_and_update_customer_details(customer_ids):
    total_customers_updated = 0
    total_customers_processed = 0
    max_retries = 5  # Maximum number of retries per customer

    for customer_id in customer_ids:
        total_customers_processed += 1
        retry_count = 0

        while retry_count < max_retries:
            try:
                with transaction.atomic():
                    customer_info = get_customer_info(customer_id)
                    if customer_info:
                        Customer.objects.update_or_create(
                            customer_id=customer_info['customerID'],
                            defaults=customer_info
                        )
                        total_customers_updated += 1
                        break  # Break out of the retry loop on success
            except OperationalError as e:
                if 'locked' in str(e):
                    retry_count += 1
                    time.sleep(1)  # Wait for 1 second before retrying
                    logging.warning(f"Database locked, retrying update for customer {customer_id} ({retry_count}/{max_retries})")
                else:
                    logging.error(f"Error updating customer {customer_id}: {e}")
                    break
            except Exception as e:
                logging.error(f"Error updating customer {customer_id}: {e}")
                break

        if total_customers_processed % 100 == 0:
            logging.info(f"Processed {total_customers_processed} customers, updated {total_customers_updated} so far.")

    logging.info(f"Total customers processed: {total_customers_processed}, total updated: {total_customers_updated}")
    return total_customers_updated

def update_customers(request):
    customer_ids = fetch_all_customer_ids()
    total_updated = fetch_and_update_customer_details(customer_ids)
    return JsonResponse({'message': f'Successfully fetched and updated {total_updated} customers.'})



import time
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from django.conf import settings
from django.core.management import call_command

import time
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.management import call_command

import time
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.management import call_command

@csrf_exempt
@user_passes_test(is_admin)
@login_required
def archive_customers(request):
    if request.method == 'POST':
        customer_ids_raw = request.POST.get('customer_ids')
        customer_ids = [customer_id.strip() for customer_id in customer_ids_raw.split(',') if customer_id.strip()]

        if settings.ACCESS_TOKEN is None:
            return JsonResponse({'error': 'Access token not available'}, status=400)

        headers = {
            'Authorization': f'Bearer {settings.ACCESS_TOKEN}'
        }

        archived_customers = []
        failed_customers = []

        for index, customer_id in enumerate(customer_ids):
            url = f"https://api.lightspeedapp.com/API/V3/Account/{settings.LIGHTSPEED_ACCOUNT_ID}/Customer/{customer_id}.json"

            response = requests.delete(url, headers=headers)
            if response.status_code == 401:  # Unauthorized error
                call_command('refresh_token')
                headers['Authorization'] = f'Bearer {settings.ACCESS_TOKEN}'
                response = requests.delete(url, headers=headers)

            if response.status_code == 429:  # Rate limited
                time.sleep(1.5)  # Wait for 1.5 seconds before retrying
                response = requests.delete(url, headers=headers)

            if response.status_code == 200:
                archived_customers.append(customer_id)
            else:
                failed_customers.append({
                    'customer_id': customer_id,
                    'status_code': response.status_code,
                    'response': response.text
                })

            # To avoid hitting the rate limit, wait for a bit before the next request
            time.sleep(1.5)  # 1.5 seconds delay to keep the request rate below 3 requests per second

        return JsonResponse({
            'archived_customers': archived_customers,
            'failed_customers': failed_customers
        })

    return render(request, 'oauth_handler/archive_customers.html')




import logging
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .forms import EmailForm

logger = logging.getLogger(__name__)

import logging
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .forms import EmailForm
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

from django.core.mail import EmailMessage
from django.core.mail import EmailMessage
from django.core.mail import EmailMessage
from time import sleep
from django.core.mail import EmailMessage

from django.core.mail import EmailMessage
import re

from django.core.mail import EmailMessage
import re
import time

@csrf_exempt
@user_passes_test(is_admin)
@login_required
def send_email(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            details = data.get('details', [])

            if not details:
                return JsonResponse({'success': False, 'error': 'No email details provided'}, status=400)

            valid_email_regex = r'^[^@]+@[^@]+\.[^@]+$'  # Regex for validating email addresses
            batch_size = 10  # Number of emails to process in each batch
            delay_between_batches = 5  # Delay in seconds between batches
            email_count = 0  # Counter for processed emails
            total_emails = len(details)  # Total emails to process

            for i, detail in enumerate(details):
                recipient_field = detail.get('email', '')
                html_message = detail.get('message', '')
                subject = "2025 Credit History Report"

                # Check if recipient_field is None or empty, or invalid
                if not recipient_field or recipient_field.lower() == "none":
                    logger.warning(f"Skipping email due to invalid recipient: {recipient_field}")
                    continue

                # Split and sanitize recipient addresses
                recipients = [
                    addr.strip() for addr in recipient_field.split(',')
                    if re.match(valid_email_regex, addr.strip())
                ]
    
                if not recipients:  # Skip if no valid recipients
                    logger.warning(f"Skipping email due to invalid recipient field: {recipient_field}")
                    continue

                # Create and send the email
                email = EmailMessage(
                    subject=subject,
                    body=html_message,
                    from_email='mekcosupply@gmail.com',
                    to=recipients,
                )
                email.content_subtype = "html"  # Specify the email format as HTML

                # Add high-importance headers
                email.extra_headers = {
                    'X-Priority': '1 (Highest)',
                    'X-MSMail-Priority': 'High',
                    'Importance': 'High',
                }

                # Send email
                email.send()
                email_count += len(recipients)
                logger.info(f"Email successfully sent to: {', '.join(recipients)}")

                # Log progress after every 10 emails
                if (i + 1) % batch_size == 0:
                    logger.info(f"Processed {i + 1} out of {total_emails} email details. Sleeping for {delay_between_batches} seconds...")
                    time.sleep(delay_between_batches)

            # Final log for remaining emails
            logger.info(f"All emails processed. Total emails sent: {email_count}")
            return JsonResponse({'success': True, 'message': f'Emails sent successfully. Total emails sent: {email_count}'})

        except json.JSONDecodeError:
            logger.error('Failed to parse JSON from request body')
            return JsonResponse({'success': False, 'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            logger.error(f"Error sending emails: {e}", exc_info=True)
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)








from django.http import JsonResponse
from .utils import send_sms

def send_message_view(request):
    """
    Handles SMS message sending via Twilio.
    """
    if request.method == "POST":
        to = request.POST.get("to")
        message = request.POST.get("message")
        if not to or not message:
            return JsonResponse({"status": "error", "message": "Missing 'to' or 'message' parameter"}, status=400)

        result = send_sms(to, message)
        return JsonResponse(result)
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)


from django.shortcuts import render
from django.http import JsonResponse
from .forms import SMSForm
from .utils import send_sms


def send_message_page(request):
    """
    Renders a page with a form to send SMS via Twilio.
    """
    if request.method == "POST":
        form = SMSForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data["phone_number"]
            message = form.cleaned_data["message"]

            # Send the SMS
            result = send_sms(phone_number, message)

            # Show success or error message
            if result["status"] == "success":
                return render(request, "oauth_handler/success.html", {"sid": result["sid"]})
            else:
                return render(request, "oauth_handler/error.html", {"error": result["message"]})
    else:
        form = SMSForm()

    return render(request, "oauth_handler/send_message.html", {"form": form})





from django.http import JsonResponse
from django.db.models import Q
from .models import Item

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from .models import Item

def search_items(request):
    """
    View to search for items by scanning or entering a query.
    Renders an HTML page if accessed without a query parameter.
    Returns JSON for search results when a query is provided.
    """
    query = request.GET.get('q', '').strip()

    # If no query, render the HTML page
    if not query:
        return render(request, 'oauth_handler/search_items.html')

    # Search across all relevant fields
    items = Item.objects.filter(
        Q(description__icontains=query) |
        Q(system_sku__icontains=query) |
        Q(manufacturer_sku__icontains=query) |
        Q(category__name__icontains=query) |
        Q(vendor__name__icontains=query) |
        Q(brand__name__icontains=query)
    ).values('id','description', 'quantity_on_hand')

    # Check if items were found
    if not items.exists():
        return JsonResponse({'message': 'No items found.'})

    # Return the name and quantity of found items
    return JsonResponse({'items': list(items)})



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from .models import Item

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Item
import json

@csrf_exempt
def update_quantity(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            action = data.get('action')  # 'add' or 'adjust'
            quantity = int(data.get('quantity', 0))

            # Fetch the item by ID
            item = Item.objects.get(pk=item_id)

            # Perform the quantity update
            if action == 'add':
                item.quantity_on_hand += quantity
            elif action == 'adjust':
                item.quantity_on_hand = quantity

            item.save()
            return JsonResponse({'message': 'Quantity updated successfully!', 'quantity_on_hand': item.quantity_on_hand})
        except Item.DoesNotExist:
            return JsonResponse({'error': 'Item not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

