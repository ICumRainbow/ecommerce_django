from collections import defaultdict

from django.contrib import admin
from django.db import models
from django.db.models import Count, Avg, F, ExpressionWrapper
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from customer.models import LikedProduct, ProductReview
from .models import Product, Category


# admin.site.register(Product)
# admin.site.register(Category)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name", "get_category", "get_formatted_price", "get_discount_price", "get_discount_percentage",
        "get_number_of_likes",
        "get_average_rating")
    list_filter = ("category",)

    @admin.display(description="Category", ordering="category__name")
    def get_category(self, obj):
        url = (
                "http://127.0.0.1:8000/admin/products/category/"
                + str(obj.category.id)
                + "/change/"
        )
        category = f'<a href="{url}">{obj.category}</a>'
        return format_html(category)

    @admin.display(description="Price", ordering="price")
    def get_formatted_price(self, obj):
        return "$" + str(obj.price)

    @admin.display(description='Discount price', ordering='discount_price')
    def get_discount_price(self, obj):
        return "$" + str(round(obj.price * (100 - obj.discount_rate) / 100, 2))

    @admin.display(empty_value="0", description="Discount percentage", ordering="discount_rate")
    def get_discount_percentage(self, obj):
        return f"{obj.discount_rate}" + "%"

    @admin.display(description="Likes", ordering="num_likes")
    def get_number_of_likes(self, obj):
        return obj.num_likes  # obj.num_likes // 2 if obj.num_likes > 1 else obj.num_likes

    @admin.display(empty_value="0", description="Average rating", ordering="avg_rating")
    def get_average_rating(self, obj):
        return round(obj.avg_rating, 2) if obj.avg_rating else obj.avg_rating

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(avg_rating=Avg('productreview__rating'),
                                                      num_likes=Count("likedproduct", distinct=True),
                                                      discount_percent=ExpressionWrapper(
                                                          (100 - F('discount_rate')) / 100.0,
                                                          output_field=models.FloatField()
                                                      ),
                                                      discount_price=ExpressionWrapper(
                                                          F('price') * F('discount_percent'),
                                                          output_field=models.FloatField()
                                                      ),
                                                      ).select_related("category")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "get_products")
    list_filter = ("name",)

    @admin.display(description="Products")
    def get_products(self, obj, products=Product.objects.all()):
        categories_child_products = defaultdict(list)
        categories_child_products_ids = defaultdict(list)
        for product in products:
            categories_child_products[product.category_id].append(product.name)
            categories_child_products_ids[product.category_id].append(product.id)

        child_products = categories_child_products[obj.id]
        child_products_ids = categories_child_products_ids[obj.id]
        child_products_with_links = []

        for product, _id in zip(child_products, child_products_ids):
            url = (
                    "http://127.0.0.1:8000/admin/products/product/"
                    + str(_id)
                    + "/change/"
            )
            product = f'<a href="{url}">{product}</a>'
            child_products_with_links.append(product)
        if len(child_products) < 6:
            return format_html(" ,&nbsp;&nbsp;".join(child_products_with_links))
        else:
            category_url = (
                "http://127.0.0.1:8000/admin/products/product/?category__id__exact=" + str(obj.id)
            )
            category_link = f'<a href="{category_url}">{len(child_products)}</a>'
            first_five_child_products = " ,&nbsp;&nbsp;".join(child_products_with_links[:5])
            return format_html(first_five_child_products + f"...({category_link})")
