from django import forms
from .models import *

class PasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)


class ItemSearchForm(forms.Form):
    query = forms.CharField(label='Search for Items by SKU or Description', max_length=255)

class QuoteItemForm(forms.ModelForm):
    class Meta:
        model = QuoteItem
        fields = ['item', 'quantity', 'price']
        widgets = {
            'item': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Assuming 'item' field is a hidden input, you would typically not need to handle it directly in the form,
        # but rather set it in the view based on a search selection.
        self.fields['quantity'].widget.attrs.update({'min': 1})
        self.fields['price'].widget.attrs.update({'step': '0.01'})

from django import forms

from django import forms

from django import forms

class EmailForm(forms.Form):
    recipient = forms.EmailField(label='Recipient Email')
    subject = forms.CharField(max_length=100, label='Subject')
    message = forms.CharField(widget=forms.Textarea, label='Message')



from django import forms
from .models import Item

class VariantForm(forms.ModelForm):
    VARIANT_CHOICES = [
        ('bag', 'Bag'),
        ('box', 'Box'),
    ]

    variant_type = forms.ChoiceField(choices=VARIANT_CHOICES)
    quantity = forms.IntegerField()
    discount_percentage = forms.DecimalField(max_digits=5, decimal_places=2, required=False)

    class Meta:
        model = Item
        fields = ['quantity', 'discount_percentage']




from django import forms

class SMSForm(forms.Form):
    phone_number = forms.CharField(
        label="Phone Number",
        max_length=15,
        widget=forms.TextInput(attrs={"placeholder": "+1234567890"})
    )
    message = forms.CharField(
        label="Message",
        max_length=160,
        widget=forms.Textarea(attrs={"placeholder": "Enter your message here", "rows": 3})
    )
