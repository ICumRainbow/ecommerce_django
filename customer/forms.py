from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, ShippingDetails, ProductReview, EmailSubscription, ContactMessage


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone')


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = ShippingDetails
        fields = ('address', 'city', 'state', 'zipcode', 'payment_type')


class ReviewForm(forms.ModelForm):
    # review = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = ProductReview
        fields = ('review', 'rating')


class EmailSubForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = EmailSubscription
        fields = ('email',)


class ContactForm(forms.ModelForm):
    contact_email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Your email'}))
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    message = forms.TextInput(attrs={'placeholder': 'Your message'})

    class Meta:
        model = ContactMessage
        fields = ('contact_email', 'name', 'message')
