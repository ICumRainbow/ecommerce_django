from django.contrib import admin
from django.db.models import F

from .models import User, Order, OrderItem, ShippingDetails, LikedProduct, ProductReview, EmailSubscription, \
    ContactMessage


# admin.site.register(User)


# admin.site.register(Order)
# admin.site.register(OrderItem)
# admin.site.register(ShippingDetails)
# admin.site.register(LikedProduct)
# admin.site.register(ProductReview)
# admin.site.register(EmailSubscription)


# admin.site.register(ContactMessage)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Model to display users in admin panel.
    """
    list_display = ("username",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Model to display orders in admin panel
    """
    list_display = ("id", "get_customer_username", "completed")

    @admin.display(description="Customer", ordering="customer")
    def get_customer_username(self, obj):
        return obj.customer_username

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(customer_username=F("customer__username"))


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Model to display order items in admin panel.
    """
    list_display = ("get_product", "order", "get_customer_username")

    @admin.display(description="Customer", ordering="order__customer")
    def get_customer_username(self, obj):
        return obj.customer_username

    @admin.display(ordering="product_name")
    def get_product(self, obj):
        return obj.product_name

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(customer_username=F("order__customer__username"),
                                                      product_name=F("product__name")).select_related("product",
                                                                                                      "order",
                                                                                                      "order__customer")


@admin.register(ShippingDetails)
class ShippingDetailsAdmin(admin.ModelAdmin):
    """
    Model to display shipping details in admin panel.
    """
    list_display = ("customer", "payment_type", "state", "city", "address", "zipcode")

    @admin.display(empty_value="???", ordering="payment_type")
    def payment_type(self, obj):
        if obj.payment_type == 1:
            payment_type = 'PayMe'
        else:
            payment_type = 'Click'
        return payment_type


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Model to display contact messages in admin panel.
    """
    list_display = ("get_name", "get_email")

    @admin.display(description="Name", ordering="name")
    def get_name(self, obj):
        return obj.name

    @admin.display(description="Email", ordering="contact_email")
    def get_email(self, obj):
        return obj.contact_email


@admin.register(LikedProduct)
class LikedProductAdmin(admin.ModelAdmin):
    """
    Model to display liked products in admin panel.
    """
    list_display = ("customer_username", "product_name")

    @admin.display(description="Customer", ordering="customer")
    def customer_username(self, obj):
        return obj.customer_username

    @admin.display(description="Product", ordering="product_name")
    def product_name(self, obj):
        return obj.product_name

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(product_name=F("product__name"),
                                                      customer_username=F("customer__username"))


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """
    Model to display product reviews in admin panel.
    """
    list_display = ("get_product", "rating", "get_customer")

    @admin.display(description="Product", ordering="product__name")
    def get_product(self, obj):
        return obj.product

    @admin.display(description="Customer", ordering="customer__username")
    def get_customer(self, obj):
        return obj.customer


@admin.register(EmailSubscription)
class EmailSubscriptionAdmin(admin.ModelAdmin):
    """
    Model to display email subscriptions in admin panel.
    """
    list_display = ("get_email",)

    @admin.display(ordering="email", empty_value="?")
    def get_email(self, obj):
        return obj.email
