from django.contrib import messages
from django.db.models import Avg, Count
from django.http import HttpResponseRedirect

from customer.forms import ReviewForm
from customer.models import ShippingDetails, Order, OrderItem, ProductReview


def get_query_params(request) -> dict:
    name, category = request.GET.get('name', ''), request.GET.get('category', False)
    query_params = {'name__icontains': name}
    if category:
        query_params['category'] = category
    return query_params


def get_reviews(product) -> tuple:
    reviews = ProductReview.objects.filter(product=product).prefetch_related('customer')
    reviews_numbers = reviews.aggregate(average=Avg('rating'), count=Count('id'))
    product.average_review = reviews_numbers['average'] or 0
    product.count_reviews = reviews_numbers['count']
    return reviews, reviews_numbers, product.average_review, product.count_reviews


def save_review_form(request, form, product) -> bool:
    print(form.errors.as_data)
    if request.method == 'POST':
        if form.is_valid():
            review: ProductReview = form.save(commit=False)
            review.customer = request.user
            review.product = product
            review.save()
            return True
        else:
            return False
    else:
        return False


def save_checkout_form(request, items, form, order) -> bool:
    if request.method == 'POST':
        if not items:
            messages.success(request, 'You have no items in your cart!')
            return False
        if form.is_valid():
            checkout: ShippingDetails = form.save(commit=False)
            checkout.customer_id = request.user.id
            checkout.order = order
            checkout.save()
            order.completed = True
            order.save()
            messages.success(request, 'Thank you! Your order will be processed within 48 hours!')
            return True
        else:
            print(form.errors.as_data)
            return False


def get_or_create_order(request) -> tuple:
    customer_id = request.user.id
    session_id = request.session.session_key

    order_kwargs = {'session_id': session_id, 'completed': False}
    if customer_id:
        order_kwargs['customer_id'] = customer_id

    order, created = Order.objects.get_or_create(**order_kwargs)
    items = OrderItem.objects.select_related('product').filter(order=order)
    return order, items


# getting items from the order when user is not registered
def get_current_order_items(request):
    order = Order.objects.get(session_id=request.session.session_key)
    order_items = OrderItem.objects.filter(order=order)
    return order, order_items


# transferring the items to order of a newly registered user
def transfer_order_items(request, user, order_items):
    session_id = request.session.session_key

    order_kwargs = {'customer': user, 'completed': False} if request.user.id else {'session_id': session_id, 'completed': False}
    order, created = Order.objects.get_or_create(**order_kwargs)
    order.session_id = session_id

    for item in order_items:
        OrderItem.objects.get_or_create(order=order, product=item.product, quantity=item.quantity)