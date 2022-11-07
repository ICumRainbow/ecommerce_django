from posts.filters import PostFilter
from posts.models import PostCategory, Post


def get_blog_page_contents(request_dict=None, query_params=None):
    """
    Getting all the contents for the Blog page.
    """
    categories = PostCategory.objects.all()
    posts_by_date = Post.objects.order_by('-created_at')
    posts = None
    if query_params:
        posts = posts_by_date.filter(**query_params)
        posts = PostFilter(request_dict, queryset=posts)
    return categories, posts_by_date, posts


def get_current_post_and_related_posts(id_):
    """
    Getting current post and posts of the same category.
    """
    post = Post.objects.get(id=id_)
    related_posts = Post.objects.filter(category=post.category).exclude(id=id_)

    return post, related_posts
