import googlemaps
from datetime import datetime

class RouteSolver:
    def __init__(self, api_key):
        self.gmaps = googlemaps.Client(key=api_key)

    def solve(self, start_address, other_addresses):
        """
        Solves the TSP for the given addresses.
        Returns a list of addresses in the optimal order.
        """
        # Combine all addresses
        all_addresses = [start_address] + other_addresses
        
        # Get distance matrix
        distance_matrix = self._get_distance_matrix(all_addresses)
        
        # Solve TSP using 2-Opt
        route_indices = self._solve_tsp(distance_matrix)
        
        # Reconstruct route
        optimized_route = [all_addresses[i] for i in route_indices]
        
        return optimized_route

    def _get_distance_matrix(self, locations):
        """
        Fetches the distance matrix from Google Maps API.
        Returns a 2D list of distances (in seconds).
        """
        matrix = []
        # Google Maps Distance Matrix API has limits on elements per request (100 max).
        # For simplicity, we assume the number of locations is small (< 10).
        # If it's larger, we would need to batch requests.
        
        result = self.gmaps.distance_matrix(locations, locations, mode="driving", units="imperial")
        
        if result['status'] != 'OK':
            raise Exception("Error fetching distance matrix")

        rows = result['rows']
        for row in rows:
            row_distances = []
            for element in row['elements']:
                if element['status'] == 'OK':
                    # Use duration value (seconds) for optimization
                    row_distances.append(element['duration']['value'])
                else:
                    # If route not found, use a very large number
                    row_distances.append(float('inf'))
            matrix.append(row_distances)
            
        return matrix

    def _solve_tsp(self, distance_matrix):
        """
        Implements 2-Opt heuristic to find a near-optimal route.
        """
        num_points = len(distance_matrix)
        route = list(range(num_points))
        
        improved = True
        while improved:
            improved = False
            for i in range(1, num_points - 1):
                for j in range(i + 1, num_points):
                    if j - i == 1: continue # No change for adjacent edges
                    
                    new_route = route[:]
                    # Reverse the segment between i and j
                    new_route[i:j] = route[j-1:i-1:-1]
                    
                    if self._calculate_total_distance(new_route, distance_matrix) < self._calculate_total_distance(route, distance_matrix):
                        route = new_route
                        improved = True
                        
        return route

    def _calculate_total_distance(self, route, distance_matrix):
        total_dist = 0
        for i in range(len(route) - 1):
            from_idx = route[i]
            to_idx = route[i+1]
            total_dist += distance_matrix[from_idx][to_idx]
        return total_dist
