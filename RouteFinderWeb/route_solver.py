import googlemaps
from datetime import datetime

class RouteSolver:
    def __init__(self, api_key):
        self.gmaps = googlemaps.Client(key=api_key)

    def solve(self, start_address, addresses_data):
        """
        Solves the TSP for the given addresses across defined priority tiers.
        Returns a list of dictionaries with optimal order and leg durations.
        """
        import collections
        buckets = collections.defaultdict(list)
        type_lookup = {start_address: 'home'}
        
        for item in addresses_data:
            prio = int(item.get('priority', 0))
            addr = item['address']
            buckets[prio].append(addr)
            type_lookup[addr] = item.get('type', 'garage')
            
        # determine order of bucket keys: 1, 2, 3... then 0
        keys = sorted([k for k in buckets.keys() if k > 0])
        if 0 in buckets:
            keys.append(0)
            
        optimized_route = []
        current_start = start_address
        
        for k in keys:
            bucket_addrs = buckets[k]
            if not bucket_addrs:
                continue
                
            all_addrs = [current_start] + bucket_addrs
            distance_matrix = self._get_distance_matrix(all_addrs)
            route_indices = self._solve_tsp(distance_matrix)
            
            for step in range(1, len(route_indices)): # skip 0 which is current_start
                cur_node = route_indices[step]
                addr = all_addrs[cur_node]
                
                prev_node = route_indices[step-1]
                drive_secs = distance_matrix[prev_node][cur_node]
                
                optimized_route.append({
                    'address': addr,
                    'drive_time_seconds': drive_secs,
                    'priority': k,
                    'type': type_lookup.get(addr, 'garage')
                })
                
            last_idx = route_indices[-1]
            current_start = all_addrs[last_idx]
            
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
