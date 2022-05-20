# local imports
from .Distance import Distance
from .Point import Point

# Python imports
from threading import Thread
from concurrent.futures.thread import ThreadPoolExecutor


class LinearRoute(Thread):

    def __int__(self, home, points):
        Thread.__init__(self)
        self.home = home
        self.points = points

    def run(self):
        return self.shortest_path_first(self.home, self.points)

    @staticmethod
    def shortest_path_first(home: Point, points: list):
        route_order = []

        while points.__len__() > 0:
            distance_list = []
            lowest = None
            for point in points:
                if route_order.__len__() < 1:
                    distance = Distance(home, point)
                    distance_list.append(distance)
                else:
                    distance = Distance(route_order[-1], point)
                    distance_list.append(distance)
                for x in distance_list:
                    x.start()
                for x in distance_list:
                    x.join(60)
            for distance in distance_list:
                if lowest is None:
                    lowest = distance
                else:
                    if lowest.value > distance.value:
                        lowest = distance
            route_order.append(lowest)


        return route_order

    @staticmethod
    def find_first_point(home: Point, points: list):
        first_point = None
        shortest_distance = None
        distance_list = []




        for distance in distance_list:
            if shortest_distance is None:
                shortest_distance = distance
            else:
                if shortest_distance.value > distance.value:
                    shortest_distance = distance

        return first_point
