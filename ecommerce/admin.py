from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import *
from oauth_handler.models import Item, Category
from .forms import PricingRuleForm
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal



class PricingRuleAdmin(admin.ModelAdmin):
    form = PricingRuleForm
    list_display = ('customer_type', 'category', 'discount_percentage', 'view_items_link')
    list_filter = ('customer_type', 'category')
    search_fields = ('customer_type', 'category__name')
    actions = ['apply_pricing_rule']

    def apply_pricing_rule(self, request, queryset):
        for pricing_rule in queryset:
            self.apply_discount(pricing_rule)
        self.message_user(request, "Pricing rules applied successfully.")
    apply_pricing_rule.short_description = "Apply selected pricing rules"

    def apply_discount(self, pricing_rule):
        descendants = pricing_rule.category.get_descendants()
        descendants_ids = [descendant.id for descendant in descendants] + [pricing_rule.category.id]

        items = Item.objects.filter(category_id__in=descendants_ids)
        for item in items:
            item.discounted_price = pricing_rule.get_discounted_price(item)
            item.save()

    def view_items_link(self, obj):
        return format_html('<a href="{}">View Items</a>', reverse('ecommerce:view_pricing_rule_items', args=[obj.id]))
    view_items_link.short_description = "View Items"

admin.site.register(PricingRule, PricingRuleAdmin)

from django.urls import path
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin


from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ('order_number', 'customer', 'status', 'created_at', 'updated_at', 'view_order_items')

    # Allow filtering and searching
    list_filter = ('status', 'delivery_option', 'created_at')
    search_fields = ('order_number', 'customer__username', 'customer__email', 'status')

    def view_order_items(self, obj):
        """Custom link to view the order details"""
        return format_html(
            '<a href="{}">View Items</a>',
            reverse('admin:ecommerce_order_change', args=[obj.id])  # Admin URL for editing the order
        )
    view_order_items.short_description = "Order Items"

    def get_urls(self):
        """Add custom URLs for admin actions"""
        urls = super().get_urls()
        custom_urls = [
            # Add your custom admin URLs here if needed
        ]
        return custom_urls + urls


class OrderItemInline(admin.TabularInline):
    """Inline view for Order Items in the Order admin"""
    model = OrderItem
    extra = 0  # Do not show extra empty fields
    readonly_fields = ('item', 'quantity', 'original_price', 'discounted_price', 'total_price', 'discount')


# Registering the OrderAdmin with the inline OrderItem view
class OrderWithItemsAdmin(OrderAdmin):
    inlines = [OrderItemInline]  # Attach the inline model


# Register the models with the improved admin interface
admin.site.register(Order, OrderWithItemsAdmin)



from decimal import Decimal
from django.contrib import admin
from .models import ReturnRequest

class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('order', 'item', 'quantity', 'status', 'request_date', 'refund_amount', 'denied_reason')
    list_filter = ('status', 'request_date')
    search_fields = ('order__order_number', 'item__description')

    actions = ['approve_returns', 'deny_returns', 'mark_as_received', 'mark_as_waiting_for_payment', 'mark_as_complete']

    def approve_returns(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, "Selected return requests have been approved.")

    def deny_returns(self, request, queryset):
        for obj in queryset:
            if not obj.denied_reason:
                # You can prompt the admin to input the reason here (or ensure it's filled before this step)
                self.message_user(request, f"Denial reason required for {obj}. Update the request with a reason.")
            else:
                obj.status = 'denied'
                obj.save()
        self.message_user(request, "Selected return requests have been denied.")

    def mark_as_received(self, request, queryset):
        queryset.update(status='received')
        self.message_user(request, "Selected return requests have been marked as received.")

    def mark_as_waiting_for_payment(self, request, queryset):
        queryset.update(status='waiting_for_payment')
        self.message_user(request, "Selected return requests have been marked as waiting for payment.")

    def mark_as_complete(self, request, queryset):
        queryset.update(status='complete')
        self.message_user(request, "Selected return requests have been marked as complete.")

    def refund_amount(self, obj):
        if obj.status in ['approved', 'complete']:
            return f"${obj.calculate_refund():.2f}"
        return "$0.00"

    refund_amount.short_description = "Refund Amount"

    approve_returns.short_description = "Approve selected return requests"
    deny_returns.short_description = "Deny selected return requests"
    mark_as_received.short_description = "Mark as received"
    mark_as_waiting_for_payment.short_description = "Mark as waiting for payment"
    mark_as_complete.short_description = "Mark as complete"

admin.site.register(ReturnRequest, ReturnRequestAdmin)



from django.contrib import admin
from .models import EcommerceItem

class EcommerceItemAdmin(admin.ModelAdmin):
    list_display = ('item', 'min_order_quantity', 'size', 'weight', 'is_returnable', 'status')
    list_filter = ('status', 'is_returnable')
    search_fields = ('item__description', 'item__manufacturer_sku', 'item__system_sku')

admin.site.register(EcommerceItem, EcommerceItemAdmin)
