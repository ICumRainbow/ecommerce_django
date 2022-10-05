import json

from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import JsonResponse

from math import ceil

from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt

from posts.models import Post
from customer.models import Order, OrderItem
from products.models import Product
from .filters import ProductFilter


def index(request):
    products = Product.objects.all().order_by('created_at')
    posts_sorted_by_date = Post.objects.all().order_by('-created_at')
    context = {
        'products': products,
        'posts_by_date': posts_sorted_by_date,
    }
    print(request)
    return render(request, 'index.html', context)


def product_details(request, id):
    product = Product.objects.get(id=id)
    related_products = Product.objects.filter(category=product.category).exclude(id=id)
    customer = request.user.id
    order, created = Order.objects.get_or_create(customer=customer, completed=False, session_id=request.session.session_key)

    try:
        order_item = order.orderitem_set.get(product__id=id)
    except OrderItem.DoesNotExist:
        quantity = 0
    else:
        quantity = order_item.quantity

    context = {
        'product': product,
        'product_quantity': quantity,
        'related_products': related_products,
    }

    return render(request, 'product-details.html', context)


def shop_grid(request):
    products_sorted_by_date = Product.objects.all().order_by('-created_at')[:6]
    products_with_discount = Product.objects.all().filter(discount=True)
    products = Product.objects.all()

    filtered_products = ProductFilter(
        request.GET,
        queryset=products
    )
    try:
        product_name = request.GET['name']
        category = request.GET['category']
        products_object = Product.objects.filter(name__icontains=product_name, category__id__icontains=category)
    except (MultiValueDictKeyError, ValueError):
        products_object = filtered_products.qs

    page_number = request.GET.get('page', 1)
    for product in products_object:
        if product.discount:
            product.price = product.discount_price
    products_paginated = Paginator(products_object, 9)
    page_obj = products_paginated.get_page(page_number)

    context = {
        'products': products,
        'products_with_discount': products_with_discount,
        'products_sorted_by_date': products_sorted_by_date,
        'page_obj': page_obj,
    }
    return render(request, 'shop-grid.html', context)


def checkout(request):
    return render(request, 'checkout.html')


@csrf_exempt
def update_item(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']

    customer = request.user.id
    product = Product.objects.get(id=product_id)
    session_id = request.session.session_key

    order, created = Order.objects.get_or_create(customer=customer, completed=False, session_id=session_id)

    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

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


def cart(request):
    return render(request, 'shopping-cart.html')

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
