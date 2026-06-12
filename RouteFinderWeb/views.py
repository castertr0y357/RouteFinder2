import json
import datetime
import urllib.parse
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect

import logging
from . import forms
from .models import AddressRating, ScoutIntel
from .route_solver import RouteSolver
from .scraper import scrape_sales, scrape_thrift_stores
from .location_service import get_zip_from_coords
from .ai_service import AIService

logger = logging.getLogger(__name__)

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
        start_address = ""
        if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
            profile = request.user.userprofile
            if profile.home_street:
                parts = [profile.home_street]
                if profile.home_zip: parts.append(profile.home_zip)
                if profile.home_state: parts.append(profile.home_state)
                start_address = ", ".join(parts)
                initial_data['start'] = start_address
            initial_data['stop_mins'] = profile.default_stop_mins
            
        if 'other_addresses' in request.session:
            initial_data['addresses'] = request.session['other_addresses']
            
        form = forms.AddressForm(initial=initial_data)
        
        import json
        context = {
            'form': form,
            'start_address': start_address,
            'stop_mins': initial_data.get('stop_mins', 15),
            'other_addresses_json': json.dumps(request.session.get('other_addresses', []))
        }
        return render(request, self.template_name, context=context)

    def post(self, request):
        start_address = request.POST.get('start_address')
        start_time = request.POST.get('start_time', '08:00')
        stop_mins = int(request.POST.get('stop_mins', 15))
        
        addresses = request.POST.getlist('address[]')
        priorities = request.POST.getlist('priority[]')
        types = request.POST.getlist('type[]')
        titles = request.POST.getlist('title[]')
        descs = request.POST.getlist('desc[]')
        tags_list = request.POST.getlist('tags[]')
        is_treasures = request.POST.getlist('is_treasure[]')
        treasure_reasons = request.POST.getlist('treasure_reason[]')
        is_wishlist_matches = request.POST.getlist('is_wishlist_match[]')
        match_reasons = request.POST.getlist('match_reason[]')
        is_community_events = request.POST.getlist('is_community_event[]')
        
        destinations = []
        for i in range(len(addresses)):
            addr = addresses[i].strip()
            if addr:
                prio = int(priorities[i]) if i < len(priorities) and priorities[i].strip() else 0
                ty = types[i] if i < len(types) and types[i] else 'garage'
                
                # Fetch metadata
                import json
                try:
                    tags = json.loads(tags_list[i]) if i < len(tags_list) else []
                except:
                    tags = []

                destinations.append({
                    'address': addr, 
                    'priority': prio, 
                    'type': ty,
                    'title': titles[i] if i < len(titles) else '',
                    'desc': descs[i] if i < len(descs) else '',
                    'tags': tags,
                    'is_treasure': is_treasures[i] == 'true' if i < len(is_treasures) else False,
                    'treasure_reason': treasure_reasons[i] if i < len(treasure_reasons) else '',
                    'is_wishlist_match': is_wishlist_matches[i] == 'true' if i < len(is_wishlist_matches) else False,
                    'match_reason': match_reasons[i] if i < len(match_reasons) else '',
                    'is_community_event': is_community_events[i] == 'true' if i < len(is_community_events) else False
                })
                
        request.session['start_address'] = start_address
        request.session['other_addresses'] = destinations
        request.session['start_time'] = start_time
        request.session['stop_mins'] = stop_mins
        
        # CLEAR DISCOVERY CACHE: The user has committed to a route
        request.session.pop('discovery_cache_key', None)
        request.session.pop('discovery_results', None)
        
        return HttpResponseRedirect(reverse('results'))


class ResultsView(LoginRequiredMixin, View):
    template_name = 'RouteFinderWeb/route.html'

    def get(self, request):
        start_address = request.session.get('start_address')
        other_addresses = request.session.get('other_addresses')

        if not start_address or not other_addresses:
            return HttpResponseRedirect(reverse('main'))

        return render(request, self.template_name, {
            'start_address': start_address,
            'other_addresses': other_addresses,
            'GOOGLE_MAPS_API_KEY': getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        })

