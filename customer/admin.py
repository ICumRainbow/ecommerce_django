from django.contrib import admin

from .models import User, Order, OrderItems, ShippingDetails

admin.site.register(User)
admin.site.register(Order)
admin.site.register(OrderItems)
admin.site.register(ShippingDetails)


