from django.core.paginator import Paginator
from django.shortcuts import render

from posts.models import Post, PostCategory


def blog(request):
    categories = PostCategory.objects.all()
    posts_by_date = Post.objects.order_by('-created_at')
    post_name = request.GET.get('heading', '')
    category = request.GET.get('category', False)

    query_params = {'heading__icontains': post_name}

    if category:
        query_params['category_id'] = int(category)

    posts = posts_by_date.filter(**query_params)

    paginator = Paginator(posts, 4)

    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    context = {
        'post_categories': categories,
        'posts_by_date': posts_by_date[:6],
        'page': page,
    }

    return render(request, 'blog.html', context)


# def blog_search(request):
#     post_categories = PostCategory.objects.all()
#     posts_sorted_by_date = Post.objects.all().order_by('-created_at')[:6]
#
#
#
#     search_query = request.GET['post_name']
#
#     page_number = request.GET.get('page', 1)
#     products_paginated = Paginator(post_object, 4)
#     page_obj = products_paginated.get_page(page_number)
#     page_count = ceil(len(post_object) / 9)
#     page_count_range = range(1, page_count + 1)
#
#     context = {
#         'page_obj': page_obj,
#         'page_count_range': page_count_range,
#         'search_query': search_query,
#         'posts_by_date': posts_sorted_by_date,
#         'post_categories': post_categories,
#     }
#
#     return render(request, 'blog-search.html', context)


def post_details(request, id):
    post = Post.objects.get(id=id)
    posts_by_date = Post.objects.order_by('-created_at')
    related_posts = Post.objects.filter(category=post.category).exclude(id=id)
    context = {
        'posts_by_date': posts_by_date,
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'post.html', context)
