from django.contrib import admin

from .models import User, Order, OrderItem, ShippingDetails, LikedProduct, ProductReview, EmailSubscription, \
    ContactMessage

admin.site.register(User)
# admin.site.register(Order)
# admin.site.register(OrderItem)
# admin.site.register(ShippingDetails)
# admin.site.register(LikedProduct)
# admin.site.register(ProductReview)
admin.site.register(EmailSubscription)


# admin.site.register(ContactMessage)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "completed")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("product", "order", "customer")

    @admin.display(empty_value="???")
    def customer(self, obj):
        return obj.order.customer


@admin.register(ShippingDetails)
class ShippingDetailsAdmin(admin.ModelAdmin):
    list_display = ("customer", "payment_type", "state", "city", "address", "zipcode")

    @admin.display(empty_value="???")
    def payment_type(self, obj):
        if obj.payment_type == 1:
            payment_type = 'PayMe'
        else:
            payment_type = 'Click'
        return payment_type


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_email")


@admin.register(LikedProduct)
class LikedProductAdmin(admin.ModelAdmin):
    list_display = ("customer", "product")


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "rating", "customer")

