import requests
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.base_url = getattr(settings, 'OLLAMA_BASE_URL', 'http://host.docker.internal:11434')
        self.model = getattr(settings, 'OLLAMA_MODEL', 'gemma:4b')

    def _call_ollama(self, prompt, timeout=50):
        """Shared logic for calling Ollama and adapting JSON responses."""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=timeout
            )
            
            if response.status_code == 200:
                result_text = response.json().get('response', '[]')
                analysis = json.loads(result_text)
                
                # ADAPTATION: Handle dict wrapper vs list
                if isinstance(analysis, dict):
                    for key in ['listings', 'results', 'data', 'analysis', 'items', 'clusters']:
                        if key in analysis and isinstance(analysis[key], list):
                            return analysis[key]
                    for val in analysis.values():
                        if isinstance(val, list):
                            return val
                return analysis if isinstance(analysis, list) else []
        except Exception as e:
            logger.error(f"Ollama Call Error: {e}")
        return []

    def analyze_thrift_batch(self, stores):
        """Specialized analysis for thrift stores with parallel chunking."""
        if not stores: return []
        
        results = []
        chunk_size = 10
        chunks = [stores[i:i+chunk_size] for i in range(0, len(stores), chunk_size)]
        
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=3) as executor:
            def process_chunk(chunk):
                prompt = (
                    "Analyze these thrift stores and return a JSON array of objects.\n"
                    "Keys: 'tags' (list), 'is_potential_goldmine' (bool), 'profit_rating' (High/Medium/None), 'profit_reason'.\n"
                    "STORES:\n"
                )
                for j, s in enumerate(chunk):
                    prompt += f"{j+1}. {s['title']} at {s['address']}\n"
                
                analysis = self._call_ollama(prompt, timeout=40)
                while len(analysis) < len(chunk):
                    analysis.append({"tags": ["#Thrift"], "is_potential_goldmine": False, "profit_rating": "None"})
                return analysis[:len(chunk)]
            
            future_results = list(executor.map(process_chunk, chunks))
            for res in future_results:
                results.extend(res)
                
        return results

    def analyze_listings_batch(self, listings, bust_history=None, wishlist=None):
        """Enriches garage sales with tactical analysis using parallel chunking."""
        if not listings: return []
        
        results = []
        chunk_size = 8
        chunks = [listings[i:i+chunk_size] for i in range(0, len(listings), chunk_size)]
        
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=3) as executor:
            def process_chunk(chunk):
                prompt = (
                    "Analyze these garage sale descriptions and return a JSON array of objects.\n"
                    "Keys: 'tags', 'is_treasure' (bool), 'treasure_reason', 'is_bust_candidate' (bool), 'bust_reason', "
                    "'is_wishlist_match' (bool), 'match_reason', 'is_moving_sale' (bool), 'is_potential_goldmine' (bool), "
                    "'profit_rating' (High/Medium/None), 'profit_reason'.\n"
                )
                
                if bust_history:
                    prompt += "USER BUST HISTORY (Dislikes):\n"
                    for h in bust_history[:2]: prompt += f"- {h}\n"
                if wishlist:
                    prompt += f"USER WISHLIST: {wishlist}\n"
                
                prompt += "\nDESCRIPTIONS:\n"
                for j, desc in enumerate(chunk):
                    prompt += f"{j+1}. {desc[:400]}\n"
                
                analysis = self._call_ollama(prompt, timeout=50)
                
                # Clean and Pad
                for item in analysis:
                    if 'tags' in item and isinstance(item['tags'], str):
                        item['tags'] = [t.strip() for t in item['tags'].split(',')]
                        
                while len(analysis) < len(chunk):
                    analysis.append({
                        "tags": [], "is_treasure": False, "is_bust_candidate": False,
                        "is_wishlist_match": False, "is_moving_sale": False, 
                        "is_potential_goldmine": False, "profit_rating": "None"
                    })
                return analysis[:len(chunk)]

            future_results = list(executor.map(process_chunk, chunks))
            for res in future_results:
                results.extend(res)
                
        return results

    def predict_bust_suitability(self, description, bust_history):
        """
        Compares a single listing against the user's history of 'Bust' sales.
        Returns a boolean (True if it looks like a bust).
        """
        if not bust_history:
            return False

        prompt = (
            "The user dislikes certain garage sales. Here are descriptions of sales they marked as a 'Bust':\n"
        )
        for history in bust_history:
            prompt += f"- {history}\n"
            
        prompt += (
            f"\nNow analyze this new listing: \"{description[:400]}\"\n"
            "Does this new listing share the same negative characteristics as the Bust history? "
            "(e.g. if history is all 'baby clothes' and this is 'infant wear', it's a match).\n"
            "Return ONLY a JSON object with a key 'is_bust_candidate' (boolean)."
        )

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result_text = response.json().get('response', '{}')
                result = json.loads(result_text)
                return result.get('is_bust_candidate', False)
        except Exception as e:
            logger.error(f"AI Service Error (Bust Prediction): {e}")
        
        return False
    def cluster_neighborhoods(self, titles):
        """
        Groups a list of titles into neighborhood/community clusters using AI.
        Returns a list of cluster objects: {"name": "Neighborhood Name", "indices": [0, 2, 5]}
        """
        if not titles:
            return []

        prompt = (
            "You are a local community expert. Analyze these garage sale titles and group them into 'Neighborhood/Community Clusters' ONLY if they are part of the same shared event.\n\n"
            "RULES:\n"
            "1. Ignore broad geographic names that appear in many unrelated listings (e.g. 'Chapel Hill', 'Durham').\n"
            "2. Look for specific subdivision or neighborhood names (e.g. 'Churton Grove', 'Oak Creek').\n"
            "3. If multiple listings share the same specific neighborhood name, cluster them.\n"
            "4. Return a JSON object with a 'clusters' key, which is an array of objects: {'name': 'Specific Neighborhood Name', 'indices': [0-based indices from the list]}.\n"
            "5. If a listing doesn't belong to any cluster, do not include it in any 'indices'.\n\n"
            "TITLES TO ANALYZE:\n"
        )
        
        for i, title in enumerate(titles):
            prompt += f"{i}. {title}\n"

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result_text = response.json().get('response', '{"clusters": []}')
                result = json.loads(result_text)
                return result.get('clusters', [])
        except Exception as e:
            logger.error(f"AI Service Error (Neighborhood Clustering): {e}")
        
        return []
