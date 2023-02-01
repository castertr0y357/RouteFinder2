# local imports
from .Distance import Distance
from .Point import Point

# Python imports
from threading import Thread
from concurrent.futures.thread import ThreadPoolExecutor


class RoundTripRoute(Thread):

    def __int__(self, home, points):
        Thread.__init__(self)
        self.home = home
        self.points = points

    def run(self):
        pass
