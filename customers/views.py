from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from .models import Customer, Address
from .forms import CustomerSignupForm, CustomerLoginForm, CustomerProfileForm, AddressForm, AdminCustomerTypeForm, CustomPasswordResetForm, CustomSetPasswordForm

def signup_view(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('customers:profile')
    if request.method == 'POST':
        form = CustomerSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account until email confirmation
            additional_emails = form.cleaned_data['additional_emails']
            user.additional_emails = [email.strip() for email in additional_emails.split(',') if email.strip()]
            user.save()
            Address.objects.create(
                customer=user,
                street=form.cleaned_data['street'],
                city=form.cleaned_data['city'],
                province=form.cleaned_data['province'],
                postal_code=form.cleaned_data['postal_code'],
                country=form.cleaned_data['country']
            )
            send_verification_email(request, user)
            messages.success(request, 'Account created successfully! Please check your email to activate your account.')
            return redirect('customers:login')
        else:
            # Form is not valid, so pass form errors to the template
            messages.error(request, "There was an error with your submission. Please correct the errors below.")
    else:
        form = CustomerSignupForm()

    return render(request, 'customers/signup.html', {'form': form})


from django.http import JsonResponse
from django.contrib.auth import authenticate, login

from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.contrib import messages
from .forms import CustomerLoginForm
from django.http import JsonResponse

from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.contrib import messages
from .forms import CustomerLoginForm

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.contrib import messages
from .forms import CustomerLoginForm

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages


def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('customers:profile')
    if request.method == 'POST':
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            email_or_phone = form.cleaned_data['email_or_phone']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email_or_phone, password=password)
            if user is not None:
                login(request, user)
                return redirect('customers:profile')
            else:
                # Let django-axes display the error if the user is locked out due to failed attempts
                messages.error(request,
                               'Invalid email/phone number or password, or your account may be temporarily locked.')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomerLoginForm()

    return render(request, 'customers/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('customers:login')

@login_required
def profile_view(request):
    if request.method == 'POST':
        profile_form = CustomerProfileForm(request.POST, instance=request.user)
        address_form = AddressForm(request.POST, instance=request.user.addresses.first())
        if profile_form.is_valid() and address_form.is_valid():
            profile_form.save()
            additional_emails = profile_form.cleaned_data['additional_emails']
            request.user.additional_emails = [email.strip() for email in additional_emails.split(',') if email.strip()]
            request.user.save()
            address_form.save()
            messages.success(request, 'Profile updated successfully!')
    else:
        profile_form = CustomerProfileForm(instance=request.user)
        address_form = AddressForm(instance=request.user.addresses.first())
    return render(request, 'customers/profile.html', {'profile_form': profile_form, 'address_form': address_form})

@user_passes_test(lambda u: u.is_staff)
@login_required
def admin_assign_customer_type_view(request):
    if request.method == 'POST':
        form = AdminCustomerTypeForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, 'Customer type assigned successfully!')
            return redirect('admin_assign_customer_type')
    else:
        form = AdminCustomerTypeForm()
    return render(request, 'customers/admin_assign_customer_type.html', {'form': form})


from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator

from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator


