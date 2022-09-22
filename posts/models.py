from datetime import datetime

from django.db import models


class PostCategory(models.Model):
    name = models.CharField('Name', max_length=200, null=False)
    description = models.TextField('Post Category Description', default="")

    class Meta:
        verbose_name = 'Post Category'
        verbose_name_plural = 'Post Categories'

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.CharField('Author', max_length=100, null=False)
    heading = models.CharField('Heading', max_length=200, null=False)
    picture = models.ImageField('Image', default='product-1.jpg')
    content = models.TextField('Content')
    created_at = models.DateTimeField(default=datetime.now)
    category = models.ForeignKey(verbose_name='Post Category', to=PostCategory, on_delete=models.CASCADE, default='', related_name='posts')

    def __str__(self):
        return self.heading