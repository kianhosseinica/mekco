from decimal import Decimal
from sqlite3 import IntegrityError
from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

class Vendor(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=[('public', 'Public'), ('private', 'Private')], default='public')
    def __str__(self):
        return self.name


class TaxClass(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name


class Category(models.Model):
    category_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    node_depth = models.IntegerField(default=0)
    full_path_name = models.CharField(max_length=255)
    left_node = models.IntegerField()
    right_node = models.IntegerField()
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    create_time = models.DateTimeField()
    last_modified = models.DateTimeField()
    status = models.CharField(max_length=10, choices=[('public', 'Public'), ('private', 'Private')], default='public')

    # New field for image
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)

    def __str__(self):
        return self.name

    def get_descendants(self):
        descendants = set()
        children = self.children.all()
        for child in children:
            descendants.add(child)
            descendants.update(child.get_descendants())
        return descendants

    def get_ancestors(self, include_self=False):
        ancestors = []
        category = self
        if include_self:
            ancestors.append(category)
        while category.parent is not None:
            ancestors.append(category.parent)
            category = category.parent
        return ancestors[::-1]  # Reverse the list to get the correct order

    # New method to get the category image URL or return a default image
    def get_image_url(self):
        if self.image:
            return self.image.url
        else:
            return '/static/images/default.jpg'  # Path to your default image




class Item(models.Model):
    description = models.TextField()
    system_sku = models.CharField(max_length=255)
    manufacturer_sku = models.CharField(max_length=255, unique=True)
    default_cost = models.DecimalField(max_digits=10, decimal_places=2)
    average_cost = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_on_hand = models.IntegerField()
    reorder_point = models.IntegerField(default=0, verbose_name="Reorder Point")
    reorder_level = models.IntegerField(default=0, verbose_name="Reorder Level")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    tax_class = models.ForeignKey(TaxClass, on_delete=models.SET_NULL, null=True)
    price_default = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_msrp = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_online = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    itemID = models.IntegerField(unique=True, null=True)
    status = models.CharField(max_length=10, choices=[('public', 'Public'), ('private', 'Private')], default='public')
    min_order_quantity = models.IntegerField(default=1)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_returnable = models.BooleanField(default=True)
    # Dimensions fields for bulky or large items (in inches)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, help_text="Weight in pounds (lbs)")


    length = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Length in inches")
    width = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Width in inches")
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Height in inches")

    # Fields for enabling bag and box options
    has_bag_option = models.BooleanField(default=False)
    has_box_option = models.BooleanField(default=False)
    bag_quantity = models.PositiveIntegerField(null=True, blank=True)
    bag_discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    box_quantity = models.PositiveIntegerField(null=True, blank=True)
    box_discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Field to link bag/box variants back to the base (single) item
    parent_item = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='variants')

    price_category_multiplier = models.ForeignKey(
        'PriceCategoryMultiplier',  # Use a string here to avoid circular import issues
        on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Choose price category multiplier for automatic price calculation"
    )

    def save(self, *args, **kwargs):
        if self.price_category_multiplier:
            self.price_default = self.default_cost * self.price_category_multiplier.multiplier
            self.price_msrp = self.default_cost * self.price_category_multiplier.multiplier
            self.price_online = self.default_cost * self.price_category_multiplier.multiplier

        super().save(*args, **kwargs)
    # Calculating the price for bag items
    def calculate_bag_price(self):
        if self.has_bag_option and self.bag_quantity:
            price_per_item = self.discounted_price if self.discounted_price > 0 else self.price_default
            discount = (price_per_item * Decimal(self.bag_discount_percentage or 0) / 100)
            return (price_per_item - discount) * Decimal(self.bag_quantity or 1)
        return None

    # Calculating the price for box items
    def calculate_box_price(self):
        if self.has_box_option and self.box_quantity:
            price_per_item = self.discounted_price if self.discounted_price > 0 else self.price_default
            discount = (price_per_item * Decimal(self.box_discount_percentage or 0) / 100)
            return (price_per_item - discount) * Decimal(self.box_quantity or 1)
        return None

    # Helper method to get the base item
    def get_base_item(self):
        return self.parent_item if self.parent_item else self

    # Helper method to get the bag variant
    def get_bag_variant(self):
        return self.variants.filter(has_bag_option=True).first()

    # Helper method to get the box variant
    def get_box_variant(self):
        return self.variants.filter(has_box_option=True).first()

    # Overriding the save method to ensure SKU uniqueness and handle variants
    def save(self, *args, **kwargs):
        # Ensure we're creating new SKU for variants
        if not self.pk:  # This check ensures that this logic only applies on creation (not on updates)
            # Handle bag variant SKU creation
            if self.has_bag_option and self.bag_quantity:
                self.manufacturer_sku = f"{self.system_sku}-Bag-{self.bag_quantity}"
            # Handle box variant SKU creation
            elif self.has_box_option and self.box_quantity:
                self.manufacturer_sku = f"{self.system_sku}-Box-{self.box_quantity}"

            # Ensure no duplicate SKUs
            if Item.objects.filter(manufacturer_sku=self.manufacturer_sku).exists():
                raise ValidationError(f"An item with the SKU {self.manufacturer_sku} already exists. Please ensure the SKU is unique.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} - {self.manufacturer_sku}"

    # Method to get the item's image URL or default image
    def get_image_url(self):
        if self.images.exists():
            return self.images.first().image_url
        else:
            return '/static/images/default.jpg'  # Path to the default image






class ItemImage(models.Model):
    item = models.ForeignKey(Item, related_name='images', on_delete=models.CASCADE)
    image_url = models.URLField()
    image_path = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.image_url



class PriceRecord(models.Model):
    item = models.ForeignKey(Item, related_name='price_records', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=5, default=0.00)
    currency = models.CharField(max_length=3, choices=(('USD', 'US Dollars'), ('CAD', 'Canadian Dollars')))
    record_date = models.DateField(default=timezone.now)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.item.manufacturer_sku} - {self.currency} {self.price} on {self.record_date}"


class Quote(models.Model):
    quote_number = models.CharField(max_length=255, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.quote_number:
            date_str = timezone.now().strftime('%Y%m%d%H%M%S')
            success = False
            attempts = 0
            while not success and attempts < 10:
                try:
                    with transaction.atomic():
                        suffix = Quote.objects.filter(quote_number__startswith=f'MQRIC-{date_str}').count()
                        self.quote_number = f'MQRIC-{date_str}-{suffix + 1}'
                        super(Quote, self).save(*args, **kwargs)
                        success = True
                except IntegrityError:
                    attempts += 1
                    continue
        else:
            super(Quote, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.quote_number}"


class QuoteItem(models.Model):
    quote = models.ForeignKey(Quote, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.item.description} - {self.quantity}"


class CustomerLightspeed(models.Model):
    customer_id = models.CharField(max_length=50)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    company = models.CharField(max_length=255, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(blank=True)
    archived = models.BooleanField(default=False)
    create_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company}"


class PriceCategoryMultiplier(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    multiplier = models.DecimalField(max_digits=5, decimal_places=2, help_text="Multiplier for price calculation")

    def __str__(self):
        return f"{self.category.name} - x{self.multiplier}"