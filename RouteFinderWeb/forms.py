from django import forms


class AddressForm(forms.Form):
    home_address = forms.CharField(label='Starting Address')
    addresses = forms.CharField(widget=forms.Textarea, label='')
