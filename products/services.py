from django.contrib import messages
from django.db.models import Count, Avg
from django.shortcuts import get_object_or_404

from customer.models import ProductReview, ShippingDetails, Order, OrderItem, LikedProduct
from products.models import Product


def get_reviews(product) -> tuple:
    """
    Getting reviews, reviews count and average rating for a product.
    """
    reviews = ProductReview.objects.filter(product=product).prefetch_related('customer')
    reviews_numbers = reviews.aggregate(average=Avg('rating'), count=Count('id'))
    product.average_review = reviews_numbers['average'] or 0
    product.count_reviews = reviews_numbers['count']
    return reviews, reviews_numbers, product.average_review, product.count_reviews


def save_review_form(request, form, product) -> bool:
    """
    Saves Review form and returns True if form is valid, False otherwise.
    """
    if request.method == 'POST' and form.is_valid():
        review: ProductReview = form.save(commit=False)
        review.customer = request.user
        review.product = product
        review.save()
        return True
    else:
        return False


def save_checkout_form(request, form, order) -> bool:
    """
    Saves checkout form, sets the order to "Completed" and returns True if form is valid, False otherwise.
    """
    if request.method == 'POST':
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
    """
    Getting or creating an order an order items.
    """
    customer_id = request.user.id
    session_id = request.session.session_key

    order_kwargs = {'session_id': session_id, 'completed': False}
    if customer_id:
        order_kwargs['customer_id'] = customer_id

    order, created = Order.objects.get_or_create(**order_kwargs)
    items = OrderItem.objects.select_related('product').filter(order=order)
    return order, items


def get_all_products():
    """
    Getting products sorted by date, likes, reviews and discount.
    """
    # single request to the database to retrieve products and categories
    products = Product.objects.select_related('category').order_by('-created_at')
    products_by_likes = products.annotate(num_likes=Count('likedproduct')).order_by('-num_likes')
    products_by_reviews = products.annotate(reviews=Avg('productreview__rating')).order_by('-reviews')
    products_with_discount = products.filter(discount=True)

    return products, products_by_likes, products_by_reviews, products_with_discount


def get_product_and_related_products(id_):
    """
    Getting a product from the querystring and products of the same category.
    """
    product = get_object_or_404(Product.objects.select_related('category'), id=id_)
    related_products = Product.objects.filter(category_id=product.category).exclude(id=id_)

    return product, related_products


def get_current_item(request, product, id_):
    """
    Getting current item in order to display its quantity or to change its quantity.
    """
    # getting the current order to retrieve the current product's quantity
    order, items = get_or_create_order(request)
    # getting product's quantity if it is present in the order
    item = order.orderitem_set.get_or_create(product_id=id_)
    product.quantity = item[0].quantity

    return item[0]


def like_or_delete_liked_product(kwargs):
    """
    If a products is already liked, removing it from Liked Products, adds to Liked Products otherwise.
    """
    # gets a queryset with a product in case it was already liked, empty queryset otherwise
    liked_product = LikedProduct.objects.filter(**kwargs)

    if not liked_product:
        liked_product.create(**kwargs)
    else:
        liked_product.delete()


def get_items_quantities(items):
    """
    Getting quantities of the items.
    """
    # getting current price (with or without discount) of a product and multiplying it its quantity in the current order
    for item in items:
        item.total = item.product.current_price * item.quantity


def get_liked_products_and_quantities(order_items, liked_products_kwargs):
    """
    Getting liked products and their quantities.
    """
    liked_products = LikedProduct.objects.select_related('product').filter(**liked_products_kwargs)
    # if a liked product is also in customer's cart, we will display its quantity
    order_items_quantities = {item.product.id: item.quantity for item in order_items}
    for liked_product in liked_products:
        if liked_product.product.id in order_items_quantities:
            liked_product.quantity = order_items_quantities[liked_product.product.id]
        else:
            liked_product.quantity = 0

    return liked_products


def add_product(item, order):
    """
    Increases item's quantity by one.
    """
    item.quantity += 1
    item.save()
    order.save()


def delete_item(item, order):
    """
    Deletes item from the order.
    """
    item.delete()
    order.save()


def decrement_item(item, order):
    """
    Decreases item's quantity by one.
    """
    item.quantity -= 1
    item.save()
    order.save()
