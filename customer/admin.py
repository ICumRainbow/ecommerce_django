from django.contrib import admin

from .models import User, Order, OrderItem, ShippingDetails

admin.site.register(User)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingDetails)


