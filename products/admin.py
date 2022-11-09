from collections import defaultdict

from django.contrib import admin
from django.db import models
from django.db.models import Count, Avg, F, ExpressionWrapper

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

    @admin.display
    def get_category(self, obj):
        return obj.category

    get_category.admin_order_field = "category__name"

    @admin.display
    def get_formatted_price(self, obj):
        return "$" + str(obj.price)

    get_formatted_price.admin_order_field = "price"

    @admin.display(description='Discount price', ordering='discount_price')
    def get_discount_price(self, obj):
        return "$" + str(round(obj.price * (100 - obj.discount_rate) / 100, 2))

    @admin.display(empty_value="0")
    def get_discount_percentage(self, obj):
        return f"{obj.discount_rate}" + "%"

    get_discount_percentage.admin_order_field = "discount_rate"

    @admin.display
    def get_number_of_likes(self, obj):
        return obj.num_likes  # obj.num_likes // 2 if obj.num_likes > 1 else obj.num_likes

    get_number_of_likes.admin_order_field = "num_likes"

    @admin.display(empty_value="0")
    def get_average_rating(self, obj):
        return round(obj.avg_rating, 2) if obj.avg_rating else obj.avg_rating

    get_average_rating.admin_order_field = "avg_rating"

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
    products = Product.objects.all()
    child_products = defaultdict(list)
    for product in products:
        child_products[product.category_id].append(product.name)

    @admin.display
    def get_products(self, obj):
        child_products = self.child_products[obj.id]
        if len(child_products) < 6:
            return child_products
        else:
            first_five_child_products = child_products[:5]
            return ", ".join(first_five_child_products) + f"...({len(child_products)})"
