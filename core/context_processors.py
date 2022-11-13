from django.contrib import messages
from django.db.models import Sum, F

from core.services import get_query_params, annotate_with_discount_prices
from customer.forms import EmailSubForm
from customer.models import Order, LikedProduct, OrderItem
from products.filters import ProductFilter
from products.models import Category, Product


def retrieve_cart_items(request):
    """
    Retrieves number of items in the cart and their total price.
    """
    customer = request.user.id
    session_id = request.session.session_key
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer_id=customer, completed=False)
        order.session_id = session_id
        order.save()
    else:
        order, created = Order.objects.get_or_create(session_id=session_id, completed=False)

    order_items_query = OrderItem.objects.filter(order=order)
    order_total_query = annotate_with_discount_prices(order_items_query)
    order_total_query = order_total_query.annotate(
        total_price=F('discount_price') * F('quantity'),
    ).aggregate(overall_price=Sum('total_price'))

    order_total = order_total_query['overall_price']
    items_count_query = order_items_query.aggregate(count=Sum('quantity'))
    items_count = items_count_query['count']
    context = {
        'cart_items': items_count or 0,
        'order_total': order_total or 0,
    }

    return context


def retrieve_liked_products(request):
    """
    Retrieves number of liked products.
    """
    customer_id = request.user.id
    session_id = request.session.session_key

    query_kwargs = {'customer_id': customer_id} if request.user.is_authenticated else {'session_id': session_id}
    liked_products_count = LikedProduct.objects.filter(**query_kwargs).count()

    return {'liked_products': liked_products_count}


def retrieve_filter_form(request):
    """
    Retrieves form to search for products.
    """
    query_params = get_query_params(request)
    filtered_products = ProductFilter(request.GET, queryset=Product.objects.filter(**query_params))

    return {'filtered_products': filtered_products}


def retrieve_categories(request):
    """
    Retrieves list of categories.
    """
    categories_list = Category.objects.all()

    return {'categories': categories_list}


def retrieve_email_sub_form(request):
    """
    Retrieves email subscription form.
    """
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
