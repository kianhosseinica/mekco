from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, SetPasswordForm
from .models import Customer, Address

class CustomerSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    company_name = forms.CharField(required=False)  # Make this field optional
    additional_emails = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="Enter additional emails separated by commas."
    )
    street = forms.CharField(required=False)
    city = forms.CharField(required=False)
    province = forms.CharField(required=False)
    postal_code = forms.CharField(required=False)
    country = forms.CharField(required=False)

    class Meta(UserCreationForm.Meta):
        model = Customer
        fields = (
            'email',
            'phone_number',
            'first_name',
            'last_name',
            'company_name',
            'additional_emails',
            'street',
            'city',
            'province',
            'postal_code',
            'country',
            'password1',
            'password2'
        )


class CustomerLoginForm(forms.Form):
    email_or_phone = forms.CharField(label="Email or Phone number")
    password = forms.CharField(widget=forms.PasswordInput)

class CustomerProfileForm(UserChangeForm):
    additional_emails = forms.CharField(widget=forms.Textarea, required=False, help_text="Enter additional emails separated by commas.")

    class Meta:
        model = Customer
        fields = ('email', 'phone_number', 'first_name', 'last_name', 'company_name', 'additional_emails', 'customer_type')
        widgets = {
            'customer_type': forms.HiddenInput()
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'city', 'province', 'postal_code', 'country']

class AdminCustomerTypeForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('customer_type',)

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label="Email", max_length=254)

class CustomSetPasswordForm(SetPasswordForm):
    pass
