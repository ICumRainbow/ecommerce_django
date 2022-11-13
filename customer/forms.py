from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, ShippingDetails, ProductReview, EmailSubscription, ContactMessage


class CustomUserCreationForm(UserCreationForm):
    """
    Form for user registration.
    """
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone')


class CheckoutForm(forms.ModelForm):
    """
    Form for checkout.
    """

    class Meta:
        model = ShippingDetails
        fields = ('address', 'city', 'state', 'zipcode', 'payment_type')


class ReviewForm(forms.ModelForm):
    """
    Form for reviews.
    """
    rating = forms.FloatField(required=False)

    class Meta:
        model = ProductReview
        fields = ('review', 'rating')


class EmailSubForm(forms.ModelForm):
    """
    Form for email subscription.
    """
    email = forms.EmailField()

    class Meta:
        model = EmailSubscription
        fields = ('email',)


class ContactForm(forms.ModelForm):
    """
    Form for contact messages.
    """
    contact_email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Your email'}))
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    message = forms.TextInput(attrs={'placeholder': 'Your message'})

    class Meta:
        model = ContactMessage
        fields = ('contact_email', 'name', 'message')
