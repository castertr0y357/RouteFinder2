from geopy.geocoders import Nominatim
from geopy.exc import GeopyError

def get_zip_from_coords(lat, lon):
    """
    Reverse geocodes latitude and longitude to find a zip code using Nominatim (OSM).
    Returns the zip code as a string, or None if not found.
    """
    try:
        # User-agent is required by Nominatim's usage policy
        geolocator = Nominatim(user_agent="routefinder_app")
        location = geolocator.reverse((lat, lon), addressdetails=True, timeout=10)
        
        if location and 'address' in location.raw:
            address = location.raw['address']
            # Postal code can be 'postcode' or 'postal-code' depending on the region
            return address.get('postcode') or address.get('postal-code')
            
    except (GeopyError, Exception) as e:
        print(f"Reverse geocoding error: {str(e)}")
        
    return None

def get_address_from_coords(lat, lon):
    """
    Reverse geocodes latitude and longitude to find a full address using Nominatim (OSM).
    Returns the formatted address as a string, or None if not found.
    """
    try:
        geolocator = Nominatim(user_agent="routefinder_app")
        location = geolocator.reverse((lat, lon), timeout=10)
        
        if location:
            return location.address
            
    except (GeopyError, Exception) as e:
        print(f"Reverse geocoding error: {str(e)}")
        
    return None
