import uuid
import json  # Add this line at the top of your views.py file

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .models import EcommerceItem, Cart, CartItem, Order, get_discounted_price
from .forms import *
from .models import *
from django.conf import settings
from django.core.mail import send_mail
from .templatetags.custom_filters import total_price as calculate_total_price
import logging
from oauth_handler.models import *
from decimal import Decimal, InvalidOperation
from .models import get_discounted_price
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)
from decimal import Decimal  # Import Decimal

# Add your view functions here, making sure to use get_discounted_price as needed


from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from customers.models import Customer
from django.db.models import Q
from django.shortcuts import render
from .models import Item  # Adjust if your model is named differently

from django.db.models import Q
from django.shortcuts import render
from .models import Item

from django.db.models import Q
from django.shortcuts import render
from .models import Item  # Ensure this is the correct import for your Item model


from django.core.paginator import Paginator

from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Item

from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Item

def item_search(request):
    query = request.GET.get('q')
    items = []

    if query:
        # Split the query into individual keywords
        keywords = query.split()

        # Construct Q objects to search across multiple fields with each keyword
        query_filter = Q()
        for keyword in keywords:
            keyword_filter = (
                Q(description__icontains=keyword) |
                Q(system_sku__icontains=keyword) |
                Q(manufacturer_sku__icontains=keyword)
            )
            query_filter &= keyword_filter  # Use '&' to require all keywords

        # Perform the search, sorted by relevance or another field if preferred
        items = Item.objects.filter(query_filter).distinct()

        # Process items to include discounted price, bag/box options, and quantity checks
        for item in items:
            # Add discounted price to each item
            item.discounted_price = get_discounted_price(item, request.user)

            # Check and set bag and box options
            item.has_bag_option = item.has_bag_option
            item.has_box_option = item.has_box_option

            # Calculate the availability of singles, bags, and boxes
            item.available_singles = item.quantity_on_hand
            item.available_bags = (
                item.quantity_on_hand // item.bag_quantity if item.has_bag_option and item.bag_quantity else 0
            )
            item.available_boxes = (
                item.quantity_on_hand // item.box_quantity if item.has_box_option and item.box_quantity else 0
            )

    # Paginate the items to show 100 items per page
    paginator = Paginator(items, 100)  # Show 100 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'ecommerce/test_search_results.html', {'page_obj': page_obj, 'query': query})





# def item_list(request):
#     brands = Brand.objects.all().order_by('name')
#     categories = Category.objects.filter(parent=None).prefetch_related('children').order_by('name')
#
#     brand_query = request.GET.get('brand', '')
#     category_query = request.GET.get('category', '')
#     search_query = request.GET.get('search', '')
#
#     items = Item.objects.filter(status='public').select_related('brand', 'category')
#
#     selected_category = None
#     subcategories = None
#
#     if category_query:
#         selected_category = get_object_or_404(Category, id=category_query)
#
#         # Use `values_list` to fetch only the `id`s of descendants.
#         descendants_ids = list(Category.objects.filter(parent=selected_category).values_list('id', flat=True))
#
#         # Apply the category and descendant filter to items
#         items = items.filter(Q(category__id=selected_category.id) | Q(category__id__in=descendants_ids))
#
#         # Load subcategories more efficiently by using `children` relation with prefetch
#         subcategories = selected_category.children.order_by('name')
#     else:
#         items = None  # No items should be loaded initially
#
#     if brand_query:
#         items = items.filter(brand__name=brand_query)
#
#     if search_query:
#         items = items.filter(
#             Q(manufacturer_sku__icontains=search_query) |
#             Q(system_sku__icontains=search_query) |
#             Q(description__icontains=search_query)
#         )
#
#     if items:
#         for item in items:
#             item.discounted_price = get_discounted_price(item, request.user)
#
#     full_category_path = []
#     if selected_category:
#         ancestor = selected_category
#         while ancestor:
#             full_category_path.insert(0, ancestor)
#             ancestor = ancestor.parent
#
#     context = {
#         'items': items,
#         'brands': brands,
#         'categories': categories,
#         'subcategories': subcategories,
#         'brand_query': brand_query,
#         'category_query': category_query,
#         'search_query': search_query,
#         'selected_category': selected_category,
#         'full_category_path': full_category_path,
#     }
#
#     return render(request, 'ecommerce/item_list.html', context)



from django.shortcuts import get_object_or_404
from .models import PricingRule
from customers.models import Customer


def get_category_full_path(category):
    path = []
    while category:
        path.insert(0, category)
        category = category.parent
    return path


def get_discounted_price(item, user_or_pricing_rule):
    def get_ancestors(category):
        ancestors = []
        while category.parent is not None:
            ancestors.append(category.parent)
            category = category.parent
        return ancestors

    if hasattr(user_or_pricing_rule, 'is_authenticated'):
        user = user_or_pricing_rule
        if not user.is_authenticated:
            return item.price_default
        customer = get_object_or_404(Customer, email=user.email)
        customer_type = customer.customer_type
    else:
        customer_type = user_or_pricing_rule.customer_type

    category_ancestors = get_ancestors(item.category)
    category_ancestors.append(item.category)

    # Get all applicable pricing rules
    pricing_rules = PricingRule.objects.filter(
        customer_type=customer_type,
        category__in=category_ancestors
    ).order_by('-discount_percentage')  # Order by discount percentage in descending order

    if pricing_rules.exists():
        # Apply the best available discount (highest discount percentage)
        best_pricing_rule = pricing_rules.first()
        discount = (best_pricing_rule.discount_percentage / 100) * item.price_default
        return round(item.price_default - discount, 2)
    else:
        return item.price_default


from oauth_handler.models import Item


# def item_detail(request, item_id):
#     # Fetch the item based on its ID and ensure it's public
#     item = get_object_or_404(Item, id=item_id, status='public')
#
#     # Default message if the item is not available for purchase
#     if item.quantity_on_hand < 1:
#         message = "This item is not available for purchase. Please contact our salespersons."
#     else:
#         message = ""
#
#     # Calculate the discounted price for the main item (single item)
#     item.discounted_price = get_discounted_price(item, request.user)
#
#     # Initialize bag and box items to None
#     bag_item = None
#     box_item = None
#
#     # If the item has a bag option
#     if item.has_bag_option:
#         # Bag quantity check
#         bag_item = item  # In this case, bag_item refers to the same item with bag options
#
#     # If the item has a box option
#     if item.has_box_option:
#         # Box quantity check
#         box_item = item  # In this case, box_item refers to the same item with box options
#
#     # Calculate the number of available singles, bags, and boxes based on the total stock
#     available_singles = item.quantity_on_hand
#     available_bags = available_singles // item.bag_quantity if bag_item and item.bag_quantity else 0  # Full bags
#     available_boxes = available_singles // item.box_quantity if box_item and item.box_quantity else 0  # Full boxes
#
#     # Remaining singles after using up bags and boxes
#     remaining_singles = available_singles % item.bag_quantity if bag_item else available_singles
#
#     # Fetch item images (if any)
#     images = item.images.all()
#
#     # Prepare the context for rendering the template
#     context = {
#         'item': item,
#         'message': message,
#         'images': images,
#         'bag_item': bag_item,
#         'box_item': box_item,
#         'available_singles': available_singles,
#         'available_bags': available_bags,
#         'available_boxes': available_boxes,
#         'remaining_singles': remaining_singles,
#     }
#
#     return render(request, 'ecommerce/item_detail.html', context)


from django.contrib import messages


from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ecommerce.models import Cart, CartItem, Item

from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ecommerce.models import Cart, CartItem, Item

@login_required
def add_to_cart(request, item_id):
    # Fetch the item based on its ID and ensure it's public
    item = get_object_or_404(Item, id=item_id, status='public')

    # Create or fetch the cart for the user
    cart, created = Cart.objects.get_or_create(customer=request.user, completed=False)

    if request.method == 'POST':
        requested_quantity = int(request.POST.get('quantity', 0))
        item_type = request.POST.get('item_type', 'single')

        # Calculate total items in the cart for this product, across all types (box, bag, single)
        total_single_equivalent = 0

        # Calculate total single-equivalent items in the cart from box and bag items
        if item.has_box_option:
            box_item = Item.objects.filter(manufacturer_sku=f"{item.system_sku}-Box-{item.box_quantity}").first()
            if box_item:
                box_cart_item = CartItem.objects.filter(cart=cart, item=box_item).first()
                if box_cart_item:
                    total_single_equivalent += box_cart_item.quantity * item.box_quantity

        if item.has_bag_option:
            bag_item = Item.objects.filter(manufacturer_sku=f"{item.system_sku}-Bag-{item.bag_quantity}").first()
            if bag_item:
                bag_cart_item = CartItem.objects.filter(cart=cart, item=bag_item).first()
                if bag_cart_item:
                    total_single_equivalent += bag_cart_item.quantity * item.bag_quantity

        # Count the single items already in the cart
        existing_cart_item = CartItem.objects.filter(cart=cart, item=item).first()
        if existing_cart_item:
            total_single_equivalent += existing_cart_item.quantity

        # Calculate total available stock and remaining stock
        total_available_stock = item.quantity_on_hand
        remaining_stock = total_available_stock - total_single_equivalent

        # Handle stock validation
        if remaining_stock <= 0:
            response = {
                'success': False,
                'message': 'No items are available to add. The cart already exceeds available stock.'
            }
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response)
            else:
                messages.error(request, response['message'])
                return redirect('ecommerce:item_detail', item_id=item_id)

        # Convert the requested quantity to single-equivalent based on the item_type
        if item_type == 'box' and item.has_box_option:
            requested_single_equivalent = requested_quantity * item.box_quantity
        elif item_type == 'bag' and item.has_bag_option:
            requested_single_equivalent = requested_quantity * item.bag_quantity
        else:
            requested_single_equivalent = requested_quantity

        # Ensure the total requested single-equivalent quantity does not exceed remaining stock
        if requested_single_equivalent > remaining_stock:
            response = {
                'success': False,
                'message': f'Only {remaining_stock} single-equivalent items are available in stock. Please reduce your quantity.'
            }
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response)
            else:
                messages.error(request, response['message'])
                return redirect('ecommerce:item_detail', item_id=item_id)

        # Proceed to add or update items in the cart based on the item_type
        if item_type == 'box' and item.has_box_option:
            box_item = Item.objects.filter(manufacturer_sku=f"{item.system_sku}-Box-{item.box_quantity}").first()
            if box_item:
                box_cart_item, created = CartItem.objects.get_or_create(cart=cart, item=box_item)
                box_cart_item.quantity = box_cart_item.quantity + requested_quantity if not created else requested_quantity
                box_cart_item.price = get_discounted_price(box_item, request.user)
                box_cart_item.save()
        elif item_type == 'bag' and item.has_bag_option:
            bag_item = Item.objects.filter(manufacturer_sku=f"{item.system_sku}-Bag-{item.bag_quantity}").first()
            if bag_item:
                bag_cart_item, created = CartItem.objects.get_or_create(cart=cart, item=bag_item)
                bag_cart_item.quantity = bag_cart_item.quantity + requested_quantity if not created else requested_quantity
                bag_cart_item.price = get_discounted_price(bag_item, request.user)
                bag_cart_item.save()
        elif item_type == 'single':
            if existing_cart_item:
                existing_cart_item.quantity += requested_quantity
                existing_cart_item.save()
            else:
                CartItem.objects.create(
                    cart=cart,
                    item=item,
                    quantity=requested_quantity,
                    price=get_discounted_price(item, request.user)
                )
        else:
            response = {
                'success': False,
                'message': 'Invalid item type selected.'
            }
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response)
            else:
                messages.error(request, response['message'])
                return redirect('ecommerce:item_detail', item_id=item_id)

        # Success response
        response = {
            'success': True,
            'message': f'Added {requested_quantity} of {item.description} to the cart.'
        }
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(response)
        else:
            messages.success(request, response['message'])
            return redirect('ecommerce:item_detail', item_id=item_id)

    return render(request, 'ecommerce/add_to_cart.html', {'item': item})





