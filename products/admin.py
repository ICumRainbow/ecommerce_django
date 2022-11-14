from collections import defaultdict

from django.contrib import admin
from django.db import models
from django.db.models import Count, Avg, F, ExpressionWrapper
from django.utils.html import format_html

from core.services import get_child_objects_with_links
from .models import Product, Category


# admin.site.register(Product)
# admin.site.register(Category)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Model to display products in admin panel.
    """
    list_display = (
        "name", "get_category", "get_formatted_price", "get_discount_price", "get_discount_percentage",
        "get_number_of_likes",
        "get_average_rating")
    list_filter = ("category",)
    search_fields = ("name", "category__name", "price", "discount_price")
    autocomplete_fields = ("category",)

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
        return "$" + str(float(obj.price))

    @admin.display(description='Discount price', ordering='discount_price')
    def get_discount_price(self, obj):
        return "$" + str(float(obj.discount_price))

    @admin.display(empty_value="0", description="Discount percentage", ordering="discount_rate")
    def get_discount_percentage(self, obj):
        return f"{float(obj.discount_rate)}" + "%"

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
                                                          output_field=models.DecimalField(decimal_places=2)
                                                      ),
                                                      discount_price=ExpressionWrapper(
                                                          F('price') * F('discount_percent'),
                                                          output_field=models.DecimalField(decimal_places=2)
                                                      ),
                                                      ).select_related("category")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Model to display product categories in admin panel.
    """
    list_display = ("name", "get_products")
    list_filter = ("name",)
    search_fields = ("name",)

    @admin.display(description="Products")
    def get_products(self, obj, products=Product.objects.all()):
        child_products_with_links = get_child_objects_with_links(queryset=products, obj=obj, products_=True)
        if len(child_products_with_links) < 6:
            return format_html(" ,&nbsp;&nbsp;".join(child_products_with_links))
        else:
            category_url = (
                "http://127.0.0.1:8000/admin/products/product/?category__id__exact=" + str(obj.id)
            )
            category_link = f'<a href="{category_url}">{len(child_products_with_links)}</a>'
            first_five_child_products = " ,&nbsp;&nbsp;".join(child_products_with_links[:5])
            return format_html(first_five_child_products + f"...({category_link})")
