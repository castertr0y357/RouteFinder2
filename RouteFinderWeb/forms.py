from django import forms
from django.core.exceptions import ValidationError

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
        return clean_addresses
