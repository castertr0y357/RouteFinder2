import json
import datetime
import urllib.parse
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect

from . import forms
from .models import AddressRating
from .route_solver import RouteSolver
from .scraper import scrape_sales, scrape_thrift_stores
from .location_service import get_zip_from_coords

# Create your views here.

def generate_google_maps_urls(optimized_route):
    urls = []
    if not optimized_route or len(optimized_route) < 2:
        return urls
        
    chunk_size = 8  # max intermediate waypoints (1 origin + 1 dest + 8 wps = 10 stops)
    i = 0
    part = 1
    
    while i < len(optimized_route) - 1:
        origin = optimized_route[i]['address']
        waypoints = optimized_route[i+1 : i+1+chunk_size]
        dest_index = i + 1 + len(waypoints)
        
        if dest_index >= len(optimized_route):
            destination = waypoints.pop()['address']
            dest_index = len(optimized_route) - 1
        else:
            destination = optimized_route[dest_index]['address']
            
        base_url = "https://www.google.com/maps/dir/?api=1"
        origin_enc = urllib.parse.quote(origin)
        dest_enc = urllib.parse.quote(destination)
        url = f"{base_url}&origin={origin_enc}&destination={dest_enc}"
        
        if waypoints:
            wp_enc = "|".join(urllib.parse.quote(wp['address']) for wp in waypoints)
            url += f"&waypoints={wp_enc}"
            
        label = f"Open Route in Google Maps (Part {part})" if len(optimized_route) > 10 else "Open Route in Google Maps"
        
        urls.append({
            'label': label,
            'url': url
        })
        
        i = dest_index
        part += 1
        
    return urls

class MainView(LoginRequiredMixin, View):
    template_name = 'RouteFinderWeb/index_form.html'

    def get(self, request):
        initial_data = {}
        if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
            if request.user.userprofile.home_address:
                initial_data['start'] = request.user.userprofile.home_address
            initial_data['stop_mins'] = request.user.userprofile.default_stop_mins
            
        if 'other_addresses' in request.session:
            initial_data['addresses'] = request.session['other_addresses']
            
        form = forms.AddressForm(initial=initial_data)
        context = {'form': form}
        return render(request, self.template_name, context=context)

    def post(self, request):
        start_address = request.POST.get('start_address')
        start_time = request.POST.get('start_time', '08:00')
        stop_mins = int(request.POST.get('stop_mins', 15))
        
        addresses = request.POST.getlist('address[]')
        priorities = request.POST.getlist('priority[]')
        types = request.POST.getlist('type[]')
        
        destinations = []
        for i in range(len(addresses)):
            addr = addresses[i].strip()
            if addr:
                prio = int(priorities[i]) if i < len(priorities) and priorities[i].strip() else 0
                ty = types[i] if i < len(types) and types[i] else 'garage'
                destinations.append({'address': addr, 'priority': prio, 'type': ty})
                
        request.session['start_address'] = start_address
        request.session['other_addresses'] = destinations
        request.session['start_time'] = start_time
        request.session['stop_mins'] = stop_mins
        
        return HttpResponseRedirect(reverse('results'))


