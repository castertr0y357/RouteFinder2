from django.shortcuts import render, HttpResponseRedirect, reverse
from django.views import View
from . import forms
from . import RouteFinder2

# Create your views here.

start = ""
addresses = []


class MainView(View):
    template_name = 'RouteFinderWeb/index_form.html'
    address_list = forms.AddressForm()

    def get(self, request):
        context = {'form': self.address_list,
                   }
        return render(request, self.template_name, context=context)

    def post(self, request):

        form = forms.AddressForm(request.POST)
        if form.is_valid():

            global start
            global addresses
            start = form.cleaned_data['start']
            addresses = form.cleaned_data['addresses']
            # print(addresses)

            return HttpResponseRedirect(reverse('results'))


class ResultsView(View):
    template_name = 'RouteFinderWeb/route.html'
    address_list = forms.AddressForm()

    def get(self, request):
        print(addresses)
        home = RouteFinder2.Point(start)
        points_list = RouteFinder2.Point.create_points(addresses)
        for x in points_list:
            print(x.address)
        route = RouteFinder2.Point.create_route(home, points_list)
        points = RouteFinder2.Point.print_points(home, route)

        context = {'addresses': points,
                   'form': self.address_list,
                   }

        return render(request, self.template_name, context=context)

    def post(self, request):

        form = forms.AddressForm(request.POST)
        if form.is_valid():
            start = form.cleaned_data['start']
            addresses = form.cleaned_data['addresses']

            return HttpResponseRedirect(reverse('results'))
