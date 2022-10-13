from customer.models import Order, LikedProducts
from products.filters import ProductFilter
from products.models import Category, Product


def retrieve_cart_items(request):
    customer = request.user.id
    session_id = request.session.session_key
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer_id=customer, session_id=session_id, completed=False)
    else:
        order, created = Order.objects.get_or_create(session_id=session_id, completed=False)
    items = order.orderitems_set.all()
    cart_items = order.get_cart_items

    context = {
        'cart_items': cart_items,
        'order': order,
        'items': items,
    }

    return context


def retrieve_liked_products(request):
    customer = request.user.id
    session_id = request.session.session_key
    if request.user.is_authenticated:
        liked_products = LikedProducts.objects.filter(customer_id=customer, session_id=session_id)
    else:
        liked_products = LikedProducts.objects.filter(session_id=session_id)

    context = {
        'liked_products': len(liked_products)
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
    categories = list(Category.objects.all())
    for ctg in categories:
        ctg.slugified_name = ''.join(filter(str.isalnum, ctg.name))

    context = {
        'categories': categories,
    }

    return context
