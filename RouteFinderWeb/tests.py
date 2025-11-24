from django.test import TestCase
from unittest.mock import MagicMock, patch
from .route_solver import RouteSolver

class RouteSolverTests(TestCase):
    def setUp(self):
        self.api_key = "test_key"
        self.start_address = "Start"
        self.other_addresses = ["A", "B", "C"]

    @patch('googlemaps.Client')
    def test_solve_tsp(self, mock_gmaps):
        # Mock the distance matrix response
        # Distances: Start->A=10, Start->B=15, Start->C=20
        # A->B=35, A->C=25
        # B->C=30
        # Optimal route should be Start -> A -> C -> B (Total: 10 + 25 + 30 = 65) 
        # Wait, let's make a simpler case where 2-opt would definitely work.
        # 0 -> 1 -> 2 -> 3
        # Distances: 0-1: 10, 1-2: 10, 2-3: 10
        # 0-2: 100, 0-3: 100, 1-3: 100
        
        # Let's just mock the _get_distance_matrix method to avoid complex API mocking
        solver = RouteSolver(self.api_key)
        
        # Mock distance matrix: 4x4
        # 0: Start, 1: A, 2: B, 3: C
        # Route: 0 -> 1 -> 2 -> 3 is optimal (distance 30)
        # Initial might be 0 -> 2 -> 1 -> 3 (distance 100 + 35 + 100 = 235)
        
        matrix = [
            [0, 10, 100, 100], # 0
            [10, 0, 10, 100],  # 1
            [100, 10, 0, 10],  # 2
            [100, 100, 10, 0]  # 3
        ]
        
        solver._get_distance_matrix = MagicMock(return_value=matrix)
        
        route = solver.solve(self.start_address, self.other_addresses)
        
        # Expected order: Start, A, B, C
        self.assertEqual(route, ["Start", "A", "B", "C"])

    @patch('googlemaps.Client')
    def test_solve_tsp_2opt_swap(self, mock_gmaps):
        # Test a case where a swap is needed
        # Points: Start, A, B, C
        # Optimal: Start -> A -> B -> C (Distances: 10, 10, 10)
        # Input: Start, B, A, C
        
        solver = RouteSolver(self.api_key)
        
        # Matrix must match input order: [Start, B, A, C]
        # Distances:
        # Start->A=10, Start->B=100, Start->C=100
        # B->A=10, B->C=10, B->Start=100
        # A->B=10, A->C=100, A->Start=10
        # C->B=10, C->A=100, C->Start=100
        
        # Indices in matrix: 0=Start, 1=B, 2=A, 3=C
        matrix = [
            [0,   100, 10,  100], # Start
            [100, 0,   10,  10],  # B
            [10,  10,  0,   100], # A
            [100, 10,  100, 0]    # C
        ]
        solver._get_distance_matrix = MagicMock(return_value=matrix)
        
        route = solver.solve("Start", ["B", "A", "C"])
        
        self.assertEqual(route, ["Start", "A", "B", "C"])
