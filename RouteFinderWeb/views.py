from django.shortcuts import render, get_object_or_404
from django.views import View
from . import forms

# Create your views here.


class MainView(View):
    template_name = 'RouteFinderWeb/index.html'
    address_list = forms.AddressForm

    def get(self, request):
        if request.method == 'POST':  # If form has been filled out and submitted

            context = {'mystring': 'You have successfully submitted the form',
                       }

            return render(request, self.template_name, context=context)

        else:  # If GET request
            context = {'form': self.address_list,
                       }
            return render(request, self.template_name, context=context)


