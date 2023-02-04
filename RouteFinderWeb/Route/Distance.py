# Python imports
from threading import Thread

# Googlemaps imports
import googlemaps

# Local imports
from RouteFinderWeb.local_settings import api_key
from .Point import Point


class Distance(Thread):
    # Need reusable class to store point and distance
    def __init__(self, point1: Point, point2: Point):
        Thread.__init__(self)
        self.point1 = point1
        self.point2 = point2
        self.value = 0
        self.gmaps = googlemaps.Client(key=api_key)
        self.start()

    def run(self):
        self.value = self.find_distance(self.point1, self.point2)

    def find_distance(self, point1, point2):
        distance = self.gmaps.distance_matrix
        result = distance(point1.address, point2.address, units="imperial")
        value = result["rows"][0]["elements"][0]["duration"]["value"]  # Value in seconds
        return value, point2
