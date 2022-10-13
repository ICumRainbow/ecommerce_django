# Generated by Django 4.1 on 2022-10-07 14:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sessions', '0001_initial'),
        ('products', '0003_alter_product_discount_rate'),
        ('customer', '0012_remove_shippingdetails_payment_click_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shippingdetails',
            options={'verbose_name_plural': 'Shipping Details'},
        ),
        migrations.AlterField(
            model_name='order',
            name='completed',
            field=models.BooleanField(default=False, verbose_name='Completed'),
        ),
        migrations.AlterField(
            model_name='order',
            name='date_ordered',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Date ordered'),
        ),
        migrations.CreateModel(
            name='LikedProducts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
                ('session_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sessions.session')),
            ],
            options={
                'verbose_name_plural': 'Liked Products',
            },
        ),
    ]
