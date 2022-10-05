from core.custom_session_middleware import CustomSessionMiddleware
from customer.models import Order
from products.filters import ProductFilter
from products.models import Category, Product


def retrieve_cart_items(request):
    customer_id = request.user.id
    session_id = request.session.session_key
    order, created = Order.objects.get_or_create(customer_id=customer_id, completed=False, session_id=session_id)
    items = order.orderitem_set.all()
    cart_items = order.get_cart_items

    context = {
        'cart_items': cart_items,
        'order': order,
        'items': items,
    }

    return context


def retrieve_filter_form(request):
    filtered_products = ProductFilter(
        request.GET,
        queryset=Product.objects.all()
    )
    context = {
        'filtered_products': filtered_products,
    }
    return context


def retrieve_categories(request):
    categories = Category.objects.all()
    for ctg in categories:
        ctg.slugified_name = ''.join(filter(str.isalnum, ctg.name))

    context = {
        'categories': categories,
    }

    return context

