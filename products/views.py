import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from customer.forms import CheckoutForm, ReviewForm
from posts.services import get_blog_page_contents
from .filters import ProductFilter
from .services import get_reviews, save_review_form, save_checkout_form, get_or_create_order, get_all_products, \
    get_product_and_related_products, get_current_item, like_or_delete_liked_product, get_items_quantities, \
    get_liked_products_and_quantities, add_product, delete_item, decrement_item


def index_view(request):
    """
    View for index page.
    """
    products, products_by_likes, products_by_reviews, _ = get_all_products()
    _, blog_posts, _ = get_blog_page_contents()

    context = {
        'blog_posts': blog_posts,
        'featured_products': products,
        'products_by_reviews': products_by_reviews,
        'products_by_likes': products_by_likes,
    }
    return render(request, 'index.html', context)


def product_details_view(request, id_):
    """
    View for product details page.
    """
    product, related_products = get_product_and_related_products(id_)
    reviews, reviews_numbers, product.average_review, product.count_reviews = get_reviews(product)
    if request.method == 'POST' and save_review_form(request, ReviewForm(request.POST), product):
        return HttpResponseRedirect(request.path_info)
    else:
        review_form = ReviewForm()

    get_current_item(request, product, id_)

    context = {
        'product': product,
        'related_products': related_products,
        'review_form': review_form,
        'reviews': reviews,
    }

    return render(request, 'product/product-details.html', context)


def shop_grid_view(request):
    """
    View for shop grid page.
    """
    products, _, _, products_with_discount = get_all_products()
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
    return render(request, 'product/shop-grid.html', context)


@csrf_exempt
def update_item_view(request):
    """
    View for adding, decrementing or removing an item from the order.
    """
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']

    product, _ = get_product_and_related_products(product_id)
    order, items = get_or_create_order(request)
    # getting or creating an item in the order to change its quantity
    item = get_current_item(request, product, product_id)

    if action == 'add':
        add_product(item, order)
        return JsonResponse({'result': 'Success!'}, status=200)

    elif action == 'delete' or item.quantity <= 1:
        delete_item(item, order)
        return JsonResponse({'result': 'Success!'}, status=200)

    elif action == 'decrement':
        decrement_item(item, order)
        return JsonResponse({'result': 'Success!'}, status=200)

    else:
        return JsonResponse({'detail': f'Unknown action {action}'}, status=400)


@csrf_exempt
def like_item_view(request):
    """
    View for liking an item or removing an item from Liked Products.
    """
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']

    if action == 'like':
        kwargs = {'customer_id': request.user.id, 'product_id': product_id} if request.user.id else {
            'session_id': request.session.session_key, 'product_id': product_id}

        like_or_delete_liked_product(kwargs)

        return JsonResponse({'result': 'Success!'}, status=200)
    else:
        return JsonResponse({'detail': f'Unknown action {action}'}, status=400)


def cart_view(request):
    """
    View for cart page.
    """
    _, items = get_or_create_order(request)
    get_items_quantities(items)

    context = {
        'items': items,
    }
    return render(request, 'order/shopping-cart.html', context)


@login_required(login_url='login')
def checkout_view(request):
    """
    View for checkout page.
    """
    order, items = get_or_create_order(request)
    if not items:
        messages.success(request, 'You have no items in your cart!')
        return redirect('shop_grid')
    else:
        get_items_quantities(items)

    checkout_form = CheckoutForm(request.POST)

    if save_checkout_form(request, checkout_form, order) is True:
        return redirect('index')

    context = {
        'checkout_form': checkout_form,
        'items': items,
    }

    return render(request, 'order/checkout.html', context)


def liked_products_view(request):
    """
    View for liked products.
    """
    order, order_items = get_or_create_order(request)
    liked_products_kwargs = {'customer_id': request.user.id} if request.user.id else {'session_id': request.session.session_key}
    liked_products = get_liked_products_and_quantities(order_items, liked_products_kwargs)

    context = {
        'liked_products_list': liked_products,
    }

    return render(request, 'customer/liked_products.html', context)