from decimal import Decimal, ROUND_HALF_UP

from decimal import Decimal, ROUND_HALF_UP

from decimal import Decimal, ROUND_HALF_UP

from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

from django.shortcuts import redirect


from django.shortcuts import redirect

@login_required
def cart_detail(request):
    try:
        # Try to retrieve the cart for the authenticated user that is not completed
        cart = Cart.objects.get(customer=request.user, completed=False)
        cart_items = cart.cartitem_set.all()

        if request.method == 'POST':
            # Iterate through POST data to handle quantity updates
            for key, value in request.POST.items():
                if key.startswith('quantity_'):
                    cart_item_id = int(key.split('_')[1])
                    quantity = int(value)

                    # Get the CartItem instance
                    cart_item = cart.cartitem_set.get(id=cart_item_id)

                    if quantity > 0:
                        # Update quantity if greater than zero
                        cart_item.quantity = quantity
                        cart_item.save()
                    else:
                        # Remove item if quantity is zero
                        cart_item.delete()

            # Redirect to the cart to see the updated items
            return redirect('ecommerce:cart_detail')

        if not cart_items:
            # If the cart exists but there are no items, redirect to the item list
            return redirect('ecommerce:item_list')

    except Cart.DoesNotExist:
        # If no cart exists, redirect to the item list
        return redirect('ecommerce:item_list')

    total_price = Decimal(0)
    total_discount = Decimal(0)
    total_single_equivalent = 0  # To track the total single-equivalent units in the cart
    parent_item_totals = defaultdict(int)

    print("\n--- CART DETAILS ---")

    for cart_item in cart_items:
        original_price = cart_item.item.price_default  # Assuming `price_default` exists
        discount_price = cart_item.price
        quantity = cart_item.quantity

        total_price += discount_price * quantity
        if discount_price < original_price:
            total_discount += (original_price - discount_price) * quantity

        item = cart_item.item
        parent_item = item.parent_item if item.parent_item else item

        # Handle box items
        if 'Box' in item.manufacturer_sku and parent_item.box_quantity:
            box_quantity = parent_item.box_quantity
            single_equivalent = box_quantity * quantity
            parent_item_totals[parent_item.manufacturer_sku] += single_equivalent
            print(f"Box: {item.manufacturer_sku}, Quantity: {quantity}, Single Equivalent: {single_equivalent}")

        # Handle bag items
        elif 'Bag' in item.manufacturer_sku and parent_item.bag_quantity:
            bag_quantity = parent_item.bag_quantity
            single_equivalent = bag_quantity * quantity
            parent_item_totals[parent_item.manufacturer_sku] += single_equivalent
            print(f"Bag: {item.manufacturer_sku}, Quantity: {quantity}, Single Equivalent: {single_equivalent}")

        # Handle single items
        else:
            parent_item_totals[parent_item.manufacturer_sku] += quantity
            print(f"Single: {item.manufacturer_sku}, Quantity: {quantity}")

    print(f"Total single-equivalent items in cart: {total_single_equivalent}")

    hst_rate = Decimal('0.13')
    hst = (total_price * hst_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_price_with_hst = (total_price + hst).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'total_discount': total_discount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'hst': hst,
        'total_price_with_hst': total_price_with_hst,
        'form_errors': {},  # Assuming form errors to be empty for the initial load
    }

    return render(request, 'ecommerce/cart_detail.html', context)



import logging

logger = logging.getLogger(__name__)


@login_required
def remove_from_cart(request, cart_item_id):
    logger.info(f"Attempting to remove CartItem ID: {cart_item_id}")

    try:
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__customer=request.user)
        logger.info(f"Found CartItem: {cart_item}")

        cart = cart_item.cart
        cart_item.delete()
        logger.info(f"Deleted CartItem ID: {cart_item_id}")

        # Check if the cart is empty after removing the item
        if not cart.cartitem_set.exists():
            logger.info(f"Cart ID {cart.id} is now empty but will be kept.")
            # You can add any logic here if you want to initialize or update the cart in some way

    except Exception as e:
        logger.error(f"Error removing CartItem ID {cart_item_id}: {e}")

    return redirect('ecommerce:cart_detail')


from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, DecimalField
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


@login_required
def update_cart_items(request):
    cart = get_object_or_404(Cart, customer=request.user, completed=False)

    if request.method == 'POST':
        form_errors = {}

        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                try:
                    cart_item_id = int(key.split('_')[1])
                    requested_quantity = int(value)
                    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)

                    # Check if quantity is zero or negative to delete the item
                    if requested_quantity <= 0:
                        cart_item.delete()  # Remove item from cart
                    elif requested_quantity > cart_item.item.quantity_on_hand:
                        form_errors[key] = (
                            f"Cannot exceed {cart_item.item.quantity_on_hand} in stock."
                        )
                    else:
                        cart_item.quantity = requested_quantity
                        cart_item.price = get_discounted_price(cart_item.item, request.user)
                        cart_item.save()
                except (ValueError, CartItem.DoesNotExist):
                    form_errors[key] = "Invalid input or item not found."

        # Calculate updated totals after processing form
        total_price = cart.cartitem_set.aggregate(
            total=Sum(F('quantity') * F('price'), output_field=DecimalField())
        )['total'] or Decimal('0')

        total_discount = cart.cartitem_set.aggregate(
            discount=Sum((F('item__price_default') - F('price')) * F('quantity'), output_field=DecimalField())
        )['discount'] or Decimal('0')

        hst = (total_price * Decimal('0.13')).quantize(Decimal('0.01'))
        total_price_with_hst = (total_price + hst).quantize(Decimal('0.01'))

        # Handle form errors, if any
        if form_errors:
            context = {
                'cart': cart,
                'cart_items': cart.cartitem_set.all(),
                'total_price': total_price,
                'total_discount': total_discount,
                'hst': hst,
                'total_price_with_hst': total_price_with_hst,
                'form_errors': form_errors,
            }
            return render(request, 'ecommerce/cart_detail.html', context)

        # If all items are removed, delete the cart or redirect to an empty cart page
        if not cart.cartitem_set.exists():
            cart.delete()
            return redirect('ecommerce:item_list')

        # Redirect to the cart detail page with updated data
        return redirect('ecommerce:cart_detail')

    return HttpResponseBadRequest('Invalid request method')





def generate_order_number():
    return str(uuid.uuid4().hex)


from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP
from .models import Cart, Order
from .forms import OrderForm

from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Cart, Order
from .forms import OrderForm
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib import messages
from ecommerce.models import Cart, Order, OrderItem
from ecommerce.forms import OrderForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
from django.utils import timezone
from django.http import HttpResponse
from threading import Timer
import requests
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cart, Item, Order, OrderItem
from .forms import OrderForm
from decimal import Decimal
from django.utils import timezone

SHIPSTATION_API_URL = "https://ssapi.shipstation.com/shipments/getrates"
SHIPSTATION_USERNAME = "b2806668fbd74c789adf93edf98cda43"
SHIPSTATION_PASSWORD = "428f6402bbfb40f3afcbf6f06e4f0840"
import threading

# Store stock reductions in a global dictionary to restore them if checkout is not completed
checkout_reservations = {}
# Set up logging
logger = logging.getLogger(__name__)
flag = None


from django.shortcuts import redirect

from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import redirect

from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import redirect

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from decimal import Decimal
import requests
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
import requests

# Define available box sizes and their limits
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
import requests

UPS_ESTIMATED_DELIVERY_TIMES = {
    "ups_next_day_air": "Next business day by 10:30 a.m., 12:00 p.m., or end of day.",
    "ups_worldwide_expedited": "2-5 business days for international shipments.",
    "ups_standard": "Day-definite delivery within 1-5 business days, depending on distance.",
    "ups_next_day_air_saver": "Next business day by 3:00 p.m. or 4:30 p.m. for commercial destinations.",
    "ups_next_day_air_early_am": "Next business day early morning delivery, as early as 8:00 a.m."
}

# Define available box sizes and their limits
BOXES = [
    {"type": "Small", "dimensions": {"length": 10, "width": 10, "height": 10}, "weight_limit": 5},
    {"type": "Medium", "dimensions": {"length": 15, "width": 15, "height": 15}, "weight_limit": 10},
    {"type": "Large", "dimensions": {"length": 20, "width": 20, "height": 20}, "weight_limit": 20},
    {"type": "Extra Large", "dimensions": {"length": 25, "width": 25, "height": 25}, "weight_limit": 30}
]



# 1. Function to pack items into boxes
def pack_items_in_boxes(items, boxes):
    packed_boxes = []
    leftover_items = []

    for item in items:
        item_length = item['dimensions'].get('length') or 0  # Default to 0 if None
        item_width = item['dimensions'].get('width') or 0  # Default to 0 if None
        item_height = item['dimensions'].get('height') or 0  # Default to 0 if None
        item_weight = item['weight']

        # Find a suitable box for the item based on dimensions and weight
        for box in boxes:
            box_length = box['dimensions']['length']
            box_width = box['dimensions']['width']
            box_height = box['dimensions']['height']
            box_weight_limit = box.get('weight_limit', float('inf'))  # Default to infinity if weight limit is missing

            if (item_length <= box_length and
                    item_width <= box_width and
                    item_height <= box_height and
                    item_weight <= box_weight_limit):
                # Add the item to the packed box list
                packed_boxes.append({
                    "box_type": box['type'],
                    "item": item,
                    "box_dimensions": box['dimensions'],
                    "box_weight_limit": box_weight_limit,
                    "total_weight": item_weight  # Include total_weight in each packed box
                })
                print(f"Selected box: {box['type']} for item: {item['name']}")  # Print selected box for debugging
                break
        else:
            # If no suitable box was found, add the item to leftovers
            leftover_items.append(item)

    return packed_boxes, leftover_items


# 2. Function to prepare the shipping request with multiple packages
def prepare_shipping_request_with_packages(packed_boxes, carrier, postal_code, country_code):
    total_weight = sum(box["total_weight"] for box in packed_boxes)
    packages = [
        {
            "weight": {"value": float(box["total_weight"]), "units": "pounds"},
            "dimensions": {
                "units": "inches",
                "length": float(box["box_dimensions"]["length"]),
                "width": float(box["box_dimensions"]["width"]),
                "height": float(box["box_dimensions"]["height"])
            }
        }
        for box in packed_boxes
    ]

    payload = {
        "carrierCode": carrier,
        "serviceCode": None,
        "packageCode": None,
        "fromPostalCode": "L4B1J9",  # Replace with your postal code
        "fromCountry": "CA",
        "toPostalCode": postal_code,
        "toCountry": country_code,
        "confirmation": "delivery",
        "residential": True,
        "weight": {"value": float(total_weight), "units": "pounds"},  # Global weight
        "packages": packages  # Package details
    }
    return payload


