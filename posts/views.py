from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.shortcuts import render

from posts.models import Post, PostCategory


def blog(request):
    post_categories = PostCategory.objects.all()
    query_for_posts_sorted_by_date = Post.objects.all().query
    query_for_posts_sorted_by_date.order_by = ['-created_at']
    posts_sorted_by_date = QuerySet(query=query_for_posts_sorted_by_date, model=Post)

    posts = Post.objects.all()
    paginator = Paginator(posts_sorted_by_date, 4)

    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'post_categories': post_categories,
        'posts_by_date': posts_sorted_by_date,
        'page_obj': page_obj
    }

    return render(request, 'blog.html', context)
