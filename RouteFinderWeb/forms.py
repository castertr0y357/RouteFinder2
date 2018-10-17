from django import forms
from . import RouteFinder2
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

        if RouteFinder2.Point.is_address_good(clean_home):
            return clean_home
        else:
            raise ValidationError

    def clean_addresses(self):
        clean_addresses_input = self.cleaned_data['addresses']
        clean_addresses = clean_addresses_input.split('\n')

        # Go through each address and make sure it's valid

        for x in clean_addresses:
            if RouteFinder2.Point.is_address_good(x):
                pass
            else:
                raise ValidationError

        return clean_addresses
