from django.shortcuts import render, HttpResponseRedirect, reverse
from django.views import View
from django.conf import settings
from . import forms
from .route_solver import RouteSolver

# Create your views here.

class MainView(View):
    template_name = 'RouteFinderWeb/index_form.html'
    address_list = forms.AddressForm()

    def get(self, request):
        context = {'form': self.address_list}
        return render(request, self.template_name, context=context)

    def post(self, request):
        form = forms.AddressForm(request.POST)
        if form.is_valid():
            # Save data to session instead of global variables
            request.session['start_address'] = form.cleaned_data['start']
            request.session['other_addresses'] = form.cleaned_data['addresses']
            return HttpResponseRedirect(reverse('results'))
        
        # If form is invalid, re-render with errors
        context = {'form': form}
        return render(request, self.template_name, context=context)


class ResultsView(View):
    template_name = 'RouteFinderWeb/route.html'
    address_list = forms.AddressForm()

    def get(self, request):
        start_address = request.session.get('start_address')
        other_addresses = request.session.get('other_addresses')

        if not start_address or not other_addresses:
            return HttpResponseRedirect(reverse('index'))

        api_key = settings.GOOGLE_MAPS_API_KEY
        if not api_key:
            return render(request, self.template_name, {'error': 'Google Maps API Key not configured.'})

        try:
            solver = RouteSolver(api_key)
            optimized_route = solver.solve(start_address, other_addresses)
            
            # Format for display (optional, but good for template)
            # Assuming template iterates over 'addresses'
            
            context = {
                'addresses': optimized_route,
                'form': self.address_list,
            }
            return render(request, self.template_name, context=context)
            
        except Exception as e:
            return render(request, self.template_name, {'error': f'Error calculating route: {str(e)}'})

    def post(self, request):
        # Allow new search from results page
        form = forms.AddressForm(request.POST)
        if form.is_valid():
            request.session['start_address'] = form.cleaned_data['start']
            request.session['other_addresses'] = form.cleaned_data['addresses']
            return HttpResponseRedirect(reverse('results'))
            
        return HttpResponseRedirect(reverse('index'))
