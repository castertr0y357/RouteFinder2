from django.test import TestCase
from unittest.mock import MagicMock, patch
from .route_solver import RouteSolver

class RouteSolverTests(TestCase):
    def setUp(self):
        self.api_key = "test_key"
        self.start_address = "Start"
        self.other_addresses = [
            {'address': 'A', 'priority': 0, 'type': 'garage'},
            {'address': 'B', 'priority': 0, 'type': 'garage'},
            {'address': 'C', 'priority': 0, 'type': 'garage'}
        ]

    @patch('googlemaps.Client')
    def test_solve_tsp(self, mock_gmaps):
        # Mock the distance matrix response
        solver = RouteSolver(self.api_key)
        
        matrix = [
            [0, 10, 100, 100], # 0
            [10, 0, 10, 100],  # 1
            [100, 10, 0, 10],  # 2
            [100, 100, 10, 0]  # 3
        ]
        
        solver._get_distance_matrix = MagicMock(return_value=matrix)
        
        route = solver.solve(self.start_address, self.other_addresses, return_to_start=False)
        
        # Expected order: A, B, C
        self.assertEqual([item['address'] for item in route], ["A", "B", "C"])

    @patch('googlemaps.Client')
    def test_solve_tsp_2opt_swap(self, mock_gmaps):
        # Test a case where a swap is needed
        solver = RouteSolver(self.api_key)
        
        # Matrix must match input order: [Start, B, A, C]
        matrix = [
            [0,   100, 10,  100], # Start
            [100, 0,   10,  10],  # B
            [10,  10,  0,   100], # A
            [100, 10,  100, 0]    # C
        ]
        solver._get_distance_matrix = MagicMock(return_value=matrix)
        
        input_addresses = [
            {'address': 'B', 'priority': 0, 'type': 'garage'},
            {'address': 'A', 'priority': 0, 'type': 'garage'},
            {'address': 'C', 'priority': 0, 'type': 'garage'}
        ]
        route = solver.solve("Start", input_addresses, return_to_start=False)
        
        self.assertEqual([item['address'] for item in route], ["A", "B", "C"])

from django.contrib.auth.models import User
from .ai_service import AIService

class AIServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.profile = self.user.userprofile

    @patch('requests.post')
    def test_ai_disabled(self, mock_post):
        self.profile.ai_enabled = False
        self.profile.save()
        
        ai = AIService(user=self.user)
        self.assertFalse(ai.ai_enabled)
        
        # Test listings batch enrichment
        listings = ["Nice garage sale in Chapel Hill", "Selling baby clothes"]
        results = ai.analyze_listings_batch(listings)
        
        # Requests should not be made
        mock_post.assert_not_called()
        # Fallback values returned
        self.assertEqual(len(results), len(listings))
        for r in results:
            self.assertFalse(r['is_treasure'])
            self.assertFalse(r['is_bust_candidate'])
            self.assertEqual(r['tags'], [])

    @patch('requests.post')
    def test_ai_thinking_payload(self, mock_post):
        self.profile.ai_enabled = True
        self.profile.ai_thinking_enabled = True
        self.profile.ai_thinking_effort = 80
        self.profile.save()
        
        ai = AIService(user=self.user)
        self.assertTrue(ai.ai_enabled)
        self.assertTrue(ai.thinking_enabled)
        self.assertEqual(ai.thinking_effort, 80)
        
        # Mock successful JSON response
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"response": '{"is_bust_candidate": true}'}
        mock_post.return_value = mock_resp
        
        # Perform query
        is_bust = ai.predict_bust_suitability("Baby stuff", ["Marked baby stuff as bust"])
        
        # Verify requests.post called with correct thinking parameters
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        payload = kwargs['json']
        
        self.assertTrue(payload['think'])
        self.assertEqual(payload['options']['temperature'], 0.2) # 1 - 80/100 = 0.2
        self.assertEqual(payload['thinking_budget'], 800)
        self.assertIn("Perform detailed logical reasoning with an effort level of 80%", payload['prompt'])


