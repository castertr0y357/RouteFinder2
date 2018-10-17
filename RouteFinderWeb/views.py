from django.shortcuts import render, HttpResponseRedirect, reverse
from django.views import View
from . import forms

# Create your views here.


class MainView(View):
    template_name = 'RouteFinderWeb/index_form.html'
    address_list = forms.AddressForm()

    def get(self, request):
        context = {'form': self.address_list,
                   }
        return render(request, self.template_name, context=context)

    def post(self, request):

        return HttpResponseRedirect(reverse('results'))


class ResultsView(View):
    template_name = 'RouteFinderWeb/route.html'
    address_list = forms.AddressForm()

    def get(self, request):

        context = {'Test': 'Test successful',
                   'form': self.address_list,
                   }

        return render(request, self.template_name, context=context)

    def post(self, request):

        return HttpResponseRedirect(reverse('results'))
