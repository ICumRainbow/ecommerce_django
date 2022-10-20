from django.db.models import Sum
from django.contrib import messages

from customer.models import Order, LikedProducts, OrderItems
from products.filters import ProductFilter
from products.models import Category, Product
from customer.forms import EmailSubForm


def retrieve_cart_items(request):
    customer = request.user.id
    session_id = request.session.session_key
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer_id=customer, completed=False)
        order.session_id = session_id
        order.save()
    else:
        order, created = Order.objects.get_or_create(session_id=session_id, completed=False)

    order_items_qs = OrderItems.objects.filter(order=order).select_related('product').only('quantity', 'product', 'product__price')
    cart_items = order_items_qs.aggregate(Sum('quantity'))
    order_items = order_items_qs.only('product', 'quantity')
    order_total = 0
    for item in order_items:
        order_total += float(item.product.current_price * item.quantity)
    context = {
        'cart_items': cart_items['quantity__sum'] or 0,
        'order_total': order_total,
    }

    return context


def retrieve_liked_products(request):
    customer = request.user.id
    session_id = request.session.session_key
    if request.user.is_authenticated:
        liked_products_count = LikedProducts.objects.filter(customer_id=customer).count()
    else:
        liked_products_count = LikedProducts.objects.filter(session_id=session_id).count()

    context = {
        'liked_products': liked_products_count
    }
    return context


# def retrieve_filter_form(request):
#     filtered_products = ProductFilter(
#         request.GET,
#         queryset=Product.objects.all()
#     )
#     context = {
#         'filtered_products': filtered_products,
#     }
#     return context


def retrieve_categories(request):
    categories_list = Category.objects.only('name', 'id', 'image').select_related()

    context = {
        'categories': categories_list,
    }

    return context


def email_sub(request):
    email_sub_form = EmailSubForm(request.POST)
    if request.method == 'POST' and 'email' in request.POST:
        if email_sub_form.is_valid():
            email_sub_form.save()
            messages.success(request, "Thank you for subscribing to our email newsletter!")
        else:
            messages.success(request, "Something went wrong, please try again!")
            print(email_sub_form.errors.as_data)

    context = {
        'email_form': email_sub_form,
    }
    return context
