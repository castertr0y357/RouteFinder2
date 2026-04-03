from django.shortcuts import render, HttpResponseRedirect, reverse, redirect
from django.views import View
from django.conf import settings
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
import urllib.parse
from . import forms
from .route_solver import RouteSolver
from .route_solver import RouteSolver

# Create your views here.

def generate_google_maps_urls(optimized_route):
    urls = []
    if not optimized_route or len(optimized_route) < 2:
        return urls
        
    chunk_size = 8  # max intermediate waypoints (1 origin + 1 dest + 8 wps = 10 stops)
    i = 0
    part = 1
    
    while i < len(optimized_route) - 1:
        origin = optimized_route[i]
        waypoints = optimized_route[i+1 : i+1+chunk_size]
        dest_index = i + 1 + len(waypoints)
        
        if dest_index >= len(optimized_route):
            destination = waypoints.pop()
            dest_index = len(optimized_route) - 1
        else:
            destination = optimized_route[dest_index]
            
        base_url = "https://www.google.com/maps/dir/?api=1"
        origin_enc = urllib.parse.quote(origin)
        dest_enc = urllib.parse.quote(destination)
        url = f"{base_url}&origin={origin_enc}&destination={dest_enc}"
        
        if waypoints:
            wp_enc = "|".join(urllib.parse.quote(wp) for wp in waypoints)
            url += f"&waypoints={wp_enc}"
            
        label = f"Open Route in Google Maps (Part {part})" if len(optimized_route) > 10 else "Open Route in Google Maps"
        
        urls.append({
            'label': label,
            'url': url
        })
        
        i = dest_index
        part += 1
        
    return urls

class MainView(View):
    template_name = 'RouteFinderWeb/index_form.html'

    def get(self, request):
        initial_data = {}
        if request.user.is_authenticated and hasattr(request.user, 'userprofile') and request.user.userprofile.home_address:
            initial_data['start'] = request.user.userprofile.home_address
        form = forms.AddressForm(initial=initial_data)
        context = {'form': form}
        return render(request, self.template_name, context=context)

    def post(self, request):
        form = forms.AddressForm(request.POST)
        if form.is_valid():
            # Save data to session instead of global variables
            request.session['start_address'] = form.cleaned_data['start']
            request.session['other_addresses'] = form.cleaned_data['addresses']
            # Save data to session instead of global variables
            request.session['start_address'] = form.cleaned_data['start']
            request.session['other_addresses'] = form.cleaned_data['addresses']
            return HttpResponseRedirect(reverse('results'))
        
        # If form is invalid, re-render with errors
        context = {'form': form}
        return render(request, self.template_name, context=context)
        
        # If form is invalid, re-render with errors
        context = {'form': form}
        return render(request, self.template_name, context=context)


class ResultsView(View):
    template_name = 'RouteFinderWeb/route.html'

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
            maps_urls = generate_google_maps_urls(optimized_route)
            
            context = {
                'addresses': optimized_route,
                'form': forms.AddressForm(),
                'maps_urls': maps_urls,
            }
            return render(request, self.template_name, context=context)
            
        except Exception as e:
            return render(request, self.template_name, {'error': f'Error calculating route: {str(e)}'})

    def post(self, request):
        # Allow new search from results page
        # Allow new search from results page
        form = forms.AddressForm(request.POST)
        if form.is_valid():
            request.session['start_address'] = form.cleaned_data['start']
            request.session['other_addresses'] = form.cleaned_data['addresses']
            request.session['start_address'] = form.cleaned_data['start']
            request.session['other_addresses'] = form.cleaned_data['addresses']
            return HttpResponseRedirect(reverse('results'))
            
        return HttpResponseRedirect(reverse('index'))

class RegisterView(View):
    template_name = 'RouteFinderWeb/register.html'
    
    def get(self, request):
        form = forms.UserRegisterForm()
        return render(request, self.template_name, {'form': form})
        
    def post(self, request):
        form = forms.UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Account created for {user.username}!")
            return redirect('main')
        return render(request, self.template_name, {'form': form})

class ProfileView(LoginRequiredMixin, View):
    template_name = 'RouteFinderWeb/profile.html'
    
    def get(self, request):
        form = forms.UserProfileForm(instance=request.user.userprofile)
        return render(request, self.template_name, {'form': form})
        
    def post(self, request):
        form = forms.UserProfileForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('main')
        return render(request, self.template_name, {'form': form})
