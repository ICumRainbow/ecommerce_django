from django.contrib import admin
from django.db.models import Count, Avg

from customer.models import LikedProduct, ProductReview
from .models import Product, Category

# admin.site.register(Product)
admin.site.register(Category)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "get_formatted_price", "get_current_price", "get_discount_percentage", "get_number_of_likes", "get_average_rating")

    @admin.display(ordering=True)
    def get_formatted_price(self, obj):
        return "$" + str(obj.price)

    @admin.display(ordering=True)
    def get_current_price(self, obj):
        return "$" + str(round(obj.price * (100 - obj.discount_rate) / 100, 2))

    @admin.display(empty_value="0", ordering=True)
    def get_discount_percentage(self, obj):
        return f"{obj.discount_rate}" + "%"

    @admin.display(ordering=True)
    def get_number_of_likes(self, obj):
        # need to override get_queryset here as well
        result = LikedProduct.objects.filter(product=obj.id).aggregate(Count("id"))
        return result["id__count"]

    @admin.display(empty_value="0")
    def get_average_rating(self, obj):
        return round(obj.avg_rating, 2) if obj.avg_rating else obj.avg_rating

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(avg_rating=Avg('productreview__rating'))