# 3. Function to fetch shipping rates using the single payload with multiple packages
def fetch_shipping_rates(payload):
    response = requests.post(
        SHIPSTATION_API_URL,
        json=payload,
        auth=(SHIPSTATION_USERNAME, SHIPSTATION_PASSWORD),
        headers={"Content-Type": "application/json"}
    )

    print("API Status Code:", response.status_code)
    print("API Response Text:", response.text)

    shipping_rates = []
    if response.status_code == 200:
        rates = response.json()
        for rate in rates:
            estimated_delivery = UPS_ESTIMATED_DELIVERY_TIMES.get(rate["serviceCode"], "Not Available")

            shipping_rates.append({
                "serviceName": rate["serviceName"],
                "serviceCode": rate["serviceCode"],
                "shipmentCost": rate["shipmentCost"],
                "otherCost": rate["otherCost"],
                "estimatedDelivery": estimated_delivery,

            })
    else:
        print("Failed to fetch shipping rates.")
    return shipping_rates


# Main function to handle the shipping rate request
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from django.contrib.auth.decorators import login_required


import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Configure a logger for this module
logger = logging.getLogger(__name__)

@login_required
def get_shipping_rate(request):
    global flag
    flag = 0
    logger.info("Entered get_shipping_rate view.")

    if request.method == 'POST' and 'get_shipping_rate' in request.POST:
        # Retrieve form data and log the input
        delivery_option = request.POST.get('delivery_option')
        carrier = request.POST.get('carrier', '')
        postal_code = request.POST.get('postal_code', '')
        country_name = request.POST.get('country', '')

        # Save shipping data in session and log it
        shipping_data = {
            'carrier': carrier,
            'street': request.POST.get('street', ''),
            'city': request.POST.get('city', ''),
            'province': request.POST.get('province', ''),
            'postal_code': postal_code,
            'country': country_name,
            'delivery_option': delivery_option
        }
        request.session['shipping_data'] = shipping_data
        logger.info("Stored shipping_data in session: %s", shipping_data)

        # If "Pickup" option is selected, skip API call and set shipping cost to zero
        if delivery_option == "pickup":
            request.session['shipping_cost'] = '0'
            request.session['shipping_service_name'] = ''
            request.session['shipping_rates'] = []  # No rates needed for pickup
            request.session['show_shipping_rates'] = False
            logger.info("Pickup selected. Set shipping_cost=0, shipping_service_name='' and empty shipping_rates.")
            messages.success(request, "Pickup selected. No shipping rates required.")
            return redirect('ecommerce:before_payment')

        # Fetch the cart and its items, and log the details
        cart = get_object_or_404(Cart, customer=request.user, completed=False)
        cart_items = cart.cartitem_set.all()
        logger.info("Cart items: %s", cart_items)

        # Prepare items for packing
        items = [
            {
                "name": item.item.description,
                "weight": item.item.weight * item.quantity,
                "dimensions": {
                    "length": item.item.length,
                    "width": item.item.width,
                    "height": item.item.height
                },
                "quantity": item.quantity
            }
            for item in cart_items
        ]
        logger.info("Prepared items for packing: %s", items)

        # Pack items into boxes
        packed_boxes, leftover_items = pack_items_in_boxes(items, BOXES)
        if leftover_items:
            logger.error("Leftover items encountered during packing: %s", leftover_items)
            messages.error(request, "Some items couldn't fit in any box size available.")
            return redirect('ecommerce:cart_detail')

        # Map full country name to ISO code
        country_codes = {"Canada": "CA", "United States": "US"}
        country_code = country_codes.get(country_name, "CA")
        logger.info("Using country code: %s", country_code)

        # Prepare payload and fetch shipping rates
        shipping_request_payload = prepare_shipping_request_with_packages(packed_boxes, carrier, postal_code, country_code)
        logger.info("Shipping request payload: %s", shipping_request_payload)
        shipping_rates = fetch_shipping_rates(shipping_request_payload)
        logger.info("Fetched shipping rates: %s", shipping_rates)

        # Store the fetched rates in the session and log the update
        request.session['shipping_rates'] = shipping_rates
        request.session['show_shipping_rates'] = True
        logger.info("Updated session with shipping_rates and set show_shipping_rates to True.")

        messages.success(request, "Shipping rates fetched successfully.")
        return render(request, 'ecommerce/get_shipping.html', {
            'shipping_rates': shipping_rates,
            'show_shipping_rates': True
        })

    # For GET requests, retrieve any saved delivery option from session and log it
    saved_delivery_option = request.session.get('shipping_data', {}).get('delivery_option', '')
    logger.info("GET request in get_shipping_rate view. Saved delivery option: %s", saved_delivery_option)
    return render(request, 'ecommerce/get_shipping.html', {
        'saved_delivery_option': saved_delivery_option
    })



CHECKOUT_TIMEOUT = 200  # 5 minutes timeout

