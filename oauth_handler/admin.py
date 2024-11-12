from sqlite3 import IntegrityError

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from .models import *
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
class PriceRecordInline(admin.TabularInline):
    model = PriceRecord
    extra = 1  # How many rows to show

class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 1  # How many rows to show
    readonly_fields = ['image_tag']

    def image_tag(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="150" height="150" />'.format(obj.image_url))
        return ""

    image_tag.short_description = 'Image'


from django.urls import path
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import admin
from .models import Item
from .forms import VariantForm  # You will create this form


from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        'description', 'system_sku', 'manufacturer_sku', 'price_default',
        'average_cost', 'vendor', 'brand', 'tax_class', 'parent_item'
    )
    search_fields = ('description', 'manufacturer_sku', 'system_sku')
    list_filter = ('vendor', 'brand', 'tax_class', 'category')

    inlines = [PriceRecordInline, ItemImageInline]

    fields = (
        'description', 'system_sku', 'manufacturer_sku', 'default_cost', 'average_cost',
        'quantity_on_hand', 'reorder_point', 'reorder_level', 'category', 'vendor', 'brand',
        'tax_class', 'price_default', 'price_msrp', 'price_online', 'discounted_price',
        'min_order_quantity', 'is_returnable', 'status',
        'has_bag_option', 'bag_quantity', 'bag_discount_percentage',
        'has_box_option', 'box_quantity', 'box_discount_percentage',
        'parent_item','weight', 'length', 'width', 'height','price_category_multiplier',
    )

    def save_model(self, request, obj, form, change):
        """
        Override save_model to calculate prices using price_category_multiplier and handle
        the creation of bag and box variants only if they do not already exist.
        """
        # Calculate prices using the multiplier if it's set
        if obj.price_category_multiplier:
            multiplier = obj.price_category_multiplier.multiplier
            obj.price_default = obj.default_cost * multiplier
            obj.price_msrp = obj.default_cost * multiplier
            obj.price_online = obj.default_cost * multiplier

        # Save the original item first
        super().save_model(request, obj, form, change)

        # Handle bag variant creation
        if obj.has_bag_option and obj.bag_quantity:
            bag_sku = f"{obj.system_sku}-Bag-{obj.bag_quantity}"
            print(f"Processing Bag SKU: {bag_sku}")

            # Check if the bag variant already exists
            if not Item.objects.filter(manufacturer_sku=bag_sku).exists():
                bag_description = f"(Bag of {obj.bag_quantity}) {obj.description}"
                price_per_item = obj.discounted_price if obj.discounted_price > 0 else obj.price_default
                bag_price = (price_per_item * obj.bag_quantity) * (1 - (obj.bag_discount_percentage or 0) / 100)
                bag_default_cost = obj.default_cost * obj.bag_quantity

                try:
                    Item.objects.create(
                        description=bag_description,
                        manufacturer_sku=bag_sku,
                        system_sku=f"{obj.system_sku}-Bag",  # Ensure unique system_sku
                        default_cost=bag_default_cost,
                        average_cost=obj.average_cost,
                        quantity_on_hand=obj.quantity_on_hand,
                        reorder_point=obj.reorder_point,
                        reorder_level=obj.reorder_level,
                        category=obj.category,
                        vendor=obj.vendor,
                        brand=obj.brand,
                        tax_class=obj.tax_class,
                        price_default=bag_price,
                        price_msrp=obj.price_msrp,
                        price_online=obj.price_online,
                        discounted_price=0,
                        min_order_quantity=obj.bag_quantity,
                        is_returnable=obj.is_returnable,
                        status=obj.status,
                        parent_item=obj
                    )
                except IntegrityError as e:
                    print(f"Error creating bag variant: {e}")
            else:
                print(f"Bag SKU {bag_sku} already exists. Skipping creation.")

        # Handle box variant creation
        if obj.has_box_option and obj.box_quantity:
            box_sku = f"{obj.system_sku}-Box-{obj.box_quantity}"
            print(f"Processing Box SKU: {box_sku}")

            # Check if the box variant already exists
            if not Item.objects.filter(manufacturer_sku=box_sku).exists():
                box_description = f"(Box of {obj.box_quantity}) {obj.description}"
                price_per_item = obj.discounted_price if obj.discounted_price > 0 else obj.price_default
                box_price = (price_per_item * obj.box_quantity) * (1 - (obj.box_discount_percentage or 0) / 100)
                box_default_cost = obj.default_cost * obj.box_quantity

                try:
                    Item.objects.create(
                        description=box_description,
                        manufacturer_sku=box_sku,
                        system_sku=f"{obj.system_sku}-Box",  # Ensure unique system_sku
                        default_cost=box_default_cost,
                        average_cost=obj.average_cost,
                        quantity_on_hand=obj.quantity_on_hand,
                        reorder_point=obj.reorder_point,
                        reorder_level=obj.reorder_level,
                        category=obj.category,
                        vendor=obj.vendor,
                        brand=obj.brand,
                        tax_class=obj.tax_class,
                        price_default=box_price,
                        price_msrp=obj.price_msrp,
                        price_online=obj.price_online,
                        discounted_price=0,
                        min_order_quantity=obj.box_quantity,
                        is_returnable=obj.is_returnable,
                        status=obj.status,
                        parent_item=obj
                    )
                except IntegrityError as e:
                    print(f"Error creating box variant: {e}")
            else:
                print(f"Box SKU {box_sku} already exists. Skipping creation.")







admin.site.register(Vendor)
admin.site.register(Brand)
admin.site.register(TaxClass)
admin.site.register(Category)
from django.contrib import admin
from .models import CustomerLightspeed

class CustomerLightspeedAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone')  # Ensure these fields exist in your model
    search_fields = ('first_name', 'last_name', 'email', 'phone')

admin.site.register(CustomerLightspeed, CustomerLightspeedAdmin)

@admin.register(PriceCategoryMultiplier)
class PriceCategoryMultiplierAdmin(admin.ModelAdmin):
    list_display = ('category', 'multiplier')  # Customize this as needed
    search_fields = ('category__name',)  # Enable searching by category name