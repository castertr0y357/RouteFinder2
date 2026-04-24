from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile

class AddressForm(forms.Form):
    start = forms.CharField(widget=forms.TextInput(attrs={'size': 60, 'placeholder': 'Enter starting address'}),
                            label="Starting Location")
    addresses = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 60, 'placeholder': 'Enter exact addresses, one per line.\n(Example: 123 Main St, Springfield, ST)'}),
                                label="Destinations")
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Departure Time", initial="08:00")
    stop_mins = forms.IntegerField(label="Minutes at Each Stop", initial=15, min_value=0)

    def clean_addresses(self):
        data = self.cleaned_data['addresses']
        # Split by newline and remove empty strings
        return [addr.strip() for addr in data.splitlines() if addr.strip()]

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email Address", widget=forms.EmailInput(attrs={'placeholder': 'name@example.com'}))

    class Meta:
        model = User
        fields = ['email']

    def save(self, commit=True):
        user = super().save(commit=False)
        # Use email as username for consistency
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email Address", widget=forms.EmailInput(attrs={'autofocus': True, 'placeholder': 'name@example.com'}))

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['home_address', 'default_stop_mins']
        labels = {
            'home_address': 'Home Address',
            'default_stop_mins': 'Default Minutes Per Sale'
        }
        widgets = {
            'home_address': forms.TextInput(attrs={'placeholder': '123 Main St, Springfield, ST'}),
            'default_stop_mins': forms.NumberInput(attrs={'min': 0})
        }

class SearchForm(forms.Form):
    zip_code = forms.CharField(max_length=10, label="Zip Code", widget=forms.TextInput(attrs={'placeholder': 'Enter Zip Code'}))
    radius = forms.ChoiceField(
        choices=[(5, '5 miles'), (10, '10 miles'), (15, '15 miles'), (30, '30 miles'), (60, '60 miles')],
        initial=15,
        required=False
    )
