import googlemaps
from threading import Thread

gapi = "AIzaSyC2mfL58CI4oSI31dB9afbJZ5EN_wDQirg"
gmaps = googlemaps.Client(key=gapi)
location = gmaps.find_place


class Point(Thread):
    address = ""
    valid_address = None

    def __init__(self, address):
        Thread.__init__(self)
        self.address = address
        self.value = 0

    def run(self):
        self.valid_address = self.is_address_good()

    def is_address_good(self):
        result = location(self.address, 'textquery')
        if result["status"] == "OK":
            return True
        else:
            return False
