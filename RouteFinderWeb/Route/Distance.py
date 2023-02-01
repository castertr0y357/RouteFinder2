import googlemaps
from threading import Thread

gapi = "AIzaSyC2mfL58CI4oSI31dB9afbJZ5EN_wDQirg"
gmaps = googlemaps.Client(key=gapi)
distance = gmaps.distance_matrix


class Distance(Thread):
    origin = None
    destination = None
    value = 0

    def __init__(self, point_1, point_2):
        Thread.__init__(self)
        self.origin = point_1
        self.destination = point_2

    def run(self):
        self.value = self.find_distance()
        return self

    def find_distance(self):
        result = distance(self.origin.address, self.destination.address, units="imperial")
        value = result["rows"][0]["elements"][0]["duration"]["value"]  # Value in seconds
        return value
