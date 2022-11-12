from collections import defaultdict

from django.contrib import admin
from django.utils.html import format_html

from .models import Post, PostCategory


@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ("name","get_posts")
    list_filter = ("name",)

    @admin.display
    def get_posts(self, obj, posts=Post.objects.all()):
        categories_child_posts = defaultdict(list)
        categories_child_posts_ids = defaultdict(list)
        for post in posts:
            categories_child_posts[post.category_id].append(post.heading)
            categories_child_posts_ids[post.category_id].append(post.id)

        child_posts = categories_child_posts[obj.id]
        child_posts_ids = categories_child_posts_ids[obj.id]
        child_posts_with_links = []

        for post, _id in zip(child_posts, child_posts_ids):
            _id = str(_id)
            url = (
                    "http://127.0.0.1:8000/admin/posts/post/"
                    + _id
                    + "/change/"
            )
            post = f'<a href="{url}">{post}</a>'
            child_posts_with_links.append(post)
        if len(child_posts) < 3:
            return format_html(" ,&nbsp;&nbsp;".join(child_posts_with_links))
        else:
            category_url = (
                    "http://127.0.0.1:8000/admin/posts/post/?category__id__exact=" + str(obj.id)
            )
            category_link = f'<a href="{category_url}">{len(child_posts)}</a>'
            first_three_child_posts = " ,&nbsp;&nbsp;".join(child_posts_with_links[:3])
            return format_html(first_three_child_posts + f"...({category_link})")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("heading", "get_category")
    list_filter = ("category",)

    @admin.display(description="Category", ordering="category__name")
    def get_category(self, obj):
        url = (
                "http://127.0.0.1:8000/admin/posts/postcategory/"
                + str(obj.category.id)
                + "/change/"
        )
        category = f'<a href="{url}">{obj.category}</a>'
        return format_html(category)