@login_required
def checkout(request):
    remaining_time = get_remaining_time(request, CHECKOUT_TIMEOUT)

    if remaining_time <= 0:
        messages.error(request, "Your checkout session has timed out. Please try again.")
        return redirect('ecommerce:cart_detail')

    print("Starting checkout process")
    cart = get_object_or_404(Cart, customer=request.user, completed=False)
    cart_items = cart.cartitem_set.all()
    print("Cart items:", cart_items)

    # Calculate subtotal, total discount, HST, and total price with HST
    subtotal = sum(item.price * item.quantity for item in cart_items).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_discount = sum((item.item.price_default - item.price) * item.quantity for item in cart_items).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP)
    hst_rate = Decimal('0.13')
    hst = (subtotal * hst_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_with_hst = (subtotal + hst).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    print(f"Calculated totals: Subtotal={subtotal}, Total Discount={total_discount}, HST={hst}, Total with HST={total_with_hst}")

    # Retrieve shipping rates and cost
    # Use defaultdict to track total quantities by parent item
    parent_item_totals = defaultdict(int)
    reduced_stock = {}

    # Check if the stock has already been reduced for this session
    if f'checkout_{cart.id}' not in checkout_reservations:
        print("\n--- CHECKOUT STARTED ---")
        print(f"Customer: {request.user}")
        print(f"Subtotal: {subtotal}, Total Discount: {total_discount}, HST: {hst}, Total with HST: {total_with_hst}")
        reset_checkout_session(request)  # Reset session for a fresh checkout

        # Consolidate quantities for each parent item and show how much will be reduced
        for cart_item in cart_items:
            item = cart_item.item
            parent_item = item.parent_item if item.parent_item else item

            print(f"Processing item: {item.system_sku} - {item.description}")

            # Handle box items
            if 'Box' in item.manufacturer_sku and parent_item.box_quantity:
                box_quantity = parent_item.box_quantity
                single_equivalent = box_quantity * cart_item.quantity
                parent_item_totals[parent_item.manufacturer_sku] += single_equivalent
                print(f"Box: {item.manufacturer_sku}, Quantity: {cart_item.quantity}, Single Equivalent: {single_equivalent}")

            # Handle bag items
            elif 'Bag' in item.manufacturer_sku and parent_item.bag_quantity:
                bag_quantity = parent_item.bag_quantity
                single_equivalent = bag_quantity * cart_item.quantity
                parent_item_totals[parent_item.manufacturer_sku] += single_equivalent
                print(f"Bag: {item.manufacturer_sku}, Quantity: {cart_item.quantity}, Single Equivalent: {single_equivalent}")

            # Handle single items
            else:
                parent_item_totals[parent_item.manufacturer_sku] += cart_item.quantity
                print(f"Single: {item.manufacturer_sku}, Quantity: {cart_item.quantity}")

        print(f"\n--- CONSOLIDATED ITEMS BY PARENT ---")
        for parent_sku, total_quantity in parent_item_totals.items():
            print(f"Parent SKU: {parent_sku}, Total Quantity: {total_quantity}")

        print(f"Total single-equivalent items in cart: {sum(parent_item_totals.values())}")

        # Perform stock reduction at the beginning of the checkout process
        for parent_sku, total_quantity in parent_item_totals.items():
            item = get_object_or_404(Item, manufacturer_sku=parent_sku)
            print(f"\n--- STOCK REDUCTION FOR ITEM {item.system_sku} ---")
            print(f"Current stock: {item.quantity_on_hand}, Reducing by: {total_quantity}")

            if item.quantity_on_hand < total_quantity:
                messages.error(request,
                               f"Insufficient stock for item {item.description}. Only {item.quantity_on_hand} available.")
                print(f"Stock insufficient for {item.system_sku}. Available: {item.quantity_on_hand}, Required: {total_quantity}")
                return redirect('ecommerce:cart_detail')

            # Reduce stock and store the reduction
            item.quantity_on_hand -= total_quantity
            item.save()
            reduced_stock[item.system_sku] = total_quantity
            print(f"New stock after reduction: {item.quantity_on_hand}")

        # Store stock reductions in the global checkout_reservations dictionary
        checkout_reservations[f'checkout_{cart.id}'] = reduced_stock
        return redirect('ecommerce:checkout')

    ####### ADDITIONAL CODE: UPDATE RESERVATION IF USER ADDED NEW ITEMS #######

    # Check for new or modified items in cart
    reserved_stock = checkout_reservations.get(f'checkout_{cart.id}', {})
    new_reservations = {}

    for cart_item in cart_items:
        item = cart_item.item
        parent_item = item.parent_item if item.parent_item else item

        reserved_quantity = reserved_stock.get(parent_item.system_sku, 0)
        current_needed = cart_item.quantity

        if current_needed > reserved_quantity:
            # Additional stock needs to be reserved
            additional_needed = current_needed - reserved_quantity
            if parent_item.quantity_on_hand < additional_needed:
                messages.error(request, f"Not enough stock for {parent_item.description}. Available: {parent_item.quantity_on_hand}.")
                return redirect('ecommerce:cart_detail')

            parent_item.quantity_on_hand -= additional_needed
            parent_item.save()
            new_reservations[parent_item.system_sku] = additional_needed

    # Update global checkout reservations with new stock adjustments
    checkout_reservations[f'checkout_{cart.id}'] = {**reserved_stock, **new_reservations}

    ####### END OF ADDITIONAL CODE #######

    # Define the timeout behavior for restoring stock
    def restore_stock_if_not_completed(cart_id, reduced_stock):
        print("\n--- CHECKOUT TIMEOUT ---")
        try:
            cart = Cart.objects.get(id=cart_id, completed=False)
            if not cart.completed:
                print(f"Restoring stock for abandoned cart {cart.id}.")
                for sku, quantity in reduced_stock.items():
                    try:
                        item = get_object_or_404(Item, system_sku=sku)
                        item.quantity_on_hand += quantity  # Restore the stock
                        item.save()
                        print(f"Restored {quantity} units for item {sku}.")
                    except Item.DoesNotExist:
                        print(f"Item with SKU {sku} does not exist. Cannot restore stock.")
                cart.completed = False  # Mark the cart as not completed
                cart.save()

                # Clean up the reservation to avoid conflict
                if f'checkout_{cart_id}' in checkout_reservations:
                    del checkout_reservations[f'checkout_{cart_id}']
                print(f"Stock restored and reservation removed for cart {cart_id}.")

                # Since we cannot redirect from a separate thread, we log the timeout
                print("Checkout timed out. Stock has been restored.")
        except Cart.DoesNotExist:
            print(f"Cart {cart_id} does not exist or is already completed. No stock to restore.")

    # Start a timer to cancel the checkout after timeout if not completed
    timeout_timer = threading.Timer(CHECKOUT_TIMEOUT, restore_stock_if_not_completed,
                                    args=(cart.id, checkout_reservations.get(f'checkout_{cart.id}', {})))
    timeout_timer.start()

    context = {
        'cart': cart,
        'subtotal': subtotal,
        'total_discount': total_discount,
        'hst': hst,
        'total_with_hst': total_with_hst,
        'cart_items': cart_items,
        'timeout': CHECKOUT_TIMEOUT,
        'remaining_time': remaining_time,
    }
    return render(request, 'ecommerce/checkout.html', context)



@login_required
def confirm_shipping_method(request):
    remaining_time = get_remaining_time(request, CHECKOUT_TIMEOUT)

    if remaining_time <= 0:
        messages.error(request, "Your checkout session has timed out. Please try again.")
        return redirect('ecommerce:cart_detail')
    context = {
        'remaining_time': remaining_time,
        # [Other context variables]
    }
    return render(request, 'ecommerce/confirm_shipping_method.html',context)


from django.shortcuts import render, redirect
from decimal import Decimal
from django.contrib.auth.decorators import login_required


from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required

import logging
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

# Configure logger for this module
logger = logging.getLogger(__name__)

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import logging

# Configure a logger for this module
logger = logging.getLogger(__name__)

@login_required
def before_payment(request):
    remaining_time = get_remaining_time(request, CHECKOUT_TIMEOUT)

    if remaining_time <= 0:
        messages.error(request, "Your checkout session has timed out. Please try again.")
        return redirect('ecommerce:cart_detail')
    logger.info("Starting checkout process in before_payment view.")

    # Fetch the user's cart and cart items
    cart = get_object_or_404(Cart, customer=request.user, completed=False)
    cart_items = cart.cartitem_set.all()
    logger.info("Cart items: %s", cart_items)

    # Calculate subtotal, total discount, HST, and total price with HST
    subtotal = sum(item.price * item.quantity for item in cart_items).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_discount = sum((item.item.price_default - item.price) * item.quantity for item in cart_items).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP)
    hst_rate = Decimal('0.13')
    hst = (subtotal * hst_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_with_hst = (subtotal + hst).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    logger.info("Calculated totals: Subtotal=%s, Total Discount=%s, HST=%s, Total with HST=%s",
                subtotal, total_discount, hst, total_with_hst)

    # Retrieve shipping data from session
    shipping_data = request.session.get('shipping_data', {})
    logger.info("Initial shipping_data from session: %s", shipping_data)
    if shipping_data.get('delivery_option') == 'pickup':
        shipping_cost = Decimal('0.00')
    else:
        shipping_cost = Decimal(request.session.get('shipping_cost', '0'))
    logger.info("Initial shipping_cost from session: %s", shipping_cost)

    # Recalculate the total with HST and shipping
    total_with_hst_and_shipping = (total_with_hst + shipping_cost).quantize(Decimal('0.01'))

    # Check if shipping selection form was submitted and update shipping data
    if request.method == 'POST' and 'manual_shipping_cost' in request.POST:
        raw_shipping_cost = request.POST.get('manual_shipping_cost')
        shipping_service_name = request.POST.get('shipping_service_name')
        logger.info("POST data received: manual_shipping_cost=%s, shipping_service_name=%s",
                    raw_shipping_cost, shipping_service_name)

        if raw_shipping_cost:
            # Remove any dollar signs or extra whitespace
            cleaned_cost = raw_shipping_cost.replace('$', '').strip()
            try:
                shipping_cost = Decimal(cleaned_cost)
                request.session['shipping_cost'] = str(shipping_cost)
                request.session['shipping_service_name'] = shipping_service_name
                logger.info("Updated session: shipping_cost=%s, shipping_service_name=%s", shipping_cost, shipping_service_name)
                messages.success(request,
                                 f"Shipping cost updated to ${shipping_cost} with service {shipping_service_name}.")
            except InvalidOperation:
                messages.error(request, "Invalid shipping cost entered.")
                logger.error("Invalid shipping cost entered: %s", raw_shipping_cost)
                return redirect('ecommerce:before_payment')
            # Recalculate total with the new shipping cost
            total_with_hst_and_shipping = (total_with_hst + shipping_cost).quantize(Decimal('0.01'))
        else:
            logger.warning("No manual_shipping_cost provided in POST.")

    logger.info("Final session data: shipping_cost=%s, shipping_service_name=%s",
                request.session.get('shipping_cost'), request.session.get('shipping_service_name'))
    logger.info("Final total_with_hst_and_shipping: %s", total_with_hst_and_shipping)

    # Prepare context for the template
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'total_discount': total_discount,
        'hst': hst,
        'total_with_hst': total_with_hst,
        'cart_items': cart_items,
        'shipping_cost': shipping_cost,
        'total_with_hst_and_shipping': total_with_hst_and_shipping,
        'shipping_service_name': request.session.get('shipping_service_name', ''),
        'delivery_option': shipping_data.get('delivery_option', ''),
        'remaining_time': remaining_time,
    }

    return render(request, 'ecommerce/before_payment.html', context)







def get_remaining_time(request, timeout_seconds):
    checkout_start_time = request.session.get('checkout_start_time')
    if not checkout_start_time:
        # Set the start time if it doesn't exist
        request.session['checkout_start_time'] = timezone.now().isoformat()
        return timeout_seconds
    else:
        # Calculate remaining time
        checkout_start_time = timezone.datetime.fromisoformat(checkout_start_time)
        elapsed_time = (timezone.now() - checkout_start_time).total_seconds()
        remaining_time = max(0, timeout_seconds - elapsed_time)

        # If time has expired, clear the session and return 0
        if remaining_time <= 0:
            reset_checkout_session(request)
            return 0
        return remaining_time



