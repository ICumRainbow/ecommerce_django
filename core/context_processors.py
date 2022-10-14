from django.db.models import Sum

from customer.models import Order, LikedProducts, OrderItems
from products.filters import ProductFilter
from products.models import Category, Product


def retrieve_cart_items(request):
    customer = request.user.id
    session_id = request.session.session_key
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer_id=customer, session_id=session_id, completed=False)
    else:
        order, created = Order.objects.get_or_create(session_id=session_id, completed=False)
    # items = order.orderitems_set.all()
    order_items_qs = OrderItems.objects.filter(order=order).select_related('product').only('quantity', 'product', 'product__price')
    cart_items = order_items_qs.aggregate(Sum('quantity'))
    order_items = order_items_qs.only('product')
    order_total = 0
    for item in order_items:
        order_total += float(item.product.current_price)
    context = {
        'cart_items': cart_items['quantity__sum'],
        'order_total': order_total,
    }

    return context


def retrieve_liked_products(request):
    customer = request.user.id
    session_id = request.session.session_key
    if request.user.is_authenticated:
        liked_products_count = LikedProducts.objects.filter(customer_id=customer, session_id=session_id).count()
    else:
        liked_products_count = LikedProducts.objects.filter(session_id=session_id).count()

    context = {
        'liked_products': liked_products_count
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
    # categories = list(Category.objects.all())
    categories_list = list(Category.objects.only('name', 'id', 'image').prefetch_related())
    # categories = set()
    # for ctg in categories_list:
    #     categories.add(ctg.category.name)
    #     ctg.slugified_name = ''.join(filter(str.isalnum, ctg.name))

    context = {
        'categories': categories_list,
    }

    return context
