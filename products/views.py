import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.models import User

from math import ceil

from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt

from customer.forms import CheckoutForm, ReviewForm
from posts.models import Post
from customer.models import Order, OrderItems, ShippingDetails, ProductReviews, LikedProducts
from products.models import Product
from .filters import ProductFilter


def index(request):
    products_all = Product.objects.all().select_related()
    products = products_all.order_by('created_at')
    products_by_likes = products_all.annotate(num_likes=Count('likedproducts')).order_by('-num_likes')
    products_by_reviews = products_all.annotate(reviews=Sum('productreviews')).order_by('reviews')
    print(products_by_reviews)
    posts_sorted_by_date = Post.objects.all().order_by('-created_at')

    context = {
        'products': products,
        'posts_by_date': posts_sorted_by_date,
        'products_by_likes': products_by_likes,
    }
    return render(request, 'index.html', context)


def product_details(request, id_):
    product = Product.objects.get(id=id_)
    related_products = Product.objects.filter(category=product.category).exclude(id=id_)
    customer_id = request.user.id
    session_id = request.session.session_key
    review_form = ReviewForm(request.POST)
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer_id=customer_id, completed=False)
        print(created)
    else:
        order, created = Order.objects.get_or_create(session_id=session_id, completed=False)

    try:
        order_item = order.orderitems_set.get(product_id=id_)
    except OrderItems.DoesNotExist:
        quantity = 0
    else:
        quantity = order_item.quantity

    if request.method == 'POST':
        if review_form.is_valid():
            review: ProductReviews = review_form.save(commit=False)
            review.customer = request.user
            review.product = product
            review.save()
            return HttpResponseRedirect(request.path_info)
        else:
            print(review_form.errors.as_data)
    reviews = ProductReviews.objects.filter(product=product)
    context = {
        'product': product,
        'product_quantity': quantity,
        'related_products': related_products,
        'review_form': review_form,
        'reviews': reviews,
    }

    return render(request, 'product-details.html', context)


def shop_grid(request):
    products_sorted_by_date = Product.objects.all().order_by('-created_at').select_related()[:6]
    products_with_discount = Product.objects.filter(discount=True).select_related()
    products = Product.objects.all().select_related()

    filtered_products = ProductFilter(
        request.GET,
        queryset=products
    )
    try:
        product_name = request.GET['name']
        category = request.GET['category']
        products_object = Product.objects.filter(name__icontains=product_name, category__id=category)
    except (MultiValueDictKeyError, ValueError):
        products_object = filtered_products.qs

    page_number = request.GET.get('page', 1)
    for product in products_object:
        if product.discount:
            product.price = product.current_price
    products_paginated = Paginator(products_object, 9)
    page_obj = products_paginated.get_page(page_number)

    context = {
        'products': products,
        'products_with_discount': products_with_discount,
        'products_sorted_by_date': products_sorted_by_date,
        'page_obj': page_obj,
    }
    return render(request, 'shop-grid.html', context)


@login_required(login_url='login')
def checkout_view(request):
    payment_type_mapping = {
        'click': ShippingDetails.PaymentType.CLICK,
        'payme': ShippingDetails.PaymentType.PAYME
    }

    customer = request.user.id
    session_id = request.session.session_key

    # if request.user.is_authenticated:
    order, created = Order.objects.get_or_create(customer_id=customer, completed=False)
    # else:
    #     order, created = Order.objects.get_or_create(session_id=session_id, completed=False)
    order_items = OrderItems.objects.filter(order=order)
    checkout_form = CheckoutForm(request.POST)

    context = {
        'checkout_form': checkout_form,
    }
    if request.method == 'POST':
        if not order_items:
            messages.success(request, 'You have no items in your cart!')
            return render(request, 'checkout.html', context)
        if checkout_form.is_valid():
            checkout: ShippingDetails = checkout_form.save(commit=False)
            checkout.customer_id = request.user.id
            checkout.order = order
            checkout.save()
            order.completed = True
            order.save()
            return HttpResponseRedirect(request.path_info)
        else:
            print(checkout_form.errors.as_data)
            print('FUCK YOU')
    return render(request, 'checkout.html', context)


@csrf_exempt
def update_item_view(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']

    customer = request.user.id
    product = Product.objects.get(id=product_id)
    session_id = request.session.session_key
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer_id=customer, session_id=session_id, completed=False)
    else:
        order, created = Order.objects.get_or_create(session_id=session_id, completed=False)

    order_item, created = OrderItems.objects.get_or_create(order=order, product=product)

    if action == 'add':
        order_item.quantity += 1
        order_item.save()
        order.save()
        return JsonResponse({'result': 'Success!'}, status=200)

    elif action == 'delete' or order_item.quantity <= 1:
        order_item.delete()
        order.save()
        return JsonResponse({'result': 'Success!'}, status=200)

    elif action == 'remove':
        order_item.quantity -= 1
        order_item.save()
        order.save()
        return JsonResponse({'result': 'Success!'}, status=200)

    else:
        return JsonResponse({'detail': f'Unknown action {action}'}, status=400)