# @login_required
# def checkout(request):
#     checkout_start_time = request.session.get('checkout_start_time')
#
#     if checkout_start_time:
#         # Convert the stored string timestamp back to a datetime object
#         checkout_start_time = timezone.datetime.fromisoformat(checkout_start_time)
#         elapsed_time = (timezone.now() - checkout_start_time).total_seconds()
#         remaining_time = max(0, CHECKOUT_TIMEOUT - elapsed_time)
#
#         # If timeout has expired, cancel the checkout and redirect to the cart
#         if remaining_time <= 0:
#             cancel_checkout(request.user.id)  # Restore stock if needed
#             reset_checkout_session(request)  # Clear session data
#             messages.error(request, "Your checkout session has timed out. Please try again.")
#             return redirect('ecommerce:cart_detail')  # Redirect to the cart page
#     else:
#         # If there's no start time, set the current time as the start time
#         request.session['checkout_start_time'] = timezone.now().isoformat()
#         remaining_time = CHECKOUT_TIMEOUT
#
#
#
#     print("Starting checkout process")
#     payment_success = request.session.get('payment_success', False)
#     cart = get_object_or_404(Cart, customer=request.user, completed=False)
#     cart_items = cart.cartitem_set.all()
#     print("Cart items:", cart_items)
#     # Calculate subtotal, total discount, HST, and total price with HST
#     subtotal = sum(item.price * item.quantity for item in cart_items).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
#     total_discount = sum((item.item.price_default - item.price) * item.quantity for item in cart_items).quantize(
#         Decimal('0.01'), rounding=ROUND_HALF_UP)
#     hst_rate = Decimal('0.13')
#     hst = (subtotal * hst_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
#     total_with_hst = (subtotal + hst).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
#     print(f"Calculated totals: Subtotal={subtotal}, Total Discount={total_discount}, HST={hst}, Total with HST={total_with_hst}")
#
#     # Retrieve shipping rates and cost
#     shipping_rates = request.session.get('shipping_rates', [])
#     show_shipping_rates = request.session.get('show_shipping_rates', False)
#     shipping_cost = Decimal(request.session.get('shipping_cost', '0'))
#     shipping_data = request.session.get('shipping_data', {})
#     print("Shipping data:", shipping_data, "Shipping cost:", shipping_cost)
#
#     # Check if user submitted a manual shipping cost
#     if request.method == 'POST' and 'x' in request.POST:
#         manual_shipping_cost = request.POST.get('manual_shipping_cost')
#         shipping_service_name = request.POST.get('shipping_service_name')  # Retrieve the service name
#
#         if manual_shipping_cost:
#             try:
#                 shipping_cost = Decimal(manual_shipping_cost)
#                 request.session['shipping_cost'] = str(shipping_cost)  # Store as string in session
#                 request.session['shipping_service_name'] = shipping_service_name  # Store service name in session
#                 messages.success(request,
#                                  f"Shipping cost updated to ${shipping_cost} with service {shipping_service_name}.")
#             except InvalidOperation:
#                 messages.error(request, "Invalid shipping cost entered.")
#
#     total_with_hst_and_shipping = total_with_hst + shipping_cost
#     request.session['total_with_hst_and_shipping'] = str(total_with_hst_and_shipping)  # Save in session as string
#     print(f"Total with HST + Shipping: {total_with_hst_and_shipping}")
#     shipping_service_name = request.session.get('shipping_service_name', '')
#
#     print('flaaaag', flag)
#     if flag == 0:
#         print('ruuuun')
#         shipping_cost = 0
#
#     print(total_with_hst)
#     print(shipping_cost)
#
#
#
#     # Use defaultdict to track total quantities by parent item
#     parent_item_totals = defaultdict(int)
#     reduced_stock = {}
#
#     # Check if the stock has already been reduced for this session
#     if f'checkout_{cart.id}' not in checkout_reservations:
#         print("\n--- CHECKOUT STARTED ---")
#         print(f"Customer: {request.user}")
#         print(f"Subtotal: {subtotal}, Total Discount: {total_discount}, HST: {hst}, Total with HST: {total_with_hst}")
#         reset_checkout_session(request)  # Reset session for a fresh checkout
#
#         # Consolidate quantities for each parent item and show how much will be reduced
#         for cart_item in cart_items:
#             item = cart_item.item
#             parent_item = item.parent_item if item.parent_item else item
#
#             print(f"Processing item: {item.system_sku} - {item.description}")
#
#             # Handle box items
#             if 'Box' in item.manufacturer_sku and parent_item.box_quantity:
#                 box_quantity = parent_item.box_quantity
#                 single_equivalent = box_quantity * cart_item.quantity
#                 parent_item_totals[parent_item.manufacturer_sku] += single_equivalent
#                 print(
#                     f"Box: {item.manufacturer_sku}, Quantity: {cart_item.quantity}, Single Equivalent: {single_equivalent}")
#
#             # Handle bag items
#             elif 'Bag' in item.manufacturer_sku and parent_item.bag_quantity:
#                 bag_quantity = parent_item.bag_quantity
#                 single_equivalent = bag_quantity * cart_item.quantity
#                 parent_item_totals[parent_item.manufacturer_sku] += single_equivalent
#                 print(
#                     f"Bag: {item.manufacturer_sku}, Quantity: {cart_item.quantity}, Single Equivalent: {single_equivalent}")
#
#             # Handle single items
#             else:
#                 parent_item_totals[parent_item.manufacturer_sku] += cart_item.quantity
#                 print(f"Single: {item.manufacturer_sku}, Quantity: {cart_item.quantity}")
#
#         print(f"\n--- CONSOLIDATED ITEMS BY PARENT ---")
#         for parent_sku, total_quantity in parent_item_totals.items():
#             print(f"Parent SKU: {parent_sku}, Total Quantity: {total_quantity}")
#
#         print(f"Total single-equivalent items in cart: {sum(parent_item_totals.values())}")
#
#         # Perform stock reduction at the beginning of the checkout process
#         for parent_sku, total_quantity in parent_item_totals.items():
#             item = get_object_or_404(Item, manufacturer_sku=parent_sku)
#             print(f"\n--- STOCK REDUCTION FOR ITEM {item.system_sku} ---")
#             print(f"Current stock: {item.quantity_on_hand}, Reducing by: {total_quantity}")
#
#             if item.quantity_on_hand < total_quantity:
#                 messages.error(request,
#                                f"Insufficient stock for item {item.description}. Only {item.quantity_on_hand} available.")
#                 print(
#                     f"Stock insufficient for {item.system_sku}. Available: {item.quantity_on_hand}, Required: {total_quantity}")
#                 return redirect('ecommerce:cart_detail')
#
#             # Reduce stock and store the reduction
#             item.quantity_on_hand -= total_quantity
#             item.save()
#             reduced_stock[item.system_sku] = total_quantity
#             print(f"New stock after reduction: {item.quantity_on_hand}")
#
#         # Store stock reductions in the global checkout_reservations dictionary
#         checkout_reservations[f'checkout_{cart.id}'] = reduced_stock
#         return redirect('ecommerce:checkout')
#
#     print('1111111111111111111')
#
#     # Define the timeout behavior for restoring stock
#     def restore_stock_if_not_completed(cart_id, reduced_stock):
#         print("\n--- CHECKOUT TIMEOUT ---")
#         try:
#             cart = Cart.objects.get(id=cart_id, completed=False)
#             if not cart.completed:
#                 print(f"Restoring stock for abandoned cart {cart.id}.")
#                 for sku, quantity in reduced_stock.items():
#                     try:
#                         item = get_object_or_404(Item, system_sku=sku)
#                         item.quantity_on_hand += quantity  # Restore the stock
#                         item.save()
#                         print(f"Restored {quantity} units for item {sku}.")
#                     except Item.DoesNotExist:
#                         print(f"Item with SKU {sku} does not exist. Cannot restore stock.")
#                 cart.completed = False  # Mark the cart as not completed
#                 cart.save()
#
#                 # Clean up the reservation to avoid conflict
#                 if f'checkout_{cart_id}' in checkout_reservations:
#                     del checkout_reservations[f'checkout_{cart_id}']
#                 print(f"Stock restored and reservation removed for cart {cart_id}.")
#
#                 # Since we cannot redirect from a separate thread, we log the timeout
#                 print("Checkout timed out. Stock has been restored.")
#         except Cart.DoesNotExist:
#             print(f"Cart {cart_id} does not exist or is already completed. No stock to restore.")
#
#     # Start a timer to cancel the checkout after timeout if not completed
#     timeout_timer = threading.Timer(CHECKOUT_TIMEOUT, restore_stock_if_not_completed,
#                                     args=(cart.id, checkout_reservations.get(f'checkout_{cart.id}', {})))
#     timeout_timer.start()
#     print('222222222222222222222222')
#     print("kir to kon", cart)
#     # Check if the request is POST to complete the order
#     if request.method == 'POST':
#         if not payment_success:
#             messages.error(request, "Please complete your payment with PayPal before placing your order.")
#             return redirect('ecommerce:checkout')  # Prevents further order processing without payment confirmation
#
#         timeout_timer.cancel()  # Cancel the timer as the checkout is proceeding
#         print(f"Checkout timer with ID {timeout_timer.ident} canceled")
#
#         # Log POST data for debugging
#         print("\n--- CHECKOUT POST DATA ---")
#         for key, value in request.POST.items():
#             print(f"{key}: {value}")
#
#         form = OrderForm(request.POST)
#
#         # Log initial field requirements
#         print("\n--- INITIAL FIELD REQUIREMENTS ---")
#         for field_name, field in form.fields.items():
#             print(f"{field_name}: required={field.required}")
#
#         # Check the delivery option to adjust form validation requirements
#         delivery_option = request.POST.get('delivery_option')
#         print(f"\nSelected delivery option: {delivery_option}")
#
#         if delivery_option == 'pickup':
#             form.fields['street'].required = False
#             form.fields['city'].required = False
#             form.fields['province'].required = False
#             form.fields['postal_code'].required = False
#             form.fields['country'].required = False
#
#             print("\n--- UPDATED FIELD REQUIREMENTS FOR PICKUP ---")
#             for field_name, field in form.fields.items():
#                 print(f"{field_name}: required={field.required}")
#
#         # Log form validation status
#
#         if form.is_valid():
#             print("\n--- CREATING ORDER ---")
#
#
#             # Create the order without address fields if pickup is selected
#             order_data = {
#                 'customer': request.user,
#                 'cart': cart,
#                 'subtotal': subtotal,
#                 'total_discount': total_discount,
#                 'hst': hst,
#                 'total_with_hst': total_with_hst,
#                 'total_price': subtotal,
#                 'delivery_option': form.cleaned_data['delivery_option'],
#                 'order_number': generate_order_number(),
#                 'order_time': timezone.now(),
#                 'total_with_hst_and_shipping': total_with_hst_and_shipping,
#
#             }
#
#             # Only include address fields if delivery is not pickup
#             if delivery_option != 'pickup':
#                 order_data.update({
#                     'street': form.cleaned_data['street'],
#                     'city': form.cleaned_data['city'],
#                     'province': form.cleaned_data['province'],
#                     'postal_code': form.cleaned_data['postal_code'],
#                     'country': form.cleaned_data['country']
#                 })
#
#             # Place the order and mark checkout as completed
#             order = Order.objects.create(**order_data)
#             for cart_item in cart_items:
#                 OrderItem.objects.create(
#                     order=order,
#                     item=cart_item.item,
#                     quantity=cart_item.quantity,
#                     original_price=cart_item.item.price_default,
#                     discounted_price=cart_item.price,
#                     total_price=cart_item.total_price(),
#                     discount=(cart_item.item.price_default - cart_item.price) * cart_item.quantity
#                 )
#             cart.completed = True
#             cart.save()
#             messages.success(request, f"Order {order.order_number} placed successfully!")
#
#             # Reset checkout session data for fresh start in next checkout
#
#               # Reset session for a fresh checkout
#
#             print(f"Order {order.order_number} created for customer {request.user}")
#
#             # Redirect to the order confirmation page
#             return redirect('ecommerce:order_confirmation', order_id=order.id)
#
#         else:
#             # Form validation failed; log errors for debugging
#             print("\nForm is invalid")
#             print("\n--- FORM ERRORS ---")
#             for field, errors in form.errors.items():
#                 print(f"{field}: {errors}")
#             print("\n--- FIELD REQUIREMENTS AFTER MODIFICATION ---")
#             for field_name, field in form.fields.items():
#                 print(f"{field_name}: required={field.required}")
#     else:
#         form = OrderForm()
#
#     # form = None
#     print('444444444444444')
#     print("\n--- CHECKOUT FORM ---")
#     context = {
#         'cart': cart,
#         'form': form,
#         'subtotal': subtotal,
#         'total_discount': total_discount,
#         'hst': hst,
#         'total_with_hst': total_with_hst,
#         'cart_items': cart_items,
#         'timeout': CHECKOUT_TIMEOUT,  # Pass timeout duration to the template
#         'payment_success': payment_success,  # Pass this to the template
#         'shipping_rates': shipping_rates,
#         'show_shipping_rates': show_shipping_rates,  # NEW: Add flag to context
#         'total_with_hst_and_shipping': total_with_hst_and_shipping,  # Updated total
#         'shipping_service_name': shipping_service_name,
#         'shipping_data': shipping_data,
#         'remaining_time': remaining_time,
#     }
#     request.session['show_shipping_rates'] = False  # NEW: Reset flag
#
#     return render(request, 'ecommerce/checkout.html', context)












def cancel_checkout(user_id):
    """
    Restore stock if the user does not complete checkout within the timeout period.
    """
    if user_id in checkout_reservations:
        reserved_items = checkout_reservations[user_id]
        print(f"\n--- RESTORING STOCK FOR USER {user_id} ---")

        for sku, reserved_quantity in reserved_items.items():
            item = Item.objects.get(manufacturer_sku=sku)
            item.quantity_on_hand += reserved_quantity
            item.save()

            print(f"Restored {reserved_quantity} to {item.system_sku}. New stock: {item.quantity_on_hand}")

        # Remove the user's reservation after restoring stock
        del checkout_reservations[user_id]

        # Redirect the user to the cart with a cancellation message
        print(f"Checkout for user {user_id} canceled due to timeout.")

def reset_checkout_session(request):
    """
    Deletes specific checkout-related keys from the session.
    """
    # List of checkout-related session keys to delete
    checkout_keys = [
        'checkout_start_time',
        'checkout_started',
        'payment_success',
        'shipping_cost',
        'shipping_service_name',
        'shipping_data',
        'shipping_rates',
        'show_shipping_rates'
    ]

    # Delete each key from the session if it exists
    for key in checkout_keys:
        if key in request.session:
            del request.session[key]
            print(f"Deleted '{key}' from session.")

    # Mark the session as modified to ensure changes are saved
    request.session.modified = True
    print("Selected checkout session data deleted. Current session data:", dict(request.session))


def cancel_checkout(user_id):
    """
    Restore stock if the user does not complete checkout within the timeout period.
    """
    if user_id in checkout_reservations:
        reserved_items = checkout_reservations[user_id]
        print(f"\n--- RESTORING STOCK FOR USER {user_id} ---")

        for sku, reserved_quantity in reserved_items.items():
            item = Item.objects.get(manufacturer_sku=sku)
            item.quantity_on_hand += reserved_quantity
            item.save()

            print(f"Restored {reserved_quantity} to {item.system_sku}. New stock: {item.quantity_on_hand}")

        # Remove the user's reservation after restoring stock
        del checkout_reservations[user_id]

        # Redirect the user to the cart with a cancellation message
        print(f"Checkout for user {user_id} canceled due to timeout.")


