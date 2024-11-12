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
from .models import Order
from .views import custom_order_list_view, custom_order_detail_view

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'status', 'created_at', 'updated_at', 'view_order')

    def view_order(self, obj):
        return format_html('<a href="{}">View</a>', reverse('ecommerce:admin_order_detail', args=[obj.id]))
    view_order.short_description = "Order Details"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('orders/', self.admin_site.admin_view(custom_order_list_view), name='admin_order_list'),
            path('orders/<int:order_id>/', self.admin_site.admin_view(custom_order_detail_view), name='admin_order_detail'),
        ]
        return custom_urls + urls

admin.site.register(Order, OrderAdmin)


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
