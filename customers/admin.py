from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Customer, Address

class AddressInline(admin.TabularInline):  # Use TabularInline for a table-like layout
    model = Address
    extra = 1  # Number of empty forms to display for new addresses
    fields = ('street', 'city', 'province', 'postal_code', 'country')  # Fields to display in the inline form

class CustomCustomerAdmin(UserAdmin):
    model = Customer
    list_display = ('email', 'phone_number', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'customer_type')
    fieldsets = (
        (None, {'fields': ('email', 'phone_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'company_name', 'additional_emails', 'customer_type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'phone_number', 'first_name', 'last_name')
    ordering = ('email',)
    inlines = [AddressInline]  # Add the AddressInline to allow address editing inline

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('customer', 'street', 'city', 'province', 'postal_code', 'country')
    search_fields = ('customer__email', 'street', 'city', 'province', 'postal_code', 'country')

# Register the CustomerAdmin with the modified inline
admin.site.register(Customer, CustomCustomerAdmin)
