from django import forms
from RouteFinderWeb.Route.Point import Point
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

    def clean_home(self):
        start = self.cleaned_home['start']

        home = Point(start)

        if home.is_address_good():
            return home
        else:
            raise ValidationError

    def clean_addresses(self):
        data = self.cleaned_data['addresses']
        clean_addresses = data.split('\r\n')

        # Go through each address and make sure it's valid

        for x in clean_addresses:
            address = Point(x)
            if address.is_address_good():
                pass
            else:
                raise ValidationError

        return clean_addresses