@csrf_exempt
def like_item_view(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']

    customer_id = request.user.id
    session_id = request.session.session_key

    if action == 'like':
        kwargs = {'customer_id': customer_id, 'session_id': session_id, 'product_id': product_id} if customer_id else {
            'session_id': session_id, 'product_id': product_id}
        liked_products = LikedProducts.objects.filter(**kwargs)

        if not liked_products:
            liked_products.create(**kwargs)
        else:
            liked_products.delete()

        return JsonResponse({'result': 'Success!'}, status=200)
    else:
        return JsonResponse({'detail': f'Unknown action {action}'}, status=400)


def cart(request):
    customer = request.user.id
    session_id = request.session.session_key
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer_id=customer, session_id=session_id, completed=False)
    else:
        order, created = Order.objects.get_or_create(session_id=session_id, completed=False)
    items = OrderItems.objects.select_related('product').filter(order=order)
    for item in items:
        item.total = item.product.price * item.quantity
    context = {
        'items': items,
    }
    return render(request, 'shopping-cart.html', context)


def liked_products_view(request):
    session_id = request.session.session_key
    customer_id = request.user.id
    # if request.user.is_authenticated:
    #     order, created = Order.objects.get_or_create(customer_id=customer_id, session_id=session_id, completed=False)
    #     liked_products = LikedProducts.objects.filter(customer=customer_id)
    # else:
    #     order, created = Order.objects.get_or_create(session_id=session_id, completed=False)
    #     liked_products = LikedProducts.objects.filter(session_id=session_id)

    order_kwargs = {'customer_id': customer_id, 'session_id': session_id, 'completed': False} if customer_id else {
        'session_id': session_id, 'completed': False}
    liked_products_kwargs = {'customer_id': customer_id, 'session_id': session_id} if customer_id else {
        'session_id': session_id}
    order, created = Order.objects.get_or_create(**order_kwargs)
    items = OrderItems.objects.prefetch_related('product').filter(order=order)
    liked_products = LikedProducts.objects.prefetch_related('product').filter(**liked_products_kwargs)
    items_dict = {item.product.id: item.quantity for item in items}
    for liked_product in liked_products:
        if liked_product.product.id in items_dict.keys():
            liked_product.quantity = items_dict[liked_product.product.id]
        else:
            liked_product.quantity = 0

            # for product in liked_products:
    #     item = OrderItems.objects.filter(order=order, product=product.product.id)
    #     quantity_qs = item.values('quantity')
    #     price_qs = item.values('product__price')
    #     print(price_qs)
    #     discount_rate_qs = item.values('product__discount_rate')
    #     print(discount_rate_qs)
    #     discount_qs = item.values('product__discount')
    #     print(discount_qs)
    #     product.price = round(price_qs[0]['product__price'] * (100 - discount_rate_qs[0]['product__discount_rate']) / 100, 2) if discount_qs[0]['product__discount'] else price_qs[0]['product__price']
    #     print(price_qs)
    #     product.quantity = quantity_qs[0]['quantity'] if len(quantity_qs) > 0 else 0

    context = {
        'liked_products_list': liked_products,
    }
    return render(request, 'liked_products.html', context)

# def product_search(request):
#     products_sorted_by_date = Product.objects.all().order_by('-created_at')[:6]
#     if request.method == 'GET':
#         product_name = request.GET['name']
#         category = request.GET['category']
#         product_object = Product.objects.filter(name__icontains=product_name, category__id__icontains=category)
#
#     search_query_name = request.GET['name']
#     if request.GET['category']:
#         search_query_category = Category.objects.get(id=request.GET['category'])
#     else:
#         search_query_category = ''
#
#     page_number = request.GET.get('page', 1)
#     products_paginated = Paginator(product_object, 9)
#     page_obj = products_paginated.get_page(page_number)
#     page_count = ceil(len(product_object) / 9)
#     page_count_range = range(1, page_count + 1)
#
#     context = {
#         'page_obj': page_obj,
#         'page_count_range': page_count_range,
#         'products_sorted_by_date': products_sorted_by_date,
#         'search_query_name': search_query_name,
#         'search_query_category': search_query_category,
#     }
#
#     return render(request, 'search.html', context)