def send_verification_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    domain = request.get_host()

    # Generate the activation link
    activate_url = reverse('customers:activate', kwargs={'uidb64': uid, 'token': token})
    full_activate_url = f'http://{domain}{activate_url}'

    email_subject = 'Activate Your Account'

    # Use external logo URL
    logo_url = 'https://www.mekcosupply.com/wp-content/uploads/2020/07/Mekco-Supply-logo-300-pix-2020.jpg'

    # Render HTML email content
    email_html_content = render_to_string('customers/activation_email.html', {
        'user': user,
        'activate_url': full_activate_url,
        'logo_url': logo_url
    })

    # Plain text content as a fallback
    email_text_content = (
        f"Hello {user.email},\n\n"
        f"Please click the following link to activate your account:\n{full_activate_url}\n\n"
        "If you did not request this, please ignore this email.\n\n"
        "Thank you!"
    )

    # Create the email and attach the HTML alternative
    email = EmailMultiAlternatives(
        subject=email_subject,
        body=email_text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    email.attach_alternative(email_html_content, "text/html")
    email.send()


def activate_view(request, uidb64, token):
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = Customer.objects.get(pk=uid)

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Account activated successfully!')
        return redirect('customers:login')
    else:
        messages.error(request, 'Activation link is invalid!')
        return redirect('customers:signup')


from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CustomPasswordResetForm, CustomSetPasswordForm
from .models import Customer


from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Customer
from .forms import CustomPasswordResetForm


from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.templatetags.static import static
from django.conf import settings

from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.contrib import messages

def password_reset_request_view(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = Customer.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                domain = request.get_host()
                reset_url = reverse('customers:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                full_reset_url = f'http://{domain}{reset_url}'

                email_subject = 'Reset Your Password'

                # Use the external URL for the logo
                logo_url = 'https://www.mekcosupply.com/wp-content/uploads/2020/07/Mekco-Supply-logo-300-pix-2020.jpg'

                # Render HTML email content
                email_html_content = render_to_string('customers/password_reset_email.html', {
                    'user': user,
                    'reset_url': full_reset_url,
                    'logo_url': logo_url  # Pass the logo URL to the template
                })

                # Plain text content as a fallback
                email_text_content = (
                    f"Hello {user.email},\n\n"
                    f"Please use the following link to reset your password:\n{full_reset_url}\n\n"
                    f"If you did not request a password reset, please ignore this email.\n\n"
                    "Thank you!"
                )

                # Create the email and attach the HTML alternative
                email = EmailMultiAlternatives(
                    subject=email_subject,
                    body=email_text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email]
                )
                email.attach_alternative(email_html_content, "text/html")
                email.send()

                messages.success(request, 'Password reset email has been sent.')
                return redirect('customers:login')
            except Customer.DoesNotExist:
                messages.error(request, 'No account is associated with this email.')
    else:
        form = CustomPasswordResetForm()
    return render(request, 'customers/password_reset.html', {'form': form})




def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Customer.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Customer.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Password has been reset successfully.')
                return redirect('customers:login')
        else:
            form = CustomSetPasswordForm(user)
        return render(request, 'customers/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'The reset link is invalid or has expired.')
        return redirect('customers:password_reset')



# customers/views.py

# customers/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from ecommerce.models import Order

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from ecommerce.models import Order
from .forms import CustomerProfileForm, AddressForm

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from ecommerce.models import Order
from .forms import CustomerProfileForm, AddressForm

@login_required
def profile_view(request):
    if request.method == 'POST':
        profile_form = CustomerProfileForm(request.POST, instance=request.user)
        address_form = AddressForm(request.POST, instance=request.user.addresses.first())
        if profile_form.is_valid() and address_form.is_valid():
            profile_form.save()
            additional_emails = profile_form.cleaned_data['additional_emails']
            request.user.additional_emails = [email.strip() for email in additional_emails.split(',') if email.strip()]
            request.user.save()
            address_form.save()
            messages.success(request, 'Profile updated successfully!')
    else:
        profile_form = CustomerProfileForm(instance=request.user)
        address_form = AddressForm(instance=request.user.addresses.first())

    orders = Order.objects.filter(customer=request.user).order_by('-created_at')

    return render(request, 'customers/profile.html', {
        'profile_form': profile_form,
        'address_form': address_form,
        'orders': orders,
    })

@login_required
def order_history_view(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'customers/order_history.html', {'orders': orders})



from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from ecommerce.models import Order, OrderItem, ReturnRequest
from django.db.models import Sum


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return_requests = order.return_requests.all()
    today = timezone.now().date()

    items_with_return_status = []
    total_refund_amount = Decimal('0.00')
    return_subtotal = Decimal('0.00')
    return_hst = Decimal('0.00')
    return_restocking_fee = Decimal('0.00')

    subtotal = order.subtotal
    total_discount = order.total_discount
    hst = order.hst
    total_price_with_hst = order.total_with_hst
    total_with_hst_and_shipping = order.total_with_hst_and_shipping

    for order_item in order.items.all():
        original_price = order_item.original_price
        discounted_price = order_item.discounted_price
        item_total_price = order_item.total_price
        discount = order_item.discount

        # Check if the item is returnable directly from the Item model
        is_returnable = getattr(order_item.item, 'is_returnable', False)
        within_return_window = (today - order.created_at.date()).days <= 30

        # Calculate the total quantity that has been returned for this item
        total_returned_quantity = return_requests.filter(item=order_item.item).aggregate(total_returned=Sum('quantity'))['total_returned'] or 0
        # Calculate the remaining quantity available for return
        remaining_quantity = max(order_item.quantity - total_returned_quantity, 0)

        return_request = return_requests.filter(item=order_item.item).first()

        if return_request and return_request.status == 'approved':
            total_refund_amount += return_request.refund_amount

        items_with_return_status.append({
            'item': order_item,
            'status': return_request.get_status_display() if return_request else 'N/A',
            'denied_reason': return_request.denied_reason if return_request else '',
            'can_return': is_returnable and within_return_window and remaining_quantity > 0,
            'total_returned_quantity': total_returned_quantity,
            'price': discounted_price,
            'refund_amount': return_request.refund_amount if return_request else Decimal('0.00'),
            'remaining_quantity': remaining_quantity,
            'original_price': original_price,
            'discounted_price': discounted_price,
            'discount': discount,
            'total_price': item_total_price,

        })

    context = {
        'order': order,
        'items_with_return_status': items_with_return_status,
        'total_refund_amount': total_refund_amount,
        'return_subtotal': return_subtotal,
        'return_hst': return_hst,
        'return_restocking_fee': return_restocking_fee,
        'total_discount': total_discount,
        'subtotal': subtotal,
        'hst': hst,
        'total_price_with_hst': total_price_with_hst,
        'total_with_hst_and_shipping':total_with_hst_and_shipping,
    }

    return render(request, 'customers/order_detail.html', context)

































import logging
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from ecommerce.models import OrderItem, ReturnRequest

# Initialize logger
logger = logging.getLogger(__name__)


@login_required
def request_return_view(request, order_item_id):
    # Ensure that the OrderItem exists and belongs to the current user's order
    order_item = get_object_or_404(OrderItem, id=order_item_id, order__customer=request.user)

    order = order_item.order
    item_instance = order_item.item  # We are now using the `Item` model directly

    # Assume `is_returnable` is a field in the `Item` model
    if not item_instance.is_returnable:
        messages.error(request, "This item is not returnable.")
        return redirect('customers:order_detail', order_id=order.id)

    # Check if the return window (e.g., 30 days) is still valid
    if (timezone.now().date() - order.created_at.date()).days > 30:
        messages.error(request, "Return window has expired.")
        return redirect('customers:order_detail', order_id=order.id)

    # Calculate the remaining quantity that can be returned
    total_returned_quantity = order.return_requests.filter(item=item_instance, status__in=['approved', 'pending']).aggregate(
        total_returned=Sum('quantity'))['total_returned'] or 0
    remaining_quantity = order_item.quantity - total_returned_quantity

    if remaining_quantity <= 0:
        messages.error(request, "You have already returned the maximum quantity for this item.")
        return redirect('customers:order_detail', order_id=order.id)

    if request.method == 'POST':
        return_quantity = int(request.POST.get('return_quantity', 0))

        if return_quantity > remaining_quantity:
            messages.error(request, f"You can only return up to {remaining_quantity} more of this item.")
            return redirect('customers:order_detail', order_id=order.id)

        # Determine which price to use for the refund calculation
        price_per_item = order_item.discounted_price if order_item.discount > 0 else order_item.original_price

        # Calculate refund details for the returned quantity
        total_item_price = price_per_item * return_quantity
        refund_hst = total_item_price * Decimal('0.13')
        refund_subtotal = total_item_price + refund_hst
        restocking_fee = refund_subtotal * Decimal('0.10')
        refund_amount = refund_subtotal - restocking_fee

        # Create the return request and save the refund details
        ReturnRequest.objects.create(
            order=order,
            item=item_instance,
            quantity=return_quantity,
            status='pending',  # or 'approved' if auto-approving
            denied_reason='',  # Only fill if applicable
            refund_amount=refund_amount,  # Store calculated refund amount
        )

        messages.success(request, "Return request submitted. Waiting for admin approval.")
        return redirect('customers:order_detail', order_id=order.id)

    return redirect('customers:order_detail', order_id=order.id)






