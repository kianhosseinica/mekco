# # utils.py
# from customers.models import Customer
# from django.shortcuts import get_object_or_404
#
# def get_discounted_price(item, user_or_pricing_rule):
#     if hasattr(user_or_pricing_rule, 'is_authenticated'):
#         user = user_or_pricing_rule
#         if not user.is_authenticated:
#             return item.price_default
#         customer = get_object_or_404(Customer, email=user.email)
#         customer_type = customer.customer_type
#     else:
#         customer_type = user_or_pricing_rule.customer_type
#
#     try:
#         pricing_rule = PricingRule.objects.get(
#             customer_type=customer_type,
#             category__in=item.category.get_ancestors(include_self=True)
#         )
#         discount = (pricing_rule.discount_percentage / 100) * item.price_default
#         return round(item.price_default - discount, 2)
#     except PricingRule.DoesNotExist:
#         return item.price_default