from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from datetime import timedelta
from django.utils import timezone


@receiver(post_save, sender=Order)
def check_order_timeout(sender, instance, **kwargs):
    # Check if the order is not completed and if 15 minutes have passed since the order time
    if not instance.completed and instance.order_time + timedelta(minutes=15) <= timezone.now():
        # Temporarily disconnect the signal to avoid recursion
        post_save.disconnect(check_order_timeout, sender=Order)

        for order_item in instance.items.all():
            # Restore the quantity to the stock
            item = order_item.item
            item.quantity_on_hand += order_item.quantity
            item.save()

        # Optionally mark the order as 'cancelled' to indicate it was timed out
        instance.status = 'cancelled'
        instance.save()  # This save won't trigger the signal because it’s disconnected

        # Reconnect the signal after the save
        post_save.connect(check_order_timeout, sender=Order)


from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from .models import Order


@shared_task
def restore_uncompleted_order_items():
    # Find all uncompleted orders older than 15 minutes
    orders = Order.objects.filter(completed=False, order_time__lt=timezone.now() - timedelta(minutes=15))

    for order in orders:
        for order_item in order.orderitem_set.all():
            item = order_item.item
            item.quantity_on_hand += order_item.quantity
            item.save()

        # Optionally mark the order as cancelled
        order.status = 'cancelled'
        order.save()


from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    cart_items = order.cart.cartitem_set.all()
    customer = order.customer

    # External logo URL
    logo_url = 'https://www.mekcosupply.com/wp-content/uploads/2020/07/Mekco-Supply-logo-300-pix-2020.jpg'

    # Prepare the context for rendering the template and email
    context = {
        'order': order,
        'cart_items': cart_items,
        'total_price': order.subtotal,
        'total_discount': order.total_discount,
        'hst': order.hst,
        'total_with_hst': order.total_with_hst,
        'total_with_hst_and_shipping': order.total_with_hst_and_shipping,
        'logo_url': logo_url,  # Pass the logo URL to the context

    }

    # Render the HTML content for the order confirmation email
    html_message = render_to_string('ecommerce/order_confirmation.html', context)
    plain_message = strip_tags(html_message)  # Fallback plain text

    # Send the email
    send_mail(
        subject=f"Order Confirmation - Mekco Supply Inc. - Order #{order.id}",
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[request.user.email],
        html_message=html_message,  # Send HTML email content
    )

    return render(request, 'ecommerce/order_confirmation.html', context)




from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .forms import PricingRuleForm
from .models import PricingRule


@staff_member_required
def pricing_rule_list(request):
    pricing_rules = PricingRule.objects.all()
    return render(request, 'ecommerce/pricing_rule_list.html', {'pricing_rules': pricing_rules})


@staff_member_required
def add_pricing_rule(request):
    if request.method == 'POST':
        form = PricingRuleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ecommerce:pricing_rule_list')
    else:
        form = PricingRuleForm()
    return render(request, 'ecommerce/add_pricing_rule.html', {'form': form})


# views.py

from django.db.models import Q

# views.py

# views.py
from django.http import JsonResponse, HttpResponseBadRequest
from oauth_handler.models import Category

from django.http import JsonResponse
from oauth_handler.models import Category

from django.http import JsonResponse
from oauth_handler.models import Category

from django.http import JsonResponse
from oauth_handler.models import Category


def load_parent_category(request):
    category_id = request.GET.get('category_id')
    try:
        category = Category.objects.get(id=category_id)
        parent_category = category.parent
        if parent_category:
            return JsonResponse({'parent_category': {'id': parent_category.id, 'name': parent_category.name}})
        else:
            return JsonResponse({'parent_category': None})
    except Category.DoesNotExist:
        return JsonResponse({'parent_category': None})


def load_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = Category.objects.filter(parent_id=category_id).order_by('name')
    return JsonResponse({'subcategories': list(subcategories.values('id', 'name'))})


from django.shortcuts import render, get_object_or_404
from .models import PricingRule
from oauth_handler.models import Item
from customers.models import Customer


def get_discounted_price_for_rule(item, pricing_rule=None):
    if pricing_rule:
        discount = (pricing_rule.discount_percentage / 100) * item.price_default
        discounted_price = item.price_default - discount
    else:
        discounted_price = item.price_default  # Use the default price if no discount

    return round(discounted_price, 2)


def view_pricing_rule_items(request, pk):
    pricing_rule = get_object_or_404(PricingRule, pk=pk)
    descendants = pricing_rule.category.get_descendants()
    descendants_ids = [descendant.id for descendant in descendants] + [pricing_rule.category.id]

    items = Item.objects.filter(category_id__in=descendants_ids)
    for item in items:
        item.discounted_price = get_discounted_price_for_rule(item, pricing_rule)

    context = {
        'pricing_rule': pricing_rule,
        'items': items,
    }
    return render(request, 'ecommerce/view_pricing_rule_items.html', context)


def index(request):
    return render(request, 'ecommerce/index.html')


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import Order
from .forms import BulkActionForm


# @staff_member_required
# def custom_order_list_view(request):
#     statuses = Order.STATUS_CHOICES
#     orders_by_status = {}
#
#     # Group orders by status for display
#     for status in statuses:
#         status_code = status[0]
#         status_display = dict(Order.STATUS_CHOICES).get(status_code)
#         orders = Order.objects.filter(status=status_code).order_by('-created_at')
#         orders_by_status[status_display] = orders
#
#     # No POST handling since bulk actions are removed
#
#     context = {
#         'orders_by_status': orders_by_status,
#     }
#     return render(request, 'ecommerce/admin_order_list.html', context)
#
#
#
#
# from django.contrib import messages
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.admin.views.decorators import staff_member_required
# from .models import Order
# from .forms import StatusChangeForm
#
#
# from django.contrib import messages
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.admin.views.decorators import staff_member_required
# from .models import Order
# from .forms import StatusChangeForm
# from django.utils.html import strip_tags
# import logging
#
# # Set up logging
# logger = logging.getLogger(__name__)
#
# from django.contrib import messages
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.admin.views.decorators import staff_member_required
# from .models import Order
# from .forms import StatusChangeForm
# import logging
#
# from django.contrib import messages
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.admin.views.decorators import staff_member_required
# from .models import Order
# from .forms import StatusChangeForm
# import logging
#
# # Set up logging
# logger = logging.getLogger(__name__)
#
# from django.contrib import messages
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.admin.views.decorators import staff_member_required
# from .models import Order
# from .forms import StatusChangeForm
# import logging
#
# logger = logging.getLogger(__name__)
#
# from django.contrib import messages
#
# from django.contrib import messages
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.admin.views.decorators import staff_member_required
# from .models import Order
# from .forms import StatusChangeForm
# import logging
#
# # Set up logging
# logger = logging.getLogger(__name__)
#
# from django.contrib.admin.views.decorators import staff_member_required
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from django.http import HttpResponseRedirect
# from .models import Order
# import logging
#
# # Set up logging
# logger = logging.getLogger(__name__)
#
# from django.contrib.admin.views.decorators import staff_member_required
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from .models import Order
# import logging
#
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from django.http import JsonResponse
# from .models import Order
#
# from django.shortcuts import get_object_or_404, redirect, render
# from django.contrib import messages
# from .models import Order
# from django.urls import reverse
#
#
# from django.shortcuts import get_object_or_404, redirect, render
# from django.contrib import messages
# from django.urls import reverse
# from .models import Order
#
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from .models import Order
# from django.urls import reverse
# import logging
#
# logger = logging.getLogger(__name__)
#
# def update_order_status_view(request, order_id):
#     """
#     Handles the order status update via POST requests.
#     """
#     order = get_object_or_404(Order, id=order_id)
#
#     if request.method == "POST":
#         # Get the submitted status from the form
#         new_status = request.POST.get("status", "").strip()  # Strip any leading/trailing spaces
#
#         # Fetch valid statuses as a list
#         valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
#
#         # Debugging: log the new status and valid statuses
#         logger.info(f"Submitted new status: '{new_status}'")
#         logger.info(f"Valid statuses: {valid_statuses}")
#
#         # Validate the new status
#         if new_status in valid_statuses:
#             previous_status = order.status
#             order.status = new_status
#             order.save()
#
#             messages.success(
#                 request, f"Order status updated from '{previous_status}' to '{new_status}'."
#             )
#             return redirect(reverse("ecommerce:order_update_status", args=[order.id]))
#         else:
#             logger.warning(f"Invalid status submitted: '{new_status}'")
#             messages.error(request, "Invalid status selected. Please try again.")
#             return redirect(reverse("ecommerce:order_update_status", args=[order.id]))
#
#     context = {
#         "order": order,
#         "status_choices": Order.STATUS_CHOICES,
#     }
#     return render(request, "ecommerce/admin_order_detail.html", context)
#
#
#
#
#
# # Initialize logger
# logger = logging.getLogger(__name__)
#
# @staff_member_required
# def custom_order_detail_view(request, order_id):
#     # Retrieve the order object
#     order = get_object_or_404(Order, id=order_id)
#     logger.info(f"Accessing details for order #{order.order_number}")
#
#     # Define valid status choices
#     status_choices = {
#         'mark_as_unread': 'unread',
#         'mark_as_preparing': 'preparing',
#         'mark_as_ready_for_pickup': 'ready_for_pickup',
#         'mark_as_ready_for_shipping': 'ready_for_shipping',
#         'mark_as_shipped': 'shipped',
#         'mark_as_delivered': 'delivered',
#         'mark_as_cancelled': 'cancelled',
#         'mark_as_complete': 'complete',
#     }
#
#     if request.method == 'POST':
#         # Log the incoming POST data
#         action = request.POST.get('action', None)
#         logger.info(f"POST request received with action: {action}")
#
#         if not action or action not in status_choices:
#             logger.error(f"Invalid action: {action} for order #{order.order_number}")
#             messages.error(request, "Invalid action. Please select a valid status.")
#             return redirect('ecommerce:admin_order_detail', order_id=order.id)
#
#         new_status = status_choices[action]
#         logger.info(f"Action '{action}' maps to status '{new_status}'.")
#
#         # Prevent status change for cancelled orders unless reverting to unread
#         if order.status == 'cancelled' and new_status != 'unread':
#             logger.warning(f"Attempt to change cancelled order #{order.order_number}")
#             messages.warning(request, "Cancelled orders can only be reverted to 'Unread'.")
#             return redirect('ecommerce:admin_order_detail', order_id=order.id)
#
#         # Update order status
#         previous_status = order.status
#         order.status = new_status
#         order.save()
#         logger.info(f"Order #{order.order_number} status updated from '{previous_status}' to '{new_status}'.")
#
#         # Notify customer
#         try:
#             send_status_update_email(order)
#             messages.success(
#                 request,
#                 f"Order status updated to {order.get_status_display()}. Notification sent to the customer.",
#             )
#         except Exception as e:
#             logger.error(f"Failed to send email for order #{order.order_number}: {e}")
#             messages.error(request, "Order status updated, but notification email failed.")
#
#         return redirect('ecommerce:admin_order_detail', order_id=order.id)
#
#     # Render the order detail page
#     context = {
#         'order': order,
#         'status_choices': status_choices.items(),  # Pass choices as a list of tuples
#         'order_items': order.items.all(),
#     }
#     return render(request, 'ecommerce/admin_order_detail.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Order
from .forms import OrderStatusForm  # Create a form to handle status changes