class ResultsView(LoginRequiredMixin, View):
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
            
            # Calculate ITINERARY ETA
            import datetime
            start_time_str = request.session.get('start_time', '08:00')
            stop_mins = int(request.session.get('stop_mins', 15))
            
            current_time = datetime.datetime.strptime(start_time_str, "%H:%M")
            
            # Fetch user's historic ratings for UI highlighting
            historic_ratings = {}
            if request.user.is_authenticated:
                all_addrs = [item['address'] for item in optimized_route]
                ratings_qs = AddressRating.objects.filter(user=request.user, address__in=all_addrs)
                for rq in ratings_qs:
                    historic_ratings[rq.address] = rq.rating
            
            for step in optimized_route:
                step['rating'] = historic_ratings.get(step['address'], 'neutral')
                
                drive_secs = step.get('drive_time_seconds', 0)
                drive_mins = drive_secs // 60
                step['drive_time_str'] = f"{drive_mins} min" if drive_mins > 0 else "N/A"
                
                current_time += datetime.timedelta(seconds=drive_secs)
                step['arrival_time'] = current_time.strftime("%I:%M %p")
                
                # add stop time
                current_time += datetime.timedelta(minutes=stop_mins)
                step['departure_time'] = current_time.strftime("%I:%M %p")
            
            maps_urls = generate_google_maps_urls(optimized_route)
            
            context = {
                'addresses': optimized_route,
                'form': forms.AddressForm(),
                'maps_urls': maps_urls,
                'api_key': api_key,
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
            user = form.save(commit=False)
            user.is_active = False # Manual Admin Approval required
            user.save()
            messages.success(request, f"Account application submitted for {user.username}. You will be able to log in once an Administrator approves the account.")
            return redirect('login')
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

class SaleDiscoveryView(LoginRequiredMixin, View):
    template_name = 'RouteFinderWeb/discover.html'
    
    def get(self, request):
        zip_code = request.GET.get('zip_code')
        radius = request.GET.get('radius', 15)
        mode = request.GET.get('mode', 'garage')
        sort_mode = request.GET.get('sort', 'time')
        sales = []
        
        if zip_code:
            form = forms.SearchForm(initial={'zip_code': zip_code, 'radius': radius})
            
            if mode == 'thrift':
                api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
                sales = scrape_thrift_stores(zip_code, api_key)
            else:
                sales = scrape_sales(zip_code, radius)
                # Apply sorting logic based on start_time_sort (contains date + time)
                if sort_mode == 'time':
                    sales.sort(key=lambda x: x.get('start_time_sort', '9999-12-31 23:59'))
                elif sort_mode == 'time_desc':
                    sales.sort(key=lambda x: x.get('start_time_sort', '0000-01-01 00:00'), reverse=True)
                elif sort_mode == 'title':
                    sales.sort(key=lambda x: x.get('title', '').lower())
            
            if request.user.is_authenticated and sales:
                sale_addrs = [s['address'] for s in sales]
                ratings_qs = AddressRating.objects.filter(user=request.user, address__in=sale_addrs)
                historic_ratings = {rq.address: rq.rating for rq in ratings_qs}
                hidden_addrs = {rq.address for rq in ratings_qs if rq.is_hidden}
                
                # Filter out hidden sales
                sales = [s for s in sales if s['address'] not in hidden_addrs]
                
                for s in sales:
                    s['rating'] = historic_ratings.get(s['address'], 'neutral')
        else:
            form = forms.SearchForm()
            
        return render(request, self.template_name, {'form': form, 'sales': sales, 'mode': mode})
        
    def post(self, request):
        selected_addresses = [addr.strip() for addr in request.POST.getlist('selected_sales') if addr.strip()]
        mode = request.POST.get('mode', 'garage')
        
        if selected_addresses:
            other_addresses = request.session.get('other_addresses', [])
            
            # Extract plain string addresses for duplicate checking
            addr_list = []
            for item in other_addresses:
                if isinstance(item, dict):
                    addr_list.append(item.get('address'))
                else:
                    addr_list.append(item)
                    
            # Ensure other_addresses is a structured list for the new form UI
            structured_addresses = [item if isinstance(item, dict) else {'address': item, 'priority': 0, 'type': 'garage'} for item in other_addresses]
                    
            for new_addr in selected_addresses:
                if new_addr not in addr_list:
                    structured_addresses.append({'address': new_addr, 'priority': 0, 'type': mode})
                    
            request.session['other_addresses'] = structured_addresses
            import json
            # Dump to JSON string so JS can parse it in the template gracefully
            request.session['other_addresses_raw'] = json.dumps(structured_addresses)
            messages.success(request, f"Imported {len(selected_addresses)} sales into the route planner!")
            
        return redirect('main')

class ToggleRatingView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            address = data.get('address')
            rating = data.get('rating')
            
            if not address or rating not in ['bust', 'great', 'neutral']:
                return JsonResponse({'error': 'Invalid data'}, status=400)
                
            obj, created = AddressRating.objects.get_or_create(user=request.user, address=address)
            if rating == 'neutral' and not obj.notes:
                obj.delete()
            else:
                obj.rating = rating
                obj.save()
                
            return JsonResponse({'success': True, 'rating': rating})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class GetZipCodeView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            lat = data.get('lat')
            lon = data.get('lon')
            
            if lat is None or lon is None:
                return JsonResponse({'error': 'Missing coordinates'}, status=400)
                
            zip_code = get_zip_from_coords(lat, lon)
            
            if zip_code:
                return JsonResponse({'success': True, 'zip_code': zip_code})
            else:
                return JsonResponse({'error': 'Could not determine zip code'}, status=404)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class HideSaleView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            address = data.get('address')
            
            if not address:
                return JsonResponse({'error': 'Missing address'}, status=400)
                
            obj, created = AddressRating.objects.get_or_create(
                user=request.user, 
                address=address
            )
            obj.is_hidden = True
            obj.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class GetAddressView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            lat = data.get('lat')
            lon = data.get('lon')
            
            if lat is None or lon is None:
                return JsonResponse({'error': 'Missing coordinates'}, status=400)
                
            from .location_service import get_address_from_coords
            address = get_address_from_coords(lat, lon)
            
            if address:
                return JsonResponse({'success': True, 'address': address})
            else:
                return JsonResponse({'error': 'Could not determine address'}, status=404)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