class RouteDataView(LoginRequiredMixin, View):
    def get(self, request):
        start_address = request.session.get('start_address')
        other_addresses = request.session.get('other_addresses')

        if not start_address or not other_addresses:
            return JsonResponse({'success': False, 'error': 'Missing route parameters'}, status=400)

        api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        if not api_key:
            return JsonResponse({'success': False, 'error': 'API Key not configured'}, status=500)

        try:
            solver = RouteSolver(api_key)
            optimized_route = solver.solve(start_address, other_addresses)
            
            import datetime
            start_time_str = request.session.get('start_time', '08:00')
            stop_mins = int(request.session.get('stop_mins', 15))
            
            start_dt = datetime.datetime.strptime(start_time_str, "%H:%M")
            current_time = start_dt
            
            # Map metadata back to optimized route
            metadata_map = {item['address']: item for item in other_addresses}
            
            historic_ratings = {}
            all_addrs = [item['address'] for item in optimized_route] + [start_address]
            ratings_qs = AddressRating.objects.filter(user=request.user, address__in=all_addrs)
            for rq in ratings_qs:
                historic_ratings[rq.address] = rq.rating

            final_itinerary = []
            # Start at Origin
            final_itinerary.append({
                'address': start_address,
                'arrival_time': 'Start',
                'departure_time': current_time.strftime("%I:%M %p"),
                'drive_time_str': 'Origin',
                'is_start': True,
                'rating': historic_ratings.get(start_address, 'neutral'),
                'type': 'home'
            })

            for stop in optimized_route:
                meta = metadata_map.get(stop['address'], {})
                
                # Travel
                current_time += datetime.timedelta(seconds=stop.get('duration_sec', stop.get('drive_time_seconds', 0)))
                arrival_str = current_time.strftime("%I:%M %p")
                
                # Stop
                duration = stop_mins * 3 if meta.get('is_community_event') else stop_mins
                current_time += datetime.timedelta(minutes=duration)
                departure_str = current_time.strftime("%I:%M %p")
                
                final_itinerary.append({
                    'address': stop['address'],
                    'arrival_time': arrival_str,
                    'departure_time': departure_str,
                    'drive_time_str': stop.get('duration_text', f"{stop.get('drive_time_seconds', 0)//60} mins"),
                    'is_start': False,
                    'rating': historic_ratings.get(stop['address'], 'neutral'),
                    'title': meta.get('title', ''),
                    'desc': meta.get('desc', ''),
                    'tags': meta.get('tags', []),
                    'is_treasure': meta.get('is_treasure', False),
                    'treasure_reason': meta.get('treasure_reason', ''),
                    'is_wishlist_match': meta.get('is_wishlist_match', False),
                    'match_reason': meta.get('match_reason', '')
                })

            maps_urls = generate_google_maps_urls(final_itinerary)
            
            # MISSION ACCOMPLISHED: Clear 'The Vault' (Saved Intel) once a route is executed/finalized
            ScoutIntel.objects.filter(user=request.user).delete()
            
            return JsonResponse({
                'success': True, 
                'itinerary': final_itinerary,
                'google_maps_urls': maps_urls
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

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
        refresh = request.GET.get('refresh') == 'true'
        
        # If no zip code provided in URL, try to use user's home zip
        if not zip_code and request.user.is_authenticated:
            zip_code = getattr(request.user.userprofile, 'home_zip', '')

        form = forms.SearchForm(initial={'zip_code': zip_code, 'radius': radius})
            
        # Check if saved intel exists for this user
        saved_intel_exists = ScoutIntel.objects.filter(user=request.user).exists()
        
        context = {
            'form': form,
            'mode': mode,
            'zip_code': zip_code,
            'radius': radius,
            'sort': sort_mode,
            'perform_search': bool(zip_code and refresh),
            'saved_intel_exists': saved_intel_exists,
            'is_authenticated': request.user.is_authenticated,
            'GOOGLE_MAPS_API_KEY': getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        }
        return render(request, self.template_name, context)

    def post(self, request):
        selected_addresses = [addr.strip() for addr in request.POST.getlist('selected_sales') if addr.strip()]
        mode = request.POST.get('mode', 'garage')
        
        # Get the cached discovery results to pull metadata from
        cached_results = request.session.get('discovery_results', [])
        cached_map = {s['address']: s for s in cached_results}
        
        if selected_addresses:
            other_addresses = request.session.get('other_addresses', [])
            
            # Extract plain string addresses for duplicate checking
            addr_list = []
            for item in other_addresses:
                if isinstance(item, dict):
                    addr_list.append(item.get('address'))
                else:
                    addr_list.append(item)
                    
            # Ensure other_addresses is a structured list
            structured_addresses = [item if isinstance(item, dict) else {'address': item, 'priority': 0, 'type': 'garage'} for item in other_addresses]
                    
            for new_addr in selected_addresses:
                if new_addr not in addr_list:
                    # Enrich with metadata if available in cache
                    metadata = cached_map.get(new_addr, {})
                    entry = {
                        'address': new_addr, 
                        'priority': 0, 
                        'type': mode,
                        'title': metadata.get('title', ''),
                        'desc': metadata.get('desc', ''),
                        'tags': metadata.get('tags', []),
                        'is_treasure': metadata.get('is_treasure', False),
                        'treasure_reason': metadata.get('treasure_reason', ''),
                        'is_wishlist_match': metadata.get('is_wishlist_match', False),
                        'match_reason': metadata.get('match_reason', ''),
                        'is_community_event': metadata.get('is_community_event', False)
                    }
                    structured_addresses.append(entry)
                    
            request.session['other_addresses'] = structured_addresses
            import json
            # Dump to JSON string so JS can parse it in the template gracefully
            request.session['other_addresses_raw'] = json.dumps(structured_addresses)
            messages.success(request, f"Imported {len(selected_addresses)} sales into the route planner!")
            
        return redirect('main')

class DiscoveryDataView(LoginRequiredMixin, View):
    def get(self, request):
        zip_code = request.GET.get('zip_code')
        radius = request.GET.get('radius', 15)
        mode = request.GET.get('mode', 'garage')
        sort_mode = request.GET.get('sort', 'time')
        force_refresh = request.GET.get('refresh') == 'true'
        
        if not zip_code:
            return JsonResponse({'success': False, 'error': 'Zip code required'})

        # Create a unique fingerprint for this search
        search_fingerprint = f"{zip_code}_{radius}_{mode}_{sort_mode}"
        
        # Check if we have this exact search cached in the session
        cached_fingerprint = request.session.get('discovery_cache_key')
        cached_results = request.session.get('discovery_results')
        
        # Fetch Route Planner addresses for "Already Imported" check
        planner_addresses = set()
        for item in request.session.get('other_addresses', []):
            if isinstance(item, dict):
                planner_addresses.add(item.get('address'))
            else:
                planner_addresses.add(item)

        cached_timestamp = request.session.get('discovery_timestamp')
        
        # Cache Expiry Hardening (2 hours)
        is_cache_stale = False
        if cached_timestamp:
            try:
                cached_dt = datetime.datetime.fromisoformat(cached_timestamp)
                if (datetime.datetime.now() - cached_dt).total_seconds() > 7200: # 2 hours
                    is_cache_stale = True
                    logger.info(f"Cache expired for {search_fingerprint}. Forcing fresh scout.")
            except:
                is_cache_stale = True

        # Check if we should load from 'The Vault' (Saved Intel)
        if request.GET.get('mode') == 'saved':
            intel = ScoutIntel.objects.filter(user=request.user).first()
            if intel:
                logger.info(f"Loading 'The Vault' intel for {request.user.username}")
                return JsonResponse({'success': True, 'sales': intel.data, 'cached': True, 'timestamp': intel.updated_at.isoformat()})
            return JsonResponse({'success': False, 'error': 'No saved intel found'})

        if not force_refresh and not is_cache_stale and cached_fingerprint == search_fingerprint and cached_results:
            logger.info(f"Serving discovery results from cache for {search_fingerprint}")
            
            # Re-check import status even for cached results
            if isinstance(cached_results, list):
                for s in cached_results:
                    if isinstance(s, dict):
                        s['is_in_planner'] = s.get('address') in planner_addresses
                
            return JsonResponse({'success': True, 'sales': cached_results, 'cached': True})

        # If no cache or force refresh, perform the full scouting operation
        try:
            if mode == 'thrift':
                api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
                sales = scrape_thrift_stores(zip_code, api_key)
                
                # --- DONATION SURGE ENGINE ---
                try:
                    moving_sales_count = 0
                    local_garage_sales = scrape_sales(zip_code, radius=5)
                    if local_garage_sales:
                        ai = AIService(user=request.user)
                        garage_analysis = ai.analyze_listings_batch([s.get('desc', '') for s in local_garage_sales[:10]])
                        moving_sales_count = sum(1 for a in garage_analysis if a.get('is_moving_sale'))
                except Exception as se:
                    logger.error(f"Surge Engine Error: {se}")
                    moving_sales_count = 0

                if sales:
                    ai = AIService(user=request.user)
                    try:
                        thrift_analysis = ai.analyze_thrift_batch(sales)
                    except Exception as ai_err:
                        logger.error(f"AI Thrift Batch Analysis failed: {ai_err}")
                        thrift_analysis = []
                        
                    for i, s in enumerate(sales):
                        analysis = thrift_analysis[i] if (i < len(thrift_analysis) and thrift_analysis[i]) else {}
                        s['tags'] = analysis.get('tags', [])
                        s['is_potential_goldmine'] = analysis.get('is_potential_goldmine', False)
                        s['profit_rating'] = analysis.get('profit_rating', 'None')
                        s['profit_reason'] = analysis.get('profit_reason', '')
                        s['surge_count'] = moving_sales_count
                        s['is_surge_potential'] = moving_sales_count >= 2
                        s['is_treasure'] = False
                        s['is_bust_candidate'] = False
                        s['is_wishlist_match'] = False
            else:
                sales = scrape_sales(zip_code, radius)

            if not isinstance(sales, list):
                sales = []
                
            # Apply sorting logic
            if sort_mode == 'time':
                sales.sort(key=lambda x: x.get('start_time_sort', '9999-12-31 23:59') if isinstance(x, dict) else '')
            elif sort_mode == 'time_desc':
                sales.sort(key=lambda x: x.get('start_time_sort', '0000-01-01 00:00') if isinstance(x, dict) else '', reverse=True)
            elif sort_mode == 'title':
                sales.sort(key=lambda x: x.get('title', '').lower() if isinstance(x, dict) else '')
            
            if request.user.is_authenticated and sales:
                sale_addrs = [s.get('address') for s in sales if isinstance(s, dict)]
                ratings_qs = AddressRating.objects.filter(user=request.user, address__in=sale_addrs)
                historic_ratings = {rq.address: rq.rating for rq in ratings_qs}
                hidden_addrs = {rq.address for rq in ratings_qs if rq.is_hidden}
                
                # Filter out hidden sales
                sales = [s for s in sales if isinstance(s, dict) and s.get('address') not in hidden_addrs]
                
                if mode != 'thrift':
                    ai = AIService(user=request.user)
                    bust_history = list(AddressRating.objects.filter(user=request.user, rating='bust').exclude(notes='').values_list('notes', flat=True)[:10])
                    wishlist = getattr(request.user.userprofile, 'looking_for', '')
                    
                    # Batch analyze garage sales
                    descriptions = [s.get('desc', '') for s in sales if isinstance(s, dict)]
                    try:
                        ai_analysis = ai.analyze_listings_batch(descriptions, bust_history=bust_history, wishlist=wishlist)
                    except Exception as ai_err:
                        logger.error(f"AI Garage Batch Analysis failed: {ai_err}")
                        ai_analysis = []
                    
                    for i, s in enumerate(sales):
                        analysis = ai_analysis[i] if (i < len(ai_analysis) and ai_analysis[i]) else {}
                        s['tags'] = analysis.get('tags', [])
                        s['is_treasure'] = analysis.get('is_treasure', False)
                        s['treasure_reason'] = analysis.get('treasure_reason', "")
                        s['is_bust_candidate'] = analysis.get('is_bust_candidate', False)
                        s['bust_reason'] = analysis.get('bust_reason', "")
                        s['is_wishlist_match'] = analysis.get('is_wishlist_match', False)
                        s['match_reason'] = analysis.get('match_reason', "")
                        s['is_potential_goldmine'] = analysis.get('is_potential_goldmine', False)
                        s['profit_rating'] = analysis.get('profit_rating', 'None')
                        s['is_moving_sale'] = analysis.get('is_moving_sale', False)
                        title_lower = s.get('title', '').lower()
                        if any(word in title_lower for word in ['community', 'subdivision', 'sub-division', 'neighborhood']):
                            s['is_bust_candidate'] = False
                            s['is_community_event'] = True
                        else:
                            s['is_community_event'] = False

                    # AI Clustering
                    ai_clusters = ai.cluster_neighborhoods([s.get('title', '') for s in sales])
                    active_neighborhoods = set()
                    for cluster in ai_clusters:
                        indices = cluster.get('indices', [])
                        if any(sales[idx]['address'] in planner_addresses for idx in indices if idx < len(sales)):
                            active_neighborhoods.add(cluster.get('name', ''))

                    for cluster in ai_clusters:
                        c_name = cluster.get('name', 'Community Event')
                        indices = cluster.get('indices', [])
                        if len(indices) >= 2:
                            for idx in indices:
                                if idx < len(sales):
                                    sales[idx]['is_potential_duplicate'] = True
                                    sales[idx]['duplicate_count'] = len(indices)
                                    sales[idx]['neighborhood_name'] = c_name
                                    sales[idx]['community_is_active'] = c_name in active_neighborhoods

                # Final metadata loop
                for s in sales:
                    s['rating'] = historic_ratings.get(s.get('address'), 'neutral')
                    s['is_in_planner'] = s.get('address') in planner_addresses

                # Persist to 'The Vault' (DB) and Session Cache
                ScoutIntel.objects.update_or_create(
                    user=request.user,
                    defaults={'data': sales, 'metadata': {'zip_code': zip_code, 'radius': radius}}
                )
                request.session['discovery_cache_key'] = search_fingerprint
                request.session['discovery_results'] = sales
                request.session['discovery_timestamp'] = datetime.datetime.now().isoformat()
            
            return JsonResponse({'success': True, 'sales': sales, 'cached': False})
            
        except Exception as e:
            logger.exception(f"Discovery Engine Failure: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

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

class RemoveAddressView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            address = data.get('address')
            
            if not address:
                return JsonResponse({'error': 'Missing address'}, status=400)
                
            other_addresses = request.session.get('other_addresses', [])
            
            # Filter out the matching address
            new_list = []
            for item in other_addresses:
                if isinstance(item, dict):
                    if item.get('address') != address:
                        new_list.append(item)
                elif item != address:
                    new_list.append(item)
            
            request.session['other_addresses'] = new_list
            # Update the raw JSON for the template as well
            request.session['other_addresses_raw'] = json.dumps(new_list)
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ClearRouteView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            request.session['other_addresses'] = []
            request.session['other_addresses_raw'] = '[]'
            return JsonResponse({'success': True})
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
