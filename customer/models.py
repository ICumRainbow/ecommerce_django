from django.contrib.auth.models import AbstractUser
from django.db import models

from products.models import Product


class User(AbstractUser):
    username = models.CharField(blank=False, max_length=100, unique=True)
    email = models.EmailField(default=False, blank=False)
    phone = models.CharField(max_length=12)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'email', 'phone']
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField('Date ordered', auto_now_add=True)
    completed = models.BooleanField('Completed', default=False)
    session = models.ForeignKey(to='sessions.Session', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        order_items = self.orderitems_set.all()
        total = sum([item.get_total for item in order_items])
        return "{:.2f}".format(total)

    @property
    def get_cart_items(self):
        order_items = self.orderitems_set.all()
        total = sum([item.quantity for item in order_items])
        return total


class OrderItems(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product}, {self.order}'

    @property
    def get_total(self):
        product_price = self.product.current_price if self.product.discount else self.product.price
        total = product_price * self.quantity
        return total


class LikedProducts(models.Model):
    class Meta:
        verbose_name_plural = 'Liked Products'

    customer = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)
    session = models.ForeignKey(to='sessions.Session', on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.product.name


class ProductReviews(models.Model):
    review = models.TextField(blank=False, null=False)
    customer = models.ForeignKey(to=User, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    rating = models.FloatField()
    date_written = models.DateTimeField(auto_now_add=True)


class ShippingDetails(models.Model):
    class Meta:
        verbose_name_plural = 'Shipping Details'

    class PaymentType(models.IntegerChoices):
        PAYME = 1, 'PayMe'
        CLICK = 2, 'Click'

    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    payment_type = models.SmallIntegerField(choices=PaymentType.choices)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.customer.username} - {self.order_id}'


class EmailSubscriptions(models.Model):
    email = models.EmailField(unique=True)


class ContactMessages(models.Model):
    name = models.CharField(max_length=30, null=False)
    contact_email = models.EmailField()
    message = models.TextField(max_length=200, null=False)
