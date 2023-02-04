# Googlemaps imports
import googlemaps

# Local imports
from RouteFinderWeb.local_settings import api_key


class Point:
    address = ""
    value = 0

    def __init__(self, address):
        self.address = address
        self.gmaps = googlemaps.Client(key=api_key)
        self.address_good = self.is_address_good()

    def is_address_good(self):
        location = self.gmaps.find_place
        result = location(self.address, 'textquery')
        if result["status"] == "OK":
            return True
        else:
            return False
