from django.contrib import admin
from django.db.models import Count, Avg

from customer.models import LikedProduct, ProductReview
from .models import Product, Category

# admin.site.register(Product)
admin.site.register(Category)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "get_formatted_price", "get_current_price", "get_discount_percentage", "get_number_of_likes", "get_average_rating")

    @admin.display
    def get_formatted_price(self, obj):
        return "$" + str(obj.price)

    @admin.display
    def get_current_price(self, obj):
        return "$" + str(round(obj.price * (100 - obj.discount_rate) / 100, 2))

    @admin.display(empty_value="0")
    def get_discount_percentage(self, obj):
        return f"{obj.discount_rate}" + "%"

    @admin.display
    def get_number_of_likes(self, obj):
        return obj.num_likes//2 if obj.num_likes>1 else obj.num_likes

    @admin.display(empty_value="0")
    def get_average_rating(self, obj):
        return round(obj.avg_rating, 2) if obj.avg_rating else obj.avg_rating

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(avg_rating=Avg('productreview__rating'),num_likes=Count('likedproduct__product_id'))