# Custom view for listing orders
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Order
from .forms import OrderStatusForm  # Create a form to handle status changes


# Custom view for listing orders
# ecommerce/views.py
from django.shortcuts import render
from .models import Order  # Make sure to import your Order model

def order_list(request):
    # Fetch all orders from the database
    orders = Order.objects.all()
    return render(request, 'ecommerce/order_list.html', {'orders': orders})



# Custom view for order detail (update status to "cancelled")



# ecommerce/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Order
from .forms import OrderStatusForm

def update_order_status(request, order_id):
    # Retrieve the order by ID
    order = get_object_or_404(Order, id=order_id)

    # Handle POST request for updating order status
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)  # Bind the form to the existing order
        if form.is_valid():
            form.save()  # Save the updated status
            messages.success(request, f"Order status updated to: {order.get_status_display()}")
            return redirect('ecommerce:order_detail', order_id=order.id)
    else:
        form = OrderStatusForm(instance=order)  # Bind the form to the order instance for GET request

    return render(request, 'ecommerce/order_detail.html', {
        'order': order,
        'form': form
    })

# views.py
from django.shortcuts import render
from .models import Order

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Order
from .forms import OrderStatusForm  # Assume this form updates the order status

from django.shortcuts import render, get_object_or_404
from .models import Order, OrderItem
from .forms import OrderStatusForm

from django.shortcuts import render, get_object_or_404
from .models import Order, OrderItem
from .forms import OrderStatusForm

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum
from decimal import Decimal
from django.contrib.auth.decorators import login_required

# Import your Order model and OrderStatusForm as needed
from ecommerce.models import Order
from ecommerce.forms import OrderStatusForm

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ecommerce.models import Order
from ecommerce.forms import OrderStatusForm  # Make sure this is correctly imported

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ecommerce.models import Order
from ecommerce.forms import OrderStatusForm


@login_required
def order_detail(request, order_id):
    # Retrieve the order, ensuring it belongs to the logged-in user
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    order_items = order.items.all()  # This uses the related_name defined in OrderItem

    # Build a customer display name using first and last names, fallback to email if needed.
    customer = order.customer
    customer_name = (f"{customer.first_name} {customer.last_name}".strip()
                     if (customer.first_name or customer.last_name)
                     else customer.email)

    # Handle order status update form
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f"Order status updated to: {order.get_status_display()}")
            return redirect('ecommerce:order_detail', order_id=order_id)
    else:
        form = OrderStatusForm(instance=order)

    context = {
        'order': order,
        'order_items': order_items,
        'customer_name': customer_name,
        'form': form,
    }
    return render(request, 'ecommerce/order_detail.html', context)


from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import logging

logger = logging.getLogger(__name__)

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_status_update_email(order):
    logger.info(f"Sending email for order #{order.order_number} with status {order.get_status_display()}")

    # External logo URL
    logo_url = 'https://www.mekcosupply.com/wp-content/uploads/2020/07/Mekco-Supply-logo-300-pix-2020.jpg'

    # Prepare the email subject and context for rendering
    subject = f"Order Status Update - Mekco Supply Inc. - Order #{order.order_number}"
    context = {
        'order': order,
        'status': order.get_status_display(),
        'order_number': order.order_number,
        'updated_at': order.updated_at,
        'logo_url': logo_url,
    }

    # Render the HTML and plain text message
    html_message = render_to_string('ecommerce/order_status_update_email.html', context)
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer.email],
            html_message=html_message,
        )
        logger.info(f"Email sent successfully to {order.customer.email} for order #{order.order_number}")
    except Exception as e:
        logger.error(f"Failed to send email for order #{order.order_number}: {e}")



from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import Order, ReturnRequest


@staff_member_required
def orders_with_returns_view(request):
    # Get all orders that have return requests
    orders_with_returns = Order.objects.filter(return_requests__isnull=False).distinct()

    context = {
        'orders_with_returns': orders_with_returns,
    }
    return render(request, 'ecommerce/orders_with_returns.html', context)


from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
import paypalrestsdk
from ecommerce.models import Order, OrderItem

from ecommerce.models import ReturnRequest

from django.shortcuts import get_object_or_404, render, redirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
import paypalrestsdk
import logging

logger = logging.getLogger(__name__)


@staff_member_required
def return_requests_by_order_view(request, order_id):
    logger = logging.getLogger(__name__)
    order = get_object_or_404(Order, id=order_id)
    return_requests = ReturnRequest.objects.filter(order=order)

    # Calculate total approved refund amount
    total_approved_refund = sum(
        request_item.refund_amount or 0 for request_item in return_requests if request_item.status == 'approved'
    )

    if request.method == "POST":
        paypal_sale_id = request.POST.get("paypal_sale_id", "").strip()
        logger.info(f"Processing refunds for order {order.order_number}, PayPal Sale ID: {paypal_sale_id}")

        if not paypal_sale_id:
            logger.error("Missing PayPal Sale ID.")
            messages.error(request, "Refund failed: Missing PayPal Sale ID.")
            return redirect('ecommerce:return_requests_by_order', order_id=order_id)

        try:
            # Configure PayPal SDK
            paypalrestsdk.configure({
                "mode": settings.PAYPAL_MODE,
                "client_id": settings.PAYPAL_CLIENT_ID,
                "client_secret": settings.PAYPAL_SECRET_KEY,
            })
            logger.info("PayPal SDK configured.")

            # Fetch PayPal sale details
            logger.debug(f"Fetching sale details for PayPal Sale ID: {paypal_sale_id}")
            sale = paypalrestsdk.Sale.find(paypal_sale_id)

            # Log the PayPal sale details for debugging
            if not sale or not hasattr(sale, 'amount'):
                raise ValueError("Invalid or incomplete sale object returned from PayPal API.")

            logger.debug(f"PayPal Sale Object: {sale.__dict__}")

        except Exception as e:
            logger.error(f"Error fetching PayPal sale details: {str(e)}")
            messages.error(request, "Could not fetch PayPal sale details. Refunds not processed.")
            return redirect('ecommerce:return_requests_by_order', order_id=order_id)

        # Process each return request
        for request_item in return_requests:
            # Skip already approved requests to prevent duplication
            if request_item.status == 'approved':
                logger.warning(f"Refund for item {request_item.item.description} (Request ID: {request_item.id}) "
                               f"already approved. Skipping.")
                continue

            refund_status = request.POST.get(f'status_{request_item.id}', '').strip()
            denied_reason = request.POST.get(f'denied_reason_{request_item.id}', '').strip()

            logger.info(f"Processing refund for item {request_item.item.description} (Request ID: {request_item.id})")
            logger.debug(f"Refund status: {refund_status}, Denied reason: {denied_reason}")

            # Update refund status
            request_item.status = refund_status
            if refund_status == 'denied':
                request_item.denied_reason = denied_reason
                request_item.save()
                logger.info(f"Refund for item {request_item.item.description} denied: {denied_reason}")
                continue

            if refund_status == 'approved':
                refund_amount = request_item.refund_amount or 0.0

                try:
                    # Process refund
                    refund = sale.refund({
                        "amount": {
                            "total": f"{refund_amount:.2f}",
                            "currency": "CAD",
                        }
                    })

                    if refund.success():
                        logger.info(f"Refund approved for {request_item.item.description}: ${refund_amount:.2f}")
                        request_item.status = 'approved'
                        request_item.denied_reason = ''
                        request_item.save()
                        total_approved_refund += refund_amount  # Update total approved refund
                        messages.success(request,
                                         f"Refund of ${refund_amount:.2f} for {request_item.item.description} approved.")
                    else:
                        error_message = refund.error.get('message', 'Unknown error') if hasattr(refund,
                                                                                                'error') else 'Unknown error'
                        logger.error(f"Refund failed for {request_item.item.description}: {error_message}")
                        request_item.status = 'denied'
                        request_item.denied_reason = error_message
                        request_item.save()
                        messages.error(request, f"Refund failed for {request_item.item.description}: {error_message}")
                except Exception as e:
                    logger.exception(f"Error processing refund for {request_item.item.description}: {str(e)}")
                    request_item.status = 'denied'
                    request_item.denied_reason = str(e)
                    request_item.save()
                    messages.error(request, f"Refund failed for {request_item.item.description}: {str(e)}")

        return redirect('ecommerce:return_requests_by_order', order_id=order_id)

    # Pass necessary data to the template
    context = {
        'order': order,
        'return_requests': return_requests,
        'total_approved_refund': total_approved_refund,  # Include total approved refund
    }
    return render(request, 'ecommerce/return_requests_by_order.html', context)



from django.shortcuts import redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import ReturnRequest, Order


@staff_member_required
def update_return_request_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        for return_request in order.return_requests.all():
            status_key = f'status_{return_request.id}'
            reason_key = f'denied_reason_{return_request.id}'
            new_status = request.POST.get(status_key)
            denied_reason = request.POST.get(reason_key)

            if new_status:
                return_request.status = new_status
                return_request.denied_reason = denied_reason if new_status == 'denied' else ''
                return_request.save()

    return redirect('ecommerce:return_requests_by_order', order_id=order.id)


from decimal import Decimal
import paypalrestsdk
from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from ecommerce.models import Cart, Item


from django.urls import reverse

@login_required
def paypal_payment(request):
    cart = get_object_or_404(Cart, customer=request.user, completed=False)
    cart_items = cart.cartitem_set.all()

    subtotal = sum(item.price * item.quantity for item in cart_items).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    hst_rate = Decimal('0.13')
    hst = (subtotal * hst_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_with_hst = (subtotal + hst).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    shipping_cost = Decimal(request.session.get('shipping_cost', '0'))
    total_with_hst_and_shipping = (total_with_hst + shipping_cost).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # PayPal configuration
    paypalrestsdk.configure({
        "mode": settings.PAYPAL_MODE,
        "client_id": settings.PAYPAL_CLIENT_ID,
        "client_secret": settings.PAYPAL_SECRET_KEY
    })

    # Create PayPal payment object with cart items
    items_list = [{
        "name": item.item.description,
        "sku": item.item.system_sku,
        "price": str(item.price),
        "currency": "CAD",
        "quantity": item.quantity
    } for item in cart_items]

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse('ecommerce:execute_payment')),
            "cancel_url": request.build_absolute_uri(reverse('ecommerce:cancel_payment'))
        },
        "transactions": [{
            "item_list": {
                "items": items_list
            },
            "amount": {
                "total": str(total_with_hst_and_shipping),
                "currency": "CAD",
                "details": {
                    "subtotal": str(subtotal),
                    "tax": str(hst),
                    "shipping": str(shipping_cost)  # Add shipping if applicable
                }
            },
            "description": "Mekco Supply Payment"
        }]
    })

    # Redirect to PayPal for approval
    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = str(link.href)
                return redirect(approval_url)
    else:
        messages.error(request, "Error processing PayPal payment.")
        return render(request, "ecommerce/error.html", {"error": payment.error})


