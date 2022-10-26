from datetime import datetime

from django.db import models


class Category(models.Model):
    name = models.CharField('Name', max_length=200)
    image = models.ImageField('Image', upload_to='media', default='cat-1.jpg')
    description = models.TextField('Description', default='')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    @property
    def slugified_name(self):
        return ''.join(filter(str.isalnum, self.name))

    def child_products(self):
        return self.products.all()


class Product(models.Model):
    name = models.CharField('Name', max_length=200)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField('Price', max_digits=5, decimal_places=2)
    description = models.TextField('Description')
    image = models.ImageField('Image', default='product-1.jpg')
    in_stock = models.BooleanField('In-stock', default=True)
    discount = models.BooleanField('Discount', default=False)
    discount_rate = models.DecimalField('Discount rate', max_digits=5, decimal_places=2, null=True, default=0)
    created_at = models.DateTimeField('Created at', default=datetime.now)

    def __str__(self):
        return self.name

    @property
    def current_price(self) -> float:
        if self.discount:
            return round(self.price * (100 - self.discount_rate) / 100, 2)
        return float(self.price)


