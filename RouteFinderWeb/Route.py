import googlemaps
from threading import Thread
from .Point import Point


class Route(Thread):

    def __init__(self, home, addresses):
        Thread.__init__(self)
        self.points = []
        self.map_order = []
        self.home = home

        self.create_points(addresses)

    def find_max(self):
        largest = Point("")
        for x in self.points:
            if x.value > largest.value:
                largest = x
        return largest

    def find_min(self):
        smallest = 0
        for x in self.points:
            print("find min x.address: " + str(x.address))
            print("find min x.value: " + str(x.value))
            if x.value == 0:
                pass
            elif smallest == 0:
                smallest = x
            elif x.value < smallest.value:
                smallest = x
        print("find_min smallest: " + str(smallest.address))
        print("")
        return smallest

    def create_points(self, points_list):
        for x in points_list:
            self.points.append(Point(x))  # Create point with just address.  Value is initialized to 0
        return

    def print_points(self, home):
        map_order = self.map_order

        left_point = map_order[0]
        right_point = map_order[(map_order.__len__() - 1)]

        print("")
        print("left point: " + left_point.address)
        print("right point: " + right_point.address)
        print("")

        # Find out if the leftmost point is closer to home than the rightmost point
        # If it is, then print out the points from left to right
        if home.find_distance(left_point) < home.find_distance(right_point):
            print("Left point is closer")
            print("")

            return map_order

        else:  # If the rightmost point is closer to home, print points right to left
            print("Left point is closer")
            print("")

            return reversed(map_order)

    def create_route(self, home, input_points):
        # print(input_points)
        map_order = self.map_order

        for x in range((input_points.__len__() * 2) + 3):  # Append empty spots for index assignment
            map_order.append("")
        print(map_order)
        center = int(map_order.__len__() / 2)  # Center is close to middle to allow for growth on either side
        left = center - 2
        right = center
        global left_open, right_open
        left_open = True
        right_open = True

        print("Home address: " + home.address)
        print("")

        map_points = self.points

        # Working from shortest 2 points out

        empty_list = ["", ""]
        shortest_points_list = []
        for x in range(map_points.__len__()):
            shortest_points_list.append(empty_list)

        # print("Shortest points list: ")
        # print(shortest_points_list)

        count = 0
        shortest = 0

        for x in map_points:
            print("count: " + str(count))
            print("")
            print("X address: " + x.address)
            for y in map_points:
                print("Y address: " + y.address)
                if x == y:
                    y.value = 0
                    pass
                else:
                    x.find_distance(y)
                    print("y value: " + str(y.value))
                print("")
            shortest_points_list[count][0] = x
            print("Shortest 0: " + shortest_points_list[count][0].address)
            shortest_points_list[count][1] = self.find_min()
            print("Shortest 1: " + shortest_points_list[count][1].address)
            print("")
            count += 1
        """
        print("Shortest points list: ")
        for x in range(shortest_points_list.__len__()):
            print(x)
            print("x[0] = " + shortest_points_list[x][0].address)
            print("x[1] = " + shortest_points_list[x][1].address)
        """

        for x in range(shortest_points_list.__len__()):
            # print("shortest: " + str(shortest))
            # print("x: " + str(x))
            if shortest_points_list[x][1].value == 0:
                pass
            elif shortest == 0:
                shortest = x
            elif shortest_points_list[x][1].value < shortest_points_list[shortest][1].value:
                shortest = x
        """
        print("Shortest points list: ")
        for x in range(shortest_points_list.__len__()):
            print(x)
            print("x[0] = " + shortest_points_list[x][0].address)
            print("x[1] = " + shortest_points_list[x][1].address)
        """
        # print(shortest_points_list)

        # Add shortest points to center of map order

        map_order[center] = shortest_points_list[shortest][1]
        print("Center address: " + map_order[center].address)
        map_points.remove(map_order[center])
        map_order[(center - 1)] = shortest_points_list[shortest][0]
        print("Center -1 address: " + map_order[(center - 1)].address)
        print("")
        map_points.remove(map_order[(center - 1)])

        # Add home address into map points

        map_points.append(home)
        global reference
        reference = center - 1

        # find left and right points

        for x in range(map_points.__len__()):
            print("reference: " + str(reference))
            print(map_order[reference])
            print("")

            if left_open and right_open:  # If both left and right side do not have home as a point

                # find distances from reference

                for y in map_points:
                    Point.find_distance(map_order[reference], y)

                min_point = self.find_min()
                print("min_point: " + str(min_point.address))
                print("")

                # if right point is closer, set right point

                min_value = min_point.value
                if map_order[right].find_distance(min_point) < min_value:
                    print("right side value: " + str(min_point.find_distance(map_order[right])))
                    print("min value: " + str(min_value))
                    print("adding to right")
                    right += 1
                    print("right: " + str(right))
                    print("")
                    reference = right
                    map_order[right] = min_point
                    map_points.remove(min_point)  # remove the minimum point from the map_points list

                    if min_point == home:  # if the next closest point is home...
                        map_order.remove(min_point)  # remove home from map order
                        right_open = False  # close the right side of the map_order list
                        reference = left + 1
                        print("right_open: " + str(right_open))
                        print("Right side is now closed")
                        print("")

                else:  # Set the point on the left side
                    print("right side value: " + str(Point.find_distance(min_point, map_order[right])))
                    print("min value: " + str(min_value))
                    print("adding to left")
                    map_order[left] = min_point
                    map_points.remove(min_point)
                    reference = left
                    left -= 1
                    print("left: " + str(left))
                    print("")

                    if min_point == home:  # if the next closest point is home...
                        map_order.remove(min_point)  # remove home from map order
                        left_open = False  # close the left side of the map order list
                        reference = right - 1
                        print("left_open: " + str(left_open))
                        print("Left side is now closed")
                        print("")

            elif left_open:  # if left side only is open
                print("working with left side only")
                print("")

                for y in map_points:
                    Point.find_distance(map_order[reference], y)

                min_point = Point.find_min(map_points)
                print("min point: " + str(min_point.address))
                map_order[left] = min_point
                map_points.remove(min_point)
                reference = left
                left -= 1
                print("left: " + str(left))
                print("")

            else:  # if right side only is open
                print("working with right side only")
                print("")

                for y in map_points:
                    Point.find_distance(map_order[reference], y)

                min_point = Point.find_min(map_points)
                print("min point: " + str(min_point.address))
                right += 1
                print("right: " + str(right))
                print("")
                reference = right
                map_order[right] = min_point
                map_points.remove(min_point)

        # print(map_order)

        for x in map_order:
            if x == '':
                map_order.remove(x)

        # print(map_order)

        for x in reversed(map_order):
            if x == '':
                map_order.remove(x)

        # print(map_order)

        return map_order
