from typing import Any, Dict
from django.conf import settings
from django.http import HttpRequest

def global_settings(request: HttpRequest) -> Dict[str, Any]:
    """
    Exposes global settings to all templates.
    """
    return {
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
        'ollama_model': getattr(settings, 'OLLAMA_MODEL', 'gemma:4b'),
    }
