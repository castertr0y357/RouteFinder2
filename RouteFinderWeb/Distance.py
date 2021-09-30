import googlemaps
from threading import Thread

gapi = "AIzaSyC2mfL58CI4oSI31dB9afbJZ5EN_wDQirg"
gmaps = googlemaps.Client(key=gapi)
distance = gmaps.distance_matrix


class Distance(Thread):
    point_1 = None
    point_2 = None
    value = 0

    def __init__(self, point_1, point_2):
        Thread.__init__(self)
        self.point_1 = point_1
        self.point_2 = point_2

    def run(self):
        self.value = self.find_distance()

    def find_distance(self):
        result = distance(self.point_1.address, self.point_2.address, units="imperial")
        value = result["rows"][0]["elements"][0]["duration"]["value"]  # Value in seconds
        return value
