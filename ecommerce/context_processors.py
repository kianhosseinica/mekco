from .models import Cart
from decimal import Decimal, ROUND_HALF_UP


def cart_summary(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(customer=request.user, completed=False)
            cart_items = cart.cartitem_set.all()

            if cart_items.exists():
                total_price = sum((item.price * item.quantity) for item in cart_items).quantize(Decimal('0.01'),
                                                                                                rounding=ROUND_HALF_UP)
                total_discount = sum(
                    (item.item.price_default - item.price) * item.quantity for item in cart_items).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP)

                hst_rate = Decimal('0.13')
                hst = (total_price * hst_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                total_price_with_hst = (total_price + hst).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                return {
                    'cart_items': cart_items,
                    'total_price': total_price,
                    'total_discount': total_discount,
                    'hst': hst,
                    'total_price_with_hst': total_price_with_hst,
                }
            else:
                return {}
        except Cart.DoesNotExist:
            return {}
    return {}
