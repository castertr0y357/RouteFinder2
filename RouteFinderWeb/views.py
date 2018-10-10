from django.shortcuts import render, get_object_or_404
from django.views import View
from . import forms

# Create your views here.


class MainView(View):
    template_name = 'RouteFinderWeb/index.html'
    mystring = "Please enter addresses in, one at a time"
    address_list = forms.AddressForm
    home_address = address_list.home_address
    addresses = address_list.addresses

    def get(self, request):
        context = {'mystring': self.mystring,
                   'home_address': self.home_address,
                   'address_list': self.addresses}
        return render(request, self.template_name, context=context)


