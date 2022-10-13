from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, ShippingDetails, ProductReviews


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone')


# class CustomUserChangeForm(UserChangeForm):
#     class Meta:
#         model = User
#         fields = ('username', 'first_name', 'last_name', 'email', 'phone')

class CheckoutForm(forms.ModelForm):
    customer_id = forms.CharField(required=False, disabled=True)
    order_id = forms.CharField(required=False, disabled=True)

    class Meta:
        model = ShippingDetails
        fields = ('address', 'city', 'state', 'zipcode', 'payment_type')


class ReviewForm(forms.ModelForm):
    review = forms.Textarea()

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = ProductReviews
        fields = ('review', 'rating')
