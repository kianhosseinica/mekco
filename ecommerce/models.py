# models.py
from django.db import models
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
import uuid
from django.db import models
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
import uuid

from oauth_handler.models import Item

class PublicPrivateMixin(models.Model):
    STATUS_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='public')

    class Meta:
        abstract = True

class EcommerceItem(PublicPrivateMixin):
    item = models.OneToOneField(Item, on_delete=models.CASCADE)
    min_order_quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=50)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    is_returnable = models.BooleanField(default=True)  # Add this line to include the is_returnable field


from django.db import models
from ecommerce.models import Item  # Assuming this is where your Item model is located
from django.conf import settings


class Cart(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Cart of {self.customer.get_username() or self.customer.email}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)  # Changed to reference Item instead of EcommerceItem
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Unit price after discount

    def save(self, *args, **kwargs):
        # Calculate the price for the item if it's not set or zero
        if not self.price or self.price == 0:
            self.price = self.get_item_price()
        super().save(*args, **kwargs)

    def get_item_price(self):
        """
        This method will determine the discounted price of the item based on the quantity
        and whether it's a bag, box, or individual item.
        """
        if self.item.has_box_option and self.quantity >= self.item.box_quantity:
            return self.item.calculate_box_price()  # Assuming you have a method to calculate box price
        elif self.item.has_bag_option and self.quantity >= self.item.bag_quantity:
            return self.item.calculate_bag_price()  # Assuming you have a method to calculate bag price
        return self.item.price_default

    def total_price(self):
        """
        Calculate the total price of the item based on its quantity and unit price.
        """
        return self.quantity * self.price




from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
from decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
def generate_order_number():
    return str(uuid.uuid4().hex)





class Order(models.Model):
    DELIVERY_CHOICES = [
        ('pickup', 'Pick up at store'),
        ('shipping', 'Shipping'),
    ]

    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('preparing', 'Preparing'),
        ('ready_for_pickup', 'Ready for Pickup'),
        ('ready_for_shipping', 'Ready for Shipping'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('complete', 'Complete'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)  # Allows multiple orders per cart
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    hst = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_with_hst = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_with_hst_and_shipping = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # New field
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Final price before any adjustments like discounts and taxes
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    delivery_option = models.CharField(max_length=10, choices=DELIVERY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unread')
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)  # Automatically updates when the record is modified
    order_number = models.CharField(max_length=100, unique=True, default=generate_order_number)
    order_time = models.DateTimeField(default=timezone.now)  # Add this field to track order placement time


    def __str__(self):
        return f"Order {self.order_number} for {self.customer}"

# Detailed information about each item in an order
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"OrderItem for {self.item.description} (Order {self.order.order_number})"


from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

@receiver(user_logged_in)
def create_or_assign_cart(sender, request, user, **kwargs):
    Cart.objects.get_or_create(customer=user, completed=False)

from customers.models import Customer
from oauth_handler.models import Category

class PricingRule(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ('bronze', 'Bronze'),
        ('gold', 'Gold'),
        ('hvac', 'HVAC'),
        ('individual', 'Individual'),
        ('platinum', 'Platinum'),
        ('silver', 'Silver'),
        ('supplier', 'Supplier'),
    ]

    customer_type = models.CharField(max_length=50, choices=CUSTOMER_TYPE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.customer_type} - {self.category.name} - {self.discount_percentage}%"


from decimal import Decimal

from django.db import models
from decimal import Decimal

from decimal import Decimal
from django.db import models

from decimal import Decimal
from django.db import models


class ReturnRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('received', 'Received'),
        ('waiting_for_payment', 'Waiting for Payment'),
        ('complete', 'Complete'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='return_requests')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_date = models.DateTimeField(auto_now_add=True)
    denied_reason = models.TextField(blank=True, null=True)  # Field for denial reason
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Store refund amount
    refund_hst = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Store refund HST
    restocking_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Store restocking fee
    refund_subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Store refund subtotal

    def calculate_refund(self):
        # Find the corresponding OrderItem
        order_item = self.order.items.get(item=self.item)

        # Use the discounted price if available, otherwise use the original price
        price_per_item = order_item.discounted_price if order_item.discount > 0 else order_item.original_price

        # Calculate the total item price for the returned quantity
        total_item_price = price_per_item * self.quantity

        # Calculate HST (13%)
        refund_hst = total_item_price * Decimal('0.13')

        # Calculate the refund subtotal (total item price + HST)
        refund_subtotal = total_item_price + refund_hst

        # Calculate the restocking fee (10% of refund subtotal)
        restocking_fee = refund_subtotal * Decimal('0.10')

        # Calculate the final refund amount (refund subtotal - restocking fee)
        refund_amount = refund_subtotal - restocking_fee

        # Return rounded refund amounts
        return {
            'refund_amount': round(refund_amount, 2),
            'refund_hst': round(refund_hst, 2),
            'restocking_fee': round(restocking_fee, 2),
            'refund_subtotal': round(refund_subtotal, 2),
        }

    def save(self, *args, **kwargs):
        if self.status == 'approved':
            refund_details = self.calculate_refund()
            self.refund_amount = refund_details['refund_amount']
            self.refund_hst = refund_details['refund_hst']
            self.restocking_fee = refund_details['restocking_fee']
            self.refund_subtotal = refund_details['refund_subtotal']
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Return Request for {self.item.description} from order {self.order.order_number}"


def get_discounted_price(item, user_or_pricing_rule):
    if hasattr(user_or_pricing_rule, 'is_authenticated'):
        user = user_or_pricing_rule
        if not user.is_authenticated:
            return item.price_default
        customer = get_object_or_404(Customer, email=user.email)
        customer_type = customer.customer_type
    else:
        customer_type = user_or_pricing_rule.customer_type

    # Fetch all applicable pricing rules and order by the highest discount percentage
    pricing_rules = PricingRule.objects.filter(
        customer_type=customer_type,
        category__in=item.category.get_ancestors(include_self=True)
    ).order_by('-discount_percentage')

    if pricing_rules.exists():
        # Use the pricing rule with the highest discount
        best_pricing_rule = pricing_rules.first()
        discount = (best_pricing_rule.discount_percentage / 100) * item.price_default
        return round(item.price_default - discount, 2)
    else:
        return item.price_default
