from django.conf import settings

def global_settings(request):
    """
    Exposes global settings to all templates.
    """
    return {
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
        'ollama_model': getattr(settings, 'OLLAMA_MODEL', 'gemma:4b'),
    }
