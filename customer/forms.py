from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, ShippingDetails, ProductReviews, EmailSubscriptions, ContactMessages


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone')


class CheckoutForm(forms.ModelForm):
    # these fields are disabled because customer doesn't have to see it, this info is retrieved & sent by ourselves
    # customer_id = forms.CharField(required=False, disabled=True)
    # order_id = forms.CharField(required=False, disabled=True)

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


class EmailSubForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = EmailSubscriptions
        fields = ('email',)


class ContactForm(forms.ModelForm):
    contact_email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Your email'}))
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    message = forms.TextInput(attrs={'placeholder': 'Your message'})

    class Meta:
        model = ContactMessages
        fields = ('contact_email', 'name', 'message')