@login_required
def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    if not payment_id or not payer_id:
        messages.error(request, "Invalid PayPal payment request.")
        return redirect('ecommerce:checkout')

    # Configure PayPal SDK
    paypalrestsdk.configure({
        "mode": settings.PAYPAL_MODE,
        "client_id": settings.PAYPAL_CLIENT_ID,
        "client_secret": settings.PAYPAL_SECRET_KEY
    })

    # Execute the payment
    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        # Extract the sale ID
        sale_id = payment.transactions[0].related_resources[0].sale.id

        # Payment succeeded, place the order with the sale ID
        return place_order(request, sale_id=sale_id)
    else:
        messages.error(request, "Payment failed. Please try again.")
        return render(request, "ecommerce/error.html", {"error": payment.error})


@login_required
def place_order(request, sale_id=None):
    # Verify that payment was successful
    if not request.session.get('payment_success', True):
        messages.error(request, "Please complete your payment before placing your order.")
        return redirect('ecommerce:checkout')

    # Fetch cart and calculate order totals
    cart = get_object_or_404(Cart, customer=request.user, completed=False)
    cart_items = cart.cartitem_set.all()
    subtotal = sum(item.price * item.quantity for item in cart_items).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_discount = sum((item.item.price_default - item.price) * item.quantity for item in cart_items).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    hst_rate = Decimal('0.13')
    hst = (subtotal * hst_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_with_hst = (subtotal + hst).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    shipping_cost = Decimal(request.session.get('shipping_cost', '0')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_with_hst_and_shipping = (total_with_hst + shipping_cost).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # Prepare order data
    order_data = {
        'customer': request.user,
        'cart': cart,
        'subtotal': subtotal,
        'total_discount': total_discount,
        'hst': hst,
        'total_with_hst': total_with_hst,
        'total_with_hst_and_shipping': total_with_hst_and_shipping,
        'delivery_option': request.session.get('shipping_data', {}).get('delivery_option', ''),
        'order_number': str(uuid.uuid4().hex),
        'order_time': timezone.now(),
        'total_price': subtotal,  # Set the total_price here
        'paypal_sale_id': sale_id  # Save the sale ID here
    }

    # Add address fields if delivery option is not pickup
    if order_data['delivery_option'] != 'pickup':
        shipping_data = request.session.get('shipping_data', {})
        order_data.update({
            'street': shipping_data.get('street', ''),
            'city': shipping_data.get('city', ''),
            'province': shipping_data.get('province', ''),
            'postal_code': shipping_data.get('postal_code', ''),
            'country': shipping_data.get('country', '')
        })

    # Create the order
    order = Order.objects.create(**order_data)

    # Create order items
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            item=cart_item.item,
            quantity=cart_item.quantity,
            original_price=cart_item.item.price_default,
            discounted_price=cart_item.price,
            total_price=cart_item.total_price(),
            discount=(cart_item.item.price_default - cart_item.price) * cart_item.quantity
        )

    # Mark the cart as completed and clear session data
    cart.completed = True
    cart.save()

    # Cancel timeout logic and clear session
    if f'checkout_{cart.id}' in checkout_reservations:
        del checkout_reservations[f'checkout_{cart.id}']

    # Safely handle timeout logic
    timeout_timer = checkout_reservations.get(f'checkout_{cart.id}')
    if timeout_timer and hasattr(timeout_timer, 'cancel'):
        timeout_timer.cancel()

    keys_to_clear = ['checkout_start_time', 'shipping_data', 'shipping_cost', 'payment_success']
    for key in keys_to_clear:
        if key in request.session:
            del request.session[key]

    request.session.modified = True  # Save session changes

    messages.success(request, f"Order {order.order_number} placed successfully!")

    # Redirect to the order confirmation page
    return redirect('ecommerce:order_confirmation', order_id=order.id)



def cancel_payment(request):
    return render(request, 'ecommerce/cancel.html', {'message': 'Your payment has been cancelled.'})


def success_view(request):
    return render(request, "ecommerce/success.html")


def error_view(request):
    return render(request, "ecommerce/error.html")


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import paypalrestsdk
from decimal import Decimal

@login_required
def refund_order_item(request, order_item_id):
    # Retrieve the order item
    order_item = get_object_or_404(OrderItem, id=order_item_id, order__customer=request.user)

    # Ensure valid refund request
    if order_item.return_quantity <= 0 or order_item.refund_status != 'pending':
        messages.error(request, "Invalid or already processed refund request.")
        return redirect('ecommerce:order_detail', order_id=order_item.order.id)

    # Calculate the refund amount
    refund_amount = order_item.return_quantity * order_item.discounted_price

    # Configure PayPal SDK
    paypalrestsdk.configure({
        "mode": settings.PAYPAL_MODE,
        "client_id": settings.PAYPAL_CLIENT_ID,
        "client_secret": settings.PAYPAL_SECRET_KEY
    })

    # Find the PayPal sale
    sale = paypalrestsdk.Sale.find(order_item.order.paypal_sale_id)

    # Attempt to refund
    refund = sale.refund({
        "amount": {
            "total": str(refund_amount),
            "currency": "CAD"
        }
    })

    if refund.success():
        # Update the order item refund details
        order_item.refund_status = 'approved'
        order_item.refund_amount = refund_amount
        order_item.save()

        messages.success(request, f"Refund for {order_item.return_quantity} items approved, total refunded: ${refund_amount}.")
    else:
        # Mark the refund as denied
        order_item.refund_status = 'denied'
        order_item.save()

        messages.error(request, f"Refund failed: {refund.error}")

    return redirect('ecommerce:order_detail', order_id=order_item.order.id)



from django.http import JsonResponse
from django.http import JsonResponse

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import OrderItem



from django.shortcuts import render, get_object_or_404
from oauth_handler.models import Category, Item

from django.shortcuts import render, get_object_or_404, redirect
from oauth_handler.models import Category
from django.shortcuts import render, get_object_or_404
from oauth_handler.models import Category, Item
from django.shortcuts import render, get_object_or_404
from oauth_handler.models import Category

from django.shortcuts import render, get_object_or_404, redirect
from oauth_handler.models import Category

def item_list(request):
    # Fetch all root categories (these are shown when no category is selected)
    categories = Category.objects.filter(parent=None).prefetch_related('children').order_by('name')

    # Fetch query parameters
    category_query = request.GET.get('category', '')

    selected_category = None
    subcategories = None
    full_category_path = []
    sidebar_categories = categories  # Default to root categories for sidebar

    if category_query:
        # Fetch the selected category
        selected_category = get_object_or_404(Category, id=category_query)

        # Fetch its subcategories
        subcategories = selected_category.children.all().order_by('name')

        # Build full category path (breadcrumb trail)
        ancestor = selected_category
        while ancestor:
            full_category_path.insert(0, ancestor)
            ancestor = ancestor.parent

        # Determine sidebar categories:
        # - If the selected category has subcategories, show them
        # - Otherwise, show the siblings of the selected category
        if subcategories.exists():
            sidebar_categories = subcategories
        else:
            sidebar_categories = Category.objects.filter(parent=selected_category.parent).order_by('name')

        # Redirect to items page if no subcategories
        if not subcategories.exists():
            return redirect('ecommerce:items_list', category_id=selected_category.id)

    context = {
        'categories': categories,  # Root categories for other parts of the page
        'selected_category': selected_category,
        'subcategories': subcategories,
        'full_category_path': full_category_path,
        'sidebar_categories': sidebar_categories,  # Sidebar updates dynamically
    }

    return render(request, 'ecommerce/test.html', context)





from django.shortcuts import render, get_object_or_404
from oauth_handler.models import Category, Item

from django.shortcuts import render, get_object_or_404
from oauth_handler.models import Category, Item


def items_list_view(request, category_id):
    # Fetch the category
    category = get_object_or_404(Category, id=category_id)

    # Fetch items under this category
    items = Item.objects.filter(category=category)

    # Process items to include discounted price and bag/box options
    for item in items:
        # Add discounted price to each item
        item.discounted_price = get_discounted_price(item, request.user)

        # Check and set bag and box options
        item.has_bag_option = item.has_bag_option
        item.has_box_option = item.has_box_option

    # Determine sidebar categories
    if category.children.exists():
        sidebar_categories = category.children.all().order_by('name')
    else:
        sidebar_categories = Category.objects.filter(parent=category.parent).order_by('name')

    # Build full category path for breadcrumbs
    full_category_path = []
    ancestor = category
    while ancestor:
        full_category_path.insert(0, ancestor)
        ancestor = ancestor.parent

    context = {
        'category': category,
        'items': items,  # Now includes discounted price and options
        'sidebar_categories': sidebar_categories,  # Update sidebar dynamically
        'full_category_path': full_category_path,
    }

    return render(request, 'ecommerce/testitems.html', context)



from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Item, Cart, CartItem

@login_required
def item_detail(request, item_id):
    # Fetch the item based on its ID and ensure it's public
    item = get_object_or_404(Item, id=item_id, status='public')

    # Default message if the item is not available for purchase
    if item.quantity_on_hand < 1:
        message = "This item is not available for purchase. Please contact our salespersons."
    else:
        message = ""

    # Calculate the discounted price for the main item (single item)
    item.discounted_price = get_discounted_price(item, request.user)

    # Calculate bag and box availability
    available_singles = item.quantity_on_hand
    available_bags = (
        available_singles // item.bag_quantity if item.has_bag_option and item.bag_quantity else 0
    )
    available_boxes = (
        available_singles // item.box_quantity if item.has_box_option and item.box_quantity else 0
    )

    success_message = None
    error_message = None

    if request.method == 'POST':
        item_type = request.POST.get('item_type', 'single')
        quantity = int(request.POST.get('quantity', 1))

        # Calculate the total quantity based on item type
        if item_type == 'box' and item.has_box_option:
            total_quantity = quantity * item.box_quantity
        elif item_type == 'bag' and item.has_bag_option:
            total_quantity = quantity * item.bag_quantity
        else:
            total_quantity = quantity

        # Validate stock availability
        if total_quantity > item.quantity_on_hand:
            error_message = 'Not enough stock available.'
        else:
            try:
                # Create or update the cart
                cart, created = Cart.objects.get_or_create(customer=request.user, completed=False)
                cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
                cart_item.quantity += total_quantity
                cart_item.save()
                success_message = f'{quantity} {item_type}(s) of "{item.description}" added to your cart.'
            except Exception as e:
                error_message = f"An error occurred while adding the item to the cart: {str(e)}"

    # Fetch item images (if any)
    images = item.images.all()

    # Build the full category path for breadcrumbs
    full_category_path = []
    ancestor = item.category
    while ancestor:
        full_category_path.insert(0, ancestor)
        ancestor = ancestor.parent

    # Prepare the context for rendering the template
    context = {
        'item': item,
        'message': message,
        'images': images,
        'available_singles': available_singles,
        'available_bags': available_bags,
        'available_boxes': available_boxes,
        'success_message': success_message,
        'error_message': error_message,
        'full_category_path': full_category_path,  # Pass the full category path for breadcrumbs
    }

    return render(request, 'ecommerce/test_detail.html', context)


def test_cart(request):
    return render(request, 'ecommerce/testcart.html')




