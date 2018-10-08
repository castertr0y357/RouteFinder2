import googlemaps

gapi = "AIzaSyC2mfL58CI4oSI31dB9afbJZ5EN_wDQirg"
gmaps = googlemaps.Client(key=gapi)
distance = gmaps.distance_matrix

input_points = []
map_points = []
map_order = []


class Point:
    address = ""
    value = 0

    def __init__(self, address):
        self.address = address
        self.value = 0

    @staticmethod
    def find_distance(point1, point2):
        result = distance(point1.address, point2.address, units="imperial")
        point2.value = result["rows"][0]["elements"][0]["duration"]["value"]  # Value in seconds
        return point2.value

    @staticmethod
    def find_max(points):
        largest = Point("")
        for x in points:
            if x.value > largest.value:
                largest = x
        return largest

    @staticmethod
    def find_min(points):
        smallest = 0
        for x in points:
            if smallest == 0:
                smallest = x
            elif x.value < smallest.value:
                smallest = x
        return smallest

    @staticmethod
    def create_points(points_list):
        for x in points_list:
            map_points.append(Point(x))  # Create point with just address.  Value is initialized to 0
        return

    @staticmethod
    def get_input_points():
        print("Enter addresses, one per line, or hit enter to finish:")
        print("")
        while True:
            point_input = input("Address: ")
            if point_input == "":  # If input is empty
                print("Input points:")
                print(input_points)
                break
            else:
                input_points.append(point_input)

    @staticmethod
    def print_points():
        counter = 1

        left_point = Point("")
        right_point = Point("")

        for x in map_order:  # Go through list and find leftmost point
            if x == "":
                pass
            else:
                left_point = x
                break

        for x in reversed(map_order):  # Go through list and find rightmost point
            if x == "":
                pass
            else:
                right_point = x
                break

        print("")
        print("left point: " + left_point.address)
        print("right point: " + right_point.address)
        print("")

        # Find out if the leftmost point is closer to home than the rightmost point
        # If it is, then print out the points from left to right
        if Point.find_distance(home, left_point) < Point.find_distance(home, right_point):
            for x in map_order:
                if x == "":
                    pass
                else:
                    print(str(counter) + ": " + x.address)
                    counter += 1

        else:  # If the rightmost point is closer to home, print points right to left
            for x in reversed(map_order):
                if x == "":
                    pass
                else:
                    print(str(counter) + ": " + x.address)
                    counter += 1
        return

    @staticmethod
    def create_route():
        for x in range((input_points.__len__() * 2) + 3):  # Append empty spots for index assignment
            map_order.append("")
        center = int(map_order.__len__() / 2)  # Center is close to middle to allow for growth on either side
        left = center - 2
        right = center
        left_open = True
        right_open = True

        print("")
        print("Home address: " + home.address)

        Point.create_points(input_points)

        # Working from shortest 2 points out

        empty_list = ["", ""]
        shortest_points_list = []
        for x in range(map_points.__len__()):
            shortest_points_list.append(empty_list)

        count = 0
        shortest = 0

        for x in map_points:
            for y in map_points:
                if x == y:
                    pass
                else:
                    Point.find_distance(x, y)
            shortest_points_list[count][0] = x
            shortest_points_list[count][1] = Point.find_min(map_points)
            count += 1

        for x in range(shortest_points_list.__len__()):
            if shortest == 0:
                shortest = x
            elif shortest_points_list[x][1].value < shortest_points_list[shortest][1].value:
                    shortest = x

        # Add shortest points to center of map order

        map_order[center] = shortest_points_list[shortest][1]
        map_points.remove(map_order[center])
        print(map_order[center].address)
        map_order[(center - 1)] = shortest_points_list[shortest][0]
        map_points.remove(map_order[(center - 1)])
        print(map_order[(center - 1)].address)

        # Add home address into map points

        map_points.append(home)
        reference = center - 1

        # find left and right points

        for x in range(map_points.__len__()):
            if left_open and right_open:  # If both left and right side do not have home as a point

                # find distances from reference

                for y in map_points:
                    Point.find_distance(map_order[reference], y)

                min_point = Point.find_min(map_points)
                print("")
                print("min_point: " + str(min_point.address))

                # if right point is closer, set right point

                min_value = min_point.value
                if Point.find_distance(map_order[right], min_point) < min_value:
                    print("")
                    print("right side value: " + str(Point.find_distance(min_point, map_order[right])))
                    print("min value: " + str(min_value))
                    print("adding to right")
                    right += 1
                    print("right: " + str(right))
                    reference = right
                    map_order[right] = min_point
                    map_points.remove(min_point)  # remove the minimum point from the map_points list

                    if min_point == home:  # if the next closest point is home...
                        map_order.remove(min_point)  # remove home from map order
                        right_open = False  # close the right side of the map_order list
                        print("Right side is now closed")

                else:  # Set the point on the left side
                    print("")
                    print("right side value: " + str(Point.find_distance(min_point, map_order[right])))
                    print("min value: " + str(min_value))
                    print("adding to left")
                    map_order[left] = min_point
                    map_points.remove(min_point)
                    reference = left
                    left -= 1
                    print("left: " + str(left))

                    if min_point == home:  # if the next closest point is home...
                        map_order.remove(min_point)  # remove home from map order
                        left_open = False  # close the left side of the map order list
                        print("Left side is now closed")

            elif left_open:  # if left side only is open
                print("")
                print("working with left side only")

                for y in map_points:
                    Point.find_distance(map_order[reference], y)

                min_point = Point.find_min(map_points)
                print("")
                print("min point: " + str(min_point.address))
                map_order[left] = min_point
                map_points.remove(min_point)
                reference = left
                left -= 1
                print("left: " + str(left))

            else:  # if right side only is open
                print("")
                print("working with right side only")

                for y in map_points:
                    Point.find_distance(map_order[reference], y)

                min_point = Point.find_min(map_points)
                print("")
                print("min point: " + str(min_point.address))
                right += 1
                print("right: " + str(right))
                reference = right
                map_order[right] = min_point
                map_points.remove(min_point)

        Point.print_points()  # Print out the points for the user.


home_address = input("Please enter your starting address: ")
home = Point(home_address)
Point.get_input_points()
Point.create_route()

