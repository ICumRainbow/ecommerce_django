import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect

from django.views.decorators.csrf import csrf_exempt

from core.services import save_review_form, get_reviews, get_or_create_order, save_checkout_form
from customer.forms import CheckoutForm, ReviewForm
from posts.models import Post
from customer.models import OrderItem, LikedProduct
from products.models import Product
from .filters import ProductFilter


def index(request):
    # single request to the database to retrieve products and categories
    products = Product.objects.select_related('category').annotate(num_likes=Count('likedproduct'),
                                                                   reviews=Avg('productreview__rating'))

    featured_products = products.order_by('-created_at')
    products_by_likes = products.order_by('-num_likes')
    products_by_reviews = products.order_by('-reviews')
    blog_posts = Post.objects.all().order_by('-created_at')

    context = {
        'blog_posts': blog_posts,
        'featured_products': featured_products,
        'products_by_reviews': products_by_reviews,
        'products_by_likes': products_by_likes,
    }
    print(type(request.GET))
    print(request.GET.urlencode())
    return render(request, 'index.html', context)


def product_details(request, id_):
    product = get_object_or_404(Product.objects.select_related('category'), id=id_)
    related_products = Product.objects.filter(category_id=product.category).exclude(id=id_)

    reviews, reviews_numbers, product.average_review, product.count_reviews = get_reviews(product)
    if request.method == 'POST' and save_review_form(request, ReviewForm(request.POST), product):
        return HttpResponseRedirect(request.path_info)
    else:
        # здесь надо разобраться
        messages.success(request, 'You need to put at least 0.5 rating and type a review!')
        review_form = ReviewForm()

    # getting the current order to retrieve the current product's quantity
    order, items = get_or_create_order(request)
    # getting product's quantity if it is present in the order
    item = order.orderitem_set.filter(product_id=id_)
    product.quantity = item[0].quantity if item else 0

    context = {
        'product': product,
        'related_products': related_products,
        'review_form': review_form,
        'reviews': reviews,
    }

    return render(request, 'product-details.html', context)


def shop_grid(request):
    products = Product.objects.select_related('category').order_by('-created_at')
    products_with_discount = products.filter(discount=True)

    # filter for search by name, price and category
    filtered_products = ProductFilter(request.GET, queryset=products)
    page_number = request.GET.get('page', 1)
    products_paginated = Paginator(filtered_products.qs, 9)
    page = products_paginated.get_page(page_number)

    context = {
        'products_with_discount': products_with_discount,
        'products_sorted_by_date': products[:6],
        'page': page,
    }
    return render(request, 'shop-grid.html', context)


@csrf_exempt
def update_item_view(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']

    product = Product.objects.get(id=product_id)
    order, items = get_or_create_order(request)
    # getting or creating an item in the order to change its quantity
    item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        item.quantity += 1
        item.save()
        order.save()
        return JsonResponse({'result': 'Success!'}, status=200)

    elif action == 'delete' or item.quantity <= 1:
        item.delete()
        order.save()
        return JsonResponse({'result': 'Success!'}, status=200)

    elif action == 'decrement':
        item.quantity -= 1
        item.save()
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
        kwargs = {'customer_id': customer_id, 'product_id': product_id} if customer_id else {
            'session_id': session_id, 'product_id': product_id}
        # gets a queryset with a product in case it was already liked, empty queryset otherwise
        liked_products = LikedProduct.objects.filter(**kwargs)

        if not liked_products:
            liked_products.create(**kwargs)
        else:
            liked_products.delete()

        return JsonResponse({'result': 'Success!'}, status=200)
    else:
        return JsonResponse({'detail': f'Unknown action {action}'}, status=400)


def cart(request):
    order, items = get_or_create_order(request)
    # getting current price (with or without discount) of a product and multiplying it its quantity in the current order
    for item in items:
        item.total = item.product.current_price * item.quantity
    context = {
        'items': items,
    }
    return render(request, 'shopping-cart.html', context)


@login_required(login_url='login')
def checkout_view(request):
    order, items = get_or_create_order(request)
    for item in items:
        item.total = item.product.current_price * item.quantity
    checkout_form = CheckoutForm(request.POST)

    if save_checkout_form(request, items, checkout_form, order) is True:
        return redirect('index')

    context = {
        'checkout_form': checkout_form,
        'items': items,
    }

    return render(request, 'checkout.html', context)


def liked_products_view(request):
    session_id = request.session.session_key
    customer_id = request.user.id

    order, order_items = get_or_create_order(request)
    liked_products_kwargs = {'customer_id': customer_id} if customer_id else {'session_id': session_id}
    liked_products = LikedProduct.objects.select_related('product').filter(**liked_products_kwargs)

    # if a liked product is also in customer's cart, we will display its quantity
    order_items_quantities = {item.product.id: item.quantity for item in order_items}
    for liked_product in liked_products:
        if liked_product.product.id in order_items_quantities:
            liked_product.quantity = order_items_quantities[liked_product.product.id]
        else:
            liked_product.quantity = 0

    context = {
        'liked_products_list': liked_products,
    }

    return render(request, 'liked_products.html', context)
