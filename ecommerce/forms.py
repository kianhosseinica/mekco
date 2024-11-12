# ecommerce/forms.py

from django import forms
from .models import CartItem, Order

from django import forms
from .models import CartItem, Order

# ecommerce/forms.py

from django import forms
from .models import CartItem


from django import forms
from .models import CartItem

class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']

    def __init__(self, *args, **kwargs):
        self.item = kwargs.pop('item', None)
        super().__init__(*args, **kwargs)

        if self.item:
            self.fields['quantity'].widget.attrs.update({
                'max': self.item.quantity_on_hand,
                'min': self.item.min_order_quantity,
            })
            self.fields['quantity'].initial = self.item.min_order_quantity

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if self.item and quantity > self.item.quantity_on_hand:
            raise forms.ValidationError(
                f'Quantity exceeds available stock. Only {self.item.quantity_on_hand} left in stock.')
        return quantity











class UpdateCartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_option', 'street', 'city', 'province', 'postal_code', 'country']

    def clean(self):
        cleaned_data = super().clean()
        delivery_option = cleaned_data.get('delivery_option')
        street = cleaned_data.get('street')
        city = cleaned_data.get('city')
        province = cleaned_data.get('province')
        postal_code = cleaned_data.get('postal_code')
        country = cleaned_data.get('country')

        # Only require address fields if the delivery option is "shipping"
        if delivery_option == 'shipping' and not (street and city and province and postal_code and country):
            self.add_error('street', 'Street address is required for shipping option.')
            self.add_error('city', 'City is required for shipping option.')
            self.add_error('province', 'Province is required for shipping option.')
            self.add_error('postal_code', 'Postal code is required for shipping option.')
            self.add_error('country', 'Country is required for shipping option.')

        return cleaned_data


from oauth_handler.models import Category, Item

from django import forms
from .models import PricingRule

from django import forms
from .models import PricingRule
from oauth_handler.models import Category

class PricingRuleForm(forms.ModelForm):
    parent_category = forms.ModelChoiceField(queryset=Category.objects.filter(parent=None), required=False)
    subcategory = forms.ModelChoiceField(queryset=Category.objects.none(), required=False)

    class Meta:
        model = PricingRule
        fields = ['customer_type', 'category', 'discount_percentage']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                category = Category.objects.get(id=category_id)
                if category.parent:
                    self.fields['parent_category'].queryset = Category.objects.filter(id=category.parent_id)
                self.fields['subcategory'].queryset = category.children.all()
            except (ValueError, TypeError, Category.DoesNotExist):
                pass
        elif self.instance.pk:
            category = self.instance.category
            if category.parent:
                self.fields['parent_category'].queryset = Category.objects.filter(id=category.parent_id)
            self.fields['subcategory'].queryset = category.children.all()






from django import forms
from .models import Order

class BulkActionForm(forms.Form):
    ACTION_CHOICES = [
        ('', 'Choose an action...'),
        ('delete', 'Delete selected orders'),
        ('mark_as_ready_for_pickup', 'Mark as Ready for Pickup'),
        ('mark_as_shipped', 'Mark as Shipped'),
        # Add more actions as needed
    ]
    action = forms.ChoiceField(choices=ACTION_CHOICES, required=True)
    selected_orders = forms.ModelMultipleChoiceField(queryset=Order.objects.all(), widget=forms.CheckboxSelectMultiple)

class StatusChangeForm(forms.Form):
    # No fields needed; we only need this for CSRF protection
    pass



# class ItemForm(forms.ModelForm):
#     add_bag = forms.BooleanField(required=False)
#     add_box = forms.BooleanField(required=False)
#     bag_quantity = forms.IntegerField(required=False, min_value=1)
#     box_quantity = forms.IntegerField(required=False, min_value=1)
#     bag_discount_percentage = forms.DecimalField(required=False, max_value=100, min_value=0)
#     box_discount_percentage = forms.DecimalField(required=False, max_value=100, min_value=0)
#
#     class Meta:
#         model = Item
#         fields = ['name', 'manufacturer_sku', 'original_price', 'discounted_price', 'add_bag', 'add_box',
#                   'bag_quantity', 'box_quantity', 'bag_discount_percentage', 'box_discount_percentage']