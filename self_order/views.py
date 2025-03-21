from django.shortcuts import render, get_object_or_404, redirect
from ecommerce.models import Item, PricingRule
from customers.models import Customer
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from ecommerce.models import Item, Category, PricingRule
from customers.models import Customer
from django.contrib.auth.decorators import login_required
from .models import SelfOrderCart, SelfOrderCartItem

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

    pricing_rules = PricingRule.objects.filter(
        customer_type=customer_type,
        category__in=category_ancestors
    ).order_by('-discount_percentage')

    if pricing_rules.exists():
        best_pricing_rule = pricing_rules.first()
        discount = (best_pricing_rule.discount_percentage / 100) * item.price_default
        return round(item.price_default - discount, 2)
    else:
        return item.price_default

def self_order_home(request):
    return render(request, "self_order/home.html")

def search_customer(request):
    phone_number = request.GET.get('phone')
    try:
        customer = Customer.objects.get(phone_number=phone_number)
        return JsonResponse({'name': f"{customer.first_name} {customer.last_name}", 'customer_id': customer.id}, status=200)
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Customer not found'}, status=404)


def self_order_menu(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    # Fetch all root categories
    categories = Category.objects.filter(parent=None).prefetch_related('children').order_by('name')

    # Get the selected category from the request
    category_query = request.GET.get('category', '')

    selected_category = None
    subcategories = None
    full_category_path = []
    sidebar_categories = categories  # Default to root categories

    if category_query:
        selected_category = get_object_or_404(Category, id=category_query)
        subcategories = selected_category.children.all().order_by('name')

        # Build full category path (breadcrumb navigation)
        ancestor = selected_category
        while ancestor:
            full_category_path.insert(0, ancestor)
            ancestor = ancestor.parent

        # Sidebar logic
        if subcategories.exists():
            sidebar_categories = subcategories
        else:
            sidebar_categories = Category.objects.filter(parent=selected_category.parent).order_by('name')

    # Fetch items based on the selected category
    if selected_category:
        items = Item.objects.filter(category=selected_category)
    else:
        items = Item.objects.all()  # Show all items if no category is selected

    # Apply user-specific pricing
    for item in items:
        item.discounted_price = get_discounted_price(item, customer)

    return render(request, "self_order/menu.html", {
        "items": items,
        "customer": customer,
        "categories": categories,
        "selected_category": selected_category,
        "subcategories": subcategories,
        "full_category_path": full_category_path,
        "sidebar_categories": sidebar_categories,
    })



@login_required
def add_to_self_order_cart(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        quantity = int(request.POST.get("quantity", 1))

        item = get_object_or_404(Item, id=item_id)
        customer = request.user

        # Get or create the self-order cart
        cart, created = SelfOrderCart.objects.get_or_create(customer=customer)

        # Check if item is already in the cart
        cart_item, created = SelfOrderCartItem.objects.get_or_create(
            cart=cart, item=item,
            defaults={"quantity": quantity, "price": get_discounted_price(item, customer)}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return JsonResponse({"message": f"{quantity}x {item.description} added to cart!"})

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def self_order_cart_view(request):
    cart, created = SelfOrderCart.objects.get_or_create(customer=request.user)
    cart_items = cart.items.all()
    total_price = cart.total_price()

    return render(request, "self_order/cart.html", {
        "cart_items": cart_items,
        "total_price": total_price,
    })


@login_required
def self_order_checkout(request):
    cart, created = SelfOrderCart.objects.get_or_create(customer=request.user)
    cart_items = cart.items.all()
    total_price = cart.total_price()

    if request.method == "POST":
        # Here we will later add payment logic (Stripe, PayPal)
        cart.delete()
        return redirect("self_order:self_order_success")

    return render(request, "self_order/checkout.html", {
        "cart_items": cart_items,
        "total_price": total_price,
    })

