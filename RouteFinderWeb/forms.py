from django import forms
from django.core.exceptions import ValidationError


class AddressForm(forms.Form):
    home = forms.CharField(widget=forms.TextInput(attrs={'size': 60}),
                           label='Starting Address',
                           required=True,
                           initial='',
                           )
    addresses = forms.CharField(widget=forms.Textarea(attrs={'cols': 60}),
                                label='',
                                initial='Please input addresses, one per line',
                                required=True,
                                )

    def clean_home(self):
        clean_home = self.cleaned_data['home']

        # Do check to make sure it's a valid address

        return clean_home

    def clean_addresses(self):
        clean_addresses_input = self.cleaned_data['addresses']
        clean_addresses = clean_addresses_input.split('\n')

        # Go through each address and make sure it's valid

        for x in clean_addresses:
            pass

        return clean_addresses
