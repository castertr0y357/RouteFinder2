import googlemaps
gapi = "AIzaSyC2mfL58CI4oSI31dB9afbJZ5EN_wDQirg"
gmaps = googlemaps.Client(key=gapi)
distance = gmaps.distance_matrix


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
        smallest = Point.find_max(points)
        for x in points:
            if x.value < smallest.value:
                smallest = x
        return smallest

    @staticmethod
    def create_points(points_list):
        for x in points_list:
            map_points.append(Point(x))
        return

    @staticmethod
    def print_points():
        counter = 1
        first_point = map_order[0]
        last_point = map_order[(map_order.__len__() - 1)]

        '''for x in map_order:
            if x == "":
                pass
            else:
                first_point = x
                break

        for x in reversed(map_order):
            if x == "":
                pass
            else:
                last_point = x
                break
                '''

        # if Point.find_distance(home, first_point) < Point.find_distance(home, last_point):
        for x in map_order:
            if x == home:
                pass
            else:
                print(str(counter) + ": " + x.address)
                counter += 1

        '''else:
            for x in reversed(map_order):
                if x == "":
                    pass
                else:
                    print(str(counter) + ": " + x.address)
                    counter += 1
                    '''
        return

    @staticmethod
    def create_route():
        # center = int(map_order.__len__() / 2)
        left = 0
        right = map_order.__len__() - 1
        left_open = True
        right_open = True

        Point.create_points(input_points)
        map_order[right] = home

        # No need to work from furthest point.  Can work from home point and build out list

        '''for x in map_points:
            Point.find_distance(home, x)

        max_point = Point.find_max(map_points)
        
        # test_order[center] = max_point.address
        print("")
        print("center address:")
        print(map_order[center].address)

        # test_order[center] = max_point.address

        # remove furthest point and add home into map points

        # map_points.remove(max_point)
        # map_points.append(home)'''

        reference = right

        # find left and right points

        for x in range(map_points.__len__()):
            if left_open and right_open:  # If both left and right side do not have home as a point

                # find distances from reference

                for y in map_points:
                    Point.find_distance(map_order[reference], y)

                min_point = Point.find_min(map_points)
                print("")
                print("min_point")
                print(min_point.address)
                # print(min_point.address)

                # if right point is closer, set right point

                min_value = min_point.value
                if Point.find_distance(map_order[right], min_point) < min_value:
                    print("")
                    print("right side value")
                    print(Point.find_distance(min_point, map_order[right]))
                    print("min value")
                    print(min_value)
                    print("adding to right")
                    right -= 1
                    reference = right
                    map_order[right] = min_point
                    # test_order[right] = min_point.address
                    map_points.remove(min_point)  # remove the minimum point from the map_points list

                    '''if min_point == home:
                        map_order.remove(min_point)  # remove home from map order
                        # test_order.remove(min_point.address)
                        right_open = False  # close the right side of the map_order list
                        '''

                else:  # Set the point on the left side
                    print("")
                    print("right side value")
                    print(Point.find_distance(min_point, map_order[right]))
                    print("min value")
                    print(min_value)
                    print("adding to left")
                    map_order[left] = min_point
                    # test_order[left] = min_point.address
                    map_points.remove(min_point)
                    # test_order.remove(min_point.address)
                    reference = left
                    left += 1

                    '''if min_point == home:
                        map_order.remove(min_point)  # remove home from map order
                        # test_order.remove(min_point.address)
                        left_open = False  # close the left side of the map order list
                        '''

            elif left_open:  # if left side only is open

                for y in map_points:
                    Point.find_distance(map_order[reference], y)

                min_point = Point.find_min(map_points)
                # print(min_point.address)
                map_order[left] = min_point
                # test_order[left] = min_point.address
                map_points.remove(min_point)
                reference = left
                left += 1

            else:  # if right side only is open

                for y in map_points:
                    Point.find_distance(map_order[reference], y)

                min_point = Point.find_min(map_points)
                # print(min_point.address)
                right -= 1
                reference = right
                map_order[right] = min_point
                # test_order[right] = min_point.address
                map_points.remove(min_point)

            '''print("")
            print("test_order")
            print(test_order)'''
            print(map_order)

        print(map_order)

        print("")
        Point.print_points()  # Print out the points for the user.


pointa = "2338 Thunder Rd, Durham, NC 27712"
pointb = "2509 Palmer Ct, Wake Forest, NC 27587"
pointc = "Cedar Creek, Wendell, NC 27591"
pointd = "136 Pineland Cir, Raleigh, NC 27606"
pointe = "5479 Cornwallis Rd, Garner, NC 27529"
pointf = "Cedar Creek, Wendell, NC 27591"
pointg = "259 Hillsboro St, Pittsboro, NC 27312"
pointh = "4644 Randleman Rd, Greensboro, NC 27406"
pointi = "seattle wa"

home = Point("141 daneborg rd durham nc 27703")

input_points = [pointa, pointb, pointc, pointd, pointe, pointg, pointh]
map_points = []
map_order = [""] * ((input_points.__len__()) + 1)
# map_order = [""] * ((input_points.__len__() * 2) + 1)
# test_order = [""] * ((input_points.__len__() * 2) + 1)
Point.create_route()

"""furthest = Point.find_max(arr)
#closest = Point.find_min(arr)
#print(furthest.address)
#print(closest.address)
Point.create_points(input_points)
print(map_points[1].address)
Point.find_distance(map_points[0], map_points[1])
print(map_points[1].value)"""

