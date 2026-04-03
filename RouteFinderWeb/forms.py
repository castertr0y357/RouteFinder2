from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class AddressForm(forms.Form):
    start = forms.CharField(widget=forms.TextInput(attrs={'size': 60, 'placeholder': 'Enter starting address'}),
                            label='Starting Address',
                            required=True,
                            initial='',
                            )
    addresses = forms.CharField(widget=forms.Textarea(attrs={'cols': 60, 'placeholder': 'Please input addresses, one per line'}),
                                label='',
                                initial='',
                                required=True,
                                )

    def clean_addresses(self):
        data = self.cleaned_data['addresses']
        # Split by newline and remove empty strings
        clean_addresses = [addr.strip() for addr in data.splitlines() if addr.strip()]
        # Split by newline and remove empty strings
        clean_addresses = [addr.strip() for addr in data.splitlines() if addr.strip()]
        return clean_addresses

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['home_address']
        labels = {'home_address': 'Home Address'}
        widgets = {
            'home_address': forms.TextInput(attrs={'placeholder': '123 Main St, Springfield, ST'})
        }
