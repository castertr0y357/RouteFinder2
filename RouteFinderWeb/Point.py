import googlemaps
from threading import Thread

gapi = "AIzaSyC2mfL58CI4oSI31dB9afbJZ5EN_wDQirg"
gmaps = googlemaps.Client(key=gapi)
distance = gmaps.distance_matrix
location = gmaps.find_place


class Point(Thread):
    address = ""
    value = 0

    def __init__(self, address):
        Thread.__init__(self)
        self.address = address
        self.value = 0

    def is_address_good(self):
        result = location(self.address, 'textquery')
        if result["status"] == "OK":
            return True
        else:
            return False

    def find_distance(self, point2):
        result = distance(self.address, point2.address, units="imperial")
        point2.value = result["rows"][0]["elements"][0]["duration"]["value"]  # Value in seconds
        return point2.value
